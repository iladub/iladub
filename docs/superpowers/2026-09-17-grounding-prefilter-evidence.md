# Evidence — the grounding pre-filter (R249, half a)

**Serves:** maintenance — executes § 4.1 of `2026-09-17-neural-worker-spec-review.md`, ruled by the maintainer ("go with the pre-filter")

**Date:** 2026-09-17. **Tree:** branch `grounding-prefilter`, cut from `main` at `64a9f25`.

**Doc impact: none.**

**Executed past the floor, in the session that wrote the review, at the maintainer's request.**
The change is 40 lines; every claim below was run.

---

## 1. What changed

- `ground.py`: `ground_concept` gains an arm between `marker_field` and the proposer. When
  `_admissible_fields` is empty — no contract field's `_grounds_to(is_exact=False)` admits the
  value — the proposer is **not asked**. The concept is quarantined with suggester
  `urn:iladub:suggester/no-admissible-field-rule`, anchor `gist:Category`, confidence 1.0
  (the precedent is `splitkey.py`'s rule-minted quarantine). §8 class: AXIOM. The arm asks only
  the shipped oracle.
- `_admissible_fields` takes an optional memo keyed on (value, field IRI).
  `feed.ground_document` owns one per call. Other callers pass none and stay correct, only slower.

## 2. Measured

**Calls** (`scripts/neural_seam_population.py`, all 7 documents, before → after):

```
before: cbh 725  gcap 377  gstem 1262   total 2364
after:  cbh   0  gcap 149  gstem    0   total  149
```

This matches the review's prediction exactly (|A| = 0 on 2,215).

**Outcome unchanged, cost bounded** (graincorp-stem, one compile, `ground_document` under the
battery's abstaining proposer, filter off/on alternated twice):

```
no memo:   off 1.2s  on 8.7s  off 1.2s  on 8.6s   grounded=644 proposed=1286 in all four
memo:      off 1.4s  on 3.0s  off 1.2s  on 3.0s   grounded=644 proposed=1286 in all four
```

**What does change, by design:** the suggester, anchor and confidence on the 2,215 quarantined
candidates. `grep` for readers of `suggestedBy` or the fake suggester IRIs across `tests/`,
`vocab/` and `*.rq` found none beyond the shape's `sh:minCount 1`, which still holds.

## 3. Tests

- **New:** `tests/test_grounding_prefilter.py`. An unadmissible value (`55%` on the transplant
  contract) never reaches the proposer and carries the rule suggester. The control: an admissible
  value (`55`, `tx:ejectionFraction` decimal 0..100) still reaches it.
- **Falsification** (both directions, then restored):

  ```
  filter removed (elif False):          1 failed, 1 passed
  filter skips everything (elif True):  1 failed, 1 passed
  restored:                             2 passed
  ```

- **Two existing tests changed their fixture, not their assertion.** Both needed the proposer to
  be asked, and both fed values nothing admits:
  - `test_suggester_guard.py` (R129's public-seam drive): `55%` → `55`.
  - `test_propose_grounding_context.py` (R211's page-context slot): empty shapes → the real
    `capacity-shapes.ttl`, and `845870` → `845,870`.
  In each case the pre-filter would have made the test vacuous rather than red.
- Grounding set (10 files): 108 passed. Corpus and contract set
  (`test_corpus`, `test_stem_contract`, `test_cbh_contract`, `test_cbh_e2e`, `test_corpus_stem`):
  51 passed (808 s). Governance gates: 53 passed.

## 4. Not done

- **R249's other half:** whether gcap's 149 cells, with one admissible field behind a number
  pattern that also admits [[R213]]'s zeros, may be handed to a model. That is a maintainer ruling.
- No wiki exemplar entry was added (`docs/wiki/concepts/neurosymbolic-exemplars.md`). This pattern
  is a candidate for it: the Loop Q "decide membership first" pattern applied to grounding.
