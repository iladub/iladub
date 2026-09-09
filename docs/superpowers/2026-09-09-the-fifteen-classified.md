# The fifteen, classified — R192's census finds 2, and its own arithmetic was off by one

Action **5a** of `docs/superpowers/2026-09-09-first-observation-is-recoverable-handoff.md`, graded
ASSERTED. Ten Evidence occurrences were to be hand-read and classified. **There are nine, not ten**,
and the classification is **2 findings / 7 exculpated**.

**Doc impact: none.**

---

## 0. What was asked, and the two corrections it produced

`docs/superpowers/specs/2026-09-09-first-observation-is-recoverable-design.md` §4 measured that
re-dating R192's supersession census by first observation moves **15** undated Evidence occurrences
from *"current when written"* to *"already superseded when written"*. It named seven of them, said
**5 of the 15** sit in the [[R187]] spec and plan (which R192's filename filter already excludes),
and left **10 unclassified**.

Both halves of that split are wrong by one, in the same direction. **It is 6 and 9.**

The spec is **not corrected in place.** It is Evidence, introduced after `5743af3`, and § Documentation
governance makes Evidence append-only prospectively from that commit — a later PR may add, and may
never modify an existing line. So the correction lives here, in a new document, which is the append-only
rule doing exactly the job [[R186]] adopted it for. A reader who opens that spec's §4 will read "5"
and "10"; the register row is where they are told otherwise ([[R192]], amended).

## 1. The 15, reproduced

The census instrument was scratch code in both prior loops and is scratch code again here — that is
deliberate and unchanged (a one-off census committed as a test is a stored label). What it does:
`tests/docgov_extract.extract` over the tree, keep `dg:FigureOccurrence`s whose document is class
`evidence` and whose `dg:blockDated` is `false`, date each document by filename-then-last-commit,
date each reading by `scripts/first_seen.py` rather than `cor:readAt`, and hold R192's own **strict**
inequality on the document's date.

```
undated evidence occurrences: 329 in 87 docs

superseded under readAt      : 48        ← R192's count
superseded under first-obs   : 63
MOVERS (current -> stale)    : 15        ← the spec's 15, reproduced exactly
```

**The denominator moved 328 → 329 for the reason §4.2 of that spec predicted for its own step.** A
census cannot see the document it is written in. This runs at `d0db4ac`, which committed the previous
loop's record; the one new occurrence is
`docs/superpowers/specs/2026-09-09-first-observation-is-recoverable-design.md:184` — that spec quoting
`0.6289`. `d0db4ac` itself touched only `scripts/first_seen.py`, so no Evidence line changed and the
mover set is the same 15 at both commits.

**And one step on, from this document.** Re-run with this loop's own record and handoff tracked and the
population reads **338 in 88 docs**, 56 superseded under `readAt` and 71 under first observation —
the same self-blindness again, and the number a successor would quote. **The mover count is unchanged
at 15**, because everything these two documents quote was already superseded under *both* schemes. The
fires figure grows every loop; the ratio is the durable claim, and 329 is the honest denominator for a
census that could not see itself.

**NULL CONTROL.** Running the identical script with first observation replaced by `cor:readAt` on both
sides scores **0 movers** and 56/56. The 15 are produced by the change of dating scheme and by nothing
else in the instrument.

## 2. The split is 6 and 9, not 5 and 10

R192's filename filter excludes documents whose **subject is** the stale figure. Among the 15 that is
the [[R187]] spec and plan, and they carry **six** occurrences on **four** lines:

```
docs/superpowers/plans/2026-09-08-a-figure-carries-its-date.md:85          0.1895  0.6289
docs/superpowers/specs/2026-09-08-a-figure-carries-its-date-design.md:75   0.1895  0.6289
docs/superpowers/specs/2026-09-08-a-figure-carries-its-date-design.md:86   0.1895
docs/superpowers/specs/2026-09-08-a-figure-carries-its-date-design.md:133          0.6289
```

Two lines carry two figures each. **Four lines, six occurrences** — the spec counted lines where the
census counts occurrences, and 15 − 6 = **9** residual.

## 3. The criterion, and where it comes from

R192 published two exculpations: *the document's subject IS the stale figure* (the filename filter,
§2 above), and *the sentence names its own staleness*. The second needs a reading, and R192 never
wrote one down — so it is derived from the three cases R192 actually exculpated
(`2026-09-09-the-register-is-a-refresh-log.md` §1):

