"""R261 Task 3 — `totals.py` (PROCEDURAL): candidates and operands.

Plan `.superpowers/sdd/2026-10-01-r261-totals-family/task-3-brief.md` Step 1. Hand-built bands
(`geometry.Word`/`Line`, `bands.Band`) and a hand-built `rdflib.Graph` carrying the same
`tab:hasCell`/`tab:atColumn`/`tab:cellText` triples `holon.py`'s entry-cell emitters write
(measured: `holon.py:114-121`) — no PDF, no compile.
"""
import os
from decimal import Decimal

import pytest
from rdflib import Graph, Namespace, RDF, URIRef, Literal

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word
from iladub.etkl.totals import candidate_lines, column_operands, match_table, match_totals

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("urn:iladub:test:")


def _line(top, *words):
    ws = tuple(words)
    return Line(ws, top, top + 8.0)


def _word(text, x0=10.0, x1=50.0, top=0.0):
    return Word(text, x0, x1, top, top + 8.0)


def _band(*lines):
    return Band(tuple(lines), lines[0].top, lines[-1].bottom)


def _entry(g, table_uri, col_uri, text):
    e = URIRef(f"urn:iladub:test:e{len(list(g.objects(table_uri, TAB.hasCell)))}-{id(text)}")
    g.add((e, RDF.type, TAB.EntryCell))
    g.add((table_uri, TAB.hasCell, e))
    g.add((e, TAB.atColumn, col_uri))
    g.add((e, TAB.cellText, Literal(text)))
    return e


# ------------------------------------------------------------------ candidate_lines


def test_candidate_lines_picks_the_lone_numeric_line():
    band = _band(
        _line(0.0, _word("Header", top=0.0)),
        _line(10.0, _word("374,904", top=10.0)),
        _line(20.0, _word("Note", top=20.0), _word("text", x0=60.0, top=20.0)),
    )
    out = candidate_lines(band)
    assert out == [(1, band.lines[1], Decimal("374904"))]


def test_candidate_lines_skips_multi_word_and_non_numeric_lines():
    band = _band(
        _line(0.0, _word("21", top=0.0), _word("more", x0=60.0, top=0.0)),  # 2 words
        _line(10.0, _word("(12)", top=10.0)),                                # not numeric (M6)
        _line(20.0, _word("Total", top=20.0)),                               # not numeric
    )
    assert candidate_lines(band) == []


# ------------------------------------------------------------------ column_operands


def test_column_operands_sums_numeric_cells_per_column_skipping_non_numeric():
    g = Graph()
    table = EX.table1
    col_a = EX.colA
    col_b = EX.colB
    _entry(g, table, col_a, "100")
    _entry(g, table, col_a, "200")
    _entry(g, table, col_b, "Label")   # non-numeric -- skipped
    _entry(g, table, col_b, "50")
    ops = column_operands(g, table)
    assert ops[col_a][0] == Decimal("300")
    assert len(ops[col_a][1]) == 2
    assert ops[col_b][0] == Decimal("50")
    assert len(ops[col_b][1]) == 1


def test_column_operands_zero_cell_table_is_empty():
    g = Graph()
    assert column_operands(g, EX.emptytable) == {}


# ------------------------------------------------------------------ match_table


def test_match_table_single_matching_column_binds():
    operands = {
        EX.colA: (Decimal("300"), [EX.e1, EX.e2]),
        EX.colB: (Decimal("999"), [EX.e3, EX.e4]),
    }
    result = match_table(Decimal("300"), operands)
    assert result == (EX.colA, [EX.e1, EX.e2])


def test_match_table_two_equal_sum_columns_refuses():
    operands = {
        EX.colA: (Decimal("300"), [EX.e1, EX.e2]),
        EX.colB: (Decimal("300"), [EX.e3, EX.e4]),
    }
    assert match_table(Decimal("300"), operands) is None


def test_match_table_zero_cell_table_refuses():
    assert match_table(Decimal("300"), {}) is None


def test_match_table_single_member_column_refuses_below_two_guard():
    operands = {EX.colA: (Decimal("300"), [EX.e1])}
    assert match_table(Decimal("300"), operands) is None


