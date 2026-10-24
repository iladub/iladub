# R334 + R336: spanners and caption lines — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** maintenance — closes [[R334]] and [[R336]]; moves `prog:criterion:tab:13`'s number (already met).

**Doc impact: increment.** Same as the spec: spanner and caption nodes on a grid, a moved corpus baseline, one new
recordings directory. No released meaning changes.

**Goal:** Fed H.4.1 p0 adopts its data grid, carrying the boxhead's spanners as a header tree and the table's own title and unit lines as region captions, so the truth scorer reads column paths that start with the author's spanners.

**Architecture:** `dispose_boxhead` gains two exact spanner checks (laminar, extent ⊆ group), and `carried_lines`/`emit_boxhead` carry the survivors as a leveled `tab:HeaderNode` tree. A new NEURAL worker in `src/iladub/etkl/caption.py` answers *which candidate lines are this table's own caption*. It is recorded under `readings/caption/`, disposed by exact address, contiguity and adjacency checks, and carried as `tab:RegionCaption` only. The adoption site in `compile.py` orders these as boxhead → spanners → captions → ledger.

**Tech Stack:** Python 3, rdflib, pySHACL (`inference="rdfs"`, `advanced=True`), BAML (`baml-py==0.222.0`), pytest (`-m corpus` for third-party documents).

**Spec:** `docs/superpowers/specs/2026-10-24-r334-r336-spanners-and-captions-design.md` (APPROVED 2026-10-24). Executors read both. The plan cites spec sections rather than restating them (plan rule 6).

## Global Constraints

- CLAUDE.md § 8 gate: classification as spec §4. **No tuned constant or tolerance anywhere.** A geometric caption heuristic ("the lines above the boxhead") is a review failure.
- Spanner refusals never fabricate. A dropped spanner leaves its line uncarried, which is the status quo (spec §3.1).
- A laminar violation drops **every spanner** of the reading and keeps the leaves (spec §8 ruling 2).
- The caption worker returns indices only, never text (spec §3.3). Caption nodes are `tab:RegionCaption` **only**, never `tab:SectionCaption`.
- **No existing boxhead recording is re-recorded** (spec §5a). `readings/boxhead/*.json` must be byte-unchanged at the end.
- The laminar check is the **only** guard on grid column-path ambiguity (spec §2). It carries a comment saying so, citing R89 (CLAUDE.md § Producer-side guards).
- Live recording budget: **one live caption ask per grid with candidate lines, across `corpus/` and `held-out/`, recorded once** (spec §8 ruling 1).
- Corpus runs are serial. Never run a corpus compile beside pytest. The baseline is regenerated once, after the last input edit (CLAUDE.md § Corpus baseline).
- Every task report carries a `## FALSIFICATION` block (CLAUDE.md plan rule 4). The tests below are propositions until falsified.
- Downward same-file citations: cite symbols, not lines (plan rule 7).

## Seams measured while writing this plan (2026-10-24, `main` at `25d561e`)

These are measurements. Two of them change what the spec says.

