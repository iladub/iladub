# Reading a table as constraint satisfaction — design

**Date:** 2026-08-08 · **Status:** draft, pending adversarial review ·
**Specimen:** `corpus/financial/apple-fy2026q3-statements.pdf` page 0 ·
**Supersedes the framing of:** `2026-08-07-producer-signature-design.md` (blocked at review;
its premises are corrected here)

**Doc impact:** increment — new sensors and constraints in the owned `tab:` namespace; no new
table classes. No site page contradicted.

## 1. The protocol, as a human actually reads it

Reported by François reading apple page 0, then verified against the ink:

> The zebra tells me where the grid is. Above it, horizontal lines at the bottom of the cells.
> One column on the left for hierarchised aggregation — I get that from the indentation, so the
> table is pivoted following hierarchies. The header is multiline with wrapped text, structured by
> horizontal lines only; I don't need vertical lines because there are vertical gutters. And I see
> a hierarchy in the horizontal lines themselves: two main groups at the top, each split into two
> columns — that's my tree. Lower down, horizontal lines separate individual metrics from
> aggregated ones, and **double lines** mark a net result ending a semantic section.

### 1.1 Every element measured on apple page 0

```
y=104   303───────────431      435───────────563     2 PARENT spans, each over 2 columns
y=125   303──365 369──431      435──497 501──563     4 LEAF spans, one per column
y=140   ▓▓▓ zebra begins ▓▓▓                         the DATA zone starts
y=168+  50────303  +  the 4 measure columns          stub span + measures
y=414/416/417   DOUBLE RULE at 303, 369, 435, 501    net result / section end
y=632/634/635   DOUBLE RULE                          again
y=746/748       DOUBLE RULE                          again
```

- **Banding locates the grid.** Grey bands run y=140→732; everything above is header structure.
- **The header tree is in the rule spans.** Two continuous rules over two columns each, then four
  individual rules one per leaf — `tab:HeaderNode` / `tab:parentHeader` / `tab:coversColumn` read
  straight off the ink. Those terms already exist.
- **Gutters replace vertical rules.** The 4pt segments at 365–369, 431–435, 497–501 are the
  gutters. **Zero vertical rules on the page**, yet every column boundary is explicit.
- **Double rules mark semantic section ends**, at exactly the four measure columns.
- **The stub is the 50→303 span**, present in data rows and absent from the header — which is
  precisely why today's `nhw == ncols` test fails.

## 2. The architecture: sense selects, it does not follow

The reading above reads like a sequence but was not produced as one. François's account of arriving
at it:

> All kinds of signals fired, all looking for some sense. Our brain looks for sense, and sense
> leads how the signals should be combined and interpreted. It's iterative — it wasn't clear at
> time 0; it took seconds to capture the signals, then figure out the spatial agency. These are
> concurrent processes that finally build a sequence, scored against sense. A naive image is
> sudoku: test candidates iteratively until they match the rules.

**This is the correction to every previous draft.** Drafts 1–7 drew decision trees walked in
order. A tree commits at each node and cannot revisit — which is exactly how the shipped pipeline
fails: `classify` decides `UNSUPPORTED_TABLE` and nothing downstream can reconsider, even though
the assignment "this block's header lives in the block above" satisfies every constraint.

The model is **constraint satisfaction over role assignments**:

```
signals fire CONCURRENTLY, each proposing candidate role assignments
        ↓
constraints prune candidates and propagate consequences
        ↓
iterate until one assignment satisfies every constraint  → the reading
        or no assignment does                            → escalate, NAMING the
                                                            constraint that failed
```

The order in which judgements resolve is a **trace**, recorded in the decision holon — not the
algorithm. Two documents may resolve the same constraints in opposite orders and both be right.

### 2.1 Non-textual evidence is privileged — start there whenever it exists

Signals fire concurrently, but they are not equally trustworthy, and the ranking follows from the
authoring order: **compute → pivot → subtotal → band → border**. Decoration is applied *last*, once
the author already knows the structure, and it is applied *deliberately to make that structure
legible*.

Two consequences:

- **Rules and fills carry structure and nothing else.** A word is content, and its position is
  structure — the two are entangled and every inference from text must disentangle them. A rule
  carries no content at all. It is pure structural annotation, so its signal-to-noise for structure
  is the highest on the page.
- **It is the author's own statement of the answer.** apple's header tree is recoverable from rule
  spans because the author drew exactly the tree they wanted read. We are not inferring their
  intent; we are reading the annotation they added for that purpose.

So the solver **seeds from non-textual evidence wherever it exists**, and falls back to alignment,
typography and datatype only for what the decoration does not settle. This is the inverse of the
authoring order, and it is why the reading protocol in §1 begins with the zebra and the rules
rather than with the words.

**When it does not exist**, the fallback is not optional: two corpus documents (`bfs`, `ons`) draw
no rules and no fills at all. There, alignment and typography carry the whole load, and the solver
must reach the same constraint set by a different route — or escalate naming the constraint it
could not satisfy. See P6.

### 2.2 Spatial agency is relative to the table, never to the page

Signals are read against the table object's own extent — its top, bottom, left, right, centre — not
against page coordinates. A rule "about one column wide, above the data zone" is a header underline
at any scale. This is the anti-magnitude rule restated: **every measurement is a ratio or an
ordinal within the table's own frame.**

## 3. What constitutes sense

A candidate reading is valid iff all of these hold. They are the sudoku rules.

