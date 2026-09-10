# Handoff — the grid the author drew: R201's fork is resolved, and the plan is next

**Topic:** [[R201]], fork resolved. Branch `r201-the-grid-the-author-drew`, off `93fa7ce`.
**Part 5 written FIRST and EARLY**, under the originating floor, per CLAUDE.md § "The handoff's
next action is TYPED". Parts 1-4 appended after.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — write the donation PLAN against the spec; do NOT re-derive the fork

The choice is made and the losing arm is refuted by measurement, not by preference: the **merge**
arm reads bfs p6 as a 2-column table and destroys all 222 cells it was meant to repair
(spec § 2.2), and no merge policy rescues it because bands 3 and 7 straddle every candidate grid
(§ 2.4). The **carriage** arm as R201 described it reuses `carried_roles_for`, which requires a
text-identical redrawn header and therefore cannot see a band that has *no* header (§ 4). What is
chosen is **grid donation**, specified in § 4.

**Why asserted:** every figure is on disk and re-runnable in two commands —
`PYTHONPATH=. .venv/bin/python scripts/grid_agreement_census.py` for the relation, and the § 2
merge figures from `merge_bands` — and the three clauses are pinned in CI with no `corpus/`
([[R173]]) by `tests/etkl/test_grid_donation_relation.py`, each falsified separately (loop
record § 3).

The plan's four decisions, in the order they bind:

1. **Where the AXIOM lives.** `sectiongraph.run_evidence` (`src/iladub/etkl/sectiongraph.py:223`)
   is the only page-scoped evidence graph; `classify_evidence` is single-band and cannot express
   a cross-band clause at all (§ 7, measured). Donation needs two facts `run_evidence` does not
   emit (`column_xs`, word boxes) and one structural change (`tab:prevBandIndex` restricts joins
   to the adjacent predecessor; donation joins **any** earlier band).
2. **What the donated reading is.** The continuation band has no header row: its line 0 is data
   and its labels are the donor's. Today bfs p6 band 4 asserts 27 cells with 9 false labels.
3. **What disposes it** — `region_tiles` plus an ink check, exactly [[R165]]'s chain. A refused
   proposal must leave the band compiling as it does today.
4. **[[R203]] first, or the plan is worse than the defect.** Donation propagates the *donor's*
   header to every band beneath it, and the donor's header is itself assumed
   (`classifygraph.py:53`). A wrong donor mislabels five bands instead of one.

### 5b. PROPOSED — that donation raises bfs's score, and by roughly the 45 label cells it moves

The relation fires on 5 bands holding 45 `tab:LabelCell`s, 40 of them numeric. Donation should turn
those into entries under band 2's true labels and add each band's line 0 to the body. **Nothing
measures the score effect**, and the loop that measured the relation deliberately took no
before/after pair (§ 7) — bfs p6 asserts 222 cells today and the donated reading's cell count is
unknown, not merely unrecorded.

**Why proposed:** two ways it can fail, and both are cheap to run before building anything.
(i) The membrane may refuse the donated reading — `region_tiles` has refused every merged
record-table reading tried so far, and no donated reading has ever been put to it. (ii) [[R205]]
guarantees the page stays wrong about 2 of its 8 data rows whatever donation does, so a plan
claiming "bfs p6 reads correctly" is already overclaiming. **Run the donated reading on bfs p6 band
4 alone, past `region_tiles`, before writing task 1.**

### 5c. PROPOSED — [[R204]] is probably dead weight, not a fix to schedule

`merge_bands`' preference for a derived `column_xs` over the author's drawn rules (spec § 2.3) is
a real defect, and once the merge arm is refused its only remaining consumer is [[R165]]'s two
accepted apple merges. The likely correct disposal is to record it and leave it, not to repair it.
**Why proposed:** that rests on the merge arm having no future, which this loop argued from one
page. A second document whose bands merge cleanly would reopen it.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the ruling, the refutation and every measurement | `docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md` | § 2 why the merge arm dies; § 3 the corpus census and the three clauses; § 4 the chosen arm and the closure-scope argument; § 5 what was deliberately not done |
| the loop record | `docs/superpowers/2026-09-10-the-grid-the-author-drew.md` | § 3 — the falsification that **fired**: the first fixture pinned only one of three clauses |
| the instrument | `scripts/grid_agreement_census.py` | that the donor is measured UNIQUE (`multi = 0`), not merely first |
| the pins | `tests/etkl/test_grid_donation_relation.py` | 4 tests, no `corpus/`; one fixture is CONSTRUCTED and says why |
| the predecessor | `docs/superpowers/specs/2026-09-10-the-header-is-assumed-design.md` | § 3 — why no *in-band* signal can exist, which is what forces a cross-band relation |
| the register | [[R201]] amended; [[R203]] [[R204]] [[R205]] raised | R203 is the one that gates the plan |

## 2. What changed

No compiler behaviour. One instrument, one test module (4 tests), three documents, four register
rows (R201 amended; R203, R204, R205 raised).

## 3. What was decided, and where that decision is recorded

- **The merge arm is refused.** Spec § 2, from `merge_bands` figures on bfs p6.
- **Grid donation is the chosen arm, and it is an AXIOM (derivation half).** Spec § 4.
- **`carried_roles_for` is the wrong instrument for a headerless band.** Spec § 4, from that
  function's own docstring. Recorded nowhere else — R201's row said the opposite.
- **The cross-band tiling test is evidence-positive and does not break `_rule_boundaries`'
  closure note.** Spec § 4, last paragraph. This is an argument, not a measurement.

## 4. Unverified or assumed

- **No donation code exists and no score was measured.** See 5b.
- **"No false donor" is 12 bands on 27 pages of 7 documents**, and the clause carrying it
  (`same_ncols`) fired exactly **once** — graincorp p0. One control is one control.
- **That band 2's line 0 is bfs p6's true header is a READING** ([[R166]]'s spec § 2 row 5), made
  from printed rows and `pdfplumber.extract_text`. Every donation figure rests on it — [[R203]].
- **`wholly_drawn` compares at 2dp**, inherited from `_rule_boundaries`' own `round(r.x, 2)`. A
  donor whose `column_xs` coincided with its rules to within 0.005 would read `drawn=yes`
  spuriously; none does on this corpus, unmeasured off it.
- **The full suite was not run** — only the two R166/R201 modules (6 tests, green). The suite takes
  ~45-60 minutes; do not run it in a background subagent (a measured trap).
