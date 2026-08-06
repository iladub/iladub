# Quantity typing — when two lexical forms of a number are the same type — design

**Date:** 2026-08-06 · **Status:** closed 2026-08-06 ·
**Discharges:** R55 (parenthesized accounting negatives) **and** the unit-marker spec's §6.1
(the `$ 45,781`-mixed-with-`45,781` homogeneity question) — measured to be one loop, not two
(§2) · **Specimen:** `corpus/financial/apple-fy2026q3-statements.pdf` page 0, band 4
(`Operating income … Net income`)

**Close-out (2026-08-06), measured, not simulated:** apple page 0 **0.0000 → 0.1170**, band 4
asserted with **20 cells** exactly as simulated in §4; apple whole document
**0.0326975477 → 0.0606860158**. Byte-identity gate all held (`tests/test_corpus_stem.py` +
`tests/test_cbh_e2e.py`: **13 passed in 248.79 s** — stem 0.9655 / 2152 cells / chain [3], CBH
0.9047; capacity **1.0000000000**; WHO **0.5597484277**). All four batteries (typing,
derivation, closure, membrane) together: **45 passed in 386.18 s**. Full suite: **1011 passed,
1 failed, 5 skipped, 1328.48 s** — the one failure is the known machine-environmental
`tests/test_release_gate.py::test_since_date_fallback_and_previous_tag` (bare env dict without
PATH hits this machine's broken Xcode git shim; no branch commit touches that test; green in
CI). §6's success criteria are all met on these numbers.

**The cross-loop finding, the most interesting thing this loop learned:** the full suite caught
loop R41's `test_axiom_refuses_past_the_end_split` failing. Diagnosed, not assumed: R41's
`$`-sandwich fixture typed `[Currency, Numeric, Numeric, Numeric, Numeric, Currency]`, and its
past-the-end split existed **because** Currency and Numeric were different types (modal
Numeric, last row a Currency mismatch → `s_col = len(rows)`). The `tab:Quantity` family this
loop shipped makes that column homogeneous, so `s_col = 1` — a correct in-range split. **This
loop dissolved R41's failure mode at its source.** R41's invariant (`?s_col <= ?maxrow`) is
untouched; only its fixture stopped exercising it. Fixed by renaming the sandwich test to
record the change honestly and adding a replacement `test_axiom_refuses_past_the_end_split` on
a `tab:Date`-terminated shape — verified empirically by both implementer and reviewer to return
`None` with the `?maxrow` guard and `7` with it stripped, proving it exercises that clause and
not some other refusal path. This is evidence the change reached further than this spec
predicted, in a good direction: a defect this spec never named was resolved as a side effect of
correctly modelling the domain.

**Doc impact:** increment — two new owned `tab:` lattice members plus a datatype-family
vocabulary; a wiki note on quantity typing queues for the next release. No site page
contradicted.

## 1. The question

`celltype._cell_datatype` recovers a lexical form's datatype, and five queries
(`header-body-split`, `looks-transposed`, `transpose-coherent`, `stub-data-split`,
`unit-marker-column`) reason about **type homogeneity** over those values. The open question
this loop answers: *when do two different lexical forms of a number count as the same type?*

Two forms currently answer it wrongly:

- `(171)` — the standard US accounting notation for a negative — types `tab:Text`, identical
  to a prose label.
- `$ 45,781` types `tab:Currency` while `45,781` types `tab:Numeric`, so a money column whose
  first and total rows carry the symbol is **not type-homogeneous**.

## 2. The measurement that re-scoped this loop (2026-08-06)

R55 stated the apple blocker as: *"`transpose_is_coherent` returns False SOLELY because row 2
types `[Numeric, Text, Numeric, Text]`"* — i.e. the parens. **Measured through the production
seam (`compile.page_bands`, which builds ruled bands — a hand-rolled band loop gives a
different, wrong answer), that attribution is off by one link:**

| simulated change | `looks_transposed` | `transpose_is_coherent` | band 4 outcome |
| --- | --- | --- | --- |
| none (today) | True | False | escalates `TRANSPOSED` |
| **parens only** | True | **False** | **unchanged — escalates** |
| **currency only** | **False** | not asked | takes the record path |
| both | False | not asked | **asserts, 20 cells** |

The real chain is: `Currency` vs `Numeric` makes *no column type-homogeneous* → that is what
makes `looks_transposed` fire → only then is the coherence oracle asked, where the parens
fail it. **Fixing the parens alone changes nothing**, because the band never gets past the
first gate. Fixing the currency split alone lets the band through. Page-0 score with both:
**0.0000 → 0.1170**.

R55 is therefore a genuine defect but a *secondary* one. Its register row's attribution is
corrected at this loop's close.

## 3. The design — one principle, two mechanisms

The two cases are genuinely different, and the difference is the design.

