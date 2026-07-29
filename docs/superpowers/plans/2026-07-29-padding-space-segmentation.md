# Padding-space word segmentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop emitting values the source does not contain — a contiguous `20,000` currently reaches the graph as `2 0,000` because padding space glyphs that overlap the digits are joined into the cell text.

**Architecture:** One helper and one replaced line in `geometry.rule_aware_lines`. Each cell's text is built from its **non-space** glyphs, inserting a space only where a space glyph exists **and** the two glyphs it separates are actually apart. Both halves are presence tests — no magnitude comparison, no unit, no tuned constant. Nothing else in the extraction path changes.

**Tech Stack:** Python 3 (`src/iladub/etkl/geometry.py`), pytest.

**Spec:** `docs/superpowers/specs/2026-07-29-padding-space-segmentation-design.md` — read §2, especially the two hypotheses that were tested and **refuted** before this one.

**Run tests with:** `. .venv/bin/activate && python3 -m pytest -q` from the repo root, `/Volumes/WD Green/dev/git/iladub`.

**Pace (changed mid-session):** run **targeted** test files per task. The full suite runs **once**, in Task 2. It takes ~165s and exceeds the default 120s tool timeout — when you run it, set the Bash tool's `timeout` parameter to `400000` ms and run it in the FOREGROUND. Never background a command.

**Baseline:** 603 passed, 5 skipped (`main` at `4907cd0`). Branch `iladub-padding-space-segmentation` is already checked out.

## Global Constraints

- **No tuned constant, no tolerance, no magnitude comparison.** Both halves of the rule are presence tests. Do NOT reintroduce a width or ratio: two such hypotheses were measured and refuted (spec §2) — *"a space overlapping a glyph is padding"* fails on `CARPE DIEM`, and *"split at ≥ the font's median space width"* yields `CARPEDIEM` / `ReferenceNumber` / `10:00:00AM` because glyphs kern **into** the space.
- **A large gap with NO space glyph must NOT split.** That is a *column* gap (residue R13), not a word gap. `rule_aware_lines` emits one `Word` per rule column and must keep doing so.
- **Only emit what the source supports (§7).** This loop exists because the graph asserts `2 0,000`, a string the document does not contain.
- **The unruled path is out of scope** — pdfplumber's `extract_words` has the same defect; it becomes residue R16. Do not touch `extract_words`.
- **Never weaken an existing test.** `borderless_*` fixtures never enter this path.
- **No third-party PDF committed.**

---

## File Structure

| File | Responsibility |
| --- | --- |
| `src/iladub/etkl/geometry.py` | **Modify** — a `_cell_text` helper + the replaced join in `rule_aware_lines`. No other function changes. |
| `tests/etkl/test_padding_space_segmentation.py` | **Create** — the five behavioural tests. |
| `docs/superpowers/residues.md` | **Modify** — R2 closed for the ruled path, R16 added, R1/R4 notes updated (Task 2). |

Task order: 1 → 2.

---

## Measured values (probed while planning — assert, do not re-derive)

From the real document. The glyphs of `20,000` are **touching**:

```
'2'(811.6–814.5) '0'(814.4–817.4) ','(817.3–818.8) '0'(818.8–821.7) '0'(821.7–824.6) '0'(824.5–827.5)
gaps: −0.08, −0.03, −0.04, −0.03, −0.08          → zero positive gaps
padding: ' '(807.6–809.1) ' '(809.0–810.5) ' '(810.5–812.0) ' '(811.9–813.4)
                                                  ↑ this one sits INSIDE the '2'
```

Gap regimes, disjoint: intra-token −0.08…+0.11 · real word space **1.38–1.39** · inter-column 5.39, 22.81, 27.07.

End-to-end with the fix: **49 of 488** GrainCorp cells change, every one a repair; `score = 0.947`, `cells = 447`, **both unchanged**.

---

### Task 1: `rule_aware_lines` drops padding spaces

**Files:**
- Modify: `src/iladub/etkl/geometry.py` (add `_cell_text`; replace line 179 and the bbox on lines 182–183)
- Test: `tests/etkl/test_padding_space_segmentation.py` (create)

**Interfaces:**
- Consumes: `geometry.Char`, `Word`, `Line`, `rule_aware_lines(chars, rule_xs, y_tol=None) -> list[Line]` (signature unchanged).
- Produces: `geometry._cell_text(glyphs) -> str` — the cell's text from its non-space glyphs.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_padding_space_segmentation.py`:

