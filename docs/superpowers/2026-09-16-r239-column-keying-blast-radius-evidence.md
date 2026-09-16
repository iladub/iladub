# Evidence — R239's blast radius: the cause is refuted, the prediction holds, the remedy regresses 20 cells

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r239-column-keying-blast-radius`, cut from `main` at
`9ef44d5`. **No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 1. What was asked

[[R239]] was ruled the next subject on 2026-09-16, and the ruling is explicit that the first action
is a measurement rather than a spec or a build:

> across the corpus, how many columns are right-aligned numerics, and does keying on span or `x1`
> rather than `x0` change any column assignment that is currently CORRECT? … **If it regresses even
> one currently-correct assignment the remedy is a different class, and this row should be re-stated
> rather than built against.**

That measurement ran. All three of its clauses are answered below, and the answer to the last one is
**20**.

## 2. The instrument, and why its obvious control is inert

`scripts/r239_column_keying_blast_radius.py`. To vary the key it re-implements the placement inline
rather than calling the shipped `_place_for_emit`, which is the wrong-seam hazard this repo has
recorded twice — so the re-implementation must be shown to BE the shipped one before any number it
prints is load-bearing.

Comparing the two under the centre key agrees on **623 of 623** admitted lines. **On its own that
proves nothing**, because both sides evaluate the same expression; it is the self-validating shape
the R235 census was caught by. The null control is what makes the comparison discriminate — run the
same comparison with a deliberately wrong key, which must DISAGREE (measured 2026-09-16 at `9ef44d5`):

```
key=centre  lines agreeing=623   disagreeing=0
key=x0      lines agreeing=512   disagreeing=111
key=x1      lines agreeing=582   disagreeing=41
```

`x0` and `x1` both disagree, so the comparison is live and the centre agreement is then evidence
that this file's keying is the shipped keying. The script **exits non-zero** if a wrong key ever
agrees, or if the centre key ever fails to.

## 3. R239's stated cause is REFUTED — the shipped key is the CENTRE, not `x0`

The row says *"column assignment … is keyed on `x0`"*. Every placement site in the shipped data-grid
path keys on the run's centre:

| site | expression |
| --- | --- |
| `datagrid.py` `place()` | `centre = (r.x0 + r.x1) / 2` |
| `datagrid.py` `place_indexed()` | `centre = (r.x0 + r.x1) / 2` |
| `datagrid.py` `_place_for_emit()` | `centre = (r.x0 + r.x1) / 2` |

The row's coordinates were read off the **emitted cell bbox** — `emit_data_grid` writes `tab:x0`
from `r.x0`, the cell's own ink extent — and the key was inferred from them. Measuring the bbox was
correct; attributing the decision to it was not.

**The counter-proof is independent of reading the code.** If the shipped key were `x0`, most of
bfs p5's 27 canton rows would sit in col 8, because their `x0` spans 12 pt with digit count.
Measured, `x0`-keying puts **17 of 27** rows in col 8 — while the shipped code drifts exactly **2**.
A key that produced 17 drifters is not the key that produced 2.

**What survives, and sharpens.** For a right-aligned numeric, `x1` is fixed and `x0` moves ~12 pt
with digit count, so the centre still moves ~6 pt — the wrong edge, half as wrong. R239's structural
argument is sound; its named coordinate was not.

## 4. What is actually deciding the column

The boundary is **381.8**, not `x0 ≈ 374.44`, and it is an **author-drawn rule**: p5's universe is
`decoration`, and `drawn_rules` returns `… 345.6, 346.1, 381.8, 390.2, 420.1 …`. Measured
2026-09-16 at `9ef44d5`:

```
 row       text       x0       x1   centre  col  canton
  34    - 3 178   374.38   389.13   381.76    8  Zurich        <- 0.04 pt under the boundary
  45    - 1 651   374.42   389.17   381.79    8  Bâle-Ville    <- 0.01 pt under
  55    - 2 425   374.46   389.20   381.83    9  Vaud          <- 0.03 pt over
  58    - 1 564   374.48   389.23   381.86    9  Genève
