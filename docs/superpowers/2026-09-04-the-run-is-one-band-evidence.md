# The run is one band — what shipped, measured on the SHIPPED tree

**Date:** 2026-09-04. **Branch:** `the-run-is-one-band`. **Plan:**
`docs/superpowers/plans/2026-09-04-the-run-is-one-band.md`. **Spec:**
`docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md`.

**Doc impact: increment.** This document discharges the `Doc impact: increment` the spec declared
and the two preceding evidence documents each recorded as still owed:
`tests/corpus-manifest.ttl` gains a third `cor:adjudication` node on apple (append-only), and
`docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM entry. No released assertion
changes; no contradiction, so nothing blocks a release tag.

---

## 0. The one thing this document is for

**Every figure in the spec and in both spike documents is the PROTOTYPE's**, whose relation was
plain Python in a script. `2026-09-04-r165-three-claims-measured.md` § A showed that a SPARQL form
*could* derive the same 14 runs. **Nothing had ever shown that a SHIPPED implementation behaves
like the prototype.** This document is the first place that is shown, and every figure below was
measured on the shipped tree unless it explicitly says otherwise.

## 1. What was built

| piece | class | file |
| --- | --- | --- |
| four terms: `tab:PageBand`, `tab:RuledBand`, `tab:bandRuleX`, `tab:prevBandIndex` | vocabulary | `vocab/ontology/tab.ttl` |
| the run-evidence emitter | PROCEDURAL (transient graph emission) | `sectiongraph.run_evidence` |
| the adjacent-subsumption relation | **AXIOM**, open world | `vocab/queries/band-run.rq` |
| chain assembly | PROCEDURAL | `sectiongraph.merge_run_candidates` |
| the merged-band constructor | PROCEDURAL | `compile.merge_bands` (promoted from the spike) |
| the disposal | **the EXISTING closed-world membrane, reused** | `compile.merged_run_admissible` |
| the seam | — | `compile.page_bands` |

`_distinct_rule_xs` was extracted as **the single 2dp rounding site**, shared by
`_rule_xs_signature` and `run_evidence`. The 2dp is INHERITED and was neither re-tuned nor
justified by this loop (Global Constraint 2); it changes the run set on 0 of 27 pages.

## 2. The headline, measured on the shipped tree

```
apple document score   0.18950437317784258  ->  0.6288659793814433
  p0   score 1.0        asserted=124  escalated=0     (8 bands -> 3, run 2..7 accepted)
  p1   score 1.0        asserted=56   escalated=0     (8 bands -> 3, run 2..7 accepted)
  p2   score 0.027027   asserted=3    escalated=108   UNCHANGED — its run 3..7 is REFUSED
```

14 candidate runs across all 27 corpus pages; the membrane accepts **two** and refuses **12**.
The SPARQL derivation was cross-checked against the committed `scripts/band_run_census.py`
plain-Python relation on all 27 pages: **0 mismatches, the same 14 runs.**

**THE MEMBRANE HAS NOW SEEN A MERGED BAND.** Spec § 8 and the three-claims doc § 4 both record
that no document score had ever been measured with `validate_shapes=True` under a merge.
Measured here: `compile_document(APPLE, validate_shapes=True)` returns **the identical
0.6288659793814433**. The merged holon crosses the contract membrane unrefused.

## 3. The three honest limits

### 3.1 apple p0 and p1 are now SATURATED, and that is a loss

Both pages score **1.0**. 1.0 is the ceiling, so **no future regression on either page can ever
be detected by its score again.** On p1, 63 of the page's 119 band words are counted on neither
side of the ratio — the stub column the matrix-asserted branch has always excluded. That
exclusion is **pre-existing convention, not something this merge introduced**, but the merge is
what made the ratio saturate, and the signal loss is real. It is recorded at
`tests/etkl/test_decisionlog.py::test_recording_does_not_change_the_verdicts`, in the corpus
manifest's new adjudication node, and here — deliberately in all three places, because the score
is the number a later reader is most likely to quote and least likely to qualify.

### 3.2 M1 is upheld by CONSTRUCTION, not by evidence

The plan's own falsifier for M1 — decide the partition on the **repaired** build instead of the
unrepaired one — **does not fail the test.** Reported as a finding, not papered over: the corpus
cannot tell the two orderings apart, because its only page with a non-empty `section_repair_bands`
(cbh p0) produces no candidate run. `test_m1_the_partition_does_not_depend_on_section_repair_bands`
pins that the band COUNT is stable across repair sets; it does not exercise "the disposal verdict
differs between a repaired and an unrepaired build", and no corpus page can. That is `R169`
(the shipped-vs-disposed band) and `R171` (the cases the corpus cannot produce).

### 3.3 The refusal is doing work nothing specified it to do

Forcing `merged_run_admissible` to accept unconditionally, measured on the shipped tree:

```
graincorp-capacity p0    390 asserted cells  ->    0
bfs                p6    222                 ->    6
apple              p2      3                 ->    0
graincorp-stem     p0    586                 ->  586    UNCHANGED
```

`is_matrix_candidate` is therefore the sole guard on **618 measured asserted cells** across three
documents. **The plan's own prediction that graincorp-stem would lose all 586 is REFUTED** — it
loses nothing — so the "976 cells on two documents" figure inherited from the prototype should not
be re-quoted without re-running this. Raised as `R170`, with O3 as its standing detector.

## 4. The budget (spec § 3.5), measured as a BEFORE/AFTER pair

`scripts/doc_walltime.py`, base `d757279` vs the shipped HEAD, corpus symlinked into a worktree:

```
                        BEFORE      AFTER      delta
