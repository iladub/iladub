# Handoff — the re-ruled walk was measured before it was built, and it is refuted

**Serves:** prog:criterion:etkl:04 — ONS. The criterion's subject is column identity, which is
exactly what the refuted mechanism destroys.

**Date:** 2026-09-15. **Tree:** branch `r232-both-ends-refusal-walk`, cut from `main` at `45480de`.
**No shipped file was edited. No behaviour changed.**

**Doc impact: none.**

**§ 5 is graded per action, because this handoff was authored OVER the originating floor**
(`plimslop preflight --shape originating --tokens 55000 --decision proceed` → OVERRIDE, logged).
Parts 1–4 are pointers and records and do not degrade.

---

## 5. The next concrete action

### 5a. ASSERTED — do NOT build the both-ends refusal walk. It is refuted, and the ruling needs revisiting

The mechanism does what § 8c said: fires on exactly one band corpus-wide (`ons p4 b0`, `L=6 T=1`,
`ncols 1→6`), no tuned constant, inert on the other six documents at document scope. **And four of
its seven cut lines are the column header.** The table it then asserts carries `Jan 2024`, `-0.1`,
`-0.3`, `0.2`, `0.1`, `-0.2` as its six `tab:HeaderNode` labels — a fresh instance of open defect
[[R166]], on the one criterion whose subject is column identity.

This is mechanical to verify and does not rest on a prediction: every figure is in
`2026-09-15-both-ends-walk-refuted-evidence.md`, re-runnable from the two scratch instruments
described in its § 6. The previous loop's § 6 stated the rule this follows — *a refuted premise
means revisiting the ruling rather than implementing.*

**The maintainer's re-ruling in § 8e rests on § 8d's claim** that *"within [rules-free] scope the
walk fires once and cuts no header anywhere."* On the single band it fires on, that claim is false.
**§ 8e is therefore open again, and only the maintainer can close it.**

### 5b. ASSERTED — the gutters are closed by the FURNITURE, and the real blocker is now named

`(L,T)=(2,1)` — cut the two furniture lines and the trailing `Source:` line, keep the boxhead —
reaches **the same `ncols=6`**. The walk's four extra lines of depth buy no column and cost the
whole header. So § 8b's *"the leading furniture is what closes the gutters"* is right about the
cause and wrong about the extent.

What `(2,1)` exposes is the actual obstacle, raised as **[[R234]]**: a four-line wrapped boxhead,
**18 words against 6 columns**, which the header reader cannot split — `UNSUPPORTED_TABLE`, region
0 `superseded`, 0 cells, document `0.7712418301 → 0.7522123894`, denominator 765 → 1017. **The
honest cut scores BELOW baseline**, and that is the finding: the walk's `+0.0351` is bought by
discarding column identity, not by reading the table.

### 5c. PROPOSED — the next subject is the wrapped boxhead, and it has NOT been attacked

**Rests on a judgement that may not survive contact.** [[R234]] looks like the right next subject
because it is the thing standing between ons p4's real table and an honest assertion, and because
[[R226]] and [[R166]] are the same family. But **nobody has measured whether a multi-line boxhead
reader is constructible here**, and § 8d's Option-B experience is the warning: the obvious
header-derivation route was already found circular (`header_body_split` returns `None` at
`ncols=1`). `(2,1)` changes that starting condition — at `ncols=6` the split is no longer being
asked for at `ncols=1` — but *that this makes it constructible is a guess, not a measurement.*

**Run that first, before any spec**: with the band cut `(2,1)`, does `header_body_split` return a
split at all, and do the four header lines carry 6 recoverable labels? If it abstains, [[R234]] is
a different problem than it looks and the next loop should say so rather than build.

### 5d. ASSERTED — what this session must NOT be read as having done

No code, no spec, no plan, no contract, no shipped instrument, no `cor:reading`. ons still carries
no `cor:scoreFloor`, stays `cor:Unadjudicated`, and its 2026-08-20 HOLD is untouched — nine pages
still unread against the compile, still no contract/terms/shapes. **etkl:04 was not advanced.**
[[R230]] is corroborated, not refuted. The two scratch instruments live in the session scratchpad
and were deliberately not committed (§ 3).

---

## 1. Where the primaries are

- **The evidence** — `docs/superpowers/2026-09-15-both-ends-walk-refuted-evidence.md`. Every figure
  below is measured there, with the method and the re-run recipe in its § 6.
- **The rows** — [[R232]] (amended today with the refutation), [[R233]] (amended: no longer
  latent), [[R234]] (raised today) in `residues-open.md` / `residues.md`.
- **What was ordered** — `2026-09-15-two-ended-peel-refuted-handoff.md` § 8e, on `main` at
  `45480de`. Read § 8d alongside it: that is the claim this loop falsified.
- **The seam** — `compile.page_bands`, whose only internal call site is `compile.py:820`.
  `document.py:111` binds a separate name at import; patching that one alone is a no-op (§ 6 of
  the evidence — this loop made that error).
