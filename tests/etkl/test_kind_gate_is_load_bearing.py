"""CHARACTERISATION GUARD — pins behaviour that is currently WRONG BUT PROTECTIVE.

Read this before changing anything it asserts (spec 2026-08-07-kind-gate-load-bearing-design.md).

`classify`'s kind gate decides which topologies a band is even offered: an
UNSUPPORTED_TABLE band never reaches `looks_transposed`. Slice B wants to remove that
early branch and carry topology candidates instead. Measured across the whole corpus,
exactly two bands are "suppressed-positive" — UNSUPPORTED_TABLE where `looks_transposed`
would return True — and BOTH are protected by the suppression:

    looks_transposed  -> True   (a FALSE POSITIVE: the "header" is a caption line)
    transpose_is_coherent -> False (the oracle correctly refuses it)

Both bands compile successfully today down the UNSUPPORTED -> hierarchical path (586 and
741 asserted cells). Un-gating routes them into the transposed branch, whose incoherent
`else` calls escalate_region(..., "TRANSPOSED", ...) and reports 0 asserted cells — so
1,327 of stem's 2,152 asserted cells would go to zero.

THIS TEST DOES NOT ENDORSE `looks_transposed` RETURNING True HERE. It is wrong: a 1-2 word
caption line spanning 17 columns produces the transposition signature (one type-homogeneous
row, no type-homogeneous column) without any transposition being present. Hardening that
oracle is the NEXT loop (spec §7), and R10 may be its real root cause.

When that hardening lands, `looks_transposed` will return False here and these assertions
SHOULD fail. Update them then — deliberately, with the corpus re-measured. Do not "fix"
this test by relaxing it while the oracle still misfires; that is the silent-regression
path this guard exists to block.
"""
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STEM = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-stem-2026-07-31.pdf")
pytestmark = pytest.mark.skipif(not os.path.exists(STEM), reason="corpus doc not fetched")

# (page, band index) of the two suppressed-positive bands, measured corpus-wide.
SUPPRESSED_POSITIVE = ((0, 2), (2, 1))


def _region_with_cells(page_number, idx):
    """The band's ClassifiedRegion, rebuilt WITH cells.

    `regions.py` assigns cells only for RECORD_TABLE, so an UNSUPPORTED_TABLE region
    arrives with `cells=()` and the orientation oracles would see nothing. Supplying them
    is precisely the evidence the kind gate withholds.
    """
    from dataclasses import replace
    from iladub.etkl.compile import page_bands
    from iladub.etkl.regions import classify, assign_cells
    band = list(page_bands(STEM, page_number))[idx]
    region = classify(band)
    assert region.grid is not None, f"stem p{page_number} region{idx} has no grid"
    return band, replace(region, cells=assign_cells(band, region.grid))


@pytest.fixture(scope="module")
def suppressed():
    """Both bands, classified once. page_bands parses a page, so keep this module-scoped."""
    return {key: _region_with_cells(*key) for key in SUPPRESSED_POSITIVE}


@pytest.mark.parametrize("key", SUPPRESSED_POSITIVE)
def test_the_band_is_unsupported_so_the_transposed_oracle_is_never_offered(suppressed, key):
    """The gate: kind decides which topologies are considered at all."""
    from iladub.etkl.regions import RegionKind
    _, region = suppressed[key]
    assert region.kind is RegionKind.UNSUPPORTED_TABLE, \
        f"stem p{key[0]} region{key[1]} is no longer UNSUPPORTED_TABLE ({region.kind.name}) — " \
        "the suppressed-positive set has changed; re-run the corpus scan in spec §3"


@pytest.mark.parametrize("key", SUPPRESSED_POSITIVE)
def test_looks_transposed_is_a_false_positive_here(suppressed, key):
    """WRONG BUT PROTECTIVE. If this starts failing, the oracle was hardened — good.
    Re-measure the corpus and update this guard deliberately."""
    from iladub.etkl.orientation import looks_transposed
    _, region = suppressed[key]
    assert looks_transposed(region) is True, \
        f"stem p{key[0]} region{key[1]}: looks_transposed no longer fires. If the oracle was " \
        "hardened (spec §7), re-measure and update this guard — do not relax it."


@pytest.mark.parametrize("key", SUPPRESSED_POSITIVE)
def test_the_coherence_oracle_refuses_the_transposed_reading(suppressed, key):
    """This refusal is what makes un-gating a REGRESSION rather than a recovery: the
    incoherent branch escalates at 0 asserted cells."""
    from iladub.etkl.orientation import transpose_is_coherent
    _, region = suppressed[key]
    assert transpose_is_coherent(region) is False, \
        f"stem p{key[0]} region{key[1]}: the coherence oracle now ACCEPTS the transposed " \
        "reading. That changes the whole finding — re-run the measurement in spec §3/§4."


@pytest.mark.parametrize("key,n_header_words,ncols", [((0, 2), 2, 17), ((2, 1), 1, 17)])
def test_the_header_is_a_caption_line(suppressed, key, n_header_words, ncols):
    """WHY the oracle misfires: a 1-2 word line spanning 17 columns is a caption, not a
    header. Pinning this keeps the diagnosis attached to the evidence, so the next loop
    knows what to harden against (and can check R10 first)."""
    band, region = suppressed[key]
    assert len(band.lines[0].words) == n_header_words, \
        f"header word count changed: {[w.text for w in band.lines[0].words]}"
    assert region.reason == f"header has {n_header_words} words but {ncols} columns", \
        f"reason changed: {region.reason!r}"


def test_both_bands_carry_real_content(suppressed):
    """The stake. These are not fringe bands — together they are the majority of stem's
    asserted cells, which is why un-gating them silently would be so costly."""
    for key in SUPPRESSED_POSITIVE:
        _, region = suppressed[key]
        assert len(region.cells) > 100, \
            f"stem p{key[0]} region{key[1]} has only {len(region.cells)} cells"
