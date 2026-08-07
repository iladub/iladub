# Harden the transposition oracles against multi-row headers — design

**Date:** 2026-08-07 · **Status:** closed 2026-08-07 — blocked, see §10 ·
**Closes:** R71 · **Unblocks:** slice B of the reading-as-differential-diagnosis
architecture (`2026-08-07-reading-decision-record-design.md` §7) ·
**Specimen:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf`, page 0 region 2 and
page 2 region 1

**Doc impact:** increment — one new term in the owned `tab:` namespace
(`tab:bodyStartsAt`), shipping with conforming-example tests and a fails-closed negative
test in `tests/etkl/test_body_start_evidence.py` / `tests/etkl/test_derivation_equiv.py`.
It carries no *worked example + SHACL negative test* pair, and correctly so: it is
transient pre-holon evidence vocabulary on a node no membrane shape targets — see §10
criterion 6, which measured that its siblings `tab:lineCount` / `tab:gridColumnCount`
carry no such pair either. No site page contradicted; a wiki note on the header/body
boundary queues for the next release.

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

> **This section describes the DESIGN, not the shipped code.** Task 3 was implemented, found to
> regress, and reverted — `orientation.py` carries no reference to `tab:bodyStartsAt` or
> `header_body_split`. See §10.

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

> **This section describes the DESIGN, not the shipped code.** Task 3 was reverted, so the guard
> was NOT updated: it still asserts `looks_transposed is True` on both stem bands and is
> byte-unchanged from before this loop. See §10.

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
`body_start ∈ (1, 2)`.

**Correction (final review, 2026-08-07): this branch is NOT inert, and an earlier draft of this
section wrongly said it was.** It ships **one acknowledged behavioural change**:

- **`transpose-coherent.rq` no longer reads the header row.** The pre-loop query had **no row
  filter at all** — only the column bounds `?ac >= 1` / `?bc >= 1` — so it consumed every physical
  row. The shipped query filters `?r >= ?bodyStart`, and at the default `?bodyStart = 1` that
  **excludes row 0**, a row the old query read. This is a real semantic change *at the default*,
  not a rewrite. Measured over 400 random grids at `body_start = 1`: **21 divergences, every one
  incoherent → coherent** (escalate → assert); over `body_start ∈ {1,2,3}` (1,200 cases), 127,
  all in the same direction and all of one shape — a header row carrying a type mismatch its body
  does not. **Kept on merits** (adjudicated by François): excluding the header from a *body*-
  coherence check is the intended semantics, and header pollution is half of what this loop
  exists to fix. Pinned by `test_transpose_coherent_diverges_from_old_only_on_the_header_row`
  (`tests/etkl/test_derivation_equiv.py`), which characterises the divergence rather than
  forbidding it, so an *unintended* divergence still fails.
- **`looks-transposed.rq` and the `tab:bodyStartsAt` plumbing ARE inert.** That query's old
  filters were the literal constants `?r >= 1` / `?cr >= 1`, so substituting `?bodyStart` is a
  genuine identity at the default; `test_looks_transposed_new_matches_old` asserts plain
  equality against the pre-loop form. And nothing calls `grid_evidence` with a non-default
  `body_starts_at` today, so the term itself moves nothing.

**Why the corpus scores do not reflect the change — a weaker guarantee than inertness.** No
corpus band reaches the transposed path at all (**R68**: apple/capacity/WHO all judge *upright*,
stem produces zero `transposed` judgements, CBH was never scanned), so `transpose_is_coherent` is
never consulted on corpus input. Score-neutrality here is therefore *unreachability*, not
behavioural equivalence. The two synthetic fixtures that do reach it
(`false_transposed_pdf`, `transposed_table_pdf`) still behave, per the controller run below.

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
   0.0606860158, WHO 0.5597). — **Not meaningfully tested.** Scores are unchanged, but *not*
   because nothing shipped that could move them: `transpose-coherent.rq` did ship a real
   behavioural change at the default (see the correction above). They are unchanged because **no
   corpus band reaches the transposed path at all** (R68), so the changed query is never
   consulted on corpus input. That is *unreachability*, a strictly weaker guarantee than the
   inertness this criterion was written to check — and it will stop holding the moment slice B
   routes a band down that path.
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
6. *`tab:bodyStartsAt` ships with a conforming example and a negative test.* — **Met; the
   criterion was miswritten, not unmet.** CLAUDE.md's obligation ("every vocabulary/shape ships
   with a worked example that conforms **and** a negative test that must fail") is a *membrane*
   obligation: a negative test fails by violating a SHACL shape. `tab:bodyStartsAt` has no
   membrane to violate. Verified by grep at final review:
   - its two siblings on the same transient node, `tab:lineCount` and `tab:gridColumnCount`
     (`vocab/ontology/tab.ttl:245-246`), carry **no** worked example and **no** negative test
     either — their only consumer is `vocab/queries/classify-kind.rq`;
   - **no shape in `vocab/shapes/` targets `tab:ClassifyBand`** (`grep -rn ClassifyBand
     vocab/shapes/` → no match; `tab-shapes.ttl`'s `sh:targetClass` list covers `LeafColumn`,
     `HeaderNode`, `EntryCell`, `LeafRow`, `PivotedDimension`, `AggregationCell`, `BaseFact`,
     `HeaderSourceCell`, `DetectedAggregationRow`, `SectionTotal`, `DerivedRowGroup`,
     `UnitMarker` — no `ClassifyBand`);
   - `vocab/examples/` **does not exist** in this repo (`vocab/` holds `ontology`, `queries`,
     `shapes`, `LICENSE`, `README.md`).

   Transient pre-holon evidence vocabulary has never carried that obligation in this codebase,
   because there is nothing for a negative test to violate. The right instrument for this class
   is a test that pins what the *query* does with the term, and that is what ships:
   `tests/etkl/test_body_start_evidence.py` (conforming: default = 1, explicit = 4, cells
   unchanged by the parameter, ontology declaration) plus
   `test_both_transposition_oracles_fail_closed_without_a_body_boundary`
   (`tests/etkl/test_derivation_equiv.py`) as the negative case — with the triple **absent**,
   both oracles must return False rather than assert from missing evidence.
7. *R71's row is deleted in the same change.* — **Unmet by design of this closing loop.**
   R71 is not closed; it is rewritten in place, keeping the number, to record the real
   blocker found here (docs/superpowers/residues.md).

Of the seven, **two are met and five are unmet** (criterion 6 was reclassified from "partial" to
met at final review — see its entry).

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

### The derive-by-absence defect — found in Task 2's review, FIXED at final review (2026-08-07)

Task 2's review found: with the `tab:bodyStartsAt` triple **absent** from an evidence graph,
`looks-transposed.rq` fails **closed** (returns False) but `transpose-coherent.rq` failed
**open** (returned True — asserting coherence from the absence of evidence, the
derive-by-absence shape CLAUDE.md §8 forbids). The mechanism: `?bd tab:bodyStartsAt ?bodyStart`
sat **inside** the `FILTER NOT EXISTS` group, so removing the triple made that group
unsatisfiable, `NOT EXISTS` held vacuously, and the ASK returned True.

**Fixed:** the binding is hoisted to the top of the `ASK {` group, above the `FILTER NOT EXISTS`.
The query now fails **closed** (returns False) when the triple is missing. Verified
behaviour-identical whenever the triple *is* present — 400 random grids × `body_start ∈ {1,2}`,
**0 mismatches** between the pre-hoist and post-hoist query text. The same hoist is **not**
available in `looks-transposed.rq`, whose body bound lives inside `SELECT` subqueries that an
outer binding cannot reach; that query already fails closed for the ordinary reason that its
`FILTER EXISTS` subquery finds nothing.

Pinned by `test_both_transposition_oracles_fail_closed_without_a_body_boundary`
(`tests/etkl/test_derivation_equiv.py`). Measured with the triple removed, on a 2×2 grid that
answers True while the boundary is present: `looks-transposed` False, `transpose-coherent`
**True before the hoist, False after**. Still unreachable in production —
`celltype.grid_evidence` always emits the triple — which is exactly why it needed a test rather
than a downstream fix. **Nothing remains deferred from this finding, so it takes no residue row.**
