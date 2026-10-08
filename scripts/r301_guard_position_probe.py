"""THROWAWAY probe for R301's guard POSITION (continues scripts/r301_guard_prototype.py, whose guard
wrapped compile_tables and so ran AFTER adoption). Needs a local, uncommitted hook in
compile_tables (`_R301_HOOK`, called 'pre' just before the adoption branch after a carry_from_pdf,
and 'post' just after the existing carry) — the diff is recorded in the loop's handoff.
Arg: pre  -> withdraw at 'pre' only; 'post' only COUNTS refused cells.
     both -> withdraw at 'pre' and again at 'post' (catches a grid adoption re-admits).
Always validate_shapes=True. Extent = closure over blank nodes only (F4); the admission root is
still deleted (not the design); escalation text = the region's own ascii (empty for an appended
grid, F7)."""
import sys, time
from dataclasses import replace
from rdflib import Graph, URIRef, BNode, Namespace
from iladub.etkl import document, compile as C
from iladub.etkl.holon import escalate_region
TAB = Namespace("https://w3id.org/iladub/tab#")
Q = open(__file__.replace("r301_guard_position_probe.py", "r301_guard_prototype.py")).read().split('Q = """')[1].split('"""')[0]
PDF = "held-out/fed-h41-2025-01-02.pdf"
MODE = sys.argv[1] if len(sys.argv) > 1 else "pre"
log = []

def closure(g, t):
    out, prefix = Graph(), str(t) + "-"
    roots = [s for s in set(g.subjects()) if isinstance(s, URIRef) and (s == t or str(s).startswith(prefix))]
    seen, fr = set(roots), list(roots)
    while fr:
        s = fr.pop()
        for p, o in g.predicate_objects(s):
            out.add((s, p, o))
            if isinstance(o, BNode) and o not in seen:
                seen.add(o); fr.append(o)
    return out

def hook(pos, g, reports, A, E, doc, page, pdf):
    cells = {r[0] for r in g.query(Q)}
    if not cells:
        return g, reports, A, E
    owners = {o for c in cells for pr in (TAB.hasCell, TAB.hasDataCell) for o in g.subjects(pr, c)}
    if pos == "post" and MODE == "pre":
        log.append((pos, page, str(doc), f"COUNT ONLY: {len(cells)} refused cells, owners {sorted(map(str, owners))}"))
        return g, reports, A, E
    reports = list(reports)
    for t in sorted(owners, key=str):
        idx = [i for i, r in enumerate(reports) if r.table_uri == t]
        if len(idx) != 1:
            log.append((pos, page, str(doc), str(t), f"NOT WITHDRAWN: named by {idx}")); continue
        i = idx[0]; r = reports[i]
        sub = closure(g, t)
        g -= sub
        escalate_region(g, URIRef(f"{doc}#region{i}"), doc, r.ascii or "(grid rows)",
                        "RULE_SEPARATED_INK", URIRef(r.anchor) if r.anchor else TAB.DataGrid, 0.0, page)
        reports[i] = replace(r, verdict="escalated", reason="RULE_SEPARATED_INK", cells=0, table_uri=None,
                             tokens_asserted=0, tokens_escalated=r.tokens_escalated + r.tokens_asserted)
        A -= r.tokens_asserted; E += r.tokens_asserted
        log.append((pos, page, str(doc), str(t), f"WITHDRAWN region {i}: {len(sub)} triples, moved {r.tokens_asserted} tok"))
    return g, reports, A, E

def summarize(tag, d):
    print(f"\n##### {tag}: score={d.score:.4f} pages={len(d.pages)} adopted={d.adopted}")
    print(f"  sum page A/E = {sum(p.asserted for p in d.pages)}/{sum(p.escalated for p in d.pages)}")
    for k, p in enumerate(d.pages):
        print(f"  p{k}: A={p.asserted} E={p.escalated} score={p.score:.4f} regions="
              f"{[(i, r.verdict, r.reason, str(r.table_uri).rsplit('/',1)[-1] if r.table_uri else None, r.tokens_asserted, r.tokens_escalated) for i, r in enumerate(p.regions) if r.verdict != 'ignored']}")
        assert sum(r.tokens_asserted for r in p.regions) == p.asserted, (k, "A ledger")
        assert sum(r.tokens_escalated for r in p.regions) == p.escalated, (k, "E ledger")
    for n in d.notes: print("  note:", n)
    dangling = [(k, i, str(r.table_uri)) for k, p in enumerate(d.pages) for i, r in enumerate(p.regions)
                if r.table_uri is not None and not any(d.graph.predicate_objects(r.table_uri))]
    print("  report table_uri with no triples (R300 class):", dangling)
    print("  refused cells left in doc graph:", len(list(d.graph.query(Q))))
    esc = sorted(str(s) for s in d.graph.subjects(TAB.escalationReason, None)) if hasattr(TAB, "escalationReason") else []
    p5 = [str(s) for s in d.graph.all_nodes() if isinstance(s, URIRef) and "page5" in str(s) and "region3" in str(s)] + \
         [str(s) for s in d.graph.all_nodes() if isinstance(s, URIRef) and str(s).endswith("p5#region3")]
    print("  IRIs naming p5 region3 in doc graph:", sorted(set(p5))[:10])

C._R301_HOOK = hook
t = time.time()
try:
    d = document.compile_document(PDF, validate_shapes=True)
    summarize(f"MODE={MODE} validate=True ({time.time()-t:.0f}s)", d)
except Exception as e:
    print(f"\n##### MODE={MODE} RAISED after {time.time()-t:.0f}s: {type(e).__name__}: {str(e)[:1500]}")
for row in log: print("  guard:", row)