```python
"""Loop F — padding space glyphs must not split a contiguous number (residue R2).

Measured on a real report: the glyphs of 20,000 are TOUCHING (gaps -0.08 to -0.03), but padding
space glyphs OVERLAP them (a space at 811.9-813.4 sits inside the '2' at 811.6-814.5), and
rule_aware_lines joined every glyph in x-order -> '2 0,000'. 49 of 488 cells were wrong.

The rule inserts a space only where a space glyph exists AND the glyphs it separates are actually
apart. Both halves are presence tests — see the spec for two magnitude-based hypotheses that were
measured and refuted.
See docs/superpowers/specs/2026-07-29-padding-space-segmentation-design.md.
"""
from iladub.etkl.geometry import Char, rule_aware_lines

RULES = [800.0, 840.0]


def _c(t, x0, x1, top=10.0):
    return Char(t, x0, x1, top, top + 8.0)


def _texts(chars, rules=None):
    lines = rule_aware_lines(chars, rules or RULES)
    return [[w.text for w in ln.words] for ln in lines]


def _number_glyphs(top=10.0):
    """20,000 with touching glyphs, exactly as measured."""
    return [_c("2", 811.6, 814.5, top), _c("0", 814.4, 817.4, top),
            _c(",", 817.3, 818.8, top), _c("0", 818.8, 821.7, top),
            _c("0", 821.7, 824.6, top), _c("0", 824.5, 827.5, top)]


def _padding(top=10.0):
    """Leading padding spaces, the last of which OVERLAPS the '2'."""
    return [_c(" ", 807.6, 809.1, top), _c(" ", 809.0, 810.5, top),
            _c(" ", 810.5, 812.0, top), _c(" ", 811.9, 813.4, top)]


def test_padding_spaces_do_not_split_a_number():
    # THE DEFECT. Padding glyphs overlap the digits; the digits themselves are touching.
    assert _texts(_padding() + _number_glyphs()) == [["20,000"]]


def test_a_real_word_space_survives():
    # A genuine space: a space glyph AND a positive gap between the glyphs it separates
    # (measured at 1.38-1.39pt on the real document).
    chars = [_c("A", 805.0, 808.0), _c("B", 808.0, 811.0),
             _c(" ", 811.0, 812.4),
             _c("C", 812.4, 815.4), _c("D", 815.4, 818.4)]
    assert _texts(chars) == [["AB CD"]]


def test_both_in_one_cell():
    chars = ([_c("A", 801.0, 804.0), _c("B", 804.0, 807.0), _c(" ", 807.0, 808.4)]
             + _padding() + _number_glyphs())
    assert _texts(chars) == [["AB 20,000"]]


def test_a_large_gap_with_no_space_glyph_does_not_split():
    # That is a COLUMN gap (residue R13), not a word gap. rule_aware_lines emits one Word
    # per rule column and must keep doing so.
    chars = [_c("A", 802.0, 805.0), _c("B", 830.0, 833.0)]
    assert _texts(chars) == [["AB"]]


def test_word_bbox_excludes_leading_padding():
    # The Word must report the ink extent of its NON-space glyphs, not the padding's.
    lines = rule_aware_lines(_padding() + _number_glyphs(), RULES)
    w = lines[0].words[0]
    assert w.x0 == 811.6
    assert w.x1 == 827.5
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_padding_space_segmentation.py -q`
Expected: **3 failures** — `test_padding_spaces_do_not_split_a_number` and `test_both_in_one_cell` produce `'2 0,000'` / `'AB  2 0,000'`, and `test_word_bbox_excludes_leading_padding` reports `x0 == 807.6`. `test_a_real_word_space_survives` and `test_a_large_gap_with_no_space_glyph_does_not_split` already pass — they are guards against over-correcting.

- [ ] **Step 3: Add `_cell_text` to `src/iladub/etkl/geometry.py`**

Insert immediately above `def rule_aware_lines(`:

