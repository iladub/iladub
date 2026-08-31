# Handoff — both of the last handoff's propositions refuted, and the WHO subject relocated by measurement

**Topic:** the loop `2026-08-31-refocus-on-etkl-handoff.md` § 5 proposed was RUN as four throwaway
spikes and **does not close `R45`**. Its measurement (§ 2.5, the manufactured fragments) is
reproduced and stands; the **inference drawn from it is false**. The real subject is
`infer_column_tree_by_proximity` — the function that handoff explicitly told the next session not
to open. Measured today at `3f3ed4e`. No repo file was changed by any spike.

Part 5 is written first, per CLAUDE.md § "The handoff's next action is TYPED".

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, outcome known, ~10 minutes each

**Reproduce these before designing anything.** Every figure below was measured this session and is
pinned here; do not take this file's word for any of it.

1. **The predecessor's §§ 2.2-2.5 all reproduce exactly** — score `0.5597`, `{MATRIX_AMBIGUOUS: 3}`,
   `classify_matrix` returning `ncols=12` on all three bands, `tab:UnambiguousAccessShape` as the
   sole refusing shape, leaf-header counts `{1:2,2:2,3:2,4:1,5:1,6:1,7:1,8:2,9:2,10:2,11:2}`, the
   14-node tree node-for-node, and `extract_words` page 0 giving
   `'Z-scores' // '(weight' // 'in' // 'kg)'`.
2. **The chop is worse than §2.5 recorded, and its mechanism is different.** The band carries **48**
   raw rule x's in quads (`125.51, 130.19, 130.91, 136.31` — twin edges, width 10.80pt), and
   `rule_aware_lines` (`geometry.py:263`, the actual cutting code) buckets **per character by
   centre** across all 48. The header becomes **seven** fragments, not three:
   `'Z-s' // 'c' // 'o' // 'res (weight' // 'i' // 'n' // 'kg)'`. Note `'res (weight'` is the tail of
   one word joined to the head of the next — **chop and merge interleave, so no downstream weld can
   recover the runs.**

### ASSERTED — BOTH of the predecessor's propositions are REFUTED

**(a) "Word-atomicity alone makes WHO tile" — FALSE.** Three spike variants (ink-extent split test,
char-centre split test, minimal-lift) give byte-identical results:

```
baseline     0.5597  {MATRIX_AMBIGUOUS: 3}
word-atomic  0.5662  {ROUND_TRIP_FAIL: 3}   no MatrixRegion produced at all
```

The invariant does exactly what it was designed to do — the header returns as
`'Z-scores' // '(weight' // 'in' // 'kg)'` — and the document still refuses. Instrumented inside the
band: `header_body_split` drops from ≥2 to **1**, so the header region collapses to one line,
`confirmed_boundaries` sees 20 glyphs and confirms **0**, `_build_ruled_band` takes its
`if not confirmed: return band` exit (`compile.py:190-191`), the second re-extraction at `:193` never
runs, `column_xs` is `()` against a baseline of 49, and `classify_matrix` refuses at its `split >= 2`
gate. **`infer_column_tree_by_proximity` never executes at all** under this change.

**(b) "The subject is `_build_ruled_band`, NOT `matrix.py`" — FALSE, and this is the load-bearing
refutation.** Spike 4 implemented the maintainer's chosen design (leave `rule_aware_lines` alone;
read the header region from the word-based `sub.lines`, keep the ruled cells for the body). The
labels come out perfect. **The tree is structurally identical:**

```
node   baseline text   after the swap   covers
ch0    'Z-s'           'Z-scores'       [1,2,3,4,5,6,7]   unchanged
ch6    'S'             'S'              [4,5,6,7,8,9,10,11]  unchanged
ch7    '-3 SD'         '-3'             [1,2,3,4,5]       unchanged
```

Every `covers` tuple and every `parent` link identical; `ch6`/`ch7` still parentless; the same shape
still refuses on all three bands; score `0.5597 → 0.5514`, slightly **worse**.

**The manufactured fragments were never the cause.** Fix the extraction perfectly and the region
refuses in exactly the same way, for exactly the same reason.

**A second finding from the same spike, and it kills the "use each reading where it is right"
design as stated:** the swap breaks what the ruled extraction was getting *right* — `'-3 SD'` becomes
`'-3'` and `'SD'`, because pdfplumber reads them as two words. **The header needs both readings at
once**: word runs to keep `Z-scores` whole, ruled cells to keep `-3 SD` together. Neither alone is
correct for a header line, and that is a harder problem than either handoff supposed.

### ASSERTED — the corpus-wide blast radius, measured (the predecessor left this UNMEASURED)

Every corpus PDF, every page; band scope reproduces `page_bands`' per-band rule filter
(`compile.py:309`) exactly, because page scope overstates by up to 30x.

| document | crossing words (band scope) | of | character |
|---|---|---|---|
| **graincorp-stem** (0.9655, the one that passes) | **1** | 2845 | `'July'`, rule 0.35pt inside |
| graincorp-capacity | 0 | 496 | — |
| bfs | 7 | 1497 | 100% genuine spanners |
| ons | 20 | 1305 | 100% genuine spanners |
| cbh | 49 | 1234 | 100% genuine spanners |
| apple | 25 | 678 | 23 sub-point overhang (0.20pt) |
| who | 129 | 349 | 126 sub-point overhang (0.03pt) |

Two clean populations. Clustering is a **per-document property, not universal** — `ons` has zero
(all 18 clusters single x's, width 0.00), WHO is a different phenomenon (106 distinct x's on page 0;
6 of its 36 clusters exceed 12pt, and no other document has one). **Any design depending on a
cluster-grouping constant is therefore both a §8 violation and empirically unsound.**

