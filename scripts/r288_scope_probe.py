"""R288 scope probe — a MEASUREMENT instrument, not a reader (it changes no compile).

Handoff `docs/superpowers/2026-10-04-r288-table-notes-approaches-handoff.md` part 5. The question:
does a NEURAL worker asked "which of these enumerated tables does this text qualify?", DISPOSED by
reading-order equality, admit exactly the table notes and refuse every title, piece of furniture,
paragraph of prose and stray data row?

Two modes, run from the repo root:

    # 1. census (offline, free): every ignored band on a page carrying >=1 asserted table, plus a
    #    rendered page image per candidate for the human truth judgement. ~10 min, serial.
    env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python \\
        scripts/r288_scope_probe.py census OUT_DIR

    # 2. live (paid): asks the worker, applies the oracle and the verdict rule fixed below.
    ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"') \\
        .venv/bin/python scripts/r288_scope_probe.py live OUT_DIR

PROCEDURAL (CLAUDE.md s8) in the census: raw extraction and rendering only, it decides nothing.
The oracle in `live` is the probe's subject, an AXIOM candidate with no constant: a band's
reading-order set is the asserted tables whose band index precedes it on its page, back to the
previous admitted note on that page.
"""
import base64, glob, re, io, json, os, pathlib, sys, urllib.error, urllib.request
sys.path.insert(0, "src")
import pdfplumber
from rdflib import URIRef

from iladub.etkl.compile import page_bands
from iladub.etkl.document import compile_document
from iladub.etkl.holon import ETKL

MODEL = os.environ.get("R288_MODEL", "claude-haiku-4-5-20251001")
REPEAT = int(os.environ.get("R288_REPEAT", "3"))


def bbox(band):
    words = [w for ln in band.lines for w in ln.words]
    if not words:
        return None
    return (min(w.x0 for w in words), band.top, max(w.x1 for w in words), band.bottom)


def render(path, page_no, tables, target, out_png):
    """The page, asserted tables outlined in blue and labelled A, B, ... in band order, the
    candidate outlined in red."""
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_no]
        im = page.to_image(resolution=110)
        for t in tables:
            x0, top, x1, bot = t["bbox"]
            im.draw_rect((x0 - 2, top - 2, x1 + 2, bot + 2), fill=None, stroke="blue", stroke_width=2)
        x0, top, x1, bot = target
        im.draw_rect((x0 - 3, top - 3, x1 + 3, bot + 3), fill=None, stroke="red", stroke_width=3)
        from PIL import ImageDraw
        img = im.annotated
        draw = ImageDraw.Draw(img)
        s = im.scale
        for t in tables:
            x0, top, _, _ = t["bbox"]
            lx, ly = x0 * s, max(0, top * s - 14)
            draw.rectangle((lx, ly, lx + 26, ly + 13), fill="blue")
            draw.text((lx + 3, ly + 1), t["label"], fill="white")
        img.save(out_png)


