# Membrane Engine Swap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put both SHACL call sites behind one `membrane.py` seam and run them on rudof (Rust), preserving today's inference semantics exactly, with a differential + mutation battery as the correctness gate.

**Doc impact:** none for this plan file — the loop's `Doc impact: increment` is declared in the design spec (`2026-08-06-membrane-engine-swap-design.md`).

**Architecture:** A new module `src/iladub/etkl/membrane.py` becomes the only place SHACL runs. Its pipeline is: owlrl full RDFS closure (today's semantics, unchanged) → drop literal-subject triples (owlrl emits 1,533 illegal ones that rudof's strict parser refuses) → serialize n-triples → a module-level persistent `pyrudof.Rudof` instance with shapes parsed once → `(conforms, report)`. The two existing call sites (`tiling.region_tiles`, `compile._validate`) keep their distinct shape sets and simply call the seam. pySHACL stays importable behind `ILADUB_MEMBRANE=pyshacl` as an escape hatch and as the battery's reference engine.

**Tech Stack:** Python 3.11+/pytest, rdflib, owlrl, pySHACL (reference + fallback), pyrudof (Rust SHACL, new optional dependency).

**Spec:** `docs/superpowers/specs/2026-08-06-membrane-engine-swap-design.md` — read it first, especially §2 (what was verified about rudof) and §3.3 (the battery is the deliverable).

## Global Constraints

- **The battery is the deliverable, not the speedup.** A membrane that silently stops catching violations is the worst possible regression (§7 credibility). Agreement on healthy graphs proves nothing — a validator that did nothing would also agree. The mutation leg is the real evidence.
- **Preserve inference semantics byte-for-byte:** owlrl full RDFS closure, exactly as `inference="rdfs"` does today. The subclass-only change is a SEPARATE loop (spec §7) — do not smuggle it in.
- **Do not edit any shape, ontology term, or `.rq` file.** Only the engine evaluating them changes.
- **Do not change the two call sites' shape sets.** The gate keeps its thirteen (`_TILING_SHAPE_IRIS` + `_PHYSICAL_SHAPE_IRIS`), the final pass keeps all twenty-four. The redundancy between them is registered, not fixed (spec §6).
- **Corpus scores must be byte-identical:** stem **0.9655** / 2152 cells, CBH **0.9047**, apple **0.0105540897**. Scores derive from conformance decisions, so any divergence surfaces there.
- **Broken system git on this machine:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …` (applies to subagents).
- **Run long suites in the FOREGROUND** with a 600000 ms timeout. Do not background them and wait for a notification — it does not reliably fire on this machine.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (contains a space — quote it).
- **Branch:** `loop-membrane-engine` off `main` (created in Task 1, Step 0).
- Never lower a floor or weaken a pin to force green.

---

### Task 1: The seam, with pySHACL only (no behaviour change)

Establish `membrane.py` and route both call sites through it while still running pySHACL. This isolates "did the refactor change anything?" from "did the engine change anything?" — if a later task's battery fails, this task's green suite proves the seam was not the cause.

**Files:**
- Create: `src/iladub/etkl/membrane.py`
- Modify: `src/iladub/etkl/tiling.py` (`region_tiles`)
- Modify: `src/iladub/etkl/compile.py` (`_validate`)
- Create: `tests/etkl/test_membrane.py`

**Interfaces:**
- Consumes: `pyshacl.validate`; `tiling._TILING_SHAPES` (cached shapes graph), `tiling._ONT`; `compile._repo_vocab()`, `compile._FULL_SHAPES`/`_FULL_ONT` globals.
- Produces (later tasks depend on these exact names): `membrane.validate(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]`; `membrane.engine_name() -> str` (returns `"pyshacl"` or `"rudof"`).

- [ ] **Step 0: Branch**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git checkout -b loop-membrane-engine main
```

- [ ] **Step 1: Write the failing test** — create `tests/etkl/test_membrane.py`:

