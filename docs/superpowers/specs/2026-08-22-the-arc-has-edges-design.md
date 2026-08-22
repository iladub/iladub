# The arc has edges — dependency at criterion scope, graded

**Date:** 2026-08-22 · **Tree:** `main` @ `fd6c81b` · **Topic:** process
· **Rows:** raises none at authoring time; §8 and §9 name the three it expects to raise

**Doc impact: increment.** One generated artifact enters the tracked tree (§6). No Assertion-class
page changes, no release-blocking contradiction. Whether the generated file needs a documentation
class of its own is §6's open sub-decision, and it is the one thing in this spec that may touch
`CLAUDE.md` — which is Contract-class and edited only on explicit request.

**Origin:** `docs/superpowers/2026-08-22-next-loop-handoff.md`, § CHOSEN DIRECTION. That handoff is
evidence-class; read it before this file. This spec does not restate its measurements — it cites
them, and §7 **contradicts one of its claims**.

---

## §1 The question

The maintainer, 2026-08-22: *"do we have a clear landscape of dependencies for building the full
architecture?"* The handoff's measured answer was **no, and deliberately so**.

`tests/arc-manifest.ttl` carries no dependency edge of any kind. Its predicate census (handoff,
§ CHOSEN DIRECTION): `ofRung` 44, `blockedBy` 11, and `precedes` appearing exactly once — inside a
comment saying it does not exist (`tests/arc-manifest.ttl:19-21`). The only edges in the graph are
criterion→rung and criterion→residue. **The arc is a scoreboard, not a graph.**

Decision 8 of the 2026-08-20 loop — *rungs are unordered* — is not wrong. It is **right at the
wrong granularity**, and that is this whole loop. At rung scope an ordering IS false: `etkl` needs
a minimal holon substrate to compile *into*, and the holarchy needs holons only `etkl` can produce,
so `etkl → holon` and `holon → etkl` are both true and the rung-level graph has a cycle. At
criterion scope the claim is smaller and checkable: *which* holon criteria does `etkl`'s next
criterion actually need.

**So the dependency edge belongs between CRITERIA, and this loop's first job is to establish
whether that graph is acyclic — not to assume it.**

---

## §2 What is measured before anything is designed

Five measurements were taken on `main` @ `fd6c81b` with `./.venv/bin/python` + rdflib 7.6.0 over
`tests/arc-manifest.ttl`. Every design decision below rests on one of them. They are reproduced
here as *facts about this tree*, and each is re-derivable by re-running the stated shape.

**Q1 — oracle coverage.** 43 criteria, 17 met. **All 17 met criteria carry a `prog:oracleArtifact`;
19 of 43 carry none, and every one of those 19 is unmet.** (Unmet-with-artifact: 7 — six `etkl`,
one `tab`.)

> Consequence: the handoff's candidate oracle — *"can X's oracle test pass with Y's artifact
> absent"* — is **structurally inapplicable to 19 of 43 criteria as dependency targets.** There is
> no artifact to remove. This is not a gap to close; it is the shape of the instrument, and §3
> is built around it rather than against it.

**Q2 — shared oracle tests.** Two groups of met criteria share one oracle test:

| criteria | shared `prog:oracleTest` |
| --- | --- |
| `dec:16`, `holon:03`, `holon:04` | `tests/test_hga_alignment.py::test_governed_grounding_conformant` |
| `dec:08`, `dec:10` | `tests/test_boundary.py::test_promotion_grounds` |

> Consequence, and it is the sharpest thing measured: **where the test is shared, ablation fails
> symmetrically.** Remove the shape file and the example's test fails; remove the example and the
> shape file's test fails — because it is the same test both times. **Ablation grounds adjacency,
> not direction.** The handoff's oracle, taken literally, cannot orient a single edge.

**Q3 — `metOn` clustering.** 10 distinct dates over 17 met criteria. `holon:01`, `holon:02`,
`holon:03`, `holon:04` **all carry `metOn 2026-06-23`**, as does `dec:16`.

> Consequence: a strict `metOn(Y) < metOn(X)` direction rule admits **zero** intra-`holon` edges.
> Within-rung edges are exactly where build order lives, so a date-based direction disposer would
> have produced a grounded inter-rung skeleton with every interesting edge demoted to a guess.
> This measurement is why §3's A4 is non-strict and why direction comes from §4 instead.

