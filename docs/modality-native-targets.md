# Modality-native targets (database-agnostic)

iladub is **database-agnostic**. The compiled output of a document is loaded into whatever
store fits the *object* — not whatever store a pipeline happens to default to. This is the
**Load** half of [the manifesto](manifesto.md): flattening the target into relational rows is
the same reduction as tokenising the source. Using modern, multimodal AI to keep producing
SQL-ingestable rows *by default* is **neolegacy**.

## The object chooses the store, not the reverse

The classic mistake is to let the destination format dictate what is captured: pick a SQL
table first, and only what fits a row survives. iladub inverts this. A single document yields
objects of many kinds — concepts and their relations, prose, quantities over time, a finding
in a figure, an embedding, the source page image itself. Each has a **native modality**, and
each belongs in a store that speaks it.

| Object modality | What it is | Example store kinds (illustrative, not prescriptive) |
|---|---|---|
| **Graph / semantic** | typed resources + relations; identity + grounding | RDF triplestores; labelled-property-graph databases |
| **Document / text** | prose, sections, narrative regions | document stores; full-text search engines |
| **Time series** | quantities indexed by time | time-series databases |
| **Vector** | embeddings for similarity / retrieval | vector indexes |
| **Tabular** | *genuinely* rectangular data | relational / columnar stores |
| **Image / media** | figures, scans, pixels | object storage + media services |
| **Blob** | opaque source artefacts | object storage |

**Relational is not banned — it is one target among many.** A truly rectangular dataset
belongs in a table. The error is *relational-by-default*: choosing rows before asking what the
object actually is. "SQL-first" is naïve; **"SQL-when-it-fits"** is correct. Increasingly these
kinds converge in **polyglot / multimodal engines** — but the principle is unchanged: the
modality of the object, not the convenience of the store, decides.

## The graph is the integration layer

One modality is special: the **holon graph** is iladub's canonical output and the place an
object's *identity, grounding, and provenance* live. **The identifiers are the integration** —
table cells, prose mentions, and figure findings converge on the **same concept IRIs**, so the
graph is what ties the modality-native stores together. Text can live in a search store, a
series in a time-series store, pixels in object storage — each **addressed from the graph** by
IRI, with provenance back to the source region. Modality-native stores are **projections of,
and satellites around, the holon** — not competing sources of truth. (See
[holonic interaction](holonic-interaction.md) and [architecture](architecture.md).)

## Standards make agnosticism real

Database-agnosticism is only real if nothing locks the meaning to one engine. iladub keeps the
canonical form in **open, standard interchange** — RDF / JSON-LD, SHACL shapes, SKOS/OWL
grounding, PROV-O provenance — so a holon can move between stores and survive the loss of any
one of them. The store is an implementation choice; **the contract and the graph are the
invariant.**

## Active holons need an enforcing substrate — but iladub does not marry one

An *active, governed* holon needs its **membrane enforced at runtime**: an append-only **event
ledger** (memory), **validation at write** (sensory), and **in-engine policy** (motor). Where a
substrate provides these natively, iladub aligns to it and lets the database *be* the membrane;
where it does not, iladub supplies them in the compile/serve layer. Either way the choice stays
**pluggable and replaceable** — the holon model and the standards above are what carry across,
so **no single engine is load-bearing for the architecture.**

> The destination must never dictate the meaning. iladub carries each object into the store
> that speaks its modality — and keeps the meaning in open form so it can always move.
