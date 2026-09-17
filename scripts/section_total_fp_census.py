"""The false-positive surface of arithmetic binding, at DOCUMENT scope, zero pages skipped.

The page-scope pass found true=0 because cbh's four roster regions are escalated
(REGION_TILING_FAILED) at page scope and asserted only at DOCUMENT scope, where section
repair adopts bands (0,1),(0,3),(0,5),(0,7). A census that cannot see the true positives
cannot measure a false-positive RATE, so this is the population that counts.

The rule under test (R47/R77): a numeric value printed in the band IMMEDIATELY FOLLOWING an
asserted table, reconciling EXACTLY with one of that table's own column sums, is that
table's section total.

Exactness: sums are Decimal parsed from tab:cellText, never float -- the rule is exact
equality and a float sum would smuggle in a tolerance the CLAUDE.md s8 gate forbids.
A column sum requires tab:atColumn to BIND: holon.py's label/header emitters attach
tab:hasCell + tab:cellText without it, and those cells are not column members.

RECORDED, NOT ADOPTED -- two candidate discriminators, both printed as columns so they can
be falsified rather than fitted:
  ordinal : the summed column's cells are consecutive integers (an index, not a measure).
            who-wfa's two surviving false positives are both c1 = [2,3,4,5,6] = 20.
  nxt_ln  : the following band's line count (the cbh-fitted 1-line/6-line shape the
            2026-09-17 evidence s10 already refused to key a rule on).

Gate classification (CLAUDE.md s8): PROCEDURAL. Raw extraction plus decidable exact
arithmetic over an existing accounting. It changes no reading and carries no tolerance.
"""
import pathlib
import sys
import time
from decimal import Decimal, InvalidOperation

sys.path.insert(0, "src")
from iladub.etkl.classifygraph import TAB
from iladub.etkl.compile import page_bands
from iladub.etkl.document import _index_suffix, compile_document

GRID = str(TAB.DataGrid)
KNOWN_TRUE = {"374904", "737289", "660363", "178708"}   # cbh's four printed panel totals


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


pdfs = sorted(pathlib.Path("corpus").rglob("*.pdf"))
skipped, matches, pages_seen = [], [], 0

# The OPPORTUNITY DENOMINATOR. The first version of this census printed the pairs that
# MATCHED and never the pairs it EXAMINED -- so "false=2" could not be read as a rate.
# These counters are report-only: they are incremented beside each existing filter and
# change no branch, so the match figures must reproduce exactly (true=4 false=2).
opp = {"tables": 0, "following": 0, "numeric": 0, "comparisons": 0, "comparisons_n1": 0}

for pdf in pdfs:
    path, stem = str(pdf), pdf.stem
    t0 = time.time()
    try:
        rep = compile_document(path, validate_shapes=False)
    except Exception as exc:
        skipped.append((stem, "-", f"compile_document {type(exc).__name__}: {exc}"))
        print(f"[{stem[:30]:<31}] FAILED {type(exc).__name__}: {exc}", flush=True)
        continue
    adopted = set(rep.adopted)
    for page, prep in enumerate(rep.pages):
        pages_seen += 1
        repair = frozenset(i for pg, i in rep.repaired_bands if pg == page)
        bands = page_bands(path, page, section_repair_bands=repair)
        extra = len(prep.regions) - len(bands)
        if extra != 0 and page not in adopted:
            skipped.append((stem, page, f"UNEXPECTED bands={len(bands)} "
                                        f"regions={len(prep.regions)}"))
            continue
        for i, r in enumerate(prep.regions):
            if r.verdict != "asserted" or r.table_uri is None or r.anchor == GRID:
                continue
            opp["tables"] += 1
            if i + 1 >= len(bands):
                continue
            opp["following"] += 1
            nxt = bands[i + 1]
            cands = [(w.text, as_decimal(w.text)) for ln in nxt.lines for w in ln.words]
            cands = [(t, d) for t, d in cands if d is not None]
            if not cands:
                continue
            opp["numeric"] += 1
            cols = sorted(columns(rep.graph, r.table_uri).items(), key=lambda kv: str(kv[0]))
            opp["comparisons"] += len(cols) * len(cands)
            opp["comparisons_n1"] += sum(len(cands) for _, (_, n, _) in cols if n == 1)
            for ci, (total, n, ordinal) in cols:
                for text, val in cands:
                    if val == total:
                        matches.append((stem, page, i, i + 1, text, ci, n,
                                        ordinal, len(nxt.lines)))
    print(f"[{stem[:30]:<31}] {len(rep.pages):>2} pages  repaired={len(rep.repaired_bands)}"
          f"  adopted={len(rep.adopted)}  {time.time() - t0:5.1f}s", flush=True)

print()
print(f"PAGES SEEN {pages_seen}   SKIPPED {len(skipped)}   MATCHES {len(matches)}")
print()
if skipped:
    print("SKIPPED -- the denominator is STILL incomplete:")
    for stem, pg, why in skipped:
        print(f"  {stem[:28]:<29} p{pg} {why}")
else:
    print("NO PAGE SKIPPED -- the denominator is complete.")
print()
print("OPPORTUNITY DENOMINATOR -- the population every match below was drawn from:")
print(f"  asserted non-grid table regions          {opp['tables']:>6}")
print(f"  ... having a following band              {opp['following']:>6}")
print(f"  ... whose following band prints a number {opp['numeric']:>6}  <- PAIRS EXAMINED")
print(f"  exact-equality comparisons performed     {opp['comparisons']:>6}")
print(f"  ... on a column of a SINGLE member       {opp['comparisons_n1']:>6}")
print()
print(f"{'cls':<6}{'document':<26}{'pg':>3}{'tbl':>5}{'nxt':>5}{'value':>12}"
      f"{'col':>5}{'mem':>5}{'ordinal':>9}{'nxt_ln':>7}")
for stem, pg, tb, nb, text, ci, n, ordinal, nlines in matches:
    cls = "TRUE" if text.replace(",", "") in KNOWN_TRUE else "FALSE"
    print(f"{cls:<6}{stem[:25]:<26}{pg:>3}{tb:>5}{nb:>5}{text:>12}"
          f"{str(ci):>5}{n:>5}{str(ordinal):>9}{nlines:>7}")

t = sum(1 for m in matches if m[4].replace(",", "") in KNOWN_TRUE)
f = len(matches) - t
print()
print(f"TOTALS  true={t}  false={f}")
if matches:
    ford = sum(1 for m in matches if m[7] and m[4].replace(",", "") not in KNOWN_TRUE)
    tord = sum(1 for m in matches if m[7] and m[4].replace(",", "") in KNOWN_TRUE)
    print(f"ORDINAL-COLUMN flag: {ford} of {f} false, {tord} of {t} true "
          f"(recorded as a correlation to falsify -- NOT a rule)")
