# Evidence — R255's second reading is not thrown away, and there is sometimes a third

**Serves:** maintenance — [[R255]] is named by no `prog:blockedBy`, and neither is the row this
loop raises. Measured on `main` at `497156d`, 2026-09-18.

**Doc impact: none.**

---

## 1. What R255's row claimed, and what is refuted

The row, raised 2026-09-18, reads:

> *"With `BAML_LIVE=1` that is **two model calls per gridded region, and only the second one's
> result reaches the graph** …"*

**The second clause is REFUTED.** Both readings reach the graph, by different routes. The first
one reaches it through **continuation recognition**, because `Band.unshown` is an input to the
header/body split that recognition's own evidence is built from.

The rest of the row stands: `page_bands` does run twice, the partition measured identical, and the
live gate does make each run a model call per gridded region.

## 2. The chain, measured hop by hop

The recognition pass and the compile are two `page_bands` calls:

```
$ grep -rn "page_bands(" src/iladub/etkl/*.py | grep -v "def page_bands"
src/iladub/etkl/compile.py:875:    bands = page_bands(pdf_path, page_number, section_repair_bands=section_repair_bands)
src/iladub/etkl/document.py:1437:        bands = page_bands(pdf_path, p)
```

`page_bands` is where the NEURAL reading happens — `compile.py:479-507`, one ask per gridded band,
gated by `baml_reader_available()`:

```python
    for i, band in enumerate(bands):
        reg = _classify(band)
        if reg.grid is None:
            continue
        found = region_unshown(pdf_path, page_number, band, reg.grid, reader)
        if found:
            bands[i] = _replace(band, unshown=tuple(sorted(found)))
```

So the question is whether the recognition caller consumes `unshown`. **It does**, through four
hops, every one of them in the shipped path:

| # | hop | site |
| --- | --- | --- |
| 1 | `compile_document`'s recognition loop calls `_recognition_blocks(bands)` | `document.py:1439` |
| 2 | which calls `leaf_block(band)` per band | `document.py:611` |
| 3 | which calls `header_body_split(band, grid)` | `document.py:322` |
| 4 | which passes **`unshown=band.unshown`** into the typed-cell evidence graph | `headers.py:111-112` |

and `grid_evidence` types those addresses `tab:UnshownInk`, which `vocab/ontology/tab.ttl` gives
`tab:datatypeAbstains true` — so they are read **out of every homogeneity judgement**
(`celltype.py:138-170`, its own docstring). Homogeneity is exactly what `header-body-split.rq`
decides the split on.

**The consequence:** reading #1 can move the header/body split, which moves `leaf_cells`, which is
the evidence `is_continuation` and `licence_evidence` judge — and a licensed pair produces the
**carried reading**, which `compile_document`'s own comment at `document.py:1431-1434` calls *"an
INPUT to that compile"*. Reading #1 therefore reaches the graph one page later, through the
carriage, while reading #2 reaches it directly.

**This was found by attempting to assert the opposite.** The draft of this evidence claimed the
recognition pass provably never consumes `unshown`, on the strength of a `grep` for `.unshown`
whose hits all looked like compile-path modules (`matrix.py:135`, `rowheaders.py:34`,
`headers.py:112`, `celltype.py:138`). `headers.py:112` is the one that is **also** on the
recognition path, and only opening it said so.

## 3. There is sometimes a THIRD reading, and it is the one that decides an adoption

A page that enters section repair is compiled a second time:

```
$ grep -rn "section_repair_bands" src/iladub/etkl/document.py
1501:    # still-escalated members (pass-2 compile_tables with `section_repair_bands`, under the
1538:                              section_repair_bands=candidates)
```

`document.py:1534-1538` calls `compile_tables` again for the same page, which calls `page_bands`
again — a **third** independent reading of that page's unshown ink. The adoption decision at
`document.py:1541-1545` then compares pass-1's region report against pass-2's:

```python
        for idx in sorted(candidates):
            r2 = rep2.regions[idx]
            if r2.verdict == "asserted" and r2.table_uri is not None:
```

**So under `BAML_LIVE` the adoption comparison is not a controlled A/B.** Pass 1 and pass 2 can
differ because the *reader* differed, not because section repair helped — and the 2026-09-18
grain-of-the-ask evidence measured that reader returning three distinct regimes across nine
readings of one band (§ 9 of that file). Raised as a row of its own; it is a different subject
from R255's cost.

## 4. What this costs, stated as structure rather than as a rate

Per page, with the live gate on: **2 model calls per gridded band**, and **3** for a page that
enters section repair. No figure for how many pages that is on the corpus is given here, because
this loop ran no live compile — the counts above are read off the call graph, and the only live
figures available are the previous loop's, which its own handoff § 3 forbids quoting as rates.

## 5. What is NOT measured, and must not be asserted

- **Whether reading #1 has ever actually changed a split, a licence or a carriage.** The path is
  live and the input is consumed; no run has been instrumented to show the two readings
  disagreeing at that seam. It is a mechanism, not an observed effect.
- **Whether the two partitions are always identical.** R255 measured them identical on
  graincorp-capacity. The recognition call passes no `section_repair_bands` and the compile call
  may pass some, so identity is not structural.
- **Any frequency.** One document, one call-graph reading, no live run in this loop.
- **The remedy.** Four are visible (read `unshown` out of the recognition path; a per-page cache;
  pass the band list into `compile_tables`; a flag suppressing the ask for the recognition call)
  and **none is evaluated here** — each trades against `page_bands`' own stated contract that
  recognition must read *the same bands* the compile reads (`compile.py:380-384`).

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
