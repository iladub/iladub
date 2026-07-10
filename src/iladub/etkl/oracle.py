"""oracle — the round-trip reproduction oracle (Loop A1 core).

A recipe is certified iff replaying it FORWARD over the flat base regenerates the
original grid cell values exactly. This is the anti-overfit gate: a recovered
operation that does not reproduce the report is residue, never an assertion.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .recipe import UnpivotOp, StripAggregationOp

_TOL = 1e-6
_FUNCS = {
    "sum": sum,
    "mean": lambda xs: sum(xs) / len(xs),
    "min": min,
    "max": max,
    "count": lambda xs: float(len(xs)),
    "product": math.prod,
}


def _close(a, b):
    return abs(a - b) <= _TOL * max(1.0, abs(b))


def _fmt(x):
    """Render a computed float the way source cells read: integral floats without '.0'."""
    return str(int(round(x))) if abs(x - round(x)) <= _TOL else repr(x)


@dataclass(frozen=True)
class OracleVerdict:
    ok: bool
    residue: tuple


def replay(base, recipe):
    """Forward-apply the recipe → {(row_label, col_leaf_label): text}."""
    grid = {}
    unpivots = [op for op in recipe.operations if isinstance(op, UnpivotOp)]
    strips = [op for op in recipe.operations if isinstance(op, StripAggregationOp)]
    # 1. unpivot: place each base row's measure into the (stub_value, dimension_value) cell,
    #    and echo the stub column (col label == stub name).
    for op in unpivots:
        for row in base:
            key = row.get(op.stub)
            dim = row.get(op.dimension)
            if key is None or dim is None:
                continue
            grid[(key, dim)] = _fmt(row["__measure__"])
            grid[(key, op.stub)] = key
    # 2. strip-inverse: re-add each aggregate row/column from its members.
    #    numeric grid view keyed by (row_label, col_label).
    stub_labels = {op.stub for op in unpivots if op.stub}

    def numeric():
        return {k: v for k, v in grid.items() if _isnum(v)}
    for op in strips:
        num = numeric()
        f = _FUNCS[op.function]
        if op.axis == "column":
            rows = sorted({r for (r, _c) in num})
            for r in rows:
                operands = [float(num[(r, m)]) for m in op.member_labels if (r, m) in num]
                if operands:
                    grid[(r, op.target_label)] = _fmt(f(operands))
        else:  # row aggregate — exclude stub columns (their echo values are numeric but
               # must not receive an aggregate; stub_labels collected from UnpivotOps above)
            cols = sorted({c for (_r, c) in num if c not in stub_labels})
            for c in cols:
                operands = [float(num[(m, c)]) for m in op.member_labels if (m, c) in num]
                if operands:
                    grid[(op.target_label, c)] = _fmt(f(operands))
    return grid


def _isnum(s):
    try:
        float(s); return True
    except (TypeError, ValueError):
        return False


def round_trip(original, base, recipe):
    """Replay then exact-compare against `original` (from grid_values). Numeric cells
    compare with tolerance; text cells compare literally."""
    repro = replay(base, recipe)
    residue = []
    for key, want in original.items():
        got = repro.get(key)
        if got is None:
            residue.append("missing %r (want %r)" % (key, want)); continue
        if _isnum(want) and _isnum(got):
            if not _close(float(got), float(want)):
                residue.append("mismatch %r: want %s got %s" % (key, want, got))
        elif got != want:
            residue.append("mismatch %r: want %r got %r" % (key, want, got))
    for key in repro:
        if key not in original:
            residue.append("extra %r = %r" % (key, repro[key]))
    return OracleVerdict(not residue, tuple(residue))
