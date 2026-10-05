"""Carried-token census — does the graph carry a token that is not on its page? (R291's oracle)

§7 says: only emit what the source supports. A reading can hold every score steady and still
fabricate a value. R291 is the measured case: bfs p5's `etkl:bandText` read `20208 606 033`, the
year glued to the population, while page totals did not move. No score could see it. This census
can.

For every literal of `tab:cellText`, `etkl:bandText` and `iladub:surfaceText` in a compiled
graph, each whitespace token must be a token of its page's `extract_words`, or a run of words on
one `text_lines` line whose glyphs ABUT (gap <= 0). pdfplumber splits such runs where no reader
sees a break (graincorp-stem `1`|`5,000`, gap -0.08; apple `2`|`2,067`, gap 0.0), and the glyph
joiner rightly reads them as one token. A positive gap is never joined, so `2020`+`8` is a
finding. The page comes from the subject IRI's `/p<n>` segment.

Run it from the repo root:

    PYTHONPATH=src .venv/bin/python scripts/carried_token_census.py            # compiles corpus/
    PYTHONPATH=src .venv/bin/python scripts/carried_token_census.py <nt-dir>   # <stem>.nt graphs

A full compile of the corpus takes ~25 minutes. Never run two at once ([[corpus-runs-are-serial]]).

Measured 2026-10-05 on `4379fbe` and on `r265-grouped-numbers` with R291 fixed: the same 7
literals, none of them R291's. 5 are `surfaceText` ([[R262]]) and 2 are ons p7/p8 `bandText`
(`aSources:`, `dataset01633`, [[R292]]).

Gate classification (CLAUDE.md §8): PROCEDURAL. It reads a graph and the page's raw words and
decides nothing about any document. Zero is the only number in it. It is the abutment the
glyph joiner itself tests, not a tolerance.
"""
from __future__ import annotations

import pathlib
import re
import sys

from rdflib import Graph, URIRef

PREDS = {
    "cellText": "https://w3id.org/iladub/tab#cellText",
    "bandText": "https://w3id.org/iladub/etkl#bandText",
    "surfaceText": "https://w3id.org/iladub#surfaceText",
}
_PAGE = re.compile(r"/doc/p(\d+)[/#]")
CORPUS = pathlib.Path("corpus")


def page_tokens(words) -> set[str]:
    """Every word's tokens, plus every run of words on one line whose glyphs abut."""
    from iladub.etkl.geometry import text_lines

    toks = {t for w in words for t in w.text.split()}
    for line in text_lines(words):
        ws = line.words
        for i in range(len(ws)):
            run = ws[i].text
            for j in range(i + 1, len(ws)):
                if ws[j].x0 - ws[j - 1].x1 > 0:
                    break
                run += ws[j].text
                toks.add(run)
    return toks


def census(graph: Graph, pdf: str) -> tuple[int, list[tuple]]:
    """(literals read, findings): one finding per literal carrying an absent token."""
    from iladub.etkl.geometry import extract_words

    pages: dict[int, set[str]] = {}
    findings, n = [], 0
    for name, pred in PREDS.items():
        for s, o in graph.subject_objects(URIRef(pred)):
            m = _PAGE.search(str(s))
            if m is None:
                raise SystemExit(f"no page in subject {s}")
            p = int(m.group(1))
            if p not in pages:
                pages[p] = page_tokens(extract_words(pdf, p))
            n += 1
            absent = [t for t in str(o).split() if t not in pages[p]]
            if absent:
                findings.append((name, p, str(s).split("/doc/")[1], absent))
    return n, findings


def main(argv):
    pdfs = {p.stem: str(p) for p in CORPUS.rglob("*.pdf")}
    if not pdfs:
        raise SystemExit("no corpus PDFs found; corpus/ is gitignored, run from a checkout that has it")
    nt_dir = pathlib.Path(argv[1]) if len(argv) > 1 else None
    total = 0
    for stem, pdf in sorted(pdfs.items()):
        if nt_dir is not None:
            g = Graph()
            g.parse(str(nt_dir / f"{stem}.nt"), format="nt")
        else:
            from iladub.etkl.document import compile_document
            g = compile_document(pdf).graph
        n, findings = census(g, pdf)
        total += len(findings)
        print(f"{stem:38} literals={n:5} carrying_absent_token={len(findings)}", flush=True)
        for name, p, subj, absent in findings:
            print(f"    {name:11} p{p} {subj} {absent[:6]}")
    print(f"TOTAL {total}")


if __name__ == "__main__":
    main(sys.argv)
