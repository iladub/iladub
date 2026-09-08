# Handoff — the judgement is made: TWO loops, and one of them needs François

**Topic:** action **5a** of the previous handoff is **taken** — [[R186]] and [[R187]] are two
loops, not one. **5b is REFUTED** (and takes R186's arm 1 with it), **5c is repaired and
falsified**, and one new row is raised ([[R188]]).

**Written 2026-09-08**, and — unlike its three predecessors — **written under the originating
floor**, with part 5 first. Grades are still given per action, because the rule asks for them
whenever part 5 carries reasoning, and 5b′ below does.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — put [[R186]]'s two surviving arms to François, WITH the proposal now written

**A proposal between them exists: `docs/superpowers/2026-09-08-r186-proposal.md`** (added later in the same session, on request, at 1.3× the floor with the override logged). It reports that neither arm is adoptable as written — arm 3's *premise* is falsified by the squash-merge regime, arm 2's *granularity* is refuted 14-to-0 — and proposes arm 3's sentence with arm 2's field folded in at value granularity. **Read it as a proposition; it is a recommendation to a maintainer, and it narrows this loop's own §1 rather than restating it.**

Mechanical: the fork is fully argued, arm 1 is struck with evidence, and **the two survivors are
both sentences in CLAUDE.md — a Contract-class file, which § Documentation governance says is
"edited only on explicit request".** There is no version of this a session can decide for itself.

Read `docs/superpowers/2026-09-08-two-loops-sequenced.md` §1 (why arm 1 is gone), then R186's row.
The question to put, in one line each:

- **Arm 2** — only the `Doc impact:` declaration line is immutable; the rest of an Evidence file is
  append-only.
- **Arm 3** — delete the word "immutable" from § Documentation governance in favour of
  *"append-only, and never rewritten"*, conceding the norm is unenforceable by instrument.

**What to carry into the asking, because it is the fact that decides it:** the repo has rewritten
its own Evidence **229 times across 133 files** and the rate is indistinguishable either side of any
clock you draw. Whichever arm is chosen, it is being chosen for a norm that is *currently* broken at
roughly a one-in-three rate — so arm 3 is not the defeatist option it reads as.

### 5b′. ASSERTED — [[R187]] is buildable NOW and its spec is the next loop's first act

Asserted rather than proposed because it rests on a run, not a prediction: the instrument exists,
runs today, and **already emits both rows R187 names** (`4 passed, 2 warnings`). §2 of the evidence
gives the three defects and how each was measured.

**Two things a spec must not get wrong**, both of them already measured so neither needs re-deriving:

1. **Do not design a new lint.** This is a recalibration of `docgov-staleness-*.rq` +
   `tests/docgov_extract.py`. A session that starts from R187's *"a design question first, a lint
   second"* will build a second instrument beside a working one.
2. **Defer arm 1's convention half** (*superseded figures struck rather than replaced*) — that is
   the one piece coupled to 5a's answer. Everything else is independent. See §0's correction, which
   walks the coupling check explicitly.

**The falsification this loop will need, named now while it is cheap:** the fix converts a
warning-path signal into a finding. Rule 4 asks for a test that fails when its subject is removed —
and the hazard is the mirror of the code path's own design argument. **If the new gate fires on 9 of
12 pages, it has not been narrowed, it has been promoted**, and every subsequent loop becomes a doc
loop exactly as `docgov-staleness-code.rq`'s comment predicts. *The oracle is: the gate fires on the
two pages R187 names and not on the other seven currently warned.* If it cannot be made to do that,
the class was never the right one.

### 5c′. PROPOSED — that [[R188]] may turn out to have a denominator of exactly two

**This is the one item here resting on reasoning rather than a measurement.** §3 generalises from
n=2 — two gates, both calibrated to zero — and the row says plainly that n=2 is a pattern, not a
census. My reasoning is that the shape recurs (a defensible local argument for an exemption, never
re-checked against its size), and R188's row lists four candidates to enumerate.

**It fails in an obvious way and the check is cheap:** the four candidates may each turn out to have
been sized by a measurement after all, in which case R186 and R187 are simply two cases and there is
no pattern to name. **Run the enumeration before writing any spec that assumes a class exists.**
Note the row already warns against the tempting-but-wrong sweep (every trivially-passing assert);
read it before choosing a population.

### 5d. PROPOSED — the capability claim, carried for the EIGHTH handoff and still part-stale

```
graincorp  0.9654      bfs   0.9401      WHO   0.9096      apple  0.6289
```

`graincorp 0.9654` is superseded ([[R174]] → `0.9658886894075404`) and the apple figure quoted
beside it in `data-grid.md` is superseded by [[R165]]. **`bfs 0.9401` and `WHO 0.9096` have still
never been re-measured** — eight handoffs now. This is no longer a warning; it is [[R187]]'s own
subject sitting in the document that keeps repeating it. Re-measure before any of them reaches a
published page.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the judgement + all three measurements | `docs/superpowers/2026-09-08-two-loops-sequenced.md` | §0 the ruling **and its own correction**, §1 why arm 1 is struck, §2 the instrument that already runs, §3 the shared invariant |
| the counts it builds on | `docs/superpowers/2026-09-08-the-two-counts.md` | §1 R186's curve, §2 R187's buckets — **unchanged and still correct**; §3's framing is what this loop revised |
| the three rows | [[R186]], [[R187]], [[R188]] in `residues-open.md` | each carries its own evidence inline — read the row, never the index line |
| the instrument to repair | `tests/test_doc_governance.py`, `vocab/queries/docgov-staleness-{evidence,code}.rq`, `tests/docgov_extract.py` | 66 lines + two derivations; the whole of R187's surface |
| the repaired test | `tests/test_corpus_stem.py:~391,430` | 5c: the floor now reads `stem_document.score`, not a literal |

## 2. What changed

One branch, `two-loops-sequenced`. `tests/test_corpus_stem.py` (5c's repair + its docstring), the
new evidence document, three register edits (R186 amended, R187 amended, R188 raised) and the index.
**No file under `src/` changed.** No wiki page was edited — the v0.0.4 ruling that rewriting a
loop's measured figures destroys the record still stands.

**Appended after the fact, within the same open PR:** a second commit (`24876e7`) adds
`docs/superpowers/2026-09-08-r186-proposal.md` and wires it into R186's row and 5a above. It was
written on request at 1.3× the originating floor with the override logged. **The branch therefore
carries TWO commits and PR #178 was still unmerged with CI in progress when this line was written** —
a fresh session should check `gh pr view 178` before assuming this loop landed. Note this paragraph
is itself an *append to Evidence mid-loop*, which the proposal's own rule permits and the boundary
makes decidable: the loop has not closed, and nothing above it was deleted or modified.

## 3. What was decided, and where that decision is recorded

- **[[R186]] and [[R187]] are TWO loops.** Recorded in `2026-09-08-two-loops-sequenced.md` §0 and in
  both rows. Ground: different kind of act, different decider — not different instruments, which was
  the framing offered and is half wrong.
- **R186 arm 1 is STRUCK.** Recorded in §1 and in R186's row. This is the only place it is recorded;
  the arm still reads as live in the *two-counts* document, which is Evidence and deliberately not
  rewritten.
- **"R186 first" is a recommendation, not a dependency.** Recorded in §0's correction block. A
  session that reads the filename as a build order has misread it.
- **[[R188]] is raised rather than folded into either row.** Recorded in the row's deferral column:
  generalising from n=2 would have made one loop answer three questions.
- **5c is repaired by removing the class, not the instance** — the bound reads the fixture. Recorded
  in §4 and in the test's own docstring, which now carries why the stale copy was invisible.
- **No arm of either fork is chosen.** Recorded in §5 of the evidence. Still deliberately untaken.

## 4. Unverified or assumed

- **The same-day zone is AMBIGUOUS by construction and I have not disambiguated it.** 113 files /
  203 events mixes loop iteration before close (not a violation) with post-close edits (a violation).
  My claim is **not** that 34.3% of files were edited after close; it is that the clock cannot tell
  the two apart, which the matched 73%/77% rewrite rates support but do not prove. **5 files at
  ≥2 days remains the honest upper estimate for unambiguously late edits.**
- **The merge-vs-squash boundary at #145/#146 is read from `git log --merges`, not from GitHub.** If
  some PRs in that range were squashed anyway, the same-day zone under-counts.
- **§3's invariant is n=2.** See 5c′. It is named as a pattern in a row that forbids closing it by
  assertion, which is the strongest available guard and not a proof.
- **R187's three defects are measured on the two pages R187 names.** The other 7 warned pages were
  not inspected, so "citation-gated" is confirmed as a mechanism and not as the explanation for
  every case.
- **`bfs 0.9401` / `WHO 0.9096` remain unmeasured** (§5d) — eighth handoff.
- **The full suite was not run.** `tests/test_corpus_stem.py` (13 passed, 252s) and
  `tests/test_doc_governance.py` (4 passed, 23s) were, and they are the two modules this branch
  touches. CI is the check that has not yet reported.
- **This handoff was written under the floor and part 5 first**, which is the format working as
  intended for the first time in four loops. That is worth imitating, not celebrating — the
  difference was that this session's assigned action was *decidable*, so nothing had to be designed
  at the end.
