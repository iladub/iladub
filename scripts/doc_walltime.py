#!/usr/bin/env python
"""doc_walltime — what a whole-corpus document compile costs, and how much of it is duplicated.

WHY THIS EXISTS. `docs/superpowers/2026-09-04-r165-preplan-spike.md` § Q-A A3 priced ONE
`page_bands` call per page and left the document-scope question open, and the spec it measures
(`docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` § 3.5) states that
`page_bands` is called "at least twice per page in a document compile ... with no caching
anywhere" and orders the wall-clock measured before "no cache" is committed to. This instrument
is that measurement, committed rather than left in a scratchpad so the figures in
`docs/superpowers/2026-09-04-r165-three-claims-measured.md` § C are re-runnable.

WHAT IT REPORTS, per corpus document:
  wall_s               `compile_document(..., validate_shapes=False)` end to end.
  page_bands_calls     how many times `page_bands` was entered (the driver's inventory call at
                       document.py:1410, compile_tables' own at compile.py:602, plus one more
                       per section-repair pass and per adoption re-compile).
  page_bands_total_s   the sum of those calls.
  cacheable_saving_s   what a perfect cache keyed on (pdf, page, section_repair_bands) would
                       return: every call after the first for each distinct key. This is the
                       memoisation question stated as a number.

HOW TO USE IT. Run it once per tree and diff the totals — the point is a BEFORE/AFTER pair, and
a single run of one tree answers nothing:

    ILADUB_ROOT=$PWD PYTHONPATH=src ./.venv/bin/python3 scripts/doc_walltime.py /tmp/before.json

CAUTION, measured 2026-09-04 and the reason no single figure here should be quoted alone: the
per-document wall-clock carries real noise. In the pair recorded in the evidence doc, `who` came
back 19% FASTER under a change that cannot make it faster (no run is proposed on any of its
pages). Read the call COUNTS, which are structural and noise-free, before reading the seconds.
"""
import glob
import json
import os
import sys
import time

ROOT = os.environ.get("ILADUB_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import iladub.etkl.compile as C          # noqa: E402
import iladub.etkl.document as D         # noqa: E402

_calls: list[tuple] = []
_real = C.page_bands


def _spy(pdf_path, page_number=0, section_repair_bands=None):
    """Wrap `page_bands` at BOTH module bindings — `document` imports it by name, so patching
    only `compile.page_bands` would miss the driver's inventory call entirely."""
    t0 = time.perf_counter()
    out = _real(pdf_path, page_number, section_repair_bands=section_repair_bands)
    _calls.append((os.path.basename(pdf_path), page_number,
                   None if section_repair_bands is None else sorted(section_repair_bands),
                   len(out), round(time.perf_counter() - t0, 4)))
    return out


def main(argv: list[str]) -> int:
    C.page_bands = _spy
    D.page_bands = _spy
    out = {"src": C.__file__, "docs": []}
    for pdf in sorted(glob.glob(os.path.join(ROOT, "corpus", "*", "*.pdf"))):
        _calls.clear()
        t0 = time.perf_counter()
        rep = D.compile_document(pdf, validate_shapes=False)
        elapsed = time.perf_counter() - t0
        by_key: dict[tuple, list[float]] = {}
        for _name, pg, srb, _nb, dt in _calls:
            by_key.setdefault((pg, tuple(srb) if srb else None), []).append(dt)
        cacheable = sum(sum(v[1:]) for v in by_key.values())
        out["docs"].append({
            "doc": os.path.basename(pdf), "wall_s": round(elapsed, 3), "score": rep.score,
            "page_bands_calls": len(_calls),
            "page_bands_total_s": round(sum(c[4] for c in _calls), 3),
            "cacheable_saving_s": round(cacheable, 3),
            "calls": list(_calls),
        })
        print(f"{os.path.basename(pdf):45s} wall={elapsed:7.2f}s "
              f"page_bands={len(_calls):3d} calls {sum(c[4] for c in _calls):7.2f}s "
              f"cacheable={cacheable:6.2f}s score={rep.score:.4f}", flush=True)
    print("TOTAL wall", round(sum(d["wall_s"] for d in out["docs"]), 2),
          "| page_bands", round(sum(d["page_bands_total_s"] for d in out["docs"]), 2),
          "| cacheable", round(sum(d["cacheable_saving_s"] for d in out["docs"]), 2))
    if len(argv) > 1:
        json.dump(out, open(argv[1], "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
