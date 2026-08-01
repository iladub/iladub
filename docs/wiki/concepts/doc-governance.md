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

# Documentation governance — classes, lint, release train

`docs/superpowers/specs/2026-07-31-documentation-governance-design.md`
opens from measured drift, not assumption: of 305 commits since 2026-07-15,
only 4 touched a published page, while `docs/neurosymbolic-exemplars.md` sat
referenced by `CLAUDE.md` yet belonged to no class. Its fix is **exactly one
class per tracked markdown file, derived from location**: Evidence
(`docs/superpowers/**`, `docs/loops/**`, `docs/w3id/**` — "records what was
measured; immutable after loop close," with `residues.md` carved out as the
deliberately mutable register), Wiki (`docs/wiki/**` — LLM-rewritten,
confidence-tagged, cites a source per claim), Assertion (files in the
`mkdocs.yml` nav — "matches the released artifact"), Manual (a small README
allowlist whose commands must run), Contract (`CLAUDE.md`, authored on
explicit request only), Confidential (`internal/**`, never tracked). A file
matching no rule is a lint failure, not a guess — `vocab/shapes/doc-governance-shapes.ttl`'s
`dg:DocumentShape` enforces `dg:docClass` with `sh:in` over exactly those
six string values.

**How it works.** The spec states the epistemics directly: "the loop record
is evidence, a wiki page is a proposition ..., a published page or contract
line is an assertion — crossed into only by an accountable promotion" — §3
of CLAUDE.md's assert/propose/promote applied to prose rather than RDF. The
freshness pipeline names four stages (propose at loop close → detect via
lint → gate the loop's definition-of-done → promote via a release campaign),
and `doc-governance-shapes.ttl` encodes the checkable half: `WikiShape`
requires title/`docType`/`confidence`/`updated`/a source on every wiki page;
`PromotedToAssertionShape` requires any `promoted_to` target to actually be
an Assertion; `WikiIndexMembershipShape` requires every wiki page to be
listed in `docs/wiki/index.md`. The promotion queue itself — wiki concept
pages with no `promoted_to` yet — is a SPARQL derivation, not a shape,
consistent with the spec's open-world/closed-world split.

The release train (spec §7) is where the contradiction gate lives:
`scripts/release_gate.py` blocks a tag build if any spec/plan registered
`Doc impact: contradiction` since the previous release tag (falling back to
the 2026-07-31 adoption date when there is no prior tag). Its own comment
flags the mechanism's known edge: the `_since_date` comparison is
day-granularity, and — per the residues register — **R26** names that this
fails open on a same-day or backdated-filename contradiction, proven against
the live query with both a same-day and a backdated fixture returning an
empty blocker list; RELEASE.md now tells the releaser to eyeball same-day
contradictions by hand until a full-timestamp or explicit-drain fact closes
it.

**What an agent should read, when.** Per CLAUDE.md's own pointer (itself
part of this governance): read `docs/wiki/index.md` first for what a
concept *is* — wiki pages are propositions, freely rewritten, never a
substitute for the exact source. Read the cited `.ttl`/`.py`/spec when the
exact mechanism, a number, or a claim's truth matters. Read the site
(`mkdocs.yml` nav) only for what the *released* artifact asserts.

**Settled vs open.** The six-class membrane, the wiki frontmatter shape, and
the promotion-queue/staleness derivations are shipped and lint-enforced
today under `pytest` (not yet CI-blocking — no `.github/` workflow exists
per the spec's own problem statement). The release-train pipeline itself
(§7's GitHub Actions, the w3id smoke test, PyPI trusted publishing) is
designed in the spec but this page's three sources evidence only the local
gate script and its known R26 gap, not a running CI pipeline.
