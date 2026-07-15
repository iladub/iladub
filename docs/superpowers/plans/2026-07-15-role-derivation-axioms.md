# Role-Derivation Axioms over the `tab:` Graph (Loop B) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lift the two graph-riding role decisions — the UNPIVOT dim-name-vs-values rule (`recover_dimensions`/`_axis_dimensions`) and the operand-exclusion role (`_operand_exclusions`) — from set-algebra Python to declarative **SPARQL `CONSTRUCT`** over the existing `tab:` header graph, retiring the Python bodies while keeping every consumer's contract unchanged.

**Architecture:** The UNPIVOT rule is realized as a **two-pass CONSTRUCT pipeline** (feasibility-proven 2026-07-15 against a Python port of `_axis_dimensions`, flat/2-level/3-level, exact match): **pass 1** `name-levels.rq` marks each spanning parent that *names* the level below (`?parent tab:namesLevel ?L`) under the naming condition (unique multi + completeness + disjointness, all holon-scoped); **pass 2** `recover-dimensions.rq` emits a `tab:PivotedDimension` for every value-level that is not itself a naming level, taking its `dimensionName` from the pass-1 mark when present. Both run via loop one's `interpret.run`. A thin PROCEDURAL reader maps the constructed RDF back to the existing `PivotedDimension` dataclasses (reproducing value order); `operand-exclusions.rq` marks barred columns. The **anti-overfit oracle** is a differential test comparing the CONSTRUCT pipeline to a frozen Python reference over a *battery* of header shapes — not fixed fixtures.

**Tech Stack:** Python 3, rdflib (SPARQL 1.1 CONSTRUCT), pytest. No new dependency. Reuses `iladub.etkl.interpret.run` from loop one.

## Global Constraints

Copied verbatim from CLAUDE.md §8 (the neurosymbolic-first gate, now with the **open/closed split**) and the spec (`docs/superpowers/specs/2026-07-15-role-derivation-axioms-design.md`). Every task's requirements implicitly include this section. **Reviewers enforce it.**

- **AXIOM — derivation (open world) → SPARQL `CONSTRUCT`.** Both rules *grow* the graph from header evidence (emit `tab:PivotedDimension` / `tab:namesLevel` / `tab:barredAsOperand`). Monotonic and evidence-positive: derived only when supporting header structure is *present*, never inferred from absence. **No transform logic in Python; no tuned constant/tolerance anywhere in the `.rq` files.**
- **Holon-scoped closed-world guards.** Counting/completeness/disjointness ("exactly one spanning parent," "covers all leaves," "disjoint from stubs," "∃ a level-≥1 column") are expressed **query-local** (`NOT EXISTS` / `FILTER` / `EXISTS`) — closed *within the one table-holon*, graph stays open. **No SHACL** (this is derivation, not membrane validation — using closed-world/SHACL to derive would risk inferring-by-absence, forbidden by §7).
- **PROCEDURAL (justified, each with a why-irreducible note):** (1) `interpret.run` engine glue (loop one); (2) the thin **RDF→dataclass reader** — reconstruction glue, including value-**ordering** (presentation, not a role decision), not transform logic. No tuned constant.
- **SPARQL-ceiling rule:** standard SPARQL only — never extended. The pipeline is feasibility-proven for the shapes below; if a subagent encounters a genuinely deeper shape that resists standard SPARQL even two-pass, that specific residue is a **justified PROCEDURAL** reader assist with a why-irreducible note — *escalate first*, do not extend SPARQL and do not add a tuned constant.
- **Behavioural spec = the shipped suites, unchanged:** `tests/etkl/test_denormalization.py`, `test_reshape_recover.py`, `test_reshape_certify.py`, `test_certify_proposals.py`, `test_denorm_integration.py`, `test_promote*.py` must end green with their existing assertions. `recover_dimensions(g,t) -> list[PivotedDimension]` and `_operand_exclusions(g,t) -> set` keep exact signatures/return types; `recover_dimensions` and `PivotedDimension` stay public exports in `iladub.etkl.__init__`. A behavioural test needing an assertion change is a supersession defect to investigate, not loosen.
- **Anti-overfit (ZERO TOLERANCE):** the lift must reproduce `_axis_dimensions` **generally**, proven by a differential oracle over a battery of shapes (flat, 2-level, 3-level, row-axis mirror, multi-stub) — never tuned to pass the two shipped fixtures.
- **Source ownership:** `.rq` reference only `tab:` (owned) + standard SPARQL. New `tab:` terms (`tab:namesLevel`, `tab:barredAsOperand`) go in the standalone `tab.ttl`. No HGA/FnO term as a subject.
- **Scope:** the two graph-riding role axioms only. Geometry-bound decisions (transpose, header/body split, stub/data split, `regions.classify`) are loop B2 (need a mid-compile typed-cell evidence graph). `detect_aggregations`' exact arithmetic stays PROCEDURAL (out of scope).

