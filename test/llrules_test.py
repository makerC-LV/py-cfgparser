import unittest

from src.llrules import Parser
from src.rules import lit, eps, eof, plus, star, reg, seqn, alt, InvalidRegexDefinitionError, lazy, Rule


class TestParserMethods(unittest.TestCase):

    def test_lit(self):
        r = lit("Hello")
        parser = Parser("Hello")
        pn = parser.apply_rule(r, 0)
        self.check(pn, True, 0, 5)
        # pn = lit("Hello").apply("Say Hello to me", 4)
        # self.check(pn, True, 4, 5)
        # pn = lit("Hello").apply("Hel", 0)
        # self.check(pn, False, 0, 0)

    # R -> Ra | b
    def test_left_recursion(self):
        rec = lazy()
        r = alt("R", seqn("Ra", rec, lit('a')), lit('b'))
        rec.set_rule(r)
        parser = Parser('b')
        pn = parser.apply_rule(rec, 0)
        print(pn)
        # self.check(pn, True, 0, 1)
        # Rule.DEBUG = True
        # pn = r.apply("bac", 0, 0)
        # self.check(pn, True, 0, 2)
        # pn = r.apply("baa", 0, 0)
        # self.check(pn, True, 0, 3)
        # pn = r.apply("baaac", 0, 0)
        # self.check(pn, True, 0, 4)

    def check(self, pn, matched, start: int, length: int):
        self.assertEqual(start, pn.start)
        self.assertEqual(matched, pn.matched)
        self.assertEqual(length, pn.length)