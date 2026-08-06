# Subclass-Only Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the membrane's full RDFS closure with `rdfs:subClassOf`-only materialisation — measured 1.311 s → 0.047 s — proving with a focus-node differential that no shape loses sight of a node, and closing the R19 hazard class at its root.

**Doc impact:** none for this plan file — the loop's `Doc impact: none` is declared in the design spec (`2026-08-06-subclass-only-closure-design.md`).

**Architecture:** `membrane.rdfs_closure` is replaced by `membrane.subclass_closure(data_graph, ont_graph)`, which reads the ontology *only* as a source of `rdfs:subClassOf` axioms (transitively closed once) and materialises supertypes over the data's asserted types. No owlrl, no `inoculate()`, so no ontology nodes and no fabricated literals ever enter the validated graph. The literal-subject filter survives as a cheap invariant guard rather than a workaround. Evidence is a new closure differential (`tests/etkl/test_closure_equiv.py`) asserting verdict **and per-shape focus-node** parity between the old and new closures.

**Tech Stack:** Python 3.11+/pytest, rdflib, pySHACL (reference engine + the old closure, kept for the differential), pyrudof.

**Spec:** `docs/superpowers/specs/2026-08-06-subclass-only-closure-design.md` — read it first, especially §1's measured blast-radius table and §3's evidence design.

## Global Constraints

- **This loop CHANGES BEHAVIOUR deliberately.** Several existing tests pin the *old* behaviour (domain/range typing). Inverting them is the point — but each inversion must be explicit and documented in the test's own docstring, never a quiet deletion. The tests to invert are named in Task 2; do not touch any other test's assertions.
- **The dangerous direction is a shape silently losing sight of a node**, not something starting to fail. That is what the focus-node parity leg exists to catch; a leak fixture whose violation stops being caught is a **hard BLOCKER**, never a test to adjust.
- **Do not edit any file under `vocab/`** — no shape, ontology term, or query changes. Only how the input graph is derived changes.
- **`subclass_closure` is PROCEDURAL engine glue**: a transitive closure over declared axioms. No domain decision, no tuned constant (CLAUDE.md §8).
- **Corpus scores must be byte-identical:** stem **0.9655** / 2152 cells, CBH **0.9047**, apple **0.0105540897**.
- **Broken system git on this machine:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …`.
- **Run every suite in the FOREGROUND** with a generous timeout. Do not background and wait for a notification — it does not reliably fire on this machine. The full suite and the corpus runs are the CONTROLLER's job; implementers run only the covering tests their task names.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (contains a space — quote it).
- **Branch:** `loop-subclass-closure` off `main` (created in Task 1, Step 0).
- Never lower a floor or weaken a pin to force green.

---

### Task 1: `subclass_closure`, alongside the old closure

Add the new function without removing the old one. Keeping both is what makes Task 3's differential possible — it compares the two closures against each other.

**Files:**
- Modify: `src/iladub/etkl/membrane.py` (add `subclass_closure`; leave `rdfs_closure` in place)
- Modify: `tests/etkl/test_membrane.py` (append new tests only; do not touch existing ones yet)

**Interfaces:**
- Consumes: `rdflib` only. Deliberately NOT owlrl, NOT `pyshacl.rdfutil.inoculate`.
- Produces (Tasks 2–3 depend on these exact names): `membrane.subclass_closure(data_graph: Graph, ont_graph: Graph) -> Graph` — a NEW graph, never mutating its inputs.

- [ ] **Step 0: Branch**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git checkout -b loop-subclass-closure main
```

- [ ] **Step 1: Write the failing tests** — append to `tests/etkl/test_membrane.py`:

```python
# ---------------------------------------------------------------- subclass-only closure

def test_subclass_closure_materializes_supertypes():
    """The half the shapes actually use: sh:targetClass tab:Cell must still see an
    explicitly-typed tab:EntryCell (tab:EntryCell rdfs:subClassOf tab:Cell in tab.ttl)."""
    from iladub.etkl import membrane
    g = Graph()
    ec = URIRef("urn:s:ec")
    g.add((ec, RDF.type, TAB.EntryCell))
    out = membrane.subclass_closure(g, _ont())
    assert (ec, RDF.type, TAB.Cell) in out, "subclass closure missing"


def test_subclass_closure_is_transitive():
    """A -> B -> C must yield C, not just B."""
    from rdflib.namespace import RDFS
    from iladub.etkl import membrane
    ont = Graph()
    a, b, c = URIRef("urn:s:A"), URIRef("urn:s:B"), URIRef("urn:s:C")
    ont.add((a, RDFS.subClassOf, b))
    ont.add((b, RDFS.subClassOf, c))
    data = Graph()
    node = URIRef("urn:s:n")
    data.add((node, RDF.type, a))
    out = membrane.subclass_closure(data, ont)
    assert (node, RDF.type, b) in out and (node, RDF.type, c) in out


def test_subclass_closure_drops_domain_typing():
    """THE BEHAVIOUR CHANGE, pinned positively. A node carrying tab:hasBBox must NOT become
    a tab:Cell — that inference is the R19 accident (a ROUND_TRIP_FAIL candidate with a bbox
    typed as a Cell and tripped WrappedCellShape). Dropping it closes R19 at its root."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:s:n"), URIRef("urn:s:bb")
    g.add((node, TAB.hasBBox, bb))      # rdfs:domain tab:Cell in tab.ttl
    g.add((bb, RDF.type, TAB.BBox))
    out = membrane.subclass_closure(g, _ont())
    assert (node, RDF.type, TAB.Cell) not in out, "domain typing survived — R19 still open"


def test_subclass_closure_drops_range_typing():
    """The other half of the same change, and the reason R58 mandates an sh:class case:
    tab:hasBBox rdfs:range tab:BBox must no longer type its object, which is what makes
    sh:class tab:BBox falsifiable again."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:s:n2"), URIRef("urn:s:bb2")
    g.add((node, TAB.hasBBox, bb))      # bb NOT explicitly typed
    out = membrane.subclass_closure(g, _ont())
    assert (bb, RDF.type, TAB.BBox) not in out, "range typing survived — sh:class stays unfalsifiable"


def test_subclass_closure_injects_no_ontology_triples():
    """The ontology is READ for its axioms, never mixed into the validated graph. So the
    graph rudof sees is data plus its own type closure — nothing else — and no ontology node
    can ever become a focus node."""
    from rdflib.namespace import RDFS
    from iladub.etkl import membrane
    ont = Graph()
    sub, sup = URIRef("urn:o:Sub"), URIRef("urn:o:Super")
    ont.add((sub, RDFS.subClassOf, sup))
    ont.add((URIRef("urn:o:thing"), URIRef("urn:o:randomPredicate"), Literal("x")))
    data = Graph()
    d = URIRef("urn:s:d")
    data.add((d, RDF.type, sub))
    out = membrane.subclass_closure(data, ont)
    assert (d, RDF.type, sup) in out, "the axiom's effect is missing"
    assert (sub, RDFS.subClassOf, sup) not in out, "a subClassOf axiom leaked into the data graph"
    assert (URIRef("urn:o:thing"), URIRef("urn:o:randomPredicate"), Literal("x")) not in out


def test_subclass_closure_does_not_mutate_its_input():
    from iladub.etkl import membrane
    g = Graph()
    g.add((URIRef("urn:s:x"), RDF.type, TAB.EntryCell))
    before = len(g)
    membrane.subclass_closure(g, _ont())
    assert len(g) == before, "subclass_closure must return a NEW graph"


def test_subclass_closure_drops_literal_subject_triples():
    """The filter survives as an INVARIANT GUARD, not a workaround: nothing in this closure
    can produce a literal-subject triple, so this pins that property rather than repairing
    owlrl's output. Built by injecting one directly, since no code path emits one."""
    from rdflib.namespace import XSD
    from iladub.etkl import membrane
    g = Graph()
    g.add((URIRef("urn:s:c"), RDF.type, TAB.EntryCell))
    g.add((Literal("307.47", datatype=XSD.decimal), RDF.type, TAB.Cell))   # illegal RDF
    out = membrane.subclass_closure(g, _ont())
    assert [s for s in out.subjects() if isinstance(s, Literal)] == []
```

