"""Battery-logic unit battery — network-free, corpus-free: exercises the helpers in
tests/test_corpus.py on a synthetic reportlab document + a tmp manifest. The real
battery (corpus-marked) reuses exactly these helpers, so verdict semantics are proven
without a single fetch."""
import hashlib

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Graph

from tests.etkl.fixtures import simple_table_pdf
from tests.test_corpus import (COR, check_verdict, manifest_entries,
                               require_pinned_edition, _compiled)

MANIFEST = """@prefix cor: <https://w3id.org/iladub/corpus#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
<urn:t> a cor:Document ; cor:file "synthetic/cbc.pdf" ; cor:url "urn:none" ;
    cor:family "health" ; cor:series "synthetic-cbc" ;
    cor:expectedVerdict {verdict} ; {extra}
    cor:sha256 "{sha}" .
"""


def _seed(tmp_path, sha=None, verdict="cor:Unadjudicated", extra=""):
    pdf = tmp_path / "synthetic" / "cbc.pdf"
    pdf.parent.mkdir(parents=True)
    simple_table_pdf(str(pdf))
    real = hashlib.sha256(pdf.read_bytes()).hexdigest()
    m = tmp_path / "manifest.ttl"
    m.write_text(MANIFEST.format(sha=sha or real, verdict=verdict, extra=extra))
    return m, tmp_path


def test_compilesabove_passes_on_synthetic(tmp_path):
    # Floor 0.5 for a clean synthetic 3-column table. If this fixture measures below
    # 0.5, report the measured score and set the floor at-or-below it (synthetic
    # fixture calibration, not a real-document verdict).
    m, root = _seed(tmp_path, verdict="cor:CompilesAbove",
                    extra='cor:scoreFloor "0.5"^^xsd:decimal ;')
    [entry] = manifest_entries(m)
    dest = require_pinned_edition(entry, root)
    rep, dt = _compiled(str(dest))
    check_verdict(rep, entry)          # must not raise
    assert dt >= 0.0


def test_unadjudicated_measures_without_gating(tmp_path):
    m, root = _seed(tmp_path)
    [entry] = manifest_entries(m)
    rep, _ = _compiled(str(require_pinned_edition(entry, root)))
    verdicts = check_verdict(rep, entry)   # no assertion beyond non-crash
    assert isinstance(verdicts, list) and verdicts


def test_absent_document_skips(tmp_path):
    m, root = _seed(tmp_path)
    [entry] = manifest_entries(m)
    (root / entry["file"]).unlink()
    with pytest.raises(pytest.skip.Exception):
        require_pinned_edition(entry, root)


def test_unpinned_document_skips(tmp_path):
    m, root = _seed(tmp_path)
    text = m.read_text()
    m.write_text(text[: text.rindex("cor:sha256")].rstrip().rstrip(";") + " .\n")
    [entry] = manifest_entries(m)
    assert entry["sha256"] is None
    with pytest.raises(pytest.skip.Exception):
        require_pinned_edition(entry, root)


def test_edition_drift_fails_not_skips(tmp_path):
    m, root = _seed(tmp_path, sha="0" * 64)
    [entry] = manifest_entries(m)
    with pytest.raises(AssertionError, match="pinned"):
        require_pinned_edition(entry, root)


def test_compilesabove_below_floor_fails(tmp_path):
    # Floor set above 1.0 so the synthetic fixture's score can never reach it —
    # proves the floor assertion actually refuses, not just passes by construction.
    m, root = _seed(tmp_path, verdict="cor:CompilesAbove",
                    extra='cor:scoreFloor "1.1"^^xsd:decimal ;')
    [entry] = manifest_entries(m)
    dest = require_pinned_edition(entry, root)
    rep, _ = _compiled(str(dest))
    with pytest.raises(AssertionError):
        check_verdict(rep, entry)


def test_semantic_escalation_without_escalated_region_fails(tmp_path):
    # The clean synthetic fixture only asserts (no escalated region), so a
    # cor:SemanticEscalation verdict must be refused, not silently accepted.
    m, root = _seed(tmp_path, verdict="cor:SemanticEscalation",
                    extra='cor:ambiguity "synthetic" ;')
    [entry] = manifest_entries(m)
    dest = require_pinned_edition(entry, root)
    rep, _ = _compiled(str(dest))
    with pytest.raises(AssertionError):
        check_verdict(rep, entry)
