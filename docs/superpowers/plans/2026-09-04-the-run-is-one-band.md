# The run is one band — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** `compile.page_bands` proposes a contiguous run of ruled bands as ONE band, the existing
tiling membrane disposes of the proposal, and a refusal leaves the page byte-identical to today.

**Architecture:** A SPARQL derivation over a transient per-page evidence graph enumerates candidate
runs (AXIOM, open world); the existing `is_matrix_candidate → classify_matrix →
assert_matrix_region → region_tiles` chain disposes of each candidate on a scratch graph (closed
world, at the membrane). Neither half is new machinery: the derivation copies the
`section_candidates` idiom verbatim and the disposal is reused, not copied.

**Tech Stack:** Python 3, rdflib, pySHACL, pytest. RDF Turtle for the vocabulary, SPARQL `SELECT`
for the derivation.

**Spec:** `docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md`

**Measurement the spec rests on, in the order it must be read when a task cites it:**

| doc | what it is |
| --- | --- |
| `docs/superpowers/2026-09-04-r165-preplan-spike.md` | the seam, M1's cost, the O5 patch point, the real test surface. § "What this changes for the plan" items 1–8 and § Q-D D1–D6 are corrections this plan carries |
| `docs/superpowers/2026-09-04-r165-three-claims-measured.md` | the SPARQL derivation (§ A), the apple-p1 token ledger (§ B), the wall-clock (§ C), six controller-side seams (§ D) |
| `docs/superpowers/2026-09-04-one-band-matrix-spike.md` | the original reading measurement (§ 2–3, § 7 the licence census, § 8 the band index) |

