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

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import PROV

from .celltype import _cell_datatype, is_blank
from .geometry import Line, extract_words, text_lines

TAB = Namespace("https://w3id.org/iladub/tab#")
DEC = Namespace("https://w3id.org/iladub/dec#")

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
    aggregates: dict = field(default_factory=dict)  # line index -> member line indices

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


def _decimal(text) -> Decimal | None:
    """A cell's value as an exact Decimal, or None when it is not a number.

    Thousands separators are stripped by the SAME convention `_SPACED_NUMBER` encodes
    (a space inside a digit run is an SI/ISO 31-0 separator), and a leading currency glyph
    is a tab:UnitMarker rather than part of the value. Exact Decimal, never float, never a
    tolerance — a tolerance here would be the tuned constant the §8 gate forbids."""
    if text is None:
        return None
    t = str(text).strip().replace(",", "").replace(" ", "").lstrip("$€£¥")
    try:
        return Decimal(t)
    except InvalidOperation:
        return None


def aggregate_members(i: int, admitted: set, aggregates: set) -> tuple[int, ...]:
    """G8's member rows: the admitted rows above `i`, back to the previous aggregate row,
    EXCLUSIVE. Ordinal only — it reads no geometry and no value.

    Rule B of spec 2026-08-09 §2.1. Measured INDISTINGUISHABLE from 'the maximal contiguous
    run of admitted rows above' on the whole corpus (both admit exactly cbh's four panel
    totals), and chosen because `rows.detect_aggregation_rows` already uses this shape, so
    the repo carries ONE member rule rather than two. Recorded as a reuse decision because
    the evidence does not choose between them."""
    stop = max((a for a in aggregates if a < i), default=-1)
    return tuple(j for j in range(stop + 1, i) if j in admitted)


def confirms_aggregate(cells: dict, member_cells: list) -> bool:
    """G8 tab:AggregateWitness as a ROW-ADMISSION disposer: EVERY occupied cell is numeric
    and equals the exact Decimal sum of that column over the member rows.

    Arithmetic only — it reads no position and never reads label text ('Total' is the tuned
    constant of natural language and is forbidden). The quantifier is UNIVERSAL, not a
    count: one column reconciling is not a witness, which is what refuses a period header
    whose leading column happens to sum.

    Two honest refusals, both deliberate: no members at all (a vacuous 0 == 0 never
    confirms, the same rule `reconciles` makes), and a cell whose column no member
    populates (a missing member is never read as a zero)."""
    if not cells or not member_cells:
        return False
    for k, text in cells.items():
        total = _decimal(text)
        if total is None:
            return False
        vals = [v for v in (_decimal(mc.get(k)) for mc in member_cells) if v is not None]
        if not vals or sum(vals) != total:
            return False
    return True


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

    def index_ink(rs: list[Run]) -> bool:
        """Does this row carry ink in the index block — outside the rectangle?"""
        return any(r.x1 <= bounds[0] - 0.5 for r in rs)

    def place_indexed(rs: list[Run], measure_cols: set,
                      min_cells: int | None = None) -> dict | None:
        """Placement once the measures are known, with the stub read as an ADDRESSING
        AXIS rather than one cell.

        A stub carries LEVELS — year, then month, then port — and two of them may print
        on one row. So several runs may share a non-measure column (they are levels of
        one address, joined in document order), while a measure column still admits
        exactly one value. And a row whose address lives entirely in the index block
        outside the rectangle is addressed by that ink, so it needs only one measure
        cell rather than two.

        Measured cause, one structure with two symptoms: ons prints '2024 Q4 102 ...'
        with year and quarter both inside the key column, and the stem prints
        'Jul 26 Total 1 18,000' with its label out at the month level, left of the grid.
        Both were refused — the first for two runs in a column, the second for having a
        single cell inside it.

        `min_cells` is a PER-CALL override used only by the aggregate-witness pass, which
        must see single-cell candidates. G2's own call site passes nothing, so no line
        reaches RowAddressability that does not reach it today — the floor is not lowered,
        it is by-passed for candidates the arithmetic then has to justify (spec §5.1)."""
        if not rs:
            return None
        outside = index_ink(rs)
        inside = [r for r in rs if r.x1 > bounds[0] - 0.5 and r.x0 < bounds[-1] + 0.5]
        if not inside:
            return None
        hit: dict = {}
        for r in inside:
            centre = (r.x0 + r.x1) / 2
            k = next((j for j in range(ncols) if bounds[j] <= centre < bounds[j + 1]), None)
            if k is None:
                return None                                    # R3 straddle
            if k in hit:
                if k in measure_cols:
                    return None                                # a measure holds one value
                hit[k] = f"{hit[k]} {r.text}"                   # stub levels, in order
            else:
                hit[k] = r.text
        floor = min_cells if min_cells is not None else (1 if outside else 2)
        return hit if len(hit) >= floor else None

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
    #
    # Re-placed now that the measures are known, so the stub can be read as an addressing
    # axis with levels. The columns themselves are unchanged — only the reading of runs
    # into them — so the fixed universe of §8.5 still holds.
    placed = [(i, place_indexed(runs[i], measures)) for i in range(len(lines))]
    placed = [(i, h) for i, h in placed if h]
    rows: list[int] = []
    refusals: dict = {}
    for i, h in placed:
        # A row addressed from the index block outside the rectangle needs no key cell
        # inside it — its address is the ink that was dropped.
        if key_col not in h and not index_ink(runs[i]):
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

    # --- G8 tab:AggregateWitness, as a ROW-ADMISSION axiom (spec 2026-08-09).
    #
    # STRICTLY ADDITIVE, and it runs AFTER the grid is closed: the column universe, the
    # measure set and key_col are already fixed, so this pass cannot change the grid's
    # identity and §8.5's non-convergence hazard cannot arise. Members always lie ABOVE
    # their candidate, so ONE top-down pass suffices — no iteration, no fixed point.
    #
    # The proposer is placement geometry and reads no value; the disposer is exact
    # arithmetic and reads no position. Neither can manufacture the other's evidence.
    #
    # Measured over the whole corpus (27 pages): 86 lines proposed, 4 admitted — exactly
    # cbh page 0's four panel totals, zero false admissions.
    cells_by_line = {}
    for i in range(len(lines)):
        h = place_indexed(runs[i], measures, min_cells=1)
        if h:
            cells_by_line[i] = h
    aggregates: dict = {}
    admitted = set(rows)
    for i in range(len(lines)):
        if i in admitted:
            continue
        h = cells_by_line.get(i)
        # PROPOSER: places into at least one measure column, carries no ink in the key
        # column and none in the index block outside the rectangle.
        if not h or key_col in h or index_ink(runs[i]):
            continue
        occupied = {k: t for k, t in h.items() if not is_blank(t)}
        if not (measures & set(occupied)):
            continue
        members = aggregate_members(i, admitted, set(aggregates))
        # DISPOSER: exact arithmetic over the member rows' cells.
        if confirms_aggregate(occupied, [cells_by_line[m] for m in members
                                         if m in cells_by_line]):
            aggregates[i] = members
            admitted.add(i)
            rows.append(i)
            refusals.pop(i, None)
        elif members and all(_decimal(t) is not None for t in occupied.values()):
            # The arithmetic actually SPOKE, so the record names the rule that decided.
            # Every other candidate keeps the reason that already refused it, which is why
            # apple's boxhead stays 'RowAddressability/no-key' and stem's carried-refusal
            # count is unchanged.
            refusals[i] = "AggregateWitness/no-reconciliation"
    rows.sort()

    for i in range(len(lines)):
        refusals.setdefault(i, "unplaceable") if i not in set(rows) else None

    return DataGrid(
        rows=tuple(rows),
        columns=tuple(columns),
        universe=universe,
        conforms=("ColumnHomogeneity", "NonDegeneracy", "RowAddressability",
                  "ColumnAlignment", "SeedFollowsUniverse", "AggregateWitness"),
        refusals=refusals,
        aggregates=aggregates,
    )


