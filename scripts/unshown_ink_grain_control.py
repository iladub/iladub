"""unshown_ink_grain_control — is the `spanned` set the ONLY thing between the shipped code and a
live end-to-end disposal on graincorp-capacity? (R253)

    ./.venv/bin/python scripts/unshown_ink_grain_control.py         # all four arms
    ./.venv/bin/python scripts/unshown_ink_grain_control.py 2       # one arm, by number

THE QUESTION. The 2026-09-18 handoff's part 5 was typed PROPOSED and named one prediction to run
before anything was built on it: *supplying the spanned set is the only thing between the shipped
code and a live end-to-end disposal on gcap.* [[R252]] measured the two address spaces disagreeing
on six of seven documents and so blocks that prediction; gcap is the silent one, but a real
disposal had never been carried through the dispatch with a reading.

THE METHOD. Hand `region_unshown` a `FakeRegionReader` — no model, no network — and compile the
document through the REAL dispatch with `validate_shapes=True`, then count what reached the graph.
Four arms, because a positive result is not self-interpreting and a control that cannot fire is not
a control (this repo's own repeated lesson):

    arm  reading handed to the reader            spanned      what it tests
    1    110 zeros U all 26 empty  (136 addr)    ()           the POSITION-grain ask
    2    110 zeros U {(1,6)}       (111 addr)    the 25 col-0 the handoff's own prescription
    3    110 zeros                 (110 addr)    the 25 col-0 refusal 3 fires (null, scoped)
    4    110 zeros                 (110 addr)    ()           refusal 3 fires (null, unscoped)

Arms 3 and 4 are the null: they must dispose NOTHING. An instrument where every arm succeeds is
measuring its own join.

EACH ARM RUNS IN ITS OWN PROCESS, and that is not hygiene theatre — it was a measured defect. A
first version ran the four arms in one interpreter and reported arm 3 disposing 110 on the first
`page_bands` call and 0 on the second, from one reading and one spanned set. The pipeline is
consistent; the contamination was the instrument's. Re-run in isolation, every arm's two calls
agree. `main()` re-execs itself per arm for that reason.

WHY `page_bands` IS CALLED TWICE PER COMPILE, since the figures show two: `document.py:1437`
(`compile_document`) and `compile.py:875` (`compile_tables`) each call it, on the same partition —
measured identical (27x16, 406 cells, 26 text-layer-empty, non-col-0 empties `[(1, 6)]`).

Measurement only: writes nothing, decides nothing, and reads no pixel value.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from rdflib import RDF, URIRef                                     # noqa: E402

from iladub.etkl import compile as _compile                        # noqa: E402
from iladub.etkl.headers import _grid_cells                        # noqa: E402
from iladub.etkl.holon import UnshownCarriageError                 # noqa: E402
from iladub.etkl.regions import classify                           # noqa: E402
from iladub.etkl.unshownink import FakeRegionReader, Reading, region_unshown   # noqa: E402

PDF = "corpus/ag-trade/graincorp-capacity-2026-08-04.pdf"
TAB = "https://w3id.org/iladub/tab#"
REGION_CELLS = 406           # gcap band 3, the one region this row is about. NOT a tolerance:
                             # it SELECTS the band by its measured cell count so the arms cannot
                             # silently run on a different region. Nothing is compared to it.
_orig_page_bands = _compile.page_bands


def band3():
    """gcap band 3, its grid, and the three address sets the arms are built from."""
    for band in _orig_page_bands(PDF, 0):
        reg = classify(band)
        if reg.grid is None:
            continue
        cells = _grid_cells(band, reg.grid)
        if len(cells) != REGION_CELLS:
            continue
        nrows, ncols = len(band.lines), reg.grid.ncols
        has_glyph = {(r, c) for r, c, _t in cells}
        zeros = frozenset((r, c) for r, c, t in cells if str(t).strip() == "0")
        empty = frozenset({(r, c) for r in range(nrows) for c in range(ncols)} - has_glyph)
        return band, reg.grid, zeros, empty
    raise SystemExit(f"no {REGION_CELLS}-cell region on {PDF}")


def arms():
    _band, _grid, zeros, empty = band3()
    span_col0 = frozenset(p for p in empty if p[1] == 0)
    return {
        "1": ("position-grain ask: reader reports every empty place",
              zeros | empty, frozenset()),
        "2": ("the handoff's prescription: 110 U (1,6), spanned supplied",
              zeros | frozenset({(1, 6)}), span_col0),
        "3": ("NULL: reader withholds the empties, spanned supplied",
              zeros, span_col0),
        "4": ("NULL: reader withholds the empties, no spanned",
              zeros, frozenset()),
    }


def _patched(reading_set, spanned, disposed):
    def page_bands(pdf_path, page_number=0, section_repair_bands=None):
        out = []
        for band in _orig_page_bands(pdf_path, page_number, section_repair_bands):
            reg = classify(band)
            if reg.grid is None or len(_grid_cells(band, reg.grid)) != REGION_CELLS:
                out.append(band)
                continue
            reader = FakeRegionReader(Reading(empty_cells=frozenset(reading_set)))
            found = region_unshown(pdf_path, page_number, band, reg.grid, reader, spanned)
            disposed.append(len(found))
            out.append(replace(band, unshown=tuple(sorted(found))) if found else band)
        return out
    return page_bands


def run_one(arm: str) -> int:
    label, reading_set, spanned = arms()[arm]
    print(f"ARM {arm} — {label}", flush=True)
    print(f"  |reading|={len(reading_set)}  |spanned|={len(spanned)}", flush=True)
    disposed: list[int] = []
    _compile.page_bands = _patched(reading_set, spanned, disposed)
    from iladub.etkl.document import compile_document
    try:
        rep = compile_document(PDF)
    except UnshownCarriageError as ex:
        print(f"  CARRIAGE REFUSED: {str(ex)[:200]}", flush=True)
        return 0
    g = rep.graph
    n_unshown = len(list(g.triples((None, URIRef(TAB + "unshownText"), None))))
    n_entry = len(set(g.subjects(RDF.type, URIRef(TAB + "EntryCell"))))
    emptied = sum(1 for _s, _p, o in g.triples((None, URIRef(TAB + "cellText"), None))
                  if str(o) == "")
    print(f"  disposed per page_bands call: {disposed}", flush=True)
    print(f"  COMPILED  score={rep.score:.4f}  tab:unshownText={n_unshown}  "
          f"tab:EntryCell={n_entry}  emptied cellText={emptied}", flush=True)
    return 0


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        return run_one(argv[1])
    for arm in sorted(arms()):
        # A fresh interpreter per arm: see the module docstring — one process gave two different
        # answers for one arm, and the difference was this instrument's, not the pipeline's.
        subprocess.run([sys.executable, "-u", os.path.abspath(__file__), arm], check=False)
        print(flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
