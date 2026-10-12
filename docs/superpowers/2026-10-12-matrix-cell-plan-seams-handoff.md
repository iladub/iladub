# Handoff: the matrix-cell spec's seams, measured before the plan (2026-10-12)

**Serves:** maintenance — direction (b) of the 2026-10-06 ruling (contracts and grounding).

**Topic:** contracts and grounding · **Date:** 2026-10-12 · **Branch:** `contracts-candidate-measured`
(PR #338), on `main` at `f976a82`.

Part 5 was written first. The session's working figure was not read from the status line; by the
size of what was opened it is near the 50K originating floor, so each action below is graded. No
plan was written, no `src/` or `vocab/` file was changed, and the spec was not edited.

## 5. The next concrete action, typed

1. **ASSERTED: the plan is not written until S1, S2 and S3 are ruled into the spec.** Each is a
   place where `2026-10-12-a-matrix-cell-is-an-observation-design.md` says something the code
   cannot do or does not do (§ 2a). They are spec changes, so they go in a new spec § 9, appended,
   in this PR while it is open. The plan then cites § 9.
2. **PROPOSED, S1: a key's region is the header label cell itself, page-qualified.** Spec § 3.3
   gives each key "the label cell" as its region and § 8 assumed a provenance region exists there.
   None does. The recommendation is to name the label cell by `tab:onPage` and its own IRI
   fragment, both RDF reads, and to raise a residue for the compile-side fact (a header label cell
   has a box and a page and no `prov:wasDerivedFrom`). The alternative, minting the provenance at
   compile, moves every document's graph hash and is a reading change. If the maintainer prefers
   it, it is its own loop and comes first.
3. **PROPOSED, S2: a shared row label is refused by rule, not left role-less.** Spec § 3.4 mints
   it with no role and expects quarantine. That holds only under the abstaining proposer. The
   recommendation is a third value on the new role field that no contract can declare, and one
   branch in `ground_concept` that emits the candidate under a rule suggester and returns
   `proposed` without asking a proposer. The reason is CLAUDE.md § 8: nothing can dispose a
   proposal here, because the scheme admits the label and the admission is the defect.
4. **PROPOSED, S3: the shared-label count is per logical table, over the row header path.** Spec
   § 3.4 says both that and "reuses the multiplicity `table_records` already computes". That
   multiplicity is global across tables and keyed on the row id, which carries the section-caption
   prefix. The two agree on apple and can disagree elsewhere. The recommendation keeps § 3.4's
   stated scope and drops the reuse clause.
5. **ASSERTED, after the rulings: write the plan in a fresh session**, from the spec with § 9 and
   from § 2a here. The seams a plan would otherwise have to measure are closed below.

## 1. Goal

One contract that names a line item, a period and a value grounds apple's two statements, one
record per cell, and survives the next filing.

## 2. Where the primaries are

- **The spec:** `docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md`.
  § 3 is the design, § 5 the predictions, § 8 the list this handoff works through.
- **The record reader:** `src/iladub/feed.py`, `table_records` (pass 1 computes `multiplicity`,
  pass 2 mints), `_read_table` (where an entry cell's region is read), `_spanning_keys` (the
  shipped precedent for a key's region, with its fallback).
- **The disposal:** `src/iladub/ground.py`, `ground_concept` (four branches, in order),
  `_grounds_to`, `_admissible_fields`, `_emit_candidate` (where a region becomes an IRI).
- **The corpus gate:** `tests/test_corpus.py::test_grounding_where_contracted`, which reads
  `cor:contract`, `cor:terms` and `cor:shapes` from `tests/corpus-manifest.ttl`.

## 2a. What was measured

On the branch head `20282cb` (no `src/` or `vocab/` difference from `f976a82`). Scripts were
throwaway and are not committed.

| # | spec claim | measurement | verdict |
| --- | --- | --- | --- |
| S1 | § 8: a row header's and a column header's label cell carry a provenance region | apple, both `mtable2`s: 76 row header nodes and 14 column header nodes, every one with `tab:hasLabel`, a `tab:hasBBox` and `tab:onPage`; **0 of 90** label cells carry `prov:wasDerivedFrom`. Entry cells: 180 of 267 carry it, and those are the 180 the feed reads. `_spanning_keys`'s fallback takes the label cell's IRI fragment, and **42 of 48** distinct fragments occur on both pages (`mtable2-rhl9` on p0 and p1). An entry region is page-qualified (`p0-305-143`) | **refuted** |
| S2 | § 3.4: a role-less shared key "is quarantined … never grounded" | `ground_concept` on `SurfaceConcept("Mackay", "Mackay", "r1")` against `examples/shipping/capacity-*`: abstaining proposer → `proposed`; a `FakeGroundingProposer` that names the port field → **`grounded`**. `_admissible_fields` is non-empty because the scheme carries the label, so the proposer is asked and scheme membership admits its answer | **refuted** under any proposer that answers |
| S3 | § 3.4: the count "reuses the multiplicity `table_records` already computes" | read at `table_records` pass 1: `multiplicity` is one dict across all logical tables, keyed on `rid_of[row]`, which is prefixed by the member's first caption. On apple no row header path is shared only across the two tables, so both scopes give 15 rows | **inconsistent with § 3.4's own scope**; not observable on apple |
| S4 | § 8: `contract.py` may be a second loader | `SemanticDataContract` reads `etkl:targetClass` and nothing about fields. `grep -rn hasField src`: four readers, `ground.py:93`, `bridge.py:92`, `to_rdf.py:65`, `timeline.py:30`. Only `ground.load_contract` builds a `ContractField`; no other `src/` file constructs one | no second site for § 3.2. The other three readers would ignore a role; whether a role contract ever reaches them was not checked |
| S5 | § 5 P5: "whether the baseline records grounding at all" | keys of `tests/corpus-baseline/apple-fy2026q3-statements.json`: `adopted, chains, graph_sha256, graph_triples, notes, pages, pdf, recognized, refused_licences, repaired_bands, score`. No grounding | it does not. The baseline must still be regenerated, because `src/` and `vocab/` are inputs |
| S6 | § 8: a wrapped header label may be joined upstream | apple column paths are three separate header nodes each (`Three Months Ended`, `June 27,`, `2026`); no row label carries a newline or a double space | space-join meets nothing joined upstream on apple |
| S7 | § 8: whether who-wfa's 19 labelled records have row header paths | its three `mtable`s have 7, 6 and 6 rows, all with a row header path and all cells under a column path. Its `htable`s and `table4`s have none | a role contract on who-wfa would read those 19 rows per cell |
| S8 | § 5 P4, the numeral pattern | apple's 180 cell texts by digit shape: `9,9` 125, `$ 9,9` 32, `$ 9.9` 8, `9,9,9` 8, `(9,9)` 3, `9` 2, `(9)` 2 | 40 cells carry a `$ ` inside the cell text; the pattern must say whether that is a numeral |

P1 and P3 follow from counts already taken: 180 concepts today is 180 records under § 3.3, and
the shared rows are 11 on p0 at four periods and 4 on p1 at two, which is 52.

## 3. What was decided, and where it is recorded

- Nothing was decided. Items 2, 3 and 4 of § 5 are recommendations and are recorded only here.
- The maintainer's two rulings of 2026-10-12 stand as spec § 2 records them.

## 4. Unverified or assumed

- **No prototype of the per-cell reading was run.** P1, P2, P4 and P6 are still predictions.
- **S2 was shown on graincorp's contract, not on a finance contract**, because none exists. The
  mechanism is contract-independent by reading; the run is one document's.
- **S3's disagreement case was not constructed.** No corpus document was searched for a row label
  shared across two tables and unique within each.
- **The S1 recommendation assumes `tab:onPage` on a label cell is the page of its ink.** Read off
  one sample cell's predicates, not checked against the page.
- **Whether a label cell's region may share the `urn:iladub:region:` space with entry regions**
  without a consumer mistaking one for the other was not checked. Two sites in `src/` build
  that IRI: `ground._emit_candidate` (`ground.py:161`) from a concept's region, and
  `splitkey.py:136` with a fixed name.
- **who-wfa under a role contract (S7)** would also carry its split spanner (`Z-scores (weight in`
  / `kg)`) into six column keys. Seen, not chased.
