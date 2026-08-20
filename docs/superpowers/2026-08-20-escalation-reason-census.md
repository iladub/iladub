# Measurement — the escalation-reason census (spec §11 seams 1 and 2)

**Date:** 2026-08-20 · **HEAD:** `820ab24`, working tree clean · **Runner:**
`./.venv/bin/python` (rdflib 7.6.0, Python 3.12.0, `pyrudof` present) · **Class:** evidence.

This is the measurement spec §11 puts on the critical path: *which of the escalation reasons
actually fire on the 7-document corpus, and how often.* It asserts nothing about the arc; it is the
input the `tab` rung's denominator and the six `etkl` adjudications are owed.

## Method

`iladub.etkl.document.compile_document(path)` once per document — the same public call as the
`corpus_graphs` fixture (`tests/etkl/test_vacuity_registry.py:298-312`) and
`tests/test_corpus.py:100-102`. Counted two ways:

- **graph-side (authoritative):** subjects typed `iladub:CandidateConcept` carrying
  `rdfs:label = <reason>` — the record `holon.escalate_region` writes (`holon.py:450-463`).
- **report-side:** `(kind, verdict, reason)` over `rep.pages[*].regions`, the idiom of
  `tests/test_corpus.py:107-108`.

Script and raw JSON: `census.py` / `census.json` (session scratchpad, not tracked); the per-document
lines are reproduced below in full.

**Trap, stated before the numbers.** `RegionReport.reason` is not reason-typed: on `ignored` bands it
carries the free-text *classification* reason from `regions._reason` (`"fewer than 2 lines"`,
`"fewer than 2 columns"`, …). Those are excluded here. They dominate the raw counts — ons books 70
of them and zero escalations.

## Seam 2 — the reason vocabulary, re-measured from the code

Spec §7.4 says **eight**. **It is nine.** `TRANSPOSED` is misfiled there as a kind and is in fact an
escalation reason: `compile.py:688` passes it to `escalate_region`, and `RegionKind`
(`regions.py:27-30`) has exactly three members — `RECORD_TABLE`, `UNSUPPORTED_TABLE`, `NON_TABLE`.
Those three, plus nothing else, are the kinds.

Every `escalate_region(` call site in `src/`, with its reason literal:

| reason | site(s) |
| --- | --- |
| `MULTI_TABLE_AMBIGUOUS` | `compile.py:596` |
| `REGION_TILING_FAILED` | `compile.py:656`, `:763`, `:939` |
| `TRANSPOSED` | `compile.py:688` |
| `ROW_GROUP_AMBIGUOUS` | `compile.py:739` |
| `MATRIX_AMBIGUOUS` | `compile.py:830` |
| `MERGE_AMBIGUOUS` | `compile.py:911` |
| `KIND_NOT_SUPPORTED` | `compile.py:978` |
| `DATAGRID_RESIDUE` | `compile.py:1145` |
| `ROUND_TRIP_FAIL` | `holon.py:493` |

