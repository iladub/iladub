# Handoff — `R154` is closed: a boundary that cuts ink is not a boundary

**Topic:** `R154`, executed from `docs/superpowers/specs/2026-08-31-a-boundary-that-cuts-ink-design.md`.
The predecessor handoff graded this **PROPOSED** and ordered the prediction be RUN first; it was, and
that is the only reason the row's central framing was caught as wrong. `geometry._row_dividers` is
new: an interior ruled boundary divides a row only where the ink on both sides clears it. WHO's
shredded header goes `['Z-s','c','o','res (weight','i','n','kg)']` → `['Z-scores (weight in','kg)']`
with its real header row byte-identical. Branch `r154-a-boundary-that-cuts-ink-is-not-a-boundary`.

Part 5 is written first, per `CLAUDE.md` § "The handoff's next action is TYPED".

## 5. The next concrete action — TYPED

### PROPOSED — `R155`, and it is the direct successor this loop created

`R155`'s row (`docs/superpowers/residues-open.md`) is the primary; **open it, do not plan against
this paragraph.** WHO's header line still divides once, at `b=594.35`, between `in` and `kg)`. That
is a **word gap**, not a mid-word cut, and this loop's predicate provably cannot reach it: at
character level a word gap and a column gutter are the same picture.

**Graded PROPOSED, and what must be run before anything is built:** the row prescribes consulting
`extract_words`' runs *only at boundaries `_row_dividers` has already honoured*. **That population
was never enumerated** — this loop measured it as exactly one on WHO's header line and nowhere else,
for no document. Enumerate it first, on all seven. If it is large, the fix is not the narrow one the
row imagines, and the trap the row names applies: WHO's twelve real data columns are separated by
gaps geometrically indistinguishable from this one, so a merge-across-word-gaps rule re-creates the
exact failure `R154` avoided.

### ASSERTED — what is measured, and the four things it does NOT license

- **The two-population framing in `R154`'s own row is REFUTED.** It reads its census as
  cbh/ons/bfs/gstem being *"100% genuine spanners"* against apple/who *"sub-point overhang"*, and
  asks for a discriminator between them. Sampling the sets shows **one** phenomenon in both — a text
  run drawn across the grid and chopped (`'GERALDTO'|'N'`, `'1TheIOSo'|'utputisdesigna'`,
  `'ThreeMo'|'nthsEndedNineM'`, `'Z-s'|'cores(weightin'`). No discriminator was needed.
- **Fidelity, the actual result.** `page_bands(who,0)[2]` line 0: 7 fragments → 2. Line 1
  (`'Year: Month','Month','L','M','S','-3 SD',…,'3 SD'`) **byte-identical** — the failure mode
  `R154`'s row warned the coarse word swap causes (`'-3 SD'` → `'-3'`,`'SD'`) does not occur.
- **Corpus, both modes, `validate_shapes=False`, DOCUMENT scope:** gstem `0.9654553611→0.9658886894`,
  gcap `1.0→1.0`, cbh `0.9046563192→0.9091940976`, apple `0.3556034482→0.3586956521`,
  bfs `0.3438438438→0.3464447806`, ons unchanged, **who unchanged at `0.9095966620305981`**. Every
  escalation reason counter unchanged **at that scope**.
- **AND NOT AT PAGE SCOPE — this corrects a claim first written here without its scope.**
  `compile_tables(cbh, 0)` baseline vs. fix: score `0.06984126984126984 → 0.05711086226203808`,
  asserted `66 → 51`, regions 1/3/5/7 reason `MERGE_AMBIGUOUS → REGION_TILING_FAILED`. Document scope
  hides it because `document.py`'s driver runs a pass-2 repair. **"Nothing regresses" is a
  document-scope statement only.** `R156`(b).
- **Do NOT cite the score rises as the justification.** All four are partly a **denominator** effect:
  welding two chopped fragments removes an ink token (cbh `asserted+escalated` 902 → 881). A smaller
  denominator is not better reading. **The oracle is two-sided and NEGATIVE — nothing regresses.**
- **Do NOT treat `graincorp-stem` as evidence.** `flush=1`; it is a near-vacuous PASS row, exactly
  the near-inertness `R154`'s row predicted. The load-bearing negative evidence is **cbh (53),
  apple (25), ons (20)**.
- **This does not make WHO's carried table faithful.** It repairs one measured defect in what is
  carried. Nobody has read WHO's table against the published PDF — still true, and `R155` guarantees
  the top-level labels are still split.
- **No new constant.** `COORD_EPS` only, already justified in `ruledroles._within` as *"NOT a
  clearance threshold … only a non-zero one."* **The AXIOM/PROCEDURAL classification is the spec's
  argument (§4), NOT ratified by the maintainer.**

### ASSERTED — the unit suite is GREEN, and three pinned baselines moved

`./.venv/bin/python -m pytest -m "not corpus" -q` on the first commit of this branch:
**`3 failed, 1382 passed, 7 skipped, 46 deselected, 1 xfailed in 1371.83s`**. All three failures
were pinned baselines, each re-based WITH its measurement recorded in the test itself, never
silently:

- `test_kind_gate_is_load_bearing` key `(0,2)`: header word count `2 → 1`. gstem's **entire** flush
  population is one crossing and this is it — the date `'Friday, 31 July 2026'`, chopped into
  `'Friday, 31' // 'July 2026'` at a boundary whose right-hand ink begins 0.353pt **before** it. The
  weld is the repair. The test's own diagnosis (*"a 1-2 word line spanning 17 columns"*) is unchanged.
