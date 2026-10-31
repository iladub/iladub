"""Synthetic contract set Task 3: seeded fill specs (spec § 4.2)."""
import pytest
from reportlab.pdfbase.pdfmetrics import stringWidth

from scripts.synthetic_contracts import fills as fl
from scripts.synthetic_contracts import manifest as mf
from scripts.synthetic_contracts import maps as mp

TEMPLATES = sorted(mf.load_manifest())


@pytest.fixture(scope="module", params=TEMPLATES)
def pmap(request):
    return mp.load_map(request.param)


def test_same_seed_same_fill(pmap):
    assert fl.make_fill(pmap, 1) == fl.make_fill(pmap, 1)
    assert fl.make_fill(pmap, 1) != fl.make_fill(pmap, 2)


def test_every_blank_filled_once(pmap):
    f = fl.make_fill(pmap, 1)
    assert sorted(f.values) == sorted(b.field for b in pmap.blanks)
    assert len({b.field for b in pmap.blanks}) == len(pmap.blanks)


def test_every_value_fits_its_blank(pmap):
    for n in (1, 2, 3):
        f = fl.make_fill(pmap, n)
        assert f.font in fl.FONTS and 8 <= f.size <= 10
        for b in pmap.blanks:
            w = stringWidth(f.values[b.field], f.font, f.size)
            assert w <= (b.box.x1 - b.box.x0) - 2, (b.field, f.values[b.field])


def test_values_unique_within_document(pmap):
    for n in (1, 2, 3):
        vs = list(fl.make_fill(pmap, n).values.values())
        for i, a in enumerate(vs):
            for j, b in enumerate(vs):
                assert i == j or a not in b, (a, b)


def test_too_long_raises_named_field(pmap, monkeypatch):
    monkeypatch.setattr(fl, "draw", lambda key, rng, width: "W" * 500)
    with pytest.raises(fl.ValueTooLong) as e:
        fl.make_fill(pmap, 1)
    assert e.value.field in {b.field for b in pmap.blanks}


def test_committed_fills_load():
    files = sorted(fl.FILLS_DIR.glob("*.ttl"))
    assert len(files) == 12
    for t in TEMPLATES:
        m = mp.load_map(t)
        for n in (1, 2, 3):
            assert fl.load_fill(fl.fill_id(t, n)) == fl.make_fill(m, n)


def test_write_refuses_overwrite(tmp_path):
    m = mp.load_map(TEMPLATES[0])
    f = fl.make_fill(m, 1)
    fl.write_fill(f, tmp_path)
    with pytest.raises(FileExistsError):
        fl.write_fill(f, tmp_path)
    assert fl.load_fill(f.id, tmp_path) == f
