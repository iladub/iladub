# Real-document generalization — the accommodation layer, Loop L, and the corpus campaign — design

**Date:** 2026-08-02
**Status:** validated in brainstorming; awaiting implementation plan
**Doc impact:** increment — adds the accommodation-layer architecture, the corpus harness +
campaign discipline; the notebook design (§7) is parked, not shipped; no published page
contradicted.

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

## 2b. The accommodation layer — invert the renderer before reading the report

**Thesis (François, 2026-08-02; forensically confirmed on the specimen):** tables are
reports — the logical layout is fixed and only the data varies. The variance that breaks
machines is **page-constraint accommodation**: text wrapping, column/row resizing,
scale-to-fit — a *readability optimization with zero semantic content*, applied
deterministically by the generating software. A human's eye discounts it without noticing;
a machine that reads structure straight off the accommodated glyphs mistakes every
re-accommodation for a new document.

**Forensic evidence (the 2026-07-31 stem):** PDF metadata `Producer: Microsoft: Print To
PDF`, `Title: Shipping Stem 2026 07 31.xlsx` — an Excel report printed by a named human;
dominant font 5.28 pt across 3,937 chars on p0 (scale-to-fit compressed a ~11 pt sheet to
~48 %); 202 border rects (Excel cell edges surviving as exact geometry). The escalation
measured in §1 is scale-induced glyph collision degrading whitespace-based grid
inference — accommodation, unmodeled.

**The architecture:**
- **Forward model:** logical report template (fixed) + edition data → layout engine
  (auto-fit, word-boundary wrap, row-height growth, clip-at-edge, scale-to-fit, page
  breaks, repeated headers) → glyphs. The engine is deterministic; therefore invertible
  as a *modeling* problem, not a perception problem.
- **De-accommodation stage:** new pipeline stage between measurement and banding —
  glyphs + rects (+ Producer metadata) → estimated accommodation parameters (scale,
  column edges, wrap map) → the **logical grid in template coordinates**. All existing
  structural/semantic reading (classify, compile, roles, grounding) then consumes the
  logical grid, where the report is stable across editions.
- **Software-aware ontology, two layers (decided 2026-08-02):** a thin owned namespace —
  `render:` = `https://w3id.org/iladub/etkl/render#`, repo-internal posture at first
  (like `dg:`), a candidate for the published etkl family once the laws stabilize —
  holding (i) **universal accommodation laws** — uniform scale, wrap only at word
  boundaries within a column, clip at the column edge, borders at cell edges, wrapped
  continuations carry blanks elsewhere (R18's blank-below convention, now a law rather
  than an observed habit) — and (ii) **per-generator refinement modules**
  (`excel-print-to-pdf` first), gated by *detected* Producer metadata, never guessed.
  Unknown generators still get the universal layer.
- **Gate classification:** the laws are AXIOM (declarative over the glyph/rect evidence
  graph); parameter estimation is exact arithmetic (a scale factor is a ratio; column
  edges are rect coordinates) — PROCEDURAL only at the raw-extraction rim; genuinely
  underdetermined readings (e.g. wrap-vs-new-row with no borders) are NEURAL
  propose→oracle→dispose. **The oracle is the loop-one signature lifted to layout:**
  propose (template, scale, wrap map) → forward-accommodate → diff against the measured
  glyphs. A tuned tolerance anywhere in this layer is a review failure.
- **Provenance through the renderer:** the accommodation record (scale, widths, wraps)
  joins the doc-holon — every logical cell traces to its glyphs *and* to the
  accommodation that displaced them. Provenance-to-the-page becomes
  provenance-through-the-renderer.
- **Cross-edition identifiability:** corpus documents group into a **series** (§4);
  the template is the series invariant, so each additional edition of the same report
  over-determines it. The corpus is thereby also template-learning evidence, not only
  a test battery.

**Pagination taxonomy (François, 2026-08-02).** Multi-page documents are unhandled today
(`compile_tables` is strictly single-page; no document driver exists). Three cases, each
with a DIFFERENT resolution — conflating them would be the defect:
1. **Unrelated tables on consecutive pages** — not accommodation; needs only a document
   driver compiling pages independently, never stitching.
