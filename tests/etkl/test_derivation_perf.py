"""Scaling guard for the row-count-sensitive SPARQL derivations.

Audit (2026-07-20): of all vocab/queries/*.rq, four read body-row cells (tab:GridCell /
tab:atGridRow) and can scale with row count — header-body-split, stub-data-split, looks-transposed,
transpose-coherent. The rest read tab:HeaderWord / column markers / the recipe graph (few nodes) and
are not row-count-sensitive. This guard exists so a future edit cannot silently reintroduce an
O(n^2) cliff.

WHAT THIS FILE USED TO DO, AND WHY IT WAS WRONG (2026-08-10). Until now each query was pinned to an
absolute wall-clock bound, `_BOUND_S = 2.0`, commented "generous enough to be machine-independent".
Measurement refutes that claim: stub-data-split.rq at 50 rows takes 0.86s on the author's Mac and
~2.0-2.05s on GitHub's shared runners (~2.4x slower), and the bound produced three CI failures, each
a hair over — 2.03s, 2.007s, 2.048s — every one of which passed on a plain re-run. The bound was not
catching a regression; it was encoding one laptop's speed. Measured scaling over n = 1..64 is
sub-linear to linear for three of the four queries: there was no O(n^2) cliff for it to catch.

WHAT REPLACES IT. The stated intent — "no O(n^2) cliff" — is a claim about the scaling EXPONENT, so
the oracle is a ratio between two problem sizes, T(2N)/T(N). A ratio is machine-independent BY
CONSTRUCTION: machine speed is a common factor and cancels. A threshold set between the linear
expectation (~2x) and the quadratic expectation (~4x) discriminates two hypotheses instead of
encoding a machine.
"""
import os
import time

import pytest
from rdflib import Literal
from rdflib.namespace import XSD

from iladub.etkl import celltype

QDIR = os.path.join(os.path.dirname(celltype.__file__), "..", "..", "..", "vocab", "queries")

# The discriminator. Doubling the rows doubles LINEAR row work (ratio -> 2.0) and quadruples
# QUADRATIC row work (ratio -> 4.0). 3.0 is the midpoint BETWEEN THE TWO HYPOTHESES — it is derived
# from the two exponents being told apart, not fitted to any measurement, and it encodes no machine
# speed. It is deliberately NOT tuned: the measured margins below are wide (1.82 / 1.82 / 1.87
# against a 3.0 threshold), and if a query ever lands near 3.0 the right response is to find out why
# it is scaling super-linearly, never to move this number.
_QUADRATIC_RATIO = 3.0

# Timing noise is ONE-SIDED — a scheduler, a GC pause or a noisy neighbour can only make a run
# slower, never faster — so the MINIMUM of a few repeats is the least-biased estimator of the true
# cost. The mean would drag both points around with whatever noise the runner happens to carry.
_REPS = 3

# CHOOSING N — the sensitivity requirement, measured, not guessed.
#
# T(n) = overhead + row_work(n), where `overhead` is the per-call fixed cost (rdflib re-parses the
# .rq text on every call — celltype.run_scalar/run_ask read and compile it each time). If overhead
# dominates at N, then even a genuinely quadratic row_work yields a ratio near 1 and this test
# detects NOTHING. For a pure quadratic row_work to push the ratio past the discriminator:
#
#       (overhead + 4*rw) / (overhead + rw) > 3      <=>      rw > 2 * overhead
#
# so N must be large enough that row work is at least twice the overhead. N below is the smallest
# convenient size meeting `row_work(N) >= 4 * overhead` — a 2x margin over that 2x minimum — subject
# to a runtime cap. Overhead was measured by fitting T(n) = a + b*n over n = 1,2,4,8,16,32,64 (each
# point the min of 3 warmed runs, 4 body columns), with `a` the intercept:
#
#   query                  a (overhead)   b (per row)    N needed   N used   measured T(2N)/T(N)
#   header-body-split.rq     0.0729 s     0.001606 s      >= 182      200      1.82
#   looks-transposed.rq      0.0378 s     0.001495 s      >= 101      200      1.87
#   stub-data-split.rq       0.0437 s     0.016462 s      >=  11       25      1.82
#   transpose-coherent.rq    see below — the fitted intercept is NEGATIVE      100      3.31
#
# stub-data-split is held at N=25 by the runtime cap, not by sensitivity: it is by far the most
# expensive per row (b is 10x the others), and at N=25 its row work already exceeds its overhead
# 9.4-fold, which is well past the 4x bar.
_N = {
    "header-body-split.rq": 200,
    "looks-transposed.rq": 200,
    "stub-data-split.rq": 25,
    "transpose-coherent.rq": 100,
}


