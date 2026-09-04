# R165 pre-plan measurement spike — the seam, the O5 technique, and the real test surface

**Date:** 2026-09-04. **Branch:** `one-band-in-page-bands`. **No `src/` or `vocab/` file was changed by
this loop** — the prototype below was applied to the working tree, measured, and reverted; the tree was
verified clean (`git status --short` → only the two pre-existing untracked `.github/` entries) before this
file was written. Subject: `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` §§ 3.0-3.5, 5, 6.

**Why this exists.** The spec's handoff (`docs/superpowers/2026-09-04-the-run-is-one-band-handoff.md` § 5)
graded three of the spec's claims **PROPOSED** and ordered them MEASURED before the plan's tasks were
written: M1's cost, O5's technique, and the real index-pinning test surface. This file is that measurement.
**Two of the three came back with a refutation inside them** (§ Q-B B1, § Q-C C4), which is the whole
reason the handoff typed them rather than writing the plan against them.

**Doc impact: none.** Evidence only; no released assertion, no wiki page and no `mkdocs.yml` nav entry
changes. The `Doc impact: increment` the spec declares is still owed by the plan that implements it.

## 0. What the prototype is, and the ONE substitution it makes

`page_bands` (`src/iladub/etkl/compile.py:270`) was patched in the working tree to:

1. build **every** band with `section_repair=False` (M1, § 3.1), remembering per index the
   `(sub, sub_rules, sub_hrules)` triple;
2. compute the § 3.3 relation (adjacent subsumption over the band's distinct rounded rule-x
   positions) **in plain Python** — `_proto_run_candidates`;
3. offer each candidate run's merged band (`_proto_merge_bands`, the spike's `merge_bands`
   verbatim) to the **existing** disposal chain `is_matrix_candidate → classify_matrix →
   assert_matrix_region → region_tiles` on a scratch `Graph` — `_proto_run_admissible`, a
   line-for-line reuse of `compile.py:817-840`'s calls;
4. then apply the repair flag by re-building **only** the bands named in `section_repair_bands`;
5. then splice each accepted run into one band, descending by `first`.

> **STATED SUBSTITUTION (required by the task brief).** Step 2 is **plain Python**, not the SPARQL
> derivation the shipped design requires (spec § 3.4: `tab:RuledBand` / `tab:ruleX` facts +
> a `vocab/queries/*.rq` `FILTER NOT EXISTS` pair derivation). This spike measures the **SEAM**
> (where the merge lives, what M1 costs, whether the fallback is clean, what tests move), **not
> the derivation**. Nothing here licenses shipping a Python relation.

No tuned constant was introduced anywhere. `_proto_rule_x_set` uses `round(r.x, 2)` — the rounding
`sectiongraph._rule_xs_signature` already performs (`sectiongraph.py:178-189`), inherited, not tuned.

Cross-check that the prototype's relation IS the census's relation B: the runs it produces are
identical to spec § 3.3's Q3 table on every page probed — apple p0 `2..7`, apple p1 `2..7`,
apple p2 `3..7`, gc-stem p0 `1..2`, gc-cap p0 `1..3`, bfs p5 `(2,5)` + `(7,8)`, ons p7 `2..15`.

Diff: `r165-prototype.diff` (123 lines). Scratch scripts: `time_page_bands.py`, `stage_cost.py`,
`m1_check.py`, `qb_stage.py`, `qb_force.py`, `qb_frag2.py`, `qb_doc.py`, `idx_test_files.txt`.

Smoke test (the seam works at all):

```
$ PYTHONPATH=src python3 -c "from iladub.etkl.compile import page_bands, compile_tables; ..."
apple p0 bands: 3
score 1.0 regions 3
  0 ignored 0 None
  1 ignored 0 None
  2 asserted 124 https://example.org/etkl/doc#mtable2
```

The 124-entry / score-1.0 headline of spike § 8.4 reproduces **from inside `page_bands`**, which is
the thing § 8.6 said had never been shown.

---

## Q-A — INVARIANT M1: implementable, and what it costs

### A1. The cheapest way to uphold M1 is ONE extra `_build_ruled_band` per named band — NOT a second page build

Measured by counting calls (`m1_check.py`, which monkeypatches `compile._build_ruled_band` with a
counter), on cbh p0 — the **only** corpus page whose `section_repair_bands` is non-empty
(spike § 8.2: 1 of 27 pages; `section_candidates == ((1,3,5,7),)`):

```
$ PYTHONPATH=src python3 scratchpad/m1_check.py
srb=None:         bands=10 _build_ruled_band calls=5 (repaired=0) runs_over_returned=[]
srb=[1, 3, 5, 7]: bands=10 _build_ruled_band calls=9 (repaired=4) runs_over_returned=[]
```

5 → 9 calls for 4 named bands: **exactly +1 `_build_ruled_band` per named band**, and only for the
named ones. The page's other machinery (`extract_words`/`extract_rules`/`extract_chars`/
`detect_bands`/`segment`/`absorb_unit_markers`) runs once, so this is **not** a second page build.
The implementation shape that achieves it: keep the `(sub, sub_rules, sub_hrules)` triple per index
while building the unrepaired list, then re-call `_build_ruled_band(..., section_repair=True)` for
each named index and overwrite that slot.

