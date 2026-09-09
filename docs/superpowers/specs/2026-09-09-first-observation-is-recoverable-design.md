# First observation is recoverable — `cor:readAt` is a refresh log, and R192's zero was measured by a blind instrument

**Spec for [[R198]].** Written 2026-09-09, in a fresh session, under the originating floor.

**Doc impact: increment.**

Predecessor: `docs/superpowers/2026-09-09-the-register-is-a-refresh-log-handoff.md` action **5a**,
graded **PROPOSED**. That grade was correct and it paid: 5a named the falsification to run *before*
designing anything, and running it first changed what this loop builds.

---

## 0. Verdict, stated first

**5a's falsification PASSES, and the repair it feared is unnecessary.**

5a asked, before any design: *is the first-observation commit recoverable for the 18 existing
readings, or only for readings taken from here on?* It predicted that if only the latter, "the
repair cannot validate itself against the 109 occurrences that motivated it, and the honest loop is
a much smaller one."

It is recoverable, for **18 of 18**, in **one 9.6-second pass over the tree's own ancestry** (§1). So the register
needs no redesign, no new stored field, and no going-forward-only compromise. The whole of 5a's
feared repair — "per-reading provenance … a redesign of `tests/corpus-manifest.ttl` and of
`load_readings`, touching the shipped wiki and code gates" — is **not built here, because it is not
needed**: first observation is a *derivation over git history*, and this repo forbids storing a
derived value as a label (CLAUDE.md § Documentation governance; `risk:RiskAssessment` is the
standing precedent).

**And the loop found something 5a did not predict.** Re-running [[R192]]'s census with sound dating
turns its headline **326 fires / 0 findings** into **15 findings**, seven of which are the very
capability-line figure R192 was raised about (§4). R192's zero was not merely a lower bound in
principle, as its amended row already conceded — **the instrument was blind to R192's own
motivating case.**

---

## 1. First observation is recoverable — 18 of 18

**MEASURED 2026-09-09 at `4b886a9`.** Two independent instruments agree on all 18 readings.

Per-value pickaxe, `git log --reverse -S<value>`, 18 invocations, **56.7s**; and a single
`git log --reverse -G<alternation> -U0 -p` pass attributing each value to the first commit
that *added* a line containing it, **9.6s**. The two agree on all 18 commits and all 18 dates.

```
value                    readAt[0]    first seen (ancestry)  lag (days)
0.06068601583113457      2026-08-09   023a880  2026-08-09      0
0.35560344827586204      2026-08-09   13e3af2  2026-08-09      0
0.1895                   2026-09-04   4cfee38  2026-09-02      2
0.6288659793814433       2026-09-04   752b807  2026-09-04      0
0.71875                  2026-09-08   f42ef99  2026-09-07      1
0.3438                   2026-08-20   c5bd91a  2026-08-04     16
0.3464447806354009       2026-09-05   4a60023  2026-09-01      4
0.40331491712707185      2026-09-08   5c141b2  2026-09-08      0
0.9047                   2026-08-20   b89cf1b  2026-08-04     16
0.9091940976163451       2026-09-05   134e26e  2026-09-05      0
0.9095022624434389       2026-09-08   5c141b2  2026-09-08      0
1.0                      2026-08-20   e48ebf2  2026-05-31     81   ← NOT a reading; see §2
0.9654553611484971       2026-08-03   318aca5  2026-08-03      0
0.9658886894075404       2026-09-05   752b807  2026-09-04      1
0.9719934102141681       2026-09-05   1d56133  2026-08-31      5
0.5597                   2026-08-20   c5bd91a  2026-08-04     16
0.9095966620305981       2026-08-31   ebee8d3  2026-08-31      0
0.9156327543424317       2026-09-08   5c141b2  2026-09-08      0
```

**`readAt` lags first observation for 8 of the 17 quotable readings, by 1 to 16 days.** That is
[[R198]] confirmed from the register's own side; the row measured it from the documents' side (109
occurrences post-dating their reading) and this is the same defect seen from the other end.

**`--all` vs the ancestry scope was checked and it changes no date, only hashes** — the `--all` hit
is the branch commit, the ancestry hit the squashed merge, and every pair falls on the same day.
Ancestry is the right scope (a value that only ever existed on an abandoned branch was never
observed *of this tree* — the `bfs 0.9401` lesson, [[R199]](b)), and the dates being identical means
the choice costs nothing today.

**The ancestry ref is `HEAD`, not `main`, and CI proved why.** `main` was the first choice, it passed
all 7 tests locally, and it **failed in CI with exit 128**: `actions/checkout` leaves a detached HEAD
with no local `main` ref. The crash was the cheap half. **The expensive half is a deadlock the crash
exposed:** under `main` scope a PR that appends a NEW reading finds its value absent from `main` and
reports it unrecoverable, so the recoverability test could never go green until after the merge it
was blocking — the same unsatisfiable-gate shape §4.1 rejects for Evidence. `HEAD` resolves in every
checkout, includes the branch's own commits, and is measured identical to `main` on all 17 quotable
readings at `3dd380f`. `tests/test_first_seen.py::test_it_runs_on_a_detached_HEAD_with_no_branch_ref`
pins it.

