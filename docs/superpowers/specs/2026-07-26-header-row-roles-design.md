# Header-region row roles — NEURAL propose → oracle → dispose (Loop C)

- **Date:** 2026-07-26
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Third loop of the GrainCorp real-document capability push.
  **SHIPPED 2026-07-27:** GrainCorp 0.0 → 0.947 (447 cells), matching planning-time predictions exactly
  (full suite 583 passed / 5 skipped, no regressions); residues = leaf-grid under-segmentation of
  columns 1 (`Month Port`) and 13 (`Date Loading CompletedCommodityTotal`), confirmed present verbatim.
- **Predecessor:** `2026-07-26-header-column-reconciliation-design.md` (Loop B) shipped **Cause A** — the
  leaf-row covering as a body-grounded SPARQL AXIOM — and *deferred* **Cause B** (the caption line) to a
  NEURAL loop, because a geometric peel cannot distinguish a leaked caption from a genuinely-ambiguous
  off-center merge. **This is that loop**, re-scoped by measurement (§2).
- **Naming note:** loop letters here are scoped to the **GrainCorp real-document push** (A =
  header/body split, PR #67; B = header→column reconciliation, PR #68; C = this one). They are a
  *separate* sequence from the earlier neurosymbolic-redesign loops that also used A/B/C (loop B =
  `recover_dimensions`, loop C = `region_tiles`, both shipped 2026-07-15/16) — where this spec means
  those, it names the artifact, not the letter. The row-grouping / interleaved-subtotal slice
  previously pencilled in as "Loop C" (Loop B spec §7.2) becomes **Loop D**.

---

## 1. Purpose and scope

Decide, for each **non-leaf row of a table's header region**, what that row *is* — document
furniture, a wrap-continuation of the labels below it, or a genuine hierarchical level — as a
**NEURAL proposal disposed by two SHACL oracles** and admitted only through an accountable
`iladub:PromotionDecision`. This is the reading judgment Loop B proved is not soundly geometric.

**In scope:**

- A new NEURAL slice `src/iladub/etkl/rowrole.py` — `propose → oracle → dispose → promote`, a direct
  sibling of the shipped `span.py` (B1.3).
- A **three-way** role per non-leaf header row: `furniture` | `continuation` | `level`.
- **Oracle 1** — the existing tiling membrane (`region_tiles`) refuses structurally illegal readings.
- **Oracle 2 (new)** — `tab:HeaderContentConservedShape` refuses readings that **lose source content**.
- Furniture is **carried, not dropped**: a `tab:RegionCaption` node bound to the region with its text
  and its source header row (§5 "context is carried, not discarded"; §7 "never dropped, never faked").
- The BAML function `ProposeHeaderRowRoles`, authored in `baml_src/` (see §3.3 — B1.3's
  `ProposeHeaderSpan` is *missing* from `baml_src/`; this loop does not repeat that).
- Committed synthetic regression fixtures; GrainCorp as a local (uncommitted) real-world confirmation.

**Non-goals (later loops):**

- **Leaf-grid under-segmentation (→ next loop).** GrainCorp's recovered grid has 14 boundaries where the
  source has ~16, collapsing `Month|Port` into column 1 and `Date Loading Completed|Commodity|Total`
  into column 13. This loop asserts those columns with merged labels; it does not split them. Named
  residue, measured (§2), not a Loop-C failure.
- **Loop D:** row-grouping with suppressed keys + interleaved subtotals (`Mackay Total`, `Jul 26 Total`).
- **Split-number / word-merged data cells** (`2 0,000` → `20,000`) — a data-side extraction concern.
- **Mixed header rows** — a row that is *part* furniture and *part* genuine header cannot be expressed
  by a per-row role and correctly **escalates** (§3.2, §7).
- Fixing B1.3's missing `ProposeHeaderSpan` BAML function — named as a separate defect (§7.3).

**Success criteria:**

1. A synthetic flat table with a **leading date caption** plus a **wrapped 2-line label**, authored so
   the header wrap pitch ≈ the body row pitch (defeating `group_wrapped`'s adaptive `gap < lead`
   wrap-continuation gate — the fixture-tuned `0.9×lead` margin was already retired in B3,
   2026-07-22, `947f6fa` — because `lead` itself equals the gap here), escalates today and
   **asserts** with the correctly merged label after, given an injected proposer.
2. A proposer reading that **loses a header word** is **refused** by the conservation oracle → the
   region escalates and `graph` is left untouched.
3. **The contract guard:** the shipped off-center-merge fixture, *with a proposer active* answering
   honestly (`level`), **still escalates** `MERGE_AMBIGUOUS`. This is the exact contract a geometric
   peel broke in Loop B; the NEURAL path must not smuggle the unsoundness back in.
4. **No regression:** the full suite (548 at Loop B close) stays green. With `row_role_proposer=None`
   — the default — behaviour is byte-identical to today, including every shipped hierarchical, matrix,
   pivot, narrow-flank and off-center escalation fixture.
5. On the real GrainCorp band (local spike, uncommitted): the main region goes from
   `escalated / MERGE_AMBIGUOUS / 0 cells / score 0.0` to **`asserted / 447 cells / score 0.947`**, with
   the two grid residues recorded verbatim. **The loop closes** end-to-end on real input.
6. **Gate (§8):** the role is decided *only* by the NEURAL proposer; `build_row_reading` is a pure
   structural rewrite with no geometry and no constant; continuation placement mirrors Loop B's
   shipped `header-covers.rq` containment rule in Python (`rowrole._column_containing`), while the
   leaf-row covering itself genuinely reuses that AXIOM directly (§6); disposal is closed-world
   SHACL, band-scoped; legality gates admission, never confidence. No tuned tolerance is introduced
   anywhere.
7. Source-ownership clean: `tab:RegionCaption`, `tab:HeaderSourceCell`, `tab:hasCaption`,
   `tab:hasHeaderSourceCell`, `tab:captionText`, `tab:captionRow`, `tab:sourceText`, `tab:sourceRow`
   are owned `tab:` vocab. No third-party PDF committed.

---

## 2. Measurement — what the document actually shows (2026-07-26, post-Loop-B)

`compile_tables` on the GrainCorp Shipping Stem, page 0: region 2 = `UNSUPPORTED_TABLE / escalated /
MERGE_AMBIGUOUS / 0 cells`, **score 0.0**. Band 2 has 55 lines, `header_body_split` = 4, and the
recovered leaf grid has **14 columns** with boundaries
`[16.3, 54.3, 159.3, 202.8, 246.3, 315.8, 365.8, 420.8, 470.3, 518.8, 567.8, 613.8, 663.8, 707.8, 827.5]`.

The header region is lines 0–3, grouped by `group_wrapped` into four rows:

| lvl | cells | resolved covers |
| --- | --- | --- |
| 0 | `Friday, 24 J` \| `uly 2026` | (2…11), (7) |
| 1 | `Date of Grain` | (1…12) |
| 2 | `Unique Slot`, `Loading`, `Date Nomination`, `Time Nomination`, `Date Nomination`, `Time Nomination`, `Date Loading` | (1-4), (6), (7-9), (8-10), (9-11), (10-12), (13) |
| 3 | `GC Fin Year`, `Month Port`, `Reference Number`, `Exporter`, `Name Of Ship`, `Date ETA of Ship`, `Commencement`, `Date ETD of Ship`, `Received`, `Received`, `Accepted`, `Accepted`, `Status`, `CompletedCommodityTotal` | (0),(1),(2),…,(13) — **a clean partition** |

**Finding 1 — Loop B's Cause-A AXIOM works.** The leaf row (level 3) partitions the 14 columns exactly.
Every remaining overlap is at levels 0–2.

**Finding 2 — peeling the caption alone is insufficient.** Tiling every row subset:

| kept rows | `merge_tiling_ok` |
| --- | --- |
| (0,1,2,3) — as-is | False |
| (1,2,3) — caption peeled | **False** |
| (2,3) | False |
| (1,3) | True *(accidental)* |
| (0,3) | False |
| **(3,) — leaf only** | **True** |

So the two-way *furniture vs header* classifier proposed in Loop B §7.1 would leave GrainCorp
escalating. The loop would not **close** — violating the loop-definition-of-done.

**Finding 3 — rows 1 and 2 are neither furniture nor hierarchy; they are wrap-continuations.**
`Unique Slot` (x 160.2–191.0) and `Reference Number` (x 160.2–207.0) both sit in column 2
`[159.3, 202.8)` → the real label is *"Unique Slot Reference Number"*. `Date of Grain`, `Loading` and
`Commencement` all start at x 378.5, inside column 6 `[365.8, 420.8)` → *"Date of Grain Loading
Commencement"*. These are the genuine GrainCorp column names.

`group_wrapped` could not absorb them: the header wrap pitch is **6.6 pt** and the body row pitch is
**6.5 pt** (lines at 61.2 / 67.8 / 74.4 / 81.0, then 88.4 / 94.8 / 101.3 / 107.8). The gate is
`gap < lead` — the adaptive median inter-line gap, **not** a tuned ratio: the fixture-tuned
`0.9 × lead` margin was already retired in B3 (2026-07-22, commit `947f6fa`; see
`cells.group_wrapped`'s docstring). Even that adaptive gate cannot fire here, because `lead` (the
median gap, ≈6.6 pt for this band) is itself ≈ the body pitch: `6.6 < 6.5` is false. **This is not
a threshold to retune** — it is a genuine, still-live limitation: an adaptive median-gap rule
cannot decide wrap-vs-row when the two leadings coincide, because that is a *reading* judgment
(which row is a wrap fragment), not a geometric threshold problem. This loop does not fence a §8
gate defect (there is none left to fence — B3 already retired the tuned constant); it recognizes
that no threshold, tuned or adaptive, can settle this class of question, and hands it to the
NEURAL slice when the resulting tree fails to tile.

**Finding 4 — the merged reading closes the loop.** Spiking the reading
`row 0 = furniture, rows 1–2 = continuation, row 3 = leaf` and re-running `compile_tables`:

```
region 2  UNSUPPORTED_TABLE  asserted  cells=447  reason=None
score= 0.947
```

with recovered labels:

```
(0,)  'GC Fin Year'                    (7,)  'Date ETD of Ship'
(1,)  'Month Port'            ← residue (8,)  'Date Nomination Received'
(2,)  'Unique Slot Reference Number'   (9,)  'Time Nomination Received'
(3,)  'Exporter'                       (10,) 'Date Nomination Accepted'
(4,)  'Name Of Ship'                   (11,) 'Time Nomination Accepted'
(5,)  'Date ETA of Ship'               (12,) 'Status'
(6,)  'Date of Grain Loading Commencement'
(13,) 'Date Loading CompletedCommodityTotal'   ← residue
furniture: ['Friday, 24 J', 'uly 2026']
```

Columns 1 and 13 carry merged labels because the **leaf grid under-segmented** those columns — a
grid-recovery gap, not a row-role gap. That is why the score is 0.947 and not 1.0, and it is the
named residue that defines the next loop (§7.1).

**Finding 5 — the honest limit of the oracles, measured precisely.** Tiling **cannot** discriminate
`furniture` from `continuation` — and the residue is wider than a single two-way tie. On this
loop's own fixture (2 non-leaf rows → 3² = 9 candidate role vectors), the oracles (tiling +
conservation) admit **6 of 9**: every vector except the three `level`-first vectors
(`('level','level')`, `('level','continuation')`, `('level','furniture')`) is legal. That includes
readings that are legal but **wrong** — e.g. `('continuation', 'furniture')` yields
`['Item', 'Ref', 'Monday Qty', '5 May Cost']`, which tiles and conserves, yet merges the leaked
date caption into the wrong labels. Both the intended reading and several unintended ones are structurally legal and
lossless. **This strengthens, not weakens, the case that the residue is irreducibly NEURAL**: it is
not merely that two candidate readings are indistinguishable by oracle, but that a *majority* of
the role-vector space is oracle-legal, so no oracle-guided search could land on the correct reading
by construction — only a proposal that actually reads the content can. This is exactly why the
driver performs **no search** over the role space (§3.1): searching this space would as likely
converge on a wrong-but-legal reading as the right one. The oracles refuse illegal and lossy
readings; the *choice among the legal ones* is governed by §3/§4 epistemics — a proposition, an
accountable promotion, a recorded rationale and provenance — not by an oracle. This is stated
plainly rather than papered over.

