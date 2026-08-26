# The membrane reports its health — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `etkl:membraneHealth` a *derived* signal on a compiled document — Intact / Weakened /
Compromised, each reachable from evidence that is present — and flip `prog:criterion:holon:05` to
`met true` on that evidence.

**Architecture:** One `CONSTRUCT` does the deriving; everything else exists to give it evidence and to
prove it is not vacuous. `document.py`'s inline block `:1609–1626` (escalation-furnish → `_validate` →
raise) becomes **one named internal seam** that additionally mints a `etkl:MembraneValidation` act
(PROCEDURAL — an engine verdict extracted into RDF) and runs `vocab/queries/membrane-health.rq`
(AXIOM — open-world, evidence-positive) before it returns *or* raises. The raise becomes
`membrane.MembraneRefusal(AssertionError)` carrying `.graph`, so a refusing document's health is
reachable by a caller. Three new owned terms, one new shape, no change to any public signature.

**Tech Stack:** Python 3.12, rdflib 7.6.0, pySHACL/rudof via `membrane.validate`, SPARQL 1.1
`CONSTRUCT` executed by `interpret.run`. Runner is `./.venv/bin/python`, **never `python3`**.

**Spec:** `docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md` — revised and
**twice amended**; read its two amendment notes first. The plan argues *from* the spec and **cites**
it (`see spec §4.5`) rather than re-deriving it (CLAUDE.md § Plan authoring discipline, rule 6). Its
**§9** is binding on every test here — see § Rule-5 reconciliation.

**Rulings this plan is written against, cited and never re-derived:**
`…-b1-ruling.md` (B1), `…-b2-b3-b7-p1-rulings.md` (B2, B3, B7, P1),
`…-o2-finding6-rulings.md` (O2's `Compromised` leg = option (a′); findings 6–8 ship as R127–R129).

**Doc impact:** increment. Carried verbatim from spec § header — `etkl:Weakened`'s and
`etkl:MembraneHealth`'s `rdfs:comment`, three new owned terms, one new shape, `owl:versionInfo`
`0.1.0` → `0.2.0`, and `docs/holonic-interaction.md:160-161`. Queues for the next release; blocks
nothing in this loop.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **Runner:** `./.venv/bin/python -m pytest`. **NEVER `python3`** — it carries a different rdflib and
   no pyrudof. `pytest-timeout` is not installed (`--timeout` is not a valid flag) and `timeout` is not
   on this machine's PATH.
2. **The neurosymbolic gate (CLAUDE.md §8) is decided, not open.** Spec §6 classifies every step:
   the validation act and the exception plumbing are **PROCEDURAL**, the derivation is **AXIOM**
   (derivation form), the shape is **AXIOM** (constraint form), the tripwire is **not gated**. No step
   in this plan is NEURAL. **A tuned constant or tolerance anywhere in this loop is a review failure.**
3. **No bare decimal literal in any `.rq`.** Enforced with zero wiring by
   `tests/etkl/test_transform_gate.py:26-31` — it globs `vocab/queries/*.rq` (M6).
4. **Source ownership:** no `holon:` IRI may become a subject anywhere. `prov:` is not HGA and is
   already prefixed in `etkl-holons.ttl:9` (spec §4.7); all three `tests/test_source_ownership.py`
   assertions are HGA-specific (M7).
5. **Never derive from absence.** `Intact` is derived from an act that says `true`, never from a
   violation not being present (spec §4.3 invariant 1). The one closed-world guard is holon-scoped and
   justified inline in the `.rq` header.
6. **Falsification is mandatory, per task** (CLAUDE.md rule 4). Every task report carries a
   `## FALSIFICATION` block: remove or invert the thing the new test pins, show it **failing**,
   restore, show green. **No falsification evidence ⇒ the task review fails.**
7. **Every test in this plan is a PROPOSITION until the implementer falsifies it** (CLAUDE.md rule 1).
   A plan-supplied test you cannot make pass is a **plan defect** — say so in the task report and
   substitute the satisfiable form carrying the same force. **Never weaken an assertion to make a
   broken contract go green.**
8. **The public signature of `compile_document` does not change** (ruling (a′)). The seam is
   **internal**; no test-only parameter is added to a public API.
9. **The producer-side guard is not softened.** `MembraneRefusal` is a *subclass* of `AssertionError`;
   the raise stays unconditional (spec §4.5, CLAUDE.md § Producer-side guards).
10. **`R127` must survive this loop intact.** It is the only measured lever into a document-scope
    refusal, and O2's third leg + O7 run on it (spec §9, ruling 2). Do not "fix" the second
    `dec:rationale` while implementing.

---

## Measurements taken while writing this plan

Every load-bearing claim below was re-derived on **2026-08-25**, on `holon-05-plan` off `main`
@ `18226e7`, with the command inline (CLAUDE.md rule 2). Measurement was **delegated**; authorship was
not. Nothing here is quoted from the spec or a handoff without being re-run, **except** what
§ Named seams deliberately leaves open.

### M1 — Seam 1 CLOSED: all seven corpus documents measured, and §5.5's table still holds exactly

The five legs tuples spec §5.4 *inferred* from the R102 closure row are now **measured**, by spying on
`_legs_for_document` (the spy delegates to the original and returns its value unchanged) through a real
`compile_document`. `document.py:1624` resolves that name as a module global and `grep -rn
"_legs_for_document" src/` shows exactly one call site, so the captured tuple is what `_validate` got.

| document | legs (MEASURED) | triples | held | wall s | vs spec §5.5 |
|---|---|---|---|---|---|
| `graincorp-stem-2026-07-31` | `('tab','dec')` | 29,999 | 0 | 190.1 | MATCHES |
| `cbh-stem-2026-08-03` | `('tab','dec')` | 12,153 | 0 | 30.7 | MATCHES |
| `ons-index-of-services-2026-02` | `('dec',)` | 11,076 | 0 | 11.7 | MATCHES |
| `graincorp-capacity-2026-08-04` | `('dec',)` | 5,705 | 0 | 11.1 | MATCHES |
| `apple-fy2026q3-statements` | `('tab','dec')` | 3,788 | **11** | 36.8 | MATCHES |
| `bfs-population-bilan-2023` | `('dec',)` | 8,244 | **10** | 30.6 | MATCHES |
| `who-wfa-boys-zscore-0-5` | `('tab','dec')` | 8,098 | **3** | 45.4 | MATCHES |

**Seven of seven rows reproduce, and `('dec',)` is unconditional on all seven** — spec §5.4's
consequence holds on measured, not inferred, input. **4 Intact / 3 Weakened**, so **seam 5 closes with
seam 1**: the split has not moved. All seven are present and hash-match their `cor:sha256` pin.
Sequential corpus cost **356.4 s**; `graincorp-stem` alone is **190.1 s**, ~4× the next.

**A free corroboration of spec §5.6:** on all seven, `held` equals the *total* `CandidateConcept`
count — **zero candidates are reviewed by any `iladub:PromotionDecision` in any corpus document graph**.
That is why O3 may not use a corpus specimen (M4).

### M2 — Seam 2 CLOSED, and the census figure is CORRECTED upward

Enumerated with `superpowers:enumerating-before-claiming`, scope `src/ tests/ scripts/`, then widened
twice (`git grep` over all tracked `*.py`/`*.ipynb`; the repo has **no `conftest.py` at all**, and
`demo/` contains no `except` or `raises(`). 33 `except` clauses exist; 23 name exception types that are
not superclasses of `AssertionError`.

**The interceptor population is 17, not 1** — the spec's §2.4 census counted `except AssertionError`
and `pytest.raises` and **omitted nine `except Exception` sites**, which catch an `AssertionError` by
isinstance just as surely:

| kind | n | compile call inside the block? |
|---|---|---|
| `except AssertionError` | 1 — `tests/test_corpus.py:129` | **YES** (`_compiled` → `compile_document`), and it **re-raises** at `:130` |
| `except Exception` | 9 | 8 no; the 9th (`test_corpus.py:131`) is **unreachable** for an `AssertionError` — `:129` shadows it |
| `pytest.raises(AssertionError…)` | 6 | none — but `test_corpus_battery_unit.py:91` and `:103` clear it **by one line** (`_compiled` sits at `:90`/`:102`, above the `with`) |
| `@pytest.mark.xfail` with no `raises=` | 1 — `test_derivation_perf.py:146` | no |

**Two corrections to the spec, both inert behaviourally, neither inert for a reviewer:**
the count was 1 where it should read 17; and spec §2.4's *"the only catcher … re-raises"* is true only
if "catcher" excludes `except Exception` — the one catcher that **does** wrap a compile call is
`test_corpus.py:127-135`, and it re-raises.

**The decisive fact, and it is unanimous:**

```
$ grep -rnE "__class__|type\(.*\)\s*(is|==|!=)|is AssertionError|== AssertionError" src/ tests/ scripts/
src/iladub/etkl/membrane.py:266:        if type(o.value) is not type(reparsed.value):   # compares LITERAL VALUES
tests/test_corpus.py:133:  f"...compile CRASHED ({type(e).__name__}: {e})..."           # message only, unreachable branch
```

**No site anywhere depends on the exact `AssertionError` class.** Every interception in the repo is
isinstance-based (`except`, `pytest.raises` and `xfail` all are). `pyproject.toml
[tool.pytest.ini_options]` sets only `testpaths`, `pythonpath`, `markers` — no `xfail_strict`, no
`addopts`. **A subclass is transparent to all 17 sites.**

### M3 — Seams 3 and 4 CLOSED

**Seam 3 — `graph` identity at the raise site, MEASURED not read.** `compile_document` binds bare
`graph` **exactly once**:

```
$ grep -nE "^[[:space:]]*graph[[:space:]]*(=|\+=|,)" src/iladub/etkl/document.py
1224:    graph = Graph()          ← the ONLY binding
1279/1352/1362/1514/1609:  graph += …        ← rdflib __iadd__ is in place (self.addN(…); return self)
```

Instrumented on `two_page_unrelated_pdf`: `id()` of `_validate`'s first argument at `:1624` ==
`id(rep.graph)` → **`SAME OBJECT: True`**, and distinct from every page graph. **The page-scope answer
does NOT transfer:** `compile_tables` binds `graph` **twice** (`compile.py:574`, and the
datagrid-withdrawal rebind at `:1115`), exactly as spec §2.4 warned.

**Seam 4 — construction style, both unchanged.** Sole construction site each:
`DocumentReport` is **entirely by keyword** (`document.py:1636-1639`, 10 fields — 4 required, 6
defaulted, declared at `:236-247`); `CompilationReport` is **positional** (`compile.py:1175`, 5 fields
declared at `:361-368`). **The R73-defect-3 trap is closed on the document side and live on the page
side** — which is one more reason this loop does not touch `compile.py:1175`.

### M4 — O3's vehicle reproduced at document scope, and it is cheap

Spec §5.6's review measurement, re-run here (script:
`scratchpad/o3_vehicle.py`; `compile_document`'s signature does take proposers —
`document.py:1165-1166`):