def _grid(nrows, ncols=4):
    # grouped-header-ish: row 0 Text header, then numeric body
    return [(r, c, ("Hdr%d" % c if r == 0 else str(r * 10 + c))) for r in range(nrows) for c in range(ncols)]


def _time_scalar(q, cells, ncols, bindings=None):
    g = celltype.grid_evidence(cells, ncols)
    t = time.perf_counter()
    celltype.run_scalar(os.path.join(QDIR, q), g, bindings)
    return time.perf_counter() - t


def _time_ask(q, cells, ncols):
    g = celltype.grid_evidence(cells, ncols)
    t = time.perf_counter()
    celltype.run_ask(os.path.join(QDIR, q), g)
    return time.perf_counter() - t


def _doubling_ratio(timer, N):
    """T(2N)/T(N), each point the minimum of _REPS runs, after a warm-up call.

    THE WARM-UP IS LOAD-BEARING, not hygiene. The first SPARQL query in a process pays a one-time
    grammar/parser setup that no later query pays. Measured cold-first vs warm-min at n=25, each in
    its own fresh interpreter: header-body-split 0.3508s vs 0.1169s (3.00x), looks-transposed
    0.2819s vs 0.0774s (3.64x), transpose-coherent 0.3563s vs 0.1610s (2.21x), stub-data-split
    0.6741s vs 0.4562s (1.48x). Un-warmed, that one-time cost lands almost entirely in T(N) — the
    first and smaller measurement — inflating it and DEPRESSING the ratio toward 1. It would make
    this guard blind, which is the one failure mode a scaling guard must not have.
    """
    timer(2)                                            # absorb the one-time parser setup
    t1 = min(timer(N) for _ in range(_REPS))
    t2 = min(timer(2 * N) for _ in range(_REPS))
    return t2 / t1, t1, t2


def _assert_not_quadratic(name, timer):
    N = _N[name]
    ratio, t1, t2 = _doubling_ratio(timer, N)
    assert ratio < _QUADRATIC_RATIO, (
        "%s scaled %.2fx from %d to %d rows (%.3fs -> %.3fs). Linear row work is ~2x and quadratic "
        "row work is ~4x, so anything at or above %.1fx is super-linear — look for a reintroduced "
        "pair self-join. Do NOT raise this threshold to make the test pass."
        % (name, ratio, N, 2 * N, t1, t2, _QUADRATIC_RATIO)
    )


def test_header_body_split_does_not_scale_quadratically():
    _assert_not_quadratic(
        "header-body-split.rq",
        lambda n: _time_scalar("header-body-split.rq", _grid(n), 4),
    )


def test_stub_data_split_does_not_scale_quadratically():
    _assert_not_quadratic(
        "stub-data-split.rq",
        lambda n: _time_scalar("stub-data-split.rq", _grid(n), 4, {"split": Literal(1, datatype=XSD.integer)}),
    )


def test_looks_transposed_does_not_scale_quadratically():
    _assert_not_quadratic(
        "looks-transposed.rq",
        lambda n: _time_ask("looks-transposed.rq", _grid(n), 4),
    )


