# Plan — a figure carries its date

**Executes** `docs/superpowers/specs/2026-09-08-a-figure-carries-its-date-design.md` ([[R187]]).
Written 2026-09-08, under the originating floor, after **O3 was run** (§0 below).

**Doc impact: increment.**

The spec is the contract. This plan states the decisions it left open, the **one correction** the
census forced on it, the task order, the interfaces, and the falsifying oracle per task. It does not
re-derive the spec's arguments — where an invariant is argued there, this plan **cites** it
(CLAUDE.md § Plan authoring discipline rule 6).

**Global constraint (CLAUDE.md §8).** The classification is spec §2 and is not reopened: D1 AXIOM
(derivation, open world), D2 CONSTRAINT (SHACL, closed world, block-scoped), D3 PROCEDURAL (exact
decimal arithmetic). **No NEURAL step. No tuned constant, no tolerance, anywhere in the diff** — §0.2
is the place this plan came closest to introducing one and did not.

---

## 0. O3 was RUN FIRST, before any code — and it moved the design twice

Handoff 5b graded the hard gate **PROPOSED**, resting on spec §5's O3 finding no unexplained false
positive. O3 is now measured, on the whole tracked-markdown tree, against a hand-built register.

### 0.1 The census

Method: every decimal literal in every tracked, non-exempt `.md` file (the extractor's own walk —
`tests/docgov_extract.py:tracked_markdown` + `is_exempt`), matched against an 18-row candidate
register by spec §3.3's rule `round(value, k) == Decimal(L)`, `k` read off the literal.

```
denoting occurrences by class: {'evidence': 571, 'wiki': 13}   (evidence is EXEMPT — spec §3.4)
ambiguous, therefore not findings: wiki '1.0' ×4; evidence '1.0' ×248, '0.9' ×61, '0.4' ×27, …
contract / manual / assertion / other: 0
```

**The first correction the census forced: the register MUST carry superseded readings.** Bootstrapped
from spec §1.4 alone — seven readings taken 2026-09-08 — the detector finds **none** of R187's
subject figures, because a superseded literal (`0.9655`, `0.9047`, `0.1895`) rounds to no current
value. Spec §3.1 already says the register holds *"the set of readings **ever** taken"*; O1's
instruction to *"bootstrap from §1.4"* is satisfiable only as *"§1.4 **and** the dated prior readings
recorded in the tree"*. Task 1 bootstraps 18 rows, not 7, and names each row's source.

### 0.2 The second correction: TWO false positives, and the derived remedy that removes them

Spec §3.3 predicted exactly one false positive (`1.0000` vs `graincorp-capacity`). The census found
**three**, in two families:

| occurrence | denotes | verdict |
| --- | --- | --- |
| `data-grid.md:191,193,197` `1.0000` | capacity `1.0` @4dp | **FALSE POSITIVE** — the hypothetical perfect page score. Predicted by spec §3.3. |
| `dimension-split.md:154` `0.1`, `neurosymbolic-exemplars.md:139` `0.1` | apple `0.06068601583113457` @1dp | **FALSE POSITIVE, unpredicted** — *"quarantines exactly like a 0.1-scored one"*, a confidence, not a corpus score. |

Under spec §5's own rule (*"a single unexplained false positive blocks the hard gate"*) the `0.1`
pair sends the wiki disposition to **warning**. The obvious rescue — a minimum-precision floor — is
**forbidden**: a threshold picked to make two findings go away is the tuned constant CLAUDE.md §8
calls *prima facie evidence* of a misclassified decision.

**The remedy is derived, not chosen: the register's own separating precision.**

> `sep(R)` = the least `k` at which all readings in `R` are pairwise distinct at `k` decimal places.
> A literal at `k < sep(R)` is **under-determined by construction** — at that precision the register
> cannot identify its own rows, so a literal cannot be a quotation *of it*, whichever row it happens
> to collide with in this particular sample.

Measured on the 18-row register: **`sep = 4`**, and the approach is monotone rather than a cliff —

```
k=0:  2/18 distinct   k=1:  8/18   k=2: 14/18   k=3: 17/18 (0.910 ×2)   k=4: 18/18   k=5: 18/18
```

There is **no free parameter**: `sep` is recomputed from the register on every run. Rejecting `k < 4`
kills both `0.1` occurrences *and* every `1.0`; `1.0000` survives at `k=4` and is disposed of by spec
§3.3's exemption, `cor:notQuotable` on capacity's reading — **one row of eighteen, stated with its
size**, as [[R188]] asks.

