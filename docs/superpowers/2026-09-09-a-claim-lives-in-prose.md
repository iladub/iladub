# A claim lives in prose — the code-scope figure gate, and the refutation of the answer it was given

**Topic:** action **5a** of `docs/superpowers/2026-09-09-a-figure-at-the-end-of-a-sentence-handoff.md`,
graded PROPOSED: settle [[R196]](a) as a design question, then extend the walk and the gate in ONE
change. Both taken. Spec: `docs/superpowers/specs/2026-09-09-a-claim-lives-in-prose-design.md`.

**Written 2026-09-09.** The candidate answer 5a named is **REFUTED by measurement**, and the
measurement licensed a different change that ships HARD. [[R196]] CLOSED on (a), amended on (b).

**Doc impact: none.**

---

## 1. The question was answered wrong, and the corpus says so

[[R196]](a) proposed that in a `.py` file the closure boundary for datedness should be **the whole
comment run or docstring**, on the ground that a block "invents findings". 5a required it be measured
against the markdown rule, and named the failure condition in advance.

**MEASURED at `6141bcd`, over 294 tracked `.py` files**, shipped instrument functions unmodified:

| rule | occurrences | undated | of the 4 findings |
| --- | --- | --- | --- |
| shipped **block** (whole file) | 44 | 16 | **4/4** |
| candidate **comment-run / docstring as the unit** | 20 | 7 | **3/4** |
| **prose region + block inside it** (shipped here) | 20 | 10 | **4/4** |

The candidate **loses a real finding**. `tests/etkl/test_datagrid.py:1085` states the superseded stem
score as a present fact inside a 32-line docstring whose *first* paragraph carries `spec 2026-08-09
§5.1` and `RE-POINTED 2026-09-02` — dates about the test's re-pointing, ten lines up and about
something else. Widen the boundary and that date absolves the claim.

A docstring is **longer** than a markdown paragraph, so it is a weaker boundary, not a better-fitting
one. R196(a)'s premise is inverted: the block does not invent findings in code, widening it **hides**
them. The shipped wiki gate had already written the principle down —

> put it in a neighbouring block and this test still fails, which is the point of the block scope

### 1.1 And its one measured false positive is a finding

R196(a) rests on `tests/etkl/test_adoption_document.py:369`:

```python
    """Measured before this loop: 0.06068601583113457, and 0.35560344827586204 after.
```

The dates two paragraphs down (`2026-09-05`, `2026-09-07`) date *later* readings — `0.6288…`,
`0.71875` — not these. Both figures are superseded (register: **2026-08-09**), and the phrase that
dates them is *"before this loop"*, which no reader can resolve. **Reclassified: a finding.** That is
a judgement against the rule the shipped gate enforces, not a new measurement, and it overturns rows
5-6 of the predecessor loop's hand census.

## 2. What the measurement DID license — the region, not the boundary

The candidate bundled two independent changes. Separating them is the whole content of this loop.

- **Which regions carry a claim — CONFIRMED.** In markdown every line is prose; in `.py` prose is
  comments and docstrings. `STEM = Decimal("0.9654553611484971")` states nothing a reader could date.
  Restricting the walk drops **24 of 44** occurrences, **6 of them undated** — every one a fixture
  literal in code — and **loses zero findings**.
- **What the boundary is inside a prose region — REFUTED.** It stays the block.

> **A claim lives in prose; the block is where its date must live.** The substrate decides which
> regions are prose. The boundary inside one is the same everywhere. Markdown is the case where the
> prose region is the whole file.

A comment run has no blank lines, so its paragraph break is a line bearing `#` and nothing else. The
extractor blanks the `#` while preserving every column, which gives a comment run the same paragraph
structure markdown gets for free — and pins it with a test, because without it a comment that dates
its first paragraph would absolve every figure below it: the refuted defect, wearing the other syntax.

## 3. What shipped

- `tests/docgov_extract.py`: `prose_regions_py` (comment runs via `tokenize`, docstrings via `ast` —
  **exact, not heuristic**; Python's own grammar decides, so there is no tolerance and no tuned
  constant), `prose_blocks_py` (`blocks` inside each region), `tracked_python`, and the `.py` walk in
  `extract()`. `_figure_facts` now takes **units** rather than text — the one change that makes the
  substrate's choice of unit visible at the call site. `is_dated`, `denotes`, `_DECIMAL` and
  `separating_precision` are untouched.
- `vocab/internal/docgov.ttl`: `docgov:SourceFile` declared; **`docgov:docClass`'s `rdfs:domain`
  removed**, measured before removing it (§4).
