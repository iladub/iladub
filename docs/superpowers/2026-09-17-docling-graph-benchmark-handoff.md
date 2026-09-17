# Handoff — the docling-graph benchmark ([[R246]], [[R247]])

**Topic:** The benchmark ran and refuted its own hypothesis; a defect in docling-graph v1.9.1 was
found, proved and patched. What survives a cleared context, and what does not.

**Serves:** maintenance — re-examines `2026-08-15-docling-positioning.md`, still NOT ACCEPTED

**Date:** 2026-09-17. **Tree:** branch `docling-benchmark-handoff`, cut from `main` at `c19f0a3`.

**Doc impact: none.**

Written because the benchmark loop merged (PR #252) **without** a handoff, and a 243-line evidence
file is not a next action. This carries the state over; it adds no new measurement.

---

## 5. The next concrete action

### 5a. ASSERTED — the harness is NOT durable; either reuse the path or rebuild from this recipe

**Typed ASSERTED because it is mechanical: the paths are known, the commands are recorded, and the
only question is whether the directory still exists.**

Everything below lives in a **session-specific** scratchpad that a fresh session will NOT be handed:

```
/private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/d771fcb5-4ee1-41c7-b7a6-a0762f06dea5/scratchpad
  dgvenv/                  1.6 GB   docling-graph 1.9.1 + templategen (rdflib 7.6.0)
  pages/                   6 MB     the 7 single-page arm PDFs
  tmpl/                    452 KB   tab_hierarchical.py, tab_d1.py, tab_min.py, apple_induced.py,
                                    sitecustomize.py (the patch)
  run/                     2.7 MB   config.yaml + 11 run output dirs (nodes.csv, graph.json,
                                    provenance.json, document.md per run)
  refusal_population.{txt,json}     the corpus census output
```

**`/private/tmp` is purged periodically by macOS.** The venv was created 2026-09-17. **Check first**
(`ls <path>/dgvenv/bin/docling-graph`); if gone, rebuild:

```
python3 -m venv dgvenv && dgvenv/bin/pip install "docling-graph[templategen]"
python scripts/refusal_population_census.py                 # the population, ~430s, SERIAL
# split the arm pages with pypdfium2 (present in both envs; pypdf is in NEITHER)
```

Then, for every run, **`sitecustomize.py` must be on `PYTHONPATH`** — it is committed as
`scripts/thirdparty/docling_strict_schema_patch.py`. **Without it every OpenAI extraction silently
degrades** to ~1 cell of 200 while reporting success (§ 3b). The exact arm command:

```
PYTHONPATH=<dir with sitecustomize.py + template> dgvenv/bin/docling-graph convert <page.pdf> \
  -t apple_induced_template.FinancialStatement -b llm -i remote -m openai/gpt-4.1 \
  --provider openai --schema-enforced-llm --llm-max-output-tokens 16384 \
  --llm-context-limit 128000 --provenance detailed -o <out>
```

The induced template is committed (`scripts/thirdparty/docling_benchmark/`) **because it is not
reproducible** — `from-docs` runs an LLM. The ontology-derived ones are not committed because they
regenerate exactly; the command is in that file's header.

### 5b. PROPOSED — [[R247]]'s hard-table head-to-head is the next measurement, and it rests on a claim

**Typed PROPOSED because it depends on a premise this session did NOT verify.**

Every arm landed on prose or near-empty pages, so the comparison that would actually decide layer 1
— merged headers, cross-page continuation, at **graph** scope — is unrun. The obvious next loop is
to run it on apple p1 / bfs p6 / graincorp-stem.

**THE SEAM TO MEASURE FIRST:** *can docling-graph's output even be compared to iladub's at graph
scope on a table?* Measured here: their induced financial template yields **1 node, 0 edges** because
`LineItem`/`SegmentSales`/`CategorySales` are all `is_entity=False` components embedded as nested
JSON. **If a table template also produces one node with embedded lists, then "compare the graphs"
has no graph on one side**, and the comparison must be defined over the embedded structures instead
— a different instrument than the one §7b used at `TableData.grid` scope.

**Do not assume a uniform template is available.** Measured: a template compiled from `tab.ttl`
extracts **~1/32** of what their induced template does on the same page, so ours cannot be the
shared schema and per-document induction makes arms non-comparable. **That tension is unresolved and
is the real design problem of R247**, not the running of it.

### 5c. ASSERTED — what is finished and must NOT be redone

- **Do not re-run the fabrication benchmark.** Five arms, all `verbatim`, zero fabrication.
  Evidence § 3d.
- **Do not re-diagnose the structured-output failure.** Root cause proved at
  `schema_utils.py:11-53`, with a passing hand-written-schema control. Evidence § 3b.
- **Do not claim "docling carries what iladub misses."** Checked and **false** — every literal is
  already in iladub's graph, under `optionSpace`/`order`/`regarding`/`rationale`. Evidence § 3d.
- **Do not re-test §5(c)'s two claims.** Both refuted: "compiles unmodified" (43 root candidates,
  65 linter repairs) and "rdflib is already a dependency" (needs the `templategen` extra).
