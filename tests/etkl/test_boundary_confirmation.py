"""Loop G attempt 2 — header confirmation of candidate column boundaries (the AXIOM).

A candidate boundary (an interior gutter the author's rules left out) becomes a column ONLY if the
header region places glyph ink strictly on both sides of it within its author interval, with no
header glyph straddling it. This is the evidence tab:CoverageShape enforced by CRASHING attempt 1
(a phantom column no header covers), consulted eagerly instead.

Coordinates are MEASURED, not invented: the GrainCorp leaf-header char runs are Completed
716.3-743.6, Commodity 764.2-793.5, Total 805.8-818.4, and the candidates are 753.7 and 798.7 in
the author interval [715.2, 829.92]. The aligned-fixture cases are the counter-example that killed
attempt 1. See docs/superpowers/specs/2026-07-30-header-confirmed-refinement-design.md §2.
"""
from iladub.etkl.boundary import confirmed_boundaries


class _G:
    """Minimal glyph: the runner only reads .x0/.x1."""
    def __init__(self, x0, x1):
        self.x0 = x0
        self.x1 = x1


# real measured GrainCorp leaf-header runs (each run stands in for its chars; extents are what count)
GRAIN = [_G(716.3, 743.6), _G(764.2, 793.5), _G(805.8, 818.4)]
GRAIN_CANDS = [(753.7, 715.2, 829.92), (798.7, 715.2, 829.92)]

# the counter-example's ID header ('I' 60-65.4, 'D' 65.4-70.8); its candidate is 73.5 in [50, 170]
ALIGNED_ID = [_G(60, 65.4), _G(65.4, 70.8)]


def test_both_sided_header_ink_confirms_both_real_boundaries():
    assert confirmed_boundaries(GRAIN, GRAIN_CANDS) == {753.7, 798.7}


def test_one_sided_header_ink_is_rejected():
    # THE COUNTER-EXAMPLE: the author labeled only the left side ('ID'); the phantom column has
    # no header ink, so the split that crashed attempt 1 is refused here.
    assert confirmed_boundaries(ALIGNED_ID, [(73.5, 50.0, 170.0)]) == set()


def test_straddling_glyph_rejects():
    # the fixture's Tonnes column: the 'n' glyph 310.8-316.2 contains the candidate 313.5 —
    # a label cannot be split through a glyph.
    glyphs = [_G(300, 305.4), _G(305.4, 310.8), _G(310.8, 316.2), _G(316.2, 321.6)]
    assert confirmed_boundaries(glyphs, [(313.5, 290.0, 395.0)]) == set()


def test_empty_header_region_confirms_nothing():
    assert confirmed_boundaries([], GRAIN_CANDS) == set()


def test_candidates_are_judged_independently():
    # ink around 753.7 only -> only it confirms; 810.0 has no right-side witness
    glyphs = [_G(716.3, 743.6), _G(764.2, 793.5)]
    assert confirmed_boundaries(glyphs, [(753.7, 715.2, 829.92), (810.0, 715.2, 829.92)]) == {753.7}


def test_no_candidates_short_circuits():
    assert confirmed_boundaries(GRAIN, []) == set()


def test_witness_must_lie_inside_the_interval():
    # header ink LEFT of the interval must not act as a left witness
    glyphs = [_G(30.0, 45.0), _G(764.2, 793.5)]          # left glyph outside [715.2, 829.92]
    assert confirmed_boundaries(glyphs, [(753.7, 715.2, 829.92)]) == set()
