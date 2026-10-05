"""M2 (scratch): ask the live CountHeaderLines reader x3 on each selected band, from M1's logged
evidence (no compile). Listing built in EXACTLY headerlines.listing_of's format from
headers._grid_cells tuples; crop = unshownink.render_region(pdf_path, page_number, band) on a
minimal band object rebuilt from the logged geometry (render_region reads only
band.lines[*].words[*].x0/x1 and band.top/bottom).

The module cache _HEADER_LINES_CACHE dedupes identical questions, so it is CLEARED before each
repeat (otherwise answers 2 and 3 would be replays of 1). Nothing is written to readings/.

usage: BAML_LIVE=1 ANTHROPIC_API_KEY=... .venv/bin/python m2_reader.py <bands.json> <out.jsonl>
"""
import json
import os
import sys
from types import SimpleNamespace as NS

REPO = "/Volumes/WD Green/dev/git/iladub"
sys.path.insert(0, os.path.join(REPO, "src"))
sys.path.insert(0, REPO)  # baml_client lives at the repo root
os.environ.pop("ILADUB_RECORD_READINGS", None)

from iladub.etkl import headerlines  # noqa: E402
from iladub.etkl.unshownink import render_region  # noqa: E402


def listing(gcells, ncols, nlines):
    text = {(r, c): headerlines._cell_line(t) for r, c, t in gcells}
    return "\n".join(
        f"L{k}: " + " | ".join(text.get((k, col), "") for col in range(ncols))
        for k in range(nlines))


def band_of(geom):
    return NS(top=geom["top"], bottom=geom["bottom"],
              lines=[NS(words=[NS(x0=a, x1=b) for a, b in ln]) for ln in geom["lines"]])


assert headerlines.baml_header_lines_available(), "BAML_LIVE=1 and baml_client required"
bands = json.load(open(sys.argv[1]))
out = open(sys.argv[2], "w")
reader = headerlines.BamlHeaderLinesReader()
for b in bands:
    pdf = b["pdf_path"]
    crop = render_region(pdf, b["page_number"], band_of(b["geom"]))
    lst = listing(b["gcells"], b["ncols"], b["nlines"])
    answers = []
    for i in range(3):
        headerlines._HEADER_LINES_CACHE.clear()
        try:
            r = reader.count_header_lines(crop, b["ncols"], lst)
            answers.append({"k": r.header_lines, "note": r.note})
        except Exception as e:  # recorded, never swallowed silently
            answers.append({"error": repr(e)[:300]})
    rec = {"band_key": b["band_key"], "doc": b["doc"], "role": b["role"], "old": b["old"],
           "new": b["new"], "nlines": b["nlines"], "ncols": b["ncols"], "answers": answers,
           "listing": lst, "crop_bytes": len(crop)}
    out.write(json.dumps(rec) + "\n")
    out.flush()
    print(b["role"], b["doc"], b["band_key"], "OLD", b["old"], "NEW", b["new"],
          "->", [a.get("k", a.get("error")) for a in answers], flush=True)
out.close()
print(json.dumps({"done": True, "n": len(bands)}))
