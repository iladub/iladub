# M-A — the handoff's named first measurement, taken

**Date:** 2026-08-17 · **Tree:** `main` @ `c83febc`, clean · **Engine:** default leg (see § Caveats)

The R97–R101 handoff named one action to run *before any spec exists*:

> **Measure whether `tests/test_zero_etl_export.py`'s compiled graph gives `tab:BaseFactShape`
> a focus node.** … if the export leg already exercises base facts, R97 is partly a stale row
> rather than a corpus gap, and the loop starts from a different question.

It does. And the answer is not the one either branch of that sentence anticipated.

## The measurement

Script: `scratchpad/m_a_basefact.py`. It imports the vacuity registry's **own**
`focus_nodes()` and `membrane.subclass_closure(rep.graph, compile_mod._FULL_ONT)`, so the
figures are directly comparable with R97's "0 focus nodes on all 7 corpus documents"
(`tests/etkl/test_vacuity_registry.py:153-163`, `:317`). It also monkeypatches
`compile._validate` to record what the membrane is actually handed.

```
=== _validate calls during compile_tables ===
calls: 1  (triples, tab:BaseFact instances seen): [(405, 0)]

=== raw tab:BaseFact instances ===
rep.graph after analyze() : 8
dr.base_facts             : 8
dr.oracle_ok              : True

=== focus nodes, the four R97 shapes (registry method, subclass-closed) ===
shape                             pre-analyze  post-analyze
AggregationCellShape                        0             0
BaseFactShape                               0             8
PivotedDimensionShape                       0             1
SectionTotalShape                           0             0
```

## What it establishes

**1. The membrane never sees a base fact — not on this fixture, and not anywhere.**
`_validate` ran **once** during `compile_tables`, on a 405-triple graph holding **0**
`tab:BaseFact` instances. The 8 base facts appear only after `analyze(rep)`, which mutates
`rep.graph` in place. Measured, not read:

- `_validate` has exactly two call sites — `compile.py:1101` and `document.py:1585`
  (`grep -rn "_validate(" src/iladub/`).
- `analyze(` is called from **`tests/test_zero_etl_export.py:56`,
  `tests/etkl/test_denormalization.py:222`, `tests/etkl/test_denorm_integration.py:14,45`,
  and `demo/etkl_1a_showcase.ipynb:1168` — and from no file under `src/`.**
- `document.py:955` already says so in a comment: *"`analyze`/denormalization is an opt-in …"*.

So both membrane legs run **before** the facts these shapes validate exist. This is a
*phase* restriction, and it is independent of R102's *gate* restriction (both `_validate`
sites additionally require tab-facts). Two different reasons a wired shape sees nothing,
stacked on the same call sites.

**2. R97's four shapes do NOT adjudicate together.** The handoff listed that as undecided
(§ Unverified: *"Whether they adjudicate together or separately is undecided"*). They split
2/2:

| shape | post-`analyze()` focus nodes | what it actually is |
| --- | --- | --- |
| `tab:BaseFactShape` | **8** | **not** a corpus gap and **not** a dead shape — a shape whose feature a shipped test exercises, wired to a membrane that runs before the feature exists |
| `tab:PivotedDimensionShape` | **1** | same category |
| `tab:AggregationCellShape` | 0 | still unadjudicated — corpus gap or dead shape |
| `tab:SectionTotalShape` | 0 | still unadjudicated — corpus gap or dead shape |

**3. Two registry rows are stale as *stated*.** `VACUITY_REGISTRY`
(`test_vacuity_registry.py:108`, `:121`) gives both `BaseFactShape` and
`PivotedDimensionShape` the reason *"corpus does not exercise it"*. The corpus does not, but
**`tests/test_zero_etl_export.py` does** — and that test has run in CI on every push since
`09b96a8`. The rows are not wrong about the number; they are wrong about the cause, which is
the same defect R98 records against spec §3's M7 table.

**4. It does not trip the guard.** `test_no_registered_shape_has_gone_live` measures the 7
corpus documents (`:298-317`), where both shapes remain at 0. A shape can therefore be
registered-idle, be genuinely exercised by a shipped test, and the guard stays green —
because the guard's scope and the shape's scope are different, which is R100's complaint
arriving through a third door.

## Caveats

- **One fixture, not the corpus.** This measures the zero-ETL fixture PDF built by
  `demo/etkl_demo_data.report_between_prose_pdf`, which is what the handoff asked for. The
  7-document corpus figures in R97 are not re-measured here and are not disputed.
- **Engine leg not pinned.** Run on the default membrane leg; the handoff's standing note
  that "every figure in R87 and these rows is the rudof leg" applies to the comparison
  figures, not to the focus-node counts above, which are computed in rdflib by the registry's
  own method and do not involve a SHACL engine at all.
- **`AggregationCellShape` and `SectionTotalShape` are 0 on this fixture only.** That is not
  evidence they are dead; this fixture is a denormalized report, not a document with section
  totals.
