# R87 Task 3 — S1: the counts at each candidate site

**Date:** 2026-08-15
**Branch:** `loop-escalation-is-a-decision`, HEAD `c3f7803`, tree clean before and after.
**Scope:** MEASUREMENT ONLY. No site is chosen here, no production code was written, and no
source file was edited — see "How each site was reached" for why none was needed.

**The four documents, at the two sites that can furnish anything** (`req` = expansion requests the
derivation actually constructs):

| document | site (i) page-scope, summed over pages | site (iii) document graph | difference |
| --- | ---: | ---: | ---: |
| who-wfa-boys-zscore-0-5 | 3 | 3 | 0 |
| cbh-stem-2026-08-03 | 4 | **0** | **4 spurious** |
| apple-fy2026q3-statements | 15 | **10** | **5 spurious** |
| graincorp-stem-2026-07-31 | 0 | 0 | 0 |

who-wfa — the plan's chosen document — cannot distinguish the sites: it carries **no**
`dec:supersedes` edge at all. The other three do.

---

## How each site was reached (no source edits)

Two of the three sites are reachable **by identity**, not by instrumentation:

* **site (i) — inside `compile_tables`, before `compile.py:1079` — IS `CompilationReport.graph`.**
  Between the last write to `graph` and `:1079` there is only score arithmetic
  (`compile.py:1064-1077`; `page_has_table` takes no graph), and `:1087` returns that same name.
  Verified at runtime as well: the probe below asserts `report.graph is <the object the site
  holds>` (`returned_graph_is_recorder_graph` on the non-adopting path).
* **site (iii) — `document.py`, before `:1515` — IS `DocumentReport.graph`.**
  `nl -ba src/iladub/etkl/document.py | sed -n '1518,1531p'` shows only sums and the dataclass
  build after the validation call; nothing mutates `graph`.

Only **site (ii)** needs a probe, because the graph the rebuild produces is observed *before* the
rest of the adoption block runs. It is reached by monkeypatching two module attributes that
`compile.py` imports **inside the function body** (so the patch is picked up at call time):

* `iladub.etkl.datagrid.emit_data_grid` — called at `compile.py:1028` with the just-rebuilt graph
  as its first argument. The wrapper counts that object after the real emit returns. It
  distinguishes the rebuild (`:1028`) from the `datagrid_fallback` emit (`:931`) by object
  identity against the recorder's graph.
* `iladub.etkl.decisionlog.ReadingRecorder` — subclassed to capture the graph object handed in at
  `compile.py:488`. Under `datagrid_adopt` this is the object `:1027` **discards**; it stays alive
  through the probe's reference, so "what was thrown away" is a measurement, not an inference.

**How the `datagrid_adopt` path was exercised** (the plan notes no test does):

1. `compile_tables(who-wfa, page_number=0, validate_shapes=False, datagrid_adopt=True)` — a direct
   call. **The adoption branch did not fire**: its gate is `asserted_total == 0 and
   escalated_total > 0` (`compile.py:993`) and who-wfa p0 asserts 191 tokens. `datagrid_adopt=True`
   is therefore a **no-op on who-wfa** — every count below is identical to the `False` run, as are
   the region verdicts, the token totals and the score.
   Site (ii) **does not exist on who-wfa at all**.
2. To measure site (ii) on a page where the branch really fires, the same direct call was made on
   `corpus/ag-trade/graincorp-stem-2026-07-31.pdf` page 1 — the page `compile.py:1020-1026`'s own
   comment names as an adopting page. Branch firing was **confirmed by the probe**
   (`adopt_branch_fired: true`, `returned_graph_is_recorder_graph: false`), not assumed.
3. The driver's own adoption call site (`document.py:1407-1412`, the only caller in the repo that
   passes `datagrid_adopt=True`) was reached by `compile_document(apple-fy2026q3-statements.pdf)`,
   which adopts page 1 (`adopted=(1,)`). An earlier attempt via `compile_document(graincorp-stem)`
   did **not** reach it, and that failure is itself a measurement — see "the driver did not adopt"
   below.

The probe script (run with `./.venv/bin/python`; it lived in the session scratchpad and is
reproduced here in full so every number below is re-runnable):

