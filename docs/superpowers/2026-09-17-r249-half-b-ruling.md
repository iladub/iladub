# Ruling — R249 half (b): no worker, the measure name is DERIVED per R212

**Serves:** prog:criterion:etkl:02 — graincorp-capacity's unlabelled tonnage column is the only
|A|=1 population [[R249]] measured.

**Date:** 2026-09-17. **Doc impact: none.**

## What was asked

[[R249]] measured that the grounding oracle admits exactly one field on 149 of the corpus's 2,364
asks: gcap's unlabelled tonnage column, `A = {capacity}`, admitted by an `sh:pattern` on
thousands-separated integers. The review (`2026-09-17-neural-worker-spec-review.md` § 4.2) left one
question to the maintainer: may a model decide whether that column is a capacity, when the only
check is a number pattern?

Two facts were put in front of the ruling:

1. **[[R213]] was already ruled, on 2026-09-13: option (c).** An invisible glyph is carried as a
   typed absence or a proposition, never as the `0` it reads. Once that ships, the 110 invisible
   zeros no longer reach the pattern, so the false-admit hazard R249 names is gone on this corpus.
   The ruling is **not implemented**: the third member of the absence distinction
   (`tab:Blank` / `tab:nilSpelling` / *ink the author hid*) is unnamed.
2. **What's left after that is structural.** The pattern checks a value's shape, not a column's
   meaning. A model's *"yes, this is a capacity"* is evidence nothing disposes of. No oracle, no
   worker.

## What was ruled

**No worker. The measure name is derived, per [[R212]]'s ruling that the machine derives it.**
Whether gcap's unlabelled column is a capacity is not handed to a model.

## What this ruling leaves unbuilt — measured, not assumed

The ruling names a derivation, and **no derivation exists.** Measured on `3f6c604`:

```
$ grep -rn "bandText\|IgnoredBand" src examples vocab --include='*.py' --include='*.ttl' --include='*.rq'
```

The only consumer of `etkl:bandText` is `feed._page_context` (`src/iladub/feed.py:40-67`). Its
result is handed to **the proposer** for every concept of the document
(`feed.py:747-757`, `page_context=context`). Its own docstring says it makes no reading and leaves
the proposer to make what it can of the furniture. **So the shipped route for "the machine derives
the measure name" is a model call.** That is the worker this ruling refuses. What replaces it is an
AXIOM derivation from the carried band text, and it is registered as [[R250]].

**PROPOSED, not asserted:** that the derivation can be AXIOM at all. The footer says *"the tonnages
shown"*, and matching that to `ship:capacity` is a lexical join between `etkl:bandText` and the
contract's terms. It could be declarative, like the exact-match leg of `_grounds_to`. It could also
turn out to be a reading judgement: *which band names the measure?* If it is, §8 sends it to
NEURAL, and then it needs an oracle this corpus doesn't have. The first measurement that would show
this: does any term label or `skos:altLabel` in `examples/shipping/capacity-terms.ttl` occur in any
gcap `etkl:bandText`?
