"""R289 blast-radius harness (READ-ONLY measurement; scratch only).

Monkeypatches iladub.etkl.headers.header_body_split (and every module that bound the name at
import) with a wrapper that computes OLD (the real function, unchanged) and NEW (candidate rule)
over the SAME evidence graph, logs both as JSONL, and RETURNS OLD.

NEW = smallest candidate among the per-column s_col values (header-body-split-percol.rq: same
per-column computation + same R41 filter as the shipped query) such that AT that row no DATA
column (header-body-split-datacols.rq: D != Text, >=1 non-abstaining body cell; R41 not applied)
has a non-abstaining cell whose normalised type is not one of that column's D. None if no
candidate row is clean.

usage: .venv/bin/python scripts/r289_split_blast/harness.py <corpus-relative-pdf> <out.jsonl>
One document per process, documents strictly one at a time (corpus compiles are memory-heavy).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
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
    for row, col, ct in cells:
        if col in dsets and ct not in dsets[col]:
            dirty.add(row)
    cands = sorted({s for _, _, s, _ in percol})
    old_mirror = cands[0] if cands else None
    new = next((s for s in cands if s not in dirty), None)
    return old_mirror, new, cands, sorted(dirty), percol


def wrapper(band, grid):
    old = REAL(band, grid)
    g = celltype.grid_evidence(headers._grid_cells(band, grid), grid.ncols, unshown=band.unshown)
    old_rq = celltype.run_scalar(SHIPPED_RQ, g)
    rec = {"doc": DOC, "old_final": old, "old_rq": old_rq}
    pages = sorted({w.page for ln in band.lines for w in ln.words})
    texts = [line_text(ln) for ln in band.lines]
    rec["pages"] = pages
    rec["nlines"] = len(texts)
    rec["band_key"] = hashlib.sha1(("|".join(texts) + repr(pages)).encode()).hexdigest()[:12]
    if old_rq is not None:
        om, new, cands, dirty, percol = new_split(g)
        rec.update(old_mirror=om, new=new, cands=cands, dirty=dirty,
                   percol=[(c, str(d).rsplit("#", 1)[-1], s, mr) for c, d, s, mr in percol])
        rec["lines"] = texts
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
