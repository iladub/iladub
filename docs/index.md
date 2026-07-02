<p align="center">
  <img src="assets/iladub-wordmark.png" alt="iladub — íl · dub, the document-carrier" width="460">
</p>

# iladub

> **The document-carrier** — compiling human documents into knowledge machines can read.

**iladub** (𒅍𒁾 · Sumerian *íl* "to lift, to carry, to bring forward" + *dub* "clay
tablet, document") compiles unstructured human documents into FAIR, contract-defined
semantic knowledge graphs. It is the reference implementation of the **ET(K)L** method
(*Extract, Transform-with-(K)nowledge, Load*), whose persistent namespace is
[`https://w3id.org/iladub/etkl`](https://w3id.org/iladub/etkl).

!!! note
    Early development — APIs are not yet stable.

## Why iladub

Five thousand years ago in Sumer, the first documents were clay tablets — and the sign
**𒅍 (*íl*)** that opens this project's name means *carrier*: one who lifts a value and
brings it forward. We still write documents **for humans**; a machine, like a non-scribe
before the clay, sees only marks. Reading a document means recovering the **knowledge**
behind it — the concepts and *how they relate* — at the level knowledge actually lives:
**holonic graphs**, on top of meta- and hypergraphs. iladub compiles human documents into
that level, knowledge-first. [Read the full story →](story.md)

## What it does

- Compiles a whole document (prose, tables, figures) and lets a **semantic contract**
  decide what becomes a typed object, from wherever it lives.
- **Asserts only what it can ground** in a provided ontology; everything else is
  **proposed**, never faked, and admitted only through an accountable **promotion
  decision**.
- Carries **provenance to the page** and converges table, prose, and figure mentions onto
  the **same concept IRIs**.

## Explore

- [The ET(K)L method](etkl.md) — knowledge as the argument of the transform.
- [Architecture](architecture.md) — the compile pipeline, end to end.
- [Assertions & propositions](assertion-proposition.md) — the epistemic boundary.
- [Holonic interaction](holonic-interaction.md) — holons, and how they interact.
- [dec — decision context](dec.md) · [Use case: clinical → FHIR](use-case-fhir.md) · [Naming](naming.md)

## Installation

```bash
pip install iladub
```

## Quickstart

```bash
# Compile a synthetic transplant organ offer into an M4 acceptance decision
# (live; needs ANTHROPIC_API_KEY)
iladub m4 examples/transplant/offer.txt
```

## Links

- **PyPI** — <https://pypi.org/project/iladub/>
- **Source** — <https://github.com/iladub/iladub>
- **ET(K)L namespace** — <https://w3id.org/iladub/etkl>
- **Author** — François Rosselet ([ORCID 0009-0002-8318-1072](https://orcid.org/0009-0002-8318-1072))

## License

iladub is dual-licensed:

- **Code** (the `iladub` package) — [Apache License 2.0](https://github.com/iladub/iladub/blob/main/LICENSE)
- **Vocabulary / ontology** (`vocab/`) — [CC-BY-4.0](https://github.com/iladub/iladub/blob/main/vocab/LICENSE)
