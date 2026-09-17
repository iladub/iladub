# Evidence — benchmarking docling-graph against the corpus (IN PROGRESS)

**Serves:** maintenance — re-examines `2026-08-15-docling-positioning.md`, which is still NOT ACCEPTED

**Date:** 2026-09-17. **Tree:** branch `docling-refusal-benchmark`, cut from `main` at `4e6611b`.

**Doc impact: none.**

**STATUS: the benchmark RAN, after eight failed controls exposed a defect in docling-graph itself.**

This file was first written when the benchmark could not run; that header is superseded and the
sections below are ordered as the session discovered them, deliberately — the failures are the
evidence for the root cause, and the root cause is what made the measurement possible.

**The three results, in order of how much they cost to establish:**
1. **A reproducible defect in docling-graph v1.9.1** silently degrades every OpenAI structured-output
   extraction to a near-empty fallback (§ 3b). Upstream-reportable, independent of iladub.
2. **The benchmark's own hypothesis is REFUTED** — with the defect patched, docling-graph fabricated
   **nothing** across five arms, and refused cleanly where the source was empty (§ 3d).
3. **The inverse claim is ALSO false** — "docling carries what iladub misses" was checked against
   iladub's graph before being written, and every literal is already carried (§ 3d).

---

## 1. Why a coverage benchmark was refused, and what was designed instead

iladub's score is an internal ink ratio (`asserted / denom`, `compile.py:1608`); docling-graph emits
entity graphs against a hand-authored Pydantic template. **There is no shared metric**, so
"who scores higher" produces a number that means nothing — the unaudited-denominator failure this
repo spent 2026-09-17's two earlier loops repairing.

The well-posed question is the **layer-4** one: *does docling-graph assert what the source does not
support, where iladub refuses?* Three arms, both controls mandatory:

| arm | pages | why |
| --- | --- | --- |
| subject | bfs p4, ons p0, bfs p0 | iladub asserts **zero** and escalates; anything emitted is differential |
| control_pos | apple p0, apple p1 | score **1.0000**, 172/98 tokens asserted — the instrument must fire here |
| control_null | bfs p2, ons p2 | score 1.0000 with **0 asserted** (no table) — a rich graph here is fabrication |

## 2. The refusal population, re-measured at HEAD (428 s, 27 pages)

**Both documents the 2026-08-15 analysis named as iladub's weak cases have been repaired since**, so
its document choice could not be inherited:

| page | 2026-08-15 | 2026-09-17 |
| --- | --- | --- |
| apple p1 | score 0.117, 151/171 escalated | **1.0000**, 0 escalated |
| cbh p0 | score 0.0603, 842 escalated | **0.9095**, 80 escalated |

Corpus today: **asserted 6356, escalated 589, ratio 0.9152**; escalation on **16 of 27 pages**,
across **30 regions**, typed by reason — `DATAGRID_RESIDUE` (4 largest: 45/44/43/36 tok),
`KIND_NOT_SUPPORTED` (6), `REGION_TILING_FAILED` (2), `ROUND_TRIP_FAIL` (1), remainder unreasoned.
Three pages score **0.0000 with 0 asserted** (bfs p0/p4, ons p0). Full table:
`scratchpad/refusal_population.txt`, JSON beside it. **The population exists** — the benchmark's
premise survives; only its engine failed.

## 3. THE CONTROL DID ITS JOB — three failures, three distinct causes

| attempt | config | result |
| --- | --- | --- |
| 1 | dense, full template, llama3.1 | **1 node, 0 edges**, 326 s. Node = `{document_reference: "June 27, 2026"}`, all 10 edge lists `[]`. `report.md`: *"Skeleton nodes discovered: 1"* after 159 s Phase 1 |
| 2 | direct, default output budget | **refused before calling**: `~1481 input + 131072 output > 32000 context`. The output default, not the document, blocks it |
| 3 | direct, `--llm-max-output-tokens 8192` | **killed, low memory**, >600 s, no output written |

