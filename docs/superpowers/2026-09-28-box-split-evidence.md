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

## § 3. Task 3d.0 baseline (2026-09-30)

**Serves:** prog:criterion:etkl:03 — same criterion as § 1; this is Task 3d.0's own "before",
taken fresh because Tasks 3/3b/3c moved cbh since § 1.1 (plan `docs/superpowers/plans/
2026-09-28-box-split.md`, Task 3d.0; brief `.superpowers/sdd/2026-09-28-box-split/
task-3d.0-brief.md`). HEAD measured: `f41ff6d` (`git status` clean throughout; no `src/`
change on this branch since the plan landed).

### 3.1 Step 1 — whole-corpus verdict snapshot (C2's "before", re-taken)

Same instrument and method as § 1.1 (Task 0 Step 1), re-run because § 1.1's own record is
stale for cbh:

```
$ PYTHONPATH=src .venv/bin/python scripts/corpus_verdict_snapshot.py \
    internal/benchmarks/box-split-2026-09-30/3d0/run1
cbh-stem-2026-08-03                    score=0.9103232533889468     triples= 13416 sha=15b7da8ef677
graincorp-capacity-2026-08-04          score=1.0                    triples=  5859 sha=3b54f16194ca
graincorp-stem-2026-07-31              score=0.9995511669658886     triples= 32422 sha=496c315f2fcc
apple-fy2026q3-statements              score=0.9418604651162791     triples=  6255 sha=1dd90f432c5e
bfs-population-bilan-2023              score=0.9021428571428571     triples= 16736 sha=4fd251c0228f
ons-index-of-services-2026-02          score=0.8684895833333334     triples= 12440 sha=8efa4def664e
who-wfa-boys-zscore-0-5                score=0.9962779156327544     triples= 12292 sha=7e6038064128
```

Output saved at `internal/benchmarks/box-split-2026-09-30/3d0/run1/*.json` (gitignored — this
table is the durable record).

**Comparison against § 1.1's row (2026-09-28, HEAD `d5e07ca`):** 6 of 7 documents are
IDENTICAL — `graincorp-capacity-2026-08-04`, `graincorp-stem-2026-07-31`,
`apple-fy2026q3-statements`, `bfs-population-bilan-2023`, `ons-index-of-services-2026-02`,
`who-wfa-boys-zscore-0-5` — same score, same triple count, same canonical hash, character for
character. Only `cbh-stem-2026-08-03` moved: score `1.0` → `0.9103232533889468`, triples
`12839` → `13416`, hash `ba056c0ed809` → `15b7da8ef677`. This is **expected**, per the brief:
"Task 0's own record is not reusable: Tasks 3, 3b and 3c moved cbh since then" — it is not a
finding, and the row above (not § 1.1's) is Task 3d's C2 "before" for every document,
including cbh.

### 3.2 Step 2 — adoption outcome of the six named tables (U14's corpus side, "before")

**Instrument (scratch, not committed to `src/`):** a spy script monkeypatching the MODULE
GLOBAL `iladub.etkl.document._band_subgraph`. Because `_band_subgraph(...)` is called as a bare
name inside `compile_document` (resolved via the module's global namespace at call time),
replacing the module attribute intercepts every call without touching `src/`. The wrapper
records, per call: the exact `table_uri` argument, the caller's line number (via
`sys._getframe(1).f_lineno`), and — only for calls from line 1733 — the caller frame's own
`p`/`idx`/`pages` locals, from which `pages[p].regions[idx].verdict/.kind/.cells` is read
**before** `document.py:1828`'s `pages[p] = rep_a` overwrites that page's report with the
adoption re-compile's own (whose superseded-band entries carry `table_uri=None`, confirmed by
direct inspection — see below).

`_band_subgraph` has exactly two call sites in the unmodified file (confirmed by
`grep -n "_band_subgraph(" src/iladub/etkl/document.py`): line 1549 (the pass-2 continuation
merge, `graph += _band_subgraph(rep2.graph, r2.table_uri)`) and line 1733 (`sub =
_band_subgraph(pages[p].graph, t)`, inside the adoption withdrawal loop's pointed-into check
the task brief names as `document.py:1733-1740`). The caller line number alone disambiguates
the two sites; no other function in the module calls `_band_subgraph`.