### 3.1 `tab:ParenthesizedNumber` — a wildcard, because the form is ambiguous

A new lattice member for `(<number>)`, recognised by a format grammar in `_cell_datatype`
(PROCEDURAL raw typing, exactly as `is_date`/`is_currency` are).

It is **format-identical to a footnote marker**: measured on apple, 34 negative-shaped and 3
footnote-shaped cells, the footnotes being exactly `(1)`. No grammar can separate them — only
context can. So the honest reading (§7: assert only what the source supports) is to
**abstain**: `tab:ParenthesizedNumber` is excluded from the modal vote and never counts as a
mismatch, precisely the treatment `tab:Blank` already receives. This reuses a shipped,
proven pattern rather than inventing a compatibility claim the evidence cannot support.

Consequence, accepted: a column of *nothing but* parenthesized numbers has no modal type and
is excluded, exactly as an all-Blank column is. No measured document exhibits one.

### 3.2 `tab:Currency` ≡ `tab:Numeric` for homogeneity — a declared family, because the form is unambiguous

`$ 45,781` is unambiguously a quantity. The `$` is a **unit marker rendered on some rows
only** — a reading this repo already asserts elsewhere (`tab:UnitMarker`, loop unit-marker).
So Currency and Numeric are the same kind of thing for homogeneity purposes, and that is a
claim the evidence *does* support.

The rule is **declared in the owned vocabulary**, not repeated in five queries:

```turtle
tab:Quantity a tab:CellDatatypeFamily .
tab:Numeric  tab:inDatatypeFamily tab:Quantity .
tab:Currency tab:inDatatypeFamily tab:Quantity .
```

Each homogeneity query normalises through it (`OPTIONAL { ?d tab:inDatatypeFamily ?fam }
BIND(COALESCE(?fam, ?d) AS ?t)`), so the compatibility rule is published, auditable, citable
with the ontology, and extensible — `tab:Date` deliberately stays its own family; a future
Percentage would join Quantity by adding one triple, not by editing five queries.

## 4. Blast radius, measured before design (2026-08-06)

Simulated end-to-end (paren → wildcard, Currency → Numeric) on every fetched corpus document:

| document | simulated | baseline | |
| --- | --- | --- | --- |
| graincorp stem (whole doc) | 0.9655 / 2152 cells / chain [3] | 0.9655 / 2152 / [3] | byte-identical |
| CBH | 0.9047 | 0.9047 | byte-identical |
| graincorp capacity | 1.0000 | 1.0000 | byte-identical |
| WHO | 0.5597 | 0.5597 | byte-identical |
| **apple page 0** | **0.1170**, band 4 asserts 20 cells | 0.0000 | **the target** |

## 5. The evidence

1. **Typing differential** — old lattice versus new, comparing each of the five queries'
   verdicts over every corpus document's compiled page graphs. The direct analogue of this
   repo's closure and engine differentials.
2. **Recall/precision battery for the paren grammar**, which R55's own register row mandates
   before the grammar is trusted to flip any homogeneity verdict: footnote `(1)`;
   non-numeric parentheticals (`(see p.250)`, `(cont'd)`, `(a)`, `(i)`); the existing
   `(blank)` marker (must stay `tab:Blank`); malformed forms (`(171`, `171)`, `$(171)`,
   `(171)*`, `()`); and a mixed-sign column.
3. **Family normalisation is honest per query** — each of the five must be shown to change
   only the intended verdicts, with the differential as the proof.

## 6. Success criteria

- Corpus byte-identity for stem (**0.9655** / 2152 / chain [3]), CBH (**0.9047**), capacity
  (**1.0000**), WHO (**0.5597**) — these are the no-regression gate.
- Apple page 0 asserts band 4 (**20 cells**), score above **0.1170** is not required but the
  measured value is recorded; the document score is recorded, not targeted.
- Both batteries green; full suite green apart from the known machine-environmental
  `test_release_gate`.
- R55 closed **with its attribution corrected**; the unit-marker spec's §6.1 discharged.

## 7. Out of scope, named

- Apple page 0's four remaining `REGION_TILING_FAILED` and one `MATRIX_AMBIGUOUS` regions:
  this loop unlocks one band, not the document.
- R61's corpus-wide emitter-typing invariant probe stays open.
- Boolean/Code datatypes remain the deferred B2b work; this loop adds only quantity forms.

## 8. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate: the paren grammar is PROCEDURAL raw typing (a format grammar, no tuned
  constant — digit-count thresholds are explicitly forbidden, which is *why* the ambiguous
  form abstains instead); the family normalisation is an AXIOM over declared vocabulary.
- §7 credibility: an ambiguous form abstains rather than guessing; nothing is typed that the
  lexical form does not support.
- Source ownership: all new terms in the owned `tab:` namespace.
