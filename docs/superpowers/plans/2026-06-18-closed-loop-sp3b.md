# SP3b — Closed-Loop Anticipation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the loop between the SP2 timeline and the SP1 extraction: when the current milestone is missing required context, drive capture from a document, merge the grounded result, re-check readiness, and advance — anticipated capture ahead of the clock.

**Architecture:** A deterministic orchestrator `advance_with_capture` (in `loop.py`) calls a supplied zero-arg `capture_fn` (the only non-deterministic seam), merges its grounded graph into the context, re-checks SP2 `readiness`, advances the SP2 `Cursor`, and reports the forward look. A thin transplant `capture_context` helper wraps SP1 (`extract_offer` → `to_rdf`). The LLM is confined to `capture_fn`; tests monkeypatch the SP1 BAML agents (offline) with a live-gated smoke.

**Tech Stack:** Python ≥3.11, rdflib (existing); SP1 (BAML) only inside `capture_context`; pytest. Offline-deterministic CI; live behind `BAML_LIVE=1`.

**Spec:** `docs/superpowers/specs/2026-06-18-closed-loop-sp3b-design.md`

---

## File structure & interfaces

| File | Responsibility |
|---|---|
| `src/iladub/loop.py` (create) | `CaptureStep` + `advance_with_capture` — the deterministic loop. |
| `src/iladub/m4.py` (modify) | Add `capture_context(offer_path, terms_path) -> Graph` wrapping SP1. |
| `tests/test_loop.py` (create) | Pure-loop unit test (stub `capture_fn`) + SP1-backed monkeypatched scenario + live-gated smoke. |
| `docs/use-case-transplant-m4.md` (modify) | SP3b section. |

**Existing interfaces this builds on (confirmed):**
- `timeline.readiness(milestone, context_graph, subject) -> Readiness` (`.ready` bool property, `.missing` tuple).
- `timeline.next_capture_plan(timeline, current, context_graph, subject) -> CapturePlan | None` (`.milestone_id`, `.needed`).
- `timeline.Cursor(timeline)`: `.current` (property → `Milestone`), `.advance(context_graph, subject) -> bool`.
- `timeline.Timeline.from_graph(graph) -> Timeline`.
- `m4`: `read_document`, `extract_offer`, `to_rdf` already imported; `_TXD` constant; default terms at `os.path.join(_TXD, "transplant-terms.ttl")`.
- SP1 sync BAML callable is `baml_client.sync_client.b` (monkeypatch target).

**`CaptureStep` (defined in `loop.py`):**
```python
@dataclass
class CaptureStep:
    captured: Graph
    readiness_before: Readiness
    readiness_after: Readiness
    advanced: bool
    still_missing: tuple[URIRef, ...]
    next_plan: CapturePlan | None
```

**Namespaces:** `TX = Namespace("https://example.org/transplant#")`.

