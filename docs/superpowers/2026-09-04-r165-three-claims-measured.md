# R165 — the three PROPOSED claims are MEASURED, and one of them refutes a line of the spec

**Date:** 2026-09-04. **Branch:** `one-band-in-page-bands`. **Measured at:** `2f55995`.
**No `src/` or `vocab/` file was changed by this loop.** The only tracked addition is
`scripts/doc_walltime.py`, the § C instrument, committed so its figures are re-runnable rather
than pasted. The baseline tree was verified clean before and after every measurement
(`git status --porcelain` → only the two pre-existing untracked `.github/` entries).

**Why this exists.** `docs/superpowers/2026-09-04-r165-preplan-spike-handoff.md` § 5 graded three
claims **PROPOSED** and ordered each MEASURED *before* the plan task resting on it was written.
This file is that measurement. **All three come back CONFIRMED** — which is itself the news, since
the two preceding measurement loops each returned a refutation — but two of them carry a finding
sharper than the claim, and one of those (§ A.2) **refutes a requirement the spec states in § 3.4**.

**Doc impact: none.** Evidence only. The `Doc impact: increment` the spec declares is still owed by
the plan that implements it.

---

## 0. The prototype, and what is NOT being measured here

Claims B and C are measured against the **same prototype** the predecessor spike built and
reverted — extracted from that document's Appendix (123 lines, `git apply --check` clean at
`2f55995`) and applied to a throwaway git worktree, never to the baseline tree. Its relation is
plain Python where the design requires a SPARQL derivation; that substitution is the predecessor's
§ 0 and it stands. Claim A is measured on the **clean** tree and needs no prototype.

**A trap the worktree exposed, which will bite the plan's executor.** `corpus/` is **gitignored**
(`.gitignore:52`), so a fresh `git worktree` has **no corpus at all** and every corpus-dependent
test **skips silently and reports green**. This was hit for real in this loop's measurement before
a symlink fixed it. This repo's habit is to execute plans in worktrees; a worktree without a
`corpus` symlink cannot falsify anything.

---

## A. The SPARQL derivation reproduces the Python relation — **CONFIRMED**

Instrument: `scratchpad/claim1/sparql_run_probe.py`, which **imports** `runs_subsumption` and
`sig_set` from the committed `scripts/band_run_census.py` rather than re-typing the relation, so
the Python side is provably the same instrument spec § 3.3's census used.

```
=== pages measured: 27
=== TOTAL RUNS  python=14  sparql(a)=14  sparql(b)=14
=== PAGES WHERE SPARQL != PYTHON: 0
```

14 runs, page-for-page identical, on all 27 pages of all 7 documents, under **both** candidate term
shapes of § Q-D D1 and **both** adjacency forms of § A.2 below. Spec § 3.4's derivation is
therefore expressible, and the § 3.3 census figures survive the change of engine.

### A.1 The one place the derivation can silently disagree, and no query can defend it

A band node emitted with **zero** rule-x facts makes both legs of the subsumption vacuously true,
so it joins **every** adjacent band in both directions:

```
synthetic graph: band0 xs={10,20,30}, band1 xs={} (node emitted anyway), band2 xs={10,20}
    derived runs    = [(0, 2)]        python relation = []
SAME, but band1 emits NO node at all (the honest-abstain emitter):
    derived runs    = []
```

No corpus band reaches it (`bands with rules but zero distinct rounded x: 0`) — `sig_set` returns
`None` only when `band.rules` is empty, and rounding cannot empty a non-empty set. **The protection
is entirely the emitter's honest abstain**, exactly as `sectiongraph.section_evidence` already does
with its `continue`, and `section-repeat.rq`'s header already states that contract for its own
emitter. This is an **emitter invariant, not a query one**, and it is the one thing in the
derivation a test must pin because the `.rq` cannot.

### A.2 **The spec asks for two incompatible things in § 3.4** — REFUTED, and the repair is measured

Spec § 3.4 requires the derivation to express adjacency as `?b = ?a + 1` **and** states, in bold,
*"It contains no numeric literal."* Those cannot both hold: `1` is a numeric literal, and
`vocab/queries/section-repeat.rq:15` makes *"this query contains no numeric literal"* a standing
property of the idiom § 3.4 says this loop copies.

Both forms were measured and **agree at 14/14**:

- **arithmetic** — `FILTER(?b = ?a + 1)` over `xsd:integer` band indices. Works, no cast needed.
- **literal-free** — the emitter emits the predecessor index as a *fact* (`tab:prevBandIndex`) and
  the query joins on it. **This is the form that matches the idiom**, and it is what the two shapes
  below use.

The plan takes the literal-free form and says so; the alternative is to weaken `section-repeat.rq`'s
standing property, which is not this loop's to do.

