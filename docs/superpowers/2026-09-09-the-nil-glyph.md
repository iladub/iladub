# Loop record — the nil glyph: `—` is a missing value, and the spellings moved into the ontology

**Residue:** [[R167]]. **Branch** `r167-the-nil-glyph`, off `3fe0ce2`. **2026-09-09.**
Spec: `docs/superpowers/specs/2026-09-09-the-nil-glyph-design.md`.

**Doc impact: increment.** New published vocabulary (`tab:nilSpelling`) and a rewritten
`tab:Blank` comment.

---

## 1. What was wrong

`celltype.is_blank` recognised `''`, `(blank)` and the ASCII `-`. The em-dash U+2014 — US-GAAP's
nil glyph and the typographically-correct spelling of the very hyphen already accepted — typed as
`tab:Text`. Because `tab:Blank` carries `tab:datatypeAbstains true` and `tab:Text` does not, one
nil cell **voted** in every homogeneity derivation instead of abstaining, and a single vote
disqualifies a whole column from `stub-data-split.rq`'s data suffix.

## 2. The population, and the honest size of this loop

**MEASURED 2026-09-09 at `3fe0ce2`**, all eight Unicode dashes, every page of all seven tracked
corpus documents, `pdfplumber.extract_words`:

```
apple-fy2026q3-statements.pdf  p2  EM-DASH  U+2014  x1
… 68 further hits, ALL of them the ASCII hyphen U+002D that is_blank already accepted
TOTAL: EM-DASH 1, EN-DASH 0, every other dash 0
```

**One instance, and it is inert.** Compiling apple page 2 and searching the emitted graph for any
literal containing U+2014 gives **0 hits**: the cell sits on a band that escalates
(`REGION_TILING_FAILED`), so no wrong assertion crosses the membrane today.

This is stated first because it is what a reader most needs and what a loop is most tempted to
bury. **The fix is licensed by the epistemics, not by a score**: a nil marker typed as text is a
false datatype assertion (§7), and the corpus is a seven-document sample that happens to contain
one US filer.

## 3. The blast radius was ENUMERATED, and R167's own row was wrong about it

R167 records *"a one-line change to a function four modules read (`feed.py:222`,
`datagrid.py:274,331`, `celltype._cell_datatype`)"*. Four modules is right; the call-site list is
not — `datagrid.py:274` is a comment, and `unitmarker.py:43` plus `datagrid.py:443,517,525,563`
are missing. The real population is **eight call sites in four modules**, and one further
enumeration was run to be sure the recogniser is the only one:

```
$ grep -rn "'-'\|\"-\"\|'—'\|\"—\"\|'–'\|\"–\"" --include='*.py' src/
… 6 hits, every one a URI slug, a split, or an ASCII rule render — no nil-marker comparison
```

**`celltype.is_blank` is the sole nil-marker recogniser in `src/`.**

All three importers use `from .celltype import is_blank`, so the name is bound per module at
import: **monkeypatching `celltype.is_blank` reaches only `_cell_datatype`**, which is why O4
takes its two readings in two processes rather than by patching one.

## 4. The change

**The spelling set moved out of Python and into the published ontology** (spec §4 arm (b)). The
argument is not aesthetic: `tab:Blank`'s CC-BY `rdfs:comment` already enumerated the set in prose,
so extending only the Python would have made the published contract false. `tab:CellDatatypeFamily`'s
own comment, in the same file, already rules against stating a rule in two places, and `celltype.py`
already parses `tab.ttl` at import — so reading the set costs a filter over a graph in memory.

```
vocab/ontology/tab.ttl   tab:nilSpelling a owl:DatatypeProperty ; rdfs:domain tab:CellDatatype ;
                                           rdfs:range xsd:string .
                         tab:Blank tab:nilSpelling "(blank)", "-", "–", "—" .
src/iladub/etkl/celltype.py   _NIL_SPELLINGS = frozenset(… _ONT.objects(TAB.Blank, TAB.nilSpelling))
                              is_blank:  return t == "" or t.lower() in _NIL_SPELLINGS
```

