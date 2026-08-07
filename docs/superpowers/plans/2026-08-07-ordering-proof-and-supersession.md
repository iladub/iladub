# Ordering Proof and Supersession Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the R55 judgement-ordering link on the fixtures that actually exercise it, and stop the audit surface silently returning superseded chains after section repair — closing R68 (narrowed) and R70.

**Doc impact:** none for this plan file — the loop's `Doc impact: increment` is declared in the design spec (`2026-08-07-ordering-proof-and-supersession-design.md`).

**Architecture:** Three tasks, none of which touches `src/`. Task 1 adds a test file that runs the committed `judgement-order.rq` / `why-escalated.rq` against two pre-existing synthetic fixtures where `looks_transposed` fires and the coherence oracle is genuinely consulted. Task 2 adds an `OPTIONAL ?supersededBy` column to `why-escalated.rq` and a new `effective-chain.rq` that follows `dec:supersedes`, tested against CBH's repaired regions plus an unrepaired control. Task 3 updates the register and closes the spec.

**Tech Stack:** Python 3.11+/pytest, rdflib SPARQL, reportlab (fixture PDFs), pdfplumber, the owned `dec:` vocabulary (no new terms).

**Spec:** `docs/superpowers/specs/2026-08-07-ordering-proof-and-supersession-design.md` — read it first, especially §4 (the design) and §6 (what the loop leaves behind).

## Global Constraints

- **NO `src/` FILE MAY CHANGE.** This is the structural guarantee that no verdict can move. Every artifact is a `.rq` file, a test, or a doc. If you believe a `src/` change is needed, **STOP and report** — do not make it.
- **No new vocabulary.** `dec:supersedes` already exists (`vocab/ontology/dec.ttl:174`, domain and range both `dec:DecisionHolon`) and got its first producer in slice A. Add no term to any `.ttl`.
- **Tests must run the committed `.rq` files read from `vocab/queries/`** — never inline query text, never reimplement query logic in Python. The queries are the artifact under test.
- **The two corpus `pytest.skip("R68: …")` calls STAY.** They are in `tests/etkl/test_decision_queries.py::test_judgement_order_answers_the_r55_question` and `tests/etkl/test_decisionlog.py::test_band_4_records_transposed_before_coherence`. Retargeting them at fixtures would erase the measured fact that no real document exercises the path. Do not touch them.
- **Slice A's existing query tests must pass UNMODIFIED.** The new `?supersededBy` column goes **last** in the `SELECT`, so positional access (`r[3]` is `?rationale`) is unchanged.
- **Gate (CLAUDE.md §8):** the queries are **AXIOM** — declarative SPARQL over an evidence graph. The `FILTER NOT EXISTS` in Task 2's `effective-chain.rq` is a *holon-scoped* closed-world guard (query-local, scoped to one region), which CLAUDE.md §8 expressly permits; the graph stays open. No tuned constant anywhere.
- **Only emit/assert what the record supports.** If a query returns something different from what this plan expects, investigate and report which is right — never weaken an assertion to make it pass.
- **Broken system git on this machine:** every git command as `export PATH=/opt/homebrew/bin:$PATH && git …`.
- **`timeout` does not exist on this macOS shell.** Do not use it. Run suites in the FOREGROUND.
- **Working directory:** `/Volumes/WD Green/dev/git/iladub` (contains a space — quote it).
- **Branch:** `loop-ordering-supersession` — already created off `main`; the design spec is already committed there.
- Do **not** run the full suite or the corpus suites — those are the CONTROLLER's job.

---

### Task 1: Prove the ordering where it is exercised (R68)

**Files:**
- Create: `tests/etkl/test_transposed_chain.py`

**Interfaces:**
- Consumes: `tests.etkl.fixtures.false_transposed_pdf` and `.transposed_table_pdf` (both already exist, `tests/etkl/fixtures.py:268` and `:288`); `iladub.etkl.compile_tables`; `iladub.etkl.compile._DOC`; the committed `vocab/queries/judgement-order.rq` and `vocab/queries/why-escalated.rq`.
- Produces: nothing later tasks depend on.

**Background you need.** Both fixtures compile through `compile_tables`, so slice A's recorder already emits their decision chains. Measured on this checkout, both put the whole table in **`region0`**:

