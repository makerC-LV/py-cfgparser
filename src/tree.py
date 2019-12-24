
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

    def insert(self, node, index):
        self.children.insert(index, node)
        node.parent = self

    def find_child(self, fn):
        return next((x for x in self.children if fn(x)), None)

    def is_root(self):
        return self.parent is None

    def child_count(self):
        return len(self.children)

    def clear(self):
        self.children = []

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'Tree({self.value})'

    @property
    def idx(self):
        return self.parent.children.index(self)



