# Tabular-topology ontology — design

- **Date:** 2026-07-05
- **Author:** François Rosselet
- **Status:** Design (brainstormed). The **Goal/verifier of Loop 1** (the table-holon compiler,
  `docs/loops/2026-07-05-table-holon-loop.md`). Sub-project **B** of the loop-engineering direction.
- **Context:** *A table is not an array.* A published table is the top of an **intentional transformation
  stack** — flat facts → pivot (analytical intent) → cosmetic (rhetorical intent). This ontology is the
  formal model a **table-holon** must conform to, so the compiler can **reverse-engineer the artefact to its
  flat facts while recovering the intent at each layer** ("facts + the context that emphasizes them").

---

## 1. Purpose & scope

Define the formal, **domain-neutral** contract for a **table-holon**: the terms to *profile* any table
precisely (both audiences — human-legible, machine-formal), the invariants a valid table-holon must satisfy
(the **verifier**), and the alignment to existing standards. This ontology is what Loop 1 converges toward.

**In scope:** the physical/logical/functional structure of tables; the three *states* (flat/cube/presented)
and the two intent-carrying *transforms* between them; the **access function** (cell ← header paths); the
**kind** taxonomy (the field of possibles); signals-as-evidence; the holon framing; alignment to CSVW,
RDF Data Cube, PROV, and HGA `holon:`.

