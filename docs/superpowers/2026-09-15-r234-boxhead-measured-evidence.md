# Evidence — the boxhead measurement was run: the reader DOES split it, and R234's premise is refuted

**Serves:** prog:criterion:etkl:04 — ONS. The criterion's subject is column identity, and this
measures what actually stands between ons p4's table and an honest assertion.

**Date:** 2026-09-15. **Tree:** branch `r234-boxhead-measured`, cut from `main` at `05ac7cf`.
**No shipped file was edited. No behaviour changed.** Measurement only.

**Doc impact: none.**

The ordered action was the measurement in [[R234]]'s closing column, restated as step 1 of
`2026-09-15-both-ends-walk-refuted-handoff.md` § 9: *with `ons p4 band 0` cut `(L,T)=(2,1)`, does
`header_body_split` return a split at all, and do the four header lines yield 6 recoverable
labels?* It was run before anything was written or built, as ordered.

**It came back a THIRD way** — neither the "returns a split → go build" branch nor the "abstains →
different problem, hand back" branch the order anticipated.

---

## 1. The two ordered questions, answered

All figures below are from `corpus/gov-stats/ons-index-of-services-2026-02.pdf`,
`page_bands(PDF, 4)[0]`, cut `(L,T)=(2,1)` — i.e. `band.lines[2:-1]`, 32 lines → **29 lines, 213
words**. The cut was proved applied by dumping the cut band's own lines before any verdict was
read (§ 6).

**Q1 — does `header_body_split` return a split at all? NO ABSTENTION. It returns `2`.**

```
infer_leaf_grid   -> ncols = 6 ;  header_body_split -> 2
recover_leaf_grid -> ncols = 6 ;  header_body_split -> 2
```

Both grids agree, so the circularity [[R232]] § 8d hit (Option B: `header_body_split` returns
`None` at `ncols=1`) **does not occur at `(2,1)`**. That much of [[R234]]'s worry is settled: the
starting condition really did change, and the splitter really does answer.

**Q2 — do the four header lines yield 6 recoverable labels? SIX LABELS, NONE NUMERIC — but
TRUNCATED, and only two of the four boxhead lines are typed header.**

```
header_rows_of -> 2 wrapped header rows
  lvl 0: 4 cells  ['Sections G & I -', 'Sections H & J -', 'Sections K to N', 'Sections O to T']
  lvl 1: 6 cells  ['Date', 'IoS', 'Distribution,', 'Transport,', '- Business', '- Government']
infer_header_tree -> 10 nodes, 6 at the deepest level
LEAF LABELS: ['Date', 'IoS', 'Distribution,', 'Transport,', '- Business', '- Government']
any leaf numeric? []
```

So the six labels are non-numeric — this is **not** a fresh [[R166]] instance, unlike the walk's
`Jan 2024 / -0.1 / …`. But every multi-word label is a **wrap fragment**: `Distribution,` is the
first line of *"Distribution, Hotels and Restaurants"*, `Transport,` of *"Transport, Storage and
Communications"*, and so on. The two remaining boxhead lines are typed **body**, and become
logical rows 0 and 1 of 27:

```
logical_rows -> 27 rows
  row0  'Hotels and'   'Storage and'   'Services and'  'and other'      <- boxhead line 3
  row1  'Restaurants'  'Communications' 'Finances'     'services'       <- boxhead line 4
  row2  'Jan 2024'  -0.1  -0.3  0.2  0.1  -0.2                          <- the real first data row
```

## 2. What [[R234]] says, and why it is REFUTED as stated

The row asserts: *"the header reader cannot map a 4-line, 18-word boxhead onto 6 columns."*

**It maps it onto 6 columns.** `ncols=6`, six leaf nodes, one per column, non-numeric, and the
tree passes its own centering oracle. What the reader actually does is read **2 of the 4** boxhead
lines and truncate every spanning label — a different defect, with a different remedy, in a
different module from the one the row points at.

The row's `UNSUPPORTED_TABLE / 'header has 18 words but 6 columns'` figure is **reproduced and is
not the operative verdict**. That string comes from `regions.classify` (`regions.py:96`), the
flat-table classifier, which counts `band.lines[0].words` against `grid.ncols`. It is the reason
the band leaves the *record-table* path; it is **not** why the table fails to assert. The
hierarchical path is the one that decides, and it gets much further than the row implies.

## 3. The measured causal chain — where it actually dies

```
classify_hierarchical(band)        -> HierRegion  (NOT None: body_line=2, ncols=6, 10 nodes)
merge_tiling_ok(tree, grid)        -> True
   => compile.py:1277 gates on `not merge_tiling_ok(...)`, so this is FALSE
   => the NEURAL row-role branch (compile.py:1288 resolve_header_row_roles) IS NEVER ENTERED
   => falls through to the plain-hierarchical membrane backstop (compile.py:1315)
assert_hier_region(...)            -> n = 0
   region_round_trips(region, band) -> False  => ROUND_TRIP_FAIL, escalate, return 0
region_tiles(scratch)              -> None (never consulted; n == 0)
   => the band ESCALATES.
```

