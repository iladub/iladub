# The engine enforces policy: meeting substrate:03 with a governed Fluree ledger (design, 2026-10-21)

**Serves:** prog:criterion:substrate:03. `prog:met false` was re-verified on 2026-10-21 at `4dc64be`
(`tests/arc-manifest.ttl:611-618`).

**Doc impact: increment.** The optional plug `iladub.substrate.fluree` gains identity-carrying reads
and writes, and `src/iladub/fluree/` gains a governance bundle and its closure check. Nothing already
released changes meaning, and the compile path still never imports the plug.

**Approved:** the design in `docs/superpowers/2026-10-21-substrate-03-design-approved-handoff.md` § 3,
which the maintainer approved in chat on 2026-10-21. That handoff ordered the Fluree findings
re-measured before this spec was written. **The written spec was approved by the maintainer on 2026-10-21 ("approved, write the plan"), with § 4.1's steward role as a parameter and § 7 as written.** They were, and § 2 records **five departures** from the
approved design that those measurements force. Each is marked **[changed]** where it lands in § 4.

## 1. Goal

Meet `substrate:03`: *"access policy is evaluated by the engine on every read and write, not held in
a template this repo only parses."* Close **R328** in the same loop: a writer who is not the steward
cannot retract the membrane's shapes, so the substrate:02 refusal cannot be switched off from outside.

Scope is the maintainer's choice from the handoff: read and write against a **claimed** identity.
The engine does not authenticate who is claiming. That is a register row (§ 7), not this loop.

Fluree stays a plug and never a dependency (maintainer ruling 2026-10-14). The default suite stays
Fluree-free.

## 2. Measured while writing this spec (2026-10-21, macOS aarch64, fluree 4.2.4)

A measurement subagent re-ran every probe from the handoff's § 4, then a second round on the
assembled bundle. **The scripts, console outputs and verbatim policy dumps are committed** in
`docs/superpowers/evidence/2026-10-21-substrate-03-probe/`. The per-request `*.log.json` files
(1.7 MB) were not committed. Each script regenerates its own log in under a minute on a
`--memory` server.

| Handoff claim | Measured | File |
|---|---|---|
| Q1: `fluree-identity` + `fluree-policy-class` headers carry identity on `/query`, `/insert`, `/update`; unsigned identity is honoured | **Holds.** Without the class header (and no `f:policyClass` on the identity node), U sees 0 rows and W's write is 403. JSON `opts.identity` works only without `from` (`from: "L:main"` → 400 "Ledger mismatch"). | `q1q3.out`, `q1json.out` |
| Q2: no identity bypasses; after `#config`, every bypass is 403 | **Holds for writes** (all 10 header combinations 403, t unchanged). **Differs for reads:** a denied read returns **200 with 0 rows**, never 403. The config graph IRI is `urn:fluree:{L}:main#config`. After config, a no-identity root read returns 0 rows. | `q2.out` |
| Q3: U=2, A=2, B=0 | **Template as-is: U=0, A=2, B=0.** U sees rows only after `U prov:actedOnBehalfOf U`. With a `union` in the view's `f:query`: U=2, A=2, B=0, W=2, S=3. | `q1q3.out`, `q1q3_fixed.py` |
| Q4: the companion allow is needed; traps 1 and 2 | Traps 1 and 2 reproduce. Without a companion, S's *guarded* retraction is admitted (200) while S's unguarded insert is 403. **New:** U's ground `DELETE DATA` of a row U cannot see is **admitted** (200, t 6→7). | `q4b_q6_q7.out`, `q4.out` |
| Q5: a `f:LedgerConfig` without `f:shaclDefaults` disables SHACL | **Holds**, even for a bare `a f:LedgerConfig` with no settings. `# PRAGMA validation-mode: warn` never relaxed a 400. | `q5.out` |
| Further: W self-promotes; W deletes `f:shaclEnabled` | Both hold unfixed. A required steward-only guard `onProperty etkl:hasRole` refuses the promotion (403), and guards on the 7 `f:` config predicates refuse the config deletes (403). | `q4b_q6_q7.out` |
| *(not in handoff)* | **The unconditional companion `{f:modify, f:allow true}` admits ANONYMOUS writes** on anything no guard names (200). | `anon_companion.out`, `q8.out` (q8e) |
| *(not in handoff)* | **A role-conditional companion** (its `f:query` is `?$identity etkl:hasRole ?r`, with no `f:allow`) refuses anonymous callers and role-less identities (403, with and without `fluree-default-allow`), admits W's untagged write (200), and keeps every guard above. | `q8.out` (q8two) |
| *(not in handoff)* | **Provisioning in ONE transaction works.** One SPARQL update holding the data, shapes, six policies and `GRAPH <…#config>` gave 200 at t=1, and every request from then on was governed. Two-step provisioning (data and shapes, then policies, then config) behaves identically. | `q8.out` (q8one, q8two), `q8_q8one_single_tx.rq` |
| *(not in handoff)* | **Under the bundle, nobody can read an untagged node.** That includes S reading the blank-node property shape, so its engine label can only be learned **before** the config lands. | `q8.out` (q8one) |
| *(not in handoff)* | The guard on `etkl:sensitivity` refuses W's write of a **tagged** doc (403). Only S can tag. | `q8.out` |