```
--- false_transposed ---
  0. multi_table         chosen=single        — single table
  1. kind                chosen=RECORD_TABLE  — flat single-level header
  2. transposed          chosen=transposed    — looks transposed
  3. transpose_coherent  chosen=incoherent    — coherence oracle refused the transposed reading
  4. verdict             chosen=escalated     — TRANSPOSED
--- transposed_table ---
  0. multi_table         chosen=single        — single table
  1. kind                chosen=RECORD_TABLE  — flat single-level header
  2. transposed          chosen=transposed    — looks transposed
  3. transpose_coherent  chosen=coherent      — coherence oracle accepted the transposed reading
  4. region_tiles        chosen=tiles         — region_tiles validated the 6 entries asserted into scratch
  5. verdict             chosen=asserted      —
```

Assert the **relative** order (`transposed` before `transpose_coherent`), not the literal indices 2 and 3 — a future judgement inserted earlier in the band loop would shift the absolute numbers without breaking the R55 claim, and pinning absolutes would make this test brittle for no gain.

- [ ] **Step 1: Write the failing test** — create `tests/etkl/test_transposed_chain.py`:

```python
"""The R55 ordering link, asserted where it is actually exercised
(spec 2026-08-07-ordering-proof-and-supersession-design.md §4.1).

R55's misattribution was claiming a gate failed "solely because" of one observation, when a
DIFFERENT gate had fired first and the second was only then consulted. `dec:order` is what
makes that answerable. No corpus document reaches the coherence oracle (R68's narrowed row),
but these two fixtures do — and they cover BOTH branches of it.

These tests run the COMMITTED .rq files; query logic is never reimplemented here.
"""
import os

import pytest

pytest.importorskip("reportlab")
pytest.importorskip("pdfplumber")

from rdflib import URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDIR = os.path.join(ROOT, "vocab", "queries")


def _run(name, g, region):
    q = open(os.path.join(QDIR, name), encoding="utf-8").read()
    return [tuple(r) for r in g.query(q, initBindings={"region": region})]


def _compile(fixture, tmp_path, stem):
    from iladub.etkl import compile_tables
    from iladub.etkl.compile import _DOC
    p = tmp_path / f"{stem}.pdf"
    fixture(str(p))
    return compile_tables(str(p)).graph, URIRef(f"{_DOC}#region0")


def _order(g, region):
    """{judgement label: dec:order} for one region, via the committed query."""
    return {str(j): int(o) for j, o in _run("judgement-order.rq", g, region)}


def _chain(g, region):
    """{judgement label: (chosen, rationale)} via the committed why-escalated.rq."""
    return {str(r[1]): (str(r[2]), str(r[3])) for r in _run("why-escalated.rq", g, region)}


def test_refusal_branch_records_transposed_before_the_coherence_oracle(tmp_path):
    """THE R55 SHAPE: looks_transposed fires FIRST; the coherence oracle is consulted
    SECOND and refuses. A reader of this chain cannot mistake the second gate for the cause."""
    from tests.etkl.fixtures import false_transposed_pdf
    g, region = _compile(false_transposed_pdf, tmp_path, "false_transposed")

    order = _order(g, region)
    assert "transposed" in order, f"transposed judgement not recorded; got {sorted(order)}"
    assert "transpose_coherent" in order, \
        f"the coherence oracle was not consulted; got {sorted(order)}"
    assert order["transposed"] < order["transpose_coherent"], \
        f"ordering inverted: {order}"

    chain = _chain(g, region)
    assert chain["transposed"][0] == "transposed"
    assert chain["transpose_coherent"][0] == "incoherent"
    assert chain["verdict"][0] == "escalated"
    assert chain["verdict"][1] == "TRANSPOSED"


def test_acceptance_branch_records_the_same_ordering(tmp_path):
    """The other branch: the oracle accepts and the region compiles. The ordering claim must
    hold regardless of which way the second gate goes."""
    from tests.etkl.fixtures import transposed_table_pdf
    g, region = _compile(transposed_table_pdf, tmp_path, "transposed_table")

    order = _order(g, region)
    assert order["transposed"] < order["transpose_coherent"], f"ordering inverted: {order}"

    chain = _chain(g, region)
    assert chain["transpose_coherent"][0] == "coherent"
    assert chain["verdict"][0] == "asserted"


def test_the_refusal_is_reachable_by_query_alone(tmp_path):
    """§4's standard: the question must be answerable from the record BY QUERY. Ask
    what-was-considered.rq what the coherence oracle had as options and which it took."""
    from tests.etkl.fixtures import false_transposed_pdf
    g, region = _compile(false_transposed_pdf, tmp_path, "false_transposed")
    rows = _run("what-was-considered.rq", g, region)
    opts = {str(o) for j, o, _ in rows if str(j) == "transpose_coherent"}
    assert opts == {"coherent", "incoherent"}, opts
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_transposed_chain.py -v`
Expected: FAIL — the file does not exist yet at Step 1, so this is the first run after creating it. It should **PASS immediately**, because the record these tests assert is already emitted by slice A. That is expected and correct: this task proves an existing capability rather than adding one.

