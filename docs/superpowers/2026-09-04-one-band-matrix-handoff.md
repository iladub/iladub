# Handoff — the one-band prediction is CONFIRMED, and R165's own licence is REFUTED by the corpus

**Topic:** the R165 handoff's part 5 (PROPOSED) — *apple p0 compiles as one matrix if bands 2–7 are
handed to the matrix reader as one band*. **RUN and CONFIRMED** on p0 and p1. Then the licence R165
proposed for producing that band — one `tab:ruleXsSignature` per band — was itself run on the
corpus, and **it is refuted**.

**Part 5 was written first**, before parts 1–4, per `CLAUDE.md` § "The handoff's next action is
TYPED", and is graded per action.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

Read `docs/superpowers/2026-09-04-one-band-matrix-spike.md` § 2–3 (the confirmation) and **§ 7 (the
refutation)** for the readings, not this file. Re-run either instrument if the compile has changed:

```
PYTHONPATH=. .venv/bin/python scripts/one_band_matrix_spike.py \
    corpus/financial/apple-fy2026q3-statements.pdf 0 2 7
```

The maintainer's ruling, 2026-09-04, recorded nowhere but here: **build first, re-measure `R160`
after** — do not rule the reader-authority question against the 0.3587-vs-0.1895 numbers, because
the one-band reading is about to invalidate them. `R160` closes as dissolved or is ruled against
the new numbers.

### PROPOSED — the spec's shape, which rests on § 7 and on nothing that has been built

The evidence supports a three-part design. **Each part is a proposition; none has been implemented
or run.**

1. **The merge is a PROPOSAL, never an unconditional band split.** § 7.3 is the falsifying case:
   bfs p6's signature run 3..10 spans six `asserted` bands, 216 cells, and its merged band is not
   even a matrix candidate. Attempt the merged reading; keep it only when `classify_matrix` **and**
   `region_tiles` both accept; otherwise fall back to today's bands. CLAUDE.md §3 applied to a band
   split — the tiling membrane is already the disposer, so no new oracle is needed.
2. **The band-forming relation is not signature EQUALITY.** § 7.1: apple p1's bands 4 and 6 differ
   from their neighbours by one extra and two missing x positions, and set equality stops the run
   at 2..3 (26 entries) where 2..7 was measured at 56. Subsumption would join them — but that is a
   *loosening*, and CLAUDE.md §8 forbids reaching for it without stating what disposes it.
   **MEASURE before designing: is band 6's x-set a strict subset of band 5's on p1, and does a
   subsumption relation produce exactly 2..7 there and change nothing on bfs/ons/who/graincorp?**
   The census script is scratch; re-derive it, do not trust this sentence.
3. **An unruled header band must be able to join a ruled run beneath it.** § 7.2: apple p2's
   `Nine Months Ended` band carries no rules, signature `None`, so no signature relation of any
   strength reaches it. This is a *separate* rule from 2, and p2 additionally needs `R167` and
   `R162`, so **p2 is out of scope for the first loop** — say so in the spec's "what is NOT done".

**Why proposed, not asserted:** every one of the three rests on a census this session ran once, on
a merge performed *after* `page_bands` returned. Nothing here shows `page_bands` can be
restructured to produce a candidate merged band and fall back cleanly, nor what that costs the
band-index contract (`compile.py:270-297`) that `section_repair_bands`, the per-band decision log
and every `#mtableN` / `#tableN` URI depend on. **The band-index question is the one that could
sink the design, and it has not been looked at at all.**

### ASSERTED — a small, separable piece, safe to do first or never

`R167` (the em-dash) is a one-line change to `celltype.is_blank` with a corpus regression run. It
unblocks nothing on p0/p1 and does not close p2 on its own (`R162` still refuses). Do it only if a
loop wants a warm-up; it is not on the critical path.

---

## 1. Goal

