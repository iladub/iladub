# Handoff — the tightest certain boundary: R208's spec is written, its prediction ran, its rival refuted

**Topic:** [[R208]]'s fix, specified. The predecessor's PROPOSED 5a
(`docs/superpowers/2026-09-10-the-weld-is-noise-handoff.md`) sent this loop to run the `pitch_min`
prediction before designing, then write a spec. Both done. Branch `r208-the-tightest-certain-boundary`,
off `d8041d8` (PR #194, still open — rebase onto `main` once #194 squashes). Part 5 written first, at
~55K working tokens, just over the originating floor; each action graded on its own line.

**Doc impact: none.** Same grounds as the spec's block.

---

## 5. The next concrete action

### 5a. ASSERTED — implement the spec's § 5 contract, in a fresh session, with no separate plan

`docs/superpowers/specs/2026-09-10-the-tightest-certain-boundary-design.md` § 5 names the one
function, the probe, three tests and four oracles; the outcome is known because every figure the
oracles demand was already produced this session by the extended probe (spec § 7) and by the
predecessor's spike (O2/O3). The change is a derived threshold and a fallback in `group_wrapped`,
with the strict `xfail` removed from the detector. A plan would restate § 5. **Graded ASSERTED** on
the mechanism; the one place it could still surprise is O2 — `corpus_verdict_snapshot.py` on the
implemented tree, where a hash other than graincorp-stem's moving would refute § 4(a)'s "0 of 30"
and send the loop back to the spec. Run O2 before O1.

### 5b. ASSERTED, and the maintainer's — the GLiNER2 spec branch still needs a disposition

Carried verbatim from two predecessors: branch `only-a-refusal-admits-the-model` is refuted before
T1 (R206) and unpushed. Push as a refuted record, or drop; nothing depends on it.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the spec | `docs/superpowers/specs/2026-09-10-the-tightest-certain-boundary-design.md` | the rule (§ 3), the fallback decision, the two limits (§ 4), the contract (§ 5), the corpus run (§ 7) |
| the weld | `src/iladub/etkl/cells.py`, `group_wrapped` | unchanged this loop; the `while` gate is `gap < lead` |
| the prediction's instrument | not committed — the probe extended to enumerate certain pairs, its full output transcribed in spec § 7; 5a commits the extension into `scripts/at_pitch_weld_probe.py` | re-run from the spec's description |
| the source-precision refutation | spec § 2; the raw `Tm` operands were read with `pdfminer` off the page's content stream | six decimals stated, jitter in the sixth |
| the register | `docs/superpowers/residues-open.md` R208, `residues.md` index | the appended SPEC note pointing here |
| the predecessor | `docs/superpowers/2026-09-10-the-weld-is-noise-handoff.md` | the located cause, the spike's figures (its § 2) that 5a must reproduce |

## 2. What was measured (2026-09-10, on `d8041d8`)

- The `pitch_min` prediction **held**: 13 of 13 graincorp at-pitch candidates refused (p0 2, p1 7,
  p2 6), the four B3 pins unchanged, the strict-xfail detector passes. Whole-corpus candidate
  population: 30 in 4 documents; `gap < lead` welds 8 (6 wrong, 2 genuine); the new rule welds the
  2 genuine ones and 0 of the 6.
- The "round to the source's stated precision" derivation is **refuted**: graincorp's `Tm` ty
  operands are stated to 6 decimals (`90.879997`, `82.080002`, `73.279999`) and the at-pitch
  disagreements are ~2e-5 pt, above that resolution.
- 3 corpus bands have no certain pair (bfs p0 b0, p6 b1, p6 b2); the fallback to `lead` leaves them
  byte-identical.
- 0 of 30 candidates lie in the interval `[tightest_row_gap, lead)` where the new rule refuses a wrap
  the old one accepted.

## 3. What was decided, and where that decision is recorded

- **The rule is the minimum over certain pairs, strict `<`, fallback to `lead` when the band
  certifies nothing.** Recorded in the spec § 3; nowhere else yet — reversible until 5a ships.
- **The refuse-when-nothing-certified arm is named and not run.** Spec § 3 and § 6.
- **The § 8 class stays PROCEDURAL, inherited from B3's argument.** Spec § 3.
- **No separate plan.** This file, 5a — nowhere else, so it is a judgment the implementer may reverse
  if § 5 turns out to underspecify anything.

## 4. Unverified or assumed

- **O2 and O3 are predicted, not run, on a tree implementing the rule.** The spike's figures are
  assumed to transfer because the spike and the rule refuse the same 13 candidates and nothing else on
  the corpus (the § 7 table); the spike's `round(·, 2)` could in principle have moved a non-candidate
  comparison the rule does not touch. O2 decides it.
- **The "1 in `n_certain + 1`" residual** (spec § 4(b)) assumes exchangeable noise across a band's
  gaps; the graincorp noise is float32 round-off of a 2-decimal grid, which is deterministic per
  value, not iid. The figure is an order of magnitude, not a probability.
- **The chained-anchor case** is assumed to inherit the threshold harmlessly; not separately measured.
- The full suite was not run (~61 min); nothing in `src/` changed this loop. Run: the doc lints
  named below.
