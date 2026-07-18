from rdflib import Namespace, RDF, Literal
from rdflib.namespace import XSD

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Word, Line
from iladub.etkl.grid import infer_leaf_grid
from iladub.etkl.classifygraph import classify_evidence, run_kind, CLASSIFY_KIND_RQ

TAB = Namespace("https://w3id.org/iladub/tab#")


def _line(words):
    return Line(tuple(words), 0.0, 10.0)


def _band(lines):
    return Band(tuple(lines), 0.0, 10.0)


def _hdr(*spans):
    # spans: (text, x0, x1)
    return _line([Word(t, x0, x1, 0.0, 10.0) for (t, x0, x1) in spans])


def _grid_of(band):
    return infer_leaf_grid(band) if len(band.lines) >= 2 else None


def _straddle_band():
    # infer_leaf_grid's whitespace profile is computed over ALL band lines
    # (header included), gutter_pct=0.98. With only a couple of data rows, a
    # single header word's ink dominates its local blank fraction enough that
    # the algorithm always re-centers the gutter to swallow the word whole --
    # it never actually straddles. To get a genuine straddler the data rows
    # must outnumber the lone header row enough that the header's ink can't
    # drag the local blank fraction below 0.98 in the true (data-driven) gutter
    # region: blank_frac there = n_data / (n_data + 1) >= 0.98 requires
    # n_data >= 49; 60 gives comfortable margin. Verified empirically: with
    # 60 data rows this band's inferred grid is ncols=3,
    # boundaries=(10, 85.0, 185.0, 260.0), and STRADDLE (140-220) lands in
    # neither column 0 ([10,85]) nor column 2 ([185,260]) while A and C each
    # land cleanly in their own column (0 and 2 respectively).
    header = _hdr(("A", 10, 60), ("STRADDLE", 140, 220), ("C", 210, 260))
    data = [_hdr((str(3 * i + 1), 10, 60), (str(3 * i + 2), 110, 160), (str(3 * i + 3), 210, 260))
            for i in range(60)]
    return _band([header] + data)


# --- emitter unit tests ---

def test_emitter_counts_and_header_words():
    # header words each cleanly inside their column; a data line to make it a 2-line band
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160), ("C", 210, 260)),
                  _hdr(("1", 10, 60), ("2", 110, 160), ("3", 210, 260))])
    grid = _grid_of(band)
    g = classify_evidence(band, grid)
    b = next(g.subjects(RDF.type, TAB.ClassifyBand))
    assert g.value(b, TAB.lineCount) == Literal(2, datatype=XSD.integer)
    assert g.value(b, TAB.gridColumnCount) == Literal(grid.ncols, datatype=XSD.integer)
    hw = list(g.subjects(RDF.type, TAB.HeaderWord))
    assert len(hw) == 3
    orders = sorted(int(g.value(w, TAB.headerWordOrder)) for w in hw)
    assert orders == [0, 1, 2]
    # each header word strictly inside its own column
    for w in hw:
        o = int(g.value(w, TAB.headerWordOrder))
        assert int(g.value(w, TAB.strictlyInColumn)) == o


def test_emitter_omits_strictlyInColumn_for_straddler():
    # 3 columns from the data rows, but the middle header word straddles the gutter
    band = _straddle_band()
    grid = _grid_of(band)
    g = classify_evidence(band, grid)
    straddlers = [w for w in g.subjects(RDF.type, TAB.HeaderWord)
                  if g.value(w, TAB.strictlyInColumn) is None]
    assert len(straddlers) == 1


def test_emitter_grid_none_for_short_band():
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160))])  # 1 line
    g = classify_evidence(band, None)
    b = next(g.subjects(RDF.type, TAB.ClassifyBand))
    assert g.value(b, TAB.lineCount) == Literal(1, datatype=XSD.integer)
    assert g.value(b, TAB.gridColumnCount) == Literal(0, datatype=XSD.integer)
    assert list(g.subjects(RDF.type, TAB.HeaderWord)) == []


# --- query tests (synthetic graphs built by the emitter) ---

def _kind(band):
    grid = _grid_of(band)
    return run_kind(str(CLASSIFY_KIND_RQ), classify_evidence(band, grid))


def test_query_record_table():
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160), ("C", 210, 260)),
                  _hdr(("1", 10, 60), ("2", 110, 160), ("3", 210, 260))])
    kind, nhw, fb = _kind(band)
    assert kind == str(TAB.RecordTableKind)
    assert nhw == 3 and fb is None


def test_query_non_table_short():
    band = _band([_hdr(("A", 10, 60), ("B", 110, 160))])
    kind, nhw, fb = _kind(band)
    assert kind == str(TAB.NonTableKind)


def test_query_unsupported_straddle_first_bad():
    band = _straddle_band()
    kind, nhw, fb = _kind(band)
    assert kind == str(TAB.UnsupportedTableKind)
    assert fb == 1  # the straddler is the second (order 1) header word
