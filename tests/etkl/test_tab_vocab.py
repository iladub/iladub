from pathlib import Path
from rdflib import Graph, Namespace, RDF, OWL

TAB = Namespace("https://w3id.org/iladub/tab#")
_TTL = Path(__file__).resolve().parents[2] / "vocab" / "ontology" / "tab.ttl"


def _graph():
    g = Graph()
    g.parse(_TTL, format="turtle")
    return g


def test_classify_evidence_terms_present():
    g = _graph()
    subjects = set(g.subjects())
    for local in ("ClassifyBand", "lineCount", "gridColumnCount", "HeaderWord",
                  "headerWordOrder", "strictlyInColumn", "RegionKind",
                  "RecordTableKind", "UnsupportedTableKind", "NonTableKind"):
        assert TAB[local] in subjects, f"missing tab:{local}"


def test_region_kinds_are_regionkind_individuals():
    g = _graph()
    # assert rdf:type specifically (not any predicate to the object)
    for local in ("RecordTableKind", "UnsupportedTableKind", "NonTableKind"):
        assert (TAB[local], RDF.type, TAB.RegionKind) in g, f"tab:{local} is not typed a tab:RegionKind"


def test_headercell_term_present():
    g = _graph()
    assert (TAB.HeaderCell, RDF.type, OWL.Class) in g
