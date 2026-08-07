# The kind gate is load-bearing — why slice B cannot start yet — design

**Date:** 2026-08-07 · **Status:** approved (François, 2026-08-07) ·
**Opens:** R71 · **Blocks:** slice B of the reading-as-differential-diagnosis
architecture (`2026-08-07-reading-decision-record-design.md` §7) ·
**Specimen:** `corpus/ag-trade/graincorp-stem-2026-07-31.pdf`, page 0 region 2 and
page 2 region 1

**Doc impact:** none — no vocabulary, no query, no `src/` change, no site page
touched. The deliverable is a measurement, a residue row, and a regression guard.

## 1. What this loop set out to do, and why it stopped

Slice B was to replace the three-value `RegionKind` enum with a carried set of
topology candidates narrowed by observation rather than by an early Python branch.
The agreed shape was a **vertical** slice: not a modelling change, but a capability
one — recover a table iladub currently misses, proven by a corpus score moving up.

**That goal has no target.** Measured across the whole corpus, there is no region
where the kind gate suppresses a topology that would have succeeded. In the only two
places it suppresses anything, it is *protecting a correct outcome*.

This loop therefore ships the measurement instead of the refactor. Building slice B
on the assumption that was refuted here would have cost 1,327 of stem's 2,152
asserted cells.

## 2. The conflation that motivated slice B — still real

`classify-kind.rq` asks exactly one question: *does the header line have exactly
`ncols` words, each strictly inside its own column?* That is **header regularity**.
Its binary outcome then decides which topologies are even considered:

```
kind
├── NON_TABLE          → ignore
├── RECORD_TABLE       → transposed? → coherent? → tiles?
│                      → row_grouped? → tiles?
└── UNSUPPORTED_TABLE  → matrix_candidate? → tiles?
                       → hierarchical? → tiles?
```

So `transposed` and `row_grouped` are unreachable for an irregular-header band, and
`matrix` is unreachable for a regular-header one — not because evidence refuted them,
but because a Python branch never offered them. The critique stands. What this loop
found is that *acting on it naively regresses the corpus*.

A second coupling makes it sharper. `regions.py:109` assigns `cells` **only** for
`RECORD_TABLE`. The gate does not merely skip the transposed test on an
irregular-header band — it withholds the evidence that test consumes. Carrying
candidates therefore means building the evidence for all of them *before* narrowing,
which is a larger change than the enum swap it looks like.

## 3. The measurement

For every band of every corpus document: classify it, assign cells regardless of kind
(the evidence the gate withholds), then run the oracles its branch would never reach.
A band is **suppressed-positive** when it is `UNSUPPORTED_TABLE` and `looks_transposed`
or `looks_row_grouped` returns True.

| document | suppressed-positive bands |
| --- | --- |
| apple (1p) | none |
| capacity (1p) | none |
| WHO (3p) | none |
| CBH (1p) | none |
| **stem (3p)** | **p0 region2, p2 region1** |

Both stem bands, examined:

| | p0 region2 | p2 region1 |
| --- | --- | --- |
| `kind` | UNSUPPORTED (`header has 2 words but 17 columns`) | UNSUPPORTED (`header has 1 words but 17 columns`) |
| `looks_transposed` | **True** | **True** |
| `transpose_is_coherent` | **False** | **False** |
| verdict today | **asserted**, 586 cells | **asserted**, 741 cells |
| "header" line | `['Friday, 31', 'July 2026']` | `['Date of Grain']` |

## 4. Why un-gating would regress, not recover

Both regions compile successfully today down the `UNSUPPORTED → hierarchical` path.
Un-gating `transposed` routes them instead into the transposed branch, where
`looks_transposed` is True and the coherence oracle then returns False. That branch
is not a fallback — `src/iladub/etkl/compile.py` (the `else:` after
`if is_coherent:`) calls `escalate_region(..., "TRANSPOSED", TAB.TransposedTable, 0.4)`,
adds every line's words to `escalated_total`, and appends
`RegionReport(..., "escalated", 0, "TRANSPOSED", ...)` — **zero asserted cells**.

So the two regions would go from 586 + 741 = **1,327 asserted cells to 0**, out of
stem's 2,152 — and their words would be added to `escalated_total` on top. The exact
resulting score is not stated here because it was not run: what was measured is the
cell movement and the code path that produces it. That is already decisive, and an
estimated score would be a number this loop did not earn.

**`looks_transposed` is a false positive on these bands.** Its signature is "a
type-homogeneous structured row, and no type-homogeneous structured column." A
caption line read as a header (`Friday, 31 July 2026` spanning 17 columns) produces
exactly that shape without any transposition being present. The coherence oracle
catches it — which is the R55 lesson intact: detection is not decision.

**The finding:** the kind gate is currently doing undocumented double duty as a guard
against this false positive. Nothing recorded that, and nothing would have caught it —
a "carry all candidates" refactor would have looked principled and lost a third of the
corpus.

## 5. What ships

1. **This spec** — the measurement, so the next attempt starts from evidence.
2. **R71** in the register — the kind gate's load-bearing role and its closing condition.
3. **`tests/etkl/test_kind_gate_is_load_bearing.py`** — an executable guard pinning, on
   the two real stem bands: `looks_transposed` is True, `transpose_is_coherent` is
   False, and the band's kind is `UNSUPPORTED_TABLE`. If a future loop carries
   candidates without hardening the oracle first, this fires with the reason attached
   instead of the corpus silently dropping 1,327 cells.

   It uses `page_bands` + `classify` on two pages, not a document compile, so it costs
   seconds. It is a **characterisation** test: it pins behaviour that is currently
   *wrong but protective*, and its docstring must say so, or a later reader will mistake
   it for an endorsement of the false positive.

## 6. Success criteria

- The suppressed-positive scan is reproducible from the method in §3, and its result
  table is recorded here.
- The guard fails if either stem band's `looks_transposed` / `transpose_is_coherent` /
  kind triple changes — verified by inverting one assertion and observing the failure.
- **No `src/` change**, so no verdict can move; corpus scores unchanged.
- R71 states the closing condition precisely enough that slice B can be re-planned
  against it without re-deriving this measurement.

## 7. What slice B needs before it can start

- **Harden `looks_transposed` against caption-line headers.** A 1–2 word line spanning
  many columns is a caption, not a header, and must not produce the transposition
  signature. Per the gate (CLAUDE.md §8) this is a recovery decision — open-world,
  evidence-positive — so it belongs in the `looks-transposed.rq` AXIOM or, if the
  judgement is genuinely perceptual, in a NEURAL proposal disposed by the coherence
  oracle. **Not a tuned word-count threshold in Python.**
- **Then** the candidate set can be carried, because the evidence that narrows it will
  no longer contain a known false positive.
- Note R10 is adjacent and may be the real root: it records that `detect_bands` cuts
  one line too high, leaving the report date inside the table band. The caption line
  these two regions read as a header is plausibly that same defect. Closing R10 might
  dissolve this one — worth checking before hardening the oracle.

## 8. Global constraints (carried, per CLAUDE.md)

- **No `src/` change**, therefore no verdict change.
- No new vocabulary; no `.ttl` touched.
- §7 *only emit what the source supports* is why this loop ships a measurement rather
  than a refactor: the evidence refuted the plan, and reporting that is the result.
- The guard is a characterisation test, not an assertion that the current behaviour is
  correct. Its docstring carries that distinction.
