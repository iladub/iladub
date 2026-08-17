# The R97–R104 loop splits into three

**Date:** 2026-08-17 · **Tree:** `main` @ `42c2610` · **Decided by:** the maintainer, in
conversation, after an adversarial review of
`specs/2026-08-17-coverage-is-not-liveness-design.md`

**Status of that spec: SUPERSEDED IN SCOPE, not withdrawn.** Its measurements stand and its
§4.1 seam, §4.6 disclosure and §5 R101 findings are reused below. Its *design* — the coverage
ledger — moves to Loop 2, where it becomes an opening brief rather than a repair list.

## Why

The spec was written at 2.5× the originating floor and reviewed adversarially by two agents with
no inherited context. The design reviewer returned **16 findings, 6 blocking**, and its verdict
was *not fit to write a plan from*. Two findings are structural rather than corrigible:

- **D12** — an RDF ledger requires an owned namespace, a `vocab/ontology/` file, shapes, and
  CLAUDE.md's mandatory worked-example-plus-negative-test. None appears in the spec's §3, §10 or
  `Doc impact:` block. That is a vocabulary loop's worth of work hidden inside a bullet.
- **D15** — §10 is six steps across four unrelated mechanisms (an f-string, a membrane gate, a
  new vocabulary, a probe script, a contract edit, a pytest census) with exactly one stopping
  point offered.

The spec's own §5 already contained the right instrument — a planned loop boundary — drawn in
the wrong place. This decision redraws it.

**The full review is not reproduced here.** Findings are cited as D1–D16 and each is assigned to
the loop that owns it, below.

## The three loops

### Loop 1 — the gate and the label

**Ships a real defect fixed on real corpus input. This is the vertical slice.**

| carries | from |
| --- | --- |
| **R104** — carry the leg identity through `_validate`; a dec-leg refusal must not report as `tab:` | spec §4.6, oracle O4 |
| **R102** — ungate the `dec` leg from the tab-fact condition; measure the cost | spec §4.1, oracle O3 |
| **R89's adopted rule** → CLAUDE.md | maintainer decision, currently recorded only in a handoff |
| **register honesty** — D5's downgrade-or-carry pass | review D5 |
| **R103's mechanical half** — widen `scripts/probe_emitter_typing.py` to `tab-datagrid.ttl`, report the count | spec §4.5 — **independent measurement, not part of the slice** |

**Corrections this loop must apply to the spec's text before reusing it:**

- **D11 (factual error).** The spec says the 316 unvalidated holons are "the documents with *no*
  tab facts." **Wrong.** They are ons and bfs, which **do** open the page gate (M-B: ons
  page-calls=1, bfs page-calls=2); what they never open is the **document** gate, whose condition
  is `recognized or section_facts`. So ungating adds validation on **full merged document
  graphs — the largest in the system**, not on cheap fact-free ones, and it makes R57's membrane
  redundancy strictly larger. Rewrite the cost paragraph before planning.
- **The missing branch.** R102's row offers an alternative closing condition the spec declined.
  If any of the 316 *does* violate `dec:DecisionHolonShape`, ungating turns a green corpus red
  **inside a compile that raises `AssertionError`**. The spec plans for cost and not for this.
  It is the more likely disruption and it needs a stated response.
- **D7.** State the principle that makes R102's membrane-composition change in-scope while R99's
  is deferred — or stop calling the R99 deferral principled. R102's own row calls its fix "a
  membrane-composition question."
- **D16.** O1's falsification may *error* rather than *fail* — a task report must distinguish
  "guard failed" from "compile raised."

**What survives review untouched and should be reused verbatim:** the spec's §4.1 named seam
(*MEASURE which shape sets each gate actually guards at `compile.py:453-465`; the comment at
`:457-459` argues for the combined report and that argument must be answered, not bypassed*).
The reviewer checked it and confirmed the seam is real. Oracles **O3** and **O4** hold, including
O4's note to assert the *absence* of `tab`, not only the presence of `dec`.

### Loop 2 — the coverage ledger

**A vocabulary loop. Its design is an open brief, not a repair list.**

Carries **R97** (the two phase-reason shapes), **R98** (registry reason amendment), **R99**,
**R100**, and the ledger itself.

**Opening brief — the questions Loop 2 must answer, all from the review:**

- **D1 — what does the registry contain?** All-∅ rows make the flagship oracle inert: coverage
  cannot shrink below ∅. Either every wired shape carries a declared-coverage row — and the
  go-live arm then fails the build on every widening, a real cost to accept deliberately — or the
  oracle bites only on a named subset and the spec says which.
