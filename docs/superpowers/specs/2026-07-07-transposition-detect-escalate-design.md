# Loop 3 · detect & escalate transposed tables — close the silent-wrong hole

**Status:** design (approved 2026-07-07)
**Loop:** [Loop 1 — the table-holon compiler](../../loops/2026-07-05-table-holon-loop.md) (next increment)
**Builds on:** Loop 1 (record path: `regions`, `holon`, `compile`) + Loop 2 (`headers.is_numeric`)

## Why this exists — a live silent-wrong, not a missing feature

A **transposed** table lays fields *down* the first column and each *other column* is a record:

```
Name   Alice   Bob
Age    30      25
City   NYC     LA
```

Compiled on `main` today, this yields a `tab:RecordTable`, **score 1.00, zero escalations**, with the
inferred header labels `['Alice', 'Bob', 'Name']` — the record identifiers "Alice"/"Bob" asserted as
*column headers*, the field names "Age"/"City" demoted to *row data*. The semantics are **inverted and
asserted with full confidence**.

Neither verifier catches it: the **2-D round-trip** checks *geometric* faithfulness and the `tab:` **SHACL**
checks *structural* tiling/access — and a transposed table is a perfectly valid grid on both. Transposition
is a **semantic orientation** property, and we have no oracle for it. This is a genuine hole in the
"no silent-wrong" guarantee, so per the doctrine it is fixed **before** any additive kind (the *compile*
loop comes after).

## §1 — Scope & closing target

The narrowest fix that closes the hole: **detect typed transposition and escalate it in-band** as an
`iladub:CandidateConcept`, instead of silently asserting an inverted `RecordTable`.

- **Closing proof:** a transposed-numeric fixture that today compiles to `RecordTable` (score 1.0) now
  **escalates** with `reason="TRANSPOSED"`; every normal table still compiles unchanged.
- **In scope:** the orientation oracle + the escalation gate + a `tab:TransposedTable` anchor class.
- **Out of scope:** *compiling* transposed tables (the next loop — transpose, then reuse the record /
  hierarchy maker); all-text transposition (see §7); non-numeric typed signals.

## §2 — The orientation oracle (`orientation.py`)

New module `src/iladub/etkl/orientation.py`:

```
looks_transposed(region) -> bool
```

Operates on the **body** of a `ClassifiedRegion` (data cells, `row > 0` — the header is `row == 0`), using
`headers.is_numeric` as the "typed" signal:

- **typed row** — there exists a body row whose cells in leaf columns `1 .. ncols-1` (excluding the first /
  label column) are **all** `is_numeric`; **and**
- **no typed column** — there is **no** leaf column whose body cells are **all** `is_numeric`.

`looks_transposed` returns **True** iff (typed row exists) **AND** (no typed column exists).

**Why this is safe.** Text-homogeneity is symmetric (both axes carry text labels), so it is ignored; only
the numeric asymmetry triggers a flag. Any normal table with a consistent numeric attribute **column** (the
overwhelming majority of numeric tables — a "Result", "Age", "Amount" column) has a typed column and so
**cannot** be flagged. An all-text table has neither a typed row nor a typed column, so it is **not**
flagged (unchanged behaviour). Only a table whose numeric values run *across* rows — the transposition
signature — trips it.

**The one residual edge, and why it's acceptable.** A normal record table that has *no* type-homogeneous
column **yet** a coincidental all-numeric record row (one record whose every non-label field is numeric,
while no field-column is consistently numeric) would be flagged. This is unusual — but note the failure
mode: it results in an **escalation** (a human-reviewable `CandidateConcept`), not a silently-wrong
assertion. That is a *safe* failure under the doctrine — credibility over completeness — and strictly better
than today's silent inversion. If it proves noisy in practice, the oracle can be tightened later (e.g.
require a majority of rows to be typed-across), but v1 keeps the simple, conservative rule.

Worked examples:
- `record_report` (normal): body col "Result" = `[13.2, 39.5, 7.8, …]` all-numeric → **typed column exists**
  → `looks_transposed = False`.
- transposed: body row `[30, 25]` (cols 1..2, excluding the "Age" label) all-numeric → typed row; no body
  column is all-numeric → `looks_transposed = True`.
- all-text: no typed row, no typed column → `looks_transposed = False`.

## §3 — Gate placement (`compile.py`)

