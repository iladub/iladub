# Evidence — the R234 lockout has a population of ZERO among natural bands

**Serves:** prog:criterion:etkl:04 — ONS. [[R234]] is the criterion's named blocker, and this
measures whether the blocker is a class or a single specimen.

**Date:** 2026-09-15. **Tree:** branch `r234-lockout-population`, cut from `main` at `024fd0d`.
**No shipped file was edited. No behaviour changed.** Measurement only.

**Doc impact: none.**

The ordered action was `2026-09-15-repair-plan-next-loop-handoff.md` § 5b, typed **PROPOSED** by
its author with an explicit warning that it might be the wrong instrument. It was run as ordered,
after the proxy question the order raised was settled first (§ 1).

**The answer: R234's signature fires on ZERO natural bands corpus-wide.** Its founding case is
reachable only through a cut the maintainer has already refused to build.

---

## 1. The proxy — settled BEFORE the instrument was written, as § 5b ordered

§ 5b proposed counting bands whose `header_rows_of` returns *"fewer rows than the band's boxhead
actually occupies"*, and warned in the same breath that **"the boxhead's actual extent" is not a
quantity the code computes — it is the very thing in dispute**, so any proxy for it risks the
circularity [[R235]]'s v1 census committed.

**That phrasing was NOT used.** The instrument asks only questions the shipped code already
answers on its own terms:

- **(a) is the NEURAL branch gated shut?** — `classify_hierarchical` returns a `HierRegion` and
  `merge_tiling_ok(tree, grid)` is `True`, so `compile.py:1277`'s `not merge_tiling_ok(...)` is
  False and `rowrole.build_row_reading` is never entered.
- **(b) did the gap test alone refuse a structural wrap?** — `group_wrapped` sees ≥ 1 consecutive
  pair that is a wrap candidate on the structural conditions, declined only because
  `gap < tightest_row_gap` is false.

**Why this is not question-begging:** neither leg consults an author's intent, a human reading, or
any ground truth about where the boxhead ends. Leg (b) reuses `group_wrapped`'s **own** predicates
rather than approximating them — its conditions 2 and 3 are together exactly
`_partial_of(prev, cur)` (`cells.py:207`), and the CERTAIN pairs whose minimum sets the threshold
are exactly that predicate's complement plus the hrule veto (`cells.py:210`). **No new threshold,
tolerance or constant enters the instrument.**

## 2. The control — required, and it PASSED

An instrument that cannot re-find its own founding case is low-power, and [[R235]]'s v1 census is
this repo's measured counter-example. The control re-runs the signature on ons p4 band 0 cut
`(L,T)=(2,1)` and demands R234's figures back:

```
=== CONTROL: ons p4 band 0 cut (L,T)=(2,1) -- R234's founding case
    state=in-scope nlines=29 words=213 merge_tiling_ok=True
    tightest_row_gap=12.00 lead=20.64 n_certain=27
    [ok  ] state is in-scope
    [ok  ] merge_tiling_ok is True
    [ok  ] >=1 gap-refused wrap candidate
    [ok  ] refusal at EXACT equality
    [ok  ] tightest_row_gap == 12.00
    [ok  ] signature fires (locked out)
    CONTROL PASSED -- the instrument re-finds R234. Sweep is trustworthy.
```

The control band is a **cut** band, so it is unreachable by the natural-band sweep; it is run
explicitly and reported separately. `tightest_row_gap=12.00`, `n_certain=27` and the
exact-equality refusal all reproduce R234's evidence § 5 independently.

## 3. The sweep — 191 bands, 7 documents

```
               bands = 191
             ncols<2 = 99          out of scope: classify_hierarchical returns None
       no-hierregion = 43          out of scope: a maker stage returned None
            in-scope = 49
           tiling-ok = 47          the NEURAL branch is gated SHUT
         tiling-fail = 2           the NEURAL branch is OPEN (correct behaviour)
          locked_out = 9           BROAD leg: any gap-refused candidate
    locked_out_at_EXACT_equality = 0      <-- R234's ACTUAL signature
          with_cands = 11
         neural_open = 1
```

**`locked_out_at_EXACT_equality = 0`.** No natural band in the corpus reproduces the
`12.00 < 12.00` refusal that R234 names.

## 4. The 9 broad hits are THREE different things, and full precision is what separates them

The broad leg (`gap >= tightest`) conflates a wrap the AXIOM could not distinguish from a row with
a candidate that plainly *is* a row. At 2 decimal places **8 of the 9 print a margin of `0.0`**,
which is what made the first reading of this sweep wrong. At full precision:

| band | refused pairs | margin (gap − tightest) | what it is |
| --- | --- | --- | --- |
| graincorp-stem p0 b2 | 14, 45 | 3.53e-05, 2.33e-05 | [[R208]] § 4(b) residual |
| graincorp-stem p1 b1 | 4, 26, 40, 51, 61, 74, 78 | 2.33e-05 … 4.65e-05 | [[R208]] § 4(b) residual |
| graincorp-stem p2 b1 | 4, 8, 13, 25, 39, 58 | 2.33e-05 … 4.65e-05 | [[R208]] § 4(b) residual |
| ons p7 b12 | 2, 14 | 3.84e-04, 3.84e-04 | sub-precision, one order wider |
| ons p7 b14 | 4, 16 | 5.80e-04, **3.60e-01** | one sub-precision, one genuine row |
| ons p8 b4 | 4, 16 | 8.88e-04, 8.88e-04 | sub-precision |
| ons p8 b5 | 4, 16 | 4.80e-04, 4.80e-04 | sub-precision |
| ons p8 b7 | 3, 15 | 4.80e-04, 4.80e-04 | sub-precision |
| bfs p5 b2 | 2 | **9.35e-01** | genuine row boundary |

