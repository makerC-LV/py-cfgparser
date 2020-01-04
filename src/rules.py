from .tree import Tree
import re
from abc import ABC, abstractmethod
from enum import Enum

class InvalidRegexDefinitionError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class Lazy:
    def __init__(self):
        # Rule.__init__(self, "Lazy")
        self.rule = None

    # def apply(self, buffer, depth: int, pos: int, parent_pn: ParseNode):
    #     raise TypeError("Cannot call apply on a lazy rule")
    #     # return self.rule.apply(buffer, depth, pos, parent_pn)
    #
    # def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
    #     pass

    def set_rule(self, arg):
        self.rule = arg
        # self.name = self.rule.name

    # def __str__(self):
    #     return self.rule.__str__()

class AltType(Enum):
    NONE = 0
    LEFT = 1
    REST = 2

class ParseNode(Tree):

    def __init__(self, rule, start: int, matched: bool = False, length: int = 0):
        Tree.__init__(self, rule)
        self.rule = rule
        self.start = start
        self.length = length
        self.matched = matched
        self.alt_type = AltType.NONE
        # Save state of last child attempted
        self.next_subrule_num = 0
        self.last_subrule_matched = False
        self.last_subrule_length = 0


    def clear(self):
        Tree.clear(self)
        self.length = 0
        self.matched = False


class Rule(ABC):
    DEBUG = False

    def __init__(self, name=None, *args):
        self.name = name
        self.subrules = []
        self.is_nullable = False
        self.is_left_recursive = False
        self.is_alt = False
        self.debug = False
        if len(args) > 0:
            self.subrules.extend(args)

    def apply(self, buffer, depth: int, pos: int, parent_pn: ParseNode = None, choice_stack = None, ptree_list = None, mode = None):
        self.debugp(' ' * depth + f'{depth}: Start: apply {self} at {pos} : ...[{buffer[pos:pos + 40]}]...')
        if choice_stack is None:
            choice_stack = []
        if ptree_list is None:
            ptree_list = []
        if mode is None:
            mode = ['BUILD']
        my_node = ParseNode(self, pos)
        if parent_pn is not None:
            parent_pn.add(my_node)
        no_left_recursion = False
        if self.is_alt:
            no_left_recursion = self.left_rec_count(my_node) > len(buffer) - pos
        self.apply_internal(buffer, depth, pos, my_node, no_left_recursion)

        self.debugp(
            ' ' * depth + f'{depth}: End match:{return_node.matched} length:{return_node.length}: apply {self} to {pos} : ...[{buffer[pos:pos + 40]}]...')
        return return_node

    def left_rec_apply(self, buffer, depth, pos, parent_pn):
        self.memo[pos] = ParseNode(self, pos)
        while True:
            my_node = ParseNode(self, pos)
            if parent_pn is not None:
                parent_pn.add(my_node)
            self.apply_internal(buffer, depth, pos, my_node)
            if parent_pn is not None:
                parent_pn.remove(my_node)
            saved = self.memo[pos]
            if not my_node.matched:
                break
            elif saved.matched and my_node.length <= saved.length:
                break
            else:
                self.memo[pos] = my_node
        return_node = self.memo[pos]
        if parent_pn is not None:
            parent_pn.add(return_node)
        return return_node

    def left_rec_call(self, parent_pn):
        if parent_pn is None or parent_pn.child_count() > 0:
            return False
        ancestor = parent_pn
        while ancestor is not None:
            if ancestor.rule == self and ancestor.child_count() == 1:
                return True
            if ancestor.parent is not None and ancestor.parent.children[0] != ancestor:
                return False
            ancestor = ancestor.parent
        return False

    @abstractmethod
    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion):
        pass

    def remove_lazy_rules(self):
        return_rule = self
        if (isinstance(self, Lazy)):
            return_rule = self.rule
        def collect_preds(rule, pmap):
            for crule in rule.subrules:
                preds = pmap.get(crule)
                if preds is None:
                    preds = set()
                    pmap[crule] = preds
                preds.add(rule)

        pmap = {}
        self.traverse(set(), collect_preds, pmap)
        for k, v in pmap.items():
            if isinstance(k, Lazy):
                for pred in v:
                    idx = pred.subrules.index(k)
                    pred.subrules.remove(k)
                    pred.subrules.insert(idx, k.rule)
        return return_rule

    def init_memos(self):
        def clear_memo(rule, *args):
            rule.memo = {}
        self.traverse(set(), clear_memo)


    def traverse(self, visited, func, *args):
        if self in visited:
            return
        else:
            func(self, *args)
            visited.add(self)
            for rule in self.subrules:
                if isinstance(rule, Lazy):
                    rule.rule.traverse(visited, func, args)
                else:
                    rule.traverse(visited, func, *args)

    def debugp(self, param):
        if Rule.DEBUG or self.debug:
            print(param)

    def __str__(self):
        return self.name


