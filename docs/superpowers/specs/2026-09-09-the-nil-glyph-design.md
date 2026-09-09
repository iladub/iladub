# Spec — the nil glyph: `—` is a missing value, and its spellings belong in the ontology

**Residue:** [[R167]] (`docs/superpowers/residues-open.md:120`).
**Written 2026-09-09**, off `3fe0ce2`, branch `r167-the-nil-glyph`. No code written yet.

**Doc impact: increment.** `tab:Blank`'s published `rdfs:comment` enumerates the nil spellings in
prose and is about to become false; the increment is that enumeration moving into triples.

---

## 1. The subject, and what R167 actually claims

`celltype.is_blank` (`src/iladub/etkl/celltype.py:67-72`) recognises three spellings of a missing
cell — `''`, `(blank)`, and the ASCII hyphen `-` — so `_cell_datatype('—')` returns `tab:Text`.
The em-dash U+2014 is US-GAAP's nil glyph and is the typographically-correct spelling of the `-`
that `is_blank` already accepts.

The consequence R167 measured is not cosmetic. `tab:Blank` carries `tab:datatypeAbstains true`
(`vocab/ontology/tab.ttl:297`), and every homogeneity derivation drops abstaining cells:

```
vocab/queries/stub-data-split.rq:17   FILTER NOT EXISTS { ?craw tab:datatypeAbstains true }
vocab/queries/stub-data-split.rq:20   } GROUP BY ?dcol HAVING(COUNT(DISTINCT ?ct) = 1 && SUM(IF(?ct = tab:Text, 1, 0)) = 0)
```

So a nil cell typed `tab:Text` does not abstain — it votes, and one vote disqualifies its whole
column from the data suffix. R167 measured that at `c9e6941`: apple p2's merged reading returns
`k=2` instead of `k=1` and `matrix_body_start` 2 instead of 3, on the strength of a single cell.

## 2. The population, MEASURED 2026-09-09 at `3fe0ce2` — and it is ONE

Every lone dash-family glyph standing as its own word, over all seven tracked corpus documents
(`pdfplumber.extract_words`, the eight Unicode dashes `- ‐ ‑ ‒ – — ― −`):

```
apple-fy2026q3-statements.pdf     p2  EM-DASH      U+2014  x1
bfs-population-bilan-2023.pdf     p5  HYPHEN-MINUS U+002D  x42
bfs-population-bilan-2023.pdf     p6  HYPHEN-MINUS U+002D  x1
cbh-stem-2026-08-03.pdf           p0  HYPHEN-MINUS U+002D  x5
graincorp-stem-2026-07-31.pdf     p0  HYPHEN-MINUS U+002D  x6
graincorp-stem-2026-07-31.pdf     p1  HYPHEN-MINUS U+002D  x10
ons-index-of-services-2026-02.pdf p4  HYPHEN-MINUS U+002D  x4
TOTAL: EM-DASH 1, HYPHEN-MINUS 68, every other dash 0
```

**One em-dash, zero en-dashes, and the other 68 are the ASCII hyphen `is_blank` already accepts.**
This is the first honest thing this spec has to say, and it sizes the loop: the corpus cannot show
this fix paying off, because the corpus contains one instance of the defect.

**And that one instance is INERT today.** Compiling apple page 2 at `3fe0ce2` and searching the
emitted graph for any literal containing U+2014 returns **0 hits**: the cell sits in a band that
escalates, so no wrong assertion crosses the membrane today.

```
page 2: score=0.05263157894736842 asserted=6 escalated=108
  band 0: ignored    (fewer than 2 lines)      band 4: escalated  REGION_TILING_FAILED
  band 1: ignored    (fewer than 2 columns)    band 5: escalated  REGION_TILING_FAILED
  band 2: escalated  MATRIX_AMBIGUOUS          band 6: asserted   cells=3
  band 3: escalated  REGION_TILING_FAILED      band 7: escalated  REGION_TILING_FAILED
```

**What this loop is therefore NOT allowed to claim:** that it moves a corpus score, repairs a
reading, or closes anything downstream. R167's own row says so — *"fixing it alone closes nothing"*,
because apple p2 refuses at the next stage on [[R162]], which is ruled NEURAL. This loop closes
R167 and nothing else.

## 3. The blast radius, ENUMERATED (not read from one file)

R167's row names *"a one-line change to a function four modules read (`feed.py:222`,
`datagrid.py:274,331`, `celltype._cell_datatype`)"*. The module count is right and **the call-site
list is not** — `datagrid.py:274` is a comment, and four call sites plus a whole module are missing:

```
$ grep -rn "is_blank" --include='*.py' src | grep -v '^src.*def is_blank'
src/iladub/etkl/celltype.py:78          _cell_datatype            — the typing itself
src/iladub/feed.py:32,222               drops blank-text cells
src/iladub/etkl/unitmarker.py:25,43     not is_blank(t) and is_currency_glyph(t)     ← module R167 missed
src/iladub/etkl/datagrid.py:40,331      row signature ("Blank" literal)
src/iladub/etkl/datagrid.py:443,517     column family sets                            ← missed
src/iladub/etkl/datagrid.py:525,563     refusing / occupied                           ← missed
```

