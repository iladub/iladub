# `f:modify` write-gate — every grounded node ← an accountable decision, enforced at the commit

- **Date:** 2026-07-25
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). A single vertical slice ("loop F-write").
- **Context:** iladub's core invariant — *every grounded node is produced by an accountable `PromotionDecision`* — is enforced today as SHACL at the **app layer** (`iladub:GroundedNodeShape`, rejection-tested by `test_neg_grounded_without_promotion_fails`). The Fluree-substrate decision (`internal/decisions/2026-07-02-fluree-as-hga-substrate.md` §7) noted this becomes enforceable *"at Fluree's transaction-time SHACL gate."* This increment moves it to the **write/commit gate**: a transaction adding a grounded node without an accountable promotion is **rejected at commit**, and only the promotion's `dec:decidedBy` agent may write it. Completes the accountable-write chain begun by the governed read gate (PR #64) and the `f:view` enforcement compile (PR #65). **Declarative + CI-runnable — no Fluree server.**

---

## 1. Purpose and scope

Enforce the promotion invariant at the Fluree **commit**, on two axes:
- **Structural (reuse):** a `GroundedNode` without `iladub:wasPromotedBy` a `PromotionDecision`, or a `CandidateConcept` carrying `status asserted`, is **rejected** by the transaction-time SHACL gate (the existing `iladub:GroundedNodeShape` / `NoLeakShape`, packaged as the commit gate).
- **Authorization (new):** a static Fluree `f:modify` `AccessPolicy` — an identity may modify a `GroundedNode` **iff** it is the `dec:decidedBy` agent of the promotion that produced it.

Together: *a decision exists* **and** *the accountable decider wrote it* — the strongest form of "every grounded node ← an accountable decision," enforced where data is committed.

**In scope:**
- A static `f:modify` policy template (`src/iladub/fluree/f-modify-policy-template.jsonld`).
- A focused `src/iladub/etkl/writegate.py`: `commit_gate_shapes()`, `gate_admits(...)`, `certify_modify_authorization(...)` + `ModifyVerdict`.
- A demonstrator + tests (admit/reject/authorization + negatives).

**Non-goals (deferred, spec §8):**
- The **live-Fluree harness** (load transaction shapes + `f:modify` policy; attempt a bare-grounded-node commit → rejected; commit as a non-decider identity → denied) — local/internal, like the ReBAC benchmark.
- Gating `PromotionDecision` writes (only its `decidedBy` may write the decision itself) — a follow-up axis.
- `f:modify` for updates/retractions of already-grounded facts.
- Any change to the promotion invariant itself (reused verbatim, never re-authored).

**Success criteria:**
1. `gate_admits` **rejects** a `GroundedNode` lacking `wasPromotedBy` and a `CandidateConcept` carrying `status asserted`; **admits** a fully membrane-conformant graph (a complete candidate → accountable promotion → grounded node). (pySHACL, no server.)
2. `certify_modify_authorization` returns `ok` for the shipped template (it is `f:modify` and its `f:query` wires `?$identity` to `wasPromotedBy → decidedBy`); `is_modify` False for an `f:view` variant; `wires_accountable` False for a variant whose `f:query` omits `decidedBy`.
3. No new vocab, no CONSTRUCT; the promotion invariant is reused from `vocab/shapes/iladub-shapes.ttl`, not duplicated.
4. `f:` appears only in the `src/iladub/fluree/` template; `hfed:` unused; no Fluree server required.

---

## 2. Architecture and data flow

```
A transaction proposing to add a GroundedNode
   │
   ├── STRUCTURAL commit gate  (reuse iladub:GroundedNodeShape + NoLeakShape — SHACL, closed-world)
   │      GroundedNode without wasPromotedBy       → REJECTED at commit
   │      CandidateConcept carrying status asserted → REJECTED
   │
   └── AUTHORIZATION  (static f:modify AccessPolicy)
          ?$identity may f:modify ?$this  iff
            ?$this iladub:wasPromotedBy ?pd . ?pd dec:decidedBy ?$identity
          → only the accountable decider commits the fact
```

The structural gate is the neurosymbolic gate's **closed-world membrane** ("what may cross into the clean holon"), now applied at the **data commit** rather than only in app validation. The authorization policy renders "accountable" into write-authorization: the writer must *be* the promotion's decider.

---

## 3. Components

### 3.1 The static `f:modify` policy — `src/iladub/fluree/f-modify-policy-template.jsonld`
A Fluree-native, data-driven `f:AccessPolicy` (identical for any data — accountability travels in `wasPromotedBy`/`decidedBy`):
- `@type` includes `f:AccessPolicy`; `f:action` = `f:modify`; `f:required` true; `f:onClass` = `iladub:GroundedNode`.
- `f:query` (escaped-JSON `where`, full IRIs): `?$this https://w3id.org/iladub#wasPromotedBy ?pd` and `?pd https://w3id.org/iladub/dec#decidedBy ?$identity`.

So a write of a grounded node is authorized iff `?$identity` is the accountable `decidedBy` agent of its promotion. Consumed as a compile *target*, never authored as iladub ontology. Loadable via rdflib (`format="json-ld"`) for the structural check.

### 3.2 The structural commit gate (reuse — the FULL iladub membrane)
The commit gate is the **whole** iladub epistemic membrane (`vocab/shapes/iladub-shapes.ttl`), reused wholesale — validating everything that would cross into the clean holon on commit, of which the promotion invariant is the headline. The promotion invariant already lives there:
- `iladub:GroundedNodeShape` — `wasPromotedBy minCount 1` ("INVARIANT: every grounded node must be produced by a promotion decision"), `groundsTo minCount 1`, `status hasValue asserted`.
- `iladub:NoLeakShape` — a `CandidateConcept` must not carry `status asserted`.
- `iladub:PromotionDecisionShape` — the promotion is accountable (`reviews` a candidate, `dec:decidedBy` an agent).

