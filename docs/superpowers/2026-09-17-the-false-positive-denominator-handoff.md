# Handoff — the false-positive denominator ([[R47]], [[R77]], [[R245]])

**Topic:** The previous handoff's § 5a was run and is refuted twice over; the corrected census
returns `true=4 false=2` with **zero** pages skipped.

**Serves:** prog:criterion:tab:04 — [[R77]] is one of its three blockers

**Date:** 2026-09-17. **Tree:** branch `the-false-positive-denominator`, cut from `main` at
`e85aefc`.

**Doc impact: none.**

This loop MEASURED and built nothing. It ran the handed-down § 5a, found its prescribed mechanism
un-writable and its premise false, and replaced it with a census at the scope that can contain the
true positives.

---

## 5. The next concrete action

### 5a. ASSERTED — obtain the OPPORTUNITY DENOMINATOR before any remedy is justified on "only 2 false positives"

**Typed ASSERTED because the outcome is a number, the instrument exists, and doing it is the work.**

This loop's census prints every (asserted table, following band) pair that **matched** and never the
number of pairs it **examined**. `false=2` out of 8 opportunities and `false=2` out of 800 are
different claims, and only the second justifies a remedy. **This loop's own subject is unaudited
denominators, and its instrument has one** — recorded in evidence § 7, not hidden.

