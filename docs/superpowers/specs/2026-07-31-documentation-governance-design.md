# Documentation governance — design

**Date:** 2026-07-31
**Status:** validated in brainstorming; awaiting implementation plan
**Scope:** every markdown document in the repo, the iladub.dev publication pipeline, and the
relationship to the external vault LLMWiki.
**Doc impact:** increment — establishes `docs/wiki/` (this spec seeds it); `CLAUDE.md`
governance section updated in-band; no published page contradicted.

## 1. Problem (measured, not assumed)

- **The public story drifts stale.** Of 305 commits since 2026-07-15, **4** touched a
  published page. The site's newest pages are `four-groundings.md` (07-24) and
  `neurosymbolic-first.md` (07-15); everything else in the nav dates 07-01→07-03, while
  loops H–K shipped through 07-30.
- **New docs have no home rule.** `docs/neurosymbolic-exemplars.md` is referenced by
  `CLAUDE.md` yet belongs to no class: not in the `mkdocs.yml` nav, not a loop record,
  not a README. Orphans accumulate one per oversight.
- **The leak boundary is convention, not a check.** Loop record and `internal/` are kept
  off the site by `exclude_docs` + `.gitignore` + care; nothing fails if a confidential
  file lands wrong.
- **Agents cannot tell which doc is authoritative.** 118 specs/plans + 16 site pages +
  `CLAUDE.md` with no stated precedence → wasted tokens and wrong premises. A committed,
  agent-facing synthesis layer keeps coding agents converged because it is *in context*.
- **`CLAUDE.md` currently asserts a CI that does not exist.** "CI runs them on push/PR"
  and "CI-enforced by `tests/test_source_ownership.py`" are false: the repo has no
  `.github/` directory, no workflows, no tags, no releases. This design makes the claims
  true rather than deleting them.

## 2. Decision summary

1. Every tracked markdown file belongs to **exactly one class**, derived from its
   **location** (no mass frontmatter migration). A file matching no rule is a lint failure.
2. A new **Wiki layer** at `docs/wiki/` — LLM-maintained synthesis, committed, reviewable,
   **never published** (added to `exclude_docs`). It is the agents' first read.
3. Documentation epistemics mirror iladub's own §3: the loop record is **evidence**, a
   wiki page is a **proposition** (confidence-tagged, freely rewritten), a published page
   or contract line is an **assertion** — crossed into only by an accountable promotion.
4. Freshness is a composed pipeline, not a single habit:
   **propose** (auto-draft wiki deltas at loop close) → **detect** (deterministic lint) →
   **gate** (loop cannot close red) → **promote** (a campaign, which *is* a release).
5. **iladub.dev builds from the release tag, never from `main`.** The site can neither
   describe unshipped code nor lag the shipped artifact: one site, one released version.
6. The vault relationship is **one-way**: vault is consumed and cited (`vault:` source
   entries), never merged, never written to. Same shape as the HGA source-ownership
   invariant, applied to prose: we author iladub docs; we cite vault.

## 3. The document classes

Precedence: **most specific path rule wins**; the Manual allowlist and exemptions are
checked before directory rules.

| # | Class | Location rule | Who writes | Truth condition | Published |
|---|-------|---------------|-----------|-----------------|-----------|
| 1 | **Evidence** | `docs/superpowers/**`, `docs/loops/**`, `docs/w3id/**` | the loop, at the time | records what was *measured*; **immutable after loop close** (carve-out: `docs/superpowers/residues.md` is the deliberately mutable register — rows appended by loops, deleted by the loop that closes them) | no |
| 2 | **Wiki** | `docs/wiki/**` | LLM-maintained, rewritten freely | every claim cites a source path; carries `confidence` | no |
| 3 | **Assertion** | `docs/*.md` present in the `mkdocs.yml` nav (+ `docs/narrative/`) | François, authored | matches the **released** artifact; dated CC-BY prior-art record | **yes** |
| 4 | **Manual** | allowlist: `README.md`, `vocab/README.md`, `demo/README-etkl-showcase.md` | François | its commands actually run | yes (in repo) |
| 5 | **Contract** | `CLAUDE.md` | François, on explicit request only | the decisions are settled | no |
| 6 | **Confidential** | `internal/**` (gitignored) | François | — | never |

**Exempt from classification** (data or tooling, not prose): `.claude/**`, `.agents/**`,
`*.databook.md` (example artifacts in DataBook format), untracked build output (`site/`,
`dist/`, `demo/out/`).

**External, not a class:** the vault (`Frosselet/vault`). Appears only as a citation in
wiki `sources:` lists (`vault:wiki/...`). Never a subject, only an object — the prose
analogue of the RDF ownership invariant.

### 3.1 Doctrine vs state (within Assertion)

