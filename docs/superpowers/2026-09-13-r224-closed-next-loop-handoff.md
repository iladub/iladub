# Handoff — R224 is closed; etkl:04 still waits on a ruling, not on code

**Serves:** prog:criterion:etkl:04 — the mechanical half is done; the blocking half is a decision.

**Date:** 2026-09-13. **Branch this was written on:** `etkl-04-r224-repair`, cut from `2556b83`.

**Doc impact: none.** A handoff ships no term, no behaviour, no released assertion.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is typed
assertion-or-proposition so a reader can tell a mechanical step from a prediction that can fail.

---

## 5. The next concrete action

### 5a. ASSERTED: the loop opens with the maintainer's ruling on R225's fork. It is unchanged, and it is now the ONLY thing between etkl:04 and a reading.

This was 5a of the previous handoff and it is still 5a, because this loop deliberately did not take
it. R225 measured that repairing band construction *costs* the grid reading — the two are coupled
through the fallback's nothing-at-all gate — so the choice is a values question about what a reading
may claim, not something a further measurement settles. Both arms are costed:

- **Arm A — widen the fallback gate.** A page may carry BOTH a band reading and a grid reading, one
  adjudicated against the other; `dec:supersedes` already models that judgement.
- **Arm B — add a resolution test to the re-bucketing, then re-derive the gate.** `xs` must resolve
  more finely than the band's own word structure (`datagrid.py:346`'s ordinal comparison, applied at
  `compile.py:133`). The gate must be re-derived in the same change or ONS silently loses 552 cells
  (measured: 0.9720 → 0.5407).

**The oracle either arm must pass is the corpus pair, already measured on both sides:** ons must not
lose its grid (571 cells) and bfs p5 must not regress from its adopted 404.

**Why asserted:** the options are enumerated, each arm's corpus effect is measured, and nothing about
the decision depends on evidence that does not yet exist.

### 5b. ASSERTED: etkl:04's route step 1 — author ONS's contract triple — is mechanical and can proceed in parallel.

The document still carries no `cor:contract` / `cor:terms` / `cor:shapes`, which is half of why the
2026-08-20 hold names it. [[R211]] did exactly this for graincorp-capacity
(`examples/shipping/capacity-{contract,terms,shapes}.ttl`, wired into `tests/corpus-manifest.ttl`),
so the shape of the work is known and copyable. It does not depend on 5a.

**Why asserted:** the precedent exists, the file layout is fixed, and the outcome of doing it is
known. Note it does NOT by itself meet the criterion — the adjudication must also accept the score.

### 5c. PROPOSED, and it must be RUN before anything is built on it: would ONS's two grids stitch even if recognition could see them?

**The prediction:** ons p7 and p8 are consecutive halves of one series, so if [[R225]]'s ruling gives
their data bands a recoverable leaf grid, the pair will be recognized and `tab:continuesTable` will
form between them.

**Why it may fail, and why this grading is not theoretical.** The *previous* handoff's 5c predicted
that binding the grid URI would restore stitching; it was run this loop and REFUTED in one compile
(see [[R226]]). Recognition additionally requires the continuation AXIOM to accept the evidence and
the R33 licence to permit it, and **nothing has measured whether either would**. The same shape of
claim has already failed once here. Check it before designing anything that assumes a chain.

### 5d. What this hands over exposed

[[R225]] is open and untouched by code — it is 5a. [[R226]] is open and new. [[R202]] keeps its open
half: this loop paired report to band by INDEX, which is not the pair-by-identity helper that row
asks for, and `scripts/unbooked_ink_census.py` / `band_run_census.py` still pair positionally.
[[R213]]'s ruling is recorded but still not implemented. etkl:04's route steps 1 and 2 are untouched.
`scripts/unbooked_ink_census.py` still passes `datagrid_fallback=False`, so the census remains blind
to this branch by construction — repairing the instrument was not in scope and no row tracks it
beyond R224's closed evidence.

---

## 1. Where the primaries are

- **The evidence** — `docs/superpowers/2026-09-13-r224-closed-the-fallback-names-its-table.md`.
  Read § 4 first: it is the refuted prediction and the reason [[R226]] exists.
- **The spec** — `docs/superpowers/specs/2026-09-13-the-fallback-that-names-no-table-design.md`.
  Its § 8 still carries the causal story; § 4's invariants are the ones this loop implemented.
- **The rows** — [[R224]] in `residues-closed.md` (closure evidence), [[R225]] and [[R226]] in
  `residues-open.md`. R225's closure column carries the fork 5a asks a ruling on.
- **The code** — `src/iladub/etkl/compile.py:1351-1367`, ten lines changed, two of them statements.
- **The oracles** — `tests/etkl/test_fallback_region_books_and_names.py` (new, I1/I2),
  `tests/etkl/test_read_band_books_every_word.py` (I3 + the helper), and
  `tests/etkl/fixtures.py::border_only_grid_pdf`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| D1 + D2 repaired; totals preserved, 7/7 corpus scores byte-identical | R224's closed row; evidence § 2 |
| ons `chains` moves [1] → [1,1,1]; `continuesTable` stays 0 | evidence § 2, last paragraph |
| § 5c's URI-restores-stitching prediction is REFUTED | evidence § 4; [[R226]] |
| No synthetic fixture reached the gate — one was authored | R224's closed row; `border_only_grid_pdf`'s docstring |
| O1's helper pairs by band index, not equal lengths | the helper's docstring; [[R202]] stays open |
| The candidate count's stillness at 91 is a cancellation | `tests/test_residue_graph.py` docstring |

## 3. Unverified or assumed

- **5c, entirely** — see its grading.
- **That ONS *should* stitch at all is unverified.** p7/p8 read as consecutive halves of one series
  from their content; no instrument has confirmed the continuation axiom would accept them.
- **[[R226]]'s scope beyond ONS is unmeasured.** `leaf_block` was measured empty on ONS's nine pages
  only. Whether other corpus documents have pages that evidence no leaf block was not checked, and
  the row does not claim it.
- **The corpus I1/I2 sweep is a snapshot.** It passed 7/7 on 2026-09-13; it is marked `corpus` and
  therefore does NOT run in CI, so a future regression on a corpus-only document would be caught by
  the fixture only if it is the fallback shape.
- **R225's arm-A/arm-B costing is inherited, not re-measured** this loop.

## 4. What this loop did

Executed the spec's § 4 and § 5: repaired both defects, authored the missing fixture, added I1/I2 as
a new suite and I3 to the existing one, and falsified all three. Ran the corpus sweep on both sides
of the repair to make "no score moves" a measurement rather than an inference. Ran the previous
handoff's § 5c prediction, refuted it, and raised [[R226]] with the mechanism. Closed [[R224]].

**A method note worth carrying.** The refutation in § 4 was reachable by reading — both stitch sites
index by band index — and reading got the *conclusion* right for the *wrong reason*: the guess was
that R225 had damaged p7/p8's bands specifically, and the measurement showed `leaf_block` empty on
all nine pages including one that asserts 19 cells. A prediction that is right about the outcome and
wrong about the cause is the kind this repo's rule 2 exists to catch, and it costs one compile.
