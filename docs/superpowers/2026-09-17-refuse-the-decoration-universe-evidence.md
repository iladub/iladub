# Evidence — the decoration universe is refused, blanket: the switch shipped

**Serves:** prog:criterion:tab:11 — the carriage criterion, met by this loop

**Date:** 2026-09-17. **Tree:** branch `refuse-the-decoration-universe`, cut from `main` at
`6145412`.

**Doc impact: none.** Measured, not assumed: no Assertion-class page (the `mkdocs.yml` nav)
mentions the decoration universe or `tab:DecorationUniverse` —
`grep -rln "decoration\|DecorationUniverse" docs/ --include="*.md"` outside
`docs/{superpowers,wiki,loops,w3id}/**` returns nothing. The wiki page that *does* describe it
(`docs/wiki/concepts/data-grid.md`) is Wiki class, updated here, and never published.

---

## 1. What was built

`derive_data_grid` no longer consults `_boundaries_from_decoration`. The column universe is
`bounds, universe = align, "alignment"`, unconditionally, per
`2026-09-16-ship-the-switch-ruling.md`. This is exactly the configuration PR #239 compiled
across all seven documents, so its effect was known rather than predicted.

`_boundaries_from_decoration` and `drawn_rules` are **retained**, not deleted: the ruling names
a document with a correctly-drawn rectangle as the case that reopens it, `drawn_rules` is
independently tested and is raw PROCEDURAL extraction, and `scripts/r239_alignment_universe_gate.py`
rebinds the former. The selection site records why it is no longer called.

**§ 8 classification.** The change *removes* a decision rather than adding one: an ordinal
comparison between two universes is gone, and with it the only site where a drawn rectangle
could decide a column boundary. Nothing tuned was introduced — there is no new constant,
threshold or tolerance in the diff.

## 2. The seam the ruling ordered measured — G0, and it was NOT what the handoff read

The ruling (§ The seam the implementer MUST measure) required measuring the
`if universe == "decoration":` branch at G0 `tab:SeedFollowsUniverse` before deleting or
stranding it. Measured at grid scope over all 7 documents / 27 pages, before the edit:

| page | before | after a blanket refusal |
| --- | --- | --- |
| `ag-trade/cbh-stem-2026-08-03.pdf` p0 | decoration 20c / 50r | alignment 16c / **45r** |
| `ag-trade/graincorp-capacity-2026-08-04.pdf` p0 | decoration 16c / 27r | alignment 15c / 27r |
| `gov-stats/bfs-population-bilan-2023.pdf` p5 | decoration 15c / 46r | alignment **12c** / 46r |

**3 pages reached the branch; 0 reach it after.** The occupancy arm is therefore unreachable —
`universe` is assigned exactly once and can no longer hold `"decoration"` — and it was removed
with its knowledge recorded in place, because a revisit must restore *both* halves together
(seeding a decoration universe by signature instead of occupancy cost capacity 19 of its 27 rows).

**The handoff's § 5b was READ, not run, and it under-read this.** It predicted the bite would be
`test_datagrid.py:1298`'s `assert g.universe == "decoration"` — a label that can no longer be
true. The label was the smaller half: cbh p0 also loses **real rows**. Four oracles failed, not
one.

## 3. The oracle — and the strict xfail doing exactly its job

`tests/test_carriage.py`, run by hand (`-m corpus`; it SKIPS in CI, so green CI is not evidence
about it):

- **Before the flip**, on the tree carrying the refusal: `[XPASS(strict)] 1 failed, 1 passed`.
  This is the FALSIFICATION (CLAUDE.md plan rule 4) and it is stronger than a re-run: the test
  was authored red-on-purpose against the unbuilt state, went red for *being right*, and could
  not be left behind — an XPASS under `strict=True` fails the suite.
- **After removing the marker and flipping `prog:met`**: `2 passed in 66.01s`.

bfs p5 reads **496 placed cells** and the document **15354 triples**, from 404 / 14251. The p6
control is unmoved at **267 cells across 6 asserted regions** — a change that moved page 6 would
not be the change the criterion asks for.

`prog:criterion:tab:11` is now `prog:met true`, `prog:metOn "2026-09-17"`, and its
`prog:blockedBy "R238"` is gone — M8 refuses a met criterion that is still blocked, so closing
the row and meeting the criterion were one act, as the ruling required.

## 4. The cost, recorded rather than hidden — cbh page 0

50 → 45 grid rows. The five, itemised:

| line(s) | what it is | direction |
| --- | --- | --- |
| 26 | a vessel row | **lost** |
| 42, 63, 74 | three of the four panel totals | **lost** — R75's aggregate-witness closure partly regressed on this page |
| 75 | the table-B leak (a row of the *second* table on the page) | **repaired** — it stops leaking |

`aggregates` goes `{20: 10, 42: 16, 63: 14, 74: 5}` → `{20: 10}`. Metadata leak is **0** either
way, so this is capacity, not soundness, and G8's mechanism is intact: panel 1's total still
reconciles exactly over its ten vessel rows, reading no label. What changed is how many rows
reach it.