- **Doctrine pages** — `manifesto.md`, `story.md`, `naming.md`, `assertion-proposition.md`:
  stability is the point. They change only when a decision is reversed or genuinely
  deepened — itself a campaign-level act. They do not ride the release train's queue.
- **State pages** — `architecture.md`, `etkl.md`, `neurosymbolic-first.md`,
  `four-groundings.md`, `holonic-interaction.md`, `dec.md`, `modality-native-targets.md`,
  `index.md`, `narrative/scope-evolution.md`, the three use-cases: they describe what the
  released system is and does, and must track it release by release.

## 4. The Wiki layer

```
docs/wiki/
  index.md        agents' first read: one line per page + confidence + updated
  concepts/       what an iladub thing IS, synthesized across loops
  sources/        one page per consumed external source (HGA modules, vault pages, papers)
```

Deliberate omissions vs the vault layout: no `overview.md` (the site *is* the narrative),
no `log.md` (`git log` + `residues.md` already cover chronology), no `entities/` /
`comparisons/` until a real need appears.

**Page admission rule** (stops a 118-page mirror of the spec record): a concept earns a
page when referenced by **≥ 2 evidence docs, or by evidence + code**. One spec, no reuse →
it stays evidence.

**Frontmatter** (Wiki pages only — no other class carries frontmatter):

```yaml
---
title: Promotion decision
type: concept              # concept | source
sources:
  - docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md
  - vocab/shapes/promotion-shapes.ttl
  - vault:wiki/concepts/holon-grounding.md    # external: cited, never merged
related: ["[[grounding-portal]]", "[[candidate-concept]]"]
confidence: high           # high = multiple evidence docs agree; medium = one; low = stub
updated: 2026-07-30
promoted_to: docs/assertion-proposition.md    # set when a release lifts it to the site
---
```

`promoted_to` is the proposition→assertion trail — the prose equivalent of
`prov:generated` on a `PromotionDecision` — and what lets a release enumerate
"N wiki pages supersede M site pages" instead of relying on memory.

**Agent usage:** `CLAUDE.md` gains one short pointer — *for concepts, read
`docs/wiki/index.md` first; specs are evidence, wiki is synthesis, the site is assertion.*
No hook, no strict-mode read blocking: synthesis must never stand in for the exact `.ttl`.

## 5. Freshness pipeline

| Stage | Mechanism | Cadence |
|---|---|---|
| **Propose** | at loop close, the agent drafts the wiki delta from the loop's spec + measurements (confidence-tagged, machine-written) | every loop |
| **Detect** | deterministic lint (§6) | every `pytest` run / push / PR |
| **Gate** | loop definition-of-done includes a green doc lint + a filled doc-impact block (§5.1) | every loop |
| **Promote** | a campaign drains the promotion queue and authors the site prose — and a campaign **is** a release (§7) | per release |

Two cadences by design: the wiki updates every loop (cheap, propositional); the site
updates per release (deliberate, assertional). The lag between them is enumerable — the
promotion queue — never silent.

### 5.1 Doc-impact registration (loop close)

Every spec/plan **dated ≥ 2026-07-31** must contain a `Doc impact:` block declaring one of:

- `none` — touches no documented concept;
- `increment` — adds to a state page's story → the wiki page updates in-band and enters
  the promotion queue; the site waits for the next release;
- `contradiction` — falsifies a claim on the published site → registered; the **release
  gate** (not the loop) blocks while any contradiction is undrained.

Because the site is tag-built (§7), a loop landing on `main` does not make the site false
— the site stays true *about the released version*. Contradictions therefore block the
*next tag*, not the loop itself; the loop's only blocking duty is honest registration.
Legacy specs/plans (118 files dated before adoption) are grandfathered: the requirement
does not apply retroactively.

## 6. The lint — neurosymbolic-first, dogfooded

Per the §8 gate, doc governance is not hand-coded Python rules:

- **PROCEDURAL** (irreducible — raw extraction): walk tracked markdown files, parse wiki
  frontmatter and the `mkdocs.yml` nav, read per-source last-commit dates from git, emit
  typed RDF facts. File I/O and date extraction only; path-glob classification is part of
  this extraction step.
- **AXIOM, closed world → SHACL** (the membrane): every tracked `.md` has exactly one
  class; every Assertion is in the nav and every nav entry resolves to a file; no Wiki or
  Evidence path is publishable (`exclude_docs` covers `wiki/`, `superpowers/`, `w3id/`,
  `loops/`); nothing under `internal/` is tracked; every `promoted_to` target is an
  Assertion; wiki frontmatter is complete.
