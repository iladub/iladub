# The arc has a denominator — slice 1 of the strategy instrument

**Date:** 2026-08-20 · **Tree:** `main` @ `4774f43` (plus the narrative edit this loop makes first)
· **Topic:** process · **Rows:** raises none; repairs the register's own stale prose

**Doc impact: increment.** One Assertion-class change — `docs/narrative/scope-evolution.md` gains a
fifth **named** rung (`tab`) and drops the numbering from all five. No release-blocking
contradiction. The wiki gains nothing this loop.

**Origin:** `docs/superpowers/2026-08-20-strategy-instrument-brief.md` (the maintainer's words) and
`docs/superpowers/2026-08-20-strategy-instrument-handoff.md` (the design, the measurements, and the
eight decisions). **Both are evidence-class; read the handoff before this file.** This spec does not
restate its measurements — it cites them.

---

## §1 The question

The maintainer: *"I have no notion of how complete the topic/epic we are working on is … Here I am
blind."* The cockpit strip (`scripts/cockpit.py`, wired as `statusLine`) answered the *rhythm* half
— closed/total, 7-day raised/closed, days idle — and left the *completeness* half printing `?/4`,
which its own docstring calls the honest answer and the point of the gauge (`cockpit.py:16-19`).

`?` is honest because **no artifact in the repo carries state about the arc.** `arc()` at
`cockpit.py:134-139` counts `^### ` headings in `scope-evolution.md` and returns `None` for the
position, with the instruction *"when an objectives artifact gains state, teach this to read it."*

This loop builds that artifact. The question it must answer is not *"which rung are we on"* — that
question was refuted (§2, decision 5) — but **"of what this project set out to do, what is done,
what is not, and which open residue stands between the two."**

## §2 What is already decided, and is not re-opened here

The eight decisions are recorded in the handoff § *What was decided*, **nowhere else**, and are the
maintainer's live answers. They are inputs to this spec, not its conclusions. In force:

1. Map → trend → selection, in that order, as **one thin vertical slice** — not three layers.
2. The surface is the **cockpit strip**, not a session-start block.
3. A rung gets state by **ASSERT + MEMBRANE**: a tracked TTL asserts, a SPARQL/SHACL membrane over
   evidence must support the assertion or refuse it.
4. Slice 1 = **map + dependency edges**. Persisted tally history is deferred.
5. The position is **five fractions, not one integer**. `stage 3/5` would have to be wrong about
   four rungs to be right about one.
6. Rendered as **bars**, keeping two rules: **unknown ≠ zero** (no criteria ⇒ `?`, never an empty
   bar) and **the fill can go down**.
7. Table-reading is a **fifth rung**.
8. Rungs are **named, never numbered** — `etkl · dec · holon · tab · substrate`. A number is an
   ordering claim, and `tab` is not entitled to one: it is depth inside `etkl`, not a stage after
   `substrate`.

## §3 The model

`prog:` (`https://w3id.org/iladub/progress#`) is **repo-internal and unpublished**, exactly as `dg:`
and `cor:` are. It is not w3id-registered and never appears in `vocab/ontology/`.

Three node types, and no more:

- **`prog:Rung`** — one of the five names. Carries `rdfs:label`, `prog:rungKey` (the strip's word),
  and its criteria. **Rungs are unordered.** No `prog:precedes`, no index: decision 8 forbids the
  repo from asserting an ordering that is false for one of the five.
- **`prog:Criterion`** — one countable thing that would have to be true for the rung to be done.
  Carries `prog:statement` (prose), `prog:declaredOn` (date), `prog:met` (boolean, **asserted**),
  `prog:metOn` (date, present iff met), `prog:retrospective` (boolean, required), and its oracle.
- **`prog:Oracle`** — how "met" is checkable by someone who does not trust the assertion:
  `prog:oracleArtifact` (a repo-relative path) and `prog:oracleTest` (a pytest node id,
  `path::function`). An unmet criterion may name a *target* oracle that does not exist yet; a met
  one may not.

### §3.1 Why `met` is asserted rather than derived, and why that is not a mirror

The cockpit's performance contract (`cockpit.py:34-38`) forbids rdflib, pytest and the corpus. So
the strip cannot derive met-ness at render time; it must read an assertion. That is decision 3's
real reason, and the honesty is restored on the other side: **the membrane refuses an assertion the
evidence does not support** (§4), and a test pins the strip's reading equal to the graph's (§6).

**The oracle greenness comes free, and this is the load-bearing simplification.** A criterion's
oracle is a node id *in this repo's own suite*. If CI is green, every oracle is green — so the
membrane never needs to run them. It needs only to check that the node id is **collectable**, which
is one cheap `pytest --collect-only -q` for the whole set.

### §3.2 `prog:declaredOn` must precede the claim — and the retroactivity that clause cannot survive

The design's sharpest idea (handoff § *The design as it stood*): the same hand authors the criteria
and the position, so they are not independent by construction; dates are what make them independent.
**You must say what done means before you may claim it.**

Applied literally the clause is unsatisfiable today: every rung already reached was reached before
any criterion was declared, and the handoff flags this under § *Unverified or assumed* as *"not
thought through."* Thinking it through gives the honest form:

> **`prog:retrospective` is required on every criterion.** `true` means the criterion was written
> after the evidence it points at already existed — the fraction it contributes is an
> **adjudication**, not an independent measurement. `false` means it was declared before, and its
> later met-ness is real evidence.

The membrane enforces the clause **going forward** rather than pretending about the past: a
criterion whose `prog:metOn` equals its `prog:declaredOn` MUST be `prog:retrospective true`.
Grandfathering is thereby *labelled*, not hidden, and every criterion declared unmet today becomes
a genuine measurement the moment it flips. **This is the spec's one substantive addition to the
handoff's design**, and it is the clause most worth attacking.

### §3.3 The edge that makes selection strategic

The load-bearing edge is **residue → criterion → rung**, not residue → residue. `prog:blockedBy`
points from a criterion to a residue row (`R43`, `R99`, …). That is what lets a query say *closing
R99 matters because it unblocks a criterion of the `dec` rung* — adjacency becomes strategy.

Residue→residue edges are the smaller, separate job: dependency prose exists in **7 rows**, measured
2026-08-20 by

```
grep -n -i -e "depends on" -e "blocked by" -e "unblock" -e "inherits R" -e "coupling" \
  docs/superpowers/residues-open.md docs/superpowers/residues-closed.md
```

→ `residues-closed.md:11 R4`, `:26 R102`, `:28 R87`; `residues-open.md:18 R14`, `:46 R51`,
`:73 R89`, `:76 R96`. The handoff's own count was 6 under a different pattern; **the plan MEASURES
the set again and states its command** — the two patterns disagreeing is exactly the kind of claim
rule 2 exists for. Either way the backfill is single digits, not 94.

## §4 The membrane (closed world — SHACL, `tests/arc-shapes.ttl`)

Per CLAUDE.md §8 the membrane validates what crossed; it never derives. It refuses:

| # | refusal | why |
| --- | --- | --- |
| M1 | a `prog:Criterion` without exactly one `prog:declaredOn`, one `prog:statement`, one `prog:met`, one `prog:retrospective` | a criterion with no declaration date cannot participate in §3.2 at all |
| M2 | `prog:met true` without `prog:metOn` | a claim with no date is not auditable |
| M3 | `prog:metOn` earlier than `prog:declaredOn` | met before it was defined |
| M4 | `prog:metOn` **equal to** `prog:declaredOn` while `prog:retrospective false` | §3.2 — grandfathering must be labelled |
| M5 | `prog:met true` whose oracle artifact does not exist, or whose `prog:oracleTest` is not collectable | the assertion the cockpit reads must be checkable |
| M6 | a `prog:Rung` whose `prog:rungKey` is not one of the five settled names | decision 8's labels are settled, and a sixth rung is a decision, not an edit |
| M7 | a `prog:blockedBy` naming a residue row that does not exist in the index | a dangling edge is worse than no edge |
| M8 | `prog:blockedBy` on a criterion that is `prog:met true` | a met criterion is not blocked; this catches the stalest kind of row |

**A rung with zero criteria is NOT a refusal.** It renders `?`. Unknown ≠ zero (decision 6).

## §5 The derivations (open world — SPARQL, `vocab/queries/arc-*.rq`)

Evidence-positive and monotone; nothing inferred from absence except query-local `NOT EXISTS`,
which closes only within one rung (CLAUDE.md §8's holon-scoped closure).

- **`arc-position.rq`** — per rung, `(met, declared)`. The denominator that was missing.
- **`arc-frontier.rq`** — the open residues that block an unmet criterion of some rung, with the
  rung and criterion they block. This is *selection*: it names what to do next and says why.
- **`arc-unblocked.rq`** — criteria whose every `prog:blockedBy` row is now closed. A criterion that
  nothing blocks any more, and is still unmet, is work that is ready and is not being done. This is
  the query the maintainer's original complaint most directly asks for.
- **`arc-orphan.rq`** — open residues that block no criterion of any rung. A row serving no rung is
  either mis-filed or is work no stated goal requires; either answer is worth having, and R101 is
  the measured first instance (§7.4). Closed-world *within* the query (`NOT EXISTS` over
  `prog:blockedBy`), which is holon-scoped and legitimate; it derives nothing about the residue
  itself.

The fifth derivation someone will ask for — *"are we going faster?"* — is **not** built. Decision 4;
see §9.

## §6 The surface

```
arc  etkl ▰▱▱▱ 1/7  dec ▰▰▰▱ 10/16  holon ▰▰▰▱ 4/6  tab ?  substrate ▱▱▱▱ 0/3
```

**These are the measured figures from §7, not an illustration** — except `tab`, whose numerator is
genuinely unmeasured until the corpus run (§7.4's seam). `tab` therefore renders **`?`**, which is
decision 6's *unknown ≠ zero* doing exactly the work it was written for, on the largest rung in the
repo. **A criterion may not be authored without its met-value measured**, so the corpus run is on
the plan's critical path, not an optional extra: authoring `tab` rows from the register alone would
put a fabricated numerator on the strip.

Note what the strip now says out loud: **`dec` and `holon` are the strong rungs and `etkl` is 1/7**,
which inverts the assumption that the compiler is the finished part and the vocabulary the thin one. The fraction sits beside each bar — the handoff left
that to this session (decision 6), and it is required: a bar reads as a percentage and these are
checklists.

**Measured constraint, 2026-08-20 — the handoff under-counted it.** The handoff estimated ~70
characters for the bars. Measured:

```
$ python3 scripts/cockpit.py --no-color --refresh </dev/null | awk '{print length($0)}'
169                                   # the strip TODAY, before any arc gauge
$ python3 -c "print(len('arc  etkl ▰▰▰▱ 3/4  dec ▰▰▰▰ 4/4  holon ▰▰▱▱ 2/4  tab ▰▱▱▱ 1/6  substrate ▱▱▱▱ 0/3'))"
82                                    # the arc segment alone
$ tput cols
80
```

251 characters on an 80-column terminal. **The strip already wraps at 169**, so width is not a hard
gate — but appending the arc nearly doubles it, and a wrapped gauge strip is the blindness it was
built to cure.

**The seam the plan must measure before choosing** (rule 3 — this is the fact to establish, not the
answer): *does the harness render a multi-line `statusLine`?* The existing test
`tests/test_cockpit.py:54` pins **exactly one** line of stdout, so a two-line strip is a deliberate
change to that test with its reason recorded — not a silent relaxation. If multi-line does not
render, the fallback is the compact form (bars without fractions, ~50 chars) and the fractions move
to `--verbose`; the fallback must NOT be abbreviating the rung names, which are settled (decision 8).

**Also measured, and it is the coupling working:** the narrative edit this loop makes first
(`scope-evolution.md` gains the `tab` heading) moved the strip from `stage ?/4` to `stage ?/5`
immediately, because `arc()` counts `^### ` in that file. The denominator already tracks the prose.
The numerator is what this loop adds.

`arc()` becomes a cheap regex read of the manifest — no rdflib (`cockpit.py:34-38`). Two tests hold
it honest:

1. **The agreement test**: the strip's reading and rdflib's reading of the same file must be equal.
   Drift between the fast reader and the authority is a failure. *This test would have caught the
   `residues()` regex defect on the day it shipped* (fixed since, `8bd3120`).
2. **The honesty test survives intact**: `tests/test_cockpit.py:22` must still pass in substance —
   delete the manifest and the gauge returns to `?`, never a guess. Its literal assertion
   (`"stage ?/" in …`) changes with the label; **the assertion that must not weaken is that a
   missing source yields `?` and never a number.**

The `▸` slot changes from the newest handoff's filename to the **frontier** — the residue
`arc-frontier.rq` names. Fall back to the filename when the frontier is empty.

## §7 The criteria — the actual denominators

**The finding that retires this loop's biggest unknown: the denominators already exist, in prose.**
**Four of five rungs** carry a countable criterion set written *before* any claim about it — the
independence §3.2 was invented to manufacture, obtained for free. The handoff said three; `dec`'s
was found in `CLAUDE.md` itself (§7.2). The work is **lifting prose into countable form**, not
inventing criteria. Only `tab` had to be constructed, and §7.4 says how and why it could not simply
be read off the register.

**`etkl` and `tab` do not double-count, and the distinction is the reason `tab` is a rung at all.**
`etkl` counts **documents** that reach an adjudicated verdict against a contract — the pipeline end
to end. `tab` counts **reading-refusal reasons** that are adjudicated — whether the author's
structure was recovered, independent of whether anything downstream conformed. A document can
compile above its floor while three reading reasons fire on it; `etkl` scores that as met and `tab`
does not.

**The dating rule, and the seam the plan must measure.** `prog:declaredOn` is **the commit date of
the line of prose that declares the criterion** — not the date this loop wrote it down. That is what
makes three of the five rungs non-retrospective. **MEASURE it per criterion** (`git log -L` or
`git blame` on the declaring line); do not take the file's creation date, and do not assume a
section is as old as its file. `docs/holonic-interaction.md` was created 2026-06-02 and
`tests/corpus-manifest.ttl` 2026-08-02 (`git log --diff-filter=A --format=%ad --date=short -- <path>`,
run 2026-08-20), but the individual bullets and entries landed later.

### §7.1 `etkl` — 1 of 7

Source: `tests/corpus-manifest.ttl` (115 lines), which declared the denominator on 2026-08-02 and
has been untouched for 16 days. **One criterion per corpus document:**

> *this document compiles via `compile_document` to `cor:CompilesAbove` with a pinned
> `cor:scoreFloor`, under a `cor:adjudication` whose rationale **accepts** that score — not one that
> holds it.*

**CORRECTED 2026-08-20, on the maintainer's challenge, and the earlier wording is kept here because
the defect is instructive.** It read *"an adjudicated verdict, with a pinned `cor:scoreFloor` the
corpus battery holds"* — which is **gameable, and in the worst direction**. A floor is a regression
guard, so nothing stops it being pinned at whatever the document scores today: `bfs` at 0.3438,
`ons` at 0.4419. Six such lines would take this rung from 1/7 to **7/7 without a single reading
improving**. That is not fraud, it is worse — it is a criterion that rewards *writing the number
down*, and `[[no-overfitting-general-fixes]]`'s standing rule (never lower a bar to meet it; honest
failure beats fake success) is aimed at exactly this shape.

**The distinction is already in the `cor:` vocabulary and costs nothing to adopt.** From the
manifest's own header (`tests/corpus-manifest.ttl:16-20`): *"There is no separate `cor:Hold` term: a
HOLD is encoded AS `cor:Unadjudicated` plus a `cor:adjudication` node carrying the reviewer's
rationale — the hold state is 'unadjudicated, with a recorded reason,' not a fourth verdict value."*

So the manifest can already say three different things, and the rung must count only the first:

| manifest state | meaning | counts as met |
| --- | --- | --- |
| `cor:CompilesAbove` + `cor:scoreFloor` + an accepting `cor:adjudication` | the reading is good enough, and someone said so and why | **yes** |
| `cor:Unadjudicated` + a `cor:adjudication` | **recorded HOLD** — measured, reasoned, and explicitly not accepted | no |
| `cor:Unadjudicated`, bare | nobody has looked | no |

Rows 2 and 3 both score zero, and **that is not the same as being indistinguishable**: today all six
non-stem documents are in row 3, and after the plan's adjudication pass they should all be in row 2.
The fraction will not move, and the register of what is *known* about this rung will have moved a
long way. **Whether the strip should show that difference is a render question the plan may raise;
the manifest must record it either way.**

Measured 2026-08-20: **7 `cor:Document` entries; 1 carries a `cor:scoreFloor` and an adjudicated
verdict** (`graincorp-stem-2026-07-31`, floor `0.95`, achieved 0.9655). The other **6 are
`cor:Unadjudicated`**.

`graincorp-stem` is the model's proof case and is **`retrospective false`**: declared into the
manifest 2026-08-02, adjudicated (HOLD lifted) 2026-08-03 — `declaredOn < metOn`, with the
intervening HOLD recorded in `cor:adjudication`. The denominator moved before the numerator did, and
it moved *through* row 2 of the table above, which is the corrected criterion's whole point: the one
met document is met because a HOLD was **lifted**, not because a number was written down.

**This denominator grows with ambition, and that is correct.** Adding a document to the corpus
lowers the fraction. A gauge that can only be lowered by aiming higher is measuring the right thing.

### §7.2 `dec` — 10 of 16, and the denominator was there all along

**The handoff is corrected here.** It says (§ *The denominators mostly already exist*) that *"rung 2
has no declared denominator anywhere … the most complete rung is the one that cannot yet say so."*
Measured 2026-08-20: **it has one, and it is in `CLAUDE.md` itself** —
`CLAUDE.md:252`: *"Every vocabulary/shape ships with a worked example that conforms **and** a
negative test that must fail."*

That is a countable rule, declared in the **Contract** class, predating every shape it governs — the
strongest possible `retrospective false` denominator, and nobody had counted it.

**Measured: 15 shapes across `dec:` / `risk:` / `iladub:` / `gsh:`; 10 carry BOTH halves; 5 are
positive-only** — `dec:ConfidenceShape` (`dec-shapes.ttl:38`), `risk:RiskAssessmentShape`
(`risk-shapes.ttl:35`), `risk:SensitivityShape` (`:49`), `gsh:PermissionShape`
(`governance-shapes.ttl:45`), `iladub:PromotionDecisionShape` (`iladub-shapes.ttl:53`). Each of the
five is one unmet criterion with a named oracle target: *a negative fixture that trips this shape.*

**A sixteenth criterion, and it is a real hole.** `CLAUDE.md:249-251` requires provenance reuse —
`dec:DecisionHolon ⊑ prov:Activity`, `dec:consideredEvidence ⊑ prov:used`, `dec:decidedBy ⊑
prov:wasAssociatedWith`, `dec:produced ⊑ prov:generated`, declared at `vocab/ontology/dec.ttl:38,55,
72,85`. **No test asserts any of the four** (`grep -rn "Activity" tests --include="*.py"` → 0 hits;
`tests/test_hga_alignment.py:69-70` pins only `dec:partOf` and `dec:Event`). Declared in the Contract,
unenforced on disk: `met false`, `retrospective false`.

So the rung reads **10/16**, not "the most complete." That is the instrument's second act
contradicting a belief the project held about itself — the first being §7.3 against `CLAUDE.md:452`.

**Blocking edges (§3.3), authored on this rung:** `R99` (`residues-open.md:79`) —
`iladub:NoLeakShape` has 11 focus nodes but its body names `iladub:asserted`, which appears in no
compiled graph, so it can never fire where it is wired. `R100` (`:80`) — `dec:EscalationShape` is
live at document scope and idle at page scope and the vacuity registry cannot express that. Neither
un-meets a pairing criterion (both shapes have both halves); both block a **liveness** criterion, and
the plan must decide whether liveness is a criterion of this rung or a residue edge only. **Name it,
do not assume it.**

### §7.2.1 The two pointers the handoff got wrong — why M5 exists

Both load-bearing citations in the handoff's rung-2 row are wrong on disk:

| handoff says | measured 2026-08-20 |
| --- | --- |
| `vocab/shapes/iladub-shapes.ttl:38` | `:37` is the shape; **`:39`** is the `iladub:wasPromotedBy` / `sh:minCount 1` clause that *is* the invariant |
| `src/iladub/compile.py:421` | **no such file.** It is `src/iladub/etkl/compile.py:421` |

Neither error changes the finding, and both are exactly what M5 refuses: **a criterion pointing at an
artifact that does not exist must not be assertable as met.** The instrument's membrane would have
caught the handoff's own citation the moment it was written into the manifest. Cite the corrected
forms; do not copy the handoff's.

### §7.2.2 The oracle is green *relative to a runner* — M5 needs a third arm

**This section began as a defect report and is kept as a correction, because the mistake is the
finding.** Collecting the oracles above under `python3`, two of them appeared broken:
`tests/etkl/test_membrane_equiv.py` skipped wholesale (*"pyrudof not installed"*), and
`tests/etkl/test_vacuity_registry.py`'s four corpus tests ERRORed at fixture setup with
`TypeError: int() argument must be … not 'NoneType'` from `regions.classify` → `run_kind`.

Neither is real. Measured 2026-08-20:

```
$ .venv/bin/python -c "import rdflib;print(rdflib.__version__)"   → 7.6.0
$ python3          -c "import rdflib;print(rdflib.__version__)"   → 7.1.4
$ .venv/bin/python -c "import pyrudof; print('pyrudof OK')"       → pyrudof OK
```

`tests/test_corpus.py:7` names **`./.venv/bin/python`** as the runner. Under the system interpreter
every corpus test reports a **false red**, and `pyrudof` — the second membrane engine — is simply
absent. Both "defects" were the wrong interpreter. **No residue row is raised** (§9 stands), and a
plan that starts debugging `classify-kind.rq` has misread this section.

**What survives, and it strengthens the model:** §3.1's *"if CI is green, every oracle is green"* is
true only **relative to a runner**. A node id that is green in the venv can be skipped or errored
under another interpreter, and a gauge that inherited that would silently un-meet criteria for an
environment reason. So:

> **M5 grows a third arm.** The manifest records the runner its assertions were validated against
> (interpreter path + the versions that matter), and `tests/test_arc_manifest.py` refuses when it is
> validated under a different one — rather than reporting criteria as unmet because the operator
> typed `python3`.

**The seam the plan must measure** (rule 3): run the oracle-collection check under
`./.venv/bin/python -m pytest --collect-only -q` and confirm every `prog:oracleTest` resolves there.
**Do not use `python3`.** This spec's own author did, twice, and wrote a defect that does not exist.

### §7.3 `holon` — 4 of 6

Source: `docs/holonic-interaction.md` § *What is built* (4 bullets, `:145-156`) and § *Planned work
(not done yet)* (2 bullets, `:158-163`). The page states both halves, which is what makes it a
denominator rather than a changelog.

Met (all **`retrospective true`** — written as a record of what existed):

1. `vocab/ontology/etkl-holons.ttl` — holon types + grounding portal + membrane health, standalone.
2. `vocab/ontology/iladub-hga-align.ttl` — optional HGA alignment, alignment-not-import.
3. `vocab/shapes/iladub-hga-shapes.ttl` — `iladub:HgaGroundingGovernanceShape`: a
   `holon:GroundingRecord` may reach `holon:RegisteredStatus` only via an `iladub:PromotionDecision`.
4. `examples/holon-grounding-conformant.ttl` + `tests/holon-grounding-leak.ttl` — a conforming
   traversal and its negative case, exercised by `tests/test_hga_alignment.py`.

Unmet (**`retrospective false`** — declared ahead of the evidence, so flipping either one is a real
measurement):

5. A membrane-health check computing `etkl:membraneHealth` (Intact / Weakened / Compromised) from
   validation results.
6. A full raw→clean traversal example spanning RawDocumentHolon → portal → CleanDocumentHolon.

**Note what this rung's fraction refutes.** `CLAUDE.md:452-456` says this work is *"not yet
started"*; the rung reads **4/6** and the page calls itself partially shipped. The instrument's
first act is to contradict the Contract file — which is the instrument working, and is §9's
excluded edit.

### §7.4 `tab` — 9 criteria, and the trap the register sets

**The trap, stated first because it nearly shaped this section.** The obvious move is to make each
open `tab:` residue a criterion. That is wrong twice over. It collapses §3.3's whole point
(*residue → criterion → rung*, not residue renamed as criterion), and — worse — **the register
records only debt**, so a denominator built from it would put the numerator near zero on the rung
carrying the majority of the repo's code. A gauge that reads `tab 1/17` would be measuring the
register, not the reading.

**The denominator that avoids it is the reading's own vocabulary.** The compiler enumerates the
reasons a region may refuse to be read; measured 2026-08-20 by
`grep -rhno '"[A-Z][A-Z_]\{6,\}"' src/iladub/etkl/*.py | sort | uniq -c`, **eight** are escalation
reasons — `REGION_TILING_FAILED`, `ROUND_TRIP_FAIL`, `MULTI_TABLE_AMBIGUOUS`, `ROW_GROUP_AMBIGUOUS`,
`MERGE_AMBIGUOUS`, `MATRIX_AMBIGUOUS`, `KIND_NOT_SUPPORTED`, `DATAGRID_RESIDUE` — the rest
(`RECORD_TABLE`, `UNSUPPORTED_TABLE`, `TRANSPOSED`, `NON_TABLE`) being *kinds*, not reasons. **The
plan MEASURES this list from the code rather than copying it from here**; it is a grep over literals,
not a declared enum, and that is itself worth reporting.

**The criterion, and the wording is load-bearing:**

> For each escalation reason: *on the 7-document corpus, this reason either does not fire, **or**
> every occurrence carries a dated adjudication.*

**Not "does not fire".** CLAUDE.md and `[[no-overfitting-general-fixes]]` are explicit that honest
refusal beats fake success; a criterion rewarding zero escalations would pay for suppressing them.
An escalation is the compiler correctly declining to read something. What is missing is not the
refusal — it is the **adjudication** of it, exactly as `cor:adjudication` already does for document
verdicts. And it is what every one of these rows asks for in its own words: R43 *"characterize
whether … is a benign classification quirk or a genuine verdict-semantics gap"*; R44 *"triage the
three escalation reasons separately … before deciding which, if any, share a root cause"*; R45 and
R62 the same shape.

**A ninth criterion, for the rung's own instruments:** *every wired `tab:` shape is live, or
registered idle with an adjudicated reason (corpus gap vs dead shape).* Half-met and the half is
recorded: `VACUITY_REGISTRY` (`tests/etkl/test_vacuity_registry.py:87`) exists and its two arms are
green — an idle shape must be registered, and a registered shape that goes live **fails** the guard
until its row is deleted. What is unmet is the adjudication of the four rows.

**Blocking edges, from the measured rows** (all verified open 2026-08-20, none struck):

| criterion | `prog:blockedBy` |
| --- | --- |
| `REGION_TILING_FAILED` adjudicated | R43, R44, R62 |
| `KIND_NOT_SUPPORTED` adjudicated | R44, R71 |
| `MATRIX_AMBIGUOUS` adjudicated | R45, R62 |
| `ROUND_TRIP_FAIL` adjudicated | R44 |
| `DATAGRID_RESIDUE` adjudicated | R79, R83, R84 |
| `ROW_GROUP_AMBIGUOUS` adjudicated | R80, R74, R77 |
| `MULTI_TABLE_AMBIGUOUS` adjudicated | R74 |
| `MERGE_AMBIGUOUS` adjudicated | — (may already be met; see the seam below) |
| every wired `tab:` shape live-or-adjudicated | R97, R98, R100 |

**The seam the plan must measure, and it is the expensive one.** *Which of the eight reasons
actually fire on the corpus today, and how often.* Nobody has counted; the register names occurrences
per document, not per reason across the corpus. The measurement is the `corpus_graphs` fixture —
**self-documented at ~5.5 minutes, all 7 documents** (`tests/etkl/test_vacuity_registry.py:298`) —
and `tests/test_corpus.py::test_expected_verdict[…ons…]` / `[…bfs…]` are 9- and 7-page compiles under
a `BUDGET_S = 320` SIGALRM. **Budget for it; do not assume a reason is met because no row names it.**
`MERGE_AMBIGUOUS` and `MULTI_TABLE_AMBIGUOUS` are the two most likely to be already-met, and
"probably zero" is not an assertion this manifest may carry.

**Two broken pointers found in the register, and they are the case for M7 and M5:**

1. **R74's closure names `test_cbh_p0_known_defects_are_pinned_not_hidden`. No such function exists.**
   The real pin is `tests/etkl/test_datagrid.py::test_cbh_p0_table_b_leak_is_pinned_not_hidden`
   (`:1135`) — measured PASS in 0.89s. Point the manifest at the real one; the register's own row
   should be corrected in the same change.
2. **`battery-run-final.log`, cited as the measurement evidence by R43, R44 AND R45, is not in the
   repo and not in git history** (`git log --all -- '*battery-run-final*'` → empty). It was a
   loop-local artifact referenced from `plans/2026-08-04-corpus-harness.md:870`. **No
   `prog:oracleArtifact` may point at it** — M5 exists for exactly this, and three register rows
   currently rest their measurement on a file nobody can open.

**R101 attaches to no rung, and that is a finding, not a gap.** It is repo-wide test hygiene (a
module-level `importorskip` collapsing a module into one skip line), not a reading capability. §5
gains a fourth query for it: **residues that block no criterion of any rung** — a row serving no
rung is either mis-filed or is work nobody's stated goal requires, and either answer is worth having.

### §7.5 `substrate` — 0 of 3

Source: `docs/narrative/scope-evolution.md` § `substrate`, which names its own three requirements:
an immutable **event ledger** (memory), **validation-at-write** (sensory), and **in-engine policy**
(motor). All three `retrospective false`; none met.

Measured (handoff § *MEASURED after the design*, rung 4): 34 LOC in `src/iladub/fluree/` (two
JSON-LD policy templates) + `writegate.py` (70 LOC, tested by 229); **zero** server/runtime code and
**zero** event-ledger implementation; `membrane.py` runs inside the compiler process, not at a write
endpoint. **The plan re-measures before writing `met false` — an unmet criterion is still an
assertion**, and this one is the only honest `0` on the strip.

Each unmet criterion names a **target** oracle that does not exist yet (§3, `prog:Oracle` on an unmet
criterion may name a path that is absent). M5 bites only on `met true`.

## §8 Falsifying oracles, named before the design

- Assert a position the criteria do not support → **refuse** (M2–M5).
- Point a criterion at an artifact that does not exist → **refuse** (M5).
- Point `prog:blockedBy` at a residue that is not in the register → **refuse** (M7).
- Declare a criterion met on the day it was declared, without `retrospective` → **refuse** (M4).
- Pin a `cor:scoreFloor` at a document's currently-measured score and assert the `etkl` criterion met
  → **must not count** (§7.1's corrected criterion; the adjudication has to accept the score, and a
  recorded HOLD scores zero). This is the falsifier for the gameability defect and the plan must
  supply a test for it.
- Point a `prog:oracleArtifact` at `battery-run-final.log` (cited by three live register rows, absent
  from the repo and from git history) → **refuse** (M5). This is a real string from the register, not
  a hypothetical.
- Validate the manifest under an interpreter other than the one it records → **refuse** (M5's third
  arm, §7.2.2).
- Remove the manifest → the gauge returns to `?`, never a guess.
- Flip an oracle test red → CI red; the assertion cannot silently stay up.

## §9 What this loop does NOT do

Read this section before writing any plan-supplied test (CLAUDE.md § Plan authoring, rule 5).

- **No persisted tally history / time series.** Decision 4. It accrues only over future loops and
  would show nothing today.
- **No velocity index, no "are we stuck" verdict.** `cockpit.py:22-32` — a tuned constant is the
  defect the §8 gate exists to catch.
- **No ordering between rungs.** No `prog:precedes`. Decision 8.
- **No auto-writing of the manifest.** The `cor:` precedent (`docs/wiki/concepts/corpus-harness.md:89-93`)
  is the rule: code validates the hand-authored graph and never writes it. A test that expects a
  criterion to flip itself to met is asserting behaviour this spec forbids.
- **No sixth rung, and no re-cutting of the arc.** M6.
- **No closure of any existing residue row.** This loop repairs the register's stale prose (§10);
  that is a repair, not a closure, and it must not be counted as one.
- **No `CLAUDE.md` edit.** The stale claim at `CLAUDE.md:452-456` (holonic ontology "not yet
  started" against 341 LOC on disk) is real and is *somebody's* job — Contract class, edited only
  on explicit request.

## §10 The two register repairs

Both measured 2026-08-20, both still open at `4774f43`:

1. `residues.md:40` says **"94 rows, 20 closed"**; `awk -F'|' '/^\| R[0-9]/ {print $3}'
   docs/superpowers/residues.md | sort | uniq -c` → **21 closed, 73 open**.
2. The convention example at `residues.md:25` writes `R97 (17/87 closed)`; the row itself
   (`residues-open.md:77`) reads `(18/87 closed)`.

The register that teaches the tally convention is the register getting the tally wrong. Fix both,
and make the index's stated figure carry the command that produced it.

---

## §11 The seams a plan must measure, in order

Named per CLAUDE.md § Plan authoring rule 3 — these are the facts to establish, **not** the answers.
The first is on the critical path; a plan that defers it will author a fabricated numerator.

1. **The `tab` numerator, and the `etkl` adjudication — one corpus run, both jobs.** Which of the
   eight escalation reasons fire on the 7-document corpus, and how often. `corpus_graphs` is ~5.5 min
   (`tests/etkl/test_vacuity_registry.py:298`); the ons and bfs single-document nodes are 9- and
   7-page compiles under `BUDGET_S = 320`. **Run under `./.venv/bin/python`** (§7.2.2).

   **The same run carries the six unadjudicated corpus documents (maintainer's call, 2026-08-20).**
   The per-document escalation-reason census IS the evidence an adjudication needs, so adjudicating
   on it costs one loop rather than six. **The expected outcome is mostly recorded HOLDs, and that is
   a success, not a failure of the pass:** R43, R44, R45 and R62 each name their closure as *"its own
   reading loop"*, so a document whose escalations are triaged and reasoned into a
   `cor:Unadjudicated` + `cor:adjudication` HOLD has been honestly disposed. **Do NOT pin a floor at a
   document's measured score to make the fraction move** — §7.1's corrected criterion refuses that,
   and §8 names the falsifier the plan must supply a test for.

   Expect `etkl` to stay near 1/7 after this pass. **The rung's fraction is not the deliverable; the
   six documents moving from "nobody has looked" to "measured, reasoned, held" is.**
2. **The eight reason literals themselves** — re-grep from `src/iladub/etkl/*.py`. They are string
   literals, not a declared enum; if the grep and §7.4's list disagree, §7.4 is wrong.
3. **`prog:declaredOn` per criterion** — `git log -L` / `git blame` on the declaring line of prose,
   not the file's creation date (§7).
4. **Every `prog:oracleTest` resolves** — one `./.venv/bin/python -m pytest --collect-only -q`.
   Three register rows currently cite `battery-run-final.log`, which does not exist, and R74 cites a
   function name that does not exist (§7.4).
5. **Does the harness render a multi-line `statusLine`?** `tests/test_cockpit.py:54` pins exactly one
   line; a two-line strip is a deliberate change to that test with its reason recorded (§6).
6. **The residue→residue backfill set** — re-measure with a stated command; this spec's pattern found
   7 rows, the handoff's found 6 (§3.3).
7. **Whether liveness is a `dec` criterion or a residue edge only** — R99 and R100 block something;
   name what (§7.2).

**And the rule that governs all seven:** a plan-supplied test must be reconciled against §9 before it
ships (CLAUDE.md rule 5). The two most likely contradictions here are a test expecting the manifest
to write itself, and a test expecting a rung with no criteria to render `0`. §9 forbids both.
