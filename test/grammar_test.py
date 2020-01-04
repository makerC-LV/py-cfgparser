import unittest

from src.grammar import Grammar
from src.rules import lit, eps, eof, plus, star, reg, seqn, alt, InvalidRegexDefinitionError, lazy, Rule


class TestGrammarMethods(unittest.TestCase):

    def test_add(self):
        g = Grammar()
        r = alt("MyAlt", lit('a'), lit('b'))
        g.add(r)
        self.assertEqual(3, len(g.rules))

        rec = lazy()
        C = seqn("At", rec, lit('t'))
        B = seqn("Cd", C, lit('d'))
        A = alt("A", seqn("Br", B, lit('r')), eps())
        rec.set_rule(A)
        g.add(A)
        self.assertEqual(11, len(g.rules))

        g.set_nullables()
        for r in g.rules.values():
            print(r, r.is_nullable)
        print("---")
        g.set_left_recursives()
        for r in g.rules.values():
            print(r, r.is_left_recursive)
