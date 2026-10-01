# Handoff: R261 — the cbh totals family, NEURAL proposer + exact sum (2026-10-01)

**Topic:** r261-totals-family · **Date:** 2026-10-01

**Serves:** prog:criterion:etkl:03 — cbh is the unaccepted document whose one live escalation is the totals family.

**Doc impact: none** (this handoff). The spec it hands to will declare its own.

Authored at 60,735 working tokens (plimslop hook), 1.2x the originating floor; the spec was not
started for that reason. Parts 1–4 are pointers. Part 5 is graded per action.

## 5. Next actions (written first)

- **Asserted.** Fresh session: `superpowers:brainstorming` on the architectural path, resuming at
  *"propose 2–3 approaches"*. The subject is chosen and R47's fork is ruled (part 3), so neither is
  re-opened. Output: `docs/superpowers/specs/2026-10-0X-r261-totals-family-design.md`.
- **Proposed, and it may fail — P1:** the worker separates the five exact-sum matches the census
  finds **today** (part 4): cbh's four port totals → *yes*, and who-wfa p0's `21` → *no*. Before the
  spec commits to a question wording, run the BAML question **once** on those five crops and record
  the answers. If the `21` comes back *yes*, the conjunction leaves 1 wrong in 24 pairs and the
  question is wrong, not the ruling. This costs minutes and needs the live key (`BAML_LIVE=1`; see the trap in
  part 4).
- **Proposed, and it may fail — P2:** binding `1,951,264` as the total over the four port totals is
  the same mechanism one level up. It may not be. The four totals sit in four separate
  `HierarchicalTable`s (`p0#table1/3/5/7` region order), and `1,951,264` sits in the box-split residue
  band, not after any one table. The spec must decide whether the grand total is in this loop or is
  its own question. Measure first which band `1,951,264` is in, and what precedes it, on a fresh
  compile.
- **Concern to put FIRST in the spec, not last:** box-split evidence § 5.4 (3) measured that the
  residue *without* `1,951,264` reads `NON_TABLE` → `ignored`. So once the total is carried, the
  Note block stops escalating because it is **ignored**, not because it is read. Part of cbh's score
  gain would come from that. The spec states it, and the acceptance adjudication must say so too.
  This is the trap recorded as *"roles→ignored games the score"*.

## 1. Goal

Carry cbh p0's totals (four port totals plus `1,951,264`) as total cells. A total binds only when a
NEURAL worker says *yes* **and** exact `Decimal` arithmetic holds. Then adjudicate cbh (`etkl:03`;
corpus 5/7 → 6/7).

## 2. Where the primaries are