**How each table was identified.** For each of the two documents, `compile_document` was run
once (whole-document compile, exactly as Step 1) with the spy installed. The six target table
URIs were then read directly off the CALL_LOG entries whose `caller_line == 1733` and whose
`table_uri` ends with `/p<page>#table<N>` for the requested page/suffix — i.e. each URI is the
**pass-1** table URI the withdrawal loop itself looked up (`t = pages[p].regions[idx].table_uri`
at `document.py:1730`), not a guess from the final (post-adoption) report. A direct dump of the
final `rep.pages[5/7/8]` regions (saved separately, not part of this record) confirms why the
final report cannot be used for this lookup: after a successful adoption, `pages[p] = rep_a`
(document.py:1828) replaces the whole page report, and `rep_a`'s own regions at the
same indices carry `table_uri=None` for every superseded band (they never got a chance to
assert their own table during the re-compile, having been pre-empted by the grid) — e.g. bfs
`rep.pages[5].regions[3..5]` all show `kind=RECORD_TABLE verdict=superseded table_uri=None`
post-compile, alongside a new `regions[17]` region typed `tab:DataGrid` at
`.../p5/adopt#p5-datagrid` (496 cells, `verdict=asserted`) — the grid that replaced them.

**Result** (full JSON at
`internal/benchmarks/box-split-2026-09-30/3d0/adoption_outcome_final.json`, gitignored):

| table | pass-1 verdict/kind/cells | called at `document.py:1733` | page has an "adoption refused" note | present in final graph |
|---|---|---|---|---|
| bfs p5 `#table3` | asserted / RECORD_TABLE / 48 | yes | no | **no** |
| bfs p5 `#table4` | asserted / RECORD_TABLE / 108 | yes | no | **no** |
| bfs p5 `#table5` | asserted / RECORD_TABLE / 36 | yes | no | **no** |
| ons p7 `#table4` | asserted / RECORD_TABLE / 6 | yes | no | **no** |
| ons p7 `#table13` | asserted / RECORD_TABLE / 86 | yes | no | **no** |
| ons p8 `#table3` | asserted / RECORD_TABLE / 6 | yes | no | **no** |

All six: asserted a `tab:RecordTable` at pass 1, were named as `superseded` candidates in the
document's own adoption re-compile, went through the pointed-into check at `document.py:1733`
(no document-level triple pointed into any of the six, and none is a member of a
multi-table chain — otherwise `blocked` would have fired and the corresponding page would carry
an "adoption refused" note, which none of the three pages (5, 7, 8) does), and are **absent**
from the final merged graph — i.e. **withdrawn today, on the pre-3d tree**, and replaced by
that page's adopted data grid (`bfs`: `.../p5/adopt#p5-datagrid`, 496 cells; `ons`:
`.../p7/adopt#p7-datagrid` 276 cells and `.../p8/adopt#p8-datagrid` 276 cells — all three
`verdict=asserted`). `rep.notes` for `bfs-population-bilan-2023` carries "adoption refused" only
for pages 0, 4 and 6 (none of which is 5, 7 or 8); for `ons-index-of-services-2026-02` only for
page 0 (not 7 or 8).

**Reading against spec § 10.5/§ 10.7.** The spec predicts that once the boxhead-absence feature
ships, three of these six (bfs p5 `#table3`/`#table4`, ons p7 `#table13`) are asked, answer `0`
(row 0 is data), and that "a correct `0` mints the edge, and the edge refuses adoption on bfs p5
and on ons p7" (spec lines 828-830). This record is the **pre-feature** state: no
`tab:boxheadAbsentBy` edge exists yet, and — consistent with the spec's own framing of what
changes — adoption today withdraws all six without exception. 3d.7's corpus run is expected to
show bfs p5 and ons p7's adoption newly **refused** post-feature (the grid's read is now
disqualified because the table it would supersede has no boxhead), while ons p8 `#table3` (not
in the three named as "asked" at spec line 828) is expected to be **unaffected** — that
divergence, if it holds, is 3d.7's own finding and is not measured here.

### 3.3 Instrument note

Both instruments above are PROCEDURAL (CLAUDE.md § 8): they read compile results (a snapshot
script; a monkeypatch spy over an existing pure function) and decide nothing about any
document's content, carry no tuned constant or tolerance, and are irreducible to AXIOM (no RDF
evidence graph is being queried; the object under test is Python call structure, not asserted
facts) or NEURAL (nothing here is underdetermined — every field read is either already computed
by `compile_document` or is the literal call-site argument a monkeypatch observed). Neither
script is committed to `src/`; both ran from the session's scratch directory, per the sub-task's
own instruction not to add either to `src/`.

## § 4. Task 3d.7 — the corpus: T2 recorded, census, O2, C2 (2026-09-30)

