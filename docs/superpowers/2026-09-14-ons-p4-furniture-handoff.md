# Handoff — ONS p4's table is lost to furniture at BOTH ends, and adoption can never reach it

**Topic:** [[R230]]'s cause is restated by measurement. Both remedies its row names are **refuted**,
and the page's other apparent escape route — document-scope adoption — is closed to it *by
construction*, not by a gate that could be widened.

**Serves:** prog:criterion:etkl:04 — ONS. The criterion's subject is column identity
([[etkl-04-not-contractable]]), and p4 is the only ONS page whose table prints column labels at all.

**Date:** 2026-09-14. **Tree:** `main` at `06d447c`, clean; PR #223 (R230/R231's raise) auto-merge
queued, CI pending at the time of writing. **No code was written this session.**

**Doc impact: none.** No released term, no vocabulary, shape, contract or instrument touched.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is typed
assertion-or-proposition. The spec was **deferred at the floor, deliberately**: `plimslop preflight
--shape originating --tokens 85000` returned *"over the 50,000 floor, defer"*, and it is logged.

---

## 5. The next concrete action

### 5a. ASSERTED — the repair site is band construction, the peel must be TWO-ENDED, and the evidence for where to cut already ships

Mechanical in the sense that matters: the outcome is known and doing it *is* the work.

R230 says p4's principal 25×6 table is discarded because of **caption contamination** in a
rules-free band, and names two candidate remedies — *(a)* a peel that does not require drawn rules,
or *(b)* a gutter profile that tolerates full-width lines. **Measured on `main` at `06d447c`, every
call at the STOCK `gutter_pct=0.98`:**

```
band 0 = 32 lines, 0 drawn rules      infer_leaf_grid -> ncols
  full band                             1    [41.8, 547.9]
  drop the trailing Source line only    1    [43.9, 547.9]
  drop the 6 leading caption/hdr lines  3    [41.8, 374.8, 435.8, 486.8]
  drop BOTH  (lines[6:-1], 25 rows)     6    [43.9, 108.4, 178.9, 263.9, 349.9, 435.9, 486.8]
```

**Arm (a) is necessary but NOT sufficient**, and arm (b) is **refuted outright**: the docstring's own
prescribed move — *"ncols too low (columns merged): lower gutter_pct (e.g. 0.95)"* — gives
`ncols=2` on the full band at 0.96, not 6. Lowering the constant is not merely forbidden by § 8; on
this page it does not even work.

The trailing line is **not a caption**. It is
`Source: Index of Services estimate from the Office for National Statistics`, prose furniture
*below* the data rows, and `peel_leading_captions` refuses trailing lines **by design** — its
docstring records that peeling them swallowed page-local subtotal rows and broke
`test_continuation_licence` / `test_logical_arithmetic`. So the repair is not "relax the peel"; it
is a **second, trailing** furniture rule that cannot reuse the leading one's licence.

**Why the profile dies on one line:** at `gutter_pct=0.98` over 25 rows, a gutter must be blank on
≥ 24.5 of them — ink on a *single* row closes it. The five true gutters are 39–70 bins wide and read
0.96. This is a threshold that admits zero exceptions, not a tolerance that is slightly mis-tuned.

**And the evidence for where to cut ALREADY SHIPS, with no new constant.** `derive_data_grid(P, 4)`
reads the same page as `rows=(6 … 30)`, 6 columns, `universe='alignment'`, conforming to
`ColumnHomogeneity, NonDegeneracy, RowAddressability, ColumnAlignment, SeedFollowsUniverse,
AggregateWitness`, and it **refuses exactly the furniture**: rows 0–5 and 31–36 `unplaceable`, rows
33–34 `HeterogeneousColumn/every-measure`. The admitted set `6 … 30` is *precisely* the line slice
`lines[6:-1]` that yields the correct six columns above, and its column x's agree with the profile's
to within 0.5pt:

```
derive_data_grid  43.92  108.57  179.32  263.80  349.85  435.89  486.82
infer_leaf_grid   43.9   108.4   178.9   263.9   349.9   435.9   486.8
```