**Q4 — the assertable envelope.** Ordered pairs (X,Y) of met criteria with distinct oracle tests:
**122** under strict `metOn(Y) < metOn(X)`, **142** under non-strict `≤`. Intra-`holon`: **0**
strict, **10** non-strict. `dec:07` and `dec:10` (the earliest, 2026-05-31) can never be a source;
`tab:06` (the latest, 2026-08-20) can never be a target.

> Consequence: the grounded subgraph is not thin. 142 of 272 ordered pairs are *eligible* to be
> asserted if the reading says so — the membrane is a filter, not a wall. The two never-sources
> and one never-target are semantically right: the earliest things depend on nothing, and the
> newest thing gates nothing yet.

**Q5 — ablation cost.** The 17 met criteria name only **11 distinct artifact files**.

> Consequence: the ablation leg costs **11 worktrees, not two per edge.** One throwaway worktree
> per removed artifact, with every test that must be checked against that artifact's absence run
> inside it, amortizes the entire leg. This is what makes §4 affordable on every push.

**Q6 — shared artifact FILES, found by this spec's own self-review.** `prog:oracleArtifact` is a
`file:line` locator, but ablation can only remove a **file**. Ten met criteria share three files:

| file | criteria |
| --- | --- |
| `vocab/shapes/dec-shapes.ttl` | `dec:01`, `dec:03`, `dec:04`, `dec:05` |
| `vocab/shapes/iladub-shapes.ttl` | `dec:07`, `dec:08`, `dec:10` |
| `vocab/shapes/iladub-hga-shapes.ttl` | `dec:16`, `holon:03` |

> Consequence: where X and Y point into the **same file**, removing "Y's artifact" removes X's too,
> and arm 1 of the ablation fails for a reason that has nothing to do with the edge. This is A3's
> failure wearing a second face — shared *test* there, shared *file* here — and it is why §4 carries
> **A6**. Cost, measured: 142 → **132** assertable pairs; intra-`dec` 57 → 47; intra-`holon`
> unaffected at 10, because `holon:01`–`holon:04` name four distinct files.

*Reproduction:* each figure comes from parsing `tests/arc-manifest.ttl` with rdflib and reading
`prog:met`, `prog:metOn`, `prog:oracleTest`, `prog:oracleArtifact` off the 43 `prog:Criterion`
subjects. **The implementer must re-run these before authoring edges** — Q1 and Q4 move the moment
any criterion flips to met, and the envelope figures are a fact about `fd6c81b`, not a constant.

---

## §3 The vocabulary — two predicates, and why not one

`prog:` (`https://w3id.org/iladub/progress#`) is repo-internal and unpublished, exactly as `cor:`
and `dg:` are: not w3id-registered, never in `vocab/ontology/`.

```
prog:dependsOn          Criterion -> Criterion   ASSERTED
prog:proposedDependsOn  Criterion -> Criterion   PROPOSITION
prog:dependencyRationale                          xsd:string, on propositions only
```

Both predicates mean exactly the same thing: **X cannot be met while Y is unmet, and X's oracle
demonstrably consumes Y's artifact.** They differ only in whether that claim is grounded.

This is CLAUDE.md §3 turned on the arc itself: *assert only what you can ground, propose everything
else, and never let a proposition pass as an assertion.*

**Why two predicates and not one predicate with a grade property.** The grade must survive
transitive closure. A SPARQL property path cannot filter on a node property mid-path, so with a
single predicate `prog:dependsOn+` walks grounded and guessed edges indiscriminately and the
asserted closure is **uncomputable** — every derived "what must land before X" would silently mix
the two. With two predicates, `prog:dependsOn+` *is* the grounded closure, for free, and
`(prog:dependsOn|prog:proposedDependsOn)+` is the full one. This is the decisive argument and it is
the only reason the vocabulary carries two names for one relation.

**What is deliberately NOT stored.** There is **no `prog:ablation` record** — no literal recording
a command, an observed failure and a date. The CI leg of §4 *is* the grounding. A stored record of
a past run is a stored label for a derived fact, which CLAUDE.md forbids for `risk:RiskAssessment`
for the same reason: it is true on the day it is written and unfalsifiable afterwards.

---

## §4 What "asserted" costs — four membrane preconditions and one test leg

An edge may be `prog:dependsOn` only if all five hold.

