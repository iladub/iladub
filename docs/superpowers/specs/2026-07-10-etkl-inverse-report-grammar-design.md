# ET(K)L Inverse-Report-Authoring Grammar — Design

**Date:** 2026-07-10
**Author:** François Rosselet
**Status:** Design approved; awaiting implementation plan(s).
**Supersedes (in behaviour, not vocabulary):** Loop 8a Python (`src/iladub/etkl/denormalization.py`), whose
tests (`tests/etkl/test_denormalization.py`, `tests/test_tab.py`) become the behavioural spec the new axioms
must satisfy.

---

## 1. Motivation — the neo-legacy trap we walked into

Loop 8a *recovered results* (pivoted dimensions, exact-arithmetic subtotals, 3NF base facts) but did it as a
fresh Python module that hard-codes the inverse of pivot and subtotal. It works on the fixture and teaches the
machine nothing reusable. That is precisely the *neolegacy* the manifesto forbids (Core Principle 0): one more
new code that does not model the problem.

The real problem, stated plainly: **a published table is the *forward* application of a small, known grammar.**
A human does not author a complex report — they author flat (CSV-like, 3NF) data and then apply a short, finite
sequence of operations that have existed in Excel since v1: **pivot, transpose, group/nest, aggregate
(subtotal/total), denormalize/join**, then decorate with **merged cells, text wrapping, alignment and sizing** to
fit a publication layout. Two operations — pivot and subtotal — scaffold the majority of every report.

There are not millions of operations; there is a **grammar**. ET(K)L for tables must **reverse-engineer the known
report-construction grammar** — recover *which* operations a human applied to go from flat data to the published
report — and express that recovery as **axioms** (declarative semantic rules), falling back to code only where no
declarative rule can reach.

This mirrors, for the *transformation* layer, what ET(K)L already does for the *concept* layer: we consumed
SKOS/gist/`qb` to ground concepts; we must likewise **consume existing RDF standards** for transformations and
mathematical rules instead of hand-rolling them in Python + bespoke `tab:` strings.

## 2. What Cagle/HGA gives us, and what it leaves open (research finding, 2026-07-10)

HGA expresses the transform that produces a projection as **SPARQL `CONSTRUCT` executed at the holon boundary**:
`CONSTRUCT` against the interior named graph → resolve RDF-1.2 annotations → apply SHACL connotations → emit a
**`holon:ProjectionGraph`** conformed to an external vocabulary. "The projection is not a copy of the interior.
It is a translation." External linkage uses `cga:bindsTo` (deliberately not `owl:sameAs`).

**The gap, stated honestly:** HGA publishes no declarative projection/transformation vocabulary (the CG repo lists
`ontology/`/`shapes/` as *forthcoming*). It gives us a **pattern** (CONSTRUCT-at-boundary) and a **target class**
(`holon:ProjectionGraph`) — nothing to *align to* for the transform mechanism itself. That white space is exactly
where ET(K)L sits, and it is upstream-portable when the CG publishes its own.

## 3. Consumed-standards stack (consume, do not reinvent)

| Layer | Consume | Maturity | Role |
| --- | --- | --- | --- |
| Aggregation / cross-row math | **SPARQL 1.1 aggregates** (`SUM`/`AVG`/`COUNT`/`MIN`/`MAX` + `GROUP BY`) | W3C Rec | Compute **and** re-verify subtotals; also HGA's boundary language |
| Naming a transform as a first-class object | **FnO** (Function Ontology) + RML-FNML; function IRIs = XPath/SPARQL F&O `sum`/`avg`/… | Working Draft (align + **pin a version**) | "This value = function F over group G" as portable, PROV-linked RDF |
| RDF→RDF reshape (unpivot/transpose/flatten) & the projection itself | **SPARQL `CONSTRUCT`** at the portal | W3C Rec + HGA pattern | Emits the derived `holon:ProjectionGraph` |
| Contract-scoped derivations | **SHACL 1.2 Rules** (`sh:rule`); SPIN is superseded — do **not** use | AF Note / 1.2 FPWD | Shape-scoped derivation, validated in the same pass |
| Source table → RDF | **RML** (+ SPARQL-Anything for irregular sources) | KG-Construct CG de-facto | Lift the recovered grid to RDF |
| Units/dimensions on numerics | **QUDT** | mature vocab | Correct dimensional semantics on ratios/%/rates |

