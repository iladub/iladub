# Kind Gate Is Load-Bearing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the measurement that stopped slice B into an executable guard, so a future "carry all candidates" refactor fails loudly with the reason attached instead of silently dropping 1,327 of stem's 2,152 asserted cells.

**Doc impact:** none for this plan file — the loop's `Doc impact: none` is declared in the design spec (`2026-08-07-kind-gate-load-bearing-design.md`).

**Architecture:** Two tasks, neither touching `src/`. Task 1 adds a characterisation test pinning the two suppressed-positive stem bands — kind, the two oracle results, and the caption-line evidence that explains them. Task 2 registers R71 and closes the spec.

**Tech Stack:** Python 3.11+/pytest, pdfplumber (via `page_bands`), the existing `regions` / `orientation` modules. No new dependency.

**Spec:** `docs/superpowers/specs/2026-08-07-kind-gate-load-bearing-design.md` — read it first, especially §4 (why un-gating regresses) and §5's insistence that the guard is a *characterisation* test, not an endorsement.

## Global Constraints

- **NO `src/` FILE MAY CHANGE, and no `.ttl`.** This is the structural guarantee that no verdict can move. If you believe a `src/` change is needed, **STOP and report** — do not make it.
- **This is a CHARACTERISATION test.** It pins behaviour that is currently **wrong but protective**: `looks_transposed` returns True on these bands and it should not. The docstring must say so explicitly. A later reader who mistakes this for an endorsement of the false positive will "fix" the test instead of the oracle.
- **No new vocabulary**, no query changes.
- **Do not attempt to fix `looks_transposed`.** Hardening it is the *next* loop and is named in spec §7. This loop only records the constraint.
- **Broken system git:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …`.
- **`timeout` does not exist on this macOS shell.** Run tests in the FOREGROUND.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (contains a space — quote it).
- **Branch:** `loop-kind-gate-load-bearing` — already created off `main`; the design spec is already committed there.
- Do **not** run the full suite or the corpus suites — those are the CONTROLLER's job.

---

### Task 1: The guard

**Files:**
- Create: `tests/etkl/test_kind_gate_is_load_bearing.py`

**Interfaces:**
- Consumes: `iladub.etkl.compile.page_bands(pdf_path, page_number)`; `iladub.etkl.regions.classify(band) -> ClassifiedRegion` (fields `.kind`, `.grid`, `.cells`, `.reason`), `.assign_cells(band, grid)`, `.RegionKind`; `iladub.etkl.orientation.looks_transposed(region)` and `.transpose_is_coherent(region)`.
- Produces: nothing later tasks depend on.

**Measured facts this test pins** (from the design spec §3, re-measured on this checkout):

| | stem p0 region2 | stem p2 region1 |
| --- | --- | --- |
| `kind` | `UNSUPPORTED_TABLE` | `UNSUPPORTED_TABLE` |
| `reason` | `header has 2 words but 17 columns` | `header has 1 words but 17 columns` |
| header line words | `['Friday, 31', 'July 2026']` | `['Date of Grain']` |
| `looks_transposed` | `True` | `True` |
| `transpose_is_coherent` | `False` | `False` |

**Why `assign_cells` is called explicitly.** `regions.py:109` assigns `cells` only for
`RECORD_TABLE`, so a `ClassifiedRegion` for these bands arrives with `cells=()` and the
orientation oracles would see nothing. The test rebuilds the region *with* cells — that is
exactly the evidence the kind gate withholds, and running the oracles on it is the whole point.

- [ ] **Step 1: Write the test** — create `tests/etkl/test_kind_gate_is_load_bearing.py`:

```python
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
```

- [ ] **Step 2: Run**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_kind_gate_is_load_bearing.py -v`
Expected: **all PASS** — this is a characterisation test of current behaviour, so there is no red phase. That is correct and expected here, not a sign the test is trivial.

**If any assertion FAILS, do not adjust it.** Report the actual value observed. A mismatch means the measurement in the spec is wrong on this checkout, and the controller needs that fact.

- [ ] **Step 3: Prove the guard can fail**

A test only ever seen passing is not yet known to work, and this one exists precisely to fire years from now. Demonstrate it:

Temporarily change `test_looks_transposed_is_a_false_positive_here`'s assertion to `is False`, run just that test, confirm it **FAILS** and that the failure message names the band and points at spec §7. Then revert and re-run to confirm it passes. Paste both outputs in your report.

- [ ] **Step 4: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add tests/etkl/test_kind_gate_is_load_bearing.py && git commit -m "test(loop-kind-gate): pin the two bands the kind gate protects

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Register R71 and close

**Files:**
- Modify: `docs/superpowers/residues.md`
- Modify: `docs/superpowers/specs/2026-08-07-kind-gate-load-bearing-design.md`

