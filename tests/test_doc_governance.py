"""The documentation-governance lint (spec §6): PROCEDURAL extraction →
SHACL membrane (hard fail) → SPARQL derivations (evidence-staleness hard,
code-staleness warning, promotion queue report). Runs on the LIVE repo."""
import warnings
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph

from tests.docgov_extract import extract

REPO = Path(__file__).resolve().parent.parent
SHAPES = REPO / "vocab" / "shapes" / "doc-governance-shapes.ttl"
QUERIES = REPO / "vocab" / "queries"


@pytest.fixture(scope="module")
def facts() -> Graph:
    return extract(REPO)


def _construct(g: Graph, name: str) -> Graph:
    out = Graph()
    for triple in g.query((QUERIES / name).read_text()):
        out.add(triple)
    return out


def test_membrane(facts):
    """Closed world: class totality, leak boundary, nav integrity, wiki
    frontmatter, doc-impact registration."""
    conforms, _, report = validate(
        facts, shacl_graph=Graph().parse(SHAPES),
        inference="rdfs", advanced=True,
    )
    assert conforms, f"doc-governance membrane violated:\n{report}"


def test_no_wiki_page_stale_against_evidence(facts):
    stale = _construct(facts, "docgov-staleness-evidence.rq")
    assert len(stale) == 0, (
        "wiki pages stale against changed evidence (update the page + its "
        f"`updated:` date):\n{stale.serialize(format='turtle')}"
    )


def test_code_staleness_is_a_warning_not_a_gate(facts):
    stale = _construct(facts, "docgov-staleness-code.rq")
    if len(stale):
        warnings.warn(
            "wiki pages stale against cited code (non-blocking, spec §6):\n"
            + stale.serialize(format="turtle"),
            UserWarning,
        )


def test_promotion_queue_report(facts):
    queue = _construct(facts, "docgov-promotion-queue.rq")
    if len(queue):
        warnings.warn(
            f"promotion queue: {len(queue)} wiki page(s) awaiting a release "
            "(spec §5, drained at the next tag):\n"
            + queue.serialize(format="turtle"),
            UserWarning,
        )


def _undated(facts: Graph, wiki: bool) -> str:
    """Render the undated-figure findings as lines an author can act on.

    Disposition lives HERE and not in a SHACL shape, following this instrument's own
    split: `staleAgainstEvidence` is a test-side gate over a SPARQL derivation, while
    `ContradictionDrainShape` is shape-side because it validates a register's own
    integrity. A derived triple is the first kind, not the second."""
    # The derivation is a CONSTRUCT, so its triples are NOT in `facts` — query the
    # union, or this test silently passes on an empty match (which it did, once).
    g = facts + _construct(facts, "docgov-undated-figure.rq")
    rows = g.query(
        """PREFIX dg: <https://w3id.org/iladub/docgov#>
        SELECT ?path ?line ?lex ?slug (GROUP_CONCAT(?d; separator="/") AS ?dates)
        WHERE {
            ?doc dg:statesUndatedReading ?occ ; dg:path ?path ; dg:docClass ?class .
            ?occ dg:line ?line ; dg:lexical ?lex ; dg:denotesReading ?r .
            ?r dg:readingOf ?slug ; dg:readAt ?d .
            FILTER (?class %s "wiki")
        } GROUP BY ?path ?line ?lex ?slug ORDER BY ?path ?line ?lex""" % ("=" if wiki else "!=")
    )
    return "\n".join(
        f"  {r.path}:{r.line}  `{r.lex}` is a reading of {r.slug}, taken {r.dates}"
        for r in rows
    )


def test_no_wiki_page_states_an_undated_reading(facts):
    """A wiki page is a proposition and may be freely rewritten; a MEASUREMENT inside
    one may not be undated. Without a date the reader cannot tell a reading from a
    current value, and the page becomes unfalsifiable — which is how four of this
    repo's seven corpus scores came to be misquoted across eight handoffs (spec §1.4).

    The repair is to DATE THE CLAIM, never to rewrite the figure ([[R187]]): rewriting
    a loop's measured figures in place destroys the record rather than dating it. The
    date belongs in the figure's own markdown block — put it in a neighbouring block
    and this test still fails, which is the point of the block scope."""
    findings = _undated(facts, wiki=True)
    assert not findings, (
        "wiki page states a corpus reading with no date in its block — date the "
        "claim (the reading's own date, from tests/corpus-manifest.ttl), do not "
        f"rewrite the figure:\n{findings}"
    )


def test_undated_readings_outside_the_wiki_are_a_warning(facts):
    """Warning, not a gate: the extractor walks tracked MARKDOWN only, so the three
    measured defects in `.py` prose (spec §1.3) are out of reach and a hard gate here
    would assert a coverage this instrument does not have. [[R189]] carries it."""
    findings = _undated(facts, wiki=False)
    if findings:
        warnings.warn(
            "non-wiki document states an undated corpus reading (non-blocking):\n"
            + findings, UserWarning,
        )