```python
"""The membrane seam: one place any SHACL runs (spec 2026-08-06-membrane-engine-swap-design.md).

Task 1 establishes the seam over pySHACL with NO behaviour change; later tasks swap the
engine underneath it. The point of the seam is that `tiling.region_tiles` and
`compile._validate` stop constructing their own pyshacl.validate calls."""
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES = os.path.join(ROOT, "vocab", "shapes")
ONT = os.path.join(ROOT, "vocab", "ontology")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _ont():
    return Graph().parse(os.path.join(ONT, "tab.ttl"), format="turtle")


def test_membrane_reports_conformance_on_a_clean_graph():
    from iladub.etkl import membrane
    g = Graph()
    cell = URIRef("urn:m:cell")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("Americas")))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is True, report
    assert isinstance(report, str)


def test_membrane_catches_a_core_violation():
    # UnitMarkerShape: a tab:UnitMarker needs >=1 tab:markerRegion.
    from iladub.etkl import membrane
    g = Graph()
    um = URIRef("urn:m:um")
    g.add((um, RDF.type, TAB.UnitMarker))
    g.add((um, TAB.markerSymbol, Literal("$")))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False
    assert "markerRegion" in report or "UnitMarkerShape" in report


def test_membrane_catches_a_sparql_constraint_violation():
    # WrappedCellShape (sh:sparql): a bbox-carrying tab:Cell needs non-empty cellText.
    from iladub.etkl import membrane
    g = Graph()
    cell, bb = URIRef("urn:m:c"), URIRef("urn:m:bb")
    g.add((cell, RDF.type, TAB.Cell))
    g.add((cell, TAB.cellText, Literal("")))
    g.add((bb, RDF.type, TAB.BBox))
    g.add((cell, TAB.hasBBox, bb))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False
    assert "cellText" in report or "WrappedCellShape" in report


def test_membrane_applies_rdfs_inference():
    """The R19 mechanism: a node typed tab:Cell ONLY via tab:hasBBox's rdfs:domain must
    still be validated. This pins that the seam preserves inference="rdfs" semantics."""
    from iladub.etkl import membrane
    g = Graph()
    node, bb = URIRef("urn:m:inf"), URIRef("urn:m:infbb")
    g.add((node, TAB.hasBBox, bb))          # NO explicit rdf:type
    g.add((bb, RDF.type, TAB.BBox))
    conforms, report = membrane.validate(g, _shapes(), _ont())
    assert conforms is False, "inference must type the node as tab:Cell and fire WrappedCellShape"


def test_engine_name_is_reported():
    from iladub.etkl import membrane
    assert membrane.engine_name() in ("pyshacl", "rudof")


def test_call_sites_use_the_seam():
    """Structural pin: neither call site may construct its own pyshacl.validate."""
    import inspect
    from iladub.etkl import tiling
    import iladub.etkl.compile as C
    assert "membrane" in inspect.getsource(tiling.region_tiles)
    assert "membrane" in inspect.getsource(C._validate)
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py -v`
Expected: FAIL with `ImportError: cannot import name 'membrane'`.

- [ ] **Step 3: Write `src/iladub/etkl/membrane.py`**

```python
"""membrane — the ONE place any SHACL validation runs (spec 2026-08-06).

Both closed-world membranes (tiling.region_tiles' per-region gate and compile._validate's
whole-graph pass) call this seam. They keep their DISTINCT shape sets — that distinction is
semantic (intra-region vs whole-graph) and is not this module's business.

Gate classification (CLAUDE.md §8): PROCEDURAL engine glue only. No decision lives here —
the decisions are the SHACL shapes. Irreducible: a validator must be invoked from somewhere,
and the invocation carries no domain decision.
"""
from __future__ import annotations

import os

from rdflib import Graph


def engine_name() -> str:
    """The engine this process validates with. `ILADUB_MEMBRANE` selects it."""
    return os.environ.get("ILADUB_MEMBRANE", "pyshacl")


def validate(data_graph: Graph, shapes_graph: Graph, ont_graph: Graph) -> tuple[bool, str]:
    """(conforms, report_text) for `data_graph` against `shapes_graph`.

    Semantics are exactly today's: RDFS inference over data + ontology, SHACL advanced
    features on. Callers must not depend on the report's exact wording — it differs by
    engine; only its content (shape names, focus nodes) is stable.
    """
    return _validate_pyshacl(data_graph, shapes_graph, ont_graph)


def _validate_pyshacl(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    from pyshacl import validate as _v
    conforms, _, text = _v(data_graph, shacl_graph=shapes_graph, ont_graph=ont_graph,
                           inference="rdfs", advanced=True)
    return bool(conforms), text
```

