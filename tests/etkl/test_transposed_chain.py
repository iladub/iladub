"""The R55 ordering link, asserted where it is actually exercised
(spec 2026-08-07-ordering-proof-and-supersession-design.md §4.1).

R55's misattribution was claiming a gate failed "solely because" of one observation, when a
DIFFERENT gate had fired first and the second was only then consulted. `dec:order` is what
makes that answerable. No corpus document reaches the coherence oracle (R68's narrowed row),
but these two fixtures do — and they cover BOTH branches of it.

These tests run the COMMITTED .rq files; query logic is never reimplemented here.
"""
import os

import pytest

pytest.importorskip("reportlab")
pytest.importorskip("pdfplumber")

from rdflib import URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDIR = os.path.join(ROOT, "vocab", "queries")


def _run(name, g, region):
    """Returns tuples, not dicts: this module never READS a column that can be unbound, so
    positional access is simpler and matches how _order/_chain below consume the results.
    (Some columns here ARE unbound — `?supersededBy` always, since compile_tables never emits
    dec:supersedes, and `?refutedBy` for a chosen option — this module just never reads them.)
    See test_supersession_queries.py's _run for why it uses .asdict() instead: asserting the
    ABSENCE of a binding needs a dict. That divergence is deliberate, not an oversight to unify."""
    q = open(os.path.join(QDIR, name), encoding="utf-8").read()
    return [tuple(r) for r in g.query(q, initBindings={"region": region})]


def _compile(fixture, tmp_path, stem):
    from iladub.etkl import compile_tables
    from iladub.etkl.compile import _DOC
    p = tmp_path / f"{stem}.pdf"
    fixture(str(p))
    return compile_tables(str(p)).graph, URIRef(f"{_DOC}#region0")


def _order(g, region):
    """{judgement label: dec:order} for one region, via the committed query."""
    return {str(j): int(o) for j, o in _run("judgement-order.rq", g, region)}


def _chain(g, region):
    """{judgement label: (chosen, rationale)} via the committed why-escalated.rq."""
    return {str(r[1]): (str(r[2]), str(r[3])) for r in _run("why-escalated.rq", g, region)}


def test_refusal_branch_records_transposed_before_the_coherence_oracle(tmp_path):
    """THE R55 SHAPE: looks_transposed fires FIRST; the coherence oracle is consulted
    SECOND and refuses. A reader of this chain cannot mistake the second gate for the cause."""
    from tests.etkl.fixtures import false_transposed_pdf
    g, region = _compile(false_transposed_pdf, tmp_path, "false_transposed")

    order = _order(g, region)
    assert "transposed" in order, f"transposed judgement not recorded; got {sorted(order)}"
    assert "transpose_coherent" in order, \
        f"the coherence oracle was not consulted; got {sorted(order)}"
    assert order["transposed"] < order["transpose_coherent"], \
        f"ordering inverted: {order}"

    chain = _chain(g, region)
    assert chain["transposed"][0] == "transposed"
    assert chain["transpose_coherent"][0] == "incoherent"
    assert chain["verdict"][0] == "escalated"
    assert chain["verdict"][1] == "TRANSPOSED"


def test_acceptance_branch_records_the_same_ordering(tmp_path):
    """The other branch: the oracle accepts and the region compiles. The ordering claim must
    hold regardless of which way the second gate goes."""
    from tests.etkl.fixtures import transposed_table_pdf
    g, region = _compile(transposed_table_pdf, tmp_path, "transposed_table")

    order = _order(g, region)
    assert order["transposed"] < order["transpose_coherent"], f"ordering inverted: {order}"

    chain = _chain(g, region)
    assert chain["transpose_coherent"][0] == "coherent"
    assert chain["verdict"][0] == "asserted"


def test_the_refusal_is_reachable_by_query_alone(tmp_path):
    """§4's standard: the question must be answerable from the record BY QUERY. Ask
    what-was-considered.rq what the coherence oracle had as options and which it took."""
    from tests.etkl.fixtures import false_transposed_pdf
    g, region = _compile(false_transposed_pdf, tmp_path, "false_transposed")
    rows = _run("what-was-considered.rq", g, region)
    opts = {str(o) for j, o, _ in rows if str(j) == "transpose_coherent"}
    assert opts == {"coherent", "incoherent"}, opts
