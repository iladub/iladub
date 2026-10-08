"""THROWAWAY probe U1 (R301 producer-guard plan). No tracked file is edited: compile_tables' source
is read with inspect, two hook calls are inserted IN MEMORY, and the result is exec'd into the
compile module's own namespace (so relative imports and module globals are unchanged).

Hook 'pre'  = the position handoff's hook: carry_from_pdf, then withdraw/escalate every owner
              table of the select, just before `if datagrid_adopt and escalated_total > 0`.
Hook 'C'    = after the adoption branch emits its new graph (after the `_emitted` loop) and
              before anything is installed: carry_from_pdf on a COPY of the new graph, select.
build_ledger is replaced (adoption module attr; compile imports it locally) by a wrapper that
computes BOTH the stock ledger and an I2 prototype, logs both, and returns I2 (MODE=i2) or
stock (MODE=stock).
"""
import inspect, sys, time, __future__
from dataclasses import replace
from rdflib import Graph, URIRef, BNode, Namespace, RDF
from iladub.etkl import compile as C, adoption, datagrid
from iladub.etkl.adoption import LineLedger
from iladub.etkl.holon import escalate_region
from iladub.etkl.document import page_doc_uri

TAB = Namespace("https://w3id.org/iladub/tab#")
DEC = Namespace("https://w3id.org/iladub/dec#")
Q = """PREFIX tab: <https://w3id.org/iladub/tab#>
SELECT DISTINCT ?this WHERE {
  ?this tab:firstGlyphEnd ?fe ; tab:lastGlyphStart ?ls ; tab:onPage ?p ; tab:hasBBox ?b .
  ?b tab:y0 ?y0 ; tab:y1 ?y1 .
  ?r a tab:RuleSpan ; tab:onPage ?p ; tab:ruleX ?value ; tab:ruleTop ?rt ; tab:ruleBottom ?rb .
  FILTER (?fe <= ?value && ?value <= ?ls)
  FILTER ((IF(?y1 < ?rb, ?y1, ?rb)) - (IF(?y0 > ?rt, ?y0, ?rt)) > 0)
}"""
PDF = "held-out/fed-h41-2025-01-02.pdf"
PAGE = 7
MODE = sys.argv[1] if len(sys.argv) > 1 else "i2"
S = {"phase": "band", "fallback_grids": None, "bands": None, "E_after_guard": None,
     "pre_cells": None, "c_cells": None}

# ---- capture the fallback grids (first derive_data_grids call in the band phase) ----
_orig_dgs = datagrid.derive_data_grids
def dgs(pdf, page):
    out = _orig_dgs(pdf, page)
    print(f"[derive_data_grids] phase={S['phase']} -> {len(out)} grid(s), rows="
          f"{[tuple(g.rows) for g in out]}")
    if S["phase"] == "band" and S["fallback_grids"] is None:
        S["fallback_grids"] = list(out)
    return out
datagrid.derive_data_grids = dgs

# ---- capture bands (page_bands is a module-level name in compile) ----
_orig_pb = C.page_bands
def pb(*a, **k):
    out = _orig_pb(*a, **k); S["bands"] = out; return out
C.page_bands = pb

def cell_info(g, cells):
    rows = []
    for c in sorted(cells, key=str):
        txt = g.value(c, TAB.cellText)
        rows.append((str(c).rsplit("#", 1)[-1], str(txt)))
    return rows

def extent(g, t):
    out, prefix = Graph(), str(t) + "-"
    roots = [s for s in set(g.subjects()) if isinstance(s, URIRef)
             and (s == t or str(s).startswith(prefix))
             and (s, RDF.type, DEC.DecisionHolon) not in g]
    seen, fr = set(roots), list(roots)
    while fr:
        s = fr.pop()
        for p, o in g.predicate_objects(s):
            out.add((s, p, o))
            if isinstance(o, BNode) and o not in seen:
                seen.add(o); fr.append(o)
    return out, roots

def hook_pre(g, reports, A, E, doc, page, pdf):
    from iladub.etkl.ruleink import carry_from_pdf
    carry_from_pdf(g, str(doc), pdf)
    S["phase"] = "adopt"
    cells = {r[0] for r in g.query(Q)}
    S["pre_cells"] = {c: str(g.value(c, TAB.cellText)) for c in cells}
    print(f"[pre] A={A} E={E} select -> {len(cells)} cells")
    if not cells:
        S["E_after_guard"] = E; return g, reports, A, E
    owners = {o for c in cells for pr in (TAB.hasCell, TAB.hasDataCell) for o in g.subjects(pr, c)}
    reports = list(reports)
    for t in sorted(owners, key=str):
        idx = [i for i, r in enumerate(reports) if r.table_uri == t]
        print(f"[pre] owner {t} named by reports {idx} (len(bands)={len(S['bands'])})")
        if len(idx) != 1: continue
        i = idx[0]; r = reports[i]
        sub, roots = extent(g, t)
        g -= sub
        escalate_region(g, URIRef(f"{doc}#region{i}"), doc, r.ascii or "(grid rows)",
                        "RULE_SEPARATED_INK", URIRef(r.anchor) if r.anchor else TAB.DataGrid, 0.0, page)
        reports[i] = replace(r, verdict="escalated", reason="RULE_SEPARATED_INK", cells=0, table_uri=None,
                             tokens_asserted=0, tokens_escalated=r.tokens_escalated + r.tokens_asserted)
        A -= r.tokens_asserted; E += r.tokens_asserted
        print(f"[pre] WITHDRAWN region {i}: {len(sub)} triples, {len(roots)} roots, moved {r.tokens_asserted} tok")
    print(f"[pre] after guard A={A} E={E}; reports="
          f"{[(i, r.verdict, r.tokens_asserted, r.tokens_escalated) for i, r in enumerate(reports)]}")
    S["E_after_guard"] = E
    return g, reports, A, E