---

## 3. Components

### 3.1 `src/iladub/etkl/rowrole.py` (new) — the NEURAL slice

Mirrors `span.py` structurally, so the shipped B1.3 pattern is reused rather than re-invented.

- **`row_role_context(band, grid, body_line) -> dict`** — builds the proposer's inputs from the header
  rows: each non-leaf row's cell texts, the leaf row's cell texts, and for each non-leaf cell the
  column index its ink center falls in (via Loop B's `header_evidence` + `HEADER_COVERS_RQ`). A pure
  structural read — it reports geometry, it never decides a role.
- **`build_row_reading(header_rows, grid, roles) -> (nodes, captions, source_cells)`** — the pure
  structural rewrite under a proposed role vector. No geometry constant, no tolerance:
  - `continuation` → the row contributes **no level**. Each of its cells' text is appended, in
    top-to-bottom source order, to the label of the leaf node covering the column that contains the
    cell's ink center (a small Python mirror, `_column_containing`, of Loop B's shipped
    `header-covers.rq` containment rule — not a call into the query itself, since that query
    filters to `MAX(?atHeaderRow)`, the leaf row only; see §6).
  - `furniture` → the row contributes **no level**. Each cell becomes a `tab:RegionCaption` carrying
    `tab:captionText` and `tab:atHeaderRow`.
  - `level` → the row stays a parent level and flows through the **unchanged** `_covers_for_cell` +
    `repair_coverage` + `resolve_narrow_flanks` path (so `Prior Visit`-style pivots are untouched).
  - The leaf row is never classified — it is always the leaf. Its covering stays Loop B's AXIOM.
  - **Unplaceable continuation (refuse).** If a `continuation` cell's ink center falls in a column that
    no leaf node covers, there is no label to merge into. The reading is **refused** (`None` →
    escalate) rather than inventing a placement or dropping the text. Loop B's uncovered-column edge
    (a terminal "short parent" column) is exactly where this can arise.
  - **All-`level` is a no-op.** If every non-leaf row is `level`, the reading reproduces today's tree,
    fails tiling, and is refused → escalate. This is precisely the contract guard of §4.
  - **No non-leaf rows (k = 0).** A single-row header has nothing to classify: return `None`
    immediately (escalate) without calling the proposer.
  - Every header-region cell also yields a `tab:HeaderSourceCell` (`tab:headerText`,
    `tab:atHeaderRow`), linked `table tab:hasHeaderSourceCell cell` — the conservation oracle's target.
