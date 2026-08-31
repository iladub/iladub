# A header level is a band line — closing `R45`

**Date:** 2026-08-31 · **Residue:** `R45` · **Branch:** `r45-a-header-level-is-a-band-line`

**Doc impact: none.** No owned term is added or re-commented, no `owl:versionInfo` moves, nothing
enters `mkdocs.yml`'s nav. The loop deletes one tuned constant from one private helper, adds one
fixture and its tests, and re-pins one corpus expectation.

**Evidence this spec is written from:** the `R45` and `R154` rows in
`docs/superpowers/residues-open.md`; the reproduction and spike measurements in §3 below, all taken
this session at HEAD `22263a2` (`src/`, `tests/`, `vocab/` byte-identical to `3f3ed4e`, where the
predecessor measured — `git diff --stat 3f3ed4e HEAD` is 3 files, all `docs/`). The two predecessor
handoffs are **cited, never restated**: `2026-08-31-who-tree-refutation-handoff.md` (whose § 5
ASSERTED block is reproduced in full, §3.1) and `2026-08-31-refocus-on-etkl-handoff.md`.

---

## 1. What this closes, and what it does not

**Closes `R45`** — WHO's 3× `MATRIX_AMBIGUOUS`, score `0.5597 → 0.9096`, measured (§3.3).

**Does NOT close `prog:criterion:tab:05`** (`tests/arc-manifest.ttl:1184-1192`). That criterion is
`prog:blockedBy "R45", "R62"`, and **apple is measured unchanged by this loop** — its 2
`MATRIX_AMBIGUOUS` survive byte-identically (§3.4). Anyone reading the score jump as "the matrix
escalation is disposed" is wrong; `R62` is untouched and the criterion stays `prog:met false`.

**Does NOT close `R154`** (the ruled re-extraction chopping `'Z-scores'` into `'Z-s' // 'res
(weight' // 'kg)'`). Measured irrelevant a second, independent way: the tree that **passes** in §3.3
still carries all seven chopped fragments. Broken labels, correct structure, document tiles. `R154`
stays open on its own row and this loop must not be read as bearing on it.

**Does NOT revisit the span-assignment question** the predecessor's § 5 posed. See §2.

**Costs more than it looks.** WHO is currently used across the suite as *evidence that escalation
happens* — one test selects it precisely because it escalates with nothing withdrawn, and fails by
design when this loop succeeds. §6 enumerates that surface; it is the loop's real work, not the
three-line change in §5.

## 2. The subject — stated once

The predecessor's § 5 named `infer_column_tree_by_proximity` (`src/iladub/etkl/matrix.py:39`) and
asked whether *"which columns does this header label span"* is determined or underdetermined,
directing the next session to re-argue `CLAUDE.md` §8 against the nearest-centre (Voronoi)
assignment.

**That framing is refuted by measurement.** The Voronoi assignment is correct and is **unchanged,
line for line**, in the spike that makes WHO tile (§3.3). The subject is one helper above it:

> **`_level_tops` (`src/iladub/etkl/matrix.py:34-36`) discards the band's own line grouping and
> re-derives header levels from `round(w.top, 1)`, then filters each level's labels with a
> `< 0.5` point tolerance (`:57`). Sub-point intra-line baseline drift is thereby promoted to a
> header level boundary.**

That is the whole defect. Everything in §4 follows from it and is not re-derived there.

## 3. Measurement at HEAD `22263a2`

### 3.1 The predecessor's § 5 ASSERTED block reproduces — all seven claims

Re-run this session, `./.venv/bin/python`, `compile_document` on
`corpus/health/who-wfa-boys-zscore-0-5.pdf`: score `0.5597`; escalated-region reasons
`{MATRIX_AMBIGUOUS: 3}`; `classify_matrix` → `ncols=12`, `stub_cols=(0,)`, `data_cols=(1..11)`,
`body_line=2` on all three bands; `tab:UnambiguousAccessShape` the sole `sh:sourceShape` in all
three reports; leaf-header counts `{1:2,2:2,3:2,4:1,5:1,6:1,7:1,8:2,9:2,10:2,11:2}` (identical on
all three bands — the handoff pinned it once); the 14-node tree node-for-node; `extract_words`
page 0 giving `'Z-scores' // '(weight' // 'in' // 'kg)'`; and the seven-fragment ruled chop.

