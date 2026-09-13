"""Span donation — the derivation half. The query ENUMERATES; the relation disposes.

Spec: docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md § 3.1
Plan: docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md, Task 1 (DECISIONS A, B)

The relation this pins: a spanning donor band's DRAWN INTERVALS each contain a whole run of
the recipient's leaf columns, and each of the donor's labels heads the run of the interval
its ink centre falls in. Both shipped covering oracles are refuted for this reading (evidence
§ 2) -- they are ink-OVERLAP derivations over one band's own grid, and this is an INTERVAL
derivation across two bands -- so the covering is new, and it is authored on header-covers.rq's
template: geometry emitted as evidence, the decision entirely in the query.

THE FIXTURE GEOMETRY IS MEASURED, never read (plan rule 2). Donor (72, 168, 264, 360) over
recipient (72, 120, 168, 216, 264, 312, 360): `_rule_boundaries` returns the donor vector
verbatim, `recover_leaf_grid` returns the recipient's 6 columns, the donor vector is a STRICT
subset, and the covering is [(0, 1), (2, 3), (4, 5)] -- total, non-overlapping.

DECISION B's FALSIFIER IS PINNED ON THE EVIDENCE GRAPH, NOT ON A BAND, and that is a
SUBSTITUTION the plan's Task 1 Step 1 did not anticipate (plan rule 5 -- reported in the task
report). The plan asks for "a donor with a label whose ink centre lies outside its own drawn
interval". MEASURED: that donor cannot exist. `_rule_boundaries` returns a vector only when
every band word lies wholly inside some interval (grid.py, the straddle loop in
`_rule_boundaries`), and a segment inside [lo, hi) has its centre inside [lo, hi) by
arithmetic -- so a label straddling a rule, and a label beyond the last rule, BOTH make the
donor own no vector at all and be refused for a different reason entirely. The satisfiable
form carrying the same force is the one below: the QUERY, handed a label whose centre matches
no interval, must place it nowhere rather than choose a nearest. That is the claim DECISION B
actually makes, and it is the claim a future edit could break.
"""
import re

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD
from decimal import Decimal

from iladub.etkl.bands import Band
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.geometry import Line, Rule, Word

TAB = Namespace("https://w3id.org/iladub/tab#")

# MEASURED (scratch probe, this loop): the recipient reads 6 leaf columns on these 7 drawn
# boundaries, and the donor's 4 boundaries are a STRICT subset of them.
R_XS = (72.0, 120.0, 168.0, 216.0, 264.0, 312.0, 360.0)
D_XS = (72.0, 168.0, 264.0, 360.0)
#: interval i of the donor contains exactly these recipient columns -- the measured partition.
PARTITION = {0: (0, 1), 1: (2, 3), 2: (4, 5)}


def _band(xs, rows, y0=0.0, pitch=14.0, column_xs=()):
    """A ruled band. `rows` is one tuple of (text, x0, x1) per line, top to bottom."""
    lines = []
    for r, words in enumerate(rows):
        y = y0 + r * pitch
        ws = tuple(Word(text=t, x0=a, x1=b, top=y, bottom=y + 10.0) for t, a, b in words)
        lines.append(Line(words=ws, top=y, bottom=y + 10.0))
    return Band(lines=tuple(lines), top=lines[0].top, bottom=lines[-1].bottom,
                rules=tuple(Rule(x=x, top=y0, bottom=y0 + pitch * len(rows)) for x in xs),
                column_xs=column_xs)


def _cells(prefix, xs):
    """One word per leaf column of `xs`, inset so every word tiles its own column."""
    return tuple((f"{prefix}{i}", xs[i] + 4.0, xs[i] + 40.0) for i in range(len(xs) - 1))


def _recipient():
    return _band(R_XS, (_cells("a", R_XS), _cells("b", R_XS), _cells("c", R_XS)))


#: Labels centred in their own drawn interval -- the only shape a donor can have (see Q2 above).
DONOR_WORDS = (("Mackay", 100.0, 140.0), ("Gladstone", 190.0, 240.0), ("Portland", 290.0, 334.0))


def _covers(donor, recipient=None):
    from iladub.etkl.spangraph import SPAN_COVERS_RQ, run_span_covers, span_evidence

    grid = recover_leaf_grid(recipient if recipient is not None else _recipient())
    return run_span_covers(SPAN_COVERS_RQ, span_evidence(donor, grid))


def test_the_covering_is_a_total_non_overlapping_partition_of_the_recipients_columns():
    """DECISION A, on the measured geometry: each label heads the whole run of recipient
    columns inside its own drawn interval, every column is headed exactly once, and no column
    is headed twice. That is the reading the shipped oracles cannot produce (evidence § 2)."""
    got = _covers(_band(D_XS, (DONOR_WORDS,)))
    assert got == PARTITION, got

    flat = [c for cols in got.values() for c in cols]
    assert sorted(flat) == list(range(len(R_XS) - 1)), flat      # total
    assert len(flat) == len(set(flat)), flat                     # non-overlapping


