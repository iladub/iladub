# Handoff: a ground-truth set for the document compiler's PDF tables (2026-10-22)

**Serves:** maintenance — proposes prog:criterion:tab:13.

**Topic:** tab · **Date:** 2026-10-22

Written in a strata session (strata may not write to neighbours). For a fresh session working in
`../iladub`; François moves or copies it there.

## Goal

Turn "are the tables right?" into a number: a small, public, cell-checked ground-truth set and a scorer,
so that a table release can be judged and progress measured. François (2026-10-22): "we need to make
focused progress and accelerate, we are going too slow."

## Where the primaries are (all in `../iladub`; establish each before relying on it)

- `tests/corpus-baseline/*.json` (committed 2026-10-20): the only tracked number, document `"score"` =
  asserted / (asserted + escalated) tokens (`src/iladub/etkl/compile.py:3-4`). Establish the per-region
  structure: what a ground-truth comparison can key on (page, region, row, column).
- `tests/corpus-manifest.ttl:74`: "A SCORE IS NOT AN ACCEPTANCE", and the three-step route to accepting the
  nearest-to-acceptable document (contract triple; `tests/test_corpus.py::test_grounding_where_contracted`;
  a dated reviewer note against the page). Read it: it is the repo's own closest thing to this goal.
- `tests/held-out-manifest.ttl`: the 4 held-out PDFs (Fed H.4.1, arXiv 1706.03762v7, Caltrain weekend
  timetable, WHO COVID sitrep 41), URLs and hashes. Main corpus of 7 in `tests/corpus-manifest.ttl`.
- `docs/superpowers/residues-open.md`: R240 (score blind to cell-carriage defects), R295 (blind to a table
  classified NON_TABLE), R247 (the deciding comparison never run; Docling stack two releases stale),
  R246 (positioning unaccepted). Table-output defects to use as test cases: R230, R322, R166, R241, R289,
  R294, R74, R292, R279, R308, R320, R215, R239, R242, R243, R261, R278, R306.
