"""R261 Task 0 — baseline (C2's "before") + census restated under the production rule.

PROCEDURAL (CLAUDE.md s8): raw extraction (compile results, graph triples) plus decidable
exact arithmetic (Decimal sums, canonical-hash comparison). It changes no reading and decides
nothing about any document; it only reads and records. Irreducible to AXIOM/NEURAL for the same
reason `corpus_verdict_snapshot.py` and `section_total_fp_census.py` are PROCEDURAL (see their
own docstrings, which this script's two halves are built from).

Two steps, run serially (corpus-runs-are-serial):

  --baseline   Step 1. For each of the 7 corpus documents: compile_document, then
               rdflib.compare.to_canonical_graph, sha256 over the sorted N-Triples, triple
               count, score. This is Task 6 C2's "before".

  --census     Step 2. Restate the census (Addendum 1/2: 24 pairs, 5 matches, 4 true + 1 false)
               using M6's parser (`headers.is_numeric` + `rows._numeric_token_sum`, never
               `as_decimal`) and LONE-LINE candidates only (spec s2.1): a line of exactly one
               word that `is_numeric`. Same population filter as
               `scripts/section_total_fp_census.py` (asserted non-grid table regions with a
               following band) so the two censuses are comparable; the filter is additionally
               narrowed to lone-line candidates, which is the thing under test.

Run from the repo root:
    env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python scripts/r261_baseline.py --baseline
    env -u BAML_LIVE -u ILADUB_RECORD_READINGS .venv/bin/python scripts/r261_baseline.py --census
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
from decimal import Decimal

sys.path.insert(0, "src")

CORPUS = pathlib.Path("corpus")


def _canonical_hash(graph) -> tuple[str, int]:
    """sha256 over sorted N-Triples of `to_canonical_graph(graph)`; also returns the raw
    (non-canonicalised) triple count, matching `corpus_verdict_snapshot.py`'s field."""
    from rdflib.compare import to_canonical_graph

    cg = to_canonical_graph(graph)
    lines = sorted(ln for ln in cg.serialize(format="nt").splitlines() if ln.strip())
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest(), len(graph)


def run_baseline():
    from iladub.etkl.document import compile_document

    pdfs = sorted(str(p) for p in CORPUS.rglob("*.pdf"))
    if not pdfs:
        raise SystemExit("no corpus PDFs found -- corpus/ is gitignored; run from a checkout "
                          "that has it")
    print(f"{'document':<42}{'score':>22}{'triples':>9}  sha256(canonical NT)")
    for pdf in pdfs:
        rep = compile_document(pdf)
        sha, n = _canonical_hash(rep.graph)
        print(f"{pathlib.Path(pdf).stem:<42}{rep.score!r:>22}{n:>9}  {sha}")


def columns(graph, table_uri, TAB, _index_suffix, numeric_token_sum):
    """{col_index: (Decimal sum, member_count)} via M6's parser, `tab:atColumn` must bind."""
    per_col: dict = {}
    for entry in graph.objects(table_uri, TAB.hasCell):
        col = graph.value(entry, TAB.atColumn)
        if col is None:
            continue
        text = graph.value(entry, TAB.cellText)
        if text is None:
            continue
        val = numeric_token_sum(str(text))
        if val is None:
            continue
        try:
            ci = _index_suffix(col, table_uri, "c")
        except Exception:
            ci = str(col)
        per_col.setdefault(ci, []).append(val)
    return {ci: (sum(vals, Decimal(0)), len(vals)) for ci, vals in per_col.items()}


def run_census():
    from iladub.etkl.classifygraph import TAB
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import _index_suffix, compile_document
    from iladub.etkl.headers import is_numeric
    from iladub.etkl.rows import _numeric_token_sum

    GRID = str(TAB.DataGrid)
    pdfs = sorted(pathlib.Path("corpus").rglob("*.pdf"))

    opp = {"tables": 0, "following": 0, "lone_pairs": 0, "lone_candidates": 0}
    matches = []          # (stem, page, i, text, value, [matching cols], n_cols_matched)
    nomatches_zero = 0
    who_wfa_21_lone = None
    skipped = []           # region/band mismatch guard -- section_total_fp_census.py:101-104

    for pdf in pdfs:
        path, stem = str(pdf), pdf.stem
        rep = compile_document(path, validate_shapes=False)
        adopted = set(rep.adopted)
        for page, prep in enumerate(rep.pages):
            repair = frozenset(i for pg, i in rep.repaired_bands if pg == page)
            bands = page_bands(path, page, section_repair_bands=repair)
            extra = len(prep.regions) - len(bands)
            if extra != 0 and page not in adopted:
                skipped.append((stem, page, f"UNEXPECTED bands={len(bands)} "
                                             f"regions={len(prep.regions)}"))
                continue
            for i, r in enumerate(prep.regions):
                if r.verdict != "asserted" or r.table_uri is None or r.anchor == GRID:
                    continue
                opp["tables"] += 1
                if i + 1 >= len(bands):
                    continue
                opp["following"] += 1
                nxt = bands[i + 1]

                lone = []
                for ln in nxt.lines:
                    if len(ln.words) == 1 and is_numeric(ln.words[0].text):
                        lone.append(ln.words[0].text)
                    if who_wfa_21_lone is None and stem.startswith("who-wfa") and page == 0 \
                            and ln.words and any(w.text.strip() == "21" for w in ln.words):
                        who_wfa_21_lone = (len(ln.words) == 1)   # first hit only

                if not lone:
                    continue
                opp["lone_pairs"] += 1
                opp["lone_candidates"] += len(lone)

                cols = columns(rep.graph, r.table_uri, TAB, _index_suffix, _numeric_token_sum)
                for text in lone:
                    val = _numeric_token_sum(text)
                    hit = [(ci, n) for ci, (total, n) in cols.items() if total == val]
                    if hit:
                        matches.append((stem, page, i, text, val, hit))
                    else:
                        nomatches_zero += 1
        print(f"[{stem}] done", flush=True)

    print()
    if skipped:
        print(f"SKIPPED {len(skipped)} page(s) -- the denominator is incomplete:")
        for stem, pg, why in skipped:
            print(f"  {stem[:28]:<29} p{pg} {why}")
    else:
        print("SKIPPED 0 -- the denominator is complete.")
    print()
    print(f"asserted non-grid table regions         {opp['tables']:>6}")
    print(f"... having a following band              {opp['following']:>6}")
    print(f"... following band has >=1 lone-line num  {opp['lone_pairs']:>6}  <- PAIRS (D-restated)")
    print(f"lone-line numeric candidates (total)      {opp['lone_candidates']:>6}")
    print(f"candidates with NO column-sum match        {nomatches_zero:>6}")
    print(f"candidates with >=1 column-sum match        {len(matches):>6}")
    print()
    print("MATCHES (D3: exactly-one-column binds; >1 column tied = no bind, flagged):")
    for stem, page, i, text, val, hit in matches:
        tag = "TIE-NO-BIND" if len(hit) > 1 else "BIND"
        cols_str = ",".join(f"c{ci}(n={n})" for ci, n in hit)
        print(f"  {tag:<12}{stem:<26}p{page} t{i:<3}{text:>12} = {val}  cols=[{cols_str}]")
    print()
    print(f"who-wfa p0 '21' is a lone-line candidate: {who_wfa_21_lone}")


if __name__ == "__main__":
    if "--baseline" in sys.argv:
        run_baseline()
    elif "--census" in sys.argv:
        run_census()
    else:
        raise SystemExit("usage: r261_baseline.py --baseline | --census")
