# The label cell that cannot be found — design

**Topic:** [[R177]], and the measurement that promoted it from a provenance gap to the **blocker of
[[R178]]'s disposal**.

**Written 2026-09-07**, in the loop that ran action **5b** of
`docs/superpowers/2026-09-07-r176-handoff.md`.

**Doc impact: none.**

---

## 1. What was measured, before anything was designed

R178's row demanded one thing first: *run `scripts/unbooked_ink_fate.py` over the whole corpus and
READ the orphan texts, before designing.* That was done. The driver is
`scripts/unbooked_ink_fate_corpus.py`; one run, 27 pages, 7 documents, ~9 min.

### 1.1 What the unrepaired instrument reported — and why it was wrong

**Read § 1.3 before believing anything in this subsection.** It is kept as written because the
correction is the finding.

The row predicted the orphan population was *"small and caption-shaped"* — 3 words of `Year: Month`
in 1 document, generalising to a caption rule at the matrix site. The first run said otherwise:

```
$ PYTHONPATH=src python3 scripts/unbooked_ink_fate_corpus.py     # BEFORE the repair
pages measured                 : 27
total orphan words             : 111          in 3 of 7 documents, on 5 pages
```

and the words looked like four unrelated shapes:

| where | words | what the orphan text appeared to be |
| --- | --- | --- |
| who-wfa p0/p1/p2, band 2 (or 1) | 3 | `Year: Month` — the axis caption R178 was raised from |
| who-wfa p0/p1 bands 3+5, p2 band 2 | 65 | a **whole data row**: `0: 7 7 0.1134 8.2970 0.10902 5.9 …` |
| ons p4 band 2 | 17 | a **footnote sentence**: `1. Revisions are rounded to one decimal place …` |
| graincorp-stem p0 band 2 | 26 | **header words + a date banner**: `Friday, 31 July 2026 Date of Grain …` |

On that reading the caption was 2.7% of the population it was proposed to explain, the 65 were
[[R166]] at a new position, and R178's frame was refuted. **All three conclusions were artefacts of
the instrument**, and § 1.2 is why.

### 1.2 …but the number cannot be trusted, and that is this loop's subject

The prober decides an orphan by **containment in an emitted cell's bbox**. A `tab:LabelCell` with
no `tab:hasBBox` is skipped and counted as `no bbox: N`, so every word that reading carried into
such a cell is **indistinguishable from ink the reading dropped**.

The correlation is not partial. It is exact:

```
pages with bbox-less LabelCells: 5   [graincorp-stem p0 (17), ons p4 (2),
                                      who-wfa p0 (24), p1 (24), p2 (12)]
pages with orphan ink          : 5   [graincorp-stem p0 (26), ons p4 (17),
                                      who-wfa p0 (27), p1 (27), p2 (14)]
SAME SET: True
```

