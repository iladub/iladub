# Handoff — the 5a census is run: scope was never the blocker, and both predictions on record are refuted

**Topic:** action **5a** of `docs/superpowers/2026-09-08-r187-closed-handoff.md`, graded PROPOSED, is
taken. The census ran **before** any scope change, which is what 5a said to do — and it is the only
reason the loop did not ship a gate that catches nothing. [[R189]] stays **open**, with its evidence
corrected and its population raised from 3 to 4. [[R196]] raised. One defect in shipped code fixed.

**Written 2026-09-09**, part 5 first.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. PROPOSED — settle [[R196]](a) as a design question, then extend the walk and gate code in ONE change

The remaining work on [[R189]] is blocked on one question that is **not a parameter**: *what is the
closure boundary for datedness in a source file?* The markdown answer — a maximal run of non-blank
lines — was chosen for a measured reason and still holds for prose. It is wrong for Python, where the
authorial unit is the whole docstring or comment run, and it invents 2 of the 13 false positives the
census measured.

**Why proposed and not asserted:** the candidate answer (comment-run as the unit) is a guess with one
measured instance behind it. It must be measured against the markdown rule rather than replacing it,
and the population it would be measured on is 17 occurrences in one repo — small enough that a rule
fitted to it is a rule fitted to noise. **It fails cheaply:** re-run §1's census with the candidate
boundary and count; if the false-positive rate does not fall below the 0-of-11 that licensed the
hard wiki disposition, the answer is a **warning** for code, and that is a legitimate outcome, not a
failure. Do not ship the scope extension without it — §2 is the record of what that costs.

**When it ships, repair the four findings in the same change.** They are left undated deliberately
(§5 of the loop record) and the reason expires the moment a gate exists.

### 5b. ASSERTED — the mention-vs-report population [[R194]] asked for now exists, and it is 11

[[R194]] arm (1) deferred *"context, not precision"* — distinguishing a **report** of a figure from a
**mention** of one — on the ground that *"it needs a population bigger than three occurrences to be
worth building."* This census supplies it: **11 of the 13 false positives are mentions** — the figure
gate's own unit fixtures (10) and a vocabulary `rdfs:comment` illustrating what `cor:value` means
(1). Mechanical to re-derive: `docs/superpowers/2026-09-09-a-figure-at-the-end-of-a-sentence.md` §3
lists every one by file and line.

This does **not** say build it. It says R194's stated blocker is gone, and the arm is now a decision
rather than a deferral. Note what the population is made of before choosing: a gate whose largest
false-positive source is *its own tests* has an exemption available that is honest and cheap, and it
is not the same thing as a general mention/report reader.

### 5c. PROPOSED — that [[R192]]'s population is bigger than n=1

**Carried verbatim for the third loop running, still unrun.** How many Evidence documents restate a
corpus figure they did not themselves measure? If the answer is "the capability line and nothing
else", R192 is one bad sentence, not a class. The count is one filter over `dg:FigureOccurrence` +
`dg:blockDated`, and this loop made it slightly cheaper again — evidence occurrences are now 503, and
**[[R196]](b) says 24 of them are dated by a filename rather than by a measurement**, so that filter
must exclude filename-dating or it will under-count.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the census, and both refutations | `docs/superpowers/2026-09-09-a-figure-at-the-end-of-a-sentence.md` | §2 why all three R189 sites were invisible; §3 the 17 undated hand-classified one by one; §4 the two dormant defects; §5 why the findings are left unrepaired |
| the fix | `tests/docgov_extract.py`, `_DECIMAL` + its comment | the widened form and the three measured deltas, stated where the rule is |
| its oracle | `tests/test_docgov_extract.py::test_a_figure_at_the_end_of_a_sentence_is_still_a_figure` and `::test_a_longer_dotted_token_is_still_refused` | the second is what stops "match everything" passing the first |
| the corrected row | [[R189]] in `residues-open.md` | four corrected facts for whoever closes it — read the row, never the index line |
| the new row | [[R196]] in `residues-open.md` | both halves, and what would NOT close it |