def hook_c(g_new, doc, pdf):
    from iladub.etkl.ruleink import carry_from_pdf
    gc = Graph()
    for tr in g_new: gc.add(tr)
    carry_from_pdf(gc, str(doc), pdf)
    cells = {r[0] for r in gc.query(Q)}
    S["c_cells"] = {c: str(gc.value(c, TAB.cellText)) for c in cells}
    print(f"[C] new adoption graph: {len(g_new)} triples; select on carried copy -> {len(cells)} cells")

# ---- ledgers ----
_stock = adoption.build_ledger
def i2_ledger(lines, grid_rows, bands, reports):
    admitted = tuple(sorted(j for j in set(grid_rows) if 0 <= j < len(lines)))
    adm = set(admitted)
    nb = len(bands)
    cover = {}
    for i in range(len(reports)):
        if i < nb:
            cover[i] = {j for j, ln in enumerate(lines) if bands[i].top <= ln.top <= bands[i].bottom}
        else:
            k = i - nb
            fg = S["fallback_grids"] or []
            cover[i] = {j for j in fg[k].rows if 0 <= j < len(lines)} if k < len(fg) else set()
    booked = [i for i, r in enumerate(reports) if r.tokens_asserted + r.tokens_escalated > 0]
    touched = frozenset(i for i in cover if cover[i] & adm)
    residue = tuple(j for j in range(len(lines)) if j not in adm
                    and any(i in touched and j in cover[i] for i in booked))
    A = (sum(len(lines[j].words) for j in admitted)
         + sum(reports[i].tokens_asserted for i in booked if i not in touched))
    E = (sum(len(lines[j].words) for j in residue)
         + sum(reports[i].tokens_escalated for i in booked if i not in touched))
    return LineLedger(admitted, residue, touched, A, E)

def ledger(lines, grid_rows, bands, reports):
    s = _stock(lines, grid_rows, bands, reports)
    n = i2_ledger(lines, grid_rows, bands, reports)
    print(f"[ledger] nlines={len(lines)} page_tokens={sum(len(l.words) for l in lines)} "
          f"len(bands)={len(bands)} len(reports)={len(reports)} admitted={len(s.admitted)} lines")
    print(f"[ledger]   STOCK: A={s.asserted_tokens} E={s.escalated_tokens} touched={set(s.touched)} residue={s.residue}")
    print(f"[ledger]   I2   : A={n.asserted_tokens} E={n.escalated_tokens} touched={set(n.touched)} residue={n.residue}")
    out = n if MODE == "i2" else s
    if S["E_after_guard"] is not None:
        print(f"[ledger]   gate ({MODE}): _led.escalated({out.escalated_tokens}) < escalated_total"
              f"({S['E_after_guard']}) -> {out.escalated_tokens < S['E_after_guard']}")
    return out
adoption.build_ledger = ledger

# ---- in-memory source transform of compile_tables ----
src = inspect.getsource(C.compile_tables)
A1 = "    if datagrid_adopt and escalated_total > 0:\n        from .adoption import build_ledger\n"
assert src.count(A1) == 1
src = src.replace(A1, "    graph, reports, asserted_total, escalated_total = _R301_PRE(graph, reports, "
                  "asserted_total, escalated_total, doc, page_number, pdf_path)\n" + A1)
A2 = "            # THE LEDGER IS LINE-GRANULAR (spec §5.3)."
assert src.count(A2) == 1
src = src.replace(A2, "            _R301_C(graph, doc, pdf_path)\n" + A2)
C.__dict__["_R301_PRE"] = hook_pre
C.__dict__["_R301_C"] = hook_c
code = compile(src, C.__file__, "exec", flags=__future__.annotations.compiler_flag, dont_inherit=True)
exec(code, C.__dict__)

adopt_doc = URIRef(f"{page_doc_uri(PAGE)}/adopt")
print("doc_uri =", adopt_doc, " MODE =", MODE)
t0 = time.time()
rep = C.compile_tables(PDF, PAGE, validate_shapes=False, datagrid_adopt=True, doc_uri=adopt_doc)
dt = time.time() - t0
print(f"\n=== result ({dt:.0f}s): score={rep.score:.4f} A={rep.asserted} E={rep.escalated}")
for i, r in enumerate(rep.regions):
    print(f"  region {i}: {r.verdict} {r.reason} cells={r.cells} A={r.tokens_asserted} "
          f"E={r.tokens_escalated} table={str(r.table_uri).rsplit('#',1)[-1] if r.table_uri else None}")
print("fallback grids rows:", [tuple(g.rows) for g in (S['fallback_grids'] or [])])
pre = S["pre_cells"] or {}; cc = S["c_cells"]
print(f"\npre-guard select cells ({len(pre)}):")
for k in sorted(pre, key=str): print("   ", str(k).rsplit("#", 1)[-1], repr(pre[k]))
if cc is None:
    print("\n[C] hook never ran: adoption gate did not open")
else:
    print(f"\nadoption-graph select cells ({len(cc)}):")
    for k in sorted(cc, key=str): print("   ", str(k).rsplit("#", 1)[-1], repr(cc[k]))
    print("\nsame IRIs:", set(pre) == set(cc), " same (IRI,text):", pre == cc)
    print("only in pre:", sorted(str(x).rsplit('#',1)[-1] for x in set(pre) - set(cc)))
    print("only in adoption:", sorted(str(x).rsplit('#',1)[-1] for x in set(cc) - set(pre)))
