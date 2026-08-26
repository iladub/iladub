# The arc's dependency landscape

<!-- GENERATED FILE — DO NOT EDIT BY HAND.
     Written by scripts/arc_depends.py, which RUNS vocab/queries/arc-depends.rq,
     arc-ready.rq and arc-reach.rq against tests/arc-manifest.ttl.
     Regenerate:  ./.venv/bin/python scripts/arc_depends.py
     Gated by:    tests/test_arc_landscape.py (regenerate-and-diff, byte identity).
     A hand edit here is reverted by the gate, not merged. -->

A **generated cache** (`CLAUDE.md` § Documentation governance, the second exception to
evidence-immutability): every figure below is the answer a SPARQL derivation gives over
the hand-authored manifest, and CI fails unless the tracked bytes are exactly what
`scripts/arc_depends.py` produces. Nothing here is recomputed in Python.

| | |
| --- | --- |
| source | `tests/arc-manifest.ttl` — hand-authored in reviewed commits; code never writes it |
| derivations | `vocab/queries/arc-depends.rq`, `arc-ready.rq`, `arc-reach.rq` (AXIOM, open world) |
| renderer | `scripts/arc_depends.py` (PROCEDURAL — markdown is not a derivation) |
| gate | `tests/test_arc_landscape.py` (regenerate-and-diff) |

**Absence of an edge is absence of a READING, never evidence of independence.** The graph was read off 43 criteria by a human and then graded by the membrane: 6 of its 27 edges are grounded by a two-sided ablation and 21 are propositions. This is a monitor, not a scheduler.

## §1 What can be started today — `arc-ready.rq`

Unmet criteria whose **direct** dependencies are all met. Direct and not transitive is a
CLAUDE.md §8 decision (spec §6): a criterion whose direct dependency is met but whose
grand-dependency is not still appears here, and transitive readiness follows by iterating.
A criterion for which no dependency has been read is ready by the same open-world reading:
there is no criterion this work is known to wait for.

**21 ready.**

