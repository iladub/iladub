# Handoff — a firing is not a fact

**Serves:** prog:criterion:tab:09 — and `tab:02`, `tab:05`, `tab:07`, `tab:08` through the one
oracle all five name.

**Topic:** the previous handoff's § 5c, second bullet, taken as the standing direction (*return to
the arc: `etkl:05` through [[R44]]*). Walking it ends at a door that is not in the reading code:
**five `tab` criteria name a `prog:oracleTest` that does not exist**, `holon:06` names a second,
and the shared one cannot be written as stated because the three things it must read — *which
reason fires on which document*, *which reason an adjudication names*, *whether it disposes or
holds* — are prose, not facts. The prose has already drifted in two measured places. A spec for the
record exists; nothing is disposed and no `prog:met` moved.

**Date:** 2026-09-18. **Branch:** `a-firing-is-not-a-fact`, cut from `main` at `2f3fc76`.

**Doc impact: none** (the spec declares `increment` for the `cor:` terms it proposes; this loop
adds none).

**Written at an ESTIMATED ≈ 60k working tokens above a ≈ 46k baseline — estimated, not read.**
No figure was available to this session, so treat the number as an order of magnitude and part 5 as
graded per action either way, which CLAUDE.md requires above the 50K originating floor.

---

## 5. The next concrete action

*(Part 5 first, per CLAUDE.md § "The handoff's next action is TYPED".)*

### 5a. **A FORK for the maintainer — and it blocks the plan, so it comes first**

The spec's § 2.3 proposes typed vocabulary (`cor:Firing`, `cor:disposes`) where a cheaper rival
exists: a canonical sentinel inside the existing `cor:rationale` prose (`DISPOSES: ROUND_TRIP_FAIL`)
read by a gate of exactly the shape [[R187]] and [[R189]] already shipped as HARD. **That rival is
not a straw man** — this repo reads claims out of prose in two live gates today.

The single measured argument for the typed arm: a sentinel can *say* disposed but can never be
**refused** for disposing a reason the document does not fire — spec § 3's D2 — and the failure this
loop actually measured was a census asserting a firing profile the document no longer had.

**Why it blocks:** D2 is half of what the vocabulary buys. Ruled the other way, the plan is a
smaller and different document, and a plan written before the ruling is a plan to rewrite.

### 5b. **ASSERTED** — two things hold under either arm, and one of them is a hard constraint

- **`scripts/oracle_test_census.py` is the loop's close condition.** When
  `tests/test_corpus.py::test_escalation_reasons_are_adjudicated` stops being reported as dangling
  with all three controls still PASS, the oracle exists; until then it does not, whatever any
  document says. This is mechanical — run the command.
- **The execution loop's first task is a full-corpus run, and it must be SERIAL.** The record
  cannot be written for 6 of 7 documents without one (~47 min; only bfs was re-measured here).
  Three memory kills are already on record for running two corpus compiles at once. This is not a
  preference.

### 5c. **PROPOSED** — the drift is worse than the two instances measured, and this must be RUN

