# Handoff — etkl:04 is ready, and the route named for it is REFUTED before it was started

**Topic:** [[etkl:04]] — ONS. The prior handoff's 5a said "author the contract triple and take the
adjudication". **Measured: a contract authored today would ground nothing.**

**Serves:** prog:criterion:etkl:04 — first of 14 `ready` criteria (`vocab/queries/arc-ready.rq`),
carries no `prog:blockedBy`.

**Date:** 2026-09-14. **Tree:** `main` at `d588412`, clean. **No code was written this session.**

**Doc impact: none.**

**Part 5 was written FIRST**, and each action is typed assertion-or-proposition.

---

## 5. The next concrete action

### 5a. ASSERTED — the subject is NOT the contract; it is that ONS's grid carries no column labels

The outcome is known and doing it *is* the work. etkl:04's bar is exact: `cor:CompilesAbove` + a
pinned `cor:scoreFloor` + an adjudication whose rationale **accepts** the score, "not one that holds
it" (`tests/arc-manifest.ttl:265`). The precedent for getting there is graincorp-capacity, whose
2026-08-20 HOLD named three steps and whose 2026-09-13 lift discharged them
(`tests/corpus-manifest.ttl:74` and `:76`). Step (1) is "author a `cor:contract` / `cor:terms` /
`cor:shapes` triple"; step (2) is `test_corpus.py::test_grounding_where_contracted` passing.

**Step (2) cannot pass on ONS today, and step (1) is therefore premature.** Measured on `main` at
`d588412`:

```
tab:EntryCell 554   tab:LeafRow 93   tab:GridColumn 12   tab:MeasureColumn 10
tab:DataGrid    2   tab:HierarchicalTable 1   tab:RecordTable **0**
distinct column labels across GridColumn/LeafColumn: **0** (0 label triples)
the only DataGrid labels: "UniformGrid on page 7: 46 rows x 6 columns" (and p8)
```

`feed.table_records(graph)` (`src/iladub/feed.py:457`) reads **only** `tab:RecordTable` and
`tab:HierarchicalTable`. ONS has zero of the former and one of the latter holding **2** entry
cells, so the record feed is empty-or-trivial and every one of the 554 carried cells is invisible
to it. `ground.exact_field` (`src/iladub/ground.py:96`) grounds by matching a surface concept's
TEXT to a contract field's property NAME, and the corpus battery runs an **abstaining** proposer
(`test_corpus.py:159`), so exact match is the only path open. With no labels there is no match, and
`test_grounding_where_contracted`'s closing assertion — *"a contracted document must ground
SOMETHING"* — fails.

**So the next loop's subject is: make ONS's adopted reading carry its columns' identity** — either
by emitting the datagrid's columns with labels, or by typing the adopted region such that
`table_records` can read it with a header path. Only then is the contract authorable.

### 5b. PROPOSED — p4's HierarchicalTable may not be the SIC2007 surface the HOLD is about

**Rests on a prediction that must be RUN.** p4 is the one non-datagrid asserting region (19 cells,
`UNSUPPORTED_TABLE asserted`), and its `tab:HierarchicalTable` `p4#htable2` shows only **2** entry
cells under its own URI space with no labels on them. The HOLD's complaint is about "nine pages of
a statistical release with hierarchical SIC2007 section headers and a Total aggregate column". If
p4's htable is a fragment rather than that table, then **no page of ONS currently carries the
structure the adjudication would have to accept**, and the gap is larger than labels alone.

Cheap to settle: dump `p4#htable2`'s rows/columns and compare against page 4 of the PDF. Minutes.

### 5c. ASSERTED — what this session must NOT be read as having done

No code, no spec, no contract. [[R226]] (no leaf header block on any ONS page) and [[R229]]
(adopted readings drop out of `chains`) are untouched and may both bear on 5a — R226 especially,
since a leaf header block is where column identity would come from. [[R228]] stays open on its
reachability half only.

---

## 1. Where the primaries are

- **The bar** — `tests/arc-manifest.ttl:265` (statement), `tests/corpus-manifest.ttl:94` (the node),
  `:109` (ONS's HOLD rationale — read it before writing anything).
- **The precedent** — `tests/corpus-manifest.ttl:74` (capacity's three-step HOLD) and `:76` (the
  lift, discharged by four independent measurements *because the maintainer declined a check
  delegated to them*). That is the standard step (3) must meet.
- **The pattern to copy** — `examples/shipping/capacity-{contract,terms,shapes}.ttl`, 39/25/29
  lines. A contract is `etkl:SemanticDataContract` + `etkl:targetClass` + optional
  `etkl:requiresKnowledge` + `etkl:hasField` → `etkl:Field` (`etkl:fillsProperty`, optional
  `etkl:admissibleScheme`).
- **Where an ONS triple would live** — `examples/gov-stats/` does not exist; the manifest points
  only at `examples/shipping/`, and `examples/tables/` holds vocabulary conformance fixtures, not
  per-document triples.
- **The grounding path** — `feed.table_records` → `feed.ground_document` → `ground.exact_field` /
  `scheme_member` / `marker_field`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| etkl:04's subject is column identity, not the contract | this file only — nothing else records it |
| Do not author the triple until `table_records` sees ONS's cells | this file only |
| Scope a future loop to steps (1)+(2); leave step (3) to its own loop | this file only |

## 3. Unverified or assumed

- **5b entirely**, per its grading.
- **Whether labelling the datagrid's columns is even the right repair** is unexamined: the
  alternative is that the adopted region should be a `tab:RecordTable` with a header path, which is
  a different change. Nothing here measures which.
- **Whether ONS's 0.7712 would survive that repair** is unmeasured.
- The `table_records` call in this session's probe raised `TypeError` — a wrong signature on my
  part (it takes the graph alone). The zero-record conclusion rests on the class census and on
  reading `:457`, **not** on a successful call.

## 4. What this session did

Re-oriented from the repo, confirmed etkl:04 is `ready` by running `arc-ready.rq` rather than
trusting the prior handoff, read the bar and the precedent, then measured what ONS actually carries
— and found the prior handoff's asserted next action rests on a false premise. **That is the whole
output, and it is worth more than a spec written against an imagined reading would have been.**

**Why this stops here.** Writing the spec is *originating* work, this session had already run long,
and `plimslop preflight` reports "unmeasured — no turn recorded for this project", so the gate had
no figure to give. Under § Loop & context hygiene the remedy for originating work in a long session
is a handoff written while still accurate, not a spec written past the floor.
