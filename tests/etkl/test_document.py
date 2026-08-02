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
    # The RECOGNITION itself must refuse, not merely fail to produce a chain: the chain is empty
    # whenever a page asserts no table, so `chains` alone would still pass if the law over-reached.
    # (This also guards the R33 activation path — carriage in task 3 keys off `recognized`.)
    assert rep.recognized == (), rep.recognized
    # both pages' tables asserted independently
    assert all(any(r.verdict == "asserted" for r in p.regions) for p in rep.pages)


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
    assert not is_continuation(continuation_evidence_from_facts(extra_col, same))
    shifted = [(0, "Port", 40.0), (1, "Ship", 111.5), (2, "Tonnes", 180.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, shifted))


def test_continuation_law_author_boundary_clause_is_load_bearing():
    """Clause (d): the author's DRAWN grid must agree. Same leaf row on both pages,
    but a boundary the author drew at a different x -> not a continuation. (The
    measured reason this clause compares author-drawn boundaries only, never loop-G's
    ink-inferred ones, is stated in continuation-of.rq's header.)"""
    from iladub.etkl.document import continuation_evidence_from_facts, is_continuation
    same = [(0, "Port", 40.0), (1, "Ship", 110.0), (2, "Tonnes", 180.0)]
    xs = (30.0, 100.0, 170.0, 240.0)
    assert is_continuation(continuation_evidence_from_facts(same, same, xs, xs))
    moved = (30.0, 100.0, 171.5, 240.0)
    assert not is_continuation(continuation_evidence_from_facts(same, same, xs, moved))
    dropped = (30.0, 100.0, 240.0)
    assert not is_continuation(continuation_evidence_from_facts(same, same, xs, dropped))
    assert not is_continuation(continuation_evidence_from_facts(same, same, dropped, xs))


def test_continuation_law_needs_both_leaf_rows():
    """Clause (a): a page evidencing no leaf header row neither continues nor is continued."""
    from iladub.etkl.document import continuation_evidence_from_facts, is_continuation
    same = [(0, "Port", 40.0), (1, "Ship", 110.0)]
    assert not is_continuation(continuation_evidence_from_facts(same, []))
    assert not is_continuation(continuation_evidence_from_facts([], same))
    assert not is_continuation(continuation_evidence_from_facts([], []))


def test_template_pages_stitch_the_known_case3_false_positive(tmp_path):
    """PINS A KNOWN LIMIT, not a desired behaviour (residue R33).

    Two logically INDEPENDENT tables built from one template — same `Store|Item|Qty` header on the
    same grid, different data, different per-page banners — satisfy every clause of the
    continuation law, because its evidence is the repeated header block and they share it exactly.
    Measured: `recognized == ((0, 1),)` and `tab:continuesTable` asserted between them.

    This is the taxonomy case-2 / case-3 boundary (spec §2b defers case 3). The test exists so the
    exposure is executable rather than merely written down, and so that whoever closes R33 (a
    body-side presence discriminator — does page N-1's table run to that page's last text line?)
    is forced to come here and invert it.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from iladub.etkl.document import compile_document
    from iladub.etkl.holon import TAB

    cols = [(60.0, 160.0), (170.0, 260.0), (270.0, 360.0)]

    def _page(c, banner, rows, top):
        c.setFont("Courier-Bold", 10)
        c.drawString(60.0, top + 30, banner)
        for (l, _r), h in zip(cols, ["Store", "Item", "Qty"]):
            c.drawString(l, top, h)
        c.setFont("Courier", 10)
        for i, row in enumerate(rows):
            y = top - (i + 1) * 18.0
            for (l, _r), cell in zip(cols, row):
                c.drawString(l, y, cell)
        c.setLineWidth(0.7)
        bottom = top - (len(rows) + 1) * 18.0
        for (l, _r) in cols:
            c.line(l - 4, top + 12, l - 4, bottom)
        c.line(cols[-1][1] + 4, top + 12, cols[-1][1] + 4, bottom)

    pdf = str(tmp_path / "template.pdf")
    top = letter[1] - 90.0
    c = canvas.Canvas(pdf, pagesize=letter)
    _page(c, "NORTH REGION WEEKLY", [("Alpha", "Bolt", "10"), ("Beta", "Nut", "20")], top)
    c.showPage()
    _page(c, "SOUTH REGION MONTHLY", [("Gamma", "Screw", "30"), ("Delta", "Nail", "40")], top)
    c.save()

    rep = compile_document(pdf)
    assert rep.recognized == ((0, 1),), rep.recognized          # the false positive, measured
    assert list(rep.graph.subject_objects(TAB.continuesTable)), "R33: the stitch is asserted"
    # Loop M task 3 re-measured this fixture after the carried header reading landed, and records
    # what carriage did to it — honestly, WITHOUT weakening the pin above (R33 is still open and
    # still exposed by the two assertions above; nothing here excuses it).
    #   * the false stitch is a real CHAIN, not merely a link: both template pages assert, so the
    #     two independent tables are walked as one logical table. This was already true before
    #     carriage — both pages compiled standalone.
    from rdflib import RDF
    assert len(rep.chains) == 1 and len(rep.chains[0]) == 2, rep.chains
    #   * carriage did NOT engage here, measured: these bands compile down the RECORD_TABLE path
    #     (a single-level header), which never reaches loop L's header-stack law, so page 0
    #     confirms no header reading and page 1 receives none. Hence no tab:RepeatedHeader. The
    #     R33 exposure on this fixture is therefore the LINK, not a carried reading — a template
    #     document with a MULTI-LEVEL header would additionally have page 0's roles carried onto
    #     page 1's identical header block. If a future change makes that happen here, this
    #     assertion flips and whoever flips it must say so rather than quietly delete it.
    assert not list(rep.graph.subjects(RDF.type, TAB.RepeatedHeader)), \
        "carriage reached the R33 fixture — re-measure the exposure before changing this"


def test_leaf_block_reads_the_production_bands(tmp_path):
    """The PRODUCTION evidence path, not hand-built facts: the driver's leaf_block must read a
    real compiled band's leaf header row (one cell per ruled column, exact text, ink origin) and
    its author-DRAWN grid boundaries. Guards the emitter the law is only as good as."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import leaf_block, _recognition_blocks
    pdf = str(tmp_path / "unrelated.pdf")
    meta = two_page_unrelated_pdf(pdf)
    for page, headers in ((0, meta["page1_headers"]), (1, meta["page2_headers"])):
        blocks = _recognition_blocks(page_bands(pdf, page))
        assert blocks, f"page {page} evidences no leaf block"
        cells, bounds = blocks[max(blocks)]
        assert [t for _, t, _ in cells] == headers
        assert [c for c, _, _ in cells] == list(range(len(headers)))
        # every boundary reported is one the author drew (the fixture rules ARE the grid)
        assert len(bounds) >= 2
    # a band with no vertical rule evidences nothing — refusal, not a verdict
    assert all(leaf_block(b) is None for b in page_bands(pdf, 0) if not b.rules)


