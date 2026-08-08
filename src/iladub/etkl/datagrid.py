"""datagrid — the DATA of a table, derived before any metadata is read.

Realises `vocab/ontology/tab-datagrid.ttl`. Wang's distinction is the architecture:
ENTRIES are data, CATEGORIES (boxhead, stub, spanners, captions, notes) are metadata.
This module derives the entries only. Nothing here reads a header, a stub label, an
indentation depth or a caption — a data grid must be identifiable without them, or the
reading is circular (the defect recorded as R71).

THE DEFINITION (spec 2026-08-08-data-grid-types-elements-axioms.md §8.1, §8.6):

    A data grid is a maximal rectangle whose rows and columns are admitted together.
    Columns are admitted because the rows agree on their type; rows are admitted
    because the columns agree on their shape.

The column universe is fixed ONCE and never re-derived — that is part of the
definition, not an implementation choice. Re-deriving it from the growing row set
changes the columns' identity between rounds, so the operators are not a closure and
were measured not to converge (§8.5).

§8 classification of what lives here:
  PROCEDURAL  `drawn_rules`, `ink_runs` — raw extraction of geometry into typed facts.
              Irreducible: there is no declarative form of "read the content stream".
  AXIOM       every judgement below (groupability, homogeneity, addressability,
              maximality) is a presence, containment or ordinal test, and is intended
              to migrate to SPARQL over the evidence graph unchanged.

The one number in this module is GAP, and it is justified by a measured invariance
plateau rather than by fit — see its comment.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from .celltype import _cell_datatype, is_blank
from .geometry import Line, extract_words, text_lines

# The run separator. NOT tuned: the page-level table/prose verdict is identical for
# every value in [3, 20]pt across the whole corpus (17 of 27 pages, unchanged), because
# `GAP` only has to fall between prose word-spacing and column gutters. Measured margin
# is ~10x: prose collapses to one run at 3pt while tables survive past 33pt.
GAP = 4.0

_TAB = "https://w3id.org/iladub/tab#"
_FAMILY = {"Numeric": "Quantity", "Currency": "Quantity"}
# tab:datatypeAbstains — these take no part in a homogeneity comparison. They do NOT
# erase a column that has nothing else (apple p2's value columns are entirely
# parenthesised negatives; erasing them read the page as "not a table").
_ABSTAIN = frozenset({"Blank", "ParenthesizedNumber"})
_UNIT_MARKER = re.compile(r"^[$€£¥]$")


# A run made only of digits and separators is ONE number, and the spaces inside it are
# thousands separators. This is the SI/ISO 31-0 convention ("8 962 258"), used natively
# by the Swiss federal statistics office throughout bfs, and it is ALSO the shape the
# split-number defect R16 produces when a padding glyph lands inside a digit run
# ("20,000" extracted as "2 0,000"). One rule covers both, because they are the same
# lexical shape — nothing here is specific to either document.
#
# Measured candidates per page: bfs 192, stem 51, apple 1 (the single row that page was
# missing), and ZERO on cbh, ons and who — so it corrects where the convention is used
# and is inert everywhere else.
_SPACED_NUMBER = re.compile(r"^-?\d[\d.,\s]*$")


def family_of(text: str) -> str:
    """The cell's datatype family, via the shipped tab:inDatatypeFamily lattice."""
    t = text.strip()
    if " " in t and _SPACED_NUMBER.match(t):
        text = re.sub(r"\s+", "", t)
    u = _cell_datatype(text)
    name = str(u).replace(_TAB, "") if u is not None else "Text"
    return _FAMILY.get(name, name)


@dataclass(frozen=True)
class Run:
    """A maximal group of words on one line with no gap wider than GAP between them."""
    x0: float
    x1: float
    text: str


@dataclass(frozen=True)
class GridColumn:
    x0: float
    x1: float
    family: str | None          # tab:columnFamily; None when the column cannot agree

    @property
    def is_measure(self) -> bool:
        """tab:MeasureColumn — carries values rather than identifiers.

        Measure-ness TYPES the grid; it never decides admission. Text IS a legal family:
        in a record table a vessel name is data, and excluding Text excluded every
        record table."""
        return self.family is not None and self.family != "Text"


