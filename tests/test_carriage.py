# tests/test_carriage.py
"""CARRIAGE — what the arc could not see until now: cells carried, not score.

The arc's ten `tab` criteria count escalation REASONS and its seven `etkl` criteria read
the document SCORE. Neither can see a cell-carriage defect. That is measured, not felt:
on 2026-09-16 the alignment-universe gate moved bfs page 5 from 404 placed cells to 496
(+92) and the document from 14251 triples to 15354 (+1103), while the document score held
at 0.8850746269 to ten decimal places — see [[R240]] and PR #239. Work that improves
carriage is therefore invisible to the arc BY CONSTRUCTION, which is why a criterion whose
oracle is CELLS AND TRIPLES exists at all (`prog:criterion:tab:11`).

Gate classification (CLAUDE.md §8): PROCEDURAL. It compiles a document and compares
integers. It decides nothing about any reading, carries no tolerance and no threshold —
the two figures below are a RECORDED MEASUREMENT of a specific tree, not a tuned constant.

THE STRICT XFAIL IS GONE, AND THAT IS THE RECORD OF THE BUILD. Until 2026-09-17 the first
test below carried `@pytest.mark.xfail(strict=True)`: `_boundaries_from_decoration` was
still consulted by `derive_data_grid`, page 5 read 404 cells / 14251 triples, and the
criterion it serves was authored `prog:met false`. The marker was the forcing function —
the day the blanket refusal landed the test XPASSed, and an XPASS under a strict marker is
a SUITE FAILURE, so the switch could not ship while the criterion stayed stale. It was
observed doing exactly that: `[XPASS(strict)] 1 failed, 1 passed` on the tree that first
carried the refusal. Marker and `prog:met` were then flipped in one reviewed act, which is
what keeps `prog:met` a reviewed assertion rather than a side effect (tests/arc-manifest.ttl,
"CODE NEVER WRITES THIS FILE").

Run locally (~5 min, one compile shared by both tests):
    ./.venv/bin/python -m pytest -m corpus tests/test_carriage.py -q
In CI the corpus is absent (`corpus/` is gitignored) and both tests SKIP — so GREEN CI IS
NOT EVIDENCE ABOUT THIS FILE, and a loop that changes carriage must run it by hand.
"""
import pytest

from tests.test_corpus import ENTRIES, require_pinned_edition, REPO

pytestmark = pytest.mark.corpus

BFS = "gov-stats/bfs-population-bilan-2023.pdf"

#: The reading the switch must produce, fixed by PR #239 (the gate) and PR #241 (identity,
#: 27/27 canton rows). Cells are counted on the ONE adopted RECORD_TABLE region of page 5,
#: which is where every placed cell on that page lives — measured 2026-09-16, `c9270bb`.
P5_CELLS_WHEN_CARRIED = 496
DOC_TRIPLES_WHEN_CARRIED = 15354

#: The control, and it passes TODAY. Page 6 carries 267 cells across six asserted regions
#: and the switch must not move it: a change that alters page 6 is not the change the
#: criterion asks for. Measured 2026-09-16 at `c9270bb`, on the same run as the figures
#: above. A pointwise pin beside a total one is what caught PR #241's mis-specified C2.
P6_CELLS = 267
P6_ASSERTED_REGIONS = 6


@pytest.fixture(scope="module")
def bfs():
    """Compile bfs ONCE for the whole module — the compile is the expensive part."""
    entry = next(e for e in ENTRIES if e["file"] == BFS)
    dest = require_pinned_edition(entry, REPO / "corpus")
    from iladub.etkl.document import compile_document

    return compile_document(str(dest))


def _page_cells(rep, n):
    return sum(r.cells for r in rep.pages[n].regions)


def test_bfs_p5_carries_the_row_label_and_percent_columns(bfs):
    """The row-label column and the final `%` column are CARRIED, not dropped.

    Both lie outside the decoration rectangle (label ends 85.65, `%` starts 516.18, the
    rectangle spans 124.3..495.3), so every row is admitted BECAUSE of ink the emitter
    then never carries — [[R238]], and [[R239]] is the same defect on the other column.
    Judged on cells and triples, NEVER on the score: [[R240]] records that the score is an
    ink-token ratio and did not move a digit while these 92 cells appeared."""
    assert _page_cells(bfs, 5) == P5_CELLS_WHEN_CARRIED
    assert len(bfs.graph) == DOC_TRIPLES_WHEN_CARRIED


def test_bfs_p6_carriage_is_untouched(bfs):
    """THE CONTROL. Page 6 is not a decoration page and must read the same either way.

    Without it the criterion could be met by any change that moves cells ANYWHERE, which
    is how a carriage gauge would rot into the same blindness it was authored to repair."""
    asserted = [r for r in bfs.pages[6].regions if r.verdict == "asserted"]
    assert _page_cells(bfs, 6) == P6_CELLS
    assert len(asserted) == P6_ASSERTED_REGIONS
