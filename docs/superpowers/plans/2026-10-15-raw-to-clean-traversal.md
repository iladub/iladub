# The raw→clean traversal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:holon:06 — the raw→clean traversal, compiler-produced.

**Goal:** `ground_document(..., traversal=Traversal(...))` derives a `GroundingPortal` and a `CleanDocumentHolon` from present promotions, and a generated worked example meets holon:06.

**Architecture:** spec § 2 approach A — an open-world `CONSTRUCT` over this call's grounding output, a closed-world shape in the grounding membrane, an opt-in keyword. This plan cites the spec and does not re-derive it (CLAUDE.md plan rule 6).

**Tech Stack:** rdflib (SPARQL CONSTRUCT, `rdflib.compare.isomorphic`), the repo membrane (`src/iladub/etkl/membrane.py`, rudof or pySHACL), pytest.

**Spec:** `docs/superpowers/specs/2026-10-15-raw-to-clean-traversal-design.md` (approved 2026-10-15).

**Doc impact: increment.** Same increment the spec declares (spec header); this plan adds no term the spec does not.

**Authored at ~40K working tokens, under the 50K originating floor, in a fresh session.**

## Global Constraints

- **Neurosymbolic gate (CLAUDE.md § 8):** every decision is classified per spec § 3.6. No NEURAL worker, no tuned constant, no Python that decides which region is reconciled or whether a portal exists — the `.rq` decides; Python only runs it and adds its triples.
- **Evidence-positive (spec § 3.3):** zero grounded nodes in scope ⇒ zero triples constructed.
- **Source ownership:** `etkl-holons.ttl` stays free of `w3id.org/holon` (`tests/test_hga_alignment.py::test_holons_module_standalone`); HGA IRIs appear only as objects, only in `iladub-hga-align.ttl`.
- **Default unchanged:** `traversal=None` constructs nothing and changes no existing output (spec § 3.4, § 5 item 6).
- **Plan rules 1–7 (CLAUDE.md § Plan authoring):** no implementation body below; tests given verbatim are propositions until the implementer falsifies them. **Every task report carries a `## FALSIFICATION` block** — remove or invert what the test pins, show it failing, restore with `cp`, show green.
- **Census pins move by SET, not by count.** `tests/test_artifact_terms.py:162` and `tests/test_artifact_declarations.py:286` pin 186 tracked `.ttl` artifacts; `tests/test_artifact_declarations.py:287` pins 57 `.rq` files (`ls vocab/queries | wc -l` → 57, measured). The population is `git ls-files`, so a new file joins it at `git add`, not at creation (`tests/test_artifact_terms.py:55-57`). Each task that adds a file re-measures as a set against HEAD, updates the pin, and appends a `RE-MEASURED` comment in the existing style. The census pins 67/72/21 (`tests/test_artifact_terms.py:420-428`) are re-run; if they move, say why.
- **Corpus baseline:** this loop edits `src/` and `vocab/`, so `tests/corpus-baseline/` is regenerated **once, after the last input edit** (Task 5). Never run a "before" pass.

## Measured before writing (the handoff's § 5 items 2–3 and the spec's three seams)