**The prediction:** the `# FIRES` comments drifted on the two documents anybody re-measured (bfs,
via [[R44]]'s triage), and five of the seven corpus documents have never been re-measured against
them at all. I expect the first full run of `scripts/escalation_census.py` to contradict at least
one more comment — apple's `tab:08` p1 firing and `tab:02`'s *"apple x8 (p0 x4, p2 x4)"* are the
most exposed, both dated 2026-08-20 and both on a document whose adoption path has changed twice
since.

**Why it is PROPOSED and must be run before anything rests on it:** the only two drifts I measured
are both on bfs, and bfs is the document four loops have been editing. *Recently edited ⇒ drifted*
is not *unedited ⇒ accurate*, and a record built on the assumption that the other six comments are
fine would bake in exactly the error this loop is about. **If the run contradicts nothing, that is
a real result too** — it means the comments' problem is that nobody reads them, not that they lie,
and the spec's § 2 argument narrows to the adjudication half.

### 5d. Still available, and untouched: **[[R258]]'s arm B**

The previous handoff's other bullet. Its scope is settled, its population bounded, its falsifier in
CI; only the second reading and its disposal are unbuilt. Nothing here consumed it, and jumping the
queue to it still needs the ruling that handoff asked for.

---

## 1. Where the primaries are

| | |
| --- | --- |
| spec | `docs/superpowers/specs/2026-09-18-a-firing-is-not-a-fact-design.md` — § 2 the terms, § 2.3 the fork, § 3 what to build, § 5 the oracles, § 6 what is NOT done, § 7 the weakest parts |
| evidence | `docs/superpowers/2026-09-18-a-firing-is-not-a-fact-evidence.md` — § 1 the census, § 2 the vocabulary gap, § 3 the drift, § 4 the stale control, § 5 falsification |
| new instrument | `scripts/oracle_test_census.py` — 3 controls, one of which caught a real bug in it on its first run |
| the repair | `scripts/bfs_reason_triage.py` — control leg re-pinned 404 → 496 with the citation inline |
| the rows | [[R259]] (the record), [[R260]] (the stale control literal) — `residues.md` + `residues-open.md` |
| the gate that makes this binding | `tests/test_arc_manifest.py:313-326` — M5b, met-gated on purpose |
| prior loop | `docs/superpowers/2026-09-18-is-arm-b-circular-handoff.md` — its § 5c is what this walked |

## 2. What was decided, and where it is recorded

- **Nothing was disposed and no `prog:met` moved.** Deliberate, spec § 6: disposing a reason is a
  judgment about a reading and belongs to a loop that can make it.
- **The bfs triage control was repaired in place rather than left failing.** An instrument printing
  *"do not trust the tally above"* over a correct tally actively misleads the next loop; the class
  stays open as [[R260]] because the durable fix needs a committed source for the figure.
- **Two rows raised, none closed.**

## 3. What is UNVERIFIED, and must not be asserted

- **That the other six documents' `# FIRES` comments are accurate.** Only bfs was re-measured
  (§ 5c). Five of seven documents are unmeasured against their own census.
- **That D3a can read the manifest at pytest collection time** without importing rdflib into a
  module CI collects under memory pressure. Spec § 7 names it as the part to re-measure first.
- **That `cor:Firing` is the right shape rather than the first one that fits.** It is modelled on
  `cor:Reading` by analogy; no loop has tried to write the record and found the model wanting.
- **The ≈ 60k working-token figure in this file's header.** Estimated, not read.
- **[[R251]], [[R252]], [[R253]], [[R254]], [[R256]], [[R257]], [[R258]] are untouched.**

## 4. Traps this loop paid for

1. **The control caught the instrument, not the repo.** `oracle_test_census.py`'s first run
   reported `0 declarations` and a FAILing control, because it had the namespace as
   `…/iladub/prog#` where the manifest declares `…/iladub/progress#`. Without the substrate leg it
   would have printed a clean, confident, empty census. **An instrument whose control cannot fail
   on day one is decoration** — this one failed on minute one.
2. **A stale literal inverts a verdict rather than announcing itself.** `bfs_reason_triage.py`
   exits 1 and says *"do not trust the tally"*; the tally is right and the control is wrong, and a
   reader in a hurry draws exactly the wrong conclusion about bfs. Read *which leg* failed before
   believing what a failing instrument says about its subject.
3. **A Turtle comment is invisible to every instrument in this repo, by construction.** Five
   `# FIRES n` census lines have sat in `tests/arc-manifest.ttl` since 2026-08-20; the parser drops
   them, so no gate, query or strip has ever read one. Recording a figure in a comment is recording
   it nowhere.
4. **`grep -rn --include=*.py` fails under zsh** (`no matches found`), silently answering a
   different question than the one asked. The known zsh-quoting family, in a new shape; `git grep`
   has no such problem and was what finally answered it.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
