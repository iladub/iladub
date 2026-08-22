# The arc's first edges — the reading, the grading, the refutation, and the acyclicity answer

Task 4 of the arc-has-edges plan (`docs/superpowers/plans/2026-08-22-the-arc-has-edges.md`,
argued from `docs/superpowers/specs/2026-08-22-the-arc-has-edges-design.md`). This is the loop's
substance: Tasks 1–3 built the instruments (`prog:dependsOn` / `prog:proposedDependsOn`, M12–M18
in `tests/arc-shapes.ttl`, M19 in `tests/test_arc_ablation.py`); this task uses them over the real
43-criterion manifest.

Tree: `the-arc-has-edges` @ `7e0470c`. Runner `./.venv/bin/python` (3.12.0, rdflib 7.6.0), never
`python3` (Global Constraint 1).

**The maintainer's question was *"do we have a clear landscape of dependencies for building the
full architecture?"* and the measured answer on 2026-08-22 was no — `tests/arc-manifest.ttl`
carried 43 criteria and zero dependency edges of any kind. It now carries 6 asserted and 22
proposed, and the criterion-scope graph is ACYCLIC (§4).**

---

## §1 The reading — written BEFORE the membrane was consulted

Method, and the order is the point (brief, Step 1): all 43 criteria were read, and every
dependency believed to exist was written down, *before* A1–A6 were checked against any of them.
An author who grades while reading only ever "finds" edges the membrane already permits, and the
proposition half of the graph then comes out empty for the wrong reason.

The 25 readings below are the raw output of that pass. Grading (§2) came after; three readings
were dropped at that stage for a stated reason, and one was authored, run and **refuted** (§5).

### Reading A — the doc-holon fabric is the vocabulary three other criteria are stated over

`vocab/ontology/etkl-holons.ttl` (holon:01) declares `etkl:DocumentHolon`,
`etkl:RawDocumentHolon`, `etkl:SemanticHolon`, `etkl:AlignmentHolon`, `etkl:CleanDocumentHolon`,
`etkl:GroundingPortal`, `etkl:MembraneHealth` and `etkl:membraneHealth` (lines 43–86). Four
readings follow:

