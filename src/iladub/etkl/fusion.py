"""fusion — the re-bucket fusion witness: evidence graph + query runner (box-split Task 3b).

The R225 resolution guard in `compile._build_ruled_band` refuses to re-bucket a band on its author
rules when the rules give fewer columns than the band's rules-free gutter count, because such a
re-bucket "can only FUSE". The count is a proxy for that property; this module lets the guard test
the property itself. The decision lives entirely in vocab/queries/rebucket-fuses.rq (AXIOM,
derivation, open world, no numeric literal): a witness is two words on one line, wholly inside one
rule interval, with a point between them that no word of any line of the band covers.

This module is PROCEDURAL engine glue only (the boundary.py pattern): it emits the transient
per-band evidence graph and asks rdflib. It decides nothing and carries no tolerance — every
coordinate is passed through as read. The band is the closure boundary: a fresh Graph() per call,
so the query's NOT EXISTS closes over this band's words and no others.
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:fusion:")     # transient per-band instance namespace

REBUCKET_FUSES_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "rebucket-fuses.rq"


def fusion_evidence(lines, rule_xs) -> Graph:
    """Fresh Graph() for one band: every word of `lines` (objects exposing `.words`, each word
    exposing `.x0`/`.x1`) with its line index, and one tab:RuleInterval per consecutive pair of the
    sorted `rule_xs`."""
    g = Graph()
    for li, ln in enumerate(lines):
        for wi, w in enumerate(ln.words):
            n = URIRef(f"{_EV}l{li}w{wi}")
            g.add((n, RDF.type, TAB.LayoutWord))
            g.add((n, TAB.onLayoutLine, Literal(li, datatype=XSD.integer)))
            g.add((n, TAB.layoutWordX0, Literal(float(w.x0), datatype=XSD.double)))
            g.add((n, TAB.layoutWordX1, Literal(float(w.x1), datatype=XSD.double)))
    xs = sorted(rule_xs)
    for i, (lo, hi) in enumerate(zip(xs, xs[1:])):
        n = URIRef(f"{_EV}i{i}")
        g.add((n, RDF.type, TAB.RuleInterval))
        g.add((n, TAB.ruleIntervalLo, Literal(float(lo), datatype=XSD.double)))
        g.add((n, TAB.ruleIntervalHi, Literal(float(hi), datatype=XSD.double)))
    return g


def fusion_witness(lines, rule_xs) -> bool:
    """True iff rebucket-fuses.rq finds a fusion witness over this band's words and rules."""
    g = fusion_evidence(lines, rule_xs)
    return bool(g.query(REBUCKET_FUSES_RQ.read_text(encoding="utf-8")).askAnswer)
