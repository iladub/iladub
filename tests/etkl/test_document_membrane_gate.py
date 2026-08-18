"""Which legs the DOCUMENT membrane runs (R102, plan 2026-08-17 Task 2).

Measured defect: 769 decision holons were minted across the 7 corpus documents and 453 ever
validated — 316 never crossed a membrane at all. Not because they were unshaped
(`dec:DecisionHolonShape` is live, 119 focus nodes on apple) but because `_validate` ran BOTH
legs under one gate, and that gate asks a question about TAB facts: `recognized or
section_facts`. Three corpus documents (ons, bfs, graincorp-capacity) never open it, so their
promotion decisions were governed by nothing but a producer-side guard.

The fix names the legs explicitly (`_legs_for_document`) and takes the `dec` leg out from
behind the tab condition. The tab leg keeps that condition bit-for-bit — ungating dec must not
put the tab shapes onto graphs the gate deliberately excludes (spec §4.1's seam).
"""
import pytest


@pytest.mark.parametrize("recognized,section_facts", [(True, True), (True, False),
                                                      (False, True), (False, False)])
def test_the_dec_leg_is_never_gated_away(recognized, section_facts):
    """R102. 316 of 769 minted decision holons crossed no membrane because the dec leg rode the
    tab-fact condition. The promotion epistemics are not conditional on a document having tables."""
    from iladub.etkl.document import _legs_for_document
    assert "dec" in _legs_for_document(recognized, section_facts)


def test_the_tab_leg_keeps_its_condition_exactly():
    """I-G. Ungating dec must not also put the tab shapes onto graphs the gate excludes — the
    §4.1 seam's specific worry."""
    from iladub.etkl.document import _legs_for_document
    assert _legs_for_document(True, False) == ("tab", "dec")
    assert _legs_for_document(False, True) == ("tab", "dec")
    assert _legs_for_document(True, True) == ("tab", "dec")
    assert _legs_for_document(False, False) == ("dec",)
