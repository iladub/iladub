# Handoff — the arc can see carriage: `tab:11` authored, `met false`, blocked by R238

**Topic:** The criterion ruled on 2026-09-16 is authored and its oracle ships RED-on-purpose. The
arc now has one criterion whose oracle is **cells and triples**, not score. Nothing was built.

**Serves:** prog:criterion:tab:11.

**Date:** 2026-09-16. **Tree:** branch `the-arc-can-see-carriage`, cut from `main` at `e394c34`.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — BUILD the blanket refusal; the criterion is now waiting for it

Mechanical, and the outcome is known because PR #239 already compiled exactly this configuration
across all seven documents. Refuse `_boundaries_from_decoration` **blanket** at
`src/iladub/etkl/datagrid.py:340-349`, per `2026-09-16-ship-the-switch-ruling.md`. The oracle is
already in the tree and already pins the answer: **bfs p5 → 496 cells, document → 15354 triples,
p6 unmoved at 267 across 6 asserted regions, the other six documents byte-identical.**

**The build is not finished until three things move in ONE commit:** the switch; the
`strict=True` marker on `test_bfs_p5_carries_the_row_label_and_percent_columns`; and
`prog:criterion:tab:11`'s `prog:met false` → `true` with a `prog:metOn`. The suite will force
this — an XPASS under a strict marker is a failure, so the tree cannot go green with the switch
shipped and the criterion stale. **M2 requires `metOn` when `met true`; M8 refuses a met criterion
that is still blocked, so [[R238]] must be struck in the same act.**

### 5b. PROPOSED — the G0 branch and `test_datagrid.py:1298` are where this will bite

**Typed PROPOSED because it is READ, not RUN** — I did not execute `test_datagrid.py`, and the
ruling's own rule 3 says name the seam, not the answer:

- **`datagrid.py:428-431`** branches on `if universe == "decoration":` for G0
  `tab:SeedFollowsUniverse`, and its comment records that seeding a decoration universe by
  signature *"cost capacity 19"*. A blanket refusal appears to make that branch **unreachable**.
  MEASURE it before deleting or stranding it.
- **`tests/etkl/test_datagrid.py:1298`** reads `assert g is not None and g.universe == "decoration"`
  — the cbh fifth oracle, explicitly *"a DECORATION-universe page"*. If the refusal is blanket,
  **this test states something that can no longer be true**, and that is a test to re-author with
  its reason recorded, not to quietly weaken. It is the most likely red in the build loop.
- Other readers of `DataGrid.universe`, measured by grep: emission at `datagrid.py:588` and
  `:625-626` (`tab:DecorationUniverse` / `tab:AlignmentUniverse`), and
  `test_datagrid.py:227,553`, `test_domain_range_agreement.py:51` which construct or assert
  `"alignment"`. **Producer-side guards are not deleted for looking redundant** (CLAUDE.md
  § Producer-side guards vs the membrane; [[R102]]).

### 5c. ASSERTED — what NOT to do

- **Do not re-measure whether the switch is free.** PR #239 ran that gate: +92 cells, +1103
  triples, zero score movement, six documents byte-identical. Re-running it is a second loop of a
  closed question.
- **Do not judge the build on the document score** — [[R240]]. Cells and triples.
- **Do not author a conditional/per-page scope.** PR #238 refuted the straddle discriminator 48/48
  for structural reasons; inventing a fresh one is the tuned constant CLAUDE.md § 8 forbids.
- **Do not treat green CI as evidence about `tests/test_carriage.py`** — it SKIPS there.
  Run `-m corpus` by hand.

---

## 1. Where the primaries are

- **The ruling** — `2026-09-16-ship-the-switch-ruling.md`; `:144` is `tab:11`'s `prog:source`.
- **This loop's evidence** — `2026-09-16-the-arc-can-see-carriage-evidence.md`. § 3 is the measured
  reading of the current tree; § 4 is the falsification; § 6 is what it does not establish.
- **The criterion** — `tests/arc-manifest.ttl`, the `tab:11` block at the foot of the `tab`
  section, with a prose header recording why `tab` and not `etkl`.
- **The oracle** — `tests/test_carriage.py`.
  `./.venv/bin/python -m pytest -m corpus tests/test_carriage.py -q -rxX`
- **The row** — [[R238]] (`residues-open.md`, appended; index line updated).

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The criterion goes on `tab`, not `etkl` — **forced** by the etkl↔corpus bijection | evidence § 2 |
| R238 blocks `tab:11`; R238 is NOT added to `etkl:05` | ruling § 2nd; evidence § 2 |
| Oracle is cells + triples, never score | `tab:11` `prog:statement`; [[R240]] |
| p5's 404 cells sit in ONE asserted region; p6 is a free control at 267/6 | evidence § 3 |
| The p5 test ships as a **strict xfail** so the build must flip it | evidence § 4 |
| Closing R238 and meeting `tab:11` are the same act | [[R238]] row, appended |

## 3. Unverified or assumed

- **§ 5b is read, not run** — the G0 branch and `test_datagrid.py:1298`.
- **Whether alignment's 12 columns are the RIGHT 12** — untouched ([[R241]]).
- **The corpus cannot falsify a blanket refusal** — no page here has a decoration rectangle that is
  both adopted and correct. Accepted on the record by the ruling.
- **[[R242]]** (footnote markers fusing into the label cell) is deferred and not a blocker.

## 4. What this session did, and what it cost

Read the ruling, measured the tree, authored one criterion and one oracle, regenerated the
landscape cache, updated the register. Four gate suites run green; the oracle falsified both ways
and restored.

**The cost worth carrying: the rung was nearly chosen by taste.** The natural-looking home for a
bfs carriage criterion is the `etkl` rung, where bfs already lives as `etkl:05` — and that is
wrong, because `test_etkl_criteria_agree_with_the_corpus_manifest` puts that rung in bijection with
the corpus register, so the criterion would have gone red on arrival. **The manifest's own test
answered a design question I was about to answer from intuition**, which is the same shape as the
ruling's other half: an edge that looked obviously right (R238 → `etkl:05`) was refused by the
rung's own stated rule and by a measurement already in hand.
