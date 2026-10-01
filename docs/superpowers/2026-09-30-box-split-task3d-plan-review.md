# Review: box-split Task 3d plan, adversarial, before SDD (2026-09-30)

**Topic:** box-split · **Date:** 2026-09-30

**Serves:** prog:criterion:etkl:03 — O2 (`tab:12`) is whole only when T2 compiles with no boxhead.

**Doc impact: none.** This reviews a plan. It changes no vocabulary and no released page.

**Subject:** Task 3d in `docs/superpowers/plans/2026-09-28-box-split.md` (`6d23e2f`), against spec
§ 10.5 + § 10.7 and CLAUDE.md § Plan authoring discipline, rules 1–7. The maintainer asked for this
review before SDD dispatch (2026-09-30, in chat).

**How it was measured.** A read-only subagent checked every code citation at HEAD `6d23e2f`, with
commands and outputs. Its report was not committed; the facts used below are quoted with their
`file:line`. The review was drafted at ~33K working tokens and written up at 52.7K, which is over the
originating floor. The override was logged, and each finding below is graded.

## 5. Next action (written first)

- **Asserted.** A fresh session amends Task 3d with findings A1–A5 and the minors, and appends the
  amendments to the plan, not to this file. Then SDD dispatches from 3d.0. None of the findings
  changes the spec's contract; each changes how a sub-task pins or measures it.
- **Proposed, and it may fail:** A6 is a real leak. It rests on reading, not a run, and it is
  settled by the MEASURE it asks for. If adopted tables carry their pass's log into the document,
  A6 does not land.

## Findings

### A1 (Important, asserted): U11's identity test is incoherent, and its falsification fails for the wrong reason

- The plan says the default call is "**isomorphic** (`rdflib.compare.isomorphic`) to the graph the
  unmodified function produces. Capture that graph in the test from a pinned count plus the
  header-label texts." A count plus texts is not a graph, so there is nothing to test isomorphism
  against.
- The FALSIFICATION line "default `header_lines` to 0 and U11's byte-identity fails" is inherited from
  spec § 10.5. Under this plan it fails **through the producer guard**: `header_lines=0` with
  `absent_by=None` raises `ValueError`. So it would fail even if the identity assertion pinned
  nothing, which is the defect-5 shape (rule 4).
- **Amend:**
  - Capture the reference graph as committed canonical N-Triples, generated at 3d.0's base commit
    from the RECORD fixture, and assert isomorphism against it.
  - Falsify with a perturbation that does not raise, for example dropping one `tab:LabelCell` on the
    default path, and show the identity fails.

### A2 (Important, asserted): Review Focus 1's test cannot see the property it names

- The ask site is on the RECORD path of `compile_tables`, and every pass runs that path: page
  (`document.py:1471`), `/r2` (`:1533-1534`) and `/adopt` (`:1669-1671`). The boxhead reader, by
  contrast, is asked only on the adopt pass (`compile.py:1683`, `:1702`). So this is the first
  worker asked on **every** pass, up to 3× per region.
- The dedupe lives in the live reader's cache. `boxhead.py` keeps it in the **module-global**
  `_BOXHEAD_CACHE` (`:95`; the plan cites `:103`). `RecordedBoxheadReader` re-reads the file on every
  call, and `FakeBoxheadReader` caches nothing.
- The plan's test ("count the fake's calls when the reader dedupes by key") uses a fake that does
  not dedupe. It either counts passes or tests a fake written to pass.
- The plan also constructs a reader per region (`headerlines.default_reader()` at the site), so an
  **instance** cache would dedupe nothing.
- **Amend:**
  - The cache is module-global, like `_BOXHEAD_CACHE`.
  - Pin it by stubbing the generated BAML function with a counter, building two
    `BamlHeaderLinesReader` instances, and asking the same question through each. Expect one call.
  - Falsify with the cache made per-instance.

### A3 (Important, asserted): MEASURE (i) is told 5 modules, and there are 6

- `grep -rn hasHeaderNode src/` finds `src/iladub/feed.py:325, 383, 661`, beyond the five § 10.2
  names (`rowgroups`, `denormalization`, `boxhead`, `document`, `holon`).
- `feed.py` is where carriage leaves for consumers. A reader there that assumes ≥ 1 header node
  would make a headerless table carry nothing, and CI would stay green.
- **Amend:** name `feed.py` in 3d.3's MEASURE (i). The plan's "re-grep" instruction would find it,
  but a plan that asserts 5 invites the implementer to stop at 5.

### A4 (Important, asserted): 3d.1 misses two measured forcing functions