| | precondition | where enforced |
| --- | --- | --- |
| **A1** | both ends `prog:met true` | membrane (M16) |
| **A2** | both ends carry `prog:oracleArtifact` and `prog:oracleTest` | membrane (M16) |
| **A3** | `oracleTest(X) ≠ oracleTest(Y)` | membrane (M16) |
| **A4** | `metOn(Y) ≤ metOn(X)`, **non-strict** | membrane (M16) |
| **A6** | X and Y name **different `oracleArtifact` files** | membrane (M16) |
| **A5** | the **two-sided ablation** passes | test leg (M19) |

**A3 is the Q2 refusal.** With a shared oracle test both ablations fail trivially and prove
nothing about either criterion in particular. Such a pair is not refused as an *edge* — it is
refused as an *assertion*, and becomes a proposition carrying a rationale.

**A4 is a sanity refusal, not the direction disposer.** It refuses only the contradiction: a target
met *after* the criterion that supposedly depended on it. Q3 is why it is non-strict — strict would
cost all 10 intra-`holon` edges to buy a direction rule that §4's A5 already provides better.

**A6 is the Q6 refusal, and it is A3's argument at file granularity.** The comparison is on the
file, with any `:line` suffix stripped: `vocab/shapes/dec-shapes.ttl:15` and
`vocab/shapes/dec-shapes.ttl:48` are the same artifact for ablation purposes, because ablation
deletes files.

> **A STATED LIMITATION, not a hidden one.** Even with A6, an asserted edge is grounded to **file
> granularity**: `X dependsOn dec:01` is demonstrated as *"X consumes `dec-shapes.ttl`"*, not as
> *"X consumes the shape at line 15"*. Where the target's file carries several criteria, the edge
> is true at file scope and under-determined at line scope. Line-granularity ablation — deleting the
> one Turtle block at that line — is the upgrade, and it is **out of scope** (§8); it ships as a
> residue row so the imprecision is on the register rather than in a footnote.

**A5, the two-sided ablation, is what grounds direction:**

- remove **Y's** artifact ⇒ **X's** oracle test must **FAIL** — X consumes Y
- remove **X's** artifact ⇒ **Y's** oracle test must **PASS** — Y does not consume X

Both arms are required. One arm alone establishes coupling; the pair establishes *which way round*,
with no appeal to dates, wherever A3 holds. If **both** arms fail, the coupling is symmetric: that
is not a dependency, and the edge is refuted rather than demoted.

**How A5 runs.** A throwaway `git worktree` per removed artifact (Q5: 11 of them for the current
met set), the artifact deleted inside the worktree only, `cwd` in the worktree, the interpreter the
repo's own `.venv/bin/python` — which is an absolute path and therefore unaffected by the worktree.
The real tree is never mutated, so a crashed subprocess cannot leave the repo broken. Tests are
grouped by removed artifact, never run per-edge.

**There is no precedent for this in the repo, and that is measured, not assumed.** `worktree`,
`pytest.main` and `shutil.copytree` return **zero hits** across `tests/`, `scripts/`, `.github/`.
The three nearest precedents, and each supplies one half of what M19 needs:

- `tests/test_arc_manifest.py:207-209` — `subprocess.run([sys.executable, "-m", "pytest",
  "--collect-only", "-q"], cwd=REPO, …)`. Subprocess pytest, but `--collect-only` and against the
  **live** tree.
- `tests/test_docgov_extract.py:83-86` — `git clone --depth 1 file://{repo}` into `tmp_path`. The
  only test that materializes a second copy of the tree; it runs no pytest inside it.
- `tests/test_release_gate.py:46-50` — a synthetic git repo built in `tmp_path`.

So M19 is the first test in this repo to run a real pytest inside a second checkout. That is a
reason to measure the seam, not a reason to avoid it.

> **MEASURE BEFORE WRITING THE RUNNER, do not assume:** whether every oracle test named by a met
> criterion actually resolves and passes when run with `cwd` inside a bare `git worktree` that has
> no `.venv` of its own. The interpreter is absolute; the *fixtures and data paths* are the seam,
> and `tests/test_docgov_extract.py:83-88` proves the repo already has one tool that **refuses** a
> shallow second checkout — so "a second copy behaves like the first" is exactly the assumption
> this repo has already been bitten by. Establish it for all 11 artifacts before designing the
> grouping, and report the answer. If some oracle cannot run in a worktree, that is a finding about
> the oracle, not a reason to weaken A5.

---

