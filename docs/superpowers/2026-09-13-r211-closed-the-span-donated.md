# R211 closed — the span the author drew is read, and graincorp's records carry their ports

**Serves:** prog:criterion:etkl:02 — Layers A and B are [[R211]]'s two arms. R211 closes here;
etkl:02 still needs a pinned floor and the maintainer's adjudication.
**Date:** 2026-09-13. **Branch:** `span-the-author-drew`, cut from `main` at `2d4850c`.
**Plan executed:** `docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md`, Tasks 1–8.

**Doc impact: increment.** New `tab:` terms and a new `etkl`-family example contract are declared
in published, CC-BY artifacts (`vocab/ontology/tab.ttl`, `examples/shipping/*`);
`docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM entry. No released assertion is
contradicted, so nothing blocks a release tag.

---

## 1. What shipped

**Layer A (compile).** A band whose wholly-drawn boundary vector is a STRICT SUBSET of a later
band's donates a spanning header to it. Two AXIOM derivations:
`vocab/queries/span-donation.rq` names the donor on clauses (a) earlier, (b) wholly drawn,
(c) the R203 licence, (d) `drawn(D) ⊊ drawn(R)`; `vocab/queries/span-covers.rq` places each label
over the recipient columns inside its own drawn interval. The evidence emitter is
`src/iladub/etkl/spangraph.py`; the relation and reading are `donation.span_offer`; the seam is in
`compile_tables`' record-table branch, compiling through `assert_hier_region` into `#htable{idx}`.

**Layer B (portal).** `feed.table_records` splits one row into one record per childless spanning
header, and the label reaches `ground.marker_field` through a SIBLING flag (`is_split_key`), not by
widening `is_section_marker`.

**The contract.** `examples/shipping/capacity-{contract,terms,shapes}.ttl`, wired into
`tests/corpus-manifest.ttl` — step (1) of the route off that document's 2026-08-20 hold.

**The proposer is handed the page.** `ProposeGrounding` gains `page_context`, filled from
`etkl:IgnoredBand`/`etkl:bandText` — the carrier R212 shipped.

## 2. The headline measurements (all run 2026-09-13)

| | before | after |
| --- | --- | --- |
| graincorp p0 entry cells | 390 | **406** (+16 = the leaf-column count) |
| graincorp p0 ink ledger | 406 asserted / 0 escalated | **unchanged** |
| header nodes over 16 leaf columns | 16, one per column | **9**, partition 1,1,2,2,2,2,2,2,2 |
| records from 27 rows | 27 | **189** (27 × 7 ports) |
| records carrying a grounded port name | 0 | **189** |

**The invariant holds: the reading moved, the ink did not.** `assert_hier_region` returns 406 and
band 3 carries exactly 406 tokens, so the hierarchical accounting books 406 asserted / 0 escalated —
byte-identical to the record path it replaces. The +16 cells are band 3's own line 0 ceasing to be
consumed as a header row; R176's `_book_recovered_ink` had already booked those label words, which
is why cells move and ink does not.

**The corpus is otherwise untouched.** `test_o3_no_page_loses_asserted_ink_to_a_merge` passes on all
27 pages; the 7-document battery passes with graincorp-capacity at score 1.0000; bfs p6's seven
strict-subset pairs stay refused by clause (c).

## 3. Five places the plan or spec was REFUTED by measurement

Each was measured before writing, reported, and a satisfiable form substituted (plan rule 5).

1. **DECISION B's falsifier is unconstructible at band level.** `_rule_boundaries` returns a vector
   only if every word lies wholly inside some interval, and a segment inside `[lo,hi)` has its
   centre inside `[lo,hi)` by arithmetic — so "a label whose ink centre falls outside its own drawn
   interval" cannot exist for a donor that owns a vector. Straddling and out-of-range labels both
   yield `None`, refusing for a different reason. Pinned on the EVIDENCE GRAPH instead, which
   carries the same force: the query must place a centre matching no interval nowhere.

2. **The plan's prescribed reading construction produces the reading its own negative forbids.**
   The plan says the donor's header row comes from `group_wrapped(donor_band, recipient_grid)`.
   Measured: that groups the donor's words by the RECIPIENT's columns, splitting the single label
   `Port Kembla` into two cells — i.e. exactly the doubled reading
   `tests/tab-span-doubled-label-leak.ttl` exists to refuse. Labels are grouped by the interval the
   QUERY placed them in.

3. **The plan's File Structure names the wrong harness.** `tab:` examples and negatives live in
   `tests/test_tab.py` with examples under `examples/tables/`, not `tests/test_vocab_shapes.py`.

