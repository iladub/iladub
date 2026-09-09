# Handoff — first observation is recoverable, and R192's zero was measured by a blind instrument

**Topic:** action **5a** of `docs/superpowers/2026-09-09-the-register-is-a-refresh-log-handoff.md`,
graded PROPOSED, is taken. [[R198]] **CLOSED**. [[R192]] **amended** — its headline zero does not
survive sound dating. [[R200]] raised as a measured refusal.

**Written 2026-09-09**, part 5 first.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — hand-classify the 10 unclassified occurrences of the spec's §4

Mechanical, and doing it *is* the work: open ten Evidence occurrences in their files and decide, one
by one, whether each is a stale figure stated as fact or an exculpated case. The list is spec §4;
five of the fifteen are already excluded by R192's own filename filter (the [[R187]] spec and plan),
and the other ten are named there with file and line.

Apply R192's two published exculpations unchanged — *the document's subject IS the stale figure*, and
*the sentence names its own staleness* — so the classification is comparable to the 326/0 it amends.

**Why asserted:** no prediction is being run. The outcome is a count, every input is on disk, and no
design decision hangs on which way it comes out. **What it settles:** R192's finding count is
currently known only as *"not zero, and it contains the motivating case"*. Ten reads make it a
number.

**What it must NOT do:** re-open arm (3). Spec §4.1 states why the append-only ground is sufficient
alone, whatever the ten turn out to be.

### 5b. ASSERTED — [[R200]] stays unbuilt, and the row is the record of why

Nothing to run. A date-correctness gate measures **7 fires / 0 findings** once first observation is
admitted (spec §3.1), which is [[R188]]'s exact shape. The row carries the measurement so the next
loop does not re-propose it from first principles — the gate looks obviously right and is measurably
not.

**If a future loop proposes closing R200 by widening the accepted date set, refuse it.** That moves
the denominator and finds nothing. The 7 are block-scope conflation, which is a **scope** question
(per-figure vs per-block) and a re-litigation of the R187 block boundary.

### 5c. ASSERTED — [[R199]] is untouched and its predecessor's 5b/5c carry forward verbatim

This loop measured nothing about truncation and nothing about unregistered figures. The previous
handoff's 5b and 5c stand exactly as written.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the spec, and all six measurements | `docs/superpowers/specs/2026-09-09-first-observation-is-recoverable-design.md` | §1 the 18-row recoverability table and the two agreeing instruments; §2 why `1.0` needs no new exemption; §3 that `readAt` is inert to both gates; §3.1 the refused strengthening at 7/0; §4 the 15, and §4.2 why the denominator is 328 not 326 |
| the dating primitive | `scripts/first_seen.py` | that it DERIVES from git and stores nothing; the §8 PROCEDURAL justification; that the `notQuotable` exclusion is read from the register |
| its tests | `tests/test_first_seen.py` | 7 tests, what each PINS rather than what it measures today; the wiring test that exists because falsification found the gap |
| the amended rows | [[R192]], [[R198]], [[R200]] in `residues.md` + `residues-open.md` / `residues-closed.md` | R192: what may no longer be cited, and that arm (3) still stands; R200: the refusal and what would NOT close it |

## 2. What changed

One branch, `r198-readat-is-a-refresh-log`, off `4b886a9`.

- **New:** `scripts/first_seen.py`, `tests/test_first_seen.py`, the spec, this handoff, [[R200]].
- **Modified:** `vocab/internal/corpus.ttl` — `corpus:readAt`'s `rdfs:comment` only.
- **Register:** [[R198]] struck and moved to `residues-closed.md`; [[R192]] amended in place.
- **NOT modified:** `tests/corpus-manifest.ttl`, `tests/docgov_extract.py`, both hard gates,
  `vocab/queries/docgov-undated-figure.rq`.

## 3. What was decided, and where that decision is recorded

- **No register redesign, and no new `cor:` term.** Spec §0 and §5.1. Ground: first observation is
  derived in 9.6s, and a derived value committed as data is a stored label.
- **The manifest is not edited.** Spec §5 item 3 and R198's closure row. Ground: every row in it is true;
  the defect was reading a refresh date as provenance, and that lived in the vocabulary comment.
- **The date-correctness gate is refused.** [[R200]]'s row, spec §3.1. Ground: 7 fires, 0 findings.
- **R192's arm (3) is not re-opened.** Spec §4.1, R192's amended row. Ground: its append-only
  ground is sufficient alone and does not depend on the hit rate.
- **The 10 are left unclassified.** Spec §4, deliberately, and 5a is the action that ends it.

## 4. Unverified or assumed

- **CI RAN, FAILED, and the failure was a real defect — now fixed.** `scripts/first_seen.py` scoped
  the pickaxe to `main`, which passed all 7 tests locally and exited 128 in CI: `actions/checkout`
  leaves a detached HEAD with no local `main` ref. The scope is now `HEAD`, measured identical to
  `main` on all 17 readings, and `test_it_runs_on_a_detached_HEAD_with_no_branch_ref` reproduces the
  CI condition locally (it fails when the default is reverted to a named branch). **The deeper defect
  the crash exposed:** under `main` scope a PR appending a NEW reading would report it unrecoverable
  and could never merge — the unsatisfiable-gate shape spec §4.1 rejects for Evidence, which this
  loop had nearly shipped in its own instrument.
- **The full suite (~61 min) has still not passed locally in this session** — the first run died on
  an unrecognised `--timeout` flag while the harness reported exit 0, and the retry was killed before
  emitting output. **CI is the check, and its second run is the one that matters.**
- **Method parity with R192's census is INFERRED, not verified.** Its instrument was scratch code
  and was never committed — its own handoff §4 says so — so this re-run reproduces the method *as
  described in that handoff's prose*: the same 328 undated evidence occurrences, the same strict
  inequality on the document's date, changing only the dating scheme. §4.2 reconciles the
  denominator exactly (326 + the 2 occurrences inside R192's own loop record = 328), which is strong
  evidence of parity but is not the same as running both instruments side by side. **The one place
  this could bite: if R192's census dated documents differently from filename-then-last-commit-date,
  the 15 could shift.** It would not plausibly shift to zero — the seven `0.6289` rows turn on a
  one-day gap that no reasonable document-dating rule erases.
- **The 15 are not read.** Only their arithmetic is established. 5a is exactly this gap.
- **First observation bounds observation from ABOVE and does not recover the instant of
  measurement** (spec §1.1). A value measured on the 7th and committed on the 8th reads as the 8th.
  Every claim here is of the form "no later than", never "exactly on".
- **`--all` vs `main` agree on dates today, for all 18.** That is measured at `4b886a9` and is not
  guaranteed to hold for a reading whose value first appeared on a branch that took days to merge.
- **The 9.6s figure is one machine, one run**, against 56.7s for the 18-pickaxe equivalent. The
  ratio is the durable claim, not the absolute.
