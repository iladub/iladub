# Header-region row roles (NEURAL) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide each non-leaf header-region row's role (`furniture` | `continuation` | `level`) as a NEURAL proposal disposed by two SHACL oracles and admitted only via an `iladub:PromotionDecision` — closing the GrainCorp `MERGE_AMBIGUOUS` escalation (0.0 → 0.947).

**Architecture:** A new `rowrole.py` NEURAL slice, structurally a sibling of the shipped `span.py` (B1.3): `propose → build → oracle → promote`. It fires from `compile.py`'s hierarchical branch **only** when the geometric tree fails `merge_tiling_ok` **and** a `row_role_proposer` is injected (default `None` → escalate exactly as today). Disposal is closed-world SHACL: the eight shipped tiling shapes plus one new content-conservation shape, both inside the single `region_tiles` call. Continuation fragments are placed by reusing Loop B's shipped `header-covers.rq` AXIOM. No search over the role space.

**Tech Stack:** Python 3 (`src/iladub/etkl/`), rdflib, pySHACL (`inference="rdfs"`, `advanced=True`), RDF Turtle (`vocab/ontology/tab.ttl`, `vocab/shapes/tab-shapes.ttl`), SPARQL (`vocab/queries/*.rq`), BAML (`baml_src/`), pytest.

**Spec:** `docs/superpowers/specs/2026-07-26-header-row-roles-design.md` (read it before starting).

**Run tests with:** `. .venv/bin/activate && python3 -m pytest -q` (from the repo root, `/Volumes/WD Green/dev/git/iladub`).

## Global Constraints

Copied verbatim from the spec's §5 gate. **Every task's requirements implicitly include this section.**

- **The role is decided ONLY by the injected NEURAL proposer.** No Python may infer a role from geometry, text patterns, or heuristics. A helper may *report* geometry; it may never *decide* a role.
- **No tuned constant, no tolerance, no new numeric literal** — in Python, in RDF, or in SPARQL. A tuned constant is prima facie evidence the decision belongs in NEURAL/AXIOM (CLAUDE.md §8). `tests/etkl/test_transform_gate.py` enforces this for `.rq` files and `tiling.py`.
- **Legality gates admission, never confidence.** A reading whose scratch region fails either oracle is refused regardless of `proposal.confidence`. Confidence is *recorded* on the promotion, never compared against a threshold. There is no `if confidence > …` anywhere.
- **No search over the role space.** One proposal, one disposal. `all furniture` is always legal, so any search converges on it and strips real header labels.
- **Open/closed split.** Growth is open-world (the reused `header-covers.rq` derivation); disposal is closed-world SHACL. A **fresh scratch `Graph()`** per candidate reading — the region is the closure boundary.
- **On refusal, `graph` MUST be untouched** and the function returns `None` so the caller escalates `MERGE_AMBIGUOUS` in-band. Honest failure over a fake success.
- **Default path byte-identical.** With `row_role_proposer=None` (the default), behaviour must be exactly today's. The full suite (548 tests at Loop B close) stays green; no existing test may be weakened.
- **Source ownership** (CLAUDE.md, CI-enforced by `tests/test_source_ownership.py`): only `tab:` terms are authored. No `w3id.org/holon` IRI may appear as a subject anywhere.
- **No third-party PDF committed.** The GrainCorp PDF stays at `/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf` and is referenced only in Task 6's local verification.
- **No overfitting** (zero tolerance): every fixture is synthetic and domain-neutral, authored from the *shape* of the problem, never from GrainCorp bytes. GrainCorp is a confirmation, not a target.
- **The three role strings are exactly** `"furniture"`, `"continuation"`, `"level"` — lowercase, no synonyms, no aliases.

---

## File Structure

| File | Responsibility |
| --- | --- |
| `vocab/ontology/tab.ttl` | **Modify (append).** Owned classes `tab:RegionCaption`, `tab:HeaderSourceCell` + properties `tab:hasCaption`, `tab:hasHeaderSourceCell`, `tab:captionText`, `tab:captionRow`, `tab:sourceText`, `tab:sourceRow`. |
| `vocab/shapes/tab-shapes.ttl` | **Modify (append).** `tab:HeaderContentConservedShape` — oracle 2. |
| `src/iladub/etkl/tiling.py` | **Modify.** Add the new shape IRI to `_TILING_SHAPE_IRIS` so one `region_tiles` call carries both oracle families. |
| `src/iladub/etkl/headers.py` | **Modify (refactor only, zero behaviour change).** Extract `header_rows_of` and `_tree_from_rows` out of `infer_header_tree` so `rowrole.py` can reuse them. |
| `src/iladub/etkl/propose.py` | **Modify (append).** `RowRoleProposal`, `RowRoleProposer` Protocol, `FakeRowRoleProposer`, `BamlRowRoleProposer`. |
| `baml_src/header_rowrole.baml` | **Create.** `HeaderRowRoleProposal` class + `ProposeHeaderRowRoles` function. |
| `src/iladub/etkl/rowrole.py` | **Create.** The NEURAL slice: `row_role_context`, `build_row_reading`, `emit_reading_evidence`, `resolve_header_row_roles`. |
| `src/iladub/etkl/promote.py` | **Modify (append).** `emit_row_role_promotion`. |
| `src/iladub/etkl/compile.py` | **Modify.** `row_role_proposer=None` kwarg; call the resolver on the tiling-failure branch. |
| `tests/etkl/test_conservation_shape.py` | **Create.** Oracle-2 unit tests (Task 1). |
| `tests/etkl/test_rowrole_proposer.py` | **Create.** Proposer seam tests (Task 2). |
| `tests/etkl/test_rowrole_reading.py` | **Create.** `build_row_reading` structural tests + the red fixture (Task 3). |
| `tests/etkl/test_rowrole_resolution.py` | **Create.** Driver / oracle-disposal / promotion tests (Task 4). |
| `tests/etkl/test_rowrole_integration.py` | **Create.** `compile_tables` wiring + the contract guard (Task 5). |

**Task order and dependencies:** 1 → 2 → 3 → 4 → 5 → 6. Task 4 consumes Tasks 1–3; Task 5 consumes Task 4.

---

## The verified fixture (used by Tasks 3, 4)

This exact fixture was **probed against the current code during planning** and confirmed to reproduce the bug. Do not alter its coordinates.

- Grid `LeafGrid((100.0, 150.0, 200.0, 250.0, 300.0), 4, 50.0, 1.0)` → 4 columns, boundaries at 100/150/200/250/300.
- Uniform 12 pt line spacing, so `group_wrapped`'s `0.9 × lead = 10.8 pt` threshold is **below** the 12 pt gap and the header rows are **not** absorbed — reproducing GrainCorp's header-leading ≈ body-leading condition.
- Row 0 (caption, top 0): `Monday`(205–240), `5 May`(242–262).
- Row 1 (wrap fragment, top 12): `Unit`(155–175).
- Row 2 (leaf labels, top 24): `Item`(110–140), `Ref`(155–172), `Qty`(205–230), `Cost`(255–285).
- Rows 3–4 (body, tops 36/48): text in col 0, values in cols 1–3.

