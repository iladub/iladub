# The ignored band carries its text — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Serves:** prog:criterion:etkl:02 — R212 is a **prerequisite** of that criterion's measures, ruled
2026-09-12; it is not a criterion of its own. R212 is named by no `prog:blockedBy` in
`tests/arc-manifest.ttl` (measured: `grep -rn "R212" tests/arc-manifest.ttl` → no match), so closing
it moves the register and not the arc.

**Goal:** every band the reader ignored puts its exact surface text, its page and its band index into
the compiled graph, as a committed fact in the `etkl` namespace with provenance to the page — and no
number that grades a document moves.

**Architecture:** one emitter in the NON_TABLE branch of `compile_tables`, writing a node per ignored
band off the page-scoped document IRI. No counter is touched, no `RegionReport` field changes, no
membrane set is edited. The vocabulary is `etkl:`; its NodeShape lives in `vocab/shapes/etkl-shapes.ttl`
and is run against real compiled graphs by a test rather than wired into the compile membrane
(DECISION D).

**Tech Stack:** Python 3, rdflib, pySHACL, pytest, reportlab (synthetic fixture). RDF Turtle for the
vocabulary.

**Spec:** `docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md` — § 3 the
reading and the three refusals, § 4 what this loop does NOT do, § 5 the oracle. **The spec's design
is unchanged and is not re-opened here.** Two 2026-09-12 maintainer rulings are settled input, not
questions: *all* ignored bands are carried, and the term lives in **`etkl:`** (spec § 0).

**Evidence this plan is built on** — read these before a task, in this order:

| doc | what it settles |
| --- | --- |
| `docs/superpowers/2026-09-12-r212-invariant-arm-evidence.md` § 1 | the invariant is CONFIRMED on all 7 corpus documents, not predicted |
| that evidence § 2 | `document.licence_evidence` is REFUTED as the producer, on four independent legs |
| that evidence § 3 | spec § 5 arm 1 is **not constructible as worded**; the `reportlab` route is, and is the RED state |
| that evidence § 4 | `_band_text`'s cycle-free home is `bands.py` |
| that evidence § 5 | the compile membrane loads neither `etkl` shapes nor `etkl` ontologies |
| `docs/superpowers/2026-09-12-the-invariant-holds-handoff.md` § 5a | the four corrections a plan must take from evidence rather than from the spec |

**Doc impact: increment.** Three new `etkl:` terms are declared in `vocab/ontology/etkl.ttl` and one
NodeShape in `vocab/shapes/etkl-shapes.ttl` (both CC-BY, published artifacts);
`docs/wiki/concepts/neurosymbolic-exemplars.md` gains one PROCEDURAL entry. No released assertion is
contradicted, so **nothing blocks a release tag**.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **The neurosymbolic gate (CLAUDE.md §8) — PROCEDURAL, and the justification is the spec's, stated
   once in spec § 3's `§8 gate` paragraph.** Cite it; do not re-derive it. Every value the emitter
   writes is passed in or derived mechanically (text by concatenation, page off `Word.page`, index
   off the loop). **The carrier decides nothing**: which bands are ignored was decided upstream by
   the existing AXIOM (`classify`), and *choosing* which ignored bands deserve carriage would be
   NEURAL — which is exactly why it does not choose. **A threshold, a tolerance, or any rule
   selecting among ignored bands anywhere in the shipped diff is a review failure.**
2. **Source ownership (CLAUDE.md § Source ownership).** Every new term is `etkl:` =
   `https://w3id.org/iladub/etkl#`. `vocab/ontology/etkl.ttl` stays **standalone** — no
   `w3id.org/holon` IRI enters it, and no HGA term is ever a subject
   (`tests/test_source_ownership.py` is CI-enforced).
3. **The figure gate binds the code and the wiki, and not this plan.** `vocab/queries/docgov-undated-figure.rq`
   exempts `docs/superpowers/**` (`FILTER (?class != "evidence")`), so figures here need no date. It
   does **not** exempt `src/**` or `docs/wiki/**`. MEASURED in `tests/docgov_extract.py:188-193`:
   the gate matches a **decimal** literal (`\d+\.\d+`), never a bare integer, and a block is dated by
   an ISO date **or** a backticked commit sha anywhere in the same run of non-blank lines
   (`is_dated`, `:218-219`). So a new comment saying *146 ignored bands* fires nothing, and one
   quoting a score like `0.6289` must carry a date in its own block.