- **`resolve_header_row_roles(graph, hreg, band, table_uri, doc_uri, page, proposer)`** — the driver,
  the direct analogue of `span.resolve_ambiguous_merge`:
  1. Ask the proposer **once** for the role vector. `None`, a wrong-length vector, or an unknown role
     → return `None` (escalate), `graph` untouched.
  2. Build the reading; assert it into a **scratch** `Graph()` via `assert_hier_region`, plus the
     caption and source-cell triples.
  3. `region_tiles(scratch)` — which now carries **both** oracle families (§3.4) — must pass, and the
     asserted token count must be > 0. Otherwise return `None` (escalate), `graph` untouched.
  4. On success: `graph += scratch`, then emit one `iladub:PromotionDecision` per classified row via
     `promote.emit_row_role_promotion`. Return `(asserted_token_count, (promotion_uri, ...))`.
- **No search.** One proposal, one disposal. A refused reading escalates honestly. This is
  load-bearing: because `all furniture` is *always* legal (it tiles, and it conserves — the text is
  carried as captions), **any** oracle-guided search over the 3^k role space would converge on it and
  silently strip the real header labels, making the oracle the decider by brute force. Honest failure
  over search.

### 3.2 `src/iladub/etkl/propose.py` (extend) — the injected seam

Following the existing `Proposal`/`SpanProposal` pattern exactly:

- `RowRoleProposal(roles: tuple[str, ...], confidence: float, rationale: str, suggester_iri: str)`
  — `roles` is parallel to the non-leaf header rows, top to bottom. Docstring states the epistemics:
  the reading is a **PROPOSITION**, admitted only via a `PromotionDecision` after the oracles confirm
  it is legal and lossless — never asserted as grounded truth.
- `RowRoleProposer` Protocol — `propose_header_row_roles(context: dict) -> RowRoleProposal | None`.
- `FakeRowRoleProposer` — deterministic offline proposer (a fixed proposal, or `None` for abstention),
  so every path is offline-testable.
- `BamlRowRoleProposer` — the live path; `baml_client` imported *inside* the method (lazy, so
  construction never trips the version guard), env-gated by the existing `baml_proposer_available()`.

A **per-row** role is the deliberate granularity: it matches the tree's structure (a level *is* a row),
keeps the proposal space at 3^k for k non-leaf rows, and covers every measured document. A **mixed**
row cannot be expressed and escalates — named honestly, not silently approximated (YAGNI: no measured
document exhibits one).

### 3.3 `baml_src/header_rowrole.baml` (new)

```
class HeaderRowRoleProposal {
  roles string[] @description("one of furniture|continuation|level per non-leaf header row, top to bottom")
  confidence float @description("0.0-1.0, calibrated confidence in the whole reading")
  rationale string @description("one sentence per row on why")
}

function ProposeHeaderRowRoles(
  rows: string[][], leaf_labels: string[], row_columns: int[][]
) -> HeaderRowRoleProposal { client Claude prompt #" <body per the paragraph below> "# }
```

