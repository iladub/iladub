<p align="center">
  <img src="docs/assets/iladub-wordmark.png" alt="iladub — íl · dub, the document-carrier" width="440">
</p>

# iladub

> **The document-carrier** — compiling human documents into knowledge machines can read.

**iladub** (𒅍𒁾 · Sumerian *íl*, "to lift, to carry, to bring forward" + *dub*, "clay
tablet, document") compiles unstructured human documents into FAIR, contract-defined
semantic knowledge graphs. It is the reference implementation of the **ET(K)L** method,
whose persistent namespace is [`https://w3id.org/etkl`](https://w3id.org/etkl).

> [!NOTE]
> Early development — APIs are not yet stable.

---

## The first documents

<p align="center">
  <a href="https://en.wikipedia.org/wiki/Kushim_(Uruk_period)">
    <img src="https://upload.wikimedia.org/wikipedia/commons/5/54/Clay_Tablet_-_Louvre_-_AO29562_%28cropped%29.jpg" alt="A late-4th-millennium-BC Sumerian proto-cuneiform clay tablet, a barley account held in the Louvre (AO 29562)" width="360">
  </a>
</p>

<p align="center"><sub>
  A late-4th-millennium-BC Sumerian account tablet (Louvre, AO&nbsp;29562) — a barley ledger
  possibly bearing <a href="https://en.wikipedia.org/wiki/Kushim_(Uruk_period)">Kushim</a>,
  the earliest personal name known to history. Photo Poulpy, crop Zunkir, via
  <a href="https://commons.wikimedia.org/wiki/File:Clay_Tablet_-_Louvre_-_AO29562_(cropped).jpg">Wikimedia&nbsp;Commons</a>,
  <a href="https://creativecommons.org/licenses/by-sa/3.0/">CC&nbsp;BY-SA&nbsp;3.0</a>.
</sub></p>

More than five thousand years ago, in the city-states of Sumer, people pressed a reed
stylus into wet clay and made the first marks that were not pictures but *records*. The
earliest of these tablets were not poems or laws — they were **accounts**: so many
measures of barley, so many head of cattle, owed by whom, to whom. Writing was born as
an instrument for keeping count, and the scribe who kept it had a title built from the
same root iladub carries: **dub-sar**, the *tablet-writer*.

That clay did something no human memory could. It lifted knowledge out of a single mind
and set it down in a durable, portable form — knowledge that could outlive the knower,
travel without them, and be read by someone who had never met them. The Sumerian verb
*íl* means exactly this act: to lift, to carry, **to bring a value forward** in a ledger.
The tablet was the first *document* — and the document was, from its very first day, a
thing made **by humans, for humans**. Reading it required a trained scribe. To anyone
else, the wedges in the clay were just marks.

## The same problem, five thousand years later

We never stopped. We still publish for each other in human-shaped documents — papers,
reports, slides, consultation notes, contracts, PDFs. The medium changed; the audience
did not. A document is written so that *a person* can understand it.

To a machine, a modern PDF is what a clay tablet was to a non-scribe: marks without
meaning. Optical character recognition and large language models can now recover the
*text* and describe the *pictures* — but the text and the pixels were never the point.
The point is the **knowledge**: the concepts a document is about, their identities, and
**how they relate**. A table of lab values means nothing without the prose around it;
the same number means different things in different contexts. Digesting a document is not
reading its characters. It is reconstructing the web of meaning a human author assumed
you already had.

## What it takes for a machine to read a document

Recovering that web of meaning needs more than a flat list of facts. It needs the right
*level* of structure:

- a **triple** says one thing about two things — `:patient :hasCondition :diabetes`;
- a **hypergraph** lets one relation bind many participants at once — a single clinical
  finding tying patient, observation, value, and time together;
- a **metagraph** lets relations themselves become things you can talk about —
  *statements about statements*, evidence about a claim, a decision about a fact;
- a **holonic graph** sits on top of these: every unit of knowledge is a **holon** — at
  once a whole and a part — carrying its own interior (what it asserts), boundary (the
  rules that govern it), context (who holds it, when, with what confidence), and the way
  it composes into larger wholes.

Knowledge is always held *by someone, about something, in a context, with a degree of
confidence* — and it nests. Only at the holonic level, **built on top of meta- and
hypergraphs**, can you express that and not just the surface of the page. That is the
level of semantics a document actually lives at, and the level iladub compiles toward:
concepts grounded in shared vocabularies, validated against an explicit contract, every
admission an accountable, auditable decision, every claim traceable back to the region of
the source it came from.

## ET(K)L — the K is an argument

This is why the method is not ETL but **ET(K)L** — *Extract, Transform-with-(K)nowledge,
Load*. The parenthetical **K** is the whole claim. In ordinary pipelines, semantics are a
downstream afterthought: extract raw data, transform it with hand-written mappings, load
it, and *then* maybe align it to an ontology. iladub inverts this. Knowledge engineering
is the **first** milestone, not the last:

```text
transform(data, knowledge)   ←  knowledge is the argument, not a later dashboard layer
```

A **semantic data contract** declares the target meaning up front, and a **knowledge
module** is passed *as an argument* of the transform — never reconstructed by mappings at
the end. Knowledge enters first, and it enters as input. That is the K.

## What documents will always be

Documents written for humans have always existed, and they always will — now written by
humans, and increasingly by machines. The format will keep changing; the human-shaped
nature of the document will not. And a document made for humans will *always* be a
challenge for a machine to truly digest — not the text, not the images, but the
**concepts and how they relate**: the knowledge behind the page.

Meeting that challenge is not a matter of bigger models reading more characters. It is a
matter of expressing knowledge at the level it actually has — **holonic graphs, on top of
meta- and hypergraphs** — and compiling human documents into it. That is iladub's work,
and it is the oldest work there is: to lift the knowledge out of a human-shaped document
and carry it forward into a durable, shareable form — as the scribe once carried the
count forward into the clay.

---

## What iladub does

- Compiles a whole document (prose, tables, figures) into a structure-preserving
  intermediate, then lets a **semantic contract** decide what becomes a typed object,
  from wherever it lives.
- **Asserts only what it can ground** in a provided ontology; everything else is
  **proposed**, never faked, and may enter the grounded graph only through an accountable
  **promotion decision**.
- Carries **provenance to the page** and converges table, prose, and figure mentions onto
  the **same concept IRIs**.

See the docs at **[iladub.dev](https://iladub.dev)** — including the
[architecture](https://iladub.dev/architecture/), the
[assertion/proposition epistemics](https://iladub.dev/assertion-proposition/), and the
[holonic interaction model](https://iladub.dev/holonic-interaction/).

## Install

```bash
pip install iladub
```

## Quickstart

```bash
# compile a document against a contract (knowledge-first)
iladub run \
  --contract  examples/patient-contract.ttl \
  --shapes    examples/patient-shapes.ttl \
  --knowledge examples/patient-knowledge.ttl \
  --input     examples/sample-admission.txt
```

```python
import iladub
print(iladub.__version__)
```

A worked end-to-end demonstrator — a synthetic German consultation report compiled into a
connected FHIR graph with a decision recorded over it — lives in
[`demo/`](demo/) (`python demo/assemble_fhir.py`).

## The project family

- **ET(K)L** (`etkl`) — the method and its umbrella vocabulary.
- **hol** — the holonic decision-context module (and, increasingly, holon interaction).
- **iladub** — the document compiler and its assertion/proposition epistemics (this repo).

## Development

```bash
git clone https://github.com/iladub/iladub
cd iladub
pip install -e ".[dev]"
pytest
```

## Citation

If you use iladub or the ET(K)L method, please cite it — see [`CITATION.cff`](CITATION.cff).

## License

This project is dual-licensed:

- **Code** (the `iladub` package) — [Apache License 2.0](LICENSE)
- **Vocabulary / ontology** (everything under [`vocab/`](vocab/)) — [Creative Commons Attribution 4.0 International (CC-BY-4.0)](vocab/LICENSE)
