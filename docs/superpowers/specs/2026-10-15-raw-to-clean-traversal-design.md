# Spec: the raw→clean traversal — grounding a document derives its portal and its clean holon

**Serves:** prog:criterion:holon:06 — picked by the maintainer on 2026-10-15, in session, from the
four unmet criteria that name no blocker (`vocab/queries/arc-unblocked.rq` over
`tests/arc-manifest.ttl`: holon:06, substrate:01–03).

**Date:** 2026-10-15. **Branch:** `holon-06-traversal`, on `main` at `e01384c`.

**Doc impact: increment.** Adds two object properties to `etkl:` (`etkl-holons.ttl`), one SPARQL
derivation, one shape, one alignment axiom plus one `rdfs:seeAlso`, and a generated worked example.
No existing term changes meaning. `docs/holonic-interaction.md` § "Planned work" loses its one item.

**Global Constraint: the neurosymbolic gate (CLAUDE.md § 8).** Every decision this spec adds is
classified in § 3.5. No NEURAL worker is added and no tuned constant appears.

**Authored at about 45K working tokens, under the 50K originating floor.** The scope fork (§ 2)
and the approach were ruled by the maintainer in session before drafting.

---

## 0. The concern, first

`etkl-holons.ttl` has declared `etkl:RawDocumentHolon`, `etkl:GroundingPortal`,
`etkl:CleanDocumentHolon`, `etkl:throughPortal` and `etkl:reconciles` since 2026-06-23, and **no
code has ever produced one of them**. The only example of the holon fabric
(`examples/holon-grounding-conformant.ttl`) is hand-authored and covers the promotion crossing
only. The architecture the repo names as its own — *how holons interact is the architecture* — is
therefore asserted in vocabulary and exhibited by nothing that runs.

## 1. What was measured

1. **Nothing in `src/` emits the three holon types or the two interaction properties.**
   `grep -rnE "RawDocumentHolon|CleanDocumentHolon|GroundingPortal|throughPortal|SemanticHolon" src`
   → one hit, a docstring (`src/iladub/m4.py:111`). `etkl:reconciles` has no emitter either (the
   `reconciles` hits in `src/` are an unrelated Python function, `etkl/datagrid.py:221`).
2. **No shape targets the clean side.** The only holon-fabric shape is `etkl:MembraneHealthShape`,
   `sh:targetClass etkl:CompiledDocumentHolon` (`vocab/shapes/etkl-shapes.ttl:161-162`).
3. **A compile has no per-document identity.** `src/iladub/etkl/compile.py:22`:
   `_DOC = URIRef("https://example.org/etkl/doc")` — one constant for every document. A Raw holon
   cannot be named from the compiled graph.
4. **A grounding contract and its terms carry no identity either.** `ground.Contract` is
   `target_class` + `fields` (`src/iladub/ground.py:114-116`); `terms` is a bare `rdflib.Graph`.
5. **The provenance path the traversal needs already exists in grounding output.** A promoted
   concept is `?pd iladub:reviews ?cand` (`ground.py:374`), `?cand iladub:fromRegion ?region`
   with `?region a iladub:SourceRegion` (`ground.py:291-293`), `?pd dec:produced ?gn`,
   `?gn iladub:groundsTo ?iri` (`ground.py:402-406`). A quarantined concept has a candidate and a
   region but no decision (`ground.py:414-488`, the three `return "proposed"` branches).
6. **CI already compiles and grounds a synthetic document.** `tests/test_concept_feed.py:34-38`
   builds `F.offer_table_pdf`, compiles it with `compile_tables`, and
   `test_offer_table_grounds_end_to_end` (`:143-150`) grounds it: `FeedResult(records=2,
   grounded=6, proposed=2)`.
7. **HGA's portal properties, measured at `w3c-cg/holon@3590f5e`,
   `architectures/hga/hga-pass-b-portals.databook.md:192-202`:** `holon:sourceHolon` is an
   `owl:ObjectProperty`, domain `holon:Portal`, range `holon:Holon`. **`holon:portalTarget` is an
   `owl:DatatypeProperty`, range `xsd:anyURI`.** The comment at `vocab/ontology/iladub-hga-align.ttl:52-53`
   names both without their kinds; it is accurate as far as it goes.

## 2. What the maintainer ruled, 2026-10-15, in session

- **Scope: compiler-produced, not hand-authored.** The example is what the real pipeline emits for
  one synthetic document, pinned by a test — not a second hand-written file nothing produces.
- **Approach A: an open-world SPARQL derivation**, run at the end of `ground_document`, plus a
  closed-world shape. Python minting in `ground_document` (B) and a separate assembly step with its
  own membrane validation and health (C) were rejected.