**Measured facts (verified during planning — assert these, don't re-derive them):**
- `header_body_split(band, grid)` → `3`.
- `group_wrapped` yields 5 rows; the 3 header rows stay separate.
- `merge_tiling_ok(infer_header_tree(band, grid, 3), grid)` → **`False`** (level-0 overlap: `Monday`→`(2,)` and `5 May`→`(2, 3)` both claim column 2).
- Under the reading `("furniture", "continuation")`: labels are exactly `Item`, `Unit Ref`, `Qty`, `Cost`; `merge_tiling_ok` → `True`; `assert_hier_region` returns **8** asserted tokens; `region_tiles` → `True`.

---

### Task 1: The content-conservation oracle (vocab + shape + wiring)

**Files:**
- Modify: `vocab/ontology/tab.ttl` (append at end of file)
- Modify: `vocab/shapes/tab-shapes.ttl` (append at end of file)
- Modify: `src/iladub/etkl/tiling.py:17-19`
- Test: `tests/etkl/test_conservation_shape.py` (create)

**Interfaces:**
- Consumes: nothing (first task).
- Produces: the IRIs `tab:RegionCaption`, `tab:HeaderSourceCell`, `tab:hasCaption`, `tab:hasHeaderSourceCell`, `tab:captionText`, `tab:captionRow`, `tab:sourceText`, `tab:sourceRow`, `tab:HeaderContentConservedShape`. `region_tiles(graph)` keeps its signature `(rdflib.Graph) -> bool` but now also enforces conservation.

- [ ] **Step 1: Confirm the new terms do not already exist**

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && grep -n "RegionCaption\|HeaderSourceCell\|captionText\|captionRow\|sourceText\|sourceRow\|HeaderContentConservedShape" vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl
```
Expected: **no output** (exit 1). This is the B2c lesson — grep the target TTL before adding. If anything is found, STOP and report; do not redefine an existing term.

- [ ] **Step 2: Write the failing test**

Create `tests/etkl/test_conservation_shape.py`:

```python
"""Loop C oracle 2 — header-region content conservation.

A reading that loses header text is REFUSED by region_tiles. See
docs/superpowers/specs/2026-07-26-header-row-roles-design.md §3.4.
"""
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from iladub.etkl.tiling import region_tiles

TAB = Namespace("https://w3id.org/iladub/tab#")
_T = URIRef("urn:doc#t0")


def _source_cell(g, k, text, row=0):
    """One committed tab:HeaderSourceCell — the conservation oracle's target."""
    sc = URIRef("%s-hsc%d" % (_T, k))
    g.add((sc, RDF.type, TAB.HeaderSourceCell))
    g.add((sc, TAB.sourceText, Literal(text)))
    g.add((sc, TAB.sourceRow, Literal(row, datatype=XSD.integer)))
    g.add((_T, TAB.hasHeaderSourceCell, sc))
    return sc


def _label(g, k, text):
    lc = URIRef("%s-hl%d" % (_T, k))
    g.add((lc, RDF.type, TAB.LabelCell))
    g.add((lc, TAB.cellText, Literal(text)))
    return lc


def _caption(g, k, text, row=0):
    cap = URIRef("%s-cap%d" % (_T, k))
    g.add((cap, RDF.type, TAB.RegionCaption))
    g.add((cap, TAB.captionText, Literal(text)))
    g.add((cap, TAB.captionRow, Literal(row, datatype=XSD.integer)))
    g.add((_T, TAB.hasCaption, cap))
    return cap


def test_lost_header_text_is_refused():
    # "Unit" appears in NO label and NO caption -> the word vanished -> refuse.
    g = Graph()
    _source_cell(g, 0, "Unit")
    _label(g, 0, "Ref")
    assert region_tiles(g) is False


def test_text_merged_into_a_label_is_conserved():
    # the continuation reading: "Unit" merged into the label "Unit Ref" -> conserved.
    g = Graph()
    _source_cell(g, 0, "Unit")
    _label(g, 0, "Unit Ref")
    assert region_tiles(g) is True


def test_text_carried_as_a_caption_is_conserved():
    # the furniture reading: "Monday" carried as a RegionCaption, not dropped -> conserved.
    g = Graph()
    _source_cell(g, 0, "Monday")
    _caption(g, 0, "Monday")
    assert region_tiles(g) is True


def test_graph_without_source_cells_is_unaffected():
    # zero-regression guard: the shape targets tab:HeaderSourceCell, so every existing
    # region (which emits none) is untouched by the new oracle.
    g = Graph()
    _label(g, 0, "Anything")
    assert region_tiles(g) is True
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_conservation_shape.py -q`
Expected: `test_lost_header_text_is_refused` **FAILS** (`assert True is False`) because the shape does not exist yet, so nothing refuses the lossy graph. The other three pass vacuously.

- [ ] **Step 4: Append the owned vocabulary to `vocab/ontology/tab.ttl`**

Append at the very end of the file:

```turtle

# --- committed row-role reading evidence (loop C, GrainCorp push) ---
# NOTE: loop B's tab:atHeaderRow / tab:headerText are deliberately NOT reused. Both carry
# rdfs:domain tab:HeaderCell, and region_tiles validates with inference="rdfs", so a committed
# caption bearing them would be INFERRED to be a tab:HeaderCell — contradicting that class's
# "transient … never asserted into a holon" definition and leaking pre-holon evidence vocabulary
# into the compiled holon. Hence dedicated properties.
tab:RegionCaption a owl:Class ; rdfs:label "Region caption"@en ;
    rdfs:comment "Document furniture (a title/date/page line) found inside a table's header region and CARRIED rather than dropped: the NEURAL row-role reading classified its row as furniture. Committed to the holon with its source row, so no source text is ever lost (spec §3.1, CLAUDE.md §5/§7)."@en .
tab:captionText a owl:DatatypeProperty ; rdfs:domain tab:RegionCaption ; rdfs:range rdfs:Literal ; rdfs:label "caption text"@en .
tab:captionRow a owl:DatatypeProperty ; rdfs:domain tab:RegionCaption ; rdfs:range xsd:integer ; rdfs:label "caption row"@en ;
    rdfs:comment "0-based header-region row index the furniture line came from (0 = topmost)."@en .
tab:hasCaption a owl:ObjectProperty ; rdfs:domain tab:Table ; rdfs:range tab:RegionCaption ; rdfs:label "has caption"@en .

tab:HeaderSourceCell a owl:Class ; rdfs:label "Header source cell"@en ;
    rdfs:comment "A committed record of one header-region source cell, region-bound, and the target of tab:HeaderContentConservedShape: every one must be accounted for either inside an asserted header label or as a tab:RegionCaption. Distinct from tab:HeaderCell, which is transient pre-holon covering evidence."@en .
tab:sourceText a owl:DatatypeProperty ; rdfs:domain tab:HeaderSourceCell ; rdfs:range rdfs:Literal ; rdfs:label "source text"@en .
tab:sourceRow a owl:DatatypeProperty ; rdfs:domain tab:HeaderSourceCell ; rdfs:range xsd:integer ; rdfs:label "source row"@en ;
    rdfs:comment "0-based header-region row index the cell came from (0 = topmost)."@en .
tab:hasHeaderSourceCell a owl:ObjectProperty ; rdfs:domain tab:Table ; rdfs:range tab:HeaderSourceCell ; rdfs:label "has header source cell"@en .
```

- [ ] **Step 5: Append the conservation shape to `vocab/shapes/tab-shapes.ttl`**

Append at the very end of the file:

```turtle

#################################################################
#  Content conservation (loop C oracle 2): every header-region
#  source cell must be accounted for — either merged into an
#  asserted header label, or carried as a region caption. This is
#  what refuses the degenerate "everything is furniture" reading
#  silently deleting real header text.
#
#  Graph-scoped, not ?tbl-scoped, on purpose: region_tiles is
#  invoked on a fresh scratch graph holding ONE candidate region,
#  so the graph IS the holon — the region is the closure boundary.
#
#  Known weakness (stated, not hidden): CONTAINS can let a lost
#  word pass if it coincidentally occurs inside another label. It
#  cannot pass a word absent from every label and every caption.
#################################################################

tab:HeaderContentConservedShape a sh:NodeShape ;
    sh:targetClass tab:HeaderSourceCell ;
    sh:sparql [
        sh:message "Header-region source cell is not accounted for: neither merged into an asserted header label nor carried as a region caption." ;
        sh:prefixes tab:prefixes ;
        sh:select """
            SELECT $this WHERE {
                $this tab:sourceText ?txt .
                FILTER NOT EXISTS { ?lc a tab:LabelCell ; tab:cellText ?lt . FILTER(CONTAINS(?lt, ?txt)) }
                FILTER NOT EXISTS { ?cap a tab:RegionCaption ; tab:captionText ?ct . FILTER(CONTAINS(?ct, ?txt)) }
            }
        """ ] .
```

- [ ] **Step 6: Wire the shape into `region_tiles`**

In `src/iladub/etkl/tiling.py`, replace lines 17-19:

```python
_TILING_SHAPE_IRIS = [TAB.CoverageShape, TAB.NoOverlapShape, TAB.RefinementShape,
                      TAB.RowCoverageShape, TAB.RowNoOverlapShape, TAB.RowRefinementShape,
                      TAB.UnambiguousAccessShape, TAB.UnambiguousRowAccessShape]
```

with:

```python
# The eight tiling invariants (loop C, 2026-07-16) + the header-content conservation oracle
# (loop C of the GrainCorp push, 2026-07-26). One pySHACL call carries both families; the
# conservation shape targets tab:HeaderSourceCell, which no pre-existing region emits, so
# every shipped region is unaffected.
_TILING_SHAPE_IRIS = [TAB.CoverageShape, TAB.NoOverlapShape, TAB.RefinementShape,
                      TAB.RowCoverageShape, TAB.RowNoOverlapShape, TAB.RowRefinementShape,
                      TAB.UnambiguousAccessShape, TAB.UnambiguousRowAccessShape,
                      TAB.HeaderContentConservedShape]
```

Also update the `_build_tiling_shapes` docstring: change `"""The eight tiling shapes extracted` to `"""The eight tiling shapes + the header-content conservation shape, extracted`.

- [ ] **Step 7: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_conservation_shape.py -q`
Expected: **4 passed.**

- [ ] **Step 8: Verify zero regression in the existing tiling/gate suites**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_tiling_gate.py tests/etkl/test_transform_gate.py tests/etkl/test_tab_vocab.py tests/test_source_ownership.py -q`
Expected: all pass. `test_no_tuned_constant_in_tiling` must still pass (we added no numeric literal). If `test_source_ownership.py` fails, a `holon:` IRI leaked in as a subject — fix the TTL, do not weaken the test.

- [ ] **Step 9: Commit**

```bash
git add vocab/ontology/tab.ttl vocab/shapes/tab-shapes.ttl src/iladub/etkl/tiling.py tests/etkl/test_conservation_shape.py
git commit -m "feat(etkl): header-content conservation SHACL oracle (loop C foundation)"
```

---

### Task 2: The injected proposer seam + BAML function

**Files:**
- Modify: `src/iladub/etkl/propose.py` (append at end)
- Create: `baml_src/header_rowrole.baml`
- Test: `tests/etkl/test_rowrole_proposer.py` (create)

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces:
  - `RowRoleProposal(roles: tuple[str, ...], confidence: float, rationale: str, suggester_iri: str = "urn:iladub:suggester/recorded-rowrole-proposer")` — frozen dataclass.
  - `RowRoleProposer` Protocol with `propose_header_row_roles(context: dict) -> RowRoleProposal | None`.
  - `FakeRowRoleProposer(proposal: RowRoleProposal | None)` — returns its fixed proposal.
  - `BamlRowRoleProposer()` — live path; `suggester_iri="urn:iladub:suggester/baml.ProposeHeaderRowRoles"`.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_rowrole_proposer.py`:

```python
"""Loop C — the injected row-role proposer seam. All logic is offline-testable via the
Fake; the live BAML path is lazy + env-gated. See spec §3.2."""
from iladub.etkl.propose import (BamlRowRoleProposer, FakeRowRoleProposer,
                                 RowRoleProposal, baml_proposer_available)


def test_fake_proposer_returns_its_fixed_proposal():
    p = RowRoleProposal(("furniture", "continuation"), 0.8, "date line, then a wrapped label")
    fake = FakeRowRoleProposer(p)
    assert fake.propose_header_row_roles({"rows": [], "leaf_labels": []}) is p


def test_fake_proposer_can_abstain():
    assert FakeRowRoleProposer(None).propose_header_row_roles({}) is None


def test_proposal_defaults_to_the_recorded_suggester_iri():
    p = RowRoleProposal(("level",), 0.5, "genuine group label")
    assert p.suggester_iri == "urn:iladub:suggester/recorded-rowrole-proposer"


def test_baml_proposer_constructs_without_baml_client():
    # lazy import guard: constructing the live proposer must never import baml_client
    # (mirrors BamlSpanProposer). Only CALLING it does.
    assert BamlRowRoleProposer() is not None


def test_live_path_is_env_gated():
    # the shipped gate: BAML_LIVE must be explicitly "1" AND baml_client importable
    import os
    if os.environ.get("BAML_LIVE") != "1":
        assert baml_proposer_available() is False
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_proposer.py -q`
Expected: **collection error** — `ImportError: cannot import name 'BamlRowRoleProposer' from 'iladub.etkl.propose'`.

- [ ] **Step 3: Append the seam to `src/iladub/etkl/propose.py`**

Append at the end of the file:

```python
@dataclass(frozen=True)
class RowRoleProposal:
    """A proposed reading of a table's header region (loop C). `roles` is parallel to the
    NON-LEAF header rows, top to bottom; each entry is 'furniture' (document furniture — a
    title/date line, carried as a tab:RegionCaption), 'continuation' (a wrap fragment whose
    text merges into the leaf label of its column) or 'level' (a genuine hierarchical parent).

    The reading is a PROPOSITION (§3): admitted only via a PromotionDecision after region_tiles
    confirms it is structurally legal AND lossless — never asserted as grounded truth. Geometry
    cannot decide it (a caption and an off-center merge are structurally identical, and the
    wrap-pitch ratio fails when header leading equals body leading), and no oracle can rank two
    legal readings — hence NEURAL."""
    roles: tuple[str, ...]
    confidence: float
    rationale: str
    suggester_iri: str = "urn:iladub:suggester/recorded-rowrole-proposer"


class RowRoleProposer(Protocol):
    def propose_header_row_roles(self, context: dict) -> "RowRoleProposal | None": ...


@dataclass(frozen=True)
class FakeRowRoleProposer:
    """Deterministic offline row-role proposer for tests/showcase. Returns its fixed proposal
    (or None to model abstention)."""
    proposal: "RowRoleProposal | None"

    def propose_header_row_roles(self, context):
        return self.proposal


class BamlRowRoleProposer:
    """Live row-role proposer — calls the BAML ProposeHeaderRowRoles function. Lazy: baml_client
    is imported only inside the method, so constructing this never triggers the version guard.
    NEURAL propose seam; env-gated by baml_proposer_available()."""

    def propose_header_row_roles(self, context):
        from baml_client import sync_client
        r = sync_client.b.ProposeHeaderRowRoles(
            context.get("rows"),
            context.get("leaf_labels"),
            context.get("row_columns"),
        )
        return RowRoleProposal(
            roles=tuple(r.roles),
            confidence=r.confidence,
            rationale=r.rationale,
            suggester_iri="urn:iladub:suggester/baml.ProposeHeaderRowRoles",
        )
```

- [ ] **Step 4: Create `baml_src/header_rowrole.baml`**

```baml
class HeaderRowRoleProposal {
  roles string[] @description("exactly one of furniture|continuation|level per non-leaf header row, in the same top-to-bottom order as the input rows")
  confidence float @description("0.0-1.0, calibrated confidence in the whole reading")
  rationale string @description("one sentence per row on why")
}

function ProposeHeaderRowRoles(
  rows: string[][], leaf_labels: string[], row_columns: int[][]
) -> HeaderRowRoleProposal {
  client Claude
  prompt #"
    A table's header region was read as several rows of text. The BOTTOM row holds the
    column labels (one per column): {{ leaf_labels }}.

    The rows ABOVE it are: {{ rows }}, and for each of their cells the column index the cell
    sits over is: {{ row_columns }}.

    Classify EACH row above the bottom row, top to bottom, as exactly one of:
      - "furniture"    — not part of the table: a report date, a title, a page number.
      - "continuation" — a wrapped fragment of the column label below it; joining it to that
                         label (fragment first) produces the real column name.
      - "level"        — a genuine hierarchical group label spanning several columns, where the
                         labels below it are its sub-columns.

    Use the column indices to see WHICH label a fragment would complete: a fragment sitting over
    the same column as a label below it, that reads as the start of a longer name, is a
    "continuation". Prefer "continuation" over "furniture" whenever a fragment plausibly reads as
    part of a label — "furniture" discards text from the table, so it is the lossy answer and must
    be reserved for lines that genuinely are not header content.

    Return one role per row above the bottom row, in order.
    {{ ctx.output_format }}
  "#
}
```

- [ ] **Step 5: Verify the BAML class matches the Python seam's field types**

The three `HeaderRowRoleProposal` fields must line up with `RowRoleProposal`: `roles` → `string[]` /
`tuple[str, ...]`, `confidence` → `float` / `float`, `rationale` → `string` / `str`. A mismatch here
surfaces only on the live path (which is env-gated off), so check it now rather than later.

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && grep -nE "roles|confidence|rationale" baml_src/header_rowrole.baml | head -5
```
Expected: `roles string[]`, `confidence float`, `rationale string` — in that order.

- [ ] **Step 6: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_proposer.py tests/etkl/test_propose.py -q`
Expected: all pass (5 new + the existing `test_propose.py`).

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/propose.py baml_src/header_rowrole.baml tests/etkl/test_rowrole_proposer.py
git commit -m "feat(etkl): RowRoleProposer seam + ProposeHeaderRowRoles BAML function (loop C)"
```

---

### Task 3: `build_row_reading` — the pure structural rewrite

**Files:**
- Modify: `src/iladub/etkl/headers.py:379-451` (refactor: extract two helpers, zero behaviour change)
- Create: `src/iladub/etkl/rowrole.py`
- Test: `tests/etkl/test_rowrole_reading.py` (create)

**Interfaces:**
- Consumes: `iladub.etkl.propose.RowRoleProposal` (Task 2, only for the role strings).
- Produces:
  - `headers.header_rows_of(band, grid, body_line) -> list[list[SourceCell]]` — the header rows (may be empty).
  - `headers._tree_from_rows(header_rows, grid) -> tuple[HeaderNode, ...]` — the covering/repair/flank/parent-link pipeline over a given row list.
  - `rowrole.ROLES = ("furniture", "continuation", "level")`
  - `rowrole.row_role_context(header_rows, grid) -> dict` with keys `rows: list[list[str]]`, `leaf_labels: list[str]`, `row_columns: list[list[int]]`.
  - `rowrole.build_row_reading(header_rows, grid, roles) -> tuple | None` returning `(nodes, captions, source_cells)` where `nodes: tuple[HeaderNode, ...]`, `captions: tuple[tuple[int, str], ...]`, `source_cells: tuple[tuple[int, str], ...]`; `None` means refuse.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_rowrole_reading.py`:

```python
"""Loop C — build_row_reading: the pure structural rewrite under a proposed role vector.

The fixture reproduces GrainCorp's shape: a leaked caption row, a wrap-continuation row, and a
leaf label row, with UNIFORM 12pt line spacing so group_wrapped's 0.9x-lead threshold (10.8pt)
cannot absorb the header rows — the exact condition where header leading equals body leading.
Verified during planning: merge_tiling_ok is False before, True under the intended reading.
See docs/superpowers/specs/2026-07-26-header-row-roles-design.md.
"""
from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Word
from iladub.etkl.grid import LeafGrid
from iladub.etkl.headers import (header_body_split, header_rows_of, infer_header_tree,
                                 merge_tiling_ok)
from iladub.etkl.rowrole import build_row_reading, row_role_context

GRID = LeafGrid((100.0, 150.0, 200.0, 250.0, 300.0), 4, 50.0, 1.0)


def _w(t, x0, x1, top):
    return Word(t, x0, x1, top, top + 10.0)


def _line(words, top):
    return Line(tuple(words), top, top + 10.0)


def caption_and_wrap_band():
    """Row 0 = a leaked date caption, row 1 = a wrap fragment over column 1, row 2 = the leaf
    labels, rows 3-4 = body. Coordinates are load-bearing — do not change them."""
    cap = [_w("Monday", 205, 240, 0.0), _w("5 May", 242, 262, 0.0)]
    wrap = [_w("Unit", 155, 175, 12.0)]
    leaf = [_w("Item", 110, 140, 24.0), _w("Ref", 155, 172, 24.0),
            _w("Qty", 205, 230, 24.0), _w("Cost", 255, 285, 24.0)]
    d1 = [_w("aa", 110, 140, 36.0), _w("R1", 155, 172, 36.0),
          _w("10", 205, 230, 36.0), _w("1.5", 255, 285, 36.0)]
    d2 = [_w("bb", 110, 140, 48.0), _w("R2", 155, 172, 48.0),
          _w("20", 205, 230, 48.0), _w("2.5", 255, 285, 48.0)]
    return Band((_line(cap, 0.0), _line(wrap, 12.0), _line(leaf, 24.0),
                 _line(d1, 36.0), _line(d2, 48.0)), 0.0, 58.0)


def test_fixture_reproduces_the_escalation():
    # the red condition: the geometric tree does NOT tile (level-0 overlap on column 2)
    band = caption_and_wrap_band()
    assert header_body_split(band, GRID) == 3
    assert merge_tiling_ok(infer_header_tree(band, GRID, 3), GRID) is False


def test_header_rows_of_returns_three_unabsorbed_header_rows():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    assert [len(r) for r in rows] == [2, 1, 4]


def test_context_reports_geometry_without_deciding():
    ctx = row_role_context(header_rows_of(caption_and_wrap_band(), GRID, 3), GRID)
    assert ctx["rows"] == [["Monday", "5 May"], ["Unit"]]        # non-leaf rows only
    assert ctx["leaf_labels"] == ["Item", "Ref", "Qty", "Cost"]
    assert ctx["row_columns"] == [[2, 3], [1]]                   # ink-center columns


def test_furniture_plus_continuation_tiles_with_the_merged_label():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    out = build_row_reading(rows, GRID, ("furniture", "continuation"))
    assert out is not None
    nodes, captions, source_cells = out
    assert [n.text for n in nodes] == ["Item", "Unit Ref", "Qty", "Cost"]
    assert merge_tiling_ok(nodes, GRID) is True
    assert captions == ((0, "Monday"), (0, "5 May"))
    # every header-region cell is recorded for the conservation oracle (2 + 1 + 4)
    assert len(source_cells) == 7


def test_all_level_reproduces_the_failing_tree():
    # the contract guard at the unit level: reading every row as a genuine level must NOT
    # invent a tiling — it reproduces today's tree and stays illegal.
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    nodes, _caps, _src = build_row_reading(rows, GRID, ("level", "level"))
    assert merge_tiling_ok(nodes, GRID) is False


def test_wrong_length_role_vector_is_refused():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    assert build_row_reading(rows, GRID, ("furniture",)) is None


def test_unknown_role_is_refused():
    rows = header_rows_of(caption_and_wrap_band(), GRID, 3)
    assert build_row_reading(rows, GRID, ("furniture", "wrap")) is None


def test_unplaceable_continuation_is_refused():
    # "Monday"/"5 May" sit over columns 2 and 3; reading row 0 as a continuation is placeable.
    # Reading row 1 ("Unit", column 1) as a continuation while ALSO removing column 1's leaf
    # label is not expressible here, so instead assert the guard directly: a continuation cell
    # over a column no leaf node covers is refused.
    band = caption_and_wrap_band()
    rows = header_rows_of(band, GRID, 3)
    # drop the leaf label that covers column 1, leaving column 1 uncovered at the leaf level
    stripped = [rows[0], rows[1], [c for c in rows[2] if c.text != "Ref"]]
    assert build_row_reading(stripped, GRID, ("furniture", "continuation")) is None
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_reading.py -q`
Expected: **collection error** — `ImportError: cannot import name 'header_rows_of' from 'iladub.etkl.headers'`.

- [ ] **Step 3: Refactor `headers.py` — extract the two helpers (zero behaviour change)**

In `src/iladub/etkl/headers.py`, replace the whole `infer_header_tree` function (currently lines 379-451) with these three functions:

```python
def header_rows_of(band: Band, grid: LeafGrid, body_line: int) -> list:
    """The header rows (wrapped cell rows whose first cell precedes the body line), top to bottom.

    Calls group_wrapped on the FULL band so the body-row pitch (not the narrow header-only pitch)
    governs the wrap-continuation threshold — correctly absorbing tight (SI) lines into their
    parent sub-header cells rather than producing a spurious extra level.

    KNOWN LIMIT (the reason loop C exists): when the header's leading EQUALS the body's leading
    (measured on the GrainCorp report: 6.6pt vs 6.5pt), the 0.9x-lead threshold cannot fire and
    genuine wrap-continuation rows survive as separate rows. That ratio must NOT be tuned — which
    row is a wrap fragment is a reading judgment, decided by the NEURAL row-role proposer
    (rowrole.py) once the resulting tree fails to tile.

    Using row[0].top (not max) is safe because header rows are compact; if the first
    (leftmost-column) cell precedes body_top, the row is a header row.
    """
    all_rows = group_wrapped(band, grid)
    body_top = band.lines[body_line].top
    return [row for row in all_rows if row and row[0].top < body_top]


def _tree_from_rows(header_rows, grid: LeafGrid) -> tuple[HeaderNode, ...]:
    """The header tree over a GIVEN list of header rows (top to bottom; the last is the leaf row).

    LEAF row covering is a body-grounded AXIOM: a leaf label covers the one column that CONTAINS
    its ink center (header-covers.rq). This replaces the "Merge & Center" ink-extent symmetrization
    for leaves only, which over-spanned wide single-column labels (e.g. "Reference Number").
    Parent rows keep _covers_for_cell + repair_coverage (the centering-bounded run extension,
    B1.1). A leaf column with no leaf label whose center lands in it stays uncovered here — it may
    be a terminal "short parent" covered by a shallower node (which repair_coverage / the parent
    path resolves), or a genuine gap that correctly fails to tile -> honest escalation.

    Factored out of infer_header_tree so the loop-C NEURAL slice (rowrole.build_row_reading) can
    build the same tree over a FILTERED row list without duplicating this pipeline.
    """
    b = grid.boundaries
    leaf_lvl = len(header_rows) - 1
    covers_map = run_covers(HEADER_COVERS_RQ, header_evidence(header_rows, grid))

    nodes: list[HeaderNode] = []
    for lvl, row in enumerate(header_rows):
        for j, cell in enumerate(row):
            cx = (cell.x0 + cell.x1) / 2.0
            if lvl == leaf_lvl:
                covers = covers_map.get((lvl, j), ())    # SPARQL leaf covering
            else:
                covers = _covers_for_cell(cell, b)        # parent path, unchanged
            nodes.append(HeaderNode(lvl, covers, cell.text, None, cx))

    nodes = repair_coverage(nodes, grid)   # non-leaf levels only (B1.1); leaf covers preserved

    # B1.2 — narrow-flank tie detect -> escalate (PROCEDURAL; see resolve_narrow_flanks).
    ink_cols_by_node = []
    for lvl, row in enumerate(header_rows):
        for cell in row:
            lo = column_of(cell.x0 + 0.1, b)
            hi = column_of(cell.x1 - 0.1, b)
            ink_cols_by_node.append(tuple(range(min(lo, hi), max(lo, hi) + 1)))
    nodes = resolve_narrow_flanks(nodes, grid, ink_cols_by_node)

    # Link each node to its nearest parent (level − 1 whose covers ⊇ this node's).
    # Break after the first match so the first qualifying parent wins deterministically
    # (nodes are ordered top-to-bottom, left-to-right, so "first" = leftmost ancestor
    # at the parent level whose covers contain this node's covers).
    linked: list[HeaderNode] = []
    for n in nodes:
        parent_idx: int | None = None
        for j, m in enumerate(nodes):
            if m.level == n.level - 1 and set(n.covers) <= set(m.covers):
                parent_idx = j
                break
        linked.append(HeaderNode(n.level, n.covers, n.text, parent_idx,
                                 n.center_x, n.ambiguous, n.ambiguous_flank))
    return tuple(linked)


def infer_header_tree(band: Band, grid: LeafGrid, body_line: int) -> tuple[HeaderNode, ...] | None:
    """Header-tree from the header lines (0..body_line-1). Returns None if no header rows are
    identified (ambiguous → escalate). See header_rows_of + _tree_from_rows."""
    header_rows = header_rows_of(band, grid, body_line)
    if not header_rows:
        return None
    return _tree_from_rows(header_rows, grid)
```

- [ ] **Step 4: Prove the refactor changed nothing**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: **all pass** except the not-yet-implemented `tests/etkl/test_rowrole_reading.py` (which still fails on `from iladub.etkl.rowrole import …`). If ANY other test changed status, the extraction was not faithful — re-read `git diff src/iladub/etkl/headers.py` and fix. Do not proceed with a regression.

- [ ] **Step 5: Create `src/iladub/etkl/rowrole.py`**

```python
"""rowrole — loop C NEURAL header-region row roles: propose -> tile+conserve oracle -> promote.

§8 gate: this module hosts the NEURAL slice. WHICH role a header-region row has is NOT decided
here — a RowRoleProposer (BAML, injected) proposes it and region_tiles (SHACL: the eight tiling
shapes + HeaderContentConservedShape) disposes it; a legal, lossless reading is admitted only as a
PromotionDecision proposition (§3).

Why NEURAL and not geometry: loop B proved a leaked caption and a genuinely-ambiguous off-center
merge are structurally identical (both are overlapping top rows), so no geometric peel is sound;
and headers.header_rows_of's 0.9x-lead wrap threshold cannot fire when a document's header leading
equals its body leading (measured on GrainCorp: 6.6pt vs 6.5pt). Both are reading judgments.

The honest limit (spec §2 Finding 5): tiling CANNOT discriminate 'furniture' from 'continuation' —
both readings tile, and both conserve (furniture text is carried as a caption). That residue is
irreducibly NEURAL; the epistemics (proposition + accountable promotion + recorded rationale)
govern it, not an oracle. Hence: ONE proposal, ONE disposal, NO search — 'all furniture' is always
legal, so any search over the role space would converge on it and strip real header labels.

row_role_context and build_row_reading are pure structural reads/rewrites: no geometry decision,
no tuned constant.
"""
from __future__ import annotations

from dataclasses import replace

from rdflib import Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from .headers import _tree_from_rows
from .regions import column_of

TAB = Namespace("https://w3id.org/iladub/tab#")

ROLES = ("furniture", "continuation", "level")


def row_role_context(header_rows, grid) -> dict:
    """The proposer's inputs, read off the header rows. Reports geometry; decides nothing.

    rows         — the NON-LEAF rows' cell texts, top to bottom.
    leaf_labels  — the leaf (bottom) row's cell texts, left to right.
    row_columns  — per non-leaf cell, the column index containing its ink center (the same
                   half-open containment header-covers.rq uses for leaf labels), so the model can
                   see WHICH label a fragment would complete.
    """
    b = grid.boundaries
    non_leaf = list(header_rows[:-1])
    return {
        "rows": [[c.text for c in row] for row in non_leaf],
        "leaf_labels": [c.text for c in header_rows[-1]],
        "row_columns": [[column_of((c.x0 + c.x1) / 2.0, b) for c in row] for row in non_leaf],
    }


def build_row_reading(header_rows, grid, roles):
    """Rewrite the header tree under a proposed role vector. Pure structural rewrite — no
    geometry decision, no tuned constant. Returns (nodes, captions, source_cells), or None to
    REFUSE (a malformed vector, or a continuation fragment that cannot be placed).

    level        -> the row stays a header level and flows through the UNCHANGED
                    _covers_for_cell + repair_coverage + resolve_narrow_flanks pipeline, so
                    genuine merged parents (the 'Prior Visit' pivot shape) are untouched.
    continuation -> the row contributes NO level; its cells' texts are prefixed, in top-to-bottom
                    source order, onto the leaf label covering the column that contains each
                    cell's ink center. Collected first and applied once, so multiple continuation
                    rows compose in reading order ('Date of Grain' + 'Loading' + 'Commencement').
    furniture    -> the row contributes NO level; its cells become tab:RegionCaption records, so
                    the text is CARRIED, never dropped (CLAUDE.md §5/§7).

    The leaf row is never classified — it is always the leaf, and its covering stays loop B's
    header-covers.rq AXIOM.
    """
    non_leaf = list(header_rows[:-1])
    if len(roles) != len(non_leaf) or any(r not in ROLES for r in roles):
        return None                            # malformed vector -> refuse

    kept = [row for row, role in zip(non_leaf, roles) if role == "level"] + [header_rows[-1]]
    nodes = list(_tree_from_rows(kept, grid))
    leaf_lvl = len(kept) - 1

    # Collect continuation fragments per column FIRST (top-to-bottom), then prefix once.
    b = grid.boundaries
    extra: dict[int, list[str]] = {}
    for row, role in zip(non_leaf, roles):
        if role != "continuation":
            continue
        for cell in row:
            extra.setdefault(column_of((cell.x0 + cell.x1) / 2.0, b), []).append(cell.text)

    for col, texts in extra.items():
        tgt = next((i for i, n in enumerate(nodes)
                    if n.level == leaf_lvl and col in n.covers), None)
        if tgt is None:
            return None                        # unplaceable continuation -> refuse (spec §3.1)
        merged = (" ".join(texts) + " " + nodes[tgt].text).strip()
        nodes[tgt] = replace(nodes[tgt], text=merged)

    captions = tuple((r, cell.text)
                     for r, (row, role) in enumerate(zip(non_leaf, roles))
                     if role == "furniture"
                     for cell in row)
    source_cells = tuple((r, cell.text)
                         for r, row in enumerate(header_rows)
                         for cell in row)
    return tuple(nodes), captions, source_cells


def emit_reading_evidence(g, table_uri, captions, source_cells):
    """Commit the reading's accountability evidence: one tab:RegionCaption per furniture cell
    (so furniture text is carried, not dropped) and one tab:HeaderSourceCell per header-region
    cell — the target of tab:HeaderContentConservedShape, which refuses any reading that loses a
    word. Region-bound; the region is the closure boundary."""
    for k, (row, text) in enumerate(captions):
        cap = URIRef("%s-cap%d" % (table_uri, k))
        g.add((cap, RDF.type, TAB.RegionCaption))
        g.add((cap, TAB.captionText, Literal(text)))
        g.add((cap, TAB.captionRow, Literal(row, datatype=XSD.integer)))
        g.add((table_uri, TAB.hasCaption, cap))
    for k, (row, text) in enumerate(source_cells):
        sc = URIRef("%s-hsc%d" % (table_uri, k))
        g.add((sc, RDF.type, TAB.HeaderSourceCell))
        g.add((sc, TAB.sourceText, Literal(text)))
        g.add((sc, TAB.sourceRow, Literal(row, datatype=XSD.integer)))
        g.add((table_uri, TAB.hasHeaderSourceCell, sc))
```

- [ ] **Step 6: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_reading.py -q`
Expected: **9 passed.**

If `test_context_reports_geometry_without_deciding` fails on `row_columns`, print the actual value and reconcile the expectation with the measured ink centers — do NOT change `column_of`.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/headers.py src/iladub/etkl/rowrole.py tests/etkl/test_rowrole_reading.py
git commit -m "feat(etkl): build_row_reading — structural rewrite under a proposed role vector (loop C)"
```

---

### Task 4: The driver — propose → oracle → promote

**Files:**
- Modify: `src/iladub/etkl/rowrole.py` (append `resolve_header_row_roles`)
- Modify: `src/iladub/etkl/promote.py` (append `emit_row_role_promotion`)
- Test: `tests/etkl/test_rowrole_resolution.py` (create)

**Interfaces:**
- Consumes: `rowrole.row_role_context`, `rowrole.build_row_reading`, `rowrole.emit_reading_evidence` (Task 3); `tiling.region_tiles` with the conservation shape (Task 1); `propose.FakeRowRoleProposer`, `propose.RowRoleProposal` (Task 2); the existing `holon.assert_hier_region`, `headers.header_rows_of`.
- Produces:
  - `promote.emit_row_role_promotion(g, region_uri, row_index, role, texts, proposal) -> URIRef`
  - `rowrole.resolve_header_row_roles(graph, hreg, band, table_uri, doc_uri, page, proposer) -> tuple[int, tuple[URIRef, ...]] | None`

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_rowrole_resolution.py`:

```python
"""Loop C — the driver: NEURAL propose -> tiling+conservation oracle -> promote.

Legality gates admission, never confidence. On any refusal the graph MUST be untouched and the
caller escalates MERGE_AMBIGUOUS. See spec §3.1.
"""
from rdflib import Graph, Namespace, RDF, URIRef

from iladub.etkl.hierarchical import classify_hierarchical
from iladub.etkl.headers import merge_tiling_ok
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
from iladub.etkl.rowrole import resolve_header_row_roles
from tests.etkl.test_rowrole_reading import GRID, caption_and_wrap_band

ILADUB = Namespace("https://w3id.org/iladub#")
TAB = Namespace("https://w3id.org/iladub/tab#")
_T = URIRef("urn:doc#htable0")
_D = URIRef("urn:doc")


def _hreg_and_band():
    band = caption_and_wrap_band()
    hreg = classify_hierarchical(band)
    assert hreg is not None
    assert merge_tiling_ok(hreg.tree, hreg.grid) is False, "fixture must start escalating"
    return hreg, band


def _resolve(roles, confidence=0.8):
    hreg, band = _hreg_and_band()
    g = Graph()
    prop = None if roles is None else RowRoleProposal(roles, confidence, "test rationale")
    out = resolve_header_row_roles(g, hreg, band, _T, _D, 0, FakeRowRoleProposer(prop))
    return g, out


def test_legal_reading_asserts_with_promotions():
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None, "a legal, lossless reading must resolve"
    n_asserted, promos = out
    assert n_asserted > 0
    assert len(promos) == 2, "one promotion per classified non-leaf row"
    assert list(g.subjects(RDF.type, ILADUB.PromotionDecision))
    # the reading is a PROPOSITION, not an assertion of ground truth
    assert list(g.subjects(RDF.type, ILADUB.CandidateConcept))


def test_furniture_text_is_carried_as_a_caption():
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None
    caps = {str(o) for _s, _p, o in g.triples((None, TAB.captionText, None))}
    assert caps == {"Monday", "5 May"}, caps


def test_merged_label_reaches_the_committed_graph():
    g, out = _resolve(("furniture", "continuation"))
    assert out is not None
    labels = {str(o) for _s, _p, o in g.triples((None, TAB.cellText, None))}
    assert "Unit Ref" in labels, labels


def test_abstaining_proposer_does_not_resolve():
    g, out = _resolve(None)
    assert out is None
    assert len(g) == 0, "graph must be untouched on refusal"


def test_all_level_reading_is_refused_by_the_oracle():
    # THE CONTRACT GUARD: an honest 'level' reading reproduces the illegal tree; the oracle
    # refuses it and the region escalates. High confidence must not rescue it.
    g, out = _resolve(("level", "level"), confidence=0.99)
    assert out is None, "an illegal reading must be refused regardless of confidence"
    assert len(g) == 0, "graph must be untouched on refusal"


def test_malformed_role_vector_is_refused():
    g, out = _resolve(("furniture",))          # wrong length
    assert out is None
    assert len(g) == 0


def test_unknown_role_is_refused():
    g, out = _resolve(("furniture", "wrap"))
    assert out is None
    assert len(g) == 0


def test_single_header_row_never_calls_the_proposer():
    # k == 0: nothing to classify -> return None without consulting the proposer.
    class _Exploding:
        def propose_header_row_roles(self, context):
            raise AssertionError("proposer must not be called when there are no non-leaf rows")

    from iladub.etkl.bands import Band
    from iladub.etkl.geometry import Line, Word
    from iladub.etkl.hierarchical import HierRegion

    def _w(t, x0, x1, top):
        return Word(t, x0, x1, top, top + 10.0)

    def _line(ws, top):
        return Line(tuple(ws), top, top + 10.0)

    leaf = [_w("Item", 110, 140, 0.0), _w("Ref", 155, 172, 0.0),
            _w("Qty", 205, 230, 0.0), _w("Cost", 255, 285, 0.0)]
    d1 = [_w("aa", 110, 140, 12.0), _w("R1", 155, 172, 12.0),
          _w("10", 205, 230, 12.0), _w("1.5", 255, 285, 12.0)]
    band = Band((_line(leaf, 0.0), _line(d1, 12.0)), 0.0, 22.0)
    hreg = classify_hierarchical(band)
    if hreg is None:                            # a 2-line band may not classify; skip if so
        return
    g = Graph()
    out = resolve_header_row_roles(g, hreg, band, _T, _D, 0, _Exploding())
    assert out is None
    assert len(g) == 0
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_resolution.py -q`
Expected: **collection error** — `ImportError: cannot import name 'resolve_header_row_roles' from 'iladub.etkl.rowrole'`.

- [ ] **Step 3: Append `emit_row_role_promotion` to `src/iladub/etkl/promote.py`**

```python
def emit_row_role_promotion(g, region_uri, row_index, role, texts, proposal):
    """Write the CandidateConcept + PromotionDecision for a NEURAL header-region row-role reading
    (loop C). The reading is a PROPOSITION: region_tiles (tiling + content conservation) has
    confirmed it is structurally LEGAL and LOSSLESS, but no oracle can rank two legal readings —
    'furniture' and 'continuation' both tile and both conserve — so it is admitted accountably,
    never asserted as grounded truth (§3). Returns the PromotionDecision uri."""
    agent = _suggester(g, proposal)
    confidence = Literal(Decimal(str(round(proposal.confidence, 6))))
    surface = " ".join(texts)

    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal("header row %d read as %s" % (row_index, role))))
    g.add((cand, ILADUB.surfaceText, Literal(surface)))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.suggestedAnchor, GIST.Category))
    g.add((cand, ILADUB.fromRegion, region_uri))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    g.add((cand, ILADUB.confidence, confidence))

    pd = URIRef("%s-rowrole-promotion-r%d-%s" % (region_uri, row_index, _slug(role)))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, region_uri))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, confidence))
    g.add((pd, DEC.rationale, Literal(
        "Header-region row %d ('%s') read as '%s'. Geometry cannot decide this (a caption and an "
        "off-center merge are structurally identical, and the wrap-pitch threshold cannot fire "
        "when header leading equals body leading); region_tiles confirms the reading is "
        "structurally legal and loses no source text, but NOT that it is unique — admitted as a "
        "proposition. Rationale: %s" % (row_index, surface, role, proposal.rationale))))
    g.add((pd, DEC.produced, region_uri))
    return pd