**Had the control been skipped, attempt 1 would have produced "docling-graph asserts nothing where
iladub refuses" — clean, flattering, and entirely an artifact of an empty skeleton.** That is the
whole value of running the positive control first, and it is the finding most worth carrying.

## 3b. ROOT CAUSE — a reproducible defect in docling-graph v1.9.1's structured output

Eight controls failed. Two engines (llama3.1 local, gpt-4o-mini and gpt-4.1 remote), three
templates (1390-line ontology-derived, 429-line minimal, **and docling-graph's own induced
template**), two contracts, schema enforcement on and off — `Extracted 1 items` every time.
Template provenance, template size, model strength, contract and engine are each eliminated by a
run that varied only that factor.

**The defect is in `normalize_schema_for_response_format` (`llm_clients/schema_utils.py:11-53`).**
It strips `title`/`examples`, inlines a top-level `$ref`, and returns
`{"name": ..., "schema": ..., "strict": True}` — but it **never sets `additionalProperties: false`
and never promotes optional properties into `required`.** OpenAI's strict mode requires both,
recursively. Measured on their own induced template, after running their own normalizer:

```
  strict: True | additionalProperties: None
  properties=7 required=1 OPTIONAL=[company_name, currency_unit, has_category_sales,
                                    has_line_item, has_segment_sales, periods_covered]
  $LineItem / $SegmentSales / $CategorySales: addProps=None, ALL fields optional
litellm.BadRequestError: OpenAIException - Invalid schema for response_format
'extraction_result': In context=(), 'additionalProperties' is required to be supplied and to be false.
```

**The control that makes this a defect rather than an environment fault:** the identical LiteLLM
call path, same venv, same key, same model, with a *hand-written* strict schema **succeeds**
(`{"title":"Apple Inc.","rows":["Products","Services"]}`). So LiteLLM, the OpenAI SDK, the key and
the network are all sound; only schemas built by docling-graph's normalizer are rejected.

**The consequence is silent.** `_call_api` (`llm_clients/litellm.py:237-257`) catches the
`BadRequestError` and re-raises a generic `ClientError`; the pipeline logs a WARNING, falls back to
"legacy prompt-schema mode", reports **"Pipeline Completed Successfully"**, and writes a graph. On
apple p0 that graph carried **one cell out of roughly two hundred**. A user not reading WARNING
lines would receive a plausible, near-empty graph and no error.

**This is upstream-reportable and reproducible in three lines** (import the template, call their
normalizer, send the result to `litellm.completion`). It affects any OpenAI-provider user of
v1.9.1, independent of iladub.

## 3c. THE PATCH CONFIRMS THE DIAGNOSIS, AND THE CONTROL FIRES

A harness-only patch (`scratchpad/tmpl/sitecustomize.py`) wrapping their normalizer to set
`additionalProperties: false` and promote optional fields — as `anyOf: [T, null]`, **never as bare
`required`**, because forcing a value for every property would manufacture the fabrication this
benchmark counts — turned eight failures into an extraction on the same page, model and prompt:

| | before patch | after patch |
| --- | --- | --- |
| apple p0, induced template | 1 cell | `has_line_item` **20**, `segment_sales` **6**, `category_sales` **6**, `periods` **4** |

**Repairing exactly the two things OpenAI's strict mode demands is what changed**, which is the
confirmation that § 3b's root cause is the real one and not a coincidence.

**GROUND TRUTH: the extraction is CORRECT, and it REFUSED where the source is empty.** All 20 line
items match the recovered markdown — labels, all four period values, negatives preserved as
`(171)`, `$` kept where printed — and `periods_covered` recovered all four merged-header periods
(`Three Months Ended June 27, 2026`, …). Critically, the five **section-header rows**
(`Net sales:`, `Cost of sales:`, `Operating expenses:`, `Earnings per share:`,
`Shares used in computing earnings per share:`) came back with `values_by_period: ['']` —
**empty, not invented.** On this page docling-graph did not fabricate.