**What ET(K)L legitimately owns** (both thin, both upstream-portable):
1. **A recovered-transformation record** — the *reverse* direction no standard covers ("this reported cell **was** a
   pivot + SUM of these source rows"), an auditable, re-verifiable object with FnO + PROV + SPARQL-aggregate as its
   executable body.
2. **A thin projection-derivation predicate** binding a projection to its generating `CONSTRUCT`/FnO/SHACL-rule via
   `prov:wasDerivedFrom`, aligned to `holon:ProjectionGraph`.

## 4. The three-tier disposition (= iladub's assert/propose/promote, applied to transforms)

Every recovered operation lands in exactly one of three states — the same three iladub already enforces
(Core Principle 3):

1. **ASSERT — deterministic grammar.** The ~80% where geometry + arithmetic force the op. SPARQL/SHACL/FnO axioms
   emit it; no model call.
2. **PROMOTE — GenAI proposes, the oracle grounds.** The divergent ~20%. GenAI does **not** produce data or an
   end-to-end path; it **proposes a candidate operation from the grammar** (typed via BAML) for an ambiguous
   region. That proposal is a `iladub:CandidateConcept` — a *proposition*, never an assertion — and it crosses the
   membrane **only** if the domain's oracle accepts it. This is `iladub:PromotionDecision` verbatim:
   agent-attributed (which model, which prompt), auditable, oracle-grounded.
3. **ESCALATE — residue.** Neither rules nor GenAI+oracle can satisfy the oracle → in-band escalation, never faked.
   The oracle *forces* this honesty: a hallucinated op will not reproduce the report, so it falls through to residue.

**Why the failed "AI reads the whole PDF→dataset path" approach differs from ours:** that asks for an unbounded,
unverifiable generation over dense information. Ours asks narrow, typed, locally-verifiable questions whose answers
are checked by exact reconstruction. AI proposes *within a formal frame*; determinism disposes.

**The containment invariant (load-bearing):**

> **GenAI's output type IS the grammar's operation vocabulary — never free-form data, never bespoke code.** A BAML
> function takes `(ambiguous grid region + context)` → returns *one operation of the grammar, with its parameters*.
> The type system bounds the search to the grammar; the oracle bounds acceptance to what reconstructs.

BAML is to the LLM what SHACL is to the graph: the typed contract on a non-deterministic engine (the AI-space
SHACL). BAML is already wired in this repo (`baml_src/`, optional dependency, from the M4 transplant work).

## 5. Architecture — two domains × two modalities → four loops

```
                    │  DETERMINISTIC (axioms:            │  NON-DETERMINISTIC
                    │  SPARQL / SHACL / FnO)             │  (GenAI-via-BAML → oracle → promote)
════════════════════╪════════════════════════════════════╪══════════════════════════════════════
 DOMAIN A           │  LOOP A1                            │  LOOP A2
 TABLE RESHAPE      │  unpivot, subtotal/total strip,     │  ambiguous pivot name; subtotal-vs-
 (semantic,         │  transpose, group-flatten,          │  datum / non-obvious aggregation;
 data-bearing)      │  denormalize                        │  ambiguous nesting
════════════════════╪════════════════════════════════════╪══════════════════════════════════════
 DOMAIN B           │  LOOP B1                            │  LOOP B2
 DATA-AGNOSTIC      │  merge→logical home, text un-wrap,  │  merge = hierarchy span vs floating
 COSMETICS          │  alignment/sizing normalization     │  metadata; wrap = one label vs two
 (presentation)     │                                     │  stacked cells
```

Two structural facts this split forces:

**5.1 Pipeline order is B → A (cosmetics upstream of reshape).** Domain B produces the *clean logical grid*;
Domain A's reshape recovery runs *on* that grid. Reshape is the semantic main event but cosmetics runs first
mechanically. Loop 8a silently assumed clean grids (i.e. assumed B was already done); that assumption is now an
explicit, owned domain.

**5.2 The oracle is per-domain, because the two domains fail differently:**
- **Domain A oracle — round-trip reproduction.** Replay the reshape recipe on the flat base ⇒ must regenerate the
  clean logical grid *exactly* (arithmetic + structural equality). The anti-overfit weapon.
- **Domain B oracle — geometric consistency / reversibility.** An un-wrap or merge-resolution is accepted only if
  the recovered logical cells re-tile the original boxes with no gap/overlap. Cosmetics carry no data, so their
  oracle is spatial, not numeric.

## 6. The four loops in detail

Format per inner loop: **axiom** (declarative mechanism) → **oracle** (what certifies it) → **boundary**
(why deterministic, or what GenAI supplies). Each inner loop closes on its own axiom + oracle + test + showcase
update.

### LOOP A1 — deterministic reshape axioms (supersedes Loop 8a)

Ordered by load-bearing weight (subtotal + pivot carry the majority):

- **A1.1 STRIP-SUBTOTAL/TOTAL** — *axiom:* a row/column is derived iff its cells equal an **exact** aggregate over a
  determined sibling group; the aggregate is a SPARQL 1.1 aggregate, the function bound to its F&O IRI and
  FnO-named (`sum`/`avg`/`min`/`max`/`count`/`product`); a SHACL rule marks `tab:AggregationRow`/`Column` and links
  `tab:aggregates`. *Oracle:* exact arithmetic — re-adding the stripped aggregate reproduces the row (float tol as
  in 8a). *Boundary:* deterministic (equality is decidable).
- **A1.2 UNPIVOT** — *axiom:* a header hierarchy is a pivot schema iff a spanning parent **names** a dimension whose
  leaf siblings are its **values** (the spanning-past-stub rule); a `CONSTRUCT` folds the N value-columns into one
  dimension column + one measure column. *Oracle:* round-trip — re-pivoting the base on that dimension reproduces
  the N columns, values and positions exactly. *Boundary:* deterministic where spanning/leaf geometry is
  unambiguous.
- **A1.3 GROUP-FLATTEN** — *axiom:* nested header/stub hierarchies (the header-tree / `coversRow` machinery) flatten
  to one attribute column per level via `CONSTRUCT`. *Oracle:* round-trip — regrouping by the attribute columns
  reproduces the tiling; certified by the existing coverage / no-overlap / refinement SHACL invariants.
  *Boundary:* deterministic where the tree tiles.
- **A1.4 TRANSPOSE** — *axiom:* the type-orientation test (Loop 4) — if the type-homogeneous axis is horizontal, the
  table was transposed; `CONSTRUCT` swaps coordinates. *Oracle:* round-trip (transpose back) + semantic
  type-orientation certifies direction. *Boundary:* deterministic where type-orientation is decisive.
- **A1.5 DENORMALIZE/JOIN inversion** — *axiom:* columns in an exact functional dependency on a key are an inlined
  join; split into base fact + dimension table. *Oracle:* round-trip — re-joining on the key reproduces the wide
  table. *Boundary:* deterministic where the FD holds exactly. *(Tail inner loop — least common; may defer.)*

### LOOP A2 — GenAI-assisted reshape (propose → oracle → promote)

Invariant pattern: **GenAI proposes the ambiguous parameter; the deterministic oracle still verifies the op
round-trips.**

- **A2.1 ambiguous pivot NAME** — spanning parent blank/merged-away, or the dimension implicit (`Q1…Q4` with no
  "Quarter" header). BAML returns the proposed dimension name. *Split verification:* the unpivot **structure** must
  still round-trip deterministically (geometry verifies the reshape); the **name**, not arithmetic-checkable, enters
  as an `iladub:CandidateConcept` promoted with provenance + confidence. GenAI names, geometry certifies.
- **A2.2 subtotal-vs-datum / non-obvious aggregation** — a row that looks like a total but fails plain SUM. BAML
  proposes *which* function or subset (weighted average, partial sum). *Oracle:* hard arithmetic — recompute the
  proposed function, require exact equality; round-trips → promote, else escalate. GenAI picks the function,
  determinism proves it.
- **A2.3 ambiguous nesting** — which level is the dimension. BAML proposes the grouping; *oracle:* group-flatten
  round-trip.

### LOOP B1 — deterministic cosmetics axioms (produces the clean logical grid)

- **B1.1 MERGE RESOLUTION** — *axiom:* a merged cell whose span aligns with the grid tiling resolves to its logical
  anchor. *Oracle:* re-tiling — resolved cells tile the original boxes, no gap/overlap (reuse the
  coverage/no-overlap SHACL invariants). *Boundary:* deterministic when the merge aligns with the tiling.
- **B1.2 TEXT UN-WRAP** — *axiom:* a multi-line block bounded by one logical cell box (lines share the cell's
  x-span, stacked in one row band) rejoins into one logical cell. *Oracle:* geometric — rejoined bounding box
  equals the logical cell box; re-wrapping at the column width reproduces the physical lines. *Boundary:*
  deterministic when the block is cleanly bounded. *(The principled home of the naive-proximity multi-word-label
  bug.)*
- **B1.3 ALIGNMENT/SIZING NORMALIZATION** — *axiom:* strip alignment/size as non-semantic; normalize to logical
  coordinates. *Oracle:* idempotent (records "cosmetic; ignore for semantics"). *Boundary:* deterministic (pure
  geometry).

### LOOP B2 — GenAI-assisted cosmetics (propose → oracle → promote)

The Domain-A round-trip is the **ultimate arbiter** of ambiguous cosmetic calls:

- **B2.1 merge: hierarchy span vs. floating metadata** — BAML proposes the classification. *Oracle:* two-stage —
  does "span" re-tile geometrically **and** let Domain A round-trip? If treating it as a span makes A's reshape
  reproduce the report, it *is* a span; otherwise it's metadata (recorded, not data). A wrong cosmetic guess
  propagates to a reshape that won't round-trip and is rejected globally — **cosmetic ambiguity is self-correcting
  through the reshape oracle.**
- **B2.2 wrap: one wrapped label vs. two stacked cells** — BAML proposes; *oracle:* geometric re-wrap consistency
  **+** the downstream reshape round-trip as a global check.

## 7. Cross-cutting mechanics (shared by all four loops)

- **Recovered-recipe vocabulary (owned, thin).** A small controlled vocabulary of report-authoring operations — the
  inverse-Excel grammar — each term bound to its SPARQL/FnO executable body and its provenance-to-the-page. Reuses
  the existing `tab:` terms (`AggregationRow`/`Column`, `PivotedDimension`, `aggregates`, `aggregationFunction`,
  `measureValue`, `atDimensionValue`) and adds the recipe/operation-sequence terms. The recipe is an **ordered list
  of operations** = the reverse of the authoring stack. This is owned artifact #1 from §3.
- **Flat base = derived `holon:ProjectionGraph`.** The normalized/3NF view is **derived, never stored** — produced
  by a `CONSTRUCT`, typed `rdfs:subClassOf holon:ProjectionGraph`, bound out with `holon`/`cga` binding predicates
  (not `owl:sameAs`). Mirrors the repo precedents `risk:RiskAssessment ⊑ hproj:Projection` and
  `tx:view-recipient a hproj:Projection`. **This re-models Loop 8a-③'s stored `tab:BaseFact` dataset as a
  derivation** — the correct holonic form. This is owned artifact #2 from §3 (the thin projection-derivation
  predicate, `prov:wasDerivedFrom` the recipe).