**The lockout is the finding.** `rowrole.build_row_reading` is precisely the code that composes a
wrapped label top-to-bottom — its own docstring (`rowrole.py:85`) gives *"'Date of Grain' +
'Loading' + …"* as the worked case — and `header_rows_of`'s KNOWN LIMIT note
(`headers.py:412-420`) names that NEURAL proposer as the designated remedy for wrap-continuation
rows. **It cannot fire here.** Its gate is a *tiling failure*, and the truncated reading does not
fail to tile: it is centered, non-overlapping, one leaf per column — self-consistently wrong.

`merge_tiling_ok` returning `True` on a truncated header is therefore not a bug in that oracle. It
is an oracle answering the question it was asked (*is this tree centered and non-overlapping?*)
and being read as if it had answered a different one (*is this tree the author's header?*).

## 4. The round-trip failure is TWO WORDS, and they are named

`region_round_trips` requires every word to sit in **exactly one** slot — a header line or a body
row, never both, never neither. Re-running its own gate word by word over all 213 words:

```
body_line=2   header_tops=[59.4, 71.4, 77.4]   win=3.0
words failing the exactly-one gate: 2
   line  1             'Date'  header_hits=1 row_hits=1
   line  1              'IoS'  header_hits=1 row_hits=1
```

**2 words of 213.** The stub labels `Date` and `IoS` are set 6 pt lower than the four spanning
labels beside them (`top` 77.4 against 71.4), so they are simultaneously within `win` of a header
top **and** inside the first body row's padded extent. The whole 25×6 table is refused on the
vertical placement of two stub words — and those two words are only ambiguous *because* the
boxhead's last two lines were typed as body rows in the first place.

## 5. CORRECTED IN-LOOP — the wrap gate IS the mechanism, and it fires at exactly equal pitch

**This section originally claimed the documented limit was absent. That was wrong twice, and the
correction is the finding.** It is corrected in place because the loop is not closed (PR #229 open,
CI pending); nothing here was ever on `main`.

**Error 1 — the wrong threshold.** `header_rows_of`'s KNOWN LIMIT (`headers.py:412-420`) names the
gate as `gap < lead`. **That gate was retired** by [[R208]] (`0133362`, 2026-09-10): the operative
gate is now `gap < tightest_row_gap`, the *minimum* gap over the band's CERTAIN pairs
(`cells.py`, `group_wrapped`). The docstring is stale — raised as [[R235]].

**Error 2 — the wrong gaps.** `group_wrapped` measures **top-to-top** (`tops[i+1] - tops[i]`). The
figures first published here (`1.92`, `-4.08`, `1.92` against a `lead` of `10.32`) were
bottom-to-top, a different statistic, and the `-4.08` is the tell: a negative "gap" is what you get
subtracting a *composite* line's bottom, not a real overlap. The correct measurement:

```
TOP-TO-TOP lead=20.64   hrules=0
certain pairs: 27 of 28   tightest_row_gap=12.00   (certified by pair j=1)

  j=1 gap= 12.00 <tight? False | cols_j=[0..5] anchor=[2,3,4,5] | subset? False fewer? False | CERTAIN
  j=2 gap= 12.00 <tight? False | cols_j=[2,3,4,5] anchor=[0..5] | subset? True  fewer? True  | candidate
  j=3 gap= 12.00 <tight? False | cols_j=[2,3,4,5] anchor=[2,3,4,5]| subset? True fewer? False | CERTAIN
  j=4 gap= 20.40 <tight? False | cols_j=[0..5] anchor=[2,3,4,5] | subset? False fewer? False | CERTAIN
```

**So the documented limit is PRESENT, not absent — in its exact stated form.** The genuine wrap
candidate is `j=2`: it passes condition 2 (`subset ✓`) and condition 3 (`fewer ✓`), so it is
structurally a wrap. It is refused **only** by the gap test, and by nothing at all: its gap is
`12.00` against a threshold of `12.00`, and `12.00 < 12.00` is false.

**The threshold is set by the boxhead itself.** `tightest_row_gap` is certified by pair `j=1` — the
boundary between the spanning row (`Sections G & I -…`, 4 columns) and the leaf row (`Date IoS…`,
6 columns). That pair is CERTAIN by construction because line 1 tiles *more* columns than its
anchor, so `partial_of` is false. The boxhead's own internal header/sub-header boundary therefore
publishes a 12.00 row gap, and the wrap continuations sit at exactly that same 12.00 pitch.

This is precisely the failure the stale docstring describes — *"the synthetic fixture uses uniform
12pt spacing — `12 < 12` is false"* — and precisely the residual [[R208]]'s own spec § 4 accepted as
HONEST LIMIT (b): *"At uniform pitch a noise floor remains."* **The AXIOM is behaving correctly by
its own design:** a gap indistinguishable from a certified row boundary *is* a row, evidence-positive
per CLAUDE.md § 8. It refuses to guess, which is right — and it means the composition can only come
from the NEURAL proposer, which § 3 shows is locked out. **The two findings compose: the AXIOM
correctly declines, and the NEURAL path that exists to take over cannot be reached.**

The wrap rows were therefore not absorbed:

```
group_wrapped -> 29 cell-rows for 29 lines        <- ZERO absorption
  row0 top= 59.45  4 cells  ['Sections G & I -', ...]
  row1 top= 77.45  6 cells  ['Date', 'IoS', 'Distribution,', ...]
  row2 top= 83.45  4 cells  ['Hotels and', 'Storage and', 'Services and', 'and other']
  row3 top= 95.45  4 cells  ['Restaurants', 'Communications', 'Finances', 'services']
```

**So the split and the grouping are two independent failures, and this matters for any remedy.**
`group_wrapped` absorbed nothing at all, so fixing `header_body_split` alone would not recover the
labels: with `split=4`, `header_rows_of` would keep rows 0-3 and `_tree_from_rows` would take
**row3** (`Restaurants / Communications / Finances / services`, 4 cells) as the leaf row — four
labels for six columns, wrong in a new way. The labels are only recoverable by **composing** rows
1-3 top-to-bottom, which is `build_row_reading`'s job, which § 3 shows is locked out.

**Why `group_wrapped` absorbed nothing is MEASURED, above:** the sole refusal is `12.00 < 12.00`
being false, against a threshold the boxhead's own first pair certifies. No other condition failed.

## 6. Method, and the guard carried from the previous loop

The previous loop's lesson — *a null result is not self-validating* — was applied before any
verdict was read: the cut band's first six lines and its last line were dumped and checked against
the baseline band's, so "the cut applied and the reader still failed" is distinguished from "the
cut never applied".

```
=== BASELINE band: 32 lines, 252 words
  [0] Table 1: Revisions to month-on-month growth for Index of Services and its sectors
  [1] February 2026 release compared with January 2026 release, percentage growth, ...
  [2] Sections G & I - Sections H & J - Sections K to N Sections O to T
=== CUT (L,T)=(2,1): 29 lines, 213 words
  [0] Sections G & I - Sections H & J - Sections K to N Sections O to T   <- was [2]
  [last] Jan 2026 0.1 0.3 0.2 -0.1 0.3                                     <- Source: line gone
```

This loop's probes call the real functions directly on a `dataclasses.replace`'d band; **nothing
was patched into a module global**, so the wrong-seam error the previous loop recorded
(`compile.page_bands` vs `document.page_bands`) cannot arise here. The trade-off is the opposite
one and is stated plainly: **these figures are for the band in isolation, not for a compile run**,
so the document-scope consequence of `(2,1)` is inherited from the previous loop's measurement and
was not re-derived.

The probes are throwaway and were **not committed**. Everything above re-runs from:
`page_bands(PDF, 4)[0]` → `lines[2:-1]` via `dataclasses.replace` (recomputing `top`/`bottom`) →
`recover_leaf_grid` / `infer_leaf_grid` → `header_body_split` → `header_rows_of` /
`infer_header_tree` → `classify_hierarchical` → `merge_tiling_ok` → `assert_hier_region` →
`region_round_trips`.

## 7. What this loop does NOT claim

- **It does not claim a remedy.** Whether the fix is the split, the grouping, the
  `merge_tiling_ok` gate, or a NEURAL proposal disposed by an oracle is a **§ 8 classification
  decision** that must be made before code, and [[R234]]'s row deliberately withholds it.
- **It does not claim this generalises.** Every figure is one band on one page of one document.
  Whether other documents carry stub labels set lower than their spanning siblings (§ 4's
  mechanism), or wrapped boxheads `group_wrapped` declines to absorb (§ 5), is **unmeasured** —
  and the previous loop's twin lesson (*a repair measured on one page is a hypothesis about a
  corpus*) applies directly.
- **It does not re-derive the document-scope score.** `0.7712418301 → 0.7522123894` and the
  `superseded` / 0-cells outcome are the previous loop's figures, inherited unchanged.
- **It does not explain `superseded`.** § 3 shows the band ESCALATES on its own; the previous
  loop measured region 0 as `superseded` with 0 cells at document scope. Those are consistent (the
  adoption ledger supersedes a touched band, `compile.py:1576`) but the link was **not traced**,
  and it was already listed as unverified in that loop's handoff.
- **It does not touch [[R166]].** The labels here are non-numeric, so this band is not a new
  instance of it.
