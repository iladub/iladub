"""The corpus register's membrane (spec 2026-08-02 §4): the tracked manifest conforms
to tests/corpus-shapes.ttl. Always-on — the register is tracked; no network, no corpus/.
Closed-world constraint side of the §8 split: the membrane validates what may enter the
battery; it derives nothing."""
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tests" / "corpus-manifest.ttl"
SHAPES = REPO / "tests" / "corpus-shapes.ttl"

PREFIXES = """@prefix cor: <https://w3id.org/iladub/corpus#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

BASE = ('<urn:x> a cor:Document ; cor:file "f.pdf" ; cor:url "https://example.org/f" ; '
        'cor:series "s" ')


def _conforms(data: Graph):
    ok, _, report = validate(
        data, shacl_graph=Graph().parse(SHAPES, format="turtle"),
        inference="rdfs", advanced=True)
    return ok, report


def _neg(ttl: str):
    ok, report = _conforms(Graph().parse(data=PREFIXES + ttl, format="turtle"))
    assert not ok, f"membrane failed to refuse:\n{ttl}"


def test_manifest_conforms():
    ok, report = _conforms(Graph().parse(MANIFEST, format="turtle"))
    assert ok, report


def test_refuses_compilesabove_without_floor():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:CompilesAbove ; '
         'cor:sha256 "%s" ; cor:adjudication [ cor:by "x" ] .' % ("0" * 64))


def test_refuses_unknown_family():
    _neg(BASE + '; cor:family "crypto" ; cor:expectedVerdict cor:Unadjudicated .')


def test_refuses_adjudicated_verdict_without_pin():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:SemanticEscalation ; '
         'cor:ambiguity "which header row" ; cor:adjudication [ cor:by "x" ] .')


def test_refuses_escalation_without_named_ambiguity():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:SemanticEscalation ; '
         'cor:sha256 "%s" ; cor:adjudication [ cor:by "x" ] .' % ("0" * 64))


def test_refuses_partial_contract_triple():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
         'cor:contract "examples/x.ttl" .')


def test_refuses_malformed_sha256():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
         'cor:sha256 "not-a-hash" .')


# A reading is the register's machine-readable measurement (vocab/internal/corpus.ttl
# § Readings). These three refusals are what make a row traceable rather than merely
# present: an undated value is not evidence of anything, and a value with neither a
# commit nor a path is a number nobody can check.

READING = ('<urn:x> a cor:Document ; cor:file "f.pdf" ; cor:url "https://example.org/f" ; '
           'cor:series "s" ; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
           'cor:reading [ a cor:Reading ; %s ] .')


def test_refuses_reading_without_a_date():
    _neg(READING % ('cor:value "0.5"^^xsd:decimal ; cor:recordedIn "docs/x.md"'))


def test_refuses_reading_without_a_value():
    _neg(READING % ('cor:readAt "2026-09-08"^^xsd:date ; cor:recordedIn "docs/x.md"'))


def test_refuses_untraceable_reading():
    """No commit and no path: the value cannot be checked, only believed."""
    _neg(READING % ('cor:value "0.5"^^xsd:decimal ; cor:readAt "2026-09-08"^^xsd:date'))
