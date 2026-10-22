"""Ground-truth vocabulary shared by the truth extractor and the scorer.

Gate classification (CLAUDE.md section 8): PROCEDURAL. `normalise` is three string rules and
`TruthRow` is a record type; nothing here reads a document or decides a reading. Irreducible to
AXIOM because it is exact string arithmetic applied identically to both sides of a comparison
(there is no evidence graph to derive from), and irreducible to NEURAL because nothing is
underdetermined. It carries no tolerance and no tuned constant (spec 2026-10-22 section 3.2).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

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
