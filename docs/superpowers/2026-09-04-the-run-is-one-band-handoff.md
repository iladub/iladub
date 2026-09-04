# Handoff — the R165 spec is written; the PLAN is next and needs a fresh session

**Topic:** `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` (PR #156). The spec is
complete, its relation is MEASURED and its two instruments are committed. **No code was written.**

**Part 5 was written FIRST**, per `CLAUDE.md` § "The handoff's next action is TYPED", and is graded
per action. **This file was authored at ~117,000 working tokens — 2.3× the 50K originating floor** —
which is why the plan is not in it. Parts 1-4 are pointers and do not degrade; part 5's PROPOSED
half is the part to re-derive from the spec rather than inherit.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

> **Write the plan from `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md`, in a
> FRESH session, under the 50K originating floor.**

The spec is the contract and it is finished: § 2 classifies both decisions under CLAUDE.md §8, § 3
fixes the seam and the invariant, § 5 gives five falsifying two-sided oracles, § 6 gives every
signature, § 7 names the three residues to raise, § 8 lists what is unverified. **The plan states
interfaces, invariants and oracles — never a function body** (plan rule 1), and cites the spec
rather than re-deriving it (plan rule 6).

Read, in this order, and nothing else to start: the spec in full (510 lines), then
`compile.py:269-323` (`page_bands`, whose docstring is the contract), then
`sectiongraph.py:178-245` (the idiom being reused).

### PROPOSED — three spec claims that must be MEASURED before the task that depends on them is written

**Each rests on reading, not on running. If one fails, the task built on it is the wrong task.**

1. **M1 is implementable, and what it costs.** § 3.1 requires the run partition to be a pure function
   of the `section_repair=False` build. That the *rules* are section-repair-invariant IS measured
   (`compile.py:73-106`, "sub_rules passes through UNTOUCHED"); that the *disposal* can be run on an
   unrepaired build and the partition then applied to a repaired one is **not**. MEASURE what that
   costs — one extra `_build_ruled_band` per named band, or a whole second page build — before
   writing the task. § 3.5's budget is what it has to fit inside.
2. **O5's technique works.** § 5 forces the non-tail case by patching the *disposal* (not the
   geometry) to accept bfs p5's `(2,5)` run on a 15-band page. Nothing shows the patch point is
   reachable from a test, or that `compile_document` survives a forced non-tail merge on bfs.
   **Run it as a spike before writing the task.** If it fails, `R169` is not closable by this loop
   and the spec's § 5 needs a substitute — say so; do not weaken the assertion (plan rule 1).
3. **Which of the 20 index-pinning tests actually change.** § 5's own instruction. The list in spike
   § 8.5(d) is read off their source, never off a failing run, and § 8 flags it unverified. Run them
   against a merged compile and report the real list.

### ASSERTED — separable, safe to do first or never

`R167` (the em-dash in `celltype.is_blank`) is a one-line change plus a corpus regression run. It is
**not** on this loop's critical path and closes nothing on p0/p1.

---

## 1. Goal

Write the spec the predecessor loop deferred to a fresh session, having first MEASURED the band-run
relation it was forbidden to assume.

## 2. Where the primaries are

| where | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` | the whole contract. § 2 the §8 classification; § 3.0-3.2 seam + M1 + fallback; § 3.3 the measured relation with Q1-Q4; § 3.5 the cost; § 5 the five oracles; § 6 the signatures; § 7 the residues; § 8 what is unverified |
| `scripts/band_run_census.py` | the relation census, **committed this loop**. Re-run it (~4 min) rather than trusting § 3.3's tables |
| `scripts/band_run_cost.py` | 266 contiguous runs corpus-wide — the measurement that rejects the no-relation design |
| `docs/superpowers/2026-09-04-one-band-matrix-spike.md` § 7-8 | the predecessor's evidence the spec builds on: the refuted licence, and the band-index inventory (§ 8.5 is the call-site list; § 8.6 is what it does not settle) |
| `src/iladub/etkl/compile.py:269-323` · `:602,:615` · `:817-840` | `page_bands`' pinned band-index contract; where `compile_tables` consumes it; the disposal chain to reuse |
| `src/iladub/etkl/sectiongraph.py:178-245` + `vocab/queries/section-repeat.rq` | the evidence-graph → SPARQL-pairs → Python-assembly idiom being copied |
| `docs/superpowers/residues-open.md` (`R160`, `R165`, `R166`, `R167`) | R165's row is the loop's subject; R160 is **not ruled** |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The relation is **adjacent subsumption** over distinct rule x-positions, not equality | spec § 3.3, with the census reproducible from `scripts/band_run_census.py` |
| The merge is a **proposal** disposed by the existing `classify_matrix` + `region_tiles` chain; **no new oracle, no new shape** | spec § 2 (D2), § 3.2 |
| The merge lives in **`page_bands`** and nowhere else — one index space | spec § 3.0 |
| **Invariant M1** — the partition is a pure function of the `section_repair=False` build | spec § 3.1 |
| D1 classifies **AXIOM** (not NEURAL) because it enumerates candidates and settles nothing | spec § 2 (D1), and the 266→14 pruning in § 3.5 is the load-bearing half of the argument |
| **No runtime no-regression guard**; the hazard is made falsifiable by oracle O3 instead | spec § 3.3 (last block), § 5 O3, `R168` |
| Two new `tab:` terms (`tab:RuledBand`, `tab:ruleX`) + one new `.rq`; no numeric literal | spec § 6 |
| `R168`/`R169`/`R170` to be raised **by the plan**, not by this loop | spec § 7 — **the register rows do not exist yet** |
| apple p2, `R167`, `R160`'s ruling and `R166` are all **out of scope** | spec § 4 |
| The two measurement instruments are committed rather than left scratch | commit `f586a4f`; spec § 3.3, § 3.5 |

## 4. Unverified or assumed

- **Nothing in the spec's § 3 is implemented or run.** Every figure comes from merging bands *after*
  `page_bands` returned.
- **The three PROPOSED items in part 5 are the concentrated form of this section.** M1's cost, O5's
  technique and the real regression list are all read, not run.
- **No document score was measured this session.** `0.1895 → 0.6289` is the predecessor's, taken with
  `validate_shapes=False` — **the membrane has never been exercised on a merged band.**
- The relation is **adjacent and transitively chained, never pairwise-total**; a page whose chain
  drifts through incomparable endpoints is unmeasured (none occurs on this corpus).
- `merge_bands`' `column_xs` provenance on the longer runs was not audited.
- The 2dp rounding in `_rule_xs_signature` is inherited, not justified; subsumption is more sensitive
  to it than equality was, and that sensitivity is unmeasured.
- **`R170` names the gap that would most embarrass this loop:** "124 entries vs 48 cells today"
  compares two different counters, and no content diff has ever been run — nothing shows the 48 cells
  asserted today are all present among the 124.
- Suite: only `test_doc_governance` + `test_source_citations` + `test_residue_register_integrity`
  were run (18 passed). **The full suite takes ~45 minutes and must not be run in a background
  subagent** — a measured trap.
- The working-token figure in the preamble is the harness's, logged via `plimslop preflight`; the
  spec itself was authored under the floor and part 5 of this file was not.
