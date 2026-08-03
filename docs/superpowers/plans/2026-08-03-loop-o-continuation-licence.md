# Loop O — The Continuation Licence (Close R33) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close R33 — the case-2/case-3 stitch boundary: recognition (leaf-identity) stays, but stitching is now LICENSED by page-invariance evidence, so independent same-template documents stop stitching while the stem stays byte-identical; faces 4–5 are measured for real first, then made moot for marked documents; R37 narrows.

**Architecture:** Task 1 measures faces 4–5 on new subtotal-carrying case-3 fixtures (the final review's explicit first step) and lays the red tests. Task 2 builds the licence: a PROCEDURAL page-block evidence emitter + a new AXIOM (`continuation-licence.rq`) expressing the **asymmetric page-invariance law** — for a recognized pair (N−1, N): (a) every non-table text block on page N other than the repeated header block must be page-invariant across the pair (present with identical text on both pages, e.g. the stem's footer); (b) every text block on page N−1 *below* its table's last body row must be page-invariant; head-page furniture above/before the table on N−1 is unconstrained (the stem's title/timestamp are head-only and legitimate). All presence/equality tests, zero numeric literals. Task 3 wires the gate into `compile_document` (licence between recognition and `continuesTable`/carriage/arithmetic), records refused licences as facts (the in-kind closure R34's row hinted at), inverts the two R33 pins, and proves stem byte-identity. Task 4 closes: R33 struck-kept — closed for marked documents; the bare-identical residual (two indistinguishable tables, no marks) is stated as **invariant-consistent, not a defect** (a fluent reader also reads them as one table); R37 narrowed to licensed continuations.

**Tech Stack:** existing modules (`document.py`, `bands.py`/`geometry.py` reads), one new `.rq`, `tab:` terms for the licence facts. No new dependencies.

**Doc impact:** increment — wiki `table-holon-compilation` gains the loop-O outcome; no published page contradicted.

## Measured intake (loops L–N reviews; reproduce, don't re-derive)

- The stem's page structure: p0 = title band (16–28) + 'SHIPPING STEM' band (52–58) + table (61–457) + footer line at **573.87**; p1/p2 = table (from ~51) + the SAME footer at 573.87. The footer is page-invariant; the title/timestamp are p0-only (head furniture). **This is why the law must be asymmetric** — symmetric invariance would refuse the genuine stitch.
- The pinned case-3 fixture (`tests/etkl/test_document.py::test_template_pages_stitch_the_known_case3_false_positive`): two independent template tables with DIFFERENT per-page banners in a separate NON_TABLE band — currently stitches (`continuesTable` asserted); loop-M's F1 fix means the identity weld is already closed; loop-N proved the chain link alone currently derives nothing on it (no aggregation candidates). Its banners are exactly the non-invariant continuation-page content the licence reads.
- Faces 4–5 (registered, measured only as mechanisms on constructed graphs): face 4 — a wrong window DESTROYS page-confirmed facts (loop-N's constructed retraction case); face 5 — on a false chain WITH subtotals, a conflicting page-2 label silently derives NO group (loss) while a matching label injects page-1's key into unrelated rows (fabrication). **Never measured on an actual false-stitch compile — that is Task 1.**
- Stem baseline (manifest-recorded): score 0.9655 / 2152 cells / chain of 3; 133 records / 585 grounded / 1265 quarantined / missing-year-key 0; ledger 41/62/0/21; suite **787/5/0** non-corpus + **10** corpus.
- R37: the wider-window reading (one logical total cut by pagination) vs a per-page restart is a modelling choice no oracle disposes; the licence's evidence is the natural narrowing.

## Global Constraints

- **§8 gate:** the licence decision lives in SPARQL over emitted evidence facts (block text identity + position relative to the table — presence/equality only, ZERO numeric literals; block comparison is evidence comparison, not text READING — state it in the query header as `continuation-of.rq` does). The emitter is justified PROCEDURAL raw extraction.
- **The fluent-reader invariant cuts BOTH ways** (spec §2): marked documents (differing banners) must refuse; **bare-identical documents must still stitch** — a human reading two identical bare tables on consecutive pages reads one continued table, so stitching there is the CORRECT reading, and the loop's close says so rather than chasing an impossible discrimination.
- **Stem byte-identity is the hard wall:** tallies (score/cells/records/grounded/quarantined/keys/ledger) must not move. Any movement = STOP and report.
- **Honest failure:** measured surprises (faces 4–5 behaving differently than the mechanisms predict; the licence refusing the stem; a fixture that won't compile) STOP the task with the measurement.
- **Specimen:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` (gitignored, sha 3bda6833…). Never committed.
- **Environment:** `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest` — FOREGROUND only; stem compile ~183 s + 42 s validation; corpus module ~5 min. The full suite no longer fits one 10-minute call — run `-m "not corpus"` and `-m corpus` as separate foreground calls.
- **Commits:** conventional style.

---

### Task 1: Face measurement + fixtures + red licence tests

**Files:**
- Modify: `tests/etkl/fixtures.py` (three fixtures)
- Create: `tests/etkl/test_continuation_licence.py`
- Modify: `tests/etkl/test_document.py` (prepare the two pins for inversion — mark with comments, do NOT invert yet; Task 3 inverts)

**Interfaces:**
- Produces: `case3_with_subtotals_pdf(path, conflicting_labels: bool) -> dict` — the pinned case-3 shape (independent template tables, DIFFERENT per-page banners in a non-table band) EXTENDED with per-store subtotal rows; `conflicting_labels=False` gives both pages the SAME group label (the fabrication face's shape), `True` gives different labels (the loss face's shape). Sums must be chosen so each page's subtotal confirms PAGE-LOCALLY (loop-H arithmetic on its own page) — the interesting measurement is what the false chain's DOCUMENT window does to them. Also `bare_identical_two_page_pdf(path)` — the same template on both pages, NO banners, no subtotals, different data (the genuinely indistinguishable case).
- The red tests Task 3 turns green:

```python
# tests/etkl/test_continuation_licence.py
"""Loop O — R33: stitching is licensed by page-invariance, not recognition alone.
Red until the licence lands (Tasks 2-3)."""
from rdflib import RDF
from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import (case3_with_subtotals_pdf,
                                 bare_identical_two_page_pdf,
                                 two_page_unrelated_pdf)


def test_marked_case3_does_not_stitch(tmp_path):
    """Differing per-page banners = non-invariant continuation content -> refuse."""
    for conflicting in (False, True):
        pdf = str(tmp_path / f"c3-{conflicting}.pdf")
        case3_with_subtotals_pdf(pdf, conflicting_labels=conflicting)
        rep = compile_document(pdf)
        assert all(len(c) == 1 for c in rep.chains), rep.chains
        assert not list(rep.graph.subjects(None, TAB.continuesTable)) \
            or not any(True for _ in rep.graph.subject_objects(TAB.continuesTable))
        # page-local subtotals keep their page-local confirmations (no window widening)
        aggs = list(rep.graph.subjects(RDF.type, TAB.DetectedAggregationRow))
        assert aggs, "page-local subtotals must remain confirmed"


def test_bare_identical_still_stitches(tmp_path):
    """No distinguishing marks -> a fluent reader reads ONE table -> stitching is
    the correct reading (the invariant cuts this way; registered as the narrowed
    residual, not a defect)."""
    pdf = str(tmp_path / "bare.pdf")
    bare_identical_two_page_pdf(pdf)
    rep = compile_document(pdf)
    assert any(len(c) == 2 for c in rep.chains), rep.chains


def test_unrelated_pages_still_never_stitch(tmp_path):
    pdf = str(tmp_path / "unrel.pdf")
    two_page_unrelated_pdf(pdf)
    rep = compile_document(pdf)
    assert rep.recognized == ()
```

- [ ] **Step 1: build the fixtures** (per the module's reportlab idiom; validate each inside the fixture-validation step: both pages compile standalone; recognition fires on the case-3 and bare fixtures; page-local subtotals confirm page-locally on the case-3-with-subtotals pages).
- [ ] **Step 2: MEASURE faces 4–5 today** (before any licence exists) on both `case3_with_subtotals_pdf` variants: compile via `compile_document`, record — does the document window retract the page-local confirmations (face 4)? do document-level groups derive across the independent tables, and does the matching-label variant inject page-1's key into page-2's records (face 5 fabrication) or the conflicting variant lose the group (face 5 loss)? Write the ACTUAL measured outcomes into the task report verbatim — they are the loop's opening evidence and go into R33's row at close. If the mechanisms do NOT reproduce on the real compile, that is a finding to report, not to hide.
- [ ] **Step 3: write the red tests**; run: licence tests RED (marked case-3 currently stitches), bare + unrelated GREEN (current behavior); stem corpus module untouched-green (spot-run).
- [ ] **Step 4: commit** `test(etkl): case-3 subtotal fixtures + face-4/5 measurements + red licence tests (loop O)`

---

### Task 2: The page-block evidence + the licence AXIOM

**Files:**
- Create: `vocab/queries/continuation-licence.rq`
- Modify: `src/iladub/etkl/document.py` (evidence emitter + `is_licensed(...)` runner, alongside the Task-2-loop-M recognition machinery)
- Modify: `vocab/ontology/tab.ttl` (licence-evidence terms, following the file's conventions)
- Test: `tests/etkl/test_continuation_licence.py` (append law-level unit probes)

**Interfaces:**
- Consumes: loop-M's `page_bands`/recognition structures (read `document.py` first — the band inventory per page already exists on the recognition path).
- Produces: `licence_evidence(prev_page_blocks, cur_page_blocks, prev_table_span, cur_repeated_header_span) -> Graph` (PROCEDURAL: one fact per non-table text block — its full text, its page, whether it sits below page N−1's last body row / outside page N's repeated-header+table region) and `is_licensed(evidence: Graph) -> bool` running the AXIOM. **The law (asymmetric, state verbatim in the query header):** a recognized pair is licensed iff (a) every non-table block on page N outside the repeated header block has a text-identical counterpart block on page N−1 (page-invariance), AND (b) every block on page N−1 below the table's last body row has a text-identical counterpart on page N. Head-side blocks above/before page N−1's table are unconstrained. `FILTER NOT EXISTS` presence patterns; zero numeric literals; block-text equality is evidence comparison (cite `continuation-of.rq`'s READING-vs-COMPARING block).
- Law-level unit probes (append):

```python
def test_licence_law_probes():
    from iladub.etkl.document import licence_evidence_from_facts, is_licensed
    # (text, page, is_below_prev_table_or_outside_cur_header) — the fact shape;
    # adapt the constructor's exact signature to what you build, meanings fixed:
    invariant_footer = [("Footer note", 0, True), ("Footer note", 1, True)]
    assert is_licensed(licence_evidence_from_facts(invariant_footer))
    differing_banner = [("STORE ALPHA", 0, True), ("STORE BETA", 1, True)]
    assert not is_licensed(licence_evidence_from_facts(differing_banner))
    head_only_title = [("GRAIN REPORT", 0, False)]      # head furniture: unconstrained
    assert is_licensed(licence_evidence_from_facts(head_only_title))
    cur_page_extra = [("A fresh section", 1, True)]      # non-invariant on the continuation
    assert not is_licensed(licence_evidence_from_facts(cur_page_extra))
    empty = []
    assert is_licensed(licence_evidence_from_facts(empty))   # bare documents license
```

- [ ] Steps: probes RED → implement (emitter + `.rq` + terms) → probes GREEN → verify the STEM's evidence licenses (probe: emit for pairs (0,1),(1,2) and run — must be True both; the footer matches, the title is head-side) and the pinned case-3's evidence refuses → commit `feat(etkl): the continuation licence — asymmetric page-invariance AXIOM over block evidence (loop O, R33)`

---

### Task 3: Gate wiring + pin inversions + stem byte-identity

**Files:**
- Modify: `src/iladub/etkl/document.py` (licence between recognition and everything downstream: no `continuesTable`, no carriage, no arithmetic, no groups for an unlicensed pair; `DocumentReport` records refused pairs — e.g. `.refused_licences` — AND asserts the refusal as a graph fact (a `tab:` term with the pair, per R34's in-kind closure hint: a refusal signal recorded, not discarded))
- Modify: `tests/etkl/test_document.py` (INVERT the two R33 pins — `test_template_pages_stitch_the_known_case3_false_positive` becomes the refusal pin, renamed accordingly, per its own inversion instructions; same for the with-subtotals variant if pinned in Task 1)
- Test: Task 1's licence tests turn GREEN; stem byte-identity

- [ ] Steps: wire → licence tests GREEN → pins inverted (their docstrings updated to cite the licence and this loop) → **stem byte-identity**: corpus module full run — score 0.9655 / 2152 / chain of 3 / 133 / 585 / 1265 / missing 0 / ledger 41/62/0/21, ALL unchanged (any drift = STOP) → non-corpus suite (expect 787 + this loop's new tests, 0 failed; foreground, split calls) → commit `feat(etkl): stitching gated by the continuation licence; refusals recorded as facts; R33 pins inverted (loop O)`

---

### Task 4: Loop close — R33, R37, register, wiki, tallies confirmation

**Files:**
- Modify: `docs/superpowers/residues.md` — R33 struck-through-and-kept: closed for marked documents (the licence), faces 1/4/5 resolved-or-mooted with Task 1's REAL measurements quoted, face 2 already closed (loop M), face 3 bounded by the licence; the bare-identical residual stated as invariant-consistent (not a defect; a fluent reader reads one table) — one sentence, no new row needed unless a genuine open edge emerged in Tasks 1–3. R37 NARROWED (not closed): the wider-window modelling choice now applies only within LICENSED continuations; update the row. R34: add the licence-recording face if the refusal-fact landed (its "in-kind closure" clause is now partially real).
- Modify: `docs/wiki/concepts/table-holon-compilation.md` — loop-O increment; `updated:` bump.
- Modify: `tests/corpus-manifest.ttl` — ONLY if François wants a note (controller presents; stem tallies are byte-identical so the default is NO manifest change).

- [ ] Steps: measure final numbers (must equal baseline) → **controller presents the close to François** (R33 closed-for-marked / bare-residual framing + face-4/5 measured outcomes; manifest note yes/no) → register/wiki edits → doc lint + corpus module green → commit `docs(loop-O): close — R33 closed for marked documents (licence), faces measured, R37 narrowed, wiki increment`

---

## Completion checklist (Loop O definition of done)

- [ ] Faces 4–5 measured on real false-stitch compiles (Task 1's report; quoted in R33's closing row).
- [ ] `test_marked_case3_does_not_stitch` (both variants) + `test_bare_identical_still_stitches` + law probes green; both R33 pins inverted.
- [ ] Stem byte-identical across every tally; suites green (non-corpus 787+new / corpus 10).
- [ ] Refused licences recorded as facts, not discarded.
- [ ] R33 struck-kept with the licence + measurements; R37 narrowed; wiki updated; doc lint green.
- [ ] François shown the close (manifest note = his call); nothing GrainCorp-authored committed.