**Cost of the M1 half alone**, from the timing table below: cbh p0 with the repair set goes
1.35s → 1.75-1.85s, i.e. **+0.40s / +30%** for 4 rebuilt bands on a 1.35s page. With
`section_repair_bands=None` (26 of 27 corpus pages) M1 costs **nothing** — the unrepaired build
*is* the build.

### A2. Wall-clock `page_bands`, before vs after

`time_page_bands.py`, two consecutive calls per case (no caching exists — spec § 3.5), run once on
the baseline tree (`git checkout -- src/iladub/etkl/compile.py`) and once with the prototype applied.

| case | page | `section_repair_bands` | bands before → after | before (s) | after (s) | factor |
| --- | --- | --- | --- | --- | --- | --- |
| apple | 0 | None | 8 → **3** | 2.873 / 2.470 | 5.641 / 5.401 | **2.1x** |
| apple | 1 | None | 8 → **3** | 1.445 / 1.475 | 2.973 / 2.995 | **2.0x** |
| ons | 7 | None | 16 → 16 | 0.414 / 0.401 | 0.460 / 0.422 | 1.08x |
| graincorp-stem | 0 | None | 4 → 4 | 2.767 / 2.704 | 5.916 / 5.745 | **2.1x** |
| cbh | 0 | None | 10 → 10 | 1.372 / 1.347 | 1.382 / 1.348 | 1.00x |
| cbh | 0 | `[1,3,5,7]` | 10 → 10 | 1.352 / 1.357 | 1.854 / 1.750 | 1.33x |

### A3. WHERE the cost is — and the finding the spec did not anticipate

Per-stage timing of the disposal on every page that has a run (`stage_cost.py`):

```
--- apple p0: 8 bands, runs=[(2, 7)]
    2..7: merge=0.000s cand=True (1.251s) classify=MatrixRegion (1.255s) assert=124 (0.017s) tiles=True (0.606s)
--- apple p1: 8 bands, runs=[(2, 7)]
    2..7: merge=0.000s cand=True (0.494s) classify=MatrixRegion (0.494s) assert=56 (0.010s) tiles=True (0.503s)
--- ons p7: 16 bands, runs=[(2, 15)]
    2..15: merge=0.000s cand=False (0.006s)
--- gc-stem p0: 4 bands, runs=[(1, 2)]
    1..2: merge=0.000s cand=False (3.063s)
--- gc-cap p0: 5 bands, runs=[(1, 3)]
    1..3: merge=0.000s cand=False (1.695s)
--- bfs p5: 15 bands, runs=[(2, 5), (7, 8)]
    2..5: merge=0.000s cand=False (0.002s)
    7..8: merge=0.000s cand=False (0.000s)
```

**A REFUSAL IS NOT FREE.** Spec § 3.2 says *"A refusal must cost nothing observable: no triple, no
decision-log node, no report."* That is true of the graph and false of the clock: graincorp-stem p0's
run `1..2` is refused **at the first stage**, `is_matrix_candidate`, and that single call costs
**3.06s** — it more than doubles the page (2.70s → 5.75s). graincorp-capacity p0 pays 1.70s for the
same refusal. `is_matrix_candidate` is cheap on small merged bands (bfs p5: 2ms; ons p7: 6ms) and
expensive on the ones with a lot of ink — which is exactly the R168 population.

Consequence for the budget (§ 3.5): the pruner reduces 266 runs to 14, but the 14 are not uniformly
cheap, and **the corpus's most expensive disposals are the two that are refused**. `page_bands` is
called ≥2x per page per document compile with no caching, so a graincorp document compile pays that
3.06s at every call. Whether that is acceptable is a plan decision; it is not a rounding error.

### A4. M1 verified empirically — but the verification available on this corpus is WEAK, and that must be said

The requested check: partition identical with `section_repair_bands=None` and with a non-empty set,
on a page where section repair actually fires. cbh p0 is the only such page.

```
srb=None:         bands=10  runs_over_returned=[]
   extents: [(34.1,52.9,2),(65.4,199.1,18),(209.8,215.8,1),(226.7,383.4,21),(394.1,400.1,1),
             (411.0,560.1,20),(570.8,576.8,1),(587.7,656.0,10),(666.7,672.7,1),(683.5,761.5,10)]
srb=[1, 3, 5, 7]: bands=10  runs_over_returned=[]
   extents: [(34.1,52.9,2),(105.4,199.1,13),(209.8,215.8,1),(241.5,383.4,19),(394.1,400.1,1),
             (434.3,560.1,17),(570.8,576.8,1),(602.6,656.0,8),(666.7,672.7,1),(683.5,761.5,10)]
   band 1: unrepaired lines=18 | repaired lines=13  -> DIFFERS
   band 3: unrepaired lines=21 | repaired lines=19  -> DIFFERS
   band 5: unrepaired lines=20 | repaired lines=17  -> DIFFERS
   band 7: unrepaired lines=10 | repaired lines=8   -> DIFFERS
```

The partition is **identical** (10 bands, same index space, no run in either case) while the four
named bands genuinely change (the peel moves their `top` and drops lines) — which is precisely the
M1 shape: constituents change, partition does not.

**But the test is weak, and the weakness is structural, not accidental:**

- the run set on cbh p0 is **empty in both cases**, so "the partition is identical" is the identity
  of two empty partitions;
- the relation half of M1 is **free by construction** and the spec already says so
  (`sub_rules` passes through `_build_ruled_band` untouched): a relation over rule x's cannot vary
  with `section_repair`. I re-confirmed it holds here and it is not news;
