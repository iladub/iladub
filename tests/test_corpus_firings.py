"""R259 task 2: the lift of firings from the corpus baseline (spec 2026-09-18 § 8, § 8.3).
Always-on: reads only committed files; carries no pytest.mark.corpus."""
import json
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import XSD

from tests.corpus_firings import lift_firings, live_pairs

REPO = Path(__file__).resolve().parent.parent
COR = Namespace("https://w3id.org/iladub/corpus#")

MANIFEST_TTL = """@prefix cor: <https://w3id.org/iladub/corpus#> .
<urn:d:a> a cor:Document ; cor:file "fam/a.pdf" .
<urn:d:b> a cor:Document ; cor:file "fam/b.pdf" .
"""


def _write(d: Path, name: str, pdf: str, regions):
    (d / name).write_text(json.dumps(
        {"pdf": pdf, "pages": [{"regions": [{"reason": r, "verdict": v} for r, v in regions]}]}))


def _setup(tmp_path, a_regions, b_regions=(), extra=True):
    m = Graph().parse(data=MANIFEST_TTL, format="turtle")
    d = tmp_path / "baseline"
    d.mkdir()
    (d / "inputs.json").write_text("{}")
    if a_regions is not None:
        _write(d, "a.json", "corpus/fam/a.pdf", a_regions)
    if b_regions is not None:
        _write(d, "b.json", "corpus/fam/b.pdf", b_regions)
    return m, d


def _firings(g, doc):
    return {str(g.value(f, COR.reason)): (int(g.value(f, COR.live)), int(g.value(f, COR.superseded)))
            for f in g.objects(URIRef(doc), COR.firing)}


def test_join_by_pdf_and_heldout_ignored(tmp_path):
    m, d = _setup(tmp_path, [("DATAGRID_RESIDUE", "escalated")], [])
    _write(d, "h.json", "held-out/zzz.pdf", [("DATAGRID_RESIDUE", "escalated")])
    g = lift_firings(m, d)
    assert _firings(g, "urn:d:a") == {"DATAGRID_RESIDUE": (1, 0)}
    assert len(list(g.subject_objects(COR.firing))) == 1


def test_missing_file_raises(tmp_path):
    m, d = _setup(tmp_path, [("X", "escalated")], None)
    with pytest.raises(ValueError, match="urn:d:b"):
        lift_firings(m, d)


def test_orphan_corpus_file_raises(tmp_path):
    m, d = _setup(tmp_path, [], [])
    _write(d, "c.json", "corpus/fam/c.pdf", [])
    with pytest.raises(ValueError, match="fam/c.pdf"):
        lift_firings(m, d)


def test_free_text_reason_not_lifted(tmp_path):
    m, d = _setup(tmp_path, [("fewer than 2 lines", "escalated"), ("KIND_NOT_SUPPORTED", "escalated")], [])
    assert list(_firings(lift_firings(m, d), "urn:d:a")) == ["KIND_NOT_SUPPORTED"]


def test_live_and_superseded_counts(tmp_path):
    m, d = _setup(tmp_path, [("R_X", "escalated")] * 3 + [("R_X", "superseded")] * 2, [])
    g = lift_firings(m, d)
    assert _firings(g, "urn:d:a") == {"R_X": (3, 2)}
    f = next(g.objects(URIRef("urn:d:a"), COR.firing))
    assert g.value(f, COR.live) == Literal(3, datatype=XSD.nonNegativeInteger)
    assert g.value(f, COR.superseded) == Literal(2, datatype=XSD.nonNegativeInteger)


def test_constant_reason_other_verdict_raises(tmp_path):
    m, d = _setup(tmp_path, [("R_X", "asserted")], [])
    with pytest.raises(ValueError, match="asserted"):
        lift_firings(m, d)


def test_clean_document_has_no_firing(tmp_path):
    m, d = _setup(tmp_path, [("R_X", "escalated")], [("free text", "asserted")])
    g = lift_firings(m, d)
    assert list(g.objects(URIRef("urn:d:b"), COR.firing)) == []


def test_live_pairs_omit_zero_live(tmp_path):
    m, d = _setup(tmp_path, [("R_X", "escalated"), ("R_Y", "superseded")], [])
    assert live_pairs(lift_firings(m, d)) == [("urn:d:a", "R_X")]


def test_recorded_in_is_repo_relative(tmp_path):
    """In the repo, each firing records the repo-relative path of the very file it was lifted
    from — not merely a path of the right shape — and that file holds the firing's reason."""
    g = lift_firings(Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle"),
                     REPO / "tests" / "corpus-baseline")
    recorded = {(str(g.value(f, COR.reason)), str(g.value(f, COR.recordedIn)))
                for f in g.subjects(None, COR.Firing)}
    assert recorded
    for reason, rel in recorded:
        assert rel.startswith("tests/corpus-baseline/") and rel.endswith(".json"), rel
        read = REPO / rel
        assert read.is_file(), rel
        regions = [r for pg in json.loads(read.read_text())["pages"] for r in pg["regions"]]
        assert any(r.get("reason") == reason for r in regions), (reason, rel)


def test_recorded_in_out_of_repo_is_the_path_read(tmp_path):
    """Out of the repo nothing is invented: the firing records the absolute path actually read."""
    m, d = _setup(tmp_path, [("R_X", "escalated")], [])
    g = lift_firings(m, d)
    assert {str(o) for o in g.objects(None, COR.recordedIn)} == {(d / "a.json").resolve().as_posix()}


def test_duplicate_file_across_documents_raises(tmp_path):
    """Two manifest documents claiming one cor:file would silently drop one (it would read as
    firing nowhere); the lift refuses instead, naming both IRIs."""
    m, d = _setup(tmp_path, [("R_X", "escalated")], [])
    m.parse(data='@prefix cor: <https://w3id.org/iladub/corpus#> .\n'
                 '<urn:d:z> a cor:Document ; cor:file "fam/a.pdf" .', format="turtle")
    with pytest.raises(ValueError, match=r"urn:d:a.*urn:d:z"):
        lift_firings(m, d)


def test_real_lift_conforms_to_firing_shape():
    manifest = Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle")
    lifted = lift_firings(manifest, REPO / "tests" / "corpus-baseline")
    data = manifest + lifted
    ok, _, report = validate(data, shacl_graph=Graph().parse(REPO / "tests" / "corpus-shapes.ttl",
                             format="turtle"), inference="rdfs", advanced=True)
    assert ok, report
