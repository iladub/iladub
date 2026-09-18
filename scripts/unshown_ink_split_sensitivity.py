"""unshown_ink_split_sensitivity — can the unshown reading MOVE the header/body split?

Measurement only. Reads nothing the pipeline writes, writes nothing, decides nothing.

WHY IT EXISTS. [[R255]] says every live compile reads the same partition twice and that both
readings reach the graph — reading #1 through continuation recognition, whose evidence is built
from `Band.unshown` (`headers.py:111-112` -> `celltype.grid_evidence` -> `header-body-split.rq`).
Its amendment records that the two readings *disagreeing at that seam* was a **mechanism, never an
observed effect**: no run had shown the split actually moving. This instrument answers the
mechanism half exhaustively and OFFLINE, where a live run could only ever sample it once from a
reader measured to give three different answers to one crop ([[R253]]).

  ./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --corpus
  ./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --band cbh-stem 0 1
  ./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --contrast
  ./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --scope
  ./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --circularity

WHAT IS PERTURBED, AND WHY THAT IS THE WHOLE SPACE. `unshownink.dispose` returns
`reading.empty_cells & has_glyph`, so **every admissible reading is a subset of the band's
glyph-bearing addresses** — no reader, however wrong, can put an address outside that set into
`Band.unshown`. The sweep therefore brackets the space from both ends: the empty set (the shipped
offline value, and the floor of the lattice) and the full glyph set (its ceiling), plus every
single-address set in between. A single address is the realistic grain: the two live readings
gcap's traced compiles took differed by ONE address (110 vs 109, 2026-09-18 grain-of-the-ask
evidence § 7).

THE TWO BRANCHES ARE REPORTED SEPARATELY, because they are two different decisions and a column
that merged them would hide the interesting one. `header_body_split` returns the AXIOM's answer
(`header-body-split.rq` over the typed evidence graph) when it has one, and falls back to
`_hrule_split` — the author's topmost interior horizontal rule, PROCEDURAL geometry — when the
query returns None. Abstention can push a column out of the AXIOM's MIN entirely (`s_col = -1`
when a column has no non-abstaining body cell), so it can move the split in EITHER direction and
can silence the AXIOM altogether, handing the answer to the rule-based fallback. `axiom` below is
the query's own scalar; `final` is what the function returns.
"""
from __future__ import annotations

import glob
import os
import sys
from dataclasses import replace

import pdfplumber

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from iladub.etkl import celltype                             # noqa: E402
from iladub.etkl.compile import page_bands                   # noqa: E402
from iladub.etkl.headers import _grid_cells, _hrule_split     # noqa: E402
from iladub.etkl.regions import classify, column_of         # noqa: E402

CORPUS = "corpus/*/*.pdf"
QUERY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "vocab", "queries", "header-body-split.rq")


def split_parts(band, grid, unshown=()):
    """(axiom, final) — `header_body_split`'s two branches, named apart.

    Reproduces the function's body rather than calling it, because the function returns one
    number and this instrument's whole subject is WHICH branch produced it. Kept beside it: if
    `headers.header_body_split` changes shape, this drifts and the band-level figures it prints
    stop matching the pipeline — so the test that pins this instrument compares the two.
    """
    g = celltype.grid_evidence(_grid_cells(band, grid), grid.ncols, unshown=unshown)
    axiom = celltype.run_scalar(QUERY, g)
    return axiom, (axiom if axiom is not None else _hrule_split(band))


def gridded_bands(path):
    with pdfplumber.open(path) as pdf:
        pages = len(pdf.pages)
    for pn in range(pages):
        for bi, band in enumerate(page_bands(path, pn)):
            reg = classify(band)
            if reg.grid is not None:
                yield pn, bi, band, reg.grid


def glyphs_of(band, grid):
    return sorted({(int(r), int(c)) for r, c, _t in _grid_cells(band, grid)})


def sweep(band, grid):
    """(base, full, movers) — movers is [(addr, axiom, final), ...] for every single address
    whose abstention alone changes `final`."""
    base = split_parts(band, grid)
    addrs = glyphs_of(band, grid)
    full = split_parts(band, grid, tuple(addrs))
    movers = []
    for a in addrs:
        parts = split_parts(band, grid, (a,))
        if parts[1] != base[1]:
            movers.append((a, *parts))
    return base, full, movers, addrs


def fmt(parts):
    axiom, final = parts
    return f"{str(axiom):>4s}/{str(final):>4s}"


