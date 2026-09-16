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

---

## 3. Results

**PENDING** — baseline in flight at the time § 1 and § 2 were written.
