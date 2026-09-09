# Handoff — the nil glyph: `—` is a missing value, and the spellings moved into the ontology

**Topic:** [[R167]]. Branch `r167-the-nil-glyph`, off `3fe0ce2`.
**Written 2026-09-09**, part 5 first, before the loop's own O4 had returned.

**Doc impact: increment.** `tab:nilSpelling` is new published vocabulary; `tab:Blank`'s comment
stopped enumerating the nil markers in prose and now points at the triples.

---

## 5. The next concrete action

### 5a. ASSERTED — R167's remedy generalises; do NOT re-open it on corpus-reach grounds

The loop's own §2 measurement is the thing a future session is most likely to misread: **the
corpus contains exactly one em-dash and zero en-dashes, and that one cell sits on an escalated
band**, so the fix moves no corpus reading. That is a fact about *this seven-document corpus*,
not about the fix. The em-dash is US-GAAP's nil glyph; a corpus with a second US filer in it
would exercise it on every statement page.

**What a future loop must NOT do:** propose reverting, narrowing, or re-litigating the spelling
set because "it changed nothing on the corpus". The oracle that licenses the change is O1–O3
(the glyph is a missing value, matched by equality, from a declared set), not a score movement.
The register's own anti-overfitting rule points the same way: a fix is judged by whether it
generalises, and a corpus is a sample.

**Why asserted:** the outcome is on disk and reproducible — §2 names all four falsifications, three
of which run in seconds; F4 needs the baseline tree, which O4's own `git stash` produces.

### 5b. PROPOSED — the next subject is [[R166]]'s surviving half, and it is LIVE

This is a prediction that must be RUN and can fail; budget for refutation.

While measuring §2 this loop compiled apple page 2 at `3fe0ce2` and got R166's live half for
free. **Band 6 is the page's ONLY asserted band, 3 cells, and it is worse than R166 records.**
Measured 2026-09-09 at `3fe0ce2`, the three `tab:LabelCell`s it asserts as the column header are:

```
table6-lc0  'Increase in cash, cash equivalents, and restricted cash and cash equivalents'
table6-lc1  '3,610'
table6-lc2  '6,326'
```

R166's row names only the sentence. **The other two labels are DATA** — `3,610` and `6,326` are
asserted as column labels, so the reading does not merely mislabel the band, it converts two real
values into header text. The body is the single row
`'Cash, … ending balances' | '$ 39,544' | '$ 36,269'`. This is a §7 false assertion standing inside
the membrane today — the most serious defect class this repo names — and unlike R167 it is not
inert.

**AND THE OBVIOUS REMEDY IS ALREADY REFUTED — do not spend a loop rediscovering this.** R166's own
close criterion is *"assert under a non-numeric header or escalate"*, which reads as a licence for
the rule *a numeric column label is not a header*. That rule is **wrong**, and decidably so: a table
headed `2023 | 2024` has numeric labels and is the single most common financial-statement header
there is (`is_numeric('2023')` is `True`). A gate on label numeracy would refuse correct readings
across the corpus. The separating signal is therefore NOT the label's datatype.

**The prediction, and what would refute it:** that R166's p2 half is repairable *independently*
of [[R162]]. R166's own row says the opposite — *"fixing them separately from R165 would be
fixing the symptom"* — and [[R165]]'s p2 merge is refused on [[R162]], which is ruled NEURAL. So
the cheap check comes first: **read what band 6 asserts today, then ask whether any decidable
signal distinguishes it from a real header without a tuned constant.** If the only separator is
"this header looks like a sentence", the answer is NEURAL-with-an-oracle, not an axiom, and the
loop is a design fork rather than a fix.

**Do not start by writing code.** The cells above are already printed; start from them and from
the refuted remedy, and let the answer to *"what decidable signal separates this from a year-headed
table?"* choose the loop's shape. If the honest answer is "none from format alone", the loop is a
NEURAL proposal disposed by an oracle (CLAUDE.md §8), not an axiom — and saying so with the
measurement above is a complete loop outcome, not a failure.

### 5c. ASSERTED — [[R78]] stays distinct and must not be folded in