- [ ] **Step 2: Run — verify they fail**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py -k subclass_closure -v`
Expected: FAIL — `module 'iladub.etkl.membrane' has no attribute 'subclass_closure'`.

- [ ] **Step 3: Implement** — add to `src/iladub/etkl/membrane.py`:

```python
def subclass_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
    """A NEW graph: the data plus its own rdfs:subClassOf type closure. Nothing else.

    The ontology is READ for its `rdfs:subClassOf` axioms and never mixed in, so no ontology
    node can become a focus node and the validated graph is data plus its type closure.

    WHAT THIS DELIBERATELY DOES NOT DO (spec 2026-08-06-subclass-only-closure-design.md):
    domain/range typing. A node no longer becomes a `tab:Cell` merely by carrying
    `tab:hasBBox` — that inference is the R19 accident, and dropping it closes that hazard at
    its root. Measured on the real stem page: the only typings lost are 2,105 vacuous
    `rdfs:Resource`, 207 ontology-node types, and 18 `tab:LabelCell` — and NO shape targets
    `tab:LabelCell`, so no verdict changes. Consequence to know: `sh:class tab:BBox` becomes
    FALSIFIABLE again, because `tab:hasBBox`'s range no longer types its object regardless
    (all 586 bbox objects on the real page are explicitly typed, so nothing relied on it).

    The literal-subject filter is an INVARIANT GUARD here, not a repair: no code path in this
    function can emit a literal-subject triple (unlike owlrl's closure, which emitted 1,533).

    Gate classification (CLAUDE.md §8): PROCEDURAL engine glue — a transitive closure over
    declared axioms. No domain decision, no tuned constant.
    """
    from rdflib import Literal as _Literal
    from rdflib.namespace import RDFS

    supers: dict = {}
    for a, _, b in ont_graph.triples((None, RDFS.subClassOf, None)):
        supers.setdefault(a, set()).add(b)
    changed = True                       # transitive closure over the axioms, computed once
    while changed:
        changed = False
        for a in list(supers):
            for b in list(supers[a]):
                for c in supers.get(b, ()):
                    if c not in supers[a]:
                        supers[a].add(c)
                        changed = True

    out = Graph()
    for s, p, o in data_graph:
        if isinstance(s, _Literal):
            continue
        out.add((s, p, o))
    for s, _, cls in data_graph.triples((None, RDF.type, None)):
        if isinstance(s, _Literal):
            continue
        for c in supers.get(cls, ()):
            out.add((s, RDF.type, c))
    return out
```

`RDF` is already imported at module top for `_conforms_from_report`'s use of rdflib namespaces; if it is not, add `from rdflib import RDF` alongside the existing rdflib imports.

- [ ] **Step 4: Run — verify green**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py -q`
Expected: all PASS — the seven new tests plus every existing one (nothing is wired to the new function yet, so old behaviour is untouched).

- [ ] **Step 5: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/membrane.py tests/etkl/test_membrane.py && git commit -m "feat(loop-subclass): subclass_closure — the ontology read for axioms, never mixed in

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Wire it in, and invert the pins that recorded the old behaviour

**Files:**
- Modify: `src/iladub/etkl/membrane.py` (`_validate_rudof` calls the new closure; `rdfs_closure` docstring gains a status note)
- Modify: `tests/etkl/test_membrane.py` (invert exactly the three named tests)

**Interfaces:**
- Consumes: Task 1's `membrane.subclass_closure`.
- Produces: `_validate_rudof` running on the narrowed closure. `rdfs_closure` REMAINS in the module — Task 3's differential needs it as the reference. Do not delete it.

