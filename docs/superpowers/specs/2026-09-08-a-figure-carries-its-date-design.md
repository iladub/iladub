# A figure carries its date — the docgov instrument gains a FIGURE scope, and the page scope is refuted as R187's detector

**Spec for [[R187]].** Written 2026-09-08, in a fresh session, under the originating floor.

**Doc impact: increment.**

Predecessor: `docs/superpowers/2026-09-08-two-loops-handoff.md` action **5b′** (ASSERTED) and
`docs/superpowers/2026-09-08-two-loops-sequenced.md` §2. The shared invariant both R186 and R187
instantiate is derived **once** in that document's §3 ([[R188]]); this spec **cites** it and does
not re-derive it (CLAUDE.md § Plan authoring discipline rule 6).

---

## 0. Verdict, stated first

**The handoff's oracle is REFUTED by measurement, and its refutation is this spec's main finding.**

5b′ named the falsification in advance: *"the gate fires on the two pages R187 names and not on the
other seven currently warned."* Three separate measurements taken in this session say that oracle
cannot be satisfied by any honest detector:

1. **The population is 8, not 9** — `pytest tests/test_doc_governance.py -W always::UserWarning`
   at `9eb5cd0` reports **8** wiki pages carrying `staleAgainstCode`, not the 9 recorded on
   2026-09-08. So "the other seven" is "the other six".
2. **Three of those 8 pages contain no decimal at all** — `decision-holon.md`,
   `promotion-decision.md`, `hga.md`. A page-scoped source-staleness signal cannot be recalibrated
   into a figure-scoped detector, because on 3 of 8 of its own firings there is no figure to be
   stale.
3. **There is a THIRD stale quantity, and the whole-wiki sweep of 2026-09-08 classified it as not
   stale.** `docs/wiki/concepts/dimension-split.md:88` and
   `docs/wiki/concepts/neurosymbolic-exemplars.md:125` both state the CBH document score as
   `0.9047`. Measured at `9eb5cd0` in this session:

   ```
   $ python -c "from pathlib import Path; from iladub.etkl.document import compile_document; \
       r = compile_document(Path('corpus/ag-trade/cbh-stem-2026-08-03.pdf')); print(repr(r.score), len(r.pages))"
   0.9095022624434389 1
   ```

   That quantity has moved **twice** since the wiki stated it: `0.9047` (census 2026-08-20) →
   `0.9091940976163451` (`2026-09-05-r173-5a-rebaseline.md` §1) → `0.9095022624434389` (today).
   `the-two-counts` §2 asserted *"the whole-wiki sweep found ZERO new stale quantities"*; that
   assertion is **false**, and the reason is instructive — the sweep classified figures by reading
   them, and a figure is only checkable against a **reading taken today**.

So: the correct gate fires on **more** than the two pages R187 names, and the handoff's oracle would
have rejected a correct instrument. It is replaced in §5.

**And the scale of the defect is larger than any previous loop measured.** §1.4 re-reads all seven
corpus documents at `9eb5cd0`: **four of the seven document scores have moved since 2026-09-05**, and
no document in this repo records the new values. Three days.

**What survives from 5b′, unchanged:** *do not design a new lint*. This spec adds one derivation and
one extraction to the instrument that already runs — same module, same membrane, same test file. No
second instrument is built.

---

## 1. What is measured, and what it costs to re-measure

### 1.1 The instrument as it stands

`tests/test_doc_governance.py` (66 lines) → `tests/docgov_extract.py` (231 lines) →
`vocab/shapes/doc-governance-shapes.ttl` → three derivations in `vocab/queries/docgov-*.rq`.
Run at `9eb5cd0`: **4 passed, 2 warnings**, 29.65 s.

### 1.2 The per-page decimal census — the measurement that refutes the page scope

`for f in $(git ls-files docs/wiki); do grep -oE '[0-9]+\.[0-9]+' "$f"; done`, at `9eb5cd0`:

| wiki page | decimals | `staleAgainstCode` today | distinct values |
| --- | --- | --- | --- |
| `concepts/data-grid.md` | 16 | **yes** | `0.06068601583113457` `0.35560344827586204` `0.7802` `0.9588` `0.9654553611484971` `0.9706` `1.0` `1.0000` `70.6` `88.6` |
| `concepts/table-holon-compilation.md` | 7 | **yes** | `0.9560` `0.9655` `1.0` `89.4` |
| `concepts/neurosymbolic-exemplars.md` | 10 | no | `0.0698` `0.1` `0.1895` `0.6289` `0.9047` `0.99` `1.1` `1.5` `2.1` `3.1` |
| `concepts/dimension-split.md` | 9 | yes | `0.0698` `0.1` `0.3` `0.9047` `0.99` `4.0` `4.2` `4.3` |
| `concepts/corpus-harness.md` | 1 | yes | `254.1` |
| `concepts/grounding-membrane.md` | 1 | yes | `0.00005` |
| `concepts/decision-holon.md` | **0** | yes | — |
| `concepts/promotion-decision.md` | **0** | yes | — |
| `sources/hga.md` | **0** | yes | — |
| `concepts/assert-propose-promote.md`, `concepts/doc-governance.md`, `index.md` | 0 | no | — |

