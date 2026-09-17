"""Score a docling-graph extraction of a dense ruled table ROW BY ROW against the PDF's own text.

NOT iladub code. A third-party probe for the graincorp-stem dense-page arm recorded in
docs/superpowers/2026-09-17-neural-workers-evidence.md. Nothing in iladub imports it.

WHAT IT CHECKS: every extracted Slot's reference is looked up on the page; the words sharing that
reference's baseline are the row's ground truth; each extracted time, exporter and commodity must
appear ON THAT ROW. A value present on the page but on another row is a MISATTRIBUTION, which a
verbatim-provenance check cannot see.

IT IS LENIENT, deliberately stated: values repeat across rows, so a wrong value that also occurs on
the right row passes. The count it prints is a floor.

PROCEDURAL, justified: exact string membership over extracted words; no reading judgement.

USAGE: python dense_page_row_check.py <pdf> <page-index> <graph.json>
"""

import collections
import json
import re
import sys

import pdfplumber


def main() -> None:
    pdf, page, graph_path = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    graph = json.load(open(graph_path))
    nodes = {n["id"]: n for n in graph["nodes"]}
    edges = graph.get("edges") or graph.get("links")
    words = pdfplumber.open(pdf).pages[page].extract_words()
    truth = {}
    for w in words:
        if re.fullmatch(r"\d{5}", w["text"]):
            row = sorted((x for x in words if abs(x["top"] - w["top"]) < 3), key=lambda x: x["x0"])
            truth[w["text"]] = " ".join(x["text"] for x in row)
    linked = collections.defaultdict(list)
    for e in edges:
        s, t = nodes.get(e["source"]), nodes.get(e["target"])
        if s and t and s.get("label") == "Slot" and t.get("label") in ("Exporter", "Commodity"):
            linked[s["slot_reference_number"]].append(next((v for k, v in t.items() if k.endswith("_name")), None))
    slots = [n for n in nodes.values() if n.get("label") == "Slot"]
    print(f"rows on page {len(truth)} | slots extracted {len(slots)} | "
          f"real references {sum(s['slot_reference_number'] in truth for s in slots)}")
    clean = 0
    for s in slots:
        ref = s["slot_reference_number"]
        row = truth.get(ref, "")
        got = [ev.get("event_time") for ev in s.get("shipment_event", []) if ev.get("event_time")] + linked[ref]
        wrong = [v for v in got if v and v not in row]
        clean += not wrong
        if wrong:
            print(f"  {ref}: not on its own row -> {wrong}\n     row: {row}")
    print(f"slots clean {clean} | slots carrying another row's value {len(slots) - clean}")


if __name__ == "__main__":
    main()
