# R87 — handoff into Task 3

**Date:** 2026-08-15
**Branch:** `loop-escalation-is-a-decision`, HEAD `d2c9b74`, tree clean

## Goal

Finish the R87 plan: Tasks 3–6 remain (wire the derivation, wire the shape, build the
vacuity registry, close the record).

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/plans/2026-08-15-escalation-is-a-decision.md` | The plan. Tasks 3–6 are unstarted and unamended — read them as written. G1–G7 and the §7 test prohibitions (G4) still bind. |
| `a5166fe` (Task 1 commit message) | What shipped in the vocabulary, the S2 measurement that selected it, and the T1 falsification table. |
| `d2c9b74` (Task 2 commit message) | The derivation's measurements, the supersession finding, and the T2 falsification table — including the one test that did not falsify on its first draft. |
| `vocab/queries/escalation-furnish.rq` | The derivation itself. Its header carries the LICENCE note (G3 condition 2), the supersession guard's justification, and the site constraint below. |
| `tests/etkl/test_escalation_furnish.py` | T2.1–T2.9. The two `-m corpus` tests are the census; they take ~70s together. |
| `vocab/queries/effective-chain.rq` | The precedent that licenses a holon-scoped `FILTER NOT EXISTS` in a query that must otherwise stay evidence-positive. Its header states the rule; do not re-derive it. |

## What was decided, and where each decision is recorded

1. **S2 — the `dec:escalatedTo` range widening ships in Task 1, not as its own residue.**
   Selected by the plan's own measurement branch (no wired shape reads the range).
   Recorded in `a5166fe` and in `dec.ttl:212-215`. Task 6 therefore raises **no** residue
   for S2.

2. **`dec:condition` binds directly from `dec:rationale`; no reduction.** Measured: every
   `dec:DecisionHolon` on who-wfa (81) and cbh-stem (65) carries exactly one
   `dec:rationale`. Recorded in `d2c9b74`. **Measured on two documents, not seven.**

3. **The derivation excludes superseded decisions.** This is a change to the plan's Task 2
   contract, made from measurement, not from reading. Recorded in `d2c9b74`, in the `.rq`
   header's SUPERSESSION GUARD section, and pinned by
   `test_a_superseded_escalation_is_not_furnished` plus the cbh-stem corpus test.

4. **T2.8's document changed from cbh-stem to who-wfa**, because all four of cbh-stem's
   escalating decisions are withdrawn and it therefore pins zero. Recorded in `d2c9b74`.
   Spec §5 M5's counts (apple 15, bfs 10, cbh-stem 4, who-wfa 3) are counts of decisions
   that CHOSE "escalated" — **not** of live escalations. apple and bfs are unmeasured for
   supersession.

5. **T1.1–T1.3 live in `tests/test_escalation_vocab.py`.** The plan's File Structure table
   assigns Task 1 no test file; this one already owns the `dec:escalatedTo` and
   `dec:maxSeverity` assertions and runs in the fast suite. Recorded nowhere but here and
   in `a5166fe`.

### S1 — the seam, ANSWERED BY MEASUREMENT

**Site (iii): `document.py`, before `:1515`.** It is the only candidate of the three.

The measurement and the commands that produced every number are in
`docs/superpowers/2026-08-15-r87-task3-measurement.md` (produced by a delegated agent —
**read it, do not take the summary below as the evidence**). The load-bearing claim was
re-verified independently at HEAD:

```
$ grep -rn "DEC.supersedes" src/ --include='*.py'
src/iladub/reopen.py:39            (not in the compile path)
src/iladub/etkl/document.py:1299   section repair
src/iladub/etkl/document.py:1503   datagrid-adoption admission
```

Both compile-path writers write into the **document** graph (created `document.py:1157`)
and into no page graph — 0 `dec:supersedes` edges were observed in any of 13 page graphs.
So sites (i) and (ii) do not merely run *early*: the edges never enter the object those
sites hold, at any time. The supersession guard is permanently vacuous there. Site (iii)
runs after both (`1299 < 1503 < 1515`).

The cost of getting this wrong, measured: page-scope furnishing produces **4 spurious
expansion requests on cbh-stem and 5 on apple** — matters a later reading had already
resolved.

**The plan's citation is wrong.** Section repair links at `:1299`, not `~L1258-1284`, and
`:1503` is a **second writer the plan and the earlier draft of this handoff both miss** —
it is the writer of all five of apple's edges.

This supersedes the plan's C1/C2/C3 framing as the deciding constraint. C1 (`compile.py`'s
gate) and C3 (the `datagrid_adopt` rebind) still describe the page-scope sites accurately;
they are simply no longer live options.

### On the adopting path (C3)

Measured A=0 escalated decisions in the rebuilt graph, C1's gate **closed** on it (0
`tab:RecordTable` + 0 `tab:HierarchicalTable` — the grid is a `tab:DataGrid`), and the
surviving DATAGRID_RESIDUE escalation mints no decision holon at all (R69), so it is
unfurnishable in principle rather than merely unfurnished. **But "furnishes nothing" is
not "needs no furnishing":** apple's five discarded decisions still stand in the document
graph, arriving via `document.py:1212`. Site (iii) sees them; that is where they are
handled, and it is why the answer to Task 3's second question matters — `document.py:1516`
sees **neither** the recorder's page graph nor the rebuilt one, but a third object merged
by value from both.

## Unverified or assumed

- **Supersession is now measured on four documents.** who-wfa 3 escalating / 0 superseded;
  cbh-stem 4 / 4; apple 15 / 5 (10 live); graincorp-stem 0 / 0. **bfs, graincorp-capacity
  and ons remain unmeasured.**
- **who-wfa cannot distinguish the three sites** — it carries no `dec:supersedes` edge
  anywhere, at page or document scope. A Task 3 test written only against who-wfa would
  pass at every site including the vacuous ones. cbh-stem and apple are the discriminating
  documents; T3.5 in particular must use one of them.
- **A page's verdict is not a property of the page.** graincorp-stem p1 escalates compiled
  standalone but **asserts** under the document driver, so it never becomes an adoption
  candidate. Any Task 3 test that compiles a page standalone is measuring a different
  thing from the driver.
- **`holons with NO dec:regarding at all` was 0 on both documents measured.** The plan
  established that `datagrid.py:695-697` mints such a holon in the code; neither document
  exercised it. T2.7 constructs it synthetically. Invariant 5's coverage hole is therefore
  **real in code and unobserved in the corpus** — B−C was 0 on both.
- **The fast-suite figure 1155 passed / 7 skipped / 1 xfailed (18m25s)** was run with
  Task 1's edits in the tree and **not** re-run after Task 2. Task 2 added only a new test
  file and a new `.rq`, but that is an inference, not a measurement. Task 6's O4 still owes
  the branch's own before-state at `401e0d6`.
- **The rudof leg has not been run at all** in this session. Every figure above is the
  default engine.
- **T2.4 is falsified in one direction only.** The "merge `risk.ttl`" direction is refused
  by the assertion's shape (an exact 3-element set) but was not separately executed.
- **`?req` as a stable IRI has never been through a membrane.** Task 2 is offline. Whether
  `dec:EventShape` and `dec:ExpansionRequestShape` are satisfied in a validated graph is
  Task 3's T3.2/T3.3 and is untested.

## The next concrete action

Write Task 3's T3.1 test — an escalating document compiled with `validate_shapes=True`
carries at least one `dec:ExpansionRequest` and does not raise — watch it fail, then wire
`interpret.run` at site (iii) in `document.py` before `:1515`, with the vocabulary file set
as a module constant on the `_GROUND_ONT_FILES` precedent (`feed.py:586-587`), parsed once
at module level rather than per page.

Note the measurement did not settle one thing Task 3 still owes: whether **page-scope**
validation (`compile.py:1083`) needs its own furnishing. It sees no `dec:supersedes` edges,
so furnishing there is unguardable — but leaving it unfurnished means `dec:EscalationShape`
stays idle on the page leg, which is a residue for Task 6 rather than a defect, provided
Task 4 wires the shape into the leg that is furnished. **Decide this explicitly; do not let
it be decided by where the call happens to land.**