1. **§ 3.3 scope seam — every `ground_document(` call site.** `grep -rn "ground_document(" --include='*.py' src tests scripts` → 26 hits. Every document caller builds `g = Graph()` immediately before the call (`tests/test_corpus.py:162`, `tests/test_corpus_stem.py:53,242`, `tests/test_cbh_e2e.py:87`, `tests/test_corpus_apple_contract.py:91`, `scripts/reach_probe.py:128`, and the rest). **The only non-empty `g` on entry** is `_bare_grounded_node(Graph())` in `tests/test_concept_feed.py` (`::test_grounding_membrane_refuses_a_node_no_promotion_produced` and its two neighbours) — membrane tests, none of which will pass `traversal`. **So no caller would break today if the query ran over `g`.** The plan nonetheless scopes to this call's output, because `ground_document` accepts a pre-populated `g` as a supported input (those tests rely on it) and the spec's scope invariant is about the function's contract, not today's callers. Task 2's scope tests make that choice falsifiable.
2. **§ 5 item 4's six regions — RUN, holds.** `ground_document(_compiled_offer_graph(), *_offer_deps(), g, validate_shapes=True)` → `FeedResult(records=2, grounded=6, proposed=2)`; distinct `iladub:fromRegion` of candidates reviewed by a `iladub:PromotionDecision` that `dec:produced` a `iladub:GroundedNode` = **6**: `urn:iladub:region:p0-{72,200,320}-{109,127}`. Unreviewed candidates' regions = **2**: `urn:iladub:region:p0-440-{109,127}` (the COD column). Spec § 8 item 3 therefore holds on this fixture. (The run prints rdflib `decimal.InvalidOperation` warnings on stderr; pre-existing, unrelated.)
3. **§ 3.5 membrane seam — which shapes `_validate_grounding` loads.** `src/iladub/feed.py:896-897`: `_GROUND_SHAPE_FILES = ("iladub-shapes.ttl", "dec-shapes.ttl")`, `_GROUND_ONT_FILES = ("iladub.ttl", "dec.ttl")`. **Decision:** the shape goes in a **new** file, `vocab/shapes/etkl-holon-shapes.ttl` (pairing with `vocab/ontology/etkl-holons.ttl`), appended to `_GROUND_SHAPE_FILES`. Rejected: adding `etkl-shapes.ttl` to the grounding membrane — it carries `sh:targetSubjectsOf etkl:fieldRole` / `etkl:hasField` and contract shapes (`vocab/shapes/etkl-shapes.ttl:14-185`) that would newly run against every corpus grounding graph, an unmeasured change to the default path. The new file targets only `etkl:CleanDocumentHolon`, which no default-path graph contains. SPARQL constraints already run in this membrane (`iladub-shapes.ttl` and `dec-shapes.ttl` both carry `sh:sparql`), and the Clean/portal focus nodes are IRIs, so `membrane.py:64-75`'s blank-node caveat does not arise.
4. **§ 5 item 7 manifest seam.** `tests/test_arc_manifest.py:16-17,315-326`: a `met true` criterion's `prog:oracleTest` must COLLECT (M5b) and any `prog:oracleArtifact` must exist (M5); M2 (`:423`) refuses `met true` without `prog:metOn`; M3 refuses `metOn` before `declaredOn`. `tests/arc-manifest.ttl:519-531` warns that a comment *inside* the block breaks `scripts/cockpit.py`'s regex reader — comments go above.

## File structure

| file | change | responsibility |
|---|---|---|
| `vocab/ontology/etkl-holons.ttl` | modify | declare `etkl:portalSource`, `etkl:portalTarget` (spec § 3.1) |
| `vocab/ontology/iladub-hga-align.ttl` | modify | `subPropertyOf` + `seeAlso` (spec § 3.2) |
| `vocab/queries/raw-to-clean-traversal.rq` | create | the derivation (spec § 3.3) |
| `src/iladub/feed.py` | modify | `Traversal`; `ground_document(traversal=)`; `_GROUND_SHAPE_FILES` |
| `vocab/shapes/etkl-holon-shapes.ttl` | create | `etkl:CleanDocumentHolonShape` (spec § 3.5) |
| `tests/raw-to-clean-traversal-leak.ttl` | create | the negative (spec § 5 item 2) |
| `scripts/raw_to_clean_example.py` | create | writes the example (spec § 4) |
| `examples/raw-to-clean-traversal.ttl` | create, generated | the worked example |
| `tests/test_raw_to_clean_traversal.py` | create | Task 2–3 behaviour tests |
| `tests/test_hga_alignment.py` | modify | alignment axioms + the manifest's oracle test + regen test |
| `tests/arc-manifest.ttl`, `docs/holonic-interaction.md`, `docs/superpowers/residues*.md`, `tests/corpus-baseline/` | modify | Task 5 |

## Review Focus