There is **no enum and no registry** — the reasons exist only as literals at the call sites, and that
is deliberate: `_suggester_uri` (`holon.py:409-421`) slugifies the string rather than looking it up,
its docstring giving the reason (*"a hand-maintained table drifts from the call sites … and the drift
is silent"*). Consequence for the plan: the manifest's reason list is a **copy of a grep**, and it can
drift. Whatever the plan writes must carry the grep that produced it.

## Seam 1 — the census

Surviving escalation records in the compiled graph. Counts are regions, not tokens.

| document | pages | score | RTF | MATRIX | ROUND_TRIP | KIND_NS | DATAGRID | MERGE | MULTI_TBL | ROW_GRP | TRANSP | total | wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cbh-stem | 1 | 0.9047 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | 28s |
| graincorp-capacity | 1 | 1.0000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | 11s |
| graincorp-stem | 3 | 0.9655 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | 162s |
| apple | 3 | 0.3556 | 8 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | **11** | 37s |
| bfs | 7 | 0.3438 | 2 | 0 | 5 | 3 | 0 | 0 | 0 | 0 | 0 | **10** | 25s |
| ons | 9 | 0.9720 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | 9s |
| who-wfa | 3 | 0.5597 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **3** | 40s |
| **corpus** | **27** | — | **10** | **5** | **5** | **3** | **1** | **0** | **0** | **0** | **0** | **24** | ~315s |

`RTF` = `REGION_TILING_FAILED`, `KIND_NS` = `KIND_NOT_SUPPORTED`.

**Four of nine reasons never fire on any document, on any page:** `MERGE_AMBIGUOUS`,
`MULTI_TABLE_AMBIGUOUS`, `ROW_GROUP_AMBIGUOUS`, `TRANSPOSED`. Each is exercised only by synthetic
fixtures. Spec §7.4 guessed `MERGE_AMBIGUOUS` and `MULTI_TABLE_AMBIGUOUS` as "the two most likely to
be already-met" and refused to assert it; the guess was right and one short.

**Four of seven documents emit no escalation record at all** — cbh-stem, graincorp-capacity,
graincorp-stem, ons. The whole corpus escalation surface is **24 records on 3 documents**.

**graincorp-stem now escalates nothing.** The `REGION_TILING_FAILED` escalations its 2026-08-02
manifest adjudication describes on pages 1–2 do not survive at HEAD. Its 77 escalated *tokens* sit
inside asserted regions and mint no record (`compile.py:960`). Same for cbh-stem's 86.

### Graph-side vs report-side — they differ, and the difference is one page

Report-side counts 29 reason-bearing reports, graph-side 24. The delta is entirely apple page 1, the
adopted page: 5 escalations are **withdrawn** from the graph when the data grid supersedes them
(`document.py:1512-1513` → `_remove_escalation_record`), but the `RegionReport` keeps its original
reason (`compile.py:1132-1136` rewrites only `verdict` and `tokens_escalated`). Withdrawn:
`REGION_TILING_FAILED` ×3, `KIND_NOT_SUPPORTED` ×1, `ROUND_TRIP_FAIL` ×1 — replaced by one
`DATAGRID_RESIDUE`. 11 escalated + 5 superseded = 16 reason-bearing reports on apple; the graph keeps
11. The two readings reconcile exactly.

**The plan must pick a side and say which.** A SHACL membrane over the compiled graph can only see
the graph-side 24.

### Token accounting for the same run

| document | asserted | escalated | score |
| --- | ---: | ---: | ---: |
| cbh-stem | 816 | 86 | 0.9047 |
| graincorp-capacity | 390 | 0 | 1.0000 |
| graincorp-stem | 2152 | 77 | 0.9655 |
| apple | 165 | 299 | 0.3556 |
| bfs | 229 | 437 | 0.3438 |
| ons | 590 | 17 | 0.9720 |
| who-wfa | 445 | 350 | 0.5597 |

graincorp-stem reproduces its adjudicated 0.9655 and clears its `cor:scoreFloor` 0.95. Measured page
counts match `cor:pages` for every document that declares one.

## Where the escalations actually are

- **apple (11)** — `REGION_TILING_FAILED` ×4 on p0 and ×4 on p2 (the cash-flow / income statements);
  `MATRIX_AMBIGUOUS` ×1 on p0 and ×1 on p2 (the `Three Months Ended … Nine Months Ended` double
  header); `DATAGRID_RESIDUE` ×1 on p1, under the adoption doc URI (`document.py:1473`).
- **bfs (10)** — `ROUND_TRIP_FAIL` ×5 all on p5, all region-level `#htable{n}-rt` URIs
  (`holon.py:493`); `KIND_NOT_SUPPORTED` ×3 (p0 the press-release masthead, p6 ×2);
  `REGION_TILING_FAILED` ×2 (p4, p5 — chart captions with mangled glyph runs).
- **who-wfa (3)** — `MATRIX_AMBIGUOUS` ×1 per page, the identical z-score header block
  (`Z-scores … Year: Month L M S`) on all three pages. One defect, three firings.

`ROUND_TRIP_FAIL` is **two mechanisms under one label** — region-level (`holon.py:493`) and cell-level
(`_emit_roundtrip_fail_cell`, `holon.py:55`, called from `:143,210,310,405`). All 5 corpus firings are
region-level; the cell-level emitter is corpus-dead. A count keyed on the label alone cannot tell them
apart, and a single document triggering the cell-level path could inflate it by hundreds.

## What this does to the spec

1. **§7.4's denominator is 10, not 9** — nine reasons plus the shape-liveness criterion. `TRANSPOSED`
   is the tenth line.
2. **Four reason criteria are met on the "does not fire" arm**, if the plan keeps the two-armed
   wording. That is a real risk to name: four of ten `tab` criteria would read met because the corpus
   never exercises them, which measures the corpus, not the reading. The honest form is closer to the
   vacuity registry's — *fires and is adjudicated, **or** registered idle with a reason* — and the
   registry is the precedent already in the repo (`test_vacuity_registry.py:87`).
3. **The `etkl` adjudications have their evidence.** Four documents escalate nothing; three carry a
   small, legible, per-page escalation surface. Each of the three is one defect repeated, not a
   scatter — which is what an adjudication needs to say.