- [ ] **Step 1: Point `_validate_rudof` at the new closure** — in `src/iladub/etkl/membrane.py`, change the one line

```python
    expanded = rdfs_closure(data_graph, ont_graph)
```

to

```python
    expanded = subclass_closure(data_graph, ont_graph)
```

and update `_validate_rudof`'s docstring: rudof still does no inference of its own; the seam now supplies a **subclass-only** closure (spec 2026-08-06), so domain/range typing is gone by design.

- [ ] **Step 2: Mark `rdfs_closure` as the reference-only survivor** — prepend one paragraph to its docstring:

```
    SUPERSEDED for production (spec 2026-08-06-subclass-only-closure-design.md): the seam now
    calls `subclass_closure`. This function is RETAINED as the reference implementation the
    closure differential (tests/etkl/test_closure_equiv.py) compares against — it is what
    pySHACL's `inference="rdfs"` produces, so it is the baseline any claim of "no verdict
    changed" must be measured against. Not called in production.
```

- [ ] **Step 3: Invert the three pins that recorded the old behaviour.** These tests are correct records of what the membrane did *before* this loop; inverting them IS the behaviour change and must be explicit.

(a) `test_rdfs_closure_materializes_subclass_and_domain_types` — it calls `rdfs_closure`, which is unchanged, so **leave its assertions exactly as they are** and add one sentence to its docstring: this pins the RETAINED reference closure, not production; production now uses `subclass_closure`, whose domain-typing behaviour is pinned by `test_subclass_closure_drops_domain_typing`.

(b) `test_membrane_applies_rdfs_inference` (around line 64) — currently asserts that a node typed `tab:Cell` only via `tab:hasBBox`'s domain still gets validated, i.e. `conforms is False`. Invert it and rename to `test_membrane_no_longer_infers_types_from_property_domains`:

```python
def test_membrane_no_longer_infers_types_from_property_domains():
    """INVERTED by spec 2026-08-06 (was test_membrane_applies_rdfs_inference).

    A node carrying tab:hasBBox but no explicit type is NO LONGER a tab:Cell, so
    WrappedCellShape does not fire on it. That inference was the R19 accident — a
    ROUND_TRIP_FAIL candidate carrying a bbox typed as a Cell and crashing the compile — and
    dropping it closes R19 at its root. The graph below carries no OTHER violation, so it now
    conforms."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:m:inf"), URIRef("urn:m:infbb")
    g.add((node, TAB.hasBBox, bb))          # no explicit rdf:type
    g.add((bb, RDF.type, TAB.BBox))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is True, report
```

(c) `test_rudof_engine_sees_inferred_types` (around line 203) — same inversion on the rudof path. Rename to `test_rudof_engine_does_not_see_domain_inferred_types`, keep the `needs_rudof` marker, and assert `_validate_rudof(...)` returns `True` for the same graph, with a docstring saying it is the rudof-path twin of (b).

**If either inverted test does NOT conform** (i.e. the graph still fails for some other reason), do not force it: capture the report, report it, and stop — an unexpected violation means the closure changed something the spec did not predict.

