"""M1 harness (READ-ONLY; scratch). Derived from scripts/r289_split_blast/harness.py.

Wraps header_body_split everywhere it is bound; computes OLD (real fn) and NEW (candidate rule)
over the same evidence graph; logs per call: caller, enclosing pdf_path/page_number (frame walk),
line texts, per-call evidence (gcells, ncols, unshown, band geometry) so M2/M3 run without a
compile. RETURNS OLD, so the compile is unchanged.

usage: .venv/bin/python harness_m1.py <corpus-relative-pdf> <out.jsonl>
"""
import hashlib
import inspect
import json
import os
import sys

import rdflib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Volumes/WD Green/dev/git/iladub"
sys.path.insert(0, os.path.join(REPO, "src"))

from iladub.etkl import headers, celltype  # noqa: E402
import iladub.etkl.matrix as m_matrix  # noqa: E402
import iladub.etkl.hierarchical as m_hier  # noqa: E402
import iladub.etkl.rowheaders as m_rowh  # noqa: E402
import iladub.etkl.segment as m_seg  # noqa: E402

REAL = headers.header_body_split
SHIPPED_RQ = os.path.join(REPO, "vocab", "queries", "header-body-split.rq")
PERCOL = os.path.join(HERE, "header-body-split-percol.rq")
DATACOLS = os.path.join(HERE, "header-body-split-datacols.rq")
CELLS = os.path.join(HERE, "cells.rq")

DOC = sys.argv[1]
OUT = open(sys.argv[2], "w")


def _q(path, g):
    return list(g.query(open(path, encoding="utf-8").read()))


def line_text(ln):
    return " ".join(w.text for w in ln.words)


def new_split(g):
    percol = [(int(r.col), r.D, int(r.s_col), int(r.maxrow)) for r in _q(PERCOL, g)]
    dsets = {}
    for r in _q(DATACOLS, g):
        dsets.setdefault(int(r.col), set()).add(r.D)
    cells = [(int(r.row), int(r.col), r.ct) for r in _q(CELLS, g)]
    dirty = set()
    dirty_cells = []
    for row, col, ct in cells:
        if col in dsets and ct not in dsets[col]:
            dirty.add(row)
            dirty_cells.append((row, col, str(ct).rsplit("#", 1)[-1]))
    cands = sorted({s for _, _, s, _ in percol})
    old_mirror = cands[0] if cands else None
    new = next((s for s in cands if s not in dirty), None)
    return old_mirror, new, cands, sorted(dirty), percol, dirty_cells, dsets


def frame_info():
    st = inspect.stack()
    # st[0] = frame_info, st[1] = wrapper, st[2] = the caller of header_body_split
    c = st[2]
    caller = f"{c.frame.f_globals.get('__name__')}.{c.function}:{c.lineno}"
    chain = [f"{f.frame.f_globals.get('__name__','?').rsplit('.',1)[-1]}.{f.function}:{f.lineno}"
             for f in st[2:12]]
    pdf = page = encl = None
    for f in st[2:]:
        if f.function == "compile_tables":
            loc = f.frame.f_locals
            pdf, page, encl = loc.get("pdf_path"), loc.get("page_number"), "compile_tables"
            break
    if pdf is None:
        for f in st[2:]:
            loc = f.frame.f_locals
            if "pdf_path" in loc and ("page_number" in loc or "p" in loc):
                pdf = loc.get("pdf_path")
                page = loc.get("page_number", loc.get("p"))
                encl = f.function
                break
    del st
    return caller, chain, pdf, page, encl


def wrapper(band, grid):
    old = REAL(band, grid)
    caller, chain, pdf, page, encl = frame_info()
    gcells = headers._grid_cells(band, grid)
    unshown = band.unshown
    g = celltype.grid_evidence(gcells, grid.ncols, unshown=unshown)
    old_rq = celltype.run_scalar(SHIPPED_RQ, g)
    rec = {"doc": DOC, "old_final": old, "old_rq": old_rq, "caller": caller, "chain": chain,
           "pdf_path": pdf, "page_number": page, "enclosing": encl}
    pages = sorted({w.page for ln in band.lines for w in ln.words})
    texts = [line_text(ln) for ln in band.lines]
    rec["pages"] = pages
    rec["nlines"] = len(texts)
    rec["band_key"] = hashlib.sha1(("|".join(texts) + repr(pages)).encode()).hexdigest()[:12]
    rec["lines"] = texts
    rec["ncols"] = grid.ncols
    if old_rq is not None:
        om, new, cands, dirty, percol, dcells, dsets = new_split(g)
        ctext = {(r, c): t for r, c, t in gcells}
        rec["dirty_cells"] = [(r, c, ct, ctext.get((r, c))) for r, c, ct in dcells]
        rec.update(old_mirror=om, new=new, cands=cands, dirty=dirty,
                   percol=[(c, str(d).rsplit("#", 1)[-1], s, mr) for c, d, s, mr in percol],
                   dsets={str(k): sorted(str(x).rsplit("#", 1)[-1] for x in v)
                          for k, v in dsets.items()})
        # evidence for M2/M3 (no recompile needed)
        rec["gcells"] = [list(x) for x in gcells]
        rec["unshown"] = [list(x) for x in unshown] if unshown else []
        rec["geom"] = {"top": band.top, "bottom": band.bottom,
                       "lines": [[[w.x0, w.x1] for w in ln.words] for ln in band.lines]}
    OUT.write(json.dumps(rec) + "\n")
    OUT.flush()
    return old


for mod in (headers, m_matrix, m_hier, m_rowh, m_seg):
    if getattr(mod, "header_body_split", None) is REAL:
        mod.header_body_split = wrapper

from iladub.etkl.document import compile_document  # noqa: E402

rep = compile_document(os.path.join(REPO, "corpus", DOC))
OUT.write(json.dumps({"doc": DOC, "done": True, "score": rep.score}) + "\n")
OUT.close()