```

- [ ] **Step 4: Append `resolve_header_row_roles` to `src/iladub/etkl/rowrole.py`**

```python
def resolve_header_row_roles(graph, hreg, band, table_uri, doc_uri, page, proposer):
    """NEURAL propose -> SHACL-oracle dispose -> promote for a header region whose geometric tree
    does not tile (loop C). The direct analogue of span.resolve_ambiguous_merge.

    ONE proposal, ONE disposal, NO search (see the module docstring: 'all furniture' is always
    legal, so search would converge on it and strip real header labels). Returns
    (asserted_token_count, (promotion_uri, ...)) on success, or None -> the caller escalates
    MERGE_AMBIGUOUS with `graph` untouched.

    Legality gates admission, never confidence: a reading whose scratch region fails region_tiles
    (the eight tiling shapes OR HeaderContentConservedShape) is refused regardless of
    proposal.confidence.
    """
    from dataclasses import replace as _replace
    from rdflib import Graph
    from .headers import header_rows_of
    from .holon import assert_hier_region
    from .promote import emit_row_role_promotion
    from .tiling import region_tiles

    header_rows = header_rows_of(band, hreg.grid, hreg.body_line)
    if len(header_rows) < 2:
        return None                            # no non-leaf row to classify -> caller escalates

    proposal = proposer.propose_header_row_roles(row_role_context(header_rows, hreg.grid))
    if proposal is None:
        return None                            # abstain -> escalate

    built = build_row_reading(header_rows, hreg.grid, tuple(proposal.roles))
    if built is None:
        return None                            # malformed / unplaceable -> escalate
    nodes, captions, source_cells = built

    scratch = Graph()
    n = assert_hier_region(scratch, _replace(hreg, tree=nodes), band, table_uri, doc_uri, page)
    emit_reading_evidence(scratch, table_uri, captions, source_cells)
    if n <= 0 or not region_tiles(scratch):
        return None                            # illegal or lossy -> oracle refuses -> escalate

    graph += scratch
    promo_uris = tuple(
        emit_row_role_promotion(graph, table_uri, r, role, [c.text for c in header_rows[r]], proposal)
        for r, role in enumerate(proposal.roles)
    )
    return n, promo_uris
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_resolution.py -q`
Expected: **8 passed.**

If `test_all_level_reading_is_refused_by_the_oracle` fails (i.e. the reading resolved), the oracle is not refusing an illegal tree — check that `assert_hier_region` + `region_tiles` see the overlap; do NOT relax the test.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/rowrole.py src/iladub/etkl/promote.py tests/etkl/test_rowrole_resolution.py
git commit -m "feat(etkl): resolve_header_row_roles — NEURAL propose/oracle/promote driver (loop C)"
```

