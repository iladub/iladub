# Harden the transposition oracles against multi-row headers — design

**Date:** 2026-08-07 · **Status:** closed 2026-08-07 — blocked, see §10 ·
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
correct — `test_orientation_matches_reference` compares *both* oracles against their
Python references. `tests/etkl/test_derivation_equiv.py` is the randomized differential
battery, but it does **not** cover `transpose-coherent` at all: verified by grep, its
coverage is `header-body-split`, `looks-transposed` (old-vs-new query text, not a Python
reference), `stub-data-split`, `header-covers`, and `row-group-key-logical` only. So it is
`test_orientation_matches_reference` alone — not `test_derivation_equiv` — that must keep
biting on both oracles' references:

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

## 10. Close-out — blocked (2026-08-07)

**Task 1 and Task 2 shipped** (commits `7b8359e`, `9abcdc5`): `tab:bodyStartsAt` is declared
in `vocab/ontology/tab.ttl`; `celltype.grid_evidence(cells, ncols, body_starts_at=1)` emits
it; `looks-transposed.rq` and `transpose-coherent.rq` both read it, and the latter gained the
row bound it never had; the Python reference implementations in `tests/etkl/test_celltype.py`
were parameterised in lockstep and the equivalence battery extended to
`body_start ∈ (1, 2)`. The default of 1 reproduces prior behaviour exactly, so these two
tasks are **inert** in production: nothing calls `grid_evidence` with a non-default
`body_starts_at` today.

**Task 3 — wiring `orientation.looks_transposed`/`.transpose_is_coherent` to the derived
boundary — was implemented, found to regress, and reverted.** The working tree at close is
byte-identical to `9abcdc5`; `orientation.py` carries no reference to `tab:bodyStartsAt` or
`header_body_split`.

### The circularity

`header_body_split` locates the header by searching for the first row from which **at least
one column is family-homogeneous non-Text**. A transposed table is *defined* by having no
type-homogeneous column — that absence is exactly what `looks_transposed` and
`transpose_is_coherent` test for. Feeding the first AXIOM's output into the second conflates
two different questions ("where does the header end column-wise" vs. "is this table
transposed"). Measured directly on the two transposition fixtures (not the corpus — see the
§7 post-mortem below):

| fixture | `header_body_split` | consequence |
| --- | --- | --- |
| `false_transposed_pdf` (4 lines) | **3** | body collapses to the single last row; `looks_transposed` returns False; the compile pipeline never reaches `transpose_is_coherent`; the region compiles as an ordinary 9-cell `RECORD_TABLE` instead of escalating `TRANSPOSED` — a wrong assertion replacing a correct escalation |
| `transposed_table_pdf` (3 lines) | **None** | no column is ever homogeneous — the transposition signature itself; the caller's None→1 fallback leaves this fixture unaffected |

On the two stem bands the wiring worked exactly as designed: `header_body_split` returned 4
and 3 respectively, `looks_transposed` flipped True→False on both, and
`transpose_is_coherent` measured False on both, unchanged. **The blocker is the fixtures, not
the stem specimens** — the same derivation that correctly separates the stem bands' wrapped
headers from their bodies also, on `false_transposed_pdf`, finds a "header" that consumes
everything but the row the transposition signature depends on.

### Controller verification at the shipped state (commit `9abcdc5`)

```
pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py tests/etkl/test_kind_gate_is_load_bearing.py tests/etkl/test_closing_slice.py tests/etkl/test_transposed_chain.py -q
→ 46 passed in 301s
```

Tasks 1–2 inert, the guard still pins the old behaviour (`looks_transposed is True` on both
stem bands) because nothing is wired to the new evidence.

### §6 criteria, measured against the shipped state — most unmet

1. *Both stem bands: `looks_transposed` returns False after the change, measured.* —
   **Unmet.** The wiring that would make this true was reverted; `looks_transposed` still
   returns True on both stem bands in the shipped code (the guard in
   `tests/etkl/test_kind_gate_is_load_bearing.py` still asserts `is True` and is
   byte-unchanged from before this loop).