**Gate classification (CLAUDE.md §8): unchanged, PROCEDURAL.** Raw datatype typing from lexical
form is raw extraction, already justified in `celltype.py`'s module docstring; the decisions built
on it stay AXIOM in `vocab/queries/*.rq`. Arm (b) moves the *data* the recogniser reads, not the
class of the decision. No tuned constant: the set is closed, typographic and decidable.

**A defect this loop committed against itself, and repaired.** The first draft of
`tab:nilSpelling`'s own `rdfs:comment` listed the four members in prose — reintroducing, one term
away, exactly the drift being removed from `tab:Blank`. It now fixes the RULE (equality on the
stripped text, case-insensitive, never a substring) and the BOUNDARY (the hyphen and its
typographic variants plus `(blank)`; suppression markers excluded), and says outright that the
members are the triples.

**Blank, deliberately, and NOT zero.** In US-GAAP the em-dash means "nil", which invites the
reading *"type it `tab:Numeric` with value 0"*. That would be a fabrication: the source wrote a
glyph meaning *nothing here*, and §7 permits emitting only what the source supports. `tab:Blank`
asserts absence of a datum, not a value — and because it carries `tab:datatypeAbstains`, the cell
takes no part in any homogeneity judgement either way. This is also what makes the change safe
across the ambiguity [[R78]] guards: whether a particular author's `—` means *zero* or *not
applicable*, "no value is asserted here" is true under both readings, and neither is invented.

