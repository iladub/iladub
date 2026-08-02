# Loop L — Accommodation Layer First Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the real `Shipping-Stem-2026-07-31.pdf` compile and ground end-to-end through the public API (spec 2026-08-02 §3) by fixing the measured defect — header-stack selection under ruled evidence — and seed the corpus mechanics minimally along the way.

**Architecture:** The controller's probes (recorded in §Diagnosis below — treat as evidence, verified reproducible) established that hypothesis H is half-true: border-rect de-accommodation already works (`_build_ruled_band` + `rule_aware_lines` recover all 17 headers cleanly at 5.28 pt), and the failure is downstream — `classify` judges `band.lines[0]` (a sparse spanner/banner row) as *the* header, and the hierarchical recovery then refuses (`MERGE_AMBIGUOUS`). The fix is an AXIOM-shaped derivation: **the leaf header row is the deepest line whose words align 1:1 with the ruled columns; lines above it are parent/banner rows spanning ruled-column groups** — loop G's header-confirmed split generalized from 2 levels to a stacked header with banners. Tasks: (1) minimal corpus seed + red test on the specimen; (2) the fix; (3) grounding end-to-end; (4) continuation pages measured; (5) loop close (residues, wiki, doc impact).

**Tech Stack:** existing etkl modules (`regions.py`, `headers.py`, `classifygraph.py`, `vocab/queries/classify-kind.rq`), pdfplumber, rdflib/pySHACL. No new dependencies.

**Doc impact:** increment — `docs/wiki/concepts/table-holon-compilation.md` gains the loop-L outcome in-band (Task 5); no published page contradicted.

## Diagnosis (controller-measured 2026-08-02; reproduce, don't re-derive)

On the specimen (sha256 `3bda68331024dbc802ad7d965dd114aeaff138c65c0571cc4d0a90d2a8b64eee`, page 0):
- `extract_rules` → 336 vertical segments, 20 distinct x; `extract_hrules` → 327; all overlap the one 61-line table band. PDF metadata: `Producer: Microsoft: Print To PDF`, `Title: Shipping Stem 2026 07 31.xlsx`, dominant font 5.28 pt.
- `_build_ruled_band(band, rules, hrules, chars)` yields a 61-line band whose line 3 reads `['GC Fin Year','Month','Port','Reference Number','Exporter','Name Of Ship','Date ETA of Ship','Commencement','Date ETD of Ship','Received','Received','Accepted',…]` — 17 words, 17 ruled columns, perfect recovery.
- `classify(ruled_band)` → `UNSUPPORTED_TABLE, "header has 2 words but 17 columns"`, because the kind evidence treats `band.lines[0]` as the header (see `_reason` in `src/iladub/etkl/regions.py:88-98`); the top lines of the stack are sparse spanners ("Date of Grain Loading" group banner, month banner). Downstream, the hierarchical path's confirmation (`src/iladub/etkl/headers.py:356` area) returns False → `MERGE_AMBIGUOUS` (`src/iladub/etkl/compile.py:341`).
- Full-page runs: page 0 `MERGE_AMBIGUOUS`; pages 1–2 `REGION_TILING_FAILED` (measured, cause not yet localized — Task 4 measures; do NOT assume it is the same defect).

## Global Constraints

- **The §8 gate binds every change:** header-stack selection is a *which-line-reads-as-what* decision → it must be a declarative derivation over evidence facts (SPARQL over the classify evidence graph, or a presence/alignment test with zero tuned constants). A Python heuristic with a tolerance is a review failure. `COORD_EPS`-style existing constants may be *reused* where already established; no new ones.
- **No overfitting (ZERO TOLERANCE):** the fix must be stated as a general law (spec §2b: banners/parents span ruled-column groups; the leaf header populates them 1:1). It must not mention the stem's specifics (17, 'GC Fin Year', month names) anywhere in `src/` or `vocab/`. The synthetic suite (735 passed / 5 skipped baseline) must stay fully green — fixtures are the regression net.
- **The specimen is NEVER committed.** It lives at `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` (gitignored), fetched by script. Tests over it carry `@pytest.mark.corpus` and **skip cleanly when the file is absent** — CI stays deterministic and network-free.
- **Honest failure:** if any Task's measured result contradicts an expected value in this plan (score floor, page-1/2 behavior), STOP that task and report the measurement to the controller — never adjust a bar silently.
- **Environment:** run tests with `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest`; the venv is editable-installed against the MAIN checkout — when working in a worktree, prefix `PYTHONPATH=src` so the worktree's `src/` is exercised (this bit Phase 3; it is real).
- **Commits:** conventional style (`feat(etkl): …`, `test(corpus): …`).

