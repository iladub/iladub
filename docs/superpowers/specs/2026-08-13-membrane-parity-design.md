# Membrane parity and the engine unpin — design spec

**Date:** 2026-08-13
**Closes:** R94 (the two membrane legs are fed different artifacts), R88 (the pySHACL capability pin)
**Branch base:** `fix/r92-decimal-typing` (PR #103, green and mergeable) — this loop depends on
R92's emitter conversion being in the tree.
**Doc impact:** increment

---

## 1. What is wrong today

`membrane.validate`'s docstring (`membrane.py:48-53`) claims *"the engine is the only variable."*
It is false, and it is not repairable as written.

- `_validate_pyshacl` hands pySHACL the **live rdflib graph** (`membrane.py:96-97`).
- `_validate_rudof` hands rudof **`expanded.serialize(format="nt")`** (`membrane.py:155-158`).

An N-Triples round trip re-parses a float-valued `xsd:decimal` into a real `Decimal`, so the
serialization boundary silently *repairs* defects before rudof sees them. Consequence:
`tests/etkl/test_membrane_equiv.py` cannot detect any divergence that depends on a literal's
in-memory value **by construction** — whatever it builds, only pySHACL ever sees the in-memory form.

Separately, `compile._DEC_ENGINE = "pyshacl"` (`compile.py:396`) pins the decision shapes to
pySHACL because rudof raises on an `sh:sparql` constraint with a blank-node focus node. The pin
splits the membrane's one-engine story: today `ILADUB_MEMBRANE=rudof` **raises** at the pinned call.

Both are one loop because both change what `subclass_closure` hands the engines. Doing them apart
means measuring the same seam twice, with the second engine-behaviour change landing on an
unverified first one.

---

## 2. Measured premises

Every premise below carries its type, per the spec-writing discipline:
`measured-on-evidence` (a real document / a third-party implementation),
`measured-on-fixture` (our own constructed graph), `read-not-run`, `not-measured`.

Probes ran 2026-08-13 on `fix/r92-decimal-typing` at `bf2868f`, from a session scratchpad that is
**not durable** — the outputs are therefore reproduced inline below rather than cited by path. Each
probe is a few lines against `membrane.subclass_closure` and is cheap to rebuild; treat the tables,
not the scripts, as the evidence.

### P1 — R94 reproduces on HEAD — *measured-on-fixture*

```
built Literal(round(x,2), XSD.decimal) -> .value type = float, lexical = '307.47'
pySHACL on the LIVE graph         : conforms = False
rudof   on the SERIALIZED graph   : conforms = True
pySHACL on the ROUND-TRIPPED graph: conforms = True
```

### P2 — byte-parity does NOT produce agreement — *measured-on-fixture*

This **refutes the remedy R94's own row prescribes** ("feed both legs the same artifact, then
confirm every leg still agrees"). It will not agree.

```
Literal(float(5e-05), XSD.decimal): lexical='5e-05'   value=5e-05
serialize('nt') emits              : "5e-05"^^xsd:decimal
after nt round trip                : lexical='0.00005' value=Decimal('0.00005')
pySHACL live=False   rudof=False   pySHACL-roundtripped=True
```

rdflib's N-Triples **parser** silently rewrites the lexical form. So given byte-identical input,
pySHACL judges a repaired value and rudof judges the bytes as written. **rudof is spec-correct** —
exponential notation is outside `xsd:decimal`'s lexical space.

**The parser is inside the engine boundary.** "The engine is the only variable" is not merely false
today; it is unachievable, and a spec promising it would promise what the code cannot deliver.

### P3 — skolemize is verdict-neutral for pySHACL and unblocks rudof — *measured-on-fixture*

Fourth independent confirmation (three prior, recorded in R88's row).

| graph | pySHACL plain | pySHACL skolemized | rudof plain | rudof skolemized |
| --- | --- | --- | --- | --- |
| conformant blank-node promotion | `True` | `True` | RAISES `ValueError` | `True` |
| `dec:optionSpace` stripped | `False` | `False` | RAISES `ValueError` | `False` |

Skolem IRIs **do** reach the human-read report:
`Focus Node: <https://rdflib.github.io/.well-known/genid/rdflib/Nbb35…>`.

### P4 — no shape is blank-node sensitive — *measured-on-evidence (our shape files)*

`grep -n "nodeKind" vocab/shapes/*.ttl` → **no matches**. `grep` for `isBlank|isIRI|isURI|BNODE`
across every `sh:sparql` body → **no matches**. So skolemization cannot flip a constraint by
turning a blank node into an IRI.

### P5 — the literal-hygiene guard on today's code — *measured-on-fixture AND measured-on-evidence*

The guard (§4) was installed over `membrane.subclass_closure` and the suites run.

| run | result | guard |
| --- | --- | --- |
| fast suite (`-m "not corpus"`) | 1141 passed, 7 skipped, 1 xfailed, exit 0, 17:00 | **17 TYPE, 0 LEXICAL** |
| corpus battery (`tests/test_corpus.py -m corpus`) | 10 passed, 0 skipped, 5:42 | **0 violations** |
| **every** corpus-marked test (`tests/ -m corpus`) | 36 passed, 1149 deselected, 10:30 | **0 violations** |

All 17 fast-suite hits are **test fixtures**, attributed by `PYTEST_CURRENT_TEST`:

- `y0 ×15` → `tests/etkl/test_row_groups.py::test_partial_derived_coverage_passes_the_row_tiling_shapes`
  and `::test_two_confirmed_groups_over_the_same_member_rows_still_tile`
- `x0 ×2` → `tests/etkl/test_decimal_typing.py::test_the_differential_is_not_vacuous` — the R92
  tripwire's **deliberately** forbidden form

**Zero come from `src/` emitters.** An earlier grep-based attribution guessed the wrong files and
was refuted by re-running them; the table above is the measured one.

### P6 — the extra parse is cheap — *measured-on-fixture, and NOT sufficient*

`closure+serialize = 5.7 ms, extra parse = 0.2 ms` on a small decision graph. **This does not
license a claim about the 8.6k-triple stem page.** The plan MUST re-measure on a real corpus page.

### P7 — the pin's cost — *measured-on-evidence, inherited from R88's row, NOT re-derived here*

Grounded stem p0: pySHACL **1.70 s** vs skolemize (**0.10 s**) + rudof **0.59 s** ≈ **2.5×**, same
verdict. On compile-only pages the pin is currently *cheaper* (pySHACL 0.15-0.17 s vs rudof
0.45-0.55 s; rudof has a ~0.45 s fixed floor). **The argument for unpinning is the one-engine
story, not performance**, and the spec makes no performance claim.

### Premises deliberately NOT measured here

- The IRI shape `Graph.skolemize(authority=…)` produces. *read-not-run.* Named as a seam in §6.
- The extra parse's cost on a real 8.6k-triple page (P6). *not-measured.* Named as a seam in §7.

---

## 3. The parity contract

Parity has exactly one available shape. `pyrudof.read_data` takes a **string**; rudof can never be
handed a live rdflib graph. So "hand rudof a live-equivalent graph" — one of the two directions the
scoping memo offered — does not exist. The contract is therefore:

> **Both engines receive the same N-Triples document. Each parses it with its own parser.
> Parser differences are engine differences.**

This is true, it is the production reality, and it replaces the false claim at `membrane.py:48-53`.

**What this contract does and does not buy.** It dissolves R94's class entirely: today's
`False`/`True` split is not an engine disagreement at all but two engines fed two different inputs.
It does **not** dissolve P2's class, and it must not — there, rudof is right and pySHACL is being
handed repaired data by its own parser. Two independent SHACL implementations are not bit-identical
on ill-typed input, and no design should pretend otherwise. §4 makes that input unreachable instead.

---

## 4. The design

### 4.1 The payload builder

One builder produces the contract artifact; both legs consume it.

```
_payload(data_graph, ont_graph) -> (Graph, str)
```

Ordered obligations, each of which the implementer writes:

1. expand via `subclass_closure` — **unchanged and still public** (`test_closure_equiv.py` depends
   on it);
2. run `audit_literals` (§4.2) over the expansion;
3. skolemize;
4. serialize to N-Triples **once**;
5. return the re-parsed `Graph` and the same `str`.

`_validate_pyshacl` takes the `Graph`; `_validate_rudof` takes the `str`.

**Invariant: rudof's input is bit-identical to today.** Only pySHACL's input changes. An
implementer who cannot demonstrate this has changed the wrong thing.

**Placement is load-bearing, not stylistic.** `test_membrane_equiv.py:35-40` calls the two leg
functions **directly**, bypassing `validate()`. A builder living in `validate()` would leave the
battery exactly as blind as it is now. It must sit below the legs.

Gate classification (CLAUDE.md §8): **PROCEDURAL**, engine glue. Irreducible: a validator must be
handed bytes from somewhere, and the handing carries no domain decision. No tuned constant appears.

### 4.2 `audit_literals` — the guard

Two invariants, in the same place and idiom as `subclass_closure`'s existing literal-subject
*"INVARIANT GUARD here, not a repair"*:

- **TYPE** — a literal's `.value` Python type matches its datatype's mapping. Catches R92's class:
  `Literal(round(x,2), XSD.decimal)` holds a `float`.
- **LEXICAL** — a literal's lexical form equals what rdflib's parser would produce for it. Catches
  P2's class: `5e-05` ≠ `0.00005`.

**Failure mode: raise.** Licensed by P5 — zero `src/` emitters violate, on the corpus battery and
the fast suite alike. It is a guard, never a repair: it must not rewrite a literal.

The licence is complete: **every** corpus-marked test in the repo (36, on real documents through
the public `compile_document` API) ran with the guard installed and produced **zero** violations,
alongside the 1141-test fast suite. The only hits anywhere are the two fixture files named above.

Two fixture files need conversion, and they are not the same case:

- `tests/etkl/test_row_groups.py` (2 tests) — mechanical conversion to `Decimal(str(...))`. Nothing
  about these tests is about literal typing.
- `tests/etkl/test_decimal_typing.py::test_the_differential_is_not_vacuous` — **must keep building
  the forbidden form**, because that form is the guard's own falsification. It gets an explicit
  documented bypass of `_payload`, not a conversion.

### 4.3 The unpin

- delete `compile._DEC_ENGINE` (`compile.py:396`);
- drop `engine=` at `compile.py:440` and `feed.py:615`;
- **keep** `validate()`'s `engine=` parameter and **keep** its raise on an `ILADUB_MEMBRANE`
  conflict — the behaviour is still right, but its stated *reason* changes from "a capability rudof
  lacks" to "an operator must never be handed the other engine's verdict unannounced." There is no
  longer a capability to protect (P3).

---

## 5. The falsifying oracle

*What fails if the two legs agree for the wrong reason?* Parity bought by making both legs equally
blind is worse than the present asymmetry, and the equivalence battery cannot tell the difference —
it is the thing under repair. So the disposal comes from outside it.

**Oracle 1 — a divergence fixture that fails on AGREEMENT.** Given byte-identical input
`Literal(float(5e-05), XSD.decimal)`, pySHACL must return `True` and rudof `False`. If a future
change makes them agree, someone canonicalized the payload — value-parity, agreement bought by
blinding. This test is the inverse of a normal test and is the detector the loop exists to install.
It calls the legs directly, below the guard.

**Oracle 2 — guard falsification** (CLAUDE.md plan rule 4, mandatory per task). Delete
`audit_literals`: the forbidden form passes the membrane silently. Restore: it raises.

**What proposes, what disposes, and are they independent?** The payload builder proposes the
artifact. The disposers are (a) rdflib's parser behaviour, measured at P2 independently of the
builder, and (b) rudof, a separate implementation by a third party. Neither derives from the
proposer, so disposal is real.

---

## 6. Test rewrites — and the trap

Leg 5's comment (`test_membrane_equiv.py:300-301`) reads: *"THIS TEST FAILING IS GOOD NEWS. It means
rudof learned to evaluate `sh:sparql` on blank-node focus nodes."*

**Once skolemize is in the builder, `test_rudof_still_cannot_evaluate_sparql_constraints_on_a_blank_node_focus`
stops raising — and that reading is FALSE.** It stopped because we routed around the incapacity, not
because rudof gained it. An implementer who deletes the test on the strength of its own comment has
destroyed the standing justification for skolemizing at all.

Required:

1. Rewrite it to hit rudof on a **raw, un-skolemized** serialization, bypassing `_payload`, so it
   keeps pinning the upstream defect.
2. Add a structural test: `_payload`'s output contains **zero** `BNode` terms. This is the one-line
   invariant that makes the unpin safe.
3. Add the one-engine test: a blank-node promotion validates identically through
   `membrane.validate` under both engines.
4. `test_the_capability_pin_refuses_a_conflicting_forced_engine` (`:351`) and
   `tests/etkl/test_compile_membrane_shapes.py:59` (`_DEC_ENGINE == "pyshacl"`) go with the constant.

**Seam the plan must MEASURE, not assume:** what IRI shape `Graph.skolemize(authority=…)` actually
produces, *before* writing the report de-skolemization. P3 shows skolem IRIs reaching the report a
human reads.

---

## 7. Ordering, and what this loop deliberately does NOT do

**Ordering.** Two sequential tasks on one branch. Task 1: parity + guard, battery re-run, any
verdict change recorded. Task 2: skolemize + unpin, measured *after* Task 1 — otherwise the cost is
taken against a moving target.

**Not done here** — stated so a plan-supplied test can be reconciled against it (CLAUDE.md plan
rule 5):

- **No SHACL shape changes.** `vocab/shapes/` is untouched.
- **No production-emitter fixes.** P5 measured them clean across the fast suite and every
  corpus-marked test. Only two fixture files change (§4.2), and neither is an emitter.
- **No attempt to make the engines agree on P2's lexical-form class.** The disagreement is preserved
  deliberately. A test asserting the two engines agree on an ill-typed lexical form contradicts this
  section and must not be written.
- **Nothing on R89** (producer-side guard policy — a project decision awaiting François) **or R61**
  (emitter typing — the `datagrid.py:635-636` modelling decision).
- **No de-skolemization outside report text.** Skolem IRIs never escape into data; the closure is
  already a copy.

---

## 8. Doc impact: `increment`

- `docs/wiki/concepts/grounding-membrane.md` gains the one-engine membrane note. Measured: that page
  currently mentions neither engine nor the pin (`grep -n "rudof\|pySHACL\|pin\|engine"` → no
  matches), so this is an addition, not a contradiction.
- No `mkdocs.yml` nav page describes membrane engines (`grep -n "rudof\|membrane" mkdocs.yml` → no
  matches), so nothing blocks a release tag.
- `docs/superpowers/residues-open.md`: strike **R88** and **R94**, closure evidence recorded in
  place, rows retained. Register goes **15/84 → 17/84**.
- `docs/loops/2026-08-11-decision-membrane-close.md` mentions the pin but is **Evidence** — immutable
  after loop close, and not edited.

---

## 9. Pre-review self-attack

**The rival this design must exclude.** *"Round-trip the graph once inside `subclass_closure` and
both legs agree."* Excluded by P2, measured: they do not agree, and the residual disagreement is one
where rudof is right. Any design premised on post-parity agreement is refuted before it is written.

**The premise most likely to be wrong.** P6. The extra parse was measured on a tiny decision graph
and says nothing about an 8.6k-triple page. It is flagged as insufficient in place rather than
carried as fact.

**The claim I could not measure.** The extra parse's cost on a real page, and the IRI shape
`Graph.skolemize(authority=…)` produces. Both are declared assumptions with named blast radii
(§2, §6, §7), never stated as fact. Everything else in §2 was run.

**Where an implementer is most likely to go wrong.** Deleting leg 5's tripwire because its own
comment says failing is good news (§6). The comment was true when written and is false after Task 2.

**Quotes verified in place.** `membrane.py:48-53`, `:96-97`, `:155-158`, `compile.py:396`, `:440`,
`feed.py:615`, `test_membrane_equiv.py:35-40`, `:300-301`, `:351`,
`test_compile_membrane_shapes.py:59` — each read at `bf2868f`, not recalled.
