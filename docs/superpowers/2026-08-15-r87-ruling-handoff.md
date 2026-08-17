# Handoff — R87, the routing is ruled; the plan is not written

**Written:** 2026-08-15 by the session asked to rule on §3.2b and then write the plan.
**Branch:** `loop-escalation-is-a-decision`, HEAD `b5606d4`, tree clean.
**Supersedes:** `2026-08-15-r87-handoff.md` §3.2b's *"nobody has ruled on this"* and its §5 next action.
Everything else in that file stands and is still the primary.

## 1. Goal

Write `docs/superpowers/plans/2026-08-15-escalation-is-a-decision.md`. The decision that blocked it
is made (§3). No code written.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/2026-08-15-r87-handoff.md` | prior handoff. Still primary for §3.2a, §3.3, §3.4-3.8. Read §3 here first — it rules the open question and corrects three of its citations |
| `specs/2026-08-13-escalation-is-a-decision-design.md` | the design. **§4.3 bullet 1 is rejected below — do not implement it** |
| `CLAUDE.md:284-373` | the five plan rules |
| `CLAUDE.md:104-141` | the §8 AXIOM/NEURAL/PROCEDURAL gate — what decided §3.1 |
| `plans/2026-08-13-membrane-parity.md` | house style. **Its Task 4 residue convention does not transfer** — see §4 |
| `residues-open.md:73` | R87's row |

## 3. What was decided, and where

**Recorded nowhere but this file and the session transcript.** No commit, no residue row, no spec
edit carries them. Reversible on the evidence cited.

### 3.1 RULING on §3.2b — option (d) ACCEPTED, conditioned

**The shape needs three triples it cannot currently bind** (`escalation-shapes.ttl:22-30`):

```text
dec:EscalationShape  sh:targetClass dec:DecisionHolon
  $this  dec:constrainedBy ?sev     ← §4.1 derivation supplies
  $this  dec:withinScope   ?scope   ← §4.1 derivation supplies
  ?scope dec:maxSeverity   ?ceil    ← etkl:readerScope ......... DOES NOT EXIST YET (§4.2)
  ?sev   risk:order        ?so      ← risk.ttl:66  Breach = 2 ... NOT IN THE GRAPH
  ?ceil  risk:order        ?co      ← risk.ttl:64  Watch  = 1 ... NOT IN THE GRAPH
  FILTER (?so > ?co)                ← never fires; ?so/?co unbound
  FILTER NOT EXISTS { $this dec:escalatedTo ?apex }
```

**Why spec §4.3's first bullet cannot fix it.** Adding `risk.ttl` to `_FULL_ONT` puts it in
`ont_graph`, and `ont_graph` is read for exactly one thing:

```text
_validate(graph)                              compile.py:435
  membrane.validate(graph, _DEC_SHAPES, _FULL_ONT)
    _payload_nt(data_graph, ont_graph)        membrane.py:318
      subclass_closure(data_graph, ont_graph) membrane.py:448
        reads ont_graph for rdfs:subClassOf ONLY      :477
        copies data_graph through, never merges ont   :489-498
        └── grep -c "subClassOf" risk.ttl = 0  ──►  0 triples contributed
```

The payload is byte-identical with and without it. That is also why §3.3's 28 identical cells are a
measurement of nothing.

**The four options, on the axes that separate them:**

| option | §8 gate | seam cost (stem p0) | paid on | drift risk |
| --- | --- | --- | --- | --- |
| (a′) `risk.ttl`+`etkl.ttl` → data graph | — | **+68.6 ms/call (+35.6%)** | every seam call | none |
| (b) derivation emits literal ordinals | AXIOM | 0 | — | **restates what `risk.ttl` owns** |
| (c) carry step inside the seam | **PROCEDURAL** | +6.8 ms | every seam call | whitelist grows; needs a fixpoint |
| **(d) CONSTRUCT binds from `risk.ttl`** | **AXIOM** | **0** | **— seam untouched** | **none** |

"Every seam call" is the load-bearing column: it includes `tiling.region_tiles` on region *scratch*
graphs (the R19 hazard, `decisionlog.py:12-14`) and `feed._validate_grounding`. (b)/(d) touch
neither — `ground_document` populates a fresh graph and never copies from `source`
(`feed.py:630-643`), so the grounding payload stays byte-identical.

**(d)'s shape** — the precedent is `interpret.run(query_path, *graphs)`, a flat union:

```text
vocab/queries/escalation-furnish.rq          CONSTRUCT
  interpret.run(rq, page_graph, vocab_graph)   etkl/interpret.py:18
       │                        └── risk.ttl + etkl.ttl
       │
       WHERE   ?d dec:chosen ?o . ?o rdfs:label "escalated"   ← label, never a URI suffix
               risk:Breach       risk:order     ?so   ← BOUND FROM risk.ttl, not written as 2
               etkl:readerScope  dec:maxSeverity ?ceil
               ?ceil             risk:order     ?co
       │
       CONSTRUCT  ?d dec:constrainedBy risk:Breach
                  ?d dec:withinScope etkl:readerScope
                  ?d dec:escalatedTo ?req  +  ?req a dec:ExpansionRequest
                                              ?req dec:regarding ?r
                                              ?req dec:condition …
                  + the 3 vocabulary triples above    ← the licence, see condition 2
