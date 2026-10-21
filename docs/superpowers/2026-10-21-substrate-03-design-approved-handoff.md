# Handoff: substrate:03 — design approved, spec not yet written (2026-10-21)

**Serves:** prog:criterion:substrate:03 — verify it is still `prog:met false` before starting.

**Topic:** substrate · **Date:** 2026-10-21

**Doc impact: none.** A handoff only.

Part 5 was written first. The session handed off at roughly 50K working tokens (~1.0× the 50K
originating floor), immediately after the maintainer approved the design ("approved") and before the
spec was written.

## 5. The next concrete action, typed

1. **ASSERTED: write the spec** at `docs/superpowers/specs/2026-10-21-substrate-03-in-engine-policy-design.md`
   from § 3 below, in the first third of a fresh session. The maintainer approved the design in chat,
   and that approval covers *writing the spec*. Then run spec self-review, ask the maintainer to review
   the written spec, and only after that use superpowers:writing-plans.
2. **PROPOSED: every Fluree behaviour in § 4 holds as the probe reported it.** The probe was a
   subagent's throwaway run (macOS aarch64, `fluree 4.2.4`, `server run --memory`), and its scripts
   live in a session scratchpad that will not survive
   (`/private/tmp/claude-501/…/scratchpad/fluree-policy-probe/`: `h.py`, `q3*.py`, `q4.py`). No number
   in § 4 was re-run by the controller. **Re-measure the ones the spec leans on before writing it**:
   the header mechanism (§ 4 Q1), the no-identity root bypass and its `#config` fix (Q2), and the
   `f:LedgerConfig`-disables-SHACL trap (Q5). If one fails, the bundle in § 3.1 changes, not the
   oracles. You find out in minutes, because a `--memory` server starts in under a second.
3. **PROPOSED: the guard closure in § 3.2 can be computed by SPARQL over the bundle.** `f:query` is a
   JSON *string* holding JSON-LD where-patterns, not RDF, so "the predicates a policy reads" may need a
   PROCEDURAL parse of that string (a decidable extraction, justifiable under CLAUDE.md § 8) before the
   AXIOM check can run. Decide this in the spec. You find out the moment you read one parsed template.

## 1. Goal

Meet `prog:criterion:substrate:03` (`tests/arc-manifest.ttl:611-618`): access policy is evaluated
**by the engine** on every read and write, not held in a template this repo only parses. In the same
loop, close **R328** (`docs/superpowers/residues-open.md:234`: the membrane does not protect itself).
Fluree stays a plug, never a dependency (maintainer ruling 2026-10-14).

## 2. Where the primaries are

- The plug: `src/iladub/substrate/fluree.py` (`FlureeEndpoint`: `provision`, `commit`, `head_t`;
  status mapping 2xx/400/raise).
- The harness: `tests/substrate/server.py` (pinned `fluree 4.2.4`, fail-never-skip),
  `tests/substrate/conftest.py`, `tests/substrate/doc_a.py`.
- The substrate:02 oracle: `tests/substrate/test_write_gate.py`.
- The templates the engine never sees today: `src/iladub/fluree/f-policy-template.jsonld` (required
  `f:view` via `prov:actedOnBehalfOf → etkl:hasRole → etkl:grantsTag → etkl:sensitivity`) and
  `f-modify-policy-template.jsonld`. Parsed only, by `src/iladub/etkl/federate.py:26`.
- The ODRL → `f:` compiler: `federate.compile_f_policy`, `federate.certify_f_faithful`.
- The invariant's shape: `gsh:AiInheritsUserShape`, `vocab/shapes/governance-shapes.ttl:27`.
- The substrate:02 handoff and spec: `docs/superpowers/2026-10-20-substrate-02-design-approved-handoff.md`,
  `docs/superpowers/specs/2026-10-20-substrate-02-*`.

## 3. What was decided, and where it is recorded

Decided in chat on 2026-10-21. This section is the only record.

- **Subject:** substrate:03 rather than substrate:01. It closes R328, and it is the motor half the
  governance story depends on.
