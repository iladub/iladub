# Evidence — the score gate: compiling the corpus under the alignment universe

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Doc impact: none.**

The gate three loops deferred. PR #236 refuted [[R239]]'s prescribed `x1` re-key (20 cells
regressed); PR #237 located the defect in the column **universe** and measured the switch at
**grid** scope; PR #238 refuted the straddle discriminator's universal form (48/48). **None of
the three compiled a document.** Every remaining remedy shape stands or falls on what follows.

---

## 1. What is patched, and the proof it reaches the compile path

`_boundaries_from_decoration` returns `None`, so every page that would have used a decoration
rectangle falls back to the alignment universe. The instrument is
`scripts/r239_alignment_universe_gate.py` (§ 8 class: PROCEDURAL).

The load-bearing claim is that a module-attribute rebind reaches `compile_document`, and not
only `derive_data_grid`. `corpus_verdict_snapshot.py`'s own docstring records the hazard that
would defeat it — `from .celltype import is_blank` binds the name at import in three modules, so
patching the origin reaches none of them. **Measured at `d653036`, not assumed:**

```
$ grep -rn "_boundaries_from_decoration" --include="*.py" src scripts tests | grep -v "scripts/r239"
src/iladub/etkl/datagrid.py:302:def _boundaries_from_decoration(rules: list[float], page_runs: list[list[Run]]
src/iladub/etkl/datagrid.py:342:    decor = _boundaries_from_decoration(drawn_rules(pdf_path, page_number), runs)

$ grep -rn "datagrid" --include="*.py" src | grep -i import
src/iladub/etkl/donation.py:120:    from .datagrid import derive_data_grid
src/iladub/etkl/compile.py:1406:        from .datagrid import derive_data_grid, emit_data_grid
src/iladub/etkl/compile.py:1505:        from .datagrid import derive_data_grid as _dg, emit_data_grid as _emit
src/iladub/etkl/compile.py:1615:        from .datagrid import page_has_table
```

One definition, **one call site, in its own module**, resolved as a module-global at call time.
No module binds the name at import. The importers take `derive_data_grid` / `emit_data_grid` /
`page_has_table`, each of which looks the patched global up when it runs. The `is_blank` hazard
does not apply here — **and the null control below is what proves that rather than arguing it.**

## 2. The reading rule, pre-registered

**Written and committed before any figure was visible**, with the baseline run still in flight.
The preceding loop's cost note is the reason: a verdict formed after seeing the numbers is
indistinguishable, in the write-up, from a measurement. Its subject there was a free parameter
inside a question; here it is the direction of a score.

### 2a. Controls — if any fails, every figure below is VOID