```
| who | 0.5597 | 0.9096 | +0.350 | ...        ← 0.5597 shown AS the "before" column
assert standalone.score < 0.9654553611484971  ← "the score [[R174]] superseded"
under both the stale `0.96546` and the live `0.96589`.
```

**All three name the specific figure.** None is a blanket caution over a block. So the criterion R192
applied, stated:

> **Does the passage tell its reader that THIS figure may not be current?** If yes, the figure is not
> stated as present fact and the occurrence is exculpated. If the passage instead affirms currency —
> including by enumerating which figures are stale and leaving this one out — it is a finding.

The second clause is what decides this classification, and it is stated before the reading rather than
after it.

## 4. The nine

| # | occurrence | verdict | why |
| --- | --- | --- | --- |
| 1 | `2026-09-04-r173-bisect.md:153` `0.3556` | exculpated | Quotes `0.3556` as the floor a **test pins** (`test_the_document_score_rises`), and the same bullet states the base measured `0.18950437317784258` and the merge takes apple to `0.6289`. Not a currency claim at all. |
| 2 | `2026-09-05-r174-stem-denominator.md:22` `0.96545…` | exculpated | The code block is captioned `^ the pinned test value    ^ what the tree reads today`. Also (a): the document's subject IS that supersession. |
| 3 | `2026-09-08-r61-handoff.md:70` `0.6289` | exculpated | *"these four figures are quoted from prior handoffs, **not re-measured today**"*, and the action is graded PROPOSED. |
| 4 | `2026-09-08-r185-handoff.md:61` `0.6289` | exculpated | *"still not re-measured"*; *"quoted through **four** handoffs without re-measurement"*. |
| 5 | `2026-09-08-release-v0-0-4-handoff.md:65` `0.6289` | exculpated | Heading: *"carried forward UNCHANGED and still unmeasured"*. The weakest of the four — it goes on to name graincorp and the `0.3556` wiki figure as the stale ones — but the blanket survives in its own heading and is never withdrawn. |
| 6 | `2026-09-08-release-v0-0-4.md:153` `0.6289` | exculpated | *"quoted through **five** handoffs now without re-measurement"*. |
| 7 | `2026-09-08-r187-closed-handoff.md:40` `0.6289` | exculpated | *"is **wrong in all four figures** (spec §1.4)"*. The strongest. |
| 8 | `2026-09-08-after-the-two-counts-handoff.md:76` `0.6289` | **FINDING** | §5 |
| 9 | `2026-09-08-two-loops-handoff.md:77` `0.6289` | **FINDING** | §5 |

## 5. The two findings: a blanket warning replaced by an enumeration that omits the figure

Rows 8 and 9 are the two handoffs that stopped saying *"unmeasured"* and started saying *"measured,
and here is which parts are stale"*. Both carry the capability line, and both then account for it
figure by figure:

```
### 5d. PROPOSED — the capability claim, carried forward and now DEMONSTRABLY part-stale
...
5a **measured** what previous handoffs only warned about: `graincorp 0.9654` is superseded
([[R174]], `0.9658886894075404`), and the apple figure quoted alongside it in `data-grid.md` is
superseded by [[R165]]. **`bfs 0.9401` and `WHO 0.9096` remain unchecked entirely.**
                                    — 2026-09-08-after-the-two-counts-handoff.md:71-81
```

