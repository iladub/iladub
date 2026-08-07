# Proving the ordering, and making supersession visible — design

**Date:** 2026-08-07 · **Status:** closed 2026-08-07 ·
**Closes:** R68 (narrowed) and R70 from `docs/superpowers/residues.md` ·
**Predecessor:** `2026-08-07-reading-decision-record-design.md` (slice A, closed) ·
**Specimens:** `tests/etkl/fixtures.py::false_transposed_pdf` /
`::transposed_table_pdf`, and `corpus/ag-trade/cbh-stem-2026-08-03.pdf`

**Doc impact:** increment — no new vocabulary and no new terms; one committed query gains
an optional column and one query is added. A wiki note on reading a superseded chain queues
for the next release. No site page contradicted.

## 1. Why this loop exists

Slice A shipped the reading decision record: every judgement on the band-to-verdict path
emits a `dec:DecisionHolon`, and three committed queries make the reading an audit surface.
It closed with two admissions, both registered rather than hidden. This loop discharges them.

Neither is a code defect. Both are places where the *record is less useful or less honest
than it looks*, which is the only failure mode slice A cared about.

## 2. R68 — the ordering was provable all along

Slice A's §6 required apple band 4's chain to show `looks_transposed` before
`transpose_is_coherent` — the R55 link, the misattribution that motivated the whole
architecture. It was reported **not met**, measured across four documents: every `transposed`
judgement in the corpus chooses `upright`, so the coherence oracle is never consulted.

That measurement is correct and stands. The **conclusion drawn from it was too strong.**
R68's own *what would close it* clause named "a fixture that reaches
`transpose_is_coherent`" — and `tests/etkl/fixtures.py` has had two since before slice A:

| fixture | `looks_transposed` | `transpose_is_coherent` | verdict |
| --- | --- | --- | --- |
| `false_transposed_pdf` (fixtures.py:268) | fires | **refuses** (the `Mix` row is type-mixed) | `escalated TRANSPOSED` |
| `transposed_table_pdf` (fixtures.py:288) | fires | accepts | `asserted` |

Both route through `compile_tables`, so slice A's recorder was **already** emitting their
chains — nobody looked. Measured on this checkout:

```
--- false_transposed ---
  0. multi_table         chosen=single        — single table
  1. kind                chosen=RECORD_TABLE  — flat single-level header
  2. transposed          chosen=transposed    — looks transposed
  3. transpose_coherent  chosen=incoherent    — coherence oracle refused the transposed reading
  4. verdict             chosen=escalated     — TRANSPOSED
--- transposed_table ---
  2. transposed          chosen=transposed    — looks transposed
  3. transpose_coherent  chosen=coherent      — coherence oracle accepted the transposed reading
  5. verdict             chosen=asserted      —
```

`transposed` at order 2, `transpose_coherent` at order 3. That is the R55 link, and
`false_transposed_pdf` exercises the **refusal** branch — precisely the shape R55 got
backwards, where a first gate fires and a second is only then consulted.

The residue was registered without first checking whether an existing fixture already
discharged it. This loop records that, because a register that overstates a gap is the same
class of defect as one that hides it.

## 3. R70 — the audit surface hands back superseded answers silently

Slice A's final fix wave made section repair carry the pass-2 chain into the merged graph and
link it `dec:supersedes` the pass-1 chain (4 edges on CBH, verdict-decision → verdict-decision).
No triple is false: the pass-1 `escalated` verdict is correctly scoped to a decision that is
now the *object* of a supersession.

But the pass-2 chain keeps its own `{page_doc}/r2#region{idx}` URI space, no bridge triple
relates it to `{page_doc}#region{idx}`, and **none of the three shipped queries follow the
edge**. So asking `why-escalated.rq` the obvious question about a repaired region returns the
superseded chain, with nothing saying so.

Two separable harms: you get the stale answer, and you cannot tell. This loop closes both.

## 4. The design

**No `src/` change.** Every artifact here is a query file, a test, or the register. That is
what makes the loop's central constraint self-evident rather than something to re-measure:
the compiler is untouched, so no verdict can move.

### 4.1 R68 — assert the ordering where it is exercised

New `tests/etkl/test_transposed_chain.py` runs the **committed** `judgement-order.rq` and
`why-escalated.rq` against both fixtures, asserting for each:

- `transposed` and `transpose_coherent` are both recorded, and `order(transposed) <
  order(transpose_coherent)` — the R55 link;