**Serves:** prog:criterion:tab:12 — O2 (`tests/test_carriage.py`, the three `test_o2_*`) XPASSes as
a whole once T2's reading is committed; this is the measurement Task 4 Steps 4–5 act on. Plan
`docs/superpowers/plans/2026-09-28-box-split.md`, Task 3d.7 as amended (A2, A6, A4); spec
`docs/superpowers/specs/2026-09-28-box-split-design.md` § 10.5–§ 10.7. Measured on `box-split` at
`7fa2b22` (3d.6's `9891f79` plus the prompt rewording below) with `readings/header_lines/` staged.
Every figure here was produced by the commands quoted; the outputs live under
`internal/benchmarks/box-split-2026-09-30/3d7/{baseline,live,replay}/` (gitignored), so this
section is the durable record.

### 4.1 Before the first live call: the prompt no longer contradicts its schema

`baml_src/header_lines.baml` said *"Answer with the count only"* while `HeaderLines` requires a
`note` (3d.5 review M6). Reworded to *"Give the count, and a note that quotes nothing from the
table"*, client regenerated (`baml-cli generate --from baml_src`, 0.222.0; `baml_client/` stays
gitignored), committed as `7fa2b22` before any call. No live answer below failed to parse: all
seven `---Parsed Response (class HeaderLines)---` blocks carry both fields, and the instrument's
spy on `sync_client.b.CountHeaderLines` recorded `ok=True` for all seven.

### 4.2 The instrument, and the one thing the plan's command would have got wrong

One scratch script (`instrument.py`, not committed) compiles ONE document with
`document.compile_document`, one process per document, serially, from a `.sh` under `bash`. It
spies, from outside `src/`, on four module globals looked up at call time: `compile._header_lines_decision`
(every site reach: region, pass, `nlines`, `ncols`, question key, row 0), `rowzero.row_zero_differs`
(the witness), `headerlines.ask_header_lines` (the reading), and `document._band_subgraph` (caller
line, and whether the returned subgraph holds a `tab:boxheadAbsentBy`). It writes the snapshot
fields of `scripts/corpus_verdict_snapshot.py` (same canonical hash: sorted N-Triples, blank-node
labels normalised) and the sorted, normalised N-Triples themselves, so C2 can diff content, not
only hashes. Three modes:

- **baseline** — `headerlines.READINGS_DIR` pointed at an empty directory, offline: no claim
  anywhere, which is the 3d.0 graph. **Proven, not assumed:** all seven canonical hashes equal
  § 3.1's to the last hex digit (`15b7da8ef677`, `3b54f16194ca`, `496c315f2fcc`, `1dd90f432c5e`,
  `4fd251c0228f`, `8efa4def664e`, `7e6038064128`), and the non-hash snapshot fields are equal too.
  This is C2's "before" with its N-Triples on disk, which § 3.1 did not keep.
- **live** — `source ~/.zshrc`, then `BAML_LIVE=1 ILADUB_RECORD_READINGS=1` (Step 1).
- **replay** — `env -u ANTHROPIC_API_KEY -u BAML_LIVE -u ILADUB_RECORD_READINGS`, recordings only.

**`BAML_LIVE=1` switches on more than this worker.** Enumerated with
`grep -rn "BAML_LIVE" src`: five gates. Two of them reach `compile_document`:
`unshownink.baml_reader_available()` (read in `compile.page_bands`, it turns on R213's region
reader, `ClaudeLongAnswer` = Sonnet 5, and fills `Band.unshown`) and
`boxhead.baml_boxhead_available()`. The offline replay (every later compile, CI, the tests) has
both OFF. Recording under them would have recorded answers to questions asked in a different
reading configuration. `Band.unshown` feeds `row_zero_evidence`, so the oracle's input would differ,
and it would have spent Sonnet calls this task does not own. So the live run patched both gates to
`False` and replaced every other generated BAML function with a trap that records and raises.
**Stray calls: 0 on all seven documents.** The replay hashes equal the live hashes on all seven,
which is the check that confining the live run changed nothing the replay sees.

(The first live launch died at `import baml_client` in every process — the script's directory,
not the repo root, was `sys.path[0]` — before any compile or call. Its partial output directory
was deleted.)

### 4.3 Step 1 — the recorded answers, and A2's count

Live run, serial, 7 documents:

```
cbh-stem-2026-08-03           mode=live score=0.9103232533889468 triples=13429 sha=0dca500a977c reaches=6 asked=3 live=1 stray=0 stmts=1
graincorp-capacity-2026-08-04 mode=live score=1.0                triples=5859  sha=3b54f16194ca reaches=0 asked=0 live=0 stray=0 stmts=0
graincorp-stem-2026-07-31     mode=live score=0.9995511669658886 triples=32422 sha=496c315f2fcc reaches=0 asked=0 live=0 stray=0 stmts=0
apple-fy2026q3-statements     mode=live score=0.9418604651162791 triples=6255  sha=1dd90f432c5e reaches=2 asked=0 live=0 stray=0 stmts=0
bfs-population-bilan-2023     mode=live score=0.9021428571428571 triples=16778 sha=d395c373c62b reaches=8 asked=6 live=3 stray=0 stmts=0
ons-index-of-services-2026-02 mode=live score=0.8684895833333334 triples=12454 sha=5db3db9c29ed reaches=6 asked=2 live=1 stray=0 stmts=0
who-wfa-boys-zscore-0-5       mode=live score=0.9962779156327544 triples=12274 sha=7532b4756f38 reaches=2 asked=2 live=2 stray=0 stmts=2
```

