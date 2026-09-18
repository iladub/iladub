# Handoff — the oracle's scope is circular in the obvious reference and sound in the one beside it

**Serves:** maintenance — [[R258]] is named by no `prog:blockedBy`, and neither is [[R255]].
Declared `maintenance` deliberately, per [[R257]].

**Topic:** the previous handoff's § 5a, ASSERTED, run as written. [[R258]]'s ruled remedy (arm B,
an agreement oracle) needs to know which addresses are header rows. **The reference it would reach
for first — the split the pipeline returns — is circular, totally so**: on cbh-stem band 1 the
header block goes 21 addresses → 1 the moment any label abstains, and the collapsing address is
scoped as *body* by the split its own abstention produced. Corpus-wide that reference collapses on
14 of 17 fragile bands. **A collapsed split is also a FIXED POINT**, so no second-order probe
recovers it. But a second reference was available all along — the **abstention-free** split
(`unshown = ()`, same query, same graph) — and it holds **71 of 80 corpus movers with zero
collapses escaping**. Arm B is buildable. It is not built.

**Date:** 2026-09-18. **Branch:** `r258-is-arm-b-circular`, cut from `main` at `6e5893f`.

**Doc impact: none.**

**Written at ≈ 60k working tokens** (session total ≈ 106k against a ≈ 46k baseline) — over the 50K
originating floor, so part 5 is graded per action, as CLAUDE.md requires.

---

## 5. The next concrete action

*(Part 5 first, per CLAUDE.md § "The handoff's next action is TYPED".)*

### 5a. **ASSERTED** — whatever arm B becomes, its scope is the ABSTENTION-FREE split

This is settled by measurement and is not a design choice left to the implementer. The oracle's
population must be `header_body_split(replace(band, unshown=()), grid)`, never
`header_body_split(band, grid)`. The two differ by one argument at `headers.py:111-112` and by
everything that matters:

| | perturbed (the returned split) | free (`unshown = ()`) |
| --- | --- | --- |
| cbh band 1 header block | **1** address | **21** addresses |
| corpus bands where it survives | **1 of 17** | all |
| corpus movers inside it | — | **71 of 80** |
| collapses escaping it | all | **0** |

Why it is asserted: the outcome is already known — evidence §§ 2-3, 7 — and three tests in
`tests/test_split_sensitivity_instrument.py` pin it on a fixture CI can see, each one falsified
before it shipped. An implementer does not need to re-derive this; they need to not undo it.

### 5b. **PROPOSED** — the oracle is a label-row question, and its cost is an eighth of a band

**The prediction:** arm B's second reading is asked only about the addresses of the free header
block — 21 of 151, 18 of 222, 19 of 191, 18 of 82 on cbh; 12 of 89 on who; 26 of 612 on
graincorp-stem — and within that block only the **label row** matters, because every collapse
measured anywhere in the corpus is a column label (`'Volume'`, `'ETD'`, `'Month'`, `'-3 SD'`,
`'S243'`, `'Total'`). So the question put to the second reading is small, closed and the kind a
human answers at a glance: *is this cell's ink shown?* — asked of one row.

**Why it is PROPOSED and must be RUN before anything is built on it:** *in-block* does not mean
*collapsing*. `graincorp-stem` p0 b2 `(3,7) 'Commencement'` is inside the free header block and
moves the split 4 → 3 rather than collapsing it, so an oracle scoped to the label row would be
asked about it too and the cost figure is a floor, not a ceiling. The implication measured is
one-directional — **collapsing ⇒ in-block** — and a design that assumes the converse is assuming
something this loop refuted.

**Also unresolved, and cheap to settle first:** `ons` page 0 band 1 is the corpus's only upward
mover (`(1,3) '14 May 2026'`, split 1 → 6) and its only non-fixed-point. Nothing here explains it,
and an oracle that treats the free split as a generous upper bound is assuming it cannot happen.
One `--band ons-index 0 1` and a look at the query's `s_col` arithmetic answers it.

### 5c. **A FORK for the maintainer — arm B, or back to the arc**

Both directions are the maintainer's own, and this loop discharges the condition that separated
them. The previous handoff's § 5c said *after R258, the arc*; § 5a was the thing owed first. It is
now paid, and **R258 is not closed** — arm B's reading and its disposal are unbuilt.

