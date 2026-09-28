# Measurements: T2's first row, before spec § 10 (2026-09-28)

**Topic:** box-split · **Date:** 2026-09-28

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) stays XFAIL on T2 until § 10 is ruled and built.

**Doc impact: none.** This is evidence for spec § 10. No code or vocabulary changes here.

This answers the three facts that `2026-09-28-box-split-t3c-handoff.md` part 5 said were unmeasured.
It was measured on `box-split` at `1b4ab25`, and no tracked file was edited. The probe scripts live in
the session scratchpad (`t2/`, `ons/`), which is gitignored and not durable, so the outputs that carry
weight are quoted here.

## Next (typed)

- **Proposed, needs two maintainer rulings first** (§ 4 below): the headerless form, and the decider
  class. After that, author spec § 10.

## 1. The path that reads T2's row 0 as a header

This was measured by patching `rdflib.Graph.add` to print a stack on
`(…p0#table11, tab:hasHeaderNode, …)`, with one cbh compile.

```
document.py:1471 compile_document
 → compile.py:970 page_bands → boxsplit.split_band → _box_band → _build_ruled_band
 → compile.py:1026 classify(band) → classify-kind.rq → RecordTableKind (nhw=2, firstBad=None)
 → RECORD_TABLE branch: transposed=upright, looks_row_grouped=flat, the `else` assert path
 → compile.py:1284 assert_record_region → holon.py:194 (a HeaderNode per column), :205 (row 0 → LabelCell)
```

- **This is a positional default, not a reading.**
  - `classify-kind.rq` asks only whether line 0 has exactly `ncols` words, each inside its own column.
  - Every T2 row satisfies that: for example, `ESP[572.1,581.0] | 1 - 15 August[610.0,641.8]`.
  - `holon.py:187-194` then mints one level-0 `tab:HeaderNode` per column unconditionally, and
    `holon.py:205` makes `row == 0` the label row.
  - T1 takes the identical path. It is right only because its row 0 happens to be a header.
  - I verified this by reading `holon.py:181-207` at `1b4ab25`.
- **What is not involved:** `datagrid_adopt`, `boxhead`, `ruledroles`, `rowrole`, and
  `header_body_split`.
  - `header_body_split` does run on T2, from `document.py:328` and from `rowheaders.stub_data_split`,
    but it mints nothing.
  - No recorded reading is consulted for T2.

## 2. The ons boxhead reader (PR #271) does not fit

- **Its question presupposes a header.**
  - `baml_src/boxhead.baml:48-57` reads *"its header area, then its first rows of data"*.
  - `BoxheadReading` (`:33-40`) has no "no header" field.
  - None of the 5 recorded readings has an empty leaf list.
- **It cannot be reached from a box band.** It runs only in page-scope `datagrid_adopt`
  (`compile.py:1683-1703`), and on cbh p0 it ran on the 16-column page grid, not on T2.
- **`dispose_boxhead` (`boxhead.py:150-185`) refutes neither wrong answer.** It checks address space,
  total accounting and placement. Hand-built inputs showed:
  - T2's row 0 read as a header (wrong): **accepted**.
  - T1 read as having no header (wrong): **accepted**.

## 3. The O2 target state cannot be constructed as a RecordTable

`test_carriage.py`'s `_o2_two_tables` requires two `tab:RecordTable`s. `test_o2_t2_…` then requires
`len(hasHeaderNode) == 0` with 2 leaf columns. `tiling.region_tiles` refuses exactly that. I re-ran
this myself:

```
2 leaf cols, 0 header nodes -> False
2 leaf cols, 2 header nodes -> True
```

- **The shapes that fire:** `tab:CoverageShape` and `tab:UnambiguousAccessShape`
  (`vocab/shapes/tab-shapes.ttl`), both in `_TILING_SHAPE_IRIS`. The RECORD branch gates on
  `region_tiles` (`compile.py:1284-1285`), so a perfect "no header" decision would still escalate T2.
- **The spec's own words are weaker than the test.** Spec § 4 risk 1 says *"O2's '0 column labels on
  T2' is the check"*, while the test asserts 0 header nodes.
- **The one headerless form in `tab:` is no remedy.** `tab:GridColumn` is transient evidence, never
  asserted into a holon (`vocab/ontology/tab.ttl:47`).

## 4. Page evidence, and a census of it

**pdfplumber, cbh p0.**

- **Rules separate nothing.** Both boxes draw a 0.48pt rule under every row, and the rule under row 0
  is the same as the rest.
- **Fill and type separate T1 from T2.**
  - T1 row 0: a full-width pure-blue fill `(0,0,1)`, with all 46 chars `Calibri` 6.0 in white.
  - T1 rows 1–4 and all of T2: the stub is `Calibri-Bold` white on light blue, and the data is
    `Calibri` black.
  - T2's row 0 is identical to its row 1.

**Corpus census.** One document per process, serially.

- 13 `assert_record_region` tables survive into final graphs:
  - cbh: 2.
  - bfs p6: 9, of which 8 were donated.
  - who: 2.
- The test was "row 0 differs from row 1 by datatype family, font set, or fill". It came out as
  follows:

  | table | proxy evidence | row 0 is | abstaining would be |
  |---|---|---|---|
  | cbh p0 `#table11` (T2) | none | data | right |
  | who p0 `#table4`, who p1 `#table4` | none | data (INFERRED from text: `1: \| 1 \| 13 \| 0.0563…`) | right |
  | bfs p6 `#table2` | none | a real boxhead whose band has no body | **wrong** |
  | the other 9 | present | header | (not asked) |

  - The proxies are the probe's own definitions, not repo terms.
  - A row-0-versus-row-1 comparison cannot see a header band that has no body. That is its first
    refutation.

## 5. What this leaves for § 10

1. **Form.** A table the author drew with no boxhead has no admissible representation today. The
   options are:
   - **(a)** A RecordTable whose header nodes carry no label, with O2 aligned to the spec's own
     "0 column labels".
   - **(b)** A positive, decision-produced statement that the table has no boxhead, which exempts it
     from Coverage and UnambiguousAccess. This is a `tab:` vocabulary and shape change, so
     `Doc impact: increment`.
2. **Decider.** Header-vs-data is a reading judgement.
   - The style proxy is the one geometric attempt, and § 4 refutes it on bfs p6 `#table2`. So by the
     2026-09-17 ruling, the next decider is NEURAL.
   - **A candidate oracle, asymmetric and not yet measured as an oracle:** refuse a "row 0 is data"
     proposal when positive header evidence exists (row 0's style or datatype differs from the body).
     It refutes the wrong answer on T1 and cannot refute one on bfs p6 `#table2`.
   - Whether one-direction disposal is enough under "no oracle, no worker" is the question § 10 must
     answer.
