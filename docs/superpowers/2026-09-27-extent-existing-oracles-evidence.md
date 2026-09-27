# Evidence — no existing oracle takes table extent as its question (2026-09-27)

**Serves:** maintenance — second refuted oracle candidate for the question compiler's round 2 (table extent); it meets no criterion

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `extent-oracle-evidence` · **HEAD measured:** `2519cad` (src identical to `ddbedb4`)

**Doc impact: none.**

## The proposition

Run after `2026-09-27-extent-boxhead-count-oracle-evidence.md` refuted a boxhead count: *the oracles
that already exist, applied per extent, refuse the two wrong extents (bfs p5's page grid, cbh
`#table9`) and admit every correct one.*

## Result: REFUTED — every oracle that ran admitted both wrong extents (MEASURED)

**cbh `#table9`** — RecordTable path (`src/iladub/etkl/compile.py:1122-1250`); the band is compiled
twice, same result both times:

| oracle | ran | verdict |
|---|---|---|
| `is_multi_table_ambiguous` (compile.py:~915) | yes | "single table" |
| `classify` | yes | RECORD_TABLE, "flat single-level header" |
| `region_tiles` (compile.py:1170) | yes | admits (13 entries, 239 triples) |
| `cell_round_trips` (compile.py:1237) | yes | 26/26 pass |
| `_book_recovered_ink` (compile.py:1242) | yes | 3 asserted, 0 escalated |
| page membrane `_validate` (compile.py:1723) | yes | conforms |
| document `_seal` | yes | conforms |
| `dispose_boxhead` | no | no grid adoption on cbh |

**bfs p5 fused grid** — document adoption (compile.py:1591ff):

| oracle | ran | verdict |
|---|---|---|
| `derive_data_grid` refusals | yes | one extent: 46 rows over lines 5–59, 12 columns; T2's header is interior `RefusedRow`s, not a boundary |
| `dispose_boxhead` (boxhead.py:150) | yes | admits: block = lines 0–4 (T1's header only), 11 labels, 2 spanners; T2's header is never offered to it |
| `region_tiles`, `cell_round_trips` | no | not on the grid path |
| page `_validate` | no | the adopted graph has no RecordTable/HierarchicalTable, so the gate at compile.py:1719 skips it |
| document `_seal` | yes | conforms |

**Why.** Tiling and round-trip test a table's cells against *its own* boundaries, so a wrong extent
brings wrong boundaries and passes. On cbh's ruled re-extraction a cell is 1–2 "words" (the whole
"Stock at Port … 29/07/2026" is one), so round-trip cannot fail at that grain.
`HeaderContentConservedShape` has 0 focus nodes on the grid (no `HeaderSourceCell`).

**Scope test (MEASURED).** `region_tiles` and the full tab+dec membrane, run on the emitted grid +
boxhead for every adopted DataGrid page (bfs p5 wrong; apple p2, ons p7, ons p8; plus cbh p0): all
admit. Not vacuous — 46 `LeafRow`, 496 `EntryCell`, 11 `HeaderNode` in scope; `LeafColumn` and
`HeaderSourceCell` have 0 focus nodes. **Unmeasurable:** `dispose_boxhead` on T2's own block (no
recorded reading, not read live); INFERRED to admit, since every check is local to block and
columns.

## What it showed

- **Two readers disagree on cbh, and that disagreement is the only extent signal found.** The page
  datagrid refuses all 10 lines of `#table9` (75–84: 5 `HeterogeneousColumn/every-measure`, 4
  unplaceable, 1 no-key); each fused cbh cell spans 7 datagrid columns (stock) or 2 (dates). It is a
  disagreement, not an oracle, and not clean: bfs p6 `table2` and ons p4 `htable3` also get 0
  admitted grid lines (whether those extents are correct was not checked). It is blind to bfs, where
  the grid itself is the wrong extent.
- **bfs's only signal is T2's header as refused lines inside the grid's row range** — the
  boxhead-count signal already refuted.
