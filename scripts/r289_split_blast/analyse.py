"""Summarise harness JSONL files: calls, unique bands, OLD==NEW, changed, NEW=None; dump changed bands."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
files = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "*.jsonl")))
allchanged = []
for f in files:
    recs = [json.loads(l) for l in open(f)]
    done = [r for r in recs if r.get("done")]
    calls = [r for r in recs if not r.get("done")]
    ax = [r for r in calls if r["old_rq"] is not None]
    none_rq = [r for r in calls if r["old_rq"] is None]
    mism = [r for r in ax if r["old_mirror"] != r["old_rq"]]
    same = [r for r in ax if r["new"] == r["old_rq"]]
    newnone = [r for r in ax if r["new"] is None]
    chg = [r for r in ax if r["new"] is not None and r["new"] != r["old_rq"]]
    ub = lambda rs: len({r["band_key"] for r in rs})
    print(f"{os.path.basename(f)}: done={bool(done)} score={done[0]['score'] if done else None} "
          f"calls={len(calls)} axiom={len(ax)} (bands {ub(ax)}) rq_none={len(none_rq)} (bands {ub(none_rq)}) "
          f"same={len(same)} (bands {ub(same)}) changed={len(chg)} (bands {ub(chg)}) "
          f"new_none={len(newnone)} (bands {ub(newnone)}) mirror_mismatch={len(mism)}")
    seen = set()
    for r in chg + newnone:
        if r["band_key"] in seen:
            continue
        seen.add(r["band_key"])
        allchanged.append(r)
print()
for r in allchanged:
    L = r["lines"]
    o, n = r["old_rq"], r["new"]
    print(f"== {r['doc']} pages={r['pages']} nlines={r['nlines']} OLD={o} NEW={n} cands={r['cands']} dirty={r['dirty']}")
    print(f"   percol={r['percol']}")
    print(f"   OLD line[{o}]: {L[o][:90]}")
    if n is not None:
        print(f"   NEW line[{n}]: {L[n][:90]}")
        for i in range(min(o, n), max(o, n)):
            print(f"     between[{i}]: {L[i][:90]}")
    print(f"   header-context lines[0:{(n or o)+1}]:")
    for i in range(0, (n or o) + 1):
        print(f"       {i}: {L[i][:90]}")
