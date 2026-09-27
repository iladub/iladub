# Evidence: an admitted arm-A extent does not reach the score — the loss is roles, not extent (2026-09-27)

**Serves:** maintenance — runs the "proposed, minutes to refute" action in part 5 of
`2026-09-27-box-as-extent-rescore-evidence.md` before any arm-A spec is written.

**Topic:** jev-reading · **Date:** 2026-09-27 · **src measured:** `8db0d03`

**Doc impact: none.**

## 5. Next action

- **Asserted:** the section-4 slice of the question-compiler spec is **not** extent reading by
  arm A. The brainstorm resumes at "present section 4" in the same session with a different slice.
- **Proposed, open to refutation:** section 4 is a **line-role slice** (round 3):
  - caption, source, note and masthead lines are *carried*, not escalated.
  - Each role is admitted only where an exact check exists:
    - a note mark matches a superscript in the admitted table exactly;
    - a caption label (`T3`, `Table n`) matches exactly;
    - a source line begins with a literal `Source:` / `Quelle:` / `Source :` token.
  - Refute it by counting how many of the escalated tokens listed below such checks can dispose.
    If the answer is few, the slice is wrong again.
- **Proposed, separate:** cbh's 80 escalated tokens are header words fused in extraction
  (`VNAVesseTimeDate`). That is word grouping, not a Jev judgement, and it may be its own slice.

## 1. Goal

Before choosing the slice, measure whether feeding an admitted extent into `compile_document`
moves the score of cbh or bfs.

## 2. Where the primaries are

- `internal/benchmarks/jev-2026-09-27/spike-A/reach_spike.py` (throwaway, untracked, beside the raw
  calls) and its output `reach_spike.jsonl`.
- It imports `ORACLE` from `spike.py` and monkeypatches `compile.page_bands` / `detect_bands`,
  plus, in arm A2, `segment.segment` and `trailing.cut_trailing_notes`.

## 3. What was decided, and where

- Maintainer, this session: run the reach spike before presenting section 4.
- Nothing else was ruled.

## Measured

**The protocol.**
- An arm-A admission is by construction *exactly* one drawn box (`ORACLE`). So forcing every box
  in as the page's extent is the **ceiling** of arm A on that page.
- Target pages: cbh p0 (6 boxes) and bfs p5 (2 boxes), the pages dev E admits.
- The arms:
  - **base** is HEAD.
  - **A1:** each box's words become one raw band, replacing `detect_bands` on that page. Words
    outside every box go through `detect_bands` as today.
  - **A2:** A1, with `segment` and `cut_trailing_notes` made identity on a box band.
- Runs were serial, one process per run, offline (recorded readings only).

| doc | base | A1 | A2 |
|---|---|---|---|
| cbh | 0.9095 (a 804 / e 80) | 0.8251 (a 750 / e 159) | = A1 |
| bfs | 0.9021 (p5: a 936 / e 76) | 0.8907 (p5: a 936 / e 94) | = A1 |

**Why the score does not move:**
- **cbh:** the four main tables assert identical cell counts (170 / 268 / 228 / 84) in every arm.
  The side-by-side pair at the foot (box 5 and box 6) goes from one RECORD_TABLE of 13 cells to
  two `MULTI_TABLE_AMBIGUOUS` escalations.
- **bfs p5:** both boxed tables fail (`ROUND_TRIP_FAIL`, `MATRIX_AMBIGUOUS`) in every arm and are
  superseded by the adopted page datagrid. That datagrid asserts 496 cells in every arm, so the
  band extent never reaches the output.
- A1 = A2 on both documents, so downstream splitting is not what undoes the extent.

**Where the escalated tokens actually are** (base, `tokens_escalated` per region):

| doc / page | region | reason | e | what it is |
|---|---|---|---|---|
| cbh p0 | 1, 3, 5, 7 (asserted) | — | 20 each = 80 | the repeated boxhead, words fused in extraction |
| bfs p0 | 0 | KIND_NOT_SUPPORTED | 6 | press-release masthead |
| bfs p4 | 0 | REGION_TILING_FAILED | 36 | chart captions G1/G2 |
| bfs p5 | 8 | REGION_TILING_FAILED | 20 | boxhead of the second table |
| bfs p5 | 15 | KIND_NOT_SUPPORTED | 39 | source / notes block |
| bfs p5 | 18 | DATAGRID_RESIDUE | 17 | residue |
| bfs p6 | 1 | KIND_NOT_SUPPORTED | 16 | `T3` title |
| bfs p6 | 11 | REGION_TILING_FAILED | 3 | source + footnotes |

