"""R261 fix round 1, ruling R7: a total bound only in section repair's PASS 2 reaches the document.

Measured on cbh (task-4 report § 7.1): the four tables escalate in pass 1, so their lone totals
cannot bind there (`reports[-1]` is escalated); pass 2 asserts the tables and binds all four
totals; and `compile_document` carried back only the CANDIDATE bands, so the document graph held
none. R7: adopting a candidate's table also adopts every pass-2 band whose `tab:PrintedTotal` is
`tab:totalOf` that table — keyed by the graph link, never by adjacency.

THE FIXTURE reproduces that shape synthetically, and it is measured below rather than assumed:
`multi_section_ruled_pdf(with_totals=False, strip_separators=True, lone_total_offset=30)` — two
doubled-edge CBH sections, each with its Volume sum printed ALONE 30 pt under the grid. Pass 1:
bands 0 and 2 escalate (REGION_TILING_FAILED) and the lone totals, bands 1 and 3, are ignored.
Section repair re-reads bands 0 and 2 and asserts them.

No case touches the network: the reader is a monkeypatched fake, and the isolation fixture is
`test_printed_total.py`'s (M9).
"""
import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS

from iladub.etkl import printedtotal as P

TAB = "https://w3id.org/iladub/tab#"
DEC = "https://w3id.org/iladub/dec#"
ETKL = "https://w3id.org/iladub/etkl#"
P0 = "https://example.org/etkl/doc/p0"
R2 = P0 + "/r2"


