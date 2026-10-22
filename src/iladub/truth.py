"""Ground-truth vocabulary shared by the truth extractor and the scorer.

Gate classification (CLAUDE.md section 8): PROCEDURAL. `normalise` is three string rules and
`TruthRow` is a record type; `score_table` is a decidable exact comparison of two finite sets of
(key, value) pairs by string equality on declared keys: label, occurrence, column path, value.
Nothing here reads a document, reads geometry, or decides a reading. Irreducible to AXIOM because
the product is a tally of outcomes against an external truth file, not a fact of the evidence graph
(the graph is read, never grown, and the closed-world counting is the point of a scorer), and
irreducible to NEURAL because nothing is underdetermined. It carries no tolerance and no tuned
constant (spec 2026-10-22 sections 3.2, 3.3, 9.2, 10.2, 10.3, 11). Regrouping the per-cell
record shape into rows ([[R333]]) is the same class of step: it reads header paths the compile
already asserted and decides nothing.
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


class TruthShapeError(ValueError):
    """A compiled record the scorer cannot read exactly: a per-cell key's region names two
    header paths ([[R333]])."""


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
    # (normalised text, normalised value) per concept of one scored row
    norm = [[(normalise(t), normalise(v)) for t, v in row] for row in _scored_rows(graph, cands)]
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


def _scored_rows(graph, records) -> list[list[tuple[str, str]]]:
    """Each compiled row as its (text, value) pairs, in record order.

    A one-record-per-row record is its concepts. The PER-CELL shape ([[R333]]; `table_records`'
    `per_cell`) mints one record per cell of a row covered by a row header, and both its keys'
    texts are space-joined, so neither the row's leaf label nor a multi-level column path can be
    read off them. Its records are regrouped into one row by the row key's region, and both
    paths are read off the header node that region names: the row as the pair (leaf, leaf), the
    label the truth file prints, and each cell as (column path joined ' > ', value), the join
    `_header_path` gives the one-record-per-row shape. Role-less riders join the row once."""
    from iladub.ground import ROLE_CELL_VALUE, ROLE_COLUMN_KEY

    rows: list[list[tuple[str, str]]] = []
    at: dict[str, int] = {}
    paths = None
    for r in records:
        by_role = {c.role: c for c in r.concepts if c.role}
        cell = by_role.get(ROLE_CELL_VALUE)
        if cell is None:
            rows.append([(c.text, c.value) for c in r.concepts])
            continue
        if paths is None:
            paths = _paths_by_region(graph)
        (key,) = [c for c in r.concepts if c.role and c.role not in (ROLE_CELL_VALUE, ROLE_COLUMN_KEY)]
        if key.region not in at:
            leaf = _path(paths, key.region)[-1]
            at[key.region] = len(rows)
            rows.append([(leaf, leaf)] + [(c.text, c.value) for c in r.concepts if not c.role])
        col = by_role.get(ROLE_COLUMN_KEY)
        rows[at[key.region]].append((" > ".join(_path(paths, col.region)) if col else "", cell.value))
    return rows


_AMBIGUOUS = object()


def _paths_by_region(graph) -> dict:
    """Every chosen header node's label path, keyed by both forms of region a per-cell key can
    carry: `_label_region`'s readable form and the label cell's whole IRI (the form the feed
    gives a second label cell whose readable form is taken). A readable form two different
    paths share is marked ambiguous, and reading it raises."""
    from iladub.feed import TAB, _header_parts, _label_region

    tables = set(graph.subjects(TAB.hasHeaderNode, None))
    out: dict = {}
    for pred in (TAB.coversRow, TAB.coversColumn):
        for labels, node in _header_parts(graph, tables, pred).values():
            cell, region = _label_region(graph, node)
            out[str(cell)] = labels
            if out.setdefault(region, labels) != labels:
                out[region] = _AMBIGUOUS
    return out


def _path(paths: dict, region: str) -> tuple:
    labels = paths.get(region)
    if labels is None or labels is _AMBIGUOUS:
        raise TruthShapeError(f"per-cell key region {region!r} names "
                              f"{'no' if labels is None else 'more than one'} header path")
    return labels


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
