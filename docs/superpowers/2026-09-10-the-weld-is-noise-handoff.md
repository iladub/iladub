# Handoff — the weld is noise: R208's fused rows are `gap < lead` decided at the fifth decimal

**Topic:** [[R208]]'s located cause. The predecessor's PROPOSED action 5a
(`docs/superpowers/2026-09-10-r207-marker-grounds-by-scheme-handoff.md`) sent this loop to find
the row weld on graincorp-stem p1 in the row-header derivation. It is not there. Branch
`r208-the-weld-is-noise`, off `cada16a` (the R207 branch, PR #193, still in CI when this was
written — rebase onto `main` once #193 squashes). Part 5 was written first, at ~70K working
tokens — over the originating floor, so each action is graded on its own line.

**Doc impact: none.** No wiki page states the wrap-continuation rule (`grep -rn "group_wrapped\|
gap < lead" docs/wiki/` is empty); the B3 spec that does is Evidence and append-only, so its
refuted claim is corrected in the register and here, not in place.

---

## 5. The next concrete action

### 5a. PROPOSED — replace `gap < lead` at equality with a derivation, in a spec, in a fresh session

R208 does **not** close here: the fix is B3's own deferred refinement
(`docs/superpowers/specs/2026-07-22-b3-wrap-continuation-procedural-design.md` § 3, *"a
distribution-aware bimodal split … deferred … only if a real jittery document demonstrates the
need"*), and graincorp-stem is that document. The design is a spec, not a patch: any constant on
the comparison is the tuned tolerance CLAUDE.md § 8 forbids, and the spike below shipped one on
purpose to measure the blast radius, not to be kept.

**The prediction to run first, before designing anything:** the *tightest certain row boundary*
derivation refuses all seven graincorp candidates and passes the four B3 pins. A pair of
consecutive body lines where line j tiles **as many** columns as line j-1 fails condition 3 and is
therefore a row boundary by construction; take `pitch_min` = the minimum gap over those pairs, and
let a candidate continue only if `gap < pitch_min`. On graincorp p1 band 1 the certain pairs
(Gladstone 7→8→9, Portland 20→21→22, …) span the whole noise interval, so `pitch_min` ≈ 6.479965
and every candidate (≥ 6.479988) is refused; on the B3 fixtures the certain pairs are at exactly 20,
so 5 and 19 merge and 20 does not. **Falsified in one run** of
`scripts/at_pitch_weld_probe.py` extended to print `pitch_min` if any candidate gap is below it.
**Its known cost, stated before it is measured:** a minimum is not jitter-robust where a median
is — one tight full-row pair in a jittery document refuses every genuine wrap just under it. No
corpus document is on record with that shape; that absence is not evidence of absence. The other
two derivations worth naming in the spec: the precision the *source* states (the decimal places of
the PDF's own text-matrix numbers, parsed rather than assumed), and the distribution split B3
named. Whatever ships must reproduce the spike's figures (§ 2) **without** the spike's constant:
six corpus hashes unchanged, graincorp-stem p1 77 leaf rows / p2 68, repeated-token cells 0,
`placement_population.py` exact-refused 24. And it must remove the strict xfail marker on the
detector (§ 1), which will fail the suite the moment the rule stops depending on noise.

### 5b. ASSERTED, and the maintainer's — the GLiNER2 spec branch still needs a disposition

Carried verbatim from the predecessor's 5b: branch `only-a-refusal-admits-the-model` is refuted
before T1 (R206) and unpushed. Push as a refuted record, or drop; nothing depends on it.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the weld | `src/iladub/etkl/cells.py`, `group_wrapped`, the `while` gate `gap < lead` | the strict `<` against a median that EQUALS the pitch; the docstring's own "HONEST LIMIT" names the suppressed-key case |
| the probe | `scripts/at_pitch_weld_probe.py` | the seven candidates on graincorp p1 band 1 with `gap - lead` printed at full precision; 3 weld, 4 do not |
| the detector | `tests/etkl/test_wrap_continuation.py::test_at_pitch_partial_line_under_coordinate_noise_is_still_not_merged` | strict xfail; the same intended reading as `test_at_pitch_partial_line_not_merged` with 1e-5 of noise on the coordinates |
| the intent pin | same file, `test_at_pitch_partial_line_not_merged` | "gap == lead -> strict `<` excludes it" — the reading the shipped code violates on real input |
| the B3 spec | `docs/superpowers/specs/2026-07-22-b3-wrap-continuation-procedural-design.md` § 3 | the deferred refinement and its trigger; the backstop claim this loop refutes |
| the register | `docs/superpowers/residues-open.md` R208, `residues.md` index | the amended cause and what closes it |
| the spike | not committed; a one-line patch (`round(gap, 2) < round(lead, 2)`) in a throwaway worktree, its outputs transcribed in § 2 | re-run from the description: `scripts/corpus_verdict_snapshot.py` on both trees, then `scripts/placement_population.py` on the patched one |

## 2. What was measured (2026-09-10, on `cada16a`)

**Where the weld is.** `page_bands(pdf, 1)[1]` holds the three Oct-26 Mackay lines as three
`Line`s (tops 71.31 / 77.79 / 84.27); `group_wrapped` returns them as ONE row whose cells read
`Mackay Mackay Mackay`, `59845 60954 59846`, `Wheat Chickpeas Chickpeas`, `10,000 15,000 15,000`.
That is upstream of `logical_rows`, `infer_row_header_tree` and every emitter, so the 5a
mechanism — a repeated row-header value read as a spanning cell — is refuted: no row header has
been derived yet when the lines are already one row.

**Why.** The band's gaps and the seven candidates, from the probe:

| | value |
| --- | --- |
| body row pitch | 6.48 pt, uniform (77 of 79 gaps; the two header gaps are 6.60, 7.32) |
| `lead` (median gap) | 6.480010499999935 |
| candidate lines (subset, fewer columns, no hrule) | 7 — every one a data row whose month column is blank: 15 or 16 of 17 columns |
| their `gap - lead` | −1.05e-05, −2.25e-05, +0.00e+00, −2.25e-05, +7.50e-07, +7.50e-07, +7.50e-07 |
| welded by `gap < lead` | **3** (lines 3→4, 25→26, 50→51); line 4→5 then chains onto 3 |
| hrules between data rows inside a port group | **none** — the author rules only the total rows, so the hrule veto is inert exactly where it is needed |

The noise is in the PDF, not in Python: word tops read `71.31424202250003`, `77.79424202250004`,
`84.27424127249998` — text-matrix positions with per-line jitter of order 1e-5 pt. The at-pitch
pin passes only because its fixture is integer-exact.

**Blast radius of refusing at-pitch continuations** (spike, disclosed constant, two readings of
`scripts/corpus_verdict_snapshot.py`):

| document | base sha / triples | spike sha / triples |
| --- | --- | --- |
| cbh-stem, graincorp-capacity, apple, bfs, ons, who | identical | identical |
| graincorp-stem | `737cf651cd9c` / 30909 | `19ef4cf500b0` / 32359 |

graincorp-stem under the spike: p0 57 leaf rows / 586 cells (unchanged), p1 73→**77** / 765→825,
p2 65→**68** / 696→741; `cellText` values whose first and last token repeat 56→**0**; score
0.9659 unchanged (it counts ink, and no ink moved). `scripts/placement_population.py`: records
140, novel 1262, exact-grounded 644, exact-refused **24** (was 48) — the 24 that remain are the
18 scheme gaps and the 6 subtotal rows R208's row already lists; the 22 joined-row values and
the 2 beyond its top-20 print are gone. The snapshot's per-region `cells` field did not move
(825 both sides — it counts words, not EntryCells); only the graph hash and triple count saw the
change.

**Detector falsified.** On the spiked tree the new test passes and its `strict=True` marker fails
(`1 failed, 4 passed`); on the shipped tree it xfails (`4 passed, 1 xfailed`).

## 3. What was decided, and where that decision is recorded

- **The spike constant does not ship.** `round(·, 2)` is a tuned tolerance; recorded in this
  file and in the register row. The fix is a spec (5a).
- **The finding is filed under R208, not a new row.** The B3 backstop claim's refutation is
  recorded in R208's row and here — nowhere else, since the spec is append-only Evidence.
- **The detector is a strict xfail, not a red test**: branch protection needs green CI, and
  strict makes the fix loop remove the marker. Recorded in the test's `reason`.
- **The probe is committed** (`scripts/at_pitch_weld_probe.py`), as the earlier spikes were, so
  5a's falsification is one command.

## 4. Unverified or assumed

- **5a's `pitch_min` derivation is reasoned from the probe's printout, not run.** The
  "≈ 6.479965" is the smallest gap in the band's distinct-gap list, assumed to lie on a
  certain-boundary pair; the probe does not yet print which pairs are certain.
- **The Nov-26 chain**: line 26 welds onto 25 but 27 does not weld onto the fused 25 — read as
  "27's gap to 26 is over the median" from the table; not printed pair by pair for the chained case.
- **The 1450-triple delta** is assumed to be the 7 extra leaf rows and their cells plus the
  row-header nodes over them; not decomposed.
- **Whether any other corpus document has at-pitch partial lines that the noise currently
  refuses** (the mirror error: a genuine wrap at the pitch left un-merged) — six identical hashes
  say the spike changed nothing there, which covers only the direction the spike moves.
- The full suite was not run (~61 min, [[R181]]'s figure); run in-session:
  `tests/etkl/test_wrap_continuation.py` (4 passed, 1 xfailed), `test_row_defusion.py`,
  `test_cells.py`, `test_rowrole_reading.py` (27 passed on the spiked tree before the detector
  was added), and the doc lints named in the PR body.
