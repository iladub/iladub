"""fusion — the re-bucket fusion witness: evidence graph + query runner (box-split Task 3b).

The R225 resolution guard in `compile._build_ruled_band` refuses to re-bucket a band on its author
rules when the rules give fewer columns than the band's rules-free gutter count, because such a
re-bucket "can only FUSE". The count is a proxy for that property; this module lets the guard test
the property itself. The decision lives entirely in vocab/queries/rebucket-fuses.rq (AXIOM,
derivation, open world, no numeric literal): a witness is a cell the re-bucket actually FORMS whose
extent holds a point that no word of any line of the band covers (the box-split spec's fix-round-1
amendment, cited by section below). The witness reads the formed cells themselves, never a model
of them, so it judges exactly what the guard would ship.

This module is PROCEDURAL engine glue only (the boundary.py pattern): it emits the transient
per-band evidence graph and asks rdflib. It decides nothing and carries no tolerance — every
coordinate is passed through as read. The band is the closure boundary: a fresh Graph() per call,
so the query's NOT EXISTS closes over this band's words and no others. The query is parsed once,
at import.
"""
# Spec: docs/superpowers/specs/2026-09-28-box-split-design.md § 8.6 (supersedes § 8.2's witness).
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from rdflib.plugins.sparql import prepareQuery

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:fusion:")     # transient per-band instance namespace

REBUCKET_FUSES_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "rebucket-fuses.rq"
_REBUCKET_FUSES = prepareQuery(REBUCKET_FUSES_RQ.read_text(encoding="utf-8"))


def fusion_evidence(layout_lines, formed_lines) -> Graph:
    """Fresh Graph() for one band: every word of `layout_lines` (the band's own word layout) as a
    tab:LayoutWord, and every word of `formed_lines` (the re-bucket's output,
    `geometry.rule_aware_lines`) as a tab:FormedCell — each with its x-extent as read. Both are
    sequences of objects exposing `.words`, each word exposing `.x0`/`.x1`."""
    g = Graph()
    for li, ln in enumerate(layout_lines):
        for wi, w in enumerate(ln.words):
            n = URIRef(f"{_EV}l{li}w{wi}")
            g.add((n, RDF.type, TAB.LayoutWord))
            g.add((n, TAB.layoutWordX0, Literal(float(w.x0), datatype=XSD.double)))
            g.add((n, TAB.layoutWordX1, Literal(float(w.x1), datatype=XSD.double)))
    for li, ln in enumerate(formed_lines):
        for wi, c in enumerate(ln.words):
            n = URIRef(f"{_EV}r{li}c{wi}")
            g.add((n, RDF.type, TAB.FormedCell))
            g.add((n, TAB.formedCellX0, Literal(float(c.x0), datatype=XSD.double)))
            g.add((n, TAB.formedCellX1, Literal(float(c.x1), datatype=XSD.double)))
    return g


def fusion_witness(layout_lines, formed_lines) -> bool:
    """True iff rebucket-fuses.rq finds a fusion witness: a formed cell of `formed_lines` whose
    extent holds a point no word of `layout_lines` covers."""
    g = fusion_evidence(layout_lines, formed_lines)
    return bool(g.query(_REBUCKET_FUSES).askAnswer)