**What is NOT mechanically enforced, stated rather than hidden:** the general property *"no comment
enumerates the members"* is not expressible as a test — `-` and `—` occur constantly in ordinary
prose, so any string-absence check is either brittle or vacuous. The shipped test pins the ONE
comment that was actually wrong (`tab:Blank`'s), and the general form is a norm. Same shape as the
unexpressible fork arms recorded in [[R179]], [[R181]] and [[R182]].

## 5. The oracles

O1–O3 ship as `tests/etkl/test_nil_glyph.py` (6 tests). **Falsification, per CLAUDE.md § Plan
authoring discipline rule 4 — each inverted, run, and restored:**

| # | inversion | result |
| --- | --- | --- |
| F1 | delete the two new `tab:nilSpelling` triples from `tab.ttl` | **3 RED** — proves the ontology is the source and the code keeps no fallback literal |
| F2 | revert `is_blank` to the hard-coded literal set | **2 RED** |
| F3 | widen the match from equality to containment | **1 RED** — the [[R78]] boundary |
| F4 | the whole baseline tree, `git stash`ed during the O4 run | **1 RED, `assert 2 == 1`** |

**F4 is the strongest of the four and it was free.** O4 stashes the three tracked edits to take its
baseline reading, so for the duration of that run the working tree IS the pre-loop tree — the exact
condition a falsification wants. `test_one_nil_cell_no_longer_disqualifies_its_column_from_the_data_suffix`
run against it returns **k=2**, which is the value R167 measured on apple p2's merged reading — so
that measurement is now **reproduced on a synthetic three-column grid, without the corpus**, and the
pin is demonstrably non-vacuous. This is the pin that matters: O1–O3 check the typing, F4's test
checks the *consequence* the residue was raised about, and it is the only one of the five that can
run in CI on a tree with no `corpus/` ([[R173]]).

`tests/etkl/test_celltype.py`'s frozen anti-overfit reference `_is_blank_shaped` was updated **from
the spec's stated rule, never by importing `_NIL_SPELLINGS`** — importing the set under test would
make the differential compare the code against itself.

## 6. O4 — the whole-corpus before/after: 27 of 27 pages byte-identical

**RUN 2026-09-09 at `3fe0ce2`**, two processes over the same checkout — the `after` reading from
this loop's tree, the `before` reading with the three tracked edits `git stash`ed — via
`scripts/corpus_verdict_snapshot.py`. The comparison is over every recorded field AND a canonical
SHA-256 of the whole merged graph, not over scores alone:

```
document                          score (before == after)   graph
apple-fy2026q3-statements         0.71875                   IDENTICAL
bfs-population-bilan-2023         0.40331491712707185       IDENTICAL
cbh-stem-2026-08-03               0.9095022624434389        IDENTICAL
graincorp-capacity-2026-08-04     1.0                       IDENTICAL
graincorp-stem-2026-07-31         0.9658886894075404        IDENTICAL
ons-index-of-services-2026-02     0.9719934102141681        IDENTICAL
who-wfa-boys-zscore-0-5           0.9156327543424317        IDENTICAL

O4: ALL DOCUMENTS BYTE-IDENTICAL — 7 documents, 27 pages
```

**The spec graded O4 PROPOSED and predicted exactly this**, apple p2 included, on the strength of
§2's finding that the one em-dash sits on an escalated band. The prediction is discharged, and it
could have failed: a single moved reading anywhere would have meant the flip reached a path §3's
enumeration did not anticipate, and the spec bound the loop to explain it rather than re-baseline.

**Two things this run establishes beyond O4 itself.**

1. **The graphs are deterministic across processes.** Identical hashes on two independent runs mean
   nothing in the emitted graph carries a timestamp or a run-dependent identifier — which is what
   makes a canonical hash a usable oracle here at all, and was not known before this loop.
2. **All seven document scores still read what [[R190]] measured on 2026-09-08.** No corpus figure
   moved in the intervening day. That is a datum for [[R190]] and [[R191]] — both are about figures
   moving unrecorded — and it is recorded here rather than in either row, because a single
   re-reading is evidence, not a current-value register (which [[R190]] explicitly forbids).

## 6.1 A trap this loop walked into — the THIRD form of phantom green

The affected-suite run was first launched as `timeout 3500 .venv/bin/python -m pytest …`. **macOS has
no `timeout` binary** (it is GNU coreutils), so the command failed with
`(eval):1: command not found: timeout` — **and the harness reported exit code 0**. A run that executed
nothing was indistinguishable from a green one, and was caught only by reading the output file instead
of the exit status.

This is the third distinct shape of the same failure recorded in this repo: a stalled background suite
reported green (`sdd-loop-process-findings`), pytest rejecting a flag and running nothing ([[R198]]'s
loop), and now a missing wrapper binary. The common cause is identical every time — **an exit code was
read where output should have been.** Never wrap a verification command in `timeout` here, and never
report a suite result without a real `N passed` line.

## 6.2 CI found a test the loop's own reach analysis missed — and it is the closure's best evidence

**PR #188's first CI run went RED**, on
`tests/test_one_band_matrix_spike.py::test_the_em_dash_types_as_text_while_the_ascii_hyphen_types_as_blank`.

That test is a **detector for R167 itself** — the R165 spike wrote it to pin the defect *"as it
stands today"*, with the ASCII `-` as its falsifying twin. Closing R167 correctly turns it red, so
the failure is not a regression: **it is the independent confirmation that the repair reached the
behaviour the residue was raised about**, from a test this loop did not write.

Two things it exposes, both worth keeping:

1. **The pre-push subset run was chosen by SOURCE reach, not TEST reach.** §3 enumerates every
   reader of `is_blank`, and the modules were right — but the subset was `tests/etkl` plus named
   top-level files, and this detector lives in `tests/test_one_band_matrix_spike.py`, which names
   none of those modules in its path. Enumerating the callers of a function does not enumerate the
   tests that assert about it. The remedy is not a better subset heuristic: it is running the full
   suite, which is what was done after this.
2. **The inverted pin's twin had to move, not just its assertion.** The old twin was the ASCII `-`
   — same grammar, opposite answer — which separated only while the classifier *disagreed* about
   the two glyphs. With all three now `tab:Blank`, that twin would pass against a classifier that
   returned `tab:Blank` for everything, i.e. it would be **vacuous**. The twin is now a dash inside
   other text (`'2020—2024'` is ink, not absence), which is the same boundary O3 guards. Re-baselining
   an inverted pin without re-checking its falsifier is how a test survives as decoration.

## 7. What this loop did NOT do

[[R162]] (unruled header labels are words, NEURAL) is untouched, so apple p2 still refuses.
[[R166]]'s p2 half is untouched and was measured to be **worse than its row records** — see the
handoff's part 5b, which carries the three asserted labels and the refutation of the remedy R166's
own close criterion invites. [[R78]] stays distinct: suppression markers are *unknown*, not
*absent*. No SHACL shape ships over `tab:nilSpelling` — spec §6 states why.

