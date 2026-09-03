"""section_repair_census — WHY loop Q's section repair does or does not fire on a document.

Raised by R161 (apple p0/p2: eight `REGION_TILING_FAILED` bands, `repaired_bands == ()`), whose
closing condition was *"a measurement of why `sectiongraph.section_candidates` recognizes no
candidate section ... dumping its own evidence graph"*. This is that instrument, committed so the
next document that raises the same question is measured rather than reasoned about.

Per page it prints three things, in the order the repair driver consults them:

1. the BAND census — for every band: line/rule/hrule counts, the region verdict + reason, and
   the two signature facts `sectiongraph` would emit (`_leading_box_y` -> header box text,
   `_rule_xs_signature`), so a band that emits no evidence says which of the two it lacks;
2. the section EVIDENCE graph and the groups `section_candidates` derives from it — the exact
   input and output of `section-repeat.rq`;
3. for every band the tiling membrane refused, the SHACL shapes that refused it — obtained by
   wrapping `region_tiles` (READ-ONLY: the wrapper calls the same `membrane.validate` and
   returns the same boolean; nothing about the compile changes).

Usage:
    PYTHONPATH=. .venv/bin/python scripts/section_repair_census.py corpus/financial/apple-fy2026q3-statements.pdf
    ... --pages 0,2 --json out.json

PROCEDURAL by CLAUDE.md §8: this is measurement glue over existing PROCEDURAL/AXIOM layers; it
decides nothing and carries no constant.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from rdflib import Graph, Namespace

SH = Namespace("http://www.w3.org/ns/shacl#")


def refusing_shapes(report: Graph | str) -> list[tuple[str, str, str]]:
    """(source shape local name, result message, focus node local name) for every
    `sh:Violation` in a SHACL validation report (a Graph, or its Turtle text)."""
    rg = report if isinstance(report, Graph) else Graph().parse(data=str(report), format="turtle")
    rows = []
    for r in rg.subjects(SH.resultSeverity, SH.Violation):
        rows.append((str(rg.value(r, SH.sourceShape)).split("#")[-1],
                     str(rg.value(r, SH.resultMessage) or ""),
                     str(rg.value(r, SH.focusNode)).split("#")[-1]))
    return sorted(rows)


def census(pdf: str, pages: list[int]) -> dict:
    from iladub.etkl import compile as C, membrane, tiling
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import (_header_box_text, _leading_box_y, _rule_xs_signature,
                                          section_candidates, section_evidence)

    refusals: list[list[tuple[str, str, str]]] = []

    def observed_region_tiles(graph):
        conforms, report = membrane.validate(graph, tiling._TILING_SHAPES, tiling._ONT)
        if not conforms:
            refusals.append(refusing_shapes(report))
        return conforms

    original = tiling.region_tiles
    tiling.region_tiles = observed_region_tiles     # compile.py imports the name inside the function, per call
    out: dict = {}
    try:
        for p in pages:
            refusals.clear()
            bands = page_bands(pdf, p)
            rep = C.compile_tables(pdf, page_number=p)
            rows = []
            for i, b in enumerate(bands):
                r = rep.regions[i] if i < len(rep.regions) else None
                rules = tuple(b.rules)
                rows.append(dict(
                    band=i, lines=len(b.lines), rules=len(rules), hrules=len(b.hrules),
                    verdict=getattr(r, "verdict", None), reason=getattr(r, "reason", None),
                    header_box_y=(_leading_box_y(b, rules) if rules else None),
                    header_box_text=(_header_box_text(b, rules) if rules else None),
                    rule_sig=_rule_xs_signature(rules),
                    first_line=" ".join(w.text for w in b.lines[0].words)[:70] if b.lines else ""))
            ruled = [(i, b, tuple(b.rules)) for i, b in enumerate(bands) if b.rules]
            ev = section_evidence(ruled) if len(ruled) >= 2 else None
            groups = section_candidates(ruled) if len(ruled) >= 2 else None
            sigs = Counter(r["rule_sig"] for r in rows if r["rule_sig"])
            out[p] = dict(score=rep.score, n_bands=len(bands), n_ruled=len(ruled),
                          distinct_rule_sigs=len(sigs), bands=rows,
                          evidence_ttl=(ev.serialize(format="turtle") if ev is not None else None),
                          groups=(list(groups) if groups is not None else "skipped (<2 ruled bands)"),
                          tiling_refusals=[dict(shapes=dict(Counter(s for s, _, _ in rr)),
                                                focus=[f for _, _, f in rr],
                                                message=(rr[0][1] if rr else "")) for rr in refusals])
    finally:
        tiling.region_tiles = original
    return out


def report(out: dict) -> str:
    lines = []
    for p, d in out.items():
        lines.append(f"page {p}: score={d['score']:.4f} bands={d['n_bands']} ruled={d['n_ruled']} "
                     f"distinct rule-x signatures={d['distinct_rule_sigs']} groups={d['groups']}")
        lines.append("  band lines rules hrules verdict    reason                header-box-y        header-box-text | first line")
        for r in d["bands"]:
            y = r["header_box_y"]
            y = f"{y[0]:.1f}-{y[1]:.1f}" if isinstance(y, tuple) else str(y)
            lines.append(f"  {r['band']:>4} {r['lines']:>5} {r['rules']:>5} {r['hrules']:>6} {str(r['verdict']):<10} "
                         f"{str(r['reason']):<21} {y:<19} {str(r['header_box_text'])[:28]!r:<30} | {r['first_line']}")
        for rr in d["tiling_refusals"]:
            lines.append(f"  tiling refused {rr['focus'][0].split('-')[0]}: {rr['shapes']} — {rr['message'][:90]}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pdf")
    ap.add_argument("--pages", default="0,1,2")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    out = census(a.pdf, [int(x) for x in a.pages.split(",")])
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=str)
    print(report(out))


if __name__ == "__main__":
    sys.exit(main())