def corpus(only=None):
    print(f"{'document':34s} {'pg':>2s} {'b':>2s} {'rows x cols':>11s} {'ink':>5s} "
          f"{'none':>9s} {'full':>9s} {'movers':>6s}")
    print(f"{'':34s} {'':>2s} {'':>2s} {'':>11s} {'':>5s} "
          f"{'axiom/fin':>9s} {'axiom/fin':>9s}")
    tot = n_full = n_one = 0
    for path in sorted(glob.glob(CORPUS)):
        if only and only not in path:
            continue
        name = os.path.basename(path)[:34]
        for pn, bi, band, grid in gridded_bands(path):
            base, full, movers, addrs = sweep(band, grid)
            tot += 1
            n_full += (full[1] != base[1])
            n_one += bool(movers)
            print(f"{name:34s} {pn:2d} {bi:2d} {len(band.lines):4d} x {grid.ncols:<4d} "
                  f"{len(addrs):5d} {fmt(base):>9s} {fmt(full):>9s} {len(movers):6d}")
    print(f"\n{tot} gridded bands. Full abstention moves the returned split on {n_full}; "
          f"at least one SINGLE address moves it on {n_one}.")


def one_band(frag, pn, bi):
    path = next(p for p in glob.glob(CORPUS) if frag in p)
    band = page_bands(path, pn)[bi]
    grid = classify(band).grid
    if grid is None:
        print(f"{path} page {pn} band {bi} is not gridded")
        return
    base, full, movers, addrs = sweep(band, grid)
    print(f"{os.path.basename(path)} page {pn} band {bi} — "
          f"{len(band.lines)} x {grid.ncols}, {len(addrs)} glyph-bearing addresses")
    print(f"  unshown = ()            axiom/final = {fmt(base)}")
    print(f"  unshown = every address axiom/final = {fmt(full)}")
    print(f"  {len(movers)} single addresses move the returned split on their own:")
    for a, axiom, final in movers:
        texts = {(int(r), int(c)): t for r, c, t in _grid_cells(band, grid)}
        print(f"    {str(a):10s} axiom/final = {fmt((axiom, final))}   text={texts[a]!r}")


