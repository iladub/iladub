"""The R172 cell-level differ — the instrument that row has been open on since 2026-09-04.

R172 (`docs/superpowers/residues-open.md`) says every statement of the R165 one-band payoff
compares `assert_matrix_region`'s RETURN VALUE against `RegionReport.cells` — two different
counters — and that **no content diff has ever been run**. Its closure criterion is a diff over
the two readings' `tab:EntryCell` content on apple p0 and p1, baseline vs merged, showing that
every cell the previous reading asserted is present in the merged reading with the same text and
the same column, and NAMING what the additional entries are.

This script is that diff. Both readings are produced IN ONE PROCESS at HEAD:

  * the MERGED reading is `compile_tables` as it ships;
  * the BASELINE reading is `compile_tables` with `compile.merged_run_admissible` forced to
    refuse every proposal — the module-global late binding `page_bands`' own docstring names as
    the patch point, and the same one O5 uses. A page whose every proposal is refused is
    byte-identical to a page compiled before R165 existed
    (`test_a_refused_run_leaves_the_page_byte_identical`), so this is the pre-merge reading and
    not an approximation of it.

THE IDENTITY KEY IS THE INK, NOT THE URI. Table and cell URIs are minted per band, so they
cannot be compared across two partitions of the page. Every `tab:EntryCell` carries
`prov:wasDerivedFrom {doc}#p{page}-{int(x0)}-{int(top)}` — its physical origin — and
`merge_bands` concatenates already-built lines rather than re-extracting them, so a cell's bbox
is invariant across the two readings by construction. LabelCells carry no `prov:wasDerivedFrom`,
so their anchor is recomputed from `tab:hasBBox` in the identical form; that is why `_anchor`
reads the bbox for every node rather than the provenance IRI for some.

WHAT A GAINED CELL IS CLASSIFIED BY: the baseline WORD standing at its exact anchor. `page_bands`
under the same forced refusal yields the baseline partition, so band `i` there IS baseline region
`i` (`page_bands`' docstring pins that correspondence), and every word of every band is indexed by
the identical `p{page}-{int(x0)}-{int(top)}` key. A gained cell therefore either lands on a real
word — naming the band that held it and that band's baseline verdict — or lands on nothing, which
would be the merge inventing ink. That is the check that distinguishes real ink from a recount,
and it is exact in BOTH text and position; an earlier draft compared against `RegionReport.ascii`
instead and reported two false misses, because that field is a width-clipped RENDER (it shows
`(14,264` for the word `(14,264)`). The render is not the ink.

Run it from the repo root:

    PYTHONPATH=src .venv/bin/python scripts/entry_cell_diff.py \
        corpus/financial/apple-fy2026q3-statements.pdf 0 1

Gate classification (CLAUDE.md § 8): PROCEDURAL. It READS two compile results and reports their
difference. It decides nothing about any document, changes no reading, and carries no tolerance:
the only geometric predicate is exact containment of a cell's ink in a band's own extent, and the
only arithmetic is set difference. It is irreducible to AXIOM because the two graphs it compares
are never both in the store — the baseline reading is discarded by the shipped pipeline — and
irreducible to NEURAL because nothing here is underdetermined.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

from rdflib import Graph, RDF, URIRef

TAB = "https://w3id.org/iladub/tab#"
PROV_DERIVED = URIRef("http://www.w3.org/ns/prov#wasDerivedFrom")
ENTRY_CELL = URIRef(TAB + "EntryCell")
LABEL_CELL = URIRef(TAB + "LabelCell")


def _anchor(g: Graph, node: URIRef, page: int) -> str | None:
    """The node's INK anchor: `p{page}-{int(x0)}-{int(y0)}`, from its bbox.

    Deliberately recomputed rather than read off `prov:wasDerivedFrom`, so an EntryCell and a
    LabelCell are keyed the identical way — a cell that is a header in one reading and an entry
    in the other must collide, or the diff cannot see the demotion at all.
    """
    bb = g.value(node, URIRef(TAB + "hasBBox"))
    if bb is None:
        return None
    x0 = g.value(bb, URIRef(TAB + "x0"))
    y0 = g.value(bb, URIRef(TAB + "y0"))
    if x0 is None or y0 is None:
        return None
    return f"p{page}-{int(float(x0))}-{int(float(y0))}"


def _labels_for(g: Graph, axis_uri: URIRef, covers: str) -> tuple[str, ...]:
    """The label texts of every HeaderNode covering `axis_uri`, ordered by `tab:headerLevel`.

    This is the column (or row) IDENTITY the criterion asks about: URIs differ between the two
    readings, the label path does not.
    """
    out = []
    for hn in g.subjects(URIRef(TAB + covers), axis_uri):
        lvl = g.value(hn, URIRef(TAB + "headerLevel"))
        lab = g.value(hn, URIRef(TAB + "hasLabel"))
        txt = g.value(lab, URIRef(TAB + "cellText")) if lab is not None else None
        out.append((int(lvl) if lvl is not None else 0, str(txt) if txt is not None else ""))
    return tuple(t for _, t in sorted(out))


@dataclass(frozen=True)
class Cell:
    anchor: str
    text: str
    columns: tuple[str, ...]
    rows: tuple[str, ...]
    table: str


def _read(g: Graph, page: int) -> tuple[dict[str, Cell], dict[str, Cell]]:
    """(entries, labels) of one reading, both keyed by ink anchor."""
    entries: dict[str, Cell] = {}
    labels: dict[str, Cell] = {}
    for kind, sink in ((ENTRY_CELL, entries), (LABEL_CELL, labels)):
        for c in g.subjects(RDF.type, kind):
            a = _anchor(g, c, page)
            if a is None:
                continue
            table = next((str(t) for t in g.subjects(URIRef(TAB + "hasCell"), c)), "")
            col = g.value(c, URIRef(TAB + "atColumn"))
            row = g.value(c, URIRef(TAB + "atRow"))
            sink[a] = Cell(
                anchor=a,
                text=str(g.value(c, URIRef(TAB + "cellText")) or ""),
                columns=_labels_for(g, col, "coversColumn") if col is not None else (),
                rows=_labels_for(g, row, "coversRow") if row is not None else (),
                table=table.split("#")[-1],
            )
    return entries, labels


def _word_index(bands, page: int) -> dict[str, tuple[int, str]]:
    """Every WORD of the baseline partition, keyed by the same ink anchor the cells use.

    This is the page's ground-truth ink inventory: `merge_bands` concatenates already-built
    lines, so a word's (x0, top) is invariant across the two readings and an anchor collision is
    identity, not coincidence. A later band wins a duplicate key, which cannot occur here (two
    words at the same rounded origin would be overprinted ink) and would be visible as a text
    mismatch in the report rather than silently absorbed.
    """
    out: dict[str, tuple[int, str]] = {}
    for i, b in enumerate(bands):
        for ln in b.lines:
            for w in ln.words:
                out[f"p{page}-{int(w.x0)}-{int(w.top)}"] = (i, w.text)
    return out


@dataclass(frozen=True)
class Comparison:
    """The two readings of one page, and their difference. A value, so a test can assert on it
    without parsing this script's stdout — `diff_page` is only the printer."""
    page: int
    base: object            # the BASELINE CompilationReport (every run proposal refused)
    merged: object          # the MERGED CompilationReport (compile_tables as it ships)
    b_entries: dict         # baseline EntryCells by ink anchor
    m_entries: dict         # merged   EntryCells by ink anchor
    b_labels: dict          # baseline LabelCells by ink anchor
    m_labels: dict          # merged   LabelCells by ink anchor
    words: dict             # every baseline WORD by ink anchor -> (band index, text)
    lost: tuple             # baseline entry anchors absent from the merged ENTRY set
    kept: tuple
    changed: tuple          # kept anchors whose text or column path moved
    gained: tuple           # merged entry anchors the baseline had no entry at