---

### Task 5: `compile_tables` integration + the contract guard

**Files:**
- Modify: `src/iladub/etkl/compile.py:74-75` (signature) and the hierarchical tiling-failure branch (currently around lines 224-231)
- Test: `tests/etkl/test_rowrole_integration.py` (create)

**Interfaces:**
- Consumes: `rowrole.resolve_header_row_roles` (Task 4).
- Produces: `compile_tables(pdf_path, page_number=0, validate_shapes=True, span_proposer=None, row_role_proposer=None) -> CompilationReport`.

- [ ] **Step 1: Write the failing test**

Create `tests/etkl/test_rowrole_integration.py`:

```python
"""Loop C — compile_tables wiring. The default path is unchanged; the NEURAL slice fires only
on a tiling failure with an injected proposer; and a genuine off-center merge STILL escalates
even with a proposer present (the contract a geometric peel broke in loop B)."""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from iladub.etkl import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
from tests.etkl import fixtures as F


def _reasons(rep):
    return [r.reason for r in rep.regions]


def _verdicts(rep):
    return [r.verdict for r in rep.regions]


def test_compile_tables_accepts_row_role_proposer_kw(tmp_path):
    # signature smoke: the new optional kw exists and the default path is unchanged
    p = os.path.join(str(tmp_path), "simple.pdf")
    F.simple_table_pdf(p)
    assert "asserted" in _verdicts(compile_tables(p))
    assert "asserted" in _verdicts(compile_tables(p, row_role_proposer=None))


def test_offcenter_merge_still_escalates_with_a_proposer(tmp_path):
    # THE CONTRACT GUARD. Loop B's geometric caption peel broke exactly this: a genuinely
    # ambiguous off-center merge must NOT be silently asserted. With the proposer answering
    # honestly ('level' for every non-leaf row), the oracle refuses and the region escalates.
    p = os.path.join(str(tmp_path), "offcenter.pdf")
    F.offcenter_merge_report_pdf(p)
    prop = RowRoleProposal(("level",) * 8, 0.99, "genuine group labels")
    rep = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
    assert "MERGE_AMBIGUOUS" in _reasons(rep), _reasons(rep)


def test_shipped_pivot_unaffected_by_a_proposer(tmp_path):
    # a region that already tiles never reaches the NEURAL slice, so an aggressive proposer
    # cannot change it.
    p = os.path.join(str(tmp_path), "pivot.pdf")
    F.pivoted_table_pdf(p)
    prop = RowRoleProposal(("furniture",) * 8, 0.99, "aggressive")
    base = compile_tables(p)
    withp = compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
    assert _verdicts(base) == _verdicts(withp)
    assert _reasons(base) == _reasons(withp)
```

