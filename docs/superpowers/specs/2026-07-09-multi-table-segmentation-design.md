# Loop 7 · multi-table page segmentation — close the fusion silent-wrongs

**Status:** design (approved 2026-07-09)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md) (next increment)
**Builds on:** all prior loops (the per-table classifiers/compilers are reused unchanged as the certifier).

## Why this exists — 1-D banding fuses distinct tables (two live silent-wrongs)

`detect_bands` splits a page **only by vertical gaps**. Probed on `main` today (2026-07-09):

| layout | bands | result |
|---|---|---|
| two tables, **clear vertical gap** | 2 | ✓ each compiled independently (own header inferred) |
| two tables **side-by-side** (horizontal) | 1 | ✗ **fused** into one wide `RecordTable` (`Analyte\|Value\|Item\|Qty`), score 1.00 |
| two tables **stacked, no gap** (repeated header) | 1 | ✗ **fused**; the second header row asserted as a data row, score 1.00 |

The two fusion cases are **silent-wrongs**: two unrelated tables asserted as one, confidently. Fusing beats
every other open gap in badness, so we close it. (Vertically-gapped multi-table already works — this loop adds
the two axes `detect_bands` is blind to.)

## §1 — Scope & closing target (decided 2026-07-09)

- **Ambition:** **split & compile** where a cut is *certified*, **escalate** where a multi-table signal is
  present but the cut cannot be cleanly certified.
- **Cases:** **both** horizontal (side-by-side) **and** vertical (stacked / repeated-header).
- **Closing proof:** a side-by-side fixture compiles to **two** `RecordTable`s (not one fused table); a
  stacked-repeated-header fixture compiles to **two** `RecordTable`s; **every existing single-table fixture
  still segments to exactly ONE region** (the hard regression constraint).

## §2 — The load-bearing idea: segmentation is a *proposal certified by the existing classifiers*

A splitter's cardinal sin is a **false positive** — splitting a legitimate single table. So a cut is never
taken on a geometric signal alone; it is *proposed* and then **certified by re-running the classifiers we
already trust** on each side. This reuses the whole ET(K)L oracle stack (`classify`, round-trip, SHACL) as
the arbiter, exactly like every prior loop, and makes "no existing single table is ever split" the provable
invariant.

**The false positive that shaped the discriminator (probed).** A **cross-tab** has a wide full-height gutter
between its column groups (`Q1 | Q2`). Splitting there yields two *valid-looking* `UNSUPPORTED_TABLE` halves —
a naive "both sides are tables" rule would wrongly split a single cross-tab in two. The tell: the cross-tab's
right half is **data-only** (its leftmost column `Rev/Cost/Unit` is a header over *numbers* — no row
identity), whereas a genuine side-by-side table's right half has **its own stub** (`Item` over
`Apple/Pear` — text row identifiers). So certification requires each side to be a **self-contained table with
its own row identity**, operationalized for v1 as **each side classifies `RECORD_TABLE`** (a flat table has a
regular header and an inherent leftmost label column). Probe result across all fixtures:

| region | split proposed at widest gutter → both sides | verdict |
|---|---|---|
| side-by-side records | `RECORD_TABLE` + `RECORD_TABLE` | **SPLIT** ✓ |
| cross-tab | `UNSUPPORTED` + `UNSUPPORTED` | keep 1 ✓ (not both-RECORD) |
| pivot / simple / all-text / row-grouped | one side `NON_TABLE` | keep 1 ✓ |

## §3 — Architecture: a recursive `segment` pass before `classify`

New module `src/iladub/etkl/segment.py`:

```
segment(band) -> list[Band]
```

Tries a vertical cut, then a horizontal cut; recurses on the pieces; bottoms out (returns `[band]`) when no
certified cut exists. `compile_tables` changes one line: it iterates
`[sub for band in detect_bands(...) for sub in segment(band)]` instead of the raw bands. Everything
downstream (`classify`, all makers) is unchanged — each certified sub-band is a clean single-table region.

- **Vertical proposer — `find_repeated_header(band) -> list[int]`:** body-row indices whose token tuple equals
  the header row's (row 0). Split the band's lines at each such index into stacks. **Zero false-positive**: a
  single table never repeats its exact header as a body row (probe-verified on simple/crosstab/pivot).
- **Horizontal proposer — `find_table_gutter(band) -> float | None`:** the x of the widest **full-height**
  whitespace gutter (blank on every row) between leaf-grid columns. Split words at that x into left/right
  sub-bands. Certify: **both** sides `classify` as `RECORD_TABLE` → accept; else reject (return `None`).
