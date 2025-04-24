# Truth-Tree CLI (Semantic Tableau)

A simple Python console tool for building and automatically expanding truth trees in propositional logic.

## Usage
```bash
python truth_tree.py "formula1, formula2, ..."
```
- **Formulas**: use `~` for ¬, `&` for ∧, `|` for ∨, `->` for →, `<->` for ↔. Unicode symbols are normalized.
- **Demo**: running without arguments uses a built‑in example.

## Features
- **α/β Decomposition**: standard tableau rules for ∧, ∨, →, ¬, ↔.  
- **Quick Inferences**: Modus Ponens (MP) and Disjunctive Syllogism (DS).  
- **Closure**: detects any φ and ¬φ, not just atoms.  
- **Auto-Expand**: one command builds the full tree.  
- **Expansion Limit**: configurable cap (default 1000) to avoid runaway.

## Next Steps
- **Interactive Steps**: allow manual rule selection.  
- **Additional Inference Rules**: Modus Tollens, Hypothetical Syllogism.  
- **GUI Version**: visual tree editing in a browser or desktop app.  
- **First‑Order Logic**: add quantifier rules and unification.

*Written as part of a Logic & Computability course project.*

## EXAMPLE
Input: 
"A <-> (B ∨ (C & D)), ~D, E -> F, E, G ∨ H, ~G, I -> J, J -> K, ~K"

Output:
F, ~D, (I -> J), (J -> K), E, (A -> (B | (C & D))), H, (G | H), (E -> F), ~K, ((B | (C & D)) -> A), ~G
├─
│  F, ~D, (J -> K), ~I, E, (A -> (B | (C & D))), H, (G | H), (E -> F), ~K, ((B | (C & D)) -> A), ~G
│  ├─
│  │  ~D, (E -> F), ~I, E, (A -> (B | (C & D))), H, (G | H), ~J, F, ~K, ((B | (C & D)) -> A), ~G
│  │  ├─
│  │  │  ~D, ~E, ~I, E, (A -> (B | (C & D))), H, (G | H), ~J, F, ~K, ((B | (C & D)) -> A), ~G (closed)
│  │     ~D, ~I, E, (A -> (B | (C & D))), H, (G | H), ~J, F, ~K, ((B | (C & D)) -> A), ~G
│  │     ├─
│  │     │  ~D, ~I, E, ~A, H, (G | H), ~J, F, ~K, ((B | (C & D)) -> A), ~G
│  │     │  ├─
│  │     │  │  ~D, ~I, E, H, G, ~A, ~J, F, ~K, ((B | (C & D)) -> A), ~G (closed)
│  │     │     ~D, ~I, E, H, ~A, ~J, F, ~K, ((B | (C & D)) -> A), ~G
│  │     │     ├─
│  │     │     │  ~D, ~(C & D), ~I, E, ~B, H, ~A, ~J, F, ~K, ~G
│  │     │     │  ├─
│  │     │     │  │  ~D, ~I, E, ~B, H, ~A, ~J, ~C, F, ~K, ~G
│  │     │     │     ~D, ~I, E, ~B, H, ~A, ~J, F, ~K, ~G
│  │     │        ~D, A, ~I, E, H, ~A, ~J, F, ~K, ~G (closed)
│  │        ~D, A, (B | (C & D)), ~I, E, H, (G | H), ~J, F, ~K, ((B | (C & D)) -> A), ~G
│  │        ├─
│  │        │  ~D, B, ~I, ~G, E, H, (G | H), ~J, F, ~K, ((B | (C & D)) -> A), A
│  │        │  ├─
│  │        │  │  ~D, A, B, ~I, E, H, G, ~J, F, ~K, ((B | (C & D)) -> A), ~G (closed)
│  │        │     ~D, A, B, ~I, E, H, ~J, F, ~K, ((B | (C & D)) -> A), ~G
│  │        │     ├─
│  │        │     │  ~D, ~(C & D), B, ~I, ~G, E, ~B, H, ~J, F, ~K, A (closed)
│  │        │        ~D, B, ~I, ~G, E, H, ~J, F, ~K, A
│  │           ~D, C, D, ~I, ~G, E, H, (G | H), ~J, (C & D), F, ~K, ((B | (C & D)) -> A), A (closed)
│     ~D, (E -> F), ~I, K, E, (A -> (B | (C & D))), H, (G | H), F, ~K, ((B | (C & D)) -> A), ~G (closed)
   F, ~D, J, (J -> K), K, E, (A -> (B | (C & D))), H, (G | H), (E -> F), ~K, ((B | (C & D)) -> A), ~G (closed)