@dataclass(frozen=True)
class DataGrid:
    """tab:DataGrid — the entries, and the record of why they were admitted."""
    rows: tuple[int, ...]                    # indices into the page's text lines
    columns: tuple[GridColumn, ...]
    universe: str                            # "decoration" | "alignment"
    conforms: tuple[str, ...] = ()           # tab:conformsTo
    refusals: dict = field(default_factory=dict)   # line index -> tab:refutedBy

    @property
    def measures(self) -> tuple[int, ...]:
        return tuple(i for i, c in enumerate(self.columns) if c.is_measure)

    @property
    def grid_type(self) -> str:
        """tab:UniformGrid when every measure shares one family, else tab:MixedGrid."""
        fams = {self.columns[i].family for i in self.measures}
        return "UniformGrid" if len(fams) == 1 else "MixedGrid"


# --------------------------------------------------------------------------- PROCEDURAL


def ink_runs(line: Line, gap: float = GAP) -> list[Run]:
    """The line's ink runs. Raw extraction; no judgement."""
    ws = sorted(line.words, key=lambda w: w.x0)
    if not ws:
        return []
    out: list[Run] = []
    x0, x1, parts = ws[0].x0, ws[0].x1, [ws[0].text]
    for w in ws[1:]:
        if w.x0 - x1 > gap:
            out.append(Run(x0, x1, " ".join(parts)))
            x0, x1, parts = w.x0, w.x1, [w.text]
        else:
            x1 = max(x1, w.x1)
            parts.append(w.text)
    out.append(Run(x0, x1, " ".join(parts)))
    return out


def absorb_unit_markers(runs: list[Run]) -> list[Run]:
    """A lone currency glyph is a tab:UnitMarker on its neighbour, not a column.

    PRECONDITION of the definition, not a clean-up: leaving markers in splits otherwise
    identical rows into different signatures, and one table is read as two (measured on
    apple, n=9 with the '$' present against n=5 without)."""
    out: list[Run] = []
    i = 0
    while i < len(runs):
        r = runs[i]
        if _UNIT_MARKER.match(r.text.strip()) and i + 1 < len(runs):
            nxt = runs[i + 1]
            out.append(Run(r.x0, nxt.x1, nxt.text))
            i += 2
        else:
            out.append(r)
            i += 1
    return out


def drawn_rules(pdf_path: str, page_number: int = 0) -> list[float]:
    """Vertical tab:DrawnRule x-positions.

    A mark is a rule iff it CONTAINS NO GLYPH CENTRE. That is the whole test, and it is
    a presence test — no thinness ratio, no minimum width. A fill contains the text it
    sits behind; a rule contains nothing.

    This separates what every previous extractor conflated: apple page 0 reports 678
    'vertical rules' when fill edges are counted and exactly 2 when they are not, and
    WHO's universe collapses from 104 spurious columns to 4 emblem strokes."""
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        rects = list(page.rects)
        centres = [((float(c["x0"]) + float(c["x1"])) / 2,
                    (float(c["top"]) + float(c["bottom"])) / 2) for c in page.chars]
    xs = []
    for r in rects:
        x0, x1 = float(r["x0"]), float(r["x1"])
        top, bot = float(r["top"]), float(r["bottom"])
        if x1 <= x0 or bot <= top:
            continue
        if any(x0 <= cx <= x1 and top <= cy <= bot for cx, cy in centres):
            continue                                    # contains ink -> a fill
        if (bot - top) > (x1 - x0):
            xs.append(round((x0 + x1) / 2, 1))
    return sorted(set(xs))


# ------------------------------------------------------------------------------- AXIOM


def is_contiguous(values: list) -> bool:
    """G9 tab:Groupability — equal values are ADJACENT.

    Adjacency, not sortedness: grouping needs only that equal values sit together, so no
    order relation, collation or date parsing is required. Callers evaluate this WITHIN a
    parent group; a global test rejects exactly the levels it should accept (a port
    recurring under three months is contiguous within each and not across the page)."""
    seen: set = set()
    prev = object()
    for v in values:
        if v != prev:
            if v in seen:
                return False
            seen.add(v)
        prev = v
    return True


def reconciles(total, members: list) -> bool:
    """G8 tab:AggregateWitness — exact Decimal, never a tolerance."""
    try:
        return members and Decimal(total) == sum(Decimal(m) for m in members)
    except (InvalidOperation, TypeError):
        return False


def _boundaries_from_alignment(seed_runs: list[list[Run]]) -> list[float]:
    """tab:AlignmentUniverse — the gaps between the seed rows' run extents."""
    n = len(seed_runs[0])
    ext = [(min(rs[k].x0 for rs in seed_runs), max(rs[k].x1 for rs in seed_runs))
           for k in range(n)]
    bounds = [ext[0][0]]
    bounds += [(ext[j][1] + ext[j + 1][0]) / 2 for j in range(n - 1)]
    bounds.append(ext[-1][1])
    return bounds


