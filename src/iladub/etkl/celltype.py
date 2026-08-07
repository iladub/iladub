"""celltype — the typed-cell evidence graph + query runner (neurosymbolic loop B2a).

The type/orientation boundary decisions (header/body split, stub/data split, transpose) are
declarative DERIVATIONS over per-cell datatype facts (open-world → SPARQL, the loop-B side of the
gate). This module is the PROCEDURAL layer only: raw datatype typing (via is_numeric), emitting the
transient typed-cell evidence graph, and invoking rdflib. No decision logic, no tuned constant —
the decisions live entirely in vocab/queries/*.rq (AXIOM). Irreducible: a SPARQL engine must be
invoked from somewhere; the invocation carries no domain decision.
"""
from __future__ import annotations

import os
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
# `\d[\d,]*` (final-review deferred minor) requires >=1 digit, so a comma-only shell
# ("(,,,)") no longer matches — was `[\d,]+`. _CURRENCY keeps the wider (pre-existing)
# form; see docs/superpowers/residues.md for that residue.
_PAREN_NUMBER = re.compile(r"^\(\s*-?\d[\d,]*(\.\d+)?\s*\)$")


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


def is_paren_number(s):
    """A number wrapped in parentheses — US accounting notation for a negative. PROCEDURAL
    raw typing: a format grammar, like is_date/is_currency, with no context and no tuned
    constant. It deliberately also matches the footnote form '(1)', which is the SAME format;
    tab:ParenthesizedNumber abstains from homogeneity judgements precisely because nothing in
    the lexical form can tell the two readings apart."""
    return bool(_PAREN_NUMBER.match(s.strip()))


def is_blank(s):
    """A genuinely-missing cell: empty/whitespace, the self-declaring '(blank)', or a lone '-'.
    Minimal, self-documenting missing-value recognition (a format signal, like is_date/is_currency)
    — NOT a broad keyword list; ambiguous markers ('N/A', '0', '-5') are left to their real type."""
    t = s.strip()
    return t == "" or t.lower() == "(blank)" or t == "-"


def _cell_datatype(t):
    """Blank (missing) first, then Numeric (= is_numeric), then the format-decidable structured
    types, else Text."""
    if is_blank(t):
        return TAB.Blank
    if is_numeric(t):
        return TAB.Numeric
    if is_paren_number(t):
        return TAB.ParenthesizedNumber
    if is_date(t):
        return TAB.Date
    if is_currency(t):
        return TAB.Currency
    return TAB.Text


_VOCAB = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab")
_ONT = Graph().parse(os.path.join(_VOCAB, "ontology", "tab.ttl"), format="turtle")
# The homogeneity rules the queries read, READ from vocab/ontology/tab.ttl (the ontology is
# the published source of truth) rather than hand-duplicated — parsed ONCE at import (the
# tiling.py caching pattern: _build_tiling_shapes / _TILING_SHAPES), so there is one source,
# not two, and editing tab.ttl to add e.g. a future Percentage member changes what every band
# emits without a second edit here. Filtered to exactly the two predicates the queries read;
# datatype-declaration triples elsewhere in tab.ttl (rdf:type, rdfs:label, ...) are irrelevant.
_DATATYPE_DECLARATIONS = tuple(
    (s, p, o) for s, p, o in _ONT if p in (TAB.datatypeAbstains, TAB.inDatatypeFamily)
)


def _emit_datatype_declarations(g):
    """The homogeneity rules the queries read. Emitted into every evidence graph because that
    graph is transient and carries no ontology — without these the normalisations silently
    no-op. READS the triples cached in _DATATYPE_DECLARATIONS (parsed once from
    vocab/ontology/tab.ttl at import) rather than repeating them, so the mirror cannot drift
    silently (I1, final review)."""
    for t in _DATATYPE_DECLARATIONS:
        g.add(t)


def grid_evidence(cells, ncols, body_starts_at=1):
    """Build the transient typed-cell evidence graph. `cells`: iterable of (row, col, text).
    Emits a tab:GridCell per cell (row/col/text/cellDatatype) + a column marker per index,
    and one tab:ClassifyBand carrying tab:bodyStartsAt.

    `body_starts_at` is the first row that is BODY rather than header, derived by
    headers.header_body_split. It DEFAULTS TO 1 — the assumption the transposition oracles
    hardcoded before this parameter existed — so every caller that does not pass it behaves
    exactly as before. Note header_body_split is itself a caller: it COMPUTES the split, so
    it must never be given one, and its query does not read this term.
    """
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
    g.add((_EV["band"], RDF.type, TAB.ClassifyBand))
    g.add((_EV["band"], TAB.bodyStartsAt, Literal(int(body_starts_at), datatype=XSD.integer)))
    _emit_datatype_declarations(g)
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
