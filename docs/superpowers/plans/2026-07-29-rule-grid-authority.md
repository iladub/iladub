# Rules as leaf-grid authority Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the author's own vertical rules the authority for the leaf-column grid when the words confirm them, recovering GrainCorp's `Month`/`Port` split from structure the author drew rather than from inferred whitespace.

**Architecture:** Two confined changes. `grid._rule_boundaries` collapses boundaries bounding an interval no word occupies (threshold-free, kills double-drawn hairline rules). `cells.recover_leaf_grid` carries `band.rules`/`band.hrules` into the sub-bands it builds — currently dropped, which silently disables the shipped border-aware path — and returns a rule-derived grid immediately instead of putting it to a vote. The modal vote is untouched and remains the path for ruleless tables.

**Tech Stack:** Python 3 (`src/iladub/etkl/`), numpy, pytest.

**Spec:** `docs/superpowers/specs/2026-07-29-rule-grid-authority-design.md` (read §2 — the measurements, including one that corrects an earlier reading of this residue).

**Run tests with:** `. .venv/bin/activate && python3 -m pytest -q` from the repo root, `/Volumes/WD Green/dev/git/iladub`. The full suite takes ~155s and exceeds the default 120s tool timeout — set the Bash tool's `timeout` parameter to `400000` ms for it, and never background it.

**Baseline:** 592 passed, 5 skipped (`main` at `60eda2c`). Branch `iladub-rule-grid-authority` is already checked out.

## Global Constraints

Copied from the spec's §5 gate. **Every task's requirements implicitly include this section.**

- **No tuned constant, no tolerance, no new numeric literal.** The empty-interval collapse is a **presence** test ("does any word occupy this interval"), NOT a distance threshold. Do **not** write `abs(a - b) < eps`, and do **not** repurpose `COORD_EPS` (0.01) as a dedup width — the duplicates are 0.12–1.0 pt apart, so using it that way would be exactly the tuned constant the gate forbids.
- **Recover the author's structure; do not re-derive it.** Rules outrank inferred gutters when the words confirm them.
- **Honest failure preserved.** If the words do not tile the rules, `_rule_boundaries` still returns `None` and the whitespace path runs. Never force the rules.
- **The ruleless path must be byte-identical.** A band with `rules == ()` must produce exactly today's grid. The modal vote is NOT being fixed in this loop (it carries a known defect — spec §2 Finding 3 / residue R3); leave it alone.
- **Never weaken an existing test.** The full suite stays green.
- **No third-party PDF committed.** GrainCorp stays local.
- **No overfitting:** fixtures synthetic and domain-neutral, authored from the shape of the problem.

---

## File Structure

| File | Responsibility |
| --- | --- |
| `src/iladub/etkl/grid.py` | **Modify** — `_rule_boundaries` gains the empty-interval collapse. No other function changes. |
| `src/iladub/etkl/cells.py` | **Modify** — `recover_leaf_grid` carries rules into sub-bands and short-circuits on rule boundaries. |
| `tests/etkl/test_rule_grid_authority.py` | **Create** — collapse, authority, straddle-self-heal, and ruleless-unchanged tests. |
| `docs/superpowers/residues.md` | **Create** — the residue register (Task 3). |

Task order: 1 → 2 → 3. Task 2 consumes Task 1's collapse.

---

## Probed fixture values

Every value below was **probed against the current code while planning** — assert them, do not re-derive them.

**The discriminating fixture** (this is what makes the tests non-vacuous): three columns separated by **2 pt** gaps. A gutter needs ≥3 blank 1-pt bins, so 2 pt is too narrow — the whitespace path merges everything into **1 column**, while the rules give **3**. Rules at `10.0, 10.3, 50.0, 90.0, 130.0` (the `10.0`/`10.3` pair is a double-drawn rule); words at `[12,49]`, `[51,89]`, `[91,128]` on each row.

| probe | current result |
| --- | --- |
| `_rule_boundaries(band)` | `[10.0, 10.3, 50.0, 90.0, 130.0]` — hairline pair present |
| `infer_leaf_grid` on the same band **without** rules | `ncols=1`, boundaries `[12, 128]` |
| `recover_leaf_grid(band)` **with** rules | `ncols=1` ← **the defect** |
| same, but first line is `CAPTION` at `[40,60]` straddling the `50.0` rule | `ncols=1`; `_rule_boundaries` on the full band → `None`; on the body-only suffix → accepted |

