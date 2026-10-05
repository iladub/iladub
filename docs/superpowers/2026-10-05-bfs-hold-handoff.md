# Handoff: bfs's recorded hold reason was fixed by #303 — adjudicate bfs, then re-evaluate strategy (2026-10-05)

**Serves:** prog:criterion:etkl:05 — bfs compiles to cor:CompilesAbove; the corpus benchmark (N/7 accepted, ruling 2026-09-18) has been 5/7 since 2026-09-18 (#272).

**Topic:** bfs-hold · **Date:** 2026-10-05

**Doc impact: none.**

Written at ~150K working tokens, past the 50K originating floor (CLAUDE.md § Loop & context hygiene).
Part 5 is graded per action. **This supersedes part 5 of `2026-10-05-r291-trailing-cut-evidence.md`**:
that note named R292 as the next subject. R292 is an ons defect, ons is already accepted, and the
work cannot move N/7. It stays a register row.

## 5. Next concrete action (written first)

1. **PROPOSED: re-read bfs on `main` (`81a2ca6`) against its own hold reason, and adjudicate it if
   nothing else holds it.** Prediction: bfs is one recorded boxhead reading away from
   `cor:CompilesAbove`.
   - **Evidence:** bfs's newest `cor:reading` comment (`tests/corpus-manifest.ttl`, the 0.9021 reading
     dated 2026-09-19) holds it for ONE reason: *"p5's one adopted grid spans TWO tables, and all 270
     of T2's entries sit under T1's column labels."* #303 (R290) split that grid in two:
     `#p5-datagrid` (cantons, 270 cells) and `#p5-datagrid-2` (years, 226 cells). Per
     `2026-10-05-r290-two-grids-evidence.md` § 2.3, the canton grid now carries **0** boxhead labels,
     because no boxhead reading is recorded for a 10-column canton grid.
   - **What may be wrong, checkable in minutes:** (a) "no labels" is not "wrong labels". Whether 270
     unlabelled entries may be adjudicated is the maintainer's ruling, not an agent's, by the same
     standard that set the hold. (b) Another unread or misread row may exist that the 09-19 comment
     never named. Re-check p5 and p6 row by row, the way the 09-19 Tessin note did, before any floor
     is proposed. (c) The year grid's 11 labels were recorded for the OLD grid (19 rows inside a
     46-row grid). Confirm they replay onto `-datagrid-2` by the readings' crop hash, not by
     assumption.
   - **If (a) needs labels:** record a boxhead reading for the canton grid with the shipped BAML
     boxhead reader, its exact oracle and `readings/boxhead/`. This is the method that accepted ons
     and apple. The API key needs the zshrc prefix: see memory `neural-worker-seams-measured`.
   - **Falsifier:** a floor pinned at bfs's live score, and every corpus-gated test green under the
     local sweep (`ci-skips-corpus-sweep-locally`). A floor never goes over a misread entry.
2. **PROPOSED (the maintainer asked for this view): pause for a strategy review AFTER item 1,
   not before.** Reasoning, graded as an opinion:
   - **For pausing:** 17 days and ~50 commits have not moved N/7. Each loop on a held document has
     surfaced the next defect inside it (R288 → R289 on cbh; R265 → R290 → R291 → R292 on bfs). That
     is the residue-chasing the 2026-09-18 ruling warns against. The two held documents may also be
     the hardest two of seven: N/7 measures how far down a fixed list the reader gets, and with 7
     documents each later point costs more and generalises less (memory `no-overfitting-general-fixes`).
   - **Against pausing now:** item 1 may be cheap and is bounded, because its hold reason is
     already fixed.
   - **Questions a review should answer** (NOT decided anywhere): Is a 7-document corpus still a
     benchmark, or has it become a fixture? Should the next documents be new, unseen ones, so that
     N/M measures generalisation? Does cbh's hold (R289) deserve a loop, or a ruling? Does the
     2026-09-20 `quarter15-convergence-pause` (memory) still stand?
   - **Recommendation:** run item 1 as ONE loop. Whether it ends 6/7 or not, the next session is a
     strategy review with the maintainer, not another loop.

## 1. Goal

Turn #303's fix into a benchmark move: adjudicate bfs, or name exactly what still holds it.

## 2. Where the primaries are

- `tests/corpus-manifest.ttl`, the bfs `cor:reading` block (its hold comments) and bfs's
  `cor:expectedVerdict` (`cor:Unadjudicated`). See how the five accepted entries pin `cor:scoreFloor`
  and `cor:adjudication`.
- `docs/superpowers/2026-10-05-r290-two-grids-evidence.md` § 2.3: the per-grid table (cells,
  superseded bands, boxhead labels).
- `docs/superpowers/2026-10-05-r291-trailing-cut-evidence.md` § 6: the sweep, re-pins and score.
- `readings/boxhead/README.txt` and its JSON readings: how a boxhead reading is recorded and
  replayed. PR #271 (ons) and #272 (apple) are the worked precedents.
- `docs/superpowers/2026-09-19-tessin-trailing-notes-evidence.md`: the last bfs adjudication
  attempt, and the row-by-row standard it used.

## 3. Decided, and where

- R265, R290 and R291 are closed: `residues-closed.md`, PR #303 (`81a2ca6`).
- R292 stays open and is NOT the next subject: recorded only here.
- "Pause for a strategy review after item 1": a recommendation, recorded only here. It is the
  maintainer's decision.

## 4. Unverified or assumed

- That nothing besides the 09-19 reason holds bfs. Not checked. Item 1 (b) is the check.
- That the year grid's recorded boxhead replays onto `#p5-datagrid-2`. Not checked. Item 1 (c).
- That N/7 has not moved since 2026-09-18. Measured by `git log -G CompilesAbove` on
  `tests/corpus-manifest.ttl`: the last acceptance is `e6ed4fe` (#272, apple).
- The strategy view in item 2 is an opinion formed late in a long session.