---

## File Structure

**Create:**
- `vocab/queries/name-levels.rq` — pass 1: CONSTRUCT `?parent tab:namesLevel ?L` for each naming parent, both axes. [AXIOM]
- `vocab/queries/recover-dimensions.rq` — pass 2: CONSTRUCT `tab:PivotedDimension` nodes joining value-levels with the pass-1 marks, both axes. [AXIOM]
- `vocab/queries/operand-exclusions.rq` — CONSTRUCT `tab:barredAsOperand` on level-0 single-leaf columns in a pivoted table. [AXIOM]
- `tests/etkl/test_role_axioms.py` — the differential oracle (frozen `_ref_axis_dimensions` port + a shape battery) and per-`.rq` unit tests.

**Modify:**
- `vocab/ontology/tab.ttl` — add owned `tab:namesLevel` (transient inference mark) and `tab:barredAsOperand`.
- `src/iladub/etkl/denormalization.py` — `recover_dimensions` runs the two-pass pipeline via `interpret` + thin reader → `PivotedDimension` dataclasses; `_operand_exclusions` runs its `.rq` + reads marks; the set-algebra bodies of `_axis_dimensions`/`_operand_exclusions` retire.
- `tests/etkl/test_transform_gate.py` — confirm the new `.rq` are covered by the existing "no tuned constant in `vocab/queries/*.rq`" glob (they are).

---

## Task 1: Pass 1 — `name-levels.rq` + the differential oracle harness

Build and prove pass 1 (the hard part: the naming condition) and the anti-overfit oracle. The query below is **feasibility-proven** (column axis) — this task promotes it, generalizes it to both axes, and validates the marks against the frozen reference.

**Files:**
- Create: `vocab/queries/name-levels.rq`
- Create: `tests/etkl/test_role_axioms.py`
- Modify: `vocab/ontology/tab.ttl` (add `tab:namesLevel`)

**Interfaces:**
- Produces: `vocab/queries/name-levels.rq` — over a `tab:` header graph, CONSTRUCT `?parent tab:namesLevel ?L` for each header node `?parent` at level `L-1` that is the unique multi-cover node whose coverage plus the level-(L-1) single-leaf nodes cover all leaves disjointly, and level `L` has value nodes under it. Both axes (column via `tab:coversColumn`, row via `tab:coversRow`). Consumed by pass 2 (Task 2).
- Produces: `tests/etkl/test_role_axioms.py::_ref_axis_dimensions(g, t)` — a frozen Python port of `_axis_dimensions` (the differential oracle), and `_battery()` of constructed header graphs. Consumed by Tasks 1–3 tests.

- [ ] **Step 1: Write the failing test — the oracle harness + pass-1 marks**

Create `tests/etkl/test_role_axioms.py`:

```python
import os
from rdflib import Graph, Namespace, URIRef, Literal, RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
EX = Namespace("https://example.org/d#")
QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "vocab", "queries")


# ---- graph builders (both axes via a covers-predicate arg) ----
def _hdr(g, t, u, lvl, lbl, covers, cpred):
    g.add((u, RDF.type, TAB.HeaderNode)); g.add((t, TAB.hasHeaderNode, u))
    g.add((u, TAB.headerLevel, Literal(lvl)))
    if lbl is not None:
        lc = URIRef(str(u) + "-l"); g.add((lc, TAB.cellText, Literal(lbl))); g.add((u, TAB.hasLabel, lc))
    for c in covers:
        g.add((u, cpred, c))


def _leaves(g, t, leafpred, *xs):
    cls = TAB.LeafColumn if leafpred == TAB.hasLeafColumn else TAB.LeafRow
    for x in xs:
        g.add((x, RDF.type, cls)); g.add((t, leafpred, x))


def _build(axis):
    """Return a dict label->(graph, table) of shapes on `axis` ('column'|'row')."""
    cp = TAB.coversColumn if axis == "column" else TAB.coversRow
    lp = TAB.hasLeafColumn if axis == "column" else TAB.hasLeafRow
    out = {}

    g = Graph(); t = EX.t; a, b, c = EX.a, EX.b, EX.c            # flat: 3 single level-0
    _leaves(g, t, lp, a, b, c)
    _hdr(g, t, EX.hA, 0, "Name", [a], cp); _hdr(g, t, EX.hB, 0, "Age", [b], cp); _hdr(g, t, EX.hC, 0, "City", [c], cp)
    out["flat"] = (g, t)

    g = Graph(); t = EX.t; y, n, s, e, w = EX.y, EX.n, EX.s, EX.e, EX.w   # region: stub + spanned
    _leaves(g, t, lp, y, n, s, e, w)
    _hdr(g, t, EX.hY, 0, "Year", [y], cp); _hdr(g, t, EX.hR, 0, "Region", [n, s, e, w], cp)
    _hdr(g, t, EX.hN, 1, "North", [n], cp); _hdr(g, t, EX.hS, 1, "South", [s], cp)
    _hdr(g, t, EX.hE, 1, "East", [e], cp); _hdr(g, t, EX.hW, 1, "West", [w], cp)
    out["region"] = (g, t)

    g = Graph(); t = EX.t; q = [EX["q%d" % i] for i in range(4)]  # hier: 3 levels
    _leaves(g, t, lp, *q)
    _hdr(g, t, EX.hM, 0, "Metrics", q, cp)
    _hdr(g, t, EX.h23, 1, "2023", [q[0], q[1]], cp); _hdr(g, t, EX.h24, 1, "2024", [q[2], q[3]], cp)
    for i, nm in enumerate(["Q1", "Q2", "Q3", "Q4"]):
        _hdr(g, t, EX["hq%d" % i], 2, nm, [q[i]], cp)
    out["hier"] = (g, t)
    return out


def _battery():
    b = {}
    for axis in ("column", "row"):
        for k, v in _build(axis).items():
            b["%s-%s" % (axis, k)] = (axis, v[0], v[1])
    return b


# ---- frozen reference: a port of _axis_dimensions (the anti-overfit oracle) ----
def _ref_axis_dimensions(g, t, axis):
    cp = TAB.coversColumn if axis == "column" else TAB.coversRow
    lp = TAB.hasLeafColumn if axis == "column" else TAB.hasLeafRow
    leaves = sorted(g.objects(t, lp), key=str)
    nodes = [h for h in g.objects(t, TAB.hasHeaderNode) if any(True for _ in g.objects(h, cp))]
    if not nodes:
        return []
    def label(h):
        lc = g.value(h, TAB.hasLabel); return str(g.value(lc, TAB.cellText)) if lc is not None else None
    by_level = {}
    for h in nodes:
        lvl = int(g.value(h, TAB.headerLevel)); cov = frozenset(g.objects(h, cp))
        by_level.setdefault(lvl, []).append((h, label(h), cov))
    dims, pending = [], None
    for lvl in sorted(by_level):
        ln = by_level[lvl]; multi = [x for x in ln if len(x[2]) > 1]
        singles = set().union(*[x[2] for x in ln if len(x[2]) == 1]) if any(len(x[2]) == 1 for x in ln) else set()
        if len(multi) == 1 and (multi[0][2] | singles) >= set(leaves) and not (multi[0][2] & singles):
            pending = multi[0][1]; continue
        seen, vals = set(), []
        for _, lbl, _c in sorted(ln, key=lambda z: min(str(c) for c in z[2])):
            if lbl is not None and lbl not in seen:
                seen.add(lbl); vals.append(lbl)
        dims.append((axis, lvl, pending, tuple(vals))); pending = None
    return dims


def _run(query_file, *graphs):
    union = Graph()
    for g in graphs:
        union += g
    out = Graph()
    for tr in union.query(open(os.path.join(QUERIES, query_file), encoding="utf-8").read()):
        out.add(tr)
    return out


def test_name_levels_marks_the_naming_parent():
    for key, (axis, g, t) in _battery().items():
        marks = _run("name-levels.rq", g)
        got = {(str(g.value(p, TAB.hasLabel and TAB.hasLabel) or p), int(l), str(a))
               for p, a, l in [(p, str(marks.value(p, TAB.onAxis)) if False else axis, l)
                               for p, _, l in marks.triples((None, TAB.namesLevel, None))]}
        # simpler: collect (parent-label, level) and compare to the reference's naming levels
        marked = {(str(g.value(g.value(p, TAB.hasLabel), TAB.cellText)), int(l))
                  for p, _, l in marks.triples((None, TAB.namesLevel, None))}
        # reference naming: a level whose emitted dim carries a name means the parent named it
        ref_named = {(nm, lvl) for (ax, lvl, nm, vals) in _ref_axis_dimensions(g, t, axis) if nm is not None}
        assert marked == ref_named, "%s: marks=%s ref=%s" % (key, marked, ref_named)
```