**Two precisions, not corrections.** The handoff's "48 raw rule x's" is **48 distinct rounded x's
from 72 raw `Rule` objects** (`xs = sorted({round(r.x, 2) …})` is the figure `_build_ruled_band`
uses). Quad width is `10.80` for 8 of 11 quads and `10.86` for 3 — modal, not uniform.

### 3.2 The evidence, and why the levels are wrong

`extract_words`, WHO page 0, the two lines that matter:

```
top 118.7   Year: | Month | Month | L | M | S
top 119.6   -3 SD | -2 SD | -1 SD | Median | 1 SD | 2 SD | 3 SD
```

0.9pt apart — **one visual header line.** Three independent facts in the tree say so:

1. `text_lines` (`geometry.py:459`) groups on `0.6 × median glyph height` (≈4-5pt here) and puts
   them in one `Line`.
2. `rule_aware_lines` (`geometry.py:263`) uses the **same** `0.6 × med_h` row grouping, so both
   band producers agree.
3. `header_body_split` returns **`split=2`** — the band asserts two header lines.

`_level_tops` overrides all three and returns three tops, manufacturing a spurious third level.
`L`/`M`/`S` become leaf headers at level 1 while `-3 SD …` are leaf headers at level 2 over
overlapping columns — the two-leaf-headers-per-column condition `tab:UnambiguousAccessShape`
(`vocab/shapes/tab-shapes.ttl:127`) **correctly** refuses. The shape is right; the tree fed to it is
wrong.

### 3.3 The spike — level ≔ band line

Throwaway monkeypatch, no repo file changed, `git status` clean throughout. Levels become
`enumerate(band.lines[:split])` with that line's labels exactly `ln.words`; Voronoi assignment,
contiguous-run covers and strict-subset parent linking all unchanged.

```
                     score     verdicts
baseline   0.559748427672956   ignored 8, escalated 3, asserted 7   {MATRIX_AMBIGUOUS: 3}
byline     0.909596662030598   ignored 8,              asserted 10  {}
```

The two nodes that were orphaned, and are no longer:

```
baseline                                  byline
ch6  L1 'S'      covers=(4,5,6,7,8,9,10,11)   ch6  L1 'S'      covers=(4,)  parent=ch0
     parent=None                                   
ch7  L2 '-3 SD'  covers=(1,2,3,4,5)              ch7  L1 '-3 SD'  covers=(5,)  parent=ch0
     parent=None
```

Under `byline` every node is parented and the covers partition: `ch0` covers `(1..7)` with children
`ch3..ch9` over exactly `1..7`; `ch1` covers `(8)` with child `ch10`; `ch2` covers `(9,10,11)` with
children `ch11,ch12,ch13`.

### 3.4 Two-sided corpus oracle — the full battery, both modes

Not run for six loops before this session. Every corpus document, `compile_document`, baseline vs
byline:

| document | baseline | byline | verdict |
| --- | --- | --- | --- |
| `graincorp-stem` | `0.9654553611484971` | **identical** | PASS — the 0.95 floor holds exactly |
| `graincorp-capacity` | `1.0` | identical | PASS |
| `ons` | `0.9719934102141681` | identical | PASS |
| `cbh` | `0.9046563192904656` | identical | PASS |
| `bfs` | `0.34384384384384387` | identical | PASS |
| `apple` | `0.35560344827586204` | identical | PASS — **`MATRIX_AMBIGUOUS: 2` survives** |
| `who` | `0.559748427672956` | `0.909596662030598` | 3 escalations → 0 |

"Identical" is exact: score, every verdict counter, every escalation reason, `asserted_tokens`,
`escalated_tokens`, `adopted`, `repaired_bands`. **Six of seven documents are inert under this
change.**

### 3.5 The constant is unpinned by the current suite

