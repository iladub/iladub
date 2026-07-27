"""Loop C — compile_tables wiring. The default path is unchanged; the NEURAL slice fires only
on a tiling failure with an injected proposer; and a genuine off-center merge STILL escalates
even with a proposer present (the contract a geometric peel broke in loop B)."""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
from tests.etkl import fixtures as F


def _reasons(rep):
    return [r.reason for r in rep.regions]


def _verdicts(rep):
    return [r.verdict for r in rep.regions]


def test_compile_tables_accepts_row_role_proposer_kw(tmp_path):
    # signature smoke: the new optional kw exists and the default path is unchanged
    p = os.path.join(str(tmp_path), "simple.pdf")
    F.simple_table_pdf(p)
    assert "asserted" in _verdicts(compile_tables(p))
    assert "asserted" in _verdicts(compile_tables(p, row_role_proposer=None))


def test_offcenter_merge_still_escalates_with_a_proposer(tmp_path):
    # THE CONTRACT GUARD. Loop B's geometric caption peel broke exactly this: a genuinely
    # ambiguous off-center merge must NOT be silently asserted. The offcenter fixture's band
    # has exactly ONE non-leaf header row and does NOT tile, so it genuinely reaches the NEURAL
    # slice; with the proposer answering honestly ('level'), the reading reproduces the illegal
    # tree, the ORACLE refuses it, and the region escalates. High confidence must not rescue it.
    p = os.path.join(str(tmp_path), "offcenter.pdf")
    F.offcenter_merge_report_pdf(p)
    prop = RowRoleProposal(("level",), 0.99, "genuine group label")
    rep = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
    assert "MERGE_AMBIGUOUS" in _reasons(rep), _reasons(rep)


def test_shipped_pivot_unaffected_by_a_proposer(tmp_path):
    # a region that already tiles never reaches the NEURAL slice, so even an aggressive
    # well-formed proposal cannot change it.
    p = os.path.join(str(tmp_path), "pivot.pdf")
    F.pivoted_table_pdf(p)
    prop = RowRoleProposal(("furniture",), 0.99, "aggressive")
    base = compile_tables(p)
    withp = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
    assert _verdicts(base) == _verdicts(withp)
    assert _reasons(base) == _reasons(withp)