```
`graincorp 0.9654` is superseded ([[R174]] → `0.9658886894075404`) and the apple figure quoted
beside it in `data-grid.md` is superseded by [[R165]]. **`bfs 0.9401` and `WHO 0.9096` have still
never been re-measured** — eight handoffs now.
                                    — 2026-09-08-two-loops-handoff.md:80-82
```

**"The apple figure quoted alongside it in `data-grid.md`" is a different figure.** MEASURED —
`docs/wiki/concepts/data-grid.md:206-207` reads:

```
Measured movement at document scope (**readings of 2026-08-09**): **apple
`0.06068601583113457` → `0.35560344827586204`**; stem unchanged at `0.9654553611484971`,
```

so the apple figure sitting beside graincorp's in that page is **`0.3556`**, not the `0.6289` in the
handoff's own block. Each passage therefore assigns a status to all four figures of the line —
graincorp stale, bfs unchecked, WHO unchecked — and assigns `apple 0.6289` none, which in a paragraph
whose whole purpose is to say *which parts are stale* reads as: this one is fine.

**It was not fine, and the repo already knew.** `0.71875` — apple's document score — entered `main`
on **2026-09-07** at `f42ef99` (PR #166, R176), stated in two places in that merge:

```
docs/superpowers/2026-09-07-r176-handoff.md:113   the document score's rise to `0.71875`
tests/etkl/test_adoption_document.py:380          2026-09-07: reads 0.71875 = 276/384, by [[R176]]
```

The register attributes `0.71875` to exactly one site, `specs/2026-09-08-a-figure-carries-its-date-design.md`,
with `cor:readAt "2026-09-08"`. **That is the mechanism, in one line:** the value was a day old and
already twice-recorded in the tree when those two handoffs were written, and the only instrument that
could have said so recorded it as same-day, so R192's strict inequality discarded it and scored the
motivating case 0.

### 5.1 The steelman, stated rather than buried

Both passages carry *"part-stale"* in their own heading, so a reader who reads only the heading is
warned. Under a looser reading of exculpation (b) — *any* caution attached to the block exculpates —
these two join the other seven and the count is **0**. That reading is rejected because R192's own
three exculpations are all figure-specific (§3), and because the paragraph is the more specific and
later statement: *"part-"* is a promise that the parts will be named, and they are.

**Either way the count is 0 or 2 of 329**, and nothing downstream turns on which — see §6.

## 6. What this does to R192's ruling: nothing, and that is the result

Arm (1) re-dated and fully classified scores **329 fires / 2 findings** — a 99.4% false-positive rate,
against the 0-of-11 that licensed the wiki gate. R192 refuted arm (1) on 326/0; the sound number is
worse for the gate, not better, because the denominator grew and the numerator did not reach 3.

**Arm (3) — leave Evidence ungated — stands, on both of its grounds.** The append-only ground was
always sufficient alone (a gate that fires on Evidence can only ever be satisfied by a new append,
never by a repair), and the hit-rate ground, which the previous loop correctly withdrew as
uncomputed, now returns and points the same way.

**What may now be cited, precisely.** Not *"326 fires, 0 findings"* — that was measured by a blind
instrument. The citable figure is **329 fires, 2 findings, both of them the capability line the
residue was raised about**. The residue's harm was real and is now counted; its proposed remedy is
still refuted.

## 7. What is NOT done

- **The two findings are not repaired, and cannot be.** Both documents are Evidence, both post-date
  `5743af3`, and § Documentation governance forbids modifying an existing line. This document is the
  repair the rule permits.
- **No gate ships, and none is proposed.** §6 is the argument against one; [[R200]] is the argument
  against the neighbouring one.
- **The 48 already-superseded-under-`readAt`** are not re-classified. R192 classified them (45 by
  filename filter, 3 by hand) and nothing here disturbs that work; only the 15 movers were open.
- **[[R199]] is untouched.** No truncation and no unregistered figure was measured in this loop.
