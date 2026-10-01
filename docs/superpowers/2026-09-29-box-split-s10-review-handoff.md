# Handoff: box-split — review spec § 10 before anything is planned on it (2026-09-29)

**Topic:** box-split · **Date:** 2026-09-29

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) is whole only when T2 compiles with no boxhead.

**Doc impact: none** (this handoff). The spec now declares `increment` for § 10.

Authored at 102,799 working tokens (plimslop hook), about 2× the originating floor. The session
self-estimated 40K and was wrong by about 60K. Parts 1–4 are pointers. **Part 5 is graded per
action.**

## 5. Next actions (written first)

- **Proposed. A fresh session reviews § 10 adversarially** (memory: adversarial spec review). § 10
  was reasoned over the floor, and the preamble inside § 10 says so. Attack three things:
  - **§ 10.3.4's ask gate:** "asked iff not donated and no witness". Does it make the oracle vacuous
    as a disposer? It never sees a `0` it could refuse. Is that the ruling's "one-way oracle", or a
    pre-filter wearing its name?
  - **§ 10.3.1's two-shape split.** `BoxheadAbsenceShape` sits in tiling and
    `BoxheadAbsenceDecidedShape` binds at compile scope only. Is compile scope actually reached by
    every path that emits the statement?
  - **§ 10.6's choice not to record a decision on witnessed tables.** It keeps I-10-1, at the cost
    of leaving the positional default unaccountable.

  If any attack lands, amend § 10 before planning. If none lands, the maintainer approves.
- **Asserted, after approval:** a Task 3d plan (or an SDD brief), then Task 3d, then Task 4 Steps
  4–5, then Tasks 5–6 of `docs/superpowers/plans/2026-09-28-box-split.md`.
- **Proposed, and it may fail:** the worker answers T2 with `0`. No worker has been asked yet (§ 10.5
  O2).

## 1. Goal

O2 XPASSes as a whole: T2 is a RecordTable with 0 header nodes and 4 rows, and T1 keeps its
7-column boxhead.

## 2. Where the primaries are

- **Spec § 10:** `docs/superpowers/specs/2026-09-28-box-split-design.md` (lines 502–end). The header
  `Doc impact` is changed to `increment` at line 8.
- **§ 10.2** is the corpus-wide oracle census. It is measured, and it is the most reliable part.
- **The probe:** session scratchpad `s10/probe.py`, which is not durable. The census output is quoted
  in § 10.2.
- **The rulings:** the addendum to `docs/superpowers/2026-09-28-box-split-t2-measurements.md`.

## 3. What was decided, and where it is recorded

- The rulings (form, decider) are recorded in the measurements addendum. They are the maintainer's,
  and they were not re-opened.
- The **design choices in §§ 10.3–10.6** are recorded **only in the spec, unapproved**, and they are
  reversible. They are:
  - the property name `tab:boxheadAbsentBy`;
  - the two-shape split;
  - the four witness features;
  - the ask gate;
  - the Haiku client;
  - the `readings/header_lines/` key;
  - no decision on witnessed tables.

## 4. Unverified or assumed

- **The census witness was computed in Python, not by the `.rq` § 10.3.2 specifies.** The plan's
  U9 is the first run of the query form.
- **Colour equality compared `str()` of pdfplumber values.** § 10.5 MEASURE (iv) is owed.
- **"Asked" questions are predicted to dedupe across passes** (the `p`, `r2` and `adopt` passes)
  **by key.** This is not measured.
- **No `tab:hasHeaderNode` consumer was checked against a table with zero header nodes** (MEASURE
  (i)).
- **The bfs p6 `#table2` reading, "a 4-line header, no numeric body", is inferred from the text of
  row 0 and row 1 only.**
