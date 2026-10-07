# Handoff: R296. Four red pins were R293's own move, and behind them is a dangling link the reading depends on (2026-10-07)

**Serves:** maintenance. Step (1) of the maintainer's "go in order" (2026-10-07), before loop 2
(Caltrain's header).

**Topic:** compile · **Date:** 2026-10-07

**Doc impact: none.**

Part 5 was written first, under the originating floor. § 6 and the R298 corrections were appended at about 76K working tokens, past that floor. They are measurements, not design.

## 5. Next concrete action

1. **ASSERTED.** Loop 2, Caltrain's header, as ordered. Start from
   `2026-10-06-r295-arm-b-census-handoff.md` § 7. This loop does not change its input.
2. **PROPOSED.** [[R297]] (raised here) and loop 2 may be one question: *which lines above a
   record band's first data line belong to its boxhead*. On bfs p6 the donor's lines 2 to 4 are
   boxhead, the reader says so (`header_lines` = 4), and the donation still hands only line 0 to
   five continuations. If loop 2 builds a line-role oracle for Caltrain, check it on bfs p6 band 2
   before calling R297 a separate loop. If the oracle cannot read bfs p6, the two are separate.
3. **PROPOSED, and graded low because it was reached past the floor.** [[R298]]: a resolvable donation
   link makes p6 refuse adoption. My guess, not measured, is that document-level chain recognition
   follows `headerDonatedBy` only when its object exists. Read the adoption refusal
   (*"13 document-level triple(s) point at"*) before designing anything. No order has been given.

## 1. Goal

Make the four corpus-gated tests on `main` read their measured cause, so [[R170]]'s standing
detector (O3) can see again.

## 2. Where the primaries are

- **Bisect, one page.** `compile_tables(bfs, 6)` at `81a2ca6^`, `81a2ca6`, `ab75542^` and
  `ab75542` (worktrees, `PYTHONPATH` at each `src/`). The first three print `cells 294 asserted 327
  escalated 19`. `ab75542` (R293, #310) prints `288 / 312 / 34`. The only region that moved is
  band 2: `asserted 6 cells, 15 tokens` became `escalated BOXHEAD_EXCEEDS_RECORD, 0 / 15`. Every
  other region is identical. `ab75542`'s commit message predicts it: *"288 entries = the old 294
  minus the six header words."*
- **The defect behind the first pin.** Once the cell pin moved, the rest of
  `test_bfs_p6_reads_267_entries_under_band_2s_labels` ran for the first time since R293. On
  `main`, `#table2` has **no triples as subject**, and eight `tab:headerDonatedBy` links point at it.
  At `ab75542^` the same node was a full record table. The grid-donation site hard-coded
  `#table{donor_index}` (`compile.py`, the `donated is not None` branch), and R293's escalation
  mints the donor as `#region{idx}`.
- **Document scope is clean.** `compile_document(bfs)` on `main` carries **0** `headerDonatedBy`
  links, because p6 adopts its data grid. At `ab75542^` it carried 8, none dangling. So no shipped
  document graph carried the dangling link. Only the page-scoped reading did.
- **A fix was built and REVERTED.** `compile._donor_node`, used by both donation sites, named the node
  the donor actually became (`#ignored{i}`, `#region{i}` or the report's `table_uri`). With it the
  strict-xfail test passed, which is that test's falsification. It is not on this branch: see § 6.
- **Whole-corpus snapshot**, `main` (`5e39331`) against this branch:
  `scripts/corpus_verdict_snapshot.py` + `corpus_snapshot_diff.py`. Result: § 6.

## 3. What was decided, and where

- **The pins move. They are not a regression.** The pins are recorded in the test comments,
  dated, and name R293 and `ab75542`. R296's row (`residues-closed.md`) records the closure.
- **The donor half of the bfs p6 test is substituted, not weakened.** It used to read the
  donor's own labels. The donor no longer has labels, so the test now pins the five
  continuations' labels literally, as the page prints line 0. The claim that every link resolves
  moved to `test_every_donation_link_on_bfs_p6_resolves`, a **strict xfail** naming [[R298]]. The donor's `surfaceText` was tried as the
  oracle and refused: it is a column-clipped render (`0-19 an…`). Recorded in the test comment.
- **The `src/` fix is reverted, not shipped**, because the snapshot in § 6 refuted it. Recorded in
  [[R298]]'s row and in a `plimslop mark` on `compile.py`.

## 4. Unverified or assumed

- R297's severity in the corpus is measured only on bfs p6. R293 measured one `header_lines > 1`
  recording corpus-wide. A page with such a donor that does **not** adopt a grid would ship the
  duplicate labels in its document graph. None is known, and none was searched for beyond R293's
  count.
- The escalated-span-donor `URIRef(None)` path is inferred from reading the code, never run.
- Why a resolvable link blocks adoption is not measured. § 5 item 3 is a guess.

## 6. Whole-corpus snapshot (main `5e39331` against the reverted `_donor_node`)

`corpus_snapshot_diff.py`: **6 of 7 documents are byte-identical.** bfs changed:

```
bfs-population-bilan-2023      0.9073502162 -> 0.8878702398  triples  15611 ->  16843  CHANGED
    adopted  [5, 6] -> [5]
    chains   0 -> 8
    p6: score 0.9543 -> 0.9017   cells   288 ->   288   asserted   522 ->   312   escalated    25 ->    34
    + note: page 6: adoption refused — band 3 asserted a table that 13 document-level triple(s) point at (https://w3id.org/iladub/tab#headerDonatedBy)
```

So the dangling link is load-bearing: p6 adopts its grid only because the links point at nothing.
The fix was reverted. The branch ships the pin moves, the substituted test, and the strict xfail.
The four held-out documents are not in `corpus_verdict_snapshot.py`'s glob (7 files on each side).
They were not checked, but they have no grid donation known to this loop.
