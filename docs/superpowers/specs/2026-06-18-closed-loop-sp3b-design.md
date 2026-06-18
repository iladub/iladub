# Design — SP3b: closed-loop anticipation (timeline drives capture)

**Date:** 2026-06-18
**Author:** François Rosselet
**Status:** Approved design, pending implementation plan

## 1. Why

SP1 compiles a document into a decision-ready context; SP2 knows where we are on the timeline
and what the next milestone needs; SP3a reopens decisions when reality perturbs them. SP3b
closes the loop: when the timeline shows the current milestone is **missing** required context,
the system **drives capture** from an incoming document, merges the grounded result, re-checks
readiness, and advances — *anticipated knowledge capture ahead of the clock*, exactly the
anti-crisis principle that motivated the timeline.

This reunites the deterministic timeline (SP2) with the LLM extraction (SP1). The LLM is
confined to a single capture step behind a callable seam; the loop itself is deterministic and
CI-safe (the seam is monkeypatched offline, exercised live behind a flag — the SP1 pattern).

## 2. Scope

**In scope**
- A **loop orchestrator** (`loop.py`): `advance_with_capture(timeline, cursor, context_graph,
  capture_fn, subject) -> CaptureStep` — ready the current milestone by capturing, merge,
  re-check readiness, advance if ready, and expose the forward look.
- A small **transplant capture helper** (`m4.py`): `capture_context(offer_path, terms_path) ->
  Graph`, wrapping SP1 (`extract_offer` → `to_rdf`) to return the grounded graph.
- Tests: deterministic loop tests (capture seam backed by SP1 with the BAML agents
  monkeypatched) + a live-gated end-to-end smoke.

**Out of scope (named, not assumed)**
- **Targeted per-milestone extraction** (generating/routing a BAML extraction for exactly the
  missing properties from each milestone's contract). SP3b uses **run-and-merge**: run SP1's
  existing extraction, merge, verify which needs are met. Targeted routing is a future
  enhancement.
- **A multi-document driver loop** (iterating capture across many arriving documents).
  `advance_with_capture` is the single step; chaining is the caller's concern.
- Automatic document arrival / event sources.
- Cursor rewind on reopening (SP3a left this out too).

## 3. The orchestrator (`src/iladub/loop.py`, deterministic)

The loop is a pure function of its inputs plus the supplied `capture_fn`. The only
non-deterministic surface is `capture_fn` (the LLM seam) — the loop never calls an LLM itself.

```python
@dataclass
class CaptureStep:
    captured: Graph                 # the grounded triples capture_fn returned
    readiness_before: Readiness     # current milestone readiness before capture
    readiness_after: Readiness      # after merging the capture
    advanced: bool                  # did the cursor move?
    still_missing: tuple[URIRef, ...]   # current milestone's remaining gaps (== readiness_after.missing)
    next_plan: CapturePlan | None   # the forward look: what the NEXT milestone will need

def advance_with_capture(timeline: Timeline, cursor: Cursor, context_graph: Graph,
                         capture_fn: Callable[[], Graph], subject: URIRef) -> CaptureStep:
    ...
```

Behaviour:
1. `readiness_before = readiness(cursor.current, context_graph, subject)`.
2. `captured = capture_fn()`; merge every triple of `captured` into `context_graph` (in place).
3. `readiness_after = readiness(cursor.current, context_graph, subject)`.
4. `advanced = cursor.advance(context_graph, subject)` — SP2's `Cursor.advance` already only
   moves when the current milestone is ready and there is a next milestone.
5. `next_plan = next_capture_plan(timeline, cursor.current, context_graph, subject)` — after a
   successful advance `cursor.current` is the new milestone, so this is the forward look at what
   the milestone *after* it needs; if no advance, it looks at the next milestone from here.
6. return the `CaptureStep`.

`capture_fn` is a zero-argument callable returning a grounded `Graph`. Merging the *full*
grounded graph (not only the needed properties) is intentional — extra captured context is
harmless, and the loop reports which *needed* properties are now satisfied via
`readiness_after`/`still_missing`.

## 4. Transplant capture helper (`src/iladub/m4.py`)

```python
def capture_context(offer_path: str, terms_path: str = <default transplant terms>) -> Graph:
    """Run the SP1 funnel over a document and return the grounded (asserted) graph,
    suitable as a capture_fn body for the timeline loop."""
    text = read_document(offer_path)
    terms = Graph().parse(terms_path, format="turtle")
    return to_rdf(extract_offer(text), terms).graph
```

The transplant `capture_fn` is then `lambda: capture_context(offer_path)`. The BAML agents
(invoked by `extract_offer`) are the LLM step — monkeypatched in tests, live behind `BAML_LIVE`.

## 5. The money-shot scenario (test)

The anti-crisis loop, end to end:
1. Heart timeline; `Cursor` at **M4**; **empty** context graph. `readiness(M4)` reports
   missing `{tx:organ, tx:aboGroup}` (M4's required context).
2. `advance_with_capture(..., capture_fn=<SP1 over the offer doc>, ...)` with the BAML agents
   monkeypatched to return the synthetic offer extraction (organ "Heart", ABO "O", …).
3. After capture: `readiness_after` is **ready**; the cursor **advances to M5**.
4. Asserts: `readiness_before.ready is False`; `readiness_after.ready is True`;
   `step.advanced is True`; `cursor.current.order == 5`; and `step.next_plan` shows **M5 still
   needs `tx:recipientReady`** — which the offer document does not supply, honestly flagged as
   the gap the next capture (from a different source) must fill.
5. A `BAML_LIVE=1`-gated smoke test runs the real funnel through one capture step.

## 6. Testing (deterministic offline; live-gated smoke)

- The loop is deterministic. Offline tests supply a `capture_fn` backed by `capture_context`
  with the SP1 BAML agents monkeypatched (the established SP1 offline pattern), or a plain stub
  `capture_fn` returning a fixed grounded graph for the pure-loop unit tests.
- `advance_with_capture`: not-ready → capture → ready → advanced; the `next_plan` forward look
  reports the subsequent milestone's gaps.
- A pure-loop unit test with a stub `capture_fn` (no BAML at all) proves the orchestration
  logic in isolation.
- `capture_context`: with monkeypatched agents, returns a graph asserting `tx:organ`/
  `tx:aboGroup`.
- Live-gated (`BAML_LIVE=1`) end-to-end: real document → real funnel → one advance.
- CI never calls the API.

## 7. Files

- Create `src/iladub/loop.py` — `CaptureStep`, `advance_with_capture`.
- Modify `src/iladub/m4.py` — add `capture_context`.
- Create `tests/test_loop.py` — pure-loop unit test (stub capture_fn) + the SP1-backed
  monkeypatched scenario + the live-gated smoke.
- Modify `docs/use-case-transplant-m4.md` — SP3b section.

## 8. Open items to resolve during planning (not blockers)
- Confirm the `next_plan` semantics after an advance (forward look at the milestone after the
  new current) read cleanly in the test; if it reads better to compute the forward look from the
  *pre-advance* position, adjust in `loop.py` (single place).
- Confirm `capture_context`'s default `terms_path` mirrors the one `m4.compile_offer` already
  uses (reuse the same default constant).
