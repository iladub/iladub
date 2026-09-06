# R175 — the control moves into CI, on a second band the grid cannot supersede

**Doc impact: none.**

**Loop:** the ASSERTED action 5b of `docs/superpowers/2026-09-05-r173-5a-handoff.md`.
**Result:** **R175 CLOSED.** The control that keeps the document-scope supersession pins
non-vacuous now runs in CI, on the same document as the pins it controls, at identical page
arithmetic. The module goes from **7 to 8 CI-visible tests**.

---

## 0. What the residue was

`R173` 5a re-pointed five document-scope adoption pins off apple and onto
`currency_marker_escalating_pdf`, a synthetic document that adopts — and they became CI-visible,
which the apple versions never were. The control did not come with them.

`test_an_unsuperseded_band_on_apples_page_one_is_untouched` exists so that a change which
superseded *every* region would not satisfy `test_no_superseded_band_keeps_its_escalation_candidate`
and `test_the_effective_reading_of_a_superseded_band_is_not_the_escalated_one` vacuously — both
iterate `_superseded(...)` and assert something of each member, so an empty-of-survivors graph
passes them for the wrong reason. It stayed on apple because the one-band fixture had no
unsuperseded region to stand on. **Five pins looked CI-covered and their control did not run
there** — and that asymmetry is invisible from the test file, which is why it was raised as a row
rather than left in the evidence.

## 1. The mechanism that makes a second band possible — MEASURED, not reasoned

The load-bearing fact is one line:

```
src/iladub/etkl/compile.py:1276
    _dc_replace(r, verdict="superseded", tokens_escalated=0)
    if i in _led.touched and r.tokens_escalated > 0 else r
```

A report is superseded only when the grid **touched** it **and** it booked escalated tokens. A
band classified `NON_TABLE` books none (`compile.py:762-763` records the verdict `ignored` at 0
tokens), so **an ignored band cannot be superseded whether or not the grid read its ink** — it
survives adoption verbatim. That is the whole of the fixture design; nothing here is tuned.

## 2. Which shape of second band — four were compiled, one was kept

The spike drew the `currency_marker_escalating_pdf` table with a note below it, varying the note,
and compiled each at document scope. Every variant still adopts (`adopted=(0,)`):

| note | region1 | page a/e | verdict usable as a control? |
| --- | --- | --- | --- |
| two lines of prose | `escalated` `KIND_NOT_SUPPORTED`, 23 tokens | 16/25 | no — see below |
| three short lines | `escalated` `KIND_NOT_SUPPORTED`, 6 tokens | 16/8 | no — same |
| **one line** | **`ignored` `NON_TABLE` ('fewer than 2 lines'), 0 tokens** | **16/2** | **yes** |
| one long line | `ignored` `NON_TABLE`, 0 tokens | 16/2 | yes |

**Why the multi-line notes were rejected, and it is not aesthetics.** They book escalated tokens
the grid does not read, which moves the page to `16/25` and breaks
`test_the_ledger_and_the_graph_agree_on_the_adopted_page`, whose assertion `booked == p.escalated`
rests on a comment stating *"on THIS specimen the grid touched every escalated band"*. That pin
would then have needed re-baselining to buy the control — trading a measured invariant for a
control is not a trade worth making inside an ASSERTED action. **The one-line note changes no
number at all**, which is the property that made it the answer:

```
adopted=(0,)  score=0.8888888888888888  page0 asserted=16 escalated=2
  region0 superseded UNSUPPORTED_TABLE REGION_TILING_FAILED   a=0  e=0
  region1 ignored    NON_TABLE         'fewer than 2 lines'   a=0  e=0
  region2 asserted   RECORD_TABLE      (the grid)             a=16 e=0
  region3 escalated  UNSUPPORTED_TABLE DATAGRID_RESIDUE       a=0  e=2
```

Identical to the one-band fixture's `score=0.888…`, `16/2`, one superseded band, a 2-token
residue. **No pin was re-baselined in this loop.**

