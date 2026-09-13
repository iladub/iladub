# Handoff — R213, the invisible glyph: the loop starts with a RULING, not with code

**Serves:** maintenance — R213 is named by no `prog:blockedBy` and blocks no criterion (it is one
of the register graph's structural candidates), so this handoff serves no rung directly. What it
unblocks is a §8 classification the maintainer owns.

**Date:** 2026-09-13. **Branch this was written on:** `span-the-author-drew` (PR #216).

**Doc impact: none.** A handoff ships no term, no behaviour, no released assertion.

**Part 5 was written FIRST**, per CLAUDE.md § Loop & context hygiene. **This handoff was authored
far OVER the originating floor** — it closes a very long session — so every action in § 5 is
graded, per action, as the rule requires. Parts 1–4 are appended after; pointers do not degrade.

---

## 5. The next concrete action

### 5a. ASSERTED: the loop opens with the maintainer's ruling. Nothing is codeable before it.

R213's question *"how many of the 110 zeros are invisible"* is **answered and closed off**: all 110,
by set identity. What remains is **what the reader should EMIT for an invisible glyph**, and that
choice determines the §8 class of everything downstream — so a spec written before the ruling would
be a spec for three different loops.

The three dispositions, with what each costs. These are settled enough to choose between; none
needs further measurement first.

- **(a) Carry it as it reads now (`0`).** Status quo. The cost is a §7 false assertion the moment a
  live proposer grounds it: 110 capacities of zero the page does not state. Measured: under the
  abstaining battery nothing grounds, so the hazard is latent, not live.
- **(b) Emit nothing.** Drops 110 cells. Violates §5 (*context is carried, not discarded*) and is
  the one option the repo's own principles seem to forbid outright — a cell the author drew becomes
  invisible to the graph as well as to the eye.
- **(c) Carry it as a typed ABSENCE or a proposition.** Most consistent with §3 and §7 — the reading
  says *"there is a glyph here that the page does not show"* rather than asserting its value. Needs
  a term (`tab:InvisibleGlyph`, or a `tab:nilSpelling` sibling), and the existing vocabulary is
  close: `tab:Blank`'s comment already distinguishes *genuinely missing* from *a marker the author
  writes to mean nothing here*, and this is a third thing again — ink the author wrote and hid.

**Why this is asserted rather than proposed:** the option space is exact, each option's cost is
measured, and the choice is a values question about what a reading may assert — not a prediction
that could be refuted by running something.

### 5b. PROPOSED, and this is the expensive one: the colour discriminator may not be shippable.

**The prediction:** invisibility can be decided PROCEDURALLY, by comparing a glyph's
`non_stroking_color` against the fill of the rectangle beneath it.

**The evidence for it.** Corpus-wide, 30,404 characters sit on a filled rectangle. The 110 invisible
ones cluster at a luminance gap of **≤ 0.0065**; the 30,294 visible ones start at **0.2000**. The
empty band between is **0.1935** — about a fifth of the whole 0..1 range — so *any* threshold inside
it classifies all 30,404 identically. On this corpus the discriminator has zero degrees of freedom.

**Why it may still fail, and why the corpus cannot tell you.** **n = 1 document.** All 110 are in
`graincorp-capacity`; the other six documents contain zero invisible glyphs. The 0.1935 band is a
property of *one publisher's palette* — dark navy on dark navy — not of the class. A second specimen
using mid-grey on light-grey would land inside that band and the threshold would start deciding,
at which point it is a tuned constant and §8 sends the decision to NEURAL. **There is no document in
the corpus that can refute this**, which is exactly [[R157]]'s shape (*a census scoped to one page
cannot validate a rule that runs on every page*) one layer up, and [[R149]]'s (*a row's caveat does
not bind its own numbers*).

**If 5b is wrong**, the loop is not a small PROCEDURAL step but either a NEURAL proposal with an
oracle, or — the honest cheap outcome — a **ruling plus a registered limit**: implement (c) for the
exact-palette case, and record that the discriminator is calibrated on one specimen. A loop that
ships the colour test as general PROCEDURAL code on n=1 would be doing what this repo names a defect.

**Two prior sins of this session are the reason 5b is graded, not asserted.** The agent stated
*"invisibility is decidable from the PDF"* on the strength of a threshold it had chosen (0.15), and
then produced a verdict line (*"NEURAL territory"*) from a second invented constant (`band > 0.3`).
Both were corrected in place. Treat any confident sentence about this discriminator as needing its
own measurement.

### 5c. What this hands over exposed

[[R213]] stays **open** with its first half done and its second untouched. [[R215]] (25 of 27 rows
carry no year) is untouched and is the maintainer's call. [[R222]] (a non-contiguous span is refused
by nothing) and [[R223]] (`tab:colX0`/`colX1` declared twice with conflicting ranges) were raised by
the loop that wrote this and are untouched. [[R166]] stays open on five donor-less bands.

---

## 1. Where the primaries are

- **The row** — [[R213]] in `docs/superpowers/residues-open.md`. Read the full row, not the index
  line; its closure column prescribes the measurement that has now been run.
- **The evidence** — `docs/superpowers/2026-09-13-r211-closed-the-span-donated.md` § 6, and
  `docs/superpowers/2026-09-13-graincorp-capacity-carried-grid.md` for what the reading now carries.
- **The instrument** — not committed. Both probes were scratch scripts over `pdfplumber`'s
  `page.chars[*].non_stroking_color` and `page.rects[*]` with `fill`. **A loop that acts on 5b must
  commit its own**, because the figures above came from throwaway code.
- **The vocabulary neighbourhood** — `tab:Blank`, `tab:nilSpelling` and `tab:datatypeAbstains` in
  `vocab/ontology/tab.ttl`; `tab:nilSpelling`'s comment is the closest existing reasoning about
  *"a marker the author writes to mean nothing here"*.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| All 110 zero-reading cells are invisible glyphs, by set identity not a matching count | R213's row, ✎ 2026-09-13 |
| Invisibility is decidable **on this corpus**, by a threshold-insensitive colour comparison | R213's row, qualified there with the n=1 caveat |
| What to EMIT is a §8 classification and no ruling was taken | R213's row, and § 5a above |
| R213 stays open; the row's first half is done and its second untouched | the row's own strike state — it is not struck |

## 3. Unverified or assumed

- **5b, entirely.** The discriminator's generality rests on one document.
- **Whether a second specimen exists at all.** Nobody has looked outside the 7-document corpus for
  a PDF that hides ink this way; the technique (white-on-white, or matched fills) is common in
  published tables, so the population is probably not 1 in the world — only 1 here.
- **Whether option (c) needs a new term or can reuse `tab:Blank` + a `nilSpelling`-style marker.**
  Not designed. The distinction *hidden ink* vs *absent ink* vs *a nil marker* is three-way and the
  vocabulary currently carries two of the three.
- **The rendering claim is asserted from colour arithmetic, not from a render.** Nobody has
  rasterised the page to confirm the glyphs are invisible to a human eye; the evidence is that the
  glyph colour matches the fill it sits on.

## 4. What this loop did

Closed [[R211]] (span donation: graincorp's 189 records carry their port names, ink unmoved),
measured [[R213]] to 110 of 110, advanced `etkl` 2/7 → 3/7 on a falsification rather than a number,
amended [[R166]] six donor-less bands → five, and raised [[R222]] and [[R223]]. PR #216.
