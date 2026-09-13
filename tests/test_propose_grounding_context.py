"""The proposer is handed the page — and the slot is actually FILLED ([[R211]], Task 6).

Spec: docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md § 0, § 3.3
Plan: docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md, Task 6 (DECISION F)

WHY THIS FILE EXISTS AT ALL, and why its central assertion is "the slot is non-empty" rather
than anything about grounding: this repo has declared a page-context slot on a proposer TWICE
and left both dead — `ProposeDimensionName`'s `table_title` is hard-coded None at
`reshape.py`, and `ProposeSplitKeyName`'s `context` is never passed because its caller has no
production call site. A third declared-and-dead slot would look exactly like a feature. So the
claim under test is the one that failed twice: for a REAL compiled document, the text the
carrier put in the graph reaches the proposer.

THE RULING THIS SERVES (§ 0, confirmed by the maintainer 2026-09-12): the MACHINE derives the
unlabelled measure's name, not the contract author. That makes two things prerequisites rather
than later work — the ignored bands' text must be carried ([[R212]], shipped), and the proposer
must be handed it (this task). Until both, the capacity measure cannot be claimed grounded.

WHAT THIS DOES NOT CLAIM: that any measure grounds. Under the corpus battery's abstaining
proposer nothing does, by design, and § 3.3 is explicit that this spec does not change the
battery's proposer to make a gate greener.
"""
import os
import re

import pytest
from rdflib import Graph, Namespace

from iladub.ground import Contract, ContractField, SurfaceConcept, ground_concept
from iladub.propose_ground import GroundingProposal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "corpus")
GRAINCORP = os.path.join(CORPUS, "ag-trade", "graincorp-capacity-2026-08-04.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(GRAINCORP), reason="corpus not fetched")

ETKL = Namespace("https://w3id.org/iladub/etkl#")
SHIP = Namespace("https://example.org/shipping#")


class _Recorder:
    """Records every page context it is handed, and abstains."""

    def __init__(self):
        self.seen = []

    def propose_grounding(self, concept, fields, page_context=None):
        self.seen.append(page_context)
        return GroundingProposal(None, "https://example.org/x#a", 0.0, "n/a",
                                 "urn:iladub:suggester/recorder")


class _TwoArgProposer:
    """A proposer written BEFORE this parameter existed. It must keep working untouched —
    that is what makes the seam a defaulted parameter rather than a breaking change."""

    def propose_grounding(self, concept, fields):
        return GroundingProposal(None, "https://example.org/x#a", 0.0, "n/a",
                                 "urn:iladub:suggester/legacy")


def _contract():
    return Contract(str(SHIP.ElevationCapacity),
                    (ContractField(str(SHIP.fCap), str(SHIP.capacity), None),))


def test_the_page_context_reaches_the_proposer():
    """The seam itself, at the unit: what `ground_concept` is given, the proposer receives."""
    from rdflib import URIRef

    rec = _Recorder()
    ground_concept(SurfaceConcept("", "845870", "reg"), _contract(),
                   URIRef("urn:iladub:record:a"), rec, Graph(), Graph(), Graph(),
                   page_context="ELEVATION CAPACITY TABLE")
    assert rec.seen == ["ELEVATION CAPACITY TABLE"], rec.seen


def test_a_proposer_written_before_this_parameter_still_works():
    """DECISION F: the parameter is DEFAULTED, so the shipped proposers and every existing
    construction site are untouched. A two-argument proposer must still be callable."""
    from rdflib import URIRef

    status = ground_concept(SurfaceConcept("", "845870", "reg"), _contract(),
                            URIRef("urn:iladub:record:b"), _TwoArgProposer(),
                            Graph(), Graph(), Graph())
    assert status == "proposed", status


@corpus_only
def test_the_slot_is_FILLED_for_a_real_compiled_document():
    """THE ASSERTION THIS FILE EXISTS FOR. Not "the parameter exists" — that is what the two
    dead slots also had — but that the carrier's text reaches the proposer on a real document.

    MEASURED on graincorp-capacity: the document graph carries four `etkl:IgnoredBand` nodes,
    and two of them are the licence § 0's ruling rests on — the TITLE ('ELEVATION CAPACITY
    TABLE / As At Tuesday, 4 August 2026') and the FOOTER ('GrainCorp advise that the tonnages
    shown are indicative only and are subject to change.')."""
    from iladub.etkl.document import compile_document
    from iladub.feed import ground_document
    from iladub.ground import load_contract

    rep = compile_document(GRAINCORP, validate_shapes=False)
    contract = load_contract(os.path.join(ROOT, "examples/shipping/capacity-contract.ttl"))
    terms = Graph().parse(os.path.join(ROOT, "examples/shipping/capacity-terms.ttl"),
                          format="turtle")
    shapes = Graph().parse(os.path.join(ROOT, "examples/shipping/capacity-shapes.ttl"),
                           format="turtle")
    rec = _Recorder()
    ground_document(rep.graph, contract, rec, terms, shapes, Graph())

    assert rec.seen, "the proposer was never called at all"
    filled = [c for c in rec.seen if c]
    assert filled, "every page context handed to the proposer was empty — the slot is DEAD"
    context = filled[0]
    assert "ELEVATION CAPACITY TABLE" in context, context
    assert "indicative only" in context, context


# --- the drift pin (Task 6, on test_rowrole_proposer's model) -----------------------------

def test_baml_function_and_python_proposer_agree_on_arity():
    """`baml_src/ground_propose.baml`'s declared signature and `propose_ground.py`'s call site
    agree in name, order and arity. There was NO drift pin for ProposeGrounding — one exists
    only for ProposeHeaderRowRoles — which is how a signature change here could ship against a
    stale generated client.

    The generated-client half is SKIPPED, not failed, when `baml_client` is absent: it is
    gitignored and a fresh checkout has none. CI regenerates it before pytest on every PR."""
    baml = open(os.path.join(ROOT, "baml_src", "ground_propose.baml"), encoding="utf-8").read()
    sig = re.search(r"function ProposeGrounding\((.*?)\)", baml, re.S).group(1)
    params = [p.split(":")[0].strip() for p in sig.split(",")]
    expected = ["surface_text", "value", "field_labels", "page_context"]
    assert params == expected, params

    src = open(os.path.join(ROOT, "src", "iladub", "propose_ground.py"), encoding="utf-8").read()
    call = re.search(r"sync_client\.b\.ProposeGrounding\((.*?)\)\s*\n", src, re.S).group(1)
    args = [a.strip() for a in call.split(",") if a.strip()]
    assert len(args) == 4, args
    assert args[0] == "concept.text" and args[1] == "concept.value", args
    assert args[2] == "labels" and args[3] == "page_context", args

    try:
        import inspect

        from baml_client.sync_client import BamlSyncClient
    except ImportError:
        pytest.skip("baml_client not generated in this checkout — source-only check ran above")
    else:
        gen = inspect.signature(BamlSyncClient.ProposeGrounding)
        gen_params = [p for p in gen.parameters if p not in ("self", "baml_options")]
        assert gen_params == expected, (
            "generated baml_client/sync_client.py is stale relative to baml_src/ — "
            "run `baml-cli generate --from baml_src`")
