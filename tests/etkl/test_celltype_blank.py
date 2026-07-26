"""tab:Blank — genuinely-missing cells (empty / '(blank)' / lone '-') type as Blank, not Text.
A minimal, self-documenting missing-value marker set (loop A)."""
from iladub.etkl.celltype import _cell_datatype
from iladub.etkl.holon import TAB


def test_missing_cells_are_blank():
    for t in ("", "   ", "(blank)", "(BLANK)", "-"):
        assert _cell_datatype(t) == TAB.Blank, t


def test_non_missing_cells_unchanged():
    assert _cell_datatype("7") == TAB.Numeric
    assert _cell_datatype("-5") == TAB.Numeric          # a signed number, not blank
    assert _cell_datatype("0") == TAB.Numeric
    assert _cell_datatype("2020-01-02") == TAB.Date
    assert _cell_datatype("$5") == TAB.Currency
    assert _cell_datatype("Alice") == TAB.Text
    assert _cell_datatype("N/A") == TAB.Text            # ambiguous marker -> NOT blank (stays Text)