- **AXIOM, open world → SPARQL `CONSTRUCT`** (derivations): the staleness set ("wiki page
  P cites evidence E; E's last commit postdates P's `updated`") and the promotion queue.
  Derived only from evidence *present*, never from absence.

**Severity:** membrane violations and evidence-staleness → hard fail. Code-staleness
(a cited `.py`/`.ttl` changed) → warning list only — code churns every commit; a hard gate
there would make every loop a doc loop. Manual pages are checked by *executing* their
quickstart commands — at release time, not per push.

Lands as `tests/test_doc_governance.py` (pySHACL + rdflib, both already dependencies), so
it runs locally under `pytest` today and becomes CI-blocking the day the workflow lands.

**Explicitly out of phase-1 scope:** mechanical enforcement of Evidence immutability
(requires git-history archaeology; stays a convention for now).

## 7. The release train

**A promotion campaign is a release; a release is the only thing that changes iladub.dev.**

Pipeline (GitHub Actions — new; makes `CLAUDE.md`'s CI claims true):

```
on push / pull_request:   pytest  (unit + source-ownership + doc-governance lint)
on tag v*:                pytest
                          → gate: no undrained contradiction registered   (blocks the tag build)
                          → mkdocs build   (flat site, from the tag)
                          → w3id smoke test against LOCAL build output    (pre-deploy, deterministic):
                              site/index.html, site/404.html,
                              site/holonic-interaction/index.html, site/etkl/index.html,
                              site/dec/index.html, site/assertion-proposition/index.html
                          → mkdocs gh-deploy (gh-pages branch; docs/CNAME is tracked, domain survives)
                          → PyPI publish via trusted publishing (OIDC, no token secret) — only if version bumped
                          → optional non-blocking live 200 probe of the w3id targets post-deploy
```

Decisions folded in:

- **No `mike` / versioned site.** The live w3id redirect rules target flat paths
  (`/holonic-interaction/`, `/etkl/`, `/dec/`, `/assertion-proposition/`); `mike` would
  move content under `/latest/` and 404 the persistent identifiers. Flat tag-built site
  gives the whole "docs ≡ shipped code" requirement without breaking them.
- **Errata** shrink to their honest size: a page wrong *about the version it documents* is
  a doc bug, fixed by a docs-only patch tag — never a mid-flight edit of the live site.
- **Release checklist** (human act, deliberately): drain the promotion queue → author
  state-page prose from the queued wiki pages → set `promoted_to` → update doctrine pages
  only if a decision changed → bump version → tag.

## 8. Repo changes (what the plan must deliver)

**Phase 1 — Foundation** (shippable alone):
1. `tests/test_doc_governance.py` + `vocab/shapes/doc-governance-shapes.ttl` + the
   extractor + `.rq` queries (§6).
2. `mkdocs.yml`: add `wiki/` to `exclude_docs`.
3. `CLAUDE.md`: add the compact governance section (classes, two paths, wiki-first
   pointer); correct the two false CI claims (true once Phase 2 lands — sequence the
   wording accordingly).
4. Resolve the orphan: `docs/neurosymbolic-exemplars.md` → `docs/wiki/` as its first
   seeded page (it is synthesis across loops — a wiki page in an assertion's clothing);
   update the `CLAUDE.md` reference.
5. Loop canvas template: add the required `Doc impact:` block.

**Phase 2 — Release train:**
6. `.github/workflows/ci.yml` (pytest on push/PR) and `release.yml` (tag pipeline, §7).
7. w3id smoke test; PyPI trusted-publisher registration; release checklist doc (a Manual).

**Phase 3 — Wiki layer:**
8. Seed `docs/wiki/index.md` + concept pages meeting the ≥2-references rule.
9. Promotion-queue query wired into the release checklist; `promoted_to` back-links for
   already-published concepts.
10. First release `v0.0.3` runs the full train end-to-end — the phase's closing proof.

## 9. Global constraints

- **Neurosymbolic gate (§8 of CLAUDE.md)** applies to the lint itself: classification
  facts are PROCEDURAL extraction; membership/membrane is SHACL; derivation is SPARQL.
  Any Python rule beyond extraction is a defect.
- **No overfitting:** the lint must pass/fail correctly on the *current* census (148
  tracked markdown files including the stragglers of §3's exemption list), not on an
  idealized tree.
- **Source ownership** extends to prose: vault and HGA material is cited, never copied.
- **Honest failure:** if the lint cannot classify a file, it fails loudly; it never
  guesses a class.

## 10. Out of scope

- Graphify or any external code-graph tooling (evaluated 2026-07-31; navigation aid at
  best, no bearing on governance).
- Mechanical Evidence-immutability enforcement (git archaeology; deferred).
- Versioned docs (`mike`) — rejected while w3id targets flat paths.
- Any write path to the vault; any vault content mirrored into this repo.
- Auto-publishing LLM prose to iladub.dev (propositions must never pass as assertions).