class Alt(Rule):
    def __init__(self, name, *args):
        Rule.__init__(self, name, *args)
        self.is_alt = True

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion):
        for i, child in enumerate(self.subrules):
            if no_left_recursion and i == 1:
                continue  # don't choose leftmost alternative
            cnode = child.apply(buffer, depth + 1, pos, node)
            if cnode.matched:
                node.length += cnode.length
                node.matched = True
                # node.add(cnode)
                break

    # def __str__(self):
    #     return f'{self.name}[' + '|'.join([c.name for c in self.subrules]) + ']'


class Seq(Rule):
    def __init__(self, name, *args):
        Rule.__init__(self, name, *args)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion = False):
        lpos = pos
        for child in self.subrules:
            cnode = child.apply(buffer, depth + 1, lpos, node)
            if cnode.matched:
                lpos += cnode.length
                node.length += cnode.length
                node.matched = True
                # node.add(cnode)
            else:
                node.clear()
                break

    # def __str__(self):
    #     return f'{self.name}[' + ','.join([c.name for c in self.subrules]) + ']'


class Opt(Rule):
    def __init__(self, arg):
        Rule.__init__(self, "Opt", arg)
        self.is_nullable = True

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode), no_left_recursion = False):
        rule = self.subrules[0]
        cnode = rule.apply(buffer, depth + 1, pos, node)
        if cnode.matched:
            node.length = cnode.length
            node.matched = True
            # node.add(cnode)
        else:
            node.length = 0
            node.matched = True

    # def __str__(self):
    #     return self.subrules[0].name + '?'


class Lit(Rule):
    def __init__(self, arg):
        Rule.__init__(self, arg)
        self.literal = arg
        self.length = len(self.literal)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion = False):
        end = pos + self.length
        if len(buffer) >= end and self.literal == buffer[pos:end]:
            # print(f'Lit:{self.literal}  buf:{buffer[pos:end]}')
            node.length = self.length
            node.matched = True


class Reg(Rule):
    def __init__(self, arg):
        Rule.__init__(self, "Reg")
        self.reg = arg

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion = False):
        m = re.search(self.reg, buffer[pos:])
        if m is None or m.start() > 0:
            return
        elif m.start() == 0:
            node.length = m.end() - m.start()
            node.matched = True
            if node.length == 0:
                raise InvalidRegexDefinitionError(f'Regex {self.reg} matches null string')

    # def __str__(self):
    #     return 're[' + self.reg + ']'


class Star(Rule):
    def __init__(self, name, arg):
        Rule.__init__(self, name, arg)
        self.is_nullable = True
        self.rule = arg

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion = False):
        lpos = pos
        while True:
            cnode = self.rule.apply(buffer, depth + 1, lpos, node)
            if cnode.matched:
                lpos += cnode.length
                node.length += cnode.length
            else:
                break
        node.matched = True

    # def __str__(self):
    #     return self.rule.name + '*'


class Eps(Rule):
    def __init__(self, name):
        Rule.__init__(self, name)
        self.is_nullable = True

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion = False):
        node.matched = True

    # def __str__(self):
    #     return '<EPS>'


class Eof(Rule):
    def __init__(self, name):
        Rule.__init__(self, name)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode, no_left_recursion = False):
        if pos == len(buffer):
            node.matched = True

    # def __str__(self):
    #     return '<EOF>'


def eof():
    return Eof('EOF')


def eps():
    return Eps('EPS')


def lazy():
    return Lazy()


def seqn(name: str, *args) -> Rule:
    return Seq(name, *args)


def alt(name, *args):
    return Alt(name, *args)


def reg(arg):
    return Reg(arg)


def lit(arg):
    return Lit(arg)


def star(name, arg):
    return Star(name, arg)


def plus(name, arg: Rule):
    return seqn(name, arg, star(arg))