| # | Constraint | Already in the repo? |
| --- | --- | --- |
| C1 | Every data cell is addressable by exactly one column path × one row path | `tab:` header-path model |
| C2 | The header tree covers every measure column, and only those | partially — `tab:coversColumn` |
| C3 | The stub accounts for every data row | — |
| C4 | Every glyph is accounted for — nothing silently dropped | **yes** — the conservation shape |
| C5 | An aggregate reconciles exactly with the members it covers | **yes** — exact Decimal arithmetic |
| C6 | The reading regenerates the observed ink | **yes** — `tab:ReshapeRecipe` round trip |
| C7 | A block with no header of its own inherits one, or escalates | — (the apple failure) |

C4, C5 and C6 already exist and are already enforced. **The architecture is not new machinery; it
is using the machinery we have as a solver rather than as a series of gates.**

## 4. First slice

Read the header tree from rule spans, and the data zone from banding, on apple page 0 — the
smallest complete instance of the architecture, and the one that exercises §2.1's privileged
evidence directly. **All four sensors below read non-textual ink only**; not one of them looks at a
word. That is the point: if the decoration alone yields the header tree, the text never had to be
disentangled.

1. **Data-zone sensor.** The banded run bounds the data; ink above it is header structure. Emits
   `tab:dataZoneStartsAt`.
2. **Rule-span sensor.** Classify each rule by its span *relative to the table's own width*:
   covering several leaf columns ⇒ a parent header node; covering one ⇒ a leaf; covering the stub
   plus all measures ⇒ a row separator. Emits `tab:HeaderNode` + `tab:parentHeader` +
   `tab:coversColumn` — existing terms.
3. **Gutter sensor.** Column boundaries from the gaps between rule segments where no vertical
   rules exist. Emits the leaf-column boundaries.
4. **Double-rule sensor.** Two rules within a small vertical distance sharing an x-span mark a
   section end. Emits `tab:SectionBoundary`.
5. **The constraint C2** then admits a header tree only when it covers exactly the measure columns
   — which is what makes an **unheaded stub** legal, and is the fix `nhw == ncols` needs.

The solver for this slice is small: candidates come from the four sensors, C2 and C4 prune, and a
consistent assignment yields the header tree.

## 5. Premises

| # | Premise | Status |
| --- | --- | --- |
| P1 | apple p0's header tree is recoverable from rule spans alone | **holds** — §1.1, two parent spans and four leaf spans measured |
| P2 | Banding bounds the data zone | **holds** — bands y=140→732; all header rules above |
| P3 | Column boundaries are recoverable from gutters without vertical rules | **holds** — zero vertical rules, gutters at 365–369, 431–435, 497–501 |
| P4 | Double rules mark section ends | **holds structurally** — three occurrences at the four measure columns; that they mean *net result* is inferred, not measured |
| P5 | `nhw == ncols` fails because the stub is unheaded | **holds** — apple p1 block 2: 2 header words, 3 columns, stub unlabelled |
| P6 | These sensors generalise beyond apple | **NOT MEASURED** — stem has 8 full-width rules only; CBH and capacity are lattices; **two corpus documents (bfs, ons) draw no rules or fills at all** and cannot use them |
| P7 | Fixing the header tree moves apple's score | **NOT MEASURED** — a prior review traced a rejoin landing flat; this slice changes `classify`, which that trace did not cover |

**P6 is the one to attack first.** Two of the seven corpus documents have no rules and no fills, so
a rule-span header sensor is inert on them. The architecture must degrade to other signals there,
or the slice is apple-shaped.

## 6. Success criteria

- apple p0's header tree is recovered from rule spans: two parents, four leaves, matching §1.1.
- The data-zone boundary is derived from banding, not from a whitespace gap.
- Column boundaries are derived from gutters, with zero vertical rules present.
- **C2 admits a header tree with an unheaded stub**, and `classify` stops rejecting apple's header
  block for the `nhw == ncols` reason.
- **apple's document score moves upward from 0.0606860158**, or the loop reports plainly that it
  did not and why — a structural win with a flat score is a result, not a failure, but it must be
  stated rather than presented as success.
- stem 0.9655 / 2152 / chain [3], CBH 0.9047, capacity 1.0000, WHO 0.5597 **unchanged**. This slice
  touches `classify`, which every document passes through: the risk is real and must be measured,
  not assumed.
- No tuned constant. Every span test is a ratio against the table's own width; "within a small
  vertical distance" for double rules must be expressed relative to the document's own rule
  spacing, or the double-rule sensor is dropped from this slice.

## 7. Out of scope

- The producer-signature sensor. The prior review established that within-producer variance exceeds
  between-producer variance (stem and capacity share byte-identical metadata and differ in
  signature), and that no constant-free rule separates more than three classes. **Grid primitives,
  not producers**, is the correct target and this spec adopts it.
- `tab:RejoinSectionsOp` as a `tab:ReshapeOperation`. Measured: apple's stub banding runs unbroken
  from y=135 to y=726 with zero gaps — **the producer emitted one continuous table and iladub's
  own segmenter split it**. That is a segmentation repair, not the inverse of an authoring
  operation, and it is mis-filed under the reshape vocabulary.
- The full solver. This slice runs a small constraint set over four sensors; a general solver over
  all of C1–C7 is a later loop.
- Reading the *meaning* of a double rule (net result, section end). We can detect the mark; naming
  what it means is domain interpretation and needs its own evidence.

## 8. Global constraints (carried, per CLAUDE.md)

- Neurosymbolic gate §8: sensors emit evidence; constraints are AXIOMs over it. **No tuned
  constant** — ratios and ordinals within the table's own frame only.
- §7 only emit what the source supports: where no assignment satisfies the constraints, escalate
  and **name the constraint that failed** — a strictly better escalation than `UNSUPPORTED_TABLE`.
- The decision holon records the trace: which signals fired, which candidates were pruned, and by
  which constraint. The order is evidence, not method.
- Source ownership: `tab:` is ours; no HGA term appears as a subject.