The replay run prints the same seven lines with `live=0` (hashes identical). `stmts` counts
`tab:boxheadAbsentBy` triples in the FINAL document graph.

**T2 answered `0`.** Model `claude-haiku-4-5-20251001`, 1505 ms, 421/60 tokens; note: *"The first
line presents data in the same format as subsequent lines, with a country code paired with a date
range, making it a data row rather than a header."*

**A2 — a region asked on N passes leaves one recording.** Over the replay's site reaches:

```
asks 13 | distinct question keys 7 | live calls (live run) 7 | files in readings/header_lines/ 7
0f852b55c8  /p5#region3, /p5/adopt#region3                  answer {0}
43d128055d  /p5#region4, /p5/adopt#region4                  answer {0}
c71008e113  /p6#region2, /p6/adopt#region2                  answer {3}
79dd813d4c  /p0#region11, /p0/r2#region11, /p0/adopt#region11   answer {0}   (cbh T2)
3c558b0c60  /p7#region13, /p7/adopt#region13                answer {0}
0f36be5b42  /p0#region4                                     answer {0}
de8744f5d9  /p1#region4                                     answer {0}
```

The key never moved between passes, and every pass of a region got the same answer, read per
reach from the spy, not from the 3d.4 corpus test's row-0-keyed dict (controller note). No note
quotes a table value (all seven read by eye).

### 4.4 Step 2 — the census against § 10.5's prediction

Every reach of the ask site (replay; `witness` = `row-zero-differs.rq`):

| document | region (pass) | nlines × ncols | witness | asked | answer | row 0 (truncated) |
|---|---|---|---|---|---|---|
| cbh | p0 `#region10` (p, r2, adopt) — T1 | 5 × 7 | true | no | — | `PORT \| WHEAT \| MAIN WHEAT GRADES …` |
| cbh | p0 `#region11` (p, r2, adopt) — **T2** | 4 × 2 | false | yes | **0** | `ALB \| 1 - 15 October` |
| who | p0 `#region4` (p) | 6 × 13 | false | yes | 0 | `1: \| 1 \| 13 \| 0.0563 …` |
| who | p1 `#region4` (p) | 6 × 13 | false | yes | 0 | `3: \| 1 \| 37 \| -0.0729 …` |
| bfs | p5 `#region3` (p, adopt) | 5 × 12 | false | yes | 0 | `2005 \| 7 415 102 …` |
| bfs | p5 `#region4` (p, adopt) | 11 × 12 | false | yes | 0 | `2010 2 \| 7 785 806 …` |
| bfs | p5 `#region5` (p, adopt) | 4 × 12 | true | no | — | `2020 \| 8 606 033 …` (the false witness, § 10.2) |
| bfs | p6 `#region2` (p, adopt) | 4 × 9 | false | yes | **3** | `Grandes régions \| Total \| 0-19 ans …` |
| ons | p7 `#region4`, p8 `#region3` (p, adopt) | 2 × 6 | true | no | — | `Section \| G-T \| …` |
| ons | p7 `#region13` (p, adopt) | 15 × 7 | false | yes | 0 | `2024 \| Dec \| 102.4 …` |
| apple | p2 `#region6` (p, adopt) | 2 × 3 | true | no | — | `Increase in cash, …` |
| graincorp-capacity, graincorp-stem | — | | | | | the site is never reached |

**The asked population is exactly § 10.5's seven questions:** cbh T2; who p0 and p1 `#table4`;
bfs p6 `#table2`; bfs p5 `#table3` and `#table4`; ons p7 `#table13`. T1, every donated table and
every witnessed table are not asked. The set holds; it is the same as 3d.6's all-zero-fake census.

**The answers.** Six `0`s, and each agrees with § 10.2's reading of that row 0 as data. One `3`:
bfs p6 `#table2`, the region § 10.2 describes as *"a 4-line header, no numeric body"*. So the
worker did **not** give the wrong `0` § 10.6 feared on the one shape the oracle cannot refute. It
under-counted by one (4 lines, all header, and it said 3). An answer ≥ 1 records `boxhead` and
emits today's table (§ 10.3.4; above 1 adds no level, § 10.6), so the under-count moves nothing.

**This is the first measurement of § 10.6's register row, widened by § 10.7 R-2** (every asked
answer is admitted undisposed, because the oracle is silent on the asked population by
construction): 7 asked, 6 × `0` admitted undisposed (3 reach the final graph: cbh T2 and who ×2;
3 are withdrawn by adoption: bfs p5 ×2 and ons p7 `#table13`), and 1 × `3` recorded as `boxhead`.

### 4.5 Step 3 — O2

