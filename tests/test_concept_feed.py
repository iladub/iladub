from iladub.ground import SurfaceConcept
from iladub.propose_ground import GroundingProposal, MappingGroundingProposer


def _c(text, value="x"):
    return SurfaceConcept(text, value, "r0")


def test_mapping_proposer_maps_by_header_text():
    prop = GroundingProposal("urn:f-ef", "urn:anchor", 0.9, "ef", "urn:s")
    mp = MappingGroundingProposer({"LVEF": prop})
    assert mp.propose_grounding(_c("LVEF"), ()) is prop


def test_mapping_proposer_unmapped_header_yields_none_field():
    mp = MappingGroundingProposer({})
    out = mp.propose_grounding(_c("Whatever"), ())
    assert out.field_iri is None


# Bridge tests: feed.table_records
import os
import tempfile

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")
from iladub.etkl import compile_tables
from iladub.feed import Record, table_records
from tests.etkl import fixtures as F


def _compiled_offer_graph():
    p = os.path.join(tempfile.mkdtemp(), "offer.pdf")
    F.offer_table_pdf(p)
    return compile_tables(p).graph


def test_table_records_two_records_correct_cells():
    recs = table_records(_compiled_offer_graph())
    assert len(recs) == 2
    by_header = [{c.text: c.value for c in r.concepts} for r in recs]
    # order is row-stable; row1 = Heart, row2 = Liver
    assert by_header[0] == {"Organ": "Heart", "LVEF": "60", "ABO": "O", "COD": "MVA"}
    assert by_header[1] == {"Organ": "Liver", "LVEF": "55", "ABO": "A", "COD": "CVA"}
    assert all(isinstance(r, Record) and len(r.concepts) == 4 for r in recs)


def test_table_records_carry_distinct_provenance():
    recs = table_records(_compiled_offer_graph())
    regions = [c.region for r in recs for c in r.concepts]
    assert all(regions) and len(set(regions)) == len(regions)  # non-empty and distinct per cell


def _hand_authored_table_graph():
    """Two columns x twelve rows, RDF authored directly (no PDF). Row URIs are minted
    …-r1 .. …-r12 (lexicographically wrong past r1: r1,r10,r11,r12,r2,...) but bbox y0
    increases monotonically with the intended row order; column x0 orders c1 < c2 within
    a row. Pins the bbox-geometry sort — must FAIL if table_records ever regresses to
    sorting by str(URIRef) again."""
    from rdflib import BNode, Graph, Literal, RDF, URIRef
    from rdflib.namespace import XSD

    from iladub.feed import TAB

    g = Graph()
    base = "https://w3id.org/iladub/example#t1"
    t = URIRef(base)
    g.add((t, RDF.type, TAB.RecordTable))

    col_uris = {1: URIRef(f"{base}-c1"), 2: URIRef(f"{base}-c2")}

    # Header: c1 -> "A", c2 -> "B".
    for idx, col in col_uris.items():
        h = URIRef(f"{base}-h{idx}")
        lc = BNode()
        g.add((lc, TAB.cellText, Literal("A" if idx == 1 else "B")))
        g.add((h, TAB.hasLabel, lc))
        g.add((h, TAB.coversColumn, col))
        g.add((t, TAB.hasHeaderNode, h))

    def bbox(x0: float, y0: float) -> BNode:
        n = BNode()
        g.add((n, RDF.type, TAB.BBox))
        g.add((n, TAB.x0, Literal(x0, datatype=XSD.decimal)))
        g.add((n, TAB.y0, Literal(y0, datatype=XSD.decimal)))
        return n

    for i in range(1, 13):
        row = URIRef(f"{base}-r{i}")
        y0 = float(i * 10)  # increases with intended row order 1..12
        for idx, col in col_uris.items():
            x0 = float(idx * 10)  # c1 (x0=10) precedes c2 (x0=20) within a row
            e = URIRef(f"{base}-r{i}-c{idx}")
            g.add((e, RDF.type, TAB.EntryCell))
            g.add((t, TAB.hasCell, e))
            g.add((e, TAB.atColumn, col))
            g.add((e, TAB.atRow, row))
            g.add((e, TAB.cellText, Literal(f"row{i}-col{idx}")))
            g.add((e, TAB.hasBBox, bbox(x0, y0)))
    return g


def test_table_records_orders_by_bbox_not_lexicographic_uri():
    recs = table_records(_hand_authored_table_graph())
    assert len(recs) == 12
    # Rows must come out r1..r12 in bbox y0 order, not lexicographic (r1,r10,r11,r12,r2,...).
    assert [r.row_id for r in recs] == [f"t1-r{i}" for i in range(1, 13)]
    # Within each row, cells must come out in x0 order: col1 ("A") before col2 ("B").
    for i, r in enumerate(recs, start=1):
        assert [c.value for c in r.concepts] == [f"row{i}-col1", f"row{i}-col2"]
        assert [c.text for c in r.concepts] == ["A", "B"]


# End-to-end DoD: ground_document (Task 3)
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from iladub.feed import ground_document, FeedResult, table_records
from iladub.ground import load_contract

