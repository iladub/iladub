"""adoption — the data grid as the DOCUMENT's last reader (spec 2026-08-09, residue R73).

A page's total reading failure is not final at page scope. Adoption is admitted only where
carriage (loop M), section repair (loop Q) and stitching have all had their turn and the page
still asserted nothing — and it withdraws the escalation of the ink it actually READ, line by
line, never the page's whole ledger.

GATE CLASSIFICATION (CLAUDE.md §8).
  * The candidate GATE is an AXIOM — `vocab/queries/adoption-candidate.rq`, holon-scoped to one
    page (the holon is the closure boundary, so its query-local NOT EXISTS is legitimate).
  * The LEDGER below is justified PROCEDURAL: exact counting over line-index sets. It is
    irreducible to AXIOM or NEURAL because it is arithmetic over indices the grid and the band
    inventory already decided — it decides nothing about the document, it only refuses to count
    a line twice. It carries no threshold, no tolerance and no tuned constant.

WHY LINE GRANULARITY IS FORCED (spec §M5). On the specimen page, NO escalated band is fully
covered by the grid. A band-granular ledger therefore withdraws nothing and scores the page
142/(142+97) = 0.594 — the double count that made the first wiring's 0.5941 meaningless, since
the grid's tokens include the very lines those bands escalate. Zeroing the escalation instead
scores it 1.0000 by construction, whatever the grid missed. Only the line is a unit both sides
agree on.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class LineLedger:
    """One adopted page's accounting. `admitted` and `residue` are DISJOINT by construction."""
    admitted: tuple[int, ...]
    residue: tuple[int, ...]
    touched: frozenset[int]
    asserted_tokens: int
    escalated_tokens: int


def build_ledger(lines, grid_rows, bands, reports) -> LineLedger:
    """Account for every line of an adopted page exactly once.

    `lines` is the page's own `text_lines(extract_words(...))` sequence, sorted by `top` — the
    SAME sequence `grid_rows` indexes into, which is what makes the join exact.

    A band is TOUCHED when the grid admitted at least one line inside it. Touched bands lose
    their escalation (part of their ink has been read, so their record no longer describes what
    happened) and contribute their UNREAD lines as residue. Untouched bands keep their own
    token count verbatim.

    The band↔line join is interval containment on the author's own band bounds — the idiom
    `page_bands` already uses for hrules — never a coordinate tolerance.
    """
    admitted = tuple(sorted(set(grid_rows)))
    admitted_set = set(admitted)
    escalated_bands = [i for i, r in enumerate(reports) if r.verdict == "escalated"]

    def _inside(band, line):
        return band.top <= line.top <= band.bottom

    touched = frozenset(
        i for i in range(len(bands))
        if any(_inside(bands[i], lines[j]) for j in admitted if j < len(lines))
    )

    residue = tuple(
        j for j, ln in enumerate(lines)
        if j not in admitted_set
        and any(i in touched and _inside(bands[i], ln) for i in escalated_bands)
    )

    asserted_tokens = sum(len(lines[j].words) for j in admitted if j < len(lines))
    escalated_tokens = (
        sum(len(lines[j].words) for j in residue)
        + sum(reports[i].tokens_escalated for i in escalated_bands if i not in touched)
    )
    return LineLedger(admitted, residue, touched, asserted_tokens, escalated_tokens)