`infer_column_tree_by_proximity` and `classify_matrix` are referenced only by
`tests/etkl/test_matrix.py` (9 references) and `tests/etkl/test_holon.py` (4). Every fixture behind
them is a **clean two-line header** (`crosstab_table_pdf`, `fixtures.py:347` — labels drawn at
`top` and `top - 13.0` exactly). **No existing test fails if `_level_tops` is deleted outright.**
This is why §7 requires a new fixture: the behaviour being changed is currently unpinned in both
directions.

## 4. Classification under the neurosymbolic gate (`CLAUDE.md` §8)

**AXIOM.** The argument is recorded here because the predecessor's handoff § 3 warns — correctly —
that the maintainer's earlier AXIOM ruling was made about a **different** subject (never splitting a
word run) and **must not be inherited**. This is a fresh argument against the relocated subject.

1. **It deletes a tuned constant rather than adding or tuning one.** `< 0.5` at `matrix.py:57` is
   precisely what §8 calls *"prima facie evidence the decision belongs in NEURAL/AXIOM, not
   procedural code."* The remedy removes it; nothing replaces it.
2. **It consumes an assertion the graph already carries.** A `Band`'s `lines` are a line grouping
   the band was built with. `infer_column_tree_by_proximity` is not asked to *judge* anything new —
   it reads what the band already says.
3. **It restores consistency with the sibling path.** `infer_header_tree` — the primary header-tree
   path — derives its levels as **rows of the band** (`header_rows_of` → `group_wrapped(band, grid)`
   filtered above `body_top`, `headers.py:386,406-408`). `infer_column_tree_by_proximity` is the only
   function in the repo that disagrees with the rest about what a header level *is*. This is not a
   new invariant; it is the removal of a divergence.
4. **No reading judgement is exercised.** The question *"are these two labels on the same header
   line"* is answered upstream, identically, by both band producers (§3.2 facts 1-2). Routing it to
   NEURAL would propose an answer the evidence already determines — and §7's *"only emit what the
   source supports"* cuts against manufacturing a judgement where none is needed.

**The honest caveat, stated once and not argued away.** `text_lines` and `rule_aware_lines` both
carry `0.6 × median glyph height`. The tolerance is **not eliminated from the system** — it is
**consolidated** into the two functions that already own line grouping and that every other reading
path already trusts. This loop reduces the number of places that decide what a line is from three to
two. It does not reduce it to zero, and no claim to that effect may appear in the implementation,
the commit message, or the residue row.

## 5. Interfaces — signatures and invariants, not bodies

**`_level_tops` is deleted.** It has exactly two references, both in `matrix.py` (`:35` definition,
`:49` call); §3.5 measures the test surface.

**`infer_column_tree_by_proximity(band, grid, split, data_cols)` — signature unchanged, return type
unchanged (`tuple[ColHeaderNode, ...] | None`).** Its contract gains one clause and keeps the rest:

- **NEW:** header levels are the band's own header lines. Level `L` is `band.lines[L]` for
  `L in range(split)`; the labels of level `L` are exactly that line's words. No tolerance appears
  in this function.
- **UNCHANGED, and the implementer must not touch:** nearest-parent-centre assignment over
  `data_cols`; a node covering the contiguous run assigned to it; strict-subset parent linking to
  level `L-1`; `None` when a level has no labels.

**The `band.lines` vs `group_wrapped` fork — SETTLED as `band.lines`, and the implementer owns
re-measuring it.** `headers.py` uses `group_wrapped`; `band.lines[:split]` is what §3.3 actually
measured. `band.lines` is chosen because it is what `split` already indexes — `header_body_split`
returns a count of `band.lines`, so `group_wrapped` rows and `split` are not the same coordinate
system and pairing them would be an unmeasured claim.

MEASURED, and the implementer re-measures before writing the call: `header_rows_of`
(`headers.py:386`) takes the same integer under the name `body_line` and dereferences it as
**`band.lines[body_line].top`** (`:407`) — so the split index is a `band.lines` index, and
`band.lines[:split]` is the coordinate system the rest of the header code already uses. If a
re-measurement contradicts this, stop and report a spec defect rather than adapting the index.

**The module docstring (`matrix.py:1-10`) must be updated.** It documents the centred-merge
assumption and the composition, and says nothing about level derivation. It gains one sentence
naming `band.lines` as the level source. Any `file:line` it cites is subject to `CLAUDE.md`
plan-rule 7 — **the docstring sits above everything it can cite in this file, so re-measure after
the edit, not only before.**

