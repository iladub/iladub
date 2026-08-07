"""CHARACTERISATION GUARD — pins behaviour that is currently WRONG BUT PROTECTIVE.

Read this before changing anything it asserts (spec 2026-08-07-kind-gate-load-bearing-design.md).

`classify`'s kind gate decides which topologies a band is even offered: an
UNSUPPORTED_TABLE band never reaches `looks_transposed`. Slice B wants to remove that
early branch and carry topology candidates instead. Measured across the whole corpus,
exactly two bands are "suppressed-positive" — UNSUPPORTED_TABLE where `looks_transposed`
would return True — and BOTH are protected by the suppression:

    looks_transposed  -> True   (a FALSE POSITIVE: see the wrapped-header cause below)
    transpose_is_coherent -> False (the oracle correctly refuses it)

Both bands compile successfully today down the UNSUPPORTED -> hierarchical path (586 and
741 asserted cells). Un-gating routes them into the transposed branch, whose incoherent
`else` calls escalate_region(..., "TRANSPOSED", ...) and reports 0 asserted cells — so
1,327 of stem's 2,152 asserted cells would go to zero.

THIS TEST DOES NOT ENDORSE `looks_transposed` RETURNING True HERE. It is wrong: both bands
carry a multi-row WRAPPED column header. `classify_evidence` reads header words from
`band.lines[0]` only, and `assign_cells` has no header/body split, so the wrapped header's
own trailing lines enter the cell grid as body rows, seeding Text cells into every column
and destroying the column type-homogeneity whose absence `looks_transposed` tests for —
producing the transposition signature (one type-homogeneous row, no type-homogeneous
column) without any transposition being present. Verified by ablation: dropping only the
leading line leaves `looks_transposed=True` on both bands; only stripping the whole
wrapped-header block flips both to `RECORD_TABLE`. Routing the orientation oracles' body-cell
evidence through a header/body split is the NEXT loop (spec §7). R10 was checked as a
possible root cause and is refuted by this same ablation (p2 has no report date at all and
fails identically) — see spec §7 and residue R71.

When that hardening lands, `looks_transposed` will return False here and these assertions
SHOULD fail. Update them then — deliberately, with the corpus re-measured. Do not "fix"
this test by relaxing it while the oracle still misfires; that is the silent-regression
path this guard exists to block.

WHAT THIS FILE DOES AND DOES NOT GUARD: everything above calls `regions.classify()` and
the `orientation` oracles directly — it pins the FACTS that justify the kind gate, not
the gate's EFFECT. A pure routing change at compile.py (e.g. deleting the
`RECORD_TABLE`/`UNSUPPORTED_TABLE` if/else) would leave `region.kind`,
`looks_transposed`, and `transpose_is_coherent` all unchanged, so every test above would
keep passing while the regression happened anyway. `test_page0_region2_still_compiles_through_the_unsupported_path`
below closes that hole for page 0's band by exercising the real `compile_tables` path.
Page 2's band is NOT guarded this way — standalone it compiles to `escalated`/0 cells;
its 741 asserted cells exist only under `compile_document`'s cross-page header carry
(~150s to run), so that half of the regression is recorded as a residue (R71) rather
than pinned here.

NOTE ON "FAILS LOUDLY": `corpus/` is gitignored and not fetched in CI, so this guard
`skipif`s (see `pytestmark` below) rather than failing there — it only fails loudly on a
machine where the corpus doc is present. This is existing house convention, not
introduced by this file; `tests/test_corpus_stem.py` and `tests/test_cbh_e2e.py` skip
the same way.
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
def test_the_header_is_a_multi_row_wrapped_header(suppressed, key, n_header_words, ncols):
    """WHY the oracle misfires: `band.lines[0]` — a 1-2 word line spanning 17 columns — is
    only the TOP of a multi-row wrapped column header, not the whole header. Pinning this
    keeps the diagnosis attached to the evidence, so the next loop knows what to fix
    (route the orientation oracles through a header/body split — spec §7; R10 was checked
    and refuted as the cause, see spec §7 and R71)."""
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


def test_page0_region2_still_compiles_through_the_unsupported_path():
    """THE ROUTING GUARD — the rest of this file pins the oracle facts that JUSTIFY the
    kind gate; this pins its EFFECT. If a future change lets this band reach the
    transposed branch, `looks_transposed` fires, the coherence oracle refuses, and the
    incoherent `else` escalates it at 0 cells (compile.py's
    `escalate_region(..., "TRANSPOSED", ...)`). That is the 586-cell half of the
    1,327-cell regression this whole file exists to prevent, and it is the ONLY
    assertion here that would catch it.

    Page 2's region1 is not guarded this way: standalone it compiles to
    `escalated / 0 cells`, and its 741 asserted cells exist only under
    `compile_document`'s cross-page header carry (~150s). Recorded in R71.
    """
    from iladub.etkl.compile import compile_tables
    report = compile_tables(STEM, page_number=0)
    region = report.regions[2]
    assert region.verdict == "asserted", \
        f"stem p0 region2 no longer compiles ({region.verdict}, reason={region.reason!r}). " \
        "If the kind gate was removed, this is the regression spec §4 predicts — the band " \
        "reaches the transposed branch and escalates at 0 cells. Do not relax this."
    assert region.cells == 586, \
        f"stem p0 region2 asserted-cell count moved: {region.cells} (was 586). Re-measure " \
        "before changing this number — spec §3/§4."
