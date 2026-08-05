# R41 — the invalid header/body split is refused at derivation — design

**Date:** 2026-08-05 · **Status:** approved (François, 2026-08-05) ·
**Discharges:** R41 (the apple crash) · **Specimen:** `corpus/financial/apple-fy2026q3-statements.pdf`
(sha256 `dc0cf747…`, pinned in `tests/corpus-manifest.ttl`; battery id `apple-fy2026q3-statements`)

**Doc impact:** none — a defect fix inside an existing AXIOM; no new vocabulary, no new
concept, no site/wiki page contradicted. (The battery's corpus page already describes the
apple entry as Unadjudicated; this loop makes that gate hold.)

## 1. Problem (measured, not assumed)

The corpus battery's one honest red: compiling
`corpus/financial/apple-fy2026q3-statements.pdf` **crashes** —
`IndexError: tuple index out of range` at `headers.py:400`
(`band.lines[body_line].top`), reached via `classify_hierarchical` →
`infer_header_tree` → `header_rows_of`. A crash violates the fluent-reader invariant
(never crash, always at worst escalate) and blocks the document outright.

**Root cause, measured by probe (2026-08-05) — not the register's trailing-footer guess.**
The failing band is the segment-footnote sub-table (7 lines × 5 columns):

```
line 0: (1) Net sales by reportable segment:
line 1: Americas | $ 45,781 | $ 41,198 | $ 149,403 | $ 134,161
line 2: Europe | 29,395 | 24,014 | 95,596 | 82,329
…
line 6: Total net sales | $ 109,417 | $ 94,036 | $ 364,357 | $ 313,695
```

Every data column's **first and last body rows are `$`-prefixed** (typed off-modal) while
interior rows are bare numbers. In `vocab/queries/header-body-split.rq` (v2), the modal
body type D = Number; the `$` rows are mismatches; `s_col = MAX(mismatch row) + 1 = 6 + 1
= 7 = len(band.lines)` in **every** data column, so `MIN(?s_col) = 7` — a "split" leaving
**zero body rows**, an index one past the band. Every downstream `band.lines[split]`
indexer is then a crash site: `header_rows_of` (headers.py:400) first, and — had only
that one been guarded — `classify_hierarchical`'s own `band.lines[split].top`
(hierarchical.py:44) three lines later, plus `matrix.py`, `rowheaders.py`, `segment.py`,
`document.py`. **The register's literal closure suggestion (a bound check in
`header_rows_of`) therefore cannot stop the crash; the fix belongs where the invalid
split is minted.** The query's own header comment already names this exact
non-robustness ("a lone such column can yield a split past the body instead of
escalating; see Loop B/C") — this loop closes the documented caveat.

## 2. The fix — a validity clause in the AXIOM (decided: AXIOM, not a Python guard)

A derived split is a claim that a label→data transition **exists**: at least one body row
lies at/after it. A column whose `s_col` lies past the last evidence row never completed
that transition — it has no body under its own reading — and is **excluded from the
`MIN`**, exactly as the existing `?s_col = -1` no-non-Blank-body exclusion already
treats columns with nothing to say. Presence-based, no numeric constant, open-world
(derives only where support exists; refusing to derive is not inferring by absence).

Mechanically: bind the global maximum evidence row (`MAX(?crow)` over all cells) and
filter `?s_col <= ?maxrow`. If no column survives → empty result → `run_scalar` returns
`None` → the **existing** `_hrule_split` fallback → the **existing** `None`-escalation
path through `classify_hierarchical` (and every other caller). No new escalation
plumbing; no Python geometry.

Gate classification (§8/CLAUDE.md §0.8): **AXIOM** — a clause added to an existing
open-world SPARQL derivation. No NEURAL, no new PROCEDURAL.

## 3. Changes, in TDD order

1. **Red test first.** A synthetic fixture shaped like the apple band — caption line 0,
   label column, data columns whose first and last rows are `$`-prefixed and interior
   rows bare numeric. On main it reproduces the exact `IndexError`; the test asserts the
   band **escalates** (compile returns, verdict escalated, no crash). Plus a unit-level
   pin: `header_body_split` on that band returns `None` or an in-range split
   (`1 <= split < len(band.lines)`) — never an out-of-range index.
2. **Query edit** in `vocab/queries/header-body-split.rq` (§2), with the caveat comment
   rewritten to state the closure (and keep the honest remainder: an *interior*
   off-type non-Blank footer still shifts the split — only the past-the-end form is
   refused; an in-range-but-wrong split is a reading-quality question, not a crash).
3. **Mirror the fast Python reference** in `tests/etkl/test_derivation_equiv.py` and keep
   the randomized equivalence battery green; check its generator actually emits
   trailing-off-type-in-every-data-column cases and extend it if it does not (the
   committed-differential method — on that case class the OLD query text and the NEW one
   must measurably differ, and the updated reference must equal the NEW query on the
   whole battery).
4. **End-to-end measurement.** `compile_document` on the apple specimen returns; battery
   `test_expected_verdict[financial/apple-fy2026q3-statements.pdf]` flips red → green
   (the `Unadjudicated` gate is exactly "compile returns at all"); the measured score and
   region verdicts are printed as adjudication evidence, asserted by no one. Full suite
   green. **No-regression proof:** the stem pins
   (`test_stem_document_stitches_three_pages`, score 0.9655 / 2152 cells) and the CBH
   E2E pin (0.9047) — this query runs on every document, so byte-identity there is the
   evidence the clause is inert on valid splits.
5. **Register.** R41's row deleted in the same change. If the apple compile, once past
   the crash, reveals a further *measured* defect downstream (a second crash, a hang),
   that becomes its own new row — measured, never assumed.

## 4. Out of scope, named

Making the segment sub-table **read** is not this loop. Typing `$ 45,781` as numeric
(currency-aware cell typing in `celltype`) would both place the split at 1 *and* recover
the table as data — but it touches the typing of every document and is its own reading
loop with its own battery evidence. If step 4's measurement confirms the band escalates
for exactly this reason, the candidate reading loop is registered as a residue row
rather than smuggled in here.

## 5. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate: the fix is a clause in an existing AXIOM; any Python beyond test
  fixtures is a defect.
- §7 credibility over completeness: the sub-table escalates honestly; nothing is read
  that the derivation cannot support.
- No overfitting: the clause is a validity condition (a split must leave a body), not an
  apple-shaped special case; the equivalence battery + stem/CBH byte-identity are the
  generalization evidence.