---

### Task 1: Minimal corpus seed + the red specimen test

**Files:**
- Modify: `.gitignore` (add `corpus/` next to the internal/ block)
- Create: `tests/corpus-manifest.ttl` (one entry; the harness plan will grow it)
- Create: `scripts/fetch_corpus.py`
- Create: `tests/test_corpus_stem.py`
- Modify: `pyproject.toml` (register the `corpus` pytest marker)

**Interfaces:**
- Produces: `CORPUS = Path("corpus")` convention; `corpus`-marked tests that skip when files are absent; `scripts/fetch_corpus.py` (no args: fetch every manifest doc absent from `corpus/`, verify sha256). Tasks 2–4 add tests to `tests/test_corpus_stem.py`.

- [ ] **Step 1: gitignore + marker**

Add to `.gitignore` (near `internal/` if present, else at end): `corpus/`
Add to `pyproject.toml` under `[tool.pytest.ini_options]` (create the table if absent — check first; the repo may not have one):

```toml
[tool.pytest.ini_options]
markers = [
    "corpus: real third-party documents (gitignored corpus/; run with -m corpus)",
]
```

If `[tool.pytest.ini_options]` already exists, append the `markers` key to it.

- [ ] **Step 2: the one-entry manifest**

```turtle
# tests/corpus-manifest.ttl — the real-document corpus manifest (spec 2026-08-02 §4).
# cor: is repo-internal (like dg:) — not published, not w3id-registered.
# Documents are FETCHED, never committed; the sha256 pins the edition measured.
@prefix cor: <https://w3id.org/iladub/corpus#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<urn:iladub:corpus:graincorp-stem-2026-07-31> a cor:Document ;
    cor:file "ag-trade/graincorp-stem-2026-07-31.pdf" ;
    cor:url "https://grains.graincorp.com.au/wp-content/uploads/2021/02/Shipping-Stem-2026-07-31.pdf" ;
    cor:family "ag-trade" ;
    cor:series "graincorp-shipping-stem" ;
    cor:producer "Microsoft: Print To PDF" ;
    cor:fetched "2026-08-02"^^xsd:date ;
    cor:sha256 "3bda68331024dbc802ad7d965dd114aeaff138c65c0571cc4d0a90d2a8b64eee" ;
    cor:expectedVerdict cor:Unadjudicated .
```

- [ ] **Step 3: the fetch script**

```python
#!/usr/bin/env python
"""Corpus fetcher (spec 2026-08-02 §4) — justified PROCEDURAL: network + file I/O +
checksum. Reads tests/corpus-manifest.ttl, downloads absent documents into corpus/,
verifies sha256. A checksum mismatch is REPORTED and the file removed — the URL now
serves a different edition; updating the manifest is a deliberate, reviewed act."""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

from rdflib import Graph, Namespace, RDF

REPO = Path(__file__).resolve().parent.parent
COR = Namespace("https://w3id.org/iladub/corpus#")


def main() -> int:
    g = Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle")
    failures = 0
    for doc in g.subjects(RDF.type, COR.Document):
        rel, url = str(g.value(doc, COR.file)), str(g.value(doc, COR.url))
        want = str(g.value(doc, COR.sha256))
        dest = REPO / "corpus" / rel
        if dest.is_file():
            print(f"present  {rel}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"fetching {rel} <- {url}")
        try:
            urllib.request.urlretrieve(url, dest)
        except OSError as e:
            print(f"  FETCH FAILED ({e}) — URL may have rotted; document skipped")
            failures += 1
            continue
        got = hashlib.sha256(dest.read_bytes()).hexdigest()
        if got != want:
            dest.unlink()
            print(f"  CHECKSUM MISMATCH (got {got[:12]}…) — a different edition now "
                  f"lives at this URL; file removed, manifest unchanged")
            failures += 1
        else:
            print(f"  ok ({want[:12]}…)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Note the manifest query uses `g.subjects(None, COR.Document)` — that is wrong on purpose to catch in the test below? NO — it is simply wrong: the pattern for typed subjects is `g.subjects(RDF.type, COR.Document)`. Use `from rdflib import RDF` and `g.subjects(RDF.type, COR.Document)`. (Left as an explicit correction so the implementer does not copy the wrong line.)

- [ ] **Step 4: fetch the specimen + write the red test**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python scripts/fetch_corpus.py`
Expected: fetches (or reports present) with checksum ok. If the URL has already rotted, copy the controller's verified specimen from the session scratchpad (`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/44aa6924-1ce0-4917-88ed-bdd6acfc2dd6/scratchpad/stem-2026-07-31.pdf`) into `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` and verify the sha256 matches the manifest.

