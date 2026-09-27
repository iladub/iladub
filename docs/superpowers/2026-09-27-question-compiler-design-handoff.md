# Handoff — the question compiler: design sections 1–3 approved, the slice waits on a measurement (2026-09-27)

**Serves:** maintenance — carries the approved design sections of the question compiler to the session that writes its spec; it meets no criterion itself

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `jev-reading-handoff`

**Doc impact: none.**

Written early (~35,000 working tokens, under the 50K originating floor), part 5 first.

## 5. Next action

**Asserted:** read the cbh/bfs failure measurement (§ 4 of this file says where it lands; if it is not
there, re-run it — the brief is in § 2), then re-present **design section 4 (scope and the first
slice)** to the maintainer, choosing the slice from the measured failure causes. Then write the spec
to `docs/superpowers/specs/2026-09-2x-question-compiler-design.md`. Sections 1–3 are approved (§ 3);
do not re-present them.

**Proposed, open to refutation:** the slice is the question kind whose oracle already exists *and*
whose reading judgement is what fails on cbh or bfs. If the measured failures sit on a judgement with
no oracle (base band cut, data-grid columns), the first loop builds that oracle, not a worker (§ 8,
*no oracle, no worker*).

## 1. Goal

Specify etkl as a question compiler (Jev proposes over linearised text; host derives closed options
with abstain; geometry/SHACL dispose; vision escalates), with a first slice judged on corpus N/7.

## 2. Where the primaries are

- The previous handoff and its evidence: `2026-09-27-question-compiler-spec-handoff.md`,
  `2026-09-27-jev-spatial-text-and-geometry-refusal-evidence.md` (Probe A/B),
  `2026-09-27-jev-reading-architecture-handoff.md` § 2a (Jev's measured behaviour).
- Stage inventory (measured this session by a subagent; re-open the files, not this list):
  `compile_tables` `src/iladub/etkl/compile.py:861`; boxhead `dispose_boxhead` `etkl/boxhead.py:150`
  (set equality at `:173`); row roles `rowrole.py:274` (BAML, disposed by `region_tiles`
  `tiling.py:74`); word-level ink booking `_book_recovered_ink` `compile.py:333`;
  `tab:HeaderContentConservedShape` `vocab/shapes/tab-shapes.ttl:256` (CONTAINS matching);
  `tab:Conservation` (G6) `vocab/ontology/tab-datagrid.ttl:214`, **declared, implemented nowhere**;
  `GridColumn.is_measure` `etkl/datagrid.py:99` (consumers `:120`, `:490`, `:651`).
- Tuned constants found: `gap_factor=1.8` (bands.py:44), `0.25`/`0.5×pitch`, `±0.1` (headers.py
  :195/:268/:287/:387), `gutter_pct=0.98` (grid.py:92), `GAP=4.0` + `±0.5` slops (datagrid.py),
  `EPS=0.5` (roundtrip.py:60).
- The cbh/bfs failure measurement brief: run both documents serially as `tests/test_corpus.py`
  does, record per-page diagnostic codes, attribute score loss to the reading judgement and the
  function that made it, MEASURED vs INFERRED. Criteria: `tests/arc-manifest.ttl:255` (etkl:03),
  `:276` (etkl:05); their `proposedDependsOn` rationales (`:1732-1748`) cite a 2026-08-20
  adjudication and are presumed stale.

## 3. What was decided, and where

Approved by the maintainer in session 2026-09-27; recorded **nowhere but this file** until the spec
is written:

1. **The unit is a compiled question**: subject, `etkl:QuestionKind`, options by a named SPARQL
   derivation *always including abstain*, state = reading-order lines without coordinates, oracle
   IRI. Recorded and replayed (hash of state+question+options). Admission by oracle, never by
   confidence. Admitted → `dec:DecisionHolon` whose rationale is derivation IRI + oracle IRI, no
   model prose. Refused/abstain → today's derivation; vision (Sonnet) only if the derivation
   disagrees or does not exist. Kinds live in an RDF registry; a SHACL shape requires
   `etkl:optionsBy` and `etkl:disposedBy` (min 1 each).
2. **Coarse-to-fine rounds**, one batched Jev call each, each compiled only over what earlier rounds
   admitted: page → regions → structure → roles → grounding. A round without an oracle keeps its
   derivation. Corrections from the inventory: the base band cut has no oracle (only merged runs
   do); `round_trip` is not in compile (round 3's oracle is `region_tiles` + `cell_round_trips`);
   grounding is downstream of `compile_tables`; row roles already have a BAML worker.
3. **Oracle coverage**: drop *not a header* from the roles options — every word of an admitted
   boxhead takes a positive role (leaf/continuation, spanner via R1, note mark = exact marker match
   in the admitted notes region, unit = exact vocabulary lookup) or abstains. Implement G6 and make
   `HeaderContentConservedShape` exact rather than CONTAINS. Title-vs-spanner stays on the derivation
   until the stub defect is fixed (R2); a **new register row** for `is_measure` (none exists; R214/R215
   are neighbours). The spec's first gate: re-run Probe B with positive-role options; any false
   refusal on the Sonnet null control withdraws the check that made it.
4. **Section 4 was NOT approved.** The proposed slice (Jev-first grid boxhead, `ReadBoxhead` as
   escalation) was flagged as possibly not moving N/7; the maintainer ruled: **measure why cbh and bfs
   fail first**, and choose the slice from that.
5. Client choice proposed and not contested: a thin direct HTTP client to Cloudflare Jev (keeps
   probabilities; no BAML v1 migration).

## 4. Unverified or assumed

- The cbh/bfs failure measurement was running in a subagent when this was written. Its result, if
  it landed, is appended below this heading; if nothing is appended, it did not land — re-run it.
- Probe A/B rest on 5 pages, one run per condition, Sonnet as reference not ground truth.
- Latency ~2 s/page for five rounds is argued from ~0.4 s/call, not measured.
- Whether the positive-role option set helps Jev or hurts it is unmeasured (that is the first gate, § 3 item 3).

**The cbh/bfs measurement LANDED (subagent, HEAD `9673199`, `BAML_LIVE` unset; scratch outputs are
non-durable, re-run before relying).** Neither document is held by its score; both are
`cor:Unadjudicated` with no floor, held by their 2026-08-20 adjudications:
- cbh 0.9095 (804/80). The 80 escalated tokens are 4 × 20 header words that ARE carried as
  `tab:LabelCell`s but booked escalated by the ledger at `compile.py:1438-1440` (`n` counts entry
  cells only): a bookkeeping gap. The real misreading, invisible to the score: `#table9` fuses the
  "Stock at Port" table, the side-by-side "PORT MAINTENANCE SHUTDOWN DATES" table and the disclaimer
  into one 2-column table, with whole stock rows as single cells (band cut / `regions.classify`,
  attribution INFERRED).
- bfs 0.9021 (1263/137). p5's one page-scoped data grid spans T1 (years) and T2 (Suisse + 26
  cantons, 270 cells under T1's labels); T2's boxhead escalated separately (band 8); T2's columns
  are also misplaced (Zurich c4 holds Décès). Judgements: table extent (`derive_data_grid`,
  page-scoped, MEASURED) and column placement (`_place_for_emit`, INFERRED).
- Common judgement: **table extent**, i.e. how many tables and where each ends. That is round 2, not
  the boxhead-roles round proposed in section 4.
