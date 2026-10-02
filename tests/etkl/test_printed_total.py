"""R261 Task 4: the printed-total worker and the binding (spec §§ 2, 3.2, 5.2).

A lone number printed beneath a table binds as its `tab:PrintedTotal` only under the CONJUNCTION
(ruling R-a): exact `Decimal` arithmetic over one of the table's columns holds AND a reader answers
`yes`. R261 loop (b) (`docs/superpowers/specs/2026-10-02-r261-grand-total-design.md` §§ 2, 6.2) adds
the TOTALS LEVEL beside it: a lone number binds as a grand total — a `tab:PrintedTotal` with no
`tab:totalOf`, aggregating the page's table-level PrintedTotals — only when their exact sum equals it
(`totals.match_totals`, the whole set, at least 2, R-f) AND `AskTotalRole` answers
`total_of_totals`. The table-level wording P3 refuted (ruling R4) is not reused; the totals level
asks its own question (`totalrole.py`), and with no role reading the grand total stays in its band.

Fixtures (`tests/etkl/fixtures.py`, band layout measured there):
  `printed_total_pdf` — band 0 table A (Tonnes = 5,100); band 1 `5,100` + a prose Note; band 2
  table B (Tonnes = 2,700); band 3 `2,700` alone; band 4 `7,800` (= 5,100 + 2,700) alone. Its
  loop (b) parameters (`grand_note_lines`, `grand_gap`, `after_grand`) are measured there too.
  `percent_total_pdf` — a Share column 25% / 35% / 40% and `100%` alone beneath it.

No case touches the network: the isolation fixture below is `test_header_lines.py`'s (M9), applied
to BOTH reader stacks, and every compile reads its readers through a monkeypatched
`printedtotal.default_reader` (and, for the totals level, `totalrole.default_reader`).
"""
import json

import pytest
from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS

from iladub.etkl import printedtotal as P
from iladub.etkl import totalrole as R

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
    R._TOTAL_ROLE_CACHE.clear()
    d = tmp_path / "readings"
    d.mkdir()
    monkeypatch.setattr(P, "READINGS_DIR", d)
    role_dir = tmp_path / "role_readings"
    role_dir.mkdir()
    monkeypatch.setattr(R, "READINGS_DIR", role_dir)
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

        def _role_tripwire(*a, **k):
            raise AssertionError("a printed-total test reached the live AskTotalRole")
        monkeypatch.setattr(sync_client.b, "AskTotalRole", _role_tripwire, raising=True)
    yield d
    P._PRINTED_TOTAL_CACHE.clear()
    R._TOTAL_ROLE_CACHE.clear()


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


# ------------------------------------------------------------------ the totals level, no reading

def test_with_no_role_reading_the_grand_total_is_not_bound_and_stays_in_its_band(
        tmp_path, monkeypatch):
    """N11: this test's R4 premise ("there is no total-of-totals level at all") is now false — loop
    (b) adds one. Its assertions stand unchanged under the new premise: band 4's `7,800` sums the two
    bound totals exactly and sits directly after a bound total whose report is `asserted` with
    `table_uri` None (D6), so the TABLE-level reader — who would say yes — is never asked about it.
    The totals level does ask, but the role reader here is the default one over an empty recordings
    directory with no live reader: NO CLAIM (ruling R3). So nothing is recorded, nothing binds, and
    the line is read in its own band exactly as before the loop."""
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


# ================================================================== R261 loop (b): the totals level
#
# Spec `docs/superpowers/specs/2026-10-02-r261-grand-total-design.md` § 6.2's table, row by row, on
# `printed_total_pdf`'s band 4. The table-level `_Reader` answers `yes` on the two table totals, so
# `#printedtotal1-l0` (5,100) and `#printedtotal3-l0` (2,700) are bound before band 4 is reached;
# the role reader `_RoleReader` answers by value and records what it was asked.

PT1 = URIRef(f"{DOC}#printedtotal1-l0")
PT3 = URIRef(f"{DOC}#printedtotal3-l0")
GRAND = URIRef(f"{DOC}#printedtotal4-l0")


