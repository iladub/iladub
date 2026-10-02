# Handoff: R261 loop (b) — the grand total's question HOLDS; write the spec (2026-10-02)

**Serves:** prog:criterion:etkl:03 — loop (b) of the R261 totals family; the role question ran
before any spec, as ordered, and held.

**Doc impact: none.**

Authored at about 45K working tokens, under the originating floor (50K). The spec was NOT started
in this session because it would cross that floor mid-draft. Part 5 was written first.

## 5. Next actions (written first)

- **Asserted — the outcome is known; doing it is the work.** The maintainer reviews and merges the
  PR that carries this handoff, the P4/P4b evidence, the probe script, and register row R287.
- **Asserted, with the design decisions already ruled (part 3):** a fresh session writes the
  loop (b) spec with `superpowers:brainstorming`, resuming at *"present design sections"*. It does
  not re-run the approaches stage, and it does not re-probe the wording. Run the skill
  `managing-context-budget` first.
- **Proposed — the first thing the PLAN must run, and it may fail.** P4b was asked over raw HTTP
  with a literal `Reply with JSON only` line. Production will ask it through a BAML function whose
  `ctx.output_format` replaces that line, as P1 → `AskPrintedTotal` did. The prediction is that the
  BAML-rendered question reproduces P4b on the same 6 cases (target `total_of_totals` ×3, no null
  `total_of_totals`). It is unrun. If it fails, the wording is not re-tuned: the grand total goes
  back to the maintainer as a ruling (exact arithmetic over admitted totals alone, or unbound).
  The spec must make that run plan Task 1, the way P3 was the R261 plan's Task 1.

## 1. Goal

Bind cbh p0's `1,951,264` as a total of the four bound port totals. It binds only when the exact
Decimal sum of every `tab:PrintedTotal` bound on the page holds AND a NEURAL worker, asked the
closed role question on the derived crop, answers `total_of_totals`.

## 2. Where the primaries are

- **The probe evidence:** `docs/superpowers/2026-10-02-r261-grand-total-role-probe.md`.
  - § 1: why P3 refuted a wording, not the level.
  - § 3: the recorded answers on both crops.
  - § 4: the 22,858 control failing on the derived crop.
- **The probe:** `scripts/r261_grand_total_role_probe.py`. The wording, the enum, the derived-crop
  construction and the run command are all here, so read the wording from this file and don't copy
  it from memory.
- **The R261 spec:** `docs/superpowers/specs/2026-10-01-r261-totals-family-design.md`. Re-establish:
  - approach A, the bind at band dispatch: carve the bound line and reclassify the remainder;
  - the Note fate ruling: normal classification, disclosed;
  - § 2.2's second bullet, the total-of-totals branch, which was dropped and is stale under P3;
  - § 6, "What is not done".
- **The R261 evidence:** `docs/superpowers/2026-10-01-r261-totals-family-evidence.md`. § 6 is P3;
  §§ 1.2/7.4 hold the band-9 baseline.
- **The table-level code** the totals level extends. Read each, don't assume:
  - `src/iladub/etkl/printedtotal.py`: the worker, the recorded readings keyed on the question name
    plus the listing, and `crop_table`;
  - `src/iladub/etkl/compile.py`: `_bind_printed_totals`, the carve;
  - `src/iladub/etkl/document.py`: R7, pass-2 adoption by the `tab:totalOf` link;
  - `src/iladub/etkl/holon.py`: `emit_printed_total`;
  - `baml_src/printed_total.baml`.
- **cbh's hold:** `tests/corpus-manifest.ttl`, the two `cor:adjudication` notes on
  `urn:iladub:corpus:cbh-stem-2026-08-03`.
- **The register:** R261, R287, and R284 (a carved donor). Read R284 because a second carve on the
  same page is new exposure to it.

## 3. Decided, and where recorded

- **Run before spec, the question, the population and the decision rule:** approved in session by
  the maintainer on 2026-10-02. The rule is recorded in the evidence § 2. The question **holds** on
  both crops, per evidence § 4.
- **Spec on the DERIVED crop; the 22,858 miss goes first as a concern and is not tuned away now:**
  the maintainer, 2026-10-02, recorded in evidence § 5 and in R287.
- **Arithmetic proposes:** the operands are every PrintedTotal bound on the page, as the R261
  spec's 2026-10-01 ruling says; that ruling is recorded in the spec and in its handoff.
- **The worker disposes, binding only on `total_of_totals`:** follows from R47's ruling
  (worker AND sum), recorded in the R261 spec. Its extension to the totals level is recorded only
  here and in evidence § 5, so it is reversible.
- **Concerns the spec states FIRST,** under the "ship compiling" ruling of 2026-09-18:
  1. R287.
  2. Once `1,951,264` is carved, the Note in band 9 reclassifies as ignored, not read. Lifting
     cbh's hold is the maintainer's call, not this loop's.

## 4. Unverified or assumed

- **The BAML-rendered wording reproduces P4b.** Unrun; this is part 5's proposed action.
- **Whether the totals-level crop needs the red box drawn by production code.** A drawn box is ink
  that is not on the page. It is a pointer, like the value string, but the recorded-readings key
  must then cover the crop, not only the listing. That is a spec decision, unmade.
- **The carve on band 9.** The grand total is line 0 of a band it shares with the Note, which is
  the same shape table level's D6/D8 carve handles. That it handles it unchanged is unmeasured.
- **What a total of totals is, in the graph.** The term to use and whether it is `tab:totalOf` the
  PrintedTotals or something else is a spec decision. The R261 spec's § 2.2 sketched it before P3
  and is stale.
- **Context figure.** About 45K working, from `plimslop preflight` at 40,061 plus the writing since.
