# The ET(K)L method

**ET(K)L** = Extract, Transform-with-**(K)**nowledge, Load. Knowledge engineering is
the *first* milestone of the pipeline, not the last.

> ET(K)L treats **every source as a fully-structured document whose structure is
> addressed to a human**. Compilation does not *add* structure to "unstructured" data —
> it **recovers** the author's structure, makes it explicit, and **carries** it into a
> machine-addressed, modality-native form without losing intent or context. The knowledge
> module is the interpreter's competence supplied as an argument; the contract declares the
> target semantics; [assert-vs-propose](assertion-proposition.md) keeps recovery honest.
> See [the manifesto](manifesto.md).

## Every document is already structured

There is no unstructured data — only **human-addressed structure** with a **latent
schema**. The failure of ordinary parsers (and of LLM pipelines built the same way) is a
mindset that cannot tell a **tabular report** from an **array with headers**: it reads a
document as text, then tokens, discarding the intent and context the author encoded for a
human reader. ET(K)L rebalances this by fixing what each stage *means*:

- **Extract** is not tokenising — it is **recovering the author's structure** (reading as
  intended). This is only possible with an interpreter, which is why **K** is required to
  read at all.
- **Transform** translates that recovered, human-addressed structure into a
  machine-addressed one — a **holon graph**, governed by the contract.
- **Load** targets whatever **modality-native** store fits the object (graph, text,
  time-series, vector, image, blob) — never a relational table *by default*. Flattening
  the target back into rows is the same reduction as tokenising the source: **neolegacy**.

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
| `etkl:Extraction` | Knowledge-guided reading of a source — **recovers the author's human-addressed structure**, applying the contract while reading. |
| `etkl:Transformation` | Takes a knowledge module as an argument (`etkl:hasKnowledgeArgument`); translates human-addressed structure into a machine-addressed holon graph. |
| `etkl:Load` | Loads the contract-validated output into a **modality-native** store (holon graph by default) — never relational-by-default. |

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
