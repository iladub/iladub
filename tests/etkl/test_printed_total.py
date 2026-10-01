"""R261 Task 4: the printed-total worker and the binding (spec §§ 2, 3.2, 5.2).

A lone number printed beneath a table binds as its `tab:PrintedTotal` only under the CONJUNCTION
(ruling R-a): exact `Decimal` arithmetic over one of the table's columns holds AND a reader answers
`yes`. TABLE LEVEL ONLY — the total-of-totals question was refuted by P3 (controller ruling R4), so
a total-of-totals line is never bound and stays in its band.

Fixtures (`tests/etkl/fixtures.py`, band layout measured there):
  `printed_total_pdf` — band 0 table A (Tonnes = 5,100); band 1 `5,100` + a prose Note; band 2
  table B (Tonnes = 2,700); band 3 `2,700` alone; band 4 `7,800` (= 5,100 + 2,700) alone.
  `percent_total_pdf` — a Share column 25% / 35% / 40% and `100%` alone beneath it.

No case touches the network: the isolation fixture below is `test_header_lines.py`'s (M9), and every
compile reads its reader through a monkeypatched `printedtotal.default_reader`.
"""
import json

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS

from iladub.etkl import printedtotal as P

TAB_NS = "https://w3id.org/iladub/tab#"
DEC_NS = "https://w3id.org/iladub/dec#"
DOC = "https://example.org/etkl/doc"


def T(local):
    return URIRef(TAB_NS + local)


def D(local):
    return URIRef(DEC_NS + local)


