# Evidence — box split, Task 0: baseline (2026-09-28)

**Serves:** prog:criterion:etkl:03 — cbh is not accepted while `#table9` fuses two side-by-side
tables; this evidence is the "before" state Task 5's C2/C3 controls diff against.

**Topic:** box-split · **Date:** 2026-09-28 · **Branch:** `box-split` · **HEAD measured:** `d5e07ca`
(`src/` unchanged since `6eb80ca`, the commit the spec was cut from).

**Doc impact: none.** Measurement only; no published term changes.

Plan: `docs/superpowers/plans/2026-09-28-box-split.md`, Task 0. Spec:
`docs/superpowers/specs/2026-09-28-box-split-design.md`.

---

## § 1. Baseline, recorded before any `src/` change

### 1.1 Step 1 — whole-corpus verdict snapshot (C2's "before")

Instrument: `scripts/corpus_verdict_snapshot.py`, run serially (nothing else running), one
process at a time, per the corpus-runs-are-serial constraint.

```
PYTHONPATH=src .venv/bin/python scripts/corpus_verdict_snapshot.py \
    internal/benchmarks/box-split-2026-09-28/before/run1
```

Output (`internal/benchmarks/box-split-2026-09-28/before/run1/*.json`, gitignored —
`internal/` never commits; this table is the durable record):

| document | score | triples | canonical sha256 (12 hex) |
|---|---|---|---|
| cbh-stem-2026-08-03 | 1.0 | 12839 | `ba056c0ed809` |
| graincorp-capacity-2026-08-04 | 1.0 | 5859 | `3b54f16194ca` |
| graincorp-stem-2026-07-31 | 0.9995511669658886 | 32422 | `496c315f2fcc` |
| apple-fy2026q3-statements | 0.9418604651162791 | 6255 | `1dd90f432c5e` |
| bfs-population-bilan-2023 | 0.9021428571428571 | 16736 | `4fd251c0228f` |
| ons-index-of-services-2026-02 | 0.8684895833333334 | 12440 | `8efa4def664e` |
| who-wfa-boys-zscore-0-5 | 0.9962779156327544 | 12292 | `7e6038064128` |

7 documents, matching `scripts/corpus_verdict_snapshot.py`'s `CORPUS.rglob("*.pdf")` population
(`corpus/ag-trade/*.pdf` x3, `corpus/financial`, `corpus/gov-stats` x2, `corpus/health`).

`scripts/corpus_snapshot_diff.py` exists and is the instrument Task 5 reuses:

```
PYTHONPATH=src .venv/bin/python scripts/corpus_snapshot_diff.py <before-dir> <after-dir>
```

It prints, per document, the score and canonical hash on both sides, and — only where they
differ — every page whose score, cells, adoption or region verdicts moved. Confirmed present
and confirmed the CLI form above by running it against the two runs below.

### 1.2 Ruling R1 — determinism NULL control

Per controller ruling: before trusting the hashes above for later comparison, a SECOND
whole-corpus snapshot was taken on the identical tree (nothing changed between the two runs —
`git status` was clean throughout) and diffed against the first with `corpus_snapshot_diff.py`:

```
PYTHONPATH=src .venv/bin/python scripts/corpus_verdict_snapshot.py \
    internal/benchmarks/box-split-2026-09-28/before/run2
PYTHONPATH=src .venv/bin/python scripts/corpus_snapshot_diff.py \
    internal/benchmarks/box-split-2026-09-28/before/run1 \
    internal/benchmarks/box-split-2026-09-28/before/run2
```

Output:

```
apple-fy2026q3-statements      0.9418604651 -> 0.9418604651  triples   6255 ->   6255  IDENTICAL
bfs-population-bilan-2023      0.9021428571 -> 0.9021428571  triples  16736 ->  16736  IDENTICAL
cbh-stem-2026-08-03            1.0000000000 -> 1.0000000000  triples  12839 ->  12839  IDENTICAL
graincorp-capacity-2026-08-04  1.0000000000 -> 1.0000000000  triples   5859 ->   5859  IDENTICAL
graincorp-stem-2026-07-31      0.9995511670 -> 0.9995511670  triples  32422 ->  32422  IDENTICAL
ons-index-of-services-2026-02  0.8684895833 -> 0.8684895833  triples  12440 ->  12440  IDENTICAL
who-wfa-boys-zscore-0-5        0.9962779156 -> 0.9962779156  triples  12292 ->  12292  IDENTICAL

0 of 7 documents changed
```

