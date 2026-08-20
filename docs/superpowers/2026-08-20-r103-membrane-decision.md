# R103, closed — `tab-datagrid.ttl` stays out of the membrane ontology

**Date:** 2026-08-20 · **Branch:** `r103-membrane-decision` · **Resumes:**
`2026-08-20-r103-membrane-half-handoff.md` · **Doc impact:** `increment`
(`docs/wiki/concepts/data-grid.md` gains § *The membrane does not validate against this module*)

## The question

Is `vocab/ontology/tab-datagrid.ttl` parsed into `compile._FULL_ONT`? Open since 2026-08-17; the
half of R103 that was always the one that mattered.

**Answer: no.** Not on balance — admitting it is a *provable no-op*.

## What the handoff asked for, and what was run instead

The handoff's next concrete action was the 2026-08-10 protocol: compile the 7 corpus documents
once, validate twice against the tab shapes, report what moves. It also flagged its own weakness,
correctly: *"a protocol that showed 'no verdict moves' may not be the right question here — no
verdict moving could equally mean the change buys nothing."*

So the protocol was run **widened**: every page closed twice and the two closures **diffed**, plus
both membrane legs validated each time. The diff is what distinguishes "harmless" from "inert",
and it is the measurement that answers the question.

Script: `measure_datagrid_membrane.py` (scratchpad, not committed — it composes committed
primitives only: `compile_tables`, `membrane.subclass_closure`, `membrane.validate`).

## The measurement

7 documents, 27 pages, `validate_shapes=False` for the compile, both legs validated.

| | base `_FULL_ONT` | `+ tab-datagrid.ttl` |
| --- | --- | --- |
| ontology triples | 1023 | 1183 (+160) |
| `rdfs:subClassOf` axioms | 21 | 27 (+6) |
| **closure delta, per page** | — | **0 triples, all 27 pages** |
| tab-leg verdict | `(True, 0)` ×27 | `(True, 0)` ×27 |
| dec-leg verdict | `(True, 0)` ×27 | `(True, 0)` ×27 |

Nothing moved because nothing *can*. `membrane.subclass_closure` (`membrane.py:448`) reads only
`rdfs:subClassOf` from the ontology graph and never mixes it into the payload. Of the 160 triples
the file adds, the membrane consults 6 axioms, and each is inert:

| axiom | why it fires on nothing |
| --- | --- |
| `UniformGrid ⊑ DataGrid` | `datagrid.py:622-623` emits `tab:DataGrid` **and** `TAB[grid.grid_type]` on the same node — the closure would re-derive a triple already present |
| `MixedGrid ⊑ DataGrid` | same |
| `AggregatingGrid ⊑ DataGrid` | `tab:AggregatingGrid` emitted nowhere in `src/` (0 hits) |
| `DecorationUniverse ⊑ ColumnUniverse` | `datagrid.py:626` emits it as the **object** of `tab:universeSource`, never as `rdf:type`; the closure materialises on `rdf:type` only |
| `AlignmentUniverse ⊑ ColumnUniverse` | same |
| `PivotFieldRepeatLabels ⊑ SuppressedRepeat` | emitted nowhere in `src/` (0 hits) |

## The finding that outranks the decision

**The probe's `ONT_VISIBLE` class, and this row's own 2026-08-18 entry, both rested on a false
premise about the membrane.**

- the probe said `ONT_VISIBLE` means the membrane *"sees the type and there is no hazard"*;
- the row said the 12 `OUTSIDE_MEMBRANE` nodes are *"this row's membrane question with a number
  attached"* — implying loading the file would resolve them.

Neither holds. **No ontology subject reaches an engine at all.** Measured on the 4,773-triple
closure of `ons-index-of-services-2026-02.pdf` p7: **0** `tab:`-namespace subjects, and each of
`(tab:Quantity a tab:CellDatatypeFamily)`, `(tab:NonDegeneracy a tab:GridAxiom)`,
`(tab:Text a tab:CellDatatype)` is absent from it.