**Eight call sites in four modules.** All three importers use `from .celltype import is_blank`, so
the name is bound at import in each module — **monkeypatching `celltype.is_blank` reaches only
`_cell_datatype`**. Any instrument that wants a before/after reading must therefore compile the two
readings in **two processes** against two trees, never by patching one. (This is the trap
`scripts/entry_cell_diff.py` avoids for a different function by patching a module-global that *is*
looked up late; that technique does not transfer here.)

Downstream, the flip is Text → abstaining wildcard, in: `stub-data-split.rq`, `header-body-split.rq`,
`looks-transposed.rq`, `transpose-coherent.rq`, `unit-marker-column.rq`, `orientation.py`,
`headers.py`, and `datagrid._ABSTAIN`.

## 4. The fork: where the spelling set lives

**(a) Python only** — add `—`/`–` to `is_blank`'s literal comparison. One line. Meets R167's close
criterion as written.

**(b) The ontology declares the spellings; `is_blank` reads them.** RECOMMENDED, and the reason is
not aesthetic — it is that **(a) ships a contradiction**. `tab:Blank`'s published comment already
enumerates the set:

```
vocab/ontology/tab.ttl:261
    "A genuinely-missing cell: empty, the self-declaring '(blank)', or a lone '-'."
```

That sentence is CC-BY published contract text. Under (a) it becomes false the moment the code
accepts a fourth spelling, and the repo's own precedent in the *same file* rules against leaving a
rule in two places:

```
vocab/ontology/tab.ttl:281 (tab:CellDatatypeFamily)
    "The grouping is declared here rather than repeated inside each query, so the rule is
     published with the ontology and a new member is one triple rather than five query edits."
```

`celltype.py` already parses `tab.ttl` at import (`_ONT`, `_DATATYPE_DECLARATIONS`, lines 87-97)
for exactly this reason, so reading a spelling set costs a filter over a graph that is already in
memory — no new I/O, no new import cost.

**Gate classification (CLAUDE.md §8).** Recognising a cell's raw datatype from its lexical form is
**PROCEDURAL**, and stays so: it is raw extraction, source → typed RDF fact, already justified in
`celltype.py`'s module docstring, and the *decisions* built on it remain AXIOM in `vocab/queries/*.rq`.
Arm (b) does not change that classification; it moves the **data** the recogniser reads out of Python
and into the published ontology, which is the direction §8 points. Neither arm introduces a tuned
constant: the set is a closed, decidable list of typographic spellings, not a tolerance.

**Scope of (b), stated so it cannot creep:** the empty/whitespace cell is NOT a spelling and is not
declared — an empty cell is the absence of ink, and stays a structural test in code. What moves into
triples is the *marker* set only: the two already recognised (`(blank)`, `-`) plus the two this loop
adds (`–`, `—`), four in all.

## 5. The oracles — named before the design, and every one falsifiable

| # | oracle | falsified by |
| --- | --- | --- |
| **O1** | `_cell_datatype('—')` and `_cell_datatype('–')` are `tab:Blank`; `_cell_datatype('-')` still is | reverting the spelling addition → RED |
| **O2** | The spellings the code accepts are **exactly** those `tab.ttl` declares — no Python-side literal outside the declared set | deleting one `tab:nilSpelling` triple → RED (this is what makes arm (b) real rather than decorative) |
| **O3** | A cell whose text is a dash **inside** other text (`'2020—2024'`, `'a — b'`) is NOT blank | broadening the comparison from equality to containment → RED |
| **O4** | **Whole-corpus verdict diff, two processes, before vs after**: every one of the 27 page readings is byte-identical except where a lone `—` is present | a moved score anywhere but apple p2 |

**O4 is the load-bearing one, and §2 tells you what it will say**: the em-dash cell is on an
escalated band, so the predicted result is **27 of 27 identical, including apple p2**. That is a
prediction that can fail — if any reading moves, the flip has reached a path §3's enumeration did
not anticipate, and the loop stops to explain it rather than re-baselining.

**O4 is graded PROPOSED.** It has not been run.

## 6. What is NOT done

- **[[R162]] is untouched** (unruled header labels are words, NEURAL). Apple p2 still refuses.
- **[[R166]]'s p2 half is untouched.** Free measurement, recorded here because §2's probe produced
  it: apple p2 band 6 is the page's ONLY asserted band (3 cells) at `3fe0ce2` — R166's live half is
  still live, and its p0 half is still disposed of by [[R165]].
- **[[R78]] stays distinct**: `..`, `n/a` and friends are *ambiguous* suppression markers whose value
  is unknown. The em-dash is decidable from format alone. Nothing here licenses widening `is_blank`
  toward a keyword list, and O3 is the guard that says so.
- **No new SHACL shape.** `tab:nilSpelling` is read by the recogniser, not validated at the membrane;
  a shape over it would validate the ontology against itself.