### 0.3 The result — and what it licenses

With `sep=4` and capacity not quotable, the census returns **11 wiki occurrences, and hand
classification finds all 11 denote a real corpus document score. Zero false positives.**

```
data-grid.md:174,188,206  0.9654553611484971 → graincorp-stem   data-grid.md:205  0.06068601583113457, 0.35560344827586204 → apple
dimension-split.md:88     0.9047 → cbh-stem                     neurosymbolic-exemplars.md:125  0.9047 → cbh-stem
neurosymbolic-exemplars.md:251  0.1895, 0.6289 → apple          table-holon-compilation.md:119,177  0.9655 → graincorp-stem
```

**Therefore the wiki disposition ships HARD, and handoff 5b's proposition is CONFIRMED** — on a
design one step different from the one it graded. The price is recorded, not hidden, in §0.4.

`dimension-split.md:88` is dated **in its own block** (`:86` carries `(tests/test_cbh_e2e.py,
2026-08-04)`) and therefore **passes**. The same figure, `0.9047`, is undated at
`neurosymbolic-exemplars.md:125` and **fails**. That pair is O4, and it is not synthetic.

Repair surface (Task 5): **10 findings, 3 pages** — `data-grid.md` ×5, `neurosymbolic-exemplars.md`
×3, `table-holon-compilation.md` ×2.

> **CORRECTED by the instrument, after Task 3 — the prediction above is wrong and is left standing
> rather than edited away.** The repair surface is **8 findings, 2 pages**:
> `table-holon-compilation.md`'s two `0.9655` occurrences are **already dated** and never fire. The
> block that states them opens at `:108` with `**Loop M (2026-08-03) — pagination as a second
> accommodation operator, whole-document.**`, and 2026-08-03 is exactly the date the register carries
> for that reading. The hand census read lines 112-121 — a window — where the instrument reads the
> block, which is the unit the design chose and argued for. Task 5's instruction to *"MEASURE the
> exact set from the instrument's own output, not from §0.3"* is the reason this cost nothing, and it
> is the second time in this plan that a hand count lost to the instrument.

### 0.4 What §0.2 costs, stated before it is built

- **`sep` is data-derived, so it MOVES.** Two future readings of one document differing only at 17dp
  would push `sep` to 17 and **silence the gate entirely** — [[R188]]'s under-firing shape. The guard
  is Task 4's O1: the ten findings are pinned by name, so a silenced gate fails loudly instead of
  passing. `sep` itself is asserted in a test (§Task 2, O5b) for the same reason.
- **Capacity's reading is unquotable, so a genuinely undated quotation of `1.0` / `1.0000` for
  `graincorp-capacity` will never be caught.** One document of seven, and the one whose score is a
  round number that means something else everywhere in this repo.
- **A 4dp-recorded reading cannot be quoted below 4dp and cannot be quoted above it either.**
  `0.9047` at 5dp denotes nothing. Correct — the digits were never measured — and a limit, not a bug.

---

## 1. The decisions this plan takes

| # | decision | ruling and ground |
| --- | --- | --- |
| **D-A** | register location: spec §3.1 **arm A** — extend `tests/corpus-manifest.ttl` | The spec recommends it and neither arm touches a Contract-class file, so this is **not the maintainer's to rule** (handoff 5a). The manifest already states these figures in `cor:adjudication` prose, is already ruled append-only *in its own text*, and its readings-vs-rationale pairing is the point. Arm B would be a second register for the same quantities. |
| **D-B** | denotation is filtered by `sep(R)`, computed per run | §0.2. Without it the wiki disposition could not be hard. |
| **D-C** | `cor:notQuotable` marks a READING, and marks it out of the **finding**, not out of the **register** | Measured, §0.2: both forms happen to give 13 findings today because many `0.9x` readings collide at `k=1`, but dropping a row from the register *shrinks the extension `sep` is computed from* and can raise a different literal to uniqueness. Filtering findings keeps the denotation extension total. |
| **D-D** | wiki = **HARD**, evidence = **exempt**, everything else = **warning** | Spec §3.4 unchanged; licensed by §0.3. |
| **D-E** | a *block* is a maximal run of consecutive non-blank lines | Spec §3.2 fixes the block scope; this is its cheapest total definition. Verified against both O4 blocks in §0.3. |

