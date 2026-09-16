# Ruling — the next loop SHIPS: refuse the decoration universe, blanket

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Doc impact: none.**

Recorded immediately after PR #241 merged (`c9270bb`), in the shape `9ef44d5` / `5e69e94` used for
the two previous rulings. **This note retracts a recommendation I made in a document that shipped
the same hour**, and that is the whole reason it exists — a fresh session reads the handoff first.

## What was ruled

Asked whether the thread was stuck, the maintainer ruled: **the next loop BUILDS.**
`_boundaries_from_decoration` is refused **blanket** — every page falls back to the alignment
universe — and the loop ships behaviour rather than another measurement.

## Why it was ruled: the measurement that prompted it

Measured on `main` at `c9270bb`, counting files touched per merge:

```
$ for c in $(git log main -18 --format=%h); do
    printf "%s src=%s vocab=%s\n" "$c" \
      "$(git show --name-only --format= $c | grep -c '^src/')" \
      "$(git show --name-only --format= $c | grep -c '^vocab/')"; done
```

**18 consecutive merges. ONE touched `src/` (`9785ce3`, 2 files). ZERO touched `vocab/`.**

The register says the same thing from the other side, read off the raise-time snapshots frozen in
the rows themselves — [[R230]] `70/219`, [[R234]] `70/223`, [[R238]] `71/227`, [[R242]] `71/231`:
**twelve rows raised, one closed.**

**Half of that stretch earned its keep and half did not, and the distinction matters.** Three
remedies were refuted *before* being built — [[R239]]'s prescribed `x1` re-key (20 correct cells
regressed), [[R232]]'s both-ends walk (cuts ONS p4's boxhead, manufacturing a fresh [[R166]]), and
the straddle discriminator (a provable no-op, 48/48). Those are shipped defects avoided. What
turned it into a pattern is that **every loop ended by naming a new "first, measure X" subject,
and the next loop honoured it.** The ratchet only ever tightened.

## What this retracts, explicitly

`2026-09-16-r238-label-identity-handoff.md` § 5b proposed measuring [[R241]] — the per-table
column semantics — before any remedy, and that proposal was briefly ruled before being withdrawn.

**It is retracted, on evidence that was already written down when it was made.** [[R241]]'s own
row records that the two-table fusion **pre-exists the switch**: the alternating 27/19 fill
pattern is present under the decoration universe too, at 46 admitted rows either way. It is
therefore **not a cost of the switch** and cannot be a reason to delay it. § 5b even said it "may
be judged orthogonal" — the evidence that it *is* orthogonal was in hand at the time. The
recommendation was the stuck pattern reproducing itself, and it is withdrawn rather than
silently dropped because CLAUDE.md § Doc governance makes Evidence append-only.

## Why BLANKET, and not a conditional scope

**No conditional shape has surviving measured support.** PR #238 ran the straddle discriminator
against all **48** interior boundaries of all three decoration pages, under both readings of the
affected column, and it **dropped nothing** — and the reason was structural, not local to those
pages: the carrier set is 44–46 of 46 admitted rows while straddling is by construction a
minority event, so a universal over nearly-everything of a minority property can only be false.
Inventing a fresh discriminator now would be a **tuned constant**, which CLAUDE.md § 8 makes
*prima facie evidence* that the decision belongs elsewhere — and the defect being repaired IS a
boundary decided by 0.04 pt.

Blanket is also **the only shape whose effect is known rather than predicted**: it is exactly the
configuration PR #239 compiled across all seven documents.

## The oracle — pre-existing, exact, and falsifying

The implementing loop does not need a new instrument. PR #239 and PR #241 already fixed the
numbers this must reproduce:

| | must read |
| --- | --- |
| bfs p5 | **12 columns, 46 rows, 496 placed cells** (from 15c / 404) |
| bfs document | triples **14251 → 15354**; score **0.8850746269**, unmoved to 10 dp |
| bfs p5 identity | **27/27** canton rows by C1 (`scripts/r238_label_identity.py`) |
| the other six documents | **byte-identical by canonical graph hash** |
| adoption / escalation | `[5]` retained; escalated ink 87 → 87; [[R44]]'s reason census unmoved |

**Judge on cells and triples, never on score** — [[R240]]: the score is an ink-token ratio and did
not move a digit while 92 cells appeared.

## The seam the implementer MUST measure — not the answer

Per CLAUDE.md plan rule 3, this names what to check, not what it will find:

- **`datagrid.py:340-349`** fixes the universe ONCE (`bounds, universe = decor, "decoration"`).
  That is the site.
- **`datagrid.py:428-431`** branches on `if universe == "decoration":` for G0
  `tab:SeedFollowsUniverse`, and its own comment records that seeding a decoration universe by
  signature *"cost capacity 19"*. **A blanket refusal makes that branch unreachable.** MEASURE
  what it does today before deleting it or leaving it stranded; do not assume either.
- **`DataGrid.universe`** (`:113`) is a public field. MEASURE every reader of it before assuming
  the string `"decoration"` can never again be produced.
- Producer-side guards are **not** deleted merely because they look redundant — CLAUDE.md
  § Producer-side guards vs the membrane, and [[R102]] is the case that shows why.

## Known risk, accepted on the record

