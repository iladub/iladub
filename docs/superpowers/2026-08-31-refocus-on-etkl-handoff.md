# Handoff — the refocus on etkl, and the WHO matrix header measured to its root

**Topic:** why the last three weeks moved the repo's governance and not its compiler, which corpus
document is the smallest slice back onto the product, and the diagnosis of that document's single
defect — measured today at `b5f395b`, and **refuting the reading this session opened with**.

Part 5 is written first, per CLAUDE.md § "The handoff's next action is TYPED".

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, outcome known

**Reproduce the diagnosis in § 2 before designing anything.** The four commands are recorded there
and each takes ~2 minutes on a warm venv. Their outcomes are known and pinned: score `0.5597`; one
refusing shape (`tab:UnambiguousAccessShape`) on all three bands; 7 of 11 leaf columns carrying
`n=2` leaf headers; and the 14-node column tree printed in § 2.4. Nothing here needs deciding — it
needs re-running, because a fresh session must not build on this file's word for it.

### PROPOSED — rests on a prediction that must be RUN before anything is built on it

**The remedy is NOT yet known, and the obvious one may be wrong.** This session's opening read —
"`infer_column_tree_by_proximity` assumes centred merges, so the fix is a NEURAL proposer at the
column-tree seam" — was **measured and refuted**: `classify_matrix` succeeds on all three WHO bands,
so the proximity tree is built, not refused. The refusal is one step later, at the tiling oracle.

That leaves **two candidate root causes, and they prescribe opposite loops**:

- **(a) The column tree is the defect.** Nearest-centre assignment hands the last label on a line
  every trailing column (`S` → cols 4-11) and strict-subset parent linking (`matrix.py:69`,
  `set(nd.covers) <= set(m.covers)`) then finds no parent, so two levels both stay leaves. Remedy:
  a NEURAL span proposer under CLAUDE.md §8, disposed by the tiling oracle that already exists.
- **(b) The grid is the defect, and the tree is a symptom.** The level-0 label
  `Z-scores (weight in kg)` arrives as **three** pseudo-labels — `"Z-s"`, `"res (weight"`, `"kg)"`.
  Those cut points look like `recover_leaf_grid` column boundaries slicing a wide centred label,
  not like three text runs the PDF actually contains. If so, a NEURAL proposer at the tree seam
  would be papering over a grid defect one layer down, and the loop to run is a different one.

**Falsify (b) FIRST — it is cheap and it decides which loop exists.** Extract the raw word runs of
the WHO header line straight from the PDF (bypassing `recover_leaf_grid`) and ask whether
`Z-scores (weight in kg)` is one run or three. One run ⇒ (b) holds, the grid is the subject. Three
runs ⇒ (b) is dead and (a) is the subject. *Budget for refutation; this session already spent one
premise that way, which is the argument for spending another.*

### PROPOSED — the loop's shape, contingent on the above

Whichever branch survives, the loop is a **reading loop on one document** (`R45`, arc `tab:05`) and
its oracle already exists and already works — `tab:UnambiguousAccessShape` refuses correctly today.
That is the unusual and favourable part: **what disposes is built and independent of whatever will
propose.** Do not rebuild it.

## 1. Goal

Refocus from repo governance back onto the compiler, on the smallest corpus slice that closes end
to end.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `tests/corpus-manifest.ttl` | The 7-document verdict register and the 2026-08-20 adjudications. **1 of 7 is accepted** (`graincorp-stem`, 0.9655, floor 0.95); the other six are dated HOLDs whose rationales name the defects |
| `docs/superpowers/arc-dependency-landscape.md` | The generated arc cache. 21 criteria ready today; `tab:05` is the sole dependency of `etkl:07` and one of three for `etkl:06` |
| `tests/arc-manifest.ttl` | 43 criteria, **18 met**, last met `2026-08-25` (`grep -oE 'prog:metOn "[0-9-]+"' | sort | tail -1`) |
| `docs/superpowers/residues-open.md`, `R45` | The row already prescribes this loop: *"whether it needs a NEURAL-disposed clause or a tiling-oracle extension"* |
| `src/iladub/etkl/matrix.py` | 127 lines. `infer_column_tree_by_proximity:39` (the proposer), `classify_matrix:101` (the chain), and the docstring's stated assumption |
| `src/iladub/etkl/tiling.py` | `region_tiles` — the 13-shape SHACL gate that refuses. PROCEDURAL glue over AXIOM shapes |
| `vocab/shapes/tab-shapes.ttl:127` | `tab:UnambiguousAccessShape` — "exactly one leaf header per column". The shape that fires |
| `src/iladub/etkl/compile.py:845-868` | The `mreg is not None and tiles` branch and its `MATRIX_AMBIGUOUS` else |

### 2.1 The refocus, measured

Over the last 40 merges (2026-08-11 → 2026-08-31): **6 changed pipeline behaviour, 34 did not.**
Three touched `src/` only to rewrite comments about line-number citations. Bucketed
`git diff --numstat dd218a5^ HEAD`: `docs/superpowers/` **+29,101** lines against **461 non-comment**
`src/iladub/` lines — **63:1**. The register holds **105 open residues, 72 of them PRODUCT**.

