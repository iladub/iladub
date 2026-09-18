# Evidence — the split does move, and the document it was never measured on is the one that cannot move it

**Serves:** maintenance — [[R255]] is named by no `prog:blockedBy`, and neither is the row this
loop raises. Declared `maintenance` deliberately, per [[R257]]: the previous thread's five loops
declared `prog:criterion:etkl:02`, which has carried `prog:met true` since 2026-09-13.

**Date:** 2026-09-18. **Branch:** `r255-does-the-split-move`, cut from `main` at `4db5f50`.

**Doc impact: none.**

**Subject.** The previous loop's handoff § 5a: *instrument the two readings and see whether they
disagree*, because [[R255]]'s amendment recorded that the two readings moving the header/body
split was **"a mechanism, never an observed effect"**. This loop answers that question, and
answers it OFFLINE and exhaustively rather than by one live sample — see § 1 for why that is the
stronger instrument and not the cheaper one.

---

## 1. Why the asserted action was run offline, and what that bought

§ 5a prescribed a live compile with a print at both `page_bands` call sites. Run as written it
would have produced **one sample** of a reader measured to give three different answers to one
crop ([[R253]]; 2026-09-18 grain-of-the-ask evidence § 7, nine readings of one band). A negative
result from it — the split did not move — would have been indistinguishable from the reader
happening to agree with itself twice.

The offline route is available because of a fact the disposal already states.
`unshownink.dispose` returns `reading.empty_cells & has_glyph` (`src/iladub/etkl/unshownink.py:176`),
so **every admissible reading is a subset of the band's glyph-bearing addresses.** No reader,
however wrong, can put any other address into `Band.unshown`. That makes the space of possible
readings a finite lattice with a known floor and ceiling, and the question *"can a reading move
the split"* answerable by perturbation rather than by sampling.

The instrument is `scripts/unshown_ink_split_sensitivity.py`. Per gridded band it computes the
split under the empty set (the shipped offline value), under the full glyph set (the ceiling), and
under **every single-address set in between** — the realistic grain, because the two live readings
gcap's traced compiles took differed by ONE address (110 vs 109).

It reports the AXIOM's own scalar and the returned value **apart**, because abstention can push a
column out of `header-body-split.rq`'s MIN entirely (`s_col = -1` when a column has no
non-abstaining body cell) and hand the answer to `_hrule_split`, the PROCEDURAL fallback. A single
number cannot tell a moved split from a silenced AXIOM.

## 2. THE FINDING — on cbh-stem, one address in the header row erases the header

```
$ ./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --band cbh-stem 0 1
cbh-stem-2026-08-03.pdf page 0 band 1 — 18 x 16, 151 glyph-bearing addresses
  unshown = ()            axiom/final =    7/   7
  unshown = every address axiom/final = None/   1
  7 single addresses move the returned split on their own:
    (6, 0)     axiom/final =    1/   1   text='VNA #'
    (6, 3)     axiom/final =    1/   1   text='Date Nominated'
    (6, 8)     axiom/final =    1/   1   text='ETD'
    (6, 9)     axiom/final =    1/   1   text='Volume'
    (6, 10)    axiom/final =    1/   1   text='+/- %'
    (7, 5)     axiom/final =    6/   6   text='Accepted'
    (7, 14)    axiom/final =    6/   6   text='Completed'
```

**Every mover is a column LABEL.** Five of the seven do not shift the split by a row — they
collapse it to **1, the floor the derivation can return**: the band's header falls from seven
lines to one, and six header lines are read as body. (The remaining two move it 7 → 6.) The
mechanism is not cbh arithmetic: a label is Text over a numeric column, so it is the MAX mismatch
row that sets `s_col`; abstain it and the column is homogeneous from row 1 down, `s_col = 1`, and
the outer MIN takes it.

The same shape on all four of cbh's 16-column bands, from the corpus sweep:

```
document                           pg  b rows x cols   ink      none      full movers
                                                  axiom/fin axiom/fin
cbh-stem-2026-08-03.pdf             0  1   18 x 16     151    7/   7 None/   1      7
cbh-stem-2026-08-03.pdf             0  3   21 x 16     222    4/   4 None/   1      7
cbh-stem-2026-08-03.pdf             0  5   20 x 16     191    5/   5 None/   1      5
cbh-stem-2026-08-03.pdf             0  7   10 x 16      82    4/   4 None/   1      6
graincorp-capacity-2026-08-04.pdf   0  3   27 x 16     406    1/   1 None/   1      0
```

So **R255's coherence half is no longer a mechanism.** Two readings of cbh band 1 differing by the
single address `(6, 9)` — the exact grain by which gcap's two traced readings differed — produce
splits of 7 and 1. The recognized band and the compiled table would then be two different tables,
which is the failure `page_bands`' own docstring says it exists to prevent
(`src/iladub/etkl/compile.py:381-384`).

## 3. Why no run had ever shown it: the traced document is the immune one

**graincorp-capacity band 3 is insensitive, and not by luck.** Its split is already **1**, the
floor — and of its 406 glyph-bearing addresses, **0** move it, full abstention included. Its 110
unshown addresses are the hidden zeros, and they are all in the BODY; a body cell's abstention
leaves the label row still voting, so `s_col` does not change.

Every live trace in this thread was taken on that document. The previous loop's *"no run has shown
the split moving"* was therefore **true and uninformative**: it measured the one corpus document
where no reading can move it. This is the same shape as R213's own O3 null, which its plan already
required be reported as holding *by construction rather than by prediction* — a null on a specimen
that cannot exhibit the effect is not evidence about the effect.

## 4. The population is the one the reader is asked about — total containment

The movers would be a curiosity if the reader were never going to touch those cells. It is asked
about exactly them.

```
$ ./.venv/bin/python scripts/unshown_ink_split_sensitivity.py --contrast

== cbh-stem-2026-08-03.pdf page 0, contrast < 3.0
   band  1  18 x 16  low-contrast addresses  20   axiom/final    7/   7 ->    1/   1   MOVED
   band  3  21 x 16  low-contrast addresses  20   axiom/final    4/   4 ->    1/   1   MOVED
   band  5  20 x 16  low-contrast addresses  20   axiom/final    5/   5 ->    1/   1   MOVED
   band  7  10 x 16  low-contrast addresses  20   axiom/final    4/   4 ->    1/   1   MOVED
   band  9  10 x 3   low-contrast addresses   8   axiom/final None/   1 -> None/   1   same

== graincorp-capacity-2026-08-04.pdf page 0, contrast < 1.5
   band  3  27 x 16  low-contrast addresses 110   axiom/final    1/   1 ->    1/   1   same
```

And the containment is total, not partial — measured per band, movers ⊆ low-contrast addresses:

| band | movers | low-contrast | movers ∖ low-contrast |
| --- | --- | --- | --- |
| cbh band 1 | 7 | 20 | **0** |
| cbh band 3 | 7 | 20 | **0** |
| cbh band 5 | 5 | 20 | **0** |
| cbh band 7 | 6 | 20 | **0** |

**Every address that can move cbh's split is inside the population R213's own evidence calls the
hardest to judge.** cbh's header labels are the white-on-grey set at ratio 2.9601 — below WCAG's
3.0 large-text minimum — which is precisely why that document was chosen as the discriminator's
control in the first place.

**What this is NOT.** It is not a claim that the live reader returns that set. `dispose` refuses
cbh's regions outright today (refusal 2: two independent blind readers rejected the supplied
18 × 16 grid), so **no live reading of these bands exists at all**, and the `< 3.0` bracket is a
census bracket, never a decision rule. The claim is the bound in the direction that matters: the
cells hardest to judge are sufficient, taken together, to erase the header on four bands.

## 5. What was already pinned, and was not looked at

`tests/etkl/test_unshown_ink.py:83` —
`test_an_unshown_cell_does_not_vote_in_the_homogeneity_judgement` — has asserted since R213 shipped
that an unshown cell moves the split to 1. **The effect the previous loop called unobserved was
pinned by a green test in this repo's own suite**, on a synthetic body cell holding the word
"closed".