**If any test FAILS, do not adjust the test.** Report exactly which assertion failed and the actual chain you observed — a mismatch means the measured behaviour in this plan's Background is wrong, and the controller needs to know that, not a test bent to fit.

- [ ] **Step 3: Confirm the tests are real gates, not vacuous**

A test that passes on the first run has not shown it can fail. Prove it can:

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python - <<'EOF'
import tempfile, os
from tests.etkl.fixtures import false_transposed_pdf
from iladub.etkl import compile_tables
from iladub.etkl.compile import _DOC
from rdflib import URIRef
d = tempfile.mkdtemp(); p = os.path.join(d, "f.pdf"); false_transposed_pdf(p)
g = compile_tables(p).graph
q = open("vocab/queries/judgement-order.rq", encoding="utf-8").read()
rows = [(str(j), int(o)) for j, o in g.query(q, initBindings={"region": URIRef(f"{_DOC}#region0")})]
print(sorted(rows, key=lambda r: r[1]))
EOF
```

Paste the output in your report. Then temporarily change one assertion in
`test_refusal_branch_records_transposed_before_the_coherence_oracle` to the opposite
(`order["transposed"] > order["transpose_coherent"]`), re-run that one test, confirm it
**FAILS**, and revert. Paste both outputs. A test never observed failing is not yet known to work.

- [ ] **Step 4: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add tests/etkl/test_transposed_chain.py && git commit -m "test(loop-ordering-supersession): the R55 ordering, proven on both oracle branches

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Mark the stale chain and ship the traversal (R70)

**Files:**
- Modify: `vocab/queries/why-escalated.rq`
- Create: `vocab/queries/effective-chain.rq`
- Create: `tests/etkl/test_supersession_queries.py`

**Interfaces:**
- Consumes: `iladub.etkl.document.compile_document` and `.page_doc_uri`; the `dec:supersedes` edges slice A emits at `src/iladub/etkl/document.py:1283` (`v2 dec:supersedes v1`, both verdict `dec:DecisionHolon` nodes).
- Produces: `vocab/queries/effective-chain.rq`, taking a bound `?region` and returning `?order ?judgement ?chosen ?rationale`.

**Background you need.** On `corpus/ag-trade/cbh-stem-2026-08-03.pdf`, section repair adopts a pass-2 re-read for `repaired_bands=((0,1),(0,3),(0,5),(0,7))` — page 0, band indices 1, 3, 5, 7. For those bands the merged graph holds **both** chains: the pass-1 chain under `{page_doc}#region{idx}-*` (verdict `escalated`) and the pass-2 chain under `{page_doc}/r2#region{idx}-*` (verdict `asserted`), joined by `v2 dec:supersedes v1` on the two verdict decisions. Bands 0, 2, 4, 6, 8, 9 are unrepaired and have one chain only.

Region IRIs come from `page_doc_uri(0)` — do **not** hardcode them: `URIRef(f"{page_doc_uri(0)}#region{idx}")`.

`compile_document` on CBH takes several minutes, so compile it **once** in a module-scoped fixture.

- [ ] **Step 1: Write the failing tests** — create `tests/etkl/test_supersession_queries.py`:

```python
"""After section repair the record holds TWO chains for a band. Asking the obvious question
must not silently return the superseded one (spec §4.2/§4.3).

Both queries are read from disk — the .rq files are the artifact under test.
"""
import os

import pytest

from rdflib import URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDIR = os.path.join(ROOT, "vocab", "queries")
CBH = os.path.join(ROOT, "corpus", "ag-trade", "cbh-stem-2026-08-03.pdf")
pytestmark = pytest.mark.skipif(not os.path.exists(CBH), reason="corpus doc not fetched")

REPAIRED = 1        # in repaired_bands ((0,1),(0,3),(0,5),(0,7))
UNREPAIRED = 0      # the control


@pytest.fixture(scope="module")
def cbh():
    """Compile CBH once — it takes minutes. Returns (merged graph, page-0 doc URI)."""
    from iladub.etkl.document import compile_document, page_doc_uri
    rep = compile_document(CBH)
    return rep.graph, page_doc_uri(0)


def _run(name, g, region):
    q = open(os.path.join(QDIR, name), encoding="utf-8").read()
    return [r.asdict() for r in g.query(q, initBindings={"region": region})]


def _region(page_doc, idx):
    return URIRef(f"{page_doc}#region{idx}")


def test_a_superseded_chain_says_so_on_every_row(cbh):
    """The silent-misleading half of R70: a consumer reading ANY row must learn the chain
    they were handed has been replaced."""
    g, page_doc = cbh
    rows = _run("why-escalated.rq", g, _region(page_doc, REPAIRED))
    assert rows, f"no chain for repaired region {REPAIRED}"
    for r in rows:
        assert "supersededBy" in r, f"row without the marker: {r}"
    verdicts = [r for r in rows if str(r["judgement"]) == "verdict"]
    assert verdicts and str(verdicts[0]["chosen"]) == "escalated", \
        "the pass-1 chain should still read escalated — this query returns it as recorded"


def test_an_unsuperseded_chain_carries_no_marker(cbh):
    """The control. Without it, a query that ALWAYS bound the marker would pass the test
    above for the wrong reason."""
    g, page_doc = cbh
    rows = _run("why-escalated.rq", g, _region(page_doc, UNREPAIRED))
    assert rows, f"no chain for unrepaired region {UNREPAIRED}"
    for r in rows:
        assert "supersededBy" not in r, f"marker bound on an unsuperseded chain: {r}"


def test_effective_chain_returns_the_live_reading_after_repair(cbh):
    """The stale-answer half of R70."""
    g, page_doc = cbh
    rows = _run("effective-chain.rq", g, _region(page_doc, REPAIRED))
    assert rows, f"effective-chain returned nothing for repaired region {REPAIRED}"
    verdicts = [r for r in rows if str(r["judgement"]) == "verdict"]
    assert verdicts, f"no verdict in the effective chain: {rows}"
    assert str(verdicts[0]["chosen"]) == "asserted", \
        f"effective chain still reports the superseded verdict: {verdicts[0]}"


def test_effective_chain_equals_why_escalated_when_nothing_superseded_it(cbh):
    """A consumer must never need to know which case they are in."""
    g, page_doc = cbh
    region = _region(page_doc, UNREPAIRED)
    eff = [(int(r["order"]), str(r["judgement"])) for r in _run("effective-chain.rq", g, region)]
    why = [(int(r["order"]), str(r["judgement"])) for r in _run("why-escalated.rq", g, region)]
    assert eff == why, f"diverged on an unrepaired region:\n eff={eff}\n why={why}"


def test_effective_chain_is_ordered(cbh):
    g, page_doc = cbh
    orders = [int(r["order"]) for r in _run("effective-chain.rq", g, _region(page_doc, REPAIRED))]
    assert orders == sorted(orders), f"not ordered: {orders}"
```

- [ ] **Step 2: Run — verify it fails**

Run: `cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_supersession_queries.py -q`
Expected: FAIL — `effective-chain.rq` does not exist (the `open()` raises `FileNotFoundError`), and the marker tests fail because `why-escalated.rq` has no `?supersededBy` yet.

- [ ] **Step 3: Add the marker to `vocab/queries/why-escalated.rq`**

Replace the file with exactly this — note `?supersededBy` is **last** in the `SELECT`, so slice A's positional access (`r[3]` is `?rationale`) is unchanged:

```sparql
# why-escalated.rq — the chain of judgements for one region, in the order they were made,
# each with its rationale and (where the candidate was refuted) the observation that killed
# it. Answers spec 2026-08-07 §4 question 1: "why was this region escalated?"
#
# ?supersededBy is bound when a LATER reading of this band replaced this one (section repair
# adopts a pass-2 re-read and links the two verdict decisions with dec:supersedes). It binds
# at REGION level, so every row of a superseded chain carries it — a consumer reading any one
# row learns the whole chain was replaced. Follow effective-chain.rq for the live reading.
PREFIX dec: <https://w3id.org/iladub/dec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?order ?judgement ?chosen ?rationale ?supersededBy WHERE {
  ?d a dec:DecisionHolon ; dec:regarding ?region ; dec:order ?order ;
     rdfs:label ?judgement ; dec:rationale ?rationale .
  OPTIONAL { ?d dec:chosen/rdfs:label ?chosen }
  OPTIONAL {
    ?v1 dec:regarding ?region .
    ?v2 dec:supersedes ?v1 .
    BIND(?v2 AS ?supersededBy)
  }
}
ORDER BY ?order
```

- [ ] **Step 4: Create `vocab/queries/effective-chain.rq`**

```sparql
# effective-chain.rq — the LIVE chain of judgements for one region: the reading that was not
# superseded. Section repair adopts a pass-2 re-read of a band and links the two verdict
# decisions with dec:supersedes, so asking why-escalated.rq the obvious question about a
# repaired region returns the SUPERSEDED reading. This query follows that edge.
#
# Correct for both cases, so a consumer never needs to know which one they are in: if a
# superseding reading exists, its chain is returned; otherwise the region's own chain is.
# The FILTER NOT EXISTS is a HOLON-SCOPED closed-world guard (query-local, scoped to this one
# region, per CLAUDE.md §8) — it selects between two present readings, it never derives a
# fact from absence.
PREFIX dec: <https://w3id.org/iladub/dec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?order ?judgement ?chosen ?rationale WHERE {
  {
    ?v1 dec:regarding ?region .
    ?v2 dec:supersedes ?v1 ;
        dec:regarding ?effective .
  }
  UNION
  {
    FILTER NOT EXISTS { ?s dec:supersedes ?v . ?v dec:regarding ?region }
    BIND(?region AS ?effective)
  }
  ?d a dec:DecisionHolon ; dec:regarding ?effective ; dec:order ?order ;
     rdfs:label ?judgement ; dec:rationale ?rationale .
  OPTIONAL { ?d dec:chosen/rdfs:label ?chosen }
}
ORDER BY ?order
```

- [ ] **Step 5: Run — verify green, and that slice A's tests still pass unmodified**

```bash
cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/etkl/test_supersession_queries.py tests/etkl/test_decision_queries.py tests/etkl/test_transposed_chain.py -q
```
Expected: all PASS (with `test_judgement_order_answers_the_r55_question` still SKIPPING on R68 — that skip must remain).

**`tests/etkl/test_decision_queries.py` must pass with zero edits.** If it does not, the `?supersededBy` column broke positional access — fix the query, never the test.

- [ ] **Step 6: Commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && git add vocab/queries/why-escalated.rq vocab/queries/effective-chain.rq tests/etkl/test_supersession_queries.py && git commit -m "feat(loop-ordering-supersession): a superseded chain says so, and the live one is queryable

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Close the register

**Files:**
- Modify: `docs/superpowers/residues.md`
- Modify: `docs/superpowers/specs/2026-08-07-ordering-proof-and-supersession-design.md`

**Note for the controller:** the measurements are yours — run the stem+CBH corpus suite and hand the implementer the numbers. The implementer does the doc edits only.

**Interfaces:** none.