```python
# tests/test_corpus_stem.py
"""Loop L — the real GrainCorp stem (spec 2026-08-02 §3): the fluent-reader
invariant's first specimen. Corpus-marked: skips when corpus/ is not populated."""
import pytest

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STEM = REPO / "corpus" / "ag-trade" / "graincorp-stem-2026-07-31.pdf"

pytestmark = pytest.mark.corpus

needs_stem = pytest.mark.skipif(not STEM.is_file(),
                                reason="corpus not populated (scripts/fetch_corpus.py)")


@needs_stem
def test_stem_page0_compiles():
    """The invariant (spec §2): a human reads this page without hesitation, so it
    must compile — not escalate. Red until the header-stack fix lands."""
    from iladub.etkl import compile_tables, RegionKind
    rep = compile_tables(str(STEM), page_number=0)
    verdicts = [(r.kind, r.verdict, r.reason) for r in rep.regions]
    compiled = [r for r in rep.regions
                if r.verdict not in ("escalated",) and r.kind not in (RegionKind.NON_TABLE,)]
    assert compiled, f"page 0 produced no compiled table region: {verdicts}"
    assert sum(r.cells for r in rep.regions) >= 400, verdicts
    # Loop-K neighborhood (0.9496 on its edition). If the fix compiles the page but
    # lands below this floor: STOP, report the measured score to the controller —
    # do not lower the bar (Global Constraints: honest failure).
    assert rep.score >= 0.9, f"score {rep.score:.4f}"
```

- [ ] **Step 5: run to verify RED for the right reason**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_corpus_stem.py -m corpus -v`
Expected: FAIL on `assert compiled` with the MERGE_AMBIGUOUS region visible in the message (not a skip, not an import error). Also run WITHOUT the corpus dir present (temporarily `mv corpus corpus.bak`): expected SKIP with the fetch-script hint; restore afterward.

- [ ] **Step 6: Commit**

```bash
git add .gitignore pyproject.toml tests/corpus-manifest.ttl scripts/fetch_corpus.py tests/test_corpus_stem.py
git commit -m "test(corpus): seed manifest + fetcher + red stem specimen test (loop L, spec §3/§4 first slice)"
```

---

### Task 2: The fix — header-stack selection under ruled evidence

**Files:**
- Modify: `src/iladub/etkl/regions.py` and/or `src/iladub/etkl/classifygraph.py` and/or `vocab/queries/classify-kind.rq` (the kind evidence/decision)
- Modify: `src/iladub/etkl/headers.py` (the stacked-header recovery, seam at the confirmation that currently returns False → MERGE_AMBIGUOUS)
- Test: `tests/etkl/test_header_stack.py` (new; synthetic fixtures) + the Task-1 corpus test turning green on compile

**Interfaces:**
- Consumes: the Diagnosis section's measured facts; existing machinery — `_build_ruled_band`, `rule_aware_lines`, the header-confirmed split (loop G), `classify_evidence`/`run_kind` (B2c), `assert_hier_region` path.
- Produces: `classify`/the hierarchical path handling a ruled band whose header STACK is [banner/spanner rows…, leaf header row] — the general law, stated here and to be implemented declaratively:
  1. **Leaf header row** = the deepest line above the body whose words align 1:1 with the ruled columns (every word inside exactly one ruled column, every ruled column populated). Alignment is the existing `_word_in_column`-style presence test against rule x-positions — no new constants.
  2. **Rows above the leaf header** are parent/banner rows: each word must span a contiguous GROUP of ruled columns (its bbox covers ≥1 ruled column fully); they become parent nodes over the columns they cover (the existing loop-G parent/child machinery), or — when a row spans ALL columns (a title banner like the month line) — a `tab:RegionCaption`-style banner, not a header level.
  3. **Body starts** at the first line after the leaf header. Nothing about this decision may read label TEXT — geometry and rule alignment only (R4's lesson).

**Implementation guidance (constrained, not prescriptive):** prefer extending the evidence graph + `classify-kind.rq`/the header-split derivations over adding Python conditionals — the decision "which line is the leaf header" is exactly the class the gate sends to AXIOM. Read `vocab/queries/header-body-split.rq` (B2a) first: the leaf-header law above may be expressible as an extension of that split. Where the ruled band already carries one Word per ruled column (`rule_aware_lines`), the 1:1 alignment test is word-count + containment — presence tests, no tolerances. If any sub-decision turns out genuinely underdetermined (no rules, colliding glyphs, no alignment signal), it escalates as today — this loop only widens the *ruled* path.

- [ ] **Step 1: Write the failing synthetic tests FIRST** (the general law, no stem specifics)

```python
# tests/etkl/test_header_stack.py
"""Loop L — stacked headers with banner rows above the leaf header (the general
law; spec 2026-08-02 §2b/§3). Synthetic: a ruled band whose line 0 is a full-width
banner, line 1 a 2-group spanner, line 2 the 1:1 leaf header, lines 3+ the body."""
# Fixture-builder: READ tests/etkl/fixtures.py FIRST and reuse its canvas/writer
# idiom (e.g. how crosstab_table_pdf draws grid lines at exact column x's) —
# import whatever real helpers it exposes; do not reinvent PDF plumbing here.


