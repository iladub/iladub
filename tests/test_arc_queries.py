"""The arc's derivations — `vocab/queries/arc-*.rq`.

Four of them are the arc's POSITION (spec 2026-08-20 §5: position, frontier, unblocked,
orphan). Three more are its EDGES (spec 2026-08-22-the-arc-has-edges-design §6: depends,
ready, reach), added once `tests/arc-manifest.ttl` carried a criterion->criterion dependency
graph — 6 asserted edges and 22 propositions — so that *"what must land before X"* became a
derivation rather than a reading of 1200 lines of Turtle.

**Gate classification (CLAUDE.md §8).** All seven `.rq` files are **AXIOM / derivation, open
world, evidence-positive**: they grow rows from triples that are present and never infer a
fact from an absence. This module is their oracle and is **PROCEDURAL** for the ordinary
reason a test is — it runs an engine and compares answers — plus one that is specific to
`arc-orphan.rq` and is not ordinary: the residue register is a **markdown file that is not
part of the graph**, so the caller that supplies `arc-orphan.rq` its subject must read it in
Python. That is the same irreducibility `tests/test_arc_manifest.py`'s M7 states, one file
along, and it is why the live arm below reads `docs/superpowers/residues.md` directly.

**Every unit answer here is computed by hand against a small fixture**, not against
`tests/arc-manifest.ttl`, whose answer changes in every loop that authors a criterion. The
live manifest appears exactly twice: once where `arc-orphan.rq` must find R101 (spec §7.4's
measured first instance — a residue attached to no rung, *a finding, not a gap*), and once
where `arc-position.rq`'s counts are checked against an INDEPENDENT rdflib walk of the same
file. Neither pins a number that a future loop's authoring would falsify.

**THE FIXTURE IS DELIBERATELY NOT MEMBRANE-VALID.** Its criteria carry no `prog:declaredOn`,
no `prog:source`, no `prog:retrospective`, and one of them is `prog:met true` while carrying
`prog:blockedBy` — which `tests/arc-shapes.ttl`'s M8 refuses outright. That is the point: a
derivation must be correct over the graph it is HANDED, and the graphs a query is handed are
not all admitted ones. The M8-refused row is what makes `arc-frontier.rq`'s `prog:met false`
binding load-bearing rather than a duplicate of the membrane.

The 2026-08-22 edges keep that rule rather than quietly breaking it: the fixture's two
`prog:proposedDependsOn` triples carry **no `rdf:Statement` rationale node**, which M18 refuses
outright, and its `prog:dependsOn` triples were never put through A1-A4/A6 or M19's ablation.
That is again the point — `arc-depends.rq` must grade an edge by WHICH PREDICATE CARRIES IT,
because that is all a derivation can see; whether the predicate was *earned* is the membrane's
question and is enforced one file along in `tests/test_arc_manifest.py`.

Run: ./.venv/bin/python -m pytest tests/test_arc_queries.py -q
NEVER `python3` — it carries rdflib 7.1.4 and reports false reds across this repo's corpus
tests (spec §7.2.2).
"""
import re
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef

REPO = Path(__file__).resolve().parent.parent
QUERIES = REPO / "vocab" / "queries"
MANIFEST = REPO / "tests" / "arc-manifest.ttl"
REGISTER = REPO / "docs" / "superpowers" / "residues.md"

PROG = "https://w3id.org/iladub/progress#"

# The seven files and the result shape each one PROMISES. The shape is a contract with
# scripts/cockpit.py, with scripts/arc_depends.py, and with any future session: a query may be
# rewritten, but a rewrite that renames or reorders a projected variable is a breaking change
# and this tuple is where it is caught.
#
# `arc-ready.rq` carries the SAME tuple as `arc-unblocked.rq` deliberately — one consumer code
# path, two different questions over disjoint evidence (register rows vs criterion edges). The
# duplication here is the contract saying so, not an oversight; the two queries' own tests show
# them disagreeing in both directions on the fixture.
SHAPES = {
    "arc-position.rq": ("rungKey", "met", "declared"),
    "arc-frontier.rq": ("residue", "rungKey", "criterion"),
    "arc-unblocked.rq": ("rungKey", "criterion", "statement"),
    "arc-orphan.rq": ("residue",),
    "arc-depends.rq": ("dependency", "grade"),
    "arc-ready.rq": ("rungKey", "criterion", "statement"),
    "arc-reach.rq": ("residue", "gated"),
}


def q(name):
    return (QUERIES / name).read_text(encoding="utf-8")


def _term(value):
    """A caller-supplied binding, as the RDF term the query expects.

    `arc-orphan.rq`/`arc-reach.rq` take a residue, which is a PLAIN STRING from a markdown file
    that is not in the graph (that seam is the whole reason those two take their subject from
    the caller). `arc-depends.rq` takes a criterion, which IS a node of the graph and must
    arrive as a URIRef — bound as a Literal it matches nothing and the query answers "depends
    on nothing", which is the one wrong answer that looks like a right one."""
    return value if isinstance(value, (URIRef, Literal)) else Literal(value)


