# D1 measured against a widened gate — the coupling really was broken, and the oracle splits

**Serves:** prog:criterion:etkl:04 — R225's own subject, the 41 border-only bands, measured for
the first time against a gate that no longer demands the page assert nothing.

**Date:** 2026-09-14. **Branch:** `r225-d1-resolution-test`, cut from `e9f772f`.

**Doc impact: none.** No released term. One new instrument
(`scripts/supersession_chain_depth.py`); no vocabulary, shape or contract is touched.

**Part 5 is written FIRST**, per CLAUDE.md § Loop & context hygiene, and each action is typed
assertion-or-proposition.

---

## 5. The next concrete action

### 5a. PROPOSED — the trade is a maintainer's ruling, and the loop should stop here until it lands

**This rests on a judgement that is not mine to make, and the work behind it is done.** Both D1
placements now keep ons's grid — the thing R225's row names as its oracle — and both drop ons's
*score*. The row's oracle is written two ways at once and this measurement separates them:

* *"ons must not lose its grid"* — **MET.** 571 cells, per-page identical, under both placements.
* *"byte-identical by canonical graph hash at 0.9719934102"* — **NOT MET.** 0.7712 (relocated),
  0.7431 (original); hashes move.

The score falls because the fused bands were booking their ink as **nothing**. Under the defect
ons p7/p8 classify `NON_TABLE / fewer than 2 columns`, are IGNORED as prose, and contribute 0 to
both sides of the ratio; the fallback then asserts 276 cells against a denominator that excludes
the 142 tokens the fusion hid. Repair the fusion and those bands classify honestly — 5 zero-cell
escalations and 142 escalated tokens appear (p7 0→80, p8 0→62), and the denominator grows.

**So the question is not "did D1 regress ons" but "what was 0.9720 measuring".** If a score may
not fall when a concealed escalation becomes visible, then no repair of this class can ever land,
and R225 is unclosable by construction.

**RULED 2026-09-14 by the maintainer: the score drop is correct; ship the relocated placement.**

**And the ruling costs less than this section first claimed — CORRECTED, measured.** An earlier
draft here said "the pinned figure is re-adjudicated". **ons has no pinned figure to re-adjudicate.**
Its `cor:Document` node carries `cor:expectedVerdict cor:Unadjudicated` and **no `cor:scoreFloor`**
(`tests/corpus-manifest.ttl:107`), under a 2026-08-20 HOLD whose rationale already refused the old
number in terms that read as if written for today: *"A score of 0.9720 on an unread nine-page
document is precisely the shape of evidence this register exists to refuse to accept. Held."* So no
CI floor breaks — `tests/test_corpus.py` reads only `floor` and `verdict` (`:50`) — and ons was
never one of § 1a's five floor-pinned documents, which is precisely why it is free to move. What is
owed instead is a new dated `cor:reading`, and § 4 records which ones.

### 5b. ASSERTED — if the ruling accepts the trade, the relocated placement is the one to ship, and D3 is its precondition

Mechanical once ruled. The relocated placement (`0e64a86`'s form, recoverable by reverse-applying
`54c0edf`) keeps R13's closure intact where the original breaks it. But it **destroys R224's
fallback fixture**: `border_only_grid_pdf` reaches the gate *by being R225's defect reproduced
synthetically*, so repairing the defect makes the page read completely through bands
(`RECORD_TABLE`, 20 cells, score 1.0, 1 region instead of 2). Spec § 4's D3 is therefore not
optional — without a replacement fixture the fallback branch loses the only CI coverage it has
ever had, which R224 created eight days ago.

**REVISED by measurement, same day: D3 may be unconstructible, and spec § 7 already ruled what to
do about it.** Four candidates were run and the vice is structural (§ 3). The branch also has no
live corpus instance left once D1 lands (§ 3), so there is nothing to point a corpus test at
either. Spec § 7's standing instruction governs: *"If D3 ships without a fixture that provably
reaches the gate, the fallback branch loses the CI coverage R224 created, and that must be raised
as a residue rather than left silent."* So the plan is: re-point R224's two invariants at the
ADOPTION route, where the same claims (a region books the ink it claims; a region names the table
it asserted) are live on ons p7/p8 — and raise the residue that the FALLBACK branch specifically is
now uncovered and unreached. **Do not delete the branch in this loop**: § Producer-side guards vs
the membrane requires provable total coverage before removing a guard, and "no corpus instance
today" is not that proof.

