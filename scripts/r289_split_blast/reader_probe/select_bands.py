"""Select M2/M3 bands from M1 logs: every distinct trigger band_key + named controls."""
import json
CONTROLS = {  # doc -> [(band_key, note)]
    "gstem": [("1cfea548c667", "control p1 HIER split 3"), ("8b8989546f59", "control p0 HIER split 4")],
    "apple": [("178e26749735", "control p2 HIER Investing"), ("2ca3ee4e23f6", "control p2 HIER Financing"),
              ("133ef9cb0591", "extra: p0 two-line header (non-HIER caller)")],
    "who": [("8a8b7efb70e0", "control p0 Z-scores header (non-HIER caller)"),
            ("aa5136048381", "control p1 Z-scores header (non-HIER caller)"),
            ("a334f1d9432e", "extra: p0 HIER headerless continuation, R166 class (split 1 known WRONG)")],
}
out = []
for n in "cbh gstem gcap ons bfs apple who".split():
    recs = [json.loads(l) for l in open(f"m1-{n}.jsonl") if '"done"' not in l]
    first = {}
    for r in recs:
        if r["old_rq"] is None:
            continue
        if r["band_key"] not in first or (first[r["band_key"]]["enclosing"] != "compile_tables"
                                         and r["enclosing"] == "compile_tables"):
            first[r["band_key"]] = r
    def mk(r, role):
        return {k: r[k] for k in ("doc", "band_key", "pdf_path", "page_number", "nlines", "ncols",
                                   "gcells", "unshown", "geom", "lines", "new")} | \
               {"old": r["old_rq"], "role": role}
    for k, r in first.items():
        if r["new"] != r["old_rq"]:
            out.append(mk(r, f"TRIGGER {n}"))
    for k, note in CONTROLS.get(n, []):
        r = first[k]
        assert r["new"] == r["old_rq"], k
        out.append(mk(r, f"CONTROL {n}: {note}"))
json.dump(out, open("bands.json", "w"))
for b in out:
    print(b["role"], b["band_key"], "pg", b["page_number"], "nl", b["nlines"], "nc", b["ncols"], "OLD", b["old"], "NEW", b["new"])
