"""The four-class split of `scripts/probe_domain_range_agreement.py`.

MEASURED 2026-08-18, 27 corpus pages: of 74 violations the probe reports, **0** are a node
missing its type — the failure the script's former name ("emitter typing") claimed to detect.
60 are the emitter and the ontology disagreeing about a node's type, 2 are a type the membrane's
own ontology supplies, and 12 are a type supplied only by `tab-datagrid.ttl`, which
`compile._FULL_ONT` does not load. Those four are different findings with different repairs, so
the probe has to name them apart — and only the first two may gate.

The classes are exercised on small hand-built graphs rather than the corpus: the corpus fixes
today's counts, these fix the meaning, and a class that cannot be produced by hand is a class
nobody can reason about.
"""
import re
from pathlib import Path

import pytest
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

from scripts.probe_domain_range_agreement import (
    DISAGREE,
    MEMBRANE_ONT_FILES,
    ONT_VISIBLE,
    OUTSIDE_MEMBRANE,
    UNTYPED,
    _closure,
    classified,
    typing_rules,
)

EX = Namespace("http://example.org/v#")
DOC = Namespace("http://example.org/doc#")


@pytest.fixture
def graphs():
    """(membrane ontology, wider probe ontology, page graph) — the three-graph shape the real
    probe runs on, in miniature. `conformsTo`/`Axiom` stand for the data-grid vocabulary the
    membrane never loads; everything else stands for `tab.ttl`."""
    membrane = Graph()
    for t in (
        (EX.hasLabel, RDFS.range, EX.LabelCell),
        (EX.columnFamily, RDFS.range, EX.Family),
        (EX.Quantity, RDF.type, EX.Family),      # a constant the membrane CAN see
        (EX.Text, RDF.type, EX.Datatype),        # typed, but not as Family
    ):
        membrane.add(t)

    wider = Graph()
    wider += membrane
    for t in (
        (EX.conformsTo, RDFS.range, EX.Axiom),
        (EX.RowAddr, RDF.type, EX.Axiom),        # declared ONLY outside the membrane
    ):
        wider.add(t)

    page = Graph()
    for t in (
        (DOC.grid, EX.columnFamily, EX.Quantity),
        (DOC.grid, EX.columnFamily, EX.Text),
        (DOC.grid, EX.conformsTo, EX.RowAddr),
        (DOC.grid, EX.hasLabel, DOC.entry),
        (DOC.entry, RDF.type, EX.EntryCell),     # typed by the emitter, just not LabelCell
        (DOC.grid, EX.hasLabel, DOC.ghost),      # typed nowhere at all
    ):
        page.add(t)
    return membrane, wider, page


def _classes(graphs):
    membrane, wider, page = graphs
    domains, ranges = typing_rules(wider)
    sup = _closure(wider)
    return {node: klass for _key, _cls, node, klass
            in classified(page, domains, ranges, sup, membrane, wider)}


def test_the_four_classes_are_told_apart(graphs):
    got = _classes(graphs)
    assert got == {
        EX.Quantity: ONT_VISIBLE,        # membrane's ontology supplies the type
        EX.Text: DISAGREE,               # ontology types it — as something else
        EX.RowAddr: OUTSIDE_MEMBRANE,    # typed only in vocabulary the membrane never loads
        DOC.entry: DISAGREE,             # emitter typed it — as something else
        DOC.ghost: UNTYPED,              # no type anywhere: the invariant R61 named
    }


def test_a_type_the_membrane_cannot_see_is_not_ont_visible(graphs):
    """The distinction the corpus measurement turned on: 12 of the 14 reported 'artifacts' are
    `tab:GridAxiom` individuals declared only in `tab-datagrid.ttl`. Collapsing them into
    ONT_VISIBLE — the fix the 2026-08-18 handoff proposed — would have silenced the sharpest
    evidence that R103's membrane question is real."""
    assert _classes(graphs)[EX.RowAddr] == OUTSIDE_MEMBRANE


def test_membrane_ont_files_mirrors_the_compiler(graphs):
    """The probe's whole claim is that it models what the membrane validates. If
    `compile._FULL_ONT` gains or loses an ontology and this tuple does not, every class above
    is computed against the wrong graph — silently, and in the direction of under-reporting."""
    src = (Path(__file__).resolve().parent.parent
           / "src" / "iladub" / "etkl" / "compile.py").read_text()
    loaded = set(re.findall(r'os\.path\.join\(v, "ontology", "([^"]+)"\)', src))
    assert loaded == set(MEMBRANE_ONT_FILES)