1. **Grounding the same document twice into one `g`, traversal only on the second call** — a reader expects the six regions reconciled. A set-difference delta (`g` after minus `g` before) yields an empty delta, because every region triple already existed. Pinned in Task 2 (`test_second_grounding_into_same_graph_still_reconciles`).
2. **A pre-populated `g` holding another document's promotions** — a reader expects only this call's regions reconciled. Pinned in Task 2 (`test_preseeded_graph_regions_not_reconciled`).
3. **A Raw IRI already carrying a fragment** (`…/doc#x`) — minting `#clean` onto it yields `…/doc#x#clean`, not an IRI. `Traversal` refuses it with `ValueError`. Pinned in Task 2.
4. **`semantic=()`** — spec § 3.4 says non-empty; a portal with no `portalTarget` would then fail the membrane far from the cause. `Traversal` refuses it at construction (R89 producer-side guard: fail at the call site). Pinned in Task 2.
5. **Two Semantic holons** — a reader expects one portal with two `portalTarget`s, not two portals. Pinned in Task 2.

---

### Task 1: Vocabulary and alignment

**Files:** Modify `vocab/ontology/etkl-holons.ttl`, `vocab/ontology/iladub-hga-align.ttl`; Test `tests/test_hga_alignment.py`.

**Interfaces:** Produces `etkl:portalSource` (`owl:ObjectProperty`, domain `etkl:GroundingPortal`, range `etkl:RawDocumentHolon`) and `etkl:portalTarget` (`owl:ObjectProperty`, domain `etkl:GroundingPortal`, range `etkl:SemanticHolon`), with `rdfs:label`/`rdfs:comment` in the file's style. Tasks 2–4 use both IRIs.

- [ ] **Step 1: failing test** — append to `tests/test_hga_alignment.py`:

```python
def test_portal_property_alignment():
    """spec § 3.2: source aligns by subPropertyOf (both object properties); target only by
    seeAlso, because holon:portalTarget is a DatatypeProperty over xsd:anyURI."""
    from rdflib import OWL, RDF
    g = _g(os.path.join(ONT, "iladub-hga-align.ttl"))
    src, tgt = URIRef(ETKL + "portalSource"), URIRef(ETKL + "portalTarget")
    assert (src, RDFS.subPropertyOf, URIRef(HOLON + "sourceHolon")) in g
    assert (tgt, RDFS.seeAlso, URIRef(HOLON + "portalTarget")) in g
    assert (tgt, RDFS.subPropertyOf, URIRef(HOLON + "portalTarget")) not in g
    h = _g(os.path.join(ONT, "etkl-holons.ttl"))
    for p, rng in ((src, "RawDocumentHolon"), (tgt, "SemanticHolon")):
        assert (p, RDF.type, OWL.ObjectProperty) in h
        assert (p, RDFS.domain, URIRef(ETKL + "GroundingPortal")) in h
        assert (p, RDFS.range, URIRef(ETKL + rng)) in h
```

- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_hga_alignment.py -q` → the new test FAILS, others pass.
- [ ] **Step 3:** add the two declarations to `etkl-holons.ttl` (no `holon:` text — `test_holons_module_standalone` guards it) and the two axioms to `iladub-hga-align.ttl`, with a comment beside the `seeAlso` stating the kind mismatch (spec § 3.2). Update the stale comment at `iladub-hga-align.ttl:52-53` only if it now contradicts; keep any edit line-neutral or re-measure citations after (plan rule 7).
- [ ] **Step 4:** `.venv/bin/python -m pytest tests/test_hga_alignment.py tests/test_source_ownership.py tests/test_artifact_terms.py tests/test_artifact_declarations.py -q` → green. No file joined the population; if a census pin (67/72/21) moved, record why.
- [ ] **Step 5:** FALSIFICATION — swap `seeAlso` for `subPropertyOf` on `portalTarget`, show FAIL, restore via `cp`.
- [ ] **Step 6:** commit `holon:06 Task 1: etkl:portalSource / portalTarget and their HGA alignment`.

### Task 2: The derivation and the call site

**Files:** Create `vocab/queries/raw-to-clean-traversal.rq`, `tests/test_raw_to_clean_traversal.py`; Modify `src/iladub/feed.py`, `tests/test_artifact_declarations.py:287` (57 → 58, set-measured).

**Interfaces:**
- Consumes: Task 1's two properties.
- Produces: `iladub.feed.Traversal` — frozen dataclass `(raw: URIRef, semantic: tuple[URIRef, ...])`; raises `ValueError` if `semantic` is empty or `str(raw)` contains `#`. `ground_document(graph, contract, proposer, terms, shapes, g, validate_shapes: bool = False, *, traversal: Traversal | None = None) -> FeedResult` — return value unchanged by `traversal`. Derived IRIs: `URIRef(str(raw) + "#grounding-portal")`, `URIRef(str(raw) + "#clean")` (spec § 3.3).

