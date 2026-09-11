# Grid donation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** a record-table band whose ink tiles the wholly-drawn column grid of an earlier band on the
same page, at the same leaf-column count, and whose donor's line 0 the page datagrid refuses as a
header, reads its labels from that donor — and a refused or absent donation leaves the band compiling
exactly as it does today.

**Architecture:** one page-scoped evidence graph (the `run_evidence` idiom, R165) carries every band
that owns a `_rule_boundaries` vector; a SPARQL `SELECT` enumerates (donor, continuation) candidates
on four positive facts — earlier on the page, wholly drawn, same leaf-column count, head line refused
`HeterogeneousColumn/every-measure` by the page datagrid; the shipped membrane disposes each candidate
on a scratch graph (`region_tiles` + `cell_round_trips`, the R165 chain). The derivation enumerates;
the oracle disposes; a refusal is invisible.

**Tech Stack:** Python 3, rdflib, pySHACL, pytest, reportlab (synthetic fixtures). RDF Turtle for
the vocabulary, SPARQL `SELECT` for the derivation.

**Spec:** `docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md` (§ 3 the relation,
§ 4 the ruling, § 5 what it does not do). The four plan decisions the spec left open were settled by
two measurement loops before this plan — read them in this order when a task cites them:

| doc | what it settles |
| --- | --- |
| `docs/superpowers/2026-09-10-the-grid-the-author-drew-handoff.md` § 5a | decisions 1–3: where the AXIOM lives, what the donated reading is, what disposes it |
| `docs/superpowers/2026-09-10-the-donated-reading-tiles-handoff.md` § 2 | the oracle numbers: 222 → 267 entries, 45 → 0 false labels, every donated reading tiles with no ink lost; the membrane is blind to header content (§ 5b) |
| `docs/superpowers/2026-09-11-the-donor-header-is-derived.md` § 1–4 | decision 4 ([[R203]]): the donor's header is DERIVED — donate iff the page datagrid refuses the donor's line 0 `every-measure`; the converse is refuted (§ 2); line identity is by ink, never by index (§ 4) |

**Doc impact: increment.** `tests/corpus-manifest.ttl`'s bfs entry gains one `cor:reading` node
(append-only); `docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM derivation. Five new
`tab:` terms are declared in `vocab/ontology/tab.ttl`. No released assertion changes; **no
contradiction**, so nothing blocks a release tag.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **The neurosymbolic gate (CLAUDE.md §8), as ruled in spec § 4.** The candidate enumeration is
   **AXIOM / derivation / open world** — it fires on present facts and infers nothing from absence;
   its one closed-world clause (`drawn`) is holon-scoped, closing within one band node. The disposal
   is the **existing closed-world membrane**, reused verbatim. **A tuned constant or tolerance
   anywhere in the shipped diff is a review failure, and so is a numeric literal in the `.rq`.**
   `COORD_EPS` stays where it is shipped (`roundtrip.py:31`, `grid.py:81`) and **never enters a
   query** — see DECISION A for why that is possible.
2. **The 2dp rounding is inherited, not tuned** (spec § 7): `sectiongraph._distinct_rule_xs`
   (`sectiongraph.py:180-187`, *"THE single rounding site"*) and `_rule_boundaries`'
   `round(r.x, 2)` (`grid.py:74`). The emitter rounds the donor vector at the same 2dp so that
   `tab:donorBoundaryX` and `tab:bandRuleX` compare **by term**. Do not add a third site.
3. **Source ownership (CLAUDE.md § Source ownership).** Every new term is in `tab:` =
   `https://w3id.org/iladub/tab#`. No HGA IRI appears as a subject anywhere.
4. **Plan rules 1–7 (CLAUDE.md § Plan authoring discipline).** No function body appears in this
   plan. Tests are supplied verbatim and are **propositions**: a test that cannot be made to pass
   has found a plan or spec defect — say so in the task report and substitute the satisfiable form
   carrying the same force; never weaken the assertion. **Every task ships a `## FALSIFICATION`
   block** (rule 4). No falsification evidence ⇒ the task review fails.
5. **Line identity is by ink, never by index ([[R202]]).** A band's line 0 is matched to a page line
   by its whitespace-stripped concatenated word text, exactly as `scripts/donor_header_criterion.py`'s
   `key` does (band words are word GROUPS — `1 736 124` is one word — so raw word-tuple equality found
   0 of 12 there). A match that is not unique emits **no** fact.
6. **A refusal is invisible (R165 spec § 3.2, pinned by
   `test_a_refused_run_leaves_the_page_byte_identical`).** No triple, no decision-log node, no report.
   The page whose donation is refused is isomorphic to the page whose donation was never proposed.
   Only an **accepted** donation records a decision.
7. **`corpus/` is gitignored.** A fresh `git worktree` has no corpus and every corpus-gated test
   skips green. Symlink it first — `ln -s "/Volumes/WD Green/dev/git/iladub/corpus" corpus` — and
   verify `ls corpus/gov-stats` lists the bfs PDF. A green run with no corpus falsifies nothing.
8. **The full suite takes ~45–60 minutes and must NOT be run in a background subagent** (measured
   trap, `docs/superpowers/2026-09-02-the-body-starts-at-the-stub-handoff.md`). Run it in-band, once,
   at Task 6. `macOS` has no `timeout` command and `pytest --timeout` is not installed: wrapping a run
   in either runs nothing and reports exit 0 — read the output, never the exit code.
9. **Branch protection.** Branch first; every commit reaches `main` through a PR whose `test` check
   is green. **This plan's branch is cut from `main` AFTER PR #198 merges** — the evidence doc it
   cites lives there.

---

## Measurement this plan rests on (2026-09-11, `main` at `808aa7a` + PR #198)

Run once, from the repo root, with the corpus present. The script is committed beside this plan as
`scripts/grid_donation_design_census.py` so the figures stay reproducible; its docstring records the
commit it was measured at.

```
$ PYTHONPATH=. .venv/bin/python scripts/grid_donation_design_census.py
bfs p6 band4 <- donor band2: ncols=9 straddlers=0 donor.grid==xs:True entries=36 tiles=True rt=True donor line0 datagrid=HeterogeneousColumn/every-measure -> ACCEPT
bfs p6 band5 <- donor band2: ncols=9 straddlers=0 donor.grid==xs:True entries=54 tiles=True rt=True donor line0 datagrid=HeterogeneousColumn/every-measure -> ACCEPT
bfs p6 band6 <- donor band2: ncols=9 straddlers=0 donor.grid==xs:True entries=36 tiles=True rt=True donor line0 datagrid=HeterogeneousColumn/every-measure -> ACCEPT
bfs p6 band8 <- donor band2: ncols=9 straddlers=0 donor.grid==xs:True entries=72 tiles=True rt=True donor line0 datagrid=HeterogeneousColumn/every-measure -> ACCEPT
bfs p6 band9 <- donor band2: ncols=9 straddlers=0 donor.grid==xs:True entries=63 tiles=True rt=True donor line0 datagrid=HeterogeneousColumn/every-measure -> ACCEPT

page_bands total 39.0s; derive_data_grid total 4.9s over 27 pages
donor-vector bands: 7; line0 identity unique=7 multi=0 none=0
structural pairs (no tiling clause): 5; accepted by disposal: 5
```

Three facts, each load-bearing for one decision below:

- **M1.** `derive_data_grid` costs **4.9 s over all 27 corpus pages** against 39.0 s of `page_bands`.
  The predecessor handoff's § 5b feared this cost unmeasured; it is ~12% of band-building and needs
  no laziness beyond "only on a page that carries a donor-vector band" (7 bands, corpus-wide).
- **M2.** Every band that owns a `_rule_boundaries` vector (7 of them, corpus-wide) has a line 0 that
  re-identifies **uniquely** among the page's text lines by ink key. The identity the plan's emitter
  needs holds on its whole population, not only on the 12 censused readings.