def rows(graph, name, **bindings):
    """Run one arc query and return its rows as tuples of plain strings, in query order."""
    result = graph.query(q(name), initBindings={k: _term(v) for k, v in bindings.items()})
    return [tuple(None if v is None else str(v) for v in r) for r in result]


# ----------------------------------------------------------------------------- the fixture
#
# Hand-built, and every expected answer below was computed from THIS text by reading it, not
# by running the query and recording what came out. Three rungs, five criteria:
#
#   etkl  — one met (etkl:01), one unmet and unblocked (etkl:02)          -> 1/2
#   tab   — one met carrying a stale blocker (tab:02, M8 would refuse),
#           one unmet with two blockers (tab:01), one unmet unblocked (tab:03)  -> 1/3
#   dec   — declared as a rung, NO criteria at all                        -> unknown (absent)
#
# Residue ids are R900+ so that nothing here can be confused with a real register row.
#
# ---- and, from the-arc-has-edges (2026-08-22), FOUR dependency edges of BOTH grades --------
#
#   etkl:02 --asserted--> etkl:01 --proposed--> tab:01
#   tab:03  --asserted--> tab:01
#   tab:03  --proposed--> etkl:01
#
# Four edges, chosen so each of the three new queries has both a positive and a negative, and
# so the three properties that would otherwise go unpinned are each pinned by ONE of them.
# NO CRITERION IS ADDED — the four position/frontier/unblocked/orphan answers above are facts
# about criteria and blockers and none of them may move when an edge appears. (If one does,
# that is a real regression in a query that should not be reading the edges at all.)
#
#   * a TWO-HOP CHAIN whose SECOND HOP IS PROPOSED (etkl:02 -> etkl:01 -> tab:01), so `?grade`
#     has something to distinguish: merge the two closures and tab:01 comes back "asserted".
#   * a node reachable BOTH WAYS: tab:01 is one asserted hop from tab:03 AND two proposed hops
#     from it (via etkl:01). It must come back ONCE, graded "asserted" — the grounded chain
#     exists. A per-path grading emits it twice.
#   * an UNMET criterion depending on an UNMET criterion (tab:03 -> tab:01), which is
#     arc-ready.rq's negative — and tab:03 is simultaneously arc-unblocked.rq's POSITIVE, which
#     is the two queries disagreeing in the direction the spec claims they can.
#   * an unmet criterion whose direct dependency is MET but whose GRAND-dependency is not
#     (etkl:02 -> etkl:01 met -> tab:01 unmet). This is the direct-vs-transitive seam: etkl:02
#     is ready on the direct reading and would vanish on a transitive one.
#
# The graph is ACYCLIC, deliberately: a cycle would make the closures true but the hand
# computation unreadable, and cycle behaviour is the membrane's question (M14 — M15 is the
# met-depends-on-unmet rule; corrected by the final review, M-2), not a query's.
FIXTURE = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prog: <https://w3id.org/iladub/progress#> .

prog:rung:etkl a prog:Rung ; prog:rungKey "etkl" ; rdfs:label "the document compiler" .
prog:rung:tab  a prog:Rung ; prog:rungKey "tab"  ; rdfs:label "reading depth" .
prog:rung:dec  a prog:Rung ; prog:rungKey "dec"  ; rdfs:label "decidability" .

prog:criterion:etkl:01 a prog:Criterion ;
    prog:ofRung "etkl" ; prog:statement "E1" ; prog:met true .
prog:criterion:etkl:02 a prog:Criterion ;
    prog:ofRung "etkl" ; prog:statement "E2" ; prog:met false .

prog:criterion:tab:01 a prog:Criterion ;
    prog:ofRung "tab" ; prog:statement "T1" ; prog:met false ;
    prog:blockedBy "R900" , "R901" .
prog:criterion:tab:02 a prog:Criterion ;
    prog:ofRung "tab" ; prog:statement "T2" ; prog:met true ;
    prog:blockedBy "R902" .
prog:criterion:tab:03 a prog:Criterion ;
    prog:ofRung "tab" ; prog:statement "T3" ; prog:met false .

