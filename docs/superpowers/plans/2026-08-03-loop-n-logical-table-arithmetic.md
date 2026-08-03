# Loop N — Logical-Table Arithmetic (Close R35) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lift subtotal confirmation's closure boundary from the page to the logical table (R35's named closure): page 2's subtotal rows confirm against members on page 1, every record on every page carries its group keys, and the chain's record identity collapses to one kind — measured on the real stem, closing R35.

**Architecture:** A document-level reconciliation pass in `compile_document` (post-stitch, pre-validation): for each chain, build the **logical row sequence** (member tables' body rows in chain order) and re-run the *unchanged* loop-H arithmetic (`detect_aggregation_rows` — PROCEDURAL, decidable exact Decimal; only the holon grows) over it; reconcile the merged graph's aggregation typing to the document-level result (retracting page-local typings the larger window no longer confirms — the pipeline refining its own intermediate before validation, stated honestly); re-derive row groups (loop I's AXIOM queries) over the document-level aggregations, attached to the **head** table with `coversRow` edges that may cross member tables; the feed's chain-walk then injects keys chain-wide. The SHACL row shapes' derived-only exemption (loop I) extends to chain-spanning derived groups — the principle, stated in the shapes' comments: **the logical table is the closure holon**.

**Tech Stack:** existing modules (`rows.py` unchanged, `rowgroups.py`, `document.py`, `feed.py`, `tab-shapes.ttl`). No new dependencies, no new query files expected (loop I's `.rq`s are reused over the document-level agg; if a chain-aware variant proves necessary, it must stay numeric-literal-free).

**Doc impact:** increment — wiki `table-holon-compilation` gains the loop-N outcome; no published page contradicted.

## Measured intake (Loops M reviews; reproduce, don't re-derive)

- Per-page aggregation state on the stem: p0 19 candidates / 18-ish confirmed (loop-H era: 17), p1 22/20, **p2 22 candidates / 0 confirmed** — p2's first candidate `Portland Total` = 70,000 vs on-page member sum 21,000 (12,250 + 8,750); its true members sit on page 1. The 22 unconfirmed rows currently mint **data records**.
- Group-key coverage per page (154 records): p0 {GC Fin Year 38, Month 38, Port 38}/38 · p1 {**1**, 49, 51}/51 · p2 {3, 12, 57}/65. Three kinds of record identity (p0 3-level paths, p1 2-level, p2 opaque); 79 of 154 ids carry a disambiguation suffix.
- Whole-document baseline (manifest-adjudicated): score 0.9655 / 2152 cells / one chain of 3; grounding 154 records / 567 grounded / 1194 quarantined; `cor:scoreFloor 0.95`. Suite baseline: **778 passed / 5 skipped / 0 failed**.
- Detection runs per-region at `src/iladub/etkl/holon.py:445-457` (typing LeafRow/AggregationRow/DetectedAggregationRow + `tab:aggregates` edges); groups derive at `src/iladub/etkl/rowgroups.py:35` from the agg dict; the feed injects keys per member table from `tab:coversRow` (`src/iladub/feed.py:141-175` — R34's third face: every key from THIS table's own groups; the document-level pass changes *whose* groups those are, deliberately).
- `tab:RepeatedHeader` rows never become EntryCells or LeafRows (verify at implementation before building the logical sequence).

## Global Constraints

- **§8 gate:** the arithmetic stays the loop-H PROCEDURAL justification verbatim (decidable exact Decimal; a SPARQL running-sum would be obfuscation) — the ONLY change is the input holon (page → logical table); state this in the pass's docstring. Group derivation stays loop I's AXIOM queries. Zero new numeric constants; label TEXT never read.
- **Reconciliation honesty:** retracting a page-local `DetectedAggregationRow` typing that the document window no longer confirms is the pipeline refining an intermediate BEFORE validation — it must happen before `_validate`/shape checks, be logged in the DocumentReport (counts: page-confirmed, document-confirmed, retracted, newly-confirmed), and never touch non-chained tables (byte-identical behavior for single-page documents and case-1 pages — assert it).
- **R33 inheritance (fourth face):** the document pass runs on chains, so a case-3 false stitch would feed INDEPENDENT tables' rows into one arithmetic window — a subtotal could confirm across unrelated tables only by coincidental sums (R4-(d)'s inherent direction). Register this as an R33 clause (or R35's successor note) in Task 5 — measured on the pinned case-3 fixture (its tables have no aggregation candidates; state what IS measured, don't speculate).
- **Honest failure:** if a measured result contradicts an expectation below (records count, key coverage, score movement, p1 confirmations changing), STOP that task and report — bars move only with the controller/François.
- **Specimen:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` (gitignored; sha 3bda6833…; controller can restore). Never committed.
- **Environment:** `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest` — FOREGROUND only; the stem document fixture is module-scoped in `tests/test_corpus_stem.py` (~3 min).
- **Manifest:** `cor:CompilesAbove @ 0.95` must keep holding; the recorded tallies (154/567/1194) are HISTORY in adjudication rationales — do not edit them; Task 5 records the NEW tallies alongside.

---

### Task 1: Red tests — synthetic cut-group fixture + whole-document assertions

**Files:**
- Modify: `tests/etkl/fixtures.py` (a two-page continuation fixture with a cut group)
- Create: `tests/etkl/test_logical_arithmetic.py`
- Modify: `tests/test_corpus_stem.py` (append the R35-closure assertions)

**Interfaces:**
- Produces: `cut_group_two_page_pdf(path) -> dict` — a ruled, stem-shaped two-page document (page 0: header block WITH a header-block rule + a group of data rows; page 1: repeated header block + the group's REMAINING rows + a subtotal row whose measure equals the FULL group's sum — confirmable only at document level) built per the module's reportlab idiom; both pages standalone-compile; recognition must stitch them (same leaf texts + author x's).
- The red assertions later tasks implement against:

```python
# tests/etkl/test_logical_arithmetic.py
"""Loop N — R35: subtotal confirmation over the LOGICAL table. Red until the
document-level pass lands."""
from rdflib import RDF
from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import cut_group_two_page_pdf


def test_cut_group_subtotal_confirms_at_document_level(tmp_path):
    pdf = str(tmp_path / "cut.pdf")
    cut_group_two_page_pdf(pdf)
    rep = compile_document(pdf)
    assert len(rep.chains) == 1 and len(rep.chains[0]) == 2
    aggs = list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
    # the page-1 subtotal is confirmed (page-locally it cannot be)
    p1_aggs = [a for a in aggs if "/p1" in str(a)]
    assert p1_aggs, "cut-group subtotal must confirm against page-0 members"
    # and its aggregates edges CROSS the member tables
    for a in p1_aggs:
        members = list(rep.graph.objects(a, TAB.aggregates))
        assert any("/p0" in str(m) for m in members), members


def test_single_page_and_case1_untouched(tmp_path):
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf, two_page_unrelated_pdf
    p1 = str(tmp_path / "single.pdf"); simple_table_pdf(p1)
    single, doc = compile_tables(p1), compile_document(p1)
    assert doc.score == single.score
    # the reconciliation pass must not touch a single-page document's typing
    # (URIs are page-scoped in the driver, so compare counts, not subjects):
    assert len(list(doc.graph.subjects(RDF.type, TAB.DetectedAggregationRow))) == \
           len(list(single.graph.subjects(RDF.type, TAB.DetectedAggregationRow)))
    p2 = str(tmp_path / "unrel.pdf"); two_page_unrelated_pdf(p2)
    rep = compile_document(p2)
    assert rep.recognized == ()   # the document pass never runs across unrecognized pages
```

Append to `tests/test_corpus_stem.py` (uses the existing module-scoped `stem_document` fixture):

```python
@needs_stem
def test_stem_r35_closed(stem_document):
    """R35's closure, measured: p2 subtotals confirm, keys reach every page,
    identity is one kind. Red until loop N lands."""
    from rdflib import RDF
    from iladub.etkl.holon import TAB
    g = stem_document.graph
    p2_aggs = [a for a in g.subjects(RDF.type, TAB.DetectedAggregationRow)
               if "/p2" in str(a)]
    assert len(p2_aggs) >= 20, f"p2 confirmed aggregations: {len(p2_aggs)} (was 0)"
    # cross-page operands exist (the cut Portland group)
    assert any(any("/p1" in str(m) for m in g.objects(a, TAB.aggregates))
               for a in p2_aggs)


@needs_stem
def test_stem_keys_reach_every_page(stem_document):
    """Every record carries the outer fiscal-year key (was: p1 1/51, p2 3/65)."""
    from iladub.feed import table_records
    recs = table_records(stem_document.graph)
    missing = [r for r, concepts in recs
               if not any(c.text == "GC Fin Year" for c in concepts)]
    print(f"\nrecords={len(recs)} missing-year-key={len(missing)}")
    assert not missing, f"{len(missing)} records lack the outer key"
    # subtotal rows no longer mint records: count drops below 154
    assert len(recs) < 154
```

**Adapt plumbing to reality** (loop-L precedent): `table_records`' return shape, the concept attribute names, and the fixture-name conventions must be verified against the code before running — assertions' meaning is fixed, calls adapt.

- [ ] Steps: build fixture (validate both pages standalone + recognition stitches, IN the fixture-validation step) → write both test files → run: new tests RED for implementation-absence reasons (p1_aggs empty; missing-year-key > 0), everything else green → commit `test(etkl): red logical-table arithmetic tests — cut-group fixture + stem R35 assertions (loop N)`.

---

### Task 2: The document-level arithmetic pass + typing reconciliation

**Files:**
- Modify: `src/iladub/etkl/document.py` (the pass; runs per chain, post-stitch, pre-merge-validation)
- Modify: `src/iladub/etkl/rows.py` ONLY if the logical-sequence input needs an adapter (the detection function itself must stay unchanged — if its signature can't take the concatenated rows+grid, build the adapter in `document.py`)
- Test: Task 1's `test_cut_group_subtotal_confirms_at_document_level` turns green

**Interfaces:**
- Produces: `DocumentReport.arithmetic` (or equivalent, named in the report): counts `{page_confirmed, document_confirmed, retracted, newly_confirmed}` per chain; the merged graph's aggregation typing reconciled — `tab:AggregationRow`/`tab:DetectedAggregationRow`/`tab:aggregates`/`tab:aggregationFunction` retracted for rows the document window does not confirm, asserted (with possibly cross-table `aggregates` edges) for rows it does. Non-chained tables untouched by construction (the pass iterates chains only).
- **The logical sequence:** members in chain order; each member's body rows in row order; repeated-header rows excluded (verify they are not LeafRows first — if they are, exclude by type and record the fact). The grid for `column_of`: each row's OWN table's grid (label/measure columns are per-table geometry; the arithmetic walks the sequence, the column mapping stays local — think through and document the cross-member label-column comparison: level = label COLUMN INDEX, and member tables share the template's columns by recognition (17=17), so column indices are comparable across members — state this licence, it rests on the continuation law's clause (c)).

- [ ] Steps: implement → cut-group test green → stem probe (`test_stem_r35_closed` should go green or report measured counts; if p1's page-confirmed rows CHANGE (retractions > 0 on p1), STOP and report the delta before proceeding) → spot-run `tests/etkl/test_document.py`, `tests/test_feed_chain_walk.py` → commit `feat(etkl): document-level subtotal arithmetic — the logical table is the closure holon (loop N, R35 first half)`.

---

### Task 3: Document-level row groups + chain-wide key injection

**Files:**
- Modify: `src/iladub/etkl/document.py` (derive groups over the document-level agg, attached to the HEAD table)
- Modify: `src/iladub/etkl/rowgroups.py` only if the derivation needs the head-table attachment parameterized
- Modify: `src/iladub/feed.py` (chain-walk reads the head's document-level groups for ALL members' key injection; per-member group reading for non-chained tables unchanged — R34's third face note updated honestly: chain keys now come from the LOGICAL table's own derivation, which is still "this logical table's own groups")
- Test: `test_stem_keys_reach_every_page` green; identity uniformity

- [ ] Steps: implement → stem: every record carries GC Fin Year/Month/Port per its position; records < 154 (p2 subtotals excluded — print the new count); identity one kind (add the assertion: all record ids share the 3-level-path shape or print the distribution and assert no opaque ids remain) → grounding tally probe (grounded should EXCEED 567 — keys ground via schemes; print, don't hard-pin) → spot-run feed + corpus batteries → commit `feat(feed): chain-wide group keys from the logical table's own derivation (loop N, R35 second half)`.

---

### Task 4: SHACL reconciliation + full verification

**Files:**
- Modify: `vocab/shapes/tab-shapes.ttl` ONLY as needed: the row-tiling shapes' derived-only exemption (loop I) must tolerate head-attached groups whose `coversRow` crosses member tables; `tab:DetectedAggregationRowShape` with cross-table `aggregates` — verify each shape against the stitched stem graph and the cut-group fixture; any change carries the principle in its comment: *the logical table is the closure holon (spec §2b/§8)*.
- Test: full validation green on both fixtures + the stem; FULL suite.

- [ ] Steps: run pySHACL over the stem document graph (compile_document already validates per page — confirm where whole-graph validation happens post-loop-M and extend to cover the document-level facts if it doesn't) → fix shapes minimally → FULL suite foreground (baseline 778/5/0 + this loop's new tests; zero failures) → commit `fix(shapes): row-shape exemptions span chain members — the logical table is the closure holon (loop N)`.

---

### Task 5: Loop close — R35, register hygiene, wiki, tallies to François

**Files:**
- Modify: `docs/superpowers/residues.md` — R35 struck-through-and-kept (register practice) with the closure measurement (new counts: p2 confirmations, key coverage per page, new record/grounded/quarantined tallies, identity uniformity); the R33 fourth-face clause (document pass inherits the false-stitch exposure — with what was actually measured on the pinned fixture); check R34/R36 texts still accurate post-changes.
- Modify: `docs/wiki/concepts/table-holon-compilation.md` — loop-N increment; `updated:` bump.
- Modify: `tests/corpus-manifest.ttl` — a new adjudication note ONLY if François wants one (controller presents the new tallies; the verdict `CompilesAbove@0.95` itself should be re-verified against the new measured score and left unchanged unless it fails).

- [ ] Steps: measure final stem numbers (score, cells, records, grounded, quarantined, per-page keys) → **controller presents them to François** (checkpoint — especially if the score moved or the floor is newly tight) → register/wiki edits → doc lint + corpus battery green → commit `docs(loop-N): close — R35 closed with measurements; register hygiene; wiki increment`.

---

## Completion checklist (Loop N definition of done)

- [ ] `test_cut_group_subtotal_confirms_at_document_level` green (synthetic, specimen-independent).
- [ ] `test_stem_r35_closed` + `test_stem_keys_reach_every_page` green: p2 aggregations ≥ 20 with cross-page operands; zero records missing the outer key; records < 154; identity one kind.
- [ ] Grounding tally recorded (expected: grounded > 567); manifest floor 0.95 still holds on the re-measured score.
- [ ] Single-page + case-1 byte-identical (asserted); full suite zero regressions vs 778/5.
- [ ] R35 closed in the register with measurements; R33 fourth face registered; wiki updated; doc lint green.
- [ ] François shown the new tallies at close; nothing GrainCorp-authored committed.
