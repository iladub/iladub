# Handoff — the span the author drew: the plan is written, execute it

**Topic:** the-span-plan
**Serves:** prog:criterion:etkl:02 — Layers A and B are R211's arms, and R211 closes when
graincorp-capacity's records carry port names verified against the page. R166 is the criterion's
declared `prog:blockedBy` (`tests/arc-manifest.ttl:215`; the block is `:210-219`).
**Date:** 2026-09-13. **Branch:** `span-donation-plan`, cut from `main` at `4e5ef50`.
**Plan:** `docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md`.
**Spec:** `docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md` (§ 0 governs where
it and the body disagree).

**Doc impact: none.** This loop ships a plan and no code. The plan it ships declares
`Doc impact: increment` for the loop that executes it.

**Part 5 was written FIRST** — before the plan, while every measurement below was fresh and the
session was still cheap. Parts 1–4 were appended afterwards, which is the order
CLAUDE.md § Loop & context hygiene requires and the order the 3-of-3 evidence says never happens.

## 5. The next concrete action

### 5a. ASSERTED: execute the plan, task by task. Do not re-plan, and do not re-measure Layer A.

The design is settled, and — unlike the spec it comes from — it is settled on **runs, not readings**.
A fresh session opens the plan and starts at Task 1.

**What is NOT open, and must not be re-litigated:**

- **The spec's § 3.1 reuse assumption is REFUTED, and the plan already carries the replacement.**
  Grid donation asserts through `assert_record_region`, whose header emission is flat by
  construction — one node per column, `tab:coversColumn` emitted once (`holon.py:112-120`). Adding a
  coarser-donor clause to `grid-donation.rq` cannot produce a spanning header. Measured: the shipped
  leaf covering leaves 7 of 16 columns uncovered and `region_tiles` → **False** (7 `tab:CoverageShape`
  violations); `_covers_for_cell` leaves 5 and is refused the same way.
- **The covering is derived from the donor's DRAWN INTERVALS, and it is constructible.** Measured on
  graincorp p0: partition `1,1,2,2,2,2,2,2,2`, all 16 columns covered exactly once, no duplicate and
  no omission; `region_round_trips` → True, `assert_hier_region` → **406**, `region_tiles` → **True**,
  and the full page membrane conforms on both legs (`tab`, `dec`) built by `compile._build_membrane`.
- **The tolerance is inert and must stay inert.** `eps=0.01` and `eps=0.0` give identical maps,
  because every donor x appears verbatim in the recipient vector at 2dp. The rule carries **no tuned
  constant**, which is what keeps it AXIOM under §8. A reviewer who finds a tolerance doing work in
  the shipped diff has found a defect.
- **The ink ledger is preserved.** `assert_hier_region` returns 406, exactly the figure
  `tests/etkl/test_run_merge_seam.py:163` pins for `("graincorp-capacity-2026-08-04", 0)`.
- **`splitkey.py` is not the key split** and must not be extended into one: it resolves a dimension's
  *name*, and it has **zero production callers**.
- **The proposer seam is a defaulted parameter, not a fifth field on `SurfaceConcept`.** Measured:
  `ground_concept` has **2** production call sites against **24** test call sites, where
  `SurfaceConcept` has 5 src + 35 test construction sites and is frozen, so a new field changes
  `__eq__`/`__hash__` at the three sites that compare instances by value.

This is asserted rather than proposed because every step is mechanical and every seam that could
surprise the implementer has been **run**, not read. Where something remains unrun, it is in 5b.

### 5b. PROPOSED: two predictions that must be RUN, and either may fail

**P1 — label-to-interval assignment is unambiguous.** Ink-center containment and ordinal position
agreed on **all 9** labels of graincorp p0. That is **one donor on one page**, and agreement there is
not evidence they agree generally. The plan picks ink-center and pins ordinal as its falsifier. *If
P1 is wrong* — a donor whose label ink center falls outside its own drawn interval — the two rules
disagree and the relation must refuse rather than choose. Refuted in minutes by the plan's synthetic
negative; nothing in Layer A's design moves, only the refusal arm.

**P2 — the capacity contract grounds SOMETHING under the abstaining battery proposer.**
`test_grounding_where_contracted` ends in `assert grounded, "a contracted document must ground
SOMETHING"`, and authoring `cor:contract`/`cor:terms`/`cor:shapes` for graincorp-capacity is what
puts the document under that gate for the first time (today it is not skipped — it is never
parametrized, 2 of 7 documents are). The prediction is that the split keys ground through
`marker_field`'s unique admission to `ship:scheme-port` and the stubs through `exact_field`, while
every unlabelled leaf quarantines. *If P2 is wrong, the contract task is blocked* and the honest
response is to report it, not to swap in a live proposer to make the gate green — the spec is
explicit that the battery's proposer does not change.