def contrast_cells(path, page_number, thresh):
    """The grid addresses holding at least one glyph below `thresh` WCAG contrast.

    Borrowed wholesale from `unshown_ink_seam_census.mode_grain`, brackets included, so the two
    instruments cannot disagree about which cells they mean. `thresh` is a CENSUS BRACKET, never
    a decision rule — nothing in `src/` reads it, and spec § 1.1 refutes the whole class of colour
    thresholds. Its use here is to name the population R213's own evidence calls hardest to judge,
    and ask what happens to the split if a reader errs across all of it.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from unshown_ink_seam_census import low_contrast_chars
    low = low_contrast_chars(path, page_number, thresh)

    def n_low_in(w):
        return sum(1 for c in low
                   if w.x0 - 0.5 <= (c["x0"] + c["x1"]) / 2 <= w.x1 + 0.5
                   and w.top - 0.5 <= (c["top"] + c["bottom"]) / 2 <= w.bottom + 0.5)

    out = {}
    for bi, band in enumerate(page_bands(path, page_number)):
        reg = classify(band)
        if reg.grid is None:
            continue
        cells = set()
        for r, ln in enumerate(band.lines):
            groups = {}
            for w in ln.words:
                groups.setdefault(column_of((w.x0 + w.x1) / 2.0, reg.grid.boundaries), []).append(w)
            for c, ws in groups.items():
                if sum(n_low_in(w) for w in ws):
                    cells.add((r, c))
        out[bi] = (band, reg.grid, cells & set(glyphs_of(band, reg.grid)))
    return out


def contrast(brackets=(("cbh-stem", 3.0), ("graincorp-capacity", 1.5))):
    """What the split does if a reader errs across a document's whole low-contrast population.

    NOT a claim about what the live reader returns — `dispose` refuses cbh's regions outright
    today (refusal 2, the grid mismatch), so no live reading of these bands exists at all. It is
    the bound in the direction that matters: the cells hardest to judge, taken together.
    """
    for frag, thresh in brackets:
        path = next(p for p in glob.glob(CORPUS) if frag in p)
        print(f"\n== {os.path.basename(path)} page 0, contrast < {thresh}")
        for bi, (band, grid, cells) in contrast_cells(path, 0, thresh).items():
            base = split_parts(band, grid)
            read = split_parts(band, grid, tuple(sorted(cells)))
            print(f"   band {bi:2d} {len(band.lines):3d} x {grid.ncols:<3d} "
                  f"low-contrast addresses {len(cells):3d}   "
                  f"axiom/final {fmt(base)} -> {fmt(read)}   "
                  f"{'MOVED' if base[1] != read[1] else 'same'}")


def scope(brackets=(("cbh-stem", 3.0), ("graincorp-capacity", 1.5))):
    """Prices the obvious remedy: scope the abstention to BODY rows, so it cannot touch a label.

    It does not hold the split, and not by a margin that a better scope would close — *which rows
    are body* is defined BY the split the scope exists to protect, so the addresses on the first
    body row are inside the scope by construction and still move it.
    """
    for frag, thresh in brackets:
        path = next(p for p in glob.glob(CORPUS) if frag in p)
        print(f"\n== {os.path.basename(path)} page 0, contrast < {thresh}")
        for bi, (band, grid, cells) in contrast_cells(path, 0, thresh).items():
            s = split_parts(band, grid)[1]
            if s is None:
                print(f"   band {bi:2d}: split None — scope undefined, {len(cells)} addresses")
                continue
            body = {a for a in cells if a[0] >= s}
            scoped = split_parts(band, grid, tuple(sorted(body)))[1]
            print(f"   band {bi:2d}: split={s:2d}  addresses {len(cells):3d} = "
                  f"{len(cells) - len(body):3d} header-row + {len(body):3d} body-row   "
                  f"body-scoped split: {scoped}  {'HELD' if scoped == s else 'MOVED'}")


def circularity(only=None):
    """Is arm B's own scope circular? Two references are possible; they are not the same set.

    [[R258]]'s ruled remedy admits a header-row address only where a second reading agrees, so it
    needs to know WHICH addresses are header rows. Two candidates, and the whole question is which
    one it may use:

      `perturbed` — the split the pipeline actually returns, i.e. computed WITH the unshown
        reading in hand. CIRCULAR by construction: the reading being checked decides the scope of
        the check, and where that reading collapsed the split the header block it leaves behind is
        the one row the collapse did not eat.
      `free`      — the split computed with `unshown = ()`, the floor of the lattice. Available
        before any reading is consumed (it is the same query over the same evidence graph, minus
        the abstentions), so it is NOT derived from the reading it scopes. This column is the one
        that decides whether arm B is buildable.

    Printed per band: both header-block sizes, the movers, how many of them fall inside the FREE
    header block, and the second-order sweep from a seeded collapse — every single address swept
    again with the collapsing mover already abstaining, which says whether a collapsed split is a
    fixed point or keeps moving.
    """
    print(f"{'document':30s} {'pg':>2s} {'b':>2s} {'ink':>5s} {'free':>4s} "
          f"{'|hdrF|':>6s} {'|hdrP|':>6s} {'mov':>4s} {'inF':>4s} {'seed':>5s} {'mov2':>5s}")
    bands = mov_tot = mov_in_free = fixed = seeded = 0
    for path in sorted(glob.glob(CORPUS)):
        if only and only not in path:
            continue
        name = os.path.basename(path)[:30]
        for pn, bi, band, grid in gridded_bands(path):
            base, _full, movers, addrs = sweep(band, grid)
            if not movers:
                continue
            bands += 1
            mov_tot += len(movers)
            free = base[1]
            hdr_free = [a for a in addrs if free is not None and a[0] < free]
            in_free = [m for m in movers if free is not None and m[0][0] < free]
            mov_in_free += len(in_free)
            # The collapsing mover that moves the split furthest DOWN is the damaging one; seed it.
            down = [m for m in movers if free is not None and m[2] is not None and m[2] < free]
            seed_addr = min(down, key=lambda m: m[2])[0] if down else movers[0][0]
            seed_parts = split_parts(band, grid, (seed_addr,))
            hdr_pert = [a for a in addrs if seed_parts[1] is not None and a[0] < seed_parts[1]]
            mov2 = [a for a in addrs
                    if a != seed_addr
                    and split_parts(band, grid, tuple(sorted({seed_addr, a})))[1] != seed_parts[1]]
            seeded += 1
            fixed += not mov2
            print(f"{name:30s} {pn:2d} {bi:2d} {len(addrs):5d} {str(free):>4s} "
                  f"{len(hdr_free):6d} {len(hdr_pert):6d} {len(movers):4d} {len(in_free):4d} "
                  f"{str(seed_parts[1]):>5s} {len(mov2):5d}")
    print(f"\n{bands} bands with at least one single-address mover; {mov_tot} movers, "
          f"{mov_in_free} of them inside the FREE header block.")
    print(f"{fixed} of {seeded} seeded collapses are fixed points — no further single address "
          f"moves the split once it has collapsed.")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--circularity"]:
        circularity(args[1] if len(args) > 1 else None)
    elif args[:1] == ["--scope"]:
        scope()
    elif args[:1] == ["--contrast"]:
        contrast()
    elif args[:1] == ["--corpus"]:
        corpus(args[1] if len(args) > 1 else None)
    elif args[:1] == ["--band"] and len(args) == 4:
        one_band(args[1], int(args[2]), int(args[3]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
