"""Agreement across flavours (spec 2026-10-31 § 4.5). Licence: Apache-2.0.

The three flavours of one fill must yield the same values and the same parts: `agree(a, b)` lists
the differences between two truth records in their `(field, value)` sets and in their part-type
multisets. Coordinates are ignored (each flavour lays the page out differently); so are document
ids, flavours and transforms. An empty list means agreement.

Justified PROCEDURAL (CLAUDE.md § 8): set and multiset comparison of two records the generator
wrote — decidable exact matching, no tolerance, no reading. No reader may call it (A3).
"""
from __future__ import annotations

from collections import Counter

from scripts.synthetic_contracts.truth import Truth


def agree(a: Truth, b: Truth) -> list[str]:
    out = []
    va = {(v.field, v.value) for v in a.values}
    vb = {(v.field, v.value) for v in b.values}
    out += [f"value {f}={v!r} only in {a.doc_id}" for f, v in sorted(va - vb)]
    out += [f"value {f}={v!r} only in {b.doc_id}" for f, v in sorted(vb - va)]
    pa, pb = Counter(p.type for p in a.parts), Counter(p.type for p in b.parts)
    for kind in sorted(set(pa) | set(pb)):
        if pa[kind] != pb[kind]:
            out.append(f"part type {kind}: {pa[kind]} in {a.doc_id}, {pb[kind]} in {b.doc_id}")
    return out
