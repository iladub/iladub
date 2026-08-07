# Harden the transposition oracles against multi-row headers — design

**Date:** 2026-08-07 · **Status:** approved (François, 2026-08-07) ·
**Closes:** R71 · **Unblocks:** slice B of the reading-as-differential-diagnosis
architecture (`2026-08-07-reading-decision-record-design.md` §7) ·
**Specimen:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf`, page 0 region 2 and
page 2 region 1

**Doc impact:** increment — one new term in the owned `tab:` namespace
(`tab:bodyStartsAt`), shipping with a conforming example and a negative test per
CLAUDE.md. No site page contradicted; a wiki note on the header/body boundary queues
for the next release.

## 1. The defect

`looks_transposed` fires on two stem bands that are not transposed at all. The
preceding loop measured why, and corrected its own first answer: the cause is not a
caption line but a **multi-row wrapped column header**.

Both oracles assume the header is exactly one physical line:

- `vocab/queries/looks-transposed.rq` filters `?r >= 1` and `?cr >= 1` — "body = row ≥ 1".
- `vocab/queries/transpose-coherent.rq` filters `?ac >= 1` / `?bc >= 1`, which are
  **column** bounds. It has **no row filter at all**, so it consumes every physical row
  including the header. It is the more polluted of the two.

`assign_cells` (`src/iladub/etkl/regions.py`) applies no header/body split, so on a band
whose header wraps across 3 or 4 lines every header row enters the grid as a body row,
seeding Text cells across all columns and destroying the column type-homogeneity whose
*absence* `looks_transposed` tests for.

The gate `classify` currently masks this: an `UNSUPPORTED_TABLE` band never reaches the
oracle. That masking is R71 — it is the only thing protecting 1,327 of stem's 2,152
asserted cells, and it is what blocks slice B.

## 2. The fix

Give both AXIOMs the body-start row instead of assuming it.

`header_body_split(band, grid)` (`src/iladub/etkl/headers.py:84`) already derives it
declaratively — it returns the first line at/after which ≥1 leaf column is
family-homogeneous non-Text. Measured on the two bands: **4** and **3**, agreeing exactly
with the preceding loop's ablation (strip lines 0–2 on p0 and line 3 becomes the header,
so the body starts at 4).

### 2.1 The term

`tab:bodyStartsAt` — `rdfs:domain tab:ClassifyBand ; rdfs:range xsd:integer`, in the owned
`tab:` namespace, alongside the existing `tab:lineCount` / `tab:gridColumnCount`.

### 2.2 The evidence

`celltype.grid_evidence(cells, ncols, body_starts_at=1)` emits a `tab:ClassifyBand` node
carrying the triple.

**The default is load-bearing.** `body_starts_at=1` reproduces today's behaviour exactly,
so the other three callers — `rowheaders`, `headers.header_body_split` itself, and the
`test_celltype` / `test_typing_equiv` / `test_invalid_split_refusal` suites — are unchanged
by construction rather than by inspection. Only the two orientation call sites pass a
different value.

Note `header_body_split` is itself a `grid_evidence` caller. It computes the split, so it
must never be *given* one; its query does not reference `tab:bodyStartsAt`, and the default
keeps that true.

### 2.3 The queries

- `looks-transposed.rq`: `?r >= 1` → `?r >= ?bodyStart`; `?cr >= 1` → `?cr >= ?bodyStart`.
- `transpose-coherent.rq`: gains a row bound it never had, `?r >= ?bodyStart`, alongside its
  existing column bounds.

Both bind `?bodyStart` from the evidence graph, so each `.rq` remains self-contained and
readable on its own — a reader learns where the body starts without consulting Python.
This stays AXIOM under CLAUDE.md §8: open-world, evidence-positive, no tuned constant. The
boundary is *derived* by an existing AXIOM, not thresholded.

### 2.4 The call sites

`orientation.looks_transposed` and `.transpose_is_coherent` compute
`header_body_split(region.band, region.grid)` — `ClassifiedRegion` already carries both —
and pass it through.

**`None` falls back to 1.** `header_body_split` returns `None` when no split exists (an
all-text table). Inventing a boundary there would be exactly the kind of guess §7 forbids;
falling back to today's assumption is the honest, behaviour-preserving default, and it is
the caller's decision rather than the AXIOM's.

## 3. The differential oracle must move in lockstep

`tests/etkl/test_celltype.py` holds Python reference implementations that prove the AXIOMs
correct — `test_orientation_matches_reference` and the randomized
`tests/etkl/test_derivation_equiv.py` compare query against reference:

- `_ref_looks_transposed` hardcodes `if r > 0`
- `_ref_transpose_coherent` applies no row filter — mirroring the query's own gap

Both take the same `body_starts_at` parameter. **If the queries change and the references
do not, the equivalence tests keep passing while no longer testing what they claim** — the
vacuous-gate failure this project has already shipped once and had to catch in review.

## 4. Why this cannot move a verdict today

Measured across the corpus: **every** band that reaches either oracle today has
`header_body_split == 1`.

| document | band reaching an oracle | split |
| --- | --- | --- |
| apple | p0 region4, p2 region6 | 1, 1 |
| capacity | p0 region3 | 1 |
| WHO | p0 region4, p1 region4 | 1, 1 |

With the split at 1 the hardened queries see exactly what they see now. The change is
therefore verdict-neutral **by measurement, not by hope** — and its whole effect falls on
bands that do not reach the oracle today, which is precisely what unblocks slice B.

## 5. What the guard does next

`tests/etkl/test_kind_gate_is_load_bearing.py` pins `looks_transposed is True` on both stem
bands as a **characterisation** of wrong-but-protective behaviour. Its docstring
pre-authorises this moment: *"When that hardening lands, `looks_transposed` will return
False here and these assertions SHOULD fail. Update them then — deliberately, with the
corpus re-measured."*

So the assertions flip to `is False`, and the docstring is rewritten from "wrong but
protective" to a record of what was fixed and when. The band's `kind` stays
`UNSUPPORTED_TABLE` and the header-shape assertions stay — those remain true, and they are
the evidence for slice B.

## 6. Success criteria

- Both stem bands: `looks_transposed` returns **False** after the change, measured.
- `transpose_is_coherent` on those bands: measured and recorded either way. The preceding
  loop's review measured it staying `False` with header rows removed; this loop must
  confirm that against the shipped change rather than inherit the claim.
- **Corpus scores byte-identical** — stem 0.9655 / 2152 cells / chain [3], CBH 0.9047,
  capacity 1.0000, apple 0.0606860158, WHO 0.5597.
- The fixtures still behave: `false_transposed_pdf` → `looks_transposed` True and
  `transpose_is_coherent` False (escalates `TRANSPOSED`); `transposed_table_pdf` → True and
  True (compiles). These are the R55 ordering specimens and must not regress.
- `test_orientation_matches_reference` and `test_derivation_equiv` still pass **with the
  references parameterised** — verified by inverting one reference and observing the
  equivalence test fail, so it is known to still bite.
- `tab:bodyStartsAt` ships with a conforming example and a negative test (CLAUDE.md).
- R71's row is deleted in the same change.

## 7. Risks, named

- **The differential oracle going vacuous** (§3) — the sharpest risk, and the reason §6
  requires the equivalence test be *observed failing* on an inverted reference.
- **`header_body_split` returning a wrong split** on some band, silently changing what an
  oracle sees. Bounded today by §4's measurement (every reachable band is at 1), but it
  becomes live the moment slice B carries candidates. Not closed here; slice B inherits it.
- **Cost:** each oracle call now runs one extra SPARQL query. Five bands today, so
  negligible — but it is per-band, so it scales with the corpus. Measure and record it.

## 8. Out of scope

- **Carrying topology candidates** — slice B. This loop removes its named blocker and
  nothing more. The `kind` gate stays exactly as it is.
- **R10** (`detect_bands` cutting one line too high). The preceding loop refuted it as the
  *cause* of this defect; it remains open on its own terms and is not touched here.

## 9. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate §8: the boundary is derived by an existing AXIOM and threaded as
  evidence. **No tuned constant** — a word-count or line-count threshold would be a defect.
- Source ownership: `tab:` is ours; `holon:` and the HGA namespaces are untouched.
- §7 *only emit what the source supports*: `None` from the split means fall back, never
  guess a boundary.
- Every vocabulary addition ships with a worked example that conforms and a negative test
  that must fail.
