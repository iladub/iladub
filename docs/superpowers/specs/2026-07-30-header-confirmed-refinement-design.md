# Header-confirmed rule refinement (Loop G attempt 2 — residues R13 + R1)

- **Date:** 2026-07-30
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Sixth loop of the GrainCorp real-document push
  (A = PR #67; B = PR #68; C = PR #69; C.1 = PR #70; D = PR #71; F = PR #72). **Second attempt** at
  R13; attempt 1 (branch `iladub-rule-column-refinement`, unmerged) is post-mortemed in
  `docs/superpowers/residues.md` §"R13 attempt 1", and this design starts from its red test.
- **Origin:** Rules coarser than the columns merge real columns. GrainCorp's measure column holds
  `Date Loading Completed | Commodity | Total` with no interior rule, compiling as one column at
  confidence 1.0. Attempt 1's interior-gutter rule reached the right answer on the target but was
  **killed by a counter-example**: an ordinary monospaced ruled table whose values carry a
  column-aligned internal space (`AB CDEFGH`, `12 500`) forms the same blank-run signal, so a
  phantom column was manufactured and `compile_tables` **crashed** on a valid document.

---

## 1. Purpose and scope

Split the columns the author's rules left out — **and only those** — by treating attempt 1's
interior-gutter boundaries as **candidates** that must be **confirmed by the header** before they
become columns. The discriminator is not geometry: it is *whether the author labeled both sides*.

The crash itself pointed here: attempt 1 died on `tab:CoverageShape` — a leaf column no header
covers. The membrane already knew the phantom column was wrong; the defect was that refinement was
**asserted** instead of **proposed and disposed**. Attempt 2 consults the same evidence *before*
asserting, and additionally closes the crash class at the membrane.

**In scope:**

1. **Candidate generation** — attempt 1's `geometry.refine_rule_columns`, reused unchanged
   (cherry-picked with its tests), demoted from decider to proposer.
2. **Header confirmation (AXIOM)** — a transient per-band evidence graph of header-region **char**
   ink + candidate boundaries, and `vocab/queries/confirm-boundary.rq`: a candidate is confirmed iff
   header ink lies strictly left AND strictly right of it within its author interval, and no header
   glyph straddles it. Unconfirmed candidates are dropped; the band keeps the author grid.
3. **Attempt 1's plumbing, cherry-picked** — `Band.column_xs` (derived, distinct from author-drawn
   `Band.rules`), `_rule_boundaries` preferring it, and the `recover_leaf_grid` sub-band carry with
   its mutation-verified regression test.
4. **The membrane backstop** — the plain hierarchical assert in `compile.py` is the only region
   path that writes into the graph without a scratch gate, which is why attempt 1 *crashed* at final
   validation instead of escalating. It gets the same `scratch → region_tiles → commit-or-escalate`
   treatment the matrix and row-hier paths already have. Any future bad region, from any loop,
   escalates in-band instead of killing the compile.
5. **Post-mortem debts:** the no-synthesised-`Rule` guard gets a **real seam** (band construction
   extracted to a callable helper so the test exercises production code, not a copy — attempt 1's C2);
   `refine_rule_columns`' docstring states the **true** trailing-run mechanism (attempt 1's I1); the
   per-interval `N` discontinuity of `gutter_pct` is documented at the call site (I3), defanged
   because misfiring candidates are now disposed.

**Non-goals:**

- **Residue R4.** This restores its clean numeric `Total` column; R4 remains blocked on the row
  de-fusion (`logical_rows` absorbs subtotal lines into data rows).
- **R3** (nested-subset vote, ruleless path) and **R16** (unruled split numbers) — untouched.
- Fixing the counter-example's *classification* beyond parity: it must compile exactly as `main`
  compiles it today.

**Success criteria:**

1. **The red test:** the committed aligned-internal-space fixture (3 ruled columns, Courier 9pt,
   values `AB CDEFGH` / `01 JAN 2026` / `12 500`) compiles `RECORD_TABLE`, 18 cells, **score 1.0**
   through `compile_tables` — byte-identical to `main`. It currently **crashes** attempt 1's branch.
2. GrainCorp: **17 header labels** with `Date Loading Completed`, `Commodity`, `Total` separate.
   **The header-label count is the discriminating criterion** — attempt 1 proved cells/score are
   not (509 / 0.9496 held identically at the broken 15-column and correct 17-column states). Cells
   509 and score 0.9496 are recorded as secondary confirmation only.
3. **The membrane backstop:** a hierarchical region that fails `region_tiles` escalates **in-band**
   with the band's ASCII; `compile_tables` never raises on it. Pinned by a test that feeds a
   non-tiling region through the plain hierarchical path.
4. **Every refusal path degrades to `main`'s measured behavior** — no candidates, no header/body
   split, none confirmed, membrane refusal: each yields exactly what `main` produces today.