**So the next loop's subject is: a two-ended furniture peel for RULES-FREE bands, disposed by the
alignment universe rather than by a new geometric rule.** Two mechanisms already agree on this page
once the furniture is gone; one of them already knows which lines the furniture is. That is an
AXIOM/NEURAL shape under § 8, and it carries no tuned constant — which the alternatives do not.

### 5b. ASSERTED — adoption is closed to p4 by construction; do not spend a loop widening it

`vocab/queries/adoption-candidate.rq` is an `ASK` requiring a `iladub:CandidateConcept` with
`prov:wasDerivedFrom ?doc` and `iladub:fromRegion`/`iladub:onPage ?page`. Measured at page scope:

```
p4: asserted=19  escalated=17  CandidateConcepts=0   -> ASK has nothing to match; gate CLOSED
p7: asserted=112 escalated=216 CandidateConcepts=5   -> is_adoption_candidate(...) True
```

p4 escalates 17 tokens **while minting no candidate at all**, so the pre-filter is false and the
costly branch behind it never runs. Document scope agrees and is the honest confirmation:
`compile_document` returns `adopted=(7, 8)`, score `0.7712418300653595`, p4's regions unchanged at
`[ignored, ignored, asserted 19, ignored]`, and the run's **only** note names *page 0* — p4 produces
no refusal note whatever, because it is never a candidate to refuse.

This matters because R225's D2 widened adoption's *downstream* comparison (unread ink) on
2026-09-14, and the obvious next thought is to widen it further. **It cannot reach p4 by any amount
of widening**: the pre-filter runs first and answers on candidate existence alone.

### 5c. PROPOSED — "escalates ink, mints no candidate" may be a residue of its own

