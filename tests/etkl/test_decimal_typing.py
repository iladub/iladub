"""R92 tripwire — no graph handed to a membrane may carry a FLOAT-VALUED xsd:decimal.

THE DEFECT THIS PINS (measured 2026-08-11, residues R92/R93/R94). `Literal(round(x, 2),
datatype=XSD.decimal)` builds a literal whose Python `.value` is a **float** while the literal
claims `xsd:decimal`. pySHACL's datatype check is `isinstance(value, Decimal)`, so it REFUSES;
rudof only ever sees the serialized lexical form (`membrane._validate_rudof` hands it
`serialize(format="nt")`) and ADMITS. **rudof is spec-correct; pySHACL over-refuses.**

WHY IT MATTERS EVEN THOUGH NO SHAPE TYPES A COORDINATE TODAY. The compile membrane's TAB leg
is UNPINNED, so the engine is whatever is installed — and `pyshacl` is a CORE dependency while
`pyrudof` is only an extra, so the *default* install is the refusing side. The day anyone adds
`sh:datatype xsd:decimal` to a coordinate, the corpus splits by install, and
`ILADUB_MEMBRANE=pyshacl` — the documented escape hatch for re-checking a suspect verdict — is
precisely the operation that flips it. Measured on graincorp-stem p0: pySHACL `conforms=False`,
rudof `conforms=True`, on 586 literals.

WHY A SOURCE LINT AND NOT ONLY A RUNTIME TEST. A runtime test only covers the paths it
exercises; the bad form was present at 39 sites across five modules, and the next one would be
written by copying a neighbouring line. The lint closes reintroduction everywhere in `src/`.

Gate classification (CLAUDE.md §8): PROCEDURAL test harness. It makes no domain decision — it
asserts a representation invariant and compares two engines. No tuned constant appears here.
"""
import glob
import os
import re
from decimal import Decimal

import pytest
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SH, XSD

from iladub.etkl import membrane

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STEM = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-stem-2026-07-31.pdf")
COORDS = (TAB.x0, TAB.y0, TAB.x1, TAB.y1)


class _Cell:
    """Minimal stand-in for the cell `_bbox_node` reads — only `.bbox` is touched."""

    def __init__(self, bbox):
        self.bbox = bbox


def _typed_coord_shapes():
    """The constraint the repo cannot currently afford to add — used here to PROVE it now can."""
    g = Graph()
    shape = URIRef("urn:test:TypedCoordShape")
    g.add((shape, RDF.type, SH.NodeShape))
    g.add((shape, SH.targetClass, TAB.BBox))
    for path in COORDS:
        pn = BNode()
        g.add((shape, SH.property, pn))
        g.add((pn, SH.path, path))
        g.add((pn, SH.datatype, XSD.decimal))
    return g


def _float_valued_decimals(graph):
    return [(s, p, o) for s, p, o in graph
            if getattr(o, "datatype", None) == XSD.decimal
            and isinstance(getattr(o, "value", None), float)]


# ---------- the invariant, at the emitter ----------

def test_the_bbox_emitter_mints_decimal_valued_coordinates():
    """`.value` must be a Decimal, not a float. This is the whole defect, at its source."""
    from iladub.etkl.holon import _bbox_node

    g = Graph()
    _bbox_node(g, _Cell((12.345, 67.891, 234.567, 89.012)))
    coords = [o for _, p, o in g if p in COORDS]
    assert len(coords) == 4, f"expected four coordinates, got {len(coords)}"
    for o in coords:
        assert o.datatype == XSD.decimal, f"{o!r} is not typed xsd:decimal"
        assert isinstance(o.value, Decimal), (
            f"{o!r} has a Python {type(o.value).__name__} value — pySHACL reads that as "
            f"ill-typed against sh:datatype xsd:decimal (R92)")


def test_both_engines_admit_a_typed_coordinate_constraint():
    """The property that actually matters: with coordinates typed, the two engines AGREE.

    Before the R92 fix this failed with pySHACL=False, rudof=True."""
    from iladub.etkl.holon import _bbox_node

    g = Graph()
    _bbox_node(g, _Cell((12.345, 67.891, 234.567, 89.012)))
    shapes, ont = _typed_coord_shapes(), Graph()
    p, _ = membrane._validate_pyshacl(g, shapes, ont)
    r, _ = membrane._validate_rudof(g, shapes, ont)
    assert p is True and r is True, f"pySHACL={p} rudof={r} on typed coordinates"


