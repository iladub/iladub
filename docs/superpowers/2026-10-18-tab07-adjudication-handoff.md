# Handoff: tab:07 by adjudication — R323 ruled; the spec is written fresh (2026-10-18)

**Serves:** prog:criterion:tab:07 — verify it is still `prog:met false` before starting.

**Topic:** compile · **Date:** 2026-10-18 (session began 2026-10-17)

**Doc impact: none.** A handoff only.

Part 5 was written first. The session was at about 49K working tokens, at the 50K originating floor.
It handed off on the maintainer's instruction ("handoff and write fresh") instead of writing the spec.
The figures in parts 1–4 were measured by a read-only subagent at `cbacae6`. They are pointers;
re-measure any of them that a spec section rests on.

## 5. The next concrete action, typed

1. **ASSERTED: the maintainer chose this subject on 2026-10-17.** The ready rung, `substrate:01–03`,
   was the alternative and was not chosen.
2. **ASSERTED: the maintainer ruled R323 on 2026-10-17.** `cor:DisposalShape` (D2) is judged at the
   disposal's **own dated reading**. The disposal records the baseline it was judged against, so a
   later repair cannot strand it under the append-only manifest. The superseding-adjudication
   alternative was rejected.
3. **PROPOSED, presented but not yet approved: the design below.** Write the spec at
   `docs/superpowers/specs/2026-10-18-<topic>-design.md` from it, in the first third of the fresh
   session. Approach 1 was offered as the recommendation, and the maintainer's reply was to hand off.
   **Re-present approach 1 and get an explicit approval before writing the spec.**
   - **Approach 1 (recommended): the disposal carries its own reading.**
     - The adjudication holding `cor:disposes` gets a `cor:Reading` node with `cor:recordedIn <the
       baseline path>`, plus a new term, e.g. `cor:blob "<git blob sha>"`.
     - A new lift entry point reads that blob through `git cat-file -p` and attaches its firings to the
       reading node.
     - D2 then checks that **reading's** firings for `cor:live > 0`, holon-scoped, never the current
       baseline's.
     - Why a blob sha: it is content-addressed, so it survives the squash merge, and it can name the
       baseline regenerated inside the disposal's own PR. A commit sha can do neither.
   - **Rejected:**
     - A commit already on `main`: it cannot name the in-PR baseline.
     - The `inputs.json` fingerprint: it identifies the inputs but cannot fetch a baseline without a
       history search.
   - **Loop scope:**
     - Rewrite D2 and its negative tests. A disposal whose reason was repaired *since* must still
       conform; one with no live firing in its *own* reading must be refused. Both are falsified.
     - Add a `(path, data)` entry point to `lift_firings`.
     - Write two dated disposals, on bfs and on ons, composed by the agent and signed off by the
       maintainer's merge.
     - Set `tab:07` met true and **delete** its `R44` and `R71` edges in the same change, with a
       recorded reason.
     - Strike R323.
     - Fix the stale pointers listed in part 4.
   - **Two costs the spec must carry:**
     - `cor:blob` is a `vocab/` edit, and `vocab/` is a compile input. So the loop ends with one
       `corpus_baseline.py regenerate` pass, about 24 minutes, after the last input edit.
     - The history-reading lift must **not** run at import of `tests/test_corpus.py`. That is R325's
       hazard, made worse by a git read. Call it only from D2's test.
4. **PROPOSED, falsifiable in minutes:** that `git cat-file -p <blob>` resolves in CI. The clone is
   `fetch-depth: 0` (`.github/workflows/ci.yml:16`), and a squash-merged blob is reachable from `main`.
   An **in-PR** baseline blob must also be reachable from the PR's merge ref. Check this first, with a
   throwaway test on a draft PR, before building on it.

## 1. Goal

Meet `prog:criterion:tab:07` (`tests/arc-manifest.ttl:1354`):
- KIND_NOT_SUPPORTED is disposed by a dated `cor:adjudication` on every corpus document it fires on.
- Its two parameters of `tests/test_corpus.py::test_escalation_reasons_are_adjudicated` turn from
  strict xfail into passes.

