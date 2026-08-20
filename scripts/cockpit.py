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
    arc  ?/4               position on `docs/narrative/scope-evolution.md`'s four-stage arc.
                           **`?` is the honest answer and the point of the gauge**: the arc exists
                           and carries no state, so nothing can say which rung we are on. It reads
                           amber until something can. Do NOT make this render a number by guessing
    ▸    <loop>            the current entry point, read from the newest handoff/brief on disk

§ THE TUNED-CONSTANT TRAP, and why there is no "velocity index" here. CLAUDE.md §8 forbids a
procedural decision with a tuned constant. "Are we stuck?" is exactly such a judgment, and
`if velocity < 0.3: return "STUCK"` would be the defect the gate exists to catch. So this strip
reports the two raw counts and the idle days and refuses to collapse them into a verdict — the
reader disposes. The only colour thresholds are on `res` (the register's own published tally
convention) and they colour, they do not decide.

Gate classification (CLAUDE.md §8): PROCEDURAL reporting harness, and irreducible for the usual
reason — it is string formatting and date arithmetic over files, making no domain decision. It
derives nothing about the graph and validates nothing. The one judgment it might have made
(stuck / not stuck) is the one it deliberately declines to make.

PERFORMANCE CONTRACT. The status line re-renders constantly, so this must never be slow and must
never touch the network, rdflib, pytest or the corpus. It reads three small markdown files and
runs at most two `git log` calls, then caches the rendered line for `_TTL` seconds. A cache miss
is a few milliseconds; a hit is a single file read. If it ever raises, it prints nothing rather
than breaking the status line.

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
ARC = os.path.join(ROOT, "docs", "narrative", "scope-evolution.md")
CACHE = os.path.join(ROOT, ".git", "cockpit-cache.json")   # inside .git: never tracked
_TTL = 180
_WINDOW = 7

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


def arc() -> tuple[int | None, int]:
    """(position, stages). Position is ALWAYS None today and that is the finding, not a bug:
    `scope-evolution.md` names the stages and records no state, so nothing in the repo can say
    which one is current. When an objectives artifact gains state, teach this to read it."""
    stages = len(re.findall(r"^### ", _read(ARC), re.M)) or 4
    return None, stages


def entry_point() -> str:
    """The newest brief/handoff on disk — the thing a fresh session would open."""
    d = os.path.join(ROOT, "docs", "superpowers")
    try:
        names = [f for f in os.listdir(d) if re.match(r"\d{4}-\d{2}-\d{2}-.*\.md$", f)
                 and ("handoff" in f or "brief" in f)]
    except OSError:
        return "?"
    if not names:
        return "?"
    newest = max(names)
    return re.sub(r"^\d{4}-\d{2}-\d{2}-|\.md$|-handoff$|-brief$", "", newest)[:28]


def work() -> str:
    """WHAT WE ARE WORKING ON — the maintainer's first ask of this strip, and the one gauge whose
    sources are chosen to make staleness impossible rather than merely unlikely.

    Both halves are read from live state, never from a field anyone maintains: the **subject** is
    the newest handoff/brief on disk (what a fresh session would open) and the **branch** is what
    git says HEAD is. A hand-written "current topic" marker would be the failure mode this whole
    strip exists against — a dashboard asserting a fact nobody re-checked.

    It is NOT the curated `topic — subtopic` taxonomy (`etkl · table-reading`) that was asked for.
    That needs an artifact naming the topics and binding work to them, which is the objectives
    artifact `docs/superpowers/2026-08-20-strategy-instrument-handoff.md` designs and does not yet
    exist. Until it does, this reports the two things the repo can actually prove."""
    branch = _run("git", "rev-parse", "--abbrev-ref", "HEAD").strip()
    subject = entry_point()
    if branch in ("", "HEAD"):
        return subject
    return f"{subject} {chr(183)} {branch[:24]}"


def bar(frac: float, width: int = 8) -> str:
    filled = int(round(frac * width))
    return "▰" * filled + "▱" * (width - filled)


def render(color: bool = True) -> str:
    c = (lambda k: C[k]) if color else _plain
    closed, total, delta = residues()
    raised, closed_7d, idle = velocity()
    pos, stages = arc()
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
        f"{c('dim')}stage{c('off')} {c('warn')}{'?' if pos is None else pos}/{stages}"
        f"{c('off')} {c('dim')}of the arc{c('off')}",
    ])


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
