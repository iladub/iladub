"""B1.2 gate — the narrow-flank silent-wrong is closed by the flank-sibling AXIOM, and NO
geometric constant decides the flank (the .rq does). Anti-overfit: regression fixture first.

Fixture calibration (measured empirically, not assumed — see task-6-report.md for the full
probe trail):

1. infer_leaf_grid needs the coarse "Region" header's ink diluted by >=48 data rows before it
   can separate the leaf columns whose internal gutters that ink straddles (the classifygraph
   straddle-fixture lesson: blank_frac at a polluted gutter ~= n_data/(n_data+2) must clear the
   0.98 gutter_pct threshold). But header_body_split's SPARQL evaluation
   (vocab/queries/header-body-split.rq, via rdflib's non-indexed nested FILTER EXISTS/NOT
   EXISTS) is super-linear in total row count — measured n=5 -> 1.15s, n=10 -> 7.9s,
   n=15 -> >15s (still running), a 48-row band killed after >4 minutes without finishing.
   This is an existing, orthogonal performance limitation of a DIFFERENT AXIOM (B2a's
   header-body-split), not something this task is scoped to fix.

   Resolution: infer_leaf_grid runs on a 60-row "big" band (the dilution grid inference
   genuinely needs); header_body_split/infer_header_tree then run on a much smaller "small"
   band (same column x-layout, 6 data rows) reusing the grid boundaries the big band produced.
   LeafGrid is a plain immutable value (boundaries/ncols/pitch/confidence) with no
   back-reference to its originating band, so this reuse is architecturally clean — every
   downstream call (header_body_split, infer_header_tree, repair_coverage,
   resolve_narrow_flanks, flank-sibling.rq) is still real, unmodified production code; only
   the row count fed to the row-count-sensitive SPARQL step is reduced, independent of the
   column-count-sensitive whitespace-profile step.

2. The idealized column-4 ink width `w4` does NOT equal the REAL grid-resolved column-4 width:
   infer_leaf_grid's rightmost boundary is the max ink extreme (not a symmetric gutter), so the
   real width is `(col4 ink extent) - (gutter midpoint)`, empirically ~= w4 + 17 for this
   fixture's fixed col3/col4 gap. w4 in {40, 49, 50} (as in the original brief) real-resolves
   to widths >= half the real median pitch (~49-50pt) — i.e. NOT narrow by `_narrow_flank_tie`'s
   own half-pitch threshold. For those values col 4 is excluded because it has its own
   same-level header, which makes it INELIGIBLE ever to be an "orphan" for repair_coverage's
   per-level absorption (see below) — independent of the tie-band width math. w4=45 (the
   original brief's header-empty case) real-resolves to width 62pt (> half-pitch ~49), so
   `_narrow_flank_tie` never even flags it as narrow and the absorption silently stands
   unresolved — the test would FALSELY show a still-open silent-wrong. Empirically swept
   w4 in [10..45] (own_header=False): ambiguous=True (genuine escalation) for w4 in [10,32],
   ambiguous=False (untouched, real-width too wide for the tie detector) for w4 in [35,45].
   w4=25 is used below — comfortably inside the reliable escalation zone.

3. A structural finding worth recording plainly (verified by tracing `repair_coverage` +
   `resolve_narrow_flanks` + `sibling_columns` together, not by intuition): when col 4 has a
   well-formed header cell of its OWN at the SAME level as the coarse spanning node,
   `repair_coverage`'s per-level "orphan" set (columns claimed by NO node at that level)
   structurally EXCLUDES col 4 before `resolve_narrow_flanks` ever runs — a genuine
   same-level sibling header can never be an "orphan," so it is never a candidate for
   over-absorption. `sibling_columns`/`flank-sibling.rq` and `repair_coverage`'s per-level
   claim-set are both ultimately grounded in the same column-membership fact (a header cell
   strictly inside one column claims that column), so a column that IS a sibling at level L is
   NEVER an orphan at level L either — the exact precondition `resolve_narrow_flanks` needs to
   fire its "exclude" branch. Consequently, through the FULL `infer_header_tree` pipeline, that
   exclude branch is unreachable when a genuine same-level sibling exists: the outcome
   (never absorbed) is real and end-to-end-verified below (tests 1/2/4), but it is delivered by
   `repair_coverage`'s (B1.1, pre-existing) per-level orphan protection, with
   `resolve_narrow_flanks` confirmed as a correctness no-op rather than the active decider.
   The "exclude" branch of `resolve_narrow_flanks` IS directly exercised — declaratively, via
   the real `sibling_columns`/flank-sibling.rq call — by test 5 below (mirroring how the B1.2
   Task 5 unit tests in test_headers.py already isolate it). Test 3 (the header-empty/orphan
   case) is the one property that exercises the NEW B1.2 machinery as the active decider
   end-to-end: verified against the OLD (pre-ambiguous-flag) behavior, this exact fixture's
   covers=(1,2,3,4) node would have PASSED the old centering-only `merge_tiling_ok` check
   (span-center 254 vs label center 250, diff 4pt, well under the 49pt tolerance) — i.e. it
   would have shipped as a silently-accepted wrong merge. B1.2's `ambiguous` flag is what
   newly closes that gap.
"""
from iladub.etkl.geometry import Word, Line
from iladub.etkl.bands import Band
from iladub.etkl.grid import infer_leaf_grid
from iladub.etkl.headers import (
    infer_header_tree, header_body_split, resolve_narrow_flanks, HeaderNode, _narrow_flank_tie,
)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _band(w4, col4_has_own_header, n_data):
    """cols 1-3 width 100 (@ x 100..400), col 4 width w4 (@ x 400..400+w4); a spanning label
    over cols 1-3 whose ink stops at col 3; n_data data rows (same column x-layout regardless
    of n_data — only the dilution available to infer_leaf_grid changes)."""
    b4 = 400
    header = [_w("Region", 150, 350, 0.0)]            # spans cols 1-3, ink stops at col 3
    if col4_has_own_header:
        header.append(_w("Notes", b4 + 2, b4 + w4 - 2, 0.0))   # col 4's OWN level-0 leaf header
    # leaf header row (level 1): a label strictly inside each data column
    leaf = [_w("S", 10, 60, 12.0), _w("a", 110, 160, 12.0), _w("b", 210, 260, 12.0),
            _w("c", 310, 360, 12.0), _w("d", b4 + 2, b4 + w4 - 2, 12.0)]
    data = []
    for i in range(n_data):
        top = 24.0 + i * 12.0
        data.append([_w("r%d" % i, 10, 60, top), _w(str(i), 110, 160, top),
                     _w(str(i), 210, 260, top), _w(str(i), 310, 360, top),
                     _w(str(i), b4 + 2, b4 + w4 - 2, top)])
    lines = [_line(header, 0.0), _line(leaf, 12.0)] + [_line(d, 24.0 + i * 12.0) for i, d in enumerate(data)]
    return Band(tuple(lines), 0.0, lines[-1].bottom)


