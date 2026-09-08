# Handoff — v0.0.4 is out, 5a is run, and one design judgement is left standing

**Topic:** the release loop closed (`v0.0.4`, live and verified), and action **5a** of its handoff
— the two counts [[R186]] and [[R187]] were each blocked on — is **taken**. What remains is the
judgement those counts were supposed to inform, and nothing else.

**Written 2026-09-08**, at the end of the session that ran the release and 5a.

**⚠ THIS HANDOFF WAS AUTHORED AT 2.2× THE ORIGINATING FLOOR (~111k working tokens).** CLAUDE.md
§ *The handoff's next action is TYPED* requires that such a handoff **grade part 5 per action**,
and it does. Read the grades as load-bearing, not decorative — particularly 5b, which is the only
item here resting on reasoning rather than on a measurement already in the register.

**Part 5 is not the usual risk in this one.** The next action was *determined by measurement*, not
designed: 5a came back and named the decision. That is the fatigue-proof kind. Where fresh
reasoning does appear, it is marked.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — rule 5b of the previous handoff: are [[R186]] and [[R187]] one loop or two?

Asserted **as the action**, not as its outcome: what is certain is that this is the next thing to
decide and that everything needed to decide it is already written down. The ruling itself is
genuinely open, and this handoff does not pre-empt it.

Read `docs/superpowers/2026-09-08-the-two-counts.md` **§3**, then both rows. The counts are
inline in the rows now, so nothing has to be re-run.

The state of the question, in one paragraph: the previous handoff proposed the two rows are **one
loop** and named its own falsifier — *opposite shapes, Evidence rewrites near-zero while wiki
staleness is widespread*. **The falsifier did not fire** (5 files at a two-day threshold; 2 distinct
stale quantities). **It also did not confirm.** The remedies diverged: R186's instrument is a
git-history rule with a grace window — which at ≥7 days fires on **zero** historical cases, making
it cheap *and* making it prove little — while R187's cannot be git or grep at all, because the
predictor is a quantity class at any precision, `1.0` is unclassifiable without its sentence, and
the population leaks outside `docs/wiki/**`.

**The judgement to make: is "same question, two instruments" one loop, or two?** CLAUDE.md
§ Plan authoring discipline **rule 6** is the relevant constraint, and it cuts both ways here —
folding them risks one spec deriving one invariant twice; splitting them risks two specs deriving
the same invariant once each. That is the call, and it has not been made.

### 5b. PROPOSED — that [[R186]] is now cheap enough to close WITHOUT a design loop

**This is the one item in this document that is fresh reasoning written at 2.2× the floor. Treat
it as a proposition to test in minutes, not a plan to build on.**

The claim: R186's arm 1 (enforce immutability by lint) was refused as expensive, and the count says
it is not. At a **≥7-day** grace window the lint fires on **zero** of 327 files, so it can be added
without triaging a backlog — the thing that made arm 1 look costly.

**Two ways it fails, and both are cheap to check.** (i) A lint that fires on nothing historical may
be pinning nothing — CLAUDE.md § Plan authoring rule 4 demands falsification, and a rule with no
positive case is exactly the shape that passes with its subject deleted. (ii) The count's own
caveat: **squash merges hide within-loop edits**, so 6.1% is a floor and the ≥7-day zero may be an
artifact of what git can see, not of what happened. **Check (ii) before believing the arm is
cheap** — if within-loop rewrites are common, the window is measuring the wrong thing entirely.

### 5c. ASSERTED — repair [[R174]]'s half-applied re-baseline

Mechanical, found incidentally by 5a, and owned by nobody: `tests/test_corpus_stem.py:421` still
uses `assert standalone.score < 0.9654553611484971` — the score [[R174]] superseded — as a live
comparator bound. Nothing is broken (it is a floor, and the floor holds), which is why it has
survived. It is a dead number executing in a test, and the next reader who takes it for the current
value will be wrong. One line; falsify it the normal way.

### 5d. PROPOSED — the capability claim, carried forward and now DEMONSTRABLY part-stale

Carried for the **seventh** handoff running:

```
graincorp  0.9654      bfs   0.9401      WHO   0.9096      apple  0.6289
```