## 3. Design

### 3.1 Vocabulary (`vocab/ontology/etkl-holons.ttl`, owned, standalone)

Two object properties, each with domain `etkl:GroundingPortal`:

| property | range | meaning |
|---|---|---|
| `etkl:portalSource` | `etkl:RawDocumentHolon` | the document whose regions cross the portal |
| `etkl:portalTarget` | `etkl:SemanticHolon` | a knowledge module the portal reconciles against (1..n) |

…and the Clean holon reuses PROV for its origin: `?clean prov:wasDerivedFrom ?raw`. No property
links a Clean holon to its interior: the interior is **reached**, not listed —
`clean →throughPortal→ portal →reconciles→ region ←fromRegion← cand ←reviews← pd →produced→ gn`.
`etkl-holons.ttl` stays free of `w3id.org/holon` (`tests/test_hga_alignment.py::test_holons_module_standalone`).

### 3.2 Alignment (`vocab/ontology/iladub-hga-align.ttl`)

- `etkl:portalSource rdfs:subPropertyOf holon:sourceHolon .` — kinds agree (§ 1 item 7).
- `etkl:portalTarget rdfs:seeAlso holon:portalTarget .` — **not** `subPropertyOf`: ours is an object
  property, HGA's a datatype property over `xsd:anyURI`; a subproperty axiom across kinds is an OWL
  error. Recorded in a comment beside the axiom.

HGA terms appear as objects only (§ Source ownership).

### 3.3 The derivation (`vocab/queries/raw-to-clean-traversal.rq`)

A `CONSTRUCT`, parameterised by the Raw holon IRI and the Semantic holon IRIs, run over the triples
the current `ground_document` call added. It derives, **only from present evidence**:

- `?portal a etkl:GroundingPortal ; etkl:portalSource ?raw ; etkl:portalTarget ?sem` and
  `?raw a etkl:RawDocumentHolon`, `?sem a etkl:SemanticHolon` — **only if** at least one promotion
  exists in scope;
- `?portal etkl:reconciles ?region` for every region whose candidate a `iladub:PromotionDecision`
  reviewed and which `dec:produced` a `iladub:GroundedNode`. A quarantined concept's region is
  never reconciled;
- `?clean a etkl:CleanDocumentHolon ; etkl:throughPortal ?portal ; prov:wasDerivedFrom ?raw`.

The portal and Clean IRIs are minted deterministically from `?raw` (`#grounding-portal`, `#clean`),
so a re-run lands on the same subjects.

**Invariant (evidence-positive):** zero grounded nodes in scope ⇒ zero triples constructed. No
portal and no Clean holon is ever derived from an absence.

**Invariant (scope):** a region is reconciled by this portal only if it came from this call's
records. **SEAM for the plan — MEASURE before writing the call:** whether any caller of
`ground_document` passes a non-empty `g` (the corpus battery, `test_corpus*.py`). If one does,
running the query over all of `g` would reconcile another document's regions; the query must then
run over this call's delta, not over `g`.

### 3.4 The call site (`src/iladub/feed.py::ground_document`)

New keyword-only parameter `traversal: Traversal | None = None`, where `Traversal` is a frozen
dataclass `(raw: URIRef, semantic: tuple[URIRef, ...])`, `semantic` non-empty.

- `None` (the default) runs no derivation — every existing call site, the corpus battery included,
  is unchanged in output.
- Given, the derivation's triples are added to `g` **before** the `validate_shapes` membrane runs,
  so the shape in § 3.5 is part of what `validate_shapes=True` checks.
- Identity is the caller's because the code has none to offer (§ 1 items 3-4). Giving compiles a
  per-document identity is out of scope (§ 6).

### 3.5 The membrane (`etkl:CleanDocumentHolonShape`, in the shape file `_validate_grounding` loads)

`sh:targetClass etkl:CleanDocumentHolon`:

- `etkl:throughPortal` exactly 1, `sh:class etkl:GroundingPortal`;
- `prov:wasDerivedFrom` min 1, `sh:class etkl:RawDocumentHolon`;
- along `etkl:throughPortal`: `etkl:portalSource` exactly 1 (class Raw), `etkl:portalTarget` min 1
  (class Semantic), `etkl:reconciles` min 1 (class `iladub:SourceRegion`);
- the portal's source **is** the holon the Clean one was derived from (`sh:equals` cannot span a
  path; a SPARQL constraint states it).

**SEAM:** measure which shape graph `_validate_grounding` (`feed.py`) loads before choosing the
file; the shape must be in it, or `validate_shapes=True` will not run it.

