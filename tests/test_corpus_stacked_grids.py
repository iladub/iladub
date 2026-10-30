"""R74 Task 4 — `compile_document` derives `tab:StackedGrids` before the seal (O4, O5).

Corpus-marked, skip-if-absent like tests/test_corpus_stem.py. Offline: `BAML_LIVE` is removed
from the environment for every compile here, so no proposer reaches a model.

  (a) O4 — cbh: exactly one stack, whose members are exactly `p0/r2#htable{1,3,5,7}`, and the
      graph grows by exactly its 5 triples over the pre-change 16,154 (MEASURED at `123301e`,
      spec 2026-10-28 § 11.1, M7 row).
  (b) O5 — graincorp-stem: no stack and no `tab:inStack`, and the document's validation act
      conforms. Its continuation `p1#htable1` carries the head page's LabelCells, so a query
      that read a table's page off ANY cell would mint a cross-page stack here (spec § 11.2 F1).
  (c) the derivation is unconditional: with `validate_shapes=False`, cbh still carries the stack.

The member IRIs are compared as strings in the TEST only; the derivation itself never reads an
IRI to decide anything (spec M7).
"""
import pytest

from pathlib import Path

from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH

REPO = Path(__file__).resolve().parent.parent
CBH = REPO / "corpus" / "ag-trade" / "cbh-stem-2026-08-03.pdf"
STEM = REPO / "corpus" / "ag-trade" / "graincorp-stem-2026-07-31.pdf"

TAB = Namespace("https://w3id.org/iladub/tab#")

CBH_LEN_BEFORE = 16_154          # MEASURED at 123301e (spec § 11.1, M7 row)
CBH_MEMBERS = {f"p0/r2#htable{i}" for i in (1, 3, 5, 7)}

pytestmark = pytest.mark.corpus

needs_cbh = pytest.mark.skipif(not CBH.is_file(),
                               reason="corpus not populated (scripts/fetch_corpus.py)")
needs_stem = pytest.mark.skipif(not STEM.is_file(),
                                reason="corpus not populated (scripts/fetch_corpus.py)")


def _compile(path, **kw):
    from iladub.etkl.document import compile_document
    with pytest.MonkeyPatch.context() as mp:
        mp.delenv("BAML_LIVE", raising=False)
        return compile_document(str(path), **kw)


def _member_suffixes(graph, stack):
    """The `p<n>/r<m>#htable<k>` tail of each member IRI — the page-document path + fragment."""
    return {"/".join(str(m).rsplit("/", 2)[-2:]) for m in graph.subjects(TAB.inStack, stack)}


@pytest.fixture(scope="module")
def cbh_graph():
    return _compile(CBH).graph


@needs_cbh
def test_o4_cbh_holds_exactly_one_stack_of_the_four_sections(cbh_graph):
    g = cbh_graph
    stacks = list(g.subjects(RDF.type, TAB.StackedGrids))
    assert len(stacks) == 1, stacks
    (s,) = stacks
    assert _member_suffixes(g, s) == CBH_MEMBERS
    # every tab:inStack names this one stack
    assert set(g.objects(None, TAB.inStack)) == {s}
    assert len(g) == CBH_LEN_BEFORE + 5, len(g)


@needs_stem
def test_o5_graincorp_stem_holds_no_stack_and_its_membrane_conforms():
    g = _compile(STEM).graph
    assert not list(g.subjects(RDF.type, TAB.StackedGrids))
    assert not list(g.triples((None, TAB.inStack, None)))
    acts = list(g.subjects(RDF.type, URIRef("https://w3id.org/iladub/etkl#MembraneValidation")))
    assert len(acts) == 1, acts
    assert str(acts[0]).endswith("#membrane-validation")
    assert (acts[0], SH.conforms, Literal(True)) in g


@needs_cbh
def test_c_the_stack_is_derived_without_validation():
    g = _compile(CBH, validate_shapes=False).graph
    stacks = list(g.subjects(RDF.type, TAB.StackedGrids))
    assert len(stacks) == 1, stacks
    assert _member_suffixes(g, stacks[0]) == CBH_MEMBERS