# ------------------------------------------------------------------------------ EMISSION


def emit_data_grid(g: "Graph", grid: "DataGrid", lines: list, doc_uri: "URIRef",
                   page: int, grid_uri: "URIRef | None" = None) -> "URIRef":
    """Emit the grid as `tab:` triples, with a `dec:DecisionHolon` recording its admission.

    The grid becomes an ASSERTED object with identity and provenance — the change from
    every grid-adjacent class in `tab.ttl`, which are documented "transient ... never
    asserted into a holon". After this, the question "why is this the data grid?" is
    answerable from the graph alone rather than from a Python dict:

        ?d a dec:DecisionHolon ; dec:chosen ?grid ; dec:optionSpace ?candidate .
        ?grid tab:conformsTo tab:ColumnHomogeneity , tab:RowAddressability , ...
        ?rejected dec:rejectedBecause "HeterogeneousColumn/every-measure" .

    Each refused line is carried, never dropped (§5): it is emitted as a rejected option
    on the decision, with the axiom that refused it. That is the "refuted this, this and
    this" half of the record, as triples.
    """
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF, XSD

    grid_uri = grid_uri or URIRef(f"{doc_uri}#p{page}-datagrid")
    dec_uri = URIRef(f"{grid_uri}-admission")

    g.add((grid_uri, RDF.type, TAB.DataGrid))
    g.add((grid_uri, RDF.type, TAB[grid.grid_type]))
    g.add((grid_uri, TAB.onPage, Literal(page, datatype=XSD.integer)))
    g.add((grid_uri, TAB.universeSource,
           TAB.DecorationUniverse if grid.universe == "decoration" else TAB.AlignmentUniverse))
    g.add((grid_uri, PROV.wasDerivedFrom, doc_uri))

    for k, col in enumerate(grid.columns):
        c_uri = URIRef(f"{grid_uri}-c{k}")
        g.add((c_uri, RDF.type, TAB.GridColumn))
        if col.is_measure:
            g.add((c_uri, RDF.type, TAB.MeasureColumn))
        g.add((grid_uri, TAB.hasGridColumn, c_uri))
        g.add((c_uri, TAB.x0, Literal(round(col.x0, 2), datatype=XSD.decimal)))
        g.add((c_uri, TAB.x1, Literal(round(col.x1, 2), datatype=XSD.decimal)))
        if col.family:
            g.add((c_uri, TAB.columnFamily, TAB[col.family]))

    for r_i, line_idx in enumerate(grid.rows):
        line = lines[line_idx]
        r_uri = URIRef(f"{grid_uri}-r{r_i}")
        g.add((r_uri, RDF.type, TAB.LeafRow))
        g.add((grid_uri, TAB.hasGridRow, r_uri))
        g.add((r_uri, PROV.wasDerivedFrom,
               URIRef(f"{doc_uri}#p{page}-line{line_idx}")))
        placed = _place_for_emit(line, grid)
        for k, (text, x0, x1) in sorted(placed.items()):
            e_uri = URIRef(f"{grid_uri}-r{r_i}c{k}")
            g.add((e_uri, RDF.type, TAB.EntryCell))
            g.add((grid_uri, TAB.hasDataCell, e_uri))
            g.add((e_uri, TAB.atRow, r_uri))
            g.add((e_uri, TAB.atColumn, URIRef(f"{grid_uri}-c{k}")))
            g.add((e_uri, TAB.cellText, Literal(text)))
            g.add((e_uri, TAB.onPage, Literal(page, datatype=XSD.integer)))
            # the cell's own ink extent, required by tab:EntryCellPhysicalShape
            b = URIRef(f"{e_uri}-bbox")
            g.add((b, RDF.type, TAB.BBox))
            g.add((b, TAB.x0, Literal(round(x0, 2), datatype=XSD.decimal)))
            g.add((b, TAB.y0, Literal(round(line.top, 2), datatype=XSD.decimal)))
            g.add((b, TAB.x1, Literal(round(x1, 2), datatype=XSD.decimal)))
            g.add((b, TAB.y1, Literal(round(line.bottom, 2), datatype=XSD.decimal)))
            g.add((e_uri, TAB.hasBBox, b))

    # the admission record: conformance on one side, every refusal on the other
    g.add((dec_uri, RDF.type, DEC.DecisionHolon))
    g.add((dec_uri, DEC.chosen, grid_uri))
    g.add((dec_uri, DEC.optionSpace, grid_uri))
    g.add((grid_uri, TAB.admittedBy, dec_uri))
    for axiom in grid.conforms:
        g.add((grid_uri, TAB.conformsTo, TAB[axiom]))
    for line_idx, reason in sorted(grid.refusals.items()):
        if line_idx in grid.rows:
            continue
        o_uri = URIRef(f"{grid_uri}-refused{line_idx}")
        g.add((o_uri, RDF.type, TAB.RefusedRow))
        g.add((dec_uri, DEC.optionSpace, o_uri))
        g.add((o_uri, DEC.rejectedBecause, Literal(reason)))
        g.add((o_uri, PROV.wasDerivedFrom,
               URIRef(f"{doc_uri}#p{page}-line{line_idx}")))
    return grid_uri