(Note: the reader/battery helpers `_battery`, `_ref_axis_dimensions`, `_run` are reused by Tasks 2–3; keep them tidy. The double-lookup in `test_name_levels_marks_the_naming_parent` collects `(parent-label, named-level)` from the marks and compares to the reference's named levels.)

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py::test_name_levels_marks_the_naming_parent -v`
Expected: FAIL — `name-levels.rq` does not exist (FileNotFoundError).

- [ ] **Step 3: Add `tab:namesLevel` to `tab.ttl`**

In `vocab/ontology/tab.ttl`, after the reshape-recipe block, add:

```turtle
# --- transient inference marks (recovery pass; not stored in a holon) ---
tab:namesLevel a owl:DatatypeProperty ; rdfs:domain tab:HeaderNode ; rdfs:range xsd:integer ;
    rdfs:label "names level"@en ;
    rdfs:comment "A recovery mark: this header node (a unique spanning parent) NAMES the pivoted dimension one header level below it. Produced by the name-levels derivation; transient, not asserted into a holon."@en .
```

- [ ] **Step 4: Implement `name-levels.rq` (both axes)**

Create `vocab/queries/name-levels.rq`. The column-axis body is the proven probe; both axes are handled by a `VALUES`-bound covers-predicate + leaf-predicate. (If rdflib rejects the variable predicate in any pattern, fall back to two `UNION` blocks — one per axis — with the identical body; do **not** change the logic.)

```sparql
# name-levels.rq — pass 1: mark each spanning parent that NAMES the level below it.
# A parent ?M at level ?PL names level ?L = ?PL+1 iff: ?M is the UNIQUE multi-cover node at ?PL;
# ?M plus the level-?PL single-leaf nodes cover all leaves; ?M is disjoint from those singles;
# and level ?L has value nodes under ?M. Counting/completeness/disjointness are holon-scoped
# (query-local NOT EXISTS). Feasibility-proven against _axis_dimensions (flat/2-level/3-level).
PREFIX tab: <https://w3id.org/iladub/tab#>
CONSTRUCT { ?M tab:namesLevel ?L . }
WHERE {
  VALUES (?cp ?lp) { (tab:coversColumn tab:hasLeafColumn) (tab:coversRow tab:hasLeafRow) }
  ?T tab:hasHeaderNode ?M . ?M tab:headerLevel ?PL ; ?cp ?ma, ?mb . FILTER(?ma != ?mb)
  BIND(?PL + 1 AS ?L)
  FILTER EXISTS { ?T tab:hasHeaderNode ?vn . ?vn tab:headerLevel ?L ; ?cp ?vl . FILTER EXISTS { ?M ?cp ?vl } }
  FILTER NOT EXISTS { ?M2 tab:headerLevel ?PL ; ?cp ?x, ?y . FILTER(?x != ?y && ?M2 != ?M) . ?T tab:hasHeaderNode ?M2 }
  FILTER NOT EXISTS {
    ?T ?lp ?lf .
    FILTER NOT EXISTS { ?M ?cp ?lf }
    FILTER NOT EXISTS { ?sg tab:headerLevel ?PL ; ?cp ?lf . ?T tab:hasHeaderNode ?sg .
                        FILTER NOT EXISTS { ?sg ?cp ?o . FILTER(?o != ?lf) } }
  }
  FILTER NOT EXISTS {
    ?M ?cp ?lf2 . ?sg2 tab:headerLevel ?PL ; ?cp ?lf2 . ?T tab:hasHeaderNode ?sg2 . FILTER(?sg2 != ?M)
    FILTER NOT EXISTS { ?sg2 ?cp ?o2 . FILTER(?o2 != ?lf2) }
  }
}
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py::test_name_levels_marks_the_naming_parent -v`
Expected: PASS across all six battery shapes (both axes × flat/region/hier). If the `VALUES` variable-predicate form fails in rdflib, switch to the two-`UNION` form (identical logic) and re-run — the marks must match `_ref_axis_dimensions`' named levels exactly.

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/name-levels.rq vocab/ontology/tab.ttl tests/etkl/test_role_axioms.py
git commit -m "feat(etkl): name-levels.rq (pass 1) + differential oracle — UNPIVOT naming condition as SPARQL [B task 1]

Marks each unique spanning parent that names the level below (holon-scoped unique-multi +
completeness + disjointness). Proven against a frozen _axis_dimensions port over a shape battery.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Pass 2 — `recover-dimensions.rq` + full differential equivalence

Emit the `tab:PivotedDimension` nodes from value-levels + the pass-1 marks, and prove the **full two-pass pipeline** equals `_axis_dimensions` over the whole battery (semantic content: axis, level, name, value-set).

**Files:**
- Create: `vocab/queries/recover-dimensions.rq`
- Modify: `tests/etkl/test_role_axioms.py` (add the pipeline differential test)

**Interfaces:**
- Produces: `vocab/queries/recover-dimensions.rq` — over (header graph + pass-1 marks), CONSTRUCT `?dim a tab:PivotedDimension ; tab:onAxis ?axis ; tab:atLevel ?L ; tab:hasDimensionValue ?label ; [tab:dimensionName ?name]` for every value-level `L` that is not a naming level; `?dim` keyed by `(table, axis, L)`. Consumed by the reader (Task 3).
- Consumes: `name-levels.rq` output (Task 1).

- [ ] **Step 1: Write the failing differential test**

Add to `tests/etkl/test_role_axioms.py`:

```python
def _pipeline_dims(g, t):
    """Run pass1 + pass2 and read PivotedDimension RDF into (axis, level, name, frozenset(values))."""
    marks = _run("name-levels.rq", g)
    out = _run("recover-dimensions.rq", g, marks)
    dims = []
    for d in out.subjects(RDF.type, TAB.PivotedDimension):
        axis = str(out.value(d, TAB.onAxis)); lvl = int(out.value(d, TAB.atLevel))
        nm = out.value(d, TAB.dimensionName); nm = str(nm) if nm is not None else None
        vals = frozenset(str(v) for v in out.objects(d, TAB.hasDimensionValue))
        dims.append((axis, lvl, nm, vals))
    return sorted(dims, key=lambda z: (z[0], z[1]))


def test_pipeline_matches_axis_dimensions_semantics():
    for key, (axis, g, t) in _battery().items():
        ref = sorted(((ax, lvl, nm, frozenset(vals)) for (ax, lvl, nm, vals) in _ref_axis_dimensions(g, t, axis)),
                     key=lambda z: (z[0], z[1]))
        got = _pipeline_dims(g, t)
        assert got == ref, "%s: got=%s ref=%s" % (key, got, ref)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py::test_pipeline_matches_axis_dimensions_semantics -v`
Expected: FAIL — `recover-dimensions.rq` does not exist.

- [ ] **Step 3: Implement `recover-dimensions.rq` (both axes)**

Create `vocab/queries/recover-dimensions.rq` (proven two-pass logic; both axes via the value node's own axis, derived from which covers-predicate it uses):

```sparql
# recover-dimensions.rq — pass 2: emit a PivotedDimension per value-level (not a naming level),
# named by the pass-1 tab:namesLevel mark when present. A value-level L is a naming level iff
# some parent names level L+1 (then L is absorbed, not emitted). ?dim is keyed by (table,axis,L)
# so all value nodes at that level aggregate into one dimension.
PREFIX tab: <https://w3id.org/iladub/tab#>
CONSTRUCT {
  ?dim a tab:PivotedDimension ; tab:onAxis ?axis ; tab:atLevel ?L ; tab:hasDimensionValue ?vlabel .
  ?dim tab:dimensionName ?pname .
}
WHERE {
  VALUES (?cp ?axis) { (tab:coversColumn "column") (tab:coversRow "row") }
  ?T tab:hasHeaderNode ?vnode . ?vnode tab:headerLevel ?L ; ?cp ?vl ; tab:hasLabel [ tab:cellText ?vlabel ] .
  BIND(IRI(CONCAT(STR(?T), "-dim-", ?axis, "-", STR(?L))) AS ?dim)
  # L is not a naming level  <=>  no SAME-TABLE, SAME-AXIS parent names level L+1.
  # (The namesLevel marks carry no table/axis, so re-join ?anyp to the current ?T + ?cp — else a
  #  row-axis mark would suppress a column-axis dimension in a crosstab. Task-2 review fix.)
  FILTER NOT EXISTS { ?anyp tab:namesLevel ?L1 . ?T tab:hasHeaderNode ?anyp . ?anyp ?cp ?anyleaf . FILTER(?L1 = ?L + 1) }
  OPTIONAL { ?p tab:namesLevel ?L ; tab:hasLabel [ tab:cellText ?pname ] . ?T tab:hasHeaderNode ?p . ?p ?cp ?pleaf . }
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py -v`
Expected: PASS (both `test_name_levels_*` and `test_pipeline_matches_axis_dimensions_semantics`, all six battery shapes). The pipeline's (axis, level, name, value-set) must equal the frozen reference. If a shape mismatches, the query is wrong — fix the query, never the oracle or the battery.

- [ ] **Step 5: Commit**

```bash
git add vocab/queries/recover-dimensions.rq tests/etkl/test_role_axioms.py
git commit -m "feat(etkl): recover-dimensions.rq (pass 2) — PivotedDimension derivation matches _axis_dimensions [B task 2]

Full two-pass pipeline (name-levels -> recover-dimensions) reproduces _axis_dimensions' semantics
(axis/level/name/value-set) over the shape battery, both axes. AXIOM derivation; no tuned constant.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Reader + `recover_dimensions` rewire (retire `_axis_dimensions`)

Wire the two-pass pipeline into `recover_dimensions` via `interpret`, with a thin reader that reproduces the `PivotedDimension` dataclasses **including value order**; retire the set-algebra `_axis_dimensions` body. Behavioural suites green.

**Files:**
- Modify: `src/iladub/etkl/denormalization.py`
- Modify: `tests/etkl/test_role_axioms.py` (add the ordered-equivalence + reader test)

**Interfaces:**
- Consumes: `interpret.run` (loop one), `name-levels.rq` + `recover-dimensions.rq` (Tasks 1–2).
- Produces: `recover_dimensions(g, t) -> list[PivotedDimension]` (unchanged signature/return; values ordered by minimum covered leaf per label, matching the retired `_axis_dimensions`).

- [ ] **Step 1: Write the failing ordered-equivalence test**

Add to `tests/etkl/test_role_axioms.py`:

```python
def test_recover_dimensions_reproduces_ordered_dataclasses():
    from iladub.etkl.denormalization import recover_dimensions, PivotedDimension
    for key, (axis, g, t) in _battery().items():
        got = [d for d in recover_dimensions(g, t) if d.axis == axis]
        ref = [PivotedDimension(ax, lvl, nm, vals) for (ax, lvl, nm, vals) in _ref_axis_dimensions(g, t, axis)]
        assert got == ref, "%s: got=%s ref=%s" % (key, got, ref)   # exact tuple incl. value ORDER
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py::test_recover_dimensions_reproduces_ordered_dataclasses -v`
Expected: FAIL — `recover_dimensions` still uses the old `_axis_dimensions` (this passes today) OR fails only after the rewrite. To make RED meaningful, first assert the NEW mechanism: temporarily the test drives the rewrite. (If it passes pre-change because old code already matches the reference, that is expected — the test's job is to stay green THROUGH the rewrite, guaranteeing no behavioural drift; proceed to Step 3 and confirm it stays green.)

- [ ] **Step 3: Implement the reader + rewire `recover_dimensions`; retire `_axis_dimensions`**

In `src/iladub/etkl/denormalization.py`: add `import os` and `from . import interpret` (and reuse the module's `TAB`). Add `_QUERIES` (three `..`, matching `oracle.py`/`reshape.py` — `denormalization.py` sits at `src/iladub/etkl/`):

```python
import os
from . import interpret
_QUERIES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "vocab", "queries")


def _read_dimensions(dimgraph, g, t):
    """PROCEDURAL reconstruction glue: map the derived tab:PivotedDimension RDF into the
    PivotedDimension dataclasses. Value ORDER (presentation, not a role decision) is
    re-derived by the same key as the retired _axis_dimensions — the minimum covered leaf
    (by IRI) per label — so the dataclass is reproduced exactly."""
    dims = []
    for dn in dimgraph.subjects(RDF.type, TAB.PivotedDimension):
        axis = str(dimgraph.value(dn, TAB.onAxis))
        level = int(dimgraph.value(dn, TAB.atLevel))
        name = dimgraph.value(dn, TAB.dimensionName)
        name = str(name) if name is not None else None
        labels = {str(v) for v in dimgraph.objects(dn, TAB.hasDimensionValue)}
        cp = TAB.coversColumn if axis == "column" else TAB.coversRow

        def _minleaf(lbl):
            best = None
            for h in g.subjects(TAB.headerLevel, Literal(level)):
                if (t, TAB.hasHeaderNode, h) not in g:
                    continue
                lc = g.value(h, TAB.hasLabel)
                if lc is None or str(g.value(lc, TAB.cellText)) != lbl:
                    continue
                m = min((str(c) for c in g.objects(h, cp)), default=None)
                if m is not None and (best is None or m < best):
                    best = m
            return best or lbl

        values = tuple(sorted(labels, key=_minleaf))
        dims.append(PivotedDimension(axis, level, name, values))
    # column dims first (level order), then row dims (level order) — matches recover_dimensions
    return ([d for d in sorted(dims, key=lambda z: z.level) if d.axis == "column"]
            + [d for d in sorted(dims, key=lambda z: z.level) if d.axis == "row"])


def recover_dimensions(g, t):
    """Recover pivoted dimensions from BOTH header axes via the declarative two-pass
    derivation (name-levels -> recover-dimensions, AXIOM), read back into PivotedDimension
    dataclasses. Replaces the set-algebra _axis_dimensions body; signature unchanged."""
    marks = interpret.run(os.path.join(_QUERIES, "name-levels.rq"), g)
    dimgraph = interpret.run(os.path.join(_QUERIES, "recover-dimensions.rq"), g, marks)
    return _read_dimensions(dimgraph, g, t)
```

Delete the `_axis_dimensions` function (lines 49-79) — its logic now lives in the two `.rq` + the reader. Keep `_leaf_cols`/`_leaf_rows`/`_label` if still referenced elsewhere (grep; remove only if unused).

- [ ] **Step 4: Run role-axiom + behavioural suites**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py tests/etkl/test_denormalization.py tests/etkl/test_reshape_recover.py tests/etkl/test_reshape_certify.py tests/etkl/test_certify_proposals.py tests/etkl/test_denorm_integration.py -v`
Expected: PASS — the ordered-equivalence test green, and every behavioural suite green with existing assertions (`recover_dimensions` output is byte-identical to before). If any behavioural test changes, STOP — supersession defect, investigate.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/denormalization.py tests/etkl/test_role_axioms.py
git commit -m "feat(etkl): recover_dimensions via the two-pass SPARQL derivation; retire _axis_dimensions [B task 3]

recover_dimensions runs name-levels.rq + recover-dimensions.rq via interpret and reads the
PivotedDimension RDF into the dataclasses (value order reconstructed by the same min-leaf key).
Set-algebra _axis_dimensions retired; consumers + behavioural suites unchanged.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: `operand-exclusions.rq` + `_operand_exclusions` rewire

Lift the operand-exclusion role to a CONSTRUCT and rewire `_operand_exclusions` to read its marks; retire the Python body.

**Files:**
- Create: `vocab/queries/operand-exclusions.rq`
- Modify: `vocab/ontology/tab.ttl` (add `tab:barredAsOperand`), `src/iladub/etkl/denormalization.py`, `tests/etkl/test_role_axioms.py`

**Interfaces:**
- Produces: `vocab/queries/operand-exclusions.rq` — CONSTRUCT `?c tab:barredAsOperand true` for each level-0 single-leaf column in a pivoted table (∃ a column with max header level ≥ 1).
- Produces: `_operand_exclusions(g, t) -> set` (unchanged signature/return).

- [ ] **Step 1: Write the failing test**

Add to `tests/etkl/test_role_axioms.py`:

```python
def test_operand_exclusions_matches_reference():
    from iladub.etkl.denormalization import _operand_exclusions
    # pivoted (region, column): Year (level-0 single) is barred; N/S/E/W are measures (not barred)
    axis, g, t = _battery()["column-region"]
    excl = _operand_exclusions(g, t)
    # the Year column EX.y is the level-0 single stub -> barred; measure leaves are not
    assert EX.y in excl
    assert EX.n not in excl and EX.s not in excl
    # flat table: nothing barred
    axis, gf, tf = _battery()["column-flat"]
    assert _operand_exclusions(gf, tf) == set()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py::test_operand_exclusions_matches_reference -v`
Expected: FAIL — `operand-exclusions.rq` does not exist yet (after the rewire in Step 4 it passes); pre-rewire the current Python `_operand_exclusions` already returns `{EX.y}` for region and `set()` for flat, so this test also serves as the behavioural pin THROUGH the rewire.

- [ ] **Step 3: Add `tab:barredAsOperand` + implement `operand-exclusions.rq`**

In `vocab/ontology/tab.ttl`, near `tab:namesLevel`, add:

```turtle
tab:barredAsOperand a owl:DatatypeProperty ; rdfs:domain tab:LeafColumn ; rdfs:range xsd:boolean ;
    rdfs:label "barred as operand"@en ;
    rdfs:comment "A recovery mark: in a pivoted table this level-0 single-leaf column is a stub/total, barred as an aggregation operand. Transient; produced by the operand-exclusions derivation."@en .
```

Create `vocab/queries/operand-exclusions.rq`:

```sparql
# operand-exclusions.rq — in a PIVOTED table (some column has max header level >= 1), the
# level-0 single-leaf columns are stubs/totals, barred as aggregation operands. Holon-scoped
# EXISTS guard for "the table is pivoted".
PREFIX tab: <https://w3id.org/iladub/tab#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
CONSTRUCT { ?c tab:barredAsOperand true . }
WHERE {
  ?t tab:hasLeafColumn ?c .
  # ?c's max covering header level is 0 (only level-0 headers cover it)
  FILTER EXISTS { ?h0 tab:headerLevel 0 ; tab:coversColumn ?c }
  FILTER NOT EXISTS { ?hd tab:headerLevel ?dl ; tab:coversColumn ?c . FILTER(?dl >= 1) }
  # the table is pivoted: some column is covered by a level->=1 header
  FILTER EXISTS { ?any tab:headerLevel ?al ; tab:coversColumn ?cc . ?t tab:hasLeafColumn ?cc . FILTER(?al >= 1) }
}
```

- [ ] **Step 4: Rewire `_operand_exclusions`**

Replace the body of `_operand_exclusions` (denormalization.py:162-180) with:

```python
def _operand_exclusions(g, t):
    """Columns barred as aggregation OPERANDS (level-0 single-leaf stubs/totals in a pivoted
    table), derived by operand-exclusions.rq. Signature/return unchanged."""
    marks = interpret.run(os.path.join(_QUERIES, "operand-exclusions.rq"), g)
    return set(marks.subjects(TAB.barredAsOperand, Literal(True)))
```

- [ ] **Step 5: Run role-axiom + aggregation suites**

Run: `python3 -m pytest tests/etkl/test_role_axioms.py tests/etkl/test_denormalization.py tests/etkl/test_reshape_certify.py -v`
Expected: PASS — `test_operand_exclusions_matches_reference` green, and `detect_aggregations`/strip-composition behaviour unchanged (the numeric-stub-operand exclusion tests still pass). If a `detect_aggregations` test changes, STOP — investigate.

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/operand-exclusions.rq vocab/ontology/tab.ttl src/iladub/etkl/denormalization.py tests/etkl/test_role_axioms.py
git commit -m "feat(etkl): operand-exclusions.rq — operand-role as SPARQL derivation; retire Python body [B task 4]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Supersession verification + gate

Prove the whole migration: full suite green, the gate covers the new `.rq`, no set-algebra role body remains, source ownership intact.

**Files:**
- Modify: `tests/etkl/test_transform_gate.py` (assert the role `.rq` are gate-covered + `_axis_dimensions` retired)

- [ ] **Step 1: Extend the gate test**

Add to `tests/etkl/test_transform_gate.py`:

```python
def test_role_axiom_queries_present_and_axis_dimensions_retired():
    import glob, os
    rqs = {os.path.basename(p) for p in glob.glob(os.path.join(QUERIES, "*.rq"))}
    assert {"name-levels.rq", "recover-dimensions.rq", "operand-exclusions.rq"} <= rqs
    import iladub.etkl.denormalization as dn
    assert not hasattr(dn, "_axis_dimensions"), "_axis_dimensions (set-algebra role body) must be retired"
```

(The existing `test_no_tuned_constant_in_rq_files` already globs `vocab/queries/*.rq`, so the three new files are automatically gate-checked for tuned constants — confirm by running it.)

- [ ] **Step 2: Run the gate + full suite**

Run: `python3 -m pytest tests/etkl/test_transform_gate.py -v`
Expected: PASS (no tuned constant in the new `.rq`; `_axis_dimensions` gone).

Run: `python3 -m pytest tests/etkl -q`
Expected: PASS — whole etkl suite green over the SPARQL derivation.

Run the source-ownership test: `python3 -m pytest tests/test_source_ownership.py -v` (or its location).
Expected: PASS — the new `.rq` + `tab.ttl` additions reference only owned `tab:` terms as subjects.

Run the full project suite: `python3 -m pytest -q`
Expected: PASS (only pre-existing skips).

- [ ] **Step 3: Commit**

```bash
git add tests/etkl/test_transform_gate.py
git commit -m "test(etkl): gate + supersession verification for the role-derivation axioms [B task 5]

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**1. Spec coverage** (against `2026-07-15-role-derivation-axioms-design.md`):
- §1/§10 both graph-riding role axioms → Tasks 1–4. ✔
- §2 AXIOM derivation (open-world SPARQL), holon-scoped guards, PROCEDURAL reader → Tasks 1–4 + Global Constraints. ✔
- §3 the exact UNPIVOT rule → realized as the proven two-pass (name-levels + recover-dimensions); §3's "level-offset join" is the `namesLevel` mark. ✔
- §4 probe-first → Tasks 1–2 are the probe, promoted from the validated prototype, with the differential oracle. ✔
- §5 components (two `.rq` → now three: name-levels + recover-dimensions + operand-exclusions; `tab:barredAsOperand` + `tab:namesLevel` vocab; reader) → Tasks 1–4. ✔ (The plan refines the spec's single `recover-dimensions.rq` into the proven two-pass `name-levels.rq` + `recover-dimensions.rq`; noted in Architecture.)
- §6 data flow, unchanged consumers, public exports preserved → Task 3. ✔
- §7 behavioural green + per-`.rq` unit tests + differential oracle → all tasks. ✔
- §8 source ownership → Task 5. ✔
- §9 SPARQL-ceiling / value-ordering reconstruction → Global Constraints + Task 3 reader. ✔

**2. Placeholder scan:** Clean — a stray placeholder line in the Task-4 test was removed (assertions are `EX.y in excl`, `EX.n/EX.s not in excl`, flat `== set()`). All `.rq` and reader code is complete and feasibility-proven.

**3. Type consistency:** `recover_dimensions(g,t) -> list[PivotedDimension]` and `_operand_exclusions(g,t) -> set` preserved (Tasks 3–4). `interpret.run(path, *graphs) -> Graph` reused as in loop one. `_read_dimensions(dimgraph, g, t)` and `_ref_axis_dimensions(g, t, axis)` consistent across tasks. `tab:namesLevel` (int) / `tab:barredAsOperand` (bool) used identically in queries and reader.

**Note (spec refinement):** the plan implements the UNPIVOT rule as a **two-pass** CONSTRUCT (`name-levels.rq` → `recover-dimensions.rq`) rather than the spec's single query — a mechanical refinement discovered and validated during the mandated feasibility probe (the single-query form tripped an rdflib nested-`NOT EXISTS`-in-`OPTIONAL` evaluation quirk; the two-pass is proven exact over flat/2-level/3-level, both axes). The spec's design (open-world derivation, holon-scoped guards, consumers unchanged) is unchanged.