- [ ] **Step 4: Run the covering tests**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py tests/etkl/test_physical_gate.py tests/etkl/test_row_groups.py tests/etkl/test_unit_marker.py -q`
Expected: all PASS. `test_row_groups.py` is included deliberately — it is the suite that exposed the last closure defect.

- [ ] **Step 5: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/membrane.py tests/etkl/test_membrane.py && git commit -m "feat(loop-subclass): the seam validates on subclass-only closure; R19's typing accident is gone

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: The closure differential (the deliverable)

**Files:**
- Create: `tests/etkl/test_closure_equiv.py`

**Interfaces:**
- Consumes: `membrane.rdfs_closure` (reference), `membrane.subclass_closure` (new), `membrane._validate_pyshacl`, `membrane._validate_rudof`; the 11 committed `tests/tab-*-leak.ttl` fixtures; `compile_tables`.
- Produces: nothing downstream; this is the evidence Task 4 measures against.

- [ ] **Step 1: Write the battery** — create `tests/etkl/test_closure_equiv.py`:

```python
"""Closure differential: full RDFS closure vs subclass-only (spec 2026-08-06 §3).

THE POINT: this loop changes behaviour, and the danger is NOT that something starts failing
— it is that a shape silently stops SEEING a node, so a violation goes uncaught. Verdict
parity alone would miss that. So the load-bearing leg compares FOCUS-NODE SETS per shape."""
import glob
import os
import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, SH

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES_DIR = os.path.join(ROOT, "vocab", "shapes")
ONT_DIR = os.path.join(ROOT, "vocab", "ontology")
TESTS = os.path.join(ROOT, "tests")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES_DIR, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES_DIR, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _ont():
    return Graph().parse(os.path.join(ONT_DIR, "tab.ttl"), format="turtle")


def _verdict_and_focus(expanded, shapes):
    """(conforms, {focus-node IRIs}) for an ALREADY-EXPANDED graph, via pySHACL with
    inference off — the expansion under test is the variable, so the engine must add none."""
    from pyshacl import validate
    conforms, results, _ = validate(expanded, shacl_graph=shapes, inference="none",
                                    advanced=True)
    focus = {n for n in results.objects(None, SH.focusNode) if isinstance(n, URIRef)}
    return bool(conforms), focus


def _both_closures(data):
    from iladub.etkl import membrane
    shapes, ont = _shapes(), _ont()
    full = membrane.rdfs_closure(data, ont)
    sub = membrane.subclass_closure(data, ont)
    return _verdict_and_focus(full, shapes), _verdict_and_focus(sub, shapes)


# ---------- leg 1: the committed leak fixtures — verdict AND focus-node parity ----------

LEAKS = sorted(glob.glob(os.path.join(TESTS, "tab-*-leak.ttl")))


def test_leak_battery_is_not_empty():
    assert len(LEAKS) >= 10, f"expected the committed leak fixtures, found {len(LEAKS)}"


@pytest.mark.parametrize("path", LEAKS, ids=[os.path.basename(p) for p in LEAKS])
def test_both_closures_agree_on_every_committed_leak(path):
    name = os.path.basename(path)
    data = Graph().parse(path, format="turtle")
    (full_ok, full_focus), (sub_ok, sub_focus) = _both_closures(data)
    assert full_ok is False, f"fixture precondition: the reference closure must refuse {name}"
    assert sub_ok is False, (
        f"REGRESSION: subclass-only closure ADMITS {name}, which full closure refuses — "
        f"a shape lost sight of its focus node")
    assert full_focus == sub_focus, (
        f"focus-node divergence on {name}: only-full={sorted(full_focus - sub_focus)} "
        f"only-sub={sorted(sub_focus - full_focus)}")


# ---------- leg 2: a real compiled page — verdict AND focus-node parity ----------

STEM = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-stem-2026-07-31.pdf")


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_both_closures_agree_on_a_real_page_graph():
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    (full_ok, full_focus), (sub_ok, sub_focus) = _both_closures(rep.graph)
    assert full_ok == sub_ok is True, f"full={full_ok} sub={sub_ok} on the real stem page"
    assert full_focus == sub_focus, (
        f"focus-node divergence on the real page: "
        f"only-full={sorted(full_focus - sub_focus)[:5]} "
        f"only-sub={sorted(sub_focus - full_focus)[:5]}")


# ---------- leg 3: R58's mandated sh:class falsifiability case ----------

needs_rudof = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


