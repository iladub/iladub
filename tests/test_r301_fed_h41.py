"""R301 on fed-h41 — the corpus oracles O1, O2 (as amended by spec § 8 S3) and O6.

Spec: docs/superpowers/specs/2026-10-08-r301-producer-guard-design.md § 2.5, § 5 and § 8 S3.

The document is the held-out H.4.1 release whose pages 5 and 7 carried rule-separated cells into
the merged graph (13 of them), so `compile_document` with validation ON raised `MembraneRefusal`.
The producer now withdraws those tables before the membrane sees them:

- **O1** — the document compiles with validation on; p5 reads 187/64, p7 0/137 and the document
  2739/663; the adopted set stays {2, 3, 5, 8, 10}; every other page is identical, region by
  region, to the baseline recorded before any producer-side guard (Task 0,
  `tests/data/r301-fed-h41-baseline.json`, recorded with validation OFF because ON refused).
- **O2** — no rule-separated cell remains; each region a refusal decision regards has exactly one,
  and `effective-chain.rq` bound to that region returns it as its LAST row, chosen `refuse`
  (S3: the option is not relabelled to fit the oracle).
- **O6** — p7's adoption refusal is reported as the cause the page compile observed (the guard),
  not inferred from a region index that counted appended regions (F3).

ONE module-scoped compile (~215 s): every test reads the same `DocumentReport`.
"""
import json
from pathlib import Path

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS

REPO = Path(__file__).resolve().parents[1]
PDF = REPO / "held-out" / "fed-h41-2025-01-02.pdf"
BASELINE = REPO / "tests" / "data" / "r301-fed-h41-baseline.json"
QDIR = REPO / "vocab" / "queries"
MOVED = {5, 7}                       # the two pages the guard changes (spec § 5 O1)

pytestmark = [
    pytest.mark.corpus,
    pytest.mark.skipif(not PDF.exists(), reason="held-out/fed-h41 absent (gitignored corpus)"),
]


@pytest.fixture(scope="module")
def doc():
    from iladub.etkl.document import compile_document
    return compile_document(str(PDF), validate_shapes=True)


def _regions(rep):
    return [{"verdict": r.verdict, "reason": r.reason, "cells": r.cells,
             "tokens_asserted": r.tokens_asserted, "tokens_escalated": r.tokens_escalated}
            for r in rep.regions]


# ---------------------------------------------------------------- O1

def test_o1_the_moved_pages_and_the_document_total(doc):
    print("\nO1 pages:", [(r.asserted, r.escalated) for r in doc.pages], "notes:", doc.notes)
    figures = {p: (doc.pages[p].asserted, doc.pages[p].escalated) for p in MOVED}
    assert figures == {5: (187, 64), 7: (0, 137)}
    assert (sum(r.asserted for r in doc.pages), sum(r.escalated for r in doc.pages)) \
        == (2739, 663)
    assert sorted(doc.adopted) == [2, 3, 5, 8, 10]


def test_o1_every_other_page_is_the_baseline_region_by_region(doc):
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert len(doc.pages) == len(base["pages"])
    moved = {p: (_regions(doc.pages[p]), base["pages"][p]["regions"])
             for p in range(len(doc.pages))
             if p not in MOVED and _regions(doc.pages[p]) != base["pages"][p]["regions"]}
    assert moved == {}
    # The page totals too: a region list can match while the page books a region it does not
    # list (an appended region's tokens are in the page total only through its report).
    totals = {p: ((doc.pages[p].asserted, doc.pages[p].escalated),
                  (base["pages"][p]["asserted"], base["pages"][p]["escalated"]))
              for p in range(len(doc.pages)) if p not in MOVED}
    assert {p: t for p, t in totals.items() if t[0] != t[1]} == {}


# ---------------------------------------------------------------- O2 (§ 8 S3)

def _refusals(g):
    """region IRI -> the refusal decisions that regard it."""
    from iladub.etkl.decisionlog import DEC
    out: dict[URIRef, list[URIRef]] = {}
    for d in g.subjects(RDF.type, DEC.DecisionHolon):
        if (d, RDFS.label, Literal("refusal")) in g:
            for r in g.objects(d, DEC.regarding):
                out.setdefault(r, []).append(d)
    return out


