# Handoff: split cbh `#table9` at the author's closed ruled boxes — design half-done (2026-09-28)

**Serves:** prog:criterion:etkl:03 — cbh is not accepted until `#table9` compiles as the two tables the author drew.

**Topic:** jev-reading · **Date:** 2026-09-28 · **src measured:** `b2d2052` · **Doc impact: none.**
**Authored at:** ~56k working tokens, over the 50K originating floor. Parts 1–4 are pointers and
records. Part 5 is graded per action.

## 5. Next action (written first)

- **Proposed, and the first thing to rule on:** redo design § 1's *touch* test. The design as
  approved said *"no added tolerance"*. The census **refuted that on cbh itself**. The right box's
  left vertical ends at x 543.88998 and its horizontals start at 543.89, a 2e-5 gap that comes from
  PDF rect widths such as 0.47998. Under exact touch that box reads 1×4 (17/21 words tile) instead
  of 2×4 (21/21).
  - **Candidate replacement:** two rules touch when the gap is **≤ the thinner of their two stroke
    widths**. The bound is derived from the page, not tuned. It reproduces cbh (2×4, 21/21, title
    bar found), and its only other effect across the whole corpus is one extra hairline row in bfs
    p5 box0.
  - **Open question for the maintainer:** is a stroke-derived bound AXIOM (a fact of the drawn
    mark) or a tolerance in disguise (CLAUDE.md § 8, "a tuned constant is prima facie evidence")?
    Ask this before re-presenting § 1.
- **Asserted:** then present design § 2 (the plug point, § 3 below), § 3 (the oracle) and § 4
  (what is not done). Then write the spec. The brainstorming path is **architectural**.

## 1. Goal

cbh page 0, y 681–761 (`#table9` today, one 2-column table of whole lines) should compile to what
the author drew:

- **Stock at Port:** a 7-column × 4-port `RecordTable` with boxhead `PORT | WHEAT | MAIN WHEAT
  GRADES | BARLEY | CANOLA | OTHER | TOTAL`.
- **Port maintenance shutdown dates 2026:** a 2-column × 4-row `RecordTable` with **no boxhead**.
  The page draws none, and the PR #282 note's claim that it has one is wrong.
- **Captions:** each box's title-bar words become that table's captions.
- **The Note block:** carried as notes, not as entry rows.

## 2. Where the primaries are

- **The defect:** `docs/superpowers/2026-09-28-cbh-one-is-not-a-compile.md`, on PR #282. That PR
  is OPEN with CI green and has not been merged by this session.
- **Scripts** (gitignored, local only): `internal/benchmarks/cbh-boxes-2026-09-28/`.
  - `tile.py`: the tiling check on cbh p0, y ≥ 670.
  - `boxes.py PDF PAGE [--bands]`: rules, touch graph, boxes, lattice, tiling, title bars, and the
    join to `page_bands`.
  - `run_all.sh exact|stroke`, which writes `out_{mode}.jsonl`; summarise with `summ.py`.
    `stroke.txt` is the summary for the stroke variant.
  - `cmp_repo.py`: our rule set compared with `extract_rules`.
  - `m1.py`–`m6.py`: the seam trace.
  - **Re-run them rather than trusting the figures here.**
- **Code seams**, at `b2d2052`:
  - `compile.py:454`, the per-raw-band loop in `page_bands`:
    `cut_trailing_notes(segment(band))` → `_build_ruled_band`.
  - `grid.py:40`, `_rule_boundaries`.
  - `segment.py:21`, `_GUTTER_DOMINANCE = 2.0`.
  - `compile.py:257`, `_emit_band_captions` (`Band.captions` → `tab:RegionCaption`).

## 3. What was decided, and where it is recorded

The maintainer ruled these in chat on 2026-09-28. They are recorded **nowhere but this file**, so
treat them as reversible.

- **Approach 1:** segment a band at closed ruled boxes *before* `segment`/classification (AXIOM).
  Each box becomes its own sub-band and is read by the unchanged rule reader. Its title-bar words
  are set directly on `Band.captions`, not through `peel_leading_captions`, which misfires here
  because the title line counts as a grid line. Ink outside every box stays one residue band that
  goes through `segment`/`cut_trailing_notes` unchanged.
  - **Rejected:** scoping `_rule_boundaries` by rule y-extent. The what-if test gave one 9-column
    table with the gutter absorbed.
  - **Rejected:** tuning the gutter splitter.
- **The totals family is deferred to its own loop.** None of the four roster port totals
  (374,904 / 737,289 / 660,363 / 178,708) is carried; they are `#ignored2/4/6/8`. 1,951,264 equals
  their sum, and `ChainArithmetic` confirms 0 of them. This widens R74. **No register row has been
  written yet**, so the next session raises it.
- **Design § 1** (a box = a touch-graph component with ≥2 verticals and ≥2 horizontals, whose cells
  are the gaps between rules; a title bar = a filled rect meeting the top rule and outer verticals)
  was **approved and then partly refuted** by the census. See part 5.
- **The oracle:** a structural carriage test (table count, columns, cells per row, captions, notes),
  pinned like `tab:11`. **Never the ink score**, which will probably not move or will fall.

## 4. Unverified or assumed

- **Why the page fuses today** (subagent trace, `m1.py`–`m6.py`, not re-run by the author):
  - band 9 is one raw band, y 683.5–761.5, 10 lines;
  - `_rule_boundaries` returns None because the title line and Note lines cross rules;
  - it falls back to whitespace columns and takes the plain record path (`assert_record_region`,
    `compile.py:1214`);
  - a what-if restricted to each box gives 7 and 2 columns, RECORD_TABLE.
- **Census populations** (stroke mode, subagent, not re-run):
  - **(a) ≥2 boxes in one band:** only cbh band 9.
  - **(b) one box plus words outside:** only the four cbh rosters, where the outside words are
    orange title-bar text.
  - **(d) one box spanning several bands:** graincorp-capacity (3), graincorp-stem p0 (2),
    bfs p6 (9).
  - **Title bars:** only on cbh.
  - **The trigger is therefore undecided.** If it is "≥2 boxes", only band 9 changes. If it is "any
    box with ink outside", the rosters change too and collide with loop P's caption peel.
- **"≥2V and ≥2H" is not the same as "closed":** bfs p5's two boxes are header-only lattices with no
  outer frame, and 2/38 words tile in one of them. The box definition may need an outer-frame
  condition.
- **The repo's `extract_rules` over-reads.** It includes every edge of every rect (title bars,
  white cell fills, grey shading): 427/460 non-rules on graincorp-capacity, 678/413 on apple p0.
  The design may need its own black-rule reader.
- **Whether the Note residue band becomes notes (a carried `tab:` note) or ignored** under the
  existing paths is **unmeasured**.
- **Band indices shift** when band 9 becomes three bands. Any band-indexed test or register row
  naming `#table9`, or `#table10` and above, on cbh will move. **Unmeasured.**