- **BAML typed contract.** Each GenAI escape-hatch is a BAML function whose **output type is the recipe
  op-vocabulary** (§4 invariant). Lives under `baml_src/`, behind the existing optional `baml` dependency — the
  deterministic loops (A1, B1) must not depend on it.
- **`iladub:PromotionDecision` gate.** Every promoted (GenAI-proposed, oracle-passed) operation is the product of a
  `PromotionDecision` (subclass of `dec:DecisionHolon`): agent-attributed, evidence via `prov:used`, product via
  `prov:generated`. Enforced by the existing SHACL invariant "every grounded node is produced by a promotion
  decision."

**Source-ownership compliance (non-negotiable, CI-enforced).** All authored triples have owned subjects
(`iladub:`/`etkl:`/`dec:`/`tab:`). `holon:ProjectionGraph`/`hproj:`/`cga:` appear **only as objects/types/targets**,
and only inside `*-hga-align.ttl` modules and HGA-bridging shapes/examples — never in the standalone core vocab.

## 8. Build roadmap (the order the four loops nest into)

1. **A1 first** — supersede Loop 8a on clean-grid fixtures (8a already assumed clean grids), proving the reshape
   axioms + the round-trip oracle against 8a's existing tests. The oracle infra + recovered-recipe vocabulary +
   the derived-`ProjectionGraph` output are born here.
