# Evidence — table extent: the marks the author drew can dispose a proposal; reader agreement cannot (2026-09-27)

**Serves:** maintenance — third extent-oracle probe for the question compiler's round 2; it meets no criterion

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `extent-oracle-evidence` (PR #277) · **src measured:** `ddbedb4`

**Doc impact: none.**

It follows `2026-09-27-extent-boxhead-count-oracle-evidence.md` and
`2026-09-27-extent-existing-oracles-evidence.md`. The maintainer asked for both leads to be measured
together. Each was also asked the architecture question: **can the signal dispose an arbitrary
PROPOSED extent (e.g. one Jev proposes), or only critique the derivation's own output?**

## Lead 1 — agreement between the band reader and the page datagrid: REFUTED as an oracle

The confusion table covers all 35 derivation extents. Ground truth for the disputed extents was seen
in a render.

| | wrong | correct |
|---|---|---|
| flagged (the datagrid admits 0 of the extent's lines) | 3 — cbh `table9`, bfs p6 `table2`, ons p4 `htable3` | 0 |
| passed | 18 — bfs p6 `table3`–`table10`, the 10 WHO fragments | 10 |

- **Grid-anchored extents (4).** The band reader sees at least 4 table bands under every page grid
  (bfs p5 9, apple p2 6, ons p7 5, ons p8 4). The signal therefore flags all four, catching bfs p5
  along with 3 correct extents, or flags none.
- **A threshold is needed above 0 (MEASURED).** A share of 0 is a presence test and is untuned; any
  higher cut-off is a tuned constant. Correct extents range from 0.50 (cbh `htable7`) to 1.0. The
  fused bfs extent scores 0.79, between correct T1 (0.83) and T2 (0.90). No cut-off separates them.
- **It cannot dispose a proposal (MEASURED on hand-written proposals).**
  - The correct cbh stock table (L76–80) scores 0/5, and the correct maintenance table (L76–79)
    scores 0/4. The signal refuses the right answer exactly as it refuses `table9`.
  - Admission follows the page's modal row signature (the roster), not table identity.

## Lead 2 — marks the author drew: PARTIAL, and it covers both known failures

| doc/page | true tables (SEEN in render) | captions | rules | side-by-side separation | bounds exactly? |
|---|---|---|---|---|---|
| cbh p0 | 6 (4 rosters, stock, maintenance) | filled title bars; the stock bar spans 38.2–449.2 against its ruled grid at 38.4–449.3 | one ruled grid per table | x 449.3–543.4: 0 words, no rule crosses | yes; the disclaimer is outside every mark |
| bfs p5 | 2 | T1, T2 | top/bottom pairs 82/262 and 354/611, no sides | n/a | yes, boxhead and body exactly; captions outside |
| bfs p6 | 1 (T3) | T3 | one 4-sided box, 93–481 | n/a | yes |
| ons p4 | 1 | "Table 1:" | **none** (0 marks on the page) | n/a | caption only |
| ons p7/p8 | 1 (IOS1, "continued") | IOS1 ×2 | header rules and a bottom rule | n/a | yes; no rule at the "Percentage change" sub-blocks |
| gcap p0; graincorp-stem p0–2 | 1 each | unnumbered title | one box each | n/a | yes |
| WHO p0–2 | 1 each | unnumbered title | top/header/bottom horizontals | n/a | yes, with pairing |
| apple p0–2 | 1 each | unnumbered title | **many full-width rules inside the table** | n/a | **no** |

**False positives.**
- Apple's interior rules, if a horizontal rule were read as a boundary.
- A numbered-caption regex matching prose ("Table 1 shows…", ons p3).
- An unnumbered-caption detector firing on ons' 5 "Percentage change" sub-blocks. The rules do not
  split those sub-blocks.

**False negatives.**
- ons p4 carries no rules.
- Numbered captions exist for only 4 true tables.

**It can dispose a proposal, if the proposal carries its x-range.**
- The marks are raw page facts, extracted independently of any extent derivation.
- Exact tests that work (see the tolerance hazard below):
  - the proposal equals the word set of one box, which refuses both too-big and too-small extents;
  - the proposal contains no numbered caption;
  - the proposal does not straddle an x-range where the rules stop.

**Limits.**
- It abstains where no marks exist (ons p4).
- Horizontal-only rules must be paired into top and bottom (bfs p5, WHO).
- **Tolerance hazard:** joining rules into a box by touching fails on cbh. The maintenance table's
  left rule ends at x1 = 543.88998 and its horizontals start at x0 = 543.89, a 2e-5 pt gap. Snapping
  across that gap would need the forbidden tuned constant; use each rule's own x-extent instead of
  connectivity.
- A proposal that gives only a line range cannot express cbh's correct answer.

## Combined

Lead 2 covers both known failures:
- **cbh:** the ruled grids plus the empty gap between the side-by-side tables.
- **bfs p5:** the captions plus the paired rules.

Lead 1 adds only the ons p4 notes extent, where lead 2 abstains, and it refuses correct side-by-side
answers. **Lead 2 is the lead.** Lead 1 is a critique of the derivation, not an oracle.

## Surprises, and corrections to the earlier evidence

- **cbh's text line L75 holds three objects:** the stock title, the maintenance title and the roster
  grand total 1,951,264. **A proposal made from lines rather than words cannot be correct there.**
  This bears directly on any Jev input format.
- **ons p4's real Table 1 is not asserted at all.** Only its "Notes" list is asserted, as a
  HierarchicalTable.
- **Corrections to the two earlier evidence files:**
  - bfs p6 is table **T3** (SEEN), not "T2".
  - ons p4 `htable3` is the notes list.
  - So the "bfs p6 `table2`/ons p4 `htable3` 0-admitted" cases are both wrong extents, not false
    refusals.

**Labels.**
- **MEASURED:** the confusion table, the proposal shares, the rule census, the empty gap, the 2e-5 pt
  gap, the caption census.
- **SEEN in render:** bfs p6 = T3; ons p4 `htable3` = Notes; ons p7, WHO p0 and apple p2 are one
  table each; cbh p0 shows two boxed tables with separate title bars and a white gap between them.
- **INFERRED:** WHO p2, apple p0/p1 and graincorp-stem are one table each; not rendered.

## Reproduction

No compiles were run; the probe reuses the first probe's dumps (`scratchpad/dump-*.json`). Each
script was run from the repo root as `./.venv/bin/python <script>`, and `bash rulecomp.sh`. The
scripts and outputs follow verbatim; the PNG renders were not kept.

### `lead1.py`

```
import sys, json, glob
from collections import Counter
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.datagrid import derive_data_grid, ink_runs, absorb_unit_markers
from iladub.etkl.compile import page_bands
from iladub.etkl.regions import classify
C="/Volumes/WD Green/dev/git/iladub/corpus/"
S1="/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/6cd0216b-5258-452e-9a86-ec4354c25f31/scratchpad"
for fn in sorted(glob.glob(S1+"/dump-*.json")):
    d=json.load(open(fn)); pdf=C+d["file"]
    for p,regs in enumerate(d["pages"]):
        ts=[r for r in regs if r["verdict"]=="asserted" and r["uri"]]
        if not ts: continue
        g=derive_data_grid(pdf,p); bands=page_bands(pdf,p)
        lines=sorted([l for l in text_lines(extract_words(pdf,p)) if l.words], key=lambda l:l.top)
        def col(x):
            if not g: return None
            for k,c in enumerate(g.columns):
                if c.x0<=x<c.x1: return k
        for r in ts:
            name=r['uri'].split('#')[-1]
            if r["anchor"].endswith("DataGrid"):
                # other reader = band reader: which bands does the grid row range intersect, and their kinds
                lo,hi=lines[min(g.rows)].top,lines[max(g.rows)].bottom
                inb=[(k,classify(b).kind.name[:4],len(b.lines)) for k,b in enumerate(bands) if b.lines and b.lines[-1].top>=lo-0.1 and b.lines[0].top<=hi+0.1]
                tabl=[x for x in inb if not x[1].startswith("NON")]
                print(f"{d['file'].split('/')[1][:14]:14s} p{p} {name:12s} GRID rows={len(g.rows)} ncols={len(g.columns)} bands_in_range={len(inb)} table-kind bands={len(tabl)} {inb}")
                continue
            b=bands[r["i"]]; tops=[l.top for l in b.lines]
            idx=[i for i,l in enumerate(lines) if any(abs(l.top-t)<1.5 for t in tops)]
            adm=[i for i in idx if g and i in g.rows]
            reg=classify(b)
            span=Counter()
            if g and reg.cells:
                for c in reg.cells:
                    ks={col((w.x0+w.x1)/2) for w in c.words}
                    kk=len({k for k in ks if k is not None})
                    span["multi" if kk>1 else ("none" if kk==0 else "one")]+=1
            print(f"{d['file'].split('/')[1][:14]:14s} p{p} {name:12s} BAND{r['i']} lines={len(idx)} admitted={len(adm)} share={len(adm)/max(1,len(idx)):.2f} bandncols={len(reg.grid.boundaries)-1 if reg.grid else '-'} gridncols={len(g.columns) if g else '-'} cells={dict(span)} gridrows_page={len(g.rows) if g else 0}")
```

### `proposals.py`

```
"""Lead 1 as a DISPOSER of hand-written CORRECT extents (as a Jev proposal would name them):
share of the proposal's lines the page datagrid admits. Correct extents were fixed by rendering."""
import sys
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.datagrid import derive_data_grid
C="/Volumes/WD Green/dev/git/iladub/corpus/"
P=[("ag-trade/cbh-stem-2026-08-03.pdf",0,"stock table (correct)",76,80),
   ("ag-trade/cbh-stem-2026-08-03.pdf",0,"maintenance table (correct; shares lines)",76,79),
   ("ag-trade/cbh-stem-2026-08-03.pdf",0,"GERALDTON roster body (correct)",10,19),
   ("gov-stats/bfs-population-bilan-2023.pdf",5,"T1 boxhead+body (correct)",2,24),
   ("gov-stats/bfs-population-bilan-2023.pdf",5,"T2 boxhead+body (correct)",30,59),
   ("gov-stats/bfs-population-bilan-2023.pdf",5,"T1+T2 fused (wrong)",2,59),
   ("gov-stats/bfs-population-bilan-2023.pdf",6,"T3 whole (correct)",3,38),
   ("gov-stats/ons-index-of-services-2026-02.pdf",4,"Table 1 whole (correct)",2,30),
   ("gov-stats/ons-index-of-services-2026-02.pdf",4,"Notes list (wrong, = htable3)",31,35),
   ("health/who-wfa-boys-zscore-0-5.pdf",0,"WHO p0 whole (correct)",3,28)]
for f,p,name,a,b in P:
    g=derive_data_grid(C+f,p)
    ls=sorted([l for l in text_lines(extract_words(C+f,p)) if l.words],key=lambda l:l.top)
    idx=range(a,b+1); adm=[i for i in idx if i in g.rows]
    print(f"{f.split('/')[1][:12]} p{p} {name:42s} L{a}-{b} ({' '.join(w.text for w in ls[a].words)[:25]!r}..{' '.join(w.text for w in ls[b].words)[:25]!r}) admitted {len(adm)}/{len(idx)} = {len(adm)/len(idx):.2f}")
```

### `captions.py`

```
import sys, re, glob, pdfplumber
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
C="/Volumes/WD Green/dev/git/iladub/corpus/"
pat=re.compile(r"^(T\d+|Table\s*\d+|IOS\d+)\b")
for f in sorted(glob.glob(C+"*/*.pdf")):
    with pdfplumber.open(f) as pdf: n=len(pdf.pages)
    for p in range(n):
        ls=sorted([l for l in text_lines(extract_words(f,p)) if l.words],key=lambda l:l.top)
        hits=[(i," ".join(w.text for w in l.words)[:70]) for i,l in enumerate(ls) if pat.match(" ".join(w.text for w in l.words))]
        pc=[(i," ".join(w.text for w in l.words)[:60]) for i,l in enumerate(ls) if " ".join(w.text for w in l.words).startswith("Percentage change")]
        if hits or pc: print(f.split("/")[-1][:22], "p",p, "numbered:",hits, "| 'Percentage change' lines:",len(pc))
```

### `marks.py`

```
import sys, pdfplumber
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.datagrid import drawn_rules
C="/Volumes/WD Green/dev/git/iladub/corpus/"
f,p=sys.argv[1],int(sys.argv[2]); y0=float(sys.argv[3]) if len(sys.argv)>3 else 0; y1=float(sys.argv[4]) if len(sys.argv)>4 else 1e9
with pdfplumber.open(C+f) as pdf:
    pg=pdf.pages[p]
    cs=[((c["x0"]+c["x1"])/2,(c["top"]+c["bottom"])/2) for c in pg.chars]
    for kind,objs in (("rect",pg.rects),("line",pg.lines),("curve",pg.curves)):
        for o in objs:
            if o["bottom"]<y0 or o["top"]>y1: continue
            ink=sum(1 for cx,cy in cs if o["x0"]<=cx<=o["x1"] and o["top"]<=cy<=o["bottom"])
            print(f"{kind} x={o['x0']:.1f}-{o['x1']:.1f} y={o['top']:.1f}-{o['bottom']:.1f} w={o['x1']-o['x0']:.1f} h={o['bottom']-o['top']:.1f} ink={ink} fill={o.get('fill')} stroke={o.get('stroke')} ncol={o.get('non_stroking_color')}")
print("drawn_rules", drawn_rules(C+f,p))
```

### `probe.py`

```
import sys
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
C="/Volumes/WD Green/dev/git/iladub/corpus/"
# cbh: words in the inter-table gap, rows 681-760
pdf=C+"ag-trade/cbh-stem-2026-08-03.pdf"
ws=extract_words(pdf,0)
band=[w for w in ws if w.top>=670]
print("cbh words y>=670 in gap x 449.3-543.4:", [(w.text,round(w.x0),round(w.top)) for w in band if w.x1>449.3 and w.x0<543.4])
print("cbh words y>=670 right of 690.4:", [(w.text,round(w.x0),round(w.top)) for w in band if w.x0>690.4])
lines=sorted([l for l in text_lines(ws) if l.words],key=lambda l:l.top)
for i,l in enumerate(lines):
    if l.top>=665: print(" L",i,round(l.top),round(l.bottom), " | ".join(f"{w.text}@{w.x0:.0f}" for w in l.words)[:230])
# bfs p5 line tops vs rules
pdf=C+"gov-stats/bfs-population-bilan-2023.pdf"
lines=sorted([l for l in text_lines(extract_words(pdf,5)) if l.words],key=lambda l:l.top)
for i,l in enumerate(lines):
    print(" bfs5 L",i,round(l.top,1),round(l.bottom,1)," ".join(w.text for w in l.words)[:70])
```

### `render.py`

```
import sys, pdfplumber
C="/Volumes/WD Green/dev/git/iladub/corpus/"
f,p,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
crop=[float(x) for x in sys.argv[4].split(",")] if len(sys.argv)>4 else None
res=int(sys.argv[5]) if len(sys.argv)>5 else 110
with pdfplumber.open(C+f) as pdf:
    pg=pdf.pages[p]
    print("size",pg.width,pg.height, "rects",len(pg.rects),"lines",len(pg.lines),"curves",len(pg.curves))
    if crop: pg=pg.crop(crop)
    pg.to_image(resolution=res).save(out)
```

### `rulecomp.py`

```
"""Connected components of ink-free drawn marks (a mark = rect/line/curve containing no glyph centre,
the drawn_rules presence test), joined by STRICT bbox intersection (touching counts; no tolerance).
Reports each component's bbox and the text lines whose vertical centre lies inside it."""
import sys, pdfplumber
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
C="/Volumes/WD Green/dev/git/iladub/corpus/"
def comps(f,p):
    with pdfplumber.open(C+f) as pdf:
        pg=pdf.pages[p]
        cs=[((c["x0"]+c["x1"])/2,(c["top"]+c["bottom"])/2) for c in pg.chars]
        marks=[]
        for o in list(pg.rects)+list(pg.lines)+list(pg.curves):
            x0,x1,t,b=float(o["x0"]),float(o["x1"]),float(o["top"]),float(o["bottom"])
            if any(x0<=cx<=x1 and t<=cy<=b for cx,cy in cs): continue
            marks.append((x0,t,x1,b))
    n=len(marks); par=list(range(n))
    def fd(i):
        while par[i]!=i: par[i]=par[par[i]]; i=par[i]
        return i
    for i in range(n):
        a=marks[i]
        for j in range(i+1,n):
            c=marks[j]
            if a[0]<=c[2] and c[0]<=a[2] and a[1]<=c[3] and c[1]<=a[3]: par[fd(i)]=fd(j)
    g={}
    for i in range(n): g.setdefault(fd(i),[]).append(marks[i])
    out=[]
    for ms in g.values():
        out.append((min(m[0] for m in ms),min(m[1] for m in ms),max(m[2] for m in ms),max(m[3] for m in ms),len(ms)))
    return sorted(out,key=lambda c:(c[1],c[0]))
if __name__=="__main__":
    f,p=sys.argv[1],int(sys.argv[2])
    lines=sorted([l for l in text_lines(extract_words(C+f,p)) if l.words],key=lambda l:l.top)
    for c in comps(f,p):
        inl=[i for i,l in enumerate(lines) if c[1]<=(l.top+l.bottom)/2<=c[3] and any(c[0]<=(w.x0+w.x1)/2<=c[2] for w in l.words)]
        print(f" comp x={c[0]:.0f}-{c[2]:.0f} y={c[1]:.0f}-{c[3]:.0f} marks={c[4]} lines_inside={(inl[0],inl[-1],len(inl)) if inl else None} :: {(' '.join(w.text for w in lines[inl[0]].words)[:60]) if inl else ''}")
```

### `rulecomp.sh`

```
#!/bin/bash
cd "/Volumes/WD Green/dev/git/iladub"
S3=/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/6cd0216b-5258-452e-9a86-ec4354c25f31/scratchpad3
while read f p; do echo "=== $f p$p"; ./.venv/bin/python $S3/rulecomp.py $f $p; done <<LIST
ag-trade/cbh-stem-2026-08-03.pdf 0
gov-stats/bfs-population-bilan-2023.pdf 5
gov-stats/bfs-population-bilan-2023.pdf 6
gov-stats/ons-index-of-services-2026-02.pdf 4
gov-stats/ons-index-of-services-2026-02.pdf 7
gov-stats/ons-index-of-services-2026-02.pdf 8
financial/apple-fy2026q3-statements.pdf 0
financial/apple-fy2026q3-statements.pdf 1
financial/apple-fy2026q3-statements.pdf 2
health/who-wfa-boys-zscore-0-5.pdf 0
health/who-wfa-boys-zscore-0-5.pdf 1
health/who-wfa-boys-zscore-0-5.pdf 2
ag-trade/graincorp-capacity-2026-08-04.pdf 0
ag-trade/graincorp-stem-2026-07-31.pdf 0
ag-trade/graincorp-stem-2026-07-31.pdf 1
ag-trade/graincorp-stem-2026-07-31.pdf 2
LIST
```

### `lead1.out`

```
apple-fy2026q3 p0 mtable2      BAND2 lines=41 admitted=31 share=0.76 bandncols=3 gridncols=5 cells={} gridrows_page=31
apple-fy2026q3 p1 mtable2      BAND2 lines=40 admitted=28 share=0.70 bandncols=3 gridncols=3 cells={} gridrows_page=28
apple-fy2026q3 p2 p2-datagrid  GRID rows=29 ncols=3 bands_in_range=6 table-kind bands=6 [(2, 'UNSU', 4), (3, 'UNSU', 14), (4, 'UNSU', 7), (5, 'UNSU', 9), (6, 'RECO', 2), (7, 'UNSU', 2)]
bfs-population p5 p5-datagrid  GRID rows=46 ncols=12 bands_in_range=12 table-kind bands=9 [(3, 'RECO', 5), (4, 'RECO', 11), (5, 'RECO', 4), (6, 'NON_', 4), (7, 'NON_', 1), (8, 'UNSU', 3), (9, 'NON_', 1), (10, 'UNSU', 5), (11, 'UNSU', 5), (12, 'UNSU', 5), (13, 'UNSU', 5), (14, 'UNSU', 6)]
bfs-population p6 table2       BAND2 lines=4 admitted=0 share=0.00 bandncols=9 gridncols=9 cells={'one': 15} gridrows_page=32
bfs-population p6 table3       BAND3 lines=1 admitted=1 share=1.00 bandncols=- gridncols=9 cells={} gridrows_page=32
bfs-population p6 table4       BAND4 lines=4 admitted=4 share=1.00 bandncols=9 gridncols=9 cells={'one': 36} gridrows_page=32
bfs-population p6 table5       BAND5 lines=6 admitted=6 share=1.00 bandncols=9 gridncols=9 cells={'one': 54} gridrows_page=32
bfs-population p6 table6       BAND6 lines=4 admitted=4 share=1.00 bandncols=9 gridncols=9 cells={'one': 36} gridrows_page=32
bfs-population p6 table7       BAND7 lines=1 admitted=1 share=1.00 bandncols=- gridncols=9 cells={} gridrows_page=32
bfs-population p6 table8       BAND8 lines=8 admitted=8 share=1.00 bandncols=9 gridncols=9 cells={'one': 72} gridrows_page=32
bfs-population p6 table9       BAND9 lines=7 admitted=7 share=1.00 bandncols=9 gridncols=9 cells={'one': 63} gridrows_page=32
bfs-population p6 table10      BAND10 lines=1 admitted=1 share=1.00 bandncols=- gridncols=9 cells={} gridrows_page=32
cbh-stem-2026- p0 htable1      BAND1 lines=18 admitted=10 share=0.56 bandncols=16 gridncols=16 cells={} gridrows_page=45
cbh-stem-2026- p0 htable3      BAND3 lines=21 admitted=15 share=0.71 bandncols=16 gridncols=16 cells={} gridrows_page=45
cbh-stem-2026- p0 htable5      BAND5 lines=20 admitted=14 share=0.70 bandncols=16 gridncols=16 cells={} gridrows_page=45
cbh-stem-2026- p0 htable7      BAND7 lines=10 admitted=5 share=0.50 bandncols=16 gridncols=16 cells={} gridrows_page=45
cbh-stem-2026- p0 table9       BAND9 lines=10 admitted=0 share=0.00 bandncols=3 gridncols=16 cells={'one': 3, 'multi': 12, 'none': 1} gridrows_page=45
graincorp-capa p0 htable3      BAND3 lines=27 admitted=27 share=1.00 bandncols=16 gridncols=15 cells={'none': 2, 'one': 404} gridrows_page=27
graincorp-stem p0 htable2      BAND2 lines=61 admitted=57 share=0.93 bandncols=17 gridncols=15 cells={} gridrows_page=57
graincorp-stem p1 htable1      BAND1 lines=80 admitted=77 share=0.96 bandncols=17 gridncols=15 cells={} gridrows_page=77
graincorp-stem p2 htable1      BAND1 lines=71 admitted=68 share=0.96 bandncols=17 gridncols=15 cells={} gridrows_page=68
ons-index-of-s p4 htable3      BAND3 lines=3 admitted=0 share=0.00 bandncols=2 gridncols=6 cells={} gridrows_page=25
ons-index-of-s p7 p7-datagrid  GRID rows=46 ncols=6 bands_in_range=12 table-kind bands=5 [(4, 'RECO', 2), (5, 'UNSU', 5), (6, 'NON_', 1), (7, 'NON_', 1), (8, 'NON_', 1), (9, 'NON_', 1), (10, 'NON_', 1), (11, 'NON_', 1), (12, 'NON_', 1), (13, 'RECO', 15), (14, 'UNSU', 7), (15, 'UNSU', 17)]
ons-index-of-s p8 p8-datagrid  GRID rows=46 ncols=6 bands_in_range=5 table-kind bands=4 [(3, 'RECO', 2), (4, 'UNSU', 17), (5, 'UNSU', 17), (6, 'NON_', 1), (7, 'UNSU', 16)]
who-wfa-boys-z p0 mtable2      BAND2 lines=9 admitted=7 share=0.78 bandncols=11 gridncols=13 cells={} gridrows_page=25
who-wfa-boys-z p0 htable3      BAND3 lines=6 admitted=6 share=1.00 bandncols=12 gridncols=13 cells={} gridrows_page=25
who-wfa-boys-z p0 table4       BAND4 lines=6 admitted=6 share=1.00 bandncols=13 gridncols=13 cells={'one': 78} gridrows_page=25
who-wfa-boys-z p0 htable5      BAND5 lines=6 admitted=6 share=1.00 bandncols=12 gridncols=13 cells={} gridrows_page=25
who-wfa-boys-z p1 mtable2      BAND2 lines=8 admitted=6 share=0.75 bandncols=11 gridncols=13 cells={} gridrows_page=24
who-wfa-boys-z p1 htable3      BAND3 lines=6 admitted=6 share=1.00 bandncols=12 gridncols=13 cells={} gridrows_page=24
who-wfa-boys-z p1 table4       BAND4 lines=6 admitted=6 share=1.00 bandncols=13 gridncols=13 cells={'one': 78} gridrows_page=24
who-wfa-boys-z p1 htable5      BAND5 lines=6 admitted=6 share=1.00 bandncols=12 gridncols=13 cells={} gridrows_page=24
who-wfa-boys-z p2 mtable1      BAND1 lines=8 admitted=6 share=0.75 bandncols=11 gridncols=13 cells={} gridrows_page=12
who-wfa-boys-z p2 htable2      BAND2 lines=6 admitted=6 share=1.00 bandncols=12 gridncols=13 cells={} gridrows_page=12
```

### `rulecomp.out`

```
=== ag-trade/cbh-stem-2026-08-03.pdf p0
 comp x=38-1152 y=105-200 marks=33 lines_inside=(7, 19, 13) :: Time Nom Date Nom Date Loading Time Loading
 comp x=797-847 y=208-208 marks=1 lines_inside=None :: 
 comp x=797-847 y=216-217 marks=1 lines_inside=None :: 
 comp x=38-1152 y=241-384 marks=39 lines_inside=(23, 41, 19) :: Time Nom Date Nom Date Loading Time Loading
 comp x=797-847 y=392-392 marks=1 lines_inside=None :: 
 comp x=797-847 y=400-401 marks=1 lines_inside=None :: 
 comp x=38-1152 y=434-561 marks=37 lines_inside=(46, 62, 17) :: Time Nom Date Nom Date Loading Time Loading
 comp x=797-847 y=569-569 marks=1 lines_inside=None :: 
 comp x=797-847 y=577-578 marks=1 lines_inside=None :: 
 comp x=38-1152 y=602-656 marks=28 lines_inside=(66, 73, 8) :: Time Nom Date Nom Date Loading Time Loading
 comp x=797-847 y=664-665 marks=1 lines_inside=None :: 
 comp x=797-847 y=673-674 marks=1 lines_inside=None :: 
 comp x=797-847 y=681-682 marks=1 lines_inside=None :: 
 comp x=797-847 y=689-690 marks=1 lines_inside=None :: 
 comp x=543-544 y=690-722 marks=1 lines_inside=None :: 
 comp x=38-449 y=690-731 marks=14 lines_inside=(76, 80, 5) :: PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL ALB 1
 comp x=544-690 y=690-722 marks=7 lines_inside=(76, 79, 4) :: PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL ALB 1
=== gov-stats/bfs-population-bilan-2023.pdf p5
 comp x=71-524 y=82-82 marks=1 lines_inside=None :: 
 comp x=71-524 y=82-82 marks=1 lines_inside=None :: 
 comp x=71-524 y=82-110 marks=28 lines_inside=(2, 4, 3) :: État de laComposantes de l'évolution de la population État d
 comp x=71-524 y=262-262 marks=2 lines_inside=None :: 
 comp x=71-524 y=354-354 marks=1 lines_inside=None :: 
 comp x=71-524 y=354-377 marks=27 lines_inside=(30, 32, 3) :: Cantons État de la Composantes de l'évolution de la populati
 comp x=71-524 y=611-611 marks=2 lines_inside=None :: 
=== gov-stats/bfs-population-bilan-2023.pdf p6
 comp x=71-524 y=93-93 marks=1 lines_inside=None :: 
 comp x=71-524 y=93-491 marks=33 lines_inside=(3, 39, 37) :: Grandes régions Total 0-19 ans 20-39 ans 40-64 ans 65-79 ans
=== gov-stats/ons-index-of-services-2026-02.pdf p4
=== gov-stats/ons-index-of-services-2026-02.pdf p7
 comp x=54-507 y=93-94 marks=1 lines_inside=None :: 
 comp x=164-507 y=104-104 marks=1 lines_inside=None :: 
 comp x=54-507 y=145-145 marks=1 lines_inside=None :: 
 comp x=54-507 y=154-154 marks=1 lines_inside=None :: 
 comp x=164-507 y=163-163 marks=1 lines_inside=None :: 
 comp x=54-540 y=588-589 marks=1 lines_inside=None :: 
 comp x=390-540 y=596-604 marks=1 lines_inside=None :: 
 comp x=62-113 y=655-655 marks=1 lines_inside=None :: 
=== gov-stats/ons-index-of-services-2026-02.pdf p8
 comp x=54-454 y=98-99 marks=1 lines_inside=None :: 
 comp x=153-454 y=105-106 marks=1 lines_inside=None :: 
 comp x=54-454 y=147-147 marks=1 lines_inside=None :: 
 comp x=54-454 y=155-156 marks=1 lines_inside=None :: 
 comp x=153-454 y=163-164 marks=1 lines_inside=None :: 
 comp x=54-491 y=587-588 marks=1 lines_inside=None :: 
 comp x=386-491 y=595-602 marks=1 lines_inside=None :: 
 comp x=62-113 y=653-653 marks=1 lines_inside=None :: 
=== financial/apple-fy2026q3-statements.pdf p0
 comp x=303-431 y=104-105 marks=5 lines_inside=None :: 
 comp x=435-563 y=104-105 marks=5 lines_inside=None :: 
 comp x=303-365 y=125-126 marks=1 lines_inside=None :: 
 comp x=369-431 y=125-126 marks=1 lines_inside=None :: 
 comp x=435-497 y=125-126 marks=1 lines_inside=None :: 
 comp x=501-563 y=125-126 marks=1 lines_inside=None :: 
 comp x=50-563 y=168-169 marks=8 lines_inside=None :: 
 comp x=50-563 y=229-230 marks=8 lines_inside=None :: 
 comp x=50-563 y=243-244 marks=8 lines_inside=None :: 
 comp x=50-563 y=257-258 marks=8 lines_inside=None :: 
 comp x=50-563 y=314-315 marks=8 lines_inside=None :: 
 comp x=50-563 y=328-329 marks=8 lines_inside=None :: 
 comp x=50-563 y=371-372 marks=8 lines_inside=None :: 
 comp x=50-563 y=400-401 marks=8 lines_inside=None :: 
 comp x=50-563 y=414-417 marks=16 lines_inside=None :: 
 comp x=501-562 y=589-590 marks=1 lines_inside=None :: 
 comp x=50-563 y=618-619 marks=8 lines_inside=None :: 
 comp x=50-563 y=632-635 marks=16 lines_inside=None :: 
 comp x=50-563 y=732-733 marks=8 lines_inside=None :: 
 comp x=302-365 y=746-747 marks=1 lines_inside=None :: 
 comp x=368-431 y=746-747 marks=1 lines_inside=None :: 
 comp x=434-497 y=746-747 marks=1 lines_inside=None :: 
 comp x=500-563 y=746-747 marks=1 lines_inside=None :: 
 comp x=302-365 y=748-749 marks=1 lines_inside=None :: 
 comp x=368-431 y=748-749 marks=1 lines_inside=None :: 
 comp x=434-497 y=748-749 marks=1 lines_inside=None :: 
 comp x=500-563 y=748-749 marks=1 lines_inside=None :: 
=== financial/apple-fy2026q3-statements.pdf p1
 comp x=420-489 y=121-122 marks=1 lines_inside=None :: 
 comp x=493-563 y=121-122 marks=1 lines_inside=None :: 
 comp x=50-563 y=235-236 marks=4 lines_inside=None :: 
 comp x=50-563 y=335-336 marks=4 lines_inside=None :: 
 comp x=50-563 y=348-350 marks=5 lines_inside=None :: 
 comp x=50-563 y=363-366 marks=9 lines_inside=None :: 
 comp x=493-562 y=420-420 marks=1 lines_inside=None :: 
 comp x=50-563 y=477-478 marks=4 lines_inside=None :: 
 comp x=50-563 y=549-549 marks=4 lines_inside=None :: 
 comp x=50-563 y=563-564 marks=4 lines_inside=None :: 
 comp x=50-563 y=577-578 marks=4 lines_inside=None :: 
 comp x=50-563 y=698-699 marks=4 lines_inside=None :: 
 comp x=50-563 y=712-713 marks=4 lines_inside=None :: 
 comp x=419-489 y=725-727 marks=2 lines_inside=None :: 
 comp x=493-563 y=726-727 marks=1 lines_inside=None :: 
 comp x=419-489 y=728-729 marks=1 lines_inside=None :: 
 comp x=493-563 y=728-729 marks=1 lines_inside=None :: 
=== financial/apple-fy2026q3-statements.pdf p2
 comp x=420-563 y=112-113 marks=5 lines_inside=None :: 
 comp x=420-489 y=134-135 marks=1 lines_inside=None :: 
 comp x=493-563 y=134-135 marks=1 lines_inside=None :: 
 comp x=50-563 y=148-149 marks=4 lines_inside=None :: 
 comp x=50-563 y=347-348 marks=4 lines_inside=None :: 
 comp x=50-563 y=362-363 marks=4 lines_inside=None :: 
 comp x=50-563 y=461-462 marks=4 lines_inside=None :: 
 comp x=50-563 y=476-477 marks=4 lines_inside=None :: 
 comp x=50-563 y=604-605 marks=4 lines_inside=None :: 
 comp x=50-563 y=618-619 marks=4 lines_inside=None :: 
 comp x=50-563 y=647-648 marks=4 lines_inside=None :: 
 comp x=50-563 y=661-664 marks=8 lines_inside=None :: 
=== health/who-wfa-boys-zscore-0-5.pdf p0
 comp x=669-709 y=57-92 marks=52 lines_inside=None :: 
 comp x=735-737 y=63-73 marks=1 lines_inside=None :: 
 comp x=738-744 y=63-73 marks=2 lines_inside=None :: 
 comp x=771-772 y=63-73 marks=1 lines_inside=None :: 
 comp x=778-784 y=63-73 marks=1 lines_inside=None :: 
 comp x=712-729 y=63-74 marks=3 lines_inside=None :: 
 comp x=749-756 y=63-73 marks=1 lines_inside=None :: 
 comp x=773-778 y=64-73 marks=1 lines_inside=None :: 
 comp x=763-769 y=66-73 marks=2 lines_inside=None :: 
 comp x=730-734 y=66-73 marks=1 lines_inside=None :: 
 comp x=758-763 y=67-73 marks=2 lines_inside=None :: 
 comp x=747-749 y=76-77 marks=2 lines_inside=None :: 
 comp x=768-769 y=76-77 marks=2 lines_inside=None :: 
 comp x=714-718 y=76-86 marks=2 lines_inside=None :: 
 comp x=762-766 y=77-86 marks=1 lines_inside=None :: 
 comp x=733-738 y=79-86 marks=2 lines_inside=None :: 
 comp x=757-762 y=79-86 marks=2 lines_inside=None :: 
 comp x=773-775 y=79-86 marks=2 lines_inside=None :: 
 comp x=721-725 y=79-86 marks=1 lines_inside=None :: 
 comp x=740-745 y=79-86 marks=1 lines_inside=None :: 
 comp x=778-784 y=79-86 marks=1 lines_inside=None :: 
 comp x=725-731 y=79-89 marks=2 lines_inside=None :: 
 comp x=747-748 y=79-86 marks=1 lines_inside=None :: 
 comp x=750-755 y=79-86 marks=1 lines_inside=None :: 
 comp x=768-770 y=79-86 marks=1 lines_inside=None :: 
 comp x=57-785 y=100-101 marks=12 lines_inside=None :: 
 comp x=57-589 y=115-116 marks=7 lines_inside=None :: 
 comp x=589-785 y=115-116 marks=3 lines_inside=None :: 
 comp x=458-721 y=116-116 marks=4 lines_inside=None :: 
 comp x=721-785 y=116-116 marks=1 lines_inside=None :: 
 comp x=57-785 y=131-132 marks=1 lines_inside=None :: 
 comp x=57-785 y=465-466 marks=24 lines_inside=None :: 
 comp x=56-786 y=492-493 marks=1 lines_inside=None :: 
=== health/who-wfa-boys-zscore-0-5.pdf p1
 comp x=669-709 y=57-92 marks=52 lines_inside=None :: 
 comp x=735-737 y=63-73 marks=1 lines_inside=None :: 
 comp x=738-744 y=63-73 marks=2 lines_inside=None :: 
 comp x=771-772 y=63-73 marks=1 lines_inside=None :: 
 comp x=778-784 y=63-73 marks=1 lines_inside=None :: 
 comp x=712-729 y=63-74 marks=3 lines_inside=None :: 
 comp x=749-756 y=63-73 marks=1 lines_inside=None :: 
 comp x=773-778 y=64-73 marks=1 lines_inside=None :: 
 comp x=763-769 y=66-73 marks=2 lines_inside=None :: 
 comp x=730-734 y=66-73 marks=1 lines_inside=None :: 
 comp x=758-763 y=67-73 marks=2 lines_inside=None :: 
 comp x=747-749 y=76-77 marks=2 lines_inside=None :: 
 comp x=768-769 y=76-77 marks=2 lines_inside=None :: 
 comp x=714-718 y=76-86 marks=2 lines_inside=None :: 
 comp x=762-766 y=77-86 marks=1 lines_inside=None :: 
 comp x=733-738 y=79-86 marks=2 lines_inside=None :: 
 comp x=757-762 y=79-86 marks=2 lines_inside=None :: 
 comp x=773-775 y=79-86 marks=2 lines_inside=None :: 
 comp x=721-725 y=79-86 marks=1 lines_inside=None :: 
 comp x=740-745 y=79-86 marks=1 lines_inside=None :: 
 comp x=778-784 y=79-86 marks=1 lines_inside=None :: 
 comp x=725-731 y=79-89 marks=2 lines_inside=None :: 
 comp x=747-748 y=79-86 marks=1 lines_inside=None :: 
 comp x=750-755 y=79-86 marks=1 lines_inside=None :: 
 comp x=768-770 y=79-86 marks=1 lines_inside=None :: 
 comp x=57-785 y=100-101 marks=12 lines_inside=None :: 
 comp x=57-589 y=115-116 marks=7 lines_inside=None :: 
 comp x=589-785 y=115-116 marks=3 lines_inside=None :: 
 comp x=458-721 y=116-116 marks=4 lines_inside=None :: 
 comp x=721-785 y=116-116 marks=1 lines_inside=None :: 
 comp x=57-785 y=131-132 marks=1 lines_inside=None :: 
 comp x=57-589 y=456-457 marks=9 lines_inside=None :: 
 comp x=589-785 y=456-457 marks=3 lines_inside=None :: 
 comp x=57-458 y=457-457 marks=7 lines_inside=None :: 
 comp x=458-721 y=457-457 marks=4 lines_inside=None :: 
 comp x=721-785 y=457-457 marks=1 lines_inside=None :: 
 comp x=56-786 y=482-483 marks=1 lines_inside=None :: 
=== health/who-wfa-boys-zscore-0-5.pdf p2
 comp x=669-709 y=57-92 marks=52 lines_inside=None :: 
 comp x=735-737 y=63-73 marks=1 lines_inside=None :: 
 comp x=738-744 y=63-73 marks=2 lines_inside=None :: 
 comp x=771-772 y=63-73 marks=1 lines_inside=None :: 
 comp x=778-784 y=63-73 marks=1 lines_inside=None :: 
 comp x=712-729 y=63-74 marks=3 lines_inside=None :: 
 comp x=749-756 y=63-73 marks=1 lines_inside=None :: 
 comp x=773-778 y=64-73 marks=1 lines_inside=None :: 
 comp x=763-769 y=66-73 marks=2 lines_inside=None :: 
 comp x=730-734 y=66-73 marks=1 lines_inside=None :: 
 comp x=758-763 y=67-73 marks=2 lines_inside=None :: 
 comp x=747-749 y=76-77 marks=2 lines_inside=None :: 
 comp x=768-769 y=76-77 marks=2 lines_inside=None :: 
 comp x=714-718 y=76-86 marks=2 lines_inside=None :: 
 comp x=762-766 y=77-86 marks=1 lines_inside=None :: 
 comp x=733-738 y=79-86 marks=2 lines_inside=None :: 
 comp x=757-762 y=79-86 marks=2 lines_inside=None :: 
 comp x=773-775 y=79-86 marks=2 lines_inside=None :: 
 comp x=721-725 y=79-86 marks=1 lines_inside=None :: 
 comp x=740-745 y=79-86 marks=1 lines_inside=None :: 
 comp x=778-784 y=79-86 marks=1 lines_inside=None :: 
 comp x=725-731 y=79-89 marks=2 lines_inside=None :: 
 comp x=747-748 y=79-86 marks=1 lines_inside=None :: 
 comp x=750-755 y=79-86 marks=1 lines_inside=None :: 
 comp x=768-770 y=79-86 marks=1 lines_inside=None :: 
 comp x=57-785 y=100-101 marks=12 lines_inside=None :: 
 comp x=57-589 y=115-116 marks=7 lines_inside=None :: 
 comp x=589-785 y=115-116 marks=3 lines_inside=None :: 
 comp x=458-721 y=116-116 marks=4 lines_inside=None :: 
 comp x=721-785 y=116-116 marks=1 lines_inside=None :: 
 comp x=57-785 y=131-132 marks=1 lines_inside=None :: 
 comp x=57-785 y=294-295 marks=24 lines_inside=None :: 
 comp x=56-786 y=320-321 marks=1 lines_inside=None :: 
=== ag-trade/graincorp-capacity-2026-08-04.pdf p0
 comp x=42-818 y=66-408 marks=122 lines_inside=(1, 30, 30) :: ELEVATION CAPACITY TABLE
=== ag-trade/graincorp-stem-2026-07-31.pdf p0
 comp x=12-833 y=49-457 marks=75 lines_inside=(2, 63, 62) :: SHIPPING STEM
=== ag-trade/graincorp-stem-2026-07-31.pdf p1
 comp x=12-833 y=49-570 marks=85 lines_inside=(2, 81, 80) :: Date of Grain
=== ag-trade/graincorp-stem-2026-07-31.pdf p2
 comp x=12-833 y=49-511 marks=60 lines_inside=(2, 72, 71) :: Date of Grain
```