2. *`transpose_is_coherent` on those bands: measured and recorded either way, confirmed
   against the shipped change.* — **Unmet as stated.** It was measured during Task 3's
   uncommitted work (False on both, unchanged) but that work was reverted, so there is no
   shipped change to confirm it against.
3. *Corpus scores byte-identical* (stem 0.9655/2152/[3], CBH 0.9047, capacity 1.0000, apple
   0.0606860158, WHO 0.5597). — **Not meaningfully tested.** Scores are trivially unchanged
   because nothing shipped that could move them, not because the hardening was verified
   neutral under load.
4. *The fixtures still behave* (`false_transposed_pdf` → True/False escalating `TRANSPOSED`;
   `transposed_table_pdf` → True/True compiling). — **Unmet in substance.** In the shipped
   (unwired) code both fixtures still behave, again trivially, because nothing changed. But
   the criterion's actual purpose — verify the fixtures survive the hardening — was tested
   with the hardening active in Task 3, and `false_transposed_pdf` failed it (see the table
   above: it stopped escalating `TRANSPOSED` and compiled as `RECORD_TABLE` instead).
5. *`test_orientation_matches_reference` and `test_derivation_equiv` still pass with the
   references parameterised, verified by inverting one reference and observing the
   equivalence test fail.* — **Met.** Shipped in Task 2: `_ref_looks_transposed` and
   `_ref_transpose_coherent` both take `body_starts_at`, and the differential-oracle-vacuous
   check was run and observed failing before being restored (per the SDD ledger). Note per
   the §3 correction above: `test_derivation_equiv` does not exercise
   `transpose-coherent`, so it is `test_orientation_matches_reference` that carries this for
   both oracles.
6. *`tab:bodyStartsAt` ships with a conforming example and a negative test.* — **Partially
   met.** `tests/etkl/test_body_start_evidence.py` ships conforming-example tests (default=1,
   explicit=4, ontology declaration) and Task 2's review separately pinned the
   fails-closed/fails-open asymmetry (see the note below). No dedicated negative test (one
   that must fail validation) for `tab:bodyStartsAt` itself was found in this pass.
7. *R71's row is deleted in the same change.* — **Unmet by design of this closing loop.**
   R71 is not closed; it is rewritten in place, keeping the number, to record the real
   blocker found here (docs/superpowers/residues.md).

Of the seven, **one is met, one is partial, and five are unmet.**

### Why §7's risk assessment failed

§7 named "`header_body_split` returning a wrong split on some band, silently changing what an
oracle sees" as a risk, and judged it "bounded today by §4's measurement (every reachable
band is at 1)." §4 measured only the **corpus** bands that reach an oracle today (apple,
capacity, WHO, stem) — it never measured the split on the two **fixtures**, which are
precisely the transposition specimens where the instrument misbehaves. The measurement
behind §7's bound was real, but its scope was corpus-only, and the risk section inherited
that scope without noticing it was narrower than the risk it was trying to bound. The
fixtures were listed as a §6 success criterion in the same spec, so the gap was between two
sections of the same document, not a missing test class.

### Note for the next loop — an unpinned precondition

Task 2's review found: with the `tab:bodyStartsAt` triple **absent** from an evidence graph,
`looks-transposed.rq` fails **closed** (returns False) but `transpose-coherent.rq` fails
**open** (returns True — asserting coherence from the absence of evidence, the
derive-by-absence shape CLAUDE.md §8 forbids). This is unreachable today because
`celltype.grid_evidence` always emits the triple, and both production call sites go through
it — but nothing pins that guarantee. `tests/etkl/test_celltype.py`'s
`test_the_two_oracles_disagree_on_an_absent_body_boundary` (added, then reverted with the
rest of Task 3) measured this directly; it is not in the shipped code. Whoever picks up R71
next should decide whether to re-add that guard independent of whichever fix they pursue.
