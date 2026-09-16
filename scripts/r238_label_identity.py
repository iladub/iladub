#!/usr/bin/env python3
"""R238 — are the 92 newly-carried cells the RIGHT cells? The IDENTITY probe.

The maintainer's ruling of 2026-09-16 (`docs/superpowers/2026-09-16-identity-before-remedy-ruling.md`)
makes this the subject, ahead of any remedy and ahead of scope. PR #239 measured that
refusing the decoration universe carries **92 more cells** on bfs p5 at zero score cost, and
its evidence § 3d measured **cardinality and side of the rectangle** — col 0 full at 46 of 46
rows, left of the decoration rectangle's 124.3 edge; col 11 full at 46 of 46, right of 495.3.
It did NOT measure IDENTITY, and the sample it printed read YEARS (`2005`, `2006`) — the T1
time-series rows — not the canton names [[R238]]'s symptom actually names.

WHY THAT GAP IS NOT PEDANTRY. If the labels land against the wrong rows the finding INVERTS:
the switch would not carry 92 more cells, it would assert 92 UNSUPPORTED facts — a CLAUDE.md
§ 7 violation, strictly worse than the 404-cell reading it replaces. A remedy designed on the
current headline would ship that.

WHY A YEAR CANNOT EXHIBIT THE RISK THIS PROBE IS LOOKING FOR. `_place_for_emit` keys a run on
its CENTRE (`datagrid.py:764`). A 4-character year (`2005`, x0 72.12) is a short run whose
centre sits deep inside col 0. The canton labels are not: `Appenzell Rh.-Ext.`, `Bâle-Campagne`
and `Saint-Gall` are long left-aligned runs, and a long run's centre can fall RIGHT of col 0's
boundary — landing in col 1, where it either displaces or fuses with that row's first data
value. That is the concrete failure mode § 3d's sample was structurally unable to show.

WHAT IS COMPARED, AND WHY THE TRUTH SIDE IS INDEPENDENT. Truth is `line.words` sorted by `x0`
— the raw extraction the pipeline itself saw, carrying NO column decision. The probe compares
it against the reconstruction of the same line from the emitted cells. The independence that
matters here is from the COLUMN decision, not from word extraction, and this has it. The
comparison is threshold-free and total: every word, in order.

  C1  RECONSTRUCTION. Concatenating the emitted cell texts in column order must reproduce the
      line's own word sequence exactly. This subsumes label identity — a label landing in the
      wrong column, or a name split across col 0 and col 1, shows up as a sequence mismatch.
  C2  EDGES. Col 0 must carry the line's leading ink and the last column its trailing ink.
      **C2 AS PRE-REGISTERED WAS MIS-SPECIFIED, and both forms are reported rather than one
      quietly replacing the other.** It compared the cell text to the line's first WORD, but a
      cell legitimately holds a multi-word run: `Suisse 3` (name + footnote marker) and
      `Appenzell Rh.-Ext.` are CORRECT cells that the first-word form calls failures. C2' is
      the threshold-free repair — the col-0 cell's words must be a PREFIX of the line's word
      sequence and the last cell's a SUFFIX. The original verdict stays in the output because
      amending a check after seeing the numbers is how a refuted claim gets rescued, and the
      only defence is showing both.
  C3  PAIRING. For each canton row the emitted label must be that row's own canton name and
      the final cell that row's own `en %` value.

CONTROLS. A clean 27/27 is self-validating unless the checker can be shown to FAIL, so:

  P    POSITIVE — the probe must reproduce § 3d: under `alignment`, 12 columns, 46 rows, 496
       placed cells, col 0 and col 11 full at 46/46.
  U    UNIVERSE NULL — under the shipped `decoration` universe the same probe must read col 0
       at 18 cells holding DATA values, not labels. A probe that cannot tell the two universes
       apart is measuring itself.
  S    SHIFT NULL — re-run C1/C3 pairing row i's emitted cells against row i+1's source words.
       This MUST report mismatches on essentially every canton row. If a deliberately broken
       pairing still passes, the checker detects nothing and every verdict above is void.

Gate classification (CLAUDE.md § 8): PROCEDURAL. It runs shipped derivations over a shipped
input and prints the comparison; it decides nothing, carries no threshold and no tolerance,
and changes no shipped file. The one structural discriminator it uses — a canton row is an
admitted row whose leading word is non-numeric — is a property of the source, not a tuned
constant, and the year rows it separates are printed too rather than discarded.

Run it from the repo root:

    PYTHONPATH=src:. .venv/bin/python scripts/r238_label_identity.py
"""
from __future__ import annotations

