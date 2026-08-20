"""The cockpit gauge strip — `scripts/cockpit.py`.

Two of these tests pin ROBUSTNESS (a status line that raises is worse than no status line) and
one pins an HONEST UNKNOWN, which is the unusual one and the reason this file exists: the `arc`
gauge must render `?`. It is the only gauge whose correct value today is "nobody knows", and the
obvious future "improvement" is to make it show a number by inferring a position. That would be
a fabricated fact on a dashboard, which is worse than the blindness it replaced.
"""
import re
import subprocess
import sys

import pytest

from scripts import cockpit


def _strip(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


def test_the_arc_gauge_reports_unknown_and_must_not_guess():
    """`docs/narrative/scope-evolution.md` names the stages and records NO state, so no source in
    the repo can say which one is current. Until an objectives artifact carries state, `?` is the
    only honest render. If this test starts failing because the position is a number, the right
    question is 'what artifact told it that?' — not 'how do we make the test pass'."""
    pos, stages = cockpit.arc()
    assert pos is None, (
        f"the arc gauge now claims position {pos}. If an objectives artifact gained state, update "
        "this test and say which artifact supplies it. If it did not, this is a fabricated figure")
    assert stages >= 1
    assert "stage ?/" in _strip(cockpit.render(color=False)), (
        "the gauge is labelled `stage N/4 of the arc`; if the label changed, keep the `?`")


def test_the_strip_never_raises_when_its_sources_are_missing(monkeypatch, tmp_path):
    """The status line re-renders constantly and runs against whatever is on disk, including a
    half-finished rebase or a fresh clone with no `.git`. It must degrade, never raise."""
    for attr in ("INDEX", "CLOSED", "ARC"):
        monkeypatch.setattr(cockpit, attr, str(tmp_path / "absent.md"))
    out = _strip(cockpit.render(color=False))
    assert "res" in out and "0/0" in out


def test_the_figures_match_the_register_itself():
    """The gauge must not carry its own copy of the tally — it reads the register."""
    closed, total, _delta = cockpit.residues()
    text = open(cockpit.INDEX, encoding="utf-8").read()
    assert total == len(re.findall(r"^\| R\d+ \|", text, re.M))
    assert closed == len(re.findall(r"^\| R\d+ \| closed \|", text, re.M))
    assert 0 < closed < total


def test_it_exits_zero_and_prints_one_line_with_stdin_attached():
    """Claude Code pipes session JSON in and reads one line out."""
    p = subprocess.run([sys.executable, "scripts/cockpit.py", "--no-color", "--refresh"],
                       input='{"session":"x"}', capture_output=True, text=True, timeout=20)
    assert p.returncode == 0, p.stderr
    assert len(p.stdout.strip().splitlines()) == 1


def test_no_stuck_verdict_is_computed_anywhere():
    """CLAUDE.md §8: 'are we stuck' is a judgment, and a tuned threshold deciding it in procedural
    code is the defect the gate exists to catch. The strip reports raw counts and refuses the
    verdict. This pins the refusal.

    It inspects the CODE, not the source text — the first version of this test matched raw
    characters and failed on `cockpit.py`'s own docstring, which quotes `return "STUCK"` as the
    example of what not to write. A checker that cannot tell an explanation from an instance is
    checking prose, not behaviour.

    Colour thresholds ARE allowed and deliberately not caught here: they colour a number the
    reader still reads, they do not replace it with a verdict."""
    import ast

    tree = ast.parse(open("scripts/cockpit.py", encoding="utf-8").read())
    verdicts = {"stuck", "stalled", "blocked", "ok", "healthy", "converging"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert node.value.strip().lower() not in verdicts, (
                f"cockpit.py now emits the verdict {node.value!r} as a value")
        if isinstance(node, ast.Name):
            assert node.id not in ("is_stuck", "velocity_index", "health_score"), (
                f"cockpit.py now computes {node.id}")

    out = _strip(cockpit.render(color=False)).lower()
    assert not (verdicts & set(re.findall(r"[a-z]+", out))), (
        f"a verdict word reached the rendered strip: {out}")


def _register(tmp_path, monkeypatch, *, index: str, closed: str = "", open_: str = ""):
    """Point the strip at a synthetic register. The three files are the gauge's only inputs."""
    paths = {"INDEX": index, "CLOSED": closed, "OPEN": open_}
    for attr, text in paths.items():
        f = tmp_path / f"{attr.lower()}.md"
        f.write_text(text, encoding="utf-8")
        monkeypatch.setattr(cockpit, attr, str(f))


_INDEX_4 = ("| R1 | closed | x |\n| R2 | closed | x |\n"
            "| R3 | open | x |\n| R4 | open | x |\n")


def test_a_struck_row_still_counts_as_a_tally_snapshot(tmp_path, monkeypatch):
    """A residue's snapshot is recorded at RAISE time and never updated; closing the row strikes
    its number to `~~R104~~` but does NOT invalidate the measurement in the same cell. A reader
    that only sees unstruck rows goes blind to every snapshot the moment its row closes — which
    is most of them, since the register's convention is to close rows, not delete them."""
    _register(tmp_path, monkeypatch, index=_INDEX_4,
              closed="| ~~R104~~ (18/94 closed) | closed | x |\n")
    _c, _t, delta = cockpit.residues()
    assert delta is not None, "the only snapshot in the register was struck, and was not read"


def test_the_newest_snapshot_wins_even_when_it_is_the_struck_one(tmp_path, monkeypatch):
    """The trend is measured against the NEWEST snapshot, wherever it lives. R104 sits in the
    closed file and R101 in the open one; reading only the open file silently measures the trend
    against a staler baseline and reports a smaller movement than the register supports."""
    _register(tmp_path, monkeypatch, index=_INDEX_4,
              closed="| ~~R104~~ (18/94 closed) | closed | x |\n",
              open_="| R101 (18/91 closed) | open | x |\n")
    _c, _t, delta = cockpit.residues()
    assert delta == pytest.approx(50.0 - 18 / 94 * 100, abs=0.01), (
        "the trend was measured against R101 (18/91), not the newer R104 (18/94)")


def test_the_raised_at_wording_is_read_too(tmp_path, monkeypatch):
    """Both wordings are in the register: `(18/94 closed)` and `(raised at 18/93 closed)`."""
    _register(tmp_path, monkeypatch, index=_INDEX_4,
              closed="| ~~R103~~ (raised at 18/93 closed) | closed | x |\n")
    _c, _t, delta = cockpit.residues()
    assert delta == pytest.approx(50.0 - 18 / 93 * 100, abs=0.01)


def test_the_work_line_renders_the_declared_topic(monkeypatch, tmp_path):
    """`topic · subject · branch` — the maintainer's ask. The topic is read from the newest
    brief/handoff's `**Topic:**` field, so it travels with the dated document that a new loop
    replaces, rather than living in a config nobody revisits."""
    doc = tmp_path / "2026-08-20-a-loop-handoff.md"
    doc.write_text("# t\n\n**Topic:** etkl · **Date:** 2026-08-20 ·\n", encoding="utf-8")
    monkeypatch.setattr(cockpit, "_newest_loop_doc", lambda: str(doc))
    monkeypatch.setattr(cockpit, "_run", lambda *a: "a-branch\n")
    assert cockpit.topic() == "etkl"
    assert cockpit.work() == "etkl \u00b7 a-loop \u00b7 a-branch"


def test_a_document_that_declares_no_topic_gets_no_topic_invented(monkeypatch, tmp_path):
    """The topic is the one AUTHORED figure on the strip and therefore the only one that could be
    wrong without anything noticing. The compensating rule is that silence stays silent: a handoff
    with no `**Topic:**` drops the segment rather than reusing a previous loop's topic or falling
    back to a default. A stale topic would be worse than none — it is the failure the `stage` gauge
    two segments over exists to refuse."""
    doc = tmp_path / "2026-08-20-a-loop-brief.md"
    doc.write_text("# t\n\n**Date:** 2026-08-20 · **Shape: originating** ·\n", encoding="utf-8")
    monkeypatch.setattr(cockpit, "_newest_loop_doc", lambda: str(doc))
    monkeypatch.setattr(cockpit, "_run", lambda *a: "a-branch\n")
    assert cockpit.topic() is None
    assert cockpit.work() == "a-loop \u00b7 a-branch"


def test_the_work_line_degrades_on_a_detached_head(monkeypatch):
    """A rebase or a bisect leaves HEAD detached. The subject still holds; the branch half drops."""
    monkeypatch.setattr(cockpit, "topic", lambda: None)
    monkeypatch.setattr(cockpit, "entry_point", lambda: "some-loop")
    monkeypatch.setattr(cockpit, "_run", lambda *a: "HEAD\n")
    assert cockpit.work() == "some-loop"
    monkeypatch.setattr(cockpit, "_run", lambda *a: "")
    assert cockpit.work() == "some-loop"


def test_the_live_newest_handoff_declares_a_topic():
    """The convention only works if loop documents actually carry the field. This is the live-repo
    half: whatever a fresh session would open right now must say what topic it belongs to."""
    path = cockpit._newest_loop_doc()
    assert path is not None, "no dated brief/handoff on disk"
    assert cockpit.topic() is not None, (
        f"{path} declares no `**Topic:**`, so the strip cannot say what we are working on")