What that test does not say, and what § 2 adds, is *where the movers are on a real document* and
*how far the split travels*: not a shift by one, but a collapse to the floor, and the addresses
that do it are the header's own labels rather than an anomalous body cell.

## 6. The obvious remedy arm is refuted, and refuted by its own definition

The first remedy anyone reaches for is *scope the abstention to BODY rows* — let an unshown
address type only where it cannot touch the label row. Priced before it was proposed:

```
== cbh-stem-2026-08-03.pdf (contrast < 3.0)
   band  1: split= 7  addresses  20 =  16 header-row +   4 body-row   body-scoped split: 6  MOVED
   band  3: split= 4  addresses  20 =  16 header-row +   4 body-row   body-scoped split: 3  MOVED
   band  5: split= 5  addresses  20 =  16 header-row +   4 body-row   body-scoped split: 4  MOVED
   band  7: split= 4  addresses  20 =  16 header-row +   4 body-row   body-scoped split: 3  MOVED
   band  9: split= 1  addresses   8 =   0 header-row +   8 body-row   body-scoped split: 1  HELD

== graincorp-capacity-2026-08-04.pdf (contrast < 1.5)
   band  3: split= 1  addresses 110 =   4 header-row + 106 body-row   body-scoped split: 1  HELD
```

**It does not hold the split**, and the reason is structural rather than a matter of degree: *which
rows are body* is defined BY the split the scope is meant to protect. The surviving movers are the
addresses sitting on the first body row — `(7, 5) 'Accepted'` and `(7, 14) 'Completed'` on band 1 —
which are body rows by construction and still move it 7 → 6. A scope cannot protect a boundary it
is measured from.

graincorp-capacity holds either way, which is the same immunity § 3 explains and not evidence for
the arm.

## 7. What ships

- `scripts/unshown_ink_split_sensitivity.py` — the instrument, three modes, every figure above
  re-runnable by the command printed with it.
- `tests/test_split_sensitivity_instrument.py` — five tests. The corpus is fetched and never
  committed (`.gitignore:52`), so the § 2 figures cannot be pinned in CI; what is pinned is the
  MECHANISM on a fixture that states its geometry in full (a label row over a numeric column, the
  label abstaining, the split collapsing to 1), its control (the split is 2 before), its null (a
  BODY address of the same column moves nothing — the cbh/graincorp difference in one assertion),
  and the instrument's non-drift from `header_body_split` on both branches.

### FALSIFICATION

The subject is `celltype.grid_evidence`'s unshown typing (`src/iladub/etkl/celltype.py:178`).
Inverted — `TAB.UnshownInk if hidden else _cell_datatype(t)` replaced by `_cell_datatype(t)`, so
an unshown cell types as its own text and keeps voting:

```
$ ./.venv/bin/python -m pytest tests/test_split_sensitivity_instrument.py -q
>       assert axiom == 1 and final == header_body_split(replace(band, unshown=(LABEL,)), _GRID)
E       assert (2 == 1)
FAILED …::test_abstaining_the_column_LABEL_alone_collapses_the_split_to_the_floor
FAILED …::test_split_parts_reports_the_AXIOM_branch_and_agrees_with_the_function
2 failed, 3 passed in 1.68s
```

Restored (`git diff --stat src/` empty), `5 passed in 2.20s`. The control and the null survive the
inversion, as they must — they assert what does NOT move.

## 8. What is UNVERIFIED

- **That the live reader ever proposes a cbh header label.** No live reading of a cbh band exists;
  refusal 2 rejects the region before any address is disposed. § 4 is a bound, not an observation.
- **Whether abstaining a label is WRONG.** If a label's ink genuinely is not shown, a split that
  stops counting it may be the right reading. This loop measures the sensitivity; it does not rule
  on which answer is correct, and that ruling is the maintainer's.
- **The five documents after graincorp-stem in the corpus sweep** — apple, bfs, ons, who — were
  still running when this was written; § 2's corpus block is quoted from the completed rows only.
- **Every cost and frequency figure in [[R255]]'s first clause** is untouched by this loop.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
