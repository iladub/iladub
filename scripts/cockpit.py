#!/usr/bin/env python3
"""cockpit — the one-line gauge strip for the Claude Code status line.

WHY THIS EXISTS. Raised by the maintainer 2026-08-20: *"I am a bit lost … I have no notion of how
complete is the topic/epic we are working on and also the rhythm at which we are really making
progress … Here I am blind."* Then, precisely: *"a line of indicators/gauges"*, always visible,
like the context gauge — not a document to go and open.

WHAT IT SHOWS, and every figure is computed from a committed source, never stored:

    res  ▰▰▱▱▱▱▱▱  21/94   the residue register: closed / total, with the trend arrow against the
                           last tally snapshot recorded in the register itself
    7d   ⊕9 ⊖9             raised / closed over the trailing 7 days — the velocity, as two numbers
                           rather than one index, DELIBERATELY (see § the tuned-constant trap)
    idle 0d                days since the last close. The stuck signal, unthresholded
    ▸    <loop>            the current entry point, read from the newest handoff/brief on disk

and, on a SECOND LINE, the arc — the thing this strip could not say until the manifest existed:

    arc  etkl ▰▱▱▱ 1/7 …   one fraction per rung of the strategy arc, counted from
                           `tests/arc-manifest.ttl`: criteria asserted met over criteria declared.
                           **The fraction sits beside every bar** because a bar reads as a
                           percentage and these are checklists — 1/7 and 14/98 are not the same
                           news. A rung with NO criteria renders `?`, never an empty bar and never
                           `0`: unknown is not zero, and that refusal is the whole point
    frontier 15 ready 17   register rows that block an unmet criterion (how much of the arc is
                           waiting on the register), and unmet criteria that name NO blocker —
                           *work that is ready and is not being done*. Two counts, never a ranking

THE `?/4` THIS REPLACES was the honest answer for as long as it was true: `scope-evolution.md`
named the stages and recorded no state, so nothing in the repo could say which rung we were on,
and the gauge refused to guess. It is a number now for one reason only — a hand-authored,
membrane-validated denominator was written (`tests/arc-manifest.ttl`, spec 2026-08-20). The
refusal has NOT been relaxed: point this at a manifest that is not there and every rung reads `?`
again. Do not make any rung render a number that no criterion in that file supports.

§ TWO READERS OF ONE FACT, and the test that makes that safe. The reader of RECORD for the arc is
`vocab/queries/arc-position.rq` (AXIOM / derivation, open world). This file cannot run it — the
performance contract below forbids rdflib — so it reads the same manifest with a regex, which is
a second reader and therefore a defect generator. What licenses it is M9/M9b in
`tests/arc-shapes.ttl`: the membrane REFUSES a criterion that is not a top-level IRI subject, and
refuses one whose IRI and `prog:ofRung` disagree, so the fast reader and the query are reading the
same fact by the same key. What PROVES it is
`tests/test_cockpit.py::test_the_strips_reading_equals_rdflibs_reading_of_the_same_file`, which
runs both and demands they agree exactly. If they ever diverge, rdflib is right.

§ THE TUNED-CONSTANT TRAP, and why there is no "velocity index" here. CLAUDE.md §8 forbids a
procedural decision with a tuned constant. "Are we stuck?" is exactly such a judgment, and
`if velocity < 0.3: return "STUCK"` would be the defect the gate exists to catch. So this strip
reports the two raw counts and the idle days and refuses to collapse them into a verdict — the
reader disposes. The arc line is held to the same rule: `frontier` and `ready` are two counts and
never a ranking of which residue to close, because that is a judgment.

Colour thresholds exist — on `res` (the register's own published tally convention) and on each
arc fraction, at the same two cut points — and they COLOUR, they do not decide. The test of that
is direct: run with `--no-color` and not one figure changes, because every number the colour
comments on is printed in full beside it. A threshold that replaced `1/7` with a word would be
the defect; one that tints `1/7` red is a reading aid.

Gate classification (CLAUDE.md §8): PROCEDURAL reporting harness, and irreducible for the usual
reason — it is string formatting and date arithmetic over files, making no domain decision. It
derives nothing about the graph and validates nothing. The one judgment it might have made
(stuck / not stuck) is the one it deliberately declines to make.

That classification carries over to `arc()` and `frontier_counts()` unchanged, and the reason is
worth stating because they read a graph: they DECIDE nothing about it. `prog:met` is hand-asserted
in a reviewed commit and validated by a closed-world membrane; these functions read that boolean
and TALLY it. They never write the manifest (spec §9), never infer a criterion's met-ness from
anything, and never rank, order or score a rung — the `frontier` and `ready` figures are two
counts precisely so that "what should we do next" stays the reader's judgment. The only decision
in the neighbourhood — *is this criterion met* — is made by a human and refused by SHACL, which
is where the gate says it belongs. The display order of the rungs is a DISPLAY order and no claim
of sequence: the manifest asserts no `prog:precedes` and `tab` is depth inside `etkl`, not a stage
after `substrate`.

PERFORMANCE CONTRACT. The status line re-renders constantly, so this must never be slow and must
never touch the network, rdflib, pytest or the corpus. It reads four small text files and runs at
most two `git log` calls, then caches the rendered strip for `_TTL` seconds. A cache miss is a few
milliseconds; a hit is a single file read. If it ever raises, it prints nothing rather than
breaking the status line.

Usage:  cockpit.py            # print the strip
        cockpit.py --no-color # plain text, for piping or tests
        cockpit.py --refresh  # ignore the cache
Claude Code passes session JSON on stdin; it is read and discarded.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "docs", "superpowers", "residues.md")
CLOSED = os.path.join(ROOT, "docs", "superpowers", "residues-closed.md")
OPEN = os.path.join(ROOT, "docs", "superpowers", "residues-open.md")
ARC_MANIFEST = os.path.join(ROOT, "tests", "arc-manifest.ttl")
CACHE = os.path.join(ROOT, ".git", "cockpit-cache.json")   # inside .git: never tracked
_TTL = 180
_WINDOW = 7

# DISPLAY order, and nothing more. The manifest deliberately asserts no ordering between rungs
# (no `prog:precedes`, no index property) because there is none: `tab` is depth inside `etkl`,
# not a stage after `substrate`. This tuple decides what the eye reads left-to-right and is not
# evidence of a sequence. It is also the closed list M6 admits — a sixth rung is a spec change
# (§9), and the agreement test fails loudly if the manifest grows one behind this file's back.
RUNGS = ("etkl", "dec", "holon", "tab", "substrate")

C = dict(dim="\033[2m", off="\033[0m", bold="\033[1m",
         good="\033[38;5;71m", warn="\033[38;5;179m", bad="\033[38;5;167m",
         cool="\033[38;5;110m", mute="\033[38;5;245m")


def _plain(_k: str) -> str:
    return ""


def _run(*args: str) -> str:
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                              timeout=3).stdout
    except Exception:
        return ""


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def residues() -> tuple[int, int, float | None]:
    """(closed, total, delta-in-points-vs-the-last-snapshot). The snapshots are the register's
    own convention — `R97 (18/87 closed)` — recorded at raise time and never updated, so reading
    the newest one gives the trend without this script storing any state of its own.

    The `~*` is load-bearing: closing a row STRIKES its number (`~~R104~~ (18/94 closed)`) without
    touching the measurement in the same cell. The first version of this pattern required the digits
    to be followed by a space, so every snapshot went invisible the moment its row closed — which is
    most of them, the register being a record of closures. Measured 2026-08-20: 6 of 13 snapshots
    lost, and the trend reported ▲2.6 against R101 where R104 gives ▲3.19."""
    idx = _read(INDEX)
    total = len(re.findall(r"^\| R\d+ \|", idx, re.M))
    closed = len(re.findall(r"^\| R\d+ \| closed \|", idx, re.M))
    snaps = re.findall(r"R(\d+)~*\s+\((?:raised at )?(\d+)/(\d+) closed\)",
                       _read(CLOSED) + _read(OPEN))
    delta = None
    if snaps and total:
        _r, c, t = max(snaps, key=lambda s: int(s[0]))
        if int(t):
            delta = closed / total * 100 - int(c) / int(t) * 100
    return closed, total, delta


def velocity() -> tuple[int, int, int | None]:
    """(raised, closed, days-since-last-close) over the trailing window.

    `closed` is counted from the `CLOSED <date>` stamps the closing convention already writes.
    `raised` is the GROWTH IN ROW COUNT over the window, taken from git rather than from any
    date stamp — rows carry no raise date, and inventing one would be a fact this script made up."""
    today = _dt.date.today()
    dates = [_dt.date.fromisoformat(d)
             for d in re.findall(r"CLOSED (\d{4}-\d{2}-\d{2})", _read(CLOSED))]
    closed = sum(1 for d in dates if (today - d).days < _WINDOW)
    idle = (today - max(dates)).days if dates else None

    raised = 0
    since = _run("git", "log", f"--since={_WINDOW}.days", "--reverse",
                 "--format=%H", "--", "docs/superpowers/residues.md").split()
    if since:
        old = _run("git", "show", f"{since[0]}^:docs/superpowers/residues.md")
        if old:
            raised = max(0, len(re.findall(r"^\| R\d+ \|", _read(INDEX), re.M))
                         - len(re.findall(r"^\| R\d+ \|", old, re.M)))
    return raised, closed, idle


# A criterion block, as the membrane guarantees it. M9 (`tests/arc-shapes.ttl:63-66`) refuses a
# criterion that is not a top-level IRI subject and M9b (:139-146) refuses one whose IRI and
# `prog:ofRung` disagree, so the rung key is readable off the SUBJECT LINE and a regex is a sound
# reader of this file. Anchored at column 0: the rung's own `prog:criterion` index lists the same
# IRIs indented, and matching those would double every count.
_CRITERION = re.compile(r"^prog:criterion:([A-Za-z0-9_-]+):[A-Za-z0-9_.-]+\s+a\s+prog:Criterion\b")
# `\s+` after `prog:met` is what keeps `prog:metOn` out: 17 of the manifest's 60 `prog:met`
# occurrences are that longer predicate, and a prefix match would read a date as a boolean.
_MET = re.compile(r"^\s+prog:met\s+(true|false)\s*[;.]\s*$")
_BLOCKING = re.compile(r"^\s+prog:blockedBy\s")
_LITERAL = re.compile(r'"([^"]*)"')


def _criteria() -> list[tuple[str, bool, tuple[str, ...]]]:
    """Every criterion in the manifest as `(rungKey, met, blocking-register-rows)`.

    A block runs from its top-level subject line to the first line ending in `.` — Turtle's own
    statement terminator, which is a STRUCTURAL boundary rather than a guess about the file's
    layout: every predicate line inside a block ends in `;`, and the manifest carries no
    triple-quoted literal (measured 2026-08-21: 0 occurrences of `\"\"\"`), so no `.` can end a
    line from inside a string. That terminator is why a comment block between two criteria —
    and this file has many, several of them quoting `prog:met` in prose — cannot leak into a
    count: it falls outside every block.

    Returns `[]` when the manifest is absent, which is how a missing source becomes `?` rather
    than a zero."""
    out: list[tuple[str, bool, tuple[str, ...]]] = []
    rung: str | None = None
    met: bool | None = None
    rows: list[str] = []
    for line in _read(ARC_MANIFEST).splitlines():
        head = _CRITERION.match(line)
        if head:
            rung, met, rows = head.group(1), None, []
        elif rung is None:
            continue
        m = _MET.match(line)
        if m:
            met = m.group(1) == "true"
        elif _BLOCKING.match(line):
            rows.extend(_LITERAL.findall(line))
        if line.rstrip().endswith("."):
            if met is not None:          # a criterion with no asserted prog:met is counted in
                out.append((rung, met, tuple(rows)))   # NEITHER column, as arc-position.rq does
            rung = None
    return out


def arc() -> list[tuple[str, int | None, int | None]]:
    """`(rungKey, met, declared)` per rung, in `RUNGS` display order.

    **`(None, None)` for a rung with no criteria, and that is not a zero.** It is decision 6 and
    the same reading `vocab/queries/arc-position.rq` gives by inner-joining the criterion: a rung
    nobody has authored criteria for produces no row there and prints `?` here. A rung with no
    criteria is not a refusal, it is an unanswered question, and rendering it `0/0` — or worse,
    `0` — would be a fabricated fact on a dashboard."""
    tally: dict[str, list[int]] = {}
    for rung, met, _rows in _criteria():
        cell = tally.setdefault(rung, [0, 0])
        cell[0] += 1
        cell[1] += 1 if met else 0
    return [(key, tally[key][1], tally[key][0]) if key in tally else (key, None, None)
            for key in RUNGS]


def frontier_counts() -> tuple[int | None, int | None]:
    """`(frontier, ready)` — the two counts that say where the work is, and neither is a verdict.

    **`(None, None)` when the manifest is not readable**, for the same reason `arc()` returns
    `(None, None)` per rung: `frontier 0 · ready 0` off an absent file asserts *nothing blocks the
    arc and no work is waiting*, which is the most flattering sentence on the strip and would be
    made up. The plan specified `tuple[int, int]` here; that signature cannot express the honest
    answer, so it is widened — the refusal outranks the type.

    **frontier** is the number of DISTINCT register rows named by a `prog:blockedBy` on an unmet
    criterion: how much of the arc is waiting on the residue register. It is a set, not a bag —
    naming R44 from three criteria is one row to close, not three.

    **ready** is the number of unmet criteria that name NO blocker at all: *work that is ready and
    is not being done*, which is `vocab/queries/arc-unblocked.rq`'s question and the one the
    maintainer's original complaint most directly asks.

    They are reported as two numbers and never combined, ranked or ordered — deciding which
    residue to close next is a judgment, and this strip does not make judgments (see § the
    tuned-constant trap)."""
    criteria = _criteria()
    if not criteria:
        return None, None
    waiting: set[str] = set()
    ready = 0
    for rung, met, rows in criteria:
        if met or rung not in RUNGS:
            continue
        if rows:
            waiting.update(rows)
        else:
            ready += 1
    return len(waiting), ready


def _newest_loop_doc() -> str | None:
    """The newest brief/handoff on disk — the thing a fresh session would open. Filenames are
    ISO-dated, so `max()` on the name is `max()` on the date."""
    d = os.path.join(ROOT, "docs", "superpowers")
    try:
        names = [f for f in os.listdir(d) if re.match(r"\d{4}-\d{2}-\d{2}-.*\.md$", f)
                 and ("handoff" in f or "brief" in f)]
    except OSError:
        return None
    return os.path.join(d, max(names)) if names else None


def entry_point() -> str:
    path = _newest_loop_doc()
    if path is None:
        return "?"
    # the suffix alternatives must carry `.md` with them: anchored at `$`, `-handoff$` can never
    # match while the extension is still there. The original pattern listed them separately and so
    # stripped neither — the strip read `strategy-instrument-handoff` for as long as it existed.
    return re.sub(r"^\d{4}-\d{2}-\d{2}-|(?:-handoff|-brief)?\.md$", "",
                  os.path.basename(path))[:28]


def topic() -> str | None:
    """The `**Topic:**` field of the newest brief/handoff, or None if it does not declare one.

    **This is the one AUTHORED figure on the strip, and it is the weakest.** Everything else here
    is counted or read from git. A topic is prose: whoever writes the handoff can write anything,
    and nothing checks it against the work. It was chosen with that known — the alternatives were a
    hand-tuned path→topic table (a tuned constant by another name) or waiting for the objectives
    artifact — and it is bounded by the one property that saves it: it lives in a DATED file that a
    new loop replaces, so it cannot outlive the work the way a marker in `settings.json` would.

    What would strengthen it: doc-governance already lints tracked markdown, so a rule requiring
    every dated brief/handoff to declare a topic drawn from a named set would make this checked
    rather than merely conventional. Not built."""
    path = _newest_loop_doc()
    if path is None:
        return None
    m = re.search(r"^\*\*Topic:\*\*\s*(.+?)\s*(?:·|$)", _read(path)[:4000], re.M)
    return m.group(1)[:18] if m else None


def work() -> str:
    """WHAT WE ARE WORKING ON — the maintainer's first ask of this strip: `topic · subtopic`.

    Rendered as `topic · subject · branch`, each part dropped when its source is silent. The
    **subject** is the newest handoff/brief on disk (what a fresh session would open) and the
    **branch** is what git says HEAD is; neither can go stale, because neither is maintained.

    The **topic** half is the exception and is declared, not proven — see `topic()` for why that
    was chosen and what would check it. A doc that declares no topic simply drops that part; the
    strip never invents one."""
    branch = _run("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
    parts = [p for p in (topic(), entry_point()) if p and p != "?"]
    if branch not in ("", "HEAD"):
        parts.append(branch[:24])
    return f" {chr(183)} ".join(parts) or "?"


def bar(frac: float, width: int = 8) -> str:
    filled = int(round(frac * width))
    return "▰" * filled + "▱" * (width - filled)


def _arc_line(c) -> str:
    """The second line: five defensible fractions, then the two counts.

    **A rung with no criteria renders `?` and nothing else** — no bar, no zero. An empty bar
    beside a `?` would read as "none of it is done"; the truth is that nobody has said how much
    there is to do."""
    segments = []
    for key, met, declared in arc():
        if met is None or declared is None:
            segments.append(f"{c('dim')}{key}{c('off')} {c('warn')}?{c('off')}")
            continue
        frac = met / declared if declared else 0.0
        tone = "good" if frac >= 0.40 else "warn" if frac >= 0.20 else "bad"
        segments.append(f"{c('dim')}{key}{c('off')} {c(tone)}{bar(frac, 4)}{c('off')} "
                        f"{c('bold')}{met}/{declared}{c('off')}")
    waiting, ready = frontier_counts()
    segments.append(f"{c('dim')}frontier{c('off')} "
                    f"{c('warn') if waiting is None else c('mute')}"
                    f"{'?' if waiting is None else waiting}{c('off')}")
    segments.append(f"{c('dim')}ready{c('off')} "
                    f"{c('warn') if ready is None else c('cool')}"
                    f"{'?' if ready is None else ready}{c('off')}")
    return f"{c('dim')}arc{c('off')}  " + "  ".join(segments)


def render(color: bool = True) -> str:
    """Two lines. Line 1 is the register and the loop; line 2 is the arc.

    The second line exists because the arc needs five fractions and a one-line strip cannot carry
    them beside the register without abbreviating the rung names, which would trade a figure a
    reader can act on for one they have to decode."""
    c = (lambda k: C[k]) if color else _plain
    closed, total, delta = residues()
    raised, closed_7d, idle = velocity()
    frac = closed / total if total else 0.0

    tone = "good" if frac >= 0.40 else "warn" if frac >= 0.20 else "bad"
    trend = ""
    if delta is not None:
        trend = (f"{c('good')}▲{delta:.1f}{c('off')}" if delta > 0.05 else
                 f"{c('bad')}▼{abs(delta):.1f}{c('off')}" if delta < -0.05 else
                 f"{c('mute')}={c('off')}")

    net = closed_7d - raised
    vtone = "good" if net > 0 else "mute" if net == 0 else "warn"
    itone = "good" if (idle is not None and idle <= 3) else \
            "warn" if (idle is not None and idle <= 10) else "bad"

    sep = f" {c('dim')}│{c('off')} "
    return sep.join([
        f"{c('cool')}{work()}{c('off')}",
        f"{c('dim')}residues{c('off')} {c(tone)}{bar(frac)}{c('off')} "
        f"{c('bold')}{closed}/{total}{c('off')} {c('dim')}closed{c('off')} {trend}",
        f"{c('dim')}7d{c('off')} {c(vtone)}{raised} raised {closed_7d} closed{c('off')}",
        f"{c('dim')}last close{c('off')} {c(itone)}"
        f"{'?' if idle is None else str(idle) + 'd ago'}{c('off')}",
    ]) + "\n" + _arc_line(c)


def main() -> int:
    if not sys.stdin.isatty():
        try:
            sys.stdin.read()
        except Exception:
            pass
    color = "--no-color" not in sys.argv
    if "--refresh" not in sys.argv:
        try:
            st = os.stat(CACHE)
            if _dt.datetime.now().timestamp() - st.st_mtime < _TTL:
                line = json.load(open(CACHE))[("color" if color else "plain")]
                print(line)
                return 0
        except Exception:
            pass
    try:
        both = {"color": render(True), "plain": render(False)}
        try:
            with open(CACHE, "w") as fh:
                json.dump(both, fh)
        except OSError:
            pass
        print(both["color" if color else "plain"])
    except Exception:
        pass                      # never break the status line
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