**Four oracles in `tests/etkl/test_datagrid.py` were re-authored to the measured reading, and
none was relaxed.** `assert not missed` became `assert missed == [26]` and
`assert missed == [42, 63, 74]` — pins, not weakenings: they fail if anything further drops
**and** if a lost row silently returns, so a recovery gets read by a human. The leak test pins
the leak's *absence*. The emitted-aggregate test keeps its claim (the same class, `sum`,
operands that are rows of this grid) and moves only its counts.

This cost was accepted in advance by the ruling (§ Known risk). It is **[[R243]]**, open, with
the cause explicitly UNMEASURED — why the alignment universe's 16 columns fail to place those
four rows is not known, only that they do.

## 5. Collateral the citation lint cannot see

The edit added 19 lines above most of the file, which silently falsified **9 cross-file
citations** naming `datagrid.py:NNN` from `compile.py`, `document.py` and four test modules.

`tests/test_source_citations.py` refuses only **downward same-file** citations (O1), and the EOF
filter (O2) keeps cross-file anchors silent by design — so **the tree would have gone green with
nine wrong anchors**. They were repaired by measuring each cited line's HEAD content and
relocating it by exact full-line match (`622-623 → 641-642`, `599-600 → 618-619`,
`582-583 → 601-602`, `695-697 → 714-716`, `620 → 639`, `706 → 725`, `341 → 363`).

Two were converted to **symbol** citations instead of new numbers — `datagrid.py`'s
`(c) THE NO-CHANGE OPTION` comment — because they had now moved twice and the anchor, not the
number, is what a reader resolves. `compile.py:158` cited the ordinal comparison this loop
deleted; it is re-authored to state the shape rather than cite a line that no longer exists.

**Arithmetic was not enough here and that is worth keeping:** the shift was assumed to be +14/+18
from counting the diff, and a check against those values matched **nothing**. The real shift is
+19 (and +22 between the two edits). Relocation by exact content match is the measurement;
counting added lines is a guess.

## 6. M4 — a near-miss, decided by the clock

`tab:11` was declared 2026-09-16 (merged PR #243, `cf077fd`, `prog:met false`, oracle red on
purpose) and met by this loop. Had the switch landed before midnight, `metOn == declaredOn` and
**M4 would have refused the honest record**: it reads same-day as grandfathering — "written
against evidence that already existed" — which git refutes here. The only ways through would
have been a false `prog:retrospective true` or a false date.

All **7** manifest criteria with `metOn == declaredOn` are genuine grandfathering. A same-day
declare-then-build has no precedent. The maintainer ruled a git-ancestry carve-out and then,
once the date rolled over and the rule lost every live subject, ruled it **deferred** — building
a rule from a near-miss instead of a real instance is [[R188]]'s failure. Recorded as **[[R244]]**
with the carve-out's shape named.

## 7. The register, and a count that moved without progress

R238 **closed** (struck, moved to `residues-closed.md`); R243 and R244 raised. 71/232 → 72/234.

`tests/test_residue_graph.py` pins the structural park-candidate count and went 90 → 92. Measured
by mechanism, as that test's own docstring demands:

- **R243** — new, open, blocks no criterion, and its only register neighbour is the now-closed R238.
- **R242** — *already existed and closed nothing*: its only neighbour was R238, and R238 closing
  removed its last OPEN neighbour.
- **R244** is NOT a candidate — it cites `[[R188]]`, which is open.

So one of the two is a new row and the other is a pre-existing row freed by a closure. Neither is
progress, which is exactly the reading that docstring exists to force.

## 8. What this does NOT establish

- **The corpus cannot falsify the blanket refusal.** No page here has a decoration rectangle that
  is both adopted and correct, so a document with a correctly-drawn rectangle would be regressed
  and could not be detected here. Accepted on the record by the ruling; that document is the case
  that reopens it.
- **The cause of cbh's four lost rows is unmeasured** ([[R243]]). Only the fact and the exact ids.
- **Whether alignment's 12 columns on bfs p5 are the RIGHT 12 is untouched** ([[R241]]) — this
  loop moved cells, and said nothing about column semantics.
- **R74 is not closed** by cbh's leak stopping. R74 is about `tab:StackedGrids` being defined and
  underived; one page's leak closing as a side effect is evidence for that row, not a disposal.
- [[R242]] (footnote markers fusing into the label cell) is untouched.

## 9. Gates run

| suite | result |
| --- | --- |
| `tests/test_carriage.py -m corpus` | 2 passed |
| `tests/etkl/test_datagrid.py` | 59 passed |
| `tests/test_arc_manifest.py` + `test_arc_landscape.py` | 34 passed |
| `tests/test_doc_governance.py` + `test_source_citations.py` + `test_docgov_extract.py` | 37 passed |
| `tests/etkl/test_fallback_region_books_and_names.py` + `test_escalation_furnish.py` + `test_domain_range_agreement.py` | 32 passed |
| `tests/test_residue_register_integrity.py` + `test_residue_graph.py` | 9 passed, then the 90 → 92 pin updated with its mechanism |