```
$ bash one.sh tests/test_carriage.py -m corpus     # offline env, one file, one process
FAILED tests/test_carriage.py::test_bfs_p5_carries_the_row_label_and_percent_columns
FAILED tests/test_carriage.py::test_o2_t1_reads_the_seven_column_boxhead - [XPASS(strict)]
FAILED tests/test_carriage.py::test_o2_t2_reads_the_two_column_no_boxhead - [XPASS(strict)]
FAILED tests/test_carriage.py::test_o2_note_block_is_not_carried_as_a_cell - [XPASS(strict)]
4 failed, 2 passed in 188.85s (0:03:08)
```

**O2 XPASSes as a whole**: `test_o2_t2_reads_the_two_column_no_boxhead` now XPASSes beside the two
that have XPASSed since Task 3c. This is the forcing function Task 4 Step 4 names, and the strict
xfail markers are Task 4's to flip, not this task's.

**A new red in the same file: `test_bfs_p5_carries_the_row_label_and_percent_columns`**,
`assert 16778 == 16736` on `DOC_TRIPLES_WHEN_CARRIED`. Its other assertion,
`P5_CELLS_WHEN_CARRIED == 496`, still holds; it is the figure the file says pins the switch. The
+42 is exactly three `header_lines` decisions × 14 triples (§ 4.6): two `no_boxhead` on bfs p5
bands whose tables adoption then withdraws, and one `boxhead` on p6. A withdrawn table's band
keeps its pass-1 decisions in the log (§ 3.2; the `d0`–`d5` of those bands are in the 3d.0 graph
too), and the new decision joins them. The file's own comments re-pin this whole-document count
each time a reading lands (15354 → 16147 → 16736). **Not re-pinned here**: `test_carriage.py`'s
edits are Task 4's. The measured value to pin is 16778.

### 4.6 Step 4 — C2 against 3d.0

**Hashes** (before = the proven 3d.0 graph of § 4.2, after = replay):

| document | before | after | identical | triples |
|---|---|---|---|---|
| apple | `1dd90f432c5e` | `1dd90f432c5e` | yes | 6255 → 6255 |
| graincorp-capacity | `3b54f16194ca` | `3b54f16194ca` | yes | 5859 → 5859 |
| graincorp-stem | `496c315f2fcc` | `496c315f2fcc` | yes | 32422 → 32422 |
| bfs | `4fd251c0228f` | `d395c373c62b` | no | 16736 → 16778 |
| cbh | `15b7da8ef677` | `0dca500a977c` | no | 13416 → 13429 |
| ons | `8efa4def664e` | `5db3db9c29ed` | no | 12440 → 12454 |
| who | `7e6038064128` | `7532b4756f38` | no | 12292 → 12274 |

The three documents with no asked region (apple is reached but only witnessed; the graincorps
are never reached) have identical hashes. The ink score is unchanged on all seven, to the last
digit. It is recorded as a fact, never as an oracle (spec § 5).

**The diff on the other four**, as a multiset of normalised N-Triples lines. First, the baseline's
decisions on each answered band are renamed `#region{i}-d{n}` → `-d{n+1}` for `n` at or above the
`header_lines` decision's number, with their `dec:order` incremented. On an answered band that
decision is recorded before `region_tiles` and the verdict, so every later decision IRI shifts by
one (controller note). The remainder, grouped by URI space and predicate:

```
bfs  p5#region3 [header_lines decision]  +14 (type 3, label 3, optionSpace 2, chosen, decidedBy, order, rationale, regarding, withinProcess) -0
     p5#region3 [other decision]          +1 -1  rationale
     p5#region4 [header_lines decision]  +14 -0      p5#region4 [other decision] +1 -1 rationale
     p6#region2 [header_lines decision]  +14 -0
cbh  p0#region11 [header_lines decision] +14 -0      p0#region11 [other decision] +1 -1 rationale
     p0#table11  +19 {type 3, wasDerivedFrom 2, atColumn 2, atRow 2, cellText 2, hasBBox 2, onPage 2, hasCell 2, hasLeafRow 1, boxheadAbsentBy 1}
                 -20 {type 4, coversColumn 2, hasLabel 2, headerLevel 2, cellText 2, hasBBox 2, onPage 2, hasCell 2, hasHeaderNode 2}
ons  p7#region13 [header_lines decision] +14 -0      p7#region13 [other decision] +1 -1 rationale
who  p0#region4, p1#region4: as cbh's region (+14; +1 -1 rationale)
     p0#table4, p1#table4 each: +107 {type 14, wasDerivedFrom 13, atColumn 13, atRow 13, cellText 13, hasBBox 13,
                                       onPage 13, hasCell 13, hasLeafRow 1, boxheadAbsentBy 1}
                                -130 {type 26, coversColumn 13, hasLabel 13, headerLevel 13, cellText 13, hasBBox 13,
                                       onPage 13, hasCell 13, hasHeaderNode 13}
```