- the chosen option on each, so the two branches are distinguished (`incoherent` → verdict
  `escalated` with rationale `TRANSPOSED`; `coherent` → verdict `asserted`).

Tests run the `.rq` files from disk, never inline query text — slice A's rule, because the
queries are the artifact under test.

The two corpus tests keep their `pytest.skip("R68: …")`. Retargeting them at the fixtures
would make the suite fully green and thereby erase the measured fact that no real document
exercises the path. **The skip is the honest signal and it stays.**

### 4.2 R70 — mark the stale chain, and ship the traversal

**`why-escalated.rq` gains an `OPTIONAL ?supersededBy`**, bound at *region* level:

```sparql
OPTIONAL { ?v1 dec:regarding ?region . ?v2 dec:supersedes ?v1 . BIND(?v2 AS ?supersededBy) }
```

Region-level, not verdict-row-level, so **every** row of a superseded chain carries the
marker — a consumer reading any single row learns the whole chain was replaced. The column is
appended **last**, so existing positional access (`r[3]` is still `?rationale`) is unaffected
and slice A's tests keep passing unchanged.

**New `vocab/queries/effective-chain.rq`** returns the live chain for a region: follow
`dec:supersedes` from that region's verdict decision to the superseding verdict, take that
decision's band process, and return its judgements in `dec:order`. When nothing supersedes the
region, it returns that region's own chain — so the query is correct for repaired and
unrepaired regions alike, and a consumer never needs to know which case they are in.

### 4.3 Tests for R70

Against CBH (`repaired_bands=((0,1),(0,3),(0,5),(0,7))`):

- a **repaired** region (e.g. 1): `why-escalated.rq` binds `?supersededBy` on every row, and
  its verdict row still reads `escalated`; `effective-chain.rq` returns the pass-2 chain with
  verdict `asserted`.
- an **unrepaired control** region: `?supersededBy` is unbound, and `effective-chain.rq`
  returns exactly what `why-escalated.rq` returns.

The control is what stops the pair passing for the wrong reason — without it, a query that
returned nothing, or always returned the pass-1 chain, could still satisfy the first case.

## 5. Success criteria

- The R55 ordering is asserted live on both fixtures, both oracle branches, by tests that run
  the committed `.rq` files. No `xfail`, no guard, no skip on the fixture tests.
- `why-escalated.rq` binds `?supersededBy` on every row of a superseded chain and leaves it
  unbound otherwise; slice A's existing query tests pass **unmodified**.
- `effective-chain.rq` returns the pass-2 chain for a repaired region and the region's own
  chain for an unrepaired one.
- **No `src/` file changes.** This is checked by reading the diff, not inferred.
- Corpus scores untouched — guaranteed by construction, and confirmed by one stem+CBH run.
- R68's row is **replaced** by the narrower residue in §6; R70's row is **deleted**.

## 6. What this loop leaves behind

R68 does not vanish; it narrows to what is actually still true and still worth knowing:

> **No real corpus document exercises the transposed path** — the ordering is proven only on
> synthetic fixtures. Every corpus `transposed` judgement chooses `upright` (apple
> `region4-d2`/`region6-d2`, capacity `region3-d2`, WHO `region4-d2`; stem records none at
> all), and CBH was never scanned for it. Closes when a real document that genuinely
> transposes enters the corpus.

That row keeps the corpus gap measurable and keeps the two `pytest.skip`s meaningful.

## 7. Out of scope

- **A bridge triple** relating `{r2_doc}#region{idx}` to `{page_doc}#region{idx}`. The
  `dec:supersedes` traversal is sufficient for the queries, and minting a cross-pass identity
  relation is a modelling decision (are they the same region, or two readings of one band?)
  that deserves its own loop.
- **Sourcing a genuinely transposed corpus document** — the §6 residue.
- **R69** (`escalate_region` puts `dec:confidence` on a region, whose RDFS domain entails the
  region is a `dec:DecisionHolon`). A real modelling question, untouched here.
- **Slice B** (candidates as ontology classes), which R66 is the evidence for.

## 8. Global constraints (carried, per CLAUDE.md)

- **No `src/` change**, therefore no verdict change.
- **No new vocabulary.** `dec:supersedes` already exists (`vocab/ontology/dec.ttl:174`) and
  gained its first producer in slice A.
- Neurosymbolic gate: the two queries are **AXIOM** — declarative SPARQL over an evidence
  graph, open-world, no closed-world derivation and no tuned constant.
