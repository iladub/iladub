# Handoff — R208 closed: the tightest certain boundary is implemented, its four oracles run

**Topic:** [[R208]]'s fix, shipped from the spec
(`docs/superpowers/specs/2026-09-10-the-tightest-certain-boundary-design.md`) with no separate plan,
as the predecessor's 5a asserted (`docs/superpowers/2026-09-10-the-tightest-certain-boundary-handoff.md`).
Branch `r208-the-boundary-implemented`, off `f905445` (PR #195, the spec, still open — this branch
is stacked on it; rebase onto `main` once #195 squashes). Part 5 written at ~60K working tokens,
under the executing floor; each action graded on its own line.

**Doc impact: none.** Same grounds as the spec's block: no published term changes, no wiki or site
page states the wrap-continuation rule.

---

## 5. The next concrete action

### 5a. ASSERTED, and the maintainer's — merge #195, then this PR; R208 closes on the merge

Spec § 6: R208 closes when O1-O4 are green on a merged branch. All four are green on this branch
(§ 2 below); the register row is struck in this PR on that evidence, and the merge is the last
step. Nothing to design.

### 5b. PROPOSED — the next subject is deliberately unnamed; read `residues.md` and pick

O2 moved exactly the one hash the spec predicted and no other, so this loop surfaced no successor
defect, and the spec's § 6 leaves two items that are decisions, not measurements: the
refuse-when-nothing-certified arm (named, costed at one bfs header wrap, not run) and the
chained-anchor case (inherits the threshold, not separately pinned). Neither is a defect on record.
The one *measurement* worth a fresh session is § 4(b)'s residual: no corpus document exercises it,
and the only way to falsify the "1 in `n_certain + 1`" order of magnitude is a generator that writes
float32 round-off around a uniform grid — a synthetic PDF, which this repo has so far refused to build
as evidence (`no-overfitting`). PROPOSED because a session that runs the register instead may find
a real document first.

### 5c. ASSERTED, and the maintainer's — the GLiNER2 spec branch still needs a disposition

Carried verbatim from three predecessors: branch `only-a-refusal-admits-the-model` is refuted before
T1 (R206) and unpushed. Push as a refuted record, or drop; nothing depends on it.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the rule | `src/iladub/etkl/cells.py`, `group_wrapped` — the certain-pair enumeration before the loop, the `while` gate on `tightest_row_gap`, the docstring's § 8 paragraph | strict `<`; hrule veto counts as certification; fallback to `lead` when the certain set is empty |
| the tests | `tests/etkl/test_wrap_continuation.py` — the detector (xfail removed), T1 fallback, T2 hrule certifies, T3 the disclosed cost, the four B3 pins | the falsification block in § 2: with the gate reverted, exactly the detector + T2 + T3 fail |
| the probe | `scripts/at_pitch_weld_probe.py` — now prints certain-pair count, `tightest_row_gap`, both verdicts | O1 in one command |
| O2's two readings | scratchpad only (not committed): `corpus_verdict_snapshot.py` at `f905445` and at this branch's HEAD; the hashes are transcribed in § 2 | re-run from the script's docstring |
| the spec | `docs/superpowers/specs/2026-09-10-the-tightest-certain-boundary-design.md` | § 3 the rule, § 4 the two limits, § 5 the contract this loop executed, § 7 the corpus table |
| the register | `docs/superpowers/residues.md` R208 (struck), `residues-closed.md` (the full row, moved) | the closure evidence |

## 2. What was measured (2026-09-10, this branch versus `f905445`)

- **RED before GREEN.** With the xfail removed and T1-T3 added, on the unmodified gate: the detector,
  T2 and T3 fail (`4 == 5`, `5 == 6`, and the detector's `5`); T1 and the four B3 pins pass. After
  the implementation: 8 of 8 pass.
- **O4 falsification, run:** gate reverted to `gap < lead` in place, everything else kept —
  `3 failed, 5 passed`, the three being the detector, T2, T3; restored — `8 passed`.
- **O1:** graincorp-stem p1 band 1 — 80 lines, 72 certain pairs, `tightest_row_gap = 6.479964750000022`,
  `lead = 6.480010499999935`; 7 candidates, welded by `gap < lead` **3**, by the new rule **0**. The
  candidate closest to the threshold sits 2.32e-5 pt above it (line 25→26).
- **O2:** six hashes unchanged (apple, bfs, cbh, graincorp-capacity, ons, who); graincorp-stem `737cf651cd9c` / 30909 → **`19ef4cf500b0` / 32359 — the spike's own hash** from the predecessor's § 2 table, so the derived rule and the disclosed-constant spike produce the same graph triple for triple. `tab:LeafRow` per page 57 / **77** / **68** (from 57 / 73 / 65). Score 0.9659 unchanged. `group_wrapped` welds nothing on the three bands (61/80/71 lines → 61/80/71 rows).
- **O3:** graincorp-stem exact-refused 48 → **24**: `Woodchip` 6, `SHUTDOWN` 6, `Cement` 4, `Peas` 1, `COMMENCED` 1 (the 18 scheme gaps) + the 6 `… Total` subtotal rows — no joined value remains. `cellText` values whose first and last token repeat: **0** of 2209 (from 56). cbh unchanged (49 marker-grounded, 1 refused).
- **Unit tests touching `group_wrapped` or pinning graincorp-stem** (`test_cells`, `test_rowrole_reading`,
  `test_row_defusion`, `test_corpus_stem`, `test_grounding`): **52 passed** in 5:54.
- The full suite (~61 min) was not run in-session; CI on the PR is the run of record.

## 3. What was decided, and where that decision is recorded

- **The rule, its strict `<`, the fallback to `lead`, and the PROCEDURAL class** — all taken by the
  spec (§ 3), executed here without variation. Recorded in the spec and now in the `group_wrapped`
  docstring.
- **T2 uses a 5-column grid** (`GRID5`), not the B3 fixtures' 3-column one — nowhere but this file
  and the test's own comment. With 3 columns a band whose *only* certain pair is vetoed cannot also
  hold a candidate between that gap and the median (two gaps, the median is their mean, so the
  candidate would have to be tighter than the vetoed gap). Five columns give four strict-subset steps
  and a median the vetoed gap sits under. The spec's T2 is satisfiable; it just needs the room.
- **T1 passes before the implementation, by design** — the spec says "byte-identical to the B3
  rule". It pins the fallback ARM against the refuse-when-nothing-certified arm (3 rows), not the
  fix. Recorded here and in the test's comment.
- **The certain-pair enumeration counts an empty line (no words) as certain** — it fails the
  structural test's `bool(cur)`, exactly as the loop would `break` on it. Not a case any fixture or
  corpus band exhibits; recorded nowhere else.

## 4. Unverified or assumed

- **O2's baseline reading was taken from a process that imported `cells.py` before this loop's
  first edit** (process start 13:43:04, first edit 13:45:23 local) and confirmed by its graincorp
  hash matching the predecessor's base column (`737cf651cd9c` / 30909). Not re-run on a clean
  worktree.
- **The chained-anchor case** inherits the threshold without a pin (spec § 6).
- **The § 4(b) residual** is stated in the docstring and not closed; 5b names the only measurement
  that could bound it.
- The full suite was not run here.
