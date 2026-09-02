# The body starts at the stub — apple's double header is a SPLIT defect, not a tree defect

**Date:** 2026-09-02. **Branch:** `the-body-starts-at-the-stub`. **Measured at:** `3055ae8` (HEAD of
`main`), every figure below from throwaway scripts in the session scratchpad; no repo file was
changed by any measurement.

**Predecessors:** `docs/superpowers/2026-09-01-corpus-reach-measured-handoff.md` § 5 named the
target — apple's `Three Months Ended … Nine Months Ended` double header, located by the 2026-08-20
escalation census in `matrix.infer_column_tree_by_proximity`. `2026-08-31-who-tree-refutation-
handoff.md` § 5 named the same function for WHO and left its §8 class open, with an explicit
instruction not to inherit the earlier AXIOM ruling.

**Doc impact: increment.** `tests/corpus-manifest.ttl`'s apple `cor:rationale` cites the census
figures (0.3556, "one double header the matrix reader cannot resolve") that this spec re-measures;
`docs/wiki/concepts/neurosymbolic-exemplars.md` gains one AXIOM derivation. No released assertion
changes; no contradiction.

**Global Constraint — the neurosymbolic gate (CLAUDE.md §8).** Every decision in this loop is
classified below (§ 2) before any code. A tuned constant anywhere in the shipped diff is a review
failure. Reviewers enforce it.

---

## 1. What was asked, and what the measurement says

### 1.1 The target is refuted

Dumping the tree (never done before this session, per the WHO handoff § 4) for the two bands that
fire `MATRIX_AMBIGUOUS` on apple:

```
apple p0 band 2: ncols=5 split=2 stub=1
  L0: ('Three Months Ended', 326.7–406.9) ('Nine Months Ended', 461.2–536.4)
  L1: ('June 27,', 317–350) ('June 28,', 383–417) ('June 27,', 449–482) ('June 28,', 515–549)
  col_tree: [(0,'Three Months Ended',(1,2)), (0,'Nine Months Ended',(3,4)),
             (1,'June 27,',(1,),→0), (1,'June 28,',(2,),→0), (1,'June 27,',(3,),→1), (1,'June 28,',(4,),→1)]
  logical_rows → None            ← the refusal
```

The column tree is **correct**. `classify_matrix` returns None because `logical_rows` finds no
anchor column — and it finds none because line 2 of the band, `2026 2025 2026 2025`, is in the
body. `header_body_split` returns 2: a Numeric line above Currency lines is one homogeneous
`tab:Quantity` family, so the type-transition query (`vocab/queries/header-body-split.rq`) places the
body start at the years line. The years line has no stub cell, `Net sales:` has only a stub cell,
so no column has exactly one cell in every body row.

WHO, the other document that handoff attached to this function, no longer refuses: it compiles at
**0.9096** against its 0.90 floor (reach handoff § 2, reproduced here byte-identical under the
spike in § 1.4). The Voronoi subject is moot for WHO.

### 1.2 Finding A — forcing the split proves it is the only blocker on page 0

Monkeypatching `matrix.header_body_split` to return 3 on apple p0 band 2:

```
col_tree: L0 'Three Months Ended'(1,2) 'Nine Months Ended'(3,4)
          L1 'June 27,'(1) 'June 28,'(2) 'June 27,'(3) 'June 28,'(4)
          L2 '2026'(1)→'June 27,'  '2025'(2)→'June 28,'  '2026'(3)  '2025'(4)
leaf_rows: 9   row_tree: 9   entries: 28   region_tiles: True
```

A three-level header, every parent link correct, and the region tiles. Nothing else stands between
this band and assertion.

### 1.3 Finding B — the tree silently drops header ink on unruled bands