- [ ] **Step 4: Route `tiling.region_tiles` through the seam** — in `src/iladub/etkl/tiling.py`, replace the body of `region_tiles` (currently importing and calling `pyshacl.validate` directly) with:

```python
    from . import membrane
    conforms, _ = membrane.validate(graph, _TILING_SHAPES, _ONT)
    return conforms
```

Leave the docstring and `_TILING_SHAPE_IRIS`/`_PHYSICAL_SHAPE_IRIS`/`_build_tiling_shapes` untouched.

- [ ] **Step 5: Route `compile._validate` through the seam** — in `src/iladub/etkl/compile.py`, keep the `_FULL_SHAPES`/`_FULL_ONT` lazy-load block exactly as it is and replace only the `validate(...)` call with:

```python
    from . import membrane
    return membrane.validate(graph, _FULL_SHAPES, _FULL_ONT)
```

- [ ] **Step 6: Run the seam tests + the near suite**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py tests/test_tab.py tests/etkl/test_physical_gate.py tests/etkl/test_unit_marker.py -q`
Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/membrane.py src/iladub/etkl/tiling.py src/iladub/etkl/compile.py tests/etkl/test_membrane.py && git commit -m "refactor(loop-membrane): one seam for SHACL — both call sites route through membrane.validate

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: RDFS closure + the literal-subject filter, as a pure function

**Files:**
- Modify: `src/iladub/etkl/membrane.py` (add `rdfs_closure`)
- Modify: `tests/etkl/test_membrane.py` (append)
- Modify: `pyproject.toml` (add `owlrl` to the `etkl` extra)

**Interfaces:**
- Consumes: Task 1's `membrane.validate`.
- Produces: `membrane.rdfs_closure(data_graph: Graph, ont_graph: Graph) -> Graph` — a NEW graph, RDFS-expanded, with every literal-subject triple removed. Task 3 feeds its output to rudof. The successor loop (spec §7) replaces exactly this function.

- [ ] **Step 1: Write the failing test** — append to `tests/etkl/test_membrane.py`:

```python
# ---------------------------------------------------------------- closure

def test_rdfs_closure_materializes_subclass_and_domain_types():
    """Closure must reproduce what inference='rdfs' gives pySHACL today: subclass closure
    (EntryCell -> Cell, which sh:targetClass needs) AND domain typing (the R19 mechanism)."""
    from iladub.etkl import membrane
    g = Graph()
    ec, node, bb = URIRef("urn:c:ec"), URIRef("urn:c:n"), URIRef("urn:c:bb")
    g.add((ec, RDF.type, TAB.EntryCell))     # subclass of tab:Cell in tab.ttl
    g.add((node, TAB.hasBBox, bb))           # rdfs:domain tab:Cell
    out = membrane.rdfs_closure(g, _ont())
    assert (ec, RDF.type, TAB.Cell) in out, "subclass closure missing"
    assert (node, RDF.type, TAB.Cell) in out, "domain typing missing (R19 mechanism)"


def test_rdfs_closure_drops_literal_subject_triples():
    """owlrl emits `"307.47"^^xsd:decimal rdf:type rdfs:Resource` — illegal RDF that rdflib
    tolerates and a strict parser refuses. The closure must remove every such triple."""
    from iladub.etkl import membrane
    from rdflib.namespace import XSD
    g = Graph()
    c = URIRef("urn:c:cell")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.x0, Literal("307.47", datatype=XSD.decimal)))
    out = membrane.rdfs_closure(g, _ont())
    bad = [s for s in out.subjects() if isinstance(s, Literal)]
    assert bad == [], f"literal-subject triples survived: {bad[:3]}"


