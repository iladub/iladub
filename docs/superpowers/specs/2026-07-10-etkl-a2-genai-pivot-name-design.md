# ET(K)L Loop A2.1 — GenAI-Proposed Pivot Dimension Names — Design

**Date:** 2026-07-10
**Author:** François Rosselet
**Status:** Design approved (sections 1–3); ready for implementation plan.
**Parent design:** `docs/superpowers/specs/2026-07-10-etkl-inverse-report-grammar-design.md` (§4 three-tier
disposition; §6 LOOP A2). **Builds on:** Loop A1 core (shipped on `main`) — the reshape recipe, the round-trip
reproduction oracle, and the derived `tab:NormalizedBase` projection.

---

## 1. Goal & scope

Loop A1 recovers reshape recipes deterministically and **escalates** what it cannot resolve. One common escalation:
a report pivots a dimension into the header axis but gives it **no spanning-parent name** (e.g. columns `Q1 Q2 Q3
Q4` with no "Quarter" header). A1 recovers the *structure* — `PivotedDimension(name=None, values=[Q1,Q2,Q3,Q4])`
— but, lacking a name, emits no `UnpivotOp` and no base facts (it short-circuits to "nothing to invert").

**A2.1 supplies the missing name via GenAI, boxed by BAML, and admits it as an accountable proposition.** This is
the first GenAI slice of the grammar: it proves the **propose → oracle → promote** machinery end-to-end on the
thinnest possible case, where the model supplies a single typed value (a name) and the reshape is still certified
deterministically.

**In scope:** A2.1 (ambiguous/implicit pivot dimension **name** for a nameless **column** pivot with intact
structure). **Out of scope (later slices):** A2.2 (non-obvious aggregation function/subset), A2.3 (ambiguous
nesting), row-axis nameless pivots, and any op whose *identity* (not just a parameter) is ambiguous.

### Verified premise (probed 2026-07-10 against `main`)
`recover_dimensions` on a nameless column pivot returns `PivotedDimension(name=None, values=[Q1..Q4])` — the
structure is recovered; only the name is missing. `recover_recipe`'s guard (`d.name and len(d.values) > 1`) skips
it, so `certify` yields `recipe=[]`, `base=[]`, `NormalizedBase=None`. A2.1 fills exactly that gap.

## 2. The honest epistemic split (why this slice matters)

The dimension **name does not affect the round-trip**: the oracle reproduces cell *values*, and the dimension name
is only a *coordinate label* on the base facts. A nameless-but-sound pivot round-trips whether we call the dimension
"Quarter" or "Xyzzy". Therefore:

- **The reshape structure is oracle-certified** (deterministic, as in A1).
- **The name is a model PROPOSITION** — accountable, provenance-bearing, confidence-scored, **never asserted as
  fact** and **never claimed to be oracle-verified.**

This is precisely iladub's assert-vs-propose contract (Core Principle 3), and A2.1 is the cleanest place to model
it correctly: GenAI *names*, geometry *certifies the reshape*, and the name rides as an `iladub:CandidateConcept`
admitted by an `iladub:PromotionDecision`.

## 3. Architecture — A2 is an augmenting pass; A1 is untouched

A1's deterministic `certify`/`recover_recipe` are **not modified**. A2 layers a separate entry point on top:

```
certify(g, t)                              # A1 — deterministic, unchanged
  └─ name=None column pivot → un-inverted (structure sound, no UnpivotOp)  → escalated
        │
        ▼
certify_with_proposals(g, t, proposer)     # A2 — new entry point
  1. detect name=None column pivots with intact structure (values > 1)   # ONLY these consult the model
  2. Proposal = proposer.propose_dimension_name(values, context)  →  (name, confidence, rationale) | None
  3. inject the name → build the recipe (reuse recover_recipe machinery) → recover_base → round-trip oracle
  4. round-trips → emit NormalizedBase  +  CandidateConcept + PromotionDecision (the name's provenance)
        else / no proposal → escalate (residue), assert nothing
```

Properties:
- **A1 remains the default and is byte-for-byte unchanged.** With no proposer, behaviour equals today's.
- **Assert-first:** the proposer is consulted **only** for a name=None structural pivot (residue) — never when
  deterministic recovery already succeeds. (Cost discipline + the three-tier order: assert, then propose.)
- **The oracle still gates the reshape.** The proposed name is injected and the reshape must round-trip. The name
  itself is not oracle-verified; it is promoted as a proposition.

