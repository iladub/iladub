"""The cockpit gauge strip — `scripts/cockpit.py`.

Two of these tests pin ROBUSTNESS (a status line that raises is worse than no status line) and
one pins an HONEST UNKNOWN, which is the unusual one and the reason this file exists: the `arc`
gauge must render `?` when nothing can tell it otherwise, because a fabricated fact on a dashboard
is worse than the blindness it replaced.

**The arc gauge shows numbers now, and that changed nothing about the refusal.** It reads them from
`tests/arc-manifest.ttl` — hand-authored, membrane-validated, never written by code. Take that file
away and every rung goes back to `?` with no digit on the line, which is what the honesty test
asserts. The rule was never "the arc must say `?`"; it was "the arc must not say a number that no
source supports", and those coincided only for as long as no source existed.

Two tests are AGREEMENT tests, and they are what the manifest made necessary: the strip may not
import rdflib, so it reads the manifest with a regex, and a second reader of one fact needs a pin
saying it agrees with the first. They run `vocab/queries/arc-{position,frontier,unblocked}.rq` and
demand the strip match. If they ever disagree, rdflib is right.
"""
import os
import re
import subprocess
import sys

import pytest

from scripts import cockpit


def _strip(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


def _query(name: str) -> str:
    with open(os.path.join(cockpit.ROOT, "vocab", "queries", name), encoding="utf-8") as fh:
        return fh.read()


def test_the_strips_reading_equals_rdflibs_reading_of_the_same_file():
    """THE STRIP AND THE GRAPH MUST COUNT THE SAME THING, and this is the only thing that says so.

    `scripts/cockpit.py` may not import rdflib (its performance contract, `cockpit.py:76-80`),
    so it reads `tests/arc-manifest.ttl` with a regex — a SECOND reader of a fact whose reader of
    record is `vocab/queries/arc-position.rq`. Two readers of one fact is a defect generator: the
    `residues()` regex once went blind to every struck tally snapshot and nothing noticed for a
    day. This test is the pin that makes the second reader safe: it parses the manifest properly,
    runs the derivation of record, and demands the strip agree EXACTLY.

    It may use rdflib — it is a test, not the strip.

    The mapping between the two shapes is decision 6 and is not a fudge: `arc-position.rq` INNER
    joins on the criterion, so a rung with no criteria yields NO ROW; `arc()` renders that same
    rung as `(None, None)` so the strip can print `?`. Unknown is not zero, on both sides.
    """
    from rdflib import RDF, Graph, Namespace

    prog = Namespace("https://w3id.org/iladub/progress#")
    g = Graph()
    g.parse(cockpit.ARC_MANIFEST, format="turtle")
    rows = {str(r[0]): (int(r[1]), int(r[2])) for r in g.query(_query("arc-position.rq"))}

    assert rows, "arc-position.rq returned nothing; the manifest or the query moved"
    assert set(rows) <= set(cockpit.RUNGS), (
        f"rdflib sees rungs the strip cannot display: {sorted(set(rows) - set(cockpit.RUNGS))}. "
        "M6 pins the five keys; if a sixth rung was added, the spec forbids it (§9)")

    expected = [(key, *rows.get(key, (None, None))) for key in cockpit.RUNGS]
    assert cockpit.arc() == expected, (
        "the regex reader and rdflib disagree about the arc. rdflib is right and the regex is "
        "wrong — fix `arc()`, never the manifest")

    # And no criterion may fall between the two readers. Both would silently drop a criterion
    # whose rung key names no `prog:Rung` node, so neither the equality above nor the query
    # would notice it; the typed-node count is the independent denominator that does.
    typed = len(set(g.subjects(RDF.type, prog.Criterion)))
    assert sum(d for _, _, d in cockpit.arc() if d is not None) == typed, (
        f"{typed} criteria are typed in the manifest but the strip counted a different number")


def test_the_frontier_and_ready_counts_equal_the_derivations_of_record():
    """`frontier_counts()` is a second reader too, and gets exactly the same treatment as `arc()`.
    Without this pin the two most actionable figures on the strip — how much of the arc is waiting
    on the register, and how much is waiting on nobody — would be regex output that no derivation
    ever checked.

    **`ready`** is `arc-unblocked.rq`'s row count, unchanged: one unmet criterion naming no
    blocker is one piece of work that is ready and is not being done.

    **`frontier`** is deliberately NOT `arc-frontier.rq`'s row count. That query emits one row per
    `(residue, rung, criterion)` EDGE, and the figure a reader can act on is how many REGISTER ROWS
    stand in the way — R44 blocking three criteria is one row to close, not three. So the strip
    counts the distinct `?residue` column, and this test derives the same set from the query rather
    than restating a number, which would go stale the day an edge is authored."""
    from rdflib import Graph

    g = Graph()
    g.parse(cockpit.ARC_MANIFEST, format="turtle")
    residues = {str(r[0]) for r in g.query(_query("arc-frontier.rq"))}
    unblocked = list(g.query(_query("arc-unblocked.rq")))

    assert residues and unblocked, "the frontier queries returned nothing; the manifest moved"
    assert cockpit.frontier_counts() == (len(residues), len(unblocked)), (
        f"the strip says {cockpit.frontier_counts()}; the derivations say "
        f"({len(residues)}, {len(unblocked)}). The queries are right and the regex is wrong")


def test_the_arc_gauge_reports_unknown_and_must_not_guess(monkeypatch, tmp_path):
    """THE REFUSAL SURVIVED THE MANIFEST. This test used to pin `pos is None` and `stage ?/` in the
    render, because `docs/narrative/scope-evolution.md` named the stages and recorded NO state, so
    no source in the repo could say which rung was current. `tests/arc-manifest.ttl` now supplies
    that state and both literals are gone with it — but the SUBSTANCE they protected has not moved
    one inch, and it is this: **a missing source yields `?`, and never a number.**

    So the test now takes the source away. Point `cockpit.ARC_MANIFEST` at a file that is not
    there and every rung must read `?`, with no digit anywhere on the arc line — no `0`, no `0/0`,
    no bar. `0/5` would be the exact fabrication this test has always existed to refuse: it claims
    somebody counted five things and found none of them done, when in fact nobody counted at all.

    The warning that is the reason this test exists, kept verbatim: If this test starts failing
    because the position is a number, the right question is 'what artifact told it that?' — not
    'how do we make the test pass'."""
    monkeypatch.setattr(cockpit, "ARC_MANIFEST", str(tmp_path / "absent.ttl"))
    rungs = cockpit.arc()
    assert rungs, "the arc gauge went silent instead of reporting unknown"
    for key, met, declared in rungs:
        assert met is None and declared is None, (
            f"with no manifest on disk the strip claims {key} is {met}/{declared}. If a new source "
            "supplies that, name it here. If it did not, this is a fabricated figure")

    arc_line = _strip(cockpit.render(color=False)).splitlines()[1]
    for key, _met, _declared in rungs:
        assert f"{key} ?" in arc_line, f"{key} does not read `?` on {arc_line!r}"
    assert not re.search(r"\d", arc_line), (
        f"a digit reached the arc line with no manifest behind it: {arc_line!r}")


def test_the_strip_never_raises_when_its_sources_are_missing(monkeypatch, tmp_path):
    """The status line re-renders constantly and runs against whatever is on disk, including a
    half-finished rebase or a fresh clone with no `.git`. It must degrade, never raise."""
    for attr in ("INDEX", "CLOSED", "ARC_MANIFEST"):
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


def test_it_exits_zero_and_prints_two_lines_with_stdin_attached():
    """Claude Code pipes session JSON in and reads the strip out. THIS PIN WAS ONE LINE AND IS NOW
    TWO — a deliberate relaxation, and here is the evidence a reviewer needs to judge it.

    WHAT IS DOCUMENTED: a multi-line `statusLine` is supported, and each printed line displays as
    a separate row. WHAT IS NOT: any limit on the number of rows, and whether an over-long row
    wraps or is truncated. ALSO KNOWN: multi-line output combined with ANSI colour is reported as
    glitch-prone. So the second line is taken on documented support, with two of the three
    questions that matter unanswered — which is exactly why it is pinned here rather than assumed.

    WHY THE RELAXATION IS NOT A WEAKENING. `1` was never the property under test; `all of it` was.
    A one-line assertion on a two-line strip would pass while the arc silently vanished, so the
    equality is re-pinned at 2 rather than loosened to `>= 1`. Ask for exactly what you expect.

    IF IT BREAKS IN PRACTICE — rows dropped, wrapped, or garbled by colour — the fallback is the
    compact SINGLE-line form with the fractions moved behind `--verbose`. It is **never** to
    abbreviate the rung names to make five fractions fit (decision 8): `etkl 1/7` is a figure a
    reader acts on and `e 1/7` is one they have to decode, and a status line nobody can read at a
    glance has lost the only argument it had over a document you go and open."""
    p = subprocess.run([sys.executable, "scripts/cockpit.py", "--no-color", "--refresh"],
                       input='{"session":"x"}', capture_output=True, text=True, timeout=20)
    assert p.returncode == 0, p.stderr
    lines = p.stdout.strip().splitlines()
    assert len(lines) == 2, f"the strip is a two-line render; got {len(lines)}: {lines}"
    assert lines[1].startswith("arc "), (
        f"the second row must be the arc line, or the first row grew a newline: {lines[1]!r}")


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
