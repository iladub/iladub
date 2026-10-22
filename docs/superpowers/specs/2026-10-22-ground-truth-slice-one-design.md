# Ground truth, slice one: the Fed H.4.1 table 1 scored cell by cell (design, 2026-10-22)

**Serves:** maintenance. This proposes a new criterion (§ 6) instead of serving an existing one. No
criterion in `tests/arc-manifest.ttl` measures carried cells against truth.

**Doc impact: increment.** The corpus baseline gains a per-document `truth` block, and the suite gains
a floor test that reads it. No released meaning changes.

**Status: DRAFT, for the maintainer's approval.** The maintainer decided on 2026-10-22 that this work
runs next, that the substrate arc pauses while it runs, and that slice one is Fed H.4.1 2025-01-02
checked against its dated HTML release (`docs/superpowers/2026-10-22-ground-truth-set-handoff.md`).
Everything below that is not quoted from that handoff is this spec's proposal.

## 1. Goal

Answer "is this table right?" with a number that sees **carriage**. The baseline score cannot:
it counts asserted tokens against escalated tokens (`src/iladub/etkl/compile.py:3-4`), so a table
carried under the wrong headers scores as fully asserted (R240). Slice one builds one truth file, one
scorer and one floor, all on one table, merged in days. Widening comes after it merges (§ 7).

## 2. What was measured before this spec (2026-10-22, on `origin/main` at `4dc64be`)

- **The compile reproduces the baseline.** `compile_document('held-out/fed-h41-2025-01-02.pdf')`,
  run offline with `BAML_LIVE` and `ILADUB_RECORD_READINGS` unset, gave 21,446 triples and a score of
  0.8051146384479718. Both match `tests/corpus-baseline/fed-h41-2025-01-02.json`. It took 3m47s.
- **A cell's row and column can be read from the graph with code that already exists.**
  `table_records(graph, per_cell=True)` (`src/iladub/feed.py:502`) returned 139 records. Each concept
  in a record carries `text` (the column's header path), `value` (the cell) and `region` (the page
  position).
- **Table 1 is carried with every column key wrong.** Region `p0#htable3`, records `htable3-r0…`.
  The table's first data row was taken as its header, so every cell's column key is a data value:

  ```
  p0 htable3-r2
      'Reserve Bank credit' = 'Bills2'
      '6,819,571' = '195,343'
      '20,940'    = '0'
      ...
  p0 htable3-r4
      '-'      = '+'          <- the sign, carried as its own cell
      '20,940' = '62'         <- truth: +62
  ```

  The baseline scores this page at 0.9019. The true column path of `195,343` is
  `Averages of daily figures › Week ended Jan 1, 2025`. This is R166's failure (a data row taken as
  the header) and R240's blindness, both on one page.
- **The publisher's HTML states its own access function.** In
  `https://www.federalreserve.gov/releases/h41/20250102/`, table 1 is the second `<table>`. Every data
  cell carries `header="t1r1c1 t1h1c2 t1h2c1"`: its row-group cell (`t1r…`) and its column header
  cells (`t1h…`). The attribute is `header`, not the standard `headers`; zero `headers=` occur. Header
  cells use `colspan`/`rowspan`. Footnote marks are `<span … vertical-align:super>` (e.g.
  `Securities held outright` + super `1`). Row nesting appears only as `text-indent`.

## 3. Design

### 3.1 The truth file (PROCEDURAL: raw extraction)

A script reads the HTML snapshot, checks its SHA-256, and writes
`tests/ground-truth/fed-h41-2025-01-02/table-1.csv` together with a provenance header (URL, retrieval
date, SHA-256, table ordinal). Each row is one truth cell:

| field | read from |
| --- | --- |
| `row_label` | the row's first cell, text without its super spans |
| `row_label_marked` | the same text with super-span text appended without a space (how the PDF renders it) |
| `row_occurrence` | the 0-based count of earlier rows in this table with the same `row_label` |
| `col_path` | the texts of the `t1h…` ids named by the cell's `header` attribute, in attribute order, joined by ` › ` |
| `value` | the cell's text |

The script reads only the publisher's markup: `header`, `id`, `vertical-align:super`. It reads no
geometry, and `text-indent` in particular is never used. **Why it is irreducible:** this is source →
typed facts, the first PROCEDURAL class in CLAUDE.md § 8, and nothing in it is underdetermined. The
HTML is a US Federal Reserve release. The CSV is committed. The HTML snapshot is not committed: its
hash pins it, and the script refuses a snapshot whose hash differs.

### 3.2 The normalisation (declared, applied to both sides, nothing else)

1. Unicode NFKC.
2. Collapse every whitespace run, including U+00A0, to one space, and strip the ends.
3. Remove the whitespace between a leading `+` or `-` and a digit (`-    20,940` → `-20,940`).

There are no case folding, no number parsing and no tolerance. A rule added later is a spec change.

### 3.3 The scorer (PROCEDURAL: decidable exact comparison)

**Compiled side:** `table_records(graph, per_cell=True)`, restricted to the records whose regions lie
in the table's PDF regions. **The plan must MEASURE**, not assume, two seams:

- **(a)** In both the record branch and the per-cell branch, which concept of a `Record` is the row
  label. In the record branch above it is the concept whose `text` is the stub column's header.
- **(b)** Which PDF regions the HTML table spans. Table 1 has 36 HTML rows. Whether they all sit in
  `p0#htable3`, or continue onto later pages or into other regions, is not established.

