"""R301 — the adoption site's guard, and adoption's outcome REPORTED rather than inferred.

Spec: docs/superpowers/specs/2026-10-08-r301-producer-guard-design.md § 2.1 step 5 and § 2.5.

`CompilationReport.adoption` records which of four things happened on the page: the gate did not
open, the ledger refused, the guard refused, or the page adopted. Step 5: after the new graph is
emitted and BEFORE anything is installed, `carry_from_pdf` runs on the new graph and the guard's
select runs over it; any returned cell refuses the adoption whole, so the graph, reports and totals
from before adoption stand (invariant I1, second half).

Synthetic throughout; the fed-h41 corpus pins are Task 6's (`tests/test_r301_fed_h41.py`).
"""
import pytest
from rdflib import URIRef
from rdflib.compare import isomorphic

from iladub.etkl.compile import compile_tables


def _compile(builder, tmp_path, name, adopt):
    p = tmp_path / f"{name}.pdf"
    builder(str(p))
    return compile_tables(str(p), 0, validate_shapes=True, datagrid_adopt=adopt)


def _regions(rep):
    return [(r.verdict, r.reason, r.cells, r.table_uri, r.tokens_asserted, r.tokens_escalated,
             r.supersedes) for r in rep.regions]


@pytest.fixture
def adopting_pdf(tmp_path):
    """R175's synthetic adopting fixture (`test_adoption_document.py`), at page scope."""
    from tests.etkl.fixtures import currency_marker_escalating_with_note_pdf
    p = tmp_path / "adopting.pdf"
    currency_marker_escalating_with_note_pdf(str(p))
    return str(p)


def test_the_default_is_not_opened(tmp_path):
    """Adoption off: the gate cannot open, whatever the page holds."""
    from tests.etkl.fixtures import currency_marker_escalating_with_note_pdf
    assert _compile(currency_marker_escalating_with_note_pdf, tmp_path, "off", False).adoption \
        == "not_opened"


def test_a_page_that_left_nothing_unread_is_not_opened(tmp_path):
    """`escalated_total == 0`: nothing for a grid to supersede (`simple_table_pdf` reads in full)."""
    from tests.etkl.fixtures import simple_table_pdf
    rep = _compile(simple_table_pdf, tmp_path, "simple", True)
    assert rep.escalated == 0
    assert rep.adoption == "not_opened"


def test_a_page_with_no_grid_is_not_opened(tmp_path):
    """The plan's FLAGGED interpretation (not ruled): a page that escalates but derives no grid
    built no ledger, so nothing was compared — the gate did not open. `false_transposed_pdf`
    escalates 12 tokens and `derive_data_grids` returns no grid on it (measured, Task 5 report)."""
    from tests.etkl.fixtures import false_transposed_pdf
    from iladub.etkl.datagrid import derive_data_grids
    p = tmp_path / "plain.pdf"
    false_transposed_pdf(str(p))
    assert not derive_data_grids(str(p), 0)
    rep = compile_tables(str(p), 0, validate_shapes=True, datagrid_adopt=True)
    assert rep.escalated > 0
    assert rep.adoption == "not_opened"


def test_the_ledger_refuses_a_grid_that_reads_no_more(tmp_path):
    """A grid is derived and a ledger built, but it leaves no less ink unread than the bands did:
    the outcome is `ledger_refused`, and the page is the adopt-off page."""
    from tests.etkl.fixtures import printed_total_pdf
    off = _compile(printed_total_pdf, tmp_path, "pt-off", False)
    on = _compile(printed_total_pdf, tmp_path, "pt-on", True)
    assert on.adoption == "ledger_refused"
    assert _regions(on) == _regions(off) and on.score == off.score


def test_the_synthetic_fixture_adopts_and_reads_as_on_main(adopting_pdf):
    """`adopted`, and the page reads exactly as it did before this task (measured at `ee34115`)."""
    rep = compile_tables(adopting_pdf, 0, validate_shapes=True, datagrid_adopt=True)
    assert rep.adoption == "adopted"
    assert rep.score == 0.8888888888888888
    assert (rep.asserted, rep.escalated) == (16, 2)
    doc = "https://example.org/etkl/doc"
    assert _regions(rep) == [
        ("superseded", "REGION_TILING_FAILED", 0, None, 0, 0, ()),
        ("ignored", "fewer than 2 lines", 0, None, 0, 0, ()),
        ("asserted", None, 12, URIRef(f"{doc}#p0-datagrid"), 16, 0, (0,)),
        ("escalated", "DATAGRID_RESIDUE", 0, None, 0, 2, ()),
    ]


def test_the_guard_refuses_adoption_whole(adopting_pdf, monkeypatch):
    """The select returns a cell at the ADOPTION site only, so the pre-adoption guard (Task 4) is
    the identity and the refusal is step 5's alone. MEASURED (Task 5 report): per compile of this
    fixture `ruleguard.rule_separated_cells` is called exactly twice through the module attribute —
    first by `ruleguard.guard`, then by the adoption site — and the spy below asserts that count.

    Refused whole: the page is byte-for-byte the adopt-off page — score, totals, regions and graph."""
    from iladub.etkl import ruleguard
    off = compile_tables(adopting_pdf, 0, validate_shapes=True, datagrid_adopt=False)

    real = ruleguard.rule_separated_cells
    calls = []

    def second_call_fires(g):
        calls.append(g)
        if len(calls) == 2:
            return frozenset({URIRef("urn:r301:task5:a-rule-separated-cell")})
        return real(g)

    monkeypatch.setattr(ruleguard, "rule_separated_cells", second_call_fires)
    on = compile_tables(adopting_pdf, 0, validate_shapes=True, datagrid_adopt=True)

    assert len(calls) == 2
    assert on.adoption == "guard_refused"
    assert _regions(on) == _regions(off)
    assert (on.score, on.asserted, on.escalated) == (off.score, off.asserted, off.escalated)
    assert isomorphic(on.graph, off.graph)
    # I1, second half: the select's graph is the NEW one, and it is never the one returned.
    assert calls[1] is not on.graph