### The five departures

1. **Reads are asserted by row count, never by status.** Denial returns 200 and no rows.
2. **The companion is role-conditional**, not `f:allow true`. Otherwise anyone can write anonymously.
3. **The view template is fixed with a `union`**, so a human user is their own principal. The probe
   measured this form. Adding a self-`actedOnBehalfOf` triple to the data would also work, but it
   puts a modelling fiction into the data.
4. **`403` is a refusal value in the plug, beside `400`.** The substrate:02 invariant "every other
   status raises" is narrowed. A 403 with `err:policy/AccessDenied` is the engine's policy membrane
   speaking, measured on every guarded write. 404 and 5xx still raise, because a wrong route must
   still never read as the membrane working.
5. **Governance is committed as its own transaction, after the shapes** (§ 4.4). This is the
   only order in which the R328 oracle can learn the blank-node label it must try to retract. The
   single-transaction form also works, but it leaves the label unknowable.

## 3. Classification under the neurosymbolic gate (CLAUDE.md § 8)

- **The access decisions are AXIOM, and the engine evaluates them.** Every view and modify decision
  is a declarative `f:AccessPolicy` stored in the ledger. Its `f:query` is a set of JSON-LD
  where-patterns, which is the engine's own declarative query form. This repo decides nothing at
  read or write time.
- **The closure check splits in two, and the split is load-bearing.**
  - **PROCEDURAL: extraction.** `f:query` is an `xsd:string` that holds JSON, not RDF, so SPARQL
    cannot see inside it. `json.loads` plus collecting the predicate keys of each where-pattern is a
    decidable, exact extraction from the raw source into typed RDF facts. It is irreducible to
    AXIOM, because no SPARQL function parses JSON. It judges nothing: it emits one fact
    "policy P reads predicate X" per key, and nothing more.
  - **AXIOM: the constraint.** A SHACL shape with `sh:sparql`, closed-world and scoped to the bundle
    (the holon is the closure boundary), refuses every predicate in the closure set (§ 4.3) that no
    **required `f:modify` guard** names by `f:onProperty`. This is a constraint, not a derivation,
    so SHACL is the right form.
- **The plug is PROCEDURAL I/O** and decides nothing (unchanged from substrate:02).
- **Bundle loading substitutes one IRI** (§ 4.1, the steward role). That is templating, not a
  decision.
- No tuned constant appears anywhere.

## 4. Design

### 4.1 The governance bundle: `src/iladub/fluree/`