class _Cell:
    """The minimum a header cell is, for the carriage matcher: text + ink box."""
    def __init__(self, text, x0, x1, top=10.0, bottom=20.0):
        self.text, self.x0, self.x1, self.top, self.bottom = text, x0, x1, top, bottom


class _Grid:
    def __init__(self, boundaries):
        self.boundaries = boundaries


_B = _Grid((0.0, 100.0, 200.0, 300.0))


def _reading(rows, table_uri="urn:t", page=0):
    """A confirmed reading over `rows` = [([(text, x0, x1)], role_or_None), ...]."""
    from iladub.etkl.ruledroles import header_reading_of
    from rdflib import URIRef
    header_rows = [[_Cell(*c) for c in cells] for cells, _ in rows]
    roles = [role for _, role in rows[:-1]]
    return header_reading_of(header_rows, _B, roles, URIRef(table_uri), page)


def test_carriage_matches_a_redrawn_block_missing_its_furniture_row():
    """The specimen's shape, in miniature: the head page carries a furniture row the continuation
    page does not redraw. The two rows that ARE redrawn carry their confirmed roles, the leaf
    matches the leaf, and the absent furniture row simply has no counterpart."""
    from iladub.etkl.ruledroles import carried_roles_for
    reading = _reading([
        ([("printed today", 10.0, 60.0)], "furniture"),
        ([("Date of", 110.0, 150.0)], "continuation"),
        ([("Port", 10.0, 40.0), ("Loading", 110.0, 160.0), ("Qty", 210.0, 240.0)], None),
    ])
    page_n = [[_Cell("Date of", 110.0, 150.0)],
              [_Cell("Port", 10.0, 40.0), _Cell("Loading", 110.0, 160.0), _Cell("Qty", 210.0, 240.0)]]
    roles, matched = carried_roles_for(reading, page_n, _B)
    assert roles == ("continuation",)
    assert len(matched) == 2 and matched[-1][1].role is None       # the leaf carried as the leaf
    assert matched[-1][1].source, "the leaf row traces to the head page's source cells"


