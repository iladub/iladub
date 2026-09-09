"""Whole-corpus verdict snapshot — the instrument behind [[R167]]'s oracle O4.

O4 asks a before/after question: does changing what `celltype.is_blank` recognises move ANY
reading anywhere in the corpus, or only where the changed glyph is present? Answering it needs
two readings of all seven documents, and §3 of the spec
(`docs/superpowers/specs/2026-09-09-the-nil-glyph-design.md`) records why they cannot be taken in
one process: `feed.py`, `unitmarker.py` and `datagrid.py` all do `from .celltype import is_blank`,
so the name is bound at import in each module and monkeypatching `celltype.is_blank` reaches only
`_cell_datatype`. This script therefore takes ONE reading and writes it to disk; the caller runs it
twice against two trees and diffs the two directories.

What a snapshot records, per document:

  * the document score and its two operands (asserted / escalated);
  * every page's per-region verdict, cell count and reason — the reading, band by band;
  * `recognized` / `chains` / `refused_licences` / `repaired_bands` / `adopted` — the
    document-level decisions, which a per-page differ would miss entirely;
  * a CANONICAL HASH of the whole merged graph (sorted N-Triples, blank-node labels normalised
    away), so the comparison is over every emitted triple and not only over the summary fields.

The hash is what makes this a whole-file diff rather than a verdict diff: two readings can agree
on every verdict and still differ in a cell's text or datatype, which is precisely the class of
change this loop makes.

Run it from the repo root:

    PYTHONPATH=src .venv/bin/python scripts/corpus_verdict_snapshot.py <out-dir>

Gate classification (CLAUDE.md §8): PROCEDURAL. It READS compile results and writes them down.
It decides nothing about any document, changes no reading, and carries no tolerance — the only
operations are field access, sorting and a SHA-256. Irreducible to AXIOM because the two graphs
being compared are never both in a store (one of them belongs to a different checkout of the
tree), and irreducible to NEURAL because nothing here is underdetermined.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

CORPUS = pathlib.Path("corpus")
_BNODE = re.compile(r"_:[A-Za-z0-9]+")


def _canonical_hash(graph) -> str:
    """SHA-256 over the graph's sorted N-Triples with blank-node labels normalised.

    Blank-node labels are allocated per parse and carry no meaning, so comparing them across
    two processes would report a difference that is not one. Normalising them to a constant
    is lossy in principle — two graphs differing ONLY in how blank nodes are shared would hash
    alike — and is recorded as such rather than hidden; the summary fields beside the hash are
    what carry the reading itself.
    """
    lines = sorted(_BNODE.sub("_:b", ln) for ln in graph.serialize(format="nt").splitlines() if ln.strip())
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def snapshot(pdf_path: str) -> dict:
    from iladub.etkl.document import compile_document

    rep = compile_document(pdf_path)
    return {
        "pdf": pdf_path,
        "score": rep.score,
        "pages": [
            {
                "score": p.score,
                "asserted": p.asserted,
                "escalated": p.escalated,
                "regions": [
                    {"kind": str(r.kind), "verdict": r.verdict, "cells": r.cells,
                     "reason": r.reason, "anchor": r.anchor,
                     "table": str(r.table_uri) if r.table_uri else None}
                    for r in p.regions
                ],
            }
            for p in rep.pages
        ],
        "recognized": [list(t) for t in rep.recognized],
        "refused_licences": [list(t) for t in rep.refused_licences],
        "repaired_bands": [list(t) for t in rep.repaired_bands],
        "adopted": list(rep.adopted),
        "chains": [[str(u) for u in c] for c in rep.chains],
        "notes": list(rep.notes),
        "graph_triples": len(rep.graph),
        "graph_sha256": _canonical_hash(rep.graph),
    }


def main(argv):
    out = pathlib.Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(str(p) for p in CORPUS.rglob("*.pdf"))
    if not pdfs:
        raise SystemExit("no corpus PDFs found — corpus/ is gitignored; run from a checkout "
                         "that has it, never from a fresh worktree")
    for pdf in pdfs:
        name = pathlib.Path(pdf).stem
        snap = snapshot(pdf)
        (out / f"{name}.json").write_text(json.dumps(snap, indent=2, sort_keys=True))
        print(f"{name:38} score={snap['score']!r:22} triples={snap['graph_triples']:6} "
              f"sha={snap['graph_sha256'][:12]}", flush=True)


if __name__ == "__main__":
    main(sys.argv)
