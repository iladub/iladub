# iladub — scope evolution: from `etkl` to active holon graphs

Orientation for anyone (human or AI) trying to understand *what iladub became and why*.
It traces the through-line from a document-transform tool to a substrate for **interacting,
governed holons**, and names the precise shifts so the growth reads as expansion, not drift.

---

## The invariant core (what never changed)

Everything below is scaffolding around one signature that has held since day one:

> **Assert only what you can ground; propose everything else; never let a proposition pass
> as an assertion — and every grounded node is the product of an accountable promotion decision.**

That epistemic invariant *is* the thin `iladub:` core (`CandidateConcept`, `GroundedNode`,
`PromotionDecision`). `etkl`, `dec`, holons, and the storage substrate are all in service of it.

---

## The arc

### 1. `etkl` — the document compiler

**Extract, Transform-with-(K)nowledge, Load.** Traditional ETL maps fields *structurally*;
`etkl` grounds *meaning* against a **contract-as-ontology**, with a knowledge module passed as
an *argument* to the transform. Knowledge — not mappings — is the shape-change engine. Any
**human-addressed document, in any format** → a grounded artifact conformed to a destination
contract. (There is no "unstructured" input — only [structure addressed to a human](../manifesto.md).)

### 2. Decidability — the context graph

`dec` added the decisions that *change state* — both decisions found in document **content**
and the compiler's own **promotion** decisions — as accountable, traceable holons
(`dec:DecisionHolon`, escalation, events, timeline), with **contextual risk** as a
decidability measure. At this stage the graph *annotated* data with decision + provenance +
risk: the **context around** assertions.

### 3. The holon reframe — from record to active holon

The pivot: what `etkl` produces and `dec` governs are not annotated records but
**interacting holons**. A holon = data **+** its context **+** its boundary **+** its
projection, as one whole-that-is-also-a-part; the real system is **many holons interacting**
through governed **membranes/portals**. The context graph did not disappear — it became the
*context layer* of each holon. What is genuinely new is **interaction** (membrane crossings,
escalation) and **lifecycle** (events, state changes). iladub adopts Cagle's **HGA**
(`holon:`) as the substrate vocabulary — **consumed and aligned (`rdfs:subClassOf`/`seeAlso`),
never cloned** — and contributes the two gaps HGA leaves open: accountable **decidability** and
**contextual risk** (both designed to be portable/upstreamable, not a fork).

### 4. The active substrate

A holon is only *active* if something **enforces its membrane at runtime**. That requires an
immutable **event ledger** (memory), **validation-at-write** (sensory), and **in-engine policy**
(motor). The chosen substrate provides all three natively, so a *described* membrane becomes an
*enforced* one. This is not a deployment detail — it is what turns a modeled holon into a living one.

---

## What actually changed (three precise shifts)

1. **The output changed category.** From a **record** (a noun — a well-shaped dataset) to an
   **active, governed holon** (a thing with a boundary, a history, and a governed interface).
2. **The membrane is *both* a semantic boundary and an access boundary.** The same interface
   that grounds meaning also gates *who/what may cross* — compartmentalization, escalation to an
   apex, and "risk visible only where it impacts." Governance is co-equal with grounding, not an
   afterthought.
3. **Autonomy became *governed* autonomy.** An active holon adapts *within its membrane*: every
   state change at the interface is an accountable decision, and any acting agent inherits exactly
   the interacting user's access. The leash is the value — this is the opposite of ungoverned agents.

---

## Precision notes (conflations to avoid)

- **Not "deterministic ETL" — deterministic-*first* with governed propositions.** Deterministic
  where content is groundable; where it isn't, an LLM *proposes* (never silently asserts), and a
  proposition enters the graph only via a `PromotionDecision`. The *output* is auditable even
  though an LLM is in the loop.
- **"Projection" has two senses — keep them apart.** (a) the `etkl` *transform* (source meaning →
  contract-shaped holon); (b) HGA's `hproj:` *projection* (a holon → viewer-relative rendering).
  Both are meaning-preserving shape changes, but they are different operations.
- **Consume, don't clone.** HGA terms are aligned to, never authored. `dec`/`risk` complement
  HGA's gaps and are built to be contributed upstream.

---

## The capability ladder — worked *semaphores*

The differentiators are demonstrated through **domain-neutral, publishable worked examples**.
Each example is a **semaphore**: a small, self-contained proxy that *signals* the mechanics a
larger, real-world governance domain requires, without carrying that domain's data. Semaphores
are **replaceable and composable** — different examples can foreground different facets
(compartmentalization, escalation, risk-scoped projection, decision-traced state change,
access-inheritance), and better ones may be introduced per facet.

- **Contract-conformance case (the compiler).** A human-addressed document compiled to a grounded,
  contract-conformed holon (e.g. clinical text → a standards-conformed clinical resource). Proves
  `etkl`: grounding + conformance. Still largely a *static* holon — a well-shaped record.
- **The transplant case (the active, governed holon).** A case holon whose state changes
  (proposed → activated → terminated) are **decisions**, with **contextual risk**,
  **compartmentalized access**, **escalation to an apex**, and **access-inheritance for agents**.
  This is where a holon becomes *active and governed*, not merely grounded.

"**Semaphore**" is apt in both senses: it *signals* the mechanics of a real target domain
(domain-neutral proof-of-mechanism), and — in the computer-science sense — a case that **governs
access to a scarce shared resource through gated state transitions** is itself an access-control
primitive. A single semaphore need not represent every facet; a family of them can.

---

## One-paragraph restatement

> iladub began as **`etkl`** — a knowledge-driven document compiler that treats every source as a
> fully-structured, human-addressed document and grounds it against a contract-as-ontology
> (knowledge, not mappings, as the shape-change engine), under one invariant: assert only what you
> can ground, propose the rest, and never let a
> proposition pass as an assertion. It then absorbed **decidability** (`dec`): the decisions that
> change state — in document *content* and in the compiler's own promotions — became accountable,
> traceable holons. The pivot was recognizing that what `etkl` produces and governs are
> **interacting holons**: the output stopped being a static record and became an **active, governed
> holon** whose semantic boundary is *also* its access boundary. iladub consumes Cagle's HGA as the
> holon substrate (aligned, never cloned) and adds the two gaps HGA lacks — accountable decidability
> and contextual risk — running on a substrate whose immutable ledger, validation-at-write, and
> in-engine policy make a *described* membrane an *enforced* one. Domain-neutral **semaphores** —
> a contract-conformance case, then the transplant case — demonstrate the ladder from *compiler* to
> *active, governed holon*, each a replaceable proxy for the mechanics a real governance domain needs.
