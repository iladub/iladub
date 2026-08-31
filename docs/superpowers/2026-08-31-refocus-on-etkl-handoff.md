# Handoff — the refocus on etkl, and the WHO matrix header measured to its root

**Topic:** why the last three weeks moved the repo's governance and not its compiler, which corpus
document is the smallest slice back onto the product, and the diagnosis of that document's single
defect — measured today at `b5f395b`, and **refuting the reading this session opened with**.

Part 5 is written first, per CLAUDE.md § "The handoff's next action is TYPED".

## 5. The next concrete action — TYPED

**The falsification this section originally ordered HAS BEEN RUN, and it settled the fork.** The
prediction, its result and the loop it produced are all below. Read § 2.5 before § 5.3 — the
proposal is only as good as the measurement under it.

### ASSERTED — mechanical, outcome known

**Reproduce §§ 2.3-2.5 before designing anything.** Each takes ~2 minutes on a warm venv and each
outcome is pinned here: score `0.5597`; one refusing shape (`tab:UnambiguousAccessShape`) on all
three bands; 7 of 11 leaf columns at `n=2`; the 14-node tree of § 2.4; and pdfplumber's four clean
header words of § 2.5. A fresh session must not take this file's word for any of it.

### ASSERTED — the fork is discharged, and the subject MOVED

The two branches this section originally posed were **(a)** the column tree is the defect and
**(b)** the grid is, with the tree a symptom. **(b) is confirmed; (a) is dead as framed.**

`extract_words` on WHO page 0 returns `'Z-scores' // '(weight' // 'in' // 'kg)'` — four clean runs
(§ 2.5). The `"Z-s" / "res (weight" / "kg)"` fragments the header tree carries **do not exist in the
PDF**. They are manufactured by `_build_ruled_band` (`compile.py:73`, called at `:319`), which
re-extracts a ruled band from `page_chars` at the ruled column boundaries — correct for data rows,
and mid-word for a header label that crosses rulings by design.

**So the subject of this loop is `_build_ruled_band`, NOT `matrix.py`.** Anyone who opens
`infer_column_tree_by_proximity` first is reading the symptom. A NEURAL span proposer at the tree
seam — this session's opening instinct — would have asked a model to reconstruct a label the
extractor had already destroyed.

### PROPOSED — the loop, and it must be scoped fresh

**The invariant:** *a ruled re-extraction must never split inside a word run.* Where a ruled
boundary falls strictly inside a word's x-extent, that word is not split; it is a label spanning the
columns it crosses.

**Classified AXIOM, not NEURAL, and the argument matters.** CLAUDE.md §8 routes *"which columns does
X span"* to NEURAL, so the reflex is a BAML proposer. The measurement makes that wrong here: knowing
`Z-scores` spans a boundary needs no perception, only the observation that the split lands mid-word,
and the extractor has already asserted the word is one run. Evidence-positive, open-world, no
tolerance, no constant, no model. §8's default IS axiom and NEURAL must be *earned*; this decision is
not underdetermined, so it does not earn it. **If a reviewer disagrees, that is the argument to have
before any code — it is the whole shape of the loop.**

**What proposes / what disposes.** Proposer: the word-atomic re-extraction (new). Disposer:
`tab:UnambiguousAccessShape` + the twelve other tiling shapes in `region_tiles` — already built,
refusing correctly today, and authored in complete ignorance of this change. **Independent by
construction**, which is the rare and favourable part of this loop.

**The loop's own falsifiable prediction — budget for refutation.** *Word-atomicity alone makes WHO
tile.* It may not. `S` covering cols 4-11 and `-3 SD` covering 1-5 (§ 2.4) come from **nearest-centre
assignment**, which may still misbehave once the top label is a single node. If the prediction
fails, the loop's second half is the column tree after all — and the spec should say so up front
rather than discover it in a plan.

**The success oracle is TWO-SIDED, and the second side is the work.** `_build_ruled_band` is on the
path for **every ruled band in every document**, `graincorp-stem` included — the one document that
passes, at 0.9655 against a pinned 0.95 floor. WHO tiling is not success if anything else regresses.
This is what makes it a loop rather than a chore, and it is the reason the full corpus battery must
run inside it (see § 4 — it has not run in five loops).

**Deliberately out of scope:** apple's 11 `REGION_TILING_FAILED` (different mechanism, unmeasured
relation); and the `< 0.5` level-grouping tolerance in `infer_column_tree_by_proximity` — a standing
§8 smell that **no measurement here implicates**. Note it; do not fix it in this loop.

