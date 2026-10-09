"""ruleguard — the producer escalates a table whose cell an author's rule separates (R301).

Spec: docs/superpowers/specs/2026-10-08-r301-producer-guard-design.md §§ 2.2, 2.3, and § 8
(S1–S3), which overrides any earlier sentence it contradicts.

Gate classification (CLAUDE.md § 8): spec § 3's table, cited and not restated. In one line per
part of this module: `rule_separated_cells` is the AXIOM — the select is READ FROM
`tab:RuleSeparatedInkShape`'s own `sh:select`, never copied here, so the guard and the membrane
cannot drift apart; `withdrawal_extent`, `chain_head`, `mint_refusal` and `guard` are PROCEDURAL
recording glue that decides nothing the select has not already decided. No tuned constant: the
one literal, confidence `0.0`, is `holon.py`'s round-trip-refusal "none" boundary (the
`ILADUB.confidence` `0.0` site in `_emit_roundtrip_fail_cell`), cited and not chosen.

R89 (CLAUDE.md § Producer-side guards vs the membrane): the membrane stays the backstop. An
owner table named by zero reports, or by several, is left untouched so the membrane refuses the
page loudly; a missing chain head RAISES at this call site (spec § 2.3).

IMPORTS: `document` imports `compile` at top level, and `compile` will call this module, so
anything from either is imported function-locally (handoff U4). `decisionlog`, `holon` and
`ruleink` import nothing that reaches back here.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from rdflib import Graph, Literal, RDF, RDFS, URIRef, BNode
from rdflib.namespace import SH, XSD

from .decisionlog import DEC, _READER_AGENT, _slug
from .holon import TAB, escalate_region
from .ruleink import _CELL_PREDS

_REASON = "RULE_SEPARATED_INK"
_SHAPE = TAB.RuleSeparatedInkShape
_QUERY: str | None = None


def _select() -> str:
    """The shape's `sh:select`, made runnable once: `$this` -> `?this`, under the PREFIX header
    its own `sh:prefixes`/`sh:declare` names (the idiom of `test_vacuity_registry._runnable`).
    Read from the membrane's own parsed tab shape set, `compile._TAB_SHAPES`, so the select the
    guard runs is the one the membrane validates with.

    RAISES if the shape carries no single `sh:select`: a vocabulary change that removed it must
    fail here, not turn the guard into a silent identity."""
    global _QUERY
    if _QUERY is None:
        from . import compile as _c
        if _c._TAB_SHAPES is None:
            _c._build_membrane()
        sg = _c._TAB_SHAPES
        nodes = list(sg.objects(_SHAPE, SH.sparql))
        selects = [s for n in nodes for s in sg.objects(n, SH.select)]
        if len(nodes) != 1 or len(selects) != 1:
            raise RuntimeError(f"{_SHAPE} must carry exactly one sh:sparql with one sh:select; "
                               f"found {len(nodes)} sh:sparql and {len(selects)} sh:select")
        ns = {}
        for p in sg.objects(nodes[0], SH.prefixes):
            for d in sg.objects(p, SH.declare):
                ns[str(sg.value(d, SH.prefix))] = str(sg.value(d, SH.namespace))
        header = "\n".join(f"PREFIX {p}: <{n}>" for p, n in sorted(ns.items()))
        _QUERY = header + "\n" + str(selects[0]).replace("$this", "?this")
    return _QUERY


def rule_separated_cells(g: Graph) -> frozenset[URIRef]:
    """Every `?this` the shape's own select binds over `g`: the cells an author's rule separates."""
    return frozenset(row.this for row in g.query(_select()))


def owner_tables(g: Graph, cells) -> frozenset[URIRef]:
    """The tables holding a returned cell, through `ruleink._CELL_PREDS` — the two cell edges the
    carrier itself reads."""
    return frozenset(t for c in cells for p in _CELL_PREDS for t in g.subjects(p, c)
                     if isinstance(t, URIRef))


def _in_space(s: str, u: str) -> bool:
    return s == u or s.startswith(u + "-")


def withdrawal_extent(g: Graph, t: URIRef, others: Iterable[URIRef], residue: URIRef) -> Graph:
    """The triples withdrawing table `t` removes (spec § 2.2, as amended by § 8 S1). Pure.

    ROOTS: every URIRef subject in `t`'s URI space (`t`, or `t-…`), minus any root explicitly
    typed `dec:DecisionHolon`, and minus any root in another report's `table_uri` space or the
    residue's (S1). CLOSURE: outgoing edges, followed into blank nodes only.

    S1 IS READ AS "THE MOST SPECIFIC SPACE OWNS THE SUBJECT". The spaces of `t`, `others` and
    `residue` that hold a subject are all prefixes of it, so they nest, and the longest wins. For
    `t` = `…-datagrid` this is S1 word for word (its sibling `…-datagrid-2…` and the residue are
    excluded). For `t` = `…-datagrid-2` with the base `…-datagrid` among `others`, S1 read
    literally would exclude EVERY root of `t` — each lies in the base's space — and the guard
    would refuse a table while withdrawing none of it."""
    spaces = [str(t), *(str(u) for u in others if u is not None and u != t), str(residue)]
    out = Graph()
    seen: set = set()
    frontier = []
    for s in set(g.subjects()):
        if not isinstance(s, URIRef) or not _in_space(str(s), str(t)):
            continue
        if max((u for u in spaces if _in_space(str(s), u)), key=len) != str(t):
            continue
        if (s, RDF.type, DEC.DecisionHolon) in g:
            continue
        seen.add(s)
        frontier.append(s)
    while frontier:
        s = frontier.pop()
        for p, o in g.predicate_objects(s):
            out.add((s, p, o))
            if isinstance(o, BNode) and o not in seen:
                seen.add(o)
                frontier.append(o)
    return out


def chain_head(g: Graph, doc: URIRef, idx: int, t: URIRef) -> URIRef:
    """The decision that currently STANDS for band `idx`: the band's `verdict`
    (`document._verdict_decision`) or, for an appended grid, `{t}-admission` when `g` types it
    `dec:DecisionHolon` (handoff M9) — walked to its head by `document._effective_verdict`
    (the 2026-09-14 lineage ruling: chain, never fan in).

    RAISES when neither exists (spec § 2.3): every branch records one `verdict` per band and
    every grid mints an admission, so a missing one is a producer defect at THIS call site."""
    from .document import _effective_verdict, _verdict_decision
    start = _verdict_decision(g, doc, idx)
    if start is None:
        adm = URIRef(f"{t}-admission")
        if (adm, RDF.type, DEC.DecisionHolon) in g:
            start = adm
    if start is None:
        raise RuntimeError(f"rule guard: no standing decision for table {t} at region index "
                           f"{idx} — neither a `verdict` under {doc}#region{idx}-d nor a "
                           f"{t}-admission decision holon")
    return _effective_verdict(g, start)


def mint_refusal(g: Graph, doc: URIRef, idx: int, head: URIRef, rationale: str) -> URIRef:
    """The one refusal decision for a withdrawn table, written DIRECTLY (spec § 8 S2), never
    through `BandRecorder`: a second `recorder.band(i)` restarts at `-d0` and overwrites.

    Its `dec:order` is one past the head's, or 0 when the head carries none (S2's flagged
    interpretation for an `{t}-admission` head, adopted by the plan). Labelled `refusal`, never
    `verdict`, so `_verdict_decision` still finds the original. The options are named in
    `BandRecorder`'s slug form."""
    r = URIRef(f"{doc}#region{idx}-refusal")
    prior = g.value(head, DEC.order)
    order = 0 if prior is None else int(prior.toPython()) + 1
    g.add((r, RDF.type, DEC.DecisionHolon))
    g.add((r, RDFS.label, Literal("refusal")))
    g.add((r, DEC.order, Literal(order, datatype=XSD.integer)))
    g.add((r, DEC.regarding, URIRef(f"{doc}#region{idx}")))
    g.add((r, DEC.rationale, Literal(rationale)))
    g.add((r, DEC.decidedBy, _READER_AGENT))
    for name in ("admit", "refuse"):
        o = URIRef(f"{r}-opt-{_slug(name)}")
        g.add((o, RDF.type, DEC.Option))
        g.add((o, RDFS.label, Literal(name)))
        g.add((r, DEC.optionSpace, o))
        if name == "refuse":
            g.add((r, DEC.chosen, o))
    g.add((r, DEC.supersedes, head))
    return r


