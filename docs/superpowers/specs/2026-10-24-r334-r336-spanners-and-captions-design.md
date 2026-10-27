# R334 + R336: a grid's spanners and its own caption lines, disposed and carried (design, 2026-10-24)

**Serves:** maintenance — closes [[R334]] and [[R336]] together, measured on Fed H.4.1 table 1 by the
truth scorer of `prog:criterion:tab:13` (already met; this loop moves its number, it does not meet it).

**Doc impact: increment.** A grid gains spanner header nodes and caption nodes, the corpus baseline
moves, and one recordings directory is added. No released meaning changes.

**Status: APPROVED by the maintainer 2026-10-24 (both §8 decisions accepted as proposed).** §8 lists the two decisions that belong to the
maintainer. The design comes from the twelfth-session section of
`docs/superpowers/2026-10-22-ground-truth-set-handoff.md` (PR #371). It changes two things there,
marked **CHANGED** in §3.

## 1. Goal

Fed H.4.1 p0 adopts its grid. The truth scorer then reads column paths that start with the author's
spanners, for example `Averages of daily figures › Week ended Jan 1, 2025`. Two things block that
today, and both are measured:

- **R334.** A disposed spanner is reported and never carried. `carried_lines` counts only leaf words
  (`src/iladub/etkl/boxhead.py:306-314`), and `emit_boxhead` emits only leaves, all at level 0
  (`:316-343`).
- **R336.** L5 (the title) and L6 (`Millions of dollars`) share band 2 with the boxhead. Once the
  grid reads that band, the band counts as touched and its unread lines become residue
  (`adoption.build_ledger`). Spanners alone give a ledger of 38 against a page total of 31, which
  refuses. Spanners plus L5 and L6 give 27, which adopts (residue row R336, offline probe).

## 2. Measured before this spec (2026-10-24, `origin/main` at `4face0d`)

- **The tree passes the shapes that bind a grid.** A scratchpad graph of Fed p0's proposed tree
  (§3.2) was built in the grid's real vocabulary (`tab:DataGrid`, `tab:hasGridColumn`,
  `tab:GridColumn`) and validated against `vocab/shapes/tab-shapes.ttl` (pySHACL, `rdfs`, `advanced`):
  `conforms=True`. A control with the same seven nodes, all at level 0 and with no parents, fails with
  `Two header nodes at the same level cover the same column (overlap).` So the handoff's refutation
  clause did not fire, and the shapes do bite.
- **On a grid, the membrane checks less than the handoff assumed.** Grid columns are
  `tab:GridColumn`, which is deliberately not a `tab:LeafColumn` (`vocab/ontology/tab.ttl:99-102`).
  So `CoverageShape` (`tab-shapes.ttl:14`) and `UnambiguousAccessShape` (`:130`) never target a grid's
  columns. On a grid only `NoOverlapShape` (`:40`) and the refinement shape (`:60-72`, child ⊆
  parent) bind. A column covered by two childless nodes at *different* levels would pass the
  membrane. **Consequence:** the laminar check in §3.1 is the only thing that keeps a grid's column
  paths unambiguous. Under CLAUDE.md § Producer-side guards (R89) it may never be deleted as a
  duplicate, because no membrane covers what it checks.
- **Blast radius of R334.** 11 of the 23 recordings in `readings/boxhead/` carry at least one
  spanner (4, 4, 4, 3, 2, 2, 1, 1, 1, 1, 1). The handoff said there were 24 recordings; there are 23.
  Every one of the 11 can start carrying lines and moving its page's ledger.
- **Fed p0's reading** (handoff, twelfth section, *Measured*): 7 columns that tile exactly. Leaves on
  cols 0, 1 and 6. Spanners (1,5) L7, (2,5) L8, (2,3) L10 and (4,5) L10. L0–L6 are filed entirely as
  `other_words`. `header_block` = page lines 0..10.

## 3. Design

### 3.1 Spanner disposal (R334, the oracle)

`dispose_boxhead` already disposes leaves. Spanners get two exact checks with no tolerance. A leaf
takes part in (a) as a one-column node placed on its topmost line.

- **(a) LAMINAR.** Any two nodes have column sets that are either disjoint or nested. A node on a
  lower line nests inside every overlapping node above it. Two spanners on one line with equal sets
  violate this. **CHANGED from the handoff:** a violation drops *every spanner* of the reading, and
  the leaves are kept. The handoff said to refuse the whole reading. For any of the 11 recordings with
  spanners (§2), that would withdraw the leaf labels emitted today because of spanners nothing
  carries yet. That is a regression this loop does not need. Dropping the spanners leaves exactly the status quo.