### 3.6 The gate

| decision | class | why |
|---|---|---|
| a region is reconciled; a portal and Clean holon exist | **AXIOM, derivation** (`.rq`, open world) | grows the graph from present promotions |
| a Clean holon is well-formed | **AXIOM, constraint** (SHACL, closed world) | the membrane; derives nothing |
| running the query, adding its triples | **PROCEDURAL**, engine glue | decides nothing |
| which IRI names the Raw / Semantic holon | caller-supplied | no evidence in the graph names it (§ 1.3-1.4) |

## 4. The worked example

`examples/raw-to-clean-traversal.ttl` is the grounding graph `ground_document` produces for the
offer fixture (§ 1 item 6) with `traversal=Traversal(raw=<fixture IRI>, semantic=(<terms IRI>,))`,
using the same `_offer_deps` contract, terms, shapes and fake proposer. It is **generated**:
a script writes it, and a test regenerates it and asserts **graph isomorphism**
(`rdflib.compare.isomorphic`) with the committed file — byte equality is impossible because
`_emit_grounded`'s decisions and options are BNodes (`ground.py:372-401`).

The Raw holon IRI is a stable synthetic one (`https://example.org/demo/offer-table`), never a
`file:` path — a path would differ per checkout and break isomorphism.

## 5. Oracles and predictions

1. **`tests/test_hga_alignment.py::test_raw_to_clean_traversal_conformant`** (the name the manifest
   already carries, `tests/arc-manifest.ttl:531`): the generated example conforms to the grounding
   shapes plus `iladub-hga-shapes.ttl`, and contains exactly one Clean holon, one portal, one Raw
   holon, ≥1 Semantic holon.
2. **Negative: `tests/raw-to-clean-traversal-leak.ttl`** — a Clean holon with no `etkl:throughPortal`,
   and a portal whose source differs from the Clean holon's `prov:wasDerivedFrom`; must not conform,
   each violation reported against its own focus node.
3. **Evidence-positive:** the fixture grounded with a proposer that grounds nothing, `traversal`
   given ⇒ zero `etkl:` holon triples.
4. **Quarantine stays out:** the two proposed COD regions (§ 1 item 6) are not `etkl:reconciles`
   objects; the six grounded ones are. *Prediction, to be run:* six reconciled regions.
5. **Isomorphism regen test** (§ 4).
6. **Default unchanged:** with `traversal=None`, `test_offer_table_grounds_end_to_end` is unchanged,
   and the corpus baseline regenerates **byte-identical** under `tests/corpus-baseline/` except
   `inputs.json`. *Proposition:* if any document snapshot moves, the default path is not inert and
   the change is wrong.
7. **Manifest:** `prog:criterion:holon:06 prog:met true`, with whatever `prog:oracleArtifact` the
   manifest tests require for a met criterion (**SEAM:** measure `tests/test_arc_manifest.py`'s
   rules for flipping `met` before editing).

Every new test carries falsification evidence (CLAUDE.md plan rule 4).

## 6. What is NOT done

- **No per-document identity for compiles.** `compile.py:22`'s shared `_DOC` stays; a register row
  records it (§ 7).
- **No membrane health for the Clean holon.** `membrane-health.rq` and `etkl:MembraneValidation`
  stay scoped to `etkl:CompiledDocumentHolon`. The Clean holon carries no `etkl:membraneHealth`.
- **The corpus does not emit the traversal.** No corpus test passes `traversal`.
- **No `etkl:AlignmentHolon`**, no convergence count (regions reconciled *onto the same IRI*): each
  promoted region is reconciled; whether two converge is read off `groundsTo`, not stated.
- **No HGA `holon:Portal` lifecycle** (`portalStatus`, `portalLock`, traversal records).
- **No change to `examples/holon-grounding-conformant.ttl`.**

## 7. Residues to raise

- The compile has one constant document IRI for every document (§ 1 item 3); the Raw holon must be
  named by the caller until it does not.
- The Clean holon has no membrane health (§ 6, second bullet), though `etkl-holons.ttl` says its
  cleanliness *is* its membrane health.

## 8. Unverified or assumed

1. That `rdflib.compare.isomorphic` is stable across rdflib versions for this graph's size.
2. That pySHACL accepts the SPARQL constraint in § 3.5 under `advanced=True` — it does for other
   shapes in this repo, not measured for this one.
3. § 5 item 4's count of six reconciled regions assumes each grounded concept has a distinct
   region IRI (`urn:iladub:region:` + `concept.region`, `ground.py:291`). Two concepts sharing a
   region would give fewer.
