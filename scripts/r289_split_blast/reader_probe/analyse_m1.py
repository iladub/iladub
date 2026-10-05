"""M1 analysis (scratch): per-doc call counts, OLD!=NEW calls, distinct trigger bands, trigger table.
usage: .venv/bin/python analyse_m1.py  (reads m1-*.jsonl beside it)"""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["cbh", "gstem", "gcap", "ons", "bfs", "apple", "who"]
for name in NAMES:
    p = os.path.join(HERE, f"m1-{name}.jsonl")
    if not os.path.exists(p):
        print(name, "MISSING"); continue
    lines = [json.loads(l) for l in open(p)]
    done = [l for l in lines if l.get("done")]
    recs = [l for l in lines if not l.get("done")]
    axiom = [r for r in recs if r.get("old_rq") is not None]
    trig = [r for r in axiom if r["new"] != r["old_rq"]]
    mism = sum(1 for r in axiom if r["old_mirror"] != r["old_rq"])
    fin = sum(1 for r in recs if r["old_final"] != r["old_rq"])
    tb = {}
    for r in trig:
        tb.setdefault(r["band_key"], []).append(r)
    print(f"## {name}: score={done[0]['score'] if done else 'NO DONE LINE'} calls={len(recs)} "
          f"axiom_calls={len(axiom)} distinct_axiom_bands={len({r['band_key'] for r in axiom})} "
          f"OLD!=NEW calls={len(trig)} trigger_bands={len(tb)} mirror_mismatch={mism} "
          f"final!=rq={fin} new_None={sum(1 for r in axiom if r['new'] is None)}")
    callers = collections.Counter(r["caller"].rsplit(":", 1)[0] for r in recs)
    print("   callers:", dict(callers))
    for k, rs in tb.items():
        r = rs[0]
        cs = sorted({x["caller"].replace("iladub.etkl.", "") for x in rs})
        pg = sorted({(x["page_number"], x["enclosing"]) for x in rs}, key=str)
        old, new = r["old_rq"], r["new"]
        dirty_old = [d for d in r["dirty_cells"] if d[0] == old]
        print(f"   TRIGGER {k} pages(word)={r['pages']} page_number/encl={pg} nlines={r['nlines']} "
              f"OLD={old} NEW={new} ncalls={len(rs)}")
        print(f"      callers={cs}")
        print(f"      L[OLD]={r['lines'][old]!r}")
        print(f"      L[NEW]={r['lines'][new]!r}" if new is not None else "      L[NEW]=None")
        print(f"      dirty@OLD={dirty_old}")