### 1.1 What "first seen" is, and what it is not

It is the **first commit reachable from `HEAD` whose diff ADDS a line containing the value's
exact lexical form**. That bounds the observation from above, and it is not the same as the moment someone ran
the compiler. A value measured on the 7th and committed on the 8th reads as the 8th.

This is stated as a limit, not a defect, because the alternative is worse: `readAt` bounds
observation from above *too*, and far more loosely — by up to 16 days rather than by the gap
between measuring and committing. **Nothing here claims to recover the instant of measurement.
The claim is only that git bounds it far more tightly than the register does**, which is exactly
enough to answer "was this figure already superseded when that document was written."

---

## 2. `1.0` is excluded, on the exemption it already carries

The single unrecoverable row is `graincorp-capacity 1.0`, whose first-added-line on `main` is a
**2026-05-31 MkDocs deploy on the docs branch** — noise, 81 days before its earliest `readAt`.

It needs no new exemption. It is already `cor:notQuotable true` in the register, and **for the same
root cause**: `1.0` is not a distinctive literal, so it cannot be matched against prose *or* against
history. The figure gate's existing exemption and this derivation's exclusion are one fact about one
value, and coupling them is the honest encoding — a second, separately-maintained skip list would be
the [[R188]] failure (an exemption is a coverage loss dressed as a fix).

**Consequence, stated with its size: 1 reading of 18 has no recoverable first observation, and it is
the one reading that may not be quoted anyway.**

---

## 3. `readAt` is INERT to both hard gates today

**MEASURED.** `is_dated` (`tests/docgov_extract.py:218`) is
`bool(_ISO_DATE.search(block) or _SHA.search(block))` — a **presence** check. `dg:readAt` reaches
only the *text of the finding message* in `_undated` (`tests/test_doc_governance.py:88`), never the
pass/fail decision, and `vocab/queries/docgov-undated-figure.rq` does not mention it.

Two consequences, and they pull in opposite directions:

- **R198 breaks nothing that ships.** No gate outcome is wrong today because `readAt` is a refresh
  log; the gates never ask it anything.
- **The gates are weaker than they read.** *Any* ISO date or backticked sha anywhere in the block
  satisfies them, including a wrong one. The gate asks whether the author dated the claim, never
  whether the date is the reading's.

### 3.1 The obvious strengthening is REFUSED, on measurement

The strengthening R198 appears to unblock — *the block's date must be one of the reading's dates* —
is **not built**, and the refusal is the measured half of this spec.

**MEASURED over all 33 gated occurrences (22 `code`, 11 `wiki`), all currently passing:** 9 carry a
block date matching no `readAt`. Cross-checking each against §1's first-observation date:

- **2 are the REGISTER lagging, not the author.** `docs/wiki/concepts/dimension-split.md:88` dates
  `0.9047` at 2026-08-04 and the register says 2026-08-20 — 08-04 is the day the value entered the
  tree (`b89cf1b`). `tests/etkl/test_adoption_document.py:380` dates `0.71875` at 2026-09-07 against
  a registered 2026-09-08 — again the author is right (`f42ef99`).
- **7 are block-scope conflation or mentions** — a block carrying several readings and one date, or
  this instrument's own docstrings describing a census.

So a date-correctness gate would fire on 9 and blame the author in all 9, while **2 of the 9 are the
register's defect**. Adding `firstSeenOn` to the accepted set repairs those 2 and leaves **7 fires,
0 findings** — [[R188]]'s exact shape, and [[R192]]'s 326/0 in miniature. **A gate that fires seven
times and finds nothing is not shipped here.**

---

## 4. The finding: R192's census was blind to R192's own case

[[R192]]'s census ruled arm (1) refuted on **326 fires / 0 findings**, and its handoff §4 recorded
the zero as a lower bound *because* `readAt` is a refresh log. This spec makes the bound concrete.

**MEASURED**, re-running the census's supersession test over the same 328 undated Evidence figure
occurrences, changing exactly one thing — the date a reading is deemed to have been taken — and
holding R192's own **strict** inequality on the document's date (its handoff §4 states and defends
that choice):

> **15 occurrences move from "current when written" to "already superseded when written".**

Seven of them are `apple 0.6289`, quoted in documents dated **2026-09-08**:

```
docs/superpowers/2026-09-08-after-the-two-counts-handoff.md:76
docs/superpowers/2026-09-08-r185-handoff.md:61
docs/superpowers/2026-09-08-r187-closed-handoff.md:40
docs/superpowers/2026-09-08-r61-handoff.md:70
docs/superpowers/2026-09-08-release-v0-0-4-handoff.md:65
docs/superpowers/2026-09-08-release-v0-0-4.md:153
docs/superpowers/2026-09-08-two-loops-handoff.md:77
```