**This corpus holds no page whose decoration rectangle is both adopted AND correct.** bfs p5 is
the only adopted decoration page in it, and it is the defective one, so the corpus **cannot**
produce the counter-example that would refute a blanket refusal — a future document with a
correctly-drawn rectangle would be regressed. This was on the table when the ruling was made and
is accepted, not overlooked. If such a document ever enters the corpus, this ruling is the one to
revisit.

## Deferred by the same ruling — and explicitly NOT blockers

- [[R241]] — one 12-column universe spanning two tables. **Pre-exists the switch**; orthogonal.
- [[R242]] — the label cell fusing the footnote marker (`'Suisse 3'`, `'2010 2'`, `'2011 3'`).
- [[R240]] — the harness reporting cells + triples beside the score. Still an instrument repair.

## Second ruling, same session: author a CARRIAGE CRITERION — and do NOT add R238 to `etkl:05`

Asked whether the register still carries a graph sense of how residues relate, the instruments
answered yes — `residue_graph.py` (232 rows, 250 row→row links, 104 components, hubs by
in-degree) and `arc_depends.py` (criterion→criterion, rendered to a committed cache under a
regenerate-and-diff gate). The follow-up question was sharper: **do we act on it?**

The first answer given in-session was *"name R238 in `etkl:05`'s `prog:blockedBy` so it inherits
reach."* **That is RETRACTED, before it was written into the manifest**, and the retraction is
recorded because the reasoning that produced it is the kind a fresh session would repeat.

**The manifest's own rule refuses the edge** (`tests/arc-manifest.ttl:1155`): *"an edge names a
register row WHOSE CLOSURE WOULD ADVANCE THIS CRITERION. It is not 'a row that mentions this
reason'."* Applied with this thread's own measurements:

| candidate edge | does closing [[R238]] advance it? | the measurement that says so |
| --- | --- | --- |
| `etkl:05` — bfs compiles to `cor:CompilesAbove` above a pinned `cor:scoreFloor` | **No** | [[R240]]: the score is an ink-token ratio and held at `0.8850746269` to 10 dp while 92 cells appeared |
| `tab:02` / `tab:07` / `tab:09` — escalation reasons disposed | **No** | PR #239 § 3c: bfs p5's reason census **identical** — RT_FAIL 5, TILING 1, KIND 1, RESIDUE 1 |

**So R238's absence from the reach table is CORRECT, not a bookkeeping gap** — and CI would not
have caught the error, because M7 only checks the row exists in the register and M21 only that it
is not parked. Both would have passed on a claim our own evidence refutes, inside the arc's
denominator, where a wrong claim propagates into every reach figure.

**The real gap is a missing criterion, not a missing edge: the arc cannot see cell carriage at
all.** It measures score and escalation reasons; nothing in it measures cells carried. Work that
improves carriage is invisible to the arc *by construction* — which is [[R240]] one level up, and
part of why this thread reads as stuck.

**RULED: the next loop authors a criterion whose oracle is CELLS AND TRIPLES, and [[R238]] blocks
that criterion.** It is authored `prog:met false` — the switch is not built when the criterion
lands — and flips only when the build above it does.

### Seams the implementer must measure — not answers

- **Which rung it belongs to is a DECISION, not a lookup.** `prog:blockedBy` exists today **only**
  on the `tab` rung; **no `etkl` criterion carries one**, and `etkl:05` reaches `tab:02` by
  `prog:proposedDependsOn`, a different relation. Choose deliberately and say why.
- **M1 requires exactly one each** of `prog:ofRung`, `prog:statement`, `prog:declaredOn`,
  `prog:source`, `prog:met`, `prog:retrospective`; at most one `prog:metOn`. **M2**: `met true`
  requires `metOn`. **M2b**: `met false` may **not** carry one.
- **M5b is the one that bites first** — the node id in `prog:oracleTest` must **COLLECT under the
  runner**. The test therefore has to exist and be collectable *before* the criterion is authored,
  not after. **M5** requires `prog:oracleArtifact` to exist; **M10** requires `prog:source`'s
  `<path>:<line>` to resolve, and is deliberately the WEAK guard (existence, not content).
- **M7 / M21 on the new edge:** [[R238]] must be present in the register and not parked. It is
  open and unparked today — **re-measure at the time**, do not inherit this sentence as fact.
- **THE TRAP: `docs/superpowers/arc-dependency-landscape.md` is a committed cache gated by
  regenerate-and-diff** (`tests/test_arc_landscape.py`). A new criterion is unmet with no
  dependency read, so it enters §1's *ready* list and moves the **"14 ready"** count. **Regenerate
  the cache in the same commit or CI fails.**
- `prog:source` may point at this ruling as the prose that declares the criterion. That is a
  cross-file citation, so measure-then-write is safe here — CLAUDE.md plan rule 7's re-measure
  hazard applies to *downward same-file* references, which this is not.

### The oracle it must pin

The figures are already fixed by PR #239 and PR #241 and are restated nowhere else in this
document: bfs p5 at **496 cells** and the document at **15354 triples**, identity **27/27**, the
other six documents byte-identical. **Cells and triples, never score** — that is the whole point
of the criterion.

## What the implementing loop owes

A **`## FALSIFICATION` block per task** (CLAUDE.md § Plan authoring discipline rule 4): remove or
invert what each new test pins, show it failing, restore, show the suite green. A test that passes
with its subject deleted pins nothing, and that is the only proof it does.
