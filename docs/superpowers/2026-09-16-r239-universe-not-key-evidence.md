# Evidence — the defect is the column UNIVERSE, not the column key; R238 and R239 share one root

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r239-universe-not-key`, cut from `main` at `5f14054`.
**No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 1. What was asked

PR #236 re-stated [[R239]]: the subject is a column boundary falling inside a cell's ink, resolved
silently by a midpoint. This loop asked the next question — **should that boundary have existed at
all?** — as three measurements agreed with the maintainer:

1. Which runs actually *witness* bfs p5's col-9 span?
2. If the decoration universe is refused, what happens to every currently-good page?
3. Do [[R238]] and [[R239]] share a cause?

All three ran. The instrument is `scripts/r239_universe_not_key.py`; it exits non-zero if either of
its controls fails, and exits 0 at `5f14054`.

## 2. Q1 — a span is witnessed by its SHORT cells, and straddled by its long ones

bfs p5's col 9 is the drawn span `[381.8, 390.2)` — **8.4 pt** wide. `_boundaries_from_decoration`
keeps a span when ≥ 2 runs *fit inside* it. Measured 2026-09-16 at `5f14054`, its 13 witnesses:

```
   contained (the witnesses): 13
                0  w= 2.64  x0=386.49 x1=389.14
              762  w= 7.83  x0=381.30 x1=389.13
                1  w= 2.64  x0=386.49 x1=389.13
              342  w= 7.83  x0=381.31 x1=389.13
              - 5  w= 6.97  x0=382.17 x1=389.14
               36  w= 5.24  x0=383.91 x1=389.15
```

Every witness is ≤ 7.83 pt. The straddlers include `- 3 178` at **14.74 pt**. So the span that
decides the column is **witnessed only by the short values of a right-aligned column, while the long
values of that same column cross it**. That is the mechanism behind R239's 0.04 pt boundary, stated
without reference to any edge.

## 3. Q3 — R238's two dropped columns are OUTSIDE the rectangle, and the row is admitted BECAUSE of it

The decoration rectangle is `124.3 .. 495.3`. Measured on three canton rows:

```
  line 34: emitted cols=[1, 2, 4, 6, 7, 8, 11, 13]
             Zurich x0=  72.20 x1=  85.65 inside=False col=None
            1 579 967 x0= 147.85 x1= 168.64 inside= True col=1
                  1.6 x0= 516.18 x1= 522.72 inside=False col=None
```

The canton label ends at **85.65**, left of the rectangle; the final *Variation en %* starts at
**516.18**, right of it. Neither is misassigned — **neither is in the grid at all**.

And the design knows. `place_indexed` admits a row with fewer cells when `index_ink` finds ink
outside the rectangle, on the stated grounds that *"a row whose address lives entirely in the index
block outside the rectangle is addressed by that ink"* — **and that address is then never emitted**.
So R238 is sharper than its row records: the row label is not dropped by accident, it is the thing
that *qualified the row for admission*, and the emitter has no path to carry it.

## 4. Q2 — refuse the decoration universe, and both symptoms vanish on bfs

```
B. bfs p5 WITHOUT THE DECORATION UNIVERSE — what happens to R239 and R238
   decoration (shipped)   rect 124.30..495.30  15c 46r
     R239  intercantonal value sits in 2 column(s): {8: 2, 9: 25}
     R238  label / final % emitted: [('Suisse 3', False, False), ('Zurich', False, False), ('Genève', False, False)]
   alignment (forced)     rect 72.12..522.82  12c 46r
     R239  intercantonal value sits in 1 column(s): {7: 27}
     R238  label / final % emitted: [('Suisse 3', True, True), ('Zurich', True, True), ('Genève', True, True)]
```

**All 27 canton rows place the intercantonal value in one column, and the label and the final `%`
come inside and are emitted — with 46 rows, none lost.** Q3 is answered: on this page R238 and R239
are one defect, the decoration universe, wearing two faces — a boundary too narrow for its cells,
and a rectangle too small for its table.

## 5. Q2 — but the remedy does not generalise, in either available form

**Blanket refusal is not available.** Corpus-wide, three pages use a decoration universe:

```
     bfs-population-bilan-2   p5  decoration 15c 46r  ->  alignment 12c 46r   rows unchanged
     cbh-stem-2026-08-03.pd   p0  decoration 20c 50r  ->  alignment 16c 45r   ROWS LOST 5
     graincorp-capacity-202   p0  decoration 16c 27r  ->  alignment 15c 27r   rows unchanged
```

Control: decoration pages 3 → 0, pages deriving a grid 16 → 16.

**The surgical variant is not available either.** Dropping only the interior boundaries that an
*admitted row's* ink straddles kills cbh p0 outright (null control: patching with the unchanged
vector reproduces each baseline exactly):

```
   cbh p0  straddled=[76.0, 154.5, 608.7]  ->  GRID LOST
       bound 76.0:  1 run(s) on line(s) [75]  e.g. 'Stock at Port (Main Storage Ar'
       bound 154.5: 1 run(s) on line(s) [75]  e.g. 'Stock at Port (Main Storage Ar'
       bound 608.7: 1 run(s) on line(s) [75]  e.g. 'PORT MAINTENANCE SHUTDOWN DATE'
```

**`grid.py::_rule_boundaries` cannot simply be ported.** It already refuses a rule vector when any
word straddles it, threshold-free — but it is **band-scoped**, and a page carries prose 300–450 pt
wide (bfs p5's footnotes and caption) that straddles every boundary there is. Scoping to admitted
rows removes the prose; cbh shows that is still not enough, because an admitted row can itself be a
banner.

**The contrast is measured, and it is the only discriminator this loop found:**

| page | straddled bounds | straddled by |
| --- | --- | --- |
| bfs p5 | 156.9, 302.0, 381.8, 420.1, 479.7 | **27, 19, 14, 19, 3** admitted rows |
| cbh p0 | 76.0, 154.5, 608.7 | **1 line** (line 75), all three |

bfs's boundaries are refuted *en masse by the table's own data cells*; cbh's are refuted by a single
banner. Whether that separation is a rule is **not tested here** — turning it into one is remedy
design and a CLAUDE.md § 8 classification, which stays the maintainer's.

## 6. What is NOT measured here

- **The compiled graph and the document score.** Nothing here ran `compile_document` or the corpus
  battery. bfs currently scores 0.8851 off the decoration grid; **what switching that page to
  alignment does to the score, the adoption, the escalations and the round-trip is unmeasured**, and
  it is the gate any remedy must pass.
- **Whether alignment's 12 columns are the RIGHT 12.** Label and `%` were checked on **3** of 27
  rows, and only for presence — not the column families, not the other 24 rows, not the header.
- **Whether the many-rows-vs-one-line contrast holds anywhere else.** Two pages, one contrast.
- **Why graincorp-capacity p0 has no straddled boundary at all** — it is the clean case and was not
  investigated.
- **What p5 region16 `DATAGRID_RESIDUE` holds** — carried forward unanswered from two loops back.
