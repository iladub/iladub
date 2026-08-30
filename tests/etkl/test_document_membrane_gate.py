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


# ==================================================================== R133: the empty legs tuple

def test_an_empty_legs_tuple_refuses_rather_than_crashing():
    """R133. `_validate(graph, legs=())` used to raise `IndexError: tuple index out of range` at
    `compile.py:523` — `verdicts` is empty, so `refusing` is empty, so the conforming branch is
    taken and indexes `legs[0]` on an empty tuple. The membrane's own entry point CRASHED.

    THE DECISION, which the row (R133) left open and this test pins: a zero-leg validation
    REFUSES. It does not conform. A validation that checked nothing and returned True is failing
    upward — CLAUDE.md § Core design principles 7 ("only emit what the source supports")
    forbids exactly that, and the row says `Prefer refuse`.
    """
    from rdflib import Graph
    from iladub.etkl.compile import _validate
    conforms, text, refusing = _validate(Graph(), legs=())
    assert conforms is False
    assert refusing == ()
    assert "no membrane leg" in text


def test_legs_for_document_never_returns_an_empty_tuple():
    """R133's DEFERRAL RATIONALE, re-measured rather than carried forward.

    The row deferred the fix on the ground that `legs=()` is unreachable because one total
    function supplies every legs tuple the tree ever builds. The 2026-08-29 handoff recorded
    that `_legs_for_document`'s returns had NOT been re-enumerated. They are, here: the function
    is total over its two boolean arguments and neither branch is empty. The rationale holds —
    which is why the fix above is a repair of a crash the membrane must not have, not a bug fix
    for a reachable path.
    """
    from iladub.etkl.document import _legs_for_document
    for recognized in (True, False):
        for section_facts in (True, False):
            assert _legs_for_document(recognized, section_facts) != ()