4. **Plan rules 1–7 (CLAUDE.md § Plan authoring discipline).** No function body appears in this plan.
   Test assertions are supplied as **contracts and exact assertions, not as transcribed fixtures**:
   where this plan names a measured shape (the reportlab page's three bands) it names the measurement
   it came from, and the coordinates are the implementer's to write, because this plan's author did
   not run them. **A supplied assertion is a proposition** — one that cannot be made to pass has
   found a plan or spec defect; say so in the task report and substitute the satisfiable form
   carrying the same force, never a weaker one. **Every task ships a `## FALSIFICATION` block**
   (rule 4); no falsification evidence ⇒ the task review fails.
5. **`corpus/` is gitignored** (`.gitignore:52`). A fresh worktree has no corpus and every
   corpus-gated test skips **green**. Symlink first — `ln -s "/Volumes/WD Green/dev/git/iladub/corpus" corpus`
   — and verify `ls corpus/ag-trade` lists the graincorp PDFs. **A green CI is not evidence for the
   corpus arm** (spec § 5 arm 5).
6. **macOS has no `timeout`** and `pytest --timeout` is not installed: wrapping a run in either runs
   nothing and exits 0. Read the output, never the exit code.
7. **The full suite takes ~45–60 minutes and must NOT be run in a background subagent.** Run it
   in-band, once, at Task 5.
8. **Branch protection.** Branch first; `main` is reachable only through a PR whose `test` check is
   green. Branch `r212-carry-the-ignored-band`, cut from `main` at `353eadc`.

---

## The invariant, stated ONCE (plan rule 6)

> **Carriage changes what is in the graph and changes no number that grades a document.**

It is **CONFIRMED, not predicted** — evidence § 1, all 7 corpus documents, score and per-page
`(asserted, escalated)` ledger and every per-region verdict byte-identical, all 7 canonical graph
hashes moved. Its mechanism is measured: the score is `asserted / (asserted + escalated)`
(`document.py:1760`), `escalated_total` is incremented by the *caller* of `escalate_region`
(`compile.py:802-803`), and the NON_TABLE branch increments neither (`compile.py:814-824`).

Every task below cites this line. **No task re-derives it**, and Task 4 re-runs it on the shipped
emitter rather than the throwaway.

---

## The five decisions this plan takes, that the spec and the evidence left open

Stated once here; **cited** from the tasks.

### DECISION A — the node is `etkl:IgnoredBand`, and its text is `etkl:bandText`

Three terms in `vocab/ontology/etkl.ttl`:

- **`etkl:IgnoredBand`** (`owl:Class`) — a band of a source document that the region reader
  classified `NON_TABLE` and therefore read nothing from. The class is named for **the verdict**,
  because that is the whole reason the node exists: a band's text is carried *because* the reader
  ignored it, not because anything read it (spec § 3).
- **`etkl:bandText`** (`owl:DatatypeProperty`, `rdfs:domain etkl:IgnoredBand`, `rdfs:range
  xsd:string`) — the band's exact surface text, its lines in reading order. Its comment must carry
  the raw-extraction stance `_band_text`'s docstring already argues (`document.py:541-547`): no
  normalisation, no case folding, no stripping.
- **`etkl:bandIndex`** (`owl:DatatypeProperty`, `rdfs:domain etkl:IgnoredBand`, `rdfs:range
  xsd:integer`) — the band's position in `page_bands`' returned list, which is the **same index
  space** as `compile_tables`' `for idx, band in enumerate(bands)` loop (`compile.py:788`) and as
  `section_repair_bands`' enumeration (`compile_tables`' docstring says so of that parameter).

**`rdfs:domain` is deliberate on both properties and safe here**, unlike the R69 mechanism
`iladub:onPage`'s comment records (`iladub.ttl:104-116`): these two properties are minted for this
class and are carried by nothing else, so a domain entailment can retype nothing that is not already
an `etkl:IgnoredBand`. **MEASURE before writing** (rule 3): grep the repo for `bandText`/`bandIndex`
and confirm no existing term collides; `tab:bandIndex` already exists in the donor-evidence family
(`vocab/ontology/tab.ttl`, Task 1 of the grid-donation plan) — **a different property in a different
namespace on a different class**, which is fine, but say so in the task report so a reviewer is not
left to wonder.