```python
def _cell_text(glyphs: list["Char"]) -> str:
    """One cell's text, built from its NON-SPACE glyphs.

    A space is inserted between consecutive non-space glyphs only when BOTH hold:
      1. a space glyph lies between them — either within [a.x1, b.x0], or contained in the span
         of a or b (the overlapping-padding case); and
      2. they are actually apart (b.x0 - a.x1 > 0).

    Both are PRESENCE tests. There is no magnitude comparison and no unit, so no tuned constant
    (CLAUDE.md §8). That matters because the obvious magnitude rules were measured and REFUTED:
      - "a space overlapping a non-space glyph is padding" — the legitimate space in 'CARPE DIEM'
        also overlaps its neighbours E and D;
      - "split where the gap >= the font's median space width (1.46pt)" — yields 'CARPEDIEM',
        'ReferenceNumber', '10:00:00AM', because adjacent glyphs kern INTO the space, so the
        measured gap is far smaller than the space's own width.
    It works because the three regimes are disjoint (measured): intra-token kerning -0.08..+0.11,
    real word space 1.38-1.39, inter-column 5-27. A contiguous '20,000' has ZERO positive gaps,
    while padding glyphs overlap the digits they pad.

    A large gap with NO space glyph does not split: that is a COLUMN gap (residue R13), and
    rule_aware_lines emits one Word per rule column.
    """
    gl = sorted(glyphs, key=lambda c: c.x0)
    ns = [c for c in gl if c.text.strip()]
    if not ns:
        return ""
    sp = [c for c in gl if not c.text.strip()]
    parts = [ns[0].text]
    for a, b in zip(ns, ns[1:]):
        between = any(a.x1 - COORD_EPS <= s.x0 and s.x1 <= b.x0 + COORD_EPS for s in sp)
        inside = any(s.x0 >= a.x0 and s.x1 <= b.x1 for s in sp)
        if (b.x0 - a.x1) > 0 and (between or inside):
            parts.append(" ")
        parts.append(b.text)
    return "".join(parts).strip()
```

- [ ] **Step 4: Use it in `rule_aware_lines`**

Replace lines 178–183 of `src/iladub/etkl/geometry.py`:

```python
            gl = sorted(buckets[col], key=lambda c: c.x0)
            text = "".join(c.text for c in gl).strip()
            if not text:
                continue
            words.append(Word(text, min(c.x0 for c in gl), max(c.x1 for c in gl),
                              min(c.top for c in gl), max(c.bottom for c in gl)))
```

with:

```python
            gl = sorted(buckets[col], key=lambda c: c.x0)
            text = _cell_text(gl)
            if not text:
                continue
            # bbox from the NON-space glyphs: a cell padded with leading spaces must not report
            # ink it does not have.
            ink = [c for c in gl if c.text.strip()]
            words.append(Word(text, min(c.x0 for c in ink), max(c.x1 for c in ink),
                              min(c.top for c in ink), max(c.bottom for c in ink)))
```

Also extend `rule_aware_lines`' docstring: after "each non-empty cell becomes one Word at its char-span bbox", add that the cell's text drops padding space glyphs (see `_cell_text`) and the bbox is taken from non-space glyphs.

- [ ] **Step 5: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_padding_space_segmentation.py -q`
Expected: **5 passed.**

- [ ] **Step 6: Targeted regression**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_geometry.py tests/etkl/test_border_grid.py tests/etkl/test_rule_grid_authority.py tests/etkl/test_cells.py tests/etkl/test_grid.py -q`
Expected: all pass. These are the files that exercise the ruled extraction path. A failure means the change altered a shipped ruled fixture — investigate, do not adjust a test.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/geometry.py tests/etkl/test_padding_space_segmentation.py
git commit -m "fix(etkl): padding space glyphs no longer split a contiguous number (loop F, R2)"
```

---

### Task 2: Verification + residue register

**Files:**
- Modify: `docs/superpowers/residues.md`
- Modify: `docs/superpowers/specs/2026-07-29-padding-space-segmentation-design.md` (status line)

**Interfaces:** none — verification and documentation only.

- [ ] **Step 1: Full suite (the one run this loop)**

Run (timeout 400000, foreground): `. .venv/bin/activate && python3 -m pytest -q`
Expected: **608 passed, 5 skipped** (603 baseline + 5 new). Report the real numbers.

- [ ] **Step 2: GrainCorp confirmation (LOCAL, uncommitted)**

Verify the PDF exists at
`/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf`.
If missing, say so and skip — it is a confirmation, not a gate. **Never copy or commit it.**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from iladub.etkl.compile import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
prop = RowRoleProposal(('furniture','continuation','continuation'), 0.85, 'date caption + two wrapped rows')
r = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
for reg in r.regions:
    if reg.verdict == 'asserted': print(reg.kind, reg.verdict, 'cells=', reg.cells)
print('score=', round(r.score, 4))
from rdflib import Namespace
TAB = Namespace('https://w3id.org/iladub/tab#')
vals = [str(o) for _s,_p,o in r.graph.triples((None, TAB.cellText, None))]
print('cells still containing a split number:', [v for v in vals if v.count(' ') and any(ch.isdigit() for ch in v.split(' ')[0]) and ',' in v][:6])
print('sample repaired:', sorted({v for v in vals if '20,000' in v or '118,000' in v})[:5])
"
```

