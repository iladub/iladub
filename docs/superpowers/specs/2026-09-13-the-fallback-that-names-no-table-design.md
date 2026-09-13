# Spec — the fallback that names no table: etkl:04's reader books its ink on a prose band

**Serves:** prog:criterion:etkl:04 — `gov-stats/ons-index-of-services-2026-02.pdf`
(`tests/arc-manifest.ttl:265`; the document's manifest node is `tests/corpus-manifest.ttl:94`).
This spec is a **prerequisite** of that criterion, not a criterion of its own.

**Date:** 2026-09-13. **Branch:** `etkl-04-the-ons-document`, cut from `fdb3122`.

**Doc impact: none.** This loop ships a spec and no released term. Nothing queues for a release
tag and nothing blocks one.

Written in the session's first third, under the originating floor. Every load-bearing claim below
carries the command that produced it, per CLAUDE.md § Plan authoring discipline rule 2.

## 0. The subject, and why this is a prerequisite rather than the criterion

`etkl:04` asks that ONS compile to `cor:CompilesAbove` under a **pinned floor** and an
**accepting** adjudication. What stands there today is a recorded HOLD (2026-08-20,
`tests/corpus-manifest.ttl:94`), whose stated reason is that *"nine pages of a statistical release
with hierarchical SIC2007 section headers and a Total aggregate column have not been read against
the compile by anyone"*, and that the document carries no `cor:contract` / `cor:terms` /
`cor:shapes`, so no membrane has ever seen its output.

The route off that hold is the one [[R211]] took for graincorp: (1) author the contract triple,
(2) exercise the grounding leg, (3) a reviewer reads the carried reading against the source page.

**Step 3 is not addressable today, and that is what this spec repairs.** The region that carries
this document's reading books no ink and names no table, so there is nothing for a reviewer to
address: the reading exists in the graph but the report that should point at it does not.

## 1. What is measured

All figures at `fdb3122`, the commit this branch was cut from.

```
$ ./.venv/bin/python -m pytest \
    "tests/test_corpus.py::test_expected_verdict[gov-stats/ons-index-of-services-2026-02.pdf]" \
    -q -s -m corpus
gov-stats/ons-index-of-services-2026-02.pdf: score=0.9720 pages=9 chains=[1] wall=10s
1 passed in 11.82s
```

73 regions: **70 `NON_TABLE ignored`**, **2 `RECORD_TABLE asserted`**, **1 `UNSUPPORTED_TABLE
asserted`**. Per-region `tokens_asserted`, measured by compiling the document and reading
`rep.pages[p].regions[*]`:

```
p7 (16 bands, 17 reports): [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, 285, 0]
p8 ( 9 bands, 10 reports): [0,0,0,0,0,0,0,0, 286, 0]
```

The 285 sits on report #15 — an **ignored prose band holding 6 words** — and the grid's own report
#16, carrying **276 cells**, books **0**. p8 is the same shape. Attributing ink by verdict
(measured, not obtained by subtraction): **571 asserted tokens on ignored bands, 19 on asserted
regions**.

The grids themselves are real and identified:

```
DataGrid subjects: https://example.org/etkl/doc/p7#p7-datagrid
                   https://example.org/etkl/doc/p8#p8-datagrid
tab:EntryCell 554 · tab:DataGrid 2 · tab:continuesTable 0
report table_uris: p4 UNSUPPORTED_TABLE …#htable2 · p7 RECORD_TABLE None · p8 RECORD_TABLE None
```

And they read as the release's index tables — 46 rows × 6 columns each, e.g. p7 row 0
`2022 | weights | 1000 | 163 | 122 | 438 | 277`, then yearly series and monthly series to
`2026 | Feb`.

**Corpus-wide, all 7 documents / 27 pages:** 14 asserted `RECORD_TABLE` regions, of which
**exactly 2 carry `table_uri=None` — ons p7#16 and p8#9**. That is the fallback site's signature,
because `compile.py:1363` is the only site that constructs a record-table report without passing a
URI. Every other asserted record table came from a band site and books ink against its cells
(graincorp 406/406, bfs p6 ×6, who-wfa 78/65 ×2, cbh 54/13, apple 6/3).

## 2. The two defects

Both live in one five-line branch, `src/iladub/etkl/compile.py:1351-1365`, the `datagrid_fallback`
path — introduced by `06c9f2bb` (2026-08-09).

**D1 — the returned URI is discarded.** `:1359` calls `emit_data_grid(graph, _grid, _lines, doc,
page_number)` and drops the result, though it is declared `-> "URIRef"` (`datagrid.py:599-600`)
and the adopt twin at `:1477` binds it as `_grid_uri` and passes it to the report. Consequence:
`table_uri` is `None` on a region the graph *does* carry, and every consumer keyed on
`table_uri is not None` skips it — section stitching (`document.py:1554`), the adoption driver's
grid check (`document.py:1648`), and continuation linking, which is why `tab:continuesTable` is 0
across a nine-page release whose two tables are consecutive halves of one series.

**D2 — the branch's mark is appended after its own ink.** `:1362` does `asserted_total +=
_tokens`; `:1365` then appends the branch's `band_marks` entry. The per-band ledger snapshots the
running totals **at the top of each band's turn** (`:789`, with the invariant stated at
`:782-785`) and closes with a sentinel at `:1367`, so the mark appended at `:1365` is the one that
closes the **last band's** slot — and it already contains the grid's ink. The differencing at
`:1370-1371` therefore books the grid's tokens against the final band.

The two are independent: D1 is a dropped value, D2 is a statement order. Neither changes any
total, which is why the document score 0.9720 is untouched and **no corpus score moves**.

## 3. Why nothing caught it

Three instruments cover band ink. Each is blind to this branch **by construction**, not by corpus
accident — and the blindness, not the arithmetic, is the reason a defect from 2026-08-09 survived.

- **O1, the every-word oracle.** `tests/etkl/test_read_band_books_every_word.py` pairs bands to
  reports in a helper that asserts `len(seen[0]) == len(rep.regions)` (`:64`). The fallback shape
  is reports = bands + 1, so the helper *refuses* it rather than checking it. Its four
  `ASSERT_SITES` are band sites reached by synthetic fixtures; the fallback is not among them.
- **O2, the unbooked-ink census.** `scripts/unbooked_ink_census.py:71-72` passes
  `datagrid_fallback=False`, and `:82` zips bands to regions. Its summary line *"ASSERTED bands
  with unbooked ink: 0 of 24"* is therefore true of a population that cannot contain the
  misattributed regions. **This was established by a refuted prediction**: the expectation that
  the census would report a negative unbooked on ons p7 band 15 was run and came back showing the
  page as `score=0.0 asserted=0 escalated=0` — the fallback-off reading — which is how the
  exclusion surfaced.
- **O3, the sum identities.** `test_datagrid.py:1149` and `test_adoption_document.py:141` assert
  that per-region tokens sum to the page totals. A misattribution preserves sums exactly.

## 4. What the loop builds

Interfaces and invariants only; the bodies are the implementer's.

**I1 — a region that claims cells claims ink.** For every region with `verdict == "asserted"` and
`cells > 0`: `tokens_asserted + tokens_escalated > 0`. Corpus-checked against § 1's sweep, which
is why the threshold is `> 0` and not a ratio: cbh books 54 for 13 cells and apple 6 for 3, so
cells and tokens are not proportional and any tighter form would be a tuned constant.

**I2 — an asserted region that carries a table in the graph names it.** For every region with
`verdict == "asserted"` and `cells > 0`: `table_uri is not None`, and that URI is typed in the
page graph. This is D1's oracle and it holds today for 12 of 14 corpus record tables.

**I3 — no band books ink it does not hold.** O1's existing invariant, extended to reach this
shape: pair report to band **by band index** over `range(len(bands))` rather than requiring equal
lengths, leaving the appended grid region (index `len(bands)`, the contract `document.py:1648`
already relies on) to I1 and I2. State it once here; the implementer cites this section rather
than re-deriving it.

**The fixture.** A synthetic page that asserts nothing, escalates nothing, and derives a grid —
the exact gate at `:1351`. This removes the n=1 dependency: unlike [[R213]]'s colour discriminator
the trigger is structural, so CI can hold it without the corpus.

**§8 class.** PROCEDURAL, and irreducible: D2 is exact counting over a ledger of integer marks and
D1 is binding a returned identifier. No threshold, no tolerance, no reading judgment.

## 5. Falsification, mandatory per task

Per CLAUDE.md rule 4, each task reports a `## FALSIFICATION` block. For this subject the
injections are named in advance, because a test that passes with its subject deleted is exactly
what O1's history warns about:

- **D2:** restore the original statement order at the branch. The new I3/I1 test must FAIL,
  naming the band that booked 285 against 6 words.
- **D1:** drop the captured URI again. The I2 test must FAIL on both ons pages.
- **The shape guard:** run the extended O1 against a *band-only* page (any graincorp page) and
  show it still passes — the extension must not weaken what O1 already pins.

## 6. What this loop does NOT do

Read this section before writing any test, per rule 5.

- **It does not author ONS's `cor:contract` / `cor:terms` / `cor:shapes`.** That is etkl:04 route
  step 1 and a loop of its own; nothing here parametrizes `test_grounding_where_contracted`.
- **It pins no floor and writes no adjudication.** The 2026-08-20 HOLD stands at loop close. A
  test asserting `cor:CompilesAbove` for this document contradicts this section.
- **It does not change any score.** Totals are preserved by both repairs; a test asserting that
  ONS's 0.9720 moves is a contradiction, not a finding.
- **It does not touch the `denom == 0 → 1.0` convention** that gives six zero-ink ONS pages a
  perfect page score. That is R72's settled ruling, and the document score is a global ink ratio
  (590/607), so those pages do not inflate it.
- **It does not close [[R202]]**, though it answers that row's open question — see § 7.

## 7. Residues

- **[[R224]] raised** — this spec's subject, with its measurement and the three blindnesses.
- **[[R202]] is ANSWERED and gets an amendment, not a closure.** That row asks what ons p7 band 16
  and p8 band 9 are, given they have no band at that index. They are **the datagrid fallback's
  appended region**, which by construction has no band: the branch appends one report beyond the
  band loop, at index `len(bands)`. The row's second half — a shared helper that pairs region to
  band by identity rather than by index — is untouched and keeps it open.
- **[[R213]] was RULED by the maintainer this session** (option (c): an invisible glyph is carried
  as a typed absence or a proposition, never as the value it hides and never dropped). Recorded in
  its row; **not implemented here** and not this loop's subject.
