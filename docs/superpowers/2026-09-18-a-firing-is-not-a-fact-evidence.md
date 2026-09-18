# Evidence — a firing is not a fact: the oracle five criteria name, and why it cannot be written

**Serves:** prog:criterion:tab:09 — and, through the same missing oracle, `tab:02`, `tab:05`,
`tab:07`, `tab:08`. The standing direction from the previous handoff's § 5c, second bullet
(return to the arc, `etkl:05` through [[R44]]); this is the gate every one of those sub-loops
reaches before it can flip anything.

**Date:** 2026-09-18. **Branch:** `a-firing-is-not-a-fact`, cut from `main` at `2f3fc76`.

**Doc impact: none.**

---

## 1. The census — six criteria name an oracle that does not exist, and two kinds of absence

New instrument, `scripts/oracle_test_census.py` (PROCEDURAL; its § header carries the
classification and the control). Run at `2f3fc76`:

```
$ ./.venv/bin/python scripts/oracle_test_census.py
61 declarations, 51 distinct node ids, 19 files, 142 ids collected

MODULE ABSENT — the file does not exist (3):
  tests/substrate/test_event_ledger.py::test_committed_events_are_immutable
      named by criterion:substrate:01
  tests/substrate/test_in_engine_policy.py::test_engine_enforces_ai_inherits_user
      named by criterion:substrate:03
  tests/substrate/test_write_gate.py::test_engine_refuses_an_ungoverned_commit
      named by criterion:substrate:02

DANGLING IN AN EXISTING FILE — the file exists, the node id does not (3):
  tests/test_corpus.py::test_escalation_reasons_are_adjudicated
      named by criterion:tab:02, criterion:tab:05, criterion:tab:07, criterion:tab:08, criterion:tab:09
  tests/test_hga_alignment.py::test_raw_to_clean_traversal_conformant
      named by criterion:holon:06
  tests/test_corpus.py::test_this_id_is_invented
      named by (null control)

CONTROL — three checks, none of them this file's own prose:
  every met criterion's id collects  (43 declarations)         PASS
  the 3 substrate ids are reported absent                      PASS
  the invented null id is reported absent                      PASS
```

**This is not a manifest defect, and saying so is load-bearing.** `tests/test_arc_manifest.py`
M5b is met-gated *on purpose* — read at `:313-316`:

```python
        if met is not True:
            # An UNMET criterion may name a TARGET oracle that does not exist yet
            # (spec §3, §7.5). M5 bites only on an assertion of met-ness.
            continue
```

So naming an unbuilt oracle is a declared target, not a leak. What the census adds is the count
nobody had: **six of 44 criteria are waiting on an oracle that has never been built**, five of them
on one, and the arc's `ready` list cannot distinguish them from work that could start today.

**The consequence is exact and unavoidable.** M5b refuses `prog:met true` on a criterion whose
named `prog:oracleTest` does not collect. So `tab:02/05/07/08/09` cannot be flipped — not after
R43, R44, R62, R71, R79, R83 or R84 close, not ever — until
`tests/test_corpus.py::test_escalation_reasons_are_adjudicated` exists. That is 5 of the 9 unmet
criteria on the arc's worst rung (`tab` 2/11).

## 2. The oracle cannot be written as stated, because "fires" and "disposes" are not facts

All five criteria state the same disjunction (`tests/arc-manifest.ttl`, e.g. `:1366`):

> … this escalation reason is disposed — **either it fires** on the 7-document corpus **and every
> firing document carries a dated `cor:adjudication` naming and disposing of it**, or it fires
> nowhere on the corpus and names a collectable `prog:oracleTest` …

Three predicates would have to be readable for a test to check that. None is:

| what the statement needs | what the graph has |
| --- | --- |
| *this reason fires on this document* | nothing — no `cor:` term relates a document to an escalation reason |
| *this adjudication names that reason* | nothing — the reason name appears **inside** a `cor:rationale` string |
| *this adjudication disposes it, rather than holding it* | nothing — `HOLD` is the first word of a prose literal |

Measured. The corpus vocabulary declares **31** terms (`vocab/internal/corpus.ttl`):
`cor:Adjudication cor:CompilesAbove cor:Document cor:Reading cor:SemanticEscalation
cor:Unadjudicated cor:Verdict cor:adjudication cor:ambiguity cor:atCommit cor:by cor:contract
cor:expectedVerdict cor:family cor:fetched cor:file cor:notQuotable cor:on cor:pages cor:producer
cor:rationale cor:readAt cor:reading cor:recordedIn cor:scoreFloor cor:series cor:sha cor:shapes
cor:terms cor:url cor:value`. The nearest is `cor:ambiguity`, a free string used **once** in the
whole register.

And the reason names themselves are enumerable from source — `git grep -ho '"[A-Z][A-Z_]\{4,\}"'
-- src/iladub/etkl/` returns 14 constants including all five criteria's subjects — so the
*vocabulary* of reasons is decidable in CI even though the *firing* is not. That asymmetry is what
§ 3 of the spec is built on.

