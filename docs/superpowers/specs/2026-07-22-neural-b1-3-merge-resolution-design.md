# NEURAL Loop B1.3 — Narrow-Flank Merge Resolution (propose → SHACL-oracle → promote)

**Date:** 2026-07-22
**Status:** Design — approved for spec (brainstorm 2026-07-22).
**Slice:** The first genuine **NEURAL** slice of the span-perception layer. Resolves the
`MERGE_AMBIGUOUS` escalations that loop **B1.2** deliberately left as a clean, quarantined input
(see `docs/superpowers/specs/2026-07-18-neural-span-perception-design.md` §2.8 — "the deferred
NEURAL residual, loop B1.3").

**Gate context (CLAUDE.md §8):** classified before any procedural code. This slice is **NEURAL**:
a genuinely perceptual "which columns does this span cover" reading judgment, resolved by
**GenAI-via-BAML proposing** under the assert/propose/promote epistemics (§3), **disposed by a
semantic oracle** (`region_tiles`, the loop-C tiling SHACL), never by a tuned tolerance or a
confidence gate. It composes three shipped loops — A2 (`reshape.certify_with_proposals`, the
propose→oracle→promote exemplar), B1.2 (the `HeaderNode.ambiguous` detect→escalate seam), and C
(`tiling.region_tiles`, the tiling SHACL oracle) — and invents no new oracle.

---

## 1. The decision (one sentence)

When B1.2 has flagged a header node `ambiguous` because a **narrow orphan flank** column sits in
the tie-band (geometry provably cannot decide whether the flank belongs *under the span* or is a
*standalone leaf*), a BAML proposer reads the labels + ink and **proposes** one reading;
`region_tiles` **rejects** structurally-illegal readings; a surviving **legal** reading is admitted
**only as an `iladub:CandidateConcept` promoted by an `iladub:PromotionDecision`** — a proposition,
never asserted as grounded truth. No proposer, no legal reading, or an illegal proposal → **escalate
`MERGE_AMBIGUOUS`** exactly as today.

## 2. Why NEURAL (the gate justification — stated in code and spec)

B1.2 established (its §2.2) that the rival readings both sit inside `_centered_run`'s `0.25·pitch`
tie-band **and** `merge_tiling_ok`'s `0.5·pitch` centering tolerance: **geometry is blind** to which
reading is correct. There is no *symbolic* fact to derive it from — a header-empty orphan flank has
no evidence, and deriving "it belongs / it doesn't" from the *absence* of a header would violate §7
(assert only what the source supports). So it is neither AXIOM nor PROCEDURAL: it is a **perceptual
NEURAL** judgment. The honest resolution is to **propose** a reading (model), **dispose** it against
a proposer-independent structural oracle (`region_tiles`), and **promote** the survivor as a
proposition (§3) — never assert it as ground truth.

**Oracle disposal semantics (the load-bearing design decision).** For a narrow-orphan flank, BOTH
readings are frequently *structurally legal* — both cover the leaves with no overlap, so
`region_tiles` admits both. `region_tiles` therefore does **not** uniquely discriminate the reading;
its job is to **reject structurally-illegal proposals** (gaps, overlaps, refinement or
unambiguous-leaf-access violations). Among legal readings, the model's pick is admitted **only as a
proposition**: an `iladub:CandidateConcept` reviewed by an `iladub:PromotionDecision` whose
`dec:rationale` records that geometry tied, the model chose, and the oracle confirmed legality. This
is exactly §3 — the span reading is *never* asserted as grounded truth; it is a quarantined
candidate admitted by an accountable, oracle-guarded promotion. The distinction from "an LLM guess
replacing geometry": geometry is not being replaced (it correctly tied); the model fills a **named**
gap, and the result is carried as a proposition with full provenance, not asserted.

This is coherent with the standing "oracle, not confidence" rule: **legality gates admission, not
confidence.** A wrong or overconfident proposal that produces an illegal tiling is rejected by
`region_tiles` regardless of its confidence; a genuine overlap collision (no legal tiling for any
reading) can never be promoted and stays escalated.

## 3. Components (each single-purpose)

### 3.1 `SpanProposer` seam (`src/iladub/etkl/propose.py`, parallel to the shipped `Proposer`)

- `SpanProposal(choice: str, confidence: float, rationale: str, suggester_iri: str)` — frozen
  dataclass; `choice ∈ {"absorb", "standalone"}`.
- `SpanProposer` Protocol: `propose_header_span(self, context: dict) -> SpanProposal | None`.
- `FakeSpanProposer` — deterministic offline proposer holding a fixed `SpanProposal | None`
  (tests/showcase). Returns `None` to model abstention.
- `BamlSpanProposer` — live path: `propose_header_span` lazy-imports `baml_client` and calls a new
  BAML `ProposeHeaderSpan` function; env-gated by the existing `baml_proposer_available()`
  (`BAML_LIVE=1` + `baml_client` importable). `suggester_iri="urn:iladub:suggester/baml.ProposeHeaderSpan"`.

The proposer `context` carries what a faithful reader needs and nothing more: the spanning parent
label, the neighbouring leaf sub-labels (in column order), the tied flank's leaf label (may be
empty), and the flank side (`"left"|"right"`). No geometry constants leak into the proposer.