**Rests on a prediction that must be RUN, and it may fail.** p4 accrues 17 escalated tokens with 0
`CandidateConcept`s. That is the *same mechanism* the cbh-stem HOLD rationale already names
(`tests/corpus-manifest.ttl`, § Seam 1: *"86 tokens sit inside asserted regions and mint no
record — `compile.py:960` accrues `escalated_total` on a path that makes no `escalate_region`
call"*), and its second-order consequence is what 5b measures: such a page is **structurally
invisible to the adoption gate**.

Whether that is a defect or a correct convention is **unmeasured**, and I decline to call it either.
The honest alternative is that these tokens belong to *ignored* bands whose free-text classification
reason was never an escalation in the first place, in which case minting no candidate is right and
the only defect is that `escalated_total` counts them.

**Cheap to settle, and it must be run before a row is raised on it:** census
`escalated_total > 0 and CandidateConcepts == 0` per page across all seven corpus documents. If p4
is the only instance, this is a footnote on R230; if it is widespread, it is a row, and it bears on
every document's adoption reach rather than on ONS.

### 5d. ASSERTED — what this session must NOT be read as having done

No code, no spec, no contract, no instrument. The peel is **unbuilt**. [[R231]] is untouched.
Whether a two-ended peel moves any of the other six documents is **entirely unmeasured** — this
session measured one page of one document. [[R226]] (no leaf header block on any ONS page) is
untouched and still stands between a repaired p4 and a contract, because recovering six *columns*
is not yet recovering six column *labels*.

---

## 1. Where the primaries are

- **The row** — [[R230]] in `residues-open.md`, amended by this loop with the refutation above.
  Its original prose still states caption contamination as the cause; the `✎` amendment is what
  supersedes it. Read both.
- **The site** — `infer_leaf_grid` (`src/iladub/etkl/grid.py`, find it by
  `grep -n "def infer_leaf_grid" src/iladub/etkl/grid.py` — a grep, not a line number, per plan
  rule 7) and `_column_blank_profile` above it. The classification that ignores the band is
  `regions.py`'s `"fewer than 2 columns"`.
- **The peel that refuses to help** — `peel_leading_captions` in `src/iladub/etkl/gridregion.py`;
  its docstring carries the measured reason trailing lines are never peeled.
- **The mechanism that already reads the page** — `derive_data_grid` in
  `src/iladub/etkl/datagrid.py`.
- **The gate that excludes p4** — `vocab/queries/adoption-candidate.rq` + `is_adoption_candidate`
  in `src/iladub/etkl/adoption.py`.
- **The recorded § 8 classification** — `docs/wiki/concepts/neurosymbolic-exemplars.md` calls
  `infer_leaf_grid`/`_word_in_column` "justified PROCEDURAL geometry" (loop B2c). **That
  justification is worth re-reading against 5a**: a PROCEDURAL step must state why it is
  irreducible, and this one ships a docstring inviting the reader to tune two constants.

**Reproducing the table in 5a** (the whole measurement is four calls, no fixture needed):

```python
import dataclasses
from iladub.etkl.compile import page_bands
from iladub.etkl.grid import infer_leaf_grid
P = "corpus/gov-stats/ons-index-of-services-2026-02.pdf"
b0 = page_bands(P, 4)[0]; L = list(b0.lines)
for name, lines in [("full", L), ("no-source", L[:-1]), ("no-captions", L[6:]), ("both", L[6:-1])]:
    print(name, infer_leaf_grid(dataclasses.replace(b0, lines=tuple(lines))).ncols)
```

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| R230's cause is furniture at BOTH ends, not caption contamination | [[R230]]'s `✎` amendment; this file § 5a |
| Both remedies R230 named are refuted (one insufficient, one ineffective) | same |
| The peel's disposal should be the alignment universe, not a new geometric rule | this file § 5a only — **nothing else records it**, and it is a design proposition a spec must argue, not inherit |
| Adoption is not the route to p4, and widening it cannot become one | this file § 5b; [[R230]]'s amendment |
| The spec was deferred at the context floor rather than written late | `plimslop` pre-flight log, this session |

## 3. Unverified or assumed

- **5c entirely**, per its grading.
- **The per-gutter "intruding words" counts are partly a PROBE ARTIFACT and are not relied on
  anywhere above.** That probe took each gutter's window from *row 0's* word extents, but negative
  values (`-0.1`) are wider than positive ones and extend past row 0's right edge, so words counted
  as "intruding" on gutters 0, 3 and 4 are in fact inside their own columns. The decisive evidence
  is the drop-both experiment, which needs no window at all. Gutters 1 and 2 are the ones the
  `Source:` line genuinely closes.
- **Whether the six recovered columns would survive the rest of the pipeline is unmeasured.** 5a
  measures `infer_leaf_grid` in isolation; it does **not** show that a peeled band classifies as a
  table, emits cells, or changes p4's verdict. Nothing here ran a modified compile.
- **The other six corpus documents were not touched.** A two-ended peel is exactly the shape that
  regressed `test_continuation_licence` / `test_logical_arithmetic` once before (see the
  `peel_leading_captions` docstring), so the next loop's first obligation is that pair, not p4.
- **`page_bands`' line indices are assumed to correspond to `derive_data_grid`'s row indices**
  because the slice `lines[6:-1]` and the admitted set `rows=(6…30)` coincide exactly. That
  coincidence is strong evidence but is **not** a proof that the two index spaces are the same
  space; a spec relying on it must measure it, not inherit it from here.

## 4. What this session did

Read the register and the two prior handoffs, found PR #223's newly-raised [[R230]] naming ONS p4 —
the one ONS page that prints column labels, and therefore the one that bears on etkl:04's actual
subject — and **attacked its stated cause instead of building on it.** Both of the row's proposed
remedies fell: the caption peel recovers 3 of 6 columns, and lowering the constant the docstring
points at recovers 2. The real cause is a conjunction the row did not see, and the page's other
apparent route was closed by a one-line `ASK` rather than by anything adjustable.

**Worth carrying, because it is the technique and not the result.** The row was written by the
session that *found* the defect, hours earlier, and it was wrong about the cause while being right
about the symptom. Its remedy column would have sent this loop to build a rules-free leading peel,
ship it, and recover **three columns of six** — a change that passes its own test, moves the score,
and leaves the table still misread. What separated them was four calls to a function that was
already installed. **Measure the row's cause before you build its remedy, even when the row is one
commit old and you wrote it yourself.**
