# Padding-space word segmentation (Loop F — residue R2)

- **Date:** 2026-07-29
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). **SHIPPED 2026-07-29:** 49 of GrainCorp's 488 cells
  repaired (`2 0,000` → `20,000`, `1 18,000` → `118,000`); no cell damaged. **Score unchanged at
  0.947 with 447 cells, as required.** Full suite 609 passed / 5 skipped. R2 closed for the ruled
  path; R16 opened for the unruled path. **New evidence for R4 recorded:** `logical_rows` also
  fuses each subtotal line into the preceding data row's cell (verified pre-existing, not caused
  by this loop), so R4 must separate rows before it can sum them. Fifth loop of the GrainCorp real-document push
  (A = header/body split PR #67; B = header→column reconciliation PR #68; C = header-region row
  roles PR #69; C.1 = grounding the row-role proposal PR #70; D = rules as leaf-grid authority PR #71).
- **Origin:** Residue **R2** — `2 0,000` should be `20,000`. Reached by re-sequencing: residue R4
  (row-grouping / subtotals) is blocked because its only sound detector is arithmetic, and there is
  no parseable measure to sum.

---

## 1. Purpose and scope

Stop emitting wrong values. 49 of GrainCorp's 488 cells currently carry text the source does not
contain — a contiguous `20,000` rendered as `2 0,000` — because `rule_aware_lines` joins **every**
glyph in a cell, including padding space glyphs that physically overlap the digits.

**In scope:**

- `geometry.rule_aware_lines` — build each cell's text from its **non-space** glyphs, inserting a
  space only where a space glyph exists **and** the two glyphs it sits between are actually
  separated.

**Non-goals (each a residue in `docs/superpowers/residues.md`):**

- **The unruled path.** pdfplumber's own `extract_words` splits `2` from `0,000` identically, so
  documents without vertical rules keep the defect. Fixing that means re-implementing word
  segmentation for every document — much larger, and no measured document needs it. New residue
  **R16**.
- **Splitting the measure column** (`Date Loading Completed | Commodity | Total`). Measured (§2
  Finding 3): those sub-columns have **no space glyphs between them at all**, so this is not a
  word-segmentation problem — it is **R1 ≡ R13**, rules coarser than the columns.
- **R4 itself.** This loop does not unblock it; see §6.

**Success criteria:**

1. `'2 0,000'` → `'20,000'`, `'1 18,000'` → `'118,000'`, and `'(blank)Chickpeas   2 0,000'` →
   `'(blank)Chickpeas 20,000'`.
2. Every genuine word space survives: `CARPE DIEM`, `Reference Number`, `10:00:00 AM`.
3. **49 of 488 GrainCorp cells change, and every change is a repair** — no cell is damaged.
4. **The score does NOT move.** It stays at **0.947** with **447** cells (measured, §2 Finding 4).
   This is a data-correctness loop, not a score loop; a changed score means something unintended.
5. **No regression:** the full suite (603 at Loop D close) stays green. `borderless_*` fixtures do
   not use this path at all.
6. **Gate:** no tuned constant, no tolerance, no magnitude comparison. Both halves of the rule are
   presence tests.

---

## 2. Measurement (2026-07-29)

**Finding 1 — the split is not in the source.** The characters of `20,000` are contiguous:

```
'2'(811.6–814.5) '0'(814.4–817.4) ','(817.3–818.8) '0' '0' '0'(824.5–827.5)
inter-glyph gaps: −0.08, −0.03, −0.04, −0.03, −0.08      → all touching
```

The split comes from padding space glyphs that **overlap** the digits — e.g. `' '` at 811.9–813.4
sits inside `'2'` at 811.6–814.5. `rule_aware_lines` (`geometry.py:179`) joins them in x-order:
`"".join(c.text for c in gl).strip()` → `'   2 0,000'` → `'2 0,000'`.

**Finding 2 — three disjoint gap regimes, so no threshold is needed.** Measured between
consecutive **non-space** glyphs:

| regime | gap (measured over ALL 4114 pairs on the page) | example |
| --- | --- | --- |
| intra-token (kerning) | −0.19 … **+0.30** | `2`→`0` inside `20,000`; the +0.30 cases are all `W`→letter |
| real word space | **1.15 … 2.04** | `E`→`D` in `CARPE DIEM` (1.39); `s`→`L` (1.15); `G`→`S` (2.04) |
| inter-column | 4.95 … 189.02 | `s`→`2` in the measure blob (22.81) |

**Correction (final review):** an earlier version of this table gave −0.08…+0.11 and 1.38–1.39.
Those came from sampling a handful of cells and are wrong by roughly 3× on one bound. The
*conclusion* survives — the regimes are still disjoint, with a margin of 0.30 vs 1.15 — and it was
never load-bearing, since the shipped rule uses no magnitude at all. But the numbers were stated as
measurements and were not.

`20,000` has **zero** positive gaps. Every real word space has a space glyph **and** a positive gap.
Padding spaces have a glyph but a **negative** gap. So the rule needs no magnitude comparison.

**Two hypotheses were tested and REFUTED before this one** — recorded so they are not re-derived:

- *"A space glyph overlapping a non-space glyph is padding."* False: the legitimate space in
  `CARPE DIEM` also overlaps `E` and `D`.
- *"Split where the gap ≥ the font's median space width (1.46)."* False: it yields `CARPEDIEM`,
  `ReferenceNumber`, `10:00:00AM`. Adjacent glyphs kern *into* the space, so the measured gap is far
  smaller than the space's own width.

**Finding 3 — R1 is not this problem.** Applying the rule to the measure column gives
`['(blank)Chickpeas', '20,000']` and `['CompletedCommodityTotal']` — the three sub-columns do **not**
split, because there are no space glyphs between them (`)`→`C` is a 27.07 pt gap with no glyph). A
large gap with no glyph is a **column** gap, not a word gap. R1 is therefore **R13** (rules coarser
than the columns), not R2.

**Finding 4 — blast radius, measured.** Across GrainCorp's 488 cells, **49 change**, all repairs:

```
'2 0,000'                    -> '20,000'
'1 18,000'                   -> '118,000'
'5 5,000'                    -> '55,000'
'(blank)Chickpeas   2 0,000' -> '(blank)Chickpeas 20,000'
'(blank)Barley   5 5,000'    -> '(blank)Barley 55,000'
```

No cell is damaged. Compiled end-to-end with the fix **under the row-role harness**
(`compile_tables(p, row_role_proposer=FakeRowRoleProposer(RowRoleProposal(('furniture',
'continuation','continuation'), 0.85, …)))` — with defaults the region escalates
`MERGE_AMBIGUOUS` at score 0.0, both before and after this change): region 2 `asserted`, **cells = 447**,
**score = 0.947** — both unchanged. Note this is not neutral by construction: repaired cells become
`Numeric` where they were `Text` (`is_numeric('2 0,000')` is False, `is_numeric('20,000')` is True),
which feeds the header/body split and region classification. It was measured precisely because it
could have moved something.

---

## 3. Components

### `src/iladub/etkl/geometry.py` — `rule_aware_lines` (one join replaced)

Today (line 179): `text = "".join(c.text for c in gl).strip()`.

Replace with: build the text from the cell's **non-space** glyphs in x-order, inserting exactly one
space between consecutive glyphs `a`, `b` when **both** conditions hold —

1. a space glyph lies between them (either strictly within `[a.x1, b.x0]`, or contained in the
   span of `a`/`b` — the overlapping-padding case), **and**
2. `b.x0 - a.x1 > 0` — they are actually separated.

The `Word`'s bbox is taken from the **non-space** glyphs, so a cell padded with leading spaces no
longer reports ink it does not have. Everything else in the function — row grouping, rule-column
bucketing, the §7 ink-extent range extension — is untouched.

Both conditions are presence tests. Neither compares a magnitude against a unit, so the §8 gate is
satisfied without appeal to a derived statistic.

---

## 4. Testing

Synthetic and domain-neutral, built from the measured shapes in §2:

- **Padding inside a number:** glyphs `2 0 , 0 0 0` with touching bboxes plus overlapping space
  glyphs → cell text `20,000`, not `2 0,000`.
- **A real word space survives:** two tokens separated by a positive gap with a space glyph →
  `CARPE DIEM`.
- **Both in one cell:** → `Chickpeas 20,000`.
- **A large gap with no space glyph does not split** (it is a column gap, R13's business, not this
  function's) — the cell keeps one token.
- **Bbox excludes padding:** a cell with leading space glyphs reports its ink extent from the
  non-space glyphs.
- **Regression:** the ruled fixtures (`ruled_tight_table_pdf`, `ruled_merged_table_pdf`) are
  unchanged; `borderless_*` never enter this path; full suite green.
- **Real-world (local, uncommitted):** 49 of 488 GrainCorp cells change, all repairs; `score == 0.947`
  and `cells == 447` unchanged. No PDF committed.

---

## 5. Neurosymbolic gate & discipline

- **PROCEDURAL, and irreducibly so.** Reconstructing which glyphs the author placed is raw
  extraction. It decides *where text is*, never what it means — no reading judgment, so neither
  AXIOM nor NEURAL applies.
- **No tuned constant, no tolerance, no magnitude comparison.** Both halves of the rule are presence
  tests. The two rejected hypotheses in §2 both required a unit; this one does not.
- **Only emit what the source supports (§7).** This loop exists precisely because the graph today
  asserts `2 0,000`, a string the document does not contain.
- **No overfitting.** Fixtures are authored from the *shape* (overlapping padding glyph; kerned word
  space), not from GrainCorp bytes. GrainCorp is confirmation.
- **Honest limits (§6).** The unruled path keeps the defect, and this does not unblock R4. Both are
  stated rather than left to be discovered.

---

## 6. Residues

New:

- **R16 — the unruled path keeps the split-number defect.** pdfplumber's `extract_words` splits `2`
  from `0,000` on its own. Only the ruled path is fixed here. Closing it means owning word
  segmentation for every document.

Updated:

- **R2** — closed for the ruled path by this loop; remains open as R16 for the unruled path.
- **R1** — measured to be **R13** (rules coarser than the columns), not a word-segmentation problem.
- **R4** — still blocked. After this loop, subtotal rows read a clean `20,000`, but data rows read
  `(blank)Chickpeas 20,000`, so there is still no clean numeric column to sum. R4 needs **R13**.

The register at `docs/superpowers/residues.md` is canonical and is updated by this loop.