## §5 Refusals — M12 to M19

Numbering continues the existing M1–M10 (`tests/arc-shapes.ttl`, `tests/test_arc_manifest.py`).
**M11 is not free** — it is reserved for R106's non-vacuity rule. MEASURED 2026-08-22:
`grep -rn '\bM11\b' src/ tests/ scripts/ vocab/ baml_src/` returns **0 hits**; all 10 hits in the
tree are prose in `docs/superpowers/*.md`, and the fixture set stops at
`tests/arc-m10-stale-source-pointer-leak.ttl`. R106 is **open** (`docs/superpowers/residues.md:188`).
So M11 exists as a reserved number and nothing else — do not reuse it.

| | refusal |
| --- | --- |
| **M12** | a dependency target, either grade, must be a declared `prog:Criterion` IRI. Unlike `prog:blockedBy` — whose values are plain string literals into a markdown register that is not in the graph at all (`vocab/queries/arc-orphan.rq` header) — this edge is **in** the graph, so dangling is checkable and is refused |
| **M13** | no self-edge, either grade |
| **M14** | **acyclicity** — no `(prog:dependsOn\|prog:proposedDependsOn)+` returns to its own subject |
| **M15** | a **met** criterion may not depend, either grade, on an **unmet** one. The analogue of M8, and the cheapest catcher of a reversed edge |
| **M16** | `prog:dependsOn` requires A1–A4 **and A6** |
| **M17** | **a proposition may not hide a groundable edge** — a `prog:proposedDependsOn` whose ends satisfy A1–A4 and A6 is refused |
| **M18** | a `prog:proposedDependsOn` carries exactly one `prog:dependencyRationale`; a `prog:dependsOn` carries none |
| **M19** | the two-sided ablation of A5, for every `prog:dependsOn`. **Test leg, not SHACL** — it asks about the filesystem and a pytest exit code, neither of which is a triple |

M12–M18 are AXIOM / constraint, closed world, in `tests/arc-shapes.ttl`: a membrane over one
hand-authored file. M19 is irreducibly PROCEDURAL — worktree creation, file removal and subprocess
exit codes — and must say so in its own docstring, per CLAUDE.md §8.

**M17 is the forcing function of this spec.** It makes *"propose it and move on"* unavailable
wherever grounding is possible. An author who believes X depends on Y, with both ends met and
distinct oracles and distinct artifact files, must assert it — and CI then **refutes** the reading if it was wrong. Without
M17 the proposition grade becomes a place to hide, and the two-predicate split buys nothing.

**M14 duplicates nothing and is not optional.** M15 refuses one *local* inconsistency; a cycle is
a *global* one and no local rule sees it.

---

## §6 The monitor

**`vocab/queries/arc-depends.rq` is the reader of record.** AXIOM / derivation, OPEN WORLD. Given
a criterion bound by the caller — the shape `vocab/queries/arc-orphan.rq` already established, and
for the same reason — it returns the transitive set that must land first, **grade-labelled**, with
the asserted closure (`prog:dependsOn+`) and the full closure reported separately so a reader can
see where the chain stops being grounded.

**`vocab/queries/arc-ready.rq`** — unmet criteria whose **direct** dependencies are all met. This
is the "what can actually be started" question, and it is *not* `arc-unblocked.rq`: that one knows
only about register rows, this one knows only about criteria, and a criterion can easily be one and
not the other.

> **Direct, not transitive, and this is a §8 decision rather than a convenience.** A `FILTER NOT
> EXISTS` over one node's own outgoing edges closes over that node — the holon-scoped closure
> `arc-unblocked.rq` already argues for. A `NOT EXISTS` over a whole transitive cone closes over a
> *chain*, which is a larger closure claim, and I do not think CLAUDE.md §8 licenses it without an
> argument nobody has made. Transitive readiness follows by iterating the direct query anyway.

**`vocab/queries/arc-reach.rq`** — for a residue named in `prog:blockedBy`, how many criteria its
closure eventually gates. **This is the cuttable one** if the loop runs long. It is also the payoff:
it upgrades `frontier 15` from an adjacency count to a ranking, because *closing R99 unblocks
`tab:07` which gates `tab:09`* is a strategy statement and *"R99 blocks one criterion"* is not.