# ------------------------------------------------------------------ match_totals


def test_match_totals_whole_set_binds():
    bound = [(EX.t1, Decimal("100")), (EX.t2, Decimal("200"))]
    assert match_totals(Decimal("300"), bound) == [EX.t1, EX.t2]


def test_match_totals_one_bound_total_refuses():
    bound = [(EX.t1, Decimal("100"))]
    assert match_totals(Decimal("100"), bound) is None


def test_match_totals_subset_sum_matches_but_whole_does_not_refuses():
    bound = [(EX.t1, Decimal("100")), (EX.t2, Decimal("200")), (EX.t3, Decimal("1"))]
    # the subset {t1, t2} sums to 300, equal to `value`; the WHOLE set sums to 301.
    assert match_totals(Decimal("300"), bound) is None


# ------------------------------------------------------------------ Step 2: corpus oracle
#
# `candidate_lines` + `column_operands` + `match_table`, run over the compiled corpus through the
# PRODUCTION path (`compile_document` + `page_bands`, same population filter as
# `scripts/r261_baseline.py --census`: asserted non-grid table regions with a following band),
# must reproduce Task 0 Step 2's match set EXACTLY (docs/superpowers/2026-10-01-r261-totals-
# family-evidence.md §§ 1-2): the 4 cbh-stem p0 port totals bind (374,904 / 737,289 / 660,363 /
# 178,708, each to exactly one column), 0 other candidates exist on the whole 7-document corpus,
# and who-wfa p0's `21` is excluded at `candidate_lines` (its line has 13 words, never reaching a
# column-sum comparison at all) -- an INDEPENDENT oracle, because the census computed its matches
# from a separate script (`r261_baseline.py`'s own inline `columns()`), not from this module.

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORPUS = os.path.join(ROOT, "corpus")


@pytest.mark.corpus
@pytest.mark.skipif(not os.path.isdir(CORPUS), reason="corpus not populated")
def test_corpus_reproduces_task0_match_set_exactly():
    import glob

    from iladub.etkl.classifygraph import TAB as CTAB
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import compile_document

    GRID = str(CTAB.DataGrid)
    pdfs = sorted(glob.glob(os.path.join(CORPUS, "**", "*.pdf"), recursive=True))
    assert pdfs, "corpus/ exists but has no PDFs -- not the expected fixture tree"

    matches = []   # (stem, page, region_idx, value)
    who_wfa_21_is_candidate = False

    for path in pdfs:
        stem = os.path.splitext(os.path.basename(path))[0]
        rep = compile_document(path, validate_shapes=False)
        adopted = set(rep.adopted)
        for page, prep in enumerate(rep.pages):
            repair = frozenset(i for pg, i in rep.repaired_bands if pg == page)
            bands = page_bands(path, page, section_repair_bands=repair)
            extra = len(prep.regions) - len(bands)
            if extra != 0 and page not in adopted:
                continue   # region/band mismatch guard (same as r261_baseline.py --census)
            for i, r in enumerate(prep.regions):
                if r.verdict != "asserted" or r.table_uri is None or r.anchor == GRID:
                    continue
                if i + 1 >= len(bands):
                    continue
                nxt = bands[i + 1]
                if stem.startswith("who-wfa") and page == 0:
                    for ln in nxt.lines:
                        if any(w.text.strip() == "21" for w in ln.words):
                            if len(ln.words) == 1:
                                who_wfa_21_is_candidate = True
                operands = column_operands(rep.graph, r.table_uri)
                for _, _, value in candidate_lines(nxt):
                    hit = match_table(value, operands)
                    if hit is not None:
                        matches.append((stem, page, i, value))

    expected = {
        ("cbh-stem-2026-08-03", 0, 1, Decimal("374904")),
        ("cbh-stem-2026-08-03", 0, 3, Decimal("737289")),
        ("cbh-stem-2026-08-03", 0, 5, Decimal("660363")),
        ("cbh-stem-2026-08-03", 0, 7, Decimal("178708")),
    }
    assert set(matches) == expected
    assert len(matches) == 4   # no duplicate / tied matches
    assert who_wfa_21_is_candidate is False
