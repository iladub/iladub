# Loop record — the grid the author drew (R201's fork resolved)

**Branch** `r201-the-grid-the-author-drew`, off `93fa7ce`. **2026-09-10.**
**Spec:** `docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md`.

**Doc impact: none.**

---

## 1. What this loop was asked to do

`docs/superpowers/2026-09-10-the-header-is-assumed-handoff.md` § 5b left [[R201]] as a **design
fork with no arm chosen** — escalate, merge, or extend the carriage seam — and said the loop's
first job was to choose, with the maintainer if it could not choose alone. It chose alone, on
measurement, and the measurement also **refuted the merge arm** on the instance R201 was raised
for.

## 2. What was measured, in order

| # | question | answer | where |
| --- | --- | --- | --- |
| 1 | does the run relation R165 shipped even reach bfs p6's header band? | **no** — its run is `3..10`; band 2 is excluded because band 3's rule-x set carries `523.26` and band 2's does not, one element out of seven | spec § 2.4 |
| 2 | what does merging the page do? | `merge_bands(2,10)` → `UNSUPPORTED_TABLE`, **2 columns**, all 222 cells destroyed | spec § 2.2 |
| 3 | why? | `_rule_boundaries(merged)` is `None`, because `merge_bands` takes `column_xs` from the first band that has any — band 2's is **empty**, so the merge is judged against band 4's inferred gutters, which band 2's header word `80 ans ou plus` straddles | spec § 2.3 |
| 4 | does a vector the whole run tiles exist? | **yes — band 2's drawn rules**, 0 straddlers on bands 2, 4, 5, 6, 8, 9 | spec § 2.4 |
| 5 | so is the merge rescuable? | **no** — bands 3 and 7 sit inside the run and straddle every candidate, because their own 3-column rule grid already cut their data row into one cell | spec § 2.4 |
| 6 | does the relation generalise? | 12 record-table bands corpus-wide, **5 with a wholly-drawn, same-ncols, tiling donor, donor unique in all 5, no false donor** | spec § 3 |
| 7 | is the "earliest donor" ordering rule load-bearing? | **no** — the `drawn` clause alone makes the donor unique (`multi = 0`) | spec § 3(b) |

## 3. Falsification

`tests/etkl/test_grid_donation_relation.py`, 4 tests, no `corpus/` required.

**Round 1 — the falsification FIRED, and the tests failed it.** The first cut had one
distractor-free fixture. Deleting the `same_ncols` clause and deleting the `wholly_drawn` clause
each left all tests **green**: the fixture pinned only tiling.

```
### F1: drop the same_ncols clause      -> 2 passed          (pinned nothing)
### F2: drop the tiling clause          -> 1 failed, 1 passed
### F3: drop the wholly_drawn clause    -> 2 passed          (pinned nothing)
```

That is CLAUDE.md § Plan authoring's defect 5 exactly — a test that passes with its subject
deleted — caught before the module shipped rather than after.

**Round 2 — after adding a drawn 2-column distractor band and constructing the inferred-boundary
band's fields, each clause reddens exactly one test:**

```
### F1: drop same_ncols   -> FAILED test_a_drawn_band_at_the_wrong_column_count_is_not_a_donor
### F2: drop tiling       -> FAILED test_a_band_whose_ink_leaves_the_drawn_columns_gets_no_donor
### F3: drop wholly_drawn -> FAILED test_a_band_whose_interior_boundaries_are_inferred_is_not_a_donor
### restored              -> 4 passed
```

**One fixture is constructed, not drawn, and it says so in the test.** A partially-ruled multi-row
band is laid out by reportlab in the *same* band as the fully-ruled one — measured while building
it, twice, at 60pt and 150pt gaps — so the page cannot express bfs p6's "author drew two of three
separators" state. The band's `column_xs` is set with `dataclasses.replace` instead, and the test
asserts the other three clauses pass on it so the refusal is attributable to `wholly_drawn` alone.

## 4. What shipped

No compiler behaviour. One instrument (`scripts/grid_agreement_census.py`), one test module
(4 tests), the spec, this record, the handoff, and three register rows ([[R203]], [[R204]],
[[R205]]) plus [[R201]] amended.
