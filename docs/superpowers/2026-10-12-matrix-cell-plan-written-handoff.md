# Handoff: the matrix-cell plan is written (2026-10-12)

**Serves:** maintenance — direction (b) of the 2026-10-06 ruling (contracts and grounding).

**Topic:** contracts and grounding · **Date:** 2026-10-12 · **Branch:** `matrix-cell-plan`, on
`main` at `94dc60c`.

Part 5 was written first. The session's working figure was not read from the status line. By what
was opened (the spec, the seams handoff, `feed.py` and `ground.py` in large part, one apple
compile) it is over the 50K originating floor, so each action below is graded. No `src/`,
`vocab/`, `examples/` or `tests/` file was changed.

## 5. The next concrete action, typed

1. **ASSERTED: execute `docs/superpowers/plans/2026-10-12-a-matrix-cell-is-an-observation.md` in a
   fresh session, Task 1 first.** Do not re-plan. The maintainer has not yet read the plan; its
   seven decisions (D1–D7) are his to overturn before or during execution.
2. **PROPOSED: Task 2 ends on a corpus run whose counts are all predictions** (180 records, 540
   concepts, 52 shared row keys, 6 column-key regions). They are derived from counts of the row
   reading and no per-cell reading has ever been run. If one fails, the loop stops there and
   reports; Tasks 3 and 4 are built on those counts.
3. **PROPOSED: Task 5's baseline diff is `inputs.json` alone.** If a snapshot moves, something in
   Tasks 1–4 touched a compile path, and that is a defect to find, not a diff to commit.
4. **PROPOSED, D7: the example's numeral pattern admits a leading `$ `.** A preference, not a
   measurement. It decides whether 40 of apple's 180 values ground.

## 1. Goal

One contract that names a line item, a period and a value grounds apple's two statements, one
record per cell, and nothing else in the corpus moves.

## 2. Where the primaries are

- **The plan:** `docs/superpowers/plans/2026-10-12-a-matrix-cell-is-an-observation.md`. Five
  tasks. § "Decisions this plan makes" and § "Review Focus" are what a reviewer reads first.
- **The spec:** `docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md`;
  § 9 overrides the rest.
- **The earlier seams:** `docs/superpowers/2026-10-12-matrix-cell-plan-seams-handoff.md` § 2a.

## 2a. What this session measured

On `94dc60c`, apple compiled once, script throwaway and not committed.

| what | result |
| --- | --- |
| `_spanning_keys` on both `mtable2`s | `()` on each |
| cells with `col is None`, under a column with no header path, or sharing a column path with another cell of their row | 0, 0, 0 of 180 |
| section markers in the 59 records | 0 |
| rows minting / rows with a row header path / covered rows | p0: 31 / 31 / 38; p1: 28 / 28 / 38 |
| shared rows, counted over minting rows and over all covered rows | p0: 11 and 11; p1: 4 and 4 |
| a label cell's `tab:onPage` | an `xsd:integer` literal, 0 or 1 |
| a label cell's fragment, an entry region | `mtable2-chl0`; `p0-305-143` |
| `grep -rn etkl-shapes src` | empty: nothing validates a contract at load |
| `ContractField(` sites | 1 in `src`, 6 in `tests`, 1 in `scripts` |
| population pins that new `.ttl` files or `etkl:` terms may move | `tests/test_artifact_terms.py` (`== 181`, `== 72`, `== 67`, `== 21`), `tests/test_artifact_declarations.py` (`== 181`, `== 57`) |
| PR #338 | merged as `94dc60c`; the spec, its § 9 and both earlier handoffs are on `main` |

## 3. What was decided, and where it is recorded

- **D1–D7**, the plan's § "Decisions this plan makes". Recorded there and nowhere else. They are
  this session's, not rulings, and each says why apple cannot test it.
- **`load_contract` refuses a contract the role shape refuses, by running the shape.** Plan
  Task 1. Recorded only there. It adds a SHACL validation to every contract load.
- **The pass-3 id guarantee must be restated per record** (D4). The spec's "then the existing
  pass-3 guarantee" does not hold as written for two cells of one row.

## 4. Unverified or assumed

- **No per-cell reading has been run** (as § 5.2).
- **D1–D6 are exercised by no corpus document.** Only the synthetic tests of Task 2 can pin them,
  and those setups were not constructed in this session.
- **What validating a contract at load costs** was not timed.
- **Whether a `CellValue` field with no value constraint should be allowed** is left to Task 3's
  first seam. Under the shipped oracle it would ground every cell by field identity.
- **That `_record_uri` gives 180 distinct subjects on apple** is a prediction. The slug collapses
  punctuation, and per-cell ids are long.
- **The plan was self-reviewed, not reviewed.** It was written over the originating floor.