- **M3.** With the **tiling clause removed from the relation** — candidates enumerated on `earlier ∧
  wholly drawn ∧ same ncols` only — the corpus yields **exactly 5 structural pairs, the census's 5**,
  and the disposal (`region_tiles` ∧ every data cell `cell_round_trips`) accepts all 5. Moving tiling
  into the disposal changes nothing on the corpus and is what keeps the query literal-free.

And the bfs baseline at `808aa7a`, measured in-session (`compile_document` 29.0 s):

```
bfs document score 0.40331491712707185          (== the manifest's latest cor:reading)
bfs p6: score 0.9169435215946844  asserted 276  escalated 25  entries 222
per band (idx, verdict, cells, tokens_asserted, tokens_escalated):
  (2,'asserted',6,15,0) (4,'asserted',27,36,0) (5,'asserted',45,54,0) (6,'asserted',27,36,0)
  (8,'asserted',63,72,0) (9,'asserted',54,63,0)  — 1 and 10 escalate 16 and 9; 0,3,7,11 ignored
```

---

## The five decisions this plan takes, that the spec and handoffs left open

Stated once here; **cited** from the tasks (plan rule 6).

### DECISION A — the tiling clause is DISPOSED, not derived

Spec § 3 lists three clauses (tiles, same_ncols, drawn) and § 4 adds the R203 licence. This plan
puts **tiles** in the disposal and the other three in the query. Why: the cross-band tiling test the
census ran (`scripts/grid_agreement_census.py:straddlers`) *is* `_rule_boundaries`' own word-in-interval
test, and its shipped per-cell form is `roundtrip.cell_round_trips` (`roundtrip.py:29-31`), which the
record-table branch already applies to every data cell. Deriving it in SPARQL would either put
`COORD_EPS` in a query (a numeric literal — Global Constraint 1) or serialise every word box of every
band into the evidence graph to evaluate a predicate with zero degrees of freedom. **M3 measures that
the accepted set is identical** (5 = 5). The synthetic straddling page (Task 3) pins that the refusal
now happens at the disposal.

### DECISION B — one page graph, one query, per-band bindings; the seam is the assert leg

The evidence graph is built **once per page** before `compile_tables`' band loop and carries only
donor-side facts. The continuation band's leaf-column count is a fact the loop already derives once
per band (`compile.py:800` `region = classify(band)` → `region.grid.ncols`); emitting it for every
band up front would run `infer_leaf_grid` twice per band, the duplication [[R168]] already records.
So the reader passes `?b` and `?n` as `initBindings` (precedent: `adoption.py:105`,
`rowgroups.py:86`, `celltype.py:168`). The proposal is offered at the record-table branch's **assert
leg** — the `else:` at `compile.py:967` (`# ---- existing RECORD_TABLE assert logic ----`) — after
`looks_transposed` (`:820`) and `looks_row_grouped` have run on the band's OWN reading. A band that
would escalate under its own reading is not offered a donation (spec § 3's population is *bands the
record-table branch reads*; every one of the 5 asserts today).

### DECISION C — the R203 licence is a fact on the donor node, carried verbatim from the datagrid

