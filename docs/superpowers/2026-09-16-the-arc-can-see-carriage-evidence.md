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

## 7. What this loop cost — its own CI red, recorded rather than quietly fixed

**APPENDED 2026-09-16, after PR #243 merged at `cf077fd`.** Under § Documentation governance this
file is Evidence and append-only from `5743af3`: this section is an **addition**, nothing above it
is edited, and the declared `Doc impact: none` is untouched. It is written because the loop's own
failure is evidence, and a record that shows only the parts that went well is the kind of artifact
[[R187]] exists to refuse.

**The first CI run failed.** Run `35134737753`, head `d71ffe1`, job `test`, 14m44s:

```
1 failed, 1566 passed, 156 skipped, 1 xfailed, 3435 warnings in 884.86s (0:14:44)
FAILED tests/test_cockpit.py::test_the_live_newest_handoff_declares_what_it_serves
  - AssertionError: …-the-arc-can-see-carriage-handoff.md declares no readable `**Serves:**`
```

**The cause, read rather than guessed.** `cockpit._serves_of` (`scripts/cockpit.py:400-417`) takes
the **first whitespace-delimited token** after the field. The handoff declared
`**Serves:** prog:criterion:tab:11.` — with a trailing period — so the token carried the period,
`cid` became `tab:11.`, and membership in `_criterion_ids()` (which holds `tab:11`) failed. A
criterion token outside that set is a **refusal, not a default**, so `serves()` returned `None`.
Repaired at `b807116` to the live form every other handoff on disk uses:
`**Serves:** prog:criterion:<rung>:<nn> — <why>`.

**The process defect is the part worth keeping, and it is not "I forgot a test".** The gates run
before pushing were the ones this diff *names* — arc manifest/queries/landscape/ablation, doc
governance, the new corpus oracle. `tests/test_cockpit.py` is named nowhere in the diff. But
`cockpit._loop_docs()` (`:314-322`) globs **every** dated `*handoff*.md` and `_newest_loop_doc()`
is `max()` by basename, so **adding a handoff silently changes which document that module reads**.
A docs-only file moved a test that no reasoning about the code change could have reached.
**The rule this yields: a change that adds a dated `*handoff*.md` or `*brief*.md` must run
`tests/test_cockpit.py`.**

**A second near-miss, caught only by a contradiction.** Locating that lint used
`files=$(grep -rl … ); pytest $files` — and **zsh does not word-split unquoted variables**, so the
whole string was passed as ONE argument and pytest reported `file or directory not found` for
`tests/test_source_citations.py`, a file `grep` had just listed as existing. The gate never ran
while appearing to have run. It was chased because "missing" and "just listed by grep" cannot both
be true; run properly it is **8 passed**. A test runner reporting a file absent is a shell finding
until proven otherwise.

**The fix's verification, before the second push** — the omission above, repaired systematically by
asking which modules *read* what this change writes (loop docs, the manifest, the register), not
which ones it names:

| gate | result |
| --- | --- |
| `tests/test_cockpit.py` (the missed module) | **24 passed** |
| `cockpit.serves()` | **`tab:11`** |
| `tests/test_source_citations.py` (the lint that had not run) | **8 passed** |
| `tests/test_residue_register_integrity.py` + `test_first_seen.py` | **16 passed** |
| `tests/test_docgov_extract.py` | **22 passed** |
| `tests/test_doc_governance.py` | **7 passed** |

Run `35137048063` (head `b807116`) completed **success**; PR #243 merged `2026-09-16T19:08:07Z` as
`cf077fd`. **The four cited line ranges above were re-measured on the merged tree**, not carried
from the session that wrote them.