**Two independent failures of the page scope are visible in this table**: 3 flagged pages carry no
figure (false positives for R187's purpose), and `neurosymbolic-exemplars.md` carries **two**
superseded corpus scores (`0.1895`, `0.9047`) while not being flagged at all (a false negative).
The signal and the defect are orthogonal.

### 1.3 The class is repo-wide, not wiki-only — already measured, re-verified here

`the-two-counts` §2 finding 1 said R187's stated scope is wrong. Re-verified at `9eb5cd0`
(`git grep -n 0.9654553611484971`), the superseded stem score is stated as fact in **three
non-Evidence, non-wiki places**:

```
src/iladub/etkl/compile.py:1288   … leaves the stem document byte-identical at 0.9654553611484971.
src/iladub/etkl/compile.py:1302   … 0.9654553611484971. Pinned by tests/test_corpus_stem.py::
tests/etkl/test_datagrid.py:1085  … the whole stem is one chain of 3, 2152 cells, at 0.9654553611484971.
```

`tests/test_corpus_stem.py:358,416` also carry the figure and are **not** defects: both name the
supersession explicitly (`"the pinned score moved 0.9654553611484971 -> 0.9658886894075404 at …"`).
That distinction is the whole design, and §3 makes it mechanical.

### 1.4 The corpus baseline at `9eb5cd0` — measured in this session, not transcribed

`compile_document` over every tracked corpus document, one process each, 2026-09-08 at `9eb5cd0`:

```
$ for d in …; do python -c "from pathlib import Path
from iladub.etkl.document import compile_document
r = compile_document(Path('corpus/$d.pdf')); print('$d', repr(r.score), len(r.pages), r.adopted)"; done
```

| document | score at `9eb5cd0` (2026-09-08) | last recorded reading | moved? |
| --- | --- | --- | --- |
| `ag-trade/graincorp-stem-2026-07-31` | `0.9658886894075404` | `0.9658886894075404` (2026-09-05) | no |
| `ag-trade/graincorp-capacity-2026-08-04` | `1.0` | `1.0` (2026-09-05) | no |
| `ag-trade/cbh-stem-2026-08-03` | `0.9095022624434389` | `0.9091940976163451` (2026-09-05) | **YES** |
| `financial/apple-fy2026q3-statements` | `0.71875` | `0.6288659793814433` (2026-09-05) | **YES** |
| `gov-stats/bfs-population-bilan-2023` | `0.40331491712707185` | `0.3464447806354009` (2026-09-05) | **YES** |
| `gov-stats/ons-index-of-services-2026-02` | `0.9719934102141681` | `0.9719934102141681` (2026-09-05) | no |
| `health/who-wfa-boys-zscore-0-5` | `0.9156327543424317` | `0.9095966620305981` (2026-09-05) | **YES** |

`adopted == ()` for all seven, unchanged.

**FOUR OF SEVEN DOCUMENT SCORES MOVED IN THREE DAYS, and no document in this repo records the new
values.** That is the strongest available argument for this spec's subject, and it was not available
to any previous loop, because none of them re-measured. It also settles the predecessor handoff's
action **5d**, carried unmeasured for eight handoffs. The capability claim it repeats —

```
graincorp  0.9654      bfs   0.9401      WHO   0.9096      apple  0.6289
```

— is now measured, and **all four figures are wrong**:

| figure | today | verdict |
| --- | --- | --- |
| `graincorp 0.9654` | `0.9659` | superseded by [[R174]] — already known |
| `apple 0.6289` | `0.71875` | superseded, **newly measured here** |
| `WHO 0.9096` | `0.9156` | superseded, **newly measured here** — 5d called it "never re-measured"; it is now |
| `bfs 0.9401` | `0.4033` | **never was a shipped reading.** It is the score under C3, the marked-content change that `2026-09-01-marked-content-is-not-a-label-handoff.md` §"C3 is reverted rather than narrowed" reverted at `51bdd23`. The line has propagated a figure from a reverted branch through eight handoffs. |

**Note where those four live: in handoffs, which are `evidence` and which §3.4 EXEMPTS.** The most
repeated wrong figure in the repo is in the class this gate does not touch. That is stated here, not
buried, and raised as [[R192]].

---

## 2. Classification under CLAUDE.md §8 — argued for THIS subject

Three decisions, classified before any code:

### D1 — *"which prose literals are corpus-measurement claims?"* → **AXIOM, derivation, open world**

**Not** a regex over decimals, and not a reading judgement. A literal is a corpus-measurement claim
**iff it round-matches a reading recorded in the register** (§3.1) — evidence-positive, monotonic, a
literal is claimed only where support is *present*. The register supplies the extension; nothing
classifies prose. This is what makes the naive-matching defect (`the-two-counts` §2 finding 3:
`0.9655` and `0.9654553611484971` are one quantity) disappear rather than be tuned around.

### D2 — *"is a matching literal admissible?"* → **CONSTRAINT, SHACL, closed world, block-scoped**

The membrane question — may this claim cross into a wiki page — is closed-world over **one markdown
block**: the block either carries the reading's date or it does not. The block is the closure
boundary, exactly as a holon is elsewhere (§8: *"holon-scoped: query-local `NOT EXISTS` closes
within the one holon while the graph stays open"*).

### D3 — *"does literal L, written at k decimal places, denote reading value V?"* → **PROCEDURAL**

Irreducible: it is decidable exact arithmetic over a lexical form — `round(V, k) == Decimal(L)`,
where k is read off L itself. **There is no tolerance and no tuned constant**: the precision is the
author's, not the instrument's. It lives in `docgov_extract.py`, whose module docstring already
justifies raw extraction as the one PROCEDURAL step in this instrument.

**NEURAL is not used and must not be introduced.** Nothing here is perceptual.

---

## 3. Design

### 3.1 The register: dated READINGS, append-only, and it cannot go stale

The instrument needs one input it does not have: **the set of readings ever taken of a corpus
quantity, each with the date it was taken.**

**It records readings, NOT a current value.** This is the load-bearing choice and it is made against
[[R188]]: a register of *current* values goes stale the moment a loop moves a score and forgets to
update it, and a gate reading it then under-fires silently — R188's shape exactly. A register of
*dated readings* is append-only and **every row stays true forever**; a new reading appends and
invalidates nothing.

The consequence is stated rather than hidden: **this design cannot tell the reader which figure is
current.** It can only tell them which figures are *undated claims*. Marking supersession requires a
current-value notion and a keeper for it, and that is deliberately not built here (§4, [[R190]]).

**Where it lives — one fork, and this spec recommends arm A.**

- **Arm A (recommended): extend `tests/corpus-manifest.ttl`** with a structured
  `cor:reading [ cor:value …; cor:readAt …; cor:atCommit … ]` node per document. That file is
  already the corpus's append-only register, already ruled append-only in its own prose
  (*"a rationale silently rewritten is a rationale nobody can audit"*), already carries every figure
  in free text, and is already cited by `corpus-harness.md`. The readings become machine-readable
  facts beside the human rationale that already states them.
- **Arm B: a new `tests/docgov-figures.ttl`** beside `tests/docgov-drains.ttl`. Decoupled, but a
  second register for the same quantities, whose rows would have to be kept in step with the
  manifest's prose by hand.

Arm A costs a `cor:` vocabulary addition (`vocab/internal/corpus.ttl`) and a `tests/corpus-shapes.ttl`
extension; arm B costs neither but adds the duplication R188 warns about. **The plan takes the
decision and records it; it is not the maintainer's to rule** — nothing in either arm changes a
Contract-class file.

### 3.2 Extraction (PROCEDURAL, `docgov_extract.py`)

New facts, emitted for every tracked file the extractor already walks:

- `?occ a dg:FigureOccurrence ; dg:inDoc ?doc ; dg:line ?n ; dg:lexical "0.9655" ; dg:blockDated ?bool`
- `?doc dg:statesReading ?reading` where the lexical form round-matches that reading's value
  **uniquely** (§3.3).

`dg:blockDated` is true when the enclosing markdown block contains an ISO date or a commit sha.
**The block, not the line** — measured reason: `dimension-split.md:87` carries
`(tests/test_cbh_e2e.py, 2026-08-04)` and `:88` carries the figures, so a line-scoped rule would
report a correctly-dated claim as a finding.

### 3.3 The uniqueness rule — a closed-world guard, scoped to the register

A lexical form `L` at `k` decimal places **denotes** reading `R` iff `round(value(R), k) == L` **and
no other registered reading satisfies the same equation**. Ambiguous forms are **not** findings.

This is not a softening; it is the only honest reading — and it is **partly load-bearing already,
measured on the one hard case**. `graincorp-capacity` reads exactly `1.0`, and `1.0` is also how
anyone writes a ratio ceiling:

| lexical | k | rounds capacity `1.0` to | rounds ons `0.9719934102141681` to | unique? |
| --- | --- | --- | --- | --- |
| `1.0` | 1 | `1.0` | **`1.0`** | **no → not a finding** |
| `1.0000` | 4 | `1.0000` | `0.9720` | **yes → a FINDING** |

So uniqueness disposes of `1.0` by itself, and **does not** dispose of `1.0000` — which
`data-grid.md` uses for a hypothetical perfect page score, not for the capacity document. That is a
**true false positive, already located**, and the plan must not ship a hard gate over it. The remedy
this spec proposes is the register marking `graincorp-capacity`'s reading `cor:notQuotable true`
with its reason in the row — an exemption of **exactly one reading of seven**, stated with its size,
which is the discipline [[R188]] asks for and neither of its two instances applied. **O3 is what
decides whether one exemption is enough**; if the census finds more, the disposition drops to
warning and the hard gate waits.

### 3.4 The derivation and the gate

New: `vocab/queries/docgov-undated-figure.rq` (open world, `CONSTRUCT`):

```
?doc dg:statesUndatedReading ?occ
```
— derived where `?occ` denotes a reading and `?occ dg:blockDated false`.

Disposition, by class:

| class | disposition | why |
| --- | --- | --- |
| `wiki` | **HARD FAIL** | R187's subject. A proposition may be freely rewritten; a measurement inside one may not be undated. |
| `evidence` | **exempt** | `docs/superpowers/**` is the dated historical record, and CLAUDE.md now makes it append-only and prospectively binding. A figure there is dated *by the document*. |
| everything else (`src/`, `tests/`, `assertion`, `manual`) | **WARNING this loop** | §1.3 shows 3 real defects there, but the extractor walks tracked **markdown** only today; reaching `.py` comments is a scope expansion the oracle cannot yet bound. See §4. |

### 3.5 The repair this loop must also ship

A hard gate that fires red on merge is not shippable without repairing what it finds. The repair is
**dating the claim, never rewriting the figure** — R187's own deferral column ruled that rewriting a
loop's measured figures in place *"destroys the record rather than dating it."* Expected surface,
from §1.2: `data-grid.md` (3 occurrences of the stem score, 2 apple), `table-holon-compilation.md`
(2), `neurosymbolic-exemplars.md` (2), `dimension-split.md` (0 — already dated). **The plan
measures the exact set from the instrument's own output and repairs precisely that.**

---

## 4. What is NOT done — deliberately

1. **No supersession marking, and no "current value" anywhere.** §3.1 gives the reason. A reader
   after this loop can tell a dated reading from an undated claim; they still cannot tell a live
   figure from a superseded one. Raised as [[R190]].
2. **No `.py`/`.ttl` comment scope.** §1.3's three defects stay open. Raised as [[R189]].
3. **`staleAgainstCode` is neither deleted nor promoted.** §0 refutes it as R187's detector; it is
   not thereby refuted as *itself* (a page whose sources moved is a page worth re-reading). It stays
   a warning, and its 8-of-12 firing rate stays [[R188]]'s subject, not this loop's.
4. **The register covers DOCUMENT-level scores of the seven tracked corpus documents, and nothing
   else.** `data-grid.md`'s `0.9588` / `0.9706` / `0.7802` are **page** scores and
   `table-holon-compilation.md`'s `0.9560` is stem page 0; none is registered, so none is gated.
   That is a deliberate first cut, not an oversight: the seven document scores are the quantities
   R187 named, they are the ones a whole-corpus run re-measures in one pass, and page scores would
   multiply the register by 27 for a class with no measured defect yet. **A consequence the plan must
   state rather than discover:** O2's "does not fire where there is no figure" is easy partly
   *because* the population is small.
5. **No re-measurement of `bfs 0.9401` / `WHO 0.9096` as capability claims.** §1.4 measures them as
   corpus readings; whether the capability sentence in `data-grid.md` is right is 5d's question,
   carried for the ninth handoff.
6. **The maintainer's "struck, not replaced" convention is NOT inherited into `docs/wiki/**`.** The
   2026-09-08 ruling edits § Documentation governance's **Evidence** clause. The predecessor handoff
   §6 extends it to wiki figures in one sentence; that extension is **unverified** (§8) and this
   spec does not depend on it — dating, not striking, is what §3.5 ships.

---

## 5. The oracle — falsifying, two-sided

The handoff's oracle is refuted (§0) and replaced. Every test below must be shown **failing** with
its subject removed (CLAUDE.md § Plan authoring discipline rule 4).

- **O1 — the detector fires where the defect is.** With the register bootstrapped from §1.4, the new
  derivation reports `statesUndatedReading` on **`data-grid.md`, `table-holon-compilation.md` and
  `neurosymbolic-exemplars.md`**, and on those pages it reports the stem, apple and CBH scores. This
  is the oracle that replaces 5b′'s; it is deliberately wider, and §0 says why.
- **O2 — the detector does NOT fire where there is no figure.** Zero occurrences on
  `decision-holon.md`, `promotion-decision.md`, `hga.md` — the three pages `staleAgainstCode` flags
  and R187 has nothing to say about. **This is the anti-promotion guard 5b′ was right to ask for**,
  restated at the level where it is true: the class must narrow, even though it does not narrow to
  two pages.
- **O3 — the false-positive census is MEASURED, not argued.** Every `dg:FigureOccurrence` in the
  whole tracked tree is enumerated and each one classified by hand as denoting a reading or not.
  **A single unexplained false positive blocks the hard gate** and sends the disposition to warning.
  `1.0` / `1.0000` is the known candidate (§3.3).
- **O4 — the block scope is load-bearing.** `dimension-split.md:88` PASSES because `:87` carries the
  date. Move the date out of the block and it must FAIL. This is the falsification for `dg:blockDated`.
- **O5 — precision matching is exact.** `0.9655` denotes the stem's `0.9654553611484971` reading;
  `0.9659` does not. Both directions asserted; no tolerance appears anywhere in the diff.
- **O6 — the suite is green after §3.5's repair**, and `pytest tests/test_doc_governance.py -q`
  reports the new hard test **passing** rather than skipped.

**The falsification hazard, named while it is cheap** — the mirror of 5b′'s: this gate is *supposed*
to be wider than two pages, so "it fires more than expected" is not by itself evidence of a defect.
The discriminator is **O3**: a firing that denotes no reading is a defect; a firing that denotes a
real undated reading is the instrument working. O3 is the test that can actually fail.

---

## 6. Interfaces — signatures and invariants only (plan rule 1)

```python
# tests/docgov_extract.py — PROCEDURAL additions
def figure_occurrences(text: str) -> list[tuple[int, str, bool]]:
    """(line, lexical, block_is_dated) for every decimal literal in a markdown text."""

def denotes(lexical: str, readings: Mapping[Key, Decimal]) -> Key | None:
    """The unique reading whose value rounds to `lexical` at `lexical`'s own precision,
    or None when zero or more than one does. NO tolerance, NO threshold."""
```

**Invariants the implementer must preserve:**

- **I1.** `denotes` uses `decimal.Decimal`, never `float`, and never a comparison with an epsilon.
  A tolerance appearing in this function is a §8 defect by CLAUDE.md's own words.
- **I2.** The register is read, never written, by the instrument.
- **I3.** `extract()` stays a pure fact emitter: no derivation, no membership decision (its docstring
  already binds this and must remain true).
- **I4.** No existing `docgov-*.rq` file changes semantics. The recalibration is **additive**;
  `staleAgainstEvidence` stays hard and `staleAgainstCode` stays a warning (§4.3).

**Seams the plan must MEASURE, not assume** (plan rule 3):

- **S1.** Where `extract()` currently reads file text — the figure walk must not re-read every file a
  second time. Measure the existing read sites before adding one.
- **S2.** ~~Whether `tests/corpus-shapes.ttl` would refuse an unknown `cor:reading` node.~~
  **MEASURED in this session:** `cor:DocumentShape` (`tests/corpus-shapes.ttl:12`) carries no
  `sh:closed`, so the predicate is admissible without a shape change. The seam that remains is the
  *positive* one — a `cor:ReadingShape` requiring value + date + commit is new work, and the plan
  decides whether to write it.
- **S3.** The instrument's runtime. It is 29.65 s today, dominated by `git log -1` per cited source.
  Measure after; a figure walk over every tracked markdown file is new I/O.

---

## 7. Residues to raise

| # | what |
| --- | --- |
| [[R189]] | The figure scope stops at markdown. `src/iladub/etkl/compile.py:1288,1302` and `tests/etkl/test_datagrid.py:1085` state a superseded corpus score as present fact, outside any gate. |
| [[R190]] | Nothing in the tree records which reading of a corpus quantity is CURRENT, so no instrument can mark a figure superseded. §3.1 refuses to solve it with a hand-kept current-value register; the honest alternative is deriving it from a corpus run, which [[R173]] shows CI cannot do. |
| [[R191]] | `the-two-counts` §2's classification is **refuted in one row**: CBH's `0.9047` was counted not-stale and has moved twice. The row exists so the count is not re-cited as a census — it was a reading, and it is dated. |
| [[R192]] | **A handoff asserts CURRENT state in a class this gate exempts.** §1.4 measures the capability line's four figures as four errors, one of them (`bfs 0.9401`) taken from a reverted branch and repeated eight times. The Evidence exemption is justified by *"the document is dated"* — true of a spec, and only half true of a handoff, whose part 5 is a claim about the tree as it stands. Whether that class should be gated is a design question, not a lint. |

---

## 8. Unverified or assumed

- **The 2026-09-05 rebaseline table is superseded on FOUR of its seven rows** (§1.4). Anything read
  from that table instead of §1.4 is a stale citation — **and §1.4 will be one within days**, which
  is the point rather than a caveat: it is a dated reading, and it says so.
- **`corpus-harness.md`'s `254.1` and `grounding-membrane.md`'s `0.00005` are assumed non-readings**
  on inspection, not by the register. O3 is what converts that assumption into a measurement.
- **The wiki extension of the maintainer's "struck, not replaced" ruling is NOT established** (§4.5).
  The predecessor handoff asserts it; the CLAUDE.md text it cites is about the Evidence class.
- **UNKNOWN figures stay unknown.** `the-two-counts` §2 recorded `88.6` / `70.6` in `data-grid.md` as
  appearing nowhere else in the tree. This design does not reach them: no reading, no denotation, no
  finding. That is the honest limit of a register-driven detector and not a defect of it.
- **The full suite was not run in this session.** Only `tests/test_doc_governance.py` (4 passed,
  2 warnings, 29.65 s) and seven single-document `compile_document` calls.
