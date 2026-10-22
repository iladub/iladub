"""Ground-truth vocabulary shared by the truth extractor and the scorer.

Gate classification (CLAUDE.md section 8): PROCEDURAL. `normalise` is three string rules and
`TruthRow` is a record type; `score_table` is a decidable exact comparison of two finite sets of
(key, value) pairs by string equality on declared keys: label, occurrence, column path, value.
Nothing here reads a document, reads geometry, or decides a reading. Irreducible to AXIOM because
the product is a tally of outcomes against an external truth file, not a fact of the evidence graph
(the graph is read, never grown, and the closed-world counting is the point of a scorer), and
irreducible to NEURAL because nothing is underdetermined. It carries no tolerance and no tuned
constant (spec 2026-10-22 sections 3.2, 3.3, 9.2, 10.2, 10.3).
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

_WS = re.compile(r"\s+")
_SIGN = re.compile(r"^([+-])\s+(?=\d)")


def normalise(text: str) -> str:
    """Exactly the three declared rules: NFKC; collapse whitespace and strip; close a leading
    sign's gap before a digit. No case folding, no number parsing."""
    s = unicodedata.normalize("NFKC", text)
    s = _WS.sub(" ", s).strip()
    return _SIGN.sub(r"\1", s)


@dataclass(frozen=True)
class TruthRow:
    """One truth cell. Field order is the CSV column order."""

    row_label: str
    row_label_marked: str
    row_occurrence: int
    col_path: str
    value: str


class TableSpanMismatch(ValueError):
    """The table's byte span does not hash to the pinned SHA-256."""


class TruthMarkupError(ValueError):
    """The publisher's markup is not what the extractor reads (unknown header id, or a header
    text containing the path separator)."""


OUTCOMES = ("CORRECT", "WRONG_VALUE", "MISATTACHED", "LOST", "MISSING", "REFUSED")
_SEP = " \u203a "          # the CSV's column-path separator, ' › '


def load_truth(table_dir: Path, table: str) -> tuple[list[TruthRow], list[int]]:
    """`<table_dir>/<table>.csv` as TruthRows, and the table's `pages` from `provenance.json`."""
    table_dir = Path(table_dir)
    with open(table_dir / f"{table}.csv", encoding="utf-8", newline="") as fh:
        rows = [TruthRow(r["row_label"], r["row_label_marked"], int(r["row_occurrence"]),
                         r["col_path"], r["value"]) for r in csv.DictReader(fh)]
    pages = json.loads((table_dir / "provenance.json").read_text(encoding="utf-8"))["pages"]
    return rows, list(pages)


def _on_pages(region: str, pages: Sequence[int]) -> bool:
    return any(region.startswith((f"p{p}-", f"p{p}#")) for p in pages)


def score_table(graph, truth: Sequence[TruthRow], pages: Sequence[int],
                refused_texts: Sequence[str]) -> dict[str, int]:
    """Score the compiler's carried cells against the truth cells of one table (spec 3.3, 9.2, 10).

    Every truth cell gets exactly one of CORRECT, WRONG_VALUE, MISATTACHED, LOST, MISSING, REFUSED;
    SPURIOUS and MARKED_LABEL are reported beside them. `refused_texts` is the text of the
    non-asserted regions on `pages`, supplied by the caller (the compiler's own verdicts)."""
    from iladub.feed import table_records      # local: feed imports are heavy and truth.py is light

    cands = [r for r in table_records(graph, per_cell=True)
             if any(_on_pages(c.region, pages) for c in r.concepts)]
    # (normalised text, normalised value) per concept, kept parallel to r.concepts
    norm = [[(normalise(c.text), normalise(c.value)) for c in r.concepts] for r in cands]
    refused = [normalise(t) for t in refused_texts]
    out = {k: 0 for k in OUTCOMES} | {"SPURIOUS": 0, "MARKED_LABEL": 0}

    groups: dict[tuple, list[TruthRow]] = {}
    for t in truth:
        groups.setdefault((t.row_label, t.row_label_marked, t.row_occurrence), []).append(t)

    for (label, marked, occ), cells in groups.items():
        wanted = {normalise(label), normalise(marked)}
        # a record matches when EXACTLY ONE concept's value is the label; two is a refusal
        hits = []
        for i, ns in enumerate(norm):
            idx = [j for j, (_t, v) in enumerate(ns) if v in wanted]
            if len(idx) == 1:
                hits.append((i, idx[0]))
        if occ < len(hits):
            i, j = hits[occ]
            if norm[i][j][1] != normalise(label):
                out["MARKED_LABEL"] += 1
            _score_row(cells, [n for k, n in enumerate(norm[i]) if k != j], out)
            continue
        if any(wanted & {x for pair in ns for x in pair} for ns in norm):       # (i)
            verdict = "MISSING"
        elif any(w in t for w in wanted for t in refused):                      # (ii)
            verdict = "REFUSED"
        else:                                                                   # (iii)
            verdict = "MISSING"
        out[verdict] += len(cells)
    return out


def _score_row(cells: Sequence[TruthRow], compiled: list[tuple[str, str]], out: dict) -> None:
    """The outcome ladder of one matched row (spec 9.2 item 4). `compiled` is the record's
    (col_path, value) cells minus the label. Pass 1 gives every cell its CORRECT/WRONG_VALUE step
    before pass 2 gives any cell its MISATTACHED/LOST step, and each compiled cell is claimed once."""
    claimed: set[int] = set()
    todo = []
    for t in cells:
        path, value = normalise(t.col_path.replace(_SEP, " > ")), normalise(t.value)
        same_path = [k for k, (p, _v) in enumerate(compiled) if p == path and k not in claimed]
        equal = [k for k in same_path if compiled[k][1] == value]
        if equal:
            claimed.add(equal[0])
            out["CORRECT"] += 1
        elif same_path:
            claimed.add(same_path[0])
            out["WRONG_VALUE"] += 1
        else:
            todo.append(value)
    for value in todo:
        same_value = [k for k, (_p, v) in enumerate(compiled) if v == value and k not in claimed]
        if same_value:
            claimed.add(same_value[0])
            out["MISATTACHED"] += 1
        else:
            out["LOST"] += 1
    out["SPURIOUS"] += len(compiled) - len(claimed)
