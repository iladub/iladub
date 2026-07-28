"""Loop C — compile_tables wiring. The default path is unchanged; the NEURAL slice fires only
on a tiling failure with an injected proposer; a genuine off-center merge STILL escalates
even with a proposer present (the contract a geometric peel broke in loop B); a region whose
tree already tiles never even CONSULTS the proposer (paid only where geometry actually failed);
and a genuinely tiling-failing region — a leaked caption + wrap-continuation, the real-PDF
analogue of test_rowrole_reading.caption_and_wrap_band — is rescued end-to-end: it escalates
without a proposer, and asserts (with a recorded PromotionDecision, carried caption, and the
merged label) with one."""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Namespace, RDF

from iladub.etkl import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
from tests.etkl import fixtures as F

TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")


def _reasons(rep):
    return [r.reason for r in rep.regions]


def _verdicts(rep):
    return [r.verdict for r in rep.regions]


class _CountingRowRoleProposer:
    """Counts how many times the NEURAL seam is actually consulted. Used to lock the
    invariant that a region whose geometric tree already tiles never pays the proposer
    cost (§8: NEURAL is invoked only where AXIOM/geometry genuinely failed)."""

    def __init__(self, proposal):
        self._proposal = proposal
        self.calls = 0

    def propose_header_row_roles(self, context):
        self.calls += 1
        return self._proposal


def test_compile_tables_accepts_row_role_proposer_kw(tmp_path):
    # signature smoke: the new optional kw exists and the default path is unchanged
    p = os.path.join(str(tmp_path), "simple.pdf")
    F.simple_table_pdf(p)
    assert "asserted" in _verdicts(compile_tables(p))
    assert "asserted" in _verdicts(compile_tables(p, row_role_proposer=None))


def test_offcenter_merge_still_escalates_with_a_proposer(tmp_path):
    # THE CONTRACT GUARD: the oracle does not rescue the honest 'level' reading. Loop B's
    # geometric caption peel broke exactly this case. The offcenter fixture's band has exactly
    # ONE non-leaf header row (role-vector length 1, measured and deliberate) and does NOT tile,
    # so it genuinely reaches the NEURAL slice; read as a genuine hierarchy level ('level'), the
    # reading reproduces the illegal tree, still fails region_tiles, and the region still
    # escalates MERGE_AMBIGUOUS, regardless of confidence. This does NOT claim the oracle can
    # rank two legal readings (it can't -- §2 Finding 5) or that every off-center merge is
    # unassertable with some other role vector; it pins only that the oracle never rescues this
    # specific honest, illegal reading.
    p = os.path.join(str(tmp_path), "offcenter.pdf")
    F.offcenter_merge_report_pdf(p)
    prop = RowRoleProposal(("level",), 0.99, "genuine group label")
    rep = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
    assert "MERGE_AMBIGUOUS" in _reasons(rep), _reasons(rep)


def test_shipped_pivot_unaffected_by_a_proposer(tmp_path):
    # THE REAL INVARIANT: a region whose geometric tree already tiles never even CONSULTS
    # the NEURAL proposer -- the LLM cost is paid only where geometry genuinely failed. A
    # FakeRowRoleProposer can't prove this (it never records whether it was called), so a
    # counting proposer asserts zero invocations; the verdict/reason comparison is kept as
    # a belt-and-braces output-stability check.
    p = os.path.join(str(tmp_path), "pivot.pdf")
    F.pivoted_table_pdf(p)
    prop = RowRoleProposal(("furniture",), 0.99, "aggressive")
    counting = _CountingRowRoleProposer(prop)
    base = compile_tables(p)
    withp = compile_tables(p, row_role_proposer=counting)
    assert counting.calls == 0
    assert _verdicts(base) == _verdicts(withp)
    assert _reasons(base) == _reasons(withp)


def test_caption_wrap_report_escalates_without_a_proposer(tmp_path):
    # THE RED CONDITION for the whole NEURAL slice: a leaked date caption (row 0) whose two
    # words' symmetrized spans overlap (the level-0 overlap mechanism), plus a wrap-continuation
    # fragment ('Unit') above the Ref column, over UNIFORM line spacing (header leading == body
    # leading, defeating header_rows_of's adaptive `gap < lead` wrap-absorption -- the
    # fixture-tuned `0.9 x lead` margin was already retired in B3, 2026-07-22, commit 947f6fa;
    # here `lead` itself equals the gap, so even the adaptive gate cannot fire). Without a
    # proposer this must genuinely escalate MERGE_AMBIGUOUS -- proving the fixture actually
    # needs the slice.
    p = os.path.join(str(tmp_path), "caption_wrap.pdf")
    F.caption_wrap_report_pdf(p)
    rep = compile_tables(p)
    assert "MERGE_AMBIGUOUS" in _reasons(rep), _reasons(rep)
    assert "asserted" not in _verdicts(rep)


def test_caption_wrap_report_asserts_with_a_resolving_proposer(tmp_path):
    # THE SUCCESS PATH (the coverage gap this test closes): the SAME fixture, with a proposer
    # reading row 0 as furniture (carried as a caption) and row 1 as a continuation (merged onto
    # 'Ref' -> 'Unit Ref'). The oracle-admitted reading must actually be COMMITTED by
    # compile_tables -- flipping the verdict from escalated to asserted, surviving compile_tables'
    # own full-shape SHACL validation (not just region_tiles' narrower 9-shape subset), and
    # carrying an accountable iladub:PromotionDecision per classified row (never a bare assertion).
    p = os.path.join(str(tmp_path), "caption_wrap.pdf")
    F.caption_wrap_report_pdf(p)
    prop = RowRoleProposal(("furniture", "continuation"), 0.85, "date caption + wrap fragment")
    rep = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))

    assert "asserted" in _verdicts(rep), _reasons(rep)
    asserted_hier = [r for r in rep.regions if r.verdict == "asserted" and r.cells > 0]
    assert asserted_hier, rep.regions

    # An accountable proposition, not a bare assertion (CLAUDE.md §3/§4).
    promotions = list(rep.graph.subjects(RDF.type, ILADUB.PromotionDecision))
    assert promotions, "expected at least one iladub:PromotionDecision in the committed graph"

    # The caption text is CARRIED (never dropped), not silently lost (CLAUDE.md §5/§7).
    captions = list(rep.graph.objects(None, TAB.captionText))
    assert captions, "expected at least one tab:captionText literal"

    # The wrap fragment merged onto its column's leaf label.
    cell_texts = {str(t) for t in rep.graph.objects(None, TAB.cellText)}
    assert "Unit Ref" in cell_texts, cell_texts