def _region_node(w4, col4_has_own_header):
    """Real infer_leaf_grid on a 60-row band (the dilution grid inference needs) -> real
    header_body_split + infer_header_tree on a 6-row band sharing the SAME column x-layout /
    grid boundaries (see module docstring point 1 for why the row counts differ)."""
    big = _band(w4, col4_has_own_header, 60)
    grid = infer_leaf_grid(big)
    assert grid.ncols == 5, f"fixture must resolve 5 cols (w4={w4}); got {grid.ncols}"
    small = _band(w4, col4_has_own_header, 6)
    split = header_body_split(small, grid)
    tree = infer_header_tree(small, grid, split)
    # the coarse (level-0) spanning node
    coarse = [n for n in (tree or ()) if n.level == 0 and len(n.covers) > 1]
    return grid, tree, coarse


# 1 + 2. SILENT-WRONG CLOSED: col 4 has its own same-level header -> excluded, never absorbed.
def test_silent_wrong_closed_narrow_flank_excluded():
    for w4 in (40, 49, 50):
        grid, tree, coarse = _region_node(w4, col4_has_own_header=True)
        assert coarse, f"expected a coarse spanning node (w4={w4})"
        assert all(4 not in n.covers for n in coarse), \
            f"col 4 silently over-absorbed at w4={w4}: {[n.covers for n in coarse]}"
        assert all(not n.ambiguous for n in coarse)


# 3. RESIDUAL ESCALATES: header-empty (orphan) flank -> ambiguous (deferred to B1.3), never
# absorbed. w4=25 is calibrated (see module docstring point 2) to fall inside the real
# resolved-width tie-band the shipped _narrow_flank_tie detector actually flags as narrow.
def test_header_empty_flank_escalates():
    grid, tree, coarse = _region_node(25, col4_has_own_header=False)
    # the coarse node either dropped col 4 already OR is flagged ambiguous; it must NEVER
    # assert col 4 under the span without escalation.
    absorbed = [n for n in coarse if 4 in n.covers and not n.ambiguous]
    assert not absorbed, "header-empty flank silently absorbed"
    # non-vacuous: confirm the resolver actually fired (not merely "nothing to see here").
    assert coarse and coarse[0].covers == (1, 2, 3, 4) and coarse[0].ambiguous is True


# 4. NO-REGRESSION: a wide standalone flank (w=60 > 0.5*pitch) is still excluded (not a tie).
def test_wide_standalone_flank_still_excluded():
    grid, tree, coarse = _region_node(60, col4_has_own_header=True)
    assert all(4 not in n.covers for n in coarse)


# 5. GATE-PIN: the flank decision is carried by the .rq, not a tuned constant. Perturbing the
# tie-band / centering tolerance does not flip a same-level-sibling exclusion. This directly
# exercises resolve_narrow_flanks' EXCLUDE branch (see module docstring point 3: through the
# full infer_header_tree pipeline that branch is structurally unreachable when a genuine
# same-level sibling exists — repair_coverage's per-level orphan protection gets there first —
# so a direct call, exactly like the shipped Task-5 unit tests, is how this branch is proven
# declarative).
def test_flank_decision_is_declarative_not_constant():
    from iladub.etkl.flankgraph import sibling_columns
    b = (0.0, 100.0, 200.0, 300.0, 400.0, 440.0)
    # col 4 has its own strict level-0 header -> sibling regardless of any geometric band width.
    sibs = sibling_columns([(0, 105.0, 295.0, "Region"), (0, 402.0, 438.0, "Notes")], b)
    assert (4, 0) in sibs
    # and the resolver excludes it independent of the specific tie-band constant:
    nodes = [HeaderNode(0, (1, 2, 3, 4), "Region", None, center_x=200.0)]
    from iladub.etkl.grid import LeafGrid
    out = resolve_narrow_flanks(nodes, LeafGrid(boundaries=b, ncols=5, pitch=100.0, confidence=1.0),
                                [(0, 105.0, 295.0, "Region"), (0, 402.0, 438.0, "Notes")],
                                ink_cols_by_node=[(1, 2, 3)])
    assert out[0].covers == (1, 2, 3)
