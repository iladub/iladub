# Handoff — R225 arm B: the predicate is measured, the gate is located, neither has landed

**Topic:** [[R225]] arm B — the adoption gate, not the predicate

**Serves:** prog:criterion:etkl:04 — the ruling is made and half-executed; what remains is one
AXIOM clause and its oracle.

**Date:** 2026-09-14. **Branch this was written on:** `r225-arm-b-resolution-test`, cut from
`10b09c5`.

**Doc impact: none.** A handoff ships no term, no behaviour, no released assertion.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is typed
assertion-or-proposition so a reader can tell a mechanical step from a prediction that can fail.

---

## 5. The next concrete action

### 5a. D1 IS REVERTED AND ITS TWO PLACEMENTS ARE BOTH REFUTED. D2 comes first.

**This section has been re-graded twice by the session that wrote it, and both corrections are
left visible rather than tidied away.** It was first typed ASSERTED ("implement D2, it is
mechanical"); then PROPOSED, when spec § 1e measured a design defect in D1; it is now a record of
a *run* experiment, because the proposed placement was built and the corpus refuted it.

**BUILT AND REFUTED (`0e64a86`), so this is no longer a prediction.** Moving the resolution test
onto the derived `col_xs`, so an under-resolving band reaches `refine_rule_columns` instead of
returning at `compile.py:151`, **does** repair [[R13]]'s closure —
`test_header_confirmed_refinement` goes green and the border-only fixture recovers four columns
through that path. **The corpus refuted it anyway, worse than the placement it replaced:**

```
                 base      first-D1   relocated
  ons          0.9720       0.5407      0.1978     cells 571 / 389 / 118
  bfs          0.4033       0.8435      0.4419     cells 274 / 773 / 423
  (the five pinned documents are byte-identical under BOTH placements)
```

**And the failure mode was not the one this paragraph predicted.** It guessed bands might "still
under-resolve after refinement". What actually happens: refinement confirms boundaries on ons p8
and bfs p5, so those bands assert a *little* (p8: 6 cells; bfs p5: 156) instead of asserting
**nothing** — and one asserted cell disqualifies the page from adoption. `adopted` goes `[8]`/`[5]`
→ `[]`, and ons p8 falls 276 → 6 cells. The relocation **widens the very defect D2 exists to
repair**, turning total reading failures (adoptable) into tiny partial readings (not adoptable).

**Ruled 2026-09-14, reversing this section's original order: D2 FIRST.** Both placements are
refuted *while D2 is absent*, and both through the same adoption clause, so iterating on D1
measures gate accidents rather than readings. `compile.py` is back at its `10b09c5` state
(`54c0edf`, verified: `_word_column_count` gone, 23 tests green); D1 is recoverable from `3ee9495`
and `0e64a86`. Judge D1's placement **after** D2, on readings.

**RE-GRADED AGAIN, 2026-09-14 (second correction): the D2 clause is NOT "still asserted".** It was
typed ASSERTED on the strength of a predicate that had never been measured. It has since been
measured and **refuted before implementation** — see spec § 4 D2, which now carries the evidence.

- **The predicate was wrong.** *"The grid reads strictly more than the bands did"* has a baseline
  population of **12 pages across every corpus document**, including all five with an adjudicated
  `cor:scoreFloor` — `graincorp-capacity` p0 among them, which reads **perfectly (1.0)** today at
  406 band cells against 432 grid cells. `compile.py:1334-1339` had already recorded why: the two
  paths *segment* differently, and more cells is not a better reading.
- **It must compare UNREAD INK**, which is what the gate already asks and what `build_ledger`
  already computes.
- **D2 is two changes, not one clause.** `is_adoption_candidate` runs on the pass-1 graph *before
  any grid exists*, so `adoption-candidate.rq` can only widen narrowly; the comparison itself must
  be a new post-hoc refusal beside `document.py:1650` / `:1663`.
- **THE LEDGER CONTRACT IS SETTLED (2026-09-14) — spec § 1f carries the measurement and its
  control.** The answer is **the premise does NOT survive**, and the mechanism is not the one this
  bullet used to assert. It said the failure was double-counting; the measured failure is ink
  **vanishing**: `escalated_bands` selects on `tokens_escalated > 0`, so a band that asserts and
  does not escalate enters neither the residue term nor the untouched term, and its unadmitted ink
  is booked by nobody. **0 of 2** control pages (genuine adopting, where the premise is stated to
  hold) drop such ink; **5 of 12** population pages do — cbh p0 143 tokens, apple p0 46, apple p1
  43, bfs p5 39, bfs p6 29.
- **The revision is TWO terms with OPPOSITE treatments, not one line.** Touched bands: select the
  residue term by ANY booked ink, so an assert-only band's unread lines become residue. Untouched
  bands: their own reading stands and is not superseded, so their ink is **asserted by the band**
  and belongs in `asserted_tokens` — widening only the residue term would book it as escalated and
  understate the page.
- **DONE — the revision SHIPPED and was verified inert (`7f365ce`).** It landed ahead of D2 exactly
  as argued, so D2's effects stay separable from it. Evidence: **7/7 corpus documents
  byte-identical** to baseline by canonical graph hash (scores equal to 10dp); `test_adoption_ledger
  .py` **9 passed** (7 existing + 2 new); and **falsification per term** — reverting `booked_bands`
  to `tokens_escalated > 0` turns BOTH new tests red, while dropping only the untouched-asserted
  term turns ONLY the second red, so each pins its own defect. After the change
  `scripts/ledger_contract_census.py` shows `lost` falling to the prose floor on cbh p0 148→5,
  apple p0 68→22, apple p1 64→21, ons p4 101→82; bfs p5/p6 retain 33 and 14 tokens, which is the
  separately-recorded mixed assert-and-escalate under-booking, not this defect.
  **The `_R` stub gained `tokens_asserted: int = 0` — a double restored to the production
  `RegionReport` shape, NOT a weakened assertion:** on an escalate-only report both new terms are
  identically zero, so every existing expectation is untouched. That the whole suite was
  escalate-only is *why* this defect survived, so two assert-only tests were added rather than the
  stub patched and the gap left standing.
- **THE NEXT TASK IS NOW D2 PROPER**, in three parts, none of them started: narrowly widen the
  closure in `vocab/queries/adoption-candidate.rq`; add the post-hoc **ink** refusal beside
  `document.py:1650` / `:1663` (never a cell-count comparison — spec § 4 D2 records why that was
  refuted on 12 pages, `graincorp-capacity` p0 among them at a perfect 1.0); and discharge § 1g by
  superseding the contested asserting bands, or refusing the adoption where the grid would only
  partly cover one. Only after all three is D1's placement re-judged, on readings.
- **A SECOND obligation the ledger cannot discharge — spec § 1g.** `document.py:1672-1674`
  withdraws only *superseded* bands, so an asserting band's table would survive beside a grid
  region re-reading the same lines. Measured contested lines: graincorp-capacity p0 **27/27**
  (475 tokens), graincorp-stem p0 57/57 (747), apple p0 31/31, who-wfa p0 25/25, bfs p6 29/32;
  ons p4 is the one disjoint case. D2 must supersede those bands or refuse the adoption.
- **Limits, stated rather than implied:** only **two** control pages exist in the corpus, so
  "0 of 2" is thin; pages with no derivable grid, or where `len(reports) != len(bands)`, were
  **skipped and are unmeasured, not clean**; and bfs p5 / ons p4 leave 33 and 19 tokens
  unexplained (bands that both assert and escalate under-book), which is a separate open question.
- **Cost bounds the widening** (`document.py:1621-1625`): each candidate page pays a full extra
  `compile_tables`, refusals included, plus whole-graph SHACL (41.3 s on the stem).

**Sequence, per the maintainer's ruling of 2026-09-14 — this REVERSES what this paragraph used to
say:** D2 **first**, measured alone against a baseline `compile.py` (already reverted, `54c0edf`),
and only then is D1's placement judged on readings rather than on gate accidents. 5b still governs
the merge: nothing lands until the pair passes the oracle together.

### 5b. ASSERTED: D1 must NOT merge alone, and CI will not stop it.

Measured this loop: with D1 applied and D2 absent, **ons goes 0.9720 → 0.5407 and 571 → 389
cells**, which is exactly the collapse that refuted the naive guard. The corpus tests that would
show this are `corpus`-marked and **do not run in CI**, so a PR carrying D1 alone can be green and
still destroy a reading. D1 is applied on this branch; treat the branch as not-mergeable until D2
lands beside it.

### 5c. PROPOSED, and it must be RUN before anything is built on it: the replacement fixture (D3).

D1 destroys `border_only_grid_pdf`, which reaches the fallback gate *by being R225's defect
reproduced synthetically*. A replacement must reach the gate by a different route.

**One candidate design is already refuted, this loop, by reading the code rather than by trying
it:** "every band is one line" cannot be built — `detect_bands` splits where a gap exceeds `1.8 ×`
the **median** gap (`bands.py:37-52`), and gaps cannot all exceed their own median. The surviving
proposal — multi-line bands that stay single-column in gutter terms while page-wide alignment still
resolves ≥ 2 columns — is **unbuilt and may not be constructible**, because D1's whole effect is to
make those two measures agree. If it cannot be built, the fallback branch loses the CI coverage
[[R224]] created, and that is a residue to raise, not a detail to absorb.

### 5d. What this hands over exposed

- **The instruments are now COMMITTED; the snapshots are not.** All three censuses the spec quotes
  are in the repo and runnable from the root: `scripts/under_resolved_band_census.py` (§ 1a),
  `scripts/ledger_contract_census.py` (§ 1f) and `scripts/grid_band_overlap_census.py` (§ 1g), each
  carrying its § 8 PROCEDURAL classification. **The corpus snapshots remain session-local and will
  be gone** — `snap-before` / `snap-after` / `snap-after2` under the scratchpad, which are the
  before/after evidence for § 1b and for the relocation. A next session re-measuring must re-take
  the baseline with `scripts/corpus_verdict_snapshot.py` against a clean tree before it can diff
  anything. No row tracks that, and the figures in § 1b are the only surviving record of it.
- [[R226]]'s row still reads *"nothing here has measured whether it would"* about ONS stitching,
  which the prior session measured **false** (`is_continuation(p7, p8)` is `False`, refused on
  origin agreement). The register is mutable; amend it rather than re-run the probe.
- [[R202]] keeps its open half. etkl:04's route steps 1 and 2 (the contract triple, the grounding
  leg) are untouched and independent of all of the above.