def test_rdfs_closure_does_not_mutate_its_input():
    from iladub.etkl import membrane
    g = Graph()
    g.add((URIRef("urn:c:x"), RDF.type, TAB.EntryCell))
    before = len(g)
    membrane.rdfs_closure(g, _ont())
    assert len(g) == before, "rdfs_closure must return a NEW graph"
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py -k closure -v`
Expected: FAIL — `module 'iladub.etkl.membrane' has no attribute 'rdfs_closure'`.

- [ ] **Step 3: Implement** — add to `src/iladub/etkl/membrane.py`:

```python
def rdfs_closure(data_graph: Graph, ont_graph: Graph) -> Graph:
    """A NEW graph: data + ontology, RDFS-expanded, minus every literal-subject triple.

    Reproduces exactly what pySHACL's `inference="rdfs"` does today — subclass closure AND
    domain/range typing (the latter is the R19 mechanism, deliberately preserved here; the
    successor loop, spec 2026-08-06 §7, is where dropping it is argued and measured).

    The literal-subject filter is NOT optional: owlrl's closure emits triples whose subject
    is a Literal (`"307.47"^^xsd:decimal rdf:type rdfs:Resource`), which is illegal RDF.
    rdflib tolerates them; a strict parser rejects the whole graph. They are semantically
    vacuous, so dropping them changes no verdict.
    """
    from rdflib import Literal as _Literal
    import owlrl
    merged = Graph()
    merged += data_graph
    merged += ont_graph
    owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(merged)
    out = Graph()
    for s, p, o in merged:
        if isinstance(s, _Literal):
            continue
        out.add((s, p, o))
    return out
```

- [ ] **Step 4: Declare the dependency** — in `pyproject.toml`, add `"owlrl>=6.0",` to the `etkl` optional-dependency list (it is currently an implicit transitive dependency of pySHACL; the seam now imports it directly).

- [ ] **Step 5: Run — verify green**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py -q`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/membrane.py tests/etkl/test_membrane.py pyproject.toml && git commit -m "feat(loop-membrane): rdfs_closure — today's inference semantics + the literal-subject filter

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: The rudof engine behind the seam

**Files:**
- Modify: `src/iladub/etkl/membrane.py` (add `_validate_rudof`, engine dispatch)
- Modify: `tests/etkl/test_membrane.py` (append)
- Modify: `pyproject.toml` (new `rudof` optional-dependency extra)

**Interfaces:**
- Consumes: Task 2's `membrane.rdfs_closure`; Task 1's `validate`/`engine_name`.
- Produces: `membrane.validate` dispatching on `engine_name()`; `membrane.rudof_available() -> bool`. Task 4's battery calls `_validate_pyshacl` and `_validate_rudof` directly, by those exact names.

Verified API facts (measured 2026-08-06, use verbatim): `pyrudof.Rudof(pyrudof.RudofConfig())`; `r.read_shacl(text, format=pyrudof.ShaclFormat.Turtle)`; `r.reset_data()`; `r.read_data(text, format=pyrudof.RDFFormat.NTriples)`; `r.validate_shacl(mode=pyrudof.ShaclValidationMode.Native)` — the return value is **not** a usable object (`type=NoneType`); read the report via `r.serialize_shacl_validation_results(pyrudof.ResultShaclValidationFormat.Turtle)`, whose text contains `sh:conforms true|false` and one `sh:ValidationResult` block per violation.

- [ ] **Step 1: Write the failing test** — append to `tests/etkl/test_membrane.py`:

```python
# ---------------------------------------------------------------- rudof engine

import pytest

needs_rudof = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


@needs_rudof
def test_rudof_engine_agrees_on_a_clean_graph():
    from iladub.etkl import membrane
    g = Graph()
    c = URIRef("urn:r:c")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.cellText, Literal("Americas")))
    ok_p, _ = membrane._validate_pyshacl(g, _shapes(), _ont())
    ok_r, _ = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_p == ok_r is True


@needs_rudof
def test_rudof_engine_catches_a_sparql_constraint_violation():
    from iladub.etkl import membrane
    g = Graph()
    c, bb = URIRef("urn:r:c2"), URIRef("urn:r:bb2")
    g.add((c, RDF.type, TAB.Cell))
    g.add((c, TAB.cellText, Literal("")))
    g.add((bb, RDF.type, TAB.BBox))
    g.add((c, TAB.hasBBox, bb))
    ok_r, report = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_r is False
    assert "cellText" in report or "WrappedCellShape" in report


@needs_rudof
def test_rudof_engine_sees_inferred_types():
    """rudof does NO inference of its own — this passes only because the seam runs
    rdfs_closure first. Pins the R19 mechanism end to end on the new engine."""
    from iladub.etkl import membrane
    g = Graph()
    n, bb = URIRef("urn:r:inf"), URIRef("urn:r:infbb")
    g.add((n, TAB.hasBBox, bb))
    g.add((bb, RDF.type, TAB.BBox))
    ok_r, _ = membrane._validate_rudof(g, _shapes(), _ont())
    assert ok_r is False


@needs_rudof
def test_engine_switch_selects_rudof(monkeypatch):
    from iladub.etkl import membrane
    monkeypatch.setenv("ILADUB_MEMBRANE", "rudof")
    assert membrane.engine_name() == "rudof"
    monkeypatch.setenv("ILADUB_MEMBRANE", "pyshacl")
    assert membrane.engine_name() == "pyshacl"
```

- [ ] **Step 2: Install the dependency and run — verify it fails**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pip install pyrudof==0.3.7 && python -m pytest tests/etkl/test_membrane.py -k rudof -v
```
Expected: FAIL — `module 'iladub.etkl.membrane' has no attribute '_validate_rudof'` (not skipped, since pyrudof is now installed).

- [ ] **Step 3: Implement** — add to `src/iladub/etkl/membrane.py`:

```python
_RUDOF = None          # persistent instance: shapes parse ONCE (0.02 s), data resets per call


def rudof_available() -> bool:
    import importlib.util
    return importlib.util.find_spec("pyrudof") is not None


def _rudof_instance(shapes_graph):
    """One instance per process, keyed by the shapes graph's identity — the two call sites
    use DIFFERENT shape sets, so a single cached instance would validate against the wrong
    one. Shapes parsing is 0.02 s; data loading (0.58 s on an 8k-triple page) dominates and
    is per-call regardless."""
    global _RUDOF
    import pyrudof
    key = id(shapes_graph)
    if _RUDOF is None or _RUDOF[0] != key:
        r = pyrudof.Rudof(pyrudof.RudofConfig())
        r.read_shacl(shapes_graph.serialize(format="turtle"), format=pyrudof.ShaclFormat.Turtle)
        _RUDOF = (key, r)
    return _RUDOF[1]


def _validate_rudof(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]:
    """rudof does NO inference of its own — rdfs_closure supplies the expanded graph, and
    its literal-subject filter is what makes the payload parseable by rudof's strict reader."""
    import pyrudof
    expanded = rdfs_closure(data_graph, ont_graph)
    r = _rudof_instance(shapes_graph)
    r.reset_data()
    r.read_data(expanded.serialize(format="nt"), format=pyrudof.RDFFormat.NTriples)
    r.validate_shacl(mode=pyrudof.ShaclValidationMode.Native)
    report = str(r.serialize_shacl_validation_results(
        pyrudof.ResultShaclValidationFormat.Turtle))
    conforms = "sh:conforms true" in " ".join(report.split())
    return conforms, report
```

and change `validate` to dispatch:

```python
def validate(data_graph: Graph, shapes_graph: Graph, ont_graph: Graph) -> tuple[bool, str]:
    """(conforms, report_text) for `data_graph` against `shapes_graph`.

    Semantics are exactly today's: RDFS inference over data + ontology, SHACL advanced
    features on. Callers must not depend on the report's exact wording — it differs by
    engine; only its content (shape names, focus nodes) is stable.
    """
    if engine_name() == "rudof" and rudof_available():
        return _validate_rudof(data_graph, shapes_graph, ont_graph)
    return _validate_pyshacl(data_graph, shapes_graph, ont_graph)
