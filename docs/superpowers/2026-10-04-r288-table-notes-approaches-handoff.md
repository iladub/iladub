# Handoff: R288 — a table note is the reader's judgement, not the author's label (2026-10-04)

**Topic:** r288-table-notes · **Date:** 2026-10-04

**Serves:** prog:criterion:etkl:03 — R288: cbh's four-line Note is classified, not read.

**Doc impact: none.**

Written at ~55K working tokens, just past the 50K originating floor. Brainstorming stopped at
"approaches", before any design section was presented. Part 5 is written first.

## 5. Next action (written first)

- **Proposed, and the probe may refute it. Design it with the maintainer before running it.** Run a
  scope probe over **every** ignored band on a page that carries at least one asserted table. Ask a
  NEURAL worker one closed question per band: *which of these enumerated tables on this page does
  this text qualify?* Its answer is a set of table addresses, and `none` is allowed. Dispose that
  answer by **equality** with the reading-order set: the asserted tables that precede the band on
  its page, back to the previous admitted note. Fix the decision rule before any call. The probe
  HOLDS only if the admitted set is exactly the human-judged notes and every title, piece of running
  furniture and paragraph of narrative prose is refused. The human-judged notes are cbh p0 band 9,
  bfs p5 `#ignored6`, ons p4 `#ignored1`/`#ignored2`, p7 `#ignored16`, p8 `#ignored8`,
  graincorp-capacity p0 `#ignored4`, and graincorp-stem p0/p1/p2. **Re-judge that list on the page
  images before using it as the oracle's truth: the controller read it from text heads only.** One
  prediction, from reading only: a title precedes its table, so its reading-order set lacks that
  table, and the equality should refuse it with no rule written for titles. Probe precedents:
  `scripts/r261_total_question_probe.py` (it carries a null control) and
  `scripts/r261_grand_total_role_probe.py`. Count the population before you count its cost
  ([[gliner2-population-count]]).

## 1. Goal

Carry cbh's Note, and every table note like it, as context bound to the tables it qualifies,
disposed by an oracle (CLAUDE.md principle 5). The maintainer can then lift cbh's hold honestly.
The scope is *carried and bound*. **Not** reading the Note's claims: the maintainer accepted that
recommendation in this session, and it is recorded nowhere else.

## 2. Where the primaries are

- R288's full row: `docs/superpowers/residues-open.md` (search `| R288`). Its close condition is
  (a) a reader plus an oracle that disposes the link, or (b) a maintainer ruling. (b) was refused,
  see § 3.
- The census script is `scripts/r288_ignored_band_census.py` (committed with this handoff, run at
  `b83d2d1` plus PR #295). It found 128 ignored bands across the 7 documents. Re-run it; do not
  trust the table in § 4.
- The `NON_TABLE` branch is `compile.compile_tables`, at the `emit_ignored_band` call. It touches
  no score counter. The score is `asserted / (asserted + escalated)` (`document.py`, `score =`).
- Existing context vocabulary: `tab:RegionCaption` / `tab:hasCaption` / `tab:SectionCaption` in
  `vocab/ontology/tab.ttl`. Check them for reuse before minting a `tab:TableNote`.
- The hold-kept ruling: the new `cor:adjudication` at the end of `tests/corpus-manifest.ttl`
  (PR #295).

## 3. Decided, and where recorded

- **The hold is kept and the next loop is R288** (maintainer, 2026-10-02). Recorded in
  `tests/corpus-manifest.ttl` (PR #295).
- **Scope: carry and bind, do not read the Note's claims** (maintainer, this session). Recorded
  only in this file.
- **Approach B is withdrawn on the maintainer's challenge.** B gated eligibility on the author's
  marker (`Note:`, `Source(s):`, …) grounded in a SKOS scheme. It misses graincorp's unlabelled
  caveats, 2 of the 5 note-bearing documents in a catalogue of 7. Every new document style would
  add a word to the scheme, which is a tuned constant in vocabulary form. Recorded only in this
  file. **What survives from B is its oracle**, the reading-order equality, because it reads no
  label.
- **Approach A is rejected** (a procedural reading order answers "which tables", so it fails §8).
  **The lexical oracle is out:** cbh's "Dates" equals no header exactly, and graincorp-capacity's
  "tonnages" matches no header at all. Both recorded only in this file.

## 4. Unverified or assumed

- **The census table, from a scratchpad run.** Re-run the script above.

  | document | ignored | table-qualifying, judged from text heads only |
  |---|---|---|
  | cbh | 2 | band 9's Note (85 words) |
  | graincorp-capacity | 4 | `#ignored4` "GrainCorp advise that the tonnages shown are indicative only…" |
  | graincorp-stem | 7 | the same caveat on p0, p1, p2 (16 words each) |
  | apple | 6 | none: titles and unit lines |
  | bfs | 42 | p5 `#ignored6` "Sources: OFS … \| 1 Jusqu'en 2010…" (97); the rest is prose and furniture |
  | ons | 59 | p4 `Source:`, `Notes`; p7/p8 numbered footnotes (89 words each) |
  | who-wfa | 8 | none: titles |

- Some ignored bands are **data rows**, a reading defect and not this subject: ons p7 `Q2 102.8…`,
  bfs p5 `#ignored9` `Suisse 3 8 815 385…`. A scope worker may answer them with a table. Decide
  before the probe whether they belong in the null set.
- The ag-trade header labels came from one scratchpad dump of `cellText` / `captionText` literals.
  cbh: `Date Loading`, `Date Nominated`, `ETA`, …. graincorp-capacity: ports only.
- **Whether a bound note's tokens should be booked `asserted` is unruled.** Booking them raises
  bfs's and ons's scores; cbh stays 1.0 either way.
- Whether "which tables does this note qualify" belongs in §8's NEURAL class is the controller's
  reading of §8, not a ruling.
