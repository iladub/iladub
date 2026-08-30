"""R131(a) — a PAGE-scope membrane refusal is a membrane verdict, and says so by TYPE.

The defect (residue R131): `compile.py`'s page-scope gate raised a bare `AssertionError` while
the document seam raised `membrane.MembraneRefusal`. A page-level violation aborts the whole
document before `_seal` is ever reached, so the document that was LEAST clean was the one no
caller could recognise as having refused — one `except membrane.MembraneRefusal` saw the
document scope and missed the page scope entirely.

**ONLY THE (a) HALF IS CLOSED HERE.** R131(b) — minting page-scope membrane HEALTH — is the
modelling half ("is a page graph a holon with its own membrane health?"), it is `holon:06`'s,
and nothing here answers it. The graph these refusals carry has no health triple.

THE ORACLE INJECTS ITS REFUSAL, AND THAT IS A WEAKER CLAIM THAN A DRIVEN ONE — stated rather
than hidden. See `test_a_page_scope_refusal_is_catchable_as_a_membrane_verdict`.
"""
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")

from rdflib import Graph

from tests.etkl.fixtures import simple_table_pdf
from iladub.etkl import compile_tables
from iladub.etkl import compile as compile_mod
from iladub.etkl import membrane


def _refusing(_graph, legs=("tab", "dec")):
    """A `_validate` stand-in that refuses on the tab leg with a recognisable report."""
    return False, "INJECTED PAGE-SCOPE REFUSAL", ("tab",)


def test_a_page_scope_refusal_is_catchable_as_a_membrane_verdict(tmp_path, monkeypatch):
    """The row's closure criterion for half (a): the page site raises `MembraneRefusal`, so one
    `except` clause sees both scopes.

    WHY THE REFUSAL IS INJECTED, MEASURED rather than assumed. The 2026-08-29 handoff required
    this seam to be measured before the test was written: *can a tracked corpus document produce
    a page-scope refusal at all?* It cannot. Measured 2026-08-30 by wrapping `compile._validate`
    and `document._validate` separately (they are distinct bindings — `document.py` holds its own
    import-time reference — so the two scopes partition exactly, confirmed by a caller-frame
    histogram showing only the two call sites) and compiling all 7 tracked corpus documents:

        page-scope `_validate` calls   14   of which conforms=False   0
        doc-scope  `_validate` calls    7   of which conforms=False   0

    14 rather than one per page because the raise site is guarded by
    `validate_shapes and (any tab:RecordTable or any tab:HierarchicalTable)` — only a page that
    produced an asserted table reaches `_validate` at all. So no tracked document violates a
    page-scope shape, which is also why the reproduction that established R131 injected its
    refusal. The only way to reach the raise is to make `_validate` refuse, and this test does
    exactly that, at the same public seam.

    What that costs, said plainly: this pins the TYPE and PAYLOAD of the raise, not that any
    real input reaches it. A regression that made the page gate unreachable would not fail here.
    """
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    monkeypatch.setattr(compile_mod, "_validate", _refusing)
    with pytest.raises(membrane.MembraneRefusal) as exc:
        compile_tables(str(p))
    assert isinstance(exc.value, membrane.MembraneRefusal)
    assert exc.value.legs == ("tab",)
    assert isinstance(exc.value.graph, Graph) and len(exc.value.graph) > 0
    assert "INJECTED PAGE-SCOPE REFUSAL" in str(exc.value)


def test_the_page_scope_refusal_message_is_unchanged(tmp_path, monkeypatch):
    """Backward compatibility, pinned: `MembraneRefusal` is an `AssertionError` subclass and
    `str(exc)` is byte-identical to what the bare `AssertionError` produced. Every existing
    interceptor in this repo is isinstance-based, so this raise is transparent to all of them."""
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    monkeypatch.setattr(compile_mod, "_validate", _refusing)
    with pytest.raises(AssertionError) as exc:
        compile_tables(str(p))
    assert str(exc.value) == compile_mod._refusal_message(
        "asserted holon", ("tab",), "INJECTED PAGE-SCOPE REFUSAL")


def test_one_except_clause_sees_both_membrane_scopes(tmp_path, monkeypatch):
    """The point of the row, stated as the invariant rather than as two type assertions: the
    page seam and the document seam raise the SAME exception class, so a caller writing one
    handler is not silently blind to the scope that aborts earliest."""
    p = tmp_path / "cbc.pdf"; simple_table_pdf(str(p))
    monkeypatch.setattr(compile_mod, "_validate", _refusing)
    seen = None
    try:
        compile_tables(str(p))
    except membrane.MembraneRefusal as e:      # the DOCUMENT seam's own handler shape
        seen = e
    assert seen is not None, "the page seam escaped the document seam's handler"
    assert seen.legs and seen.graph is not None