### 5c. ASSERTED — what this loop must NOT be read as having done

No D1 variant is committed; both live only in scratchpad worktrees. The full suite has **not**
been run on either — § 1d's twelve failures were all measured pre-D2 and none of them has been
re-checked. R226 is untouched. The ons `chains 3 → 1` change is measured and **undiagnosed**.

---

## 1. Where the primaries are

- **The two D1 variants** — both recoverable from git, neither committed: the *relocated* form by
  reverse-applying `54c0edf` (`git show 54c0edf -- src/iladub/etkl/compile.py | git apply -R`),
  the *original* form as `git diff 3ee9495^ 3ee9495 -- src/iladub/etkl/compile.py`. Both apply
  cleanly onto post-D2 `compile.py`.
- **The gate that used to refuse them** — `vocab/queries/adoption-candidate.rq`. Read it: the
  `FILTER NOT EXISTS { ?cell a tab:EntryCell }` clause is **gone**, and the query is now a pure
  positive ASK. That deletion is why this loop could measure anything at all.
- **The fallback gate, which D2 did NOT widen** — `compile.py:1351`,
  `asserted_total == 0 and escalated_total == 0`, with its own comment on why it must stay narrow.
- **The snapshots** — session-local under the scratchpad (`before/`, `after-reloc/`, `after-orig/`,
  `after-reloc-full/`); the figures below are the surviving record, which is [[R227]]'s handoff
  lesson repeating.
