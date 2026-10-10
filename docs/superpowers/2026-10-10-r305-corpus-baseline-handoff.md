# Handoff: R305, a committed corpus baseline (2026-10-10)

**Serves:** maintenance — R305 was picked by the maintainer on 2026-10-10 from
`2026-10-10-r300-closed-handoff.md` § 5.1.

**Topic:** test infrastructure · **Date:** 2026-10-10

Part 5 was written first, before execution, under the 50K originating floor. It was revised once
O1 had run, at about 80K working tokens, under the 150K executing floor.

## 5. The next concrete action, typed

1. **ASSERTED, for every loop from now on: a PR that changes `src/`, `vocab/`, `readings/`,
   `pyproject.toml` or the two snapshot scripts must carry a regenerated baseline, or CI's `test`
   job fails.** Run `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate` (one
   serial pass, about 24 min, unattended) after the last input edit. `git add` new input files
   first, or it refuses. `git diff -- tests/corpus-baseline/` is the blast radius. Never run
   a "before" pass on `main` again: the committed files are the before.
2. **PROPOSED: no subject is chosen.** The candidates from the R300 handoff remain: R299, R295, R304
   and R83. The maintainer picks.

## 1. Goal

Make a blast-radius check one corpus pass plus a `git diff`, never a re-measurement of `main` (R305).

## 2. Where the primaries are

- The spec: `docs/superpowers/specs/2026-10-10-r305-corpus-baseline-design.md`. § 1 holds this
  session's measurements, and § 5 the oracles.
- The code: `scripts/corpus_baseline.py` (`regenerate`, `check`, `verify`) and
  `tests/test_corpus_baseline.py` (the gate, plus the completeness and fingerprint-sensitivity tests).
- The baseline: `tests/corpus-baseline/`, first generated at `650bad1`'s inputs.
- The closure evidence: `docs/superpowers/residues-closed.md`, R305.

## 2a. Results

- **O1, reproducibility: held.** The first `regenerate` ran 10:19:04 to 10:42:43. `verify`, a second
  full pass, ran 10:43:04 to 11:06:51 and reported 12 of 12 files byte-equal, `inputs.json` included.
- **O2, the gate fires.** One character added to `src/iladub/etkl/boxhead.py`'s module docstring
  turned `test_the_baseline_was_regenerated_from_this_tree` red, and `check` exited 1. Both went
  green on restore.
- **O3, fingerprint sensitivity.** With `readings` dropped from `INPUTS`, the fixture test failed on
  `readings/boxhead/r.json`. It passed on restore.
- **O4, refusals before writes.** An untracked `src/` file, `BAML_LIVE=1`, and a renamed held-out
  PDF each made `regenerate` exit 2 with `tests/corpus-baseline/` never created.
- **Completeness.** Removing one baseline file failed `test_the_baseline_holds_exactly_the_listed_documents`.
- **Scores match the record.** Every score and triple count in the baseline matches `main`'s
  readings as recorded in `2026-10-08-r301-o4-o5-record.md` where that file lists them (caltrain
  0.0 with 415 triples is `main`'s reading since R301, not an artefact of this harness).
- **No document text in the baseline.** All 30 `notes` across the eleven files are three
  adoption-refusal messages from the compiler.
- `test_residue_graph`'s candidate pin: 97 → 96, REMOVED = [305], measured on both trees.

## 3. What was decided, and where it is recorded

- **The CI gate is blocking** (maintainer, 2026-10-10, this session). Recorded in spec § 2, here,
  and in R305's closure. It is not in CLAUDE.md (spec § 7). Whether it belongs there is the
  maintainer's call.
- **One subprocess per document**, so a document's bytes cannot depend on the documents before it.
  This loop's call, in spec § 4. Reversible.

## 4. Unverified, assumed, or found on the way

See spec § 6: the other three readers' offline path was not read, dependency versions are recorded
but not gated, and two concurrent input-touching PRs can leave `main` stale until its next CI run.