None of that governance work was wrong. The repo was governing a compiler it had stopped teaching
to read.

### 2.2 The score line, re-measured at `b5f395b` today

```
who-wfa-boys-zscore-0-5.pdf   0.5597  {MATRIX_AMBIGUOUS: 3}
apple-fy2026q3-statements.pdf 0.3556  {REGION_TILING_FAILED: 11, MATRIX_AMBIGUOUS: 2,
                                       KIND_NOT_SUPPORTED: 1, ROUND_TRIP_FAIL: 1, DATAGRID_RESIDUE: 1}
```

Both reproduce their 2026-08-20 census figures **exactly**. No regression, no progress. WHO is the
only corpus document whose entire escalation surface is a single reason — which is why it was
chosen over apple's four mechanisms.

### 2.3 Why the opening premise was refuted

Wrapping `classify_matrix` and reporting which stage returns `None` prints, for all three bands:

```
stage=OK  returned_None=False  ncols=12  nlines=9
stage=OK  returned_None=False  ncols=12  nlines=8
stage=OK  returned_None=False  ncols=12  nlines=8
```

So `MATRIX_AMBIGUOUS` does **not** fire because the matrix classifier refused. It fires because
`region_tiles` returned false. Wrapping `region_tiles` and dumping `sh:sourceShape` gives one shape,
on every band: `tab:UnambiguousAccessShape`. Counting leaf headers per leaf column gives **n=2 for
columns 1,2,3,8,9,10,11 and n=1 for 4,5,6,7**.

### 2.4 The tree the reader actually builds

```
ch0  L0 parent=NONE  cols=[1,2,3,4,5,6,7]   "Z-s"
ch1  L0 parent=NONE  cols=[8]               "res (weight"
ch2  L0 parent=NONE  cols=[9,10,11]         "kg)"
ch3  L1 parent=ch0   cols=[1]               "Month"
ch4  L1 parent=ch0   cols=[2]               "L"
ch5  L1 parent=ch0   cols=[3]               "M"
ch6  L1 parent=NONE  cols=[4,5,6,7,8,9,10,11]  "S"
ch7  L2 parent=NONE  cols=[1,2,3,4,5]       "-3 SD"
ch8  L2 parent=ch6   cols=[6]               "-2 SD"
ch9  L2 parent=ch6   cols=[7]               "-1 SD"
ch10 L2 parent=ch6   cols=[8]               "Median"
ch11 L2 parent=ch6   cols=[9]               "1 SD"
ch12 L2 parent=ch6   cols=[10]              "2 SD"
ch13 L2 parent=ch6   cols=[11]              "3 SD"
```

Three failures compound: the spanning label `Z-scores (weight in kg)` arrives as three pseudo-labels;
`S` and `-3 SD` absorb every column to their right under nearest-centre; and strict-subset parent
linking then leaves `ch6` and `ch7` parentless, so two levels are simultaneously leaves over the
same columns.

**The oracle is right and the proposer is wrong.** That is the epistemics working — nothing
silently mis-read — and it is why the loop is a *reading* loop, not a bug fix.

## 3. What was decided, and where that decision is recorded

- **Refocus onto the product, and specifically onto WHO / `R45` / `tab:05`** — the maintainer chose
  it from four options this session. Recorded **here and nowhere else; reversible.**
- **Apple was considered and set aside** for this loop: four mechanisms rather than one. The census
  claim that two defects explain ten of its eleven escalations is **not re-verified** and would be
  the loop's own first half.
- **Accepting `graincorp-capacity` (1.0000) and `ons` (0.9720) was considered and set aside**: they
  are held for want of a contract and a human reading the compile against the PDF, so the work is
  the maintainer's eyes rather than a loop. It remains the cheapest route from 1/7 to 3/7.
- **No spec was written this session, deliberately** — CLAUDE.md § Loop & context hygiene: a loop is
  a session. This session spent its budget on reflection and measurement; the spec belongs to a
  fresh one.

## 4. Unverified or assumed

- **The full corpus battery was NOT run.** Two documents were compiled directly; the other five
  carry 2026-08-20 figures nobody has reproduced since. **Unchanged for five loops now.**
- **The `-m "not corpus"` suite was NOT run this session.** No code was changed, so nothing is
  claimed about it.
- **Branch (b) of part 5 is unfalsified** — that `"Z-s" / "res (weight" / "kg)"` are grid artefacts
  rather than genuine PDF text runs is inferred from how the cuts *look*, not from reading the PDF's
  word runs. It is the single most load-bearing unmeasured claim in this file.
- **The apple tree was not dumped**; whether its two `MATRIX_AMBIGUOUS` firings share WHO's
  mechanism is unknown, and the two documents are assumed related only by escalation label.
- **`infer_column_tree_by_proximity`'s `< 0.5` level-grouping tolerance was not exercised** as a
  suspect. It is a tuned constant and CLAUDE.md §8 calls that prima facie evidence, but no
  measurement here implicates it.
- **No working-token figure was reported to this session**, so the gate was logged at 0 and the
  handoff was written on the reading-order argument rather than on a measured crossing.