`0.6289` was superseded by `0.71875`, which **entered the tree on 2026-09-07** (`f42ef99`) and which
the register did not record until **2026-09-08**. Under `readAt` the supersession lands on the same
day as those documents and R192's strict inequality discards it; under first-observation dating it
lands the day before, and the quotations are stale.

**That is the capability line — the eight-handoff `apple 0.6289` that [[R192]] was raised about.**
R192 found it by hand, in a spec; R192's census, run on `readAt`, scored it **0**.

### 4.1 What this does and does not do to R192's ruling

**It does not re-open arm (3).** R192 left Evidence ungated on *two* grounds, and only one moves.
The surviving ground is untouched and is sufficient on its own: **Evidence is append-only since
`5743af3`, so a firing gate can only ever be satisfied by a new append, never by a repair.** A gate
that cannot be satisfied by fixing the thing it complains about is unshippable whatever its hit rate.

**It does change what the ruling rests on.** "326 fires, 0 findings" must no longer be cited as
evidence that Evidence has nothing to find. On sound dating the same census finds 15, and the seven
that matter are the case that motivated the residue. R192's row is amended accordingly (§6).

**Deliberately NOT done: the 15 are not hand-classified into findings and non-findings.** R192's
census applied two further filters — a filename pattern for documents whose *subject is* the stale
figure, and hand-reading of the residual. 5 of the 15 are in the [[R187]] spec and plan, which that
filename filter already excludes. The other 10 are not classified here, because the ruling does not
turn on the exact count and classifying them is a second loop's work. **What is established is that
the count is not zero, and that it contains the motivating case.**

### 4.2 The denominator reconciles exactly: 326 → 328

R192's census reports **326** undated evidence figure occurrences; this re-run considers **328**.
The gap is not a method difference. R192 ran at `9716755`; this runs at `4b886a9`, the merge that
committed R192's own loop record — and that document contributes exactly two undated occurrences,
`0.9096` and `0.6289` at `docs/superpowers/2026-09-09-the-register-is-a-refresh-log.md:59-60`. A
census cannot see the document it is written in. **326 + 2 = 328**, and the two populations are
otherwise identical.

---

## 5. What ships

1. **`scripts/first_seen.py`** — the one-pass derivation of §1, over the register's own values,
   excluding `cor:notQuotable` rows per §2. **PROCEDURAL** under CLAUDE.md §8, and irreducible for
   the sanctioned reason: this is **raw extraction** — git history is not an RDF graph, so there is
   no evidence graph for an AXIOM to query until this has run. No tolerance, no threshold, no tuned
   constant: an exact substring match of a lexical form against added diff lines.
2. **A test pinning it** — that all 17 quotable readings resolve, that `1.0` is excluded by the
   register's own `notQuotable` flag rather than by a literal in the code, and that the derivation
   refuses to run on a shallow clone (reusing `_require_full_history`'s reasoning: on a shallow
   clone the pickaxe silently returns nothing and every reading would look unrecoverable).
3. **`vocab/internal/corpus.ttl`** — `corpus:readAt`'s `rdfs:comment` says what the property
   actually holds: the day the register was refreshed, which is at or after first observation, and
   is not a first-read date. **Nothing in `tests/corpus-manifest.ttl` is edited** — the register is
   append-only and, more to the point, every row in it is *true*; the defect was in reading it as
   provenance, which is what this comment repairs.
4. **The register rows** — [[R198]] closed, [[R192]] amended with §4.

### 5.1 What deliberately does NOT ship

- **No new `cor:` term and no new field in the manifest.** First observation is derived, and a
  derived value committed as data is a stored label (CLAUDE.md § Documentation governance).
- **No change to `tests/docgov_extract.py` or to either hard gate.** §3 measures them inert to this
  defect, and §3.1 measures the strengthening at 7 fires / 0 findings.
- **No committed census.** R192's handoff §4 gave the reason and it still holds: committing a
  one-off census as a test makes it a gate nobody chose. What is committed is the *dating
  primitive*, which R192's handoff specifically complained did not exist — *"nothing in the repo
  re-derives them, and a future loop wanting to re-measure must rewrite it."*

---

## 6. The falsifying oracle

**The claim this loop can be wrong about:** that the first-added-line-in-this-tree's-ancestry date
is a sound proxy for first observation.

**What falsifies it:** a reading whose value appears in the ancestry in a commit *earlier* than any
document that reports measuring it — i.e. the value was in the tree before anyone read it, which
would mean the match is coincidental rather than provenantial. §1's table is the check: `1.0` is
exactly that failure, at 81 days, and it is excluded on an independent ground (§2). If a *second*
row showed a large negative gap against a hand-read source, the derivation would be matching noise
and §4's finding would not stand.

**What does NOT falsify it:** a lag of a day or two between measuring and committing (§1.1 states
that as a known upper-bound property, not an error).