**7 of 7 documents IDENTICAL** across two independent processes on the identical tree — every
score, triple count, and canonical (blank-node-normalised, sorted-N-Triples) graph hash matches
exactly. Both runs completed end to end with no memory kill (each run ~7-9 min wall clock, run
serially, nothing else compiling concurrently). The hashes in 1.1 are therefore trustworthy as
Task 5's C2 "before": a hash that moves after the split moved because of the split, not because
of run-to-run nondeterminism. No nondeterministic triple was found (there was nothing to find).

### 1.3 Step 2 — cbh page-0 RegionReports (C3's "before")

Instrument: a one-off script (not shipped; the measurement is preserved as data, not as an
instrument) compiling cbh once and reading `rep.pages[0].regions` alongside a content-keyed
dump of every `tab:RecordTable`/`tab:HierarchicalTable` it asserts, via `tab:hasCell` /
`tab:atRow` / `tab:atColumn` / `tab:cellText` / `tab:hasHeaderNode` / `tab:coversRow` /
`tab:coversColumn` / `tab:hasLabel` (`src/iladub/etkl/holon.py:320-407` is the emission code
these properties come from). Full output saved at
`internal/benchmarks/box-split-2026-09-28/before/cbh-page0-content.json` (gitignored).

`rep.pages[0].regions` — 10 entries (band-by-band, index = the page's raw-band order):

| idx | kind | verdict | cells | reason | table_uri |
|---|---|---|---|---|---|
| 0 | NON_TABLE | ignored | 0 | fewer than 2 columns | — |
| 1 | UNSUPPORTED_TABLE (`tab:HierarchicalTable`) | asserted | 170 | — | `…/p0/r2#htable1` |
| 2 | NON_TABLE | ignored | 0 | fewer than 2 lines | — |
| 3 | UNSUPPORTED_TABLE (`tab:HierarchicalTable`) | asserted | 268 | — | `…/p0/r2#htable3` |
| 4 | NON_TABLE | ignored | 0 | fewer than 2 lines | — |
| 5 | UNSUPPORTED_TABLE (`tab:HierarchicalTable`) | asserted | 228 | — | `…/p0/r2#htable5` |
| 6 | NON_TABLE | ignored | 0 | fewer than 2 lines | — |
| 7 | UNSUPPORTED_TABLE (`tab:HierarchicalTable`) | asserted | 84 | — | `…/p0/r2#htable7` |
| 8 | NON_TABLE | ignored | 0 | fewer than 2 lines | — |
| 9 | RECORD_TABLE (`tab:RecordTable`) | asserted | 13 | — | `…/p0#table9` |

**Identifying "the four cbh rosters" (spec §4, §7.2).** Spec §7.2's `closed2.py` census says
"cbh p0 6 boxes closed True (4 rosters, 7-col box, 2-col box)". Re-running that probe
(`internal/benchmarks/cbh-boxes-2026-09-28/closed2.py`, still present locally, gitignored)
confirms exactly 6 closed boxes on cbh page 0:

```
bbox [37.9, 1151.6, 105.0, 199.6]  words_in 224   <- htable1 (region idx 1)
bbox [37.9, 1151.6, 241.1, 383.9]  words_in 331   <- htable3 (region idx 3)
bbox [37.9, 1151.6, 433.9, 560.6]  words_in 285   <- htable5 (region idx 5)
bbox [37.9, 1151.6, 602.1, 656.5]  words_in 126   <- htable7 (region idx 7)
bbox [37.9,  449.3, 689.6, 730.7]  words_in  37   <- table9's future T1 (7-col box)
bbox [543.4, 690.4, 689.6, 722.3]  words_in  21   <- table9's future T2 (2-col box)
```

So **the four rosters are regions 1/3/5/7** (`#htable1`, `#htable3`, `#htable5`, `#htable7`) —
each a single closed box of a 20-column vessel-loading manifest (`VNA #`, `Vessel Name`,
`Client`, `Commodity`, `ETA`/`ETA Time`, `ETC`/`ETC Time`, `ETD`/`ETD Time`, `Date Nom(inated)`,
`Date Loading`, `Time Nom(inated)`, `Time Loading`, `Loading Status`, `Other Port/s`, `+/- %`,
`Volume`), and **not #table9** — confirmed by their table-URI suffixes (1, 3, 5, 7, all < 9),
which is also why they are outside this loop's blast radius (§ 1.4: only N ≥ 9 shifts).

Cells by content, keyed by row identity (row URI, never label text — see the FALSIFICATION-
adjacent note below) with each row's cell texts left to right by x0:

| roster | table_uri | n cols | n rows | content sha256 (first 16 hex) |
|---|---|---|---|---|
| htable1 | `…/p0/r2#htable1` | 20 | 11 | `2312d93a98f271db` |
| htable3 | `…/p0/r2#htable3` | 20 | 17 | `2ab9c4eeb7977851` |
| htable5 | `…/p0/r2#htable5` | 20 | 15 | `478e3fc2457f7085` |
| htable7 | `…/p0/r2#htable7` | 20 | 6 | `91d0cf3cd58e17d5` |

The content hash is `sha256(json({"column_labels": <sorted set>, "rows": sorted(tuple(cell
texts) per row)}))` — order-independent over rows (today's row ORDER is a reading artifact,
not identity) but exact over the cell-text multiset per row. Task 5's C3 re-runs the same
script post-split and checks these four hashes are unchanged — the correct control, because it
compares by content, never by `#tableN`, and the four rosters are not renumbered by the split
either way (their table-URI suffixes 1/3/5/7 stay < 9).

**A first attempt at this extraction was WRONG and is recorded because the fix matters for
Task 4/5.** Keying the per-row dict by row-LABEL text (`row_label_by_leafrow.get(row, "<no
label>")`) collapsed all 11/17/15/6 rows of each roster into a single dict entry, because none
of these rows carry a `tab:coversRow`-linked label (the header tree's `coversRow` edges are
per-table and these four are flat 20-column manifests with no stub column) — every row's
"label" is the same empty sentinel, so a naive `dict[label] = cells` silently kept only the
LAST row and discarded the rest. `rows_out` above is keyed by the row's own URI (minted
`#htableN-rM`, M = the row's position in `mreg.leaf_rows`, `src/iladub/etkl/holon.py:453`),
never by label text, which is why the counts above (11/17/15/6) match `n_leaf_rows`. Task 4's
literals must do the same: identify a roster row by its OWN identity (URI suffix or ordinal),
never assume a label makes rows unique.

**cbh `#table9`, today's fused reading (band 9, pre-split — this is what Task 5 replaces).**
`RECORD_TABLE`, 3 "columns" (in fact the two title-bar texts plus the maintenance total,
misread as column headers), 9 "rows" (each raw text line of the 10-line band, one line — the
boxhead line pair — absorbed):

```
r1: "PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL" | "ALB 1 - 15 October"
r2: "ALB 129,183 APW1/ASW9/AWW1 27,023 3,345 1,293 160,845" | "ESP 1 - 15 August"
r3: "ESP 25,013 APW1/H2/ASW9 49,244 5,596 2,997 82,850" | "GER 24 August - 04 September"
r4: "GER 160,198 AWW1/ASW9/ANW1 3,406 2,667 4,460 170,731" | "KWI 1 - 15 September"
r5: "KWI 170,878 AUH2/APWN/APW1 33,996 76,603 3,418 284,895"
r6: "Note:"
r7: "Dates are based on Daily Transport capacity and assume total capacity is allocated to
     grade types required. Dates are subject to change and are only a guide."
r8: "The information provided is only an estimate based on information currently to hand and
     dates or order of loading are subject to change in accordance with the Export Accumulation"
r9: "Guidelines, Port Queue Policy and matters beyond the control of CBH. Reliance on, use or
     distribution of the information contained within is at the risk of the recipient."
```

This confirms the defect the spec names: the WHEAT/BARLEY/CANOLA/OTHER stock figures (T1) and
the maintenance-shutdown date ranges (T2) are interleaved line-by-line into one fused
`RecordTable`, and the Note block (r6-r9) is absorbed as data rows rather than left out of both
tables. The expected POST-split reading (T1 7 columns `PORT | WHEAT | MAIN WHEAT GRADES |
BARLEY | CANOLA | OTHER | TOTAL`, rows `ALB, ESP, GER, KWI`, `KWI x TOTAL = 284,895`; T2 2
columns x 4 rows, no boxhead) is already fixed by spec §1/§5 (O2) and is not re-derived here —
this section records only the BEFORE state.

### 1.4 Step 3 — band-index blast radius (spec § 4, risk 2)

**Method.** `grep -rnoE "#table[0-9]+"` (and, separately, `regions\[[0-9]+\]`, `table[0-9]+`
bareword, and `band[_ ]?(index)?[ _:=]*9`/`band9` prose forms) across `tests/`, `src/`,
`vocab/`, `docs/wiki/`, `readings/` (incl. `readings/boxhead/`), `scripts/`, and every
`docs/superpowers/**/*.md` (the register `residues*.md` plus every dated spec/plan/evidence/
handoff — the broader scope was needed to satisfy the control below, since the register alone
does not hold the `#table9` citation). `.claude/worktrees/**` is excluded — untracked
(`.git/info/exclude`), a stray local worktree, not part of this branch.

**Control** (must find `docs/superpowers/2026-09-28-cbh-one-is-not-a-compile.md`'s citation, or
— that file not existing on this branch, PR #282 unmerged here — the spec's own):

```
$ grep -rn "#table9" docs/superpowers/specs/2026-09-28-box-split-design.md
docs/superpowers/specs/2026-09-28-box-split-design.md:3:**Serves:** prog:criterion:etkl:03 — cbh is not accepted while `#table9` fuses two side-by-side
```

Found — the control passes.

**Every committed `#tableN` (N >= 9) reference to a cbh region**, repo-wide:

| file | lines | class |
|---|---|---|
| `docs/superpowers/2026-09-27-extent-boxhead-count-oracle-evidence.md` | 18 | Evidence (append-only) |
| `docs/superpowers/2026-09-27-extent-existing-oracles-evidence.md` | 13, 17, 56 | Evidence (append-only) |
| `docs/superpowers/2026-09-27-question-compiler-design-handoff.md` | 93 | Evidence (append-only) |
| `docs/superpowers/2026-09-28-box-split-plan-handoff.md` | 3 | Evidence (append-only) |
| `docs/superpowers/plans/2026-09-28-box-split.md` | 6, 97, 351, 389 | Evidence (append-only) |
| `docs/superpowers/specs/2026-09-28-box-split-design.md` | 3 | Evidence (append-only) |

**Every `#tableN` with N < 9 found in `tests/`/`src/`** (for completeness — none of these are
at risk, shown only because the same command surfaces them): `tests/test_ground_section_marker.py:31`
(`#table0`, synthetic `urn:doc` fixture, unrelated to cbh), `tests/etkl/test_section_repair.py:480,515-516`
(bare `regions[0]`/`regions[1]`, not cbh), `tests/etkl/test_kind_gate_is_load_bearing.py:166`
(`regions[2]`, not cbh), `tests/etkl/test_run_merge_seam.py:30-31,41` (`regions[2]`/`#mtable2`, not
cbh), `src/iladub/etkl/document.py:276,1715` and `src/iladub/etkl/compile.py:888` (`#table0`/`#table6`
in docstrings, synthetic examples, not cbh). `tests/etkl/test_grid_donation_seam.py:43` has
`regions[10]`/`regions[3]`/`regions[7]` — checked and confirmed **bfs page 6**, not cbh
(`BFS = ".../bfs-population-bilan-2023.pdf"`, line 15); bfs is untouched by this loop's touch
bound (R-c) and unaffected by the split regardless.

**Prose `band 9`/`band9` references** (the RAW page-0 band, not a `#tableN`/`regions[N]` index —
this descriptor is assigned during band DETECTION, before the split runs, and does not move:
band 9 is still band 9 whether it compiles to one fused table or two split ones) appear in
several `docs/superpowers/**` evidence files and **one register row**
(`docs/superpowers/residues-open.md:119`, `docs/superpowers/residues.md:327,337,373`, both
citing "cbh p0 band 9" in the R211/span-donation history) and **one wiki page**
(`docs/wiki/concepts/neurosymbolic-exemplars.md:130`, "band 9 (a differently-shaped table, not a
repeated section) correctly abstains"). None of these name a `#tableN`/`regions[N]` index and
none are re-keyed by this loop: they describe the physical band, which this split does not
renumber.

**Verdict: zero live (test/src/vocab/wiki/readings/scripts/register) references to a cbh region
by index with N >= 9.** Every citation at risk of the split's +2 shift is confined to
`docs/superpowers/**` (Evidence class, append-only per CLAUDE.md § Documentation governance —
never re-keyed regardless of what this loop does). This loop is the first to mint a live
`#table9`-successor reference (Task 4's test literals); there is nothing existing to migrate.

## FALSIFICATION

The enumeration's completeness rests on the control finding a real citation and the same
command finding nothing for a token that was never written. Both checked:

```
$ grep -rn "#table9" docs/superpowers/specs/2026-09-28-box-split-design.md
docs/superpowers/specs/2026-09-28-box-split-design.md:3:**Serves:** prog:criterion:etkl:03 — cbh is not accepted while `#table9` fuses two side-by-side
    (found — 1 hit)

$ grep -rn "#table999" tests/ src/ vocab/ docs/wiki/ readings/ scripts/ docs/superpowers/
    (exit 1 — no hit, the null)
```

The same `grep -rn` form finds the real citation and returns nothing for a deliberately absent
one, which is what makes the "zero live references" verdict above a measurement rather than an
assumption that the search terms happened not to match.

## § 2. AMENDMENT (2026-09-28, fix round 1) — the census generalised past `#tableN`/`regions[N]`

**§ 1.4's "zero live references" verdict was WRONG.** Task 0's review found a Critical finding:
`tests/etkl/test_typing_equiv.py:16-44` is a live, index-KEYED reference to cbh raw band 9 that
`grep -rnoE "#table[0-9]+"` structurally cannot catch, because it is not a `#tableN` citation at
all — it is a **positional list literal**. `EXPECTED_VERDICTS["cbh"]` is a 10-element list;
`test_band_verdicts_are_recorded_and_stable` calls `page_bands(path, 0)` directly and asserts the
full ordered list equals this literal by `==`. List index 9 is exactly cbh page-0 band 9's
pre-split verdict tuple. **This section does not rewrite § 1.4 (Evidence is append-only per
CLAUDE.md § Documentation governance) — it corrects the verdict here, in place.**

### 2.1 The corrected method

§ 1.4's `grep` census answers "does anything cite cbh by `#tableN`/`regions[N]` string form" and
nothing else — it is blind to any reference that is positional *by construction* (a Python list
whose INDEX is never written as a literal `9` anywhere in the source) or count-based (a `len(...)`
over `page_bands`'/`compile_tables`'/`compile_document`'s output). The corrected method:

1. **Find every file that could possibly be affected** — every test/script/reading referencing
   the cbh corpus path or ENTRIES key, case-insensitively: `grep -rlni "cbh" tests/ scripts/
   readings/`. 39 files matched (11 in `scripts/`, 28 in `tests/`+`readings/`'s parent).
2. **Narrow to files that actually run cbh page 0 through a band/region producer**
   (`page_bands`, `compile_tables`, `compile_page`, or `compile_document` called on the cbh
   corpus PDF specifically — not a synthetic fixture, not a docstring mention, not the "CBH" demo
   *contract* namespace used by `test_cbh_contract.py`/`test_split_key_naming.py`, neither of
   which compiles the corpus PDF at all). Read every candidate file's actual test bodies (not
   just its `grep` hit line) to make this call — a file mentioning "cbh" in a comment or using a
   different document as its fixture (`test_membrane_health.py`'s `bfs_report`,
   `test_escalation_wiring.py`'s synthetic/`APPLE` fixtures, `test_grounding.py`'s synthetic
   `ground_concept` calls) is excluded here, explicitly, having been checked rather than assumed
   absent.
3. **Within each surviving file, find every assertion that is positional or count-based over the
   bands/regions that call returns**: list/tuple equality against a literal (`==`), `len(...)`
   (over `page_bands(...)`, `rep.regions`, `rep.repaired_bands`, `rep.chains`), `[i]` indexing,
   `zip` against an expected sequence, a per-region/per-band ordinal loop, or a snapshot keyed by
   ordinal. A test that instead FILTERS regions by a property (`verdict == "asserted"`) and
   asserts something about the filtered population, with no ordinal/count tying it to band 9
   specifically, is not in this class — `enumerate()` alone does not make a loop positional; what
   matters is whether the ASSERTION depends on band 9's ordinal position or on a count that
   includes band 9's contribution.

### 2.2 Control

The method must find `test_typing_equiv.py`'s `EXPECTED_VERDICTS["cbh"]` — it does, by direct
inspection (step 2/3 above are a reading method, not a grep pattern, so the "control" here is
that the method's own worked application surfaces the exact finding the review reported):

```
tests/etkl/test_typing_equiv.py:36    "cbh": [
tests/etkl/test_typing_equiv.py:38-44     8 more (NON_TABLE, None, None, None) elements
tests/etkl/test_typing_equiv.py:53         ("RECORD_TABLE", 1, False, None),   ]   <- index 9
tests/etkl/test_typing_equiv.py:103   def test_band_verdicts_are_recorded_and_stable(name, path):
tests/etkl/test_typing_equiv.py:117       assert verdicts == EXPECTED_VERDICTS[name], (...)
```

Found — the control passes, and this is the SAME finding the review reported verbatim.

### 2.3 The corrected list — every live positional/count-based cbh page-0 dependent

| file:line | what it runs | what it asserts | at risk (N>=9 / count includes band 9) |
|---|---|---|---|
| `tests/etkl/test_typing_equiv.py:36-53,79-119` | `page_bands(cbh, 0)` directly, via `_band_verdicts` | `EXPECTED_VERDICTS["cbh"]`, a 10-element list, compared `==` to the live per-band `(kind, split, looks_transposed, coherent)` tuples; **index 9 is band 9's current fused `RECORD_TABLE` verdict** | **YES — certain.** The split changes what `page_bands` returns for band 9 (one band -> the split's box bands + residue), so both the LIST LENGTH and index 9 move. No `@pytest.mark.corpus` marker (self-skips only if the PDF is absent) — it runs in CI whenever the corpus is present locally and always runs here. |
| `tests/etkl/test_run_merge_seam.py:145-150` (`test_m1_the_partition_does_not_depend_on_section_repair_bands`) | `page_bands(CBH, 0, None)` and `page_bands(CBH, 0, frozenset({1,3,5,7}))` | `len(...)` equality between the two calls | **Checked, NOT at risk by construction** — band 9 is not in the passed `section_repair_bands` set on EITHER side, so the split applies identically to both calls (it runs before section repair, § 3.1); the two lengths move by the same amount and stay equal. Included because it IS a live `len(page_bands(...))` count over cbh page 0 and must be re-run in Task 3/5, not because it is expected to fail. |
| `tests/etkl/test_run_merge_seam.py:182,320-338` (`BASELINE_ASSERTED[("cbh-stem-2026-08-03", 0)] = 54`, used by `test_o3_no_page_loses_asserted_ink_to_a_merge`) | `compile_tables(cbh, 0, validate_shapes=False, datagrid_fallback=False)` | `rep.asserted == 54` (cbh is in none of `MERGE_MOVES`/`D1_MOVES`/`HEADER_INK_MOVES`, so it falls to the `else` branch's exact equality) | **AT RISK.** 54 is band 9's CURRENT total asserted-token count (all of it, per § 1.3's dump: `tokens_asserted=54, tokens_escalated=0`) — the only asserted band on this page under `compile_tables` (`datagrid_fallback=False`, no document driver). Whether the post-split T1+T2+residue reading still books all 54 tokens as `asserted` (vs. some moving to `escalated`/`ignored`, e.g. the Note residue) is exactly the open question spec § 4 leaves unsettled ("whether the residue reads as notes or `#ignored` is recorded"). **This test WILL need its baseline re-measured, not merely re-run.** |
| `tests/test_cbh_e2e.py:107-117` (`test_cbh_sections_repaired_and_chained`) | `compile_document(cbh)` | `len(rep.repaired_bands) == 4`; `len({page for page, _ in rep.repaired_bands}) == 1`; `len(four_chains) == 1` where `four_chains = [c for c in rep.chains if len(c) == 4]` | **Checked, NOT at risk** — `repaired_bands`/`chains` concern the section-repair driver over bands **1, 3, 5, 7** (the four rosters, N < 9, § 1.3). Band 9 is not part of that repeating group and the split does not touch bands < 9. Included for completeness (it IS a live count-based cbh-page-0 dependent) though it is not expected to move. |

**No other file in the 39-file case-insensitive `cbh` population compiles the cbh corpus PDF
through a band/region producer AND asserts anything positional/count-based over its bands or
regions.** Every other hit was checked and is one of: a docstring/comment-only mention
(`test_ground_section_marker.py`, `test_escalation_wiring.py`, `test_hier_header_ink_is_asserted.py`,
`test_corpus_stem.py`, `test_membrane_health.py`, `test_grounding.py`, `test_kind_gate_is_load_bearing.py`,
`test_arc_manifest.py`, `test_artifact_terms.py`, `test_docgov_extract.py`); a test against pure
functions with literal values copied off the page but never run through the compiler at all
(`tests/etkl/test_datagrid.py`'s `CBH_PANEL1_MEMBERS`/`CBH_PANEL4_MEMBERS` — no `compile_document`/
`compile_tables`/`page_bands` import in that file); a test against synthetic fixtures, not the
corpus PDF (`test_ground_section_marker.py`, `test_escalation_wiring.py`,
`test_fallback_region_books_and_names.py`'s CI-half fixture — its corpus-marked sweep
(`test_every_claiming_region_books_ink_and_names_its_table`) does compile cbh but only FILTERS
`_claiming_regions` and asserts a per-region property, never a count or index, so a region set
that changes shape from 1 to 2/3 members is still checked correctly, member by member); a test
keyed on section-repair region indices `#region0`/`#region1` (N < 9,
`test_supersession_queries.py`); a whole-corpus SHACL focus-node/term-reachability count that is
not band-ordinal (`test_vacuity_registry.py`); a document-level score/accepted comparison, the
same class § 1.1's C2 already covers (`test_cockpit.py`); or a "CBH" demo *contract* namespace
that never touches the corpus PDF (`test_cbh_contract.py`, `test_split_key_naming.py`). The 11
`scripts/*.py` files matching the case-insensitive grep were also checked
(`grep -n "assert " <file> | grep -i cbh`, all empty) — they are census/probe instruments with no
gating assertion, not tests. `readings/boxhead/` (the only `readings/` subdirectory) contains no
cbh reading at all (checked in § 1.4 already).

### 2.4 Affected files run NOW, on today's (pre-split) tree — the "before" for Task 3's Step 3

One file per process, foreground, serially (nothing else compiling concurrently):

```
$ PYTHONPATH=src .venv/bin/python -m pytest tests/etkl/test_typing_equiv.py -q -p no:cacheprovider
6 passed in 38.56s

$ PYTHONPATH=src .venv/bin/python -m pytest tests/etkl/test_run_merge_seam.py -q -p no:cacheprovider
9 passed in 462.49s (0:07:42)

$ PYTHONPATH=src .venv/bin/python -m pytest tests/test_cbh_e2e.py -q -p no:cacheprovider
4 passed in 41.29s
```

**All three files pass in full on today's (pre-split) tree.** This is the "before" Task 3's Step
3 diffs against: `test_typing_equiv.py`'s `EXPECTED_VERDICTS["cbh"]` and
`test_run_merge_seam.py`'s `BASELINE_ASSERTED[("cbh-stem-2026-08-03", 0)]` are the two literals a
later task must re-measure and update (never silently relax) once the split lands; the other two
dependents (`test_m1`, `test_cbh_sections_repaired_and_chained`) are expected to keep passing
unchanged and are re-run as a control on that expectation.

### 2.5 Caveat on § 1.1/1.2's canonical hash (necessary, not sufficient, for C2)

`scripts/corpus_verdict_snapshot.py`'s `_canonical_hash` normalises every blank-node label to the
constant `_:b` before hashing (`_BNODE.sub("_:b", ln)`, per its own docstring: "two graphs
differing ONLY in how blank nodes are SHARED would hash alike"). A blank node is exactly what
every `tab:BBox` node is (`holon.py`'s `_bbox_node`/`_label` helpers mint a bare `BNode()`), and
`tab:hasHeaderNode`/`tab:hasCell` targets are also blank in several emission paths. **A hash match
between a before-snapshot and an after-snapshot in § 1.1 is therefore necessary but NOT
sufficient evidence that the split preserved every bbox's sharing structure** — two graphs whose
blank nodes are wired differently (e.g. two cells that used to share one `BBox` node now each
minting their own, or vice versa) but whose normalised N-Triples are otherwise identical would
still hash identically. Task 5's C2 should read this hash match as "no non-blank-node fact moved"
and lean on § 1.3's content-keyed, non-hash comparison (and `corpus_snapshot_diff.py`'s per-page
verdict/cell diff, which does not depend on blank-node identity at all) for the load-bearing
claim that nothing else changed.
