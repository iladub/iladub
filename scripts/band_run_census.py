"""The band-run census: relation A (equality) vs relation B (adjacent subsumption).

Spec: docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md § 3.3, whose
Q1-Q4 tables are this script's output. Committed so the numbers are re-runnable
rather than pasted (the predecessor loop's census was scratch and had to be
re-derived; see that spec's § 1.2).

Original header:
SCRATCH measurement: relation A (equality) vs relation B (adjacent subsumption)
over rule-x signature sets, censused across the whole corpus, and disposed by the
one-band-matrix spike's oracle chain.

Mirrors scripts/one_band_matrix_spike.py (imported, not copied) and
sectiongraph._rule_xs_signature (imported).
"""
from __future__ import annotations

import os
import sys
import glob
import traceback

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

from rdflib import Graph, URIRef  # noqa: E402

from iladub.etkl.compile import compile_tables, page_bands  # noqa: E402
from iladub.etkl.document import page_count  # noqa: E402
from iladub.etkl.sectiongraph import _rule_xs_signature  # noqa: E402
from iladub.etkl.matrix import is_matrix_candidate, classify_matrix  # noqa: E402
from iladub.etkl.holon import assert_matrix_region  # noqa: E402
from iladub.etkl.tiling import region_tiles  # noqa: E402
from one_band_matrix_spike import merge_bands  # noqa: E402


def sig_set(band):
    """The band's signature as a SET of rounded x's — exactly _rule_xs_signature's
    content, re-split. None when the band carries no rules at all."""
    s = _rule_xs_signature(band.rules)
    if s is None:
        return None
    return frozenset(s.split(" "))


