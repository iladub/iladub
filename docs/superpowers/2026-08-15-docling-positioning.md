# Positioning against Docling — a decision record, NOT YET ACCEPTED

**Written:** 2026-08-15, by the session that surveyed `docling-project/docling-graph`.
**Status:** **proposal.** Recorded nowhere but this file. Nothing in it has been acted on, no
dependency has changed, no code has moved. Reversible on the evidence cited, and the positioning
call is the owner's, not the analysis's.
**Written at 385,833 tokens**, 7.7× the originating floor, logged as an override. Read §7 before
trusting any judgement here that is not a citation.

---

## 1. The question that prompted it

*"Why develop custom systems when world-class solutions like IBM's Docling are available for free?"*

Asked in the open, and it will be asked again — by collaborators, by funders, by anyone evaluating
iladub. It deserves an answer with measurements behind it rather than conviction.

## 2. What was actually surveyed

`https://github.com/docling-project/docling-graph` — MIT, IBM (LF AI & Data), first commit
2025-10-21, **v1.9.1**, 29 releases, ~319 stars, 495 commits, last push 2026-08-14, 0 open issues.
Maintainers are IBM Zurich (`deepsearch-core@zurich.ibm.com`). It depends on `docling>=2.105` and
`docling-core[chunking]>=2.86`. Docs at `docling-project.github.io/docling-graph`.

**What it does:** document → Docling conversion → chunking → LLM/VLM extraction against a
user-authored **Pydantic** template → `networkx.DiGraph` → CSV / Cypher / Neo4j / JSON / HTML.

## 3. The four-layer map — where the "why custom" argument wins and loses

```text
  LAYER                              docling stack              iladub              call
 ──────────────────────────────────────────────────────────────────────────────────────────
  1  PDF → physical grid          world-class, free,        hand-rolled on      ADOPT THEIRS
     cells, spans, offsets        IBM-maintained            pdfplumber+rapidocr
       docling-core TableCell:    row_span, col_span, start/end_{row,col}_offset_idx,
                                  column_header, row_header, row_section, TableData.grid

  2  grid → entities/relations    LLM+template runtime,     —                   THEIRS
                                  multi-backend, chunking,
                                  gleaning, dense extraction

  3  reading → SEMANTICS          ONE FILE, and it only     tab.ttl ~60 classes  ← OUR GROUND
     header trees, spans,         strips control chars      + tab-datagrid.ttl
     crosstabs, aggregation,      from cells                + 38 SPARQL derivations
     cross-page continuation      (doclang_sanitizer.py)

  4  ADMISSION CONTROL            none — "validated" means  10 SHACL shape files,← OUR GROUND
     what may become a fact       Pydantic type-checks an   dec:DecisionHolon,
                                  LLM response              recorded refusal
```

**The argument wins at layers 1–2 and has no purchase at 3–4.** That asymmetry is the whole
positioning.

## 4. The measured basis for the layer-3/4 claim

Each of these is a fact about their repo, checkable today:

| claim | evidence |
| --- | --- |
| No SHACL anywhere | code search for `shacl` → **0 hits** |
| No RDF output | exporters are `csv`, `cypher`, `json`, `docling`. No Turtle, JSON-LD or OWL writer |
| RDF is input-only, and IRIs are discarded | `templategen/ontology/owl.py` compiles OWL/RDFS/SKOS → Pydantic classes; IRIs become Python names and are not retained |
| No table structure in the graph | code search for `TableItem` → **0 hits**; no cell/row/column/header node types |
| Table semantics live in a **prompt** | `core/extractors/contracts/dense/prompts.py`: *"A data row of a table becomes a separate entity instance ONLY when that row names a distinct instance of a catalog entity… When unsure, prefer FEWER instances"* |
| …backed by a tuned constant | `graph_max_instances`, an anti-spam cardinality rail written because "hundreds of financial-table rows" got promoted to entities; surplus rows are "demoted" |
| No confidence in the data model | `confidence` appears twice repo-wide: a doc example and a test |
| No provenance on **edges** | only nodes carry `__provenance__`; *why* a relation was asserted is unrecorded |
| Nobody is asking for any of this | 4 issues ever, 0 discussions, **no thread mentioning RDF/SPARQL/SHACL/ontology output** |