The fix is a counter, not a new instrument: increment on every `(i, i+1)` pair the census reaches
after its filters, and print it beside `MATCHES`. One whole-corpus pass. **Budget ~10 minutes and
run it serially** — measured this loop: 27 pages, ~72 s/page worst case (`graincorp-stem` 217 s for
3 pages), and never two corpus compiles at once (four memory kills on this repo's record). The
script is `fp_census_doc.py`, reproduced in evidence § 8's header; it is ~110 lines and is the only
thing that needs editing.

### 5b. PROPOSED — the GUARD cannot be settled on this corpus, so the remedy should PROPOSE, not ASSERT

**Typed PROPOSED because it rests on a claim about the code that this loop did NOT measure.**

Evidence § 9 is the load-bearing finding: **two rival discriminators separate all six instances
perfectly** — the summed column being ordinal (0/4 true, 2/2 false) and the following band having 1
line vs 6 (4/4 true, 2/2 false). The second is the shape the 2026-09-17 evidence § 10 already
refused as cbh-fitted. A corpus that cannot distinguish two rival rules cannot justify either, so
**any guard chosen today is fitted by construction.**

The reading that follows, and it is a proposition: split the decision by CLAUDE.md § 8 rather than
choosing a guard.

- **The arithmetic binding is AXIOM.** "A numeric value in the band immediately following a table,
  reconciling exactly with one of that table's own column sums" is a derivation over an RDF evidence
  graph — open-world, evidence-positive, monotonic, no tolerance (this loop's census computes it in
  exact `Decimal` today). It grows the graph from evidence that is *present*.
- **Whether that bound block IS the section total is a reading judgement**, and the two-rival result
  is the evidence that it is underdetermined rather than merely unsolved. Under § 8 that is NEURAL —
  proposed, disposed by a semantic oracle — or, equivalently here, routed through § 3's
  assert/propose/promote: emit the binding as a **proposition**, let a `iladub:PromotionDecision`
  govern its entry, and let the two who-wfa coincidences be *refused at the membrane* rather than
  *excluded by a fitted guard*.

**THE SEAM TO MEASURE FIRST, before writing any of it:** *can the section-total path express a
proposition at all today?* `_confirm_section_total` (`document.py:1136-1151`) returns
`(bool, value)` and its caller emits `tab:SectionTotal` as a fact. **MEASURE whether a proposed
SectionTotal has any representation** — grep for whether `tab:SectionTotal` is ever minted through a
promotion decision, and whether `dec:`/`iladub:` vocabulary is reachable from that call site — **do
not assume it is, and do not assume it is not.** If the path cannot carry a proposition, 5b is a
larger slice than it appears and the fork in § 5c below is the decision to take instead.

**If 5b is wrong, the next session finds out in the time it takes to run that grep.** That is why it
is graded PROPOSED and placed behind a named seam rather than stated as the plan.

### 5c. ASSERTED — what is mechanically finished and must NOT be redone

- **Do not attempt § 5a's y-overlap match.** It is un-writable: `RegionReport` (`compile.py:547-577`)
  carries no y-extent and no band reference. Evidence § 1.
- **Do not re-measure the six "skipped" pages.** All 27 pages align 1:1 under `page_bands` +
  `compile_tables`; not one of the six mismatches reproduces. Evidence § 2.
- **Do not census at PAGE scope.** cbh's four rosters are `UNSUPPORTED_TABLE`/escalated there and
  asserted only at document scope (`repaired_bands ((0,1),(0,3),(0,5),(0,7))`). A page-scope census
  returns `true=0` — a defect, not a result. Evidence § 4.
- **Do not trust prior's `false=4`.** It is 2 reproducible instances plus 2 band-source artifacts;
  prior's `value=17` has no counterpart at the correct indices. Evidence §§ 3, 5.
- **Do not use `detect_bands` where regions are involved.** `page_bands` re-segments and may merge
  (`compile.py:398-407`); raw output does not index-align with region reports. This is the whole of
  the prior instrument's defect. Evidence § 3.
- **Do not adopt either discriminator**, including the better-founded ordinal one. Evidence § 9.
- **Do not re-derive the operands.** Column 13, members 10/16/14/5, now agreed by three independent
  paths. Evidence § 8.

### 5d. PROPOSED — the design fork is STILL named and NOT chosen

Unchanged from the previous handoff's § 5c, and deliberately so: widen `_confirm_section_total`'s
window to the following band, or build [[R47]]'s trailing-strip peel/carry so the total enters the
band as a row. This loop removed the *reason given* for deferring it (the false-positive surface was
supposed to be a floor; it is not) but did not choose, because 5b may reshape the question into
"where does the proposition get minted" rather than "where does the window go."

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-17-the-false-positive-denominator-evidence.md`. § 1 the
  un-writable remedy, § 2 the alignment table, § 3 the pre-merge band source, § 4 the scope defect,
  § 5 the ordinal coincidence, § 6 R47 confirmation, § 7 what is NOT established, § 8 the corrected
  census, § 9 the two-rival finding.
- **The previous loop** — `2026-09-17-section-total-is-in-its-own-band-evidence.md` and its handoff.
  **Evidence is append-only after loop close**, so its § 11 still reads `false=4` and still lists six
  skipped pages. Those numbers are superseded by this loop's § 8 and by [[R245]]; the file is
  correctly left untouched.
- **The rows** — [[R47]] (owns the window gate), [[R77]] (the arc-serving second gate), [[R245]]
  (new: the instrument defect), all in `residues-open.md` + `residues.md`.
- **The scripts** — all four in this session's scratchpad, none committed: `skip_diagnosis.py`,
  `band_source.py`, `fp_census.py` (page scope, superseded), `fp_census_doc.py` (document scope, the
  one that produced § 8).

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| § 5a's prescribed y-overlap remedy is un-writable | evidence § 1 |
| § 5a's premise (a correspondence hole) is false | evidence § 2; [[R245]] |
| The prior instrument counted pre-merge bands against post-merge regions | evidence § 3; [[R245]] |
| The `+2` half of the prior mismatch is a reconstruction, not a finding | evidence § 3, § 7 |
| A page-scope census cannot contain the true positives | evidence § 4 |
| § 5a's prediction is refuted; the surface shrank rather than grew | evidence § 8 |
| Two rival discriminators fit equally ⇒ adopt neither | evidence § 9 |
| The census lacks its own opportunity denominator | evidence § 7; § 5a above |
| `grid_band_overlap_census.py`'s identical skip is DEAD, not a twin defect | evidence § 3 |
| The design fork remains unchosen | § 5d above — **nowhere else**, so it is open |

## 3. Unverified or assumed

- **The `+2` half of the prior mismatch** — consistent with document scope, but the prior script was
  never committed (`e85aefc` landed evidence, handoff and register rows only). May be permanently
  unreconstructable.
- **The opportunity denominator** — unknown. § 5a.
- **Whether the section-total path can express a proposition** — the seam named in § 5b, unmeasured.
- **The ordinal-column discriminator** — n=2, one document. Recorded to be falsified, not adopted.
- **Why vessel row 26 is `unplaceable`** — the other half of [[R243]], untouched by two loops now.
- **Whether a correctly-drawn decoration rectangle would be regressed** — inherited, unchanged,
  still undetectable on this corpus.

## 4. What this session did, and what it cost

Ran the handed-down § 5a, refuted its mechanism from the API surface, refuted its premise on all
seven named pages, identified the prior instrument's band source, wrote and ran a page-scope census
(wrong population — caught by `true=0`), then a document-scope census over all 27 pages. Amended two
register rows, raised one, wrote this handoff and the evidence.

**The cost worth carrying: the loop's own instrument reproduced the loop's own subject, twice.**

1. **The page-scope census had an unaudited population** — it filtered on `verdict == "asserted"`
   at a scope where the true positives are escalated. It returned `true=0` and *looked like* a
   finding. It was caught only because a zero true count is implausible on its face. **A census that
   cannot contain its own known positives is a broken instrument, and a control of known positives
   is the cheapest way to see that.**
2. **The document-scope census reports matches without the population examined** — recorded as a
   limitation rather than fixed, and promoted to § 5a as the next action. Same defect class as the
   one the loop was convened to repair, one level up.
3. **A construct that looked like a defect was not one.** `grid_band_overlap_census.py:38` carries
   the identical skip rule and was flagged mid-loop as a twin; measuring its call site showed the
   branch unreachable. **Measure the call site before naming a defect.**