Declarative `f:` JSON-LD, authored by hand:

- **`f-policy-template.jsonld` [changed]**: the existing view policy, with its `f:query` rewritten
  so that `?principal` is either `?$identity`'s `prov:actedOnBehalfOf` or `?$identity` itself (a
  `union`). It keeps every IRI in `federate._F_QUERY_REFS` (`src/iladub/etkl/federate.py:29`), so
  `certify_f_faithful` still reads it as faithful. **Measure before editing:** what
  `tests/test_fluree_policy.py:48` asserts about the query's shape.
- **`f-governance.jsonld` (new)** holds the required steward-only `f:modify` guards:
  - one guard `f:onClass sh:NodeShape`;
  - one guard `f:onProperty` per predicate in the closure set (§ 4.3);
  - the role-conditional, non-required `f:modify` companion **[changed]**.

  Each guard's `f:query` is `{"where":[{"@id":"?$identity","…etkl#hasRole":{"@id":"<STEWARD>"}}]}`.
- **`f-config.jsonld` (new)**: one `f:LedgerConfig` node with `f:policyDefaults` (`defaultAllow
  false`, `policyClass f:AccessPolicy`, `overrideControl f:OverrideNone`) and **explicit**
  `f:shaclDefaults` (`shaclEnabled true`, `validationMode f:ValidationReject`, `overrideControl
  f:OverrideNone`). § 2, Q5 shows why the explicit block is mandatory. The plug inserts this into the
  named graph `urn:fluree:{ledger}:main#config` (measured, § 2, Q2).
- **The steward role is a parameter, `steward_role: str`.** It is not a vocabulary term. A role
  instance is deployment data, and minting `etkl:steward` would put an individual into the ontology.
  `iladub.fluree.load_bundle(steward_role) -> Graph` substitutes it into the guard queries.
  *Reviewer's choice:* if the maintainer prefers a vocabulary term, it goes into `etkl.ttl` with an
  example and a negative test (CLAUDE.md § Serialization).

### 4.2 The plug: `src/iladub/substrate/fluree.py`

Every method that touches a ledger takes an optional `identity: str | None = None`. When it is
given, the request carries `fluree-identity: <identity>` and `fluree-policy-class:
https://ns.flur.ee/db#AccessPolicy`. The plug uses only the header form, never JSON `opts`, because
of the `from` mismatch in § 2, Q1.

- **`commit(ledger, data, identity=None)`**: unchanged route.
- **`query(ledger, sparql, identity=None) -> list[dict]`** (new): `POST /v1/fluree/query/{ledger}`
  with `application/sparql-query`. It returns the bindings and raises on non-2xx. A denied read is
  an empty list, as measured.
- **`retract(ledger, data, identity=None) -> CommitResult`** (new): it sends a **ground** delete and
  never `DELETE … WHERE` (trap 2: a `WHERE` the caller cannot see returns 200 with t unchanged).
  Blank nodes cannot appear in SPARQL `DELETE DATA`, so the probe deleted the blank-node triple with
  a JSON-LD `{"delete": {"@id": "_:fdb-…", …}}` body.
  - **SEAM, measure before writing:** how rdflib serialises a `BNode("fdb-…")` into JSON-LD.
    `retract` must send the engine's own label back unchanged, so do not assume rdflib preserves it.
    If it does not, `retract` builds the JSON-LD body directly. That is serialisation, not a
    decision.
- **`govern(ledger, bundle, config, identity=None)`** (new): commits the policies into the default
  graph and the config into `…#config`, in **one** transaction. It is the last root act on a
  ledger (§ 4.4). The transaction must be accepted, or `govern` raises. This is the producer-side
  guard, by the same argument as `provision`.
- **Status mapping [changed]:** 2xx is accepted, and **400 or 403** is a refusal (`accepted=False`,
  with `status` telling them apart). Anything else raises.

### 4.3 The closure check (default suite, no Fluree)

