# Fluree `f:` enforcement compile — the governed policy, enforced at the data layer

- **Date:** 2026-07-25
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). A single vertical slice ("loop F-fluree").
- **Context:** The governed/ViewerPass increment (`docs/superpowers/specs/2026-07-25-governed-viewerpass-projection-design.md`, shipped PR #64) proved a viewer-relative projection *certified by an oracle*. This increment moves the same governance to *enforcement at the data layer*: compile the ODRL sensitivity-tag policy into a data-driven **Fluree `f:AccessPolicy`**, and certify the `f:` grants equal the ODRL grants — closing **governed-projection-permitted == odrl-grants == f:-permitted** from one policy. Realizes the High Seas thesis (deterministic access *in* the data, AI-inherits-user via `?$identity`). **Declarative and CI-runnable — no Fluree server**; live enforcement is a separate local/internal harness.

---

## 1. Purpose and scope

Compile iladub's governed tag-policy into a Fluree `f:` policy and prove the translation is faithful. The governed projection (PR #64) and this `f:` policy become **two faithful renderings of the same ODRL tag-policy** — one enforcing at the app/oracle layer, the other at the Fluree data layer. An AI agent authenticating under a user's identity (`?$identity`) receives exactly the user's data access — AI-inherits-user, now deterministic and *in the data*.

**In scope:**
- A static, data-driven `f:AccessPolicy` template (Fluree-native JSON-LD).
- `vocab/queries/compile-f-grants.rq` — an AXIOM CONSTRUCT reshaping ODRL read-permissions into flat `etkl:grantsTag` grant triples the policy's `f:query` reads.
- `federate.compile_f_policy(odrl_policy) -> Graph` (assemble template + grants) and `federate.certify_f_faithful(odrl_policy, f_policy, roles) -> FlureeVerdict`.
- Thin owned vocab `etkl:grantsTag`.
- A domain-neutral demonstrator reusing the transplant tag-policy.

**Non-goals (deferred, spec §8):**
- A **live Fluree enforcement harness** (running server; load data + policy; query as an identity; assert only permitted rows) — kept local/internal like the existing gitignored ReBAC benchmark. This increment does not run Fluree.
- Multi-dimensional ABAC (`region/desk/deal` tags) — one categorical tag dimension, as in PR #64.
- `f:modify` / write policies — this is a read (`f:view`) access policy only.
- Authoring the Fluree `f:` ontology — `f:` is consumed as a compile *target*, never authored.

**Success criteria:**
1. `compile_f_policy` over the transplant tag-policy produces an `f:` policy whose `etkl:grantsTag` grants equal the ODRL grants for every role — `certify_f_faithful(...).ok` is True.
2. A dropped grant → `missing` non-empty; an injected extra grant → `extra` non-empty; both make `ok` False.
3. AI-inherits-user is preserved: the template's `f:query` binds `?$identity` and resolves the role via the SAME `(prov:actedOnBehalfOf)?/etkl:hasRole` path the projection uses; a template missing the `actedOnBehalfOf` leg → `identity_ok` False.
4. No Fluree server is required to run any test. `f:` never appears as an authored iladub-ontology subject; `hfed:` unused.

---

## 2. Architecture and data flow

```
governed ODRL tag-policy  (odrl:permission[ read ; assignee ?role ; target ?tag ])   ── ONE source of truth
        │                                                       │
        │ compile-f-grants.rq (AXIOM CONSTRUCT)                 │ federate-projection-governed.rq (PR #64)
        ▼                                                       ▼
  ?role etkl:grantsTag ?tag   +   f-policy-template.jsonld      governed projection (app/oracle layer)
        │        (static, data-driven f:AccessPolicy)           │
        └───────────────► f: policy graph ◄────────────────────┘
                               │ certify_f_faithful
                               ▼
   ∀ role:  { etkl:grantsTag } == { odrl read-targets }   (grant-set equivalence)
   ∧ identity_ok: template f:query binds ?$identity, resolves role via
                  (prov:actedOnBehalfOf)?/etkl:hasRole  (AI-inherits-user at the data layer)
```

The chain closes: the governed projection admits exactly `odrl-grants` (PR #64's oracle), and the `f:` policy enforces exactly `odrl-grants` (this oracle) — so **projection-permitted ⟺ f:-permitted**, both derived from the single ODRL policy.

---

## 3. Components

### 3.1 The static `f:AccessPolicy` template — `src/iladub/fluree/f-policy-template.jsonld`
A Fluree-native, **data-driven** policy (identical for any tag-policy — the grants travel as data, not baked in):
- `@type` includes `f:AccessPolicy`; `f:action` = `f:view`; `f:required` true; deny-overrides posture.
- `f:query` whose `where` binds `?$identity`, then: `?$identity (prov:actedOnBehalfOf)?/etkl:hasRole ?role`, `?role etkl:grantsTag ?tag`, `?$this etkl:sensitivity ?tag`. So an identity may `f:view` a resource iff the resource's sensitivity tag is one the identity's role grants — and an AI agent under a user's identity resolves through `actedOnBehalfOf` to the user's role.

Kept under `src/iladub/fluree/` (a Fluree interchange target, outside the `vocab/`/`examples/` authored-ontology trees). Authored so its role-resolution and joins are **inspectable** — the `f:query` `where` references `?$identity`, the `actedOnBehalfOf`/`etkl:hasRole` role resolution, and the `etkl:grantsTag`/`etkl:sensitivity` joins in a form the oracle can find (whether modeled as JSON-LD objects or as a `where` string). Loadable via rdflib for that check.

### 3.2 The grant compile — `vocab/queries/compile-f-grants.rq` (AXIOM)
A fixed SPARQL CONSTRUCT, open-world, evidence-positive:
- WHERE: `?perm odrl:action odrl:read ; odrl:assignee ?role ; odrl:target ?tag .`
- CONSTRUCT: `?role etkl:grantsTag ?tag .`

Mirrors the governed CONSTRUCT's grant pattern exactly (same read/assignee/target semantics), so the flattened grants are the same set the projection gates on.

### 3.3 `federate.py` additions (PROCEDURAL glue, justified)
- `compile_f_policy(odrl_policy: Graph) -> Graph` — run `compile-f-grants.rq` over `odrl_policy` → grant triples; load `f-policy-template.jsonld`; return their union (the full `f:` policy graph). No decision, no tuned constant.
- `certify_f_faithful(odrl_policy: Graph, f_policy: Graph, roles) -> FlureeVerdict` where `FlureeVerdict(ok, missing, extra, identity_ok)` (frozen):
  - `odrl_grants(role) = { tag : odrl:permission[read, assignee role, target tag] }` (reuse the governed oracle's grant logic).
  - `f_grants(role) = { tag : role etkl:grantsTag tag in f_policy }` — read only over **real-IRI** grant triples (the CONSTRUCT-derived grants use concrete role/tag IRIs; the template's `f:query` references `etkl:grantsTag` with query *variables*, not real role/tag IRIs, so it contributes no spurious grant).
  - `missing = ⋃_role (odrl_grants(role) − f_grants(role))`; `extra = ⋃_role (f_grants(role) − odrl_grants(role))`.
  - `identity_ok` = the template's `f:query` binds `?$identity` and contains the `actedOnBehalfOf`/`hasRole` role-resolution and the `etkl:grantsTag` + `etkl:sensitivity` joins (structural presence check over the loaded template).
  - `ok = not (missing or extra) and identity_ok`.

### 3.4 Vocab (standalone, in `etkl.ttl`)
- `etkl:grantsTag` — `owl:ObjectProperty`, a role's granted sensitivity tag (the flat grant relation the `f:query` joins). No HGA/`f:` refs.

---

## 4. Source-ownership & alignment discipline

- `etkl:grantsTag` authored only in `etkl:`; `etkl.ttl` stays standalone.
- **`f:` is Fluree's vocabulary — neither HGA nor iladub-owned.** It appears ONLY in the generated interchange artifact (`src/iladub/fluree/f-policy-template.jsonld`), as a compile *target* (like JSON-LD interchange), never as an authored iladub ontology, and outside the `vocab/`/`examples/` trees the source-ownership CI scans. The HGA source-ownership rule (holon-terms-as-subjects) is unaffected.
- Access rides `odrl:` (aligned to `hpol:`) and `prov:` (aligned to `hview:`); `f:` is the enforcement rendering. `hfed:` (reserved) unused.

---

## 5. Neurosymbolic gate compliance (Global Constraint)

- **Grant derivation → AXIOM.** `compile-f-grants.rq` is a fixed SPARQL CONSTRUCT, open-world, evidence-positive. No tuned constant.
- **Compile assembly + oracle → PROCEDURAL, justified.** `compile_f_policy` is graph union + query delegation; `certify_f_faithful` is set comparison plus a structural presence check over the template — same class as `interpret.run` / the reshape oracle. No domain decision, no tuned tolerance. The authoritative "who may read what" decision lives entirely in the ODRL policy + the `f:query`; the Python is a translation-faithfulness check.
- The static template is a reviewed-once artifact, not generated per-decision.

---

## 6. Demonstrator and testing

- **Demonstrator (domain-neutral):** reuse the transplant tag-policy (roles `role-opo`/`role-recipient-ctr`/`role-donor-region`/`role-board`; tags `clinical`/`phi`). `compile_f_policy` → an `f:` policy whose `etkl:grantsTag` grants restate the ODRL grants; `certify_f_faithful` → `ok`. Show that an AI-assistant identity (`prov:actedOnBehalfOf` a recipient clinician) resolves through the `f:query` to the recipient's grants — the governed-bot claim at the data layer.
- **Tests (`tests/test_fluree_policy.py`):**
  - `compile_f_policy` over the demo policy → `certify_f_faithful(...).ok` True; the grant triples match the ODRL grants per role.
  - **Negative — dropped grant:** remove one `etkl:grantsTag` from the compiled policy → `missing` non-empty, `ok` False.
  - **Negative — extra grant:** inject a `role etkl:grantsTag` the ODRL policy doesn't grant → `extra` non-empty, `ok` False.
  - **Negative — AI-inherits-user broken:** a template variant whose `f:query` resolves the role WITHOUT the `actedOnBehalfOf` leg → `identity_ok` False.
  - A structural test that the shipped template binds `?$identity` and contains the three joins.

---

## 7. Relation to prior work and steering

- Extends the **governed/ViewerPass** increment (PR #64): the same ODRL tag-policy now also compiles to Fluree enforcement; `certify_f_faithful` closes the projection⟺enforcement chain.
- Realizes **topic 1 (consume-don't-clone) + topic 3 (federation) convergence**: the projection is enforced at the Fluree data layer, per the Fluree-substrate decision (`internal/decisions/2026-07-02-fluree-as-hga-substrate.md` §7 names the ODRL→`f:` compile as the exact adapter) — consuming Fluree's `f:` model, not cloning it.
- Realizes the **High Seas / governed-bot** thesis (`[[high-seas-bridge]]`, `[[governed-bot-poc]]`): deterministic access in-data, AI-inherits-user via `?$identity`; the single tag dimension is the seed of ABAC `f(region,role,desk,deal)`.

---

## 8. Open questions / later increments

1. **Live-Fluree enforcement harness** (local/internal): stand up Fluree, load a governed dataset + the compiled policy, query as an identity, assert only permitted rows — the empirical enforcement proof. Kept out of the public repo/CI (external dependency, work-boundary).
2. Multi-dimensional ABAC — `region/desk/deal` tags + policy over their conjunction (High Seas ReBAC shape).
3. `f:modify` / write policies — governing transaction-time writes (the promotion-decision commit gate).
4. Per-producer projection scheme IRIs (shared with the compile→federate deferred list).