- **Scope (maintainer's choice):** read, plus a closed write, against a **claimed** identity.
  Authentication is a named register row. It is not in scope.

### 3.1 Components (plug side; the default suite stays Fluree-free)
- **The governance bundle, declarative `f:` JSON-LD under `src/iladub/fluree/`:**
  - a `#config` graph with `f:policyDefaults` (`defaultAllow false`, `policyClass f:AccessPolicy`,
    `overrideControl f:OverrideNone`);
  - **explicit** `f:shaclDefaults` (`shaclEnabled true`, `validationMode f:ValidationReject`,
    `OverrideNone`);
  - steward-only required `f:modify` guards on the shapes (`onClass sh:NodeShape` **and**
    `onProperty sh:*`), on the `f:` config predicates, on `f:AccessPolicy` nodes, and on the role
    predicate the guards read;
  - a non-required companion `f:modify` allow, so ordinary writers can still commit;
  - the view template, with its chain fixed so a human user is their own principal.
- **`FlureeEndpoint`** gains an optional `identity=` on `commit` and on a new `query`, sent as the
  `fluree-identity` header, plus `retract(ledger, graph, identity)` sent as `DELETE DATA`. It never
  uses `DELETE…WHERE`, because under view policy a `WHERE` the caller cannot see returns `200` with `t`
  unchanged (§ 4 Q4, trap 2). The plug stays PROCEDURAL I/O and decides nothing.

### 3.2 The closure check (AXIOM, default suite, no Fluree)
Every predicate read by any policy's `f:query` must be covered by a required `f:modify` guard. The
check refuses the bundle otherwise. It is the check that would have caught the self-promotion hole
(§ 4, further bypasses). See part 5 item 3 for how `f:query` gets parsed.

### 3.3 Oracles (`pytest -m substrate`, non-required `substrate` CI job)
- **`test_engine_enforces_ai_inherits_user`** (the manifest's named oracle): U and A(U) see the same
  row count, which is above zero, and B, an agent with no principal, sees 0. *Falsification:* provision
  without the view policy, and B sees every row.
- **`test_engine_refuses_unauthorised_shape_retraction`** (closes R328): W's `DELETE DATA` of a
  `sh:targetClass` triple and of a blank-node `sh:minCount` triple each get `403` with `t` unchanged,
  and the ungoverned doc-a commit after them is still refused with `400`. The steward's retraction is
  admitted. *Falsification:* drop the `onProperty` guard, and W's `sh:minCount` retraction is admitted.
- **The substrate:02 oracle re-runs on the governed ledger**, so the config cannot have switched
  SHACL off (§ 4 Q5).

### 3.4 Arc, register, baseline
- Flip `substrate:03 prog:met true` by hand once the job is green on the PR. Strike R328 with its
  closure evidence in place.
- Raise these as register rows:
  - authentication (JWS or bearer; the engine enforces policy against an identity it does not verify);
  - the pre-config window (root can act until the `#config` commit lands, so provisioning order is
    load-bearing);
  - parity of the full membrane between Fluree and pySHACL (carried from #361);
  - `hpol:`/ODRL → `f:` compilation for the guards.
- New `src/` files are compile inputs. Regenerate the corpus baseline after the last input edit, and
  expect an empty snapshot diff.

## 4. Unverified or assumed: the probe's findings (a subagent's report, not re-run)

All on `fluree 4.2.4`, `server run --memory`. Every write was SPARQL `POST /v1/fluree/update/{L}` or
`/insert`, with `GET /info` for head `t`.

- **Q1, how identity is carried.** The `fluree-identity: <full IRI>` header, plus
  `fluree-policy-class: https://ns.flur.ee/db#AccessPolicy` (or `f:policyClass` on the identity node),
  works on `/query`, `/insert` and `/update`. JSON `opts.identity`/`opts.policyClass` works too.
  **Unsigned identities are honoured** in unauthenticated mode (the embedded doc
  `security/authentication.md` says so), so an identity can be spoofed: claiming to be the steward
  retracted a shape (`200`, t 3→4).
- **Q2, the root bypass.** With no identity, a query returned every row despite a required view
  policy, and a write was accepted (shape retracted, ungoverned insert admitted). `fluree-default-allow:
  true` and an inline `fluree-policy` allow-all also bypassed. **Fix:** a `#config` TriG insert of
  `f:policyDefaults [f:defaultAllow false; f:policyClass f:AccessPolicy; f:overrideControl
  f:OverrideNone]`. After it, all six bypass header combinations got `403`.
- **Q3, AI inherits the user.** With the class supplied: U=2, A=2, B=0. The policy was stored in the
  ledger exactly as the template. The template defect: U needs `prov:actedOnBehalfOf U` to see anything.
- **Q4, the steward-only modify guard.** Deny-by-default blocks every write until a non-required
  `{f:action f:modify, f:allow true}` companion is added. W's retraction of `sh:targetClass` got `403`,
  and so did W's retraction of `sh:minCount`. The steward got `200`, after which an ungoverned insert by
  W was accepted. **Trap 1:** with `onClass NodeShape` alone, W retracted the blank node's `sh:minCount`
  and the gate fell. **Trap 2:** `DELETE…WHERE` under a view policy that hides the rows returns `200`
  with t unchanged.
- **Q5, SHACL with policy.** An identity-carrying writer still got `400 … INVARIANT`. **Any
  `f:LedgerConfig` without `f:shaclDefaults` silently disabled SHACL**, which contradicts Fluree's docs.
  Explicit `f:shaclDefaults` restored the `400`.
- **Further bypasses.** W deleted `f:shaclEnabled` from the config (`200`), which a guard on the config
  predicates fixed. W ran `INSERT DATA { W ex:role "steward" }` and got `200`, promoting itself; the
  probe left that unfixed, and it is the reason for the closure check in § 3.2.
- **Unmeasured:** signed JWS or bearer auth; Linux on CI (the substrate:02 job already runs 4.2.4 on
  Linux, but policy has not been exercised there); RDFS subclass reach of `f:onClass`.