`iladub.fluree.closure_violations(bundle: Graph, shapes: Graph) -> list` (`[]` means closed).

**The closure set** is everything the membrane reads, minus `rdf:type`:
1. every predicate a policy's `f:query` reads (extracted, § 3);
2. every predicate used in the shapes graph;
3. every predicate on the `f:LedgerConfig` node and its blank-node values.

`rdf:type` is excluded **by construction**, because guarding it steward-only refuses every write;
doc-a alone carries 31 typed triples. Type retraction on shapes is covered by `onClass
sh:NodeShape` instead. **SEAM, measure before relying on it:** whether W's `DELETE DATA { ex:DocShape a
sh:NodeShape }` is refused by the `onClass` guard. The probe never tried it. If it is admitted, the
remedy goes into this section of the spec and not into the plan.

The rule closes recursively without a special case. The guards read `etkl:hasRole`, so
`etkl:hasRole` is in the set, so it must be guarded. That is the self-promotion hole of § 2, caught
statically.

The extracted facts use one predicate that is internal to the check (`urn:iladub:fluree-closure#reads`)
and is not vocabulary. It never leaves the check's in-memory graph.

### 4.4 Provisioning order and the pre-config window

`provision(L, shapes)` (root, unchanged) → *the caller may read as root here* → `govern(L, bundle,
config)` (root, last). The role and tag facts (`etkl:hasRole`, `etkl:grantsTag`, `etkl:sensitivity`, `prov:actedOnBehalfOf`) are root writes in the same window, before `govern`, because afterwards only the steward may write them. Root can act between create and `govern`. That window is a register row (§ 7).
Shrinking it to the single transaction would cost the R328 oracle its blank-node label.

### 4.5 The oracles: `tests/substrate/test_in_engine_policy.py`, marker `substrate`

The fixture data is: tagged rows d1 (public), d2 (clinical) and d3 (secret); U and W hold a
clinician role (public and clinical); S holds the steward role; A acts on behalf of U; B is an agent
with no principal. Doc-a's interior is reused unchanged from `tests/substrate/doc_a.py`.