import sys

import iladub.etkl.datagrid as dg
from iladub.etkl.datagrid import (_place_for_emit, extract_words, text_lines)

BFS = "corpus/gov-stats/bfs-population-bilan-2023.pdf"
PAGE = 5


def _lines(pdf: str, page: int):
    return [ln for ln in sorted(text_lines(extract_words(pdf, page)),
                                key=lambda l: l.top) if ln.words]


def _grid(pdf: str, page: int, universe: str):
    original = dg._boundaries_from_decoration
    if universe == "alignment":
        dg._boundaries_from_decoration = lambda *a, **k: None
    try:
        return dg.derive_data_grid(pdf, page)
    finally:
        dg._boundaries_from_decoration = original


def _source_words(line) -> list[str]:
    """Truth: the line's own words, left to right. No column decision involved."""
    return [w.text for w in sorted(line.words, key=lambda w: w.x0)]


def _emitted(line, grid) -> tuple[dict, list[str]]:
    placed = _place_for_emit(line, grid)
    seq: list[str] = []
    for _, (text, _x0, _x1) in sorted(placed.items()):
        seq.extend(text.split())
    return placed, seq


def _is_canton_row(words: list[str]) -> bool:
    """Structural, not a curated list: a canton row leads with non-numeric ink."""
    return bool(words) and not words[0][0].isdigit()


def report(universe: str) -> dict:
    lines = _lines(BFS, PAGE)
    grid = _grid(BFS, PAGE, universe)
    ncols = len(grid.columns)
    fill: dict[int, int] = {}
    placed_total = 0
    rows: list[dict] = []
    for i in grid.rows:
        placed, seq = _emitted(lines[i], grid)
        placed_total += len(placed)
        for k in placed:
            fill[k] = fill.get(k, 0) + 1
        src = _source_words(lines[i])
        rows.append({"i": i, "src": src, "seq": seq, "placed": placed,
                     "canton": _is_canton_row(src)})
    print(f"\n=== universe={universe}: {ncols}c {len(grid.rows)}r, "
          f"{placed_total} placed cells")
    print(f"    col fill: " + "  ".join(f"c{k}:{fill.get(k, 0)}" for k in range(ncols)))
    first = rows[0] if rows else None
    if first:
        lo = sorted(first["placed"])[0] if first["placed"] else None
        print(f"    col 0 sample over all rows: "
              f"{[r['placed'].get(0, ('-',))[0] for r in rows[:4]]}")
        print(f"    last col sample over all rows: "
              f"{[r['placed'].get(ncols - 1, ('-',))[0] for r in rows[:4]]}  (lo={lo})")
    return {"grid": grid, "rows": rows, "ncols": ncols, "fill": fill,
            "placed_total": placed_total}


