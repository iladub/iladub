"""Rule-crossing census (measurement only). One document per process.

usage: python scripts/rule_crossing_probe.py <pdf> <out.json>

1. Wraps compile._validate AND document._validate (document.py:111 imports it by name) and records,
   per call, the predicate counts of the graph passed (Q1 at scale: does any validated graph carry a
   rule fact?).
2. compile_document(pdf) with defaults (as tests/test_corpus.py:101 and
   scripts/corpus_verdict_snapshot.py do).
3. POPULATION = every node of the FINAL document graph with tab:hasCell or tab:hasDataCell (see code); report regions cross-checked.
   against every subject carrying tab:hasCell in the final document graph.
4. For each cell (?t tab:hasCell ?c . ?c tab:hasBBox ?b; ?b tab:x0/x1/y0/y1 -- 2dp Decimals as
   emitted by holon._bbox_node), rules = geometry.extract_rules(pdf, page) -- the raw page extraction
   compile.page_bands uses (compile.py:518). Crossing: x0 < rule.x < x1 (strict) AND
   min(y1, rule.bottom) - max(y0, rule.top) > 0 (positive-length). Touching-only: x strict inside
   and that intersection == 0 exactly. Full-height: rule.top <= y0 and rule.bottom >= y1.
   No tolerance is applied anywhere.
"""
import sys, json, collections, time
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from rdflib import Namespace, RDF, URIRef
from iladub.etkl import compile as C
from iladub.etkl import document as D
from iladub.etkl.geometry import extract_rules

TAB = Namespace("https://w3id.org/iladub/tab#")
pdf, out = sys.argv[1], sys.argv[2]

validate_calls = []
def _wrap(orig, site):
    def w(graph, *a, **k):
        preds = collections.Counter(str(p) for _, p, _ in graph)
        types = collections.Counter(str(o) for _, _, o in graph.triples((None, RDF.type, None)))
        rule_preds = {p: n for p, n in preds.items() if "rule" in p.lower()}
        rule_types = {t: n for t, n in types.items() if "rule" in t.lower()}
        validate_calls.append({"site": site, "triples": len(graph), "rule_predicates": rule_preds,
                               "rule_types": rule_types,
                               "geometry_predicates": {p: n for p, n in preds.items()
                                                       if p.rsplit("#", 1)[-1] in ("x0", "x1", "y0", "y1", "hasBBox")}})
        return orig(graph, *a, **k)
    return w
C._validate = _wrap(C._validate, "compile (page scope)")
D._validate = _wrap(D._validate, "document (document scope)")

t0 = time.time()
rep = D.compile_document(pdf)
elapsed = time.time() - t0
g = rep.graph

# asserted reports (verdict == "asserted" with a table_uri), for cross-check only
asserted = []
for pi, page in enumerate(rep.pages):
    for r in page.regions:
        if r.verdict == "asserted" and r.table_uri is not None:
            asserted.append((pi, URIRef(str(r.table_uri)), r.cells, r.anchor))
report_tables = {t for _, t, _, _ in asserted}
# POPULATION: every table node in the FINAL document graph that carries cells, via tab:hasCell
# (holon.py) or tab:hasDataCell (datagrid.py:739). Escalated regions carry no cells; withdrawn
# tables are removed from the graph (document.py adoption pass), so what remains is asserted output.
CELL_PREDS = (TAB.hasCell, TAB.hasDataCell)
graph_tables = set()
for cp in CELL_PREDS:
    graph_tables |= set(g.subjects(cp, None))
report_diag = {}
for t in sorted(report_tables - graph_tables):
    report_diag[str(t)] = {"as_subject": len(list(g.triples((t, None, None)))),
                           "as_object": len(list(g.triples((None, None, t))))}

import re
def uri_page(t):
    m = re.search(r"/p(\d+)(?:/adopt)?#", str(t))
    return int(m.group(1)) if m else None

rules_cache = {}
def rules_for(page):
    if page not in rules_cache:
        rules_cache[page] = extract_rules(pdf, page)
    return rules_cache[page]

tables = []
examples = []
for t in sorted(graph_tables, key=str):
    cells = [c for cp in CELL_PREDS for c in g.objects(t, cp)]
    ttypes = sorted(str(o).rsplit("#", 1)[-1] for o in g.objects(t, RDF.type))
    up = uri_page(t)
    rec = {"page_uri": up, "table": str(t), "types": ttypes, "in_reports": t in report_tables,
           "graph_cells": len(cells), "crossed_cells": 0, "crossings": 0, "full_height": 0,
           "partial": 0, "touching_only_pairs": 0, "touching_only_cells": 0, "no_bbox": 0,
           "onpage_ne_uri_page": 0, "by_type": {}}
    for c in cells:
        b = g.value(c, TAB.hasBBox)
        ctype = ",".join(sorted(str(o).rsplit("#", 1)[-1] for o in g.objects(c, RDF.type)))
        rec["by_type"][ctype] = rec["by_type"].get(ctype, 0) + 1
        if b is None:
            rec["no_bbox"] += 1
            continue
        x0, x1, y0, y1 = (float(g.value(b, TAB[k])) for k in ("x0", "x1", "y0", "y1"))
        op = g.value(c, TAB.onPage)
        page = int(op) if op is not None else up
        if up is not None and page != up:
            rec["onpage_ne_uri_page"] += 1
        crossed = touching = False
        for r in rules_for(page):
            if not (x0 < r.x < x1):
                continue
            inter = min(y1, r.bottom) - max(y0, r.top)
            if inter > 0:
                crossed = True
                rec["crossings"] += 1
                full = r.top <= y0 and r.bottom >= y1
                rec["full_height" if full else "partial"] += 1
                if len(examples) < 2000:
                    examples.append({"page_index": page, "table": str(t), "cell": str(c), "cell_type": ctype,
                                     "text": str(g.value(c, TAB.cellText)), "bbox": [x0, y0, x1, y1],
                                     "rule": {"x": round(r.x, 3), "top": round(r.top, 3), "bottom": round(r.bottom, 3)},
                                     "full_height": full})
            elif inter == 0:
                touching = True
                rec["touching_only_pairs"] += 1
        rec["crossed_cells"] += crossed
        rec["touching_only_cells"] += (touching and not crossed)
    tables.append(rec)

json.dump({"pdf": pdf, "elapsed_s": round(elapsed, 1), "score": rep.score,
           "n_pages": len(rep.pages),
           "asserted_report_regions": len(asserted), "asserted_tables": len(graph_tables), "report_tables_not_in_graph_diag": report_diag,
           "graph_hasCell_subjects": len(graph_tables),
           "graph_tables_not_in_reports": sorted(str(x) for x in graph_tables - report_tables),
           "report_tables_not_in_graph": sorted(str(x) for x in report_tables - graph_tables),
           "tables": tables, "examples": examples,
           "rule_counts_per_page": {p: len(v) for p, v in rules_cache.items()},
           "validate_calls": validate_calls}, open(out, "w"), indent=1, default=str)
print("done", pdf, round(elapsed, 1))