- [ ] **Step 1 (CONTROLLER): confirm nothing moved**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_corpus_stem.py tests/test_cbh_e2e.py -q
```
Expected: 13 passed (stem 0.9655 / 2152 cells / chain [3]; CBH 0.9047). Since no `src/` file changed, any movement means something is wrong with that premise — STOP and report.

- [ ] **Step 2: Replace R68's row with the narrowed residue**

In `docs/superpowers/residues.md`, R68 currently reads *"The R55 ordering link … is unproven end-to-end."* That is no longer true. Replace the row **in place, keeping the number R68** (the residue narrows; it does not disappear, and renumbering would break references). The new row, in the existing house table format:

- **Residue:** *No real corpus document exercises the transposed path* — the R55 ordering is proven only on synthetic fixtures.
- **Measured:** this loop, 2026-08-07 — `tests/etkl/test_transposed_chain.py` asserts `order(transposed) < order(transpose_coherent)` on both branches of the oracle (`false_transposed_pdf` → `incoherent` → `escalated TRANSPOSED`; `transposed_table_pdf` → `coherent` → `asserted`). The corpus scan that motivated the original row still stands: apple (`region4-d2`, `region6-d2` = upright), capacity (`region3-d2` = upright), WHO (`region4-d2` = upright), stem (zero `transposed` judgements at all); CBH never scanned for it.
- **Why deferred:** sourcing a real document that genuinely transposes a table is corpus acquisition, not a code change; the two `pytest.skip("R68: …")` calls keep the gap visible in test output meanwhile.
- **What would close it:** a real document that genuinely transposes entering the corpus, at which point both skips become live assertions.

**Also record, in the same row or beside it, that the original R68 was overstated:** its own *what would close it* clause named a fixture reaching `transpose_is_coherent`, and two such fixtures already existed at `tests/etkl/fixtures.py:268` and `:288` when the row was written. A register that overstates a gap is the same class of defect as one that hides it, and this loop's spec §2 says so.

- [ ] **Step 3: Delete R70's row**

R70 is closed outright — `why-escalated.rq` now binds `?supersededBy` and `effective-chain.rq` ships. Per the register's own rule ("a loop that closes a residue deletes its row in the same change"), remove the row entirely. Do **not** renumber any other row.

- [ ] **Step 4: Close the spec**

In `docs/superpowers/specs/2026-08-07-ordering-proof-and-supersession-design.md`, set `**Status:**` to `closed 2026-08-07` and add a short measured-results section carrying: the corpus numbers the controller hands you, the two fixture chains proving the ordering, and a criterion-by-criterion pass over §5 stating for each whether it was met. If any criterion was not met, say so plainly with its evidence — do not soften it.

Assert nothing you were not handed or cannot read in the repo.

- [ ] **Step 5: Lints + close commit**

```bash
export PATH=/opt/homebrew/bin:$PATH && cd "/Volumes/WD Green/dev/git/iladub" && python -m pytest tests/test_doc_governance.py tests/test_source_ownership.py -q && git add docs/superpowers/residues.md docs/superpowers/specs/2026-08-07-ordering-proof-and-supersession-design.md && git commit -m "docs(loop-ordering-supersession): close — R70 closed, R68 narrowed to the corpus gap

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>"
```
(The `PATH` prefix matters — `test_doc_governance.py` shells out to `git`, and without it you get spurious `subprocess.CalledProcessError` setup errors that are a machine problem, not your edit.)

- [ ] **Step 6: Finish the branch** — superpowers:finishing-a-development-branch (house convention: PR to `main`).

---

## Self-Review (run after writing — done 2026-08-07)

- **Spec coverage:** §2 (R68 provable all along) → Task 1; §3 (R70's two harms) → Task 2 Steps 3–4; §4.1 → Task 1 Step 1, including the instruction to keep the corpus skips; §4.2 → Task 2's two queries, with `?supersededBy` last and region-level as the spec requires; §4.3 → Task 2's repaired/unrepaired tests, control included; §5 criteria → Task 3 Step 4's criterion pass, plus Task 2 Step 5's "slice A's tests unmodified" check and Task 3 Step 1's corpus run; §6 (narrowed residue) → Task 3 Step 2; §7 out-of-scope items are named in no task, correctly.
- **Placeholder scan:** none. Every query and test is given in full; the one judgement call left open (exact prose of the residue row) is bounded by four bullet points of required content.
- **Type consistency:** `_run` returns `tuple` in Task 1 (positional, matching slice A's harness) and `dict` via `asdict()` in Task 2 (because `?supersededBy` must be tested for *absence*, which positional access cannot express) — deliberate, and the two files never share a helper. `?region` is the bound variable name in all four queries. `page_doc_uri(0)` is used rather than a hardcoded IRI in Task 2; `_DOC` directly in Task 1, since single-page `compile_tables` does not page-scope.
- **One risk I checked rather than assumed:** appending `?supersededBy` to `why-escalated.rq` cannot break slice A's tests, because `SELECT ?order ?judgement ?chosen ?rationale` keeps indices 0–3 and `tests/etkl/test_decision_queries.py` reads `r[0]` and `r[3]` only. Task 2 Step 5 verifies this rather than trusting it.