*(Contrast, recorded as an anecdote and NOT as evidence: an out-of-harness llama3.1 probe assigned
the label-only row `"Net sales:"` the figure `$ 78,678`, which belongs to `Products`. n=1.)*

**OUR ontology-derived template does NOT work as the instrument.** `tab_min` under the same patch,
same page, same model: `has_cell` **1**, `has_header_node` **1**, `has_leaf_column` **1**, in 114 s
— against 32 items from their induced template. So a template compiled from `tab.ttl` extracts
~1/32 of what a template their own pipeline induces does. That is a finding about
**ontology→template compilation**, not a harness defect, and it kills the uniform-template design:
cross-arm comparison cannot use ours.

## 3d. THE BENCHMARK RAN — AND ITS OWN HYPOTHESIS IS REFUTED

Five arms, patched normalizer, `openai/gpt-4.1`, induced template. **Every arm grounded
`match: verbatim`. Not one fabricated.**

| arm | page | iladub | docling-graph | verdict |
| --- | --- | --- | --- | --- |
| control_pos | apple p0 | 1.0000, 172 tok asserted | 20 line items + 6 segments + 6 categories + 4 periods, **all correct** | instrument fires |
| control_null | bfs p2 | 1.0000, 0 asserted | **0 items** | clean refusal |
| control_null | ons p2 | 1.0000, 0 asserted, 3 `ignored` | 7 items, all verbatim | see below |
| subject | bfs p4 | 0.0000, 36 tok escalated | 3 real labels, **values empty `''`** | did NOT invent numbers |
| subject | ons p0 | 0.0000, 16 tok escalated | 2 items (release metadata) | verbatim |
| subject | bfs p0 | **0.0000**, 6 tok escalated | **23 items** from PROSE | verbatim |

**The fabrication hypothesis is refuted on this corpus.** The sharpest available case — a
financial-statement schema pointed at pages with no table — produced either nothing (bfs p2) or
verbatim-grounded real content. On bfs p4, where labels exist but values do not, it returned
`values_by_period: ['']` rather than inventing figures. **docling-graph refused where the source
was empty**, which is the behaviour iladub's § 7 demands of itself.

**AND THE INVERSE CLAIM IS ALSO FALSE — checked before it was written.** The tempting finding was
*"docling carries what iladub misses."* Measured against iladub's own graph, every literal is
**already present**: ons p2 carries `34.9`, `Retail Sales Inquiry`, `Government Expenditure`;
bfs p0 carries `8 962 300`, `146 900`, `1,7`, `Croissance`. What differs is **how**: iladub's
predicates on those pages are `optionSpace`, `order`, `regarding`, `rationale`, `withinProcess` —
decision-holon bookkeeping, 191 and 594 triples — so the text is retained as band/decision records,
**not as typed table facts**. Neither tool "misses" this content; they type it differently.

**Two of my own framings were wrong and are corrected here rather than quietly dropped:**
1. **bfs p0 scores 0.0, not 1.0.** `page_has_table` is true and the reader produced nothing — the
   degenerate-1.0 case `compile.py:1613-1619` exists to catch. **The gate is working.**
2. **ons p2 was never a fabrication opportunity.** Its three regions are `ignored` (prose), so
   labelling it a "null control" was a category error on my part.

**The real difference the arms expose is NOT fabrication — it is PROSE.** bfs p0's ground truth has
**zero table rows**; docling-graph extracted 23 label/value pairs from running text
(`Population résidante permanente… 8 962 300`, `Croissance démographique 2022-2023: +1,7%`). That
is a capability iladub does not target, and it cannot be scored against a table-oriented ink ratio
in either direction.

## 4. What IS established (all stable, none dependent on the benchmark running)

**Layer 1 is excellent and the 2026-07-05 dismissal remains false.** On apple p0, `document.md`
recovered the *entire* table: 40 markdown rows, every figure, correct column labels (the two-level
merged header flattened to `"Three Months Ended - June 27, 2026"`). Conversion is not the weak link.