- The pre-loop `region_tiles` refusal on bfs p5 is `merged_run_admissible` declining to merge bands,
  not an extent verdict.

## Consequence for the design

Table extent has **no oracle, existing or trivially re-scoped.** Every present oracle is
*self-referential*: it checks a table against the geometry the extent itself supplies. An extent
oracle must question the boundary from outside it — the one lead measured here is agreement between
two independent readers at a finer grain (row-band reader vs page datagrid), which is a proposition,
unmeasured as an oracle, with two unexamined 0-admission cases against it.

## Reproduction

Serial compiles, `BAML_LIVE` unset; scores match the prior probe (cbh 0.9095, bfs 0.9021).
`bash <scratch2>/run.sh ag-trade/cbh-stem-2026-08-03.pdf gov-stats/bfs-population-bilan-2023.pdf`
(wraps the oracles via `instr.py`, writes `instr-*.json`, 150 KB, not kept); then
`./.venv/bin/python <scratch2>/gridtiles.py` (scope test), `cbhgrid.py` and `census.py` (the
two-reader finding). Scripts follow verbatim.

### `run.sh`

```
#!/bin/bash
cd "/Volumes/WD Green/dev/git/iladub"
S2=/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/6cd0216b-5258-452e-9a86-ec4354c25f31/scratchpad2
unset BAML_LIVE
for f in "$@"; do
  n=$(basename $f .pdf)
  ./.venv/bin/python $S2/instr.py "$f" "$S2/instr-$n.json" > "$S2/log-$n.txt" 2>&1
  echo "done $n $?"; tail -2 "$S2/log-$n.txt"
done
```

### `instr.py`

```
import sys, json, time
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl import compile as C, document as D, decisionlog as DL, boxhead as BH, tiling as T, datagrid as DG
LOG=[]; ctx={"page":None,"band":None,"adopt":False,"doc":None}
def log(**k): k.update(page=ctx["page"],band=ctx["band"],adopt=ctx["adopt"]); LOG.append(k)
_ct=C.compile_tables
def ct(pdf, page_number=0, *a, **k):
    old=dict(ctx); ctx.update(page=page_number, adopt=bool(k.get("datagrid_adopt")), band=None)
    try: return _ct(pdf, page_number, *a, **k)
    finally: ctx.update(old)
C.compile_tables=ct; D.compile_tables=ct
_rb=DL.ReadingRecorder.band
def rb(self, idx): ctx["band"]=idx; return _rb(self, idx)
DL.ReadingRecorder.band=rb
_rec=DL.BandRecorder.record
def rec(self, j, options, chosen, rationale, *a, **k):
    log(ev="decision", j=j, chosen=str(chosen), why=str(rationale)[:160]); return _rec(self, j, options, chosen, rationale, *a, **k)
DL.BandRecorder.record=rec
_rt=T.region_tiles
def rt(g):
    r=_rt(g); log(ev="region_tiles", result=r, triples=len(g)); return r
T.region_tiles=rt
_crt=C.cell_round_trips
RTC={}
def crt(c,b):
    r=_crt(c,b); key=(ctx["page"],ctx["band"],ctx["adopt"]); RTC.setdefault(key,[0,0])[0 if r else 1]+=1; return r
C.cell_round_trips=crt
_bri=C._book_recovered_ink
def bri(band, booked, ext):
    r=_bri(band, booked, ext); log(ev="book_recovered_ink", asserted=r[0], escalated=r[1], band_words=sum(len(l.words) for l in band.lines), booked=len(booked)); return r
C._book_recovered_ink=bri
_db=BH.dispose_boxhead
def db(reading, lines, block, grid):
    r=_db(reading, lines, block, grid)
    log(ev="dispose_boxhead", reading=reading is not None, block=list(block), ncols=len(grid.columns), refused=r.refused, labels=len(r.labels or {}), dropped=list(r.dropped or ()), spanners=len(r.spanners or ())); return r
BH.dispose_boxhead=db
_rgb=BH.read_grid_boxhead
def rgb(pdf, p, lines, grid, reader, *a, **k):
    r=_rgb(pdf, p, lines, grid, reader, *a, **k)
    log(ev="read_grid_boxhead", refused=r.refused, labels=len(r.labels or {})); return r
BH.read_grid_boxhead=rgb
_ddg=DG.derive_data_grid
def ddg(pdf, p, *a, **k):
    g=_ddg(pdf, p, *a, **k)
    if g is not None:
        from collections import Counter
        reasons=Counter(str(v).split(":")[0].split("(")[0][:40] for v in g.refusals.values())
        log(ev="derive_data_grid", p=p, rows=len(g.rows), ncols=len(g.columns), rowrange=(min(g.rows),max(g.rows)) if g.rows else None, refusals=dict(reasons))
    else: log(ev="derive_data_grid", p=p, result=None)
    return g
DG.derive_data_grid=ddg
_v=C._validate
def v(graph, legs=("tab","dec")):
    r=_v(graph, legs); log(ev="membrane_validate", legs=list(legs), conforms=r[0], refusing=list(r[2]), text=r[1][:400] if not r[0] else ""); return r
C._validate=v; D._validate=v
_cst=D._confirm_section_total
def cst(graph, table_uri, band):
    r=_cst(graph, table_uri, band); log(ev="confirm_section_total", table=str(table_uri), result=list(r)); return r
D._confirm_section_total=cst
f=sys.argv[1]; t=time.time()
rep=D.compile_document("/Volumes/WD Green/dev/git/iladub/corpus/"+f)
out={"file":f,"score":rep.score,"secs":time.time()-t,"notes":list(getattr(rep,"notes",[])),
     "log":LOG,"roundtrip":[[list(k),v] for k,v in RTC.items()],
     "pages":[[{"i":i,"verdict":r.verdict,"anchor":r.anchor,"cells":r.cells,"uri":str(r.table_uri) if r.table_uri else None,"reason":r.reason} for i,r in enumerate(pg.regions)] for pg in rep.pages]}
json.dump(out,open(sys.argv[2],"w"),indent=1,default=str)
print(f, rep.score, out["secs"])
```

