"""R334 + R336 on Fed H.4.1 p0, as shipped (spec 2026-10-24 §5 item 6, amended by the maintainer's
SHIP AS IS decision of 2026-10-24, recorded in the loop's SDD ledger).

The spec predicted p0 would adopt once its spanners and its caption lines were carried, escalating
27 tokens against the bands' 31. The spanners are carried (Task 2). The caption worker's recorded
answer on p0 is lines {1, 5, 6}: the masthead release number "H.4.1", the title, and "Millions of
dollars". That set is not one contiguous run ending at the labels, so the disposal refuses it (NO
CLAIM), the caption lines stay unread, the ledger books 38 > 31, and the page does not adopt.

These tests pin that state AND its cause:

- with the recording as committed, p0's adoption is `ledger_refused` at 31 escalated tokens;
- with ONLY that one recording replaced by {5, 6} (a scratch copy of `readings/caption/`, patched in
  through `caption.READINGS_DIR`), p0 adopts at 27 — the spec's prediction, exactly. So the caption
  answer is the one remaining blocker, and nothing else in the loop's carriage is.

Page scope (`compile_tables(..., datagrid_adopt=True)`), ~15 s per compile; the document's adopted
set, which excludes 0, is pinned by `tests/test_r301_fed_h41.py`.
"""
import json
import os
import shutil

import pytest
from rdflib.namespace import RDF

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FED = os.path.join(ROOT, "held-out", "fed-h41-2025-01-02.pdf")
P0_CAPTION_KEY = "e33c186e3654d25c2eb56b438c67e29f67e23b4c7eb646b1a9ea67777ac65a82"

pytestmark = [
    pytest.mark.corpus,
    pytest.mark.skipif(not os.path.exists(FED), reason="held-out/fed-h41 absent (gitignored corpus)"),
]


def _p0():
    from iladub.etkl.compile import compile_tables
    return compile_tables(FED, 0, validate_shapes=True, datagrid_adopt=True)


def test_the_recorded_caption_answer_is_the_non_contiguous_one():
    """The premise of the two tests below: the committed recording is {1, 5, 6}, not refused."""
    from iladub.etkl import caption
    d = json.loads((caption.READINGS_DIR / f"{P0_CAPTION_KEY}.json").read_text(encoding="utf-8"))
    assert d["caption_lines"] == [1, 5, 6] and d["refuses"] is False


def test_p0_does_not_adopt_with_the_recorded_caption_answer():
    rep = _p0()
    assert rep.adoption == "ledger_refused"
    assert (rep.asserted, rep.escalated) == (285, 31)


def test_p0_adopts_when_only_its_caption_answer_is_contiguous(tmp_path, monkeypatch):
    """Positive control: the same compile, with one recording changed to {5, 6}, adopts at 27."""
    from iladub.etkl import caption
    from iladub.etkl.holon import TAB
    copy = tmp_path / "caption"
    shutil.copytree(caption.READINGS_DIR, copy)
    path = copy / f"{P0_CAPTION_KEY}.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    d["caption_lines"] = [5, 6]
    path.write_text(json.dumps(d), encoding="utf-8")
    monkeypatch.setattr(caption, "READINGS_DIR", copy)

    rep = _p0()
    assert rep.adoption == "adopted"
    assert (rep.asserted, rep.escalated) == (336, 27)
    caps = {str(rep.graph.value(c, TAB.captionText))
            for c in rep.graph.subjects(RDF.type, TAB.RegionCaption)}
    assert caps == {"1. Factors Affecting Reserve Balances of Depository Institutions",
                    "Millions of dollars"}
    # RegionCaption only, never SectionCaption (Global Constraints).
    assert not list(rep.graph.subjects(RDF.type, TAB.SectionCaption))