**Every orphan word in the corpus sits on a page where label geometry is missing, and no page with
complete label geometry has a single orphan.** 79 bbox-less LabelCells; 111 orphan words. Until
those 79 carry their boxes, R178's population is unmeasured — it is somewhere between 0 and 111,
and its *shape* (§ 1.1's four rows) may be an artefact of the instrument rather than a fact about
the reading. graincorp-stem is the clearest case: `LabelCells=0 (no bbox: 0/17)` — the entire label
channel of that page is invisible to the prober, and its 26 "orphans" read exactly like the header
labels a hierarchical reading would have carried.

**Ordering ruling: R177 closes before R178 is designed.** Not a preference — R178's own prescribed
disposal runs on an instrument R177 blinds.

### 1.3 The repair settles it: 99 of the 111 were never dropped

Same command, same corpus, after § 3's repair:

```
$ PYTHONPATH=src python3 scripts/unbooked_ink_fate_corpus.py     # AFTER the repair
pages with bbox-less LabelCells: 0 []
total orphan words             : 12          in 2 of 7 documents, on 4 pages
```

**111 → 12.** Every word of the footnote sentence and every word of the "data rows" was carried
label ink the prober could not see:

| band | before | after |
| --- | --- | --- |
| ons p4 b2 (the footnote) | `label=0  orphan=17` | `label=17 orphan=0` |
| who-wfa p0 b3 / b5 (the "data rows") | `label=0  orphan=13` each | `label=13 orphan=0` each |
| graincorp-stem p0 b2 | `label=0  orphan=26` | `label=17 orphan=9` |
| who-wfa p0 b2 (the caption) | `label=20 orphan=1` | `label=20 orphan=1` — unchanged |

So § 1.1's four shapes collapse to two, and R178's own frame survives better than its refutation did:

* **3 words, `Year: Month`** on who-wfa p0/p1/p2 — the axis caption, exactly the row's original
  sample, now 25% of the population rather than 2.7%.
* **9 items on graincorp-stem p0** — a date banner (`Friday, 31 July 2026`) plus eight uncarried
  column-header fragments (`Date of Grain`, `Unique Slot`, `Loading Date`, `Nomination Time` ×2,
  `Nomination Date` ×2, `Loading`). Not captions, and not [[R166]] either: the band's other 17
  header cells *were* carried.

**This is the loop's headline.** R178's row was right that the disposal had to be run first and
right that it was cheap. It could not know that running it on the unrepaired instrument would have
sent the next loop to design a footnote rule and an [[R166]] re-frame for 99 words that were never
dropped at all. The row's prescribed disposal was sound; the instrument it prescribed was not.

## 2. R177's own prescribed remedy is also REFUTED

The row says: *"`nd.x0/top/x1/bottom` are already in hand at that site, so nothing has to be
recomputed."* They are not.

```
$ sed -n '136,144p' src/iladub/etkl/headers.py
@dataclass(frozen=True)
class HeaderNode:
    level: int
    covers: tuple[int, ...]
    text: str
    parent: int | None
    center_x: float | None = None
    ambiguous: bool = False
    ambiguous_flank: int | None = None
```

`HeaderNode` carries **`center_x` and nothing else geometric** — no bounds, no page. The row
conflated it with `RowHeaderNode` (`src/iladub/etkl/rowheaders.py:72-82`), which *does* carry
`x0, top, x1, bottom, page`, and which is why `assert_row_hier_region`
(`src/iladub/etkl/holon.py:289-294`) can write a bbox and `assert_hier_region` cannot.

So the repair is not a four-line addition at the emitter. The geometry must be **carried through the
node** from the site that already holds it.

## 3. The repair

### 3.1 `assert_hier_region` is the sole offender — measured, not assumed

```
$ grep -n "TAB.LabelCell" src/iladub/etkl/holon.py
140  190  252  284  336  535
```

Of those six emitters, five write `tab:hasBBox` within twelve lines (`:144` `:194` `:262` `:294`
`:346`); `:535` writes `RDF.type`, `TAB.hasCell`, `TAB.cellText`, `TAB.hasLabel` and stops. Its own
comment claims otherwise — *"LabelCell carries the header text + provenance context"* — which is
the defect stated in the code and not noticed.

### 3.2 Where the geometry already is

`_tree_from_rows` builds every node from a `SourceCell` (`src/iladub/etkl/cells.py:19-27`), which
carries `text, x0, top, x1, bottom, page, words`. The construction site
`src/iladub/etkl/headers.py:437` already reads `cell.x0`, `cell.x1` and `cell.text` from it. The
four remaining bounds and the page are one attribute access away and are **thrown away today**.

### 3.3 The change, and why it is safe

Line numbers below are **post-change** (`headers.py:458,489`; `holon.py:554`), re-measured after the
edit rather than before it — CLAUDE.md § Plan authoring discipline rule 7. The code comments cite
**symbols** instead, which removes the hazard rather than guarding it.

1. `HeaderNode` gains `x0, top, x1, bottom: float | None = None` and `page: int | None = None`,
   **appended after `ambiguous_flank`** so every existing positional construction keeps its meaning
   (23 of them across `tests/etkl/`).
2. `_tree_from_rows` (`headers.py:458`) populates them from `cell`, which already had them in hand.
3. The node-linking rebuild (`headers.py:489`) — of the **seven** sites that rebuild a `HeaderNode`,
   the one that listed its fields explicitly — becomes `replace(n, parent=parent_idx)`, so it can
   never again drop a field added later. The other six (`headers.py:326,368,373`;
   `span.py:29,33,36`) already use `replace` and need no edit.
4. `assert_hier_region` (`holon.py:554`) writes `tab:onPage` and `tab:hasBBox`, **only when the
   geometry is present** — a presence test, never an inference from absence (§ Core design
   principles 7).

The one node with genuinely no geometry is `span.py:38`'s synthetic flank filler
(`HeaderNode(0, (flank,), "", None)`), which stands for a column that has no header ink at all.
Under (4) it emits a `LabelCell` with **empty** `cellText` and no bbox, exactly as today — the
honest reading, and the reason the writer is conditional rather than unconditional. That its text is
empty is not incidental: `tab:WrappedCellShape` requires non-empty `cellText` *on cells that carry a
box*, so an unconditional writer would have turned this node into a membrane violation and, through
`region_tiles`, into a refusal to assert (§ 4.1).

### 3.4 Classification (§ Core design principles 8)

**PROCEDURAL — raw extraction.** The values are pdfplumber word bounds becoming typed RDF facts;
there is no evidence graph to derive them from, because this *is* the step that puts them in one.
Irreducible to AXIOM for that reason, and irreducible to NEURAL because nothing is being judged: the
node's bounds are already decided by the time the emitter runs. It carries **no constant and no
tolerance**. Five sibling emitters are PROCEDURAL on identical grounds; this change makes the sixth
match them rather than introducing a new class of code.

### 3.5 What the membrane says about it — and it says nothing

```
$ grep -rn "LabelCell" vocab/shapes/*.ttl
vocab/shapes/tab-shapes.ttl:294:  … FILTER NOT EXISTS { ?lc a tab:LabelCell ; tab:cellText ?lt … }
```

`tab:EntryCellPhysicalShape` (`vocab/shapes/tab-physical-shapes.ttl:13-19`) requires
`tab:hasBBox minCount 1` on every `tab:EntryCell`. **No shape requires it on a `tab:LabelCell`**, so
these 79 cells are not a membrane violation — they violate § Core design principles 6
(provenance-to-the-page) with nothing validating it. R177's row asked whether a shape existed; the
answer is no, which makes this a provenance gap and *not* larger than one.

**Adding that shape is deliberately NOT in this loop** — see § 6.

## 4. Oracles

| # | oracle | falsifies |
| --- | --- | --- |
| **O1** | `unbooked_ink_fate.py`'s own `no bbox:` counter reaches `0/0` on who-wfa p0/p1/p2, graincorp-stem p0 and ons p4 | the emitter still drops geometry |
| **O2** | unit tests on the `#htable` fixture: every `tab:LabelCell` reachable from a `tab:HeaderNode` carries a `tab:hasBBox` **and** a `tab:onPage`; the boxes are distinct and non-degenerate; **and a node stripped of its geometry stays boxless** | the emitter writes a box that is not the node's, or invents one it does not have |
| **O3** | the corpus orphan total, re-measured after the repair | § 1.2's claim that the 111 are confounded |
| **O4** | full `tests/etkl/` suite | the field addition breaks a positional construction somewhere |

**O3 is a measurement, not a pass/fail.** Whatever it returns is R178's real population and is
recorded as such — a *fall* confirms § 1.2, and *no fall at all* would mean the 111 were true
orphans all along and the correlation of § 1.2 is a coincidence across 5 pages. Either way R178 is
re-raised on a number rather than on a sample of one document.

### 4.1 RESULTS

| # | result |
| --- | --- |
| **O1** | **PASS.** `total bbox-less LabelCells: 79 → 0`; `pages with bbox-less LabelCells: 5 → 0`. |
| **O2** | **PASS.** `tests/etkl/test_hier_label_cells_carry_geometry.py`, **4 passed** — three on the positive half, one pinning that a geometry-less node stays boxless. Five falsifications, in the loop handoff. |
| **O3** | **111 → 12 orphan words.** § 1.3 carries the split and the ruling. § 1.2's confound claim is CONFIRMED — 99 of 111 were carried ink. |
| **O4** | **PASS.** full `tests/etkl/` suite, corpus included: `893 passed, 2 skipped, 1 xfailed in 40:36`; nothing re-baselined. |

**And the thing O1–O4 do not say, measured separately because it is the risk this change carries.**
A repair that only adds triples can still move a reading, because `compile.py:1166` runs
`region_tiles(scratch)` — the tiling SHACL membrane — over the very graph `assert_hier_region`
writes, and `tab:WrappedCellShape` (`vocab/shapes/tab-physical-shapes.ttl:26-31`) fires *only when
`tab:hasBBox` is present*. Giving 79 label cells a box brings them under a shape they had escaped by
omission. So every page's verdict was diffed, not assumed:

```
$ diff <(grep -E "^===|^page " BEFORE | sed 's/ | EntryCells.*//') \
       <(grep -E "^===|^page " AFTER  | sed 's/ | EntryCells.*//') && echo IDENTICAL
IDENTICAL
```

All 27 pages: same `score`, same `asserted`, same `escalated`. The new boxes satisfy
`WrappedCellShape` because the cells they land on carry non-empty `cellText` — which is exactly what
that shape checks, and why the one node with no text (`span.build_reading`'s flank filler) is
also the one node § 3.3 leaves boxless.

## 5. What is NOT done

- **R178 is not repaired.** Its population is re-measured and its row re-raised; carrying orphan ink
  into a structure is a reading change and does not belong in a provenance diff.
- **No `LabelCellPhysicalShape` is added.** § 3.5 shows the membrane is silent here, and closing that
  silence is a membrane decision with its own blast radius (every LabelCell in every shipped graph,
  including `span.py:38`'s legitimately boxless filler, which such a shape would reject). Raised as a
  residue, not folded in.
- **`center_x` is not removed**, though the four new bounds subsume it. Two consumers read it
  (`headers.py`'s flank resolution, `span.py`) and rewriting them is unrelated work.
- **The five sibling emitters are untouched.** They already write what this one now writes.
