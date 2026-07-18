# CLAUDE.md — iladub project conventions & durable decisions

This file orients any contributor (human or AI assistant) working in this repo.
It records decisions that are settled and should not be re-litigated without cause.

## What iladub is

**iladub** — Sumerian *íl* ("to lift, carry, deliver, bring forward") + *dub*
("clay tablet, document") = "the document-carrier." It compiles **human-addressed
documents** (any format) into FAIR, contract-defined semantic knowledge graphs that
machines can read.

It is the document-compiling front end of the **ET(K)L** method
(*Extract, Transform-with-(K)nowledge, Load*), whose persistent namespace is
`https://w3id.org/iladub/etkl`.

## The project family — `iladub` is the root (decided 2026-07-01)

`iladub` is the namespace **root** and the owned artifact: it predates HGA, and `etkl` + `dec`
are related concepts arranged freely before Cagle's Holon Graph existed. iladub adopts the
holon graph as the architecture *for* its work and **consumes HGA as the external substrate**.

> **iladub = a thin epistemic core + `etkl` + `dec`** — the carrier that lifts knowledge from
> raw documents into HGA holons and governs the decisions made about them.

- **iladub** (thin **core**) — the assertion/proposition epistemics (the signature: assert
  only what you can ground, propose everything else, never let a proposition pass as an
  assertion). `CandidateConcept`, `GroundedNode`, `PromotionDecision`.
