# The accounting currency-marker column — design

**Date:** 2026-08-05 · **Status:** closed 2026-08-05, final-review fix wave 2026-08-06 —
apple 0.0106 at 4dp (pre-loop 0.0106, unchanged at 4dp); the deep decimal MOVED
(0.0106100796 → 0.0105540897) after the final-review C1 fix made escalation branches
carry previously-silently-dropped marker tokens into `escalated_total` (the p2
MATRIX_AMBIGUOUS band's 2 absorbed `$` markers, formerly uncounted) — an honest, more
conservative score, not a capability change; p0 0 new bands asserted, band 4.0 (the
measured floor) is still MISSED — it never reaches absorption at all, because every
page-0 content band is author-RULED and §4's ruled path is explicitly untouched by
design ("a ruled `$` column is the author's drawn column and stays"); band 4.0 is
independently blocked by R55 (`(171)`-style accounting negatives typing `tab:Text`,
§6.2), confirmed as its sole blocker by direct row-homogeneity inspection. The
mechanism fires exactly once on the whole document (p2 band2, borderless, 2 `$` markers
absorbed, ncols reduced) — that band still fails to tile, for the already-registered §6.3
detached-header/caption class. Stem 0.9655 / CBH 0.9047 byte-identical (re-verified
2026-08-06, `tests/test_corpus_stem.py`+`tests/test_cbh_e2e.py` 13 passed); full suite
green pre-wave (934 passed, 1 pre-existing environmental failure, 5 skipped) ·
**Specimen:** `corpus/financial/apple-fy2026q3-statements.pdf` (sha256 `dc0cf747…`, pinned;
battery id `apple-fy2026q3-statements`; compiles since loop R41 at score 0.0106 — unblocked,
unread) · **Follows:** `2026-08-05-r41-invalid-split-refusal-design.md` §4's named reading loop,
re-scoped by measurement (see §1).

**Doc impact:** increment — a new owned `tab:` term family (`tab:CurrencyGlyph`,
`tab:UnitMarkerColumn` recognition, `tab:hasUnitMarker`) and one new query; a wiki
concept note queues for the next release. No existing page contradicted.

## 1. Problem (measured 2026-08-05, not the loop-R41 spec's guess)

The R41 spec §4 guessed the apple reading gap was Currency-vs-Numeric *cell typing*
(`$ 45,781`). Probing the real page-0 geometry refutes that framing: **the `$` is a separate
word in its own grid column** (accounting style — symbol at the column's left edge, value
right-aligned beside it, drawn on the first and total rows only):

```text
Net income | $ | 29,789 | $ | 23,434 | $ | 101,464 | $ | 84,544
Services   |     30,739 |     27,423 |     91,728 |     80,408
```

A bare `$` types `tab:Text` (measured), so each symbol column reads as a 1–2-cell Text
column: `recover_leaf_grid` fabricates columns (ncols **9** where the author drew **5**),
leaf coverage breaks, and every section band fails tiling (`REGION_TILING_FAILED`).

**The discriminating probe (measured):** removing the `$` words collapses every page-0
band's grid to the correct 5 columns, and band 4.0 (`Operating income…Net income`,
31 cells) **tiles and asserts**. The remaining bands stay blocked by two *other*
registered classes — the detached header block + section captions (the CBH
dimension-split shape, loop-Q territory) and R16 split numbers (`2 | 2,067`) — which
are this loop's successors, not its scope.

## 2. The reading

A column whose every non-blank cell is the **same currency symbol** is not a column of
the table — it is a **unit marker on its right neighbor**. Recovering the author's
structure (§0) means reading the symbol as unit evidence carried on the value column,
never as table data and never as silently-dropped ink.

## 3. The decision, classified (§8 gate)

**AXIOM.** "Is grid column *c* a unit-marker column for column *c+1*?" is an open-world
derivation over the existing typed-cell evidence graph (`celltype.grid_evidence`), in a
new query `vocab/queries/unit-marker-column.rq`:

- every non-blank cell of *c* carries `tab:cellDatatype tab:CurrencyGlyph` — a new open-
  lattice datatype for a cell that is exactly one currency symbol, recognized by **B2b's
  already-shipped symbol set `[$€£¥]`** (`celltype._CURRENCY`'s symbol class, reused —
  no new constant), and all of *c*'s non-blank cells are the **same** symbol;
