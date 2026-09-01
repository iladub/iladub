# Corpus reach, measured — R158's prediction is refuted, and the instrument is committed

**What this is:** the measurement `R158` deferred and the predecessor handoff required be RUN before
anything was built on it. It is not a diagnosis and it proposes no remedy.

**Result in one line: the prediction is REFUTED.** *"Most changed functions are reached by 3 or fewer
of the 7 documents"* — measured, **6 of 16 (37.5%)**. Ten of sixteen are reached by **all seven**.

**Doc impact: none.**

---

## 1. The question, in the form it was set

`R158` generalized five register rows and two loop findings into one claim: *"the 7-document corpus
does not enter the code under test."* Its successor handoff graded that a **reframing, not a
measurement**, and set the falsifiable form:

> take the changed function from each of the last ~6 `src/`-touching loops and count, per corpus
> document, how many times it executes on a full compile.
> **Prediction: most changed functions are reached by 3 or fewer of the 7 documents.**

## 2. Method

`scripts/reach_probe.py`, committed by this loop. One `cProfile`'d `compile_document` per document,
**plus** a profiled `ground_document` for the two documents carrying a `cor:contract` — because the
corpus battery has both legs and four of the sixteen functions live on the grounding side. Counting
every function in one pass was measured first, as the handoff required: it works, and it is why the
instrument answers for **any** function rather than only these sixteen.

**Cost:** 2.1× wall overhead (graincorp-capacity 12.0 s → 25.7 s); 840 s for the whole corpus, one
process per document. Reported scores reproduce the manifest: gstem 0.9659 (floor 0.95), who 0.9096
(floor 0.90), gcap 1.0000, ons 0.9720, cbh 0.9092, apple 0.3587, bfs 0.3464.

