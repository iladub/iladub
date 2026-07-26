# Robust header/body split — modal column type + missing-value cells (Loop A)

- **Date:** 2026-07-26
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). First loop of the GrainCorp real-document capability push.
- **Context:** iladub escalates the real-world **GrainCorp Shipping Stem** report (`MERGE_AMBIGUOUS`, 0 cells) — a document iladub is *built* for. Systematic-debugging traced the root cause to `vocab/queries/header-body-split.rq`: it defines the header/body boundary as the earliest row from which some non-Text leaf column is type-homogeneous **to the end of the band**, using the column's **bottom-cell** datatype as the reference. On real reports this returns `split=48` (should be `4`): (a) anomalous total/footer bottom rows corrupt the per-column reference type, and (b) missing-value **placeholder cells** (the literal `"(blank)"`) are typed `Text`, so they flip columns' types and count as mismatches deep in the body. This loop fixes the split derivation. **Evidence-driven, one gap per loop:** after this, GrainCorp will still escalate — on the *header-tree/caption* gap, which defines Loop B.

---

## 1. Purpose and scope

Make the header/body split derivation robust to the two real-world features that break it: **anomalous bottom rows** (totals/footers) and **missing-value placeholder cells**. Both fixes stay AXIOM (declarative aggregations over the existing typed-cell evidence graph), with no tuned constant.

**In scope:**
- `celltype`: recognize genuinely-missing cells as a new `tab:Blank` datatype (empty string, the self-declaring `"(blank)"`, a lone `"-"`) — not `Text`.
- `header-body-split.rq` v2: reference type = each column's **modal (dominant) non-`Blank` datatype** (not bottom-cell); `Blank` cells are wildcards; `split = MIN` over data columns of the first modal-type-consistent row.
- Update the differential-oracle reference (`test_derivation_equiv`) to the modal/blank definition.
- Declare `tab:Blank` in `tab.ttl`.
- A committed synthetic regression fixture reproducing the failure mode; the GrainCorp PDF as a local (uncommitted) real-world confirmation.

**Non-goals (later loops — the split fix re-measures and exposes them):**
- The leaked **title/date caption line** (`"Friday, 24 July 2026"`) inside the table band (Loop B).
- **Wrapped multi-line flat header** recovery (labels wrapped across lines, not merged parents) (Loop B/C).
- **Row-grouping with suppressed keys + interleaved subtotals** (Loop C+).
- Making GrainCorp *fully compile* — this loop only corrects the split; GrainCorp is expected to still escalate on the header tree afterward.

**Success criteria:**
1. `header_body_split` on a synthetic fixture with placeholder cells + an anomalous text bottom row + an interleaved subtotal returns the **true data-start** row (fails on the current query, passes on v2).
2. On the real GrainCorp band (local spike), the split moves from **48 → 4** (documented; PDF not committed).
3. **No regression:** existing header-body-split unit tests, all other celltype-derived queries (stub-data-split, classify-kind, transpose), the synthetic fixtures' splits, the differential oracle, and the full suite stay green.
4. Both changes are AXIOM: no tuned constant, mode = argmax, the `Blank` marker set is minimal + self-documenting; all-text tables still return `None` (honest escalation preserved).
5. No third-party PDF committed; repo stays synthetic/domain-neutral.

---

## 2. Root cause (confirmed) and the fix

**Current derivation** (`header-body-split.rq`): per column, reference type `T` = the **bottom (max-row) cell's** datatype; a column contributes `s_col` = 1 + (last row whose cell type ≠ `T`) if its bottom type is non-Text; `split = MIN(s_col)`.

**Why it returns 48 on GrainCorp** (both measured):
- **Bottom-cell reference:** the clean Date columns (ETA/ETD of ship) have a total/footer row at the bottom whose cell is Text/off-type, so `T` becomes Text → the column is excluded, or its last-mismatch is deep. The two genuinely-clean date columns never get to contribute `s_col=4`.
- **Placeholder pollution:** empty cells are written as the literal `"(blank)"` → typed `Text` → scattered through date/numeric columns, they (a) flip a column's mode/bottom to Text and (b) count as mismatches at deep rows, pushing `s_col` to ~48.

**The fix (verified → split 4):**
- Reference type = each column's **modal (dominant) datatype over non-`Blank` cells** (`argmax` of per-type counts). Robust to a single anomalous bottom row.
- `Blank` cells are **wildcards** — never a mismatch, excluded from the mode. Missing values stop polluting the type analysis.
- Keep the `MIN`-over-data-columns structure: the boundary is the earliest row from which the first clean data column becomes modal-type-consistent. On GrainCorp the two clean Date columns yield `s_col=4` → `MIN=4`.

---

## 3. Components

