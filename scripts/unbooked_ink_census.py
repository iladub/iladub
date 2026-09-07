"""Unbooked-ink census: how much of an ASSERTED band's ink lands in neither score operand.

Written 2026-09-07 by the loop that takes [[R176]]'s fork. R176 was measured on TWO PAGES
(apple p0/p1) and its corpus-wide consequence was explicitly typed PROPOSED; this is the
instrument that decides it, because a fork taken from a two-page sample is a preference.

WHAT IT MEASURES, per band, and why that is the right unit rather than per page:

  band_ink   = sum(len(ln.words) for ln in band.lines)   -- every word the band holds
  booked     = report.tokens_asserted + report.tokens_escalated
  unbooked   = band_ink - booked

`reports[i]` IS `bands[i]`: `compile_tables`' loop appends exactly one report per band and
records `tokens_*` by DIFFERENCING the running totals around each band's turn
(`src/iladub/etkl/compile.py:722-727`), so the zip below is an identity, not an alignment guess.

A NON_TABLE ("ignored") band books nothing BY DESIGN (`compile.py:757`) -- its ink is prose, not
a reading, and counting it would be the C1 defect in reverse. So ignored bands are reported
SEPARATELY and never folded into the headline: the number the fork turns on is unbooked ink in
bands the reader claims to have READ.

An ESCALATED band books every word it holds, so its unbooked should be 0 (+/- unit markers,
which are booked but are not `band.lines` words -- a NEGATIVE unbooked is that, and is reported
rather than clamped).

Corpus root is derived from THIS FILE, never hard-coded -- see scripts/page_ink_census.py's
docstring for why (a hard-coded path is what makes band_run_census unrunnable from a worktree).

    PYTHONPATH=src python3 scripts/unbooked_ink_census.py [out.json]
"""
import json
import os
import sys
import traceback
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO, "corpus")


def corpus_pdfs():
    found = []
    for root, _dirs, files in os.walk(CORPUS, followlinks=True):
        for f in sorted(files):
            if f.lower().endswith(".pdf"):
                found.append(os.path.join(root, f))
    return sorted(found)


def census_page(path, page_number):
    """Return one row per band of this page. Raises whatever compile/page_bands raise."""
    from iladub.etkl import compile as C

    # CAPTURE the bands `compile_tables` itself used rather than re-deriving them. Two reasons,
    # and the first is correctness, not speed: `page_bands` takes `section_repair_bands`, so a
    # second independent call is only *probably* the same list. `compile_tables` looks
    # `page_bands` up as a module global (`compile.py:715`), so wrapping it here observes the
    # exact list -- the same late-binding property [[R172]]'s differ used to produce two readings
    # in one process (`scripts/entry_cell_diff.py`). It also halves the parse: page_bands is the
    # expensive half and is not cached (measured: no lru_cache in compile.py).
    seen = []
    real = C.page_bands

    def _capture(*a, **kw):
        got = real(*a, **kw)
        seen.append(got)
        return got

    C.page_bands = _capture
    try:
        rep = C.compile_tables(path, page_number, validate_shapes=False,
                               datagrid_fallback=False)
    finally:
        C.page_bands = real
    if len(seen) != 1:
        raise AssertionError("expected exactly one page_bands call, saw %d" % len(seen))
    bands = seen[0]
    if len(bands) != len(rep.regions):
        raise AssertionError("band/report misalignment: %d bands, %d reports"
                             % (len(bands), len(rep.regions)))
    rows = []
    for idx, (band, r) in enumerate(zip(bands, rep.regions)):
        ink = sum(len(ln.words) for ln in band.lines)
        booked = r.tokens_asserted + r.tokens_escalated
        rows.append({"band": idx, "kind": r.kind.name, "verdict": r.verdict,
                     "reason": r.reason, "ink": ink,
                     # The emitted table TYPE, which is what actually names the assert branch:
                     # `kind` only says what `classify` saw, and three different branches can
                     # assert under one kind (RECORD_TABLE covers the record, transposed and
                     # row-hierarchical sites). Paired with `table_uri`'s `#table` / `#mtable`
                     # prefix it pins the site uniquely.
                     "anchor": r.anchor, "uri": str(r.table_uri) if r.table_uri else None,
                     "asserted": r.tokens_asserted, "escalated": r.tokens_escalated,
                     "booked": booked, "unbooked": ink - booked})
    return rows, rep


def main(argv):
    import pdfplumber

    pdfs = corpus_pdfs()
    if not pdfs:
        print("no corpus PDFs under %s -- symlink the corpus before trusting a census" % CORPUS)
        return 1

    rows = []
    for path in pdfs:
        rel = os.path.relpath(path, CORPUS)
        with pdfplumber.open(path) as pdf:
            npages = len(pdf.pages)
        print("=== %s : %d pages" % (rel, npages), flush=True)
        for p in range(npages):
            try:
                brows, rep = census_page(path, p)
            except Exception as exc:  # noqa: BLE001 -- a raising page is a result, not a stop
                rows.append({"doc": rel, "page": p,
                             "error": "%s: %s" % (type(exc).__name__, exc)})
                print("  p%-3d RAISED %s: %s" % (p, type(exc).__name__, exc), flush=True)
                traceback.print_exc()
                continue
            for br in brows:
                br.update(doc=rel, page=p)
                rows.append(br)
            unb = sum(b["unbooked"] for b in brows if b["verdict"] == "asserted")
            print("  p%-3d bands=%-3d score=%-8s asserted=%-6d escalated=%-6d "
                  "UNBOOKED-in-asserted=%d"
                  % (p, len(brows), rep.score, rep.asserted, rep.escalated, unb), flush=True)

    ok = [r for r in rows if "error" not in r]
    by_verdict = defaultdict(lambda: [0, 0, 0])  # ink, booked, nbands
    for r in ok:
        acc = by_verdict[r["verdict"]]
        acc[0] += r["ink"]
        acc[1] += r["booked"]
        acc[2] += 1

    print("\n########## SUMMARY ##########")
    print("pages that raised : %d" % (len(rows) - len(ok)))
    print("\n%-12s %6s %10s %10s %10s  %s" % ("verdict", "bands", "ink", "booked",
                                              "unbooked", "unbooked%"))
    for v in sorted(by_verdict):
        ink, booked, n = by_verdict[v]
        pct = "n/a" if ink == 0 else "%.1f%%" % (100.0 * (ink - booked) / ink)
        print("%-12s %6d %10d %10d %10d  %s" % (v, n, ink, booked, ink - booked, pct))

    asserted = [r for r in ok if r["verdict"] == "asserted"]
    dirty = [r for r in asserted if r["unbooked"] != 0]
    print("\nASSERTED bands with unbooked ink : %d of %d" % (len(dirty), len(asserted)))
    for r in sorted(dirty, key=lambda r: -r["unbooked"])[:30]:
        print("    %-40s p%-3d b%-3d %-18s ink=%-5d booked=%-5d unbooked=%d"
              % (r["doc"], r["page"], r["band"], r["kind"], r["ink"], r["booked"],
                 r["unbooked"]))

    neg = [r for r in ok if r["unbooked"] < 0]
    print("\nbands booking MORE than band.lines holds (unit markers) : %d" % len(neg))
    for r in neg[:10]:
        print("    %-40s p%-3d b%-3d %-10s unbooked=%d"
              % (r["doc"], r["page"], r["band"], r["verdict"], r["unbooked"]))

    if len(argv) > 1:
        with open(argv[1], "w") as fh:
            json.dump(rows, fh, indent=2)
        print("\nwrote %s" % argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