```python
import os, time
from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS
ROOT = "/Volumes/WD Green/dev/git/iladub"
ONT  = os.path.join(ROOT, "vocab", "ontology")
RQ   = os.path.join(ROOT, "vocab", "queries", "escalation-furnish.rq")
DEC  = Namespace("https://w3id.org/iladub/dec#")
TAB  = Namespace("https://w3id.org/iladub/tab#")

def vocab():                      # risk.ttl u etkl.ttl, as tests/etkl/test_escalation_furnish.py
    g = Graph()
    g.parse(os.path.join(ONT, "risk.ttl"),  format="turtle")
    g.parse(os.path.join(ONT, "etkl.ttl"), format="turtle")
    return g

def census(g):
    from iladub.etkl import interpret
    esc = {d for d in g.subjects(RDF.type, DEC.DecisionHolon)
           if any(str(l) == "escalated" for o in g.objects(d, DEC.chosen)
                  for l in g.objects(o, RDFS.label))}
    reg = {d for d in esc if list(g.objects(d, DEC.regarding))}
    sup = {d for d in esc if list(g.subjects(DEC.supersedes, d))}
    out = interpret.run(RQ, g, vocab())
    return dict(triples=len(g), A=len(esc), B=len(reg), superseded=len(sup),
                supersedes_edges=len(list(g.triples((None, DEC.supersedes, None)))),
                RecordTable=len(list(g.subjects(RDF.type, TAB.RecordTable))),
                HierarchicalTable=len(list(g.subjects(RDF.type, TAB.HierarchicalTable))),
                requests=len(set(out.subjects(RDF.type, DEC.ExpansionRequest))),
                out_triples=len(out))

class Probe:                      # installs the two wrappers; collects every observation
    def __init__(self): self.rec, self.emits = [], []
    def install(self):
        from iladub.etkl import datagrid, decisionlog
        self.dg, self.dl = datagrid, decisionlog
        self.real_emit, self.real_rec = datagrid.emit_data_grid, decisionlog.ReadingRecorder
        probe = self
        class WrappedRecorder(probe.real_rec):
            def __init__(self, graph, doc, page_number, *a, **k):
                probe.rec.append((str(doc), page_number, graph))
                super().__init__(graph, doc, page_number, *a, **k)
        def wrapped_emit(g, grid, lines, doc_uri, page, *a, **k):
            rebuilt = id(g) not in [id(x[2]) for x in probe.rec]   # :1028 vs the :931 fallback
            res = probe.real_emit(g, grid, lines, doc_uri, page, *a, **k)
            probe.emits.append(dict(page=page, into_rebuilt_graph=rebuilt,
                                    census_right_after_emit=census(g)))
            return res
        datagrid.emit_data_grid, decisionlog.ReadingRecorder = wrapped_emit, WrappedRecorder
    def remove(self):
        self.dg.emit_data_grid, self.dl.ReadingRecorder = self.real_emit, self.real_rec
```

Column key, per candidate site, in the graph object **that site actually holds**:

| column | what it counts |
| --- | --- |
| **A** | `?d a dec:DecisionHolon ; dec:chosen ?o . ?o rdfs:label "escalated"` |
| **B** | of A, those that also carry `dec:regarding` |
| **sup** | of A, those with an incoming `?later dec:supersedes ?d` |
| **RT / HT** | `tab:RecordTable` / `tab:HierarchicalTable` subjects — C1's gate |
| **req** | `dec:ExpansionRequest` instances the derivation actually constructs there (`interpret.run(escalation-furnish.rq, graph, risk.ttl ∪ etkl.ttl)`) |

---

## Table 1 — who-wfa-boys-zscore-0-5.pdf (the priority document)

`./.venv/bin/python measure.py doc-who` → `compile_document(WHO)`, 43.0 s, 3 pages,
`adopted=()`, `repaired_bands=()`. Region verdicts: p0 and p1 each
`ignored, ignored, escalated, asserted, asserted, asserted, ignored`; p2
`ignored, escalated, asserted, ignored`.

`./.venv/bin/python measure.py page who 0 noadopt|adopt` →
`compile_tables(WHO, page_number=0, validate_shapes=False, datagrid_adopt=False|True)`, 13.6 / 13.4 s.