| # | Control | Must read |
| --- | --- | --- |
| **N1** | **Null run.** The patch mechanism installed but delegating to the original function. | All **7** canonical graph hashes identical to `before`. Any difference means the harness perturbs the reading and measures itself. |
| **N2** | **In-run null, free.** Only 3 pages corpus-wide carry a decoration universe — bfs p5, cbh p0, graincorp-capacity p0 (PR #237 § 4, control 3 → 0 / grids 16 → 16). | Under `alignment`, the **four** documents with no decoration page — graincorp-stem, apple, ons, who-wfa — byte-identical to `before`. A move there is an unknown coupling or an artefact, **not** the universe switch. |
| **P** | Positive. | At least one of the three decoration documents moves. If none moves, the patch did not take, and N1 passing would not distinguish that from a real null result. |

N2 is the one that carries weight. N1 shares the harness with the measurement; N2 rides the
real patched run, so it cannot pass by the patch silently failing to install.

### 2b. What each outcome MEANS — decided in advance, per document

- **A score rise is not, by itself, a gain.** If bfs p5 rises while **losing adoption** or
  shedding cells, the rise is a denominator effect — escalated ink leaving the denominator — and
  is read as a **collapse**. This repo has been caught by that exact shape before ([[R155]];
  the `0.9720 → 0.5407` reading in ~~R225~~'s row). The operands `asserted` / `escalated` and
  the `adopted` tuple are read **before** the score, not after it.
- **bfs** (baseline `0.8851`, p5 adopted at 404 cells). PR #237 predicts 15c → 12c, 46 rows kept,
  both [[R238]] and [[R239]] symptoms gone. The compile-scope question is whether p5 **stays
  adopted**, at what cell count, and whether `ROUND_TRIP_FAIL` / `REGION_TILING_FAILED` /
  `KIND_NOT_SUPPORTED` counts ([[R44]]'s three reasons) move.
- **cbh** is the **cost** side: grid scope already measured **ROWS LOST 5**. Whatever it costs is
  recorded as the price of a blanket switch.
- **graincorp-capacity**: 16c → 15c, rows unchanged at grid scope; compile effect unknown, no
  prediction offered.

### 2c. What this loop will NOT do with the result

**Record it, not design against it.** The previous handoff's § 5d is explicit that no remedy is
designed before this runs, and running it does not license designing one in the same breath — a
scoped remedy (blanket vs. per-page vs. per-document) is a CLAUDE.md § 8 classification and a
maintainer's call. If cbh's cost lands where grid scope says it will, **the blanket switch is
refused and that is a finding, not a defeat.**

### 2d. A PREDICTION, registered before the data that tests it existed

**Written with the alignment run at 2 of 7 documents, before bfs — the deciding one — had
compiled.** Committed at that moment on purpose, for the same reason § 2 was: a mechanism offered
after the numbers are in is an explanation, and this repo does not let an explanation wear a
measurement's clothes.

The first two alignment snapshots (cbh, graincorp-capacity) came back **byte-identical** — same
canonical hash, same score, same cells — although PR #237 measured **both** moving at *grid*
scope (cbh 20c 50r → 16c 45r, a loss of 5 rows; graincorp-capacity 16c → 15c). Grid scope and
compile scope disagree, and the mechanism is visible in the **baseline** alone:

```
document                                score     adopted  decor-page  CAN MOVE?
apple-fy2026q3-statements        0.9302325581         [2]  -           no (no decor page)
bfs-population-bilan-2023        0.8850746269         [5]  p5          yes
cbh-stem-2026-08-03              0.9095022624          []  p0          no (decor page, not adopted)
graincorp-capacity-2026-08-04    1.0000000000          []  p0          no (decor page, not adopted)
graincorp-stem-2026-07-31        0.9658886894          []  -           no (no decor page)
ons-index-of-services-2026-02    0.7712418301      [7, 8]  -           no (no decor page)
who-wfa-boys-zscore-0-5          0.9156327543          []  -           no (no decor page)
```

**Adoption is what carries a grid reading into the emitted graph.** A decoration page whose grid
is never adopted cannot change the graph by changing its universe — the grid is derived, loses
the comparison, and is discarded. Crossing the three decoration pages against the `adopted`
tuples leaves **exactly one document that can move at compile scope: bfs.** apple and ons adopt,
but have no decoration page, so their grids already run on the alignment universe.

**If this holds, PR #237's headline cost is an artefact of scope.** *"A blanket refusal is not
available — cbh loses 5 rows"* is a **grid**-scope fact that does not survive to compile scope,
because cbh's emitted reading is band-derived and never consults the grid at all. That would
remove the stated obstacle to the bluntest remedy — but the removal is **not** this loop's to
bank, and § 2c still binds.

**Three ways this is falsified, named before bfs landed:**

1. **bfs comes back byte-identical.** Then control P fails: the patch never installed, and every
   figure in this run is void — including the two identities above, which would be identity by
   inaction rather than by mechanism. This is the reading that must be ruled out first.
2. **Any non-decoration document moves.** N2 fails: an unknown coupling, not the universe switch.
3. **bfs moves but adoption is unchanged in kind** — e.g. p5 stays adopted at 404 cells with a
   different hash. Then adoption is not the whole mechanism and the table above is too simple.

**A flaw in this run, recorded rather than hidden:** the launch pipes the instrument through
`tail -20`, so its `universe=alignment … <lambda>` confirmation line does not flush until exit.
The patch's installation therefore cannot be confirmed until the run completes — which is why
control P, and not a startup log line, is what will settle falsifier 1. It is the same mistake as
the pytest rule about piping into `tail`, committed again in a different shape.

---

## 3. Results — the alignment universe, all seven documents

**All three controls pass.** N1 is settled below in § 3a; the paragraph that stood here while it
was in flight said that if it failed every figure in this section would be void. It did not fail.

### 3a. The controls

**P — PASSES.** bfs changed. The patch demonstrably took, and this is corroborated independently
by the instrument's own startup line, which `tail` withheld until exit:

```
universe=alignment  _boundaries_from_decoration=<function install.<locals>.<lambda> at 0x105ee6660>
```

**N2 — PASSES, 7 of 7 as predicted in § 2d, which was committed before bfs compiled** (`72faef7`):

```
apple-fy2026q3-statements        N2 control adopts=[2]      IDENTICAL  as predicted
bfs-population-bilan-2023        PREDICTED MOVER            CHANGED    as predicted
cbh-stem-2026-08-03              decor, not adopted         IDENTICAL  as predicted
graincorp-capacity-2026-08-04    decor, not adopted         IDENTICAL  as predicted
graincorp-stem-2026-07-31        N2 control adopts=[]       IDENTICAL  as predicted
ons-index-of-services-2026-02    N2 control adopts=[7, 8]   IDENTICAL  as predicted
who-wfa-boys-zscore-0-5          N2 control adopts=[]       IDENTICAL  as predicted
```

The two strongest rows are **apple** and **ons**: both *adopt* (so they exercise the path the
mechanism runs through) while carrying no decoration page, and both are byte-identical. A patch
that perturbed adoption generally would have moved them.

### 3b. The corpus, by the shipped differ

`scripts/corpus_snapshot_diff.py` is a separate code path from the ad-hoc comparison above and
agrees with it exactly:

```
apple-fy2026q3-statements      0.9302325581 -> 0.9302325581  triples   6225 ->   6225  IDENTICAL
bfs-population-bilan-2023      0.8850746269 -> 0.8850746269  triples  14251 ->  15354  CHANGED
    p5: score 0.9127 -> 0.9127   cells   404 ->   496   asserted   910 ->   910   escalated    87 ->    87
cbh-stem-2026-08-03            0.9095022624 -> 0.9095022624  triples  12839 ->  12839  IDENTICAL
graincorp-capacity-2026-08-04  1.0000000000 -> 1.0000000000  triples   5859 ->   5859  IDENTICAL
graincorp-stem-2026-07-31      0.9658886894 -> 0.9658886894  triples  32422 ->  32422  IDENTICAL
ons-index-of-services-2026-02  0.7712418301 -> 0.7712418301  triples  12196 ->  12196  IDENTICAL
who-wfa-boys-zscore-0-5        0.9156327543 -> 0.9156327543  triples  12292 ->  12292  IDENTICAL

1 of 7 documents changed
```

### 3c. THE HEADLINE — the switch is free, and the score cannot see it

**bfs carries 92 more cells and 1103 more triples, at a score identical to ten decimal places.**

| | before | alignment |
| --- | --- | --- |
| document score | 0.8850746269 | **0.8850746269** |
| p5 cells | 404 | **496** (+92) |
| p5 asserted ink / escalated ink | 910 / 87 | **910 / 87** |
| adopted | `[5]` | `[5]` |
| p5 reason census | RT_FAIL 5, TILING 1, KIND 1, RESIDUE 1 | **identical** |
| graph triples | 14251 | **15354** (+1103) |

Only p5 moved; every other bfs page is unchanged. **Nothing was traded for the 92 cells** — no
adoption lost, no escalation gained, no reason count moved, so the § 2b denominator trap
([[R155]]'s score-rise-is-a-collapse) does not apply: this is not a rise at all.

**Why the score is blind, measured rather than read off the formula.** The score is an ink-token
ratio — `document.py:1582`, `score = 1.0 if (a + e) == 0 else a / (a + e)` — and cells appear
nowhere in it. Verified against the snapshots on both sides:

```
before     sum_asserted=  1186 sum_escalated=  154  A/(A+E)=0.8850746269   recorded=0.8850746269  MATCH
alignment  sum_asserted=  1186 sum_escalated=  154  A/(A+E)=0.8850746269   recorded=0.8850746269  MATCH
```

This is [[R238]]'s own mechanism confirmed end to end at compile scope: *the row is admitted
BECAUSE of the outside ink, and the emitter never carries it.* The ink was always in the
numerator; the cells were never emitted. **A defect that adds no escalated ink is invisible to
this score by construction** — which is the most useful thing the gate produced, because four
loops reasoned about this page with the score as their instrument.

### 3d. What the 92 cells are — MEASURED, and the arithmetic guess was right for a better reason

This section first shipped reading *"NOT MEASURED"*, recording 46 × 2 = 92 as arithmetic
agreement only and naming the probe. **The probe was then run, in this same loop**, and the text
above is superseded by it. It is kept in the git history rather than silently replaced, because
the guess and the measurement agreeing is only worth something if the order is visible.

`_place_for_emit` over bfs p5's admitted rows, under both universes:

```
=== decoration (shipped): 15c 46r, 404 placed cells
    col 0     :  18 cells  e.g. ["('7 415 102', 136.", "('7 459 128', 136.", ...]
    col 14    :  19 cells  e.g. ["('44 026', 479.661", "('49 611', 479.659",  ...]
=== alignment (patched): 12c 46r, 496 placed cells
    col 0     :  46 cells  e.g. ["('2005', 72.117262", "('2006', 72.1201, ",  ...]
    col 11    :  46 cells  e.g. ["('0.60', 514.22986", "('0.70', 514.22986",  ...]

placed-cell delta: 404 -> 496  (= 92)
```

**The two new columns are exactly [[R238]]'s two missing ones, and their x-coordinates prove it.**
The decoration rectangle is `124.3 .. 495.3`. Under alignment, col 0 sits at **x ≈ 72**, left of
`124.3` — the row-label column — and col 11 at **x ≈ 514**, right of `495.3` — the
`Variation en %` column. Both are **full at 46 of 46 rows**, where under decoration the
corresponding edge columns held only 18 and 19 cells and contained data values (`'7 415 102'` at
x ≈ 136), not labels.

**The 46 × 2 = 92 correspondence is real, and the reason is sharper than the guess.** 46 + 46 = 92
is the whole delta, which means the interior re-partition from **15 columns to 10** is
**cell-count neutral at 404**: the same interior ink lands in fewer, wider columns without
gaining or losing a single placed cell. The guess in the superseded text treated the match as
possibly coincidental precisely because that neutrality was not established; it now is.

**What is still NOT established:** that the 46 labels are the *right* labels for their rows. The
sample above shows years (`2005`, `2006`) — the time-series rows at the top of the page — not the
canton names [[R238]] names in its symptom (*"nothing says which row is Zurich"*). Those rows are
further down and were not sampled. The narrow claim measured here is **cardinality and side of
the rectangle**, not identity.
