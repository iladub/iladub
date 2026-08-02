# Real-document generalization — Loop L + the corpus campaign — design

**Date:** 2026-08-02
**Status:** validated in brainstorming; awaiting implementation plan
**Doc impact:** increment — adds the corpus harness + campaign discipline; the notebook design
(§7) is parked, not shipped; no published page contradicted.

## 1. Problem (measured, not assumed)

- **The shipped compiler cannot compile today's real GrainCorp stem.** Fetched live
  (2026-08-02): `Shipping-Stem-2026-07-31.pdf` from the [ports page]
  (https://grains.graincorp.com.au/ports-shipping/), 3 pages, 821 words on p0, the exact
  `GRAINCORP SHIPPING STEM` header the loops worked on. `compile_tables` (public API,
  per-page): **page 0 escalates `MERGE_AMBIGUOUS`, pages 1–2 escalate
  `REGION_TILING_FAILED`, score 0.0 everywhere** — while loop K recorded **0.9496 / 509
  cells** on its late-July edition (spec 2026-07-30-graincorp-grounding-design.md).
  Either a near-identical edition diverges in a way that breaks the compiler, or loop K's
  measurement path differs from the public API path. Both possibilities are defects of
  generality or of measurement honesty; neither is acceptable.
- **The escalation is honest but wrong-headed.** §7 held (nothing was faked; a
  `CandidateConcept` with `tab:HierarchicalTable` anchor came back in-band). But a human
  reads this stem without doubt or hesitation. An escalation on a document humans read
  fluently is not "honest refusal" — it is an implementation gap wearing honesty's
  clothes.
- **The synthetic battery is self-tailored.** Every fixture in `tests/etkl/fixtures.py`
  was written by the same hands that wrote the methods — including
  "GrainCorp's shape, synthetically." The no-overfitting rule was meant to prevent
  tuning to examples; generating our own examples is a subtler form of the same bias.
  The suite being green (735 passed) while the real document escalates is the
  measurement of that bias.
- **Real documents rot and are copyrighted.** GrainCorp's 2025 stem URLs are already
  404; the PDFs are third-party works we must never commit (CLAUDE.md: synthetic
  example documents; no redistribution). Any corpus mechanism must survive both facts.

## 2. The invariant (the campaign's verifier — falsifiable, standing)

> **For any real document a competent human reads without hesitation, ET(K)L must
> either compile it, or escalate with a NAMED ambiguity that the human adjudicator
> confirms is genuinely semantic.** A non-semantic escalation — one where the human
> says "there is nothing ambiguous here" — is a compiler defect, full stop.

- Escalations on corpus documents are **adjudicated by François** — an accountable,
  recorded act (the corpus manifest records adjudications as RDF; the prose analogue of a
  `dec:DecisionHolon`, kept thin).
- The bar deliberately excludes score-chasing: a *correct* escalation (true semantic
  ambiguity, e.g. a caption that genuinely belongs to two tables) passes the invariant.
  The verifier is about the *class* of failure, not a percentage.
- This invariant supersedes the synthetic suite as the campaign's primary oracle. The
  synthetic suite remains the regression net (it pins fixed behavior cheaply); it is no
  longer evidence of generality.

## 3. Loop L — diagnose the stem divergence (first specimen)

**Goal/verifier (designed first):** one of two exits, both evidence-backed:
1. `Shipping-Stem-2026-07-31.pdf` page 0 **compiles** via the public API with a score in
   loop K's neighborhood, and the fix is a *generality* fix (classified through the §8
   gate, no tuned constants, synthetic suite stays green); or
2. the divergence is **measured and pinned** — edition diff (fonts, rules, spacing,
   generator metadata) or measurement-path diff (what loop K actually ran vs
   `compile_tables(pdf, 0)`) — the escalation is proven semantic or the gap is
   registered as a residue with its closure named, and the manifest records the
   adjudication.

**Method:** systematic debugging, geometry-first: where does the pipeline lose the
columns (`extract_words` → `text_lines` → `detect_bands` → `infer_leaf_grid` →
header-confirmed refinement)? The crushed ASCII render (`GC FMonPort ReferExpoName…`)
suggests column pitch/overlap at extraction level — measure, don't guess. Compare
against loop K's edition **if locatable** (it was never committed; check local
non-repo storage); if unavailable, diagnose the 07-31 edition on its own terms — the
invariant does not care which edition loop K used, only that THIS one reads fluently
to human eyes and must therefore compile or escalate semantically.

**Constraints:** the §8 gate binds every fix (a span/read/group question resolved by a
Python heuristic with a tolerance is a review failure); fixes must not regress the
synthetic suite; the real PDF stays out of the repo (scratchpad/corpus only).

## 4. The corpus harness (infrastructure; makes "extensive tests on real examples" permanent)