```
$ ./.venv/bin/python .../o3_vehicle.py
DocumentReport fields: ['score','pages','chains','graph','recognized','arithmetic',
                        'refused_licences','repaired_bands','adopted','notes']
wall = 3.42 s   triples = 327
candidates = 2
held = 0
PromotionDecision = 2
```

`compile_document(caption_wrap.pdf, row_role_proposer=FakeRowRoleProposer(RowRoleProposal(
("furniture","continuation"), 0.85, "date caption + wrap fragment")))` at the **default
`validate_shapes=True`**, through the real membrane. **2 candidates, 2 promotions, 0 held → `Intact`.**
Delete the `FILTER NOT EXISTS` and held becomes 2 → `Weakened`: that is O3's falsification, and it is
the only document-scope vehicle in the tree where promoted ≠ 0 (M1).

### M5 — The spec's §4.3 query shape is SATISFIABLE, and every invariant it claims holds

`rdflib 7.6.0` executes `BIND(EXISTS{…})` inside a `CONSTRUCT` — this was **not** established anywhere
before, and the whole design rests on it. The spec's §4.3 shape (**cited, not reproduced here**) was run
through the real `interpret.run` over seven hand-built graphs (`scratchpad/rq_smoke.py`):

```
A conforming, no candidates        -> health=['Intact']       types=['CompiledDocumentHolon']  triples=2
B conforming, one HELD candidate   -> health=['Weakened']     types=['CompiledDocumentHolon']  triples=2
C non-conforming                   -> health=['Compromised']  types=['CompiledDocumentHolon']  triples=2
D conforming, candidate PROMOTED   -> health=['Intact']       types=['CompiledDocumentHolon']  triples=2
E conforms as plain Literal("false")   -> health=[]  types=[]  triples=0
F conforms as Literal("false", xsd:string) -> health=[]  types=[]  triples=0
G no validation act at all             -> health=[]  types=[]  triples=0
idempotent re-run equal as triple sets: True
```

A/B/C are **O1**; D is **O3**'s assertion; E/F are **O8**'s read side (no health triple, and
specifically **not `Intact`**); G is **O4**; the last line is **O5**. Each oracle's *setup* is therefore
measured-constructible (CLAUDE.md rule 5), not assumed.

### M6 — Wiring measurements the tasks depend on

- **`etkl-shapes.ttl` is not loaded by the membrane, and neither is `etkl-holons.ttl`.**
  `_TAB_SHAPE_FILES = ("tab-shapes.ttl","tab-physical-shapes.ttl")` (`compile.py:398`),
  `_DEC_SHAPE_FILES = ("dec-shapes.ttl","iladub-shapes.ttl","escalation-shapes.ttl")` (`:421`), and
  `_FULL_ONT` parses `tab.ttl` + `dec.ttl` + `iladub.ttl` only (`:441-453`). **Five shape files of the
  ten in `vocab/shapes/`.** This is spec §2.1's and §4.8's premise, re-measured — and it is also why
  `MembraneHealthShape` cannot enter the SHACL vacuity registry's population (spec §2.8).
- **`etkl-shapes.ttl` already declares every prefix the new shape needs** (`etkl:`, `sh:`, at `:1-4`).
  No prefix edit.
- **The `.rq` decimal lint covers a new file with zero wiring:** `test_transform_gate.py:26-31` runs
  `glob.glob(os.path.join(QUERIES, "*.rq"))` and strips `#`-comments first (`:19-23`). Spec §2.7
  confirmed.
- **`ESCALATION_FURNISH_RQ = _QUERIES / "escalation-furnish.rq"` is at `document.py:130`** — the one
  precedent for where `MEMBRANE_HEALTH_RQ` goes. `interpret.run(path, *graphs)` copies every input graph
  into a fresh union (`interpret.py:19-30`), so one call over the 29,999-triple stem is a full 30k-triple
  copy (spec §2.7, review B7).
- **`_validate` and `_refusal_message` are imported into `document.py` by name at `:110-111`.**

### M7 — `tests/test_source_ownership.py` is HGA-only, and `test_vocab_shapes.py` discovers nothing

Three test functions (`:42`, `:58`, `:77`), all keyed on `w3id.org/holon`. `prov:` is unaffected, and
nothing constrains which file a term lives in — spec §4.7 confirmed. Separately,
`tests/test_vocab_shapes.py` is 66 lines of **four hard-coded pairs, no glob and no `parametrize`**:
positives live in `examples/*.ttl`, negatives in `tests/*-bad.ttl`, and `etkl-shapes.ttl` is validated
against **`etkl.ttl`** as its ontology graph (`:35`, `:44`). **`etkl-holons.ttl` appears nowhere in that
file** — so Task 5's two new functions must pass it explicitly or the shape targets nothing.

### M8 — Seam 6's two open questions are CLOSED, and both answers are better than the ruling assumed

**(a) The unmutated re-entry is EXACTLY a no-op — the control arm exists.** On
`recognized_pair_plus_escalating_page_pdf` (compile **6.15 s**), running `escalation-furnish.rq` a
second time over a graph already carrying its own output:

```
[control] second furnish: 0.02 s; CONSTRUCT emitted 9 triples
[control] graph triples BEFORE=576 AFTER=576 (grew by 0)
[control] triples that were NOT already present: 0
[control] _validate(graph, ('tab','dec')) -> conforms=True refusing=()  (1.15 s)
```

Structural, not incidental: `?req` is bound `IRI(CONCAT(STR(?d),"-expansion"))`, a pure function of
`?d`, and the query's own header says so at `escalation-furnish.rq:56-59`.

**And the mutated arm, from the same script, same base graph:**

```
[mutate] ONE triple added: graph 576 -> 577
[mutate] BEFORE re-furnish: dec:condition count on …-d4-expansion = 1
[mutate] re-furnish: 577 -> 578; ADDED (…-d4-expansion, dec:condition, "a second rationale…"@fr)
[mutate] AFTER  re-furnish: dec:condition count = 2
[mutate] _validate(graph, ('tab','dec')) -> conforms=False refusing=('dec',)  (1.21 s)
         sh:resultMessage "An event must declare exactly one condition."
```

**(b) CORPUS documents DO carry the lever — the ruling's worry does not survive measurement.**
Census over the five cheap corpus documents (`chose-escalated` / furnished `dec:ExpansionRequest`):

| document | DecisionHolons | chose `escalated` | superseded | ExpansionRequests | lever? |
|---|---|---|---|---|---|
| `graincorp-capacity` | 18 | 0 | 0 | 0 | no |
| `ons-index-of-services` | 218 | 0 | 0 | 0 | no |
| `bfs-population-bilan` | 232 | 10 | 0 | **10** | **YES** |
| `who-wfa-boys` | 81 | 3 | 0 | **3** | **YES** |
| `apple-fy2026q3` | 119 | 15 | 5 | **10** | **YES** |

`graincorp-stem` and `cbh-stem` were **not run** — stated, not guessed. Confirmed end-to-end on a real
corpus document, no monkeypatch, `validate_shapes` at its default:

```
===== bfs-population-bilan-2023 (CORPUS) =====  triples=8244  legs=('dec',)
[control] re-furnish: 8244 -> 8244 (grew by 0);  _validate -> conforms=True  refusing=()
[mutate]  ONE triple added: 8244 -> 8245; re-furnish 8245 -> 8246; dec:condition count = 2
[mutate]  _validate -> conforms=False refusing=('dec',)
```

**Only a non-superseded escalation is a lever.** `caption_wrap_report_pdf` and
`currency_marker_escalating_pdf` each *have* an escalated decision and are `LEVER=False`, because
adoption supersedes it and `escalation-furnish.rq`'s supersession guard furnishes nothing.

**The cheapest legitimate vehicle in the tree is `false_transposed_pdf` — 1.12 s**, `legs=('dec',)`,
lever present, control conforms / mutation refuses (measured, above). That is **5.5× cheaper** than the
fixture seam 6 proved the lever on, and **27× cheaper** than `bfs`.

**A caveat the plan carries rather than hides:** `section_facts` is a local of `compile_document` that
`DocumentReport` does not expose, so the re-entry runs above used `_legs_for_document`'s output where
`recognized` was truthy, and inferred `section_facts=False` from `adopted=()`/`repaired_bands=()`
elsewhere. Both arms were therefore **re-run under the forced superset `('tab','dec')`** and the
verdicts are unchanged (`conforms=True refusing=()` / `conforms=False refusing=('dec',)`). The
re-entry was also driven by calling the four steps in order on a copied graph — **not** through an
extracted seam, because none exists yet. That absence is what Task 2 fixes.

### M9 — A HAZARD NEITHER THE SPEC NOR THE RULING NAMES: re-entry mints a SECOND `sh:conforms`