### 3.2 Tie carry-through (`src/iladub/etkl/headers.py`)

`resolve_narrow_flanks` today sets only `ambiguous=True`. Extend `HeaderNode` with
`ambiguous_flank: int | None = None` and record the tied leaf column when `_narrow_flank_tie` fires.
Additive; B1.2 detect→escalate semantics unchanged (a node with `ambiguous=True` still escalates
whenever no proposer resolves it). `infer_header_tree`'s parent-linking reconstruction must carry the
new field through (same discipline the `ambiguous` flag already required).

### 3.3 Candidate-reading builder (`src/iladub/etkl/span.py`, new — single purpose)

Given the ambiguous node and its `ambiguous_flank` f, produce the header tree under a chosen reading:
- `absorb` — the node's `covers` include f (the span owns the flank);
- `standalone` — f is removed from the node's `covers` and becomes a top-level leaf node.

Pure structural rewrite over `HeaderNode`s; no geometry, no constant.

### 3.4 Oracle reuse (`src/iladub/etkl/tiling.py::region_tiles`, unchanged)

Build a scratch region graph under the proposed reading and tile-check it — mirroring the shipped
matrix path (`compile.py:194–197`: build scratch → `region_tiles(scratch)` → `graph += scratch`).
`region_tiles` is the closed-world SHACL conformance oracle (coverage / no-overlap / refinement /
unambiguous-leaf-access, both axes). No change to the oracle.

### 3.5 Span-promotion emitter (`src/iladub/etkl/promote.py`, sibling of `emit_promotion`)

`emit_span_promotion(g, region, node, flank, choice, proposal)` writes:
- an `iladub:CandidateConcept` for the chosen span reading (`rdfs:label`, `iladub:surfaceText` =
  the flank/leaf labels, `iladub:suggestedBy` the suggester, `iladub:status iladub:proposed`,
  `iladub:confidence`);
- an `iladub:PromotionDecision` (`dec:DecisionHolon`) reviewing it, `dec:rationale` =
  *"geometry tied at narrow flank col f; model proposed &lt;choice&gt;; region_tiles confirms
  structurally legal; the span reading is a proposition, not oracle-verified as unique. Rationale:
  &lt;proposal.rationale&gt;"*, `dec:confidence`, `dec:consideredEvidence` the region + candidate,
  `dec:produced` the region.

Reuses the exact provenance shape `emit_promotion` established for A2.

### 3.6 Compile plumbing (`src/iladub/etkl/compile.py`)

`compile_tables(pdf_path, page_number=0, validate_shapes=True, span_proposer=None)`. At the
hierarchical `not merge_tiling_ok(hreg.tree, hreg.grid)` branch (`compile.py:224`): if the ambiguity
is a **narrow-flank tie** (some node has `ambiguous_flank is not None`) **and** `span_proposer` is
present, run propose → build reading → `region_tiles` → on a legal reading, `emit_span_promotion`,
`graph += scratch`, assert the hier region (carrying the proposition provenance), count its cells
asserted; otherwise `escalate_region(MERGE_AMBIGUOUS)` exactly as today. Multiple ambiguous nodes are
resolved independently; if any cannot be legally resolved, the whole region escalates.

## 4. Data flow

```
infer_header_tree
  -> resolve_narrow_flanks: node.ambiguous=True, node.ambiguous_flank=f      (B1.2, PROCEDURAL detect)
compile_tables (span_proposer present?)
  -> merge_tiling_ok == False  (some node ambiguous)
  -> narrow-flank tie? and proposer present?
       -> propose_header_span(context) -> SpanProposal(choice) | None        (NEURAL propose, BAML)
       -> build reading (absorb|standalone) -> scratch region RDF            (structural)
       -> region_tiles(scratch)                                             (SHACL oracle dispose)
            legal   -> emit_span_promotion + graph += scratch + assert region as PROPOSITION
            illegal -> escalate_region(MERGE_AMBIGUOUS)
       -> None / no proposer -> escalate_region(MERGE_AMBIGUOUS)             (unchanged default)
```

## 5. Testing (offline; injected `FakeSpanProposer`; run via `./.venv/bin/python -m pytest`)

