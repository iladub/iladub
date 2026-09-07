"""Where does an ASSERTED band's UNBOOKED ink actually GO -- into the graph, or nowhere?

Written 2026-09-07, for [[R176]]'s fork. `scripts/unbooked_ink_census.py` measures HOW MUCH ink
an asserted band books in neither score operand; this measures WHAT HAPPENED TO IT, which is the
fact the fork turns on:

  * ink covered by an emitted `tab:LabelCell`  -> the reading RECOVERED it. Booking it as
    unread would be a lie in the other direction, so under fork (a) it lands ASSERTED.
  * ink covered by an emitted `tab:EntryCell`  -> already booked; appears here only as a
    cross-check that the census' `unbooked` really is label-and-orphan ink.
  * ink covered by NO cell                     -> the reading dropped it. Under fork (a) it
    lands ESCALATED, and it is the only part of the unbooked that can push a score DOWN.

So the split printed below IS the prediction R176 § 5a asks to run: if apple p0/p1's unbooked ink
is entirely label-covered, fork (a) leaves them at 1.0 and R176's own prediction is REFUTED; if
any of it is orphan, they fall.

CONTAINMENT, and why the epsilon is not a tuned tolerance. A word is covered by a cell when its
box lies inside the cell's box. Cell bboxes are written through `Decimal(str(round(v, 2)))`
(`src/iladub/etkl/holon.py:336-339`), so a stored bound differs from the true one by at most
0.005. EPS below is 0.01 -- twice that bound, covering both ends of an interval -- and is derived
from the serialisation, not fitted to a document. Change the rounding and this number changes
with it; there is nothing to tune.

    PYTHONPATH=src python3 scripts/unbooked_ink_fate.py <pdf> <page> [<page> ...]
"""
import os
import sys
from collections import Counter

from rdflib import Graph, URIRef

TAB = "https://w3id.org/iladub/tab#"
EPS = 0.01  # exactly twice the 2-dp rounding bound in holon.py's bbox writer; see docstring


def _boxes(g: Graph, kind: str):
    """Every emitted cell of `kind`, as (x0, y0, x1, y1). Missing bbox -> skipped, counted."""
    out, missing = [], 0
    for node in g.subjects(URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                           URIRef(TAB + kind)):
        bb = g.value(node, URIRef(TAB + "hasBBox"))
        if bb is None:
            missing += 1
            continue
        vals = [g.value(bb, URIRef(TAB + a)) for a in ("x0", "y0", "x1", "y1")]
        if any(v is None for v in vals):
            missing += 1
            continue
        out.append(tuple(float(v) for v in vals))
    return out, missing


def _covered(w, boxes):
    return any(x0 - EPS <= w.x0 and w.x1 <= x1 + EPS
               and y0 - EPS <= w.top and w.bottom <= y1 + EPS
               for (x0, y0, x1, y1) in boxes)


def fate(path, page_number):
    from iladub.etkl import compile as C

    seen = []
    real = C.page_bands

    def _capture(*a, **kw):
        got = real(*a, **kw)
        seen.append(got)
        return got

    C.page_bands = _capture
    try:
        rep = C.compile_tables(path, page_number, validate_shapes=False,
                              datagrid_fallback=False)
    finally:
        C.page_bands = real
    bands = seen[0]

    entries, e_missing = _boxes(rep.graph, "EntryCell")
    labels, l_missing = _boxes(rep.graph, "LabelCell")
    print("page %d: score=%s asserted=%d escalated=%d | EntryCells=%d LabelCells=%d "
          "(no bbox: %d/%d)"
          % (page_number, rep.score, rep.asserted, rep.escalated,
             len(entries), len(labels), e_missing, l_missing))

    page_orphans = 0
    for idx, (band, r) in enumerate(zip(bands, rep.regions)):
        if r.verdict != "asserted":
            continue
        tally = Counter()
        orphan_text = []
        for ln in band.lines:
            for w in ln.words:
                if _covered(w, entries):
                    tally["entry"] += 1
                elif _covered(w, labels):
                    tally["label"] += 1
                else:
                    tally["orphan"] += 1
                    orphan_text.append(w.text)
        ink = sum(tally.values())
        booked = r.tokens_asserted + r.tokens_escalated
        print("  b%-2d %-18s ink=%-5d booked=%-5d unbooked=%-4d || entry=%-5d label=%-5d "
              "orphan=%d" % (idx, r.kind.name, ink, booked, ink - booked,
                             tally["entry"], tally["label"], tally["orphan"]))
        if orphan_text:
            print("      orphans: %s" % " ".join(orphan_text[:24]))
        page_orphans += tally["orphan"]
    # Returned so a corpus driver can derive facts ACROSS pages without re-parsing stdout.
    # `no_bbox` is the count of LabelCells this page emitted with no `tab:hasBBox` -- the ink
    # they cover is invisible to `_covered`, so it lands in `orphan` whether it was carried or
    # dropped. That confound is [[R177]]; `unbooked_ink_fate_corpus.py` pairs the two counts
    # across all 27 corpus pages, which is how [[R178]]'s population is bounded.
    return {"page": page_number, "no_bbox": l_missing, "orphans": page_orphans}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    path = argv[1]
    if not os.path.exists(path):
        print("no such pdf: %s" % path)
        return 1
    for p in argv[2:]:
        fate(path, int(p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
