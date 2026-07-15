# ET(K)L Recovery/Perception Layer — Neurosymbolic Audit

**Date:** 2026-07-14
**Purpose:** Read-only audit of the shipped table-compiler recovery/perception layer against the
project thesis — *reading a document is a neurosymbolic process, not a procedural one; formal
semantic code prevails over Python (CLAUDE.md §8); fill semantic gaps rather than hand-code around
them.* This is the evidence base for the neurosymbolic redesign (loop one: the declarative
transform substrate; loop two: the visual-encoding perception grammar).

**Classification legend:**
- **AXIOM** — should be declarative: a SHACL rule / SPARQL `SELECT`-`CONSTRUCT` over an RDF evidence graph.
- **NEURAL** — genuinely perceptual, underdetermined symbolically → GenAI-via-BAML *proposes* under
  assert/propose/promote + a semantic oracle (the A2.1 pattern).
- **PYTHON-OK** — irreducibly procedural: raw extraction or exact arithmetic.

---

## A. `grid.py` + `bands.py` — raw column/band perception

- **A1. `grid.infer_leaf_grid`** — column boundaries from a whitespace occupancy profile. Tuned
  constants `gutter_pct=0.98`, `min_gutter_bins=3`, `sample_target=4`, plus an explicit "tuning
  guidance" docstring (raise/lower the constant per document). **NEURAL** (where are the columns is
  perceptual). *Wall:* the per-document tuning guidance itself; a merged header collapses the grid
  (7-col pivot read as 5). *Reuse:* output → `oa:` selectors / `doco:TableColumn`; raw
  `extract_words` is PYTHON-OK.
- **A2. `bands.detect_bands`** — vertical segmentation; split where gap `> gap_factor*median_gap`,
  `gap_factor=1.8`. **NEURAL** (layout region perception; relative-median is a defensible near-oracle).
  *Wall:* `1.8×` magic constant; 1-D only → forces `segment.py`. *Reuse:* DoCO/Deo.

## B. `regions.py` — kind classification

- **B1. `classify`** — RECORD only if `len(header.words)==grid.ncols` with per-column containment.
  Routing = **AXIOM** ("a flat record has a 1:1 single-word header tiling"); the multi-word-header
  escape is **NEURAL** (B1.2 wrap-vs-two-cells; the docstring concedes a multi-word label is
  "geometrically indistinguishable from two columns whose gutter collapsed").

## C. `headers.py` — header/body split + header-tree span recovery

- **C1. `header_body_split`** — first line after which ≥1 leaf column is all-numeric to band end.
  **AXIOM** (SPARQL SELECT over per-cell datatype facts). *Wall:* "numeric-homogeneity as the
  operative proxy" acknowledged narrower than the "type-homogeneous" concept.
- **C2. `_covers_for_cell`** — center-of-mass span symmetrization (which leaf cols a merged header
  spans). **NEURAL.** *Wall:* "assumes Merge & Center"; "a single word straddling one gutter may be
  over-spanned"; left/right-aligned merge out of scope; a fixture-shaped anti-regression comment
  ("Do NOT add a `cc != lc` guard: it would block the pivot's 'Prior Visit' header"). *Reuse:* BAML
  proposes span, `NoOverlapShape`/`CoverageShape` dispose.
- **C3. `_centered_run` + `repair_coverage`** — B1.1 centering tie-band (`0.25*_median_pitch`), pick
  widest-then-closest run. **NEURAL** — *the flagship documented wall*: the narrow-flank
  over-absorption silent-wrong deferred to B1.2 (`2026-07-13-b1-1-narrow-flank-...deferred.md`); the
  tie-band exists *because geometry cannot decide* — the signal to hand it to perception + oracle.
- **C4. `merge_tiling_ok`** — centering consistency oracle (span midpoint within `0.5*pitch` of ink
  center + overlap rejection). **AXIOM** — a verification backstop; should be a SHACL centering /
  no-overlap invariant (`sh:sparql`); the overlap half already exists as `NoOverlapShape`.
- **C5. `infer_header_tree` wrap-continuation** — is a tight sub-line ("(SI)") a wrapped continuation
  or a distinct level; threshold `0.9×lead`, reasoned in fixture-specific point magnitudes
  (14/12.6/13/18/16.2 pt). **NEURAL** (B1.2 text un-wrap). *Wall:* strongest "tuned to the document
  in front of us" smell in the header code.

## D. `matrix.py` — cross-tab column tree

- **D1. `infer_column_tree_by_proximity`** — Voronoi nearest-center column→label assignment.
  **NEURAL** (same "which columns does X span" family; Voronoi is a geometric proxy). *Wall:*
  mis-resolves off-center / unequal-width groups. *Reuse:* BAML span proposal + `col_tree_tiles`
  SHACL oracle.
- **D2. `is_matrix_candidate`/`classify_matrix`** — routing gates (`ncols>=3`, `split>=2`,
  `stub_data_split`). **AXIOM** (thin declarative routing; low-risk integer gates).