- column *c+1* carries, **ON THE SAME ROW as at least one marker glyph**, a non-blank
  cell typed `tab:Numeric` or `tab:Currency` — the "$ beside its value" shape (final-
  review fix, I1: an *any-row* neighbor form would let a numeric YEAR HEADER over an
  all-text body license absorption; tightened to same-row 2026-08-05).

Presence-based: no distance, no count, no tolerance. The typing addition
(`is_currency_glyph` → `tab:CurrencyGlyph`) is PROCEDURAL raw typing exactly like B2b's
`is_currency`; the word filtering + grid re-derivation is PROCEDURAL engine glue; the
decision lives in the query.

## 4. Mechanics — two-pass, the loop-G candidates pattern

Pass 1 recovers the grid as today and builds the typed-cell evidence. The AXIOM derives
the marker columns. For each derived marker: the marker **words** are removed from the
band, the grid re-derived on the remainder, and compilation proceeds unchanged. Applied
on the borderless path in `compile_tables` before kind classification (the marker column
distorts `classify`'s evidence too); the ruled path is untouched (rules define columns —
a ruled `$` column is the author's drawn column and stays).

**Carried, not discarded (§5/§6):** each absorbed marker emits
`<column> tab:hasUnitMarker "$"` on the surviving neighbor column plus provenance to the
marker glyphs' source regions (bbox), so a contract can ground the column's unit later
and no ink is dropped. A membrane shape (`tab:UnitMarkerShape`: a `hasUnitMarker` fact
requires its provenance) ships with a conformant example and a negative test, per the
house rule. On a band that ESCALATES (or is NON_TABLE-ignored) for reasons unrelated to
its markers, the marker facts attach to the escalation region's candidate node instead
of a column — no column claim was ever asserted for that band — so the carry holds on
every verdict path, not only the seven asserted branches (final-review fix, C1).

## 5. Guards (no overfitting)

- A column with **any** non-symbol non-blank cell never absorbs — `*` footnote columns
  and mixed-symbol (`$`/`€`) columns stay ordinary columns (negative fixtures pin both).
- A symbol column with **no numeric right neighbor** never absorbs.
- The recognition is per-holon (per band evidence graph) — no cross-band closure.
- Byte-identity everywhere no marker column exists: stem, CBH, and the whole fixture
  suite are the proof (this path runs on every borderless band).

## 6. Out of scope, named (register candidates if measured blocking)

1. **The one-word form** `$ 45,781` (types `tab:Currency`) mixed with bare Numerics in
   one column — the homogeneity-compatibility question. Untouched: B2b's types stay
   exact.
2. **Accounting negatives** `(171)` type `tab:Text` today (measured) — a B2b-style
   capability extension with its own recall/precision batteries.
3. **The detached header block + section captions** (apple's dominant remaining blocker;
   loop-Q generalization to the borderless path) and **R16 split numbers** — the
   successor loops.
4. **Trailing-marker locales** (a symbol column drawn to the *right* of its value
   column, e.g. `123 | €`): the AXIOM binds the marker to its right neighbor only,
   matching the measured US accounting form; a document with the mirrored form extends
   the query when one is measured, not before.

## 7. Success criteria

- Red test first: an apple-shaped synthetic fixture (symbol columns on first/total rows
  only) fails tiling on main, asserts with the correct grid after.
- Apple p0 measured: ncols 9 → 5 on the section bands; ≥ 1 band flips to asserted
  (band 4.0, 31 cells, is the measured floor); document score strictly > 0.0106, the
  delta recorded, never tuned toward.
- `tab:hasUnitMarker` facts present with provenance; SHACL conforms; negative fixtures
  (footnote `*` column, mixed symbols, no numeric neighbor) refuse.
- Stem 0.9655 / CBH 0.9047 byte-identical; full suite green (modulo the known
  environmental release-gate failure on this machine).

## 8. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate: recognition is the AXIOM; typing and word filtering are justified
  PROCEDURAL (raw typing / engine glue); any tuned constant is a defect.
- §7 credibility: bands still blocked by §6's classes keep escalating honestly.
- Source ownership: all new terms in the owned `tab:` namespace.
