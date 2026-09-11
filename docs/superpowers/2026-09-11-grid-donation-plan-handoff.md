# Handoff — the donation plan is written; execute it, do not re-plan

**Topic:** [[R201]] / [[R203]], the grid-donation PLAN — the ASSERTED action 5a of
`docs/superpowers/2026-09-11-the-donor-header-is-derived-handoff.md`

**Date:** 2026-09-11. **Loop shape:** a PLAN loop (originating), off `main` at `808aa7a` with PR
#198's evidence doc. No compiler behaviour changes. One plan, one measurement script, no code. **Doc impact: none** for this loop; the plan it writes
declares **increment**.

Part 5 was written first, under the 50K originating floor (preflight logged: 0 working tokens at
start; the session's total was not read from a status line).

## 5. The next concrete action

### 5a. ASSERTED — execute `docs/superpowers/plans/2026-09-11-grid-donation.md`, fresh session, six tasks

Cut the branch from `main` **after** PR #198 and this handoff's PR have merged (the plan cites the
evidence doc that lives in #198). The plan carries every measurement it rests on inline (§ Measurement:
M1–M3 and the bfs baseline), takes five decisions once (DECISIONS A–E) and cites them from the tasks,
supplies every test verbatim as a proposition, and names a FALSIFICATION per task. **Why asserted:**
the outcome of executing it is known to within the propositions listed in 5b/5c, both of which the
plan's own tasks run before anything is built on them; the oracle numbers (222 → 267 entries, 45 → 0
false labels, every donated reading tiles) are on disk from two prior loops and were reproduced this
session through the plan's construction, not the spike's (M3).

### 5b. PROPOSED — donation moves no ink between the ledgers: tokens, page score and document score are unchanged

DECISION D predicts bfs p6 keeps `asserted 276 / escalated 25`, page score 0.9169, document score
0.4033, and per-band tokens 36/54/36/72/63, because the donor's label bboxes lie outside every
continuation band and each band's own line 0 becomes round-tripping data cells. **Why proposed:** it
is reasoned from `_book_recovered_ink`'s contract (`compile.py:276-306`), not measured through
`compile_tables`; the plan's Task 4 test `test_donation_moves_no_ink_between_the_ledgers` is the run.
If it is refuted, the plan's oracle (entry count + label texts) still stands and the manifest reading
simply records the moved figure.

### 5c. PROPOSED — `derive_data_grid` refuses the synthetic reportlab head line `every-measure`

The plan's end-to-end CI pin (Task 4, `test_a_headerless_band_reads_under_the_ruled_head_above_it`)
would carry the R203 licence through the real refusal map if the datagrid refuses `Region | Total |
Share` on the synthetic page. **Why proposed:** never run; Task 3 measures it before writing, and the
test ships with a monkeypatched map otherwise, saying so.

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the plan | `docs/superpowers/plans/2026-09-11-grid-donation.md` | § Measurement (M1–M3, the baseline), § Decisions A–E, Tasks 1–6 |
| the measurement script | `scripts/grid_donation_design_census.py`, committed with the plan | 5 structural pairs = the census's 5, all accepted; datagrid 4.9 s / 27 pages; line-0 identity 7/7 |
| the ruling the plan executes | `docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md` § 4 | grid donation as specified |
| decisions 1–4 | `docs/superpowers/2026-09-10-the-grid-the-author-drew-handoff.md` § 5a; `docs/superpowers/2026-09-11-the-donor-header-is-derived.md` § 1–4 | the plan's inputs |
| the oracle numbers | `docs/superpowers/2026-09-10-the-donated-reading-tiles-handoff.md` § 2 | 222 → 267, per-band entries |
| PR #198 | `gh pr view 198` | the evidence doc; its CI failed once on `test_cockpit.py::test_the_live_newest_handoff_declares_a_topic` (missing `**Topic:**`), fixed in-branch this session |

## 2. What was measured this session (all at `808aa7a`, corpus present)

- `derive_data_grid`: **4.9 s** over all 27 corpus pages; `page_bands`: 39.0 s. (M1)
- 7 bands corpus-wide own a `_rule_boundaries` vector; all 7 line-0s re-identify uniquely by ink. (M2)
- Structural candidate pairs with the tiling clause removed: **5**, all bfs p6, all accepted by
  `region_tiles` ∧ `cell_round_trips`; entries 36/54/36/72/63. (M3)
- bfs baseline: document 0.4033 (29.0 s), p6 0.9169, 276/25 tokens, 222 entries.

## 3. What was decided, and where that decision is recorded

- **DECISION A** (tiling is disposed, not derived), **B** (one page graph, per-band `initBindings`,
  seam at the assert leg `compile.py:967`), **C** (`tab:headLineRefusal` verbatim from the datagrid),
  **D** (the reading is built from the donor's own grid with rows shifted, NOT the spike's prepend),
  **E** (unique donor or nothing): the plan's § Decisions. **Nowhere else** — reversible until the
  plan ships.
- The `**Topic:**` line is a CI requirement on the newest dated handoff (`tests/test_cockpit.py:291`).
  Recorded here and in the fix commit on PR #198.

## 4. Unverified or assumed

- 5b and 5c above.
- Whether `tab:headerDonatedBy` on a `tab:RecordTable` node passes the document membrane under
  `validate_shapes=True` (Task 4's MEASURE).
- Whether rdflib's `initBindings` binds a variable used only inside `FILTER` (Task 2's MEASURE).
- Which existing corpus-gated pins move (Task 5 measures; none predicted).
- No suite run this session; the measurement script has no CI test.
- The working-token figure was not read from a status line; the plan was written at an estimated
  ~110K working tokens — over the 50K originating floor, which is why 5b/5c are graded rather than
  asserted.
