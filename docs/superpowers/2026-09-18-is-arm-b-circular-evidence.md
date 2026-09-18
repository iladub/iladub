# Evidence — arm B's scope is circular in the reference it would reach for first, and buildable in the one beside it

**Serves:** maintenance — [[R258]] is named by no `prog:blockedBy`, and neither is [[R255]], which
this continues. Declared `maintenance` deliberately, per [[R257]].

**Date:** 2026-09-18. **Branch:** `r258-is-arm-b-circular`, cut from `main` at `6e5893f`.

**Doc impact: none.**

**Subject.** The previous loop's handoff § 5a, ASSERTED: *measure whether arm B's own scope is
circular.* [[R258]]'s ruled remedy admits a header-row address only where a second, independent
reading agrees — so it must know **which addresses are header rows**, and the worry put on record
was that if a first reading collapses the split to 1 there is no header block left to scope the
oracle to. The worry is **confirmed for the reference the remedy would reach for first, and
dissolved by a second reference that was available all along.** § 5b's population figure is
refuted as arithmetic and confirmed in substance.

---

## 1. The question, stated so it can be answered by measurement

Arm B needs a set: *the header-row addresses of this band*. Two candidates exist, and until this
loop nobody had said which one the remedy meant.

| reference | how it is computed | circular? |
| --- | --- | --- |
| `perturbed` | the split the pipeline **returns** — `header_body_split(band, grid)`, which reads `band.unshown` at `headers.py:111-112` | **YES**, by construction: the reading being checked decides the scope of the check |
| `free` | the same query over the same evidence graph with `unshown = ()` — the floor of the lattice | **NO**: it is computable before any reading is consumed |

Both are one call to the same function. The difference is one argument, and § 2 shows it is the
difference between an oracle that cannot see the defect and one that sees all of it.

## 2. The circularity is real, and it is total on the flagship band

`./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --band cbh-stem 0 1`, then the same
sweep seeded with one collapsing address (`--circularity`, and the scratch reproduction in § 6):

```
seed = ()        axiom/final = 7/7    header block rows 0..6  -> 21 of 151 addresses   7 movers
seed = {(6,9)}   axiom/final = 1/1    header block rows 0..0  ->  1 of 151 addresses   0 movers
```

Read the two rows together:

1. **The perturbed scope excludes the address that caused the collapse.** `(6,9) 'Volume'` is a
   header address under the free split (row 6 < 7) and a **body** address under the split its own
   abstention produced (row 6 ≥ 1). An oracle scoped to the returned header block would examine
   **one address** on this band — the title line in row 0 — and would never be asked about the
   label row at all. That is the circularity § 5a predicted, and it is not a margin: the scope
   loses 20 of its 21 addresses and every one of the movers.
2. **A collapsed split is a FIXED POINT.** Seeded with `(6,9)`, **no further single address moves
   the split** — 7 movers before, **0** after. So there is no second-order probe either: an
   oracle that asked *"does another address move this reading?"* would report nothing to see on
   exactly the bands that are already wrong. The collapse is one-way and self-concealing.

## 3. The free reference is not circular, and on cbh it covers every collapse

Same four cbh bands, movers classified by whether they lie inside the **abstention-free** header
block and by how far they move the split:

```
band  free  ink  |hdr_free|  movers  in hdr_free   collapses to 1   one-step moves
   1     7  151          21       7            5          5 (all)                2
   3     4  222          18       7            5          5 (all)                2
   5     5  191          19       5            4          4 (all)                1
   7     4   82          18       6            5          5 (all)                1
```

**The separation is exact and it is the useful one.** Every mover that collapses the split to the
floor lies inside the free header block — 19 of 19 across the four bands, each one a column label
(`'VNA #'`, `'Date Nominated'`, `'ETD'`, `'Volume'`, `'+/- %'`). Every mover *outside* it lies on
the FIRST BODY ROW (`'Accepted'`, `'Completed'`) and moves the split by **exactly one row**,
7→6, 4→3, 5→4, 4→3 — the arm-A figures, now explained: those are the same six addresses, and they
are one-step moves rather than erasures.

So an oracle scoped to the free header block is not a partial remedy for the defect R258 names. It
is a **total** one for the collapse, and silent about a one-row shift that is a different and much
smaller claim. § 7 puts the same question to the other four documents and the coverage of the
collapse stays total.

