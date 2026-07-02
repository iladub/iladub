# The ET(K)L method

**ET(K)L** = Extract, Transform-with-**(K)**nowledge, Load. Knowledge engineering is
the *first* milestone of the pipeline, not the last.

## The inversion

Conventional ETL treats semantics as a downstream concern: extract raw data, transform
with hand-written mappings, load, and *then* maybe align to an ontology.

ET(K)L: a **semantic data contract** declares the target semantics, and an
**ontology/knowledge module** is ingested as an **argument** of the transformation
function — not reconstructed by a mapping at the end. Knowledge enters first (through
the contract, applied already at extraction) and as an argument (at transform).

## Core constructs

| Construct | Role |
|---|---|
| `etkl:SemanticDataContract` | Declares target SHACL shape(s), terminology bindings, required knowledge modules. |
| `etkl:KnowledgeModule` | A reusable OWL/SKOS/SHACL artifact, passable as a transform argument. |
| `etkl:Extraction` | Knowledge-guided reading of a source — applies the contract while reading. |
| `etkl:Transformation` | Takes a knowledge module as an argument (`etkl:hasKnowledgeArgument`). |
| `etkl:Load` | Loads the contract-validated output graph. |

## Conformance (checkable, not aspirational)

A pipeline is ET(K)L-conformant when SHACL confirms:
- every contract declares ≥1 target shape and references ≥1 knowledge module;
- every transformation has ≥1 knowledge argument and a governing contract;
- every extraction applies a contract (knowledge-guided);
- every source document declares its format.

This makes "knowledge is not optional, and it comes first" a *checkable property*.

## Modules

ET(K)L is modular. `dec` (decidability/decisionality) and the `iladub` core
(assertion/proposition epistemics) plug in; `etkl` produces the holons.

Persistent namespace: `https://w3id.org/iladub/etkl`.
