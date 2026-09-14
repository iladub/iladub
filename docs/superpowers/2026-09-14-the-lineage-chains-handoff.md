# Handoff — the lineage chains, and the three tests that encoded a world without it

**Topic:** [[R227]] lineage — D2 merged, the walk is length 2

**Serves:** prog:criterion:etkl:04 — R225's gate half is merged; what remains is the misreading
R225 is actually about.

**Date:** 2026-09-14. **Merged as:** `523e00b` (PR #219, squashed). **Branch:**
`r225-arm-b-resolution-test`, now merged — note a squash merge leaves it NOT an ancestor of
`main`, so `git branch --merged` reports it unmerged and `-d` will refuse. That is expected, not
a failed merge.

**Doc impact: none.** No released term; the two `.rq` files are internal queries and
`dec-shapes.ttl` gained a comment, not a constraint.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is typed
assertion-or-proposition.

---

## 5. The next concrete action

### 5a. ASSERTED — R225's own subject is STILL UNREPAIRED, and that is the loop to run

This is mechanical in the sense that matters: the outcome is known and doing it *is* the work.
D2 broke the coupling that made R225 need a ruling, and nothing more.

**41 of 41 border-only bands are still re-bucketed into one column** (ons 33, bfs 8). D1 — the
resolution test, the arm that would actually repair them — is still reverted at `54c0edf`. What
changed is the reason it was blocked: repairing those bands used to cost ons its grid reading,
because the fallback gate demanded the page assert nothing. That gate is gone. **The next loop
can land D1 and measure it against the corpus pair without the two arms fighting.**

The oracle R225's row already names, unchanged: **ons must not lose its grid** (0.9719934102,
571 cells, byte-identical by canonical graph hash) and **bfs p5 must not gain zero-cell
escalations** (it now adopts at 404 cells). Both figures are measured and in the row.

### 5b. PROPOSED — R227's cycle guard is unmeasured, and a third hop may not exist at all

**This rests on a prediction that must be RUN and may fail.** `_effective_verdict` walks the
supersession chain with a `seen` set against cycles. Measured reality: **the corpus produces
chains of length 2 only** — v1 ← v2 ← admission — so the guard has never been exercised, and
neither has any length > 2 behaviour.

The prediction: *a third hop is unreachable by construction, because there are exactly two
writers of `dec:supersedes` and each fires at most once per band per compile.* If that holds,
the guard is dead code defending against nothing and R227 closes by argument rather than by
test. **If it is false** — if some path can supersede twice — then both transitive queries need
re-examining at length 3, where "the head" and "the immediate superseder" diverge further than
anything measured here.

Cheap to settle: enumerate `dec:supersedes` edges per verdict across all seven documents and
check the maximum chain depth. Minutes, not a loop. **Do it before building anything on the
walk.**

### 5c. ASSERTED — what this loop must NOT be read as having done

D1 is still reverted. R171 half (a) — a non-tail **accepted** merge — is untouched; only half
(b) retired, and only under the same monkeypatched forcing it was always measured under. R226
(ons evidences no leaf header block) is untouched and still blocks ons stitching.

---

## 1. Where the primaries are

- **The lineage walk** — `src/iladub/etkl/document.py`, `_effective_verdict`, beside
  `_verdict_decision`; its caller is the admission site in the adoption pass.
- **The two writers it reconciles** — the section-repair `graph.add((v2, DEC.supersedes, v1))`
  and the admission site. Find them by `grep -n "DEC.supersedes" src/iladub/etkl/document.py`
  (a grep, not a line number — plan rule 7).
- **The ruling, recorded where it was reserved** — `vocab/shapes/dec-shapes.ttl`, the comment
  above `dec:SupersededOnceShape`. The shape body is unchanged.
- **The transitive queries** — `vocab/queries/effective-chain.rq` and `why-escalated.rq`.
- **The rows** — [[R227]] (new), [[R225]], [[R171]], [[R226]] in `residues-open.md`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| Chain, do not fan in — admission supersedes the reading that STANDS | `dec-shapes.ttl` comment; [[R227]] |
| Both consumers go transitive in the same change | the two `.rq` headers; [[R227]] |
| Band 1 is correctly superseded (grid re-reads the whole page) | `test_adoption_swaps_only_asserting_bands` docstring |
| R127 vehicle reverts to bfs — apple's lever pool is empty | `bfs_report` fixture docstring |

## 3. Unverified or assumed

- **5b entirely**, per its grading.
- **The `seen` cycle guard has never executed.** No corpus document reaches chain length 3.
- **R171 half (b) closes weakly.** bfs p5 adopts on a merged page, but `merged_run_admissible`
  is still monkeypatched. The row demanded a corpus document; it did not get one.
- **`main`'s CI on `523e00b` was still running when this was written.** The PR run on the
  identical tree (`bf8858f`) was green and the merge was `CLEAN`; that is not the same claim.

## 4. What this loop did

Measured that D2 caused all three failures (`47 passed` on `main` at `10b09c5`, in a detached
worktree with the interpreter and the gitignored corpus both guard-verified before any test —
either trap would have yielded a false "still passes"). Took the maintainer's lineage ruling,
implemented it as a walk, made both consumer queries transitive in the same change, re-baselined
three tests with rulings recorded rather than assertions softened, and falsified four ways.

**Worth carrying, because it is the technique and not the result.** Falsification case B is what
earns the new lineage pin: deleting section repair's own edge collapses the chain to one hop,
**SHACL conforms to that graph**, and only the test assertion catches it. Case A showed the
membrane catches fan-in on its own — so a pin justified by "it catches fan-in" would have been
worthless. The pin had to be justified by what the membrane *cannot* see.

**Five claims written from reasoning were refuted by running them**, each corrected in place
rather than deleted: that D2 moves band 0's fate but not band 1's; that `page_bands` under the
forced merge is 15 (it is 12 — four bands become one); that a fan-in regression fails before the
membrane (it does not); and two pins of my own that could not fail (one caught by falsification,
one by inspection). The rate is the signal: on this codebase, reasoned claims needed running.

**Three background jobs reported nothing while being described as running** — two deadlocked on a
`pgrep -f` pattern that matched the waiting shell itself, one parked on a heredoc that never fed
the interpreter. The habit that fixes it: **verify a live PID before claiming work is in flight**,
and never `pgrep -f` a string that appears in the grepping script.
