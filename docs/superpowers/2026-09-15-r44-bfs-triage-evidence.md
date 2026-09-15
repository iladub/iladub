# Evidence — R44's premise re-measured: bfs at HEAD, four weeks after the only census that ever read it

**Serves:** prog:criterion:etkl:05 — bfs. R44 gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-15. **Tree:** branch `r44-bfs-triage`, cut from `main` at `22a8264`.
**No shipped file edited. No behaviour changed.** One instrument, measurement only.

**Doc impact: none.**

---

## 1. What was asked, and why this document exists

[[R44]] has never been worked. Its own closure column names the shape of the work — *"its own
reading loop: triage the three escalation reasons separately (kind support, tiling, round-trip)
against the document's actual layout before deciding which, if any, share a root cause"* — and the
maintainer chose it as this loop's subject on the arc evidence: **R44 gates 5 unmet criteria, more
than any other row in the register** (`arc-reach.rq`, rendered 2026-09-15).

Before triaging three reasons, this loop measured whether the row still describes the document.
**It does not.** The row is dated 2026-08-04 and every figure on it was read once, at
`820ab24` on 2026-08-20, by `docs/superpowers/2026-08-20-escalation-reason-census.md`.

**Nothing has re-run a per-reason census on bfs since.** The later bfs figures a reader might
mistake for one — `B=10 C=10` (2026-08-31), `superseded=4 live=6` (2026-09-14) — are *decision*
censuses, counting decision holons, not reason breakdowns. That absence is itself a measurement and
is the reason this loop is a measurement and not a repair.

## 2. The instrument, and the control that caught it

`scripts/` gains nothing here; the driver reuses the shipped `corpus_verdict_snapshot.snapshot()`
rather than re-deriving a reading, so what is counted is what the compiler reports.

**The control failed on its first run, and that is the part worth recording.** Per the 2026-09-15
repair #3 (*every instrument carries a control that must find a known positive*) it asserted three
figures measured independently of it by the R224/R225 closure: bfs scores `0.4033`, page 5 is
adopted, page 5 asserts 404 cells. Legs two and three passed. **The score leg failed against a
correct measurement** — the literal `0.4033` was two readings stale.

So the control was repaired to read `tests/corpus-manifest.ttl`'s own `cor:reading` log instead of
a hard-coded number. **A control pinned to a literal goes stale exactly as the row it is checking
did** — which is the defect `cor:reading` exists to prevent, committed inside the instrument built
to find that class of defect. After the repair all three legs pass and the run reports *which*
recorded reading it matched and whether that reading is the newest.

## 3. The score ladder — measured, and the row is four readings behind

Every score this repo has recorded for bfs, oldest first, read from `tests/corpus-manifest.ttl`
by the instrument itself:

```
0.3438                 2026-08-20  820ab24
0.3464447806354009     2026-09-05  (no commit)
0.40331491712707185    2026-09-08  9eb5cd0
0.40331491712707185    2026-09-12  b2bdbbe
0.889055472263868      2026-09-14  e9f772f
0.8850746268656716     2026-09-14  (no commit)   <-- today's reading
```

Today's compile reads **`0.8850746268656716`**, byte-identical to the newest recorded reading, and
confirmed independently by the shipped oracle — `test_expected_verdict[gov-stats/bfs-population-bilan-2023.pdf]`
prints `score=0.8851 pages=7 chains=[1, 1, 1, 1, 1, 1]`, **1 passed in 69.74s**.

**R44's row says `0.3438`.** The row is not slightly stale; it is stale across a 0.54 rise that
R225's D2 delivered and that no one attributed to R44's subject matter at the time.

**The oracle passing is not evidence the document is read well.** bfs carries
`cor:expectedVerdict cor:Unadjudicated` and **no `cor:scoreFloor`** (`tests/corpus-manifest.ttl:120`),
by an explicit 2026-08-20 ruling: *"cor:scoreFloor is a regression guard, so nothing in the
vocabulary stops a floor being pinned at 0.3438 and this document being called met without one
glyph of it being read correctly. That is refused here explicitly, on the standing rule that a bar
is never lowered to meet it. Held."* The test passes at any score, and would have passed at 0.34.

## 4. A second finding, not sought: every line citation in the `tab` rung is stale

While locating the three reasons' emission sites — R44's triage needs them — **all ten of the
`tab` rung's criteria statements were found to cite a line that does not carry the thing it names.**
Measured by printing each cited line at `22a8264`:

| criterion | reason | cited | what is actually there | where the reason really is |
| --- | --- | --- | --- | --- |
| `tab:01` | MULTI_TABLE_AMBIGUOUS | `compile.py:596` | `cand = os.path.join(d, "vocab")` | `:849`, `:852`, `:859` |
| `tab:02` | REGION_TILING_FAILED | `compile.py:656` | a comment about promotion decisions | `:918`, `:1120`, `:1334` |
| `tab:02` | REGION_TILING_FAILED | `compile.py:763` | `_shapes_for = {"tab": …}` | as above |
| `tab:02` | REGION_TILING_FAILED | `compile.py:939` | round-trip token booking | as above |
| `tab:03` | TRANSPOSED | `compile.py:688` | a comment about `tab:DataGrid` | `:958`, `:965`, `:966` |
| `tab:04` | ROW_GROUP_AMBIGUOUS | `compile.py:739` | a comment about a crash | `:1024`, `:1031`, `:1032` |
| `tab:05` | MATRIX_AMBIGUOUS | `compile.py:830` | `graph = Graph()` | `:1224`, `:1231`, `:1232` |
| `tab:06` | MERGE_AMBIGUOUS | `compile.py:911` | `if tiles is not None:` | `:1305`, `:1312`, `:1313` |
| `tab:07` | KIND_NOT_SUPPORTED | `compile.py:978` | `from .tiling import region_tiles` | `:1373`, `:1381`, `:1383` |
| `tab:08` | DATAGRID_RESIDUE | `compile.py:1145` | an f-string fragment | `:1597`, `:1599` |
| `tab:09` | ROUND_TRIP_FAIL | `holon.py:493` | a docstring line in `emit_ignored_band` | `:536`, `:545` |
| `tab:09` | ROUND_TRIP_FAIL (cell) | `holon.py:55` | a blank line | `:59`–`:95` |

**This is [[R235]]'s class one layer up, and worse in one specific way.** R235 was a stale citation
in a *docstring*. These are inside `prog:statement` string literals — **the criteria's own
operative text**, which is what a future loop reads to learn what it must dispose of. `tab:06` is
the rung's one met row, and its own falsification evidence cites `compile.py:911` for the literal
it inverted, so that citation was true when written: this is drift, not an authoring error.

**Nothing covers it, by design.** `tests/source_citations.py` reads `.py`/`.ttl`/`.rq` but only
*comment lines*, and states outright: *"WHAT THIS DOES NOT CHECK: whether a citation is CORRECT."*
A citation inside a string literal is outside its lexicon twice over. This is recorded as a finding
with its measurement, not proposed as a lint — whether it earns one is a separate judgement, and
[[R188]] is the standing ruling against gates calibrated to fire on nothing.

## 5. The reason tally at HEAD — and the triage R44 asked for

Every reason-bearing region, with its verdict, run at `22a8264`:

```
  p0 region0   escalated   UNSUPPORTED_TABLE  KIND_NOT_SUPPORTED
  p4 region0   escalated   UNSUPPORTED_TABLE  REGION_TILING_FAILED
  p5 region2   escalated   UNSUPPORTED_TABLE  ROUND_TRIP_FAIL
  p5 region7   escalated   UNSUPPORTED_TABLE  REGION_TILING_FAILED
  p5 region9   superseded  UNSUPPORTED_TABLE  ROUND_TRIP_FAIL
  p5 region10  superseded  UNSUPPORTED_TABLE  ROUND_TRIP_FAIL
  p5 region11  superseded  UNSUPPORTED_TABLE  ROUND_TRIP_FAIL
  p5 region12  superseded  UNSUPPORTED_TABLE  ROUND_TRIP_FAIL
  p5 region13  superseded  UNSUPPORTED_TABLE  KIND_NOT_SUPPORTED
  p5 region16  escalated   UNSUPPORTED_TABLE  DATAGRID_RESIDUE
  p6 region1   escalated   UNSUPPORTED_TABLE  KIND_NOT_SUPPORTED
  p6 region10  escalated   UNSUPPORTED_TABLE  KIND_NOT_SUPPORTED

reason                      2026-08-04   live   sup.  total   moved?
DATAGRID_RESIDUE                     0      1      0      1   MOVED
KIND_NOT_SUPPORTED                   2      3      1      4   MOVED
REGION_TILING_FAILED                 2      2      0      2   -
ROUND_TRIP_FAIL                      5      1      4      5   -
```

**The headline, and it is the opposite of what the score suggests: the 0.3438 → 0.8851 rise
repaired none of R44's three reasons.**

- **ROUND_TRIP_FAIL is unmoved at 5.** One still escalates; four were *superseded* by page 5's
  adoption. They went from visible to concealed, not from broken to fixed. The four are p5 regions
  9, 10, 11 and 12 — **the same four the 2026-09-14 decision census independently names** as the
  withdrawn `#region9/10/11/12-d4`, which corroborates this reading by a route that never touches
  this instrument.
- **REGION_TILING_FAILED is unmoved at 2** — p4 and p5, the chart captions with mangled glyph runs
  the 2026-08-20 adjudication describes.
