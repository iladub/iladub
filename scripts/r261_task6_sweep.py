"""R261 Task 6 — corpus sweep instrument: disjointness control + cbh cell dump.

PROCEDURAL (CLAUDE.md s8): raw extraction (graph reads) plus exact comparison (set
intersection on provenance URIs). Decides nothing, proposes nothing; records facts only.

COMMITTED here (final review item 6, ruling R283): originally left in the untracked
scratchpad/ (the task's own convention at the time distinguished a committed instrument,
`r261_baseline.py`, from a scratchpad diagnostic explaining its output), but R283 cites this
script's own run as its sole measurement — a residue row whose evidence lives only in an
untracked, about-to-be-deleted file is not reproducible, so it moves here unchanged bar this
docstring note.

Run from repo root:
    env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python scripts/r261_task6_sweep.py
"""
import pathlib
import sys

sys.path.insert(0, "src")

from rdflib import RDF  # noqa: E402
from rdflib.namespace import PROV  # noqa: E402

from iladub.etkl.classifygraph import TAB  # noqa: E402
from iladub.etkl.document import compile_document  # noqa: E402

CORPUS = pathlib.Path("corpus")


def disjointness(g):
    """No word is both a tab:SectionTotal row cell and a tab:PrintedTotal (M3: the identity
    key is the word's own provenance URI, '{doc}#p{page}-{int(x0)}-{int(top)}', which both
    _emit_entry_cell and emit_printed_total mint from the SAME word-extent convention)."""
    st_rows = set(g.subjects(RDF.type, TAB.SectionTotal))
    st_prov = set()
    st_cells = 0
    for row in st_rows:
        for entry in g.subjects(TAB.atRow, row):
            if (entry, RDF.type, TAB.EntryCell) not in g:
                continue
            st_cells += 1
            for p in g.objects(entry, PROV.wasDerivedFrom):
                st_prov.add(p)
    pt_nodes = set(g.subjects(RDF.type, TAB.PrintedTotal))
    pt_prov = set()
    for pt in pt_nodes:
        for p in g.objects(pt, PROV.wasDerivedFrom):
            pt_prov.add(p)
    overlap = st_prov & pt_prov
    return {
        "section_total_rows": len(st_rows),
        "section_total_cells": st_cells,
        "printed_total_nodes": len(pt_nodes),
        "overlap": overlap,
    }


def dump_printed_totals(g, label):
    pt_nodes = sorted(g.subjects(RDF.type, TAB.PrintedTotal))
    print(f"  PrintedTotal nodes: {len(pt_nodes)}")
    for pt in pt_nodes:
        text = g.value(pt, TAB.cellText)
        totalof = g.value(pt, TAB.totalOf)
        aggregates = list(g.objects(pt, TAB.aggregates))
        page = g.value(pt, TAB.onPage)
        prov = list(g.objects(pt, PROV.wasDerivedFrom))
        decisions = list(g.subjects(None, pt))  # anything pointing AT pt (dec:produced)
        print(f"    {pt}")
        print(f"      cellText={text!r} onPage={page} totalOf={totalof}")
        print(f"      aggregates (operand count={len(aggregates)}): {aggregates}")
        print(f"      prov:wasDerivedFrom={prov}")


def main():
    pdfs = sorted(str(p) for p in CORPUS.rglob("*.pdf"))
    print(f"{'document':<42}{'score':>22}")
    results = []
    for pdf in pdfs:
        rep = compile_document(pdf)
        g = rep.graph
        d = disjointness(g)
        results.append((pdf, rep.score, d))
        print(f"{pathlib.Path(pdf).stem:<42}{rep.score!r:>22}  "
              f"st_rows={d['section_total_rows']} st_cells={d['section_total_cells']} "
              f"pt_nodes={d['printed_total_nodes']} overlap={len(d['overlap'])}")
        if d["overlap"]:
            print(f"    !!! OVERLAP: {d['overlap']}")
        if "cbh" in pdf:
            print("  --- cbh PrintedTotal dump ---")
            dump_printed_totals(g, pathlib.Path(pdf).stem)
            # Also dump the per-band RegionReport for page 0, like Task 0 s1.2.
            prep = rep.pages[0]
            print("  --- cbh p0 RegionReport (post-sweep) ---")
            for i, r in enumerate(prep.regions):
                print(f"    {i} {r.kind} {r.verdict} cells={r.cells} "
                      f"tok_a={r.tokens_asserted} tok_e={r.tokens_escalated} "
                      f"table_uri={r.table_uri}")
    print()
    total_overlap = sum(len(d["overlap"]) for _, _, d in results)
    print(f"TOTAL disjointness overlap across corpus: {total_overlap}")
    total_pt = sum(d["printed_total_nodes"] for _, _, d in results)
    print(f"TOTAL PrintedTotal nodes across corpus: {total_pt}")


if __name__ == "__main__":
    main()