```

**Note on the conformance parse:** `sh:conforms true` is read from the serialized report. If the report's turtle renders the boolean as `"true"^^xsd:boolean` rather than bare `true`, adapt the check to match both forms and say so in your report — do NOT invert the default (an unparseable report must never read as "conforms").

- [ ] **Step 4: Declare the dependency** — in `pyproject.toml`, add a new optional-dependency extra:

```toml
rudof = [
    "pyrudof==0.3.7",
]
```

Pin exactly: the spec names 0.3.7's behaviour as verified, and this is a young project.

- [ ] **Step 5: Run — verify green (both engines)**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane.py -q && ILADUB_MEMBRANE=rudof python -m pytest tests/etkl/test_membrane.py tests/etkl/test_physical_gate.py -q
```
Expected: both PASS.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add src/iladub/etkl/membrane.py tests/etkl/test_membrane.py pyproject.toml && git commit -m "feat(loop-membrane): rudof engine behind the seam, selected by ILADUB_MEMBRANE

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: The differential + mutation battery (the deliverable)

**Files:**
- Create: `tests/etkl/test_membrane_equiv.py`

**Interfaces:**
- Consumes: `membrane._validate_pyshacl`, `membrane._validate_rudof`, `membrane.rdfs_closure`; the 11 committed negative fixtures `tests/tab-*-leak.ttl`; `compile_tables` for real graphs.
- Produces: nothing downstream; this is the correctness gate Task 5 measures against.

- [ ] **Step 1: Write the battery** — create `tests/etkl/test_membrane_equiv.py`:

```python
"""Differential battery: pySHACL vs rudof (spec 2026-08-06 §3.3).

THE POINT: agreement on healthy graphs proves almost nothing — a validator that did nothing
would also agree. The mutation leg is the evidence: violations are INJECTED into real
compiled graphs and BOTH engines must catch every one."""
import glob
import os
import random
import pytest
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

TAB = Namespace("https://w3id.org/iladub/tab#")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHAPES_DIR = os.path.join(ROOT, "vocab", "shapes")
ONT_DIR = os.path.join(ROOT, "vocab", "ontology")
TESTS = os.path.join(ROOT, "tests")

pytestmark = pytest.mark.skipif(
    not __import__("importlib").util.find_spec("pyrudof"),
    reason="pyrudof not installed (optional dependency)")


def _shapes():
    g = Graph()
    g.parse(os.path.join(SHAPES_DIR, "tab-shapes.ttl"), format="turtle")
    g.parse(os.path.join(SHAPES_DIR, "tab-physical-shapes.ttl"), format="turtle")
    return g


def _ont():
    return Graph().parse(os.path.join(ONT_DIR, "tab.ttl"), format="turtle")


def _both(g):
    from iladub.etkl import membrane
    s, o = _shapes(), _ont()
    p, _ = membrane._validate_pyshacl(g, s, o)
    r, _ = membrane._validate_rudof(g, s, o)
    return p, r


# ---------- leg 1: NEGATIVE — the committed leak fixtures (both must REFUSE) ----------

LEAKS = sorted(glob.glob(os.path.join(TESTS, "tab-*-leak.ttl")))


@pytest.mark.parametrize("path", LEAKS, ids=[os.path.basename(p) for p in LEAKS])
def test_both_engines_refuse_every_committed_leak(path):
    g = Graph().parse(path, format="turtle")
    p, r = _both(g)
    assert p is False, f"fixture precondition: pySHACL must refuse {os.path.basename(path)}"
    assert r is False, f"rudof ADMITTED a leak pySHACL refuses: {os.path.basename(path)}"


def test_leak_battery_is_not_empty():
    assert len(LEAKS) >= 10, f"expected the committed leak fixtures, found {len(LEAKS)}"


# ---------- leg 2: POSITIVE — a real compiled page graph (both must ADMIT) ----------

STEM = os.path.join(ROOT, "corpus", "ag-trade", "graincorp-stem-2026-07-31.pdf")


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
def test_both_engines_admit_a_real_page_graph():
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    p, r = _both(rep.graph)
    assert p is True and r is True, f"pySHACL={p} rudof={r} on the real stem page"


# ---------- leg 3: MUTATION — inject violations, BOTH must catch (the real evidence) ----------

def _mutations(g, seed):
    """Yield (name, mutated_graph): each drops or corrupts something a shape requires."""
    rnd = random.Random(seed)
    outs = []

    cells = [s for s in g.subjects(RDF.type, TAB.EntryCell)]
    if cells:
        c = rnd.choice(cells)
        m = Graph(); m += g
        for o in list(m.objects(c, TAB.onPage)):
            m.remove((c, TAB.onPage, o))          # EntryCellPhysicalShape: onPage minCount 1
        outs.append(("drop-onPage", m))

        m2 = Graph(); m2 += g
        for o in list(m2.objects(c, TAB.cellText)):
            m2.remove((c, TAB.cellText, o))
        m2.add((c, TAB.cellText, Literal("")))     # WrappedCellShape (sh:sparql)
        outs.append(("blank-cellText", m2))

        m3 = Graph(); m3 += g
        for o in list(m3.objects(c, TAB.hasBBox)):
            m3.remove((c, TAB.hasBBox, o))         # EntryCellPhysicalShape: hasBBox minCount 1
        outs.append(("drop-bbox", m3))

    m4 = Graph(); m4 += g
    um = URIRef("urn:mut:um")
    m4.add((um, RDF.type, TAB.UnitMarker))
    m4.add((um, TAB.markerSymbol, Literal("$")))   # UnitMarkerShape: markerRegion minCount 1
    outs.append(("orphan-unit-marker", m4))

    return outs


@pytest.mark.skipif(not os.path.exists(STEM), reason="corpus document not fetched")
@pytest.mark.parametrize("seed", [11, 23, 37])
def test_both_engines_catch_every_injected_violation(seed):
    from iladub.etkl import compile_tables
    rep = compile_tables(STEM, page_number=0, validate_shapes=False)
    muts = _mutations(rep.graph, seed)
    assert muts, "mutation generator produced nothing — the graph shape changed"
    for name, m in muts:
        p, r = _both(m)
        assert p is False, f"[{name}] fixture precondition: pySHACL must catch it"
        assert r is False, f"[{name}] rudof MISSED a violation pySHACL catches"
```