**Matching key:** a compiled row matches a truth row when its normalised label equals `row_label` or
`row_label_marked` at the same `row_occurrence`. Each truth cell receives **exactly one** outcome:

| outcome | meaning |
| --- | --- |
| `CORRECT` | row matched, `col_path` equal, `value` equal |
| `MISATTACHED` | row matched, `value` found on that row, `col_path` differs (header attachment failed) |
| `WRONG_VALUE` | row matched, a cell under the equal `col_path` with a different value (a dropped sign lands here) |
| `REFUSED` | the cell's region carried no asserted table (escalated or ignored) |
| `MISSING` | an asserted table covers the region, but no row matches |

Two counts are reported beside the outcomes. `SPURIOUS` counts compiled cells of the matched rows that
no truth cell claims. `MARKED_LABEL` counts rows matched only through `row_label_marked`, meaning a
footnote mark was carried as part of the label.

**`REFUSED` is never folded into a wrong count.** The compiler's stance, refuse rather than invent,
stays visible in the number.

Where `MISATTACHED` and `WRONG_VALUE` could both apply (a value repeats on a row), the scorer pairs
cells by `col_path` first and claims each compiled cell at most once. The pairing order is the plan's
to fix and the test's to pin.

### 3.4 Where the number lives, and the floor

The corpus PDFs never reach CI, so CI cannot compile and score. The proposal:
`scripts/corpus_verdict_snapshot.py` adds a `truth` block (the outcome counts per table) to a
document's snapshot whenever `tests/ground-truth/<doc>/` exists. That makes the score part of the
committed baseline, so the R305 gate already proves it was regenerated. Both the script and the
truth directory become baseline inputs.

A suite test, which runs in CI, reads the committed `truth` block and fails if `CORRECT` falls below
`tests/ground-truth/fed-h41-2025-01-02/floor.json`. The floor is a **ratchet, not a tuned constant**:
it starts at the measured value and is raised by hand in the change that raises the score. Lowering
it needs a dated note in that file saying why.

### 3.5 Prediction (PROPOSED, falsifiable in the first task)

On table 1 as compiled today, `CORRECT` is 0 or near it, and `MISATTACHED` takes most of the cells,
because every column key is a data value (§ 2). `WRONG_VALUE` is at least the number of signed,
non-zero change cells that the PDF splits into a separate sign. If `CORRECT` comes out high, the
scorer is wrong: § 2's record dump shows no cell keyed by a true header.

## 4. Gate classification (CLAUDE.md § 8)

| decision | class | why |
| --- | --- | --- |
| HTML → truth cells | PROCEDURAL | raw extraction of publisher markup; no reading judgement |
| normalisation | PROCEDURAL | three declared string rules; no constant, no tolerance |
| truth ↔ compiled matching | PROCEDURAL | exact equality on declared keys; decidable |
| which PDF regions a table spans (seam b) | measured by hand once, recorded in the truth file's provenance | it is a fixture fact, not a decision the scorer makes at run time |

The scorer makes no span/read/group judgement about the PDF. It only reads what the compiler asserted.

## 5. Tests (each with a falsification in the task report, per plan rule 4)

1. **Extractor on a hand fixture:** a three-row HTML fragment with a super-span footnote, a `colspan`
   header and a repeated row label yields the exact CSV rows.
2. **Scorer, one outcome each:** a minimal graph built with the compiler's own `tab:` terms produces
   exactly one each of `CORRECT`, `MISATTACHED`, `WRONG_VALUE`, `REFUSED` and `MISSING`.
3. **Floor test:** the committed `truth` block's `CORRECT` is ≥ `floor.json`.
4. **Hash refusal:** the extractor refuses a snapshot whose SHA-256 differs.

## 5a. What is NOT done in this slice

- No change to the compiler. This slice measures; fixing R166 on this page is the next loop's job,
  and the floor is what will show that it worked.
- No second document, no public benchmark (FinTabNet, OmniDocBench), no Docling re-run (R247).
- No hand-transcribed truth. Slice one uses publisher truth only.
- No grounding check: whether a cell grounds to a concept is out of scope. Only carriage is scored.

## 6. Arc criterion (proposed)

`prog:criterion:etkl:<next>`: *"carried table cells are scored against independent truth, and the
score is a committed, CI-gated number."* It would be met when tests 1–4 pass and the `truth` block is
in the baseline. The criterion is met by the instrument existing, not by its score being high.

## 7. Unverified

- Seams (a) and (b) in § 3.3.
- That `table_records`' row ordering puts repeated labels in page order, which `row_occurrence` relies on.
- That the PDF's header text, once normalised, can equal the HTML's at all. If the PDF breaks a header
  across lines differently, rule 2 covers it. If its wording differs, `CORRECT` is unreachable for
  that column, and the spec must say how that is handled before the floor means anything.
- The time a baseline regeneration takes once the `truth` block is added (24 minutes today, per CLAUDE.md).

## 8. Approval

**Approved by the maintainer on 2026-10-22 ("I will follow your recommendations here").** The three
open decisions are settled as recommended:

1. The score lives in the committed corpus baseline (§ 3.4). `scripts/corpus_verdict_snapshot.py` and
   `tests/ground-truth/` become baseline inputs, and this loop pays one regeneration.
2. The arc criterion in § 6 is added.
3. The slice is table 1 only.