## 4. § 5b's population figure is refuted, and its substance survives

The prediction was **20 addresses against cbh band 1's 151**, an eighth of the band. Measured:
**21**, and the 20 it quoted is a **different set** — the low-contrast address count from
[[R258]]'s own containment measurement.

```
band   |hdr_free|   |low-contrast|   overlap
   1           21               20        16
   3           18               20        16
   5           19               20        16
   7           18               20        16
```

Four addresses of the low-contrast set are outside the free header block on every band, and 2-5 of
the header block are not low-contrast. The two sets are near-equal in SIZE on every cbh band and
**equal on none of them**, which is exactly how a wrong population passes unnoticed: the figure
was right to within one and came from the wrong place. The claim underneath — the oracle runs on
the header block, roughly an eighth of the band — stands at 21/151, 18/222, 19/191, 18/82.

## 5. What this does NOT establish

- **That the free split is the RIGHT split.** It is the split with every glyph counted as shown,
  which is the pre-reading state, not a better reading. Arm B uses it as a **scope**, where being
  generous is the safe direction; nothing here licenses using it as an answer.
- **That an agreement oracle can be built.** § 5a asked only whether it has a non-circular
  population. It does. What the second reading *is*, and what disposes it, is unbuilt.
- **That any of this is reachable live.** `dispose` still refuses every cbh region (refusal 2, the
  grid mismatch), so these bands have no live reading. Unchanged from the previous loop.
- **Direction of movement corpus-wide.** On cbh every mover moves the split DOWN. § 7 reports what
  the corpus sweep found elsewhere; nothing outside it is asserted.

## 6. How to re-run it

```
./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --band cbh-stem 0 1
./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --circularity            # whole corpus
./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --circularity cbh-stem   # one document
```

`--circularity` is this loop's addition to the instrument that already carries the rest of the
thread. It prints both header-block sizes per band (`|hdrF|`, `|hdrP|`), the movers, how many fall
inside the free block, and the second-order sweep from a seeded collapse. The corpus mode needs
`corpus/*.pdf`, which is fetched and never committed — so `tests/test_split_sensitivity_instrument.py`
carries the three claims of §§ 2-3 on the fixture CI can see, each falsified before it shipped
(§ 8).

## 7. The whole corpus — 71 of 80 movers inside the non-circular scope, and every escaping one named

`./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --circularity` (≈ 47 min, 17 of the
122 gridded bands have a mover). `|hdrF|` and `|hdrP|` are the two header-block sizes of § 1;
`seed` is the split after the furthest-DOWN mover abstains; `mov2` is the second-order sweep from
that state.

```
document                       pg  b   ink free |hdrF| |hdrP|  mov  inF  seed  mov2
cbh-stem-2026-08-03.pdf         0  1   151    7     21      1    7    5     1     0
cbh-stem-2026-08-03.pdf         0  3   222    4     18      1    7    5     1     0
cbh-stem-2026-08-03.pdf         0  5   191    5     19      1    5    4     1     0
cbh-stem-2026-08-03.pdf         0  7    82    4     18      1    6    5     1     0
graincorp-stem-2026-07-31.pdf   0  2   612    4     26      1    3    3     1     0
graincorp-stem-2026-07-31.pdf   1  1   850    3     25      1    3    3     1     0
graincorp-stem-2026-07-31.pdf   2  1   766    3     25      1    4    4     1     0
bfs-population-bilan-2023.pdf   4  0     5    1      1      0    1    0  None     0
ons-index-of-services-2026-02.  0  1    16    1      3     11    1    0     6     2
ons-index-of-services-2026-02.  4  2     5    1      2      0    1    0  None     0
ons-index-of-services-2026-02.  7 13    31    2      6      1    4    4     1     0
ons-index-of-services-2026-02.  7 14    81    2      6      1    4    4     1     0
ons-index-of-services-2026-02.  8  4    81    2      6      1    4    4     1     0
ons-index-of-services-2026-02.  8  5    65    2      5      1    3    3     1     0
who-wfa-boys-zscore-0-5.pdf     0  2    89    2     12      1    9    9     1     0
who-wfa-boys-zscore-0-5.pdf     1  2    78    2     12      1    9    9     1     0
who-wfa-boys-zscore-0-5.pdf     2  1    78    2     12      1    9    9     1     0

17 bands with at least one single-address mover; 80 movers, 71 of them inside the FREE header block.
16 of 17 seeded collapses are fixed points — no further single address moves the split once it has
collapsed.
```