| site | `datagrid_adopt` | triples | A | B | sup | RT | HT | C1 gate | req |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| (i) before `compile.py:1079`, p0 | False | 3437 | 1 | 1 | 0 | 1 | 2 | **opens** | 1 |
| (i) before `compile.py:1079`, p0 | True | 3437 | 1 | 1 | 0 | 1 | 2 | **opens** | 1 |
| (ii) after the `:1027` rebuild, p0 | True | — | — | — | — | — | — | — | — |
| (iii) before `document.py:1515` | n/a (driver) | 8077 | 3 | 3 | 0 | 2 | 5 | **opens** | 3 |

Row (ii) is empty because **the rebuild never happens on who-wfa** — the `:993` gate is closed on
every page (p0: `asserted_total=191`, `escalated_total=129`, score 0.5969). The two (i) rows are
identical for exactly that reason, and `adopt_branch_fired` is `false` in both.

Per-page pass-1 recorder graphs inside that document compile (the objects `graph += pages[-1].graph`
at `document.py:1212` copies in):

| page graph | triples | A | B | sup | RT | HT | req |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `…/doc/p0` | 3437 | 1 | 1 | 0 | 1 | 2 | 1 |
| `…/doc/p1` | 3437 | 1 | 1 | 0 | 1 | 2 | 1 |
| `…/doc/p2` | 1209 | 1 | 1 | 0 | 0 | 1 | 1 |

3 pages × 1 = the document graph's 3. **who-wfa carries no `dec:supersedes` edge anywhere** — 0 at
page scope and 0 at document scope — so on this document alone the supersession guard is
indistinguishable from absent, at every site. That is why cbh-stem is measured below.

---

## Table 2 — the adopting path, where it actually fires: graincorp-stem p1

`./.venv/bin/python measure.py page stem 1 adopt` →
`compile_tables(graincorp-stem, page_number=1, validate_shapes=False, datagrid_adopt=True)`, 17.1 s.
`adopt_branch_fired: true`. Report: verdicts `ignored, superseded, ignored, asserted, escalated`,
asserted 1025 / escalated 44, score 0.9588 (the figure `compile.py:1024` records).

| graph object | triples | A | B | sup | RT | HT | C1 gate | req |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| pass-1 recorder graph, **discarded at `:1027`** | 218 | 1 | 1 | 0 | 0 | 0 | closed | **1** |
| **site (ii)** — right after the `:1027` rebuild + `:1028` emit | 10086 | **0** | 0 | 0 | 0 | 0 | **closed** | **0** |
| **site (i)** — same object, before `:1079` | 10099 | **0** | 0 | 0 | 0 | 0 | **closed** | **0** |

Three things are measured here, not read:

1. The rebuilt graph **retains no escalated decision at all** (A = 0), while the graph it replaced
   held one that the derivation would have furnished (req = 1).
2. The 13 triples added between site (ii) and site (i) are the DATAGRID_RESIDUE escalation
   (`compile.py:1053-1058`). It adds **no** decision holon: `escalate_region` emits a
   `iladub:CandidateConcept` proposition and no `dec:` property at all
   (`nl -ba src/iladub/etkl/holon.py | sed -n '424,463p'`, R69). So the one region this page still
   escalates after adoption is **not furnishable in principle** — the derivation binds
   `?d a dec:DecisionHolon`.
3. **C1's gate does not open on the adopting path.** RT = HT = 0 in the rebuilt graph (the grid is
   a `tab:DataGrid`), so `compile.py:1079`'s `_validate` never runs there — with or without
   furnishing.

### …and the driver did not adopt that page

`./.venv/bin/python measure.py doc-stem` → `compile_document(graincorp-stem)`, **171.2 s**,
3 pages, `adopted=()`, `repaired_bands=()`, `notes=()`. Page 1's verdicts under the driver are
`ignored, asserted, ignored` — the band that escalates when page 1 is compiled **standalone**
**asserts** when the driver compiles it with its carried header reading, so
`is_adoption_candidate` (`document.py:1402`) is false and `datagrid_adopt=True` is never passed.
Document graph: 29999 triples, A = 0, RT = 0, HT = 3, gate opens, 0 requests, **0 supersedes edges**.
graincorp-stem therefore escalates **nothing** at document scope.

