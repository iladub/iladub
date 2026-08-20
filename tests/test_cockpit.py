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
    assert "arc ?/" in _strip(cockpit.render(color=False))


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