**The generated landscape.** `scripts/arc_depends.py` renders the graph to a committed markdown
file, gated by **regenerate-and-diff**: CI regenerates and fails unless the tracked file is
byte-identical. That gate is the whole argument for committing a derived artifact at all — it makes
the file a **cache** that cannot drift, rather than the stored label CLAUDE.md forbids. Without the
gate this file must not exist.

**The cockpit is NOT touched.** `scripts/cockpit.py` reads the manifest with a regex under a
performance contract that forbids rdflib (`cockpit.py:76-80`), and a regex cannot compute
transitive closure. Teaching it a derived depth would mean reading a precomputed number out of the
generated file — a second reader of a derived fact, which is the M9/M9b defect-generator again.

### Where the generated file lives — MEASURED 2026-08-22, and it needs one maintainer decision

Documentation class is decided **by path prefix, not frontmatter** (`tests/docgov_extract.py:36-51`,
`classify()`, most-specific-first). The rules that bear on a generated file:

| finding | measurement |
| --- | --- |
| `docs/superpowers/**` → class `evidence` | `docgov_extract.py:27,47-48` (`EVIDENCE_DIRS`) |
| evidence carries **no** frontmatter obligation | `_evidence_facts` returns immediately for any non-dated path, `docgov_extract.py:178-186` |
| a **dated** file under `specs/`|`plans/` triggers the `Doc impact:` requirement | `_DATED` at `docgov_extract.py:91`; `dg:DocImpactShape` at `vocab/shapes/doc-governance-shapes.ttl:123-136` |
| **there is no immutability check anywhere in code** | grep of `tests/ scripts/ .github/` for `immutab\|append-only\|read-only\|frozen` finds only prose at `CLAUDE.md:419-421`. `docgov_extract.py:116-121 last_commit_date` is used solely for *staleness of cited sources*, never to forbid a change |
| `docs/wiki/**` demands `title`, `type ∈ {concept,source,index}`, **`confidence ∈ {high,medium,low}`**, `updated` (xsd:date), ≥1 `sources:` entry, **and** a hand-written row in `docs/wiki/index.md` | `doc-governance-shapes.ttl:74-96`, `:140-148` |
| `mkdocs.yml:40-44` already excludes `superpowers/` and `wiki/` from the site | — |

**The decision: `docs/superpowers/arc-dependency-landscape.md` — undated, not under `specs/` or
`plans/`.** It classifies as `evidence`, is already excluded from the site, and trips **no** test:
no frontmatter, no index row, no staleness query, no `Doc impact:` block.

**`docs/wiki/` is rejected on epistemics, not on cost.** The generator could emit every field the
shape wants. But a wiki page is specified as a *proposition* — confidence-tagged, freely rewritten
— and this file is a **derivation**. Putting a `confidence: high` tag on a SPARQL result is
asserting a grade the artifact does not have, which is the precise error CLAUDE.md §3 exists to
prevent. A cheaper wrong answer is still the wrong answer.

**And there are two exemption holes that must NOT be used.** `docgov_extract.py:31-33` exempts
`.claude/`, `.agents/` and **any path ending `.databook.md`** from classification entirely, and
`:108-113` only ever sees `*.md`, so a `.txt` rendering is invisible to governance. Both would let
this file escape the membrane rather than satisfy it. Naming them here so that a later reader knows
they were seen and declined.

**THE ONE THING THAT IS NOT THE IMPLEMENTER'S CALL.** Nothing in code forbids a regenerated evidence
file — but `CLAUDE.md:419-421` says evidence is *"immutable after loop close"*, and a
regenerate-and-diff cache is by construction not immutable. **The contract already carries an
exception of exactly this shape** in the same sentence: *"`residues.md` is the mutable register."*
So the honest resolution is a second entry beside it — one clause naming generated caches, gated by
regenerate-and-diff, as likewise mutable.

`CLAUDE.md` is **Contract-class, edited only on explicit request.** The implementer must therefore
**stop and ask the maintainer** for that clause before committing the generated file. If the answer
is no, the generated landscape does not ship and §6 reduces to the three queries — which is a
legitimate outcome, not a blocked loop. **Do not edit `CLAUDE.md` without that answer, and do not
route around it via the `.databook.md` exemption.**

---

## §7 A correction to the origin handoff — the 80% question is NOT subsumed

The handoff claims this loop subsumes its candidate 1 (**59 of 74 open register rows block no
criterion of any rung**), on the reasoning that those rows *"have nowhere to attach today because
there is no edge type that would carry them."*

