"""Release gate (spec §7, and 2026-09-08-the-drain-is-a-release-act-design.md):
a contradiction registered since the previous release blocks the tag UNTIL a
docgov:ContradictionDrain is recorded for it. Query tested on synthetic facts;
_since_date on a throwaway git repo (never the live one — its tag list changes
over time); the live register gets its own pin, because a gate that passes
because the query broke is indistinguishable from one that passes because the
drain was recorded (spec §5, O2)."""
import subprocess
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

from tests.docgov_extract import DG, doc_iri, extract
from scripts.release_gate import _since_date, blocking_docs

REPO = Path(__file__).resolve().parent.parent

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


def _drain(g, doc, when="2026-08-02", by="t", evidence="page X fixed in abc1234"):
    d = URIRef("https://w3id.org/iladub/docgov/drain/t")
    g.add((d, RDF.type, DG.ContradictionDrain))
    g.add((d, DG.drains, doc))
    g.add((d, DG.drainedOn, Literal(when, datatype=XSD.date)))
    g.add((d, DG.drainedBy, Literal(by)))
    g.add((d, DG.drainEvidence, Literal(evidence)))
    return d


def test_a_drained_contradiction_does_not_block():
    """The whole point of the register: same facts as
    test_contradiction_after_since_blocks, plus a drain."""
    g = Graph()
    doc = _spec(g, "docs/superpowers/specs/2026-08-02-x-design.md",
                "contradiction", "2026-08-02")
    _drain(g, doc)
    assert blocking_docs(g, date(2026, 7, 31)) == []


def test_a_drain_of_a_DIFFERENT_doc_does_not_unblock_this_one():
    """dg:drains is per-document: one drain must not clear the whole gate."""
    g = Graph()
    _spec(g, "docs/superpowers/specs/2026-08-02-x-design.md", "contradiction", "2026-08-02")
    other = _spec(g, "docs/superpowers/specs/2026-08-03-y-design.md",
                  "contradiction", "2026-08-03")
    _drain(g, other)
    assert blocking_docs(g, date(2026, 7, 31)) == [
        "docs/superpowers/specs/2026-08-02-x-design.md"]


def test_live_repo_gate_is_clear_and_it_is_the_REGISTER_that_clears_it():
    """O1 + O2 on the live repo (spec §5). O1 alone cannot tell a gate that
    passes because a drain was recorded from one that passes because the query
    stopped matching, so the same facts are re-run with the drains stripped and
    must block on exactly the two documents that declare a contradiction."""
    facts = extract(REPO)
    since = date(2026, 8, 2)  # v0.0.3; pinned, not read from tags (they move)
    assert blocking_docs(facts, since) == []

    for d, _, _ in list(facts.triples((None, DG.drains, None))):
        facts.remove((d, None, None))
    assert blocking_docs(facts, since) == [
        "docs/superpowers/plans/2026-08-10-the-decision-membrane.md",
        "docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md",
    ]


def test_the_two_drained_docs_still_declare_contradiction_verbatim():
    """R185's closure condition is that the gate clears WITHOUT editing Evidence
    (spec §5, O1). If a later loop ever drains one of these by rewriting the
    declaration instead, this pin is what notices."""
    for path in ("docs/superpowers/plans/2026-08-10-the-decision-membrane.md",
                 "docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md"):
        assert "**Doc impact:** contradiction" in (REPO / path).read_text(), path