- `vocab/shapes/doc-governance-shapes.ttl`: `dg:SourceFileShape`, with a positive and three negative
  tests.
- `vocab/queries/docgov-undated-figure.rq`: **unchanged.** It already reads `?doc dg:docClass ?class
  . FILTER (?class != "evidence")`, so `"code"` derives findings with no edit to the AXIOM.
- `tests/test_doc_governance.py`: `test_no_source_file_states_an_undated_reading` — **HARD**; the
  old non-wiki warning narrowed to the classes neither gate covers.
- **Ten repairs**, all by DATING the claim, none by rewriting a figure (§5).

## 4. The entailment that had to be measured, not reasoned

A source file is deliberately **not** a `dg:Document`: it has no class by location, is never in the
nav, is never published. But it must carry `dg:docClass "code"` for the derivation to reach it, and
`docgov:docClass` declared `rdfs:domain docgov:Document`. Under the lint's `inference="rdfs"` run
that entailed every source file into `dg:Document`, where `dg:DocumentShape` failed it **three ways**
— the `sh:in` list, `dg:inNav`, `dg:excludedFromSite` — for being a `.py` file rather than for any
defect. Measured before the fix and pinned after it
(`test_a_source_file_is_not_entailed_into_a_document`, which goes RED if the domain returns).

`docgov:path` had already written the argument for exactly this case, one property above.

## 5. The disposition is HARD, and the licence is the pre-repair census

The wiki gate ships HARD on **0 false positives in 11**. The code census measures **10 undated, 6
findings and 4 false positives** — and all 4 are in `tests/test_docgov_extract.py`, in the figure
gate's **own docstrings**, where the prose must quote figures to say what the gate discriminates.

All ten were repaired the way [[R187]] prescribes — **date the claim, never rewrite the figure**:

| site | reading | dated with |
| --- | --- | --- |
| `src/iladub/etkl/compile.py:1288, 1302` | stem `0.9654553611484971` | `(read 2026-08-20)` |
| `tests/etkl/test_datagrid.py:1085` | same | `(read 2026-08-20)` |
| `tests/etkl/test_membrane_health.py:429` | `0.9655` | `(read 2026-08-20)` |
| `tests/etkl/test_adoption_document.py:369` ×2 | apple `0.0606…`, `0.3556…` | `Measured 2026-08-09:` |
| `tests/test_docgov_extract.py:153` ×2, `154`, `163` | stem, apple | the readings' own dates |

**No exemption list was introduced.** An exemption is a coverage loss dressed as a fix — the shape
[[R188]] exists for — and the honest repair was available and cheaper. **No figure's value was
edited**; a reflow that dropped one repeated mention of `0.9659` was reverted so that the occurrence
count after repair (21) differs from before (22) by nothing but the repairs' own added dates.

**The licence for HARD is §1's census, taken before the repair.** [[R187]]'s recorded trap is that a
gate with nothing to find is indistinguishable from a clean tree; the table is what distinguishes
them here.

**FALSIFICATION.** Reverting one repair — the `(read 2026-08-20)` at `compile.py:1288` — turns the
new gate RED with the exact site and the reading's dates:

```
src/iladub/etkl/compile.py:1288  `0.9654553611484971` is a reading of
graincorp-stem-2026-07-31, taken 2026-08-03/2026-08-20
```

Restored; green. The gate fires.

## 6. [[R196]](b) does NOT become live — its row said it would

R196 asserts of both halves: *"Both become live the moment the scope extends to code."* **Measured
2026-09-09 and refuted for (b):** over every `.py` prose block, the count of denoting occurrences
whose block is dated ONLY by a date inside a letter-bearing token (a filename) is **0**. The corpus
PDFs are named `graincorp-stem-2026-07-31.pdf` and `cbh-stem-2026-08-03.pdf`, so the hazard is real
in principle; no `.py` prose block relies on one. (b) stays deferred, now on two corpora.

## 7. What is NOT done

- **`.ttl` / `.rq` prose regions.** One undated occurrence across 203 files, a false positive, zero
  findings — against writing a Turtle lexer that tells a `#` comment from the `#` in an IRI and from
  one inside a string literal. Raised as [[R197]].
- **[[R196]](b).** §6.
- **A mention-vs-report reader ([[R194]] arm 1).** Not needed here: the prose restriction removed 6
  of the 11 mentions, and the remaining 4 were repaired by dating. R194's population falls 11 → 4.