- `docs/superpowers/2026-08-15-docling-positioning.md:138-162` (worse on unruled / merged headers, better on
  ruled and cross-page); `docs/superpowers/2026-10-06-held-out-corpus.md` §3-4 (reach vs score; "The score
  cannot see a table the compiler ignored").
- `tests/arc-manifest.ttl` (progress criteria; 36 met / 14 unmet per a subagent count) and `RELEASE.md`
  (procedure, no quality bar): where a "table release" criterion would be recorded.
- Latest handoff: `docs/superpowers/2026-10-21-substrate-03-spec-approved-handoff.md` (storage ledger and
  policy, not tables). This work competes with it for the next session.

## What was decided, and where it is recorded

- Build the ground-truth set next, for focus and speed (François, 2026-10-22): **recorded only here.**
- Whether the substrate arc pauses while this runs: **not decided.** François's call; recorded nowhere.
- Everything under "Proposed" is a proposal from this session, not a decision.

## Proposed (for the spec session to accept, change or drop)

- Size: 20 to 30 tables from the 11 corpus PDFs, both corpora, weighted to the held-out four and to the
  documents with open defects above. Public documents only.
- Ground truth source, cheapest first: (1) the publisher's own machine-readable release of the same table
  (statistics offices and the Fed often publish CSV/XLSX next to the PDF); (2) hand transcription with a
  second, independent check. Record which per table.
- Metrics: cell accuracy on exact text after a declared normalisation; tables found vs missed vs spurious;
  header-to-cell attachment. Report refusals separately: a refused cell is not a wrong cell, and the
  compiler's stance (refuse rather than invent) must stay visible in the number.
- Speed: time-box the first slice to one document end to end (graincorp-capacity, per manifest :74, or ONS
  if a publisher CSV exists), scorer plus CI floor, before widening. Merge the first slice in days, not an arc.
- Later, not in this slice: one public benchmark (FinTabNet or OmniDocBench) and a current-Docling re-run
  (closes R247).

## Unverified or assumed

- That the publishers (ONS, BFS, Fed H.4.1, WHO) release the same tables as CSV/XLSX: not checked.
- The residue list, the 36/14 arc count and the "~30 confirmed defects" are a subagent's keyword and hand
  count, spot-checked only for R230, R240, R247, R322, manifest :74, tags and baseline scores.
- That 20 to 30 tables is enough to separate progress from noise: an assumption.
- That the baseline JSON carries enough per-cell structure to compare against truth: not checked.

## Findings, second session (2026-10-22, read only in `../iladub`; web checks by a subagent)

- Manifest :74 confirmed as quoted above (graincorp-capacity, 390 asserted / 0 escalated, HOLD).
- **The baseline JSON carries no cell values.** Per page it has regions with `kind`, `verdict`, `cells`
  (a count), `reason`, and the `table` IRI (e.g. graincorp-capacity `p0#htable3`, 406 cells); plus
  `graph_sha256` and `graph_triples`. A scorer must compile the PDF and read the RDF graph: `tab:cellText`,
  `tab:value`, `tab:columnIndex`/`tab:colIndex`, `tab:headerText` (`vocab/ontology/tab.ttl:121,194,326,558,551`).
  Exact row/column keying on the graph: not yet established. PDFs live in `corpus/` (gitignored).
- Fed H.4.1 baseline: score 0.805, 11 pages, 2,413 cells over region verdicts asserted 15, escalated 19,
  superseded 9, ignored 39 (NON_TABLE); 36 of its table regions are UNSUPPORTED_TABLE.
- Publisher machine-readable releases (subagent opened each URL; not re-checked by me):

  | Document | Source | Verdict |
  | --- | --- | --- |
  | Fed H.4.1 2025-01-02 | HTML of the dated release, https://www.federalreserve.gov/releases/h41/20250102/ (21 tables) | exact match |
  | Apple FY26 Q3 | 10-Q XBRL, EDGAR 0000320193-26-000020 (period 2026-06-27) | exact values; label-to-concept mapping needed |
  | arXiv 1706.03762v7 | e-print LaTeX, https://arxiv.org/e-print/1706.03762v7 | exact; LaTeX parsing needed |
  | BFS bilan 2023 | PxWeb px-x-0102020000_101 (T1, T2); one row matched exactly | same data, other layout |
  | ONS IoS Feb 2026 | ios1 v131 minus v130 (beware: the previous-versions page mislabels v130's date) | derived only |
  | WHO wfa boys | expanded daily XLSX; monthly needs LMS recompute | other layout |
  | Caltrain weekend | GTFS starts 2026-01-31, PDF Aug 2024 | other vintage |
  | WHO sitrep 41 | global CSV is back-revised | none |
  | GrainCorp, CBH stems | PDF only, daily files overwritten | none |

- Consequence: the proposed first document (graincorp-capacity) has no publisher truth; it would need
  hand transcription with a second check (406 cells on one page, small).

## Next concrete action

**Decided (François, 2026-10-22): slice one is Fed H.4.1 2025-01-02**, truth from the dated HTML release,
time-boxed to its first one or two tables. Recorded only here.

In a fresh `../iladub` session: (1) establish how a cell's row and column are read from the compiled graph
for the Fed document; (2) fetch the dated HTML, pick the first one or two tables, and confirm they map to
regions in the baseline; (3) then write the slice-one spec (scorer, normalisation, refusals counted
separately, CI floor) for François's approval.

## Third session (2026-10-22, in `../iladub`)

- **Decided (François, 2026-10-22): the substrate arc pauses while slice one runs.** The substrate:03
  amendment (PR #364) stays as approved and is picked up after.
- Steps 1 and 2 were done and step 3 was drafted:
  `docs/superpowers/specs/2026-10-22-ground-truth-slice-one-design.md` (DRAFT, awaiting approval).

## Next concrete action (third session, written before the pointers below)

**ASSERTED:** the spec was approved on 2026-10-22, with all three decisions as recommended (spec § 8).
In a fresh session, write the plan from
`docs/superpowers/specs/2026-10-22-ground-truth-slice-one-design.md`. This session stopped at about
58K working tokens, past the originating floor, so it did not write the plan.

**PROPOSED (the plan's task 1 must run it, and it may fail):** seams (a) and (b) in spec § 3.3. Seam
(a) is which concept of a `Record` is the row label; seam (b) is which PDF regions HTML table 1's 36
rows span. Also § 3.5's prediction: `CORRECT` is about 0 on today's compile. If seam (b) shows table 1
split across regions or pages in a way `row_occurrence` cannot key, the matching key in § 3.3 needs
a spec amendment before any scorer code is written.

Pointers:
- The Fed graph compiles in 3m47s offline. Run it with `BAML_LIVE` and `ILADUB_RECORD_READINGS`
  unset (`scripts/corpus_baseline.py:60`); the API keys in the shell do not matter.
- The HTML snapshot is `https://www.federalreserve.gov/releases/h41/20250102/`. Table 1 is the
  2nd `<table>`; its cells carry `header=` (not `headers=`).

## Fourth session (2026-10-22, in `../iladub`)

### Next concrete action (written first)

**ASSERTED, if the maintainer approves spec § 9:** in a fresh session, write the plan from
`docs/superpowers/specs/2026-10-22-ground-truth-slice-one-design.md`, sections 1-8 as amended by § 9.
**PROPOSED:** § 9.2 item 5's prediction (`CORRECT` 0, `REFUSED` 4, `LOST` ≥ 36), which the plan's
first scorer run must test. Separately, § 9.3's multi-level header join must be measured in
`src/iladub/feed.py` before the scorer compares a `col_path`.

### Pointers

- The seam measurements, the reasons for them and the outcome rules they forced are spec § 9,
  commit `259c6e3`. **Approval of § 9 is recorded nowhere yet.**
- Two plan seams were measured in this session:
  - The baseline inputs are `INPUTS` at `scripts/corpus_baseline.py:56`; the truth directory and
    the scorer must be added there.
  - The snapshot's per-document hook is `snapshot()` in `scripts/corpus_verdict_snapshot.py`. Its
    document stem (`fed-h41-2025-01-02`) names `tests/ground-truth/<stem>/`.
- The minus-sign drop at `src/iladub/feed.py:297` is proposed in § 9.1 as a residue row. No row has
  been raised.

### Unverified

- The scratch artefacts (graph `.nt`, HTML snapshot, throwaway scripts) were not kept. Every
  § 9.1 figure is a subagent's measurement, spot-checked only for `feed.py:297` and the
  `MS Facilities` truth label.

### Fourth session, addendum

- **Spec § 9 was approved by the maintainer on 2026-10-22.** This is recorded in spec § 9.4. The
  next action above is now asserted: write the plan in a fresh session.
- The sign defect is raised as R332 (`residues-open.md`, `residues.md`).

## Fifth session (2026-10-22, in `../iladub`): the plan session's measurements

### Next concrete action (written first)

**PROPOSED, pending two maintainer rulings (below):** write the plan in a fresh session from the spec
as amended by those rulings. The plan is NOT written. This session measured first, found two spec
defects, and crossed the 50K originating floor (~64K working tokens) before any plan text existed.

### Measured (one offline compile at `4ed74f8`, 21,446 triples, score 0.8051146384479718)

- **§ 9.2 item 5's prediction holds**, on a throwaway scorer that implements § 9.2 as written
  (scratch, not kept): CORRECT 0, MISATTACHED 71, LOST 45, MISSING 8, REFUSED 4; sum 128;
  MARKED_LABEL 17; SPURIOUS 57. MISSING rows: `Reserve Bank credit` (consumed as header) and
  `Net portfolio holdings of MS Facilities 2020 LLC (Main Street Lending Program)` (split over
  r20/r21). REFUSED: `Total factors supplying reserve funds` (`p0#ignored4`).
- **§ 9.3's join is answered.** The record branch joins a column path with ASCII `" > "`
  (`_header_path`, `src/iladub/feed.py`); the per-cell branch joins with one space and carries the
  column key as a separate concept, the cell's own `text` set to `""`. Today every Fed record takes
  the record branch. The scorer must therefore compare truth paths joined with `" > "`, not ` › `.
- **Defect 1: the whole-page SHA-256 cannot be reproduced.** Two fetches 6 s apart, both 722,459
  bytes, hash `ffd2e532…` and `88c46ed0…`; § 9.1 recorded `bbe64539…`. The diff is two per-request
  tokens (a `data-injected="worker-…"` id and a Cloudflare `__CF$cv$params` script). The byte span
  of the 2nd `<table …>` … `</table>` (78,874 bytes, no nested table) hashes to
  `964e62c8ed5f3742b24df41f846950b3bcde45e97bbff92664cb84cda89a00fa` in both fetches.
- **Defect 2: the row_id page filter (§ 9.2 item 2) goes stale on the R166 fix.** `rid` is the row's
  header path when one covers it, and `p<page> <frag>` (`_row_discriminator`) only when none does.
  A fix that gives table 1's rows a row header tree removes the `p0 ` prefix, so every row stops
  being a candidate and the score cannot rise. Entry-cell concept regions are prov fragments of the
  form `p0-43-218`. Region subjects carry `prov:wasDerivedFrom <…/p0>` (the page document), which is
  how check (ii) can find a page's non-asserted text without parsing an IRI.
- **`beautifulsoup4` is not in CI's extras** (`readers` only; CI installs `baml,dev,docs,etkl`). The
  extractor must use stdlib `html.parser`. The throwaway did, and got 128 cells and the four paths.
- The `header` attribute values end with a space; split on whitespace.

### Fifth session, addendum

- **Both defects were ruled by the maintainer on 2026-10-22** and are recorded as spec § 10
  (amendment 2): the pin is the table-1 byte span, and a record's page is read from its concepts'
  region prefix.
- **ASSERTED next action:** in a fresh session, write the plan from the spec, §§ 1-8 as amended by
  § 9 and § 10. Task 1's first scorer run must reproduce the counts above (CORRECT 0, REFUSED 4,
  LOST 45, MISATTACHED 71, MISSING 8). These are now measured, not predicted.

## Sixth session (2026-10-22, in `../iladub`): the plan

### Next concrete action (written first)

**ASSERTED:** in a fresh session, execute `docs/superpowers/plans/2026-10-22-ground-truth-slice-one.md`
with superpowers:subagent-driven-development, from Task 1. Task 3 step 4's counts are measured, not
predicted. A difference there is a stop, not a tuning target.

### Pointers

- Plan committed at `7a851c8`, with four tasks. **Approved by the maintainer on 2026-10-22 ("approved,
  subagent-driven")**, including the plan's one "FOR RULING" point. Check (ii)'s refused texts come
  from `RegionReport.text` where `verdict != "asserted"` on a listed page, not from graph predicates.
  The reason, measured: `etkl:bandText` exists only on `etkl:IgnoredBand`, and no graph fact marks an
  escalated region as non-asserted.
- Not done: CLAUDE.md § Corpus baseline's input list will miss `tests/ground-truth/` once Task 3
  lands. That file is in the Contract class, so the edit is the maintainer's. The PR body flags it.

## Seventh session (2026-10-22, in `../iladub`): slice one executed

### Next concrete action (written first)

**PROPOSED:** the next loop fixes [[R166]] on Fed H.4.1 page 0 (a data row taken as header). Before
any compiler change it must close [[R333]] (amend the scorer for the per-cell record shape), else the
floor cannot move and `CORRECT` stays 0 whatever the fix does. Prediction to RUN first: after an R166
fix, `score_table` on table 1 gives `CORRECT > 0`. Refuted in minutes by one compile and one score.

### Pointers

- Commits: `9c15e50` (extractor and truth file), `87916db` (scorer), `ef73357` (snapshot hook),
  `8335cdd` (floor, `tab:13`), `ac5fc4d` (baseline truth block).
- Measured truth block: CORRECT 0, WRONG_VALUE 0, MISATTACHED 71, LOST 45, MISSING 8, REFUSED 4,
  SPURIOUS 57, MARKED_LABEL 17. Equal to the plan's oracle.
- The truth file has 18 marked labels (72 cells), not spec § 9.1's 17. The scorer's `MARKED_LABEL` is
  17 because the MS Facilities row is split in the PDF and never matches.
- `tab:13` carries `retrospective true` (`prog.ttl` M4 requires it when metOn == declaredOn).

### Decided, and where recorded

- The per-cell record shape is a known blind spot, deferred: [[R333]] (`residues-open.md`).
- The sign-cell asymmetry is measured, not fixed: [[R332]].
- The input-list gap in CLAUDE.md is the maintainer's edit: the PR body, and Unverified below.
- Slice one measures and does not change the compiler: spec § 5a.

### Unverified

- The multi-level `" > "` join (no equal col_paths in the real run). [[R333]].
- The per-cell shape: read from `src/iladub/feed.py:664,694,701`, never compiled. [[R333]].
- Byte-equality of the baseline: `corpus_baseline.py verify` was not run; one regenerate only.
- The floor test proves only that the instrument exists: `CORRECT >= 0` cannot fail, and the
  six-outcome sum holds by construction.
- CLAUDE.md § Corpus baseline's input list omits `tests/ground-truth/` (Contract class; maintainer's edit).

## Eighth session (2026-10-22): R333 closed

### Next concrete action (written first)

**PROPOSED:** fix [[R166]] on Fed H.4.1 page 0, where a data row is read as the column header. The
prediction to run first is that after the fix `score_table` on table 1 gives `CORRECT > 0`. One
compile (about 4 minutes, `held-out/fed-h41-2025-01-02.pdf`) and one score refute it. Second
prediction, also unrun: the fix produces the per-cell shape. If it produces one-record-per-row
records instead, the § 11 regrouping is never entered on this document, and that is still correct.

### Pointers

- Branch `r333-per-cell-scorer`. Code: `src/iladub/truth.py` (`_scored_rows`, `_paths_by_region`,
  `_path`, `TruthShapeError`). Tests: the four R333 tests at the end of
  `tests/test_ground_truth_score.py`. Spec: § 11 of `specs/2026-10-22-ground-truth-slice-one-design.md`.
- Probe: Fed page 0 has 31 records and 0 per-cell records. The truth block is byte-equal to the
  committed one.

### Decided, and where recorded

- The per-cell shape is regrouped by the row key's region, and an ambiguous region refuses: spec § 11.
- R333 is closed: `residues-closed.md`.

### Unverified

- The per-cell path has never run on a real compile. Only synthetic fixtures exercise it.
- `_paths_by_region` passes every table that has a header node to `_header_parts`, while the feed
  passes one logical table. A wider candidate set could choose a different deepest node for a row.
  If it does, the scorer raises (the region is unknown); it does not misscore. This is argued from
  the code, not measured.

## Ninth session (2026-10-22): R166 on Fed page 0 is a NEURAL question defect, not a missing worker

Written at about 55,000 working tokens, past the 50K originating floor. Part 5 was written first,
and it is graded per action below.

### Next concrete action (written first)

**PROPOSED, graded LOW-MEDIUM (written past the floor):** change how `ReadBoxhead` is asked so the
reader can see word *position*, then re-record Fed p0 and run the original prediction (`CORRECT > 0`
on table 1). The defect is in the question, not the oracle. `listing_of` (`src/iladub/etkl/boxhead.py`)
lists words in text-line order, and on this page the text layer interleaves two header rows. The
reader answers by text, and `dispose_boxhead` places by x, so it refutes the answer every time.
Candidate remedies, none measured:
(a) address words with their x-extent in the listing;
(b) a second ask that carries the oracle's refutation ("a fragment of col 1 centres in col 3").
(a) changes `question_key` for every recorded boxhead (`readings/boxhead/`), so every grid's reading
re-asks. That is a corpus-wide blast radius, and the 24-minute baseline regenerate comes with it.
**Refuted in minutes if:** a re-asked reading with the new question still drops col 1 or col 6.
Measure that with one live call before building anything else.

**ASSERTED:** a hand-edited recording is not a remedy. The recording is the worker's proposal, and
authoring it would make a person the proposer while the file claims to be reader output (§3).

### Measured (branch `r166-fed-header-row`, off `main` at `c63f5c2`, 2026-10-22)

- PR #367 (R333) merged as `c63f5c2`.
- Fed p0 derives one data grid: 7 columns, 32 rows. Its first admitted row is `Reserve Bank credit`,
  the true first data row. `header_block` = page lines 0–10. Lines 7–10 are the true boxhead; lines
  0–6 are the release title.
- **There is no recorded boxhead reading for it** (key `c5ab6578…f3acd6`). Offline, the boxhead is
  empty, nothing is carried, and adoption refuses ("the data grid left no less ink unread than the
  bands did", baseline `notes`). htable3 then asserts its own line 0 as the header: R166.
- **Three live asks (`ClaudeLongAnswer`, `claude-sonnet-5`) gave the same reading** and the same
  disposal. Col 0 (the stub label) stands. Four spanners stand: `Averages of daily figures` 1–5,
  `Change from week ended` 2–5, `Dec 25, 2024` 2–3, `Jan 3, 2024` 4–5. **Cols 1 and 6 are DROPPED.**
  The reader took col 1 = L9 words 0–4 (`Week ended Jan 1, 2025`), whose fragment spans
  x 271.8–567.4 with centre 419.6, and col 3 = [364.6, 419.4). It took col 6 = L8 word 10
  (`Wednesday`) + L10 words 3–5, whose L10 fragment centres at 294.2 in col 1. The page: L9's
  `Jan 1, 2025` sits at x≈530–567 (Wednesday's date), and L10's sits at x≈273–315 (Week ended's).
  The dates are swapped between text lines. `carried_lines` = (), so the ledger cannot improve.
- With cols 1 and 6 read correctly, every word of L7–L10 would be claimed by a standing label. That
  is argued from the addresses above and not measured, because no such reading exists.
- The grid splits each sign into a column of its own (7 columns against the truth's 5; [[R332]]).
  The reader's own note says it treated sign and value as two sub-columns. Even after a fix, the
  signed `Change` cells cannot score CORRECT until R332 moves. The unsigned `Week ended` and
  `Wednesday` columns can, which is what `CORRECT > 0` predicts.
- `scripts/header_row_census.py` on Fed found a second R166 instance: p3 band 2's labels are
  `Loans1, 3,621, 4,046, 365, 1,597, 0, ..., 9,629`. The census does not cover htable3, which is a
  hierarchical reading and not a record table.

### Pointers

- The three refuted readings are kept outside the repo. None is committed; `readings/boxhead/` is
  unchanged.
- Probes: `derive_data_grids` + `header_block` + `listing_of` + `question_key`; placement is
  `dispose_boxhead`'s fragment-centre check. A live call needs `PYTHONPATH=.:src` (the generated
  `baml_client` is at the repo root) and `BAML_LIVE=1`.

### Unverified

- That a correct boxhead would open adoption on p0. The ledger also books title lines 0–6 and the
  other bands' ink.
- That adoption puts the grid's labels where `table_records` and `score_table` read a `col_path`.
  The second prediction of the eighth session (the per-cell shape) is still unrun.

## Tenth session (2026-10-22): the boxhead question shows positions; p0 is now blocked on spanners

### Next concrete action (written first, at about 80,000 working tokens; graded per action)

**PROPOSED, graded MEDIUM:** design a disposal for boxhead spanning labels and their carriage into a
grid's column paths ([[R334]]). This is a design loop, so start it in a fresh session with a spec.
Without spanners, Fed p0's L7, L8 and L10 are never read in full, and every column path in the Fed
truth starts with a spanner. **Refuted in minutes if:** a reading with spanners carried still leaves
p0's data grid unadopted. Hand-patch `carried_lines` to count L7–L10 in one offline probe, rerun p0
and read the adoption verdict. That check is a probe, never a commit. If p0 still refuses, the
blocker is the title lines 0–6 in the ledger, and R334 is not the next loop.

**ASSERTED:** do not re-ask ons p8 to get `Section` back. One sample per question is the policy
until an omission oracle exists ([[R335]]).

### Measured (branch `r166-boxhead-positions`, off `main` at `ad43125`)

- `boxhead.listing_of` now gives each word as `[i]word@x0-x1` (whole points), and `boxhead.baml`
  says what the numbers are. Word order and addresses are unchanged, so `dispose_boxhead` is
  unchanged.
- Before any code change, three live asks with a positioned listing on Fed p0 all gave the true
  reading (cols 1 and 6 stand, none dropped). The recorded reading under the final prompt agrees.
- Every boxhead recording was re-asked: 23 questions, 23 files, 0 offline misses. The 10 old files
  are asked by no compile and were removed. Method and the reason for it: `readings/boxhead/README.txt`,
  last row. A fully live compile crashed on Fed with `UnshownCarriageError` before any boxhead ask,
  and that crash is live-only.
- Blast radius (`tests/corpus-baseline/`): Fed 0.8051 → 0.8128 (pp 2, 3, 8, 10), bfs 0.9074 → 0.9144,
  who-covid up (pp 2, 3), ons 0.8685 → 0.8555 (p8, [[R335]]). The other seven documents are byte-identical.
- **The ninth session's prediction `CORRECT > 0` on Fed table 1 is REFUTED:** truth is unchanged,
  `CORRECT: 0`. p0 still does not adopt ([[R334]]).

### Pointers

- Probes in the session scratchpad, not committed: an offline hit/miss logger wrapped around
  `RecordedBoxheadReader.read_boxhead`, a recorder with only the boxhead reader live, and an old/new
  disposal diff per grid. Each is under 30 lines and simple to rewrite.
- The 11 `readings/header_lines/` files the live compile wrote were set aside and not committed.

### Unverified

- That the bfs and ons differences are sampling variance and not caused by the new prompt. It is one
  sample per question, with no repeat run.
- That carrying spanners would open adoption on p0 (see the next action).

## Eleventh session (2026-10-24): the tenth session's probe, run — spanners are not enough

### Next concrete action (written first; graded)

**PROPOSED, graded MEDIUM:** one design loop, in a fresh session, that carries both a boxhead's spanners
([[R334]]) and a grid's title and unit lines ([[R336]]), with the spec written first. Fed p0 adopts only
when both are carried. Score it with ground-truth slice one's scorer on Fed table 1. **Refuted in minutes
if:** with both carried for real (not patched), p0's ledger still books 31 or more escalated tokens, or
`truth.table-1` stays at `CORRECT: 0` after adoption. In that case, read the column paths the adopted grid
emits before designing anything else. The neurosymbolic gate applies: what a title or a unit *is* is a
reading judgment, so it is NEURAL with an oracle, and it is not a line-position heuristic.

**ASSERTED:** lines 0–4 (the release masthead, band 1) need no carrying. Band 1 is never touched, so its
18 tokens stay booked verbatim, and p0 adopts anyway.

### Measured (offline, at `0ffa420`, `held-out/fed-h41-2025-01-02.pdf`, with `boxhead.carried_lines` patched in a scratchpad probe)

| carried on p0 | ledger escalated (page total 31) | residue | p0 adopted |
|---|---|---|---|
| (9,), as shipped | — | — | no |
| (7, 8, 9, 10), spanners | 38 = band 1's 18 + L5, L6, L32 | (5, 6, 32) | **no** |
| (5, 6, 7, 8, 9, 10) | 27 | (32,) | **yes** |
| 0–10, everything | 9 | (32,) | yes |

The tenth session's refutation clause fired: carrying the spanners alone leaves p0 refused. But the
blocker is not "the title lines 0–6", as that clause guessed. It is only L5 (`1. Factors Affecting
Reserve Balances of Depository Institutions`) and L6 (`Millions of dollars`). They share band 2 with the
boxhead, so reading the boxhead touches that band and turns them into residue.

### Pointers

- Probe scripts: the session scratchpad holds a `carried_lines` patch and a `build_ledger` printer, each
  under 30 lines. One full Fed compile takes about 4.5 minutes.
- [[R336]] is new. [[R334]]'s index line is annotated *necessary, not sufficient*.

### Unverified

- Whether refused pages in other documents share the title-in-touched-band shape. No census was run.
- Whether L32 on p0 (still residue in every variant) matters to the truth scorer.
