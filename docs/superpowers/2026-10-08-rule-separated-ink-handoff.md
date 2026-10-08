# Handoff: loop 3, the membrane refuses a cell whose ink an author's rule separates (2026-10-08)

**Serves:** maintenance — loop 3 of the four the maintainer ordered on 2026-10-06
(`2026-10-06-r295-grid-scope-handoff.md` § 3).

**Topic:** compile · **Date:** 2026-10-08

**Doc impact: increment.** See the spec's header: two `tab:` datatype properties, one shape, and a
widened `tab:RuleSpan` comment.

## 5. Next concrete action (written first)

1. **ASSERTED.** The remaining loops in the 2026-10-06 order are [[R301]] (this loop's deferred
   half: the producer-side guard, so fed-h41's merged tables escalate instead of aborting the page)
   and loop 4, contracts. Picking between them is the maintainer's call. R299 (Caltrain's held
   `tab:ClockTime`) is still open beside them.
2. **PROPOSED — R301's design rests on a prediction that has not been run.** It assumes one seam
   can withdraw a refused table and re-book its ink as escalated without the double count [[R73]]
   exists to prevent. Ten asserting sites in `compile.py` plus grid adoption book ink at assertion
   time (`asserted_total += …` beside each `RegionReport(…, "asserted", …)`). **Before designing,
   measure** whether a post-hoc withdrawal can find a refused table's booked tokens from its
   `RegionReport` alone (`tokens_asserted` and the report's `table_uri`), on fed-h41 p5 and p7. If
   it cannot, the guard has to sit at each producer, and the loop is ten times wider than it reads.
   Note [[R300]]: p5's report names `p5/adopt#htable3` while the graph holds `p5#htable3`, so the
   report-to-table join is already broken on exactly the page this needs.
3. **ASSERTED, if this loop's PR is not yet open:** finish acceptance. Read
   `$SCRATCH/snap/{main,branch}/*.json` (written by a scratch `snap_strip.py`; if the scratchpad is
   gone, rerun `scripts/corpus_verdict_snapshot.py` on both trees and strip the
   `tab:firstGlyphEnd`/`tab:lastGlyphStart`/`#rule-p…` triples before hashing). Pass = for each of
   the seven, `sha_stripped` equal across the trees, score and region verdicts equal; fed-h41
   `refused` with `rule_separated`; who-covid compiled. Then move `DOC_TRIPLES_WHEN_CARRIED` in
   `tests/test_carriage.py` (15611 → 18199, bfs, measured by the suite) citing the snapshot.

## 1. Goal

Ship tab:RuleSeparatedInkShape as a membrane-only guard (ruled 2026-10-08), with the facts it reads.

## 2. Where the primaries are

- Spec: `docs/superpowers/specs/2026-10-08-rule-separated-ink-design.md` (§ 1 holds the predicate run).
- Code: `src/iladub/etkl/ruleink.py`, its call in `compile.py` before the page-scope `_validate`.
- Vocabulary: `tab.ttl` (`tab:firstGlyphEnd`, `tab:lastGlyphStart`, `tab:RuleSpan ⊑ tab:PageLocated`),
  `tab-shapes.ttl` (`tab:RuleSeparatedInkShape`).
- Tests: `tests/test_rule_separated_ink.py` (pySHACL and rudof). FALSIFICATION: with the shape
  deleted, 3 of 11 fail (both engines' refusal plus the equality case). Restored, 11 pass.
- Local suite, 2026-10-08, chunked serially (237 files): the only failures were
  `test_cockpit` (handoff lacked `**Topic:**`, fixed), `test_carriage::test_bfs_p5…` (the triple
  pin, item 3), and `tests/etkl/test_header_stack.py::test_genuine_spanner_is_never_demoted_or_welded`
  (see § 3).

## 3. What was decided, and where it is recorded

- Membrane shape only, not a producer guard or per-cell withholding: the maintainer in chat,
  2026-10-08. Recorded in the spec's header and in [[R301]].
- **The spanner fixture is a misread the shape catches, not a false positive.** In
  `spanner_with_space_ruled_pdf`, 'Arrivals Total' sits over ruled columns 0-1, but the page
  asserts it as the label of ONE leaf column (`htable0-h0 coversColumn htable0-c1` only, measured).
  fed-h41 p5's merge has the same shape (`htable3-h0` covers `c0` only). The fixture's docstring
  already expected escalation. The test now compiles its A/B with `validate_shapes=False` and pins
  the refusal with `pytest.raises(MembraneRefusal)`. Recorded in the test comment and here.

## 4. Unverified or assumed

- **A spanner that IS read correctly, whose header node covers leaf columns on both sides of a rule
  drawn through its text, would also be refused.** No document or fixture shows that case; the shape
  has no allowance for it. If one appears, the allowance is "the reading declares the span"
  (covered columns on both sides of the rule), not a tolerance.
- The glyph-to-cell assignment (centre in the 2dp bbox) can share a glyph between overlapping cells.
  No instrument checks it.
- The stripped-hash comparison of item 3 had not finished when this was written.