apple p2 band 2 (the four-line supplemental cash table) carries **no vertical rules**
(`0` of the page's 347 intersect it), so its words are pdfplumber words, not ruled cells:
`Nine | Months | Ended` on L0, `June | 27, | June | 28,` on L1. p0 band 2 is ruled (136 rules
intersect) and `_build_ruled_band` re-extracts `Three Months Ended` as one cell — the same
header, two granularities. Forcing split=3 on p2 band 2:

```
col_tree: L0 'Nine'(1) 'Ended'(2)   L1 '27,'(1) '28,'(2)   L2 '2026'(1) '2025'(2)
header words: Nine Months Ended June 27, June 28, 2026 2025      (9)
nodes: 6 — 'Months', 'June', 'June' carried by NO node
```

`infer_column_tree_by_proximity` assigns each data column to its nearest label; a label that wins
no column simply never becomes a node, and `region_tiles` cannot see it because it was never
emitted. Today Finding A masks this (the band refuses earlier). **Fix A alone and this band ASSERTS
a header with a third of its ink gone** — CLAUDE.md §7, "only emit what the source supports",
violated silently.

### 1.4 Finding C — the end-to-end run, and the score DROP that is accepted

`matrix.header_body_split` patched to: type split, then advance to the first line at/after it that
carries a stub-column cell (§ 3.1, exactly). Whole-document compile:

```
                       HEAD      spike     adopted pages
apple                  0.3587    0.2087    (1,) → ()
who                    0.9096    0.9096    () → ()        byte-identical verdicts, all pages
apple p0 band 2   MATRIX_AMBIGUOUS → asserted
apple p1 band 2   superseded       → asserted   (and bands 3,4,5,7 revert superseded → escalated)
apple p2 band 2   MATRIX_AMBIGUOUS → asserted   ← Finding B's false assertion; § 3.2 refuses it
```

The drop is a single mechanism. `vocab/queries/adoption-candidate.rq` admits a page to the datagrid
adoption (R73) only when the page carries **no `tab:EntryCell`**; once the balance-sheet header
band asserts, page 1 has entry cells and the whole-page reader that had superseded five escalations
is refused. A band reader taking one small band pre-empts a reader that took the whole page.

**The maintainer chose to accept the drop (2026-09-02, this session; recorded here only).** The
header bands' assertions are correct readings; the adoption was a fallback whose gate is
"nothing asserted", and the interaction is raised as a residue (§ 7), not resolved here. **The score
is not the oracle** (see `r155-refuted-neural`: a score movement in either direction licenses
nothing) — the oracle is § 5.

### 1.5 Corpus census for the rule in § 3.1

Every matrix candidate in the 7-document corpus, all pages:

```
ons   p4 band0  ncols=3  split=6 stub=1 first_stub_line=6
apple p0 band2  ncols=5  split=2 stub=1 first_stub_line=3   <-- DIFFERS
apple p2 band2  ncols=3  split=2 stub=1 first_stub_line=3   <-- DIFFERS
who   p0 band2  ncols=12 split=2 stub=1 first_stub_line=2
who   p1 band2  ncols=12 split=2 stub=1 first_stub_line=2
who   p2 band1  ncols=12 split=2 stub=1 first_stub_line=2
```

The rule agrees with the current split on all four non-apple candidates and differs on exactly
apple's two. **This is a LOW-POWER oracle** — six bands, four agreeing — and is recorded as such
(`header-level-is-band-line` memory: a corpus oracle that cannot fail is not an oracle). The unit
fixtures in § 5 are the falsifying instrument; the corpus is the two-sided regression check.

---

## 2. Classification under §8 — argued for THIS subject, not inherited

**A — the matrix body start: AXIOM, derivation, open world.** The question is *"which line is the
first body line of a two-axis matrix"*. It is answered by the **presence** of a stub cell: a leaf
row of a matrix is a row headed in the stub (that is what `logical_rows`' anchor column and
`infer_row_header_tree` both consume), so the body cannot start before the first line that has
one. The derivation is evidence-positive — a line is body because a stub cell is *there*, never
because something is absent; the `MIN` over lines is holon-scoped to one band; it consumes two
assertions that already exist (`header_body_split`'s type transition and `stub_data_split`'s `k`)
and adds no vocabulary. It is not NEURAL: no span, read or group judgement is made, and no
constant is tuned. The WHO handoff's warning applies — the earlier AXIOM ruling was about
word-atomicity and does not transfer — and this argument is made fresh against the years row.

**What the rule does with a line it moves.** A line between the type split and the first stub
line becomes a *header level*. It is not asserted as a header by the rule; the tree over it and
`region_tiles` dispose of it exactly as they dispose of any header level. A numeric header level
(`2026 2025 2026 2025`) is what the author drew.

**B — uncarried header ink: a closed-world completeness check, implemented as a producer-side
guard.** The constraint — *every header word over the data columns is carried by exactly one
node* — is closed-world over one holon (the band), which is SHACL's world. But the membrane cannot
enforce it: the dropped words are precisely the ink that never enters the graph, and a shape
cannot refuse what is not there without inferring from absence. CLAUDE.md § "Producer-side guards
vs the membrane" is the ruling: a guard is kept where the membrane provably cannot validate every
product of the producer. The guard consumes the band's own words and the nodes' words; no
constant. **Grouping the words into labels** (which would let the band assert) is a *"which
words form one label"* question — NEURAL by §8's wording, and `R155` measured the geometric half
impossible without a tuned constant. Not this loop (§ 6).

---

## 3. Design

### 3.1 The matrix body start (A)

A new derivation, `vocab/queries/matrix-body-start.rq`, run over the same typed-cell evidence graph
`header_body_split` already builds (`celltype.grid_evidence(_grid_cells(band, grid), ncols)`), with
two bindings: `?split` (the type transition) and `?k` (the stub width). It returns

    MIN(row) over cells with tab:atGridRow ≥ ?split and tab:atGridColumn < ?k

— the first cell-bearing line at or after the type split that has a stub cell. Stub cells are
identified by column, not by datatype: a numeric stub label is still a stub label.

Python seam: one function in `matrix.py`,

    matrix_body_start(band, grid, split: int, k: int) -> int | None

returning the derived line index, or `None` when no line at/after `split` carries a stub cell.
`classify_matrix` and `is_matrix_candidate` call it after `stub_data_split` and use its result
wherever they use `split` today (the header levels `band.lines[:split]`, `band.lines[split].top`,
`MatrixRegion.body_line`). `header_body_split` and `header-body-split.rq` are **untouched**; the
record and hierarchical paths never see this rule.

Invariants:

- `matrix_body_start(...) ≥ split` always, and `< len(band.lines)` when not None.
- When line `split` itself carries a stub cell the result equals `split` — every non-apple corpus
  band (§ 1.5) must produce a byte-identical graph.
- `k` is derived from the type split, as today, and is not re-derived from the moved body start.
  Stated as an assumption (§ 8).

### 3.2 The uncarried-ink refusal (B)

In `infer_column_tree_by_proximity`, after the nodes are built: if any word on a header level whose
centre lies in a data column (`column_of(centre, boundaries) in data_cols`) is not the `word` of
some node, return `None`. `classify_matrix` then returns `None` and the band escalates
`MATRIX_AMBIGUOUS` through the existing site (`compile.py:859`) — no new escalation reason, no
new vocabulary. The stub header (`Year: Month` on WHO, centre in column 0) is *not* over a data
column and must not trigger the guard; that is the case § 1.5's WHO bands pin.

The rationale recorded by the band recorder for the `matrix_candidate`/`verdict` records is not
changed by this loop; the guard's reason is visible in the region's `MATRIX_AMBIGUOUS` and in the
unit test's name. (A named reason is a candidate increment — § 7.)

### 3.3 Order of operations, stated once

    grid → type split → k → matrix body start → column tree (with guard) → leaf rows → row tree

Any plan task that changes this order must re-measure § 1.2 first.

---

## 4. What is NOT done — deliberately

- **Grouping unruled header words into labels.** NEURAL by wording; `R155` measured its geometric
  half a tuned constant. apple p2 band 2 stays `MATRIX_AMBIGUOUS`, now for an honest reason (B).
- **The adoption gate (C).** Page 1's datagrid adoption is lost and the score drops to ~0.2087.
  Raised as a residue; the reader-authority question touches R73's monotonicity premise and is
  its own loop.
- **The eight `REGION_TILING_FAILED` section bands** (p0 bands 3,5,6,7; p2 bands 3,4,5,7). Loop Q's
  section repair never fires on apple (`DocumentReport.repaired_bands == ()`), and nobody has
  measured why. Larger than this loop's subject; raised as a residue.
- **`header-body-split.rq` is not changed.** The type transition stays the global rule; the stub
  rule is matrix-scoped because "stub" is a two-axis notion.
- **No new escalation reason** for the guard.

---

## 5. The oracle — falsifying, two-sided, per task

**O1 (A, positive).** A synthetic ruled PDF fixture with a three-level header whose third level is
numeric (`Three Months Ended / Nine Months Ended` over `June 27, / June 28,` over `2026 / 2025`),
a stub column and a section row. `classify_matrix` returns a region whose `col_tree` has three
levels with the year nodes parented under the date nodes, and `region_tiles` is True.
**Falsification:** revert `classify_matrix` to the type split; the test fails at `logical_rows`.

**O2 (A, negative, the invariant).** On a fixture where line `split` carries a stub cell,
`matrix_body_start == split`. **Falsification:** make the query ignore `?split`; the test fails on
a fixture whose stub column has a header cell above the split.

**O3 (B, negative).** A synthetic *unruled* fixture whose top header level is a multi-word spanner
(`Nine Months Ended` as three pdfplumber words) — the fixture must be measured to produce three
words, not assumed. `classify_matrix` returns `None`. **Falsification:** delete the guard; the test
fails by asserting a tree of fewer nodes than data-column header words.

**O4 (B, the stub-header exemption).** A fixture with a text header over the stub column at a
header level (WHO's `Year: Month`) still classifies. **Falsification:** drop the data-column
condition from the guard; WHO refuses. This is also the corpus leg.

**O5 (corpus, two-sided).** Full corpus battery: WHO 0.9096 byte-identical verdicts; gstem ≥ 0.95;
gcap, ons, cbh, bfs unchanged; apple's p0 and p1 header bands **asserted**, p2 band 2
`MATRIX_AMBIGUOUS`, score at the § 1.4 figure ± the p2 effect, `adopted == ()`. The apple
manifest rationale is updated to say so (Doc impact). **The battery has not run in seven loops;
this loop runs it.**

**O6 (declaration).** The new `.rq` names only declared `tab:` terms — the declaration instrument
(`tests/query_terms.py`) is already green on every tracked query and must stay green.

---

## 6. Interfaces (signatures and invariants only — plan rule 1)

    # vocab/queries/matrix-body-start.rq — bindings ?split ?k, SELECT (MIN(?row) AS ?body)
    # src/iladub/etkl/matrix.py
    def matrix_body_start(band, grid, split: int, k: int) -> int | None: ...
    def infer_column_tree_by_proximity(band, grid, split, data_cols):   # unchanged signature
        # returns None when a data-column header word is carried by no node

Seams the implementer must MEASURE before writing the call (plan rule 3): where `split` is
consumed inside `classify_matrix`/`is_matrix_candidate` (three uses, § 3.1); whether `run_scalar`'s
`bindings` reach the query as typed integers; and that `absorb_unit_markers` has already removed
marker words from the lines the guard reads.

---

## 7. Residues to raise (register rows, numbered by the plan)

- **The datagrid adoption gate is pre-empted by one asserting band** — measured apple p1,
  0.3587 → 0.2087, `adopted (1,) → ()`; the gate is `adoption-candidate.rq`'s `NOT EXISTS
  tab:EntryCell`. A reader-authority question, not a bug in either reader.
- **Loop Q's section repair never fires on apple p0/p2** — 8 of 11 escalations; `repaired_bands`
  empty; cause unmeasured.
- **Unruled header labels are words** — one `Line.words` abstraction carries two granularities
  (ruled cell vs pdfplumber word); grouping is NEURAL by wording. Sibling of `R155`.
- **The guard's refusal carries no named reason** — a candidate `tab:`/`dec:` increment.
- **§ 1.5 is a six-band oracle.** Recorded so nobody reads "4 of 4 agree" as power.

---

## 8. Unverified or assumed

- `k` from the type split equals `k` from the moved body start on every corpus band — assumed,
  measured only on apple (k=1 either way).
- The p1 balance-sheet header band's assertion is a *correct* reading — its tree was not dumped;
  only p0's was. The plan's O5 leg dumps it.
- `run_scalar` bindings: read (`celltype.py:141-147`), not driven with two bindings.
- The `- 0.5` in `logical_rows` (`rows.py:28`) is a pre-existing constant this loop consumes and
  does not touch; noted, not classified here.