### DECISION B — the classifier's reason is carried IFF it is total, and that is measured, not assumed

`classify` returns a `reason` alongside `NON_TABLE` — the census reads `fewer than 2 columns` (77) and
`fewer than 2 lines` (69) and nothing else (spec § 2.1). Carrying it makes the node self-describing
for one triple, and the value is the AXIOM's own published output, so §7 is satisfied.

**But whether `region.reason` is ever `None` on a NON_TABLE verdict is NOT measured.** The seam
(rule 3): **enumerate every `NON_TABLE` return site in `src/iladub/etkl/regions.py` and say in the
task report whether all of them set a reason.**

- If **total** → declare `etkl:ignoredBecause` (`xsd:string`) and make it `sh:minCount 1` in the shape.
- If **not total** → declare it, emit it only when present, and leave it out of the shape's required
  set. **Do not invent a placeholder reason** (§7: never fabricate to achieve coverage).

Either way the answer goes in the task report with the enumeration that produced it.

### DECISION C — a DISTINCT subject IRI, because `{doc}#region{idx}` is already taken on this branch

The NON_TABLE branch **already mints `{doc}#region{idx}`** when the band has unit markers, purely as
a hanger for `_emit_unit_markers` (`compile.py:819-820`). The carrier must **not** reuse that IRI: on
a ruled ignored band with markers the two products would become one node carrying both vocabularies,
and the unit-marker hanger's own typing is not this plan's to inherit.

The carrier mints **`{doc}#ignored{idx}`**, and its source region is **`{doc}#ignored{idx}-source`** —
the `{cand_uri}-source` idiom `escalate_region` already uses (`holon.py:458`).

**A test pins the disjointness**: on a band that has both unit markers and an ignored verdict, the
two subjects are different IRIs and neither carries the other's properties. (If the corpus has no
such band, build it synthetically; do not skip the assertion.)

### DECISION D — the shape lives in `etkl-shapes.ttl` and is run against real compiled graphs by a test, NOT wired into the compile membrane

The evidence measured that the compile membrane loads neither `etkl` shapes nor `etkl` ontologies
(§ 5). This plan measured the second half, and it is decisive:

**`_validate` does not run at all on a page with no table.** `compile.py:1441-1445` guards the page
membrane with `if validate_shapes and (any(graph.subjects(RDF.type, TAB.RecordTable)) or
any(graph.subjects(RDF.type, TAB.HierarchicalTable)))`. A page of pure furniture — precisely the page
with the most ignored bands — never reaches a shape at all. So wiring a carrier shape into
`_TAB_SHAPE_FILES` would buy enforcement that **looks** total and is silently absent exactly where the
carrier matters most. That is failing upward, and §7 refuses it.

Wiring `etkl-shapes.ttl` in is refused for a second, independent reason: that file's own header
records why it is the one shape file the compile membrane does not load
(`vocab/shapes/etkl-shapes.ttl:68-82`), and wiring it would re-open the holon:05 §2.1 safety argument
and make `etkl:MembraneHealthShape` vacuous at compile time. **Not this plan's argument to re-open.**

So: **the NodeShape goes in `vocab/shapes/etkl-shapes.ttl`** (inheriting its non-loading, as
`MembraneHealthShape` deliberately does) and enforcement comes from **two** places:

1. the vocabulary convention — `tests/test_vocab_shapes.py`, a conformant example and a negative
   example that must fail (Task 1);
2. **a test that validates a REAL compiled page graph against that shape file** (Task 3) — real
   enforcement on a real product, without touching any membrane set.

**Consequence, and it is a saving:** the shape is **not wired**, so evidence § 5's vacuity-registry
question does not arise at all — `tests/etkl/test_vacuity_registry.py:140` enumerates wired shapes
only, and its reverse arm (`:352`) polices rows for unwired shapes, i.e. it *forbids* a row here.
**Handoff § 5b's prediction ("zero registry rows") is therefore not tested by this plan** — it was a
prediction about the wiring arm this plan declines to take. Say so in Task 3's report rather than
claiming it confirmed.