### The proposer seam (containment + offline-testability)
```python
@dataclass(frozen=True)
class Proposal:
    name: str
    confidence: float
    rationale: str

class Proposer(Protocol):
    def propose_dimension_name(self, values: list[str], context: dict) -> Proposal | None: ...
```
- **`FakeProposer(name, confidence)`** — deterministic, offline; injected by all unit tests. No API key, no network.
- **`BamlProposer`** — the live default; **lazily** imports `baml_client` and calls the BAML function. Constructed
  only when `BAML_LIVE=1` **and** `baml_client` is importable (mirrors the repo's existing baml-skip pattern). Never
  imported at module top level, so the deterministic code path has no BAML dependency.

## 4. The BAML function (the containment boundary)

For A2.1 the *op* is known deterministically (a nameless column pivot ⇒ `UnpivotOp`); only its `dimension` field is
unknown. The typed slot the model fills is the name:

```baml
class DimensionNameProposal {
    name: string @description("the single attribute/dimension these column labels are the values of"),
    confidence: float @description("0.0-1.0, calibrated"),
    rationale: string,
}

function ProposeDimensionName(values: string[], stub: string?, table_title: string?)
    -> DimensionNameProposal {
    client: Claude
    prompt: #"These column labels are the VALUES of one pivoted dimension: ${values}.
             The row-key column is ${stub}. Name the dimension (one word / short phrase).
             ${ctx.output_format}"#
}
```

The return type **is** the schema — the model cannot emit anything but a typed `DimensionNameProposal`. (The
broader "return type is the op *union*" containment fully manifests in A2.2/A2.3, where the op *choice* is
ambiguous; for A2.1 it is a typed name slot in a fixed op. Stated honestly, not over-modelled.) `client: Claude`
reuses the existing `baml_src/clients.baml` client. `baml_client` is regenerated and stays pinned to the installed
`baml-py` (0.222.0) — the two versions must always match (a mismatch hard-errors on import).

## 5. The promotion emission (reuse the epistemic vocab; near-zero new terms)

When the injected name makes the reshape round-trip, emit — alongside the `NormalizedBase` — the name's
accountable provenance, consuming the existing `iladub:`/`dec:` vocabulary:

```turtle
# the proposition — the name is a CandidateConcept, never a bare assertion
_:cand a iladub:CandidateConcept ;
    iladub:surfaceText "Q1 | Q2 | Q3 | Q4" ;         # the evidence that suggested it
    rdfs:label "Quarter" ;                            # the proposed name
    iladub:suggestedBy <urn:iladub:suggester/baml.ProposeDimensionName@claude-opus-4-8> ;
    iladub:confidence 0.9 .

# the accountable act — a PromotionDecision (subclass of dec:DecisionHolon, a prov:Activity)
_:pd a iladub:PromotionDecision ;
    iladub:reviews _:cand ;
    dec:decidedBy <urn:iladub:suggester/baml.ProposeDimensionName@claude-opus-4-8> ;   # a prov:Agent
    dec:consideredEvidence <…the-table>, _:cand ;     # the grid region + the candidate
    dec:confidence 0.9 ;
    dec:rationale "Reshape round-trips exactly with dimension=Quarter; the name is a model proposition, not oracle-verified." ;
    dec:produced <…normbase> .                         # the derived base it unlocked

# the admitted name carries its provenance
<…unpivot-op-or-coordinate> iladub:wasPromotedBy _:pd .
```

- The honesty split is written into the record: `dec:rationale` + `dec:consideredEvidence` state that the
  **structure is oracle-certified** while the **name is a model proposition at confidence C** — never conflated.
- Satisfies iladub's SHACL invariant *"an admitted/promoted node is produced by a promotion decision"* — the
  GenAI-admitted name is, by construction, the product of one. (The deterministic A1 base facts are unaffected:
  they are asserted, not promoted; only the GenAI-proposed name gains a `PromotionDecision`.)
- **New vocabulary:** essentially none in the core. Consume `iladub:CandidateConcept`/`PromotionDecision`/`reviews`/
  `suggestedBy`/`confidence`/`wasPromotedBy` and `dec:*`. Add at most **one thin `tab:` link** so the recipe's
  `UnpivotOp` (or the base-fact coordinate) points at its `PromotionDecision`, plus a **stable Suggester IRI
  convention** for the model agent (`urn:iladub:suggester/<baml-fn>@<model-id>`). Any new term is owned and thin.

## 6. Testing — offline-first; the model call is the only gated part

100% of the *logic* (detection, name injection, oracle, promotion emission) is tested offline with `FakeProposer`;
only the real model call sits behind a gate.

**Offline unit tests (no API key, no network):**
- **happy path** — nameless-pivot graph + `FakeProposer("Quarter", 0.9)` → `NormalizedBase` emitted, 8 base facts
  carry the `Quarter` coordinate, oracle_ok.
- **promotion triples** — assert the `CandidateConcept` (label "Quarter", `confidence`, `suggestedBy` the agent) +
  `PromotionDecision` (`reviews` it, `decidedBy` the agent, `produced` the base, `dec:rationale` carries the
  structure-certified / name-a-proposition split) + the admitted name `iladub:wasPromotedBy` it.
- **escalation guards (three — because the name does not affect the round-trip):**
  1. `FakeProposer` returns `None` → escalate: no `NormalizedBase`, no promotion (A1 behaviour preserved).
  2. a name=None region that is **not cleanly invertible** (ragged/irregular values) → even with a proposed name
     the oracle **rejects** → escalate, nothing asserted.
  3. **no-call guard** — a fully *named* pivot → A1 already inverts it; A2 must **not** invoke the proposer at all
     (assert-first). Assert the proposer is never called (e.g. a spy proposer that raises if called).

**Gated live smoke test:** behind `BAML_LIVE=1` + `baml_client` importable + API key (mirrors the repo's existing
BAML smoke tests). Real `ProposeDimensionName(["Q1","Q2","Q3","Q4"])` returns a plausible name. Skipped in normal
CI. No network in the default suite.

**Showcase (Part J):** leads with the rendered original PDF (a nameless-pivot report); shows A1 **escalating** it
(no base), then A2 naming the dimension, the reshape round-tripping, base emitted, and the `PromotionDecision`
printed — accountable: "model proposed 'Quarter' @0.9; structure certified, name a proposition." To keep the
notebook **offline-reproducible to 0 errors** (standing directive: zero network in the demo), the showcase injects
a **recorded/deterministic proposer**, narrating that live it is a BAML call. The demo stays zero-network while
honestly showing the promotion.

## 7. File structure

| File | Responsibility |
| --- | --- |
| `baml_src/reshape_propose.baml` (create) | `ProposeDimensionName` + `DimensionNameProposal`; regenerate `baml_client` (pinned to baml-py 0.222.0) |
| `src/iladub/etkl/propose.py` (create) | `Proposal`, `Proposer` protocol, `FakeProposer`, lazy/gated `BamlProposer` |
| `src/iladub/etkl/promote.py` (create) | emit `CandidateConcept` + `PromotionDecision` + `wasPromotedBy` for a promoted name |
| `src/iladub/etkl/reshape.py` (modify) | add `certify_with_proposals(g, t, proposer)`; **A1 functions unchanged** |
| `vocab/ontology/tab.ttl` (modify, thin) | at most one `tab:`→`PromotionDecision` link property |
| `tests/etkl/test_propose.py` (create) | offline: happy path + no-call guard |
| `tests/etkl/test_promote.py` (create) | offline: promotion triples + escalation guards |
| `tests/test_baml_propose_smoke.py` (create) | gated live smoke (`BAML_LIVE`) |
| `demo/etkl_1a_showcase.ipynb` (modify) | Part J — nameless pivot → A1 escalates → A2 names + promotes |

## 8. Honest gaps & non-goals

- **The name is never oracle-verified.** A2.1's oracle gates the *reshape*, not the *name*. A confidently-wrong
  name (e.g. "Period" instead of "Quarter") would still round-trip and be admitted — as a proposition at the
  model's confidence, with full provenance, reviewable/revisable. This is by design (the honest split), not a bug;
  the mitigation is accountability, not certification.
- **Column pivots only.** Row-axis nameless pivots are deferred.
- **A2.1 fills a name in a *fixed* op (`UnpivotOp`).** The stronger containment ("return type is the op *union*, the
  model cannot pick a non-grammar op") is only fully exercised when the op *choice* is ambiguous — A2.2/A2.3.
- **Calibration of `confidence`** is the model's; we record it, we do not re-scale it. Downstream policy on a
  minimum confidence to admit is out of scope for A2.1 (everything that round-trips is admitted, tagged with its
  confidence).
- **No deterministic name heuristics.** We do NOT hand-code `Q1..Q4 → "Quarter"` lookups — that is exactly the
  neolegacy trap. A nameless pivot goes straight to the proposer.

## 9. Relationship to prior work
- **Builds on** A1 core (recipe + oracle + `NormalizedBase`), untouched.
- **Consumes** the existing `iladub:` promotion epistemics + `dec:` decision vocabulary + the repo's BAML wiring
  (`baml_src/`, `baml_client`, the `client: Claude`).
- **Implements** the parent design's §4 three-tier PROMOTE tier and the BAML containment invariant, on the thinnest
  real case.
