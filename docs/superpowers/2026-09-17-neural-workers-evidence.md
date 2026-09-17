# Evidence — a dense page, and what a small model can and cannot be asked

**Serves:** maintenance — the measurements behind `2026-09-17-neural-workers-handoff.md`

**Date:** 2026-09-17. **Tree:** branch `neural-workers-handoff`, cut from `main` at `b7dd468`.

**Doc impact: none.**

Two measurements, both run in one session and both committed with their instruments, because a
measurement that lives only in a scratchpad is [[R245]]'s failure.

---

## 1. docling-graph on a dense ruled page — the first arm of [[R247]]

**Page:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf`, page index 1 — 1026 words, **45 slot
rows** (counted from the PDF text: 45 five-digit references, 45 distinct).

**On their terms.** Their own induced template (`template from-docs`, `openai/gpt-4.1`), committed
as `scripts/thirdparty/docling_benchmark/graincorp_induced_template.py` because induction is not
reproducible. It is a good template: `Slot`, `Exporter`, `Ship`, `Port`, `Commodity` are real
entities with identity — so, unlike every arm before it, this run yields a real graph.

**A SECOND defect in v1.9.1, same normalizer.** The first run fell back to legacy mode again:
`Invalid schema … $ref cannot have keywords {'description', 'default', 'examples'}` — the induced
enum. The committed patch (`docling_strict_schema_patch.py`) now strips siblings of `$ref` too.
Degraded run: 6 slots, every `exporter`/`ship`/`commodity`/`port` `None`, every date lost to
"best-effort salvage". **Discard it; the clean run is the measurement.**

**Clean run** (no fallback, no salvage, 124 s, 58 nodes / 146 edges), scored by
`scripts/thirdparty/docling_benchmark/dense_page_row_check.py`:

```
rows on page 45 | slots extracted 13 | real references 13
  59845: not on its own row -> ['10:00:00 AM']
  60954: not on its own row -> ['8:45:00 AM', '3:05:00 PM']
  60952: not on its own row -> ['GCOP']
slots clean 10 | slots carrying another row's value 3
```

iladub on the same page, from the same day's census (`refusal_population.txt`): score **0.9706**,
825 tokens asserted, 25 escalated in one `UNSUPPORTED` region.

**What it establishes.** 13 of 45 rows carried, and 3 of the 13 carry a value that belongs to a
neighbouring row. Every such value is *verbatim* — present on the page — so their provenance ladder
passes it. **The morning benchmark's "zero fabrication" holds and is the wrong question on a dense
page: the failure class is misattribution, and verbatim grounding cannot see it.**

**Where it starts.** Before the LLM: docling's grid for the page is 59×23 and its markdown fuses
rows (`60954 59846 Total`, `8:45:00 AM 10:00:00 AM` in single cells). The model is handed a
scrambled table. Not context length — ~8.5k input tokens against a 128k limit.

**Not established.** n = 1 page, 1 run, 1 model. Why extraction stopped at 13 is unknown (no
truncation or cardinality message in the log). The row check is lenient by construction (its
docstring says how), so 3 is a floor. iladub's figure is the census's, not a fresh compile.

## 2. One proposer, four renderings, two small models

**Instrument:** `scripts/neural_worker_demo/` — the shipped `ProposeHeaderRowRoles` against three
variants, 8 runs each, dispatched through BAML's generated async client. Run 2026-09-17:

```
gpt-4.1-nano  baseline  in= 969 out= 193 correct=3/8 wall= 5.2s
gpt-4.1-nano  outonly   in= 960 out=  14 correct=0/8 wall= 1.7s
gpt-4.1-nano  lean      in= 365 out=  32 correct=0/8 wall= 1.7s
gpt-4.1-nano  lean2     in= 434 out=  85 correct=0/8 wall= 2.4s
gpt-4.1-mini  baseline  in= 969 out= 186 correct=7/8 wall= 2.9s
gpt-4.1-mini  outonly   in= 960 out=   9 correct=6/8 wall= 1.1s
gpt-4.1-mini  lean      in= 365 out= 214 correct=0/8 wall= 4.1s
gpt-4.1-mini  lean2     in= 434 out=  63 correct=0/8 wall= 1.6s

8 outonly calls on mini: sequential 7.1s | asyncio.gather 1.0s
```

Three earlier runs the same day agree in every direction (mini baseline 6–7/8, outonly 6/8, both
lean variants 0–1/8, nano 0–2/8 throughout).

| variant | what changed | held? |
| --- | --- | --- |
| `outonly` | instructions untouched; return type is `HeaderRowRole[]`, an enum with 1-char `@alias` codes; no `confidence`, no `rationale` | **yes** — output ~190 → 9 tokens, wall time more than halved, accuracy within noise of baseline |
| `lean` | prompt compressed, row-major table rendering, `...` reasoning scaffold | **no** — the compression deleted the one load-bearing rule (*stacked fragments compose top to bottom*) |
| `lean2` | that evidence moved into the data (column-major, names pre-composed); scaffold forced before the answer | **no** — the model now reasons first, confidently, to the wrong reading |
| async | `asyncio.gather` over the generated `async_client` | **yes** — ~7× on 8 calls |

**What it establishes.** The safe savings are on the **output** side and in **dispatch**. The
shipped schema puts `rationale` *after* `roles`, so it is written after the decision: it buys
nothing toward the answer and is ~95% of the output tokens. Prompt *text* is load-bearing and a
shorter one is a proposition. A reasoning scaffold does not give a weak model the missing rule; it
makes it commit to its first idea. **nano is below the floor for this judgement even with the
shipped prompt.**

**Not established — and this is the important half.** One hand-built input, which is the shipped
prompt's **own worked example** ("Date of Grain … Commencement"), so the comparison is tilted
toward the baseline. OpenAI models, not the Haiku the repo ships on (the session's
`ANTHROPIC_API_KEY` returned 401). Iteration was stopped after `lean2` deliberately: tuning a
prompt against one example is overfitting. **This demonstrates techniques; it evaluates nothing.**

## 3. Two facts about the shipped proposers, measured while writing the handoff

- **`rationale` and `confidence` are consumed.** `grep -rn "\.rationale\|\.confidence" src/iladub`
  (excluding `baml_client`) → 43 lines; the proposal's `rationale` flows into `dec:rationale` on the
  promotion decision (`etkl/promote.py:85-87`). Dropping them from the wire is therefore a change to
  what a decision holon records, not a free optimisation.
- **`ProposeHeaderSpan` is called and does not exist.** `etkl/propose.py:88` calls
  `sync_client.b.ProposeHeaderSpan`; `grep -rn ProposeHeaderSpan baml_src baml_client/sync_client.py`
  → no match. A live call through that seam would raise. Unexplained here; not investigated.
- Every live proposer call is `sync_client` (7 call sites; no `async_client`, no `asyncio` anywhere
  in `src/iladub` outside `baml_client`).