def runs_equality(sets):
    """A: maximal contiguous runs (len >= 2) of EQUAL non-empty sets."""
    out = []
    i = 0
    n = len(sets)
    while i < n:
        if not sets[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and sets[j + 1] and sets[j + 1] == sets[i]:
            j += 1
        if j > i:
            out.append((i, j))
        i = j + 1
    return out


def runs_subsumption(sets):
    """B: run extends i -> i+1 when both non-empty and one is a subset of the other."""
    out = []
    i = 0
    n = len(sets)
    while i < n:
        if not sets[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and sets[j + 1] and (
            sets[j] <= sets[j + 1] or sets[j + 1] <= sets[j]
        ):
            j += 1
        if j > i:
            out.append((i, j))
        i = j + 1
    return out


def dispose(bands, first, last, page):
    """The spike's chain on the merged run. Returns a dict."""
    res = {"candidate": None, "classify": None, "entries": None, "tiles": None,
           "error": None}
    try:
        merged = merge_bands(bands, first, last)
        cand = is_matrix_candidate(merged)
        res["candidate"] = cand
        if not cand:
            return res
        mreg = classify_matrix(merged)
        res["classify"] = "MatrixRegion" if mreg is not None else "None"
        if mreg is None:
            return res
        doc = URIRef("https://example.org/etkl/doc")
        scratch = Graph()
        n = assert_matrix_region(scratch, mreg, merged,
                                 URIRef(f"{doc}#mtableMERGED"), doc, page)
        res["entries"] = n
        res["tiles"] = region_tiles(scratch)
    except Exception as exc:  # noqa: BLE001
        res["error"] = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    return res


DOCS = sorted(glob.glob("/Volumes/WD Green/dev/git/iladub/corpus/*/*.pdf"))


def main():
    print("=== corpus file list")
    for d in DOCS:
        print("   ", d, "pages=", page_count(d))
    print()

    all_rows = []
    for pdf in DOCS:
        name = pdf.split("/")[-1]
        npages = page_count(pdf)
        for p in range(npages):
            try:
                bands = page_bands(pdf, p)
                base = compile_tables(pdf, page_number=p)
            except Exception as exc:  # noqa: BLE001
                print(f"!! FAILED {name} p{p}: {type(exc).__name__}: {exc}")
                traceback.print_exc()
                continue
            sets = [sig_set(b) for b in bands]
            verdicts = [base.regions[i].verdict for i in range(len(bands))]
            cells = [base.regions[i].cells for i in range(len(bands))]
            A = runs_equality(sets)
            B = runs_subsumption(sets)
            all_rows.append(dict(name=name, page=p, nbands=len(bands), sets=sets,
                                 verdicts=verdicts, cells=cells, A=A, B=B,
                                 bands=bands, pdf=pdf))
            print(f"--- {name} p{p}: {len(bands)} bands")
            for i, b in enumerate(bands):
                s = _rule_xs_signature(b.rules)
                txt = " ".join(w.text for w in b.lines[0].words)[:48] if b.lines and b.lines[0].words else ""
                print(f"    band {i}: {verdicts[i]:10} cells={cells[i]:4} "
                      f"nsig={0 if sets[i] is None else len(sets[i]):3} "
                      f"sig={'None' if s is None else s[:80]!s:80} {txt!r}")
            print(f"    A(equality)   runs: {A}")
            print(f"    B(subsumption) runs: {B}")
            print(f"    DIFFER: {'YES' if A != B else 'no'}")
            print()

    # ---------- Q2 summary table ----------
    print()
    print("=== Q2 SUMMARY TABLE")
    print(f"{'document':34} {'pg':>3} {'A runs':28} {'B runs':28} "
          f"{'A cov (verdicts/cells)':40} {'B cov (verdicts/cells)':40}")
    for r in all_rows:
        def cov(runs):
            parts = []
            for (a, b) in runs:
                vs = ",".join(v[:3] for v in r["verdicts"][a:b + 1])
                cs = sum(r["cells"][a:b + 1])
                parts.append(f"{a}..{b}[{vs}]={cs}")
            return "; ".join(parts) or "-"
        print(f"{r['name']:34} {r['page']:>3} "
              f"{str(r['A']):28} {str(r['B']):28} {cov(r['A']):40} {cov(r['B']):40}")

    print()
    print("=== Q2 DIFFERENCES (A != B)")
    for r in all_rows:
        if r["A"] != r["B"]:
            onlyA = [x for x in r["A"] if x not in r["B"]]
            onlyB = [x for x in r["B"] if x not in r["A"]]
            print(f"  {r['name']} p{r['page']}: only-A={onlyA}  only-B={onlyB}")

    # ---------- Q3 disposal ----------
    print()
    print("=== Q3 DISPOSAL of every B run")
    print(f"{'document':34} {'pg':>3} {'run':>8} {'shared with A':>13} "
          f"{'cand':>6} {'classify':>12} {'entries':>8} {'tiles':>6} "
          f"{'cells today':>12} {'DESTROYS?':>10} {'tail?':>6} {'renumber':>9}")
    destroyers = []
    accepted_nontail = []
    for r in all_rows:
        for (a, b) in r["B"]:
            d = dispose(r["bands"], a, b, r["page"])
            today = sum(r["cells"][a:b + 1])
            accepted = bool(d["tiles"]) and d["entries"] is not None
            destroys = accepted and d["entries"] < today
            tail = (b == r["nbands"] - 1)
            renum = 0 if tail else (r["nbands"] - 1 - b)
            if destroys:
                destroyers.append((r["name"], r["page"], a, b, d["entries"], today))
            if accepted and not tail:
                accepted_nontail.append((r["name"], r["page"], a, b, d["entries"], renum))
            print(f"{r['name']:34} {r['page']:>3} {f'{a}..{b}':>8} "
                  f"{str((a, b) in r['A']):>13} "
                  f"{str(d['candidate']):>6} {str(d['classify']):>12} "
                  f"{str(d['entries']):>8} {str(d['tiles']):>6} "
                  f"{today:>12} {('YES' if destroys else 'no'):>10} "
                  f"{str(tail):>6} {renum:>9}"
                  + (f"   ERROR={d['error']}" if d["error"] else ""))

    print()
    print("=== Q3 ANSWER — B runs the oracle ACCEPTS that DESTROY cells asserted today:")
    if destroyers:
        for x in destroyers:
            print(f"    {x[0]} p{x[1]} run {x[2]}..{x[3]}: merged={x[4]} < today={x[5]}")
    else:
        print("    NONE")

    print()
    print("=== Q4 ANSWER — accepted B runs that are NOT a page tail:")
    if accepted_nontail:
        for x in accepted_nontail:
            print(f"    {x[0]} p{x[1]} run {x[2]}..{x[3]}: entries={x[4]} "
                  f"bands that would renumber={x[5]}")
    else:
        print("    NONE — every accepted B run is a page tail")

    return 0


if __name__ == "__main__":
    sys.exit(main())
