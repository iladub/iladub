# CLAUDE.md — iladub project conventions & durable decisions

This file orients any contributor (human or AI assistant) working in this repo.
It records decisions that are settled and should not be re-litigated without cause.

## What iladub is

**iladub** — Sumerian *íl* ("to lift, carry, deliver, bring forward") + *dub*
("clay tablet, document") = "the document-carrier." It compiles unstructured human
documents into FAIR, contract-defined semantic knowledge graphs that machines can read.

It is the document-compiling front end of the **ET(K)L** method
(*Extract, Transform-with-(K)nowledge, Load*), whose persistent namespace is
`https://w3id.org/etkl`.

## The project family (separate, coherent artifacts)

- **ET(K)L method + vocabulary** (`etkl`) — the method spec and umbrella ontology.
- **hol** — the holonic decision-context module; the layer FHIR (and most data
  models) have no equivalent of.
- **iladub** — the document compiler + its assertion/proposition epistemics
  (this repo / package).
- **iladub.dev** — the docs site (Material for MkDocs).

## Licensing (non-negotiable, applies everywhere)

- **Code** → Apache-2.0.
- **Vocabulary / ontology / spec** → CC-BY-4.0.
- Every published artifact carries author metadata and links to the ET(K)L
  namespace from its first release, so the dated record is part of the authorship trail.
- Author: François Rosselet. © 2026.

## Core design principles (do not violate)

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
     `hol:DecisionHolon`). This is enforced by SHACL: *every grounded node must be
     produced by a promotion decision.*

4. **A promotion is a decision holon.** Admitting a proposition is an accountable,
   agent-attributed, auditable act using the *same* `hol` vocabulary that models
   decisions in document *content*. The tool that reads decisions out of documents
   governs its own reading with the same decision model.

5. **Context is carried, not discarded.** Table cells, prose concepts, and figure
   findings converge on the *same* concept IRIs. The story around a table is often
   richer than the table; capture it.

6. **Provenance to the page.** Every carried object traces back to the source
   document region it came from.

7. **Only emit what the source supports.** Never fabricate resources/data to achieve
   "full coverage." Credibility over completeness.

## Serialization & stack conventions

- Ontologies, shapes, contracts, examples → **RDF Turtle** (`.ttl`) for authoring,
  **JSON-LD** for interchange.
- Validation → **pySHACL** (`inference="rdfs"`, `advanced=True` for SPARQL constraints).
- `iladub:` namespace = `https://w3id.org/etkl/iladub#`.
  `hol:` = `https://w3id.org/etkl/hol#`. `etkl:` = `https://w3id.org/etkl#`.
- Decision/provenance reuse standards: `hol:DecisionHolon ⊑ prov:Activity`;
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

- [ ] Register the `w3id.org/etkl` (and `/etkl/iladub`, `/etkl/hol`) redirects so the
      namespaces actually resolve (required for FAIR).
- [ ] Confirm the masthead cuneiform glyph for *íl* against a sign list, or fall back
      to the "íl + dub" transliteration.
- [x] Confirm `vocab/LICENSE` (CC-BY-4.0) exists and `CITATION.cff` is at repo root.
      (Verified 2026-05-31: `vocab/LICENSE` is CC-BY-4.0, `CITATION.cff` at root.)
- [ ] SNOMED CT / LOINC identifiers in examples are illustrative — confirm terminology
      licensing before redistributing real mappings. Keep example documents synthetic.
