# Row groups from confirmed aggregations (Loop I)

- **Date:** 2026-07-30
- **Author:** François Rosselet
- **Status:** Design (brainstormed, approved). Ninth loop of the GrainCorp real-document push
  (A = PR #67; B = PR #68; C = PR #69; C.1 = PR #70; D = PR #71; F = PR #72; G = PR #73;
  H = PR #74).
- **Origin:** Loop H's closure note — "the row-group *hierarchy* (Month > Port `coversRow`
  tree) is its own future loop, now unblocked." Plus the PR #59 recorded minor
  (`_record_uri` has no collision guard), which this loop makes real and closes.

---

## 1. Purpose and scope

**The gap, measured (2026-07-30):** GrainCorp's 50 body rows split 33 data + 17 aggregation.
The Month key (c1) is **suppressed on 30 of 33 data rows** (the author writes it once per
month); Port (c2) is repeated (1 exception). So a record minted from row 10 does not know it
is an Aug 26 / Mackay booking — the group identity the author encoded positionally is
discarded.

**The insight:** Loop H's confirmed aggregation rows are *witnesses to the groups themselves*:

- the aggregation's **label column L** names the grouping **level** (port totals label in c2,
  month totals in c1) — author-evidenced, not guessed from "leading text columns";
- its **`tab:aggregates` edges** name the group's exact **member rows**, arithmetic already
  verified;
- the group's **key** is derivable with no language reading: **the unique distinct non-blank
  cell value in column L among the member rows** (`Jul 26` — the only non-blank c1 among
  member rows 0/2/4/6; `Mackay` — the repeated c2 of its members). No unique value → no
  group. Honest refusal, never a guess.
- **Nesting** is member-set containment: port members ⊂ month members → `parentHeader`, with
  a no-intermediate-group guard.

