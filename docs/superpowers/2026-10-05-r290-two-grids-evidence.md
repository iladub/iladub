# Evidence + handoff: a page reads as many grids as it has tables (R290 closed); R265 still held, now on R291 (2026-10-05)

**Serves:** prog:criterion:etkl:03 — R265 is sequenced before R289, the named blocker on lifting cbh's hold.

**Topic:** r290-two-grids · **Date:** 2026-10-05

**Doc impact: none.**

Branch `r265-grouped-numbers` (draft PR #303) now carries R265 and R290 together. **R290's prediction
held:** bfs is back to 0.9021, and the other 6 documents are identical to the triple hash. **The PR
is still held**, for a different reason: R265 puts a token that is not on the page into the graph
(§ 2.4, raised as R291). Part 5 was written at about 125K working tokens. That is under the 150K
executing floor and over the 50K originating floor, so each action is graded.

## 5. Next concrete action (written first)

1. **PROPOSED: find where band formation produces the `Word` `20208` under R265's typing (R291), and
   fix it there.**
   - **Evidence (§ 2.4):** `band_text` joins words with a space, so the fused `Word` exists before
     the join.
   - **What may be wrong:** the cause was not located. The prediction is that it lies in a stage
     that consults `_cell_datatype` while forming a band's lines (the run-merge seam is the first
     suspect, because the band boundary also moved). A suspect is not a measurement.
   - **The oracle is wider than bfs p5:** a whole-corpus census showing that no `etkl:bandText`,
     cell or label carries a token absent from its page's `extract_words`. Run it on `4379fbe`
     first. If `main` already fails it, R291 is not R265's defect alone, and the census becomes
     the subject.
2. **ASSERTED: do not merge #303 until R291 is closed.** Under §7 a value that is not on the page
   outranks an unchanged score.
3. **ASSERTED: finish the local corpus sweep before merging #303, whatever R291's outcome.** The
   pins `P5_CELLS_WHEN_CARRIED = 496` (`tests/test_carriage.py:71`) and `grid[0].cells == 496`
   (`tests/etkl/test_run_merge_seam.py:466`) count ONE grid region and will read 270, because the
   cells are now split 270 + 226. Re-pin them from a run, not by arithmetic.

## 1. Goal

Make `datagrid` read every table on a page, so that R265's correct typing stops lowering bfs.

## 2. Findings

### 2.1 What changed (in the code; the tests run)

- `datagrid.derive_data_grids` runs `derive_data_grid` again over the lines no earlier grid
  admitted (`exclude=`), until no rectangle is admissible. A line another grid admitted is struck
  from each grid's refusals; otherwise `boxhead.header_block` would climb through the other
  table's body. No constant was added, and every grid passes the same G0–G8.
- `compile.py` adoption and fallback emit every grid. The first keeps `#p<n>-datagrid` and later
  grids are `-datagrid-2`, … . The ledger books the union of their lines.
  `RegionReport.supersedes` records, per grid, the bands that grid's own lines touched.
- `document.py` gives each grid its own admission verdict, and supersedes only that grid's bands.
- Gate classification: AXIOM. The definition is already "a maximal rectangle", and this
  applies it to the page instead of stopping at the first. Docstring in `derive_data_grids`.

### 2.2 Census before the code (measured, all 27 corpus pages, R265 applied)

Iterated re-seeding yields a second grid on **one** page: bfs p5, 19 rows × 12 columns, all
`Quantity`, rows 2005 … . No page yields a fragment grid, so the handoff's worry (two matching
footnote lines make a "recurring" signature) does not occur on this corpus.

### 2.3 The falsifier (run)

`scripts/corpus_verdict_snapshot.py` at `4379fbe` (worktree, corpus symlinked) against this tree,
then `corpus_snapshot_diff.py`:

```
bfs-population-bilan-2023      0.9021428571 -> 0.9021428571  triples  16778 ->  16846  CHANGED
    p5: score 0.9249 -> 0.9249   cells   496 ->   496   asserted   936 ->   936   escalated    76 ->    76
(apple, cbh, graincorp-capacity, graincorp-stem, ons, who)                          IDENTICAL
```

Per grid on bfs p5 (document compile, region reports):

| region | table | cells | supersedes | boxhead labels |
|---|---|---|---|---|
| 16 `#p5-datagrid` | cantons, 27 × 10 | 270 | bands 9–13 | 0 |
| 17 `#p5-datagrid-2` | years, 19 × 12 | 226 | bands 2–4 | 11 (the existing recording) |

The canton cells no longer wear the year table's 11 labels, as they did inside the old 46-row
grid. They wear none, because no boxhead reading has been recorded for a 10-column canton grid.
The year grid holds 226, not 228, cells: the 2015 row leaves columns 1 and 9 empty.

### 2.4 R265 fuses a year into the next number (measured; cause not located) → R291

R265's close condition asks for bfs p5's row-0 witness to be re-measured. On `4379fbe`, band 5
(row 0 `2020 | 8 606 033 …`) gives `witness=True`, the false witness R265 names. On this tree
**band 5 no longer exists in that form**: the page has 16 bands instead of 17, and band 5 has
absorbed the `Sources:` line, classifies `NON_TABLE`, and is `ignored`. Its carried text is one
triple:

```
<…/p5#ignored5> etkl:bandText "20208 606 033 85 914 … 0.75\n20218 670 300 89 644 …"
```

`20208` and `20218` are not on the page. `extract_words` holds `2020` and `8 606 033` apart,
and the year grid places them as two cells. The witness question therefore has no subject on
this tree, and R265 cannot close.

## 3. Decided, and where

- R290 is closed: `residues-closed.md` (row and closure evidence) and the `residues.md` index.
- R291 is raised and blocks R265: `residues-open.md` and the index. R265's index line says so.
- Keeping #303 held is an agent call, recorded only here. It applies §7 and the 2026-09-18 ruling.

## 4. Unverified or assumed

- **The local corpus sweep did not finish in-session.** It started per file with this tree's code,
  and had covered 18 of 235 files when this note was written. Its output was in the session
  scratchpad, which is not kept. Corpus pins counting a single p5 grid region will fail (part 5,
  item 3).
- `donation.py` still calls the single-grid `derive_data_grid` (the seed winner). On this corpus
  that changes nothing measured, because the snapshot is identical apart from bfs and bfs's page
  totals hold. It is not argued for a page where a band's line 0 sits in a later grid.
- R290's code was not measured on `main`'s typing alone (without R265).

## 2b. Where the primaries are

- Code: `src/iladub/etkl/datagrid.py` (`derive_data_grids`, `derive_data_grid(exclude=)`);
  `compile.py` (`RegionReport.supersedes`, the fallback and adoption branches); `document.py`
  (one admission per grid).
- Test: `tests/etkl/test_datagrid.py::test_a_page_with_two_tables_yields_two_grids_r290`, which is
  synthetic and runs in CI. It was falsified twice: with the re-seed removed it fails on
  `[(8, 9, 10, 11)]`, and with the refusal strip removed it fails on grid B refusing A's six rows.
- Probes (scratchpad, not kept): the re-seed census; the bfs p5 per-grid inspector; the row-0
  witness on both trees; the `20208` graph search. Each one is about 20 lines.
