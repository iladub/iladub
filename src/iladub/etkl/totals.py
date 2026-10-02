"""totals — operands and candidates for a printed total (R261, spec § 2.2, § 7).

PROCEDURAL (CLAUDE.md § 8). Every decision in this module is one of the gate's two PROCEDURAL
classes: raw extraction (a line's word count, a column's cells read back out of the graph exactly
as `holon.py`'s emitters wrote them) or decidable exact arithmetic (`Decimal` sums compared to a
candidate's value, no tolerance). Neither is a reading judgement — "is this number the total of
what is above it" is the NEURAL worker's question (spec § 3.2, `printedtotal.py`); this module
supplies only the arithmetic a worker's *yes* is checked against, and is the SOLE enforcement of
that property (CLAUDE.md § Producer-side guards, R89: a producer-side guard the membrane cannot
also check, because `tab:cellText`'s range is `rdfs:Literal`, never `xsd:decimal`, spec § 4).
One parser throughout — `headers.is_numeric` + `rows._numeric_token_sum` (M6) — never a second.
"""
from __future__ import annotations

import re
from decimal import Decimal

from rdflib import RDF, Graph, URIRef

from .bands import Band
from .classifygraph import TAB
from .geometry import Line
from .headers import is_numeric
from .rows import _numeric_token_sum


def candidate_lines(band: Band) -> list[tuple[int, Line, Decimal]]:
    """A band's lone-numeric-token lines (spec § 2.2 step 1): PROCEDURAL raw extraction — a line
    qualifies iff it has exactly one word and that word `is_numeric`, with no reading judgement
    about what the number means. Returns `(line_index, line, value)` for each; `line_index` is the
    line's position in `band.lines`, `value` is the ONE parser's `_numeric_token_sum` of that
    word (never a second parser, CLAUDE.md § 8 / M6)."""
    out: list[tuple[int, Line, Decimal]] = []
    for i, ln in enumerate(band.lines):
        if len(ln.words) == 1 and is_numeric(ln.words[0].text):
            value = _numeric_token_sum(ln.words[0].text)
            if value is not None:
                out.append((i, ln, value))
    return out


def column_operands(
    graph: Graph, table_uri: URIRef
) -> dict[URIRef, tuple[Decimal, list[URIRef]]]:
    """Table-level operands (spec § 2.2 step 2): PROCEDURAL raw extraction over the already-
    asserted graph — `tab:hasCell` -> `tab:atColumn` + `tab:cellText`, exactly the triples
    `holon.py`'s entry-cell emitters wrote, with no judgement made here. Only cells whose
    `tab:cellText` `is_numeric` (M6's one parser) count toward a column's sum. Returns
    `{column_uri: (exact Decimal sum, [entry-cell uris])}` — a column with zero numeric cells is
    absent from the result, never present with an empty list."""
    per_col: dict[URIRef, tuple[Decimal, list[URIRef]]] = {}
    for entry in graph.objects(table_uri, TAB.hasCell):
        col = graph.value(entry, TAB.atColumn)
        if col is None:
            continue
        text = graph.value(entry, TAB.cellText)
        if text is None or not is_numeric(str(text)):
            continue
        value = _numeric_token_sum(str(text))
        if value is None:
            continue
        total, cells = per_col.get(col, (Decimal(0), []))
        cells.append(entry)
        per_col[col] = (total + value, cells)
    return per_col


def match_table(
    value: Decimal, operands: dict[URIRef, tuple[Decimal, list[URIRef]]]
) -> tuple[URIRef, list[URIRef]] | None:
    """Table-level match (spec § 2.2 step 2, D3): decidable exact `Decimal` arithmetic — binds
    iff EXACTLY ONE column's exact sum equals `value` AND that column has >= 2 member cells (a
    one-cell "total" is not a total — `tab:PrintedTotalShape`'s `tab:aggregates` `sh:minCount 2`,
    spec § 4). Two or more columns tying on the same sum is refused (D3), not arbitrated — no
    tolerance anywhere."""
    hits = [
        (col, cells)
        for col, (total, cells) in operands.items()
        if total == value and len(cells) >= 2
    ]
    if len(hits) != 1:
        return None
    return hits[0]