Three behavioral pins on the **real** `compile_tables` engine, plus units. The resolution fixture is
the narrow-orphan geometry from B1.2's gate (`tests/etkl/test_span_gate.py` — a legal tiling exists,
geometry ties); the negative fixture is `offcenter_merge_report_pdf` (overlap collision, no legal
tiling).

1. **Resolves (the close):** `FakeSpanProposer` returning the tiling choice → the region that
   escalated `MERGE_AMBIGUOUS` in B1.2 now **asserts** a `HierarchicalTable`, and the graph carries a
   `PromotionDecision` + `CandidateConcept` for the span reading. **RED-check**: removing the B1.3
   resolution path makes exactly this test fail (non-vacuous).
2. **Abstains → escalates:** `span_proposer=None` and a proposer returning `None` → **still**
   `MERGE_AMBIGUOUS`, byte-identical to today. Proves the default path is untouched.
3. **Illegal proposal → escalates (the oracle holds the gate):** a proposed reading whose scratch
   region violates tiling is **rejected by `region_tiles`** → the resolution refuses → the region
   stays `MERGE_AMBIGUOUS`. Because for a narrow-orphan *both* readings are usually legal, this is
   pinned at the builder+oracle seam: build a deliberately-illegal reading (e.g. a flank absorbed so
   it collides with a sibling's coverage, or a `standalone` that leaves a leaf-access violation),
   assert `region_tiles(scratch) is False`, and assert the resolution path escalates on it — **not**
   at the full-pipeline level, where an illegal-yet-tie fixture is hard to construct honestly. This
   is the load-bearing guard: **legality — not confidence — admits.**
4. **Overlap collision stays escalated (distinct from B1.3's scope):** on `offcenter_merge_report_pdf`
   (LEFT/RIGHT claims collide → `merge_tiling_ok==False` via the *overlap* check, no `ambiguous_flank`
   set), the region **never enters the resolution branch** even with a confident `FakeSpanProposer`
   present → stays `MERGE_AMBIGUOUS`. Proves B1.3 touches only narrow-flank ties and leaves genuine
   overlap collisions escalated (audit C2 / loop B2 territory).

Units: `SpanProposal` frozen/shape; the candidate-reading builder yields the expected covers for
`absorb` vs `standalone`; `region_tiles` returns `False` for the illegal reading of test 3;
`emit_span_promotion` writes the `CandidateConcept` + `PromotionDecision` with the tie-rationale;
`baml_proposer_available()` gating unchanged.

## 6. Anti-overfit (the standing rule)

The resolution is driven entirely by **injected proposer + SHACL oracle** — **zero tuned constants**
in the decision. Test 3 (oracle rejects an illegal reading) is the load-bearing guard: a
wrong/overconfident proposal cannot promote because `region_tiles` rejects illegal structure.
Confidence never gates admission; **legality does.**
The proposer is injected (Fake offline, BAML live + env-gated), so the logic is fully offline-testable
and the model is never on the test path.

## 7. Scope boundary (YAGNI)

- **Only** the single narrow-orphan tied flank (one endpoint column, B1.2's `_narrow_flank_tie`).
  General merged-header span (`_covers_for_cell`, audit C2) is **loop B2**, later.
- Genuine overlap collisions (offcenter) stay escalated — not in scope to resolve (no legal tiling to
  promote).
- Multiple ambiguous nodes: resolved independently; if any cannot be legally resolved, the region
  escalates.
- `span_proposer` defaults to `None` → **no behavior change to any shipped path**; live
  `BamlSpanProposer` stays `BAML_LIVE=1`-gated.
- Reuses shipped machinery (`region_tiles`, the `MERGE_AMBIGUOUS` seam, the A2 propose/promote
  pattern) — no new oracle, no new control flow beyond the resolution branch.
- The actual BAML `ProposeHeaderSpan` function definition (`.baml` source + generated client) is a
  live-path artifact; tests never touch it. Authoring/wiring the `.baml` is included, but its live
  behavior is exercised only under `BAML_LIVE=1`, never in CI.

## 8. Definition of done (the loop CLOSES)

- A previously-`MERGE_AMBIGUOUS` narrow-orphan region compiles to an **asserted** `HierarchicalTable`
  carrying `PromotionDecision` proposition-provenance, end-to-end through `compile_tables` with a
  `FakeSpanProposer` — RED-checked non-vacuous.
- With no proposer (or an abstaining one, or an illegal proposal / overlap collision), the region
  **still escalates** `MERGE_AMBIGUOUS`; every shipped `test_headers` / `test_hierarchical` /
  `test_merge_resolution` / `test_span_gate` fixture stays green.
- Honestly classified NEURAL (propose → SHACL-oracle → promote), stated in code and spec; no tuned
  constant gates the decision.
- Residue (unresolvable ties, illegal proposals, overlap collisions) escalated in-band, never dropped.

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
