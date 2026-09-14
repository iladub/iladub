# Handoff — D2: the adoption gate widened, and the four sites it actually touches

**Serves:** prog:criterion:etkl:04 — the gate half of [[R225]]'s ruled arm B.

**Date:** 2026-09-14. **Branch:** `r225-arm-b-resolution-test`, continuing from `5a893e0`.

**Doc impact: none.** No released term, no vocabulary change; the `.rq` is an internal query.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene, before any code was written,
and each action is typed assertion-or-proposition.

---

## 5. The next concrete action

### 5a. ASSERTED — D2 is FOUR sites, not the three the previous handoff named

Measured by reading the two gates the spec § 1c already paired, and stated here because the prior
handoff's task list omits the third one:

1. `vocab/queries/adoption-candidate.rq` — the candidate AXIOM, run on the pass-1 graph.
2. **`compile.py:1428` — `if datagrid_adopt and asserted_total == 0 and escalated_total > 0`.**
   The document driver adopts by RE-COMPILING the page with `datagrid_adopt=True`, so a page whose
   bands assert anything makes this branch refuse, no grid region is appended, and
   `document.py:1650` refuses with *"no data grid region on the re-compile"*. **Widening the `.rq`
   alone is therefore a no-op** — spec § 1c says the two branches share the precondition; it does
   not say that the second one is a D2 site, and it is.
3. `document.py` — the post-hoc **ink** refusal (never a cell count: spec § 4 D2).
4. `document.py` — § 1g's obligation: an asserting band whose lines the grid re-reads.

### 5b. ASSERTED — the ledger revision forces site 2's supersession predicate to move with it

`compile.py:1479-1483` marks a touched band superseded iff `r.tokens_escalated > 0`, and its own
comment says this predicate *"has to be"* the one `build_ledger` selects by. That selection was
widened to booked ink (`tokens_asserted + tokens_escalated > 0`) in `7f365ce`. So on a page whose
bands assert, a touched ASSERTING band keeps `verdict="asserted"` and its `tokens_asserted`, while
the ledger has already handed that ink to the grid — and `sum(r.tokens_asserted) == asserted_total`
(I5, `test_adoption_document.py:141`, `test_datagrid.py:1149`) breaks from the side nothing tests.
Site 2 must zero it and mark the band superseded, or the identity reopens.

### 5c. RUN, AND REFUTED — D2 alone is NOT inert, and that is the loop's finding

**Read 5c as written below, then this correction: the prediction it orders to be run was run, and
it failed.** Two documents move — apple `adopted () -> (2,)` and bfs `() -> (5,)` — while the other
five stay byte-identical. The refutation is good news rather than bad, and it is the reason the
maintainer's ordering was right: **bfs p5 adopts at 404 cells — exactly [[R225]]'s stated oracle — with
D1 REVERTED**, and ons is untouched. The gain the row costed as D1's belongs to the gate. Full
figures and the isolated § 1g sweep: spec § 9e / § 9f.

The original text, kept because a refuted prediction is evidence:

The design admits a page whose reading is INCOMPLETE (it carries an escalation) and then refuses
unless the grid leaves **strictly less ink unread** than the bands did:
`ledger.escalated_tokens < pages[p].escalated`. Ordinal, no constant, and it is the quantity the
existing gate asks for in its absence-shaped form.

**The prediction: at baseline (D1 reverted), every newly-admitted page REFUSES, so all seven corpus
documents stay byte-identical by canonical graph hash.** If it is false — a pinned document moves —
the predicate is wrong or I1 needs the maintainer, and nothing further should be built on it.
Run it as `scripts/corpus_verdict_snapshot.py` against `snap-base` (taken this session on
`5a893e0`; it is session-local and will be gone).

**Why this order:** sites 1+2+3 are small and produce a `notes` line per refusal, so ONE corpus
sweep answers both *"is it inert"* and *"which pages did it admit"*. Site 4's graph surgery is the
expensive half and must not be written before that answer exists.

### 5d. BUILT AND MEASURED — site 4 refuses where the table is load-bearing, supersedes otherwise

**Status 2026-09-14: this section was PROPOSED and is now shipped as written, with one change.**
"Participates in a document-level fact" became a CLOSURE CHECK — *nothing outside the table's own
subgraph points into it* — plus a chain-membership test, rather than an enumeration of fact types
that would rot as facts are added. The ONS prediction below was never exercised: ons does not adopt
at baseline, so the live case is apple p2 (2 of 29 admitted lines contested, `#table6` withdrawn).
Isolated measurement of this site alone: −93 triples on apple, −254 on bfs, no score moved.

