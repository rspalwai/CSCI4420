import unittest

from truth_tree import parse, Var, Not, And, Or, Imply, Equiv, Node, Tableau

class TestParser(unittest.TestCase):
    def test_simple_and(self):
        f = parse('A & B')
        self.assertIsInstance(f, And)
        self.assertEqual(repr(f), '(A & B)')

    def test_imply(self):
        f = parse('A -> B')
        self.assertIsInstance(f, Imply)

    def test_equiv(self):
        f = parse('A <-> B')
        self.assertIsInstance(f, Equiv)

    def test_negation(self):
        f = parse('~A')
        self.assertIsInstance(f, Not)
        self.assertIsInstance(f.operand, Var)
        self.assertEqual(repr(f), '~A')

class TestTableau(unittest.TestCase):
    def collect_open(self, root):
        open_leaves = []
        def collect(node):
            if not node.children:
                if not node.closed:
                    open_leaves.append(node)
            else:
                for c in node.children:
                    collect(c)
        collect(root)
        return open_leaves

    def test_contradiction(self):
        root = Node([parse('A'), Not(parse('A'))])
        tb = Tableau(root)
        tb.expand_all()
        self.assertTrue(root.closed)

    def test_disjunction_open(self):
        root = Node([parse('A | B'), Not(parse('A'))])
        tb = Tableau(root)
        tb.expand_all()
        opens = self.collect_open(root)
        # Expect one open branch containing B
        self.assertTrue(any(any(isinstance(f, Var) and f.name=='B' for f in leaf.formulas) for leaf in opens))

    def test_negated_conjunction(self):
        root = Node([Not(parse('A & B')), parse('A'), parse('B')])
        tb = Tableau(root)
        tb.expand_all()
        # both branches close
        self.assertTrue(all(leaf.closed for leaf in self.collect_open(root)))

    def test_negated_implication(self):
        root = Node([Not(parse('A -> B')), parse('A')])
        tb = Tableau(root)
        tb.expand_all()
        opens = self.collect_open(root)
        # open branch should contain ~B
        self.assertTrue(any(any(isinstance(f, Not) and isinstance(f.operand, Var) and f.operand.name=='B'
                                 for f in leaf.formulas)
                            for leaf in opens))

    def test_equivalence_open(self):
        root = Node([parse('A <-> B'), parse('A'), parse('B')])
        tb = Tableau(root)
        tb.expand_all()
        # no closure, should be one open leaf
        opens = self.collect_open(root)
        self.assertFalse(root.closed)
        self.assertEqual(len(opens), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)