def _bad_bbox_graph():
    """An EntryCell whose tab:hasBBox points at something that is NOT a tab:BBox. Under FULL
    closure this conforms, because tab:hasBBox's rdfs:range types the object regardless —
    which is what made sh:class unfalsifiable. Under subclass-only it must be refused."""
    g = Graph()
    cell, notbb = URIRef("urn:k:cell"), URIRef("urn:k:notabbox")
    g.add((cell, RDF.type, TAB.EntryCell))
    g.add((cell, TAB.cellText, Literal("x")))
    g.add((cell, TAB.onPage, Literal(0)))
    g.add((cell, TAB.hasBBox, notbb))
    g.add((notbb, RDF.type, TAB.LeafRow))     # deliberately the wrong class
    return g


def test_sh_class_was_unfalsifiable_under_full_closure():
    """The premise R58 states, pinned so the next leg means something."""
    from iladub.etkl import membrane
    full = membrane.rdfs_closure(_bad_bbox_graph(), _ont())
    assert (URIRef("urn:k:notabbox"), RDF.type, TAB.BBox) in full, \
        "range typing did NOT fire — R58's premise is wrong, investigate before proceeding"


def test_sh_class_is_falsifiable_under_subclass_closure():
    from iladub.etkl import membrane
    sub = membrane.subclass_closure(_bad_bbox_graph(), _ont())
    assert (URIRef("urn:k:notabbox"), RDF.type, TAB.BBox) not in sub
    conforms, _ = _verdict_and_focus(sub, _shapes())
    assert conforms is False, "sh:class tab:BBox still unfalsifiable under the new closure"


@needs_rudof
def test_rudof_implements_sh_class_once_range_typing_is_gone():
    """R58's addendum: prove the NEW ENGINE actually implements sh:ClassConstraintComponent,
    now that the range-typing fallback no longer hides it."""
    from iladub.etkl import membrane
    ok, report = membrane._validate_rudof(_bad_bbox_graph(), _shapes(), _ont())
    assert ok is False, "rudof admitted a wrong-class hasBBox — sh:class unimplemented?"
```

- [ ] **Step 2: Run the battery**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_closure_equiv.py -v`
Expected: all PASS.

**Failure protocols, both binding:**
- A **focus-node divergence** or a leak fixture that subclass-only ADMITS is a hard BLOCKER. Do not weaken the assertion. Report which fixture, which shape, and the two focus-node sets — it means the spec's blast-radius measurement was incomplete, which is a plan-level finding.
- If `test_sh_class_was_unfalsifiable_under_full_closure` fails, R58's stated premise is wrong. Stop and report; the rest of leg 3 is meaningless without it.

- [ ] **Step 3: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add tests/etkl/test_closure_equiv.py && git commit -m "test(loop-subclass): closure differential — verdict AND per-shape focus-node parity

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: Measure and close