**Doc impact: increment.** Per spec preamble: `tests/corpus-manifest.ttl`'s apple entry gains a third
`cor:adjudication` node (append-only — see spike § Q-D D6); `docs/wiki/concepts/neurosymbolic-exemplars.md`
gains one AXIOM derivation. No released assertion changes; **no contradiction**, so nothing blocks a
release tag.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **The neurosymbolic gate (CLAUDE.md §8), as argued in spec § 2 for THIS subject.** D1 ("which
   contiguous bands are candidates for one table?") is **AXIOM / derivation / open world** — it
   enumerates, it does not settle. D2 ("is the merged reading admissible?") is the **existing
   closed-world membrane**, reused verbatim. **A tuned constant or tolerance anywhere in the shipped
   diff is a review failure**, and so is a new numeric literal in the `.rq`.
2. **No re-tuning of `_rule_xs_signature`'s 2dp rounding** (spec § 4 item 6). It is inherited. Note
   that it changes the run set on **0 of 27 pages** (three-claims § A.3) — it is guarding a hazard
   that does not fire, and this loop neither justifies nor removes it.
3. **Source ownership (CLAUDE.md § Source ownership).** Every new term is in `tab:` =
   `https://w3id.org/iladub/tab#`, which we own. No HGA IRI appears as a subject anywhere.
4. **Plan rules 1–7 (CLAUDE.md § Plan authoring discipline).** No function body appears in this
   plan. Tests are supplied verbatim and are **propositions**: a test that cannot be made to pass has
   found a plan or spec defect — say so in the task report and substitute the satisfiable form
   carrying the same force; never weaken the assertion. **Every task ships a `## FALSIFICATION`
   block** (rule 4): remove or invert the thing the new test pins, show it failing, restore, show
   green. No falsification evidence ⇒ the task review fails.
5. **`corpus/` is gitignored (`.gitignore:52`).** A fresh `git worktree` has **no corpus**, and every
   corpus-dependent test then **skips silently and reports green**. Symlink it before running
   anything: `ln -s "/Volumes/WD Green/dev/git/iladub/corpus" corpus`, and verify
   `ls corpus/financial` lists files. This was hit for real in the predecessor loop (three-claims
   § 0). **A green run in a worktree with no corpus falsifies nothing.**
6. **The full suite takes ~45 minutes and must NOT be run in a background subagent** (a measured
   trap — `docs/superpowers/2026-09-02-the-body-starts-at-the-stub-handoff.md`). Run it in-band,
   once, at Task 7.
7. **Branch protection (CLAUDE.md § Branch protection).** Every commit reaches `main` through a PR
   whose `test` check is green. Branch first; direct pushes to `main` are refused.

---

## The four decisions this plan takes, that the spec left open

The spec required each of these to be *decided and justified in the plan*, not defaulted. They are
stated once here and **cited** from the tasks (plan rule 6).

### DECISION A — the term-shape fork (§ Q-D D1): shape **(a)**, a band-scoped datatype property

Spec § 6 asks for `tab:ruleX` on the new class. **That is REFUTED**: `tab:ruleX` already exists with
`rdfs:domain tab:RuleSpan` and two shipped query consumers (spike § Q-D D1). The fork is genuinely
open, because the run-evidence graph is **outside** `probe_domain_range_agreement`'s population
(three-claims § A.5) — so this is a modelling-honesty decision, not a gate-passing one, and cost does
not decide it either (0.30 s vs 0.60 s over 27 pages, three-claims § A.4; neither is a budget item
beside `page_bands`' 0.03–3.93 s/page).

**Take (a): a new datatype property `tab:bandRuleX`, `rdfs:domain tab:RuledBand`.** Three reasons:

- The fact the derivation needs is *"this band's set of distinct rounded rule x-positions"* — a
  property of the **band**. `tab:ruleX` means *"this drawn rule segment's x"* — a property of a
  **segment**. Putting it on a band node asserts exactly the domain disagreement
  `scripts/probe_domain_range_agreement.py` grades as a modelling defect.
- Shape (b) is honest only in its `gridregion.py:53-58` form, one `tab:RuleSpan` per **rule** — which
  is what makes it 1869 triples on apple p0 against 101. The distinct-x variant that would close the
  cost gap emits `tab:RuleSpan` nodes carrying no `tab:ruleTop`/`tab:ruleBottom`, i.e. spans that are
  not spans: it trades a domain disagreement for a class lie.
- (b) buys nothing the relation uses. The relation never reads a rule's y-extent.

### DECISION B — `tab:bandIndex`'s domain (three-claims § A.5): a common superclass `tab:PageBand`

§ A.5 found the fork is **wider** than § Q-D D1 says: `tab:bandIndex` is declared
`rdfs:domain tab:SectionBand` (`vocab/ontology/tab.ttl:302`), so spec § 6's `run_evidence` contract
hits it too. Three shapes were open, and the choice is:

**Declare `tab:PageBand` and move `tab:bandIndex`'s domain to it, with `tab:SectionBand rdfs:subClassOf
tab:PageBand` and `tab:RuledBand rdfs:subClassOf tab:PageBand`.**

- The two classes have genuinely different populations — spec § 6's argument stands and is the reason
  `tab:RuledBand` exists at all: `section_evidence` abstains for any band whose header box is not
  locatable, so a `tab:RuledBand` is **not** a `tab:SectionBand` and must not be declared one, or the
  new derivation silently inherits that abstention as a modelling claim.
- But *"the band's 0-based position among the page's bands, exactly as `compile.page_bands`
  enumerates them"* — `tab:bandIndex`'s own `rdfs:comment` — is the **identical fact** for both. A
  second index property would be a synonym; reuse without a superclass would be a domain
  disagreement. Generalising the domain is additive and changes nothing about `tab:SectionBand`.
- **MEASURED before deciding, not read** (plan rule 2): nothing reads `tab:bandIndex`'s declared
  *domain*; the property has exactly two consumers, both of which bind it as a predicate.

  ```
  $ grep -rn "bandIndex" vocab/ tests/ src/ --include="*.rq" --include="*.ttl" --include="*.py" \
        | grep -v "^vocab/ontology/tab.ttl"
  vocab/queries/section-repeat.rq:19:  ?u1 a tab:SectionBand ; tab:bandIndex ?a ; …
  vocab/queries/section-repeat.rq:20:  ?u2 a tab:SectionBand ; tab:bandIndex ?b ; …
  src/iladub/etkl/sectiongraph.py:205:        g.add((u, TAB.bandIndex, Literal(idx, datatype=XSD.integer)))
  ```

### DECISION C — adjacency is **literal-free**, via an emitted predecessor fact

Spec § 3.4 asks for `?b = ?a + 1` **and** for "no numeric literal"; three-claims § A.2 proves those
are incompatible and measured both forms at 14/14. **Take the literal-free form**: the emitter emits
`tab:prevBandIndex` and the query joins on it. `vocab/queries/section-repeat.rq:15` makes *"this query
contains no numeric literal"* a standing property of the idiom § 3.4 says this loop copies, and
weakening that property is not this loop's to do.

`tab:prevBandIndex` is emitted for every band at index > 0, **whether or not its predecessor emitted a
node**. When the predecessor abstained (no rules) the join simply finds nothing — which is the correct
behaviour: an unruled band never joins, and it breaks the chain.

### DECISION D — overlap (§ 3.2): **no resolution rule, and that is the decision**

§ 3.2 requires the implementation to "state and pin its resolution rule" for two accepted runs sharing
a band, and suggests *longest run first, then leftmost*. **That tie-break can never fire here and must
not be written.** `merge_run_candidates` returns *maximal contiguous chains under an adjacent
relation over a linear index*, and maximal chains under adjacency on a line are disjoint by
construction. § 3.2's rule presupposes an enumerator that can propose overlapping runs — the design
in § 3.5 that was **rejected on measurement** (enumerate all 266 contiguous runs) is that enumerator;
this one is not.

The obligation is discharged by **pinning disjointness as an invariant of `merge_run_candidates`**
(Task 2, test 3), not by adding a tie-break that is dead code the day it ships.

---

## File Structure

| file | created / modified | responsibility |
| --- | --- | --- |
| `vocab/ontology/tab.ttl` | modify (~`:290`, `:300-306`) | declare `tab:PageBand`, `tab:RuledBand`, `tab:bandRuleX`, `tab:prevBandIndex`; move `tab:bandIndex`'s domain |
| `src/iladub/etkl/sectiongraph.py` | modify (append beside `section_evidence`/`section_candidates`, `:190-245`) | `run_evidence`, `merge_run_candidates` — the sibling emitter and the sibling assembler |
| `vocab/queries/band-run.rq` | **create** | the derivation: adjacent comparable pairs, literal-free |
| `src/iladub/etkl/compile.py` | modify (`page_bands` `:270-323`; new module-level `merge_bands`, `merged_run_admissible`) | the seam: propose, dispose, splice; M1 |
| `tests/etkl/test_band_runs.py` | **create** | O1, O2, the emitter's abstain, disjointness, the 8-field merge pin |
| `tests/etkl/test_run_merge_seam.py` | **create** | O3 (corpus no-regression), O4 (fragment/position), O5 (forced non-tail) |
| `tests/test_query_terms.py` | modify (`:62`) | re-pin the query population 49 → 50 |
| 5 existing test modules | modify | the 14 measured re-baselines (Task 5) |
| `tests/corpus-manifest.ttl` | modify (append after `:118`) | a third `cor:adjudication` node for apple |
| `docs/superpowers/residues.md` + `residues-open.md` | modify | `R170`, `R171`, `R172` |
| `docs/wiki/concepts/neurosymbolic-exemplars.md` | modify | one AXIOM derivation entry |

---

## Task 1: The vocabulary and the run-evidence emitter

**Files:**
- Modify: `vocab/ontology/tab.ttl:290`, `:300-306`
- Modify: `src/iladub/etkl/sectiongraph.py` (append after `section_evidence`, `:190-208`)
- Test: `tests/etkl/test_band_runs.py` (create)

**Interfaces:**
- Produces: `sectiongraph.run_evidence(bands: Sequence[Band]) -> Graph`.
  One `tab:RuledBand` node per band **that carries rules**, at `_EV["runband-%d" % idx]`, carrying
  `tab:bandIndex` (`xsd:integer`), `tab:prevBandIndex` (`xsd:integer`, only when `idx > 0`), and one
  `tab:bandRuleX` per **distinct rounded (2dp)** x in `band.rules`. **A band with no rules emits
  NOTHING** — no node, no type triple. Index = position in the passed list.
- Consumes: nothing.

**Why `Sequence[Band]` and not `section_evidence`'s `(idx, band, rules)` triples** — the spec's § 6
line (`run_evidence(bands) -> Graph`) does not say. This is the plan's call: `page_bands` holds a
plain band list and each band's `rules` are already on it (`bands.py:19`), so taking the list directly
keeps **one** index space (spec § 3.0) instead of asking the caller to build a parallel one.

- [ ] **Step 1: Declare the four terms in `vocab/ontology/tab.ttl`**

Add, in the intra-page evidence block (beside `tab:SectionBand`, `:300-306`):

- `tab:PageBand a owl:Class` — "one band of a page, as transient evidence". Its `rdfs:comment` must
  say it is the **shared** superclass of the two evidence classes and that the ONLY thing shared is
  the index; the populations differ (DECISION B).
- `tab:SectionBand rdfs:subClassOf tab:PageBand` — added to the existing declaration, nothing else
  about it changes.
- `tab:RuledBand a owl:Class ; rdfs:subClassOf tab:PageBand` — "a band carrying rules". Its comment
  must state, in one line, why it is **not** `tab:SectionBand` (spec § 6: `section_evidence` abstains
  when the header box is unlocatable, so conflating them would make the new derivation silently
  inherit that abstention).
- `tab:bandRuleX a owl:DatatypeProperty ; rdfs:domain tab:RuledBand ; rdfs:range xsd:decimal` — one
  distinct rounded (2dp) rule x-position of the band. Comment: same 2dp rounding as
  `tab:ruleXsSignature`, inherited from `sectiongraph._rule_xs_signature`, **not re-tuned**; and why
  it is not `tab:ruleX` (DECISION A).
- `tab:prevBandIndex a owl:DatatypeProperty ; rdfs:domain tab:PageBand ; rdfs:range xsd:integer` —
  the index of the band immediately before this one. Comment: it exists so adjacency is a **join on a
  fact** rather than arithmetic on a literal, preserving `section-repeat.rq:15`'s standing property
  (DECISION C). It is emitted whether or not the predecessor emitted a node.

Move `tab:bandIndex`'s domain from `tab:SectionBand` to `tab:PageBand` (`:302`), leaving its range,
label and comment untouched.

> **Plan rule 7 — this edit's citations.** `tab.ttl` comments in this block cite `sectiongraph.py`
> by symbol, not by line. Keep it that way: do not introduce a `file:line` citation pointing
> **downward inside `tab.ttl` itself**, and if you touch one that already does, **re-measure after
> the edit, not only before**.

- [ ] **Step 2: Write the failing tests**

```python
# tests/etkl/test_band_runs.py
"""R165 — the run is one band. The derivation half.

Spec: docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md
"""
from rdflib import Graph, Namespace

from iladub.etkl.bands import Band
from iladub.etkl.geometry import Line, Rule, Word

TAB = Namespace("https://w3id.org/iladub/tab#")


def _rule(x, top=0.0, bottom=10.0):
    return Rule(x=x, top=top, bottom=bottom)


def _band(xs, y=0.0):
    """A band whose rules sit at `xs`. Lines are irrelevant to run_evidence and are
    deliberately minimal — the emitter reads geometry, never text."""
    w = Word(text="x", x0=0.0, x1=1.0, top=y, bottom=y + 1.0)
    return Band(lines=(Line(words=(w,), top=y, bottom=y + 1.0),),
                top=y, bottom=y + 1.0,
                rules=tuple(_rule(x) for x in xs))


def test_a_band_with_no_rules_emits_no_node_at_all():
    """THE emitter invariant, and the one thing the .rq cannot defend.

    A node emitted with ZERO tab:bandRuleX facts makes both legs of the subsumption
    vacuously true, so it would join EVERY adjacent band in both directions —
    derived runs [(0,2)] where the relation says [] (three-claims measurement § A.1).
    The protection is entirely the emitter's honest abstain, exactly as
    section_evidence's `continue` already does for its own population."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.0, 20.0, 30.0]), _band([]), _band([10.0, 20.0])])
    indices = sorted(int(o) for o in g.objects(None, TAB.bandIndex))
    assert indices == [0, 2], "the ruleless band at index 1 must emit nothing"
    assert (None, None, TAB.RuledBand) not in g or len(
        set(g.subjects(None, TAB.RuledBand))) == 2


def test_the_emitter_emits_distinct_rounded_xs_not_one_per_rule():
    """The relation is over the band's SET of distinct rounded x-positions. Two rules
    at the same rounded x are one fact, not two — otherwise the subsumption legs
    compare multisets."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.001, 10.004, 20.0])])
    xs = sorted(float(o) for o in g.objects(None, TAB.bandRuleX))
    assert xs == [10.0, 20.0]


def test_the_predecessor_index_is_a_fact_and_index_zero_has_none():
    """DECISION C: adjacency is a join on an emitted fact, never arithmetic on a
    numeric literal — so the .rq keeps section-repeat.rq:15's standing property."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.0]), _band([10.0])])
    prevs = {int(s_i): int(p)
             for s in g.subjects(None, TAB.RuledBand)
             for s_i in [next(g.objects(s, TAB.bandIndex))]
             for p in g.objects(s, TAB.prevBandIndex)}
    assert prevs == {1: 0}, "index 0 has no predecessor fact; index 1 has exactly one"


def test_the_predecessor_fact_is_emitted_even_when_the_predecessor_abstained():
    """DECISION C, second half. Band 1 has no rules and emits nothing; band 2 still
    carries prevBandIndex=1. The join then finds nothing — which is the CORRECT
    behaviour (an unruled band never joins, and it breaks the chain), and it must be
    the emitter that is simple, not the query."""
    from iladub.etkl.sectiongraph import run_evidence

    g = run_evidence([_band([10.0]), _band([]), _band([10.0])])
    node = next(s for s in g.subjects(None, TAB.RuledBand)
                if int(next(g.objects(s, TAB.bandIndex))) == 2)
    assert int(next(g.objects(node, TAB.prevBandIndex))) == 1
```

**MEASURE before writing the test bodies, do not assume** (plan rule 3): the exact constructor
signatures of `Line`, `Rule` and `Word` in `src/iladub/etkl/geometry.py`. The helpers above are
written from the field names used elsewhere in `tests/etkl/`; if a keyword differs, **fix the helper,
not the assertion**.

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m pytest tests/etkl/test_band_runs.py -q -p no:randomly`
Expected: 4 failed — `ImportError` / `AttributeError: module 'iladub.etkl.sectiongraph' has no
attribute 'run_evidence'`.

- [ ] **Step 4: Implement `run_evidence`**

A sibling of `section_evidence` (`sectiongraph.py:190-208`) — same transient-graph shape, same
honest-abstain `continue`, same `XSD.integer` on the index (three-claims § A.2 measured that an index
emitted as a **string** derives `[]` **silently**, with no error). Reuse the module's existing 2dp
rounding; **do not introduce a second rounding site**.

- [ ] **Step 5: Run the tests, and the two declaration gates**

Run:
```
python3 -m pytest tests/etkl/test_band_runs.py tests/test_query_declarations.py \
    tests/test_query_terms.py -q -p no:randomly
```
Expected: `test_band_runs` 4 passed; the two declaration modules still pass (no query names the new
terms yet, so the count pin at `tests/test_query_terms.py:62` is still 49 at this point).

- [ ] **Step 6: Run the section-recognition regression, because Step 1 edited a shipped declaration**

Run: `python3 -m pytest tests/etkl/test_section_repair.py tests/etkl/test_supersession_queries.py -q -p no:randomly`
Expected: green. Both consume `tab:bandIndex` and `tab:SectionBand`; DECISION B claims the domain move
is additive, and this is the check that it is. (Spike § Q-C measured both green under the prototype —
if either moves here, **the vocabulary edit did it**, and that is a finding.)

- [ ] **Step 7: FALSIFICATION**

Delete the `continue` that makes `run_evidence` abstain for a ruleless band (emit the node with no
`tab:bandRuleX` facts). Show `test_a_band_with_no_rules_emits_no_node_at_all` **failing**. Restore.
Show the 4 tests green. Paste both outputs in the task report.

- [ ] **Step 8: Commit**

```bash
git add vocab/ontology/tab.ttl src/iladub/etkl/sectiongraph.py tests/etkl/test_band_runs.py
git commit -m "feat(R165): tab:RuledBand + the run-evidence emitter, with the honest abstain pinned"
```

---

## Task 2: The derivation query and the run assembly

**Files:**
- Create: `vocab/queries/band-run.rq`
- Modify: `src/iladub/etkl/sectiongraph.py` (append after `section_candidates`, `:211-245`)
- Modify: `tests/test_query_terms.py:62`
- Test: `tests/etkl/test_band_runs.py` (append)

**Interfaces:**
- Consumes: `run_evidence` (Task 1) and the four terms it declares.
- Produces: `sectiongraph.merge_run_candidates(bands: Sequence[Band]) -> tuple[tuple[int, int], ...]`
  — maximal contiguous runs as `(first, last)` with `last > first`, **disjoint**, ascending by
  `first`, deterministic.

**The relation, stated once (spec § 3.3):** a run extends from band *i* to band *i+1* when both bands
carry rules and one's set of distinct rule x-positions is a **subset of the other's, in either
direction**. Runs are the maximal contiguous chains under that adjacent relation. An unruled band
never joins.

- [ ] **Step 1: Write the query `vocab/queries/band-run.rq`**

`SELECT ?a ?b`, over the transient per-page graph `run_evidence` builds. Its header comment must state
(the `section-repeat.rq` convention, which this file copies):

- the open-world / one-page-closure argument — the page is the closure boundary, one fresh `Graph` per
  `merge_run_candidates` call, exactly like `section-repeat.rq`, `classify-kind.rq` and
  `grid-region.rq`;
- that the derivation **enumerates candidates and settles nothing** — the tiling membrane disposes
  (spec § 2, D1/D2). This is the sentence a reviewer checks the §8 classification against;
- **"this query contains no numeric literal"**, as `section-repeat.rq:15` does.

Three constraints on its body, all measured:

1. **Adjacency is the `tab:prevBandIndex` join** (DECISION C), never `FILTER(?b = ?a + 1)`.
2. **The two subsumption legs must sit inside ONE `FILTER(… || …)`, never as two `UNION` branches** —
   a `UNION` branch is evaluated independently, so `?a`/`?b` fall out of scope (three-claims § A.4,
   construction note).
3. Each leg is a holon-scoped `FILTER NOT EXISTS { ?a tab:bandRuleX ?x . FILTER NOT EXISTS { ?b
   tab:bandRuleX ?x } }`, closing **within** the one page graph (spec § 3.4).

**A hazard the query cannot defend, and does not have to** (three-claims § A.3): `NOT EXISTS` matches
by **term**, not value — `"10.0"^^xsd:decimal` and `"10.00"^^xsd:decimal` do not match. The emitter is
the guarantee: one emitter produces every x, `Literal(Decimal(str(round(r.x, 2))))` is lexically
canonical across all 3,668 corpus literals, and 0 values carry more than one lexical form. **Do not
add a `STR()`/`xsd:decimal()` cast to work around this** — a cast would hide a future emitter defect
that the single-emitter invariant is supposed to make impossible.

- [ ] **Step 2: Re-pin the query population**

`tests/test_query_terms.py:62` reads `assert len(query_files()) == 49`. It becomes **50**. Record the
re-measurement and its cause in the docstring in place, following that file's own 46 → 48 → 49
convention (spike § Q-D D2).

- [ ] **Step 3: Write the failing tests (O1 — two-sided)**

```python
# appended to tests/etkl/test_band_runs.py
import pytest

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
APPLE = os.path.join(CORPUS, "financial", "apple-fy2026q3-statements.pdf")
STEM = os.path.join(CORPUS, "ag-trade", "graincorp-stem-2026-07-31.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus not fetched")


def test_the_relation_is_subsumption_not_equality_apple_p1():
    """O1, first half. Under set EQUALITY apple p1 stops at (2,3) — 26 entries, not the
    56 measured. Under adjacent subsumption its six ruled bands are ONE run 2..7.
    (spec § 1.2 refutation 1, § 3.3 Q1/Q2.)"""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import merge_run_candidates

    bands = page_bands(APPLE, 1)
    assert merge_run_candidates(bands) == ((2, 7),)


def test_the_relation_joins_the_dangerous_case_too_graincorp_stem_p0():
    """O1, SECOND half, and it is the half that matters: a test that only pinned apple
    would pass for a relation that special-cases it.

    graincorp-stem p0 band 1 is a TITLE band ('SHIPPING STEM', 5 rule x's) whose set is a
    strict subset of the table's 20. The relation JOINS them — 586 asserted cells are
    inside that proposed run — and only the oracle keeps them (spec § 3.3, R171)."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import merge_run_candidates

    bands = page_bands(STEM, 0)
    assert (1, 2) in merge_run_candidates(bands)


def test_runs_are_disjoint_and_ascending_across_the_whole_corpus():
    """DECISION D: maximal contiguous chains over adjacency on a linear index are
    disjoint BY CONSTRUCTION, which is why § 3.2's 'longest run first, then leftmost'
    tie-break is not implemented. This is the pin that makes that argument checkable
    rather than asserted."""
    from iladub.etkl.compile import page_bands
    from iladub.etkl.sectiongraph import merge_run_candidates

    for pdf, page in [(APPLE, 0), (APPLE, 1), (APPLE, 2), (STEM, 0)]:
        runs = merge_run_candidates(page_bands(pdf, page))
        assert list(runs) == sorted(runs), (pdf, page)
        seen = set()
        for first, last in runs:
            assert last > first, (pdf, page, first, last)
            span = set(range(first, last + 1))
            assert not (span & seen), f"overlapping runs on {pdf} p{page}: {runs}"
            seen |= span
```

**The corpus constants, MEASURED** (`find -L corpus -name '*.pdf'`, 2026-09-04) — use these, and
build them with `os.path.join(CORPUS, …)` the way `tests/etkl/test_datagrid.py:21-23` does, never as
bare relative strings:

```
corpus/ag-trade/cbh-stem-2026-08-03.pdf                 corpus/gov-stats/bfs-population-bilan-2023.pdf
corpus/ag-trade/graincorp-capacity-2026-08-04.pdf       corpus/gov-stats/ons-index-of-services-2026-02.pdf
corpus/ag-trade/graincorp-stem-2026-07-31.pdf           corpus/health/who-wfa-boys-zscore-0-5.pdf
corpus/financial/apple-fy2026q3-statements.pdf
```

`corpus_only` is **not** in `tests/etkl/fixtures.py` — it is defined in `test_datagrid.py:23` as
`pytest.mark.skipif(not os.path.exists(APPLE), …)`. Define the equivalent locally in each new test
module rather than importing across test modules.

- [ ] **Step 4: Run to verify they fail**

Run: `python3 -m pytest tests/etkl/test_band_runs.py -q -p no:randomly`
Expected: the 3 new tests fail on `AttributeError: … has no attribute 'merge_run_candidates'`; Task 1's
4 still pass.

- [ ] **Step 5: Implement `merge_run_candidates`**

Mirror `section_candidates`' procedural role (`sectiongraph.py:211-245`): build the evidence graph,
run the query, assemble the derived `(?a, ?b)` pairs into **maximal contiguous chains**. Chains, not
union-find groups — `section_candidates` unions because its pairs are *non-adjacent* repeats; these
pairs are adjacent, so the assembly is a walk. Return `(first, last)` pairs, ascending, disjoint.

- [ ] **Step 6: Run the tests**

Run: `python3 -m pytest tests/etkl/test_band_runs.py tests/test_query_terms.py tests/test_query_declarations.py -q -p no:randomly`
Expected: all green, including the 49 → 50 re-pin.

- [ ] **Step 7: Cross-check the derivation against the committed census instrument**

`scripts/band_run_census.py` holds `runs_subsumption` and `sig_set` — the plain-Python relation the
spec's § 3.3 Q3 table and three-claims § A were both measured with. Run the census and confirm the
SPARQL implementation produces the **same 14 runs on the same pages**:

Run: `PYTHONPATH=src python3 scripts/band_run_census.py`
Expected: relation-B runs matching spec § 3.3's Q3 table row-for-row.

**Fix `scripts/band_run_census.py:111` while you are here.** It hard-codes
`/Volumes/WD Green/dev/git/iladub/corpus/*/*.pdf`, which defeats the reason it was committed
(re-runnability) and fails outright in a worktree. Make it relative to the repo root. This is a
one-line change and belongs in this commit, not a separate one.

- [ ] **Step 8: FALSIFICATION**

Replace the subsumption `FILTER` in `band-run.rq` with signature **equality** (join on
`tab:ruleXsSignature`, or require the two `NOT EXISTS` legs both to hold in one direction only). Show
`test_the_relation_is_subsumption_not_equality_apple_p1` **failing** with `((2, 3),)`. Restore. Show
green. Paste both.

- [ ] **Step 9: Commit**

```bash
git add vocab/queries/band-run.rq src/iladub/etkl/sectiongraph.py \
        tests/etkl/test_band_runs.py tests/test_query_terms.py scripts/band_run_census.py
git commit -m "feat(R165): band-run.rq derives adjacent subsumption; merge_run_candidates assembles the chains"
```

---

## Task 3: `merge_bands`, promoted from the spike

**Files:**
- Modify: `src/iladub/etkl/compile.py` (new module-level function)
- Test: `tests/etkl/test_band_runs.py` (append)

**Interfaces:**
- Produces: `compile.merge_bands(bands: Sequence[Band], first: int, last: int) -> Band`.
- Consumes: `bands.Band` (8 fields, `bands.py:16-34`).

**Contract (spec § 6, and `scripts/one_band_matrix_spike.py:37-55`'s docstring, which travels with the
function):** lines in document order; `top`/`bottom` the run's extent; `rules`, `hrules`, `captions`,
`unit_markers` concatenated; **`column_xs` taken from the first band in the run that carries any —
NEVER unioned**, because `column_xs` is a boundary vector and mixing two invents boundaries no band
derived.

- [ ] **Step 1: Write the failing tests**

```python
# appended to tests/etkl/test_band_runs.py
import dataclasses


def test_merge_bands_covers_every_field_of_band():
    """A ninth Band field would be SILENTLY DEFAULTED by merge_bands, and nothing else
    in the suite would notice. Band has 8 fields (bands.py:16-34). If this fails, a
    field was added: decide how the merge carries it, then move this number."""
    from iladub.etkl.bands import Band

    assert len(dataclasses.fields(Band)) == 8, [f.name for f in dataclasses.fields(Band)]


def test_column_xs_comes_from_the_first_carrier_and_is_never_unioned():
    """The contract's load-bearing clause. column_xs is a BOUNDARY VECTOR: unioning two
    vectors invents boundaries no band derived."""
    from iladub.etkl.compile import merge_bands

    a = dataclasses.replace(_band([10.0]), column_xs=())
    b = dataclasses.replace(_band([10.0], y=20.0), column_xs=(1.0, 2.0))
    c = dataclasses.replace(_band([10.0], y=40.0), column_xs=(7.0, 8.0))
    merged = merge_bands([a, b, c], 0, 2)
    assert merged.column_xs == (1.0, 2.0), "first CARRIER, not first band, and not a union"


def test_merge_bands_takes_the_runs_extent_and_concatenates_the_rest():
    from iladub.etkl.compile import merge_bands

    a, b = _band([10.0], y=0.0), _band([20.0], y=20.0)
    merged = merge_bands([a, b], 0, 1)
    assert merged.top == min(a.top, b.top) and merged.bottom == max(a.bottom, b.bottom)
    assert merged.lines == a.lines + b.lines
    assert len(merged.rules) == len(a.rules) + len(b.rules)
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m pytest tests/etkl/test_band_runs.py -q -p no:randomly -k merge_bands or column_xs`
Expected: `ImportError` on `merge_bands` (the field-count test passes immediately — it is a pin, not a
driver, and that is intentional).

- [ ] **Step 3: Promote the function**

Move it from `scripts/one_band_matrix_spike.py:37-55` into `compile.py` **with its docstring's
contract intact**. Leave the script's copy in place and have it import from `compile` — the script is
committed evidence and its output must stay reproducible, but a second copy of the constructor is
exactly the drift `page_bands`' own docstring exists to prevent.

- [ ] **Step 4: Run the tests**

Run: `python3 -m pytest tests/etkl/test_band_runs.py tests/etkl/test_one_band_matrix_spike.py -q -p no:randomly`
Expected: green — including the spike's own test module, which now exercises the promoted function.

- [ ] **Step 5: FALSIFICATION**

Change `column_xs` to a union of every band's vector. Show
`test_column_xs_comes_from_the_first_carrier_and_is_never_unioned` **failing**. Restore. Show green.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py scripts/one_band_matrix_spike.py tests/etkl/test_band_runs.py
git commit -m "feat(R165): merge_bands promoted from the spike, contract and 8-field coverage pinned"
```

---

## Task 4: The seam — `page_bands` proposes, the membrane disposes, M1 holds

This is the task the whole loop is for. **It will turn 14 existing tests red** (spike § Q-C, measured:
14 failures in 5 files, all apple, all baseline-green). That is expected and is Task 5's subject —
**do not re-baseline anything here**, and do not "fix" a failing apple test by weakening the seam.

**Files:**
- Modify: `src/iladub/etkl/compile.py:270-323` (`page_bands`) + one new module-level function
- Test: `tests/etkl/test_run_merge_seam.py` (create)

**Interfaces:**
- Consumes: `sectiongraph.merge_run_candidates` (Task 2), `compile.merge_bands` (Task 3).
- Produces:
  - `compile.merged_run_admissible(merged: Band, first: int, last: int, page_number: int) -> bool` —
    **the whole of D2**. Offers `merged` to the identical chain at `compile.py:817-840`
    (`is_matrix_candidate → classify_matrix → assert_matrix_region → region_tiles`) on a **scratch**
    `Graph` that is discarded. **Reuse that chain; do not copy it.**
  - `compile.page_bands` — **signature unchanged**, returns the merged list.

**Why the predicate must exist as a named module-level function, and take `first`/`last`:** O5 has no
patch point otherwise. Spec § 5's prescribed technique (patch `is_matrix_candidate`/`region_tiles`) is
**REFUTED** — `classify_matrix` refuses bfs p5's `(2,5)` band *independently*, so forcing an
acceptance through those two would require fabricating a `MatrixRegion`, i.e. patching the geometry,
which O5 forbids (spike § Q-B B1). The predicate **is** the disposal taken whole, and
`monkeypatch.setattr(compile, "merged_run_admissible", fake)` reaches it because `page_bands` looks it
up as a plain module global — the same late-binding the shipped `compile.py:817` idiom already relies
on, verified reachable in B1. `first`/`last` are in the signature so O5's fake keys on the run
(`(first, last) == (2, 5)`) rather than on a line count.

**MEASURE, do not assume** (plan rule 3): `assert_matrix_region` takes a `doc` URI and a `table_uri`,
and `page_bands` knows neither. **Measure whether any of the four stages' verdicts depend on them**
before choosing what the predicate passes — run the 14 corpus runs through the predicate with the real
URIs and with a placeholder and diff the verdicts. If they differ, the predicate needs the doc URI in
its signature and this plan is wrong about it; say so in the task report.

**INVARIANT M1 (spec § 3.1), stated once:** the run partition `page_bands` applies is a pure function
of the band list built with `section_repair=False`, for every value of `section_repair_bands`. The
partition is decided on the unrepaired build; the repair flag is then applied to the constituent bands
*within* that fixed partition.

**The shape that upholds M1, and what it costs — MEASURED, not proposed** (spike § Q-A A1): keep the
`(sub, sub_rules, sub_hrules)` triple per index while building the unrepaired list, then re-call
`_build_ruled_band(..., section_repair=True)` for each **named** index and overwrite that slot. That is
**+1 `_build_ruled_band` per named band and nothing else** — 5 → 9 calls for 4 named bands on cbh p0 —
**not** a second page build; the page's `extract_words`/`extract_rules`/`extract_chars`/`detect_bands`/
`segment`/`absorb_unit_markers` machinery runs once. With `section_repair_bands=None` (26 of 27 corpus
pages) M1 costs **nothing**: the unrepaired build *is* the build.

**Order of operations in `page_bands`:** build unrepaired → `merge_run_candidates` → dispose each run
via `merged_run_admissible` → apply the repair flag to named indices → splice accepted runs, **descending
by `first`** (so earlier indices are not invalidated mid-splice).

- [ ] **Step 1: Write the failing tests**

```python
# tests/etkl/test_run_merge_seam.py
"""R165 — the seam. page_bands proposes a run; the tiling membrane disposes.

Spec: docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md § 3.0, § 3.2
"""
import os

import pytest

CORPUS = os.path.join(os.path.dirname(__file__), "..", "..", "corpus")
APPLE = os.path.join(CORPUS, "financial", "apple-fy2026q3-statements.pdf")
STEM = os.path.join(CORPUS, "ag-trade", "graincorp-stem-2026-07-31.pdf")
CAPACITY = os.path.join(CORPUS, "ag-trade", "graincorp-capacity-2026-08-04.pdf")
BFS = os.path.join(CORPUS, "gov-stats", "bfs-population-bilan-2023.pdf")
CBH = os.path.join(CORPUS, "ag-trade", "cbh-stem-2026-08-03.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(APPLE), reason="corpus not fetched")


@corpus_only
def test_apple_p0_reads_as_one_band_and_the_merge_is_what_did_it():
    """The headline. apple p0's eight bands become three; the merged band occupies
    index 2, mints #mtable2 — the IRI band 2 already mints today — and asserts 124
    entries where 48 cells are asserted at baseline. Page score 1.0.
    (spike § 2-3, § 8.4; reproduced from INSIDE page_bands in the pre-plan spike § 0.)"""
    from iladub.etkl.compile import compile_tables, page_bands

    assert len(page_bands(APPLE, 0)) == 3
    rep = compile_tables(APPLE, 0, validate_shapes=False)
    assert [r.verdict for r in rep.regions] == ["ignored", "ignored", "asserted"]
    assert rep.regions[2].cells == 124
    assert rep.regions[2].table_uri.endswith("#mtable2")
    assert rep.score == 1.0


@corpus_only
def test_apple_p1_reads_as_one_band():
    from iladub.etkl.compile import compile_tables, page_bands

    assert len(page_bands(APPLE, 1)) == 3
    rep = compile_tables(APPLE, 1, validate_shapes=False)
    assert rep.regions[2].cells == 56
    assert rep.score == 1.0


@corpus_only
def test_o2_the_fallback_is_what_saves_the_ink():
    """O2. Four documents propose a run the membrane REFUSES, and every one of them
    still asserts exactly what it asserts today. This is the test that pins § 2's D2
    and § 3.2 — and the reason the change is safe on 5 of the 7 documents.

    FALSIFIER (Step 5): make merged_run_admissible return True unconditionally. All
    four fail. graincorp-stem alone loses 586 asserted cells."""
    from iladub.etkl.compile import compile_tables

    def cells(pdf, page):
        return sum(r.cells for r in compile_tables(pdf, page, validate_shapes=False).regions)

    assert cells(STEM, 0) == 586
    assert cells(CAPACITY, 0) == 390
    assert cells(BFS, 6) == 216
    assert cells(APPLE, 2) == 3


@corpus_only
def test_a_refused_run_leaves_the_page_byte_identical():
    """§ 3.2: 'a refusal must cost nothing observable: no triple, no decision-log node,
    no report.' Serialise the whole graph of a page whose run is refused and compare it
    against the same page with the proposal suppressed. Identical.

    NOTE, and it is a real qualification the spike measured: this holds IN THE GRAPH and
    NOT ON THE CLOCK. graincorp-stem p0's refused run costs 3.06s at is_matrix_candidate
    alone (spike § Q-A A3) — see Task 7's budget."""
    import iladub.etkl.compile as compile_mod
    from iladub.etkl.compile import compile_tables

    with_proposal = compile_tables(STEM, 0, validate_shapes=False)
    real = compile_mod.merged_run_admissible
    try:
        compile_mod.merged_run_admissible = lambda merged, first, last, page_number: False
        suppressed = compile_tables(STEM, 0, validate_shapes=False)
    finally:
        compile_mod.merged_run_admissible = real
    assert (with_proposal.graph.serialize(format="nt").splitlines().sort()
            == suppressed.graph.serialize(format="nt").splitlines().sort())
    assert [r.verdict for r in with_proposal.regions] == [r.verdict for r in suppressed.regions]
    assert with_proposal.score == suppressed.score


@corpus_only
def test_m1_the_partition_does_not_depend_on_section_repair_bands():
    """INVARIANT M1 (§ 3.1). The partition is a pure function of the unrepaired build.

    THE HONEST LIMIT OF THIS TEST, which must be stated and not implied away: the only
    corpus page with a non-empty section_repair_bands is cbh p0, and cbh p0 has NO
    candidate run (spike § Q-A A4, § 'What this changes' item 7). So this pins that the
    band COUNT is stable across repair sets; it does NOT exercise 'the disposal verdict
    differs between a repaired and an unrepaired build', because no corpus page can.
    M1 is upheld by construction, not by evidence. That gap is R171."""
    from iladub.etkl.compile import page_bands

    assert len(page_bands(CBH, 0, None)) == len(
        page_bands(CBH, 0, frozenset({1, 3, 5, 7})))
    for pdf, page in [(APPLE, 0), (APPLE, 1), (STEM, 0)]:
        assert len(page_bands(pdf, page, None)) == len(
            page_bands(pdf, page, frozenset({0, 1, 2})))
```

**MEASURE before writing, do not assume** (plan rule 3): every corpus path and page number above, the
`corpus_only` import, `RegionReport`'s real field names (`verdict`? `cells`? `table_uri`?
`compile.py:326-340`), and whether `compile_tables`' report exposes `.graph`. Take them from
`tests/etkl/test_datagrid.py` and `compile.py`, not from this plan.

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m pytest tests/etkl/test_run_merge_seam.py -q -p no:randomly`
Expected: the apple tests fail (8 bands, not 3; 48 cells, not 124); `test_o2…` **passes** at baseline
(nothing merges yet, so today's ink is today's ink) — that is correct and is why its falsifier in
Step 5 is the test that actually pins it.

- [ ] **Step 3: Implement**

`merged_run_admissible` first, then the `page_bands` restructure. Extend `page_bands`' docstring's
BAND-INDEX ENUMERATION contract to say **what a band index now names — a band, or a merged run of
bands** — because three other modules are written against that docstring (spec § 6).

- [ ] **Step 4: Run the seam tests, and confirm the expected damage**

Run: `python3 -m pytest tests/etkl/test_run_merge_seam.py tests/etkl/test_band_runs.py -q -p no:randomly`
Expected: green.

Run: `python3 -m pytest tests/etkl/test_typing_equiv.py tests/etkl/test_apple_statement_headers.py \
    tests/etkl/test_decision_queries.py tests/etkl/test_decisionlog.py tests/etkl/test_datagrid.py \
    -q --tb=line -p no:randomly`
Expected: **14 failed**, matching spike § Q-C C3's table test-for-test. **If the count or the set
differs, stop and report it** — the plan's Task 5 is sized on that exact list, and a difference means
the seam is not doing what the prototype did.

- [ ] **Step 5: FALSIFICATION (two, because two things are pinned)**

1. Make `merged_run_admissible` return `True` unconditionally. Show `test_o2_the_fallback_is_what_saves_the_ink`
   **failing** on all four documents. Restore. Show green.
2. Decide the partition on the **repaired** build (move the `merge_run_candidates` call after the
   repair rebuild). Show `test_m1_the_partition_does_not_depend_on_section_repair_bands` **failing**.
   Restore. Show green.

**If (2) does not fail** — i.e. the corpus cannot tell the two orderings apart — say so plainly in the
task report. That is a real finding about the test, not a pass: it means M1 is pinned by construction
only, exactly as the test's own docstring says, and `R171` is the row that carries it.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/compile.py tests/etkl/test_run_merge_seam.py
git commit -m "feat(R165): page_bands proposes the run, the tiling membrane disposes — M1 upheld on the unrepaired build"
```

---

## Task 5: Re-baseline the 14 measured failures, and rule on the fixture-drift guard

**Files (measured, not read — spike § Q-C C2/C3):**
- Modify: `tests/etkl/test_apple_statement_headers.py` (2), `tests/etkl/test_datagrid.py` (2),
  `tests/etkl/test_decision_queries.py` (4), `tests/etkl/test_decisionlog.py` (4),
  `tests/etkl/test_typing_equiv.py` (2)
- Modify: `tests/corpus-manifest.ttl` (append after `:118`)

**`tests/etkl/test_supersession_queries.py` is NOT in this set.** Spike § 8.5(d) predicted it and the
prediction is **REFUTED** — 5 passed under the prototype, because its band indices are cbh's and cbh
p0's partition is untouched. **Do not budget a re-baseline for it.** Likewise, 22 of the 27
index-referencing modules are untouched, `test_document.py` and `test_section_repair.py` among them.

**The rule for every re-baseline in this task:** a moved number is only allowed to move if the task
report says **what the new number means**. `assert 56 == 14` is not "the fixture moved"; it is
"apple p1's entry count is 56 because bands 2..7 are one table". Nine of the fourteen are
consequences of a band index no longer existing (bands 3 and 4 of apple p0 are *inside* the merged
band) — for those, the honest repair is usually to **retarget the test at the merged band**, not to
delete the assertion.

- [ ] **Step 1: Re-baseline the 12 index/count failures**

Work through spike § Q-C C3's table rows 1, 2, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14. Row 13
(`EXPECTED_VERDICTS["apple"]`, `test_typing_equiv.py:70-79`) goes from an 8-entry positional list to a
**3**-entry list; its `stem`, `cbh` and `capacity` lists are **unchanged** (spike § Q-D D4, measured).

- [ ] **Step 2: Rule on row 11 — `test_decisionlog.py:340`**

`test_region_tiles_rationale_names_the_real_unit` fails with *"the apple corpus doc's page 0 does not
exercise the assert_hier_region (body-token) region_tiles path — cannot assert the unit fix on this
fixture"*. This is **not** an index pin and **not** a moved number: the merged reading never takes the
hier path, so the test's fixture no longer exercises what it was written to exercise. **It needs a new
fixture or an explicit deletion with a recorded reason — not a re-baseline.** Find a corpus page that
still takes the `assert_hier_region` path and retarget it; if none does, say so and record it as a
residue rather than deleting the coverage silently.

- [ ] **Step 3: Rule on row 3 — `test_datagrid.py:907`, the fixture-drift guard**

`test_fallback_never_masks_an_escalation` fails at its own precondition — `assert 0 > 0`, *"fixture
drift: this page is supposed to escalate"*. **This is the one failure that is not a re-baseline**, and
it needs a deliberate ruling (spike § Q-C C4).

**What is measured and settled** (three-claims § B): the ink is fully accounted for. apple p1's 70
baseline-escalated tokens become 42 asserted + 0 escalated + 28 counted-nowhere, and the 28 are
*exactly* the stub column that the matrix-asserted branch has always excluded
(`compile.py:843-851`) — verified as a set. The merge swallows nothing.

**What is NOT settled, and is this task's decision** (three-claims § B.1 item 1): apple p1 stops
escalating, so `:908` (`on.score == off.score`) and `:909` (`len(on.regions) == len(off.regions)`)
become **vacuous** there and the guard stops guarding. A replacement fixture must exercise the gate
**for the reason the guard names** — the gate is `asserted_total == 0 and escalated_total == 0`
(`compile.py:1040`), and a page that also asserts something declines on the *first* clause, so the
escalation clause is never reached.

**THE RULING — `apple p2` is REFUTED as the replacement, and four real witnesses exist.**

`docs/superpowers/2026-09-04-r165-three-claims-handoff.md` § 5 graded *"apple page 2 is the right
replacement fixture"* **PROPOSED** and ordered it run before this task was written. It was run
(2026-09-04, this plan's session) over all 27 pages of all 7 documents, at baseline and under the
prototype, 0 pages raised. **The instrument is committed at `scripts/page_ink_census.py`** so the
table below is re-runnable rather than pasted — `PYTHONPATH=src python3 scripts/page_ink_census.py`,
verified reproducing on the clean main tree:

```
apple p1 BASELINE: asserted=14  escalated=70   score=0.16667   ← the current fixture
apple p2 BASELINE: asserted=3   escalated=108  score=0.02703   ← the PROPOSED replacement
```

**Both decline on the ASSERTED clause.** `asserted_total == 0` is False on each, so `and`
short-circuits and `escalated_total == 0` is never the operative reason. apple p2 is therefore no
better than apple p1 — and the sharper finding is about apple p1: **the guard has not isolated the
escalation clause for some time already.** It asserts 14 at baseline. The test's name has been
ahead of what it checks since the reading on that page started asserting anything at all; the merge
exposes that, it does not cause it.

**Four corpus pages DO isolate the clause** (`asserted == 0 and escalated > 0`), and — measured under
the prototype as well — **all four are completely unchanged by the merge**, so any of them is a stable
witness rather than another fixture that drifts on the next reading improvement:

```
ag-trade/graincorp-stem-2026-07-31.pdf   p1   asserted=0  escalated=850
ag-trade/graincorp-stem-2026-07-31.pdf   p2   asserted=0  escalated=766
gov-stats/bfs-population-bilan-2023.pdf  p0   asserted=0  escalated=6
gov-stats/bfs-population-bilan-2023.pdf  p4   asserted=0  escalated=36
```

**Take `graincorp-stem p1`** — the largest escalation on the corpus (850 tokens), so a fallback that
fired there would be unmissable. Retarget the test at it, and **replace the precondition**: assert
`off.asserted == 0 and off.escalated > 0`, which is what makes the escalation clause the operative
one, instead of `off.escalated > 0`, which does not. Say in the docstring **why both clauses are
asserted** — that is the whole content of the repair.

**Two things the task report must also say.** (1) The corpus's 11 pages where the fallback actually
FIRES (`asserted == 0 and escalated == 0`) are 3 bfs pages and 8 ons pages, also unchanged by the
merge — so `test_fallback_fires_only_where_the_page_produced_nothing_at_all` (ons p7) is untouched
and needs nothing. (2) apple p1 loses its role here entirely; **do not leave a weakened version of the
old test behind beside the new one.**

- [ ] **Step 4: Append the manifest note (Doc impact: increment)**

`tests/corpus-manifest.ttl:105-118` is apple's entry; `:118` is the 2026-09-02 `cor:adjudication` node
whose rationale pins `0.18950437317784258`. The register is **append-only**: add a **third**
`cor:adjudication` node recording the new document score and its cause. **Repair nothing in place** —
the 2026-09-02 note itself models this, superseding the 2026-08-20 framing while leaving its
measurements standing (spike § Q-D D6).

**MEASURE the new score, do not carry `0.6289` forward from the spike.** That figure was measured with
`validate_shapes=False` on a prototype whose relation was plain Python. Run `compile_document` on the
shipped tree and record what it actually returns.

- [ ] **Step 5: Run the five files plus the manifest gate**

Run:
```
python3 -m pytest tests/etkl/test_typing_equiv.py tests/etkl/test_apple_statement_headers.py \
    tests/etkl/test_decision_queries.py tests/etkl/test_decisionlog.py tests/etkl/test_datagrid.py \
    tests/test_corpus_manifest.py -q -p no:randomly
```
Expected: green. (Baseline control for this set is **88 passed, 2 skipped in 264 s** — spike § Q-C C2.)

- [ ] **Step 6: FALSIFICATION**

For the re-baselined `EXPECTED_VERDICTS["apple"]`: revert `page_bands` to return the unmerged list
(comment out the splice). Show `test_band_verdicts_are_recorded_and_stable[apple]` **failing** with an
8-entry list against the new 3-entry expectation. Restore. Show green. This proves the new baseline
pins the merged partition and not merely "whatever the code does".

- [ ] **Step 7: Commit**

```bash
git add tests/etkl/ tests/corpus-manifest.ttl
git commit -m "test(R165): re-baseline the 14 measured apple failures; rule on the datagrid fixture-drift guard"
```

---

## Task 6: The three remaining oracles — O3, O4, O5

**Files:**
- Test: `tests/etkl/test_run_merge_seam.py` (append)

- [ ] **Step 1: Write O3 — corpus-wide, per page, a merge never loses asserted ink**

```python
# appended to tests/etkl/test_run_merge_seam.py

# The pre-merge baseline, per (document, page). MEASURED 2026-09-04 on the CLEAN tree
# (not on the prototype) by scripts/page_ink_census.py — all 27 pages of all 7 documents,
# validate_shapes=False, datagrid_fallback=False, 27 compiled, 0 raised.
# RE-RUN IT rather than trusting this table if main has moved:
#     PYTHONPATH=src python3 scripts/page_ink_census.py
BASELINE_ASSERTED = {
    ("cbh-stem-2026-08-03", 0): 51,
    ("graincorp-capacity-2026-08-04", 0): 390,
    ("graincorp-stem-2026-07-31", 0): 586,
    ("graincorp-stem-2026-07-31", 1): 0,
    ("graincorp-stem-2026-07-31", 2): 0,
    ("apple-fy2026q3-statements", 0): 48,
    ("apple-fy2026q3-statements", 1): 14,
    ("apple-fy2026q3-statements", 2): 3,
    ("bfs-population-bilan-2023", 0): 0,
    ("bfs-population-bilan-2023", 1): 0,
    ("bfs-population-bilan-2023", 2): 0,
    ("bfs-population-bilan-2023", 3): 0,
    ("bfs-population-bilan-2023", 4): 0,
    ("bfs-population-bilan-2023", 5): 7,
    ("bfs-population-bilan-2023", 6): 222,
    ("ons-index-of-services-2026-02", 0): 0,
    ("ons-index-of-services-2026-02", 1): 0,
    ("ons-index-of-services-2026-02", 2): 0,
    ("ons-index-of-services-2026-02", 3): 0,
    ("ons-index-of-services-2026-02", 4): 19,
    ("ons-index-of-services-2026-02", 5): 0,
    ("ons-index-of-services-2026-02", 6): 0,
    ("ons-index-of-services-2026-02", 7): 0,
    ("ons-index-of-services-2026-02", 8): 0,
    ("who-wfa-boys-zscore-0-5", 0): 268,
    ("who-wfa-boys-zscore-0-5", 1): 257,
    ("who-wfa-boys-zscore-0-5", 2): 129,
}


@corpus_only
def test_o3_no_page_loses_asserted_ink_to_a_merge():
    """O3, and the STANDING DETECTOR for R170 (is_matrix_candidate is the sole guard on
    976 asserted cells it was never specified to guard).

    This is deliberately corpus-WIDE rather than a runtime guard. § 3.3 explains why a
    runtime guard is not implementable where the decision lives: page_bands decides the
    partition BEFORE anything is compiled, so it cannot know what the constituent bands
    would have asserted without compiling both readings. So the hazard is made
    FALSIFIABLE rather than guarded — and this generalises to any document later added
    to the corpus, which a guard tuned to today's evidence would not."""
    from iladub.etkl.compile import compile_tables

    for (stem, page), baseline in sorted(BASELINE_ASSERTED.items()):
        rep = compile_tables(_pdf_for(stem), page, validate_shapes=False,
                             datagrid_fallback=False)
        assert rep.asserted >= baseline, f"{stem} p{page}: {rep.asserted} < {baseline}"
```

Only **two** entries in that table may move at all, and both must move UP: apple p0 48 → 124 and
apple p1 14 → 56. Every other page was measured **byte-identical between the clean tree and the
prototype** — the merge touches nothing else on this corpus. **Assert that too**, as an equality on
the other 25: `>=` alone would not catch a page that silently gained ink for the wrong reason.

**MEASURE, do not assume** (plan rule 3): whether `sum(r.tokens_asserted for r in rep.regions)`
equals `rep.asserted` — the table above is the **page-level** counter, and spec § 5's O3 is written
in terms of `RegionReport.tokens_asserted`. If they agree, prefer `rep.asserted`; if they do not,
**that discrepancy is a finding**, and O3 must use the per-region field the spec names.

**And measure WHERE `RegionReport.tokens_*` are written before you call anything that reads them.**
A field populated after the report is built reads as zero, and the reader fails **upward** —
invisibly. This is defect 2 of CLAUDE.md § Plan authoring discipline (*"`build_ledger` called before
the only site that ever writes `RegionReport.tokens_*`"*), and it is the same field.

- [ ] **Step 2: Write O4 — the index space is single and consistent**

**O4's `tab:bandIndex` clause as the spec states it is UNSATISFIABLE and must be substituted.**
`tab:bandIndex` never appears in the compile graph — it is emitted at exactly one site
(`sectiongraph.py:205`) into the transient section-recognition graph, which is discarded (spike § Q-B
B2, § Q-D D3, independently measured twice). The satisfiable form carrying the same force, which the
spike **measured**: every minted `#regionN` / `#tableN` / `#mtableN` / `#ttableN` / `#htableN` fragment
index is `< len(report.regions)` and names the report position it describes. This is a spec defect
found by measuring the test's setup (plan rule 5), not a weakening.

```python
@corpus_only
def test_o4_every_minted_fragment_index_names_its_report_position():
    """O4, substituted (spike § Q-B B2). On apple p0/p1 page_bands returns 3 bands, the
    merged band occupies index 2 and mints #mtable2 — the IRI band 2 already mints
    today — and every minted fragment index is < len(regions) and matches its position."""
    import re
    from iladub.etkl.compile import compile_tables

    for page in (0, 1):
        rep = compile_tables(APPLE, page, validate_shapes=False)
        assert len(rep.regions) == 3
        minted = {(m.group(1), int(m.group(2)))
                  for m in re.finditer(r"#(m?t?h?table|region)(\d+)",
                                       rep.graph.serialize(format="nt"))}
        assert minted, "no fragment was minted at all — the regex is wrong, not the code"
        for _kind, idx in minted:
            assert idx < len(rep.regions), (page, _kind, idx)
        assert ("mtable", 2) in minted
```

**MEASURE, do not assume:** the real fragment vocabulary and the regex that matches it. Spike § Q-B B2
observed `htable`, `ttable`, `region` and `mtable`; derive the pattern from
`src/iladub/etkl/decisionlog.py:102-110` and `compile.py`'s `URIRef(f"{doc}#…")` sites rather than from
this plan's regex, which is a placeholder for a shape.

- [ ] **Step 3: Write O5 — the forced NON-TAIL merge**

No corpus document exhibits a non-tail accepted merge (spec § 1.3: every accepted run on this corpus
is a page **tail**, so indices are only removed, never shifted). The repo ships **no** synthetic-PDF
capability (`find tests -name '*.pdf'` → nothing; no reportlab/fpdf dependency), so inventing one is a
dependency decision this loop does not make. Force it on a real page instead, **by patching the
disposal, never the geometry**.

```python
@corpus_only
def test_o5_a_forced_non_tail_merge_renumbers_consistently(monkeypatch):
    """O5. bfs p5 has 15 bands and produces runs (2,5) and (7,8) — both NON-TAIL, both
    refused today. Force (2,5) through by patching the ADMISSIBILITY PREDICATE, which is
    the disposal taken whole, not one of its four stages.

    Why not the spec's prescribed patch point: classify_matrix refuses this band
    INDEPENDENTLY of is_matrix_candidate, so patching those two cannot force an
    acceptance, and patching classify_matrix would mean fabricating a MatrixRegion —
    patching the geometry, which O5 forbids (spike § Q-B B1)."""
    import re
    import iladub.etkl.compile as compile_mod
    from iladub.etkl.compile import compile_tables, page_bands

    monkeypatch.setattr(
        compile_mod, "merged_run_admissible",
        lambda merged, first, last, page_number: (first, last) == (2, 5))

    bands = page_bands(BFS, 5)
    assert len(bands) == 12, "the run 2..5 — four bands — must become one"

    rep = compile_tables(BFS, 5, validate_shapes=False)
    assert len(rep.regions) == 12
    minted = {int(m.group(2)) for m in re.finditer(r"#(m?t?h?table|region)(\d+)",
                                                   rep.graph.serialize(format="nt"))}
    assert minted == set(range(12)) or minted <= set(range(12))
    assert max(minted) < 12, "a fragment index >= the band count means two index spaces"


@corpus_only
def test_o5_document_scope_completes_with_a_forced_non_tail_merge(monkeypatch):
    """The second half of O5: a document-scope compile over bfs completes, and adoption's
    grid_idx equals the page's band count on the merged page.

    THE LIMIT, stated because the spike measured it and the plan must not imply coverage
    it does not have: adoption's re-compile fires only on bfs p0 and p4 and is REFUSED on
    both, so ADOPTION'S BRANCH IS NEVER ENTERED on the merged page. This verifies an
    equality of counts, NOT a successful trip through document.py:1657-1740. No corpus
    document both merges and adopts. That gap is R171."""
    import iladub.etkl.compile as compile_mod
    from iladub.etkl.compile import page_bands
    from iladub.etkl.document import compile_document

    monkeypatch.setattr(
        compile_mod, "merged_run_admissible",
        lambda merged, first, last, page_number: (first, last) == (2, 5))

    doc = compile_document(BFS, validate_shapes=False)
    assert len(doc.pages[5].regions) == 12 == len(page_bands(BFS, 5))
```

**MEASURE, do not assume:** `compile_document`'s real return shape and how a page's regions are
reached (`doc.pages[5].regions` is read from spike § Q-B B3's output, not from the source), and
whether `document.py` looks `merged_run_admissible` up through `compile_mod` or re-imports it — if the
patch does not reach the document path, **the predicate's lookup is not late-bound there and that is a
finding**, not a reason to patch something else.

- [ ] **Step 4: Run**

Run: `python3 -m pytest tests/etkl/test_run_merge_seam.py -q -p no:randomly`
Expected: green. Spike § Q-B B3 measured the document-scope compile at **23.0 s**; if this test takes
dramatically longer, that is Task 7's subject, not a failure.

- [ ] **Step 5: FALSIFICATION**

Merge into a copy of the band list that **preserves the original indices** (splice the merged band in
without removing the bands it absorbs, or pad the list back to its original length). Show
`test_o5_a_forced_non_tail_merge_renumbers_consistently` **failing** on the band count or the gap
check. Restore. Show green.

- [ ] **Step 6: Commit**

```bash
git add tests/etkl/test_run_merge_seam.py
git commit -m "test(R165): O3 corpus no-regression, O4 fragment/position (substituted), O5 the forced non-tail merge"
```

---

## Task 7: The budget, the register, the wiki, and the whole suite

**Files:**
- Modify: `docs/superpowers/residues.md`, `docs/superpowers/residues-open.md`
- Modify: `docs/wiki/concepts/neurosymbolic-exemplars.md`
- Create: `docs/superpowers/2026-09-04-the-run-is-one-band-evidence.md`

- [ ] **Step 1: Measure the wall-clock, before and after (spec § 3.5)**

`scripts/doc_walltime.py` is the committed instrument. Run it once per tree (baseline commit and
HEAD) and diff. **Read the call counts before the seconds** — its docstring records why, and § C of
the three-claims doc names the noise it exposed (one document came back 19% *faster* under a change
that proposes no run on any of its pages).

What is already measured and must be reported alongside, not re-derived:

- +27.8 s of `page_bands` on a 312 s corpus compile (~9%) — **affordable** (three-claims § C).
- **A refusal is not free on the clock.** graincorp-stem p0's refused run costs **3.06 s** at
  `is_matrix_candidate` alone, graincorp-capacity p0 **1.70 s** — and `page_bands` is called ≥2× per
  page per document compile with **no caching anywhere** (`grep -rn lru_cache src/iladub/etkl/*.py`
  → no output). The corpus's two most expensive disposals are the two that are **refused**
  (spike § Q-A A3).
- **Do not build a cache in this loop.** A perfect `(pdf, page, srb)` cache returns **41.54 s** —
  more than this change costs — and that win **predates this loop** and is not caused by it. It is
  `R172` (three-claims § C). Bundling it would make this diff answer two questions at once.

**The decision this step must record:** whether the measured after-figure is acceptable as shipped. If
it is not, the remedy is `R172`, raised and deferred — **not** a cache added here.

- [ ] **Step 2: Raise the three register rows**

Spec § 7 numbers them R168/R169/R170. **That numbering is superseded**: the predecessor loop took
`R168` and `R169`. The rows this plan raises are **`R170`**, **`R171`**, **`R172`**, and the register's
snapshot convention puts the tally at the moment each is raised in parentheses. Measured at the head of
this branch:

```
$ awk -F'|' '/^\| ~?~?R[0-9]/{t++; if ($3 ~ /closed/) c++} END{print c"/"t" closed"}' \
      docs/superpowers/residues.md
43/159 closed
```

so: **`R170 (43/159 closed)`**, **`R171 (43/160 closed)`**, **`R172 (43/161 closed)`**. **Re-run that
command before writing the rows** — if another loop has landed on `main` in the meantime, the tally and
possibly the numbers have moved.

| row | subject |
| --- | --- |
| **R170** | *`is_matrix_candidate` is the sole guard on 976 asserted cells it was never specified to guard.* graincorp-capacity p0 `1..3` (390 cells) and graincorp-stem p0 `1..2` (586) become proposed runs joining a **title** band to the page's main table on a strict-subset signature; only the refusal keeps them. Deferred because the runtime guard is not implementable where the decision lives (spec § 3.3). **O3 is its standing detector.** Sharpened by spike § Q-A A3: the guard is also the most expensive call in the design. |
| **R171** | *Two things the corpus cannot exercise, and they are wider than the spec's R169 states.* (a) The **non-tail accepted merge** — O5 forces it by patching the disposal, which is not a document that exhibits the case. (b) **M1's load-bearing half**: the only page with a non-empty `section_repair_bands` (cbh p0) has no candidate run, so "the disposal verdict differs between a repaired and an unrepaired build" is never tested — M1 is upheld by construction, not by evidence. (c) **Adoption's branch is never entered on a merged page** — `grid_idx == band count` is an equality of counts, not a trip through `document.py:1657-1740`. Closed by a corpus document that merges and adopts, or that accepts a non-tail run. |
| **R172** | *`page_bands` has no cache, and the cache is worth more than this change costs.* ≥2 calls per page per document compile, no memoisation anywhere; a perfect `(pdf, page, srb)` cache returns 41.54 s against this change's +27.8 s. **Not caused by this loop**; deliberately not bundled. Closed by a memoisation whose key is proven sound across the repair passes. |

**Also record, in `residues-open.md` and not only here:** `R170` (entry-vs-cell counters) from spec § 7
— *"124 entries vs 48 cells today" compares `assert_matrix_region`'s return against
`RegionReport.cells`; no content diff has ever been run.* **Reconcile this against the three rows
above before writing**: spec § 7 lists **three** rows and this plan lists three, but they are not the
same three — the spec's R170 (entry-vs-cell) is not in the table above. **Decide whether it is a
fourth row (`R173`) or subsumed by O3's token ledger, and say which.** O3 bounds the ink but does not
identify the cells, which argues it is a fourth row.

- [ ] **Step 3: Update `R165`, `R160`, `R166`, `R167`**

- **`R165`** — strike the number (`~~R165~~`) and record the closure evidence in place: the score
  movement, the two accepted runs, the oracle set. **Do not delete the row** (CLAUDE.md § Deferred
  residues).
- **`R160` is NOT ruled by this loop** (spec § 4 item 3). The one-band reading makes adoption
  *unnecessary* on p0/p1 (`adopted=()` in both baseline and merged runs) rather than restoring it.
  **If the implementation makes the row moot, say so in the evidence and leave the row open.** Do not
  rule the reader-authority question in passing.
- **`R166` is not closed by fiat** (spec § 4 item 4). Its p0 half is *disposed of* by the merged
  reading (band 4's `Operating income 35,695 …` becomes a leaf row); its p2 half survives. Narrow the
  subject; leave the row open. Note that three-claims § B.1 item 3 found **one new mis-label of the
  same family** on apple p1 — a three-line wrapped stub yielding a `HeaderNode` labelled
  `respectively` (the last wrap line, not the first). All its ink is present as `LabelCell`s; only the
  chosen label is wrong. **Add it to R166's subject.**
- **`R167`** (the em-dash in `celltype.is_blank`) is untouched — spec § 4 item 2.

- [ ] **Step 4: The wiki exemplar (Doc impact: increment)**

Add one AXIOM derivation to `docs/wiki/concepts/neurosymbolic-exemplars.md`, following that file's
existing entry shape. It must carry the § 2 argument that makes this an AXIOM and not a NEURAL
violation — **the judgement §8 sends to NEURAL is the one that DISPOSES; D1 enumerates candidates and
settles nothing** — and name the file paths (`vocab/queries/band-run.rq`,
`sectiongraph.run_evidence`/`merge_run_candidates`, `compile.merged_run_admissible`). A wiki page is a
**proposition**: confidence-tagged, citing its sources.

- [ ] **Step 5: Write the loop's evidence document**

`docs/superpowers/2026-09-04-the-run-is-one-band-evidence.md`. It records what was **measured on the
shipped tree**, and must distinguish those figures from the prototype's everywhere it cites one.
Three things it must state explicitly, because they are the loop's honest limits:

1. **Every figure in the spec and both spike documents is the PROTOTYPE's**, whose relation is plain
   Python. The SPARQL form was shown to derive the same 14 runs (three-claims § A); nothing showed a
   *shipped* implementation behaves like the prototype. **This document is the first place that is
   shown.**
2. **The document score under the membrane.** No document score has ever been measured with
   `validate_shapes=True` — *the membrane has never seen a merged band* (spec § 8, three-claims § 4).
   Measure it here and report both.
3. **The apple p1 signal loss** (three-claims § B.1 item 2): apple p1's page score becomes **1.0**
   while 63 of its 119 band words are counted on neither side of the ratio. The exclusion is
   pre-existing convention (`compile.py:843-851`), not something the merge introduces — but 1.0 is the
   ceiling, so **no future regression on that page can ever be detected by its score again.** That is
   a real loss of signal and it belongs in the record.

- [ ] **Step 6: Run the FULL suite, in-band**

Run: `python3 -m pytest -q -p no:randomly`
Expected: green. **~45 minutes. Do not run this in a background subagent** (Global Constraint 6).
Paste the summary line in the task report — a claim of green without the output is not evidence
(superpowers:verification-before-completion).

- [ ] **Step 7: Commit and open the PR**

```bash
git add docs/superpowers/ docs/wiki/concepts/neurosymbolic-exemplars.md
git commit -m "docs(R165): the run is one band — evidence, R170/R171/R172, R165 struck"
git push -u origin the-run-is-one-band
gh pr create --title "R165: the run is one band — the merge is a proposal, the tiling membrane disposes" --body "..."
```

The required check is **`test`**, the JOB name in `.github/workflows/ci.yml`. `gh pr merge --auto`
now means what it says (CLAUDE.md § Branch protection).

---

## Self-review against the spec

**Spec coverage.** § 3.0 the seam → Task 4. § 3.1 M1 → Task 4 (invariant + test + falsification).
§ 3.2 the fallback → Task 4 (`merged_run_admissible`, byte-identical test); its overlap clause →
DECISION D + Task 2 test 3. § 3.3 the relation → Task 2. § 3.4 the derivation → Tasks 1–2 (with
DECISION A/B/C carrying the three measured refutations). § 3.5 the budget → Task 7 Step 1. § 4's six
non-goals → carried in Task 7 Step 3 (`R160`, `R166`, `R167`) and Global Constraint 2. § 5's oracles:
O1 → Task 2, O2 → Task 4, O3/O4/O5 → Task 6 (O4 and O5 **substituted**, per the measured refutations,
with the substitution and its evidence stated at the test). § 6's interfaces → Tasks 1–4, with
`tab:ruleX` **replaced** by `tab:bandRuleX` (DECISION A) and `run_evidence`'s parameter shape decided.
§ 7's residues → Task 7 Step 2, **renumbered** and with the spec's entry-vs-cell row flagged for
reconciliation.

**Known gaps, stated rather than closed:**

- **Task 5 Step 3's measurement was RUN in this session and the handoff's PROPOSED fixture is
  REFUTED** — apple p2 declines on the asserted clause exactly as apple p1 does. The step is unblocked
  and names `graincorp-stem p1` instead, with the four-witness census behind it. The raw census
  (baseline and prototype, 27 pages, 0 raised) belongs in Task 7 Step 5's evidence document.
- **Task 7 Step 2's fourth-row question is left open deliberately.** The spec lists three residues and
  this plan lists three, and they are not the same three; the reconciliation is a judgement the
  implementer makes with the O3 ledger in front of them, which is a better place to make it than here.
- **No task exercises the membrane on a merged band under `validate_shapes=True`** beyond Task 7's
  full-suite run and its evidence measurement. If the membrane refuses a merged band, that is a
  finding large enough to stop the loop, and it will surface in Task 7 Step 6 — **late**. An
  implementer who wants it earlier should run
  `compile_tables(APPLE, 0, validate_shapes=True)` at the end of Task 4 and report it.