**This plan's own finding, and it is load-bearing for Task 2.** Ruling (a′) has O2's third leg and O7
re-enter the seam on **a real compiled document graph** — a graph that, once Task 2 ships, *already
carries the validation act its first pass minted*. The act IRI is `<{doc}#membrane-validation>`, a
function of the doc URI, so a second mint lands on the **same subject**. Measured
(`scratchpad/rq_reentry.py`):

```
run 1 health: ['Intact']
after re-entry, sh:conforms values = ['false', 'true']
after re-entry, health = ['Compromised', 'Intact']
health triples constructed = 3
```

**One document, two health values, and nothing at runtime refuses it** — `MembraneHealthShape` would
(`sh:maxCount 1`), but §4.8 deliberately does not wire it into the membrane. The mint must therefore be
**idempotent by replacement**, and Task 2 states that as an invariant with its own oracle (**O10**).
This is a defect the oracles ruling (a′) prescribes would have *created*; it is found here rather than
in review because the query shape was run before the plan was written.

---

## Named seams — MEASURE these before writing the call, do not assume the answer

Everything above is closed. These are not, and each names *the fact to measure*, not the answer
(CLAUDE.md rule 3):

- **S1 (Task 4).** *Does `apple-fy2026q3-statements`' lever actually refuse?* M8 measured apple as
  lever-**applicable** (10 furnished requests) but ran the end-to-end mutation only on `bfs` and
  `false_transposed_pdf`. O2 needs apple compiled anyway for its `Weakened` leg, so one compile can
  serve two legs — **but only if apple's mutation refuses.** Measure before writing the call.
  Measured-positive fallbacks, in cost order: `false_transposed_pdf` (1.12 s), `bfs` (30.6 s).
- **S2 (Task 2).** *Which `dec:rationale`-bearing decision does the mutation target on the chosen
  vehicle, and is it non-superseded?* M8 shows a superseded escalation furnishes nothing. Read the
  census off the graph in the test; never hardcode a region URI from this plan.
- **S3 (Task 2).** *Does the extracted seam change what `DocumentReport` receives?* M3 measured
  `graph` is one object bound once and identical to `rep.graph` **today**. The extraction moves the
  `+=` inside a function — re-measure `id()` identity after the extraction, do not carry M3 across it.
- **S4 (Task 6).** Held open pending the registry measurement — see Task 6.
- **S5 (Task 7).** *Does `tests/test_doc_governance.py` still pass after `docs/holonic-interaction.md`
  is edited?* It was `4 passed` on the parent branch. The membrane checks nav integrity and
  doc-impact registration; run it, do not reason about it.

---

## File Structure

**Create**

| path | responsibility |
|---|---|
| `vocab/queries/membrane-health.rq` | the derivation (AXIOM). Spec §4.3 is its contract; the implementer writes the text |
| `tests/etkl/test_membrane_health.py` | O1–O8, O10. Its `test_compiled_document_reports_membrane_health` is pre-declared by the manifest and must exist under **exactly** that name |
| `examples/membrane-health-conformant.ttl` | O9's positive — a `etkl:CompiledDocumentHolon` with one legal health value |
| `tests/membrane-health-bad-two-values.ttl` | O9's negative 1 — two health values on one subject (`sh:maxCount 1`) |
| `tests/membrane-health-bad-outside-enum.ttl` | O9's negative 2 — a value outside the three individuals (`sh:in`) |

**Modify**

| path | change |
|---|---|
| `vocab/ontology/etkl-holons.ttl` | +3 terms; `etkl:Weakened`'s comment (`:82`) and `etkl:MembraneHealth`'s (`:77`) amended; `owl:versionInfo` `:33` → `0.2.0` |
| `vocab/shapes/etkl-shapes.ttl` | +`etkl:MembraneHealthShape` (no prefix edit — M6) |
| `src/iladub/etkl/membrane.py` | +`MembraneRefusal` |
| `src/iladub/etkl/document.py` | +`MEMBRANE_HEALTH_RQ` beside `:130`; `:1609–1626` extracted into `_seal`; `_seal` called from `compile_document` |
| `tests/test_vocab_shapes.py` | +2 hand-wired functions (nothing discovers them — M7) |
| `tests/etkl/test_vacuity_registry.py` | Task 6's tripwire, **or** the fallback |
| `tests/arc-manifest.ttl` | `holon:05` flipped; `:1337`'s `75-86` citation corrected to `75-89` |
| `docs/holonic-interaction.md` | `:160-161` out of *Planned work* (heading `:158`) into *What is built* (`:145`), reworded |
| `docs/superpowers/residues.md` + `-open.md` + `-closed.md` | R126 closed and **moved**; R127–R129 raised |

**Not touched, deliberately:** `src/iladub/etkl/compile.py` (the page raise site `:1173`, the page skip
guard `:1167-1170`, and the positional `CompilationReport(…)` at `:1175` all stay as they are —
spec §9, M3), and `src/iladub/feed.py:643` (spec §9).

## Interfaces

Signatures and invariants only. **The bodies are the implementer's** (CLAUDE.md rule 1).

**Task 2 produces — `src/iladub/etkl/membrane.py`:**

```python
class MembraneRefusal(AssertionError):
    """Raised when the document membrane refuses; carries the graph it refused."""
    graph: Graph                 # the refused graph, health triple included
    legs: tuple[str, ...]        # _validate's third element: the legs that REFUSED
```

- `str(exc)` **is unchanged** — still exactly `_refusal_message("document-level facts", legs, text)`.
- It is a **subclass**, so all 17 interceptors of M2 keep working untouched.

**Task 2 produces — `src/iladub/etkl/document.py`:**

```python
def _seal(graph: Graph, legs: tuple[str, ...], validate_shapes: bool) -> None
```

Mutates `graph` **in place**, returns `None`, raises `MembraneRefusal` on a document-scope refusal.
Its invariants, each pinned by a named oracle:

1. Runs `ESCALATION_FURNISH_RQ` into `graph` **unconditionally** — before any validation, and
   regardless of `validate_shapes`. This preserves the reason stated at `document.py:1596-1608`
   verbatim: the membrane must be able to refuse what the furnish writes.
2. `validate_shapes=False` ⇒ **returns after the furnish, having minted nothing** — no validation act,
   no health triple, no type triple (spec §4.5 row 3; **O4**).
3. Otherwise mints the validation act of spec §4.2 **idempotently by replacement**: after `_seal`
   returns or raises, `<{doc}#membrane-validation>` carries **exactly one** `sh:conforms` (**M9**,
   **O10**).
4. The conformance literal is built from the Python `bool` `_validate` returned — **never**
   `str(conforms)` (spec §4.2; **O8** mint side).
5. `etkl:refusingLeg` carries `_validate`'s **third element verbatim**, so a conforming validation
   carries **no leg at all** (spec §2.3).
6. Runs `MEMBRANE_HEALTH_RQ` and adds its result to `graph` **on both paths**, before returning and
   before raising (**O7**).
7. `graph` is the same object on the way out as on the way in — **S3**.

**Task 2 also produces the call-site fact Task 4 depends on:** `compile_document` computes
`_legs_for_document(recognized, section_facts)` **at the call site** and passes the tuple in.
**S6 — MEASURE, do not assume:** confirm that neither `recognized` nor `section_facts` is mutated
between where they are computed and `:1609`, so hoisting the `_legs_for_document` call above the
furnish cannot change its value. If either is mutated, pass `(recognized, section_facts)` instead and
compute the legs inside `_seal`.

**Task 3 produces — `vocab/queries/membrane-health.rq`,** run as
`interpret.run(MEMBRANE_HEALTH_RQ, graph)`. Contract: **spec §4.3**, whose five invariants are
numbered there. Do not re-derive them here; cite them. M5 measured the shape satisfiable.

## Rule-5 reconciliation — every plan-supplied test against spec §9

CLAUDE.md rule 5: a plan-supplied test asserting behaviour the spec scoped **out** is a contradiction
the plan author is uniquely placed to catch and uniquely unlikely to. Checked, item by item:

| spec §9 says this loop does NOT… | does any test here assert it? |
|---|---|
| give the grounding portal a health signal | **No.** No test touches `feed.py` or `ground_document`. |
| give page-scope graphs health, or mint at `compile.py:1173` | **No.** O4 and O6 assert only at document scope; **O11 asserts the page site is UNCHANGED** — the inverse, which is legitimate. |
| fix the shared `_DOC` IRI | **No.** Every test uses the one `_DOC`; none asserts two documents get different subjects. |
| widen `membrane.validate`'s `(bool, str)` return | **No.** `_seal` reads `_validate`'s existing 3-tuple. |
| rewrite the vacuity registry's SHACL machinery | Task 6's fallback exists precisely so no test forces this. |
| score the `holon:05 → holon:01` edge | **No.** Task 7 adds `prog:oracleArtifact` and **notes**, never measures, the edge. |
| fix the `IndexError` on `legs=()` | **No.** No test calls `_validate` with an empty tuple. |
| fix **`R127`** | **No — and this is the live trap.** O2's third leg and O7 *use* R127 as their lever. A test that "fixed" the second `dec:rationale` would delete its own subject. Global Constraint 10. |
| add a fourth health value / report health where nothing was validated | **No.** O4 asserts exactly the opposite. |

**The one that would have bitten.** Spec §7's O2 was amended *because* `Compromised` is not reachable
from public input — so **a test that compiles a public document and expects `Compromised` cannot pass,
ever.** M8 measured why: the page gate at `compile.py:1173` fires first on every tab-side lever, and no
compile can produce a second `dec:rationale` (`BandRecorder.record` writes exactly one, and the four
decision-URI namespaces are disjoint). Task 4's O2 third leg therefore re-enters `_seal`; it does not
compile and hope.

---

## Task ordering, and the one cross-task dependency

`1 → 2 → 3 → 4`, then `5`, `6`, `7` in any order. **Task 3's `.rq` cannot be wired before Task 2's
`_seal` exists** (there is no act for it to read) and **Task 4 cannot run before Task 3** (there is no
health triple to assert on). Tasks 5–7 touch disjoint files and depend only on Task 1's terms.

