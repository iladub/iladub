# A claim lives in prose — extending the figure gate to Python source

**Topic:** action **5a** of `docs/superpowers/2026-09-09-a-figure-at-the-end-of-a-sentence-handoff.md`,
graded PROPOSED: settle [[R196]](a) — *what is the closure boundary for datedness in a source file?* —
as a design question, then extend the walk and the gate in one change.

**Written 2026-09-09.** The question is settled by measurement, and **the candidate answer 5a named
is REFUTED**. A second measurement refutes [[R196]]'s own deferral ground for its (b) half.

**Doc impact: none.**

---

## 1. The question, and why the given answer is wrong

[[R196]](a) records that `is_dated` scopes datedness to a **block** — a maximal run of non-blank
lines — and proposes that in Python the unit should instead be **the whole comment run or docstring**,
because that is "what a `.py` author actually writes". 5a required the candidate be *measured against*
the markdown rule rather than replacing it. It was. It loses.

**MEASURED 2026-09-09 at `6141bcd`**, shipped instrument functions unmodified (`blocks`, `is_dated`,
`denotes`, `load_readings`, `separating_precision`, `_DECIMAL`), register as shipped (18 readings, 1
`cor:notQuotable`, `sep = 4`), over `git ls-files '*.py'` — 294 files:

| rule | occurrences | undated | of R189's 4 findings |
| --- | --- | --- | --- |
| shipped **block** (whole file) | 44 | 16 | **4/4** |
| candidate **comment-run / docstring as the unit** | 20 | 7 | **3/4** |
| **prose region + block inside it** | 20 | **10** | **4/4** |

**The candidate loses a real finding, and it loses it for the exact reason the block rule exists.**
`tests/etkl/test_datagrid.py:1085` states the superseded stem score `0.9654553611484971` as a present
fact. It sits in a 32-line docstring whose *first* paragraph carries `spec 2026-08-09 §5.1` and
`RE-POINTED 2026-09-02` — dates about the test's re-pointing, ten lines above and about something
else. Widen the boundary to the docstring and that unrelated date silently absolves the claim.

This is the shipped wiki gate's own stated principle, verbatim
(`tests/test_doc_governance.py::test_no_wiki_page_states_an_undated_reading`):

> The date belongs in the figure's own markdown block — put it in a neighbouring block and this test
> still fails, which is the point of the block scope.

A docstring is *longer* than a markdown paragraph, not shorter, so it is a **weaker** boundary, not a
better-fitting one. [[R196]](a)'s premise — that the block boundary "invents" findings in code — is
the reverse of what the corpus shows: widening it **hides** them.

### 1.1 And the false positive it was raised to fix is a finding

[[R196]](a)'s single measured instance is `tests/etkl/test_adoption_document.py:369`, whose block
(367-369) is undated while "the enclosing docstring dates itself twice, two paragraphs down". Line 369
reads:

```python
    """Measured before this loop: 0.06068601583113457, and 0.35560344827586204 after.
```

The dates two paragraphs down (`2026-09-05`, `2026-09-07`) date *later* readings — `0.6288…` and
`0.71875` — not these two. The sentence dates itself with the phrase **"before this loop"**, which no
reader can resolve, and both figures are superseded: the register has them at **2026-08-09** (and
2026-08-20), while the document now reads 0.71875. This is precisely the disease [[R187]] names.

**It is reclassified: a finding, not a false positive.** That is a judgement, made against the rule
the shipped gate already enforces rather than by taste — and it is recorded as a reclassification of
the predecessor loop's hand census (`docs/superpowers/2026-09-09-a-figure-at-the-end-of-a-sentence.md`
§3, rows 5-6), not as a new measurement.

## 2. What the measurement DOES license: the region, not the boundary

The candidate bundled two independent changes, and they have opposite verdicts. Separating them is the
whole content of this spec.

- **Which regions of a source file can carry a claim at all — CONFIRMED.** In markdown every line is
  prose. In Python prose lives in **comments and docstrings**; everything else is code. A decimal in
  code is a *value*, not a claim about a corpus: `STEM = Decimal("0.9654553611484971")` states nothing
  a reader could date. Restricting the walk to prose regions drops 24 of the 44 occurrences, **6 of
  them undated** — `tests/test_docgov_extract.py:148, 149, 156, 157, 158` and
  `tests/test_docgov_queries.py:77`, every one a fixture literal in code — and **loses zero findings**.
- **What the closure boundary is INSIDE a prose region — REFUTED.** It stays the block, for the
  reason measured in §1.

**The rule, stated once (plan rule 6 — cite this, do not re-derive it):**

> **A claim lives in prose; the block is where its date must live.** The substrate decides which
> regions are prose. The boundary inside a prose region is the same everywhere: a maximal run of
> non-blank lines. Markdown is the case where the prose region is the whole file.

## 3. Scope — `.py` only