- `test_decisionlog`: apple page-0 pinned score `0.1170 → 0.1198`. A **denominator** effect; the
  docstring now says so and points at the closure row.
- `test_typing_equiv[cbh]`: band 9 kind `UNSUPPORTED_TABLE → RECORD_TABLE`. **This one is NOT
  certified** — see `R156`(a) and the next bullet.

### PROPOSED — `R156`(a), and it is the one thing here I would not ship unexamined

cbh page-0 band 9 now asserts `RECORD_TABLE` where it asserted `UNSUPPORTED_TABLE`, on a band whose
header row is `'PORT','WHEAT','MAIN WHEAT GRADES','BARLEY','CANOLA','OTHER','TOTAL'` **followed by
`'ALB','1 - 15 October'`** — the header of a SECOND, side-by-side table. One grid, two tables.

**The conflation is pre-existing and this loop did not cause it**: the band's data lines 1-5 are
byte-identical before and after, and only the kind label moved — welding the chopped *title* row
made the band read as records. So refusing this loop would not fix it. **But the claim is stronger
than it was, over a grid that cannot support it, and that is a §7 question the loop's own tiling
oracle cannot answer** — tiling certifies consistency, not fidelity. Open `R156` before treating
this branch as safe to build on.

### PROPOSED — blocked on rulings, unchanged and NOT re-derived

`R132`, `R127`, `R131`(b). Open `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5.

## 1. Goal

Close `R154`: stop the ruled re-extraction shredding a header label mid-word, without breaking what
the ruled reading gets right, and without a tuned constant.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `src/iladub/etkl/geometry.py` (`_row_dividers`) | **THE CHANGE.** The predicate, and its docstring's argument for why row-locality is load-bearing |
| `src/iladub/etkl/geometry.py` (`rule_aware_lines`) | The one call into it, per row; docstring amended |
| `src/iladub/etkl/ruledroles.py:112-129` (`_within`) | The prior art the predicate is taken from — read its docstring, it carries the justification this change did not restate |
| `tests/etkl/test_boundary_cuts_ink.py` | The four oracles, incl. row-locality and the 0.03pt sub-point case |
| `docs/superpowers/specs/2026-08-31-a-boundary-that-cuts-ink-design.md` | The contract. §3.2 (the refutation), §3.4 (the residual's clearances), §8 (what is not done) are the live parts |
| `docs/superpowers/residues-closed.md`, `~~R154~~` | The closure row and the five things it does not license |
| `docs/superpowers/residues-open.md`, `R155` | The successor, with the full clearance table |
| `src/iladub/etkl/gridregion.py` | A comment saying `rule_aware_lines` *"keeps using every rule x"*, annotated (it still RECEIVES every rule x) |

## 3. What was decided, and where that decision is recorded

- **The predicate is `_within`'s, moved one stage earlier.** Recorded in `_row_dividers`' docstring
  and spec §3.1. Reversible.
- **The decision is ROW-LOCAL, not global.** This is the whole separation from the word-atomicity
  variant `R154` records as measured to fail. Recorded in the docstring, spec §2 and §3.5.
- **Classified PROCEDURAL** — a modification inside an existing justified PROCEDURAL step (raw
  extraction), held to that step's own stated standard of *"no tuned constant."* Recorded in spec §4
  **and nowhere else; not ratified.**
- **`R155` raised rather than solved.** Recorded in the register and spec §10.

## 4. Unverified or assumed

- **`ruledroles._within`'s behaviour on a WELDED banner is reasoned, not measured.** The reasoning:
  a welded banner is one wide cell reaching across boundaries, so `_within` returns False in every
  column — the same answer it gave each chopped piece. cbh (the banner-heavy document) does not
  regress, but that is corpus evidence, not a read of the function under the new input.
- The `flush` counts differ from `R154`'s census on three documents (cbh 53/49, bfs 6/7, who
  139/129). Attributed to row bucketing; **not run to ground.**
- **Whether the second call site (`compile.py:193`, re-bucketing on `col_xs`) contributes any of the
  score movement, or whether all of it comes from the first, is not separated.**
- **A COST was measured and not investigated.** `_row_dividers` is O(rows x boundaries x chars) and
  the battery's wall times rose: gstem `155s → 161s`, cbh `23s → 26s`, who `36s → 40s`, apple/bfs/ons/
  gcap flat. ~4-11% on the three slowest documents, from one run each with no repeats and the two
  modes run back to back in one process, so it is **not** a controlled measurement. It touches the
  still-open perf residue `R39`; nothing was done about it here.
- The spec's §3.2/§3.4 figures were produced by a monkeypatched copy of `rule_aware_lines`, then the
  shipped function was written to match. Spec §5 names re-deriving them against the edited source as
  the implementer's seam. **The FIDELITY half is now re-derived and reproduces exactly** — against
  the shipped function, `page_bands(who,0)` band 2 gives line 0 `['Z-scores (weight in','kg)']` and
  line 1 `['Year: Month','Month','L','M','S','-3 SD','-2 SD','-1 SD','Median','1 SD','2 SD','3 SD']`.
  **The §3.3 corpus battery has NOT been re-run against the shipped source** — those seven score
  lines are still the monkeypatched figures. CI is not a check on this: no test pins them.
- No `plimslop` working-token figure exists for this session — `preflight` reported *"unmeasured, no
  turn recorded for this project."* The shape was logged as *originating*.
