# Evidence — the straddle discriminator cannot be universally quantified; § 5d is refuted

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r239-straddle-weight-falsifier`, cut from `main` at `9e69261`.
**No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

## 1. What was asked

`2026-09-16-r239-universe-not-key-handoff.md` § 5d left one **PROPOSED** claim and named its own
falsifier. The contrast it rests on is real and was measured in PR #237:

| page | straddled bounds | straddled by |
| --- | --- | --- |
| bfs p5 | 156.9, 302.0, 381.8, 420.1, 479.7 | **27, 19, 14, 19, 3** admitted rows |
| cbh p0 | 76.0, 154.5, 608.7 | **1 line**, all three |

A rule of the form *"more than n rows straddle it"* is the tuned constant CLAUDE.md § 8 forbids —
the defect being repaired is itself a boundary decided by 0.04 pt. § 5d named the only constant-free
form available and the measurement that settles it:

> *"on bfs's five boundaries, does **every** admitted row carrying a cell in the affected column
> straddle, while cbh's banner is the **only** line touching its three?"*

That measurement was run. **It refutes the form.**

## 2. The instrument

`scripts/r239_straddle_universal.py`, PROCEDURAL (§ 8): it runs shipped derivations and prints their
results; it decides nothing and repairs nothing.

```
PYTHONPATH=src:. .venv/bin/python scripts/r239_straddle_universal.py
```

Every definition is taken from the shipped code rather than invented:

- **admitted rows** — `grid.rows` from `derive_data_grid`.
- **a run STRADDLES x** — `r.x0 < x - 0.5 and r.x1 > x + 0.5`, the identical test PR #237's
  instrument used, so the straddle counts are comparable.
- **a run CARRIES column k** — its **centre** falls in `[bounds[k], bounds[k+1])`, which is `place`'s
  own test (`datagrid.py:369-370`), not a re-invention.

The `0.5` is the shipped rectangle tolerance from `_place_for_emit`, copied so the test stays
identical to the code it asks about. No other constant appears in the script.

**"The affected column" is a free parameter, and both readings are printed.** An interior boundary
separates two columns and § 5d's phrase does not say which is affected. Choosing the reading after
seeing the numbers is how a refuted claim gets rescued, so **EITHER** (a row carrying a cell in
either adjacent column) and **BOTH** (in both) are measured side by side, before any verdict.

## 3. The result — the universal drops NOTHING, anywhere

48 interior boundaries across the corpus's three decoration pages. **`UNIV` is false on every one of
them, under both readings** — including all five bfs boundaries the rule was invented to drop.

```
bfs-population-bilan-2 p5  15c 46r  14 interior boundaries
        bound    cols  strad  either  both  UNIV(either)  UNIV(both)  UNIV(vacuous)
       156.90  (0, 1)     27      46    18         False       False          False
       198.00  (1, 2)      0      46    27         False       False          False
       213.80  (2, 3)      0      46     0         False       False           True
       234.20  (3, 4)      0      46     0         False       False           True
       257.90  (4, 5)      0      46     0         False       False           True
       273.20  (5, 6)      0      46    19         False       False          False
       302.00  (6, 7)     19      46    46         False       False          False
       345.60  (7, 8)      0      46    21         False       False          False
       381.80  (8, 9)     14      46     0         False       False           True
       390.20 (9, 10)      0      44     0         False       False           True
       420.10 (10, 11)     19      46     0         False       False           True
       435.60 (11, 12)      0      45     0         False       False           True
       461.60 (12, 13)      0      45     0         False       False           True
       479.70 (13, 14)      3      46     0         False       False           True

WHAT THE UNIVERSAL RULE WOULD DROP
    bfs-population-bilan-2   p5  either-reading drops []   both-reading drops []
    cbh-stem-2026-08-03.pd   p0  either-reading drops []   both-reading drops []
    graincorp-capacity-202   p0  either-reading drops []   both-reading drops []
