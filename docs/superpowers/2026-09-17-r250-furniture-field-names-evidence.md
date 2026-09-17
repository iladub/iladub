# Evidence — R250: does the carried furniture name the capacity field?

**Serves:** prog:criterion:etkl:02 — graincorp-capacity's unlabelled tonnage column.

**Date:** 2026-09-17. **Doc impact: none.**

Measured on `main` at `db49647` by `scripts/furniture_field_names.py`, run twice (first from the
scratchpad on `ca75218`, whose `src/` is identical, then from the committed script on `db49647`),
with byte-identical output. It covers the three contracted corpus documents, serially, one per
process.

## The question

[[R250]]'s first step: does any label for the `capacity` field occur in graincorp-capacity's
carried `etkl:bandText`? The field has no label of its own. `exact_field` compares a concept's text
against the property's local name (`src/iladub/ground.py:100-105`), so the local name is the only
label there is to test.

## What was measured

| doc | field names found in the furniture | asks with a non-empty A |
| --- | --- | --- |
| cbh | none of 5 | 0 |
| gcap | **all 4**: `year`, `elevationPeriod`, `port`, `capacity` | 149, all text `''`, all `A = {capacity}`: **110 `0`**, 39 printed tonnages |
| gstem | none of 5 | 0 |

gcap's furniture, verbatim (`feed._page_context`):

```
GrainCorp Operations Ltd ABN 52003875401
ELEVATION CAPACITY TABLE
As At Tuesday, 4 August 2026
Year Elevation Period Mackay Gladstone Fisherman Islands Carrington Port Kembla Geelong Portland
GrainCorp advise that the tonnages shown are indicative only and are subject to change. 1
```

## What it establishes

1. **Yes, `capacity` occurs, as a whole word in the title** (`ELEVATION CAPACITY TABLE`). Positive
   evidence for the derivation is present on the page and already carried.
2. **Occurrence alone does not pick out the field: 4 of 4 field names hit.** The carried furniture
   includes the page's **real column header** band (R212's closure recorded this). That band
   supplies `year` and `elevationPeriod`, and `port` hits only through the port name
   `Port Kembla`. A rule of the form *"the field named in the furniture"* has 1 right answer among
   4 on the only document where it fires.
3. **The 110 invisible zeros are 110 of the 149 asks (74%).** Any derivation that admits
   `capacity` on this column asserts 110 tonnages of 0 where a reader sees an empty cell, unless
   [[R213]]'s ruled option (c) has shipped first. **R213 must ship before R250 is built.** That
   ordering is measured, not a preference.
4. **The controls fire nothing, and that cuts both ways.** cbh and gstem name no field in their
   furniture and send no ask past the pre-filter, so a derivation would stay silent there. But
   neither can refute a derivation either. gcap is the only specimen: n = 1, [[R157]]'s shape
   again. gstem's footer (*"the load dates shown are indicative only"*) has the same construction as
   gcap's (*"the tonnages shown"*), but names no contract field, so it tests nothing here.

## What it does not establish — PROPOSED

**Whether a derivation can be AXIOM is still open, and the measurement narrows the question.**
Picking the one right name out of the four needs a second signal. The obvious one is elimination:
remove the words that are already some column's label or some key's value, and `capacity` is the
only name left. That is a holon-scoped closed-world guard, which §8 permits in a derivation. But it
was **constructed after looking at the one document it would fire on**, and nothing in this corpus
can refute it. That is exactly the "tuned to one specimen" evidence the no-overfitting rule
forbids. The alternative, *which band is the title?*, is a reading judgement, and §8 sends it to
NEURAL, where no oracle exists.

**How this could fail:** a second capacity-like document whose title does not name the measure, or
whose header carries a word equal to an unclaimed field name. Neither exists in this corpus.