class _RoleReader:
    """The totals-level twin of `_Reader`: answers by printed value from the closed
    `table_total | total_of_totals | other | cannot_tell` set; records every value it was asked
    about. A value absent from `answers` gets `default` (None = no claim). `raises` makes every
    ask raise (Review Focus 3)."""

    def __init__(self, answers=None, default=None, raises=False):
        self.answers = dict(answers or {})
        self.default = default
        self.raises = raises
        self.asked: list[str] = []

    def ask(self, crop_png, value, listing):
        self.asked.append(value)
        assert crop_png[:8] == b"\x89PNG\r\n\x1a\n", "the role reader must be handed the crop"
        if self.raises:
            raise RuntimeError("the role reader failed")
        a = self.answers.get(value, self.default)
        return None if a is None else R.TotalRoleReading(answer=a)


_TABLE_YES = {"5,100": "yes", "2,700": "yes"}


def _compile_levels(monkeypatch, pdf, role_reader, table_answers=None, **kw):
    """Compile with the table-level `_Reader` answering `yes` on the two table totals and
    `role_reader` patched onto `totalrole.default_reader` (looked up at call time)."""
    monkeypatch.setattr(R, "default_reader", lambda: role_reader)
    return _compile(monkeypatch, pdf, _Reader(_TABLE_YES if table_answers is None
                                              else table_answers), **kw)


@pytest.mark.parametrize("answer, grand, bound", [
    ("total_of_totals", "7,800", True),    # role + arithmetic   -> bound
    ("total_of_totals", "7,801", False),   # role, no arithmetic -> NOT bound, role never asked
    ("table_total", "7,800", False),       # arithmetic, no role -> NOT bound: one not_total
    ("other", "7,800", False),
    ("cannot_tell", "7,800", False),
])
def test_the_totals_level_conjunction_binds_band_4(tmp_path, monkeypatch, answer, grand, bound):
    pdf = _pdf(tmp_path, "printed_total_pdf", grand_total=grand)
    role = _RoleReader({grand: answer})
    rep = _compile_levels(monkeypatch, pdf, role)
    g = rep.graph
    assert {PT1, PT3} <= set(_printed_totals(g))          # both table totals bound first
    holds = grand == "7,800"
    # Arithmetic first: the role reader is asked about band 4's number only when the sum holds.
    assert role.asked == ([grand] if holds else [])
    r4 = rep.regions[4]
    chosen = [c for _, c in _decisions(g, 4, "printed_total")]
    if bound:
        assert (GRAND, RDF.type, T("PrintedTotal")) in g
        assert g.value(GRAND, T("cellText")) == Literal("7,800")
        assert (GRAND, T("totalOf"), None) not in g
        assert set(g.objects(GRAND, T("aggregates"))) == {PT1, PT3}
        assert chosen == ["total"]
        assert (r4.verdict, r4.table_uri, r4.cells, r4.tokens_asserted, r4.tokens_escalated) \
            == ("asserted", None, 0, 1, 0)
    else:
        assert (GRAND, None, None) not in g
        assert not [p for p in _printed_totals(g) if "#printedtotal4" in str(p)]
        assert (r4.verdict, r4.reason) == ("ignored", "fewer than 2 lines")
        assert chosen == (["not_total"] if holds else [])


def test_with_one_table_total_bound_the_role_reader_is_not_asked(tmp_path, monkeypatch):
    """§ 6.2 row 4: `5,101` fails table A's arithmetic, so only `2,700` binds at table level;
    `match_totals` needs >= 2 operands, so band 4's `2,700` (equal to the one bound total) is never
    put to the role reader, and nothing is recorded for it."""
    pdf = _pdf(tmp_path, "printed_total_pdf", first_total="5,101", grand_total="2,700")
    role = _RoleReader(default="total_of_totals")
    rep = _compile_levels(monkeypatch, pdf, role)
    g = rep.graph
    assert _printed_totals(g) == [PT3]
    assert role.asked == []
    assert _decisions(g, 4, "printed_total") == []
    assert (rep.regions[4].verdict, rep.regions[4].reason) == ("ignored", "fewer than 2 lines")


def test_a_bound_grand_total_is_never_an_operand_of_a_later_one(tmp_path, monkeypatch):
    """R-f / Review Focus 4: `15,600` = 5,100 + 2,700 + 7,800 — the sum of every PrintedTotal on the
    page once the grand total has bound. The operands are the TABLE-LEVEL totals only (those carrying
    `tab:totalOf`), whose sum is 7,800, so `15,600` never matches and is never asked."""
    pdf = _pdf(tmp_path, "printed_total_pdf", after_grand=("15,600",))
    role = _RoleReader(default="total_of_totals")
    rep = _compile_levels(monkeypatch, pdf, role)
    g = rep.graph
    assert (GRAND, RDF.type, T("PrintedTotal")) in g
    assert role.asked == ["7,800"]
    assert not [p for p in _printed_totals(g) if "#printedtotal5" in str(p)]
    assert _decisions(g, 5, "printed_total") == []
    assert (rep.regions[5].verdict, rep.regions[5].reason) == ("ignored", "fewer than 2 lines")


