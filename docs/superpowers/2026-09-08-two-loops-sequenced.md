# The judgement: TWO loops, sequenced — and both gates are calibrated to zero

**Loop:** `two-loops-sequenced`, 2026-09-08. Ran action **5a** of
`docs/superpowers/2026-09-08-after-the-two-counts-handoff.md` (typed ASSERTED there): the design
judgement the two counts were taken to inform. Also ran **5b** (PROPOSED — refuted) and **5c**
(ASSERTED — done, falsified, green).

**Doc impact: none.**

---

## 0. The ruling, in one paragraph

[[R186]] and [[R187]] are **TWO loops, sequenced — R186 first.** Not because they are different
questions; they share one, and §3 below derives it once so neither successor spec has to. They are
two because **R186's remedy is a maintainer wording ruling on a Contract-class file and R187's is a
threshold-and-scope repair to running code.** R186 needs François; R187 does not. Folding them
blocks the buildable half on the unbuildable half, and it would put a loop in the position of
making a ruling and then building against it in the same document — the plan-authors-its-own-test
failure (CLAUDE.md § Plan authoring discipline, defect 5) at loop scale.

Neither candidate framing offered in the handoff survived. The previous session asked whether
"same question, two instruments" is one loop or two. **The premise is half wrong**: R187's
instrument already exists and runs, and R186's proposed instrument is refuted below. What separates
them is not the instrument, it is who has to answer.

**A correction to this section's own first word, made before it shipped.** "Sequenced" overstates
the coupling, and the check is worth writing down because the ordering claim is weaker than the
two-loops claim. **R187's instrument repair is NOT blocked on R186.** All three defects in §2 —
citation-gating, the warning-only code path, unextracted inline citations — are repairs to
`docgov_extract` and two `.rq` files, and none of them needs to know what CLAUDE.md ends up saying
about immutability. **Exactly one thing couples them:** R187's *arm 1* asks that a superseded wiki
figure be **struck rather than replaced**, and that is the same append-only convention R186 is
ruling on for Evidence. So the precise statement is:

- **TWO loops — firm.** Different kind of act, different decider.
- **R186 first — a RECOMMENDATION, not a dependency.** Its ground is that a maintainer question
  should be asked early rather than discovered late, not that R187 cannot start.
- **If R187 runs first, it builds the instrument and DEFERS arm 1's convention half**, which is the
  only part that inherits R186's answer.

The section heading and this document's filename say "sequenced"; read them as *ordered by who is
blocked on whom to ANSWER*, not by what is blocked from being BUILT.

## 1. 5b is REFUTED — and it takes [[R186]] arm 1 with it

5b proposed that R186's arm 1 (enforce immutability by lint) is now cheap, because at a ≥7-day
grace window the lint fires on **zero** of 327 historical files. It named check (ii) as its own
falsifier: *squash merges hide within-loop edits, so the ≥7-day zero may be an artifact of what git
can see.*

