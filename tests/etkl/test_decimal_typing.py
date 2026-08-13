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


def test_the_split_moved_from_the_membrane_to_the_transport():
    """Guard: the shape must actually bite, or the test above proves nothing.

    SUPERSEDES `test_the_differential_is_not_vacuous` (spec 2026-08-13-membrane-parity-design.md,
    Task 1). Before parity, `_validate_pyshacl` validated `subclass_closure`'s LIVE in-memory
    Graph directly, so it saw the float-valued literal's Python `.value` and refused; `_validate_rudof`
    only ever saw a serialized N-Triples string, whose lexical form rudof admits. That was a real
    engine split — but for the wrong reason: the two legs were handed two DIFFERENT artifacts, so
    the split could always have been an artifact difference wearing an engine's name.

    Parity (`membrane._payload`) removes that confound BY CONSTRUCTION: both legs now consume the
    SAME re-parsed N-Triples document, and rdflib's own parser repairs the float `307.47` back
    into a `Decimal` on the way back in — so pySHACL now judges the SAME repaired bytes rudof has
    always judged, and admits them. The split has not disappeared, it MOVED: from the membrane
    (which engine you ask) to the transport (whether you serialize-and-reparse before asking).
    `test_the_transport_does_not_canonicalise_lexical_forms`
    (tests/etkl/test_membrane_equiv.py) is where the split still lives and is pinned.

    THIS TEST FAILING IS GOOD NEWS in one direction — it would mean pySHACL stopped inspecting
    the in-memory float (`p_live is False` failing), or that `_payload` stopped repairing the
    round-tripped lexical form (`p_payload is True` failing) — either way, R92's hazard would be
    gone or `_payload` would no longer be doing what parity requires of it. The `r is True`
    assertion is the ORIGINAL vacuity guard for rudof's half, carried over unchanged: rudof
    judges `"307.47"` (a valid decimal lexical form) as-written and always admitted it, before
    and after parity — dropping this assertion would let rudof stop enforcing `sh:datatype`
    altogether without anything in the repo noticing.

    THE GUARD SEAM (Task 2, spec §4.2). Once `audit_literals` is wired into `_payload`, the
    forbidden literal this test deliberately builds makes `_payload` RAISE — and `_validate_pyshacl`
    / `_validate_rudof` call `_payload` internally with no way to turn the guard off (that
    parameter is deliberately NOT added to those two production leg functions — an entry point
    that can disarm the membrane is a hazard, not a convenience;
    `test_the_production_legs_refuse_the_forbidden_form` below asserts that refusal directly).
    So this test reaches `_payload` with the guard off (`audit=False`, fenced to exactly this
    test and one other by `test_the_audit_escape_hatch_is_not_used_in_production`) and then
    drives each engine on that pre-built artifact through the SAME seams the (guarded) leg
    functions use internally — `pyshacl.validate` for the pySHACL half, `membrane._rudof_on_payload`
    for the rudof half. Neither is a new production surface, and `_rudof_on_payload` is the
    literal body of `_validate_rudof` minus its payload construction, so this test cannot drift
    out of step with how the repo actually drives rudof.

    Converting the literal is NOT an option: the forbidden form IS this test's subject."""
    from pyshacl import validate as _v

    g = Graph()
    n = BNode()
    g.add((n, RDF.type, TAB.BBox))
    g.add((n, TAB.x0, Literal(round(307.474, 2), datatype=XSD.decimal)))   # the forbidden form
    shapes, ont = _typed_coord_shapes(), Graph()

    live = membrane.subclass_closure(g, ont)
    p_live, _, _ = _v(live, shacl_graph=shapes, inference="none", advanced=True)
    assert p_live is False, (
        "pySHACL admitted a float-valued xsd:decimal on the LIVE (un-transported) graph — the "
        "constraint is vacuous")

    graph_payload, nt_payload = membrane._payload(g, ont, audit=False)
    p_payload, _, _ = _v(graph_payload, shacl_graph=shapes, inference="none", advanced=True)
    assert p_payload is True, (
        "pySHACL refused the SAME source triples once handed _payload's re-parsed document — "
        "parity should have repaired the lexical form via rdflib's own parser, moving the split "
        "to the transport")

    r, _ = membrane._rudof_on_payload(nt_payload, shapes)
    assert r is True, "rudof refused a well-formed decimal — re-read R92 before changing this"


def test_the_production_legs_refuse_the_forbidden_form():
    """The membrane's ANSWER to R92 is now refusal, not divergence.

    The test above pins what the bare TRANSPORT does to the forbidden literal, with the guard
    deliberately off. This one pins what PRODUCTION does with the guard on: neither leg has an
    `audit` parameter, both build their payload through `_payload`, and so both refuse outright
    rather than returning a verdict that depends on which engine is installed. That is a
    strictly stronger property than the old accidental split, and it is the one a caller gets."""
    g = Graph()
    n = BNode()
    g.add((n, RDF.type, TAB.BBox))
    g.add((n, TAB.x0, Literal(round(307.474, 2), datatype=XSD.decimal)))   # the forbidden form
    shapes, ont = _typed_coord_shapes(), Graph()

    with pytest.raises(ValueError, match="xsd:decimal"):
        membrane._validate_pyshacl(g, shapes, ont)
    with pytest.raises(ValueError, match="xsd:decimal"):
        membrane._validate_rudof(g, shapes, ont)


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


# ---------- the guard: audit_literals (spec 2026-08-13-membrane-parity-design.md §4.2) --------


def test_the_guard_refuses_a_float_valued_decimal():
    """R92's class. `Literal(round(x, 2), datatype=XSD.decimal)` keeps a Python float as
    .value while the lexical form is a valid xsd:decimal — pySHACL's datatype check is
    isinstance(value, Decimal), so it refuses; rudof only ever sees the lexical form and
    admits. Byte-parity hides this from the membrane, so the guard must catch it instead."""
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(round(307.474, 2), datatype=XSD.decimal)))
    with pytest.raises(ValueError, match="xsd:decimal"):
        membrane.audit_literals(g)


def test_the_membrane_itself_refuses_the_forbidden_form():
    """The guard must be WIRED, not merely present. This is the assertion that fails if
    _payload stops calling audit_literals — the direct-call test above would not notice."""
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(round(307.474, 2), datatype=XSD.decimal)))
    with pytest.raises(ValueError, match="xsd:decimal"):
        membrane._payload(g, Graph())


def test_the_guard_refuses_a_non_canonical_lexical_form():
    """The 5e-05 class. Exponential notation is outside xsd:decimal's lexical space, so
    rudof refuses it while rdflib's parser silently rewrites it to 0.00005 for pySHACL."""
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(float(5e-05), datatype=XSD.decimal)))
    with pytest.raises(ValueError, match="lexical"):
        membrane.audit_literals(g)


def test_the_guard_admits_a_well_formed_decimal():
    """The converted emitter form must pass untouched — the guard is not a repair."""
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(Decimal(str(round(307.474, 2))))))
    membrane.audit_literals(g)          # must not raise


def test_the_audit_escape_hatch_is_not_used_in_production():
    """`audit=False` disables the guard. It exists for the two falsification tests and
    nothing else; a src/ call site passing it would silently disarm the membrane."""
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[2] / "src"
    offenders = [p for p in src.rglob("*.py") if "audit=False" in p.read_text()]
    assert offenders == [], f"audit=False must never appear under src/: {offenders}"
