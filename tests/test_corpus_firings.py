"""R259 task 2: the lift of firings from the corpus baseline (spec 2026-09-18 § 8, § 8.3).
Always-on: reads only committed files; carries no pytest.mark.corpus."""
import json
import subprocess
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import XSD

from tests.corpus_firings import lift_firings, lift_snapshots, live_pairs

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
    data = manifest + lifted + lift_snapshots(manifest)
    ok, _, report = validate(data, shacl_graph=Graph().parse(REPO / "tests" / "corpus-shapes.ttl",
                             format="turtle"), inference="rdfs", advanced=True)
    assert ok, report


# --- tab:07 task 1: lift_snapshots (spec 2026-10-19 § 4.3). Helpers are module-level for Task 2.
_DOC = "urn:d:a"
_PATH = "tests/corpus-baseline/a.json"


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def _baseline(regions):
    return json.dumps({"pdf": "corpus/fam/a.pdf", "pages": [{"regions": [
        {"reason": r, "verdict": v} for r, v in regions]}]})


def _commit(repo, regions, msg):
    p = repo / _PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_baseline(regions))
    _git(repo, "add", _PATH)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", f"HEAD:{_PATH}")


def _repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    return tmp_path


def _publish(repo):
    _git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")


def _manifest(blob, path=_PATH):
    return Graph().parse(data=f"""@prefix cor: <https://w3id.org/iladub/corpus#> .
        <{_DOC}> a cor:Document ; cor:file "fam/a.pdf" ;
            cor:adjudication [ cor:disposes "R_X" ;
                cor:judgedAgainst [ a cor:Snapshot ; cor:recordedIn "{path}" ;
                                    cor:blob "{blob}" ] ] .""", format="turtle")


def _durable_of(g):
    # rdflib's Graph.value(None, p) returns None when subject AND object are both None, so the
    # brief's `.value(None, COR.durable)` cannot pass; read the single object instead.
    (o,) = list(g.objects(None, COR.durable))
    return o


def _snap(g):
    return next(g.subjects(COR.snapshotOf, URIRef(_DOC)))


def test_snapshot_lifts_the_firings_of_its_own_blob(tmp_path):
    repo = _repo(tmp_path)
    old = _commit(repo, [("R_X", "escalated"), ("R_X", "escalated"), ("R_Y", "superseded")], "1")
    _commit(repo, [], "2")                     # the current baseline no longer fires R_X
    _publish(repo)
    g = lift_snapshots(_manifest(old), repo=repo)
    s = _snap(g)
    by_reason = {str(g.value(f, COR.reason)): f for f in g.objects(s, COR.firing)}
    assert sorted(by_reason) == ["R_X", "R_Y"]
    assert int(g.value(by_reason["R_X"], COR.live)) == 2
    assert int(g.value(by_reason["R_Y"], COR.superseded)) == 1
    assert {str(o) for o in g.objects(by_reason["R_X"], COR.recordedIn)} == {f"{_PATH}@{old}"}
    assert g.value(s, COR.durable) == Literal(True)        # historical, on origin/main


def test_intermediate_branch_blob_is_not_durable(tmp_path):
    repo = _repo(tmp_path)
    _commit(repo, [("R_X", "escalated")], "base")
    _publish(repo)
    _git(repo, "checkout", "-q", "-b", "feat")
    mid = _commit(repo, [("R_X", "escalated"), ("R_X", "escalated")], "mid")
    head = _commit(repo, [("R_X", "escalated")] * 3, "head")
    assert _durable_of(lift_snapshots(_manifest(mid), repo=repo)) == Literal(False)
    assert _durable_of(lift_snapshots(_manifest(head), repo=repo)) == Literal(True)


def test_unresolvable_blob_raises(tmp_path):
    repo = _repo(tmp_path)
    _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    with pytest.raises(ValueError, match="cat-file -p 0{40} failed"):
        lift_snapshots(_manifest("0" * 40), repo=repo)