A **silent** failure mode was measured beside it: a band index emitted as a *string* returns `[]` —
an empty derivation, no error.

```
bandIndex=integer  arith(?b=?a+1)=[(1, 3)]   fact(prevBandIndex)=[(1, 3)]
bandIndex=bare     arith(?b=?a+1)=[(1, 3)]   fact(prevBandIndex)=[(1, 3)]
bandIndex=string   arith(?b=?a+1)=[]         fact(prevBandIndex)=[(1, 3)]
```

`Literal(i)` and `Literal(i, datatype=XSD.integer)` are the same term, so a bare literal is safe;
the honest emitter is `sectiongraph.py:205`'s explicit `XSD.integer`.

### A.3 Term equality, not value equality — a property of the EMITTER

`NOT EXISTS` matches by **term**, so `"10.0"^^xsd:decimal` and `"10.00"^^xsd:decimal` — the same
*value* — do not match, and mixing `xsd:decimal` with `xsd:double` for one value derives nothing:

```
band0=decimal band1=decimal  -> pairs=[(0, 1)]   (identical value sets)
band0=decimal band1=double   -> pairs=[]         (identical value sets)
lexical probe: '10.0' vs '10.00' (both xsd:decimal) -> pairs=[]
```

The shipped `Literal(Decimal(str(round(r.x, 2))))` idiom is lexically canonical across the whole
corpus, which is why the hazard is inert today:

```
total rule-x literals emitted: 3668   distinct VALUES: 286
values carrying MORE THAN ONE lexical form: 0
literals in exponent form: 0
```

Also measured, and worth recording because the spec inherits the rounding without justifying it
(§ 8): **the 2dp rounding changes the run set on 0 of 27 pages.** It is guarding a hazard that does
not currently fire.

### A.4 The two term shapes — both work; the cost difference is emission volume, not the path

| shape | build (27 pp) | query (27 pp) | total | worst page |
| --- | --- | --- | --- | --- |
| (a) new datatype property on the band node, no path | 0.0140 s | 0.2866 s | **0.3006 s** | 0.0194 s (bfs p6, 101 triples) |
| (b) real `tab:RuleSpan` nodes + property path, reusing `tab:ruleX` | 0.1038 s | 0.4972 s | **0.6010 s** | 0.0948 s (apple p0, 1869 triples) |

~11 ms/page vs ~22 ms/page. **Neither is a budget item** beside `page_bands`' 0.03–3.93 s/page.
Most of (b)'s 2.0x is that the `gridregion.py` idiom emits one `RuleSpan` per **rule**, not per
distinct x (1869 triples vs 101 on apple p0); a distinct-x variant would close much of the gap and
is **untested**. The cost is therefore *not* a reason to prefer (a) — the modelling argument is.

Construction note that does **not** separate the shapes: the two subsumption legs must sit inside
one `FILTER(... || ...)`, never as two `UNION` branches — a `UNION` branch is evaluated
independently, so `?a`/`?b` fall out of scope.

### A.5 The domain fork is WIDER than § Q-D D1 says, and the probe does not grade it

Measured controller-side on the clean tree:

- **`tab:bandIndex` has the same problem as `tab:ruleX`.** It is declared
  `rdfs:domain tab:SectionBand` (`vocab/ontology/tab.ttl:302`). Spec § 6's `run_evidence` contract
  — *"one `tab:RuledBand` per band … with its `tab:bandIndex`"* — therefore hits the D1 fork on
  **both** properties, not the one D1 names.
- **D1's own unmeasured item is answerable, and the answer is NO.**
  `scripts/probe_domain_range_agreement.py:265` builds its population from
  `compile_tables(...).graph` and nothing else, and `section_evidence` is reached only from
  `document.py:1481-1490` with its transient graph discarded. A run-evidence graph that is never
  `+=`'d into the compile graph is **outside** the probe's population. So the term-shape choice is
  a modelling-honesty decision, **not** a gate-passing one — which removes the argument D1 leans on
  and leaves the fork genuinely open.

---

## B. `test_datagrid.py:907` is fixture drift, not a loss — **CONFIRMED**, and the ink is accounted for

The fixture is **apple page 1**, the condensed consolidated balance sheet
(`tests/etkl/test_datagrid.py:22,905-906`). The test guards the datagrid fallback gate at
`compile.py:1040` (`asserted_total == 0 and escalated_total == 0`): appending a grid reading to a
page that already escalated would mask an honest escalation and double-count the same tokens on
both sides of the ratio (`compile.py:1030-1039`).

**Line 907 is a precondition, not a pin.** With it removed, `:908` (`on.score == off.score`) and
`:909` (`len(on.regions) == len(off.regions)`) both **pass** under the prototype.