def identity(rep: dict, shift: bool = False, kind: str = "canton") -> dict:
    """C1/C2/C2'/C3 over one row class. `shift` is the SHIFT NULL."""
    rows = rep["rows"]
    ncols = rep["ncols"]
    sel = [r for r in rows if r["canton"] == (kind == "canton")]
    tag = "SHIFT NULL (row i's cells vs row i+1's source)" if shift else "IDENTITY"
    print(f"\n--- {tag} [{kind}]: {len(sel)} rows")
    tally = {"c1": 0, "c2": 0, "c2p": 0, "c3": 0, "c3p": 0, "all": 0, "allp": 0}
    for n, r in enumerate(sel):
        truth = sel[(n + 1) % len(sel)]["src"] if shift else r["src"]
        label = r["placed"].get(0, ("<none>",))[0]
        last = r["placed"].get(ncols - 1, ("<none>",))[0]
        lab_w, last_w = label.split(), last.split()
        c1 = r["seq"] == truth
        c2 = bool(truth) and label == truth[0]
        c3 = bool(truth) and last == truth[-1]
        # C2' / C3': threshold-free, and correct for a multi-word cell
        c2p = bool(lab_w) and truth[:len(lab_w)] == lab_w
        c3p = bool(last_w) and truth[-len(last_w):] == last_w
        for key, val in (("c1", c1), ("c2", c2), ("c2p", c2p), ("c3", c3), ("c3p", c3p),
                         ("all", c1 and c2 and c3), ("allp", c1 and c2p and c3p)):
            tally[key] += 1 if val else 0
        if not (c1 and c2p and c3p) or not c2 or n < 3 or shift:
            flags = (f"C1{'ok' if c1 else 'FAIL'} C2{'ok' if c2 else 'FAIL'} "
                     f"C2'{'ok' if c2p else 'FAIL'} C3{'ok' if c3 else 'FAIL'}")
            print(f"    line {r['i']:<3} {flags}  label={label!r:22} "
                  f"last={last!r:8} truth[0]={truth[0]!r:22} truth[-1]={truth[-1]!r}")
            if not c1:
                miss = [w for w in truth if w not in r["seq"]]
                extra = [w for w in r["seq"] if w not in truth]
                print(f"         seq {len(r['seq'])} vs src {len(truth)}  "
                      f"missing={miss[:6]} extra={extra[:6]}")
    n = len(sel)
    print(f"    => C1 {tally['c1']}/{n}   C2(pre-registered) {tally['c2']}/{n}   "
          f"C2' {tally['c2p']}/{n}   C3 {tally['c3']}/{n}   C3' {tally['c3p']}/{n}")
    print(f"       ALL as pre-registered {tally['all']}/{n}   ALL amended {tally['allp']}/{n}")
    tally["n"] = n
    return tally


def main() -> int:
    dec = report("decoration")
    ali = report("alignment")

    print("\n### CONTROL P — reproduce PR #239 § 3d under alignment")
    p_ok = (ali["ncols"] == 12 and len(ali["grid"].rows) == 46
            and ali["placed_total"] == 496
            and ali["fill"].get(0) == 46 and ali["fill"].get(11) == 46)
    print(f"    12c/46r/496 cells, c0=46, c11=46  -> {'PASS' if p_ok else 'FAIL'}")

    print("\n### CONTROL U — the probe distinguishes the two universes")
    u_ok = dec["fill"].get(0, 0) != ali["fill"].get(0, 0)
    print(f"    decoration c0={dec['fill'].get(0, 0)} vs alignment c0="
          f"{ali['fill'].get(0, 0)}  -> {'PASS' if u_ok else 'FAIL'}")

    can = identity(ali, kind="canton")
    yr = identity(ali, kind="year")
    sh = identity(ali, shift=True, kind="canton")

    print("\n### CONTROL S — a deliberately broken pairing must FAIL")
    s_bad = sh["n"] - sh["allp"]
    print(f"    shift null: {sh['allp']} pass, {s_bad} fail  -> "
          f"{'PASS' if s_bad > sh['allp'] else 'FAIL (checker detects nothing)'}")

    print(f"\n### VERDICT — canton-row identity under alignment")
    print(f"    C1 reconstruction (total, threshold-free): {can['c1']}/{can['n']}")
    print(f"    ALL as pre-registered {can['all']}/{can['n']}   "
          f"ALL amended (C2'/C3') {can['allp']}/{can['n']}")
    print(f"    year rows (T1, split across source lines): C1 {yr['c1']}/{yr['n']}, "
          f"ALL amended {yr['allp']}/{yr['n']}")
    if not (p_ok and u_ok and s_bad > sh["allp"]):
        print("REFUSED: a control failed; the verdict above is VOID.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
