"""FIRST OBSERVATION — the day a registered corpus reading first entered `main`.

WHY THIS EXISTS (R198). `cor:readAt` in `tests/corpus-manifest.ttl` records when the
register was REFRESHED, not when a figure was read: 7 distinct days for 95 figure-
bearing evidence documents spanning six weeks. MEASURED 2026-09-09, `readAt` lags
first observation for 8 of the 17 quotable readings, by 1 to 16 days, so every
date-based judgement about where a figure came from is late by an unknown amount.

That is not academic. Re-running R192's supersession census with the dates below,
holding every other choice of that census fixed, moves 15 undated evidence
occurrences from "current when written" to "already superseded when written" —
including the seven 2026-09-08 quotations of `apple 0.6289` that R192 was raised
about, and which R192's own census scored as zero (spec §4).

R192's handoff recorded that its census was scratch code and that "nothing in the
repo re-derives them". This is the dating primitive that census needed, committed so
the next loop measures instead of rewriting. It is deliberately NOT a gate: it
answers a question, it does not refuse anything.

WHAT IT MEASURES, EXACTLY. The first commit on `main` whose diff ADDS a line
containing the reading's exact lexical form. That bounds observation from ABOVE — a
value measured on the 7th and committed on the 8th reads as the 8th — and it is the
whole claim. Nothing here recovers the instant of measurement; the point is only
that git bounds it far more tightly than a refresh log does.

WHAT IS EXCLUDED, AND WHY IT IS NOT A SKIP LIST. A reading flagged `cor:notQuotable`
in the register is excluded. Today that is exactly one row, `graincorp-capacity 1.0`,
whose first added line on `main` is a 2026-05-31 MkDocs deploy — 81 days of noise.
The exclusion is read from the REGISTER, never from a literal here, because it is the
same root cause the flag already names: `1.0` is not a distinctive literal, so it
cannot be matched against prose or against history. A second, separately-maintained
skip list would be the R188 failure (an exemption is a coverage loss dressed as a fix).

CLASSIFICATION (CLAUDE.md §8): PROCEDURAL, and irreducible for the sanctioned reason
— this is RAW EXTRACTION, source to typed facts. Git history is not an RDF graph, so
there is no evidence graph for an AXIOM to query until this has run, and nothing is
read or proposed, so it is not NEURAL. It carries no tolerance, no threshold and no
tuned constant: an exact substring match of a lexical form against added diff lines.

USAGE

    python3 scripts/first_seen.py            # a table, newest reading last
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from rdflib import Graph, Namespace

COR = Namespace("https://w3id.org/iladub/corpus#")
REGISTER = Path("tests/corpus-manifest.ttl")
#: The one history walk. `-G` selects commits whose diff touches a matching line;
#: `-U0 -p` then gives just those lines, and a NUL record separator keeps commit
#: boundaries unambiguous against diff text that may contain anything. Git expands
#: `%x00` itself — a real NUL cannot be passed through argv (`ValueError: embedded
#: null byte`), which is why the emitted and the split form differ here.
_SEP_FORMAT = "%x00%h %ad"
_SEP = "\0"


def require_full_history(repo: Path) -> None:
    """A shallow clone has no history to pickaxe, so every reading would resolve to
    None and this module would report "unrecoverable" for all of them — a false
    negative that reads exactly like a real finding. Fail loudly instead of guessing
    (CLAUDE.md § Core design principles 7; the same guard, for the same reason, as
    `tests/docgov_extract.py::_require_full_history`)."""
    out = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"], cwd=repo,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if out == "true":
        raise RuntimeError(
            "first_seen requires full git history (shallow clone detected): "
            "fetch with --unshallow / fetch-depth: 0"
        )


def quotable_readings(repo: Path) -> dict[str, str]:
    """value -> slug, for every registered reading that may be quoted.

    Keyed by VALUE because that is what git can search for. The register's
    one-node-per-distinct-value rule is scoped PER DOCUMENT, so two documents may in
    principle register the same value; git cannot tell those apart, and attributing
    the commit to whichever was parsed first would be a silent wrong answer. Refuse
    instead (CLAUDE.md § Core design principles 7)."""
    reg = Graph().parse(repo / REGISTER)
    out: dict[str, str] = {}
    for doc, node in reg.subject_objects(COR.reading):
        if reg.value(node, COR.notQuotable):
            continue
        value, slug = str(reg.value(node, COR.value)), str(doc).rsplit(":", 1)[-1]
        if value in out and out[value] != slug:
            raise ValueError(
                f"{value} is registered by two documents ({out[value]}, {slug}): git "
                "cannot attribute a shared literal, so first observation is undecidable"
            )
        out[value] = slug
    return out


def first_seen(repo: Path, values: list[str], rev: str = "HEAD") -> dict[str, tuple[str, str]]:
    """value -> (short sha, ISO date) of the first commit reachable from `rev` that ADDS it.

    `rev` is `HEAD` — this tree's own history, mainline plus whatever branch you are
    on — and NOT `--all`. A value that only ever existed on an abandoned branch was
    never a reading of this tree (R199(b), the `bfs 0.9401` case), and `--all` would
    resurrect exactly those. MEASURED 2026-09-09: `--all` agrees with the ancestry
    scope on the DATE for all 18 registered readings and differs only in which hash
    it names, the branch commit against the squashed merge.

    NOT a named branch, and CI is why. `main` was the first choice and it FAILED in
    CI with exit 128: `actions/checkout` leaves a detached HEAD with no local `main`
    ref, so the pickaxe could not run at all. The deeper defect the crash exposed is
    worse than the crash — under `main` scope, a PR that appends a NEW reading to the
    register would find its value absent from `main` and report it unrecoverable, so
    `test_every_quotable_reading_is_recoverable` could never go green until after the
    merge it is blocking. `HEAD` resolves in every checkout and includes the branch's
    own commits, which is also the honest answer to "when did this value enter the
    tree" while a change is in flight."""
    require_full_history(repo)
    if not values:
        return {}
    alternation = "|".join(re.escape(v) for v in sorted(values))
    out = subprocess.run(
        ["git", "log", "--reverse", "--date=short", "--format=" + _SEP_FORMAT,
         "-G" + alternation, "-U0", "-p", rev],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout
    found: dict[str, tuple[str, str]] = {}
    for record in out.split(_SEP):
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        sha, date = header.split()
        added = [ln for ln in body.splitlines() if ln.startswith("+")]
        for value in values:
            if value not in found and any(value in ln for ln in added):
                found[value] = (sha, date)
    return found


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    readings = quotable_readings(repo)
    seen = first_seen(repo, list(readings))
    reg = Graph().parse(repo / REGISTER)
    read_at = {
        str(reg.value(n, COR.value)): min(str(d) for d in reg.objects(n, COR.readAt))
        for _, n in reg.subject_objects(COR.reading)
    }
    rows = sorted(readings, key=lambda v: (seen.get(v, ("", "9999"))[1], readings[v]))
    print(f"{'slug':30s} {'value':22s} {'readAt[0]':11s} {'first seen (ancestry)':26s} lag")
    for value in rows:
        hit = seen.get(value)
        where = f"{hit[0]}  {hit[1]}" if hit else "UNRECOVERABLE"
        lag = ""
        if hit:
            from datetime import date as _d
            lag = (_d.fromisoformat(read_at[value]) - _d.fromisoformat(hit[1])).days
        print(f"{readings[value]:30s} {value:22s} {read_at[value]:11s} {where:26s} {lag}")


if __name__ == "__main__":
    main()
