"""The residue register as a GRAPH, read from what the rows already carry (2026-09-11).

Nodes are the register's rows; an edge R_a -> R_b exists iff row a's text in
`residues-open.md` / `residues-closed.md` carries the wikilink `[[R_b]]`. Criteria come from
`tests/arc-manifest.ttl`: an edge criterion -> row for every `prog:blockedBy "R…"`. No new
convention is introduced: the graph is what the register already says about itself.

It prints the figures the maintainer asked for on 2026-09-11 (handoff
`docs/superpowers/2026-09-11-the-register-serves-the-arc-handoff.md` § 2b): hubs by in-degree,
connected components, how many rows are isolated, and where the arc touches the live component.
With `--json PATH` it also writes the node/edge lists the graph artifact was drawn from.

PROCEDURAL by CLAUDE.md §8: it reads two files and counts. It decides nothing.

Run from the repo root:

    .venv/bin/python scripts/residue_graph.py [--json out.json]
"""
from __future__ import annotations

import collections
import json
import re
import sys

OPEN = "docs/superpowers/residues-open.md"
CLOSED = "docs/superpowers/residues-closed.md"
INDEX = "docs/superpowers/residues.md"
ARC = "tests/arc-manifest.ttl"


def read_rows():
    rows = {}
    for f in (OPEN, CLOSED):
        for line in open(f, encoding="utf-8"):
            m = re.match(r"\| ~?~?R(\d+)~?~?", line)
            if not m:
                continue
            n = int(m.group(1))
            rows[n] = {int(x) for x in re.findall(r"\[\[R(\d+)\]\]", line) if int(x) != n}
    status, label = {}, {}
    # The status word is the FIRST word of the cell; a parenthetical qualifier may follow
    # (`open (half (a) done)`, `open (parked 2026-09-11)`). The reader of record for the index
    # is `tests/test_residue_register_integrity.py:40`, whose status group this one copies.
    for line in open(INDEX, encoding="utf-8"):
        m = re.match(r"\| ~?~?R(\d+)~?~? \| ([A-Za-z]+)[^|]*\| (.*?) \|", line)
        if m:
            status[int(m.group(1))] = m.group(2)
            t = re.sub(r"\*\*|`|\[\[|\]\]", "", m.group(3)).strip()
            label[int(m.group(1))] = t[:150] + ("…" if len(t) > 150 else "")
    return rows, status, label


def read_criteria():
    crit = {}
    txt = open(ARC, encoding="utf-8").read()
    for block in re.split(r"\n(?=prog:criterion:)", txt):
        m = re.match(r"prog:criterion:(\S+)", block)
        if not m or not block.startswith("prog:criterion:"):
            continue
        bl = re.search(r"prog:blockedBy([^;.]*)", block)
        if bl:
            crit[m.group(1)] = [int(x) for x in re.findall(r'"R(\d+)"', bl.group(1))]
    return crit


def main(argv):
    rows, status, label = read_rows()
    crit = read_criteria()
    edges = [(a, b) for a, refs in rows.items() for b in refs if b in rows]
    indeg = collections.Counter(b for _, b in edges)
    parent = {n: n for n in rows}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in edges:
        parent[find(a)] = find(b)
    comps = collections.defaultdict(list)
    for n in rows:
        comps[find(n)].append(n)
    big = max(comps.values(), key=len)
    front = {r for v in crit.values() for r in v}
    print(f"rows {len(rows)}  row->row links {len(edges)}  rows with any link "
          f"{len({a for a, _ in edges} | {b for _, b in edges})}  isolated "
          f"{sum(1 for c in comps.values() if len(c) == 1)}")
    print(f"components {len(comps)}; largest {len(big)} rows R{min(big)}..R{max(big)}, "
          f"{sum(status.get(n) == 'open' for n in big)} open")
    print("hubs (in-degree >= 5):",
          [(f"R{n}", c, status.get(n)) for n, c in indeg.most_common() if c >= 5])
    print(f"criterion->row edges {sum(len(v) for v in crit.values())}; frontier rows {len(front)}, "
          f"in the largest component: {sorted(n for n in front if n in big)}")
    if "--json" in argv:
        out = argv[argv.index("--json") + 1]
        json.dump({"nodes": [{"id": n, "status": status.get(n), "label": label.get(n, ""),
                              "deg": indeg[n] + sum(1 for a, _ in edges if a == n)} for n in rows],
                   "edges": [{"s": a, "t": b} for a, b in edges], "crit": crit},
                  open(out, "w", encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
