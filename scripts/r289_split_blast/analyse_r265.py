"""Summarise the R265 counterfactual columns of harness JSONL: per document, unique bands where
OLD' != OLD (R265's own effect on the shipped split), NEW != OLD (candidate rule, today's typing),
NEW' != OLD' (candidate rule over R265-retyped cells); then every band in any of those sets."""
import json
import os
import sys

rows = []
for f in sys.argv[1:]:
    recs = [json.loads(l) for l in open(f)]
    done = [r for r in recs if r.get("done")]
    ax = {}
    for r in recs:
        if r.get("done") or r.get("old_rq") is None:
            continue
        ax.setdefault(r["band_key"], r)
    a = {k for k, r in ax.items() if r["old_r265"] != r["old_rq"]}
    b = {k for k, r in ax.items() if r["new"] != r["old_rq"]}
    c = {k for k, r in ax.items() if r["new_r265"] != r["old_r265"]}
    print(f"{os.path.basename(f)}: done={bool(done)} score={done[0]['score'] if done else None} "
          f"axiom_bands={len(ax)} r265_moves_old={len(a)} rule_moves_today={len(b)} "
          f"rule_moves_after_r265={len(c)}")
    for k in sorted(a | b | c):
        rows.append(ax[k])
print()
for r in rows:
    L = r["lines"]
    print(f"== {r['doc']} {r['band_key']} pages={r['pages']} OLD={r['old_rq']} NEW={r['new']} "
          f"OLD'={r['old_r265']} NEW'={r['new_r265']}")
    for v in sorted({x for x in (r["old_rq"], r["new"], r["old_r265"], r["new_r265"]) if x is not None}):
        print(f"   line[{v}]: {L[v][:100]}")
    print(f"   dirty today: {r['dirty_cells']}")
    print(f"   dirty R265': {r.get('dirty_cells_r265')}")