| rung | criterion | statement |
| --- | --- | --- |
| `dec` | `dec:02` | vocab/shapes/dec-shapes.ttl:38 — dec:ConfidenceShape ships a worked example that conforms and a negative test that must fail; the negative half is missing (no fixture carries an out-of-range or duplicated dec:confidence). |
| `dec` | `dec:09` | vocab/shapes/iladub-shapes.ttl:53 — iladub:PromotionDecisionShape ships a worked example that conforms and a negative test that must fail; the negative half is missing (no test validates a promotion decision lacking iladub:reviews or dec:decidedBy against these shapes). |
| `dec` | `dec:12` | vocab/shapes/risk-shapes.ttl:35 — risk:RiskAssessmentShape ships a worked example that conforms and a negative test that must fail; the negative half is missing (no fixture carries an assessment without its subject, context or severity). |
| `dec` | `dec:13` | vocab/shapes/risk-shapes.ttl:49 — risk:SensitivityShape ships a worked example that conforms and a negative test that must fail; the negative half is missing (no fixture carries a sensitivity without its severity or its risk:reads conditions). |
| `dec` | `dec:15` | vocab/shapes/governance-shapes.ttl:45 — gsh:PermissionShape ships a worked example that conforms and a negative test that must fail; the negative half is missing (no fixture carries a permission without an odrl:action or an odrl:assignee). |
| `dec` | `dec:17` | The four provenance-reuse axioms declared in the Contract — dec:DecisionHolon ⊑ prov:Activity, dec:consideredEvidence ⊑ prov:used, dec:decidedBy ⊑ prov:wasAssociatedWith, dec:produced ⊑ prov:generated (vocab/ontology/dec.ttl:38,55,72,85) — are asserted by a test. They are declared and enforced by nothing. |
| `etkl` | `etkl:02` | ag-trade/graincorp-capacity-2026-08-04.pdf: this document compiles via compile_document to cor:CompilesAbove with a pinned cor:scoreFloor, under a cor:adjudication whose rationale accepts that score — not one that holds it. |
| `etkl` | `etkl:04` | gov-stats/ons-index-of-services-2026-02.pdf: this document compiles via compile_document to cor:CompilesAbove with a pinned cor:scoreFloor, under a cor:adjudication whose rationale accepts that score — not one that holds it. |
| `holon` | `holon:06` | A full raw→clean traversal example spanning RawDocumentHolon → portal → CleanDocumentHolon (the current example covers the grounding-governance crossing only). |
| `substrate` | `substrate:01` | The membrane is enforced at runtime by an immutable event ledger (memory): the holon's history is kept by the substrate itself, not reconstructed by the compiler process. |
| `substrate` | `substrate:02` | The membrane is enforced at runtime by validation-at-write (sensory): a non-conforming write is refused AT THE WRITE ENDPOINT, not inside the process that produced it. |
| `substrate` | `substrate:03` | The membrane is enforced at runtime by in-engine policy (motor): access policy is evaluated by the engine on every read and write, not held in a template this repo only parses. |
| `tab` | `tab:01` | MULTI_TABLE_AMBIGUOUS (compile.py:596): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:02` | REGION_TILING_FAILED (compile.py:656, :763, :939): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:03` | TRANSPOSED (compile.py:688): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:04` | ROW_GROUP_AMBIGUOUS (compile.py:739): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:05` | MATRIX_AMBIGUOUS (compile.py:830): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:07` | KIND_NOT_SUPPORTED (compile.py:978): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:08` | DATAGRID_RESIDUE (compile.py:1145): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:09` | ROUND_TRIP_FAIL (holon.py:493, region-level; the cell-level emitter at holon.py:55 shares the label and is corpus-dead): this escalation reason is disposed — either it fires on the 7-document corpus and every firing document carries a dated cor:adjudication naming and disposing of it, or it fires nowhere on the corpus and names a collectable prog:oracleTest that exercises the path, plus a recorded reason distinguishing corpus gap from dead path. |
| `tab` | `tab:10` | Every shape wired into the compile membrane is live, or registered idle with an adjudicated reason distinguishing corpus gap from dead shape; four VACUITY_REGISTRY rows still read 'corpus gap or dead shape, not adjudicated here'. |

## §2 What must land first — `arc-depends.rq`

The transitive closure per criterion, **grade-labelled**, with the grounded closure
(`prog:dependsOn+`) and the full one reported apart so a reader sees where the chain
stops being grounded. A dependency reachable both by an asserted chain and by one
containing a proposition is graded `asserted` — the grounded chain exists, and that is
the fact.

**16 of 43 criteria carry a closure**; for the other 27 no dependency has been read, which is not a claim that they have none.

| criterion | asserted — grounded by ablation | proposed — read, not grounded |
| --- | --- | --- |
| `dec:02` | — | `dec:01` |
| `dec:06` | `dec:01` | — |
| `dec:08` | — | `dec:01`, `dec:07` |
| `dec:10` | — | `dec:07` |
| `dec:12` | — | `dec:11` |
| `dec:13` | — | `dec:11` |
| `dec:15` | — | `dec:14` |
| `dec:16` | `holon:01` | `dec:07`, `dec:10`, `holon:03`, `holon:04` |
| `etkl:03` | — | `tab:01`, `tab:04` |
| `etkl:05` | — | `tab:02`, `tab:07`, `tab:09` |
| `etkl:06` | — | `tab:02`, `tab:05`, `tab:08` |
| `etkl:07` | — | `tab:05` |
| `holon:03` | `holon:01` | — |
| `holon:04` | `dec:07`, `dec:10`, `holon:01` | `holon:03` |
| `holon:06` | — | `holon:01` |
| `substrate:03` | — | `dec:14` |

## §3 How much of the arc each residue holds up — `arc-reach.rq`

For every residue the manifest names in `prog:blockedBy`: the count of **unmet** criteria
that reach the criterion it blocks, that criterion included. A met criterion mid-chain
still transmits gating; a met criterion is never counted as gated.

`?` means the derivation returns **no row** — the residue gates nothing
measurable — and is deliberately not `0`: unknown is not zero, and a rendered `0` would
be a measurement this evidence does not make. The order is by the measured count and is
not a recommendation; which residue to close is a judgment and stays the reader's.

| residue | unmet criteria gated |
| --- | --- |
| `R44` | 5 |
| `R62` | 5 |
| `R43` | 3 |
| `R45` | 3 |
| `R71` | 3 |
| `R74` | 3 |
| `R77` | 2 |
| `R79` | 2 |
| `R80` | 2 |
| `R83` | 2 |
| `R84` | 2 |
| `R97` | 1 |
| `R98` | 1 |
| `R99` | 1 |
| `R100` | 1 |

