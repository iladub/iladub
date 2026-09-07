# Spec — the box that covers the join ([[R181]])

**Date:** 2026-09-07. **Residue:** [[R181]]. **Predecessor:** the ruling loop
`the-box-that-covers-one-line` (PR #169), whose handoff § 5a ordered this measurement and
§ 5b named the fork.

**Doc impact: none.**

---

## 0. Neurosymbolic classification (CLAUDE.md § Core design principles 8)

**PROCEDURAL — decidable exact arithmetic, and irreducible.** The change unions four bounds over a
set whose membership was *already decided* upstream: `build_row_reading` has, at the point of the
fix, the exact list of `SourceCell`s whose text it is about to join. There is no span/read/group
judgement left to make — the reading judgement is the role vector, and it was made by the NEURAL
proposer and disposed by the tiling oracle before this line runs. It cannot be AXIOM: the source
cells' geometry is not in the RDF graph at all (§ 3.2), so no SPARQL can see it. It cannot be
NEURAL: there is nothing underdetermined about `min`/`max` over four numbers. Its exact sibling
already exists and is the precedent — `cells._cell_from` (`cells.py:96-103`) unions its words'
bounds the same way.

**No tuned constant is introduced.**

---

## 1. The site, MEASURED

R181's row named `headers.py:458` as the construction site and left the *joining* site explicitly
unmeasured, naming `headers.py:62`/`:80` as suspects. **Both suspects are refuted; the site is
`rowrole.py:176-182`.**

The instrument wrapped every candidate and ran the real page
(`corpus/ag-trade/graincorp-stem-2026-07-31.pdf`, page 0):

```
=== group_wrapped  rows=61
   row0: [('Friday, 31 July 2026', 61.23, 66.51)]
   row1: [('Date of Grain', 67.83, 73.11)]
   row2: [('Unique Slot', 74.43, 79.71), ('Loading', 74.43, 79.71), ('Date Nomination', …), …]
   row3: [('GC Fin Year', 81.03, 86.31), … ('Commencement', 81.03, 86.31), … ]
=== build_row_reading  roles=('furniture', 'continuation', 'continuation')
   (0, 'Date of Grain Loading Commencement', 376.32, 81.03, 417.58, 86.31)
```

`group_wrapped` does **not** merge the three lines — it returns them as rows 1, 2, 3, exactly as
`headers.header_rows_of`'s KNOWN LIMIT docstring predicts (the wrap-continuation gate cannot fire
when header leading equals body leading). The join is performed afterwards, by the loop-C NEURAL
reading, at:

```python
    for col, texts in extra.items():                      # rowrole.py:176
        …
        merged = (" ".join(texts) + " " + nodes[tgt].text).strip()
        nodes[tgt] = replace(nodes[tgt], text=merged)      # rowrole.py:182
```

`extra` (`:174`) stores `cell.text` and **discards `cell`** — so the four bounds of every
continuation fragment are read (for `_column_containing`, `:171`) and thrown away one line later.
`replace(…, text=merged)` then keeps the *leaf* node's box. That is the whole defect, in two lines.

**This refutes the predecessor's own caution.** The R178 handoff and R181's row both say
*"do not assume `rowrole.py:182` is the same defect — it is the ROW-header analogue"*, leaving
"whether they are one defect" open. They are one defect, and `rowrole` is not the row-header
module: it decides the **role of each header ROW** in a column-header block. The measurement above
is that line producing the column-header labels R181 was raised on.

## 2. The population, CORRECTED — 7 labels, not 8

R181's row states **"8 of 17 labels on graincorp-stem p0"**. Measured, it is **7**. 8 is the count
of continuation *fragments* (1 in row1 + 7 in row2); they land on 7 labels, because `col7` takes
two (`'Date of Grain'` + `'Loading'` → `'Commencement'`). The prober's `orphan=9` is those 8
fragments plus the furniture banner, which is why the arithmetic looked consistent.

| col | emitted text | fragments joined in | emitted box | union box |
| --- | --- | --- | --- | --- |
| 3 | `Unique Slot Reference Number` | `Unique Slot` | 158.04, 81.03, 204.87, 86.31 | 158.04, **74.43**, 204.87, 86.31 |
| 7 | `Date of Grain Loading Commencement` | `Date of Grain`, `Loading` | 376.32, 81.03, 417.58, 86.31 | 376.32, **67.83**, 417.58, 86.31 |
| 9 | `Date Nomination Received` | `Date Nomination` | 474.72, 81.03, 497.73, 86.31 | 474.72, **74.43**, **516.69**, 86.31 |
| 10 | `Time Nomination Received` | `Time Nomination` | 522.60, 81.03, 545.61, 86.31 | 522.60, **74.43**, **565.53**, 86.31 |
| 11 | `Date Nomination Accepted` | `Date Nomination` | 570.48, 81.03, 593.98, 86.31 | 570.48, **74.43**, **612.45**, 86.31 |
| 12 | `Time Nomination Accepted` | `Time Nomination` | 618.36, 81.03, 641.86, 86.31 | 618.36, **74.43**, **661.29**, 86.31 |
| 14 | `Date Loading Completed` | `Date Loading` | 714.12, 81.03, 741.48, 86.31 | 714.12, **74.43**, **747.44**, 86.31 |

