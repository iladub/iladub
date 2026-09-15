# Handoff — the boxhead measurement was run first, and R234's premise is refuted as stated

**Serves:** prog:criterion:etkl:04 — ONS. The criterion's subject is column identity, which is
exactly what this measurement is about.

**Date:** 2026-09-15. **Tree:** branch `r234-boxhead-measured`, cut from `main` at `05ac7cf`.
**No shipped file was edited. No behaviour changed.**

**Doc impact: none.**

**§ 5 was written FIRST**, per CLAUDE.md § "The handoff's next action is TYPED". This session did
one measurement and wrote it up; it did not approach the originating floor, and no plimslop
override was taken. **No token figure is claimed** — none was measured, and inventing one would be
the defect that rule exists to catch.

---

## 5. The next concrete action

### 5a. ASSERTED — the measurement did NOT abstain, and did NOT confirm. It landed a third way

The order (§ 9 step 1 of `2026-09-15-both-ends-walk-refuted-handoff.md`) anticipated two outcomes:
a split is returned → write the spec; it abstains → hand back. **Neither happened.**

`header_body_split` returns **`2`** on the `(2,1)` band — no abstention, on both `infer_leaf_grid`
and `recover_leaf_grid`, so [[R232]] § 8d's `ncols=1` circularity really is gone at this cut. And
the reader **does** map the boxhead onto 6 columns, minting six leaf labels of which **none is
numeric** — so, unlike the refuted walk, this is **not** a fresh [[R166]] instance.