- **The new instrument** — `scripts/supersession_chain_depth.py`, for [[R227]]'s open half.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| Re-point R224's I1/I2 at adoption; retire I3 (no document-scope subject) | [[R228]]; the two test docstrings |
| Do NOT delete the fallback branch — coverage proof first | [[R228]]; § Producer-side guards |
| The `chains` identity loss is raised, not repaired here | [[R229]] |
| The original placement is NOT dominated — it reads 27 more bfs p6 cells | § 3 below; nowhere else |
| The relocated placement is the ship candidate (keeps R13's closure) | § 3; `0e64a86`'s message for the pre-D2 half |
| No full suite run until the trade is ruled (~51 min, worthless if refused) | this file only |
| D3 is a precondition of shipping D1, not a follow-up | spec § 4 D3; § 5b above |

## 3. The measurement

Baseline is `e9f772f` (main, D2 landed, D1 absent). Every figure from
`scripts/corpus_verdict_snapshot.py`, guards fired before each run (interpreter resolving inside
the worktree, corpus symlink verified — either trap yields a false result).

```
                    baseline          relocated D1      original D1
ons   score       0.9719934102       0.7712418301      0.7430730479
      cells               571                571               571
      per-page  [0,0,0,0,19,0,0,276,276]   identical        identical
      adopted                []             [7, 8]            [7, 8]
bfs   score       0.8890554723       0.8850746269      0.8861232109
      cells               671                671               698
      adopted               [5]                [5]            [5, 6]
      p6 cells              267                267               294
```

**ons p7/p8 change route, not content.** `adopted [] → [7,8]`: the fallback shuts (its gate needs
`asserted_total == 0`, and repaired bands assert) and *adoption* recovers the same 276+276 cells.
This is the mechanism predicted from `compile.py:1351` before it was run.

**R225's bfs half is met literally:** p5 stays adopted at exactly 404 cells and gains **no**
zero-cell escalations (3 → 3). ons gains 5 (p7 0→3, p8 0→2).

**ons `chains 3 → 1` — DIAGNOSED, and it is a finding, not noise.** Before: three singletons
`(p4#htable2,)`, `(p7#p7-datagrid,)`, `(p8#p8-datagrid,)`. After: only `(p4#htable2,)`. The cause is
an identity change, measured on the region's own `table_uri`:

```
before  p7: p7#p7-datagrid        after  p7: adopt#p7-datagrid
before  p8: p8#p8-datagrid        after  p8: adopt#p8-datagrid
```

Moving from the fallback to adoption re-mints the asserting region under the **adopt-scoped** doc
URI, and chain assembly keys on the page-scoped one — so two readings that still carry 276 cells
each vanish from `chains` while their cells survive. `recognized`, `refused_licences` and
`repaired_bands` are all empty on both sides, so nothing else moved. This is the [[R202]] /
[[R226]] family again — a region the stitch sites cannot name — arriving from a new direction, and
it is a **candidate residue row** rather than something this loop repairs.

**I1 — MET, all five pinned documents byte-identical by canonical graph hash.**

```
cbh-stem             ba056c0ed809 = ba056c0ed809     graincorp-capacity  3b54f16194ca = 3b54f16194ca
graincorp-stem       496c315f2fcc = 496c315f2fcc     apple               cabc69d718d6 = cabc69d718d6
who-wfa              7e6038064128 = 7e6038064128
```

**apple is the one that had to be measured rather than inferred, and it held.** § 1a's
zero-under-resolved-bands census was taken PRE-D2; D2 makes apple p2 adopt, which triggers a second
page compile whose bands D1 would reshape, so byte-identity there could not be read off that census.
It was measured, not assumed. The two-document screen and the full seven-document sweep also agree
to the digit on both movers (bfs `e3903f3046f5`, ons `afe6d4bd3108`), which is the cross-check that
the narrowed screen was sound.

**THE FALLBACK BRANCH HAS NO LIVE CORPUS INSTANCE ONCE D1 LANDS.** The two routes are
distinguishable in the snapshots because adoption re-mints under an `adopt#` doc URI where the
fallback is page-scoped, so the scan is exact:

```
baseline   ons p7  p7#p7-datagrid       276  asserted   <- FALLBACK (compile.py:1351)
           ons p8  p8#p8-datagrid       276  asserted   <- FALLBACK
post-D1    ons p7  adopt#p7-datagrid    276  asserted   <- ADOPTION
           ons p8  adopt#p8-datagrid    276  asserted   <- ADOPTION
           (apple p2 and bfs p5 were already adoption-scoped on both sides)
```

Zero page-scoped datagrid regions remain anywhere in the corpus. ons p7/p8 were the branch's
**only** live instances (its own comment at `:1339` names them), so D1 retires it on real data.

**AND D3 — A REPLACEMENT FIXTURE — LOOKS UNCONSTRUCTIBLE, WITH AN ARGUMENT AND NOT ONLY FAILED
ATTEMPTS.** Four candidate shapes were drawn and run through the production path with D1 applied:

```
A  single-run bands, differing x      asserted=0 escalated=0  gate=OPEN   grid=None
B  two-run rows, one line per band    asserted=6              gate=shut   (the 3 bands MERGED)
C  ragged x inside bands              asserted=12             gate=shut   both bands RECORD_TABLE
D  lightly ragged x                   asserted=12             gate=shut   both bands RECORD_TABLE
```

A opens the gate and has nothing to read; B, C and D all read through the bands instead. The
mechanism is a vice: a band's leaf grid and the page-wide grid consult the **same alignment
evidence**, so any page whose grid resolves >= 2 columns is a page whose bands do too. The one
mechanism that ever separated them was the fusion defect D1 removes.

The counting argument for why no shape escapes: the gate needs every >= 2-run row isolated in a band
of <= 1 line (so it is IGNORED as "fewer than 2 lines" rather than classified), `datagrid.py:341`
needs >= 2-run rows to be the MODAL row signature, and `bands.py:37-52` splits only where a gap
exceeds 1.8x the MEDIAN gap — so the small gaps that permit any split can come only from multi-line
single-run bands. That requires #prose-lines > #large-gaps ~ #data-rows AND #data-rows >
#prose-lines at once. **This is a proposition**: it is a counting argument over three shipped
mechanisms, not a proof, and one candidate outside these four could still refute it.

> ## REFUTED THE SAME DAY, BY THE FIFTH SHAPE — and the grading is why it was cheap
>
> **The argument is WRONG, and precisely at the word "modal".** It read modal as
> majority-by-count. `datagrid.py:337` maximises **`len(s) * counts[s]`** — runs times rows — so 8
> two-run rows score **16** against 10 one-run rows' **10**, and the two-column universe wins
> without the data rows being anywhere near a majority. The contradiction I derived (#prose-lines >
> #data-rows *and* #data-rows > #prose-lines) simply does not bind.
>
> **Candidate E, measured, D1 applied:** one TALL prose band — 10 single-word lines at a 14pt pitch
> — supplying NINE small gaps so `detect_bands`' median is 14 and its threshold 25.2; then 8 data
> rows each behind a 60pt gap, so each becomes its own single-line band. Result: **9 bands, all
> ignored** (prose band "fewer than 2 columns", each data band "fewer than 2 lines"),
> `asserted=0 escalated=0` so **the gate opens**, `derive_data_grid` -> `rows=8 cols=2`, and with
> the fallback on **10 regions = bands + 1** carrying **16 cells** on `…#p0-datagrid` — booking
> **16** tokens, naming its table, with every ignored band booking **0**. `validate_shapes=True`
> passes on the same shape. **It draws NO rules at all**, so `len(xs) >= 2` is false, D1's
> comparison never runs, and the mechanism cannot be repaired out from under this fixture the way
> it was from under `border_only_grid_pdf`.
>
> Shipped as `isolated_rows_grid_pdf`, with all ten of its docstring's claims verified against the
> committed function (0 false). **Three tests come back off the retired list** — the fallback-gate
> test, the SHACL-through-production test, and [[R224]]'s I3 — and both `test_datagrid` ones lose
> their corpus gates, so they now hold the line on every push rather than only where the
> gitignored corpus is present. **R72's witness A stays retired**: `page_has_table` is False on
> this page and the corpus-wide sweep found no table page that reads nothing, which is a separate
> and still-measured finding.
>
> **The lesson is about the grade, not the error.** This was labelled a proposition and ordered to
> be run before anything was built on it; it cost one probe to refute and turned a permanent
> coverage loss into restored CI coverage. Had it shipped as a theorem, [[R228]] would have
> justified deleting a branch on reasoning that was wrong at one word.

**[[R227]] 5b, argument half — CLOSED by reading, no corpus needed.** A third supersession hop is
unreachable by construction: there are exactly two writers (`document.py:1563` section repair,
`:1827` adoption); repair is the pass at `:1513` and adoption a strictly later pass at `:1665`;
adoption attaches to `_effective_verdict(v1)`, the chain head; each page is adopted at most once;
and `_verdict_decision` matches only `{page_doc}#region{idx}-d`, while the admission is minted
`{grid_uri}-admission` (`:1809`) — so it can never be returned, and adoption cannot chain onto an
adoption. Lineage is capped at **two edges**.

**[[R227]] 5b, empirical half — RUN, and it REFUTES the row's own claim.** The row says *"the walk
is exercised at chain length 2 only"*. Measured on main at `e9f772f` with `HAS_D1: False` verified
before the run (`scripts/supersession_chain_depth.py`, which prints the unit because this is exactly
the figure a unitless number gets wrong):

```
cbh     4 edges / 4 chains / max 1  →  p0#region1-d5 ← p0/r2#region1-d5        (section repair)
apple   6 edges / 6 chains / max 1  →  p2#region2-d3 ← p2/adopt#p2-datagrid-admission
bfs     5 edges / 5 chains / max 1  →  p5#region10-d4 ← p5/adopt#p5-datagrid-admission
ons, who-wfa, graincorp-stem, graincorp-capacity: 0 edges
max depth over 7 documents: 1 edge. No third hop, and no SECOND hop either.
```

**The two writers never meet on any corpus document.** Every chain is either a repair pair or an
admission pair, never stacked — so the walk returns `v1` on its first iteration everywhere, behaving
as precisely the lookup it was written to replace. Its chaining behaviour is exercised by that loop's
synthetic test and by nothing else. With the argument half above, [[R227]] closes: the `seen` guard
defends against nothing the code can reach, and the walk is correct but unexercised in production.

**I2 COULD NOT BE FALSIFIED IN ITS ORIGINAL FORM, AND THAT IS A FINDING ABOUT THE INVARIANT.**
Re-pointed at adoption, *"a claiming region names a table carrying `rdf:type`"* cannot fail: two
producer-side guards enforce it before any test sees the graph — `document.py:1629` (`r.table_uri
is None` → no adoption) and `document.py:1687` (`(grid_uri, RDF.type, TAB.DataGrid) not in
rep_a.graph` → no adoption). Both falsification attempts (nulling `table_uri` at `compile.py:1590`;
deleting `datagrid.py:622-623`) made the page **stop adopting**, so the fixture precondition
collapsed and the tests ERRORED rather than the invariant FAILING. Two wrong mutations in a row
looked like weak attempts; the third measurement showed the subject is unreachable by any mutation.

This is § Producer-side guards vs the membrane **inverted**: the guidance there defends a
producer-side guard against being deleted as a duplicate of the membrane, and here the *test* was
the duplicate of two guards. So I2's subject moved to the guard — **an untyped grid must not be
adopted** — which is falsifiable by deleting `document.py:1687`. I1 keeps its original form and IS
falsified (dropping `tokens_asserted=_admitted_tokens` at `compile.py:1591` fails it with
`tokens_asserted=0` on a region claiming `cells=18`; restored green).

## 3b. The re-baseline, measured — and it is a QUARTER of what the spec's § 1d implied

§ 1d recorded twelve failures. That list was taken **pre-D2** and is stale in BOTH directions:
seven of its twelve are now green (D2 fixed them), and the one that matters most was never on it.
Measured 2026-09-14 in four foreground chunks, after the background runner stalled 14 minutes and
died at exit 144:

```
chunk 1  test_datagrid, test_header_confirmed_refinement, test_read_band_books_every_word
         3 failed, 66 passed, 1 skipped
chunk 2  test_escalation_furnish, test_grid_donation_seam          14 passed
chunk 3  test_run_merge_seam, test_adoption_* (4)                   1 failed, 36 passed
chunk 4  test_membrane_health, test_section_repair,
         test_apple_statement_headers, test_escalation_wiring      42 passed
```

**4 failures, in two categories that must not be conflated.** Three are page-scope fallback-gate
tests on ons p7 whose premise D1 deletes — coverage genuinely lost, recorded as [[R228]]. The
fourth, `test_o3_no_page_loses_asserted_ink_to_a_merge`, is a **live standing detector** for
[[R170]]'s 976 unguarded cells, and D1 merely hands it a second legitimate cause of gain. It was
AMENDED, not retired: a `D1_MOVES` set beside `MERGE_MOVES` pins D1's three movers to their
measured figures — bfs p5 `16 → 180`, ons p7 `0 → 112`, ons p8 `0 → 12`, with 24 of 27 pages
byte-equal. **Deliberately NOT loosened to `>=`**, which is the easy edit and would have blinded
the detector to the hazard it exists for. NB apple p0/p1 look like movers in a naive sweep
(`72 → 172`, `27 → 98`) but are PRE-MERGE pins under forced `merged_run_admissible = False`;
`MERGE_MOVES` already governs them, and adding them to `D1_MOVES` would count one cause twice.

**FALSIFICATION, per CLAUDE.md plan rule 4 — three taken, one graded partial:**

| what | mutation | result |
| --- | --- | --- |
| I1, adoption route | drop `tokens_asserted=_admitted_tokens` (`compile.py:1591`) | **FAILS**: `tokens_asserted=0` on a region claiming `cells=18`; restored green |
| I2 re-scoped to the guard | delete the type clause at `document.py:1687` | **FAILS**: an untyped grid is adopted; restored green |
| O3's `D1_MOVES` pin | ons p7 `112 → 111` | **FAILS** with the amendment's own message; restored green |
| R72's prose half, witness clause | witness moved to ons p4 (asserts 19) | **FAILS** the drift-guard (`assert not page_has_table(p, 4)`); restored green |
| R72's prose half, THE CLAIM | invert the score gate at `compile.py:1616` (`0.0 if page_has_table else 1.0` → reversed) | **FAILS** the claim itself: `assert 0.0 == 1.0, "a prose page has nothing to read and is not a failure"`; restored green |

**The R72 row was graded PARTIAL for one turn, and the upgrade is the point.** The first mutation
failed the *witness-validity* guard, which proves the guard bites but says nothing about the
property beneath it — a test can have a working drift-guard and a claim that cannot fail. Only
inverting the gate exercises `score == 1.0` itself. Recorded because the distinction is easy to
miss and the weaker evidence looked sufficient.

## 4. Unverified or assumed

- **The whole of 5a**, per its grading.
- **The full suite has not been run on either variant.** § 1d's twelve pre-D2 failures are
  unre-checked; at least `test_read_band_books_every_word` and
  `test_fallback_region_books_and_names` (2 errors) still break, measured this loop.
- ~~**ons `chains 3 → 1`** is measured and undiagnosed.~~ **Diagnosed in § 3** — the adopt-scoped
  `table_uri` re-mint. What remains unverified is whether losing those two chains has any
  downstream consequence; nothing here measures that.
- **A background job reported figures for a chain-depth measurement nobody in this session
  launched** (task `b0d1typyi`, claiming `max_depth=1` everywhere). It is not cited above and was
  not built on; `scripts/supersession_chain_depth.py` exists so the question has an instrument whose
  provenance and unit (**edges**, printed beside the node count) are unambiguous.
- **TWO RUNS REPORTED `exit code 0` HAVING EXECUTED NOTHING — a phantom green, in a new dress.**
  `zsh` does **not** word-split unquoted parameter expansions, so `pytest $HALF` handed pytest all
  57 module paths as ONE argument; it matched nothing and exited 0 with `no tests ran in 0.00s`.
  Both halves of the remainder ran this way before it was caught. The repo already has this class
  on record twice — `--timeout=1200` (an unrecognised argument, exit 0, nothing run) and
  `--timeout` again in [[R166]]'s loop — and it recurred here through a different mechanism, which
  is why the remedy has to be structural rather than remembered: **pass file lists through `xargs`
  and run a `--collect-only` smoke check whose number is read before the results are believed.**
  The fixed run collects **439 tests** where the broken one collected 0. A zero-collection run and
  a passing run are indistinguishable by exit code, and this loop also misread a compound
  command's exit code as a test verdict once (chunk 1, which was actually `3 failed, 66 passed`).
  **Read the summary line; never the exit status.**
- **I DIAGNOSED A HEALTHY JOB AS DEAD, AND STATED THE DIAGNOSIS AS CONFIRMED.** The corpus
  witness sweep's output file read **0 bytes** two minutes into a ~4-minute run with no visible
  interpreter, and I called it the handoff's known "heredoc never fed the interpreter" failure,
  killed it, and rewrote it as a file-based script. It had simply been buffering: it completed
  normally and wrote 1310 bytes. **Two real probe failures earlier in the session (a `-e`/`-p`
  flag collision, a pattern that missed the framework interpreter path) primed me to reach for a
  known failure mode instead of waiting one more minute** — and the relaunch then duplicated a
  running sweep, costing CPU the falsification wanted. The lesson is narrow and worth keeping: a
  0-byte output file is evidence about *flushing*, not about liveness, and an unflushed sweep and
  a dead one are indistinguishable by that signal alone.
- **The PID-chaining technique used here has a live trap.** Three processes matched `snap_two.py`
  at once, because a *waiting* job's own command line contains the path it will later run. The
  lowest-PID match happened to be correct; that was luck. Wait on a marker FILE, or capture the PID
  before arming the waiter.