Note on `("level",) * 8` and `("furniture",) * 8`: the role vector length must equal the number of non-leaf header rows, which these fixtures do not expose. A wrong length is **refused** by `build_row_reading` — which is exactly the safe outcome these two tests assert (escalation / no change). Both tests therefore pass whether the length happens to match or not, and neither can pass by accident in the wrong direction.

- [ ] **Step 2: Run the test to verify it fails**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_integration.py -q`
Expected: `test_compile_tables_accepts_row_role_proposer_kw` **FAILS** with `TypeError: compile_tables() got an unexpected keyword argument 'row_role_proposer'`.

- [ ] **Step 3: Add the kwarg to `compile_tables`**

In `src/iladub/etkl/compile.py`, replace lines 74-75:

```python
def compile_tables(pdf_path: str, page_number: int = 0,
                   validate_shapes: bool = True, span_proposer=None) -> CompilationReport:
```

with:

```python
def compile_tables(pdf_path: str, page_number: int = 0,
                   validate_shapes: bool = True, span_proposer=None,
                   row_role_proposer=None) -> CompilationReport:
```

- [ ] **Step 4: Wire the resolver into the tiling-failure branch**

In `src/iladub/etkl/compile.py`, find this block (in the `else: # UNSUPPORTED_TABLE` → hierarchical path):

