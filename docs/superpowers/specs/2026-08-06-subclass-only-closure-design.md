# Subclass-only closure — the membrane's inference, narrowed to what shapes use — design

**Date:** 2026-08-06 · **Status:** closed 2026-08-06 ·
**Discharges:** R58 (owlrl is the membrane's bottleneck); closes the **R19 hazard class at its
root** · **Predecessor:** `2026-08-06-membrane-engine-swap-design.md` §7, which split this
change out precisely because it changes behaviour

**Doc impact:** none — no new vocabulary, no new concept, no site or wiki page contradicted.
The change is to how the membrane's input graph is derived; every shape and query is
untouched.

## 1. Problem (measured 2026-08-06)

With the SHACL engine now rudof, the membrane's cost has moved: RDFS closure **1.311 s**
versus rudof's own validate **~0.08 s**, roughly two-thirds of a ~2.1 s per-validation total.
The closure is Python (owlrl) and is now the thing worth attacking.

It is also doing far more than the shapes need. Measured on the real stem page-0 graph, full
closure versus `rdfs:subClassOf`-only materialisation over asserted types:

| what full closure adds that subclass-only does not | count | verdict-relevant? |
| --- | --- | --- |
| `rdf:type rdfs:Resource` | 2,105 | no — vacuous, no shape targets it |
| ontology-node types (`Class`, `ObjectProperty`, `DatatypeProperty`, `Property`, `Ontology`) | 207 | no — these are axiom nodes, not data |
| `tab:LabelCell` (via a property domain) | 18 | **no — no shape targets `tab:LabelCell`** |

`tab:Cell` — the one targeted class that domain typing *could* have supplied — loses nothing,
because every cell is explicitly typed at emission. **Zero verdict-relevant type assertions
disappear.** Timing: closure **1.311 s → 0.047 s** (~28×), taking the membrane from ~2.1 s to
~0.75 s.

## 2. The change

`membrane.rdfs_closure` is replaced by:

```
membrane.subclass_closure(data_graph: Graph, ont_graph: Graph) -> Graph
```

It reads the ontology **only** as a source of `rdfs:subClassOf` axioms — transitively closed
once — and materialises every supertype over the data graph's asserted types. No owlrl. No
`inoculate()`.

**Dropping `inoculate()` is deliberate** (François, 2026-08-06). The predecessor loop adopted
pySHACL's `inoculate()` in order to *match* pySHACL's inference exactly; this loop
deliberately departs from that inference, so matching its ontology mix-in is no longer a
goal and keeping it would be cargo-cult. Measured: without it the validated graph is 9,028
triples instead of 9,730, closure 0.047 s instead of 0.053 s, and both conform identically at
the gate and at the full shape set. The semantic gain is the real point — the validated graph
becomes **data plus its own type closure, nothing else**, with no ontology nodes present as
potential focus nodes, and our last dependency on a pySHACL internal goes away.

**The literal-subject filter stays**, but changes role. It existed because owlrl emitted
1,533 triples with literals as subjects (illegal RDF that rudof's strict parser refuses).
Nothing in this loop can produce such a triple, so the filter becomes a cheap invariant guard
rather than a workaround — and is documented as such, not silently deleted.

## 3. The evidence (the deliverable)

The risk of this change is **not** that something starts failing. It is that a shape silently
stops *seeing* a node, so a violation goes uncaught — the §7 credibility direction, and the
worst regression class in this project. The evidence must therefore be about focus nodes, not
just verdicts.

`tests/etkl/test_closure_equiv.py` — a committed **closure differential**, the direct analogue
of the predecessor loop's engine differential:

1. **Verdict parity** — for every committed `tests/tab-*-leak.ttl` fixture and for real
   compiled page graphs, full closure and subclass-only closure must yield the **same
   conformance verdict**.
2. **Focus-node parity (the load-bearing leg)** — for the same inputs, the **set of focus
   nodes per shape must be identical** between the two closures. Focus nodes are exactly what
   typing determines, so this proves directly that no shape lost sight of a node. A leak
   fixture whose violation stops being caught is a **hard blocker**, never a test to adjust.
3. **R58's mandated `sh:class` case** — under full closure, `tab:hasBBox rdfs:range tab:BBox`
   types every object as a `tab:BBox`, making the shape set's single `sh:class` constraint
   (`EntryCellPhysicalShape`'s `hasBBox`) **unfalsifiable**. Once range typing is gone it
   becomes real, so this loop must prove it: a `hasBBox` pointing at a node that is not a
   `tab:BBox` must be refused, **by both engines**. Prerequisite verified — all 586 bbox
   objects on the real page are explicitly typed, so nothing depends on the fallback today.

## 4. Success criteria

- **Corpus scores byte-identical**: stem **0.9655** / 2152 cells, CBH **0.9047**, apple
  **0.0105540897**. Scores derive from conformance decisions, so divergence surfaces there.
- Page-0 stem compile below the current **12.5 s**, with the measured number recorded.
- Closure battery green; the predecessor's engine battery (`test_membrane_equiv.py`) still
  green; full suite green apart from the known machine-environmental `test_release_gate`.
- R58's register row closed; R19 recorded as closed **at its root** (a node can no longer
  become a `tab:Cell` merely by carrying a bbox).

## 5. Out of scope, named

- **R57** (the membrane redundancy — the final pass re-checking gate-covered shapes) stays
  registered; unchanged by this loop.
- **R59** (the engine battery's positive leg is corpus-only and single-page) stays registered.
- **rudof's n-triples parse (~0.58 s) becomes the new dominant membrane cost** once closure
  drops to 0.047 s. That is measured into R58's replacement register row, not fixed here.

## 6. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate: `subclass_closure` is PROCEDURAL engine glue — a transitive closure over
  declared axioms, no domain decision, no tuned constant. Every shape and `.rq` is untouched.
- §7 credibility: the focus-node parity leg exists because a membrane that silently stops
  refusing is worse than a slow one.
- Source ownership: the ontology is read, never edited.

## 7. Close-out (measured 2026-08-06)

- **Page-0 stem compile:** 12.5 s → **10.1 s**; score **0.9560**, byte-identical.
- **Whole stem document:** 166 s → **151 s**; score **0.9655**, byte-identical.
- **Corpus pins** (`tests/test_corpus_stem.py` + `tests/test_cbh_e2e.py`): **13 passed in
  223.32 s** (stem 0.9655, CBH 0.9047 — both byte-identical).
- **Closure + engine batteries together** (`test_closure_equiv.py` + `test_membrane_equiv.py`):
  **33 passed in 285.28 s** (closure differential 17, engine differential 16).
- **Full suite:** **996 passed, 1 failed, 5 skipped, 1232.34 s** — the failure is the known
  machine-environmental `tests/test_release_gate.py::test_since_date_fallback_and_previous_tag`
  (a bare env dict without `PATH` hits this machine's broken Xcode git shim; zero branch commits
  touch it; green in CI).
- **Closure timing:** full RDFS closure 1.311 s → subclass-only **0.047 s**.

**§4's "corpus scores byte-identical" criterion was NOT met as written.** Stem and CBH held
byte-identical; **apple's did not**: **0.0105540897 → 0.0326975477**. Per §2 Step 2's own stop
condition ("if any score moves, STOP and report BLOCKED — a moved score means the closure
changed a real verdict, which outranks the speedup"), this was investigated rather than waved
through.

Diagnosis: apple p1's region 4 flipped from `MATRIX_AMBIGUOUS` to **asserted (8 cells)**. Two
nodes — `mtable4-cc0_2` and `mtable4-cc1_2` — are `iladub:CandidateConcept` instances
(escalation records that carry a `tab:hasBBox` for provenance) with **no `tab:cellText`
property at all**. Under full closure, `tab:hasBBox`'s `rdfs:domain tab:Cell` typed them as
`tab:Cell`, so `tab:WrappedCellShape` fired on them and refused the entire region. That is
**R19 verbatim** — and it proves R19 was **not a latent hazard but an active defect**,
suppressing a real region on a real document. A shape was firing on something that was never a
cell.

**Adjudication (François, 2026-08-06):** accept as a measured fix. The score movement is the
loop's intended effect, not a regression — the criterion as literally written ("byte-identical")
is superseded by the criterion the loop actually exists to serve (§3: no shape silently stops
seeing a node it should see). The criterion is recorded here as not met, honestly, rather than
reworded after the fact to match the outcome.

All other §4 criteria held: page-0 below 12.5 s (10.1 s), both batteries green, full suite green
apart from the known machine-environmental failure, R58 closed, R19 closed at its root.