**Note for the controller:** Step 1 is a measurement — the controller runs the corpus suite and hands the implementer the result.

**Interfaces:** none.

- [ ] **Step 1 (CONTROLLER): confirm nothing moved**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q
```
Expected: 13 passed (stem 0.9655 / 2152 cells / chain [3]; CBH 0.9047). Since no `src/` file changed, any movement contradicts that premise — STOP and report.

- [ ] **Step 2: Add R71 to `docs/superpowers/residues.md`**

Use the existing house table format (`| # | Residue | Measured | Why deferred | What would close it |`). Read the file's tail first to confirm R71 is free and to match the prose density of recent rows. **Use R71, not R70** — R70 was used by an earlier loop and deleted when closed; reusing the number would be confusing.

- **Residue:** *The kind gate is load-bearing* — suppressing `looks_transposed` on an `UNSUPPORTED_TABLE` band is currently the only thing protecting two stem regions from a false-positive transposition reading. Slice B (carrying topology candidates instead of branching early) cannot start until that is fixed.
- **Measured:** spec `2026-08-07-kind-gate-load-bearing-design.md` §3/§4, 2026-08-07. Corpus-wide scan: only `stem` p0 region2 and p2 region1 are suppressed-positive (apple, capacity, WHO, CBH: none). Both have `looks_transposed=True`, `transpose_is_coherent=False`, and compile today at 586 and 741 asserted cells. Un-gating routes them to the incoherent branch, which escalates at 0 cells — 1,327 of stem's 2,152 asserted cells. `looks_transposed` misfires because the "header" is a caption line (`['Friday, 31', 'July 2026']`; `['Date of Grain']`) spanning 17 columns, producing the transposition signature without a transposition. Pinned by `tests/etkl/test_kind_gate_is_load_bearing.py`.
- **Why deferred:** hardening the oracle is a separate change to a recovery decision, and R10 may be its real root — R10 records `detect_bands` cutting one line too high so the report date lands inside the band, which is plausibly the very caption line these two regions read as a header. Fixing the oracle before checking R10 risks patching a symptom.
- **What would close it:** `looks_transposed` no longer firing on a caption-line header — either by closing R10, or by an open-world AXIOM/NEURAL change to `looks-transposed.rq` (**not** a tuned word-count threshold in Python, per CLAUDE.md §8). At that point the guard's assertions flip and slice B can be re-planned against a corpus with no known false positive.

- [ ] **Step 3: Close the spec**

Set `**Status:**` to `closed 2026-08-07` and add a short measured-results section carrying the controller's corpus numbers from Step 1, the guard's test count, and a criterion-by-criterion pass over §6. If any criterion was not met, say so plainly with its evidence — do not soften it. Assert nothing you were not handed or cannot read in the repo.

- [ ] **Step 4: Lints + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add docs/superpowers/residues.md docs/superpowers/specs/2026-08-07-kind-gate-load-bearing-design.md && git commit -m "docs(loop-kind-gate): close — R71 registered, slice B correctly scoped

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```
(The `PATH` prefix matters — `test_doc_governance.py` shells out to `git`; without it you get spurious `subprocess.CalledProcessError` setup errors that are a machine problem, not your edit.)

- [ ] **Step 5: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-07)

- **Spec coverage:** §1 (why the loop stopped) → the spec itself, closed in Task 2 Step 3; §2 (the conflation + the `cells` coupling) → Task 1's `_region_with_cells` docstring, which states why cells must be supplied; §3 (the scan) → Task 1's `SUPPRESSED_POSITIVE` constant and the kind/reason/header assertions; §4 (why un-gating regresses) → `test_the_coherence_oracle_refuses_the_transposed_reading` and `test_both_bands_carry_real_content`, plus R71's Measured column; §5 (what ships) → Tasks 1 and 2 exactly; §6 criteria → Task 2 Step 3's criterion pass, with the falsifiability requirement discharged by Task 1 Step 3; §7 (what slice B needs first) → R71's *what would close it*, including the R10-first instruction and the no-tuned-threshold constraint.
- **Placeholder scan:** none. The test file is complete; R71's four columns are given as prose bullets to be transcribed into the table.
- **Type consistency:** `_region_with_cells` returns `(band, region)` and every test unpacks it that way, including the one that only needs `region` (`_, region = …`). `SUPPRESSED_POSITIVE` is a tuple of `(page, idx)` used identically as parametrize argument, fixture key, and message interpolation.
- **One risk I checked rather than assumed:** the guard would be worthless if it silently skipped. `pytestmark` skips only when the corpus PDF is absent, and the controller's environment has it — Task 1 Step 2 runs with `-v`, so a skip would be visible rather than passing as a green dot.
