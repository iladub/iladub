# Gate the record and transposed paths (Loop J — residue R17)

- **Date:** 2026-07-30
- **Author:** François Rosselet
- **Status:** **Shipped** (2026-07-30, branch `iladub-r17-gate`). Tenth loop of the GrainCorp
  real-document push (A = PR #67 … H = PR #74; I = PR #75). **Measured at close:** both red
  tests reproduce the R17 crash on the ungated code (AssertionError from inside
  `compile_tables` at final validation, independently re-verified by the task reviewer) and
  escalate `REGION_TILING_FAILED` in-band after the gate; healthy-path graphs
  cross-version **isomorphic** with the parent commit for both `simple_table_pdf` and
  `transposed_table_pdf` (scores 1.0 unchanged); GrainCorp unchanged
  (0.9496 / 509 / 15 groups / 17 detected / 33 records, 33 distinct). Full suite 677
  passed / 5 skipped. R17 row deleted from the register. Observation carried in the ledger
  (not a defect): on every gated path, `n == 0` takes the commit branch without consulting
  `region_tiles` — the shared loop G gate shape, pre-existing.
- **Origin:** Residue **R17** (loop G attempt 2 final review): `assert_record_region` /
  `assert_transposed_region` write directly into the output graph with no
  scratch + `region_tiles` gate, so a defective region there still RAISES at
  `compile_tables`' final validation (`AssertionError`, `tab:CoverageShape` at `#table0-c0` —
  demonstrated by dropping one `tab:coversColumn`) instead of escalating in-band. This is the
  same crash class loop G attempt 1 died of, through the two remaining ungated paths.

## 1. Purpose and scope

Give both remaining direct-assert sites the exact membrane backstop the hierarchical
(loop G), matrix and row-hier (loop C) paths already have:

> assert into a **scratch `Graph()`** → `region_tiles(scratch)` → merge on pass, escalate
> **`REGION_TILING_FAILED`** in-band on fail. Never crash.

**Sites (both in `src/iladub/etkl/compile.py`):**
- the transposed branch (~line 196: `assert_transposed_region(graph, …)`),
- the record branch (~line 245: `assert_record_region(graph, …)`).

**Approach decision:** inline gate per site, byte-matching the loop G pattern. REJECTED: a
shared `_gated_assert` helper refactoring all five sites — it would touch three shipped
gates whose accounting differs per path, for zero behavioral gain.

**Non-goals:** no new vocab, no new shapes, no constants, no accounting change on the
commit path.

**Success criteria:**
1. The R17 repro (corrupt the assert output by removing one `coversColumn` triple) compiles
   with an `escalated` / `REGION_TILING_FAILED` report and **no exception** — on each path.
   On main today the same repro raises `AssertionError`. Red first.
2. **Byte-identical when healthy:** the shipped record and transposed fixtures compile to
   graphs **isomorphic** with main's, with identical scores — the gate is invisible for
   well-formed regions.
3. GrainCorp unchanged: 0.9496 / 509 (failure condition, the structural-loop pattern).
4. Full suite green (baseline 673 passed / 5 skipped). Accepted measured cost: one
   `region_tiles` call (~75 ms, loop H review's measurement) per record/transposed region.
5. R17's register row is **deleted** (closed fully — these were the last direct-assert
   region paths), and loop G's compile.py NOTE comment no longer claims the record/
   transposed paths are ungated.

## 2. Components

### 2.1 The transposed site

Current: `n = assert_transposed_region(graph, region, table_uri, _DOC, page_number)` then
round-trip accounting + an `asserted` report. New: assert into `scratch`; if
`n and not region_tiles(scratch)` → `escalate_region(graph, cand_uri, _DOC, ascii_view,
"REGION_TILING_FAILED", TAB.RecordTable, 0.4)`, `escalated_total += band tokens`, report
`("escalated", 0, "REGION_TILING_FAILED", str(TAB.RecordTable))`; else `graph += scratch`
and the existing accounting verbatim. (The transposed path asserts a `tab:RecordTable` —
the anchor matches what it builds.)

### 2.2 The record site

Same transformation around `assert_record_region`, anchor `TAB.RecordTable`.

### 2.3 Comment + register

Loop G's backstop NOTE in compile.py (~line 325) drops its "record and transposed paths are
STILL direct-assert — residue R17" sentence (now false). `docs/superpowers/residues.md`
deletes the R17 row in the same change (the register rule: a loop that closes a residue
deletes its row).

## 3. Testing

New file `tests/etkl/test_r17_gate.py`:
- **Red, record path:** monkeypatch `iladub.etkl.compile.assert_record_region` (imported at
  module top) with a wrapper that calls the real function then removes one
  `tab:coversColumn` triple from the target graph; compile the shipped `simple_table_pdf`
  fixture → must NOT raise; report verdict `escalated`, reason `REGION_TILING_FAILED`.
- **Red, transposed path:** same via `iladub.etkl.holon.assert_transposed_region` (imported
  inside the branch, so patch at the holon module) over `transposed_table_pdf`.
- **Healthy-path guards:** for `simple_table_pdf` and `transposed_table_pdf`, the compile
  still yields verdict `asserted` with no `REGION_TILING_FAILED` report and the score the
  shipped tests pin — a committed test cannot diff against main in-process, so the true
  cross-version check is (a) the full-suite regression net (every shipped record/transposed
  test), and (b) a one-off controller probe during Task 2 comparing the HEAD graph with the
  pre-change graph via `rdflib.compare.isomorphic` (recorded in the ledger, not committed).
- **GrainCorp** (controller, local): criteria §1.3.

## 4. Gate & discipline

Pure control-flow hardening: PROCEDURAL engine glue around an existing closed-world SHACL
membrane (`region_tiles` — the loop C oracle). No new decision, no constant, no language.
Honest failure: a defective region now escalates with its ascii view carried, instead of
killing the whole document's compile (§7: the other regions' evidence survives).

## 5. Residues

- **Closes R17** (row deleted).
- No new residues expected; if the isomorphism guard surfaces a healthy-region behavioral
  delta, that is a defect in this loop, not a residue.
