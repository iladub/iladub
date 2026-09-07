# R172 — the cell-level diff, RUN. The reading is right; the criterion was wrong; the score is not

**Loop:** `r172-the-cell-level-diff`, 2026-09-07. Ran action **5c** of
`docs/superpowers/2026-09-06-r175-handoff.md` (typed PROPOSED there).

**Doc impact: none.**

---

## 0. What R172 asked, and what it got

R172's closure criterion, verbatim from its row:

> A diff over the two readings' `tab:EntryCell` content on apple p0 and p1 — baseline vs merged —
> showing that **every cell the previous reading asserted is present in the merged reading with the
> same text and the same column**, and naming what the additional entries are.

The diff was run. On **p1** the criterion is met exactly. On **p0** it is **REFUTED** — and the
refutation is in the merged reading's favour, because the criterion silently assumed the baseline
was ground truth and on p0 it is not.

| | apple p0 | apple p1 |
| --- | --- | --- |
| baseline entry cells | 48 | 14 |
| merged entry cells | **124** | **56** |
| LOST (baseline entry absent from merged) | **4** | **0** |
| KEPT with text or column CHANGED | **16** | **0** |
| GAINED | **80** | **42** |
| gains landing on no baseline word (invented ink) | **0** | **0** |
| gains out of an `ignored` (prose) band | **0** | **0** |

---

## 1. The instrument, and why it needed no bisect

`scripts/entry_cell_diff.py`. Both readings are produced **in one process at HEAD**:

* MERGED — `compile_tables` as it ships.
* BASELINE — `compile_tables` with `compile.merged_run_admissible` forced to refuse every run
  proposal. `page_bands` looks that function up as a plain module global (`compile.py:352`, and
  its own docstring names the late binding as O5's patch point), and
  `test_a_refused_run_leaves_the_page_byte_identical` pins that a page whose proposals are all
  refused is byte-identical to one compiled before R165. So this **is** the pre-merge reading, not
  an approximation, and the worktree-at-the-branch-base machinery the R173 bisect needed is not
  required here.

**The identity key is the ink, not the URI.** Table and cell URIs are minted per band and cannot be
compared across two partitions of the page. Every cell carries the anchor
`p{page}-{int(x0)}-{int(top)}`, and `merge_bands` concatenates already-built lines rather than
re-extracting them, so a cell's bbox is invariant across the two readings **by construction**
(`compile.py:370-393`). The anchor is recomputed from `tab:hasBBox` for entry cells *and* label
cells alike — deliberately, because a cell that is a header in one reading and an entry in the
other must collide, or the diff cannot see the demotion at all. That is precisely the case p0 turns
out to contain.

### A false result the first draft produced, and what it cost

The first draft checked a gained cell's text against the baseline band's `RegionReport.ascii` and
reported **two misses on p1** — `'(14,264)'` and `'(5,571)'` at `p1-527-672` and `p1-533-686`.
Both were artefacts of the check. `ascii` is a **width-clipped render**: it shows `(14,264` for the
word `(14,264)`. Re-keyed against the band's actual `Line.words`, both are exact matches in *text
and position*:

```
p1-527-672 [(7, '(14,264)')]
p1-533-686 [(7, '(5,571)')]
```

The instrument now indexes words, never the render, and says so in its docstring. **The render is
not the ink** — and a diff that had shipped against `ascii` would have reported a two-cell defect
in a reading that has none.

---

## 2. apple p1 — the criterion met, and `escalated=0` is honest

**LOST 0. CHANGED 0. GAINED 42**, every one landing on a real baseline word with **identical text**,
every one out of a band that **escalated** at baseline:

```
  -- INK LEDGER: baseline words per band, and how many the merged reading asserts
     band  0 ignored     words=   2 baseline entries=   0 merged entries=   0
     band  1 ignored     words=  19 baseline entries=   0 merged entries=   0
     band  2 asserted    words=  27 baseline entries=  14 merged entries=  14
     band  3 escalated   words=  19 baseline entries=   0 merged entries=  12
     band  4 escalated   words=  20 baseline entries=   0 merged entries=  12
     band  5 escalated   words=  13 baseline entries=   0 merged entries=   8
     band  6 ignored     words=   1 baseline entries=   0 merged entries=   0
     band  7 escalated   words=  18 baseline entries=   0 merged entries=  10
```

The three `ignored` bands (0, 1, 6 — 22 words of prose) are **still ignored**: the merge did not
swallow prose to reach 1.0. Band 2's 14 asserted cells are carried through unchanged. The extra 42
are the balance-sheet values of bands 3/4/5/7, attributed to the column path
`('June 27,', '2026')` / `('September 27,', '2025')` and to row headers read off the stub.

So on p1 the answer to *"are the 56 a superset of the 14, and are the extras real ink?"* is
**yes, exactly, with no qualification** — and `escalated=0` is honest: nothing on that page is left
unread.

---

## 3. apple p0 — the criterion REFUTED, because the baseline reading was wrong

p0 loses 4 baseline entry cells and changes the column of 16 more. **All 20 are band 4, and 20 is
band 4's entire baseline entry set** (measured, not inferred):

```
lost bands    [4]
changed bands [4]
band4 baseline entry count 20 lost+changed = 20
```

Band 2's 28 cells are untouched. What happened to band 4 — a baseline `RECORD_TABLE` — is that it
read the page wrong in two matching ways:

* **It took a data row as its column header.** Its four columns were labelled `('35,695',)`,
  `('28,202',)`, `('122,432',)`, `('100,623',)` — the four values of the `Operating income` row.
  This is [[R166]]'s shape (a data row asserted as header), caught here on a second document
  position.
* **It took four row stubs as data cells.** `Other income/(expense), net`, `Income before provision
  for income taxes`, `Provision for income taxes` and `Net income` were `tab:EntryCell`s in a column
  named `Operating income`.

The merged reading repairs both, and the diff shows the repair as a loss and a set of changes
because it is comparing against a wrong baseline:

```
  -- LOST: baseline entry cells absent from the merged reading: 4
     p0-52-360   'Other income/(expense), net'              -> LABEL in merged
     p0-52-375   'Income before provision for income taxes' -> LABEL in merged
     p0-52-389   'Provision for income taxes'               -> LABEL in merged
     p0-52-403   'Net income'                               -> LABEL in merged

  -- KEPT: 44   of which text-or-column CHANGED: 16
     p0-305-403  text '$ 29,789' -> '$ 29,789'
                 col  ('35,695',) -> ('Three Months Ended', 'June 27,', '2026')
     …

  -- GAINED …
     [  4] band 4 asserted / was a baseline LABEL / text matches the word
            p0-333-346  '35,695'  col=('Three Months Ended','June 27,','2026') row=('Operating income',)
```

Every lost cell is **present in the merged graph as a `tab:LabelCell`** — none vanishes. Every
changed cell keeps its text byte-for-byte and gains a real column path in place of a data value.
The four values that were column *labels* become entry cells under the right row.

**The ruling.** R172's criterion cannot be met on p0 and should not be: it asks the merged reading
to preserve an assertion that was false. The correct general invariant, which the diff establishes
on **both** pages, is:

> Every baseline entry cell is present in the merged reading **as an entry or as a label** — never
> absent — and every gained entry lands on a baseline **word** with identical text. The merge loses
> no cell and invents no ink.

That is what `test_the_merge_loses_no_cell_and_invents_no_ink` now pins.

---

## 4. What the diff turned up that R172 was not asking about — the denominator moves

`score=1.0` on these two pages is **not** "everything was read". It is "everything the denominator
counts was read", and the denominator changed under the merge:

```
  page 0  TOKEN DENOMINATOR: baseline 148 (=48+100) -> merged 124 (=124+0)   delta -24
          page words in banded ink: 194   counted NOWHERE at baseline: 46   when merged: 70
  page 1  TOKEN DENOMINATOR: baseline  84 (=14+70)  -> merged  56 (=56+0)    delta -28
          page words in banded ink: 119   counted NOWHERE at baseline: 35   when merged: 63
```

The mechanism is an asymmetry in the token unit, and it is structural rather than introduced by
R165:

* an **escalated** band books *every word of every line it holds* — `escalated_total += sum(len(ln.words) for ln in band.lines)` (`src/iladub/etkl/compile.py:744`);
* an **asserted** matrix band books only its *data cells'* words — `asserted_total += sum(len(c.words) for c in data_cells if cell_round_trips(c, b))` (`compile.py:923`).

So reading a band instead of escalating it **removes** its row-stub ink from `asserted+escalated`
rather than moving it across. 24 words on p0 and 28 on p1 leave the accounting entirely. The R165
three-claims ledger already recorded p1's 28 as "counted nowhere" (`2026-09-04-r165-three-claims-measured.md` § B); what is new here is that it is a **denominator effect on the
score**, that it is the same effect on p0 at a different size, and that it is systematic rather
than a property of one stub column.

This is **not** R172, and it is not repaired here. It is raised as **R176**, with the fork it turns
on stated there and in this loop's handoff § 5a: *count* label ink, or *exclude* it from both sides.

---

## 5. Falsification

Per CLAUDE.md § Plan authoring discipline rule 4, for the one test this loop adds.

**The pin:** `tests/etkl/test_band_runs.py::test_the_merge_loses_no_cell_and_invents_no_ink`.

```
$ PYTHONPATH=src .venv/bin/python -m pytest tests/etkl/test_band_runs.py -q -k merge_loses
```

**Stub 1 — break "loses no cell".** Delete the `or a in m_labels` clause of the survival check, so
a baseline entry demoted to a label counts as lost:

```
E   AssertionError: page 0: 4 baseline entry cells vanish entirely: ['p0-52-360', …]
```

Restored → passes. This is the clause that carries p0's whole finding; without it the test asserts
the refuted criterion.

**Stub 2 — break "invents no ink".** In `entry_cell_diff._word_index`, skip band 7's words
(`if i == 7: continue`), so 10 gains on p1 lose their baseline word:

```
E   AssertionError: page 1: 10 gained cells land on no baseline word
```

Restored → passes. Full evidence in the commit that adds the test.

---

## 6. What is NOT done

* **The other 5 corpus documents are not diffed.** Apple is the only one on which a run merge is
  accepted (R165 measured 14 candidate runs, 2 accepted, both apple page tails), so there is no
  second document to diff — but that is an argument from a prior measurement, not one re-run here.
* **R176 is raised, not priced.** No fork taken, no score movement measured beyond these two pages.
* **The row label `('respectively',)`** on p1's `100,702` / `93,568` entries is a continuation
  fragment of the multi-line `Common stock and additional paid-in capital …` stub. It is a
  row-header *quality* defect, not an ink-identity one, so it does not bear on R172; recorded here
  and in R176's row rather than raised as a row of its own, since nothing in this loop measured how
  general it is.
* **The full suite was not run in this session.** `test_band_runs.py` and the register/governance
  tests were. The PR's CI is the record for everything else.
