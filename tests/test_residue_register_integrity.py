"""The residue register's own integrity — the check R137 says has never existed.

CLAUDE.md § Deferred residues calls `docs/superpowers/residues.md` **canonical** and directs
every contributor to read it before planning. On 2026-08-12 it was split into an index plus
two detail files for a context-budget reason, and **the integrity check that split needed was
never written**: R137 measured all three falsifications on 2026-08-25 and the suite stayed
green for two of them — delete an index row outright (its detail row left orphaned), or flip
a `closed` index row back to `open` while its detail row sits in `residues-closed.md`. Only
the third, deleting a row a `prog:blockedBy` NAMES, was caught, by `test_arc_manifest.py`'s
M7 — whose scope is exactly the handful of rows the arc manifest happens to name, not the
register.

**Gate classification (CLAUDE.md §8): PROCEDURAL, and it is the same irreducibility M7
states one file away.** The register is markdown on the filesystem, not triples: it is not in
any graph, no shape can target it, and minting triples that mirror it would put a *derived*
copy of the register under the membrane while the register itself stayed unguarded — which is
the failure being fixed, not a fix for it. There is no tuned constant here and no reading
judgment; it is three set comparisons over parsed table rows.

WHAT THIS DOES NOT CHECK, stated rather than left to be discovered: whether an index line
*says the same thing* as its detail row. That is a semantic question about prose, this is a
structural one about rows, and conflating them would make one refusal answer two. The index
line is defined as a pointer (CLAUDE.md); what it points AT is what is checked here.
"""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "docs" / "superpowers" / "residues.md"
DETAIL = {
    "open": REPO / "docs" / "superpowers" / "residues-open.md",
    "closed": REPO / "docs" / "superpowers" / "residues-closed.md",
}

# An index row: `| R95 | open | …`. The status cell may carry a parenthetical qualifier —
# two do at HEAD (`open (half (a) done)`, `open (code landed)`) — so the leading word is the
# status and the rest is prose.
_INDEX_ROW = re.compile(r"^\| *(R\d+) *\| *([A-Za-z]+)[^|]*\|", re.M)

# A detail row: `| R137 (25/126 closed) |` when open, `| ~~R1~~ (22/108 closed) |` when
# closed. The strike is the marker CLAUDE.md's register convention uses for a closed row,
# and the tally in parentheses is a never-updated snapshot, so neither is parsed further.
_DETAIL_ROW = re.compile(r"^\| *(~~)?(R\d+)(?(1)~~) *[^|]*\|", re.M)


def index_rows():
    """`{id: status}` for every row of the index, which is the canonical list."""
    return {rid: status.lower() for rid, status in _INDEX_ROW.findall(INDEX.read_text("utf-8"))}


def detail_rows(status):
    """`{id: struck}` for every row of one detail file."""
    return {rid: bool(struck)
            for struck, rid in _DETAIL_ROW.findall(DETAIL[status].read_text("utf-8"))}


def test_every_index_status_is_open_or_closed():
    """The status word is what routes a row to a detail file, so it must be one of two."""
    unknown = {rid: s for rid, s in index_rows().items() if s not in DETAIL}
    assert unknown == {}, f"index rows with an unroutable status: {unknown}"


def test_every_index_row_has_exactly_one_detail_row_in_the_file_its_status_names():
    """R137's falsification (b): flipping `closed` back to `open` left the suite green."""
    index = index_rows()
    detail = {s: set(detail_rows(s)) for s in DETAIL}
    misfiled = {}
    for rid, status in index.items():
        homes = sorted(s for s in DETAIL if rid in detail[s])
        if homes != [status]:
            misfiled[rid] = f"index says {status!r}, detail row is in {homes or 'NO detail file'}"
    assert misfiled == {}, f"index and detail disagree: {misfiled}"


def test_every_detail_row_has_an_index_row():
    """R137's falsification (a): deleting an index row orphaned its detail row, green."""
    index = set(index_rows())
    orphaned = {s: sorted(set(detail_rows(s)) - index, key=lambda r: int(r[1:]))
                for s in DETAIL}
    assert {s: v for s, v in orphaned.items() if v} == {}, (
        f"detail rows with no index row — the index is canonical, so these do not exist: "
        f"{orphaned}")


@pytest.mark.parametrize("status", sorted(DETAIL))
def test_a_row_is_struck_if_and_only_if_it_is_filed_closed(status):
    """`~~Rn~~` marks repair. A struck row in the open file, or an unstruck one in the
    closed file, is a half-done move between the two — which is what a closing loop does by
    script and nothing has ever checked."""
    wrong = sorted((rid for rid, struck in detail_rows(status).items()
                    if struck != (status == "closed")), key=lambda r: int(r[1:]))
    assert wrong == [], (
        f"in residues-{status}.md, rows whose strike contradicts the file they are in: {wrong}")


def test_no_residue_id_is_declared_twice():
    """A duplicate makes 'exactly one detail row' unverifiable by set comparison alone."""
    dupes = {}
    for name, path in [("index", INDEX)] + [(f"residues-{s}", DETAIL[s]) for s in sorted(DETAIL)]:
        pattern = _INDEX_ROW if name == "index" else _DETAIL_ROW
        ids = [m[0] if name == "index" else m[1]
               for m in pattern.findall(path.read_text("utf-8"))]
        seen = {r for r in ids if ids.count(r) > 1}
        if seen:
            dupes[name] = sorted(seen, key=lambda r: int(r[1:]))
    assert dupes == {}, f"residue ids declared more than once: {dupes}"
