"""Release gate (spec §7) — PROCEDURAL runner (CLAUDE.md §8).

Justification: irreducible orchestration — reads git tag dates (subprocess),
executes the AXIOM query, and maps its result to a process exit code. The
gating RULE lives entirely in vocab/queries/docgov-release-gate.rq; nothing
here decides what blocks.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import XSD

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

QUERY = REPO / "vocab" / "queries" / "docgov-release-gate.rq"
GOVERNANCE_ADOPTED = date(2026, 7, 31)  # spec §5.1 grandfather line — same date as the DocImpactShape cutoff (vocab/shapes/doc-governance-shapes.ttl); change both together


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=True).stdout


def _since_date(repo: Path) -> date:
    """Commit date of the previous release tag (v*), excluding tags on HEAD
    (during a release run HEAD carries the tag being built)."""
    at_head = set(_git(repo, "tag", "--points-at", "HEAD", "--list", "v*").split())
    for line in _git(repo, "for-each-ref", "--sort=-creatordate",
                     "--format=%(refname:short) %(creatordate:short)",
                     "refs/tags/v*").splitlines():
        name, _, day = line.partition(" ")
        if name and name not in at_head:
            return date.fromisoformat(day)
    return GOVERNANCE_ADOPTED


def blocking_docs(facts: Graph, since: date) -> list[str]:
    from tests.docgov_extract import DG
    out = Graph()
    for t in facts.query(QUERY.read_text(),
                         initBindings={"since": Literal(since, datatype=XSD.date)}):
        out.add(t)
    docs = [str(next(facts.objects(s, DG.path))) for s in
            {s for s, _, _ in out.triples((None, DG.blocksRelease, None))}]
    return sorted(docs)


def main() -> int:
    from tests.docgov_extract import extract
    since = _since_date(REPO)
    blockers = blocking_docs(extract(REPO), since)
    if blockers:
        print(f"RELEASE BLOCKED — undrained contradiction(s) since {since}:")
        for p in blockers:
            print(f"  - {p}")
        print("Fix the affected published page(s) in this release, per RELEASE.md.")
        return 1
    print(f"release gate clear (no contradiction registered since {since})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
