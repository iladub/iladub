# Handoff — all three PROPOSED claims are CONFIRMED; the PLAN is next and still needs a fresh session

**Topic:** `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` (PR #156) plus the two
measurement docs beneath it — `docs/superpowers/2026-09-04-r165-preplan-spike.md` and this loop's
`docs/superpowers/2026-09-04-r165-three-claims-measured.md`. **No `src/` or `vocab/` file was
changed.** The only tracked additions are `scripts/doc_walltime.py`, two register rows, and the two
docs.

**Part 5 was written FIRST**, per `CLAUDE.md` § "The handoff's next action is TYPED", and is graded
per action. This file was authored at **~110,000 working tokens — 2.2x the 50K originating floor**,
which is why the plan is *again* not in it. That is the finding this loop should be read for as much
as its three verdicts: **measuring the claims a handoff types PROPOSED, and then writing the plan
that rests on them, does not fit in one session on this repo.** Two loops in a row have now been
spent discharging propositions rather than writing the plan. The plan is the next loop's whole job
and it now has nothing left to measure.

**Doc impact: none.**

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, the outcome is known and doing it is the work

> **Write the plan from `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md`, carrying
> the six corrections in `docs/superpowers/2026-09-04-r165-preplan-spike.md` § "What this changes
> for the plan" AND the nine below. In a FRESH session, under the 50K originating floor. Nothing is
> left to measure first.**

The six predecessor corrections are unchanged and still hold. **Nine more**, each measured this
loop, each contradicting or extending the spec:

1. **Spec § 3.4 asks for two incompatible things and the plan must pick one.** Adjacency as
   `?b = ?a + 1` *and* "no numeric literal" cannot both hold. Take the **literal-free** form — the
   emitter emits the predecessor index as a fact and the query joins on it — because
   `vocab/queries/section-repeat.rq:15` makes "no numeric literal" a standing property of the idiom
   § 3.4 says this loop copies. Both forms were measured at 14/14 (evidence § A.2).
2. **Pin the emitter's honest abstain with a test; the `.rq` cannot defend it.** A band node with
   zero rule-x facts joins *every* adjacent band in both directions — SPARQL `[(0,2)]` where Python
   says `[]`. This is the derivation's only silent-divergence mode (§ A.1).
3. **The domain fork covers `tab:bandIndex` too, not just `tab:ruleX`** — it is declared
   `rdfs:domain tab:SectionBand` (`vocab/ontology/tab.ttl:302`). Spec § 6's `run_evidence` contract
   hits it on both properties (§ A.5).
4. **`probe_domain_range_agreement` does NOT grade the new graph** — its population is
   `compile_tables(...).graph` alone (`scripts/probe_domain_range_agreement.py:265`). The term-shape
   choice is a modelling-honesty decision, not a gate-passing one, which removes the argument
   § Q-D D1 leans on (§ A.5).
5. **A band index emitted as a string derives `[]` silently** — no error. Emit `xsd:integer`, as
   `sectiongraph.py:205` already does (§ A.2). And `NOT EXISTS` matches by **term**, not value, so
   the derivation is sound only while one emitter produces every x; the shipped
   `Literal(Decimal(str(round(r.x, 2))))` is lexically canonical across all 3,668 corpus literals
   (§ A.3).
6. **`test_datagrid.py:907` is fixture drift and the ink is fully accounted for** — 70 escalated →
   42 asserted + 0 escalated + 28 counted-nowhere, where the 28 are exactly the stub column the
   matrix-asserted branch has always excluded (`compile.py:843-851`). **But re-baselining is not a
   one-line edit**: apple p1 stops escalating, so the guard loses its witness and `:908`/`:909` go
   vacuous. A new fixture page is required (§ B, § B.1).
7. **Budget the cache separately, and do not fold it in.** +27.8 s of `page_bands` on a 312 s corpus
   compile (~9%) — affordable. But a perfect `(pdf, page, srb)` cache returns **41.54 s**, more than
   the change costs, and that win predates this loop. Raised as **`R168`** (§ C).
8. **`section_candidates` is a THIRD index-keyed flow reading the merged partition**
   (`document.py:1487-1490`), sound only because of M1. Spec § 3.0 names carriage and adoption and
   not this one (§ D.2).
9. **Two cheap pins worth having**: `merge_bands` covers all 8 `Band` fields
   (`bands.py:16-34`) and a ninth would be silently defaulted — assert the field count in the merge
   test; and `scripts/band_run_census.py:111` hard-codes an absolute corpus path, which defeats the
   reason it was committed (§ D.4, § D.5).

### PROPOSED — one claim that must be MEASURED before the task resting on it is written

**apple page 2 is the right replacement fixture for `test_datagrid.py:907`.** Measured: under the
prototype 12 corpus pages still escalate and the datagrid fallback is a **no-op on every one of
them**, and apple p2 is the natural same-document swap (`asserted=3, escalated=108, score=0.0270,
fallback_noop=True`). What is **not** measured is whether p2 exercises the guard the way p1 did —
p1 was chosen because appending a grid reading there would have *double-counted tokens on both
sides of the ratio* (`compile.py:1030-1039` names p1 and its 0.5941 by name). If p2's fallback is a
no-op for a different reason, the re-baselined test guards a different thing under the same name,
which is worse than deleting it. **Run the gate on p2 and read why it declines, before writing the
re-baseline task.**

### ASSERTED — separable, safe to do first or never

`R167` (the em-dash in `celltype.is_blank`) is a one-line change plus a corpus regression run. Not
on the critical path. Unchanged from the two predecessor handoffs.

---

## 1. Goal

Measure the three claims the predecessor handoff graded PROPOSED, so the plan is written against
measurement rather than reading. **All three came back CONFIRMED** — the first loop in this arc
where nothing was refuted at the claim level, though § A.2 refutes a line of the spec.

## 2. Where the primaries are

| where | what to establish there |
| --- | --- |
| `docs/superpowers/2026-09-04-r165-three-claims-measured.md` | this loop's whole output. § A the SPARQL derivation + the § 3.4 refutation + the domain fork; § B the apple-p1 token ledger and its three consequences; § C the wall-clock and the cache arithmetic; § D six controller-side seams; § E what is unverified |
| `docs/superpowers/2026-09-04-r165-preplan-spike.md` | the predecessor's measurement — the seam, M1's cost, the O5 patch point, the 14-test surface. **Still authoritative; nothing here refutes it** |
| `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md` | the contract. Authoritative except § 5 (O4, O5 — refuted by the predecessor), § 6 (`tab:ruleX`, and now `tab:bandIndex`) and § 3.4 (the numeric-literal contradiction, § A.2) |
| `scripts/doc_walltime.py` | the § C instrument, committed. Run it once per tree and diff; **read the call counts before the seconds** — its docstring records why |
| `docs/superpowers/residues-open.md` (`R160`, `R165`–`R169`) | R165 is the subject; **`R168` and `R169` were raised by this loop**; R160 is still not ruled |
| `src/iladub/etkl/compile.py:270-323` · `:817-840` | the seam and the disposal chain |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The SPARQL derivation reproduces the Python relation — 14 runs, 27 pages, 0 differing, both term shapes | evidence § A |
| Spec § 3.4's "no numeric literal" wins over `?b = ?a + 1`; the emitter emits the predecessor index as a fact | evidence § A.2 — **a recommendation, the plan disposes** |
| `test_datagrid.py:907` is fixture drift; the merge swallows nothing | evidence § B |
| Memoisation is not a blocker for R165, and is worth more than R165 costs | evidence § C, and `R168` |
| The plan's own three rows are now **`R170`/`R171`/`R172`**, not R168/R169/R170 as spec § 7 says — this loop took 168 and 169 | spec § 7 is superseded here; **recorded nowhere but this file and the register** |
| The register stands at `43/157 closed` and `len(query_files()) == 49` at `2f55995` | evidence § D.6 |
| The plan is written fresh, again | this file's preamble — **recorded nowhere but this file** |

## 4. Unverified or assumed

- **No pytest was run in this loop** beyond `tests/test_residue_register_integrity.py` (6 passed).
  The predecessor's 14-failures-in-5-files surface is inherited, not re-verified. **The full suite
  takes ~45 minutes and must not be run in a background subagent.**
- **`corpus/` is gitignored (`.gitignore:52`), so a fresh `git worktree` has NO corpus and every
  corpus test skips silently, reporting green.** Hit for real this loop. Any worktree-based
  execution of the plan needs a `corpus` symlink or it falsifies nothing.
- **Every § B and § C figure is the prototype's**, and the prototype's relation is plain Python.
  § A shows the SPARQL form derives the same runs; it does not show a shipped implementation
  behaves like the prototype.
- **No document score has ever been measured with the membrane on.** Everything ran
  `validate_shapes=False`; the membrane has never seen a merged band.
- **§ C is one run per tree**, and it names the noise it exposed (`who` came back 19% *faster*
  under a change that proposes no run on any of its pages).
- **§ D.3 / `R169` is read from the prototype's diff ordering, not run** — no corpus page can run it.
- **The vacuous-truth divergence (§ A.1) is proven reachable only synthetically.**
- Everything else this loop could not measure is under evidence § E, per-item.