def test_snapshot_of_an_unknown_pdf_raises(tmp_path):
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    m = _manifest(blob)
    m.remove((URIRef(_DOC), COR.file, None))
    m.add((URIRef(_DOC), COR.file, Literal("fam/other.pdf")))
    with pytest.raises(ValueError, match="corpus/fam/a.pdf"):
        lift_snapshots(m, repo=repo)


def test_snapshot_without_origin_main_raises(tmp_path):           # Review Focus 1
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _commit(repo, [], "2")                                         # blob is not HEAD's
    with pytest.raises(Exception, match="origin/main"):
        lift_snapshots(_manifest(blob), repo=repo)


def test_durability_cache_does_not_cross_repos(tmp_path):          # Review Focus 2
    (tmp_path / "a").mkdir(); (tmp_path / "b").mkdir()
    a, b = _repo(tmp_path / "a"), _repo(tmp_path / "b")
    x = _commit(a, [("R_X", "escalated")], "1"); _commit(a, [], "2"); _publish(a)
    _commit(b, [], "1"); _publish(b)
    # the same bytes stored in b as a loose object: resolvable there, on no commit of b's main
    loose = tmp_path / "x.json"
    loose.write_text(_baseline([("R_X", "escalated")]))
    assert _git(b, "hash-object", "-w", str(loose)) == x
    assert _durable_of(lift_snapshots(_manifest(x), repo=a)) == Literal(True)
    assert _durable_of(lift_snapshots(_manifest(x), repo=b)) == Literal(False)


def test_no_snapshots_needs_no_git(tmp_path):                      # Review Focus 3
    m = Graph().parse(data='@prefix cor: <https://w3id.org/iladub/corpus#> .\n'
                           '<urn:d:a> a cor:Document ; cor:file "fam/a.pdf" .', format="turtle")
    assert len(lift_snapshots(m, repo=tmp_path / "not-a-repo")) == 0


def test_live_pairs_ignores_snapshot_subjects(tmp_path):
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    assert live_pairs(lift_snapshots(_manifest(blob), repo=repo)) == []


def test_deletion_commit_contributes_no_post_image(tmp_path):
    from tests.corpus_firings import _main_blobs
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _git(repo, "rm", "-q", _PATH)
    _git(repo, "commit", "-q", "-m", "delete")                    # post-image is 000...0
    sha = _git(repo, "rev-parse", "HEAD")
    got = _main_blobs(str(repo.resolve()), sha, _PATH)
    assert got == frozenset({blob})                               # not the zero sha


def _snap_node(m):
    return next(m.objects(None, COR.judgedAgainst))


def test_snapshot_without_a_blob_raises(tmp_path):
    repo = _repo(tmp_path)
    m = _manifest(_commit(repo, [("R_X", "escalated")], "1"))
    _publish(repo)
    m.remove((_snap_node(m), COR.blob, None))
    with pytest.raises(ValueError, match="exactly one cor:blob.*got 0 and 1"):
        lift_snapshots(m, repo=repo)


def test_snapshot_with_two_blobs_raises(tmp_path):
    repo = _repo(tmp_path)
    blob = _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    m = _manifest(blob)
    m.add((_snap_node(m), COR.blob, Literal("1" * 40)))
    with pytest.raises(ValueError, match="exactly one cor:blob.*got 2 and 1"):
        lift_snapshots(m, repo=repo)


def test_snapshot_without_recorded_in_raises(tmp_path):
    repo = _repo(tmp_path)
    m = _manifest(_commit(repo, [("R_X", "escalated")], "1"))
    _publish(repo)
    m.remove((_snap_node(m), COR.recordedIn, None))
    with pytest.raises(ValueError, match="exactly one cor:blob.*got 1 and 0"):
        lift_snapshots(m, repo=repo)


def test_snapshot_blob_that_is_not_a_json_object_raises(tmp_path):
    repo = _repo(tmp_path)
    _commit(repo, [("R_X", "escalated")], "1")
    _publish(repo)
    (repo / "list.json").write_text("[1, 2]")
    blob = _git(repo, "hash-object", "-w", "list.json").strip()
    with pytest.raises(ValueError, match="not a JSON object"):
        lift_snapshots(_manifest(blob), repo=repo)
