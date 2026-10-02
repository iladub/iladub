# Handoff: R261 loop (b) — the grand total binds; cbh's hold goes to the maintainer (2026-10-02)

**Topic:** r261-totals-family · **Date:** 2026-10-02

**Serves:** prog:criterion:etkl:03 — loop (b) of the R261 totals family: cbh's grand total `1,951,264`.

**Doc impact: none.**

Written by the controller at ~105K working tokens — past the 50K originating floor, under the 150K
executing floor. Part 5 is written first and graded per action (CLAUDE.md § the handoff's next action
is typed).

## 5. Next actions (written first)

- **Asserted — the maintainer's decision, not a loop's:** lift cbh's hold (`tests/corpus-manifest.ttl`)
  and set `etkl:03`'s `prog:met`, or keep the hold. The facts the decision rests on (evidence § 7):
  cbh compiles at **1.0** (was 0.9107); the grand-total binding is worth **+0.0010** of that and the
  Note leaving the denominator unread is worth **+0.0883** ([[R288]]). Spec § 0 concern 2 predicted
  exactly this. If the hold is lifted, the adjudication's rationale must say the score is accepted
  with the Note ignored — otherwise R288 is the subject of the next loop.
- **Asserted — rides with the hold decision:** `test_escalation_furnish.py`'s
  `test_corpus_cbh_furnishes_exactly_one_request_for_its_one_live_escalation_the_residue` now pins
  **0** live escalations (re-read and falsified in Task 7: the binding supersedes the pass-1
  escalation). Its name is stale, and `tests/corpus-manifest.ttl` cites it — rename both together
  when the hold is decided. This loop was barred from touching the manifest.
- **Asserted — a one-line correction, mechanical:** three places say `tab:cellText`'s range is
  `xsd:string`: `vocab/ontology/tab.ttl`'s `tab:PrintedTotal` comment and `src/iladub/etkl/totals.py`
  (its module docstring and `table_level_totals`). That is false — `tab.ttl` declares
  `tab:cellText rdfs:range rdfs:Literal`, "NOT constrained to xsd:string". The conclusion drawn from
  it stands (the literal is never `xsd:decimal`, so the membrane cannot re-check the sum without
  reopening [[R92]]); only the premise is wrong. The first two predate this loop (loop (a), on
  `main`); this loop's final fix wave copied it into the third. Found by the fix wave's re-review,
  parked because the process allows no second fix wave.
- **Proposed, minutes to refute:** byte-compare the PNG production's `render_crop` sends for cbh's
  candidate against the probe's (`scripts/r261_grand_total_role_probe.py`, CROP=derived). Box parity
  is MEASURED (Task 6, exact equality); image parity is INFERRED — production boxes `line.words[0]`,
  the probe boxes the word from `page.extract_words()`. If they differ, "production reproduces the
  measured instrument" holds for the box only, and the one live production reading (Task 6) is the
  only evidence for the production image.
- **Proposed:** a page whose grand total binds in r2 over one adopted and one non-adopted table total
  keeps pass 1's record for that band — the R7 hop is universal by ruling (Task 5) — and nothing
  records the lost grand total. Unreachable on the corpus; spec § 8 excludes partial sets. Raise a row
  only if a corpus document reaches it.

## 1. Goal

Bind cbh's grand total `1,951,264` as a total-of-totals `tab:PrintedTotal` when the NEURAL worker
`AskTotalRole` answers `total_of_totals` AND exact Decimal arithmetic holds. Done.

## 2. Where the primaries are

- Spec / plan: `docs/superpowers/specs/2026-10-02-r261-grand-total-design.md`,
  `docs/superpowers/plans/2026-10-02-r261-grand-total.md` (PRs #292, #293).
- Evidence: `docs/superpowers/2026-10-02-r261-grand-total-evidence.md` §§ 0–7.
- Code: `src/iladub/etkl/totalrole.py` (worker stack), `compile._bind_printed_totals` (totals level),
  `totals.table_level_totals`, `document._printed_total_bands` (R7 hop, universal).
- Reading: `readings/total_role/1cabff….json` (`total_of_totals`).

## 3. Decided, and where recorded

- Every execution ruling is listed in the PR description ("Rulings I made"), with its cost if wrong.
- R7 hop universal, not existential (Task 5 fix round; spec § 5's wording said "any operand").
- R288 raised against the plan's "raise no row" — the row it assumed existed was never raised.

## 3a. Verified on the final tree (`189216a`)

- Full non-corpus suite, 30 chunks of 8 files, one process each: **1970 passed**, 0 failed
  (skips/xfail pre-existing).
- `scripts/r261_baseline.py --baseline` re-run on the final tree: all 7 hashes equal evidence § 7's
  after-table (cbh `354196bf…`, 1.0, 13698 triples; the other six byte-identical to § 0).
- `tests/etkl/test_escalation_furnish.py -m corpus`: 2 passed. The other 16 corpus files ran green
  at `0f3617b` (Task 7); the only behavioural change since is a `None` guard production cannot reach.

## 4. Unverified or assumed

- Spec § 7 S5's "the Note lands `ignored`" rests on the cbh run alone; the CI fixture's remainder
  measured `escalated`.
- The worker's discrimination beyond the arithmetic rests on n = 1 target / 4 nulls ([[R287]]).
