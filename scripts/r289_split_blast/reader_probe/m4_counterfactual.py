"""M4 (READ-ONLY; scratch): cbh end-to-end with header_body_split returning NEW instead of OLD
ONLY when the caller is iladub.etkl.hierarchical.classify_hierarchical. Other callers keep OLD.
Also wraps ruledroles.resolve_ruled_header_rows to log whether it returns None per table_uri.

usage: .venv/bin/python m4_counterfactual.py <out.json>
"""
import inspect
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Volumes/WD Green/dev/git/iladub"
sys.path.insert(0, os.path.join(REPO, "src"))
sys.argv = [sys.argv[0], "ag-trade/cbh-stem-2026-08-03.pdf", os.devnull, sys.argv[1]]

from iladub.etkl import headers, celltype, ruledroles  # noqa: E402
import iladub.etkl.matrix as m_matrix  # noqa: E402
import iladub.etkl.hierarchical as m_hier  # noqa: E402
import iladub.etkl.rowheaders as m_rowh  # noqa: E402
import iladub.etkl.segment as m_seg  # noqa: E402

REAL = headers.header_body_split
SHIPPED_RQ = os.path.join(REPO, "vocab", "queries", "header-body-split.rq")
OUTP = sys.argv[3]

# reuse new_split from the M1 harness without executing its compile
_src = open(os.path.join(HERE, "harness_m1.py"), encoding="utf-8").read()
_src = _src.split("for mod in (headers")[0].replace('OUT = open(sys.argv[2], "w")', "OUT = None")
_ns = {"__file__": os.path.join(HERE, "harness_m1.py"), "__name__": "m1lib"}
exec(compile(_src, "harness_m1_lib", "exec"), _ns)
new_split = _ns["new_split"]

LOG = {"splits": [], "ruled": []}


def wrapper(band, grid):
    old = REAL(band, grid)
    c = inspect.stack()[1]
    is_hier = (c.function == "classify_hierarchical"
               and c.frame.f_globals.get("__name__") == "iladub.etkl.hierarchical")
    if not is_hier:
        return old
    gcells = headers._grid_cells(band, grid)
    g = celltype.grid_evidence(gcells, grid.ncols, unshown=band.unshown)
    old_rq = celltype.run_scalar(SHIPPED_RQ, g)
    ret = old
    new = None
    if old_rq is not None:
        new = new_split(g)[1]
        if new is not None:
            ret = new
    LOG["splits"].append({"L0": " ".join(w.text for w in band.lines[0].words),
                          "nlines": len(band.lines), "old": old, "new": new, "returned": ret,
                          "ret_line": " ".join(w.text for w in band.lines[ret].words)
                          if ret is not None else None})
    return ret


BASELINE = os.environ.get("M4_BASELINE") == "1"   # control: no patch, same dump
if not BASELINE:
    for mod in (headers, m_matrix, m_hier, m_rowh, m_seg):
        if getattr(mod, "header_body_split", None) is REAL:
            mod.header_body_split = wrapper

REAL_RULED = ruledroles.resolve_ruled_header_rows


def ruled_wrapper(graph, hreg, band, table_uri, doc_uri, page, *a, **k):
    r = REAL_RULED(graph, hreg, band, table_uri, doc_uri, page, *a, **k)
    LOG["ruled"].append({"table_uri": str(table_uri), "page": page, "body_line": hreg.body_line,
                         "L0": " ".join(w.text for w in band.lines[0].words),
                         "returned_none": r is None})
    return r


ruledroles.resolve_ruled_header_rows = ruled_wrapper

# diagnostics: why a region does or does not tile (report text, truncated), and merge_tiling_ok
from iladub.etkl import tiling, membrane  # noqa: E402
REAL_TILES = tiling.region_tiles
LOG["tiles"] = []


def tiles_wrapper(graph):
    ok = REAL_TILES(graph)
    from rdflib import RDF as _R, Namespace as _N
    _T = _N("https://w3id.org/iladub/tab#")
    tbl = sorted(str(t) for t in graph.subjects(_R.type, None) if "#htable" in str(t)
                 and "-" not in str(t).rsplit("#", 1)[-1])
    rec = {"tables": tbl[:3], "tiles": ok}
    if not ok:
        _, txt = membrane.validate(graph, tiling._TILING_SHAPES, tiling._ONT)
        rec["report"] = txt[:3000]
    LOG["tiles"].append(rec)
    return ok


tiling.region_tiles = tiles_wrapper
REAL_MTO = headers.merge_tiling_ok
LOG["merge_tiling_ok"] = []


def mto_wrapper(tree, grid):
    r = REAL_MTO(tree, grid)
    LOG["merge_tiling_ok"].append(r)
    return r


headers.merge_tiling_ok = mto_wrapper

from rdflib import RDF, Namespace  # noqa: E402
from iladub.etkl.document import compile_document  # noqa: E402

TAB = Namespace("https://w3id.org/iladub/tab#")
rep = compile_document(os.path.join(REPO, "corpus", "ag-trade", "cbh-stem-2026-08-03.pdf"))
G = rep.graph

tables = {}
for t in set(G.subjects(TAB.hasCell, None)):
    s = str(t)
    if not re.search(r"#htable[1357]$", s):
        continue
    cells = list(G.objects(t, TAB.hasCell))
    entries = [c for c in cells if (c, RDF.type, TAB.EntryCell) in G]
    rows = {G.value(c, TAB.atRow) for c in entries}
    rows.discard(None)
    acc = [(str(c).rsplit("#", 1)[-1], str(G.value(c, TAB.cellText)))
           for c in entries if str(G.value(c, TAB.cellText)) in ("Accepted", "Completed")]
    # per row: entry texts (to see what the first carried row is)
    by_row = defaultdict(list)
    for c in entries:
        by_row[str(G.value(c, TAB.atRow)).rsplit("#", 1)[-1]].append(str(G.value(c, TAB.cellText)))
    # leaf columns and the labels of the header nodes covering them
    cols = {}
    for col in G.objects(t, TAB.hasLeafColumn):
        labs = []
        for hn in G.subjects(TAB.coversColumn, col):
            lvl = G.value(hn, TAB.headerLevel)
            lab = G.value(hn, TAB.hasLabel)
            labs.append((int(lvl) if lvl is not None else -1,
                         str(G.value(lab, TAB.cellText)) if lab is not None else None))
        cols[str(col).rsplit("#", 1)[-1]] = sorted(labs)
    tables[s] = {"n_rows": len(rows), "n_entries": len(entries), "accepted_completed": acc,
                 "rows": {k: v for k, v in sorted(by_row.items())}, "cols": cols}

regions = []
for i, pg in enumerate(rep.pages):
    for r in pg.regions:
        regions.append({"page_idx": i, "kind": str(r.kind), "verdict": r.verdict, "cells": r.cells,
                        "reason": r.reason, "anchor": r.anchor,
                        "table_uri": str(getattr(r, "table_uri", None)),
                        "ascii0": (r.ascii or "").splitlines()[:1]})
alltables = sorted({str(t) for t in G.subjects(TAB.hasCell, None)})
json.dump({"baseline": BASELINE, "score": rep.score, "tables": tables, "log": LOG,
           "regions": regions, "alltables": alltables,
           "repaired_bands": [list(map(str, x)) for x in rep.repaired_bands],
           "chains": [list(map(str, c)) for c in rep.chains]}, open(OUTP, "w"), indent=1)
print(json.dumps({"done": True, "score": rep.score, "ntables": len(tables)}))
