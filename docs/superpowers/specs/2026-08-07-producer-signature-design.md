# The producer signature, and rejoining a split table — design

**Date:** 2026-08-07 · **Status:** **BLOCKED at adversarial review, 2026-08-07 — superseded** ·
**Specimens:** all five corpus documents + a reportlab control ·
**Follows:** the table-production algebra — a report contains no structure no tool could produce,
so reading is inferring which operations produced it, and `tab:ReshapeRecipe` already commits to
that road ("inverse report-authoring operations … certified by round-trip reproduction").

**Doc impact:** increment — one new sensor and one new `tab:ReshapeOperation` subclass in the
owned `tab:` namespace. No site page contradicted.

## 1. Why a producer signature comes first

Every operation inference presupposes an operation *set*. A table laid out by a spreadsheet admits
pivot, rollup, label suppression and cell-level banding; one typeset by LaTeX admits none of them
and offers `booktabs` rules instead; one drawn by a plotting library admits neither. **Choosing the
wrong operation set is choosing the wrong inverse**, and no amount of geometric care recovers from
it.

### 1.1 File metadata does not answer this — measured

The obvious shortcut is the PDF's own metadata. It is wrong, and knowing *why* is the point:

| document | `Creator` / `Producer` / `Title` |
| --- | --- |
| apple | `Creator='Word'`, Producer = macOS Quartz |
| WHO | `Creator='Acrobat PDFMaker 7.0 for Word'` |
| stem | `Title='Shipping Stem 2026 07 31.xlsx'` |
| capacity | `Title='Shipping Stem 2026 08 04.xlsx'` |
| CBH | `Producer='Microsoft® Excel® for Microsoft 365'` |

Metadata names **the assembler of the page, not the producer of the table**. A Word document
routinely carries a table pasted from a spreadsheet, copied from a notebook, or captured as an
image. Read naively, apple's `Creator='Word'` rules out every spreadsheet operation — and apple's
table is a spreadsheet artefact. The metadata misleads in both directions and is therefore, at
most, weak evidence about who assembled the page.

## 2. The signature is per-table, and it discriminates — measured

Rendering signature across the corpus plus a **reportlab control** (a third producer, drawn by our
own fixtures):

| document | h-rules | v-rules | fills | per-cell | per-row | narrow (<12px) | rule widths |
| --- | --- | --- | --- | --- | --- | --- | --- |
| apple | 52 | 0 | 318 | 235 | 83 | **79** | 4, 69, 70, 71 |
| WHO | 55 | 4 | 38 | 34 | 4 | 0 | 2, 43, 45, 54 |
| stem | 8 | 3 | 191 | 170 | 21 | 0 | 777, 819, 821 |
| capacity | 56 | 65 | 391 | 390 | 1 | 0 | 102, 606, 773, 774 |
| CBH | 74 | 95 | 21 | 7 | 14 | 0 | 50, 147, 411, 1113 |
| **reportlab control** | **0** | **0** | **0** | 0 | 0 | 0 | — |

Every producer is distinguishable:

- **apple** is the only document with narrow sub-column fills (79). Combined with per-cell fills at
  one column's width (70×14, grey 0.937 alternating with white) and per-column bottom borders
  (69–71px), this is spreadsheet accounting format: the currency glyph occupies its own narrow
  sub-cell, and banding is applied cell-by-cell rather than as a full-width row band.
- **capacity, CBH** — heavy rules on both axes: a drawn lattice.
- **stem** — eight rules, all ≈800px: full-width separators only, with banding doing the row work.
- **WHO** — segmented rules, few fills.
- **reportlab** — draws nothing at all. Pure text placement is itself a signature class.

**The distinguishing measurements are ratios and counts relative to the page and to the table's own
column width — never absolute sizes.** A rule about one column wide above data is a header
underline whatever the document's scale.

## 3. Consequence the loop must handle, not discover later

**The fixtures cannot validate this sensor.** Every reportlab fixture draws zero rules and zero
fills, so a fixture-based test of signature classification passes vacuously — it exercises only the
"draws nothing" branch. Validation must run against the real corpus documents, and any fixture test
must assert the *control* behaviour explicitly rather than standing in for the others.

## 4. The inverse operation: rejoining a split table

`tab:RejoinSectionsOp` — the inverse of splitting one grouped report into separate blocks, whether
for readability or because a group-by was emitted per group.

apple page 1 is one balance sheet cut into eight blocks and judged eight times. Measured column
geometry per block:

| block | kind | ncols | boundaries |
| --- | --- | --- | --- |
| 2 | UNSUPPORTED | 3 | 50, 417, 489, 562 |
| 3 | UNSUPPORTED | 3 | 53, 316, 493, 562 |
| 4 | UNSUPPORTED | 4 | 53, 194, 412, 492, 562 |
| 5 | UNSUPPORTED | 3 | 50, 417, 489, 562 |
| 7 | UNSUPPORTED | 3 | 53, 419, 493, 562 |

### 4.1 The criterion is a round trip, not a tolerance

The measure columns agree (≈489/493 and 562 throughout); the **stub** boundary varies (316 / 417 /
419) because `infer_leaf_grid` derives it from each block's own ink, and block 4 carries a spurious
extra split. So identical-boundaries is the wrong test, and "within N points" would be a tuned
constant — a §8 defect.

**The criterion:** merge the candidate blocks, re-infer a single grid over the merged ink, and
require that **every row of every contributing block tiles under that one grid**. If they do, the
blocks were one table; if any row fails, they were not. No tolerance, no threshold, and it fails
loudly rather than silently welding unrelated blocks — which is the R19 hazard this project has
already been bitten by.

## 5. Success criteria

- The signature sensor classifies each of the five corpus documents into a distinct producer class,
  and the reportlab control into its own — measured, with the classification recorded as evidence
  rather than asserted.
- `tab:RejoinSectionsOp` merges apple page 1's blocks into one table **only when the merged grid
  tiles every contributing row**, and refuses otherwise.
- **apple's document score moves upward from 0.0606860158.** This loop changes a verdict by design;
  it is a capability slice, not a recording one.
- stem 0.9655 / 2152 cells / chain [3], CBH 0.9047, capacity 1.0000, WHO 0.5597 **unchanged** — the
  rejoin must fire only where the criterion holds.
- Round-trip: the merged table regenerates the observed blocks, per `tab:ReshapeRecipe`'s existing
  certification contract.
- No tuned constant anywhere. Every threshold is a ratio against the page or the table's own width.

## 6. Premises, measured

| # | Premise | Status |
| --- | --- | --- |
| P1 | The rendering signature discriminates between producers | **holds** — §2, five documents plus a control, all distinct |
| P2 | The fixtures can validate the sensor | **REFUTED** — §3, they draw nothing; real documents required |
| P3 | apple's blocks share column geometry | **partial** — measure columns agree, stub varies, one block has a spurious split; criterion revised to the round trip in §4.1 |
| P4 | CBH's per-port sections are the same shape of split | **not measured** — assumption, blast radius: the loop may target apple only |
| P5 | Rejoining moves apple's score | **not measurable before building it** — the loop's own success criterion |

## 7. Out of scope

- `tab:RefillLabelsOp` — the ditto/label-suppression inverse. Already implemented as forward-fill
  in `rowheaders.py`; naming it in the ontology is a separate, behaviour-neutral change.
- `tab:SplitRowFieldsOp` — recovering a multi-level row index from an indented single stub column.
  The inverse is right, but its attribution to Excel Compact Form was wrong (apple's table reaches
  Word from a spreadsheet by an unknown path), and it needs its own premise pass.
- Producer classes beyond those the corpus exhibits. LaTeX `booktabs`, `gt`, `flextable`, pandas
  and ASCII renderers all have distinct signatures, but **we hold no document from any of them** —
  modelling them now would be fitting to imagination.

## 8. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate §8: the signature is evidence, and classification is an AXIOM over it. **No
  tuned constant** — ratios against the page or the table's own width only.
- §7 only emit what the source supports: an unrecognised signature is recorded as unrecognised, and
  the operation set stays open, never guessed.
- Round-trip certification is the proof, as `tab:ReshapeRecipe` already requires.
- Source ownership: `tab:` is ours; no HGA term appears as a subject.

---

## Close — BLOCKED, and kept as history

Committed 2026-08-08, unchanged apart from this note, so the record of a rejected approach is
not lost.

**Producer attribution is unmeasurable.** stem and capacity carry byte-identical PDF metadata
and land in *different* signature classes; capacity and CBH differ in producer and land in the
*same* one. Within-producer variance exceeds between-producer variance, and no constant-free
rule separates more than three classes.

**`RejoinSectionsOp` inverts an operation no producer performed.** apple's banding runs unbroken
y=139.56→746.28, so **iladub's own segmenter split that table**, not the author. That is a
segmentation repair, and filing it under the reshape vocabulary mis-describes it.

**What replaced it.** Grid primitives rather than producers — see
`2026-08-08-data-grid-types-elements-axioms.md`, which defines the data grid before detecting
it and reaches four transcribed oracles at 162/162 entry rows. The one durable idea from this
spec survives there: *decoration is posterior to reshape*, so a drawn mark measures the
finished dimensions.