def census(out):
    out.mkdir(parents=True, exist_ok=True)
    cases, nulls, skipped = [], [], []
    for path in sorted(glob.glob("corpus/**/*.pdf", recursive=True)):
        doc = pathlib.Path(path).stem
        rep = compile_document(path, validate_shapes=False)
        ignored_text = {str(b): str(rep.graph.value(b, ETKL.bandText) or "")
                        for b in rep.graph.subjects(None, ETKL.IgnoredBand)}
        for page, prep in enumerate(rep.pages):
            repair = frozenset(i for pg, i in rep.repaired_bands if pg == page)
            bands = page_bands(path, page, section_repair_bands=repair)
            regions = prep.regions
            if len(regions) < len(bands):
                skipped.append((doc, page, len(regions), len(bands)))
                continue
            # Regions 0..len(bands)-1 ARE bands 0..len(bands)-1. A data-grid adoption appends its
            # grid region (and a DATAGRID_RESIDUE) after the band loop (compile.py, the R73
            # adoption branch): the grid's ink is the bands it superseded, so its box is their
            # union and its reading-order position is the first of them.
            superseded = [i for i in range(len(bands)) if regions[i].verdict == "superseded"]
            tables, seen = [], set()
            for i, r in enumerate(regions):
                if r.verdict != "asserted" or r.table_uri is None or r.table_uri in seen:
                    continue
                if i < len(bands):
                    pos, box = i, bbox(bands[i])
                elif superseded:
                    boxes = [bbox(bands[j]) for j in superseded if bbox(bands[j])]
                    pos = superseded[0]
                    box = (min(b[0] for b in boxes), min(b[1] for b in boxes),
                           max(b[2] for b in boxes), max(b[3] for b in boxes))
                else:
                    skipped.append((doc, page, "grid with no superseded band", str(r.table_uri)))
                    continue
                seen.add(r.table_uri)
                tables.append({"band": pos, "uri": str(r.table_uri), "bbox": box})
            tables.sort(key=lambda t: t["band"])
            for k, t in enumerate(tables):
                t["label"] = chr(ord("A") + k)   # neutral letters: bfs prints its own T1/T2
            if not tables:
                continue
            for i, r in enumerate(regions[:len(bands)]):
                if r.verdict != "ignored":
                    continue
                # The address join, measured, not assumed: the text the compile CARRIED on this
                # page's `#ignored{i}`. A carve (R261's grand total) can leave the carried text a
                # remainder of the band, so the candidate is the band's lines that the carried
                # text holds, not the whole band.
                carried = next((v for k, v in ignored_text.items()
                                if re.search(rf"/p{page}(/r2)?#ignored{i}$", k)), None)
                lines = [ln for ln in bands[i].lines
                         if carried is not None
                         and " ".join(w.text for w in ln.words) in carried.split("\n")]
                if not lines:
                    skipped.append((doc, page, i, "no carried line"))
                    continue
                target = (min(w.x0 for ln in lines for w in ln.words), lines[0].top,
                          max(w.x1 for ln in lines for w in ln.words), lines[-1].bottom)
                text = "\n".join(" ".join(w.text for w in ln.words) for ln in lines)
                png = out / f"{doc[:24]}_p{page}_b{i}.png"
                render(path, page, tables, target, png)
                cases.append({"doc": doc, "page": page, "band": i, "kind": "ignored",
                              "joined": text == carried, "words": len(text.split()), "text": text,
                              "reason": r.reason, "tables": tables, "png": png.name, "path": path})
            # NULL CONTROL: the last line of each asserted table, asked as if it were a band at
            # its table's position. It must be refused.
            for t in tables:
                if t["band"] >= len(bands) or regions[t["band"]].verdict != "asserted":
                    continue   # a grid: its last line is not one band's
                ln = bands[t["band"]].lines[-1]
                lb = (min(w.x0 for w in ln.words), ln.top, max(w.x1 for w in ln.words), ln.bottom)
                png = out / f"{doc[:24]}_p{page}_null{t['band']}.png"
                render(path, page, tables, lb, png)
                nulls.append({"doc": doc, "page": page, "band": t["band"], "kind": "null",
                              "text": " ".join(w.text for w in ln.words), "tables": tables,
                              "png": png.name, "path": path})
        print(f"### {doc} pages={len(rep.pages)} candidates="
              f"{sum(c['doc'] == doc for c in cases)}", flush=True)
    (out / "cases.json").write_text(json.dumps({"cases": cases, "nulls": nulls,
                                                "skipped": skipped}, indent=1))
    for c in cases:
        print(f"  {c['doc'][:24]:<24} p{c['page']} b{c['band']:<3} {c['words']:>4}w "
              f"join={'ok' if c['joined'] else 'MISS'} :: {c['text'][:110]!r}")
    print(f"candidates={len(cases)} nulls={len(nulls)} skipped={skipped}")