## 2. Where the primaries are

**Rulings and specs**
- R323's full row: `docs/superpowers/residues-open.md:230`. Its "what would close it" column is
  answered by part 5 item 2.
- R259 spec: `docs/superpowers/specs/2026-09-18-a-firing-is-not-a-fact-design.md`. D2 is in § 3; the
  strengthened D2 and the lift are in § 8.

**Shapes and lift**
- D2: `tests/corpus-shapes.ttl:106-118`, with its rationale at `:91-105`.
- `ReadingShape`: `:63-75`. It already provides `cor:readAt`, `cor:atCommit` and `cor:recordedIn`.
- The lift: `tests/corpus_firings.py:36-86`. It globs one directory and records a path, but no sha.

**The oracle**
- Its parameters are built at `tests/test_corpus.py:212-235`. `_adjudication_param` derives
  `xfail(strict=True)` from the SPARQL ASK `is_disposed`, so no marker is hand-removed.
- At `cbacae6` it reports `6 xfailed`: apple, bfs and ons DATAGRID_RESIDUE; bfs and ons
  KIND_NOT_SUPPORTED; bfs REGION_TILING_FAILED.
- Five criteria share this oracle (`arc-manifest.ttl:1262, 1318, 1362, 1374, 1387`), and a strict
  xfail exits 0. So `met true` stays an authored claim; it is not proved by an exit code.

**The rules met true has to satisfy**
- M8 (`tests/arc-shapes.ttl:149-153`) refuses **any** `prog:blockedBy` on a met criterion, whether the
  row is open or closed.
- What an edge means: `arc-manifest.ttl:1174-1175`.
- Precedent for deleting the edge in the same act that sets met: `:232` (R166).

**The term and the firings**
- `cor:disposes` is declared at `vocab/internal/corpus.ttl:273` (domain Adjudication, range
  `xsd:string`), and it is used nowhere yet.
- The five live firings (from the baseline JSON, with the band text from a per-page compile) are all
  not-a-table:

  | Document | Page/region | What the band is |
  |---|---|---|
  | bfs | p0 r0 | press-release masthead |
  | bfs | p5 r15 | sources line and footnotes |
  | bfs | p6 r1 | table title "T3" |
  | ons | p0 r1 | release masthead plus contents list |
  | ons | p7 r0 | table title "IOS1" |

  The ons firings at p7 r3 and p8 r2 are superseded by the grid adoption. Two caveats for the
  disposal text:
  - ons p0 r1 holds a 3-column label/value release block. Name it as metadata.
  - The two titles are context that does not reach their tables (§ Core design principles 5). Say so,
    as the R288 ruling did for the cbh Note.
- The existing adjudications that name the reason without disposing it:
  - bfs: `tests/corpus-manifest.ttl:127, 454, 470`.
  - ons: `:114, 465`.

## 3. What was decided, and where it is recorded

- **The subject and the R323 ruling:** both on 2026-10-17, by the maintainer. They are recorded here
  and in the user-scope memory, and are not yet in the register. **Record the ruling in R323's row
  when it is struck.**
- **Why the R44 and R71 edges can be deleted without closing either row** (an inference, to be
  re-argued in the spec):
  - Closing either row would dispose of none of the five firings.
  - R71 concerns two graincorp-stem bands, and none of the five is a stem band.
  - R44 is a three-reason bfs row with no shared root cause.

## 4. Unverified or assumed

- **Item 4 of part 5:** whether an in-PR blob resolves in CI. Not run.
- **Stale pointers, measured but not fixed:**
  - The tab:07 statement cites `compile.py:978`, but the emitter is at
    `src/iladub/etkl/compile.py:1876-1890`.
  - The comment at `arc-manifest.ttl:1351` says "bfs only", but the reason fires on bfs 3 plus ons 2.
  - R44's "4 (3 live + 1 superseded)" is wrong: the baseline has 0 superseded on bfs.
- Whether the manifest can be edited in place for the statement's citation. Check
  `tests/arc-manifest.ttl`'s own editing rules before touching a `prog:statement`.
