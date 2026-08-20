# Brief — a strategy instrument: where are we on the map, and are we converging?

**Date:** 2026-08-20 · **Branch:** none yet (start from `main`) · **Shape: originating** ·
**Status: NOT STARTED. This is a brief, not a design.**

> Raised by the maintainer at the end of the R103 loop, in these words: *"I am a bit lost … I have
> no notion of how complete is the topic/epic we are working on and also the rhythm at which we
> are really making progress … Here I am blind."* Written from a session at 155K, 3× the
> originating floor, which is why this is a brief and not a spec.

## The ask, as stated

Alongside the residue register, maintain:

1. **Four quality monitors** — completeness, correctness, currency, consistency.
2. **A real dependency graph** — *"not only linked strings"*: traversable and queryable, so we can
   see **what must be unblocked**.
3. **A velocity index** — *"tells us if we are stuck or not"*.
4. All of it **visible at important decision times**, so loop selection is strategy, not adjacency.

The success criterion in the maintainer's own terms: **"tell us where we are on the map and if we
are converging to objectives."**

## CORRECTION (2026-08-20, same day): the first draft of this section was WRONG

It said flatly *"there is no objectives artifact in this repo."* **That claim was measured badly**
— it listed `docs/*.md` (top level) only and never looked in subdirectories. A survey run the same
hour found the artifact it denied. Recorded here rather than silently edited, because the
corrected version is weaker and more useful than the original.

## What actually exists, and the sharper problem

Program-level intent **does** exist, spread across four artifacts, none of which is a roadmap:

| where | what it gives | what it does not |
| --- | --- | --- |
| `docs/narrative/scope-evolution.md` | **the closest thing to an objectives doc** — "The arc" (4 stages: etkl compiler → decidability → holon reframe → active substrate) and a "capability ladder" of worked semaphores. In the mkdocs nav as *Scope & vision* | no state, no completion, nothing is a fraction of it |
| `CLAUDE.md` § *Open items* (line 442) | a checkbox list of program commitments | 3 checked, 2 open, no grain below the checkbox |
| `docs/superpowers/2026-08-17-loop-split-decision.md` | the only multi-loop **forward** plan — Loops 1/2/3 with the residues each carries | Loop-scoped; expires when the three are done |
| `docs/loops/README.md` | methodology: loop engineering, trust tiers L1/L2/L3, definition of done | how to run a loop, not which loops remain |

**So the real defect is not "no objectives" — it is that the objectives that exist have no state.**
`scope-evolution.md` names four stages and a ladder; **nothing anywhere says which rung we are on,
what remains on it, or what "done" would look like.** That is a much better-posed problem than the
first draft's, and a much smaller one: *the map exists and has no "you are here" marker.*

Note also that a **loop tracker lives in agent memory** (`next-loop-r97-r101.md`), not in the repo
— which is why the maintainer cannot see it. That alone may account for a large share of the
reported blindness, and it is cheap to fix.

## The second finding: dependencies exist only as prose

**No structured dependency data exists anywhere.** Measured: `docs/superpowers/residues.md` (the
index) contains not one occurrence of "blocks", "unblocked", "blocked by", "waits for" or
"depends on". That information lives *only* in full-row prose and in session memory — e.g. R61
"waits for R103's count" was recorded in a memory file, and R103's close unblocked it by a
sentence in a table cell.

Refined by the survey: **~8 lines in the whole register** use dependency language (5 in
`residues-open.md`, 3 in `residues-closed.md`) — e.g. R14 *"Depends on R10"*, R102 *"R89's answer
depends on this row"*, R4 *"now unblocked"*. So the data is not absent; it is **prose, uncounted,
and unqueryable**. There is no predicate, no field, no graph for it.

This is precisely the maintainer's *"not only linked strings"*.

## The hypothesis HELD — measured, not assumed

The four C's **are** largely already measured. What is missing is aggregation, a trend, and a
denominator. Survey result:

| instrument | measures | persists over time? |
| --- | --- | --- |
| `scripts/release_gate.py` + `vocab/queries/docgov-release-gate.rq` | doc-governance contradictions/staleness; **rule in SPARQL**, script only maps to exit code | no |
| `scripts/measure_dec_membrane.py` | per-document SHACL conformance under two closures | no |
| `scripts/probe_domain_range_agreement.py` | 4-class emitter-vs-ontology disagreement, 27 pages | `--json` snapshot; **no time series** |
| `tests/etkl/test_vacuity_registry.py` | per-shape focus-node count + term reachability — *can this shape refuse at all* | no; **skips entirely without the gitignored `corpus/`** |
| `tests/corpus-manifest.ttl` + `tests/corpus-shapes.ttl` | per-document `cor:scoreFloor`, `cor:expectedVerdict`, dated `cor:adjudication` by reviewer | **YES — adjudication history accumulates in the TTL** |
| `docs/superpowers/residues.md` tally | closed/open ratio snapshot per row at raise time | **YES, by convention** |
| `scripts/context_budget.py` | per-turn context %, thresholds 30/40 | no |
| `tests/etkl/test_adoption_ledger.py` | line-adoption ledger / page score | no |

