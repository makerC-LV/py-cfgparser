from .tree import Tree
import re
from abc import ABC, abstractmethod


class InvalidRegexDefinitionError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class ParseNode(Tree):

    def __init__(self, rule, start: int, matched: bool = False, length: int = 0):
        Tree.__init__(self, rule)
        self.rule = rule
        self.start = start
        self.length = length
        self.matched = matched

    def clear(self):
        Tree.clear(self)
        self.length = 0
        self.matched = False


class Rule(ABC):
    DEBUG = False

    def __init__(self, name=None, *args):
        self.name = name
        self.subrules = []
        self.debug = False
        if len(args) > 0:
            self.subrules.extend(args)

    def apply(self, buffer, depth: int, pos: int, parent_pn: ParseNode = None) -> ParseNode:
        self.debugp(' ' * depth + f'{depth}: Start: apply {self} at {pos} : ...[{buffer[pos:pos + 40]}]...')
        return_node = None
        if parent_pn is None:
            my_node = ParseNode(self, pos)
            self.apply_internal(buffer, depth, pos, my_node)
            return_node = my_node
        else:
            my_count = 0
            ancestor = parent_pn
            depth = 0
            while ancestor is not None:
                # print(f'anc:{ancestor.rule} self: {self}')
                if ancestor.rule == self and ancestor.start == pos:
                    my_count = my_count + 1
                ancestor = ancestor.parent
                depth += 1

            # print(f'my_count={my_count}  depth:{depth}')
            if pos + my_count >= len(buffer):  # failed
                self.debugp(' ' * depth + f'recursive depth limit for {self.__str__()}')
                return_node = ParseNode(self, pos)
            else:
                my_node = ParseNode(self, pos)
                parent_pn.add(my_node)
                self.apply_internal(buffer, depth, pos, my_node)
                if not my_node.matched:
                    parent_pn.remove(my_node)
                return_node = my_node
        self.debugp(
            ' ' * depth + f'{depth}: End match:{return_node.matched} length:{return_node.length}: apply {self} to {pos} : ...[{buffer[pos:pos + 40]}]...')
        return return_node

    @abstractmethod
    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        pass

    def debugp(self, param):
        if Rule.DEBUG or self.debug:
            print(param)

    def __str__(self):
        return self.name


class Alt(Rule):
    def __init__(self, name, *args):
        Rule.__init__(self, name, *args)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        for child in self.subrules:
            cnode = child.apply(buffer, depth+1, pos, node)
            if cnode.matched:
                node.length += cnode.length
                node.matched = True
                node.add(cnode)
                break

    def __str__(self):
        return f'{self.name}[' + '|'.join([c.name for c in self.subrules]) + ']'


class Seq(Rule):
    def __init__(self, name, *args):
        Rule.__init__(self, name, *args)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        lpos = pos
        for child in self.subrules:
            cnode = child.apply(buffer, depth+1, lpos, node)
            if cnode.matched:
                lpos += cnode.length
                node.length += cnode.length
                node.matched = True
                node.add(cnode)
            else:
                node.clear()
                break

    def __str__(self):
        return f'{self.name}[' + ','.join([c.name for c in self.subrules]) + ']'


class Opt(Rule):
    def __init__(self, arg):
        Rule.__init__(self, "Opt", arg)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        rule = self.subrules[0]
        cnode = rule.apply(buffer, depth+1, pos, node)
        if cnode.matched:
            node.length = cnode.length
            node.matched = True
            node.add(cnode)
        else:
            node.length = 0
            node.matched = True

    def __str__(self):
        return self.subrules[0].name + '?'


class Lit(Rule):
    def __init__(self, arg):
        Rule.__init__(self, arg)
        self.literal = arg
        self.length = len(self.literal)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        end = pos + self.length
        if len(buffer) >= end and self.literal == buffer[pos:end]:
            # print(f'Lit:{self.literal}  buf:{buffer[pos:end]}')
            node.length = self.length
            node.matched = True


class Reg(Rule):
    def __init__(self, arg):
        Rule.__init__(self, "Reg")
        self.reg = arg

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        m = re.search(self.reg, buffer[pos:])
        if m is None or m.start() > 0:
            return
        elif m.start() == 0:
            node.length = m.end() - m.start()
            node.matched = True
            if node.length == 0:
                raise InvalidRegexDefinitionError(f'Regex {self.reg} matches null string')

    def __str__(self):
        return 're[' + self.reg + ']'


class Star(Rule):
    def __init__(self, name, arg):
        Rule.__init__(self, name, arg)
        self.rule = arg

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        lpos = pos
        while True:
            cnode = self.rule.apply(buffer, depth+1, lpos, node)
            if cnode.matched:
                lpos += cnode.length
                node.length += cnode.length
            else:
                break
        node.matched = True

    def __str__(self):
        return self.rule.name + '*'


class Eps(Rule):
    def __init__(self, name):
        Rule.__init__(self, name)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        node.matched = True

    def __str__(self):
        return '<EPS>'


class Eof(Rule):
    def __init__(self, name):
        Rule.__init__(self, name)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        if pos == len(buffer):
            node.matched = True

    def __str__(self):
        return '<EOF>'


class Lazy(Rule):
    def __init__(self):
        Rule.__init__(self, "Lazy")
        self.rule = None

    def apply(self, buffer, depth: int, pos: int, parent_pn: ParseNode):
        return self.rule.apply(buffer, depth, pos, parent_pn)

    def apply_internal(self, buffer, depth: int, pos: int, node: ParseNode):
        pass

    def set_rule(self, arg):
        self.rule = arg
        self.name = self.rule.name

    def __str__(self):
        return self.rule.__str__()


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
