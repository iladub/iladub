# Evidence — a boxhead count cannot be the table-extent oracle (2026-09-27)

**Serves:** maintenance — records a refuted oracle candidate for the question compiler's round 2 (table extent); it meets no criterion

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `jev-reading-handoff` · **HEAD measured:** `2519cad`

**Doc impact: none.**

## The proposition, and why it was run

`2026-09-27-question-compiler-design-handoff.md` § 4 measured that cbh and bfs both fail on **table
extent** (how many tables, where each ends). Design section 4 was re-presented with a structural
oracle as its first slice: *an admitted table extent contains exactly one boxhead, above every body
row.* The maintainer ruled: run the check before the spec. Three parts:

- **P1** — bfs p5's page-scoped data grid (`derive_data_grid`, `src/iladub/etkl/datagrid.py:319`)
  counts 2 boxheads.
- **P2** — cbh `#table9` (stock table + side-by-side maintenance table + disclaimer) counts ≥ 2.
- **P3** — null control: every other extent in the 7-document corpus counts ≤ 1.

## Result: REFUTED on all three, for a reason upstream of the count

**There is no header signal independent of the extent.** (MEASURED, by reading and running.)

- `header_block` (`src/iladub/etkl/boxhead.py:125`) and the datagrid refusals
  (`datagrid.py:513/516/541/549/598/602`) are the same `derive_data_grid` pass that chooses the
  extent; `header_block` walks upward from `min(grid.rows)` and can return only one block.
  **Circular.**
- `header_body_split` (`src/iladub/etkl/headers.py:84`) over raw `detect_bands` + `segment` is
  independent, but returns a split ≥ 1 on every band holding a typed column and `None` on a pure
  header band: it marks line 0 of body fragments and **misses the real boxheads**.
- `classify` (`src/iladub/etkl/regions.py:101`) always treats line 0 as the header.
- `page_bands` is itself grid-dependent (`cut_trailing_notes`, `trailing.py:71`); only raw
  `detect_bands` + `segment` is grid-free.

Two instruments, both reported below: **I1** (independent) = raw bands inside the extent with
split ≥ 1; **I2blk** (circular) = runs of refused lines, containing a no-key or heterogeneous-column
refusal, directly above an admitted grid row. The I2blk run rule is the probe's own definition,
guided by `header_block`, not a pipeline function.

- **P1: holds only on the circular signal.** I2blk = 2 (lines 0–4, 25–32). I1 = 6, every one a data
  band; the true boxheads (raw bands B2, B7) have `split=None`.