```

**Four conditions on acceptance:**

1. Ordinals **bound from `risk.ttl` as a query input, never literals**. This is the whole difference
   from (b), so it must be a testable property.
2. The `.rq` file carries an explicit note: *a derivation may carry vocabulary into data when a shape
   reads it, scoped to the derived subject* — and its boundary.
3. A test pins the carry is **bounded** — exactly the triples the shape reads, no more. "Merge
   `risk.ttl`" must fail it as surely as asserting nothing does.
4. **O3 re-run against the real change.** §3.3 does not transfer.

**The argument against (d), and why it is priced in rather than dismissed:** it puts vocabulary
triples into a document data graph — the category `subclass_closure`'s docstring exists to prevent
(`membrane.py:451-452`). But that docstring forbids a *standing structural merge* of 192 triples on
every document. (d) asserts 3, only where an escalation is present, 0 when nothing escalates. What
the objection does establish is that the precedent is over-applicable — hence conditions 2 and 3.

### 3.2 RULING on §3.6 — widen `dec:escalatedTo`'s range

```diff
 dec:escalatedTo a owl:ObjectProperty ;                        # dec.ttl:212-214
     rdfs:domain dec:DecisionHolon ;
-    rdfs:range dec:DecisionHolon ;
+    rdfs:range [ a owl:Class ; owl:unionOf ( dec:DecisionHolon dec:ExpansionRequest ) ] ;
```

The derivation asserts `?d dec:escalatedTo ?req` where `?req a dec:ExpansionRequest`, and
`dec:ExpansionRequest rdfs:subClassOf dec:Event` (`dec.ttl:197-198`) — not `dec:DecisionHolon`.
Nothing enforces the range today (`subclass_closure` does no range typing, `membrane.py:458-465`),
but that is luck. Precedent is one line away: `dec:regarding` was widened identically at
`dec.ttl:204-205`.

### 3.3 NOT decided

- **Where the derivation runs.** Constrained by §3.4/§3.5 below, not answered. Name it as a MEASURE
  seam (plan rule 3).
- **Whether the `dec:escalatedTo` widening ships this loop or as its own residue.** Ruled *what*,
  not *when*.

**The two call sites, both conditional:**

```text
compile.py:1083   _validate(graph)     gated :1079-1082
                    validate_shapes AND (tab:RecordTable OR tab:HierarchicalTable in graph)

document.py:1516  _validate(graph)     gated :1515
                    validate_shapes AND (recognized OR section_facts)
                    assignments at :1158 :1184 :1324 :1336 :1368 :1506
```

**The `datagrid_adopt` trap — furnishing placed at the recording site is discarded here:**

```text
compile_tables(pdf, page)
  graph = Graph()                        # :486    ← graph A
  recorder = ReadingRecorder(graph)      # :488    ← recorder captures A, holds it as self._g
  for band in bands:
    brec.record("verdict", …)            # :514-898   17 sites, all decisions ──► A
  if datagrid_adopt and asserted == 0:   # :993
    graph = Graph()                      # :1027   ← NAME REBINDS TO B. A is dropped.
    _emit(graph, …)                      # :1028      admission holon ──► B
  if validate_shapes and has_table:      # :1079
    _validate(graph)                     # :1083   ← validates B. The 17 decisions are gone.
  return CompilationReport(…, graph, …)  # :1087   ← also B
```

Same shape as R73's defect 2, which plan rule 2 exists to catch.

## 4. Measured this session — re-run these, do not cite this file

**Three citations in the prior handoff are wrong:**

```diff
- interpret.run(query, graph, vocab)  at  src/iladub/federate.py:56
+ run(query_path, *graphs)            at  src/iladub/etkl/interpret.py:18
+   flat `union += g` at :23; no named vocab param, no initBindings
+   called from src/iladub/etkl/federate.py:56
+   STRONGER precedent than described: federate.py:97-100 passes FIVE graphs
+   including a synthetic one-triple parameter graph; denormalization.py:96-97 chains
- document.py:1516
+ src/iladub/etkl/document.py:1516        (no src/iladub/document.py exists)
- vocab/ontology/etkl.ttl does not exist
+ etkl.ttl exists, 161 lines; it is etkl:readerScope that does not
```

**New, load-bearing for §4.2:**

```text
dec:maxSeverity          dec.ttl:216-218
  rdfs:domain dec:Scope
  rdfs:range  — NONE, deliberately ("dec stays standalone, the range is left open")
  ──► §4.2 must type  etkl:readerScope a dec:Scope
      or the ceiling triple's subject sits outside its own predicate's declared domain
