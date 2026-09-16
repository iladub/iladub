# Ruling — the next subject is the 92 cells' IDENTITY, not the remedy

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Doc impact: none.**

Recorded immediately after PR #239 merged (`34dc05d`), in the shape `9ef44d5` used for the
previous ruling. **This note supersedes one paragraph of a document that shipped hours earlier,
and that is the whole reason it exists** — a fresh session reads the handoff first.

## What was ruled

Asked to choose the next loop's subject, the maintainer ruled: **verify that the 92 cells are the
RIGHT cells.** Before any remedy is designed, and before scope is ruled.

## What it supersedes, explicitly

`2026-09-16-r239-alignment-universe-gate-handoff.md` § 5a reads:

> **5a. ASSERTED — nothing further needs MEASURING; the next action is a maintainer's ruling on scope**

**That is superseded.** It is not withdrawn as wrong-at-the-time — it was typed ASSERTED on a
correct reading of the gate's own question, which *was* fully answered. What it failed to weigh is
that the evidence's own § 3d names an unmeasured precondition **sitting upstream of the remedy**,
and an asserted "nothing further needs measuring" in § 5a cannot stand beside a "NOT shown" in
§ 3d of the same loop. **The defect is an internal contradiction between two sections written an
hour apart**, and it is recorded here rather than silently corrected because CLAUDE.md § Doc
governance makes Evidence append-only: a later PR may add, never modify.

## Why identity, and why it comes first

§ 3d measured **cardinality and side** — col 0 at x ≈ 72 and col 11 at x ≈ 514, both outside the
decoration rectangle's `124.3 .. 495.3`, both full at **46 of 46 rows**. It did **not** measure
**identity**.

**If the labels land against the wrong rows, the finding inverts.** The switch would not "carry 92
more cells"; it would **assert 92 unsupported facts** — a CLAUDE.md § 7 violation ("only emit what
the source supports"), which is strictly worse than the 404-cell reading it replaces. A remedy
designed on the current headline would ship that.

The gap is concrete, not theoretical: the sampled labels were **years** (`2005`, `2006`) — the
time-series rows at the top of the page — **not the canton names [[R238]]'s symptom actually
names.** *"Nothing says which row is Zurich"* remains literally unverified at compile scope.

## The concrete next action

Read the emitted `tab:EntryCell` texts for bfs p5 under the alignment universe, **col 0 and col 11,
on the CANTON rows** (not the time-series rows), and check each label sits against its own row's
values. `scripts/r239_alignment_universe_gate.py` already installs the universe; the reading is the
new part.

**Falsifier, so the loop can end either way:** if the canton labels are correctly paired, the
switch's value stands as measured and scope becomes the live question. If they are not, [[R238]]'s
symptom is *not* fixed by refusing decoration, the +92 headline is withdrawn, and the subject
returns to column identity.

## Deferred by the same ruling

- [[R240]] — the harness reporting cells + triples beside the score. Cheap and valuable, but it
  repairs the *instrument*, and the identity question can be answered without it.
- **The scope classification** — blanket vs per-page vs per-document. Unruled, and deliberately so
  until identity is settled. The premise it must attack first is unchanged: this corpus holds no
  page whose decoration rectangle is both adopted *and* correct.