- **The band** — ons p4 band 0, 32 lines / 252 words, rules-free. `page_bands(P, 4)[0]`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The both-ends walk cuts the boxhead on the one band it fires on — do not build it | evidence § 2, [[R232]]'s row |
| The asserted labels are `Jan 2024 / -0.1 / -0.3 / 0.2 / 0.1 / -0.2` — a new [[R166]] instance | evidence § 2.1 |
| `(2,1)` reaches the same 6 columns with the header kept; furniture closes the gutters | evidence § 3, [[R234]] |
| The honest cut scores BELOW baseline (0.7522 vs 0.7712) | evidence § 4, [[R234]] |
| The walk is inert on the other 6 documents at document scope | evidence § 5 |
| [[R233]]'s ambiguous-ink hazard is live, not latent (1 band abstains) | evidence § 1, [[R233]]'s row |
| A walk must precede `compile.py:447`; the merge partition cannot be perturbed | evidence § 6 |
| Whether § 8e's re-ruling stands | **undecided — 5a puts it back to the maintainer** |

## 3. Unverified or assumed

- **§ 5c entirely**, per its grading. Nobody has run `header_body_split` on the `(2,1)` band.
- **`superseded` is reported verbatim, not explained.** `(2,1)` leaves region 0 `superseded` with 0
  cells; *which* region supersedes it, and why, was not measured.
- **The `+7 escalated` on the walked region is inferred, not traced.** Document escalated moves
  175 → 182 and the walked region books `168/7`; that the 7 are the cut lines' ink is consistent
  with every figure but was not proven line by line.
- **Carriage was measured only at document scope.** Variants A (drop) and B (leading →
  `Band.captions`) are identical on score, cells and tokens; whether B pollutes candidate keys was
  reasoned from `feed.py:411`, **not run** — ons carries no contract, so the path may not execute
  there at all.
- **The two instruments are uncommitted**, so § 1/§ 5 figures are reproducible only by rewriting
  them from the evidence's § 6 description. That is a deliberate cost: they are throwaway probes,
  and one of them embodied the wrong-seam error for several turns.
- **The `(2,1)` sweep is one band.** Nothing says furniture-only is the right cut anywhere else,
  and § 5b does not claim it.

## 4. What this session did

Took § 8e's order to build, and measured its premises first. Three things moved:

1. § 8c **reproduced** independently — the walk really does fire exactly once corpus-wide.
2. § 8d's safety claim **held** at document scope, and its no-header claim was **refuted** on the
   only band in scope.
3. The mechanism's benefit **inverted** on inspection: `+0.0351` is the price of the header, not
   the reward for reading the table.

**Worth carrying, because it is the technique and not the result.** A wrong-seam patch produced
`delta = +0.0000000000` on both carriage variants — a clean null that reads exactly like a
refutation, and it was nearly written up as one. What caught it was dumping the region and noticing
its `ascii` still held the lines the walk claimed to have cut. **A null result is not
self-validating**: "the mechanism does nothing" and "the mechanism never ran" produce identical
numbers, and only a diagnostic that inspects the artifact distinguishes them. The previous loop's
own lesson — *a repair measured on one page is a hypothesis about a corpus* — has a twin here: **a
refutation measured through one seam is a hypothesis about the code.**

---

## 9. RULED — 2026-09-15, by the maintainer: the refutation is accepted, R234 is the next subject

§ 5a put § 8e's re-ruling back to the maintainer, and § 2's table recorded the question as
**undecided**. It is now decided: **the refutation is ACCEPTED. The both-ends refusal walk is NOT
to be built**, and [[R234]] — the four-line wrapped boxhead — is the next subject.

**Appended, not edited.** Evidence is append-only after loop close (CLAUDE.md § Documentation
governance), so § 5a's "only the maintainer can close it" and § 2's "undecided" stay exactly as
written. This section records that someone else closed it, which is the same shape the previous
handoff used for its own § 6 and § 8.

**What the ruling does NOT license.** § 5c is still typed **PROPOSED** and that grade survives the
ruling — choosing the subject does not run its prediction. Nobody has measured whether a multi-line
boxhead reader is constructible on this band, and the obvious route was already found circular
(`header_body_split` returns `None` at `ncols=1`, § 8d Option B). `(2,1)` changes that starting
condition without proving it.

**The next session's order of work:**

1. **RUN THE MEASUREMENT FIRST, before any spec** (§ 5c): with `ons p4 band 0` cut `(L,T)=(2,1)`,
   does `header_body_split` return a split at all, and do the four header lines yield **6**
   recoverable labels? If it abstains, [[R234]] is a different problem than it looks — **write that
   and hand back; do not weaken the mechanism to make it pass.**
2. Only then write the spec. The closing condition is on [[R234]]'s row: ons p4's 25x6 table
   asserting under six **non-numeric** column labels, with a test pinning that no `tab:HeaderNode`
   label on a p4 table is numeric.
3. Inherit the two measured wiring facts in the evidence § 6 (the merge partition cannot be
   perturbed; any such cut must precede `compile.py:447`), and translate by ink key, never
   `offset + j` ([[R233]], now measured live).

**NOT STARTED.** No spec, no plan, no code for [[R234]]. A loop is a session (CLAUDE.md § Loop &
context hygiene) and this one is past the originating floor; the R234 loop wants a cleared context.
This session recorded the ruling and stopped.