- the half that M1 actually exists for — **the disposal verdict differing between a repaired and an
  unrepaired build** — is **UNEXERCISED ON THIS CORPUS**, because the one page with a repair set has
  no candidate run at all. No corpus page has both.

**VERDICT Q-A: PARTIAL — M1 is implementable and cheap (one extra `_build_ruled_band` per named
band; free when the repair set is empty), but its load-bearing half cannot be validated on this
corpus, and the seam's real cost is 2.0-2.1x on three of six pages, driven by `is_matrix_candidate`
on large merged bands, including on runs that are REFUSED.**

---

## Q-B — the O5 technique: does the forced NON-TAIL merge work?

### B1. The patch point — the spec's prescribed one does NOT work; a different one does

Spec § 5, O5: *"With `region_tiles`/`is_matrix_candidate` patched to accept `(2,5)` for that one
call…"*. Measured what the chain actually does on the bfs p5 `(2,5)` merged band (`qb_stage.py`):

```
bfs p5 raw bands: 15
merged lines 27 rules 19 col_xs 0
is_matrix_candidate -> False
classify_matrix -> None
```

**`classify_matrix` refuses independently.** Patching `is_matrix_candidate` to `True` is therefore
not sufficient: the chain then calls `classify_matrix`, gets `None`, and refuses at stage 2. Patching
`classify_matrix` too would mean **fabricating a `MatrixRegion`** for a band that has none — which is
patching the geometry, exactly what O5 forbids. **O5's stated technique is REFUTED at the mechanism.**

The lookup *is* late-bound, which is worth recording separately because it was the other half of the
question (`qb_force.py` section A):

```
=== A. is the lookup late-bound? patch iladub.etkl.matrix.is_matrix_candidate
   the patched callable WAS reached: True   call band line-counts: [27, 4]
   bands returned: 15   (classify_matrix still refuses -> no merge)
```

So `monkeypatch.setattr("iladub.etkl.matrix.is_matrix_candidate", …)` **does** reach the disposal
(the prototype's function-level `from .matrix import …` resolves the module attribute at call time,
matching the shipped idiom at `compile.py:817`). It just cannot force an acceptance on its own.

**THE ATTRIBUTE PATH THAT WORKS:** the **admissibility predicate itself** — in the prototype
`iladub.etkl.compile._proto_run_admissible`, called by `page_bands` as a plain module-global name
lookup, so `monkeypatch.setattr(compile, "_proto_run_admissible", fake)` reaches it. In the shipped
design this is whatever § 3.2 step 2 is named. It is still "patching the disposal, never the
geometry" — it *is* the disposal, taken whole rather than at one of its four stages. **The plan must
name that function in § 6's interface table so O5 has a patch point at all.**

### B2. With `(2,5)` force-accepted: the index space is single, dense, and correct

`qb_frag2.py` — same page compiled twice, once with the predicate refusing everything (=today's
behaviour), once accepting `(2,5)` only:

```
--- BASELINE-equivalent: regions=15 positions=0..14
    minted (kind, index): [('htable',2),('htable',9),('htable',10),('htable',11),('htable',12),
                           ('region',0..14 all present),('ttable',13)]
    distinct indices minted: [0..14]      every minted index < len(regions): True
    positions with an escalation-or-table: [2, 7, 9, 10, 11, 12, 13]   minted ⊇ those: True

--- FORCED (2,5): regions=12 positions=0..11
    minted (kind, index): [('htable',6),('htable',7),('htable',8),('htable',9),
                           ('region',0..11 all present),('ttable',10)]
    distinct indices minted: [0..11]      every minted index < len(regions): True
    positions with an escalation-or-table: [4, 6, 7, 8, 9, 10]         minted ⊇ those: True
```

- `page_bands` returns **12** bands. ✔ (the run `2..5` — four bands — becomes one)
- indices are **0..11 with no gap**. ✔
- every minted `#regionN` / `#ttableN` / `#htableN` fragment index is `< len(regions)` and matches
  its report position. ✔ The renumbering is consistent end to end: baseline `region7 → region4`,
  `region9..12 → region6..9`, `ttable13 → ttable10` — each shifted by exactly 3, the number of
  indices the merge removes.
- verdict shift check: baseline `[.., 2 escalated, .., 7 escalated, .., 13 asserted(7 cells), 14 ignored]`
  → forced `[.., 2 ignored(the merged band), .., 4 escalated, .., 10 asserted(7 cells), 11 ignored]`.
  The 7 asserted cells survive the renumbering; the merged band itself is `ignored` (bands 2..5
  asserted 0 cells today, per spec § 3.3 Q3, so nothing is lost).