---

## 1. Where the primaries are

- **The spec** — `docs/superpowers/specs/2026-09-14-the-gate-not-the-predicate-design.md`. Read
  § 1c first: it is the p7/p8 contrast that locates the defect in an adoption clause rather than in
  the fallback.
- **The code** — D1 is `src/iladub/etkl/compile.py`: a new `_word_column_count` helper and the
  guarded call at the old `:133`. Nothing else is modified.
- **The gate** — `vocab/queries/adoption-candidate.rq`, and its callers
  `adoption.py:97`, `document.py:1629`.
- **The rows** — [[R225]] (this), [[R226]], [[R202]] in `residues-open.md`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| Maintainer ruled arm B + subject etkl:04 (2026-09-14) | this handoff and the spec § 0 — **nowhere else**; it was a session decision |
| The binding constraint is the gate, not the predicate | spec § 1b, § 2 |
| The fix belongs in the `.rq` (AXIOM), not Python | spec § 4 D2 |
| D1 alone is the refuted state | spec § 1b; 5b above |
| Arm B completed converges on arm A's framing | spec § 8 |

## 3. Unverified or assumed

- **The full `tests/etkl` run COMPLETED, and it refuted this handoff's first framing.** It is
  **12 failed, 994 passed, 2 skipped, 1 xfailed, 2 errors (51m20s)** — not the three this document
  and the spec originally implied. The list and the two clearly-substantive cases are in the spec
  § 1d, corrected in place. In short: D1 also moves bfs p5's region count (12 → 14, pinned at
  `test_run_merge_seam.py:331`) and bfs p6's donated entry count (267 → 369, pinned in
  `test_grid_donation_seam.py`), so it reaches [[R210]]'s ink ledgers and the run-merge seam, not
  only ONS. **Classification was then RUN, and it found a DESIGN DEFECT in D1 — read spec § 1e
  before touching 5a.** `test_header_confirmed_refinement` fails because D1's refusal leaves
  `relines` empty, so `_build_ruled_band` returns at `compile.py:151` **before**
  `refine_rule_columns` at `:155` — which is [[R13]]'s closure, the confirmed-boundary path that
  recovers columns exactly when the author's rules are COARSER than the columns. A fixture's 4
  recovered columns collapse to 2. This **falsifies part of spec § 1a**, which offered the bfs p6
  `drawn=6, word=9` bands as D1's extra reach over the naive guard: those are refinement's own
  cases, and D1 disables the repair instead of extending it. The likely correction — compare
  AFTER refinement, against `col_xs`, rather than against the raw `xs` of `compile.py:111` — is a
  **proposition and unbuilt**. The other seven failures (3 `test_datagrid`, 3
  `test_grid_donation_seam`, 1 `test_escalation_furnish`) are named but **not diagnosed**.
  (The first attempt at this run passed `--timeout=1200`, which this repo has no plugin for:
  pytest answered `unrecognized arguments` and **exited 0 having run nothing** — a phantom green
  that would have shipped this understatement as verified.)
