# Handoff — v0.0.4 is released, and the item "nothing in this repo can verify" was verified in one call

**Topic:** the release loop. `RELEASE.md` steps 1–6 run end to end; **v0.0.4** is the first tag
since 2026-08-02, and the first ever cut with the contradiction gate passing rather than bypassed.

**The part worth reading is not the tag.** It is that the predecessor handoff's §5b — the one item
it graded PROPOSED and called *"unverifiable from here"*, the single thing standing between one
loop and two — was answered by `gh run view` on the **previous release's own run**. The claim was
about the repo's *files*; the pipeline's run history is evidence too.

**Written 2026-09-08**, in the loop that ran action **5a** of
`docs/superpowers/2026-09-08-r185-handoff.md`.

**Part 5 was written FIRST**, before parts 1–4, per CLAUDE.md § *The handoff's next action is
TYPED*. It is typed per action.

**Doc impact: none.**

---

## 5. The next concrete action

The release train has reached the station. Both open forks this loop leaves behind
([[R186]], [[R187]]) are blocked on the **same missing thing: a count**.

### 5a. ASSERTED — take the two counts both forks are blocked on

Asserted because the outcome is a number, the method is `git log` and `grep`, and taking the
count *is* the work. Neither fork can be argued before it exists; both rows say so in their own
"measure before choosing" clause.

- **[[R186]]'s count.** *How many tracked files under `docs/superpowers/**` have commits dated
  after their own loop closed, and how many of those **rewrote** rather than **appended**?* The
  R185 loop found exactly **one** by accident and its row says, literally, *"do not read 'one' as
  the population."* Arm 1 (enforce immutability by lint) is refuted the moment the rewrite count
  is non-trivial; arm 3 (delete the word "immutable") is refuted the moment it is zero.
- **[[R187]]'s count.** *How many decimals across `docs/wiki/**` are corpus measurements at all —
  as opposed to thresholds, versions, confidences — and how many does the tree still read?* This
  loop counted them in **one page** (`data-grid.md`: 4 figures, 2 stale) and generalised nothing.

Both are cheap and both are **delegable measurement**, not authorship (§ managing-context-budget).
Take them before designing anything.

### 5b. PROPOSED — that [[R186]] and [[R187]] are ONE loop, not two

They look like different subjects — Evidence immutability, wiki figure staleness — and they fork on
the *same* question: **is a claim's provenance carried in the file, or in an instrument?** R186 arm 2
(freeze only the `Doc impact:` line, everything else append-only) and R187 arm 1 (date the figure
inline, strike rather than replace) are the same answer written twice; R186 arm 1 and R187 arm 2 are
both "put it in a lint/gate instead". A loop that rules one has ruled most of the other.

**Graded PROPOSED, and this is the prediction to run first:** it fails if the two counts come back
with opposite shapes — e.g. Evidence rewrites are near-zero (R186 collapses to arm 3, a one-line
CLAUDE.md edit) while wiki stale figures are widespread (R187 needs a real instrument). Then they
are two loops and CLAUDE.md § Plan authoring discipline rule 6 says do not fold them. **Run 5a
before believing 5b** — that is three greps, and it decides whether the next spec covers one
subject or two.

### 5c. PROPOSED — the capability claim, carried forward UNCHANGED and still unmeasured

Carried verbatim for the **sixth** handoff running, and still not re-measured — this loop touched
no reader:

```
graincorp  0.9654      bfs   0.9401      WHO   0.9096      apple  0.6289
```

**This loop has moved it from "unmeasured" to "partly known-stale", and that is a downgrade, not
a reassurance.** `graincorp 0.9654` is superseded by [[R174]] (`0.9658886894075404` since
`20cc5b8`, 2026-09-05) wherever it names the stem document score, and the `0.3556` apple figure
in the same wiki page is superseded by [[R165]]. **Re-measure before any of them reaches a
published page** — this release avoided the question by promoting zero, not by answering it.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| this loop's evidence | `docs/superpowers/2026-09-08-release-v0-0-4.md` | §0 (the 5b refutation, with the three commands), §3 (the guard that did not exist) |
| what the release ruled | the PR, and §1 of that evidence doc | promote **zero**, ruled by the maintainer from a three-arm choice |
| the release procedure | `RELEASE.md` | step 3 now names **two** guards, not one — read the parenthetical for what was false |
| the new guard | `tests/test_smoke.py::test_citation_version_matches` | it exists because `CITATION.cff` was guarded by nothing |
| the new residue | [[R187]] in `docs/superpowers/residues-open.md` | the three arms, and the count nobody has taken |
| the predecessor | `docs/superpowers/2026-09-08-r185-handoff.md` | §5b, as the worked example of "unverifiable from here" being verifiable |
| the drain register | `tests/docgov-drains.ttl` | why the gate passed without a new drain this release |

## 2. What changed

Version `0.0.3` → `0.0.4` in `pyproject.toml`, `src/iladub/__init__.py`, `CITATION.cff`
(+ `date-released: 2026-09-08`). New: `tests/test_smoke.py::test_citation_version_matches`,
`docs/superpowers/2026-09-08-release-v0-0-4.md`, [[R187]] in the register. Changed: `RELEASE.md`
step 3 (two guards named; `date-released` declared unguarded) and its step 5 example tag.
**No source file under `src/` changed** apart from the version string — this loop touched no
reader, and its blast radius on corpus tests is nil by construction.