The prompt states the three roles concretely (a date/title/page line is `furniture`; a fragment that
completes a label below it is `continuation`; a group label spanning several leaf columns is `level`),
supplies the leaf labels and each fragment's column so the model can see *which* label a fragment
would complete, and instructs it to prefer `continuation` over `furniture` when a fragment reads as
part of a label — because `furniture` is the lossy answer.

**Defect named, not fixed here:** `BamlSpanProposer` (B1.3, shipped) calls `ProposeHeaderSpan`, which
**does not exist in `baml_src/`** — only `ProposeDimensionName` and `ProposeGrounding` are authored. So
B1.3's live path cannot run. This loop authors its own function properly and records that gap (§7.3).

### 3.4 `vocab/ontology/tab.ttl` + `vocab/shapes/tab-shapes.ttl` — the conservation oracle

New **owned** `tab:` terms (grep the file first — the B2c lesson): classes `tab:RegionCaption`,
`tab:HeaderSourceCell`; object properties `tab:hasCaption` (Table→RegionCaption),
`tab:hasHeaderSourceCell` (Table→HeaderSourceCell); datatype properties `tab:captionText`,
`tab:captionRow`, `tab:sourceText`, `tab:sourceRow`.

`tab:HeaderSourceCell` is deliberately *distinct* from Loop B's `tab:HeaderCell`: the latter lives
only in the transient pre-holon evidence graph, the former is committed and region-bound.