## 6. The consumers of WHO's escalation — enumerated, not assumed

**This section is the loop's real cost.** A document that stops escalating is not only a score
change: WHO is *used as evidence that escalation happens*. The surface below was enumerated by
grepping `tests/` for `who-wfa`, `0.5597` and `MATRIX_AMBIGUOUS` at HEAD `22263a2`. **The
implementer re-runs that enumeration before editing** — a missed pin is a green suite hiding a stale
expectation.

### 6.1 The blocker — a test that fails BY DESIGN when this loop succeeds

`tests/etkl/test_escalation_furnish.py:222-243`,
`test_corpus_census_every_live_escalating_decision_is_furnished`:

```
assert len(escalating) > 0, "chose a document that does not escalate — the test pins nothing"
```

Its docstring (`:228-231`) states the choice explicitly: *"who-wfa is chosen because it escalates
and NONE of its escalations are withdrawn (measured 2026-08-15: B=3, C=3, superseded=0); a test
written against graincorp-stem or ons, which carry zero escalations, pins nothing."*

**This loop removes exactly that property.** The test must be re-pointed at another corpus document
before the fix lands, or it goes red — correctly, and for the reason its own author wrote down.

**Name the seam, not the answer.** §3.4 shows `apple` (11 escalated, 5 superseded regions) and `bfs`
(10 escalated, no superseded regions) are the surviving candidates, but those are **region-level**
counters and `_census` counts **decision-level** `dec:chosen`/`dec:supersedes`. **MEASURE B, C and
superseded per candidate document with `_census` itself before choosing**; do not infer the
decision-level figures from the region-level table in §3.4. Record the chosen document's B/C/
superseded triple in the docstring the way the WHO one is recorded, and say there why WHO no longer
qualifies.

### 6.2 The corpus manifest — a HOLD adjudication that must become an ACCEPT

`tests/corpus-manifest.ttl:118-129`. WHO carries `cor:expectedVerdict cor:Unadjudicated`, **no**
`cor:scoreFloor`, and a HOLD `cor:adjudication` whose rationale is a prose record of the exact
figures this loop invalidates: *"score 0.5597, 3 pages, 3 escalation records, all MATRIX_AMBIGUOUS
… 445 asserted / 350 escalated tokens … Held until that header block is read."*

**That header block is now read.** The adjudication's own stated condition is discharged, so the
row moves to an accepting verdict with a pinned floor. The new rationale must be dated, must cite
this loop, and must carry §9's `R154` caveat — WHO now asserts a table whose top-level header nodes
read `'Z-s'`, `'res (weight'`, `'kg)'`. **Do not delete the HOLD rationale's measurements**; the
register convention (`CLAUDE.md` § Deferred residues) is that closure evidence is recorded in place,
never erased.

### 6.3 The arc manifest

| site | what it says | what this loop does to it |
| --- | --- | --- |
| `tests/arc-manifest.ttl:234-240` | criterion: WHO compiles to `cor:CompilesAbove` with a pinned `cor:scoreFloor` under an **accepting** adjudication | becomes satisfiable for the first time — §6.2 is its precondition |
| `:1184-1192` `prog:criterion:tab:05` | `prog:blockedBy "R45", "R62"` | edge on `R45` **deleted**, `R62` kept, `prog:met` stays `false` (§1) |
| `:121`, `:1022`, `:1182`, `:1551`, `:1597` | census comments and a `prog:dependencyRationale` reciting `who-wfa MATRIX_AMBIGUOUS x3` | prose records of a past census — **re-measure each before touching it**, and prefer annotating with the new date over rewriting history |

Per the maintainer's 2026-08-22 ruling in the `R108` row, closing a residue is a two-file change:
strike the register row **and** delete every `prog:blockedBy` edge naming it, or the arc refuses.

### 6.4 Comments and registries that recite the old figure