PROMPT = """The image shows one page of a document. The tables on it are outlined in blue and
labelled {labels}. One block of text is outlined in red.

READ THE PAGE AS A PERSON READS IT. Is the red text a note on one or more of the labelled tables:
text that tells the reader how to read those tables' contents? If it is, which tables does it apply
to? If it is not a note on any labelled table, answer with an empty list.

Reply with JSON only: {{"tables": [<labels, or nothing>]}}"""


def ask(png_bytes, labels):
    """A frozenset of labels, or "UNPARSED" / "HTTP<code>". Closed contract: exactly the key
    `tables`, a list of distinct labels drawn from this page's labels; anything else is UNPARSED."""
    body = {"model": MODEL, "max_tokens": 200, "messages": [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                     "data": base64.b64encode(png_bytes).decode()}},
        {"type": "text", "text": PROMPT.format(labels=", ".join(labels))}]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
                                 {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                                  "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        out = json.load(urllib.request.urlopen(req))["content"][0]["text"]
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}"
    try:
        obj = json.loads(out[out.index("{"):out.rindex("}") + 1])
        ts = obj["tables"]
        if set(obj) == {"tables"} and isinstance(ts, list) and len(set(ts)) == len(ts) \
                and set(ts) <= set(labels):
            return frozenset(ts)
    except Exception:
        pass
    return "UNPARSED"


def majority(answers):
    """The answer at least 2 of 3 repeats gave (strictly more than half), else None."""
    for a in answers:
        if answers.count(a) * 2 > len(answers):
            return a
    return None


def reading_order(tables, band, floor):
    """THE ORACLE (AXIOM candidate, no constant): the asserted tables whose band precedes `band`
    on its page, after `floor`, the band of the previous admitted note on that page (-1 if none)."""
    return frozenset(t["label"] for t in tables if floor < t["band"] < band)


def live(out):
    data = json.loads((out / "cases.json").read_text())
    truth = {(d, p, b) for d, p, b in json.loads((out / "truth.json").read_text())}
    rows, admitted = [], set()
    by_page = {}
    for c in data["cases"] + data["nulls"]:
        by_page.setdefault((c["doc"], c["page"]), []).append(c)
    for (doc, page), cs in sorted(by_page.items()):
        floor = -1
        # Real bands in page order; a null is asked at its table's position against the floor
        # in force there, and never moves the floor.
        for c in sorted(cs, key=lambda c: (c["band"], c["kind"] == "ignored")):
            labels = [t["label"] for t in c["tables"]]
            png = (out / c["png"]).read_bytes()
            answers = [ask(png, labels) for _ in range(REPEAT)]
            m = majority(answers)
            ro = reading_order(c["tables"], c["band"], floor)
            ok = isinstance(m, frozenset) and bool(m) and m == ro
            if ok and c["kind"] == "ignored":
                floor = c["band"]
                admitted.add((doc, page, c["band"]))
            rows.append((c, answers, m, ro, ok))
            fmt = lambda a: "{" + ",".join(sorted(a)) + "}" if isinstance(a, frozenset) else str(a)
            print(f"{c['kind']:<7} {doc[:22]:<22} p{page} b{c['band']:<3} "
                  f"truth={'NOTE' if (doc, page, c['band']) in truth and c['kind'] == 'ignored' else '-   '} "
                  f"ans={' '.join(fmt(a) for a in answers):<28} ro={fmt(ro):<12} "
                  f"{'ADMIT' if ok else 'refuse'} :: {c['text'][:60]!r}", flush=True)
    null_admits = [r for r in rows if r[0]["kind"] == "null" and r[4]]
    missed, extra = truth - admitted, admitted - truth
    holds = not missed and not extra and not null_admits
    print(f"\nadmitted={sorted(admitted)}\nmissed notes={sorted(missed)}\n"
          f"admitted non-notes={sorted(extra)}\nnull admits={len(null_admits)}\n"
          f"VERDICT: {'HOLDS' if holds else 'REFUTED'}")


if __name__ == "__main__":
    mode, out = sys.argv[1], pathlib.Path(sys.argv[2])
    if mode == "census":
        census(out)
    elif mode == "live":
        live(out)