In iladub's §8 vocabulary, their layer-3 decision is *a reading judgement answered by a prose
heuristic with a tuned constant as backstop* — the exact form the gate exists to forbid. That is not
a criticism of their engineering; it is a different problem statement. They assume the reading is
given and extract from it. iladub treats the reading as the contested object.

## 5. The proposed decision

**(a) Stop competing at layer 1. Evaluate `docling-core` as the raw grid extractor.**
`TableCell` already carries exactly what the PROCEDURAL stage must produce before any AXIOM query
runs. Every hour in `etkl/geometry.py`, `grid.py`, `cells.py` is bought at full price on IBM's
strongest ground and not spent on layers 3–4. **This is an evaluate-or-reject, not a migration** —
and it must be recorded as a `dec:DecisionHolon`, because the current record is two dismissive lines
in old docs (`docs/loops/2026-07-05-table-holon-loop.md:5`,
`docs/superpowers/specs/2026-07-04-etkl-compiler-design.md:55`) and no dependency. Rejecting it on
measured grounds is a fine outcome; leaving it unexamined is not.

**(b) Spend the freed effort at layers 3–4**, which they have declined to build and show no sign of
building.

**(c) Treat their adoption as a tailwind.** More ungoverned document graphs means more demand for
something that can say *why* a triple is there and refuse the ones that are not earned. Two
interop surfaces exist today:
- **iladub → them, working now.** Our ontologies are plain OWL/RDFS/SKOS with
  `vann:preferredNamespaceUri` set, so `docling-graph template from-ontology` compiles them into
  extraction templates unmodified.
- **them → iladub, missing one piece.** Their output is flat `graph.json`; no RDF exporter exists,
  and `rdflib` is already a dependency there. Writing one is a small upstream contribution that
  would create the surface our shapes could validate.

**(d) Correct one differentiator claim.** `CLAUDE.md`'s "provenance to the page" is **no longer
distinctive.** Their `ProvenanceLedger` does it deterministically with bboxes and a
`verbatim → observed → document → unresolved` ladder under the rule *"fail-empty, never fail-wrong"*,
with zero LLM calls. It is well-designed and better documented than ours. The honest framing of
iladub's edge is **governed reading and admission**, not ingestion and not provenance.

## 6. What would reverse this

State it now, while it is cheap:

- **A SHACL or RDF exporter appears in docling-graph**, or an issue asking for one gains traction.
  Then layer 4 is contested and the analysis must be redone.
- **`docling-core`'s `TableCell` turns out not to carry what layer 1 needs** on real corpus
  documents — merged cells, hierarchical headers, cross-page tables. §5(a) is an evaluation
  precisely because this is unmeasured.
- **Someone builds the governance layer first**, in which case the question becomes whether to
  contribute to it rather than continue.
- **"Governed reading" proves too narrow a market.** This is the real strategic risk and no
  measurement here touches it.

## 7. Unverified or assumed

- **Nothing here has been tried.** No docling package has been installed, imported or benchmarked in
  this repo. `grep -rni docling src pyproject.toml README.md` → no matches.
- **Whether `docling-core` actually handles iladub's hard cases is unmeasured.** The 2026-07-05 loop
  doc asserts LlamaParse/docling/unstructured "fails: merged cells + hierarchical headers", but
  cites no measurement, names no version, and is now over a month old against a stack releasing
  monthly. **That claim is the load-bearing one for §5(a) and it has never been tested.**
- **Layer-1 duplication is inferred, not demonstrated.** Whether `readers.py`, `geometry.py`,
  `grid.py` and `cells.py` do more than `TableCell` provides was explicitly out of scope for the
  survey. They may well do more; nobody has compared them.
- **The survey read the repo, not the running system.** Every claim in §4 is from source and docs.
- **Both subagent reports were produced in one session and cross-checked against each other, not
  against a third source.** One of them mis-attributed concurrent test records earlier the same day,
  so their attribution reasoning is not infallible.
- **The market judgement in §6 is opinion.** It carries no evidence at all.

## 8. The next concrete action

Run §5(a): take three corpus documents that exercise the hard cases — merged cells, hierarchical
headers, a cross-page continuation — convert them with current `docling-core`, and compare its
`TableData.grid` against what `etkl/grid.py` produces. Record the outcome as a `dec:DecisionHolon`
either way. **That single measurement decides whether layer 1 is duplicated work or a real moat**,
and it is the only thing in this note that can be settled cheaply.
