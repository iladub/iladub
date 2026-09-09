# R192's census is run — and the register cannot answer the question R192 asks

**Topic:** action **5a** of `docs/superpowers/2026-09-09-a-claim-lives-in-prose-handoff.md`, graded
ASSERTED: run [[R192]]'s census — *how many Evidence documents restate a corpus figure they did not
themselves measure?* — carried unrun for four loops.

**Written 2026-09-09.** A **RULING loop: no code ships.** The census is run, **all three of R192's
arms are refuted or unnecessary on today's evidence**, and the reason is not the one R192 expected:
`cor:readAt` is a **register-refresh log, not reading provenance**, so the question is
under-determined by the instrument that would have to answer it. Two new residues.

**Doc impact: none.**

---

## 1. The census

Instrument: the shipped extractor functions over every tracked `evidence` markdown file, at
`9716755`. Four **disjoint** dating classes per figure occurrence.

```
evidence figure occurrences: 525 in 95 documents

  block dated by none      : 326 occurrences in 85 docs
  block dated by sha       :  20 occurrences in  8 docs
  block dated by filename  :  24 occurrences in 13 docs   ← [[R196]](b)'s 24, re-derived
  block dated by own date  : 155 occurrences in 25 docs
```

**Arm (1) of R192 — "gate handoffs like wiki" — fires on the 326.** What is in them:

```
of the 326 undated:
  278 in 83 docs  the reading was CURRENT on the day the document was written
   48 in 10 docs  the reading was ALREADY SUPERSEDED before that day
       of those 48:
         45 in  5 docs  the document's SUBJECT IS the stale figure (the [[R187]] spec and
                        plan, this repo's two 2026-09-09 loop records, `the-two-counts`)
          3 in  3 docs  everything else
```

**And all three of the residual three name their own staleness in the same sentence:**

```
2026-09-01-progress-census-handoff.md:125  | who | 0.5597 | 0.9096 | +0.350 | +0.3499 (genuine — R45) |
2026-09-08-after-the-two-counts-handoff.md:66  assert standalone.score < 0.9654553611484971
                                               — the score [[R174]] superseded — as a live …
2026-09-08-two-loops-sequenced.md:170          under both the stale `0.96546` and the live `0.96589`.
```

A before/after column, a sentence saying *"the score R174 superseded"*, and a sentence saying
*"the stale"*. **Zero is a restatement of a superseded figure as present fact.**

> **Arm (1) would fire 326 times and find nothing.** The wiki gate ships HARD on 0 false positives
> in 11; this is 326 in 326.

## 2. And it is blind to half of R192's own motivating case

R192 exists because one capability line — `graincorp 0.9654 · bfs 0.9401 · WHO 0.9096 · apple
0.6289` — was repeated by eight handoffs with all four figures wrong. **A register-based gate can
see two of the four, and the two it misses fail for two independent reasons neither R192 nor the
[[R187]] spec records:**

| figure | visible to the gate? | why |
| --- | --- | --- |
| `graincorp 0.9654` | **NO** | a **truncation**. `denotes` uses `round`, and `round(0.9654553611484971, 4)` is **`0.9655`** |
| `bfs 0.9401` | **NO** | **deliberately unregistered** — measured under C3, reverted at `51bdd23`, never a reading of any commit on main (`tests/corpus-manifest.ttl:156`) |
| `WHO 0.9096` | yes | rounds correctly |
| `apple 0.6289` | yes | rounds correctly |

The second is not a defect — refusing to register a figure that was never read on main is the
register being right. It is a **structural limit**: the figures most likely to be wrong are the ones
no register will ever carry, and no register-based gate can ever catch them.

The first **is** a defect, and it is live. Measured: **22 occurrences** (21 `evidence`, 1 `code`)
denote a registered reading under truncation and nothing under rounding; **0 in `docs/wiki/**`**.
Its cost is not free either — truncation at 4 decimals is **AMBIGUOUS across this register** (17
distinct of 18 readings; rounding is unique at 4), so accepting truncation needs its own separating
precision, computed under truncation, at 5. Raised as [[R199]].

## 3. The finding under the finding: `cor:readAt` is a refresh log

Every one of R192's three arms presupposes that the register knows **when a figure was read**. It
does not.

```
distinct cor:readAt days in the register: 7
  2026-08-03  2026-08-09  2026-08-20  2026-08-31  2026-09-04  2026-09-05  2026-09-08
```

Seven days, for 95 figure-bearing documents spanning six weeks. The proof that these are **refresh
dates and not reading dates** is a cross-check that should have been empty and is not:

```
evidence occurrences stating a reading FIRST TAKEN AFTER the document's own date:
  109 occurrences in 43 documents
```

`docs/superpowers/2026-08-20-escalation-reason-census.md:67` reports `ons 0.9720`; the register says
that reading was taken `2026-09-05`. The document did not quote the future. **The register recorded
that value sixteen days after the census that measured it**, because `readAt` is written when the
whole corpus is re-run, not when a figure is first observed.

Three consequences, in order of how much they cost:

1. **The obvious criterion is degenerate.** *"Is the document's own date a day this reading was
   taken?"* fails for 260 of 326 occurrences **for a structural reason** — 7 days cannot match 95
   documents — not because those documents restated anything.
2. **The supersession criterion under-counts, and §1's zero is a lower bound.** If a superseding
   reading was first observed before its registered `readAt`, a document written in between states a
   figure that was already stale and is **not** flagged. §1's three residuals are what the
   instrument can see; it cannot see that class at all.
3. **No date-based judgement about a figure's provenance is sound until this is fixed.** That is
   [[R198]], and it is upstream of every arm R192 offers.

## 4. The ruling

**No code ships, and that is the outcome, not a shortfall.**

- **Arm (1) — gate Evidence like wiki: REFUTED.** 326 fires, 0 findings. It would also be
  unrepairable by construction: Evidence is append-only since `5743af3`, so a firing gate can only
  be satisfied by a *new append*, never by a repair — a gate whose only remedy is to write more.
- **Arm (2) — rule that a handoff must cite rather than restate: UNNECESSARY on this evidence.** The
  class it would prevent measures zero. It also could not have prevented the case that motivated it:
  `bfs 0.9401` was not a restatement of a register row, it was a figure that never had one.
- **Arm (3) — leave it: TAKEN**, on the measurement rather than on fatigue.

**What R192 got right, and it matters:** the harm was real. Eight handoffs did repeat four wrong
figures. **What it got wrong is the class.** The harm was not "Evidence restates figures"; it was
that the two figures most repeated were the two no register could check, and nothing measured that
until now.

## 5. What is NOT done

- **The truncation blind spot is not fixed.** [[R199]]. 0 occurrences in `docs/wiki/**`, and its
  single `code`-class instance (`tests/etkl/test_adoption_document.py:371`, `> 0.0606…`) is a
  *mention* of a pin's threshold, not a claim about the corpus — so fixing it now would change a
  running instrument against a population of zero true findings, and would need a second separating
  precision to do it. The [[R188]] shape, declined for the third time on measurement.
- **`cor:readAt` is not repaired.** [[R198]]. It needs per-reading provenance — the commit or day a
  value was first observed — which is a register redesign, not a field edit.
- **The 3 residual occurrences are not repaired.** They are correct as written; each names its own
  staleness in the same sentence. There is nothing to repair.