def test_the_differential_is_not_vacuous():
    """Guard: the shape must actually bite, or the test above proves nothing.

    A float-valued literal is the exact form R92 forbids, and the two engines must SPLIT on it.
    THIS TEST FAILING IS GOOD NEWS in one direction — it would mean pySHACL stopped inspecting
    the in-memory value (or rudof started), and R92's hazard is gone."""
    g = Graph()
    n = BNode()
    g.add((n, RDF.type, TAB.BBox))
    g.add((n, TAB.x0, Literal(round(307.474, 2), datatype=XSD.decimal)))   # the forbidden form
    shapes, ont = _typed_coord_shapes(), Graph()
    p, _ = membrane._validate_pyshacl(g, shapes, ont)
    r, _ = membrane._validate_rudof(g, shapes, ont)
    assert p is False, "pySHACL admitted a float-valued xsd:decimal — the constraint is vacuous"
    assert r is True, "rudof refused a well-formed decimal — re-read R92 before changing this"


# ---------- the invariant, on a real compiled page ----------

@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_no_float_valued_decimal_survives_a_real_compile():
    from iladub.etkl import compile_tables

    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    bad = _float_valued_decimals(rep.graph)
    assert not bad, (
        f"{len(bad)} float-valued xsd:decimal literals in a compiled page; first: {bad[0]}")


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_a_real_page_survives_typed_coordinates_under_both_engines():
    """The end of R92: the constraint the register said could not be added, added."""
    from iladub.etkl import compile_tables

    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    shapes, ont = _typed_coord_shapes(), Graph()
    p, _ = membrane._validate_pyshacl(rep.graph, shapes, ont)
    r, _ = membrane._validate_rudof(rep.graph, shapes, ont)
    assert p is True and r is True, f"pySHACL={p} rudof={r} on a real page with typed coordinates"


def test_to_rdf_mints_a_decimal_valued_confidence():
    """R93, and the reason the lint below is NOT sufficient on its own.

    `to_rdf` wrote `Literal(cc.confidence, datatype=XSD.decimal)` — a BARE FLOAT VARIABLE, not
    a `round(...)`/`float(...)` call — so no syntactic pattern can catch it. `iladub:confidence`
    is one of only two `sh:datatype xsd:decimal` constraints in the shipped shapes
    (`iladub-shapes.ttl:25`), so this needs a runtime assertion of its own."""
    from iladub.extract_baml import CodedConcept, OfferExtraction
    from iladub.to_rdf import to_rdf

    ILADUB = Namespace("https://w3id.org/iladub#")
    ext = OfferExtraction(cause_of_death=CodedConcept(
        "takotsubo-pattern abnormality", "transient wall-motion abnormality", 0.4))
    eg = to_rdf(ext, Graph())                      # empty terms => nothing grounds => candidate
    confidences = [o for _, p, o in eg.propositions if p == ILADUB.confidence]
    assert confidences, "no candidate minted — fixture no longer exercises the quarantine path"
    for o in confidences:
        assert isinstance(o.value, Decimal), (
            f"{o!r} carries a Python {type(o.value).__name__} against "
            f"iladub-shapes.ttl:25's sh:datatype xsd:decimal (R93)")


# ---------- reintroduction lint ----------

_BAD_FORM = re.compile(r"Literal\(\s*(round|float)\(.*?datatype\s*=\s*XSD\.decimal")


def test_no_source_file_builds_an_xsd_decimal_from_a_float():
    """The 39 sites are converted; this stops the 40th being written by copying a neighbour.

    The safe form is `Literal(Decimal(str(round(x, n))))` — see `holon.py`'s note."""
    offenders = []
    for path in glob.glob(os.path.join(ROOT, "src", "iladub", "**", "*.py"), recursive=True):
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            if line.lstrip().startswith("#"):        # the cautionary note in holon.py QUOTES it
                continue
            if _BAD_FORM.search(line):
                offenders.append(f"{os.path.relpath(path, ROOT)}:{i}: {line.strip()}")
    assert not offenders, (
        "xsd:decimal built from a Python float (R92) at:\n  " + "\n  ".join(offenders))
