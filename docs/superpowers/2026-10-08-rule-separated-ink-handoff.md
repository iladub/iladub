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
