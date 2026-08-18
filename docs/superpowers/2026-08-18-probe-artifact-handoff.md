# Handoff — fix `probe_emitter_typing`'s false-positive class (R103 carry)

**Date:** 2026-08-18 · **Branch:** `loop1-gate-and-label` · **PR:** #106 (open, CI green)
· **Shape: originating** — it changes an oracle's semantics. Not started; see § Why.

> **START WITH `superpowers:brainstorming`, before reading the options below.** Decided
> 2026-08-18 with the maintainer. The question to open with is **not** "which of the two designs" —
> it is *what invariant is this probe an oracle for?* R61's premise is "emitters must type every
> node explicitly", but `tab:AggregateWitness` was never emitter output; it is a vocabulary constant
> an emitter *referenced*. The probe may be conflating two different invariants that share one
> mechanism — in which case the fix is to split the check, and neither option below is right.

## Goal

`scripts/probe_emitter_typing.py` reports a violation whenever a `rdfs:range`'s object is a
**vocabulary constant** typed in the ontology but not in the page graph. 14 of the 18
`tab-datagrid.ttl` violations are this class. Decide the fix, apply it, re-run.

## Where the primaries are

| what | where |
| --- | --- |
| the probe | `scripts/probe_emitter_typing.py` — `types_of` (reads the PAGE GRAPH only) and `probe` |
| the membrane it is supposed to model | `compile._validate` → `membrane.validate(graph, shapes, _FULL_ONT)` — page graph **+ ontology** |
| the measurement | R103's row in `docs/superpowers/residues-open.md`, § ARTIFACT/REAL SPLIT |
| why the probe exists at all | the probe's own module docstring, § WHY THIS EXISTS |

## The measured facts to design against

- `tab.ttl`: 56 violations, **0 artifacts**, 14 live. Clean — the fix must not move these.
- `tab-datagrid.ttl`: 18 violations, **14 artifacts**, 4 real, 0 live.
- The artifacts are objects like `tab:AggregateWitness` (`a tab:GridAxiom`, `tab-datagrid.ttl:318`)
  and `tab:Quantity` (`a tab:CellDatatypeFamily`, `tab.ttl:227`).

## Two candidate designs — PROPOSITIONS TO ATTACK, not a shortlist

**Provenance, stated so they are weighted correctly:** both were generated while writing this
handoff, at 222k context, by the session that had just made the measurement. They are the least
trustworthy part of this file. The measured facts above are the solid part. A fresh session that
discards both and reframes the problem is doing this right, not going off-brief.

1. **Let `types_of` consult the merged ontology as well as the page graph.** Mirrors what the
   membrane actually does, so the probe stops disagreeing with the thing it models.
   *Risk:* it weakens the probe's whole premise — R61 exists because emitters must type every node
   **explicitly**, and an ontology-wide type lookup could mask a genuine emitter loss. Measured
   partial reassurance: minted `doc#…` nodes are never typed in the ontology, so `tab.ttl`'s 56
   would not move. **That is measured for today's corpus, not proved in general.**
2. **Exclude vocabulary constants from the range check.** Keep `types_of` page-graph-only, but skip
   any object that is a subject in the ontology — it is not emitter output, so emitter-typing has no
   claim on it. Narrower, preserves the premise.
   *Risk:* needs a crisp definition of "is a vocabulary constant" that does not accidentally exempt
   a minted node.

**Do not pick by which is fewer lines.** The question is what the probe is *for*, and both answers
are defensible.

## Unverified / assumed

- The `tab.ttl`-is-unaffected claim under design 1 is **measured on this corpus only**.
- **A third finding, not part of this fix and not yet triaged:** `tab:Text` is declared
  `a tab:CellDatatype` (`tab.ttl:211`), never `a tab:CellDatatypeFamily`, while
  `tab-datagrid.ttl:177`'s prose says it *is* a legal family and `datagrid.py:638` emits it as one.
  2 of the 4 real violations are this. **Reported, not fixed** — it is R103's deferred modelling
  question, and fixing the probe will not make it go away.
- The measurement script was a throwaway (not committed). Reproduce it before trusting the numbers:
  add an `ont`-consulting branch to `probe`'s violation loop and split the counts.

## The next concrete action

In a fresh session: pick design 1 or 2 with the premise argument written down, apply it, re-run the
probe on the corpus, and confirm `tab.ttl` still reports 56/14. Then decide whether R103's
membrane question is now cheap enough to answer too.
