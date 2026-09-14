# Handoff — R225 arm B: the predicate is measured, the gate is located, neither has landed

**Serves:** prog:criterion:etkl:04 — the ruling is made and half-executed; what remains is one
AXIOM clause and its oracle.

**Date:** 2026-09-14. **Branch this was written on:** `r225-arm-b-resolution-test`, cut from
`10b09c5`.

**Doc impact: none.** A handoff ships no term, no behaviour, no released assertion.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is typed
assertion-or-proposition so a reader can tell a mechanical step from a prediction that can fail.

---

## 5. The next concrete action

### 5a. RE-GRADED — was ASSERTED, is now **PROPOSED** in its first half: D1's placement must be settled BEFORE D2 is implemented.

**This grading was changed after the fact, by the session that wrote it, and the reason is on the
record rather than tidied away.** When 5a was written, classification had not been run, and the
action read as mechanical. Spec § 1e then measured a design defect in D1 itself, so the premise
under "nothing depends on evidence that does not yet exist" was false when written — the evidence
simply had not been gathered yet.

**PROPOSED, and it must be RUN first:** that D1 belongs *after* `refine_rule_columns`, comparing
against the derived `col_xs` rather than the raw `xs` of `compile.py:111`. Today D1's refusal
returns at `compile.py:151` and skips refinement entirely, disabling [[R13]]'s closure. The
proposed placement is unbuilt, and it may not work: D1's whole effect is to make the drawn and
word measures agree, and refinement's candidates are judged by `confirmed_boundaries` on header
ink, so a band may still under-resolve after refinement. **Build it, run the corpus pair and
`test_header_confirmed_refinement`, and only then treat D1 as settled.**

**STILL ASSERTED, and unchanged by the above:** the D2 clause itself. The site is named — the
closure in `vocab/queries/adoption-candidate.rq` (`FILTER NOT EXISTS { ?cell a tab:EntryCell ;
tab:onPage ?page }`) — the two post-hoc refusals that stay are `document.py:1650` and `:1663`, and
the comparison neither makes (*does the grid read strictly more than the bands did*) is the thing
to add. Keeping it in the `.rq` keeps the decision an AXIOM, holon-scoped, the § 8 default.
**Sequence:** settle D1's placement, then D2, then land them together per 5b.

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

- **The instruments live in the scratchpad, not the repo.** The probe (`probe_all.py`) and both
  corpus snapshots are session-local and will be gone. The spec quotes their output, but a next
  session wanting to re-measure must rebuild the probe from § 1a's description. Committing it as a
  `scripts/` instrument was not done and no row tracks it.
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