### PROPOSED — the loop, and it must be scoped fresh

**The subject is `infer_column_tree_by_proximity` (`src/iladub/etkl/matrix.py:39`)** — nearest-parent-
centre (Voronoi) assignment. `'S'`, a one-character label centred over its own column, is the nearest
centre for columns 4-11 and absorbs all eight; `'-3'` absorbs 1-5. Strict-subset parent linking then
leaves `ch6` and `ch7` parentless, so two levels are simultaneously leaves over the same columns —
which is precisely what `tab:UnambiguousAccessShape` refuses. **This is independent of how the text
was extracted**, which is what spike 4 proves.

**The question to settle BEFORE designing, and it is genuinely open:** is *"which columns does this
header label span"* determined by the evidence, or underdetermined? CLAUDE.md §8 routes it to NEURAL
by wording. The predecessor argued AXIOM and the maintainer ratified that — **but that argument was
made about the dead subject (never splitting a word run), not this one.** It does not transfer:
consuming `extract_words`' existing run assertion needs no judgement, whereas assigning a centred
1-character label over a sparse 8-column group may. **Do not inherit the AXIOM ruling; re-argue it
against this subject.**

**The `< 0.5` level-grouping tolerance in the same function is now implicated** — the predecessor
noted it as a standing §8 smell that "no measurement here implicates". This session's measurement
moves the subject onto that function, so it is in scope rather than beside it.

**The success oracle stays TWO-SIDED.** WHO tiling is not success if `graincorp-stem` (0.9655 against
a pinned 0.95 floor) regresses. The full corpus battery has not run in six loops now.

**Deliberately out of scope:** the extraction defect itself, now recorded as **R154** — it is real,
measured, and NOT the WHO blocker, so fixing it closes nothing on `R45`.

### PROPOSED — blocked on rulings, unchanged and NOT re-derived

`R132`, `R127`, `R131`(b). Open `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5.

## 1. Goal

Discharge the predecessor's § 5 by running its own falsifications before building on them, and
relocate the WHO subject to wherever the measurement puts it.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `src/iladub/etkl/matrix.py:39` (`infer_column_tree_by_proximity`) | **THE SUBJECT.** Nearest-centre assignment + the `< 0.5` level grouping + strict-subset parent linking. The module docstring states the centred-merge assumption the WHO header violates |
| `src/iladub/etkl/geometry.py:263` (`rule_aware_lines`) | The per-char-centre bucketing that manufactures the fragments. Both its call sites (`compile.py:133`, `:193`) are inside `_build_ruled_band` (73-197). Subject of R154, **not** of the WHO loop |
| `src/iladub/etkl/compile.py:190-193` | The `if not confirmed: return band` exit and the second re-extraction. The cascade that swallowed spikes 1-3 |
| `vocab/queries/confirm-boundary.rq` | The boundary AXIOM. Its third clause refuses a boundary any header glyph straddles — read it before touching header extraction |
| `vocab/shapes/tab-shapes.ttl:127` | `tab:UnambiguousAccessShape` — the shape that refuses, correctly, on all three bands |
| `tests/etkl/fixtures.py:875` + `tests/etkl/test_header_stack.py:214` | `spanner_with_space_ruled_pdf(chop_mid_word=True)` — an existing adversarial fixture where a rule falls inside a word. Pinned as an **A/B** against a hook-disabled base run, not a snapshot, so it tolerates upstream change better than it first appears |
| `docs/superpowers/residues-open.md`, `R45` / `R154` | `R45` is the WHO blocker; `R154` is this session's extraction finding |

## 3. What was decided, and where that decision is recorded

- **The §8 classification for the word-atomicity invariant was ruled AXIOM by the maintainer** this
  session. Recorded **here only; reversible** — and § 5 above records why it must **not** be
  inherited by the relocated subject.
- **The "use each extraction where it is right" design was chosen by the maintainer and then refuted
  by measurement** (spike 4) before any spec was written. Recorded **here only.**
- **The subject moved from `_build_ruled_band` to `infer_column_tree_by_proximity`**, reversing the
  predecessor's § 5. Recorded here and in this branch's PR; **nowhere else; reversible.**
- **No spec was written, deliberately.** The design the session was authorised to spec was refuted
  by its own falsification. Recorded here.
- **R154 raised** for the extraction defect — `docs/superpowers/residues.md` + `residues-open.md`.

## 4. Unverified or assumed

- **The full corpus battery was NOT run** — unchanged for six loops. Only WHO was compiled
  repeatedly; the other six carry 2026-08-20 figures nobody has reproduced.
- **The `-m "not corpus"` suite was NOT run.** No repo file was changed, so nothing is claimed
  about it. `git status` was clean throughout; all four spikes were monkeypatches in the scratchpad.
- **Whether ANY tolerance-free rule produces the correct `covers` for the WHO header is UNKNOWN.**
  It is § 5's open question, not a result. Nothing here shows the tree defect is fixable as AXIOM.
- **The apple tree was never dumped.** Whether its 2 `MATRIX_AMBIGUOUS` share WHO's mechanism is
  still unknown, six loops on.
- **Spike 4's swap was applied at the whole-header granularity** (replace header lines wholesale by
  top-match). A finer variant — per-word, only where the ruled reading splits a run — was not tried
  and could behave differently. The structural-identity result is what matters and would not change,
  but the `'-3 SD'` regression specifically is an artefact of the coarse granularity.
- **`header_body_split`'s reason for returning 1 under word-atomicity was not opened.** It is
  reported as measured behaviour, not explained.
- **The ~50k working-token figure this session stopped at is an ESTIMATE** — no status-line
  measurement was available, and `plimslop preflight` reported "unmeasured, no turn recorded for
  this project" on both calls. The floor decision rests on that estimate.