**MEASURE before writing the Task 3 test** (rule 3): validating a compiled graph against the whole of
`etkl-shapes.ttl` also loads `DocumentProjectionShape` and `MembraneHealthShape`. **Confirm the new
shape is the only one with focus nodes in a compiled page graph** and report the focus-node counts. A
compiled graph is expected to contain no `etkl:DocumentProjection`, but *expected* is not *measured*.

### DECISION E — `_band_text` moves to `bands.py` and becomes public

Evidence § 4: `document.py:110` imports from `.compile` at module level, so `compile.py` importing
`document._band_text` is a cycle. `bands.py` imports only `from .geometry import Line, Rule, HRule`
(`bands.py:12`) and defines `Band` itself, so it is reachable from both with no cycle.

**Move, do not copy** — two call sites follow it (`document.py:594,598`). It becomes `band_text`
(public: it is now the definition two modules depend on), and its docstring travels **verbatim**; it
already argues the stance this carrier needs.

**Two PROSE references also name it and are not call sites** — `document.py:476` and `:480`, inside
`licence_evidence`'s docstring family, both written as `` `_band_text` `` (measured: `grep -n
"_band_text" src/iladub/etkl/document.py` returns exactly `:476, :480, :540, :594, :598`). A move that
updates the two calls and leaves the two mentions makes the file cite a function it no longer
contains. **Update all four, and re-measure if the target sits below the comment in the same file**
(CLAUDE.md plan rule 7). The function-local-import alternative is refused: it
answers the cycle but leaves a definition this plan makes load-bearing sitting private in the wrong
module.

---

## File Structure

```
vocab/ontology/etkl.ttl                       MODIFY  3–4 new terms (DECISION A, B)
vocab/shapes/etkl-shapes.ttl                  MODIFY  etkl:IgnoredBandShape (DECISION D)
examples/ignored-band-conformant.ttl          NEW     the worked example that conforms
tests/ignored-band-textless-leak.ttl          NEW     negative: a node with no bandText
tests/ignored-band-pageless-leak.ttl          NEW     negative: a node with no page
tests/test_vocab_shapes.py                    MODIFY  +1 conformant, +2 negative tests
src/iladub/etkl/bands.py                      MODIFY  band_text moves here (DECISION E)
src/iladub/etkl/document.py                   MODIFY  -_band_text, +import, 2 call sites
src/iladub/etkl/holon.py                      MODIFY  emit_ignored_band, beside escalate_region
src/iladub/etkl/compile.py                    MODIFY  one call in the NON_TABLE branch
tests/etkl/test_ignored_band_carrier.py       NEW     arms 1, 2, 3 + DECISION C disjointness
docs/wiki/concepts/neurosymbolic-exemplars.md MODIFY  one PROCEDURAL entry
docs/superpowers/residues.md                  MODIFY  strike R212, status cell
docs/superpowers/residues-open.md             MODIFY  R212 row moves out
docs/superpowers/residues-closed.md           MODIFY  R212 row moves in, with closure evidence
docs/superpowers/2026-09-12-...-evidence.md   NEW     the corpus + invariant arms, run locally
```

---

## Task 1: The vocabulary, the shape, and the examples

**Files:** `vocab/ontology/etkl.ttl`, `vocab/shapes/etkl-shapes.ttl`,
`examples/ignored-band-conformant.ttl`, `tests/ignored-band-*-leak.ttl`, `tests/test_vocab_shapes.py`

**Interfaces:** no Python. Terms per DECISION A and DECISION B; shape per DECISION D.

**The shape — `etkl:IgnoredBandShape`, `sh:targetClass etkl:IgnoredBand`:**

- `etkl:bandText` — `sh:minCount 1`, `sh:datatype xsd:string`. **Required is the point**: spec § 2.5
  records `tab:RegionCaption` as a carried node that decayed into a typed-but-empty stub with no page
  and no provenance ([[R218]]), and this shape is what forbids the carrier repeating it.
- `iladub:fromRegion` — `sh:minCount 1`. Provenance-to-the-page (CLAUDE.md §6) reaches the node
  through the region, exactly as a candidate's does (`iladub-shapes.ttl:27`).
- `etkl:bandIndex` — `sh:minCount 1`, `sh:maxCount 1`, `sh:datatype xsd:integer`.
- `etkl:ignoredBecause` — required **iff** DECISION B's measurement says the reason is total.
- **The page itself is required on the REGION, not on the band node** — `iladub:onPage` has
  `rdfs:domain iladub:SourceRegion` and its comment explains at length why it may never sit anywhere
  else (`iladub.ttl:104-116`, the R69 mechanism). **MEASURE and report**: whether the shape can reach
  it with `sh:node`/a property shape on `iladub:fromRegion`, or whether a second NodeShape targeting
  `iladub:SourceRegion` is needed. **If a second shape is needed, do not add one**: an
  `iladub:SourceRegion` shape would fire on every escalated region in every compiled graph, which is
  far outside this loop — instead put the requirement on the path `iladub:fromRegion / iladub:onPage`
  from the band node, and say in the report which form you used and why.

`examples/ignored-band-conformant.ttl` — one `etkl:IgnoredBand` with every required property, its
region, and a page. Two negatives, each removing exactly one thing: `-textless-` drops `etkl:bandText`,
`-pageless-` drops the page from the region. Register all three in `tests/test_vocab_shapes.py`
following the existing `_validate(...)` idiom (`:22-27`, used at `:32-46`), with `[os.path.join(ONT, "etkl.ttl"),
os.path.join(ONT, "iladub.ttl")]` as the ontology graph — **the example uses `iladub:` terms, so
`iladub.ttl` must be in the ont list or the negative may fail for the wrong reason.**

- [ ] **Step 1: Write the failing tests** — the three `test_vocab_shapes.py` cases, against terms and
      examples that do not exist yet. Confirm they fail, and **read the failure**: a parse error is
      not the assertion failing.
- [ ] **Step 2: Declare the terms** in `etkl.ttl` (after the existing core-classes block; match the
      file's `rdfs:label` + `rdfs:comment`@en style exactly).
- [ ] **Step 3: The shape and the three example files.** Green.
- [ ] **Step 4: Run the whole `tests/test_vocab_shapes.py` file**, not only the new cases — the new
      shape shares a file with `DocumentProjectionShape` and `MembraneHealthShape`.

**## FALSIFICATION (required):** delete `sh:minCount 1` from `etkl:bandText`; show
`ignored-band-textless-leak` **passing validation** (i.e. the negative test failing); restore; show
green. Repeat for the page requirement.

---

## Task 2: `band_text` moves, the emitter, and the wiring

**Files:** `src/iladub/etkl/bands.py`, `document.py`, `holon.py`, `compile.py`,
`tests/etkl/test_ignored_band_carrier.py`

**Interfaces:**
- Move (DECISION E): `bands.band_text(band) -> str`, docstring verbatim from `document.py:540-548`.
  `document.py` imports it and its two call sites (`:594,598`) follow.
- New: `holon.emit_ignored_band(g, doc_uri, idx, band, page, reason)` — subjects per DECISION C,
  properties per DECISION A/B. It writes triples and **returns nothing**. It is placed beside
  `escalate_region` and carries the same `Gate classification (CLAUDE.md §8): PROCEDURAL` paragraph
  shape that function already uses (`holon.py:438-441`) — cite spec § 3's gate paragraph rather than
  arguing it afresh.
- Call site: the NON_TABLE branch, `compile.py:814-824`, where `doc`, `idx`, `band` and `page_number`
  are all already in scope (evidence § 2). **It touches no counter and adds no `RegionReport` field**
  — see § The invariant.

**MEASURE before writing the call** (rule 3): the branch's existing comment
(`compile.py:816-818`) states the accounting stance for absorbed ink. **Read it, and extend it rather
than adding a second comment making the same claim** (plan rule 6 applies to code comments too).
**Re-measure any `file:line` you put in a comment AFTER the edit** if its target is below the comment
in the same file (CLAUDE.md plan rule 7, [[R139]]) — prefer naming a symbol.

**The RED state is already measured** (evidence § 3): a `reportlab` page carrying a one-line title, a
ruled 3-column table and a one-line footer compiles to `b0 NON_TABLE 'fewer than 2 lines'`, `b1
RECORD_TABLE`, `b2 NON_TABLE 'fewer than 2 lines'` — 420 triples, with the title and footer strings
scoring **0 hits** among the graph's literals. Build that page with `reportlab` (the `_page` helper in
`tests/etkl/test_grid_donation_disposal.py:31-45` is the idiom; `pytest.importorskip("reportlab")` and
`("pdfplumber")` at the top, **not** corpus-gated). **The coordinates are yours to write — this plan's
author did not run them.** If the page does not band as measured, say so and adjust the fixture; do
not adjust the assertion.

**The assertions (propositions — see Global Constraint 4):**

1. Compiling that page through `compile_tables` puts the title's exact text and the footer's exact
   text in the graph as `etkl:bandText` values — **exact string equality with `bands.band_text(band)`
   for the corresponding band**, not a substring match.
2. Each carried node carries its `etkl:bandIndex`, and the two indices are the band positions
   `page_bands` returned (0 and 2 on the measured fixture).
3. Each carried node reaches a page through `iladub:fromRegion / iladub:onPage`, typed `xsd:integer`.
4. The RECORD_TABLE band mints **no** `etkl:IgnoredBand` — carriage is scoped to the ignored verdict.
5. **DECISION C's disjointness**: on a band with unit markers and an ignored verdict,
   `{doc}#ignored{idx}` and `{doc}#region{idx}` are different subjects and neither carries the
   other's properties.

