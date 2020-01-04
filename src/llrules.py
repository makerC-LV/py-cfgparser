from src.rules import ParseNode, Alt


def to_key(rule, pos):
    return tuple({id(rule), pos})

class MemoEntry:
    def __init__(self, lr, pos):
        self.lr = lr
        self.pos = pos

class Head:
    def __init__(self, rule, invSet, evalSet):
        self.rule = rule
        self.invSet = invSet
        self.evalSet = evalSet


class LR:
    def __init__(self, seed, rule, head, next): #LR : (seed : AST,rule : RULE,head : HEAD,next : LR)
        self.seed = seed
        self.rule = rule
        self.head = head
        self.next = next





class Parser:

    def __init__(self, buffer):
        self.pos = 0
        self.heads = {}
        self.memo = {}
        self.lrstack = []
        self.buffer = buffer


    def apply_rule(self, rule, pos):
        m = self.recall(rule, pos)
        if m is None:
            lr = LR(ParseNode(rule, pos), rule, None, self.lrstack)     #LR(FAIL,R,NIL,LRStack)
            self.lrstack = lr
            m = MemoEntry(lr, pos)
            self.memo[to_key(rule, pos)] = m
            ans = self.eval_body(rule, pos)
            self.lrstack = self.lrstack.next
            m.pos = self.pos
            if lr.head is not None:
                lr.seed = ans
                return self.lr_answer(rule, pos, m)
            else:
                m.ans = ans
                return ans
        else:
            self.pos = m.pos
            if isinstance(m.ans, LR):
                self.setup_lr(R, m.ans)
                return m.ans.seed
            else:
                return m.ans





    def recall(self, rule, pos):
        pass

    def setup_lr(self, rule, lr):
        if lr.head is None:
            lr.head = Head(rule, {}, {})
        s = self.lrstack
        while s.head != lr.head:
            s.head = lr.head
            lr.head.invSet.add(s.rule)
            s = s.next

    def lr_answer(self, rule, pos, m):
        h = m.ans.head
        if h.rule != rule:
            return m.ans.seed
        else:
            if not m.ans.matched:
                return m.ans
            else:
                return self.grow_lr(rule, pos, m, h)

    def grow_lr(self, rule, pos, m, h):
        self.heads[pos] = h
        while True:
            self.pos = pos
            h.evalSet = h.invSet.copy()
            ans = r_eval(rule, pos)
            if not ans.matched or self.pos <= ans.pos + ans.length:
                break
            m.ans = ans
            m.pos = pos
        del self.heads[pos]
        self.pos = m.pos
        return m.ans

    def eval_body(self, rule, pos):
        if isinstance(rule, Alt):
            for c in rule.children:
                p = pos
                pn = self.apply_rule(c, pos)
                if pn.matched:
                    return pn
            return ParseNode(rule, pos)

        else:
            return self.apply_rule(rule, pos)









