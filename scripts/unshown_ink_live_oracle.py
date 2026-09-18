"""unshown_ink_live_oracle — O8: does a LIVE reader, given the place-grain ask, report the
positions the span clause taught it to withhold? (R253)

    ANTHROPIC_API_KEY=… BAML_LIVE=1 BAML_LOG=off \
        ./.venv/bin/python -u scripts/unshown_ink_live_oracle.py

THE QUESTION, and it is this loop's whole risk. Spec 2026-09-18 § 3.1 deletes the ask's span
clause and states the question at PLACE grain, which makes refusal 3 satisfiable with no `spanned`
set (spec § 1, evidence E1 arm 1). That is arithmetic about the disposal. Whether a real reader
ANSWERS at place grain is not arithmetic, and nothing offline can settle it.

THE PASS CONDITION — both halves, on graincorp-capacity band 3 (27 x 16, 406 populated, 110
unshown, 26 text-layer-empty of which 25 are column 0's blank places):

    (a) reading.empty_cells  SUPERSET-OR-EQUAL  the 26 text-layer-empty positions
        -- else refusal 3 fires and the rephrasing is WRONG.
    (b) dispose(...) returns EXACTLY the 110
        -- no more (a false assertion), no fewer (a miss).

A FAILURE HERE REFUTES THE SPEC AND IS NOT TO BE PATCHED. R253's other candidates -- extend R211's
span reading to body columns, or build a separate span oracle -- become the subject again. Do not
add a tolerance, do not re-introduce `spanned` to make this pass, and do not re-run hoping for a
better sample: a re-run is a NEW proposal that supersedes the old one, and any difference between
them is a MEASUREMENT to report (unshownink.py's module docstring).

NON-DETERMINISM IS EXPECTED AND IS NOT AVERAGED AWAY. This prints one run's answer and its verdict.
Run it again and you get another proposal; report both figures rather than the better one.

Costs one live model call per invocation. Reads no pixel value.
"""
from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "src"))
sys.path.insert(0, _ROOT)          # `baml_client` is generated at the repo root, and a script run
                                   # from scripts/ does not otherwise have it on sys.path.

from iladub.etkl.compile import page_bands                        # noqa: E402
from iladub.etkl.headers import _grid_cells                       # noqa: E402
from iladub.etkl.regions import classify                          # noqa: E402
from iladub.etkl.unshownink import (                              # noqa: E402
    BamlRegionReader, baml_reader_available, dispose, render_region,
)

PDF = "corpus/ag-trade/graincorp-capacity-2026-08-04.pdf"
REGION_CELLS = 406        # SELECTS the band by its measured cell count; compared to nothing.


def main() -> int:
    if not baml_reader_available():
        print("O8 NOT RUN — needs BAML_LIVE=1 and an importable baml_client.", flush=True)
        return 2

    band = grid = None
    for b in page_bands(PDF, 0):
        reg = classify(b)
        if reg.grid is not None and len(_grid_cells(b, reg.grid)) == REGION_CELLS:
            band, grid = b, reg.grid
    if band is None:
        print(f"O8 NOT RUN — no {REGION_CELLS}-cell region on {PDF}.", flush=True)
        return 2

    cells = _grid_cells(band, grid)
    nrows, ncols = len(band.lines), grid.ncols
    has_glyph = {(r, c) for r, c, _t in cells}
    zeros = frozenset((r, c) for r, c, t in cells if str(t).strip() == "0")
    empty = frozenset({(r, c) for r in range(nrows) for c in range(ncols)} - has_glyph)

    print(f"region {nrows}x{ncols}  populated={len(has_glyph)}  zeros={len(zeros)}  "
          f"text-layer-empty={len(empty)}", flush=True)

    crop = render_region(PDF, 0, band)
    reading = BamlRegionReader().read_empty_cells(crop, nrows, ncols)
    if reading is None:
        print("O8 FAILED — the reader returned nothing.", flush=True)
        return 1

    answer = reading.empty_cells
    print(f"\nreader: |A|={len(answer)}  refuses_grid={reading.refuses_grid}  "
          f"rows_you_see={reading.rows_seen}  cols_you_see={reading.cols_seen}", flush=True)
    print(f"reader note: {reading.note!r}", flush=True)

    missed_empty = sorted(empty - answer)
    print(f"\n(a) text-layer-empty positions the reader MISSED: {len(missed_empty)} "
          f"{missed_empty[:12]}{' …' if len(missed_empty) > 12 else ''}", flush=True)

    # RAW, independent of `dispose` -- so grain-compliance and reader ACCURACY can be attributed
    # separately. `dispose` returns the empty set on any refusal, which collapses the two: an ask
    # that makes the reader withhold looks identical to a reader that found nothing. These three
    # figures are the ONLY way to compare two asks on one crop (the control O8 first lacked).
    print(f"    raw recall on the 110: {len(answer & zeros)}/{len(zeros)}   "
          f"raw control: reported {len(empty & answer)}/{len(empty)} empty places   "
          f"raw off-target (neither hidden nor empty): {len(answer - zeros - empty)}", flush=True)

    found = dispose(reading, cells, nrows, ncols)
    extra = sorted(found - zeros)
    lost = sorted(zeros - found)
    print(f"(b) disposed |found|={len(found)}   false positives={len(extra)} {extra[:12]}"
          f"   missed zeros={len(lost)} {lost[:12]}", flush=True)

    ok_a = not missed_empty
    ok_b = found == zeros
    print(f"\nO8 (a) reader reports every empty place : {'PASS' if ok_a else 'FAIL'}", flush=True)
    print(f"O8 (b) disposal is exactly the 110      : {'PASS' if ok_b else 'FAIL'}", flush=True)
    print(f"O8 VERDICT: {'PASS' if (ok_a and ok_b) else 'FAIL — the spec is refuted, not patched'}",
          flush=True)
    return 0 if (ok_a and ok_b) else 1


if __name__ == "__main__":
    raise SystemExit(main())
