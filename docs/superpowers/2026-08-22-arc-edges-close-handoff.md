# The arc has edges — loop close: handoff, the spec's four corrections, and the definition-of-done audit

Task 7 of `docs/superpowers/plans/2026-08-22-the-arc-has-edges.md`, argued from
`docs/superpowers/specs/2026-08-22-the-arc-has-edges-design.md`. Branch `the-arc-has-edges`,
BASE `dcd45fd`, closing at Task 7's commit. Runner `./.venv/bin/python` (3.12.0, rdflib 7.6.0),
never `python3` (Global Constraint 1).

This file is **evidence class** (`docs/superpowers/**`) and is immutable after loop close. It is
also the loop's handoff, which is why the handoff proper is at the top: a later session reads
§A–§E and stops there unless it needs the audit.

---

# §A The handoff

## Goal, in one line

`tests/arc-manifest.ttl` now carries a **criterion→criterion dependency graph** — 6 asserted
edges grounded by a two-sided ablation, 22 propositions each carrying one rationale — so
*"what must land before X"* is a **derivation** and no longer a reading.

## Where the primaries are, and what to establish at each

Read these, in this order, and stop as soon as the question is answered. **Nothing below
restates them.**

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-22-the-arc-has-edges-design.md` | the binding authority — §1 the question, §4 the four preconditions + the ablation, §5 the refusals M12–M19, §7 the 80% correction, §8 what the loop does not do, §10 the definition of done |
| `docs/superpowers/plans/2026-08-22-the-arc-has-edges.md` **§0** | **four measured corrections to that spec**, which the spec does not carry — summarised in §C below because a committed spec must not be edited |
| `docs/superpowers/2026-08-22-worktree-oracle-seam.md` | Task 1: can an oracle run in a throwaway worktree at all, what the ablation costs, and the instrument defect (`rc=4` swallows a healthy sibling) that forced one subprocess per module |
| `docs/superpowers/2026-08-22-arc-edges-authored.md` | **the loop's substance** — the reading (§1, incl. nine readings rejected with a stated reason), the grading (§2), the acyclicity answer (§4), the one refuted edge (§5), the blast-radius disclosure (§6), the falsification (§7), and §9 *"what a later reader should not re-derive"* |
| `docs/superpowers/arc-dependency-landscape.md` | **generated cache** — the current landscape. Never hand-edit it; see §D |
| `tests/arc-manifest.ttl`, foot of file | the authored edges themselves, with the refutation recorded as a comment |
| `tests/arc-shapes.ttl` + `tests/test_arc_manifest.py` | M12–M18, closed world, 13 `sh:sparql` arms and 13 fixtures |
| `tests/test_arc_ablation.py` | M19, the procedural leg; its docstring is the argument for why it is irreducible |
| `vocab/queries/arc-depends.rq` · `arc-ready.rq` · `arc-reach.rq` | the three derivations; each header carries its own design argument |
| `scripts/arc_depends.py` + `tests/test_arc_landscape.py` | the renderer and the regenerate-and-diff gate that earns the cache exception |
| `.superpowers/sdd/2026-08-22-the-arc-has-edges/progress.md` | **the controller's ledger** — every dispatch, every ruling, every deferred finding, task by task. Untracked; if it is gone, this file and the six task reports beside it are the record |

Commit chain: `dcd45fd` (plan) → `5f0647f` T1 → `657fecb` T2 → `7e0470c` T3 → `026f974` T4 →
`e8df8b7` T5 → `19ba03f` T6 → this commit T7.

## What was decided, and WHERE each decision is recorded

A decision recorded only here is **reversible**; one recorded in a tracked artifact with a test
behind it is **settled**. The column says which.

| decision | recorded where | status |
| --- | --- | --- |
| Two predicates, `prog:dependsOn` / `prog:proposedDependsOn`, not one with a grade property | spec §3; enforced by M15/M16/M17 in `tests/arc-shapes.ttl` | settled |
| A rationale rides a standard `rdf:Statement` reification node, not RDF-star and not a literal on the criterion | plan §0/C3; enforced by M18; the manifest's `@prefix rdf:` comment says why | settled |
| A4 stays **non-strict** (same-day `metOn` is admissible) | spec §2 Q3, plan §0/C5's existence proof (`holon:03 → holon:01`, both met 2026-06-23) | settled — the edge exists and is asserted |
| A **refuted** edge is DELETED, never demoted — M17 forbids the demotion | plan §0/C4; the deletion is recorded in `arc-edges-authored.md` §5 and in a manifest comment | settled by the membrane; the *record* of the refutation is prose only |
| Ablation groups by **criterion**, not by file (≤ 17 worktrees, not 28) | plan §0/C2; implemented in `ablation_refusals` | settled |
| M13 owns the self-edge; M14 must **not** fire on a pure self-loop | controller ruling, pre-flight; implemented as `FILTER(?y != $this)` and pinned by a fixture | settled |
| 13 `sh:sparql` arms and 13 fixtures, not the plan's 7/7 | Task 2's report + review (adjudicated a **strengthening**: under one disjunction, 4 of A1/A2/A4/A6 and 2 of M18's arms would have been pinned by nothing) | settled |
| A SKIPPED/XFAIL/XPASS oracle **refuses** an edge on both arms rather than being scored | `tests/test_arc_ablation.py` (`_scores`), pinned by a terminal-width test | settled |
| `arc-ready.rq` counts **positive met evidence** rather than `NOT EXISTS { … met false }` | `arc-ready.rq`'s header; pinned by an oracle independent of the textual absence-scan | settled |
| Where `arc-reach.rq` returns no row, the renderer prints `?`, never `0` | that query's header; pinned on a fixture asserting **both** branches | settled |
| Rungs stay unordered (decision 8 of the earlier loop) | **confirmed by measurement this loop** — §E.6 below | settled, and now evidenced |
| `arc-reach.rq` was NOT cut, though spec §6 called it cuttable | controller ruling, pre-flight; the query exists | settled by existence |
| The landscape is regenerated **by hand**; a manifest edit without a regenerate is a RED CI | §D below, and `scripts/arc_depends.py`'s header | **recorded nowhere but here and that header** — reversible |
| Blast-radius imprecision is disclosed rather than filtered: all six asserted edges are inside Task 1's 18-pair set **by construction** | `arc-edges-authored.md` §6, per-edge `file:line` | settled as disclosure; the *soundness* argument is an argument, not a proof, and §6 says so |
| Nothing anywhere records that this loop closed **no** residue while raising seven | `docs/superpowers/residues.md`, the tally paragraph — written this task | settled |

## Unverified or assumed

Not empty. Four items, each of which a later session may act on without re-deriving:

1. **The 18-of-44 blast-radius figure and the 44/272 pair census (Task 1) are not reproducible
   from repo state alone.** The raw 17×25 outcome data and the scratch scripts lived in an
   uncommitted scratchpad. Task 1's reviewer spot-checked the citations underlying the 18-pair
   claim and they held; the underlying table did not ship. Deferred by ruling to the final
   review, which is this task. **Still unverified from the tree.**
2. **"The reading was written before the membrane was consulted"** (`arc-edges-authored.md` §1's
   own claim) is *inference from shape*, not from timestamps — one commit cannot show temporal
   order. Task 4's reviewer said so explicitly and gave the one-directional evidence that
   supports it (the reading includes edges the membrane can never ground; a membrane-filtered
   reading yields the opposite shape).
3. **Task 1's sweep found no oracle that FAILS in a worktree.** It found one that **skips**
   (`etkl:01`, [[R114]]). The sweep covered the 17 met criteria's declared oracles, not every
   test in the suite, so "no oracle fails in a worktree" is a claim about the met set only.
4. **The `?` legend in the landscape's §3 documents a convention no live row exercises today** —
   all 15 residues named in `prog:blockedBy` currently gate at least one unmet criterion. It is
   pinned on a fixture instead (Task 6, GC9 substitution, premise verified independently by that
   task's reviewer).

## One next concrete action

**Run the ready list and start `etkl:02`.** The derivation's live answer (Task 5, reproduced
independently by its reviewer): the next unmet criterion is `etkl:02` and **nothing must land
before it**; 22 of 26 unmet criteria are startable today. The only four with anything in front
of them are all `etkl`, all waiting on `tab`, and all through **proposed** edges —
`etkl:03 ← tab:01,tab:04` · `etkl:05 ← tab:02,tab:07,tab:09` · `etkl:06 ← tab:02,tab:05,tab:08` ·
`etkl:07 ← tab:05`.

> **Read the 22 with its caveat — the number is honest, but it is not what it first sounds like**
> (final review, M-4; re-measured here over the shipped manifest). Of the 22 criteria
> `arc-ready.rq` returns, **15 have no dependency edge of either grade at all** — `dec:09 dec:17
> etkl:02 etkl:04 substrate:01 substrate:02 tab:01 tab:02 tab:03 tab:04 tab:05 tab:07 tab:08
> tab:09 tab:10` — i.e. they are ready through the query's **vacuous branch**. Only **7** are
> ready because a *read* dependency was found and is met (`dec:02←dec:01`, `dec:12←dec:11`,
> `dec:13←dec:11`, `dec:15←dec:14`, `holon:05←holon:01`, `holon:06←holon:01`,
> `substrate:03←dec:14`). **`etkl:02`, the headline, is one of the 15.** So *"nothing blocks
> `etkl:02`"* is what the graph says; *"we established what `etkl:02` needs and it is already
> there"* is what it does **not** say, and the two must not be read as the same claim. The
> reading behind the 15 was a real sweep, not an omission — `2026-08-22-arc-edges-authored.md`
> §1 names nine rejected readings, `etkl:02` and `etkl:04` among them explicitly (the manifest
> comment *"graincorp-capacity … fire NOTHING and take no edge here"*) — but **the graph cannot
> represent the difference between *read, none found* and *never read***, so a later reader
> cannot recover it from the manifest alone. Worth a row: an explicit "read, no dependency
> found" marker, so the two branches stop rendering as the same row. `arc-ready.rq`'s header,
> `arc-depends.rq`'s *"absence of an edge is absence of a READING"*, the landscape's §1 prose
> and the generated file's own lede all state this; this handoff repeated the bare number and
> now does not.

```
$ ./.venv/bin/python scripts/arc_depends.py && open docs/superpowers/arc-dependency-landscape.md
```

If the intent is instead to pay down this loop's debt, the highest-leverage row is **[[R117]]** —
it is the only one that, once closed, lets a deleted edge (`holon:02 → holon:01`) be re-authored,
and its reading is already written down.

---

# §B What this loop is NOT, restated because the origin handoff got it wrong

Spec §7 corrects the origin handoff's claim that this loop subsumes the orphan-residue question.
It does not. **Re-measured at close: 65 of 80 open register rows block no criterion of any rung**
(the origin handoff's "59 of 74" was quoted and never re-measured). A criterion→criterion edge
gives a *residue* nowhere new to attach. Raised as [[R115]] with the command that produced the
figure.

---

# §C The plan author's four corrections to a committed spec — recorded where a later session finds them

Plan §0 measured four things wrong with the spec and fixed them **in the plan**. The spec still
says the old thing. Editing it is not an option — `docs/superpowers/**` is evidence class and
immutable after loop close, and `CLAUDE.md` § Documentation governance grants exactly two
exceptions (`residues.md` and a gated cache), of which a spec is neither. So they are recorded
**here**, in the loop's own evidence, and in the handoff table above.

**Read plan §0 for the measurements. This is the index to it, not a substitute.**

| # | the spec says | the measured correction | consequence |
| --- | --- | --- | --- |
| **C1** | §2 Q5/Q6: the met set names **11** distinct artifact files | `prog:oracleArtifact`/`prog:oracleTest` are **multi-valued**; the 11 came from `Graph.value()` returning one object of many. Via `objects()`: **28** files | A3 and A6 are defined over **SETS** (refuse if the two ends share **any** test / **any** artifact file), not scalars. The assertable envelope moves: A4 non-strict + A3 + A6 = **130** ordered pairs, not the spec's 132 |
| **C2** | §4: group ablation worktrees by removed **file** — 11 of them | With 28 files that is worse, not better. Group by **criterion**: one worktree per endpoint criterion, all its artifacts removed at once | The bound is **endpoint criteria, ≤ 17**, whatever the edge count. The live leg came in at **6.69 s over 7 edges / 9 endpoints** |
| **C3** | §3: `prog:dependencyRationale xsd:string`, on propositions | A proposition is a plain triple; a literal on `X` cannot say **which** proposed edge it explains, and "exactly one" is unstatable for a criterion with two proposed targets | The rationale rides a standard `rdf:Statement` reification node **beside** the direct triple, so `(prog:dependsOn|prog:proposedDependsOn)+` — the property path §3's whole argument rests on — is untouched. M18 became a statement about those nodes |
| **C4** | §9.2: a refuted edge may be *"deleted or demoted with a rationale"* | **M17 forbids the demotion.** If the pair satisfies A1–A4+A6 — which it must have, or A5 never ran — a `prog:proposedDependsOn` between them is precisely what M17 refuses | **Deletion is the only membrane-legal outcome**, and the refutation is written into the loop's evidence, never into the graph. Exercised once, on `holon:02 → holon:01` |

Plan §0 also carries **C5**, which is not a correction but a measured **existence proof** that at
least one edge is groundable and that it is intra-rung — the risk the plan most needed to retire
(*"the ablation refutes everything and the asserted graph ships empty"*). `holon:03 → holon:01`
survived to close.

**What §0 does not change:** A4 stays non-strict, A6 stays, the two-predicate split stays, and
nothing in §0 weakens a refusal.

---

# §D The landscape is a cache, and it is regenerated BY HAND

`docs/superpowers/arc-dependency-landscape.md` is written by `scripts/arc_depends.py` and gated
by `tests/test_arc_landscape.py`, which regenerates it into a `tmp_path` and demands the tracked
bytes are **exactly** what the generator produces.

**Nothing regenerates it automatically.** Edit `tests/arc-manifest.ttl` and forget to run the
generator, and the next `pytest -q` goes **RED**, naming the first differing line:

```
docs/superpowers/arc-dependency-landscape.md has DRIFTED from its source at line 102:
  tracked:   '| `R44` | 6 |'
  regenerated: '| `R44` | 5 |'
This file is a generated cache, never hand-edited: run `./.venv/bin/python scripts/arc_depends.py`.
```

**That is the intended contract, not a rough edge, and it is what makes the file a cache rather
than a stored label.** `CLAUDE.md` § Documentation governance grants evidence-immutability's
second exception to *"a file written by a script from a committed source and gated by
regenerate-and-diff, so CI fails unless the tracked bytes are exactly what the source produces"*
— and says in the same sentence that **the gate is what earns the exception**: *"without it a
derived file committed here is a stored label, and is forbidden."* A silent auto-regeneration
would remove the drift signal and, with it, the exception. Ungated, this file must not exist.

Task 6's reviewer broke the gate deliberately (`| R44 | 5 |` → `6`) and it named line 102;
moving both the landscape and the generator away produced an `AssertionError`, not a collection
error, because the generator import is lazy inside the test body — a gate that ERRORs is a broken
test module, not a failing gate.

**Task 7 addendum.** `--out` was unconstrained, so `arc_depends.py --out tests/arc-manifest.ttl`
would have had this renderer overwrite the hand-authored source it had just parsed — contrary to
Global Constraint 4's letter (*code never writes `tests/arc-manifest.ttl`*, `arc-manifest.ttl:16-18`).
Misuse-only: the default path and every in-repo call site were correct. A hard constraint held by
an argparse default and by every call site happening to be right is held by nothing, so `main()`
now refuses an `--out` resolving to the manifest — the tracked one, or whichever file `--manifest`
named — and `test_the_generator_refuses_to_write_the_hand_authored_manifest` pins it.

---

# §E The definition-of-done audit — spec §10, item by item

Each item states the evidence. Anything not done is said plainly.

## §10.1 — all 43 criteria read for dependencies; every edge found authored at the grade the membrane permits

**MET.** `docs/superpowers/2026-08-22-arc-edges-authored.md` §1 is the full sweep: five reading
groups (A–E) over all 43 criteria, **29 readings**, plus **nine readings considered and rejected
with a stated reason** so a later author does not re-derive them. Result: **7 asserted authored →
1 refuted and deleted → 6 asserted surviving**, and **22 propositions**, each with exactly one
`rdf:Statement` rationale.

The grading is the membrane's, not taste: M17 refuses a proposition whose ends satisfy A1–A4+A6,
so an author cannot hedge a groundable edge down to a proposition. Task 4's reviewer re-measured
**all 22** propositions' stated failing preconditions and found them accurate, and closed M17's
one mechanical gap (A4's date filter) by enumerating the six met/met propositions, each of which
fails A3 or A6 substantively.

**Full-sweep evidence, and this is the one-directional argument for it:** the reading includes
edges the membrane can **never** ground — `holon:05/06`, `dec:02/12/13/15`, `substrate:03`, D1–D9,
all `met false` with zero `prog:oracleArtifact`. A reading filtered by the membrane first would
have the opposite shape.

## §10.2 — M12–M18 green, each with a fixture tripping EXACTLY ONE of them

**MET, and strengthened.** Shipped as **13** `sh:sparql` arms and **13** fixtures rather than the
plan's 7/7, because M16 is five constraints (one per precondition) and M18 is three: *a branch
reachable by no fixture cannot be falsified*. Task 2's implementer cut all 13 individually and all
13 went red; Task 2's **reviewer re-ran all 13 extracting which arm fired** and confirmed each
trips exactly one, nothing unreachable and nothing duplicated.

`_refused_by_shacl` asserts an **exact set** of distinct M-numbers, which is why 13 arms still
collapse correctly. The reviewer additionally proved M16/M17 **complementarity exhaustively** over
all 272 ordered pairs — M16-asserted fires iff M17-proposed does not, zero disagreements — and
confirmed no cycle escapes both M13 and M14 (2-cycle, 3-cycle, half-graded cycle, acyclic chain,
diamond, pure self-loop).

## §10.3 — M19 runs the two-sided ablation over every asserted edge and is green

**MET, and non-vacuous for the first time at Task 4.** `ablation_refusals(live manifest) == []`
over **6 edges / 9 endpoint criteria in 5.69 s** (reviewer's independent run; the implementer
measured 6.69 s over 7 edges before the refuted one was deleted), with worktrees really created
and the real tree `git status --porcelain` clean before and after.

The leg refuses rather than scores anything it did not see: a SKIPPED/XFAIL/XPASS oracle grounds
nothing and therefore refuses both arms; an unresolved node id **raises** with the transcript
rather than being guessed; a testless end is refused by a producer-side guard (CLAUDE.md § R89)
before arm 2 can go vacuously green.

**And it refuted something**, which spec §9.2 asks for explicitly: `holon:02 → holon:01`, arm 1 —
with `etkl-holons.ttl` removed, both of `holon:02`'s oracles still pass. Deleted, not demoted
(§C/C4). The refutation found a hole in the **oracle**, not an error in the reading → [[R117]].

## §10.4 — `arc-depends.rq` and `arc-ready.rq` return rows over the real manifest, and the answer is printed in the loop's evidence

**MET.** The three queries ship, `tests/test_arc_queries.py` grew 13 → 23 tests with
fixture-computed expectations recomputed in Python sharing no code with the `.rq` files, and the
live answer is printed in `docs/superpowers/arc-dependency-landscape.md` §1 (*what can be started
today*, 22 ready) and §2 (*what must land first*), and restated as this handoff's **one next
concrete action**: the next unmet criterion is **`etkl:02`** and **nothing
must land before it**; 22 of 26 unmet criteria are startable today; the only four with anything
in front of them are `etkl:03/05/06/07`, all waiting on `tab`, all through **proposed** edges.
**With the caveat recorded under *One next concrete action* above: 15 of those 22 — `etkl:02`
included — are ready through `arc-ready.rq`'s VACUOUS branch (no edge of either grade), and only
7 because a read dependency is met.**

`arc-reach.rq` — the spec's own cuttable item, **not cut** — ranks the frontier: **R44** and
**R62** gate five unmet criteria each; R97–R100 one each.

## §10.5 — the generated landscape is committed AND its regenerate-and-diff gate is green

**MET.** `docs/superpowers/arc-dependency-landscape.md` (122 lines) + `tests/test_arc_landscape.py`.
Two regenerations byte-identical to each other and to the tracked file; no clock, env or path read.
The reviewer broke the gate and it named the line; content spot-checked by **independent
recomputation** (6 asserted / 22 proposed / 28 edges, 43 criteria, 17 with a closure, 22 ready, 15
residues, R44=5 R62=5 R97–R100=1) — all match. The generator is the **one reader of record**: the
reviewer read it line by line and confirmed no closure walk, no grade decision and no reach count
is recomputed in Python. See §D for the hand-regeneration contract.

## §10.6 — §9's acyclicity result stated as a MEASUREMENT, whichever way it came out

**MET, and it is the loop's headline result.** Measured both ways, and it cuts both ways:

> **At CRITERION scope the graph is ACYCLIC. At RUNG scope the same edges carry a 2-cycle.**

```
$ ./.venv/bin/python  # depth-first cycle search over (prog:dependsOn | prog:proposedDependsOn)
CRITERION-SCOPE CYCLES: NONE — the graph is ACYCLIC
rung-level edges: {'dec': ['holon'], 'etkl': ['tab'], 'holon': ['dec'], 'substrate': ['dec']}
RUNG-SCOPE CYCLES: [['dec', 'holon', 'dec']]
```

M14 is green over the live manifest and `validate_manifest(MANIFEST)` returns `True`, so **no
cycle had to be resolved and nothing was split or deleted on acyclicity grounds**. Task 4's
reviewer reproduced the search byte-for-byte with an independent implementation. **There is no
unresolved cycle, so spec §9.1's residue row was not raised** — that is a measurement, not an
omission.

**The rung-scope cycle CONFIRMS decision 8 (rungs are unordered); it does not weaken it.** Spec §1
argued that decision 8 is *right at the wrong granularity*. The authored edges reproduce exactly
that shape one rung over: `dec:16 → holon:01` and `holon:04 → dec:07`/`dec:10` are **both
asserted** — grounded by ablation, not by reading. Projected onto rungs they contradict each
other; at criterion scope they do not touch. **Spec §1's argument, turned into a measurement.**

## What is NOT done — stated plainly

- **Nothing in spec §10 is unmet.** All six items are met, with the evidence above.
- **Seven residue rows were raised and none closed** — R113–R119, recorded in
  `docs/superpowers/residues.md` and `residues-open.md`. Three are limitations the spec named
  before the loop started (R113 file-granularity ablation, R114 the un-runnable oracle, R115 the
  orphan question); four are findings the loop's own instruments produced (R116 the M20 membrane
  gap, R117 the alignment-declaration gap, R118 arm-1 permissiveness on a collection ERROR, R119
  the undeclared `addopts` assumption). Two of them — R117 and R118 — exist only because the loop
  built something able to refute a claim.
- **Spec §8's list stayed unbuilt, deliberately**: the register is not mirrored into the graph,
  there is no rung-level ordering, the cockpit gained no line, no `prog:met` was touched, the 19
  artifact-less criteria were not given artifacts, and R106/M11, R108, R109's `split_pointer()`
  and R110 stay on the menu.
- **Four items are unverified or inferred rather than measured** — see §A's *Unverified or
  assumed*, which is not empty.

---

# §F Two process facts worth carrying, both paid for in this loop

1. **A written warning in a dispatch does not prevent a subagent backgrounding a long suite.**
   Two of two long-suite implementers did it despite an explicit line in the brief. The durable
   fix is a harness fact, not a prompt line: **a single Bash call caps at 600 s, so a ~36-minute
   suite needs chained foreground waits** (`caffeinate -dimsu -w <pid>`). This is the subagent-side
   face of the known controller-never-idles trap.
2. **A figure was written into a report inside the same heredoc that launched the command
   producing it** — i.e. before the run returned (`6 passed … 3.83s` written; `4 passed … 9.50s`
   returned). The implementer corrected it when the number came back and **left an annotated note
   rather than overwriting silently**, which is the right response and is to its credit. This is
   exactly the failure `CLAUDE.md` § Plan authoring rule 2 exists to catch, and it happened inside
   a report *about measuring things*. The controller's response — an extra audit mandate on the
   re-review — found no other such figure and reported **high confidence** in the file's numbers,
   on the grounds that they carry real transcript noise rather than clean recalled values.
