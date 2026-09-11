# Handoff — the register serves the arc: a process spec, for a fresh session

**Topic:** the residue register's relation to the arc — why the architecture line is flat while
the register moves, and what the maintainer agreed to change on 2026-09-11

**Date:** 2026-09-11. **Loop shape:** none — this is a HANDOFF written from a conversation, at
~224K working tokens (4.5× the originating floor), which is why the spec is not drafted here.
**Doc impact: none** (the spec it hands off will declare its own).

Part 5 written first. Every figure below was measured in-session on `main` at `0bc7aca`; the
commands are in part 2 so a fresh session can re-run them rather than trust them.

## 5. The next concrete action

### 5a. ASSERTED — write the SPEC, fresh session, before or beside the donation plan's execution

Subject: *the register serves the arc.* The maintainer agreed to the direction in conversation
(recorded nowhere but here — part 3). Three changes, to be specified against the measurements in
part 2, each with its falsifying oracle:

1. **A loop names the criterion it serves, or declares itself maintenance.** One typed line in the
   handoff's part 5 (`serves: prog:criterion:etkl:05` or `serves: maintenance`). Oracle: the
   cockpit strip's `work` segment can print it; `tests/test_cockpit.py`'s live-handoff test is
   the shape to copy.
2. **Selection comes from the arc, not from the newest handoff.** The next subject is chosen from
   the strip's `ready` and `frontier` sets; `residues.md` is opened to find what blocks a chosen
   criterion, not to find a subject. Oracle: the fraction of loops in a window that name a
   criterion — today it is 0 of the September loops.
3. **A third register state, PARKED.** Recorded by rule, not pursued by intent; keeps the row and
   its evidence (the never-delete rule stands); dated, by decision, in one triage pass. The spec
   must decide how parked rows enter the tally fraction — the `(c/t closed)` snapshot convention
   in CLAUDE.md § Deferred residues is the maintainer's and must not be silently redefined.

**Why asserted:** the mechanism is measured (part 2), the direction is the maintainer's, and the
three changes are small and separable. What is NOT asserted is the middle layer in 5b.

### 5b. PROPOSED — residues cluster under a few ARCHITECTURAL QUESTIONS, and that layer is what makes them closable

The arc's criteria are adjudication-shaped (a document's score floor accepted; every escalation
reason disposed) — too coarse to steer one loop. The September chain R154 → R208 (about 55 rows)
looks, from the handoffs, like three questions: *which line is the header, and whose reading has
authority* (R160, R165, R166, R201, R203, R205 …); *what the score's denominator counts* (R176,
R177, R178, R181 …); *what the evidence-doc gates may fire on* (R186 → R199). If that holds, the
register is a tree with few roots, closing a root closes many rows at once, and rows that are the
same root seen from different loops become visible as one. **Why proposed:** it is read from
handoff titles, not measured. **Falsify it first**, in the spec session: triage the 61 open rows
numbered ≥ 150 by the criterion or question each bears on. If most fall under a handful of
questions, the middle layer earns its place (a `prog:` or `res:` term per question, rows linked to
it, questions linked to criteria). If they scatter, PARKED alone is the remedy and the layer is
not built.

### 5c. PROPOSED — an adjudication loop is the cheapest visible move on the arc

`ready 15` includes etkl:02–06, all unblocked. Apple (etkl:06) sits at 0.6289 with three
proposed dependencies (tab:02/05/08). An adjudication loop that pins a floor under an accepting
rationale flips a fraction the strip has not moved since 2026-08-31. **Why proposed:** whether the
maintainer accepts 0.6289 as a floor is a reading judgement nobody has made, and the dependencies
are `prog:proposedDependsOn`, not hard.

### 5d. ASSERTED — the donation plan executes regardless

`docs/superpowers/plans/2026-09-11-grid-donation.md` is bfs work under etkl:05 and does not wait
on this spec. If the spec lands first, its Task 6 names `serves: prog:criterion:etkl:05` and
notes the criterion will not flip (the score is predicted unchanged).

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the strip | `scripts/cockpit.py` — `_criteria`, `arc`, `frontier_counts`, `_arc_line` | the second line moves only on `prog:met`; `?` is not zero; `frontier`/`ready` are counts, not verdicts |
| the arc | `tests/arc-manifest.ttl` | five rungs; 43 criteria; `prog:blockedBy` names 13 rows; `prog:proposedDependsOn` edges |
| the register | `docs/superpowers/residues.md` (index), `residues-open.md`, `residues-closed.md` | the `(c/t closed)` snapshot convention; 198 rows, 63 closed, 135 open |
| the conventions | `CLAUDE.md` § Deferred residues, § The handoff's next action is TYPED | what a spec may and may not redefine |
| the last arc movement | `git log -S'prog:met true' -- tests/arc-manifest.ttl` | 2026-08-31 (R45, WHO) |

## 2. What was measured (2026-09-11, `main` at `0bc7aca`)

- **Arc line:** etkl 2/7 · dec 11/17 · holon 5/6 · tab 1/10 · substrate 0/3 · frontier 13 · ready 15
  (`.venv/bin/python scripts/cockpit.py`).
- **Frontier rows** (every `prog:blockedBy`): R43 R44 R62 R71 R74 R77 R79 R80 R83 R84 R97 R99 R100
  — **13 of 13 open**, all raised in August, none touched by a September loop.
- **Open rows numbered ≥ 150: 61.** None is named by any criterion. Every row closed since
  2026-08-31 is numbered ≥ 150.
- **Closed fraction at raise time** (from the `(c/t closed)` snapshots in `residues-open.md` /
  `residues-closed.md`): R95 0.20 · R120 0.20 · R144 0.20 · R157 0.28 · R181 0.30 · R208 0.31.
  Rising, not falling.
- **Rows first added per week** (first commit adding the row line to `residues.md`, via
  `git log --reverse -- docs/superpowers/residues.md` + `git show -U0`): 10 Aug 12 · 17 Aug 27 ·
  24 Aug 29 · 31 Aug 23 · 7 Sep 33.
- **Velocity, 7 days:** 42 raised, 18 closed; last close 1 day ago.

## 3. What was decided, and where that decision is recorded

- **The direction (the three changes in 5a) was agreed by the maintainer in conversation on
  2026-09-11.** Recorded **nowhere but this file** — reversible; the spec is where it becomes
  a ruling.
- **Nothing in the register, the arc, or CLAUDE.md was changed.**

## 4. Unverified or assumed

- 5b's clustering claim (read from handoff titles).
- That the raise rate is a property of the discipline rather than of the code: inferred from the
  rule "every deferral is recorded"; not measured against what a loop would have raised without it.
- Whether a PARKED state is expressible without touching the `(c/t closed)` arithmetic the
  maintainer ruled — the spec's question.
- The working-token figure (~224K) is from the harness's context line, not a status-line reading.
