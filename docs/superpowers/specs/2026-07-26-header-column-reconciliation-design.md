# Header→column reconciliation — body-grounded covering partition (Loop B)

- **Date:** 2026-07-26
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Second loop of the GrainCorp real-document capability push. **SCOPE REVISED during implementation (2026-07-26): Cause A only.** Cause B (caption peel) was found to be an **unsound geometric problem** — a leaked caption line and a genuinely-ambiguous off-center merge are structurally identical (both are overlapping top rows), so every geometric peel that removes the caption also silently asserts an off-center merge that must escalate (breaks the shipped `test_offcenter_merge_escalates` / B1.3 / span-gate contracts). "Is this line a title/date furniture, or a header?" is a **semantic/NEURAL judgment**, deferred to a dedicated propose→oracle→dispose loop (see §7). Loop B ships Cause A; GrainCorp still escalates on the caption line, named as residue.
- **Context:** After Loop A fixed the header/body split (48→4, PR #67), re-measuring the real-world **GrainCorp Shipping Stem** report shows `compile_tables` still escalates the main table (`UNSUPPORTED_TABLE` / `MERGE_AMBIGUOUS`) — now **downstream** of the split, on the hierarchical header-tree path. `classify_hierarchical` builds a header tree with **overlapping covers** (not coverage gaps), so `merge_tiling_ok` returns False. Two independent, confirmed causes (each alone leaves it escalating):
  - **Cause A (dominant):** the leaf grid has 17 columns inferred from the *data* rows, but `_covers_for_cell` attributes each header label's span by **ink extent under a "Merge & Center" assumption**. Wide *single-column* labels get over-spanned — `Reference Number`→covers(1,2,3), colliding with `Month`→(1) and `Exporter`→(3) → same-level overlap → cannot tile. This blocks even a clean single header row.
  - **Cause B (secondary contamination):** a leaked caption/date line `Friday, 24 July 2026` and a wrapped fragment `Date of Grain` sit inside the header region `[0,split)` and are modeled as spurious level-0/1 nodes (`Friday, 24`→covers 1..13, `July 2026`→col 7), adding more overlaps.

---

## 1. Purpose and scope

Make the hierarchical header tree's **leaf covering** correct for real reports whose header is a wrapped, multi-word structure over a body-derived column grid: the covering becomes a **body-grounded, gate-clean AXIOM** (an evidence-positive SPARQL derivation over a header+grid evidence graph), no tuned constant. (The leading-caption contamination — originally Cause B — is deferred to a NEURAL loop; see the status note and §7.)

**In scope (Cause A only):**
- **Cause A — the covering partition.** A new header evidence graph (`iladub.etkl.headergraph`) + a SPARQL derivation (`vocab/queries/header-covers.rq`) that assigns each **leaf-row** header label the one column that **contains its ink center** — exact, no symmetrization. Parent rows keep the existing B1.1 centering-bounded run extension (`repair_coverage`) over the leaf partition.
- A differential oracle certifying the SPARQL leaf-covering against a fast python reference.
- Committed synthetic regression fixtures; the GrainCorp PDF as a local (uncommitted) real-world confirmation of the covering fix (the split's leaf covers no longer over-span).

**Non-goals (later loops):**
- **Cause B — caption / non-header-row exclusion (MOVED OUT, → NEURAL Loop C).** Distinguishing a leaked title/date/furniture line from a genuine header row is not soundly decidable from geometry (it is indistinguishable from an off-center merge — see §7); it becomes a dedicated NEURAL slice.
- **Row-grouping with suppressed keys + interleaved subtotals** (the `Mackay Total` / `Jul 26 Total` rows) — Loop C.
- **Split-number / word-merged data cells** (`2 0,000` should be `20,000`) — a data-side extraction concern, separate loop.
- The **NEURAL residual**: a wide label over *blank/unclaimed* body columns, where the partition genuinely cannot decide, still escalates honestly `MERGE_AMBIGUOUS`. GrainCorp does not need it.

**Success criteria (Cause A):**
1. A synthetic table with **wide single-column labels** over narrow columns (the `Reference Number` shape) tiles / **asserts** (was escalate) — the covering partitions without overlap.
2. A synthetic **genuine merged-parent** table (pivot shape) **still asserts with its hierarchy intact** — no regression; the leaf change only narrows over-spanned leaves, parents are untouched.
3. The differential oracle certifies `header-covers.rq` == the python reference over random grids.
4. On the real GrainCorp band (local spike), the leaf covering no longer over-spans (documented). GrainCorp still escalates on the **caption** contamination (Cause B, deferred) — that residual is expected and named, not a Loop-B failure.
5. **No regression:** every existing header/tiling/pivot test, `region_tiles`, the differential oracles, and the full suite stay green; all shipped pivot/hierarchical fixtures — including the off-center-merge / narrow-flank **escalations** — behave byte-identically.
6. **Gate:** the leaf covering is an evidence-positive SPARQL AXIOM (no constant, no symmetrization, no numeric literal); the parent path is the existing justified centering-bounded geometry; honest `MERGE_AMBIGUOUS` escalation preserved for genuinely ambiguous input.
7. Source-ownership clean (`tab:HeaderCell`, `tab:covers`, `tab:GridColumn` and their properties are owned `tab:` vocab); no third-party PDF committed.

---

## 2. Root cause (confirmed) and the fix

**Current derivation** (`_covers_for_cell` in `headers.py`): every header cell's cover is its **center column + symmetrized ink extent** (extend the shorter side to match the longer — the "Merge & Center" convention). This cannot distinguish, from header geometry alone:
- a **short** merged parent over a **wide** span (ink narrower than span → needs extension), from
- a **wide** single-column label over a **narrow** column (ink wider than the column → must NOT extend).

These are opposite failure modes; pure header geometry is genuinely underdetermined between them (the reason the prior "B2 general span" slice was dropped as NEURAL-unsound).

**The body removes the underdetermination, and the resolution splits by level:**
- **Genuine merged headers are PARENTS in upper rows; the LEAF (bottom) header row is 1:1 with body columns.** So at the leaf row, "how many body-column centers fall under this label's ink" is exactly the body evidence: a wide single-column label's ink contains **one** column center (its neighbours sit under their own labels); a genuine merged parent's ink contains **several** leaf-column centers (no competing label between them).
- **Leaf rule (AXIOM, evidence-positive) — CORRECTED during implementation (2026-07-26):** leaf label `L` covers the one column `C` that **contains L's ink center** (`C.colX0 ≤ centerX(L) < C.colX1`, half-open, mirroring `regions.column_of`). No symmetrization. Because grid columns are body columns, this is body-grounded, and it is the faithful realization of "the leaf row is 1:1 with body columns" (a leaf label sits in exactly one column). *(The originally-designed "column center ∈ label ink" predicate was empirically wrong: 26 existing fixtures use left-aligned leaf labels whose ink does not reach their own column center, so they got zero coverage; and the Voronoi fallback added to rescue them mis-assigned a column already owned by a childless "short parent." Label-center-in-column fixes the wide-label bug identically, covers left-aligned labels correctly, leaves short-parent columns alone, and needs **no fallback** — verified full suite 548 passed.)*
- **Parent rule (unchanged):** a parent covers the contiguous run of leaf columns under its ink via the B1.1 centering-bounded `repair_coverage`, so `Q1`/`Prior Visit`-style pivots keep spanning correctly, bounded by the leaf partition (a parent never claims a leaf's column).

**Caption (Cause B) — deferred (NEURAL).** The caption/fragment rows do not partition-align and their inclusion breaks tiling, but *removing* them cannot be done from geometry alone: a caption row and a genuinely-ambiguous off-center merge are both overlapping top rows, so any peel that drops the caption also drops (and silently asserts) an off-center merge that must escalate. Deferred to a propose→oracle→dispose loop (§7).

---

## 3. Components

### 3.1 `src/iladub/etkl/headergraph.py` (new) + `vocab/ontology/tab.ttl`
- `header_evidence(header_rows, grid) -> Graph` — a fresh per-band `Graph()` (the band is the closure boundary, as in B2c `classifygraph`): one `tab:HeaderCell` per header cell with `tab:atHeaderRow` (int), `tab:cellIndex` (int), `tab:headerText` (string), `tab:inkX0`/`tab:inkX1` (float ink extent), `tab:inkCenterX` (float ink midpoint — raw geometry); and one `tab:GridColumn` per leaf column with `tab:colIndex` (int), `tab:colCenterX` (float), and boundaries `tab:colX0`/`tab:colX1` (float).
- A thin runner (reuse the `celltype.run_scalar`/`grid_evidence` pattern; a `run_covers(rq, graph) -> dict[int, tuple[int,...]]` reader returning, per header-cell row-index/id, its covered column indices).
- `vocab/ontology/tab.ttl`: declare `tab:HeaderCell a owl:Class`, `tab:GridColumn a owl:Class`, and properties `tab:atHeaderRow`, `tab:cellIndex`, `tab:headerText`, `tab:inkX0`, `tab:inkX1`, `tab:inkCenterX`, `tab:covers` (HeaderCell→GridColumn), `tab:colIndex`, `tab:colCenterX`, `tab:colX0`, `tab:colX1` — owned `tab:` vocab. (Confirm none already exist with a conflicting definition — the B2c lesson: grep the target ttl before adding.)

### 3.2 `vocab/queries/header-covers.rq` (new, AXIOM)
Derives leaf-row coverage: for the leaf header row (the max `atHeaderRow` present, i.e. the row adjacent to the body), a leaf cell covers the column whose half-open `[colX0, colX1)` contains the cell's `inkCenterX`: `SELECT ?hrow ?cellIdx ?cidx WHERE { { SELECT (MAX(?r) AS ?leaf) WHERE { ?hc a tab:HeaderCell ; tab:atHeaderRow ?r } } ?cell a tab:HeaderCell ; tab:atHeaderRow ?hrow ; tab:cellIndex ?cellIdx ; tab:inkCenterX ?center . FILTER(?hrow = ?leaf) ?gc a tab:GridColumn ; tab:colIndex ?cidx ; tab:colX0 ?cx0 ; tab:colX1 ?cx1 . FILTER(?cx0 <= ?center && ?center < ?cx1) }`. Evidence-positive, open-world, no threshold, and **no numeric literal** (the midpoint is `tab:inkCenterX`, emitted by `headergraph.py`, so the query passes `test_transform_gate.py::test_no_tuned_constant_in_rq_files`). The load-bearing comment explains the leaf-vs-parent split.

**Uncovered-column edge (honest):** a leaf column whose center is not contained in any leaf cell's column — i.e. a column with no leaf label of its own — stays uncovered at the leaf level. This is correct: it is either a terminal **short parent** column (covered by a shallower node, as in the all-text `hrule` fixture's `Name`) or a genuine gap that correctly fails to tile → honest escalation. Because the rule assigns by the label's own center (not by ink reaching a column center), ordinary **left-aligned** leaf labels are covered without a fallback. *No Voronoi fallback is used* (the originally-designed center-in-ink rule needed one; label-center-in-column does not — verified full suite 548 passed).

### 3.3 `src/iladub/etkl/headers.py` (integration)
- `infer_header_tree`: for the **leaf row**, build each cell's `covers` from `header-covers.rq` (via `headergraph`) instead of `_covers_for_cell`; for **parent rows**, keep `_covers_for_cell` + `repair_coverage` unchanged. `_covers_for_cell` remains for the parent path (justified PROCEDURAL, oracle-disposed).
- **Caption peel — REMOVED from scope (see status note + §7).** A maximal-tiling-suffix peel was implemented and reverted: it cannot distinguish a caption from a genuinely-ambiguous off-center merge (both are overlapping top rows), so any peel that drops the caption also silently asserts an off-center merge that must escalate. Header-row assembly is left unchanged (`infer_header_tree` returns the full-header tree; the caller escalates as before). Caption exclusion is deferred to a NEURAL loop.
- `merge_tiling_ok` / `region_tiles` (the closed-world membrane) are **unchanged**.

### 3.4 `tests/etkl/test_derivation_equiv.py` (extend)
Add a differential oracle: the shipped `header-covers.rq` leaf-covering == a fast python reference (`_ref_header_covers`: a leaf cell covers the column whose `[b[i], b[i+1])` contains its ink center) over random header/grid shapes (wide labels, gaps, single-column labels). Certifies the AXIOM.

---

## 4. Testing

- **Committed failing tests (TDD), synthetic, domain-neutral:**
  - **Wide single-column labels** (`tests/etkl/…`): a flat record table (e.g. columns `Month | Port | Reference Number | Exporter` where `Reference Number`'s label ink is wider than its narrow data column) → asserts a record table, no `MERGE_AMBIGUOUS`. Fails on current (symmetrizing) code, passes after.
  - *(Leading-caption fixture — dropped with Cause B; caption handling is a NEURAL loop.)*
  - **Genuine merged parent (regression guard):** a pivot-shaped table with a real 2-level header (`Prior Visit` spanning 2 leaf columns) → still asserts with the parent spanning correctly and the hierarchy intact. Must pass before *and* after (guards against the leaf change breaking real merges).
- **Differential oracle:** `header-covers.rq` == `_ref_header_covers` over random grids (§3.4).
- **Real-world confirmation (local, not committed):** re-run `compile_tables` on the GrainCorp PDF and record that the main table asserts `tab:HierarchicalTable` with score > 0 and records > 0 (was `MERGE_AMBIGUOUS`, 0 cells). PDF stays in the scratchpad.
- **No regression:** full suite; confirm every existing header/tiling/pivot test, `region_tiles`, `test_derivation_equiv`, and all shipped hierarchical/matrix fixtures assert byte-identically.

---

## 5. Neurosymbolic gate & discipline

- **AXIOM, not NEURAL (the reclassification):** with body evidence (leaf headers are 1:1 with body columns), "which columns does a leaf label cover" is a *derivation* over the header+grid evidence graph — evidence-positive, open-world, realized as SPARQL `SELECT`. This is the sound answer the prior NEURAL framing lacked; it dodges the "LLM replaces geometry" trap. NEURAL remains the fallback for the genuine residual (wide label over unclaimed/blank columns), deferred.
- **No tuned constant / no overfit:** the leaf rule is `colX0 ≤ inkCenterX < colX1` (a containment test, not a tolerance; the query carries no numeric literal); the parent path is the pre-existing centering-bounded geometry (`0.5·pitch` tolerance is derived, not tuned — unchanged). Validated on synthetic fixtures + the differential oracle, not tuned to GrainCorp bytes. (Caption peel was removed precisely because a geometric threshold could not soundly separate it from a real escalation — honest failure over a fake heuristic.)
- **Constraint stays SHACL, open/closed split intact:** `merge_tiling_ok` / `region_tiles` remain the closed-world membrane disposing what may cross; the covering derivation is the open-world growth. The **holon (band) is the closure boundary** (fresh per-band evidence graph).
- **Source ownership:** `tab:HeaderCell`/`tab:GridColumn`/`tab:covers`/`tab:atHeaderRow`/`tab:cellIndex`/`tab:headerText`/`tab:inkX0`/`tab:inkX1`/`tab:inkCenterX`/`tab:colIndex`/`tab:colCenterX`/`tab:colX0`/`tab:colX1` are owned `tab:` vocab; no HGA/Fluree terms. No third-party PDF committed.
- **Honest failure preserved:** genuinely ambiguous input (no tiling suffix) still escalates `MERGE_AMBIGUOUS` — credibility over completeness (§7).

---

## 6. Relation to prior work and steering

- Direct outcome of re-measuring GrainCorp after Loop A (PR #67). Second loop of the evidence-driven real-document push: fix the covering + caption → re-measure → the next exposed gap (row-grouping/subtotals, or split-number cells) defines Loop C.
- **Reopens and reclassifies the dropped "B2 general merged-header span":** the prior drop was correct *for a header-geometry-only NEURAL framing*; the body/sibling evidence turns it into a sound AXIOM. Resurrects the `tab:HeaderCell` evidence-graph idea (built then removed in B1.2) for a genuine, non-redundant purpose.
- Aligns with the shipped evidence-graph derivation family (celltype B2a/B2b, classify-kind B2c): a fresh per-band evidence graph + a holon-scoped SPARQL derivation + a differential oracle.
- The parked `iladub-zero-etl-showcase` branch can gain GrainCorp as a *win* example once this loop closes.

---

## 7. Open questions / later loops

1. **Caption / header-vs-furniture (the deferred Cause B) — a NEURAL loop.** Deciding whether a header-region line is a leaked title/date/furniture line or a genuine header row is not soundly geometric: a caption and an off-center merge are structurally identical (overlapping top rows), so a geometric peel breaks the off-center-merge / narrow-flank escalation contracts. The sound shape is **propose→oracle→dispose**: a BAML proposer classifies each header-region row (header vs furniture), the tiling membrane (`merge_tiling_ok`/`region_tiles`) disposes the resulting tree, and the exclusion is admitted only as a proposition per §3. Design the oracle first (the recurring lesson). Could also inform band segmentation (excluding furniture at `detect_bands`) rather than only at header-tree assembly.
2. **Loop C:** row-grouping with suppressed keys + interleaved subtotals (`Mackay Total`, `Jul 26 Total`) as first-class structure.
3. **Split-number / word-merged data cells** (`2 0,000` → `20,000`): a data-side extraction concern (cf. the border-aware char re-extraction), likely PROCEDURAL, its own loop.
4. **NEURAL residual:** a wide label over blank/unclaimed columns where the partition cannot decide — the genuine perceptual slice, via the `span_proposer` seam, if a real document ever needs it.