**After the fix, both must give `ncols=3` with boundaries `(10.0, 50.0, 90.0, 130.0)`.**

---

### Task 1: `_rule_boundaries` collapses unoccupied intervals

**Files:**
- Modify: `src/iladub/etkl/grid.py` (the `_rule_boundaries` function only)
- Test: `tests/etkl/test_rule_grid_authority.py` (create)

**Interfaces:**
- Consumes: `iladub.etkl.geometry.Word`, `Line`, `Rule`; `iladub.etkl.bands.Band`.
- Produces: `_rule_boundaries(band) -> list[float] | None`, unchanged signature. It now returns only boundaries bounding at least one occupied interval, and `None` when fewer than two survive.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_rule_grid_authority.py`:

```python
"""Loop D — the author's vertical rules as leaf-grid authority.

Two shipped defects made GrainCorp's grid 14 columns where the source has 15:
recover_leaf_grid rebuilt every sub-band WITHOUT band.rules (so the border-aware
path never ran), and double-drawn rules would otherwise yield hairline columns.
See docs/superpowers/specs/2026-07-29-rule-grid-authority-design.md.

The fixture is deliberately TIGHT — 2pt gaps, below the 3-bin gutter minimum — so the
whitespace path merges all three columns into one. That is what makes these tests
discriminating: rule-derived 3 vs gutter-derived 1.
"""
from iladub.etkl.bands import Band
from iladub.etkl.cells import recover_leaf_grid
from iladub.etkl.geometry import Line, Rule, Word
from iladub.etkl.grid import _rule_boundaries, infer_leaf_grid

# 10.0 and 10.3 are the SAME physical rule drawn twice — the artefact that would
# otherwise produce a 0.3pt hairline column.
RULES = (Rule(10.0, 0, 70), Rule(10.3, 0, 70), Rule(50.0, 0, 70),
         Rule(90.0, 0, 70), Rule(130.0, 0, 70))