- [ ] **Step 1: Reproduce the RED state.** Build the fixture, compile it, and show the title/footer
      strings scoring 0 hits **before writing the emitter**. Paste the count into the task report. A
      fixture that is already green has not reproduced the RED state — stop and say why.
- [ ] **Step 2: Write the failing tests** (assertions 1–5).
- [ ] **Step 3: Move `band_text`**; run `tests/etkl/test_document.py` and anything touching
      `licence_evidence` to show the move is behaviour-neutral.
- [ ] **Step 4: The emitter and its one call.** Green.

**## FALSIFICATION (required):** delete the `emit_ignored_band` call from the NON_TABLE branch; show
assertions 1–4 **failing**; restore; show green. **Separately**, for assertion 5: point the emitter at
`{doc}#region{idx}` instead of `{doc}#ignored{idx}` and show the disjointness assertion failing. A
falsification that only removes the call has not tested DECISION C.

---

## Task 3: The membrane, on a real compiled graph

**Files:** `tests/etkl/test_ignored_band_carrier.py` (same file, new test)

Per DECISION D, the shape is not wired into any membrane set, so **this test is the enforcement**.
Compile the Task 2 fixture, validate the resulting graph against `vocab/shapes/etkl-shapes.ttl` with
`inference="rdfs", advanced=True` (the `tests/test_vocab_shapes.py:19-24` idiom), and assert it
conforms.