- **`corpus/` is gitignored** (listed next to `internal/` in `.gitignore`). Populated
  locally by a fetch script; never enters the repo or the site.
- **`tests/corpus-manifest.ttl` is tracked** — knowledge-first: the manifest is RDF in a
  thin repo-internal namespace (`cor:` = `https://w3id.org/iladub/corpus#`, same
  posture as `dg:`: not published, not w3id-registered). Per document:
  `cor:url`, `cor:family` (ag-trade | gov-stats | financial | health),
  `cor:fetched` (xsd:date), `cor:sha256` (pins the edition actually measured — the
  manifest outlives the URL), `cor:pages`, `cor:expectedVerdict` — one of
  `cor:CompilesAbove` (with `cor:scoreFloor`), `cor:SemanticEscalation` (with
  `cor:ambiguity` naming it in prose), or `cor:Unadjudicated` (freshly added, first
  run pending) — and, once adjudicated, `cor:adjudication` (agent, date, rationale).
- **`scripts/fetch_corpus.py`** (justified PROCEDURAL: network + file I/O + checksum):
  reads the manifest, downloads what is absent, verifies sha256 (a checksum mismatch
  means the URL now serves a different edition — recorded, not silently accepted;
  the manifest is then updated deliberately, never automatically).
- **`tests/test_corpus.py`**, pytest marker `corpus`: for each manifest document
  present in `corpus/`, run the public-API compile (+ grounding where a contract
  exists, e.g. the stem contract) and assert the manifest's expected verdict.
  **Documents absent → skip with a visible count** — the default suite and CI stay
  deterministic and network-free; the battery runs locally (`pytest -m corpus`) and
  its tally is quoted in loop evidence. Adding the marker to `pyproject.toml`'s pytest
  config so unknown-marker warnings don't appear.
- **Verdict discipline:** `test_corpus` NEVER auto-updates the manifest. A verdict
  change (new compile success, new escalation) is a measured event a loop records by
  editing the manifest in a reviewed commit — the same append/adjudicate rhythm as
  `residues.md`.

## 5. Seed corpus (first manifest entries; grown by every campaign loop)

| Family | Documents (fetch-at-runtime URLs; sha256 pinned at first fetch) |
|---|---|
| ag-trade | GrainCorp Shipping Stem 2026-07-31 (already in scratchpad; the Loop-L specimen) · GrainCorp Capacity 2026-07-31 · CBH shipping stem (current edition) |
| gov-stats | 2 documents: one ABS release table, one Eurostat/BFS table (chosen at implementation for hierarchical headers + subtotals; stable institutional URLs preferred) |
| financial | 1 public annual-report financial-statements extract (nested subtotal ladder, multi-year comparatives) |
| health | 1 WHO or public clinical reference table (keeps the neutral-domain family exercised) |

Seven documents to start — small enough to adjudicate honestly, real enough to bite.
All seeded as `cor:Unadjudicated`; the first battery run measures, François
adjudicates every escalation, and the manifest's expected verdicts are set from those
adjudications. Each *defect* the battery reveals becomes its own loop (M, N, …) with
its own canvas; the battery re-run is every such loop's definition-of-done.

## 6. What this changes about the standing rules

- The no-overfitting memory gains teeth: "every fix must generalize to every document"
  now has a concrete, third-party test — a fix that moves fixtures but not corpus
  documents is decoration.
- The synthetic fixtures are demoted from evidence-of-generality to regression net
  (stated here; CLAUDE.md unchanged — this is loop discipline, not contract).
- Public examples stay synthetic and the domain-neutral posture holds for *published*
  material; the corpus manifest (tracked) does name ag-trade sources — accepted, as
  `examples/shipping/` already took that step illustratively.

## 7. Parked: the notebook companion update (design agreed 2026-08-02, sequenced after Loop L)

Decisions locked with François, recorded here so the later plan needs no re-litigation:
Part J + an evidence-graph interlude; narration-only truth pass over Parts A–I;
notebook executed headlessly in CI (env-guarded live cell, `demo` extra);
**dual-path Part J** — synthetic stem-shaped default (deterministic, CI-run) + a live
cell that scrapes the ports page, fetches today's stem to a temp dir, runs the same
compile→ground pipeline, and honestly reports whatever it measures (score or in-band
escalation), skipping gracefully offline; nothing GrainCorp-authored committed.
The live cell's story depends on Loop L's outcome — hence the sequencing.

## 8. Out of scope

- Committing any third-party document (rights + synthetic-only rule).
- Auto-adjudication of escalations (the human is the oracle of "semantic").
- A public benchmark publication from the corpus (interesting later; rights review first).
- CI running the corpus battery (network + nondeterminism; local by design for now).
