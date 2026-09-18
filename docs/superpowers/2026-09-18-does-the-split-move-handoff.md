# Handoff — the split moves, and the only document it was ever traced on cannot show it

**Serves:** maintenance — [[R255]] is named by no `prog:blockedBy`, and neither is [[R258]], raised
here. Declared `maintenance` on purpose, per [[R257]]: the thread this continues spent five loops
declaring a criterion met since 2026-09-13.

**Topic:** the previous handoff's § 5a — *do the two readings disagree?* — answered, and answered
more strongly than a live run could have. On **cbh-stem band 1, 7 of 151 addresses each move the
header/body split on their own**, five of them collapsing it 7 → 1, and **every one is a column
LABEL**. On graincorp-capacity — the only document every live trace in this thread was ever taken
on — **0 of 406** move it. Corpus-wide: **17 of 122 gridded bands, on 5 of the 7 documents.**
[[R255]]'s coherence half is now an observed effect; [[R258]] is raised for the one-address
fragility itself, one of its remedy arms is refuted, and **the maintainer ruled its direction the
same day** — a defect, remedied by an agreement oracle.

**Date:** 2026-09-18. **Branch:** `r255-does-the-split-move`, cut from `main` at `4db5f50`.

**Doc impact: none.**

**Written at ≈ 58k working tokens** (session total ≈ 104k against a ≈ 46k baseline) — over the 50K
originating floor, so part 5 is graded per action, as CLAUDE.md requires.

---

## 5. The next concrete action

*(Part 5 first, per CLAUDE.md § "The handoff's next action is TYPED".)*

### 5a. **ASSERTED** — run arm B's circularity check. The direction is RULED; the construction is not.

**RULED by the maintainer 2026-09-18**, with all three arms priced in front of them: **the collapse
is a DEFECT whatever the ink says**, and the remedy is **arm B** — a header-row address is admitted
only where a second, independent reading agrees. Arm C (rule the collapse intended) and parking the
row were declined.

**The action, and it must come before any oracle is written:** measure whether arm B's own scope is
circular. If a first reading collapses cbh band 1's split from 7 to 1, **there is no header block
left to scope the oracle to** — the oracle's population is decided by the reading it exists to
check. Concretely: take the movers of the COLLAPSED partition (`unshown = {(6, 9)}`, split 1) and
compare them with the movers of the original (split 7). Same instrument, same `--band` mode, no new
machinery.

Why it is asserted: the outcome is unknown, but doing it *is* the work, and it is one command
against a question whose answer decides whether arm B is buildable at all. **This is the same
circularity that killed arm A**, one level up, and arm A took one command to refute.

- **arm A — scope the abstention to body rows.** **REFUTED**, in the loop that proposed it
  (`--scope`): 7 → 6, 4 → 3, 5 → 4, 4 → 3 on cbh's four bands. *Which rows are body* is defined BY
  the split the scope protects, so the first body row is inside the scope by construction and its
  addresses still move it. **A scope cannot protect a boundary it is measured from.**
- **arm B — an agreement oracle.** **CHOSEN.** Admit a header-row address only where a second,
  independent reading agrees — CLAUDE.md's shape for a reading judgement: the effort goes into the
  disposal, not the reader. Its population is discussed in 5b; its buildability is 5a's subject.
- **arm C — rule the collapse intended.** **DECLINED 2026-09-18.**

### 5b. **PROPOSED** — arm B's cost is bounded by the header, not by the band

**The prediction:** an agreement oracle needs to run on the HEADER rows only, so its population is
the split's own header block — **20 addresses against cbh band 1's 151**, an eighth of the band —
and a second reading of a header strip is a smaller crop than the region reading already made.

**Why it is PROPOSED and not asserted:** the figure is arithmetic; the claim underneath it is not.
It assumes the movers stay in the header block once the block is re-derived under the second
reading, which is exactly what 5a measures. **Do not build on this figure before 5a runs** — if the
circularity is real, the population is not 20-of-151, it is undefined.

### 5c. **After R258** — the arc, and it still has not moved

The maintainer's direction of 2026-09-18 stands and is untouched by this loop: return to
**`etkl:05` (bfs) through [[R44]]** — reach 5, the highest in `arc-dependency-landscape.md` § 3,
with its instruments (`scripts/r238_label_identity.py`, `r239_*.py`) already built, and R44's own
triage saying its three escalation reasons share no root cause, so it is three bounded sub-loops.