- **D3. `col_tree_tiles`/`matrix_tiles`** — partition backstop. **AXIOM** — a Python reimplementation
  of the Coverage/NoOverlap/Refinement SHACL invariants that already exist; **delete** in favor of
  the shapes.

## E. `rowheaders.py` — row-header tree (vertical mirror)

- **E1. `stub_data_split`** — leading text-stub column count. **AXIOM** (type-boundary, same as C1).
- **E2. `infer_row_header_tree`** — blank-below (forward-fill) row-span. **AXIOM at core** (a
  decidable windowing rule → SPARQL CONSTRUCT) **/ NEURAL at the margin** (is a blank a
  ditto-continuation or a genuinely empty cell — a reading convention; ambiguous blanks escalate).
- **E3. `looks_row_grouped`** — routing (coarse stub under-populated, rightmost full). **AXIOM**.
- **E4. `row_tree_tiles`** — **AXIOM** (duplicates `RefinementShape`).

## F. `orientation.py` — transpose detection

- **F1. `looks_transposed`/`transpose_is_coherent`** — type-orientation oracle (`typed_row and not
  typed_col`). **AXIOM** — literally the A1.4 TRANSPOSE axiom; the module calls itself "iladub's
  first *semantic* oracle" yet is hand-coded Python. *Reuse:* SPARQL 1.1 aggregate/`GROUP BY` over
  datatypes; the `is_numeric` typing underneath is PYTHON-OK.

## G. `segment.py` — multi-table splitting

- **G1. `_widest_gutter_cut`** — gutter-dominance side-by-side detection (`widest >= 2.0*second`,
  `_GUTTER_DOMINANCE=2.0`). **NEURAL** (figure/ground segmentation). *Wall:* `2.0` justified
  empirically ("ratio 1.05–1.59 in probes"). *Reuse:* BAML proposes cut; `find_table_gutter`'s
  re-classification is the disposing oracle — **already a near-A2.1 pattern (a bright spot)**.
- **G2. `find_repeated_header`** — exact token-tuple repeat. **PYTHON-OK** (exact equality).
- **G3. `has_own_stub`** — majority-text row identity (`>0.5`). **AXIOM** (majority-typing predicate)
  with a `0.5` cutoff.
- **G4. `find_table_gutter`/`is_multi_table_ambiguous`** — certify-by-reclassify. **AXIOM/PYTHON-OK**
  (legitimate oracle composition; the good propose-cut / certify / else-escalate shape).

## H. `denormalization.py` — pivot & aggregation DETECTION

- **H1. `_axis_dimensions`/`recover_dimensions`** — spanning-parent-names-below rule. **AXIOM** —
  verbatim the A1.2 UNPIVOT axiom; should be a SHACL rule / SPARQL SELECT, not set-algebra Python.
  *Reuse:* `qb:`/CSVW; `tab:PivotedDimension` vocab already exists — only the *recovery* is procedural.
- **H2. `detect_aggregations`+`verify_group`** — exact-arithmetic subtotal detection (`_EXACT_FUNCS`,
  `_TOL=1e-6`, iterated greedy strip, `<2` guards). **PYTHON-OK arithmetic / AXIOM search** — the
  exact equality is irreducible (or SPARQL 1.1 aggregate `HAVING`); the greedy search order encodes a
  declarable "row = SUM over sibling group" rule. *Reuse:* SPARQL aggregates + FnO IRIs (design §3).
- **H3. `_operand_exclusions`** — level-0 stubs barred as operands. **AXIOM** (role-assignment over
  header depth).
- **H4. `emit_base_facts`** — 3NF emission via nested rdflib `g.add` loops. **AXIOM (missed
  CONSTRUCT)** — the design's "flat base = `CONSTRUCT`-derived `holon:ProjectionGraph`."

## I. `reshape.py` — recipe recovery + emission (Loop A1/A2)

- **I1. `recover_recipe`/`recover_base`/`_named_pivot_recipe_and_base`** — recipe construction +
  value-set measure detection. **Mixed** — the `Recipe` is the correct declarative artifact
  (`tab:ReshapeRecipe` already exists — the healthiest part of the layer); its *recovery* is
  AXIOM-declarable Python; the ragged-rectangularity guard is PYTHON-OK.
- **I2. `emit_base_projection`** — **AXIOM (missed CONSTRUCT)** (same as H4; derived
  `holon:ProjectionGraph`, design §7).
- **I3. `certify`/`certify_with_proposals`** — A2.1 propose→oracle→promote. **NEURAL, done correctly
  — the reference pattern** the rest of the layer should converge toward. (Its oracle `round_trip` is
  itself procedural — see J1.)

## J. `oracle.py` — the round-trip oracle

- **J1. `replay`** — executes the reshape recipe in **Python** (`_FUNCS`, `_fmt` float-formatting,
  `_close`/`_TOL`). **AXIOM — the single biggest missed-semantic opportunity.** The design (§2, §3,
  §5.2, §6) specifies the reshape as **SPARQL `CONSTRUCT` + SPARQL 1.1 aggregates at the holon
  boundary** emitting a `holon:ProjectionGraph`; what shipped is a hand-coded Python interpreter of
  the recipe. The recipe is declarative *data* but its **executor is procedural Python** — forward
  replay and reverse recovery are two Python codepaths kept in lockstep by hand (neo-legacy). *Wall:*
  `_fmt` is a fragile procedural reconstruction of source float formatting the exact-string compare
  depends on. *Split:* op execution = `CONSTRUCT`/aggregate AXIOM; the exact equality check
  (`_close`) is PYTHON-OK.