@pytest.fixture(autouse=True)
def _isolated(monkeypatch, tmp_path):
    P._PRINTED_TOTAL_CACHE.clear()
    d = tmp_path / "readings"
    d.mkdir()
    monkeypatch.setattr(P, "READINGS_DIR", d)
    for k in ("BAML_LIVE", "ILADUB_RECORD_READINGS", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    try:
        from baml_client import sync_client
    except ImportError:
        sync_client = None
    if sync_client is not None:
        def _tripwire(*a, **k):
            raise AssertionError("a printed-total test reached the live AskPrintedTotal")
        monkeypatch.setattr(sync_client.b, "AskPrintedTotal", _tripwire, raising=True)
    yield
    P._PRINTED_TOTAL_CACHE.clear()


class _Yes:
    def __init__(self):
        self.asked = []

    def ask(self, crop_png, value, listing):
        self.asked.append(value)
        return P.PrintedTotalReading(answer="yes")


class _NoClaim:
    def ask(self, crop_png, value, listing):
        return None


@pytest.fixture
def pdf(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl.fixtures import multi_section_ruled_pdf
    p = tmp_path / "sections.pdf"
    truth = multi_section_ruled_pdf(str(p), with_totals=False, strip_separators=True,
                                    lone_total_offset=30)
    return str(p), truth


def _doc(monkeypatch, path, reader):
    from iladub.etkl.document import compile_document
    monkeypatch.setattr(P, "default_reader", lambda: reader)
    return compile_document(path)


def _verdict(g, page_doc, idx):
    from iladub.etkl.document import _verdict_decision
    return _verdict_decision(g, URIRef(page_doc), idx)


def _chosen(g, d):
    return str(g.value(g.value(d, URIRef(DEC + "chosen")), RDFS.label))


def test_the_fixture_binds_nothing_in_pass_one(pdf, monkeypatch):
    """The precondition, measured: pass 1 escalates both tables and ignores both lone totals, so
    no total can bind there and the reader is never asked."""
    from iladub.etkl.compile import compile_tables
    path, _ = pdf
    reader = _Yes()
    monkeypatch.setattr(P, "default_reader", lambda: reader)
    rep = compile_tables(path, 0)
    assert [(r.verdict, r.reason) for r in rep.regions] == [
        ("escalated", "REGION_TILING_FAILED"), ("ignored", "fewer than 2 lines"),
        ("escalated", "REGION_TILING_FAILED"), ("ignored", "fewer than 2 lines")]
    assert reader.asked == []


def test_a_total_bound_only_in_pass_two_reaches_the_document(pdf, monkeypatch):
    path, _ = pdf
    reader = _Yes()
    doc = _doc(monkeypatch, path, reader)
    g = doc.graph
    assert reader.asked == ["128,904", "128,100"]           # asked in pass 2 only
    assert doc.repaired_bands == ((0, 0), (0, 2))           # candidates: unchanged
    regions = doc.pages[0].regions
    pts = sorted(g.subjects(RDF.type, URIRef(TAB + "PrintedTotal")), key=str)
    assert pts == [URIRef(f"{R2}#printedtotal1-l0"), URIRef(f"{R2}#printedtotal3-l0")]
    for pt, table_idx in zip(pts, (0, 2)):
        # keyed by the graph link: each total is tab:totalOf the table its candidate adopted
        assert g.value(pt, URIRef(TAB + "totalOf")) == regions[table_idx].table_uri
        assert len(set(g.objects(pt, URIRef(TAB + "aggregates")))) == 3

    for j in (1, 3):
        r = regions[j]
        assert (r.verdict, r.table_uri, r.tokens_asserted, r.tokens_escalated) == \
            ("asserted", None, 1, 0)
        # (1) no duplicate carriage: the pass-1 IgnoredBand of the same number is withdrawn,
        # and pass 2 minted none (its band was emptied).
        for page_doc in (P0, R2):
            assert (URIRef(f"{page_doc}#ignored{j}"), None, None) not in g
            assert (URIRef(f"{page_doc}#ignored{j}-source"), None, None) not in g
        # (2) the supersession: pass 2's `asserted` verdict supersedes pass 1's `ignored` one.
        v1, v2 = _verdict(g, P0, j), _verdict(g, R2, j)
        assert v1 is not None and v2 is not None
        assert (_chosen(g, v1), _chosen(g, v2)) == ("ignored", "asserted")
        assert (v2, URIRef(DEC + "supersedes"), v1) in g
        # the decision that produced the total rode in with the reading log
        d = next(g.subjects(URIRef(DEC + "produced"), pts[(j - 1) // 2]))
        assert str(g.value(d, RDFS.label)) == "printed_total" and _chosen(g, d) == "total"

    # (3) booked once at document scope: the page's score operands ARE the per-band ledger, and
    # each lone total's single word is booked asserted once, by its band, and carried once.
    page = doc.pages[0]
    assert page.asserted == sum(r.tokens_asserted for r in regions)
    assert page.escalated == sum(r.tokens_escalated for r in regions)
    carried = [o for o in g.objects(None, URIRef(TAB + "cellText"))
               if str(o) in ("128,904", "128,100")]
    assert sorted(map(str, carried)) == ["128,100", "128,904"]
    assert not [o for o in g.objects(None, URIRef(ETKL + "bandText"))
                if str(o) in ("128,904", "128,100")]


def test_the_denominator_moves_by_exactly_the_two_bound_words(pdf, monkeypatch):
    """The control and the measurement: with no claim, nothing binds, both lone totals stay
    ignored and carried as IgnoredBands, and the document denominator is the before figure. With
    a yes, it grows by exactly the two words now booked asserted."""
    path, _ = pdf
    before = _doc(monkeypatch, path, _NoClaim())
    assert list(before.graph.subjects(RDF.type, URIRef(TAB + "PrintedTotal"))) == []
    for j in (1, 3):
        assert before.pages[0].regions[j].verdict == "ignored"
        assert (URIRef(f"{P0}#ignored{j}"), None, None) in before.graph
    after = _doc(monkeypatch, path, _Yes())
    b, a = before.pages[0], after.pages[0]
    assert (a.asserted - b.asserted, a.escalated - b.escalated) == (2, 0)


# --------------------------------------------------------------------------------------- R7
# REFUSAL: "pass 1 asserted a TABLE in this band" (document.py's R7 block, `if
# pages[p].regions[j].table_uri is not None or any(graph.subjects(None, ign)): ... continue`,
# first disjunct). Final review item 5.
#
# CONSTRUCTED, not assumed: a band whose SOLE content, read on its own, would be band 1's lone
# total (R7's usual shape) is instead given extra ruled content directly below it, tight enough
# that `detect_bands` keeps it ONE band. `_bind_printed_totals` runs only against an ASSERTED
# previous band (compile.py:1027-1029), so in PASS 1 — where section 0's table ESCALATES
# (REGION_TILING_FAILED, same as `pdf` above) — nothing tries to bind band 1's lone number, and
# the WHOLE band (lone total + the extra rows) tiles as its OWN small table on its own merits,
# asserting with a `table_uri`. In PASS 2, section 0's table is repaired and ASSERTS, so
# `_bind_printed_totals` now runs FIRST for band 1 (compile.py:1140-1141, before classify), finds
# the lone total, matches the arithmetic, and (with a yes reader) carves it out as a
# `tab:PrintedTotal` — but `document.py`'s R7 adoption must refuse to carry that pass-2 reading
# back, because pass 1's band 1 is not a candidate (its own table asserted there, not escalated)
# and withdrawing it would destroy that table.
def _dirty_total_band_pdf(path: str) -> None:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from tests.etkl.fixtures import _draw_section
    H = letter[1]

    def y(top):
        return H - top

    cols = [72, 172, 292, 392, 492]
    rows0 = [("10097", "15:01", "Brahman", "30,000"), ("10076", "14:38", "CBH", "50,000"),
             ("10118", "11:28", "Cargill", "48,904")]
    rows1 = [("20011", "09:15", "Viterra", "40,000"), ("20032", "10:47", "CBH", "35,500"),
             ("20050", "13:02", "GrainCorp", "52,600")]
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Courier", 9)
    STEP = 280.0
    grid_bot0 = _draw_section(c, H, 0, "GERALDTON", "BERTH MAY BE UNAVAILABLE 2000HRS", rows0,
                              cols, doubled_edges=True, extra_hrule_offsets=(22,))
    vol_sum0 = sum(int(r[3].replace(",", "")) for r in rows0)
    c.drawString(cols[3] + 4, y(grid_bot0 + 30), f"{vol_sum0:,}")
    # the EXTRA ruled content, tight pitch (18pt) below the lone total -- same band, and
    # enough for `classify` to tile band 1 as its own RECORD_TABLE (2 columns, 1 header row).
    c.drawString(cols[0] + 4, y(grid_bot0 + 48), "Qty")
    c.drawString(cols[1] + 4, y(grid_bot0 + 48), "Unit")
    c.drawString(cols[0] + 4, y(grid_bot0 + 66), "999")
    c.drawString(cols[1] + 4, y(grid_bot0 + 66), "APW")
    grid_bot1 = _draw_section(c, H, STEP, "KWINANA", "VESSEL DELAYED PENDING SURVEY", rows1,
                              cols, doubled_edges=True, extra_hrule_offsets=(22,))
    vol_sum1 = sum(int(r[3].replace(",", "")) for r in rows1)
    c.drawString(cols[3] + 4, y(grid_bot1 + 30), f"{vol_sum1:,}")
    c.save()


@pytest.fixture
def dirty_pdf(tmp_path):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    p = tmp_path / "dirty.pdf"
    _dirty_total_band_pdf(str(p))
    return str(p)


def test_the_dirty_fixture_asserts_band_one_as_its_own_table_in_pass_one(dirty_pdf):
    """The precondition, measured: band 0 escalates (REGION_TILING_FAILED, a repair candidate
    exactly as `pdf`'s band 0 does) and band 1 — the lone total PLUS the extra ruled rows —
    tiles and ASSERTS on its own, with a `table_uri`, because nothing tries to bind its total in
    pass 1 (band 0 never asserted)."""
    from iladub.etkl.compile import compile_tables
    rep = compile_tables(dirty_pdf, 0)
    regions = rep.regions
    assert (regions[0].verdict, regions[0].reason) == ("escalated", "REGION_TILING_FAILED")
    assert regions[1].verdict == "asserted" and regions[1].table_uri is not None
    assert (regions[2].verdict, regions[2].reason) == ("escalated", "REGION_TILING_FAILED")


def test_the_r7_refusal_keeps_band_one_a_table_and_mints_no_printed_total(dirty_pdf, monkeypatch):
    """The refusal itself: section repair adopts band 0's table (candidate), and pass 2 binds
    band 1's lone total against it — but band 1 is not a candidate (`pages[p].regions[1]`
    already carries a `table_uri` from pass 1), so document.py's R7 block refuses to adopt it,
    with a note, and band 1's pass-1 table survives UNTOUCHED: no `tab:PrintedTotal` is `totalOf`
    band 0's table, no `dec:supersedes` edge lands on band 1's verdict, and its own `table_uri`
    is unchanged. Band 3 (section 1's OWN lone total, which has no interfering content) binds
    normally — the control that shows the refusal is specific to band 1, not a global stall."""
    doc = _doc(monkeypatch, dirty_pdf, _Yes())
    assert doc.repaired_bands == ((0, 0), (0, 2))        # only the two escalated tables repair
    assert any("band 1: pass-2 printed total not adopted" in n for n in doc.notes), doc.notes
    g = doc.graph
    r0 = doc.pages[0].regions[0]
    pts = list(g.subjects(RDF.type, URIRef(TAB + "PrintedTotal")))
    assert pts and all(g.value(pt, URIRef(TAB + "totalOf")) != r0.table_uri for pt in pts)
    r1 = doc.pages[0].regions[1]
    assert r1.verdict == "asserted" and r1.table_uri is not None
    v1 = _verdict(g, P0, 1)
    assert v1 is not None and _chosen(g, v1) == "asserted"
    assert not list(g.subjects(URIRef(DEC + "supersedes"), v1))
    # band 1's own IgnoredBand was never minted (it asserted a table in pass 1) and the pass-2
    # reading log for band 1 never rode in either.
    assert (URIRef(f"{P0}#ignored1"), None, None) not in g
    assert not list(g.subjects(None, URIRef(f"{R2}#region1")))
