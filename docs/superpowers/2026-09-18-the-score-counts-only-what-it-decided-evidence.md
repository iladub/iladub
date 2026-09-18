# Evidence — ons did not regress, and the score counts only the ink it decided about

**Serves:** prog:criterion:etkl:04 — ons-index-of-services.

**Date:** 2026-09-18. **Branch:** `the-reader-answers-the-scope`.

**Doc impact: none.**

---

## 1. The claim this refutes

The corpus gauge shows `ons 0.77▼`, down from 0.9720 on 2026-09-05 — read all day as *a document
we made worse*, and named as such when the maintainer asked for compiling success as the
benchmark.

**It is not a regression.** Bisected over the window (isolated worktree, corpus symlinked because
`corpus/` is gitignored):

```
134e26e  ons=0.9720     4e5ef50  ons=0.9720     10b09c5  ons=0.9720     523e00b  ons=0.9720
d588412  ons=0.7712     8d6d20d  ons=0.7712     debc004  ons=0.7712     91430d2  ons=0.7712
```

`d588412` — R225's resolution test — is the boundary. And the per-region diff across it says what
actually happened:

```
before: 73 regions, asserted ink 590, escalated ink  17, score 0.9720
after : 75 regions, asserted ink 590, escalated ink 175, score 0.7712
```

**Asserted ink is identical, 590 on both sides.** Nothing stopped being read. 16 regions changed,
every one of them from `ignored / "fewer than 2 columns"` — which books **no ink at all** — to
`escalated` or `superseded`, which book ink in the denominator. The resolution test made those
bands resolve into columns, so the pipeline began to *decide about* ink it had previously passed
over in silence.

The score did not fall because the compile got worse. It fell because the accounting got honest.

## 2. The hole, measured

`document.py`: `score = asserted / (asserted + escalated)`. **Ignored ink is in neither term.** A
band the pipeline declines to look at costs nothing, so *ignoring more of the page raises the
score*.

Words on the page (`extract_words` summed over every page) against what the score's universe
contains:

| document | ink on page | asserted | escalated | never counted | published score | carried (asserted / page ink) |
| --- | --- | --- | --- | --- | --- | --- |
| ons | 2520 | 590 | 175 | **1755 — 70%** | 0.7712 | **0.2341** |
| graincorp-capacity | 516 | 406 | 0 | 110 — 21% | **1.0000** | 0.7868 |

**The caveat, stated before the figure is used for anything.** `carried` is not a target and must
not be read as one. Running heads, page numbers, footnotes and prose are legitimately not table
data, and on gcap the 110 uncounted words are **exactly** the `tab:UnshownInk` cells this same
branch taught the pipeline not to assert as values — correct behaviour that this ratio penalises.
`carried` is comparable to ITSELF across commits, as a trend; it is not a grade.

What it does establish, and what the published score cannot: **on ons, 70% of the document is
outside the score's universe entirely.** A figure of 0.77 over 30% of a page is not a statement
about the document.

## 3. What this means for the four unaccepted documents

ons is not a document to repair back to 0.97 — that number was the pipeline looking at less. Its
real compiling gap is small and nameable: **6 live escalations**, 4 `KIND_NOT_SUPPORTED` (p0 r1,
p7 r0, p7 r3, p8 r2) and 2 `DATAGRID_RESIDUE` (p7 r17, p8 r10), carrying 175 tokens between them.
Those four KIND_NOT_SUPPORTED regions are precisely the bands the resolution test newly resolved
into columns: the pipeline now sees them as tables and cannot read them. That is a reading gap on
a real document, which is the kind of work that moves `etkl` 3/7 → 4/7.

## 4. Falsification

- **The bisect is a bisect**, not a reading: eight compiles, four either side, all at 46s, the
  boundary commit's `src/` diff inspected (`compile.py` only, +58/-4, the resolution test).
- **The identical 590** is the control. Had asserted ink moved, the regression reading would have
  stood; it did not move by one token.
- The `extract_words` figure was wrong on its first run (72 words — the function is per-page and
  was called without a page loop) and produced an absurd 1062% before it was corrected. The
  absurdity is what caught it.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
