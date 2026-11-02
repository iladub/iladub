"""Synthetic contract set Task 1: manifest, fetch, verify — network-free (download injected)."""
import hashlib
import subprocess

import pytest

from scripts.synthetic_contracts import manifest as m

ROW = """@prefix syn: <https://w3id.org/iladub/synthetic#> .
<urn:t> a syn:Template ; syn:id "t1" ; syn:url "https://example.org/t.pdf" ;
    syn:sha256 "{sha}" ; syn:pages 1 .
"""


def _manifest(tmp_path, data):
    p = tmp_path / "templates.ttl"
    p.write_text(ROW.format(sha=hashlib.sha256(data).hexdigest()))
    return p


def test_manifest_pins_four_templates():
    t = m.load_manifest()
    assert set(t) == {"gafta-48", "gafta-79b", "gafta-124", "usda-ffp-cp"}
    for x in t.values():
        assert len(x.sha256) == 64 and int(x.sha256, 16) >= 0


def test_fetch_downloads_and_verifies(tmp_path):
    data = b"%PDF-fake"
    mf = _manifest(tmp_path, data)
    root = tmp_path / "synthetic"
    assert m.fetch(root, download=lambda url: data, manifest=mf) == 0
    t = m.load_manifest(mf)["t1"]
    assert m.template_path(t, root).read_bytes() == data
    m.verify(t, root)


def test_build_refuses_sha_mismatch(tmp_path):
    mf = _manifest(tmp_path, b"expected")
    root = tmp_path / "synthetic"
    t = m.load_manifest(mf)["t1"]
    with pytest.raises(m.TemplateMissing):
        m.verify(t, root)
    assert m.fetch(root, download=lambda url: b"other bytes", manifest=mf) != 0
    assert not m.template_path(t, root).exists()
    p = m.template_path(t, root)
    p.write_bytes(b"other bytes")
    with pytest.raises(m.TemplateMismatch):
        m.verify(t, root)


def test_synthetic_dir_is_ignored():
    r = subprocess.run(["git", "check-ignore", "synthetic/x.pdf"], cwd=m.REPO)
    assert r.returncode == 0


def test_fetch_keeps_and_verifies_a_hand_placed_template(tmp_path):
    """The README's USDA route (final review minor 1): omb.report answers a script with 403, so the
    file is downloaded in a browser and placed under synthetic/templates/. fetch must not download
    it again, must verify it, and must remove it if it is another edition."""
    data = b"%PDF-browser"
    mf = _manifest(tmp_path, data)
    root = tmp_path / "synthetic"
    t = m.load_manifest(mf)["t1"]
    p = m.template_path(t, root)
    p.parent.mkdir(parents=True)
    p.write_bytes(data)

    def refuse(url):
        raise AssertionError("fetch downloaded a template that was already in place")

    assert m.fetch(root, download=refuse, manifest=mf) == 0
    assert p.read_bytes() == data
    p.write_bytes(b"%PDF-another-edition")
    assert m.fetch(root, download=refuse, manifest=mf) == 1
    assert not p.exists()
