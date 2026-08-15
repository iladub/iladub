# Handoff — R87, the routing is ruled; the plan is not written

**Written:** 2026-08-15, at 112,912 tokens, by the session asked to rule on §3.2b and then write the plan.
**Branch:** `loop-escalation-is-a-decision`, HEAD `b5606d4`, working tree clean.
**Supersedes:** `docs/superpowers/2026-08-15-r87-handoff.md` §3.2b's "nobody has ruled on this" and §5's
next action. Everything else in that file stands and is still the primary.

## 1. Goal

Write `docs/superpowers/plans/2026-08-15-escalation-is-a-decision.md`. The routing decision that
blocked it is made (§3 below). No code has been written.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/2026-08-15-r87-handoff.md` | The prior handoff. Still the primary for §3.2a (three triples, not one), §3.3 (O3 measured, and why it does not transfer), §3.4-3.8. Read it, but read §3 of THIS file first — it rules on the question that one left open, and corrects three of its citations. |
| `docs/superpowers/specs/2026-08-13-escalation-is-a-decision-design.md` (303 lines) | The design. §4 what ships, §5 oracles, §7 what is NOT done. **§4.3's first bullet is rejected by the ruling below** — do not implement it. |
| `CLAUDE.md` §"Plan authoring discipline" (lines 284-373) | The five rules the plan is reviewed against. |
| `CLAUDE.md` §8 (lines 104-141) | The AXIOM/NEURAL/PROCEDURAL gate. It is what decided §3.2b. |
| `docs/superpowers/plans/2026-08-13-membrane-parity.md` | House style. Copy its shape — but see §4's note: its Task 4 residue convention does **not** transfer. |
| `docs/superpowers/residues-open.md:73` | R87's row, verbatim and long. |

## 3. What was decided, and where each decision is recorded

**Both rulings below are recorded nowhere but this file and the session transcript.** No commit, no
residue row, no spec edit carries them. They are reversible on the evidence cited.

### 3.1 RULING on §3.2b — option (d) is ACCEPTED, with four conditions

The §4.1 `CONSTRUCT` carries the three ordinal/ceiling triples, binding them from the vocabulary
supplied as a query input rather than restating them as literals.

Decided on the **§8 gate**, which is what separates the options — blast radius does not (the prior
handoff's exhaustive target enumeration: every candidate triple yields 0 focus nodes):

- **(c) is PROCEDURAL and not earned.** Its whitelist of carried predicates is an untethered constant
  list that grows whenever a shape reads a new ontology predicate. §8 calls a tuned constant *prima
  facie evidence* the decision belongs elsewhere. It also needs a fixpoint, bought for nothing.
- **(b) restates a fact `risk.ttl` owns.** Hard-coding `risk:order 2` violates §7 (emit what the
  source supports), and the drift is silent — change an ordinal in `risk.ttl` and the derivation
  keeps asserting the old one, with no test to notice.
- **(a′) works but is paid everywhere.** +68.6 ms/call on stem p0 is 46% of the 148 ms the parity
  loop worked to remove, paid on *every* seam call — including `tiling.region_tiles` on region
  scratch graphs (the R19 hazard at `decisionlog.py:12-14`) and `feed._validate_grounding`. Spec §7
  says this loop changes nothing about what escalates; (a′) changes what every membrane call sees.
- **(d) is AXIOM, derivation form** — the same classification §4.1 already gives the furnishing. No
  new mechanism, no procedural code, no new seam. `_payload_nt` is untouched, so the grounding
  payload stays byte-identical.

**The argument against (d) is real and is priced in, not waved off.** Its own recommender's objection
— that it puts vocabulary-level triples into a *document* data graph, the category
`subclass_closure`'s docstring exists to prevent (`membrane.py:451-452`) — does not reach (d) at full
strength. That docstring prohibits a *standing structural merge* of the ontology into data: 192
triples on every document, unconditionally. (d) asserts three triples, only where an escalation is
present, zero when nothing escalates. That is evidence carried with the fact it supports, not
vocabulary decanted into data. What the objection *does* establish is that the precedent is
over-applicable, so acceptance carries four conditions the plan must hold:

1. **Ordinals are bound from `risk.ttl` as a query input, never written as literals.** This is the
   entire difference between (d) and (b), so it must be a *testable property*, not a style note.
2. **The query file carries an explicit note** stating the narrow licence — *a derivation may carry
   vocabulary into data when a shape reads it, scoped to the derived subject* — and its boundary.
3. **A test pins that the carry is bounded**: exactly the triples the shape reads, and no more.
   "Merge `risk.ttl`" must fail that test as surely as asserting nothing does.
4. **O3 must be re-run against the real change.** The prior handoff §3.3's 28 identical cells
   measured a byte-identical payload — the same fact that made §4.3 ineffective. It does not transfer.

**Consequence for spec §4.3:** its first bullet (`risk.ttl` joins `_FULL_ONT`) is **rejected**.
`escalation-shapes.ttl` joining `_DEC_SHAPE_FILES` (second bullet) and compile-leg-only (third
bullet) both stand.

### 3.2 RULING on §3.6 — widen `dec:escalatedTo`'s range

`dec:escalatedTo` declares `rdfs:range dec:DecisionHolon` (`dec.ttl:213`); the derivation asserts
`?d dec:escalatedTo ?req` with `?req a dec:ExpansionRequest`, and `dec:ExpansionRequest rdfs:subClassOf
dec:Event` (`dec.ttl:197-198`) — not `dec:DecisionHolon`. Widen it to
`owl:unionOf (dec:DecisionHolon dec:ExpansionRequest)`, following the shipped precedent one line away
in the same file: `dec:regarding` at `dec.ttl:204-205` was widened for this exact reason.

Reason: nothing enforces the range today (`subclass_closure` does no range typing, `membrane.py:458-465`),
but that is luck, not design. §7 says emit only what the source supports; asserting a triple outside
its own declared range is emitting something the vocabulary does not support.

### 3.3 NOT decided — deliberately, and constrained

- **Where the derivation runs.** §3.4/§3.5 of the prior handoff constrain it; they do not answer it.
  The measurement in §4 below is now complete enough to make this a short decision, but it is still
  a decision. State it as a MEASURE seam per plan rule 3.
- **Whether `dec:escalatedTo`'s widening ships in this loop or as a separate residue.** Ruled *what*,
  not *when*.

## 4. Measured evidence gathered this session

Two subagents re-measured at `b5606d4`. Commands are given so the plan can carry them inline per
rule 2 — **re-run them rather than citing this file**, which is a secondary source.

**Three citations in the prior handoff are wrong and are corrected here:**

- `interpret.run(query, graph, vocab)` at `src/iladub/federate.py:56` → the module is
  **`src/iladub/etkl/interpret.py:18`**, the signature is **`run(query_path, *graphs)`** (variadic,
  flat `union += g` at `:23`, no named vocab parameter, no `initBindings`), and the call site is
  `src/iladub/etkl/federate.py:56`. The precedent is *stronger* than described:
  `federate.py:97-100` already passes **five** graphs including a synthetic one-triple parameter
  graph built inline. `denormalization.py:96-97` chains one CONSTRUCT's output into the next.
- `document.py:1516` → **`src/iladub/etkl/document.py:1516`**. There is no `src/iladub/document.py`.
- `vocab/ontology/etkl.ttl` **exists** (161 lines); it is `etkl:readerScope` that does not
  (`grep -n "readerScope" vocab/ontology/*.ttl` → no matches).

**New, and load-bearing for §4.2:** `dec:maxSeverity` (`dec.ttl:216-218`) declares
`rdfs:domain dec:Scope` and **deliberately no range** ("dec stays standalone, so the range is left
open"). So §4.2 must type `etkl:readerScope a dec:Scope`, or the ceiling triple's subject sits
outside `dec:maxSeverity`'s declared domain — the same defect §3.2 above rules against.

Confirmed unchanged at `b5606d4`:

- `grep -c "subClassOf\|subPropertyOf" vocab/ontology/risk.ttl` → **0**. (The 5 risk-side axioms live
  in `risk-hga-align.ttl`, loaded by no membrane.)
- `risk:Watch risk:order 1` (`risk.ttl:64`), `risk:Breach risk:order 2` (`risk.ttl:66`).
- `_FULL_ONT` = tab.ttl + dec.ttl + iladub.ttl, as three hardcoded `o.parse` calls
  (`compile.py:419,430,431`) — **not** a named constant like `_TAB_SHAPE_FILES`/`_DEC_SHAPE_FILES`
  (`compile.py:398-399`). `feed._GROUND_ONT_FILES` **is** a named constant (`feed.py:587`).
- `dec:EscalationShape`'s body needs exactly three triples — `?scope dec:maxSeverity ?ceil`,
  `?sev risk:order ?so`, `?ceil risk:order ?co` (`vocab/shapes/escalation-shapes.ttl:22-30`).
  Confirms prior handoff §3.2a.
- `grep -rn "record(\"verdict\"" src/iladub/etkl/compile.py | wc -l` → **17**, all between
  `compile.py:514` and `:898` — i.e. **all strictly before** the `graph = Graph()` rebuild at
  `compile.py:1027`, with the recorder bound at `compile.py:486-488`. Prior handoff §3.5 confirmed
  exactly: on the adopt path no band decision reaches `_validate` **or** the returned
  `CompilationReport.graph` (`compile.py:1087`).
- The two `_validate` gates: `compile.py:1079-1082` (`validate_shapes` AND a `tab:RecordTable` or
  `tab:HierarchicalTable` subject) and `document.py:1515` (`validate_shapes` AND
  `recognized or section_facts`; assignments at `document.py:1158,1184,1324,1336,1368,1506`).
- `BandRecorder.record` writes `dec:regarding` unconditionally (`decisionlog.py:52`) and
  `rdfs:label` on **every** option (`decisionlog.py:61`) — so §4.1's label-matching contract is
  sound. The stale comment §4.4 asks to fix is at `decisionlog.py:92-93`.
- The second producer: `emit_data_grid` (`datagrid.py:695-697`) emits no `dec:regarding`, no
  `rdfs:label` on the holon, and its `dec:chosen` object is a `tab:DataGrid`, not a `dec:Option`.
  It is the only live witness for §4.1 invariant 5.
- `tests/etkl/test_membrane.py` exists (28 tests, no `pyrudof` skip) — correct placement for §4.5's
  registry. `tests/etkl/test_membrane_equiv.py:19-21` is a module-level `pytestmark` skipping the
  **whole file** without `pyrudof`, exactly as the spec warns.
- `-m corpus` is registered only in `pyproject.toml:93-95`. No `pytest.ini`, no `setup.cfg`.
- Both existing escalation tests merge `risk.ttl` into the **data** graph, with an explicit comment
  saying why (`tests/test_escalation_shacl.py:20-21,24`; `tests/test_escalate.py:65`). Both use
  `iladub.validate.validate`, **not** the membrane.
- `grep -rn "escalation-shapes" src/ tests/ scripts/` → three hits, all in `tests/`. R87's row holds.

**Residue bookkeeping — the house-style plan's convention does NOT transfer.**
`residues-open.md` carries **69** `^| R` rows and **0** `^| ~~R` struck rows; closed rows live in a
separate `docs/superpowers/residues-closed.md`. `residues.md:32` states **86 rows, 17 closed** as of
2026-08-13, and `residues.md:17-18` gives the stamp convention — a row raised today would carry
`(17/87 closed)`. The membrane-parity plan's Task 4 "strike in place, do not delete" instruction
describes a convention this register does not use; check `residues-closed.md` before copying it.

## 5. Unverified or assumed

- **The plan does not exist.** Nothing below the ruling has been written.
- **The ruling rests on the prior session's measurements, not this session's.** The option table,
  the cost figures (20.5/192.9 ms baseline; (a) +63.6%/+35.6%; (c) +74.4%/+3.5%), the exhaustive
  target enumeration (21 `sh:targetClass`, 4 `sh:targetSubjectsOf`, 0/0), and the idempotence and
  evidence-positivity checks for (d) are all from `2026-08-15-r87-handoff.md` §3.2b. Their scripts
  did not survive. **This session re-verified the structural claims only** (§4 above), not the
  behavioural ones. If the ruling is to be defended, (d)'s two-directional verdict on bfs p5 is the
  one measurement to reproduce first.
- **O3 has not been re-run against (d).** Condition 4 exists because of this.
- **Only bfs p5 was ever exercised.** apple (15 escalations), cbh-stem (4), who-wfa (3) were not.
- **The `datagrid_adopt` path has never been exercised** — and §3.3 above leaves *where the
  derivation runs* open, which is exactly the decision that path constrains.
- **The rudof leg was never re-confirmed.** All §3.2b verdicts were forced to `engine="pyshacl"`;
  `engine_name()` reports `rudof` as this environment's default.
- **`etkl:readerScope` is still simulated, not declared.** Spec §4.2 has not been written.
- **The vacuity registry (§4.5) has not been designed at all.** M7's 10 idle shapes were not
  re-measured; that table is the spec's, carried forward untested.
- **No corpus battery or fast suite has been run on this branch.** O4's baselines are the spec's, at
  `06fe726`. Nothing establishes them at `b5606d4`.
- **`CLAUDE.md:278-282` still describes the wrong enforcement mechanism** (`scripts/context_budget.py`,
  which is orphaned; plimslop is what actually fires). Unrelated to R87, still true, still unfixed.

## 6. The next concrete action

Write `docs/superpowers/plans/2026-08-15-escalation-is-a-decision.md`, in a fresh session, at the 50K
originating floor, taking §3's two rulings as given and re-running §4's commands to carry them inline
per plan rule 2.

**Read this before planning the read.** Three sessions have now stopped at this point (87K, 119K,
112K). The cause is arithmetic, not carelessness: spec (11K) + CLAUDE.md's two sections (5K) +
house-style plan (14K) + harness preamble (12K) ≈ 42K before a word is written, and the earlier
sessions each spent 30-70K more on measurement and deliberation. **What this session removes from
that budget is the deliberation and the structural measurement** — the ruling is made, the citations
are corrected. Do not re-derive §3; do not re-run the subagents that produced §4 except to paste
their commands into the plan.

**Delegating the plan to a subagent was proposed this session and rejected.** Recorded via
`plimslop.mark`. The reason is CLAUDE.md rule 1: a subagent handed a finished ruling is a
transcriber, and *"an implementer reduced to a transcriber cannot catch a plan defect"* — which is
the failure the plan-authoring discipline exists to prevent. Same objection holds regardless of the
subagent's model. If the floor is crossed again, the honest move is to log the override and write it,
not to launder the token count through an agent that did not do the reasoning.
