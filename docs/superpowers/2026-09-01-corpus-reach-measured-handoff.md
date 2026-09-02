# Handoff — corpus reach is measured, R158's prediction is refuted, and the instrument is committed

**Topic:** `R158` — corpus REACH as a corpus property. Its falsifiable prediction was RUN, as the
predecessor handoff required. It is **refuted**: 6 of 16 changed functions are reached by <=3 of 7 documents, not most. The reach instrument the row asked for is built,
committed and unit-tested.

**Part 5 was written before parts 1–4, past the 50K originating floor** (this session's working
figure was not readable from the status line and is estimated at 60–70K; treated as over). Per
`CLAUDE.md` § "The handoff's next action is TYPED", part 5 is graded per action.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

**Run the instrument before making any "the other documents are unchanged" claim, and paste its
table into the loop's evidence.**

```
./.venv/bin/python scripts/reach_probe.py run    --out /tmp/reach          # ~20 min, once
./.venv/bin/python scripts/reach_probe.py report --out /tmp/reach  <fn>…   # instant, many times
```

This is mechanical because the answer is already known for the functions this loop measured, and
because the instrument prints the score beside the reach — which is exactly what `R158` asked for.
There is no judgement in running it.

### ASSERTED — the compiler fix this loop did not reach, and why it is still the right next loop

The maintainer chose *"reach probe → then fix"*. The probe ran; **the fix did not**, and that is
stated here rather than hidden: this session crossed the originating floor producing the
measurement, and the measurement changed which fix is defensible. The next loop is the fix.

**The target with measured reach is `apple`.** Its 0.3587 is the corpus's second-worst score, the
2026-08-20 escalation census attributes **10 of its 11 escalations to two defects** (a tiling
failure repeated on the two statement pages, and the `Three Months Ended … Nine Months Ended`
double header firing once per page), and the double header sits in
`matrix.infer_column_tree_by_proximity` — measured here at **apple 2 · who 3, and 0 on the other
five**. That is not a vacuous target: it is a narrow one, and now provably so.

### PROPOSED — the reading of the bimodality, which is a REFRAMING and must not be built on unrun

The distribution below is bimodal: **10 of 16 changed functions at 7/7, 3 at 0/7, only 3 in
between.** The tempting reading — *"the compiler has a spine every document walks and limbs the
corpus never touches, so risk is binary: a change is either corpus-wide or corpus-invisible"* — is
a story fitted to 16 points, by the session that measured them. It predicts something checkable:

> **Prediction: over ALL 318 executed functions the same bimodality holds — the modes at 1/7 and
> 7/7 dominate and the middle is thin.**
> Measured here: 122 at 7/7 and 114 at 1–2/7, against 8 at 4/7. **It is directionally consistent
> and it is NOT a test**, because the same run produced both the claim and its check.
> **If refuted** — if reach is smooth once measured against a larger function population, or once
> unit-test reach is included — then "spine vs limb" is a re-description of `compile_document`'s
> call tree and licenses nothing about risk.

**Do not adopt "grow the corpus" as the remedy for a 0/7 row.** `R146` and this row's own closure
text forbid inferring from absence: a function no document reaches may be a corpus gap OR an honest
statement that the change was narrow, and nothing measured here distinguishes them.

---

## 1. Goal

Answer `R158`'s own falsifiable prediction with a measurement rather than a reframing, and leave
behind an instrument a later loop can re-run instead of rewriting.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `scripts/reach_probe.py` | The instrument, its two legs, and the module docstring's statement of what a zero does and does not mean |
| `tests/test_reach_probe.py` | What is pinned, and the prototype defect the two-modules test exists for |
| `docs/superpowers/2026-09-01-corpus-reach-measured.md` | The measurement: the 16-function table, the corpus-wide distribution, the cost, and the § Unverified |
| `docs/superpowers/2026-09-01-candidate-a-refuted-handoff.md` | The predecessor. Its part 5 set this prediction and required it be run first |
| `residues.md` / `residues-closed.md` `~~R158~~` | The row and its closure evidence |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| `R158`'s prediction refuted — 6/16 changed functions reached by ≤3, not "most" | `2026-09-01-corpus-reach-measured.md`; `residues-closed.md` `~~R158~~` |
| `R158` closed on its stated condition (a committed instrument reporting reach beside score) | same |
| The bimodality is raised as an open question, not a conclusion | `R159`, and part 5 above — **nowhere else**, so it is reversible |
| The compiler fix was deferred to the next loop, target `apple`'s double header | **this file only.** Not a plan, not a spec; reversible |
| The instrument is PROCEDURAL under §8 | argued in `scripts/reach_probe.py`'s module docstring |

## 4. Unverified or assumed

- **Reach is measured for the corpus battery's two legs only** — `compile_document` and, on the two
  contracted documents, `ground_document`. Unit tests, the CLI and every other entry point are
  outside it. A 0/7 row is silent about them.
- **cProfile records a function only when CALLED**, so an absent entry cannot distinguish "imported
  but unused" from "never imported". The instrument says so in its docstring; no row here should be
  read as "dead code".
- **The 16 changed functions were extracted from `git diff -U0` hunk headers**, which name the
  *enclosing* def. A hunk touching only a comment counts the same as one changing behaviour —
  `R139`'s `_seal` row is exactly that case and is not a behavioural change.
- **The bimodality claim and its check came from the same run.** Graded PROPOSED above for that
  reason.
- **`run` was executed once.** Call counts are deterministic in principle and were not re-run to
  confirm it; the compile-leg counts reproduced a separate prototype run to the unit on every
  document, which is evidence but not a repeat.
- **No `src/` behaviour changed in this loop.** By the cost measurement's own finding it is another
  session that spends tokens without moving the compiler — recorded, not hidden. What it leaves is
  an instrument, which the two loops that needed one had to write from scratch.
