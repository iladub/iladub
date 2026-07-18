"""celltype — the typed-cell evidence graph + query runner (neurosymbolic loop B2a).

The type/orientation boundary decisions (header/body split, stub/data split, transpose) are
declarative DERIVATIONS over per-cell datatype facts (open-world → SPARQL, the loop-B side of the
gate). This module is the PROCEDURAL layer only: raw datatype typing (via is_numeric), emitting the
transient typed-cell evidence graph, and invoking rdflib. No decision logic, no tuned constant —
the decisions live entirely in vocab/queries/*.rq (AXIOM). Irreducible: a SPARQL engine must be
invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

import re
from pathlib import Path

from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

from .headers import is_numeric

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

_ISO_DATE = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
_DMY_DATE = re.compile(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$")
_MON_DATE = re.compile(r"^\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}$", re.I)
_CURRENCY = re.compile(r"^-?[$€£¥]\s?-?[\d,]+(\.\d+)?$|^-?[\d,]+(\.\d+)?\s?[$€£¥]$")


def is_date(s):
    """Conservative date typing: a full date shape with a 4-digit YEAR and valid month(1-12)/
    day(1-31) ranges. The 4-digit-year + range requirement excludes '1-2', '99-99-9999',
    '2024-13-01'. Raw datatype detection (PROCEDURAL) — a format grammar, not a tuned tolerance."""
    t = s.strip()
    m = _ISO_DATE.match(t)
    if m:
        parts = re.split(r"[-/]", t)
        return 1 <= int(parts[1]) <= 12 and 1 <= int(parts[2]) <= 31
    m = _DMY_DATE.match(t)
    if m:
        parts = re.split(r"[-/]", t)
        return 1 <= int(parts[1]) <= 12 and 1 <= int(parts[0]) <= 31
    m = _MON_DATE.match(t)
    if m:
        return 1 <= int(re.match(r"^\d{1,2}", t).group()) <= 31
    return False


def is_currency(s):
    """A recognized currency symbol ($ € £ ¥) adjacent to a numeric body. PROCEDURAL raw typing."""
    return bool(_CURRENCY.match(s.strip()))


def _cell_datatype(t):
    """Numeric (= is_numeric, UNCHANGED) first, then the format-decidable structured types, else Text."""
    if is_numeric(t):
        return TAB.Numeric
    if is_date(t):
        return TAB.Date
    if is_currency(t):
        return TAB.Currency
    return TAB.Text


def grid_evidence(cells, ncols):
    """Build the transient typed-cell evidence graph. `cells`: iterable of (row, col, text).
    Emits a tab:GridCell per cell (row/col/text/cellDatatype) + a column marker per index."""
    g = Graph()
    for i, (r, c, t) in enumerate(cells):
        u = _EV["cell-%d" % i]
        g.add((u, RDF.type, TAB.GridCell))
        g.add((u, TAB.atGridRow, Literal(int(r), datatype=XSD.integer)))
        g.add((u, TAB.atGridColumn, Literal(int(c), datatype=XSD.integer)))
        g.add((u, TAB.gridText, Literal(t)))
        g.add((u, TAB.cellDatatype, _cell_datatype(t)))
    for c in range(ncols):
        g.add((_EV["col-%d" % c], TAB.columnIndex, Literal(c, datatype=XSD.integer)))
    return g


def run_scalar(rq_path, graph, bindings=None):
    """Run a SELECT that returns a single integer variable; return int or None (empty result)."""
    q = Path(rq_path).read_text(encoding="utf-8")
    for row in graph.query(q, initBindings=bindings or {}):
        v = row[0]
        return int(v) if v is not None else None
    return None


def run_ask(rq_path, graph):
    """Run an ASK; return bool."""
    q = Path(rq_path).read_text(encoding="utf-8")
    return bool(graph.query(q).askAnswer)
