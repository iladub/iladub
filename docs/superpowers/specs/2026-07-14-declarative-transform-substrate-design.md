# ET(K)L Declarative Transform Substrate (Neurosymbolic Loop One) — Design

**Date:** 2026-07-14
**Status:** ✅ **SHIPPED to main 2026-07-15** (merged `--no-ff`, pushed to `origin/main`). Implemented via
subagent-driven development (6 tasks, all task-reviews + final whole-branch review clean); plan at
`docs/superpowers/plans/2026-07-14-declarative-transform-substrate.md`; full suite 350 passed / 5 skipped.
(Original status: design approved, prototype-confirmed feasibility — retained below as the as-designed record.)
**Governed by:** CLAUDE.md §8 (neurosymbolic-first gate) + `docs/superpowers/specs/2026-07-14-recovery-layer-neurosymbolic-audit.md` (reframe #1, the single biggest missed-semantic opportunity).
**Supersedes (in execution, not behaviour):** `oracle.replay` and the Python bodies of `emit_base_facts`/`emit_base_projection`. A1/A2.1/B1.1 shipped on `main`; their tests are the behavioural spec this must keep green.

---

## 1. Goal

The reshape recipe (`tab:ReshapeRecipe` / `tab:UnpivotOp` / `tab:StripAggregationOp`) is declarative *as data*
but has **no declarative interpreter** — `oracle.replay` executes it in procedural Python, and the reverse
recovery is a *second* Python codepath kept in lockstep by hand (the neo-legacy the manifesto forbids), with
correctness riding on `_fmt`'s float-formatting matching the source. The A1 design **already specified** the
reshape as SPARQL `CONSTRUCT` + SPARQL 1.1 aggregates at the holon boundary; it was not built until loop one (this spec, shipped 2026-07-15).

Loop one builds it: **each recipe op-type gets one fixed SPARQL `CONSTRUCT` that reads its parameters from the
RDF recipe graph** and executes the transform. The recipe becomes an actually-executable declarative artifact
with a standard interpreter; the flat base becomes a `CONSTRUCT`-derived `hproj:Projection`; `oracle.replay`'s
Python twin-codepath is retired. Scope is **A only** (the interpreter); the role/type/boundary axiom-lifts (B)
and the redundant-tiling-backstop deletion (C) are the queued follow-on slices.

## 2. Gate compliance (CLAUDE.md §8)

- **AXIOM:** the transform is SPARQL `CONSTRUCT` + SPARQL 1.1 aggregates, consuming standards (SPARQL,
  FnO function IRIs, `hproj:Projection`). No transform logic in Python; no tuned constant anywhere in it.
- **PYTHON-OK (justified):** (1) invoking rdflib's SPARQL engine on the query files; (2) the exact-equality
  compare in the round-trip (`_close`, `_TOL=1e-6` — decidable arithmetic, irreducible); (3) `recover_recipe`'s
  procedural *search* that emits the declarative recipe (legitimately-procedural recovery — its **output** is an
  axiom). Each is irreducible to AXIOM/NEURAL and is stated as such in code + this spec.
- **NEURAL:** none in loop one (the span-perception family is loop two).

## 3. Architecture — the CONSTRUCT interpreter (prototype-confirmed)

**Proven 2026-07-14:** a fixed unpivot `CONSTRUCT`, reading `tab:opDimension`/`tab:opStub` from the recipe op in
RDF, produced the correct 8 base facts (Region×Year) over the real `tab:` grid model — zero Python transform
logic. The mechanism:

```sparql
# vocab/queries/unpivot-inverse.rq  (grid -> base). Params read from the recipe op node.
CONSTRUCT {
  ?bf a tab:BaseFact ; tab:measureValue ?v ; tab:atDimensionValue ?coDim , ?coStub .
  ?coDim  tab:dimensionName ?dimName ; tab:value ?colLabel .
  ?coStub tab:dimensionName ?stubName ; tab:value ?stubVal .
} WHERE {
  ?op a tab:UnpivotOp ; tab:opDimension ?dimName ; tab:opStub ?stubName .
  ?hp tab:coversColumn ?c ; tab:headerLevel 0 ; tab:hasLabel [ tab:cellText ?dimName ] .   # measure col
  ?hl tab:coversColumn ?c ; tab:headerLevel 1 ; tab:hasLabel [ tab:cellText ?colLabel ] .  # pivot value
  ?e a tab:EntryCell ; tab:atRow ?r ; tab:atColumn ?c ; tab:cellText ?v .
  ?hs tab:coversColumn ?sc ; tab:headerLevel 0 ; tab:hasLabel [ tab:cellText ?stubName ] . # stub col
  ?se tab:atRow ?r ; tab:atColumn ?sc ; tab:cellText ?stubVal .
  BIND(IRI(CONCAT(...)) AS ?bf) BIND(IRI(CONCAT(STR(?bf),"-dim")) AS ?coDim) BIND(IRI(CONCAT(STR(?bf),"-stub")) AS ?coStub)
}
```
(rdflib rejects inline `[ … ]` property-lists in a CONSTRUCT template — coordinate IRIs are `BIND`-constructed,
which also gives stable, dereferenceable coordinate IRIs.)

**Two directions, both SPARQL:**
- **Inverse (grid → base):** `unpivot-inverse.rq` (+ strip-inverse: base excludes aggregate rows/cols). Produces
  the flat base as a derived `hproj:Projection`.
- **Forward (base → grid):** `unpivot-forward.rq` re-pivots base measures into their grid cells;
  `strip-aggregation-forward.rq` re-adds each aggregate row/col via a sub-`SELECT (SUM(?v) AS ?t) … GROUP BY …`
  (SPARQL 1.1 aggregates, function named by its **F&O/FnO IRI**, e.g. `fn:sum`).

**Round-trip oracle** = run the forward CONSTRUCTs over the derived base → a reconstructed grid → **exact-compare**
to the original `grid_values`. Reproduction is the anti-overfit gate exactly as today; only the *executor* changes
from Python to SPARQL. `_fmt` is retired (SPARQL literals render canonically; the compare normalizes numeric
literals via the existing `_close`).

**Op-CONSTRUCTs live as `.rq` files** under `vocab/queries/` — version-controlled, testable in isolation, one per
op-type-and-direction — first-class declarative artifacts, not strings buried in Python.

## 4. Components

| Unit | Responsibility | Gate |
| --- | --- | --- |
| `vocab/queries/*.rq` (create) | the fixed per-op `CONSTRUCT`s (unpivot/strip × inverse/forward), reading recipe params from RDF | AXIOM |
| `src/iladub/etkl/interpret.py` (create) | thin executor: load a `.rq`, run it via rdflib over (source graph + recipe graph), return the constructed graph; ordered by `tab:opIndex` | PYTHON-OK (engine glue) |
| `src/iladub/etkl/oracle.py` (modify) | `replay` → runs the forward CONSTRUCTs (via `interpret`) instead of Python; `round_trip` keeps its signature + the `_close` exact compare | AXIOM exec + PYTHON-OK compare |
| `src/iladub/etkl/reshape.py` (modify) | `emit_base_projection` → runs the inverse CONSTRUCTs; the emitted base is typed `hproj:Projection`; `certify`/`certify_with_proposals` signatures unchanged | AXIOM |
| `vocab/ontology/tab-hga-align.ttl` (modify) | `tab:NormalizedBase rdfs:subClassOf hproj:Projection` already present — confirm the derived base carries it | alignment (HGA object-only) |
| `vocab/ontology/tab-fno-align.ttl` (modify) | ensure the strip functions map to their F&O IRIs (used by the aggregate CONSTRUCT) | alignment |

**Retired:** `oracle.replay` (Python), `emit_base_facts` (Python loop), `emit_base_projection`'s Python emission
loop. **Kept as PYTHON-OK:** `recover_recipe`/`recover_base` (recovery search → declarative recipe),
`verify_group`/`_close` (exact arithmetic).

## 5. Data flow

```
compiled tab: grid graph  +  recovered tab:ReshapeRecipe (recover_recipe — unchanged)
      │
      ▼  interpret.run(inverse CONSTRUCTs, ordered by opIndex)      [AXIOM]
   derived base  →  typed hproj:Projection (tab:NormalizedBase, prov:wasDerivedFrom t)   [not stored — a CONSTRUCT result]
      │
      ▼  round_trip: interpret.run(forward CONSTRUCTs) → reconstructed grid
   exact-compare(reconstructed, grid_values(g,t))   [PYTHON-OK _close]  →  ok / residue
      │
   ok → emit the projection ;  residue → escalate (unchanged disposition)
```

A1's deterministic path and A2.1's `certify_with_proposals` call the same `interpret`/`round_trip`; the only change
under them is that execution is SPARQL, not Python. B1.1 is untouched (headers, not transform).

## 6. Testing

- **Behavioural spec = the shipped suites, unchanged.** `tests/etkl/test_denormalization.py`, `test_oracle.py`,
  `test_reshape_*.py`, `test_certify_proposals.py`, `test_promote*.py`, `test_tab.py` must stay green — same
  assertions, now satisfied by the SPARQL interpreter. If any needs editing, that is a supersession defect to
  investigate, not a test to loosen.
- **New per-CONSTRUCT unit tests** (one per `.rq`, both directions): the inverse `unpivot.rq` over a constructed
  pivot graph yields the exact base (the prototype, promoted to a test); the forward pair reconstructs the grid;
  the strip aggregate re-adds the correct total; each `.rq` is exercised in isolation via `interpret`.
- **Round-trip oracle test:** a correct recipe round-trips; a corrupted base is rejected with residue (the
  existing anti-overfit assertions, now over SPARQL execution).
- **Gate test:** assert no tuned constant enters the transform (the `.rq` files + `interpret.py` contain no
  numeric tolerance; the only `_TOL` is in the equality compare, PYTHON-OK).

## 7. Source ownership / conventions

- `hproj:` (HGA) appears only as an object in `tab-hga-align.ttl` (already so). `fn:`/FnO IRIs only as objects in
  `tab-fno-align.ttl`. The `.rq` files reference `tab:` (owned) + standard fns; they are queries, not authored
  ontology, so they don't affect the standalone-core rule.
- The base is a **derived** `hproj:Projection` (a CONSTRUCT result), never a stored dataset — the correct holonic
  form, and it makes the transform upstream-portable to HGA's CONSTRUCT-at-boundary pattern.

## 8. Honest gaps & scope boundaries

- **In scope:** A — the CONSTRUCT interpreter for the *existing* op-types (UnpivotOp, StripAggregationOp), both
  directions, base as `hproj:Projection`, retiring `oracle.replay`. **Out of scope:** B (role/type/boundary
  axiom-lifts) and C (backstop deletion) — the queued next slices; the NEURAL span-perception family (loop two).
- **Feasibility validated for unpivot** (prototype). The strip-aggregate and forward directions are standard
  SPARQL 1.1 on the proven pattern — validated per-`.rq` in the plan's TDD.
- **The SPARQL-ceiling rule (settled):** we use **standard SPARQL `CONSTRUCT` only — we do NOT extend SPARQL**.
  Where an op genuinely reaches the expressiveness limit of standard `CONSTRUCT`/aggregates, **substituting
  Python for that specific piece is an acceptable, justified PYTHON-OK** (per §2 and CLAUDE.md §8 — "irreducible
  to AXIOM"): we prefer SPARQL and accept Python *at the ceiling*, rather than contorting or extending SPARQL to
  force it. Such a substitution ships with the standard why-irreducible note.
- **A2.1's transpose/group-flatten ops are not yet built** (they were A1's deferred inner loops); this substrate
  covers the op-types that exist. New op-types added later ship with their `.rq` pair from the start.
- **rdflib is the SPARQL engine** (already a dependency). No new runtime dependency.

## 9. Settled design decisions (for the implementation plan)

- **Base representation: NATIVE RDF (decision B, 2026-07-14).** `base` is the derived `hproj:Projection`
  RDF graph, not a Python `list[dict]`. The **inverse CONSTRUCT** produces it (retiring `recover_base`'s and
  `emit_base_projection`'s Python bodies); the **forward CONSTRUCT** reconstructs the grid; `round_trip`
  exact-compares. Consequence, stated honestly:
  - **Behavioural suites stay green unchanged** — `certify`/`analyze`/`emit_normalized_base`/
    `certify_with_proposals` keep their public behaviour and graph output (`NormalizedBase`, `tab:BaseFact`
    coords, `oracle_ok`, promotion). These are the real behavioural spec.
  - **A handful of *mechanism* unit tests coupled to the retired Python representation are re-expressed** —
    `test_oracle.py`'s `replay(list[dict])` and `test_reshape_recover.py`'s `recover_base(list[dict])` test the
    *old implementation*, not the behaviour; they become tests of the SPARQL mechanism (per-`.rq` + native-RDF
    base). This is supersession, not loosening.
  - **A2.1's base-building becomes CONSTRUCT-based:** `_named_pivot_recipe_and_base` (which builds a
    `list[dict]` for the nameless-pivot case) is reworked so the nameless case emits its base via an inverse
    CONSTRUCT (value-set measure detection expressed in the query) — keeping `certify_with_proposals`'s public
    behaviour and A2.1's promotion tests green.
- **The unpivot inverse CONSTRUCT is prototype-validated** (2026-07-14, over the real `tab:` grid model,
  reading params from the RDF recipe → correct 8-fact base). Promote the probe to the first task's test.
- **SPARQL-ceiling rule (§8):** standard SPARQL only; Python at the genuine expressiveness ceiling is justified
  PYTHON-OK with a why-irreducible note.

**Resume pointer (updated 2026-07-15):** ✅ Loop one is **shipped to main**. Live: the `CONSTRUCT` interpreter
(`interpret.run` + `vocab/queries/{unpivot-inverse,unpivot-inverse-valueset,unpivot-forward,strip-aggregation-forward-sum}.rq`),
the native-RDF `hproj:Projection` base (decision B), the SPARQL round-trip oracle, and the gate test. Retired: the three
Python twins (`oracle.replay`/`_fmt`/`_FUNCS`, `reshape.recover_base`, `denormalization.emit_base_facts`'s loop — the last
re-backed onto `reshape.derive_base`). **Next slices (queued, both AXIOM, both extend this substrate):** **B** —
role/type/boundary axiom-lifts (transpose, header/body split, dim-name-vs-values, stub-vs-measure → SHACL/SPARQL); **C** —
delete the redundant Python tiling backstops. Then **loop two** — the NEURAL span-perception grammar. **Deferred within loop
one (all fail-safe, documented):** multi-strip `?op2` correlation in `strip-aggregation-forward-sum.rq` (single-strip-only,
doc-fenced), gate `_strip_comments` hardening, and value-set inverse aggregate-row exclusion (A2.1 nameless scope).