- [ ] **Step 2: Run the battery**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_membrane_equiv.py -v`
Expected: all PASS.

**If a leak fixture or a mutation shows `pySHACL=False, rudof=True`** — that is rudof MISSING a violation, the dangerous direction, and it is a genuine blocker. Do NOT weaken the assertion. Capture which shape and which fixture, and report BLOCKED to the controller: it decides whether the loop proceeds with a narrowed engine scope or stops.

**If `test_both_engines_admit_a_real_page_graph` fails with rudof=False** — rudof is refusing a graph pySHACL admits (spurious violation). Capture the full rudof report (which shape, which focus node) and report it; this is diagnosable and usually a shape-feature gap, but it must not be papered over.

- [ ] **Step 3: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add tests/etkl/test_membrane_equiv.py && git commit -m "test(loop-membrane): differential + mutation battery — both engines must catch every injected violation

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: Flip the default, measure, close

**Files:**
- Modify: `src/iladub/etkl/membrane.py` (`engine_name` default)
- Modify: `docs/superpowers/specs/2026-08-06-membrane-engine-swap-design.md` (status + measured numbers)
- Modify: `docs/superpowers/residues.md` (register the deferred items)

- [ ] **Step 1: Flip the default** — in `membrane.engine_name`, change the default so rudof is preferred when available:

```python
def engine_name() -> str:
    """The engine this process validates with.

    rudof (Rust) is preferred where installed; pySHACL is the fallback AND the escape hatch:
    `ILADUB_MEMBRANE=pyshacl` re-runs any suspect verdict under the reference engine without
    a code change. Correctness is established by tests/etkl/test_membrane_equiv.py, not by
    trust — see spec 2026-08-06 §3.3.
    """
    forced = os.environ.get("ILADUB_MEMBRANE")
    if forced:
        return forced
    return "rudof" if rudof_available() else "pyshacl"
