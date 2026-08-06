# The membrane seam — a Rust SHACL engine behind one interface — design

**Date:** 2026-08-06 · **Status:** closed 2026-08-06 ·
**Measured baseline:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` page 0 —
compile **28.4 s**, of which **20.4 s (72%) is pySHACL** in exactly **two calls**
(`tiling.region_tiles` 8.3 s, `compile._validate` 12.1 s), both over the same 8,424-triple
graph · **Scope:** engine swap only; the inference-semantics change is deliberately split
into its own successor loop (§7)

**Closed, measured (2026-08-06):** page-0 compile **28.4 s → 12.5 s** (score **0.9560**,
byte-identical) — a **2.3×** win, well short of §5's ~6× arithmetic, because that arithmetic
was per-validation-call, while wall-clock also carries owlrl's closure and rudof's own parse
across the Python/Rust boundary (§8). Whole-stem document: **~180–202 s baseline → 166 s**
(score **0.9655**, **2152** cells, one chain **[3]**, byte-identical) — a much smaller win,
stated plainly rather than alongside only the flattering page number, because a document
compile is dominated by other costs this loop never touched, chiefly R39's
`row-group-nesting.rq` self-join (~93 s). Corpus byte-identity gate
(`tests/test_corpus_stem.py` + `tests/test_cbh_e2e.py`): **13 passed in 251.79 s** (stem
0.9655, CBH 0.9047); apple **0.0105540897**, exactly the expected value. Full suite (final,
after the closure fix below): **968 passed, 1 failed, 5 skipped, 1281.74 s** — the single
failure is the known machine-environmental
`tests/test_release_gate.py::test_since_date_fallback_and_previous_tag` (a bare env dict
without PATH hits this machine's broken Xcode git shim; zero branch commits touch those
files; green in CI). Differential + mutation battery: **16 passed (~236 s)** — 11 committed
leak fixtures refused by BOTH engines, 1 real compiled page admitted by both, 3 seeds × 4
mutation kinds all caught by BOTH engines. The battery's real-corpus agreement was necessary
but not sufficient: the full suite subsequently found a genuine engine disagreement on a
*synthetic* fixture (`tests/etkl/test_row_groups.py`), root-caused to `rdfs_closure` using
plain `owlrl.RDFS_Semantics` (whose `one_time_rules()` fabricates hidden literals by
value-space unification, unlike pySHACL's own `CustomRDFSSemantics`, which disables exactly
those rules); fixed in `f9ea992`, pinned by
`test_rdfs_closure_does_not_fabricate_hidden_literals`. Three residues registered in
`docs/superpowers/residues.md` for the deferred work — the membrane redundancy (§6), owlrl as
the new bottleneck (§7/§8), and the battery's positive leg needing synthetic-fixture coverage
alongside corpus graphs.

**Doc impact:** increment — a new module and a new optional dependency; a wiki note on the
membrane seam queues for the next release. No published vocabulary or ontology term changes,
no site page contradicted.

## 1. Problem (measured 2026-08-06, not assumed)

Profiling a real page compile attributes the runtime as follows:

| component | self time | share |
| --- | --- | --- |
| rdflib | 24.9 s | 38% |
| pyparsing (SPARQL text parsing, driven by pySHACL) | 21.6 s | 33% |
| stdlib/builtins (driven by the above) | 16.2 s | 25% |
| pdfminer + pdfplumber | 1.4 s | 2% |
| **iladub's own code** | **0.1 s** | **0.2%** |

**iladub's own procedural code is 0.2% of runtime.** That is the neurosymbolic gate working
as designed — the decisions live in `.rq` files and SHACL shapes, and the Python is thin
glue — and it means no rewrite of iladub in any language can matter. Instrumenting the
callers shows **2,872 of 2,910 SPARQL executions come from pySHACL's
`sparql_based_constraints.py`** (one execution per focus node, per `sh:sparql` constraint;
we ship 15 such constraints). Our own derivations are 38 calls / ~8 s.

The cost is therefore the **membrane** (closed-world validation), not the **derivations**
(open-world SPARQL). That asymmetry is what this loop exploits: the derivations are where
the published semantics live and they are cheap; the membrane's semantics is its *shape
declaration*, and only its *evaluation* is expensive. Evaluation strategy is not semantics,
so it can be replaced with nothing asserted differently.

## 2. The candidate, measured

`pyrudof` 0.3.7 (rudof-project/rudof) — Rust, Apache-2.0/MIT, embeds oxigraph, exposes SHACL
validation with `Native` and `Sparql` modes. Verified against the shipped shapes, not
assumed:

- **It evaluates our `sh:sparql` constraints.** A graph violating both `UnitMarkerShape`
  (`sh:minCount`) and `WrappedCellShape` (`sh:sparql`) produced both violations with the
  correct focus nodes, `sh:SPARQLConstraintComponent`, and our exact message text. This was
  the make-or-break question — an engine without `sh:sparql` (e.g. bare oxigraph) is useless
  to us.
- **On the real page graph it agrees and is fast:** 0.09 s validate versus pySHACL's 12.0 s.
- **It does no RDFS inference.** Tested on the exact R19 mechanism (a node typed `tab:Cell`
  only via `tab:hasBBox`'s `rdfs:domain`): pySHACL with `inference="rdfs"` catches the
  resulting `WrappedCellShape` violation; **rudof misses it**, even with the ontology merged
  into the data graph. This is a soundness difference, and §3 addresses it.
- **Its strict parser rejects our expanded graph.** owlrl's RDFS closure emits **1,533
  triples with literals as subjects** (`"307.47"^^xsd:decimal rdf:type rdfs:Resource`) —
  illegal RDF that rdflib tolerates silently and rudof refuses outright. We have therefore
  been validating a technically-invalid graph, undetected.

## 3. The design

### 3.1 One seam

Today both call sites construct their own pySHACL invocation inline. They move behind a new
module `src/iladub/etkl/membrane.py`, the single place any SHACL runs:

```
membrane.validate(graph, shapes) -> (conforms: bool, report: str)
```

Pipeline: **owlrl full RDFS closure** (preserving today's semantics exactly) → **drop
literal-subject triples** (mandatory; see §2) → **serialize n-triples** → **persistent rudof
instance** (shapes parsed once at import; `reset_data` per call) → conformance + report.

The two call sites keep their **distinct shape sets** — the gate's thirteen
(`_TILING_SHAPE_IRIS` + `_PHYSICAL_SHAPE_IRIS`), the final pass's twenty-four. That
distinction is semantic (intra-region membrane vs whole-graph membrane) and is **not**
touched by this loop.

### 3.2 Three units, independently testable

- `membrane.validate(graph, shapes) -> (bool, str)` — engine choice, instance lifecycle,
  report normalization.
- `membrane.rdfs_closure(graph, ont) -> Graph` — owlrl closure plus the literal-subject
  filter, as one pure function. Isolated because the successor loop (§7) replaces exactly
  this function and nothing else.
- An engine adapter thin enough that pySHACL remains a drop-in alternative behind the §3.4
  switch.

### 3.3 The correctness gate is the deliverable

A committed differential battery, `tests/etkl/test_membrane_equiv.py`, running pySHACL
against rudof on three fronts:

1. **Positive** — corrected to what ships (final-review wave, 2026-08-06): the stem
   document's page-0 compiled graph, compared against both engines. The spec originally
   claimed "every corpus document's compiled page graphs and every shipped fixture" for this
   leg; that was aspirational, not what was built — the positive leg is single-document,
   single-page. See R59 for the coverage gap this leaves (both the corpus-only scope and the
   single-page scope) and what would close it.
2. **Negative** — every negative fixture already in the repo (the committed `tab-*-leak.ttl`
   set): both engines must report a violation, on the same focus node. Source shapes are
   frequently blank nodes with engine-specific labels — comparing those is not reliable (see
   §8), so only focus-node IRIs are compared, not source shapes.
3. **Mutation battery (the load-bearing one)** — seeded random mutations injected into real
   compiled graphs: drop a required triple, blank a `cellText`, duplicate a column claim,
   orphan a `tab:UnitMarker`'s `tab:markerRegion`. **Both engines must catch every injected
   defect.** Agreement on healthy graphs proves almost nothing — a validator that did nothing
   would also agree. Agreement on injected defects is the evidence.

The battery runs in CI, not once.

### 3.4 Escape hatch, not dual-run

pySHACL stays importable, selected by an environment switch (`ILADUB_MEMBRANE=pyshacl`), so
a suspected disagreement in the wild can be re-run under the old engine without a code
change. Production runs one engine — a dual-run would forfeit the entire win. The same
switch is the fallback if `pyrudof` wheels are unavailable on a platform.

## 4. What this loop does NOT change

- No shape, ontology term, or `.rq` file is edited.
- The gate's and the final pass's shape sets stay exactly as they are (the redundancy
  measured in §6 is left alone deliberately — see §7).
- Inference semantics are preserved byte-for-byte: full RDFS closure, as today.
- No parallelism. At ~2 s per validation there is nothing to parallelise, and parallelism
  would make the residue register's measured gate costs (`~0.26 s/call`, `0.095 s/call`)
  ambiguous between wall-clock and CPU time.

## 5. Success criteria

- **All corpus scores byte-identical**: stem **0.9655** / 2152 cells, CBH **0.9047**, apple
  **0.0105540897**. Scores derive from conformance decisions, so any divergence surfaces
  there — this is the strongest single regression signal available.
- Page-0 compile of the stem: **28.4 s → under 14 s** (expected ~12 s).
- The stem whole-document compile and its whole-graph validation (41–47 s at last
  measurement) re-measured and **recorded in the register**, so §7's loop has a committed
  number to improve on rather than a remembered one.
- Full suite green; the mutation battery green.

Per-validation arithmetic, from measurements already taken: owlrl 1.4 s + filter/serialize
~0.08 s + rudof parse 0.58 s + rudof validate 0.08 s ≈ **2.1 s**, versus pySHACL's 12.0 s —
about **6×**. (The 140× headline applies to validation alone; graph transfer across the
Python/Rust boundary dominates, and owlrl dominates that.)

## 6. Measured but deliberately not acted on

**8.2 of the final validation's 12.6 s re-checks shapes the region gate already checked**
(gate subset alone 8.2 s; the remaining eleven shapes 5.1 s). This 12.6 s and §1's 12.1 s are
**two different measurements, not one number that drifted**: §1 is the end-to-end profile's
whole-call figure for `compile._validate`; §6 is a separate shape-subset experiment (gate
shapes run alone, then the remaining eleven run alone) done to attribute the redundancy, not
to re-measure the whole call — the two runs are not expected to agree to the decimal. Scoping
the final pass to
non-gate shapes would recover ~25% *today* — but at rudof speed it recovers ~0.06 s, so it
is not worth a locality proof for performance reasons. It remains open as an **architectural
clarity** question (what does each membrane mean?), and it needs a per-shape proof that
every gate shape is region-local — a claim this repo has been bitten by before (loop M's
duplicate `doc#table0`, R36's slug collisions). Registered as a residue, not built.

