# Handoff — the opportunity denominator ([[R47]], [[R77]], [[R245]])

**Topic:** The denominator is obtained. The disposer's surface is **2 false positives in 22 examined
pairs (9.1%)**, not "only 2" — and the § 5b seam measured out the other way, so the proposition
route is a larger slice than it looked.

**Serves:** prog:criterion:tab:04 — [[R77]] is one of its three blockers

**Date:** 2026-09-17. **Tree:** branch `the-opportunity-denominator`, cut from `main` at `0b34c28`.

**Doc impact: none.**

This loop MEASURED and built nothing shippable: five report-only counters on a committed
instrument, one corpus pass, three greps.

---

## 5. The next concrete action

### 5a. ASSERTED — measure what shipping the binding UNGUARDED would actually emit on who-wfa

**Typed ASSERTED because the outcome is a list of triples and a yes/no from an existing membrane,
the instrument already names the exact two pairs, and doing it is the work.**

The fork in § 5d has been unchosen for three loops because a guard cannot be justified (two rival
discriminators fit all 6 instances perfectly, so either is fitted by construction). **That framing
assumes a guard is required. Measure whether it is.**

The two false positives are `who-wfa-boys-zscore-0-5` p0 and p1, region 4, following band 5, value
`20`/`20.0`, column `c1`, an ordinal `[2,3,4,5,6]`. The question is narrow: **if
`_confirm_section_total` bound them, would anything already refuse them?**

- Does `tab:SectionTotal` have a SHACL shape at all, and does it constrain the summed column to be
  a *measure* rather than an index? (`grep -rn "SectionTotal" vocab/shapes/`)
- Does the membrane run on this path? `document.py:1631` sits inside `compile_document`; the
  section-facts branch sets `section_facts = True` to force validation (`:1830`) — confirm that
  reaches the same validator.
- What do the 2 bad facts cost if nothing refuses? They are 2 triples on one document of seven.

**If a shape already refuses an ordinal-column total, the guard question dissolves and the fork can
be taken on arithmetic alone.** If nothing refuses, the honest cost of the unguarded remedy is
known and small, and the fork becomes a decision the maintainer can rule rather than a measurement
gap. Either outcome ends a three-loop deferral. Budget: greps plus one single-document compile
(who-wfa, 50 s) — **not** a corpus pass.

> **ANSWERED — added by a later PR, 2026-09-17. § 5a WAS RUN, AND ITS HOPED-FOR OUTCOME DID NOT
> OCCUR: nothing refuses an ordinal-column `tab:SectionTotal`, so the guard question does NOT
> dissolve.**
>
> - **The shape exists and cannot refuse.** `tab:SectionTotalShape`
>   (`vocab/shapes/tab-shapes.ttl:323-326`) constrains exactly one thing — `tab:confirmsSection`
>   `minCount 1`/`maxCount 1`. Nothing about which column was summed, nothing about ordinality,
>   nothing about measure-vs-index.
> - **And it is satisfied BY CONSTRUCTION.** The emitter adds the typing and its witness in the
>   same unconditional branch (`document.py:1165-1166`), so a typing never ships without its
>   witness and the shape's only constraint can never fire.
> - **The subclass route is closed, deliberately.** `tab:SectionTotal ⊑ tab:AggregationRow`
>   (`tab.ttl:551`) and pySHACL runs `inference="rdfs"`, so a shape targeting `tab:AggregationRow`
>   would inherit onto it — but **no such shape exists**. The only aggregation-row shape targets
>   `tab:DetectedAggregationRow` (`tab-shapes.ttl:308`), and `tab.ttl:548` records that the
>   subclass exists *precisely so* the operand-requiring shape does not fire on bare
>   `AggregationRow`s.
> - **Validation reachability is NOT the obstacle.** `document.py:1632` sets
>   `section_facts = section_facts or confirmed`, and `_legs_for_document` (`:1199`) turns the TAB
>   leg on whenever `recognized or section_facts`. SHACL would run; it would find nothing to
>   object to.
>
> **Consequence for § 5d's fork:** shipping the binding unguarded costs the 2 known bad triples on
> who-wfa, refused by nothing. **The fork must be RULED, not dissolved by a membrane that already
> exists.** Both prior deferral reasons are gone and this one is now gone too — what remains is a
> maintainer's decision.
>
> **Incidental, and it sharpens [[R77]] rather than adding to it:** confirmation requires
> `last in agg` (`document.py:1164`), so on the widen-the-window arm cbh's real totals are *still*
> refused — a label-less total line has ONE occupied column and `is_aggregation_shaped` demands
> two. Window gate first, shape predicate second, exactly as [[R77]] already records.
>
> This block **adds** to the record; no line above it has been altered, Evidence being append-only
> after loop close. [[R47]]'s row carries the same finding.

### 5b. ASSERTED — the § 5b seam of the previous handoff is MEASURED, and it inverted

The previous § 5b asked whether the section-total path can express a proposition today, and said
"do not assume it is, and do not assume it is not." Correct on both counts — **the first grep said
no and was wrong.** Measured (evidence § 4):

- Proposition vocabulary **is** in the table path — 91 hits across `promote.py`, `propose.py`,
  `membrane.py`, `holon.py`, `rowrole.py`, `span.py`. A grep of `document.py` alone returns 0 and
  would have answered no.