**§5(c)'s "compiles our ontologies unmodified" is REFUTED, twice:**
1. Root auto-election **fails** on `tab.ttl` — 43 candidate classes, exits 1, requires `--root`.
2. Their linter applied **65 repairs (R24×52, R19×10, R4×2, R16×1) + 17 advisories** before it
   would compile. "Unmodified" is not what happens.

**§5(c)'s "`rdflib` is already a dependency there" is REFUTED.** Absent from the v1.9.1 install
closure; OWL support needs the `templategen` extra. An upstream RDF exporter is a *new* dependency,
not a free one.

**§6's reversal condition has NOT triggered.** Confirmed at the CLI, not just the docs:
`--export-format` accepts **`csv` or `cypher` only**. Ontologies are input-only. No RDF/SHACL/SPARQL
output. Layer 4 remains uncontested.

**Release cadence, and a nuance the survey could not have seen:** docling-graph is still **v1.9.1
(published 2026-07-17)** — no release since the survey, last commit a dependabot bump. But the
*converter* moved: `docling 2.120.1 → 2.128.0`, `docling-core 2.91.0 → 2.97.0`. So §7b's layer-1
figures are stale even though the graph layer's are not. Stars: **319 → 894** in a month.

**`--depth` is not a size lever on our ontology** (20 → 18 components), because nearly every class
is one hop from `HierarchicalTable` across its 9 edges. `--include` globs are
(`tab_min.py`: 429 lines, 6 components, 4 edges, vs 1390/20/9).

## 5. What is NOT established

- **Generality of the no-fabrication result.** Five arms, one corpus, one model (`gpt-4.1`), one
  induced template. It is a refutation of the hypothesis *on this corpus*, **not** a clearance of
  docling-graph in general, and n=5 cannot support a rate.
- **Whether the defect reproduces on non-OpenAI providers.** Only `openai/` was tested. Anthropic,
  Mistral, vLLM and Ollama-local take different `response_format` paths; the local-Ollama runs
  failed for unrelated reasons (empty skeleton, memory), so they neither confirm nor deny it.
- **Whether the patch's `anyOf: [T, null]` form matches what upstream would choose.** It is
  OpenAI's documented shape and it avoids forcing a value per field, but it is my repair, not
  theirs, and a different fix could extract differently.
- **What docling-graph does with a table iladub reads WELL but differently.** Every subject arm
  landed on prose or near-empty pages; the head-to-head on a hard *table* (merged headers,
  cross-page continuation) is still unrun, and that is where § 7b's 2026-08-15 findings live.
- **Nothing here re-tests § 7b's layer-1 grid comparison**, whose figures are stale by two
  `docling-core` releases (2.91.0 → 2.97.0).
- **The one-off anecdote is NOT evidence.** A direct Ollama probe had llama3.1 assign the
  label-only row `"Net sales:"` the figure `$ 78,678`, which belongs to `"Products"` — the exact
  class of unearned assertion the benchmark counts. **n=1, outside the harness. Recorded to be
  re-measured, never to be cited as a result.**

## 6. Harness state, so the next attempt starts here

- venv `scratchpad/dgvenv` — docling-graph 1.9.1 + templategen (rdflib 7.6.0, linkml-runtime).
- `scratchpad/tmpl/tab_hierarchical.py` (1390 ln), `tab_d1.py` (1232), `tab_min.py` (429).
- `scratchpad/run/config.yaml` — Ollama-patched, `provider: ollama`, `model: ollama/llama3.1:latest`.
- `scratchpad/pages/*.pdf` — the 7 single-page arms, split with `pypdfium2` (present in both envs;
  `pypdf` is in neither).
- **Local engine verdict: not viable.** 326 s/page at best, one memory kill, and an empty skeleton
  under the full schema. This machine has now recorded five memory kills.

## 7. Cost

One corpus census (428 s), three failed control runs (~20 min of model time), one install
(multi-GB), three template compilations, and the survey re-verification. **No production code
touched; no dependency added to the project environment** — everything lives in a scratch venv.