**Loop B's `tab:atHeaderRow` / `tab:headerText` are deliberately NOT reused**, despite the obvious
temptation. Both carry `rdfs:domain tab:HeaderCell`, and `region_tiles` validates with
`inference="rdfs"` — so a committed caption bearing them would be *inferred* to be a
`tab:HeaderCell`, contradicting that class's "transient … never asserted into a holon" definition and
silently leaking pre-holon evidence vocabulary into the compiled holon. Four dedicated properties are
the correct cost.

New shape, in the same `sh:sparql` style as the eight other tiling shapes:

```
tab:HeaderContentConservedShape a sh:NodeShape ;
    sh:targetClass tab:HeaderSourceCell ;
    sh:sparql [
        sh:message "Header-region source cell is not accounted for: neither merged into an asserted header label nor carried as a region caption." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                $this tab:sourceText ?txt .
                FILTER NOT EXISTS { ?lc a tab:LabelCell ; tab:cellText ?lt . FILTER(CONTAINS(?lt, ?txt)) }
                FILTER NOT EXISTS { ?cap a tab:RegionCaption ; tab:captionText ?ct . FILTER(CONTAINS(?ct, ?txt)) }
            }
        """ ] .
```

Its IRI is added to `tiling._TILING_SHAPE_IRIS`, so `region_tiles` carries both invariant families in
one pySHACL call. **Zero regression by construction:** no existing region emits a
`tab:HeaderSourceCell`, so the shape targets nothing and passes.

**Known weakness, stated:** `CONTAINS` can let a lost word pass if it coincidentally occurs inside
another label. It cannot pass a word absent from every label and every caption. That is an honest
membrane — it blocks the failure mode that matters (a role vector that silently deletes header text)
without claiming exactness.

### 3.5 `src/iladub/etkl/promote.py` (extend)