- The `dec:supersedes` lines from `p5/adopt#p5-datagrid-admission` and `p7/adopt#p7-datagrid-admission`
  (the pass-1 verdict decision, `-d5` → `-d6`, on bfs p5 `#region3`/`#region4` and ons p7
  `#region13`) vanish under the rename. They point at the shifted pass-1 decisions.
- The one `rationale` per `0`-answered band is `region_tiles`' entry count: T2's
  *"validated the 6 entries"* → *"the 8 entries"*. Row 0 is now two entries.
- No line has a blank-node subject; no subject lies outside an asked region's decisions or an
  asked table's URI space. **C2 holds.** The table-space deltas are the § 10.3.4 emission: header
  nodes and label cells out, one more `tab:LeafRow` of entry cells in, and the statement.
- § 2.5's caveat applies unchanged: blank-node sharing is invisible to this diff.
- **The criterion applied is "an asked region's decisions", wider than the brief's "an asked
  table's URI space or its `header_lines` decision"** (added in fix round 1). It also admits the
  `region_tiles` rationale change and the `-d{n}` renumbering of the band's later decisions. The
  spec admits both: § 10.5's C2 confines the diff to "the asked tables' triples and their
  decisions", and those two are the same band's decisions. A `0` changes the entry count that
  `region_tiles` validates (§ 10.3.4, "the region gate then runs unchanged" over the new
  emission), and recording the decision before the gate is § 10.3.4's order, so the later
  decision IRIs shift by construction. Neither reaches outside the asked region's own band.

**U14's corpus side, A6 as corrected.** The six tables of § 3.2 were checked in the FINAL graph by
direct URI membership (any triple with the URI as subject or object):

```
p5#table3 False  p5#table4 False  p5#table5 False  p7#table4 False  p7#table13 False  p8#table3 False
```

This is the same outcome as at 3d.0: all six withdrawn, adoption not refused on bfs p5 or on
ons p7. ons stays accepted, and § 10.7's predicted regression does not occur. The `_band_subgraph`
spy at the withdrawal site (`compile_document`, `document.py:1752`) shows the observable A6 needs:

```
p5#table3   statement in subgraph: (p5#table3 -> p5#region3-d4)   decision nodes in subgraph: 0
p5#table4   statement in subgraph: (p5#table4 -> p5#region4-d4)   decision nodes in subgraph: 0
p7#table13  statement in subgraph: (p7#table13 -> p7#region13-d4) decision nodes in subgraph: 0
p5#table5, p7#table4, p8#table3: no statement (witnessed, never asked)
```