TOTAL wall              312.95s     361.7s     +48.8s
page_bands total         56.48s      87.57s    +31.09s   (~9.9% of the baseline compile)
perfect-cache saving     27.23s      42.96s    +15.7s
page_bands CALL COUNTS  3/2/6/6/16/18/6  ==  3/2/6/6/16/18/6   IDENTICAL
```

**Read the call counts before the seconds**, as that instrument's docstring orders. They are
identical per document: **the seam adds no extra `page_bands` call**, so the whole +31.09s is
*inside* `page_bands` — the SPARQL derivation plus disposing 14 proposed runs, 12 of which are
refused. A refusal is free in the graph and **not** free on the clock: graincorp-stem p0's refused
run costs 3.06s at `is_matrix_candidate` alone.

The documented per-document noise reproduced in this pair too, in the opposite direction from the
one recorded earlier: `who` came back **60.60s → 54.01s** under a change that proposes no run on
any of its pages. No single per-document figure here should be quoted alone.

**THE DECISION: the after-figure is accepted as shipped.** The remedy for the rest is `R168`
(the `page_bands` cache, whose 42.96s is worth MORE than this change costs) — deferred, and
deliberately not bundled, so this diff answers one question.

## 5. Plan defects found by measuring, and what was done about each

Every one of these was found by running the plan's own instruction, not by reading it.

| # | the plan said | measured | done |
| --- | --- | --- | --- |
| 1 | one `49` query-count pin (`test_query_terms.py:62`) | **three**: also `test_query_declarations.py:122` and `test_artifact_declarations.py:158` (the last counts `git ls-files`, so the new `.rq` had to be `git add`ed before it counted) | all three re-pinned to 50, each with its cause in place |
| 2 | the spike's test module is `tests/etkl/test_one_band_matrix_spike.py` | it is `tests/test_one_band_matrix_spike.py` | ran the real path; 16 passed |
| 3 | O2: `cells(BFS, 6) == 216` | the baseline is **222** (both counters); **216 is the LOSS under the falsifier**, written where the baseline belongs — and the plan's own Task 6 table says 222 | corrected to 222 |
| 4 | byte-identical: `a.splitlines().sort() == b.splitlines().sort()` | `list.sort()` returns `None`, so it reads `None == None` and passes with the seam deleted — CLAUDE.md defect 5, verbatim. Its `sorted()` repair then FAILS: 3516 `tab:hasBBox` blank nodes, same 8660 lines, same verdicts, same score, different bnode labels | substituted `rdflib.compare.isomorphic`, which is **strictly stronger** (it matches bnodes structurally rather than ignoring them), 3.8s |
| 5 | O1: `merge_run_candidates(page_bands(APPLE, 1))` | once the seam lands, `page_bands` returns the MERGED list, so O1 runs the relation over its own output and derives `()` — vacuous on apple, the only document where it bites, while still passing on refused-run documents | added an `as_proposed` fixture suppressing the DISPOSAL (never the geometry, at O5's own patch point); assertions unchanged |
| 6 | O2 falsifier: "graincorp-stem alone loses 586 asserted cells" | REFUTED — stem is unchanged at 586; capacity, bfs and apple p2 are what collapse | recorded as § 3.3 and `R170`; O2 still bites, on 3 of 4 documents |
| 7 | raise `R170`/`R171`/`R172`, since "the predecessor loop took R168 and R169" | **the predecessor took those numbers for THESE SUBJECTS**: `R168` *is* the `page_bands` cache the plan wanted to raise as `R172`, and `R169` *is* M1's load-bearing half, part of the plan's `R171` | `R170` raised as planned; `R171` raised for the two gaps that are **not** `R169` and cites it; the cache is **not** re-raised — `R168` gains the before/after pair its own closure condition asks for; `R172` raised instead for the spec § 7 entry-vs-cell row |
| 8 | Task 5 Step 3: the guard needs a fixture that isolates the escalation clause | the plan had already refuted apple p2; `graincorp-stem p1` measured asserted=0 / escalated=850, and the sharper finding is that **apple p1 asserted 14 at baseline**, so the guard had not isolated that clause for some time already | retargeted, with BOTH clauses now asserted in the precondition |

Two plan predictions were also **confirmed** and are worth recording as such: the expected damage
is exactly **14 failures in 5 files**, test-for-test; and the disposal verdict is **independent of
the doc and table URIs** (14 runs × 3 unrelated URI pairs, 0 verdicts differ), which is why
`merged_run_admissible` takes no doc URI.

## 6. What this loop did NOT rule

- **`R160` stays open.** `DocumentReport.adopted` is `()` **both before and after** — the one-band
  reading makes the page-1 adoption *unnecessary* rather than restoring it, so the reader-authority
  question is not answered and not made moot; it is simply no longer exercised by apple.
- **`R166` is narrowed, not closed.** Its p0 half is disposed of (band 4's operating-income row
  becomes a leaf row of the merged matrix); its p2 half survives. Its subject GROWS by one new
  mis-label of the same family measured on apple p1 — a three-line wrapped stub yielding a
  `HeaderNode` labelled `respectively`, the last wrap line rather than the first. No ink is lost;
  only the chosen label is wrong.
- **`R167`** (the em-dash in `celltype.is_blank`) is untouched.
- **`R172`** is the loop's own admission: *no content diff between the two readings has ever been
  run.* O3 bounds the ink per page; it does not identify the cells. "124 entries vs 48 cells"
  compares two different counters, and nothing has checked that the 124 contain the 48.

## 7. The full suite, and the eight failures that are NOT this loop's

`python3 -m pytest -q -p no:randomly` on the shipped tree, with the corpus present:

```
first run,  before the two fixes below:
10 failed, 1470 passed, 7 skipped, 1 xfailed, 3129 warnings in 3257.18s (0:54:17)

