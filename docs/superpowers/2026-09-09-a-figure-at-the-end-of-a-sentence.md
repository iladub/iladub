# A figure at the end of a sentence — the 5a census, and the two scope defects it found

**Topic:** action **5a** of `docs/superpowers/2026-09-08-r187-closed-handoff.md`, graded PROPOSED:
run the figure census over tracked `.py` / `.ttl` / `.rq` **before** extending the gate's scope, and
let it decide the disposition.

**Written 2026-09-09**, part 5 of the handoff first. **The census refuted both predictions on
record** — [[R189]]'s and 5a's own — and found a defect in the shipped instrument that neither
predicted and that is not about scope at all.

**Doc impact: none.**

---

## 1. The census

Instrument: the shipped `tests/docgov_extract.py` functions, unmodified — `blocks`, `is_dated`,
`separating_precision`, `load_readings`, `denotes`, `_DECIMAL` — over
`git ls-files '*.py' '*.ttl' '*.rq'`. Register as shipped: 18 readings, 1 `cor:notQuotable`,
`sep = 4`.

```
population: 497 tracked files (294 py / 150 ttl / 53 rq)
denoting occurrences: 74      of which undated: 14
```

**Zero occurrences anywhere under `src/`.** That is the first surprise, and it is wrong.

## 2. Why it is wrong — D1, the sentence-final figure

[[R189]] names three sites. All three still exist, at exactly the lines it gives:

```
$ grep -n '0\.9654553611484971' src/iladub/etkl/compile.py tests/etkl/test_datagrid.py
src/iladub/etkl/compile.py:1288:    # page leaves the stem document byte-identical at 0.9654553611484971.
src/iladub/etkl/compile.py:1302:    # 0.9654553611484971. Pinned by tests/test_corpus_stem.py::
tests/etkl/test_datagrid.py:1085:    0.9654553611484971. See tests/test_corpus_stem.py's
```

The census found **none of them**. Each writes the reading at the **end of a sentence**, and the
lexical rule was

```python
#: A decimal literal, not part of a longer dotted token (a version, an IP, a range).
_DECIMAL = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
```

`(?![\w.])` refuses a following dot unconditionally. A full stop is not a longer dotted token, so
**the rule over-refused against its own comment** — an implementation defect, not a design choice.
The spec never specifies the tokenisation (it specifies `denotes`, §3.3), and no test pinned it.

Widened to `(?<![\w.])\d+\.\d+(?!\w)(?!\.\d)` — refuse a following dot only when another digit group
follows it:

| corpus | shipped | widened | newly visible |
| --- | --- | --- | --- |
| tracked `.py` / `.ttl` / `.rq` | 74 | 77 | **3 — exactly R189's three sites, and nothing else** |
| tracked markdown | 497 | 514 | 17, **all `evidence`** |
| `docs/wiki/**` (the hard gate's class) | 11 | **11** | **0** |

So the fix repairs recall and **changes nothing the hard gate reports**. Shipped in this loop, with
`test_a_figure_at_the_end_of_a_sentence_is_still_a_figure` and
`test_a_longer_dotted_token_is_still_refused` (the second is what stops "match everything" passing
the first).

**The finding under the finding:** 5a proposed extending the gate's *scope* to `.py`. Had that
shipped alone, it would have closed R189 on paper and caught **zero of R189's own three sites**. The
blocker was never the scope.

## 3. The disposition — 17 undated, and only 4 are findings

With D1 fixed, the undated population in code is 17. Hand-classified, every one:

| # | site | verdict |
| --- | --- | --- |
| 1-2 | `src/iladub/etkl/compile.py:1288,1302` | **finding** — superseded stem score as present fact |
| 3 | `tests/etkl/test_datagrid.py:1085` | **finding** — same |
| 4 | `tests/etkl/test_membrane_health.py:429` | **finding** — `0.9655` + "77 escalated tokens", both superseded. **R189 does not name this one** |
| 5-6 | `tests/etkl/test_adoption_document.py:369` (×2) | false positive — **D2**, below |
| 7-15 | `tests/test_docgov_extract.py` (×9) | false positive — the figure gate's **own unit-test fixtures** |
| 16 | `tests/test_docgov_queries.py:77` | false positive — a synthetic literal in a query test |
| 17 | `vocab/internal/corpus.ttl:215` | false positive — an `rdfs:comment` illustrating what `cor:value` means |

**4 findings, 13 false positives — 76%.** Against `docs/wiki/**`, which shipped a HARD gate on
**0 of 11** false positives.

**[[R189]]'s warning is refuted as stated:** it predicted the false positives would be *parameters*
(*"a `.py` file's decimals are mostly parameters"*). **Zero of the 13 is a parameter** — the
register-driven rule does exactly what 5a reasoned it would, and `0.5` or `1e-5` never round-matches
at 4 decimals uniquely. **5a's conclusion was wrong anyway**, from a source neither prediction
names: the instrument's own fixtures, and D2.

**R189's population is 4, not 3.**

## 4. D2 — the block is the wrong closure boundary in code, and a filename dates a claim

Two defects in `is_dated`'s scope, both measured, **neither fixed here**.

**D2a — a dated docstring, split into paragraphs, reports its first paragraph as undated.**

```
$ block containing tests/etkl/test_adoption_document.py:369 → lines 367-369, dated=False
$ the enclosing docstring (369-382)                          → dated=True
```

`blocks()` is maximal runs of non-blank lines. In markdown a paragraph is the authorial unit, and the
block rule was chosen for a measured reason (a date one line above the figure). In Python the
authorial unit is the **whole docstring or comment run**; splitting it on blank lines invents a
finding out of a document that dates itself twice, two paragraphs down.

**D2b — a date inside a filename dates the block.** `_ISO_DATE` is `\b\d{4}-\d{2}-\d{2}\b`, and the
corpus is named `graincorp-stem-2026-07-31.pdf`, `cbh-stem-2026-08-03.pdf`.

```
figure occurrences whose block is dated ONLY by a date inside a filename: 24
   all 24 in `evidence`; 0 in docs/wiki/**
```

Not all 24 are defects — an evidence file citing `2026-09-05-r173-5a-rebaseline.md` is genuinely
dated by that filename. The ones citing a **corpus PDF** are not: that date is the document's, not
the reading's, and it is off by up to five weeks from when the figure was measured.

**Both are invisible in `docs/wiki/**` today** (0 of 11 occurrences), so the hard gate that shipped
on 2026-09-08 is not under-firing. Both become live the moment the scope extends to code.

## 5. What was NOT done, and why

**The 4 findings are left in place, undated.** They state a superseded score in shipped source and
repairing them is a two-minute edit. Deliberately not taken: they are the **only measured positive
population on the live tree** for a future code-scope gate, and [[R187]]'s own trap is that a gate
with nothing to find is indistinguishable from a clean tree — it shipped green once here for exactly
that reason. Repair them in the same change that gates them, not before.
