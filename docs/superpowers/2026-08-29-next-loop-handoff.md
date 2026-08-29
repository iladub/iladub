# Handoff — choosing the loop after `R135`

**Topic:** what follows the declaration instrument — `R135` is closed and its four successor rows
(`R142`–`R145`) are on the register, so the next loop is a *selection*, not a continuation. This
file carries pointers only; the register and the loop evidence carry the numbers.

**Date:** 2026-08-29 · **Branch:** `main` at `71a6312` · **Shape: pointers only.**

## Goal

Pick and spec the loop after `R135` — in a fresh session, because selection is originating work and
the session that closed `R135` ended at 92,969 working tokens, 1.9× the floor.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/residues.md` | the INDEX — read it **in full**, it is the one file meant to be read entire. The tally is now **27 closed / 135**. An index line is a pointer: never plan against one without opening its full row |
| `docs/superpowers/residues-open.md`, rows `R142`–`R145` | the four candidates this loop raised, each with its measurement and its "what would close it" |
| `docs/superpowers/2026-08-28-r135-loop-evidence.md` | what the instrument actually does, O1–O5 with their commands, and the four places the plan was contradicted. Read the **Task 5** table rather than re-reading the plan |
| PR #130 (`71a6312`) | the merged loop, if you want the argument rather than the evidence |
| `vocab/shapes/query-declaration-shapes.ttl:23-28` | the `prog:`/`docgov:` exemption, with its date and reason — this is what `R142` proposes to delete |
| `tests/query_terms.py:46-58` | `query_files()` and `declaring_files()` — the two globs that define the instrument's population, which is what `R143` proposes to widen |

## What was decided, and where it is recorded

- **`R135` closed on both halves of its own "what would close it"** — recorded in
  `residues-closed.md` (struck row, closure evidence in place, original text kept) and in the loop
  evidence. Not reversible without reopening the row.
- **`R117` deliberately NOT struck**, and `R144` exists so that its *unrealized hypothetical* is not
  later mistaken for a stale row. Recorded in spec §9, `R144`, and the closure row.
- **The index never strikes an id; the detail row does.** This is the file's practice
  (`grep -c "^| ~~R" residues.md` → 0), not a written rule — the plan's §Done says "struck in all
  three files", which is looser than what the register does. **Recorded nowhere but here and in the
  loop evidence.**
- **A recommendation, recorded nowhere but this file, and therefore reversible:** `R142` looks like
  the sharpest of the four — the arc instrument's own vocabulary (`prog:`, 9 terms) is undeclared,
  and its closure has a **deletion as its oracle** (author the two ontologies, then remove the
  in-scope filter and require the corpus to stay green), which is the shape that has worked twice
  now. `R143` is larger and carries `R130`'s standing warning: census the population before
  enumerating it. **The next session should re-derive this, not inherit it.**

## Unverified or assumed

- ~~CI on the merge commit was still running when `main` was merged.~~ **RESOLVED 2026-08-29:** run
  `33235356253` on `main` completed **success**. Kept because the *cause* is still live and is worth
  someone's attention: `gh pr merge --auto` did **not** queue behind checks, because this repo has
  **no required status checks** — so `--auto` silently degrades to an immediate merge, and
  `6268437` / `b8f6dde` went in on the local suite alone. The next merge will behave the same way.
- **`R145`'s hazard is measured but not demonstrated.** The 6-of-7 ablation breadth is a real
  measurement; that a *future* edge out of `holon:05` would be wrongly admitted is a reading of
  M19's arm 1, not something that has happened.
- **`R142`'s term counts (9 `prog:`, 12 `docgov:`) come from the loop's own census**, reproduced at
  `63892ae`. They have not been re-measured since the merge.
- **The floors this handoff obeys are asserted, not proven** — `tiers.py` labels the 150K
  `NO SOURCE`, and `R141` is still open on the prediction that the override rate falls below 54%,
  with `n=0` observed records under the new gate.

## The next concrete action

In a **fresh session**: read `docs/superpowers/residues.md` in full, open the full rows for `R142`
and `R143`, and decide between them — the deletion-as-oracle loop or the census loop. Everything
else in this file is a pointer to check that decision against.