- **M1 — `tab:hasCaption` on a grid adds no new typing (spec §7, first bullet: RESOLVED).**
  `tab:hasCaption rdfs:domain tab:Table` (`vocab/ontology/tab.ttl:579`), but `emit_boxhead` already puts
  `tab:hasHeaderNode` and `tab:hasCell` on the grid, and both have `rdfs:domain tab:Table` (`tab.ttl:78-92`). So
  under `rdfs` every grid with a disposed label is **already** typed `tab:Table`. The caption disposal (Task 3)
  requires a surviving label, so captions are only ever emitted on such a grid. `grep "tab:Table" vocab/shapes/*.ttl`
  → only `tab-shapes.ttl:537` (`sh:class tab:Table` on a printed total's binding), and no `sh:targetClass tab:Table`.
  Task 4's corpus test re-checks this on Fed p0's real graph.
- **M2 — the spec's caption box cannot ride `tab:hasBBox`. DEVIATION from spec §3.3.**
  `tab:hasBBox rdfs:domain tab:Cell` (`tab.ttl:130-131`). Under `rdfs` a caption carrying it is inferred to be a
  `tab:Cell`, and `tab:WrappedCellShape` (`vocab/shapes/tab-physical-shapes.ttl:43-48`, `sh:targetClass tab:Cell`)
  refuses a `tab:Cell` with a `hasBBox` and no `cellText`/`unshownText`. `rowrole.emit_reading_evidence`'s
  docstring records the same trap for `tab:HeaderSourceCell`. **This plan therefore emits caption text, page and
  row, and no box.** `tab:onPage`'s domain is `tab:PageLocated` (`tab.ttl:124-125`), and nothing targets that
  class. The box half of R218 stays open, and Task 6 records it on R218's row. *Maintainer: if a box is wanted
  this loop, it needs a caption-scoped box property in `tab.ttl`, plus a conforming example and a negative test.
  That is a vocabulary change the spec did not scope.*
- **M3 — "candidate line" reduces to *every word in `other_words`*.** `dispose_boxhead` refuses unless every
  listed word is in exactly one list (`boxhead.py`, `dispose_boxhead`, "a listed word left unaccounted for" /
  "a word used twice"). So a line whose words are all `other_words` holds no spanner word, surviving or dropped,
  and spec §3.3's "no surviving spanner touches it" follows. Candidates exist only for a disposed (non-refused)
  boxhead.
- **M4 — there is no single-worker live switch.** `grep -rn "ILADUB_LIVE\|LIVE_WORKERS" src scripts` → nothing.
  R166 recorded "with only the boxhead reader live" from a scratchpad script (commit `0ffa420`, handoff text), because a
  fully live compile crashed on Fed (`UnshownCarriageError`). Task 5 does the same for captions.
- **M5 — the Fed truth floor is `{"table-1": {"CORRECT": 0}}`** (`tests/ground-truth/fed-h41-2025-01-02/floor.json`).
  The baseline's `truth.table-1` is CORRECT 0, LOST 45, MISATTACHED 71, MISSING 8, REFUSED 4, SPURIOUS 57
  (`tests/corpus-baseline/fed-h41-2025-01-02.json:790-801`). Fed p0 escalates 31 (same file, page 0).

## Review Focus

1. **A reading whose spanners all fail and whose leaves all stand** must emit exactly what `main` emits. Covered by Task 1 test `test_laminar_violation_drops_every_spanner_and_keeps_the_leaves` and Task 2 test `test_a_reading_without_spanners_emits_exactly_the_triples_it_emits_today`.
2. **Two spanners with the same column set on different lines** (a nested repeat) must nest rather than violate, and the parent of a leaf must be the *lower* one. Covered by Task 2 test `test_equal_sets_on_different_lines_nest_and_the_lower_one_is_innermost`.
3. **A caption answer naming a line that is not directly above the topmost surviving label**, for example one separated from it by a line holding a dropped spanner's words, must be NO CLAIM. Covered by Task 3 test `test_caption_not_adjacent_to_the_topmost_label_is_no_claim`.
4. **A grid with no candidate lines** must never ask the worker, so recording costs nothing there. Covered by Task 3 test `test_no_candidate_lines_asks_nothing`.
5. **A caption recording keyed like a boxhead recording** must never collide with one. Covered by Task 3 test `test_the_caption_key_differs_from_the_boxhead_key_for_the_same_listing`.

---

### Task 1: Spanner disposal (laminar, extent ⊆ group)

**Files:**
- Modify: `src/iladub/etkl/boxhead.py`: `DisposedBoxhead`, `dispose_boxhead`, and the module docstring's last paragraph ("Spanners are therefore REPORTED and not yet carried …"), which this loop falsifies.
- Test: `tests/etkl/test_boxhead.py`

**Interfaces:**
- Produces: `DisposedBoxhead.spanners` now holds **only surviving** spanners, still as `(first, last, addresses)`, in reading order. New fields: `spanners_dropped: tuple[int, ...]` (indices into `reading.spanning_labels`) and `spanner_refusal: str | None` (`"spanners are not laminar"` when check (a) fires, else `None`). A whole-reading refusal leaves all three empty or `None`, as today.

**Invariants (spec §3.1):**
- A node is `(column set, topmost block line)`. A leaf is a one-column node on its topmost line, and a spanner covers `first..last` on its topmost line.
- **(a) laminar:** for every pair of nodes whose column sets intersect, the one on the strictly lower line has a set ⊆ the other's. Two intersecting nodes on the **same** topmost line violate, and that includes equal sets. Violation → `spanners=()`, every spanner index goes in `spanners_dropped`, `spanner_refusal` is set, and leaves are untouched.
- **(b) extent:** run only if (a) passed. On every line a spanner occupies, its ink run on that line (`min x0 .. max x1` of its words there) satisfies `columns[first].x0 <= lo` and `hi <= columns[last].x1`. A failure drops that spanner only. Only **surviving leaves** take part in (a). A dropped leaf is not a node.
- The order is fixed: leaves are placed first (existing check 3), then (a) over surviving leaves and all proposed spanners, then (b).

- [ ] **Step 1: Write the failing tests** (append to `tests/etkl/test_boxhead.py`; they reuse its `_w` helper)

```python
def _wide_grid():
    """Four columns at [0,100) … [300,400); block lines 0-2 refused, rows 3-4 admitted."""
    cols = tuple(SimpleNamespace(x0=float(a), x1=float(a + 100)) for a in (0, 100, 200, 300))
    return SimpleNamespace(rows=(3, 4), columns=cols,
                           refusals={j: "HeterogeneousColumn/every-measure" for j in (0, 1, 2)})


def _wide_lines():
    """L0 spans cols 1-3; L1 has two words, over cols 1-2 and col 3; L2 holds the leaves."""
    return [SimpleNamespace(words=[_w("Group", 150, 350)], top=0, bottom=1),
            SimpleNamespace(words=[_w("Left", 120, 280), _w("Right", 310, 390)], top=2, bottom=3),
            SimpleNamespace(words=[_w("Id", 10, 40), _w("a", 140, 160), _w("b", 240, 260),
                                   _w("c", 340, 360)], top=4, bottom=5),
            SimpleNamespace(words=[_w("x", 10, 20), _w("1", 140, 150), _w("2", 240, 250),
                                   _w("3", 340, 350)], top=6, bottom=7),
            SimpleNamespace(words=[_w("y", 10, 20), _w("4", 140, 150), _w("5", 240, 250),
                                   _w("6", 340, 350)], top=8, bottom=9)]


def _leaves():
    return ((0, ((2, 0),)), (1, ((2, 1),)), (2, ((2, 2),)), (3, ((2, 3),)))


def test_a_laminar_reading_keeps_every_spanner():
    r = BoxheadReading(leaf_labels=_leaves(),
                       spanning_labels=((1, 3, ((0, 0),)), (1, 2, ((1, 0),)), (3, 3, ((1, 1),))))
    d = dispose_boxhead(r, _wide_lines(), (0, 1, 2), _wide_grid())
    assert d.refused is None and d.spanner_refusal is None
    assert [s[:2] for s in d.spanners] == [(1, 3), (1, 2), (3, 3)] and d.spanners_dropped == ()


def test_laminar_violation_drops_every_spanner_and_keeps_the_leaves():
    """(1,2) on L1 and (2,3) on L1 cross: one line, intersecting sets."""
    r = BoxheadReading(leaf_labels=_leaves(),
                       spanning_labels=((1, 3, ((0, 0),)), (1, 2, ((1, 0),)), (2, 3, ((1, 1),))))
    d = dispose_boxhead(r, _wide_lines(), (0, 1, 2), _wide_grid())
    assert d.refused is None and d.spanner_refusal == "spanners are not laminar"
    assert d.spanners == () and d.spanners_dropped == (0, 1, 2)
    assert sorted(d.labels) == [0, 1, 2, 3]


def test_a_lower_spanner_wider_than_the_one_above_violates():
    r = BoxheadReading(leaf_labels=_leaves(),
                       spanning_labels=((2, 3, ((0, 0),)), (1, 3, ((1, 0), (1, 1)))))
    d = dispose_boxhead(r, _wide_lines(), (0, 1, 2), _wide_grid())
    assert d.spanners == () and d.spanner_refusal == "spanners are not laminar"


def test_extent_too_narrow_drops_that_spanner_only():
    """`Right` (310-390) claimed over cols 2-3 is inside [200,400): stands. `Left` (120-280) claimed over
    col 2 alone overflows [200,300) on the left: dropped."""
    r = BoxheadReading(leaf_labels=_leaves(),
                       spanning_labels=((1, 3, ((0, 0),)), (2, 2, ((1, 0),)), (3, 3, ((1, 1),))))
    d = dispose_boxhead(r, _wide_lines(), (0, 1, 2), _wide_grid())
    assert d.spanner_refusal is None and d.spanners_dropped == (1,)
    assert [s[:2] for s in d.spanners] == [(1, 3), (3, 3)]
```

- [ ] **Step 2: Run them, expect FAIL** (`AttributeError: … 'spanner_refusal'`)

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/etkl/test_boxhead.py -q`

- [ ] **Step 3: Implement** the invariants above in `dispose_boxhead`. Put a comment at the laminar check that states it is the only guard on grid column-path ambiguity and may never be deleted as a duplicate (spec §2, R89). Rewrite the module docstring's spanner paragraph to name both checks and the one blind spot, *too wide passes*.

- [ ] **Step 4: Run** `PYTHONPATH=src .venv/bin/python -m pytest tests/etkl/test_boxhead.py -q`. Expect every test to pass, the existing ones included.

- [ ] **Step 5: FALSIFICATION.** (i) Make the same-line case pass, so that intersecting nodes on one line count as nested. `test_laminar_violation…` must FAIL. (ii) Delete check (b). `test_extent_too_narrow…` must FAIL. Restore with `cp` from a saved copy and show the suite green.

- [ ] **Step 6: Commit** `R334: dispose a boxhead's spanners (laminar, extent within group)`.

---

### Task 2: Spanner carriage (carried lines, a leveled header tree)

**Files:**
- Modify: `src/iladub/etkl/boxhead.py`: `carried_lines`, `emit_boxhead`
- Test: `tests/etkl/test_boxhead.py`; `tests/etkl/test_boxhead_fed_tree.py` (new, `@pytest.mark.corpus`)

**Interfaces:**
- Consumes: `DisposedBoxhead.spanners` (survivors) from Task 1.
- Produces: `carried_lines(lines, block, disposed)`, unchanged signature, now also counting surviving spanner words. `emit_boxhead(g, grid_uri, lines, block, disposed, page) -> int`, unchanged signature. It returns leaves + spanners emitted. Spanner URIs are `f"{grid_uri}-s{n}"` / `f"{grid_uri}-ls{n}"`, where `n` is the spanner's index in `disposed.spanners`. Leaf URIs are unchanged.

**Invariants (spec §3.2):**
- A spanner node carries `tab:coversColumn` for each column `first..last`, `tab:hasLabel` a `tab:LabelCell` (text from the text layer, `tab:onPage`, and a `tab:hasBBox` that is the union of its words, as a leaf's is), and `tab:parentHeader` the **innermost** surviving spanner whose set ⊇ its own and which sits on a strictly higher line. Among equal sets the lowest such line is innermost.
- A leaf's parent is the innermost surviving spanner covering its column. A leaf with none gets **no** `parentHeader` and level 0.
- Level: a root is 0, and a child is its parent's level + 1.
- **No-spanner identity:** with `spanners == ()` the emitted triple set equals what `main` emits. Measure it against `main`'s `emit_boxhead` on the synthetic grid, then pin the triple set literally in the test.
- MEASURE `tab:parentHeader`'s and `tab:headerLevel`'s exact IRIs and directions in `vocab/ontology/tab.ttl` before you emit, and how `feed.py`'s scorer walk (`src/iladub/feed.py`, the function that takes the deepest node covering a column) reads them. Do not assume the direction.

- [ ] **Step 1: Write the failing tests** (synthetic, append to `tests/etkl/test_boxhead.py`)

```python
def _emitted(reading):
    from rdflib import Graph, URIRef
    lines, block, grid = _wide_lines(), (0, 1, 2), _wide_grid()
    d = dispose_boxhead(reading, lines, block, grid)
    g = Graph()
    from iladub.etkl.boxhead import emit_boxhead
    n = emit_boxhead(g, URIRef("urn:g"), lines, block, d, 0)
    return g, n, d


def _levels(g):
    from iladub.etkl.holon import TAB
    return {str(h).rsplit("-", 1)[1]: int(lv) for h, lv in g.subject_objects(TAB.headerLevel)}


def test_spanners_are_carried_as_a_leveled_tree():
    r = BoxheadReading(leaf_labels=_leaves(),
                       spanning_labels=((1, 3, ((0, 0),)), (1, 2, ((1, 0),)), (3, 3, ((1, 1),))))
    g, n, d = _emitted(r)
    assert n == 7
    assert _levels(g) == {"h0": 0, "s0": 0, "s1": 1, "s2": 1, "h1": 2, "h2": 2, "h3": 2}
    from iladub.etkl.boxhead import carried_lines
    assert carried_lines(_wide_lines(), (0, 1, 2), d) == (0, 1, 2)


def test_equal_sets_on_different_lines_nest_and_the_lower_one_is_innermost():
    """`Group` (L0) and `Left Right` (L1) both claim cols 1-3; both runs lie inside [100,400)."""
    r = BoxheadReading(leaf_labels=_leaves(),
                       spanning_labels=((1, 3, ((0, 0),)), (1, 3, ((1, 0), (1, 1)))))
    g, _, d = _emitted(r)
    assert d.spanner_refusal is None and d.spanners_dropped == ()
    assert _levels(g) == {"h0": 0, "s0": 0, "s1": 1, "h1": 2, "h2": 2, "h3": 2}


def test_a_reading_without_spanners_emits_exactly_the_triples_it_emits_today():
    r = BoxheadReading(leaf_labels=_leaves(), other_words=((0, 0), (1, 0), (1, 1)))
    g, n, _ = _emitted(r)
    assert n == 4 and set(_levels(g).values()) == {0}
    # PIN: the implementer replaces EXPECTED with the sorted N-Triples main's emit_boxhead produces
    # for this reading (measured on `main`, blank nodes normalised to _:b), and records the command.
    assert _normalised_nt(g) == EXPECTED_NO_SPANNER_NT
```

`_normalised_nt` sorts N-Triples lines with blank nodes rewritten to `_:b`, the rule `scripts/corpus_verdict_snapshot.py` uses. `EXPECTED_NO_SPANNER_NT` is captured **from `main`** (`git stash`, or a worktree at `25d561e`) before Step 3. That is the measured oracle. Writing it from reading the code is a rule-2 violation.

- [ ] **Step 2: Run, expect FAIL** (n == 4, no `s*` nodes).

- [ ] **Step 3: Write the Fed p0 corpus test** `tests/etkl/test_boxhead_fed_tree.py`, `pytestmark = pytest.mark.corpus`. Derive p0's grid (`datagrid.derive_data_grids(FED, 0)`), read its boxhead with `default_reader()` offline, emit into a graph, and assert:
  - 7 header nodes
  - levels L7 = 0, col 0 leaf = 0, col 6 leaf = 0, L8 = 1, col 1 leaf = 1, both L10 spanners = 2 (spec §3.2)
  - col 2 has no leaf and its deepest covering node walks to `Averages of daily figures › Change from week ended › Dec 25, 2024`, through the scorer's own walk in `feed.py`, not a re-implementation
  - the graph, unioned with the grid's emitted triples, conforms to `vocab/shapes/tab-shapes.ttl` (pySHACL, `rdfs`, `advanced=True`)

  If the walked path differs from the spec's text, **report it**. Do not edit the expected path to make it pass: that would be spec §7's "unverified", measured.

- [ ] **Step 4: Implement** `carried_lines` and `emit_boxhead` per the invariants.

- [ ] **Step 5: Run** `tests/etkl/test_boxhead.py` (expect all pass) and `-m corpus tests/etkl/test_boxhead_fed_tree.py` (expect all pass, serially, nothing else running).

- [ ] **Step 6: FALSIFICATION.** (i) Emit every spanner at level 0. The tree tests must FAIL, and the Fed test's shape conformance must FAIL with the overlap message from spec §2. (ii) Drop spanner words from `carried_lines`. `carried_lines == (0,1,2)` must FAIL. Restore and show green.

- [ ] **Step 7: Commit** `R334: carry surviving spanners as a leveled header tree`.

---

### Task 3: The caption worker (question, recording, disposal, carriage)

**Files:**
- Create: `baml_src/caption.baml`, `src/iladub/etkl/caption.py`, `readings/caption/README.txt`
- Test: `tests/etkl/test_caption.py`

**Interfaces:**
- Consumes: `boxhead.header_block`, `boxhead._ordered`, `DisposedBoxhead` (Task 1). The crop is the region `read_grid_boxhead` renders. **Extract** that region builder into a shared helper in `boxhead.py` (`boxhead_region(lines, grid, data_rows_shown=3)`). Do not duplicate it. `read_grid_boxhead` must keep its exact crop.
- Produces, in `caption.py`:
  - `CaptionReading(caption_lines: tuple[int, ...] = (), refuses: bool = False, note: str = "")`, frozen.
  - `CaptionReader` protocol `read_caption(crop_png: bytes, ncols: int, listing: str) -> CaptionReading | None`. Also `FakeCaptionReader(reading)`, `BamlCaptionReader`, `RecordedCaptionReader(live=None, directory=None)` (directory resolved at call time, the `headerlines.RecordedHeaderLinesReader` precedent), `default_reader()`, and `READINGS_DIR = <repo>/readings/caption`.
  - `candidate_lines(lines, block, disposed) -> tuple[int, ...]`: block positions (not page indices) of lines whose every word is in `disposed`'s `other_words`, top to bottom. `()` if `disposed.refused`. **This needs `other_words` on `DisposedBoxhead`.** Add `other_words: tuple[Address, ...] = ()` there in this task, populated only for a non-refused disposal (M3).
  - `listing_of(lines, block, candidates) -> str`: `C<i>: <words>` per candidate, with `i` the index into `candidates`. Word extents are rendered as in `boxhead.listing_of`.
  - `question_key(ncols, listing) -> str` = `sha256("caption\n" + str(ncols) + "\n" + listing)`. Spec §3.3 writes `"caption\n" + ncols + listing`, and the extra `"\n"` mirrors `boxhead.question_key`'s separator. **Note the choice in the README.**
  - `dispose_captions(reading, candidates, block, lines, disposed) -> tuple[int, ...]`: block positions of the disposed caption lines, or `()` for NO CLAIM.
  - `read_grid_captions(pdf_path, page_number, lines, grid, disposed, reader) -> tuple[int, ...]`: returns **page-line indices**. It asks nothing when `candidate_lines` is empty or `reader is None`. Every exception is `()`.
  - `emit_captions(g, grid_uri, lines, caption_page_lines, page) -> int`.

**Invariants (spec §3.3 + M2):**
- Disposal, all exact. `refuses` → `()`. Every index must be in `range(len(candidates))`. The set must be non-empty. The block positions must be **consecutive block positions** (contiguous in page order, not merely consecutive candidate indices). The last one must be the block position directly above the topmost block line holding a word of a surviving leaf **or** surviving spanner. Anything else → `()`.
- Emission: one `tab:RegionCaption` per line, URI `f"{grid_uri}-cap{k}"`, with `tab:captionText` (the line's words left to right, from the text layer), `tab:captionRow` (its block position, as `xsd:integer`), `tab:onPage` (`xsd:integer`) and `grid_uri tab:hasCaption cap`. **Never** `tab:SectionCaption`, and **never** `tab:hasBBox` (M2).
- The BAML prompt asks spec §3.3's question in a human reader's terms. It shows the crop and the candidate listing, says that refusing is correct, and says to answer with numbers only, quoting nothing. Client: `Claude` (the small one, the `header_lines.baml` precedent and its reasoning). Regenerate with `baml-cli generate`. `baml_client/` is untracked.

- [ ] **Step 1: Write the failing tests** `tests/etkl/test_caption.py`

```python
from types import SimpleNamespace

from iladub.etkl.boxhead import BoxheadReading, dispose_boxhead
from iladub.etkl import boxhead
from iladub.etkl.caption import (CaptionReading, FakeCaptionReader, candidate_lines,
                                 dispose_captions, question_key, read_grid_captions)


def _w(text, x0, x1):
    return SimpleNamespace(text=text, x0=x0, x1=x1, top=0.0, bottom=1.0)


def _ln(*ws, top):
    return SimpleNamespace(words=list(ws), top=top, bottom=top + 1)


COLS = tuple(SimpleNamespace(x0=float(a), x1=float(a + 100)) for a in (0, 100, 200))
GRID = SimpleNamespace(rows=(5, 6), columns=COLS,
                       refusals={j: "HeterogeneousColumn/every-measure" for j in range(5)})
LINES = [_ln(_w("Masthead", 0, 290), top=0),                      # block 0: candidate
         _ln(_w("Title", 100, 200), top=2),                       # block 1: candidate
         _ln(_w("Millions", 120, 180), top=4),                    # block 2: candidate
         _ln(_w("Group", 120, 280), top=6),                       # block 3: spanner cols 1-2
         _ln(_w("Id", 10, 40), _w("a", 140, 160), _w("b", 240, 260), top=8),   # block 4: leaves
         _ln(_w("x", 10, 20), _w("1", 140, 150), _w("2", 240, 250), top=10),
         _ln(_w("y", 10, 20), _w("3", 140, 150), _w("4", 240, 250), top=12)]
BLOCK = (0, 1, 2, 3, 4)
READING = BoxheadReading(leaf_labels=((0, ((4, 0),)), (1, ((4, 1),)), (2, ((4, 2),))),
                         spanning_labels=((1, 2, ((3, 0),)),),
                         other_words=((0, 0), (1, 0), (2, 0)))


def _disposed():
    return dispose_boxhead(READING, LINES, BLOCK, GRID)


def test_candidates_are_the_lines_filed_entirely_as_other_words():
    assert candidate_lines(LINES, BLOCK, _disposed()) == (0, 1, 2)


def test_contiguous_captions_ending_above_the_topmost_label_are_disposed():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(1, 2)), c, BLOCK, LINES, _disposed()) == (1, 2)
    assert dispose_captions(CaptionReading(caption_lines=(0, 1, 2)), c, BLOCK, LINES, _disposed()) == (0, 1, 2)


def test_caption_out_of_range_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(2, 3)), c, BLOCK, LINES, _disposed()) == ()


def test_caption_not_contiguous_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(0, 2)), c, BLOCK, LINES, _disposed()) == ()


def test_caption_not_adjacent_to_the_topmost_label_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(caption_lines=(0, 1)), c, BLOCK, LINES, _disposed()) == ()


def test_empty_or_refusing_answer_is_no_claim():
    c = candidate_lines(LINES, BLOCK, _disposed())
    assert dispose_captions(CaptionReading(), c, BLOCK, LINES, _disposed()) == ()
    assert dispose_captions(CaptionReading(caption_lines=(2,), refuses=True), c, BLOCK, LINES,
                            _disposed()) == ()


def test_no_candidate_lines_asks_nothing():
    asked = []

    class Spy:
        def read_caption(self, crop_png, ncols, listing):
            asked.append(listing)
            return CaptionReading(caption_lines=(0,))

    no_other = BoxheadReading(leaf_labels=READING.leaf_labels,
                              spanning_labels=((1, 2, ((0, 0), (1, 0), (2, 0), (3, 0))),))
    d = dispose_boxhead(no_other, LINES, BLOCK, GRID)
    assert read_grid_captions("unused.pdf", 0, LINES, GRID, d, Spy()) == () and asked == []


def test_the_caption_key_differs_from_the_boxhead_key_for_the_same_listing():
    assert question_key(3, "L0: x") != boxhead.question_key(3, "L0: x")


def test_captions_are_region_captions_only_with_text_row_and_page():
    from rdflib import Graph, URIRef
    from iladub.etkl.caption import emit_captions
    from iladub.etkl.holon import TAB
    from rdflib.namespace import RDF
    g = Graph()
    assert emit_captions(g, URIRef("urn:g"), LINES, (1, 2), 0) == 2
    caps = set(g.subjects(RDF.type, TAB.RegionCaption))
    assert len(caps) == 2 and not set(g.subjects(RDF.type, TAB.SectionCaption))
    assert not any(True for c in caps for _ in g.objects(c, TAB.hasBBox))
    assert sorted(str(t) for t in g.objects(None, TAB.captionText)) == ["Millions", "Title"]
```

Plus one shapes test: the caption graph from the last test, unioned with a minimal grid that carries one `tab:hasHeaderNode`, validates against `tab-shapes.ttl` + `tab-physical-shapes.ttl` (`rdfs`, `advanced`) with `conforms=True`. **Add a control** that also attaches a `tab:hasBBox` to one caption and must **fail** with the `WrappedCellShape` message. That control is M2, kept as a regression.

- [ ] **Step 2: Run, expect FAIL** (`ModuleNotFoundError: iladub.etkl.caption`).

- [ ] **Step 3: Implement** `caption.py`, `caption.baml`, the shared region helper, `DisposedBoxhead.other_words`, and the README (the boxhead README's format, with its table empty until Task 5). Give the module docstring the § 8 classification table rows for this worker (spec §4).

- [ ] **Step 4: Run** `tests/etkl/test_caption.py` and `tests/etkl/test_boxhead.py`. Expect all to pass.

- [ ] **Step 5: FALSIFICATION.** (i) Remove the adjacency check. `…not_adjacent…` must FAIL. (ii) Check contiguity on candidate indices instead of block positions. Construct the failing case with a non-candidate line between two candidates, and show it FAIL. (iii) Make the emitter also add `tab:SectionCaption`. The emission test must FAIL. Restore and show green.

- [ ] **Step 6: Commit** `R336: a caption worker for a grid's own title and unit lines`.

---

### Task 4: Wire the adoption site

**Files:**
- Modify: `src/iladub/etkl/compile.py`, the adoption block (the `from .boxhead import (carried_lines, default_reader, emit_boxhead, header_block, read_grid_boxhead)` site, and the `emit_boxhead(_new, …)` call in the rebuild loop)
- Test: `tests/etkl/test_caption_adoption.py` (new)

**Interfaces:**
- Consumes: Tasks 1–3.
- Order (spec §3.4): `read_grid_boxhead` (now disposing spanners) → `read_grid_captions` → a grid's read lines are `tuple(grid.rows) + carried_lines(...) + caption page lines`. The `_read` tuple gains the caption page lines, and the rebuild loop calls `emit_captions` beside `emit_boxhead`. `build_ledger` and the R290 union are untouched.
- MEASURE: `_read` is unpacked by position in the rebuild loop. Find every unpacking site before you widen the tuple.

- [ ] **Step 1: Failing test.** On a synthetic page this is costly, so use `monkeypatch`: replace `caption.default_reader` with a `FakeCaptionReader`, replace the boxhead reader with a `FakeBoxheadReader` holding the Task 3 reading, and run the adoption path on the smallest committed non-corpus fixture that derives a grid. MEASURE which fixture: `grep -rln "datagrid_adopt=True" tests/` and pick one that does not need `corpus/`. If none exists, make this test `@pytest.mark.corpus` on Fed p0 with a fake caption reader answering `(1, 2)` over its candidates. Assert that the adopted graph has `tab:RegionCaption` nodes under the grid with the expected texts, and that the ledger books those lines.
- [ ] **Step 2: Run, expect FAIL.**
- [ ] **Step 3: Implement.** With no caption recording and no live reader, `read_grid_captions` returns `()` and the site is the identity for captions.
- [ ] **Step 4: Run** the new test, then the non-corpus suite (`PYTHONPATH=src .venv/bin/python -m pytest -q -m "not corpus"`). Read `N passed`, not the exit code.
- [ ] **Step 5: FALSIFICATION.** Drop the caption lines from the read lines. The ledger assertion must FAIL. Restore and show green.
- [ ] **Step 6: Commit** `R334+R336: carry spanners and captions at the adoption site`.

---

### Task 5: Count the grids with candidate lines, then record one live caption ask each

**This task spends money and is run by the controller with the maintainer's key, not by a subagent.** The approved budget is spec §8 ruling 1.

**Files:**
- Create: `readings/caption/*.json` (recordings), and a README table row
- Scratchpad only (not committed): the count and recorder scripts

- [ ] **Step 1: Count first, offline.** Write a scratchpad script that wraps `caption.read_grid_captions` with a logger and compiles every document in `corpus/` and `held-out/` (one file per process, serially, nothing else running). It logs `(doc, page, grid, len(candidates))` for every grid where `candidates` is non-empty. The count of rows is the number of live asks. **Report it to the maintainer before Step 2.** If it is far from the order of the 23 boxhead recordings, stop and ask.
- [ ] **Step 2: Record** with only the caption reader live (M4). In the scratchpad recorder, patch `caption.default_reader` to return `RecordedCaptionReader(live=BamlCaptionReader())`, set `ILADUB_RECORD_READINGS=1`, and leave `BAML_LIVE` unset so every other worker stays offline. Run the same serial sweep. Exactly one ask per question. If a question's answer is disposed to NO CLAIM, it is still recorded: the recording is the proposal (boxhead README).
- [ ] **Step 3: Verify offline.** Rerun Step 1's sweep with no live reader. Expect 0 misses (every candidate-bearing grid hits a recording), and `git status readings/boxhead` clean.
- [ ] **Step 4: README.** Add one row per document: the date, what was disposed versus NO CLAIM, and whether Fed's answer is {L6}, {L5, L6} or wider (spec §7, last bullet: state which).
- [ ] **Step 5: Commit** `R336: record one caption reading per candidate-bearing grid`.

---

### Task 6: Fed p0 end to end, the floor, the baseline, the register

**Files:**
- Create: `tests/etkl/test_r334_r336_fed_p0.py` (`@pytest.mark.corpus`)
- Modify: `tests/ground-truth/fed-h41-2025-01-02/floor.json`, `tests/corpus-baseline/**` (regenerated), `readings/boxhead/README.txt` (one row: spanners now carried, no file changed), `docs/superpowers/residues.md`, `docs/superpowers/residues-open.md`

- [ ] **Step 1: Test (spec §5 item 6).** `compile_document(FED)` offline. Assert that p0 is in `adopted`, and that p0's ledger escalates **the exact number measured** (the probe predicted 27). Pin the measured value and state it in the report next to the prediction. Assert `truth_block(...)["table-1"]["CORRECT"] > 0`, via `scripts/corpus_verdict_snapshot.truth_block`. Also assert that the graph contains the col-2 path from Task 2.
- [ ] **Step 2: Run it, serially.** If p0 does not adopt, **stop**: spec §7's "whether carriage reproduces 27" has been refuted, so report it rather than tune anything.
- [ ] **Step 3: FALSIFICATION.** Disable the caption carriage in `compile.py`. p0 must not adopt (the probe's 38 > 31). Restore.
- [ ] **Step 4: Floor.** Set `table-1.CORRECT` in `floor.json` to the measured CORRECT. Run `tests/test_ground_truth_floor.py -m corpus`.
- [ ] **Step 5: Baseline.** After `git add` of every new input file (`src/iladub/etkl/caption.py`, `readings/caption/*`), run `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate`, once, about 24 minutes, unattended. Read `git diff --stat -- tests/corpus-baseline/`. Every moved document must be one of the 11 with spanners (spec §2) or a caption-bearing grid from Task 5, and anything else is a finding to report. Then run `corpus_baseline.py verify`.
- [ ] **Step 6: Register.** Strike ~~R334~~ and ~~R336~~ with the closure evidence (the PR, Fed p0's ledger, CORRECT). Open new rows, each with the `(c/t closed)` tally snapshot:
  - units stay text (scale, currency and QUDT are not read)
  - `UnambiguousAccessShape` does not target `tab:GridColumn` (spec §2)
  - a too-wide spanner group passes (b), and only the scorer sees it
  - a caption over-claim of masthead lines, if Task 5 measured one

  Append to R218's row that grid captions now carry page and row but no box, and why (M2).
- [ ] **Step 7: Full gate.** `PYTHONPATH=src .venv/bin/python -m pytest -q` (non-corpus), then `corpus_baseline.py check`.
- [ ] **Step 8: Commit** `R334+R336: Fed p0 adopts; floor, baseline and register`.

## Self-review (done at authoring)

- Spec coverage: §3.1 → T1, §3.2 → T2, §3.3 → T3 + T5, §3.4 → T4, §5 items 1–2 → T1, items 3–4 → T2, item 5 → T3, item 6 → T6, §5a respected (Global Constraints), §7 bullet 1 → M1, bullet 2 → T6 step 2, bullet 3 → T2 step 3 (report), bullet 4 → register row, bullet 5 → T5 step 4, §8 ruling 1 → T5, ruling 2 → T1.
- Deviation from spec: M2, the caption box. Flagged for the maintainer above.
- `DisposedBoxhead` gains `spanners_dropped`, `spanner_refusal` (T1) and `other_words` (T3). Names are consistent across T1–T4.