Two facts the table carries that matter downstream, and neither was known when the fork was written:

* **`x0` never moves.** In all 7 the fragment's left edge is at or right of the leaf's. The union
  widens `top` in all 7 and `x1` in 5; `x0` and `bottom` are unchanged everywhere.
* **The widened boxes do not collide.** The largest new `x1` in each case stays left of the next
  label's `x0` (516.69 < 522.60; 565.53 < 570.48; 612.45 < 618.36; 661.29 < 714.12; 747.44 <
  762.02), and the union grows only *upward*, into the header rows and away from the body.

## 3. The fork, disposed

### 3.1 Union the bounds at the joining site — **ADOPTED**

`extra` carries the `SourceCell`, not just its `.text`; the `replace` at `:182` sets `text` **and**
the four bounds to the union of the target node's and every consumed fragment's. `page` is
unchanged (a wrap is within one page by construction — the fragments come from
`header_rows_of(band, …)`, one band, one page).

### 3.2 A containment shape — **NOT EXPRESSIBLE TODAY, and this is measured**

The fork offered "a containment shape (nothing enforces box-covers-text in either direction)". It
cannot be written against the graph as it stands, because the thing it would have to compare
against is not in the graph:

```
$ sed -n '204,210p' src/iladub/etkl/rowrole.py      # emit_reading_evidence
        g.add((sc, RDF.type, TAB.HeaderSourceCell))
        g.add((sc, TAB.sourceText, Literal(text)))
        g.add((sc, TAB.sourceRow, Literal(row, datatype=XSD.integer)))
```

A `tab:HeaderSourceCell` carries **text and row index only — no `tab:hasBBox`, no `tab:onPage`**.
So SHACL can see *that* a label's text was joined from three source cells and cannot see *where*
any of them was. Making the shape expressible therefore requires emitting geometry on
`HeaderSourceCell` first — a graph change strictly larger than the fix it would guard. Deferred as
[[R182]], not silently dropped.

### 3.3 `rowrole.py`'s row-header sibling — **there is none, and that closes the open question**

`grep -n "replace(" src/iladub/etkl/rowrole.py` returns exactly two hits: `:182` (this defect) and
`:248` (`_replace(hreg, tree=nodes)`, a region rebuild carrying no cell geometry). The "sibling
site" the predecessor kept open does not exist as a separate site.

## 4. The oracle

**Disposal (the only signal with power):** `PYTHONPATH=src python3 scripts/unbooked_ink_fate.py
corpus/ag-trade/graincorp-stem-2026-07-31.pdf 0` — `orphan` must fall **9 → 1**, the survivor being
the furniture banner `Friday, 31 July 2026`, which is a `tab:RegionCaption` and correctly covered by
no cell box.

**Guard (not an oracle — the population is 1 page of 27):** the whole-file corpus verdict diff must
come back identical. Per the predecessor's § 5b trap, an identical diff is consistent with the fix
working, doing nothing, and never running; it can only *refute*, never confirm.

**The prediction § 5b rests on is REFUTED as stated, and survives on a narrower basis.** § 5b
predicted no reading consequence because *"no site in `src/` or `vocab/` reads a LabelCell's
bbox"*, flagging `feed._bbox_xy`'s uneumerated call sites as what would sink it. Enumerated:

```
$ grep -rn "_bbox_xy" src/ tests/ scripts/ vocab/
src/iladub/feed.py:228:        x0, y0 = _bbox_xy(graph, e)          # an EntryCell
src/iladub/feed.py:285:            x0, _ = _bbox_xy(graph, label)   # a LABEL — the claim is false
src/iladub/feed.py:479:def _bbox_xy(graph: Graph, entry_cell) -> …
```

`feed.py:285` **does** read a label's bbox. The prediction is re-based on § 2's first fact instead:
that call takes `x0` alone (`x0, _ =`), and **`x0` does not move for any of the 7**. The claim is
now *"the one label-bbox reader reads a coordinate this change never alters"*, which is a claim
about a member and is checked by reading it. The `region_tiles` gate remains the live hazard, and
§ 2's second fact (no collisions, growth upward only) is why it is expected to pass — expected, and
the corpus guard is what tests it.