`n/a`, `..` and `c` are *suppression* markers: the value is unknown, not absent. Nothing in this
loop licenses widening `tab:nilSpelling` toward them, and `test_a_dash_inside_other_text_is_not_a_missing_value`
plus the property's own published comment are the record of that boundary. A future loop that
wants them must argue the epistemics (unknown ≠ missing), not the convenience.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the design, the fork and every measurement | `docs/superpowers/specs/2026-09-09-the-nil-glyph-design.md` | §2 the population census and the inertness probe; §3 the ENUMERATED blast radius (R167's own call-site list is wrong); §4 why the ontology arm was taken; §5 the four oracles |
| the loop record | `docs/superpowers/2026-09-09-the-nil-glyph.md` | O4's result and the three falsifications |
| the change itself | `vocab/ontology/tab.ttl` (`tab:nilSpelling`), `src/iladub/etkl/celltype.py` (`_NIL_SPELLINGS`, `is_blank`) | that the Python side holds NO literal spelling — deleting a triple turns three tests RED |
| the oracles | `tests/etkl/test_nil_glyph.py` | O1–O3 and the two ontology-is-the-source tests |
| the O4 instrument | `scripts/corpus_verdict_snapshot.py` | why the two readings cannot be taken in one process |
| the finished row | [[R167]] in `residues-closed.md` | the closure evidence |

## 2. What changed

One branch, `r167-the-nil-glyph`, off `3fe0ce2`.

- **Vocabulary:** `tab:nilSpelling` (`owl:DatatypeProperty`, domain `tab:CellDatatype`, range
  `xsd:string`) with four values on `tab:Blank`; `tab:Blank`'s `rdfs:comment` rewritten to point
  at them instead of enumerating them.
- **Code:** `celltype._NIL_SPELLINGS` reads those triples from the `tab.ttl` parse that module
  already did at import; `is_blank` tests membership instead of three hard-coded comparisons.
- **Tests:** `tests/etkl/test_nil_glyph.py` (7 tests); `tests/etkl/test_celltype.py`'s frozen
  anti-overfit reference `_is_blank_shaped` updated **from the spec's rule, not by importing the
  set under test** — importing it would make the differential compare the code against itself.
- **Instrument:** `scripts/corpus_verdict_snapshot.py`, committed (O4 is load-bearing and must
  stay reproducible).
- **One detector INVERTED, after CI found it:**
  `tests/test_one_band_matrix_spike.py::test_the_em_dash_types_as_text_while_the_ascii_hyphen_types_as_blank`
  pinned R167 *"as it stands today"*, so the closure turned it red — independent confirmation from a
  test this loop did not write. Its falsifying twin was MOVED as well as its assertion: the old twin
  (the ASCII `-`) stops separating once all three glyphs agree. Loop record §6.2.

**Falsification, all three run and restored:**

| # | inversion | result |
| --- | --- | --- |
| F1 | delete the two new `tab:nilSpelling` triples | 3 RED |
| F2 | revert `is_blank` to the hard-coded literal set | 2 RED |
| F3 | widen the match from equality to containment | 1 RED |
| F4 | the whole baseline tree (the `git stash` O4 takes anyway) | 1 RED, `assert 2 == 1` |

**F4 is the one to read.** O1–O3 pin the typing; F4 pins the CONSEQUENCE — the stub\|data split
returning k=2 instead of k=1 — which is what R167 was actually raised about, and it reproduces that
apple measurement on a synthetic grid, so it runs in CI on a tree with no `corpus/` ([[R173]]).

## 3. What was decided, and where that decision is recorded

- **The spelling set lives in the ontology, not in Python.** Spec §4, arm (b). Ground: `tab:Blank`'s
  published CC-BY comment already enumerated the set in prose, so a Python-only fix would have made
  the published contract false — and `tab:CellDatatypeFamily`'s own comment, in the same file,
  already rules against stating a rule in two places.
- **The gate classification does not change.** Spec §4. Raw datatype typing stays PROCEDURAL
  (`celltype.py`'s module docstring); arm (b) moves the *data* the recogniser reads, not the class
  of the decision. No tuned constant is introduced — the set is closed, typographic and decidable.
- **The empty cell is not a declared spelling.** Spec §4. Absence of ink is structural; a marker is
  something an author writes.
- **This loop closes R167 and nothing else.** Spec §6. [[R162]], [[R166]] and [[R78]] are untouched
  and each says so in its own row.

## 4. Unverified or assumed

- **O4 RAN and CONFIRMED its prediction** (loop record §6): 7 documents, 27 pages, every canonical
  graph hash identical. It was written into part 5 while still running and is no longer unverified.
  It also establishes, as a side effect, that the emitted graphs are deterministic across processes.
- **The canonical graph hash normalises blank-node labels away** (`scripts/corpus_verdict_snapshot.py`,
  `_canonical_hash`). Two graphs differing ONLY in how blank nodes are shared would hash alike. Stated
  in the docstring rather than hidden; the summary fields beside the hash carry the reading itself.
- **The pre-push subset was chosen by SOURCE reach and was INCOMPLETE** — CI caught a detector in
  `tests/test_one_band_matrix_spike.py` that the subset never ran (loop record §6.2). The full suite
  was run afterwards; its result is in the loop record. **Do not repeat the subset heuristic**:
  enumerating a function's callers does not enumerate the tests that assert about it.
- **The dash census is over `pdfplumber.extract_words`, not over cells.** A standalone word is a
  proxy for a whole-cell text: it is exact wherever a cell is one word, and a cell whose text joins
  a dash to other words is not a nil cell anyway. No cell-level census was run.
- **`tab:nilSpelling` is read at import and never emitted into a document graph**, so the R61/[[R184]]
  domain/range probe has no instance of it to check. Its domain/range are consistent within `tab.ttl`
  itself and that is all that was verified.