```python
                if hreg is not None and not merge_tiling_ok(hreg.tree, hreg.grid):
                    resolved = None
                    if span_proposer is not None:
                        from .span import resolve_ambiguous_merge
                        table_uri = URIRef(f"{_DOC}#htable{idx}")
                        resolved = resolve_ambiguous_merge(
                            graph, hreg, band, table_uri, _DOC, page_number, span_proposer)
                    if resolved is not None:
```

and replace it with:

```python
                if hreg is not None and not merge_tiling_ok(hreg.tree, hreg.grid):
                    resolved = None
                    if span_proposer is not None:
                        from .span import resolve_ambiguous_merge
                        table_uri = URIRef(f"{_DOC}#htable{idx}")
                        resolved = resolve_ambiguous_merge(
                            graph, hreg, band, table_uri, _DOC, page_number, span_proposer)
                    if resolved is None and row_role_proposer is not None:
                        # Loop C NEURAL slice. The narrow-flank resolver keeps priority: it fires
                        # on an explicit ambiguous_flank flag, a strictly narrower trigger. This
                        # handles the general tiling failure (caption / wrap-continuation rows).
                        from .rowrole import resolve_header_row_roles
                        table_uri = URIRef(f"{_DOC}#htable{idx}")
                        resolved = resolve_header_row_roles(
                            graph, hreg, band, table_uri, _DOC, page_number, row_role_proposer)
                    if resolved is not None:
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_rowrole_integration.py -q`
Expected: **3 passed.**

