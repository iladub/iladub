# CLAUDE.md — iladub project conventions & durable decisions

This file orients any contributor (human or AI assistant) working in this repo.
It records decisions that are settled and should not be re-litigated without cause.

## What iladub is

**iladub** — Sumerian *íl* ("to lift, carry, deliver, bring forward") + *dub*
("clay tablet, document") = "the document-carrier." It compiles **human-addressed
documents** (any format) into FAIR, contract-defined semantic knowledge graphs that
machines can read.

It is the document-compiling front end of the **ET(K)L** method
(*Extract, Transform-with-(K)nowledge, Load*), whose persistent namespace is
`https://w3id.org/iladub/etkl`.

## The project family — `iladub` is the root (decided 2026-07-01)

`iladub` is the namespace **root** and the owned artifact: it predates HGA, and `etkl` + `dec`
are related concepts arranged freely before Cagle's Holon Graph existed. iladub adopts the
holon graph as the architecture *for* its work and **consumes HGA as the external substrate**.

> **iladub = a thin epistemic core + `etkl` + `dec`** — the carrier that lifts knowledge from
> raw documents into HGA holons and governs the decisions made about them.

- **iladub** (thin **core**) — the assertion/proposition epistemics (the signature: assert
  only what you can ground, propose everything else, never let a proposition pass as an
  assertion). `CandidateConcept`, `GroundedNode`, `PromotionDecision`.
