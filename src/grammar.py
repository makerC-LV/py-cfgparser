from src.rules import Alt, Seq, Opt, Star, ParseNode, AltType, Lit, Reg, Eps, Eof
from enum import Enum



class Grammar:

    def __init__(self):
        self.rules = {}
        self.ptree_list = None
        self.backtrack_choices = None

    def init_parse(self):
        self.ptree_list = []
        self.backtrack_choices = []

    def parse(self, rule, buffer):
        self.init_parse()
        root = ParseNode(rule, 0)
        stack = [root]
        self.extend(buffer, root, stack)


    # Adds all possible extensions from node to ptree_list
    def extend(self, buffer, root, stack):
        while len(stack) > 0:
            node = stack.pop()
            if self.is_terminal(node.rule):
                self.process_terminal_rule(buffer, node, stack)
            else:
                if isinstance(node.rule, Alt):
                    self.process_alt(buffer, root, node, stack)
                elif isinstance(node.rule, Seq):
                    self.process_seq(buffer, root, node, stack)
                elif isinstance(node.rule, Opt):
                    self.process_opt(buffer, root, node, stack)
                elif isinstance(node.rule, Star):
                    self.process_star(buffer, root, node, stack)
                else:
                    raise Exception(f'Unknown rule class: {type(node.rule)}')

    def process_terminal_rule(self, buffer, node, stack):
        node.rule.apply_internal(buffer, 0, node.start, node)
        while node.parent is not None:
            parent = node.parent;
            if self.update_parent(node, parent, stack):
                node = stack.pop
                assert node == parent
            else:
                break;

    def update_parent(self, node, parent, stack):
        assert (parent is None and len(stack) == 0) or (parent == stack[-1])
        if isinstance(parent.rule, Alt):
            parent.next_subrule_num += 1
            if node.matched:
                parent.matched = True
                parent.length = node.length
            return True


    def is_terminal(self, rule):
        return isinstance(rule, Lit) or isinstance(rule, Reg) or isinstance(rule, Eps) or isinstance(rule, Eof)


    def process_alt(self, buffer, root, node, stack):

        if node.alt_type == AltType.NONE:
            if left_recursion_allowed():
                lroot, lnode = self.copy_tree(root, node)
                lstack = self.copy_stack(stack)
                lnode.alt_type = AltType.LEFT
                self.extend(buffer, lroot, lnode, lstack)
            node.alt_type = AltType.REST
            self.extend(buffer, root, node)

        elif node.alt_type == AltType.LEFT:
            subrule = node.rule.subrules[0]
            cnode = ParseNode(subrule, node.start)
            node.add(cnode)
            stack.append(cnode)
        elif node.alt_type == AltType.REST:
            next_rule = self.next_rule(node, 1)
            if next_rule is not None:
                cnode = ParseNode(next_rule, node.start)
                node.add(cnode)
                stack.append(cnode)

    def process_seq(self, buffer, root, node, stack):
        next_rule = self.next_rule(node)
        if next_rule is not None:
            cnode = ParseNode(next_rule, node.start)
            node.add(cnode)
            stack.append(cnode)
        else:


    def process_opt(self, buffer, root, node, stack):
        next_rule = self.next_rule(node)
        if next_rule is not None:
            cnode = ParseNode(next_rule, node.start)
            node.add(cnode)
            stack.append(cnode)

    def process_star(self, buffer, root, node, stack):
        next_rule = self.next_rule(node)
        if next_rule is not None:
            cnode = ParseNode(next_rule, node.start)
            node.add(cnode)
            stack.append(cnode)


    def add(self, *args):
        for rule in args:
            # print(f'Before lazy removal: {rule}')
            rule = rule.remove_lazy_rules()
            # print(f'After lazy removal: {rule}')
            my_rules = self.rules

            def add_internal(r, *args):
                my_rules[r.name] = r

            rule.traverse(set(), add_internal)



    def set_nullables(self):
        for i in range(len(self.rules)):
            for rule in self.rules.values():
                if not rule.is_nullable:
                    if isinstance(rule, Alt):
                        for child in rule.subrules:
                            if child.is_nullable:
                                rule.is_nullable = True
                                break
                    elif isinstance(rule, Seq):
                        for child in rule.subrules:
                            if not child.is_nullable:
                                rule.is_nullable = False
                                break

    def set_left_recursives(self):
        could_start_with = set()
        for rule in self.rules.values():
            if isinstance(rule, Alt):
                for child in rule.subrules:
                    could_start_with.add((rule, child))
            elif isinstance(rule, Seq) or isinstance(rule, Opt) or isinstance(rule, Star):
                for child in rule.subrules:
                    could_start_with.add((rule, child))
                    if not child.is_nullable:
                        break

        closure = transitive_closure(could_start_with)

        for rule in self.rules.values():
            rule.is_left_recursive = (rule, rule) in closure




def transitive_closure(a):
    closure = set(a)
    while True:
        new_relations = set((x,w) for x,y in closure for q,w in closure if q == y)

        closure_until_now = closure | new_relations

        if closure_until_now == closure:
            break

        closure = closure_until_now

    return closure