TX = Namespace("https://example.org/transplant#")
ILA = Namespace("https://w3id.org/iladub#")
CONTRACT = "examples/transplant/offer-contract.ttl"


def _offer_deps():
    c = load_contract(CONTRACT)
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    abo = next(f for f in c.fields if f.fills_property.endswith("aboGroup"))
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    cod = next(f for f in c.fields if f.fills_property.endswith("causeOfDeath"))
    mapping = {
        "ABO": GroundingProposal(abo.iri, str(TX) + "Category", 0.8, "abo", "urn:iladub:suggester/fake"),
        "LVEF": GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9, "ef", "urn:iladub:suggester/fake"),
        "COD": GroundingProposal(cod.iri, str(TX) + "Category", 0.7, "cod", "urn:iladub:suggester/fake"),
    }
    return c, terms, shapes, MappingGroundingProposer(mapping)


def test_offer_table_grounds_end_to_end():
    graph = _compiled_offer_graph()
    c, terms, shapes, proposer = _offer_deps()
    g = Graph()
    res = ground_document(graph, c, proposer, terms, shapes, g)
    assert res == FeedResult(records=2, grounded=6, proposed=2)
    assert len(set(g.subjects(RDF.type, TX.OrganOffer))) == 2        # two record subjects
    assert len(list(g.subjects(RDF.type, ILA.GroundedNode))) == 6    # organ/abo/ef x 2 rows
    assert list(g.objects(None, TX.causeOfDeath)) == []              # COD quarantined, no property


def test_feed_is_load_bearing_red_check(monkeypatch):
    graph = _compiled_offer_graph()
    c, terms, shapes, proposer = _offer_deps()
    monkeypatch.setattr("iladub.feed.table_records", lambda _g: [])
    g = Graph()
    res = ground_document(graph, c, proposer, terms, shapes, g)
    assert res == FeedResult(0, 0, 0)
    assert list(g.subjects(RDF.type, ILA.GroundedNode)) == []


# --- Hierarchical feed ---


def _compiled_hier_graph():
    p = os.path.join(tempfile.mkdtemp(), "hier.pdf")
    F.pivoted_table_pdf(p)
    return compile_tables(p).graph


def test_hierarchical_records_carry_header_paths():
    recs = table_records(_compiled_hier_graph())
    assert len(recs) == 5                                   # five analyte rows
    # every record has the stub + the 6 merged-header data cells
    by_path = {c.text: c.value for r in recs for c in r.concepts}
    assert by_path["Current Visit > Result (SI)"] in {"13.2", "39.5", "7.8", "252", "88.4"}
    assert by_path["Prior Visit > Unit"] in {"g/dL", "%", "x10^9/L", "fL"}
    assert "Analyte" in by_path                              # the stub column path is its single label
    # at least one full root>leaf path is present verbatim
    assert any(c.text == "Current Visit > Result (SI)" for r in recs for c in r.concepts)


def test_column_header_path_flat_is_single_label_hier_is_path():
    from iladub.feed import _column_header_path
    from rdflib import RDF as _RDF
    TAB_NS = Namespace("https://w3id.org/iladub/tab#")
    # flat: offer RecordTable -> each column path is a single label
    fg = _compiled_offer_graph()
    ftab = next(fg.subjects(_RDF.type, TAB_NS.RecordTable))
    assert "Organ" in set(_column_header_path(fg, ftab).values())
    assert all(" > " not in p for p in _column_header_path(fg, ftab).values())
    # hierarchical: at least one column path is a root>leaf path
    hg = _compiled_hier_graph()
    htab = next(hg.subjects(_RDF.type, TAB_NS.HierarchicalTable))
    assert any(" > " in p for p in _column_header_path(hg, htab).values())


def test_recordtable_feed_unchanged_single_label_header():
    # backward compat: an offer record's concept header is a plain label, never a path
    recs = table_records(_compiled_offer_graph())
    headers = {c.text for r in recs for c in r.concepts}
    assert "Organ" in headers and all(" > " not in h for h in headers)


def test_hierarchical_grounds_end_to_end():
    # illustrative wiring: map the numeric "Result" path to the value-constrained EF field. In-range
    # Current-Visit results ground via the value-constraint oracle THROUGH the hierarchical feed;
    # out-of-range ("252") and unmapped paths quarantine. Proves path-concepts flow + the oracle gates.
    c = load_contract(CONTRACT)
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    proposer = MappingGroundingProposer({
        "Current Visit > Result (SI)": GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9,
                                                         "result", "urn:iladub:suggester/fake"),
    })
    g = Graph()
    res = ground_document(_compiled_hier_graph(), c, proposer, terms, shapes, g)
    assert res.records == 5
    assert res.grounded > 0 and res.proposed > 0            # some in-range results ground; rest quarantine
    assert len(list(g.subjects(RDF.type, ILA.GroundedNode))) == res.grounded


# --- Matrix / cross-tab feed ---
from iladub.feed import _row_header_path