**Invariants (spec § 3.3–3.4, cited not restated):** evidence-positive; scope = this call's grounding output only; derived triples are added to `g` **before** the `validate_shapes` branch (`feed.py`, the `if validate_shapes:` block at the end of `ground_document`); `traversal=None` executes no query.

**SEAMS — MEASURE before writing, record the answers in the task report:**
- **How "this call's output" is isolated.** Review Focus 1 rules out a before/after set difference. The obvious alternative is to ground into a fresh local graph and merge it into `g` afterwards — which is sound **only if** nothing on the `ground_concept` path reads `g` (`src/iladub/ground.py`, `_emit_grounded` and the three `return "proposed"` branches the spec cites at `ground.py:414-488`). Measure that; do not assume it. If something does read `g`, the scope must be expressed another way, and the task report says how.
- **How several Semantic IRIs reach one CONSTRUCT.** `initBindings` binds one value per variable (the idiom at `src/iladub/etkl/adoption.py:147`). Choose a form (`VALUES` substitution, or one execution per IRI whose triples merge on the deterministic portal IRI); Review Focus 5 is the oracle either way.
- **The query loader.** Follow an existing `Path(__file__).resolve().parents[…] / "vocab" / "queries"` idiom (`adoption.py:29`) or `feed.py`'s own `_repo_vocab()` (`feed.py:903`); state which.

- [ ] **Step 1: failing tests** — create `tests/test_raw_to_clean_traversal.py`:

```python
"""holon:06 — the raw→clean traversal derived by ground_document (spec 2026-10-15)."""
import pytest
from rdflib import Graph, Namespace, RDF, URIRef

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")
from iladub.feed import Traversal, ground_document
from iladub.propose_ground import FakeGroundingProposer, GroundingProposal
from tests.test_concept_feed import _compiled_hier_graph, _compiled_offer_graph, _offer_deps

ETKL = Namespace("https://w3id.org/iladub/etkl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
RAW = URIRef("https://example.org/demo/offer-table")
SEM = URIRef("https://example.org/demo/transplant-terms")
GROUNDED = {URIRef(f"urn:iladub:region:p0-{x}-{y}") for x in (72, 200, 320) for y in (109, 127)}
QUARANTINED = {URIRef(f"urn:iladub:region:p0-440-{y}") for y in (109, 127)}


def _offer(g=None, traversal=Traversal(RAW, (SEM,)), proposer=None):
    c, terms, shapes, p = _offer_deps()
    g = Graph() if g is None else g
    ground_document(_compiled_offer_graph(), c, proposer or p, terms, shapes, g,
                    validate_shapes=True, traversal=traversal)
    return g


def _etkl_triples(g):
    return [t for t in g if any(str(x).startswith(str(ETKL)) for x in t)]


def test_six_grounded_regions_reconciled_quarantine_excluded():
    g = _offer()
    portal, clean = URIRef(str(RAW) + "#grounding-portal"), URIRef(str(RAW) + "#clean")
    assert set(g.objects(portal, ETKL.reconciles)) == GROUNDED
    assert not QUARANTINED & set(g.objects(None, ETKL.reconciles))
    assert (clean, ETKL.throughPortal, portal) in g
    assert (clean, PROV.wasDerivedFrom, RAW) in g
    assert (portal, ETKL.portalSource, RAW) in g
    assert (portal, ETKL.portalTarget, SEM) in g
    assert len(set(g.subjects(RDF.type, ETKL.CleanDocumentHolon))) == 1


def test_nothing_grounded_constructs_nothing():
    abstain = FakeGroundingProposer(GroundingProposal(
        None, "https://example.org/transplant#x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    c, terms, shapes, _ = _offer_deps()
    g = Graph()
    # The Organ column may still ground by an exact-match oracle under an abstaining proposer;
    # MEASURE the grounded count first. If it is non-zero, use a contract/terms pair under
    # which it is zero and say so in the task report — never weaken the assertion below.
    res = ground_document(_compiled_offer_graph(), c, abstain, terms, shapes, g,
                          traversal=Traversal(RAW, (SEM,)))
    assert res.grounded == 0
    assert _etkl_triples(g) == []


def test_default_constructs_nothing():
    assert _etkl_triples(_offer(traversal=None)) == []


def test_preseeded_graph_regions_not_reconciled():
    c, terms, shapes, p = _offer_deps()
    g = Graph()
    ground_document(_compiled_hier_graph(), c, p, terms, shapes, g)
    g = _offer(g)
    assert set(g.objects(None, ETKL.reconciles)) == GROUNDED


def test_second_grounding_into_same_graph_still_reconciles():
    g = _offer(traversal=None)
    g = _offer(g)
    assert set(g.objects(None, ETKL.reconciles)) == GROUNDED


def test_two_semantic_holons_one_portal():
    sem2 = URIRef("https://example.org/demo/other-terms")
    g = _offer(traversal=Traversal(RAW, (SEM, sem2)))
    portals = set(g.subjects(RDF.type, ETKL.GroundingPortal))
    assert len(portals) == 1
    assert set(g.objects(next(iter(portals)), ETKL.portalTarget)) == {SEM, sem2}


@pytest.mark.parametrize("raw, sem", [(RAW, ()), (URIRef(str(RAW) + "#x"), (SEM,))])
def test_traversal_refuses_unusable_identity(raw, sem):
    with pytest.raises(ValueError):
        Traversal(raw, sem)
```