def match_totals(
    value: Decimal, bound: list[tuple[URIRef, Decimal]]
) -> list[URIRef] | None:
    """Total-of-totals match (spec § 2.2 step 2): decidable exact `Decimal` arithmetic over the
    WHOLE set of `PrintedTotal`s passed — never a subset (spec § 2.2: "subsets breed spurious
    matches"). The caller passes `table_level_totals`, the table-level totals only (R261 loop (b)
    ruling R-f), so a bound grand total never sums into a later one. Binds iff `bound` has >= 2 members AND their exact sum equals
    `value`; returns the bound totals' URIs in that case, else `None`."""
    if len(bound) < 2:
        return None
    total = sum((v for _, v in bound), Decimal(0))
    if total != value:
        return None
    return [uri for uri, _ in bound]


_PT_FRAGMENT = re.compile(r"#printedtotal(\d+)-l(\d+)$")


def _band_order(pt: URIRef) -> tuple[int, int, int, str]:
    """D6's sort key: the (band index, line index) `holon.emit_printed_total` minted into the
    PrintedTotal's own URI fragment (`#printedtotal{idx}-l{line_no}`), read back exactly. A URI not
    of that form (never minted by the emitter) sorts after every minted one, by its text.

    PROCEDURAL raw extraction: a regex read of a URI fragment the emitter already minted, no
    judgement and no constant."""
    m = _PT_FRAGMENT.search(str(pt))
    if m is None:
        return (1, 0, 0, str(pt))
    return (0, int(m.group(1)), int(m.group(2)), str(pt))


def table_level_totals(graph: Graph) -> list[tuple[URIRef, URIRef, Decimal]]:
    """The totals level's operand set (R261 loop (b), spec § 2 step 2, ruling R-f): every
    `tab:PrintedTotal` in `graph` CARRYING `tab:totalOf` — the table-level totals, the whole set —
    as `(printed_total, table, value)`, ordered by ascending band index then line index (plan D6),
    so the listing, the rationale and `tab:aggregates` are deterministic. A grand total (no
    `tab:totalOf`) is never returned, so a bound grand total never sums into a later one.

    PROCEDURAL raw extraction over the already-asserted graph: it reads back the triples
    `holon.emit_printed_total` wrote, with no judgement. `value` is the ONE parser's
    `_numeric_token_sum` of the node's `tab:cellText` (M6). A table-level PrintedTotal whose text
    does not parse cannot have been emitted (its line passed `candidate_lines`), so one raises
    rather than silently shrinking the whole set to a subset (R-f: never a subset).

    Irreducible to AXIOM: the value must go through this ONE parser (`_numeric_token_sum` via
    `headers.is_numeric`), which must not be duplicated as a second implementation in SPARQL —
    and it could not be anyway: `tab:cellText`'s range is `rdfs:Literal` (`tab.ttl`), never
    `xsd:decimal`, so a membrane arithmetic check over it would reopen the R92-R94 engine split
    (CLAUDE.md § Producer-side guards, R89). Irreducible to NEURAL because nothing in it is
    underdetermined — the triples are read back exactly as the emitter wrote them."""
    out: list[tuple[URIRef, URIRef, Decimal]] = []
    for pt in graph.subjects(RDF.type, TAB.PrintedTotal):
        table = graph.value(pt, TAB.totalOf)
        if table is None:
            continue
        text = graph.value(pt, TAB.cellText)
        value = _numeric_token_sum(str(text)) if text is not None and is_numeric(str(text)) \
            else None
        if value is None:
            raise ValueError(f"table-level PrintedTotal {pt} carries no parseable cellText: "
                             f"{text!r}")
        out.append((pt, table, value))
    out.sort(key=lambda t: _band_order(t[0]))
    return out