## Notes for the implementer
- Repo root `/Volumes/WD Green/dev/git/iladub`, branch `closed-loop-sp3b` (already created). Commit per task. Venv `/Volumes/WD Green/dev/git/iladub/.venv/bin/python`; run `python -m pytest`.
- The loop is deterministic. `capture_fn` is the LLM seam — in the SP1-backed test it runs `capture_context` with the BAML agents monkeypatched; the pure-loop unit test uses a plain stub returning a fixed graph (no BAML at all).
- `next_plan` is computed from the **pre-advance** cursor position (so after readying M4 and advancing to M5, `next_plan` reports M5's remaining needs). Full suite must stay green.

---

### Task 1: The loop orchestrator (`advance_with_capture`)

**Files:**
- Create: `src/iladub/loop.py`
- Test: `tests/test_loop.py`

- [ ] **Step 1: Write the failing pure-loop unit test (stub capture_fn, no BAML)**

Create `tests/test_loop.py`:
```python
import os
from rdflib import Graph, Namespace, Literal
from iladub.timeline import Timeline, Cursor
from iladub.loop import advance_with_capture

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")
TX = Namespace("https://example.org/transplant#")


def _heart():
    return Timeline.from_graph(Graph().parse(os.path.join(TXD, "heart-timeline.ttl"), format="turtle"))


def _captures(*props):
    # a stub capture_fn that "captured" the given properties on tx:offer
    def fn():
        g = Graph()
        for p in props:
            g.add((TX["offer"], p, Literal("x")))
        return g
    return fn


def test_capture_readies_current_and_advances():
    tl = _heart()
    cursor = Cursor(tl)                     # at M4, which requires {organ, aboGroup}
    ctx = Graph()                           # empty -> M4 not ready
    step = advance_with_capture(tl, cursor, ctx, _captures(TX.organ, TX.aboGroup), TX["offer"])
    assert step.readiness_before.ready is False
    assert step.readiness_after.ready is True
    assert step.advanced is True
    assert cursor.current.order == 5
    # forward look: M5 still needs recipientReady (the stub did not capture it)
    assert step.next_plan is not None
    assert TX.recipientReady in step.next_plan.needed


def test_no_advance_when_capture_insufficient():
    tl = _heart()
    cursor = Cursor(tl)
    ctx = Graph()
    step = advance_with_capture(tl, cursor, ctx, _captures(TX.organ), TX["offer"])  # abo missing
    assert step.advanced is False
    assert cursor.current.order == 4
    assert TX.aboGroup in step.still_missing
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_loop.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'iladub.loop'`.

- [ ] **Step 3: Implement `src/iladub/loop.py`**

Create `src/iladub/loop.py`:
```python
"""Closed-loop anticipation: drive capture to ready the current milestone, merge
the result, and advance. Deterministic — the only non-deterministic surface is the
supplied capture_fn (which, for the transplant case, runs the SP1 LLM funnel)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rdflib import Graph, URIRef

from .timeline import (Timeline, Cursor, Readiness, CapturePlan,
                       readiness, next_capture_plan)


@dataclass
class CaptureStep:
    captured: Graph
    readiness_before: Readiness
    readiness_after: Readiness
    advanced: bool
    still_missing: tuple[URIRef, ...]
    next_plan: CapturePlan | None


def advance_with_capture(timeline: Timeline, cursor: Cursor, context_graph: Graph,
                         capture_fn: Callable[[], Graph], subject: URIRef) -> CaptureStep:
    before = readiness(cursor.current, context_graph, subject)
    captured = capture_fn()
    for triple in captured:
        context_graph.add(triple)
    after = readiness(cursor.current, context_graph, subject)
    # Forward look BEFORE advancing: the next milestone and the needs it still has.
    plan = next_capture_plan(timeline, cursor.current, context_graph, subject)
    advanced = cursor.advance(context_graph, subject)
    return CaptureStep(captured=captured, readiness_before=before, readiness_after=after,
                       advanced=advanced, still_missing=after.missing, next_plan=plan)
```

- [ ] **Step 4: Run the test + full suite**

Run: `python -m pytest tests/test_loop.py -v && python -m pytest -q`
Expected: both new tests PASS; full suite green.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/loop.py tests/test_loop.py
git commit -m "feat(sp3b): advance_with_capture loop orchestrator (deterministic)"
```

---

### Task 2: Transplant `capture_context` helper

**Files:**
- Modify: `src/iladub/m4.py`
- Test: add to `tests/test_loop.py`

- [ ] **Step 1: Add the failing test (SP1 agents monkeypatched → grounded graph)**

Append to `tests/test_loop.py`:
```python
from baml_client import sync_client
from baml_client.types import DonorClinical, Immunology, Logistics, CodedConcept
from iladub.m4 import capture_context

OFFER = os.path.join(TXD, "offer.txt")


def _patch_agents(monkeypatch):
    cc = lambda v, q, c=0.9: CodedConcept(value=v, source_quote=q, confidence=c)
    monkeypatch.setattr(sync_client.b, "ExtractDonorClinical",
        lambda doc: DonorClinical(organ=cc("Heart", "Organ offered: HEART"),
                                  ejectionFraction=cc("60", "LVEF 60%"),
                                  causeOfDeath=cc("anoxic brain injury", "anoxic brain injury"),
                                  sizeMetric=cc("78 kg", "Donor size: 78 kg")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractImmunology",
        lambda doc: Immunology(aboGroup=cc("O", "Blood group: O"),
                               hlaTyping=cc("A2, B7, DR15", "HLA: A2, B7, DR15"),
                               serology=cc("HIV negative", "HIV negative")), raising=True)
    monkeypatch.setattr(sync_client.b, "ExtractLogistics",
        lambda doc: Logistics(projectedTransportMinutes=cc("95", "estimated transport 95 minutes")),
        raising=True)


def test_capture_context_grounds_organ_and_abo(monkeypatch):
    _patch_agents(monkeypatch)
    g = capture_context(OFFER)
    assert (TX["offer"], TX.organ, Literal("Heart")) in g
    assert (TX["offer"], TX.aboGroup, Literal("O")) in g
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_loop.py -k capture_context -v`
Expected: FAIL with `ImportError: cannot import name 'capture_context' from 'iladub.m4'`.

- [ ] **Step 3: Add `capture_context` to `src/iladub/m4.py`**

In `src/iladub/m4.py`, add this function (it reuses the module's existing imports
`read_document`, `extract_offer`, `to_rdf`, `Graph`, and the `_TXD` constant):
```python
def capture_context(offer_path: str,
                    terms_path: str = os.path.join(_TXD, "transplant-terms.ttl")) -> Graph:
    """Run the SP1 funnel over a document and return the grounded (asserted) graph,
    suitable as a capture_fn body for the timeline loop (loop.advance_with_capture)."""
    text = read_document(offer_path)
    terms = Graph().parse(terms_path, format="turtle")
    return to_rdf(extract_offer(text), terms).graph
```

- [ ] **Step 4: Run the test + full suite**

Run: `python -m pytest tests/test_loop.py -k capture_context -v && python -m pytest -q`
Expected: PASS; full suite green (the two pre-existing `*_live` tests remain skipped).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/m4.py tests/test_loop.py
git commit -m "feat(sp3b): capture_context wraps the SP1 funnel for the loop"
```

---

### Task 3: End-to-end closed-loop scenario (SP1-backed) + live-gated smoke

**Files:**
- Modify: `tests/test_loop.py`

- [ ] **Step 1: Add the failing end-to-end test (capture_fn = SP1 over the offer doc)**

Append to `tests/test_loop.py`:
```python
import pytest


def test_closed_loop_readies_m4_from_offer_and_advances(monkeypatch):
    _patch_agents(monkeypatch)
    tl = _heart()
    cursor = Cursor(tl)                 # at M4
    ctx = Graph()                       # empty
    step = advance_with_capture(tl, cursor, ctx, lambda: capture_context(OFFER), TX["offer"])
    assert step.readiness_before.ready is False
    assert step.readiness_after.ready is True
    assert step.advanced is True
    assert cursor.current.order == 5
    assert step.next_plan is not None and TX.recipientReady in step.next_plan.needed


@pytest.mark.skipif(os.environ.get("BAML_LIVE") != "1",
                    reason="set BAML_LIVE=1 to call the real API")
def test_closed_loop_live():
    tl = _heart()
    cursor = Cursor(tl)
    ctx = Graph()
    step = advance_with_capture(tl, cursor, ctx, lambda: capture_context(OFFER), TX["offer"])
    assert step.advanced is True
    assert cursor.current.order == 5
```

- [ ] **Step 2: Run it to verify it passes offline (live skipped)**

Run: `python -m pytest tests/test_loop.py -v`
Expected: all offline loop tests PASS; `test_closed_loop_live` SKIPPED.

- [ ] **Step 3: Run the full suite**

Run: `python -m pytest -q`
Expected: full suite green; exactly the live tests (`test_ping_live`, `test_compile_offer_live`, `test_closed_loop_live`) skipped.

- [ ] **Step 4: Commit**

```bash
git add tests/test_loop.py
git commit -m "test(sp3b): end-to-end closed-loop scenario (offline + live-gated)"
```

---

### Task 4: Documentation

**Files:**
- Modify: `docs/use-case-transplant-m4.md`

- [ ] **Step 1: Append the SP3b section**

Append to `docs/use-case-transplant-m4.md`:
```markdown

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
```

- [ ] **Step 2: Verify markdown**

Run: `python -c "t=open('docs/use-case-transplant-m4.md').read(); assert 'SP3b' in t and 'advance_with_capture' in t; print('ok')"`
Expected: prints `ok`.

- [ ] **Step 3: Commit**

```bash
git add docs/use-case-transplant-m4.md
git commit -m "docs(sp3b): closed-loop section in the transplant use case"
```

---

## Coverage map (plan ↔ spec)
- Spec §3 (orchestrator + `CaptureStep`) → Task 1. §4 (`capture_context`) → Task 2. §5 (money-shot scenario) → Tasks 1 (stub) + 3 (SP1-backed). §6 (testing: pure-loop unit, SP1-backed, live-gated) → Tasks 1–3. §7 (files) → all tasks.
- Spec §2 out-of-scope (targeted per-milestone extraction, multi-document driver, auto event sources, cursor rewind) → not built.
- `next_plan` computed pre-advance (spec §3 step 4, §8 open item resolved) → Task 1 `advance_with_capture`.

## Note on the `capture_fn` seam
`advance_with_capture` never imports or calls BAML — it only invokes `capture_fn()`. This keeps
the orchestrator a pure, deterministic function (the pure-loop unit test in Task 1 uses a stub
`capture_fn` with no BAML at all). The LLM enters only when the caller passes
`lambda: capture_context(...)`, and the offline tests monkeypatch the SP1 agents — so CI never
calls the API.