```

So the **0.04 pt** magnitude R239 names is real; the coordinate it was attributed to was not.

**And a structure larger than the row states.** Col 9 is `[381.8, 390.2)` — **8.4 pt wide** — while
`- 3 178` is **14.75 pt** of ink. Every one of these 27 cells is wider than the column it lands in:
they all cross the 381.8 boundary. The shipped `place` refuses a straddle only when the *centre*
escapes every bound, so a cell whose ink crosses a boundary is silently resolved by which side its
midpoint happens to fall. Corpus-wide, **206 of 5782** admitted cells straddle their own column
boundary — 121 of them on bfs p5 alone.

## 5. The blast radius

Every cell an unconditional `x1` re-key would move, joined to the **measured** alignment class of
its source column (the class is derived from that column's own cells: which edge is the steady one).
Measured 2026-09-16 at `9ef44d5`:

```
doc                    pg  kc  k1  class(kc)    n  sprd_x0  sprd_x1  example
cbh-stem-2026-08-03.pd  0   1   2      RIGHT    1    69.02    40.52  Stock at Port (Main Storage
cbh-stem-2026-08-03.pd  0   9  10       LEFT    1    24.84    77.96  PORT MAINTENANCE SHUTDOWN DA
graincorp-stem-2026-07  0   0   1       LEFT    2     4.71    37.34  Fisherman Islands Total
graincorp-stem-2026-07  1   0   1       LEFT    1     4.71    37.35  Fisherman Islands Total
graincorp-stem-2026-07  1   2   3       LEFT    6     0.05    16.05  SHUTDOWN
bfs-population-bilan-2  5   6   7      RIGHT   19     9.53     6.31  118 270
bfs-population-bilan-2  5   8   9      RIGHT    2    10.67     9.52  - 3 178
who-wfa-boys-zscore-0-  0   0   1       LEFT    4     0.00     9.95  0:10
who-wfa-boys-zscore-0-  1   0   1       LEFT    4     0.00     9.95  2:10
who-wfa-boys-zscore-0-  2   0   1       LEFT    2     0.00     9.95  4:10

cells=5782  straddling their own column boundary=206  moved by an x1 re-key=42
moved cells by SOURCE-column alignment class: {'RIGHT': 22, 'LEFT': 20}
```

**Right-aligned columns, corpus-wide:** of 171 columns carrying ≥ 3 cells, **50 are right-aligned**
(x1 the steady edge), 44 left-aligned, 77 neither. **41 of the 50** are measure columns. That is the
first clause of the ruling, answered.

## 6. The verdict against the ruling's own gate

The gate was *"if it regresses even one currently-correct assignment, the remedy is a different
class."*

- **Confirmed, narrowly:** R239's falsifiable prediction holds. Under an `x1` key all 27 bfs p5 rows
  land in col 9 — the two drifters join the other 25.
- **Refuted, decisively:** the same re-key moves **20 cells out of LEFT-aligned columns, where `x1`
  is the noisy edge** — the exact mirror of the defect R239 names. WHO's stub column is the cleanest
  case: `x0` spread **0.00**, `x1` spread **9.95**, and the re-key pushes `0:10` — a `Year:Month`
  address — out of the Text stub and into a `Quantity` measure column.

So the remedy R239 prescribes **regresses 20, not one**, and by the ruling's own terms the row is to
be **re-stated rather than built against**. It has been (register row updated this loop).

**The re-statement the evidence supports:** the subject is not *which edge to key a right-aligned
numeric on*. It is that **a column boundary falls inside a cell's ink, and the straddle is resolved
silently by a midpoint**. 206 cells do this. Any remedy keyed on a single edge is wrong for the
opposite alignment, and a remedy that first classifies a column's alignment is making a reading
judgement — which is the § 8 call the ruling deliberately left unmade, and this evidence now argues
is NEURAL-shaped rather than a one-line keying change.

## 7. What is NOT measured here

- **Whether the 19-cell bfs col6→col7 move is a repair or a regression.** It is the largest single
  block in the table and its source column is RIGHT-aligned, but nothing here establishes which
  column `118 270` belongs to. **22 RIGHT-class moves must not be read as 22 repairs** — only the
  2 canton drifters are known repairs.
- **Whether the alignment class is stable for columns with few cells.** The class is computed over a
  column's own admitted cells; the table above includes three columns with n=1.
- **The 77 "neither" columns.** Neither edge is steady; no remedy proposed here would have a defined
  answer for them.
- **Whether any of this generalises past the 7-document corpus.** 5782 cells, 27 pages.
- **What p5 region16 `DATAGRID_RESIDUE` holds** — carried forward unanswered from the prior loop.