- **D1's § 8 classification is asserted, not argued.** It is procedural code comparing two derived
  measures, justified by the shipped precedent at `datagrid.py:346`. The plan must state that
  classification explicitly and defend it against the AXIOM default, or move it.
- **5c entirely**, per its grading.
- **That D2 as specified actually recovers p7** is unverified. p7's grid is intact (46 × 6 = 276,
  measured) and only the gate refuses it, but no run has yet shown the widened clause admitting it
  without disturbing the five pinned documents.

## 4. What this loop did

Took the maintainer's ruling; measured the predicate's corpus reach with a new probe (95 call
sites, 41 border-only, 33 under-resolved, **zero in the five documents carrying pinned floors**);
applied D1 and read the whole corpus twice, before and after, establishing that D1 alone reproduces
the refuted collapse and that the five pinned documents are byte-identical by canonical graph hash;
localised the collapse to ons p7 and traced it to the adoption gate's "not one entry cell anywhere"
closure, with p8 surviving via adoption as the contrast that proves the mechanism; and wrote the
spec.

**A method note worth carrying.** The spec's first draft cited a combined test figure from a
command that was never run — two real runs merged into one invented line, inside a document whose
own preamble claims rule-2 compliance. It was caught by re-reading the draft against the session's
actual commands and corrected to quote both runs as issued. A fabricated figure in a spec is
indistinguishable from a measured one to every later reader, which is the whole reason the rule
names the command rather than the number.
