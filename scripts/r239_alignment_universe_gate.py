#!/usr/bin/env python3
"""R239/R238 — the score gate: what does the ALIGNMENT universe cost the whole corpus?

Four loops have now reasoned about bfs p5's column geometry without once compiling a
document behind the patch. PR #237 measured that refusing the decoration universe fixes
both [[R238]]'s and [[R239]]'s symptoms on that page at the GRID level (27 canton rows
collapse to one column, the row label and the final `%` come inside), and PR #236 measured
that the prescribed `x1` re-key regresses 20 cells. Neither measured what the switch does
to a READING: score, adoption, escalation, round-trip, or the emitted graph.

This script is that measurement, and it decides nothing. It takes a whole-corpus
`corpus_verdict_snapshot.py` reading under one of three universes and writes it to disk for
`corpus_snapshot_diff.py` to compare:

    before     the shipped derivation, untouched
    alignment  `_boundaries_from_decoration` returns None, so every page that would have
               used a decoration rectangle falls back to the alignment universe
    null       NULL CONTROL — the patch mechanism is installed but delegates to the
               ORIGINAL function, so the reading must be byte-identical to `before` by
               canonical graph hash on all seven documents. If it is not, this harness is
               measuring itself and every `alignment` figure it produces is void.

The null control is not ceremony. The patch is a module-attribute rebind consulted at
`datagrid.py:342`, and a harness that perturbs the reading merely by being present would
report a change indistinguishable from the one being asked about. A passing positive
control does not establish that; only a null does.

WHY A MONKEYPATCH REACHES THE COMPILE PATH (measured, not assumed). At `9e69261`:
`_boundaries_from_decoration` is DEFINED at `src/iladub/etkl/datagrid.py:302` and CALLED at
exactly one site, `datagrid.py:342`, as a module-global inside its own module. No module
anywhere binds the name at import (`grep -rn "_boundaries_from_decoration" --include="*.py"
src scripts tests` returns those two lines and this file's callers only); `compile.py` and
`donation.py` import `derive_data_grid` / `emit_data_grid` / `page_has_table`, each of which
resolves the patched global at call time. The `from .celltype import is_blank` hazard
recorded in `corpus_verdict_snapshot.py`'s docstring therefore does not apply here — and the
null control is what proves that claim rather than merely arguing it.

Run it from the repo root, once per universe, then diff:

    PYTHONPATH=src .venv/bin/python scripts/r239_alignment_universe_gate.py before    out/before
    PYTHONPATH=src .venv/bin/python scripts/r239_alignment_universe_gate.py alignment out/alignment
    PYTHONPATH=src .venv/bin/python scripts/r239_alignment_universe_gate.py null      out/null
    PYTHONPATH=src .venv/bin/python scripts/corpus_snapshot_diff.py out/before out/null
    PYTHONPATH=src .venv/bin/python scripts/corpus_snapshot_diff.py out/before out/alignment

Gate classification (CLAUDE.md § 8): PROCEDURAL. It installs one module attribute, runs a
shipped derivation over shipped inputs and writes the result down. It decides nothing about
any document, carries no threshold and no tolerance, and changes no shipped file.
"""
from __future__ import annotations

import sys

import iladub.etkl.datagrid as dg

import corpus_verdict_snapshot

UNIVERSES = ("before", "alignment", "null")


def install(universe: str) -> None:
    """Rebind the decoration-boundary derivation for this process, or leave it alone."""
    original = dg._boundaries_from_decoration
    if universe == "alignment":
        dg._boundaries_from_decoration = lambda *a, **k: None
    elif universe == "null":
        dg._boundaries_from_decoration = lambda *a, **k: original(*a, **k)


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in UNIVERSES:
        print(f"usage: {argv[0]} {{{'|'.join(UNIVERSES)}}} <out-dir>", file=sys.stderr)
        return 2
    universe, out = argv[1], argv[2]
    install(universe)
    print(f"universe={universe}  _boundaries_from_decoration="
          f"{dg._boundaries_from_decoration!r}", flush=True)
    corpus_verdict_snapshot.main([argv[0], out])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