**`test_engine_enforces_ai_inherits_user`** (the manifest's named oracle, verbatim):
- `count(U) == count(A) > 0`, `count(B) == 0`, and `count(S) > count(U)`.
- The last assertion is the control: it shows the view discriminates, not merely that it hides.

**`test_engine_refuses_unauthorised_shape_retraction`** (closes R328). Provision `iladub-shapes.ttl`,
read one property shape's blank-node label as root, `govern`, then take `t0`. Then:
- W retracts a `sh:targetClass` triple: 403, t0.
- W retracts that blank node's `sh:minCount`: 403, t0.
- W commits `ungoverned(compiled_interior())`: 400, the `INVARIANT` text (`vocab/shapes/iladub-shapes.ttl:40`), t0.
- W commits `compiled_interior()`: accepted, t0+1. This is the control: W can write at all.
- S retracts the same `sh:targetClass`: accepted. This is the control: the guard is not refusing
  everyone.

**`test_engine_refuses_self_promotion`**: W inserts `W etkl:hasRole <steward>` and gets 403 with t
unchanged. Then W's targetClass retraction is still 403.

**`test_engine_refuses_anonymous_and_roleless_writes`**: a commit of `compiled_interior()` with no
identity, and one as B, each get 403 with t unchanged.

### 4.6 Default-suite tests (required `test` job)

- **The closure check:**
  - The shipped bundle plus `iladub-shapes.ttl` returns `[]`.
  - Drop the `etkl:hasRole` guard and the result names `etkl:hasRole`.
  - Drop the `sh:minCount` guard and the result names `sh:minCount`.
  - Add a policy that reads a new predicate and the result names that predicate.
- **The plug's stub server:** extend the existing status-mapping stub with 403, which must be a
  refusal. The identity and class headers must be present when `identity=` is given and absent when
  it is not.
- **`load_bundle`:** the steward IRI appears in every guard query, and no placeholder remains.

## 5. Falsification (the implementer runs and records it, per plan rule 4)

Each arm provisions through the plug and **bypasses `closure_violations`**. A weakened bundle is
exactly what the check exists to refuse, so the test has to go around it.

| Arm | The test that must fail |
|---|---|
| Replace the view `f:query` with an allow-all view | `ai_inherits_user` (B sees rows) |
| Restore the as-is view template (no `union`) | `ai_inherits_user` (U=0, which is not equal to A=2) |
| Drop the `onProperty sh:minCount` guard | `shape_retraction` (W's minCount retraction is admitted) |
| Drop the `onProperty etkl:hasRole` guard | `self_promotion` |
| Use the unconditional companion | `anonymous_and_roleless` |
| Omit `f:shaclDefaults` from the config | `shape_retraction` (the ungoverned commit is admitted) |
| Map 403 to accepted in the plug | `shape_retraction` |

## 6. CI, the arc, the register and the baseline

- **CI:** no workflow edit is expected. The non-required `substrate` job runs `pytest -m substrate`
  and picks the new file up. **Unmeasured:** policy behaviour on Linux. If the first run differs,
  the CI section changes and the oracles do not.
- **The arc:** set `substrate:03 prog:met true` by hand once the `substrate` job is green on the
  implementation PR, with a dated comment naming the run. The PR says plainly that the proving job is
  not required.
- **R328:** strike it, with the closure evidence written in place.
- **Corpus baseline:** the new and changed files under `src/` are compile inputs. After the last
  input edit and `git add`, run `corpus_baseline.py regenerate`. The expected snapshot diff is
  **empty**. A non-empty diff is a finding.

## 7. What is NOT done (each becomes a register row in the implementation PR)

- **Authentication.** The engine enforces policy against an identity it does not verify. Claiming to
  be S by header retracts a shape (§ 2, Q1). JWS and bearer auth are unmeasured.
- **The pre-config window.** Root can act between ledger creation and `govern` (§ 4.4).
- **The view does not bound retraction.** U deleted a row U cannot see (§ 2, Q4, new). Data-level
  write authorisation beyond the governance plane is not in this loop.
- **Agents cannot write.** The companion requires the identity itself to hold a role, and A holds
  none (it inherits through `prov:actedOnBehalfOf`). Write delegation to agents is unspecified.
- **Only the steward can tag.** Tagging decides who may read, so this loop treats it as governance.
  A tagging workflow for ordinary writers is a design question.
- **`hpol:`/ODRL → `f:` compilation for the guards.** The guards are hand-authored, and only the view
  grants are compiled today (`federate.compile_f_policy`).
- **`iladub:accountableWritePolicy`** (`f-modify-policy-template.jsonld`) is not in the bundle.
- **No root inspection after `govern`.** A no-identity read returns 0 rows. Recovery runs through
  the steward identity only.
- **Carried, not re-raised:** R329 (membrane parity), and RDFS reach of `f:onClass` (substrate:02
  § 7).

## 8. Unverified at the time of writing

- All of § 2 is macOS aarch64, measured by a subagent. The controller read its outputs
  (`q8.out` in full) but did not re-run the scripts.
- The two seams in § 4.2 and § 4.3 (rdflib's blank-node labels, and `rdf:type` retraction of a
  NodeShape) are unmeasured.
- The `union` view was measured on the probe's `ex:` fixture, not on the shipped template file.
- **The composite is unmeasured:** iladub-shapes' `INVARIANT` 400 for W *under the full bundle*. substrate:02 measured the 400 without policy, and q8 measured W's 400 under policy on the probe's `ex:Doc` shape only.
- `count(S) > count(U)` assumes the fixture tags d3 with a tag only the steward role grants. That
  is true of the probe fixture, and the test's fixture must reproduce it.