**Three readings, and the third is the one that matters.**

1. **The perturbed scope collapses on 14 of 17 bands** (`|hdrP| = 1`) and **empties on two more**
   (`0`). The reference arm B would reach for first survives on exactly one band in the corpus.
2. **Every collapse is a fixed point.** `seed = 1` on 14 bands and `mov2 = 0` on all 14; the two
   `None` seeds are fixed too. The single non-fixed-point — `ons` page 0 band 1, `mov2 = 2` — is
   the one band in the corpus where abstention moves the split **UP** (`(1,3) '14 May 2026'`,
   1 → 6), so no collapse happened there to be concealed.
3. **The 9 movers outside the free header block are enumerated, and none of them is a collapse.**
   Six are cbh's first-body-row addresses of § 3 (one-step moves). The other three sit on bands
   whose free split is **already 1**, so there is no header block above the floor to scope
   anything to: `bfs` 4/0 `(3,1) '5'` and `ons` 4/2 `(1,0) '2.'` both move the split to **None** —
   the AXIOM silenced with no interior rule, which **escalates** the band rather than mis-reading
   it — and `ons` 0/1 is the upward mover above. **Zero collapses escape the non-circular scope.**

**And the mechanism is the same on every document.** The in-block movers are column labels
wherever they were printed: `'Month' 'L' 'M' 'S' '-3 SD' '-2 SD' '1 SD' '2 SD' '3 SD'` on who
page 0 (all nine, all row 1, all collapsing 2 → 1), `'S243' 'KI77' 'KI7G' 'KI7O'` — the series
codes — on ons page 7, `'Commencement' 'Date ETD of Ship' 'Total'` on graincorp-stem page 0.
That last band is also the counter-example to a tidier claim: `'Commencement'` is **inside** the
free header block and moves the split 4 → 3 rather than collapsing it, so *in-block* does not mean
*collapsing*. The implication runs one way only, and it is the way arm B needs: **collapsing ⇒
in-block.**

## 8. Falsification

Per CLAUDE.md § Plan authoring discipline rule 4, each of the three new pins in
`tests/test_split_sensitivity_instrument.py` was inverted and shown to fail before it shipped. The
inversions are at the single site that carries the abstention into the evidence graph,
`src/iladub/etkl/headers.py:111-112`.

**Inversion A — the abstention is ignored** (`unshown=()` instead of `unshown=band.unshown`):

```
FAILED ...::test_abstaining_the_column_LABEL_alone_collapses_the_split_to_the_floor
FAILED ...::test_split_parts_reports_the_AXIOM_branch_and_agrees_with_the_function
FAILED ...::test_the_RETURNED_split_is_a_circular_scope_it_excludes_its_own_collapsing_address
FAILED ...::test_a_collapsed_split_is_a_FIXED_POINT_no_further_address_moves_it
4 failed, 4 passed
```

**Inversion B — the recomputation is never abstention-free** (`unshown=((1, 1),)` unconditionally,
so the free reference cannot recover the pre-collapse block):

```
FAILED ...::test_the_fixture_puts_the_split_below_the_label_row
FAILED ...::test_a_BODY_address_of_the_same_column_does_not_move_it
FAILED ...::test_split_parts_reports_the_AXIOM_branch_and_agrees_with_the_function
FAILED ...::test_the_RETURNED_split_is_a_circular_scope_it_excludes_its_own_collapsing_address
FAILED ...::test_the_ABSTENTION_FREE_split_is_a_non_circular_scope_and_contains_the_address
5 failed, 3 passed
```

Restored, `8 passed`. **A first attempt at inversion B was a phantom** — it wrote
`((1,1),) if band.unshown else band.unshown`, which leaves the `unshown=()` path untouched and so
left the abstention-free test green while failing an unrelated one. An inversion that fails *some*
test is not an inversion of *this* test; the named test has to be in the failure list.