- **etkl** — the narrow-scope **K-transform**: raw document → grounded holon, conformed to a
  destination holon's required schema (the contract). Includes the doc-holon fabric
  (Raw/Clean/Semantic/GroundingPortal/MembraneHealth). *Could* one day be an HGA contribution
  (HGA defines holons; it doesn't build them from raw human-addressed documents) — not now.
- **dec** — **decidability / decisionality**: `DecisionHolon`, escalation, events, timeline
  (and `risk`, contextual risk, as a decidability measure). An HGA extension, built now
  because HGA isn't ready for strict decidability yet; **deliberately portable** — designed to
  be upstreamed to / replaced by an HGA equivalent later.
- **HGA** (`holon:`) — external substrate; consumed, aligned (`rdfs:subClassOf`/`seeAlso`),
  **never cloned** (see § Source ownership).
- **iladub.dev** — the docs site (Material for MkDocs). *(PyPI package name `iladub` and
  `iladub.dev` are unaffected by the namespace re-rooting: namespace ≠ package.)*

**Migration status:** The re-rooting from the previous `…/etkl/*` layout was completed
2026-07-01, and the w3id redirects are **live** (PR #6281, merged; verified 2026-07-02):
`w3id.org/iladub{,/etkl,/dec,/risk}` content-negotiate to the canonical `vocab/ontology/*.ttl`
on `main`, HTML → `iladub.dev`, and old `…/etkl` 301-redirects into the new roots. (See the
migration plan at `docs/superpowers/plans/2026-07-01-semantic-architecture-migration.md`.)

## Licensing (non-negotiable, applies everywhere)

- **Code** → Apache-2.0.
- **Vocabulary / ontology / spec** → CC-BY-4.0.
- Every published artifact carries author metadata and links to the ET(K)L
  namespace from its first release, so the dated record is part of the authorship trail.
- Author: François Rosselet. © 2026.

## Core design principles (do not violate)

0. **There is no unstructured data.** Structure is interpreter-relative; a document
   the industry calls "unstructured" is **human-addressed structure with a latent
   schema** — complete relative to its intended (human) interpreter, not absent.
   ET(K)L **recovers** the author's structure (it does not tokenise the source) and
   **carries** it into a **machine-addressed, modality-native** form (it does not
   flatten the target into rows). Using AI to produce SQL-ingestable rows by default is
   *neolegacy* and is forbidden. Never write "unstructured" as if structure were
   missing; the framing is **human-addressed vs machine-addressed structure**, in
   filigran everywhere we state. See `docs/manifesto.md`.

1. **Knowledge-first.** Knowledge engineering is the *first* milestone of the
   pipeline, not the last. A semantic data contract declares the target semantics,
   and a knowledge module is passed as an *argument* to the transform — never
   reconstructed by mappings at the end.

2. **The contract is an ontology, not a JSON/YAML schema.** Contracts declare typed,
   vocabulary-grounded *semantic objects* (identity, SKOS/OWL grounding, SHACL
   validation, participation in a wider graph) — not field names and primitive types.

3. **Assert only what you can ground; propose everything else — and never let a
   proposition pass as an assertion.**
   - **Assertions**: content groundable in a provided ontology → typed,
     contract-bound, SHACL-validated → the grounded graph.
   - **Propositions**: ungroundable content → quarantined `iladub:CandidateConcept`
     with a suggested upper-ontology anchor (e.g. gist), source provenance, the
     suggester, and a confidence. Never dropped, never faked.
   - A proposition enters the grounded graph **only** as the product of a
     **promotion decision** (`iladub:PromotionDecision`, a subclass of
     `dec:DecisionHolon`). This is enforced by SHACL: *every grounded node must be
     produced by a promotion decision.*

4. **A promotion is a decision holon.** Admitting a proposition is an accountable,
   agent-attributed, auditable act using the *same* `dec` vocabulary that models
   decisions in document *content*. The tool that reads decisions out of documents
   governs its own reading with the same decision model.

5. **Context is carried, not discarded.** Table cells, prose concepts, and figure
   findings converge on the *same* concept IRIs. The story around a table is often
   richer than the table; capture it.

6. **Provenance to the page.** Every carried object traces back to the source
   document region it came from.

7. **Only emit what the source supports.** Never fabricate resources/data to achieve
   "full coverage." Credibility over completeness.

8. **Neurosymbolic-first — formal semantic code prevails over procedural code (the gate).**
   Reading a human-addressed document is a *neurosymbolic* process, not a procedural one.
   iladub's edge is *filling semantic gaps* (as `dec` did for decidability), never
   hand-coding geometry around them. **No decision is implemented in procedural code
   until it has been classified and justified** — the default is semantic; procedural code
   must be *earned* (Python is iladub's reference-implementation language — the class is
   language-agnostic):
   - **AXIOM (default)** — the decision is *declarative* over an RDF evidence graph
     (consuming an existing ontology or filling a *named* gap with thin owned vocabulary),
     in one of **two world-split forms** — the split is load-bearing:
       - **Derivation → SPARQL `SELECT`/`CONSTRUCT`** (+ FnO IRIs), **open world**: recovery /
         transform / role decisions that *grow* the graph from evidence — monotonic and
         evidence-positive (a fact is derived only when its support is *present*, never
         inferred from absence). Any closed-world guard (counting, completeness, disjointness)
         is **holon-scoped**: query-local `NOT EXISTS`/`COUNT` closes *within* the one holon
         while the graph stays open.
       - **Constraint → SHACL**, **closed world**: the contract *membrane* validating what may
         *cross* into the clean holon (cardinality, `sh:closed`, promotion-required).
     **Never use closed-world/SHACL to *derive*** — inferring-by-absence violates §7 (assert
     only what the source supports). Recovery is open-world; the membrane is closed-world; the
     **holon is the closure boundary**.
   - **NEURAL** — genuinely perceptual / underdetermined decisions (any *"which
     columns/rows does X span / read / group"* reading judgment) are **GenAI-via-BAML
     proposing** under the assert/propose/promote epistemics (§3), **disposed by a
     semantic oracle** (tiling SHACL / reshape round-trip). *Never* a Python geometry
     heuristic with a tuned tolerance.
   - **PROCEDURAL** — reserved for irreducibly procedural computation: **raw extraction**
     (source → typed RDF facts) and **decidable exact arithmetic**. The class is *procedural
     code*, not a language — **Python in iladub's reference implementation**, TypeScript/.NET/
     Rust/… in any other; each instance must state *in the code and the spec why it is
     irreducible* to AXIOM or NEURAL.
   Any procedural code that isn't a justified PROCEDURAL step is a **defect**. A **tuned constant
   or tolerance is prima facie evidence** the decision belongs in NEURAL/AXIOM, not procedural code.
   Every spec/plan carries this gate as a hard Global Constraint; **reviewers enforce it**
   — a tuned geometric constant, or a Python heuristic answering a span/read/group/role
   question, is a *review failure* unless it is an oracle-disposed NEURAL proposal or a
   justified PROCEDURAL step. Exemplars already shipped: see `docs/wiki/concepts/neurosymbolic-exemplars.md`
   (the loop-by-loop catalog of compliant AXIOM/NEURAL/PROCEDURAL code, with file paths).

## Holonic interaction model (align, don't reinvent — esp. with the W3C Holon CG)

iladub is modeled as **interacting holons**, not just isolated definitions — *how
holons interact is the architecture*. A **RawDocumentHolon** and the **SemanticHolons**
(ontologies / SKOS terminology) interact through a governed **grounding portal**;
concept-matching at that portal is governed by **PromotionDecisions** at the contract
**membrane** (SHACL); what passes is assembled into a **CleanDocumentHolon** whose
**membrane-health is its cleanliness**. Assertions are *inside* the membrane;
propositions are candidates *at* it. See `docs/holonic-interaction.md`.

- We **align with**, and do **not** reinvent, the holonic-graph model. The **anchor
  is Cagle's W3C HGA** (`holon:` = `http://w3id.org/holon/`), the W3C Holon CG's
  reference ontology — *not* Welz's CGA (`urn:holonic:ontology:`), which remains useful
  conceptual prior art but is no longer the alignment target (decided 2026-06-23).
- **Alignment, not import:** the doc-holon fabric and grounding portal live in the
  `etkl` namespace and are aligned via `rdfs:subClassOf` to `holon:`
  (e.g. `etkl:CleanDocumentHolon ⊑ holon:DataHolon` (or `holon:Holon`),
  `etkl:RawDocumentHolon ⊑ holon:DataHolon`, `etkl:GroundingPortal ⊑ holon:Portal`)
  — never copied, never hard-imported. Reuse HGA's grounding lifecycle where it fits:
  iladub's `iladub:PromotionDecision` governs the `holon:GroundingRecord` →
  `holon:RegisteredStatus` transition that HGA leaves to a bare confidence gate.
- `dec` therefore generalizes from "decision-context only" toward "holon + interaction,"
  with `dec:DecisionHolon` as one holon type and `iladub:PromotionDecision` as the
  governed membrane-crossing.

### Posture toward the W3C Holon Community Group (settled 2026-06-23)

Cagle now chairs the **W3C Holon Community Group** (github.com/w3c-cg/holon), with his
own ontology **HGA** (`http://w3id.org/holon/`) and a **DataBook** authoring format.
This is the standardization venue for the general holon substrate. **iladub anchors to
HGA** (`holon:`), not Welz's CGA (`urn:holonic:ontology:`) — settled 2026-06-23; see the
alignment bullets above.

- **iladub does NOT compete with or reinvent what the CG builds.** Be a good citizen:
  align (not import), and contribute iladub's distinctive parts upstream rather than
  duplicating the substrate.
- **Defer to the CG (do not build a parallel version):** core holon vocabulary,
  portal/boundary machinery, the Markov-blanket / Friston–Bayesian layer, federation,
  generic event/projection/camera infra, the DataBook format + CLI.
- **iladub focuses on its differentiators:** (1) **document compilation** — the ET(K)L
  RawDocument→grounding-portal→CleanDocument front end; (2) **promotion epistemics** —
  SHACL-enforced "every grounded node is produced by an `iladub:PromotionDecision`,"
  which is *stronger* than HGA's confidence-gate (HGA routes low-confidence to
  `CandidateStatus` but does not require an accountable decision); (3) the **semantic
  data contract as ontology**; (4) **provenance-to-the-page**; (5) **domain-neutral
  worked examples** (healthcare/insurance) that can feed CG WG V (Industry Utilisation);
  (6) **contextual-risk governance** (`etkl/risk`) — a genuine *gap* in HGA (which has
  `hpol:` for access and `hbayes:` for probabilistic uncertainty, but nothing for
  contextual risk). Hosted in the ET(K)L family for now; a candidate CG contribution.
- **Information governance — align, don't reinvent the access half; contribute the risk half.**
  Access control rides HGA `hpol:` (ODRL) + `hview:` (ViewerPass) — do not build a parallel
  access layer. Risk is **contextual, not empiric**: `risk(condition, context) = condition ⊗
  effective_sensitivity(context)`, sensitivity inherited **top-down only**, a `risk:RiskAssessment`
  is a derived `hproj:Projection` (never a stored label — SHACL-enforced). AI access must equal
  the interacting user's access (the agent carries the user's identity; the membrane is the gate;
  enforced by `gsh:AiInheritsUserShape`). Worked example:
  `examples/transplant/transplant-governance.ttl` + `vocab/shapes/governance-shapes.ttl`.

## Source ownership (non-negotiable; the line we never cross)

We **develop** only the namespaces we own. HGA (Cagle's W3C Holon CG ontology) is an
**external source of truth we consume** — never one we author, edit, or redefine. Mixing the
two corrupts authorship provenance and the alignment story. This is settled (2026-06-29) and
**CI-enforced** by `tests/test_source_ownership.py`.

| We OWN — develop freely (root `https://w3id.org/iladub…`) | HGA — Cagle's; CONSUME only, never touch (`http://w3id.org/holon/…`) |
| --- | --- |
| the thin core `iladub:` · `etkl:` · `dec:` · `risk:` (+ their shapes, examples, Python) | `holon:` · `hev:` · `hpol:` · `hmk:` · `hproj:` · `hbayes:` · `hprov:` · `hspec:` · `hmedia:` · `hvc:` |

**The invariant (one line):** *In every authored RDF file, the subject of every triple is a
term we own. HGA terms appear ONLY as objects/types/targets — never as a subject.* We never
write `holon:X a owl:Class` or add any property to an HGA term; we only point our terms at
theirs (`our:T rdfs:subClassOf holon:T`).

Concrete rules:
1. **Edit only our four namespaces.** Adding `dec:escalatedTo` to `dec.ttl` is fine;
   declaring or annotating `hev:HolonEvent` anywhere is forbidden.
2. **HGA IRIs live only in `*-hga-align.ttl` modules and in HGA-bridging shapes/examples, as
   objects.** Core ontologies (`dec.ttl`, `risk.ttl`, `iladub.ttl`, `etkl.ttl`, `etkl-holons.ttl`) stay
   **standalone** — zero `w3id.org/holon` references (alignment-not-import; reasoner-free).
3. **Any local HGA copy is read-only and segregated** — fetched at test time or kept under a
   clearly-marked `vendor/hga/` snapshot (`@ <sha>`, "NOT OURS"). Never under `vocab/`.

iladub's role is to **complement HGA's gaps** (the accountable `dec:DecisionHolon`, promotion
epistemics, contextual risk, apex escalation), aligned by `rdfs:subClassOf`/`subPropertyOf`/
`seeAlso` — never to re-author the substrate.

## Serialization & stack conventions

- Ontologies, shapes, contracts, examples → **RDF Turtle** (`.ttl`) for authoring,
  **JSON-LD** for interchange.
- Validation → **pySHACL** (`inference="rdfs"`, `advanced=True` for SPARQL constraints).
- Namespaces: `iladub:` = `https://w3id.org/iladub#`, `etkl:` = `https://w3id.org/iladub/etkl#`,
  `dec:` = `https://w3id.org/iladub/dec#`, `risk:` = `https://w3id.org/iladub/risk#`;
  HGA alignment modules are `*-hga-align.ttl`.
- Decision/provenance reuse standards: `dec:DecisionHolon ⊑ prov:Activity`;
  evidence via `prov:used`, agency via `prov:wasAssociatedWith`, products via
  `prov:generated`. Don't reinvent provenance.
- Every vocabulary/shape ships with a worked example that conforms **and** a negative
  test that must fail. Tests run under `pytest`; CI runs them on every push to `main` and every PR (`.github/workflows/ci.yml`).
- Multilingual by construction: rationale/label literals may be language-tagged
  (de/fr/it) — do **not** constrain such properties to `xsd:string` (that rejects
  `rdf:langString`).

## Naming discipline (a hard-won lesson)

Before claiming any name, verify across **PyPI + GitHub (repo collision) + a web
search including "+ ontology / semantic / knowledge graph"**. "Free on PyPI" is
necessary but **not sufficient** — the check that matters is *no same-domain prior
art*. (This rule exists because an earlier candidate, `dubsar`, was clear on PyPI but
turned out to be a dormant, same-domain semantic-modeling project — which would have
muddied authorship provenance.)

## Authorship / FAIR posture

- Publish openly, dated, under your name (PyPI release dates, git history, Zenodo DOI,
  `CITATION.cff`). Open publication is *defensive*: it establishes prior art and a
  citable record, and published knowledge cannot be used to restrain you later.
- Keep the work domain-neutral in public examples (healthcare, insurance, etc.) — never
  tied to an employer's domain. Personal time, personal resources, no internal data.

## Loop & context hygiene (enforced, 2026-08-09)

**A loop is a session.** Starting a new loop requires a cleared context — not a continuation.

**Never work past 40% of the context window.** Accuracy degrades well before the window is
full: in the session that produced this rule, 40% was crossed at turn 222 of 763, and the
later 71% produced five blocked specs while the early part shipped a loop. The fourth spec of
that day misquoted this repo's own residue register — a fatigue signature, not a knowledge gap.

**Specs are written in the first third of a session or not at all.** A spec drafted late is a
draft to re-derive, not work to review.

**The handoff is written at 30%, while still accurate** — never saved for the end.

Enforced by `scripts/context_budget.py`, wired as a `UserPromptSubmit` hook in
`.claude/settings.json`: it reads the true per-turn figure the API reports
(`input + cache_read + cache_creation`) from the session transcript, stays silent below 30%,
asks for the handoff at 30%, and refuses new design work past 40%. Self-monitoring is the
thing that fails first, so the harness does it. See R76.

## Plan authoring discipline (enforced, 2026-08-09)

**A plan is a contract, not a draft of the code.** It states *interfaces, invariants and the
falsifying oracle*. It does **not** contain the function body.

This rule exists because of a measured failure, not a preference. The R73 adoption loop shipped
a 919-line plan against a 316-line spec, most of it verbatim implementation, and **five defects
were found in the plan text itself** — none in the implementers' work:

1. A half-applied index guard (`j < len(lines)` with no lower bound; the returned `admitted`
   never filtered at all).
2. `build_ledger` called **before** the only site that ever writes `RegionReport.tokens_*`, so
   an untouched escalated band's ink silently vanished from the denominator — **failing upward,
   and invisible to the plan's own tests.**
3. A self-contradictory instruction (declare the field *after* `repaired`, pass it *last*) that
   would have swapped two `DocumentReport` fields silently.
4. A `dec:supersedes` wiring that was **dead code for every document** — the plan named
   `_verdict_decision` when its own spec §5.4 had already named the right subject.
5. The V7 test the plan supplied **passed with the withdrawal loop deleted entirely.**

Defects 2 and 5 are one failure wearing two faces: *the plan authored both the code and the test
meant to check it, so the same misunderstanding shaped both, and no independent oracle existed.*

The rules:

1. **No implementation source in a plan.** State the signature, the invariants it must preserve,
   and the oracle that falsifies it. **Tests may still be given verbatim** — they are the spec's
   contract with the implementation — but the body that satisfies them is the implementer's to
   write. An implementer reduced to a transcriber cannot catch a plan defect, and the person at
   the keyboard is the one who would have found defect 2 in thirty seconds.
2. **Every load-bearing claim about existing code is MEASURED, and carries its measurement
   inline** (`file:line`, the command run, its output). A plan that says *"verify X still holds"*
   is a plan whose author did not. Defects 2 and 4 were both claims made from reading.
3. **Name the seam the implementer must check, not the answer.** Where a plan depends on an
   ordering, a call site, or a field being populated, say *which fact must be measured before
   writing the call* — e.g. *"MEASURE where `tokens_*` are actually written before you call
   this; do not assume the caller's position."*
4. **FALSIFICATION IS MANDATORY, per task.** Every task report carries a `## FALSIFICATION`
   block beside its TDD evidence: remove or invert the thing the new test pins, show the test
   **failing**, restore, show the suite green. **No falsification evidence ⇒ the task review
   fails.** A test that passes when its subject is deleted pins nothing, and this is the only
   proof that it does.

The five defects above were measured against
`docs/superpowers/plans/2026-08-09-adoption-at-document-scope.md` and its spec — read that plan
as the worked counter-example of what this section forbids.

**Reviewers enforce all four.** A plan containing a function body, an unmeasured load-bearing
claim, or a task report without a falsification block is a *review failure* — not a style note.

## Deferred residues — the register

Every loop that defers something records it in **`docs/superpowers/residues.md`**, which is the
**canonical** list of open residues. Each row carries what the residue is, where it was *measured*
(never assumed), why it was deferred, and what would close it. Loops append rows; a loop that closes
a residue deletes its row in the same change. Specs may describe a residue in prose, but do not rely
on a spec §7 to remember it — check the register.

## Documentation governance (spec 2026-07-31; lint-enforced)

Every tracked markdown file belongs to **exactly one class**, by location —
enforced by `tests/test_doc_governance.py` (SHACL membrane + SPARQL staleness,
under `pytest`): **Evidence** (`docs/superpowers/**`, `docs/loops/**`,
`docs/w3id/**` — immutable after loop close; `residues.md` is the mutable
register), **Wiki** (`docs/wiki/**` — LLM-maintained synthesis, committed,
never published), **Assertion** (the `mkdocs.yml` nav — authored, CC-BY,
describes the *released* artifact only), **Manual** (the READMEs + `RELEASE.md` —
their commands must run), **Contract** (this file — edited only on explicit
request), **Confidential** (`internal/` — never tracked).

- **Agents: for concepts, read `docs/wiki/index.md` first.** Specs are
  evidence, wiki is synthesis, the site is assertion. The wiki never
  substitutes for reading the exact `.ttl`/`.py`.
- **Epistemics as in §3:** a wiki page is a *proposition* (confidence-tagged,
  cites its sources, freely rewritten); a site page is an *assertion*, entered
  only via a release (`promoted_to` records the promotion). iladub.dev builds
  from release tags (`.github/workflows/release.yml`); the first tagged
  release supersedes the hand-deployed site.
- **Every spec/plan dated ≥ 2026-07-31 carries a `Doc impact:` block**
  (`none | increment | contradiction`). Increments queue for the next release;
  contradictions block the release tag (`scripts/release_gate.py`), not the loop.
  Earlier docs grandfathered.
- **Vault is cited (`vault:…` in wiki `sources:`), never merged, never
  written** — the prose analogue of § Source ownership.

## Open items (verify; do not assert as done)

- [x] w3id redirects for the old `…/etkl/*` namespace tree (done 2026-06-02, PR #6144, merged).
- [x] w3id `iladub` redirect rules for the re-rooting (done PR #6281, verified 2026-07-02 —
      see § Migration status).
- [x] Masthead glyph verified 2026-06-03: `𒅍` U+1214D (íl, "carrier") + `𒁾` U+12077 (dub,
      "tablet") = "the document-carrier".
- [x] `vocab/LICENSE` (CC-BY-4.0) + root `CITATION.cff` verified 2026-05-31.
- [ ] SNOMED CT / LOINC identifiers in examples are illustrative — confirm terminology
      licensing before redistributing real mappings. Keep example documents synthetic.
- [ ] Express the holonic interaction model in `vocab/` — but **scope it to iladub's
      differentiators** (grounding portal + membrane/promotion shapes + the
      RawDocument→CleanDocument traversal), *not* a parallel general holon ontology;
      defer the substrate to the W3C Holon CG and align by `rdfs:subClassOf`. Design
      fixed in `docs/holonic-interaction.md`; ontology work not yet started.
- [x] Alignment anchor settled 2026-06-23: **Cagle's W3C HGA** (`holon:`), not Welz CGA —
      see § Holonic interaction model.
