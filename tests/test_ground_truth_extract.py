import hashlib
import importlib.util
import pathlib

import pytest

from iladub.truth import TableSpanMismatch, TruthMarkupError, TruthRow

_spec = importlib.util.spec_from_file_location(
    "ground_truth_extract",
    pathlib.Path(__file__).resolve().parent.parent / "scripts" / "ground_truth_extract.py",
)
gte = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gte)

DECOY = "<table><tr><td id='t1h1c1'>decoy</td></tr></table>"


def _table(bad_header="t1h2c1", top_extra=""):
    return f"""<table>
<thead>
<tr><td rowspan="2" id="t1h1c1"><p><span>Item</span></p></td>
<td colspan="2" id="t1h1c2"><p><span>Top{top_extra}</span></p></td></tr>
<tr><td id="t1h2c1"><p><span>Week ended</span><br><span>Jan 1, 2025</span></p></td>
<td id="t1h2c2"><p><span>Change</span></p></td></tr>
</thead>
<tbody>
<tr><td id="t1r1c1" header="t1h1c1 "><p><span>Label</span><span style="vertical-align:super">1</span></p></td>
<td id="t1r1c2" header="t1r1c1 t1h1c2 {bad_header} "><p><span>&#xa0;</span><span>1,000</span></p></td>
<td id="t1r1c3" header="t1r1c1 t1h1c2 t1h2c2 "><p><span>-</span><span>&#xa0;&#xa0; </span><span>20</span></p></td></tr>
<tr><td id="t1r2c1" header="t1h1c1 "><p><span>Others</span></p></td>
<td id="t1r2c2" header="t1r1c1 t1h1c2 t1h2c1 "><p><span>5</span></p></td>
<td id="t1r2c3" header="t1r1c1 t1h1c2 t1h2c2 "><p><span>&#xa0;</span></p></td></tr>
<tr><td id="t1r3c1" header="t1h1c1 "><p><span>&#xa0;</span></p></td>
<td id="t1r3c2" header="t1r1c1 t1h1c2 t1h2c1 "><p><span>&#xa0;</span></p></td></tr>
<tr><td id="t1r4c1" header="t1h1c1 "><p><span>Others</span></p></td>
<td id="t1r4c2" header="t1r1c1 t1h1c2 t1h2c1 "><p><span>7</span></p></td></tr>
</tbody>
</table>"""


def _page(table):
    return ("<html><body>" + DECOY + "\n" + table + "<p>tail</p></body></html>").encode()


def _sha(table):
    return hashlib.sha256(table.encode()).hexdigest()


def test_fixture_extracts_exact_rows():
    t = _table()
    rows = gte.extract_table(_page(t), 2, _sha(t))
    wk = "Top › Week ended Jan 1, 2025"
    assert rows == [
        TruthRow("Label", "Label1", 0, wk, "1,000"),
        TruthRow("Label", "Label1", 0, "Top › Change", "-20"),
        TruthRow("Others", "Others", 0, wk, "5"),
        TruthRow("Others", "Others", 1, wk, "7"),
    ]


def test_span_hash_mismatch_refused():
    t = _table()
    with pytest.raises(TableSpanMismatch):
        gte.extract_table(_page(t), 2, "0" * 64)


def test_unknown_header_id_refused():
    t = _table(bad_header="t1h9c9")
    with pytest.raises(TruthMarkupError):
        gte.extract_table(_page(t), 2, _sha(t))


def test_header_text_containing_separator_refused():
    t = _table(top_extra=" › x")
    with pytest.raises(TruthMarkupError):
        gte.extract_table(_page(t), 2, _sha(t))


# --- SEC mode (spec 2026-10-29 § 6.4, § 12.4 item 1): colspan intervals, not header ids. ---

SEC_FIXTURE = pathlib.Path(__file__).resolve().parent / "data" / "sec-colspan-table.html"
NINE = "Nine Months Ended"
Q26 = f"{NINE} › June 27, 2026"
Q25 = f"{NINE} › June 28, 2025"


def _sec(ordinal=1):
    html = SEC_FIXTURE.read_bytes()
    return gte.extract_sec_table(html, ordinal, hashlib.sha256(gte._span(html, ordinal)).hexdigest())


def test_sec_fixture_extracts_exact_rows():
    assert _sec() == [
        TruthRow("Cash, beginning balances", "Cash, beginning balances", 0, Q26, "35,934"),
        TruthRow("Cash, beginning balances", "Cash, beginning balances", 0, Q25, "29,943"),
        TruthRow("Other", "Other", 0, Q26, "(2,037)"),
        TruthRow("Other", "Other", 0, Q25, "(1,748)"),
        TruthRow("Proceeds from issuance of term debt, net",
                 "Proceeds from issuance of term debt, net", 0, Q25, "4,481"),
        TruthRow("Other", "Other", 1, Q26, "(1,234)"),
        TruthRow("Other", "Other", 1, Q25, "5"),
    ]


def test_sec_colspan_intervals_give_two_level_paths():
    assert {r.col_path for r in _sec()} == {Q26, Q25}


def test_sec_dollar_glyph_dropped_neighbour_kept():
    rows = [r for r in _sec() if r.row_label == "Cash, beginning balances"]
    assert [r.value for r in rows] == ["35,934", "29,943"]
    assert all(r.value != "$" for r in _sec())


def test_sec_br_reads_as_space():
    assert any(r.col_path.endswith("June 27, 2026") for r in _sec())


def test_sec_nil_dash_is_no_cell_and_parenthesised_value_kept_verbatim():
    proceeds = [r for r in _sec() if r.row_label.startswith("Proceeds")]
    assert [(r.col_path, r.value) for r in proceeds] == [(Q25, "4,481")]
    assert TruthRow("Other", "Other", 1, Q26, "(1,234)") in _sec()


def test_sec_value_cell_outside_every_header_interval_refused():
    with pytest.raises(TruthMarkupError):
        _sec(ordinal=2)


def test_sec_span_hash_mismatch_refused():
    with pytest.raises(TableSpanMismatch):
        gte.extract_sec_table(SEC_FIXTURE.read_bytes(), 1, "0" * 64)