- **(b) EXTENT ⊆ GROUP.** On every line, a spanner's ink extent lies inside
  `[columns[first].x0, columns[last].x1]`. A violation drops that spanner only. This is exact because
  grid columns tile with no gaps. It catches a group that is too narrow. **It cannot catch one that is
  too wide.** Only the truth scorer sees that, and §7 records it.

A spanner that is dropped leaves its line uncarried, which is the status quo. A refusal never
fabricates anything.

### 3.2 Spanner carriage

- `carried_lines` counts a surviving spanner's words as kept.
- `emit_boxhead` emits one `tab:HeaderNode` + `tab:LabelCell` per surviving spanner. The node carries
  `coversColumn` over first..last and `parentHeader` to the innermost spanner that contains it. Its
  label text is read back from the text layer, and its box is the union of its words (R179), exactly
  as a leaf's is.
- **Levels.** A root has level 0, and a node has level = its parent's level + 1. A leaf's parent is the
  innermost surviving spanner that covers its column. A leaf with no such spanner keeps level 0, so a
  reading with no spanners emits exactly the triples it emits today.
- On Fed p0 this gives L7 = 0, leaves col 0 and col 6 = 0, L8 = 1, leaf col 1 = 1, and both L10
  spanners = 2. The scorer takes the deepest node that covers a column and walks `parentHeader`
  (`src/iladub/feed.py:790-823`). Col 2 has no leaf, so it reads
  `Averages of daily figures › Change from week ended › Dec 25, 2024`.

### 3.3 The caption worker (R336, a separate NEURAL worker)

**Why a separate worker and not a wider `ReadBoxhead`:** a recording is keyed on
`sha256(ncols, listing)` (`boxhead.py:254`), not on the prompt or the schema. A wider question would
replay all 23 recordings as answers to a question that is no longer asked. Re-recording them reopens
R335's drift.

- **When it is asked.** Once per grid, after boxhead disposal, and only if the header block has
  *candidate lines*. A candidate line is one whose every word the disposed boxhead filed as
  `other_words`, and which no surviving spanner touches.
- **The question.** *Which of these lines are this table's own caption: its title, its unit line?*
  The worker sees the crop that `read_grid_boxhead` already renders, plus a numbered listing of the
  candidate lines only.
- **The answer.** A strongly typed, closed shape: `{caption_lines: int[], refuses: bool}`. It holds
  candidate indices only and never any text, so it cannot return a value from the page.
- **Disposal (oracle).** Every index is a candidate. The set is non-empty and contiguous in page
  order. Its last line is the text line directly above the topmost line that holds a surviving label
  (leaf or spanner). Anything else means NO CLAIM, which is the status quo.
- **Carriage.** Each disposed line joins `carried_lines` and is emitted as a `tab:RegionCaption`
  **only**, never a `tab:SectionCaption`. `feed.py:426-458` turns SectionCaption text into concepts,
  and the scorer would count those as SPURIOUS riders. Text and page are required (R218), and the box
  is the union of the line's words. Precedents: the box title bar (`compile.py:291-300`) and
  row-role furniture (`rowrole.py:219`).
- **Recording.** Under `readings/caption/`, keyed on `sha256("caption\n" + ncols + listing)`. It
  replays offline and is disposed again on every compile, exactly as `RecordedBoxheadReader` does
  (`boxhead.py:268-292`).
- **Units stay text.** Scale, currency and QUDT are not read, because neither the truth nor the scorer
  reads a unit (handoff, twelfth section). This becomes a new residue row.

### 3.4 Order at the adoption site

At `compile.py:2059-2066`: read the boxhead, then dispose its spanners, then ask the caption worker,
then build `carried_lines` over leaves, spanners and captions. The ledger and the R290 multi-grid union
do not change.

## 4. Gate classification (CLAUDE.md § 8)

| decision | class | why |
|---|---|---|
| which words are a spanner, and which columns it groups | NEURAL (existing `ReadBoxhead`) | a reading judgment, already proposed and recorded |
| laminar, extent ⊆ group | PROCEDURAL, disposal | exact interval comparisons over the grid's own tiling, with no constant. Irreducible because the oracle compares numbers |
| parent and level | PROCEDURAL, emission | a deterministic function of the disposed sets, with no judgment |
| which lines are the table's own caption | NEURAL (new worker) | *what a title is* is a reading judgment, never line position |
| caption disposal | PROCEDURAL, disposal | address-space, contiguity and adjacency checks, all exact |

