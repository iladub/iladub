# Design — SP3c: targeted per-milestone extraction (contract-generic funnel)

**Date:** 2026-06-19
**Author:** François Rosselet
**Status:** Approved design, pending implementation plan

## 1. Why

SP3b's closed loop drives capture by running the **fixed** SP1 funnel (the three transplant
agents) and merging whatever grounds. That works because the offer document happens to carry
M4's needs, but it is not *targeted*: every milestone would run the same organ/ABO/logistics
extraction regardless of what it actually needs.

SP3c makes the funnel **contract-generic**: given *any* milestone's required-context contract,
the system generates — at build time — a typed extractor for *exactly* that contract's fields,
and the loop runs the right extractor for the milestone it is on. The fixed three-agent funnel
was an SP1 shortcut; SP3c removes the hard-coding from the funnel's middle.

It stays faithful to SP1's principle: **BAML types and functions are generated, committed, and
known before any document is compiled.** SP3c generates a *function per context contract* at
build time; the loop only *selects* one at runtime.

## 2. Scope

**In scope**
- `iladub:extractor` vocabulary: a `SemanticDataContract` declares its BAML extractor function
  by name. `must_ground` is **derived** from `etkl:admissibleScheme` (no new predicate).
- `bridge.generate_context_baml(contract, fn_name, class_name) -> str`: emit a **class + an
  extraction function** for one context contract (the SP1 bridge only emitted types).
- `to_rdf.ground_typed(typed_obj, contract, terms, subject) -> ExtractionGraph`: a
  **contract-driven** grounding mapper (reads fields from the contract, configurable subject).
- `capture_for_milestone(...)`: read a milestone's contract → its declared extractor → run it →
  ground → return the grounded graph on the shared subject. Usable as a loop `capture_fn`.
- A worked **M5** instance: `tx:ctx-m5` declares `ExtractRecipientContext`; a generated
  `RecipientContext` class + `ExtractRecipientContext` function; a synthetic recipient-status
  document; the loop at M5 captures `recipientReady` and advances.

**Out of scope (named, not assumed)**
- **Migrating M4 (and the other milestones) off the fixed three-agent funnel.** SP3c adds the
  targeted path and demonstrates it on M5; M4 keeps the SP1 offer funnel. Generating extractors
  for *every* milestone + retiring the fixed agents is the follow-up.
