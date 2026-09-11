# Handoff — the donor's header is derived, and adoption is not the cheaper arm


**Topic:** [[R203]], the donor's header derived — the measurement loop before the donation plan
**Date:** 2026-09-11. **Loop shape:** a MEASUREMENT loop against the previous handoff's § 5c/§ 5d,
run before the donation plan. No compiler behaviour changes. One instrument committed.
**Doc impact: none.**

Part 5 was written first, under the 50K originating floor.

## 5. The next concrete action

### 5a. ASSERTED — write the donation PLAN, fresh session, against spec § 4; all four decisions are now settled

Decisions 1-3 stand as `2026-09-10-the-grid-the-author-drew-handoff.md` § 5a states them. Decision 4
([[R203]]) is resolved by measurement (`2026-09-11-the-donor-header-is-derived.md` § 1): *donate
under the donor's line 0 iff the page datagrid refuses that line `HeterogeneousColumn/every-measure`;
a body-row verdict, any other refusal, or no datagrid refuses the donation.* 12 of 12 censused
readings agree. Decision 1 gains one obligation (evidence doc § 4): the refusal must reach the page
evidence graph as a fact on the donor's line 0, identified by ink and never by index. The oracle
numbers are unchanged: 222 → 267 entries on bfs p6, 45 false labels → 0, every band tiles, no ink
lost (`scripts/grid_donation_spike.py`). Do not re-run § 5c or § 5d to decide; both are on disk.

### 5b. PROPOSED — the plan's evidence seam is `derive_data_grid` at page scope feeding `run_evidence`

The cheapest carrier is to run `derive_data_grid` once per page in the ordinary compile and emit
its `every-measure` refusals as page-line facts beside the band nodes. **Why proposed:** its cost
inside the ordinary path is unmeasured (it runs today only on adoption candidates), and the line
identity between `page_bands` and `text_lines(extract_words(...))` is asserted by one instrument on
7 pages. Measure both before task 1 depends on them.

### 5c. ASSERTED, and the maintainer's — [[R160]] now has the corpus instance its closure asked for

bfs p6: the band reader asserts 222 cells (45 false labels), the whole-page reader reads 288 entries
correctly, and adoption cannot be offered. Appended to R160's row. The reader-authority ruling stays
the owner's; nothing in the donation plan depends on it.

### 5d. PROPOSED — the same criterion is an [[R166]] instrument at page scope

All 11 false label rows in the corpus are body rows of their page datagrid (evidence doc § 2). A
rule refusing a record-table assertion whose line 0 the page grid places as a body row would fix
R166 corpus-wide and re-baseline six documents. **Why proposed:** the converse fails on titles and
on second tables under another universe, and nobody has counted what such a refusal does to the
bands that then escalate. Not this plan's scope.

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the instrument | `scripts/donor_header_criterion.py` | one run prints the 12 verdicts and every `every-measure` refusal per page |
| the measurement record | `docs/superpowers/2026-09-11-the-donor-header-is-derived.md` | § 1 the table, § 2 the converse, § 3 the § 5d weighing, § 4 what decision 1 must add |
| the ruling this serves | `docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md` § 4 | grid donation as specified |
| the plan's four decisions | `docs/superpowers/2026-09-10-the-grid-the-author-drew-handoff.md` § 5a | decisions 1-3 unchanged; decision 4 per § 5a above |
| the before/after oracle | `scripts/grid_donation_spike.py`, handoff `2026-09-10-the-donated-reading-tiles` § 2 | 222 → 267, 45 → 0 |
| the refusal's home | `src/iladub/etkl/datagrid.py:507-523`; `vocab/ontology/tab-datagrid.ttl:222` | the universal quantifier; `tab:HeterogeneousColumn` |
| the adoption gates | `src/iladub/etkl/compile.py:1251,1323`; `vocab/queries/adoption-candidate.rq` | both need `asserted_total == 0` |
| the register | `docs/superpowers/residues-open.md` R203, R160, R166 | the notes appended this loop |

## 2. What was measured

See the evidence doc; every figure there is from one run of the instrument at `808aa7a`.

## 3. What was decided, and where that decision is recorded

- **Decision 4 of the donation plan** (the donor's header is derived, not assumed): evidence doc
  § 2 and § 5a above. Nowhere else — it is a plan input, reversible until the plan ships.
- **Donation over adoption for bfs p6**: evidence doc § 3. Nowhere else.
- **Nothing about the compiler, and no residue closed.** R203 stays open until the derivation
  ships; its row records that the derivation exists.

## 4. Unverified or assumed

- One donor in the corpus exercises the licence; a page title as a donor's line 0 is not measured.
- `derive_data_grid`'s cost in the ordinary compile is not measured.
- No suite run this loop; the instrument is corpus-gated ([[R173]]) and has no CI test.
- The working-token figure is an estimate; no status-line reading was taken.
