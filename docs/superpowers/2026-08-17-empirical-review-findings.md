# The empirical review — findings

**Date:** 2026-08-17 · **Tree:** `main` @ `fc0a908` · engine **rudof**, corpus present locally
· reviewer had no inherited context; a first attempt died on a transient 529 and this is the
re-run

Target: `specs/2026-08-17-coverage-is-not-liveness-design.md` and the three `2026-08-17-m-*`
measurement documents, the latter reviewed **as claims, not as authority** (they share an author
with the spec).

## The shape of the result

**Every measurement reproduced. The prose around them did not.** R102's 769/453/316, M-B's full
per-leg table, M-A byte-for-byte, and M-C's headline census were all independently re-derived and
matched. Every defect below is in a *sentence written from* a measurement, not in a measurement.

That pattern is the useful finding: this repo's discipline of measuring before claiming worked;
the failures are all in the restatement, which is where CLAUDE.md plan-rule 2 says they live.

## Defects affecting Loop 1

### E1 — `16 of 27 corpus pages` does not reproduce. It is 14, and only 13 mean what the sentence says. [MEDIUM]

The claim is in **R102's row (`residues-open.md:82`)** as well as the spec — i.e. **the canonical
register carries a wrong number.**

Measured (spying both `_validate` references, evaluating the page gate on every
`compile_tables` return):

- **27 distinct pages** ✓ (31 `compile_tables` calls).
- **14** have the page gate FALSE — not 16.
- Of those 14, **apple p1's 37 holons ARE validated**, at the document leg. So **13** pages carry
  holons no membrane ever sees; their holons sum to 113 + 203 = **316**, cross-checking the
  headline exactly.

The claim also encodes a false inference — *gate FALSE ⇒ unseen* — which apple p1 refutes. Fix
the row and the spec together; Loop 1 will quote this number.

### E2 — the split decision's own D11 correction is incomplete, and its central worry is measured away. [MEDIUM]

D11's substance is **confirmed**: the 316 are exactly ons + bfs, which fail the *document* gate,
not a tab-fact gate. But:

- **Three documents never open the document gate, not two** — `graincorp-capacity` too. It
  contributes 0 never-validated holons and does contribute cost.
- **Which gate is being ungated is load-bearing and unstated.** Ungating the **document** gate
  alone covers all 316 (the merged graph accumulates every page graph at `document.py:1245`);
  ungating the **page** gate adds 14 further page-leg validations. Loop 1's spec must say which.

**The "missing branch" the split decision flagged as unplanned is now measured** — validating the
full merged graph of each never-gated document against both shape sets:

```
graincorp-capacity: triples=5705   holons=18    DEC conforms=True (0.6s)  TAB conforms=True (0.6s)
bfs:                triples=8244   holons=232   DEC conforms=True (0.6s)  TAB conforms=True (0.8s)
ons:                triples=11076  holons=218   DEC conforms=True (0.8s)  TAB conforms=True (0.8s)
```

**At HEAD, ungating does not turn the corpus red, and costs ~1.4 s per document (~4 s total).**
The §4.1 seam's specific worry — that ungating would put the tab shapes onto fact-free graphs —
is empirically safe on these three today. **The seam remains a correct design requirement; it is
no longer an unquantified risk.**

### E3 — R104 touches six sites, not two. [LOW, scoping]

Beyond `compile.py:1103` and `document.py:1587`, a `_validate` signature change also touches
`tests/etkl/test_compile_membrane_shapes.py:35,94,122,143` (`:94,:122,:143` unpack a 2-tuple) and
`tests/etkl/test_membrane.py:92`, which pins `inspect.getsource(C._validate)`. The "~1 hour"
estimate was scoped against two.

### E4 — the register's own preamble contradicts CLAUDE.md. [Loop 1's register-honesty pass]

`docs/superpowers/residues.md:6` still says *"a loop that closes a residue **deletes its row** in
the same change."* CLAUDE.md § Deferred residues explicitly reverses this (*"strikes the row's
number … It does NOT delete the row (this reverses the earlier rule)"*).

## Defects affecting Loop 2

### E5 — `dec:Event … only at document.py:1575` is wrong in both directions. [LOW-MEDIUM]

- **`dec:Event` is never asserted there.** The CONSTRUCT at
  `vocab/queries/escalation-furnish.rq:64-75` types `?req` as `dec:ExpansionRequest` only.
  `dec:EventShape`'s 13 doc-leg focus nodes arrive via **RDFS closure** —
  `dec:ExpansionRequest rdfs:subClassOf dec:Event` (`vocab/ontology/dec.ttl:197-198`).
- **`dec:Event` IS asserted under `src/`** — `src/iladub/events.py:21` and
  `src/iladub/escalate.py:68` — outside the etkl compile path. No `DEC.Event` is typed anywhere
  under `src/iladub/etkl/`.