def test_the_grand_totals_carved_remainder_is_classified_alone(tmp_path, monkeypatch):
    """Spec § 2 step 4 (concern 2's shape): `grand_note_lines=2` puts the Note in band 4 beside
    `7,800`. The grand total binds and is carved; the Note is read on its own — the same two lines
    band 1's carved remainder holds, and classified exactly as `test_the_carved_remainder_is_
    classified_alone` measures band 1's (escalated KIND_NOT_SUPPORTED, 16 words), with the bound
    total booked asserted to the same band."""
    pdf = _pdf(tmp_path, "printed_total_pdf", grand_note_lines=2)
    role = _RoleReader(default="total_of_totals")
    rep = _compile_levels(monkeypatch, pdf, role)
    g = rep.graph
    assert (GRAND, RDF.type, T("PrintedTotal")) in g
    r1, r4 = rep.regions[1], rep.regions[4]
    assert (r4.verdict, r4.reason, r4.tokens_asserted, r4.tokens_escalated) == \
        ("escalated", "KIND_NOT_SUPPORTED", 1, 16)
    assert (r4.verdict, r4.reason, r4.tokens_escalated) == \
        (r1.verdict, r1.reason, r1.tokens_escalated)               # the same Note, read alike
    assert "7,800" not in r4.ascii and "Note:" in r4.ascii


def test_a_grand_total_beneath_the_last_table_total_in_the_same_band_binds(tmp_path, monkeypatch):
    """Review Focus 1 / D3: `grand_gap=14.0` puts `7,800` in band 3 as line 1, beneath `2,700` on
    line 0. Line 0 binds at table level first, so by line 1 it is in the graph and is an operand:
    both bind, and the grand total aggregates `#printedtotal3-l0`."""
    pdf = _pdf(tmp_path, "printed_total_pdf", grand_gap=14.0)
    role = _RoleReader(default="total_of_totals")
    rep = _compile_levels(monkeypatch, pdf, role)
    g = rep.graph
    grand = URIRef(f"{DOC}#printedtotal3-l1")
    assert set(_printed_totals(g)) == {PT1, PT3, grand}
    assert (grand, T("totalOf"), None) not in g
    assert set(g.objects(grand, T("aggregates"))) == {PT1, PT3}
    assert role.asked == ["7,800"]
    assert [c for _, c in _decisions(g, 3, "printed_total")] == ["total", "total"]
    r3 = rep.regions[3]
    assert (r3.verdict, r3.table_uri, r3.cells, r3.tokens_asserted, r3.tokens_escalated) \
        == ("asserted", None, 0, 2, 0)


def test_an_operand_table_band_is_resolved_only_when_unique():
    """Review Focus 2 / D1: the operand's table band is the UNIQUE `j` whose report names the table
    — zero or two matching reports is no band (so no crop, no ask), never a guess from `j - 1`."""
    from iladub.etkl.compile import RegionKind, RegionReport, _operand_table_band
    t = URIRef(f"{DOC}#table2")

    def rep(table_uri):
        return RegionReport(RegionKind.NON_TABLE, "asserted", 0, None, None, "",
                            table_uri=table_uri)
    assert _operand_table_band([rep(None), rep(None), rep(t), rep(None)], t) == 2
    assert _operand_table_band([rep(URIRef(f"{DOC}#table0")), rep(None)], t) is None
    assert _operand_table_band([], t) is None
    assert _operand_table_band([rep(t), rep(None), rep(t)], t) is None


def test_an_unresolved_operand_table_band_is_no_ask_no_record_no_bind(tmp_path, monkeypatch):
    """Review Focus 2 at the compile: the binding takes each operand's table band from
    `_operand_table_band` (D1) and from nothing else — when it resolves no band the arithmetic still
    holds, but no crop can be built, so the role reader (who would say `total_of_totals`) is never
    asked, nothing is recorded and nothing binds. On this fixture every operand's table sits directly
    above its total, so a `j - 1` guess would build the same crop: only this patch can show that the
    call site consults the resolver rather than a position."""
    from iladub.etkl import compile as C
    monkeypatch.setattr(C, "_operand_table_band", lambda reports, table_uri: None)
    pdf = _pdf(tmp_path, "printed_total_pdf")
    role = _RoleReader(default="total_of_totals")
    rep = _compile_levels(monkeypatch, pdf, role)
    g = rep.graph
    assert set(_printed_totals(g)) == {PT1, PT3}
    assert role.asked == []
    assert _decisions(g, 4, "printed_total") == []
    assert (rep.regions[4].verdict, rep.regions[4].reason) == ("ignored", "fewer than 2 lines")