### `gridtiles.py`

```
import sys
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from rdflib import Graph, URIRef
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.datagrid import derive_data_grid, emit_data_grid
from iladub.etkl.boxhead import header_block, read_grid_boxhead, emit_boxhead, default_reader
from iladub.etkl.tiling import region_tiles, _TILING_SHAPES, _ONT
from iladub.etkl import membrane
from iladub.etkl.compile import _validate
C="/Volumes/WD Green/dev/git/iladub/corpus/"
for f,p in [("gov-stats/bfs-population-bilan-2023.pdf",5),("financial/apple-fy2026q3-statements.pdf",2),("gov-stats/ons-index-of-services-2026-02.pdf",7),("gov-stats/ons-index-of-services-2026-02.pdf",8),("ag-trade/cbh-stem-2026-08-03.pdf",0)]:
    pdf=C+f; g=derive_data_grid(pdf,p)
    lines=sorted([l for l in text_lines(extract_words(pdf,p)) if l.words], key=lambda l:l.top)
    doc=URIRef("https://example.org/x")
    s=Graph(); u=emit_data_grid(s,g,lines,doc,p)
    blk=header_block(lines,g); bh=read_grid_boxhead(pdf,p,lines,g,default_reader())
    emit_boxhead(s,u,lines,blk,bh,p)
    ok,txt=membrane.validate(s,_TILING_SHAPES,_ONT)
    full=_validate(s)
    print(f,p,"rows",len(g.rows),"ncols",len(g.columns),"boxhead",bh.refused,len(bh.labels or {}),"| region_tiles",ok,"| full tab+dec membrane",full[0],full[2])
    if not ok: print(txt[:600])
from rdflib.namespace import RDF
SH=URIRef("http://www.w3.org/ns/shacl#targetClass")
print("--- focus-node census on last graph (cbh) and bfs:")
for f,p in [("gov-stats/bfs-population-bilan-2023.pdf",5)]:
    pdf=C+f; g=derive_data_grid(pdf,p)
    lines=sorted([l for l in text_lines(extract_words(pdf,p)) if l.words], key=lambda l:l.top)
    s=Graph(); u=emit_data_grid(s,g,lines,URIRef("https://example.org/x"),p)
    blk=header_block(lines,g); bh=read_grid_boxhead(pdf,p,lines,g,default_reader()); emit_boxhead(s,u,lines,blk,bh,p)
    for shp,_,cls in _TILING_SHAPES.triples((None,SH,None)):
        print(str(shp).split("#")[-1], str(cls).split("#")[-1], len(set(s.subjects(RDF.type,cls))))
    from collections import Counter
    print(Counter(str(o).split("#")[-1] for o in s.objects(None,RDF.type)))
```

