# Handoff — R239's remedy regresses 20 cells; the row is re-stated, and the real subject is the straddle

**Topic:** [[R239]]'s blast-radius measurement ran, as ruled. Its stated cause is **refuted** (the
shipped key is the run CENTRE, not `x0`), its falsifiable prediction **holds** (an `x1` key puts all
27 bfs p5 rows in col 9), and its prescribed remedy **regresses 20 currently-correct cells** in
LEFT-aligned columns. By the ruling's own gate the row is re-stated, not built against.

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r239-column-keying-blast-radius`, cut from `main` at
`9ef44d5`. **No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — do NOT build the `x1` re-key. It regresses 20 cells.

Measured, evidence § 5. An unconditional `x1` re-key moves 42 cells; **22 come from RIGHT-aligned
columns and 20 from LEFT-aligned ones**, where `x1` is the noisy edge — the exact mirror of the
defect R239 names. WHO's stub column is the cleanest case (`x0` spread **0.00**, `x1` spread
**9.95**): the re-key pushes `0:10`, a `Year:Month` address, out of the Text stub into a `Quantity`
measure column.

The ruling's gate was *"if it regresses even one, the remedy is a different class."* It regresses
20. **The row has been re-stated in the register this loop, and must not be built against as
written.**

### 5b. ASSERTED — R239's stated cause is refuted; the key is the CENTRE

All three shipped placement sites key on `(r.x0 + r.x1) / 2` — `place`, `place_indexed`,
`_place_for_emit`. The row's `x0` coordinates were read off the emitted cell bbox, which
`emit_data_grid` writes from the cell's own ink extent, and the key was inferred from them.
Independent counter-proof, needing no code reading: `x0`-keying puts **17 of 27** bfs rows in col 8;
the shipped code drifts exactly **2**. The boundary is **381.8**, an author-drawn rule — not
`x0 ≈ 374.44`. The 0.04 pt magnitude is real; the coordinate was not.

### 5c. ASSERTED — the real subject is a boundary inside a cell's ink

Col 9 on bfs p5 is 8.4 pt wide; `- 3 178` is 14.75 pt of ink. **Every one of those 27 cells is wider
than the column it lands in.** `place` refuses a straddle only when the *centre* escapes all bounds,
so a cell crossing a boundary is resolved silently by which side its midpoint falls. Corpus-wide,
**206 of 5782** admitted cells straddle their own column boundary. That is the defect; "which edge
for a right-aligned numeric" is one symptom of it.

### 5d. PROPOSED — the § 8 classification is NEURAL-shaped, and this loop did not test that

**Rests on a judgement not measured here.** Any remedy keyed on a single edge is wrong for the
opposite alignment (§ 5a is the measurement of that), so a single-edge fix is ruled out. What
remains is either (i) classify a column's alignment first, or (ii) treat a straddle as
underdetermined and refuse/propose rather than resolve. **(i) is itself a reading judgement** — a
"which column does this span" question, the § 8 NEURAL signature — and calling it AXIOM because it
looks geometric is what the gate forbids.

**Why this may be wrong, stated before anyone builds it:** nothing here tests whether an
alignment classifier would actually be underdetermined in practice. On the 94 classifiable columns
the steady edge is unambiguous (spreads differ by more than a point in every case printed), and a
classifier that is never in doubt on real input may well be AXIOM — a derivation over evidence
present in the column's own cells — rather than NEURAL. **The measurement that would settle it:** on
the 77 "neither" columns, is there a column where the two edges are genuinely tied? If none, (i) is
decidable and the NEURAL framing is over-cautious. **The § 8 call remains the maintainer's.**

### 5e. ASSERTED — what NOT to do

- **Do not read the 22 RIGHT-class moves as 22 repairs.** Only the 2 canton drifters are known
  repairs; the 19-cell bfs col6→col7 block has no source truth behind it (evidence § 7).
- **Do not re-measure R239's coordinates from `tab:x0`/`tab:x1`.** That is the bbox, not the key —
  it is how the row's cause came out wrong.
- **Do not trust a control that compares a re-implementation against the code it copies.** The
  centre control agrees 623/623 and proves nothing without its null (evidence § 2).
- **Do not pin a `cor:scoreFloor` for bfs.** The 2026-08-20 hold stands.
- **Do not trust the `tab` rung's `file:line` citations or `FIRES n` counts** — [[R236]], [[R237]].

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-16-r239-column-keying-blast-radius-evidence.md` (§ 2 the
  control and its null, § 3 the refuted cause, § 4 what actually decides, § 5 the blast radius,
  § 6 the verdict, § 7 what is not measured).
- **The instrument** — `scripts/r239_column_keying_blast_radius.py`, null control inline, exits
  non-zero if a deliberately wrong key agrees or the centre key does not.
  `PYTHONPATH=src:. .venv/bin/python scripts/r239_column_keying_blast_radius.py`
- **The keying sites** — `datagrid.py`: `place`, `place_indexed`, `_place_for_emit`.
- **The prior loop** — `2026-09-16-r44-roundtrip-reporting-or-reading-handoff.md`, whose § 5c raised
  R239 and whose § 5d predicted exactly this regression risk.
- **The rows** — [[R239]] re-stated; [[R238]] untouched.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The shipped key is the centre, not `x0` | this § 5b, evidence § 3, R239's row |
| The `x1` prediction holds on bfs p5 (27/27) | evidence § 6, R239's row |
| The `x1` remedy regresses 20 LEFT-aligned cells | this § 5a, evidence § 5, R239's row |
| R239 is re-stated, not built against | R239's row, per the ruling's own gate |
| 206 of 5782 cells straddle their column boundary | evidence § 4, R239's row |
| **The § 8 classification for the remedy** | **UNDECIDED — the maintainer's** |

## 3. Unverified or assumed

- **§ 5d entirely** — that the remedy is NEURAL-shaped, and that an alignment classifier would be
  underdetermined. The falsifying measurement is named there and was not run.
- **Whether the 19-cell bfs col6→col7 move is repair or regression.** No source truth.
- **Whether alignment class is stable for columns with few cells** — three columns in the table have
  n=1.
- **Whether any of this generalises past the 7-document corpus** (5782 cells, 27 pages).
- What p5 region16 `DATAGRID_RESIDUE` holds — carried forward unanswered.

## 4. What this session did, and what it cost

Took the ruled subject, ran the blast-radius measurement it names, refuted the row's stated cause,
confirmed its prediction, refuted its remedy, and re-stated the row. Built no remedy, edited no
shipped file.

**The cost worth carrying: the loop's first instinct was to inherit the row's cause and measure from
there.** R239 says "keyed on `x0`" in bold, and the natural loop reads that as settled and goes
looking for the blast radius of changing it. Reading the three placement sites took one grep and
showed the shipped key is the centre — after which the row's boundary value (`374.44`), its
coordinate, and its framing ("right-aligned numerics") were all wrong, while its *prediction* and
its *magnitude* were right. A row raised by a careful loop one day earlier, from a real measurement,
still carried a wrong cause into a maintainer's ruling.

That is the third consecutive loop in which the first reading of a measurement was wrong and a
second, independent measurement caught it — and the second instance is inside this loop: the
`623/623` control was written, passed, and was **inert**, exactly as the R235 census was. It only
became evidence once the null control was run against it.