RE-RUN on the shipped tree, after them:
 8 failed, 1472 passed, 7 skipped, 1 xfailed, 3129 warnings in 3452.86s (0:57:32)
```

The remaining 8 are exactly the pre-existing set enumerated below — no other test moved.

**Two of the ten were this loop's, and both are fixed.** Both were mechanical consequences of this
loop's own documentation edits, and both are the *citation-into-another-file* hazard rather than a
code defect:

- `test_every_detail_row_has_an_index_row` — the register's INDEX rows are never struck; only
  detail rows are (`_INDEX_ROW = r"^\| *(R\d+) *\| *([A-Za-z]+)"`). The index row was written
  `| ~~R165~~ | closed |` and had to be `| R165 | closed |`.
- `test_etkl_criterion_sources_point_at_the_document_they_name` — appending apple's third
  `cor:adjudication` node pushed the who-wfa subject line down, so
  `tests/arc-manifest.ttl:259`'s `prog:source "tests/corpus-manifest.ttl:120"` no longer pointed at
  it. Re-pointed to `:122` and re-measured **after** the edit.

**The other eight are PRE-EXISTING and this change moves none of them.** Measured, not argued —
the three files were run in a `git worktree` at the branch base `d757279` with the corpus
symlinked:

```
                          base d757279      shipped HEAD
tests/etkl/test_adoption_document.py            6 failed        6 failed
tests/etkl/test_escalation_wiring.py            1 failed        1 failed
tests/test_corpus_stem.py                       1 failed        1 failed
                                          8 failed, 22 passed at BOTH
```

and the failure VALUES are byte-identical at both:
`test_stem_document_is_byte_identical_under_adoption` reports
`0.9658886894075404 == 0.9654553611484971`, and `test_corpus_apple_furnishes_the_measured_ten`
reports `() == (1,)`.

**The part worth recording is why nobody knew.** `corpus/` is gitignored (`.gitignore:52`), so in CI
every one of these eight SKIPS and the run is green: `gh pr view 158` reports the `test` check
**SUCCESS**, and the last three `main` runs are all `success`, on the very tree where these eight
fail locally. **A green `test` check is not evidence about this class of test at all.** Raised as
`R173`, with the note that the shared symptom — `adopted == ()` — is very likely the same finding
§ 6 records for `R160`, i.e. the 2026-09-02 loop's intended consequence never re-baselined here.