def guard(graph: Graph, reports, asserted_total: int, escalated_total: int,
          doc: URIRef, page_number: int) -> tuple[list, int, int]:
    """Withdraw, refuse, escalate and re-book every table owning a rule-separated cell (spec
    § 2.2's four steps, in order). Mutates `graph`; returns the new reports and totals.

    `sum(r.tokens_asserted) == asserted_total` and `sum(r.tokens_escalated) == escalated_total`
    hold afterwards if they held before: each move books one report's count out of one total and
    into the other. A page whose select returns nothing is the identity."""
    reports = list(reports)
    cells = rule_separated_cells(graph)
    if not cells:
        return reports, asserted_total, escalated_total
    table_uris = [r.table_uri for r in reports]
    residue = URIRef(f"{doc}#p{page_number}-datagrid-residue")
    for t in sorted(owner_tables(graph, cells)):
        named = [i for i, u in enumerate(table_uris) if u == t]
        if len(named) != 1:
            continue                    # R89: left to the membrane, which refuses loudly
        i = named[0]
        r = reports[i]
        head = chain_head(graph, doc, i, t)     # raises before anything for THIS owner is mutated
        crossing = sorted(str(c) for c in cells
                          if any((t, p, c) in graph for p in _CELL_PREDS))
        others = [u for j, u in enumerate(table_uris) if j != i and u is not None]
        for triple in withdrawal_extent(graph, t, others, residue):
            graph.remove(triple)
        mint_refusal(graph, doc, i, head,
                     f"tab:RuleSeparatedInkShape: an author's rule separates the ink of "
                     f"{', '.join(crossing)}")
        anchor = URIRef(r.anchor) if r.anchor is not None else TAB.DataGrid
        # 0.0: the reading was refuted and no confidence is claimed — holon.py's round-trip
        # refusal precedent (module docstring), not a tuned value.
        escalate_region(graph, URIRef(f"{doc}#region{i}"), doc, r.ascii, _REASON, anchor,
                        0.0, page_number)
        moved = r.tokens_asserted
        # header_reading=None as on every other escalated branch: the driver carries a report's
        # reading onto the next page (`document.py`, `.header_reading` read off the previous
        # page's region), and a refused table's reading has row sources inside the withdrawn space.
        reports[i] = replace(r, verdict="escalated", reason=_REASON, cells=0, table_uri=None,
                             header_reading=None, tokens_asserted=0,
                             tokens_escalated=r.tokens_escalated + moved)
        asserted_total -= moved
        escalated_total += moved
    return reports, asserted_total, escalated_total