def compare(pdf: str, page: int) -> Comparison:
    """Both readings of one page, and their difference. See the module docstring for why the
    baseline is produced by patching `merged_run_admissible` rather than by a worktree."""
    from iladub.etkl import compile as C

    merged = C.compile_tables(pdf, page_number=page, validate_shapes=False)
    orig = C.merged_run_admissible
    C.merged_run_admissible = lambda *a, **k: False
    try:
        base = C.compile_tables(pdf, page_number=page, validate_shapes=False)
        base_bands = C.page_bands(pdf, page)
    finally:
        C.merged_run_admissible = orig

    m_entries, m_labels = _read(merged.graph, page)
    b_entries, b_labels = _read(base.graph, page)
    kept = sorted(set(b_entries) & set(m_entries))
    return Comparison(
        page=page, base=base, merged=merged,
        b_entries=b_entries, m_entries=m_entries,
        b_labels=b_labels, m_labels=m_labels,
        words=_word_index(base_bands, page),
        lost=tuple(sorted(set(b_entries) - set(m_entries))),
        kept=tuple(kept),
        changed=tuple(a for a in kept if b_entries[a].text != m_entries[a].text
                      or b_entries[a].columns != m_entries[a].columns),
        gained=tuple(sorted(set(m_entries) - set(b_entries))),
    )