- **D3 — what does the ledger record?** Focus-node **counts** cannot support a union of holon
  **identities**. Decide, and reconcile with whatever continuity claim survives.
- **D4 — is the reason column falsifiable?** Today no. **Adopt the reviewer's O6:** compile the
  zero-ETL fixture, run `analyze()`, assert `tab:BaseFactShape` ≥ 1 focus node. It pins the phase
  reason and **runs in CI without the corpus**. The superseded spec's §7.1 was overstated — it
  conflated *"cannot detect phase-narrowing automatically"* with *"cannot pin the declared
  reason."* The second is measurable and M-A already demonstrated it.
- **D8 — the neurosymbolic gate, twice.** (a) The gate condition itself
  (`if validate_shapes and (any tab:RecordTable …)`) is the loop's largest decision and was left
  unclassified. (b) `focus_nodes` and `unreachable_terms` are derivations over an RDF evidence
  graph — **AXIOM** by principle 8's default — and were labelled raw extraction. Split the row or
  carry a justified exception.
- **D12** — namespace, `vocab/` locations, worked example, negative test, `Doc impact:`.
- **D9** — *"run"* is a load-bearing undefined term; the holon boundary depends on it.
- **D10** — I2 is over-broad (it forbids the corpus list the guard needs) and unoracled.
- **D13** — the go-live oracle's setup is not constructible: every registered-∅ row is one the
  design scoped out of reach. Falsify the disposal arm against a hand-written ledger graph, and
  admit it then pins SHACL rather than end-to-end wiring.
- **D6** — the superseded §4.3 promised coverage visible "on both membranes" while §7.9 excluded
  the grounding leg. Do not carry that promise forward.

### Loop 3 — what CI does not run

**R101's CI sibling — and the split's one substantive relocation.**

The triage proposed raising the review's **D2** as a standalone residue. **It is not standalone.**
D2's repo-level half — `corpus/` is gitignored (`.gitignore:44`), the vacuity fixture skips
without it (`test_vacuity_registry.py:298-317`), and CI never fetches it, so **the guard R87
shipped has never run in CI** — is the *same subject* as R101: a check that is wired, reported as
health, and covering nothing where it matters. It belongs in this loop, not before it.

That gives Loop 3 a sharper thesis than R101's row had: **the repo's own vacuity guard is an
instance of R101.** Whatever registry Loop 3 builds must have a row for it.

Carries **R101**, D2's repo half, and D16's note that a recorded test count (*"59 for
`test_datagrid.py`"*) **rots** — pin the **construct** (`importorskip` collapses,
`pytestmark` stays proportional), which is M-C's durable finding, not the number.

Prohibitions carried unchanged from R101's row: do **not** add `demo` to the CI install line; do
**not** resolve the CI-extras policy question.

## What this decision does NOT settle

- **Loop order beyond Loop 1 first.** Loops 2 and 3 are independent of each other.
- **D14** — whether "coverage, not liveness" survives as a thesis. The reviewer scored one row
  (R100) as genuinely closed by the instrument and called the reduction packaging. Loop 2 should
  answer it rather than inherit it; the disclosure obligation, at least, is accepted — R98, R99
  and R103 were owed the same candour the superseded §4.6 gave R104.
- **Tier 0 as a separate action.** Superseded by this decision; it is Loop 3's opening fact.
- **R61.** Still deferred by maintainer decision until R103's count exists (Loop 1).
- **The empirical review NEVER RAN.** A second reviewer was dispatched to check every `file:line`
  citation and every number; it **died on a transient API error (529) before producing any
  report**, having got as far as starting to reproduce M-A. There is nothing to recover — **it
  must be re-run from scratch.** This is not a nicety: D11 was a factual error found *incidentally*
  by the design reviewer, which is weak evidence that more of that class exist, and **every
  citation in this repo's specs is exactly what CLAUDE.md plan-rule 2 exists to protect.** Re-run
  it before planning Loop 1 — Loop 1 is the one whose citations it was checking.
- **The pySHACL leg.** Standing since R87, still unrun.

## Next concrete action

**Re-run the empirical review** (it never ran — see above), apply its findings to Loop 1's inputs,
then write Loop 1's spec in a fresh session. Loop 1 is small enough that its spec should be
short — a membrane gate, an error label, a contract paragraph and a register pass.

Its brief: verify every `file:line` citation and every number in
`specs/2026-08-17-coverage-is-not-liveness-design.md` against the code itself, treating the three
`2026-08-17-m-*` measurement documents as **under review rather than as authority** — they share
an author with the spec.
