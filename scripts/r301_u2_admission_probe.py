"""THROWAWAY probe U2 (R301 producer-guard plan): does keeping `{t}-admission` while its option
IRIs lose their triples pass dec:DecisionHolonShape? No tracked file is edited."""
import time
from rdflib import Graph, URIRef, BNode, Namespace, RDF
from iladub.etkl import compile as C
from iladub.etkl.holon import escalate_region
from iladub.etkl.ruleink import carry_from_pdf

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
short = lambda u: str(u).rsplit("#", 1)[-1]

t0 = time.time()
rep = C.compile_tables(PDF, PAGE, validate_shapes=False)
doc = C._DOC
print(f"compile ({time.time()-t0:.0f}s): A={rep.asserted} E={rep.escalated} doc={doc}")
for i, r in enumerate(rep.regions):
    print(f"  region {i}: {r.verdict} cells={r.cells} A={r.tokens_asserted} table={r.table_uri}")
g = rep.graph
carry_from_pdf(g, str(doc), PDF)
cells = {r[0] for r in g.query(Q)}
owners = {o for c in cells for pr in (TAB.hasCell, TAB.hasDataCell) for o in g.subjects(pr, c)}
print(f"select -> {len(cells)} cells; owners = {sorted(map(str, owners))}")
assert len(owners) == 1
t = next(iter(owners))
gi = [i for i, r in enumerate(rep.regions) if r.table_uri == t]
print("region index naming t:", gi)

# --- control: the unwithdrawn graph through the membrane ---
t1 = time.time()
ok0, text0, legs0 = C._validate(g)
print(f"\nCONTROL _validate(unwithdrawn) ({time.time()-t1:.0f}s): conforms={ok0} legs={legs0} "
      f"RuleSeparatedInkShape in text: {'RuleSeparatedInk' in text0}")

# --- extent per spec § 2.2 ---
prefix = str(t) + "-"
cand = sorted({s for s in g.subjects() if isinstance(s, URIRef) and (s == t or str(s).startswith(prefix))}, key=str)
dh = [s for s in cand if (s, RDF.type, DEC.DecisionHolon) in g]
roots = [s for s in cand if s not in dh]
sub = Graph(); seen = set(roots); fr = list(roots)
while fr:
    s = fr.pop()
    for p, o in g.predicate_objects(s):
        sub.add((s, p, o))
        if isinstance(o, BNode) and o not in seen:
            seen.add(o); fr.append(o)
print(f"\ncandidate roots in t's URI space: {len(cand)}; typed dec:DecisionHolon (excluded): {[short(x) for x in dh]}")
print(f"roots withdrawn ({len(roots)}):")
from collections import Counter
import re
kinds = Counter(re.sub(r"\d+", "N", short(r)) for r in roots)
print("  root shapes:", dict(kinds))
print("  first 15:", [short(r) for r in roots[:15]])
print("  ALL:", " ".join(short(r) for r in roots))
print(f"triples removed: {len(sub)} (bnodes followed: {len(seen) - len(roots)})")
n_before = len(g)
g -= sub
print(f"graph {n_before} -> {len(g)}")

adm = URIRef(f"{t}-admission")
print(f"\n{{t}}-admission survives: {any(g.predicate_objects(adm))}  (triples: {len(list(g.predicate_objects(adm)))})")
for p, o in sorted(g.predicate_objects(adm), key=lambda x: (str(x[0]), str(x[1]))):
    print(f"   {short(p)} -> {short(o) if isinstance(o, URIRef) else repr(str(o))[:80]}")
opts = sorted(set(g.objects(adm, DEC.optionSpace)) | set(g.objects(adm, DEC.chosen)), key=str)
print("option IRIs (optionSpace ∪ chosen):")
for o in opts:
    n_subj = len(list(g.predicate_objects(o)))
    n_obj = len(list(g.subject_predicates(o)))
    print(f"   {short(o)}: as-subject triples={n_subj} as-object triples={n_obj} -> "
          f"{'LOST ALL ITS OWN TRIPLES' if n_subj == 0 else 'kept'}")
inbound = [(short(s), short(p), short(o)) for s, p, o in g if isinstance(o, URIRef)
           and (o == t or str(o).startswith(prefix)) and not any(g.predicate_objects(o))]
print(f"dangling inbound edges to withdrawn IRIs: {len(inbound)}: {inbound[:10]}")

def validate(tag, gg):
    rt = any(gg.subjects(RDF.type, TAB.RecordTable)) or any(gg.subjects(RDF.type, TAB.HierarchicalTable))
    t2 = time.time()
    ok, text, legs = C._validate(gg)
    print(f"\n=== _validate [{tag}] ({time.time()-t2:.0f}s): conforms={ok} refusing legs={legs}")
    print(f"    compile_tables would call _validate here (RecordTable/HierarchicalTable present): {rt}")
    print(f"    RuleSeparatedInkShape in report text: {'RuleSeparatedInk' in text}")
    print(f"    DecisionHolonShape in report text: {'DecisionHolonShape' in text}")
    if not ok:
        print("    --- report text, first 40 lines ---")
        for ln in text.splitlines()[:40]: print("    " + ln)
        srcs = Counter(re.findall(r"Source Shape: (\S+)", text))
        print("    source shapes:", dict(srcs))
        foci = Counter(re.findall(r"Focus Node: (\S+)", text))
        print("    focus nodes:", dict(list(foci.items())[:15]))

validate("withdrawn, no escalation", g)
i = gi[0]
r = rep.regions[i]
escalate_region(g, URIRef(f"{doc}#region{i}"), doc, r.ascii or "(grid rows)", "RULE_SEPARATED_INK",
                TAB.DataGrid, 0.0, PAGE)
validate("withdrawn + escalate_region(region%d)" % i, g)
print(f"\ntotal {time.time()-t0:.0f}s")