`emit_row_role_promotion(g, region_uri, row_index, role, texts, proposal)` — mirrors
`emit_span_promotion`: an `iladub:CandidateConcept` (label = the row reading, `iladub:surfaceText` =
the row's joined text, `iladub:suggestedBy` the suggester, `iladub:fromRegion`, `iladub:status
iladub:proposed`, `iladub:confidence`) reviewed by an `iladub:PromotionDecision` with
`dec:decidedBy` / `dec:consideredEvidence` / `dec:confidence`. Returns the decision URI.

### 3.6 `src/iladub/etkl/compile.py` (integration)

`compile_tables(..., span_proposer=None, row_role_proposer=None)`. On the hierarchical branch, where
the tree currently fails and falls through to `escalate_region(..., "MERGE_AMBIGUOUS", ...)`, try
`resolve_header_row_roles` first **only if** `row_role_proposer is not None`. Ordering relative to the
existing `span_proposer` path: the narrow-flank resolver keeps priority (it fires on an explicit
`ambiguous_flank` flag, a strictly narrower trigger); the row-role resolver handles the general
tiling failure. Both absent → escalate exactly as today.

---

## 4. Testing

All fixtures **synthetic and domain-neutral**; the GrainCorp PDF stays uncommitted (scratchpad only).

- **Red (the closing case):** a flat record table with a leading date caption row and a wrapped 2-line
  column label, authored so the header wrap pitch ≈ the body row pitch (defeating `group_wrapped`).
  Escalates `MERGE_AMBIGUOUS` today; asserts with the merged label given a
  `FakeRowRoleProposer(roles=("furniture", "continuation"))`.
- **Conservation refusal:** a `FakeRowRoleProposer` returning a reading that drops a header word →
  `resolve_header_row_roles` returns `None`, the region escalates, `graph` is unchanged.
- **Contract guard (the one that matters):** the shipped off-center-merge fixture
  (`test_offcenter_merge_escalates` and its B1.3 / span-gate siblings) with a `FakeRowRoleProposer`
  answering `level` **must still escalate** `MERGE_AMBIGUOUS`. Loop B's geometric peel broke exactly
  this; the NEURAL path must not.
- **Abstain / malformed:** proposer returns `None`, a wrong-length vector, or an unknown role string →
  escalate, `graph` untouched.
- **Unplaceable continuation:** a `continuation` cell whose ink center lands in a column no leaf node
  covers → refused, escalate, `graph` untouched (§3.1).
- **Furniture is carried:** the caption text appears in the committed graph as a `tab:RegionCaption`
  with `tab:atHeaderRow` — asserting §5/§7 (never dropped).
- **Promotion emitted:** one `iladub:PromotionDecision` per classified row, each reviewing an
  `iladub:CandidateConcept` with `iladub:status iladub:proposed` — the membrane invariant.
- **Pivot / hierarchical regression:** every shipped hierarchical, matrix, pivot, narrow-flank and
  escalation fixture asserts byte-identically with `row_role_proposer=None` (the default) — the
  proposer never fires on a tree that already tiles.
- **Shape isolation:** `region_tiles` on a graph with no `tab:HeaderSourceCell` behaves exactly as
  before (the new shape targets nothing).
- **Full suite** green (548 at Loop B close, plus the new tests).
- **Real-world confirmation (local, uncommitted):** GrainCorp region 2 goes
  `escalated / MERGE_AMBIGUOUS / 0 cells / score 0.0` → **`asserted / 447 cells / score 0.947`**;
  the 14 recovered labels and the two grid residues recorded verbatim in the report.

---

## 5. Neurosymbolic gate & discipline

- **NEURAL, correctly classified.** "Is this header-region line furniture, a wrap-continuation, or a
  level?" is a *reading* judgment over human-addressed structure. Loop B proved it is not soundly
  geometric (a caption and an off-center merge are structurally identical), and §2 Finding 3 proves the
  pitch-ratio heuristic fails on a real document where header leading equals body leading. So it is
  GenAI-via-BAML **proposing** under §3 epistemics, **disposed by semantic oracles** — never a Python
  geometry heuristic with a tuned tolerance.
- **The only decider is the proposer.** `row_role_context` reports geometry; `build_row_reading` is a
  pure structural rewrite; continuation placement is a small Python mirror (`_column_containing`) of
  Loop B's shipped `header-covers.rq` containment rule, not a call into the query (see §6) — the
  leaf-row covering inside `_tree_from_rows` is what genuinely reuses that AXIOM. No new numeric
  literal, no new tolerance, in Python or in RDF.
- **Open/closed split intact.** Growth is open-world (the leaf-row covering's genuinely-reused
  `header-covers.rq` derivation; continuation placement mirrors the same containment rule in
  Python); disposal is closed-world SHACL (`region_tiles`: the nine tiling shapes, including the
  conservation shape). The **band/region is the closure boundary** — a fresh scratch `Graph()` per
  candidate reading.
- **Legality gates admission, never confidence.** A proposal whose scratch region fails either oracle
  is refused regardless of `proposal.confidence`. Confidence is *recorded* on the promotion, never
  consulted as a threshold.
- **No search** (§3.1) — the anti-overfitting decision of this design. `all furniture` is always legal,
  so a search would find it and destroy the labels.
- **Honest failure preserved.** No proposer, an abstaining proposer, a malformed vector, an illegal
  reading, or a lossy reading → `MERGE_AMBIGUOUS`, in-band, with the region's ASCII. Credibility over
  completeness.
- **Never overfit.** Validated on synthetic fixtures authored from the *shape* of the problem
  (caption + wrap-at-body-pitch), not on GrainCorp bytes. GrainCorp is a confirmation, not a target;
  its residual 0.947 (not 1.0) is reported as a named gap, not tuned away.
- **Source ownership.** `tab:RegionCaption`, `tab:HeaderSourceCell`, `tab:hasCaption`,
  `tab:hasHeaderSourceCell`, `tab:captionText`, `tab:captionRow`, `tab:sourceText`, `tab:sourceRow`
  are owned `tab:` vocab; Loop B's evidence properties are deliberately not reused (§3.4). No HGA
  term appears as a subject. No third-party PDF committed.
- **What this loop does and does not do about `group_wrapped`'s gate.** The tuned `0.9 × lead`
  margin was **already retired** in B3 (2026-07-22, commit `947f6fa`), replaced by the adaptive
  `gap < lead` median-gap rule — that debt was retired *before* this loop, not by it. What remains,
  and what this loop actually fences, is a *residual reading limit*: even the adaptive rule cannot
  decide wrap-vs-row when a document's header leading coincidentally equals its body leading (§2
  Finding 3) — that is not a threshold miscalibration, it is a reading judgment no geometric gate,
  tuned or adaptive, can make. `group_wrapped` remains the cheap first-pass grouping; when its
  grouping yields a tree that cannot tile, the NEURAL slice decides instead.

---

## 6. Relation to prior work and steering

- Direct discharge of Loop B §7.1, **re-scoped by measurement** from two-way (furniture vs header) to
  three-way (furniture / continuation / level), because §2 Finding 2 shows two-way does not close.
- Reuses the shipped NEURAL family: `span.py` (B1.3) is the structural template; `reshape.certify_with_proposals`
  (A2.1) and `segment.find_table_gutter` are the other propose→oracle→dispose exemplars.
- Reuses the shipped AXIOM family: Loop B's `header-covers.rq` is reused directly for leaf-row
  covering (inside `_tree_from_rows`); continuation-fragment placement is a small Python mirror of
  the same containment rule (`rowrole._column_containing`), not a call into the query itself, since
  the query filters to `MAX(?atHeaderRow)` (the leaf row only) and so cannot be reused as-is for
  non-leaf rows. The closed-world membrane is the shipped `region_tiles` SHACL, extended by one
  shape in the same file.
- **Closes the loop** (loop-definition-of-done): an end-to-end score on real input — GrainCorp
  0.0 → 0.947, 447 cells — with the residue escalated/named in-band, not silently dropped.
- Unblocks GrainCorp as a *win* example for the parked `iladub-zero-etl-showcase` branch, once the
  grid residue (§7.1) is also closed.

---

## 7. Open questions / later loops

1. **Leaf-grid under-segmentation (the next loop, and the reason GrainCorp is 0.947 not 1.0).**
   `recover_leaf_grid` found 14 boundaries where the source has ~16, collapsing `Month|Port` into
   column 1 and `Date Loading Completed|Commodity|Total` into column 13. The header labels prove the
   split points exist (two/three label tokens per collapsed column, each with its own ink run), so
   this is likely a sound **AXIOM** — a header-ink-grounded boundary derivation — not a NEURAL slice.
   Measure before designing.
2. **Loop D:** row-grouping with suppressed keys + interleaved subtotals (`Mackay Total`,
   `Jul 26 Total`) as first-class structure.
3. **`ProposeHeaderSpan` is missing from `baml_src/` (defect).** `BamlSpanProposer` (B1.3, shipped)
   references it, so B1.3's live path cannot run; only `FakeSpanProposer` works. Authoring it is a
   small separate fix, deliberately not bundled here.
4. **Split-number / word-merged data cells** (`2 0,000` → `20,000`) — a data-side extraction concern,
   likely PROCEDURAL, its own loop.
5. **Mixed header rows** — if a real document ever shows a row that is part furniture and part header,
   the per-row role must become per-cell (§3.2). Not before evidence demands it.
6. **The furniture/continuation residue is permanently NEURAL** (§2 Finding 5). No oracle can rank two
   legal readings. If this ever needs strengthening, the lever is a *knowledge-first* one — a contract
   declaring the destination's expected column labels, letting the grounding portal prefer the reading
   that grounds — not a sharper geometric test.
