"""The router's two oracles: the checklist (Q-doctype) and the boundary oracle (Q-boundary).

AXIOM (CLAUDE.md § 8, derivation form, open world). Every admission is decided in
vocab/queries/route-checklist.rq and vocab/queries/route-boundary.rq — counts, distinctness, ranges,
the first-page rule and the split clauses all live there. This module is PROCEDURAL glue only: it
writes the proposer's answer and the lines it was shown as triples into a fresh per-call Graph (the
closure boundary for the queries' NOT EXISTS), runs the query, and reads the boolean back. It holds
no clause of its own; a check added here beside the query would be a defect.

Line ids in an answer are positions in the listing the proposer was shown (0-based). A position is
written as given — negative or past the end included — so that the query, not Python, refuses it. A
position cited twice is two `route:Citation`s, so the query can see the repeat.

`check_boundary_split` asks the checklist for each side first (spec: a side that fails it fails the
split) and records an admitted side as `route:admittedBy route:ChecklistOracle`; whether both sides
were admitted is still the boundary query's clause.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal as Lit

from rdflib import BNode, Graph, Literal, Namespace, RDF
from rdflib.namespace import DCTERMS, XSD

from iladub.route.lines import ROUTE, Line

DEC = Namespace("https://w3id.org/iladub/dec#")

_QUERIES = Path(__file__).resolve().parents[3] / "vocab" / "queries"
CHECKLIST_RQ = _QUERIES / "route-checklist.rq"
BOUNDARY_RQ = _QUERIES / "route-boundary.rq"

_DOCTYPE_OPTION = {
    "CONTRACT": ROUTE.ContractOption,
    "OTHER": ROUTE.NotAContractOption,
    "REFUSES": ROUTE.RefusedOption,
}
_BOUNDARY_OPTION = {
    "STARTS": ROUTE.StartsOption,
    "CONTINUES": ROUTE.ContinuesOption,
    "REFUSES": ROUTE.RefusedOption,
}


@dataclass(frozen=True)
class BoundaryAnswer:
    verdict: Lit["STARTS", "CONTINUES", "REFUSES"]
    start_line: int | None
    evidence_lines: tuple[int, ...]


@dataclass(frozen=True)
class DoctypeAnswer:
    kind: Lit["CONTRACT", "OTHER", "REFUSES"]
    party_lines: tuple[int, ...]
    commitment_lines: tuple[int, ...]
    other_evidence_lines: tuple[int, ...]
    proposed_type: str | None
    admitted_type: str | None


@dataclass(frozen=True)
class Verdict:
    admitted: bool
    reason: str


def _ask(graph: Graph, query: Path) -> bool:
    return bool(graph.query(query.read_text(encoding="utf-8")).askAnswer)


def _add_lines(g: Graph, lines: list[Line], document=None) -> list[BNode]:
    nodes = []
    for pos, ln in enumerate(lines):
        node = BNode()
        g.add((node, RDF.type, ROUTE.Line))
        g.add((node, ROUTE.listPosition, Literal(pos, datatype=XSD.integer)))
        g.add((node, ROUTE.textSha, Literal(ln.sha)))
        if document is not None:
            g.add((node, DCTERMS.isPartOf, document))
        nodes.append(node)
    return nodes


def _cite(g: Graph, answer: BNode, role, positions: Iterable[int]) -> None:
    for pos in positions:
        c = BNode()
        g.add((answer, ROUTE.cites, c))
        g.add((c, RDF.type, ROUTE.Citation))
        g.add((c, ROUTE.citedAs, role))
        g.add((c, ROUTE.listPosition, Literal(pos, datatype=XSD.integer)))


def _add_doctype_answer(g: Graph, answer: DoctypeAnswer) -> BNode:
    a = BNode()
    g.add((a, DEC.chosen, _DOCTYPE_OPTION[answer.kind]))
    _cite(g, a, ROUTE.PartyRole, answer.party_lines)
    _cite(g, a, ROUTE.CommitmentRole, answer.commitment_lines)
    _cite(g, a, ROUTE.OtherEvidenceRole, answer.other_evidence_lines)
    if answer.admitted_type is not None:
        g.add((a, ROUTE.admittedTypeName, Literal(answer.admitted_type)))
    return a


def check_doctype(answer: DoctypeAnswer, extent: list[Line], admitted_types: set[str]) -> Verdict:
    """The checklist oracle (route-checklist.rq) on one doctype answer about one extent."""
    g = Graph()
    _add_lines(g, extent)
    _add_doctype_answer(g, answer)
    for name in admitted_types:
        g.add((ROUTE.ChecklistOracle, ROUTE.admitsType, Literal(name)))
    if _ask(g, CHECKLIST_RQ):
        return Verdict(True, f"route-checklist.rq admits the {answer.kind} answer")
    return Verdict(False, f"route-checklist.rq refuses the {answer.kind} answer")


def check_boundary_local(answer: BoundaryAnswer, page_lines: list[Line], first_page: bool) -> Verdict:
    """The boundary oracle's local check (route-boundary.rq, LOCAL) on one answer about one page."""
    g = Graph()
    _add_lines(g, page_lines)
    a = BNode()
    g.add((a, DEC.chosen, _BOUNDARY_OPTION[answer.verdict]))
    if answer.start_line is not None:
        _cite(g, a, ROUTE.StartLineRole, (answer.start_line,))
    _cite(g, a, ROUTE.BoundaryEvidenceRole, answer.evidence_lines)
    if first_page:
        given = BNode()
        g.add((given, RDF.type, ROUTE.BoundaryDecision))
        g.add((given, ROUTE.rung, ROUTE.GivenRung))
    if _ask(g, BOUNDARY_RQ):
        return Verdict(True, f"route-boundary.rq admits the {answer.verdict} answer")
    return Verdict(False, f"route-boundary.rq refuses the {answer.verdict} answer")


def check_boundary_split(prev_extent: list[Line], prev_doctype: DoctypeAnswer,
                         next_extent: list[Line], next_doctype: DoctypeAnswer,
                         *, admitted_types: frozenset[str] = frozenset()) -> Verdict:
    """The boundary oracle's split check (route-boundary.rq, SPLIT): may a document start between
    these two extents? `admitted_types` is passed through to each side's checklist."""
    g = Graph()
    sides = []
    for extent, doctype in ((prev_extent, prev_doctype), (next_extent, next_doctype)):
        doc = BNode()
        g.add((doc, RDF.type, ROUTE.Document))
        nodes = _add_lines(g, extent, document=doc)
        if nodes:
            g.add((doc, ROUTE.startsAt, nodes[0]))
        a = _add_doctype_answer(g, doctype)
        g.add((a, ROUTE.aboutDocument, doc))
        side = check_doctype(doctype, extent, set(admitted_types))
        if side.admitted:
            g.add((a, ROUTE.admittedBy, ROUTE.ChecklistOracle))
        sides.append(side)
    if _ask(g, BOUNDARY_RQ):
        return Verdict(True, "route-boundary.rq admits the split")
    return Verdict(False, "route-boundary.rq refuses the split "
                          f"(previous: {sides[0].reason}; next: {sides[1].reason})")