Note `tab:bandIndex` does **not** appear in the compile graph at all — it is `sectiongraph`'s
evidence-graph term. The index reaches the compile graph as the `#region{idx}` / `#region{idx}-reading`
URI fragments (`decisionlog.py:102-110`). **O4 as written ("every `RegionReport`'s position equals the
`tab:bandIndex` on its decision-log nodes") therefore asserts something about a term that is not in
that graph** — the satisfiable form is the fragment/position equality measured above.

### B3. Document scope completes; adoption's `grid_idx` tracks — but its branch was NOT exercised

`qb_doc.py` — `compile_document('corpus/gov-stats/bfs-population-bilan-2023.pdf',
validate_shapes=False)` with the predicate accepting `(2,5)` on page 5 only, and `compile.page_bands` /
`document.page_bands` spied:

```
compile_document COMPLETED in 23.0s
  score: 0.35837245696400627
  per-page regions: [9, 11, 8, 7, 1, 12, 12]
  adopted: ()  repaired_bands: ()
  notes: ['page 0: adoption refused — no data grid region on the re-compile',
          'page 4: adoption refused — no data grid region on the re-compile']
  page_bands calls (page, nbands, srb): [(0,9,None),(0,9,None),(1,11,None),(1,11,None),(2,8,None),
    (2,8,None),(3,7,None),(3,7,None),(4,1,None),(4,1,None),(5,12,None),(5,12,None),(6,12,None),
    (6,12,None),(0,9,None),(4,1,None)]
```

**No exception.** `len(pages[5].regions) == 12 == len(page_bands(pdf, 5))`, so `grid_idx`
(`document.py:1657`) equals the page's band count on the merged page — the two sides move together
because both read the same `page_bands` output, as § 3.0 predicts. Both `page_bands` calls for page 5
(the driver inventory at `document.py:1410` and the one inside `compile_tables`) return **12**.

**Caveat, stated because the brief demands the failure be named:** adoption's re-compile fired only
on pages **0 and 4**, and was refused on both. **The adoption branch was never entered on the merged
page.** So `grid_idx == band count` is verified as an equality of counts, *not* as a successful trip
through `document.py:1657-1740`. bfs offers no page that both merges and adopts; neither does apple
(`adopted=()` in both baseline and merged runs, spike § 8.4). **That gap is R169's real shape and it
is wider than R169 states.**

**VERDICT Q-B: PARTIAL — the forced non-tail merge WORKS and the index machinery is correct
(12 bands, 0..11, fragments track positions, document compile completes), but O5's *prescribed patch
point is REFUTED* (`classify_matrix` refuses independently of `is_matrix_candidate`), O4's
`tab:bandIndex` clause is unsatisfiable as written, and adoption's branch is not reached by the
fixture at all.**

---

## Q-C — which index-pinning tests ACTUALLY change

### C1. The file set that was run, and how it was chosen

Spike § 8.5(d) claims *"20 test files pin a band index"* but **names only six**. I therefore derived
the candidate set mechanically and ran it — never the full suite.

```
$ grep -rlE "regions\[[0-9]|#(m|t|rh|h)?table[0-9]|#region[0-9]|page_bands|bandIndex|band [0-9]" tests/ | sort
   → 29 paths, of which 27 are test modules (the other two are tests/corpus-manifest.ttl and
     tests/etkl/fixtures.py)
```

**That grep MISSES one of § 8.5(d)'s own six**: `tests/etkl/test_supersession_queries.py` pins band
indices through named constants (`REPAIRED = 1`, `UNREPAIRED = 0`, `test_supersession_queries.py:17-18`),
which no index-shaped regex finds. It was added by hand and run separately. **Final set: 28 modules.**

### C2. The result — 14 failures in 5 files, all apple

```
$ python3 -m pytest <27 modules> -q --tb=line -p no:randomly --durations=25
14 failed, 254 passed in 813.42s (0:13:33)

FAILED tests/etkl/test_apple_statement_headers.py::test_p0_income_statement_header_is_three_levels
FAILED tests/etkl/test_apple_statement_headers.py::test_p1_balance_sheet_header_is_two_levels
FAILED tests/etkl/test_datagrid.py::test_fallback_never_masks_an_escalation
FAILED tests/etkl/test_datagrid.py::test_adoption_never_touches_a_page_that_read_something
FAILED tests/etkl/test_decision_queries.py::test_why_escalated_returns_an_ordered_chain
FAILED tests/etkl/test_decision_queries.py::test_what_was_considered_shows_the_thin_option_space
FAILED tests/etkl/test_decision_queries.py::test_a_positive_justification_refutes_nothing
FAILED tests/etkl/test_decision_queries.py::test_judgement_order_answers_the_r55_question
FAILED tests/etkl/test_decisionlog.py::test_the_kind_rejection_is_recorded_for_band_3
FAILED tests/etkl/test_decisionlog.py::test_band_4_records_transposed_before_coherence
FAILED tests/etkl/test_decisionlog.py::test_region_tiles_rationale_names_the_real_unit
FAILED tests/etkl/test_decisionlog.py::test_recording_does_not_change_the_verdicts
FAILED tests/etkl/test_typing_equiv.py::test_band_verdicts_are_recorded_and_stable[apple]
FAILED tests/etkl/test_typing_equiv.py::test_apple_band_4_is_no_longer_seen_as_transposed

$ python3 -m pytest tests/etkl/test_supersession_queries.py -q --tb=line -p no:randomly
5 passed in 29.96s                      # ← under the PROTOTYPE
```

**Baseline control** (`git checkout -- src/iladub/etkl/compile.py`, same five files):

```
$ python3 -m pytest tests/etkl/test_apple_statement_headers.py tests/etkl/test_datagrid.py \
      tests/etkl/test_decision_queries.py tests/etkl/test_decisionlog.py \
      tests/etkl/test_typing_equiv.py -q --tb=line -p no:randomly
88 passed, 2 skipped in 264.44s (0:04:24)
```

So **all 14 failures are caused by the prototype**; none is pre-existing.

### C3. Every failure, with the assertion that failed

| # | test | assertion (from `--tb=line`) | what moved |
| --- | --- | --- | --- |
| 1 | `test_apple_statement_headers.py::test_p0_income_statement_header_is_three_levels` | `:40 assert (38 == 9)` — `len(MatrixRegion.leaf_rows)` | one band ⇒ 38 leaf rows, not 9 |
| 2 | `…::test_p1_balance_sheet_header_is_two_levels` | `:52 assert 56 == 14` | apple p1 entry count 14 → 56 |
| 3 | `test_datagrid.py::test_fallback_never_masks_an_escalation` | `:907 "fixture drift: this page is supposed to escalate" — assert 0 > 0`, `report.escalated == 0` | the fixture page no longer escalates anything |
| 4 | `…::test_adoption_never_touches_a_page_that_read_something` | `:1155 assert 124 == 48` | apple p0 cells 48 → 124 |
| 5 | `test_decision_queries.py::test_why_escalated_returns_an_ordered_chain` | `:33 "no chain for band 3" — assert []` | apple p0 has no band 3 any more |
| 6 | `…::test_what_was_considered_shows_the_thin_option_space` | `:50 assert set() == {'NON_TABLE','RECORD_TABLE','UNSUPPORTED_TABLE'}` | same, band 3 gone |
| 7 | `…::test_a_positive_justification_refutes_nothing` | `:69 assert set() == {…}` | same |
| 8 | `…::test_judgement_order_answers_the_r55_question` | `:79 assert 'transposed' in {}` | apple p0 band 4 (the transposed judgement) is inside the merged band |
| 9 | `test_decisionlog.py::test_the_kind_rejection_is_recorded_for_band_3` | `:243 "band 3's kind rejection is not in the record; got ['fewer than 2 lines','fewer than 2 lines','fewer than 2 columns','fewer than 2 columns','header has 2 words but 3 columns']"` | band 3 gone |
| 10 | `…::test_band_4_records_transposed_before_coherence` | `:259 "no transposed judgement recorded; got []"` | band 4 gone |
| 11 | `…::test_region_tiles_rationale_names_the_real_unit` | `:340 "the apple corpus doc's page 0 does not exercise the assert_hier_region (body-token) region_tiles path — cannot assert the unit fix on this fixture"` | the merged read never takes the hier path |
| 12 | `…::test_recording_does_not_change_the_verdicts` | `:374 "score moved: 1.0" — assert 0.6757 < 0.0001` (0.3243 → 1.0) | apple p0 page score |
| 13 | `test_typing_equiv.py::test_band_verdicts_are_recorded_and_stable[apple]` | `:111` got a **3**-entry list, expected the **8**-entry positional list | `EXPECTED_VERDICTS["apple"]`, exactly as O4 predicts |
| 14 | `…::test_apple_band_4_is_no_longer_seen_as_transposed` | `:139 assert 'UNSUPPORTED_TABLE' == 'RECORD_TABLE'` | index 4 now names a different band |

### C4. What § 8.5(d) got right, and what it got wrong

**Right (5 of its 6):** `test_typing_equiv.py`, `test_apple_statement_headers.py`,
`test_decision_queries.py`, `test_decisionlog.py`, `test_datagrid.py` all fail, and
`test_typing_equiv`'s failure is exactly the 8-entry → 3-entry list O4 names.

**WRONG — flagged as required:**

- **`tests/etkl/test_supersession_queries.py` does NOT change.** § 8.5(d) names it; it is **5 passed**
  under the prototype. Its band indices are cbh's, and cbh p0's partition is untouched (Q-A A4).
- **The "20 test files pin a band index" figure over-predicts by ~4x for this change.** Of the 27
  modules the mechanical grep found, **22 are untouched**: `test_adoption_gate`, `test_adoption_ledger`,
  `test_b1_3_merge_resolution`, `test_boundary_cuts_ink`, `test_continuation_licence`, `test_document`,
  `test_grid`, `test_holon`, `test_kind_gate_is_load_bearing`, `test_matrix`, `test_physical_gate`,
  `test_promote_shacl`, `test_rowrole_resolution`, `test_section_repair`, `test_span_promotion`,
  `test_transposed_chain`, `test_unit_marker`, `test_vacuity_registry`, `test_feed_section_keys`,
  `test_forced_carriage_spike`, `test_one_band_matrix_spike`, `test_section_repair_census`
  (+ `test_supersession_queries`). Notably **`test_document.py` and `test_section_repair.py` are green.**
- **Nothing failed that the list did not predict**, at the FILE level. At the TEST level, § 8.5(d)
  predicted "at least the apple rows of `test_typing_equiv` and every apple assertion in the other
  four" — that holds, and adds `test_datagrid.py:907` (`test_fallback_never_masks_an_escalation`),
  which is a **fixture-drift guard** rather than an index pin: the page it uses stops escalating
  altogether. A guard whose own message says "fixture drift" is the kind the plan must re-baseline
  deliberately, not silently.
- **Every one of the 14 is apple.** Not one non-apple corpus regression moved — which is O2's claim
  (the fallback saves graincorp/bfs/ons/cbh ink) demonstrated in the existing test surface rather
  than in a new test.

**VERDICT Q-C: CONFIRMED with one refutation — 14 tests in 5 files change, all apple-driven, all
baseline-green; § 8.5(d)'s `test_supersession_queries.py` prediction is REFUTED, and its "20 files"
figure is a read-off-the-source over-estimate (22 of the 27 index-referencing modules are untouched).**

---

## What this changes for the plan

1. **The seam is confirmed and the fallback is clean.** `page_bands` can propose a run, offer it to
   the untouched disposal chain on a scratch graph, and splice — and a refused run leaves the page
   exactly as it is today (22 test modules and 4 of 5 non-apple corpus documents stayed green).
   Spec § 8's *"nothing shows `page_bands` can be restructured to propose a run and fall back
   cleanly"* is now shown. **§ 3.0 and § 3.2 need no change.**

2. **M1 is cheap and the plan can state its shape.** Keep `(sub, sub_rules, sub_hrules)` per index
   while building unrepaired, then re-build only the named indices repaired: **+1
   `_build_ruled_band` per named band, zero when the repair set is empty.** Measured 5 → 9 calls on
   cbh p0. **§ 3.1's open question ("one extra `_build_ruled_band` per named band, or a whole second
   page build?") is answered: the former.**

3. **§ 3.2's "a refusal costs nothing" must be qualified: it costs nothing IN THE GRAPH and up to
   3.06 s ON THE CLOCK.** `is_matrix_candidate` on graincorp-stem p0's merged `1..2` band is the
   single most expensive call the change introduces, and it is on a run that is **refused**.
   `page_bands` per-page cost roughly **doubles** on apple p0/p1 and graincorp-stem p0.
   The plan's § 3.5 budget task must measure the corpus-suite wall-clock **and** decide whether the
   disposal needs memoising across the ≥2 `page_bands` calls per page (there is no cache today).
   This is also fresh evidence for **R168**: the guard holding 976 cells is not only unspecified for
   the job, it is the most expensive call in the design.

4. **O5 must be rewritten. Its prescribed patch point does not work.** `classify_matrix` refuses
   bfs p5's `(2,5)` merged band *independently* of `is_matrix_candidate`, so patching
   `is_matrix_candidate`/`region_tiles` cannot force an acceptance, and patching `classify_matrix`
   would mean fabricating a `MatrixRegion` — patching the geometry, which O5 forbids. **The plan must
   give the run-admissibility predicate a NAME in § 6's interface table and make O5 patch that**
   (`monkeypatch.setattr(compile, "<that name>", …)` — a plain module-global lookup inside
   `page_bands`, verified reachable). Everything else O5 asserts then HOLDS: 12 bands, indices
   `0..11` with no gap, every minted fragment index matching its report position, and
   `compile_document` over bfs completing in 23.0 s.

5. **O4's `tab:bandIndex` clause is unsatisfiable and must be substituted.** `tab:bandIndex` never
   appears in the compile graph — it is `sectiongraph`'s evidence-graph term. The index reaches the
   compile graph as the `#region{idx}` / `#region{idx}-reading` URI fragments
   (`decisionlog.py:102-110`). The satisfiable form carrying the same force: *every minted
   `#regionN`/`#tableN`/`#mtableN`/`#ttableN`/`#htableN` fragment index is `< len(report.regions)`
   and names the report position it describes* — which is what was measured here. (Plan rule 5:
   this is a spec defect found by measuring the test's setup, not a weakening.)

6. **O4's expected test-surface list is now measured, not read.** 14 tests in 5 files:
   `test_typing_equiv` (2), `test_apple_statement_headers` (2), `test_decision_queries` (4),
   `test_decisionlog` (4), `test_datagrid` (2). **`test_supersession_queries.py` is NOT one of
   them** — the plan must not budget a re-baseline for it. `test_datagrid.py:907`
   (`test_fallback_never_masks_an_escalation`) is a *fixture-drift guard*, not an index pin; it needs
   a deliberate ruling, not a re-baseline.

7. **Two gaps the corpus cannot close, and the plan should say so rather than imply coverage:**
   - **M1's load-bearing half is unexercised.** The only page with a non-empty
     `section_repair_bands` (cbh p0) has **no candidate run**, so "the disposal verdict differs
     between a repaired and an unrepaired build" is never tested. M1 is upheld by construction, not
     by evidence. **This is wider than R169 states and deserves its own note.**
   - **Adoption's branch is never entered on a merged page.** In the O5 fixture, adoption fired only
     on bfs p0 and p4 and was refused on both; on apple, `adopted=()` in baseline and merged alike.
     `grid_idx == len(page_bands(...))` is verified as an equality of counts (12 == 12), *not* as a
     successful trip through `document.py:1657-1740`.

8. **The three residues stand as written.** Nothing measured here closes R168, R169 or R170;
   item 3 above sharpens R168 and item 7 sharpens R169.

---

## Q-D — the vocabulary and register seams, measured controller-side while the spike ran

Not part of the handoff's three PROPOSED items. Measured 2026-09-04 at `9ef63cb` because the plan's
first task depends on all six, and two of them contradict the spec.

### D1. `tab:ruleX` is NOT a new term — spec § 6 is REFUTED on one of its two

```
$ grep -rn "ruleX" --include="*.py" --include="*.rq" --include="*.ttl" src tests vocab scripts \
      | grep -v ruleXsSignature
src/iladub/etkl/gridregion.py:59:        g.add((u, TAB.ruleX, Literal(Decimal(str(round(r.x, 2))))))
vocab/queries/grid-region-ink.rq:31:  ?r a tab:RuleSpan ; tab:ruleX ?x ; tab:ruleTop ?rt ; tab:ruleBottom ?rb ;
vocab/ontology/tab.ttl:290:tab:ruleX a owl:DatatypeProperty ; rdfs:domain tab:RuleSpan ; rdfs:range xsd:decimal .
vocab/queries/grid-region.rq:12:      ?rr a tab:RuleSpan ; tab:ruleX ?rx .
vocab/queries/grid-region.rq:17:    ?r a tab:RuleSpan ; tab:ruleX ?x ; tab:ruleTop ?rt ; tab:ruleBottom ?rb .
```

Spec § 6 asks for *"two new declared terms … `tab:ruleX` — one distinct rounded rule x-position.
Declared beside `tab:ruleXsSignature`"*. It exists already, in live use by two shipped queries, with
`rdfs:domain tab:RuleSpan` — **not** the new `tab:RuledBand`. Putting it on a `tab:RuledBand` node
asserts a domain disagreement of exactly the class `tests/test_probe_domain_range_agreement.py`
grades (`scripts/probe_domain_range_agreement.py`'s `DISAGREE` bucket: *"the node IS typed — just not
as the domain/range rule says … a MODELLING decision"*).

**This is a decision the plan must take and justify, not a naming detail.** Two shapes are open:
(a) one new datatype property on the new class (`tab:bandRuleX`), no path traversal, no reuse
conflict; or (b) emit real `tab:RuleSpan` nodes — the `gridregion.py:53-58` idiom — linked from the
`tab:RuledBand` by one new object property, reusing `tab:ruleX` verbatim at the cost of a property
path in the derivation. **Whichever it takes, it must also state whether the new transient graph is
inside `probe_domain_range_agreement`'s population** — that was not measured here.

### D2. A new `.rq` moves a population pin the spec does not name

```
$ sed -n '62p' tests/test_query_terms.py
    assert len(query_files()) == 49, len(query_files())
```

`tests/test_query_terms.py::test_the_population_is_every_file_in_vocab_queries` enumerates
`vocab/queries/*.rq` from the directory and pins the count. The spec's § 6 names
`tests/test_query_declarations.py` and `tests/test_query_terms.py` as the tests a *new term* must
satisfy, but not this count: **49 → 50**, and the docstring convention is to record the re-measurement
and its cause in place (see its 46 → 48 → 49 history).

### D3. `tab:bandIndex` is emitted at exactly ONE site — independent confirmation of § Q-B's O4 refutation

```
$ grep -rn "bandIndex" src/iladub/
src/iladub/etkl/sectiongraph.py:205:        g.add((u, TAB.bandIndex, Literal(idx, datatype=XSD.integer)))
```

One site, and it is the transient section-recognition evidence graph. The compile graph carries the
index only as a URI fragment, minted at `decisionlog.py:102-110`
(`prefix = f"{self._doc}#region{idx}"`, `band_node = URIRef(f"{prefix}-reading")`). O4's clause
*"every `RegionReport`'s position equals the `tab:bandIndex` on its decision-log nodes"* therefore
names a term that is not in the graph it validates. Substitute the fragment/position equality § Q-B
B2 measured.

### D4. The apple pin O4 predicts, located

`tests/etkl/test_typing_equiv.py:70-79` is the 8-entry positional `EXPECTED_VERDICTS["apple"]` list;
`_band_verdicts` (`:83-95`) builds it by calling `page_bands` directly and classifying each returned
band, so it moves with the partition and not with anything downstream. `EXPECTED_VERDICTS` also holds
`stem`, `cbh` and `capacity` lists — Q-C measured all three unchanged.

### D5. The register's next rows, computed rather than guessed

```
$ awk -F'|' '/^\| ~?~?R[0-9]/{t++; if ($3 ~ /closed/) c++} END{print c"/"t" closed"}' \
      docs/superpowers/residues.md
43/157 closed
```

Highest existing row is `R167`, so the spec § 7 numbering holds. Per the register's snapshot
convention the rows the plan raises are **`R168 (43/157 closed)`**, **`R169 (43/158 closed)`**,
**`R170 (43/159 closed)`** — the tally is the count at the moment each row is raised and is never
updated afterwards.

### D6. The manifest note the Doc-impact increment lands in

`tests/corpus-manifest.ttl:105-118` is apple's entry; `:118` is the 2026-09-02 `cor:adjudication`
node whose rationale pins `0.18950437317784258`. The register is **append-only**: the plan adds a
third `cor:adjudication` node and repairs nothing in place (the 2026-09-02 note itself models this,
superseding the 2026-08-20 framing while leaving its measurements standing).

---

## Appendix — the prototype, in full

Applied to the working tree, measured, reverted. **It is not an implementation and must not be
copied into one**: its relation is plain Python where the design requires a SPARQL derivation (§ 0),
and its names carry a `_proto_` prefix for that reason. It is committed so every figure above is
reproducible from this file alone.

```diff
diff --git a/src/iladub/etkl/compile.py b/src/iladub/etkl/compile.py
index 16019c9..d74efcd 100644
--- a/src/iladub/etkl/compile.py
+++ b/src/iladub/etkl/compile.py
@@ -267,6 +267,73 @@ def _marker_word_count(band) -> int:
     return sum(len(m[2]) for m in getattr(band, "unit_markers", ()) or ())
 
 
+def _proto_merge_bands(bands, first: int, last: int):
+    """PROTOTYPE (R165 pre-plan spike, throwaway): the spike's merge_bands verbatim
+    (scripts/one_band_matrix_spike.py:37-55)."""
+    from .bands import Band
+    run = bands[first:last + 1]
+    lines = tuple(ln for b in run for ln in b.lines)
+    col_xs = next((b.column_xs for b in run if b.column_xs), ())
+    return Band(
+        lines=lines,
+        top=min(b.top for b in run),
+        bottom=max(b.bottom for b in run),
+        rules=tuple(r for b in run for r in b.rules),
+        hrules=tuple(h for b in run for h in b.hrules),
+        column_xs=col_xs,
+        captions=tuple(c for b in run for c in b.captions),
+        unit_markers=tuple(m for b in run for m in b.unit_markers),
+    )
+
+
+def _proto_rule_x_set(band):
+    """PROTOTYPE substitution for the shipped SPARQL derivation (spec § 3.4): the band's
+    distinct rounded rule x positions, or None when the band carries no rules."""
+    if not band.rules:
+        return None
+    return frozenset("%.2f" % round(r.x, 2) for r in band.rules)
+
+
+def _proto_run_candidates(bands):
+    """PROTOTYPE (plain Python, spec § 3.3 relation B): maximal contiguous runs of >=2
+    bands where each adjacent pair's rule-x sets are comparable by subsumption."""
+    sets = [_proto_rule_x_set(b) for b in bands]
+    out = []
+    i, n = 0, len(sets)
+    while i < n:
+        if not sets[i]:
+            i += 1
+            continue
+        j = i
+        while j + 1 < n and sets[j + 1] and (
+            sets[j] <= sets[j + 1] or sets[j + 1] <= sets[j]
+        ):
+            j += 1
+        if j > i:
+            out.append((i, j))
+        i = j + 1
+    return out
+
+
+def _proto_run_admissible(bands, first: int, last: int, page_number: int) -> bool:
+    """PROTOTYPE: offers the merged band to the EXISTING disposal chain (compile.py:817-840)
+    on a scratch graph. Module attributes are resolved at call time, so monkeypatch reaches
+    them."""
+    from .matrix import is_matrix_candidate, classify_matrix
+    from .holon import assert_matrix_region
+    from .tiling import region_tiles
+    merged = _proto_merge_bands(bands, first, last)
+    if not is_matrix_candidate(merged):
+        return False
+    mreg = classify_matrix(merged)
+    if mreg is None:
+        return False
+    scratch = Graph()
+    n = assert_matrix_region(scratch, mreg, merged,
+                             URIRef(f"{_DOC}#mtableRUN{first}"), _DOC, page_number)
+    return bool(n) and bool(region_tiles(scratch))
+
+
 def page_bands(pdf_path: str, page_number: int = 0,
                section_repair_bands: frozenset[int] | None = None):
     """The page's bands, exactly as compile_tables reads them (band i here IS band i there).
@@ -304,6 +371,7 @@ def page_bands(pdf_path: str, page_number: int = 0,
     page_chars = extract_chars(pdf_path, page_number) if page_rules else []
     raw_bands = detect_bands(text_lines(words))
     bands = []
+    specs = []                            # PROTOTYPE: per-index (sub, sub_rules, sub_hrules)
     for band in raw_bands:
         for sub in segment(band):
             sub_rules = tuple(r for r in page_rules if r.top <= sub.bottom and r.bottom >= sub.top)
@@ -311,15 +379,34 @@ def page_bands(pdf_path: str, page_number: int = 0,
             idx = len(bands)             # the position this band is about to occupy
             if not sub_rules:
                 bands.append(_replace(sub, hrules=sub_hrules) if sub_hrules else sub)
+                specs.append(None)
                 continue
             # RULED band: re-extract cells by the ruled columns (splits pdfplumber-merged blobs at
             # the author's exact boundaries) — else keep pdfplumber's words. Candidate boundaries
             # become columns only when the header confirms them (_build_ruled_band, the seam).
-            section_repair = bool(section_repair_bands) and idx in section_repair_bands
+            # PROTOTYPE / M1: EVERY band builds unrepaired here; the repair flag is applied
+            # below, WITHIN the partition this unrepaired list decides.
             bands.append(_build_ruled_band(sub, sub_rules, sub_hrules, page_chars,
-                                           section_repair=section_repair))
+                                           section_repair=False))
+            specs.append((sub, sub_rules, sub_hrules))
     from .unitmarker import absorb_unit_markers
     bands = [absorb_unit_markers(b) for b in bands]
+    # --- PROTOTYPE, M1 (spec § 3.1): the run partition is a pure function of the
+    #     section_repair=False build above.
+    runs = [(a, b) for (a, b) in _proto_run_candidates(bands)
+            if _proto_run_admissible(bands, a, b, page_number)]
+    # --- PROTOTYPE, M1 second half: re-build ONLY the named bands, repaired, in place.
+    if section_repair_bands:
+        for idx in sorted(section_repair_bands):
+            if 0 <= idx < len(bands) and specs[idx] is not None:
+                sub, sub_rules, sub_hrules = specs[idx]
+                bands[idx] = absorb_unit_markers(
+                    _build_ruled_band(sub, sub_rules, sub_hrules, page_chars,
+                                      section_repair=True))
+    # --- PROTOTYPE: replace each accepted run by its merged band, descending so the
+    #     surviving indices stay valid while splicing.
+    for first, last in sorted(runs, reverse=True):
+        bands[first:last + 1] = [_proto_merge_bands(bands, first, last)]
     return bands
 
 
```
