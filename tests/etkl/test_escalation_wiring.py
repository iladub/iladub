"""escalation-furnish.rq, WIRED — S1 answered, and the two shapes it takes live.

Task 2 shipped the derivation offline. This is the commit that can break every escalating
document: the moment a `dec:ExpansionRequest` enters a validated graph, `dec:EventShape`
and `dec:ExpansionRequestShape` — both already in `_DEC_SHAPE_FILES` (`compile.py:399`)
and both idle until now — go live and can refuse it.

THE SITE, and why it is not a matter of taste. S1 was answered by measurement
(`docs/superpowers/2026-08-15-r87-task3-measurement.md`): the derivation's supersession
guard only works where the `dec:supersedes` edges exist, and BOTH writers of those edges
(`document.py:1299` section repair, `document.py:1503` datagrid adoption) write into the
DOCUMENT graph and into no page graph — 0 edges observed in 13 page graphs. Page-scope
furnishing is therefore not merely early: the edges never enter the object it holds, at
any time. Measured cost of getting it wrong: 4 spurious expansion requests on cbh-stem
and 5 on apple, every one of them a matter a later reading had already resolved.

So the tests below are written against the DOCUMENT driver. Two of them
(`test_the_adopting_path_furnishes_nothing`, and the apple census) would still pass at a
page-scope site with the numbers inverted, which is why each states the number the
measurement recorded rather than the number that felt right.
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Namespace
from rdflib.namespace import RDF, RDFS

from iladub.etkl.document import compile_document
from tests.etkl.fixtures import (currency_marker_escalating_pdf,
                                 recognized_pair_plus_escalating_page_pdf)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEC = Namespace("https://w3id.org/iladub/dec#")
ETKL = Namespace("https://w3id.org/iladub/etkl#")
RISK = Namespace("https://w3id.org/iladub/risk#")


def _chose_escalated(g):
    return {d for d in g.subjects(RDF.type, DEC.DecisionHolon)
            if any(str(lbl) == "escalated"
                   for o in g.objects(d, DEC.chosen)
                   for lbl in g.objects(o, RDFS.label))}


def _requests(g):
    return set(g.subjects(RDF.type, DEC.ExpansionRequest))


@pytest.fixture(scope="module")
def escalating_doc(tmp_path_factory):
    """One compile of the gate-opening escalating document, shared by T3.1-T3.3.

    ~6 s, so it is built once: three tests each compiling it would put 18 s into the
    fast suite for one document's worth of evidence.
    """
    pdf = tmp_path_factory.mktemp("r87") / "recognized_plus_escalating.pdf"
    recognized_pair_plus_escalating_page_pdf(str(pdf))
    return compile_document(str(pdf))


# ---------------------------------------------------------------- T3.1


def test_an_escalating_document_is_furnished_and_still_compiles(escalating_doc):
    """The derivation runs in the pipeline, and the membrane admits what it wrote.

    `recognized` is asserted, not assumed: it is `document.py:1515`'s validation gate
    (`recognized or section_facts`), and without it this document would cross no
    document-level membrane at all and the test would be green for the wrong reason.
    Every other synthetic fixture that escalates leaves that gate shut — see the
    fixture's docstring for the measurement.
    """
    assert escalating_doc.recognized, "the validation gate is shut — the pin is vacuous"
    assert len(_chose_escalated(escalating_doc.graph)) == 1
    assert len(_requests(escalating_doc.graph)) == 1


# ---------------------------------------------------------------- T3.2


def test_every_request_carries_exactly_one_condition(escalating_doc):
    """dec:EventShape, satisfied from the first commit.

    dec:ExpansionRequest rdfs:subClassOf dec:Event (dec.ttl:197-198), so under the
    membrane's subclass closure every request the derivation mints is a dec:Event, and
    dec-shapes.ttl:60-63 requires exactly one dec:condition on one.

    THIS TEST'S FALSIFICATION IS ALSO T3.1'S ORDERING PROOF. Drop dec:condition from the
    CONSTRUCT template and `compile_document` above must RAISE — the document is REFUSED,
    not merely unvalidated (plan §4.4). A refusal is only possible if the derivation runs
    BEFORE `document.py:1515`; furnishing after it would leave this same broken graph
    compiling clean, which no assertion on the returned graph could tell apart.
    """
    g = escalating_doc.graph
    requests = _requests(g)
    assert requests
    for req in requests:
        assert len(list(g.objects(req, DEC.condition))) == 1


# ---------------------------------------------------------------- T3.3


def test_every_request_names_what_it_is_about(escalating_doc):
    """dec:ExpansionRequestShape (dec-shapes.ttl:71-74): "I don't know" has to be
    provenanced. The request's dec:regarding is the decision's own — the region the
    reader could not read — never a fresh subject."""
    g = escalating_doc.graph
    requests = _requests(g)
    assert requests
    for req in requests:
        regarding = set(g.objects(req, DEC.regarding))
        assert regarding
        d = next(g.subjects(DEC.escalatedTo, req))
        assert regarding == set(g.objects(d, DEC.regarding))


# ---------------------------------------------------------------- T3.4


def test_the_derivation_runs_once_on_the_document_graph(tmp_path, monkeypatch):
    """R19 hazard (decisionlog.py:12-14): a decision graph handed to a membrane that
    thinks it is looking at something else. Pinned by IDENTITY, not by reading the call
    site — the graph the derivation is handed must be the very object the driver returns,
    which no region scratch graph and no per-page graph can be.

    The call count is half the pin: once per document. A derivation invoked per page (or,
    worse, per region) would still satisfy an identity check on its last call while having
    furnished pages whose escalations the document graph later withdraws.
    """
    from iladub.etkl import document as docmod
    from iladub.etkl import interpret

    seen = []
    real_run = interpret.run

    def spy(query_path, *graphs):
        if os.path.basename(str(query_path)) == "escalation-furnish.rq":
            seen.append(graphs)
        return real_run(query_path, *graphs)

    monkeypatch.setattr(interpret, "run", spy)

    pdf = tmp_path / "recognized_plus_escalating.pdf"
    recognized_pair_plus_escalating_page_pdf(str(pdf))
    rep = docmod.compile_document(str(pdf))

    assert len(seen) == 1, f"the derivation ran {len(seen)} times, not once per document"
    assert seen[0][0] is rep.graph, "the derivation was handed a graph that is not the document's"


# ---------------------------------------------------------------- T3.5


def test_the_adopting_path_furnishes_nothing(tmp_path):
    """The adopting path, pinned at the number the measurement recorded — ZERO.

    `currency_marker_escalating_pdf` escalates its one band, the driver adopts the page's
    data grid, and `document.py:1503` links the admission holon to the withdrawn verdict
    with dec:supersedes. Measured 2026-08-15 at document scope: one decision chose
    "escalated", one carries an incoming dec:supersedes, and the derivation furnishes 0.

    THIS IS THE SITE TEST. The same document furnishes ONE request at page scope, where
    that dec:supersedes edge does not exist and never will (the edge is written into the
    document graph by a writer that runs after `compile_tables` has returned). A wiring
    that put the derivation inside `compile_tables` passes T3.1-T3.4 and fails here — and
    on the corpus it fails by 4 requests on cbh-stem and 5 on apple.
    """
    pdf = tmp_path / "adopting.pdf"
    currency_marker_escalating_pdf(str(pdf))
    rep = compile_document(str(pdf))

    assert rep.adopted == (0,), rep.adopted
    escalating = _chose_escalated(rep.graph)
    assert len(escalating) == 1
    assert all(list(rep.graph.subjects(DEC.supersedes, d)) for d in escalating), \
        "the adoption no longer withdraws the escalation — the pin measures something else"
    assert _requests(rep.graph) == set()


# ---------------------------------------------------------------- T3.5, on the corpus

APPLE = os.path.join(ROOT, "corpus", "financial", "apple-fy2026q3-statements.pdf")


@pytest.mark.corpus
@pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus not populated")
def test_corpus_apple_furnishes_what_it_escalates(tmp_path):
    """RE-BASELINED 2026-09-05 ([[R173]] 5a), from `test_corpus_apple_furnishes_the_measured_ten`.

    It was written 2026-08-15 against the measurement of the day: apple was the one corpus
    document that reached `document.py`'s adoption gate (`adopted=(1,)`), 15 decisions chose
    "escalated", 5 were withdrawn by page 1's adoption, and the document graph furnished 10 —
    so the single number 10 was the DIFFERENCE between the two candidate derivation sites on a
    real document, page scope summing to 15.

    WHAT THE NEW NUMBERS MEAN. Since `4cfee38` ([[R160]]) apple adopts nothing, and since
    [[R165]]'s one-band reading pages 0 and 1 assert outright, so almost all of that escalation
    is gone: MEASURED 2026-09-05 as `adopted=(), chose escalated=5, superseded=0, requests=5`.
    With no adoption there is no withdrawal, so the difference this test measured is ZERO on
    apple and the number 10 cannot be recovered by editing it — `escalating == requests` is
    what apple can still say, and it says it: every escalating decision furnishes a request
    because none is superseded.

    THE SITE CLAIM IS NOT LOST WITH IT. `test_the_adopting_path_furnishes_nothing` above pins
    the derivation site on a SYNTHETIC adopting document (`adopted=(0,)`, one withdrawal, zero
    requests) and runs in CI, where this test has always skipped — see the module-level note in
    `tests/etkl/test_adoption_document.py`. This one is now apple's corroboration, not the pin.
    """
    rep = compile_document(APPLE)
    escalating = _chose_escalated(rep.graph)
    superseded = {d for d in escalating if list(rep.graph.subjects(DEC.supersedes, d))}
    requests = _requests(rep.graph)

    print(f"\napple: adopted={rep.adopted!r} chose escalated={len(escalating)} "
          f"superseded={len(superseded)} requests={len(requests)}")
    assert rep.adopted == ()
    assert len(escalating) == 5
    assert len(superseded) == 0
    assert len(requests) == 5
    # the invariant that survives the numbers: with nothing withdrawn, the document furnishes
    # exactly what it escalates — a request lost between the two sites still fails here.
    assert requests and len(requests) == len(escalating)


# ---------------------------------------------------------------- the carried vocabulary


def test_the_vocabulary_carry_reaches_the_document_graph(escalating_doc):
    """G3 condition 3, at the far end of the wire. T2.4 pins the carry on the derivation's
    OUTPUT; this pins that all three triples survive into the graph the membrane validates,
    because a shape that cannot see `?ceil risk:order ?co` binds nothing and R87 comes back
    wearing a different hat.

    Exactly three, named — the same closure T2.4 pins. If a fourth ever appears, something
    merged the vocabulary.

    The selector is `risk:`-anything plus `etkl:readerScope` specifically, NOT the whole
    etkl: namespace: `etkl:reader` (decisionlog's `prov:SoftwareAgent`) is a data subject
    the pipeline has always written, and sweeping it in would make this test measure the
    recorder rather than the carry. risk: has no other producer, so a `risk.ttl` merge
    still fails here on the terms that matter.
    """
    from rdflib import Literal

    g = escalating_doc.graph
    carried = {t for t in g
               if str(t[0]).startswith(str(RISK)) or t[0] == ETKL.readerScope}
    assert carried == {
        (ETKL.readerScope, DEC.maxSeverity, RISK.Watch),
        (RISK.Breach, RISK.order, Literal(2)),
        (RISK.Watch, RISK.order, Literal(1)),
    }
