import unittest

from src.tree import Tree


class TestTreeMethods(unittest.TestCase):

    def test_creation(self):
        node = Tree('a')
        self.assertEqual('a', node.value)

    def test_separation(self):
        a = Tree('a')
        b = Tree('b')
        b.add(Tree('c'))
        self.assertEqual(0, len(a.children))

    def test_add(self):
        node = Tree('a')
        child = Tree('b')
        node.add(child)
        self.assertEqual(1, node.child_count())
        self.assertEqual(child.parent, node)
        self.assertEqual(0, child.idx)

    def test_add_multiple(self):
        node = Tree('a')
        child = Tree('b')
        node.add(child)
        child2 = Tree('c')
        node.add(child2)
        self.assertEqual(1, child2.idx)
        child3 = Tree('d')
        node.insert(child3, 1)
        self.assertEqual(1, child3.idx)
        self.assertEqual(2, child2.idx)

    def test_list_add(self):
        node = Tree('a')
        child = Tree('b')
        child2 = Tree('c')
        node.add(child, child2)
        self.assertEqual(2, node.child_count())

    def test_find(self):
        node = Tree('a')
        child = Tree('b')
        node.add(child)
        child2 = Tree('c')
        node.add(child2)
        child3: Tree = Tree('d')
        self.assertEqual(child2, node.find_child(lambda x: x == child2))

    def test_replace(self):
        node = Tree('a')
        child = Tree('b')
        node.add(child)
        child2 = Tree('c')
        node.add(child2)
        child3 = Tree('d')
        node.replace_child(child2, child3)
        self.assertEqual(child3, node.children[-1])

if __name__ == '__main__':
    unittest.main()
