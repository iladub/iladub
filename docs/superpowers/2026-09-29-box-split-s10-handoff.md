# Handoff: box-split — author spec § 10 (T2 has no boxhead) from two rulings (2026-09-29)

**Topic:** box-split · **Date:** 2026-09-29

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) is whole only when T2 compiles with no boxhead.

**Doc impact: none** (this handoff). § 10 itself will carry `increment` (a `tab:` term and a shape change).

Authored at ~45K working tokens, measured by `plimslop preflight`, under the originating floor. It
was handed off rather than written here because § 10 would have finished well past the floor.

## 5. Next actions (written first)

- **Asserted:** a fresh session authors spec § 10 in
  `docs/superpowers/specs/2026-09-28-box-split-design.md`, from the two rulings. It is classified
  under CLAUDE.md § 8, and it carries its contract and a FALSIFICATION block in the § 8.4/§ 9.5 form.
  Doing that is the work. The rulings are not re-opened.
- **Proposed, and it may fail. Measure it while authoring, before § 10 relies on it:**
  - **The one-way oracle refutes a wrong "row 0 is data" answer on T1.** Predicted from the style
    census (T1's row 0 has a full-width fill, white regular text, and a text-over-numbers datatype
    change). It has **not** been run as an oracle.
  - **The census also predicts** that the oracle admits "data" on cbh T2 and on who p0/p1 `#table4`,
    and cannot refute a wrong "data" on bfs p6 `#table2`.
  - If the oracle cannot be stated as a query over an evidence graph (AXIOM, holon-scoped), the rule
    is "no oracle, no worker", and § 10 has to say so.
- **Asserted, after § 10 is approved:** SDD dispatch, then Task 4 Steps 4–5 (flip O2, re-pin the cbh
  literals once), then Tasks 5 and 6 of `docs/superpowers/plans/2026-09-28-box-split.md`.

## 1. Goal

Make O2 XPASS as a whole. T2 compiles as a RecordTable with 0 header nodes and 4 data rows, and T1
still reads its 7-column boxhead.

## 2. Where the primaries are

- `docs/superpowers/2026-09-28-box-split-t2-measurements.md` (`86a39e9`, plus the rulings addendum)
  holds:
  - the path (§ 1);
  - why the ons reader does not fit (§ 2);
  - the unconstructible O2 state (§ 3);
  - the page evidence and the 13-table census (§ 4);
  - the rulings (addendum).

  **Read this first.**
- **Spec:** `docs/superpowers/specs/2026-09-28-box-split-design.md`.
  - § 4 risk 1 is T2.
  - § 8.4 and § 9.5 are the contract form to copy.
  - § 8.0: the branch does not merge until O2 XPASSes.
- `docs/superpowers/2026-09-28-box-split-t3c-handoff.md` part 3 holds the two register rows owed at
  Task 5, and the deferred minors.
- **Seams § 10 must name** (the measured sites; the next session re-measures them at HEAD):
  - `vocab/queries/classify-kind.rq`: the line-0 word-count gate.
  - `holon.py:181-207` `assert_record_region`: it mints a HeaderNode per column, and row 0 becomes the
    label row.
  - `compile.py:1284-1285`: the `region_tiles` gate.
  - `tab:CoverageShape` and `tab:UnambiguousAccessShape` in `vocab/shapes/tab-shapes.ttl`, and
    `_TILING_SHAPE_IRIS` in `tiling.py`.
  - The worker precedent: `etkl/boxhead.py`, `baml_src/boxhead.baml`, `readings/boxhead/`, with its key
    `sha256(ncols+listing)`. T2 needs its own directory and a key that includes the body rows.
  - The style evidence: pdfplumber `fontname`, `non_stroking_color`, and the rect fills under each cell
    centre. `boxes.py:113-121` is the only place fills are read today.

## 3. What was decided, and where it is recorded

- **The headerless form is a positive, decision-produced no-boxhead statement** that exempts the table
  from Coverage and UnambiguousAccess, and the O2 test stands as written. Recorded in the
  measurements addendum.
- **The decider is NEURAL**, answering "how many leading lines are header" as a closed int. It is
  disposed by a one-way oracle, and a "header" answer keeps today's behaviour. The unrefutable case
  becomes a register row. Recorded in the measurements addendum.
- **The style proxy is the one geometric attempt, and it is refuted** on bfs p6 `#table2`. That
  follows from the census in the measurements, § 4. It is reasoning, not a separate ruling.

## 4. Unverified or assumed

- **who p0/p1 `#table4` being data rows read as headers is INFERRED from their text.** Nobody has
  looked at the page.
- **The census proxies are the probe's own definitions, not repo terms.** The probe scripts were in a
  non-durable scratchpad.
- **Which RECORD tables the worker is asked about has not been decided.** The census counts 13 in
  final graphs, and the asking population and its live-call cost are § 10's to state.
- **cbh numbers after `7263784` are still the implementer's run**, as in the t3c handoff, part 4.
- **The live reader needs the API key:** `source ~/.zshrc` before `BAML_LIVE=1`. It is not exported
  into the tool shell.