2. **B1** — cosmetics determinism, feeding A1 real (dirty) PDF grids; brings the geometric oracle.
3. **A2 then B2** — GenAI-via-BAML, buildable only now that both oracles exist to fence it.

Each big loop is its own spec → plan → build cycle (this document is the shared design they descend from); each
inner loop closes with its axiom, oracle, test, and showcase-notebook update (the showcase always leads with the
rendered original PDF, per standing directive).

## 9. Testing strategy

- **Oracles as first-class tests.** Domain A: round-trip reproduction (replay recipe ⇒ regenerate grid, exact).
  Domain B: geometric re-tiling (no gap/overlap) + re-wrap consistency. The oracle *is* the test; no tuned
  constants, no confidence thresholds standing in for correctness.
- **Loop 8a tests are the A1 behavioural spec** — the new axioms must pass `tests/etkl/test_denormalization.py`
  and the relevant `tests/test_tab.py` cases, or the supersession is incomplete.
- **Negative test per axiom** (project convention): a fixture that must *fail* the oracle and escalate as residue,
  proving we do not fake coverage.
- **GenAI loops (A2/B2):** the promotion path is tested with the oracle mocked deterministic where possible;
  a proposal that fails its oracle must produce residue, not an assertion. No network in unit tests.
- **Showcase re-run to 0 errors** after each inner loop.