graincorp's cluster matches [[R208]] spec § 4(b) — *"the margin is 2.3e-5 pt (candidates ≥
6.479988, certain minimum 6.479965)"* — to four significant figures. **None is at zero.**

**No cutoff is applied to this table.** A threshold separating "sub-precision" from "real" would be
exactly the tuned constant CLAUDE.md § 8 forbids; the instrument prints margins at full precision
and the classification above is made in prose, by a reader, and is falsifiable by re-reading the
column.

## 5. The instrument is VALIDATED against R208's shipped probe

Agreement was checked against `scripts/at_pitch_weld_probe.py` — R208's own instrument, which
reads the page exactly as `group_wrapped` does — on the current corpus bytes:

```
$ .venv/bin/python scripts/at_pitch_weld_probe.py corpus/ag-trade/graincorp-stem-2026-07-31.pdf 1 1
band 1 on page 1: 80 lines, 17 columns, 101 hrule ys, lead=6.480010499999935,
                  certain pairs=72, tightest_row_gap=6.479964750000022
  line  3->4 : gap-tightest=+3.52e-05   ...  candidates 7, welded by gap<tightest_row_gap 0
  line 25->26: gap-tightest=+2.32e-05
  line 39->40: gap-tightest=+4.57e-05
  line 50->51: gap-tightest=+2.33e-05
  line 60->61: gap-tightest=+4.65e-05
  line 73->74: gap-tightest=+4.65e-05
  line 77->78: gap-tightest=+4.65e-05
```

Pair for pair and margin for margin, identical to this census's
`{4: 3.525e-05, 26: 2.325e-05, 40: 4.575e-05, 51: 2.325e-05, 61: 4.650e-05, 74: 4.650e-05,
78: 4.650e-05}`. Likewise on `ons 7 12`: the probe reports 2 candidates at `+3.84e-04`, this
census `{2: 3.840e-04, 14: 3.840e-04}`.

**A side finding, recorded because it is about published evidence.** [[R208]] spec § 7's table
claims to list *"every page, every band with ≥ 1 candidate"* over the corpus, and lists 11 bands —
**no ons p7 or p8 band among them**, though its own shipped probe reports candidates on ons p7 b12
(above). So § 7's table is **incomplete**, and the "**30** candidates" denominator § 4(a) rests on
is understated. **§ 4(a)'s CONCLUSION is unaffected**: its claim is that 0 candidates lie in
`[tightest_row_gap, lead)`, and ons p7 b12's `gap - lead = +5.68e-14` places it at or above `lead`,
outside that interval. Wrong citation, right conclusion — [[R235]]'s pattern exactly. Not raised as
a new row: § 7 is Evidence and append-only, and the claim it supports still stands.

## 6. What this measurement means for the remedy — and what it does NOT decide

**It does not classify the remedy.** Which module the fix belongs in and which CLAUDE.md § 8 class
it is remains the maintainer's decision, deliberately withheld by [[R234]]'s row, by its handoff
§ 5a, and by this document. A loop may not make it on its own evidence.

What the measurement *constrains*:

- **The lockout is not a corpus-wide class.** It is a population of **zero** natural bands. Any
  remedy is justified by one specimen, on one page, of one document.
- **That specimen is reachable only through a refused cut.** The `(2,1)` cut that produces it is
  furniture-peeling territory, and [[R232]]'s walk was **ruled not to be built** (maintainer,
  2026-09-15). Nothing in the shipped pipeline produces the control band today.
- **The gap test must still not be loosened.** Inherited unchanged from R234's evidence § 5:
  `<` → `<=` re-admits the at-pitch fusions [[R208]] exists to refuse, and the three graincorp
  bands above are precisely that population, live, at 2.3e-05 pt.
- **The NEURAL branch does open where tiling genuinely fails** (`tiling-fail = 2`,
  `neural_open = 1`). The lockout is specific to trees that are self-consistently wrong, not a
  general unreachability of `rowrole`.

## 7. What this loop does NOT claim

- **It does not claim R234 should be closed, parked, or built.** It measured a population; the
  disposition is a maintainer's.
- **It does not re-derive any document-scope score.** No compile was run; every figure here is
  band-scoped, from the shipped functions named in § 1.
- **"Zero at exact equality" is a statement about THIS corpus**, seven documents, 191 bands —
  absence on this corpus, not evidence of absence, the same limit [[R208]] § 4(a) states about
  its own null.
- **It does not explain `superseded`**, still unexplained since two loops ago and still listed
  unverified.
- **The three-way classification in § 4 is a reading**, not a computed verdict. The margins are
  computed; calling `2.3e-05` sub-precision and `9.35e-01` a row is prose, and the table prints the
  numbers so a later reader can disagree.

## 8. Reproduce

```
PYTHONPATH=. .venv/bin/python scripts/r234_lockout_census.py
```

Exits non-zero if the control fails. `scripts/r234_lockout_census.py` is committed with this
evidence; it carries its control inline and no tuned constant.