**Out of scope:** the extraction *algorithm* (that is the loop's Actions — a later spec/plan); domain
terminologies (LOINC/UCUM/FHIR — a separate contract layer that plugs in); exhaustive coverage of every
exotic table in v1 (the *structure* is complete; *depth* is incremental).

**Success:** a table-holon that (a) round-trips against measured geometry and (b) SHACL-conforms to this
ontology is *understood* — every entry cell resolves to exactly one column-path × row-path, header trees
tile, and the profiled kind holds — **verified across the RealHiTBench/CHiTab benchmarks, not one PDF**
(no-overfitting).

## 2. Prior art & alignment strategy (build on what exists — align, don't reinvent)

| Prior art | What we take | How |
|---|---|---|
| **Wang Abstract Table Model** (1993/1998) | the **base structure** — four models (physical/logical/functional/semantic), **label vs entry**, table = **map from a product of categories (header paths) → entry values** | formalize in `tab:` (Wang is conceptual, no canonical OWL); it *is* the access function |
| **CSVW** (W3C) | the **flat state** schema (columns, rows-as-records, keys, datatypes) | align `tab:FlatView` → `csvw:` (objects only) |
| **RDF Data Cube `qb:`** (W3C) | the **cube/pivot state** (dimensions, measures, observations, slices) | align `tab:CubeView` → `qb:`; CSVW→QB is an existing bridge = *flat→pivot* |
| **PROV `prov:`** (W3C) | the **transforms as activities** carrying intent (`prov:used`/`generated`) | `tab:*Transform ⊑ prov:Activity` (iladub already uses `prov:` for `dec`) |
| **HGA `holon:` · `etkl:` · `dec:`** | a **table is a holon**, produced by `etkl`, its compilation governed by `dec` | `tab:Table ⊑ holon:DataHolon`; align to `etkl`/`dec` |
| **Pivot/unpivot algebra** (SQL, tidy-data, Power Query) | the **transform semantics** ("unpivot = normalize a *wide human-friendly* table to a *tall tidy* one") | informs `tab:PivotTransform`; not authored |
| **Hierarchical-table research + RealHiTBench / CHiTab** | the **problem definition** (spatial-logical discontinuity; ancestral-label chains) + the **test bed** | benchmark harness, not an ontology |

**Source ownership (CLAUDE.md invariant):** we **own** `tab:` (a new module under the iladub root); `qb:`,
`csvw:`, `prov:`, `holon:` are **consumed** — they appear only as *objects/alignment targets* in
`tab-*-align.ttl` modules, never authored. Core `tab.ttl` stays **standalone** (zero external refs,
reasoner-free).

## 3. Core thesis — the intent-transformation stack

```
 FLAT / tidy (facts)  ──pivot/cast──▶  CUBE / pivoted  ──present/format──▶  PRESENTED / cosmetic
  align: CSVW            analytical       align: qb:          rhetorical          the published artefact
                          intent                              intent               (what we MEASURE)

 COMPILER = the inverse chain:
   presented ──recover present-intent──▶ cube ──recover pivot-intent──▶ flat facts
   (each inversion a prov:Activity carrying the WHY; the holon ends holding facts + emphasis-context)
```

Everything starts from a flat table; **pivoting** adds analytical intent (which variables to compare);
**cosmetics** add rhetorical intent (merges/alignment/color/emphasis/ordering/caption = *weight and role*).
Compilation inverts the stack and **records the intent it inverted**, so the output holon carries the
**facts and the context that emphasizes them** — the whole intentional history.

## 4. Core vocabulary — `tab:`

- **`tab:Table`** — a holon (`⊑ holon:DataHolon`); has a `tab:kind`, one or more `tab:*View` states, a
  `tab:accessFunction`, and `tab:region`s. Interior = entries; boundary = header structure; context =
  caption/footnotes/provenance; projection = grounded observations.
- **Cell roles (Wang):** `tab:Cell` → `tab:LabelCell` | `tab:EntryCell`; derived: `tab:DerivedCell`
  (totals/subtotals). Region roles: `tab:Caption`, `tab:HeaderBlock`, `tab:Stub` (row-key columns),
  `tab:Body`, `tab:Footnote`, `tab:Legend`.
- **Header trees:** `tab:HeaderNode` with `tab:parentHeader`; `tab:ColumnHeaderTree`, `tab:RowHeaderTree`;
  `tab:coversLeaf` (a node covers a contiguous run of leaves — the *tiling* relation); `tab:headerPath`
  (root→leaf label chain — the access anchor).
- **Access function:** `tab:LeafColumn`, `tab:LeafRow`; `tab:cellAt(colPath, rowPath) → EntryCell` (total,
  unambiguous). This is Wang's map, made an OWL property with SHACL invariants.
- **Spans/merges:** `tab:spansColumns` / `tab:spansRows` (a header span = a parent node; a body span = a
  merged entry).
- **Signals as evidence (never truth):** `tab:Signal` → `tab:Alignment`, `tab:Emphasis` (bold/italic),
  `tab:Color`, `tab:Indentation`, `tab:Rule` (border); each with `tab:evidenceFor` a role/structure and
  `tab:confidence`. Signals **feed the verifier**; they are not asserted facts.
- **Rhetorical weight:** `tab:weight` / `tab:emphasis` — the meaning a cosmetic conveys (a highlighted row,
  a bold total), captured as recovered intent.

## 5. The three states (holon views)

- **`tab:FlatView`** — aligned to **CSVW**: columns as `csvw:Column`, each row a record/observation, a
  primary key. The tidy, agnostic facts.
- **`tab:CubeView`** — aligned to **`qb:`**: a `qb:DataSet` whose `qb:dimension`s are the header axes, whose
  `qb:measure` is the entry value, one `qb:Observation` per leaf cell. The pivot.
- **`tab:PresentedView`** — the cosmetic artefact: the physical layer (cells+bboxes, merges, alignment,
  color, rules, whitespace) + the header trees + caption/footnote/legend. **This is what we measure.**

A table-holon may hold all three views plus the transforms between them.

## 6. The two transforms (intent-carrying, invertible)

- **`tab:PivotTransform ⊑ prov:Activity`** (flat→cube): `tab:pivotedOn` (which flat columns became
  dimensions), `tab:aggregation`, `tab:intent`. Inverse = unpivot.
- **`tab:PresentTransform ⊑ prov:Activity`** (cube→presented): `tab:merges` (header tree derived from
  dimensions), `tab:emphasisOf` (signal→weight), `tab:captionOf`/`tab:footnoteOf` (scope/exceptions),
  `tab:ordering`. Inverse = recover-structure.

The compiler emits these with `prov:used`/`prov:generated`, so the intent history is queryable — "why is
this table shaped this way" becomes an SPARQL question.

## 7. The kind taxonomy (the field of possibles) — SHACL patterns

Each kind is a `sh:NodeShape` constraining the access-function/header-tree/regions:

- **`tab:RecordTable`** — 1-level column header, no row-header tree (the "array with headers"; near-flat).
- **`tab:MatrixTable` / cross-tab** — both axes headered; 2-D access function.
- **`tab:PivotTable`** — cube-derived; `qb:` dimensions present on ≥1 axis.
- **`tab:HierarchicalTable`** — multi-level header tree on a column or row axis (the merged/nested case).
- **`tab:KeyValueTable`** — two-column label:value property sheet.
- **`tab:StackedTable`** — several logical tables in one grid → must decompose.

## 8. The verifier — what "conformant" means (Loop 1's Goal, formalized)

- **Access-function totality + unambiguity** — every `tab:EntryCell` resolves to **exactly one**
  column-path × one row-path (no orphan, no double). *(SHACL.)*
- **Header-tree tiling** — coverage (each leaf covered once per level), refinement (each child span ⊆ one
  parent), leaf-accounting. *(SHACL.)*
- **Kind conformance** — the profiled `tab:kind`'s shape holds. *(SHACL.)*
- **Round-trip** — re-render the `PresentedView` to spatial-ASCII and diff against measured geometry.
  *(Procedural oracle, enforced in the loop — the geometry is the ground truth, not a SHACL rule.)*
- **Honesty** — every entry is a grounded **assertion** or a `dec:` **proposition**; **provenance-to-page
  mandatory**. Silent-wrong is impossible.

## 9. Determinism-cursor mapping (Wang's four models ↔ the cursor)

- **physical** → *measured* (the oracle; 1a's points/geometry).
- **logical + functional** → *inferred + verified* (1b: label-vs-entry, header-tree tiling, the access
  function) — the model proposes, the tiling/round-trip validates.
- **semantic** → the *contract/grounding* layer (domain terminology, plugged in).
- **signals** are evidence feeding the verifier, never asserted as truth.

## 10. Modules & artefacts (what gets built — per iladub conventions)

- `vocab/ontology/tab.ttl` — core `tab:`, **standalone** (no external refs).
- `vocab/ontology/tab-csvw-align.ttl` · `tab-qb-align.ttl` · `tab-prov-align.ttl` · `tab-holon-align.ttl`
  — alignment (`rdfs:subClassOf`/`subPropertyOf`/`seeAlso`; external terms as objects only).
- `vocab/shapes/tab-shapes.ttl` — the §8 invariants + §7 kind patterns.
- `examples/tables/*.ttl` — a **conforming** pivoted/hierarchical table-holon + **negative** cases (per
  CLAUDE.md: one that conforms, one that must fail).
- `tests/test_tab_*.py` — pySHACL validation + the **benchmark round-trip harness** (RealHiTBench/CHiTab).

## 11. Testing & no-overfitting

Validate against **RealHiTBench + CHiTab** (diverse real hierarchical tables) and synthetic fixtures, with
the **round-trip oracle**. A kind's shape must pass **across the benchmark**, not on one hand-made PDF.
Report coverage per kind + escalation rate. Any shape that only passes a single example is rejected.

## 12. Decisions (resolved 2026-07-05 — all recommendations adopted)

1. **Namespace** — a new owned module `tab:` = `https://w3id.org/iladub/tab#` (w3id-redirected like the
   others) **vs** folding into `etkl:`. *Recommendation:* a separate `tab:` module — a table ontology is
   reusable beyond etkl and deserves its own IRI space; add a w3id redirect rule alongside core/etkl/dec/risk.
2. **`qb:` obligation** — require the CubeView only for pivot/matrix kinds; optional for record/key-value.
   *Rec: conditional on kind.*
3. **Round-trip enforcement** — procedural (in the loop) vs SHACL-SPARQL (partial). *Rec: procedural for the
   geometric diff; SHACL for the structural invariants.*
4. **v1 kind coverage** — *Rec:* record · hierarchical · pivot · key-value in v1; defer stacked/transposed.

## 13. Roadmap

- **v1:** core `tab.ttl` + access/tiling/kind SHACL (record/hierarchical/pivot/key-value) + CSVW/`qb:`/PROV/
  holon alignment + the benchmark round-trip harness + conforming/negative examples.
- **then:** intent-transform provenance depth (recover `pivotedOn`/`emphasisOf`); stacked/transposed kinds;
  the cosmetic-weight semantics; wire into Loop 1's Actions (the maker's HTML→holon mapping) and the
  generator-abduction field-of-possibles.