```

- [ ] **Step 2: Measure the page baseline against the spec's number**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl import compile_tables, membrane
print("engine:", membrane.engine_name())
t0 = time.monotonic()
rep = compile_tables("corpus/ag-trade/graincorp-stem-2026-07-31.pdf", page_number=0)
print(f"page-0 compile: {time.monotonic()-t0:.1f}s  score={rep.score:.4f}  (baseline 28.4s / 0.9560)")
EOF
```
Expected: score **0.9560 unchanged**; wall under 14 s (spec §5). Record the real number.

- [ ] **Step 3: The corpus gate — byte-identical scores**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q
```
Expected: PASS with stem **0.9655** / 2152 cells and CBH **0.9047**. Then the apple record:

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -c "
from iladub.etkl.document import compile_document
r = compile_document('corpus/financial/apple-fy2026q3-statements.pdf')
print(f'apple {r.score:.10f} (expect 0.0105540897)')"
```

If any score moves, STOP and report BLOCKED with the measurement — a moved score means the two engines disagree on a real document, which is exactly what the battery exists to prevent, and it outranks the speedup.

- [ ] **Step 4: The whole-document measurement for the successor loop**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import time
from iladub.etkl.document import compile_document
t0 = time.monotonic()
rep = compile_document("corpus/ag-trade/graincorp-stem-2026-07-31.pdf")
print(f"stem document: {time.monotonic()-t0:.0f}s  score={rep.score:.4f}  (baseline ~180-202s / 0.9655)")
EOF
```
Record verbatim — spec §5 requires this number in the register so the successor loop has a committed baseline.

- [ ] **Step 5: Full suite, foreground**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest -q 2>&1 | tail -6
```
Expected: 0 failed except the known machine-environmental `tests/test_release_gate.py::test_since_date_fallback_and_previous_tag` (bare env dict without PATH hits this machine's broken git shim; pre-existing, CI-green). Anything else red must be diagnosed regression-vs-pre-existing and reported.

- [ ] **Step 6: Spec status + register rows**

Update the spec's `**Status:**` line to `closed 2026-08-06` with the measured page and document numbers. Then append to `docs/superpowers/residues.md`, in the house format (what / measured / why deferred / what would close it), two rows:

- **The membrane redundancy** — 8.2 s of the final pass's 12.6 s re-checks gate-covered shapes (measured 2026-08-06; gate subset 8.2 s, remaining eleven shapes 5.1 s). Deferred because at rudof speed it recovers ~0.06 s, and closing it needs a per-shape region-locality proof — a claim this repo has been bitten by before (loop M's duplicate `doc#table0`, R36's slug collisions). Closes with that proof, or with an adjudication that the two membranes' scopes stay as they are.
- **owlrl is now the membrane's bottleneck** — measured: closure 1.4 s vs rudof validate 0.08 s, i.e. ~two-thirds of the new membrane cost. Deferred to the successor loop (spec §7, subclass-only closure, measured at 0.07 s / +604 types, which also closes the R19 hazard class at its root).

- [ ] **Step 7: Lints + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add src/iladub/etkl/membrane.py docs/superpowers/specs/2026-08-06-membrane-engine-swap-design.md docs/superpowers/residues.md && git commit -m "feat(loop-membrane): rudof by default, measured and closed

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 8: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-06)

- **Spec coverage:** §3.1 seam → Task 1; §3.2 units → Tasks 1–3; §3.3 battery → Task 4; §3.4 switch → Tasks 3 and 5 Step 1; §4 no-change constraints → Global Constraints; §5 success criteria → Task 5 Steps 2–5; §6 registered-not-built → Task 5 Step 6 row 1; §7 successor baseline → Task 5 Steps 4 and 6 row 2; §8 risks → Task 3's report-parse note, Task 4's two failure protocols, Task 1's isolation of refactor from engine change.
- **Placeholder scan:** none. The two "adapt if…" notes (Task 3's conformance parse, Task 2's owlrl dependency) state the invariant and the safe direction rather than deferring a decision.
- **Type consistency:** `validate(data_graph, shapes_graph, ont_graph) -> tuple[bool, str]`, `rdfs_closure(data_graph, ont_graph) -> Graph`, `engine_name() -> str`, `rudof_available() -> bool`, `_validate_pyshacl`/`_validate_rudof` — used identically in Tasks 1, 3, 4, 5.