### `cbh9.py`

```
import sys
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify
from iladub.etkl.roundtrip import render_ascii
pdf="/Volumes/WD Green/dev/git/iladub/corpus/ag-trade/cbh-stem-2026-08-03.pdf"
b=page_bands(pdf,0)[9]
print("rules?", bool(getattr(b,"rules",None)), "hrules", len(getattr(b,"hrules",()) or ()), "column_xs", getattr(b,"column_xs",None))
print(render_ascii(b, 140))
r=classify(b); print(r.kind, r.grid.boundaries)
for c in r.cells: print(c.row, c.col, " ".join(w.text for w in c.words)[:90])
```

### `cbhgrid.py`

```
import sys
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.datagrid import derive_data_grid
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify
pdf="/Volumes/WD Green/dev/git/iladub/corpus/ag-trade/cbh-stem-2026-08-03.pdf"
g=derive_data_grid(pdf,0)
lines=sorted([l for l in text_lines(extract_words(pdf,0)) if l.words], key=lambda l:l.top)
b=page_bands(pdf,0)[9]; r=classify(b)
ids={id(w) for l in b.lines for w in l.words}
tops=sorted({round(l.top) for l in b.lines})
for i,l in enumerate(lines):
    if any(abs(l.top-t)<2 for t in tops):
        st="ROW" if i in g.rows else "REF:"+str(g.refusals.get(i))[:45]
        print(i, st, " ".join(w.text for w in l.words)[:100])
def col(x):
    for k,c in enumerate(g.columns):
        if c.x0<=x<c.x1: return k
for c in r.cells:
    ks={col((w.x0+w.x1)/2) for w in c.words}
    print(c.row,c.col,len(c.words),"gridcols",sorted(k for k in ks if k is not None), "unplaced" if None in ks else "")
```

### `census.py`

```
import sys, json, glob
from collections import Counter
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.datagrid import derive_data_grid
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify
C="/Volumes/WD Green/dev/git/iladub/corpus/"
for fn in sorted(glob.glob(sys.argv[1]+"/dump-*.json")):
    d=json.load(open(fn)); pdf=C+d["file"]
    for p,regs in enumerate(d["pages"]):
        ts=[r for r in regs if r["verdict"]=="asserted" and r["uri"] and not r["anchor"].endswith("DataGrid")]
        if not ts: continue
        g=derive_data_grid(pdf,p); bands=page_bands(pdf,p)
        lines=sorted([l for l in text_lines(extract_words(pdf,p)) if l.words], key=lambda l:l.top)
        for r in ts:
            b=bands[r["i"]]; tops=[l.top for l in b.lines]
            idx=[i for i,l in enumerate(lines) if any(abs(l.top-t)<1.5 for t in tops)]
            reg=classify(b)
            st=Counter(("ROW" if g and i in g.rows else ("REF:"+str(g.refusals[i]).split(":")[0][:36] if g and i in g.refusals else "none")) for i in idx[1:])
            hetero=st.get("REF:HeterogeneousColumn/every-measure",0)
            print(f"{d['file'].split('/')[1][:22]:22s} p{p} {r['uri'].split('#')[-1]:10s} ncols={len(reg.grid.boundaries)-1 if reg.grid else '-'} lines={len(idx)} {'***' if hetero else ''} {dict(st)}")
```