4. **`tab:headerDonatedBy` cannot carry this provenance.** Its domain and range are both
   `tab:RecordTable`; a span donation's product is a `tab:HierarchicalTable` and its donor is
   usually an IGNORED band with no table URI at all (graincorp's band 2 mints `#ignored2`). Reusing
   it would mistype the table and dangle. New rangeless `tab:spanHeaderDonatedBy`.

5. **Evidence § 4's UNVERIFIED document-scope question is not answerable on this document.**
   `_legs_for_document` gates the TAB leg on `recognized or section_facts`; graincorp has one page,
   so it returns `("dec",)` and the document-scope TAB leg never runs. Neither input is a function of
   how band 3 is read, so a donation cannot open that condition.

## 4. Falsification evidence

| task | inversion | result |
| --- | --- | --- |
| 1 | delete the column-containment filter from `span-covers.rq` | partition test RED (4 of 5) |
| 2 | delete clause (d)'s subset leg | S1 admitted RED **and** the bfs p6 negative RED |
| 3 | remove the offer at the seam | 4 reading tests RED, **ledger test stays GREEN** |
| 4 | delete *covers more than one* | `Year` becomes a key, RED |
| 5 | revert `marker_field`'s gate to the single flag | split key quarantines, RED (exactly 1) |
| 6 | hard-code `page_context` to `None` | slot-is-FILLED RED, other three green |

Task 3's separation is the loop's central claim: the reading tests redden while the ledger test does
not move, which is what "it changes the reading and not the ink" means operationally.

## 5. What is NOT claimed

- **The measures are not grounded.** Under the corpus battery's abstaining proposer `ship:capacity`
  grounds 0 — exactly as spec § 3.3 predicted — so [[R213]]'s invisible-`0` hazard is not live in CI.
  It becomes live the first time a real proposer runs against this contract.
- **The year is still missing.** [[R215]] is visible in the grounded graph: 14 of 189 offers carry a
  `ship:year`, because the author prints it once per group.
- **etkl:02 is not met.** R211 closes; the criterion needs a pinned floor and the maintainer reading
  the carried grid against the page (route step 3 of the manifest's hold note).

## 6. The reading verified four ways, and R213 measured (added 2026-09-13, after `7482db3`)

The maintainer's read (route step 3) was scoped down by measurement rather than left whole. The
question *"is each value under the right port?"* is answered by four checks, each using a different
instrument, and the last two were run only because the maintainer declined to accept a check I had
wrongly handed to them.

| check | instrument | result |
| --- | --- | --- |
| structure | `region_tiles` / SHACL | 16 leaf columns covered exactly once; partition 1,1,2,2,2,2,2,2,2 |
| content | `pdftotext -layout` (spec § 2.5, a different loop) | all 7 distribution figures identical |
| per-cell geometry | each entry cell's bbox vs its port's drawn interval | **406 of 406 inside, 0 outside** |
| ruling vs print | nearest printed label ink, using NO drawn rules | **406 agree, 0 disagree** |

The fourth is the one that retires *"only an eye can settle whether the drawn rules sit where the
labels appear"*. Assigning every data word to a port by proximity to the printed label ink — a rule
that never consults the ruling — reproduces the drawn-interval assignment exactly. And every label
is wholly inside its own interval with left/right gaps matching within about 1pt (`Mackay`
28.92/28.62, `Gladstone` 24.07/24.32, `Fisherman Islands` 8.85/9.93), which is what a centred label
over its own drawn cell looks like; an offset ruling would show as a lopsided or overflowing label.

**[[R213]] is MEASURED and stays open.** Its central unmeasured question was *how many of the 110
zero-reading cells are the invisible glyph*. The answer is all of them, by set identity rather than
by a matching count: each of the 110 carries a glyph whose colour matches the filled rectangle
behind it, dark navy `(0.063, 0.2, 0.353)` on `(0.114, 0.169, 0.314)`, and none is genuinely
printed. The page's other 144 zero glyphs are black on pale blue — the zeros inside printed
tonnages such as `10,000`. So invisibility is **decidable from the PDF**, which is a remedy path the
row did not have; what it is not is a repair, because deciding what to emit for an invisible glyph
(nothing, a typed absence, a proposition) is a §8 classification and not a change to slip into this
loop.

## 7. Residues

**Closed:** [[R211]]. **Raised:** [[R222]] (a non-contiguous span is refused by nothing in the
shipped membrane — measured, left open because interval containment makes it unreachable and
DECISION C forbids authoring a shape), [[R223]] (`tab:colX0`/`tab:colX1` are each declared twice in
`tab.ttl` with conflicting ranges, and two emitters mint them at the two datatypes).
Register after this loop: **213 rows, 67 closed, 146 open.**
