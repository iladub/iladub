"""R259 final fix: pin `is_disposed`, the predicate the shared oracle
(tests/test_corpus.py::test_escalation_reasons_are_adjudicated) decides on. Every param of that
oracle is a strict xfail today, so neither an always-False nor an always-True `is_disposed` turned
anything red; this file pins it directly. Always-on: reads only committed files plus an injected
disposal (the `_with_disposal` pattern of tests/test_corpus_manifest.py); no pytest.mark.corpus.
CLAUDE.md § 8: PROCEDURAL test glue; the decision under test is the SPARQL ASK in test_corpus.py."""
import pytest

from tests.corpus_firings import live_pairs
from tests.test_corpus import ADJUDICATED, is_disposed
from tests.test_corpus_manifest import BFS, ONS, _conforms, _with_disposal

KIND = "KIND_NOT_SUPPORTED"


@pytest.mark.parametrize("spelling", [f'"{KIND}"', f'"{KIND}"^^xsd:string'])
def test_disposal_of_a_live_firing_is_disposed(spelling):
    assert is_disposed(_with_disposal(BFS, spelling), BFS, KIND)


def test_no_disposal_is_not_disposed():
    assert not is_disposed(ADJUDICATED, BFS, KIND)


def test_disposal_on_the_other_document_is_not_disposed():
    # KIND_NOT_SUPPORTED fires live on ons too, so this disposal is admissible there -- it just
    # disposes nothing on bfs.
    assert not is_disposed(_with_disposal(ONS, f'"{KIND}"'), BFS, KIND)


def test_language_tagged_disposal_is_not_disposed():
    assert not is_disposed(_with_disposal(BFS, f'"{KIND}"@en'), BFS, KIND)


@pytest.mark.parametrize("doc, reason", live_pairs(ADJUDICATED),
                         ids=lambda v: v.rsplit(":", 1)[-1])
def test_is_disposed_agrees_with_disposal_shape(doc, reason):
    """For each live pair and each spelling of a disposal of it, the oracle's predicate and the
    membrane (cor:DisposalShape) give the same answer: admitted iff disposed."""
    for spelling in (f'"{reason}"', f'"{reason}"^^xsd:string', f'"{reason}"@en'):
        g = _with_disposal(doc, spelling)
        ok, report = _conforms(g)
        assert is_disposed(g, doc, reason) == ok, (spelling, report)