A page's verdict is therefore **not a property of the page**: page 1 escalates standalone and
asserts under the driver. Any claim of the form "document D's page p adopts" has to name which
call made it.

---

## Table 2b — the driver's own adoption path: apple-fy2026q3-statements.pdf

`./.venv/bin/python measure.py doc-apple` → `compile_document(APPLE)`, **37.8 s**, 3 pages,
**`adopted=(1,)`**, `repaired_bands=()`. This is the one document measured here that reaches
`document.py:1407-1412` and hands `datagrid_adopt=True` to `compile_tables`.

| graph object | triples | A | B | sup | edges | RT | HT | C1 gate | req |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| pass-1 `…/doc/p0` | 1062 | 5 | 5 | 0 | 0 | 1 | 0 | opens | 5 |
| pass-1 `…/doc/p1` | 669 | 5 | 5 | 0 | 0 | 0 | 0 | **closed** | 5 |
| pass-1 `…/doc/p2` | 833 | 5 | 5 | 0 | 0 | 1 | 0 | opens | 5 |
| the adopt re-compile's recorder graph `…/p1/adopt`, **discarded at `:1027`** | 669 | 5 | 5 | 0 | 0 | 0 | 0 | closed | 5 |
| **site (ii)** — `…/p1/adopt` rebuilt, right after `:1027`/`:1028` | 1192 | **0** | 0 | 0 | 0 | 0 | 0 | **closed** | **0** |
| **(iii)** document graph before `document.py:1515` | 3725 | 15 | 15 | **5** | **5** | 2 | 0 | opens | **10** |

The page-scope sum is 5+5+5+0 = **15 requests**; the document graph furnishes **10**. The five that
differ are page 1's, withdrawn by the adoption — measured, not reasoned: all five
`dec:supersedes` edges have the subject `…/doc/p1/adopt#p1-datagrid-admission`, i.e. they are
`document.py:1503`'s writer, and their objects are `…/doc/p1#region{2,3,4,5,7}-d{4,5}`.
**Furnishing at site (i) would raise five expansion requests on apple for bands whose ink the
document graph now asserts as the page's data grid.**

It also confirms Table 2 through the driver rather than through a direct call: the rebuilt graph
the driver adopts retains **zero** escalated decisions while the graph it replaced held five.

---

## Table 3 — cbh-stem-2026-08-03.pdf (the supersession contrast)

`./.venv/bin/python measure.py doc-cbh` → `compile_document(CBH)`, 28.0 s, 1 page,
`repaired_bands=((0,1),(0,3),(0,5),(0,7))`, `adopted=()`. All ten region verdicts end
`asserted`/`ignored` — zero `escalated`.

| site / object | triples | A | B | sup | edges | RT | HT | C1 gate | req |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| pass-1 page graph `…/doc/p0` (what sites (i)/(ii) hold) | 951 | 4 | 4 | **0** | **0** | 0 | 1 | opens | **4** |
| pass-2 page graph `…/doc/p0/r2` | 11670 | 0 | 0 | 0 | 0 | 0 | 5 | opens | 0 |
| **(iii)** document graph before `document.py:1515` | 12153 | 4 | 4 | **4** | **4** | 0 | 5 | opens | **0** |

**This is the whole decision, in one table.** The same four decisions are present at page scope and
at document scope. At page scope they carry no incoming `dec:supersedes`, so the derivation
furnishes **four expansion requests for matters a pass-2 re-read already resolved**. At document
scope the four edges exist and the derivation correctly furnishes **zero**. The handoff's warning
is now measured rather than predicted.

---

## Question 1 — does the adopting path retain any escalated decision at all?

**No. Measured A = 0 in the rebuilt graph, on both pages that reach the branch:**

| page | how the branch was reached | discarded pass-1 graph | rebuilt graph |
| --- | --- | --- | --- |
| graincorp-stem p1 | direct `compile_tables(..., datagrid_adopt=True)` | A=1 B=1, **1 request** | A=0, **0 requests**, gate closed |
| apple p1 | the driver, `document.py:1407-1412` | A=5 B=5, **5 requests** | A=0, **0 requests**, gate closed |

