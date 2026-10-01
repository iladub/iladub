"""R261 P1/P3 probe — a MEASUREMENT instrument, not a reader (it changes no compile).

Run from the repo root, LIVE and paid:
    ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"') \\
    P1_REPEAT=3 env -u BAML_LIVE .venv/bin/python scripts/r261_total_question_probe.py

P1 probe (re-run on the D7 crop, task 1 step 3): does a closed yes/no/cannot_tell question
separate the census's 5 exact-sum matches (4 TRUE cbh port totals, 1 FALSE who-wfa `21`)? Null
control: numbers in following bands that match NO column sum. Calls Haiku 4.5 (the shared
`Claude` client's model) over raw HTTPS.

P3 probe (task 1 step 2): a second wording asks whether `1,951,264` is the total of the four
port totals (the total-of-totals level, spec s5.1). Null control: each of the four port totals,
asked the same grand-total question.

D7 (plan shared-context): the crop has no line-count constant.
  - Table level: the WHOLE previous (table) band, through the candidate's own line (not the
    band's last 8 lines, and not necessarily the whole following band).
  - Total-of-totals level: the union box of the four port-total lines and the `1,951,264` line.

Closed output contract (spec s3.2, resolutions): `{"answer": "yes" | "no" | "cannot_tell"}` only
-- no `note` field, for both wordings. Anything else parsed is recorded as UNPARSED.
"""
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

Reply with JSON only: {{"answer": "yes" | "no" | "cannot_tell"}}"""

# P3 (task 1 step 1-2): the total-of-totals wording. Draft, a proposition (brief, verbatim).
# The worker is NOT given the operands' values -- it answers the role question, and arithmetic
# answers the sum.
PROMPT2 = """The image shows part of a page on which several tables each have a total printed beneath
them. The number {value} is also printed. READ IT AS A PERSON READS THE PAGE. Is {value} the
total of those tables' totals — a grand total? Answer exactly one of: yes / no / cannot_tell.

Reply with JSON only: {{"answer": "yes" | "no" | "cannot_tell"}}"""


def crop_table(pdf_path, page_no, band, line):
    """D7 table level: the whole previous (table) band through the candidate's own line. No
    tail-line constant (supersedes the old `tail_lines=8` crop)."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no]
        words = [w for ln in band.lines for w in ln.words] + list(line.words)
        top, bot = band.top, line.bottom
        box = (max(0, min(w.x0 for w in words) - 4), max(0, top - 4),
               min(float(page.width), max(w.x1 for w in words) + 4), min(float(page.height), bot + 4))
        im = page.crop(box).to_image(resolution=150)
        buf = io.BytesIO(); im.original.save(buf, format="PNG"); return buf.getvalue()


def crop_union(pdf_path, page_no, lines):
    """D7 total-of-totals level: the union box of the given lines (the four port-total lines plus
    the candidate line)."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_no]
        words = [w for ln in lines for w in ln.words]
        top = min(ln.top for ln in lines)
        bot = max(ln.bottom for ln in lines)
        box = (max(0, min(w.x0 for w in words) - 4), max(0, top - 4),
               min(float(page.width), max(w.x1 for w in words) + 4), min(float(page.height), bot + 4))
        im = page.crop(box).to_image(resolution=150)
        buf = io.BytesIO(); im.original.save(buf, format="PNG"); return buf.getvalue()


def ask(png, prompt_text):
    """Returns one of "yes" | "no" | "cannot_tell" | "UNPARSED" | "HTTP<code>". The closed
    contract has no `note` field; any reply that is not exactly {"answer": one of the three} is
    UNPARSED."""
    body = {"model": MODEL, "max_tokens": 300, "messages": [{"role": "user", "content": [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                     "data": base64.b64encode(png).decode()}},
        {"type": "text", "text": prompt_text}]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", json.dumps(body).encode(),
                                 {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                                  "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        out = json.load(urllib.request.urlopen(req))["content"][0]["text"]
    except urllib.error.HTTPError as e:
        return f"HTTP{e.code}"
    try:
        obj = json.loads(out[out.index("{"):out.rindex("}") + 1])
        ans = obj.get("answer")
        if ans in ("yes", "no", "cannot_tell") and set(obj.keys()) == {"answer"}:
            return ans
        return "UNPARSED"
    except Exception:
        return "UNPARSED"


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


def find_line(bands, text):
    """The single-word line printing exactly `text`, or None. Used only for the known cbh p0
    totals (D7 total-of-totals crop), never as a general lookup."""
    for b in bands:
        for ln in b.lines:
            if len(ln.words) == 1 and ln.words[0].text.strip() == text:
                return ln
    return None


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
                        cases.append((stem, page, i, w.text, True, path, bands[i], ln))
                    elif not null_taken:   # NULL CONTROL: first non-matching number of each pair
                        null_taken = True
                        cases.append((stem, page, i, w.text, False, path, bands[i], ln))


# --- P3: the total-of-totals wording (step 2) --------------------------------------------------
PORT_TOTALS = ["374,904", "737,289", "660,363", "178,708"]
GRAND_TOTAL = "1,951,264"

cbh_path = glob.glob("corpus/**/cbh*.pdf", recursive=True)[0]
cbh_rep = compile_document(cbh_path, validate_shapes=False)
cbh_repair = frozenset(i for pg, i in cbh_rep.repaired_bands if pg == 0)
cbh_bands = page_bands(cbh_path, 0, section_repair_bands=cbh_repair)

grand_line = find_line(cbh_bands, GRAND_TOTAL)
port_lines = [find_line(cbh_bands, v) for v in PORT_TOTALS]
if grand_line is None or any(ln is None for ln in port_lines):
    raise SystemExit(f"P3 setup: a totals line was not found -- grand={grand_line} ports={port_lines}")

union_png = crop_union(cbh_path, 0, port_lines + [grand_line])

print("--- P3: total-of-totals wording, D7 union crop ---", flush=True)
p3_grand = [ask(union_png, PROMPT2.format(value=GRAND_TOTAL)) for _ in range(REPEAT)]
print(f"P3 grand {GRAND_TOTAL:>10} -> " + " ".join(p3_grand), flush=True)

p3_nulls = {}
for v in PORT_TOTALS:
    a = [ask(union_png, PROMPT2.format(value=v)) for _ in range(REPEAT)]
    p3_nulls[v] = a
    print(f"P3 null  {v:>10} -> " + " ".join(a), flush=True)


# --- P1 on the D7 table-level crop (step 3) -----------------------------------------------------
print(f"--- P1 on the D7 table-level crop: {len(cases)} numeric candidates; "
      f"{sum(c[4] for c in cases)} exact-sum matches ---", flush=True)
for stem, page, i, text, match, path, tb, ln in cases:
    png = crop_table(path, page, tb, ln)
    answers = [ask(png, PROMPT.format(value=text)) for _ in range(REPEAT)]
    print(f"{'MATCH' if match else 'null '} {stem:<8} p{page} t{i:<3} {text:>10} -> "
          + " ".join(answers), flush=True)
