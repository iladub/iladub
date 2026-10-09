# Handoff: R300's cause measured — the driver installs the re-compile's report over pass 1's graph (2026-10-09)

**Serves:** maintenance. R300 was picked by the maintainer 2026-10-09; its cause is now measured, nothing is fixed.

**Topic:** compile · **Date:** 2026-10-09

Written at ~65K working tokens, 1.3× the 50K originating floor. The maintainer chose "handoff, fix
fresh" over continuing past the floor. Part 5 was written first and is graded per action.

## 5. The next concrete action, typed

1. **ASSERTED — measure equality on every adopting document before writing the fix.** Run the probe in
   § 2 (temporary print in the adoption loop, then revert) on apple, graincorp-stem, bfs and fed-h41,
   **serially** (one compile at a time; see the `corpus-runs-are-serial` memory). The outcome is
   mechanical: each untouched region is either equal to pass 1 modulo `table_uri`, or it is not. On
   fed-h41 it is 20/20 (§ 2). Only fed-h41 has been measured. Do this before step 2, because step 2's
   design depends on the answer.
2. **ASSERTED if step 1 is all-equal, PROPOSED otherwise — the document-scope remedy.** In
   `compile_document`'s adoption loop, at `pages[p] = rep_a`, install **pass 1's region**
   (`pages[p].regions[idx]`, before the reassignment) for every `idx < grid_idx` that no grid's
   `supersedes` names. Keep `rep_a`'s entries for the superseded indices and for the grids. The graph
   already holds pass 1's subgraph for those bands, and `chains` and the section-total confirmations
   were built from pass-1 URIs before this loop. So the report would name what the graph holds, and
   ink, cells and the score cannot move, because the regions are equal modulo URI. If step 1 finds an
   unequal region, R301 ruling 3's alignment premise is broken on that document, and what to do with it
   (refusal note, or raise) is a design decision, not this handoff's to make.
3. **PROPOSED (low confidence) — the CI-visible pin.** R300's closing criterion asks for "a test on a
   synthetic adopted page". That page needs an escalating band (to open the gate), a band the grid
   supersedes, and an **asserted band whose lines the grid does not admit**. No existing fixture is
   known to have the third property, and the R302 loop already refuted one "the existing helpers can
   build it" prediction. **Try for one hour at most.** If no fixture reaches it, extract the install
   step as a pure function over `(pass1_report, rep_a, grid_idx)` and pin that directly, then add a
   held-out-gated test on fed-h41 p3/p10. Report this as a substitution for the row's criterion, not
   as meeting it (CLAUDE.md plan rule 5's posture).
4. **ASSERTED — raise the page-scope twin as a new register row** in the closing PR (§ 4, finding B).
   Do not fix it in the same loop. R83's analysis says re-escalating at page scope breaks document
   scope, and the asserted twin plausibly inherits that tension. That is unmeasured.

## 1. Goal

Run the handoff's "run first" check for R300 (`2026-10-09-after-r302-handoff.md` § 5): is the `/adopt`
URI the re-compile's `adopt_doc` leaking into the installed report? **Yes.**

## 2. Where the primaries are, and what was measured

All measurements at `b161a61` (`origin/main`), branch `r300-adopt-uri`, which has no commits besides
this file. Every run used `compile_document("held-out/fed-h41-2025-01-02.pdf", validate_shapes=False)`;
each took 3 min 26 s.

- **Probe A (read-only):** for every installed region with a `table_uri`, count its subject triples in
  `DocumentReport.graph`, and the same count with `/adopt#` replaced by `#`.

  ```
  adopted (2, 3, 5, 8, 10)
  p3 r7  asserted UNSUPPORTED_TABLE cells=199 tok_a=218  p3/adopt#htable7   n=0  pass1_uri_n=39
  p10 r3 asserted UNSUPPORTED_TABLE cells=36  tok_a=52   p10/adopt#htable3  n=0  pass1_uri_n=14
  ```

  Every grid region (`pN/adopt#pN-datagrid`, on p2, p3, p5, p8 and p10) resolves (n = 48 to 252).
  **Exactly two reports dangle, and both are UNTOUCHED asserted bands**, meaning no grid's `supersedes`
  names them. **R300's row says p3, p5 and p10 (at `542116d`); p5 no longer dangles at `b161a61`.** What
  changed p5 between those commits is unmeasured. R301's guard (#325) is the obvious suspect, and it
  is not confirmed.

- **Probe B (temporary edit in `compile_document`'s adoption loop, just before `pages[p] = rep_a`,
  reverted with `git checkout`):** for each untouched `idx < grid_idx`, compare
  `dataclasses.replace(rep_a.regions[idx], table_uri=pages[p].regions[idx].table_uri)` with
  `pages[p].regions[idx]`, and check whether `rep_a.graph` holds `rep_a.regions[idx].table_uri`.

  ```
  20 untouched regions over the 5 adopted pages: eq_mod_uri=True for all 20
  p3 r7   p3/adopt#htable7  | p3#htable7    in_rep_a_graph=False
  p10 r3  p10/adopt#htable3 | p10#htable3   in_rep_a_graph=False
  ```

- **The mechanism, from reading and agreeing with both probes.** The adoption loop compiles page `p`
  again under `adopt_doc = {page_doc_uri(p)}/adopt` and merges `rep_a.graph`, which is the page graph
  `compile.py` rebuilds from the grids alone (`_new = Graph()` in the adoption branch). From the
  document graph it withdraws only the superseded bands' escalation records and withdrawable tables.
  So every untouched band keeps **pass 1's** subgraph under `page_doc_uri(p)`. Then
  `pages[p] = rep_a` installs the **re-compile's** report, whose untouched regions name tables minted
  under `adopt_doc`. Grids resolve because they come from `rep_a.graph`. Untouched asserted tables
  dangle because they are in neither graph under that name.

## 3. What was decided, and where it is recorded

- **The maintainer picked R300** over R299 and R295 (2026-10-09, this session).
- **The maintainer chose to hand off** rather than build the fixture and fix past the floor.
- Nothing else was decided. The remedy in § 5.2 is a proposal for the next session.

## 4. Unverified, assumed, or found on the way

- **Finding A: R300's population moved.** It was 3 reports at `542116d` and is 2 at `b161a61`. The
  register row is Evidence, so it is not edited. The closing row must cite this re-measurement.
- **Finding B: R300 has a page-scope twin, and it is live.** `rep_a.graph` holds neither untouched
  asserted table (`in_rep_a_graph=False`). So `compile_tables(fed-h41, 3, datagrid_adopt=True)` reports
  199 cells and 218 asserted tokens for a table that is in **no graph**. This is R83's *asserted*
  sibling: R83 is about untouched *escalated* bands at page scope. Not yet a register row (§ 5.4).
- **Finding C: R83's "dormant" premise does not hold on the held-out document.** R83 says the
  untouched term is empty on both adopting pages *of the corpus*. On fed-h41, untouched **escalated**
  regions sit on adopted pages p2 (r1, r4), p5 (r1, r3) and p8 (r1). This does not falsify R83 as
  written, because fed-h41 is held out, not corpus. It does mean R83 is no longer dormant everywhere
  the compiler runs, and R83 blocks `prog:criterion:tab:08`. Whether fed-h41's page-scope graph lacks
  those candidates was **not** checked.
- Equality in Probe B is measured on one document. § 5.1 exists to widen that.
- No `src/` line changed, and no test was run.
