# Handoff — the census is run; R139 is now a decision, and it is the maintainer's

**Topic:** what the R139 census settled, the one live defect it found, and the fork it deliberately
did not resolve

**This handoff supersedes nothing.** It follows `docs/superpowers/2026-08-31-four-mechanical-rows-handoff.md`,
whose part 5 proposed the census and ordered it RUN first. It was, and it refuted — so that handoff's
proposal is **discharged**, not still pending.

Authored at **~125,000 working tokens — 2.5× the 50,000 originating floor**, `originating` logged as
`stop`. Part 5 is written first and is deliberately a **fork statement, not a plan**: the decision it
names belongs to the maintainer, and pre-resolving it at 2.5× the floor is exactly what the floor
exists to prevent.

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, whichever way the fork below goes

Nothing is queued. Both prior menus are empty: the 2026-08-30 table is closed out (PR #139) and the
2026-08-31 census proposal is discharged (PR #140).

### THE FORK — a DESIGN decision, not a measurement, and not resolvable by reading

**`R139`'s disjunct (a) — the instrument.** The census removed the unknown; what is left is a choice
with two defensible answers, and **nobody has made it**:

| option | what it costs | what it buys |
|---|---|---|
| **Build the narrow lint** | source comments only (`.py`/`.ttl`/`.rq`), bare + explicit forms, EOF filter, paragraph-scoped referent, past-tense suppression. Flags **5**, of which 4 are real | Guards a class that has now bitten **three times**, twice by authors who knew the rule and were applying it at that moment |
| **Record disjunct (a) as REFUSED, with the measurement** | one register edit; strike nothing, since (b) already shipped as plan-rule 7 | Honest closure of an instrument the tree cannot support in general — recall 0/4 as prescribed, 0.7% precision tree-wide |

**The case for building** is that three instances is not a fluke and 4/4 recall for one false positive
is cheap. **The case against** is that the shippable lint guards **four citations in one directory**,
which is a lot of machinery for a small blast radius. Both are reasonable; the numbers do not decide it.

### PROPOSED — blocked on rulings, unchanged and NOT re-derived

`R132` (identity/merge), `R127` (four coupled oracles), `R131`(b). Open
`docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5 — that table is still the source.

## 1. Goal

Run the census the previous handoff graded PROPOSED, before anything was built on it. Done: it
**refutes** the prescribed instrument, scopes a narrower one, and turned up a third live instance,
which was repaired in the same act. `R139` stays **open**; no row was struck.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/residues-open.md`, row `R139` | **The census in full** — the counts, the filter ladder, the third instance, and what is *not* re-verified. This is the canonical record; there is deliberately no separate evidence doc |
| PR #140 | The same numbers as a reviewable diff, plus the `compile.py` repair |
| `src/iladub/etkl/compile.py`, the `escalation-shapes.ttl` wiring comment | The repaired citation — a `grep`, not a line number, and why |
| `docs/superpowers/2026-08-31-four-mechanical-rows-handoff.md` § 5 | The proposal this discharges. Read it to see the grading working as intended |

## 3. What was decided, and where that decision is recorded

- **The prescribed lint is refuted, and NOT for the predicted reason.** The handoff predicted death by
  quotation false-positives; those are real but small (only **one** same-file quotation exists). It
  dies instead on **recall 0/4** — every real instance is a bare `:NNN`, and the explicit
  `basename:NNN` form the rule names occurs once repo-wide, upward, in a test string. Recorded in the
  `R139` row.
- **A narrow form IS shippable and its scope is measured**: `.py` comments, 5 flagged / 4 real / 20%
  FP, recall 4/4 held at every filter tier. Over `docs/**` it is 71–99% FP and must not run there.
  Recorded in the same row.
- **The third live instance was fixed, not just recorded.** `compile.py` cited `:1124` for a call at
  `:1200`, having already rotted once from `:1083`. Repaired by promoting the grep the comment already
  carried to be the citation. Line-neutral, 6 in / 6 out, **re-measured after the edit**.
- **No separate evidence document was written for the census.** The register row is where residue
  evidence lives, and duplicating it would be plan-rule 6's defect in another medium. **Recorded here
  and nowhere else — reversible.**

## 4. Unverified or assumed

- **117 of the 521 false positives are ASSERTED cross-file, not proven.** The other 371 are provable
  by the EOF test (target line exceeds the citing file's own length); the 117 fall within range, so
  their classification rests on the census's referent resolution rather than on a check. All four LIVE
  hits were re-measured by hand. **If someone disputes the 0.7% precision figure, this is where to
  attack it.**
- **The census's own scripts are in a scratchpad, not the repo.** They are re-derivable from the
  commands in PR #140's body, but they are not tracked, so the numbers are not regenerate-and-diff
  gated the way a committed cache would be.
- **`R139`'s row now carries a long census.** Nobody has ruled whether that belongs in the row or in a
  separate artefact; the last handoff raised the same question about index-line length and it is still
  unruled.
- **The corpus-marked suite was NOT run** — only `-m "not corpus"` (`1371 passed`). Unchanged for
  three loops now.
- The 150K executing floor is still labelled `NO SOURCE` in `tiers.py`.