5a **measured** what previous handoffs only warned about: `graincorp 0.9654` is superseded
([[R174]], `0.9658886894075404`), and the apple figure quoted alongside it in `data-grid.md` is
superseded by [[R165]]. **`bfs 0.9401` and `WHO 0.9096` remain unchecked entirely.** Re-measure
before any of them reaches a published page; the v0.0.4 release avoided this by promoting zero,
which is a deferral and not an answer.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the counts | `docs/superpowers/2026-09-08-the-two-counts.md` | §1 R186's curve, §2 R187's buckets, **§3 what it does to the ruling** |
| the two rows | [[R186]], [[R187]] in `docs/superpowers/residues-open.md` | each now carries its count inline — read the row, not the index |
| the release | `docs/superpowers/2026-09-08-release-v0-0-4-handoff.md` | its appended block: what shipped and how it was verified |
| the release evidence | `docs/superpowers/2026-09-08-release-v0-0-4.md` | §0 the 5b refutation technique, §3 the guard that did not exist |
| the half-applied re-baseline | `tests/test_corpus_stem.py:421` (vs `:377`) | 5c's whole subject |
| the out-of-scope stale figure | `tests/etkl/test_datagrid.py:1085` | why R187's stated scope is wrong |

## 2. What changed

Three PRs merged: **#174** (v0.0.4 — version bump, `test_citation_version_matches`, `RELEASE.md`
correction, [[R187]] raised), **#175** (the release outcome appended to its handoff), **#176** (the
two counts, both rows corrected by them). `v0.0.4` is tagged, on PyPI, and deployed to iladub.dev.
**No file under `src/` changed** beyond the version string across this whole session.

## 3. What was decided, and where that decision is recorded

- **Promote zero from the wiki queue for v0.0.4.** Maintainer ruling; recorded in
  `2026-09-08-release-v0-0-4.md` §1 and PR #174.
- **`RELEASE.md` corrected by ADDING the missing guard, not by weakening its sentence.** Recorded
  in that doc §3 and in the test's docstring.
- **`data-grid.md`'s stale figures are NOT edited.** Recorded in [[R187]]'s deferral column:
  rewriting a loop's measured figures in place destroys the record rather than dating it.
- **The append to the release handoff is labelled the APPEND arm of [[R186]].** Recorded in the
  appended block itself and in PR #175, so a later count can tell append from rewrite rather than
  infer it.
- **No arm of either fork was chosen.** Recorded in `2026-09-08-the-two-counts.md` §3 — deliberately
  untaken, at 1.9× the floor.
- **5b of the previous handoff is neither confirmed nor refuted.** Recorded in the same §3. It is
  **not** settled, and a session that reads it as settled has misread it.

## 4. Unverified or assumed

- **R186's 6.1% is a FLOOR, not a rate.** Squash merges hide within-loop edits entirely; a file
  rewritten inside its own PR after that loop's review closed does not appear in the data at all.
  The day-threshold separator is a proxy — medium confidence at ≥1 day, high at ≥2.
- **R187's LIVE bucket means "a test carries this figure", which is weaker than "a test pins it".**
  `tests/test_corpus_stem.py:406` carries `0.9706` while explicitly disclaiming that it pins it; it
  was filed UNKNOWN for that reason. Others may deserve the same scrutiny and did not get it.
- **Nine R187 figures are UNKNOWN, and they are not evenly ignorant.** `88.6` / `70.6` (apple
  x-coordinates in `data-grid.md`) appear **nowhere else in the tree** — no test, no register row,
  no source comment. No future loop can check those at all.
- **`bfs 0.9401` and `WHO 0.9096` have never been re-measured** (§5d).
- **The Trusted Publisher evidence is historical again.** It published on 2026-09-08; that says
  nothing about the next release. The *form* of the caveat regenerates every time.
- **Both counts were taken by subagents.** Their methods are stated in
  `2026-09-08-the-two-counts.md` and their numbers were not independently re-derived by the session
  that recorded them. The R186 agent's self-check (does R185's known case appear?) passed **and
  returned a correction** — which is evidence the method works, not proof the totals are right.
- **A process note, and the reason this file carries a warning at the top.** This handoff was
  authored at ~111k working tokens, 2.2× the originating floor, because the session was asked for it
  after the work rather than before. The mitigation available was to make part 5 mostly a *pointer*
  to a decision the counts had already framed, and to isolate the one piece of fresh reasoning (5b)
  and grade it PROPOSED with two named ways to falsify it in minutes. **That is a mitigation, not a
  fix.** The fix was to write it earlier, and the previous handoff — authored under the floor — is
  the one to imitate.