@pytest.fixture(autouse=True)
def _fresh_cache_and_readings(monkeypatch, tmp_path):
    """Copied from `test_header_lines.py` (M9): the live cache is module-global, so it is cleared;
    every test reads recordings from its own empty directory; and NO CASE MAY REACH THE MODEL —
    the key is removed and the generated function is a tripwire."""
    P._PRINTED_TOTAL_CACHE.clear()
    d = tmp_path / "readings"
    d.mkdir()
    monkeypatch.setattr(P, "READINGS_DIR", d)
    monkeypatch.delenv("BAML_LIVE", raising=False)
    monkeypatch.delenv("ILADUB_RECORD_READINGS", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        from baml_client import sync_client
    except ImportError:
        sync_client = None
    if sync_client is not None:
        def _tripwire(*a, **k):
            raise AssertionError("a printed-total test reached the live AskPrintedTotal")
        monkeypatch.setattr(sync_client.b, "AskPrintedTotal", _tripwire, raising=True)
    yield d
    P._PRINTED_TOTAL_CACHE.clear()


class _Reader:
    """Answers by printed value; records every value it was asked about. A value absent from
    `answers` gets `default` (None = no claim)."""

    def __init__(self, answers=None, default=None):
        self.answers = dict(answers or {})
        self.default = default
        self.asked: list[str] = []

    def ask(self, crop_png, value, listing):
        self.asked.append(value)
        assert crop_png[:8] == b"\x89PNG\r\n\x1a\n", "the reader must be handed the D7 crop"
        a = self.answers.get(value, self.default)
        return None if a is None else P.PrintedTotalReading(answer=a)


def _pdf(tmp_path, builder, **kw):
    pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
    from tests.etkl import fixtures
    p = tmp_path / "pt.pdf"
    getattr(fixtures, builder)(str(p), **kw)
    return str(p)


def _compile(monkeypatch, pdf, reader, **kw):
    from iladub.etkl.compile import compile_tables
    monkeypatch.setattr(P, "default_reader", lambda: reader)
    return compile_tables(pdf, 0, **kw)


def _printed_totals(g):
    return sorted(g.subjects(RDF.type, T("PrintedTotal")), key=str)


def _decisions(g, idx, label):
    """The band's decisions labelled `label`, as (decision, chosen option label)."""
    prefix = f"{DOC}#region{idx}-d"
    out = []
    for d in g.subjects(RDF.type, D("DecisionHolon")):
        if str(d).startswith(prefix) and (d, RDFS.label, Literal(label)) in g:
            out.append((d, str(g.value(g.value(d, D("chosen")), RDFS.label))))
    return out


# ------------------------------------------------------------------ the reading and its key

def test_the_reading_is_a_closed_enum_with_no_other_field():
    assert P.PrintedTotalReading(answer="yes").answer == "yes"
    with pytest.raises(ValueError):
        P.PrintedTotalReading(answer="probably")
    import dataclasses
    assert [f.name for f in dataclasses.fields(P.PrintedTotalReading)] == ["answer"]


def test_the_key_is_text_facts_only_and_namespaced_by_the_question():
    k = P.question_key("5,100", "L0: a\nL1: 5,100")
    assert P.question_key("5,100", "L0: a\nL1: 5,100") == k
    assert P.question_key("5,101", "L0: a\nL1: 5,100") != k
    assert P.question_key("5,100", "L0: b\nL1: 5,100") != k
    import hashlib
    assert k != hashlib.sha256("5,100\nL0: a\nL1: 5,100".encode()).hexdigest()
    import inspect
    assert list(inspect.signature(P.question_key).parameters) == ["value", "listing"]


def _band(texts):
    """A minimal Band whose lines are one-word lines of `texts`, in order — for `listing_of`
    tests that need a multi-line band without a full PDF compile."""
    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Word
    lines = tuple(Line((Word(t, 10.0, 60.0, 10.0 * i, 10.0 * i + 8.0),), 10.0 * i, 10.0 * i + 8.0)
                 for i, t in enumerate(texts))
    return Band(lines, 0.0, 10.0 * len(texts))


def test_listing_includes_the_candidates_own_prior_band_lines():
    """Final review finding, item 2: the crop spans `table_band.top` through `line.bottom` (D7),
    so it shows the candidate's OWN band's lines before the candidate too, when the candidate sits
    at `line_no > 0` in its own band — `listing_of` must include them, and the key must move when
    one of them changes."""
    table_band = _band(["Header"])
    band = _band(["Note: subject to change", "2,700"])
    line_no = 1
    line = band.lines[line_no]
    listing = P.listing_of(table_band, band, line_no, line)
    assert listing.splitlines() == ["L0: Header", "L1: Note: subject to change", "L2: 2,700"]
    key = P.question_key("2,700", listing)

    other_band = _band(["Note: SUBJECT TO CHANGE", "2,700"])
    other_listing = P.listing_of(table_band, other_band, line_no, other_band.lines[line_no])
    assert P.question_key("2,700", other_listing) != key


def test_listing_at_line_zero_is_unchanged_by_the_fix():
    """The only case the corpus has recorded (cbh's 4 printed-total candidates are all at line
    index 0, per the final review): `band.lines[:0]` is `()`, so the listing — and therefore the
    key — is byte-identical to the pre-fix listing (`table_band.lines + [line]`). This is the
    offline proof the final review asked for in place of a corpus recompile."""
    table_band = _band(["Site Tonnes Grade", "Alpha 1,200 APW"])
    band = _band(["2,700"])
    line_no = 0
    line = band.lines[line_no]
    new_listing = P.listing_of(table_band, band, line_no, line)
    pre_fix_listing = "\n".join(f"L{k}: {P._line_text(ln)}"
                                for k, ln in enumerate(list(table_band.lines) + [line]))
    assert new_listing == pre_fix_listing


def test_a_recorded_reading_replays_and_an_out_of_set_one_is_no_claim(
        tmp_path, _fresh_cache_and_readings):
    pdf = _pdf(tmp_path, "printed_total_pdf")
    from iladub.etkl.compile import page_bands
    bands = page_bands(pdf, 0)
    table, band, line_no = bands[2], bands[3], 0
    line = band.lines[line_no]
    key = P.question_key("2,700", P.listing_of(table, band, line_no, line))
    path = _fresh_cache_and_readings / f"{key}.json"
    path.write_text(json.dumps({"answer": "yes"}), encoding="utf-8")
    got = P.ask_printed_total(pdf, 0, table, band, line_no, line, "2,700", P.default_reader())
    assert got == P.PrintedTotalReading(answer="yes")
    path.write_text(json.dumps({"answer": "probably"}), encoding="utf-8")
    assert P.ask_printed_total(pdf, 0, table, band, line_no, line, "2,700",
                               P.default_reader()) is None


def test_no_recording_and_not_live_is_no_claim_and_never_builds_the_live_reader(
        tmp_path, monkeypatch):
    pdf = _pdf(tmp_path, "printed_total_pdf")
    from iladub.etkl.compile import page_bands
    bands = page_bands(pdf, 0)

    def _boom(*a, **k):
        raise AssertionError("the live reader was constructed")
    monkeypatch.setattr(P, "BamlPrintedTotalReader", _boom)
    assert P.ask_printed_total(pdf, 0, bands[2], bands[3], 0, bands[3].lines[0], "2,700",
                               P.default_reader()) is None


# ------------------------------------------------------------------ the conjunction (spec § 5.2)

@pytest.mark.parametrize("answer, printed, bound", [
    ("yes", "2,700", True),            # yes + holds  -> bound
    ("yes", "2,701", False),           # yes + fails  -> NOT bound: the worker cannot bind alone
    ("no", "2,700", False),            # no + holds   -> NOT bound: arithmetic cannot bind alone
    ("cannot_tell", "2,700", False),   # cannot_tell + holds -> not bound
])
def test_the_conjunction_binds_band_3(tmp_path, monkeypatch, answer, printed, bound):
    pdf = _pdf(tmp_path, "printed_total_pdf", second_total=printed)
    reader = _Reader({printed: answer})
    rep = _compile(monkeypatch, pdf, reader)
    g = rep.graph
    pt = URIRef(f"{DOC}#printedtotal3-l0")
    r3 = rep.regions[3]
    holds = printed == "2,700"
    # Arithmetic first: the reader is asked about band 3's number only when the sum holds.
    assert (printed in reader.asked) is holds
    if bound:
        assert (pt, RDF.type, T("PrintedTotal")) in g
        assert g.value(pt, T("cellText")) == Literal("2,700")
        assert g.value(pt, T("totalOf")) == URIRef(f"{DOC}#table2")
        ops = set(g.objects(pt, T("aggregates")))
        assert len(ops) == 2
        assert {str(g.value(o, T("cellText"))) for o in ops} == {"2,000", "700"}
        assert _decisions(g, 3, "printed_total") == [(_decisions(g, 3, "printed_total")[0][0],
                                                      "total")]
        assert (r3.verdict, r3.table_uri, r3.cells, r3.tokens_asserted, r3.tokens_escalated) \
            == ("asserted", None, 0, 1, 0)
    else:
        assert (pt, None, None) not in g
        assert not [p for p in _printed_totals(g) if "#printedtotal3" in str(p)]
        # the band is read exactly as today: a lone line, ignored
        assert (r3.verdict, r3.reason) == ("ignored", "fewer than 2 lines")
        chosen = [c for _, c in _decisions(g, 3, "printed_total")]
        assert chosen == (["not_total"] if holds else [])


def test_no_claim_records_nothing_and_binds_nothing(tmp_path, monkeypatch):
    """Ruling R3: a reader returning None is not a decision — no `printed_total` is recorded."""
    pdf = _pdf(tmp_path, "printed_total_pdf")
    reader = _Reader(default=None)
    rep = _compile(monkeypatch, pdf, reader)
    assert reader.asked == ["5,100", "2,700"]        # asked on both matches ...
    assert _printed_totals(rep.graph) == []            # ... bound neither
    for idx in range(len(rep.regions)):
        assert _decisions(rep.graph, idx, "printed_total") == []
    assert [r.verdict for r in rep.regions] == \
        ["asserted", "escalated", "asserted", "ignored", "ignored"]


# ------------------------------------------------------------------ the carve

def test_the_carved_remainder_is_classified_alone(tmp_path, monkeypatch):
    pdf = _pdf(tmp_path, "printed_total_pdf")
    rep = _compile(monkeypatch, pdf, _Reader(default="yes"))
    g = rep.graph
    assert (URIRef(f"{DOC}#printedtotal1-l0"), RDF.type, T("PrintedTotal")) in g
    r1 = rep.regions[1]
    # Uncarved, band 1 escalates 17 words (control: the no-claim test). Carved, the Note is read
    # on its own: 16 words, and the bound total is booked asserted to the same band.
    assert (r1.verdict, r1.reason, r1.tokens_asserted, r1.tokens_escalated) == \
        ("escalated", "KIND_NOT_SUPPORTED", 1, 16)
    assert "5,100" not in r1.ascii and "Note:" in r1.ascii
    cand = URIRef(f"{DOC}#region1")
    texts = [str(o) for o in g.objects(cand, None) if isinstance(o, Literal)]
    assert texts and not any("5,100" in t for t in texts)


def test_an_empty_remainder_mints_no_band_node_and_still_appends_one_report(
        tmp_path, monkeypatch):
    pdf = _pdf(tmp_path, "printed_total_pdf")
    rep = _compile(monkeypatch, pdf, _Reader(default="yes"))
    from iladub.etkl.compile import page_bands
    g = rep.graph
    assert len(rep.regions) == len(page_bands(pdf, 0))      # one report per band (M2)
    r3 = rep.regions[3]
    assert (r3.verdict, r3.table_uri, r3.cells) == ("asserted", None, 0)
    # No band node: band 3's only subjects are its reading log (`#region3-…`) and the
    # PrintedTotal it produced — no `#region3`, no `#ignored3`, no table of any kind.
    band3 = {str(s) for s in g.subjects()
             if str(s).startswith(f"{DOC}#") and str(s)[len(DOC) + 1:].lstrip(
                 "abcdefghijklmnopqrstuvwxyz").startswith("3")}
    assert band3 and all(s.startswith((f"{DOC}#region3-", f"{DOC}#printedtotal3-"))
                         for s in band3), band3
    assert (URIRef(f"{DOC}#region3"), None, None) not in g
    assert (URIRef(f"{DOC}#ignored3"), None, None) not in g
    # exactly one verdict, as on every band
    assert [c for _, c in _decisions(g, 3, "verdict")] == ["asserted"]


def test_every_uncarved_word_is_booked_exactly_once(tmp_path, monkeypatch):
    """MEASURE (c) as a test: for every band of the UNCARVED page, its words land in exactly one
    bucket — asserted, escalated, or (ignored) the IgnoredBand's carried text. The sum identity
    `asserted == sum(tokens_asserted)` holds by the differencing, and is checked as well."""
    pdf = _pdf(tmp_path, "printed_total_pdf")
    rep = _compile(monkeypatch, pdf, _Reader(default="yes"))
    from iladub.etkl.compile import page_bands
    bands = page_bands(pdf, 0)
    g = rep.graph
    assert len(rep.regions) == len(bands)                    # zip must not truncate
    for i, (b, r) in enumerate(zip(bands, rep.regions)):
        words = sum(len(ln.words) for ln in b.lines)
        ignored = g.value(URIRef(f"{DOC}#ignored{i}"), URIRef("https://w3id.org/iladub/etkl#bandText"))
        ignored_words = len(str(ignored).split()) if ignored is not None else 0
        assert r.tokens_asserted + r.tokens_escalated + ignored_words == words, (i, r)
    assert rep.asserted == sum(r.tokens_asserted for r in rep.regions)
    assert rep.escalated == sum(r.tokens_escalated for r in rep.regions)
    assert (rep.regions[1].tokens_asserted, rep.regions[3].tokens_asserted) == (1, 1)


# ------------------------------------------------------------------ total-of-totals (ruling R4)

def test_a_total_of_totals_line_is_never_bound_and_stays_in_its_band(tmp_path, monkeypatch):
    """Review Focus 3 + R4: band 4's `7,800` sums the two bound totals exactly, and sits directly
    after a bound total whose report is `asserted` with `table_uri` None (D6). There is no table
    level for it and no total-of-totals level at all, so the reader — who would say yes — is never
    asked, and the line is read in its own band exactly as today."""
    pdf = _pdf(tmp_path, "printed_total_pdf")
    reader = _Reader(default="yes")
    rep = _compile(monkeypatch, pdf, reader)
    g = rep.graph
    assert len(_printed_totals(g)) == 2                      # both table totals bound ...
    assert "7,800" not in reader.asked                       # ... the grand total never asked
    assert not [p for p in _printed_totals(g) if "#printedtotal4" in str(p)]
    assert _decisions(g, 4, "printed_total") == []
    r4 = rep.regions[4]
    assert (r4.verdict, r4.reason) == ("ignored", "fewer than 2 lines")
    text = g.value(URIRef(f"{DOC}#ignored4"), URIRef("https://w3id.org/iladub/etkl#bandText"))
    assert str(text) == "7,800"


# ------------------------------------------------------------------ Review Focus 4: a percentage

@pytest.mark.parametrize("answer, bound", [("yes", True), ("no", False)])
def test_a_percentage_total_is_decided_by_the_conjunction_not_the_parse(
        tmp_path, monkeypatch, answer, bound):
    """M6 drops the `%`, so `100%` sums 25% + 35% + 40% exactly either way; only the reader's
    answer differs between the two cases, and only it decides."""
    pdf = _pdf(tmp_path, "percent_total_pdf")
    reader = _Reader({"100%": answer})
    rep = _compile(monkeypatch, pdf, reader)
    assert reader.asked == ["100%"]
    pts = _printed_totals(rep.graph)
    assert bool(pts) is bound
    if bound:
        assert rep.graph.value(pts[0], T("cellText")) == Literal("100%")


# ------------------------------------------------------------------ Review Focus 5 + D8: donation

def test_a_bound_line_is_never_offered_for_donation_and_the_remainder_is_what_is_offered(
        tmp_path, monkeypatch):
    """Review Focus 5: binding runs before the lone-line donation hook, so band 3 (bound, empty)
    is never offered; band 4 (a lone line nothing bound) is — the spy's control. D8: band 1 with a
    ONE-line Note carves to a one-line remainder, and `offer_single_line` reads `bands[idx]`
    directly, so it must see the remainder, not the uncarved two-line band (which its own guard
    would refuse before asking anything)."""
    from iladub.etkl import donation
    seen: dict[int, list[str]] = {}

    def _spy(bands, idx, evidence, page_number):
        seen[idx] = [" ".join(w.text for w in ln.words) for ln in bands[idx].lines]
        return None
    monkeypatch.setattr(donation, "offer_single_line", _spy)
    pdf = _pdf(tmp_path, "printed_total_pdf", note_lines=1)
    rep = _compile(monkeypatch, pdf, _Reader(default="yes"))
    assert len(_printed_totals(rep.graph)) == 2
    assert 3 not in seen                                     # bound: never offered
    assert seen.get(4) == ["7,800"]                          # control: the spy is live
    assert seen.get(1) == ["Note: tonnages are estimates as at the date shown"]


# ------------------------------------------------------------------ the membrane

def test_the_graph_conforms_under_the_production_membrane_and_the_shape_is_live(
        tmp_path, monkeypatch):
    """The compile ran with `validate_shapes=True` (the default) and did not raise. The membrane
    is also run explicitly, then twice more with a defect, to show `tab:PrintedTotalShape` and
    `tab:WrappedCellShape` both bind the emitted node under the PRODUCTION membrane (subclass
    closure, M10): no cellText refuses on PrintedTotalShape; an empty cellText beside a box
    refuses on WrappedCellShape (the Task 2 review's carried check)."""
    from iladub.etkl.compile import _validate
    pdf = _pdf(tmp_path, "printed_total_pdf")
    rep = _compile(monkeypatch, pdf, _Reader(default="yes"))
    g = rep.graph
    assert len(_printed_totals(g)) == 2
    ok, text, _ = _validate(g)
    assert ok, text
    pt = URIRef(f"{DOC}#printedtotal3-l0")

    g1 = g.__class__(); g1 += g
    g1.remove((pt, T("cellText"), None))
    ok, text, legs = _validate(g1)
    assert not ok and "tab" in legs and "printed total must carry exactly one cellText" in text

    g2 = g.__class__(); g2 += g
    g2.set((pt, T("cellText"), Literal("")))
    ok, text, legs = _validate(g2)
    assert not ok and "tab" in legs
    assert "non-empty cellText or non-empty unshownText (drop-continuation guard)" in text
