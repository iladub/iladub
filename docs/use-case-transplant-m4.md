# Reference use case — Transplant M4 (Offer → Acceptance)

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