On graincorp-stem the rebuilt graph was counted at **both** observation points (immediately after
the `:1027`/`:1028` rebuild, and again at `:1079`): A = 0 at each.

So furnishing after `:1027` furnishes nothing — **and the reason is not only that the escalations
were withdrawn.** Two further measured facts sharpen it: the page's surviving escalation (the
DATAGRID_RESIDUE region) is a proposition with no decision holon and is unfurnishable by
construction, and C1's gate is **closed** on the rebuilt graph (RT = HT = 0), so nothing validates
there either.

Caveat, stated rather than inferred: **on who-wfa the adopting branch never fires**, so
"`datagrid_adopt=True` on who-wfa" was measured as identical to `False` in every column. The
adopting-path numbers above are graincorp-stem's and apple's, not who-wfa's.

**But "furnishes nothing" is not the same as "needs no furnishing."** Apple shows the cost lands
one level up: the five decisions the rebuild discarded are still standing in the **document**
graph, arriving from the pass-1 page graph at `:1212`, and they are withdrawn only by the
admission edges written at `:1503`. A site inside `compile_tables` sees them **before** that.

## Question 2 — does `document.py:1516` see the page graph the recorder wrote, or the rebuilt one?

**Neither: it sees a third object, into which page graphs are merged by value.**
`document.py:1157` creates `graph = Graph()` and nothing rebinds that name for the rest of the
function (`grep -n "graph = Graph()" src/iladub/etkl/document.py` → `1157` only; the only other
rebind in the pipeline is `compile.py:1027`, inside the page compile). Content arrives at three
places, all measured present in the counts above:

* `:1212` `graph += pages[-1].graph` — the driver's main pass calls `compile_tables` **without**
  `datagrid_adopt` (`document.py:1207-1211`, default `False`), so this is the **recorder-written**
  page graph, escalated decisions and all. who-wfa: 1+1+1 = the document graph's 3.
* `:1285` / `:1295` — section repair merges the pass-2 band subgraph and reading record, then
  `:1299` adds the supersedes edge. cbh-stem: 4 edges.
* `:1447` `graph += rep_a.graph` — for an **adopted** page, the `datagrid_adopt=True` re-compile's
  **rebuilt** graph is merged **in addition to** the pass-1 page graph already merged at `:1212`
  (`:1446` only removes the escalation *record* of the superseded bands). **Measured on apple**,
  the one adopting document here: its document graph is 3725 triples against 1062+669+833 = 2564
  of pass-1 page graphs, and it carries the adopt graph's `…/p1/adopt#p1-datagrid-admission`
  subject — so both the recorder-written p1 graph (whose 5 escalating decisions are still in the
  A = 15) **and** the rebuilt adopt graph are present at `:1515`.

So at `:1515` the document graph holds the recorder's page graphs always, plus the rebuilt graph on
any adopted page. Document-scope validation is therefore **not** covered by a page-scope call: the
page-scope object is a different `Graph`, and triples furnished into it at `:1079` reach
`document.py` only because `:1212` copies whatever the page graph contained at `:1087`.

## Question 3 — where does section repair link its `dec:supersedes` edges, and which sites run after?

**Re-measured. The cited `~L1258-1284` is the wrong range.** The link is one line:

```
$ grep -rn "supersedes" src/iladub/ | grep "graph.add"
src/iladub/reopen.py:39:    graph.add((new_subject, DEC.supersedes, prior_subject))
src/iladub/etkl/document.py:1299:                    graph.add((v2, DEC.supersedes, v1))
src/iladub/etkl/document.py:1503:                graph.add((admission, DEC.supersedes, v1))
```

* **`document.py:1299`** — section repair. Inside the repair loop that opens at `:1231`
  (the LOOP Q block comment) / `:1249` (`for p in range(n_pages)`), in the adoption arm at
  `:1279-1302`. `1258-1284` covers the candidate selection and `_remove_escalation_record`, but the
  edge itself is **15 lines past** the cited upper bound.
