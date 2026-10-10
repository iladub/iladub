# Handoff: R300 closed — an adopted page reports pass 1's reading of every band the grid left alone (2026-10-10)

**Serves:** maintenance. R300 was picked by the maintainer 2026-10-09; this loop executes the remedy
in `2026-10-09-r300-cause-measured-handoff.md` § 5.

**Topic:** compile · **Date:** 2026-10-10

Part 5 was written first, at ~100K working tokens, under the 150K executing floor. This loop
originated no design: the remedy is the previous handoff's § 5.2.

## 5. The next concrete action, typed

1. **PROPOSED — no subject is chosen; the maintainer picks.** The open candidates this loop knows
   of are R299 (caltrain's heading admitted as a data row), R295 (held-out caltrain), R304 (raised
   here: R300's page-scope twin) and R83 (no longer dormant on fed-h41, see § 4). None is ordered
   over the others by anything measured here. Read `residues.md`'s index and ask.
2. **ASSERTED, whichever subject is picked — R304 is not a one-line fix.** Do not "just name the
   pass-1 table" at page scope: page scope has no pass-1 graph to name. R83's comment in
   `compile.py` (the adoption branch, "NOT REPAIRED HERE, on purpose") says re-emitting at page
   scope breaks document scope. R304 inherits that tension, and how it resolves is a design
   question, not a mechanical one.

## 1. Goal

Make every asserted `RegionReport.table_uri` on an adopted page name a table the document graph
holds (R300).

## 2. Where the primaries are, and what was measured

- **The fix:** `src/iladub/etkl/document.py`, `_untouched_from_pass_one` and its one call site in
  `compile_document`'s adoption loop. For every index below `grid_idx` whose re-compiled verdict is
  not `superseded`, the page installs pass 1's region. If any such region differs from pass 1 in
  anything but `table_uri`, the page refuses adoption with a note, decided before any mutation.
- **Step 1 of the previous handoff (equality on every adopting document):** a temporary probe in
  the adoption loop, reverted, run serially over all eleven documents. Output kept in this
  session's scratchpad only. RESULT: _filled below in § 2a_.
- **The CI pin:** `tests/etkl/test_r300_report_names_the_graph.py`, on
  `tests/etkl/fixtures.py::currency_marker_escalating_with_untouched_table_pdf`. The fixture was
  found inside the hour the previous handoff allowed: an all-text second table that no grid admits.
  Three of the four shapes tried reproduce R300; its docstring records which one did not.
- **The held-out pin:** `tests/test_r301_fed_h41.py::test_r300_every_asserted_report_names_a_table_in_the_graph`,
  riding that module's one compile.
- **FALSIFICATION** (each run, then restored, suite green at 6/6):
  - install `rep_a` whole: the criterion test and the pass-1-name test fail;
  - drop the equality check: `test_a_band_the_two_compiles_read_differently_refuses` fails;
  - drop the caller's refusal: `test_the_driver_refuses_the_page_before_it_mutates_anything` fails.
- **Blast radius:** `scripts/corpus_verdict_snapshot.py`'s `snapshot()` on all eleven documents,
  from a `main` worktree and from this branch, serially. RESULT: _filled below in § 2a_.

## 2a. Results

**Step 1, equality (probe at `e26948d` plus this branch's uncommitted fixture, serial, one process,
`validate_shapes=False`): 48 of 48 untouched regions equal pass 1 modulo `table_uri`, 0 unequal.**
Four documents adopt a page: fed-h41 (20 regions, matching the previous handoff's 20/20), ons (15),
bfs (11) and apple (2). The other seven adopt nothing: graincorp-stem, cbh-stem, graincorp-capacity,
who-wfa, caltrain, who-covid and arxiv. On fed-h41 the two asserted untouched regions are p3 r7 and
p10 r3. Their pass-1 table is in the document graph, and the re-compile's `…/adopt#` name is in neither graph.
So the refusal branch of `_untouched_from_pass_one` is reached by no document. It is pinned in CI only.

_Blast radius: pending._

## 3. What was decided, and where it is recorded

- **A disagreement refuses the page, it does not raise.** Recorded in `_untouched_from_pass_one`'s
  docstring. It follows the adoption loop's own idiom (every other pass-1/re-compile disagreement is
  a refusal note), and nothing measured reaches it. Reversible: it is this loop's call, not a
  maintainer ruling.
- **R304 is raised, not fixed.** As the previous handoff's § 5.4 asked.

## 4. Unverified, assumed, or found on the way

- R83's "dormant" premise still fails on held-out fed-h41 (previous handoff, finding C). Not
  re-measured here.
- What moved R300's population from 3 to 2 between `542116d` and `b161a61` (p5) is still unmeasured.