---

## Task 1: The three owned terms and the semantic amendment (spec §4.6, §4.7)

**Files:**
- Modify: `vocab/ontology/etkl-holons.ttl` (`:33`, `:77`, `:82`, and an append)
- Test: `tests/test_source_ownership.py` (existing, must stay green), `tests/test_vocab_shapes.py`
  (existing, must stay green)

**Interfaces:**
- Consumes: nothing.
- Produces: `etkl:CompiledDocumentHolon` (`⊑ etkl:DocumentHolon`), `etkl:MembraneValidation`
  (`⊑ prov:Activity`), `etkl:refusingLeg` (an `owl:DatatypeProperty`, `rdfs:range xsd:string`).
  Tasks 2, 3, 5 and 6 all name these IRIs.

- [ ] **Step 1: Declare the three terms.** Append to `vocab/ontology/etkl-holons.ttl`. Requirements,
      not text: `etkl:CompiledDocumentHolon` is a concrete `owl:Class`, `rdfs:subClassOf
      etkl:DocumentHolon` — which is what puts it inside `etkl:membraneHealth`'s declared `rdfs:domain`
      (`:88`, the abstract parent declared `:43-45`). Its `rdfs:comment` says what the **compile-scope
      product** is and, per B8, **must not claim the graph is fully read** (see spec §4.4's last
      paragraph and the B1 ruling). `etkl:MembraneValidation` is `rdfs:subClassOf prov:Activity` —
      `@prefix prov:` is already at `:9` and used by no triple, so this is its first real use and no
      prefix edit is needed (M6/M7). `etkl:refusingLeg`'s range is `xsd:string` because a leg identity
      is a code-level key (`{"tab","dec"}`, `compile.py:516`) — spec §4.2.

- [ ] **Step 2: Amend the two comments — this is a semantic amendment, not a tweak (B3 ruling).**
      `etkl:Weakened`'s `rdfs:comment` at `:82` currently reads *"Interior conforms but warnings are
      present."* — **underivable**, because there is no `sh:severity` anywhere in the authored tree
      (spec §2.5). `etkl:MembraneHealth`'s at `:77` reads *"…the result of validating its interior
      against its membrane"*, which the design also contradicts. Reword both per **spec §4.4's last
      paragraph**: `Weakened` means **propositions are held at the membrane**; `Intact` means **nothing
      is held**, never *"fully read"*. **The gloss *"not everything that reached the boundary crossed
      it"* is FALSE and must not appear** — `graincorp-stem` books 77 escalated tokens, mints zero
      candidates, and is correctly `Intact` (M1 reproduces its 29,999/0).

- [ ] **Step 3: Bump `owl:versionInfo` `:33` from `"0.1.0"` to `"0.2.0"`.** It covers Step 1's three
      terms and Step 2's two amendments together.

- [ ] **Step 4: Run the two suites that can see this file.**

Run: `./.venv/bin/python -m pytest -q tests/test_source_ownership.py tests/test_vocab_shapes.py tests/test_hga_alignment.py`
Expected: PASS. M7 measured that all three `test_source_ownership.py` assertions are HGA-keyed and
`prov:` is unaffected; **the one live risk is that file's parse arm (`:67-68`), where a Turtle syntax
error surfaces as an `AssertionError`** (spec §4.7).

- [ ] **Step 5: FALSIFICATION.** No new test ships in this task, so falsify the *parse* arm: introduce
      a deliberate Turtle syntax error in the appended block, show `tests/test_source_ownership.py`
      **failing** at `:67-68`, restore, show green. Record both outputs.

- [ ] **Step 6: Commit.**

```bash
git add vocab/ontology/etkl-holons.ttl
git commit -m "vocab(etkl): CompiledDocumentHolon, MembraneValidation, refusingLeg; amend the health model"
```

---

## Task 2: `MembraneRefusal` and the extracted seam (spec §4.2, §4.5; ruling (a′))

**Files:**
- Modify: `src/iladub/etkl/membrane.py` (append the class)
- Modify: `src/iladub/etkl/document.py` (`:130` area; extract `:1609–1626`; call it)
- Test: `tests/etkl/test_membrane_health.py` (create)

**Interfaces:**
- Consumes: Task 1's `etkl:MembraneValidation`, `etkl:refusingLeg`.
- Produces: `membrane.MembraneRefusal`, and `document._seal(graph, legs, validate_shapes) -> None`
  — signature and seven invariants in § Interfaces above. Task 3 adds invariant 6's query; Task 4
  calls `_seal` directly.

- [ ] **Step 1: MEASURE S6 and S3's precondition before writing a line.** Confirm `recognized` and
      `section_facts` are not mutated between their computation and `:1609` (§ Interfaces, S6), and
      record `id(graph)` at `:1609` and at the `DocumentReport(…)` call **before** the refactor, so
      Step 6 can show it unchanged. Paste both into the task report.

- [ ] **Step 2: Write the failing tests.** In `tests/etkl/test_membrane_health.py`. These are
      **propositions** (Global Constraint 7); if one cannot pass, you have found a plan defect — say so
      and substitute the satisfiable form carrying the same force.

```python
"""holon:05 — the membrane reports its health. Oracles O1-O11 (spec 2026-08-25 §7).

Vehicles are chosen for cost, and every one of them is MEASURED (plan M1, M4, M8):
`false_transposed_pdf` compiles at document scope in ~1.1 s and carries the refusal lever;
the corpus specimens are used only where reachability ON REAL INPUT is the claim (O2).
"""
import os

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

from iladub.etkl import membrane
from iladub.etkl.compile import _DOC, _validate
from iladub.etkl.document import compile_document, _legs_for_document, _seal
from tests.etkl import fixtures as F

ETKL = Namespace("https://w3id.org/iladub/etkl#")
ILADUB = Namespace("https://w3id.org/iladub#")
SH = Namespace("http://www.w3.org/ns/shacl#")
PROV = Namespace("http://www.w3.org/ns/prov#")
ACT = URIRef(f"{_DOC}#membrane-validation")


def _cheap_document(tmp_path, name="false_transposed.pdf"):
    """The cheapest document-scope vehicle in the tree: 1.12 s, legs ('dec',), and it
    carries a NON-SUPERSEDED escalated decision — i.e. the refusal lever (plan M8)."""
    p = os.path.join(str(tmp_path), name)
    F.false_transposed_pdf(p)
    return compile_document(p)


def test_membrane_refusal_is_an_assertionerror_subclass():
    """O11 (half): the producer-side guard is not softened. Every one of the repo's 17
    AssertionError interceptors is isinstance-based (plan M2), so a subclass is
    transparent — but only if it really is one."""
    assert issubclass(membrane.MembraneRefusal, AssertionError)


def test_validate_shapes_false_mints_no_validation_act(tmp_path):
    """O4 (half — the health half lands in Task 3): no validation means no act. Absence,
    never a fourth state (spec 4.5, third row)."""
    p = os.path.join(str(tmp_path), "false_transposed.pdf")
    F.false_transposed_pdf(p)
    rep = compile_document(p, validate_shapes=False)
    assert (ACT, RDF.type, ETKL.MembraneValidation) not in rep.graph
    assert list(rep.graph.objects(ACT, SH.conforms)) == []


def test_the_conformance_literal_is_xsd_boolean(tmp_path):
    """O8, mint side (review B6 — the one finding that fails UPWARD). A Literal('false')
    with no datatype makes a REFUSING membrane report Intact, because SPARQL's effective
    boolean value of a non-empty string is true."""
    rep = _cheap_document(tmp_path)
    values = list(rep.graph.objects(ACT, SH.conforms))
    assert len(values) == 1, values
    assert values[0].datatype == XSD.boolean, values[0]
    assert values[0].toPython() is True


def test_a_conforming_validation_names_no_refusing_leg(tmp_path):
    """Spec 2.3: _validate's third element is the legs that REFUSED, and it is () on every
    conforming validation. A leg appears only when it has something to say."""
    rep = _cheap_document(tmp_path)
    assert list(rep.graph.objects(ACT, ETKL.refusingLeg)) == []


def test_re_entering_the_seam_leaves_exactly_one_conformance_value(tmp_path):
    """O10 — plan M9, a hazard neither the spec nor the (a') ruling names. O2's third leg
    and O7 re-enter _seal on a graph that ALREADY carries the act its first pass minted.
    The act IRI is a function of the doc URI, so a second mint lands on the SAME subject:
    unless the mint replaces, one document ends up carrying sh:conforms true AND false,
    and therefore Intact AND Compromised, with nothing at runtime to refuse it."""
    rep = _cheap_document(tmp_path)
    g = rep.graph
    legs = _legs_for_document(rep.recognized, False)
    _seal(g, legs, True)                       # unmutated re-entry: a no-op (plan M8)
    values = list(g.objects(ACT, SH.conforms))
    assert len(values) == 1, values
    assert values[0].toPython() is True
```

- [ ] **Step 3: Run them to verify they fail.**

Run: `./.venv/bin/python -m pytest -q tests/etkl/test_membrane_health.py`
Expected: FAIL — `ImportError`/`AttributeError` on `membrane.MembraneRefusal` and `document._seal`.

- [ ] **Step 4: Add `MembraneRefusal` to `src/iladub/etkl/membrane.py`.** Signature and invariants in
      § Interfaces. **Classify it in the docstring as PROCEDURAL** (exception plumbing; no decision
      lives in it) per spec §6 and CLAUDE.md §8 — that file's module docstring is the precedent for
      how the classification is worded.

- [ ] **Step 5: Extract the seam.** Move `document.py:1609–1626` into `_seal`, add
      `MEMBRANE_HEALTH_RQ` beside `ESCALATION_FURNISH_RQ` at `:130` (Task 3 uses it), and mint the
      validation act of **spec §4.2** — do not re-derive its shape here, and note the mint is
      **idempotent by replacement** (invariant 3). `compile_document` calls `_seal(graph,
      _legs_for_document(recognized, section_facts), validate_shapes)` where the block used to be.
      **Carry the comment block at `:1596-1608` and `:1611-1622` with the code** — it is the measured
      record of why the furnish is unconditional and why the gate is per-leg, and it belongs beside the
      lines it explains.
      **Two things that do NOT change:** the raise stays unconditional (Global Constraint 9), and
      `str(exc)` stays exactly `_refusal_message("document-level facts", legs, text)`.

