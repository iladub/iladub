"""M3 (scratch, pure computation): evaluate R1/R3 for each reader answer K, S = OLD, over the band's
typed evidence graph rebuilt from M1's logged evidence (celltype.grid_evidence(gcells, ncols,
unshown=...)) — same "data column" and "D" definitions as header-body-split-datacols.rq, same
normalised cell type as cells.rq.

R1: row K holds no non-abstaining cell whose normalised type is not in its data column's D set.
R3: for K > S, rows S..K-1 hold no non-abstaining cell whose normalised type IS in its data
    column's D set. (vacuously true for K <= S)
admitted = K >= S and R1 and R3.

usage: .venv/bin/python m3_oracle.py <bands.json> <m2.jsonl>
"""
import json
import os
import sys

REPO = "/Volumes/WD Green/dev/git/iladub"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "src"))
from iladub.etkl import celltype  # noqa: E402

DATACOLS = os.path.join(HERE, "header-body-split-datacols.rq")
CELLS = os.path.join(HERE, "cells.rq")


def q(path, g):
    return list(g.query(open(path, encoding="utf-8").read()))


bands = {b["band_key"]: b for b in json.load(open(sys.argv[1]))}
answers = [json.loads(l) for l in open(sys.argv[2]) if '"done"' not in l]
print("| role | doc | band | nlines | S=OLD | NEW | K | K vs S | K vs NEW | R1 | R3 | admitted | adm K==NEW |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for a in answers:
    b = bands[a["band_key"]]
    g = celltype.grid_evidence([tuple(x) for x in b["gcells"]], b["ncols"],
                               unshown=[tuple(x) for x in b["unshown"]] or None)
    D = {}
    for r in q(DATACOLS, g):
        D.setdefault(int(r.col), set()).add(r.D)
    cells = [(int(r.row), int(r.col), r.ct) for r in q(CELLS, g)]
    S, NEW = b["old"], b["new"]
    seen = set()
    for ans in a["answers"]:
        if "k" not in ans:
            print(f"| {b['role']} | {b['doc'].split('/')[-1][:12]} | {b['band_key']} | | {S} | {NEW} | ERR | | | | | | |")
            continue
        K = ans["k"]
        if K in seen:
            continue  # one row per distinct answer
        seen.add(K)
        r1_viol = [(r, c, str(ct).rsplit('#', 1)[-1]) for r, c, ct in cells
                   if r == K and c in D and ct not in D[c]]
        r3_viol = [(r, c, str(ct).rsplit('#', 1)[-1]) for r, c, ct in cells
                   if K > S and S <= r < K and c in D and ct in D[c]]
        R1, R3 = not r1_viol, not r3_viol
        adm = K >= S and R1 and R3
        vs = "<" if K < S else ("=" if K == S else ">")
        vn = "n/a" if NEW is None else ("<" if K < NEW else ("=" if K == NEW else ">"))
        cnt = sum(1 for x in a["answers"] if x.get("k") == K)
        print(f"| {b['role']} | {b['doc'].split('/')[-1][:12]} | {b['band_key']} | {b['nlines']} | {S} | "
              f"{NEW} | {K} (x{cnt}) | {vs} | {vn} | {R1}{'' if R1 else ' ' + str(r1_viol[:4])} | "
              f"{R3}{'' if R3 else ' ' + str(r3_viol[:4])} | {adm} | {adm and K == NEW} |")
