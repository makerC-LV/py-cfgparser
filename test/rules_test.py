import unittest

from src.grammar import Grammar
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
        r.remove_lazy_rules()
        pn = r.apply("b", 0, 0)
        self.check(pn, True, 0, 1)
        r.init_memo()
        pn = r.apply("bac", 0, 0)
        self.check(pn, True, 0, 2)
        r.init_memo()
        pn = r.apply("baa", 0, 0)
        self.check(pn, True, 0, 3)
        r.init_memo()
        pn = r.apply("baaac", 0, 0)
        self.check(pn, True, 0, 4)

    # R = aRb | eps
    def test_non_left_recursion(self):
        rec = lazy()
        r = alt("R", seqn("aRb", lit('a'), rec, lit('b')), eps())
        rec.set_rule(r)
        r.remove_lazy_rules()
        pn = r.apply("ab", 0, 0)
        self.check(pn, True, 0, 2)
        r.init_memos()
        pn = r.apply("aabb", 0, 0)
        self.check(pn, True, 0, 4)
        r.init_memos()
        pn = r.apply("aacbb", 0, 0)
        self.check(pn, True, 0, 0)

    # A --> Br | eps
    # B --> Cd
    # C --> At
    def test_indirect_left_recursion(self):
        rec = lazy()
        C = seqn("At", rec, lit('t'))
        B = seqn("Cd", C, lit('d'))
        A = alt("Br|eps", seqn("Br", B, lit('r')), eps())
        rec.set_rule(A)
        g = Grammar()
        g.add(A)
        g.set_nullables()
        g.set_left_recursives()
        # A.remove_lazy_rules()
        Rule.DEBUG = True
        pn = A.apply("tdr", 0, 0)
        self.check(pn, True, 0, 3)


    def check(self, pn, matched, start: int, length: int):
        self.assertEqual(start, pn.start)
        self.assertEqual(matched, pn.matched)
        self.assertEqual(length, pn.length)