This increment **reuses** them as the commit-gate shape-set — no re-authoring.

### 3.3 `src/iladub/etkl/writegate.py` (PROCEDURAL glue, justified)
- `commit_gate_shapes() -> Graph` — parse `vocab/shapes/iladub-shapes.ttl` (the commit-gate shape-set). No decision, no tuned constant.
- `gate_admits(transaction: Graph, knowledge: Graph) -> ValidationResult` — `validate(transaction, commit_gate_shapes(), knowledge)` (reuse `iladub.validate.validate`). `.conforms` False ⇒ the commit is rejected (a bare grounded node, or a leaked candidate).
- `ModifyVerdict(ok, is_modify, wires_accountable)` (frozen).
- `certify_modify_authorization(f_modify_policy: Graph) -> ModifyVerdict`:
  - `is_modify` = the policy carries `f:action f:modify` (and is an `f:AccessPolicy`).
  - `wires_accountable` = the `f:query` literal references `?$identity`, `https://w3id.org/iladub#wasPromotedBy`, and `https://w3id.org/iladub/dec#decidedBy` (it resolves the write to the accountable decider). Substring presence check (the `f:query` is an opaque Fluree DSL literal, as in PR #65).
  - `ok = is_modify and wires_accountable`.

---

## 4. Source-ownership & neurosymbolic gate

- **No new vocab, no CONSTRUCT.** Reuses `iladub:wasPromotedBy`, `dec:decidedBy`, `iladub:GroundedNode`, and the shipped invariant shapes.
- **Source-ownership:** `f:` (Fluree's, `https://ns.flur.ee/db#`) appears ONLY in the `src/iladub/fluree/` template (a compile target), outside the `vocab/`/`examples/`/`tests/*.ttl` trees the CI scans. The commit gate reuses owned `iladub-shapes.ttl`. No HGA term as a subject; `hfed:` unused.
- **Gate:** the commit gate is **CONSTRAINT → SHACL** (closed-world membrane, at the data commit — the gate's exact intent). `writegate.py` is **PROCEDURAL** glue (graph parse, `validate` delegation, substring presence check) — no domain decision, no tuned constant. No Python answers "may this write happen" — the SHACL shape and the `f:modify` policy do.

---

## 5. Demonstrator and testing

- **Demonstrator (domain-neutral):** a purpose-built, fully membrane-conformant admit fixture `tests/writegate-promoted.ttl` — a **complete** `CandidateConcept` (`surfaceText`, `suggestedAnchor`, `suggestedBy`, `confidence`, `fromRegion`, `status proposed`) → an accountable `PromotionDecision` (`reviews` the candidate, `dec:decidedBy` a curator) → an `iladub:GroundedNode` (`wasPromotedBy` the promotion, `groundsTo` a concept, `status asserted`). `gate_admits` conforms; the `f:modify` policy's `decidedBy` binding is certified. (Note: neither `examples/promotion.ttl` — its candidate is stripped — nor `holon-grounding-conformant.ttl` — HGA `GroundingRecord` bridge, no `iladub:GroundedNode` — is fully membrane-conformant, so a dedicated admit fixture is used.)
- **Tests (`tests/test_writegate.py`):**
  - `gate_admits` **admits** `tests/writegate-promoted.ttl` (a fully membrane-conformant, properly-promoted graph).
  - `gate_admits` **rejects** a bare grounded node — `tests/writegate-unpromoted.ttl` (a `GroundedNode` with `status asserted`, no `wasPromotedBy`); `.conforms` False, "promotion" in the report.
  - `gate_admits` **rejects** a leaked candidate — reuse `tests/leak-attempt.ttl`.
  - `certify_modify_authorization` on the shipped template → `ok` (`is_modify` and `wires_accountable`).
  - **Negative — not modify:** a template variant with `f:action f:view` → `is_modify` False, `ok` False.
  - **Negative — not accountable:** a variant whose `f:query` omits `decidedBy` → `wires_accountable` False, `ok` False.
  - A structural test that the shipped template is `f:modify` and its `f:query` binds `?$identity`, `wasPromotedBy`, `decidedBy`.

---

## 6. Relation to prior work and steering

- Completes the **accountable-data chain**: PR #64 (governed read projection) → PR #65 (`f:view` read enforcement at the data layer) → this (`f:modify` write enforcement + the promotion invariant at commit). Read and write are now both governed in-data.
- Realizes the Fluree-substrate decision's §7 promise: *"iladub's invariant — every grounded node produced by a promotion decision — now enforceable at Fluree's transaction-time SHACL gate."*
- Strengthens **iladub's core epistemic signature** (assert only what you can ground; every grounded node ← an accountable promotion) from an app-layer check into a data-commit guarantee — the sharpest statement of the promotion epistemics differentiator vs HGA's bare confidence gate.

---

## 7. Open questions / later increments

1. **Live-Fluree write-gate harness** (local/internal): load the transaction shapes + `f:modify` policy; attempt a bare-grounded-node commit → rejected; commit as a non-decider identity → denied — the empirical enforcement proof. Off the public repo (external dep, work-boundary).
2. Gate `PromotionDecision` writes too (only its `decidedBy` may write the decision), closing the "fabricate a promotion then a fact" path at the write layer (the structural gate already requires the promotion to be accountable; this adds write-authorization to the decision itself).
3. `f:modify` for updates/retractions of grounded facts (supersession/withdrawal as accountable writes).
4. Bind the committing identity to the `dec:decidedBy` via verifiable credentials (`hvc:`) for cross-org trust.