def diff_page(pdf: str, page: int) -> Comparison:
    cmp = compare(pdf, page)
    base, merged = cmp.base, cmp.merged
    b_entries, m_entries = cmp.b_entries, cmp.m_entries
    b_labels, m_labels = cmp.b_labels, cmp.m_labels
    lost, kept, changed, gained = list(cmp.lost), list(cmp.kept), list(cmp.changed), list(cmp.gained)

    print(f"\n=== {pdf} page {page}")
    print(f"  BASELINE  score={base.score:.6f} tokens asserted={base.asserted} "
          f"escalated={base.escalated}  entry cells={len(b_entries)} labels={len(b_labels)}")
    print(f"  MERGED    score={merged.score:.6f} tokens asserted={merged.asserted} "
          f"escalated={merged.escalated}  entry cells={len(m_entries)} labels={len(m_labels)}")
    print("  baseline bands: " + ", ".join(
        f"{i}:{r.verdict}({r.cells})" for i, r in enumerate(base.regions)))

    print(f"\n  -- LOST: baseline entry cells absent from the merged reading: {len(lost)}")
    for a in lost:
        c = b_entries[a]
        became = "LABEL in merged" if a in m_labels else "ABSENT from merged graph"
        print(f"     {a:22} {c.text!r:24} col={c.columns} row={c.rows} -> {became}")

    print(f"\n  -- KEPT: {len(kept)}   of which text-or-column CHANGED: {len(changed)}")
    for a in changed:
        b, m = b_entries[a], m_entries[a]
        print(f"     {a:22} text {b.text!r} -> {m.text!r}")
        print(f"     {'':22} col  {b.columns} -> {m.columns}")

    print(f"\n  -- GAINED: entry cells the merged reading has and the baseline did not: "
          f"{len(gained)}")
    words = cmp.words
    buckets: dict[str, list[str]] = {}
    for a in gained:
        hit = words.get(a)
        if hit is None:
            key = "NO BASELINE WORD AT THIS ANCHOR — the merge invented ink"
        else:
            i, wtext = hit
            same = "text matches the word" if wtext == m_entries[a].text \
                else f"TEXT DIFFERS from the word {wtext!r}"
            was = "was a baseline LABEL" if a in b_labels else "not asserted at baseline"
            key = f"band {i} {base.regions[i].verdict} / {was} / {same}"
        buckets.setdefault(key, []).append(a)
    for key in sorted(buckets):
        anchors = buckets[key]
        print(f"     [{len(anchors):3}] {key}")
        for a in anchors[:4]:
            c = m_entries[a]
            print(f"            {a:22} {c.text!r:24} col={c.columns} row={c.rows}")
        if len(anchors) > 4:
            print(f"            \u2026 {len(anchors) - 4} more")

    print("\n  -- INK LEDGER: baseline words per band, and how many the merged reading asserts")
    per_band: dict[int, list[str]] = {}
    for a, (i, _) in words.items():
        per_band.setdefault(i, []).append(a)
    for i in sorted(per_band):
        anchors = set(per_band[i])
        print(f"     band {i:2} {base.regions[i].verdict:11} words={len(anchors):4} "
              f"baseline entries={len(anchors & set(b_entries)):4} "
              f"merged entries={len(anchors & set(m_entries)):4}")

    # THE DENOMINATOR MOVED, and the score cannot be compared across the merge without saying so.
    # The token unit is asymmetric by construction: an ESCALATED band books every word of every
    # line it holds (compile.py:744 — `sum(len(ln.words) for ln in band.lines)`), row stubs and
    # all, while an ASSERTED matrix band books only its DATA cells' words (compile.py:923 —
    # `sum(len(c.words) for c in data_cells …)`). So reading a band instead of escalating it
    # REMOVES its label ink from asserted+escalated rather than moving it across. This is not
    # introduced by the merge; the merge is simply the first change large enough to make it
    # visible on a whole page.
    b_denom, m_denom = base.asserted + base.escalated, merged.asserted + merged.escalated
    total_words = sum(len(set(v)) for v in per_band.values())
    print(f"\n  -- TOKEN DENOMINATOR: baseline {b_denom} (={base.asserted}+{base.escalated}) "
          f"-> merged {m_denom} (={merged.asserted}+{merged.escalated})   delta {m_denom - b_denom}")
    print(f"     page words in banded ink: {total_words}   "
          f"counted NOWHERE at baseline: {total_words - b_denom}   "
          f"counted nowhere when merged: {total_words - m_denom}")

    return cmp


def main(argv):
    pdf = argv[1]
    pages = [int(p) for p in argv[2:]] or [0]
    for p in pages:
        diff_page(pdf, p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
