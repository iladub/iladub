"""Run `unbooked_ink_fate` over EVERY page of EVERY corpus document, in one process.

Written 2026-09-07 for [[R178]]'s prescribed disposal: its row says the orphan texts must be READ
across the corpus before any repair is designed, because the 3-word `Year: Month` sample is one
document and cannot distinguish "axis caption" from "[[R166]] at a new position".

It exists as a committed script rather than a scratch one-liner because its output is the evidence
[[R177]] and [[R178]] are both re-stated on, and a claim nobody can re-run is a claim.

    PYTHONPATH=src python3 scripts/unbooked_ink_fate_corpus.py

~9 min on 7 documents / 27 pages. Prints `unbooked_ink_fate`'s per-page block for each, then the
one derived fact this loop turns on: whether the set of pages carrying bbox-less LabelCells is the
same set as the pages carrying orphan ink. A raising page is a result, not a stop.
"""
import os
import sys
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import unbooked_ink_fate as F  # noqa: E402

CORPUS = os.path.join(REPO, "corpus")


def corpus_pdfs():
    found = []
    for root, _dirs, files in os.walk(CORPUS, followlinks=True):
        for f in sorted(files):
            if f.lower().endswith(".pdf"):
                found.append(os.path.join(root, f))
    return sorted(found)


def main():
    import pdfplumber

    pdfs = corpus_pdfs()
    if not pdfs:
        print("no corpus PDFs under %s -- symlink the corpus before trusting this" % CORPUS)
        return 1
    rows = []
    for path in pdfs:
        rel = os.path.relpath(path, CORPUS)
        with pdfplumber.open(path) as pdf:
            npages = len(pdf.pages)
        print("=== %s : %d pages" % (rel, npages), flush=True)
        for p in range(npages):
            try:
                got = F.fate(path, p)
                rows.append(dict(got, doc=rel))
            except Exception as exc:  # noqa: BLE001 -- a raising page is a result, not a stop
                print("  p%-3d RAISED %s: %s" % (p, type(exc).__name__, exc), flush=True)
                traceback.print_exc()
            sys.stdout.flush()

    blind = {(r["doc"], r["page"]) for r in rows if r["no_bbox"] > 0}
    dirty = {(r["doc"], r["page"]) for r in rows if r["orphans"] > 0}
    print()
    print("pages measured                 : %d" % len(rows))
    print("pages with bbox-less LabelCells: %d %s" % (len(blind), sorted(blind)))
    print("pages with orphan ink          : %d %s" % (len(dirty), sorted(dirty)))
    # The load-bearing fact. While these sets are EQUAL, every orphan word in the corpus sits on a
    # page whose label geometry is incomplete, so the orphan count is an upper bound on [[R178]]'s
    # population and not a measurement of it. When [[R177]] is closed, `blind` empties and whatever
    # `dirty` still holds is the real population.
    print("SAME SET                       : %s" % (blind == dirty))
    print("total orphan words             : %d" % sum(r["orphans"] for r in rows))
    print("total bbox-less LabelCells     : %d" % sum(r["no_bbox"] for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
