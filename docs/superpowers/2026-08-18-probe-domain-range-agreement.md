# The probe was named after a failure it has never seen (R61 / R103 carry)

**Date:** 2026-08-18 · **Branch:** `probe-domain-range-agreement` · **Doc impact:** none
· **Predecessor:** `2026-08-18-probe-artifact-handoff.md` (its two candidate designs are both
refuted below — by measurement, not by preference)

## Goal

Fix the false-positive class in `scripts/probe_emitter_typing.py`. The handoff framed this as a
choice between two designs; it also said to open with a brainstorm asking *what invariant is this
probe an oracle for*. That question turned out to be the whole loop.

## What was measured

27 corpus pages, `validate_shapes=False`, every violation classified by asking which graph — the
page, the membrane's ontology, or the wider vocabulary — supplies the type the rule demands.

| declaring file | total | UNTYPED | DISAGREE | ONT-VISIBLE | OUTSIDE-MEMBRANE | live | sh:sparql |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tab.ttl` | 56 | **0** | 56 | 0 | 0 | 14 | 14 |
| `tab-datagrid.ttl` | 18 | **0** | 4 | 2 | 12 | 0 | 0 |

**Zero UNTYPED, across every rule and every page.** The probe's name and its § WHY THIS EXISTS
claimed it enforced *"emitters type every node explicitly"* (R61). It has never once observed that
failure. Every node it flags carries a type — from the emitter, or from a vocabulary file:

- `range hasLabel -> LabelCell` (18) on nodes typed `Cell, EntryCell`
- `domain x0 -> BBox` (12) and `domain x1 -> BBox` (12) on nodes typed `GridColumn, MeasureColumn`
- `range atColumn -> LeafColumn` (12) on nodes typed `GridColumn` — **live, `sh:sparql`**
- `domain onPage -> Cell` (2) on nodes typed `DataGrid, UniformGrid` — **live, `sh:sparql`**
- `domain universeSource -> ColumnUniverse` (2) on nodes typed `DataGrid, UniformGrid`
- `range columnFamily -> CellDatatypeFamily` (2) on `tab:Text`, typed `tab:CellDatatype`

So the probe measures **emitter/ontology disagreement**, and always has. That is a different
finding from a lost `rdf:type`, with a different repair (a modelling decision, not an emitter fix),
which is why the two are now separate columns and the script is renamed
`scripts/probe_domain_range_agreement.py`.

## Why both handoff designs were wrong

`compile.py:441-454` builds `_FULL_ONT` from `tab.ttl` + `dec.ttl` + `iladub.ttl`. **It does not
load `tab-datagrid.ttl`.** So the 14 nodes the 2026-08-17 measurement called "probe artifacts" are
two different things:

- **2** — `tab:Quantity`, `a tab:CellDatatypeFamily` at `tab.ttl:227`. The membrane genuinely sees
  this type. A true false positive.
- **12** — the six `tab:GridAxiom` individuals (`RowAddressability`, `AggregateWitness`,
  `ColumnAlignment`, `SeedFollowsUniverse`, `NonDegeneracy`, `ColumnHomogeneity`), every one
  declared **only** in `tab-datagrid.ttl`. The membrane never loads that file, so it does **not**
  see those types.

**Design 1** ("let `types_of` consult the merged ontology") silences all 14 with one lookup —
including the 12 that are the sharpest available evidence that R103's open membrane question is
real: the emitter conforms to a vocabulary the membrane does not validate against.

**Design 2** ("skip any object that is a subject in the ontology") skips `tab:Text`, a subject at
`tab.ttl:211` — 2 of the 4 genuine `tab-datagrid.ttl` findings, and the whole third finding of
R103's 2026-08-18 entry.

Each design suppresses a real finding to remove a false one.

## What shipped

`types_of` still reads the **page graph only**. The two ontologies are consulted separately and by
name (`MEMBRANE_ONT_FILES` mirrors `compile._FULL_ONT`; `ONT_FILES` is the wider vocabulary), and
`classify` sorts each violation into one of four total, mutually-exclusive findings. Only UNTYPED
and DISAGREE gate.

**The invariant the change had to preserve:** remove false positives, move no live number. Live is
**14 before and 14 after**, still all `sh:sparql`, exit code still 1.

## FALSIFICATION

`tests/test_probe_domain_range_agreement.py`, 3 tests, exercised on hand-built graphs so every
class can be produced without the corpus.

1. **Collapse the two ontology lookups into one** — i.e. apply handoff design 1 (`if cls in
   wider_types: return ONT_VISIBLE`):
   `2 failed` — `test_the_four_classes_are_told_apart`,
   `test_a_type_the_membrane_cannot_see_is_not_ont_visible`. Restored: `3 passed`.
2. **Drift `MEMBRANE_ONT_FILES` from `compile._FULL_ONT`** (drop `dec.ttl`):
   `1 failed` — `test_membrane_ont_files_mirrors_the_compiler`. Restored: `3 passed`.

`tests/test_doc_governance.py tests/test_source_ownership.py`: `7 passed`.

## Unverified / assumed

- ~~The full suite was not run on this branch.~~ **Run at `c9541c4`: `1231 passed, 7 skipped,
  1 xpassed in 2168.87s (0:36:08)`, exit 0.** The 1228 recorded at `4bb023b` plus this loop's
  three new tests. The suite exceeds a 10-minute foreground timeout — run it backgrounded.
- **The probe is still wired into nothing.** No test, no CI job runs it; it is a script somebody
  has to invoke. It cannot become a gate while live is 14, so this stays deferred under R61.
- **The 0-UNTYPED result is bounded by the probe's reach.** It only inspects nodes that some
  `rdfs:domain`/`rdfs:range` rule touches. A node minted with no such property and no type is
  invisible to it. So "0 untyped" means *among nodes a typing rule reaches*, not *in the graph*.
- **`classify`'s ordering is load-bearing and rests on `lookup_graphs` returning a superset.**
  Pinned by construction (`wider += membrane`) and by the class test, not by a separate assertion.

## The next concrete action

Neither of the two modelling questions this loop *reported* is decided: `tab:Text`'s family
(`tab.ttl:211` vs `tab-datagrid.ttl:177`'s prose vs `datagrid.py:638`), and whether
`tab-datagrid.ttl` belongs in `_FULL_ONT` at all. The second now has 12 nodes of evidence behind
it and is R103's remaining half — take that one.