EXPECTED = (10.0, 50.0, 90.0, 130.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def _body_rows():
    """Four data rows whose 2pt inter-column gaps are too narrow to be gutters."""
    return [_line([_w("a%d" % i, 12, 49, t), _w("b%d" % i, 51, 89, t),
                   _w("c%d" % i, 91, 128, t)], t)
            for i, t in enumerate((12.0, 24.0, 36.0, 48.0))]


def tight_ruled_band():
    rows = _body_rows()
    return Band(tuple(rows), 12.0, 58.0, RULES)


def straddling_caption_band():
    """Same table, but line 0 is a caption straddling the 50.0 rule — the GrainCorp
    shape ('Friday, 24 J' was the single word of 472 that vetoed the whole band)."""
    rows = [_line([_w("CAPTION", 40, 60, 0.0)], 0.0)] + _body_rows()
    return Band(tuple(rows), 0.0, 58.0, RULES)


def test_unoccupied_interval_is_not_a_column():
    # The 10.0-10.3 interval holds no word, so it is not a column. Threshold-free:
    # a presence test, never a distance comparison.
    assert _rule_boundaries(tight_ruled_band()) == list(EXPECTED)


def test_occupied_intervals_all_survive():
    # Guard against over-collapsing: every interval that DOES hold ink is kept.
    kept = _rule_boundaries(tight_ruled_band())
    assert len(kept) - 1 == 3


def test_rules_still_refused_when_a_word_straddles():
    # Honest failure preserved: the full band still falls through to whitespace.
    assert _rule_boundaries(straddling_caption_band()) is None


def test_no_rules_means_no_rule_boundaries():
    assert _rule_boundaries(Band(tuple(_body_rows()), 12.0, 58.0)) is None
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_grid_authority.py -q`
Expected: `test_unoccupied_interval_is_not_a_column` and `test_occupied_intervals_all_survive` **FAIL** — the current function returns `[10.0, 10.3, 50.0, 90.0, 130.0]` (5 boundaries, 4 columns). The other two pass already; they are guards.

- [ ] **Step 3: Extend `_rule_boundaries` in `src/iladub/etkl/grid.py`**

Replace the function's final `return xs` with the collapse, and extend the docstring. The full function becomes:

```python
def _rule_boundaries(band: Band) -> list[float] | None:
    """Candidate leaf boundaries from the band's vertical rules — returned ONLY if every band
    word strictly tiles them (each word within some [x_i, x_i+1]); else None (whitespace fallback).
    Threshold-free: the words confirm the rules are column separators.

    Boundaries bounding an interval NO word occupies are dropped. A rule drawn twice (a table
    border rendered as two segments a fraction of a point apart) would otherwise contribute a
    hairline column that no label can ever cover, which fails CoverageShape downstream. Measured
    on a real report: exactly the 4 double-drawn hairlines were empty while every real column held
    4-53 words.

    This is a PRESENCE test ("does any ink occupy this interval"), NOT a dedup tolerance. Do not
    "simplify" it to abs(a - b) < eps: the duplicates there were 0.12-1.0pt apart, so any distance
    threshold would be a tuned constant, which the CLAUDE.md §8 gate forbids. COORD_EPS (0.01) is a
    float-comparison epsilon and must not be repurposed as a width either.
    """
    if not band.rules:
        return None
    xs = sorted({round(r.x, 2) for r in band.rules})
    if len(xs) < 2:
        return None
    words = [w for ln in band.lines for w in ln.words]
    if not words:
        return None
    for w in words:
        if not any(xs[c] - COORD_EPS <= w.x0 and w.x1 <= xs[c + 1] + COORD_EPS
                   for c in range(len(xs) - 1)):
            return None            # a word straddles / lies outside the rules -> reject
    kept = [xs[0]]
    for c in range(len(xs) - 1):
        if any(w.x0 < xs[c + 1] and w.x1 > xs[c] for w in words):
            kept.append(xs[c + 1])
    return kept if len(kept) >= 2 else None
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_grid_authority.py -q`
Expected: **4 passed.**

- [ ] **Step 5: Confirm the ruled fixtures are unaffected**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_border_grid.py tests/etkl/test_grid.py tests/etkl/test_cells.py tests/etkl/test_hrule_split.py -q`
Expected: all pass. These exercise the rule path directly; a failure means the collapse dropped a real column — re-read Step 3, do not adjust a test.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/grid.py tests/etkl/test_rule_grid_authority.py
git commit -m "fix(etkl): an interval no word occupies is not a column (loop D)"
```

---

### Task 2: `recover_leaf_grid` treats rules as authority

**Files:**
- Modify: `src/iladub/etkl/cells.py` (the `recover_leaf_grid` function only)
- Test: `tests/etkl/test_rule_grid_authority.py` (extend)

**Interfaces:**
- Consumes: Task 1's `_rule_boundaries`; the fixtures `tight_ruled_band()` and `straddling_caption_band()` defined in Task 1's test file.
- Produces: `recover_leaf_grid(band) -> LeafGrid`, unchanged signature. When any row-suffix yields rule boundaries, the returned grid is rule-derived with `confidence == 1.0`; otherwise the modal-vote grid, unchanged.

- [ ] **Step 1: Write the failing test**

Append to `tests/etkl/test_rule_grid_authority.py`:

```python
def test_rules_outrank_inferred_gutters():
    # THE LOOP'S POINT. The 2pt gaps are below the gutter minimum, so whitespace
    # inference merges all three columns into ONE. The author drew rules; they win.
    band = tight_ruled_band()
    gutter_only = infer_leaf_grid(Band(band.lines, band.top, band.bottom))
    assert gutter_only.ncols == 1, "fixture must be tight enough to defeat the gutter path"

    grid = recover_leaf_grid(band)
    assert grid.ncols == 3
    assert grid.boundaries == EXPECTED
    assert grid.confidence == 1.0


def test_straddling_caption_self_heals_via_the_suffix():
    # _rule_boundaries refuses the FULL band (the caption straddles a rule), but
    # recover_leaf_grid already walks row-suffixes to skip unstable top rows, so a
    # later suffix accepts. This is the GrainCorp shape: one word of 472 vetoed
    # the rules for the whole band.
    grid = recover_leaf_grid(straddling_caption_band())
    assert grid.ncols == 3
    assert grid.boundaries == EXPECTED


def test_ruleless_band_is_unchanged():
    # The modal-vote path is NOT being changed in this loop. A band with no rules
    # must return exactly what it returns today.
    band = Band(tuple(_body_rows()), 12.0, 58.0)
    assert recover_leaf_grid(band).ncols == 1
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_grid_authority.py -q`
Expected: `test_rules_outrank_inferred_gutters` and `test_straddling_caption_self_heals_via_the_suffix` **FAIL** with `assert 1 == 3` — `recover_leaf_grid` currently discards the rules. `test_ruleless_band_is_unchanged` passes already; it is the regression guard.

- [ ] **Step 3: Replace `recover_leaf_grid` in `src/iladub/etkl/cells.py`**

```python
def recover_leaf_grid(band: Band) -> LeafGrid:
    """Leaf grid = the author's vertical rules when the words confirm them, else the
    most-stable column count across row-suffixes.

    RULES ARE AUTHORITY. If any row-suffix's words strictly tile the band's rules, that
    rule-derived grid is returned immediately — the author drew those separators, so there is
    nothing to vote on (CLAUDE.md §0: recover the author's structure, do not re-derive it).
    Walking suffixes matters: a single leaked caption word straddling a rule vetoes the rules
    for the WHOLE band, but a suffix that skips it accepts them (measured on a real report:
    one word of 472).

    WHITESPACE FALLBACK (unchanged): spanning or verbose header rows cause instability at the
    top of the suffix range — either collapsing the column count (few wide clusters) or
    inflating it (many short tokens whose inter-word gaps look like gutters). The stable leaf
    count is the MODE (most frequent column count) across all qualifying suffixes of >=2 rows.
    Among suffixes achieving the modal count, the longest (most rows = strongest gutter
    evidence) is returned. Falls back to infer_leaf_grid(band) if nothing qualifies (e.g. a
    single-line band).

    KNOWN DEFECT in that mode, deliberately NOT fixed here (residue R3): the suffixes are
    NESTED SUBSETS of one another, not independent witnesses, so the vote systematically
    over-weights the degraded tail. Measured on a real report: the correct grid was found by
    the longest suffix, then outvoted 35-to-16 by shorter ones. Ruled documents now route
    around this; ruleless ones still hit it.
    """
    lines = list(band.lines)
    results: list[tuple[int, int, LeafGrid]] = []  # (ncols, n_rows, grid)
    for start in range(max(1, len(lines) - 1)):
        sub = lines[start:]
        if len(sub) < 2:
            break
        sub_band = Band(tuple(sub), min(l.top for l in sub), max(l.bottom for l in sub),
                        band.rules, band.hrules)
        try:
            g = infer_leaf_grid(sub_band)
        except ValueError:
            continue
        if _rule_boundaries(sub_band) is not None:
            return g               # author's rules confirmed by the words -> authority, no vote
        results.append((g.ncols, len(sub), g))
    if not results:
        return infer_leaf_grid(band)
    # Modal column count — the count that most suffixes agree on.
    # Tie-break toward the higher count (finer grid = more columns revealed).
    freq: dict[int, int] = {}
    for ncols, _, _ in results:
        freq[ncols] = freq.get(ncols, 0) + 1
    modal_count = max(freq, key=lambda k: (freq[k], k))
    # Among all suffixes achieving the modal count, take the longest (strongest evidence).
    best = max((r for r in results if r[0] == modal_count), key=lambda r: r[1])
    return best[2]
```

Change `cells.py:14` from

```python
from .grid import LeafGrid, infer_leaf_grid
```

to

```python
from .grid import LeafGrid, _rule_boundaries, infer_leaf_grid
```

(verified during planning: that is the existing import line, and `grid.py` does not import `cells`, so there is no cycle).

**Why re-check `_rule_boundaries` after calling `infer_leaf_grid`:** `infer_leaf_grid` calls it internally but does not report whether it fired. Re-calling is a pure function over the same band, so it cannot disagree; this keeps `infer_leaf_grid`'s signature untouched.

- [ ] **Step 4: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rule_grid_authority.py -q`
Expected: **7 passed.**

- [ ] **Step 5: Verify the measured blast radius**

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
import os, tempfile
from dataclasses import replace as _replace
from iladub.etkl.geometry import extract_words, extract_rules, extract_hrules, extract_chars, rule_aware_lines, text_lines
from iladub.etkl.bands import detect_bands, Band
from iladub.etkl.segment import segment
from iladub.etkl.cells import recover_leaf_grid
from tests.etkl import fixtures as F
d = tempfile.mkdtemp()
for nm, want in [('ruled_tight_table_pdf',5), ('ruled_merged_table_pdf',5),
                 ('borderless_tight_table_pdf',5), ('borderless_merged_table_pdf',5),
                 ('simple_table_pdf',3), ('pivoted_table_pdf',7), ('crosstab_table_pdf',7)]:
    p = os.path.join(d, nm + '.pdf'); getattr(F, nm)(p)
    w=extract_words(p,0); pr=extract_rules(p,0); ph=extract_hrules(p,0); pc=extract_chars(p,0)
    for band in detect_bands(text_lines(w)):
        for sub in segment(band):
            sr=tuple(r for r in pr if r.top<=sub.bottom and r.bottom>=sub.top)
            sh=tuple(h for h in ph if sub.top<=h.y<=sub.bottom)
            if not sr: bb=_replace(sub,hrules=sh) if sh else sub
            else:
                xs=sorted({round(r.x,2) for r in sr})
                bc=[c for c in pc if c.top>=sub.top-0.5 and c.bottom<=sub.bottom+0.5]
                rl=rule_aware_lines(bc,xs) if len(xs)>=2 else []
                bb=Band(tuple(rl),sub.top,sub.bottom,sr,sh) if rl else _replace(sub,rules=sr,hrules=sh)
            if len(bb.lines) < 2: continue
            try: g = recover_leaf_grid(bb)
            except ValueError: continue
            print('%-30s rules=%d ncols=%d %s' % (nm, len(bb.rules), g.ncols, 'OK' if g.ncols==want else 'CHANGED (was %d)'%want))
            break
        else: continue
        break
"
```
Expected: every line ends `OK` — the counts measured during planning. A `CHANGED` line means the fix altered a shipped fixture's grid; investigate before proceeding.

- [ ] **Step 6: Full suite**

Run (timeout 400000): `. .venv/bin/activate && python3 -m pytest -q`
Expected: **599 passed, 5 skipped** (592 baseline + 7 new). Report the real numbers.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/cells.py tests/etkl/test_rule_grid_authority.py
git commit -m "fix(etkl): recover_leaf_grid carries the band's rules and treats them as authority (loop D)"
```

---

### Task 3: The residue register + GrainCorp confirmation

**Files:**
- Create: `docs/superpowers/residues.md`
- No source changes.

**Interfaces:** none — documentation and verification only.

- [ ] **Step 1: Create `docs/superpowers/residues.md`**

Copy the table from the spec's §6 verbatim into this file, with this header above it:

```markdown
# Residue register

Deferred items from the ET(K)L loops, in one tracked place. Each row records what the residue is,
where it was **measured** (never assumed), why it was deferred, and what would close it.

**This register is canonical.** Loops append rows here; a loop that closes a residue deletes its
row in the same change. Specs may describe a residue in prose, but the list of open residues lives
here.

| # | Residue | Measured | Why deferred | What would close it |
| --- | --- | --- | --- | --- |
```

Then the twelve rows R1–R12 exactly as written in `docs/superpowers/specs/2026-07-29-rule-grid-authority-design.md` §6. Do not paraphrase them — they carry measured values.

- [ ] **Step 2: GrainCorp confirmation (LOCAL, uncommitted)**

Verify the PDF exists at
`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf`.
If it does not, report that and skip this step — it is a confirmation, not a gate. **Never copy or commit the PDF.**

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from rdflib import Namespace
from iladub.etkl.compile import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
TAB = Namespace('https://w3id.org/iladub/tab#')
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
prop = RowRoleProposal(('furniture','continuation','continuation'), 0.85, 'date caption + two wrapped rows')
r = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
for reg in r.regions:
    if reg.verdict == 'asserted': print(reg.kind, reg.verdict, 'cells=', reg.cells)
print('score=', round(r.score, 4))
labels = [str(o) for s,_p,o in r.graph.triples((None, TAB.cellText, None)) if 'hl' in str(s)]
print('n header labels =', len(labels))
for l in sorted(labels): print('   ', l)
"
```

Expected, and **report what you actually observe**:
- `score= 0.947` and `cells= 447` — **unchanged**. This loop must NOT move the score; splitting a column changes no token counts. A changed score means something unintended happened — investigate and report rather than celebrating it.
- `n header labels = 15` (was 14).
- `Month` and `Port` appear as **separate** labels (was the single label `Month Port`).
- `Date Loading CompletedCommodityTotal` is still present — residue R1, expected.

- [ ] **Step 3: Update the spec's status line**

In `docs/superpowers/specs/2026-07-29-rule-grid-authority-design.md`, append to the `**Status:**` line what you measured in Step 2, using today's date. Use **your** numbers, not the planned ones, and state any difference explicitly.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/specs/2026-07-29-rule-grid-authority-design.md
git commit -m "docs: residue register + loop D measured outcome"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
| --- | --- |
| §1 in-scope: `_rule_boundaries` empty-interval collapse | Task 1 |
| §1 in-scope: `recover_leaf_grid` carries rules + short-circuits | Task 2 |
| §1 in-scope: residue register | Task 3 Step 1 |
| §1 success 1 (14→15, `Month`/`Port` separate) | Task 3 Step 2 |
| §1 success 2 (15 not 19; hairlines collapsed) | Task 1 `test_unoccupied_interval_is_not_a_column` |
| §1 success 3 (**score does not move**) | Task 3 Step 2, stated as a failure condition |
| §1 success 4 (no regression) | Task 1 Step 5, Task 2 Steps 5–6 |
| §1 success 5 (gate: no tuned constant) | Global Constraints + the Step 3 docstring |
| §1 success 6 (register exists, all items present) | Task 3 Step 1 |
| §2 Findings 1–6 | Encoded as the probed fixture values and Task 2's docstring |
| §3.1 `_rule_boundaries` | Task 1 Step 3 |
| §3.2 `recover_leaf_grid` | Task 2 Step 3 |
| §3.3 register | Task 3 Step 1 |
| §4 all six test bullets | Task 1 Step 1 (4 tests) + Task 2 Step 1 (3 tests) + Task 3 Step 2 |
| §5 gate | Global Constraints |
| §6 register contents | Task 3 Step 1 |
| §7 open questions | No task — correctly deferred |

**Gap found and closed during review:** §4's "ruleless path untouched" bullet needed an explicit assertion rather than relying on the suite; it is now `test_ruleless_band_is_unchanged`, and it is a genuine guard because the same fixture yields 1 column through the whitespace path and 3 through the rules.

**Placeholder scan:** none. Every step carries complete, copy-ready code and exact expected output. Task 3 Step 1 references the spec's §6 table rather than duplicating twelve rows a second time — that is a deliberate single-source-of-truth choice, not a placeholder, and the rows are fully written in the spec.

**Type consistency:**
- `_rule_boundaries(band) -> list[float] | None` — signature unchanged; Task 2 calls it as a predicate (`is not None`). Consistent.
- `recover_leaf_grid(band) -> LeafGrid` — signature unchanged; `LeafGrid(boundaries: tuple[float, ...], ncols: int, pitch: float, confidence: float)` per `grid.py:17`. Task 2's test asserts `grid.boundaries == EXPECTED` where `EXPECTED` is a **tuple**, matching `LeafGrid.boundaries`; Task 1's test asserts `_rule_boundaries(...) == list(EXPECTED)` because that function returns a **list**. The two are deliberately different types and the tests reflect that.
- `Rule(x, top, bottom)` per `geometry.py:68`; `Band(lines, top, bottom, rules=(), hrules=())` per `bands.py:16`. Both used with matching arity in the fixtures.
- `Word(text, x0, x1, top, bottom)` — the `_w` helper matches the shipped helpers in `tests/etkl/test_rowrole_reading.py`.