def _stacked_banner_pdf(path):
    """3-level stack over 4 ruled columns:
        line0: 'Quarterly Movements'                  (banner, spans all 4)
        line1: 'Arrivals' (cols 0-1) 'Departures' (cols 2-3)   (parents)
        line2: 'Port' 'Tonnes' 'Port' 'Tonnes'        (leaf header, 1:1)
        line3+: 4 body rows of data with vertical rules at all 5 column edges
    Build with the same reportlab idiom as fixtures.crosstab_table_pdf (grid lines
    drawn at exact column x's; distinct column content types)."""
    ...


def test_banner_and_parents_recovered_not_escalated(tmp_path):
    from iladub.etkl import compile_tables
    pdf = str(tmp_path / "stack.pdf")
    _stacked_banner_pdf(pdf)
    rep = compile_tables(pdf)
    assert not any(r.verdict == "escalated" for r in rep.regions), \
        [(r.kind, r.reason) for r in rep.regions]
    assert rep.score >= 0.9
    # the leaf header populated the columns; the banner did NOT become a header level
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    headers = [str(o) for s in rep.graph.subjects(RDF.type, TAB.ColumnHeader)
               for o in rep.graph.objects(s, TAB.headerText)]
    assert "Port" in headers and "Quarterly Movements" not in headers


def test_flat_table_unaffected(tmp_path):
    """Regression guard: a plain single-header ruled table still compiles identically."""
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf
    pdf = str(tmp_path / "flat.pdf")
    simple_table_pdf(pdf)
    rep = compile_tables(pdf)
    assert not any(r.verdict == "escalated" for r in rep.regions)
```

The `...` in `_stacked_banner_pdf` is the ONE deliberate open point: the implementer writes the fixture following `fixtures.crosstab_table_pdf`'s exact reportlab idiom (read it first). The predicate names in the header assertion (`TAB.ColumnHeader`, `TAB.headerText`) must be checked against `src/iladub/etkl/holon.py` / `vocab/ontology/tab.ttl` and corrected to the real vocabulary before running — verify, don't trust this plan.

- [ ] **Step 2: Run both new tests — expect the stack test RED (escalated / banner-as-header), the flat test GREEN**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/etkl/test_header_stack.py -v`

- [ ] **Step 3: Implement the law** (per the Produces block; prefer the declarative seam; keep the diff minimal and gate-clean; state the §8 classification of each change in its docstring)