- [ ] **Step 6: Run the tests and the seam's own regression set.**

Run: `./.venv/bin/python -m pytest -q tests/etkl/test_membrane_health.py tests/etkl/test_escalation_wiring.py tests/etkl/test_escalation_furnish.py tests/etkl/test_document_membrane_gate.py tests/etkl/test_membrane_equiv.py`
Expected: PASS. Then re-measure `id(graph)` per **S3** and paste it beside Step 1's figure — the
extraction moves the `+=` inside a function, and M3's identity finding does **not** survive that move
by assumption.

- [ ] **Step 7: FALSIFICATION.** Four inversions, each shown failing then restored:
      (a) make `MembraneRefusal` subclass `Exception` instead of `AssertionError` →
      `test_membrane_refusal_is_an_assertionerror_subclass` **and** `tests/test_corpus.py:129`'s
      re-raise path must change behaviour; (b) mint the act unconditionally, ignoring
      `validate_shapes` → `test_validate_shapes_false_mints_no_validation_act` fails; (c) mint with
      `Literal(str(conforms))` → `test_the_conformance_literal_is_xsd_boolean` fails; (d) make the mint
      **add** instead of replace → `test_re_entering_the_seam_leaves_exactly_one_conformance_value`
      fails with two values. **(d) is the one that matters most** — it is the defect ruling (a′) would
      otherwise have created (M9).

- [ ] **Step 8: Commit.**

```bash
git add src/iladub/etkl/membrane.py src/iladub/etkl/document.py tests/etkl/test_membrane_health.py
git commit -m "feat(etkl): MembraneRefusal carries the refused graph; extract the document seal seam"
```

---

## Task 3: The derivation, and the pre-declared oracle (spec §4.3)

**Files:**
- Create: `vocab/queries/membrane-health.rq`
- Modify: `src/iladub/etkl/document.py` (`_seal` invariant 6 only)
- Test: `tests/etkl/test_membrane_health.py` (extend)

**Interfaces:**
- Consumes: Task 1's three terms; Task 2's `_seal`, `MEMBRANE_HEALTH_RQ`, and the validation act.
- Produces: the health triple and the `etkl:CompiledDocumentHolon` type triple in every validated
  document graph. Task 4 asserts on both; Task 5's shape targets the type; Task 6 registers the
  query's promotion clause.

- [ ] **Step 1: Write the failing tests.** Every one of these was measured constructible in M5 — the
      case letters below are M5's rows.

```python
def test_compiled_document_reports_membrane_health(tmp_path):
    """THE PRE-DECLARED ORACLE (tests/arc-manifest.ttl:359 — this name is fixed and the
    manifest names it; do not rename it). A compiled document carries exactly one health
    value, and it is one of the three."""
    rep = _cheap_document(tmp_path)
    doc = URIRef(_DOC)
    assert (doc, RDF.type, ETKL.CompiledDocumentHolon) in rep.graph
    values = list(rep.graph.objects(doc, ETKL.membraneHealth))
    assert len(values) == 1, values
    assert values[0] in (ETKL.Intact, ETKL.Weakened, ETKL.Compromised), values[0]


def test_the_three_values_discriminate(tmp_path):
    """O1 — THE FALSIFYING ORACLE. Three hand-built graph states must yield three DIFFERENT
    values. Expected values are computed BY HAND from the fixture (spec 3), never by
    running the query and recording what it said. Falsify by collapsing the IF to a
    constant: this test must fail."""
    from iladub.etkl import interpret
    from iladub.etkl.document import MEMBRANE_HEALTH_RQ

    def act(conforms):
        g = Graph()
        g.add((ACT, RDF.type, ETKL.MembraneValidation))
        g.add((ACT, PROV.used, URIRef(_DOC)))
        g.add((ACT, SH.conforms, Literal(conforms)))
        return g

    def health(g):
        return list(interpret.run(MEMBRANE_HEALTH_RQ, g).objects(None, ETKL.membraneHealth))

    conforming_empty = act(True)                                    # hand-computed: Intact
    conforming_held = act(True)                                     # hand-computed: Weakened
    conforming_held.add((URIRef(f"{_DOC}#c1"), RDF.type, ILADUB.CandidateConcept))
    refusing = act(False)                                           # hand-computed: Compromised

    assert health(conforming_empty) == [ETKL.Intact]
    assert health(conforming_held) == [ETKL.Weakened]
    assert health(refusing) == [ETKL.Compromised]
    assert len({str(health(g)[0]) for g in
                (conforming_empty, conforming_held, refusing)}) == 3


def test_a_document_compiled_without_the_membrane_has_no_health(tmp_path):
    """O4 — ABSENCE, NEVER A FOURTH STATE. No validation means no act means the WHERE has
    no support means no health triple. `validate_shapes` is the only route into this
    state — spec 5.4 refuted the zero-legs one."""
    p = os.path.join(str(tmp_path), "false_transposed.pdf")
    F.false_transposed_pdf(p)
    rep = compile_document(p, validate_shapes=False)
    assert list(rep.graph.objects(URIRef(_DOC), ETKL.membraneHealth)) == []
    assert (URIRef(_DOC), RDF.type, ETKL.CompiledDocumentHolon) not in rep.graph


def test_health_is_re_derived_not_stored(tmp_path):
    """O5 — NOT A STORED LABEL. Strip the health triple and the type triple, re-run the
    .rq, and the re-derived triples equal what was stripped, compared AS SETS OF TRIPLES
    (RDF has no byte identity without canonicalisation — spec 3). This is explicitly NOT
    the falsifying oracle, and it says nothing about the validation act."""
    from iladub.etkl import interpret
    from iladub.etkl.document import MEMBRANE_HEALTH_RQ

    rep = _cheap_document(tmp_path)
    g, doc = rep.graph, URIRef(_DOC)
    stripped = set(g.triples((doc, ETKL.membraneHealth, None))) | \
               set(g.triples((doc, RDF.type, ETKL.CompiledDocumentHolon)))
    assert stripped, "nothing to strip — the compile did not mint health"
    for t in stripped:
        g.remove(t)
    assert set(interpret.run(MEMBRANE_HEALTH_RQ, g)) == stripped


def test_a_slipped_datatype_yields_no_health_rather_than_intact(tmp_path):
    """O8, READ side (review B6 — the only finding that failed UPWARD). A validation act
    carrying Literal('false') with no datatype, or xsd:string, must yield NO health triple
    — and specifically NOT Intact, which is what SPARQL's effective boolean value of a
    non-empty string would otherwise produce. This fails DOWNWARD, into the silence spec
    4.5's third row already licenses."""
    from iladub.etkl import interpret
    from iladub.etkl.document import MEMBRANE_HEALTH_RQ

    for slipped in (Literal("false"), Literal("false", datatype=XSD.string)):
        g = Graph()
        g.add((ACT, RDF.type, ETKL.MembraneValidation))
        g.add((ACT, PROV.used, URIRef(_DOC)))
        g.add((ACT, SH.conforms, slipped))
        out = interpret.run(MEMBRANE_HEALTH_RQ, g)
        assert len(out) == 0, (slipped, list(out))
```

- [ ] **Step 2: Run them to verify they fail.**

Run: `./.venv/bin/python -m pytest -q tests/etkl/test_membrane_health.py`
Expected: FAIL — no `MEMBRANE_HEALTH_RQ` target file, no health triples.

- [ ] **Step 3: Write `vocab/queries/membrane-health.rq`.** **Its contract is spec §4.3** — the five
      numbered invariants there, not restated here. Its **header** must carry, in the
      `escalation-furnish.rq:10-12` form (`# GATE (CLAUDE.md §8):`, the n=1 spelling spec §2.7 chose
      and this file mirrors):
      (a) the classification — **AXIOM, derivation form**, open world, evidence-positive, idempotent;
      (b) the **holon-scoped justification** for the `FILTER NOT EXISTS`, in the form
      `escalation-furnish.rq:44-47` uses;
      (c) the **SITE CONSTRAINT on the caller**, in the form `escalation-furnish.rq:48-49` uses —
      *run over one document's graph, never a union* — **with the collision as its stated reason**:
      `_DOC` is one constant IRI shared by every document (`compile.py:22`), so a union puts two health
      values on one subject (spec §4.3 invariant 3);
      (d) **the test that pins each claim**, as `escalation-furnish.rq:31,34` does.
      No bare decimal literal (Global Constraint 3).

- [ ] **Step 4: Wire it — `_seal` invariant 6.** Run it on **both** paths, before returning and before
      raising.

- [ ] **Step 5: Run the tests and the transform gate.**

Run: `./.venv/bin/python -m pytest -q tests/etkl/test_membrane_health.py tests/etkl/test_transform_gate.py`
Expected: PASS. The gate covers the new `.rq` with zero wiring (M6).

- [ ] **Step 6: FALSIFICATION.** Three inversions: (a) collapse the `IF` to a constant →
      `test_the_three_values_discriminate` fails; (b) drop the `datatype(?conforms) = xsd:boolean`
      filter **and** mint with `Literal(str(conforms))` → `test_a_slipped_datatype_yields_no_health…`
      fails, **and the failure must be the silent-`Intact` one** (record which value it reported —
      that is the whole point of B6); (c) mint the health triple in `_seal` as a literal constant
      instead of running the query → `test_health_is_re_derived_not_stored` fails.

- [ ] **Step 7: Commit.**

```bash
git add vocab/queries/membrane-health.rq src/iladub/etkl/document.py tests/etkl/test_membrane_health.py
git commit -m "feat(etkl): derive membrane health from the validation act and held propositions"
```

---