@pytest.mark.xfail(
    strict=False,
    reason=(
        "KNOWN DEFECT, measured 2026-08-10, not introduced here: transpose-coherent.rq IS quadratic. "
        "It is the only one of the four never converted to the aggregation form — its comment header "
        "describes a pair self-join (`?a tab:atGridRow ?r ... ?b tab:atGridRow ?r`), while the other "
        "three say 'AGGREGATION FORM (linear in rows) ... replacing the O(cells^2) pair self-joins'. "
        "Log-log local exponent over n = 25,50,100,200,400 climbs 1.26 -> 1.55 -> 1.70 -> 1.89 and the "
        "doubling ratio climbs 2.39 -> 2.92 -> 3.26 -> 3.71, both converging on the quadratic values "
        "(2.0 and 4.0). Absolute cost: 0.39s at 50 rows but 13.7s at 400. The wall-clock bound this "
        "file used to carry never saw it, because it only ever looked at 50 rows. "
        "NOT strict=True: the margin at the affordable N=100 is only ~10% (3.31 measured vs 3.0), so a "
        "strict marker would itself become a borderline CI failure on a different runner — the exact "
        "pathology this file was rewritten to remove. Closing it means rewriting the query to "
        "aggregation form under the existing differential oracles in test_derivation_equiv.py; that is "
        "a change to a load-bearing derivation with documented hoist/quantifier semantics, so it is "
        "registered as a residue rather than smuggled into a test-infrastructure commit."
    ),
)
def test_transpose_coherent_does_not_scale_quadratically():
    _assert_not_quadratic(
        "transpose-coherent.rq",
        lambda n: _time_ask("transpose-coherent.rq", _grid(n), 4),
    )


def test_realistic_multirow_report_compiles_fast():
    """A ~50-row grouped-header table that HANGS on the pre-rewrite queries now compiles quickly
    (drives the real hierarchical pipeline: header_body_split + stub/orientation derivations).

    The 5.0s here is a HANG detector, not a scaling oracle, and it is deliberately left as an
    absolute bound: the property it guards ("this input terminates promptly instead of hanging") is
    a statement about wall-clock, and unlike the bound that was removed it has real headroom rather
    than a fingernail. Measured 2026-08-10, five fresh interpreters: 0.43 / 0.31 / 0.40 / 0.38 /
    0.39 s on this machine, i.e. ~0.9s at the ~2.4x GitHub-runner slowdown observed for the SPARQL
    derivations — over 5x under the bound. The removed _BOUND_S, by contrast, sat at 2.3x headroom
    locally and 0.98x on CI, which is why it failed three times.
    """
    from iladub.etkl.geometry import Word, Line
    from iladub.etkl.bands import Band
    from iladub.etkl.hierarchical import classify_hierarchical
    def w(t, x0, x1, top): return Word(t, x0, x1, top, top + 10.0)
    header = [w("Region", 150, 350, 0.0)]                       # spanning coarse header
    leaf = [w("Site", 10, 60, 12), w("Q1", 110, 160, 12), w("Q2", 210, 260, 12), w("Q3", 310, 360, 12)]
    rows = []
    for i in range(50):
        top = 24.0 + i * 12.0
        rows.append([w("s%d" % i, 10, 60, top), w(str(i), 110, 160, top),
                     w(str(i + 1), 210, 260, top), w(str(i + 2), 310, 360, top)])
    lines = [Line(tuple(header), 0.0, 10.0), Line(tuple(leaf), 12, 22)] + \
            [Line(tuple(r), 24.0 + i * 12.0, 34.0 + i * 12.0) for i, r in enumerate(rows)]
    band = Band(tuple(lines), 0.0, lines[-1].bottom)
    t = time.time()
    hreg = classify_hierarchical(band)
    dt = time.time() - t
    assert dt < 5.0, f"50-row hierarchical compile took {dt:.2f}s (hang guard; see the docstring)"
    assert hreg is not None, "the realistic 50-row report should classify, not escalate/hang"