The original text, kept:

An adopted page's pass-1 asserted table survives in the merged graph beside the grid that re-reads
its lines (§ 1g: graincorp-capacity p0 27/27 contested, stem p0 57/57, apple p0 31/31, who-wfa p0
25/25, bfs p6 29/32, ons p4 0/25 — the one disjoint case). Adoption today withdraws only escalation
CANDIDATES, which carry no document-level links; an asserted table does — `tab:continuesTable`,
`_link_columns`, `tab:licenceRefused`, section totals, and `DocumentReport.chains`, all computed
BEFORE adoption runs.

So: **refuse the adoption when a contested asserting band's table participates in any
document-level fact; otherwise withdraw its subgraph and record `dec:supersedes`.** The subgraph
must be computed from `pages[p].graph` (the page's own pass-1 graph, where `_band_subgraph`'s
reachability closure is bounded as designed) and subtracted from the merged graph — NEVER computed
from the merged graph, where the closure reaches the document node and would sweep the document.

**Why this is not a dodge on the one page that matters:** [[R226]] measured that ONS evidences no
leaf header block on any of its nine pages, so `recognized` is `()` and ons's tables participate in
no chain — the document that needs the repair is the one where the withdrawal is safe. **This is a
prediction and it is unrun**: it must be checked on ons p7 under D1, not adopted from this
paragraph.

### 5e. ASSERTED — what this loop must NOT do

D1 stays reverted (`54c0edf`). The maintainer ruled D2 is measured alone. Judging D1's placement
belongs to the loop after this one, on readings.

---

## 1. Where the primaries are

- **The spec** — `docs/superpowers/specs/2026-09-14-the-gate-not-the-predicate-design.md`; D2's
  corrected form is § 4 D2, the ledger contract § 1f, the graph obligation § 1g.
- **The gate** — `vocab/queries/adoption-candidate.rq`; callers `adoption.py:131`,
  `document.py:1629`.
- **The two page-scope branches** — `compile.py:1351` (fallback) and `compile.py:1428` (adoption).
- **The rows** — [[R225]] (this), [[R226]], [[R202]] in `residues-open.md`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| D2 is four sites, `compile.py:1428` among them | 5a above — nowhere else |
| The candidate gate widens to "the page's reading is incomplete" | 5c above |
| The refusal predicate is unread INK, ordinal | spec § 4 D2; 5c |
| Site 4 refuses where the table is load-bearing | 5d above |

## 3. Unverified or assumed

- **5c and 5d entirely**, per their grading.
- The baseline `snap-base` was taken on `5a893e0` in this session's scratchpad and is
  **session-local**; a later session must re-take it before diffing anything.

## 4. What this loop did

Took a baseline corpus snapshot on `5a893e0`; built D2 across the four sites of § 5a; ran the
prediction of § 5c FIRST and had it refuted; measured § 1g's withdrawal in isolation with a second
whole-corpus sweep; re-baselined the four contract pins the widened gate moved, each with its
ruling recorded in its own docstring; and wrote the evidence into the spec as § 9 rather than into
a new document, so the design and its execution sit in one file.

**Shipped, by file:**

| file | what changed |
| --- | --- |
| `vocab/queries/adoption-candidate.rq` | the `NOT EXISTS tab:EntryCell` closure deleted; page scope now carried by the candidate's own `iladub:fromRegion` → `iladub:onPage` |
| `src/iladub/etkl/compile.py` | adoption precondition `asserted_total == 0` dropped; the ordinal unread-ink refusal added; supersession predicate widened to booked ink; the grid region books ADMITTED lines only |
| `src/iladub/etkl/document.py` | § 1g withdraw-or-refuse, decided before any mutation, with the singleton-chain entry dropped |
| `scripts/corpus_snapshot_diff.py` | new instrument — the missing half of `corpus_verdict_snapshot.py` |
| 4 test modules | `test_adoption_gate` (rewritten to the new contract), `test_adoption_document`, `test_escalation_wiring`, `test_apple_statement_headers` |

**The instruments are committed; the three snapshots are NOT** — `snap-base`, `snap-d2`, `snap-d2g`
live in this session's scratchpad and will be gone. A later session re-measuring must re-take a
baseline against a clean tree before it can diff anything, exactly as § 5d of the previous handoff
warned; the figures in spec § 9e are the only surviving record.