## Task 4: The real-input oracles (spec §7 O2, O3, O6, O7; ruling (a′))

**Files:** Test only — `tests/etkl/test_membrane_health.py` (extend).

**Interfaces:** Consumes Tasks 2 and 3 whole. Produces nothing other tasks read.

- [ ] **Step 1: MEASURE S1 and S2 first, and write the answers into the task report.** *Does apple's
      lever actually refuse?* — M8 measured apple **lever-applicable** (10 furnished
      `dec:ExpansionRequest`s) but ran the mutation end-to-end only on `bfs` and `false_transposed_pdf`.
      apple must be compiled anyway for O2's `Weakened` leg, so one compile can serve two legs **if it
      refuses**. If it does not, use `bfs` (30.6 s, measured-positive). *Which decision is the target?*
      — read the non-superseded escalated decisions off the graph; **never hardcode a region URI from
      this plan**, and note M8's finding that a *superseded* escalation furnishes nothing and is not a
      lever.

- [ ] **Step 2: Write the failing tests.** Every vehicle below is MEASURED (M1, M4, M8). The
      `Compromised` leg is written against `bfs`, the measured-positive corpus lever — **if Step 1
      shows apple also refuses, move it onto apple and delete the `bfs` compile**, which saves 30.6 s
      and is the only substitution this task authorises.

```python
CORPUS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "corpus")


def _corpus(rel):
    """Corpus PDFs are gitignored, so an absent one SKIPS visibly rather than failing —
    the discipline tests/test_corpus.py:65-68 already uses."""
    path = os.path.join(CORPUS_ROOT, rel)
    if not os.path.exists(path):
        pytest.skip(f"corpus not populated: {rel} (scripts/fetch_corpus.py)")
    return path


def _one_more_rationale(graph):
    """The R127 lever: a SECOND dec:rationale on a NON-SUPERSEDED escalated decision.
    escalation-furnish.rq then carries it into a second dec:condition, which dec:EventShape
    caps at 1 (dec-shapes.ttl:60-63). Returns the decision it mutated.

    The target is READ OFF THE GRAPH, never hardcoded: a SUPERSEDED escalation furnishes
    nothing and is not a lever (plan M8)."""
    DEC = Namespace("https://w3id.org/iladub/dec#")
    targets = [d for d in graph.subjects(DEC.escalatedTo, None)
               if not list(graph.subjects(DEC.supersedes, d))]
    assert targets, "vehicle broken: no non-superseded escalated decision to mutate"
    d = sorted(targets)[0]
    existing = list(graph.objects(d, DEC.rationale))
    assert len(existing) == 1, existing
    graph.add((d, DEC.rationale, Literal("une seconde raison", lang="fr")))
    return d


@pytest.mark.corpus
def test_intact_and_weakened_are_reachable_on_real_input():
    """O2, legs 1 and 2 — REACHABILITY ON REAL INPUT. NOT an independence check: these
    expectations were derived with the same held-candidate pattern the query uses, so if
    that reading of "held" is wrong, query and expectation share the error (spec 3, review
    P3). O1 is what carries independence. If a value cannot be produced from real input,
    THIS TEST FAILS AND SAYS WHICH — it does not fall back to a fixture.

    graincorp-stem is NOT interchangeable with a cheaper Intact document: it is the specimen
    that carries the point that health is not the score (spec 1, review B8) — it scores
    0.9655 with 77 escalated tokens of unread ink and is correctly Intact, because nothing
    is HELD at the membrane."""
    doc = URIRef(_DOC)
    stem = compile_document(_corpus("ag-trade/graincorp-stem-2026-07-31.pdf"))
    assert list(stem.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Intact]

    apple = compile_document(_corpus("financial/apple-fy2026q3-statements.pdf"))
    assert list(apple.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Weakened]


@pytest.mark.corpus
def test_compromised_is_reachable_by_the_r127_lever_on_a_real_graph():
    """O2, leg 3 — AMENDED 2026-08-25, option (a'), and the concession is written here
    rather than engineered around.

    COMPROMISED IS NOT REACHABLE FROM ANY PUBLIC INPUT TODAY. Measured on three independent
    routes: every tab-side lever refuses at the PAGE gate (compile.py:1173) before document
    validation is reached, and no compile can mint a second dec:rationale (BandRecorder.record
    writes exactly one, and the four decision-URI namespaces are disjoint). So this leg takes
    a REAL compiled corpus graph, adds ONE triple, and re-enters the REAL seam: no
    monkeypatch of validate/_validate, no validate_shapes=False, no hand-built graph.

    THE LEVER IS R127 — dec:rationale is uncapped while dec:condition is capped at 1, and
    CLAUDE.md explicitly permits language-tagged rationale literals. It is a latent REAL
    defect this loop deliberately does not fix, because it is the only measured route to this
    value. CLOSING R127 WITHOUT RE-HOMING THIS LEG TURNS THIS TEST RED FOR AN INVISIBLE
    REASON.

    Vehicle: bfs-population-bilan-2023 — a CORPUS document, unlike the synthetic PDF the
    lever was first proven on. So all three legs stand on corpus specimens; what this leg
    does NOT share with the other two is their public-input footing, which is the whole
    subject of the paragraph above."""
    rep = compile_document(_corpus("gov-stats/bfs-population-bilan-2023.pdf"))
    g, doc = rep.graph, URIRef(_DOC)
    assert list(g.objects(doc, ETKL.membraneHealth)) == [ETKL.Intact], "control arm broken"

    _one_more_rationale(g)
    with pytest.raises(membrane.MembraneRefusal) as exc:
        _seal(g, _legs_for_document(rep.recognized, False), True)
    assert exc.value.legs == ("dec",), exc.value.legs
    assert list(exc.value.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Compromised]


def test_an_unmutated_re_entry_still_conforms(tmp_path):
    """O2's CONTROL ARM — the thing the (a') ruling explicitly left for the plan to measure.
    escalation-furnish.rq runs a second time over a graph already carrying its own output;
    that must be a no-op and the graph must still conform, or the leg above proves nothing
    about the mutation. MEASURED before this plan: 0 triples added, conforms=True.
    Structural, not incidental — ?req is bound IRI(CONCAT(STR(?d),"-expansion")), a pure
    function of ?d (escalation-furnish.rq:56-59)."""
    rep = _cheap_document(tmp_path)
    g, doc = rep.graph, URIRef(_DOC)
    before = len(g)
    _seal(g, _legs_for_document(rep.recognized, False), True)
    assert len(g) == before, "the re-entry was not a no-op"
    assert list(g.objects(doc, ETKL.membraneHealth)) == [ETKL.Intact]


def test_a_promoted_candidate_does_not_weaken_a_document(tmp_path):
    """O3 — PROMOTION IS NOT HELD, ON A REAL EXECUTION PATH. Vehicle: the caption-wrap
    fixture compiled AT DOCUMENT SCOPE with a proposer wired, at the default
    validate_shapes=True (plan M4: 2 candidates, 2 promotions, 0 held, 3.4 s). NOT a
    hand-built graph and NOT a corpus document — M1 measured promoted == 0 on all seven
    corpus documents, so no corpus specimen can exercise this clause at all.
    Falsify: delete the FILTER NOT EXISTS; held becomes 2 and this must fail."""
    p = os.path.join(str(tmp_path), "caption_wrap.pdf")
    F.caption_wrap_report_pdf(p)
    from iladub.etkl.propose import FakeRowRoleProposer, RowRoleProposal
    prop = RowRoleProposal(("furniture", "continuation"), 0.85, "date caption + wrap fragment")
    rep = compile_document(p, row_role_proposer=FakeRowRoleProposer(prop))

    promotions = list(rep.graph.subjects(RDF.type, ILADUB.PromotionDecision))
    assert promotions, "vehicle broken: no promotion, so this oracle proves nothing"
    reviewed = {c for pd in promotions for c in rep.graph.objects(pd, ILADUB.reviews)}
    candidates = set(rep.graph.subjects(RDF.type, ILADUB.CandidateConcept))
    assert candidates and candidates <= reviewed, (candidates - reviewed)
    assert list(rep.graph.objects(URIRef(_DOC), ETKL.membraneHealth)) == [ETKL.Intact]


def test_the_minted_nodes_perturb_no_verdict(tmp_path):
    """O6 — spec 2.1 held as a regression rather than a one-off measurement. Re-validating
    a graph that carries the health triple, the type triple and the validation act yields
    the same verdict as before they were added, ON BOTH LEGS. Safe because none of the five
    wired shape files names an etkl: term and etkl-holons.ttl is not in _FULL_ONT (plan M6)."""
    rep = _cheap_document(tmp_path)
    g = rep.graph
    minted = set(g.triples((None, None, ETKL.MembraneValidation))) | \
             set(g.triples((ACT, None, None))) | \
             set(g.triples((URIRef(_DOC), ETKL.membraneHealth, None))) | \
             set(g.triples((URIRef(_DOC), RDF.type, ETKL.CompiledDocumentHolon)))
    assert minted, "nothing was minted — this oracle would be vacuous"
    after = _validate(g, ("tab", "dec"))
    before_graph = Graph()
    for t in g:
        if t not in minted:
            before_graph.add(t)
    before = _validate(before_graph, ("tab", "dec"))
    assert before[0] == after[0] and before[2] == after[2], (before[0], after[0])


def test_the_refusal_carries_the_graph(tmp_path):
    """O7 — THE HIGHEST-RISK ORACLE IN THE SET. Shares its vehicle and its seam with O2's
    third leg (ruled 2026-08-25): the same real-graph-plus-one-triple mutation through the
    same _seal. A forced non-conforming document raises MembraneRefusal; the raised
    object's .graph carries <doc> etkl:membraneHealth etkl:Compromised; and
    `except AssertionError` still catches it (plan M2: all 17 interceptors in the repo are
    isinstance-based, none depends on the exact class).
    Falsify: revert to a bare AssertionError; this must fail."""
    rep = _cheap_document(tmp_path)
    g, doc = rep.graph, URIRef(_DOC)
    _one_more_rationale(g)
    with pytest.raises(AssertionError) as exc:          # deliberately the BASE class
        _seal(g, _legs_for_document(rep.recognized, False), True)
    assert isinstance(exc.value, membrane.MembraneRefusal)
    assert exc.value.graph is g
    assert list(exc.value.graph.objects(doc, ETKL.membraneHealth)) == [ETKL.Compromised]
    assert str(exc.value).startswith("document-level facts failed dec: SHACL:")
```

