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

## The finding that resizes the whole job

**There is no objectives artifact in this repo.** Measured: `docs/*.md` is fifteen files, all
conceptual or assertion-class (`manifesto`, `architecture`, `story`, `four-groundings`,
`use-case-*`, …). No roadmap, no epic, no milestone, no objective register. `docs/superpowers/
plans/*` are per-loop plans; there is no program-level plan above them.

**A velocity index has no denominator without objectives, and "converging" has no target.** This
is the same defect the residue register had before 2026-08-12, when it counted only openings and
therefore read as pure degradation: *a metric that cannot say what it is a fraction OF is a number,
not a position on a map.*

So the first question of this work is **not** "which dashboard" — it is:

> **What are iladub's objectives, written down, at a grain something can be a fraction of?**

Until that exists, monitors 1, 3 and 4 above measure activity rather than progress, and would
reproduce exactly the blindness they are meant to cure.

## The second finding: dependencies exist only as prose

**No structured dependency data exists anywhere.** Measured: `docs/superpowers/residues.md` (the
index) contains not one occurrence of "blocks", "unblocked", "blocked by", "waits for" or
"depends on". That information lives *only* in full-row prose and in session memory — e.g. R61
"waits for R103's count" was recorded in a memory file, and R103's close unblocked it by a
sentence in a table cell.

This is precisely the maintainer's *"not only linked strings"*. The dependency graph is not an
enhancement of the register; **it is data that has never been captured**.

## The hypothesis to test FIRST (cheap, and it decides the loop's size)

**Most of the four C's are probably already measured, and merely never aggregated, never
persisted, and never trended.** Candidate existing instruments to check before building anything:

| C | plausibly already covered by | to establish |
| --- | --- | --- |
| correctness | the test suite; membrane conformance; the corpus score gate | does anything persist a figure across runs, or only report *now*? |
| completeness | the corpus coverage work; the R97–R100 "coverage ledger" loop (**which is literally about this and is still open**) | is the coverage ledger the completeness monitor under another name? |
| currency | doc governance's SPARQL **staleness** checks (CLAUDE.md § Documentation governance) | what does it consider stale, and does it trend? |
| consistency | `tests/test_source_ownership.py`; `scripts/probe_domain_range_agreement.py`; doc governance's contradiction class | these are consistency checks with no shared reporting surface |

**If the hypothesis holds, the work is aggregation + persistence + objectives — one loop — rather
than four new monitors.** If it fails, that is a finding worth having before designing.

*A survey of these was dispatched to a subagent as this brief was written; its findings are not
folded in here, and the fresh session should simply re-run the survey rather than trust this
table. Every row above is a CANDIDATE, not a measurement.*

## The design question this loop must answer before designing (do not skip)

**Should the strategy instrument BE an iladub holon graph, or a reporting script?**

The arguments for the graph are not aesthetic:

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
