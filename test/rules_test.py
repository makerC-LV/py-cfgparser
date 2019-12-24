import unittest

from src.rules import lit, eps, eof, plus, star, reg, seqn, alt, InvalidRegexDefinitionError, lazy, Rule


class TestRulesMethods(unittest.TestCase):

    def test_lit(self):
        pn = lit("Hello").apply("Say Hello to me", 0)
        self.check(pn, False, 0, 0)
        pn = lit("Hello").apply("Say Hello to me", 4)
        self.check(pn, True, 4, 5)
        pn = lit("Hello").apply("Hel", 0)
        self.check(pn, False, 0, 0)

    def test_reg(self):
        pn = reg("S[a-z][a-z]").apply("Say Hello to me", 0)
        self.check(pn, True, 0, 3)
        pn = reg(" [a-z][a-z] ").apply("Say Hello to me", 0)
        self.check(pn, False, 0, 0)
        with self.assertRaises(InvalidRegexDefinitionError):
            pn = reg("a*").apply("bc", 0)


    def test_seqn(self):
        pn = seqn("MySeq", lit('a'), lit('b')).apply("abcd", 0)
        self.check(pn, True, 0, 2)
        pn = seqn("MySeq", lit('a'), lit('b')).apply("abcd", 2)
        self.check(pn, False, 2, 0)

    def test_alt(self):
        pn = alt("MyAlt", lit('a'), lit('b')).apply("abcd", 0)
        self.check(pn, True, 0, 1)
        pn = alt("MyAlt", lit('a'), lit('b')).apply("abcd", 2)
        self.check(pn, False, 2, 0)

    def test_star(self):
        altr = star("MyStar", lit('a'))
        pn = altr.apply("abcd", 0, 0)
        self.check(pn, True, 0, 1)
        pn = altr.apply("abcd", 0, 1)
        self.check(pn, True, 1, 0)
        pn = altr.apply("aabcd", 0, 0)
        self.check(pn, True, 0, 2)

    # R -> Ra | b
    def test_left_recursion(self):
        rec = lazy()
        r = alt("R", seqn("Ra", rec, lit('a')), lit('b'))
        rec.set_rule(r)
        pn = r.apply("b", 0, 0)
        self.check(pn, True, 0, 1)
        Rule.DEBUG = True
        pn = r.apply("bac", 0, 0)
        self.check(pn, True, 0, 2)
        pn = r.apply("baa", 0, 0)
        self.check(pn, True, 0, 3)
        pn = r.apply("baaac", 0, 0)
        self.check(pn, True, 0, 4)

    def check(self, pn, matched, start: int, length: int):
        self.assertEqual(start, pn.start)
        self.assertEqual(matched, pn.matched)
        self.assertEqual(length, pn.length)
