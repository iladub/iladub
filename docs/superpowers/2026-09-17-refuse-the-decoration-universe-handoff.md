# Handoff — the decoration universe is refused, blanket; `tab:11` met, R238 closed

**Topic:** The switch ruled on 2026-09-16 is built. bfs p5 carries its row-label and final `%`
columns; `prog:criterion:tab:11` is met; R238 is closed; the cost is recorded as R243.

**Serves:** prog:criterion:tab:11 — the carriage criterion this loop meets

**Date:** 2026-09-17. **Tree:** branch `refuse-the-decoration-universe`, cut from `main` at `6145412`.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. PROPOSED — measure WHY cbh p0 loses four rows ([[R243]]), before anything is built on it

**Typed PROPOSED because the cause is unmeasured and the obvious hypothesis may be wrong.** This
loop measured *that* cbh page 0 loses vessel row 26 and panel totals 42, 63, 74 under the
alignment universe, and deliberately did not ask why — the ruling's mandate was to ship.

The prediction worth registering before it is run: **the four rows fail for ONE shared reason**,
visible in `grid.refusals`, most likely an R3 straddle or the two-runs-in-one-column refusal in
`place`. If that holds, R243 is one defect with four symptoms and has a single remedy; if the
four carry different reasons, it is four defects and the row should be split.

**The probe is one command and refutes the prediction in minutes:**

```
./.venv/bin/python -c "
import sys; sys.path.insert(0,'src')
from iladub.etkl.datagrid import derive_data_grid
g = derive_data_grid('corpus/ag-trade/cbh-stem-2026-08-03.pdf', 0)
print({i: g.refusals.get(i) for i in (26, 42, 63, 74)})"
```

Run it FIRST. A day of remedy design on a wrong shared-cause assumption is the cost of not
running it, and the oracles already pin the ids (`missed == [26]`, `missed == [42, 63, 74]`) so
any recovery fails a test rather than landing silently.

### 5b. ASSERTED — what is mechanically finished and must not be redone

- **Do not re-measure whether the switch is free.** PR #239 ran that gate and this loop shipped
  it: +92 cells, +1103 triples, zero score movement, six documents byte-identical.
- **Do not judge carriage work on the document score** — [[R240]]. Cells and triples.
- **Do not re-open the blanket-vs-conditional question** without a *new document*. The straddle
  discriminator is refuted 48/48 for structural reasons; the corpus cannot falsify the refusal.
- **Do not build the M4 carve-out yet** ([[R244]]) — deferred by the maintainer precisely because
  it now has zero live subjects.

### 5c. PROPOSED — [[R241]] is the sharper question and this loop made it sharper

bfs p5's single 12-column grid spans two tables, so a column index means different things by row
class. This loop moved 92 cells into that grid without saying anything about what its columns
*mean*. Typed PROPOSED: it is a measurement whose shape is not yet known.

---

## 1. Where the primaries are

- **The ruling** — `2026-09-16-ship-the-switch-ruling.md`.
- **This loop's evidence** — `2026-09-17-refuse-the-decoration-universe-evidence.md`. § 2 is the
  G0 seam measurement, § 4 the cbh cost, § 5 the citation collateral, § 8 what is NOT established.
- **The switch** — `derive_data_grid` in `src/iladub/etkl/datagrid.py`; the selection site records
  why `_boundaries_from_decoration` is retained but never called.
- **The oracle** — `tests/test_carriage.py`.
  `./.venv/bin/python -m pytest -m corpus tests/test_carriage.py -q` (it SKIPS in CI).
- **The rows** — [[R238]] closed in `residues-closed.md`; [[R243]] and [[R244]] open.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| Refuse blanket; retain `_boundaries_from_decoration` uncalled, for the revisit case | evidence § 1; the selection site |
| Remove the G0 occupancy arm, measured unreachable (3 pages → 0) | evidence § 2 |
| cbh's 5-row cost is pinned by id, never relaxed | evidence § 4; the four re-authored oracles |
| `metOn` is the day the switch landed, not the day it was ruled | `tab:11`'s prose header |
| The M4 carve-out is deferred, not refused | [[R244]] |
| cbh's leak stopping does NOT close R74 | evidence § 8; the leak test's docstring |

## 3. Unverified or assumed

- **The cause of cbh's four lost rows** — unmeasured; § 5a is the probe.
- **Whether alignment's 12 columns are the RIGHT 12** — untouched ([[R241]]).
- **A correctly-drawn decoration rectangle would be regressed** and this corpus cannot detect it.
- The `docs/wiki/concepts/data-grid.md` rewrite is synthesis, not re-derived from the code.

## 4. What this session did, and what it cost

Measured the G0 seam, shipped the switch, watched the strict xfail XPASS and flipped it with
`prog:met` in one act, re-authored four cbh oracles to the measured reading, repaired nine
citations the lint cannot see, closed R238 and raised R243/R244.

**The cost worth carrying: the lint's silence is not evidence, and arithmetic is not measurement.**
Two findings, both about *how* the loop was checked:

1. **A +19 line shift silently falsified nine cross-file citations, and every gate stayed green.**
   `test_source_citations.py` refuses only downward same-file citations; cross-file anchors are
   kept silent by the EOF filter *by design*. CLAUDE.md plan rule 7 warns about the downward
   same-file class — this is its blind twin, and nothing in the suite sees it. **Any edit that
   inserts lines high in a large module must re-locate every inbound `file:line` anchor.**
2. **The shift was not what counting the diff said it was.** +14/+18 by arithmetic matched
   *nothing*; the true shift was +19/+22. Relocate by exact full-line content match, never by
   counting added lines.

A third, smaller: **`assert g.universe == "decoration"` looked like the whole blast radius and was
the smallest part of it.** Reading a test's assertion tells you what it claims; only running it
tells you what it protects.
