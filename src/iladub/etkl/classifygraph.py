"""classifygraph — the band-classification evidence graph + kind-query runner (loop B2c).

regions.classify's kind decision (NON_TABLE / UNSUPPORTED / RECORD) is a declarative
DERIVATION over a per-band evidence graph (open-world -> SPARQL; the band is the closure
boundary). This module is the PROCEDURAL layer only: geometric containment (via the
unchanged _word_in_column), emitting the transient evidence graph, and invoking rdflib.
No decision logic, no tuned constant -- the kind decision lives entirely in
vocab/queries/classify-kind.rq (AXIOM).
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD

from .bands import Band
from .grid import LeafGrid

TAB = Namespace("https://w3id.org/iladub/tab#")
_EV = Namespace("urn:iladub:evidence:")

# three dirs up from src/iladub/etkl/classifygraph.py -> repo root, then vocab/queries/
CLASSIFY_KIND_RQ = Path(__file__).resolve().parents[3] / "vocab" / "queries" / "classify-kind.rq"


def _strictly_in_column(w, boundaries):
    """The unique column index the word is strictly inside (via _word_in_column), or None."""
    # Deferred import: regions imports this module back (regions.classify calls
    # run_kind/classify_evidence), so importing _word_in_column at module load
    # time would be a circular import. Both modules are fully loaded by the
    # time any band is actually classified, so a call-time import is safe.
    from .regions import _word_in_column
    for c in range(len(boundaries) - 1):
        if _word_in_column(w, c, boundaries):
            return c
    return None


def classify_evidence(band: Band, grid: LeafGrid | None) -> Graph:
    """Emit the transient band-classification evidence graph.

    grid is None iff the band has < 2 lines (grid undefined); gridColumnCount is then 0
    and no header words are emitted -- the SPARQL derives NonTable from lineCount anyway.
    """
    g = Graph()
    b = _EV["band"]
    g.add((b, RDF.type, TAB.ClassifyBand))
    g.add((b, TAB.lineCount, Literal(len(band.lines), datatype=XSD.integer)))
    ncols = grid.ncols if grid is not None else 0
    g.add((b, TAB.gridColumnCount, Literal(int(ncols), datatype=XSD.integer)))
    if grid is not None and band.lines:
        header = band.lines[0]
        for i, w in enumerate(sorted(header.words, key=lambda w: w.x0)):
            u = _EV["hw-%d" % i]
            g.add((u, RDF.type, TAB.HeaderWord))
            g.add((u, TAB.headerWordOrder, Literal(i, datatype=XSD.integer)))
            col = _strictly_in_column(w, grid.boundaries)
            if col is not None:
                g.add((u, TAB.strictlyInColumn, Literal(col, datatype=XSD.integer)))
    return g


def run_kind(rq_path, graph):
    """Run classify-kind.rq; return (kind_iri: str, nhw: int, first_bad: int | None)."""
    q = Path(rq_path).read_text(encoding="utf-8")
    for row in graph.query(q):
        fb = row.firstBad
        return (str(row.kind), int(row.nhw), None if fb is None else int(fb))
    return (str(TAB.NonTableKind), 0, None)  # defensive: empty graph (no band)