## 7. The successor loop (split out on François's call, 2026-08-06)

Replacing `membrane.rdfs_closure` with **subclass-closure only** — materialising
`rdfs:subClassOf` over asserted types (0.07 s, +604 types) and dropping domain/range typing.
Measured on the real page: both readings conform, and the cheap one is **20× faster**, which
would take the membrane from ~2.1 s to ~0.75 s. It is split out because it **changes
behaviour**: a node would no longer type as `tab:Cell` merely by carrying `tab:hasBBox` —
which is exactly the R19 accident, so the change closes that hazard class at its root. That
is a semantic argument deserving its own evidence, and it will be provable with the battery
this loop ships rather than argued from first principles.

## 8. Risks, named

- **rudof is 0.3.7 with a small community.** Mitigations: the §3.3 battery, the §3.4 switch,
  and a pinned version. Its provenance (the ShEx/SHACL standards community) is good for
  correctness but is not a substitute for the battery.
- **Report text differs between engines**, and `compile._validate` raises `AssertionError`
  carrying that text. Any test asserting on message content must be found and checked.
- **Blank-node labels differ across the serialization boundary.** Harmless unless something
  asserts on them; the battery's negative leg compares focus nodes and source shapes, which
  are IRIs.
- **owlrl becomes the bottleneck** (two-thirds of the new membrane cost). Named, measured,
  and handed to §7 rather than hidden.

## 9. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate: no decision moves into procedural code. The shapes and queries are
  untouched; only the engine evaluating them changes.
- §7 credibility: a membrane that silently stops catching violations is the worst possible
  regression, which is why the mutation battery — not the speedup — is this loop's
  deliverable.
- Source ownership: `pyrudof` is consumed, never authored or vendored.
- Licensing: rudof is Apache-2.0/MIT, compatible with iladub's Apache-2.0 code.
