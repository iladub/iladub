# Handoff 2026-10-30: HDC-first contract compiler in iladub (brainstorm, continued)

> Copied from the hdc-contract repo (`/Volumes/WD Green/dev/git/hdc-contract`, commit `3a5f355`). In §2,
> "this session" and the earlier brief `docs/superpowers/2026-10-30-handoff-rescope-specs.md` refer to
> hdc-contract. The research file was copied alongside, to `docs/superpowers/research/` in this worktree.

## 1. Goal

Finish the brainstorm, then write the iladub `contract` rung design. That design rebuilds iladub's compiling on
a neuro-symbolic division of labour: HDC, Jev and small models decide, and the symbolic layer reasons. It is
tested on contracts first, then carried over to etkl tables.

## 2. Where the primaries are

- **This session:** the 2026-10-30 conversation, after `4b576f0` (see the commit trailers).
- **Earlier brief:** `docs/superpowers/2026-10-30-handoff-rescope-specs.md`. This handoff overrides its §3 items
  2, 4 and 5 and the "no model" part of item 9 (see §3 below). Its §2 file pointers still hold.
- **Research:** `docs/superpowers/research/2026-10-30-hdc-capabilities-research.md`, sections A–E (all five
  agent reports are in).
- **etkl-table drift scan (shallow, read-only):**
  - Package: `iladub/src/iladub/etkl/` (about 17k lines). Ontology: `vocab/ontology/tab.ttl` and
    `tab-datagrid.ttl`.
  - The ontology already has most of the domain classes (HierarchicalTable, HeaderNode, AggregationRow/Column,
    SuppressedRepeat, RepeatedHeader).
  - The decision layer is named geometrically: bands, gutters, flanks, donor bands, "matrix".
  - Tuned constants include `bands.py:60` (gap_factor 1.8), `grid.py:129`, and `headers.py:268/287/387`.
  - Footnotes, units-in-caption and total columns are not modelled. Re-run a scan before the tables phase rather
    than trusting these line numbers.
- **Memory note:** a separate iladub worktree `contract-rung-spec` holds
  `docs/superpowers/2026-10-30-contract-semantic-model-first-handoff.md`, from a parallel session
  ("model the contract first", JSON-LD family ontology). Read it and reconcile it before writing the spec.

## 3. What was decided (owner, 2026-10-30; recorded only here and in memory `tiny-semantic-architecture`)

1. **Soften iladub's no-LLM rule (owner).**
   - Why: heuristics without models drifted into rules nobody can follow, even the owner. Their names left the
     domain's lingua franca, and that is where neuro-symbolic gets weak.
   - New rule (my wording, the owner agreed in substance): models **decide, never reason**, and every decision is
     traced.
2. **Spatial evidence is a means, not the product (owner).** "We are not building a document GIS engine, but a
   semantic one." Concepts, names and traces stay in the domain vocabulary. Geometry is evidence only.
3. **Contracts first, then etkl tables (owner).** The contract rung refines the architecture. The spec should name
   which concepts carry over to tables.
4. **Every decision is a named question in domain vocabulary, answered by the simplest capable tool (my proposal,
   the owner said "exactly").** The tools, in order: exact rules, HDC, Jev (typed choice), small model (reads
   spans). Each answer leaves a trace: question, evidence, decider, confidence.
5. **The HDC core moves into iladub, and hdc-contract imports it (owner).** This reverses the earlier brief's item
   5. hdc-contract keeps the arbitrage-specific parts: comparison, scoring, bench.
6. **Haiku is the stand-in for a small local model for now (owner).** No local 1-9B runtime exists yet. It plays
   the same narrow role, so swapping it later changes nothing else.
7. **First establish everything HDC can do, then fill the gaps with Jev and a small model (owner).** The research
   is in the file above. My working division (shown to the owner, no answer yet):
   - **HDC:** segment evidence (depth permutation), type clauses (prototypes plus a three-way decision), clean up
     values to IRIs, fuzzy references, a role-filler record per clause holon, instant learning from SME answers.
   - **Haiku:** reads spans.
   - **Jev:** decides the "ask" cases.
   - **SHACL / exact rules:** decide.

## 4. Unverified or assumed

- The owner has not answered "what's wrong or missing in this division of labour". Two questions are open, and
  research gives a recommendation for each that the owner has not seen yet:
  - **Text encoding:** recommended lexical base plus a NEG/modal feature, with an A/B against a projected
    embedding (research §D).
  - **Layout encoding:** recommended FPE/KDE with data-derived bandwidth, which also targets the tuned constants
    in etkl (research §E).
- The conformal-prediction recipe (research §C) is the agents' and my inference. Neither the owner nor any data
  has checked it.
- How the earlier brief's open items fare under this rework is unchecked:
  - the seam format
  - gUFO classes per construct
  - the B-none baseline (60/85 unscored vs 48/85 scored)
  - the GAFTA licence
  - the number of SME questions per contract
- Whether the softened rule needs an owner ruling recorded in iladub's CLAUDE.md, and the wording, is not
  discussed.
- The parallel worktree handoff (§2) may conflict with items here. It is not read.

## 5. Next concrete action

In a fresh session:

1. Read the parallel worktree handoff.
2. Resume the brainstorm by putting the division-of-labour question back to the owner, together with research
   §C–E.