```

**Confirmed unchanged at `b5606d4`:**

| fact | where |
| --- | --- |
| `risk.ttl` subClassOf/subPropertyOf count = **0** | `grep -c` |
| `risk:Watch` order 1, `risk:Breach` order 2 | `risk.ttl:64,66` |
| `_FULL_ONT` = tab + dec + iladub, three hardcoded `o.parse` calls | `compile.py:419,430,431` |
| `_GROUND_ONT_FILES` **is** a named constant | `feed.py:587` |
| 17 verdict sites, **all before** the `:1027` rebuild | `grep -c 'record("verdict"'` |
| `BandRecorder` writes `dec:regarding` always, `rdfs:label` on every option | `decisionlog.py:52,61` |
| stale comment §4.4 asks to fix | `decisionlog.py:92-93` |
| 2nd producer emits no `dec:regarding`, no holon label | `datagrid.py:695-697` |
| `tests/etkl/test_membrane.py` exists, 28 tests, **no pyrudof skip** ⇒ §4.5 goes here | — |
| `test_membrane_equiv.py` skips the **whole file** without pyrudof | `:19-21` |
| `-m corpus` registered only in `pyproject.toml:93-95` | — |
| both escalation tests merge `risk.ttl` into the **data** graph, with a comment saying why | `test_escalation_shacl.py:20-21,24`; `test_escalate.py:65` |
| `escalation-shapes` referenced 3×, all in `tests/` | R87's row holds |

**Residue bookkeeping — the house-style plan's convention does NOT transfer:**

```text
residues-open.md     69 rows matching ^| R      0 rows matching ^| ~~R
residues-closed.md   ← closed rows live HERE, they are not struck in place
residues.md:32       "86 rows, 17 closed" as of 2026-08-13
residues.md:17-18    a row raised today is stamped (17/87 closed)
```

## 5. Unverified or assumed

- **The plan does not exist.** Nothing below the ruling is written.
- **The ruling rests on the PRIOR session's behavioural measurements, not this one's.** The option
  table's cost figures, the exhaustive target enumeration (21 `sh:targetClass`, 4
  `sh:targetSubjectsOf`, 0 focus nodes from any added triple), and (d)'s idempotence and
  evidence-positivity checks all come from `2026-08-15-r87-handoff.md` §3.2b. Those scripts are gone.
  **This session re-verified structural claims only** (§4). To defend the ruling, reproduce (d)'s
  two-directional verdict on bfs p5 first.
- **O3 has not been re-run against (d).** Condition 4 exists for this.
- **Only bfs p5 was ever exercised.** apple (15 escalations), cbh-stem (4), who-wfa (3) were not.
- **The `datagrid_adopt` path has never been exercised** — and it constrains the one decision §3.3
  leaves open.
- **The rudof leg was never re-confirmed.** All §3.2b verdicts forced `engine="pyshacl"`;
  `engine_name()` reports `rudof` as this environment's default.
- **`etkl:readerScope` is simulated, not declared.** Spec §4.2 unwritten.
- **The vacuity registry (§4.5) has not been designed at all.** M7's 10 idle shapes carried forward
  untested.
- **No corpus battery or fast suite run on this branch.** O4's baselines are the spec's, at `06fe726`.
- **`CLAUDE.md:278-282` describes the wrong enforcement mechanism** — `scripts/context_budget.py` is
  orphaned; plimslop is what fires. Unrelated to R87, still true.

## 6. The next concrete action

Write the plan, fresh session, 50K originating floor, taking §3's rulings as given and re-running
§4's commands to carry them inline (plan rule 2).

**Budget the read before starting.** Three sessions have stopped here (87K, 119K, 112K):

```text
harness preamble    ~12K
spec                ~11K
CLAUDE.md ×2         ~5K
house-style plan    ~14K      ← the compressible one; copy the shape from this file instead
                    -----
                    ~42K before a word is written
```

This handoff removes the deliberation and the structural measurement from that budget. Do not
re-derive §3; do not re-run §4's subagents except to paste their commands into the plan.

**Delegating the plan to a subagent was proposed and rejected.** Recorded via `plimslop.mark`.
CLAUDE.md rule 1: a subagent handed a finished ruling is a transcriber, and *"an implementer reduced
to a transcriber cannot catch a plan defect."* Holds regardless of the subagent's model. If the floor
is crossed again, log the override and write it — do not launder the token count through an agent
that did not do the reasoning.