```

**A rule that drops nothing is not a rule; it is a no-op.** The § 5d remedy shape does not exist in
its constant-free form.

## 4. Why it fails, and why that is STRUCTURAL rather than an accident of these pages

Read the `strad` and `either` columns together. On bfs's strongest case — boundary 156.9, the one
with **27** straddlers, the most straddle evidence anywhere in the corpus — **46 admitted rows carry
a cell in an adjacent column.** 19 carriers do not straddle. The gap is not marginal on any
boundary, on any page.

The reason is visible in the `either` column itself: it reads **44–46 of 46** on all fourteen bfs
boundaries. **On a grid wide enough to matter, the carrier set IS the admitted set** — almost every
row touches almost every pair of adjacent columns. Meanwhile straddling is by construction a
minority event: a straddling run is one run doing what most rows do with two. A universal quantifier
over a set that is nearly everything, of a property held by a minority, can only ever be false.

That argument does not depend on these three pages, which is what makes it the finding rather than
the table above. It does depend on grid width, and the corpus offers no narrow decoration page to
test it on (§ 6).

## 5. The vacuous variant — reported because the numbers surfaced it, and it is WORSE

Dropping the non-emptiness guard makes the BOTH form true wherever **no** admitted row carries cells
in both adjacent columns. It is printed rather than omitted, because omitting it would be choosing
the reading after seeing the result. It is **not proposed**, for two reasons.

**It is not a straddle rule at all.** Its firing condition never mentions straddling; it fires on an
absence of joint carriage. The straddle evidence — the entire content of § 5d's contrast — is not
consulted.

**It is anti-correlated with that evidence.** On bfs it drops 9 of 14 boundaries:

```
    vacuous-variant drops [213.8, 234.2, 257.9, 381.8, 390.2, 420.1, 435.6, 461.6, 479.7]
      -> misses [156.9, 302.0], adds [213.8, 234.2, 257.9, 390.2, 435.6, 461.6]
```

The two it **misses** are 156.9 and 302.0 — precisely the two with the **strongest** straddle witness
(27 and 19 rows). It keeps the boundaries the evidence most condemns and drops six the loop never
wanted. On cbh and graincorp it drops nothing, so it is safe on exactly the pages where the question
does not arise and wrong on the one page where it does.

## 6. Controls

**CONTROL — the straddle counts reproduce PR #237 exactly**, on both recorded pages. A different
number would mean this script measures a different thing and its verdict is void; the script exits
non-zero if they differ.

```
    bfs p5  CONTROL straddle counts vs PR #237: {156.9: 27, 302.0: 19, 381.8: 14, 420.1: 19, 479.7: 3}
            expected {156.9: 27, 302.0: 19, 381.8: 14, 420.1: 19, 479.7: 3} -> MATCH
    cbh p0  CONTROL straddle counts vs PR #237: {76.0: 1, 154.5: 1, 608.7: 1}
            expected {76.0: 1, 154.5: 1, 608.7: 1} -> MATCH
```

**NULL CONTROL — 40 unstraddled boundaries checked, all refused.** A boundary nothing straddles has
carriers and zero straddlers, so both universals must come out false on every one. This is the
direction a silently-inverted quantifier would fail in, and it is the reason a null result here is
not self-validating: the instrument is shown to be capable of saying "no" for the right reason
before its global "no" is believed. The script exits non-zero if any fires.

Both controls passed; `EXIT=0`.

## 7. What is NOT measured here

- **The gate, still.** Nothing in this loop compiled a document or ran the corpus battery either.
  bfs scores 0.8851 off the decoration grid, and the score/adoption/escalation/round-trip effect of
  switching that page to alignment remains **unmeasured**, three loops on. It is the gate any remedy
  must pass and it is still open.
- **Whether the structural argument in § 4 generalises beyond grid width ≥ 15.** The corpus has three
  decoration pages (15, 16 and 20 columns) and no narrow one. A 2- or 3-column decoration page, where
  the carrier set could be a genuine subset of the admitted set, would be the falsifier — and this
  corpus cannot supply one.
- **Whether alignment's 12 columns are the RIGHT 12** — unchanged from PR #237: 3 of 27 rows, presence
  only.
- **Why graincorp-capacity p0 straddles nothing.** Still the clean case, still uninvestigated. Its 15
  boundaries are in the table above and all read `strad 0`.
- **What p5 region16 `DATAGRID_RESIDUE` holds** — carried forward unanswered, four loops on.