**That does not survive.** A **criterion→criterion** edge gives a *residue* nowhere new to attach.
An orphan row still blocks no criterion, `prog:blockedBy` is untouched by this spec, and
`vocab/queries/arc-orphan.rq` will return the same set the day this ships as it does today. The
edge type this loop adds is between criteria; the orphan problem is about residues.

What the graph *does* buy is **reach** (`arc-reach.rq`): a blocker gains a ranked consequence
instead of a count. That is worth having and it is a different claim.

**So the 80% question stays open**, and is recorded here rather than left for the next handoff to
inherit as settled. *(The 59/74 figure is quoted from the origin handoff and was **not** re-measured
for this spec.)*

---

## §8 What this loop does NOT do

- **The register is not mirrored into the graph.** `prog:blockedBy` stays plain string literals and
  M7 keeps reading `residues.md` procedurally. `arc-orphan.rq`'s rejected alternative — mirror the
  register into triples — stays rejected, for the reason its own header gives.
- **No rung-level ordering.** Decision 8 stands as written. There is still no `prog:precedes` and no
  index property between rungs. This loop asserts order **only between criteria**, which is a
  strictly smaller claim, and §1 is the argument that the smaller claim is the true one.
- **The cockpit gains no line.** §6.
- **No criterion's `prog:met` is touched.** Code never writes the manifest (`arc-manifest.ttl:16-18`).
  A dependency edge is a claim about order, never about doneness.
- **R106/M11, R108, R109's `split_pointer()`, R110** stay on the menu behind this.
- **Ablation stays at file granularity.** Q6/A6 bound the imprecision rather than remove it.
  Line-granularity ablation is a named residue, not a stretch goal.
- **The 19 artifact-less criteria are not given artifacts.** Q1 is a fact about where grounding is
  possible, and inventing an artifact to make an edge assertable would be marking our own homework.

---

## §9 The falsifying oracle, and what a failure looks like

**The loop's own claim is: *the criterion-scope dependency graph is acyclic, and the part of it that
can be grounded, is*.** Three things falsify it, and each is a **result**, not a defeat:

1. **M14 trips.** The authored graph has a cycle at criterion scope. This is the finding §1 refuses
   to assume away. It is resolved by splitting a criterion doing two jobs, or by deleting the weaker
   direction — **never by relaxing M14**. An unresolved cycle ships as a residue row with the cycle
   printed in it.
2. **A5 refutes an authored edge.** The reading was wrong. Delete the edge or demote it with a
   rationale saying what the ablation showed. Expect this; it is the disposer doing its job, and a
   loop where A5 refutes nothing should be suspected of having authored only safe edges.
3. **An oracle cannot run in a worktree** (§4's MEASURE box). That is a finding about that oracle's
   hidden dependence on the working tree, and it is worth a residue row of its own.

**Proposer and disposer are independent, which is the point.** The edges are authored by *reading*
what a criterion needs. They are disposed by *running a test with a file deleted*. Neither reading
can rescue the other, and no edge is asserted on the strength of the reading alone.

**Per-task falsification is mandatory** (CLAUDE.md § Plan authoring, rule 4): every task report
carries a block showing the new test **failing** with its subject removed or inverted, then green.
For M19 specifically, the falsification is pointed: **assert an edge that is false** — pick two met
criteria with distinct oracles and no real relation — and show M19 catching it.

---

## §10 Definition of done

The loop closes when, on real input and not a fixture:

1. All 43 criteria have been read for dependencies, and every edge found is authored at the grade
   the membrane permits — full sweep, because a partial dependency graph answers the maintainer's
   question with a partial landscape, which is the one thing it must not do.
2. M12–M18 are green in `tests/arc-shapes.ttl` + `tests/test_arc_manifest.py`, each with a fixture
   tripping **exactly one** of them — the discipline the existing membrane already holds itself to.
3. M19 runs the two-sided ablation over every asserted edge and is green.
4. `arc-depends.rq` and `arc-ready.rq` return rows over the real manifest, and the answer to
   *"what must land before the next unmet criterion"* is printed in the loop's evidence.
5. **Either** the generated landscape is committed with its regenerate-and-diff gate green **or**
   §6's `CLAUDE.md` clause was declined and the loop ships the three queries without it — stated
   explicitly, either way. A loop that quietly drops the landscape has not closed.
6. §9's acyclicity result is stated as a **measured** answer, whichever way it came out.
