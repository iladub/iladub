"""Per-page ink census: (asserted, escalated, score) for every page of every corpus document.

Committed 2026-09-04 by the R165 plan session, because the plan's Task 6 (oracle O3) pins a
per-page baseline table and a pasted table nobody can re-run is a number, not a measurement.

It also answers the question the R165 handoff graded PROPOSED — *which page can serve as the
fixture for `test_fallback_never_masks_an_escalation`?* The datagrid fallback gate is
`asserted_total == 0 and escalated_total == 0` (`compile.py:1040`), so a page only isolates the
ESCALATION clause when `asserted == 0 and escalated > 0`; a page that also asserts declines on the
first clause and never reaches the second. Bucket (a) below is exactly that set.

Path handling: the corpus root is derived from THIS FILE's location, never hard-coded — a
hard-coded absolute corpus path is what makes `scripts/band_run_census.py:111` unrunnable from a
worktree, and `corpus/` is gitignored (`.gitignore:52`) so a worktree has none until it is
symlinked. Run with the corpus present; a missing corpus prints nothing and exits 1 rather than
reporting a green empty census.

    PYTHONPATH=src python3 scripts/page_ink_census.py [out.json]
"""
import json
import os
import sys
import traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO, "corpus")


def corpus_pdfs():
    found = []
    for root, _dirs, files in os.walk(CORPUS, followlinks=True):
        for f in sorted(files):
            if f.lower().endswith(".pdf"):
                found.append(os.path.join(root, f))
    return sorted(found)


def main(argv):
    import pdfplumber
    from iladub.etkl.compile import compile_tables

    pdfs = corpus_pdfs()
    if not pdfs:
        print("no corpus PDFs under %s — symlink the corpus before trusting a census" % CORPUS)
        return 1

    rows = []
    for path in pdfs:
        rel = os.path.relpath(path, CORPUS)
        with pdfplumber.open(path) as pdf:
            npages = len(pdf.pages)
        print("=== %s : %d pages" % (rel, npages), flush=True)
        for p in range(npages):
            try:
                r = compile_tables(path, p, validate_shapes=False, datagrid_fallback=False)
                row = {"doc": rel, "page": p, "asserted": r.asserted,
                       "escalated": r.escalated, "score": r.score}
                print("  p%-3d asserted=%-6d escalated=%-6d score=%s"
                      % (p, r.asserted, r.escalated, r.score), flush=True)
            except Exception as exc:  # noqa: BLE001 — a raising page is a result, not a stop
                row = {"doc": rel, "page": p, "error": "%s: %s" % (type(exc).__name__, exc)}
                print("  p%-3d RAISED %s" % (p, row["error"]), flush=True)
                traceback.print_exc()
            rows.append(row)

    ok = [r for r in rows if "error" not in r]
    isolating = [r for r in ok if r["asserted"] == 0 and r["escalated"] > 0]
    firing = [r for r in ok if r["asserted"] == 0 and r["escalated"] == 0]

    print("\n########## SUMMARY ##########")
    print("pages compiled OK : %d" % len(ok))
    print("pages raised      : %d" % (len(rows) - len(ok)))
    print("\n(a) asserted==0 AND escalated>0  -> can isolate the escalation clause : %d"
          % len(isolating))
    for r in isolating:
        print("    %-42s p%-3d asserted=%-5d escalated=%-5d" % (r["doc"], r["page"],
                                                                r["asserted"], r["escalated"]))
    print("\n(b) asserted==0 AND escalated==0 -> the datagrid fallback FIRES : %d" % len(firing))
    for r in firing:
        print("    %-42s p%-3d score=%s" % (r["doc"], r["page"], r["score"]))

    if len(argv) > 1:
        with open(argv[1], "w") as fh:
            json.dump(rows, fh, indent=2)
        print("\nwrote %s" % argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