prog:criterion:etkl:02 prog:dependsOn         prog:criterion:etkl:01 .
prog:criterion:etkl:01 prog:proposedDependsOn prog:criterion:tab:01 .
prog:criterion:tab:03  prog:dependsOn         prog:criterion:tab:01 .
prog:criterion:tab:03  prog:proposedDependsOn prog:criterion:etkl:01 .
"""


@pytest.fixture()
def fixture_graph():
    g = Graph()
    g.parse(data=FIXTURE, format="turtle")
    return g


def crit(rung, n):
    return f"{PROG}criterion:{rung}:{n}"


# ------------------------------------------------------------------- one test per query

def test_arc_position_counts_met_and_declared_per_rung(fixture_graph):
    """Hand-computed: etkl has 2 criteria of which etkl:01 is met; tab has 3 of which tab:02
    is met. ORDER BY ?rungKey puts etkl before tab. `dec` has none and is absent — its own
    test is below, because that absence is decision 6 and not an incidental."""
    assert rows(fixture_graph, "arc-position.rq") == [
        ("etkl", "1", "2"),
        ("tab", "1", "3"),
    ]


def test_arc_frontier_names_the_blockers_of_unmet_criteria_only(fixture_graph):
    """Hand-computed: tab:01 is unmet and names R900 and R901, so two rows, ordered by
    ?residue. tab:02 also carries a blocker (R902) but is MET, and a met criterion's blocker
    is not a frontier — it is a stale edge. R902 must not appear."""
    assert rows(fixture_graph, "arc-frontier.rq") == [
        ("R900", "tab", crit("tab", "01")),
        ("R901", "tab", crit("tab", "01")),
    ]


def test_arc_unblocked_names_unmet_criteria_that_nothing_blocks(fixture_graph):
    """Hand-computed: the unmet criteria are etkl:02, tab:01 and tab:03; of those only
    tab:01 carries a prog:blockedBy. So two rows, ordered by rung then criterion. The met
    criteria (etkl:01, tab:02) are absent whether or not anything blocks them."""
    assert rows(fixture_graph, "arc-unblocked.rq") == [
        ("etkl", crit("etkl", "02"), "E2"),
        ("tab", crit("tab", "03"), "T3"),
    ]


def test_arc_orphan_answers_only_about_the_caller_supplied_residue(fixture_graph):
    """Hand-computed. R903 is named by no criterion in the fixture -> it is an orphan and
    comes back. R900 blocks tab:01 -> no row. R902 blocks tab:02, which is met; the edge is
    stale but it EXISTS, so R902 is not an orphan — orphan-ness is about being named at all,
    and un-staling an edge is a different question (arc-frontier.rq's)."""
    assert rows(fixture_graph, "arc-orphan.rq", residue="R903") == [("R903",)]
    assert rows(fixture_graph, "arc-orphan.rq", residue="R900") == []
    assert rows(fixture_graph, "arc-orphan.rq", residue="R902") == []


# -------------------------------------------------- the three edge queries (2026-08-22)

def test_arc_depends_returns_the_full_closure_graded_by_which_predicate_carries_it(
        fixture_graph):
    """Hand-computed from the FIXTURE text, edge by edge, for two callers.

    From `etkl:02` the only outgoing edge is the asserted one to `etkl:01`; `etkl:01`'s only
    outgoing edge is the PROPOSED one to `tab:01`. So the full closure is {etkl:01, tab:01}
    and the asserted closure — `prog:dependsOn+`, which cannot traverse the second hop — is
    {etkl:01} alone. ORDER BY ?grade puts "asserted" before "proposed".

    From `tab:03` there are two outgoing edges: asserted to `tab:01`, proposed to `etkl:01`;
    and `etkl:01` reaches `tab:01` again by a proposed hop. `tab:01` is therefore reachable
    BOTH ways and must come back exactly ONCE, graded "asserted" — the grounded chain exists,
    and that is the fact. Two rows, not three."""
    assert rows(fixture_graph, "arc-depends.rq",
                criterion=URIRef(crit("etkl", "02"))) == [
        (crit("etkl", "01"), "asserted"),
        (crit("tab", "01"), "proposed"),
    ]
    assert rows(fixture_graph, "arc-depends.rq",
                criterion=URIRef(crit("tab", "03"))) == [
        (crit("tab", "01"), "asserted"),
        (crit("etkl", "01"), "proposed"),
    ]


def test_arc_depends_grade_marks_where_the_chain_stops_being_grounded(fixture_graph):
    """The one assertion the whole two-predicate vocabulary exists to make (spec §3).

    A grade column that reads "asserted" on every row has pinned NOTHING — it is the merged
    single-predicate closure wearing a label — so this test asserts the distinction directly
    rather than only through a row tuple: over `etkl:02`'s closure BOTH grades occur, and the
    node whose only route is through a `prog:proposedDependsOn` hop is the one graded
    "proposed". Merge the two closures in the query and this fails on the second assertion
    with `tab:01` labelled "asserted", which is exactly the silent mixing §3 forbids."""
    got = dict(rows(fixture_graph, "arc-depends.rq", criterion=URIRef(crit("etkl", "02"))))

    assert set(got.values()) == {"asserted", "proposed"}, (
        "arc-depends must report BOTH closures — a grade column that is constant across a "
        f"chain with a proposed hop in it distinguishes nothing; got {got!r}")
    assert got[crit("etkl", "01")] == "asserted", (
        "etkl:02 --prog:dependsOn--> etkl:01 is a grounded hop and must grade asserted")
    assert got[crit("tab", "01")] == "proposed", (
        "tab:01 is reachable from etkl:02 ONLY through etkl:01's prog:proposedDependsOn hop, "
        "so the chain stops being grounded there and the grade must say so")


def test_arc_depends_says_nothing_where_no_edge_was_read(fixture_graph):
    """Open world, evidence-positive: a criterion with no outgoing edge returns NO rows.

    `tab:01` carries no dependency edge and `tab:02` carries none either. The empty answer
    means *no dependency has been READ for this criterion* — never *this criterion depends on
    nothing*. The distinction is the reason 22 of the manifest's 28 edges are propositions.
    And with the caller's binding omitted entirely the query does not answer about one
    criterion at all, which the header states rather than leaves to be discovered."""
    assert rows(fixture_graph, "arc-depends.rq", criterion=URIRef(crit("tab", "01"))) == []
    assert rows(fixture_graph, "arc-depends.rq", criterion=URIRef(crit("tab", "02"))) == []
    assert rows(Graph(), "arc-depends.rq", criterion=URIRef(crit("etkl", "02"))) == [], (
        "over a graph with no criteria the answer must be empty, not 'depends on nothing'")


def test_arc_ready_names_unmet_criteria_whose_DIRECT_dependencies_are_all_met(fixture_graph):
    """Hand-computed. The unmet criteria are etkl:02, tab:01 and tab:03:

      etkl:02 — one direct dependency, etkl:01, which is `prog:met true`  -> READY
      tab:01  — no outgoing dependency edge at all (vacuously ready)      -> READY
      tab:03  — two direct dependencies: tab:01 (`met false`) and etkl:01 (`met true`), so
                one of the two carries no met evidence                    -> NOT ready

    Two rows, ordered by rung then criterion. The met criteria (etkl:01, tab:02) are absent
    whatever their dependencies say — this query is about work that is not done."""
    assert rows(fixture_graph, "arc-ready.rq") == [
        ("etkl", crit("etkl", "02"), "E2"),
        ("tab", crit("tab", "01"), "T1"),
    ]


def test_arc_ready_is_direct_and_not_transitive(fixture_graph):
    """Spec §6's closure decision, asserted as a property of the ANSWER and not of the text.

    `etkl:02`'s direct dependency `etkl:01` is met, so it is ready. Its GRAND-dependency
    `tab:01` is unmet — `etkl:01 --prog:proposedDependsOn--> tab:01`. A transitive reading
    would therefore drop `etkl:02`, and this test is what fails when someone makes that
    change: the two paths in the query become `+`, the answer loses its `etkl` row, and the
    holon-scoped closure CLAUDE.md §8 licenses has quietly become a claim about a chain.

    Stated the other way: this test asserts that a criterion IS reported ready while something
    it transitively needs is still missing. That is a feature of the direct reading, it is the
    cost the header names, and transitive readiness follows by iterating this query."""
    ready = [r[1] for r in rows(fixture_graph, "arc-ready.rq")]

    # the direct dependency is met ...
    assert rows(fixture_graph, "arc-depends.rq",
                criterion=URIRef(crit("etkl", "02")))[0] == (crit("etkl", "01"), "asserted")
    assert (URIRef(crit("etkl", "01")), URIRef(PROG + "met"), Literal(True)) in fixture_graph
    # ... while the grand-dependency is NOT ...
    assert (URIRef(crit("tab", "01")), URIRef(PROG + "met"), Literal(False)) in fixture_graph
    # ... and etkl:02 is ready anyway. This is the whole assertion.
    assert crit("etkl", "02") in ready, (
        "arc-ready must close over ONE criterion's own outgoing edges (CLAUDE.md §8): "
        "etkl:02's direct dependency is met, so it is ready even though the chain behind it "
        "is not — a transitive NOT EXISTS would close over a chain, which is a larger closure "
        "claim than this repo has licensed")


def test_arc_ready_requires_positive_met_evidence_and_never_infers_it_from_absence():
    """A dependency carrying NO `prog:met` triple at all must NOT count as met.

    This is the difference between the count in `arc-ready.rq` and the obvious
    `FILTER NOT EXISTS { ?c <hop> ?dep . ?dep prog:met false }`, which passes every test above
    and gets THIS one wrong. Hand-computed over a graph where `x:02` depends on `x:03` and
    `x:03` carries a statement and a type but no met boolean: `x:02` is NOT ready, because
    nothing in the graph says its dependency is done. Deriving met-ness from that silence is
    precisely what CLAUDE.md §8 forbids.

    `x:01` is in the same graph, depends on nothing, and IS ready — so an empty answer here
    could not be produced by the query simply failing to match anything."""
    g = Graph()
    g.parse(data="""
@prefix prog: <https://w3id.org/iladub/progress#> .
prog:rung:x a prog:Rung ; prog:rungKey "x" .
prog:criterion:x:01 a prog:Criterion ; prog:ofRung "x" ; prog:statement "X1" ; prog:met false .
prog:criterion:x:02 a prog:Criterion ; prog:ofRung "x" ; prog:statement "X2" ; prog:met false ;
    prog:dependsOn prog:criterion:x:03 .
prog:criterion:x:03 a prog:Criterion ; prog:ofRung "x" ; prog:statement "X3" .
""", format="turtle")

    assert rows(g, "arc-ready.rq") == [("x", crit("x", "01"), "X1")], (
        "x:02 depends on x:03, which carries NO prog:met triple; a dependency is met only "
        "where the evidence SAYS SO, never because nothing says otherwise")


def test_arc_ready_and_arc_unblocked_disagree_in_both_directions(fixture_graph):
    """Spec §6: *it is NOT arc-unblocked.rq* — same result shape, different evidence.

    Hand-computed, and the fixture is built so the disagreement runs BOTH ways at once:

      tab:01 — no dependency edges, so READY; carries R900 and R901, so NOT unblocked.
      tab:03 — nothing names it as blocked, so UNBLOCKED; depends on the unmet tab:01, so
               NOT ready.

    A rewrite that made either query read the other's evidence — say, arc-ready growing a
    `prog:blockedBy` clause — collapses one of these two assertions. The shared SHAPES tuple
    cannot catch that, because the shape would still be identical; this can."""
    ready = {r[1] for r in rows(fixture_graph, "arc-ready.rq")}
    unblocked = {r[1] for r in rows(fixture_graph, "arc-unblocked.rq")}

    assert crit("tab", "01") in ready and crit("tab", "01") not in unblocked, (
        "tab:01 has no dependency edges (ready) but two register rows name it (not unblocked)")
    assert crit("tab", "03") in unblocked and crit("tab", "03") not in ready, (
        "tab:03 is named by no register row (unblocked) but depends on the unmet tab:01 "
        "(not ready)")
    assert ready != unblocked


def test_arc_reach_counts_the_unmet_criteria_a_residue_closure_gates(fixture_graph):
    """Hand-computed. R900 blocks tab:01, which is unmet. Walking
    `(prog:dependsOn|prog:proposedDependsOn)*` BACKWARDS from tab:01 reaches, in the fixture:

      tab:01  itself (the zero-length step)                      unmet -> counted
      etkl:01 (etkl:01 --proposed--> tab:01)                     MET   -> not counted
      etkl:02 (etkl:02 --asserted--> etkl:01 --proposed--> tab:01)  unmet -> counted
      tab:03  (tab:03 --asserted--> tab:01, and again via etkl:01)  unmet -> counted, ONCE

    So three. R901 blocks the same criterion and must give the same three — a residue's reach
    is a fact about the criterion it blocks, not about how many residues share it. Note that
    etkl:01, though MET, still TRANSMITS the gating to etkl:02: the path runs over edges, not
    over met-ness, and a met criterion mid-chain does not shield its dependents."""
    assert rows(fixture_graph, "arc-reach.rq", residue="R900") == [("R900", "3")]
    assert rows(fixture_graph, "arc-reach.rq", residue="R901") == [("R901", "3")]


def test_arc_reach_answers_only_about_the_caller_supplied_residue(fixture_graph):
    """The caller-binding contract, and it is the assertion that fails if a rewrite stops
    honouring it (this file's falsification arm for arc-reach.rq).

    R900 and R901 both block tab:01, so a query that ignored its binding would return BOTH
    rows for either call — the answer would still be true and would no longer be an answer
    about anything. Each call returns exactly its own residue, and the value echoed back in
    column one is the caller's own term."""
    for residue in ("R900", "R901"):
        got = rows(fixture_graph, "arc-reach.rq", residue=residue)
        assert [r[0] for r in got] == [residue], (
            f"arc-reach must answer about {residue} alone; got {got!r}")


def test_arc_reach_reports_no_row_rather_than_zero(fixture_graph):
    """Decision 6 of the previous loop, applied here: unknown is not zero.

    Hand-computed. R902 blocks tab:02, which is MET — a met criterion's blocker is a stale
    edge and not a frontier (arc-frontier.rq's own argument, and M8 refuses the combination
    on an admitted manifest), so the reach is not `0`, it is NOT REPORTED. R903 is named by
    nothing at all and is likewise absent. A `("R902", "0")` row would licence a reading —
    *this residue gates nothing* — that the graph does not support, and it would rank a stale
    edge alongside a measured one.

    The empty graph is the fail-safe: no blocking triple, no row, so a missing manifest can
    never make every residue look harmless."""
    assert rows(fixture_graph, "arc-reach.rq", residue="R902") == []
    assert rows(fixture_graph, "arc-reach.rq", residue="R903") == []
    assert rows(Graph(), "arc-reach.rq", residue="R900") == []


# --------------------------------------------------- decision 6, and the two gate arms

def test_arc_position_counts_a_rung_with_no_criteria_as_unknown_not_zero(fixture_graph):
    """Decision 6: unknown is NOT zero. `prog:rung:dec` is a declared rung with no criteria.

    It must come back ABSENT — never as a row this consumer could render as an empty bar.
    Spec §6 requires `?` for such a rung, and §9's `0` reading is exactly what a `(dec, 0, 0)`
    row would licence, so this test asserts the absence and, separately, that NO row anywhere
    in the result carries a zero denominator. A query that grew a LEFT JOIN over the rung
    would still pass the first assertion for the wrong reason; the second catches it."""
    result = rows(fixture_graph, "arc-position.rq")
    assert "dec" not in [r[0] for r in result], (
        "a rung with no criteria must be ABSENT from arc-position (decision 6: unknown is "
        "not zero); the consumer renders `?` for what it does not find")
    assert [r for r in result if r[2] == "0"] == [], (
        "arc-position must never emit a 0 denominator — `0/0` rendered as `0` is the reading "
        "spec §9 forbids")


def test_arc_orphan_derives_nothing_about_the_residue_itself(fixture_graph):
    """The `NOT EXISTS` is holon-scoped (CLAUDE.md §8): it closes inside the query and states
    nothing about the row it selected.

    **Rewritten in fix round 1, and the reason is worth keeping.** The first version asserted
    that `Literal("R903")` was not a subject of the graph and had no predicate-objects. Both
    are STRUCTURALLY UNFALSIFIABLE: rdflib never yields a Literal as a subject, so they pass
    over every graph, including one that flagrantly violated the property they claimed to
    check. That is R106's genre exactly — *a check that is wired but says nothing, reported
    as health* — shipped inside the very loop that raised R106, which is how cheap the mistake
    is to make.

    What replaces them BITES, and the fix report shows it biting:

    1. **The answer is the caller's own term, echoed back.** Not a node minted for it, not a
       derived value about it — the identical `rdflib.Literal`. A query rewritten to return
       `IRI(CONCAT(prog:residue, ?residue))`, or a label, or a boolean verdict, fails here;
       the result-shape test would not notice, because the shape is still one column called
       `?residue`. This is the assertion that carries "derives nothing ABOUT the residue".
    2. **The graph never mentions the residue at all** — before or after. The row was selected
       while no triple in the graph names it, which is the literal statement of the seam this
       query is built around, and it fails the moment anyone "fixes" the seam by mirroring
       register rows into the graph.

    The mutation guard (`set(graph) == before`) is kept as the third assertion and is labelled
    for what it is: cheap insurance against a future rewrite, not a live check — `Graph.query`
    cannot write, so nothing available today falsifies it. The gate it was reaching for is
    enforced by `test_no_query_infers_a_fact_from_absence_of_evidence`, over the source."""
    before = set(fixture_graph)

    # Stated BEFORE the run, so it is falsifiable on its own: nothing in the graph names this
    # residue, in any position. That is the seam — the row about to come back is selected
    # while the graph holds no triple about it — and it fails the moment anyone "fixes" the
    # seam by mirroring register rows into the graph, which is the rejected design.
    assert not any(Literal("R903") in triple for triple in fixture_graph), (
        "arc-orphan answers about a residue the graph does not mention anywhere")

    got = [tuple(r) for r in fixture_graph.query(
        q("arc-orphan.rq"), initBindings={"residue": Literal("R903")})]

    assert got == [(Literal("R903"),)], (
        "arc-orphan must echo the caller's own term — a minted node or a derived value about "
        f"the residue is a fact this query may not assert; got {got!r}")
    assert isinstance(got[0][0], Literal)

    assert set(fixture_graph) == before, "a derivation must not write into the graph it reads"


# A SECOND prog:Rung node carrying a key that is already in use. `tests/arc-shapes.ttl`
# ADMITS this — M6 (`:38-41`) constrains the VALUE of prog:rungKey on each rung node and
# nothing counts the nodes, so a duplicate-key manifest validates clean (measured with
# pySHACL: `Conforms: True`). It is the membrane's gap, and closing it belongs on
# prog:RungShape as an eleventh refusal, not in a query — a derivation reports, it never
# refuses. Until that lands, the queries must survive the graph as it can actually arrive.
DUPLICATE_RUNG = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prog: <https://w3id.org/iladub/progress#> .

prog:rung:etkl  a prog:Rung ; prog:rungKey "etkl" ; rdfs:label "the document compiler" .
prog:rung:etkl2 a prog:Rung ; prog:rungKey "etkl" ; rdfs:label "the same rung, again" .

prog:criterion:etkl:01 a prog:Criterion ;
    prog:ofRung "etkl" ; prog:statement "E1" ; prog:met true .
prog:criterion:etkl:02 a prog:Criterion ;
    prog:ofRung "etkl" ; prog:statement "E2" ; prog:met false .
prog:criterion:etkl:03 a prog:Criterion ;
    prog:ofRung "etkl" ; prog:statement "E3" ; prog:met false ; prog:blockedBy "R900" .
"""


def test_a_duplicated_rung_node_does_not_double_any_count_or_row():
    """The join on `?rung a prog:Rung` is what a duplicate rung node doubles, because `COUNT`
    and `SUM` count SOLUTIONS and not criteria.

    Hand-computed over DUPLICATE_RUNG, which carries the SAME three criteria seen through TWO
    rung nodes: etkl is 1 met of 3 declared; etkl:02 is the one unmet criterion nothing
    blocks; R900 blocks etkl:03, once. Every answer below is a fact about criteria, so none of
    them may move when a second rung node appears.

    Before the fix this test measured `('etkl', '2', '6')` from arc-position and two identical
    rows from each of arc-frontier and arc-unblocked. arc-orphan was already immune (it has
    carried DISTINCT since it was written, for exactly this reason)."""
    g = Graph()
    g.parse(data=DUPLICATE_RUNG, format="turtle")

    assert rows(g, "arc-position.rq") == [("etkl", "1", "3")], (
        "a second prog:Rung node must not change the fraction — the fraction counts CRITERIA")
    assert rows(g, "arc-frontier.rq") == [("R900", "etkl", crit("etkl", "03"))]
    assert rows(g, "arc-unblocked.rq") == [("etkl", crit("etkl", "02"), "E2")]
    assert rows(g, "arc-orphan.rq", residue="R901") == [("R901",)]

    # The 2026-08-22 queries carry the same hazard for the same reason. DUPLICATE_RUNG has no
    # dependency edges, so both unmet criteria are vacuously ready — and each must appear ONCE
    # despite the doubled rung join (arc-ready.rq is the one that joins the rung; arc-reach.rq
    # deliberately does not, and its count is DISTINCT over criteria either way).
    assert rows(g, "arc-ready.rq") == [
        ("etkl", crit("etkl", "02"), "E2"),
        ("etkl", crit("etkl", "03"), "E3"),
    ], "a second prog:Rung node must not report one ready criterion as two pieces of work"
    assert rows(g, "arc-reach.rq", residue="R900") == [("R900", "1")], (
        "R900 blocks etkl:03, which nothing depends on — reach 1, not 2")


def test_arc_orphan_returns_nothing_when_there_is_no_arc():
    """The fail-safe, and it is the deriving-by-absence guard doing its job. Over a graph
    with no prog:Rung, "this residue blocks no criterion of any rung" is vacuously true — and
    answering it would declare every row in the register an orphan on the strength of a
    missing file. The positive `?rung a prog:Rung` support makes the answer empty instead,
    the same discipline `tests/test_cockpit.py:106` holds for the strip (no source -> `?`,
    never a number)."""
    assert rows(Graph(), "arc-orphan.rq", residue="R903") == []


def test_arc_orphan_unbound_returns_nothing(fixture_graph):
    """A caller that forgets to supply a residue gets nothing back, never everything. The
    query text carries no literal (adoption-candidate.rq's idiom), so the subject is the
    caller's to provide; with it unbound the inner pattern matches the fixture's own
    prog:blockedBy triples and the filter rejects."""
    assert rows(fixture_graph, "arc-orphan.rq") == []


# ------------------------------------------------------ the seven sources, inspected

def _strip_comments(text):
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def _negation_groups(body):
    """Every `NOT EXISTS {...}` / `MINUS {...}` group in `body`, brace-matched, as text."""
    out = []
    for m in re.finditer(r"\bNOT\s+EXISTS\b|\bMINUS\b", body, re.I):
        i = body.index("{", m.end())
        depth, j = 0, i
        while j < len(body):
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        assert depth == 0, f"unbalanced braces after {m.group(0)!r}"
        out.append(body[i:j + 1])
    return out


def test_no_query_infers_a_fact_from_absence_of_evidence():
    """CLAUDE.md §8, checked over the source rather than asserted in a comment.

    Two properties, and together they are what "evidence-positive" means operationally here:

    1. **Every arc query is a `SELECT`.** No `CONSTRUCT`, no SPARQL Update verb. A query that
       cannot produce a triple cannot derive a fact — its output is a selection of nodes the
       caller already has, which is the open-world half of the gate. This is also the
       enforcement of spec §9's *no auto-writing of the manifest* at the query layer, and of
       the brief's *none is a CONSTRUCT that adds prog:met*.

    2. **No negation reads met-ness.** `prog:met` never appears inside a `NOT EXISTS` or
       `MINUS` group in any of the seven. Met-ness is READ from the hand-asserted boolean in a
       positive triple pattern and is never concluded from something being absent — which is
       precisely the derive-by-absence CLAUDE.md §8 forbids. (`arc-position.rq`'s
       `(SUM(?one) AS ?met)` is an alias over a tally of present criteria, not a met-ness
       judgement, and it is nowhere near a negation.)

       **This rule survived the edge queries unchanged, and it cost something to keep.**
       `arc-ready.rq`'s question — *are this criterion's direct dependencies all met?* — is
       naturally written `FILTER NOT EXISTS { ?c <hop> ?dep . ?dep prog:met false }`, which
       trips this scan. It is also WRONG for the reason the scan exists: a dependency carrying
       no `prog:met` triple at all would be treated as met. So the query counts positive met
       evidence instead of negating over its absence (see its header, and
       `test_arc_ready_requires_positive_met_evidence_and_never_infers_it_from_absence`). The
       textual rule pointed at a real defect rather than merely inconveniencing a rewrite,
       which is the argument for leaving it exactly as strict as it was.

    The file set is pinned to the seven so an eighth arc query cannot ship unscanned."""
    found = sorted(p.name for p in QUERIES.glob("arc-*.rq"))
    assert found == sorted(SHAPES), f"unexpected arc query file set: {found}"

    forbidden = re.compile(
        r"\b(CONSTRUCT|INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|ADD|COPY|MOVE)\b", re.I)
    for name in SHAPES:
        body = _strip_comments(q(name))
        assert re.search(r"\bSELECT\b", body, re.I), f"{name}: not a SELECT query"
        bad = forbidden.search(body)
        assert bad is None, (
            f"{name}: {bad.group(0)!r} — an arc query is a selection, never a writer of "
            "facts; it may not construct or update anything")
        for group in _negation_groups(body):
            assert "prog:met" not in group, (
                f"{name}: prog:met inside a negation — met-ness would be derived from an "
                f"absence, which CLAUDE.md §8 forbids: {group!r}")


def test_every_arc_query_keeps_its_declared_result_shape(fixture_graph):
    """The contract task 8, `scripts/arc_depends.py` and every future session read. A projected
    variable that is renamed or reordered breaks a consumer silently; here it breaks a test
    loudly.

    Each query is run with the binding its header says it takes, so the shape is measured on a
    query the caller could actually have issued — a residue for the two that read the register
    seam, a criterion (as a URIRef, not a Literal) for `arc-depends.rq`, nothing for the three
    that answer about the whole arc."""
    bindings = {
        "arc-orphan.rq": {"residue": "R903"},
        "arc-reach.rq": {"residue": "R900"},
        "arc-depends.rq": {"criterion": URIRef(crit("etkl", "02"))},
    }
    for name, shape in SHAPES.items():
        result = fixture_graph.query(
            q(name),
            initBindings={k: _term(v) for k, v in bindings.get(name, {}).items()})
        assert tuple(str(v) for v in result.vars) == shape, (
            f"{name}: result shape drifted from its declared contract")


# --------------------------------------------------------------- the live-manifest arms

def _open_register_rows():
    """`{residue id -> state}` for every row of the register INDEX, which is the canonical
    list (CLAUDE.md § Deferred residues). Procedural because the register is markdown and
    not a graph — the same irreducibility M7 states in tests/test_arc_manifest.py.

    A closed row is struck (`| ~~R4~~ | closed |`), so the id pattern tolerates the tildes;
    the state column, not the strike, is what is read."""
    text = REGISTER.read_text(encoding="utf-8")
    return {m.group(1): m.group(2)
            for m in re.finditer(r"^\| *~*(R\d+)~* *\| *(open|closed) *\|", text, re.M)}


def test_arc_orphan_finds_r101_in_the_live_manifest():
    """Spec §7.4: *"R101 attaches to no rung, and that is a finding, not a gap."* The whole
    reason the fourth query exists. If this ever fails because a criterion has since named
    R101 as a blocker, that is a real change in the arc and the assertion should be RETIRED
    with that measurement recorded — not adjusted to keep passing."""
    state = _open_register_rows()
    assert state.get("R101") == "open", (
        "R101 must be an open row of the register index for this arm to mean anything; "
        f"read {state.get('R101')!r}")

    g = Graph()
    g.parse(MANIFEST, format="turtle")
    assert rows(g, "arc-orphan.rq", residue="R101") == [("R101",)], (
        "arc-orphan must report R101 as blocking no criterion of any rung (spec §7.4)")
    # And the query is not answering "orphan" to everything: a residue the manifest DOES
    # name must come back empty. R43 is named by tests/arc-manifest.ttl:1067.
    assert rows(g, "arc-orphan.rq", residue="R43") == [], (
        "R43 blocks a tab criterion and must not be reported as an orphan")


def test_arc_position_agrees_with_an_independent_count_of_the_live_manifest():
    """The query's arithmetic, checked against a walk of the same file that shares no code
    with it. Nothing here pins a NUMBER — a loop that authors a criterion moves both sides
    together — it pins that the two readings cannot disagree."""
    from rdflib import RDF, Namespace
    prog = Namespace(PROG)
    g = Graph()
    g.parse(MANIFEST, format="turtle")

    by_rung = {}
    for c in g.subjects(RDF.type, prog.Criterion):
        key = str(g.value(c, prog.ofRung))
        met, declared = by_rung.get(key, (0, 0))
        by_rung[key] = (met + (1 if bool(g.value(c, prog.met)) else 0), declared + 1)

    from_query = {r[0]: (int(r[1]), int(r[2])) for r in rows(g, "arc-position.rq")}
    assert from_query == by_rung
    assert by_rung, "the live manifest must carry criteria for this arm to mean anything"