### 3.1 `src/iladub/etkl/celltype.py` + `vocab/ontology/tab.ttl`
- `_cell_datatype(t)` returns `TAB.Blank` when the cell is missing: `t` is empty/whitespace, or its stripped form equals `"(blank)"` (case-insensitive) or is exactly `"-"`. Otherwise unchanged (Numeric → Date → Currency → Text). The marker set is deliberately minimal and self-documenting; ambiguous tokens (`"0"`, `"N/A"`, `"-5"`, ranges) are **not** treated as Blank.
- `vocab/ontology/tab.ttl`: declare `tab:Blank a tab:CellDatatype` (owned vocab, alongside Numeric/Date/Currency/Text).

### 3.2 `vocab/queries/header-body-split.rq` (v2, AXIOM)
Rewrite the aggregation:
- Per column, compute the **modal non-`Blank` datatype** `D` (group by column+datatype over non-`Blank` cells, take the max-count datatype — a groupwise-argmax, the pattern the file already uses).
- Qualify a column as a *data column* iff `D != tab:Text` and it has ≥1 non-`Blank` body cell.
- `s_col` = 1 + MAX(row of a non-`Blank` cell whose datatype ≠ `D`), or 1 if the column is homogeneous in `D`. `Blank` cells are excluded from this MAX (wildcards).
- `SELECT (MIN(?s_col) AS ?split)` over qualifying columns. Returns unbound/`None` when no column qualifies (all-text table → honest escalation, unchanged).
- The load-bearing comment block is rewritten from the bottom-type/pure-to-end explanation to the modal/blank-wildcard semantics, keeping the cell-bearing-row invariant note.

### 3.3 `tests/etkl/test_derivation_equiv.py`
Update the differential-oracle **reference implementation** from the bottom-type definition to the modal/blank definition, so the oracle certifies the corrected derivation. The randomized new-vs-reference equivalence check now pins v2.

---

## 4. Testing

- **Committed failing test (TDD), synthetic:** a new fixture (a small table graph or a generated PDF in `tests/etkl/fixtures` / `etkl_demo_data`) with: structured columns (a Date and a Numeric column), **`"(blank)"` placeholder cells** in those columns on some data rows, an **interleaved subtotal text row**, and an **anomalous text total/footer bottom row** that flips a column's bottom-cell type. Assert `header_body_split(band, grid)` returns the true header/body boundary. Verify it **fails against the pre-change query** and **passes after** v2.
- **`tab:Blank` unit test:** `_cell_datatype("(blank)") == TAB.Blank`, `_cell_datatype("") == TAB.Blank`, `_cell_datatype("-") == TAB.Blank`; and non-blanks unchanged (`"0"`, `"N/A"`, `"-5"`, a date, a number).
- **Real-world confirmation (local, not committed):** re-run the GrainCorp spike (`compile_tables` / `header_body_split`) and record split 48 → 4 in the implementer report. The PDF stays in the scratchpad (gitignored).
- **No regression:** run the full suite; confirm the existing header-body-split tests, `test_derivation_equiv`, and all celltype-derived queries (stub-data-split, classify-kind, orientation/transpose) still pass, and the synthetic `etkl_demo_data` fixtures compile with unchanged splits (they contain no `Blank` cells, so the addition is inert for them).

---

## 5. Neurosymbolic gate & discipline

- **AXIOM, not NEURAL:** the split stays a declarative type-transition derivation over the typed-cell evidence graph; the fix is a *better aggregation* (modal type + missing-value wildcard), not a perceptual judgment. NEURAL remains the fallback for genuinely ambiguous *merges* (`span_proposer`, unchanged) and all-text tables still escalate.
- **No tuned constant / no overfit:** mode = argmax (no threshold); the `Blank` marker set is minimal and self-documenting (empty / `"(blank)"` / lone `-`), justified as universal missing-value recognition (the same class as the shipped Date/Currency format recognition) — not a GrainCorp keyword hack. The fix is validated on a *synthetic* fixture and the differential oracle, not tuned to the GrainCorp bytes.
- **Source ownership:** `tab:Blank` is owned `tab:` vocab; no HGA/Fluree terms involved.

---

## 6. Relation to prior work and steering

- Direct outcome of the systematic-debugging investigation into the GrainCorp `MERGE_AMBIGUOUS` escalation.
- First of an evidence-driven sequence: fix the split → re-measure GrainCorp → the next exposed gap (caption line / wrapped header) defines Loop B.
- The parked `iladub-zero-etl-showcase` branch will later gain GrainCorp as a *win* example once the stacked gaps are closed (or keep it as an honest-floor example until then).

---

## 7. Open questions / later loops

1. **Loop B:** the leaked title/date caption line inside the table band + wrapped multi-line flat header recovery (the header tree that still fails after the split is fixed).
2. **Loop C:** row-grouping with suppressed keys + interleaved subtotals as first-class structure.
3. Whether `tab:Blank` should also inform stub/data split and record-feed (a missing cell is a null value, not a datum) — revisit if a later loop needs it; out of scope here.