No tuned constant appears anywhere. A geometric heuristic for captions (for example "the lines above
the boxhead") is forbidden by the 2026-09-17 ruling. This design makes no geometric attempt at all.

## 5. Tests (each carries a FALSIFICATION in its task report, per plan rule 4)

1. **Laminar refusal drops spanners only.** A synthetic reading with crossing spanners keeps its
   leaves, drops every spanner, and leaves `carried_lines` as it is today.
2. **Extent too narrow drops that spanner only.**
3. **The tree.** Fed p0's recorded reading emits 7 header nodes with the levels and parents of §3.2,
   and the page graph conforms to `tab-shapes.ttl`.
4. **No-spanner identity.** A reading with no spanners emits byte-identical triples to `main`.
5. **Caption disposal.** Out-of-range, non-contiguous, and not-adjacent answers each return NO CLAIM.
6. **Fed p0 end to end (offline, recorded).** p0 adopts, and the ledger escalates fewer than 31
   tokens. The probe gave 27, and the plan pins the exact number it measures. `truth.table-1` reports
   `CORRECT` > 0.

## 5a. What is NOT done

- Unit semantics (scale, currency, QUDT).
- R335 (an omitted leaf label).
- Re-recording any existing boxhead reading.
- `UnambiguousAccessShape` for grids, meaning a membrane that sees ambiguous column paths on a
  `tab:GridColumn`. §2 shows the gap, and a new residue row records it.
- A census of other documents with the title-in-touched-band shape. The caption worker is asked
  wherever candidate lines exist, but it answers only where a recording exists (§8).

## 6. Arc criterion

None proposed. `tab:13` is already met, and this loop moves its number.

## 7. Unverified

- **The seam the plan must measure first:** `tab:hasCaption` has `rdfs:domain tab:Table`
  (`tab.ttl:579`), and `tab:DataGrid` is not declared a `tab:Table` in this vocabulary (grep found no
  such axiom). Under `inference="rdfs"` a caption edge would type the grid as `tab:Table`, which may
  pull it into shapes that target tables. The plan measures this on a real page graph *before*
  choosing the edge.
- Whether carriage for real reproduces the probe's ledger of 27.
- How the sign sub-columns (2 and 4) score against a truth path. They share their spanner with the
  number columns (3 and 5).
- A group that is too wide passes (b). Only the scorer sees it.
- Whether the caption worker over-claims band-1 masthead lines (L0–L4) on Fed. Contiguity ending at
  L6 admits {L6}, {L5, L6} and {L0…L6}. All three adopt (probe: carrying everything gives a ledger of
  9). The masthead would then be carried as this table's caption, which is wrong but harmless to the
  scorer, much like the too-wide group.

## 8. Approval: the maintainer's decisions

1. **Live recording budget for the caption worker.** Recording it for Fed p0 alone would make the
   feature work only on the document it was built for, which the no-overfitting rule forbids. The
   proposal is one live sample per grid that has candidate lines, across `corpus/` and `held-out/`,
   recorded once (`BAML_LIVE=1 ILADUB_RECORD_READINGS=1`). The count of such grids is the plan's
   first measurement.
2. **§3.1's change:** a laminar violation drops the spanners, not the whole reading.

**Ruled 2026-10-24 by the maintainer:** (1) accepted. One live caption-worker sample per grid with
candidate lines, across `corpus/` and `held-out/`, recorded once. (2) accepted. A laminar violation drops
the spanners and keeps the leaves.

## 9. Amendment, 2026-10-24: ship as is (the maintainer's decision)

§5 item 6 was refuted at plan Task 5. The caption worker's recorded answer on Fed H.4.1 p0 is lines
{1, 5, 6}: `H.4.1` from the band-1 masthead, the title and `Millions of dollars`. It is not
contiguous, so the §3.3 disposal refuses it (NO CLAIM). The caption lines stay unread, the ledger
books 38 > 31, and p0 does not adopt. Plan Task 6 Step 2 said to stop rather than tune. Three options
were put to the maintainer: (a) ship as is, (b) a revised prompt plus one re-ask, (c) an oracle that
admits the maximal contiguous run ending at the labels. **The maintainer chose (a).**

§5 item 6 is therefore replaced by the following, in `tests/etkl/test_r334_r336_fed_p0.py`:

- As recorded, p0's adoption is `ledger_refused`, at 285 asserted and 31 escalated.
- As a control, the only change is that one recording replaced by {5, 6} in a scratch copy of
  `readings/caption/`. p0 then adopts at 336 asserted and 27 escalated, which is the probe's
  prediction exactly, with the title and the unit line carried as `tab:RegionCaption`. The caption
  answer is the one remaining blocker.

`truth.table-1` stays at `CORRECT: 0`, and `floor.json` is unchanged. The over-claim is residue R340.
R336 stays open, and R334 closes.