2. **One logical table split across pages, with or without repeated headers** — the page
   break IS an accommodation operator (Excel print-titles = its repeated-header law).
   De-accommodation: recognize continuation (identical ruled column x-positions under
   the same scale; leaf header equal to page 1's, or a headerless first line that is
   body-shaped and column-aligned), drop the repetition, concatenate the logical rows
   into ONE table holon. Provenance keeps each row's true page.
3. **The same template split along one dimension** (a page per port / year / …) —
   pagination as *denormalization along a dimension*: each page compiles to the same
   template; the page-scoped dimension value (typically a banner/title cell — the rows
   §3's header-stack law learns to read) is recovered as a column of the base facts,
   via the loop-I inversion machinery meeting series/template identity within one
   document. The corpus's gov-stats family will supply natural specimens.
Cases 1–2 are **Loop M** (outlined below); case 3 is designed here and deferred until a
corpus specimen demands it — never built speculatively (§7 of the core principles).

## 3. Loop L — diagnose the stem divergence = the accommodation layer's first slice

**Goal/verifier (designed first):** one of two exits, both evidence-backed:
1. `Shipping-Stem-2026-07-31.pdf` page 0 **compiles** via the public API with a score in
   loop K's neighborhood, and the fix is a *generality* fix (classified through the §8
   gate, no tuned constants, synthetic suite stays green); or
2. the divergence is **measured and pinned** — edition diff (fonts, rules, spacing,
   generator metadata) or measurement-path diff (what loop K actually ran vs
   `compile_tables(pdf, 0)`) — the escalation is proven semantic or the gap is
   registered as a residue with its closure named, and the manifest records the
   adjudication.

**Hypothesis H (from §2b, falsifiable):** the escalation is scale-induced glyph
collision breaking whitespace-based grid inference; a grid built from the 202 border
rects (exact column edges, immune to collision) de-accommodates the page and the
existing compile machinery succeeds on the logical grid.

**Method:** systematic debugging, H first — build the border-rect grid, re-run compile,
measure. If H holds, ship it as the accommodation layer's first thin slice (universal
law: *borders sit at cell edges*; Excel refinement gated by the Producer metadata that
this specimen carries). If H fails, fall back to geometry-first tracing
(`extract_words` → `text_lines` → `detect_bands` → `infer_leaf_grid`) — measure where
the columns are lost, don't guess. Compare against loop K's edition **if locatable**
(never committed; check local non-repo storage); if unavailable, diagnose the 07-31
edition on its own terms — the invariant cares only that THIS edition reads fluently
to human eyes and must therefore compile or escalate semantically. Vertical-slice
discipline: Loop L ships the smallest de-accommodation that makes the real stem
compile end-to-end (through grounding against the stem contract); wrap-map inversion
and the full forward-render oracle are later loops of the campaign.

**Constraints:** the §8 gate binds every fix (a span/read/group question resolved by a
Python heuristic with a tolerance is a review failure); fixes must not regress the
synthetic suite; the real PDF stays out of the repo (scratchpad/corpus only).

## 3b. Loop M (outlined; planned after Loop L closes) — pagination de-accommodation

**Goal/verifier:** the whole 3-page stem compiles as ONE logical table via a new
document-level driver (`compile_document`, name indicative), with the continuation
pages stitched per taxonomy case 2 and every row's provenance keeping its true page;
unrelated-tables documents (case 1, synthetic fixture) stay unstitched. Loop L's
Task-4 measurement (do the stem's continuation pages repeat the leaf header?)
determines which continuation law the slice implements first. Grounding then runs on
the full stitched document — the tally comparable to loop K's full-document numbers.
Case 3 stays out of Loop M's scope.

## 4. The corpus harness (infrastructure; makes "extensive tests on real examples" permanent)

- **`corpus/` is gitignored** (listed next to `internal/` in `.gitignore`). Populated
  locally by a fetch script; never enters the repo or the site.
- **`tests/corpus-manifest.ttl` is tracked** — knowledge-first: the manifest is RDF in a
  thin repo-internal namespace (`cor:` = `https://w3id.org/iladub/corpus#`, same
  posture as `dg:`: not published, not w3id-registered). Per document:
  `cor:url`, `cor:family` (ag-trade | gov-stats | financial | health),
  `cor:series` (editions of the same fixed report share a series — the template
  invariant of §2b; e.g. all GrainCorp stem editions), `cor:producer` (the PDF's
  Producer metadata, recorded at fetch),
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