- **Certification & escalation:** a proposed cut is taken only when certified. When a horizontal gutter is a
  strong outlier **and exactly one** side certifies as a table while the other is a degenerate fragment (a
  boundary-ish but unclean signal), `segment` marks the band `MULTI_TABLE_AMBIGUOUS` so `compile_tables`
  escalates it in-band rather than fusing. (A cross-tab produces *neither* a repeated header *nor* a
  both-RECORD split *nor* a lone-valid-side signal → it is never touched → compiles as a cross-tab.)

Recursion makes composites work: a side-by-side pair where one side is itself stacked splits horizontally
first, then each side re-segments vertically.

## §4 — No-false-positive invariant (the regression that matters most)

`segment(band)` **must** return a single-element list for every existing single-table fixture. The proof
suite asserts `len(segment(band)) == 1` for: `simple_table`, `record_report`, `pivoted_table`,
`all_text_table`, `crosstab_table`, `row_grouped_table`, `transposed_table`. This is the invariant that makes
the loop safe; it is tested before any positive split test.

## §5 — Honest limits (documented, not swallowed)

- **Side-by-side of *non-record* tables** (two hierarchies / cross-tabs abreast) is **not** split in v1:
  its halves classify `UNSUPPORTED`, geometrically indistinguishable from a single cross-tab's internal
  gutter, so splitting would risk the cross-tab false-positive. Left as one region (a residual fusion,
  documented) until a stub-based right-side-has-own-row-identity check is added (a follow-up). v1 handles the
  common **record** side-by-side.
- **Stacked tables with *different* headers and no gap** need a column-schema-discontinuity detector (harder);
  v1 handles the repeated-**same**-header case. Different-header stacks in practice usually have a gap
  (already segmented by `detect_bands`).
- Segmentation is geometric/lexical (gutter width, header repetition), certified by the classifiers — no
  model calls, consistent with the whole compiler.

## §6 — Proof of closure (tests)

1. **`test_side_by_side_splits_to_two`** — a side-by-side-records fixture → `segment` returns 2 bands →
   `compile_tables` emits **2** `RecordTable`s (was 1 fused); the two headers are distinct.
2. **`test_stacked_repeated_header_splits`** — a stacked-repeated-header fixture → 2 bands → 2 `RecordTable`s;
   the repeated header is no longer a data row.
3. **`test_single_tables_never_split`** (the invariant) — `segment(band)` returns exactly one band for
   simple/record/pivoted/all-text/**crosstab**/row-grouped/transposed. The cross-tab guard is explicit.
4. **`test_find_repeated_header`** / **`test_find_table_gutter`** (unit) — the proposers fire on the
   multi-table fixtures and return empty/None on the single-table ones.
5. **`test_multi_table_ambiguous_escalates`** — a band with a boundary-ish gutter but only one certifiable
   side → escalates `MULTI_TABLE_AMBIGUOUS`, no fused assertion.
6. **`test_vertically_gapped_unaffected`** — the existing `record_and_pivot`-style two-gap page still yields
   its two regions (segmentation of each gapped band is a no-op).
7. **No regression** — full suite green; every prior fixture compiles exactly as before.

## §7 — Showcase (part of the loop)

Add **Part H** to `demo/etkl_1a_showcase.ipynb`: render a page holding **two side-by-side tables** (and,
below, a **stacked repeated-header** block) first (original document, always), then show `segment` split it
and `compile_tables` emit a table-holon **per** sub-table — with the "so what": the compiler no longer fuses
unrelated tables; it segments the page (horizontally *and* vertically) and compiles each, and it provably
never splits a single table (the cross-tab stays whole). Re-run to 0 errors.

## §8 — What's notable

This loop closes the compiler's worst residual failure — **fusing unrelated tables into one confident
assertion** — and does it without a new oracle: segmentation *proposes*, and the existing per-table
classifiers *certify*. The cross-tab false-positive (a single table that splits into two valid-looking halves)
is the mirror image of Loop 6's insight (two axes that compose into one table); recognizing it forced the
discriminator to be "each side is self-contained with its own row identity," not merely "each side is a
table." And the no-false-positive invariant — every existing single table segments to exactly one region — is
the kind of provable safety property the doctrine is built around.

## Module map

| File | Change |
|------|--------|
| `src/iladub/etkl/segment.py` (create) | `find_repeated_header`, `find_table_gutter`, `segment` (recursive) |
| `src/iladub/etkl/compile.py` (modify) | iterate `segment`-ed sub-bands; escalate `MULTI_TABLE_AMBIGUOUS` |
| `src/iladub/etkl/__init__.py` (modify) | export `segment` |
| `tests/etkl/fixtures.py` (modify) | `side_by_side_pdf`, `stacked_repeated_header_pdf`, `multi_table_ambiguous_pdf` |
| `demo/etkl_demo_data.py` (modify) | `multi_table_report_pdf` |
| `demo/etkl_1a_showcase.ipynb` (modify) | Part H |
| `tests/etkl/test_segment.py` (create), `tests/etkl/test_closing_slice.py` | the §6 proof suite |