- [ ] **Step 6: Verify the B1.3 span path is unaffected**

Run: `. .venv/bin/activate && python3 -m pytest tests/etkl/test_b1_3_merge_resolution.py tests/etkl/test_span_gate.py tests/etkl/test_span_promotion.py tests/etkl/test_merge_resolution.py tests/etkl/test_ambiguous_flank.py -q`
Expected: all pass.

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_rowrole_integration.py
git commit -m "feat(etkl): wire the row-role NEURAL slice into compile_tables (loop C)"
```

---

### Task 6: Full-suite verification + GrainCorp end-to-end confirmation

**Files:**
- None committed unless a regression fix is needed (verification only).

- [ ] **Step 1: Full suite**

Run: `. .venv/bin/activate && python3 -m pytest -q`
Expected: all pass — the prior total (548 at Loop B close) plus the ~29 new tests from Tasks 1–5. Confirm **zero** regressions in header/tiling/pivot fixtures, `region_tiles`, `test_derivation_equiv.py`, `test_transform_gate.py`, `test_tiling_gate.py`, and `tests/test_source_ownership.py`.

If any test regresses, read it and reconcile — **do NOT weaken a test**. In particular a genuine merged-header fixture must still assert with its hierarchy intact, and every shipped escalation (off-center merge, narrow flank) must still escalate.

- [ ] **Step 2: Confirm the default path is byte-identical**

Run:
```bash
. .venv/bin/activate && python3 -m pytest tests/etkl -q -k "not rowrole and not conservation_shape"
```
Expected: exactly the pre-existing pass count, all green. This is the "default path unchanged" constraint.

- [ ] **Step 3: GrainCorp real-world confirmation (LOCAL, not committed)**

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from iladub.etkl.compile import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
prop=RowRoleProposal(('furniture','continuation','continuation'), 0.85, 'date caption, then two wrapped label rows')
r=compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
for i,reg in enumerate(r.regions):
    print(i, reg.kind, reg.verdict, 'cells=', reg.cells, 'reason=', reg.reason)
print('score=', round(r.score,4))
"
```
Expected (measured during planning with an equivalent spike): region 2 flips from
`UNSUPPORTED_TABLE escalated cells=0 reason=MERGE_AMBIGUOUS` to
**`UNSUPPORTED_TABLE asserted cells=447 reason=None`**, and `score= 0.947`.