def test_a_label_whose_centre_lies_in_no_interval_is_placed_nowhere():
    """DECISION B, on the EVIDENCE GRAPH -- see the module docstring for why not on a band.

    The query must REFUSE rather than choose a nearest interval. A stray label at x = 400,
    beyond the donor's last boundary, heads nothing; the labels that do sit in an interval are
    unaffected, which is what makes this a claim about selectivity and not about emptiness."""
    from iladub.etkl.spangraph import SPAN_COVERS_RQ, run_span_covers

    g = Graph()
    for i in range(len(D_XS) - 1):
        u = URIRef(f"urn:iladub:span:ivl{i}")
        g.add((u, RDF.type, TAB.SpanInterval))
        g.add((u, TAB.spanIntervalIndex, Literal(i, datatype=XSD.integer)))
        g.add((u, TAB.spanIntervalLo, Literal(Decimal(str(D_XS[i])))))
        g.add((u, TAB.spanIntervalHi, Literal(Decimal(str(D_XS[i + 1])))))
    for j in range(len(R_XS) - 1):
        u = URIRef(f"urn:iladub:span:col{j}")
        g.add((u, RDF.type, TAB.GridColumn))
        g.add((u, TAB.colIndex, Literal(j, datatype=XSD.integer)))
        g.add((u, TAB.colX0, Literal(Decimal(str(R_XS[j])))))
        g.add((u, TAB.colX1, Literal(Decimal(str(R_XS[j + 1])))))
    for k, cx in ((0, 120.0), (1, 400.0)):          # 120 sits in interval 0; 400 in none
        u = URIRef(f"urn:iladub:span:lab{k}")
        g.add((u, RDF.type, TAB.SpanLabel))
        g.add((u, TAB.spanLabelIndex, Literal(k, datatype=XSD.integer)))
        g.add((u, TAB.spanLabelText, Literal(f"L{k}")))
        g.add((u, TAB.spanLabelCenterX, Literal(Decimal(str(cx)))))

    got = run_span_covers(SPAN_COVERS_RQ, g)
    assert got == {0: (0, 1)}, got


def test_a_donor_vector_that_is_not_a_subset_leaves_a_column_headed_by_nobody():
    """Clause (d)'s shape at the derivation: a donor carrying one boundary the recipient lacks
    (200.0) cuts a recipient column in half, so no interval contains that column whole and the
    covering is no longer total. The relation refuses on the partition, not on a tolerance."""
    donor = _band((72.0, 168.0, 200.0, 264.0, 360.0),
                  ((("Mackay", 100.0, 140.0), ("Gl", 172.0, 190.0),
                    ("Gladstone", 212.0, 250.0), ("Portland", 290.0, 334.0)),))
    got = _covers(donor)
    flat = sorted(c for cols in got.values() for c in cols)
    assert flat != list(range(len(R_XS) - 1)), got
    assert 2 not in flat, got          # the column the stray boundary cuts


def test_two_labels_inside_one_interval_both_head_it():
    """The 1:1 between labels and intervals is graincorp's coincidence (9 words, 9 intervals),
    NOT a property of the relation -- so the derivation must stay correct without it. Both
    words land in interval 0 and both head its columns; the reading joins their text."""
    donor = _band(D_XS, ((("Port", 90.0, 112.0), ("Kembla", 118.0, 150.0),
                          ("Gladstone", 190.0, 240.0), ("Portland", 290.0, 334.0)),))
    got = _covers(donor)
    assert got[0] == (0, 1) and got[1] == (0, 1), got
    assert got[2] == (2, 3) and got[3] == (4, 5), got


def test_the_query_carries_no_numeric_literal():
    """Global Constraint 1, and the whole reason this derivation is AXIOM rather than a tuned
    heuristic. Containment is a comparison between two EMITTED values, both minted by the one
    inherited 2dp rounding -- there is no tolerance in the shipped diff to tune, inert or
    otherwise. The same standing property grid-donation.rq and header-covers.rq claim."""
    from tests.query_terms import _strip_comments
    from iladub.etkl.spangraph import SPAN_COVERS_RQ

    body = _strip_comments(SPAN_COVERS_RQ.read_text(encoding="utf-8"))
    body = re.sub(r"(?i)PREFIX\s+[A-Za-z]*:\s*<[^>]*>", " ", body)
    numerals = re.findall(r"(?<![A-Za-z0-9_:/#.\-])[0-9]+(?:\.[0-9]+)?(?![A-Za-z0-9_])", body)
    assert numerals == [], numerals