* **`document.py:1503`** — the datagrid-adoption admission holon, a second writer the handoff does
  not name. Same document graph, still before `:1515`. **Live, not hypothetical**: it is the writer
  of all five of apple's edges (subject `…/doc/p1/adopt#p1-datagrid-admission`).
* **`reopen.py:39`** is **not in the compile path**: `grep -rn "import reopen\|from .reopen" src/
  tests/` returns only `tests/test_reopen.py`.

Which of the four cbh-stem edges came from which writer is measured from their subjects — every one
is a pass-2 verdict decision under the `/r2` doc URI, i.e. all four are `:1299`, none are `:1503`
(an admission subject would end `-admission`):

```
https://example.org/etkl/doc/p0/r2#region1-d5  dec:supersedes  https://example.org/etkl/doc/p0#region1-d4
https://example.org/etkl/doc/p0/r2#region3-d5  dec:supersedes  https://example.org/etkl/doc/p0#region3-d4
https://example.org/etkl/doc/p0/r2#region5-d5  dec:supersedes  https://example.org/etkl/doc/p0#region5-d4
https://example.org/etkl/doc/p0/r2#region7-d5  dec:supersedes  https://example.org/etkl/doc/p0#region7-d4
```

**Both writers write into the document graph and into no page graph.** Measured `supersedes_edges`
= 0 in **every** page-scope graph observed in this session: who-wfa p0/p1/p2, cbh-stem `p0` and
`p0/r2`, graincorp-stem p1 pass-1 and p1 rebuilt, apple p0/p1/p2, `p1/adopt` pass-1 and rebuilt —
13 page graphs, 0 edges. The relation is not "site (i)/(ii) run too early in time" — the edges
never enter those objects at any time, because `compile_tables` returns before the driver has
anything to link, and the link is then made to a **copy** of what it returned.

Therefore:

| site | runs after the `dec:supersedes` edges exist? | consequence measured |
| --- | --- | --- |
| (i) `compile.py:1079` | **No** — never; different graph object | cbh-stem: **4** spurious requests (4 vs 0); apple: **5** spurious (15 vs 10) |
| (ii) `compile.py` after `:1027` | **No** — never; different graph object | vacuous *and* empty (A = 0, gate closed, 0 requests) |
| (iii) `document.py:1515` | **Yes** — `1299 < 1503 < 1515`, and nothing mutates `graph` after `:1518` | who-wfa 3, cbh-stem 0, apple 10, graincorp-stem 0 |

Site (iii) is the only candidate at which the supersession guard is non-vacuous. Choosing the site
is Task 3's next step and is deliberately not done here.

---

## Stated plainly: what was NOT measured

* **who-wfa never exercises the adopting branch**, so no who-wfa number exists for site (ii).
  The adopting-path counts are graincorp-stem p1's (direct page-scope call) and apple p1's
  (through the driver).
* **Site (ii) was observed at one point in the rebuild block** — after `:1028`'s emit, before the
  residue at `:1053-1058`. The difference between that point and site (i) is the 13 residue triples
  and is shown; no other intermediate point in `:1027-1062` was sampled.
* The `compile_tables` runs used `validate_shapes=False` (the counts are of graph content, not of
  membrane behaviour). The `compile_document` runs used the default `validate_shapes=True`.
* **T3.2/T3.3 are untested here.** Whether `dec:EventShape` and `dec:ExpansionRequestShape` are
  satisfied when the furnished triples are actually in a validated graph is not measured — nothing
  was wired, so nothing crossed a membrane.
* Supersession is now measured on **four documents** (who-wfa 3 escalating / 0 superseded;
  cbh-stem 4 / 4; apple **15 / 5**; graincorp-stem 0 / 0) — the handoff listed apple and
  graincorp-stem as unmeasured, and they are no longer. **bfs, graincorp-capacity and ons remain
  unmeasured.** Note apple's 15 matches spec §5 M5's count of decisions that CHOSE "escalated";
  its live count is **10**.
* The rudof leg was not run. Every figure is the default engine.
* **No test was run.** These are direct API calls under a probe, not the suite; the fast suite and
  the `-m corpus` tests were not re-run in this session.
* No site is chosen and no code is written. `git status --short` is clean apart from this
  untracked file.
