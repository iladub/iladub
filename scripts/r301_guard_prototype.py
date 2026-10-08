"""THROWAWAY prototype of R301's guard, kept as the evidence instrument for
`docs/superpowers/2026-10-08-r301-guard-prototype-handoff.md`. NOT the design: it mints no refusal
decision, deletes `{t}-admission`, and escalates an appended region with placeholder text.
Arg: base | guard | both. Run 1: unguarded, validate_shapes=False. Run 2: guarded (after
carry_from_pdf, i.e. AFTER adoption), validate_shapes=True. ~430 s for both."""
import sys, time
from dataclasses import replace
from rdflib import Graph, Namespace, URIRef, BNode, RDF
from iladub.etkl import document, compile as C
from iladub.etkl.holon import escalate_region
TAB = Namespace("https://w3id.org/iladub/tab#")
Q = """PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT DISTINCT ?this WHERE {
  ?this tab:firstGlyphEnd ?fe ; tab:lastGlyphStart ?ls ; tab:onPage ?p ; tab:hasBBox ?b .
  ?b tab:y0 ?y0 ; tab:y1 ?y1 .
  ?r a tab:RuleSpan ; tab:onPage ?p ; tab:ruleX ?value ; tab:ruleTop ?rt ; tab:ruleBottom ?rb .
  FILTER (?fe <= ?value && ?value <= ?ls)
  FILTER ((IF(?y1 < ?rb, ?y1, ?rb)) - (IF(?y0 > ?rt, ?y0, ?rt)) > 0)
}"""
PDF = "held-out/fed-h41-2025-01-02.pdf"
orig = document.compile_tables
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

def guarded(pdf, page_number=0, **kw):
    vs = kw.pop("validate_shapes", True)
    rep = orig(pdf, page_number=page_number, validate_shapes=False, **kw)
    g = rep.graph
    cells = {r[0] for r in g.query(Q)}
    if not cells:
        if vs: _check(g)
        return rep
    owners = {o for c in cells for pr in (TAB.hasCell, TAB.hasDataCell) for o in g.subjects(pr, c)}
    regions, A, E = list(rep.regions), rep.asserted, rep.escalated
    doc = kw.get("doc_uri") or C._DOC
    for t in sorted(owners, key=str):
        idx = [i for i, r in enumerate(regions) if r.table_uri == t]
        if len(idx) != 1:
            log.append((page_number, str(doc), str(t), f"NOT WITHDRAWN: named by {idx}")); continue
        i = idx[0]; r = regions[i]
        sub = closure(g, t)
        nodes = set(sub.subjects())
        inbound = [(s, p) for n in nodes for s, p in g.subject_predicates(n) if s not in nodes]
        g -= sub
        escalate_region(g, URIRef(f"{doc}#region{i}"), doc, r.ascii or "(grid rows)",
                        "RULE_SEPARATED_INK", URIRef(r.anchor) if r.anchor else TAB.DataGrid, 0.0, page_number)
        regions[i] = replace(r, verdict="escalated", reason="RULE_SEPARATED_INK", cells=0, table_uri=None,
                             tokens_asserted=0, tokens_escalated=r.tokens_escalated + r.tokens_asserted)
        A -= r.tokens_asserted; E += r.tokens_asserted
        log.append((page_number, str(doc), str(t), f"WITHDRAWN region {i}: {len(sub)} triples, "
                    f"moved {r.tokens_asserted} tok, inbound left dangling={len(inbound)} {inbound[:2]}"))
    denom = A + E
    from iladub.etkl.datagrid import page_has_table
    score = A / denom if denom else (0.0 if page_has_table(pdf, page_number) else 1.0)
    out = C.CompilationReport(score, tuple(regions), g, A, E)
    if vs: _check(g)
    return out

def _check(g):
    if any(g.subjects(RDF.type, TAB.RecordTable)) or any(g.subjects(RDF.type, TAB.HierarchicalTable)):
        ok, text, legs = C._validate(g)
        if not ok:
            from iladub.etkl import membrane
            raise membrane.MembraneRefusal(C._refusal_message("asserted holon", legs, text), g, legs)

def summarize(tag, d):
    print(f"\n##### {tag}: score={d.score:.4f} pages={len(d.pages)} adopted={d.adopted}")
    A = sum(p.asserted for p in d.pages); E = sum(p.escalated for p in d.pages)
    print(f"  sum page A/E = {A}/{E}")
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

which = sys.argv[1] if len(sys.argv) > 1 else "both"
if which in ("both", "base"):
    t = time.time(); d0 = document.compile_document(PDF, validate_shapes=False)
    summarize(f"BASELINE unguarded validate=False ({time.time()-t:.0f}s)", d0)
if which in ("both", "guard"):
    document.compile_tables = guarded
    t = time.time()
    try:
        d1 = document.compile_document(PDF, validate_shapes=True)
        summarize(f"GUARDED validate=True ({time.time()-t:.0f}s)", d1)
    except Exception as e:
        print(f"\n##### GUARDED RAISED after {time.time()-t:.0f}s: {type(e).__name__}: {str(e)[:1500]}")
    for row in log: print("  guard:", row)