**Recorded as a deliberate non-choice:** the multi-line variant is the *stronger* control in one
respect — it books tokens, so it is eligible for supersession and would detect over-application
by flipping its own verdict, which an ignored band can never do. It was still rejected, because
the graph-level over-application it would catch that way is already caught by the query
assertions below (§ 4), and the price was a re-baselined ledger pin.

## 3. What was built

- **`tests/etkl/fixtures.py` — `currency_marker_escalating_with_note_pdf`**, a SIBLING, not an
  edit. `currency_marker_escalating_pdf` is relied on by `tests/etkl/test_unit_marker.py:250`
  and `tests/etkl/test_escalation_wiring.py:162`, and **both name its single band in prose**;
  adding a band there would have falsified two docstrings to fix a third file. Verified
  unaffected: `26 passed`.
- **`tests/etkl/test_adoption_document.py::adopting_doc`** re-pointed at it.
- **`test_an_unsuperseded_band_on_the_adopting_page_is_untouched`** — the control, in CI. It
  asserts *both* halves of R175's criterion in one run: that `_superseded(p)` is non-empty (so
  the pins it controls are not vacuous) **and** that the two shipped queries agree on the
  untouched band with no `supersededBy` on any row.
- **`test_the_two_queries_agree_on_an_untouched_band_of_a_real_document`** — the apple test,
  renamed and re-docstringed rather than deleted. It was *called* the control and had stopped
  being one: apple adopts nothing since `4cfee38`, so apple p1 has **no superseded region for it
  to be the control OF** — it was named for tests that run on a different document. The
  assertion is still true and still worth making against a real statement, so it is kept, saying
  what it is.

## 4. FALSIFICATION

The control is one-sided by design, and the stub is the over-application it exists to catch:
widen `document.py:1737`'s loop from `for idx in superseded` to `for idx in range(grid_idx)`.
That file has TWO textually identical `for idx in superseded:` loops — `:1682` withdraws the
escalation records, `:1737` writes the `dec:supersedes` edges. It is the second one.

```
FAILED tests/etkl/test_adoption_document.py::test_an_unsuperseded_band_on_the_adopting_page_is_untouched
E  AssertionError: diverged on an unsuperseded region:
E     eff=[(0, 'verdict')]
E     why=[(0, 'multi_table'), (1, 'kind'), (2, 'verdict')]
```

Both assertions break; the test can only report the first. Measured separately, out of band:

```
UNDER STUB, region 1
  eff: [(0, 'verdict')]                                    # the grid's admission itself
  why: [(0, 'multi_table'), (1, 'kind'), (2, 'verdict')]   # the band's own chain
  rows carrying supersededBy: 3 of 3
```

`effective-chain.rq` answers *the grid's admission* as the effective reading of a band the grid
never touched — the defect, reproduced. Restored: `12 passed`.

**A correction made before this document was written, and worth stating.** The docstring first
claimed the test fails "on that exact assertion" about `supersededBy`. It does not — `eff == why`
trips first. The stub was run, the output read, and the docstring rewritten to the measured
result. The `supersededBy` assertion is kept because it *names* the defect the first one only
detects.

## 5. The runs

| run | before this loop | after |
| --- | --- | --- |
| `pytest tests/etkl/test_adoption_document.py` | 11 passed, 1 failed by design | **12 passed, 1 failed by design** |
| `pytest tests/etkl/test_adoption_document.py -m "not corpus"` (the CI view) | 7 passed | **8 passed, 5 deselected** |
| `pytest tests/etkl/test_unit_marker.py tests/etkl/test_escalation_wiring.py` | — | **26 passed** |

The one failure is `test_an_adopted_page_never_scores_one_by_construction`, **red on purpose** as
[[R172]]'s detector. It was red before this loop and is red after, for the same reason, on the
same assertion. It must not be re-baselined.

## 6. What this loop did NOT do

- **It did not touch `currency_marker_escalating_pdf`.** Two other modules name its single band.
- **It did not re-baseline any pin.** The fixture shape was chosen to make that unnecessary.
- **It did not run the full suite.** The PR's CI is the record.
- **It did not touch [[R172]] or [[R173]]'s CI-visibility half.** Those are 5c and 5a of the same
  handoff, still open and still typed PROPOSED.
