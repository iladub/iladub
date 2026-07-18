from pathlib import Path
from rdflib import Graph, Namespace

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
                  "RecordTable", "UnsupportedTable", "NonTable"):
        assert TAB[local] in subjects, f"missing tab:{local}"


def test_region_kinds_are_regionkind_individuals():
    g = _graph()
    for local in ("RecordTable", "UnsupportedTable", "NonTable"):
        assert (TAB[local], None, TAB.RegionKind) in ((s, None, o) for s, p, o in g.triples((TAB[local], None, None))), \
            f"tab:{local} is not a tab:RegionKind"