- **Register:** `docs/superpowers/residues-open.md` row **R261** (subject, closure condition, furnish
  pin to move), plus rows **R47** (the fork, the 9.1% denominator, *"membrane does not dissolve the
  guard"*), **R77** (second gate: label-less total) and **R74** (`StackedGrids`, narrowed).
- **The candidate population, the false positives and the two tied discriminators:**
  `docs/superpowers/2026-09-17-the-false-positive-denominator-evidence.md` § 5, § 9;
  `…-the-opportunity-denominator-evidence.md` §§ 2–3;
  `…-section-total-is-in-its-own-band-evidence.md` § 4.
- **Census instrument:** `scripts/section_total_fp_census.py`. It pairs each asserted non-grid table
  with `bands[i+1]` and does exact equality against column sums. **This enumeration exists only in
  the script, not in `src/`.** A run was started this session (part 4).
- **Today's section-total code:** `src/iladub/etkl/document.py` `_confirm_section_total`. It searches
  the table's **own** band below the last hrule, never the following band; on confirm it writes only
  `rdf:type tab:SectionTotal` and `tab:confirmsSection`. It is called in `compile_document` after
  chain arithmetic and before adoption. Exact sums are in `rows.py` (`_numeric_token_sum`,
  `detect_aggregation_rows`) and `datagrid.py` `reconciles` (G8).
- **The worker pattern to copy:** `baml_src/header_lines.baml` + `src/iladub/etkl/headerlines.py`.
  That means a closed output, a module-global cache, `readings/<name>/{question_key}.json`, and a
  `Recorded…Reader` that writes only under `ILADUB_RECORD_READINGS=1`. Its ask site is
  `compile.py` `_header_lines_decision`, where the oracle runs first and the decision is recorded via
  `brec.record`.
- **cbh's current state:** the port-total bands are `NON_TABLE` → `emit_ignored_band` in
  `compile.py` and book 0/0. There is also an existing `donation.offer_single_line` hook for one-line
  bands, which must be checked as a possible seam. The residue escalates at the `KIND_NOT_SUPPORTED`
  else-branch. Re-booking ink as asserted is `_book_recovered_ink` (extent-exact), which the
  `NON_TABLE` path never calls.
- **Vocab:** `vocab/ontology/tab.ttl` defines `tab:SectionTotal` as *"below the section grid's
  closing rule"*. A total in the **following** band therefore needs a new term or an amended
  definition: a spec decision, with `Doc impact: increment`. There is no grand-total class; the
  nearest are `tab:overAxis`, `tab:aggregates` and `tab:AggregationCell`. Shape:
  `vocab/shapes/tab-shapes.ttl` `tab:SectionTotalShape` checks cardinality only.

Line numbers were measured by a subagent this session and are not reproduced here; open the
symbols.

## 3. Decided, and where it is recorded

- **Subject = R261, serving `etkl:03`.** Chosen by the maintainer 2026-10-01 in this session. It is
  recorded in this file and in user memory `r261-totals-family-loop`.
- **R47's fork RULED 2026-10-01: NEURAL + exact sum, conjunction.** The worker answers a closed
  *yes/no/abstain*. Exact `Decimal` arithmetic disposes. A binding needs both. **Rejected options:**
  the AXIOM ordinal-column filter (n=2, the footing already ruled insufficient), accepting cbh as-is
  at 0.91, and switching to bfs. **Recorded only here and in user memory**, so the spec's § 0 must
  carry it as a ruling, and R47's row needs an ✎ amendment when the loop lands.

## 4. Unverified or assumed

- **The census moved since 2026-09-17, and its new figures sit only in this session's transcript.**
  `section_total_fp_census.py` run at `5e33652`: 27 pages, 0 skipped. There are 32 asserted non-grid
  tables, 29 with a following band, and **24 pairs examined** (was 22). There are 5,775 comparisons
  and **5 matches**: cbh p0 tables 1/3/5/7 → the four port totals (col 13, members 10/16/14/5,
  1-line following bands), all TRUE. There is **1 FALSE**: who-wfa p0 table 4 → `21` (col 1, 6
  members, ordinal, 6-line following band). who-wfa's p1 false positive and the old `20` are gone.
  Nobody has asked why. It matters to P1 and to the spec's denominator, so re-run before quoting
  (~6 min).
- **cbh numbers.** Offline `compile_document(cbh)` at `5e33652` gives score `0.9103`, 873 asserted
  and 86 escalated. All 86 are in the residue region, `KIND_NOT_SUPPORTED`. This was measured this
  session; the command is in the transcript only.
- **Assumed, not measured:** that carrying the totals is all cbh needs for acceptance. The lesson
  from 2026-09-28 (*"dump the tables' cells before accepting"*) still applies at adjudication time.
- **Trap:** `ANTHROPIC_API_KEY` is in the shell, and `BAML_LIVE=1` also turns on the R213 region
  reader and the boxhead live half. Run offline work under `env -u ANTHROPIC_API_KEY -u BAML_LIVE`.

## Addendum 1 — P2 measured, census re-run, P1 blocked (2026-10-01, session 2)

Authored at ~55K working tokens (plimslop hook: 52,037 when it first fired; preflight logged
`handoff`). The spec was again **not** started. Part 5 below is graded per action and supersedes
part 5 above only where it says so.

### 5. Next actions (written first)

- **Asserted, and BLOCKED on the maintainer:** P1 cannot run. Every call to the Anthropic API
  returned `HTTP 400 invalid_request_error: "Your credit balance is too low"` (12 asks × 3
  repeats, all refused). Nothing was answered, so **P1 is unmeasured, not failed**. Once credit
  is restored the probe is one command from the repo root (~3 min, then 36 paid Haiku calls):
  `P1_REPEAT=3 env -u BAML_LIVE .venv/bin/python scripts/r261_total_question_probe.py`.
- **Proposed, and it may fail — P1 as specified above, with two additions.** (a) The probe now
  carries a **null control**: the first non-matching number of each table→following-band pair on
  cbh and who-wfa, so 7 nulls beside the 5 matches. A *yes* on a null is a finding, even though
  arithmetic would refuse it, because it says the question is answered by layout rather than by
  reading. (b) The question wording under test is the `PROMPT` constant in the probe. It is a
  **draft**. The spec owns the wording and must cite what P1 measured against it.
- **Asserted:** after P1, resume `superpowers:brainstorming` at *"propose 2–3 approaches"*. P2
  below **settles the scope fork** raised in part 5 above.

### P2 — where `1,951,264` sits (measured, offline, `5e33652`)

Offline `compile_document(cbh)` plus `page_bands(…, section_repair_bands={1,3,5,7})`, page 0:

| band | kind / verdict | tokens a/e | content |
| --- | --- | --- | --- |
| 1, 3, 5, 7 | `UNSUPPORTED_TABLE` asserted (`#htable1/3/5/7`) | 190/288/248/104 | the four port rosters |
| 2, 4, 6, 8 | `NON_TABLE` ignored, *fewer than 2 lines* | 0/0 | `374,904` / `737,289` / `660,363` / `178,708`, x 813–832 |
| 9 | `UNSUPPORTED_TABLE` escalated, `KIND_NOT_SUPPORTED` | 0/86 | line 0 `1,951,264` (x 812–836, y 683); lines 1–4 the Note (x 39–216, y 733–756) |
| 10 | `RECORD_TABLE` asserted `#table10` | 35/0 | PORT/WHEAT/…/TOTAL. Its TOTAL column sums to 699,321, not a rival |

What follows from it:

1. **`1,951,264` = 374,904 + 737,289 + 660,363 + 178,708 exactly.** It is a total of the four port
   totals, not of any one table's column. So its arithmetic needs the four port totals to be
   **bound first**. It is the same mechanism one level up, as part 5 above guessed. Its operands
   are totals, though, not cells.
2. **The grand total is NOT deferrable. This settles part 5's P2 fork.** The 2026-08-20 hold in
   `tests/corpus-manifest.ttl` (cbh `cor:adjudication`) is lifted by *"a reading of WHERE those 86
   tokens went and whether losing them loses anything the page asserts"*. The answer is now
   measured. 1 token is an asserted figure (`1,951,264`) and the rest are the prose Note. A loop
   that carries the port totals and defers the grand total leaves the only asserted content in
   the 86 unread.
3. **The concern from part 5 is now QUANTIFIED.** The port totals are booked 0/0 today, so binding
   them moves the score by about +4 asserted tokens (873/959 = 0.9103 → about 877/963 = 0.9107).
   Essentially all of any score gain comes from band 9, and most of band 9 is the Note. Whatever
   the spec does with the Note's tokens decides the score. Binding the totals does not. The spec
   must state the Note's fate as its own decision, not as a side effect. *Assumed, not measured:*
   the remainder reads `NON_TABLE` → ignored once line 0 is carved out. That is box-split evidence
   § 5.4 (3)'s counterfactual, measured on the residue *without* `1,951,264`, not on a carved band.
4. **Band 9 and band 10 interleave in y** (band 9: y 683–756, band 10: y 692–724). Band 9 is
   therefore not a contiguous strip. Any carve of line 0 out of band 9 must not assume one.

### Census re-run (`scripts/section_total_fp_census.py`, `5e33652`, this session)

It reproduces part 4 above exactly: 27 pages, 0 skipped, 32 → 29 → **24 pairs**, 5,775 comparisons,
**5 matches = 4 TRUE (cbh p0 t1/3/5/7, col 13) + 1 FALSE (who-wfa p0 t4 `21`, col 1, 6 members,
ordinal, 6-line following band)**. The part-4 figures are now reproduced in two sessions. Why
who-wfa's old p1 false positive and `20` vanished is **still unasked**.

### 3. Decided this session, and where recorded

- **The grand total is in scope** (P2, point 2). It is recorded only in this addendum, and it is a
  reading of the hold's own wording, not a maintainer ruling. The spec's § 0 should carry it for
  the maintainer to confirm.

### 4. Unverified or assumed

- P1 entirely: no answer has been observed.
- That the carved band-9 remainder reads `NON_TABLE` (point 3).
- Whether binding a word *inside* an escalated band has any precedent seam. Nobody has looked at
  `donation.offer_single_line` or `_book_recovered_ink` for this case yet.