| # | reading | what I read |
| --- | --- | --- |
| A1 | `holon:02 → holon:01` | `iladub-hga-align.ttl` subclasses five of those terms; the alignment axioms name terms that must exist |
| A2 | `holon:03 → holon:01` | `tests/test_hga_alignment.py:33` binds `ONTS = [iladub.ttl, etkl-holons.ttl]` and passes it as the knowledge graph of holon:03's two oracles |
| A3 | `holon:04 → holon:01` | same `ONTS`, same two oracles |
| A4 | `dec:16 → holon:01` | same `ONTS`; dec:16 asks CLAUDE.md:252's pairing question of the same shape+examples |
| A5 | `holon:05 → holon:01` | a membrane-health check reports `etkl:membraneHealth → Intact/Weakened/Compromised`, declared at `etkl-holons.ttl:75-86` and nowhere else (the manifest's own grep) |
| A6 | `holon:06 → holon:01` | a Raw→portal→Clean traversal can only be typed out of `etkl-holons.ttl:47,62,67` |

### Reading B — the HGA governed-grounding example is also an *iladub-core* example

`examples/holon-grounding-conformant.ttl:17` types `ex:cand-egfr a iladub:CandidateConcept`, and
`tests/test_hga_alignment.py:34` binds `SHAPES = [iladub-shapes.ttl, iladub-hga-shapes.ttl]` —
so the conformant example is validated against the **core** shapes as well as the HGA-facing one.

| # | reading |
| --- | --- |
| B1 | `holon:04 → dec:07` — `iladub:CandidateConceptShape` ranges over that example's candidate |
| B2 | `holon:04 → dec:10` — `iladub:NoLeakShape` also targets `iladub:CandidateConcept` |
| B3 | `holon:04 → holon:03` — the conformant/leak pair exists to exercise the shape |
| B4 | `dec:16 → holon:03` and `dec:16 → holon:04` — two rules about one artifact set (Ruling 12: the rungs partition declaring prose, not artifacts) |

`holon:04 → dec:08` was **read and rejected on the spot**: that example carries no
`iladub:GroundedNode`, so `iladub:GroundedNodeShape` has no focus node in it.

### Reading C — inside `dec`, where one vocabulary is layered on another

| # | reading | what I read |
| --- | --- | --- |
| C1 | `dec:06 → dec:01` | `examples/transplant/transplant-escalation.ttl:20,34` carry two `dec:DecisionHolon` subjects, and `tests/test_escalation_shacl.py:30-31` loads `dec-shapes.ttl` **into the shape graph** beside `escalation-shapes.ttl` (the leak test at `:37` loads `escalation-shapes.ttl` alone) |
| C2 | `dec:08 → dec:07` | `examples/promotion.ttl:12` — the promotion `iladub:reviews ex:cand-wirkstoffspiegel`, a subject that exists only in `examples/proposal.ttl:9` |
| C3 | `dec:10 → dec:07` | `iladub:NoLeakShape` targets `iladub:CandidateConcept`; the manifest's own non-vacuity count records its ONLY focus node anywhere is `examples/proposal.ttl:10` |
| C4 | `dec:08 → dec:01` | `examples/promotion.ttl:11` types the promotion as `iladub:PromotionDecision , dec:DecisionHolon`, and `tests/test_boundary.py:25-26` validates proposal+promotion against `dec-shapes.ttl` |
| C5 | `dec:02 → dec:01` | `dec:ConfidenceShape` **targets** `dec:DecisionHolon` (the manifest's own dec:02 note), so its positive half is dec:01's example |
| C6 | `dec:12 → dec:11`, C7 `dec:13 → dec:11`, C8 `dec:15 → dec:14` | the missing-negative-half criteria sit on the shape file and conformant example their met sibling declares (2, 3 and 7 focus nodes respectively, per the manifest's census) |

### Reading D — a corpus document cannot be *accepted* while a reason it fires is undisposed

The `etkl` criteria demand a `cor:adjudication` that ACCEPTS the score, *"not one that holds it"*.
The `tab` criteria demand each escalation reason be DISPOSED on every document it fires on, and
every adjudication naming one of these reasons today is a recorded **HOLD**. Per document, from
the graph-side census the manifest reproduces:

| document (criterion) | reasons it fires | readings |
| --- | --- | --- |
| apple (`etkl:06`) | REGION_TILING_FAILED ×8 (p0,p2), MATRIX_AMBIGUOUS ×2 (p0,p2), DATAGRID_RESIDUE ×1 (p1) | D1 `etkl:06 → tab:02`, D2 `→ tab:05`, D3 `→ tab:08` |
| bfs (`etkl:05`) | REGION_TILING_FAILED ×2 (p4,p5), KIND_NOT_SUPPORTED ×3 (p0,p6), ROUND_TRIP_FAIL ×5 (p5) | D4 `etkl:05 → tab:02`, D5 `→ tab:07`, D6 `→ tab:09` |
| who-wfa (`etkl:07`) | MATRIX_AMBIGUOUS ×3 | D7 `etkl:07 → tab:05` |
| cbh (`etkl:03`) | **nothing** — but R74 and R77 measure cbh places where structure goes unread *without* a reason firing, and they are tab:01's and tab:04's own blocking rows | D8 `etkl:03 → tab:01`, D9 `→ tab:04` |

### Reading E — the one edge that leaves the vocabulary rungs

E1 `substrate:03 → dec:14`. substrate:03's oracle is named
`test_engine_enforces_ai_inherits_user`, and *"AI access must equal the interacting user's
access … enforced by `gsh:AiInheritsUserShape`"* is CLAUDE.md's own wording — the invariant an
engine would enforce is the one dec:14 pairs with an example and a negative test.

### Readings considered and NOT authored — and why

Recorded so a later author does not re-derive them and think they were missed.

1. **`dec:03/04/05 → dec:01` (Milestone / Event / ExpansionRequest on DecisionHolon).** Four
   shapes in ONE file (`dec-shapes.ttl`) are **siblings, not dependents**. `dec:MilestoneShape`
   and `dec:EventShape` target their own classes, not `dec:DecisionHolon`. Contrast C1, where
   `escalation-shapes.ttl` is a *separate* file whose conformant test explicitly loads
   `dec-shapes.ttl` as well. The distinction is the file boundary plus a measured second load,
   not taste.
2. **`etkl:04 (ons) → tab:02`.** R43 claims a `REGION_TILING_FAILED` on the ONS document; the
   manifest's own `tab` header measures ons at **zero** escalation records of any reason and
   calls the row stale. An edge resting on a row the file already flags as stale would be worse
   than no edge.
3. **`tab:08 → tab:02 / tab:07 / tab:09`** (the data grid supersedes what it absorbs). The D2
   block measures 5 escalations WITHDRAWN from apple p1 — REGION_TILING_FAILED ×3,
   KIND_NOT_SUPPORTED ×1, ROUND_TRIP_FAIL ×1 — and replaced by the one DATAGRID_RESIDUE. But the
   manifest counts **graph-side**, so those 5 are *not* in tab:02's 10, tab:07's 3 or tab:09's 5:
   the firing sets are disjoint. Disposing tab:02 on apple p0/p2 and bfs disposes nothing on
   apple p1. Mechanism-related is not criterion-related.
4. **`tab:10 → dec:10` / `tab:10 → dec:06`** (R99 is `iladub:NoLeakShape`, R100 is
   `dec:EscalationShape`). The manifest says in as many words that liveness and pairing are
   **different questions** — *"NO LIVENESS CRITERION IS AUTHORED HERE (decision D3) … a different
   question from CLAUDE.md:252's, which asks only whether the pairing exists."* The source
   explicitly denies the edge.
5. **`dec:14 → dec:11`** (governance on risk). `tests/test_governance.py:29` loads
   `governance-shapes.ttl` **alone**; there is no consumption. §0/C5 and Task 1 both used exactly
   this pair as the instrument's *negative control* (`dec:01 → dec:11`, `dec:14 → dec:11`).
6. **`dec:09 → dec:07/08/10`.** dec:09's future oracle would consume `iladub-shapes.ttl`, which
   *three* criteria declare — there is no non-arbitrary choice of target at file granularity, so
   nothing is authored rather than one of three picked.
7. **`substrate:01 → dec:04`** (event ledger on `dec:EventShape`). The manifest's substrate header
   measures that the only "ledger" in `src/` is the adoption **token** ledger and explicitly says
   it is NOT an immutable event ledger. Different sense of the word.
8. **`substrate:02 → <any shape criterion>`.** "Validation-at-write refuses a non-conforming
   write" ranges over *every* shape; no single criterion is its target.
9. **Anything with `etkl:01` as an endpoint.** Measured (Task 1, Step 2, and re-confirmed by M19's
   own `_SKIPS_WITH_A_REASON` test): `corpus/` is gitignored, so `etkl:01`'s oracle
   `tests/test_corpus.py::test_expected_verdict[...]` **SKIPS inside every worktree M19 creates**.
   M19 scores a skip as *"did not execute"* — neither pass nor fail — so an edge at either end of
   `etkl:01` would come back "cannot judge" on whichever arm ran it. `etkl:01` is un-ablatable on
   this tree, and that is a fact about the corpus fixture, not about the arc.

---

## §2 The grading — by the membrane's rules, not by taste

M17 is the forcing function: a proposition whose ends satisfy A1–A4 **and** A6 is refused, so
"propose it and move on" is unavailable wherever grounding is possible.

**Asserted (7 authored).** A1–A4 + A6 all hold, so M17 leaves no choice:

| edge | A1 met/met | A3 tests disjoint | A4 `metOn(Y) ≤ metOn(X)` | A6 files disjoint |
| --- | --- | --- | --- | --- |
| A1 `holon:02 → holon:01` | ✓ | `test_alignment_axioms_present`, `test_alignment_modules_only_point_outward` vs `test_holons_module_standalone` | 06-23 ≤ 06-23 | `iladub-hga-align.ttl` vs `etkl-holons.ttl` |
| A2 `holon:03 → holon:01` | ✓ | the two hga tests vs `test_holons_module_standalone` | 06-23 ≤ 06-23 | `iladub-hga-shapes.ttl` vs `etkl-holons.ttl` |
| A3 `holon:04 → holon:01` | ✓ | ditto | 06-23 ≤ 06-23 | the two example files vs `etkl-holons.ttl` |
| A4 `dec:16 → holon:01` | ✓ | ditto | 06-23 ≤ 06-23 | three files vs `etkl-holons.ttl` |
| B1 `holon:04 → dec:07` | ✓ | hga 2 vs `test_boundary` 2 | 05-31 ≤ 06-23 | disjoint |
| B2 `holon:04 → dec:10` | ✓ | hga 2 vs `test_promotion_grounds`/`test_leak_rejected` | 05-31 ≤ 06-23 | disjoint |
| C1 `dec:06 → dec:01` | ✓ | `test_escalation_shacl` 2 vs `test_vocab_shapes` 2 | 06-02 ≤ 06-30 | `escalation-shapes.ttl`+2 vs `dec-shapes.ttl`+2 |

**Proposed (22).** Each carries exactly one `prog:dependencyRationale` on an `rdf:Statement`
reification node (plan §0/C3), naming *what I read* and *which precondition it fails*:

| refused by | edges |
| --- | --- |
| **A3** (shared oracle test) | B3 `holon:04 → holon:03` |
| **A3 + A6** | B4 `dec:16 → holon:03`, `dec:16 → holon:04`; C3 `dec:10 → dec:07` |
| **A6** (shared artifact file) | C2 `dec:08 → dec:07`, C4 `dec:08 → dec:01` |
| **A1 + A2** (an unmet end, with no artifact to ablate) | A5, A6, C5, C6, C7, C8, D1–D9, E1 — 16 edges |

Three of those (C6 `dec:12 → dec:11`, C7 `dec:13 → dec:11`, C8 `dec:15 → dec:14`) carry an extra
caveat in their own rationale, stated rather than glossed: the predicate means *"X cannot be met
while Y is unmet **and** X's oracle consumes Y's artifact"*, and for these three only the second
half is read — Y being unmet would not by itself block X. That is a second, independent reason
they are propositions.

---

## §3 The parse trap, hit and fixed in the same commit

MEASURED twice before this task (Task 2 and its reviewer) and confirmed here: `arc-manifest.ttl`
bound only `rdfs:`, `xsd:` and `prog:`. The **first** `[] a rdf:Statement` block raises
`BadSyntax: Prefix "rdf:" not bound` — a parse error, not a refusal, so it takes the whole
membrane down rather than producing a message. `@prefix rdf:` was added in the same commit, with a
comment saying why it is there.

---

## §4 The acyclicity answer — MEASURED, and it cuts both ways

> **At criterion scope the graph is ACYCLIC. At rung scope the same edges have a 2-cycle.**

```
$ ./.venv/bin/python  # depth-first cycle search over (prog:dependsOn | prog:proposedDependsOn)
CRITERION-SCOPE CYCLES: NONE — the graph is ACYCLIC
rung-level edges: {'dec': ['holon'], 'etkl': ['tab'], 'holon': ['dec'], 'substrate': ['dec']}
RUNG-SCOPE CYCLES: [['dec', 'holon', 'dec']]
```

M14 is green over the live manifest — `validate_manifest(MANIFEST)` returns `True`
(`./.venv/bin/python -m pytest tests/test_arc_manifest.py -q` → **27 passed in 12.91s**) — so no
cycle had to be resolved and nothing was split or deleted on acyclicity grounds.

**The rung-scope cycle is the loop's thesis, measured rather than assumed.** Spec §1 argued that
decision 8 (*rungs are unordered*) is *"right at the wrong granularity"*: at rung scope an
ordering is false because `etkl` needs holons to compile into and the holarchy needs holons only
`etkl` can produce. The authored edges reproduce exactly that shape one rung over:
`dec:16 → holon:01` (a `dec` criterion needs a `holon` one) and `holon:04 → dec:07`/`dec:10` (a
`holon` criterion needs two `dec` ones) are **both true**, and both are ASSERTED — grounded by
ablation, not by reading. Projected onto rungs they contradict each other; at criterion scope they
do not touch. Decision 8 is confirmed by this loop, not weakened by it, and `arc-manifest.ttl`'s
header now says so.

---

## §5 What A5 refuted — one edge, deleted, not demoted

Spec §9.2: *"a loop where A5 refutes nothing should be suspected of having authored only safe
edges."* Seven edges were authored and asserted; M19 refuted one.

```
$ ./.venv/bin/python -c "<parse tests/arc-manifest.ttl; ablation_refusals(g)>"
M19 live leg over 7 asserted edges: 6.69s
refusals: 1
 * M19: arm 1 refutes prog:criterion:holon:02 prog:dependsOn prog:criterion:holon:01 — with
   holon:01's artifacts ['vocab/ontology/etkl-holons.ttl'] removed, every one of holon:02's
   oracle tests still passes ({'tests/test_hga_alignment.py::test_alignment_axioms_present':
   'passed', 'tests/test_source_ownership.py::test_alignment_modules_only_point_outward':
   'passed'}), so holon:02 does not consume holon:01
```

**REFUTED: `holon:02 → holon:01`, arm 1, DELETED** (plan §0/C4 — M17 would refuse demoting it,
since the pair still satisfies A1–A4+A6, so deletion is the only membrane-legal outcome; the
refutation lives here and in a comment in the manifest, never in the graph).

**What the refutation actually found is a hole in holon:02's oracle, not an error in the reading.**
`vocab/ontology/iladub-hga-align.ttl` really does subclass five terms declared only in
`etkl-holons.ttl`. But `test_alignment_axioms_present` parses `iladub-hga-align.ttl` alone
(`tests/test_hga_alignment.py:39`) and `test_alignment_modules_only_point_outward` is a
source-ownership text check — **nothing in the tree checks that the terms the alignment module
aligns are declared anywhere**. A dangling `etkl:Foo rdfs:subClassOf holon:DataHolon` would keep
both green. That is a residue-worthy gap and it is flagged in the task report for the loop's
closing task rather than numbered here, to avoid colliding with a sibling task's `R113`.

*(No edge was refuted by arm 2, and no edge came back "cannot judge" — the etkl:01 skip hazard was
avoided at authoring time, §1's rejected reading 9.)*

**Cost:** 6.69 s over 7 asserted edges / 9 endpoint criteria. Task 3 projected a ~15 s floor,
30–40 s likely, 124.91 s hard ceiling — the live leg came in **~8.3 s BELOW the projected floor**,
because the bound is endpoint criteria × modules-per-criterion (9 × 1–2 subprocesses here) rather
than Task 1's full sweep (17 × 13 = 221 spawns). Real tree `git status --porcelain` clean and
`git worktree list` showing only the main worktree, before and after.

---

## §6 The blast-radius disclosure — ALL SIX asserted edges are inside Task 1's 18-pair set

Task 1 measured 44 ordered cross-criterion blast-radius pairs `(X removed → Y's own oracle fails)`
in the met set, of which **26 already share a declared artifact file** (A6 refuses those on file
grounds) and **18 do not** — because some oracle tests load a wider shape/knowledge graph than
their criterion declares. For such a pair, arm 1 can be satisfied for a reason that has nothing to
do with the edge. M17 forbids demoting a groundable edge on those grounds, so per the controller's
ruling the imprecision goes on the record instead of being hidden.

**Every one of the 6 surviving asserted edges is in that 18-pair set, and it is in it by
construction:** "arm 1 fires on a pair with no shared artifact file" *is* the definition of the
18. The disclosure is therefore total across the asserted subgraph, and what separates a genuine
edge from a spurious one here is the **reading**, not the ablation — which is why §1 records, per
edge, the exact `file:line` where the oracle loads the wider graph.

| asserted edge | Task 1 cause | the wider load, measured |
| --- | --- | --- |
| `dec:06 → dec:01` | cause 1 | `tests/test_escalation_shacl.py:30-31` loads `dec-shapes.ttl` **and** `escalation-shapes.ttl` for the conformant test; the leak test at `:37` loads `escalation-shapes.ttl` alone |
| `holon:03 → holon:01` | cause 2 | `tests/test_hga_alignment.py:33` — `ONTS = [iladub.ttl, etkl-holons.ttl]` |
| `holon:04 → holon:01` | cause 2 | same |
| `dec:16 → holon:01` | cause 2 | same |
| `holon:04 → dec:07` | cause 2 | `tests/test_hga_alignment.py:34` — `SHAPES = [iladub-shapes.ttl, iladub-hga-shapes.ttl]` |
| `holon:04 → dec:10` | cause 2 | same |

In every one of the six, the wider load **is** the reading rather than an accident of it: the
escalation example is validated against the decision shape because an escalation *is* a decision
(`transplant-escalation.ttl:20,34`), and the HGA example is validated against the core shapes
because it carries an `iladub:CandidateConcept` (`holon-grounding-conformant.ttl:17`). That is an
argument, not a proof, and spec §4 already concedes what the proof is worth: an asserted edge is
grounded to **file** granularity. `holon:04 → dec:07` and `holon:04 → dec:10` are the sharpest
case — both ground to the *same* file, `vocab/shapes/iladub-shapes.ttl`, so the ablation cannot
tell them apart and only the two shapes' target classes do.

---

## §7 FALSIFICATION — the direction of an asserted edge is grounded by something

The graph is data, not code, so the thing to falsify is the **authoring**: an edge whose reversal
is also admitted is an edge whose direction nothing grounded.

`holon:03 → holon:01` — plan §0/C5's existence proof, and the intra-rung edge Q3 said a date rule
could never orient — was reversed in a scratch copy (`arc-manifest-REVERSED.ttl`, one line
changed, line 1279) and both legs were re-run:

```
$ sed 's|^prog:criterion:holon:03 prog:dependsOn prog:criterion:holon:01 \.$|prog:criterion:holon:01 prog:dependsOn prog:criterion:holon:03 .|' \
      tests/arc-manifest.ttl > $SP/arc-manifest-REVERSED.ttl
1279c1279
< prog:criterion:holon:03 prog:dependsOn prog:criterion:holon:01 .
> prog:criterion:holon:01 prog:dependsOn prog:criterion:holon:03 .

MEMBRANE ADMITS THE REVERSAL: True
 * M19: arm 2 refutes holon:01 prog:dependsOn holon:03 — with holon:01's artifacts
   ['vocab/ontology/etkl-holons.ttl'] removed, holon:03's oracle tests
   ['…::test_governed_grounding_conformant', '…::test_ungoverned_grounding_rejected'] fail too,
   so the coupling is symmetric and this is not a dependency
 * M19: arm 1 refutes holon:01 prog:dependsOn holon:03 — with holon:03's artifacts
   ['vocab/shapes/iladub-hga-shapes.ttl'] removed, every one of holon:01's oracle tests still
   passes ({'…::test_holons_module_standalone': 'passed'}), so holon:01 does not consume holon:03
```

**The membrane admits the reversal** — A1–A4 and A6 are all symmetric here (same `metOn`, disjoint
tests, disjoint files), so M16 has nothing to say and M14/M15 see no cycle. **Only M19 catches
it**, and it catches it on *both* arms: arm 1 says holon:01 does not consume holon:03, arm 2 says
the coupling would be symmetric if it did. Restored: the tracked file is byte-identical to the
authored one (`diff -q` → IDENTICAL) and the reversal lives only in the scratchpad.

That is the property spec §2's Q2 said ablation alone cannot supply for a *shared-test* pair, and
supplies exactly where A3 holds.

---

## §8 The cockpit is unchanged, and that is the point

No `prog:met` was touched (spec §8; `arc-manifest.ttl:16-18` — code never writes this file, and
neither did this task's hand). The strip is byte-identical before and after, measured by stashing
the manifest and re-running:

```
=== AFTER (working tree):
arc  etkl ▰▱▱▱ 1/7  dec ▰▰▰▱ 11/17  holon ▰▰▰▱ 4/6  tab ▱▱▱▱ 1/10  substrate ▱▱▱▱ 0/3  frontier 15  ready 17
=== BEFORE (HEAD 7e0470c manifest):
arc  etkl ▰▱▱▱ 1/7  dec ▰▰▰▱ 11/17  holon ▰▰▰▱ 4/6  tab ▱▱▱▱ 1/10  substrate ▱▱▱▱ 0/3  frontier 15  ready 17
```

`scripts/cockpit.py`'s regex reader is unaffected by construction: `_CRITERION`
(`cockpit.py:188`) matches `^prog:criterion:<rung>:<slug>\s+a\s+prog:Criterion`, and every new
line in the dependency section is either `prog:criterion:… prog:dependsOn …` (no `a
prog:Criterion`), a `[] a rdf:Statement` block, or a comment — none of which can open a criterion
block, and none of which carries a `prog:met` line to be counted.

---

## §9 What a later reader should not re-derive

1. **`holon:02 → holon:01` is refuted, and the reason is holon:02's oracle, not the reading.**
   Do not re-author it until something checks that the terms `iladub-hga-align.ttl` aligns are
   declared. §5.
2. **`etkl:01` cannot be an endpoint of an asserted edge on this tree** — its oracle SKIPS in
   every worktree because `corpus/` is gitignored, and M19 scores a skip as *did not execute*.
   §1, rejected reading 9.
3. **Nine readings were considered and rejected with a stated reason.** §1's last table. Five of
   them (`dec:03/04/05 → dec:01`, the ons edge, `tab:08`'s three, `tab:10 → dec:10/dec:06`,
   `dec:14 → dec:11`) look plausible on a first read of the manifest and are refused by something
   the manifest itself already measured.
4. **6 asserted of 130 pairs in Task 1's assertable envelope is not a coverage figure.** The
   envelope counts pairs the membrane would *permit*; the reading is what proposes. CLAUDE.md §7
   — credibility over completeness — is why the other 124 are absent.