`test_preseeded_graph_regions_not_reconciled` needs the hier fixture's regions to be disjoint from the offer's and to ground at least one concept under `_offer_deps()` — **MEASURE both before relying on it** (plan rule 5: can the setup be constructed?). If they overlap or nothing grounds, substitute another compiled fixture from `tests/test_concept_feed.py` with the same force and say so.

- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_raw_to_clean_traversal.py -q` → FAIL (`ImportError: Traversal`).
- [ ] **Step 3:** write the `.rq` (header comment in the style of `vocab/queries/adoption-candidate.rq`: gate class AXIOM/derivation, open world, evidence-positive) and the `feed.py` changes. Python runs the query and adds its triples; it decides nothing (spec § 3.6). Comment the PROCEDURAL step's irreducibility in the code, as `membrane.py:1-8` does.
- [ ] **Step 4:** run the new file, then `tests/test_concept_feed.py tests/test_artifact_terms.py tests/test_artifact_declarations.py -q`. Update the `.rq` pin 57 → 58 after `git add`, set-measured, with a `RE-MEASURED` comment.
- [ ] **Step 5:** FALSIFICATION, at least: (a) delete the `dec:produced`/`GroundedNode` pattern from the `.rq` → `test_six_grounded…` fails on the quarantined regions; (b) replace your scope isolation with "query all of `g`" → `test_preseeded…` fails; (c) replace it with a before/after set difference → `test_second_grounding…` fails; (d) drop the evidence gate → `test_nothing_grounded…` fails. Restore via `cp` each time.
- [ ] **Step 6:** commit `holon:06 Task 2: ground_document derives the raw→clean traversal (opt-in)`.

### Task 3: The membrane

**Files:** Create `vocab/shapes/etkl-holon-shapes.ttl`, `tests/raw-to-clean-traversal-leak.ttl`; Modify `src/iladub/feed.py:896` (`_GROUND_SHAPE_FILES`), `tests/test_raw_to_clean_traversal.py`, the 186 pins (+2, set-measured).

**Interfaces:** Consumes Task 1–2. Produces `etkl:CleanDocumentHolonShape` with exactly the constraints of spec § 3.5 (cited; not restated here). The source-equality constraint is `sh:sparql` (spec § 3.5 explains why `sh:equals` cannot). File header carries CC-BY-4.0 and author metadata as the other shape files do.

**SEAM:** whether `_GROUND_ONT_FILES` must gain `etkl-holons.ttl`. Every `sh:class` here names a type the CONSTRUCT asserts directly, so subclass closure should not be needed — **measure by running the Task 2 tests with `validate_shapes=True` (they already do) before adding anything**, and add the ontology only if a conformant graph is refused.

- [ ] **Step 1: failing tests** — append to `tests/test_raw_to_clean_traversal.py`:

```python
def _membrane(g):
    from iladub.feed import _validate_grounding
    return _validate_grounding(g)


