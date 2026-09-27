# Evidence and handoff: arm A rescored under ruling (a), where the box is the extent (2026-09-27)

**Serves:** maintenance. It tests the proposition in part 5 of `2026-09-27-jev-decides-architecture-handoff.md` before any arm-A spec is written.

**Topic:** jev-reading · **Date:** 2026-09-27 · **src measured:** `c9e5567`

**Doc impact: none.**

This session stopped at the originating floor (about 51K working tokens, logged by plimslop). The
spec was **not** started. Part 5 is written first, and each action in it is graded.

## 5. Next action

- **Asserted:** in a fresh session, run the brainstorm and then write the spec for arm A under
  ruling (a).
  - Design sections 1–3 of `2026-09-27-question-compiler-design-handoff.md` § 3 stand.
  - The slice (section 4) is **extent reading by arm A, with neighbour-absorbing variants** (below).
  - Start from the spike script and `replay.py`.
- **Proposed, open to refutation (minutes):**
  - **Does an admitted cbh p0 / bfs p5 extent move the corpus score?**
  - Dev E already admits bfs p5 2/2 and cbh p0 4–5 of 6 in every repeat.
  - What is unmeasured is whether feeding those extents into `compile_tables` changes N/7. Etkl
    stands at 4/7 (memory `boxhead-reader-ons-accepted`).
  - Measure where the extent enters compile before choosing the slice. If an admitted extent does
    not reach the score, the slice is wrong.
- **Proposed, a question the spec must answer and not assume:**
  - Under (a), the line roles *inside* an admitted extent (caption, note, footer, total) are
    carried with **no oracle**.
  - The box disposes only the extent. It does not dispose whether a boxed line is a title or a
    footnote.
  - "No oracle, no worker" (CLAUDE.md § 8) applies to those roles.

## 1. Goal

Test the handoff's proposition that under ruling (a) the held-out yield of arm A rises from 3/24.

## 2. Where the primaries are

- `internal/benchmarks/jev-2026-09-27/spike-A/replay.py` is `spike.py` with three changes:
  - `jev1` reads the recorded `calls2/` responses and asserts that the question set matches, so no
    new Jev calls are made;
  - it adds the `variants_a` block described in "Measured" below;
  - it writes `replay.jsonl` next to itself.
- The script is untracked and confidential, beside the raw calls.
- The spike itself: `2026-09-27-jev-picks-oracle-disposes-spike-evidence.md`.

## 3. What was decided, and where

- Ruling (a), *extent = what the author boxed*, is recorded in
  `2026-09-27-jev-decides-architecture-handoff.md`.
- Nothing new was ruled in this session.

## Measured

**The proposition as written is refuted by construction.**
- The spike's "admitted" count is decided by the oracle, which is equality with the drawn box. It
  does not depend on ground truth.
- Relabelling ground truth as the box therefore renames the outcomes but leaves the yield at 3/24.
- The yield rises only if the host **enumerates a variant equal to the box**. When Jev's round 1
  splits a boxed title or footer into its own piece, no trim variant of the table piece contains it.

**The protocol change that makes (a) reachable** (`variants_a`, PROCEDURAL enumeration, no constant):
- Besides the 8 trim variants, each table piece may absorb pieces that are **not** labelled TAB but
  that Jev's round 3 labelled caption, note or furniture.
- An absorbed piece must be contiguous in line index (directly above, chained upward, or directly
  below, chained downward) and must overlap the table in x.
- A chain stops when there is not exactly one such neighbour.
- Admission is unchanged: a variant is admitted only if its word set is exactly equal to one drawn
  box.

**Replay fidelity.** 84 page-runs replayed (E and R × h1–h3 × 14 pages). The recomputed `variants`
equal the recorded ones in **84/84**.

| pages | cond | table-runs | admitted, old | admitted, `variants_a` | admitted ⊇ old GT (headings+body) |
|---|---|---|---|---|---|
| dev | E | 36 | 23 | **26** | 26/26 |
| held-out | E | 24 | 3 | **14** | 14/14 |
| dev | R | 36 | 20 | 23 | 23/23 |
| held-out | R | 24 | 4 | 7 | 7/7 |

Held-out E admits:
- WHO p1 and p2 in 3/3 repeats (the footer is absorbed);
- gcap p0 in 3/3 (the title is absorbed);
- stem p0 in 2/3;
- stem p2 in 3/3.

It still admits nothing on:
- ons p7/p8, where Jev splits the "Percentage change" sub-blocks;
- stem p1, which is still not diagnosed.

## 4. Unverified or assumed

- **The absorbing rule was chosen after seeing the held-out failures** (WHO footer, gcap/stem
  titles). So 14/24 is **not** a clean held-out figure.
  - A clean test needs pages that neither this rule nor the spike's question set was designed
    against.
  - The same Jev answers were reused, so the absorbing step itself has seen no new Jev output.
- "Admitted ⊇ old GT" shows each admitted box contains the whole table. It does **not** show that
  the roles of the absorbed lines are right, because nothing checks them.
- The chain rule "exactly one neighbour" is a choice, not a derivation. Pages with two adjacent
  captions side by side were not in the sample.
- Scale: 14 pages, 3 repeats, all from recorded calls. apple p0/p1 were still excluded (lead 2: the
  oracle breaks there).