**No decision here is escalated to the maintainer.** Nothing touches CLAUDE.md.

---

## 2. Task order

Five tasks. Each ships with TDD evidence **and** a `## FALSIFICATION` block (CLAUDE.md § Plan
authoring discipline rule 4) — remove or invert what the new test pins, show it **failing**, restore,
show green. **No falsification evidence ⇒ the task fails review.**

### Task 1 — the register (arm A)

Add to `vocab/internal/corpus.ttl`: `cor:reading` (property), `cor:Reading` (class), `cor:value`
(`xsd:decimal`), `cor:readAt` (`xsd:date`), `cor:atCommit`, `cor:recordedIn` (the tree path the
reading is transcribed from), `cor:notQuotable` (`xsd:boolean`).

Add to `tests/corpus-shapes.ttl` a `cor:ReadingShape` requiring exactly one `cor:value`, one
`cor:readAt`, and at least one of `cor:atCommit` / `cor:recordedIn`.

> **S2 is MEASURED and closed** (spec §6): `cor:DocumentShape` (`tests/corpus-shapes.ttl:12`) carries
> no `sh:closed`, so `cor:reading` is admissible without touching it. The *positive* shape above is
> new work and is this task's.

Add 18 `cor:reading` nodes across the seven `cor:Document` nodes. **Every row names where it was
transcribed from**; the values and their provenance are §0.1's register — spec §1.4 for the
2026-09-08 seven, and for the priors: `2026-09-05-r173-5a-rebaseline.md:34-40`,
`2026-08-20-escalation-reason-census.md:62-68`, and the manifest's own 2026-08-03 rationale. Mark
capacity's `1.0` `cor:notQuotable true` **with its reason in the row** (§0.2).

**Invariants.** The manifest stays append-only — **no existing line is modified**, rows are added.
`cor:scoreFloor` is untouched: a floor is not a reading. **`bfs 0.9401` is NOT registered** — spec
§1.4 establishes it was taken under C3, reverted at `51bdd23`, and never a reading of a commit on
`main`; the plan records the exclusion so the next reader does not think it was missed.

**Oracle.** `pytest tests/test_corpus.py -k manifest` (or whichever test validates the manifest
against `corpus-shapes.ttl` — **MEASURE which test that is before writing the assertion**) is green,
and a reading node missing `cor:readAt` makes it fail.

### Task 2 — extraction (PROCEDURAL, `tests/docgov_extract.py`)

```python
def figure_occurrences(text: str) -> list[tuple[int, str, bool]]:
    """(line, lexical, block_is_dated) for every decimal literal in a markdown text."""

def separating_precision(values: Sequence[Decimal]) -> int:
    """Least k at which every value is pairwise-distinct at k decimal places."""

def denotes(lexical: str, readings: Mapping[Key, Decimal], sep: int) -> Key | None:
    """The unique reading whose value rounds to `lexical` at `lexical`'s own precision k,
    or None when k < sep, or when zero or more than one reading does. NO tolerance."""
```

**Invariants** (spec §6 I1–I3, plus one this plan adds):

- **I1.** `decimal.Decimal` throughout; no `float`, no epsilon. A tolerance in `denotes` is a §8
  defect by CLAUDE.md's own words.
- **I2.** The register is read, never written.
- **I3.** `extract()` stays a pure fact emitter — the docstring binds this and must stay true.
  `denotes` computing a *denotation* is arithmetic, not a membership decision; the **disposition**
  stays in SHACL.
- **I5 (new).** `sep` is computed from the register that is loaded, never passed in as a literal and
  never written down in the source. A digit `4` appearing as a precision anywhere in the diff is the
  defect this task exists to avoid.

**Facts emitted**, per spec §3.2: `dg:FigureOccurrence` with `dg:inDoc`, `dg:line`, `dg:lexical`,
`dg:blockDated`; and `?occ dg:denotesReading ?reading` where `denotes` returns a key. Occurrences
that denote nothing emit **no** occurrence node — the graph carries figures, not every decimal.

**Seams to MEASURE before writing the call** (plan rule 3):