- [ ] **Step 3: Run to verify they fail**, then implement nothing — **these oracles assert
      against Tasks 2 and 3 exactly as shipped.** If one fails, the defect is in Task 2 or Task 3,
      not here; fix it there. The only edit this task authorises to the tests above is Step 2's
      named `bfs` → `apple` substitution, and only if Step 1 measured it.

Run: `./.venv/bin/python -m pytest -q tests/etkl/test_membrane_health.py`
Expected: FAIL on the four new names.

- [ ] **Step 4: Run the fast legs, then the corpus legs.**

Run: `./.venv/bin/python -m pytest -q tests/etkl/test_membrane_health.py`
then: `./.venv/bin/python -m pytest -q -m corpus tests/etkl/test_membrane_health.py`
Expected: PASS. **Budget, measured (M1):** `graincorp-stem` 190.1 s + `apple` 36.8 s + `bfs` 30.6 s
≈ **258 s added** to a 2386.82 s baseline — **227 s if Step 1 lets the `Compromised` leg ride apple's
compile.** Corpus PDFs are gitignored, so an unpopulated `corpus/` **skips these two visibly**; a skip
is not a pass, and Task 7's definition of done is not met until they have actually run.

- [ ] **Step 5: FALSIFICATION.** (a) delete the `FILTER NOT EXISTS` → O3 fails; (b) revert
      `MembraneRefusal` to a bare `AssertionError` → O7 fails; (c) collapse the `IF` → O2 fails on at
      least two legs; (d) skip the query on the raising path in `_seal` → O7 fails on `.graph`.
      **And one more, because it is the residue this loop ships on purpose:** state in the report that
      capping `dec:rationale` would turn O2's third leg and O7 red — that is `R127`'s coupling, and
      Task 7 records it.

- [ ] **Step 6: Commit.**

```bash
git add tests/etkl/test_membrane_health.py
git commit -m "test(etkl): reachability, promotion, perturbation and refusal oracles on real input"
```

---

## Task 5: The health signal's own shape, hand-wired (spec §4.8)

**Files:**
- Modify: `vocab/shapes/etkl-shapes.ttl`, `tests/test_vocab_shapes.py`
- Create: `examples/membrane-health-conformant.ttl`, `tests/membrane-health-bad-two-values.ttl`,
  `tests/membrane-health-bad-outside-enum.ttl`

**Interfaces:** Consumes Task 1's `etkl:CompiledDocumentHolon`. Produces `etkl:MembraneHealthShape`.

- [ ] **Step 1: Ship the shape.** Spec §4.8 gives it: `sh:targetClass etkl:CompiledDocumentHolon`,
      one `sh:property` on `etkl:membraneHealth` with `sh:maxCount 1` and
      `sh:in ( etkl:Intact etkl:Weakened etkl:Compromised )`. **In `vocab/shapes/etkl-shapes.ttl`,
      deliberately** — it is the one shape file the compile membrane does not load (M6), so the shape
      inherits that non-loading and spec §2.1's safety argument is untouched. No prefix edit is needed
      (M6). **It is validated in the test, NOT wired into the membrane**: wiring it would re-open §2.1
      *and* be vacuous, since health does not exist when validation runs. `owl:FunctionalProperty` is
      **rejected**, not merely unused — inference is off (`membrane.py:124-125`) so it would do
      nothing, and under a reasoner it would *entail `owl:sameAs`* between two health values rather
      than refuse them (spec §4.8).

- [ ] **Step 2: Write the three fixtures and the two test functions.** **Nothing discovers them
      (M7):** `tests/test_vocab_shapes.py` is 66 lines of four hard-coded pairs, no glob, no
      `parametrize`. **And the ontology graph must be `etkl-holons.ttl`, not `etkl.ttl`** — the four
      existing pairs pass `etkl.ttl` (`:35`, `:44`), which does not declare
      `etkl:CompiledDocumentHolon`; pass the wrong one and `sh:targetClass` finds no focus node and the
      negatives pass vacuously. The positive goes in `examples/`, the negatives in `tests/`, following
      the file's own convention (`examples/etkl-conformant.ttl` / `tests/etkl-bad.ttl`).

```python
# --- membrane health: the signal minted after validation is governed by SHACL ---

def test_membrane_health_conformant():
    c, t = _validate(
        [os.path.join(EX, "membrane-health-conformant.ttl")],
        os.path.join(SH, "etkl-shapes.ttl"),
        [os.path.join(ONT, "etkl-holons.ttl")],
    )
    assert c, t


@pytest.mark.parametrize("bad", ["membrane-health-bad-two-values.ttl",
                                 "membrane-health-bad-outside-enum.ttl"])
def test_membrane_health_malformed_rejected(bad):
    c, _ = _validate(
        [os.path.join(TST, bad)],
        os.path.join(SH, "etkl-shapes.ttl"),
        [os.path.join(ONT, "etkl-holons.ttl")],
    )
    assert not c
```

**Note:** `tests/test_vocab_shapes.py` does not currently import `pytest` (M7 — it has no
`parametrize`). Add the import, or write the two negatives as two functions; either satisfies the
CLAUDE.md pair rule.

- [ ] **Step 3: Run.**

Run: `./.venv/bin/python -m pytest -q tests/test_vocab_shapes.py`
Expected: PASS, 4 existing + the new ones.

- [ ] **Step 4: FALSIFICATION.** Delete `sh:maxCount 1` → the two-values negative passes and its test
      **must fail**; restore. Delete `sh:in` → the outside-enum negative passes and its test **must
      fail**; restore. Show both. **A negative fixture that still conforms after you delete the
      constraint it targets is pinning nothing** — that is defect 5's shape.

- [ ] **Step 5: Commit.**

```bash
git add vocab/shapes/etkl-shapes.ttl tests/test_vocab_shapes.py examples/membrane-health-conformant.ttl tests/membrane-health-bad-*.ttl
git commit -m "feat(etkl): MembraneHealthShape governs the signal minted after validation"
```

---

## Task 6: The promotion clause's vacuity tripwire (spec §4.9 — P1 ruled IN)

**Files:** Modify `tests/etkl/test_vacuity_registry.py` **only** — the new arm must live in that file
or it re-instantiates the module-scoped `corpus_graphs` fixture and pays another **~357 s**
(MEASURED: `4 passed, 4 deselected in 360.07s`, of which **356.88 s is fixture setup and 3.01 s is all
four test calls**; there is no `conftest.py` in this repo to share it through).

**Interfaces:** Consumes Task 3's `membrane-health.rq`. Produces nothing other tasks read.

**Seam 7 is CLOSED: the answer is YES.** Measured — the extension needs **none** of the four
SHACL-shaped functions (`shapes_graph:143`, `node_shapes:150`, `focus_nodes:154`, `body_terms:166`),
nor `unreachable_terms:184` or `idle_shapes:190`. Reusable **unchanged**: `vocabulary_of` (`:178`),
`_TERM` (`:63`), **`_PREFIX_NS` (`:58-62`)**, `CORPUS` (`:65-73`), `corpus_graphs` (`:297-318`,
returning `dict[str, Graph]` of subclass-closed compile graphs).

**The crux the brief flagged does not exist.** Both sides already yield full-IRI `URIRef`s:
`_TERM.findall` returns `(prefix, local)` tuples and the two-line expansion idiom is already inline at
`body_terms:173-174`; `vocabulary_of` returns `URIRef`s. Demonstrated:

```
terms from .rq text via _TERM + _PREFIX_NS: ['https://w3id.org/iladub#PromotionDecision',
                                             'https://w3id.org/iladub#reviews']
vocabulary_of() element type: {'URIRef'}
SET DIFFERENCE (unreachable):               ['https://w3id.org/iladub#PromotionDecision',
                                             'https://w3id.org/iladub#reviews']
```

**And the premise re-measured at `18226e7`, all seven documents:** `iladub:PromotionDecision` and
`iladub:reviews` are **absent from the union of all seven** compile graphs — worth measuring because
reading the code suggests the opposite (five sites write both terms, and `promote.py` **is** reachable
from the compile path via `rowrole.py:230`, `reshape.py:221`, `span.py:79`).

**Genuinely new machinery, all small:** an enumerator over `.rq` files (none exists — every call site
names one file); **comment stripping, which is MANDATORY** (measured: **10 of 45** files' prose headers
name terms their query bodies do not — e.g. `escalation-furnish.rq` adds `dec:EscalationShape` and
`risk:Severity`); a second dict keyed **(query file, term)**; and its two arms mirroring
`test_every_idle_shape_is_registered` (`:325`) and `test_no_registered_shape_has_gone_live` (`:337`).

- [ ] **Step 1: MEASURE S4 — the population, and how many rows it yields — BEFORE writing the dict.**
      The SHACL arm's population is **not a glob**: `wired_shape_files` (`:133-140`) reads it *from the
      compile membrane*. The query analogue must be scoped the same way, and the reason is a category
      error the spec's §2.8 already warns about: `corpus_graphs` holds **compile** graphs, so a query
      that runs over a *different* graph is not idle merely because its terms are absent there.
      **Measured, for the plan:** 30 `.rq` files are named from `src/`, of 45 in the directory; exactly
      **3 belong to `federate.py`** (`federate-projection.rq`, `federate-projection-governed.rq`,
      `compile-f-grants.rq`), which runs over the grounded interior ∪ terms, **not** the compile graph.
      That leaves **27 compile-path queries, plus `membrane-health.rq` = 28**.
      **This matters concretely:** `federate-projection.rq:18` and `federate-projection-governed.rq:25`
      each name `iladub:PromotionDecision` in their bodies, so a naive directory sweep registers
      **three** files where the loop intends one — and the new arm's first run fails with two
      unregistered rows.
      **Now measure the thing this plan cannot:** over the 28-query population, how many (query, term)
      pairs come back unreachable? **Each row needs a MEASURED prose reason, as all nine SHACL rows
      have.**