## 2. What changed

One branch, `r196-a-figure-at-the-end-of-a-sentence`, off `4991dd1`.

- **Fixed:** `tests/docgov_extract.py` — `_DECIMAL` widened from `(?<![\w.])\d+\.\d+(?![\w.])` to
  `(?<![\w.])\d+\.\d+(?!\w)(?!\.\d)`. The old form refused a following dot unconditionally; the
  comment above it says it exists to refuse *"a longer dotted token (a version, an IP, a range)"*,
  and a full stop is not one. **Over-refusal against its own stated intent** — no test pinned it and
  the spec never specified the tokenisation (it specifies `denotes`, §3.3).
- **New tests:** 2 in `tests/test_docgov_extract.py`, plus a `_lexicals` helper.
- **New:** the loop record; [[R196]] in both register files.
- **Amended:** [[R189]]'s row and index line — not closed, corrected.

**The measured effect of the fix, all three corpora:**

```
tracked .py/.ttl/.rq (497 files)   74 → 77 occurrences   (+3: exactly R189's three sites)
tracked markdown                  497 → 514              (+17, ALL `evidence`)
docs/wiki/**  (the hard gate)      11 →  11              (+0)
```

The 11 is the same 11 the R187 loop shipped against. **The hard gate's findings are unchanged**, so
this is a recall repair with no disposition consequence.

Suite: `tests/test_docgov_extract.py` **19 passed**; `test_doc_governance.py` + `test_docgov_queries.py`
+ `test_docgov_shapes.py` + `test_corpus_manifest.py` **46 passed, ~25 s**.

## 3. What was decided, and where that decision is recorded

- **The walk is NOT extended to code.** Loop record §3 and [[R189]]'s amended row. Ground: 76%
  false positives against the 0-of-11 that licensed the hard wiki disposition.
- **The four findings are left in place, undated.** Loop record §5. Ground: they are the only measured
  positive population on the live tree, and [[R187]]'s own trap is a gate with nothing to find being
  indistinguishable from a clean tree. Repair them in the change that gates them.
- **[[R196]] is not fixed in the loop that found it.** Its row. Ground: 0 of 11 wiki occurrences are
  affected, so fixing now is changing a running instrument against a population of zero.
- **R189 is corrected, not closed.** Its row. Its criterion (*"extend the walk, re-run the census"*)
  was executed and is now known to be insufficient on its own.

## 4. Unverified or assumed

- **The full suite has not reported at the time of writing.** The four governance files and
  `test_docgov_extract.py` are green; the whole-suite run and CI are the checks that have not. The
  suite takes roughly 45-60 minutes here.
- **The hand classification in §3 of the loop record is mine, not an instrument's.** 17 rows, each
  read in its file. The R187 loop's lesson was that a hand census was wrong and the instrument right
  — this one is a *judgement* about each occurrence, which no instrument here can make, but the
  boundary between "finding" and "mention" is exactly the judgement [[R194]] arm (1) says is NEURAL.
  Treat the 4/13 split as a considered reading, not a measurement.
- **`(?!\w)(?!\.\d)` is verified on six probes, not proved.** `1.2.3`, `v0.0.4`, `10.0.9655.1`,
  `0.9655.0607`, `0.9655.9659`, `a.0.9047` all still refuse; sentence-final and ellipsis-truncated
  forms now match. A dotted form outside those shapes is unmeasured.
- **A truncation ellipsis is now a match** — `0.9655...` yields `0.9655`. Judged correct (it denotes
  the reading) and pinned by the new test, but it is a behaviour change nobody asked for, and it is
  the one part of the widening that is a reading judgement rather than a defect repair.
- **`0.9720`-style occurrences in `tests/corpus-manifest.ttl` are counted as denoting** and were not
  classified — the register quoting itself is a category the census did not need to settle, since
  those blocks are dated.
- **[[R196]](b)'s 24 is a count of filename-dated blocks, not of defects.** Some of those dates are
  right. The row says so; the number must not be re-cited as a defect count.