| | BASELINE (8 bands) | PROTOTYPE (3 bands) |
| --- | --- | --- |
| region 2 | UNSUPPORTED_TABLE · asserted · 14 cells · ta 14 / te 0 | UNSUPPORTED_TABLE · asserted · **56** · ta **56** / te 0 |
| regions 3,4,5,7 | escalated · te **19 + 20 + 13 + 18 = 70** | — merged into region 2 — |
| page `asserted` / `escalated` | 14 / **70** | **56** / **0** |
| page score | 0.16667 | **1.0** |
| graph census | EntryCell 14, LabelCell 13, LeafRow 9, HeaderNode 13 | EntryCell 56, LabelCell 42, LeafRow 38, HeaderNode 42 |

**The arithmetic that settles it**, re-derived from the word sets the counters actually saw (both
trees reproduce their own counters exactly, so the sets are sound):

```
=== FATE OF THE 70 BASELINE-ESCALATED TOKENS ===
  -> now ASSERTED   : 42        -> still escalated : 0        -> counted NOWHERE : 28
=== WHERE THE 56 PROTOTYPE-ASSERTED TOKENS CAME FROM ===
  was baseline-asserted : 14    was baseline-escalated: 42     was baseline-nowhere : 0
```

The 28 are **exactly the stub column** (`Non-current assets:`, `Marketable securities`, … `Total
liabilities and shareholders' equity`) — verified as a set (`28 vanished-token texts NOT found
among prototype LabelCells: []`). **That exclusion is pre-existing**: the matrix-asserted branch
counts only leaf-row × data-column tokens (`compile.py:843-851`), and at baseline every one of the
page's 13 LabelCells is already in the counted-nowhere set. The merge changes the *quantity*
(13 → 42), not the convention.

**Independent oracle that the merge read it correctly** — joining `HeaderNode → LabelCell` with
`HeaderNode → LeafRow` yields 56 stub/value pairs, and the balance sheet balances:

```
Total current assets 149,818 + Total non-current assets 233,448 = 383,266 = Total assets      OK
Total liabilities    275,746 + Total shareholders' equity 107,520 = 383,266 = Total L&SE      OK
```

### B.1 Three consequences the claim did not anticipate — all for the plan, none refuting it

1. **Re-baselining `:907` is not a one-line edit: the guard loses its witness.** apple p1 stops
   escalating, so `:908`/`:909` become vacuous there and the guard stops guarding. A **new fixture
   page** is needed. Corpus-wide under the prototype, 12 pages still escalate and the fallback is a
   no-op on **every** one; the natural swap, same document, is **apple page 2**
   (`asserted=3, escalated=108, score=0.0270, fallback_noop=True`).
2. **apple p1's score becomes 1.0 while 63 of its 119 band words are counted on neither side.**
   Pre-existing convention, not a defect the merge introduces — but 1.0 is the ceiling, so **no
   future regression on that page can ever be detected by its score again.** A real loss of signal.
3. **One new mis-label, not a swallow.** The three-line wrapped stub `Common stock and additional
   paid-in capital, $0.00001 par value: / authorized; 14,608,963 … / respectively` yields a
   `HeaderNode` labelled **`respectively`** — the last wrap line rather than the first. All its ink
   is present as LabelCells; only the chosen label is wrong. At baseline that band escalated
   wholesale, so this is **new**, and it is the same family as `R166`.

The *other* `test_datagrid.py` failure (`:1155 assert 124 == 48`) is **apple page 0**, a different
page: 48 → 124 cells, escalated 100 → 0, score 0.32432 → 1.0. Its own gates still hold; only the
cell pin moved, and that pin exists "so that a movement is loud" (`:1147`).

---

## C. Memoisation is not needed — **CONFIRMED as a blocker**, but a cache is worth MORE than the change costs

Instrument: `scripts/doc_walltime.py` (committed by this loop), one run per tree,
`compile_document(..., validate_shapes=False)` over all 7 documents.

| | BASELINE | PROTOTYPE | delta |
| --- | --- | --- | --- |
| total document-compile wall-clock | 312.24 s | 346.35 s | **+34.1 s / +10.9%** |
| of which `page_bands` | 55.94 s | 83.77 s | **+27.8 s / +50%** |
| recoverable by a perfect cache | 26.73 s | **41.54 s** | — |
| apple document score | 0.1895 | **0.6289** | — |

**Read the call counts before the seconds.** The per-document wall-clock carries real noise: `who`
came back **19% faster** under a change that proposes no run on any of its pages, and
`graincorp-capacity` +83% on an 8.6 s document. Single run per tree; treat ±20% per document as
noise and only the totals as signal.