- **Refactoring the offer `to_rdf`** to use `ground_typed` (kept side-by-side; unify later).
- Enum-typed fields in the generated context class (M5's field has no `admissibleScheme`);
  enum generation for admissible-scheme fields is reused from the SP1 bridge only if needed.
- Multi-document orchestration (which document feeds which milestone) — the caller supplies the
  document; SP3c targets the *extractor*, not document routing.

## 3. Vocabulary (`vocab/ontology/iladub.ttl`)

Add one property:
- `iladub:extractor` (DatatypeProperty, domain `etkl:SemanticDataContract`, range `rdfs:Literal`)
  — the name of the build-time-generated BAML function that extracts this contract's fields.

`must_ground` is not a vocabulary term: a field with `etkl:admissibleScheme` must ground
against the terminology (unresolved → `iladub:CandidateConcept` proposition); a field without
one is asserted as a free literal.

## 4. Bridge generalization (`src/iladub/bridge.py`)

Add (the existing `generate_baml` is untouched):
```python
def generate_context_baml(contract: Graph, fn_name: str, class_name: str) -> str:
    """Emit a BAML class + extraction function for ONE context contract's fields.
    Deterministic, build-time; references the shared CodedConcept from generated_types.baml."""
```
For a contract whose fields fill `tx:recipientReady` with `fn_name="ExtractRecipientContext"`,
`class_name="RecipientContext"`:
```baml
class RecipientContext {
  recipientReady CodedConcept?
}

function ExtractRecipientContext(doc: string) -> RecipientContext {
  client Claude
  prompt #"
    From the document below, extract ONLY these fields: recipientReady.
    For each, copy the exact source phrase into source_quote and give a 0..1 confidence.
    If a field is absent, omit it. Do not invent values.

    Document:
    ---
    {{ doc }}
    ---
    {{ ctx.output_format }}
  "#
}
```
Field names are the property local-names (`recipientReady`), sorted for determinism. The output
is committed (e.g. `baml_src/generated_recipient.baml`) and guarded by a sync test, then
`baml-cli generate` regenerates the client.

## 5. Contract-driven grounding (`src/iladub/to_rdf.py`)

Add alongside the existing `to_rdf`:
```python
def ground_typed(typed_obj, contract_graph: Graph, contract_node: URIRef,
                 terms: Graph, subject: URIRef) -> ExtractionGraph:
    """Map a typed extraction object to RDF, driven by ONE contract (identified by
    contract_node in contract_graph): for each etkl:hasField of contract_node, read the
    field's fillsProperty local-name off typed_obj; a field WITH an etkl:admissibleScheme
    must ground (unresolved -> CandidateConcept proposition), a field WITHOUT one is
    asserted as a free literal on `subject`."""
```
`contract_node` is required because the timeline graph holds several context contracts
(`ctx-m4`, `ctx-m5`, `ctx-m7`). It reuses the existing `_resolves(terms, value)` helper and the
`ExtractionGraph`/proposition machinery. The subject is a parameter (the loop passes the shared
`tx:offer`).

## 6. `capture_for_milestone` (`src/iladub/m4.py`)

```python
def capture_for_milestone(milestone, timeline_graph: Graph, document_text: str,
                          terms: Graph, subject: URIRef, b=None) -> Graph:
    """Select the milestone's declared extractor, run it on the document, ground the
    result via ground_typed, and return the grounded graph on `subject`."""
```
Steps: `contract_node = timeline_graph.value(milestone.id, hol:requiresContext)`; read its
`iladub:extractor` literal; `getattr(b or sync_client.b, fn_name)`; call it with `document_text`;
`ground_typed(typed, timeline_graph, contract_node, terms, subject).graph`. The loop `capture_fn`
is then `lambda: capture_for_milestone(cursor.current, timeline_graph, recipient_text, terms,
TX["offer"])`. (`Milestone.id` is the milestone URI, already on the SP2 dataclass.)

## 7. The worked M5 instance (`examples/transplant/`)

- `heart-timeline.ttl`: add `tx:ctx-m5 iladub:extractor "ExtractRecipientContext" .` (the M5
  context already declares `etkl:hasField tx:tf-recipient-ready` → `tx:recipientReady`).
- `recipient-status.txt`: a synthetic recipient-readiness report containing a line that grounds
  `recipientReady` (e.g. "Recipient readiness: READY; final crossmatch negative").
- `tx:recipientReady` has **no** `admissibleScheme` → asserted as a free literal, so capturing it
  satisfies M5's readiness directly.

## 8. The money-shot scenario (test)

1. Heart timeline; a `Cursor` positioned at **M5** (context already has M4's `organ`/`aboGroup`).
   `readiness(M5)` reports missing `{tx:recipientReady}`.
2. `advance_with_capture(..., capture_fn=lambda: capture_for_milestone(M5, timeline_graph,
   recipient_text, terms, TX["offer"]), ...)` with **only** `ExtractRecipientContext`
   monkeypatched (the organ/ABO agents are NOT invoked — proving targeting).
3. The targeted extractor returns `recipientReady="READY"`; `ground_typed` asserts
   `(tx:offer, tx:recipientReady, "READY")`; `readiness(M5)` becomes ready; the cursor advances
   to **M6**.
4. Asserts: `step.advanced is True`; `cursor.current.order == 6`; the captured graph contains the
   `recipientReady` assertion; the organ/ABO extractors were never called.
5. A `BAML_LIVE=1`-gated smoke runs the real `ExtractRecipientContext`.

## 9. Testing (deterministic offline; live-gated smoke)

- `bridge.generate_context_baml`: structural assertions (`class RecipientContext`,
  `function ExtractRecipientContext`, the `recipientReady` field) + a sync test that the
  committed `baml_src/generated_recipient.baml` equals a regeneration.
- `ground_typed`: a free-literal field (no scheme) is asserted; a scheme field that doesn't
  resolve becomes a `CandidateConcept` (reuses the SP1 assert/propose behaviour, now
  contract-driven).
- `capture_for_milestone`: with `ExtractRecipientContext` monkeypatched, returns a graph
  asserting `tx:recipientReady`.
- The targeted-capture loop test (§8), offline + `BAML_LIVE=1` smoke.
- SHACL/vocab: `iladub:extractor` defined; the M5 instance parses.
- Full SP1/SP2/SP3a/SP3b suite stays green.

## 10. Files

- Modify `vocab/ontology/iladub.ttl` — add `iladub:extractor`.
- Modify `src/iladub/bridge.py` — add `generate_context_baml`.
- Create `baml_src/generated_recipient.baml` (generated, committed) + regenerate the client.
- Modify `src/iladub/to_rdf.py` — add `ground_typed`.
- Modify `src/iladub/m4.py` — add `capture_for_milestone`.
- Modify `examples/transplant/heart-timeline.ttl` — `iladub:extractor` on `tx:ctx-m5`.
- Create `examples/transplant/recipient-status.txt`.
- Tests: `tests/test_bridge.py` (context generation + sync), `tests/test_to_rdf.py`
  (`ground_typed`), `tests/test_loop.py` (targeted capture), vocab test.
- Modify `docs/use-case-transplant-m4.md` — SP3c section.

## 11. Open items to resolve during planning (not blockers)
- Confirm the generated context class references the shared `CodedConcept` (defined in
  `generated_types.baml`) and that `baml-cli generate` accepts a second generated file in
  `baml_src/`.
- Confirm `capture_for_milestone` reads `hol:requiresContext` from the timeline graph the
  milestone came from (pass the timeline graph alongside the `Milestone`, since `Milestone`
  currently holds only `requires` property URIs, not the contract node).
