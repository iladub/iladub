# Loop 8-pre · header-span coverage repair — short parent over a wide span

**Status:** design (approved 2026-07-09)
**Loop:** hardening prerequisite for [Loop 8a — denormalization evidence](2026-07-09-aggregation-evidence-design.md)
**Builds on:** Loop 2 (`headers.infer_header_tree`).

## Why this exists — a short parent label under-covers its span

`infer_header_tree` recovers a merged column-header's span from the parent label's **text extent**
(center-of-mass symmetrization). A **short** parent label over a **wide** column span **under-covers**:
probed on `main` (2026-07-09), a `Region` header centered over four wide numeric columns
(`North South East West`) is recovered as covering only `[1,2,3]` — `West` (col 4) is **orphaned** (no
level-0 parent). The tree still tiles for SHACL (West is covered by its own leaf node), so it compiles — but
the **parent span is wrong**, and any consumer that reads the tree as structure (Loop 8a's dimension recovery:
`Region` would yield `{North,South,East}`, missing `West`) inherits the error.

Loop 6 solved this for the *matrix* path with a proximity builder, but only there (data-columns-only,
single-word labels). A general replacement is unsafe — proximity splits multi-word labels (`Current Visit` →
`Current`/`Visit`) and mishandles wrapped lines (`(SI)`) (probe-confirmed). So the fix is a **narrow,
additive coverage-repair**, not a re-inference.

## §1 — Scope & closing target

- **The fix:** in `infer_header_tree`, after building the text-extent spans and **before** parent linking,
  **extend** each coarse (non-leaf) header node to absorb **contiguous adjacent** leaf columns that have **no
  parent at that node's level**, excluding the leftmost (stub) column. Only extends; never removes or overlaps.
- **Closing proof:** a `Region`-over-`{North,South,East,West}` fixture → the level-0 `Region` node covers all
  four leaf columns (`West` no longer orphaned), and `West`'s leaf node links `parentHeader Region`; **every
  existing hierarchical / pivot / matrix / row-grouped fixture is byte-for-byte unchanged** (they already
  tile, so no repair fires).
- **Out of scope:** multi-word / wrapped label handling (already correct via text-extent — untouched);
  proximity re-inference; row-axis stubs (this is column-header span repair).

## §2 — The repair (probe-verified)

`repair_coverage(nodes, ncols) -> nodes`:
1. Compute, per non-leaf level `L` (any level with children below it), the set of leaf columns **covered** by
   an `L`-node.
2. An **orphan** at level `L` = a leaf column not covered at `L`, **excluding column 0** (the stub — the
   leftmost column is by convention the row-identifier and must remain its own orphan-promoted dimension).
3. For each orphan `c` (ascending), find an `L`-node whose span is **immediately adjacent** (`max(covers)==c-1`
   or `min(covers)==c+1`) and extend that node's `covers` to include `c`. Absorb into the adjacent node only;
   do not bridge across a gap already owned by another node (preserves no-overlap + contiguity).

Applied inside `infer_header_tree` before parent-linking, so the extended parent correctly becomes the
`parentHeader` of the absorbed leaf's node (its `covers ⊆` the extended parent's). The repair is a **no-op**
when the tree already tiles (no orphans) — hence zero regression on existing fixtures (probe-confirmed on the
`Current Visit`/`Prior Visit` pivot: unchanged).

**Why it is safe (not a tuned heuristic beyond the stub rule):** it only ever *adds* an orphaned leaf to a
*spatially adjacent* parent, so the result still tiles (the downstream `tab:` SHACL — coverage, no-overlap,
refinement, unambiguous access — remains the certifier). The single convention it applies is
**column 0 is the stub** (the dominant report layout); a table with a genuinely different stub position is a
documented edge, and its leaf simply stays orphan-promoted (its pre-repair behaviour).

## §3 — Proof of closure (tests)

1. **`test_short_parent_covers_full_span`** — a `region_pivot` fixture (single `Region` parent over four wide
   numeric leaf columns + a `Year` stub) → the level-0 `Region` `HeaderNode` `coversColumn` all four leaf
   columns; `West`'s leaf node has `parentHeader Region`; the holon conforms to the `tab:` SHACL.
2. **`test_repair_noop_on_tiling_tree`** (unit) — `repair_coverage` returns the input unchanged for a tree that
   already tiles (the existing pivot's node set).
3. **`test_stub_not_absorbed`** — column 0 (`Year`) is **not** absorbed into `Region`; it remains its own
   orphan-promoted level-0 node.
4. **No regression (the critical guard)** — the existing pivot, crosstab, hierarchical, and row-grouped
   fixtures compile identically (same header-node covers); full suite green.

## §4 — What's notable

A minimal, additive repair that fixes a real structural error (a short dimension label under-covering its
pivoted values) without re-opening the text-extent inference that correctly handles multi-word and wrapped
headers. It fires only on coverage gaps, extends only into adjacent orphans, and leaves the `tab:` SHACL as the
arbiter — so it cannot introduce a non-tiling tree. It is the prerequisite that lets Loop 8a read a
single-spanning-parent pivot (`Region → {North,South,East,West}`) as a named dimension end-to-end.

## Module map

| File | Change |
|------|--------|
| `src/iladub/etkl/headers.py` (modify) | add `repair_coverage`; call it in `infer_header_tree` before parent-linking |
| `tests/etkl/fixtures.py` (modify) | add `region_pivot_pdf` (single spanning parent over wide numeric leaves + stub) |
| `tests/etkl/test_headers.py` (modify) | `test_short_parent_covers_full_span`, `test_repair_noop_on_tiling_tree`, `test_stub_not_absorbed` |
| `tests/etkl/test_hierarchical.py` / `test_closing_slice.py` | assert the existing pivot's covers are unchanged (regression) |
