"""R259 final fix: pin `is_disposed`, the predicate the shared oracle
(tests/test_corpus.py::test_escalation_reasons_are_adjudicated) decides on. Every param of that
oracle is a strict xfail today, so neither an always-False nor an always-True `is_disposed` turned
anything red; this file pins it directly. Always-on: reads only committed files plus an injected
disposal (the `_with_disposal` pattern of tests/test_corpus_manifest.py); no pytest.mark.corpus.
CLAUDE.md § 8: PROCEDURAL test glue; the decision under test is the SPARQL ASK in test_corpus.py.

tab:07 (spec 2026-10-19 § 4.3, § 8 A2): the real manifest now disposes of KIND_NOT_SUPPORTED on
bfs and ons, so a pin built on that pair asserts the opposite of the manifest, or passes without
its injection. The single-pair pins sit on bfs DATAGRID_RESIDUE, which fires live on bfs and on
ons and is disposed of on neither; the agreement test removes the real disposals of the pair it
checks, so every spelling is compared against an undisposed pair."""
import pytest
from rdflib import BNode, Graph, URIRef

from tests.corpus_firings import COR, lift_firings, lift_snapshots, live_pairs
from tests.test_corpus import ADJUDICATED, is_disposed
from tests.test_corpus_manifest import (BASELINE, BFS, MANIFEST, ONS, _conforms,
                                        _with_disposal)

RESIDUE = "DATAGRID_RESIDUE"        # live and undisposed on bfs and on ons (spec § 4.3)


@pytest.mark.parametrize("spelling", [f'"{RESIDUE}"', f'"{RESIDUE}"^^xsd:string'])
def test_disposal_of_a_live_firing_is_disposed(spelling):
    assert is_disposed(_with_disposal(BFS, spelling), BFS, RESIDUE)


def test_no_disposal_is_not_disposed():
    assert not is_disposed(ADJUDICATED, BFS, RESIDUE)


def test_disposal_on_the_other_document_is_not_disposed():
    # DATAGRID_RESIDUE fires live on ons too, so this disposal is admissible there -- it just
    # disposes of nothing on bfs, where the same reason also fires live and stays undisposed.
    assert not is_disposed(_with_disposal(ONS, f'"{RESIDUE}"'), BFS, RESIDUE)


def test_language_tagged_disposal_is_not_disposed():
    assert not is_disposed(_with_disposal(BFS, f'"{RESIDUE}"@en'), BFS, RESIDUE)


def _real_disposals(doc: str, reason: str) -> set[tuple]:
    """(by, on, rationale) of each adjudication the committed manifest holds on `doc` disposing
    of `reason`. Literals compare across parses; the adjudication blank nodes do not."""
    m = Graph().parse(MANIFEST, format="turtle")
    return {(m.value(a, COR.by), m.value(a, COR.on), m.value(a, COR.rationale))
            for a in m.objects(URIRef(doc), COR.adjudication)
            if any(str(v) == reason for v in m.objects(a, COR.disposes))}


def _drop(g: Graph, node) -> None:
    """Remove `node`'s triples and, recursively, those of the blank nodes it reaches."""
    for p, o in list(g.predicate_objects(node)):
        g.remove((node, p, o))
        if isinstance(o, BNode):
            _drop(g, o)


def _without_real_disposals(g: Graph, doc: str, reason: str) -> Graph:
    """`g` less the committed adjudications disposing of (doc, reason), with their snapshots and
    the snapshots' lifted firings. The injected disposal is not among them: its by/on/rationale
    ("t", 2026-10-16, "t") match no committed adjudication."""
    real = _real_disposals(doc, reason)
    for a in list(g.objects(URIRef(doc), COR.adjudication)):
        if (g.value(a, COR.by), g.value(a, COR.on), g.value(a, COR.rationale)) in real:
            g.remove((URIRef(doc), COR.adjudication, a))
            _drop(g, a)
    return g


@pytest.mark.parametrize("doc, reason", live_pairs(ADJUDICATED),
                         ids=lambda v: v.rsplit(":", 1)[-1])
def test_is_disposed_agrees_with_disposal_shape(doc, reason):
    """For each live pair and each spelling of a disposal of it, the oracle's predicate and the
    membrane (cor:DisposalShape) give the same answer: admitted iff disposed. The pair's real
    disposals are removed first, so the injected spelling alone decides both answers."""
    for spelling in (f'"{reason}"', f'"{reason}"^^xsd:string', f'"{reason}"@en'):
        g = _without_real_disposals(_with_disposal(doc, spelling), doc, reason)
        ok, report = _conforms(g)
        assert is_disposed(g, doc, reason) == ok, (spelling, report)


def test_live_pairs_reads_no_snapshot_as_a_document():
    """spec § 8 A8: `live_pairs` filters cor:firing subjects to URIRefs. On the real manifest
    with its snapshots lifted, the snapshot blank nodes hold live firings, and none of them may
    come back as a document."""
    m = Graph().parse(MANIFEST, format="turtle")
    g = m + lift_firings(m, BASELINE) + lift_snapshots(m)
    snapshot_subjects = {s for s in g.subjects(COR.firing) if isinstance(s, BNode)}
    assert snapshot_subjects, "precondition: the real manifest names a snapshot with firings"
    docs = {d for d, _ in live_pairs(g)}
    assert docs == {d for d, _ in live_pairs(m + lift_firings(m, BASELINE))}
    assert not docs & {str(s) for s in snapshot_subjects}