`tab:headLineRefusal` is a datatype property on the donor node whose value is the datagrid's refusal
string **verbatim** — the same lexical form `emit_data_grid` writes into `dec:rejectedBecause`
(`datagrid.py:610`: `?rejected dec:rejectedBecause "HeterogeneousColumn/every-measure"`). The query
matches the literal `"HeterogeneousColumn/every-measure"`. It is emitted **only** when the band's
line 0 re-identifies uniquely (Global Constraint 5) among the page's lines **and** that line is in
`grid.refusals` — a body-row verdict, any other refusal, no datagrid, or no unique match emits no fact
(evidence doc § 2's ruling: the reading escalates rather than carrying a header nobody derived). This
is the first shipped `.rq` to match a string literal; it is justified because the literal is the
datagrid's own published refusal name, not a constant of this loop's.

### DECISION D — the donated reading is built from the donor's OWN classified grid, rows shifted by one

`donated_region(bands, donor_idx, idx)` returns a `ClassifiedRegion(RECORD_TABLE, band=bands[idx],
grid=infer_leaf_grid(bands[donor_idx]), cells=head + body, reason="donated")` where `head` is the
donor's row-0 cells under that grid and `body` is `assign_cells(bands[idx], grid)` with every row
index incremented by one (`Cell` is frozen — `dataclasses.replace`). **Not** the spike's construction:
`scripts/grid_donation_spike.py` prepends the donor's `Line` to the continuation band, which would put
the donor's 9 words inside five bands' ink and book them five times under R176's ledger
(`compile.py:276`, `_book_recovered_ink` reads *this band's* words). With the donor's label cells
carrying the donor's bboxes — which lie outside the continuation band — the ledger books 0 recovered
words there, and the band's own line 0 becomes data cells that all round-trip. **Prediction (task 4
measures it): every donated band's `tokens_asserted` is unchanged (36/54/36/72/63), the page score
stays 0.9169, and the document score stays 0.4033. The score is NOT this loop's oracle; the entry
count and the label texts are.** `infer_leaf_grid` returns `_rule_boundaries`' vector at confidence
1.0 whenever that vector exists (`grid.py`, `infer_leaf_grid`, the `rb is not None` return), so the
grid the reading uses is the vector the query licensed — measured `donor.grid==xs:True` on all 5.

### DECISION E — the donor must be UNIQUE, and no ordering rule is added

`donors_for` returns every qualifying donor; `offer` proposes a reading **only when exactly one**
qualifies. Two qualifying donors is a page this relation cannot read, and the band compiles as today.
Spec § 3(b) measured uniqueness on the corpus (`multi = 0`) and refused an ordinal rule; this plan
keeps that refusal as the shipped behaviour and pins it on a synthetic page with two drawn donors.

---

## File Structure

| file | responsibility |
| --- | --- |
| `vocab/ontology/tab.ttl` (modify, after `:350` `tab:prevBandIndex`) | five terms: `tab:DonorBand`, `tab:donorBoundaryX`, `tab:leafColumnCount`, `tab:headLineRefusal`, `tab:headerDonatedBy` |
| `src/iladub/etkl/sectiongraph.py` (modify, after `run_evidence` `:223-256`) | `donor_evidence(bands, head_refusals) -> Graph` — the emitter, beside its siblings |
| `vocab/queries/grid-donation.rq` (create) | the derivation |
| `src/iladub/etkl/donation.py` (create) | `head_line_refusals`, `donors_for`, `donated_region`, `donation_admissible`, `offer`, `Donation` — the reader, the reading, the disposal |
| `src/iladub/etkl/compile.py` (modify, `:731-800` prologue and the `:967` leg) | the seam: build the page graph once; offer at the assert leg; record acceptance; emit `tab:headerDonatedBy` |
| `scripts/grid_donation_design_census.py` (committed with this plan) | the measurement above, reproducible |
| `tests/etkl/test_donor_evidence.py`, `test_grid_donation_query.py`, `test_grid_donation_disposal.py`, `test_grid_donation_seam.py` (create) | one module per layer, synthetic pins in CI, corpus pins gated |
| `tests/corpus-manifest.ttl`, `docs/superpowers/residues*.md`, `docs/wiki/concepts/neurosymbolic-exemplars.md`, `docs/superpowers/2026-09-11-grid-donation-evidence.md` | Task 5–6 records |

`tests/etkl/test_grid_donation_relation.py` and the two instruments it imports from `scripts/` are
**not modified**: they pin the census's relation as measured and stay the evidence for spec § 3.

---

## Task 1: The vocabulary and the donor-evidence emitter

**Files:**
- Modify: `vocab/ontology/tab.ttl` (append after `:350`, inside the *intra-page band evidence graphs*
  block that starts at `:334`)
- Modify: `src/iladub/etkl/sectiongraph.py` (new function after `run_evidence`, `:256`)
- Test: `tests/etkl/test_donor_evidence.py`

**Interfaces:**
- Consumes: `grid._rule_boundaries(band) -> list[float] | None` (`grid.py:40`),
  `sectiongraph._distinct_rule_xs(rules)` (`:180`), the `_EV` namespace and `TAB` already in
  `sectiongraph.py`.
- Produces: `sectiongraph.donor_evidence(bands: Sequence[Band], head_refusals: Mapping[int, str])
  -> Graph`. One `tab:DonorBand` node per band for which `_rule_boundaries` returns a vector of ≥ 3
  boundaries (`_EV["donor-%d" % idx]`), carrying `tab:bandIndex` (integer, position in the passed
  list — `page_bands`' single index space), one `tab:donorBoundaryX` per boundary as
  `Literal(Decimal(str(round(x, 2))))`, one `tab:bandRuleX` per distinct rounded rule x (via
  `_distinct_rule_xs`, same lexical form as `run_evidence`), `tab:leafColumnCount` = `len(vector) - 1`,
  and `tab:headLineRefusal` **iff** `idx in head_refusals`, with that string. A band with no vector
  emits **nothing** — the honest abstain `run_evidence`'s docstring argues (`:234-238`).

**Vocabulary, stated once.** `tab:DonorBand rdfs:subClassOf tab:RuledBand` — every donor band carries
rules by construction (`_rule_boundaries` returns `None` without them, `grid.py:69-70`), so
`tab:bandRuleX`'s domain is satisfied; the population comment on `tab:PageBand` (`tab.ttl:336`) must
be extended to name this third population and say it is emitted into its **own** graph, never merged
with `run_evidence`'s. `tab:donorBoundaryX` (`xsd:decimal`, domain `tab:DonorBand`),
`tab:leafColumnCount` (`xsd:integer`), `tab:headLineRefusal` (`xsd:string`; comment cites DECISION C
and `datagrid.py:599-625`), `tab:headerDonatedBy` (`owl:ObjectProperty`, domain and range
`tab:RecordTable`; emitted by Task 4 into the compiled graph, **never** into a scratch graph —
`region_tiles` validates the scratch and an undeclared property on the table node is the implementer's
to measure against the tiling shapes before deciding where it goes).

**MEASURE before writing** (plan rule 3): whether `tests/test_query_declarations.py`'s membrane
requires a declared `rdfs:domain`/`rdfs:range` on every term a query names, or only a declaration —
read `vocab/shapes/query-declaration-shapes.ttl` and say which in the task report.

- [ ] **Step 1: Reproduce the measurement**

Run `PYTHONPATH=. .venv/bin/python scripts/grid_donation_design_census.py` once and confirm its last
three lines match § Measurement above. If they do not, the tree has moved since the plan was written:
stop and say what moved before writing anything.

- [ ] **Step 2: Write the failing tests**

```python
# tests/etkl/test_donor_evidence.py
"""Grid donation — the evidence half (R201 → R203).

Spec: docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md § 3–4
Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 1
"""
from decimal import Decimal

from rdflib import Literal, Namespace

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Rule, Word

TAB = Namespace("https://w3id.org/iladub/tab#")
EVERY_MEASURE = "HeterogeneousColumn/every-measure"


def _band(xs, words, y=0.0, column_xs=()):
    """A one-line band ruled at `xs`, its words given as (text, x0, x1). `column_xs`
    is the DERIVED vector `_rule_boundaries` prefers when present (grid.py:73)."""
    ws = tuple(Word(text=t, x0=a, x1=b, top=y, bottom=y + 10.0) for t, a, b in words)
    return Band(lines=(Line(words=ws, top=y, bottom=y + 10.0),), top=y, bottom=y + 10.0,
                rules=tuple(Rule(x=x, top=y, bottom=y + 10.0) for x in xs),
                column_xs=column_xs)


HEAD = (("Region", 80.0, 120.0), ("Total", 210.0, 240.0), ("Share", 340.0, 370.0))
RULED = _band((72.0, 200.0, 330.0, 460.0), HEAD)


def _nodes(g):
    return {int(g.value(u, TAB.bandIndex)): u for u in g.subjects(None, TAB.DonorBand)}


def test_a_band_with_no_vector_emits_no_node_at_all():
    """The honest abstain, for this population: no rules, or a word that straddles
    the band's own rule, means _rule_boundaries returns None and the band is absent —
    never a node with zero boundaries, which the query could not defend against."""
    from iladub.etkl.sectiongraph import donor_evidence

    unruled = _band((), HEAD)
    straddling = _band((72.0, 200.0, 330.0, 460.0),
                       (("Region", 80.0, 120.0), ("Total", 190.0, 240.0), ("Share", 340.0, 370.0)))
    g = donor_evidence([unruled, RULED, straddling], {})
    assert set(_nodes(g)) == {1}


def test_the_vector_and_the_rule_xs_are_decimals_at_the_inherited_2dp():
    """DECISION A/Global Constraint 2: the drawn clause is a TERM match between
    tab:donorBoundaryX and tab:bandRuleX, so both must be minted by the same rounding."""
    from iladub.etkl.sectiongraph import donor_evidence

    g = donor_evidence([_band((72.004, 200.0, 330.0, 460.0), HEAD)], {})
    u = _nodes(g)[0]
    bounds = set(g.objects(u, TAB.donorBoundaryX))
    rules = set(g.objects(u, TAB.bandRuleX))
    assert bounds == {Literal(Decimal(s)) for s in ("72.0", "200.0", "330.0", "460.0")}
    assert bounds == rules
    assert int(g.value(u, TAB.leafColumnCount)) == 3


def test_a_derived_gutter_is_a_boundary_but_not_a_rule_x():
    """bfs p6 bands 4-9's shape: column_xs carries an interior gutter this compiler
    inferred (291.5) where the author drew nothing. It is emitted as a boundary — the
    band DOES own a vector — and the query's drawn clause is what refuses it (Task 2)."""
    from iladub.etkl.sectiongraph import donor_evidence

    faked = _band((72.0, 200.0, 460.0), HEAD, column_xs=(72.0, 200.0, 291.5, 460.0))
    g = donor_evidence([faked], {})
    u = _nodes(g)[0]
    assert Literal(Decimal("291.5")) in set(g.objects(u, TAB.donorBoundaryX))
    assert Literal(Decimal("291.5")) not in set(g.objects(u, TAB.bandRuleX))


def test_the_head_refusal_is_a_fact_only_where_the_caller_mapped_one():
    """DECISION C: the R203 licence is carried verbatim from the datagrid's refusal
    record, and only for the band the caller identified BY INK. Nothing here infers."""
    from iladub.etkl.sectiongraph import donor_evidence

    g = donor_evidence([RULED, _band((72.0, 200.0, 330.0, 460.0), HEAD, y=50.0)],
                       {1: EVERY_MEASURE})
    n = _nodes(g)
    assert g.value(n[0], TAB.headLineRefusal) is None
    assert str(g.value(n[1], TAB.headLineRefusal)) == EVERY_MEASURE


def test_band_index_is_the_position_in_the_passed_list():
    """The single index space page_bands enumerates (compile.py:320 docstring)."""
    from iladub.etkl.sectiongraph import donor_evidence

    g = donor_evidence([_band((), HEAD), RULED, _band((), HEAD)], {})
    assert set(_nodes(g)) == {1}
```

- [ ] **Step 3: Run them to verify they fail**

Run: `.venv/bin/pytest tests/etkl/test_donor_evidence.py -q`
Expected: 5 failed, `ImportError: cannot import name 'donor_evidence'`.

- [ ] **Step 4: Declare the five terms, write the emitter**

Signature and invariants as in *Interfaces*. Mirror `run_evidence`'s docstring discipline: say why the
abstain is the emitter's job and not the query's, and that the graph is never merged with
`run_evidence`'s.

- [ ] **Step 5: Run the tests and the declaration membrane**

Run: `.venv/bin/pytest tests/etkl/test_donor_evidence.py tests/test_query_declarations.py tests/test_query_terms.py tests/test_source_ownership.py -q`
Expected: all pass (the declaration membrane has no new `.rq` to read yet; Task 2 gives it one).

- [ ] **Step 6: FALSIFICATION**

(a) Delete the `continue` (or equivalent) that makes the emitter abstain for a band without a vector,
emitting a node with no boundaries. Show `test_a_band_with_no_vector_emits_no_node_at_all`
**failing**. Restore. (b) Round the boundary at 3dp instead of 2. Show
`test_the_vector_and_the_rule_xs_are_decimals_at_the_inherited_2dp` **failing**. Restore. Show all
green. Paste all three outputs in the task report.

- [ ] **Step 7: Commit**

```bash
git add vocab/ontology/tab.ttl src/iladub/etkl/sectiongraph.py tests/etkl/test_donor_evidence.py
git commit -m "feat(grid donation): tab:DonorBand and the donor-evidence emitter, with the honest abstain pinned"
```

---

## Task 2: The derivation query and its reader

**Files:**
- Create: `vocab/queries/grid-donation.rq`
- Create: `src/iladub/etkl/donation.py` (this task adds `donors_for` only)
- Test: `tests/etkl/test_grid_donation_query.py`

**Interfaces:**
- Consumes: Task 1's graph.
- Produces: `donation.donors_for(evidence: Graph, idx: int, ncols: int) -> tuple[int, ...]` — the
  ascending band indices of every `tab:DonorBand` node `?u` such that: `?u tab:bandIndex ?a` with
  `?a < ?b` (`?b` bound to `idx`); `?u tab:leafColumnCount ?n` (`?n` bound to `ncols`);
  `?u tab:headLineRefusal "HeterogeneousColumn/every-measure"`; and **no** `tab:donorBoundaryX` of
  `?u` lacks an equal `tab:bandRuleX` on `?u` (the drawn clause — one `FILTER NOT EXISTS { … FILTER
  NOT EXISTS { … } }`, holon-scoped to `?u`, the same idiom as `band-run.rq:32-33`). The query is
  `SELECT ?a` and carries **no numeric literal**; `?b` and `?n` arrive as `initBindings`.

**The `.rq` header comment must argue, once, three things** (the `band-run.rq` header is the model):
why the tiling clause is absent (DECISION A), why the string literal is admissible (DECISION C), and
that this derivation *enumerates and settles nothing* — `donation.offer` disposes.

**MEASURE before writing** (plan rule 3): that rdflib's `initBindings` binds a variable that appears
only inside `FILTER(?a < ?b)` — some SPARQL engines drop unbound-in-pattern bindings. If it does not,
bind `?b`/`?n` through a `VALUES` clause built by the reader, and say so.

- [ ] **Step 1: Write the failing tests**

```python
# tests/etkl/test_grid_donation_query.py
"""Grid donation — the derivation half. The query ENUMERATES; donation.offer disposes.

Spec § 3 (the clauses), § 4 (the R203 licence as decision 4).
Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 2
"""
from iladub.etkl.sectiongraph import donor_evidence

from tests.etkl.test_donor_evidence import HEAD, EVERY_MEASURE, _band

RULED = _band((72.0, 200.0, 330.0, 460.0), HEAD)
COARSE = _band((72.0, 265.0, 460.0), (("Subtotal", 80.0, 130.0), ("29.5", 340.0, 370.0)), y=30.0)


def _donors(bands, refusals, idx, ncols):
    from iladub.etkl.donation import donors_for

    return donors_for(donor_evidence(bands, refusals), idx, ncols)


def test_the_relation_fires_on_a_drawn_refused_head_at_the_same_column_count():
    assert _donors([RULED], {0: EVERY_MEASURE}, idx=2, ncols=3) == (0,)


def test_a_later_band_is_never_a_donor():
    """Earlier on the page, by the emitted index — the only ordering the relation uses."""
    assert _donors([RULED], {0: EVERY_MEASURE}, idx=0, ncols=3) == ()


def test_the_wrong_column_count_is_refused_graincorp_p0s_shape():
    """Spec § 3(c): drawn, tiling, and 2 columns against 3. The null control, in CI."""
    assert _donors([RULED, COARSE], {0: EVERY_MEASURE, 1: EVERY_MEASURE}, idx=3, ncols=2) == (1,)
    assert _donors([RULED, COARSE], {0: EVERY_MEASURE, 1: EVERY_MEASURE}, idx=3, ncols=3) == (0,)


def test_an_inferred_interior_boundary_refuses_the_donor():
    """Spec § 3(b), bfs p6 bands 4-9: the vector carries a gutter the compiler inferred.
    Every other clause passes; the drawn clause alone refuses. This is what makes the
    donor unique on bfs p6 rather than merely first."""
    faked = _band((72.0, 200.0, 460.0), HEAD, column_xs=(72.0, 200.0, 291.5, 460.0))
    assert _donors([faked], {0: EVERY_MEASURE}, idx=1, ncols=3) == ()


def test_a_head_the_datagrid_did_not_refuse_is_not_a_donor():
    """Decision 4 / R203: the donor's header is DERIVED. A body-row verdict, any other
    refusal, or no fact at all refuses the donation — the reading must not carry a
    header nobody derived (evidence doc § 2)."""
    assert _donors([RULED], {}, idx=2, ncols=3) == ()
    assert _donors([RULED], {0: "HeterogeneousColumn/col1"}, idx=2, ncols=3) == ()
    assert _donors([RULED], {0: "RowAddressability/no-key"}, idx=2, ncols=3) == ()


def test_two_qualifying_donors_are_both_returned_the_reader_orders_nothing():
    """DECISION E lives in donation.offer, not here: the derivation reports every
    donor and adds no ordinal rule (spec § 3(b) refused one)."""
    twice = _band((72.0, 200.0, 330.0, 460.0), HEAD, y=30.0)
    assert _donors([RULED, twice], {0: EVERY_MEASURE, 1: EVERY_MEASURE}, idx=2, ncols=3) == (0, 1)
```

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/pytest tests/etkl/test_grid_donation_query.py -q`
Expected: 6 failed, `ModuleNotFoundError: No module named 'iladub.etkl.donation'`.

- [ ] **Step 3: Write the query and the reader**

`donation.py`'s module docstring states the §8 classification of each function it will hold (this
task: `donors_for` is the AXIOM's reader, PROCEDURAL glue like `sectiongraph.section_candidates`).
Load the `.rq` the way `sectiongraph.py` loads `SECTION_REPEAT_RQ`.

- [ ] **Step 4: Run the tests and the two query gates**

Run: `.venv/bin/pytest tests/etkl/test_grid_donation_query.py tests/test_query_declarations.py tests/test_query_terms.py -q`
Expected: all pass — the population gates pick up `grid-donation.rq` automatically
(`test_the_population_is_every_file_in_vocab_queries`), and every term it names is declared by Task 1.

- [ ] **Step 5: FALSIFICATION**

(a) Delete the drawn clause's `FILTER NOT EXISTS` from the `.rq`. Show
`test_an_inferred_interior_boundary_refuses_the_donor` **failing** with `(0,)`. Restore. (b) Delete
the `tab:headLineRefusal` triple pattern. Show `test_a_head_the_datagrid_did_not_refuse_is_not_a_donor`
**failing**. Restore. (c) Delete `tab:headLineRefusal`'s declaration from `tab.ttl`. Show
`tests/test_query_declarations.py` **failing** on `grid-donation.rq`. Restore. Show green. Paste all
four outputs.

- [ ] **Step 6: Commit**

```bash
git add vocab/queries/grid-donation.rq src/iladub/etkl/donation.py tests/etkl/test_grid_donation_query.py
git commit -m "feat(grid donation): grid-donation.rq enumerates donors on four positive facts; the reader binds the continuation"
```

---

## Task 3: The head-line refusals, the donated reading, and the disposal

**Files:**
- Modify: `src/iladub/etkl/donation.py`
- Test: `tests/etkl/test_grid_donation_disposal.py`

**Interfaces:**
- Consumes: `datagrid.derive_data_grid(pdf_path, page_number) -> DataGrid | None` (`datagrid.py:319`;
  `.rows` the admitted line indices, `.refusals: dict[int, str]`), `geometry.extract_words` /
  `text_lines` (`geometry.py:41`, `:508`), `grid.infer_leaf_grid` (`grid.py:92`),
  `regions.assign_cells` (`regions.py:65`), `regions.Cell` / `ClassifiedRegion` (`:33-56`),
  `holon.assert_record_region` (`holon.py:106`), `tiling.region_tiles` (`tiling.py:74`),
  `roundtrip.cell_round_trips` (`roundtrip.py:29`), Task 2's `donors_for`.
- Produces:
  - `donation.head_line_refusals(pdf_path: str, page_number: int, bands: Sequence[Band]) ->
    dict[int, str]` — for each band that owns a `_rule_boundaries` vector, the datagrid's refusal
    string for the page line its line 0 re-identifies to **by ink key** (Global Constraint 5), if
    that line is refused. Returns `{}` **without calling `derive_data_grid`** when no band owns a
    vector (M1's laziness); otherwise calls it exactly once. The page-line list is *exactly*
    `derive_data_grid`'s — `[l for l in sorted(text_lines(extract_words(pdf, page)), key=top) if
    l.words]`, as `scripts/donor_header_criterion.py:page_lines` documents — or the indices disagree.
  - `donation.donated_region(bands: Sequence[Band], donor_idx: int, idx: int) -> ClassifiedRegion` —
    DECISION D. Invariants: `.band is bands[idx]`; `.grid == infer_leaf_grid(bands[donor_idx])`;
    row-0 cells are exactly the donor's row-0 cells under that grid; rows 1..k are
    `assign_cells(bands[idx], grid)` with `row + 1`; `.reason == "donated"`.
  - `donation.donation_admissible(region: ClassifiedRegion, page_number: int) -> bool` — the
    disposal, a single named module-level function so a test can patch it (the
    `merged_run_admissible` precedent, `compile.py:456-487`). Offers `region` to
    `assert_record_region` on a **scratch** `Graph` under a placeholder doc URI, and returns
    `region_tiles(scratch)` **and** every row > 0 cell `cell_round_trips` against `region.grid.boundaries`.
    The placeholder is legitimate for the same measured reason as `_RUN_PROPOSAL_DOC`
    (`compile.py:453-457`) — **re-measure it here**: run the 5 bfs p6 donations through the disposal
    under two unrelated doc URIs and show 0 verdicts differ.
  - `donation.Donation` (frozen dataclass: `region: ClassifiedRegion`, `donor_index: int`) and
    `donation.offer(bands, idx, region, evidence: Graph, page_number: int) -> Donation | None` —
    proposes iff `region.kind is RECORD_TABLE`, `donors_for(evidence, idx, region.grid.ncols)` has
    **exactly one** element (DECISION E), and `donation_admissible(donated_region(...))`. Returns
    `None` otherwise; must not touch any graph that survives.

**MEASURE before writing** (plan rule 3): `derive_data_grid` on the **synthetic** donated page below
— does it return a grid, and does it refuse the head line `HeterogeneousColumn/every-measure`? The
answer decides whether Task 4's end-to-end CI pin runs through the real map or a patched one. Record
the answer in the task report either way.

- [ ] **Step 1: Write the failing tests**

```python
# tests/etkl/test_grid_donation_disposal.py
"""Grid donation — the reading and the disposal. The derivation proposed; this refuses or accepts.

Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 3 (DECISIONS A, D, E)
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from reportlab.lib.pagesizes import letter  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

from iladub.etkl.compile import page_bands  # noqa: E402
from iladub.etkl.regions import RegionKind, classify  # noqa: E402
from iladub.etkl.sectiongraph import donor_evidence  # noqa: E402

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not fetched")

EVERY_MEASURE = "HeterogeneousColumn/every-measure"
PAGE_H = letter[1]
RULES = (72.0, 200.0, 330.0, 460.0)
HEAD = (("Region", 80.0), ("Total", 210.0), ("Share", 340.0))
ROWS = (("Vaud", "845870", "18.4"), ("Valais", "365844", "70.5"),
        ("Geneve", "524410", "11.0"), ("Berne", "1063533", "20.3"))


def _page(path, data_cols, head_twice=False):
    """test_grid_donation_relation's page: a ruled 3-column head band, a gap, four unruled
    data rows on `data_cols`. `head_twice` draws the head band a second time — two wholly
    drawn donors at the same column count, the page DECISION E refuses."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    y = PAGE_H - 90.0
    for _ in range(2 if head_twice else 1):
        for x in RULES:
            c.line(x, y - 4.0, x, y + 14.0)
        for (t, x) in HEAD:
            c.drawString(x, y, t)
        y -= 150.0
    for i, row in enumerate(ROWS):
        for x, cell in zip(data_cols, row):
            c.drawString(x, y - i * 14.0, cell)
    c.save()
    return page_bands(str(path), 0)


def _record_band(bands):
    idx = [i for i, b in enumerate(bands) if classify(b).kind is RegionKind.RECORD_TABLE]
    assert idx, "fixture drew no record-table band"
    return idx[-1]


def _head_bands(bands):
    """Every band the head was drawn into — the donors a refusal map must name."""
    return [i for i, b in enumerate(bands)
            if [w.text for w in b.lines[0].words] == ["Region", "Total", "Share"]]


def test_the_donated_region_takes_the_donors_grid_and_labels_and_shifts_the_rows(tmp_path):
    """DECISION D, on the page: the continuation keeps its band, takes the donor's grid,
    reads the donor's line 0 as its row 0, and its own line 0 becomes row 1."""
    from iladub.etkl.donation import donated_region
    from iladub.etkl.grid import infer_leaf_grid

    bands = _page(tmp_path / "donated.pdf", (80.0, 210.0, 340.0))
    i, d = _record_band(bands), _head_bands(bands)[0]
    reg = donated_region(bands, d, i)
    assert reg.band is bands[i]
    assert reg.grid == infer_leaf_grid(bands[d])
    assert reg.grid.boundaries == RULES
    assert [c.text for c in sorted(reg.cells, key=lambda c: c.col) if c.row == 0] == ["Region", "Total", "Share"]
    assert [c.text for c in sorted(reg.cells, key=lambda c: c.col) if c.row == 1] == list(ROWS[0])
    assert max(c.row for c in reg.cells) == len(ROWS)
    assert reg.reason == "donated"


def test_a_straddling_page_is_refused_at_the_disposal_not_at_the_derivation(tmp_path):
    """DECISION A. The same page with one value shifted across a drawn rule: the
    derivation still names the donor (drawn, refused head, same count — every fact it
    reads is present), and the disposal refuses, because the straddling word's cell does
    not round-trip. The tiling clause lives HERE now, in the shipped per-cell form."""
    from iladub.etkl.donation import donated_region, donation_admissible, donors_for

    bands = _page(tmp_path / "straddling.pdf", (80.0, 190.0, 340.0))
    i, d = _record_band(bands), _head_bands(bands)[0]
    ev = donor_evidence(bands, {d: EVERY_MEASURE})
    assert donors_for(ev, i, classify(bands[i]).grid.ncols) == (d,)
    assert donation_admissible(donated_region(bands, d, i), 0) is False


def test_offer_accepts_a_unique_donor_and_refuses_two(tmp_path):
    """DECISION E: two wholly drawn donors at the same column count is a page this
    relation cannot read. No ordinal rule; the band compiles as it does today."""
    from iladub.etkl.donation import offer

    one = _page(tmp_path / "one.pdf", (80.0, 210.0, 340.0))
    i = _record_band(one)
    d = _head_bands(one)
    assert len(d) == 1
    got = offer(one, i, classify(one[i]), donor_evidence(one, {d[0]: EVERY_MEASURE}), 0)
    assert got is not None and got.donor_index == d[0]

    two = _page(tmp_path / "two.pdf", (80.0, 210.0, 340.0), head_twice=True)
    j = _record_band(two)
    dd = _head_bands(two)
    assert len(dd) == 2, f"fixture must draw two donor bands, got {dd}"
    assert offer(two, j, classify(two[j]), donor_evidence(two, {k: EVERY_MEASURE for k in dd}), 0) is None


@corpus_only
def test_bfs_p6_the_refusal_map_names_band_2_and_no_other_band_every_measure():
    """Evidence doc § 1 row 5, through the shipped function: band 2's line 0 is the one
    head the page datagrid refuses every-measure."""
    from iladub.etkl.donation import head_line_refusals

    bands = page_bands(BFS, 6)
    got = head_line_refusals(BFS, 6, bands)
    assert got.get(2) == EVERY_MEASURE, got
    assert [k for k, v in got.items() if v == EVERY_MEASURE] == [2], got


@corpus_only
def test_bfs_p6_the_five_donations_are_admissible_with_the_spikes_entry_counts():
    """The oracle numbers of handoff 2026-09-10-the-donated-reading-tiles § 2, through the
    plan's construction rather than the spike's (DECISION D)."""
    from iladub.etkl.donation import donated_region, donation_admissible

    bands = page_bands(BFS, 6)
    for i, n in {4: 36, 5: 54, 6: 36, 8: 72, 9: 63}.items():
        reg = donated_region(bands, 2, i)
        assert donation_admissible(reg, 6), i
        assert len([c for c in reg.cells if c.row > 0]) == n, i
```

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/pytest tests/etkl/test_grid_donation_disposal.py -q`
Expected: 5 failed, `ImportError` on each new name.

- [ ] **Step 3: Write the four functions and the dataclass**

Each carries its §8 line: `head_line_refusals` is PROCEDURAL glue over two shipped derivations;
`donated_region` is the same PROCEDURAL region construction every branch does; `donation_admissible`
is the membrane reused, not copied (cite `merged_run_admissible`); `offer` decides nothing itself.

- [ ] **Step 4: Run the tests**

Run: `.venv/bin/pytest tests/etkl/test_grid_donation_disposal.py -q`
Expected: 5 passed (corpus present).

- [ ] **Step 5: FALSIFICATION**

(a) Make `donation_admissible` return `region_tiles(scratch)` alone, dropping the round-trip
conjunct. Show `test_a_straddling_page_is_refused_at_the_disposal_not_at_the_derivation` — if it
stays green, the membrane's own shapes already refuse the straddle and **the round-trip conjunct is
dead**; say so and delete it rather than keep an unpinned guard (CLAUDE.md § Producer-side guards:
keep a guard only where the membrane does not provably cover the producer's output). Restore what
survives. (b) In `offer`, accept the **first** donor instead of requiring exactly one. Show
`test_offer_accepts_a_unique_donor_and_refuses_two` **failing**. Restore. (c) In `donated_region`,
do not shift the rows. Show `test_the_donated_region_takes_…` **failing**. Restore. Show green.
Paste every output.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/donation.py tests/etkl/test_grid_donation_disposal.py
git commit -m "feat(grid donation): the head-line refusals, the donated reading, and the disposal — tiling is the membrane's, uniqueness is required"
```

---

## Task 4: The seam — `compile_tables` proposes at the assert leg, records acceptance, refuses invisibly

**Files:**
- Modify: `src/iladub/etkl/compile.py` — the prologue between `bands = page_bands(...)` (`:766`) and
  the loop (`:779`), and the assert leg at `:967-1010`
- Test: `tests/etkl/test_grid_donation_seam.py`

**Interfaces:**
- Consumes: Task 1's `donor_evidence`, Task 3's `head_line_refusals` and `offer`, the leg's existing
  locals (`region`, `band`, `idx`, `brec`, `table_uri`, `doc`, `graph`, `scratch`).
- Produces: no new public signature. **`compile_tables`' signature is unchanged.** Behaviour: before
  the loop, `evidence = donor_evidence(bands, head_line_refusals(pdf_path, page_number, bands))`
  once per page. At the assert leg, **before** `scratch = Graph()`: `d = offer(bands, idx, region,
  evidence, page_number)`; if `d` is not `None`, `region = d.region` and the leg runs unchanged on it.
  After `graph += scratch` in the accepted branch, and only if `d` is not `None`:
  `graph.add((table_uri, TAB.headerDonatedBy, URIRef(f"{doc}#table{d.donor_index}")))` and
  `brec.record("grid_donation", ["donated", "own_line_0"], "donated", <rationale naming the donor
  band index and its line-0 text>)`.

**What must stay true, and where it is pinned:**

- The leg's own `region_tiles` call still runs on the donated region — a second validation, the price
  R165's merged band also pays; do not skip it.
- R176's ledger (`compile.py:276`) sees the donor's label bboxes as recovered extents that hold none
  of this band's words — DECISION D's prediction; `test_donation_moves_no_ink_between_the_ledgers`
  measures it.
- `_emit_band_captions` / `_emit_unit_markers` are called with the band and `region.grid.boundaries`
  exactly as today; measure that no donated band on bfs p6 carries unit markers or captions before
  assuming the calls are inert.
- **The decision record is minted only on acceptance** (Global Constraint 6). Recording it shifts the
  `-d{n}` numbering of later decisions on that band; if any decision-log pin reads bfs p6 URIs it
  moves, and Task 5 says what the new number means.

**MEASURE before writing** (plan rule 3): whether `tab:headerDonatedBy` on the table node passes the
**document** membrane under `validate_shapes=True` — `_build_membrane` (`compile.py:588`) may close
`tab:RecordTable`. Run bfs p6 with `validate_shapes=True` after the seam and read the report; if the
membrane refuses the property, it is undeclared in a shape, not wrong, and the shape gains it in this
task.

- [ ] **Step 1: Write the failing tests**

```python
# tests/etkl/test_grid_donation_seam.py
"""Grid donation — the seam. compile_tables offers the donated reading at the assert leg;
the membrane disposes; acceptance is recorded; refusal is invisible.

Plan: docs/superpowers/plans/2026-09-11-grid-donation.md, Task 4
"""
import os

import pytest
from rdflib import Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF

from tests.etkl.test_grid_donation_disposal import EVERY_MEASURE, _head_bands, _page, _record_band

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(BFS), reason="corpus not fetched")
TAB = Namespace("https://w3id.org/iladub/tab#")


def _labels(g, table):
    """The table's label texts in column order, via tab:hasHeaderNode -> tab:hasLabel."""
    out = []
    for h in g.objects(table, TAB.hasHeaderNode):
        lc = g.value(h, TAB.hasLabel)
        out.append((str(h), str(g.value(lc, TAB.cellText))))
    return [t for _, t in sorted(out)]


@corpus_only
def test_bfs_p6_reads_267_entries_under_band_2s_labels():
    """The headline (handoff 2026-09-10-the-donated-reading-tiles § 2): 222 -> 267 entries,
    every donated table labelled by the author's own header, and the provenance link set."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(BFS, 6, validate_shapes=False)
    assert sum(r.cells for r in rep.regions) == 267
    g = rep.graph
    doc = next(s for s in g.subjects(RDF.type, TAB.RecordTable) if str(s).endswith("#table2"))
    doc = URIRef(str(doc).rsplit("#", 1)[0])
    donor = URIRef(f"{doc}#table2")
    want = _labels(g, donor)
    assert want[0] == "Grandes régions", want
    for idx, cells in {4: 36, 5: 54, 6: 36, 8: 72, 9: 63}.items():
        t = URIRef(f"{doc}#table{idx}")
        assert rep.regions[idx].cells == cells, idx
        assert _labels(g, t) == want, idx
        assert (t, TAB.headerDonatedBy, donor) in g, idx
    assert (donor, TAB.headerDonatedBy, None) not in g


@corpus_only
def test_donation_moves_no_ink_between_the_ledgers():
    """DECISION D's prediction, measured: the donor's label bboxes hold none of the
    continuation's words, the band's own line 0 becomes round-tripping data cells, and
    every token figure on the page is what it was at 808aa7a."""
    from iladub.etkl.compile import compile_tables

    rep = compile_tables(BFS, 6, validate_shapes=False)
    assert (rep.asserted, rep.escalated) == (276, 25)
    assert {i: (r.tokens_asserted, r.tokens_escalated) for i, r in enumerate(rep.regions)
            if i in (2, 4, 5, 6, 8, 9)} == {2: (15, 0), 4: (36, 0), 5: (54, 0), 6: (36, 0),
                                            8: (72, 0), 9: (63, 0)}


@corpus_only
def test_an_accepted_donation_is_a_recorded_decision():
    from iladub.etkl.compile import compile_tables
    from rdflib.namespace import RDFS

    g = compile_tables(BFS, 6, validate_shapes=False).graph
    labels = [str(o) for o in g.objects(None, RDFS.label)]
    assert labels.count("grid_donation") == 5


def test_a_refused_donation_leaves_the_page_isomorphic(tmp_path, monkeypatch):
    """Global Constraint 6, R165's § 3.2 in this loop's clothes. On the straddling page the
    derivation names a donor and the disposal refuses. Compare against the same page with
    the derivation suppressed: isomorphic (the honest form of byte-identical — see
    test_a_refused_run_leaves_the_page_byte_identical for why N-Triples equality is not)."""
    import iladub.etkl.donation as donation
    from iladub.etkl.compile import compile_tables

    path = tmp_path / "straddling.pdf"
    bands = _page(path, (80.0, 190.0, 340.0))
    d = _head_bands(bands)[0]
    monkeypatch.setattr(donation, "head_line_refusals", lambda *a, **k: {d: EVERY_MEASURE})
    with_proposal = compile_tables(str(path), 0, validate_shapes=False)
    monkeypatch.setattr(donation, "donors_for", lambda *a, **k: ())
    without = compile_tables(str(path), 0, validate_shapes=False)
    assert isomorphic(with_proposal.graph, without.graph)
    assert [r.verdict for r in with_proposal.regions] == [r.verdict for r in without.regions]


def test_a_headerless_band_reads_under_the_ruled_head_above_it(tmp_path, monkeypatch):
    """R166's detector, inverted for the ONE shape this loop repairs: the same four data
    rows, with the head the author ruled above them, read under 'Region Total Share' and
    assert 12 entries. (test_header_row_is_assumed's detector stays RED-by-design for
    the donor-less shape it draws; this is not that fixture.)"""
    import iladub.etkl.donation as donation
    from iladub.etkl.compile import compile_tables

    path = tmp_path / "donated.pdf"
    bands = _page(path, (80.0, 210.0, 340.0))
    i, d = _record_band(bands), _head_bands(bands)[0]
    # Task 3 measured whether derive_data_grid refuses this synthetic head every-measure.
    # If it does, DELETE this monkeypatch and let the real map carry the licence.
    monkeypatch.setattr(donation, "head_line_refusals", lambda *a, **k: {d: EVERY_MEASURE})
    rep = compile_tables(str(path), 0, validate_shapes=False)
    assert rep.regions[i].verdict == "asserted"
    assert rep.regions[i].cells == 12
    t = URIRef(rep.regions[i].table_uri)
    assert _labels(rep.graph, t) == ["Region", "Total", "Share"]
```

- [ ] **Step 2: Run them to verify they fail**

Run: `.venv/bin/pytest tests/etkl/test_grid_donation_seam.py -q`
Expected: the three corpus tests fail on counts (222, no `headerDonatedBy`, 0 decisions); the two
synthetic ones fail on labels / are trivially isomorphic — **note that the isomorphism test passes
before the seam exists** (nothing proposes, so nothing differs). That is expected: its falsification
is step 5(b), and it pins the seam only in conjunction with that.

- [ ] **Step 3: Write the seam**

As in *Interfaces*. The prologue import is local (`from .donation import head_line_refusals, offer`),
matching the leg's existing `from .tiling import region_tiles` style. **Look `offer` up through the
module** (`donation.offer`), not by name, so the tests' `monkeypatch.setattr(donation, …)` reaches it —
the late binding `page_bands` relies on for `merged_run_admissible` (`compile.py:400-403`).

- [ ] **Step 4: Run the tests, then the modules that read bfs p6**

Run: `.venv/bin/pytest tests/etkl/test_grid_donation_seam.py tests/etkl/test_grid_donation_disposal.py tests/etkl/test_run_merge_seam.py tests/etkl/test_datagrid.py tests/etkl/test_escalation_furnish.py tests/etkl/test_header_row_is_assumed.py tests/etkl/test_grid_donation_relation.py -q`
Expected: the five new pins pass; `test_run_merge_seam.py`'s `BASELINE_ASSERTED[("bfs-…", 6)] == 276`
holds (DECISION D's prediction — if it moves, the ledger moved, and the task report says by what).
Any other red here is Task 5's list, not this task's to silence.

- [ ] **Step 5: FALSIFICATION**

(a) Make the seam take `d.region` but skip the `headerDonatedBy` triple. Show
`test_bfs_p6_reads_267_entries_under_band_2s_labels` **failing** on the provenance assertion. Restore.
(b) Make `offer`'s refusal record a `brec.record("grid_donation", …, "own_line_0", …)`. Show
`test_a_refused_donation_leaves_the_page_isomorphic` **failing**. Restore. (c) Skip the `region =
d.region` assignment (emit the link and the decision but assert the band's own reading). Show
`test_a_headerless_band_reads_under_the_ruled_head_above_it` **failing** on labels. Restore. Show
green. Paste all.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_grid_donation_seam.py
git commit -m "feat(grid donation): compile_tables offers the donated reading at the assert leg — bfs p6 reads 267 entries under the author's header"
```

---

## Task 5: The corpus oracle, the re-baseline, and the manifest reading

**Files:**
- Modify: whichever test modules Step 1 turns red (measured, not listed — none is predicted)
- Modify: `tests/corpus-manifest.ttl` (append one `cor:reading` to the bfs entry after `:225`)

- [ ] **Step 1: The whole-corpus before/after**

`scripts/corpus_verdict_snapshot.py` is the committed instrument (one reading per tree; its docstring
says why two readings cannot share a process). Take one on `main` and one on this branch:

```bash
git stash -u 2>/dev/null; git checkout main && PYTHONPATH=src .venv/bin/python scripts/corpus_verdict_snapshot.py /tmp/snap-before
git checkout - && git stash pop 2>/dev/null; PYTHONPATH=src .venv/bin/python scripts/corpus_verdict_snapshot.py /tmp/snap-after
diff -r /tmp/snap-before /tmp/snap-after
```

**Expected, and the task report must confirm or refute each line:** six documents hash-identical;
bfs differs **only** on page 6 (entries 222 → 267, five verdict rows change cell counts, no verdict
changes, `adopted=()` before and after); bfs document score **unchanged at 0.4033** (DECISION D). A
difference anywhere else is a finding, not noise — name the page and the triple.

- [ ] **Step 2: The wall clock**

`scripts/doc_walltime.py`, once per tree, read call counts before seconds (its docstring). Report the
after-figure beside M1's 4.9 s bound. **Do not build a cache** ([[R168]] / R172 are the rows).

- [ ] **Step 3: Re-baseline what moved, saying what the new number means**

Run the corpus-gated modules that index bfs or count decisions:
`tests/etkl/test_decision_queries.py tests/etkl/test_decisionlog.py tests/etkl/test_typing_equiv.py
tests/etkl/test_membrane_health.py tests/etkl/test_adoption_document.py tests/etkl/test_document_membrane_gate.py`.
For each red: a moved number is only allowed to move if the report says what it now means (the R165
plan's Task 5 rule). Nothing here may be silenced by widening an assertion.

- [ ] **Step 4: Append the bfs reading**

After `tests/corpus-manifest.ttl:222-225`'s reading node, append one `cor:reading` in the same shape —
`cor:value` the measured document score, `cor:readAt "2026-09-11"^^xsd:date`, `cor:atCommit` the
branch head at the time of measurement, `cor:recordedIn` this plan's evidence doc (Task 6). If the
score is unchanged, append it anyway: the register is a refresh log ([[R198]]), and an unchanged figure
under a changed reading is the fact worth dating.

- [ ] **Step 5: FALSIFICATION**

Run `tests/test_arc_manifest.py` and `tests/test_doc_governance.py`. Then remove the appended
`cor:atCommit` from the new node and show the manifest membrane **failing**; restore; green.

- [ ] **Step 6: Commit**

```bash
git add tests/corpus-manifest.ttl <re-baselined modules>
git commit -m "measure(grid donation): whole-corpus snapshot — six documents identical, bfs p6 222 -> 267; the bfs reading appended"
```

---

## Task 6: The register, the wiki, the evidence doc, the whole suite, the PR

**Files:**
- Modify: `docs/superpowers/residues.md`, `docs/superpowers/residues-open.md`
- Modify: `docs/wiki/concepts/neurosymbolic-exemplars.md` (a new `##` section after `:213`'s)
- Create: `docs/superpowers/2026-09-11-grid-donation-evidence.md`

- [ ] **Step 1: The register — re-run the tally first**

```
$ awk -F'|' '/^\| ~?~?R[0-9]/{t++; if ($3 ~ /closed/) c++} END{print c"/"t" closed"}' docs/superpowers/residues.md
63/198 closed          # measured 2026-09-11 before this plan; the last row is R208
```

| row | action |
| --- | --- |
| **~~R201~~** | **CLOSE.** Its closure condition (spec § 5) is met: bands 4/5/6/8/9 read under band 2's header. Strike the number, record the evidence in place (267 entries, 45 → 0 false labels, `test_bfs_p6_reads_267_entries_under_band_2s_labels`). Do not delete the row. |
| **~~R203~~** | **CLOSE.** The derivation ships (`tab:headLineRefusal`, DECISION C); its membrane arm was struck 2026-09-10 and stays struck. Record that it is exercised on ONE donor (→ R210). |
| **R166** | **APPEND**: 5 of the 11 false label rows repaired by donation; the 6 donor-less bands (apple p2 band 6, who p0/p1 band 4, cbh p0 band 9, graincorp p0 band 3, bfs p5 band 13) untouched; the page-scope criterion of evidence doc § 2 remains the proposition for them. |
| **R205** | **APPEND**: bands 3 and 7 still `ignored`, 0 cells, after donation — the loss the ruling accepted; band 10's joined cell is the third instance. |
| **R160** | **untouched** (evidence doc § 3 appended the bfs instance; the ruling is the maintainer's). |
| **R168** | **APPEND** the after wall-clock and the datagrid's per-page cost. |
| **R209 (63/199 closed)** | *The disposal's refusal has no corpus instance.* M3: 5 structural pairs, 5 accepted — `donation_admissible` is exercised in the refusing direction only by the synthetic straddling page. Closed by a corpus document with a drawn, same-count, refused-head donor whose continuation straddles it. |
| **R210 (63/200 closed)** | *The R203 licence is exercised on one donor, and a page TITLE as a donor's line 0 is the case the forward direction cannot separate* (evidence doc § 2: bfs p5/p6 titles are refused `every-measure` exactly as headers are). Whether a title line can sit inside a wholly-drawn grid at all is unmeasured. Closed by a second ruled donor in the corpus, or by a measurement that a title inside a drawn grid is impossible by construction. |

Re-run the tally before writing each row's snapshot; if another loop has landed, the numbers move.

- [ ] **Step 2: The wiki exemplar**

One `##` section in `docs/wiki/concepts/neurosymbolic-exemplars.md`, in the shape of `:213`'s R165
entry: the AXIOM (`grid-donation.rq`, four positive facts, one holon-scoped closed clause), why the
tiling clause is the membrane's (DECISION A), the disposal reused not copied, the measured figures
**with their date and commit** (the R187 figure gate is HARD — a bare figure fails the suite), and the
exposure: R209/R210.

- [ ] **Step 3: The evidence doc**

`docs/superpowers/2026-09-11-grid-donation-evidence.md`: every task's FALSIFICATION output, the
snapshot diff summary, the wall clock, the re-baseline table, and **Doc impact: increment** restated
with the two increments named. **Part 5 of its handoff is written FIRST and typed** (CLAUDE.md § The
handoff's next action is TYPED).

- [ ] **Step 4: The whole suite, in-band**

Run: `.venv/bin/pytest -q -p no:cacheprovider 2>&1 | tail -30` — foreground, once, ~45–60 minutes.
Read the tail: the count of passed/failed/skipped, and every failure's name. The one test that is
RED by design and must stay red: `test_a_headerless_band_asserts_its_first_data_row_as_the_column_header`
is **not** red today (its fixture asserts the false header, which is what it pins) — confirm it is
still green and still describes the donor-less shape.

- [ ] **Step 5: Commit, push, PR**

```bash
git add docs/superpowers/residues.md docs/superpowers/residues-open.md docs/wiki/concepts/neurosymbolic-exemplars.md docs/superpowers/2026-09-11-grid-donation-evidence.md
git commit -m "R201 + R203 closed: grid donation — the datagrid derives the donor's header, the membrane disposes, bfs p6 reads 267 entries under the author's labels"
git push -u origin grid-donation
gh pr create --title "R201 + R203 closed: grid donation" --body-file <the evidence doc's summary>
gh pr merge --auto --squash
```

`--auto` waits for `test` under the ruleset (CLAUDE.md § Open items, proven on PR #136).

---

## Self-review against the spec

| spec | task |
| --- | --- |
| § 3 relation: `tiles` | Task 3 (disposal, DECISION A) + `test_a_straddling_page_is_refused_at_the_disposal_…` |
| § 3 relation: `same_ncols` | Task 2 query + `test_the_wrong_column_count_is_refused_graincorp_p0s_shape` |
| § 3 relation: `drawn` | Task 1 emitter + Task 2 query + `test_an_inferred_interior_boundary_refuses_the_donor` |
| § 3(b) uniqueness, no ordinal rule | Task 3 `offer` (DECISION E) + `test_offer_accepts_a_unique_donor_and_refuses_two` |
| § 4 the reading: line 0 is data, labels are the donor's | Task 3 `donated_region` (DECISION D) + Task 4 `test_bfs_p6_reads_267_entries_under_band_2s_labels` |
| § 4 AXIOM, no tolerance, `COORD_EPS` not repurposed | Global Constraint 1; DECISION A keeps the epsilon in `cell_round_trips` only |
| § 4 disposed by the shipped membrane, refusal leaves the band as today | Task 3 `donation_admissible` + Task 4 `test_a_refused_donation_leaves_the_page_isomorphic` |
| § 4 no merge, no contiguity, indices do not renumber | DECISION B (seam at the leg; `page_bands` untouched) |
| § 4 closure-scope: the collapse stays holon-scoped | the emitter reads `_rule_boundaries`' vector as-is; no donor boundary is ever dropped for want of ink in the continuation |
| § 5 does not repair band 2's body | out of scope, R203's related note; band 2's own 6 cells unchanged (`(2,'asserted',6,15,0)` pinned in `test_donation_moves_no_ink_…`) |
| § 6 R203 — the donor's header derived | Task 1 `tab:headLineRefusal`, Task 2 query clause, Task 3 `head_line_refusals` (DECISION C) |
| handoff decision 1 — the AXIOM in the page-scoped graph | Task 1 emitter beside `run_evidence`; Task 2 query; DECISION B for the per-band bindings |
| evidence doc § 4 — the refusal reaches the graph as a fact on the donor's line 0, by ink | Task 1 + Task 3 (Global Constraint 5), M2 |

**Placeholder scan:** none. **Type consistency:** `donors_for(evidence, idx, ncols) -> tuple[int, ...]`,
`donated_region(bands, donor_idx, idx) -> ClassifiedRegion`, `donation_admissible(region, page_number)
-> bool`, `offer(bands, idx, region, evidence, page_number) -> Donation | None`,
`head_line_refusals(pdf_path, page_number, bands) -> dict[int, str]`, `donor_evidence(bands,
head_refusals) -> Graph` — used identically in Tasks 2, 3 and 4.

**Where this plan is a proposition, not an assertion** (CLAUDE.md § The handoff's next action is
TYPED): DECISION D's ledger prediction (tokens and scores unchanged) and DECISION B's claim that no
donated band is transposed or row-grouped under its own reading are **predictions Task 4 runs**; the
`initBindings`-in-`FILTER` behaviour and the synthetic datagrid's verdict on the head line are
**seams the implementer measures before writing**. Everything else above carries its measurement.