The conclusion ("no page graph can carry these") is verified. **The mechanism is not — and under
Loop 2's D4, a registry row citing this mechanism would fail its own oracle.**

### E6 — `analyze(` "nowhere under `src/`" is literally false. [LOW-MEDIUM]

`src/iladub/etkl/denormalization.py:319` is `def analyze(report):`. **The substance holds** —
exhaustively, zero *call sites* under `src/`. M-A stated it correctly (*"called from … and from
no file under `src/`"*); the spec dropped "called from". §7.1 rests on the substance, which
survives.

### E7 — `document.py:736-737` cites a read for one of the two predicates. [LOW]

`:737` is a lookup (`graph.value(..., TAB.inLogicalColumn)`). The writes are `:736`
(`continuesColumn`) and `:738,:739` (`inLogicalColumn`). Correct citation: **`736, 738-739`**.
The **"only"** claim is verified exhaustively — neither predicate is added anywhere else in
`src/`, no `.rq` constructs them, and `_link_columns` is called only from `document.py:1261` and
`:1367`, both document-scope.

### E8 — `test_vacuity_registry.py:196-198` is code, not docstring. [LOW]

The docstring is `:191-195` and the aggregation argument is at `:193-195`; `:196-198` is
`out = {}` / the loop / `max_focus = max(...)`. (`:190-205` for `idle_shapes` is correct.)

### E9 — minor overreach

§4.2's *"AggregationCell / SectionTotal: coverage ∅ on **every axis**"* exceeds the evidence. Two
axes were measured, and M-A's own caveat says the fixture zero *"is not evidence they are dead."*

## Defect affecting Loop 3

### E10 — M-C's rapidocr grep claim overstates. [COSMETIC]

The grep M-C reports as finding nothing **does** hit: R101's own row says *"`rapidocr` sits in the
`ocr` extra, which CI does not install."* What is genuinely absent is any statement that the
omission is **deliberate**. The finding survives; the wording does not.

## Verified — the load-bearing claims that held

- **The §4.1 seam is real.** `_validate` (`compile.py:453-465`) runs `_TAB_SHAPES` at `:460` and
  `_DEC_SHAPES` at `:461` **unconditionally**, under one gate. Splitting it is not free, and
  `:457-459` is exactly the comment that argues for the combined report.
- **I3 verified** — `document.py:110` binds `_validate` at import.
- **§4.6's wrinkle is real** — `:463` returns `True, tab_report`; the dec report is discarded when
  both conform. Both raise sites hardcode `"tab: SHACL"`.
- **R102 reproduced exactly**: 769 minted / 453 seen / **316 never**; ons 203/218, bfs 113/232,
  the other five 0; 119 focus nodes on apple.
- **M-B reproduced to the digit** — the call census, 14 page calls, 4 doc calls, 3 of 7 documents
  never opening the doc gate, `dec:EscalationShape` reachable on 2 of 4 doc-leg calls, and all
  four leg-differing shapes' counts.
- **M-A reproduced byte-for-byte** — 1 call, 405 triples, 0 base facts; 0→8, 0→1, 0→0, 0→0.
- **M-C's census reproduced** — 1227 collected / 164 files; 45 files / 390 tests; 48 and 8
  (R101's own figures); 37 import-time / 11 function-body / 1 both; **59 → 1 confirmed** for
  `test_datagrid.py`; 31 proportional skips for `test_membrane_equiv.py`.
- **R97/R98/R99 registry rows correct** on the 7 final graphs — including who-wfa's
  `refused_licences=((1, 2),)`, 0 `tab:licenceRefused` triples, and NoLeakShape's 11 focus nodes
  with `iladub:asserted` absent. The guard is internally consistent: `registered-but-live: []`.
- **Loop 3 / D2 verified** — `.gitignore:44`, the skip at `test_vacuity_registry.py:314-315`,
  neither workflow fetching the corpus. **The R87 guard has never executed its assertions in CI.**
- Tally **94 rows / 18 closed** ✓. `probe_emitter_typing.py:111` parses `tab.ttl` only ✓.

## Unverifiable

- **CI run figures** (`31998036351` → 1103/120; `31998847175` → 1106/119) — GitHub Actions
  history, not queried.
- **The pySHACL leg** — deliberately unrun, standing since R87. All figures here are the rudof
  leg; focus-node counts are pure rdflib and engine-independent, and the exact agreement with
  M-B's rudof run supports that.
- **M-C's "confirmed from pytest 9.0.3's source"** — the *behaviour* was confirmed end to end
  (59 → 1); `_pytest/outcomes.py` was not read.
- **`compile.py:411`'s "4 spurious expansion requests on cbh-stem and 5 on apple"** — a
  counterfactual requiring a code change; not re-run.
