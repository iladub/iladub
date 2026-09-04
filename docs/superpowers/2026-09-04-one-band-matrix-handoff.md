# Handoff — the one-band prediction is CONFIRMED, and R165's own licence is REFUTED by the corpus

**Topic:** the R165 handoff's part 5 (PROPOSED) — *apple p0 compiles as one matrix if bands 2–7 are
handed to the matrix reader as one band*. **RUN and CONFIRMED** on p0 and p1. Then the licence R165
proposed for producing that band — one `tab:ruleXsSignature` per band — was itself run on the
corpus, and **it is refuted**.

**Part 5 was written first**, before parts 1–4, per `CLAUDE.md` § "The handoff's next action is
TYPED", and is graded per action.

**But it was AMENDED twice, late, and the second amendment is exactly what that rule warns about.**
The maintainer asked for the band-index measurement after this file already existed, so part 5's
design list grew a fourth item — and that item was authored at ~170,000 working tokens, 3.4× the
50K originating floor, which is the condition the rule exists to prevent. Two consequences, stated
rather than hidden: the four design parts are **not** of equal provenance (1–3 were written under
the floor, 4 was not), and part 4 of *this* file is the one to trust over part 5 if they disagree.
Parts 1–4 are pointers and records, which do not degrade; part 5's fourth item is originating
reasoning written at the worst moment for it. **Re-derive it from evidence doc § 8.5 rather than
inheriting it.**

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

> **The next session writes the SPEC.** All three measurements this loop was raised to make are in:
> the one-band prediction (§ 2–3), the licence (§ 7), and the band-index renumbering (§ 8). Nothing
> further needs measuring before a spec can be written, and no code was written this loop.
> **The spec is originating work — start it in a fresh session, under the 50K floor** (CLAUDE.md
> § Loop & context hygiene). This loop authored none of it deliberately; it ended at 2.3× that floor.

### ASSERTED — mechanical, the outcome is known and doing it is the work

Read `docs/superpowers/2026-09-04-one-band-matrix-spike.md` § 2–3 (the confirmation), **§ 7 (the
licence refuted)** and **§ 8 (the band index)** for the readings, not this file. § 8.6 is the list
of what § 8 does *not* settle and is the shortest thing worth reading twice. Re-run either
instrument if the compile has changed:

```
PYTHONPATH=. .venv/bin/python scripts/one_band_matrix_spike.py \
    corpus/financial/apple-fy2026q3-statements.pdf 0 2 7
```

The maintainer's ruling, 2026-09-04, recorded nowhere but here: **build first, re-measure `R160`
after** — do not rule the reader-authority question against the 0.3587-vs-0.1895 numbers, because
the one-band reading was about to invalidate them. **It did** (§ 8.4: document score 0.6289, and
`adopted=()` in both runs). `R160`'s measurement is therefore complete and **its ruling is still
open and is the maintainer's** — a spec may cite § 8.4 but must not rule it in passing.

### PROPOSED — the spec's shape, which rests on § 7–8 and on nothing that has been built

The evidence supports a **four**-part design. **Each part is a proposition; none has been
implemented or run.** Parts 1–3 come from § 7; part 4 is what § 8 added.

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

4. **The design must be correct for a non-tail merge, which this corpus cannot exercise.** § 8.1
   measured zero renumbering only because every run the oracle accepts happens to end at the last
   band on its page. § 8.5 lists what breaks otherwise: the index is persisted into the shipped and
   **grounded** graphs (`ground.py:100`), and three two-pass flows use pass-1 indices against pass-2
   results — adoption (`document.py:1657-1740`) being the one the merge touches directly, where
   `grid_idx = len(pages[p].regions)` goes 8 → 3. **The spec must state what happens to a non-tail
   accepted merge and supply its own fixture**, because no corpus document will fail for it.

**Why proposed, not asserted:** every one of the four rests on a census this session ran once, on
a merge performed *after* `page_bands` returned. Nothing here shows `page_bands` can be
restructured to produce a candidate merged band and fall back cleanly.

**The band-index question — named here first as "the one that could sink the design" — WAS then
measured** (evidence doc § 8). It does not sink it, on this corpus: **zero bands renumber**, because
every run the oracle accepts is a page tail, and the full compile reaches page score 1.0000 on p0
and p1 with the apple document score going **0.1895 → 0.6289**. Read § 8 rather than this paragraph.
What § 8 nevertheless surfaced, and what the spec must answer:

- the index is persisted into the **shipped** graph and onward into the **grounded** graph
  (`ground.py:100` mints `urn:iladub:region:<fragment>` node IRIs from it), so a renumbering is an
  identity change in published output, not an internal detail;
- **three** two-pass flows use pass-1 indices against pass-2 results, and the merge touches one of
  them directly — adoption, where `grid_idx = len(pages[p].regions)` (`document.py:1657`) goes
  8 → 3 on the two merged pages;
- **the corpus contains no non-tail run that the oracle accepts**, so the one dangerous case has no
  evidence at all. A spec that relies on "accepted runs are tails" is relying on a corpus accident.

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
| The band-index renumbering is measured: zero bands renumber on this corpus | evidence doc § 8; `R165` row |
| `R160`'s 0.3587-vs-0.1895 numbers are superseded by 0.6289, and adoption never fires either way | evidence doc § 8.4; `R160` row last cell |
| **`R160` itself is NOT ruled** — the measurement is in, the call is the maintainer's | `R160` row; nowhere else |

## 4. Unverified or assumed

- **The three-part design in § 5 is a proposition. None of it is implemented or run.**
- **The band-index renumbering WAS examined** (evidence doc § 8) — but only for runs this corpus contains. **No non-tail run that the oracle accepts exists anywhere in the corpus**, so the case § 8.5 says would be dangerous is entirely unmeasured.
- The § 8.4 document compiles ran with `validate_shapes=False`: the membrane was not exercised.
- The 20 index-pinning test files were **not** run against a merged compile. Which ones would change (evidence doc § 8.5 (d)) is read off their source, not off a failing run.
- § 8.4 patches `page_bands` from outside with a hard-coded run. It shows the compile survives a merged band; it shows nothing about a licence selecting one.
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