**Check (ii) is answerable locally, and the previous count did not run it.** PRs up to **#145** were
merge-committed, not squashed (`git log --merges --oneline -5` → newest merge commit is #145);
#146 onward are squashed. So for the whole pre-2026-09-01 era, **within-loop edits ARE in history**,
as same-day later commits — the zone the R186 count reported as one line (`any later commit, same
day included: 123 files`) and did not classify.

Classified (script: `git log --reverse --numstat` over `docs/superpowers`, one pass; population =
333 tracked − 3 register − 1 gated cache = **329**, which reconciles with the count's 327 plus this
session's PRs #176/#177):

| zone | files | events | REWRITE | APPEND | rewrite rate |
| --- | --- | --- | --- | --- | --- |
| same day as introduction | **113 (34.3%)** | **203** | 148 | 55 | **73%** |
| ≥1 day (the count's) | 20 (6.1%) | 26 | 20 | 6 | **77%** |
| ≥2 days | 5 | 6 | — | — | — |
| ≥7 days | **0** | **0** | — | — | — |

**Two things follow, and the second is the one that matters.**

1. The ambiguous zone is **5.6× the ≥1-day signal and 34× the ≥2-day signal** (113 files vs 20 vs 5).
   A ≥7-day window does not fire on zero because rewriting stopped; it fires on zero because it has
   discarded **229 events to keep none**. *A window wide enough to be safe is wide enough to be
   empty.* 5b's inference — cheap because it fires on nothing — inverts the evidence.
2. **The rewrite rate is the same on both sides of the clock: 73% same-day, 77% later.** If the
   separator were separating two behaviours — *iterating before close* versus *editing after close*
   — the two zones would look different. They do not. That is evidence the separator is not
   separating anything: it is one behaviour (authors rewrite their own evidence) cut arbitrarily by
   a calendar.

**Therefore R186 arm 1 is refuted on its mechanism, not merely priced out.** Any time-windowed
git-history rule inherits this: the date cannot distinguish the case it must permit from the case it
must refuse. R186 collapses to arms 2 and 3, and both of those are sentences in CLAUDE.md, not code.

**What this does NOT show.** It does not show the ≥7-day zero is *wrong*, and it does not show
post-close rewriting is common — 5 files at ≥2 days remains the honest upper estimate for edits that
are unambiguously late. It shows the **instrument** cannot be calibrated, which is a different and
stronger claim than 5b's, pointing the opposite way.

## 2. [[R187]]'s instrument ALREADY EXISTS, already runs, and already flags both offending pages

The previous session's §3 asserted R187's remedy "cannot be a git rule or a grep". True, and it
buried the lead: **it does not need to be either, because the instrument is built.**
`tests/test_doc_governance.py` runs a PROCEDURAL extraction → SHACL membrane → three SPARQL
derivations, two of which are staleness derivations over exactly this class.

Run today, on a green suite (`pytest tests/test_doc_governance.py -W always::UserWarning`,
**4 passed, 2 warnings**):

```
data-grid.md              staleAgainstCode  src/iladub/etkl/compile.py     … and inPromotionQueue true
table-holon-compilation.md staleAgainstCode  src/iladub/etkl/document.py    … and inPromotionQueue true
```

**Both pages [[R187]] names are flagged, right now, by an instrument that passes.** Three measured
defects explain why that is not a contradiction:

1. **The hard gate is citation-gated.** `docgov-staleness-evidence.rq` derives staleness only where
   `?page dg:cites ?src` and `?src dg:docClass "evidence"`. `data-grid.md`'s `sources:` names three
   specs from 2026-08-08/09 and **none of R174, R165, or any loop that superseded its figures** —
   because nobody edited the page, which is the condition the lint is supposed to detect. *A page
   goes stale only against sources it has named, and a page never names the loop that refuted it.*
2. **Its one live edge is downgraded by design.** Both pages cite `src/…` and `tests/…`, so their
   real signal goes down `docgov-staleness-code.rq`, whose own comment says: *"WARNING ONLY — code
   churns every commit; a hard gate here would make every loop a doc loop."* That prediction is now
   measurable: **9 of 12 wiki pages carry `staleAgainstCode` today.**
3. **Inline citations are not extracted.** R187 finding (d) — `table-holon-compilation.md` declares
   `updated: 2026-08-03` while citing a 2026-09-07 spec at `:32` — is invisible because that
   citation is prose, not `sources:`. The frontmatter fallback R187 proposed can therefore be wrong
   with no instrument dissenting.

So R187 is not "design a lint". It is **recalibrate and rescope one that runs**, with a green-suite
oracle already emitting the two rows it must convert from warning to finding.

## 3. The invariant both rows are instances of — derived ONCE, here

State it once so neither successor spec derives it again (CLAUDE.md § Plan authoring discipline
rule 6):

> **Both doc-governance gates in this repo are calibrated to fire on ZERO, and the population each
> was built to guard sits entirely in an ungated zone beside it.**

| | the gate | fires on | the zone beside it | fires on |
| --- | --- | --- | --- | --- |
| [[R186]] | a ≥7-day immutability window | **0** events | same-day + ≥1-day rewrites | **229** events |
| [[R187]] | `staleAgainstEvidence` (hard) | **0** pages | `staleAgainstCode` (warning) | **9 of 12** pages |

This is one defect wearing two faces, and it is **not** dishonesty or neglect: each zero was reached
by a defensible local argument (a grace window must not punish loop iteration; a code-staleness gate
would make every loop a doc loop). The failure is that in both cases the argument for widening the
exemption was never re-checked against how much it exempted. **A gate reporting zero is a claim that
should be measured, not a reassurance.**

Every successor spec cites this section rather than re-deriving it.

## 4. [[R174]]'s half-applied re-baseline is REPAIRED (5c)

`tests/test_corpus_stem.py:421` used `assert standalone.score < 0.9654553611484971` — the figure
[[R174]] superseded on 2026-09-05 — as a live comparator bound, and the docstring above it asserted
in prose that this literal is *"what the driver reads over all three pages"*. Both were stale; the
test passed anyway, because a floor that moves **up** still holds, which is precisely why it was
invisible for three days.

**Repaired by removing the class, not the instance:** the bound is now read from the
`stem_document` fixture itself (`assert standalone.score < stem_document.score`), so it cannot go
stale again. The docstring records what happened and why the copy was invisible.

**FALSIFICATION.** Comparator inverted to `>`:

```
E  assert 0.9588400374181478 > 0.9658886894075404
E   + where 0.9588400374181478 = CompilationReport(...).score
E   + and   0.9658886894075404 = DocumentReport(...).score
1 failed in 189.31s
```

The failure output is itself the evidence that the bound now reads the fixture rather than a
literal — `0.9658886894075404` is derived from `DocumentReport`, not typed. Restored; full module
**13 passed in 252.14s**. Note the repair is behaviour-preserving today: standalone reads `0.95884`,
under both the stale `0.96546` and the live `0.96589`.

## 5. What is deliberately NOT done here

- **No arm of either fork is chosen.** This document rules the *sequencing*, not the remedy.
  R186's arms 2 and 3 are a maintainer decision; arm 1 is struck.
- **No spec is written.** R187 is buildable and its spec is the next loop's first act.
- **The stale wiki figures are not edited** — the v0.0.4 ruling stands (rewriting a loop's measured
  figures in place destroys the record rather than dating it).
- **`bfs 0.9401` and `WHO 0.9096` are still not re-measured** (carried for the eighth handoff).