So the 2 `ONT_VISIBLE` and the 12 `OUTSIDE_MEMBRANE` nodes are **the same situation**. The split
between them reports which *file declares the type* — a fact about the vocabulary, useful for
attributing a disagreement to the module that must fix it — and nothing about the membrane's
reach. The names are kept for exactly that reason; only the inference was wrong.

This is also why the decision is not close. The repair that motivated the question would not have
performed the repair.

## The separability question, answered

The handoff listed as unverified: *whether admitting the file turns the `tab:Text` contradiction
into a refusal — and if it does, the two questions are one.* It does not. **The two questions are
separable.** MEASURED: the only `sh:class` in either tab shape file is `sh:class tab:BBox`
(`tab-shapes.ttl:19`, one occurrence), and none of the 13 shape-targeted classes is
`tab:CellDatatypeFamily`. Nothing in the membrane can see the contradiction whatever is loaded.

Also re-measured against the current tree, as the handoff asked: **there is still no
`tab-datagrid-shapes.ttl`** (`find . -name 'tab-datagrid*'` returns the ontology file alone), so
the change was indeed closure-only — which is what made the closure diff the decisive instrument.

## What shipped

1. **The decision, recorded at its own absence** — `compile._build_membrane`, beside the
   2026-08-10 note whose protocol it repeats. It carries the inertness table, the measurement, and
   the reversal condition.
2. **`test_tab_datagrid_axioms_are_unreachable_by_every_membrane_shape`**
   (`tests/etkl/test_compile_membrane_shapes.py`) — pins the condition that would reverse the
   decision rather than the decision itself. It reads the added superclasses out of the vocabulary
   (never a hardcoded list) and fails, naming R103, if any membrane shape targets or
   `sh:class`-constrains `tab:DataGrid`, `tab:ColumnUniverse` or `tab:SuppressedRepeat`.
3. **The probe's two false claims corrected in place** —
   `scripts/probe_domain_range_agreement.py`. No class renamed, no output format changed.
4. **The wiki increment** and the register close.

## FALSIFICATION

The new test's subject inverted — a shape made to reach one of the three superclasses:

```
$ cat >> vocab/shapes/tab-shapes.ttl        # temporary probe
tab:FalsifyDataGridShape a sh:NodeShape ; sh:targetClass tab:DataGrid ;
    sh:property [ sh:path tab:onPage ; sh:minCount 1 ] .

$ pytest tests/etkl/test_compile_membrane_shapes.py::test_tab_datagrid_axioms_are_unreachable_by_every_membrane_shape -q
E  AssertionError: a membrane shape now reaches a superclass tab-datagrid.ttl introduces
   (['https://w3id.org/iladub/tab#DataGrid']) — admitting the file is no longer a no-op.
   REOPEN R103 and re-run the 27-page closure-delta measurement.
1 failed in 1.50s

$ cp /tmp/tab-shapes.bak vocab/shapes/tab-shapes.ttl     # restored
$ pytest tests/etkl/test_compile_membrane_shapes.py -q
9 passed in 8.17s
$ git diff --stat vocab/                                  # (empty)
```

The test fails for its own reason, with the message that tells the next reader what to do.

## What this loop did NOT do

- **It did not fix the two real emitter/vocabulary disagreements** — `tab:universeSource`'s domain
  (2 nodes) and `columnFamily -> CellDatatypeFamily` on `tab:Text` (2 nodes). They are real, they
  are unenforceable by the membrane *by construction*, and they belong to **R61**, which already
  carries them. What R103 adds is that no membrane-ontology change can ever reach them.
- **It did not re-open whether `subclass_closure` should mix the ontology in.** That is the
  2026-08-06 subclass-only-closure decision, deliberately untouched here; this loop measured its
  consequence, it did not relitigate it.
- **It did not write a spec.** The handoff said the decision follows the measurement — it did.
