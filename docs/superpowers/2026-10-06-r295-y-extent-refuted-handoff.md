# Handoff: R295, the y-extent remedy is refuted, and the tiling test is an oracle (2026-10-06)

**Serves:** maintenance — loop 1 of the four the maintainer accepted on 2026-10-06
(`2026-10-06-r295-grid-scope-handoff.md` § 3). No `src/` changes.

**Topic:** compile · **Date:** 2026-10-06

**Doc impact: none.**

Written at about 50K working tokens, at the originating floor. Part 5 comes first and is graded
per action.

## 5. Next concrete action

1. **A MAINTAINER RULING comes first.** § 2 measured two ways to find the grid's lines. They are
   not equivalent under CLAUDE.md §8:
   - **(a) NEURAL proposer, the ruling as written.** Under *"one geometric attempt, then NEURAL"*
     (2026-09-17), the y-extent test was the one geometric attempt and it is refuted (§ 2.1). The
     next loop writes a worker that answers *"which numbered lines of this band are the grid,
     from its header row to its last data row?"* It returns two line indices, a closed shape and
     no page value. It is disposed by the tiling oracle in § 2.2.
   - **(b) Derive the span with no worker.** The oracle in § 2.2 is cheap, so it can be searched
     directly: take the widest contiguous run of lines that the rules drawn within that run tile.
     There is no constant in it. But it is a second geometric attempt, which the ruling forbids.
     It would also take in any furniture line that fits within one interval (§ 4).

   **Recommended: (a).** The oracle refuses a span that is too wide but cannot refuse one that is
   too narrow (§ 4). Only a reader can see that a header row was left out. So (b) would carry the
   oracle's blind side forward as its answer.
2. **ASSERTED (minutes, already run by hand in § 2.2).** Whichever arm is ruled, its first test is
   the hand-supplied span 4..36 on all four Caltrain pages. Rules clipped to that span tile into
   18, 19, 18 and 19 columns, and each page classifies `UNSUPPORTED_TABLE`, so it escalates and
   enters the score's denominator. The legend line 3 is refused. That is the definition-of-done
   shape from the previous handoff's item 3, reached by hand.
3. **PROPOSED (unmeasured).** The blind side. Does the tiling oracle accept a span that omits the
   header row (5..36)? By construction it should, because a subset of tiling words still tiles.
   Run it. If it accepts, the worker's answer for the top edge is undisposed, and the loop has to
   say which oracle would dispose it. The ons boxhead reader (`baml_src/boxhead.baml`) is the
   candidate to measure.

## 1. Goal

Make Caltrain's three ignored timetable pages reach a table region, and stop page 2 asserting a
2-column misread. Unchanged from `2026-10-06-r295-grid-scope-handoff.md` § 1.

## 2. Where the primaries are, and what was measured

All measurements were taken at `b62fb68` (`main`), offline, using
`held-out/caltrain-weekend-timetable.pdf`. Fetch it with
`.venv/bin/python scripts/fetch_corpus.py tests/held-out-manifest.ttl held-out`. The scripts were
scratchpad monkeypatches and were not committed. Their logic is stated in enough detail here to
rebuild them.

### 2.1 The y-extent remedy (previous handoff, item 1): REFUTED in both halves

Patch: in `grid._rule_boundaries` (`src/iladub/etkl/grid.py:40`), a word has to respect a rule x
only where a segment of that rule overlaps the word in y.

- **Inner test only, outer bound left global:** no change on any page. Pages 0, 1 and 3 stay at 1
  column (`NON_TABLE`), and page 2 stays at 2 columns (`RECORD_TABLE`). Two kinds of word still
  failed on page 0:
  - Line 37 (the footer, starting "EFFECTIVE September 21, 2024") has x0 = 13.5, left of the
    leftmost rule at x = 14.0, so it fails the global outer bound. It lies below every rule.
  - Line 2 ("Northbound – WEEKEND SERVICE to SAN FRANCISCO") is a single word box 25 pt tall, at
    y 80.2 to 105.2. The grid rules start at y 105.227. The overlap is **0.003 pt** on pages 0 and
    1, and **1.16 pt** on pages 2 and 3 (word bottom 105.69 against rule top 104.53).
