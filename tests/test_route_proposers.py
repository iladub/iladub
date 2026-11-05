"""Recorded replay of the router's NEURAL proposers (Task 5). No model is ever called here."""
import json

from iladub.route import proposers as P
from iladub.route.lines import Line
from iladub.route.oracle import BoundaryAnswer, DoctypeAnswer

LISTING = "0\tfirst\n1\tsecond"
TAIL = "tail line"

BOUNDARY_JSON = {"verdict": "STARTS", "start_line": 1, "evidence_lines": [1], "model": "recorded-model"}
DOCTYPE_JSON = {"kind": "CONTRACT", "party_lines": [0, 1], "commitment_lines": [1],
                "other_evidence_lines": [], "proposed_type": None, "admitted_type": None,
                "model": "recorded-model"}


class FakeLive:
    client = "RouterHaiku"

    def __init__(self):
        self.calls = 0

    def boundary(self, listing, previous_tail):
        self.calls += 1
        return P.Proposed(BoundaryAnswer("CONTINUES", None, ()), "live-model")

    def doctype(self, listing, admitted):
        self.calls += 1
        return P.Proposed(DoctypeAnswer("REFUSES", (), (), (), None, None), "live-model")


def _line(i, text):
    return Line(page=1, index=i, text=text, top=0.0, bottom=1.0, x0=0.0, x1=1.0)


def test_listing_is_id_tab_text_zero_based():
    assert P.listing([_line(5, "a b"), _line(6, "c")]) == "0\ta b\n1\tc"


def test_recorded_reading_replays_without_live(tmp_path):
    (tmp_path / f"{P.boundary_key('RouterHaiku', TAIL, LISTING)}.json").write_text(json.dumps(BOUNDARY_JSON))
    got = P.RecordedProposer(live=None, client="RouterHaiku", directory=tmp_path).boundary(LISTING, TAIL)
    assert got == P.Proposed(BoundaryAnswer("STARTS", 1, (1,)), "recorded-model")
    (tmp_path / f"{P.doctype_key('RouterHaiku', ['x'], LISTING)}.json").write_text(json.dumps(DOCTYPE_JSON))
    got = P.RecordedProposer(live=None, client="RouterHaiku", directory=tmp_path).doctype(LISTING, ["x"])
    assert got.model == "recorded-model" and got.answer.kind == "CONTRACT"
    assert got.answer.party_lines == (0, 1)


def test_miss_without_live_is_none(tmp_path):
    rp = P.RecordedProposer(live=None, client="RouterHaiku", directory=tmp_path)
    assert rp.boundary(LISTING, TAIL) is None
    assert rp.doctype(LISTING, []) is None


def test_different_inputs_miss_the_recording(tmp_path):
    (tmp_path / f"{P.boundary_key('RouterHaiku', TAIL, LISTING)}.json").write_text(json.dumps(BOUNDARY_JSON))
    (tmp_path / f"{P.doctype_key('RouterHaiku', ['a'], LISTING)}.json").write_text(json.dumps(DOCTYPE_JSON))
    rp = P.RecordedProposer(live=None, client="RouterHaiku", directory=tmp_path)
    assert rp.boundary(LISTING, TAIL) is not None
    assert rp.boundary(LISTING, "another tail") is None
    assert rp.doctype(LISTING, ["a"]) is not None
    assert rp.doctype(LISTING, ["a", "b"]) is None
    assert P.RecordedProposer(live=None, client="Other", directory=tmp_path).boundary(LISTING, TAIL) is None


def test_doctype_key_ignores_admitted_order():
    assert P.doctype_key("c", ["b", "a"], "L") == P.doctype_key("c", ["a", "b"], "L")


def test_records_only_under_flag(tmp_path, monkeypatch):
    live = FakeLive()
    rp = P.RecordedProposer(live=live, client="RouterHaiku", directory=tmp_path)
    monkeypatch.delenv("ILADUB_RECORD_READINGS", raising=False)
    assert rp.boundary(LISTING, TAIL).model == "live-model"
    assert rp.doctype(LISTING, []).model == "live-model"
    assert list(tmp_path.iterdir()) == []
    monkeypatch.setenv("ILADUB_RECORD_READINGS", "1")
    rp.boundary(LISTING, TAIL)
    rp.doctype(LISTING, [])
    assert len(list(tmp_path.iterdir())) == 2
    # and the recording now replays, with the live model id
    again = P.RecordedProposer(live=None, client="RouterHaiku", directory=tmp_path)
    assert again.boundary(LISTING, TAIL).model == "live-model"


def test_reading_has_no_note_field(tmp_path, monkeypatch):
    monkeypatch.setenv("ILADUB_RECORD_READINGS", "1")
    rp = P.RecordedProposer(live=FakeLive(), client="RouterHaiku", directory=tmp_path)
    rp.boundary(LISTING, TAIL)
    rp.doctype(LISTING, [])
    for f in tmp_path.iterdir():
        d = json.loads(f.read_text())
        assert "note" not in d and "model" in d
        assert not any(isinstance(v, str) and v not in ("live-model",) and len(v) > 12 for v in d.values())


def test_directory_defaults_at_call_time(tmp_path, monkeypatch):
    rp = P.RecordedProposer(live=None, client="RouterHaiku")
    monkeypatch.setattr(P, "BOUNDARY_DIR", tmp_path)
    (tmp_path / f"{P.boundary_key('RouterHaiku', TAIL, LISTING)}.json").write_text(json.dumps(BOUNDARY_JSON))
    assert rp.boundary(LISTING, TAIL) is not None


def test_default_order_jev_then_haiku(monkeypatch):
    monkeypatch.setattr(P, "jev_available", lambda: True)
    monkeypatch.setattr(P, "haiku_available", lambda: False)
    ps = P.default_proposers()
    assert [p.client for p in ps] == ["RouterJev", "RouterHaiku"]
    assert ps[1].live is None
    monkeypatch.setattr(P, "jev_available", lambda: False)
    ps = P.default_proposers()
    assert [p.client for p in ps] == ["RouterHaiku"]


def test_live_haiku_only_when_available(monkeypatch):
    monkeypatch.setattr(P, "jev_available", lambda: False)
    monkeypatch.setattr(P, "haiku_available", lambda: True)
    live = P.default_proposers()[0].live
    assert live is not None and live.client == "RouterHaiku"


def test_import_does_not_need_baml_client():
    src = open(P.__file__, encoding="utf-8").read()
    assert not any(l.startswith(("import baml", "from baml")) for l in src.splitlines())


def test_baml_proposer_converts_a_reading(monkeypatch):
    import enum
    from types import SimpleNamespace as NS

    class V(str, enum.Enum):
        STARTS = "STARTS"

    class K(str, enum.Enum):
        OTHER = "OTHER"

    b = NS(RouteBoundaryHaiku=lambda l, t: NS(verdict=V.STARTS, start_line=2, evidence_lines=[2]),
           RouteDoctypeHaiku=lambda l, a: NS(kind=K.OTHER, party_lines=[], commitment_lines=[],
                                              other_evidence_lines=[3], proposed_type="t", admitted_type=None))
    prop = P.BamlProposer("RouterHaiku")
    monkeypatch.setattr(prop, "_fn", lambda stem: getattr(b, stem + "Haiku"))
    assert prop.boundary("l", "t") == P.Proposed(BoundaryAnswer("STARTS", 2, (2,)), "claude-haiku-5-5")
    got = prop.doctype("l", ["x"])
    assert got.answer.kind == "OTHER" and type(got.answer.kind) is not K and got.answer.other_evidence_lines == (3,)
