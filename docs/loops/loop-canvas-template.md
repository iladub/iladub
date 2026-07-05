# The iladub Loop Canvas

One page. Fill it **outside-in** — Goal/Verifier first, Model last. Copy this file per loop.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ② PROBLEM  — the recurring class of work this loop owns · what stays human    │
├──────────────────┬───────────────────────────────────┬────────────────────────┤
│ ③ TRIGGER        │                                   │ ⑦ CONTROL              │
│  what starts a    │        ① GOAL / VERIFIER          │  after each verify:    │
│  run · concurrency│      the checkable "done" —       │  continue · retry ·    │
│                   │      a PROOF, not a claim.         │  repair · ESCALATE ·   │
├──────────────────┤      Designed FIRST. Must          │  ship   (= dec)        │
│ ④ ACTIONS (maker) │      GENERALISE to every doc.     ├────────────────────────┤
│  tools · scope ·  │                                   │ ⑤ STATE                │
│  isolation ·      │   score = validated% + escalated% │  holon-in-progress +   │
│  propose→validate │   silent-wrong is IMPOSSIBLE      │  durable skills        │
├──────────────────┴───────────────────┬───────────────┴────────────────────────┤
│ ⑥ LIMITS  caps · budget · no-progress │ ⑨ MODEL & PROMPT  (chosen LAST, residue │
│           detection (escalate, don't  │    only, swappable)                     │
│           spin)                        │                                         │
├───────────────────────────────────────┴─────────────────────────────────────────┤
│ ⑧ OBSERVABILITY  provenance-to-page · the dec decision log · the score · run trace│
└───────────────────────────────────────────────────────────────────────────────┘
      maker = proposer (stochastic where needed)  ·  checker = the deterministic ORACLE
```

## ① Goal / Verifier — *design this first*
The **checkable "done."** For iladub, the produced holon must **(a)** round-trip against the measured
evidence (re-render the reading; diff the geometry) **and (b)** conform to the contract/ontology (SHACL);
every emitted fact is a grounded **assertion** or an honest **proposition** (`dec`) — *never* a proposition
passed as an assertion. *If the gate is wrong, nothing else matters — and it must hold for **every**
document, not the one on screen.*

## ② Problem
The recurring class of work this loop owns (worth a system, not a one-off) — and what stays human-controlled.

## ③ Trigger
What starts a run (a document/region arrives; a re-grounding; a contract change) and the concurrency policy.

## ④ Actions (the maker)
The permitted operations, tool scope, network, and isolation. iladub shape: **measure → propose
(deterministic first, small model only on the residue) → validate → ground.** The maker proposes; it never
self-certifies.

## ⑤ State
What persists **between** runs: the **holon-in-progress** (this run) and **durable skills** (learned
generator signatures, kind patterns, ontology refinements) that make the loop better over time. The spine.

## ⑥ Limits
Hard stops: iteration caps, token/latency budget, circuit breakers, and **no-progress detection** — a region
that won't converge is **escalated via `dec`**, not spun on.

## ⑦ Control
The allowed decision after each verification: **continue · retry (different hypothesis) · repair (the
failing region) · escalate (`dec`/`risk`) · ship.** This *is* iladub's decidability layer.

## ⑧ Observability
Provenance-to-page, the `dec` decision log, the score, validated-vs-escalated — enough to reconstruct any
run and see *why* each fact is where it is.

## ⑨ Model & Prompt — *chosen last*
The small model, **residue only**, swappable — picked after the harness (verifier, actions, control, limits)
is solid. The loop must be correct with a mediocre model and merely *faster* with a better one.

---
**Rollout tier:** L1 report · L2 assisted · L3 unattended — advance only when the verifier is trusted.
