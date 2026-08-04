"""scripts/fetch_corpus.py unit battery — network-free (`download` is injected)."""
import hashlib

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF, Graph

from scripts.fetch_corpus import COR, USER_AGENT, _download, fetch_one
from tests.etkl.fixtures import simple_table_pdf

ENTRY = """@prefix cor: <https://w3id.org/iladub/corpus#> .
<urn:t> a cor:Document ; cor:file "fam/doc.pdf" ;
    cor:url "https://example.org/doc.pdf" ; cor:family "health" ;
    cor:series "s" ; cor:expectedVerdict cor:Unadjudicated {pin}.
"""


def _graph(sha=None):
    pin = f'; cor:sha256 "{sha}" ' if sha else ""
    return Graph().parse(data=ENTRY.format(pin=pin), format="turtle")


def _doc(g):
    return next(g.subjects(RDF.type, COR.Document))


def _pdf_bytes(tmp_path):
    p = tmp_path / "src.pdf"
    simple_table_pdf(str(p))
    return p.read_bytes()


def test_first_fetch_pins_and_keeps(tmp_path, capsys):
    """No cor:sha256 yet -> the file is KEPT and the values to pin are PRINTED
    (never written back — spec §4 verdict discipline)."""
    data = _pdf_bytes(tmp_path)
    g = _graph()
    out = fetch_one(g, _doc(g), tmp_path / "corpus", download=lambda url: data)
    assert out == "pin"
    assert (tmp_path / "corpus" / "fam" / "doc.pdf").is_file()
    printed = capsys.readouterr().out
    assert hashlib.sha256(data).hexdigest() in printed
    assert "cor:pages 1" in printed


def test_matching_checksum_fetches(tmp_path):
    data = _pdf_bytes(tmp_path)
    g = _graph(hashlib.sha256(data).hexdigest())
    assert fetch_one(g, _doc(g), tmp_path / "corpus",
                     download=lambda url: data) == "fetched"
    assert (tmp_path / "corpus" / "fam" / "doc.pdf").read_bytes() == data


def test_mismatch_removes_file(tmp_path, capsys):
    data = _pdf_bytes(tmp_path)
    g = _graph("0" * 64)
    assert fetch_one(g, _doc(g), tmp_path / "corpus",
                     download=lambda url: data) == "mismatch"
    assert not (tmp_path / "corpus" / "fam" / "doc.pdf").exists()
    assert "MISMATCH" in capsys.readouterr().out


def test_present_short_circuits_network(tmp_path):
    g = _graph()
    dest = tmp_path / "corpus" / "fam" / "doc.pdf"
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b"x")

    def boom(url):
        raise AssertionError("network touched for a present file")

    assert fetch_one(g, _doc(g), tmp_path / "corpus", download=boom) == "present"


def test_fetch_failure_reported(tmp_path, capsys):
    g = _graph("0" * 64)

    def down(url):
        raise OSError("HTTP Error 403: Forbidden")

    assert fetch_one(g, _doc(g), tmp_path / "corpus", download=down) == "failed"
    assert "FETCH FAILED" in capsys.readouterr().out


def test_download_sends_browser_ua(monkeypatch):
    """GrainCorp's CDN 403s bare Python-urllib — the UA header is the whole point."""
    seen = {}

    class _Resp:
        def read(self):
            return b"pdf"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req):
        seen["ua"] = req.get_header("User-agent")
        return _Resp()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    assert _download("https://example.org/x.pdf") == b"pdf"
    assert seen["ua"] == USER_AGENT
