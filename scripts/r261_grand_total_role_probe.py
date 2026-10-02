"""P4 / P4b — loop (b) of the R261 totals family: can a reader tell a total of totals from a table's
total? Evidence: `docs/superpowers/2026-10-02-r261-grand-total-role-probe.md`.

P3 (`scripts/r261_total_question_probe.py`, evidence `2026-10-01-r261-totals-family-evidence.md`
§ 6.4) refuted a yes/no "is {value} the grand total?" asked over a union crop: the port totals drew
`yes` too. This probe asks a different question — the ROLE of one number, marked on the image with a
red box, as a closed enum — of the same population (cbh p0's `1,951,264` and its four port totals)
plus one in-table cell as an extra control.

CROP=strip    P4:  a hand-picked strip, pt (600, 60, 1000, 700). A tuned constant (CLAUDE.md § 8):
                   kept only as the first measurement, never as a production crop.
CROP=derived  P4b: the union of the four operand totals' D7 table-level crops (each total's previous
                   band through its own line, as `printedtotal.crop_table` crops one) plus the
                   candidate line — derived from the bands, no constant but the D7 4 pt margin.

Decision rule, fixed before either run: holds iff `1,951,264` -> total_of_totals x3 AND no null ask
-> total_of_totals.

Run from the repo root (the API key is read the way the R261 probes read it; never printed):

    ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"') \\
      CROP=derived REPEAT=3 PYTHONPATH="$PWD" .venv/bin/python scripts/r261_grand_total_role_probe.py
"""
import base64, glob, io, json, os, sys, urllib.request, urllib.error
sys.path.insert(0, "src")
import pdfplumber

MODEL = "claude-haiku-4-5-20251001"
REPEAT = int(os.environ.get("REPEAT", "3"))
CROP = os.environ.get("CROP", "derived")
GRAND = "1,951,264"
PORTS = ["374,904", "737,289", "660,363", "178,708"]
CELL = "22,858"  # last Volume cell of ESPERANCE: a value inside a table, expected `other`
STRIP = (600, 60, 1000, 700)
ALLOWED = ("table_total", "total_of_totals", "other", "cannot_tell")
PROMPT = """The image shows part of a page. One number is marked with a red box: {value}.

READ IT AS A PERSON READS THE PAGE. What is the number in the red box?

Answer exactly one of:
- table_total: the total of the one table directly above it.
- total_of_totals: a total that sums the totals of several tables.
- other: something else (a value inside a table, a note, a label, ...).
- cannot_tell: the image does not let a reader decide.

Reply with JSON only: {{"answer": "table_total" | "total_of_totals" | "other" | "cannot_tell"}}"""


def ask(png, text):
    """One of ALLOWED, or "UNPARSED" / "HTTP<code>". Closed: any reply that is not exactly
    {"answer": one of ALLOWED} is UNPARSED."""
    body = {"model": MODEL, "max_tokens": 300, "messages": [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                     "data": base64.b64encode(png).decode()}},
        {"type": "text", "text": text}]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
                                 {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                                  "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        out = json.load(urllib.request.urlopen(req))["content"][0]["text"]
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}"
    try:
        obj = json.loads(out[out.index("{"):out.rindex("}") + 1])
        a = obj.get("answer")
        return a if a in ALLOWED and set(obj) == {"answer"} else "UNPARSED"
    except Exception:
        return "UNPARSED"


def derived_box(path, page):
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import compile_document
    rep = compile_document(path, validate_shapes=False)
    bands = page_bands(path, 0, section_repair_bands=frozenset(i for pg, i in rep.repaired_bands if pg == 0))

    def lone(text):
        hits = [(i, ln) for i, b in enumerate(bands) for ln in b.lines
                if len(ln.words) == 1 and ln.words[0].text == text]
        if len(hits) != 1:
            raise SystemExit(f"{text}: {len(hits)} lone lines, expected 1")
        return hits[0]

    words, tops, bots = [], [], []
    for v in PORTS:
        i, ln = lone(v)
        tb = bands[i - 1]
        print(f"operand {v}: table band {i - 1}, {len(tb.lines)} lines", flush=True)
        words += [w for l in tb.lines for w in l.words] + list(ln.words)
        tops.append(tb.top); bots.append(ln.bottom)
    _, gl = lone(GRAND)
    words += list(gl.words); bots.append(gl.bottom)
    return (max(0, min(w.x0 for w in words) - 4), max(0, min(tops) - 4),
            min(float(page.width), max(w.x1 for w in words) + 4), min(float(page.height), max(bots) + 4))


path = glob.glob("corpus/**/cbh*.pdf", recursive=True)[0]
with pdfplumber.open(path) as pdf:
    page = pdf.pages[0]
    box = STRIP if CROP == "strip" else derived_box(path, page)
    print(f"--- CROP={CROP} {[round(c) for c in box]} ---", flush=True)
    crop = page.crop(box)
    words = page.extract_words()
    for kind, v in [("target", GRAND)] + [("null", p) for p in PORTS] + [("null", CELL)]:
        hits = [w for w in words if w["text"] == v and box[0] <= w["x0"] and w["x1"] <= box[2]
                and box[1] <= w["top"] and w["bottom"] <= box[3]]
        if len(hits) != 1:
            raise SystemExit(f"{v}: {len(hits)} hits in the crop, expected 1")
        w = hits[0]
        im = crop.to_image(resolution=150)
        im.draw_rect((w["x0"] - 2, w["top"] - 2, w["x1"] + 2, w["bottom"] + 2), fill=None,
                     stroke="red", stroke_width=2)
        buf = io.BytesIO(); im.annotated.save(buf, format="PNG")
        answers = [ask(buf.getvalue(), PROMPT.format(value=v)) for _ in range(REPEAT)]
        print(f"{kind:<6} {v:>10} -> " + " ".join(answers), flush=True)
