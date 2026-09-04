# Handoff — the eight are TWO findings, and R173's row is set-wrong

**Written 2026-09-04**, immediately after running the bisect that the previous handoff
(`docs/superpowers/2026-09-04-r173-handoff.md`) typed **ASSERTED**.

**Part 5 was written FIRST, at ~34,000 working tokens — under the 50K originating floor**
(CLAUDE.md § Loop & context hygiene; logged via `plimslop preflight`). It is still typed per
action, because the type is what the next session budgets against, not the cost of writing it.

---

## 1. Goal

Decide what to do about eight corpus-gated tests now that the bisect has run and shown they are
**two findings with two different origin commits**, not one — and about R173's own row, which the
bisect also falsified in one clause.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/2026-09-04-r173-bisect.md` | **The bisect itself** — the probe table, both origins, the method, and the two traps that make a naive re-run report green. This is the only place the measurement is written down. |
| `docs/superpowers/residues-open.md`, row **R173** | Re-shaped by this loop: now the seven apple tests + the CI-visibility half, with the bisect's correction to its own earlier claim recorded in place. |
| `docs/superpowers/residues-open.md`, row **R174** | The stem half, split out because it has a different origin commit and a different remedy. |
| `docs/superpowers/residues-open.md`, row **R160** | The `adopted (1,) → ()` consequence recorded by the 2026-09-02 loop. The bisect confirms it is the origin of seven of the eight. |
| `docs/superpowers/residues-open.md`, row **R172** | Owns whether apple p1's 56 asserted cells are the right reading. It is now load-bearing for one of the seven — see §5b. |
| `docs/superpowers/2026-09-04-r173-handoff.md` § 5 | The prediction this loop ran. 5a discharged; 5b **REFUTED**. |

## 3. What was decided, and where each decision is recorded

- **5b is refuted — the eight are two findings.** Measured, not argued. Recorded in the bisect
  document § 3–4, in R173's re-shaped row, and in R174's new row.
- **R173's "the one-band merge moves NEITHER" is false as stated.** The *count* is stable at 8/22
  either side of the R165 merge; the *membership* is not. Recorded in the bisect document § 5 and
  as a dated ✎ CORRECTION inside R173's own row. The original row is **not** deleted or rewritten
  — the correction sits beside the claim it corrects.
- **The stem half was SPLIT into R174 rather than left inside R173.** Recorded nowhere but this
  file and the two rows themselves. Two origin commits, two remedies; a single row would have had
  to carry two closure paths that share nothing. Reversible if a later session finds one cause.
- **Nothing about either remedy has been decided.** There is no spec and no plan for R173 or R174.
  That is recorded nowhere but here — which marks it reversible, not settled.

## 4. Unverified or assumed

- **Why stem's score ROSE at `20cc5b8` is NOT measured.** The bisect establishes *when*, not *why*.
  The bisect document § 4 offers a reading — that it is the same denominator effect the R154 loop
  itself ruled on for apple p0 (0.1170 → 0.1198, "not a reading improvement") — and types it
  **PROPOSED**. Nobody has counted stem's ink tokens either side of `20cc5b8`.
- **Why the R154 loop did not see the stem failure is UNKNOWN.** Its commit re-baselined three
  *non-corpus* pinned-score tests with explicit rulings and did not touch `test_corpus_stem.py`.
  Whether it ran the corpus tests at all and missed the result, or never ran them, is not recorded
  anywhere this session found.
- **Whether other corpus-gated tests fail is STILL unknown.** This loop ran three files, the same
  three R173 named. The full suite with a corpus present has not been run since the R165 loop.
- **The CI reporting remedy is still unpriced** — unchanged from the previous handoff. Nobody has
  looked at whether `pytest` can fail-or-warn on an unexpectedly-skipped marker.
- **`p1.score == 1.0` at HEAD is measured; whether it is CORRECT is not.** See §5b.

## 5. The next concrete action

Two actions, typed separately. Unlike the previous handoff, they are **independent** — neither
gates the other, and a session may take either.

### 5a. ASSERTED — re-baseline the seven, each with what its new number MEANS

The origin is `4cfee38` and the mechanism is R160's `adopted (1,) → ()`. Six of the seven fail
because they index a page the document no longer adopts; the seventh
(`test_corpus_apple_furnishes_the_measured_ten`) asserts `rep.adopted == (1,)` directly.

This is **asserted**: the origin is measured to a single commit whose parent is measured green,
the mechanism is already written down in R160, and doing the re-baselining *is* the work.

**The previous handoff's warning still binds, and now has a named exception.** Do not weaken an
assertion to make a test green. `test_the_admission_verdict_names_its_agent` and
`test_no_superseded_band_keeps_its_escalation_candidate` are adoption *epistemics* tests: a page
that no longer adopts needs a fixture that still adopts, or an explicit deletion with a recorded
reason.

**The exception is `test_an_adopted_page_never_scores_one_by_construction`, and it is NOT a
re-baseline.** It fails at HEAD only — it passed at `4cfee38` and at the R165 branch base — because
apple p1 now reads `score=1.0, asserted=56, escalated=0`. That test exists to refuse exactly a page
that scores 1.0, and it is now firing on a page that reached 1.0 *without* adopting anything. **Do
not re-baseline it. It is a signal, and it belongs to [[R172]]** — which already records that
nobody has ever content-diffed the merged band's 124 entries against the 48 cells asserted before.
If 56 asserted cells is the wrong reading of apple p1, this test found it.

### 5b. PROPOSED — stem's rise at `20cc5b8` is a denominator effect, not a reading gain

**The prediction:** `test_stem_document_is_byte_identical_under_adoption`'s
`0.9654553611484971 → 0.9658886894075404` is the same effect the R154 loop ruled on in
`tests/etkl/test_decisionlog.py` for apple p0 — welding two ink fragments into one cell removes a
token from the denominator, so the score rises without a single additional cell being read. If so,
the remedy is a re-baseline carrying R154's own ruling verbatim, and the closure is cheap.

**Why it is PROPOSED and not asserted:** it is an analogy between two documents, not a measurement
of stem. The R154 change (`geometry.py` +53, `gridregion.py`) is a general boundary change; stem is
a different document with a different failure profile, and a rise of 4.3e-4 is small enough to be
consistent with several mechanisms. **Count stem's ink tokens and cells either side of `20cc5b8`
before writing anything.** If the denominator is unchanged, this is a reading change and the number
must not be moved — the test's own docstring says so: *"If this number moves, STOP and report it —
never lower it."*

**If 5b is refuted, do not improvise.** Record it in R174 and let a fresh session take it.

### What NOT to do

- **Do not re-run the bisect to "confirm" it.** Each probe costs 4–6 minutes and the origins are
  single-commit-precise with measured-green parents. Read the bisect document's § 1 instead — its
  two traps are the reason a casual re-run reports green and proves nothing.
- **Do not fold the CI-visibility half into either.** It is R173's larger half and is still
  unpriced; both 5a and 5b are repairs to the tests themselves.