**MEASURE and report** (DECISION D's seam, rule 3): the focus-node count of **every** shape in that
file against the compiled graph. State in the task report that `etkl:IgnoredBandShape` is the only one
with focus nodes — or, if it is not, stop and report before proceeding; validating a compiled graph
against a shape you did not expect to fire is a finding, not a nuisance.

**Report, do not claim:** handoff § 5b predicted *"a wired carrier shape costs zero vacuity-registry
rows."* **This plan does not wire it, so that prediction is untested here.** Record it as untested,
not as confirmed.

- [ ] **Step 1:** the conformance test, and the focus-node census in the report.
- [ ] **Step 2:** run `tests/etkl/test_vacuity_registry.py` in full and show it green — the file's
      reverse arm forbids a registry row for an unwired shape, so an unexpected failure here means
      DECISION D was mis-measured.

**## FALSIFICATION (required):** make the emitter drop `etkl:bandText` on one band; show this test
**refusing** the compiled graph; restore; show green. This is the arm that proves the shape reaches
real products and not only the hand-written example.

---

## Task 4: The invariant arm and the corpus arm, on the shipped emitter

**Files:** `docs/superpowers/2026-09-12-the-ignored-band-carries-its-text-evidence.md` (new)

Evidence § 1 confirmed the invariant with a **throwaway** emitter. This task re-runs it against the
**shipped** one. Both arms need the corpus (Global Constraint 5) and **neither runs in CI**.

- [ ] **Step 1 (arm 4 — the invariant):** `PYTHONPATH=src .venv/bin/python
      scripts/corpus_verdict_snapshot.py <dir>` on `main` at the branch point and again on the
      branch. Diff per-document score, per-page `(asserted, escalated)`, every per-region verdict,
      and the canonical graph hash. **Expected: 7 scores SAME, 7 ledgers SAME, all verdicts SAME, 7
      hashes MOVED** — see § The invariant. Paste the table into the evidence doc.
- [ ] **Step 2:** check the triple deltas against spec § 2.1's per-document ignored-band counts. The
      throwaway wrote 3 triples per band; the shipped emitter writes more (DECISION A/B/C), so the
      delta per band is a **different constant** — state which, and that it is uniform per document.
      A non-uniform delta means the emitter is conditional somewhere it should not be.
- [ ] **Step 3 (arm 5 — the corpus arm, R212's actual subject):** compile
      `ag-trade/graincorp-capacity-2026-08-04.pdf` and show that its title
      (`ELEVATION CAPACITY TABLE`), its print line, its issuer line and its footer are now **in** the
      graph — the four bands spec § 2.2 lists verbatim. **Paste the output.** This is the measurement
      that closes R212; a green CI is not evidence for it.
- [ ] **Step 4:** if any score moves, **stop**. Do not adjust a pinned floor. A moved score refutes
      the invariant this whole loop rests on, and that is a finding worth more than the feature.

**## FALSIFICATION (required):** the invariant arm is itself a falsification instrument, but it can
lie by not running: **show the shipped emitter is live on the corpus run** (triple counts up, probe
strings found) before reporting SAME scores as meaningful. Evidence § 1 records why — an unmoved hash
from a silently no-op emitter reads as a refutation when it is an instrument failure.

---

## Task 5: The register, the wiki, the suite, the PR

- [ ] **Step 1: Close [[R212]].** Strike the number in `docs/superpowers/residues.md`
      (`~~R212~~`), set its **status cell** to `closed` — the status is its own cell, not a
      strikethrough — and move the full row from `residues-open.md` to `residues-closed.md`, adding
      the closure evidence in place (the corpus arm's output, Task 4 Step 3). **Do not delete the
      row.**
- [ ] **Step 2: Raise what this loop leaves exposed**, each with a raise-time tally snapshot. The
      immediately preceding snapshot is `| R219 (65/209 closed)` (`residues-open.md`) — recompute,
      do not copy. Candidates, only if true at the end: the carrier and the unit-marker hanger are two
      unlinked nodes for one band (DECISION C); [[R219]]'s band-vs-distinct-text confound is
      untouched and now has a graph to measure against.
- [ ] **Step 3: The wiki entry.** One PROCEDURAL entry in
      `docs/wiki/concepts/neurosymbolic-exemplars.md`, appended after the *Grid donation (2026-09-12)*
      section (`:270`). Bump `updated:` in the front matter and add the new source files to
      `sources:`. **Global Constraint 3 binds here**: any decimal figure needs a date or a backticked
      sha in its own block. The entry says what the carrier decides — **nothing** — and why that is
      what keeps it PROCEDURAL rather than NEURAL.
- [ ] **Step 4: The evidence doc**, completed from Task 4, with a `Serves:` line and a
      `Doc impact:` line.
- [ ] **Step 5: The whole suite, in-band, once.** ~45–60 minutes (Global Constraint 7). Read the
      output.
- [ ] **Step 6: The PR.** Body states: R212 closed, the invariant re-confirmed on the shipped
      emitter, DECISION D's membrane choice and its reason, and handoff § 5b left **untested** by
      design.

**## FALSIFICATION (required):** not applicable to the register/wiki steps — they assert nothing
about behaviour. Say so explicitly in the task report rather than omitting the block.

---

## Self-review against the spec

Before opening the PR, check each line and answer it in the PR body:

1. **Spec § 4's "what this loop does NOT do"** — does any shipped test assert that an ignored band
   becomes a header, that the text reaches the proposer, or that the capacity contract exists? All
   three are **out of scope** (plan rule 5). A test asserting any of them is a contradiction to
   report, not to satisfy.
2. **Spec § 3's three refusals** — no `iladub:CandidateConcept` is minted for an ignored band
   (which would falsify § 2.8's registered 3-of-7), no `tab:RegionCaption` is reused, and no
   transient `tab:*Block` term is promoted.
3. **The ruling** — *all* ignored bands are carried; no rule anywhere selects among them.
4. **The namespace** — `etkl:`, and `etkl.ttl` is still standalone.
5. **Plan rule 4** — every task shipped a `## FALSIFICATION` block.
6. **Plan rule 7** — every `file:line` in a new comment whose target is below it in the same file was
   re-measured after the edit, or was replaced by a symbol.