- **Do not use local Ollama.** 326 s/page, one memory kill, empty skeletons under a large schema.
- **Do not call ons p2 a fabrication opportunity** — its three regions are `ignored` prose.
- **Do not cite bfs p0 as a 1.0 page** — it scores **0.0**; `page_has_table` is true and the reader
  produced nothing, which is `compile.py:1613-1619` working as designed.

### 5d. The two decisions that are the MAINTAINER'S, not a loop's

1. **[[R246]] — rule on the 2026-08-15 positioning analysis.** Still "NOT YET ACCEPTED", no
   `dec:DecisionHolon` despite its own §5(a) demanding one, and it has now accrued two rounds of
   measurement. Accept, reject, supersede or park — but a proposal that only ever gains evidence is
   the failure the register exists to prevent.
2. **Reporting the defect upstream.** § 3b is reproducible in three lines and affects any
   OpenAI-provider user of v1.9.1. Filing it is **outward-facing and published under the owner's
   name**, so it is not a loop's call. The reproducer is committed and ready.

---

## 1. Where the primaries are

- **Evidence** — `2026-09-17-docling-graph-benchmark-evidence.md`. § 1 why coverage was refused +
  the arm design, § 2 the re-measured population, § 3 the eight failures, **§ 3b the root cause**,
  § 3c the patch + ground truth, **§ 3d the arms and the refutation**, § 4 stable tool findings,
  § 5 what is not established, § 6 harness state, § 7 cost.
- **The rows** — [[R246]] (unaccepted + unregistered), [[R247]] (hard-table head-to-head unrun),
  both in `residues.md` + `residues-open.md`.
- **The instruments** — `scripts/refusal_population_census.py`,
  `scripts/thirdparty/docling_strict_schema_patch.py`,
  `scripts/thirdparty/docling_benchmark/apple_induced_template.py` (+ its spec).
- **The analysis under re-examination** — `2026-08-15-docling-positioning.md` (§7b is its own
  later-appended layer-1 measurement).

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| A coverage benchmark is a category error; layer-4 is the question | evidence § 1 |
| The population was re-measured; two inherited figures were stale | evidence § 2 |
| docling-graph v1.9.1 has a silent structured-output defect | evidence § 3b |
| The fabrication hypothesis is REFUTED (5 arms, 0 fabrication) | evidence § 3d |
| "docling carries what iladub misses" is also FALSE | evidence § 3d |
| §5(c)'s two claims refuted; §6's reversal condition not triggered | evidence § 4 |
| Our ontology cannot be the uniform template (~1/32 extraction) | evidence § 3c; § 5b above |
| The positioning call stays unruled | [[R246]] |

## 3. Unverified or assumed

- **Generality.** n=5, one corpus, one model, one induced template. A refutation on this corpus, not
  a clearance of docling-graph.
- **Non-OpenAI providers.** Only `openai/` was tested for the defect.
- **The patch's shape is mine, not upstream's** — `anyOf: [T, null]` is OpenAI's documented form and
  avoids forcing a value per field, but a different fix could extract differently.
- **Whether the scratchpad still exists.** § 5a. `/private/tmp` is purged; the venv is same-day.
- **§7b's layer-1 figures** are stale by two `docling-core` releases (2.91.0 → 2.97.0).

## 4. What this session did, and what it cost

Re-measured the refusal population (428 s, 27 pages), designed a three-arm benchmark with both
controls, failed eight controls, isolated and proved a defect in docling-graph, patched it, ran five
arms, refuted the benchmark's hypothesis, checked and refuted the inverse claim, corrected two of its
own framings, raised two register rows and committed three instruments. One multi-GB install; no
dependency added to the project environment.

**The cost worth carrying: the positive control is the only reason any of this is trustworthy.**
Attempt 1 returned an empty skeleton that, read without a control, says *"docling-graph asserts
nothing where iladub refuses"* — the exact result the benchmark was built to look for, flattering to
this project, and entirely an artifact. **A benchmark that can only confirm its author's hypothesis
is not an instrument.** The control cost one extra run and changed the conclusion completely.
