# M-B — R100's own cheap close, tested and refuted

**Date:** 2026-08-17 · **Tree:** `main` @ `c83febc`, clean · engine `rudof`
(`membrane.engine_name()`, `src/iladub/etkl/membrane.py:19`) · no tracked file modified

R100 offers two closing conditions. The second is the cheap one:

> "a measured finding that no wired shape's liveness differs by leg except this one, which would
> make the (shape, leg) key unnecessary."

**Measured across all 34 wired node shapes and all 7 corpus documents: five differ. The
condition is not met.**

## Method

Both `_validate` references were spied, not one: `document.py:110` binds its own name at import
(`from .compile import … _validate`), so patching `compile._validate` alone would have missed
the document leg entirely. Each spy subclass-closed the data graph with
`membrane.subclass_closure(graph, compile_mod._FULL_ONT)` and applied the vacuity registry's own
`focus_nodes()` (`tests/etkl/test_vacuity_registry.py:154`) and `unreachable_terms()` (`:184`),
then delegated to the real `_validate`. All 7 documents compiled with `validate_shapes=True`;
all conformant.

Scripts in scratchpad (`measure_leg_liveness.py`, `analyse.py`, raw `leg_liveness.json`).

## Call-site facts

- Page leg `compile.py:1101`, gated `:1097-1100` on `validate_shapes and (any tab:RecordTable
  or any tab:HierarchicalTable)`.
- Document leg `document.py:1585`, gated `:1584` on `validate_shapes and (recognized or
  section_facts)`.
- Both legs run the *same* two shape sets (`compile.py:453-465`), so only the data graph differs.

**Citation drift, worth fixing when the loop touches this code:** R100's row *and* the comment at
`compile.py:408-409` both cite `compile.py:1083` for the page call. At HEAD, `:1083` is
`if denom:`.

```
  cbh-stem               page-calls=  2  doc-calls=1
  graincorp-capacity     page-calls=  1  doc-calls=0
  graincorp-stem         page-calls=  3  doc-calls=1
  apple                  page-calls=  2  doc-calls=1
  bfs                    page-calls=  2  doc-calls=0
  ons                    page-calls=  1  doc-calls=0
  who-wfa                page-calls=  3  doc-calls=1
```

**3 of 7 documents never call the document leg at all.** 14 page calls against 27 corpus pages
(the tab-fact gate), and not 1:1 with pages either way — `document.py:1240,1303,1440` all call
`compile_tables`.

## The answer, in two readings that disagree

The task defined liveness as focus nodes; the guard's actual verdict function `idle_shapes()`
(`test_vacuity_registry.py:190`) uses focus nodes **or** term reachability. Both are reported
rather than one being picked.

**By focus nodes alone — `dec:EscalationShape` does not differ by leg at all.** It targets
`dec:DecisionHolon` (`vocab/shapes/escalation-shapes.ttl:17`) and every page graph carries
decision holons (`decisionlog.py:50`): 11–61 focus nodes on every one of the 14 page calls.
Four *other* shapes differ:

| shape | page tot / max | doc tot / max |
| --- | --- | --- |
| `dec:EventShape` | 0 / 0 | 13 / 10 |
| `dec:ExpansionRequestShape` | 0 / 0 | 13 / 10 |
| `tab:ContinuesColumnDisciplineShape` | 0 / 0 | 94 / 60 |
| `tab:InLogicalColumnDisciplineShape` | 0 / 0 | 131 / 80 |

**By the guard's own criterion — five differ, and `dec:EscalationShape` is the only one that
differs by criterion 2:**

```
page idle reasons:
  dec#EscalationShape  — c2: unreachable constrainedBy, escalatedTo, maxSeverity, order, withinScope
  dec#EventShape       — c1: 0 focus nodes on every graph
  dec#ExpansionRequestShape          — c1: 0 focus nodes
  tab#ContinuesColumnDisciplineShape — c1: 0 focus nodes
  tab#InLogicalColumnDisciplineShape — c1: 0 focus nodes
```

R100's prose ("binds rows on one leg and none on the other") matches the second reading.

**The four others are structural, not corpus accidents.** `tab:continuesColumn` /
`tab:inLogicalColumn` are written **only** at `document.py:736-737`, and the shapes target them
via `sh:targetSubjectsOf` (`tab-shapes.ttl:367,411`); `dec:Event` / `dec:ExpansionRequest` are
minted **only** by the furnishing query at `document.py:1575`. **No page graph can ever contain
any of them.** So this is not "the corpus happens not to exercise it" — it is a shape set applied
to a scope that cannot, in principle, produce its focus nodes.

## The finding neither row anticipated

**`dec:EscalationShape` is reachable on only 2 of the 4 doc-leg calls** (apple and who-wfa; not
cbh-stem, not graincorp-stem):

```
  every PAGE call (all 14): unreachable = [constrainedBy, escalatedTo, maxSeverity, withinScope, order]
  cbh-stem       doc: focus= 65  unreachable = [constrainedBy, escalatedTo, maxSeverity, withinScope, order]
  graincorp-stem doc: focus= 36  unreachable = [same five]
  apple          doc: focus=119  unreachable = []
  who-wfa        doc: focus= 81  unreachable = []
```

It reads as live **because `idle_shapes` intersects the unreachable sets across graphs** and the
intersection is empty. A shape unreachable on half the documents it is applied to is reported as
healthy. Whether that aggregation is a defect or the intended corpus-wide semantics is
**undecided** — the docstring argues for it in the focus-node case (`:196-198`) and is silent on
criterion 2. **Candidate new residue; decide in the spec.**

## Also established, and larger than R100

**The registry measures 7 final `rep.graph`s (`:316-317`); the document membrane validates only
4 of them.** The guard's graph set and the membrane's graph set are different objects, and
nothing in the repo said so. This is a fourth axis alongside gate, phase and leg.

## Caveats

- **Five is a FLOOR, not a ceiling.** The 3 documents whose doc-leg gate never opens had no
  doc-leg graph to capture. Adding their final graphs can only make more shapes live on the doc
  side, so the differing set can only grow. Stated by the measuring agent; not independently
  re-derived.
- Pages compiled twice (`document.py:1303,1440`) were counted per `_validate` call, not
  deduplicated — the question is what the membrane saw.
- The **grounding** membrane (`feed.py`'s `_GROUND_SHAPE_FILES`) is a third leg and was not
  measured; it is outside `compile._validate` entirely.
