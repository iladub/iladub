# Handoff: R303 execution, a refusal is furnished for escalation (2026-10-09)

**Serves:** maintenance. This is [[R303]], executing spec
`docs/superpowers/specs/2026-10-09-r303-a-refusal-is-furnished-design.md` (PR #327) without a plan.

**Topic:** compile · **Date:** 2026-10-09

Written at ~59K working tokens, 1.2× the 50K originating floor (override logged). Parts 1–4 are
pointers. Part 5 is graded per action, as CLAUDE.md § "The handoff's next action is TYPED" requires.

## 5. The next concrete actions, each one typed

1. **ASSERTED.** Cut a branch (or a worktree, whose traps are in part 4) from `main` once PR #327 has
   merged. Write O1 and O2 from spec § 5 first, and watch both **fail** on `main`. O2 is in
   `tests/etkl/test_ruleguard.py` on `_minted_page`. O1 is in `tests/test_r301_fed_h41.py`. The
   outcome is known, because spec § 1 M1 measured 0 requests on both regions, so this is the work
   and not a prediction.
2. **ASSERTED.** Make the spec § 2 change in `vocab/queries/escalation-furnish.rq`:
   `VALUES ?label { "escalated" "refuse" }` and `?o rdfs:label ?label` replace the literal, and the
   header comment names both labels and cites R301 § 8 S3. M5 prototyped exactly this on the real
   graph (12 → 14, idempotent, shapes conform). Then run O3: remove `"refuse"`, show O1 and O2 fail,
   restore it.
3. **PROPOSED (graded: high confidence, cheap to refute).** O4 says the other ten documents are
   unchanged and `test_escalation_furnish.py` passes **unmodified** (O5). The prediction rests on a
   grep (only `ruleguard.mint_refusal` chooses `"refuse"`) and on R301's O4 (the guard fires on
   fed-h41 only). It has not been run. A refutation means some document carries a refusal nobody
   enumerated. Stop and report that; do not adjust the pins to fit. Run it serially: a before/after
   `scripts/corpus_verdict_snapshot.py --pdf` per document, then `pytest -m corpus` on
   `tests/etkl/test_escalation_furnish.py`.
4. **ASSERTED.** Close R303. Strike the row's number and append the closure evidence in place in
   `docs/superpowers/residues-open.md`. Evidence files are append-only, so add text and never edit
   existing text. Then strike the index line in `residues.md`. The close condition is in the row: an
   `increment` loop, plus a fed-h41 pin that both regions are furnished. The `Doc impact: increment`
   is declared by the spec, so check whether `scripts/release_gate.py` or the drain register
   expects an entry for it.

## 1. Goal

A region the producer guard withdraws reaches a human through a `dec:ExpansionRequest`, like every
other escalated band, without relabelling the refusal's option.

## 2. Where the primaries are

- **The spec**, `docs/superpowers/specs/2026-10-09-r303-a-refusal-is-furnished-design.md`. § 1 has
  the measurements M1–M5, § 2 the one change and its invariants, § 5 the oracles O1–O6, § 6 the
  unverified items.
- **The row**, R303 in `docs/superpowers/residues-open.md`, with its close condition.
- **The query**, `vocab/queries/escalation-furnish.rq`. The label line is `?o rdfs:label "escalated"`.
  Find it by grep, not by line number.
- **The refusal's shape**, `src/iladub/etkl/ruleguard.py` `mint_refusal`.
- **The tests**: `tests/test_r301_fed_h41.py` (O1, corpus-gated),
  `tests/etkl/test_ruleguard.py` (O2, runs in CI), and `tests/etkl/test_escalation_furnish.py` and
  `test_escalation_wiring.py` (O5, which must stay unmodified).

## 3. What was decided, and where it is recorded

- **The design**, approved by the maintainer in chat on 2026-10-09. It is recorded as a comment on
  PR #327 and in the spec.
- **Executing without a plan**, approved by the maintainer in the same chat and recorded in the same
  PR comment (spec § 8, on the R208 precedent).
- **Arm (b) and the `CandidateConcept` conjunct are rejected.** The measurements are in spec § 4.

## 4. Unverified or assumed

- O4's blast radius: part 5 action 3.
- Spec § 6's three items. Whether `_census` in `test_escalation_furnish.py` should also count
  refusals: measure it and report, it is not ruled. Whether the vacuity registry's per-document
  binding counts move: predicted not, because fed-h41 is held-out. Whether
  `docs/wiki/concepts/neurosymbolic-exemplars.md` cites the evidence label.
- Whether PR #327 had merged when this was written. It was queued with `--auto`, waiting on `test`.
  Check with `gh pr view 327 --json state`.
- **Worktree traps** (memory `r301-execution-in-progress`, not re-measured). Symlink `corpus`,
  `held-out` **and** `baml_client`; a missing `baml_client` silently skips suite chunks. Use
  `PYTHONPATH=src`, because the editable install points at the main checkout. Corpus compiles are
  serial, and fed-h41 alone took 218 s in this session.
- **CI skips the corpus.** A green `test` check is no evidence for O1 or O4, so run them locally.
