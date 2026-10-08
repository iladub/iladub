"""Carry the author's vertical rules and each cell's glyph extents into the page graph, so the
membrane can refuse a cell whose ink a rule separates (spec 2026-10-08-rule-separated-ink-design.md).

Gate classification (CLAUDE.md § 8): PROCEDURAL — raw extraction (rule and glyph geometry, source to
typed facts) plus decidable exact arithmetic (a min and a max). Nothing here decides whether a rule
separates anything: that is `tab:RuleSeparatedInkShape`'s, a closed-world SHACL constraint at the
membrane. No tolerance and no constant: the rounding is the 2dp `tab:ruleX` already carries
(`gridregion.py`), reused rather than chosen.
"""
from __future__ import annotations

from decimal import Decimal

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

TAB = Namespace("https://w3id.org/iladub/tab#")
_CELL_PREDS = (TAB.hasCell, TAB.hasDataCell)


def _d2(x: float) -> Literal:
    return Literal(Decimal(str(round(x, 2))))


def glyph_extents(chars, bbox) -> tuple[float, float] | None:
    """(min glyph.x1, max glyph.x0) over the non-space glyphs whose centre lies inside `bbox`
    (x0, y0, x1, y1), inclusive — or None when the box holds no glyph. A glyph wholly left of x
    exists iff the first value is <= x; one wholly right iff the second is >= x (spec § 1)."""
    x0, y0, x1, y1 = bbox
    ends, starts = [], []
    for c in chars:
        if not c.text.strip():
            continue
        if x0 <= (c.x0 + c.x1) / 2 <= x1 and y0 <= (c.top + c.bottom) / 2 <= y1:
            ends.append(c.x1)
            starts.append(c.x0)
    if not ends:
        return None
    return min(ends), max(starts)


def carry_rule_ink(graph: Graph, doc: str, rules_by_page, chars_by_page) -> int:
    """Add, for every page a cell of `graph` sits on (by its `tab:onPage`) that has at least one
    rule: one `tab:RuleSpan` per rule, and the two glyph-extent literals on each of that page's
    cells. A page with no rule adds nothing, so an unruled page's graph is byte-identical.
    `rules_by_page` / `chars_by_page` are mappings page -> list (or callables page -> list).
    Returns the number of triples added."""
    get_rules = rules_by_page if callable(rules_by_page) else rules_by_page.get
    get_chars = chars_by_page if callable(chars_by_page) else chars_by_page.get
    before = len(graph)
    cells_by_page: dict[int, list] = {}
    for cp in _CELL_PREDS:
        for c in set(graph.objects(None, cp)):
            p = graph.value(c, TAB.onPage)
            if p is not None and graph.value(c, TAB.hasBBox) is not None:
                cells_by_page.setdefault(int(p), []).append(c)
    for page in sorted(cells_by_page):
        rules = get_rules(page) or []
        if not rules:
            continue
        for k, r in enumerate(rules):
            u = URIRef(f"{doc}#rule-p{page}-{k}")
            graph.add((u, RDF.type, TAB.RuleSpan))
            graph.add((u, TAB.ruleX, _d2(r.x)))
            graph.add((u, TAB.ruleTop, _d2(r.top)))
            graph.add((u, TAB.ruleBottom, _d2(r.bottom)))
            graph.add((u, TAB.onPage, Literal(page, datatype=XSD.integer)))
        chars = get_chars(page) or []
        for c in sorted(cells_by_page[page], key=str):
            b = graph.value(c, TAB.hasBBox)
            box = tuple(float(graph.value(b, TAB[k])) for k in ("x0", "y0", "x1", "y1"))
            ext = glyph_extents(chars, box)
            if ext is None:
                continue
            graph.add((c, TAB.firstGlyphEnd, _d2(ext[0])))
            graph.add((c, TAB.lastGlyphStart, _d2(ext[1])))
    return len(graph) - before


def carry_from_pdf(graph: Graph, doc: str, pdf_path: str) -> int:
    """`carry_rule_ink` over the PDF's own extraction, read lazily per cell page."""
    from .geometry import extract_chars, extract_rules
    rules_cache: dict[int, list] = {}

    def rules(p):
        if p not in rules_cache:
            rules_cache[p] = extract_rules(pdf_path, p)
        return rules_cache[p]

    return carry_rule_ink(graph, doc, rules, lambda p: extract_chars(pdf_path, p))