def test_leak_fixture_refused_on_both_focus_nodes():
    """spec § 5 item 2: no throughPortal on one Clean holon; a portal whose source is not
    the other Clean holon's wasDerivedFrom. Each violation on its own focus node."""
    import os
    g = Graph().parse(os.path.join(os.path.dirname(__file__),
                                   "raw-to-clean-traversal-leak.ttl"), format="turtle")
    conforms, report = _membrane(g)
    assert not conforms
    assert "https://example.org/leak/no-portal#clean" in report
    assert "https://example.org/leak/wrong-source#clean" in report


def test_grounding_membrane_runs_the_clean_shape():
    """The shape is IN the membrane validate_shapes=True runs (spec § 3.4), not only in a
    file a test loads by hand."""
    g = _offer()
    g.remove((URIRef(str(RAW) + "#clean"), ETKL.throughPortal, None))
    conforms, report = _membrane(g)
    assert not conforms and "CleanDocumentHolon" in report
```

The leak fixture's two Clean holons are `https://example.org/leak/no-portal#clean` and `https://example.org/leak/wrong-source#clean`; it is otherwise well-formed, so each refusal has exactly one cause. Report wording differs by engine (`membrane.py:56-58`); if `"CleanDocumentHolon"` does not appear in a rudof report, assert on the shape IRI instead and say so.

- [ ] **Step 2:** run → FAIL.
- [ ] **Step 3:** write the shape file, the leak fixture, the `_GROUND_SHAPE_FILES` entry.
- [ ] **Step 4:** run the new file under both engines (`ILADUB_MEMBRANE=pyshacl` and the default), then `tests/test_concept_feed.py tests/test_vocab_shapes.py tests/test_artifact_terms.py tests/test_artifact_declarations.py tests/test_source_ownership.py -q`. Pins 186 → 188 after `git add`, set-measured.
- [ ] **Step 5:** FALSIFICATION — (a) delete the `sh:sparql` source-equality constraint → the leak test fails on `wrong-source`; (b) remove the file from `_GROUND_SHAPE_FILES` → `test_grounding_membrane_runs_the_clean_shape` fails. Restore via `cp`.
- [ ] **Step 6:** commit `holon:06 Task 3: etkl:CleanDocumentHolonShape joins the grounding membrane`.

### Task 4: The generated worked example and the manifest's oracle

**Files:** Create `scripts/raw_to_clean_example.py`, `examples/raw-to-clean-traversal.ttl`; Modify `tests/test_hga_alignment.py`, the 188 pins (+1).

**Interfaces:** `scripts/raw_to_clean_example.py` exposes `build() -> rdflib.Graph` (the grounding graph of spec § 4: the offer fixture, `_offer_deps()`, `validate_shapes=True`, `Traversal(URIRef("https://example.org/demo/offer-table"), (URIRef("https://example.org/demo/transplant-terms"),))`) and, as `__main__`, writes it as Turtle to `examples/raw-to-clean-traversal.ttl`. It imports the fixture helpers from `tests/`; state in its docstring that it is PROCEDURAL glue (spec § 3.6) and that the file is generated.

**SEAM:** whether `build()` is deterministic up to blank nodes — run it twice and compare with `rdflib.compare.isomorphic` **before** writing the regen test (spec § 8 item 1). Region IRIs come from reportlab coordinates; a non-isomorphic second run is a finding to report, not a test to loosen.

- [ ] **Step 1: failing tests** — append to `tests/test_hga_alignment.py`:

```python
TRAVERSAL_SHAPES = [os.path.join(SH, f) for f in
                    ("iladub-shapes.ttl", "dec-shapes.ttl", "etkl-holon-shapes.ttl",
                     "iladub-hga-shapes.ttl")]
TRAVERSAL_ONTS = ONTS + [os.path.join(ONT, "dec.ttl")]
TRAVERSAL_EX = os.path.join(EX, "raw-to-clean-traversal.ttl")


def test_raw_to_clean_traversal_conformant():
    """holon:06's oracle (tests/arc-manifest.ttl): the compiler-produced example conforms and
    spans Raw → portal → Clean (spec § 5 item 1)."""
    from rdflib import RDF
    c, t = _v([TRAVERSAL_EX], TRAVERSAL_SHAPES, TRAVERSAL_ONTS)
    assert c, t
    g = _g(TRAVERSAL_EX)
    count = lambda cls: len(set(g.subjects(RDF.type, URIRef(ETKL + cls))))
    assert (count("CleanDocumentHolon"), count("GroundingPortal"),
            count("RawDocumentHolon")) == (1, 1, 1)
    assert count("SemanticHolon") >= 1


def test_raw_to_clean_example_is_what_the_compiler_emits():
    """spec § 4: regenerate and compare by graph isomorphism (decisions are blank nodes)."""
    import importlib.util
    import pytest
    from rdflib.compare import isomorphic
    pytest.importorskip("pdfplumber")
    pytest.importorskip("reportlab")
    spec = importlib.util.spec_from_file_location(
        "raw_to_clean_example", os.path.join(ROOT, "scripts", "raw_to_clean_example.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert isomorphic(mod.build(), _g(TRAVERSAL_EX)), \
        "examples/raw-to-clean-traversal.ttl is stale: run scripts/raw_to_clean_example.py"
```

- [ ] **Step 2:** run → FAIL (file missing).
- [ ] **Step 3:** write the script; run it; `git add` the example.
- [ ] **Step 4:** `.venv/bin/python -m pytest tests/test_hga_alignment.py tests/test_artifact_terms.py tests/test_artifact_declarations.py tests/test_doc_governance.py -q` → green; pins 188 → 189 set-measured. (`examples/` is not an Evidence path; confirm `test_doc_governance.py` agrees rather than assuming — handoff § 4.)
- [ ] **Step 5:** FALSIFICATION — (a) delete one `etkl:reconciles` triple from the committed example → the regen test fails; (b) delete the Clean holon's `etkl:throughPortal` → the oracle test fails. Restore via `cp`.
- [ ] **Step 6:** commit `holon:06 Task 4: the generated raw→clean worked example`.

### Task 5: Close the criterion, raise the residues, regenerate the baseline

**Files:** Modify `tests/arc-manifest.ttl:524-531`, `docs/holonic-interaction.md` (§ "Planned work"), `docs/superpowers/residues.md`, `docs/superpowers/residues-open.md`, `tests/corpus-baseline/`.

- [ ] **Step 1:** `prog:criterion:holon:06`: `prog:met true`, `prog:metOn "<merge-day>"^^xsd:date`, `prog:oracleArtifact "examples/raw-to-clean-traversal.ttl"`. No comment inside the block (`arc-manifest.ttl:519-528`). Run `tests/test_arc_manifest.py tests/test_cockpit.py -q`; FALSIFICATION — rename the oracle test node id in the manifest → M5b fails; restore.
- [ ] **Step 2:** `docs/holonic-interaction.md` — remove the one planned-work item this ships, pointing at the example and the `.rq` (spec header). Check its class first (`tests/test_doc_governance.py`); if it is Evidence, add rather than delete.
- [ ] **Step 3:** raise two rows per spec § 7, each with the closed-tally snapshot `(c/t closed)` measured from `residues.md` at that moment, full rows in `residues-open.md`, one index line each: (a) one constant document IRI for every compile (`src/iladub/etkl/compile.py:22`), so the Raw holon is caller-named; (b) the Clean holon carries no membrane health (`membrane-health.rq` scoped to `etkl:CompiledDocumentHolon`, `vocab/shapes/etkl-shapes.ttl:161-162`).
- [ ] **Step 4 (last input edit is behind you):** `PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate` — serial, ~24 min, nothing else running. **PROPOSITION (spec § 5 item 6):** `git diff --stat -- tests/corpus-baseline/` touches only `inputs.json`. If any document snapshot moves, the default path is not inert: stop, diagnose (superpowers:systematic-debugging), do not commit the baseline as-is.
- [ ] **Step 5:** full suite `.venv/bin/python -m pytest -q` — read the `N passed` line, not the exit code. Commit `holon:06 Task 5: criterion met; residues raised; baseline regenerated`.

## What this plan does not do

Spec § 6 in full. In particular no corpus test passes `traversal`, and `examples/holon-grounding-conformant.ttl` is untouched.