## K. `compile.py` — routing + scoring

- **K1. Routing cascade** — hand-ordered `if looks_transposed / elif looks_row_grouped / else matrix
  / else hierarchical`. **AXIOM** (declarative SHACL-driven classification; precedence is procedural).
- **K2. Cell-fits check** (`b[col]-0.5 <= w.x0 ... <= b[col+1]+0.5`) — **PYTHON-OK** (exact geometric
  containment; `0.5`pt slop).
- **K3. Score ratio** — **PYTHON-OK** (arithmetic bookkeeping).

---

# Synthesis

## Highest-value neurosymbolic reframes (ranked)

1. **Reshape *execution* → SPARQL `CONSTRUCT` + SPARQL 1.1 aggregates (AXIOM).** `oracle.replay` +
   `emit_base_facts`/`emit_base_projection` hand-code the grammar in Python with a paired hand-coded
   recovery. The design already specified `CONSTRUCT`-at-boundary; it was not built. Makes the recipe
   truly declarative (standard SPARQL interpreter, not a bespoke Python twin) and the base a derived
   `holon:ProjectionGraph`. **The single biggest missed-semantic opportunity.**
2. **All "which columns/rows does X span" decisions → NEURAL (BAML proposes, tiling-SHACL disposes).**
   `_covers_for_cell`, `_centered_run`/`repair_coverage` (B1.1 tie-band), `infer_column_tree_by_proximity`
   (Voronoi), the ditto margin of `infer_row_header_tree`. These carry every span tolerance and the
   only documented silent-wrong; they are the A2.1 pattern `certify_with_proposals` already shows.
3. **Raw boundary/segmentation perception → NEURAL, quarantine the tuned constants.**
   `grid.infer_leaf_grid` (`0.98`/`3`/`4` + tuning docstring), `bands.detect_bands` (`1.8`),
   `segment._widest_gutter_cut` (`2.0`). Every fixture-tuned constant lives here; keep
   certify-by-reclassify as the disposing oracle.
4. **Pivot/aggregation ROLE assignment → AXIOM (SHACL rules), arithmetic stays PYTHON-OK.**
   `_axis_dimensions`, `_operand_exclusions`, `orientation.looks_transposed`. Exact aggregate check
   stays PYTHON-OK / SPARQL `HAVING`.
5. **Kind routing + redundant tiling backstops → AXIOM.** `compile.py` cascade + `regions.classify`
   → declarative classification; `col_tree_tiles`/`matrix_tiles`/`row_tree_tiles` **delete** in favor
   of the SHACL invariants that already exist.

## Recurring patterns
- **"Which columns/rows does X span?" is always perceptual → NEURAL** — clusters all tuned
  tolerances and the only deferred silent-wrong.
- **"Is this an aggregate / what function?" is arithmetic → PYTHON-OK-but-declarable** (SPARQL
  aggregates + FnO; move the *search* into a rule).
- **"What is the type-boundary / role?" is declarative → AXIOM** (header/body, stub/data, transpose,
  dimension-name-vs-values, stub-vs-measure).
- **The op *execution* is a missed SPARQL-`CONSTRUCT` axiom** (reframe #1), dragging a fragile
  float-formatting oracle (`_fmt`) with it.
- **Bright spots to generalize:** `reshape.certify_with_proposals` (A2.1) and
  `segment.find_table_gutter` already embody propose→oracle→dispose. The redesign is largely
  *retrofitting the rest of the layer to these two shipped exemplars.*

## The single biggest missed-semantic opportunity
**`oracle.replay` (+ its emission twins) executes the report-authoring grammar in procedural Python
instead of the SPARQL `CONSTRUCT` + aggregates the design mandated.** The recipe is declarative *as
data* but has **no declarative interpreter** — a "pivot + SUM" is proven by a Python replay that must
mirror a Python recovery by hand, with correctness riding on `_fmt`'s float-rendering matching the
source. Making the recipe's executable body standard SPARQL (emitting a `CONSTRUCT`-derived
`holon:ProjectionGraph`) removes the twin-codepath neo-legacy, makes the transform upstream-portable
to HGA's CONSTRUCT-at-boundary pattern, and turns the recipe from declarative-looking data into an
actually-executable declarative artifact.

## Honest PYTHON-OK boundaries (do not over-semanticize)
pdfplumber word extraction; `is_numeric` typing; exact aggregate verification (`verify_group`,
`round_trip._close`, `_TOL=1e-6`); exact token-tuple header-repeat; geometric containment checks
(`_word_in_column`, the `±0.5`pt cell-fit); score arithmetic. These are raw extraction or decidable
exact arithmetic and are correctly procedural.
