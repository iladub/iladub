# Reference use case — Transplant M4 (Offer → Acceptance)

## The M4 pipeline (SP1)

A time-critical crash test: compile a raw, synthetic heart-offer document into the
SHACL-validated, provenanced context the accept/decline decision (milestone M4) requires —
then record the decision as a `hol:DecisionHolon` with its rejected option.

The trust gradient: deterministic build-time RDF→BAML type generation → controlled,
schema-constrained multi-agent LLM extraction → deterministic grounding (assert/propose) →
deterministic SHACL validation → deterministic decision on clean concepts.

Run the offline demo: `python -m pytest tests/test_m4_pipeline.py -v`.
Run it live (calls Anthropic): `BAML_LIVE=1 iladub m4 examples/transplant/offer.txt`.

> Synthetic data only. Clinical codes are illustrative; confirm terminology licensing
> before any real use. This is a demonstrator, not medical guidance.

## The timeline around the decision (SP2)

M4 is one milestone in a known supply chain. The **timeline engine** (`iladub.timeline`)
drives that chain from a declarative `hol:Process` of `hol:Milestone`s: it tracks where we
are (a cursor), checks whether each milestone's required context is **ready**, runs the
**forward pass** (what the *next* milestone needs that isn't captured yet — anti-crisis
anticipation), and computes **clock feasibility** via Allen's interval algebra
(`iladub.allen`) — does transport finish before the cold-ischemia window closes?

The engine is domain-agnostic: the same code drives `heart-timeline.ttl` (≈240-min window)
and `kidney-timeline.ttl` (≈1800-min window) — distinct supply chains within one domain.
Swap the TimelineContract, get a new chain; no engine change.

> Deterministic — no LLM. Event-driven reopening (`hol:revisitIf`) and live wiring of the
> forward pass to the extraction funnel are the next slice (SP3).

## When reality perturbs the plan (SP3a)

The timeline anticipates (SP2); SP3a reacts. An **event** (`iladub.events.Event` — a named
`condition` + payload) is matched against a decision's declared `hol:revisitIf` keys. If it
fires, `iladub.reopen.reopen` **re-evaluates** the decision with the event payload and emits a
new `hol:DecisionHolon` that `hol:supersedes` the prior one and is `hol:triggeredBy` the event.
The prior decision is preserved — an accountable audit trail.

Worked example: M4 *accepts* a heart (projected ischemia 95 min). A transport-delay event
`Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})` reopens the decision, which
now *declines* (270 > 240-min window) — superseding the acceptance, with the triggering event
recorded and both decisions retained.

> Deterministic — no LLM. Reopening is at the decision level; rewinding the timeline cursor and
> wiring the forward pass to the extraction funnel remain the next slice (SP3b).

## Closing the loop (SP3b)

The timeline now both anticipates and acts on its anticipation. `iladub.loop.advance_with_capture`
readies the current milestone by **driving capture**: when the milestone is missing required
context, it runs a supplied `capture_fn`, merges the grounded result into the context, re-checks
`readiness`, and advances the cursor — then reports the **forward look** (what the next milestone
still needs). For the transplant case, `iladub.m4.capture_context` is that `capture_fn`: it runs
the SP1 funnel (`extract_offer` → `to_rdf`) over an incoming document.

Worked example: the cursor sits at M4 with an empty context. A donor offer arrives;
`advance_with_capture` runs the funnel, grounds `tx:organ`/`tx:aboGroup`, M4 becomes ready, and
the cursor advances to M5 — whose remaining need (`tx:recipientReady`, absent from the offer) is
flagged for the next capture from a different source. Capture is *anticipated* — driven by what
the timeline knows the next decision will require.

> The loop is deterministic; the LLM is confined to `capture_fn` (the SP1 funnel), monkeypatched
> offline and exercised live behind `BAML_LIVE=1`. This completes the compile → anticipate →
> react → drive-capture arc (SP1 → SP2 → SP3a → SP3b).

## Targeted capture (SP3c)

SP3b drove capture by running the whole offer funnel. SP3c makes the funnel **contract-generic**:
each milestone's required-context contract declares its own extractor (`iladub:extractor`), and
`iladub.bridge.generate_context_baml` emits — at build time — a BAML class + function for exactly
that contract's fields. `iladub.m4.capture_for_milestone` reads the declaration, runs the
milestone's extractor, and grounds it via `iladub.to_rdf.ground_typed` (a field with an
`etkl:admissibleScheme` must ground; otherwise it is a free literal).

Worked example: the cursor reaches M5, which needs `tx:recipientReady`. A recipient-status report
arrives; the loop runs **only** `ExtractRecipientContext` (not the organ/ABO agents), grounds
`tx:recipientReady`, and advances to M6. Extraction is now driven by what *this* milestone needs.

> Build-time-faithful: the per-milestone extractor is generated, committed, and sync-tested before
> any document is compiled. M4 still uses the SP1 offer funnel; generating extractors for every
> milestone (and retiring the fixed agents) is the natural next step.
