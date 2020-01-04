
class Tree:

    def __init__(self, value=None):
        self.children = []
        self.parent = None
        self.value = value

    def add(self, *args):
        # print(args)
        for arg in args:
            # print(arg)
            self.children.append(arg)
            arg.parent = self

    def remove(self, arg):
        self.children.remove(arg)
        arg.parent = None

    def insert(self, node, index):
        self.children.insert(index, node)
        node.parent = self

    def replace_child(self, node, other):
        idx = self.children.index(node)
        if idx >= 0:
            self.remove(node)
            self.insert(other, idx)

    def find_child(self, fn):
        return next((x for x in self.children if fn(x)), None)

    def is_root(self):
        return self.parent is None

    def get_root(self):
        node = self
        while node.parent is not None:
            node = node.parent
        return node

    def child_count(self):
        return len(self.children)

    def clear(self):
        self.children = []

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'Tree({self.value})'

    def pprint_tree(self, file=None, _prefix="", _last=True):
        print(_prefix, "`- " if _last else "|- ", self.value, sep="", file=file)
        _prefix += "   " if _last else "|  "
        child_count = len(self.children)
        for i, child in enumerate(self.children):
            _last = i == (child_count - 1)
            child.pprint_tree(file, _prefix, _last)

    @property
    def idx(self):
        return self.parent.children.index(self)