The sixteen functions are the distinct `(file, name)` pairs named by the enclosing-def hunk headers
of `git diff -U0` over the last six `src/`-touching loops: R154 (#146), R45 (#145), R139 (#142), the
four-rows membrane repair (#141), `holon:05` (#128), R103 (#109).

## 3. The measurement

```
$ ./.venv/bin/python scripts/reach_probe.py report --out /tmp/reach \
    geometry.py:rule_aware_lines geometry.py:refine_rule_columns \
    gridregion.py:interior_rule_xs matrix.py:infer_column_tree_by_proximity \
    document.py:_seal document.py:_legs_for_document document.py:compile_document \
    compile.py:_validate compile.py:compile_tables compile.py:_build_membrane \
    promote.py:emit_span_promotion promote.py:_suggester holon.py:_suggester_uri \
    ground.py:_emit_candidate splitkey.py:_emit_candidate membrane.py:subclass_closure

defining file       function                          gstem  gcap   cbh   ons   bfs apple   who  reach
etkl/geometry.py    rule_aware_lines                     14     6    15    72    50    40    28   7/7
etkl/geometry.py    refine_rule_columns                   8     6    15    72    38    40    22   7/7
etkl/gridregion.py  interior_rule_xs                      2     3     5     3    11    17     9   7/7
etkl/matrix.py      infer_column_tree_by_proximity        0     0     0     0     0     2     3   2/7
etkl/document.py    _seal                                 1     1     1     1     1     1     1   7/7
etkl/document.py    _legs_for_document                    1     1     1     1     1     1     1   7/7
etkl/document.py    compile_document                      1     1     1     1     1     1     1   7/7
etkl/compile.py     _validate                             4     2     3     2     3     3     4   7/7
etkl/compile.py     compile_tables                        3     1     2     9     9     4     3   7/7
etkl/compile.py     _build_membrane                       1     1     1     1     1     1     1   7/7
promote.py          emit_span_promotion                  --    --    --    --    --    --    --   0/7
promote.py          _suggester                           --    --    --    --    --    --    --   0/7
etkl/holon.py       _suggester_uri                        0     0     4     0    12    21     0   3/7
ground.py           _emit_candidate                    1850     0   909     0     0     0     0   2/7
splitkey.py         _emit_candidate                      --    --    --    --    --    --    --   0/7
etkl/membrane.py    subclass_closure                     12     4    17     4    15    23    18   7/7

CORPUS-WIDE, over 318 src/iladub functions called at least once:
  reached by 1/7 documents:   26      reached by 5/7 documents:   18
  reached by 2/7 documents:   88      reached by 6/7 documents:   32
  reached by 3/7 documents:   24      reached by 7/7 documents:  122
  reached by 4/7 documents:    8
```

## 4. What it says

**The prediction is refuted.** 6 of 16 changed functions are reached by ≤3 documents (37.5%); 10 of
16 are reached by all seven. `R158`'s framing does not hold as a **corpus property**.

**The row was right about its instances and wrong about their generality.** `R45`'s figure reproduces
to the call — `infer_column_tree_by_proximity`: gstem 0 · gcap 0 · cbh 0 · ons 0 · bfs 0 · apple 2 ·
who 3 — so the five vacuous PASS rows were real, and so was PR #109's inert zero-delta. They are the
**tail** of the distribution, not a description of it.

**The distribution is bimodal**, and this is the part worth carrying: 10 functions at 7/7, 3 at 0/7,
and only 3 anywhere in between (3/7, 2/7, 2/7). The reading that suggests itself — a *spine* every
document walks and *limbs* the corpus never enters — is a story fitted to sixteen points by the
session that measured them, and is filed as `R159` rather than asserted here.

## 5. The instrument's own first version was wrong, in the understating direction

Recorded because it will recur for anyone building a probe like this. The first committed version
compiled all seven documents **in one process**, and reported `compile.py:_build_membrane` at **1/7**.
It is `functools.lru_cache`d: document one pays the call, documents two through seven are served the
cache, and cProfile records nothing for them — so the function was attributed to whichever document
the loop happened to visit first (cbh, alphabetically). Every memoized or run-once function fails the
same way, silently, and **always in the direction that understates reach** — which is the direction
that would let a loop dismiss a real regression risk as unreachable.

One interpreter per document is the fix; `_build_membrane` then reads 7/7, and the corpus-wide count
at 7/7 moves 110 → 122. Pinned by
`tests/test_reach_probe.py::test_run_gives_every_document_a_fresh_interpreter`, falsified by
reverting to a shared process (RED), restored (green, 5 passed).

A second defect, caught in the prototype before it reached a file: `_emit_candidate` was resolved to
the module its diff hunk header named rather than the module it is defined in, and reported 0/7 for a
function called 1850 times. A lookup that misses reads exactly like a function nothing reaches. Pinned
by `test_a_name_defined_in_two_modules_reports_both`.

## 6. What this does NOT say

- **A 0/7 row is not dead code.** cProfile records a function only when CALLED, so an absent entry
  cannot distinguish "never imported" from "imported, never called", and says nothing about unit
  tests, the CLI, or any entry point outside the corpus battery's two legs. `R146` records that
  inferring from absence is what CLAUDE.md §8 forbids; **nothing here licenses "grow the corpus"** as
  the remedy for a low-reach row.
- **A 7/7 row is not a safety claim.** It says a document executes the function, not that the
  document's oracle would notice if the function broke. Reach is necessary for power, not sufficient.
- **Not every changed function is a behavioural change.** The sixteen come from hunk headers, which
  name the *enclosing* def; `R139`'s `_seal` row is a comment-only edit and counts the same as a
  semantic one.
- **The bimodality claim and its only check came from the same run.** See `R159`.

## 7. Unverified

- `run` was executed once end-to-end on the fixed instrument. Call counts should be deterministic and
  were not re-run to prove it; the compile-leg counts do reproduce an independent prototype run to the
  unit on every document, which is evidence and not a repeat.
- The grounding leg was measured for the two contracted documents only, because only two carry a
  `cor:contract`. The other five have no grounding leg to reach — a fact about the manifest, and the
  progress census's candidate B, not about the code.
