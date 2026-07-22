from dataclasses import replace
from iladub.etkl.headers import HeaderNode, resolve_narrow_flanks
from iladub.etkl.grid import LeafGrid


def test_ambiguous_flank_records_the_tied_column():
    # boundaries [0,100,200,300,400,440]: col4 width 40 < 0.5*median_pitch(100)=50, ink-unreached
    grid = LeafGrid(boundaries=(0.0, 100.0, 200.0, 300.0, 400.0, 440.0), ncols=5,
                    pitch=100.0, confidence=1.0)
    node = HeaderNode(level=0, covers=(1, 2, 3, 4), text="Span", parent=None, center_x=250.0)
    ink = [(1, 2, 3)]                      # node's ink reaches cols 1..3 only; col4 is the flank
    out = resolve_narrow_flanks([node], grid, ink)
    assert out[0].ambiguous is True
    assert out[0].ambiguous_flank == 4


def test_ambiguous_flank_defaults_none_and_field_present():
    n = HeaderNode(0, (1,), "x", None)
    assert n.ambiguous_flank is None
    assert replace(n, ambiguous_flank=3).ambiguous_flank == 3
