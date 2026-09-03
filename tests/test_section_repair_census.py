"""scripts/section_repair_census.py — the R161 instrument's one pure function.

`census()` needs a PDF and a compile, so it is exercised by running the script on the corpus
(the evidence doc pastes its output). `refusing_shapes` is the part that turns a SHACL report
into the "which shape refused" answer, and it is pinned here on a synthetic report so a change
in pySHACL's report vocabulary is caught before it silently empties the census.
"""
import importlib.util
import pathlib

from rdflib import Graph

_SPEC = importlib.util.spec_from_file_location(
    "section_repair_census",
    pathlib.Path(__file__).resolve().parents[1] / "scripts" / "section_repair_census.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

_REPORT = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix tab: <https://w3id.org/iladub/tab#> .
[] a sh:ValidationReport ; sh:conforms false ;
   sh:result [ a sh:ValidationResult ; sh:resultSeverity sh:Violation ;
               sh:sourceShape tab:CoverageShape ; sh:focusNode <urn:x#htable3-c2> ;
               sh:resultMessage "Leaf column is not covered by any header node of its table (coverage gap)." ],
             [ a sh:ValidationResult ; sh:resultSeverity sh:Warning ;
               sh:sourceShape tab:SomeAdvisoryShape ; sh:focusNode <urn:x#htable3-c1> ;
               sh:resultMessage "advisory only" ] .
"""


def test_refusing_shapes_reads_violations_only_from_turtle_and_graph():
    expected = [("CoverageShape",
                 "Leaf column is not covered by any header node of its table (coverage gap).",
                 "htable3-c2")]
    assert _MOD.refusing_shapes(_REPORT) == expected
    assert _MOD.refusing_shapes(Graph().parse(data=_REPORT, format="turtle")) == expected


def test_refusing_shapes_is_empty_on_a_conforming_report():
    assert _MOD.refusing_shapes("@prefix sh: <http://www.w3.org/ns/shacl#> . [] a sh:ValidationReport ; sh:conforms true .") == []