def _compiled_crosstab_graph():
    p = os.path.join(tempfile.mkdtemp(), "ct.pdf"); F.crosstab_table_pdf(p)
    return compile_tables(p).graph


def test_crosstab_records_identified_by_row_header_path():
    recs = table_records(_compiled_crosstab_graph())
    assert len(recs) == 2
    assert {r.row_id for r in recs} == {"North", "South"}          # row identity, not opaque ids
    # each record carries column-path concepts (Q1/Q2 > Rev/Cost/Unit)
    paths = {c.text for r in recs for c in r.concepts}
    assert any(" > " in p and p.startswith("Q1") for p in paths)


def test_row_header_path_present_for_crosstab_empty_otherwise():
    from rdflib import RDF as _RDF
    TABNS = Namespace("https://w3id.org/iladub/tab#")
    hg = _compiled_crosstab_graph()
    ht = next(hg.subjects(_RDF.type, TABNS.HierarchicalTable))
    assert set(_row_header_path(hg, ht).values()) == {"North", "South"}
    # a RecordTable and a plain hierarchical (pivoted) table have NO row tree -> {}
    og = _compiled_offer_graph()
    ot = next(og.subjects(_RDF.type, TABNS.RecordTable))
    assert _row_header_path(og, ot) == {}
    pg = _compiled_hier_graph()
    pt = next(pg.subjects(_RDF.type, TABNS.HierarchicalTable))
    assert _row_header_path(pg, pt) == {}


def test_recordtable_row_ids_unchanged_opaque():
    # backward compat: an offer RecordTable's row_id stays the opaque URI fragment, not a header label
    recs = table_records(_compiled_offer_graph())
    assert all("-r" in r.row_id for r in recs)                     # e.g. "table0-r1"


def test_crosstab_grounds_to_named_subjects_end_to_end():
    c = load_contract(CONTRACT)
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    ef = next(f for f in c.fields if f.fills_property.endswith("ejectionFraction"))
    proposer = MappingGroundingProposer({
        "Q1 > Unit": GroundingProposal(ef.iri, str(TX) + "Magnitude", 0.9, "unit", "urn:iladub:suggester/fake"),
    })
    g = Graph()
    res = ground_document(_compiled_crosstab_graph(), c, proposer, terms, shapes, g)
    assert res.records == 2
    assert res.grounded > 0 and res.proposed > 0
    subjects = set(g.subjects(RDF.type, TX.OrganOffer))
    assert URIRef("urn:iladub:record:North") in subjects
    assert URIRef("urn:iladub:record:South") in subjects


# --- Enum/pattern value-constrained columns, end-to-end from a PDF ---
from rdflib import BNode, Literal
from rdflib.collection import Collection
from iladub.ground import SH


def _augment(shapes, prop_iri, add):
    node = next(shapes.subjects(SH.targetClass, TX.OrganOffer))
    ps = BNode(); shapes.add((node, SH.property, ps)); shapes.add((ps, SH.path, URIRef(prop_iri)))
    add(shapes, ps)
    return shapes


def test_pattern_enum_columns_ground_end_to_end():
    # a pattern column (Size) + an enum column (Sero) ground through the raw-doc->grounded-graph feed,
    # via in-memory augmented shapes (M4-safe: offer-shapes.ttl is never modified).
    p = os.path.join(tempfile.mkdtemp(), "pe.pdf"); F.pattern_enum_table_pdf(p)
    graph = compile_tables(p).graph
    c = load_contract(CONTRACT)
    terms = Graph().parse("examples/transplant/transplant-terms.ttl", format="turtle")
    shapes = Graph().parse("examples/transplant/offer-shapes.ttl", format="turtle")
    _augment(shapes, str(TX) + "sizeMetric",
             lambda s, ps: s.add((ps, SH.pattern, Literal("^[0-9]+(kg|cm)$"))))
    def _enum(s, ps):
        lst = BNode(); Collection(s, lst, [Literal("positive"), Literal("negative")])
        s.add((ps, SH["in"], lst))
    _augment(shapes, str(TX) + "serology", _enum)
    size = next(f for f in c.fields if f.fills_property.endswith("sizeMetric"))
    sero = next(f for f in c.fields if f.fills_property.endswith("serology"))
    proposer = MappingGroundingProposer({
        "Size": GroundingProposal(size.iri, str(TX) + "Magnitude", 0.9, "size", "urn:iladub:suggester/fake"),
        "Sero": GroundingProposal(sero.iri, str(TX) + "Category", 0.8, "sero", "urn:iladub:suggester/fake"),
    })
    g = Graph()
    res = ground_document(graph, c, proposer, terms, shapes, g)
    assert res == FeedResult(records=2, grounded=2, proposed=2)
    # row 1 grounded: matching pattern + enum member
    assert Literal("78kg") in set(g.objects(None, TX.sizeMetric))
    assert Literal("negative") in set(g.objects(None, TX.serology))
    # row 2 quarantined: non-matching value / non-member -> no property emitted
    assert Literal("big") not in set(g.objects(None, TX.sizeMetric))
    assert Literal("unknown") not in set(g.objects(None, TX.serology))
