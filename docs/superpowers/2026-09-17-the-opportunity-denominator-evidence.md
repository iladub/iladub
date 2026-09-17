# Evidence — the opportunity denominator ([[R47]], [[R77]], [[R245]])

**Serves:** prog:criterion:tab:04 — [[R77]] is one of its three blockers

**Date:** 2026-09-17. **Tree:** branch `the-opportunity-denominator`, cut from `main` at `0b34c28`.

**Doc impact: none.**

The handed-down § 5a was ASSERTED — "the outcome is a number, the instrument exists, and doing it
is the work." It was, and this file is the number. It also answers the § 5b seam, which cost three
greps and changes that section's type.

---

## 1. What was run, and the control that says it measured the same thing

The committed census (`scripts/section_total_fp_census.py`, landed AS RUN in PR #248) gained five
counters and no branch. Every increment sits beside an existing filter; no `continue`, no
comparison, and no match-recording line was touched. **That makes the prior figures the control:**
a report-only edit must reproduce `true=4 false=2` over 27 pages with zero skipped, and any
movement would mean the edit changed the instrument rather than instrumented it.

```
PAGES SEEN 27   SKIPPED 0   MATCHES 6
NO PAGE SKIPPED -- the denominator is complete.
TOTALS  true=4  false=2
```

**The control holds, exactly.** Same 6 rows, same values, same columns, same member counts as
`2026-09-17-the-false-positive-denominator-evidence.md` § 8 — cbh's four panel totals on column 13
(members 10/16/14/5) and who-wfa's two ordinal coincidences (`c1 = [2,3,4,5,6] = 20`). One
whole-corpus serial pass, 460 s wall.

## 2. The denominator, as a ladder

```
OPPORTUNITY DENOMINATOR -- the population every match below was drawn from:
  asserted non-grid table regions              28
  ... having a following band                  25
  ... whose following band prints a number     22  <- PAIRS EXAMINED
  exact-equality comparisons performed       5703
  ... on a column of a SINGLE member            2
```

The ladder is reported rather than a single figure because each rung is a different claim, and the
rung that was missing is the one the remedy would be justified on. Six matches arise from six
distinct pairs (cbh tables 1/3/5/7; who-wfa table 4 on p0 and p1), so **6 of the 22 examined pairs
matched, and 2 of those 6 are wrong.**

The `comparisons_n1 = 2` rung was added to close a hole before it could be pleaded: a column of one
member has a "sum" equal to its own single cell, which is a trivial way to manufacture a collision.
Two such comparisons exist in the entire corpus, so single-member columns inflate nothing here.

## 3. THE FINDING: the two denominators differ by 260x, and the decision scope is the pair scope

This is the part worth carrying forward, and it is a trap the loop nearly walked into.

- **2 of 22 pairs = 9.1%.**
- **2 of 5703 comparisons = 0.035%.**

Both are true, both are drawn from the same run, and they differ by a factor of 260. The flattering
one is the wrong one. **The rule under test fires once per (asserted table, following band) pair** —
it decides *"does the band below this table hold its section total"* — so the pair is the unit of
decision, and 5703 is the count of interior equality tests performed inside those 22 decisions, not
a count of decisions. Quoting 0.035% would be the same defect this loop was convened to repair,
wearing the opposite sign: an unaudited denominator chosen because it is large.

**So the honest statement of the disposer's surface is: on this corpus the arithmetic binding fires
on 6 of 22 candidate pairs and is wrong on 2 of them — a 9.1% false-positive rate over examined
pairs, or 33% of what it actually fires on.** The previous handoff's *"only 2 false positives"* is
not supported at pair scope; 2 out of 22 is a rate a remedy must answer for, not a rounding error.

## 4. The § 5b seam, measured — and it inverts that section's own guess

§ 5b asked, before anything is written: *can the section-total path express a proposition at all
today?* It warned "do not assume it is, and do not assume it is not." Both halves of that warning
earned their place — the first grep suggested NO and was wrong.

| question | measurement | answer |
| --- | --- | --- |
| Is proposition vocabulary in the table path? | `grep -rE "CandidateConcept\|PromotionDecision\|ILADUB" src/iladub/etkl/` → **91 hits**, in `promote.py`, `propose.py`, `membrane.py`, `holon.py`, `rowrole.py`, `span.py`, … | **YES** — a first grep of `document.py` alone returned 0 and would have said no |
| Does `document.py` mint one? | `grep -cE "propose\|promote" src/iladub/etkl/document.py` → **8**, all of them pass-through `span_proposer=`/`row_role_proposer=` kwargs (`:1363, :1472-3, :1535-6, :1672-3`) plus one comment | **NO** — it threads proposers, never mints |
| Are proposers in scope at the call site? | `_confirm_section_total` is called at `document.py:1631`, inside `compile_document` (`def` at `:1362`), whose signature carries `span_proposer=None, row_role_proposer=None` | **YES** |
| Is there a generic proposition emitter to call? | `promote.py` exposes exactly three: `emit_promotion` (`:62`), `emit_span_promotion` (`:106`), `emit_row_role_promotion` (`:150`) | **NO** |

The blocker is the **shape of a proposal, not the reachability of the machinery.**
`emit_promotion` opens `agent = _suggester(g, proposal)` and
`Literal(Decimal(str(round(proposal.confidence, 6))))` (`promote.py:65-66`) — every existing
promotion is built around a NEURAL proposal object carrying a suggester and a confidence, because
all three were minted for BAML proposers. **An arithmetic derivation has no suggester and no
confidence**: it is exact Decimal equality, and inventing a confidence for it would be the tuned
constant CLAUDE.md § 8 forbids, smuggled in through a field.

**Consequence for the fork.** § 5b was typed PROPOSED against exactly this risk, and the risk is
real: routing the section total through assert/propose/promote is not a call to existing code but a
**fourth proposal shape plus its emitter**, for a proposer that is not neural. That is a larger
slice than widening `_confirm_section_total`'s window, and the fork in § 5d is the decision to take
first. This does **not** refute § 5b's reading — the AXIOM/NEURAL split it argues still stands and
is untouched by this measurement.

## 5. What is NOT established

- **Whether 9.1% is acceptable.** This file gives the rate, not a verdict on it. Nothing here
  licenses a remedy; it removes the *reason recorded for deferring one*, which was that the figure
  was unknown.
- **Neither discriminator is adopted, and nothing here weakens that.** The ordinal flag still
  separates all 6 instances perfectly (2 of 2 false, 0 of 4 true) and is still recorded to be
  falsified, not used. The denominator does not break the two-rival tie — it only tells us the tie
  is being broken over 22 pairs, not 8.
- **22 pairs is small, and it is one corpus.** A 9.1% rate on n=22 has a wide interval; the figure
  is a floor on knowledge, not a population estimate. Both false positives come from one document
  (who-wfa), so the rate is really "one document out of seven contributes every error."
- **Whether an arithmetic proposal SHOULD carry a confidence at all** is a design question this
  file raises and does not answer.
- **Why vessel row 26 is `unplaceable`** — [[R243]]'s other half, untouched by three loops now.

## 6. Cost

One corpus pass (460 s, serial — never two at once), five counters, three greps. The loop's own
subject held: the instrument now reports the population it drew from, and the first thing that
population did was expose a 260x choice of denominator that nobody had to make before.
