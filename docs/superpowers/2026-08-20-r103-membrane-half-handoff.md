# Handoff — does `tab-datagrid.ttl` belong in the membrane ontology? (R103, remaining half)

**Date:** 2026-08-20 · **Branch:** none (start from `main` @ `55b72a5`) · **Shape: originating**
— it changes what the membrane validates against. Not started.

> Written from a session at 130K, 2.6× the originating floor, immediately after closing the probe
> half. Nothing below is a design. The measurements are cited to their source; treat any sentence
> that sounds like a conclusion as a claim to re-derive.

## Goal

Decide whether `vocab/ontology/tab-datagrid.ttl` is parsed into `compile._FULL_ONT`, and act on the
decision. This is the half of R103 that was always the one that mattered; the probe half closed
2026-08-19 (PR #107).

## Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the membrane ontology | `src/iladub/etkl/compile.py:440-454` | what `_FULL_ONT` is built from, and **the 2026-08-10 comment at `:447`** — the last time a file was added here, the author measured all 7 corpus documents, validated twice (tab shapes alone, before and after), and recorded that every verdict was identical. That is the protocol to repeat, not to reinvent |
| the vocabulary in question | `vocab/ontology/tab-datagrid.ttl` | what it would ADD to the closure — its `rdfs:subClassOf` axioms are the part that can move a shape's reach; its `rdfs:domain`/`rdfs:range` rules cannot (they are inert since 2026-08-06) |
| the evidence that the question is live | `scripts/probe_domain_range_agreement.py`, class `OUTSIDE_MEMBRANE` | 12 nodes, the six `tab:GridAxiom` individuals. Re-run it; do not quote the number from here |
| the shapes side | `compile.py:398` `_TAB_SHAPE_FILES` | there is no `tab-datagrid-shapes.ttl`, so admitting the ontology adds **no new shapes**. Confirm this is still true before assuming the change is closure-only |
| the row | R103 in `docs/superpowers/residues-open.md` (index line in `residues.md`) | the full row, including the two 2026-08-18 entries and the 2026-08-19 one. **Open the row; the index line is a pointer** |
| the probe half | `docs/superpowers/2026-08-18-probe-domain-range-agreement.md` | why both of the earlier candidate designs were refuted, and the four classes |

## The seam to measure before writing anything

**`tests/test_probe_domain_range_agreement.py::test_membrane_ont_files_mirrors_the_compiler` will
fail the moment `_FULL_ONT` changes.** That is deliberate — the probe's `MEMBRANE_ONT_FILES` must
move with it, or every violation is classified against a graph the membrane no longer has. Expect
that failure; it is the guard working. What is **not** obvious, and must be measured rather than
reasoned: if `tab-datagrid.ttl` enters `_FULL_ONT`, the 12 `OUTSIDE_MEMBRANE` nodes reclassify to
`ONT_VISIBLE`, and whether anything else moves with them is unknown.

## What was decided, and where that decision is recorded

- **Nothing about this question has been decided anywhere.** Not in this file, not in the row, not
  in code. The row has said since 2026-08-17 that the membrane question is untouched, and it still
  is.
- Decided and recorded elsewhere: the probe stays page-graph-only and consults the two ontologies
  by name (`2026-08-18-probe-domain-range-agreement.md`, § What shipped; merged as `55b72a5`).

## Unverified / assumed

- **That this change is closure-only.** It rests on there being no `tab-datagrid-shapes.ttl`,
  measured 2026-08-17 and re-stated 2026-08-19, but never re-measured against the current tree.
- **That the 2026-08-10 protocol transfers.** `dec.ttl`/`iladub.ttl` were added to make the *dec*
  leg's shapes target anything at all; `tab-datagrid.ttl` would be added for a different reason
  (the emitter conforms to a vocabulary the membrane cannot see), and a protocol that showed
  "no verdict moves" may not be the right question here — *no verdict moving* could equally mean
  the change buys nothing.
- **That the second modelling question is separable.** `tab:Text` is declared `a tab:CellDatatype`
  (`tab.ttl:211`) while `tab-datagrid.ttl:177`'s prose calls it a legal family and `datagrid.py:638`
  emits it as one. This loop reported it and did not fix it. Whether admitting the file into the
  membrane turns that contradiction into a *refusal* is unmeasured — and if it does, the two
  questions are one.
- **The corpus score impact is entirely unmeasured.** No before/after exists.

## The next concrete action

In a fresh session, before any design: compile the 7 corpus documents once and validate twice
against the tab shapes — with `_FULL_ONT` as it stands, then with `tab-datagrid.ttl` added —
exactly as `compile.py:447` records for 2026-08-10, and report what moves. The decision follows the
measurement; do not write a spec first.
