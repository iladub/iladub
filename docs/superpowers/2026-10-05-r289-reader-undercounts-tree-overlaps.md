# Evidence + handoff: R289's default arm is refuted twice — the reader undercounts, and the right split breaks the header tree (2026-10-05)

**Serves:** prog:criterion:etkl:03 — cbh's acceptance; [[R289]] is its only blocker.

**Topic:** r289-reader-refuted · **Date:** 2026-10-05

**Doc impact: none.**

Read-only measurement. No `src/` change. The spec this session set out to write is **not** written:
two of its premises were refuted before it was finished (§ 2). Part 5 was written at about 66K working
tokens, past the 50K originating floor, so each action in it is graded.

## 5. Next concrete action (written first)

1. **ASSERTED — run first, in a fresh session: find why `infer_header_tree` builds overlapping
   same-level nodes on cbh's rosters when `body_line` is the first vessel line.** Every arm that puts
   the `Accepted` line into the header passes through `infer_header_tree`, and § 2.3 shows that today
   it makes every roster fail tiling (`tab:NoOverlapShape`). Until the tree tiles, no split proposer,
   whether reader, rule or anything else, can lift cbh's hold. The harness is
   `scripts/r289_split_blast/reader_probe/m4_counterfactual.py`. Dump the tree's nodes per level,
   with their column spans, for one roster at NEW, and name the two nodes that overlap. The outcome is
   open. The action is mechanical.
2. **PROPOSED, and the maintainer's call: what proposes the split.** The shipped `CountHeaderLines`
   question fails here (§ 2.2). The two arms in view are:
   - (a) **NEW as an AXIOM.** NEW is the typed split refined to "the smallest candidate whose row
     holds no off-type cell in a data column". In § 2.1 it is wrong only on the bfs `2010 2` fragment
     ([[R242]]), where OLD is already wrong. Arguably it is a second rule, against CLAUDE.md § 8's
     "one geometric attempt, then NEURAL". It is typed, not geometric, and has no constant, so the
     ruling is the maintainer's to apply, not the agent's.
   - (b) **A reshaped question,** asked per line ("is L*k* header or data?") rather than as a count.
     `baml_src/header_rowrole.baml` exists. It was **not** measured here. The prediction to run
     before any spec relies on it: it answers 3 header lines on GERALDTON's r2 band and the right
     count on graincorp-stem p0/p1.
   Either way, the oracle of § 2.4 stays useful as the disposer.
3. **ASSERTED:** do not write the draft spec into the repo. Its design is summarised in § 1 so it is
   not lost. Its trigger and oracle survive. Its proposer does not.

## 1. What was attempted

The design drafted under the floor in this session, following the strategy review's default arm
(`2026-10-05-r289-seam-measured.md` § 5), had three parts:

- **Trigger (AXIOM):** ask only when the typed split's row `S` holds an off-type, non-abstaining
  cell in a data column.
- **Proposer (NEURAL):** the shipped `CountHeaderLines` reader, unchanged, asked on the
  hierarchical path with a listing built from `headers._grid_cells` in `listing_of`'s format.
- **Disposer (AXIOM, one-way):** admit `K` iff `K > S`, row `K` holds no off-type cell (R1), and
  rows `S…K-1` hold no body-typed cell (R3). Otherwise `S` stands.
- **Scope:** `compile.py`'s `classify_hierarchical` call site only, recorded as a `header_split`
  decision.

## 2. Findings

These were measured by a subagent at `66b15a7` (`src/` identical to `main` `6ed16d7`). Each compile
ran in its own process, serially. Scripts and two recorded outputs are in
`scripts/r289_split_blast/reader_probe/`; run outputs go to `reader_probe/out/` (not committed). The
harness returns OLD, so the scores match the baseline: cbh 1.0, gstem 0.99955, gcap 1.0,
ons 0.86849, bfs 0.90214, apple 0.94186, who 0.99628.

### 2.1 The trigger population after #303: 15 band keys (RUN)

| doc | trigger keys | OLD → NEW | line moved into the header |
|---|---|---|---|
| cbh | 8 (4 rosters × 2 passes) | 7→8, 4→5, 5→6, 4→5; r2: 2→3 ×4 | `Accepted Accepted Completed Completed` |
| ons | 4 (p7 ×2, p8 ×2) | 1→2 | the CDID line `S222 S243 KI77 …` |
| bfs | 3 | 1→2 ×2 keys; 2→3 | `2011 3 7 870 …` (R242, ✘); `au 1er janvier …` |

- gstem, gcap, apple and who: 0. After #303 the two R265 bfs bands (`Berne`, `Bâle-Ville`) no longer
  trigger.
- `header_body_split` has 7 callers: `_build_ruled_band`, `document.leaf_block`,
  `matrix.is_matrix_candidate`, `matrix.classify_matrix`, `rowheaders.stub_data_split`,
  `rowheaders.looks_row_grouped` and `hierarchical.classify_hierarchical`. **No bfs trigger reaches
  `classify_hierarchical`.** The cbh and ons triggers do. Per-band detail is in `m1-analysis.txt`.