In the existing `RECORD_TABLE` branch of `compile_tables`, **before** `assert_record_region`:

```
if looks_transposed(region):
    escalate_region(graph, cand_uri, _DOC, ascii_view,
                    reason="TRANSPOSED", anchor=TAB.TransposedTable, confidence=0.4)
    # count the region's tokens as escalated; RegionReport(verdict="escalated", reason="TRANSPOSED")
else:
    assert_record_region(...)   # unchanged
```

Scoped to the record path — the only place the demonstrated hole occurs. The hierarchical path is not
touched (a merged-header transposed table is not a case we assert today).

## §4 — Ontology

Add to `vocab/ontology/tab.ttl`:

```turtle
tab:TransposedTable a owl:Class ; rdfs:subClassOf tab:Table ;
    rdfs:label "Transposed table"@en ;
    rdfs:comment "A table whose records run along columns and whose fields run down the first column
      (rows are attributes). Recognized but not yet compiled — used as an escalation anchor."@en .
```

**No new SHACL shape** — a `TransposedTable` is only ever an escalation `suggestedAnchor`, never an asserted
holon in this loop. `tab.ttl` core stays standalone (no external subjects). A `tests/test_tab.py`
term-presence assertion confirms the class exists.

## §5 — What's notable

This is ET(K)L's **first *semantic* oracle** — it closes a hole that neither the geometric round-trip nor
the structural SHACL could catch, because a transposed table satisfies both. Geometry + tiling cannot tell
you *which axis is the record axis*; **type-orientation** can. It sits alongside the round-trip and SHACL as
a third, orthogonal check on the record path.

## §6 — Score & escalation

A transposed region escalates whole → `iladub:CandidateConcept` (surfaceText = the region's spatial-ASCII,
`suggestedAnchor` = `tab:TransposedTable`, `dec:rationale` = `TRANSPOSED`, `prov:wasDerivedFrom`). Its tokens
count as escalated in the score, exactly like any other escalated region; nothing is asserted.

## §7 — Proof of closure (tests)

1. **`test_transposed_escalates`** — a transposed-numeric fixture (fields down the first column, numeric
   record columns) → `compile_tables` emits an `iladub:CandidateConcept` with `reason="TRANSPOSED"`, **no**
   `tab:RecordTable` in the graph. The silent-wrong is closed.
2. **`test_normal_tables_still_compile`** (the critical regression guard) — `record_report` and
   `simple_table` still compile to `RecordTable` with their existing scores; `looks_transposed` returns
   `False` for both. No false positive.
3. **`test_looks_transposed_oracle`** (unit) — a synthetic region with a typed row and no typed column →
   True; a region with a typed column → False; an all-text region → False.
4. **`test_tab_transposedtable_term`** — `tab:TransposedTable` is declared `rdfs:subClassOf tab:Table`.
5. **No regression** — the full etkl + tab suite stays green (the record/hierarchy paths are unchanged
   except for the added pre-assert gate).

## §8 — Out of scope (on the canvas, honest)

- **Compiling** transposed tables — the *next* loop: once detected, transpose the cell grid and run it
  through the existing record / hierarchy maker on the flipped axis, emitting a correct holon.
- **All-text transposition** — with no type signal on either axis, both orientations are equally valid; it
  is genuinely undetectable from geometry, so it is left unflagged (documented, like the all-text
  header/body boundary case). It remains a *possible* silent-wrong for the all-text transposed case, but one
  no deterministic oracle can resolve without external evidence (signal-tagging / a contract).
- **Non-numeric typed signals** (dates, currencies, codes) — `is_numeric` only for v1; `looks_transposed`
  can later take a richer `is_typed` without changing its shape.

## Module map

| File | Change |
|------|--------|
| `src/iladub/etkl/orientation.py` (create) | `looks_transposed(region) -> bool` |
| `src/iladub/etkl/compile.py` (modify) | orientation gate in the `RECORD_TABLE` branch (escalate before asserting) |
| `vocab/ontology/tab.ttl` (modify) | add `tab:TransposedTable ⊑ tab:Table` |
| `src/iladub/etkl/__init__.py` (modify) | export `looks_transposed` |
| `tests/etkl/test_orientation.py`, `tests/etkl/test_closing_slice.py`, `tests/test_tab.py` | the §7 proof suite |