- [ ] **Step 4: Green locally, then the specimen**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/etkl/test_header_stack.py tests/test_corpus_stem.py -v`
(no `-m` filter — corpus tests run whenever `corpus/` is populated; their skip guard, not the marker, is what protects CI)
Expected: header-stack tests green; `test_stem_page0_compiles` green (compiled, ≥400 cells, score ≥ 0.9) — if the score lands below 0.9 with a compiled page, STOP and report the measured value.

- [ ] **Step 5: Full synthetic suite — zero regressions**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest -q`
Expected: 735+ passed (baseline 735/5 plus this loop's new tests), 0 failed.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/ vocab/queries/ tests/etkl/test_header_stack.py
git commit -m "feat(etkl): header-stack selection under ruled evidence — leaf header = deepest 1:1 rule-aligned line; banners/parents above (loop L, AXIOM)"
```

---

### Task 3: Grounding end-to-end on the real specimen

**Files:**
- Test: `tests/test_corpus_stem.py` (append)

**Interfaces:**
- Consumes: Task 2's compiled graph; the shipped grounding (`iladub.feed.ground_document`, the stem contract at `examples/shipping/stem-{contract,terms,shapes}.ttl`, the always-abstain proposer idiom from `tests/test_stem_contract.py`).

- [ ] **Step 1: Append the grounding test**

```python
@needs_stem
def test_stem_page0_grounds_against_contract():
    """Loop K's capstone on the LIVE document: assert/propose split with accountable
    promotions; non-grain cargo refused. Tallies are printed (edition-dependent),
    invariants are asserted (edition-independent)."""
    from rdflib import Graph, Namespace, RDF, URIRef
    from iladub.etkl import compile_tables
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

    ILADUB = Namespace("https://w3id.org/iladub#")
    SHIP = Namespace("https://example.org/shipping#")
    rep = compile_tables(str(STEM), page_number=0)
    contract = load_contract("examples/shipping/stem-contract.ttl")
    terms = Graph().parse("examples/shipping/stem-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/shipping/stem-shapes.ttl", format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, str(SHIP) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(rep.graph, contract, abstain, terms, shapes, g)
    grounded = set(g.subjects(RDF.type, ILADUB.GroundedNode))
    proposed = set(g.subjects(RDF.type, ILADUB.CandidateConcept))
    print(f"\nstem 2026-07-31 p0: grounded={len(grounded)} quarantined={len(proposed)}")
    assert len(grounded) >= 50 and len(proposed) > 0
    # every grounded node behind exactly one accountable promotion (the §3 invariant)
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1
    # honest refusal: non-grain cargo visible on this edition (Woodchip, Cement rows
    # measured in the ascii render) must NOT ground through the grain scheme
    grounded_texts = {str(t) for n in grounded for t in g.objects(n, ILADUB.surfaceText)}
    assert not any("Woodchip" in t or "Cement" in t for t in grounded_texts), \
        sorted(t for t in grounded_texts if "Wood" in t or "Cem" in t)
```

**Verify the call signature first:** `ground_document(graph, contract, proposer, terms, shapes, g)` is taken from `src/iladub/feed.py:174` — read that function before running; if its parameters differ (order, contract node argument like `tests/test_stem_contract.py`'s `URIRef("urn:slot#s1")` slot), adapt the CALL, never the assertions. Same for `ILADUB.surfaceText`/`wasPromotedBy` — confirm the exact predicates in `vocab/ontology/iladub.ttl` and `tests/test_grounding.py`, correct the test to the real vocabulary.

- [ ] **Step 2: Run — expect green with the tally printed**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_corpus_stem.py -m corpus -v -s`
Record the printed grounded/quarantined tally in the commit body — it is this loop's measured capstone number for THIS edition.

- [ ] **Step 3: Commit**

```bash
git add tests/test_corpus_stem.py
git commit -m "test(corpus): live stem grounds against the stem contract — assert/propose split + honest non-grain refusal (loop L capstone)"
```

---

### Task 4: Continuation pages — measure, don't assume

**Files:**
- Test: `tests/test_corpus_stem.py` (append)

- [ ] **Step 1: Measure pages 1 and 2**

```python
@needs_stem
@pytest.mark.parametrize("page", [1, 2])
def test_stem_continuation_pages_status(page):
    """Pages 1-2 escalated REGION_TILING_FAILED pre-loop (cause NOT localized).
    This test records the post-fix state honestly: they must either compile or
    escalate — never crash. If they still escalate after Task 2, that is a
    MEASURED RESULT: report it to the controller; it becomes a registered
    residue + follow-up loop, not a silent pass and not a forced fix."""
    from iladub.etkl import compile_tables
    rep = compile_tables(str(STEM), page_number=page)
    assert rep.regions, "no regions at all"
    print(f"\nstem p{page}: score={rep.score:.4f} "
          f"regions={[(r.kind.name, r.verdict, r.reason) for r in rep.regions]}")
```

- [ ] **Step 2: Additionally measure the CONTINUATION CASE (feeds Loop M, spec §3b)**

Append to the same test (or a sibling) a printed classification: does page 1's first
band line equal page 0's leaf header row (Excel print-titles → taxonomy case 2 WITH
repeated headers), or is it body-shaped (headerless continuation)? Compare the ruled
column x-positions of pages 0/1/2 (same template ⇒ same x's under the same scale) and
print both facts. No assertion beyond non-crash — this is Loop M's intake evidence.

- [ ] **Step 3: Run, read the output, and ROUTE the result**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_corpus_stem.py -m corpus -v -s -k continuation`
If pages 1–2 now compile: strengthen the test to assert it (mirror Task 1's compiled-region assertion) in the same commit. If they still escalate: leave the test as the honest recorder, and report the reason strings + the continuation-case classification to the controller for residue registration in Task 5. Either way the test passes — its assertions match reality, its print is the evidence.

- [ ] **Step 4: Commit**

```bash
git add tests/test_corpus_stem.py
git commit -m "test(corpus): continuation pages measured post-fix + continuation-case classification for loop M (loop L, honest recorder)"
```

---

### Task 5: Loop close — residues, wiki, adjudication

**Files:**
- Modify: `docs/superpowers/residues.md` (register/close per measured outcomes)
- Modify: `tests/corpus-manifest.ttl` (set the specimen's verdict from `cor:Unadjudicated` to the measured outcome)
- Modify: `docs/wiki/concepts/table-holon-compilation.md` (loop-L increment; bump `updated:`)

- [ ] **Step 1: Manifest adjudication**

Replace `cor:expectedVerdict cor:Unadjudicated .` with the measured outcome, e.g. (adapt the floor to Task 2's measured score — never above it):

```turtle
    cor:expectedVerdict cor:CompilesAbove ;
    cor:scoreFloor "0.90"^^xsd:decimal ;
    cor:adjudication [ cor:by "François Rosselet" ; cor:on "2026-08-02"^^xsd:date ;
        cor:rationale "Fluent-reader invariant: page 0 compiles post loop-L header-stack fix; pages 1-2 status per loop record" ] .
```

**The adjudication names François — it is HIS act:** the controller presents the measured outcomes and François confirms (in-session confirmation suffices; record the date). Do not fabricate his adjudication.

- [ ] **Step 2: Residues**

- If pages 1–2 still escalate: append a row (next free R-number) recording the measured reason strings, why deferred (loop-L slice = page 0 end-to-end), and what would close it (localize + fix as its own loop).
- Check R4's open forms and R18: if the stem's blank-total subtotals / doubled-key behaviors surfaced in Task 2–3 runs, annotate — do not silently close anything.

- [ ] **Step 3: Wiki increment**

In `docs/wiki/concepts/table-holon-compilation.md`: add loop L to the arc (2–4 sentences: the accommodation thesis, the header-stack law, the live-stem result with the measured tally), add `tests/test_corpus_stem.py` to `sources:`, bump `updated:` to the commit date. Run the doc lint: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_doc_governance.py -q -W default::UserWarning` → green.

- [ ] **Step 4: Full suite + commit**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest -q` → all green (corpus tests skip without `-m corpus` only if corpus/ absent; with it present they run — both states must be green).

```bash
git add docs/superpowers/residues.md tests/corpus-manifest.ttl docs/wiki/concepts/table-holon-compilation.md
git commit -m "docs(loop-L): close — adjudicated stem verdict, residues routed, wiki increment (measured tallies in body)"
```

---

## Completion checklist (Loop L definition of done — the loop CLOSES, spec §3)

- [ ] `test_stem_page0_compiles` green: the real 2026-07-31 stem compiles via the public API (≥400 cells, score ≥ 0.9 or the measured value explicitly accepted by François).
- [ ] `test_stem_page0_grounds_against_contract` green: live-document assert/propose split, every grounded node behind exactly one PromotionDecision, non-grain cargo refused. Tally recorded in the commit body.
- [ ] Synthetic suite: zero regressions (735/5 baseline + new tests).
- [ ] Pages 1–2: measured and routed (compiled-and-asserted, or residue-registered).
- [ ] Manifest verdict adjudicated BY FRANÇOIS; wiki + residues updated; doc lint green.
- [ ] Nothing GrainCorp-authored committed (`git status` + `git log --stat` show no corpus content).