- Tests run the committed `.rq` files; query logic is never reimplemented in Python.
- `docs/superpowers/**` is Evidence and immutable after close, so this loop does **not** edit
  slice A's closed spec. Corrections land here and in `residues.md`, the mutable register.

## 9. Measured results (loop close, 2026-08-07)

**Corpus confirmation (controller-run):** `pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q`
→ **13 passed in 253s** (stem 0.9655 / 2152 cells / chain `[3]`; CBH 0.9047) — the exact figures
§4.1's baseline expected, confirming §8's "no `src/` change, therefore no verdict change" by
observation rather than inference. `git diff --stat` for `src/` and `*.ttl` across the whole branch
is **empty**; the whole-branch diff touches only `tests/etkl/test_transposed_chain.py` (new),
`tests/etkl/test_supersession_queries.py` (new), `vocab/queries/effective-chain.rq` (new),
`vocab/queries/why-escalated.rq` (+11/-1 lines: the `?supersededBy` `OPTIONAL` and its header
comment), plus this plan/spec pair.

**R68 — the ordering, proven (`tests/etkl/test_transposed_chain.py`, 3 passed, no skip/xfail on
the fixture tests — only environment `importorskip("reportlab")`/`importorskip("pdfplumber")`
guards):**

```
--- false_transposed_pdf ---            --- transposed_table_pdf ---
  2. transposed  chosen=transposed        2. transposed  chosen=transposed
  3. transpose_coherent  chosen=incoherent 3. transpose_coherent  chosen=coherent
  4. verdict  chosen=escalated TRANSPOSED  5. verdict  chosen=asserted
```

`order(transposed) < order(transpose_coherent)` holds on both branches of the coherence oracle.
The tests were shown to be real gates during Task 1: one assertion was inverted, observed
**FAILING**, then reverted.

**R70 — closed (`tests/etkl/test_supersession_queries.py`, 5 tests, all passing on CBH with
`repaired_bands=((0,1),(0,3),(0,5),(0,7))`):** region 1 (repaired) — `why-escalated.rq` binds
`?supersededBy` on every row and its verdict row still reads `escalated` (the pass-1 chain, as
recorded); `effective-chain.rq` returns the pass-2 chain, verdict `asserted`. Region 0
(unrepaired control) — `?supersededBy` is unbound on every row, and `effective-chain.rq` returns
exactly what `why-escalated.rq` returns. Slice A's `tests/etkl/test_decision_queries.py` shows an
**empty `git diff` against `main`** — unmodified, and still passing.

### Criterion-by-criterion pass over §5

1. *"The R55 ordering is asserted live on both fixtures, both oracle branches, by tests that run
   the committed `.rq` files. No `xfail`, no guard, no skip on the fixture tests."* — **MET.**
   `test_transposed_chain.py` reads `judgement-order.rq`/`why-escalated.rq` from disk (verified by
   reading the test file), runs both fixtures and both branches, 3/3 passing, no
   `skip`/`xfail`/guard on any assertion in the file.
2. *"`why-escalated.rq` binds `?supersededBy` on every row of a superseded chain and leaves it
   unbound otherwise; slice A's existing query tests pass unmodified."* — **MET.**
   `test_a_superseded_chain_says_so_on_every_row` and `test_an_unsuperseded_chain_carries_no_marker`
   cover both halves; `git diff --stat main -- tests/etkl/test_decision_queries.py` is empty and
   the file still passes.
3. *"`effective-chain.rq` returns the pass-2 chain for a repaired region and the region's own
   chain for an unrepaired one."* — **MET.** `test_effective_chain_returns_the_live_reading_after_repair`
   and `test_effective_chain_equals_why_escalated_when_nothing_superseded_it` cover both cases; the
   control (§4.3's point) is present and passing.
4. *"No `src/` file changes. This is checked by reading the diff, not inferred."* — **MET.**
   `git diff --stat main -- src/ '*.ttl'` is empty; the full `git diff --stat main..HEAD` lists only
   docs, tests, and the two `.rq` files.
5. *"Corpus scores untouched — guaranteed by construction, and confirmed by one stem+CBH run."* —
   **MET.** See the controller-run figures above, matching the pre-loop baseline exactly.
6. *"R68's row is replaced by the narrower residue in §6; R70's row is deleted."* — **MET.**
   `docs/superpowers/residues.md` R68 now reads the §6 text (with the overstatement correction
   named in-row); the R70 row no longer exists in the table, and no other row was renumbered.

All six criteria met; none required softening.
