# Documentation Governance — Phase 3 (Wiki Layer + v0.0.3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Seed the wiki layer (spec §8 items 8–9), drain the promotion queue's one entry into authored site prose, and hand François a fully rehearsed tree so his `v0.0.3` tag runs the release train end-to-end (item 10 — the phase's closing proof).

**Architecture:** Task 1 closes the lintable half of R25 (index-membership becomes a fact + shape). Tasks 2–3 seed six concept pages + one source page — LLM-synthesized propositions, each citing verified evidence/code paths the lint enforces. Task 4 drains the queue: a drafted addition to `neurosymbolic-first.md` (Assertion class — François's PR review is the authorship act) + `promoted_to` back-link. Task 5 bumps the version, runs the full RELEASE.md rehearsal, and opens the PR. The tag itself is François's act, per RELEASE.md — this plan ends at the handoff.

**Tech Stack:** rdflib/pySHACL (existing), markdown frontmatter per spec §4. No new dependencies.

**Doc impact:** increment — wiki pages are propositions; the one Assertion change (`neurosymbolic-first.md` gains the exemplars section) is additive; no published claim contradicted.

## Global Constraints

- **Decisions locked by François (2026-08-01):** standard seeding (6 concepts + 1 source page); R26 drain-fact DEFERRED (registered; the v0.0.3 gate uses the no-tag fallback so the window cannot bite this release); site prose drafted by the implementer and **authored by François via PR review**; the tag is pushed **by François by hand**.
- **Wiki pages are propositions (spec §3/§4):** every claim cites a `sources:` path; `confidence: high` only when ≥2 independent evidence docs agree; a page NEVER asserts beyond its sources — when a source is ambiguous, say so in the page. The wiki never substitutes for the exact `.ttl`/`.py` (no code blocks copied wholesale; link by path instead).
- **Source paths must exist and be tracked** — verify EVERY `sources:` entry with `git ls-files <path>` before writing it; the membrane hard-fails a missing path. NEVER cite `docs/superpowers/residues.md` (R24: mutable Evidence — the first page citing it breaks the lint on every loop) and never cite untracked/gitignored paths.
- **Evidence-staleness discipline:** every seeded page's `updated:` is `2026-08-01`; cited evidence docs are all last-committed ≤ 2026-08-01, so the lint stays green. Run `pytest tests/test_doc_governance.py -q -W default::UserWarning` after EVERY task.
- **Tests:** repo venv — `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest …`. Full-suite baseline on `main`: 732 passed, 5 skipped.
- **Queue semantics (spec §8 item 9):** seeded pages whose concept is ALREADY asserted on a published nav page carry `promoted_to` from birth (the back-link) and never queue; only genuinely-unpromoted synthesis queues (`table-holon-compilation`, `doc-governance`). Only the exemplars page is drained in v0.0.3. Task 4 fixes RELEASE.md's wording to match.
- **Commits:** conventional style. Merge will be a merge commit (never squash).

---

### Task 1: Index-membership lint (closes the lintable half of R25)

**Files:**
- Modify: `tests/docgov_extract.py` (`_wiki_facts` + a small index parser)
- Modify: `vocab/shapes/doc-governance-shapes.ttl` (one new shape)
- Modify: `tests/test_docgov_extract.py`, `tests/test_docgov_shapes.py`
- Modify: `docs/superpowers/residues.md` (narrow R25's row)

**Interfaces:**
- Consumes: Phase-1/2 extractor (`extract`, `DG`, `doc_iri`, `parse_frontmatter`).
- Produces: per wiki-classed Document (except `docs/wiki/index.md` itself): `dg:inWikiIndex` (xsd:boolean — true iff `index.md` contains a markdown link to the page, path-relative to `docs/wiki/`). New shape `dg:WikiIndexMembershipShape` fails any wiki page with `dg:inWikiIndex false`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_docgov_extract.py`:

```python
def test_wiki_pages_carry_index_membership():
    g = extract(REPO)
    exemplars = doc_iri("docs/wiki/concepts/neurosymbolic-exemplars.md")
    assert (exemplars, DG.inWikiIndex, Literal(True)) in g
    # the index itself carries no membership fact
    index = doc_iri("docs/wiki/index.md")
    assert list(g.objects(index, DG.inWikiIndex)) == []
```

Append to `tests/test_docgov_shapes.py`:

```python
def test_wiki_page_missing_from_index_fails():
    g = Graph()
    d = _wiki(g)  # docs/wiki/concepts/ok.md with full frontmatter facts
    g.add((d, DG.inWikiIndex, Literal(False)))
    ok, report = _conforms(g)
    assert not ok and "index.md" in str(report)


def test_wiki_page_listed_in_index_passes():
    g = Graph()
    d = _wiki(g)
    g.add((d, DG.inWikiIndex, Literal(True)))
    assert _conforms(g)[0]
```

Note: the existing `_wiki` fixture graph carries no `inWikiIndex` fact — the shape below only fires on an explicit `false`, so `test_conforming_minimal_graph` stays green (extractor always emits the fact on live runs; synthetic fixtures without it are legacy-compatible).

- [ ] **Step 2: Run to verify failure**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_docgov_extract.py tests/test_docgov_shapes.py -q`
Expected: the three new tests FAIL (no `inWikiIndex` facts; shape missing).

- [ ] **Step 3: Implement the fact**

In `tests/docgov_extract.py`, add near the other helpers, and call it from `extract()`'s per-file loop for wiki-classed files other than `docs/wiki/index.md` (pass the pre-read index text in; read it once before the loop):

```python
def _index_links(repo: Path) -> set[str]:
    """Paths (repo-relative) that docs/wiki/index.md links to — PROCEDURAL
    extraction of markdown link targets, resolved against docs/wiki/."""
    idx = repo / "docs" / "wiki" / "index.md"
    if not idx.is_file():
        return set()
    return {
        str((Path("docs/wiki") / m).as_posix())
        for m in re.findall(r"\]\(([^)#]+\.md)\)", idx.read_text())
    }
```

In `extract()`, before the per-file loop: `index_links = _index_links(repo)`. Inside the loop, after `_wiki_facts(...)` for wiki-classed files:

```python
        if cls == "wiki" and path != "docs/wiki/index.md":
            g.add((d, DG.inWikiIndex, Literal(path in index_links)))
```

- [ ] **Step 4: Implement the shape**

Append to `vocab/shapes/doc-governance-shapes.ttl`:

```turtle
# Every wiki page must be listed in docs/wiki/index.md — the index is the
# agents' first read; an unlisted page is invisible synthesis (R25, lintable half).
dg:WikiIndexMembershipShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:sparql [
        sh:message "wiki page is not listed in docs/wiki/index.md (add its row)" ;
        sh:select """
            SELECT $this WHERE {
                $this <https://w3id.org/iladub/docgov#inWikiIndex> false .
            }""" ;
    ] .
```

- [ ] **Step 5: Run all docgov tests + live lint**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_docgov_extract.py tests/test_docgov_shapes.py tests/test_docgov_queries.py tests/test_doc_governance.py -q -W default::UserWarning`
Expected: all pass (the one existing wiki concept page IS linked from index.md).

- [ ] **Step 6: Narrow R25's residue row**

In `docs/superpowers/residues.md`, replace R25's **Residue** cell text with: `**The ≥2-references wiki admission rule is unenforced** — index membership is now linted (dg:WikiIndexMembershipShape, Phase 3), but whether a concept EARNS a page (≥2 evidence docs, or evidence + code) remains judgment` — keep the row's other cells, updating "What would close it" to: `Decide whether admission is lintable (citation-count query over the fact graph) or stays judgment; document the decision in the governance spec's successor`.

- [ ] **Step 7: Commit**

```bash
git add tests/docgov_extract.py tests/test_docgov_extract.py tests/test_docgov_shapes.py vocab/shapes/doc-governance-shapes.ttl docs/superpowers/residues.md
git commit -m "feat(docgov): wiki index-membership fact + shape (R25 lintable half)"
```

---

### Task 2: Seed concept pages — batch 1 (epistemics, promotion-decision, decision-holon)

**Files:**
- Create: `docs/wiki/concepts/assert-propose-promote.md`
- Create: `docs/wiki/concepts/promotion-decision.md`
- Create: `docs/wiki/concepts/decision-holon.md`
- Modify: `docs/wiki/index.md` (three new rows)

**Interfaces:**
- Consumes: the frontmatter contract (spec §4; enforced by `WikiShape`) and Task 1's index-membership shape.
- Produces: three synthesis pages Task 4/5's lint runs validate; the page names `[[assert-propose-promote]]`, `[[promotion-decision]]`, `[[decision-holon]]` used in `related:` links by Task 3's pages.

**Method (applies to every page in Tasks 2–3):** read the listed sources FIRST; write 300–600 words of synthesis that answers "what IS this thing, across loops" — not a copy of any single source. Structure: one-paragraph definition → how it works (citing each source by path inline) → what's settled vs open (cite residue IDs by number only, e.g. "R20", never the residues file as a source). Frontmatter per spec §4. Verify every `sources:` path with `git ls-files` before writing it. After each page, add its `index.md` row and re-run the lint.

- [ ] **Step 1: `assert-propose-promote.md`**

Frontmatter (sources verified against the tree; adjust ONLY by removing a path that `git ls-files` fails on — do not add unverified ones):

```yaml
---
title: Assert / propose / promote — the iladub epistemics
type: concept
sources:
  - vocab/ontology/iladub.ttl
  - vocab/shapes/iladub-shapes.ttl
  - docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md
related: ["[[promotion-decision]]", "[[decision-holon]]"]
confidence: high
updated: 2026-08-01
promoted_to: docs/assertion-proposition.md
---
```

(`promoted_to` from birth — spec §8 item 9's back-link: the site already asserts this concept on `assertion-proposition.md`, published pre-wiki.)

Content covers: assertions (groundable → typed, contract-bound, SHACL-validated) vs propositions (quarantined `iladub:CandidateConcept` with anchor/provenance/confidence, never dropped, never faked); the SHACL enforcement that every grounded node is produced by a promotion decision; the loop-K measured shape (137 grounded / 323 quarantined on the real document — cite the r17 spec).

- [ ] **Step 2: `promotion-decision.md`**

```yaml
---
title: Promotion decision
type: concept
sources:
  - vocab/ontology/iladub.ttl
  - vocab/ontology/dec.ttl
  - vocab/shapes/iladub-shapes.ttl
related: ["[[assert-propose-promote]]", "[[decision-holon]]"]
confidence: high
updated: 2026-08-01
promoted_to: docs/assertion-proposition.md
---
```

Content covers: `iladub:PromotionDecision ⊑ dec:DecisionHolon`; a proposition enters the grounded graph ONLY as the product of a promotion decision — accountable, agent-attributed, auditable; the prov reuse (`prov:used`/`wasAssociatedWith`/`generated`); how this is stronger than HGA's bare confidence gate; the doc-governance parallel (`promoted_to` in wiki frontmatter is the prose analogue).

- [ ] **Step 3: `decision-holon.md`**

```yaml
---
title: Decision holon (dec)
type: concept
sources:
  - vocab/ontology/dec.ttl
  - vocab/shapes/dec-shapes.ttl
  - vocab/shapes/escalation-shapes.ttl
related: ["[[promotion-decision]]"]
confidence: high
updated: 2026-08-01
promoted_to: docs/dec.md
---
```

Content covers: `dec:DecisionHolon ⊑ prov:Activity`; escalation, events, timeline; deliberately portable toward HGA (built now because HGA lacks strict decidability); the same vocabulary governs decisions read OUT of documents and decisions made ABOUT them.

- [ ] **Step 4: index rows + lint**

Add one row per page to `docs/wiki/index.md`'s table (same format as the existing row: link, one-line hook, confidence, updated). Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_doc_governance.py -q -W default::UserWarning`
Expected: green; promotion-queue warning still lists ONLY the exemplars page — all three batch-1 pages carry `promoted_to` from birth (item 9 back-links), so they never queue.

- [ ] **Step 5: Commit**

```bash
git add docs/wiki/
git commit -m "docs(wiki): seed concepts — assert/propose/promote, promotion decision, decision holon"
```

---

### Task 3: Seed concept pages — batch 2 (table compilation, grounding membrane, doc governance) + the HGA source page

**Files:**
- Create: `docs/wiki/concepts/table-holon-compilation.md`
- Create: `docs/wiki/concepts/grounding-membrane.md`
- Create: `docs/wiki/concepts/doc-governance.md`
- Create: `docs/wiki/sources/hga.md`
- Modify: `docs/wiki/index.md` (four new rows)

**Interfaces:**
- Consumes: Task 2's method block (read sources first; 300–600 words; verify paths; cite residues by ID only) and its page names for `related:` links.
- Produces: the completed standard seeding; `[[hga]]` as the citation target for alignment claims.

- [ ] **Step 1: `table-holon-compilation.md`**

```yaml
---
title: Table-holon compilation — the loop family
type: concept
sources:
  - docs/loops/2026-07-05-table-holon-loop.md
  - vocab/ontology/tab.ttl
  - vocab/shapes/tab-shapes.ttl
related: ["[[assert-propose-promote]]", "[[grounding-membrane]]"]
confidence: high
updated: 2026-08-01
---
```

Content covers: the loop-engineering paradigm (verifier-first canvas, silent-wrong impossible); the arc from Loop 3 (first semantic oracle) through transposed/matrix/multi-table/row-groups to loop K's grounding capstone; where the open residues cluster (R3, R4 families — by ID only).

- [ ] **Step 2: `grounding-membrane.md`**

```yaml
---
title: Grounding portal and the contract membrane
type: concept
sources:
  - vocab/ontology/etkl-holons.ttl
  - vocab/ontology/etkl.ttl
  - docs/superpowers/specs/2026-07-30-r17-direct-assert-gate-design.md
related: ["[[assert-propose-promote]]", "[[hga]]"]
confidence: medium
updated: 2026-08-01
promoted_to: docs/holonic-interaction.md
---
```

`confidence: medium` deliberately: the portal is designed (holonic-interaction) and partially expressed in vocab — the page must say which parts are shipped vs design-only, citing the sources for each. Content covers: RawDocumentHolon ↔ SemanticHolons interaction through the governed portal; membrane-health as cleanliness; assertions inside the membrane, propositions at it.

- [ ] **Step 3: `doc-governance.md`**

```yaml
---
title: Documentation governance — classes, lint, release train
type: concept
sources:
  - docs/superpowers/specs/2026-07-31-documentation-governance-design.md
  - vocab/shapes/doc-governance-shapes.ttl
  - scripts/release_gate.py
related: ["[[promotion-decision]]"]
confidence: high
updated: 2026-08-01
---
```

Content covers: the six classes and their truth conditions; evidence→wiki→assertion as propose→promote applied to prose; the freshness pipeline; the release train and the contradiction gate (note R26's same-day window by ID); what an agent should read when (wiki first, exact files for claims).

- [ ] **Step 4: `sources/hga.md`** (the one `type: source` page)

```yaml
---
title: HGA — Cagle's W3C Holon CG ontology (consumed, never authored)
type: source
sources:
  - vocab/ontology/iladub-hga-align.ttl
  - vocab/ontology/dec-hga-align.ttl
  - vocab/ontology/risk-hga-align.ttl
  - vocab/ontology/tab-hga-align.ttl
  - CLAUDE.md
related: ["[[grounding-membrane]]", "[[decision-holon]]"]
confidence: high
updated: 2026-08-01
---
```

Content covers: what HGA is (`holon:` namespace, the CG's reference ontology); the source-ownership invariant (HGA terms appear only as objects — one line, pointing at CLAUDE.md § Source ownership rather than restating it); which iladub terms align where (read the four align files and enumerate the actual `rdfs:subClassOf` targets — do not invent); what iladub deliberately does NOT build (defer-to-CG list). This page also demonstrates the `type: source` arm of `WikiShape`/the promotion queue (source pages never queue — verify in Step 6's warning output).

- [ ] **Step 5: index rows**

Add the four rows to `docs/wiki/index.md` (sources/hga.md links as `sources/hga.md` relative path).

- [ ] **Step 6: Lint + queue check**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_doc_governance.py -q -W default::UserWarning`
Expected: green; promotion-queue warning lists **exactly 3 pages** — exemplars, `table-holon-compilation`, `doc-governance` (the two genuinely-unpromoted syntheses; batch-1 pages and `grounding-membrane` carry item-9 back-links) — and does NOT list `sources/hga.md` (docType "source" never queues — the live proof of Phase-2's Task-4 deferred-minor gap).

- [ ] **Step 7: Commit**

```bash
git add docs/wiki/
git commit -m "docs(wiki): seed concepts — table compilation, grounding membrane, doc governance; HGA source page"
```

---

### Task 4: Drain the queue — exemplars → `neurosymbolic-first.md` (Assertion prose, François authors via PR)

**Files:**
- Modify: `docs/neurosymbolic-first.md` (new section near the end, before any closing material)
- Modify: `docs/wiki/concepts/neurosymbolic-exemplars.md` (frontmatter: add `promoted_to`, bump `updated`)
- Modify: `docs/wiki/index.md` (exemplars row: updated date)
- Modify: `RELEASE.md` (drain-wording fix)

**Interfaces:**
- Consumes: the exemplars wiki page (the synthesis being promoted) and the live `docs/neurosymbolic-first.md` (read it fully first — the new section must match its voice and heading style).
- Produces: promotion queue drops to 6; the PR's review of this diff is François's authorship act on the Assertion.

- [ ] **Step 1: Draft the site section**

Append to `docs/neurosymbolic-first.md` (adapt heading level to the page's existing structure) a section titled `## Shipped exemplars — the gate in practice` of 150–250 words: what the AXIOM/NEURAL/PROCEDURAL gate looks like in shipped code, naming the flagship cases from the wiki catalog (the declarative transform substrate with its round-trip oracle; role recovery as two-pass SPARQL derivation; region tiling as the closed-world constraint mirror; declarative kind classification with its frozen differential oracle) with file paths in backticks. This is ASSERTION prose: present tense, no confidence hedges, no residue IDs, describes only what is released. Do NOT link to the wiki page (the site never references unpublished trees).

- [ ] **Step 2: Set the promotion trail**

In `docs/wiki/concepts/neurosymbolic-exemplars.md` frontmatter: add `promoted_to: docs/neurosymbolic-first.md` and set `updated: 2026-08-01`. Update its `index.md` row's updated date.

- [ ] **Step 3: Fix RELEASE.md's drain wording**

In `RELEASE.md` step 1, replace the sentence `For each queued wiki page: author/refresh the state-page prose it feeds, set `promoted_to:` in the wiki page's frontmatter, update its `updated:`.` with: `For each queued page you choose to promote THIS release: author/refresh the state-page prose it feeds, set `promoted_to:` in the wiki page's frontmatter, update its `updated:`. Unpromoted pages stay queued — the queue is the visible, enumerable lag (spec §5), not a blocker.`

- [ ] **Step 4: Lint + queue check**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_doc_governance.py -q -W default::UserWarning`
Expected: green (`PromotedToAssertionShape` accepts the target — `neurosymbolic-first.md` is in the nav); queue warning now lists **2** pages (`table-holon-compilation`, `doc-governance`), exemplars gone.

- [ ] **Step 5: Strict site build**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m mkdocs build --strict && test ! -d site/wiki && echo OK`
Expected: builds; `OK`.

- [ ] **Step 6: Commit**

```bash
git add docs/neurosymbolic-first.md docs/wiki/ RELEASE.md
git commit -m "docs(site): promote neurosymbolic exemplars to the published page; RELEASE.md drain wording (queue = visible lag)"
```

---

### Task 5: Version bump + full release rehearsal + PR

**Files:**
- Modify: `pyproject.toml` (`version = "0.0.2"` → `"0.0.3"`)

**Interfaces:**
- Consumes: everything prior; RELEASE.md steps 1–4 as the rehearsal script.
- Produces: the PR whose review is François's authorship act, and a tree where his `git tag -a v0.0.3` is the only remaining step.

- [ ] **Step 1: Bump the version**

In `pyproject.toml`: `version = "0.0.3"`.

- [ ] **Step 2: Run RELEASE.md's checklist steps 2–4 verbatim**

```bash
/Volumes/WD Green/dev/git/iladub/.venv/bin/python scripts/release_gate.py
/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest -q
/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m mkdocs build --strict
```

Expected: gate clear (fallback 2026-07-31; all dated docs declare increment — including THIS plan); full suite green (baseline 732+ the new tests, 0 failed); strict build green.

- [ ] **Step 3: Commit and push the branch; open the PR**

```bash
git add pyproject.toml
git commit -m "release: bump to 0.0.3 (first tagged release — runs the full train)"
```

PR body must tell François: (1) reviewing the `docs/neurosymbolic-first.md` hunk IS the authorship act on the Assertion; (2) after merge (merge commit, never squash), he runs RELEASE.md step 5 — `git tag -a v0.0.3 -m "iladub v0.0.3" && git push origin v0.0.3` from updated `main` — and watches with `gh run watch`; (3) the trusted publisher is registered, so the publish step should log a successful OIDC exchange.

- [ ] **Step 4: Watch ci.yml green on the PR**

Run: `gh pr checks --watch` (or `gh run watch <id> --exit-status`).
Expected: pass. THEN STOP — merge is François's review decision; the tag is his hand.

---

## Completion checklist (Phase 3 definition of done — items after the PR are François's)

- [ ] Lint green with promotion queue = exactly 2 (`table-holon-compilation`, `doc-governance` — the honest lag for the NEXT release; `sources/hga.md` and all back-linked pages absent from the queue).
- [ ] Full suite green; `ci.yml` green on the PR.
- [ ] François reviews (authorship act on the site prose) and merges with a **merge commit**.
- [ ] François tags: `git tag -a v0.0.3 -m "iladub v0.0.3" && git push origin v0.0.3` — the train runs: guard → tests → gate → build → w3id smoke → leak guard → deploy → PyPI (first OIDC publish) → live probe.
- [ ] Post-release verification (either of us): `https://iladub.dev/neurosymbolic-first/` shows the exemplars section; `pip index versions iladub` (or the PyPI page) shows 0.0.3; the w3id targets respond 200.
- [ ] Spec §8 item 10 thereby closed — the governance spec's three phases are complete. Remaining open residues: R23, R24, R25 (narrowed), R26, R27.
