# Handoff — R225 is closed, and what the fallback's retirement leaves open

**Topic:** [[R225]] closed by D1; [[R228]] and [[R229]] raised; [[R227]] closed by refuting its own
open half

**Serves:** prog:criterion:etkl:04 — R225 no longer blocks it. What remains for the criterion is
ONS's contract triple and an adjudication, plus [[R226]].

**Date:** 2026-09-14. **PR:** #221 (`r225-d1-resolution-test`, commits `314fa33` + `0f08ede`).

**Doc impact: none.** No released term. One new instrument
(`scripts/supersession_chain_depth.py`); no vocabulary, shape or contract touched.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is typed
assertion-or-proposition.

---

## 5. The next concrete action

### 5a. ASSERTED — etkl:04's remaining route is the contract triple and an adjudication, not a repair

Mechanical in the sense that matters: the outcome is known and doing it *is* the work. With R225
closed, the criterion's blocker is gone and what is left is what the prior spec's § 6 already named
as out of scope: **ONS carries no `cor:contract` / `cor:terms` / `cor:shapes`**, so no membrane has
ever seen its output, and its `cor:expectedVerdict` is `cor:Unadjudicated` under a 2026-08-20 HOLD
whose rationale refuses to accept a score on an unread document. The new reading (0.7712418300653595)
is registered and dated; the criterion needs the contract authored and the adjudication taken.

Read the HOLD rationale at `tests/corpus-manifest.ttl:109` before writing anything — it states the
standard the adjudication has to meet, and it is about *reading the document*, not about the score.

### 5b. RUN, AND REFUTED — the prediction below came true; this action is DONE, not pending

**The prediction was RUN, and it refuted the claim — so this is a record, not an action.** [[R228]]
first held that the datagrid fallback is *uncoverable*: no synthetic page can reach
`compile.py:1351` post-D1, on four failed shapes plus a counting argument over three shipped
mechanisms. **The argument was wrong at one word.** It read `datagrid.py:341`'s "modal" row
signature as majority-by-count; `:337` maximises **`len(s) * counts[s]`**, so 8 two-run rows score
16 against 10 one-run rows' 10 and the two-column universe wins without the data rows being a
majority at all.

The fifth shape is `isolated_rows_grid_pdf`: one tall prose band (10 single-word lines at a 14pt
pitch) supplying the nine small gaps that set `detect_bands`' median, then 8 data rows each behind a
60pt gap so each becomes its own single-line band. Every band is legitimately ignored, the gate
opens, `derive_data_grid` reads `rows=8 cols=2`, and the fallback appends a region carrying 16
cells that books 16 tokens and names its table. **It draws no rules**, so D1 never runs on it and
cannot repair the mechanism out from under it the way it did to `border_only_grid_pdf`.

