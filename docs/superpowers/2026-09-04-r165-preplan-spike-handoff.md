# Handoff — the three PROPOSED claims are MEASURED; the PLAN is next and needs a fresh session

**Topic:** `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` (PR #156) plus this
loop's measurement, `docs/superpowers/2026-09-04-r165-preplan-spike.md`. **No `src/` or `vocab/` file
was changed.** The prototype was applied to the working tree, measured, reverted, and is committed as
an appendix to the spike doc.

**Part 5 was written FIRST**, per `CLAUDE.md` § "The handoff's next action is TYPED", and is graded
per action. This file was authored at **~72,000 working tokens — 1.4x the 50K originating floor**,
which is why the plan is not in it: the maintainer ruled mid-session that the spike evidence lands
here and the plan is written fresh.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

> **Write the plan from `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md`, carrying
> the six corrections in `docs/superpowers/2026-09-04-r165-preplan-spike.md` § "What this changes for
> the plan" and § Q-D. In a FRESH session, under the 50K originating floor.**

Both halves of the contract now exist: the spec states interfaces, invariants and oracles, and the
spike has measured everything the spec left as reading. The plan states interfaces, invariants and
the falsifying oracle — **never a function body** (plan rule 1) — and **cites** the spec rather than
re-deriving it (plan rule 6).

Six things the plan MUST carry, each measured and each contradicting or extending the spec:

1. **Name the run-admissibility predicate in the interface table.** O5's prescribed patch point is
   REFUTED (spike § Q-B B1): `classify_matrix` refuses independently of `is_matrix_candidate`, so
   the oracle must patch the whole disposal, and it can only do that if the function has a name.
2. **Substitute O4's `tab:bandIndex` clause** with the fragment/position equality measured in
   § Q-B B2. That term is emitted at one site and it is not the compile graph (§ Q-D D3).
3. **Decide the rule-x term shape and justify it** — `tab:ruleX` already exists with a different
   domain (§ Q-D D1). Two shapes are laid out there; the plan picks one and says why.
4. **Budget the cost.** `page_bands` roughly doubles on three of six pages, and the corpus's two most
   expensive disposals are REFUSALS (3.06s on gc-stem p0). Spec § 3.2's "a refusal costs nothing" is
   true of the graph and false of the clock (§ Q-A A3).
5. **The test surface is 14 tests in 5 files**, listed with their assertions in § Q-C C3 — not the
   ~20 files § 8.5(d) read off the source. `test_supersession_queries.py` is NOT among them.
6. **Say what the corpus cannot cover**: M1's load-bearing half is unexercised, and adoption's branch
   is never entered on a merged page (§ Q-C item 7). Both are wider than R169 as written.

### PROPOSED — three claims that must be MEASURED before the task resting on them is written

**Each rests on reading or on a substitution, not on running the shipped shape.**

1. **The SPARQL derivation reproduces the Python relation.** The spike computed the § 3.3 relation in
   **plain Python** and says so (§ 0). Nothing shows a `FILTER NOT EXISTS` subsumption over emitted
   `xsd:decimal` facts returns the same 14 runs — rounding, datatype and the `?b = ?a + 1` adjacency
   are all re-expressed in a different engine. **Run the query against the census before writing the
   task that consumes it**; a divergence makes the relation task different work, not a bug to fix
   later.
2. **`test_datagrid.py:907` is fixture drift, not a loss.** Its own message says *"fixture drift: this
   page is supposed to escalate"* and under the prototype the page stops escalating entirely
   (§ Q-C C3 row 3). It is a **guard**, not an index pin. Whether that is the merge working as
   designed or the merge swallowing an escalation the guard exists to catch is **not measured**. If
   it is the second, re-baselining it hides the defect this loop is most likely to ship.
3. **Memoisation is not needed.** § Q-A A3 prices one `page_bands` call; a document compile makes at
   least two per page with no cache. Whether the corpus suite absorbs that, or the disposal has to be
   memoised across calls, is a **design change** if it comes back the wrong way — measure the
   suite wall-clock before committing to "no cache".

### ASSERTED — separable, safe to do first or never

`R167` (the em-dash in `celltype.is_blank`) is a one-line change plus a corpus regression run. Not on
the critical path; closes nothing on p0/p1. Unchanged from the predecessor handoff.

---

## 1. Goal

Measure the three claims the spec's handoff graded PROPOSED, so the plan is written against
measurement rather than against reading.

## 2. Where the primaries are

| where | what to establish there |
| --- | --- |
| `docs/superpowers/2026-09-04-r165-preplan-spike.md` | this loop's whole output. § 0 the prototype and its ONE substitution; § Q-A M1 + the cost table + the refusal finding; § Q-B the O5 refutation and the forced non-tail result; § Q-C the 14 real failures with their assertions; § Q-D the vocabulary/register seams; § "What this changes for the plan"; Appendix the prototype diff |
| `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` | the contract. Still authoritative except where the spike refutes it — § 5 (O4, O5) and § 6 (`tab:ruleX`) |
| `docs/superpowers/2026-09-04-the-run-is-one-band-handoff.md` § 5 | the predecessor's typed part 5, whose three PROPOSED items this loop discharged |
| `src/iladub/etkl/compile.py:270-323` · `:817-840` | the seam and the disposal chain the prototype reused verbatim |
| `src/iladub/etkl/sectiongraph.py:192-245` + `vocab/queries/section-repeat.rq` | the evidence-graph → SPARQL-pairs → Python-assembly idiom the derivation copies |
| `docs/superpowers/residues-open.md` (`R160`, `R165`, `R166`, `R167`) | R165 is the subject; R160 is **not ruled** |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The seam holds — `page_bands` proposes, the untouched chain disposes, a refusal is byte-identical | spike § 0 (smoke), § Q-C C4 (22 modules untouched) |
| M1 costs **+1 `_build_ruled_band` per named band**, not a second page build | spike § Q-A A1, reproducible via the appendix diff + `m1_check.py`'s method |
| O5's patch point is REFUTED; the plan must name the admissibility predicate | spike § Q-B B1 |
| O4's `tab:bandIndex` clause is unsatisfiable; substitute the fragment/position equality | spike § Q-B B2, § Q-D D3 |
| The real test surface is 14 tests in 5 files, all apple | spike § Q-C C2-C4 |
| `tab:ruleX` is not a new term; the term shape is an open plan decision | spike § Q-D D1 |
| The evidence lands here and the plan is written fresh | the maintainer, this session — **recorded nowhere but this file** |
| `R168`/`R169`/`R170` are still the plan's to raise, at tally `43/157`, `43/158`, `43/159` | spec § 7; tally computed in spike § Q-D D5 |
| apple p2, `R167`, `R160`'s ruling and `R166` remain out of scope | spec § 4 |

## 4. Unverified or assumed

- **The relation was computed in plain Python, not SPARQL** (spike § 0). Every run figure in the
  spike inherits that substitution — see part 5's first PROPOSED item.
- **M1's load-bearing half is unexercised on this corpus**: the only page with a non-empty
  `section_repair_bands` (cbh p0) has no candidate run, so "the disposal verdict differs between a
  repaired and an unrepaired build" was never tested. M1 is upheld by construction.
- **Adoption's branch was never entered on a merged page.** `grid_idx == len(page_bands(...))` is
  verified as a count equality (12 == 12), not as a trip through `document.py:1657-1740`.
- **No document score was measured with the membrane on.** Everything ran `validate_shapes=False`;
  the membrane has still never been exercised on a merged band.
- **Whether the new transient evidence graph falls inside `probe_domain_range_agreement`'s
  population was not measured** (spike § Q-D D1).
- **Only three test modules were run by the controller** — `test_doc_governance`,
  `test_source_citations`, `test_residue_register_integrity` (18 passed). The spike ran 28 modules
  (14 failed under the prototype, all apple; 88 passed + 2 skipped on the same files at baseline).
  **The full suite takes ~45 minutes and must not be run in a background subagent.**
- The working-token figure in the preamble is the harness's, logged via `plimslop preflight`.
