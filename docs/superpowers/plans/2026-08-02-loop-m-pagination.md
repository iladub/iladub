# Loop M — Pagination De-accommodation (Taxonomy Case 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The whole 3-page GrainCorp stem compiles as ONE logical table through a new `compile_document` driver — continuation pages recognized declaratively, repeated headers carried (never read as data), body rows keeping their true page — and grounds full-document (spec 2026-08-02 §3b; closes R29).

**Architecture:** A new document driver (`src/iladub/etkl/document.py`) compiles page 0 unchanged, then for each later page derives **continuation-of** as an AXIOM over a two-page leaf-evidence graph (leaf rows text-identical column-for-column at identical ruled x's). Recognition licenses carrying page 0's confirmed header-row reading into the continuation page's compile (the block-rule evidence R29 measured as page-0-only), suppresses the repeated header block as carried `tab:RepeatedHeader` facts, and links the page tables with `tab:continuesTable`. The feed walks continuation chains as one logical table, so grounding runs over the full document. Case 1 (unrelated tables on consecutive pages) must stay unstitched — proven by a synthetic fixture.

**Tech Stack:** existing etkl modules + one new `document.py`, one new `.rq`, two new `tab:` terms. No new dependencies.

**Doc impact:** increment — wiki `table-holon-compilation` page gains the loop-M outcome in-band (Task 5); no published page contradicted.

## Measured intake (Loop L Task 4 + controller probes 2026-08-02; reproduce, don't re-derive)

- Page 1's ruled band: 80 lines; header block = `['Date of Grain'] (1w) / [7w wrap row] / [17w LEAF]` then 17-word body rows — **page 0's header stack minus the timestamp furniture line**. Leaf rows repeat **verbatim** across pages; ruled column x's identical on pages 1–2 (page 0 carries one extra rule x 832.32). Pages 1–2 escalate `REGION_TILING_FAILED` today because clause-0's block-rule evidence exists only on page 0 (R29).
- `tab:onPage` already emitted on every cell (`src/iladub/etkl/holon.py:46` etc.) — page provenance is free.
- `_DOC` is a FIXED URI (`src/iladub/etkl/compile.py:21`) — two per-page compiles collide on `doc#table0`; the driver must namespace per page.
- Loop L's hook (`compile.py` → `ruledroles.resolve_ruled_header_rows`) is the carrier seam: it already gates the header reading; a carried reading enters there.

## Global Constraints

- **§8 gate:** "is page N a continuation of page N−1" is a which-reads-as-what decision → a SPARQL derivation over evidence facts (text identity per column + ruled-x identity are presence/equality tests; ZERO numeric constants beyond reusing `COORD_EPS` for float equality; no label-text SEMANTICS read — raw string equality between two pages' cells is evidence comparison, not text reading, state this in the query header). The driver/carrier plumbing is justified PROCEDURAL wiring.
- **§5/§7:** repeated headers are CARRIED as `tab:RepeatedHeader` facts with full provenance — never dropped, never read as data rows; a page that does NOT match stays independent (case 1) — stitching is evidence-licensed, never assumed. Any partial match (some leaf cells equal, others not) → NOT a continuation (no fuzzy matching).
- **No overfitting:** no stem specifics ('17', 'GC Fin Year', month names) in `src/` or `vocab/`. Synthetic suite baseline **754 passed / 5 skipped** — zero regressions. Case-1 fixture must be genuinely different tables (different leaf texts AND different x's).
- **Honest failure:** if a measured result contradicts a plan expectation (cell counts, grounding tallies, page-2 behavior), STOP that task and report — never adjust a bar silently.
- **Specimen:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` (gitignored; sha256 `3bda6833…b64eee`; restore from the manifest URL or ask the controller if absent). Never committed.
- **Environment:** `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest …` (PYTHONPATH mandatory in a worktree). Known pattern: do NOT background the full suite — run it foreground and wait, or the controller will supply the tally.
- **Human checkpoint (Task 5):** the manifest verdict flip to `cor:CompilesAbove` is FRANÇOIS's adjudication (his recorded HOLD lifts "when the full document compiles") — the controller presents the measured whole-document result and he confirms; never fabricate it.

---

### Task 1: Red driver tests + the case-1 fixture

**Files:**
- Create: `tests/etkl/test_document.py` (case-1 synthetic; driver API)
- Modify: `tests/test_corpus_stem.py` (the whole-stem red test)
- Modify: `tests/etkl/fixtures.py` (two-page unrelated-tables fixture)

**Interfaces:**
- Produces (Tasks 2–4 implement against these): `from iladub.etkl.document import compile_document` — `compile_document(pdf_path: str, validate_shapes: bool = True) -> DocumentReport` where `DocumentReport` has `.graph` (one merged rdflib Graph), `.pages` (list of per-page `CompilationReport`), `.score` (asserted/(asserted+escalated) over the whole document), and `.chains` (list of tuples of table URIRefs, each tuple one continuation chain in page order, length 1 for unstitched tables).

- [ ] **Step 1: Two-page unrelated fixture** (in `fixtures.py`, following the module's existing reportlab idiom — read a neighboring builder first; reuse its helpers)

```python
def two_page_unrelated_pdf(path: str) -> dict:
    """Taxonomy case 1: two CONSECUTIVE pages, each a self-contained ruled record
    table with DIFFERENT leaf headers AND different column x-positions
    (page 1: Port|Ship|Tonnes at one grid; page 2: Patient|Analyte|Result|Unit at
    a 4-column grid shifted right). compile_document must NOT stitch them."""
```

Body per the module idiom; both pages must compile standalone (verify with `compile_tables(path, page_number=p)` in the test).

- [ ] **Step 2: The driver tests**

```python
# tests/etkl/test_document.py
"""Loop M — the document driver (spec 2026-08-02 §3b): case-1 independence and
the DocumentReport contract. The case-2 stitching proof lives in
tests/test_corpus_stem.py against the real specimen."""
from iladub.etkl.document import compile_document
from tests.etkl.fixtures import two_page_unrelated_pdf


def test_case1_unrelated_pages_never_stitch(tmp_path):
    pdf = str(tmp_path / "unrelated.pdf")
    two_page_unrelated_pdf(pdf)
    rep = compile_document(pdf)
    assert len(rep.pages) == 2
    assert all(len(chain) == 1 for chain in rep.chains), rep.chains
    # both pages' tables asserted independently
    assert all(any(r.verdict == "asserted" for r in p.regions) for p in rep.pages)


def test_single_page_document_matches_compile_tables(tmp_path):
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf
    pdf = str(tmp_path / "single.pdf")
    simple_table_pdf(pdf)
    single = compile_tables(pdf)
    doc = compile_document(pdf)
    assert len(doc.pages) == 1
    assert doc.score == single.score
    assert len(doc.graph) >= len(single.graph)   # same assertions (URIs may be page-scoped)
```

Append to `tests/test_corpus_stem.py`:

```python
@needs_stem
def test_stem_document_stitches_three_pages():
    """Loop M's verifier (spec §3b): the whole stem is ONE logical table.
    RED until the driver + recognition land."""
    from iladub.etkl.document import compile_document
    from iladub.etkl.holon import TAB
    from rdflib import RDF
    rep = compile_document(str(STEM))
    assert len(rep.pages) == 3
    assert len(rep.chains) == 1 and len(rep.chains[0]) == 3, rep.chains
    total_cells = sum(sum(r.cells for r in p.regions) for p in rep.pages)
    print(f"\nstem document: score={rep.score:.4f} total_cells={total_cells}")
    assert total_cells > 586          # more than page 0 alone
    assert rep.score >= 0.9           # floor; if compiled-but-lower, STOP and report
    # repeated headers carried, never data: RepeatedHeader facts exist on pages 1-2
    reps = list(rep.graph.subjects(RDF.type, TAB.RepeatedHeader))
    assert reps, "repeated header blocks must be carried as facts"
    # page provenance: cells exist on all three pages
    pages = {int(o) for o in rep.graph.objects(None, TAB.onPage)}
    assert pages == {0, 1, 2}, pages
```

- [ ] **Step 3: Run — RED for the right reasons**

Run: `PYTHONPATH=src /Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/etkl/test_document.py tests/test_corpus_stem.py::test_stem_document_stitches_three_pages -v`
Expected: ImportError (`iladub.etkl.document` does not exist) — collection-level red, uniformly.

- [ ] **Step 4: Commit**

```bash
git add tests/etkl/test_document.py tests/test_corpus_stem.py tests/etkl/fixtures.py
git commit -m "test(etkl): red document-driver tests — case-1 independence + whole-stem stitching (loop M)"
```

---

### Task 2: Continuation recognition (AXIOM) + the document driver skeleton

**Files:**
- Create: `vocab/queries/continuation-of.rq`
- Create: `src/iladub/etkl/document.py`
- Modify: `vocab/ontology/tab.ttl` (two terms: `tab:continuesTable` object property, `tab:RepeatedHeader` class — follow the file's comment/version conventions)
- Test: `tests/etkl/test_document.py` (append law-level tests)

**Interfaces:**
- Consumes: Loop L's `ruledroles.ruled_boundaries`/`leaf` notions (read `src/iladub/etkl/ruledroles.py` first), `_build_ruled_band` (`compile.py`), `extract_rules/extract_hrules/extract_chars/extract_words/text_lines` (`geometry.py`), `detect_bands` (`bands.py`).
- Produces: `continuation_evidence(prev_band, prev_grid_xs, cur_band, cur_grid_xs) -> Graph` (PROCEDURAL emitter: per page, one fact per leaf cell — column index, exact text, column rule x — plus per-page rule-x list facts) and `is_continuation(evidence: Graph) -> bool` running `continuation-of.rq`. The law (state in the query header): **page N continues page N−1 iff (a) both leaf rows exist, (b) every column's leaf cell text on page N equals page N−1's exactly, (c) no column exists on either page without a matching counterpart, (d) the ruled x-sets agree under COORD_EPS equality** — all as `FILTER NOT EXISTS` presence patterns over facts present; zero numeric literals in the query (the epsilon is applied at emission, as `ruledroles` does).
- Also produces the driver skeleton: `compile_document` that compiles each page via `compile_tables(pdf, page_number=p, doc_uri=<page-scoped>)` — which requires threading an optional `doc_uri: URIRef | None = None` parameter through `compile_tables` (default `_DOC`, existing behavior byte-identical; page-scoped URIs are `URIRef(f"{_DOC}/p{p}")`). Chains built from `is_continuation` on adjacent page pairs; `tab:continuesTable` asserted `(page_n_table, page_{n-1}_table)`.

- [ ] **Step 1: Law-level tests first** (append to `tests/etkl/test_document.py`)

```python
def test_continuation_law_positive_and_negatives():
    """Law probes on hand-built evidence: identical leaves+x's -> continuation;
    one differing cell text -> not; one extra column -> not; shifted x -> not."""
    from iladub.etkl.document import continuation_evidence_from_facts, is_continuation
    # helper builds the evidence graph directly from (col, text, x) triples per page
    same = [(0, "Port", 40.0), (1, "Ship", 110.0), (2, "Tonnes", 180.0)]
    assert is_continuation(continuation_evidence_from_facts(same, same))
    diff_text = [(0, "Port", 40.0), (1, "Vessel", 110.0), (2, "Tonnes", 180.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, diff_text))
    extra_col = same + [(3, "Flag", 250.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, extra_col))
    shifted = [(0, "Port", 40.0), (1, "Ship", 111.5), (2, "Tonnes", 180.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, shifted))
```

(`continuation_evidence_from_facts` is the test-facing constructor the production emitter also uses internally — one evidence shape, two entry points.)

- [ ] **Step 2: RED** — run the new tests; ImportError, then implement.

- [ ] **Step 3: Implement** — the `.rq`, the emitter(s), `is_continuation`, the `tab:` terms, the `doc_uri` threading (grep every `_DOC` use in `compile.py`/`holon.py` — table, region, and candidate URIs must ALL derive from the parameter or stitching collides), and the driver skeleton with chains (recognition only — carried compile is Task 3; for now continuation pages still escalate, chains reflect recognition regardless of compile outcome ONLY if that keeps `test_case1…` green; otherwise chains = recognized AND asserted, note which in the docstring).
- [ ] **Step 4: GREEN on law tests + case-1 + single-page equivalence; the stem test still RED (pages 1-2 still escalate)** — that's the expected mid-loop state. Full docgov + etkl battery spot-run.
- [ ] **Step 5: Commit** — `feat(etkl): continuation-of AXIOM + compile_document driver skeleton with page-scoped URIs (loop M)`

---

### Task 3: The carried header reading + repeated-header carriage

**Files:**
- Modify: `src/iladub/etkl/document.py`, `src/iladub/etkl/compile.py` (carrier parameter), `src/iladub/etkl/ruledroles.py` (accept a carried reading — read its round-2 shape first)
- Test: the Task-1 stem test turns GREEN

**Interfaces:**
- Consumes: Task 2's recognition; Loop L's role machinery.
- Produces: when page N is recognized as a continuation, `compile_document` compiles it with a **carried header reading**: the page's own header rows (band top through its leaf row, located by the same 1:1 rule-alignment notion) are matched row-by-row against page N−1's header block by exact text identity; matched rows take the PRIOR page's confirmed roles (`continuation` wrap rows; the leaf is the leaf); the prior page's furniture rows simply have no counterpart. The carried reading enters through a new optional `compile_tables(..., carried_header_roles=None)` consumed at Loop L's hook — **carriage only ever applies when recognition licensed it**; an unrecognized page never receives a reading (case 1 safe by construction). The repeated header rows are asserted as `tab:RepeatedHeader` (one node per row, `tab:onPage`, bbox provenance, `prov:wasDerivedFrom` the page-0 header node it repeats) and NEVER become EntryCells.

**Honest-failure watchpoints (STOP and report if hit):** page 2's leaf differs from page 1's; body rows of continuation pages fail tiling for a NEW reason after carriage (report the reason string — do not widen the law); the stitched score lands below 0.9 while pages compile.

- [ ] Steps: implement → stem test GREEN (`score`, `total_cells`, chains `(p0,p1,p2)`, RepeatedHeader facts, onPage {0,1,2}) → spot-run Loop L's batteries (`test_header_stack.py`, `test_corpus_stem.py` all) → commit `feat(etkl): carried header reading for recognized continuations + tab:RepeatedHeader carriage (loop M — the stem stitches)`.

---

### Task 4: Whole-document grounding + feed chain-walk + full suite

**Files:**
- Modify: `src/iladub/feed.py` (chain-walk: a table with `tab:continuesTable` predecessors is read as ONE logical table — records in page order, continuation pages' records joining the head table's identity space; read the row-group key-injection path first and measure whether groups on continuation pages behave)
- Test: `tests/test_corpus_stem.py` (append)

```python
@needs_stem
def test_stem_document_grounds_full():
    """Loop-K's capstone over the WHOLE document. Invariants asserted,
    edition-dependent tallies printed."""
    from rdflib import Graph, Namespace, RDF
    from iladub.etkl.document import compile_document
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal
    ILADUB = Namespace("https://w3id.org/iladub#")
    SHIP = Namespace("https://example.org/shipping#")
    rep = compile_document(str(STEM))
    contract = load_contract("examples/shipping/stem-contract.ttl")
    terms = Graph().parse("examples/shipping/stem-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/shipping/stem-shapes.ttl", format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, str(SHIP) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(rep.graph, contract, abstain, terms, shapes, g)
    grounded = set(g.subjects(RDF.type, ILADUB.GroundedNode))
    print(f"\nstem FULL document: records={result.records} grounded={len(grounded)} "
          f"still-quarantined={result.proposed}")
    assert result.records > 33         # page 0 alone had 33-record-scale; full doc more
    assert len(grounded) > 167         # more than page 0 alone
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1
```

(Adapt attribute/predicate names to reality per the Loop-L precedent — assertions' meaning fixed, plumbing verified against `feed.py`/`iladub.ttl`.)

- [ ] Steps: red (chain-walk absent → duplicate/fragmented records or undercount) → implement chain-walk → green with tally printed → **full suite foreground** (baseline 754/5; zero regressions) → commit `feat(feed): continuation chains read as one logical table — full-document grounding (loop M capstone)`.

---

### Task 5: Loop close — R29, manifest flip (François), wiki, residues

**Files:**
- Modify: `docs/superpowers/residues.md` (DELETE R29's row — the loop that closes a residue deletes it; register any new measured residues from Tasks 3–4 watchpoints)
- Modify: `tests/corpus-manifest.ttl` (verdict flip — ONLY after François confirms)
- Modify: `docs/wiki/concepts/table-holon-compilation.md` (loop-M increment; `updated:` bump)

- [ ] **Step 1 (controller-mediated human checkpoint):** present François the measured whole-document result (score, cells, records, grounding tally) — his HOLD lifts by his own rationale. On his confirmation: `cor:expectedVerdict cor:CompilesAbove ; cor:scoreFloor "<at-or-below-measured>"^^xsd:decimal ;` + a NEW adjudication node (keep the HOLD node — adjudication history accretes, matching the register's append style) with his rationale. Define `cor:CompilesAbove`/`cor:scoreFloor` semantics in a manifest header comment (the final review noted no `cor:Hold` term existed — one comment line acknowledging the HOLD-was-Unadjudicated encoding closes that loose end for the future `test_corpus.py`).
- [ ] **Step 2:** residues — delete R29; route watchpoint findings (if any) as new rows; check R30–R32 texts still accurate post-carriage (R32 especially: does the carried reading widen the fabricated-boundary exposure? measure: the carrier only applies roles to TEXT-MATCHED rows, reason it through and state the conclusion in the row if touched).
- [ ] **Step 3:** wiki increment (3–5 sentences: pagination as accommodation operator, the continuation law, the carried reading, full-document numbers); doc lint green; full suite green.
- [ ] **Step 4:** commit `docs(loop-M): close — R29 closed, manifest CompilesAbove (adjudicated), wiki increment (full-document tallies in body)`.

---

## Completion checklist (Loop M definition of done)

- [ ] `test_stem_document_stitches_three_pages` green: ONE chain of three tables, score ≥ 0.9, > 586 cells, RepeatedHeader facts carried, onPage {0,1,2}.
- [ ] `test_stem_document_grounds_full` green with the full-document tally recorded.
- [ ] `test_case1_unrelated_pages_never_stitch` green (stitching is evidence-licensed).
- [ ] Full suite: zero regressions vs 754/5.
- [ ] R29 deleted; manifest `cor:CompilesAbove` set with François's recorded confirmation; wiki updated; doc lint green.
- [ ] Nothing GrainCorp-authored committed.