def _withdrawn(doc):
    """The region IRIs whose report the guard escalated (`ruleguard`'s RULE_SEPARATED_INK)."""
    from iladub.etkl.document import page_doc_uri
    return {URIRef(f"{page_doc_uri(p)}#region{i}")
            for p, rep in enumerate(doc.pages) for i, r in enumerate(rep.regions)
            if r.reason == "RULE_SEPARATED_INK"}


def test_o2_no_rule_separated_cell_remains(doc):
    from iladub.etkl.ruleguard import rule_separated_cells
    assert rule_separated_cells(doc.graph) == frozenset()


def test_o2_each_withdrawn_region_has_one_refusal_and_it_ends_the_chain(doc):
    from iladub.etkl.decisionlog import DEC
    refusals = _refusals(doc.graph)
    print("\nO2 refused regions:", sorted(str(r) for r in refusals))
    assert refusals, "no refusal decision in the document graph: nothing was withdrawn"
    assert {r: len(ds) for r, ds in refusals.items() if len(ds) != 1} == {}
    # EVERY withdrawn table has its refusal, not only every refusal its region: the regions a
    # refusal regards are exactly the regions whose report the guard re-booked. Keyed by the
    # PAGE doc URI because the merged graph keeps pass 1's decision log for a band adoption did
    # not supersede; an adopted page's report (`doc.pages[p]` is then the re-compile's) carries
    # the same band index.
    assert set(refusals) == _withdrawn(doc)
    q = (QDIR / "effective-chain.rq").read_text(encoding="utf-8")
    for region, (d,) in refusals.items():
        assert str(region).rsplit("#", 1)[1].startswith("region")
        order = int(doc.graph.value(d, DEC.order))
        rows = [(int(r["order"]), str(r["judgement"]), str(r["chosen"]))
                for r in doc.graph.query(q, initBindings={"region": region})]
        assert rows and rows[-1] == (order, "refusal", "refuse"), (region, rows)
        # LAST, not tied for last: ORDER BY leaves the relative order of equal keys unspecified,
        # so a second row at the refusal's order would make "last" an accident of the engine.
        assert [r for r in rows[:-1] if r[0] >= order] == [], (region, rows)
        # THE EDGE, which the chain rows alone cannot see: with `dec:supersedes` absent the
        # query's fallback branch returns the region's own chain, where the refusal's order
        # (one past the head's) still sorts it last. § 2.3: it supersedes the ONE head.
        heads = list(doc.graph.objects(d, DEC.supersedes))
        assert len(heads) == 1 and (heads[0], RDF.type, DEC.DecisionHolon) in doc.graph, \
            (region, heads)


# ---------------------------------------------------------------- O6

def test_o6_p7_states_the_guard_as_its_cause(doc):
    p7 = [n for n in doc.notes if n.startswith("page 7:")]
    assert any(n.startswith("page 7: adoption refused") and "rule-separated ink" in n
               for n in p7), p7
    assert not any("no data grid region" in n for n in p7), p7


# ---------------------------------------------------------------- R303 O1

def test_r303_each_withdrawn_region_is_furnished_by_its_refusal(doc):
    """R303 (spec 2026-10-09-r303-a-refusal-is-furnished-design.md § 5 O1): the two tables the
    guard withdrew reach a human like every other escalated band, through the refusal."""
    from iladub.etkl.decisionlog import DEC
    g = doc.graph
    requests = set(g.subjects(RDF.type, DEC.ExpansionRequest))
    regarded = {g.value(q, DEC.regarding) for q in requests}
    print("\nR303 O1 requests:", len(requests), "regions:", len(regarded))
    for region, (d,) in _refusals(g).items():
        mine = [q for q in requests if g.value(q, DEC.regarding) == region]
        assert mine == [g.value(d, DEC.escalatedTo)], (region, mine)
    assert set(_refusals(g)) == _withdrawn(doc) and len(_withdrawn(doc)) == 2
    assert (len(requests), len(regarded)) == (14, 14)


# ---------------------------------------------------------------- R300

def test_r300_every_asserted_report_names_a_table_in_the_graph(doc):
    """[[R300]] on the document that raised it. Before the fix p3 `htable7` and p10 `htable3`
    were reported under `…/adopt#` with 0 subject triples (handoff 2026-10-09 § 2, probe A)."""
    dangling = [(p, i, r.table_uri)
                for p, page in enumerate(doc.pages)
                for i, r in enumerate(page.regions)
                if r.verdict == "asserted" and r.table_uri is not None
                and (URIRef(r.table_uri), None, None) not in doc.graph]
    assert dangling == []
