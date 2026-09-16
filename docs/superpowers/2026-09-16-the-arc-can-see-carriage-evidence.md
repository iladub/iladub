# Evidence — the arc gains a criterion that can see CARRIAGE

**Serves:** prog:criterion:tab:11 — the criterion this loop authors.

**Date:** 2026-09-16. **Tree:** branch `the-arc-can-see-carriage`, cut from `main` at `e394c34`.
**No shipped file edited. No behaviour changed.** One criterion authored, one oracle added.

**Doc impact: none.**

---

## 1. What was authored, and the ruling it discharges

`2026-09-16-ship-the-switch-ruling.md:144` ruled: *the next loop authors a criterion whose oracle
is CELLS AND TRIPLES, and [[R238]] blocks that criterion.* That is done — `prog:criterion:tab:11`,
`prog:met false`, `prog:blockedBy "R238"`, oracle `tests/test_carriage.py`.

**The gap it fills, restated as a measurement rather than a complaint.** The arc's ten `tab`
criteria count escalation REASONS and its seven `etkl` criteria read the document SCORE. PR #239
moved bfs p5 from 404 placed cells to 496 and the document from 14251 to 15354 triples; the score
held at `0.8850746269` to ten decimal places and the escalation-reason census came back identical.
So the arc was blind to that work **by construction** — [[R240]] one level up.

## 2. Which rung — a DECISION, and it turned out to be forced

The ruling said this was a decision, not a lookup, and to say why. **It is forced, and the thing
that forces it is a test, not a preference:**

```
$ sed -n '802,832p' tests/test_arc_manifest.py
def test_etkl_criteria_agree_with_the_corpus_manifest():
    assert set(asserted) == set(computed), (
        "every corpus document must have exactly one etkl criterion and vice versa; ...
    assert sum(computed.values()) == 3
```

The `etkl` rung is in **bijection with the corpus register**: an eighth `etkl` criterion naming no
eighth document goes red the moment it is authored. M6 forbids a sixth rung. So the choice was
`etkl` or `tab`, and only one admits the row. `tab` also already hosts a criterion that is not an
escalation reason — `tab:10`, widened past the nine reasons by D3 — so this is a precedent, not a
new shape on that rung.

**The ruling's other half is honoured too:** R238 was NOT added to `etkl:05`'s `prog:blockedBy`.
Closing R238 advances neither `etkl:05` (the score held) nor tab:02/07/09 (the reason census was
identical), and the manifest's own rule (`:1155`) says an edge names a row *whose closure would
advance this criterion*. R238 blocks `tab:11` because closing it and meeting `tab:11` are the
**same act**.

## 3. The reading this tree produces today — MEASURED, not inherited from the ruling's prose

```
$ PYTHONPATH=src .venv/bin/python -c "...compile_document('corpus/gov-stats/bfs-population-bilan-2023.pdf')..."
score 0.8850746268656716
triples 14251
page 5 sum_cells 404  regions [... ('RegionKind.RECORD_TABLE', 'asserted', 404), ...]
page 6 sum_cells 267  regions [6 x ('RegionKind.RECORD_TABLE', 'asserted', ...)]
adopted [5]
```

Two facts the ruling did not state and the oracle depends on:

- **p5's 404 cells sit in exactly ONE region** — a single `asserted` `RECORD_TABLE`. The per-page
  sum and the per-region count are the same number here, so the oracle may count either.
- **p6 carries 267 cells across 6 asserted regions**, and p6 is not a decoration page. That is a
  free CONTROL the corpus was already holding: a change that moves p6 is not the change the
  criterion asks for. Shipping it beside the p5 pin is the lesson PR #241 paid for — a total check
  and a pointwise check disagree informatively.

## 4. FALSIFICATION (CLAUDE.md § Plan authoring discipline, rule 4)

Both oracle tests were falsified by inverting what they pin, then restored.

**The strict xfail — the stronger arm.** A `strict=True` xfail that never XPASSes is decoration.
Setting the expectations to *today's* reading (404 / 14251) must make it XPASS, and an XPASS under
`strict=True` is a suite FAILURE:

```
$ .venv/bin/python -m pytest -m corpus tests/test_carriage.py -q -rxX     # P5 set to 404 / 14251
____________ test_bfs_p5_carries_the_row_label_and_percent_columns _____________
[XPASS(strict)] UNBUILT, not broken: ...
2 failed in 62.72s
```

**The control.** `P6_CELLS = 266`:

```
E       AssertionError: assert 267 == 266
```

**Restored, and green:**

```
$ .venv/bin/python -m pytest -m corpus tests/test_carriage.py -q -rxX
XFAIL tests/test_carriage.py::test_bfs_p5_carries_the_row_label_and_percent_columns - UNBUILT, not broken: ...
1 passed, 1 xfailed in 68.89s
```

**What the first arm proves is the forcing function.** The day the blanket refusal lands, this
test XPASSes and the suite goes RED until a hand flips both the marker and `prog:met`. That is
what keeps `prog:met` a reviewed assertion rather than a side effect — the manifest's own rule is
that code never writes it.

## 5. Gates run

| gate | result |
| --- | --- |
| `tests/test_arc_manifest.py` + `test_arc_queries.py` (M1, M2b, M5, M5b, M7, M9b, M10, M21 …) | **51 passed** |
| `tests/test_arc_landscape.py` + `test_arc_ablation.py` | **15 passed** |
| `tests/test_doc_governance.py` (after the register edits) | **7 passed** |
| `tests/test_carriage.py -m corpus` | **1 passed, 1 xfailed** |

The landscape cache was regenerated in the same commit, which is the trap the ruling named:
**43 → 44 criteria**, **14 → 15 ready**, and `R238` enters the §4 reach table at 1 gated criterion.
The cockpit strip now reads `tab 1/11` and `frontier 14`.

## 6. What this does NOT establish

- **Nothing was built.** `_boundaries_from_decoration` is still consulted
  (`src/iladub/etkl/datagrid.py:340-349`); p5 still reads 404. The criterion is `met false` and the
  switch is the next loop's.
- **The oracle is one document.** It pins bfs; it does not measure carriage corpus-wide. A general
  carriage gauge would be a different instrument and is not claimed here.
- **GREEN CI IS NOT EVIDENCE ABOUT `tests/test_carriage.py`.** `corpus/` is gitignored, so both
  tests SKIP in CI. They were run by hand, locally, and the figures above are that run.
- **The known risk the ruling accepted stands**: this corpus holds no page whose decoration
  rectangle is both adopted and correct, so it cannot produce the counter-example that would refute
  a blanket refusal.