**The structural fact, which is noise-free because it is a count.** Every document makes exactly
**two** `page_bands` calls per page, plus one per section-repair pass and two per adoption attempt
— `apple 6 calls / 3 pages`, `graincorp-stem 6 / 3`, `who 6 / 3`, `ons 18 / 9`, `bfs 16 / 7`,
`cbh 3 / 1`. There is no cache (`grep -rn lru_cache src/iladub/etkl/*.py` → no output), so **at
least half of all disposal work is duplicated by construction**, on every page, forever.

**The verdict, both halves stated because they point opposite ways:**

- Memoisation is **not** needed to make this change affordable. +27.8 s of `page_bands` on a
  312 s corpus compile is ~9%, and no plan task blocks on it.
- But a perfect cache would return **41.54 s** — *more than the entire 27.8 s the change costs*.
  So a cache is the single largest optimisation available here, and it is a **separate, larger win
  that predates this loop**. It should be raised as a residue, not folded into this diff.

**And the headline reproduces end to end.** apple `0.1895 → 0.6289` at *document* scope, from
inside `page_bands`, through the whole driver — where the predecessor's 0.6289 came from an
instrument that merged bands *after* `page_bands` returned. That was spike § 8's first unverified
line and it is now shown.

---

## D. Six further seams, measured controller-side

1. **`page_bands` has exactly two call sites in `src/`** — `compile.py:602` (inside
   `compile_tables`) and `document.py:1410` (the driver inventory, which always passes
   `section_repair_bands=None`). Every other `src/` hit is a comment or the import. Eight test
   modules and five scripts also call it.
2. **`section_candidates` runs over MERGED bands.** `document.py:1487-1490` derives `ruled` from
   `band_lists[p]`, which is `page_bands`' output. This is a second index-keyed flow reading the
   merged partition, and it is **sound only because of M1** — pass 2 re-derives the same partition
   from the unrepaired build, so the `candidates` frozenset indexes the same list. The spec names
   carriage and adoption at § 3.0; it does not name this one.
3. **The band that ships is not the band the oracle disposed of.** In the prototype the run
   decision is taken on the unrepaired list, the repair rebuild runs next, and the splice runs
   last — so on a page that both repairs *and* merges, `merge_bands` builds from **repaired**
   constituents no oracle ever saw. This is an unavoidable consequence of M1, not a prototype
   defect, and it is spike § Q-A A4's "load-bearing half unexercised" **located at a line**: the
   failure it permits is a shipped merged band that does not tile. No corpus page exercises it
   (cbh p0 is the only repairing page and it has no run).
4. **`merge_bands` covers every `Band` field.** `bands.py:16-34` declares exactly 8 fields and the
   constructor at `one_band_matrix_spike.py:45-55` names all 8. A ninth field added later would be
   **silently defaulted** — cheap to pin with a `len(dataclasses.fields(Band)) == 8` assertion in
   the merge test, which costs nothing and is not a tuned constant.
5. **`scripts/band_run_census.py:111` hard-codes `/Volumes/WD Green/dev/git/iladub/corpus/*/*.pdf`**,
   unlike its sibling `band_run_cost.py:13-21` and `probe_domain_range_agreement.py:85`. It was
   committed one loop ago *so the census would be re-runnable*, and it is not, off this machine.
6. **The register and the population pins, re-measured at `2f55995`** (the spike measured them at
   `9ef63cb`): `43/157 closed`, highest row `R167`, `len(query_files()) == 49`
   (`tests/test_query_terms.py:62`) against 49 files in `vocab/queries/`. The spec's § 7 numbering
   and § 6's count bump both still hold.

---

## E. Unverified or assumed

- **Every figure in § B and § C is the prototype's, and the prototype is not the design** — its
  relation is plain Python (predecessor § 0). § A shows the SPARQL form derives the same runs; it
  does **not** show a shipped implementation behaves like the prototype.
- **No document score was measured with the membrane on.** Everything ran `validate_shapes=False`.
  The membrane has still never been exercised on a merged band — unchanged from the predecessor.
- **No pytest was run in this loop at all.** The predecessor's 14-failures-in-5-files surface is
  inherited, not re-verified. The full suite takes ~45 minutes and must not be run in a background
  subagent.
- **§ C is one run per tree**, and § C names the noise it exposed. A second pair would be cheap and
  was not done.
- **Shape (b) was measured at one `RuleSpan` per rule, not per distinct x** — most of its 2.0x.
  A distinct-x variant is untested.
- **Nothing proves a second SPARQL engine agrees** on the nested `NOT EXISTS`-inside-`FILTER-||`
  shape. Every § A figure is rdflib's.
- **§ A.1's vacuous-truth divergence is proven reachable only synthetically.** That no future band
  shape can produce a rules-carrying band with an empty x set is not proven.
- **§ D.3 is read from the prototype's diff order, not run.** No page exists on which to run it.
- **§ B measured `compile_tables` at page scope only** for the ledger; document-scope effects of
  the p1 change, and the *graphs* of the other five documents, were not diffed.