**What that changes:** three tests come off the retired list (the gate test, the SHACL-through-
production test, and [[R224]]'s I3), and the two `test_datagrid` ones **lose their corpus gates**,
so they hold the line on every push rather than only where the gitignored corpus is present. R72's
witness A stays retired on separate evidence — `page_has_table` is False on this page, and the
corpus-wide sweep found no table page that reads nothing.

**The grade is the lesson.** Labelled a proposition and ordered run before anything was built on
it, it cost one probe. As a theorem it would have justified deleting a live branch on reasoning
that failed at a single word.

### 5c. ASSERTED — what this loop must NOT be read as having done

The fallback branch is **not deleted** (§ Producer-side guards: coverage proof first). [[R226]] is
untouched and still blocks ons stitching. [[R229]] is measured and unrepaired. R72's table-page
direction has **no witness anywhere in the corpus** and is retired, not relocated. The full suite
was run in **chunks**, never as one invocation.

---

## 1. Where the primaries are

- **What shipped** — `compile.py`'s `_word_column_count` plus the resolution test at the derived
  `col_xs`. Find it by `grep -n "_word_column_count" src/iladub/etkl/compile.py` (a grep, not a
  line number — plan rule 7).
- **The evidence** — `docs/superpowers/2026-09-14-d1-post-d2-measured.md`. Its § 3b carries the
  re-baseline and the falsification table; § 4 carries this loop's own three process failures.
- **The rows** — ~~R225~~ and ~~R227~~ in `residues-closed.md`; [[R228]], [[R229]], [[R226]] in
  `residues-open.md`.
- **The new instrument** — `scripts/supersession_chain_depth.py`, which prints depth in **edges**
  beside the node count, because that is the figure a unitless number gets wrong.
- **The scratch worktrees** — `wt-d1` (D1 applied; where O3 was falsified) and `wt-d1a` (the
  original placement). Both under the session scratchpad, both removable once #221 merges.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The score drop is correct; ship the RELOCATED placement | maintainer's ruling, 2026-09-14; ~~R225~~'s closure |
| Re-point R224's I1 at adoption; re-scope I2 to the guard; retire I3 | [[R228]]; the three test docstrings |
| O3 amended with measured `D1_MOVES` pins, never loosened to `>=` | `test_run_merge_seam.py`'s `D1_MOVES` comment |
| Do NOT delete the fallback branch | [[R228]]; § Producer-side guards |
| R72's table direction retires; prose direction keeps ons p1 | `test_datagrid.py`'s docstring; [[R228]] |

## 3. Unverified or assumed

- **5b entirely**, per its grading.
- **R229's downstream consequence is unmeasured.** Two readings carrying 276 cells each leave
  `chains`; nothing here measures whether anything depends on them being there.
- **The original D1 placement was never swept over all seven documents.** It was screened on
  ons+bfs only and rejected on R13's closure, so its byte-identity on the five pinned documents is
  *inferred from the relocated variant's*, not measured.
- **CI on #221 FAILED on its first run, and the cause was mine.** `test_residue_graph.py::
  test_the_graph_reports_parked_rows_and_the_structural_candidates` pins the structural-candidate
  count, which this loop's register edits moved 91 -> 90. Re-baselined with the delta's
  composition measured against `HEAD~2` (ADDED = [], REMOVED = [170]) and the mechanism named:
  R228's prose cites R170, which had been open and isolated. **None of this loop's four status
  changes moved that count at all** — two closures and two raises left every row's candidacy
  untouched; a single sentence moved it. The ruleset is confirmed firing (`mergeStateStatus:
  BLOCKED`), and at the time of writing the re-pushed run had not yet reported, which is not the
  same claim as green.

## 4. What this loop did

Measured both D1 placements against a post-D2 gate, found that D2's deleted clause was the sole
reason either was ever refuted, and shipped the relocated one under a ruling. Closed R227 by
*refuting its own open half* — the corpus produces chains of 1 edge, not 2, so the lineage walk has
never walked. Re-pointed, re-scoped and retired five tests, each with falsification or an explicit
skip, and amended a standing detector rather than loosening it.

**Worth carrying, because it is the technique and not the result.** FOUR separate false greens
appeared in one session and each looked like success: a compound command's exit code read as a test
verdict (chunk 1 was `3 failed, 66 passed`); `pytest $FILES` under zsh, which does not word-split
unquoted expansions, so pytest got one giant argument and reported `no tests ran in 0.00s` with exit
0 — twice; a 0-byte background output file read as a dead job, which was killed and duplicated
while healthy; and **"suite green" claimed from a subset I had chosen myself** — `tests/etkl/**`
plus five hand-picked repo-level modules, where the repo has about **ninety** outside `tests/etkl`.
CI then failed on one in neither set. The remedies are structural: pass file lists through `xargs`,
read a `--collect-only` count before believing results, read the summary line rather than the exit
status, and **run `pytest tests/ --ignore=tests/etkl` before a push** rather than naming the
modules you think a change could reach — this change reached one nobody would have predicted, via
a citation in prose.

**Two of my own claims were refuted by running them** — that the original placement was "dominated"
(it reads 27 more bfs p6 cells), and a *fabricated* docstring measurement (`page_has_table(ons, 5)`
true; it is False for every ons page). Both are corrected in place in the evidence doc rather than
deleted.
