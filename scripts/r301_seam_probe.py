"""R301 seam probe: can a post-hoc withdrawal find a refused table's booked ink from its
RegionReport alone? Captures every compile_tables call the document driver makes on fed-h41
(validate_shapes=False), runs the RuleSeparatedInk query on each returned page graph, maps
refused cells -> owning table -> report(s) naming that table."""
import sys, time
from rdflib import Namespace
from iladub.etkl import document, compile as C

TAB = Namespace("https://w3id.org/iladub/tab#")
Q = """PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT DISTINCT ?this WHERE {
  ?this tab:firstGlyphEnd ?fe ; tab:lastGlyphStart ?ls ; tab:onPage ?p ; tab:hasBBox ?b .
  ?b tab:y0 ?y0 ; tab:y1 ?y1 .
  ?r a tab:RuleSpan ; tab:onPage ?p ; tab:ruleX ?value ; tab:ruleTop ?rt ; tab:ruleBottom ?rb .
  FILTER (?fe <= ?value && ?value <= ?ls)
  FILTER ((IF(?y1 < ?rb, ?y1, ?rb)) - (IF(?y0 > ?rt, ?y0, ?rt)) > 0)
}"""
calls = []
orig = document.compile_tables
def spy(pdf, page_number=0, **kw):
    rep = orig(pdf, page_number=page_number, **kw)
    calls.append((page_number, str(kw.get("doc_uri")), kw.get("datagrid_adopt", False), rep))
    return rep
document.compile_tables = spy
t = time.time()
drep = document.compile_document(sys.argv[1], validate_shapes=False)
print(f"compiled in {time.time()-t:.0f}s, {len(calls)} page compiles")
for p, du, adopt, rep in calls:
    cells = [r[0] for r in rep.graph.query(Q)]
    if not cells:
        continue
    print(f"\n== page {p} doc={du} adopt={adopt} score={rep.score:.4f} A={rep.asserted} E={rep.escalated}")
    tables = {}
    for c in cells:
        owners = set(rep.graph.subjects(TAB.hasCell, c)) | set(rep.graph.subjects(TAB.hasDataCell, c))
        for o in owners:
            tables.setdefault(o, []).append(c)
        if not owners:
            print("  ORPHAN cell", c)
    for tbl, cs in tables.items():
        types = [str(x).split('#')[-1] for x in rep.graph.objects(tbl, C.RDF.type)] if hasattr(C, 'RDF') else []
        idx = [i for i, r in enumerate(rep.regions) if r.table_uri == tbl]
        print(f"  table {tbl} types={types} refused_cells={len(cs)} -> reports {idx}")
        for i in idx:
            r = rep.regions[i]
            print(f"    region {i}: verdict={r.verdict} kind={r.kind} cells={r.cells} "
                  f"tA={r.tokens_asserted} tE={r.tokens_escalated} supersedes={r.supersedes}")
        # how many reports share this band's table? and how many tables does the graph hold?
    print("  all regions:", [(i, r.verdict, str(r.table_uri).rsplit('/',1)[-1] if r.table_uri else None,
                              r.tokens_asserted, r.tokens_escalated) for i, r in enumerate(rep.regions)])
    alltables = set(rep.graph.subjects(C.RDF.type, TAB.RecordTable)) | set(rep.graph.subjects(C.RDF.type, TAB.HierarchicalTable))
    named = {r.table_uri for r in rep.regions if r.table_uri}
    print("  graph tables not named by any report:", sorted(str(x) for x in alltables - named))
