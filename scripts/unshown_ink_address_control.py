"""unshown_ink_address_control — O7's null, run in the form the control actually takes (R213).

    ./.venv/bin/python scripts/unshown_ink_address_control.py

THE QUESTION. The NEURAL reader answers in GRID space — `headers._grid_cells`' (row, col) — and
the membrane and the contract read `tab:EntryCell`s, whose index is minted by a different producer
at each of the six minting sites. Spec § 8.4 measured the two spaces COINCIDING on graincorp-
capacity — 406/406 cells, 110/110 zeros, by set identity — and said in terms that this is
EMPIRICAL, not structural. This instrument asks whether it holds anywhere else.

THE METHOD, and why it is maximal. Declare EVERY populated grid address of every gridded band
unshown, compile the document through the real dispatch, and see whether
`holon._UnshownCarriage.refuse_unless_complete` fires. It fires exactly when an address in grid
space reaches no minted `tab:EntryCell`. A real disposal supplies a SUBSET of these addresses, so
this measures the JOIN, not the disposal — a document that refuses here would refuse a real
disposal only if a disposed address landed in the disagreeing part.

A control that cannot fire is not a control (this repo's own repeated lesson), and the plan
required O7's null to be found or its absence recorded. Measured 2026-09-18: it fires on SIX of
seven corpus documents, through four different makers. Only graincorp-capacity — the one document
§ 8.4 measured — agrees.

Measurement only: reads nothing the pipeline writes, writes nothing, decides nothing.
"""
from __future__ import annotations

import glob
import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from iladub.etkl import compile as _compile                        # noqa: E402
from iladub.etkl.headers import _grid_cells                        # noqa: E402
from iladub.etkl.holon import UnshownCarriageError                 # noqa: E402
from iladub.etkl.regions import classify                           # noqa: E402

CORPUS = "corpus/*/*.pdf"
_orig_page_bands = _compile.page_bands


def _saturated_page_bands(pdf_path, page_number=0, section_repair_bands=None):
    """Every populated grid address declared unshown — the maximal probe."""
    out = []
    for band in _orig_page_bands(pdf_path, page_number, section_repair_bands):
        reg = classify(band)
        if reg.grid is None:
            out.append(band)
            continue
        addrs = tuple(sorted({(r, c) for r, c, _t in _grid_cells(band, reg.grid)}))
        out.append(replace(band, unshown=addrs) if addrs else band)
    return out


def main() -> int:
    _compile.page_bands = _saturated_page_bands
    from iladub.etkl.document import compile_document

    fired = agreed = 0
    for path in sorted(glob.glob(CORPUS)):
        name = os.path.basename(path)
        try:
            compile_document(path)
        except UnshownCarriageError as ex:
            print(f"{name:42s} REFUSED     {str(ex)[:150]}", flush=True)
            fired += 1
        except Exception as ex:                       # noqa: BLE001 — a census, not a gate
            print(f"{name:42s} other: {type(ex).__name__}: {str(ex)[:110]}", flush=True)
        else:
            print(f"{name:42s} NO REFUSAL  (address spaces agree on every carried region)",
                  flush=True)
            agreed += 1
    print(f"\nO7 CONTROL: fired on {fired} document(s), silent on {agreed}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
