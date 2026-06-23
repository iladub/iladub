# Transplant use case, DataBook-native — design

- **Status:** design (approved in brainstorm 2026-06-23)
- **Author:** François Rosselet
- **Related:** `CLAUDE.md` ("Holonic interaction model" / "Posture toward the W3C Holon
  Community Group"), `docs/holonic-interaction.md`, the HGA alignment module
  (`vocab/ontology/iladub-hga-align.ttl`, PR #11), memories `w3c-holon-cg` /
  `iladub-focus-vs-holon-cg`.

## Problem & intent

The transplant showcase (SP1 BAML compile → SP2 timeline → SP3a reopen → SP3b closed
loop) is currently authored as ~15 loose files: `.ttl` knowledge artifacts (ontology,
SKOS terms, contract, shapes, timelines), `.txt` raw inputs, inline conformant/leak
pairs, and Python orchestration, tied together by pytest. There is no markdown, no
provenance stamp, and no single portable artifact.

Having anchored iladub to **Cagle's W3C Holon CG / HGA** and the **DataBook** concept,
we want to recast the use case so that **DataBook is a real pipeline I/O format**: a
RawDocumentHolon DataBook in → a CleanDocumentHolon DataBook out, carrying the grounded
graph, the propositions, the decision, and the provenance trail in one auditable holon.

This is both a better showcase and a concrete demonstration of the alignment — a good
W3C Holon CG citizen *using* the format rather than reinventing it.

### Key reframe

A DataBook is not a file format; it is how a **holon** is serialized — frontmatter is the
holon's *context* layer, fenced blocks its *interior*, prose its *projection*. So the use
case becomes a **holarchy of DataBooks** connected by IRIs, transformed by iladub through
the grounding portal. Outputs reference inputs by IRI (the CG's "a pipeline of DataBooks
is a holarchy").

## Decisions (from the brainstorm)

1. **Aim:** DataBook as real pipeline I/O (not just a docs artifact).
2. **Scope (eventual):** everything — document holons, knowledge stack, timeline/reopen.
3. **Architecture — option C, "canonical DataBooks, transient graphs":** DataBooks are the
   only authored/stored artifact. On load, each turtle/shacl/sparql block is parsed into an
   in-memory rdflib graph; the existing engine runs unchanged; outputs are re-serialized to
   a DataBook. No graph is ever persisted as a loose `.ttl`. Only the *edges* change.
4. **Sequencing:** build the M4 raw→clean vertical first, then fan out.
5. **Defer to the CG, explicitly not built:** the DataBook CLI, triplestore push/pull, and
   the DataBook format spec itself. iladub only reads/writes the markdown in Python.

## Target architecture

```
KNOWLEDGE DataBooks (DataHolons / the membrane)
  contract · ontology · SKOS terms · shapes
        │  (inputs, referenced by IRI in the process stamp)
        ▼
RawDocumentHolon DataBook ──▶ [ iladub compile = grounding portal ] ──▶ CleanDocumentHolon DataBook
  offer.databook.md                  BAML extract → ground →               offer.clean.databook.md
  (raw text + acquisition            SHACL validate → M4 decide            #asserted · #propositions
   provenance in frontmatter)                                             #decision + process: stamp
        │
        ▼  later slices
  Process DataBook (timeline)  ·  Event/Decision DataBooks (reopen lineage)
```

Runtime rule: the grounding / decision / timeline / reopen engine is **untouched**; it
operates on graphs as today. DataBook ⇄ graph happens only at the load edge and the output
edge.

## Component 1 — DataBook I/O adapter (the only genuinely new code)

New module `src/iladub/databook.py`. No triplestore, no CLI.

- **Reader:** `read_databook(path) -> Databook`, exposing:
  - `.frontmatter: dict` (parsed YAML);
  - `.blocks: list[Block]` — ordered; each `Block` has `lang`, `id`, `graph_iri`, `content`;
  - `.prose: str`;
  - `.graph(*selectors) -> rdflib.Graph` — parses the requested turtle/shacl blocks
    (by block `id` or by `lang`) into one graph.
- **Writer:** `write_databook(frontmatter: dict, blocks: list[Block], prose: str, path)` —
  emits a spec-shaped `.databook.md`: YAML frontmatter, then for each block a
  `<!-- databook:id: … -->` (and `<!-- databook:graph: … -->` where set) comment followed
  by the fenced block.
- **Conformance scope (slice 1):** frontmatter follows the CG keys — `id`, `title`,
  `type`, `version`, `created`, and a `process:` object with `transformer`,
  `transformer_type`, `transformer_iri`, `inputs[]` (each `{iri, role, description}`),
  `agent`, `timestamp`. A lightweight `validate_frontmatter()` checks required keys.
  Validating against the CG's actual `databook.shacl.ttl` / JSON schema is a later
  hardening step, not in slice 1.

Block metadata round-trips via HTML comments immediately preceding the fence, matching the
DataBook spec; the writer must reproduce what the reader parsed (round-trip fidelity is a
test).

## Component 2 — The M4 vertical (slice 1)

### New input: `examples/transplant/offer.databook.md` (RawDocumentHolon)
- Frontmatter: `id` = raw-offer holon IRI; `type: databook`; acquisition stamp as the
  context layer (EUROTRANSPLANT ref `ET-2026-0091`, source, retrieved-at). All synthetic.
- Body: the current `offer.txt` content as the prose/`text` interior — unstructured source,
  no grounding.

### Transform: `iladub.m4.compile_offer()` becomes DataBook-aware at its edges only
1. `read_databook("offer.databook.md")` → pull the raw text.
2. Run the **unchanged** SP1 funnel: BAML extract → `ground_typed` → SHACL validate →
   `evaluate_m4` → `build_decision_holon`.
3. Assemble blocks + frontmatter and `write_databook(...)`.

### New output: `examples/transplant/offer.clean.databook.md` (CleanDocumentHolon)
- Frontmatter `process:` stamp: `transformer: "BAML + Claude"`, `transformer_type: llm`,
  `transformer_iri`, `inputs: [offer-databook IRI, contract IRI, terms IRI, shapes IRI]`,
  `agent`, `timestamp`, iladub version.
- Fenced `turtle` blocks:
  - `#asserted` — the grounded offer graph (`tx:offer` assertions);
  - `#propositions` — the takotsubo `iladub:CandidateConcept`;
  - `#decision` — the M4 `hol:DecisionHolon` (accept; option space; `hol:revisitIf`).
- Prose: the M4 narrative (what was decided, why, what was quarantined).

### Accuracy note (kept honest)
Today the transplant grounding asserts SKOS-resolved values as plain `tx:` triples and
quarantines the rest as `iladub:CandidateConcept`; it does **not** emit a per-node
`iladub:PromotionDecision`. So slice 1's `#decision` block carries the **M4 clinical
decision holon**, not grounding-governance decisions. Wiring the new
`holon:GroundingRecord` + `iladub:PromotionDecision` governance (PR #11) into transplant
grounding is fan-out slice 4 — a strong CG-story slice, deliberately out of slice 1.

## Testing & the conformant/leak discipline

- **Adapter** (`tests/test_databook.py`): round-trip (write→read fidelity), block
  extraction by id and by lang, `validate_frontmatter` required-key check.
- **M4 vertical** (new file `tests/test_m4_databook.py`):
  `compile_offer` reads the raw DataBook and emits a clean DataBook; assert `#asserted`
  passes SHACL against `offer-shapes`, `#propositions` count == 1 (takotsubo), `#decision`
  == accept and is a valid `hol:DecisionHolon`, and the `process:` stamp is present and
  names its inputs. BAML agents monkeypatched as today.
- **Conformant/leak pair** (preserves the existing discipline):
  - `offer.clean.databook.md` (conformant);
  - a SHACL leak variant whose `#asserted` block drops `tx:organ` → SHACL must fail;
  - a frontmatter leak (missing `process:` stamp) → `validate_frontmatter` must fail.

## Fan-out plan (after slice 1 is green)

1. **Knowledge stack → DataHolon DataBooks:** contract / ontology / SKOS terms / shapes
   re-homed into `*.databook.md`; `inputs` then reference real DataBook IRIs.
2. **Timeline → Process DataBook:** `heart-timeline` / `kidney-timeline` as DataBooks; the
   closed loop reads them through the adapter.
3. **Reopen → Event/Decision DataBooks:** the supersede / triggeredBy lineage as appended
   decision DataBooks.
4. **Grounding-governance enrichment:** emit `holon:GroundingRecord`s and govern
   Candidate→Registered with `iladub:PromotionDecision` inside the clean DataBook — the
   per-node demonstration of iladub's contribution to the CG (WG IV).

## Out of scope

- A DataBook CLI, triplestore push/pull, or the DataBook format spec (CG's responsibility).
- Changing the grounding / decision / timeline / reopen engine internals.
- Full CG-spec SHACL/JSON-schema validation of frontmatter (later hardening).
- Any non-synthetic clinical data; all examples stay synthetic and domain-illustrative.

## Success criteria (slice 1)

- `compile_offer` runs end-to-end from `offer.databook.md` to `offer.clean.databook.md`
  with no loose intermediate `.ttl`.
- The clean DataBook is a single self-contained artifact: grounded graph + propositions +
  M4 decision + provenance stamp.
- All new tests pass; the full existing suite stays green (no engine regressions).