def test_carriage_refuses_a_row_that_does_not_match_exactly():
    """One character of difference is a refusal, not a near-match: the page keeps its own path."""
    from iladub.etkl.ruledroles import carried_roles_for
    reading = _reading([
        ([("Date of", 110.0, 150.0)], "continuation"),
        ([("Port", 10.0, 40.0), ("Qty", 210.0, 240.0)], None),
    ])
    assert carried_roles_for(reading, [[_Cell("Date  of", 110.0, 150.0)],
                                       [_Cell("Port", 10.0, 40.0), _Cell("Qty", 210.0, 240.0)]],
                             _B) is None
    # same texts, different COLUMN -> also a refusal (identity is per column, not per row)
    assert carried_roles_for(reading, [[_Cell("Date of", 210.0, 250.0)],
                                       [_Cell("Port", 10.0, 40.0), _Cell("Qty", 210.0, 240.0)]],
                             _B) is None


def test_carriage_refuses_an_ambiguous_carried_block():
    """Two carried rows with the SAME signature and DIFFERENT roles: which one a page-N row
    repeats is undecidable by text identity, so the whole carriage is refused rather than taking
    the first."""
    from iladub.etkl.ruledroles import carried_roles_for
    reading = _reading([
        ([("Date of", 110.0, 150.0)], "furniture"),
        ([("Date of", 110.0, 150.0)], "continuation"),
        ([("Port", 10.0, 40.0), ("Qty", 210.0, 240.0)], None),
    ])
    assert carried_roles_for(reading, [[_Cell("Date of", 110.0, 150.0)],
                                       [_Cell("Port", 10.0, 40.0), _Cell("Qty", 210.0, 240.0)]],
                             _B) is None


def test_carriage_refuses_when_the_leaf_is_not_the_leaf():
    """A page whose LAST header row matches a NON-leaf carried row must not take that row's
    reading for its leaf — nor may a non-leaf row take the carried leaf's."""
    from iladub.etkl.ruledroles import carried_roles_for
    reading = _reading([
        ([("Date of", 110.0, 150.0)], "continuation"),
        ([("Port", 10.0, 40.0), ("Qty", 210.0, 240.0)], None),
    ])
    assert carried_roles_for(reading, [[_Cell("Date of", 110.0, 150.0)]], _B) is None
    assert carried_roles_for(reading,
                             [[_Cell("Port", 10.0, 40.0), _Cell("Qty", 210.0, 240.0)],
                              [_Cell("Date of", 110.0, 150.0)]], _B) is None


def test_repeated_header_facts_carry_page_bbox_and_head_page_provenance():
    """One tab:RepeatedHeader per repeated row, with its page, its measured box, its surface text
    (the drop-continuation guard) and prov:wasDerivedFrom the HEAD page's header-source cells."""
    from rdflib import Graph, RDF, URIRef
    from iladub.etkl.ruledroles import PROV, TAB, carried_roles_for, emit_repeated_headers
    reading = _reading([
        ([("Date of", 110.0, 150.0)], "continuation"),
        ([("Port", 10.0, 40.0), ("Qty", 210.0, 240.0)], None),
    ], table_uri="urn:head", page=0)
    page_n = [[_Cell("Date of", 110.0, 150.0, top=5.0, bottom=12.0)],
              [_Cell("Port", 10.0, 40.0, top=15.0, bottom=22.0),
               _Cell("Qty", 210.0, 240.0, top=15.0, bottom=22.0)]]
    _roles, matched = carried_roles_for(reading, page_n, _B)
    g = Graph()
    emit_repeated_headers(g, URIRef("urn:cont"), page_n, matched, 1)
    reps = sorted(g.subjects(RDF.type, TAB.RepeatedHeader))
    assert len(reps) == 2                              # the leaf row is a repeated row too
    for r in reps:
        assert g.value(r, TAB.onPage).toPython() == 1
        assert str(g.value(r, TAB.cellText))
        assert g.value(r, TAB.hasBBox) is not None
        assert all(str(o).startswith("urn:head-hsc") for o in g.objects(r, PROV.wasDerivedFrom))
    leaf = URIRef("urn:cont-rephdr1")
    assert g.value(g.value(leaf, TAB.hasBBox), TAB.x1).toPython() == 240.0
    assert (URIRef("urn:cont"), TAB.hasRepeatedHeader, leaf) in g
    assert not list(g.subjects(RDF.type, TAB.EntryCell)), "a repeated header is never a data cell"


def test_single_page_document_matches_compile_tables(tmp_path):
    from iladub.etkl import compile_tables
    from tests.etkl.fixtures import simple_table_pdf
    pdf = str(tmp_path / "single.pdf")
    simple_table_pdf(pdf)
    single = compile_tables(pdf)
    doc = compile_document(pdf)
    assert len(doc.pages) == 1
    assert doc.score == single.score
    # EXACT, not >=: page-scoping renames URIs, it must not add or lose a triple (measured 175==175)
    assert len(doc.graph) == len(single.graph)