**Two already persist.** The completeness monitor (Loop 2's "coverage ledger") is **designed but
not built** — a brief, not code — which is why framing this work to *close* R97–R100 is live.

## The design question this loop must answer before designing (do not skip)

**Should the strategy instrument BE an iladub holon graph, or a reporting script?**

**The survey settles most of this: the repo ALREADY dogfoods RDF on its own process, in two
places.** This is not a greenfield choice — there is a working pattern to copy:

- **Documentation governance** — `vocab/shapes/doc-governance-shapes.ttl` (a `dg:` repo-internal,
  unpublished vocabulary), `tests/docgov_extract.py` (a PROCEDURAL extractor emitting typed RDF
  from tracked markdown, mkdocs config and git commit dates), four SPARQL derivations in
  `vocab/queries/docgov-*.rq`, and four test modules. Spec:
  `docs/superpowers/specs/2026-07-31-documentation-governance-design.md`.
- **The corpus** — `tests/corpus-manifest.ttl` + `tests/corpus-shapes.ttl`, the `cor:` vocabulary
  modeling pins, verdicts and human adjudications as a graph.

**NOT modeled as RDF: residues, loops, plans, dependencies, metrics history** — precisely the five
things this brief is about. The gap is exact, and the precedent for closing it is
`docgov`: an internal unpublished vocabulary + a procedural extractor + SPARQL derivations + a
SHACL membrane. **Read that spec before designing anything.**

The remaining arguments for the graph are not aesthetic:

- **CLAUDE.md §8 forbids the script version by default.** A Python module computing health
  figures and a stuck/not-stuck verdict from tuned thresholds is *prima facie* a gate defect. A
  **velocity index is a tuned-constant trap by construction** — "are we stuck" is a judgment, and
  encoding it as `if velocity < 0.3` is exactly what the gate exists to prevent.
- **A dependency graph is a graph.** RDF is the substrate this project already runs on, SPARQL
  answers "what is on the critical path to objective X" natively, and `dec:DecisionHolon` already
  models accountable decisions — which is what loop selection *is*.
- **Dogfooding is on-message.** iladub's thesis is that decisions should be accountable graph
  objects. A strategy instrument that is a spreadsheet contradicts the product.

The counter-argument deserves equal weight and is not answered here: **a vocabulary loop that
ships no visible answer to "where am I" would make the maintainer's problem worse, not better**,
and the register's own economics (§ below) punish instrument loops that close nothing.

## Constraints this loop inherits

- **Slice vertically; a loop ships only when it CLOSES** (memory `loop-definition-of-done`). An
  instrument built as a horizontal layer across three loops is the failure mode here, because the
  complaint being answered *is* about rhythm. **One thin end-to-end slice that answers one real
  question at one real decision point beats a complete schema.**
- **The register economics argue against instrument loops**: measured 2026-08-20, the recent rate
  is 9 raised / 9 closed (break-even), 21/94 closed, 73 open. A loop that closes nothing worsens
  the very trend it is measuring. Consider whether this work can be framed to **close R97–R100**
  (the coverage ledger) rather than run beside them.
- **Start with `superpowers:brainstorming`** — this is creative/design work and the skill is
  mandatory before planning. Then `spec-writing-and-fresh-loops`: *what proposes, what disposes,
  and are they independent?* — and **name the falsifying oracle before designing**.

## Unverified / assumed

- **That the four C's are the right four.** They are the maintainer's framing, adopted as given.
  Whether they carve iladub's actual risk surface is untested.
- **That the existing-instrument hypothesis holds.** Table above is candidates, not measurements.
- **That objectives can be written at a measurable grain.** Plausible for the ET(K)L pipeline
  (documents compiled, corpus coverage, membrane enforcement) and much harder for the vocabulary
  and standards-alignment work. Nobody has tried.
- **That "velocity" is even the right instrument.** An alternative reading of the complaint is
  that the maintainer wants *orientation* (a map), and velocity is a proxy that may not be needed
  once the map exists. Worth testing before building it.
- **Whether this should be one epic or the first of several.** Not decided.

## The next concrete action

In a **fresh session**, before any design: (1) run `superpowers:brainstorming` on the ask as
stated above; (2) re-run the existing-instrument survey rather than trusting this brief's table;
(3) answer the objectives question — *what is iladub converging TO, written down?* — because every
other part of the ask depends on it. **Do not write a spec before the objectives exist**; a
velocity index without a denominator is the thing being complained about, rebuilt.