**Accounting if it closes:** strikes `R45`, moves arc `tab:05` — the sole dependency of `etkl:07`
and one of three for `etkl:06`. It would be the first arc movement since 2026-08-25.

### PROPOSED — blocked on rulings, unchanged and NOT re-derived

`R132` (identity/merge), `R127` (four coupled oracles), `R131`(b). Open
`docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5 — that table is still the source.

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
| `src/iladub/etkl/compile.py:73` (`_build_ruled_band`), called at `:319` | **THE SUBJECT OF THE LOOP.** Re-extracts a ruled band from `page_chars` (`:304`) at ruled column boundaries. Read its comment at `:316-317` for the stated intent, and `:132` for the char filter |
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

### 2.5 The falsification, run — the fragments are manufactured

`extract_words(pdf, 0)` + `text_lines`, page 0, first lines:

```
top= 104.37 | 'Z-scores' // '(weight' // 'in' // 'kg)'
top= 118.71 | 'Year:' // 'Month' // 'Month' // 'L' // 'M' // 'S' // '-3' // 'SD' // '-2' // 'SD'
             // '-1' // 'SD' // 'Median' // '1' // 'SD' // '2' // 'SD' // '3' // 'SD'
```

Four clean runs where the header tree of § 2.4 carries three mid-word fragments. The cut points are
therefore **grid artefacts, not text**. `compile.py:304` extracts `page_chars` only when the page has
rules, and `:319` hands them to `_build_ruled_band` (`:73`), whose own comment states the intent:
*"re-extract cells by the ruled columns (splits pdfplumber-merged blobs at the author's exact
boundaries)."* That intent is right for a data row and wrong for a spanning header, and nothing in
the code distinguishes the two.

## 3. What was decided, and where that decision is recorded

- **Refocus onto the product, and specifically onto WHO / `R45` / `tab:05`** — the maintainer chose
  it from four options this session. Recorded **here and nowhere else; reversible.**
- **Apple was considered and set aside** for this loop: four mechanisms rather than one. The census
  claim that two defects explain ten of its eleven escalations is **not re-verified** and would be
  the loop's own first half.
- **Accepting `graincorp-capacity` (1.0000) and `ons` (0.9720) was considered and set aside**: they
  are held for want of a contract and a human reading the compile against the PDF, so the work is
  the maintainer's eyes rather than a loop. It remains the cheapest route from 1/7 to 3/7.
- **The loop's subject MOVED from `matrix.py` to `_build_ruled_band`, by measurement, not by argument** (§ 2.5). Recorded here and in this branch's PR; **nowhere else; reversible.**
- **The word-atomicity invariant is classified AXIOM rather than NEURAL** — the argument is in § 5, and it is deliberately exposed there as the thing to attack. Recorded **here only.**
- **No spec was written this session, deliberately** — CLAUDE.md § Loop & context hygiene: a loop is
  a session. This session spent its budget on reflection and measurement; the spec belongs to a
  fresh one.

## 4. Unverified or assumed

- **The full corpus battery was NOT run.** Two documents were compiled directly; the other five
  carry 2026-08-20 figures nobody has reproduced since. **Unchanged for five loops now**, and § 5
  makes running it part of the next loop's success oracle rather than a chore beside it.
- **The `-m "not corpus"` suite was NOT run this session.** No code was changed, so nothing is
  claimed about it.
- **Whether word-atomicity alone makes WHO tile is UNKNOWN** — it is § 5's stated prediction, not a
  result. The nearest-centre assignment may still mis-span once the top label is one node.
- **The blast radius of changing `_build_ruled_band` is UNMEASURED.** It is asserted to be on every
  ruled band's path from reading `:319`, not from a call-site census or a corpus run.
- **The apple tree was not dumped**; whether its two `MATRIX_AMBIGUOUS` firings share WHO's
  mechanism is unknown, and the two documents are assumed related only by escalation label.
- **`infer_column_tree_by_proximity`'s `< 0.5` tolerance was not exercised** as a suspect. It is a
  tuned constant and CLAUDE.md §8 calls that prima facie evidence, but nothing here implicates it.
- **The AXIOM-not-NEURAL classification in § 5 is an argument, not a measurement.** It is the single
  most contestable claim in this file and the right thing for a reviewer to attack first.
- **This handoff's § 5 was authored at ~87k working tokens, 1.7x the originating floor**, with the
  override logged. Its measurements are safe; its reasoning is the part to re-derive.