5. **No regression:** full suite green (609 at Loop F close, plus attempt 1's 10 carried tests, plus
   this loop's); both shipped ruled fixtures unchanged; borderless fixtures never enter the path.
6. **Gate:** the confirmation is an evidence-positive SPARQL derivation with **no numeric literal**
   (all bounds come from the evidence graph); candidate generation inherits `gutter_pct = 0.98` /
   `min_gutter_bins = 3` from `infer_leaf_grid`, stated as inherited constants, not claimed away.
   No new tolerance anywhere. `Band.rules` never contains a synthesised `Rule`.

---

## 2. Measurement (2026-07-30, on attempt 1's branch)

**Finding 1 — the header discriminates perfectly, at char level.** For each derived boundary, count
header-region char ink strictly left / strictly right within its author interval:

| document | derived boundary | header ink L / R | verdict |
| --- | --- | --- | --- |
| aligned fixture | 73.5 in [50, 170] | 2 / **0** | REJECT — phantom (`ID` sits left of the split) |
| aligned fixture | 215.0 in [170, 290] | 4 / **0** | REJECT — phantom (`Date` likewise) |
| GrainCorp | 753.7 in [715.2, 829.9] | 9 / 14 | **CONFIRM** (`Completed` \| `Commodity`) |
| GrainCorp | 798.7 in [715.2, 829.9] | 18 / 5 | **CONFIRM** (`Commodity` \| `Total`) |
| contaminated probe | 52.1 in [15.6, 58.2] | 9 / 0 | REJECT — a spurious candidate (probe filter had leaked the page-bottom disclaimer line into the chars) is *also* correctly rejected |

The counter-example's phantom columns have no header ink because the author did not label them —
which is the same fact `tab:CoverageShape` enforced by crashing. Confirmation is CoverageShape's
evidence, consulted eagerly.

**Finding 2 — confirmation must read CHARS, not Words.** GrainCorp's leaf header is extracted as
the single word-blob `CompletedCommodityTotal` (x 716.3–818.4), which **straddles** 753.7 at word
level and would self-reject the target. Its chars do not straddle — the gutter lies between glyphs
(`Completed` ends ≈751, `Commodity` begins 764.2). Word-level kills the target; char-level
discriminates. The evidence graph therefore carries char ink extents.

**Finding 3 — the space-glyph discriminator is REFUTED** (the post-mortem's other named direction):
**51 space glyphs** overlap GrainCorp's genuine column run `[789.2, 808.2]` (the padding spaces
Loop F characterised), so "a run containing space glyphs is a word gap, not a column gap" would
reject a real column boundary. Recorded so it is not re-derived.

**Finding 4 — single-row tables fix themselves.** Confirmation requires a header region, which
requires a `header_body_split`. A single-row band has neither, so no candidate can ever be
confirmed and the author grid stands — closing attempt 1's I4 (single-row over-split to 6 columns
at confidence 1.0) structurally rather than by a guard.

**Finding 5 (carried from the attempt 1 post-mortem, all reviewer-verified):** the candidates were
never the problem — `refine_rule_columns` is additive under every adversarial input tried, and its
GrainCorp candidates are exactly right. The true trailing-run rejector is the **no-flush** behavior
(a run still open at interval end is never emitted), *not* the interior condition as attempt 1's
docstring claimed. Cells/score are non-discriminating for this change. `gutter_pct = 0.98` with
per-interval `N` is discontinuous at `N = 50` (blank = inked in ≤ ⌊0.02·N⌋ rows: zero rows below 50,
one row at 50+) — acceptable for *candidates*, whose misfires confirmation now disposes.

---

## 3. Components

### 3.1 Cherry-picked from attempt 1 (base, unchanged)

`geometry.refine_rule_columns` + its 7 tests; `Band.column_xs` + `_rule_boundaries` preference + its
2 tests; the `recover_leaf_grid` sub-band carry + its mutation-verified test. Attempt 1's
`compile.py` wiring is **replaced** by §3.3.

### 3.2 The confirmation AXIOM (new)

- **Owned vocabulary** (`vocab/ontology/tab.ttl`; grep before adding — the B2c lesson):
  `tab:HeaderGlyph` (transient char-ink evidence: `tab:glyphX0`, `tab:glyphX1`) and
  `tab:CandidateBoundary` (`tab:boundaryX`, `tab:intervalLo`, `tab:intervalHi`), plus the derived
  marker `tab:confirmedBoundary`. All transient pre-holon evidence, never asserted into a holon —
  same posture as Loop B's `tab:HeaderCell`.
