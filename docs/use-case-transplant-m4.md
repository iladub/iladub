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