### 2.2 The shipped reader undercounts stacked headers, stably (RUN, live Haiku 4.5, ×3 per band)

| band | OLD | NEW | answers |
|---|---|---|---|
| cbh GERALDTON / KWINANA / ALBANY / ESPERANCE (p0) | 7 / 4 / 5 / 4 | 8 / 5 / 6 / 5 | 6 / 3 / 5 / 4, each ×3 |
| cbh r2 rosters ×4 | 2 | 3 | 2 ×3 on each |
| ons ×4 | 1 | 2 | 2 ×3 on each ✔ |
| bfs `2010 2` ×2 keys | 1 | 2 | 0 ×3 (no header) |
| bfs boxhead `ee5a083ef386` | 2 | 3 | 2, 2, 3 (unstable) |
| **control** gstem p1 / p0 (hierarchical) | 3 / 4 | = | **2 / 3, each ×3: wrong** |
| control apple ×2 (hier), apple two-line, who Z-scores ×2 | = | = | equal to OLD ✔ |

- The reader is stable: 22 of 23 bands give the same answer three times.
- It is **low by 1–2 lines on every cbh roster and on both graincorp-stem controls**.
- Its notes call the r2 rosters a "two-level header".
- In the crop, each `Time Nom` / `Accepted` stack renders as one wrapped cell inside one visual
  header row. That is a plausible reason for the undercount. It was **not tested**.

### 2.3 Even the right split breaks cbh: the header tree overlaps (RUN)

`header_body_split` was forced to return NEW **only** when called from `classify_hierarchical`, and
cbh was compiled end to end:

- **Score 1.0 → 0.6929.** The baseline control run in the same harness gives 1.0.
- All four p0 rosters are superseded with `REGION_TILING_FAILED`. An adoption pass mints
  `p0/adopt#p0-datagrid`, plus a `DATAGRID_RESIDUE` escalation. No `#htable1/3/5/7` survives.
- A wrapper on `tiling.region_tiles` shows every roster region failing:
  - p0 and adopt: `tab:NoOverlapShape`, *"Two header nodes at the same level cover the same
    column"*;
  - r2: `NoOverlapShape` plus `tab:UnambiguousAccessShape`.
  - Only the first 3000 characters of each report were read.
- `merge_tiling_ok` returned True on all 12 calls.
- `resolve_ruled_header_rows` still returns None at the moved `body_line`, which matches
  `2026-10-05-r289-split-on-a-line-with-no-data.md` § 2.3.
- The baseline reproduces R289: carried rows 11/17/15/6 against 10/16/14/5 vessel rows, `r0` =
  `Accepted`/`Completed`, and labels `Time Nom` / `Date Nom` / `Date Loading` / `Time Loading`.

**So R289 is two defects in series:** the split (§ 2.1 of the seam note) and the tree.

### 2.4 The oracle refuses every wrong answer it was shown (RUN, `m3.txt`)

R1 ("row K holds no off-type cell in a data column") refuses:
- every cbh reader answer (the row the reader calls body holds `Accepted` or the main label line);
- both wrong gstem answers.

It admits the ons answers and every sound control. On who's [[R166]] headerless band, `K = 0` is
R1-clean and is refused only by the `K > S` clause. **The disposer worked. The proposer is what
failed.**

## 3. Decided, and where

Nothing was decided by the maintainer this session. The following are agent conclusions, recorded
here and in R289's register row:
- The `CountHeaderLines` count is refuted as R289's proposer (§ 2.2).
- R289 is blocked behind the header tree (§ 2.3).

## 4. Unverified or assumed

- Why the reader undercounts. The wrapped-cell reading of the crop is an inference from one image.
- Which tree nodes overlap, and why (§ 5, action 1).
- Whether `header_rowrole.baml` answers better. Not run.
- The bfs `Word.page` oddity: `bc099aefff2a` has words on page 0 but compiles at page 5. It is still
  unexplained.
- The ons and bfs-boxhead verdicts ("header ink ✔") are text readings, not renders.

## 2b. Where the primaries are

- `scripts/r289_split_blast/reader_probe/`:
  - `harness_m1.py` + `run_m1.sh` (M1), with `analyse_m1.py` → `m1-analysis.txt`;
  - `select_bands.py` → `bands.json`, then `m2_reader.py` + `run_m2.sh` (live reader);
  - `m3_oracle.py` → `m3.txt`;
  - `m4_counterfactual.py` + `run_m4.sh` / `run_m4b.sh` (forced NEW, end to end).
  - Run outputs land in `$S`, which defaults to `reader_probe/out/`.
- Live calls need `BAML_LIVE=1` and the API key prefix recorded in the `neural-worker` notes.
  Never set `ILADUB_RECORD_READINGS`.
- `src/iladub/etkl/headers.py` (`infer_header_tree`, `header_body_split`, `_grid_cells`),
  `hierarchical.py`, `compile.py:1699`.
- The seam note: `2026-10-05-r289-seam-measured.md`.