---

## 1. Where the primaries are

| | |
| --- | --- |
| evidence | `docs/superpowers/2026-09-18-does-the-split-move-evidence.md` — § 2 the finding, § 3 why it was never seen, § 4 the containment, § 6 the refuted arm |
| the instrument | `scripts/unshown_ink_split_sensitivity.py` — `--corpus`, `--band <frag> <pg> <i>`, `--contrast`, `--scope` |
| the test | `tests/test_split_sensitivity_instrument.py` — mechanism, control, null, and the instrument's non-drift from `header_body_split` on both branches |
| the rows | [[R255]] amended a SECOND time, [[R258]] raised — `residues.md` + `residues-open.md` |
| the consumption hop | `src/iladub/etkl/headers.py:111-112` → `celltype.grid_evidence` → `vocab/queries/header-body-split.rq` |
| the lattice fact everything rests on | `src/iladub/etkl/unshownink.py:176` — `dispose` returns `reading.empty_cells & has_glyph` |
| prior loop | `docs/superpowers/2026-09-18-r255-the-seam-that-pays-twice-handoff.md` — its § 5b remedy fork is UNCHANGED and still unchosen |

## 2. What was decided, and where it is recorded

- **[[R255]] stays OPEN, amended twice.** The cost half stands; the coherence half is no longer a
  mechanism but an observed effect, measured offline and exhaustively. Its remedy fork is
  unchanged and still unchosen — that is a design decision and nothing this loop found narrows it.
- **[[R258]] raised** — the split is one-address fragile at the label row, and the fragile
  addresses are exactly the population [[R213]]'s reader is asked about (containment measured
  TOTAL on four bands; corpus scale 17 of 122 bands on 5 of 7 documents). **Its direction was
  RULED by the maintainer 2026-09-18 — a defect, remedy arm B**; arm A is refuted and arm C
  declined, both recorded in the row.
- **§ 5a of the previous handoff was NOT run as written**, and § 1 of the evidence says why in
  full: the live run it prescribed would have produced one sample of a reader that gives three
  answers to one crop, where the disposal's own `& has_glyph` makes the whole space of readings
  perturbable offline. **That is a substitution, not an omission** — and it is the same move a
  plan-supplied test's implementer is told to make when the prescribed form cannot carry the
  claim.

## 3. What is UNVERIFIED, and must not be asserted

- **That the live reader ever proposes a cbh header label.** `dispose` refuses every cbh region
  today (refusal 2, the grid mismatch), so no live reading of these bands exists. § 4 is a BOUND.
- **Arm B's buildability.** The direction is ruled; whether an agreement oracle can be scoped
  without circularity is 5a's subject and is NOT answered here.
- ~~The four documents after graincorp-stem in the corpus sweep.~~ **RESOLVED** — the sweep
  completed: **17 of 122 gridded bands one-address fragile, on 5 of the 7 documents**; full
  abstention moves 32 of 122 and removes the split entirely on six. apple is the only document
  besides graincorp-capacity with no fragile band.
- **Every cost and frequency figure in [[R255]]'s first clause.** No live run was made in this
  loop either.
- **[[R251]], [[R252]], [[R254]], [[R256]], [[R257]] are untouched.**

## 4. Traps this loop paid for

1. **A null measured on the one specimen that cannot exhibit the effect reads exactly like a null.**
   *"No run has shown the split moving"* was true, and every run had been on graincorp-capacity,
   whose split is at the floor with 0 of 406 movers. The question to ask of any null is not *how
   many runs* but **could this specimen have shown it** — R213's own O3 control carries the same
   warning in its plan, and it did not transfer to the next loop's reading of its own evidence.
2. **The effect called unobserved was pinned by a green test in this repo's own suite** —
   `tests/etkl/test_unshown_ink.py:83` has asserted since R213 shipped that an unshown cell moves
   the split to 1. A loop that says *"never observed"* should grep its own tests before the corpus.
3. **The obvious remedy was refuted by its own definition, not by its cost.** Scoping the
   abstention to body rows fails because *body* is defined by the split being protected. Worth
   checking, in any remedy for a derived quantity, whether the guard's own scope is derived from
   the thing it guards.
4. **A first instrument conflated two decisions.** The first version reported one split number, so
   full abstention appeared to "hold at 1" on cbh when in fact the AXIOM had gone silent and
   `_hrule_split` answered. Reporting the two branches apart is what made § 2 legible.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
