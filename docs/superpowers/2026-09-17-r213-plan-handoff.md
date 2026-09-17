# Handoff — R213 is planned and its two open seams are measured: execute, do not re-plan

**Topic:** [[R213]]'s plan is written against spec § 8, and the handoff's two outstanding items were
**run before the plan rather than transcribed into it**. One resolved a PROPOSED prediction (the
membrane's clause 2 has no SHACL subject); the other **refuted a claim in the spec** (three
`tab:cellText` readers are actually nine). The next session executes the plan.

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]].

**Date:** 2026-09-17. **Doc impact: increment** (the spec's own, unchanged).

Written with part 5 first, per CLAUDE.md § "The handoff's next action is TYPED". plimslop reports no
measured turn for this project this session, so the working-token figure is absent rather than
withheld — as in the three predecessor handoffs.

## 5. The next concrete action

### 5a. ASSERTED — execute `plans/2026-09-17-the-ink-the-page-does-not-show.md`, task by task, in order

Mechanical in its *scope*: the plan is the contract and its seven tasks are ordered by what blocks
what. **T1 first and alone** — the `tab:WrappedCellShape` disjunct (RS1) — because an unshown cell
cannot cross the shipped physical membrane until it lands, and every later task mints one.

Do **not** re-plan and do **not** re-derive the plan's invariants: each is stated once in spec § 8
and cited from the plan (plan rule 6). A session that re-argues the term, the two crossings or the
worker's refusals is rewriting a settled spec.

The plan carries, per task: the interface, the § 8 class (AXIOM / NEURAL / PROCEDURAL) with its
justification, the oracle, and a **FALSIFICATION** block (plan rule 4 — no evidence, the task
review fails).

### 5b. ASSERTED — clause 2 is a producer-side guard, and the two graphs are NOT unioned

This was 5c of the previous handoff and it is now **measured and closed**. `scripts/unshown_ink_prov_probe.py`:

```
   tab:EntryCell: 406   carrying prov:wasDerivedFrom: 406
   distinct prov objects: 406   objects shared by >1 cell: 0
   CandidateConcept: 769 nodes, 413 distinct regions reached
       fragment IS a cell IRI fragment (outcome 1): 0/413
       fragment IS a prov-object fragment (outcome 3): 406/413
   prov fragments naming exactly 1 cell: 406 / 406
```

and the decisive half — the grounded graph holds **0 `tab:` triples of any kind** while the document
graph holds 406 `tab:EntryCell`s, because `feed._validate_grounding` (`feed.py:720-730`) validates
`g` alone. **A `tab:EntryCell` shape in the grounding membrane would have zero focus nodes forever.**
Clause 1 (structural, over the document membrane, 406 live focus nodes) is the only shape written.

The join *is* constructible — a string rewrite between `urn:iladub:region:<frag>` and the cell's
`prov:wasDerivedFrom` fragment, injective 406/406 on gcap. **Do not build it.** § 8.5 forbids
inventing a path, and unioning two graphs to give one shape a subject is that.

### 5c. PROPOSED — the reshape round-trip is the one seam that could change the plan's shape at T5, and it must be RUN

**This is a prediction. It is the only one left, and it is deliberately labelled.** The plan assumes
that emptying `tab:cellText` moves the reshape round-trip's **two sides together**, because
`unpivot-inverse.rq:27` reads the entry cell's text into the reshaped graph and
`recipe.grid_values` (`recipe.py:87-101`) reads the same property off the source graph. If both go
empty, the round-trip still agrees and T5 is a disposition note.

**If they diverge, T5 is a task and the loop's shape changes there** — not at T1. Run the gcap
round-trip before and after emptying, and treat a divergence as a finding, never as a tolerance to
widen. The check costs one compile; discovering it at T7 costs the loop.

### 5d. ASSERTED — what the census already settled, so nobody re-greps it

The population of `tab:cellText` readers is **9 EntryCell readers**, enumerated in the plan's M2
table with the classifying command. 6 of the 10 `src/` reads are LabelCell reads through
`tab:hasLabel` and are **untouched** by this change. Spec § 8.2's three-reader parenthesis is
refuted and its three line numbers are miscited — use the plan's table, not the spec's sentence.

### 5e. ASSERTED — what must NOT be redone

- **Do not re-run O1 or O2 to establish anything** (§ 8.8). Both passed blind and are recorded.
  Re-run O2 only as a regression against § 8.7's changed ask.
- **Do not re-measure** region count (122), crop cost (0.05–0.54 s), crop legibility, the `tab:Blank`
  census, RF2's reach figures, RS1's shape refusal or RS2's address identity —
  `scripts/unshown_ink_seam_census.py --regions --blank --grain --graph --shape --address` re-runs
  every one.
- **Do not re-run M1.** `scripts/unshown_ink_prov_probe.py` is committed and its output is in the
  plan.
- **Do not re-open the term or the fork**, and do not re-litigate R213 option (c).
- **Do not write `tab:cellDatatype`, or any `tab:GridCell`-domained property, on a persisted cell**
  (§ 8.2's RDFS-domain hazard; [[R19]] is the precedent). **Do not write any shape over
  `tab:GridCell`** — 0 in the compiled graph.
- **Do not carry a colour into `src/`** and **do not build [[R250]]'s derivation**.
- **Do not read `grounded=0` on gcap as "nothing to guard."** It is the corpus battery's abstaining
  proposer behaving as designed (`tests/test_propose_grounding_context.py:19-21`).

## 1. Where the primaries are

- **The plan:** `docs/superpowers/plans/2026-09-17-the-ink-the-page-does-not-show.md` (7 tasks; M1
  and M2 inline at § 1; the weakest parts at § 4).
- **The governing spec text:** § 8 of
  `docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md`. §§ 1.4, 2.3, 2.4,
  3.1 and 4.3 above it are superseded in place.
- **The review behind § 8:** `docs/superpowers/2026-09-17-unshown-ink-spec-review.md` (RF1–RF8 and
  the two blind runs).
- **Instruments:** `scripts/unshown_ink_prov_probe.py` (M1, new) and
  `scripts/unshown_ink_seam_census.py` (six modes).
- **The rows:** [[R213]] (amended four times now) and [[R251]].
- **The seams, all measured:** `feed.py:253-258`, `feed.py:720-730`, `document.py:787-790`,
  `recipe.py:37,87-101`, `denormalization.py:168`, `celltype.is_blank` (`celltype.py:67-82`),
  `headers._grid_cells` (`headers.py:66-81`), `grid_evidence` (`celltype.py:138-160`), the five
  EntryCell minting sites (`holon.py:154,214,314` via `holon.py:41`; `holon.py:628`;
  `datagrid.py:691`), `tab:WrappedCellShape` (`tab-physical-shapes.ttl:26-42`), `tab:cellDatatype`
  (`tab.ttl:273`).

## 2. What was decided, and where it is recorded

- **Clause 2 of the membrane is a producer-side guard, not a shape** (M1). Plan § 1 M1, T5; R213's row.
- **Clause 1 stays a shape**, in the document membrane where 406 focus nodes exist today.
- **The `tab:cellText` consumer population is 9, not 3** (M2), and spec § 8.2's parenthesis is
  refuted on all three of its line numbers plus two whole classes of consumer. Plan § 1 M2; R213's row.
- **O3's six-document null is weaker than § 5 assumed** — it holds by construction, not by
  prediction. Report it as such rather than as a passed test. Plan T7.
- **Nothing was implemented.** No `src/` and no `vocab/` file was touched: this loop measured, planned
  and recorded.

## 3. Unverified or assumed

- **The reshape round-trip's two sides are assumed to move together** — 5c, the one PROPOSED item.
- **RS2's address identity is empirical**: one region, one document, five minting sites, and
  `datagrid.py:691` keys its IRI off a different counter.
- **O7's null may not exist in this corpus.** The plan requires the search and requires an absence to
  be *recorded*; an absence is not a control.
- **`tab:EntryCell` coverage is measured on graincorp-capacity only** (406/406).
- **The enhancement prohibition stays unenforceable from the answer alone**; no control page exists
  on which the reading route and the analysis route diverge.
- **The blind readers are not the shipped worker** — `baml_src/` holds five text functions and no
  image input. T6 is the plan's largest and least specified task, and is where a long loop will run
  long.
- **T5's falsification must construct the grounding path**, because `grounded=0` under the battery's
  proposer; a constructed path is weaker evidence than an observed one.
- **RF5's grain problem and § 7's fourth case are untouched.**

## 4. What this session did

Read the respec handoff and spec § 8, then ran the two things the handoff left outstanding rather
than transcribing them into a plan: the provenance probe (a new committed instrument), which
resolved § 8.5's three-way fork to outcome 2 and moved clause 2 off SHACL entirely; and the
`tab:cellText` consumer census as an `enumerating-before-claiming` job, which refuted spec § 8.2's
three-reader claim three ways. Then wrote the plan against § 8 with both measurements inline,
amended R213's row in both register files, and ran the register, doc-governance, arc and
source-citation gates green (17 + 81 + 8 passed).

**The transferable lesson, and it is the same one the predecessor handoff recorded in a different
costume:** the previous handoff typed its part 5 honestly — 5c PROPOSED, 5d a census not yet taken
— and *both* turned out to change the design. Running them cost minutes. Had this session written
the plan first and measured second, it would have shipped a SHACL shape with no focus nodes and a
consumer list missing two thirds of its population, and found out at implementation time inside a
plan it had already written.
