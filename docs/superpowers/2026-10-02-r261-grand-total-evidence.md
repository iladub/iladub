# Evidence — R261 loop (b), Task 0: baseline and seams (2026-10-02)

**Serves:** prog:criterion:etkl:03 — ag-trade/cbh-stem-2026-08-03.pdf: this document compiles via
`compile_document` to `cor:CompilesAbove` with a pinned `cor:scoreFloor`, under a `cor:adjudication`
whose rationale accepts that score — not one that holds it. Loop (b) is attempting to bind cbh's
grand total `1,951,264` as a total-of-totals `PrintedTotal`.

**Topic:** r261-totals-family · **Date:** 2026-10-02 · **Branch:** `r261-grand-total` · **HEAD
measured:** `019b0ed`.

**Doc impact: none.** Measurement only; no `src/` change, no vocabulary or published term changes.

Plan: `docs/superpowers/plans/2026-10-02-r261-grand-total.md` (§§ "Measured seams", "Decisions
this plan takes where the spec is silent"). Task brief:
`.superpowers/sdd/2026-10-02-r261-grand-total/task-0-brief.md`.

This task is MEASUREMENT ONLY: no `src/` change. Three scratch scripts were written and run from
the scratchpad directory (not committed, per the prior loop's § 3 convention — a diagnostic over a
committed compile, not a committed instrument itself): `r261_task0_d1_cbh.py`,
`r261_task0_d1_fixture.py`, `r261_task0_step4_box_sources.py`.

---

## § 0. Step 1 — whole-corpus canonical-hash baseline (Task 7's "before")

Instrument: `scripts/r261_baseline.py --baseline` (unmodified, same instrument the loop (a)
evidence used), run serially, nothing else compiling at the same time.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python scripts/r261_baseline.py --baseline
```

Output:

| document | score | triples | sha256(canonical NT) |
|---|---|---|---|
| cbh-stem-2026-08-03 | 0.9106957424714434 | 13624 | `8ab724dd0efb124ff22f70ad2829800e0f85ca09dcab5accf2ac9affc2bd479e` |
| graincorp-capacity-2026-08-04 | 1.0 | 5859 | `4a7ffe8598fdb5d2b69f8e98cb228f85ea254132a62c2565ff4b1f0532984f68` |
| graincorp-stem-2026-07-31 | 0.9995511669658886 | 32422 | `96436660c468a30fc92a7c14af95e8d25dc4dd1bf8b71054c7dc1e616bb3375f` |
| apple-fy2026q3-statements | 0.9418604651162791 | 6255 | `f8c56e57e59947631d27def1caedaf6591683965af67abbd9dd3e01aeaee8bfc` |
| bfs-population-bilan-2023 | 0.9021428571428571 | 16778 | `4a176ec3138f99cbcd61db4c736a4fb834ba226e2d6e0aeea5d1616c358a225a` |
| ons-index-of-services-2026-02 | 0.8684895833333334 | 12454 | `4847d19fbd326488078653dbe1373d6f4d9634359b869f8b77eb6c319b336c08` |
| who-wfa-boys-zscore-0-5 | 0.9962779156327544 | 12274 | `7931db4b52d368bf32338c5e6773e3c47f79e33919b948e6ea2dd8c7fe41ea18` |

**Byte-identical to loop (a)'s own "after" baseline** (`docs/superpowers/2026-10-01-r261-totals-family-evidence.md`
§ 7.1, measured at `8cf306e`): every score, triple count and sha256 matches across all 7 rows. The
corpus has not moved between loop (a)'s close and this loop's Task 0 — the correct "before" for
this loop's Task 7 C2 diff is therefore identical to loop (a)'s "after".

---

## § 0.1 D1 on cbh's r2 pass (Step 2)

D1 (plan § "Decisions", `D1`): an operand's table band is the unique `j` with
`reports[j].table_uri == t`, where `t` is the operand `PrintedTotal`'s `tab:totalOf` object. Zero
or several such `j` ⇒ no claim (mirrors ruling R3).

**Instrument:** `r261_task0_d1_cbh.py` (scratchpad, not committed). Monkeypatches
`iladub.etkl.document.compile_tables` — the **module-level name** `document.py` binds via `from
.compile import compile_tables` (measured: `src/iladub/etkl/document.py:111`), not
`iladub.etkl.compile.compile_tables` itself, since patching the latter would not reach
`document.py`'s already-bound reference — to capture the one call whose `doc_uri` ends in `/r2`
for page 0 (the section-repair pass-2 compile Loop Q runs, `document.py:1579-1584`). Then runs the
whole `compile_document` with the **recorded readers** (`BAML_LIVE` and `ILADUB_RECORD_READINGS`
both unset — no API calls; the recorded JSON files under `readings/printed_total/` already cover
cbh's four port totals). Over the captured `CompilationReport`: for every `(pt, t)` in
`g2.subject_objects(TAB.totalOf)`, lists every `j` with `rep2.regions[j].table_uri == t`.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python \
  /private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/001554b5-6d54-4e42-831b-fe6ba897a981/scratchpad/r261_task0_d1_cbh.py
```

Output (full `rep2.regions` dump, then the four pairs):

```
captured r2 compile_tables call, doc_uri=https://example.org/etkl/doc/p0/r2
rep2.regions: 12 bands
  band 0: kind=RegionKind.NON_TABLE verdict=ignored table_uri=None
  band 1: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable1
  band 2: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 3: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable3
  band 4: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 5: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable5
  band 6: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 7: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable7
  band 8: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 9: kind=RegionKind.UNSUPPORTED_TABLE verdict=escalated table_uri=None
  band 10: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=.../r2#table10
  band 11: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=.../r2#table11

4 tab:PrintedTotal -> tab:totalOf pairs in rep2.graph
  #printedtotal2-l0 (cellText=374,904) -> totalOf #htable1 -> j=[1]
  #printedtotal4-l0 (cellText=737,289) -> totalOf #htable3 -> j=[3]
  #printedtotal6-l0 (cellText=660,363) -> totalOf #htable5 -> j=[5]
  #printedtotal8-l0 (cellText=178,708) -> totalOf #htable7 -> j=[7]
```

**Result: exactly one `j` each, `{1, 3, 5, 7}` — matches the brief's expectation exactly.** D1
needs no review before Task 4 on this corpus.

---

## § 0.2 D1 on the fixture (Step 3)

Same measurement over `tests.etkl.fixtures.printed_total_pdf` with an **always-yes table-level
reader** (`iladub.etkl.printedtotal.default_reader` monkeypatched to a reader whose `ask` always
returns `PrintedTotalReading(answer="yes")`, mirroring `tests/etkl/test_printed_total.py`'s
`_Reader`/`_compile` pattern — no network touched, no `BAML_LIVE`/`ILADUB_RECORD_READINGS`/
`ANTHROPIC_API_KEY` needed since the reader is fully faked). The fixture is a single page, so this
calls `compile_tables(pdf_path, 0, validate_shapes=False)` directly — no `compile_document`/Loop Q
needed (table and band index coincide here; no grid-donation path is exercised).

**Instrument:** `r261_task0_d1_fixture.py` (scratchpad, not committed).

```
PYTHONPATH="$PWD" .venv/bin/python \
  /private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/001554b5-6d54-4e42-831b-fe6ba897a981/scratchpad/r261_task0_d1_fixture.py
```

Output:

```
rep.regions: 5 bands
  band 0: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=#table0
  band 1: kind=RegionKind.UNSUPPORTED_TABLE verdict=escalated table_uri=None
  band 2: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=#table2
  band 3: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 4: kind=RegionKind.NON_TABLE verdict=ignored table_uri=None

2 tab:PrintedTotal -> tab:totalOf pairs
  #printedtotal1-l0 (cellText=5,100) -> totalOf #table0 -> j=[0]
  #printedtotal3-l0 (cellText=2,700) -> totalOf #table2 -> j=[2]
```

**Result: `#table0 → 0`, `#table2 → 2` — matches the brief's expectation exactly.** The
grand-total line (`7,800`, band 4) never produces a `PrintedTotal` here (total-of-totals binding
was dropped by controller ruling R4 in loop (a); band 4 is `ignored`, carrying no claim), so only
the two table-level totals appear in the `tab:totalOf` pairs, as expected.

---

## § 0.3 Step 4 — does a port-total word supply an extremal coordinate of the probe's derived box?

**Instrument:** `r261_task0_step4_box_sources.py` (scratchpad, not committed; `scripts/
r261_grand_total_role_probe.py` is evidence and was not amended, per the plan's N11). Re-implements
`derived_box` (`scripts/r261_grand_total_role_probe.py:71-94`) line-for-line, additionally tagging
every word (and each operand table band's `.top`, each total line's `.bottom`) with its origin —
one of the four port-total table bands, one of the four port-total lines themselves, or the
grand-total line — then reports, for each of x0/y0/x1/y1, which origin supplies the raw (pre
±4 pt padding, pre page-clamp) extremal value. No API call: the script exits right after printing
the box and its sources.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python \
  /private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/001554b5-6d54-4e42-831b-fe6ba897a981/scratchpad/r261_task0_step4_box_sources.py
```

Output:

```
operand 374,904: table band 1, 13 lines
operand 737,289: table band 3, 19 lines
operand 660,363: table band 5, 17 lines
operand 178,708: table band 7, 8 lines

--- derived box (post +/-4pt padding, page-clamped): [45.68, 101.44, 1147.886, 693.46] ---
  x0: raw=49.68 supplied by: table band 1 (operand 374,904's table), word 'VNA #'
  y0: raw=105.43999999999994 supplied by: table band 1 (operand 374,904's table) .top
  x1: raw=1143.8860000000002 supplied by: table band 1 (operand 374,904's table), word 'Time Loading'
  y1: raw=689.4599999999999 supplied by: grand-total line '1,951,264' .bottom
```

**Finding: no extremal coordinate is supplied by a port-total word (a port-total's own line).**
All three of x0/y0/x1 come from **table band 1's own cell words** (the first operand's table —
`#htable1`, un-carved, its own full-precision pdfplumber word geometry) and y1 comes from the
**grand-total line's own word** (`1,951,264`, not a `PrintedTotal` in production per loop (a)'s
ruling R4 — it stays an escalated band, so its extent is never passed through N4's 2 dp rounding
either). None of the four port-total LINES (`374,904`/`737,289`/`660,363`/`178,708` themselves, as
opposed to their table bands) supplies any of the four extremal coordinates.

**Consequence for Task 6 Step 3 (recorded per the brief, as a finding — not a tolerance).** N4
(plan § "Measured seams") observes that an operand total band is carved by the time the grand
total is reached, so its extent survives in production only via its `PrintedTotal`'s
`tab:hasBBox`, rounded to 2 dp (`holon.py:684-690`, `Decimal(str(round(word.x0, 2)))`) — a
potential < 0.01 pt divergence between the probe's full-precision box and a production box built
from rounded bboxes, **if** a port-total word supplied an extremal coordinate. **It measurably does
not, for cbh's current geometry**: the box's bounds are pinned by band 1's own (un-carved,
full-precision) table-cell words on three sides and by the grand-total line's own (also
full-precision — it is never emitted as a `PrintedTotal`, so N4's rounding never touches it) word
on the fourth. **The 2 dp-rounding concern N4 raises is therefore moot for Task 6's crop on this
document**: a production box built the same way (operand table bands' words + the grand-total
line, no port-total `PrintedTotal` bboxes contributing an extremal corner) would coincide with the
probe's box exactly, not merely to within 0.01 pt. This is recorded here as the measured fact
Task 6 Step 3 should re-check against its own production-box construction, not assumed to
generalize to a different document's geometry.

---

## § 0.4 Commands run, in order (corpus-runs-are-serial; checked clear before each)

```
# Step 1
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python scripts/r261_baseline.py --baseline

# Step 3 (fixture — no corpus compile, run first since it carries no corpus-serial constraint)
PYTHONPATH="$PWD" .venv/bin/python <scratchpad>/r261_task0_d1_fixture.py

# Step 2 (cbh r2 pass — corpus compile, run alone)
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python <scratchpad>/r261_task0_d1_cbh.py

# Step 4 (derived-box sources — single compile, run alone)
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python <scratchpad>/r261_task0_step4_box_sources.py
```

`pgrep -fl "compile_document\|r261_"` was checked clear immediately before Steps 2 and 4; macOS has
no `timeout` and none was used. `BAML_LIVE` and `ILADUB_RECORD_READINGS` were unset throughout
(confirmed by the `env -u` prefix on every corpus-touching command); Step 3's fixture reader is
fully faked, so no `ANTHROPIC_API_KEY` was read or needed for any command in this task — no API
call was made.

---

## § 0.5 Concerns for Task 4 review

None. Both D1 checks (cbh, the fixture) produced exactly the expected mapping with no ties, no
misses, and no second finding beyond the box-source observation in § 0.3, which is itself scoped
and handed to Task 6 Step 3 as instructed, not treated as a defect in D1 or in this task.