def _boundaries_from_decoration(rules: list[float], page_runs: list[list[Run]]
                                ) -> list[float] | None:
    """tab:DecorationUniverse — columns between drawn rules, each ink-witnessed.

    A column counts only when at least two rows place a run inside it, which refuses
    ornament: WHO's four emblem strokes bound no column any row occupies."""
    if len(rules) < 3:
        return None
    spans = [(rules[j], rules[j + 1]) for j in range(len(rules) - 1)]
    good = [s for s in spans
            if sum(1 for rs in page_runs for r in rs
                   if r.x0 >= s[0] - 0.5 and r.x1 <= s[1] + 0.5) >= 2]
    if len(good) < 2:
        return None
    return [good[0][0]] + [g[1] for g in good]


def derive_data_grid(pdf_path: str, page_number: int = 0) -> DataGrid | None:
    """Derive the page's data grid, or None when no rectangle is admissible."""
    lines = [l for l in sorted(text_lines(extract_words(pdf_path, page_number)),
                               key=lambda l: l.top) if l.words]
    if not lines:
        return None
    runs = [absorb_unit_markers(ink_runs(l)) for l in lines]

    # --- the seed: the recurring row signature accounting for the most ink.
    # NOT the most frequent one: wrapped continuation fragments are the most numerous
    # line shape on a real document, and frequency alone picks them (measured on stem,
    # where a 2-run fragment class outnumbers the 15-run data rows).
    sigs = [tuple(family_of(r.text) if not is_blank(r.text) else "Blank" for r in rs)
            for rs in runs]
    counts = Counter(sigs)
    recurring = [s for s in counts if counts[s] >= 2 and s]
    if not recurring:
        return None
    modal_sig = max(recurring, key=lambda s: len(s) * counts[s])
    sig_seed = [i for i, s in enumerate(sigs) if s == modal_sig]

    # --- the column universe, fixed ONCE.
    align = _boundaries_from_alignment([runs[i] for i in sig_seed])
    decor = _boundaries_from_decoration(drawn_rules(pdf_path, page_number), runs)
    # Decoration wins only when it resolves AT LEAST AS FINELY as alignment — an ordinal
    # comparison, not a threshold. Preferring it unconditionally cost stem every row,
    # because its three drawn marks are page borders giving 2 columns against 15.
    if decor is not None and len(decor) >= len(align):
        bounds, universe = decor, "decoration"
    else:
        bounds, universe = align, "alignment"
    ncols = len(bounds) - 1
    if ncols < 2:
        return None

    def place(rs: list[Run]) -> dict | None:
        """Map a row's runs into the fixed columns, or refuse it.

        Ink OUTSIDE the column extent is not a refusal. The grid is the rectangle, so ink
        beyond it is metadata by construction — an index value, not a defect in the row.
        Measured on the stem: 24 real data rows carry a year or month value that their
        neighbours ditto-suppress, and treating that ink as grounds for refusal discarded
        every row that begins a group."""
        if not rs:
            return None
        rs = [r for r in rs if r.x1 > bounds[0] - 0.5 and r.x0 < bounds[-1] + 0.5]
        if not rs:
            return None
        hit: dict = {}
        for r in rs:
            centre = (r.x0 + r.x1) / 2
            k = next((j for j in range(ncols) if bounds[j] <= centre < bounds[j + 1]), None)
            if k is None or k in hit:            # R3 straddle, or two runs in one column
                return None
            hit[k] = r.text
        return hit if len(hit) >= 2 else None

    placed = [(i, place(runs[i])) for i in range(len(lines))]
    placed = [(i, h) for i, h in placed if h]
    if not placed:
        return None

    # --- G0 tab:SeedFollowsUniverse: the seed is the modal class in WHATEVER universe
    # supplied the columns. Seeding a decoration universe by signature cost capacity 19
    # of its 27 rows: the seed must be modal in the space the columns came from.
    if universe == "decoration":
        key_occ = Counter(frozenset(h) for _, h in placed).most_common(1)[0][0]
        seed_rows = [h for _, h in placed if frozenset(h) == key_occ]
    else:
        wanted = set(sig_seed)
        seed_rows = [h for i, h in placed if i in wanted]
    if not seed_rows:
        return None

    def _type(rows_: list[dict]) -> list[GridColumn]:
        cols = []
        for k in range(ncols):
            fams = {family_of(h[k]) for h in rows_ if k in h and not is_blank(h[k])}
            core = fams - _ABSTAIN
            use = core if core else fams
            cols.append(GridColumn(bounds[k], bounds[k + 1],
                                   next(iter(use)) if len(use) == 1 else None))
        return cols

    # --- G1 tab:ColumnHomogeneity, in two bounded passes.
    #
    # Typing from the seed ALONE manufactures agreement a column does not have: the seed
    # rows are one signature class, so a column they happen to fill uniformly is declared
    # homogeneous even when the rest of the table contradicts it. Measured on the stem,
    # where the slot-reference column is Quantity across the seed but carries a commodity
    # word on every non-grain row — 10 real data rows refused for disagreeing with a
    # family the column never actually had.
    #
    # G1 says a column agrees over the ADMITTED rows. So: type provisionally from the
    # seed, take the rows that satisfy addressability under it, then RE-TYPE over those.
    # A column they contradict has no family, and a column with no family refuses nobody.
    #
    # This is two passes, not an iteration: the columns themselves never move, so the
    # non-convergence of §8.5 cannot arise.
    # The second pass is ASYMMETRIC: it may only RELAX a refusal, never redefine what the
    # grid is. Letting it re-derive the measures destroyed capacity, bfs and ons outright
    # (one contradicting row emptied the measure set, and with it the grid). So the seed
    # establishes the grid's identity — its measures and its key column — while the wider
    # evidence decides only whether a column is entitled to REFUSE a row.
    columns = _type(seed_rows)
    measures = {i for i, c in enumerate(columns) if c.is_measure}
    if not measures:                              # G1b tab:NonDegeneracy
        return None
    key_col = min(k for k in range(ncols) if columns[k].family is not None)
    addressable = [h for _, h in placed if key_col in h and (measures & set(h))]
    # A column that the addressable rows contradict has no agreed family, and a column
    # with no agreed family refuses nobody.
    refusing = {k: c.family for k, c in enumerate(_type(addressable))} if addressable \
        else {k: c.family for k, c in enumerate(columns)}

    # --- G2 tab:RowAddressability + G1 compatibility.
    rows: list[int] = []
    refusals: dict = {}
    for i, h in placed:
        if key_col not in h:
            refusals[i] = "RowAddressability/no-key"
            continue
        if not (measures & set(h)):
            refusals[i] = "RowAddressability/no-measure"
            continue
        # A row contradicting the seed's family in EVERY measure column it occupies is
        # not a row of this grid — it is a header. A universal quantifier, not a count.
        #
        # It exists because the asymmetric relaxation above disarmed the refusal that
        # used to catch a boxhead: the stem's placeholder and mixed-cargo rows null
        # several column families between them, after which the header row places
        # cleanly into the very columns it labels. Measured, it contradicts all six
        # measure columns (Text against Date and Quantity) while a mixed-cargo row
        # contradicts one and a placeholder row two, so the quantifier separates them
        # without counting anything.
        #
        # Over EVERY occupied measure column, however few. A ">= 2" carve-out was tried
        # and REVERTED: it was justified by row counts on pages that had no oracle, and
        # when ons was transcribed those extra rows turned out to BE the leaks — its
        # title and two footnotes each occupy exactly one measure column and contradict
        # it. Row counts on unverified pages are not evidence.
        occupied = measures & set(h)
        if occupied and all(
                not is_blank(h[k]) and columns[k].family
                and columns[k].family not in _ABSTAIN
                and family_of(h[k]) not in _ABSTAIN
                and family_of(h[k]) != columns[k].family
                for k in occupied):
            refusals[i] = "HeterogeneousColumn/every-measure"
            continue
        clash = next((k for k, t in h.items()
                      if not is_blank(t) and refusing.get(k)
                      and refusing[k] not in _ABSTAIN
                      and family_of(t) not in _ABSTAIN
                      and family_of(t) != refusing[k]), None)
        if clash is not None:
            refusals[i] = f"HeterogeneousColumn/col{clash}"
            continue
        rows.append(i)
    if not rows:
        return None
    for i in range(len(lines)):
        refusals.setdefault(i, "unplaceable") if i not in set(rows) else None

    return DataGrid(
        rows=tuple(rows),
        columns=tuple(columns),
        universe=universe,
        conforms=("ColumnHomogeneity", "NonDegeneracy", "RowAddressability",
                  "ColumnAlignment", "SeedFollowsUniverse"),
        refusals=refusals,
    )