Expected, and **report what you actually observe**:
- `score= 0.947`, `cells= 447` — **unchanged**. This loop must NOT move the score; a change means something unintended and must be investigated, not celebrated.
- `20,000` / `118,000` present; no `2 0,000` or `1 18,000`.

- [ ] **Step 3: Update the residue register**

In `docs/superpowers/residues.md`:
- **R2** — mark closed for the ruled path, noting it remains open for the unruled path as R16. Keep the measured root-cause text; it is what makes the entry useful.
- **R1** — note it is measured to be **R13** (rules coarser than the columns), not a word-segmentation problem.
- **R4** — note it is **still blocked**: subtotal rows now read a clean `20,000`, but data rows read `(blank)Chickpeas 20,000`, so there is no clean numeric column to sum until R13 lands.
- **Add R16** — *"the unruled path keeps the split-number defect"*: pdfplumber's `extract_words` splits `2` from `0,000` on its own; only the ruled path is fixed. Closing it means owning word segmentation for every document. Measured: Loop F.

- [ ] **Step 4: Update the spec status line**

Append the measured outcome to the `**Status:**` line of `docs/superpowers/specs/2026-07-29-padding-space-segmentation-design.md`, using your numbers, and state any difference from the plan explicitly.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/residues.md docs/superpowers/specs/2026-07-29-padding-space-segmentation-design.md
git commit -m "docs: loop F measured outcome; R2 closed for the ruled path, R16 opened"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
| --- | --- |
| §1 in-scope: the `rule_aware_lines` text rule | Task 1 Steps 3–4 |
| §1 success 1 (numbers repaired) | Task 1 `test_padding_spaces_do_not_split_a_number`, `test_both_in_one_cell`; Task 2 Step 2 |
| §1 success 2 (real spaces survive) | Task 1 `test_a_real_word_space_survives` |
| §1 success 3 (49/488, all repairs) | Task 2 Step 2 |
| §1 success 4 (**score does not move**) | Task 2 Step 2, stated as a failure condition |
| §1 success 5 (no regression) | Task 1 Step 6, Task 2 Step 1 |
| §1 success 6 (gate) | Global Constraints + the `_cell_text` docstring |
| §2 Findings 1–4 | Encoded in the measured-values section and the fixtures |
| §3 component | Task 1 |
| §4 all seven test bullets | Task 1 Step 1 (five) + Step 6 (regression) + Task 2 Step 2 (real-world) |
| §5 gate | Global Constraints |
| §6 residues (R2/R16/R1/R4) | Task 2 Step 3 |

**Gap found and closed during review:** §4's "bbox excludes padding" bullet needed its own test — leading padding would otherwise silently widen the `Word`'s ink extent, which feeds `_rule_boundaries`' occupancy test shipped last loop. It is now `test_word_bbox_excludes_leading_padding`, and Task 1 Step 4 changes the bbox accordingly.

**Placeholder scan:** none. Every step carries complete, copy-ready code and exact expected output. Task 2 Step 2 has an explicit skip instruction because the PDF is local-only.

**Type consistency:**
- `_cell_text(glyphs: list[Char]) -> str` — called with `gl` (a `list[Char]`) at the one call site.
- `Char(text, x0, x1, top, bottom)` — the `_c` helper matches; verified against `geometry.py`'s `Char` dataclass.
- `Word(text, x0, x1, top, bottom)` — construction unchanged apart from sourcing the bbox from `ink`.
- `rule_aware_lines(chars, rule_xs, y_tol=None) -> list[Line]` — signature unchanged, so `compile.py`'s call site needs no edit.
- `COORD_EPS` is already imported in `geometry.py` (it is defined there, line 19).