## 5. What is deliberately NOT done

* **`HeaderSourceCell` geometry, and therefore the containment shape** → [[R182]] (§ 3.2).
* **Nothing is changed for the furniture caption.** `Friday, 31 July 2026` stays orphan-by-box and
  is carried as `tab:RegionCaption`; [[R178]] ruled that carriage sufficient.
* **The prober is not fixed.** Its `orphan` still means "ink no emitted cell's BOX contains" — three
  distinct defects have now worn that label ([[R177]] absent box, R181 short box, R178 genuine
  caption). Unchanged deliberately: R178 § 5 already declined to raise a lint on suspicion.

---

## 6. Results — what was actually run

### 6.1 The disposal: 9 → 1, exactly as prescribed

```
$ PYTHONPATH=src python3 scripts/unbooked_ink_fate.py corpus/ag-trade/graincorp-stem-2026-07-31.pdf 0
BEFORE  b2  UNSUPPORTED_TABLE  ink=612 booked=612 unbooked=0 || entry=586 label=17 orphan=9
        orphans: Friday, 31 July 2026 Date of Grain Unique Slot Loading Date Nomination
                 Time Nomination Date Nomination Time Nomination Date Loading
AFTER   b2  UNSUPPORTED_TABLE  ink=612 booked=612 unbooked=0 || entry=586 label=25 orphan=1
        orphans: Friday, 31 July 2026
```

`score=0.9575163398692811 asserted=586 escalated=26` on both sides. The 8 fragments moved from
`orphan` into `label`; the survivor is the furniture banner, a `tab:RegionCaption` correctly covered
by no cell box ([[R178]]'s ruling).

### 6.2 The guard: the whole-file corpus diff is two lines

`scripts/unbooked_ink_fate_corpus.py`, 27 pages, run before and after:

```
$ diff before.txt after.txt
9,10c9,10
<   b2  UNSUPPORTED_TABLE  … label=17    orphan=9
<       orphans: Friday, 31 July 2026 Date of Grain Unique Slot Loading …
---
>   b2  UNSUPPORTED_TABLE  … label=25    orphan=1
>       orphans: Friday, 31 July 2026
68c68
< total orphan words             : 12
---
> total orphan words             : 4
```

**Every `score=` / `asserted=` / `escalated=` line on all 27 pages is byte-identical**, so the
`region_tiles` hazard § 4 named did not fire. Read as § 4 says: this refutes "the union moved a
verdict"; it confirms nothing on its own, because 26 of the 27 pages never enter the changed path.

### 6.3 FALSIFICATION

Rule 4 (CLAUDE.md § Plan authoring discipline) — both new pins, both shown failing with their
subject removed, then restored green.

**F1 — remove the union.** `replace(n, text=merged, x0=…, top=…, x1=…, bottom=…)` →
`replace(n, text=merged)`:

```
FAILED tests/etkl/test_rowrole_reading.py::test_continuation_merge_unions_the_fragment_bounds_into_the_label_box
1 failed, 12 passed
  b2  UNSUPPORTED_TABLE  … label=17    orphan=9        # the disposal reverts too
```

**F2 — leak the union onto every leaf label** (the second pin's subject: that the union does NOT
spread beyond the target). A three-line insert widening every other leaf node's `top`:

```
FAILED tests/etkl/test_rowrole_reading.py::test_an_unmerged_label_keeps_its_own_box_exactly
1 failed, 12 passed
```

F2 matters because without it F1's pin passes under a change that destroys the geometry of the
other three labels — the [[R173]]-adjacent failure mode of a test that pins a value rather than a
behaviour.

**Restored:** `13 passed`.

### 6.4 The pins run in CI

Unlike this loop's three predecessors, the reproduction needs no corpus: `caption_and_wrap_band`
(`tests/etkl/test_rowrole_reading.py:29`) is a synthetic fixture built for loop C, and it exhibits
the defect at unit scale (`Unit` at top 12 prefixed onto leaf `Ref` at top 24 → the box must grow up
to 12 and right to 175). The **oracle** still needed the corpus; the **pin** did not. That
distinction is finer than [[R173]]'s row currently records and is carried into this loop's handoff
§ 5c.

### 6.5 The suite

```
$ PYTHONPATH=src python3 -m pytest tests/ -q
1508 passed, 7 skipped, 1 xfailed, 3147 warnings in 3670.18s (1:01:10)
```

Run with every file staged, so [[R179]]'s trap — a new tracked `.ttl` that fails
`test_artifact_terms.py` / `test_artifact_declarations.py` only after `git add` — is covered even
though this loop adds no `.ttl`.
