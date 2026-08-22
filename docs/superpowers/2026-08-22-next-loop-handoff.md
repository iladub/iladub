# Handoff — the arc loop is merged and pushed; what the next loop can pick up

**Topic:** process · **Date:** 2026-08-22 · **`main` @ `6139998`, pushed** (fast-forward from
`f436a8c`; CI run `32552846172`) · **Shape: mechanical** — written at 166k as a pointer document,
authoring nothing.

## Goal (of the loop that just closed)

Give every named rung of the arc a countable denominator and a dependency edge to the register, so
the cockpit stops printing `stage ?/5`. **Shipped**: `arc etkl 1/7 · dec 11/17 · holon 4/6 · tab
1/10 · substrate 0/3`, **17 of 43 criteria met**, `frontier 15`, `ready 17`.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/2026-08-22-arc-merge-handoff.md` | the close itself: what was decided at the merge, what was assumed, and the correction that `scripts/review-package` never existed |
| `docs/superpowers/residues.md` → `residues-open.md` | **102 rows, 22 closed, 80 open.** R107-R112 are this close's; read the full rows, never the index line |
| `tests/arc-manifest.ttl` · `tests/arc-shapes.ttl` · `tests/test_arc_manifest.py` | the manifest, its ten numbered refusals, and the environment leg (M5/M5b/M5c/M7/M10) |
| `vocab/queries/arc-*.rq` | position, frontier, unblocked, orphan — AXIOM, open world, `SELECT`-only |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` | the spec — **carries three measured errors**; the ledger lists them |
| `.superpowers/sdd/2026-08-20-the-arc-has-a-denominator/` | the ledger (Rulings 1-21), the eight tasks' evidence, and the whole-branch review with its ~42-minor triage. **GIT-IGNORED — `git clean -fdx` destroys all of it.** Its actionable half was lifted into R109-R112; the triage table was not |

## What was decided, and where each decision is recorded

- **R108 is DECIDED, not open** (maintainer, 2026-08-22; recorded **in the R108 row**): a
  `prog:blockedBy` naming a **closed** register row is a **manifest ERROR** and M7 must refuse it.
  The consequence is deliberate and belongs to the implementer — **closing a residue becomes a
  two-file change by design**, and the refusal should name the edge to delete.
- **I-1 stays parked** (maintainer, 2026-08-22): the three-row composed status line in gitignored
  `.claude/settings.local.json` is left alone. The fallback shape lives in a test docstring only.
- **R109's four faces were not fixed**, deliberately — the row says why one shared `split_pointer()`
  is the fix and why closing them face by face is the trap.

## Unverified or assumed

- **The merged-result legs were still running when `main` was pushed.** Both legs are green at
  `e64a379` (1235 passed / 7 skipped / 1 xfailed / 10 warnings; corpus 43 passed) and the pushed tree
  is that plus **one docs-only commit**, whose four affected guards passed. If the re-run or CI
  disagrees, the disagreement is the finding.
- **The whole-branch review's ~28 DEFER / ~13 VOID verdicts rest on its own measurements**, quoted
  inline in a git-ignored file. Only B1, R107, R108 and R109's four faces were re-measured by a
  second seat.
- **`holon:03` would be FALSE-refused by a literal M11** (R106's remedy): it is an
  *existence-of-shape* claim citing the shape file, which has 0 focus nodes by construction. Recorded
  here and in the merge handoff; nowhere else tracked.
- **"Exactly 10 warnings" is data-dependent** — 8 rdflib + 2 doc-governance queue warnings; it
  becomes 8 when a release drains the wiki promotion queue. A leg reporting 8 is **not** a regression.

## The candidates, with what each costs — not a choice, a menu

1. **The 80% question.** **59 of 74 open register rows block no criterion of any rung** — confirmed
   twice, element for element, where spec §7.4 had called R101 "the first instance." This is the most
   consequential thing the loop measured and **nothing acts on it**. Either the arc's 43 criteria are
   incomplete, or most of the register serves no stated goal. *Cost: a spec-shaped question, not a
   fix. It is the only candidate here that could change what the project counts as progress.*
2. **M11, the non-vacuity refusal (R106).** The rule that a `met true` criterion must cite evidence
   containing focus nodes exists **only in prose**. Honest form re-derives the count over exactly the
   files each criterion cites. *Cost: one test-leg constraint; watch the `holon:03` caveat above.*
3. **R108 as decided, plus R109's `split_pointer()`, plus R110's message hygiene.** Three rows, one
   file each, all in `tests/`. *Cost: small, and it is the tidy-the-membrane loop.*
4. **R97-R101** — the vacuity-registry family the earlier tracker still names, of which R101 (a
   module-level skip hides a subsystem behind one line) is the one with teeth.

## CHOSEN DIRECTION (maintainer, 2026-08-22): the dependency graph

**The question asked:** *do we have a clear landscape of dependencies for building the full
architecture?* **Measured answer: NO, and deliberately so.**

`tests/arc-manifest.ttl` carries **no dependency edge of any kind**. Predicate census of the live
file: `ofRung` 44, `blockedBy` 11, and **`precedes` appears exactly once — in a comment saying it
does not exist** (`:19-21`): *"RUNGS ARE UNORDERED (decision 8). There is no prog:precedes and no
index property: `tab` is depth inside `etkl`, not a stage after `substrate`, so the repo does not
assert an ordering that is false for one of the five."* The only edges in the graph are
criterion→rung and criterion→residue. **The arc is a scoreboard, not a graph.**

**Decision 8 is not wrong — it is right at the wrong granularity, and that is the whole loop.** At
rung scope an ordering IS false: `etkl` needs a minimal holon substrate to compile *into*, and the
holarchy needs holons that only `etkl` can produce, so `etkl → holon` and `holon → etkl` are both
true and the rung-level graph has a **cycle**. At criterion scope it need not: *which* holon
criteria `etkl`'s next criterion actually needs is a smaller, checkable claim. **So the dependency
edge belongs between CRITERIA, and the loop's first job is to establish whether that graph is
acyclic — not to assume it.**

**What this subsumes:** candidate 1. The register's 59-of-74 orphan rows have nowhere to attach
today *because there is no edge type that would carry them*; a criterion→criterion graph gives
"what unblocks what" a derivation instead of a count.

**The seam to name in the spec, not answer here** — a hand-asserted `prog:dependsOn` is a
**proposition**, and the loop is worthless without an independent disposer. The candidate oracle:
a dependency X→Y is falsifiable by asking whether X's oracle test can pass with Y's artifact absent.
Whoever writes the spec must decide whether that is checkable at acceptable cost, and say so before
designing the vocabulary. **Proposer and disposer must not be the same reading** (see the
spec-writing discipline).

**What "one document that monitors" means here:** the monitor is **generated from the graph**, never
hand-maintained — the cockpit strip and `residues.md` are hand-maintained today, which is why they
drift (three recorded tally corrections). Its shape is a spec question, not a plan one.

## The next concrete action

In a **fresh session, in its first third**: write the spec for the dependency graph above — the
edge's semantics, the acyclicity question at criterion scope, the falsifying oracle for a dependency
claim, and what the generated monitor asserts. Candidates 2-4 stay on the menu behind it.
