"""Loop H — the author's hrules are the row delimiters (residue R4, de-fusion half).

group_wrapped absorbs a line as a wrap-continuation when its columns are a proper subset of the
anchor's, it is partial, and the gap < lead. A SUPPRESSED-KEY data row and a subtotal row are both
proper-subset partial rows — the suppressed-key convention IS the false-absorption trigger
(measured on a real report: three source lines fused into one record, '20,000 20,000 20,000' as
one cell). But the author draws every real row boundary: 35/54 line pairs carry an hrule, and the
19 that do not are exactly the genuine wraps. The veto: never absorb across an hrule.
See docs/superpowers/specs/2026-07-30-subtotal-rows-design.md §2.
"""
from iladub.etkl.bands import Band
from iladub.etkl.cells import group_wrapped
from iladub.etkl.geometry import HRule, Line, Word
from iladub.etkl.grid import LeafGrid

GRID = LeafGrid((100.0, 150.0, 200.0, 250.0, 300.0), 4, 50.0, 1.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 8.0)


def _line(words, top):
    return Line(tuple(words), top, top + 8.0)


def _texts(rows):
    return [[c.text for c in row] for row in rows]


def suppressed_key_lines():
    """A normal PRIOR row and a normal NEXT row bracket the suppressed-key triplet under test,
    at the document's ordinary 16pt row pitch — an anchor row with all 4 columns, then a
    suppressed-key data row (3 cols, proper subset) and a subtotal row (2 cols, proper subset),
    both tight-gapped (7pt), i.e. absorbable without the veto.

    The bracket rows are load-bearing, not padding: `lead` is the MEDIAN of the band's own
    gaps (cells.py), so a bare 3-line band (full, data, sub) has only two gaps, and a median of
    two values IS one of them — `gap < lead` can then never hold for both transitions at once,
    whatever the numbers, so the fused-defect this suite targets would be unreachable by
    construction. Bracketing with the ordinary pitch gives `lead` an honest population to be
    computed from, exactly as it is on a real, multi-row band — without changing which lines are
    candidates for absorption (the bracket rows are full 4-column rows, never proper subsets, so
    they are never themselves absorbed or absorbing, regardless of gap or hrule)."""
    prior = _line([_w("Jun", 105, 130, 0.0), _w("Rockhampton", 155, 205, 0.0),
                   _w("V0", 205, 230, 0.0), _w("050", 255, 280, 0.0)], 0.0)
    full = _line([_w("Jul", 105, 130, 16.0), _w("Mackay", 155, 190, 16.0),
                  _w("V1", 205, 230, 16.0), _w("100", 255, 280, 16.0)], 16.0)
    data = _line([_w("Gladstone", 155, 195, 23.0), _w("V2", 205, 230, 23.0),
                  _w("200", 255, 280, 23.0)], 23.0)
    sub = _line([_w("Total", 155, 185, 30.0), _w("300", 255, 280, 30.0)], 30.0)
    nxt = _line([_w("Aug", 105, 130, 46.0), _w("Portland", 155, 195, 46.0),
                 _w("V2", 205, 230, 46.0), _w("200", 255, 280, 46.0)], 46.0)
    return prior, full, data, sub, nxt


def test_hrule_vetoes_false_absorption():
    # THE FUSION DEFECT: without hrules these three lines fuse into one row (see
    # test_without_hrules_behavior_is_unchanged). With an hrule on EACH of the two
    # false-absorption transitions, all three stay separate rows.
    prior, full, data, sub, nxt = suppressed_key_lines()
    hrules = (HRule(20.0, 100.0, 300.0), HRule(27.0, 100.0, 300.0))
    band = Band((prior, full, data, sub, nxt), 0.0, 54.0, (), hrules)
    rows = group_wrapped(band, GRID)
    assert len(rows) == 5, _texts(rows)
    assert _texts(rows)[3] == ["Total", "300"]


def test_without_hrules_behavior_is_unchanged():
    # The veto is inert on unruled bands: today's (defective, documented) fusion persists —
    # the data row AND the subtotal row both absorb into the anchor, concatenating the measure
    # column ('100 200 300'), the same shape as the real report's '20,000 20,000 20,000'.
    prior, full, data, sub, nxt = suppressed_key_lines()
    band = Band((prior, full, data, sub, nxt), 0.0, 54.0)
    rows = group_wrapped(band, GRID)
    assert len(rows) == 3, _texts(rows)          # pins main's current behavior
    fused = _texts(rows)[1]
    assert fused[-1] == "100 200 300", fused


def test_genuine_wrap_in_hrule_free_gap_still_absorbs():
    # A wrapped body cell has NO hrule inside it (measured: all 19 hrule-free pairs are wraps).
    # hrules elsewhere must not disturb it.
    anchor = _line([_w("Jul", 105, 130, 0.0), _w("Fisherman", 155, 198, 0.0),
                    _w("V1", 205, 230, 0.0), _w("100", 255, 280, 0.0)], 0.0)
    wrap = _line([_w("Islands", 155, 190, 10.0)], 10.0)
    nxt = _line([_w("Aug", 105, 130, 30.0), _w("Portland", 155, 195, 30.0),
                 _w("V2", 205, 230, 30.0), _w("200", 255, 280, 30.0)], 30.0)
    hrules = (HRule(19.0, 100.0, 300.0),)       # hrule AFTER the wrap pair only
    band = Band((anchor, wrap, nxt), 0.0, 38.0, (), hrules)
    rows = group_wrapped(band, GRID)
    assert len(rows) == 2, _texts(rows)
    assert "Fisherman Islands" in " ".join(_texts(rows)[0])


def test_double_drawn_hrule_is_harmless():
    # Real borders render as two segments a fraction apart (measured: 87.0/87.2). Any of them
    # vetoing is enough; duplicates change nothing.
    prior, full, data, sub, nxt = suppressed_key_lines()
    hrules = (HRule(20.0, 100, 300), HRule(20.12, 100, 300),
              HRule(27.0, 100, 300), HRule(27.1, 100, 300))
    band = Band((prior, full, data, sub, nxt), 0.0, 54.0, (), hrules)
    assert len(group_wrapped(band, GRID)) == 5