The statement leaves with its table; the decision stays in the log (3d.2's stop, on real input).
The `/adopt` asks are discarded with the rebuilt page graph, as 3d.6 found. **The `/r2` merge-in
has no corpus population.** cbh T2 is asked on `/r2`, but the `/r2` merge (`document.py:1568`)
takes only `r2#htable1`, `#htable3`, `#htable5` and `#htable7`, none of them asked. So T2's final
table is the pass-1 `p0#table11`, and A6's merge-in direction stays pinned by 3d.6's synthetic U14
test only.

**I-10-3 at document scope.** In every final graph, every `tab:boxheadAbsentBy` object is a
`dec:DecisionHolon` in that graph with label `header_lines` and `dec:chosen` → `no_boxhead`: cbh
`p0#table11` → `p0#region11-d4`, who `p0#table4` → `p0#region4-d4`, `p1#table4` → `p1#region4-d4`.
The query for a statement whose object is not a decision returns 0 rows on all seven. The three
`no_boxhead` decisions with no table in the final graph (bfs p5 `#region3`, `#region4`, ons p7
`#region13`) belong to withdrawn tables.

**C1 (controller notes from 3d.3), on the FINAL document graphs:**

```
SELECT DISTINCT ?t ?h { ?t tab:boxheadAbsentBy ?d ; tab:hasHeaderNode ?h }                         -> 0 rows, all 7
SELECT DISTINCT ?t { ?t tab:boxheadAbsentBy ?d . {?t tab:continuesTable ?x} UNION {?y tab:continuesTable ?t} } -> 0 rows, all 7
SELECT DISTINCT ?t ?h ?ty { ?t tab:boxheadAbsentBy ?d ; ?p ?h . ?h a ?ty .
                            FILTER(?ty IN (tab:HeaderNode, tab:DerivedRowGroup)) }                 -> 0 rows, all 7
```

This time with real recorded answers, not 3d.6's all-zero fake.

**Rect fill under an unshown row-0 address (controller note from 3d.4's review): 0, and
vacuously so.** At every one of the 24 oracle reaches the spy computed the row-0 cells whose
address is in `band.unshown` and whether a filled rect contains their centre: 0 such cells,
because `band.unshown` is `()` on every band. It is filled only by R213's live reader
(`unshownink.baml_reader_available`, § 4.2), which is off in every offline compile. The unsafe
direction the note names (a withheld fill removes a witness) cannot occur offline. It is
**unmeasured** under the R213 reader.

### 4.7 Step 5 — the local sweep, and the known-red set

**Controller ruling (2026-09-30, mid-task):** the full-suite sweep was stopped after 5 of 29
chunks and replaced by a TARGETED sweep. 3d.6 ran the full suite at `9891f79` (1924 passed, 8
known-red), and 3d.7 changes no `src/` logic: it adds readings, one `.baml` prompt line, this
evidence, and comment-only, line-neutral citation edits. The five full chunks that did finish
(40 files, sorted, `tests/etkl/test_adoption_document.py` through
`tests/etkl/test_document_membrane_gate.py`,
including both `test_boxhead_absence*` files, `test_closure_equiv.py` and the four
`test_adoption_*` files) were all green: 454 passed, 2 skipped, 1 xfailed.

The targeted set: every file in its own process, in the foreground, offline
(`env -u ANTHROPIC_API_KEY -u BAML_LIVE -u ILADUB_RECORD_READINGS`), from a `.sh` under `bash`, with
the readings, this file and the citation edits staged:

```
tests/test_doc_governance.py            7 passed
tests/test_docgov_extract.py           22 passed
tests/test_source_ownership.py          3 passed
tests/test_source_citations.py          8 passed
tests/test_artifact_declarations.py     9 passed
tests/test_artifact_terms.py           18 passed
tests/test_query_declarations.py        5 passed
tests/test_arc_manifest.py             28 passed
tests/etkl/test_header_lines.py        16 passed
tests/etkl/test_boxhead_absence.py     26 passed
tests/etkl/test_boxhead_absence_site.py 17 passed
tests/etkl/test_row_zero_differs.py    16 passed
tests/etkl/test_vacuity_registry.py     9 passed                 <- was red (4 idle shapes)
tests/test_carriage.py                  4 failed, 2 passed
tests/test_cbh_e2e.py                   2 failed, 2 passed
tests/etkl/test_run_merge_seam.py       1 failed, 8 passed
tests/etkl/test_typing_equiv.py         1 failed, 5 passed
tests/etkl/test_escalation_furnish.py   1 failed, 9 passed
tests/etkl/test_boxhead.py             11 passed
tests/etkl/test_adoption_document.py   12 passed
```

**The known-red set, before (3d.6, `9891f79`) → after:**

| test | before | after |
|---|---|---|
| `test_run_merge_seam::test_o3_no_page_loses_asserted_ink_to_a_merge` | red, cbh 43 < 54 | red, cbh 43 < 54 (unchanged) |
| `test_typing_equiv::test_band_verdicts_are_recorded_and_stable[cbh]` | red | red (unchanged) |
| `test_escalation_furnish::test_corpus_a_wholly_superseded_document_furnishes_nothing` | red, `5 == 4` | red, `5 == 4` (unchanged) |
| `test_vacuity_registry::test_every_idle_shape_is_registered` | red, 4 shapes | **green** (A4's prediction held: cbh and who mint the statement, all four shapes go live) |
| `test_carriage::test_o2_t1_reads_the_seven_column_boxhead` | XPASS(strict) | XPASS(strict) (unchanged) |
| `test_carriage::test_o2_note_block_is_not_carried_as_a_cell` | XPASS(strict) | XPASS(strict) (unchanged) |
| `test_carriage::test_o2_t2_reads_the_two_column_no_boxhead` | xfail | **XPASS(strict)** (O2 as a whole; Task 4 Step 4 flips it) |
| `test_carriage::test_bfs_p5_carries_the_row_label_and_percent_columns` | green | **red**, `16778 == 16736` (§ 4.5; the pin is Task 4's) |
| `test_cbh_e2e::test_cbh_every_sectioned_record_carries_its_section_port` | red | red (unchanged) |
| `test_cbh_e2e::test_cbh_cascade_resolves_port` | red | red (unchanged) |

8 red before, 9 red after: one left (vacuity), two joined. One of those is the forcing function
this task exists to trip (O2 T2); the other is a whole-document triple pin that moved by the
+42 § 4.6 accounts for, triple by triple.

### 4.8 For Task 5's list (raised there, not here)

1. **§ 10.6's first row, widened by § 10.7 R-2.** Every asked answer is admitted undisposed, and the
   oracle is silent on that population by construction. First measurement: § 4.4 (7 asked; 6 × `0`,
   1 × `3`). The body-less shape § 10.6 names, bfs p6 `#table2`, answered `3` of 4 header lines:
   an under-count, and not the feared wrong `0`.
2. **§ 10.7 R-3's row.** A witnessed table's header stays an unrecorded positional default. bfs p5
   `#table5` (false witness, `celltype`'s space-thousands typing) is the case § 10.2 names; on this
   corpus it is withdrawn by adoption.
3. (§ 10.6's second bullet, already scoped there.) The `celltype` space-thousands false witness,
   bfs p5 `#region5`: still `witness=true` here.
4. **New, from this run: a headerless table's `kind` decision still says "flat single-level
   header".** On cbh `p0#region11` (and on each `0`-answered band), `-d1` (label `kind`, chosen
   `RECORD_TABLE`) keeps classify's stock rationale. The table now states `tab:boxheadAbsentBy`.
   No shape reads rationale prose, so nothing is refused, but the log contradicts itself in prose.
5. **New: the rect-fill-under-unshown count is unmeasured under R213's reader** (§ 4.6, last
   paragraph). A future offline replay of R213 readings would populate `band.unshown` and make it
   measurable.
6. **Carried from § 4.2 as a process fact:** the `BAML_LIVE=1` recording recipe (plan Step 1, spec
   § 10.5 O2) also switches on R213's region reader and the boxhead reader's live half. A recording
   run for one worker has to switch the others off.
7. **Owner for the bfs triple pin (fix round 1): Task 4, alongside the O2 flip.**
   `tests/test_carriage.py`'s `DOC_TRIPLES_WHEN_CARRIED` (`= 16736`, at `:71` when measured) is red
   at `16778`. The +42 is three `header_lines` decisions × 14 triples each (§ 4.5, § 4.6): bfs p5
   `#region3`/`#region4` (`no_boxhead`, tables withdrawn by adoption) and p6 `#region2` (`boxhead`).
   Task 4 Steps 4–5 name only the O2 flip and the `tab:12` manifest, so nothing else would re-pin
   it. Re-pin to the measured 16778, with a dated comment in the file's own style
   (`16736 -> 16778 on 2026-09-30: …`). `P5_CELLS_WHEN_CARRIED == 496` still holds and is not touched.
8. **Task 5 Step 2's C2 must judge bfs, ons and who against § 4.6, not against Task 0's hashes**
   (fix round 1). Task 5 Step 2 requires every non-cbh document to hash identically to Task 0 and
   calls any difference a finding. After 3d.7, bfs (`d395c373c62b`), ons (`5db3db9c29ed`) and who
   (`7532b4756f38`) differ from Task 0 BY DESIGN: the answered bands of § 4.4. The check for those
   three is that the diff against the 3d.0 graph is exactly § 4.6's accounted deltas (with the
   `-d{n}` rename). Any triple beyond them is the finding. apple, graincorp-capacity and
   graincorp-stem still hash identically to Task 0 and keep the hash test.
9. **The Task 5 / whole-branch sweep must include five files not run after the readings landed**
   (fix round 1, reviewer M2). They read the re-recorded documents, and 3d.7's targeted sweep
   (§ 4.7) did not run them: `tests/etkl/test_read_band_books_every_word.py`,
   `tests/etkl/test_membrane_health.py`, `tests/etkl/test_grid_donation_seam.py`,
   `tests/etkl/test_span_donation_seam.py`, `tests/test_cockpit.py`.

### 4.9 3d.6's measurements, carried into the record

Two citations in the tree pointed at 3d.6's task report, which is gitignored (`.superpowers/`).
The measurements they rely on are quoted here, from that report (3d.6, `9891f79`), so the
citations can point at a tracked file:

- **What the `header_lines` decision points at** (cited by `compile._header_lines_decision`'s
  docstring). `decisionlog.BandRecorder.record` writes `rdf:type dec:DecisionHolon`, `rdfs:label`,
  `dec:regarding {doc}#region{idx}` (the band's region node, not a table or cell URI),
  `dec:withinProcess` (the band process), `dec:decidedBy`, `dec:order`, `dec:rationale`,
  `dec:optionSpace`/`dec:chosen` → `{d}-opt-*`, and `dec:consideredEvidence` only for `evidence=`.
  The site passes no `evidence=`. So the decision points into no `#table{idx}` / cell space, and
  `document._band_reading_subgraph` (outgoing closure from the log) cannot walk from it into a
  table. On the corpus, § 4.6's spy confirms the other half: the withdrawal subgraph holds the
  statement and 0 decision nodes.
- **Which synthetic fixtures reach the site on more than one pass** (cited by
  `tests/etkl/test_boxhead_absence_site.py`'s Review Focus 1 comment). Over every `fixtures.py`
  builder that takes a path alone, reaches of `assert_record_region` by pass were
  `p0: 36, p1: 3, r2: 2, adopt: 1`. The 8 unwitnessed, non-donated reaches were all on `p0`, one
  pass each. Every non-`p0` reach was witnessed: `currency_marker_escalating_with_asserting_table_pdf`
  (`p0` and `/adopt`, `table1`), `multi_section_ruled_pdf` (`/r2` only, `table0` and `table1`).
  On the corpus the unwitnessed multi-pass case exists (§ 4.3: cbh T2 on `p`/`r2`/`adopt`, bfs p5
  and p6 and ons p7 on `p`/`adopt`), and every pass asked the same key.
