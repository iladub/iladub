"""The arc's four derivations (spec 2026-08-20 §5) — `vocab/queries/arc-*.rq`.

**Gate classification (CLAUDE.md §8).** The four `.rq` files are **AXIOM / derivation, open
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

Run: ./.venv/bin/python -m pytest tests/test_arc_queries.py -q
NEVER `python3` — it carries rdflib 7.1.4 and reports false reds across this repo's corpus
tests (spec §7.2.2).
"""
import re
from pathlib import Path

import pytest
from rdflib import Graph, Literal

REPO = Path(__file__).resolve().parent.parent
QUERIES = REPO / "vocab" / "queries"
MANIFEST = REPO / "tests" / "arc-manifest.ttl"
REGISTER = REPO / "docs" / "superpowers" / "residues.md"

PROG = "https://w3id.org/iladub/progress#"

# The four files and the result shape each one PROMISES. The shape is a contract with
# scripts/cockpit.py (task 8) and with any future session: a query may be rewritten, but a
# rewrite that renames or reorders a projected variable is a breaking change and this tuple
# is where it is caught.
SHAPES = {
    "arc-position.rq": ("rungKey", "met", "declared"),
    "arc-frontier.rq": ("residue", "rungKey", "criterion"),
    "arc-unblocked.rq": ("rungKey", "criterion", "statement"),
    "arc-orphan.rq": ("residue",),
}


def q(name):
    return (QUERIES / name).read_text(encoding="utf-8")


def rows(graph, name, **bindings):
    """Run one arc query and return its rows as tuples of plain strings, in query order."""
    result = graph.query(q(name), initBindings={k: Literal(v) for k, v in bindings.items()})
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


def test_arc_orphan_returns_nothing_when_there_is_no_arc():
    """The fail-safe, and it is the deriving-by-absence guard doing its job. Over a graph
    with no prog:Rung, "this residue blocks no criterion of any rung" is vacuously true — and
    answering it would declare every row in the register an orphan on the strength of a
    missing file. The positive `?rung a prog:Rung` support makes the answer empty instead,
    the same discipline `tests/test_cockpit.py:22` holds for the strip (no source -> `?`,
    never a number)."""
    assert rows(Graph(), "arc-orphan.rq", residue="R903") == []


def test_arc_orphan_unbound_returns_nothing(fixture_graph):
    """A caller that forgets to supply a residue gets nothing back, never everything. The
    query text carries no literal (adoption-candidate.rq's idiom), so the subject is the
    caller's to provide; with it unbound the inner pattern matches the fixture's own
    prog:blockedBy triples and the filter rejects."""
    assert rows(fixture_graph, "arc-orphan.rq") == []


# ------------------------------------------------------- the four sources, inspected

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
       `MINUS` group in any of the four. Met-ness is READ from the hand-asserted boolean in a
       positive triple pattern and is never concluded from something being absent — which is
       precisely the derive-by-absence CLAUDE.md §8 forbids. (`arc-position.rq`'s
       `(SUM(?one) AS ?met)` is an alias over a tally of present criteria, not a met-ness
       judgement, and it is nowhere near a negation.)

    The file set is pinned to the four so a fifth arc query cannot ship unscanned."""
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


def test_the_four_queries_keep_their_declared_result_shapes(fixture_graph):
    """The contract task 8 and every future session read. A projected variable that is
    renamed or reordered breaks a consumer silently; here it breaks a test loudly."""
    for name, shape in SHAPES.items():
        result = fixture_graph.query(q(name), initBindings={"residue": Literal("R903")})
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
