"""The grid-agreement census: does an EARLIER band on the page carry a column grid
that this band's ink already tiles?

[[R166]]'s spec (`docs/superpowers/specs/2026-09-10-the-header-is-assumed-design.md` § 3)
answered the in-band question — no in-band signal separates a data row from a header row —
and left the cross-band remedy as [[R201]]'s three-arm design fork. All three arms need the
same missing primitive: a decidable, threshold-free relation saying *these bands are one
table*. This script measures whether the author's own drawn column rules supply it.

For every band the record-table branch reads (`regions.classify(band).kind is RECORD_TABLE`),
it asks, of each EARLIER band on the same page:

    donor  = grid._rule_boundaries(earlier_band)   # the shipped, threshold-free derivation
    tiles  = every word of THIS band lies strictly inside some [donor_i, donor_i+1]
    ncols  = len(donor) - 1 == this band's own leaf-column count
    drawn  = every boundary of the donor is an x the AUTHOR DREW, not an inferred gutter

`_rule_boundaries` is used exactly as `infer_leaf_grid` uses it, never reimplemented: it
returns a vector ONLY if the donor band's own words tile it, so a donor is by construction a
grid its own author drew and its own ink confirms. The cross-band question added here is
evidence-POSITIVE — *is this word present inside that interval* — and never asks whether an
interval is empty, which is the closed-world half `_rule_boundaries`' closure note reserves to
the band's own holon.

PROCEDURAL by CLAUDE.md §8: an instrument that reads compile results and prints them. It
decides nothing about any document, carries no tuned constant, and leaves every judgement
(is the donor's line 0 actually a header?) to the reader, in prose.

Run it from the repo root:

    PYTHONPATH=. .venv/bin/python scripts/grid_agreement_census.py [pdf ...]
"""
from __future__ import annotations

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iladub.etkl.compile import page_bands  # noqa: E402
from iladub.etkl.document import page_count  # noqa: E402
from iladub.etkl.grid import COORD_EPS, _rule_boundaries  # noqa: E402
from iladub.etkl.regions import RegionKind, classify  # noqa: E402


def straddlers(band, xs):
    """The band's words that lie inside NO interval of `xs` — the same test
    `_rule_boundaries` applies to a band's own words, asked across bands."""
    out = []
    for ln in band.lines:
        for w in ln.words:
            if not any(xs[c] - COORD_EPS <= w.x0 and w.x1 <= xs[c + 1] + COORD_EPS
                       for c in range(len(xs) - 1)):
                out.append(w)
    return out


def wholly_drawn(band, xs):
    """Is every boundary in `xs` an x the AUTHOR DREW, rather than a gutter inferred from
    whitespace? `_rule_boundaries` prefers `band.column_xs` (author rules PLUS the interior
    gutters the rules left out) over the raw marks, so this separates a band the author ruled
    from a band whose interior boundaries this compiler guessed."""
    drawn = {round(r.x, 2) for r in band.rules}
    return all(round(x, 2) in drawn for x in xs)


def line_text(band, i=0, n=6):
    if len(band.lines) <= i:
        return []
    return [w.text for w in sorted(band.lines[i].words, key=lambda w: w.x0)][:n]


def main(argv):
    pdfs = argv[1:] or sorted(glob.glob("corpus/*/*.pdf"))
    pop = donors_found = multi = 0
    for pdf in pdfs:
        name = os.path.basename(pdf).split("-")[0]
        for p in range(page_count(pdf)):
            try:
                bands = page_bands(pdf, p)
            except Exception as exc:  # noqa: BLE001
                print(f"{name} p{p}: page_bands failed: {type(exc).__name__}: {exc}")
                continue
            regs = []
            for b in bands:
                try:
                    regs.append(classify(b))
                except Exception:  # noqa: BLE001
                    regs.append(None)
            for i, reg in enumerate(regs):
                if reg is None or reg.kind is not RegionKind.RECORD_TABLE:
                    continue
                pop += 1
                ncols = reg.grid.ncols if reg.grid else None
                print(f"{name} p{p} band{i} ncols={ncols} labels={line_text(bands[i])}")
                qualifying = []
                for j in range(i):
                    try:
                        donor = _rule_boundaries(bands[j])
                    except Exception:  # noqa: BLE001
                        donor = None
                    if donor is None or len(donor) < 3:
                        continue
                    bad = straddlers(bands[i], donor)
                    same = (len(donor) - 1) == ncols
                    drawn = wholly_drawn(bands[j], donor)
                    print(f"    donor band{j}: ncols={len(donor) - 1} same_ncols={'yes' if same else 'no '}"
                          f" straddlers={len(bad)} drawn={'yes' if drawn else 'no '}")
                    if same and not bad and drawn:
                        qualifying.append(j)
                if qualifying:
                    donors_found += 1
                    if len(qualifying) > 1:
                        multi += 1
                    print(f"    -> DONORS {qualifying} (n={len(qualifying)}); "
                          f"band{qualifying[0]} line0={line_text(bands[qualifying[0]])}")
                else:
                    print("    -> no earlier band on this page supplies a tiling grid")
    print(f"\nTOTAL record-table bands: {pop}; with a wholly-drawn, same-ncols, tiling donor "
          f"earlier on the page: {donors_found}; of those, with MORE THAN ONE such donor "
          f"(i.e. the donor is not unique): {multi}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