@pytest.mark.parametrize("role_reader", [
    None,                                   # no reader at all
    _RoleReader(default=None),              # the reader returns no claim
    _RoleReader(raises=True),               # the reader raises
], ids=["no-reader", "returns-none", "raises"])
def test_no_role_claim_records_nothing_and_binds_nothing(tmp_path, monkeypatch, role_reader):
    """Review Focus 3 / ruling R3: a role reader that is absent, returns None or raises is NO
    CLAIM — no `printed_total` decision on band 4, nothing bound, the band read as today."""
    pdf = _pdf(tmp_path, "printed_total_pdf")
    rep = _compile_levels(monkeypatch, pdf, role_reader)
    g = rep.graph
    assert set(_printed_totals(g)) == {PT1, PT3}
    assert _decisions(g, 4, "printed_total") == []
    assert (rep.regions[4].verdict, rep.regions[4].reason) == ("ignored", "fewer than 2 lines")
    if role_reader is not None:
        assert role_reader.asked == ["7,800"]


def test_the_grand_total_graph_conforms_and_both_shape_halves_are_live(tmp_path, monkeypatch):
    """The compile ran with `validate_shapes=True` (the default) and did not raise; the membrane is
    run explicitly, then with each half of `tab:PrintedTotalShape`'s level constraint broken on the
    COMPILED grand total: a `tab:totalOf` added (a table-level total may not aggregate a
    PrintedTotal), and a non-PrintedTotal operand added (a grand total aggregates only
    PrintedTotals)."""
    from iladub.etkl.compile import _validate
    pdf = _pdf(tmp_path, "printed_total_pdf")
    rep = _compile_levels(monkeypatch, pdf, _RoleReader(default="total_of_totals"))
    g = rep.graph
    assert (GRAND, RDF.type, T("PrintedTotal")) in g
    ok, text, _ = _validate(g)
    assert ok, text

    g1 = g.__class__(); g1 += g
    g1.add((GRAND, T("totalOf"), URIRef(f"{DOC}#table2")))
    ok, text, legs = _validate(g1)
    assert not ok and "tab" in legs
    assert "may not aggregate another tab:PrintedTotal" in text

    g2 = g.__class__(); g2 += g
    g2.add((GRAND, T("aggregates"), next(iter(g.objects(PT3, T("aggregates"))))))
    ok, text, legs = _validate(g2)
    assert not ok and "tab" in legs
    assert "may aggregate only tab:PrintedTotal operands" in text


def test_every_uncarved_word_is_booked_exactly_once_with_the_grand_total_bound(
        tmp_path, monkeypatch):
    """`test_every_uncarved_word_is_booked_exactly_once`, with the totals level binding band 4."""
    pdf = _pdf(tmp_path, "printed_total_pdf", grand_note_lines=2)
    rep = _compile_levels(monkeypatch, pdf, _RoleReader(default="total_of_totals"))
    from iladub.etkl.compile import page_bands
    bands = page_bands(pdf, 0)
    g = rep.graph
    assert (GRAND, RDF.type, T("PrintedTotal")) in g
    assert len(rep.regions) == len(bands)
    for i, (b, r) in enumerate(zip(bands, rep.regions)):
        words = sum(len(ln.words) for ln in b.lines)
        ignored = g.value(URIRef(f"{DOC}#ignored{i}"),
                          URIRef("https://w3id.org/iladub/etkl#bandText"))
        ignored_words = len(str(ignored).split()) if ignored is not None else 0
        assert r.tokens_asserted + r.tokens_escalated + ignored_words == words, (i, r)
    assert rep.asserted == sum(r.tokens_asserted for r in rep.regions)
    assert rep.escalated == sum(r.tokens_escalated for r in rep.regions)
    assert [r.tokens_asserted for r in rep.regions][1::2] == [1, 1]   # bands 1 and 3
    assert rep.regions[4].tokens_asserted == 1
