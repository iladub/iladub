"""Release gate (spec §7): a contradiction registered since the previous
release blocks the tag. Query tested on synthetic facts; _since_date on a
throwaway git repo (never the live one — its tag list changes over time)."""
import subprocess
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD

from tests.docgov_extract import DG, doc_iri
from scripts.release_gate import _since_date, blocking_docs

Q = Path(__file__).resolve().parent.parent / "vocab" / "queries" / "docgov-release-gate.rq"


def _spec(g, path, impact, when):
    d = doc_iri(path)
    g.add((d, RDF.type, DG.Document))
    g.add((d, DG.path, Literal(path)))
    g.add((d, DG.docDate, Literal(when, datatype=XSD.date)))
    g.add((d, DG.docImpact, Literal(impact)))
    return d


def test_contradiction_after_since_blocks():
    g = Graph()
    _spec(g, "docs/superpowers/specs/2026-08-02-x-design.md", "contradiction", "2026-08-02")
    assert blocking_docs(g, date(2026, 7, 31)) == [
        "docs/superpowers/specs/2026-08-02-x-design.md"]


def test_increment_and_old_contradiction_do_not_block():
    g = Graph()
    _spec(g, "docs/superpowers/specs/2026-08-02-y-design.md", "increment", "2026-08-02")
    _spec(g, "docs/superpowers/specs/2026-07-20-z-design.md", "contradiction", "2026-07-20")
    assert blocking_docs(g, date(2026, 7, 31)) == []


def _git(cwd, *args, when=None):
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "PATH": "/usr/bin:/bin", "HOME": str(cwd)}
    if when:  # backdate so the two tags carry DIFFERENT creatordates
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


def test_since_date_fallback_and_previous_tag(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / "f").write_text("x")
    _git(tmp_path, "add", "f")
    _git(tmp_path, "commit", "-qm", "one", when="2026-01-01T12:00:00")
    # no v* tags → governance-adoption fallback
    assert _since_date(tmp_path) == date(2026, 7, 31)
    _git(tmp_path, "tag", "v0.0.1")  # lightweight → creatordate = 2026-01-01
    (tmp_path / "f").write_text("y")
    _git(tmp_path, "add", "f")
    _git(tmp_path, "commit", "-qm", "two", when="2026-06-01T12:00:00")
    # HEAD untagged (dev run) → newest tag overall is the previous release
    assert _since_date(tmp_path) == date(2026, 1, 1)
    _git(tmp_path, "tag", "v0.0.2")
    # HEAD tagged (release run) → the HEAD tag (2026-06-01) is excluded;
    # v0.0.1 is the previous release. A broken exclusion would return 2026-06-01.
    assert _since_date(tmp_path) == date(2026, 1, 1)
