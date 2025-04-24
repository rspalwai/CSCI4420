import re
import sys
from collections import deque
from typing import List, Union, Optional

# AST classes with equality and hashing defining basis for use in sets
class Formula:
    def __eq__(self, other):
        return isinstance(other, type(self)) and self.__dict__ == other.__dict__
    def __hash__(self):
        return hash((type(self), tuple(sorted(self.__dict__.items()))))

class Var(Formula):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return self.name

class Not(Formula):
    def __init__(self, operand: Formula):
        self.operand = operand
    def __repr__(self):
        return f"~{self.operand}"

class And(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right
    def __repr__(self):
        return f"({self.left} & {self.right})"

class Or(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right
    def __repr__(self):
        return f"({self.left} | {self.right})"

class Imply(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right
    def __repr__(self):
        return f"({self.left} -> {self.right})"

class Equiv(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left, self.right = left, right
    def __repr__(self):
        return f"({self.left} <-> {self.right})"

# Parser: normalize unicode then shunting-yard
TOKENS = [r"~", r"&", r"\|", r"->", r"<->", r"\(", r"\)", r"[A-Za-z][A-Za-z0-9_]*"]
TOKEN_RE = re.compile("|".join(f"(?P<T{i}>{t})" for i,t in enumerate(TOKENS)))
PRECEDENCE = {'~':5,'&':4,'|':3,'->':2,'<->':1}
RIGHT_ASSOC = {'~','->','<->'}

def tokenize(s: str):
    for m in TOKEN_RE.finditer(s):
        yield m.group(0)

def parse(s: str) -> Formula:
    # normalize logical symbols
    s = s.replace('∧','&').replace('∨','|').replace('→','->').replace('↔','<->')
    output: List[Union[Formula,str]] = []
    ops: List[str] = []
    def apply_op(op: str):
        if op == '~':
            arg = output.pop()
            output.append(Not(arg))
        else:
            right = output.pop()
            left = output.pop()
            if op == '&': output.append(And(left,right))
            elif op == '|': output.append(Or(left,right))
            elif op == '->': output.append(Imply(left,right))
            elif op == '<->': output.append(Equiv(left,right))
    for tok in tokenize(s):
        if re.match(r"[A-Za-z]", tok):
            output.append(Var(tok))
        elif tok in PRECEDENCE:
            while ops and ops[-1] != '(' and (
                PRECEDENCE[ops[-1]] > PRECEDENCE[tok] or
                (PRECEDENCE[ops[-1]] == PRECEDENCE[tok] and tok not in RIGHT_ASSOC)
            ):
                apply_op(ops.pop())
            ops.append(tok)
        elif tok == '(':
            ops.append(tok)
        elif tok == ')':
            while ops and ops[-1] != '(':
                apply_op(ops.pop())
            ops.pop()
    while ops:
        apply_op(ops.pop())
    return output[0]

# Tableau engine with recursive expand
class Node:
    def __init__(self, formulas: List[Formula], parent=None):
        self.formulas = set(formulas)
        self.parent = parent
        self.children: List[Node] = []
        self.closed = False

    def is_closed(self):
        for f in self.formulas:
            if isinstance(f, Not) and f.operand in self.formulas:
                return True
            if not isinstance(f, Not) and Not(f) in self.formulas:
                return True
        return False

    def expand(self):
        if self.closed or self.children:
            return
        # closure
        if self.is_closed():
            self.closed = True
            return
        # quick MP
        for f in list(self.formulas):
            if isinstance(f, Imply):
                A,B = f.left, f.right
                if A in self.formulas and B not in self.formulas:
                    self.formulas.add(B)
                    self.expand()
                    return
        # quick DS
        for f in list(self.formulas):
            if isinstance(f, Or):
                A,B = f.left, f.right
                if Not(A) in self.formulas and B not in self.formulas:
                    self.formulas.add(B)
                    self.expand()
                    return
                if Not(B) in self.formulas and A not in self.formulas:
                    self.formulas.add(A)
                    self.expand()
                    return
        # α rules
        for f in list(self.formulas):
            if isinstance(f, And):
                new = [f.left, f.right]
                self.formulas.update(new)
                self.expand()
                return
            if isinstance(f, Equiv):
                self.formulas.remove(f)
                self.formulas.update({Imply(f.left,f.right), Imply(f.right,f.left)})
                self.expand()
                return
            if isinstance(f, Not):
                g = f.operand
                if isinstance(g, Or):
                    self.formulas.remove(f)
                    self.formulas.update({Not(g.left), Not(g.right)})
                    self.expand()
                    return
                if isinstance(g, Imply):
                    self.formulas.remove(f)
                    self.formulas.update({g.left, Not(g.right)})
                    self.expand()
                    return
        # β rules
        for f in list(self.formulas):
            if isinstance(f, Or):
                left = Node(list(self.formulas - {f}) + [f.left], parent=self)
                right = Node(list(self.formulas - {f}) + [f.right], parent=self)
                self.children = [left,right]
                return
            if isinstance(f, Imply):
                left = Node(list(self.formulas - {f}) + [Not(f.left)], parent=self)
                right = Node(list(self.formulas - {f}) + [f.right], parent=self)
                self.children = [left,right]
                return
            if isinstance(f, Not) and isinstance(f.operand, And):
                g = f.operand
                left = Node(list(self.formulas - {f}) + [Not(g.left)], parent=self)
                right = Node(list(self.formulas - {f}) + [Not(g.right)], parent=self)
                self.children = [left,right]
                return
        # saturated

class Tableau:
    MAX_EXPANSIONS = 1000
    def __init__(self, root: Node):
        self.root = root

    def expand_all(self):
        queue = deque([self.root])
        expansions = 0
        while queue:
            node = queue.popleft()
            node.expand()
            for child in node.children:
                queue.append(child)
            expansions += 1
            if expansions > self.MAX_EXPANSIONS:
                print(f"Reached maximum expansions ({self.MAX_EXPANSIONS}). Halting further expansion.")
                break

    def print_tree(self, node: Optional[Node]=None, prefix: str=""):
        if node is None:
            node = self.root
        status = "(closed)" if node.closed else ""
        print(prefix + ', '.join(map(str,node.formulas)) + f" {status}")
        if node.children:
            print(prefix + "├─")
            for i,child in enumerate(node.children):
                branch = "│  " if i < len(node.children)-1 else "   "
                self.print_tree(child, prefix + branch)

# CLI
if __name__ == '__main__':
    if len(sys.argv) < 2:
        demo = "A -> (B | C), A, ~B, C -> D, ~D"
        print(f"No input provided; running demo: {demo}\n")
        inp = demo
    else:
        inp = sys.argv[1]
    parts = [p.strip() for p in inp.split(',') if p.strip()]
    formulas = [parse(p) for p in parts]
    root = Node(formulas)
    tb = Tableau(root)
    tb.expand_all()
    tb.print_tree()
