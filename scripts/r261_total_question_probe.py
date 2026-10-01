"""R261 P1 probe — a MEASUREMENT instrument, not a reader (it changes no compile).

Run from the repo root, LIVE and paid:  P1_REPEAT=3 env -u BAML_LIVE .venv/bin/python scripts/r261_total_question_probe.py

P1 probe: does a closed yes/no/cannot_tell question separate the census's 5 exact-sum
matches (4 TRUE cbh port totals, 1 FALSE who-wfa `21`)? Null control: numbers in following bands
that match NO column sum. Calls Haiku 4.5 (the shared `Claude` client's model) over raw HTTPS."""
import base64, glob, io, json, os, sys, urllib.request, urllib.error
sys.path.insert(0, "src")
import pdfplumber
from iladub.etkl.classifygraph import TAB
from iladub.etkl.compile import page_bands
from iladub.etkl.document import compile_document

GRID = str(TAB.DataGrid)
MODEL = os.environ.get("P1_MODEL", "claude-haiku-4-5-20251001")
REPEAT = int(os.environ.get("P1_REPEAT", "1"))

PROMPT = """The image shows the bottom of a table and what is printed directly beneath it.

Beneath the table, the number {value} is printed.

READ IT AS A PERSON READS A TABLE. Is {value} the total of the table above it — the sum of the
values in one of its columns, printed as that column's total?

Answer exactly one of:
- yes: it is the table's total.
- no: it is something else (a note, a page number, a label, a value of another table, ...).
- cannot_tell: the image does not let a reader decide.

Reply with JSON only: {{"answer": "yes" | "no" | "cannot_tell", "note": "<one short sentence; never quote any text or number from the page>"}}"""


def crop(pdf_path, page_no, bands, tail_lines=None):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no]
        words = [w for b in bands for ln in b.lines for w in ln.words]
        top = bands[0].top
        # the bottom of the table: at most the last 8 lines of the table band
        tl = bands[0].lines[-8:]
        top = min(w.top for ln in tl for w in ln.words)
        bot = bands[1].bottom
        box = (max(0, min(w.x0 for w in words) - 4), max(0, top - 4),
               min(float(page.width), max(w.x1 for w in words) + 4), min(float(page.height), bot + 4))
        im = page.crop(box).to_image(resolution=150)
        buf = io.BytesIO(); im.original.save(buf, format="PNG"); return buf.getvalue()


def ask(png, value):
    body = {"model": MODEL, "max_tokens": 300, "messages": [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                     "data": base64.b64encode(png).decode()}},
        {"type": "text", "text": PROMPT.format(value=value)}]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
                                 {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                                  "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        out = json.load(urllib.request.urlopen(req))["content"][0]["text"]
    except urllib.error.HTTPError as e:
        return {"answer": f"HTTP{e.code}", "note": e.read().decode()[:200]}
    try:
        return json.loads(out[out.index("{"):out.rindex("}") + 1])
    except Exception:
        return {"answer": "UNPARSED", "note": out[:120]}


from decimal import Decimal, InvalidOperation
from iladub.etkl.document import _index_suffix

# as_decimal / columns: copied from scripts/section_total_fp_census.py (that script runs on import)
def as_decimal(text):
    if text is None:
        return None
    s = str(text).strip().replace(",", "").replace("%", "").replace("$", "").strip()
    if s in ("", "-", "."):
        return None
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1].strip()
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    return -d if neg else d


def columns(graph, table_uri):
    """{col_index: (Decimal sum, member_count, is_ordinal)} -- atColumn must bind."""
    per_col = {}
    for entry in graph.objects(table_uri, TAB.hasCell):
        col = graph.value(entry, TAB.atColumn)
        if col is None:
            continue
        val = as_decimal(graph.value(entry, TAB.cellText))
        if val is None:
            continue
        try:
            ci = _index_suffix(col, table_uri, "c")
        except Exception:
            ci = str(col)
        per_col.setdefault(ci, []).append(val)
    out = {}
    for ci, vals in per_col.items():
        ordered = sorted(vals)
        ordinal = (len(ordered) > 1
                   and all(v == v.to_integral_value() for v in ordered)
                   and all(b - a == 1 for a, b in zip(ordered, ordered[1:])))
        out[ci] = (sum(vals, Decimal(0)), len(vals), ordinal)
    return out




cases = []
for stem in ("cbh-", "who-wfa"):
    path = glob.glob(f"corpus/**/{stem}*.pdf", recursive=True)[0]
    rep = compile_document(path, validate_shapes=False)
    for page, prep in enumerate(rep.pages):
        repair = frozenset(i for pg, i in rep.repaired_bands if pg == page)
        bands = page_bands(path, page, section_repair_bands=repair)
        for i, r in enumerate(prep.regions):
            if r.verdict != "asserted" or r.table_uri is None or r.anchor == GRID or i + 1 >= len(bands):
                continue
            nxt = bands[i + 1]
            sums = {t for _, (t, n, o) in columns(rep.graph, r.table_uri).items()}
            null_taken = False
            for ln in nxt.lines:
                for w in ln.words:
                    d = as_decimal(w.text)
                    if d is None:
                        continue
                    if d in sums:
                        cases.append((stem, page, i, w.text, True, path, bands[i], nxt))
                    elif not null_taken:   # NULL CONTROL: first non-matching number of each pair
                        null_taken = True
                        cases.append((stem, page, i, w.text, False, path, bands[i], nxt))

print(f"{len(cases)} numeric candidates; {sum(c[4] for c in cases)} exact-sum matches")
for stem, page, i, text, match, path, tb, nb in cases:
    png = crop(path, page, [tb, nb])
    answers = [ask(png, text) for _ in range(REPEAT)]
    print(f"{'MATCH' if match else 'null '} {stem:<8} p{page} t{i:<3} {text:>10} -> "
          + " ".join(a["answer"] for a in answers) + f"   | {answers[0]['note'][:90]}", flush=True)
