"""spangraph — the span-covering evidence graph + query runner (span donation, R211).

Which recipient leaf columns a spanning donor's label heads is a declarative DERIVATION over
the two bands' drawn geometry (open-world -> SPARQL; vocab/queries/span-covers.rq). This
module is the PROCEDURAL layer only: emitting the transient evidence graph and invoking
rdflib. No decision logic, no tuned constant, no tolerance — the covering decision lives
entirely in the query. The BAND PAIR is the closure boundary: a fresh Graph() per call, the
same shape headergraph.py and sectiongraph.donor_evidence keep for their own populations.

CLAUDE.md §8 CLASSIFICATION, per function:

- `span_evidence` — PROCEDURAL raw extraction: two already-computed geometries (the donor's
  leaf-boundary vector and the recipient's leaf grid) turned into typed RDF facts. It decides
  nothing. Irreducible to AXIOM because there is no evidence graph to derive over until it has
  run — it is the step that makes one; irreducible to NEURAL because nothing here is
  underdetermined: a boundary either is in the vector or is not.
- `run_span_covers` — PROCEDURAL glue over an AXIOM. It reads the query's answer and groups
  it; the relation is span-covers.rq. Mirrors `headergraph.run_covers` exactly.

ITS OWN GRAPH AND ITS OWN POPULATION, never merged with the donor-evidence graph
sectiongraph.donor_evidence builds. The two ask different questions of the same band: the
equal-count relation needs the donor's boundary COUNT, this one needs the boundaries
THEMSELVES, and tab:PageBand's rule in tab.ttl forbids reading a node under the wrong
population's query.

THE EMITTER APPLIES THE ROUNDING, and does not re-tune it: `grid._rule_boundaries` passes
`Band.column_xs` through unrounded, so both the donor's boundaries and the recipient's are
minted here at the 2dp inherited from `sectiongraph._distinct_rule_xs` — THE single rounding
site. One rounding for both sides is what lets the query compare them exactly and carry no
tolerance at all.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .bands import Band
from .grid import LeafGrid, _rule_boundaries

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:span:")       # transient per-band-pair instance namespace

SPAN_COVERS_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "span-covers.rq"


def _dec(x: float) -> Literal:
    """One 2dp xsd:decimal literal, minted the way the membrane's TYPE invariant requires —
    `Decimal(str(round(x, 2)))`, never a bare `round()`, whose `.value` stays a Python float
    (membrane.audit_literals, and R92 before it)."""
    return Literal(Decimal(str(round(float(x), 2))))


def span_evidence(donor: Band, recipient_grid: LeafGrid) -> Graph:
    """Fresh Graph() for one (donor, recipient) pair.

    Emits one `tab:SpanInterval` per interval of the donor's `grid._rule_boundaries` vector
    (index, lo, hi), one `tab:GridColumn` per recipient leaf column (index, x0, x1), and one
    `tab:SpanLabel` per WORD on the donor's line 0 (index in x order, text, ink centre).

    ONE LABEL PER WORD, and the grouping is the query's to do, not this function's. MEASURED
    on graincorp p0: the donor's line 0 carries nine `Word` objects for nine intervals, and
    'Fisherman Islands' / 'Port Kembla' each arrive as ONE word — the geometry adapter has
    already grouped them. That 1:1 is this document's coincidence and is NOT assumed: two
    words falling in one interval both head it, and the reading joins their text. Grouping the
    words BY INTERVAL here would move the containment decision out of the query and into
    Python, which is exactly what the §8 gate forbids.

    THE HONEST ABSTAIN: a donor that owns no vector (`_rule_boundaries` returns None — no
    rules, or a word straddling its own rules) emits NOTHING AT ALL, not a node with zero
    intervals. The query would read an interval-less donor as a donor that heads nothing,
    which is the right answer by luck rather than by construction; the emitter is where the
    abstain belongs, exactly as `sectiongraph.donor_evidence` and `run_evidence` place it for
    their own populations.

    A band with no lines likewise emits nothing: there is no label row to read.
    """
    g = Graph()
    vector = _rule_boundaries(donor)
    if vector is None or not donor.lines:
        return g

    for i in range(len(vector) - 1):
        u = URIRef(f"{_EV}ivl{i}")
        g.add((u, RDF.type, TAB.SpanInterval))
        g.add((u, TAB.spanIntervalIndex, Literal(i, datatype=XSD.integer)))
        g.add((u, TAB.spanIntervalLo, _dec(vector[i])))
        g.add((u, TAB.spanIntervalHi, _dec(vector[i + 1])))

    b = recipient_grid.boundaries
    for j in range(recipient_grid.ncols):
        u = URIRef(f"{_EV}col{j}")
        g.add((u, RDF.type, TAB.GridColumn))
        g.add((u, TAB.colIndex, Literal(j, datatype=XSD.integer)))
        g.add((u, TAB.colX0, _dec(b[j])))
        g.add((u, TAB.colX1, _dec(b[j + 1])))

    for k, w in enumerate(sorted(donor.lines[0].words, key=lambda w: w.x0)):
        u = URIRef(f"{_EV}lab{k}")
        g.add((u, RDF.type, TAB.SpanLabel))
        g.add((u, TAB.spanLabelIndex, Literal(k, datatype=XSD.integer)))
        g.add((u, TAB.spanLabelText, Literal(w.text)))
        # The ink centre is raw geometry (PROCEDURAL); WHICH interval contains it is the
        # query's decision, which is what keeps span-covers.rq free of numeric literals.
        g.add((u, TAB.spanLabelCenterX, _dec((float(w.x0) + float(w.x1)) / 2.0)))
    return g


def run_span_covers(rq_path, graph: Graph) -> dict[int, tuple[int, ...]]:
    """Run span-covers.rq; return {donor label index: tuple(sorted recipient column indices)}.

    Keyed by LABEL rather than by interval, deliberately: the reading needs to know which
    columns a LABEL heads, and an interval carrying no label heads nothing that could be
    asserted without inventing a header node with no ink behind it (§7). Keying by interval
    would hide exactly that case — the label map makes an unlabelled interval visible as a
    coverage gap, which is what the caller must refuse on.

    The query returns MATCHES ONLY, so a label the derivation places in no interval is absent
    from the map rather than present with an empty tuple. Absence is the refusal."""
    q = Path(rq_path).read_text(encoding="utf-8")
    out: dict[int, list[int]] = {}
    for row in graph.query(q):
        out.setdefault(int(row.labelIdx), []).append(int(row.cidx))
    return {k: tuple(sorted(v)) for k, v in out.items()}