def _place_for_emit(line, grid: "DataGrid") -> dict:
    """Re-place one admitted line into the grid's columns: {col: (text, x0, x1)}."""
    bounds = [c.x0 for c in grid.columns] + [grid.columns[-1].x1]
    measures = set(grid.measures)
    hit: dict = {}
    for r in absorb_unit_markers(ink_runs(line)):
        if r.x1 <= bounds[0] - 0.5 or r.x0 >= bounds[-1] + 0.5:
            continue
        centre = (r.x0 + r.x1) / 2
        k = next((j for j in range(len(grid.columns))
                  if bounds[j] <= centre < bounds[j + 1]), None)
        if k is None:
            continue
        if k in hit and k not in measures:
            t, a, _ = hit[k]
            hit[k] = (f"{t} {r.text}", a, r.x1)      # stub levels share one cell's extent
        else:
            hit[k] = (r.text, r.x0, r.x1)
    return hit


def page_has_table(pdf_path: str, page_number: int = 0, gap: float = GAP) -> bool:
    """Does this page carry a table at all? The grid gate, as a page-level verdict.

    Modal ink-run count per text line: more than one run means the lines are laid out in
    columns, exactly one means prose. Measured across the whole corpus this keeps 17 of
    27 pages, and the verdict is IDENTICAL for every separator from 3pt to 20pt — `gap`
    only has to fall between prose word-spacing and column gutters, and the margin is
    about tenfold (prose collapses to one run at 3pt while tables survive past 33pt).

    Its purpose is to separate *nothing to read* from *failed to read*. Without it a page
    that yields no cells scores a perfect 1.0 whether it is a page of prose or a table
    the reader could not handle — measured on 11 of 27 corpus pages (R72)."""
    lines = [l for l in text_lines(extract_words(pdf_path, page_number)) if l.words]
    if not lines:
        return False
    counts = [len(ink_runs(l, gap)) for l in lines]
    return Counter(counts).most_common(1)[0][0] > 1