Run the prediction the predecessor graded PROPOSED before anything was designed on it; then run the
licence that prediction's remedy names, before anything was designed on *that*. Record both.

## 2. Where the primaries are

| where | what to establish there |
| --- | --- |
| `docs/superpowers/2026-09-04-one-band-matrix-spike.md` | § 2–3 the confirmation with its column trees and leaf rows; § 4 p2's two blockers; § 5–6 what is and is not settled; **§ 7 the corpus census and the licence's refutation** |
| `scripts/one_band_matrix_spike.py` | the instrument: `merge_bands` + the `is_matrix_candidate` → `classify_matrix` → `assert_matrix_region` → `region_tiles` chain, mirroring `compile.py:819-835` |
| `tests/test_one_band_matrix_spike.py` | `merge_bands` pinned; `R167` pinned beside its ASCII-hyphen falsifier; `R162`'s three-word spanner pinned beside its one-word falsifier |
| `docs/superpowers/residues-open.md` (`R165`, `R167`) · `residues.md` | R165's last cell carries both the confirmation and the census refutation; R167 is the new row |
| `src/iladub/etkl/compile.py:270-297` (`page_bands`) | the band-index contract the design must not break — read the docstring in full before touching the split |
| `src/iladub/etkl/sectiongraph.py:178-207` | `_rule_xs_signature` — DISTINCT rounded rule x positions, space-joined; the relation § 7.1 says is too strict |
| `src/iladub/etkl/matrix.py:174-209` (`classify_matrix`) | the five-stage chain; `matrix_body_start` and `stub_data_split` are where `R167` bites |
| `src/iladub/etkl/celltype.py:67-88` | `is_blank` / `_cell_datatype` — `R167`'s one line |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The one-band prediction is CONFIRMED on apple p0 and p1 | evidence doc § 2–3; `R165` row; commit `11668f3` |
| `R166`'s p0 half is disposed of by the one-band reading | evidence doc § 2, § 5; `R165` row |
| p2 refuses for two reasons, neither the merge | evidence doc § 4; `R167` row (new); `R162` unchanged |
| `R167` raised: the em-dash types as `tab:Text` | `residues-open.md` `R167`; `residues.md` index |
| **R165's own `tab:ruleXsSignature` licence is REFUTED by the corpus** | evidence doc § 7; `R165` row last cell |
| **Maintainer ruling: build first, re-measure `R160` after** | **this file § 5 only** — nowhere else; reversible |
| The three-part design shape in § 5 | **this file § 5 only**, graded PROPOSED; nothing built |

## 4. Unverified or assumed

- **The three-part design in § 5 is a proposition. None of it is implemented or run.**
- **The band-index renumbering was not examined at all** — the single largest unknown.
- The subsumption relation in § 5 part 2 was **not run**. That apple p1 band 6's x-set is a strict
  subset of band 5's is read off the printed signatures in evidence doc § 7.1, not computed.
- Five signature runs (bfs p3/p5, ons p0/p1/p5/p8) were censused but **never merged or read**. They
  assert 0 cells today, so the downside is bounded, not measured.
- **No document score was measured on any page under any of this.** The entry counts are
  `assert_matrix_region`'s return on a scratch graph, not a compile.
- Whether the merged reading would survive the *full* compile (band captions, unit markers, token
  accounting, `_emit_band_captions` / `_emit_unit_markers` on a 41-line band) was not tested.
- The census script is scratch and is **not committed**; its output is pasted in evidence doc § 7.
  Re-derive it rather than trusting the table.
- Suite: `test_one_band_matrix_spike` (6), `test_residue_register_integrity` +
  `test_doc_governance` + `test_source_ownership` (13), `test_source_citations` (8). The full suite
  was **not** run; no `src/` file changed.
- The working-token figure is the model's estimate — `plimslop preflight` reported
  `unmeasured — no turn recorded for this project` on both calls this session, so the gate logged
  0 and never bound. Treat this handoff as authored without a measured budget.