`.ttl` and `.rq` are **out of scope**, measured rather than assumed. Across 203 tracked `.ttl`/`.rq`
files the census finds exactly **one** undated denoting occurrence — `vocab/internal/corpus.ttl:215`,
an `rdfs:comment` illustrating what `cor:value` means, a false positive — and **zero findings**.
Turtle and SPARQL have no `tokenize`/`ast`: recovering their prose regions exactly means writing a
lexer that distinguishes a `#` comment from the `#` in an IRI and from a `#` inside a string literal.
**The measured population licensing that work is zero.** Recorded as a residue, not as a silent gap.

## 4. What the extension is NOT: [[R196]](b) does not become live

[[R196]]'s row asserts of both halves: *"Both become live the moment the scope extends to code."*
**MEASURED 2026-09-09, and refuted for (b):** over every `.py` prose block, the number of denoting
occurrences whose block is dated ONLY by a date inside a letter-bearing token (a filename) is **0**.
The corpus PDFs are named `graincorp-stem-2026-07-31.pdf` and `cbh-stem-2026-08-03.pdf`, so the hazard
is real in principle; no `.py` prose block relies on one. (b) stays deferred on its original ground,
which is now measured on two corpora instead of one.

## 5. The instrument

`tests/docgov_extract.py`, PROCEDURAL under CLAUDE.md §8, on the module's existing justification —
raw extraction, source → typed RDF facts, irreducible because no ontology can read a file or run a
tokenizer. **Exact, not heuristic:** Python's own grammar defines what a comment and a docstring are,
via `tokenize` and `ast`. There is no tolerance, no threshold and no tuned constant anywhere in it;
that is what distinguishes this from a "prose-looking line" reader, which would be a §8 defect.

- `prose_regions_py(text) -> list[tuple[int, list[str]]]` — one entry per **comment run** (maximal run
  of consecutive lines bearing a `tokenize.COMMENT` token) and per **docstring** (`ast`: the first
  statement of a Module / FunctionDef / AsyncFunctionDef / ClassDef, when it is a string constant).
  A trailing comment contributes its comment text only, **left-padded to preserve column positions**,
  so a decimal in the code half of that line is not admitted as prose.
- The figure walk applies `blocks()` **inside** each region and is otherwise unchanged. `_figure_facts`
  stays a pure fact emitter (spec 2026-09-08 §6 I3); `is_dated`, `denotes`, `_DECIMAL` and
  `separating_precision` are **untouched**.
- A source file is emitted as **`dg:SourceFile`**, carrying `dg:path` and `dg:docClass "code"` — NOT
  `dg:Document`. `dg:DocumentShape` constrains `dg:docClass` to six values and requires `dg:inNav` and
  `dg:excludedFromSite`; a `.py` file has none of those, and typing it `dg:Document` would make the
  membrane fail it for being a file rather than a defect. A new `dg:SourceFileShape` validates the
  new class instead.
- **The derivation is unchanged.** `vocab/queries/docgov-undated-figure.rq` already reads
  `?doc dg:docClass ?class . FILTER (?class != "evidence")`, so `"code"` derives findings with no edit
  to the AXIOM. Open world, evidence-positive, as it was.

## 6. Disposition — HARD, on the same licence the wiki gate had

The wiki gate ships HARD because its census measured **0 false positives in 11 occurrences**. The
code census measures **10 undated occurrences, of which 6 are findings and 4 are false positives** —
and all 4 false positives are in **one file**, `tests/test_docgov_extract.py`, in the figure gate's
**own docstrings**, where the prose must quote figures to explain what the gate discriminates.

**The repair for all ten is the same, and it is [[R187]]'s own prescription: DATE THE CLAIM, never
rewrite the figure.** A mention in the gate's own test prose *is* a quotation of a dated reading;
writing that date in is true, informative, and costs one edit. **No exemption list is introduced** —
an exemption would be a coverage loss dressed as a fix, and it is the shape [[R188]] exists for.

So: repair all ten by dating them, then gate `"code"` HARD alongside `"wiki"`. **The licence for HARD
is the pre-repair census in this spec, published before the repair** — [[R187]]'s recorded trap is
that a gate with nothing to find is indistinguishable from a clean tree, and §1's table is what
distinguishes them here.

**The falsifying oracle, per [[R188]]:** the gate must be shown to fire. Reverting any one of the ten
repairs must turn the new test RED. A plan that ships without that evidence has shipped a gate
calibrated to zero.

## 7. What is NOT done

- **`.ttl` / `.rq` prose regions.** §3. Zero measured findings; needs a Turtle/SPARQL comment lexer.
- **[[R196]](b), filename dating.** §4. Measured at 0 on the code corpus; stays deferred.
- **A mention-vs-report reader ([[R194]] arm 1).** Not built and not needed: the prose restriction
  removes 6 of the 11 mentions the predecessor census found, and the remaining 4 are repaired by
  dating rather than by classification. R194's population argument is unaffected by this loop; its
  count changes from 11 to 4.
- **Rewriting any superseded figure.** Every repair adds a date. No figure's value is edited.
- **The 24 filename-dated markdown occurrences.** [[R196]](b) again; all in `evidence`, which the
  derivation exempts.