- **etkl** — the narrow-scope **K-transform**: raw document → grounded holon, conformed to a
  destination holon's required schema (the contract). Includes the doc-holon fabric
  (Raw/Clean/Semantic/GroundingPortal/MembraneHealth). *Could* one day be an HGA contribution
  (HGA defines holons; it doesn't build them from raw human-addressed documents) — not now.
- **dec** — **decidability / decisionality**: `DecisionHolon`, escalation, events, timeline
  (and `risk`, contextual risk, as a decidability measure). An HGA extension, built now
  because HGA isn't ready for strict decidability yet; **deliberately portable** — designed to
  be upstreamed to / replaced by an HGA equivalent later.
- **HGA** (`holon:`) — external substrate; consumed, aligned (`rdfs:subClassOf`/`seeAlso`),
  **never cloned** (see § Source ownership).
- **iladub.dev** — the docs site (Material for MkDocs). *(PyPI package name `iladub` and
  `iladub.dev` are unaffected by the namespace re-rooting: namespace ≠ package.)*

**Migration status:** The re-rooting from the previous `…/etkl/*` layout was completed
2026-07-01, and the w3id redirects are **live** (PR #6281, merged; verified 2026-07-02):
`w3id.org/iladub{,/etkl,/dec,/risk}` content-negotiate to the canonical `vocab/ontology/*.ttl`
on `main`, HTML → `iladub.dev`, and old `…/etkl` 301-redirects into the new roots. (See the
migration plan at `docs/superpowers/plans/2026-07-01-semantic-architecture-migration.md`.)

## Licensing (non-negotiable, applies everywhere)

- **Code** → Apache-2.0.
- **Vocabulary / ontology / spec** → CC-BY-4.0.
- Every published artifact carries author metadata and links to the ET(K)L
  namespace from its first release, so the dated record is part of the authorship trail.
- Author: François Rosselet. © 2026.

## Core design principles (do not violate)

0. **There is no unstructured data.** Structure is interpreter-relative; a document
   the industry calls "unstructured" is **human-addressed structure with a latent
   schema** — complete relative to its intended (human) interpreter, not absent.
   ET(K)L **recovers** the author's structure (it does not tokenise the source) and
   **carries** it into a **machine-addressed, modality-native** form (it does not
   flatten the target into rows). Using AI to produce SQL-ingestable rows by default is
   *neolegacy* and is forbidden. Never write "unstructured" as if structure were
   missing; the framing is **human-addressed vs machine-addressed structure**, in
   filigran everywhere we state. See `docs/manifesto.md`.

1. **Knowledge-first.** Knowledge engineering is the *first* milestone of the
   pipeline, not the last. A semantic data contract declares the target semantics,
   and a knowledge module is passed as an *argument* to the transform — never
   reconstructed by mappings at the end.

2. **The contract is an ontology, not a JSON/YAML schema.** Contracts declare typed,
   vocabulary-grounded *semantic objects* (identity, SKOS/OWL grounding, SHACL
   validation, participation in a wider graph) — not field names and primitive types.

3. **Assert only what you can ground; propose everything else — and never let a
   proposition pass as an assertion.**
   - **Assertions**: content groundable in a provided ontology → typed,
     contract-bound, SHACL-validated → the grounded graph.
   - **Propositions**: ungroundable content → quarantined `iladub:CandidateConcept`
     with a suggested upper-ontology anchor (e.g. gist), source provenance, the
     suggester, and a confidence. Never dropped, never faked.
   - A proposition enters the grounded graph **only** as the product of a
     **promotion decision** (`iladub:PromotionDecision`, a subclass of
     `dec:DecisionHolon`). This is enforced by SHACL: *every grounded node must be
     produced by a promotion decision.*

4. **A promotion is a decision holon.** Admitting a proposition is an accountable,
   agent-attributed, auditable act using the *same* `dec` vocabulary that models
   decisions in document *content*. The tool that reads decisions out of documents
   governs its own reading with the same decision model.

5. **Context is carried, not discarded.** Table cells, prose concepts, and figure
   findings converge on the *same* concept IRIs. The story around a table is often
   richer than the table; capture it.

6. **Provenance to the page.** Every carried object traces back to the source
   document region it came from.

7. **Only emit what the source supports.** Never fabricate resources/data to achieve
   "full coverage." Credibility over completeness.

8. **Neurosymbolic-first — formal semantic code prevails over procedural code (the gate).**
   Reading a human-addressed document is a *neurosymbolic* process, not a procedural one.
   iladub's edge is *filling semantic gaps* (as `dec` did for decidability), never
   hand-coding geometry around them. **No decision is implemented in procedural code
   until it has been classified and justified** — the default is semantic; procedural code
   must be *earned* (Python is iladub's reference-implementation language — the class is
   language-agnostic):
   - **AXIOM (default)** — the decision is *declarative* over an RDF evidence graph
     (consuming an existing ontology or filling a *named* gap with thin owned vocabulary),
     in one of **two world-split forms** — the split is load-bearing:
       - **Derivation → SPARQL `SELECT`/`CONSTRUCT`** (+ FnO IRIs), **open world**: recovery /
         transform / role decisions that *grow* the graph from evidence — monotonic and
         evidence-positive (a fact is derived only when its support is *present*, never
         inferred from absence). Any closed-world guard (counting, completeness, disjointness)
         is **holon-scoped**: query-local `NOT EXISTS`/`COUNT` closes *within* the one holon
         while the graph stays open.
       - **Constraint → SHACL**, **closed world**: the contract *membrane* validating what may
         *cross* into the clean holon (cardinality, `sh:closed`, promotion-required).
     **Never use closed-world/SHACL to *derive*** — inferring-by-absence violates §7 (assert
     only what the source supports). Recovery is open-world; the membrane is closed-world; the
     **holon is the closure boundary**.
   - **NEURAL** — genuinely perceptual / underdetermined decisions (any *"which
     columns/rows does X span / read / group"* reading judgment) are **GenAI-via-BAML
     proposing** under the assert/propose/promote epistemics (§3), **disposed by a
     semantic oracle** (tiling SHACL / reshape round-trip). *Never* a Python geometry
     heuristic with a tuned tolerance.
   - **PROCEDURAL** — reserved for irreducibly procedural computation: **raw extraction**
     (source → typed RDF facts) and **decidable exact arithmetic**. The class is *procedural
     code*, not a language — **Python in iladub's reference implementation**, TypeScript/.NET/
     Rust/… in any other; each instance must state *in the code and the spec why it is
     irreducible* to AXIOM or NEURAL.
   Any procedural code that isn't a justified PROCEDURAL step is a **defect**. A **tuned constant
   or tolerance is prima facie evidence** the decision belongs in NEURAL/AXIOM, not procedural code.
   Every spec/plan carries this gate as a hard Global Constraint; **reviewers enforce it**
   — a tuned geometric constant, or a Python heuristic answering a span/read/group/role
   question, is a *review failure* unless it is an oracle-disposed NEURAL proposal or a
   justified PROCEDURAL step. Exemplars already shipped: the **declarative transform substrate** —
   the reshape recipe executed as fixed SPARQL `CONSTRUCT`s (`vocab/queries/*.rq`, run by
   `iladub.etkl.interpret.run`) reading their params from the RDF recipe, with the flat base a
   derived `hproj:Projection` and a forward-`CONSTRUCT` round-trip oracle; the *flagship AXIOM*
   case, gate-enforced by `tests/etkl/test_transform_gate.py` (neurosymbolic loop one, shipped
   2026-07-15) — plus **role recovery** (`recover_dimensions`: the UNPIVOT dim-name + operand-role
   rules as a two-pass SPARQL `CONSTRUCT` derivation over the `tab:` header graph — the first
   *derivation axiom* under the open/closed split, loop B, shipped 2026-07-15),
   `reshape.certify_with_proposals` (A2.1, NEURAL propose → oracle → promote), and
   **region tiling** (`iladub.etkl.tiling.region_tiles`: the tiling backstops as a SHACL oracle
   over each candidate region's RDF — the closed-world *constraint* mirror of loop B's open-world
   derivation, loop C, shipped 2026-07-16), the **typed-cell evidence graph** (`iladub.etkl.celltype`
   + `vocab/queries/{header-body-split,stub-data-split,looks-transposed,transpose-coherent}.rq`:
   header/body split, stub/data split, and transpose orientation as SPARQL derivations over a
   transient pre-holon typed-cell graph — the first evidence graph in the pipeline, loop B2a, shipped
   2026-07-17; extended in B2b (2026-07-18) with an open `tab:cellDatatype` lattice — Date/Currency
   body-signals + "homogeneous non-Text" queries — for date/currency recall), the **declarative kind
   classification** (`iladub.etkl.regions.classify` + `iladub.etkl.classifygraph` +
   `vocab/queries/classify-kind.rq`: the whole NON_TABLE/UNSUPPORTED/RECORD kind decision as ONE
   holon-scoped SPARQL `SELECT` over a fresh per-band evidence graph — the band *is* the closure
   boundary; a byte-identical *faithful lift* gated by a frozen `_ref_classify` differential oracle,
   with `infer_leaf_grid`/`_word_in_column` staying justified PROCEDURAL geometry, loop B2c, shipped
   2026-07-18), and `segment.find_table_gutter` (propose → oracle → dispose).

## Holonic interaction model (align, don't reinvent — esp. with the W3C Holon CG)

iladub is modeled as **interacting holons**, not just isolated definitions — *how
holons interact is the architecture*. A **RawDocumentHolon** and the **SemanticHolons**
(ontologies / SKOS terminology) interact through a governed **grounding portal**;
concept-matching at that portal is governed by **PromotionDecisions** at the contract
**membrane** (SHACL); what passes is assembled into a **CleanDocumentHolon** whose
**membrane-health is its cleanliness**. Assertions are *inside* the membrane;
propositions are candidates *at* it. See `docs/holonic-interaction.md`.

- We **align with**, and do **not** reinvent, the holonic-graph model. The **anchor
  is Cagle's W3C HGA** (`holon:` = `http://w3id.org/holon/`), the W3C Holon CG's
  reference ontology — *not* Welz's CGA (`urn:holonic:ontology:`), which remains useful
  conceptual prior art but is no longer the alignment target (decided 2026-06-23).
- **Alignment, not import:** the doc-holon fabric and grounding portal live in the
  `etkl` namespace and are aligned via `rdfs:subClassOf` to `holon:`
  (e.g. `etkl:CleanDocumentHolon ⊑ holon:DataHolon` (or `holon:Holon`),
  `etkl:RawDocumentHolon ⊑ holon:DataHolon`, `etkl:GroundingPortal ⊑ holon:Portal`)
  — never copied, never hard-imported. Reuse HGA's grounding lifecycle where it fits:
  iladub's `iladub:PromotionDecision` governs the `holon:GroundingRecord` →
  `holon:RegisteredStatus` transition that HGA leaves to a bare confidence gate.
- `dec` therefore generalizes from "decision-context only" toward "holon + interaction,"
  with `dec:DecisionHolon` as one holon type and `iladub:PromotionDecision` as the
  governed membrane-crossing.

### Posture toward the W3C Holon Community Group (settled 2026-06-23)

Cagle now chairs the **W3C Holon Community Group** (github.com/w3c-cg/holon), with his
own ontology **HGA** (`http://w3id.org/holon/`) and a **DataBook** authoring format.
This is the standardization venue for the general holon substrate. **iladub anchors to
HGA** (`holon:`), not Welz's CGA (`urn:holonic:ontology:`) — settled 2026-06-23; see the
alignment bullets above.

- **iladub does NOT compete with or reinvent what the CG builds.** Be a good citizen:
  align (not import), and contribute iladub's distinctive parts upstream rather than
  duplicating the substrate.
- **Defer to the CG (do not build a parallel version):** core holon vocabulary,
  portal/boundary machinery, the Markov-blanket / Friston–Bayesian layer, federation,
  generic event/projection/camera infra, the DataBook format + CLI.
- **iladub focuses on its differentiators:** (1) **document compilation** — the ET(K)L
  RawDocument→grounding-portal→CleanDocument front end; (2) **promotion epistemics** —
  SHACL-enforced "every grounded node is produced by an `iladub:PromotionDecision`,"
  which is *stronger* than HGA's confidence-gate (HGA routes low-confidence to
  `CandidateStatus` but does not require an accountable decision); (3) the **semantic
  data contract as ontology**; (4) **provenance-to-the-page**; (5) **domain-neutral
  worked examples** (healthcare/insurance) that can feed CG WG V (Industry Utilisation);
  (6) **contextual-risk governance** (`etkl/risk`) — a genuine *gap* in HGA (which has
  `hpol:` for access and `hbayes:` for probabilistic uncertainty, but nothing for
  contextual risk). Hosted in the ET(K)L family for now; a candidate CG contribution.
- **Information governance — align, don't reinvent the access half; contribute the risk half.**
  Access control rides HGA `hpol:` (ODRL) + `hview:` (ViewerPass) — do not build a parallel
  access layer. Risk is **contextual, not empiric**: `risk(condition, context) = condition ⊗
  effective_sensitivity(context)`, sensitivity inherited **top-down only**, a `risk:RiskAssessment`
  is a derived `hproj:Projection` (never a stored label — SHACL-enforced). AI access must equal
  the interacting user's access (the agent carries the user's identity; the membrane is the gate;
  enforced by `gsh:AiInheritsUserShape`). Worked example:
  `examples/transplant/transplant-governance.ttl` + `vocab/shapes/governance-shapes.ttl`.

## Source ownership (non-negotiable; the line we never cross)

We **develop** only the namespaces we own. HGA (Cagle's W3C Holon CG ontology) is an
**external source of truth we consume** — never one we author, edit, or redefine. Mixing the
two corrupts authorship provenance and the alignment story. This is settled (2026-06-29) and
**CI-enforced** by `tests/test_source_ownership.py`.

| We OWN — develop freely (root `https://w3id.org/iladub…`) | HGA — Cagle's; CONSUME only, never touch (`http://w3id.org/holon/…`) |
| --- | --- |
| the thin core `iladub:` · `etkl:` · `dec:` · `risk:` (+ their shapes, examples, Python) | `holon:` · `hev:` · `hpol:` · `hmk:` · `hproj:` · `hbayes:` · `hprov:` · `hspec:` · `hmedia:` · `hvc:` |

**The invariant (one line):** *In every authored RDF file, the subject of every triple is a
term we own. HGA terms appear ONLY as objects/types/targets — never as a subject.* We never
write `holon:X a owl:Class` or add any property to an HGA term; we only point our terms at
theirs (`our:T rdfs:subClassOf holon:T`).

Concrete rules:
1. **Edit only our four namespaces.** Adding `dec:escalatedTo` to `dec.ttl` is fine;
   declaring or annotating `hev:HolonEvent` anywhere is forbidden.
2. **HGA IRIs live only in `*-hga-align.ttl` modules and in HGA-bridging shapes/examples, as
   objects.** Core ontologies (`dec.ttl`, `risk.ttl`, `iladub.ttl`, `etkl.ttl`, `etkl-holons.ttl`) stay
   **standalone** — zero `w3id.org/holon` references (alignment-not-import; reasoner-free).
3. **Any local HGA copy is read-only and segregated** — fetched at test time or kept under a
   clearly-marked `vendor/hga/` snapshot (`@ <sha>`, "NOT OURS"). Never under `vocab/`.

iladub's role is to **complement HGA's gaps** (the accountable `dec:DecisionHolon`, promotion
epistemics, contextual risk, apex escalation), aligned by `rdfs:subClassOf`/`subPropertyOf`/
`seeAlso` — never to re-author the substrate.

## Serialization & stack conventions

- Ontologies, shapes, contracts, examples → **RDF Turtle** (`.ttl`) for authoring,
  **JSON-LD** for interchange.
- Validation → **pySHACL** (`inference="rdfs"`, `advanced=True` for SPARQL constraints).
- Namespaces: `iladub:` = `https://w3id.org/iladub#`, `etkl:` = `https://w3id.org/iladub/etkl#`,
  `dec:` = `https://w3id.org/iladub/dec#`, `risk:` = `https://w3id.org/iladub/risk#`;
  HGA alignment modules are `*-hga-align.ttl`.
- Decision/provenance reuse standards: `dec:DecisionHolon ⊑ prov:Activity`;
  evidence via `prov:used`, agency via `prov:wasAssociatedWith`, products via
  `prov:generated`. Don't reinvent provenance.
- Every vocabulary/shape ships with a worked example that conforms **and** a negative
  test that must fail. Tests run under `pytest`; CI runs them on push/PR.
- Multilingual by construction: rationale/label literals may be language-tagged
  (de/fr/it) — do **not** constrain such properties to `xsd:string` (that rejects
  `rdf:langString`).

## Naming discipline (a hard-won lesson)

Before claiming any name, verify across **PyPI + GitHub (repo collision) + a web
search including "+ ontology / semantic / knowledge graph"**. "Free on PyPI" is
necessary but **not sufficient** — the check that matters is *no same-domain prior
art*. (This rule exists because an earlier candidate, `dubsar`, was clear on PyPI but
turned out to be a dormant, same-domain semantic-modeling project — which would have
muddied authorship provenance.)

## Authorship / FAIR posture

- Publish openly, dated, under your name (PyPI release dates, git history, Zenodo DOI,
  `CITATION.cff`). Open publication is *defensive*: it establishes prior art and a
  citable record, and published knowledge cannot be used to restrain you later.
- Keep the work domain-neutral in public examples (healthcare, insurance, etc.) — never
  tied to an employer's domain. Personal time, personal resources, no internal data.

## Open items (verify; do not assert as done)

- [x] Register w3id.org redirects for the old `…/etkl/*` namespace tree (done 2026-06-02,
      w3id PR #6144, merged by dgarijo; content negotiation verified).
- [x] Open a new w3id PR to add `iladub` redirect rules (core, etkl, dec, risk) for the
      2026-07-01 re-rooting. **Done: w3id PR #6281 merged; verified 2026-07-02** —
      `w3id.org/iladub{,/etkl,/dec,/risk}` content-negotiate to the canonical
      `vocab/ontology/*.ttl` on `main`, HTML → `iladub.dev`, old `…/etkl` 301s into the new roots.
- [x] Confirm the masthead cuneiform glyph for *íl* against a sign list, or fall back
      to the "íl + dub" transliteration.
      (Verified 2026-06-03: `𒅍` = U+1214D "CUNEIFORM SIGN IL2" = *íl/il₂*, "to carry,"
      noun "carrier, porter"; `𒁾` = U+12077 DUB = "tablet/document". `𒅍𒁾` = "the
      document-carrier". Sources: Oracc Sign List IL₂, ePSD, Wiktionary U+1214D.)
- [x] Confirm `vocab/LICENSE` (CC-BY-4.0) exists and `CITATION.cff` is at repo root.
      (Verified 2026-05-31: `vocab/LICENSE` is CC-BY-4.0, `CITATION.cff` at root.)
- [ ] SNOMED CT / LOINC identifiers in examples are illustrative — confirm terminology
      licensing before redistributing real mappings. Keep example documents synthetic.
- [ ] Express the holonic interaction model in `vocab/` — but **scope it to iladub's
      differentiators** (grounding portal + membrane/promotion shapes + the
      RawDocument→CleanDocument traversal), *not* a parallel general holon ontology;
      defer the substrate to the W3C Holon CG and align by `rdfs:subClassOf`. Design
      fixed in `docs/holonic-interaction.md`; ontology work not yet started.
- [x] Decide the alignment anchor. (Settled 2026-06-23: anchor to **Cagle's W3C HGA**,
      `holon:` = `http://w3id.org/holon/`; Welz CGA is no longer the target. See the
      "Holonic interaction model" alignment bullets above.)