`tests/etkl/test_typing_equiv.py:24` pins `WHO 0.5597` in a comment describing a byte-identical
pre/post claim. `tests/etkl/test_vacuity_registry.py:72,114,446` use WHO as a registry entry and in
two prose rationales. **Open each; establish whether it is an assertion the suite checks or a prose
record of a past measurement**, and treat those two cases differently — the first is re-pinned, the
second is dated and annotated.

## 7. Oracles — what falsifies each piece

1. **The new fixture (the falsification that matters).** A cross-tab whose leaf header row carries
   sub-point baseline drift — the synthetic form of §3.2. `crosstab_table_pdf` (`fixtures.py:347`)
   is the template: draw three of the six leaf labels at `top - 13.0` and three at `top - 13.9`.
   Expected: **at HEAD it yields three levels and does not tile; with the fix it yields two levels
   and tiles.** Per `CLAUDE.md` plan-rule 1 this test is a **proposition until the implementer
   falsifies it** — the task report must show it RED before the fix, GREEN after, and RED again with
   the fix reverted. If it cannot be made to go red at HEAD, that is a spec defect: say so and
   report it, do not weaken the assertion.
2. **WHO, end to end.** `compile_document` on the WHO PDF: score `0.909596662030598`, zero escalated
   regions. Falsified by restoring `_level_tops`.
3. **The two-sided corpus oracle.** The six inert documents must stay byte-identical to §3.4 —
   score, verdicts, reasons, both token counts, `adopted`, `repaired_bands`. `graincorp-stem` at
   `0.9654553611484971` against its 0.95 floor is the headline; **any** change on **any** of the six
   is a stop-and-report, not a re-pin.
4. **The re-pointed escalation census (§6.1).** `test_corpus_census_every_live_escalating_decision_is_furnished`
   must pass against its NEW document and must still pin something: `len(escalating) > 0` has to
   hold for a real reason, not because the assertion was relaxed. **Falsify it the way its author
   did** — point it at `graincorp-stem` or `ons` (zero escalations) and show it RED. A version of
   this test that passes on a non-escalating document is `CLAUDE.md` plan-rule 1's defect 5 exactly.
5. **The unit suite.** `-m "not corpus"` green. It was **not** measured green at HEAD before this
   spec was written (§9).

## 8. What this loop deliberately does NOT do

- **Does not touch `rule_aware_lines` or the ruled re-extraction.** `R154` stays open; §1 gives the
  measurement showing it is not this defect.
- **Does not touch apple.** `R62` stays open, `tab:05` stays blocked (§1, §3.4).
- **Does not unify line grouping across `text_lines`/`rule_aware_lines`.** The `0.6 × med_h`
  consolidation caveat (§4) is recorded, not acted on.
- **Does not change `tab:UnambiguousAccessShape`.** The shape is correct and its refusal was
  correct; only the tree it was fed was wrong.
- **Does not touch `infer_header_tree`.** It is cited in §4 as prior art; it is not modified.
- **Does not re-argue the span-assignment AXIOM/NEURAL question.** §2 records why that framing was
  refuted; a future loop that finds a genuine span underdetermination reopens it on its own evidence.

## 9. Unverified when this spec was written

- **The `-m "not corpus"` suite has NOT been observed green at HEAD `22263a2`.** A run was
  commissioned in parallel with this spec and had not returned. The implementer must establish the
  baseline green **before** changing code; if it is already red, that is a finding that precedes
  this loop.
- **Whether any corpus document other than WHO contains sub-point header drift is UNKNOWN.** §3.4
  shows six are inert *under this change*, which is a statement about outcomes, not about whether
  the condition is present and harmless somewhere.
- **The WHO tree under `byline` was inspected on page 0 and asserted structurally correct against
  the visual layout by reading `extract_words` output** (§3.2). It was not checked against the
  published WHO table by a human. The tiling oracle certifies consistency, not fidelity to the
  source document.
- **`R154`'s chopped labels persist in the passing tree** — WHO now asserts a table whose top-level
  header nodes read `'Z-s'`, `'res (weight'`, `'kg)'`. Structurally correct, textually wrong. This
  is a **known-bad text payload shipping as an assertion**, and it is the strongest argument for
  prioritising `R154` next. It must be named in the `R45` closing row, not left implicit.

## 10. Residue raised by this spec

None new. `R154` and `R62` are cited, both already open.