**P2 is the expensive one.** P1 costs minutes; P2 is discovered only after Layers A and B are both
shipped, because nothing grounds until the split exists. Run P2's probe the moment Layer B mints its
first record — do not leave it to the contract task.

### 5c. What this loop deliberately leaves exposed

[[R213]] gains a live edge and the plan says so rather than closing it: graincorp's tonnages are
comma-formatted (`10,000`, `12,500`, `14,000`), so `ship:total`'s pattern
`^[0-9]{1,3}(,[0-9]{3})*$` admits them and refuses `Available`, `On Application`, `Y` and `N` — **but
it also admits bare `0`**, which is exactly the invisible-glyph hazard. Under the abstaining battery
proposer no leaf grounds at all, so the hazard is not live in CI; it becomes live the first time a
real proposer runs against this contract. [[R215]] (25 of 27 records carry no year) is untouched and
is the maintainer's call at etkl:02's read. [[R214]], [[R216]], [[R217]], [[R218]], [[R219]] and
[[R220]] are untouched.

**[[R221]] raised** `(66/210 closed)` — recomputed, not copied: the register stands at 210 rows / 66
closed, and R221 is the 211th. *A navigation aid's prescribed grep reaches only half the call sites
its own comment claims* — `compile.py:577` offers a grep in place of a line citation, deliberately,
because line citations there had rotted twice; the document-scope call binds different names
(`document.py:1243`) and is missed. Found while measuring the membrane wiring, not fixed here.

## 1. Where the primaries are

- **The plan** — `docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md`. Read § *Global
  Constraints*, then § *The invariant, stated ONCE*, then § *The seven decisions*, before any task.
  The tasks cite those sections rather than re-deriving them (plan rule 6).
- **The evidence** — `docs/superpowers/2026-09-13-the-span-the-author-drew-evidence.md`, 14 sections,
  every figure run on `4e5ef50`. The plan's evidence table says which section settles what.
- **The spec** — `docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md`. **§ 0
  governs** where it and the body disagree, and **§ 3.1's reuse assumption is refuted** by evidence
  § 2 — the plan carries the replacement, so do not implement § 3.1 as written.
- **The criterion** — `tests/arc-manifest.ttl:210-219`; the hold note and its three-step route off
  HOLD, `tests/corpus-manifest.ttl:46-73`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The covering is derived from the donor's DRAWN INTERVALS, in its own transient population | plan DECISION A, on `tab.ttl:336`'s population rule |
| A label belongs to the interval containing its ink center; **ordinal is the falsifier**, not a second rule | plan DECISION B (measured on one donor only — evidence § 7) |
| The reading is a `HierRegion` with the donor's tree and the recipient's rows, no level-1 nodes; the disposal is the shipped `region_tiles` and **no new shape** | plan DECISION C, evidence § 3 |
| Clause (d) `drawn(D) ⊊ drawn(R)` is ADDED; `same_ncols` is narrowed, never deleted, so grid donation's only null control survives | plan DECISION D |
| Layer B routes a NEW population to the SAME oracle via a sibling flag — `marker_field`'s body untouched, `test_corpus_stem.py:263` keeps its meaning | plan DECISION E, evidence § 9 |
| The proposer seam is a defaulted PARAMETER (2 call sites) not a `SurfaceConcept` field (5 + 35 sites), and **a test proves the slot is filled** | plan DECISION F, evidence § 10, § 11 |
| Provenance targets `{doc}#ignored{idx}-source`, not the band node, because `dec:consideredEvidence` has range `prov:Entity` and `etkl:IgnoredBand` is not one | plan DECISION G, evidence § 12 |

## 3. Unverified or assumed

- **Document-scope membrane conformance is UNVERIFIED** and is Task 3's named measurement. Evidence
  § 4 verified the *page* membrane on the region graph (both legs conform, donor-sourced label
  bboxes and all); the document-scope TAB leg runs on a different condition
  (`recognized or section_facts`, `document.py:1162`) and no code path builds a spanning donation to
  compile, so there was nothing to run.
- **P1 and P2 are propositions, graded in § 5b.** P1 (label assignment unambiguous) rests on one
  donor; P2 (the contract grounds something under the abstaining proposer) is unrunnable until Layer
  B mints a record.
- **Layer B's post-Layer-A population is predicted, not measured.** Today the condition fires on
  nothing — 0 of 8 childless multi-column nodes corpus-wide (evidence § 8) — and graincorp is
  predicted to be the only match afterwards. Not run.
- **Nothing but `region_tiles` judges a childless node's span**: `merge_tiling_ok`'s centering check
  is gated on `i in has_child` (`headers.py:398`), so it skips these nodes entirely. Measured, and
  left standing.

## 4. What this loop did

Wrote the plan the spec's § 5 step 3 ordered, on measurements rather than readings: it refuted the
spec's own § 3.1 reuse assumption, replaced it, and confirmed the replacement constructible and
membrane-clean before a line of plan was written. Shipped no code. Raised [[R221]].