- **`vocab/queries/confirm-boundary.rq`** — one `SELECT`: a candidate is confirmed iff
  `EXISTS` a header glyph with `glyphX1 <= boundaryX` inside `[intervalLo, intervalHi]`, `EXISTS`
  one with `glyphX0 >= boundaryX` inside it, and `NOT EXISTS` one with
  `glyphX0 < boundaryX < glyphX1`. Open-world, evidence-positive, **no numeric literal** — every
  bound is data. The holon-scoped closure (`NOT EXISTS`) closes within the one band, per the gate.
- **Emitter + runner** — new thin module `src/iladub/etkl/boundary.py`, mirroring `headergraph.py`
  exactly (that module is Loop B's covering evidence and keeps its single responsibility): emit the
  fresh per-band `Graph()`, run the query, return the confirmed subset. PROCEDURAL engine glue only;
  the decision lives entirely in `confirm-boundary.rq`.

### 3.3 `compile.py` — band construction, extracted and rewired

Extract the ruled-band construction into a module-level helper (the **real seam** the C2 finding
demands), with the flow: author-bucketed lines → candidates → *(if any)* provisional grid +
`header_body_split` → *(if split)* confirm against the header-region chars → *(if confirmed)*
re-bucket with author+confirmed and set `column_xs`. Every refusal exits to the author-bucketed
band. `sub_rules` passes through untouched — no `Rule` is ever synthesised, and the seam makes that
testable against production code.

### 3.4 The membrane backstop

The plain hierarchical branch currently does `n = assert_hier_region(graph, …)` directly. It
becomes: assert into a **scratch** graph; `region_tiles(scratch)` → merge and count, else
`escalate_region(…, "REGION_TILING_FAILED", …)` in-band with the ASCII view. This mirrors the
row-hier and matrix branches exactly and removes the last direct-assert region path. (Attempt 1's
crash — `AssertionError` at final `_validate` — becomes an honest escalation even if every other
layer fails.)

---

## 4. Testing

- **The red fixture (committed, synthetic):** `fixtures.aligned_space_table_pdf` — the
  counter-example. End-to-end: `RECORD_TABLE`, 18 cells, score 1.0, and **identical verdicts on
  `main`'s code path** (parity, not merely non-crash).
- **Confirmation unit tests:** both-sided ink → confirmed; one-sided → rejected; straddling glyph →
  rejected; empty header region → nothing confirmed; multiple candidates independently judged.
- **Gate test:** `confirm-boundary.rq` carries no numeric literal (extends the existing
  `test_transform_gate.py` coverage of `vocab/queries/*.rq` automatically).
- **Membrane backstop test:** a hand-built non-tiling hierarchical region through the plain path →
  escalated in-band, `compile_tables` returns normally, the region's reason names the tiling
  refusal.
- **Seam test (C2 redress):** the extracted band builder, called directly, never emits a `Rule` not
  drawn by the author — and the test fails if `compile.py` is mutated to synthesise one.
- **Carried from attempt 1:** all 10 tests, including the sub-band-carry mutation guard.
- **Regression:** both ruled fixtures byte-identical; borderless untouched; full suite green.
- **Real-world (local, uncommitted):** GrainCorp **17 header labels** (primary criterion), cells
  509 / score 0.9496 (secondary), residues R14/R10 behavior unchanged.

---

## 5. Neurosymbolic gate & discipline

- **The decision is an AXIOM.** "Which candidate boundaries are columns" is a recovery decision
  that grows the graph — the gate's default class — realized as an evidence-positive SPARQL
  derivation over a per-band evidence graph. The band is the closure boundary.
- **Propose → dispose, twice.** Candidates are proposed by geometry, disposed by the header
  derivation; regions are proposed by assembly, disposed by the SHACL membrane. Nothing is asserted
  at confidence 1.0 that the evidence has not confirmed, and refusal always degrades to `main`'s
  behavior, never to a crash.
- **No new constant.** The derivation has no numeric literal. Candidate generation inherits
  `gutter_pct` / `min_gutter_bins` (stated, documented at the call site with the `N = 50`
  discontinuity). No width threshold exists anywhere — the counter-example is defeated by evidence,
  not magnitude.
- **Provenance honest:** `Band.rules` = author's marks only; `column_xs` = derived; the seam test
  enforces it against production code.
- **Corrected claims carried forward:** the docstring's trailing-run attribution is fixed to the
  measured mechanism (no-flush), and the spec's discriminating criterion is the header-label count,
  not cells/score.

---

## 6. Residues

- **R13 / R1** — closed by this loop for ruled documents whose missing boundaries the header
  labels. Still open in the narrower form: a genuinely unlabeled sub-column (header ink on one side
  only, yet truly two columns) is indistinguishable from the counter-example by construction and
  stays merged — honest, since asserting it would be exactly attempt 1's defect. No measured
  document exhibits it.
- **R4** — regains its clean numeric `Total` column; still blocked on row de-fusion.
- **New:** none anticipated; the membrane backstop *removes* a standing hazard rather than adding
  one.
