# Header→column reconciliation — body-grounded covering partition + oracle-disposed caption peel (Loop B)

- **Date:** 2026-07-26
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Second loop of the GrainCorp real-document capability push.
- **Context:** After Loop A fixed the header/body split (48→4, PR #67), re-measuring the real-world **GrainCorp Shipping Stem** report shows `compile_tables` still escalates the main table (`UNSUPPORTED_TABLE` / `MERGE_AMBIGUOUS`) — now **downstream** of the split, on the hierarchical header-tree path. `classify_hierarchical` builds a header tree with **overlapping covers** (not coverage gaps), so `merge_tiling_ok` returns False. Two independent, confirmed causes (each alone leaves it escalating):
  - **Cause A (dominant):** the leaf grid has 17 columns inferred from the *data* rows, but `_covers_for_cell` attributes each header label's span by **ink extent under a "Merge & Center" assumption**. Wide *single-column* labels get over-spanned — `Reference Number`→covers(1,2,3), colliding with `Month`→(1) and `Exporter`→(3) → same-level overlap → cannot tile. This blocks even a clean single header row.
  - **Cause B (secondary contamination):** a leaked caption/date line `Friday, 24 July 2026` and a wrapped fragment `Date of Grain` sit inside the header region `[0,split)` and are modeled as spurious level-0/1 nodes (`Friday, 24`→covers 1..13, `July 2026`→col 7), adding more overlaps.

---

## 1. Purpose and scope

Make the hierarchical header tree **tile** for real reports whose header is a wrapped, multi-word structure over a body-derived column grid, contaminated by a leading caption line. Both fixes are **body-grounded and gate-clean**: the covering becomes an **AXIOM** (an evidence-positive SPARQL derivation over a header+grid evidence graph); the caption exclusion is **oracle-disposed** (the tiling membrane decides which rows are real header rows). No tuned constant.

**In scope:**
- **Cause A — the covering partition.** A new header evidence graph (`iladub.etkl.headergraph`) + a SPARQL derivation (`vocab/queries/header-covers.rq`) that assigns each **leaf-row** header label the columns whose **center falls within its ink x-extent** — exact, no symmetrization. Parent rows keep the existing B1.1 centering-bounded run extension (`repair_coverage`) over the leaf partition.
- **Cause B — caption / non-header-row exclusion.** Build the tree from the **maximal body-adjacent contiguous suffix of header rows that yields a valid tiling**: if the tree fails `merge_tiling_ok`, peel the **top** header row and retry, down to the leaf row alone; keep the largest suffix that tiles. Genuine parent rows join the tiling and are never peeled; caption/fragment rows cannot join and are peeled. Disposed by the oracle, not a threshold.
- A differential oracle certifying the SPARQL leaf-covering against a fast python reference.
- Committed synthetic regression fixtures; the GrainCorp PDF as a local (uncommitted) real-world confirmation.

**Non-goals (later loops — this loop re-measures and may expose them):**
- **Row-grouping with suppressed keys + interleaved subtotals** (the `Mackay Total` / `Jul 26 Total` rows) — Loop C.
- **Split-number / word-merged data cells** (`2 0,000` should be `20,000`) — a data-side extraction concern, separate loop.
- The **NEURAL residual**: a wide label over *blank/unclaimed* body columns, where the partition genuinely cannot decide, still escalates honestly `MERGE_AMBIGUOUS` and is named as the future NEURAL slice via the existing `span_proposer` seam. GrainCorp does not need it.

**Success criteria:**
1. A synthetic table with **wide single-column labels** over narrow columns (the `Reference Number` shape) **asserts** (was escalate) — the covering partitions without overlap.
2. A synthetic table with a **leading caption/date line** above a real header **asserts** — the caption row is peeled by the tiling oracle.
3. A synthetic **genuine merged-parent** table (pivot shape) **still asserts with its hierarchy intact** — no regression; the leaf change only narrows over-spanned leaves, parents are untouched.
4. On the real GrainCorp band (local spike), the main table **compiles end-to-end** — asserts `tab:HierarchicalTable`/record cells with score > 0 and records > 0, not `MERGE_AMBIGUOUS` (documented; PDF not committed).
5. **No regression:** every existing header/tiling/pivot test, `region_tiles`, the differential oracles, and the full suite stay green; all shipped pivot/hierarchical fixtures assert byte-identically.
6. **Gate:** the leaf covering is an evidence-positive SPARQL AXIOM (no constant, no symmetrization); the caption peel is oracle-disposed (no constant); the parent path is the existing justified centering-bounded geometry; honest `MERGE_AMBIGUOUS` escalation preserved for genuinely ambiguous input.
7. Source-ownership clean (`tab:HeaderCell`, `tab:covers`, `tab:GridColumn` and their properties are owned `tab:` vocab); no third-party PDF committed.

---

## 2. Root cause (confirmed) and the fix

**Current derivation** (`_covers_for_cell` in `headers.py`): every header cell's cover is its **center column + symmetrized ink extent** (extend the shorter side to match the longer — the "Merge & Center" convention). This cannot distinguish, from header geometry alone:
- a **short** merged parent over a **wide** span (ink narrower than span → needs extension), from
- a **wide** single-column label over a **narrow** column (ink wider than the column → must NOT extend).

These are opposite failure modes; pure header geometry is genuinely underdetermined between them (the reason the prior "B2 general span" slice was dropped as NEURAL-unsound).

**The body removes the underdetermination, and the resolution splits by level:**
- **Genuine merged headers are PARENTS in upper rows; the LEAF (bottom) header row is 1:1 with body columns.** So at the leaf row, "how many body-column centers fall under this label's ink" is exactly the body evidence: a wide single-column label's ink contains **one** column center (its neighbours sit under their own labels); a genuine merged parent's ink contains **several** leaf-column centers (no competing label between them).
- **Leaf rule (AXIOM, evidence-positive):** leaf label `L` covers grid column `C` iff `C`'s center-x ∈ `[L.inkX0, L.inkX1]`. No symmetrization. Because grid columns are body columns, this is body-grounded. Non-overlapping labels ⇒ automatic partition (no column center under two labels).
- **Parent rule (unchanged):** a parent covers the contiguous run of leaf columns under its ink via the B1.1 centering-bounded `repair_coverage`, so `Q1`/`Prior Visit`-style pivots keep spanning correctly, bounded by the leaf partition (a parent never claims a leaf's column).

**Caption (Cause B):** the caption/fragment rows do not partition-align, so a header tree that includes them cannot tile. The tiling membrane already knows this — so we let it decide: keep the **maximal body-adjacent suffix of header rows that tiles**; leading non-aligning rows peel away.

---

## 3. Components

### 3.1 `src/iladub/etkl/headergraph.py` (new) + `vocab/ontology/tab.ttl`
- `header_evidence(band, grid, split) -> Graph` — a fresh per-band `Graph()` (the band is the closure boundary, as in B2c `classifygraph`): one `tab:HeaderCell` per header cell in rows `[0,split)` with `tab:atHeaderRow` (int), `tab:headerText` (string), `tab:inkX0`/`tab:inkX1` (float ink extent); and one `tab:GridColumn` per leaf column with `tab:colIndex` (int) and `tab:colCenterX` (float = midpoint of `b[i]..b[i+1]`).
- A thin runner (reuse the `celltype.run_scalar`/`grid_evidence` pattern; a `run_covers(rq, graph) -> dict[int, tuple[int,...]]` reader returning, per header-cell row-index/id, its covered column indices).
- `vocab/ontology/tab.ttl`: declare `tab:HeaderCell a owl:Class`, `tab:GridColumn a owl:Class`, and properties `tab:atHeaderRow`, `tab:headerText`, `tab:inkX0`, `tab:inkX1`, `tab:covers` (HeaderCell→GridColumn), `tab:colIndex`, `tab:colCenterX` — owned `tab:` vocab. (Confirm none already exist with a conflicting definition — the B2c lesson: grep the target ttl before adding.)

### 3.2 `vocab/queries/header-covers.rq` (new, AXIOM)
Derives leaf-row coverage: for the leaf header row (the max `atHeaderRow` present, i.e. the row adjacent to the body), `SELECT ?cell ?col WHERE { ?cell a tab:HeaderCell ; tab:atHeaderRow ?r ; tab:inkX0 ?x0 ; tab:inkX1 ?x1 . ?gc a tab:GridColumn ; tab:colIndex ?col ; tab:colCenterX ?cx . FILTER(?cx >= ?x0 && ?cx <= ?x1) }` scoped to the leaf row. Evidence-positive (coverage only where a center is present under ink), open-world, no threshold. The load-bearing comment explains the leaf-vs-parent split and why symmetrization is *not* applied here.

**Uncovered-column edge (honest, decided against the fixtures):** a leaf column whose center falls in a gutter between labels, or under a non-centered / blank-header label, is covered by *no* leaf cell under the strict center-in-ink rule → a coverage gap → the tree would not tile (honest escalation). This is a possible regression vs the old symmetrization, which absorbed such columns into a neighbour. The **mitigation, still body-grounded and threshold-free:** assign each *otherwise-uncovered* column to the leaf label whose **center-x is nearest** (a Voronoi fallback over leaf-label centers, restricted to the leaf row) — still a partition, no tolerance. Whether this fallback is needed is settled empirically in the plan: run the full existing suite; add it only if a real fixture regresses (YAGNI). GrainCorp needs only the strict rule (every column is under its label's ink).

### 3.3 `src/iladub/etkl/headers.py` (integration)
- `infer_header_tree`: for the **leaf row**, build each cell's `covers` from `header-covers.rq` (via `headergraph`) instead of `_covers_for_cell`; for **parent rows**, keep `_covers_for_cell` + `repair_coverage` unchanged. `_covers_for_cell` remains for the parent path (justified PROCEDURAL, oracle-disposed).
- **Caption peel:** wrap the tree assembly so the header-row set is the maximal body-adjacent contiguous suffix `[k, split)` (k from 0 up) whose assembled tree passes `merge_tiling_ok`. Return the first (largest) tiling tree; if none tiles, return the current result (→ honest `MERGE_AMBIGUOUS`, unchanged). This is a bounded search (≤ split iterations), each disposed by the existing oracle.
- `merge_tiling_ok` / `region_tiles` (the closed-world membrane) are **unchanged**.

### 3.4 `tests/etkl/test_derivation_equiv.py` (extend)
Add a differential oracle: the shipped `header-covers.rq` leaf-covering == a fast python reference (`_ref_header_covers`: column covered iff its center ∈ [inkX0, inkX1]) over random header/grid shapes (wide labels, gaps, single-column labels). Certifies the AXIOM.

---

## 4. Testing

- **Committed failing tests (TDD), synthetic, domain-neutral:**
  - **Wide single-column labels** (`tests/etkl/…`): a flat record table (e.g. columns `Month | Port | Reference Number | Exporter` where `Reference Number`'s label ink is wider than its narrow data column) → asserts a record table, no `MERGE_AMBIGUOUS`. Fails on current (symmetrizing) code, passes after.
  - **Leading caption line:** a table with a `Friday, 24 July 2026`-style date line above a real single- or two-row header → the caption row is peeled, the table asserts. Fails on current code, passes after.
  - **Genuine merged parent (regression guard):** a pivot-shaped table with a real 2-level header (`Prior Visit` spanning 2 leaf columns) → still asserts with the parent spanning correctly and the hierarchy intact. Must pass before *and* after (guards against the leaf change breaking real merges).
- **Differential oracle:** `header-covers.rq` == `_ref_header_covers` over random grids (§3.4).
- **Real-world confirmation (local, not committed):** re-run `compile_tables` on the GrainCorp PDF and record that the main table asserts `tab:HierarchicalTable` with score > 0 and records > 0 (was `MERGE_AMBIGUOUS`, 0 cells). PDF stays in the scratchpad.
- **No regression:** full suite; confirm every existing header/tiling/pivot test, `region_tiles`, `test_derivation_equiv`, and all shipped hierarchical/matrix fixtures assert byte-identically.

---

## 5. Neurosymbolic gate & discipline

- **AXIOM, not NEURAL (the reclassification):** with body evidence (leaf headers are 1:1 with body columns), "which columns does a leaf label cover" is a *derivation* over the header+grid evidence graph — evidence-positive, open-world, realized as SPARQL `SELECT`. This is the sound answer the prior NEURAL framing lacked; it dodges the "LLM replaces geometry" trap. NEURAL remains the fallback for the genuine residual (wide label over unclaimed/blank columns), deferred.
- **No tuned constant / no overfit:** the leaf rule is `center ∈ [inkX0, inkX1]` (a containment test, not a tolerance); the caption peel is disposed by the tiling oracle (no threshold — a genuine parent joins the tiling, a caption cannot); the parent path is the pre-existing centering-bounded geometry (`0.5·pitch` tolerance is derived, not tuned — unchanged). Validated on synthetic fixtures + the differential oracle, not tuned to GrainCorp bytes.
- **Constraint stays SHACL, open/closed split intact:** `merge_tiling_ok` / `region_tiles` remain the closed-world membrane disposing what may cross; the covering derivation is the open-world growth. The **holon (band) is the closure boundary** (fresh per-band evidence graph).
- **Source ownership:** `tab:HeaderCell`/`tab:GridColumn`/`tab:covers`/`tab:atHeaderRow`/`tab:headerText`/`tab:inkX0`/`tab:inkX1`/`tab:colIndex`/`tab:colCenterX` are owned `tab:` vocab; no HGA/Fluree terms. No third-party PDF committed.
- **Honest failure preserved:** genuinely ambiguous input (no tiling suffix) still escalates `MERGE_AMBIGUOUS` — credibility over completeness (§7).

---

## 6. Relation to prior work and steering

- Direct outcome of re-measuring GrainCorp after Loop A (PR #67). Second loop of the evidence-driven real-document push: fix the covering + caption → re-measure → the next exposed gap (row-grouping/subtotals, or split-number cells) defines Loop C.
- **Reopens and reclassifies the dropped "B2 general merged-header span":** the prior drop was correct *for a header-geometry-only NEURAL framing*; the body/sibling evidence turns it into a sound AXIOM. Resurrects the `tab:HeaderCell` evidence-graph idea (built then removed in B1.2) for a genuine, non-redundant purpose.
- Aligns with the shipped evidence-graph derivation family (celltype B2a/B2b, classify-kind B2c): a fresh per-band evidence graph + a holon-scoped SPARQL derivation + a differential oracle.
- The parked `iladub-zero-etl-showcase` branch can gain GrainCorp as a *win* example once this loop closes.

---

## 7. Open questions / later loops

1. **Loop C:** row-grouping with suppressed keys + interleaved subtotals (`Mackay Total`, `Jul 26 Total`) as first-class structure.
2. **Split-number / word-merged data cells** (`2 0,000` → `20,000`): a data-side extraction concern (cf. the border-aware char re-extraction), likely PROCEDURAL, its own loop.
3. **NEURAL residual:** a wide label over blank/unclaimed columns where the partition cannot decide — the genuine perceptual slice, via the `span_proposer` seam, if a real document ever needs it.
4. Whether the caption peel should also inform band segmentation (excluding furniture lines earlier, at `detect_bands`) rather than only at header-tree assembly — revisit if a later real document needs it.
