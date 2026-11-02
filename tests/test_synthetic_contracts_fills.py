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


def test_no_value_is_template_text():
    """Local only: Task 6 locates values by exact match, so none may occur in template text."""
    import pdfplumber

    bad, seen = [], 0
    for t in TEMPLATES:
        path = mf.template_path(mf.load_manifest()[t])
        if not path.exists():
            pytest.skip("synthetic/templates/ absent (local-only test)")
        with pdfplumber.open(path) as pdf:
            text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
        flat = " ".join(text.split())
        for n in (1, 2, 3):
            for k, v in fl.load_fill(fl.fill_id(t, n)).values.items():
                seen += 1
                if v in text or v in flat:
                    bad.append((t, n, k, v))
    assert seen and not bad, bad


# ------------------------------------------------------------------ fill shapes (CI; final review I2)

EX = mf.REPO / "examples" / "synthetic-contracts"
FILL_NEGATIVE = EX / "negative" / "fill-negative.ttl"


def _validate_fills(*files):
    from pyshacl import validate
    from rdflib import Graph

    g = Graph()
    for f in files:
        g.parse(f, format="turtle")
    return validate(g, shacl_graph=Graph().parse(EX / "shapes.ttl"),
                    ont_graph=Graph().parse(EX / "synthetic.ttl"), inference="rdfs", advanced=True)


def test_committed_fills_conform():
    """All 12 committed fills conform under the repo's standard validation (rdfs inference).

    Until 2026-11-02 `syn:template` carried `rdfs:domain syn:PartMap`, so every fill was inferred
    to be a PartMap and failed the PartMap shape's `syn:review minCount 1` (final review I2)."""
    files = sorted(fl.FILLS_DIR.glob("*.ttl"))
    assert len(files) == 12
    ok, _, report = _validate_fills(*files)
    assert ok, report


def test_fill_negative_fails_each_planted_fault():
    from rdflib.namespace import SH

    ok, rg, report = _validate_fills(FILL_NEGATIVE)
    assert not ok
    viol = list(rg.subjects(SH.resultSeverity, SH.Violation))
    paths = {str(rg.value(r, SH.resultPath)) for r in viol}
    comps = {rg.value(r, SH.sourceConstraintComponent) for r in viol}
    syn = "https://w3id.org/iladub/synthetic#"
    assert syn + "font" in paths, report        # 1. a font outside the base-14 three
    assert syn + "text" in paths, report        # 2. a value with an empty text
    assert SH.SPARQLConstraintComponent in comps, report  # 3. two values fill one field key
    assert SH.ClosedConstraintComponent in comps, report  # 4. a property no fill may carry