Record the observed lines verbatim in your report. **Do NOT commit the PDF.**

The role vector is supplied by a `FakeRowRoleProposer` here because `BAML_LIVE` is not set — this
confirms the *mechanism* end-to-end on real input. It is NOT overfitting: the roles are the reading
a model is asked to produce, the oracles still dispose it, and nothing in the shipped code is tuned
to this document.

- [ ] **Step 4: Record the named residues**

Confirm and report these two, which are **expected and out of scope** (spec §7.1):
- Column 1's label is `Month Port` — two source columns collapsed into one grid column.
- Column 13's label is `Date Loading CompletedCommodityTotal` — three source columns collapsed.

These are **leaf-grid under-segmentation** (`recover_leaf_grid` found 14 boundaries where the source
has ~16), and they are why the score is 0.947 rather than 1.0. They define the next loop.

To dump the labels for the report, run:
```bash
cd "/Volumes/WD Green/dev/git/iladub" && . .venv/bin/activate && python3 -c "
from rdflib import Namespace
from iladub.etkl.compile import compile_tables
from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
TAB=Namespace('https://w3id.org/iladub/tab#')
p='/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/e181df4d-88f3-4dbc-bdca-e5822715046c/scratchpad/stem.pdf'
prop=RowRoleProposal(('furniture','continuation','continuation'), 0.85, 'date caption + two wrapped rows')
r=compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
for _s,_pd,o in r.graph.triples((None, TAB.captionText, None)): print('caption:', o)
for _s,_pd,o in sorted(r.graph.triples((None, TAB.cellText, None)), key=lambda t: str(t[0])): print('label:', o)
" 2>&1 | head -30
```
(`CompilationReport.graph` is verified to exist — `src/iladub/etkl/compile.py:38`.) This step is
reporting only and must not change any shipped code.

- [ ] **Step 5: Commit (only if a regression fix was needed in Step 1; otherwise skip)**

```bash
git add -A && git commit -m "fix(etkl): <describe the regression fix>"
```

- [ ] **Step 6: Update the spec's status line with the measured outcome**

In `docs/superpowers/specs/2026-07-26-header-row-roles-design.md`, append to the `**Status:**` line:
`**SHIPPED <date>:** GrainCorp 0.0 → 0.947 (447 cells); residues = leaf-grid under-segmentation of columns 1 and 13.`

Adjust the numbers to whatever Step 3 actually measured — **report the observed values, never the
planned ones.** If they differ from 0.947/447, say so explicitly and explain why.

```bash
git add docs/superpowers/specs/2026-07-26-header-row-roles-design.md
git commit -m "docs(spec): record loop C measured outcome"
```

---

## Self-Review

**Spec coverage:**

| Spec section | Task |
| --- | --- |
| §1 in-scope: `rowrole.py` propose→oracle→dispose→promote | Tasks 3, 4 |
| §1 in-scope: three-way role per non-leaf row | Task 3 (`ROLES`, `build_row_reading`) |
| §1 in-scope: oracle 1 (`region_tiles`) | Task 4 Step 4 |
| §1 in-scope: oracle 2 (`HeaderContentConservedShape`) | Task 1 |
| §1 in-scope: furniture carried as `tab:RegionCaption` | Task 1 (vocab), Task 3 (`emit_reading_evidence`), Task 4 (test) |
| §1 in-scope: `ProposeHeaderRowRoles` authored in `baml_src/` | Task 2 Step 4 |
| §1 success criterion 1 (red fixture asserts) | Task 3 Step 1, Task 4 Step 1 |
| §1 success criterion 2 (lossy reading refused) | Task 1 Step 2, Task 4 (malformed/illegal refusals) |
| §1 success criterion 3 (off-center still escalates) | Task 5 Step 1 `test_offcenter_merge_still_escalates_with_a_proposer`; unit-level in Task 3 `test_all_level_reproduces_the_failing_tree` and Task 4 `test_all_level_reading_is_refused_by_the_oracle` |
| §1 success criterion 4 (no regression, default byte-identical) | Task 3 Step 4, Task 5 Step 6, Task 6 Steps 1–2 |
| §1 success criterion 5 (GrainCorp closes) | Task 6 Steps 3–4 |
| §1 success criterion 6 (gate) | Global Constraints; enforced by `test_transform_gate.py` in Task 1 Step 8 / Task 6 Step 1 |
| §1 success criterion 7 (source ownership) | Task 1 Steps 4, 8 |
| §2 Findings (measurements) | Encoded as asserted facts in Task 3's fixture + "The verified fixture" section |
| §3.1 `rowrole.py` incl. unplaceable / all-level / k=0 edges | Task 3 (`build_row_reading` refusals), Task 4 (`len(header_rows) < 2`) |
| §3.2 proposer seam | Task 2 Step 3 |
| §3.3 BAML function | Task 2 Step 4 |
| §3.4 vocab + shape (dedicated properties, not Loop B's) | Task 1 Steps 4–5 |
| §3.5 `emit_row_role_promotion` | Task 4 Step 3 |
| §3.6 `compile.py` integration + resolver ordering | Task 5 Steps 3–4 |
| §4 testing (every bullet) | Tasks 1–5 test files; the caption-carried and promotion-emitted bullets are Task 4 Step 1 |
| §5 gate & discipline | Global Constraints |
| §7 residues named | Task 6 Step 4 |

**Gap found and closed during review:** §4's "Furniture is carried" and "Promotion emitted" bullets had no explicit test in my first pass — they are now `test_furniture_text_is_carried_as_a_caption` and `test_legal_reading_asserts_with_promotions` in Task 4 Step 1. §1 criterion 3's *unit-level* coverage was likewise added as `test_all_level_reading_is_refused_by_the_oracle`.

**Placeholder scan:** No "TBD"/"TODO"/"implement later"/"add error handling" anywhere. Every code step carries complete, correct, copy-ready code. Task 2 Step 5 is a type-consistency *check* (not a repair of a planted error). Task 6 Step 4's `report.graph` access was verified against `src/iladub/etkl/compile.py:38` rather than left as an assumption.

**Type consistency (checked across tasks):**
- `RowRoleProposal.roles: tuple[str, ...]` (Task 2) — `build_row_reading` receives `tuple(proposal.roles)` (Task 4 Step 4), and compares `len(roles) != len(non_leaf)`. Consistent.
- `build_row_reading -> (nodes: tuple[HeaderNode, ...], captions: tuple[tuple[int, str], ...], source_cells: tuple[tuple[int, str], ...]) | None` (Task 3) — unpacked as exactly three values in Task 4 Step 4 and in Task 3's test. Consistent.
- `emit_reading_evidence(g, table_uri, captions, source_cells)` (Task 3) iterates `(row, text)` pairs, matching the shapes above. Consistent.
- `_tree_from_rows(header_rows, grid) -> tuple[HeaderNode, ...]` (Task 3 Step 3) — called by `infer_header_tree` and `build_row_reading` with the same argument order. Consistent.
- `header_rows_of(band, grid, body_line)` (Task 3 Step 3) — called in Task 3's test as `header_rows_of(band, GRID, 3)` and in Task 4 as `header_rows_of(band, hreg.grid, hreg.body_line)`. `HierRegion.body_line` exists (`hierarchical.py:18`). Consistent.
- `emit_row_role_promotion(g, region_uri, row_index, role, texts, proposal)` (Task 4 Step 3) — called with `(graph, table_uri, r, role, [c.text for c in header_rows[r]], proposal)`; `texts` is a list of `str`, joined by `" ".join(texts)`. Consistent.
- Property IRIs used identically in Task 1's test, Task 1's TTL, the shape, and Task 3's emitter: `tab:sourceText`, `tab:sourceRow`, `tab:captionText`, `tab:captionRow`, `tab:hasHeaderSourceCell`, `tab:hasCaption`. Consistent.
- `promote.py` uses `_suggester`, `Decimal`, `BNode`, `RDFS`, `GIST`, `DEC`, `ILADUB`, `_slug` — all already imported/defined at the top of that module (verified). No new imports needed.
- `rowrole.py` module-level imports (`replace`, `Literal`, `Namespace`, `RDF`, `URIRef`, `XSD`, `_tree_from_rows`, `column_of`) are all used; `Graph`, `assert_hier_region`, `region_tiles`, `emit_row_role_promotion`, `header_rows_of` are imported inside `resolve_header_row_roles` to avoid a circular import with `headers`/`holon` (the same pattern `span.py` uses). Consistent.