- **S1 — the read sites.** MEASURED here so the implementer verifies rather than searches:
  `_evidence_facts` and `_wiki_facts` each call `(repo / path).read_text()` independently, so a
  wiki/evidence file is already read once and a plain file zero times. Adding a third read per file
  is the wrong shape: **measure whether hoisting one `read_text()` into `extract`'s loop and passing
  it down is line-neutral in behaviour**, and do that rather than adding a read.
- **S3 — runtime.** 29.65 s today, dominated by `git log -1` per cited source. Re-measure after; a
  walk over every tracked markdown file is new I/O and the figure must appear in the task report.

**Oracles.**
- **O5 (spec §5).** `0.9655` denotes the stem's `0.9654553611484971`; `0.9659` does not. Both
  directions, on fixtures, not on the tree.
- **O5b.** `separating_precision` of the shipped register **is 4**, asserted by value — §0.4 says why
  a silent move is the hazard.
- **O4 (spec §5).** Block scope: a two-line fixture whose figure line carries no date but whose
  block does → `blockDated True`; move the date out of the block → `False`.

### Task 3 — the derivation (AXIOM, open world)

`vocab/queries/docgov-undated-figure.rq`, `CONSTRUCT { ?doc dg:statesUndatedReading ?occ }` over
`?occ dg:inDoc ?doc ; dg:denotesReading ?r ; dg:blockDated false`.

**Invariant I4 (spec §6).** No existing `docgov-*.rq` changes semantics — the recalibration is
purely additive. `staleAgainstEvidence` stays hard, `staleAgainstCode` stays a warning (spec §4.3:
it is refuted as *this* detector, not as itself).

**Oracle.** The construct returns exactly the occurrences §0.3 enumerates, minus
`dimension-split.md:88`; **and returns nothing at all** for `decision-holon.md`,
`promotion-decision.md`, `hga.md` — spec §5's **O2**, the anti-promotion guard.

### Task 4 — the gate

A new hard test in `tests/test_doc_governance.py` failing on any `wiki` document carrying
`dg:statesUndatedReading`, and a **warning** for any other class (spec §3.4). The membrane half (D2)
is a `dg:UndatedFigureShape` in `vocab/shapes/doc-governance-shapes.ttl`; **decide from the existing
file's idiom whether the disposition belongs in the shape or in the test, and say which in the task
report** — `staleAgainstEvidence` is a test-side gate and `ContradictionDrainShape` is shape-side, so
both idioms are already in this instrument.

**Oracle — O1 (spec §5), pinned BY NAME.** Before Task 5 the test **fails**, naming
`data-grid.md`, `neurosymbolic-exemplars.md` and `table-holon-compilation.md` and exactly the ten
occurrences of §0.3. That red run is the task's TDD evidence and it must be in the report verbatim.

### Task 5 — the repair (spec §3.5)

**Date the claim; never rewrite the figure.** R187's deferral column ruled that rewriting a loop's
measured figures in place *destroys the record rather than dating it*. Each of the ten findings gets
its reading's date from the register — the form `dimension-split.md:86` already uses, in the block.

**MEASURE the exact set from the instrument's own output**, not from §0.3: §0.3 is a hand census run
against a hand register and is the *prediction*, not the input.

**Invariants.** `docs/wiki/**` is Wiki class, not Evidence: it is freely rewritable and the
append-only rule does not apply. Each repaired page's `updated:` frontmatter moves to the repair
date — and the pages cite code sources, so **re-run `test_no_wiki_page_stale_against_evidence`
after**: moving `updated:` forward can only help there, but measure rather than assume.

**Oracle — O6.** `pytest tests/test_doc_governance.py -q` green with the new test **passing, not
skipped**; then the full suite.

---

## 3. What this plan does NOT do

Spec §4, unchanged and not re-argued: no supersession marking and no "current value" anywhere
([[R190]]); no `.py`/`.ttl` comment scope ([[R189]]); `staleAgainstCode` neither deleted nor
promoted; **document** scores only, never page scores — so `data-grid.md`'s `0.9588` / `0.9706` /
`0.7802` and `table-holon-compilation.md`'s `0.9560` are deliberately ungated; and no re-measurement
of the capability sentence.

One addition of this plan's own: **`bfs 0.9401` is deliberately absent from the register** (Task 1).

## 4. Residues this plan expects to raise

- The `sep` movement hazard of §0.4 — under-firing, [[R188]]'s shape, guarded only by a pinned test.
- Capacity's unquotable reading — one document of seven outside the gate.
- Whatever Task 5 finds that §0.3 did not predict.
