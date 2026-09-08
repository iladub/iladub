"""R61 — a published rdfs:domain/rdfs:range is a claim, and the emitter must honour it.

`vocab/ontology/tab.ttl` ships under CC-BY. A consumer running a stock RDFS reasoner over our
published graph derives every domain/range axiom in it, so an emitter that hangs a property on a
node the axiom types differently makes a FALSE ASSERTION in a published graph (CLAUDE.md § Core
design principles 7). That the membrane happens not to materialise domain/range typing is a local
choice about one validator; it binds nobody downstream. R182 § 2.3 is the case that established
this, and `scripts/measure_dec_membrane.py:18` is the docstring that names the consumer.

R61 sat open for a month because closing it needed one modelling decision — *is the ontology wrong
about these properties, or is the emitter?* — that the row declined to take. The seven rulings are
in `docs/superpowers/specs/2026-09-08-the-axiom-binds-the-emitter-design.md` § 3.

THE GATE (this module's reason to exist). R61's stated closure condition is a corpus-wide probe
WIRED AS A GATE; the row records that it could not be wired while `scripts/probe_domain_range_agreement.py`
exits 1, and that because nothing ran it, the live count moved 14 -> 32 unnoticed when R179 shipped
a shape on 2026-09-07. `test_the_gate_*` below runs the probe's own classifier over a graph built
by the real emitters and fails on any DISAGREE or UNTYPED. It is deliberately built from synthetic
`Line`/`Word` objects rather than a corpus PDF: the corpus is gitignored, and a gate that skips in
CI is the R173 trap — a green check that is no evidence at all.
"""
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

from iladub.etkl.datagrid import DataGrid, GridColumn, emit_data_grid
from iladub.etkl.geometry import Line, Word

TAB = "https://w3id.org/iladub/tab#"


def _t(name):
    return URIRef(TAB + name)


# --------------------------------------------------------------------------- a synthetic grid

def _synthetic_grid():
    """Two columns x two rows, one Text and one Quantity — enough to exercise every ruled
    emission: the grid (onPage, universeSource), its columns (colX0/colX1, columnFamily,
    MeasureColumn) and its entries (atColumn, onPage, hasBBox)."""
    def line(top, cells):
        ws = tuple(Word(txt, x0, x0 + 30.0, top, top + 10.0) for txt, x0 in cells)
        return Line(ws, top, top + 10.0)

    lines = [line(100.0, [("Alpha", 50.0), ("1.5", 200.0)]),
             line(120.0, [("Beta", 50.0), ("2.5", 200.0)])]
    grid = DataGrid(
        rows=(0, 1),
        columns=(GridColumn(45.0, 100.0, "Text"), GridColumn(195.0, 250.0, "Quantity")),
        universe="alignment",
        conforms=("ColumnHomogeneity", "RowAddressability"),
    )
    return grid, lines


def _emitted():
    g = Graph()
    grid, lines = _synthetic_grid()
    uri = emit_data_grid(g, grid, lines, URIRef("urn:test:r61"), 0)
    return g, uri


# --------------------------------------------------------------------------- the seven rulings

@pytest.mark.parametrize("subject,prop,expected", [
    # 1 — hasLabel ranges over Cell: rowgroups.py:93 points it at a SOURCE EntryCell.
    ("hasLabel", "range", "Cell"),
    # 3 — atColumn ranges over the new abstract supertype, NOT LeafColumn: a GridColumn is
    #     hasGridColumn of a grid and could never satisfy the LeafColumn shapes.
    ("atColumn", "range", "Column"),
    # 4 — onPage is domained on the new abstract supertype: a DataGrid is page-located.
    ("onPage", "domain", "PageLocated"),
    # 2 — the column geometry properties are domained on GridColumn, not BBox.
    ("colX0", "domain", "GridColumn"),
    ("colX1", "domain", "GridColumn"),
])
def test_ontology_declares_the_ruled_axiom(subject, prop, expected):
    from rdflib.namespace import RDFS
    ont = Graph().parse("vocab/ontology/tab.ttl", format="turtle")
    pred = RDFS.domain if prop == "domain" else RDFS.range
    assert (_t(subject), pred, _t(expected)) in ont, f"tab:{subject} lost its R61 {prop}"


def test_grid_column_is_not_declared_a_leaf_column():
    """The ruling that measuring reversed. tab:GridColumn's own comment calls it 'a transient
    leaf column', which invites the subclass edge — but tab-shapes.ttl targets tab:LeafColumn
    with shapes requiring `?tbl tab:hasLeafColumn $this`, which a grid column never satisfies.
    The abstract supertype asserts what is true; the subclass edge would assert what is not."""
    from rdflib.namespace import RDFS
    ont = Graph().parse("vocab/ontology/tab.ttl", format="turtle")
    assert (_t("GridColumn"), RDFS.subClassOf, _t("Column")) in ont
    assert (_t("GridColumn"), RDFS.subClassOf, _t("LeafColumn")) not in ont


def test_text_is_declared_both_a_datatype_and_its_own_family():
    """tab-datagrid.ttl already asserted this in prose — 'tab:Text IS a legal family' — while
    only tab:Quantity carried the declaration. tab:columnFamily ranges over the family."""
    ont = Graph().parse("vocab/ontology/tab.ttl", format="turtle")
    assert (_t("Text"), RDF.type, _t("CellDatatype")) in ont
    assert (_t("Text"), RDF.type, _t("CellDatatypeFamily")) in ont


