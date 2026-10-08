# Handoff: R301's guard, prototyped at document scope: p7 escalates, adoption undoes p5 (2026-10-08)

**Serves:** maintenance. This is [[R301]], continuing `2026-10-08-r301-seam-measured-handoff.md`
(PR #319), whose § 5 sent this session to write the spec.

**Topic:** compile · **Date:** 2026-10-08

**Doc impact: none.** This adds one probe script and this handoff. No vocabulary, shape or compile
path changed.

The spec was **not** written. Measuring the predecessor's three PROPOSED items took this session to
about 78K working tokens, 1.6x the originating floor, before a design could be fixed. One of the
measurements refutes the seam position that the predecessor's § 5.1 marked ASSERTED.

## 5. Next concrete action (written first, at about 82K working tokens, over the 50K floor, graded per item)

1. **PROPOSED, and run it before writing anything on it: move the guard to before the adoption
   branch.** The predecessor placed it after `carry_from_pdf`, which runs after adoption. At
   document scope that position cannot see p5's refused table (§ 1, F2). The prediction to run:
   in `compile_tables` the order becomes differencing, then carry, then guard, then adoption, then
   carry again on the rebuilt graph, then score, then validate. With that order, p5's `/adopt`
   re-compile no longer reports band 3 as asserted (26 tokens on `adopt#htable3`). The band either
   escalates or is superseded by the grid. If the prediction fails, the position question is open
   again, and R301 may need [[R300]] after all.
   The test is to edit `scripts/r301_guard_prototype.py` so the guard runs inside `compile_tables`
   at that point instead of wrapping it. Run with `guard`, then read p5's region 3 and the R300
   line. About 4 minutes.
   *Confidence: medium.* The failure mechanism is measured. The remedy is reasoned from it, and
   the second carry is an unmeasured cost.
2. **ASSERTED, once item 1 holds: write R301's spec in a fresh session**, from § 1's F1 to F7. The
   spec must rule four things. (a) The position, from item 1. (b) The withdrawal extent: the
   table's URI-space roots minus explicit `dec:DecisionHolon` roots, closed over **blank nodes
   only** (F4). (c) The refusal decision: one `dec:DecisionHolon` per withdrawn table, chained
   onto the standing verdict through `_effective_verdict` (F5). (d) The escalation text of an
   appended region (F7).
   *Confidence: high that these four are the open rulings. None of the rulings is made here.*

## 1. What was measured

`scripts/r301_guard_prototype.py both` was run at `0f8c695` and took 201 s plus 227 s. Run 1 is
unguarded with `validate_shapes=False`. Run 2 wraps every `document.compile_tables` call with a
prototype guard and uses `validate_shapes=True`. The guard is placed after `carry_from_pdf`, as
§ 5.1 of the predecessor prescribed. It runs the shape's select, then for each owner table named
by exactly one report it withdraws the table's subgraph, escalates `{doc}#region{i}` and moves
the report's tokens from asserted to escalated.

- **F1. CONFIRMED: the document compiles, with validation on.** `compile_document(fed-h41,
  validate_shapes=True)` completes and nothing raises. Refused cells in the document graph go
  from 13 to 0. `sum(r.tokens_*) == page totals` holds on all 11 pages (asserted in the probe).
  The document score goes from 0.8530 to 0.8128, and all of the drop is p7: p7 goes from
  A=137 E=0 to A=0 E=137, and (2902-137)/3402 = 0.8128.
- **F2. REFUTES the predecessor's § 5.1 position at document scope: adoption undoes p5.** At page
  scope the guard withdraws `p5#htable3`, which is 113 triples with nothing pointing in, and books
  its 26 tokens as escalated. p5 is still an adoption candidate. Its `/adopt` re-compile rebuilds
  the page graph from the grid (the `graph = Graph()` in `compile.py`'s adoption branch). That
  rebuild discards band 3's table but keeps band 3's report verbatim as an untouched band,
  asserted 26 on `adopt#htable3` (R83's "the report is the authority for the rest"). The guard,
  which reads only the graph, finds no refused cell in that re-compile. `pages[5] = rep_a`
  installs the report. **Result, measured: p5 still reads region 3 as `asserted 26`, while the
  document graph carries the pass-1 `p5#region3` RULE_SEPARATED_INK candidate over the same ink.**
  That is a graph-versus-report contradiction, and it is R300's `p5/adopt#htable3` dangling join
  on the same region. p5's score is unchanged at 0.8486.
- **F3. The predecessor's § 5.2 premise was wrong in both directions.** p5 was already an
  adoption candidate before the guard: it escalated 225 tokens, and `adoption-candidate.rq` asks
  only whether a candidate exists. **p7 becomes one** (E goes from 0 to 137). Its `/adopt`
  re-compile takes `datagrid_fallback` again (gate `escalated_total == 0`). The guard withdraws
  the grid again, so the adoption is refused. The refusal comes from `grid_idx =
  len(pages[p].regions)` being out of range, because p7's pass 1 has an *appended* region, so
  `grid_idx` is not the band count the comment there claims. It is safe, but only by accident.
  It costs one extra page compile, and its note ("no data grid region on the re-compile") states
  a cause that is false here.
- **F4. Extent: `_band_subgraph` is the wrong closure for a grid.** It roots every IRI under
  `{t}-`, which includes `p7-datagrid-admission`, a `dec:DecisionHolon`. Through that decision's
  `dec:decidedBy` it pulls in `etkl:reader`, the one `prov:SoftwareAgent` that 9 other decisions
  on the page point at. `graph -= sub` would delete the agent from under them, and the §1g
  closure check would refuse the table instead. A closure over blank nodes only gives the exact
  extent on both pages: p5 is identical (6 blank-node bboxes, 113 triples), and p7 loses only
  `etkl:reader`'s 2 triples. The prototype still deleted the admission root. The document
  membrane passed either way, so **the shape does not decide whether the admission stays. The
  2026-09-29 "the log is a boundary" ruling does** (box-split spec § 10.7).
- **F5. The refusal needs a decision record, or `effective-chain.rq` lies.** p5 band 3's reading
  chain ends in `region3-d5`, labelled `verdict` and choosing `asserted`. p7's grid carries
  `p7-datagrid-admission`, which chose the grid. Withdrawing the table with neither of these
  superseded reproduces the failure documented at `document.py`'s adoption supersession site (on
  apple p1 the effective chain returned `escalated` for ink the graph asserted). The guard would
  be a third writer of `dec:supersedes`, beside section repair and adoption, chaining onto
  `_effective_verdict` under the 2026-09-14 lineage ruling. `dec:SupersededOnceShape` caps the
  in-degree at 1, and `effective-chain.rq` requires `dec:regarding`, `dec:order`, `rdfs:label`
  and `dec:rationale` on a superseding decision.
- **F6. Classification (the predecessor's § 5.3): the select is a pure positive conjunctive
  pattern.** It has no `NOT EXISTS`, no `COUNT` and no closure. Run at the producer as a SELECT,
  it is an AXIOM derivation in the open world: monotonic, and evidence-positive (the rule and both
  glyph extents must be present). The withdrawal it triggers refuses admission. It is not a fact
  derived from absence. Read the query from `tab:RuleSeparatedInkShape` so that the guard and the
  membrane cannot drift apart.
- **F7. An appended region has no escalation text.** The fallback region's `RegionReport` is built
  with `ascii=""` (`compile.py`, the `if datagrid_fallback and asserted_total == 0 …` block).
  The prototype passed a placeholder, so the provenance-to-the-page of the p7 candidate is
  **not** representative.

## 2. Where the primaries are

- The probe: `scripts/r301_guard_prototype.py`. Its full output is not committed. Re-run with
  `both` to get it.
- The seam: `src/iladub/etkl/compile.py`, from the `band_marks` differencing through the
  adoption branch (`if datagrid_adopt and escalated_total > 0`), the score, `carry_from_pdf`
  and the page-scope raise.
- Document scope: `src/iladub/etkl/document.py`. See `is_adoption_candidate`'s loop, `grid_idx`,
  the §1g withdraw-or-refuse block, `_band_subgraph`, `_remove_escalation_record` and
  `_effective_verdict`.
- Decisions: `src/iladub/etkl/decisionlog.py` (`BandRecorder.record`),
  `vocab/queries/effective-chain.rq` and `vocab/shapes/dec-shapes.ttl`.
- The predicate: `tab:RuleSeparatedInkShape` in `vocab/shapes/tab-shapes.ttl`.
- Rows: [[R301]], [[R300]] and [[R83]] (page-scope `rep.graph` versus report authority).

## 3. What was decided

Nothing was decided. F2 to F7 are measurements, and the rulings they call for belong to the spec
(§ 5.2). The 2026-10-08 ruling, which set loop 3 to the membrane shape only and deferred the
producer guard to R301, stands.

## 4. Unverified

- The remedy in § 5.1 is reasoned, not run.
- Whether the guard, once moved before adoption, changes any other page's adoption outcome. On
  fed-h41 only p5 and p7 hold refused cells, but an escalation added before adoption changes the
  ledger that adoption compares against.
- The cost of a second `carry_from_pdf` per adopting page has not been measured.
- The extent of a withdrawal on corpus documents other than fed-h41. On the 7 tuned documents
  plus the other 3 held-out documents, loop 3's census found the predicate firing on 0 cells, so
  the guard should be the identity there. That is inferred from that census, not re-run against
  the guard.
- Whether keeping `{t}-admission` (rather than deleting it) passes `dec:DecisionHolonShape` once
  its option-space IRIs have no triples. Reading `dec-shapes.ttl` (`optionSpace` minCount 2, and
  `chosen` must be in `optionSpace`) suggests it passes, but it was not run.