- **KIND_NOT_SUPPORTED: the row's `2` was wrong when written.** The 2026-08-20 census and bfs's own
  adjudication both say **×3** (p0 the masthead, p6 ×2), and today's three live firings sit on
  exactly those pages. The fourth is p5 region13, superseded — new, and a consequence of adoption.
- **DATAGRID_RESIDUE ×1 is new**, on p5 region16: the residue adoption leaves behind. It is
  `tab:08`'s subject, and it arrived on bfs without any loop recording that it had.

**The triage answer R44's closure column asks for: the three reasons do NOT share a root cause.**
Round-trip failure is confined to p5 and is one mechanism (region-level, `holon.py:536`/`:545`);
kind-not-supported is a press-release masthead on p0 and two p6 bands; tiling failure is two chart
captions on p4 and p5. Three surfaces, three pages, no common cause — which is what the adjudication
guessed in 2026-08-20 prose (*"the surface is small and legible"*) and what nobody had re-measured
since.

**Two figures on the row are NOT reconciled here**, and are left open rather than explained away:
the row records **8** `RECORD_TABLE` regions asserting where HEAD reads **7** asserted plus 2
superseded, and it records `chains [1,1,1,1,1,1,1]` (seven) where HEAD reads six. The chain fall
7 → 6 is recorded at 2026-09-14 as D2's doing; the RECORD_TABLE count is not accounted for by
anything measured here.

## 7. A third finding, from a snapshot taken by accident

This loop's first command was `corpus_verdict_snapshot.py --help`. That script takes `argv[1]` as
its **output directory**, so the help request compiled all seven corpus documents into a directory
named `--help` — which is why the call hit its timeout. The directory was untracked junk in the
repo root and had to go; it was **read before being deleted**, because it is a valid whole-corpus
snapshot of the same unmodified tree.

Tallied by `(reason, verdict)` across all 7 documents, against the `FIRES n` comments the `tab`
rung carries:

| reason | the manifest says | HEAD live | HEAD superseded | total |
| --- | --- | --- | --- | --- |
| REGION_TILING_FAILED | FIRES 10 — apple ×8, bfs ×2 | 2 | 6 | **8** |
| MATRIX_AMBIGUOUS | FIRES 2 — apple only | **0** | 1 | **1** |
| KIND_NOT_SUPPORTED | FIRES 3 — **bfs only** | 7 | 1 | **8** |
| DATAGRID_RESIDUE | FIRES 1 — apple p1 | 4 | 0 | **4** |
| ROUND_TRIP_FAIL | FIRES 5 — bfs p5 | 1 | 8 | **9** |

**All five firing counts are stale, and two are wrong about which documents fire at all.**
`KIND_NOT_SUPPORTED` says *bfs only* while **ons fires 4 of its 7 live firings**; `ROUND_TRIP_FAIL`
says *bfs p5* while **ons carries 4**, a document the comment never mentions. This matters beyond
arithmetic: `tab:07` is blocked by [[R44]] and [[R71]], both bfs-shaped rows, while the majority of
its live firings are on a different document — so the blocking edges may be pointing at the wrong
place.

The three corpus-dead reasons (MULTI_TABLE_AMBIGUOUS, TRANSPOSED, ROW_GROUP_AMBIGUOUS) are still
dead at 0, and `tab:06` MERGE_AMBIGUOUS is still 0 — **the rung's one met row is unaffected**, which
is the check worth making before reporting any of this.

Raised as [[R237]], distinct from [[R236]]: that row is about the `file:line` citations in the same
block, this one about the counts.

## 6. What was wrong in this loop's own first reading, and how it was caught

The first version of the driver counted `verdict == "escalated"` alone and printed
**`ROUND_TRIP_FAIL 5 → 1`**, which reads as *four of the five round-trip failures are fixed*.

They are not. The shipped oracle's region dump — a path that is not this instrument — shows bfs
also carrying `('UNSUPPORTED_TABLE', 'superseded', 'ROUND_TRIP_FAIL')` **four times**, plus one
superseded `KIND_NOT_SUPPORTED`. A `superseded` report is a reading that page 5's adoption
**replaced**, not one that was repaired (`compile.py:547-552`): its ink moved to the grid region,
so the band's own record no longer describes what happened to it.

**Counting only live firings turns an adoption into a fix.** That is the previous loop's repair #4
— *a positive result is not self-interpreting* — recurring in the next loop, in an instrument
written by someone who had just read that sentence. The driver now counts both classes and prints
them apart, and § 5's table compares the row against the **total**, which is the like-for-like
figure: nothing was adopted on bfs when R44 was written, so both sides agreed then.

It is also the divergence apple's 2026-08-20 adjudication warned about in general terms — *"any
later criterion that counts this document must say which side it counts"* — landing on bfs, which
the 2026-09-14 decision census had already flagged as **the corpus's only document carrying live
and withdrawn escalations at once**.