- **Engine parity is not hypothetical.** Three tests evaluate `tab-shapes.ttl` under rudof:
  `test_membrane_equiv.py:26,39`, `test_closure_equiv.py:27,214` and `test_membrane.py:18`. The
  guards added to two `sh:sparql` `sh:select` shapes, and the two new shapes, must pass on both
  engines. The rudof blank-node `sh:sparql` pin (PR #100) is the known trap.
- **`test_vacuity_registry.py:343`** (corpus-gated, so CI is blind to it) requires every wired shape
  that stays idle on the corpus to be listed in `VACUITY_REGISTRY`. Both new shapes are likely idle,
  because a conforming corpus never makes them fire.
- **Amend:**
  - Name both in 3d.1's MEASURE (v).
  - Measure what "idle" means in that test before 3d.7's sweep finds it red.
- The plan's "prove the grep with a control" stands. `test_compile_membrane_shapes.py:320-334`
  (tiling ⊆ declared) is the set-based test the new tiling IRI must satisfy.

### A5 (Important, asserted): "exactly what the RECORD path's other callers pass" does not exist

- The RECORD path's `grid_evidence` callers disagree:
  - `orientation.py:36,59` passes **no** `unshown`;
  - `headers.py:111` and `rowheaders.py:33` pass `unshown=band.unshown`.
- There is also a join seam. `grid_evidence` mints `urn:iladub:evidence:cell-%d` keyed on the
  **enumeration index** (`celltype.py:22`, `:174`), not on `(row, col)`, as the plan says it does.
  It builds a fresh local graph, so there is no side effect on the unshown carriage (that lives in
  `holon._UnshownCarriage`, `:46`, `:92`).
- **Amend:**
  - Pass `unshown`, and say why.
  - State that `tab:UnshownInk` must contribute **no** datatype family, or a row-0 unshown cell
    becomes a false witness. Pin it with a U9 case.
  - Join the style facts through `tab:atGridRow` / `tab:atGridColumn`, not through the IRI.

### A6 (Important, **proposed**): the statement may dangle when a table is adopted from another pass

- § 10.7 attacked withdrawal: a table leaving the document. Remedy (a) keeps the statement triple
  and leaves the decision in the log. The reverse direction was not attacked: a table **merged in**
  from a pass graph (`:1549` pass-2 merge, adoption from `/adopt`).
  - Its `header_lines` decision was minted into **that pass's** log.
  - After remedy (a), `_band_subgraph` no longer brings the decision along.
  - If nothing else merges that pass's log into the document graph, the statement's object is a
    decision the document does not hold, and `BoxheadAbsenceDecidedShape` refuses it at any scope
    that validates the merged graph.
- `_band_reading_subgraph` (`document.py:1032`) may already carry the band's log. § 10.7 called the
  pass-2 merge "probably duplicative" next to it, **unmeasured**. For adoption, nothing measured
  says which log arrives.
- **Amend:** extend 3d.2's MEASURE (vi) with the merge-in direction: for a table taken from `/r2`
  and from `/adopt`, does its decision arrive in the document graph? Add a U14 case for it. If it
  does not arrive, this is a plan finding (the § 10.7 rule), not something to patch silently.
- **Also for MEASURE (vi):** `src/iladub/feed.py:117` has a `while queue:` loop that nobody opened.
  Classify it: is it a reachability closure over a table or not?

## Minors (asserted)

- Citation drift: `_BOXHEAD_CACHE` is at `boxhead.py:95` (not `:103`), and the span-donation
  `continue` is at `compile.py:1281` (not `:1283`). `document.py:1049`/`:1126` are the `while
  frontier` lines; the defs are at `:1032`/`:1111`.
- The listing unit: the question counts "lines", while the closed check is against "the region's
  row count". State that a listing line **is** a region row. A wrapped cell spanning two text lines
  must not change `nlines`.
- The model: `clients.baml` `Claude` is Haiku 4.5. The `ClaudeLongAnswer` comment records Haiku at
  68/110 against Sonnet-5's 109/110 on a region question. The plan already cites that comment as
  precedent; keep it that way (measure first, do not pre-switch).

## Checked and not landing

- **Tiling failure on a `0` region** (Review Focus 2): `assert_record_region` writes to `scratch`
  (`compile.py:1284`), `region_tiles(scratch)` follows (`:1285`), and a failing region never merges
  scratch (`graph += scratch` only at `:1304`). The decision, recorded into `graph` by `brec`
  (`compile.py:994`, `decisionlog.py:39`), stays. The plan's expectation is right.
- **No closed shape** in `vocab/shapes/` targets `tab:RecordTable` (`grep sh:closed` → none), so the
  new property is not refused by closure.
- **In scope at the site:** `pdf_path`, `page_number` (`compile.py:935`) and `brec` (`:994`). The
  `record` signature matches the plan's call.
- **Row-0 tests:** only `holon.py:196`, `:205` and `compile.py:1323`, `:1331`. The plan's list is
  complete.
- **Rules 1, 5 and 6:** no function body, no test asserts behaviour § 10.6 scopes out, and the
  contract is cited, not re-derived.