- Proposers **are** in scope at the call site: `document.py:1631` is inside `compile_document`
  (`:1362`), whose signature carries `span_proposer=None, row_role_proposer=None`.
- But `promote.py` exposes exactly three emitters (`:62`, `:106`, `:150`), and each is built around
  a **NEURAL proposal object carrying `.confidence` and a suggester** (`promote.py:65-66`).

**An arithmetic derivation has neither.** It is exact Decimal equality; minting a confidence for it
would smuggle in the tuned constant CLAUDE.md § 8 forbids, through a field rather than a threshold.
So the proposition route is **a fourth proposal shape plus its emitter**, not a call to existing
code. That does not refute the previous § 5b's AXIOM/NEURAL reading — it prices it.

### 5c. ASSERTED — what is mechanically finished and must NOT be redone

- **Do not re-run the corpus census for the denominator.** It is `22` pairs examined / `5703`
  comparisons / `2` single-member comparisons, 27 pages, 0 skipped. Evidence § 2.
- **Do not quote 0.035%.** Both denominators are real and differ by 260x; the rule fires per pair,
  so the pair scope is the decision scope. Evidence § 3. Quoting the comparison scope is this
  loop's own subject inverted.
- **Do not re-verify that the counter edit was behaviour-neutral.** The control held exactly —
  same 6 rows, same values, same columns, same member counts as the prior § 8. Evidence § 1.
- **Do not re-grep the proposition machinery.** Evidence § 4 is a four-row table of what exists
  and where.
- **Do not adopt either discriminator.** Unchanged. The denominator does not break the tie; it only
  says the tie is being broken over 22 pairs rather than 8.
- **Do not re-derive the operands.** Column 13, members 10/16/14/5 — now four independent paths.

### 5d. PROPOSED — the fork is still unchosen, and 5a is what should decide it

Unchanged in substance from two handoffs ago: widen `_confirm_section_total`'s window to the
following band, or build [[R47]]'s trailing-strip peel so the total enters the band as a row.

**What changed is that both reasons given for deferring it are now gone** — the false-positive
"floor" (refuted last loop) and the unknown denominator (this loop). What remains is a genuine
design choice, and § 5a is proposed as the measurement that makes it decidable without fitting a
guard to six instances.

**Typed PROPOSED because it rests on 5a's outcome, which has not been run.** If a shape already
refuses ordinal-column totals, this fork is smaller than it looks; if nothing validates this path at
all, it is larger. **The next session finds out in the time it takes to grep `vocab/shapes/`.**

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-17-the-opportunity-denominator-evidence.md`. § 1 the control,
  § 2 the ladder, § 3 the 260x denominator fork, § 4 the seam table, § 5 what is not established.
- **The instrument** — `scripts/section_total_fp_census.py`, now carrying its own denominator.
  Committed in PR #248 as run; this loop adds five counters and no branch.
- **The run** — `docs/superpowers/2026-09-17-the-opportunity-denominator-evidence.md` § 1-2 quotes
  it in full. 460 s, serial, 27 pages.
- **The previous two loops** — `2026-09-17-the-false-positive-denominator-*` and
  `2026-09-17-section-total-is-in-its-own-band-*`. Evidence is append-only after loop close; their
  figures stand as written and are superseded only by this file's § 2-3.
- **The rows** — [[R47]] (owns the window gate), [[R77]] (the arc-serving second gate), [[R245]]
  (the instrument defect this loop's edit answers), all in `residues-open.md` + `residues.md`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The opportunity denominator is 22 pairs / 5703 comparisons | evidence § 2; [[R47]], [[R77]] |
| The pair scope is the decision scope; 0.035% is the wrong denominator | evidence § 3 |
| The counter edit is behaviour-neutral (control reproduced exactly) | evidence § 1 |
| The section-total path CAN reach proposition machinery | evidence § 4 |
| ...but has no arithmetic-shaped proposal, so the route is a new emitter | evidence § 4; § 5b |
| [[R245]]'s instrument now reports its own population | [[R245]] row; evidence § 1 |
| The design fork remains unchosen | § 5d above — **nowhere else**, so it is open |

## 3. Unverified or assumed

- **Whether 9.1% is acceptable** — this loop gives the rate, not a verdict. No remedy is licensed.
- **Whether anything refuses an ordinal-column SectionTotal today** — § 5a, unmeasured.
- **Whether an arithmetic proposal should carry a confidence at all** — raised, unanswered.
- **The 22-pair population is small and one-sided** — both false positives come from a single
  document (who-wfa), so "9.1% of pairs" is really "one of seven documents contributes every error."
- **Why vessel row 26 is `unplaceable`** — [[R243]]'s other half, untouched by three loops now.
- **Whether a correctly-drawn decoration rectangle would be regressed** — inherited, unchanged,
  still undetectable on this corpus.

## 4. What this session did, and what it cost

Read the handed-down § 5a, added five counters to the committed census beside its existing filters,
ran one serial corpus pass (460 s), and measured the § 5b seam in three greps. Amended three
register rows, wrote this handoff and the evidence. No production code touched.

**The cost worth carrying: the flattering denominator was available and would have been wrong.**
The same run yields 0.035% and 9.1% from one set of counters. The first is what an author reaching
for a number to justify a remedy would quote, and the rung that makes it wrong — that the rule fires
per pair, not per comparison — is visible only because the ladder was reported instead of a single
figure. **A census that prints one denominator invites the author to pick it; a ladder makes the
choice explicit and reviewable.**