- [ ] **Step 2: Branch on Step 1's number, and record which branch you took.**
      **If every row can be given a measured reason within this task** — ship the tripwire: the
      enumerator, the comment stripper, the `(query, term)` dict with the `membrane-health.rq` row, and
      the two arms.
      **If it cannot** — **take spec §4.9's named fallback**: register a residue row instead, and
      **record the count you measured as the reason**. The fallback exists because rewriting the
      registry's machinery is out of scope for a loop already minting three terms and a shape.
      **Do not silently drop it** (spec §8 item 8), and do not invent a threshold — the criterion is
      whether each row can carry a measured reason, not a number.

- [ ] **Step 3: If the tripwire ships, its bidirectional arm is the point.** The forward arm registers
      today's residual; **the reverse arm fails the suite the day a proposer is wired into the corpus
      sweep and those terms go live**, forcing de-registration rather than leaving the residue to a
      human's memory. R106's row says *"the rule that catches it is prose"*; this is the instrument
      that stops it being the second instance.

- [ ] **Step 4: Run.**

Run: `./.venv/bin/python -m pytest -q -m corpus tests/etkl/test_vacuity_registry.py`
Expected: PASS in ~6 min, **unchanged from the 360.07 s baseline** — the new arms ride the existing
fixture and all four current test *calls* together cost 3.01 s.

- [ ] **Step 5: FALSIFICATION.** If the tripwire shipped: delete the `membrane-health.rq` row from the
      new dict → the forward arm must fail naming that row; restore. Then add a **bogus** row for a
      term that *is* reachable → the reverse arm must fail; remove. If the fallback was taken, the
      falsification is the register row's own evidence — paste the measured count.

- [ ] **Step 6: Commit.**

```bash
git add tests/etkl/test_vacuity_registry.py
git commit -m "test(etkl): a machine tripwire for membrane-health.rq's unexercised promotion clause"
```

---

## Task 7: The record this loop owes (spec §4.6, §4.10, §8, §11)

**Files:** `tests/arc-manifest.ttl`, `docs/holonic-interaction.md`, `docs/superpowers/residues.md`,
`residues-open.md`, `residues-closed.md`.

**Interfaces:** Consumes Tasks 1–6's shipped artifacts and their evidence. Produces nothing code reads.

- [ ] **Step 1: Flip the criterion** (`tests/arc-manifest.ttl:352-359`). `prog:met false` → `true`,
      with a **MEASURED comment block in the `dec:16` form** (`:838-856` is the exemplar — it shows the
      register: the commands, their output, and the `metOn`/`declaredOn` arithmetic spelled out). Add
      `prog:metOn`, derive `prog:retrospective` from `declaredOn "2026-06-23"` vs `metOn` (later ⇒
      **false**), and add `prog:oracleArtifact "vocab/queries/membrane-health.rq"`, which this criterion
      has never had. **Keep `prog:oracleTest` byte-for-byte as `:359` already writes it** — Task 3 made
      that exact name exist.

- [ ] **Step 2: Amend `prog:statement` (`:354`), in the same act, with its own comment saying so.**
      *"…from validation results"* excludes held candidates, which is now half the design (spec §4.6
      row 4). **Amending a criterion's statement in the very loop that flips it to `met true` is
      indistinguishable from moving the goalposts unless the manifest says why** — so say why, in the
      MEASURED form the file already uses.

- [ ] **Step 3: Move and reword `docs/holonic-interaction.md:160-161`.** Out of *"Planned work (not
      done yet)"* (heading `:158`) into *"What is built"* (`:145`) — **and reword it in the same act**
      (spec §4.6 row 3), consistently with Task 1 Step 2's wording. **This is the sentence the loop
      makes true**, and it is the criterion's own `prog:source`. *(The spec's first version cited
      `:154-155` for this bullet; that is the done-list above it. `:160-161` is correct — re-verified
      here.)*

- [ ] **Step 4: Close `R126`.** Index row in `docs/superpowers/residues.md:235` → status `closed` with
      the evidence pointer; **move the full row from `residues-open.md:100` to `residues-closed.md`**
      — **do not delete it** (CLAUDE.md § Deferred residues: a deleted row erases the proof of repair
      and silently shrinks the denominator). The closing evidence is Task 1 + Task 3: the `etkl` fabric
      now has instance data, and `etkl:membraneHealth`'s `rdfs:domain` is instantiated.
      **Correct its two mis-cited ranges in the same act:** the row's `etkl-holons.ttl:74-88` and
      `tests/arc-manifest.ttl:1337`'s `75-86` both become **`75-89`** (verified: `:75` is
      `etkl:MembraneHealth a owl:Class`, `:89` is `etkl:membraneHealth`'s closing `rdfs:comment`).

- [ ] **Step 5: Raise R127, R128, R129** (spec §11 gives all three verbatim, with their closing
      conditions — **cite, do not re-derive**). Tally snapshot `(24/116 closed)` on each new row per
      the register's convention; **the next number after this loop is `R130`.**
      **`R127` must carry its O2 coupling explicitly in the row text** — *closing this requires
      re-homing O2's `Compromised` leg first* — because a shipped oracle depends on it staying open and
      a row a test depends on cannot sit unranked among 116 others (ruling 2).
      Add residues 1–4 of spec §11 (page-scope preemption, the shared `_DOC` IRI, `_validate`'s
      `IndexError` on `legs=()`, the grounding portal's missing health). **Residue 5 is raised ONLY if
      Task 6 took the fallback** — if the tripwire shipped it is a machine guard, not a residue.

- [ ] **Step 6: Run the governance lint (S5) and then the full suite.**

Run: `./.venv/bin/python -m pytest -q tests/test_doc_governance.py`
Expected: PASS (`4 passed` on the parent branch). It checks nav integrity and **doc-impact
registration** — this plan's own `Doc impact: increment` header is what registers it.

Run: `./.venv/bin/python -m pytest -q`
Expected: **at least `1312 passed, 7 skipped, 1 xfailed`** — the baseline measured 2026-08-25 before
any implementation, in **2386.82 s** (~40 min). The loop's own run must **match or exceed the passed
count**. `pytest-timeout` is not installed and `timeout` is not on PATH (Global Constraint 1), so let
it run.

- [ ] **Step 7: Commit.**

```bash
git add tests/arc-manifest.ttl docs/holonic-interaction.md docs/superpowers/residues*.md
git commit -m "record(holon:05): criterion met, R126 closed, R127-R129 raised"
```

---

## Definition of done (spec §8, mapped to tasks)

| spec §8 | task |
|---|---|
| 1. All nine oracles green, each with falsification evidence | Tasks 2–5 (**and O10, O11 — this plan adds two: M9's re-entry hazard and the subclass check**) |
| 2. `membrane-health.rq` with its GATE header, negation justification, site constraint + collision reason, and the pinning tests | Task 3 Step 3 |
| 3. `test_compiled_document_reports_membrane_health` exists under **exactly** the pre-declared name | Task 3 Step 1 |
| 4. `holon:05` flipped with MEASURED comment, `metOn`, derived `retrospective`, `oracleArtifact`, amended `statement` + its comment | Task 7 Steps 1–2 |
| 5. Three terms declared, two comments amended, `versionInfo` → `0.2.0` | Task 1 |
| 6. `MembraneHealthShape` **with its conformance pair hand-wired** | Task 5 |
| 7. `holonic-interaction.md:160-161` out of *Planned work* **and reworded in the same act** | Task 7 Step 3 |
| 8. Tripwire shipped **or** its named fallback taken and recorded | Task 6 Step 2 |
| 9. Full suite green in the repo venv, ≥ `1312 passed` | Task 7 Step 6 |
| 10. Residues appended, `R126` **struck and moved**, not deleted | Task 7 Steps 4–5 |

## Unverified at plan time — read this before Task 1

- **S1–S6 are open by design** (§ Named seams and the Step-1 of Tasks 2, 4, 6). Each names a fact to
  measure, not an answer to transcribe.
- **The suite baseline `1312 passed, 7 skipped, 1 xfailed` in 2386.82 s is the spec's**, measured
  2026-08-25 before any implementation. **It was not re-run in this session.** Task 7 Step 6 is where
  it gets tested, and a lower passed-count is a finding, not a rounding error.
- **`graincorp-stem` and `cbh-stem` were not compiled for the escalation census** (M8). Their lever
  status is unknown; three of the five documents that *were* measured carry it, which is enough for
  Task 4, and cbh is suspected negative (its four escalated decisions are recorded as superseded in an
  earlier register note) — **suspected, not measured.**
- **apple's lever is applicable but its refusal is unmeasured** — S1. `bfs` (30.6 s) and
  `false_transposed_pdf` (1.12 s) are the measured-positive fallbacks.
- **M8's re-entry was driven by calling the four steps in order on a copied graph, not through
  `_seal`**, because `_seal` does not exist yet. Task 2 Step 6 is where that becomes real, and Task 4
  is where it is asserted.
- **The wall-clock figures throughout are single runs on one machine under concurrent load** (three
  measurement agents ran in parallel). Treat them as order-of-magnitude cost, not benchmarks — M8's
  corpus numbers in particular ran high against M1's for exactly that reason.
- **`R127`'s coupling to O2 is asserted from the seam-6 measurement**, dated 2026-08-25, not re-run
  here. Its census (`{1: 17}`, `{1: 18}`) was however **corroborated on three further documents** by
  M8's histograms (`{1: 232}`, `{1: 81}`, `{1: 119}`, and ons's `{1: 216, 0: 2}`).
