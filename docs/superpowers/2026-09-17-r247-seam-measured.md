# R247's seam, measured: the one-node graph is a template flag, not a tool limit

**Topic:** The docling-graph handoff's 5b named one fact to measure before designing [[R247]]'s
hard-table head-to-head. It was measured, offline and at no API cost, and the feared outcome does not
hold — but what replaces it is not a graph comparison either.

**Serves:** maintenance — [[R247]], under `2026-08-15-docling-positioning.md` (still NOT ACCEPTED, [[R246]])

**Date:** 2026-09-17. **Tree:** branch `r247-seam-entity-flag`, cut from `main` at `12ca369`.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — nothing here is a loop's to run next; the two open calls are the maintainer's

Unchanged from `2026-09-17-docling-graph-benchmark-handoff.md` § 5d: rule on [[R246]], and decide
whether the v1.9.1 defect is reported upstream. This file changes neither. It removes one reason
R247 could not be *designed*; it does not make R247 the next subject, and R247 serves no arc
criterion.

### 5b. PROPOSED — if R247 is ever run, its unit is the CELL TRIPLE, not the graph

**Typed PROPOSED because it rests on an extraction this session did not run** (§ 3).

The measurement below says a graph exists on docling-graph's side whenever the template asks for
one. It also says that graph is a **star**: root → row, with the row's values still a positional
list (`values_by_period`) beside a positional list of period names on the root
(`periods_covered`). No edge joins a value to its column. So "compare the graphs" would compare
iladub's cell↔header structure against positions in two lists. The unit both sides can actually
yield is `(row label, column position or label, value)`, and it can be read from the embedded form
just as well as from the flipped one — which means **the flag does not need flipping to run R247**,
and the extraction path the benchmark already validated can be reused as it stands.

**If this is wrong, the next session finds out in minutes**: read one recorded `graph.json` and
try to build the triples.

---

## 1. What was measured

The handoff's seam: *"If a table template also produces one node with embedded lists, then 'compare
the graphs' has no graph on one side."*

**First, from the recorded runs, for free.** Every run that wrote a `graph.json` — 15 of the
harness's 17 output directories, both template families (`FinancialStatement` induced, `HierarchicalTable` compiled
from `tab.ttl`) — is **1 node, 0 edges**. So the table template does produce one node. Read alone,
that confirms the fear.

**Then, why.** `graph_converter.py:9-10` states the rule and `:529-531` applies it: a model is a
separate node unless its `model_config` says `is_entity=False`, in which case it is embedded in its
parent as a dict. **The converter's default is `True`.** Both generated templates set `False` on
every non-root class (3 of 3 in `apple_induced.py`, 6 of 6 in `tab_min.py`), and `templategen`
does that by rule, not by accident: `kind == "component"` renders `is_entity=False`
(`templategen/renderer.py:449-451`), a component may carry no identity field (`spec.py:233-237`),
and an entity must carry at least one (`spec.py:246`). So a class with no identity field can only
be a component. Table rows and cells have no natural identity, which is why both generators
embedded them.

**Then, the flip, with a control.** `scripts/thirdparty/docling_benchmark/entity_flip_seam.py`
re-validates a recorded extraction against the same template with the flags turned, and hands it to
docling-graph's own `GraphConverter`. No LLM, no document. Run 2026-09-17, docling-graph 1.9.1:

```
apple_induced  control  flags=3 nodes=1  edges=0   types={'FinancialStatement': 1}
apple_induced  flipped  flags=3 nodes=33 edges=32  types={'LineItem': 20, 'SegmentSales': 6,
                                                          'CategorySales': 6, 'FinancialStatement': 1}
                                                   edge_labels={'CONTAINS_LINE': 32}
tab_min        control  flags=6 nodes=1  edges=0   types={'HierarchicalTable': 1}
tab_min        flipped  flags=6 nodes=4  edges=4   types={'Cell': 1, 'HeaderNode': 1,
                                                          'LeafColumn': 1, 'HierarchicalTable': 1}
```

The **control arm reproduces the recorded 1/0 on both templates**, which is what licenses reading
the flipped arm: the offline path is the path the CLI took. Flipped, the same extraction is 33
nodes and 32 edges. `tab_min`'s 4 nodes are the known ~1/32 extraction, not a converter effect.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| "1 node, 0 edges" is the generated template's `is_entity=False`, not a docling-graph limit | § 1; [[R247]] |
| The flipped graph is a star with positional values; no value↔column edge exists | § 5b |
| R247's comparison unit is the cell triple, readable without flipping | § 5b — PROPOSED |
| The uniform-template tension (~1/32) is untouched by this | benchmark handoff § 5b |

## 3. Unverified or assumed

- **Extraction under a flipped template is unrun.** `is_entity` is also read by the dense
  extraction catalog (`core/extractors/contracts/dense/catalog.py:42-55, :230-239`), so an LLM run
  with the flags turned is a different extraction and may yield different content. Only the
  *conversion* of an already-recorded extraction was measured.
- **n = 2 templates, 1 page (apple p0), 1 recorded extraction each.** Neither is a hard table.
- **A hand-written template could give cells identity** (and value→column edges). Whether that is
  still "their tool on their terms" is R247's design question, not answered here.
- **The harness is still in `/private/tmp`** under the 2026-09-17 session's scratchpad; it existed
  when this ran. The rebuild recipe is the benchmark handoff's § 5a.

## 4. Cost

One session, no API calls, no install, no production code touched.