- **Outer bound scoped the same way, with overlap > `COORD_EPS`:**
  - Pages 0 and 1 give **23 and 24 columns**, not the predicted 17 to 19. The six title-area
    marks (y 81 to 99) enter the boundary vector as separators.
  - Pages 2 and 3 do not change. The heading's 1.16 pt overlap still makes it straddle 11 grid
    rules.

The previous handoff stated that line 2 *"lies outside the y-extent of the rules it crosses"*. That
is false on pages 2 and 3. A word's box is its font box, not its ink, and the heading's box runs
1.16 pt into the drawn grid. Any overlap tolerance that admits 1.16 would be a tuned constant.

### 2.2 The tiling test, given the right span, is an exact oracle

The span was supplied by hand: a sub-band of lines *lo*..36, keeping only the rules whose y-extent
overlaps the span (strict overlap), with `column_xs` cleared. The test is then the unmodified
`_rule_boundaries` followed by `regions.classify`.

| page | span 4..36 (header row "Train No." to the last data row) | span 3..36 (adds the legend "6XX Local") |
| --- | --- | --- |
| 0 | 19 rule xs, **tiles 18 cols**, `UNSUPPORTED_TABLE` *"header has 17 words but 18 columns"* | 23 rule xs, **refused** (`None`) |
| 1 | 20 rule xs, **tiles 19**, `UNSUPPORTED_TABLE` (18 words / 19) | 24, **refused** |
| 2 | 20 rule xs, **tiles 18**, `UNSUPPORTED_TABLE` (17 / 18) | 24, **refused** |
| 3 | 20 rule xs, **tiles 19**, `UNSUPPORTED_TABLE` (18 / 19) | 24, **refused** |

The page-2 misread disappears once the span is right. The header's word count is one short of the
column count on every page, which is loop 2's subject (Caltrain's header via the boxhead method).

### 2.3 The blind side, measured (part 5, item 3): the oracle admits every narrower span

The same construction was run over spans *lo*..*hi* for *lo* in 0..7 and *hi* in {30, 36, 37}.
On all four pages the oracle admits **every** span with 4 ≤ *lo* and *hi* ≤ 36: 4..36, 5..36 (no
header row), 7..30, and so on. It refuses every span that starts at line 3 or earlier, or ends at
line 37. So the oracle fixes the **outer** bound exactly and is blind to everything inside it.

This weakens part 5's recommendation. Under arm (a), the only choice a worker could make that the
oracle does not already make is a span *inside* 4..36, and nothing disposes that choice, so
*"no oracle, no worker"* forbids it. The widest admitted span, 4..36, is the right extent on all
four pages, and it is arm (b)'s answer. Whether a header row belongs inside the table is a line
role, which is loop 2's subject (the boxhead).

## 3. What was decided, and where it is recorded

- **The y-extent remedy is refuted.** Recorded here only. R295's full row in `residues-open.md` is
  Evidence and append-only, so it was not edited.
- **The fork in part 5 is NOT decided.** It is the maintainer's ruling.
- No blast-radius census was run (previous handoff, item 2). It only applies to a change to
  `_rule_boundaries`, and neither arm in part 5 changes that function's test.

## 4. Unverified or assumed

- ~~**The oracle's blind side (part 5, item 3).**~~ **Measured afterwards: § 2.3.**
- **Arm (b) absorbing furniture.** A footnote line that happens to fit within one rule interval
  would be absorbed by the widest-tiling-span search. Not observed on Caltrain, where the footer
  fails the outer bound. Not checked on the seven.
- **What the six title-area marks are.** They are still assumed to be a legend swatch (previous
  handoff, § 4).
- **Whether the seven carry the same defect.** Not measured. Neither arm has been run on them.
- **The 1.16 pt figure is the font box.** Glyph ink was not extracted to confirm that the heading's
  visible ink stops above the rule.
