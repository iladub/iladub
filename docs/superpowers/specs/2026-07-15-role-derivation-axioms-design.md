# Role-Derivation Axioms over the `tab:` Graph (Neurosymbolic Loop B) — Design

**Date:** 2026-07-15
**Status:** ✅ **SHIPPED to main 2026-07-15** (merged `--no-ff`, pushed to `origin/main`). Implemented via subagent-driven development (5 tasks + 2 review fixes; the final whole-branch review caught a cross-table dim-leak, fixed before merge); plan at `docs/superpowers/plans/2026-07-15-role-derivation-axioms.md`; full project suite 357 passed / 5 skipped. The UNPIVOT rule is realized as the two-pass `name-levels.rq` → `recover-dimensions.rq` (a probe-validated refinement of §3's single query). (Original status: design approved — retained below as the as-designed record.)
**Governed by:** CLAUDE.md §8 (the neurosymbolic-first gate — now with the **open/closed derivation-vs-constraint split**) + `docs/superpowers/specs/2026-07-14-recovery-layer-neurosymbolic-audit.md` (reframe #4: pivot/aggregation ROLE assignment → AXIOM).
**Builds on (shipped):** loop one — the declarative transform substrate (`interpret.run` + `vocab/queries/*.rq`, native-RDF `hproj:Projection` base). This is the **first *derivation axiom*** under the refined gate; it retires the role-assignment part of `recover_recipe`'s procedural search that loop one deliberately left PROCEDURAL.

---

## 1. Goal

Two role decisions in `denormalization.py` are declarable rules expressed as **set-algebra Python over the `tab:` RDF graph** — the exact shape the gate calls a *derivation axiom*:

- **The UNPIVOT dim-name-vs-values rule** (`recover_dimensions` / `_axis_dimensions`) — *"a level's values are named by the spanning parent one level up."* The A1.2 UNPIVOT axiom, hand-coded as level-grouping set algebra.
- **The operand-exclusion role** (`_operand_exclusions`) — *"in a pivoted table, level-0 single-leaf columns are stubs/totals, barred as aggregation operands."* A role-over-header-depth rule.

Loop B lifts both to **SPARQL `CONSTRUCT`** over the existing header graph, retiring the Python bodies while keeping every consumer's contract unchanged. Scope is **the two graph-riding role axioms only**; the geometry-bound type/boundary decisions (transpose, header/body split, stub/data split, `regions.classify`) are the queued follow-on (loop B2) because they run mid-compile on Python geometry, before any RDF exists, and first need a typed-cell *evidence graph*.

## 2. Gate compliance (CLAUDE.md §8 — the open/closed split)

- **AXIOM — derivation (open world) → SPARQL `CONSTRUCT`.** Both rules *grow* the graph from header evidence (they emit `tab:PivotedDimension` nodes / a `tab:barredAsOperand` role mark). Monotonic and evidence-positive: a dimension or a role mark is derived only when its supporting header structure is *present*, never inferred from absence. This is the correct world for recovery (§7 — assert only what the source supports).
- **Closed-world guards are holon-scoped.** The rules contain counting / completeness / disjointness conditions ("*exactly one* spanning parent," "covers *all* leaves," "*disjoint* from the stubs," "*∃* a level-≥1 column"). These are expressed as **query-local** `COUNT(…)=1` / `NOT EXISTS` / `FILTER` / `EXISTS` — closed *within the one table-holon*, while the graph stays open. The holon is the closure boundary; no SHACL (global closed-world) is used, because this is derivation, not membrane validation.
- **PROCEDURAL (justified, each with a why-irreducible note):** (1) `interpret.run` engine glue (from loop one); (2) the thin **RDF→dataclass reader** that maps the constructed `tab:PivotedDimension` nodes back into the existing `PivotedDimension` dataclasses (and the role marks into the existing `set`) for unchanged consumers — reconstruction glue, not transform logic.
- **Out of gate scope:** `detect_aggregations`' exact-arithmetic subtotal detection stays PROCEDURAL (audit H2 — decidable arithmetic); loop B lifts only the *role* parts it depends on.
- **NEURAL:** none.

## 3. The rule, exactly (what the CONSTRUCT must reproduce)

`_axis_dimensions(g, t, axis, covers_pred, leaves)` (denormalization.py:49) processes, per axis, the header nodes that cover ≥1 leaf on that axis, grouped by `tab:headerLevel`, in ascending level order, carrying a `pending_name`:

> At a level: let **multi** = nodes covering >1 leaf, **singles_cov** = union of the coverage of single-leaf nodes. **If** there is *exactly one* `multi` node **and** `multi.cov ∪ singles_cov ⊇ all-leaves` **and** `multi.cov ∩ singles_cov = ∅` → this is a **naming level**: set `pending_name := multi.label`, emit nothing. **Else** → emit `PivotedDimension(axis, level, pending_name, values)` where `values` = the level's distinct node labels ordered by min covered-column position; reset `pending_name := None`.

`recover_dimensions` (denormalization.py:82) runs this for the column axis (`coversColumn`) and the row axis (`coversRow`) and concatenates. A flat single-level axis (all level-0 leaf nodes) takes the *else* branch at level 0 and yields one `PivotedDimension(axis, 0, None, all-labels)`.

**Declarative reformulation (the CONSTRUCT's shape).** The stateful `pending_name` carry collapses to a **level-offset join**: a value-level `L` is *named* by the level-`(L-1)` node `P` iff `P` covers >1 leaf, `P` is the *unique* multi-cover at `L-1`, and the `L-1` singles together with `P` cover all leaves disjointly. So the CONSTRUCT emits, per axis and per emitted level `L`:

```
?dim a tab:PivotedDimension ; tab:onAxis ?axis ; tab:atLevel ?L ;
     tab:dimensionName ?parentLabel ;        # OPTIONAL — only when a qualifying parent exists at L-1
     tab:hasDimensionValue ?v0, ?v1, … .      # distinct labels of the level-L nodes
```
guarded by holon-scoped aggregates (`COUNT(?multi)=1`, coverage `NOT EXISTS { leaf not covered by P∪singles }`, disjointness `NOT EXISTS { leaf covered by both }`), and the level itself is an *emitted* (non-naming) level (`FILTER NOT EXISTS { this level qualifies as a naming level }`).

`_operand_exclusions` (denormalization.py:162) is simpler: if `EXISTS { ?c a tab:hasLeafColumn target with headerLevel ≥ 1 }` (the table is pivoted), CONSTRUCT `?c tab:barredAsOperand true` for every column whose *max* covering header level is 0; else emit nothing.

## 4. Feasibility probe (task one — non-negotiable, as in loop one)

The cross-level naming carry and the multi-condition guard are the genuine **SPARQL-expressibility risk**. Task one promotes a probe to a test: the `recover-dimensions.rq` CONSTRUCT, run via `interpret.run` over (a) the real `region_pivot` fixture and (b) a constructed multi-level hierarchical header graph, must reproduce `_axis_dimensions`' `PivotedDimension` output exactly (name + ordered values, both axes) **before** the rest is built. **If** a genuinely stateful residue (e.g. two consecutive naming levels that do not reduce to a single level-offset join) exceeds standard `CONSTRUCT`, that specific piece is **justified PROCEDURAL** with a why-irreducible note (the SPARQL-ceiling rule — standard SPARQL only, never extended). The probe decides; the plan does not assume expressibility.

## 5. Components

| Unit | Responsibility | Gate |
| --- | --- | --- |
| `vocab/queries/recover-dimensions.rq` (create) | CONSTRUCT `tab:PivotedDimension` nodes (onAxis/atLevel/dimensionName?/hasDimensionValue*) from header evidence, both axes, encoding the UNPIVOT rule with holon-scoped guards | AXIOM (derivation) |
| `vocab/queries/operand-exclusions.rq` (create) | CONSTRUCT `tab:barredAsOperand` on level-0 single-leaf columns, guarded by the pivoted-table `EXISTS` | AXIOM (derivation) |
| `vocab/ontology/tab.ttl` (modify) | add the owned role predicate `tab:barredAsOperand` (`rdfs:domain tab:LeafColumn`, `rdfs:range xsd:boolean`) | owned vocab |
| `src/iladub/etkl/denormalization.py` (modify) | `recover_dimensions` runs `recover-dimensions.rq` via `interpret` → thin reader → `PivotedDimension` dataclasses (values ordered by leaf-column position); `_operand_exclusions` runs `operand-exclusions.rq` → reads marks into the existing `set`. Set-algebra bodies of `_axis_dimensions`/`_operand_exclusions` retire | AXIOM exec + PROCEDURAL reader |
| `tests/etkl/test_role_axioms.py` (create) | per-`.rq` unit tests (the UNPIVOT axiom over constructed header graphs, both axes; operand exclusion over a pivoted + a flat graph) | test |
| `tests/etkl/test_transform_gate.py` (modify) | the new `.rq` are covered by the existing "no tuned constant in `vocab/queries/*.rq`" assertion (glob already matches; confirm) | gate test |

**Retired:** the set-algebra Python bodies of `_axis_dimensions` and `_operand_exclusions`. **Kept PROCEDURAL:** `interpret.run`, the RDF→dataclass reader, `detect_aggregations`' exact arithmetic (out of scope), `_num`/`_value_matrix` (raw typing/extraction).

## 6. Data flow

```
compiled tab: header graph
   │
   ▼  interpret.run(recover-dimensions.rq)         [AXIOM · derivation · open-world]
 tab:PivotedDimension RDF (both axes)
   │
   ▼  thin reader → PivotedDimension dataclasses (values re-ordered by leaf-column position)   [PROCEDURAL]
   │
   ▼  (UNCHANGED consumers) recover_recipe · annotate_dimensions · emit_base_facts · analyze · _nameless_col_pivots

compiled tab: header graph
   │
   ▼  interpret.run(operand-exclusions.rq)          [AXIOM · derivation]
 tab:barredAsOperand marks  →  reader → set  →  (UNCHANGED) detect_aggregations
```

`recover_dimensions(g,t) -> list[PivotedDimension]` and `_operand_exclusions(g,t) -> set` keep their exact signatures and return types; only the *body* changes from Python set-algebra to SPARQL-execution + read-back. (`recover_dimensions` and the `PivotedDimension` dataclass are **public exports** in `iladub.etkl.__init__` — the public API is preserved.)

## 7. Testing

- **Behavioural spec = the shipped suites, unchanged:** `tests/etkl/test_denormalization.py` (`recover_dimensions`, `detect_aggregations`, `emit_base_facts`, `analyze`), `test_reshape_recover.py` / `test_reshape_certify.py` (`recover_recipe` consumes the dims), `test_certify_proposals.py`, `test_denorm_integration.py`. If any needs an assertion change, that is a supersession defect to investigate, not a test to loosen.
- **New per-`.rq` unit tests** (`test_role_axioms.py`): the inverse-free `recover-dimensions.rq` over a constructed column pivot (named spanning parent + stub) yields the exact `PivotedDimension` (name + ordered values); over a row-axis pivot (mirror via `coversRow`); over a flat single-level axis yields one nameless value-dimension; over a multi-level hierarchical header reproduces `_axis_dimensions`. `operand-exclusions.rq` bars level-0 columns in a pivoted graph and bars nothing in a flat graph.
- **Probe-as-test** (task one): the region-pivot reproduction, promoted from the feasibility probe.
- **Gate test:** the new `.rq` carry no tuned constant (they are pure set-algebra/structure — confirm the existing `test_transform_gate` glob covers `vocab/queries/*.rq`).

## 8. Source ownership / conventions

- The `.rq` reference only `tab:` (owned) + standard SPARQL. `tab:barredAsOperand` is an owned `tab:` term added to the standalone `tab.ttl` (no HGA/FnO). No HGA term appears as a subject.
- The derived `tab:PivotedDimension` nodes are the same class `annotate_dimensions` already emits — the CONSTRUCT *is* the declarative form of that evidence, now produced by rule rather than Python.

## 9. Honest gaps & scope boundaries

- **In scope:** the two graph-riding role axioms (`recover_dimensions`/`_axis_dimensions`, `_operand_exclusions`) → SPARQL `CONSTRUCT`, retiring their Python bodies, consumers unchanged.
- **Out of scope:** the geometry-bound type/boundary decisions (transpose, header/body split, stub/data split, `regions.classify`) — they run mid-compile on Python `Band`/`grid`/`Cell` objects before any RDF exists; lifting them needs a typed-cell *evidence graph* materialized mid-pipeline + feedback into the compile cascade. That is a distinct architecture and its own loop (**B2**). `detect_aggregations`' exact arithmetic stays PROCEDURAL (audit H2). `C` (redundant-tiling-backstop deletion) remains queued.
- **The SPARQL-expressibility risk is real and probed first** (§4). We prefer SPARQL and accept Python *at the genuine ceiling* (justified PROCEDURAL), never extend SPARQL.
- **Values-ordering** is reconstructed by the reader (RDF `hasDimensionValue` is a set; the dataclass `values` tuple is ordered by covered-column position). The reader re-derives the order using the *same key* as `_axis_dimensions` — the minimum covered leaf-column (by IRI) per distinct label — a deterministic reconstruction, not a stored order.

## 10. Settled design decisions (for the implementation plan)

- **Mechanism: SPARQL `CONSTRUCT`** (open-world derivation), executed via loop one's `interpret.run`, with a thin RDF→dataclass reader. *Not* SHACL: this is derivation, not membrane validation — using closed-world/SHACL to derive would risk inferring-by-absence, which §7 forbids (the open/closed split, CLAUDE.md §8).
- **Both axioms in this slice:** `recover_dimensions`/`_axis_dimensions` **and** `_operand_exclusions`.
- **Probe first** (task one) validates SPARQL-expressibility before the rest is built; ceiling residue is justified PROCEDURAL.
- **Behavioural suites stay green unchanged;** signatures/return types of `recover_dimensions` and `_operand_exclusions` are preserved.

**Resume pointer:** design + gate refinement (CLAUDE.md §8 open/closed split) committed on `main`. **Next action:** invoke `superpowers:writing-plans` on this spec → task-by-task plan (probe → recover-dimensions.rq + reader → operand-exclusions.rq + reader → supersession verification) → subagent-driven execution. **After B:** B2 (geometry-bound type/boundary via a typed-cell evidence graph) and C (backstop deletion) remain queued.