- Every escalated token on both documents is either **a line role around a table** (masthead,
  caption, title, source, notes) or **a boxhead**.
- None of it is a table's extent.

## 4. Unverified or assumed

- **The spike's "drawn box" oracle is hand-transcribed.** `spike.py`'s `ORACLE` rectangles were
  transcribed from a render and the lead-2 rule census. They are not derived from the PDF's rules.
  An arm-A oracle in `src/` would need that derivation first. This is moot for the slice now, but
  it must not be cited as existing.
- **The score is blind to ignored ink** (`a/(a+e)`). A role slice that moves these lines from
  escalated to *ignored* would raise the score while reading nothing. A role must be carried: the
  caption onto its table as `tab:RegionCaption`, notes and sources as nodes with provenance.
- Only 2 of 7 documents were run. The breakdown for the others was not measured.
- The recorded boxhead readings key on a listing hash. Asserted counts were unchanged in every
  arm, so no reading was lost to a hash change, but this was inferred, not logged.

## Appended: the role-check count (same session, part 5's first proposed action)

**Method.**
- Each escalated region's lines were dumped from `page_bands`; the band word count equals
  `tokens_escalated` for every region except p5's DATAGRID_RESIDUE, which has no band.
- Caption labels were checked for references anywhere in the document (`pdfplumber` text,
  `\bT1\b` etc.).
- Note marks were checked for small-font characters (< 0.8 × the page's median char size) inside
  the tables they would attach to.

**Result.** 217 escalated tokens (cbh 80 + bfs 137):

| class | tokens | exact check available | kind of check |
|---|---|---|---|
| boxhead words (cbh ×4 fused; bfs p5 table 2) | 80 + 20 = **100** | none — header reading, not a role | — |
| footnotes (bfs p5: 34; bfs p6: 2 of the region's 3 merged words) | **36** | **yes**: every leading note digit (p5 1/2/3, p6 1/2) matches a small-font digit inside its table | independent: an author-drawn typographic mark |
| source line (`Sources:` p5, 5; `Source:` p6, 1) | **6** | a lexical derivation | not independent: the pattern proposes and decides |
| captions T3 (16), G1/G2 (20) | **36** | a label pattern only; **each label occurs exactly once in the document**, so there is no referent to match | not independent |
| masthead / footer (p0: 6; p4: 4 + 12) | **22** | none exact: the lines differ across pages (`OFS` appended, page number) | — |
| DATAGRID_RESIDUE (p5) | **17** | not diagnosed | — |

**Reading it:**
- An **independent oracle** covers 36 / 217 tokens (17%), all footnotes.
- Adding the lexical derivations (sources, caption labels), which need no model at all, raises it
  to 78 / 217 (36%).
- The single largest block is **boxhead reading: 100 / 217 (46%)**, and 80 of those are cbh's
  fused header words.
- The roles that have no check (masthead, footer, 22 tokens) are exactly where "no oracle, no
  worker" forbids a Jev worker.

**Unverified:**
- Whether a *carried* caption or note counts as asserted in `a/(a+e)` was not measured. If it
  does not, carrying roles moves ink out of `e` without adding to `a`, and part of the gain is the
  ignored-ink blindness described above.
- The upper bounds if everything in a class became asserted, computed only:
  - cbh 804 / 884 → 1.0 if its 80 header tokens are read;
  - bfs 1263 / 1400 → 0.928 (+36) or → 0.958 (+78).

## Next action, superseding part 5 (written before the context was cleared)

- **Asserted:** the role slice proposed in part 5 is refuted by the count above. Do not spec it.
- **Proposed, for the maintainer to rule (recommended by this session, not yet ruled):**
  - Section 4's first slice is **cbh's fused boxhead words**: 80 of 217 escalated tokens, and cbh
    → 1.0 if read (computed).
  - First, a short diagnosis that decides the tier:
    - are the words fused in *extraction* (pdfplumber / the ruled re-extraction in
      `_build_ruled_band`)? Then it is PROCEDURAL raw extraction, with no Jev.
    - or are they intact words that the reader then mis-groups? Then it is a NEURAL judgement,
      which needs an oracle first.
  - Refute it quickly: dump cbh p0's raw `extract_words` for the boxhead lines and compare them with
    the region's `ascii`.
