# Handoff — R238 and R239 are one defect on bfs p5: the column universe, not the column key

**Topic:** The three measurements ran. bfs p5's col-9 span is witnessed only by its **short** cells;
R238's two "dropped" columns are **outside the rectangle** and the row is admitted *because* of that
ink; and refusing the decoration universe makes **both** symptoms vanish with no row lost. Neither a
blanket nor a surgical refusal generalises — cbh p0 refutes both.

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r239-universe-not-key`, cut from `main` at `5f14054`.
**No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — the defect on bfs p5 is the UNIVERSE, not the key

Measured, evidence § 4. Forcing the alignment universe: the rectangle grows `124.3..495.3` →
`72.12..522.82`, **all 27** canton rows place the intercantonal value in **one** column (R239's
symptom gone), and the label and final `%` come inside and are **emitted** (R238's symptom gone),
with 46 rows and none lost. The key was never the subject; PR #236's re-statement was right to move
off it, and this moves off the edge question entirely.

### 5b. ASSERTED — R238 and R239 are one defect wearing two faces, and R238 is sharper than recorded

A boundary too narrow for its cells (`[381.8, 390.2)` is 8.4 pt; `- 3 178` is 14.74 pt) and a
rectangle too small for its table (label ends at 85.65, `%` starts at 516.18). **R238's mechanism is
not "the grid drops the label"**: `place_indexed` admits those rows *because* `index_ink` finds ink
outside the rectangle — *"addressed by that ink"* — and the emitter then never carries it. The row
label is the thing that qualified the row for admission.

### 5c. ASSERTED — no remedy is available in either form tried, and `grid.py`'s test cannot be ported

Blanket refusal costs cbh p0 **5 rows**. The surgical variant (drop only boundaries an admitted
row's ink straddles) **kills cbh p0's grid outright**. `grid.py::_rule_boundaries` already does this
threshold-free but is **band-scoped**; page-wide it sees bfs's 300–450 pt footnote and caption runs,
which straddle everything. Scoping to admitted rows removes the prose and is still not enough,
because an admitted row can be a banner — cbh's three straddled boundaries all come from **one**
line.

### 5d. PROPOSED — the discriminator is the WEIGHT of the straddle evidence, and this loop did not test it

**Rests on a contrast measured on two pages, never turned into a rule.** bfs's boundaries are
straddled by **27, 19, 14, 19 and 3** admitted rows; cbh's three are straddled by **1 line each**. A
boundary refuted by a table's own data cells en masse looks nothing like one refuted by a single
banner.

**Why this may be wrong, stated before anyone builds it:** any rule of this shape needs a count or a
proportion, and **a tuned threshold here is precisely what CLAUDE.md § 8 forbids** — the defect being
repaired is itself a boundary decided by 0.04 pt. A defensible form would have to be ordinal or
universally quantified (e.g. *every* admitted row's cell in that column straddles), not "more than
n". **The measurement that would settle it:** on bfs's five boundaries, does *every* admitted row
carrying a cell in the affected column straddle, while cbh's banner is the *only* line touching its
three? If that holds, the rule is a universal quantifier and needs no constant. **The § 8
classification remains the maintainer's.**

### 5e. ASSERTED — what NOT to do

- **Do not switch bfs p5 to the alignment universe without running the corpus battery.** Nothing
  here compiled a document. bfs scores 0.8851 off the decoration grid; the effect of the switch on
  score, adoption, escalation and round-trip is **unmeasured** (evidence § 6).
- **Do not read § 5a as "alignment is correct for bfs p5".** Label and `%` were checked on **3** of
  27 rows, for presence only — not families, not the header, not the other 24.
- **Do not port `grid.py::_rule_boundaries` page-wide.** It is band-scoped for a reason (§ 5c).
- **Do not raise a new row for the banner contamination.** It is R239's closure work, not a separate
  obligation; both rows were updated in place this loop.
- **Do not trust the `tab` rung's `file:line` citations or `FIRES n` counts** — [[R236]], [[R237]].

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-16-r239-universe-not-key-evidence.md` (§ 2 the short-cell
  witnesses, § 3 R238's real mechanism, § 4 the universe comparison, § 5 why no remedy generalises,
  § 6 what is not measured).
- **The instrument** — `scripts/r239_universe_not_key.py`, parts A/B/C, control and null control
  inline, exits non-zero if either fails.
  `PYTHONPATH=src:. .venv/bin/python scripts/r239_universe_not_key.py`
- **The sites** — `datagrid.py`: `_boundaries_from_decoration` (keeps a span on ≥ 2 contained runs),
  `place_indexed` / `index_ink` (admits a row on outside ink), `_place_for_emit` (drops it).
  `grid.py::_rule_boundaries` is the band-scoped test that already does what is wanted.
- **The prior loop** — `2026-09-16-r239-column-keying-blast-radius-handoff.md` (PR #236).
- **The rows** — [[R238]] and [[R239]], both updated in place.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| A span is witnessed by its short cells, straddled by its long ones | evidence § 2, R239's row |
| R238's columns are outside the rectangle; index ink admits then is dropped | evidence § 3, R238's row |
| Refusing decoration fixes both symptoms on bfs, no rows lost | evidence § 4, both rows |
| Blanket refusal costs cbh 5 rows; surgical kills cbh's grid | evidence § 5, R239's row |
| `grid.py`'s test is band-scoped and cannot be ported page-wide | evidence § 5, this § 5c |
| **What to build** | **UNDECIDED — a § 8 classification, the maintainer's** |

## 3. Unverified or assumed

- **§ 5d entirely** — the straddle-weight discriminator, and that it can be written without a tuned
  constant. Its falsifier is named there and was not run.
- **The score/graph effect of switching bfs p5's universe.** Not compiled, not batteried. This is
  the gate, and it is open.
- **Whether alignment's 12 columns are the right 12** — 3 rows checked, presence only.
- **Whether the many-rows-vs-one-line contrast holds anywhere else.** Two pages.
- **Why graincorp-capacity p0 straddles nothing.** The clean case, uninvestigated.
- What p5 region16 `DATAGRID_RESIDUE` holds — still unanswered, three loops on.

## 4. What this session did, and what it cost

Ran the three agreed measurements plus two follow-ups, confirmed the universe hypothesis on bfs,
refuted both available remedy shapes on cbh, and updated both rows in place. Built no remedy, edited
no shipped file.

**The cost worth carrying: an instrument's framing can be wrong while its numbers are right.** The
surgical-variant probe reported bfs p5 as `12c 46r` under "drop the straddled boundaries" — and that
was **not** what it measured. Removing five boundaries made the decoration vector shorter than the
alignment one, so `derive_data_grid`'s own `len(decor) >= len(align)` test handed the page to
alignment. The figure was correct and the label above it was false; it was caught only because Q2
had independently produced the same `12c 46r` by a different route, and two routes agreeing on a
number that *should* have differed is what exposed it.

That is the fourth time in two loops that a first reading was wrong and a second, independent
measurement caught it — and the third time the wrong reading was *mine*, not an inherited one.