But it types **2 of the 4** boxhead lines as header. Every spanning label is a wrap fragment —
`Distribution,` for *"Distribution, Hotels and Restaurants"* — and the remaining two boxhead lines
become logical rows 0 and 1 of 27. So [[R234]] as written (*"the header reader cannot map a
4-line, 18-word boxhead onto 6 columns"*) is **refuted**: it maps it, and truncates it.

This is mechanical, not predictive. Every figure is in
`2026-09-15-r234-boxhead-measured-evidence.md` § 1-2, re-runnable from its § 6.

### 5b. ASSERTED — the real blocker is a LOCKOUT, and it is named precisely

```
classify_hierarchical -> HierRegion (not None)
merge_tiling_ok       -> True     => compile.py:1277 `not merge_tiling_ok(...)` is FALSE
                                  => rowrole.build_row_reading IS NEVER ENTERED
assert_hier_region    -> n=0, because region_round_trips -> False  => ROUND_TRIP_FAIL
```

`rowrole.build_row_reading` is the code that composes a wrapped label top-to-bottom — its own
docstring gives that as the worked case (`rowrole.py:85`), and `headers.py:412-420` names that
NEURAL proposer as the designated remedy for wrap-continuation rows. **It cannot fire here**,
because its gate is a *tiling failure* and the truncated tree tiles: centered, non-overlapping,
one leaf per column. Self-consistently wrong.

`merge_tiling_ok` is not misbehaving. It answers *is this tree centered and non-overlapping?* and
the call site reads it as *is this tree the author's header?* Those are different questions.

The band then dies on **2 words of 213**: `Date` and `IoS` sit 6 pt below their four spanning
siblings, so each lands in a header slot **and** in the first body row — violating
`region_round_trips`' exactly-one invariant. The 25×6 table is refused on the vertical placement
of two stub words, and they are ambiguous only *because* the boxhead's last two lines were typed
body in the first place.

### 5c. PROPOSED — the next measurement is why `group_wrapped` absorbed nothing, and it is cheap

**Rests on a reading of one function's behaviour that may not survive contact.** `group_wrapped`
returned **29 cell-rows for 29 lines** — zero absorption — although the documented blocker for its
wrap gate is *absent* here: all three boxhead gaps (1.92, −4.08, 1.92) are well below the band
lead (10.32), where `headers.py`'s KNOWN LIMIT describes failure when the gap *equals or exceeds*
lead (GrainCorp: 6.6 against 6.48). **So the gate's stated condition is satisfied and it still did
not group.** Why is unmeasured.

This matters before any remedy, because it kills the obvious fix: **repairing the split alone
would not work.** With `split=4`, `header_rows_of` keeps rows 0-3 and `_tree_from_rows` takes
row 3 (`Restaurants / Communications / Finances / services`, **4 cells**) as the leaf row — four
labels for six columns, wrong in a new way. The labels are recoverable only by *composing* rows
1-3, which is § 5b's locked-out path.

**Run that first, before any spec:** why does `group_wrapped` emit one cell-row per line on this
band? If its wrap gate is firing but something downstream re-splits, the remedy is in a different
module again, and the next loop should say so rather than build.

### 5d. ASSERTED — the remedy is a § 8 classification and this loop deliberately did not make it

[[R234]]'s row withholds a remedy on purpose, and this loop kept that. Whether the fix belongs in
the split (AXIOM), the grouping (AXIOM), the `merge_tiling_ok` gate at `compile.py:1277`, or a
NEURAL proposal disposed by an oracle is a **CLAUDE.md § 8 classification decision that precedes
code**, and § 5c shows the remedy space is not yet even localised to one module. **A maintainer's
call, not a loop's.**

### 5e. ASSERTED — what this session must NOT be read as having done

No spec, no plan, no code, no shipped instrument, no `cor:reading`. The probes were throwaway and
**not committed** (evidence § 6 carries the re-run recipe). ons still carries no `cor:scoreFloor`,
stays `cor:Unadjudicated`, and its 2026-08-20 HOLD is untouched — nine pages still unread against
the compile, still no contract/terms/shapes. **etkl:04 was not advanced.** The document-scope
figures (`0.7712418301 → 0.7522123894`, region 0 `superseded`, 0 cells) are the PREVIOUS loop's,
inherited unchanged and **not re-derived** here.

---

## 1. Where the primaries are

- **The evidence** — `docs/superpowers/2026-09-15-r234-boxhead-measured-evidence.md`. Every figure
  above is measured there, with the re-run recipe in its § 6 and the non-claims in its § 7.
- **The row** — [[R234]] in `residues-open.md` / `residues.md`, amended today with this result.
- **What was ordered** — `2026-09-15-both-ends-walk-refuted-handoff.md` § 9, on `main` at
  `05ac7cf`.
- **The band** — ons p4 band 0, `page_bands(PDF, 4)[0]`, cut `lines[2:-1]` → 29 lines / 213 words.
  PDF: `corpus/gov-stats/ons-index-of-services-2026-02.pdf` (the corpus is gitignored).
- **The lockout** — `compile.py:1277` (`not merge_tiling_ok`), gating `compile.py:1288`
  (`resolve_header_row_roles`). The composer is `rowrole.build_row_reading`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| `header_body_split` does not abstain at `(2,1)` — it returns 2 | evidence § 1, [[R234]]'s row |
| Six leaf labels, none numeric — NOT a new [[R166]] instance | evidence § 1 |
| [[R234]]'s premise ("cannot map onto 6 columns") is refuted as stated | evidence § 2 |
| The blocker is the NEURAL lockout via `merge_tiling_ok` → True | evidence § 3 |
| The round-trip fails on exactly 2 words (`Date`, `IoS`) | evidence § 4 |
| `group_wrapped` absorbed nothing; fixing the split alone cannot work | evidence § 5 |
| What the remedy is, and which § 8 class it belongs to | **undecided — 5d puts it to the maintainer** |

## 3. Unverified or assumed

- **§ 5c entirely**, per its grading. Nobody has measured why `group_wrapped` emits one row per
  line on this band.
- **Single band, single page, single document.** Whether other documents carry stub labels set
  lower than their spanning siblings (§ 5b's mechanism) or boxheads `group_wrapped` declines to
  absorb (§ 5c) is unmeasured. *A repair measured on one page is a hypothesis about a corpus.*
- **`superseded` is still not explained.** § 5b shows the band escalates on its own; the previous
  loop measured region 0 `superseded` with 0 cells at document scope. Consistent with the adoption
  ledger (`compile.py:1576`), but the link was **not traced** — it was already open in that loop's
  handoff and stays open.
- **Band-in-isolation, not a compile run.** The probes call the real functions on a
  `dataclasses.replace`'d band; nothing was patched into a module global, so the previous loop's
  wrong-seam hazard cannot arise — at the cost that document-scope effects are inherited, not
  re-derived.
- **The two-word round-trip failure was re-derived by replicating the gate**, not by instrumenting
  `region_round_trips` itself. The function's own verdict (`False`) was measured directly; the
  attribution to `Date`/`IoS` reproduces its published logic.

## 4. What this session did

Took § 9's order to measure before building, and ran it. Three things moved:

1. The circularity fear is **settled** — the splitter answers at `(2,1)`.
2. The row's premise is **refuted** — the reader maps 6 columns and truncates, rather than failing.
3. The blocker **relocated**, from "the reader cannot" to "the repair is locked out by an oracle
   that is satisfied by a truncated reading."

**Worth carrying, because it is the technique and not the result.** The ordered question had two
anticipated answers and the true answer was neither. Had this loop reported only *"a split is
returned"* — literally true, and the branch the order treats as "go build" — the next session would
have written a spec against a premise that is false in the same sentence. **A yes/no question
answered `yes` can still refute the claim it was asked in service of**, and the only defence is to
keep measuring one step past the question until the mechanism is visible: here, three steps past —
the labels were truncated, the gate was `True`, the failure was two words.

The previous loop's lesson has a sibling: *a null result is not self-validating*, and **a positive
result is not self-interpreting.**