## 10. Honest gaps & open decisions (do not assert as settled)

- **FnO is a Working Draft, not a W3C Rec.** Align and **pin a version**; be ready for churn. It is the only
  standard that makes a transform a first-class RDF object, so the trade is worth it — but flagged.
- **The long tail is real.** The core grammar is small; hand-tweaked layouts, irregular merges, and mixed
  hierarchies are not. The discipline that prevents neo-legacy-again: **axiomatize the grammar, escalate the tail
  in-band** — never grow Python (or GenAI) to silently fake-cover it. The oracle enforces this automatically.
- **A1.5 (denormalize/join inversion)** is the least common op; may be deferred to a later inner loop without
  blocking the roadmap.
- **Round-trip exactness for floats** reuses 8a's tolerance (`abs(f-t) <= 1e-6*max(1,|t|)`); revisit if real
  documents need currency/rounding-aware comparison.
- **Where exactly RML enters** (vs. compiling the grid to RDF with existing `tab:` machinery) is deferred to the
  A1 plan; RML's known aggregation/pivot weakness means the math stays in SPARQL regardless.

## 11. Relationship to prior work

- **Supersedes** Loop 8a's Python behaviour (keeps its vocabulary terms and tests).
- **Reuses** Loop 2/5 header-tree + `coversRow`, Loop 4 transpose/type-orientation, Loop 6 matrix, Loop 7
  segmentation, Loop 8-pre coverage repair, and the tiling/coverage/refinement/unambiguous-access SHACL invariants.
- **Aligns** to Cagle HGA `holon:ProjectionGraph` (consume, never author); contributes the recovered-transformation
  record and projection-derivation predicate as candidate upstream contributions.