**Evidence decision (user-approved): H-confirmed only.** A row group exists only where a
confirmed aggregation row evidences it. Unconfirmed groups (Port Kembla — blank total) get
no group node; named residue. Ditto/forward-fill (rowheaders' blank-below convention) is NOT
used here: it guesses levels from "leading text columns", which is wrong on GrainCorp
(nearly all 17 columns are text) and weaker evidence than the verified aggregations.

**Representation decision (user-approved): the shipped `coversRow` tree.** Group nodes are
row headers in the exact shape `assert_row_hier_region` and the matrix path already emit
(`tab:HeaderNode` + `hasHeaderNode` + `headerLevel` + `coversRow` + `parentHeader` +
`hasLabel`) — the feed's `_row_header_path` walk then gives records their
`Jul 26 > Mackay` identity with minimal feed change. One refinement: `hasLabel` points at
the **existing source `tab:EntryCell`** that carries the key, so provenance-to-the-page (§6)
comes for free and no text is duplicated (`_header_path` reads `cellText` off the label
node, which an EntryCell has).

**Non-goals:**

- Groups without a confirmed total (ditto-only evidence) — named residue.
- The row-hier / record / transposed paths (R17 and the H remainder (c)/(c')) — untouched.
- Grounding the group key as a `SurfaceConcept` per record cell — the record identity path
  carries the keys; per-cell concept injection can be a later slice if grounding needs it.

**Success criteria (GrainCorp, measured not assumed):**

1. **16 group nodes** (3 months + 13 confirmed port groups), each with the correct key label
   and the correct `coversRow` member set.
2. **Nesting:** every port group's `parentHeader` is its month group; months have no parent.
3. **Record identity:** every data record covered by groups carries its path (row 10 →
   `Aug 26 > Mackay` prefix); Port Kembla data rows keep their opaque identity (no confirmed
   group — honest).
4. **The collision guard:** rows 9 and 10 (two bookings, same Aug 26 / Mackay group) mint
   **two distinct records** — never silently merged.
5. **Structural loop:** GrainCorp score/cells UNCHANGED at 0.9496/509 — written as a FAILURE
   condition (the pattern of loops D/F/G/H): any score delta means this loop leaked into
   assertion accounting.
6. Full suite green.

---

## 2. Components

### 2.1 `vocab/queries/row-groups.rq` — the derivation (AXIOM, open world)

One SPARQL `CONSTRUCT` over the already-emitted table graph (post `assert_hier_region`
emission, pre-membrane), reading only: `tab:DetectedAggregationRow`, `tab:aggregates`,
`tab:EntryCell` / `atRow` / `atColumn` / `cellText`, and the table's row/column URIs.

For each confirmed aggregation row A with label column L. L and the measure column are
already known to the emitter (detect_aggregation_rows returns them), so the emission (2.2)
passes them as **bindings** — the same pattern as `stub-data-split.rq`'s `?split` binding;
the query does not re-derive them:

- **Key:** the member cell value `?v` at column L such that no other member row carries a
  *different* non-blank value at L (query-local `NOT EXISTS` — holon-scoped closed-world
  guard inside an open derivation, per §8). No such `?v` → the group is not constructed.
- **Construct:** a group node `<table>-rg<i>` typed `tab:HeaderNode` **and**
  `tab:DerivedRowGroup` (new subclass, mirroring H's Detected pattern), with
  `tab:hasHeaderNode` from the table, `tab:coversRow` → each member row, `tab:hasLabel` →
  the source EntryCell carrying `?v`, and `prov:wasDerivedFrom` → the aggregation row A
  (the witness).
- **Nesting (second pass or same query):** `parentHeader` from group P to group Q iff
  members(P) ⊂ members(Q) strictly (every member of P in Q; some member of Q not in P) and
  no group R with members(P) ⊂ members(R) ⊂ members(Q). `headerLevel` = the count of groups
  strictly containing this one (exact, derivable, no ordering assumption on column indices).
- **No numeric literal in the query** (the transform-gate rule); columns arrive as bindings.

**Why AXIOM:** this is a role/structure decision derived monotonically from present evidence
(the confirmed aggregations) — the §8 default. The only closed-world elements (key
uniqueness, strict containment, no-intermediate) are query-local guards inside the one
table holon — the holon is the closure boundary.

### 2.2 Emission point — `holon.py::assert_hier_region`

After the aggregation-row emission (the loop H block), run `row-groups.rq` per confirmed
aggregation (bindings: table URI, aggregation row URI, label column URI, measure column
URI) and add the constructed triples — all still inside the scratch graph of the loop G
backstop, so a malformed group escalates in-band (`REGION_TILING_FAILED`), never crashes.

### 2.3 Membrane — `vocab/shapes/tab-shapes.ttl`

`tab:DerivedRowGroupShape`, targeting the **subclass only** (`tab:DerivedRowGroup` — the
row-hier and matrix paths' plain `HeaderNode`s are untouched): exactly one `tab:hasLabel`,
≥ 1 `tab:coversRow`, exactly one `prov:wasDerivedFrom`. Added to `_TILING_SHAPE_IRIS`
(eleventh entry). Vocab: `tab:DerivedRowGroup ⊑ tab:HeaderNode` in `tab.ttl` (versionInfo
already 0.2.0; additive change, no bump needed — monotonic).

### 2.4 Feed — `feed.py::table_records` collision guard

`_row_header_path` already returns paths for any `coversRow` tree — zero change there. The
guard: after grouping rows, if two rows map to the **same** row-path identity, each keeps
its opaque row fragment appended (`Aug 26 > Mackay > r10`) — applied uniformly (also fixes
the PR #59 recorded minor for cross-tabs). Rows with no covering group keep today's opaque
identity unchanged.

---

## 3. Testing

- **Derivation units** (small graphs, no PDF): unique key → group with correct label cell +
  members; conflicting non-blank values at L → NO group; all-blank at L → NO group; nesting
  containment incl. the no-intermediate guard (3-level chain); `headerLevel` = containment
  count; language-independence (a key in another language derives identically — the value
  is read positionally, never matched).
- **Membrane:** a `DerivedRowGroup` without a label (or without members) fails the shape;
  a bare `HeaderNode` (row-hier path shape) still passes.
- **Feed:** covered rows get path identity; two same-group rows → two distinct record URIs
  (the collision guard, RED first against today's silent merge); uncovered rows keep opaque
  identity; existing matrix/row-hier feed tests unchanged.
- **E2E:** `subtotal_hier_table_pdf` — its one confirmed subtotal has label column 1 and
  members r0/r1, whose c1 values are 'Mackay'/'Mackay' → key 'Mackay': exactly one group
  node covering r0/r1, and the two data records carry the 'Mackay' path prefix with
  distinct URIs (the collision guard exercised E2E).
- **Real-world (local, uncommitted):** GrainCorp — the six success criteria of §1.
- **Mutation checks:** disable the uniqueness guard → conflicting-key test fails; disable
  the collision guard → distinct-URI test fails.

---

## 4. Neurosymbolic gate & discipline

- **AXIOM (SPARQL derivation, open world)** with holon-scoped closed-world guards — the §8
  default; no NEURAL (nothing perceptual: membership and keys are already verified facts),
  no new PROCEDURAL beyond engine glue (bindings + graph merge, the `interpret.run`
  pattern).
- **No language matching:** keys are read positionally from member cells; aggregation label
  text is never parsed (`'Jul 26 Total'` is never split into `'Jul 26'` + `' Total'` — the
  key comes from row 0's own cell).
- **No tuned constant:** no numeric literal in the query; the collision guard is exact
  (path multiplicity), not a threshold.
- **§5/§6:** the group key is *carried context* with provenance to the page — `hasLabel`
  points at the source cell; the group node's `wasDerivedFrom` names its aggregation-row
  witness.
- **§7:** unconfirmed groups do not exist in the graph; conflicting keys refuse.

---

## 5. Residues

- **Closes:** the PR #59 `_record_uri` collision minor (silent record merge on duplicate
  paths).
- **Opens:** *groups without a confirmed total* — Port Kembla's rows stay ungrouped (its
  total is blank, arithmetically unverifiable); would close via ditto-fill evidence
  (rowheaders' blank-below convention) cross-checked against H where both exist — deferred
  until a document *needs* it. Registered in `docs/superpowers/residues.md` by this loop.
- The H remainder rows (row-hier/record paths, dense totals, false-positive direction)
  are R4-register items, untouched here.