def test_universe_source_is_not_transposed():
    """It was declared rdfs:domain tab:ColumnUniverse with no range, while the emitter writes
    grid -> universe. Every emitting grid was therefore derived a tab:ColumnUniverse."""
    from rdflib.namespace import RDFS
    ont = Graph().parse("vocab/ontology/tab-datagrid.ttl", format="turtle")
    assert (_t("universeSource"), RDFS.domain, _t("DataGrid")) in ont
    assert (_t("universeSource"), RDFS.range, _t("ColumnUniverse")) in ont
    assert (_t("universeSource"), RDFS.domain, _t("ColumnUniverse")) not in ont


# --------------------------------------------------------------------------- the emitter

def test_grid_column_carries_an_interval_not_a_box():
    """R182's remedy, applied to R92's site. A column has an x-interval and no y extent: it
    could not satisfy a box shape, so carrying tab:x0 (rdfs:domain tab:BBox) made every grid
    column a tab:BBox for any consumer of our published axioms."""
    g, uri = _emitted()
    cols = list(g.objects(uri, _t("hasGridColumn")))
    assert cols, "the synthetic grid emitted no columns"
    for c in cols:
        assert list(g.objects(c, _t("colX0"))), f"{c} lost its colX0"
        assert list(g.objects(c, _t("colX1"))), f"{c} lost its colX1"
        assert not list(g.objects(c, _t("x0"))), f"{c} still carries tab:x0 (domain tab:BBox)"
        assert not list(g.objects(c, _t("x1"))), f"{c} still carries tab:x1 (domain tab:BBox)"


def test_entry_cell_bboxes_are_untouched_by_the_column_ruling():
    """The falsifier for the edit's blast radius: datagrid.py emits tab:x0 twice, once on the
    column (ruled) and once on the entry cell's real bbox (correct, and must stay)."""
    g, uri = _emitted()
    entries = list(g.objects(uri, _t("hasDataCell")))
    assert entries, "the synthetic grid emitted no entries"
    boxed = [e for e in entries if list(g.objects(e, _t("hasBBox")))]
    assert len(boxed) == len(entries), "an entry lost its bbox"
    for e in boxed:
        bb = next(g.objects(e, _t("hasBBox")))
        assert (bb, RDF.type, _t("BBox")) in g
        assert list(g.objects(bb, _t("x0"))), "the entry bbox lost tab:x0"


# --------------------------------------------------------------------------- the R179 carve-out

def test_the_label_carve_out_is_lossless_by_domination():
    """R61's row asks for the R179 carve-out to be pinned as load-bearing. It cannot be, and the
    reason is the finding: it is not load-bearing — it is LOSSLESS BY DOMINATION, which is what
    the shape's comment always claimed ("provably lossless") and what nobody had measured.

    MEASURED here: a both-typed cell with cellText and no geometry is refused, and the ONLY shape
    that refuses it is tab:EntryCellPhysicalShape — which requires cellText + onPage + hasBBox of
    every entry unconditionally, strictly more than the label shape asks. So exempting such a cell
    from tab:LabelCellPhysicalShape cannot hide a defect: the entry shape has already caught it.

    This is what the attempted falsification returned. Deleting the carve-out and asserting a
    refusal FAILS, because the entry shape refuses either way — a test asserting that would have
    pinned the entry shape while claiming to pin the carve-out."""
    from pyshacl import validate

    shapes = Graph().parse("vocab/shapes/tab-physical-shapes.ttl", format="turtle")

    def refusers(g):
        ok, _, txt = validate(g, shacl_graph=shapes, advanced=True, inference="none")
        import re as _re
        return ok, set(_re.findall(r'sh:name\s+Literal\("([^"]+)"', txt))

    data = Graph()
    n = URIRef("urn:test:both-typed")
    data.add((n, RDF.type, _t("LabelCell")))
    data.add((n, RDF.type, _t("EntryCell")))
    data.add((n, _t("cellText"), Literal("carries text, carries no box")))

    ok, names = refusers(data)
    assert not ok, "a boxless cell was admitted by the physical membrane"
    assert names == {"EntryCellPhysicalShape"}, (
        f"the carve-out is not lossless after all — refused by {names}, expected the entry "
        "shape alone. If LabelCellPhysicalShape appears here the exemption stopped applying.")

    bb = URIRef("urn:test:both-typed-bbox")
    data.add((bb, RDF.type, _t("BBox")))
    data.add((n, _t("hasBBox"), bb))
    data.add((n, _t("onPage"), Literal(0)))
    ok, names = refusers(data)
    assert ok, f"a geometry-complete both-typed cell was refused by {names}"


# --------------------------------------------------------------------------- THE GATE

def test_the_gate_no_domain_range_disagreement_on_an_emitted_graph():
    """R61's closure condition, runnable in CI.

    Runs `scripts/probe_domain_range_agreement.py`'s own classifier — the same code the corpus
    run uses — over a graph produced by the real emitters. DISAGREE means a node carries a
    property whose published domain/range types it as something it is not. UNTYPED means the
    node carries no type at all. Neither may ever be non-zero again without a test going red."""
    import importlib.util
    import os

    root = os.path.join(os.path.dirname(__file__), "..", "..")
    spec = importlib.util.spec_from_file_location(
        "probe_dra", os.path.join(root, "scripts", "probe_domain_range_agreement.py"))
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)

    vocab = os.path.join(root, "vocab")
    ont, _ = probe.rules_by_file(vocab)
    domains, ranges = probe.typing_rules(ont)
    sup = probe._closure(ont)
    membrane, wider = probe.lookup_graphs(vocab)

    g, _uri = _emitted()
    findings = [(k, cls, node, f)
                for k, cls, node, f in probe.classified(g, domains, ranges, sup, membrane, wider)
                if f in (probe.DISAGREE, probe.UNTYPED)]
    assert not findings, "\n".join(f"{f}: {k} on {node}" for k, cls, node, f in findings)