Where the reason names actually live today, in the whole tracked register: inside four
`cor:rationale` literals (`tests/corpus-manifest.ttl:44,122,135,137`, of 15 rationales). bfs's, at
`:122`, is the specimen — it opens `"HOLD — recorded, not accepted."` and narrates
`ROUND_TRIP_FAIL x5`, `KIND_NOT_SUPPORTED x3`, `REGION_TILING_FAILED x2` in prose. Nothing reads
it. Nothing can.

## 3. The prose census has already drifted — three instances, measured at HEAD

The arc manifest keeps its own census, in Turtle **comments** — five of them, `grep -n "^# FIRES"
tests/arc-manifest.ttl` → `:1233, :1284, :1332, :1345, :1357`, all written 2026-08-20. A Turtle
comment is dropped by the parser, so no instrument in this repo reads them, by construction rather
than by neglect.

Re-measured today at `2f3fc76` with the shipped instrument
(`./.venv/bin/python scripts/bfs_reason_triage.py`, one document):

```
reason                      2026-08-04   live   sup.  total   moved?
DATAGRID_RESIDUE                     0      1      0      1   MOVED
KIND_NOT_SUPPORTED                   2      3      1      4   MOVED
REGION_TILING_FAILED                 2      2      0      2   -
ROUND_TRIP_FAIL                      5      1      4      5   -
```

**3.1 `tab:08`'s comment is wrong.** `:1345` reads *"FIRES 1 — apple p1, under the adoption doc
URI"*. bfs fires it too, today, at p5 region16 — printed in the same run's region list
(`p5 region16  escalated  RegionKind.UNSUPPORTED_TABLE DATAGRID_RESIDUE`). [[R44]]'s row already
recorded this on 2026-09-15 (*"arrived on bfs with no loop recording it"*) and the comment three
files away still says apple only. **Nothing connects them, because one of them is a comment.**

**3.2 `tab:07`'s comment is a live-only count.** `:1332` reads *"FIRES 3 — bfs only"*. The
multiset at HEAD is **4** — 3 live and 1 superseded by p5's adoption. Superseded is *replaced*, not
repaired.

**3.3 `tab:09`'s 5 would read as 1 to any instrument that counted live firings.** `:1357` reads
*"FIRES 5 — bfs p5"*, and the total is still 5 — but 4 of them are superseded, so a naive
re-measure reports an 80% improvement that is pure concealment. This is the trap [[R44]]'s triage
named, and it is a property of the *fact shape*, not of any one instrument: a firing has a verdict
class, and a census that records a number without it records a figure that will be misread by the
next honest reader.

## 4. The one instrument that re-measures this fails its own control on a stale literal

The run in § 3 exits **1**:

```
CONTROL — three known positives recorded INDEPENDENTLY of this script:
  score matches a recorded reading  PASS  (2026-09-14 )
  page 5 is adopted                 PASS  (adopted [5])
  page 5 asserts 404 cells           FAIL  (got 496)
  ...and it is the NEWEST reading   yes

FAIL -- instrument did not re-find its known positives; do not trust the tally above.
```

**The tally is right and the control is stale.** 404 came from the R224/R225 closure; [[R240]]'s
row records that bfs p5 *"gained 92 cells and 1103 triples with the score identical to 10 dp"* when
[[R238]]'s decoration→alignment switch shipped. 404 + 92 = **496**, exactly what the run reports.

This is the defect the script's own docstring warns about, committed inside the instrument built to
catch it: *"A control pinned to a literal goes stale exactly as the row it is checking did."* Its
score leg reads `cor:reading` from the manifest for precisely this reason; its cell leg could not,
because no committed source records that figure — it lives in a residue row's prose. **Same cause
as § 2, one layer down.**

Repaired in this loop, minimally and with its citation inline (`scripts/bfs_reason_triage.py`); the
durable repair is the spec's subject, not a second literal.

## 5. Falsification

**F1 — the census (`scripts/oracle_test_census.py`).** Its first run reported `0 declarations` and
`FAIL` on the substrate check, because the script had the namespace as
`https://w3id.org/iladub/prog#` where the manifest declares `https://w3id.org/iladub/progress#`
(`tests/arc-manifest.ttl:41`). **The control caught a real bug in the instrument on its first
run**, which is the only evidence that the control is load-bearing rather than decorative. Fixed;
all three controls PASS.

**F2 — the null.** `--null` injects an invented node id (`test_this_id_is_invented`) into an
existing file and requires it to be reported absent. Remove the null from the absent set and the
control fails: an instrument that reports everything present cannot report anything absent.

**F3 — the stale-literal repair.** The inversion is the run above: at `404` the control prints
`FAIL` and the script exits 1; at `496` it prints `PASS` and exits 0. Both observed today, in that
order, on the same document and the same commit.

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
