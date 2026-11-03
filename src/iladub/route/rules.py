"""The rule rung: written-back rules keyed by line-text hashes (document-router plan, Task 4).

AXIOM (CLAUDE.md § 8, derivation form, open world). Whether a rule fires, which lines it cites, and
every abstention (two STARTS lines on a page, a conflicted rule, two firing doctype rules that
disagree) are decided in vocab/queries/route-boundary-rule.rq and route-doctype-rule.rq. A rule only
PROPOSES: its answer is disposed by the same oracles as a model's (oracle.check_*), in the router.

PROCEDURAL glue, each piece irreducible to a query: (1) loading the .rq files and reading their rows
back into the answer dataclasses; (2) write-back, which is storage — it appends triples. Rule IRIs are
content-addressed (the cue hashes, the roles and the verdict), so "is the opposite rule already
there?" is a membership test on a name, not a judgement; finding it marks both rules
`route:conflicted true`, and the queries do the refusing. Python decides nothing about a page.

Rules hold sha256 only (`route:cueSha`), never line text — templates stay out of git. Line ids in a
reproduced answer are positions in the list passed in, counted from 0, as the oracles read them.
Write-back is never called on a held-out PDF (the router, Task 6, enforces).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

from iladub.route.lines import ROUTE, Line
from iladub.route.oracle import BoundaryAnswer, DoctypeAnswer, _QUERIES, _add_lines

RULES_PATH = Path(__file__).resolve().parents[3] / "readings" / "route" / "rules.ttl"
BOUNDARY_RULE_RQ = _QUERIES / "route-boundary-rule.rq"
DOCTYPE_RULE_RQ = _QUERIES / "route-doctype-rule.rq"

_BOUNDARY_VERDICT = {"STARTS": ROUTE.StartsOption, "CONTINUES": ROUTE.ContinuesOption}
_DOCTYPE_KIND = {"CONTRACT": ROUTE.ContractOption, "OTHER": ROUTE.NotAContractOption}
_ROLES = {ROUTE.PartyRole: "party_lines", ROUTE.CommitmentRole: "commitment_lines",
          ROUTE.OtherEvidenceRole: "other_evidence_lines"}
_KIND_OF = {v: k for k, v in _DOCTYPE_KIND.items()}


def _rows(lines: list[Line], rules: Graph, query: Path):
    g = Graph()
    g += rules
    _add_lines(g, lines)
    return list(g.query(query.read_text(encoding="utf-8")))


def rule_boundary(page_lines: list[Line], rules: Graph) -> BoundaryAnswer | None:
    rows = _rows(page_lines, rules, BOUNDARY_RULE_RQ)
    if not rows:
        return None
    verdict = {r.verdict for r in rows}
    positions = tuple(sorted(int(r.p) for r in rows))
    if verdict == {ROUTE.StartsOption}:
        return BoundaryAnswer("STARTS", positions[0], positions)
    return BoundaryAnswer("CONTINUES", None, positions)


def rule_doctype(extent: list[Line], rules: Graph) -> DoctypeAnswer | None:
    rows = _rows(extent, rules, DOCTYPE_RULE_RQ)
    if not rows:
        return None
    by_role: dict[str, list[int]] = {name: [] for name in _ROLES.values()}
    for r in rows:
        by_role[_ROLES[r.role]].append(int(r["first"]))
    typ = str(rows[0].type) if rows[0].type is not None else None
    return DoctypeAnswer(_KIND_OF[rows[0].verdict],
                         tuple(sorted(set(by_role["party_lines"]))),
                         tuple(sorted(set(by_role["commitment_lines"]))),
                         tuple(sorted(set(by_role["other_evidence_lines"]))), None, typ)


def _mark_conflicted(rules: Graph, *rule_iris: URIRef) -> None:
    for iri in rule_iris:
        rules.set((iri, ROUTE.conflicted, Literal(True, datatype=XSD.boolean)))


def _add_boundary_rule(rules: Graph, sha: str, verdict: URIRef) -> None:
    rule = ROUTE[f"boundary-rule-{sha}-{verdict.fragment}"]
    for other in _BOUNDARY_VERDICT.values():
        opposite = ROUTE[f"boundary-rule-{sha}-{other.fragment}"]
        if other != verdict and (opposite, RDF.type, ROUTE.BoundaryRule) in rules:
            _mark_conflicted(rules, rule, opposite)
    rules.add((rule, RDF.type, ROUTE.BoundaryRule))
    rules.add((rule, ROUTE.cueSha, Literal(sha)))
    rules.add((rule, ROUTE.verdict, verdict))


def write_back_boundary(answer: BoundaryAnswer, page_lines: list[Line], rules: Graph) -> None:
    """Append one hashed-cue rule per evidence line of an admitted STARTS / CONTINUES answer."""
    if answer.verdict not in _BOUNDARY_VERDICT:
        raise ValueError(f"only an admitted STARTS or CONTINUES answer is written back, not {answer.verdict}")
    verdict = _BOUNDARY_VERDICT[answer.verdict]
    cited = (answer.start_line,) if answer.verdict == "STARTS" else answer.evidence_lines
    for sha in sorted({page_lines[i].sha for i in cited}):
        _add_boundary_rule(rules, sha, verdict)


def write_back_doctype(answer: DoctypeAnswer, extent: list[Line], rules: Graph) -> None:
    """Append one rule whose cues are the (hash, role) pairs of an admitted CONTRACT / OTHER answer."""
    if answer.kind not in _DOCTYPE_KIND:
        raise ValueError(f"only an admitted CONTRACT or OTHER answer is written back, not {answer.kind}")
    cues = sorted({(extent[i].sha, role) for role, attr in
                   ((ROUTE.PartyRole, "party_lines"), (ROUTE.CommitmentRole, "commitment_lines"),
                    (ROUTE.OtherEvidenceRole, "other_evidence_lines"))
                   for i in getattr(answer, attr)}, key=lambda c: (c[0], str(c[1])))
    if not cues:
        raise ValueError("a doctype rule needs at least one cue")
    key = hashlib.sha256("\n".join(f"{role.fragment}|{sha}" for sha, role in cues).encode()).hexdigest()
    verdict = _DOCTYPE_KIND[answer.kind]
    rule = ROUTE[f"doctype-rule-{key}-{verdict.fragment}"]
    rules.add((rule, RDF.type, ROUTE.DoctypeRule))
    rules.add((rule, ROUTE.verdict, verdict))
    if answer.admitted_type is not None:
        rules.add((rule, ROUTE.admittedTypeName, Literal(answer.admitted_type)))
    for sha, role in cues:
        cue = ROUTE[f"doctype-cue-{key}-{role.fragment}-{sha}"]
        rules.add((rule, ROUTE.hasCue, cue))
        rules.add((cue, RDF.type, ROUTE.Citation))
        rules.add((cue, ROUTE.cueSha, Literal(sha)))
        rules.add((cue, ROUTE.citedAs, role))
    for other in _DOCTYPE_KIND.values():
        opposite = ROUTE[f"doctype-rule-{key}-{other.fragment}"]
        if other != verdict and (opposite, RDF.type, ROUTE.DoctypeRule) in rules:
            _mark_conflicted(rules, rule, opposite)
