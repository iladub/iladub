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