- **Build arm B.** The scope is settled (5a), the population is bounded (5b), the falsifier is
  already in CI. What is missing is the second reading itself and what disposes it — and per
  CLAUDE.md § "One geometric attempt, then NEURAL" the effort goes into the disposal, not the
  reader. **Not reachable live**: `dispose` still refuses every cbh region (refusal 2), so arm B
  would ship against the offline lattice and the fixture, not against a live reading.
- **Return to the arc: `etkl:05` (bfs) through [[R44]].** Reach 5, the highest in
  `arc-dependency-landscape.md` § 3, instruments already built (`scripts/r238_label_identity.py`,
  `r239_*.py`), and R44's own triage says its three escalation reasons share no root cause — three
  bounded sub-loops. Untouched by this loop.

The second bullet is the standing direction and needs no new ruling to resume; the first needs one
only if it is to jump the queue.

---

## 1. Where the primaries are

| | |
| --- | --- |
| evidence | `docs/superpowers/2026-09-18-is-arm-b-circular-evidence.md` — § 2 the circularity, § 3 cbh's exact separation, § 4 the refuted population figure, § 7 the corpus, § 8 falsification |
| the instrument | `scripts/unshown_ink_split_sensitivity.py` — new mode `--circularity [doc]`, beside `--corpus`, `--band`, `--contrast`, `--scope` |
| the tests | `tests/test_split_sensitivity_instrument.py` — three new pins: the circular scope, the non-circular one, the fixed point |
| the row | [[R258]] amended (not closed) — `residues.md` + `residues-open.md` |
| the one site both references run through | `src/iladub/etkl/headers.py:111-112` — `unshown=band.unshown` into `celltype.grid_evidence` |
| prior loop | `docs/superpowers/2026-09-18-does-the-split-move-handoff.md` — its § 5a is what this ran |

## 2. What was decided, and where it is recorded

- **[[R258]] stays OPEN, amended.** The circularity is confirmed for the perturbed reference and
  dissolved by the free one. The row records both, the corpus figures, and that arm B's reading
  and disposal are unbuilt.
- **The instrument gained `--circularity`** rather than a scratch script, because the figure it
  prints is the one the row now quotes and the register is entitled to a command that reproduces
  it. ≈ 47 min over the corpus.
- **Nothing was raised.** This loop found no new residue: the circularity it measured was already
  named in [[R258]]'s row as the open question, and the answer closes that question without
  opening another.

## 3. What is UNVERIFIED, and must not be asserted

- **That the free split is the RIGHT split.** It is the pre-reading state — every glyph counted as
  shown. It is used as a **scope**, where generous is the safe direction. Nothing licenses it as
  an answer.
- **That an agreement oracle can be built.** § 5a of the previous handoff asked only whether it
  has a non-circular population. It does. The reading and its disposal are undesigned.
- **Why `ons` page 0 band 1 moves UP.** The corpus's single upward mover and single
  non-fixed-point, measured and unexplained (5b).
- **That any of this is reachable live.** `dispose` refuses every cbh region today; these bands
  have no live reading, and every figure here is offline-exhaustive rather than observed.
- **Every cost and frequency figure in [[R255]]'s first clause.** No live run in this loop either.
- **[[R251]], [[R252]], [[R254]], [[R256]], [[R257]] are untouched.**

## 4. Traps this loop paid for

1. **An inversion that fails *some* test is not an inversion of *this* test.** The first attempt at
   falsification B wrote `((1,1),) if band.unshown else band.unshown`, which leaves the
   `unshown=()` path untouched — the abstention-free test stayed green while an unrelated one went
   red, and the run reads as a successful falsification at a glance. **Read the failure list for
   the named test**, not the exit status. Evidence § 8.
2. **A near-equal figure from the wrong population.** § 5b predicted 20 header addresses; the
   answer is 21, and the 20 was the low-contrast set from R258's own row — overlap 16, on all four
   cbh bands. A figure that is right to within one is the hardest kind to catch.
3. **`set -- $a` does not word-split in zsh.** Three `--band` runs silently printed the module
   docstring instead of measuring, because the argument count never reached 4. The known
   `zsh-unsplit args = phantom green` trap, met again in a new shape — a loop over a list of
   argument triples.
4. **A fully-buffered background run shows 0 bytes for 47 minutes.** `wc -c` on the redirect said
   nothing was happening; `ps -o time,rss` said 31 minutes of CPU at 97 MB. **Check the process,
   not the file**, before concluding a long run has hung.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