- **P2: REFUTED.** `page_bands` band 9 line 0 is one text line spanning *both* tables ("Stock at
  Port… | PORT MAINTENANCE SHUTDOWN DATES - 2026 | 1,951,264"); `classify` reads it as a flat
  3-cell header. The stock table's real boxhead is read as a body row. I1 = I2blk = 0.
  `find_table_gutter` → `None`, `is_multi_table_ambiguous` → `False`. **Side-by-side tables share
  lines, so no line-grain count can separate them.**
- **P3: REFUTED — false refusals.** ons p7 and p8 each count 4 on both instruments (the
  "Percentage change, …" sub-blocks, each followed by a series-ID code row). apple p2's single
  cash-flow grid counts I1 = 5. That ons p7/p8 are one table each is INFERRED from extracted text;
  the PDF was not read against it.

## What else it showed

- **Admitted, correct extents often exclude their boxhead** (gcap: band 2 donates it; bfs p6: T2 is
  nine extents; who), so "exactly one boxhead *inside*" is false of good extents.
- A boxhead count can only refuse an extent that is **too big**, never one that is **too small**
  (bfs p6's nine-way split is invisible to it).
- A boxhead repeated across a page break was **not exercised** (stem is one extent per page).
- The "band 8" of the handoff is raw band B7 in `explore.py`'s numbering.

## Consequence for the design

Table extent is a reading judgement with **no oracle** today. Under *no oracle, no worker* the first
loop builds the oracle. The next probe, run from this result: do the oracles that already exist
(`dispose_boxhead`, `region_tiles`, round-trip, ink conservation), applied per extent, refuse the
two wrong extents and admit the correct ones?

## Reproduction

All seven documents compiled serially with `compile_document`, `BAML_LIVE` unset. Scores: apple
.9419, bfs .9021, cbh .9095, gcap 1.0, stem .9659, ons .8464, who .9156. Commands, from the repo
root: `bash <scratch>/run.sh` (runs `dump.py` per document), then
`./.venv/bin/python <scratch>/measure.py <scratch>/dump-*.json > measure.out`. The scripts and the
full output follow verbatim.

### `run.sh`

```
#!/bin/bash
cd "/Volumes/WD Green/dev/git/iladub"
S=/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/6cd0216b-5258-452e-9a86-ec4354c25f31/scratchpad
unset BAML_LIVE
for f in ag-trade/graincorp-capacity-2026-08-04.pdf ag-trade/cbh-stem-2026-08-03.pdf gov-stats/bfs-population-bilan-2023.pdf gov-stats/ons-index-of-services-2026-02.pdf financial/apple-fy2026q3-statements.pdf health/who-wfa-boys-zscore-0-5.pdf ag-trade/graincorp-stem-2026-07-31.pdf; do
  n=$(basename $f .pdf)
  ./.venv/bin/python $S/dump.py "$f" "$S/dump-$n.json" > "$S/log-$n.txt" 2>&1
  echo "done $n $?"
done
```

### `dump.py`

```
import sys, json, time
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.document import compile_document
f=sys.argv[1]
t=time.time()
rep=compile_document("/Volumes/WD Green/dev/git/iladub/corpus/"+f)
out={"file":f,"score":rep.score,"pages":[]}
for p,pg in enumerate(rep.pages):
    out["pages"].append([{"i":i,"kind":r.kind.name,"verdict":r.verdict,"anchor":r.anchor,"cells":r.cells,"uri":str(r.table_uri) if r.table_uri else None,"reason":r.reason} for i,r in enumerate(pg.regions)])
out["secs"]=time.time()-t
json.dump(out,open(sys.argv[2],"w"),indent=1)
print(f, rep.score, out["secs"])
```

### `measure.py`

```
import sys, json, glob, os
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.bands import detect_bands
from iladub.etkl.segment import segment
from iladub.etkl.regions import classify
from iladub.etkl.headers import header_body_split
from iladub.etkl.datagrid import derive_data_grid
from iladub.etkl.boxhead import header_block
from iladub.etkl.compile import page_bands
C="/Volumes/WD Green/dev/git/iladub/corpus/"
S=os.path.dirname(os.path.abspath(__file__))
HDR=("RowAddressability","HeterogeneousColumn")
def txt(l): return " ".join(w.text for w in l.words)
def map_line(line, lines):
    best=None
    for i,l in enumerate(lines):
        d=abs(l.top-line.top)
        if d<1.5:
            ov=min(l.words[-1].x1 if False else max(w.x1 for w in l.words), max(w.x1 for w in line.words))-max(min(w.x0 for w in l.words),min(w.x0 for w in line.words))
            if best is None or (d,-ov)<best[0]: best=((d,-ov),i)
    return best[1] if best else None
def runs_above_rows(idxs, g, pred):
    """maximal runs of lines (in extent order) satisfying pred, directly followed by an admitted row"""
    rows=set(g.rows) if g else set(); out=[]; cur=[]
    for i in idxs:
        if pred(i): cur.append(i)
        else:
            if cur and i in rows: out.append(tuple(cur))
            cur=[]
    return out
for fn in sys.argv[1:]:
    d=json.load(open(fn)); pdf=C+d["file"]
    print(f"=== {d['file']} score={d['score']:.4f}")
    for p,regs in enumerate(d["pages"]):
        asserted=[r for r in regs if r["verdict"]=="asserted" and r["uri"]]
        if not asserted: continue
        lines=[l for l in sorted(text_lines(extract_words(pdf,p)),key=lambda l:l.top) if l.words]
        g=derive_data_grid(pdf,p)
        bands=page_bands(pdf,p)
        raw=[b for rb in detect_bands(text_lines(extract_words(pdf,p))) for b in segment(rb)]
        rawinfo=[]
        for b in raw:
            reg=classify(b); sp=header_body_split(b,reg.grid) if reg.grid is not None else None
            li=sorted({map_line(l,lines) for l in b.lines}-{None})
            rawinfo.append((li,sp,reg.kind.name))
        ref=g.refusals if g else {}
        hdr=lambda i: i in ref and str(ref[i]).startswith(HDR)
        anyref=lambda i: i in ref
        for r in asserted:
            if r["anchor"] and r["anchor"].endswith("DataGrid"):
                blk=header_block(lines,g)
                ext=list(range(min(list(blk)+list(g.rows)), max(g.rows)+1)); src="grid"
            else:
                b=bands[r["i"]]
                ext=sorted({map_line(l,lines) for l in b.lines}-{None}); src=f"band{r['i']}"
                up=ext[0]-1 if ext else -1; above=[]
                while up>=0 and up in ref: above.insert(0,up); up-=1
                if above: src+=f"+above{above[0]}-{above[-1]}"
                ext=above+ext
            es=set(ext)
            inb=[(k,li,sp,kd) for k,(li,sp,kd) in enumerate(rawinfo) if es & set(li)]
            i1=[k for k,li,sp,kd in inb if sp is not None and sp>=1]
            i2=runs_above_rows(ext,g,hdr)
            i2any=[run for run in runs_above_rows(ext,g,lambda i: i in ref and not str(ref[i]).startswith("AggregateWitness")) if any(hdr(j) for j in run)]
            print(f" p{p} {r['uri'].split('#')[-1]:22s} {src:7s} lines {ext[0] if ext else '-'}-{ext[-1] if ext else '-'} n={len(ext)} cells={r['cells']}")
            print(f"    I1(raw bands in extent w/ split>=1)={len(i1)}  rawbands={[(k,(li[0],li[-1]) if li else None,sp,kd[:3]) for k,li,sp,kd in inb]}")
            print(f"    I2(grid hdr-refusal runs above admitted row)={len(i2)} {i2}   I2blk={len(i2any)} {i2any}")
            for run in i2any:
                print("       run:", " // ".join(txt(lines[j])[:50] for j in run))
```

### `explore.py`

```
import sys
sys.path.insert(0, "/Volumes/WD Green/dev/git/iladub/src")
from iladub.etkl.geometry import extract_words, text_lines
from iladub.etkl.bands import detect_bands
from iladub.etkl.segment import segment
from iladub.etkl.regions import classify
from iladub.etkl.headers import header_body_split
from iladub.etkl.datagrid import derive_data_grid
from iladub.etkl.boxhead import header_block
C="/Volumes/WD Green/dev/git/iladub/corpus/"
pdf=C+sys.argv[1]; p=int(sys.argv[2])
lines=[l for l in sorted(text_lines(extract_words(pdf,p)),key=lambda l:l.top) if l.words]
top2i={id(l):i for i,l in enumerate(lines)}
def idx(line):
    for i,l in enumerate(lines):
        if abs(l.top-line.top)<0.01 and l.words[0].x0==line.words[0].x0: return i
    return None
raw=detect_bands(text_lines(extract_words(pdf,p)))
bi=0
for rb in raw:
  for b in segment(rb):
    reg=classify(b)
    sp=header_body_split(b,reg.grid) if reg.grid is not None else None
    t=" | ".join(" ".join(w.text for w in l.words)[:60] for l in b.lines[:3])
    print(f"B{bi} top={b.top:.0f}-{b.bottom:.0f} n={len(b.lines)} x={min(w.x0 for l in b.lines for w in l.words):.0f}-{max(w.x1 for l in b.lines for w in l.words):.0f} kind={reg.kind.name} ncols={reg.grid.ncols if reg.grid else None} split={sp} :: {t[:150]}")
    bi+=1
g=derive_data_grid(pdf,p)
if g:
  print("GRID rows", min(g.rows), max(g.rows), len(g.rows), "ncols", len(g.columns), g.universe)
  print("header_block", header_block(lines,g))
  for i,l in enumerate(lines):
    tag = "ROW" if i in g.rows else ("REF:"+str(g.refusals.get(i))[:50] if i in g.refusals else "-")
    print(f"  L{i} top={l.top:.0f} {tag:55s} {' '.join(w.text for w in l.words)[:90]}")
```

### `measure.out`

```
=== financial/apple-fy2026q3-statements.pdf score=0.9419
 p0 mtable2                band2+above0-2 lines 0-43 n=44 cells=124
    I1(raw bands in extent w/ split>=1)=5  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 2), None, 'NON'), (2, (3, 14), None, 'UNS'), (3, (15, 18), 1, 'UNS'), (4, (19, 23), 1, 'UNS'), (5, (24, 29), 1, 'UNS'), (6, (30, 36), 1, 'UNS'), (7, (37, 43), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=1 [(0, 1, 2, 3, 4, 5, 6)]
       run: Apple Inc. // CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (U // (In millions, except number of shares, which are r // Three Months Ended Nine Months Ended // June 27, June 28, June 27, June 28, // 2026 2025 2026 2025 // Net sales:
 p1 mtable2                band2+above0-2 lines 0-42 n=43 cells=56
    I1(raw bands in extent w/ split>=1)=5  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 2), None, 'NON'), (2, (3, 13), 1, 'UNS'), (3, (14, 20), 1, 'UNS'), (4, (21, 28), 1, 'UNS'), (5, (29, 33), 1, 'UNS'), (6, (34, 34), None, 'NON'), (7, (35, 42), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=1 [(0, 1, 2, 3, 4, 5, 6)]
       run: Apple Inc. // CONDENSED CONSOLIDATED BALANCE SHEETS (Unaudited) // (In millions, except number of shares, which are r // June 27, September 27, // 2026 2025 // ASSETS: // Current assets:
 p2 p2-datagrid            grid    lines 0-40 n=41 cells=87
    I1(raw bands in extent w/ split>=1)=5  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 2), None, 'NON'), (2, (3, 6), None, 'UNS'), (3, (7, 20), 1, 'UNS'), (4, (21, 27), 1, 'UNS'), (5, (28, 36), 1, 'UNS'), (6, (37, 38), 1, 'UNS'), (7, (39, 40), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(4, 5)]   I2blk=1 [(0, 1, 2, 3, 4, 5)]
       run: Apple Inc. // CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS (U // (In millions) // Nine Months Ended // June 27, June 28, // 2026 2025
=== gov-stats/bfs-population-bilan-2023.pdf score=0.9021
 p5 p5-datagrid            grid    lines 0-59 n=60 cells=496
    I1(raw bands in extent w/ split>=1)=6  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 1), None, 'NON'), (2, (2, 4), None, 'UNS'), (3, (5, 9), 1, 'UNS'), (4, (10, 20), 1, 'UNS'), (5, (21, 28), None, 'NON'), (6, (29, 29), None, 'NON'), (7, (30, 32), None, 'UNS'), (8, (33, 33), None, 'NON'), (9, (34, 38), 1, 'UNS'), (10, (39, 43), 1, 'UNS'), (11, (44, 48), 1, 'UNS'), (12, (49, 53), 1, 'UNS'), (13, (54, 63), None, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=2 [(1, 2, 3, 4), (29, 30, 31, 32)]   I2blk=2 [(0, 1, 2, 3, 4), (25, 26, 27, 28, 29, 30, 31, 32)]
       run: Communiqué de presse OFS // T1 Bilan de la population résidante permanente, de // État de laComposantes de l'évolution de la populat // population Naissances Décès Accroissement Immigrat // au 1er janvier vivantes naturel migratoire 1 stati
       run: Sources: OFS - BEVNAT, ESPOP, STATPOP // 1 Jusqu'en 2010 inclus les changements de statut;  // 2 Ne correspond pas au chiffre officiel des décès  // 3 Dès 2011, changement des méthodes de production  // T2 Bilan de la population résidante permanente sel // Cantons État de la Composantes de l'évolution de l // population Naissances Décès Accroissement Solde mi // au 1er janvier vivantes naturel international 1 in
 p6 table2                 band2+above0-2 lines 0-6 n=7 cells=6
    I1(raw bands in extent w/ split>=1)=0  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 2), None, 'UNS'), (2, (3, 6), None, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p6 table3                 band3+above0-6 lines 0-7 n=8 cells=9
    I1(raw bands in extent w/ split>=1)=0  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 2), None, 'UNS'), (2, (3, 6), None, 'UNS'), (3, (7, 7), None, 'NON')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=1 [(0, 1, 2, 3, 4, 5, 6)]
       run: Communiqué de presse OFS // T3 Population résidante permanente par classe d’âg // canton, au 31.12.2023 // Grandes régions Total 0-19 ans 20-39 ans 40-64 ans // Cantons dépendance dépendance des // des jeunes 1 personnes // âgées 2
 p6 table4                 band4   lines 8-11 n=4 cells=36
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(4, (8, 11), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p6 table5                 band5   lines 12-17 n=6 cells=54
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(5, (12, 17), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p6 table6                 band6   lines 18-21 n=4 cells=36
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(6, (18, 21), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p6 table7                 band7   lines 22-22 n=1 cells=9
    I1(raw bands in extent w/ split>=1)=0  rawbands=[(7, (22, 22), None, 'NON')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p6 table8                 band8   lines 23-30 n=8 cells=72
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(8, (23, 30), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p6 table9                 band9   lines 31-37 n=7 cells=63
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(9, (31, 37), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p6 table10                band10  lines 38-38 n=1 cells=9
    I1(raw bands in extent w/ split>=1)=0  rawbands=[(10, (38, 41), None, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
=== ag-trade/cbh-stem-2026-08-03.pdf score=0.9095
 p0 htable1                band1+above0-1 lines 0-19 n=20 cells=170
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 1), None, 'NON'), (1, (2, 19), 7, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(9,)]   I2blk=1 [(0, 1, 2, 3, 4, 5, 6, 7, 8, 9)]
       run: Daily Ship Roster // As of03/08/2026 // GERALDTON // BERTH MAY BE UNAVAILABLE 2000HRS 04TH AUG UNTIL 01 // BERTH MAY BE UNAVAILABLE 1500HRS 05TH AUG UNTIL 23 // BERTH MAY BE UNAVAILABLE 1600HRS 08TH AUG UNTIL 23 // PORT MAINTENANCE SHUTDOWN AM 24TH AUG UNTIL PM 04T // Time Nom Date Nom Date Loading Time Loading // VNA # Vessel Name Time Nominated Date Nominated Cl // Accepted Accepted Completed Completed
 p0 htable3                band3   lines 21-41 n=21 cells=268
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(3, (21, 41), 4, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=1 [(21, 22, 23, 24, 25, 26)]
       run: KWINANA // PORT MAINTENANCE SHUTDOWN AM 01ST SEPT UNTIL PM 15 // Time Nom Date Nom Date Loading Time Loading // VNA # Vessel Name Time Nominated Date Nominated Cl // Accepted Accepted Completed Completed // 10167 YM COURAGE 10:59 06/07/2026 11:31 06/07/2026
 p0 htable5                band5+above42-42 lines 42-62 n=21 cells=228
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(4, (42, 42), None, 'NON'), (5, (43, 62), 5, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(48,)]   I2blk=1 [(43, 44, 45, 46, 47, 48)]
       run: ALBANY // BERTH UNAVAILABLE UNTIL PM 05TH AUG DUE TO SEABED  // PORT MAINTENANCE SHUTDOWN AM 01ST OCT UNTIL PM 15T // Time Nom Date Nom Date Loading Time Loading // VNA # Vessel Name Time Nominated Date Nominated Cl // Accepted Accepted Completed Completed
 p0 htable7                band7+above63-63 lines 63-73 n=11 cells=84
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(6, (63, 63), None, 'NON'), (7, (64, 73), 4, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(68,)]   I2blk=1 [(64, 65, 66, 67, 68)]
       run: ESPERANCE // PORT MAINTENANCE SHUTDOWN AM 01ST AUG UNTIL PM 15T // Time Nom Date Nom Date Loading Time Loading // VNA # Vessel Name Time Nominated Date Nominated Cl // Accepted Accepted Completed Completed
 p0 table9                 band9+above74-74 lines 74-84 n=11 cells=13
    I1(raw bands in extent w/ split>=1)=0  rawbands=[(8, (74, 74), None, 'NON'), (9, (75, 84), None, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
=== ag-trade/graincorp-capacity-2026-08-04.pdf score=1.0000
 p0 htable3                band3+above0-3 lines 0-30 n=31 cells=406
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 2), None, 'NON'), (2, (3, 3), None, 'NON'), (3, (4, 30), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(3,)]   I2blk=1 [(0, 1, 2, 3)]
       run: GrainCorp Operations Ltd ABN 52003875401 // ELEVATION CAPACITY TABLE // As At Tuesday, 4 August 2026 // Year Elevation Period Mackay Gladstone Fisherman I
=== ag-trade/graincorp-stem-2026-07-31.pdf score=0.9659
 p0 htable2                band2+above0-2 lines 0-63 n=64 cells=586
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 1), None, 'NON'), (1, (2, 2), None, 'NON'), (2, (3, 63), 4, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(5, 6)]   I2blk=1 [(0, 1, 2, 3, 4, 5, 6)]
       run: GRAINCORP SHIPPING STEM // GrainCorp Operations Ltd ABN 52003875401 // SHIPPING STEM // Friday, 31 July 2026 // Date of Grain // Unique Slot Loading Date Nomination Time Nominatio // GC Fin Year Month Port Reference Number Exporter N
 p1 htable1                band1+above0-1 lines 0-81 n=82 cells=825
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 1), None, 'NON'), (1, (2, 81), 3, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(3, 4)]   I2blk=1 [(0, 1, 2, 3, 4)]
       run: GRAINCORP SHIPPING STEM // GrainCorp Operations Ltd ABN 52003875401 // Date of Grain // Unique Slot Loading Date Nomination Time Nominatio // GC Fin Year Month Port Reference Number Exporter N
 p2 htable1                band1+above0-1 lines 0-72 n=73 cells=741
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 1), None, 'NON'), (1, (2, 72), 3, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(3, 4)]   I2blk=1 [(0, 1, 2, 3, 4)]
       run: GRAINCORP SHIPPING STEM // GrainCorp Operations Ltd ABN 52003875401 // Date of Grain // Unique Slot Loading Date Nomination Time Nominatio // GC Fin Year Month Port Reference Number Exporter N
=== gov-stats/ons-index-of-services-2026-02.pdf score=0.8464
 p4 htable3                band3+above31-32 lines 31-35 n=5 cells=19
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 31), None, 'NON'), (1, (32, 32), None, 'NON'), (2, (33, 35), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p7 p7-datagrid            grid    lines 0-59 n=60 cells=276
    I1(raw bands in extent w/ split>=1)=5  rawbands=[(0, (0, 1), None, 'UNS'), (1, (2, 2), None, 'NON'), (2, (3, 3), None, 'NON'), (3, (4, 6), None, 'UNS'), (4, (7, 8), 1, 'UNS'), (5, (9, 13), 1, 'UNS'), (6, (14, 15), None, 'REC'), (7, (16, 16), None, 'NON'), (8, (17, 17), None, 'NON'), (9, (18, 18), None, 'NON'), (10, (19, 19), None, 'NON'), (11, (20, 20), None, 'NON'), (12, (21, 35), 1, 'REC'), (13, (36, 42), 2, 'UNS'), (14, (43, 59), 2, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=4 [(3, 4, 5, 6, 7), (9,), (37,), (44,)]   I2blk=4 [(0, 1, 2, 3, 4, 5, 6, 7), (9,), (36, 37), (43, 44)]
       run: IOS1 IOS: Index of Services 1 // Chained volume indices of gross value added 2,3,4  // Industry sections (SIC2007) // Business Govern- // Total Distribution Transport, services ment and // service hotels and storage and and other // industries restaurants communication finance servi // Section G-T G and I H and J K-N O-T
       run: S2KU S2MV KI7B KI7L KI7T
       run: Percentage change, latest year on previous year // S222 S243 KI77 KI7G KI7O
       run: Percentage change, latest month on same month a ye // S26Q S28R KI7A KI7I KI7Q
 p8 p8-datagrid            grid    lines 0-60 n=61 cells=276
    I1(raw bands in extent w/ split>=1)=4  rawbands=[(0, (0, 3), None, 'UNS'), (1, (4, 4), None, 'NON'), (2, (5, 7), None, 'UNS'), (3, (8, 9), 1, 'UNS'), (4, (10, 26), 2, 'UNS'), (5, (27, 43), 2, 'UNS'), (6, (44, 44), None, 'NON'), (7, (45, 60), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=4 [(4, 5, 6, 7, 8), (11,), (28,), (45,)]   I2blk=4 [(0, 1, 2, 3, 4, 5, 6, 7, 8), (10, 11), (27, 28), (44, 45)]
       run: IOS1 IOS: Index of Services 1 // Chained volume indices of gross value added 2,3,4  // continued // Industry sections (SIC2007) // Business Govern- // Total Distribution Transport, services ment and // service hotels and storage and and other // industries restaurants communication finance servi // Section G-T G and I H and J K-N O-T
       run: Percentage change, latest month on previous month // S222 S243 KI77 KI7G KI7O
       run: Percentage change, latest 3 months on same 3 month // S2G6 S2I7 KI7C KI7J KI7R
       run: Percentage change, latest 3 months on previous 3 m // S2BG S2DH KI7D KI7K KI7S
=== health/who-wfa-boys-zscore-0-5.pdf score=0.9156
 p0 mtable2                band2+above0-1 lines 0-10 n=11 cells=77
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 1), None, 'NON'), (2, (2, 10), 2, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(3,)]   I2blk=1 [(0, 1, 2, 3)]
       run: Weight-for-age BOYS // Birth to 5 years (z-scores) // Z-scores (weight in kg) // Year: Month Month L M S -3 SD -2 SD -1 SD Median 1
 p0 htable3                band3   lines 11-16 n=6 cells=63
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(3, (11, 16), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p0 table4                 band4   lines 17-22 n=6 cells=65
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(4, (17, 22), 1, 'REC')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p0 htable5                band5   lines 23-28 n=6 cells=63
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(5, (23, 28), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p1 mtable2                band2+above0-1 lines 0-9 n=10 cells=66
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 0), None, 'NON'), (1, (1, 1), None, 'NON'), (2, (2, 9), 2, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(3,)]   I2blk=1 [(0, 1, 2, 3)]
       run: Weight-for-age BOYS // Birth to 5 years (z-scores) // Z-scores (weight in kg) // Year: Month Month L M S -3 SD -2 SD -1 SD Median 1
 p1 htable3                band3   lines 10-15 n=6 cells=63
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(3, (10, 15), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p1 table4                 band4   lines 16-21 n=6 cells=65
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(4, (16, 21), 1, 'REC')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p1 htable5                band5   lines 22-27 n=6 cells=63
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(5, (22, 27), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
 p2 mtable1                band1+above0-1 lines 0-9 n=10 cells=66
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(0, (0, 1), None, 'NON'), (1, (2, 9), 2, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=1 [(3,)]   I2blk=1 [(0, 1, 2, 3)]
       run: Weight-for-age BOYS // Birth to 5 years (z-scores) // Z-scores (weight in kg) // Year: Month Month L M S -3 SD -2 SD -1 SD Median 1
 p2 htable2                band2   lines 10-15 n=6 cells=63
    I1(raw bands in extent w/ split>=1)=1  rawbands=[(2, (10, 15), 1, 'UNS')]
    I2(grid hdr-refusal runs above admitted row)=0 []   I2blk=0 []
```