**Files:**
- Modify: `docs/superpowers/specs/2026-08-06-subclass-only-closure-design.md` (status + measured numbers)
- Modify: `docs/superpowers/residues.md` (close R58; note R19's root closure; add the successor row)

**Note for the controller:** Steps 1–4 are measurements. Per this loop's policy the long runs (corpus, whole document, full suite) are the controller's to run in the foreground; the implementer does Steps 5–6 with the numbers handed to it.

- [ ] **Step 1: Page-0 baseline**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl import compile_tables, membrane
print("engine:", membrane.engine_name())
t0 = time.monotonic()
rep = compile_tables("corpus/ag-trade/graincorp-stem-2026-07-31.pdf", page_number=0)
print(f"page-0: {time.monotonic()-t0:.1f}s  score={rep.score:.4f}   [pre-loop 12.5s / 0.9560]")
EOF
```
Expected: score **0.9560** unchanged; wall below 12.5 s. Record the real number.

- [ ] **Step 2: Corpus byte-identity gate**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q
```
Expected: 13 passed (stem 0.9655 / 2152, CBH 0.9047). Then apple:

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -c "
from iladub.etkl.document import compile_document
r = compile_document('corpus/financial/apple-fy2026q3-statements.pdf')
print(f'apple {r.score:.10f}  [expect 0.0105540897]')"
```

If any score moves, STOP and report BLOCKED — a moved score means the closure changed a real verdict, which outranks the speedup.

- [ ] **Step 3: Whole-document measurement (the number R58's successor row is judged against)**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl.document import compile_document
t0 = time.monotonic()
rep = compile_document("corpus/ag-trade/graincorp-stem-2026-07-31.pdf")
print(f"stem document: {time.monotonic()-t0:.0f}s  score={rep.score:.4f}   [pre-loop 166s / 0.9655]")
EOF
```

- [ ] **Step 4: Both batteries + full suite**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_closure_equiv.py tests/etkl/test_membrane_equiv.py -q
```
Expected: both green (the engine differential must survive the closure change). Then the full suite:

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -q 2>&1 | tail -6
```
Expected: 0 failed except the known machine-environmental `tests/test_release_gate.py::test_since_date_fallback_and_previous_tag`. Anything else red must be diagnosed regression-vs-pre-existing and reported.

- [ ] **Step 5: Spec status + register**

Set the spec's `**Status:**` to `closed 2026-08-06` with the measured page, document, and closure numbers. Then in `docs/superpowers/residues.md`, in the house format (what / measured / why deferred / what would close it):

- **Close R58** — strike it (`| ~~R58~~ | **CLOSED (loop-subclass, 2026-08-06)** — …`) recording: closure 1.311 s → measured value; the membrane's new dominant cost is rudof's n-triples parse; the measured blast radius (2,105 vacuous `rdfs:Resource` + 207 ontology-node types + 18 `tab:LabelCell`, none targeted by any shape); and that R58's mandated `sh:class` case shipped as `test_rudof_implements_sh_class_once_range_typing_is_gone`.
- **Note R19's root closure** — R19 is already struck (closed by the unit-marker loop's gate extension). Append one clause to its row: the hazard's *mechanism* — a node typing as `tab:Cell` merely by carrying `tab:hasBBox` — is now gone at the root, since the membrane no longer materialises domain typing (pinned by `test_subclass_closure_drops_domain_typing`).
- **Add the successor row** — rudof's n-triples parse (~0.58 s on an 8k-triple page) is now the membrane's dominant cost, with the measured post-loop split. Why deferred: it is a Python↔Rust boundary cost, not a semantic one, and closing it means either a smaller payload or an in-process binding, neither of which this loop scoped. What would close it: measure whether rudof parses Turtle faster than N-Triples on our payloads (Turtle is ~3× smaller), or whether a future pyrudof exposes a graph-passing API that avoids serialization entirely.

- [ ] **Step 6: Lints + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add docs/superpowers/specs/2026-08-06-subclass-only-closure-design.md docs/superpowers/residues.md && git commit -m "docs(loop-subclass): close — measured, R58 closed, R19 closed at its root

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 7: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-06)

- **Spec coverage:** §1 measured blast radius → Task 1's docstring + Task 4's register row; §2 the change (no owlrl, no inoculate) → Task 1 Steps 1/3 + Task 2 Step 1; §2 literal filter as invariant guard → `test_subclass_closure_drops_literal_subject_triples`; §3 leg 1 verdict parity + leg 2 focus-node parity → Task 3 legs 1–2; §3 leg 3 R58's `sh:class` case → Task 3 leg 3 (three tests, including the premise pin); §4 success criteria → Task 4 Steps 1–4; §5 out-of-scope → Task 4 Step 5's successor row.
- **Placeholder scan:** none. The two failure protocols state the binding action rather than deferring a decision.
- **Type consistency:** `subclass_closure(data_graph, ont_graph) -> Graph` (Task 1) consumed in Tasks 2–3; `rdfs_closure` retained by name for Task 3's reference leg; `_validate_pyshacl`/`_validate_rudof`/`membrane.validate` used with their existing signatures throughout.
- **One risk I checked rather than assumed:** Task 3's `_verdict_and_focus` runs pySHACL with `inference="none"` so the closure under test is the only variable — otherwise pySHACL would re-add the very typing this loop removes and both legs would trivially agree.
