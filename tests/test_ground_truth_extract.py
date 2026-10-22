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