## 3. What was decided, and where that decision is recorded

- **Promote zero from the wiki queue.** Ruled by the maintainer; recorded in
  `docs/superpowers/2026-09-08-release-v0-0-4.md` §1 and in the PR body. The five pages stay
  queued and the lint goes on reporting them — that is the design, not a leak.
- **`RELEASE.md` is corrected by ADDING the guard, not by weakening the sentence.** Recorded in
  the evidence doc §3 and in the test's own docstring. The alternative — editing the manual to
  say "two files" — would have left the citable record of every release unguarded.
- **`data-grid.md` is NOT edited to refresh its stale figures.** Recorded in [[R187]]'s deferral
  column. Rewriting a loop's measured figures in place destroys the record rather than dating it;
  which of the three arms fixes that is the fork, and it is not this loop's to take.
- **The PyPI Trusted Publisher question is closed by CI history, not by asking.** Recorded in the
  evidence doc §0, with the run id (`30730453507`) and the PyPI upload timestamp.
- **`CITATION.cff: date-released:` is guarded by nothing, deliberately.** Recorded in `RELEASE.md`
  step 3. It cannot be checked against a tag that does not exist yet; the honest remedy was to say
  so in the manual, not to invent a guard that would fire on every non-release commit.

## 4. Unverified or assumed

- **The full suite was launched detached** and its result is in the PR / final commit message. It
  was launched **before** three of this loop's edits landed (`test_citation_version_matches`, the
  `RELEASE.md` correction, the two register rows), so it is not evidence about them. Those three
  were verified separately: `tests/test_smoke.py` **3 passed** (with falsification),
  `tests/test_residue_register_integrity.py tests/test_doc_governance.py` **10 passed**, both run
  *after* the edits. CI on the PR runs the whole tree.
- **CI green is NOT full-suite evidence on this repo** ([[R173]]) — `corpus/` is gitignored, so
  corpus-gated tests skip there. This loop touches no reader; *should be nil* is the assumption.
- **The Trusted Publisher evidence is historical.** It proves the publisher was configured and
  used on 2026-08-02. A publisher can be revoked on pypi.org and nothing in this repo would see
  it. If the tag build's publish step errors with OIDC, that is the residual risk, and the site
  will already have deployed.
- **The gate passing is not evidence the two 2026-08-10 wiki pages are correct** — carried
  unchanged from the R185 handoff; `scripts/release_gate.py` exiting 0 means a drain was
  *recorded*, and spec §3.3 says SHACL cannot read prose.
- **[[R187]]'s population is one page.** Four figures counted, two stale. Do not read that ratio
  as the wiki's.
- **A process note.** The R185 handoff's §5b named the account owner as the only route to a fact
  the CI history already carried. It was graded PROPOSED, which is exactly right and is why it was
  checked rather than obeyed — but the lesson generalises past the grade: **before writing
  "unverifiable from here", ask whether the thing has ever run.** A pipeline that has executed a
  step once has left evidence that it was configured.

---

## APPENDED 2026-09-08, after the tag — the release outcome

**Strictly additive.** Parts 1–5 above are untouched; part 5 in particular is the reasoning written
first, and is left exactly as it was authored. This block records what the pipeline did, which was
unknown when the rest was written. (Whether appending to Evidence is legitimate at all is [[R186]]'s
open question; this is the append arm, not the rewrite arm, and it is labelled so the distinction is
readable rather than assumed.)

**`v0.0.4` shipped.** Release run `34254093475`, tag `v0.0.4`, from `1007d48` on `main`. Every step
of the pipeline reported `success` — including the two that could have failed independently:

```
Tag must match pyproject version=success          ← the guard on step 3's bump
Tests (incl. doc-governance lint)=success
Release gate — no undrained contradiction=success ← first tag ever cut with this passing
Deploy iladub.dev (gh-pages)=success
Publish to PyPI (trusted publishing)=success      ← the residual risk in part 4, discharged
```

**Verified independently of the run's own self-report**, because a green step and a live artifact
are different claims:

| what | measured | result |
| --- | --- | --- |
| PyPI | `curl https://pypi.org/pypi/iladub/json` | `latest: 0.0.4`; wheel `17:06:03`, sdist `17:06:05` |
| iladub.dev | `curl -sIL https://iladub.dev` | `200` |
| the deploy is THIS commit | `gh api …/branches/gh-pages` | `Deployed 1007d48 with MkDocs 1.6.1`, `17:05:41Z` |
| w3id content negotiation | `curl -L -H "Accept: text/turtle" https://w3id.org/iladub` | `200` → `raw.githubusercontent.com/…/vocab/ontology/iladub.ttl` |
| w3id, HTML leg | `curl -L -H "Accept: text/html" https://w3id.org/iladub` | `200` → `iladub.dev/assertion-proposition/` |

**The Trusted Publisher caveat in part 4 is now discharged for this release** — the publisher was
not merely configured in 2026-08, it published four minutes ago. The caveat's *form* still holds for
the next release: the evidence is again historical the moment this is written.

**One thing part 4 said would be nil, and was.** The full suite ran **1538 passed, 7 skipped, 1
xfailed** in 56:10 with the corpus present — zero failures, on a branch that touched no reader. The
[[R173]] eight did not appear. That is worth exactly one line and no more: this branch is not the
place to conclude anything about R173, whose CI-visibility half stays open and unpriced.
