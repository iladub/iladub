# Membrane parity and the engine unpin — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make both membrane legs consume one N-Triples artifact, guard the two literal-defect
classes that artifact hides, and remove the pySHACL capability pin.

**Architecture:** A single `_payload` builder below the two leg functions produces the contract
artifact once — expand, audit, skolemize, serialize — and returns `(Graph, str)`. `_validate_pyshacl`
takes the graph, `_validate_rudof` takes the string, and rudof's input stays bit-identical to today.
Skolemizing removes the blank-node focus nodes rudof cannot evaluate, which retires `_DEC_ENGINE`.

**Tech Stack:** Python 3.12, rdflib, pySHACL, pyrudof, pytest.

**Spec:** `docs/superpowers/specs/2026-08-13-membrane-parity-design.md` — read §2 (measured premises)
and §7 (what this loop deliberately does NOT do) before starting any task.

**Branch:** `loop-membrane-parity`, off `main` at `e84aa81` (PR #103 merged).

**Doc impact:** increment — carried from the spec §8; realised in Task 4.

## Global Constraints

- **CLAUDE.md §8 gate.** Every change here is **PROCEDURAL** engine glue and must say so in the code:
  a validator must be handed bytes from somewhere, and the handing carries no domain decision.
  **No tuned constant or tolerance may appear.** A geometric constant or a heuristic answering a
  span/read/group/role question is a review failure.
- **Source ownership.** `vocab/` is untouched by this plan. No shape file is edited (spec §7).
- **The guard is a guard, never a repair.** `audit_literals` must not rewrite a literal.
- **Never weaken a plan-supplied assertion to make it go green.** If a supplied test cannot pass,
  you have found a plan defect — say so in the task report and substitute the satisfiable form
  carrying the same force (CLAUDE.md, plan rule 5).
- **Falsification is mandatory per task.** No `## FALSIFICATION` block ⇒ the task review fails.
- Full suite command: `python -m pytest tests/ -q -m "not corpus"`.
  Corpus battery: `python -m pytest tests/ -q -m corpus`.

---

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `src/iladub/etkl/membrane.py` | `_payload` builder, `audit_literals`, both legs, docstring | 1, 2, 3, 4 |
| `tests/etkl/test_membrane_equiv.py` | the engine differential + the divergence oracle + leg 5 | 1, 2, 3 |
| `tests/etkl/test_decimal_typing.py` | R92's tripwire — `:99` is superseded by parity; gains the guard's falsification | 1, 2 |
| `tests/etkl/test_row_groups.py` | two fixtures build float-valued decimals; convert | 2 |
| `src/iladub/etkl/compile.py` | `_DEC_ENGINE` constant + its call site | 3 |
| `src/iladub/feed.py` | the grounding membrane's call site | 3 |
| `tests/etkl/test_compile_membrane_shapes.py` | asserts the pin; goes with it | 3 |
| `docs/wiki/concepts/grounding-membrane.md` | the one-engine note | 4 |
| `docs/superpowers/residues-open.md`, `residues.md` | strike R88, R94 | 4 |

---

## Task 1: The payload builder — one artifact, both legs

**Files:**
- Modify: `src/iladub/etkl/membrane.py` — add `_payload`; rewrite `_validate_pyshacl` (currently
  `:88-98`) and `_validate_rudof` (currently `:149-162`) to consume it
- Test: `tests/etkl/test_membrane_equiv.py` — add the divergence oracle
- Modify: `tests/etkl/test_decimal_typing.py:99` — **parity breaks this test; see Step 4**

**THE ONE TEST PARITY BREAKS — measured, not predicted.** `test_the_differential_is_not_vacuous`
(`tests/etkl/test_decimal_typing.py:99-114`) asserts `p is False` and `r is True`: that the two legs
**split** on a float-valued decimal. Parity removes that split by construction — pySHACL will see
the re-parsed graph and return `True`. Measured by reading every membrane call site in that file
(`grep -n "_validate_pyshacl\|_validate_rudof" tests/etkl/test_decimal_typing.py` → lines 94-95,
110-111, 135-136): **only** the pair at `:110-111` asserts a split; the other two assert agreement,
which parity preserves. So exactly one test changes, and Step 4 says what it becomes.

**Interfaces:**
- Consumes: `subclass_closure(data_graph, ont_graph) -> Graph` — **unchanged and still public**;
  `tests/etkl/test_closure_equiv.py` depends on it.
- Produces: `_payload(data_graph: Graph, ont_graph: Graph) -> tuple[Graph, str]` — the re-parsed
  graph and the N-Triples document it was parsed from, from **one** serialization.

**Obligations (write the body yourself):**

1. expand via `subclass_closure`;
2. serialize the expansion to N-Triples **once**;
3. return `(Graph().parse(that string), that same string)`.

**Invariants this must preserve:**

- **rudof's input is bit-identical to today.** Only pySHACL's input changes. If you cannot
  demonstrate this, you have changed the wrong thing.
- **Placement is load-bearing.** `tests/etkl/test_membrane_equiv.py:35-40` calls the two leg
  functions **directly**, bypassing `validate()`. A builder living in `validate()` leaves the
  battery exactly as blind as it is now. `_payload` must sit below the legs.
- `subclass_closure`'s signature and behaviour do not change.

**MEASURE before writing the call, do not assume:** run `python -m pytest tests/etkl/test_closure_equiv.py -q`
first and record its result, so any later change there is attributable to you and not inherited.

- [ ] **Step 1: Write the failing test — the divergence oracle**

This test **fails on agreement**. It is the inverse of a normal test: it pins that the transport
does not canonicalize, so that parity can never be bought by blinding both engines (spec §5).

```python
def test_the_transport_does_not_canonicalise_lexical_forms():
    """THE ORACLE (spec §5). Both legs now receive the SAME N-Triples document, but each
    parses it with its own parser — and rdflib's parser silently rewrites "5e-05" into
    "0.00005" while rudof judges the bytes as written. rudof is spec-correct: exponential
    notation is outside xsd:decimal's lexical space.

    THIS TEST FAILING BECAUSE THE ENGINES NOW AGREE IS BAD NEWS, NOT GOOD. It means someone
    canonicalised the payload — value-parity — buying agreement by making both engines blind
    to ill-typed literals. That is the failure mode this loop exists to prevent.
    """
    from iladub.etkl import membrane
    shapes = Graph().parse(data="""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        @prefix ex: <urn:parity:> .
        ex:S a sh:NodeShape ; sh:targetClass ex:Box ;
          sh:property [ sh:path ex:x0 ; sh:datatype xsd:decimal ; sh:minCount 1 ] .
    """, format="turtle")
    EX = Namespace("urn:parity:")
    g = Graph()
    g.add((EX.b1, RDF.type, EX.Box))
    g.add((EX.b1, EX.x0, Literal(float(5e-05), datatype=XSD.decimal)))

    graph_payload, nt_payload = membrane._payload(g, Graph())
    assert '"5e-05"' in nt_payload, (
        "the transport must carry the lexical form as written; if this fails, the payload "
        "builder is canonicalising and the oracle below is meaningless")

    p, _ = membrane._validate_pyshacl(g, shapes, Graph())
    r, _ = membrane._validate_rudof(g, shapes, Graph())
    assert p is True, "rdflib's parser repairs the lexical form before pySHACL judges it"
    assert r is False, "rudof judges the bytes as written, and is spec-correct"
```

- [ ] **Step 2: Run it and watch it fail**

Run: `python -m pytest tests/etkl/test_membrane_equiv.py::test_the_transport_does_not_canonicalise_lexical_forms -v`
Expected: FAIL — `AttributeError: module 'iladub.etkl.membrane' has no attribute '_payload'`.

- [ ] **Step 3: Implement `_payload` and rewire both legs**

Per the obligations and invariants above. Docstring must state the PROCEDURAL classification and
the parity contract in the spec's words: *both engines receive the same N-Triples document; each
parses it with its own parser; parser differences are engine differences.*

- [ ] **Step 4: Rewrite the one test parity supersedes**

`test_the_differential_is_not_vacuous` asserted the legs split. They no longer do, and its own
comment already anticipated this: *"THIS TEST FAILING IS GOOD NEWS in one direction — it would mean
pySHACL stopped inspecting the in-memory value."* Parity is exactly that, deliberately.

Its subject — *the constraint actually bites, so the test above proves something* — survives at the
level where the split still exists. Rewrite it to assert that pySHACL returns `False` on the **live**
graph and `True` on `_payload`'s graph, from the same source triples. That pins the real, falsifiable
claim this task makes: **parity changed what pySHACL is handed.** Keep the existing docstring's
warning voice; say in it that the split moved from the membrane to the transport.

Do **not** simply delete it, and do **not** weaken it to `p == r`.

- [ ] **Step 5: Run the oracle, then the whole differential**

Run: `python -m pytest tests/etkl/test_membrane_equiv.py tests/etkl/test_closure_equiv.py tests/etkl/test_decimal_typing.py -q`
Expected: PASS, with no test lost relative to the Step-2 measurement.

- [ ] **Step 6: Run the full fast suite and record any verdict change**

Run: `python -m pytest tests/ -q -m "not corpus"`
Expected: 1141 passed, 7 skipped, 1 xfailed — the same totals, since Step 4 rewrote the single test
parity supersedes rather than removing it. **Any other deviation is a verdict change caused by
parity and must be reported in the task report before Task 2 starts** — that is the whole reason
parity lands before the unpin (spec §7).

- [ ] **Step 7: Commit**

```bash
git add src/iladub/etkl/membrane.py tests/etkl/test_membrane_equiv.py \
        tests/etkl/test_decimal_typing.py
git commit -m "fix(membrane): one N-Triples artifact, both legs (closes R94's asymmetry)"
```

## FALSIFICATION

Revert `_validate_pyshacl` to taking the live graph (one line), leaving `_payload` in place. Show
`test_the_transport_does_not_canonicalise_lexical_forms` **failing** on the `p is True` assertion —
pySHACL sees the un-parsed float literal and returns `False`. Restore; show the suite green.

---

## Task 2: `audit_literals` — the guard for what parity hides

**Files:**
- Modify: `src/iladub/etkl/membrane.py` — add `audit_literals`; `_payload` grows `audit`
- Modify: `tests/etkl/test_row_groups.py` — two fixtures build float-valued decimals
- Modify: `tests/etkl/test_membrane_equiv.py` — the Task 1 oracle now passes `audit=False`
- Test: `tests/etkl/test_decimal_typing.py` — the guard's falsification

**Interfaces:**
- Produces: `audit_literals(graph: Graph) -> None` — raises on violation, returns nothing.
- Changed: `_payload(data_graph, ont_graph, *, audit: bool = True) -> tuple[Graph, str]`.

**Two invariants, enforced in the same idiom as `subclass_closure`'s existing literal-subject
"INVARIANT GUARD here, not a repair" (`membrane.py:240-242`):**

- **TYPE** — a literal's `.value` Python type matches its datatype's mapping. Catches R92's class.
- **LEXICAL** — a literal's lexical form equals what rdflib's parser would produce for it. Catches
  the `5e-05` class.

**Failure mode: raise.** Licensed by measurement, not preference (spec §2 P5): fast suite 1141
passed with **0 LEXICAL** hits, every corpus-marked test (36, real documents) **0 violations**.

**The `audit=False` escape hatch is a hazard and must be fenced.** Exactly two tests pass it — the
Task 1 oracle and the guard's own falsification. Step 1 below includes the test that keeps it that
way. **MEASURE, do not assume:** the two `test_row_groups.py` sites are the *only* fixture sites
that trip TYPE (`y0 ×15`); confirm by re-running the guard, because an earlier grep-based
attribution named the wrong files and was refuted.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_guard_refuses_a_float_valued_decimal():
    """R92's class. `Literal(round(x, 2), datatype=XSD.decimal)` keeps a Python float as
    .value while the lexical form is a valid xsd:decimal — pySHACL's datatype check is
    isinstance(value, Decimal), so it refuses; rudof only ever sees the lexical form and
    admits. Byte-parity hides this from the membrane, so the guard must catch it instead."""
    from iladub.etkl import membrane
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(round(307.474, 2), datatype=XSD.decimal)))
    with pytest.raises(ValueError, match="xsd:decimal"):
        membrane.audit_literals(g)


def test_the_membrane_itself_refuses_the_forbidden_form():
    """The guard must be WIRED, not merely present. This is the assertion that fails if
    _payload stops calling audit_literals — the direct-call test above would not notice."""
    from iladub.etkl import membrane
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(round(307.474, 2), datatype=XSD.decimal)))
    with pytest.raises(ValueError, match="xsd:decimal"):
        membrane._payload(g, Graph())


def test_the_guard_refuses_a_non_canonical_lexical_form():
    """The 5e-05 class. Exponential notation is outside xsd:decimal's lexical space, so
    rudof refuses it while rdflib's parser silently rewrites it to 0.00005 for pySHACL."""
    from iladub.etkl import membrane
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(float(5e-05), datatype=XSD.decimal)))
    with pytest.raises(ValueError, match="lexical"):
        membrane.audit_literals(g)


def test_the_guard_admits_a_well_formed_decimal():
    """The converted emitter form must pass untouched — the guard is not a repair."""
    from iladub.etkl import membrane
    g = Graph()
    g.add((BNode(), TAB.x0, Literal(Decimal(str(round(307.474, 2))))))
    membrane.audit_literals(g)          # must not raise


def test_the_audit_escape_hatch_is_not_used_in_production():
    """`audit=False` disables the guard. It exists for the two falsification tests and
    nothing else; a src/ call site passing it would silently disarm the membrane."""
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[2] / "src"
    offenders = [p for p in src.rglob("*.py") if "audit=False" in p.read_text()]
    assert offenders == [], f"audit=False must never appear under src/: {offenders}"
```

- [ ] **Step 2: Run them and watch them fail**

Run: `python -m pytest tests/etkl/test_decimal_typing.py -q -k "guard or escape_hatch or membrane_itself"`
Expected: FAIL — `module 'iladub.etkl.membrane' has no attribute 'audit_literals'`.

- [ ] **Step 3: Implement `audit_literals` and wire it into `_payload`**

Raise a `ValueError` naming the predicate, the datatype, and the offending literal — a human reads
this. The message must contain `xsd:decimal` for a TYPE violation and `lexical` for a LEXICAL one,
per the tests above.

- [ ] **Step 4: Convert the fixtures, and route the two tests that need the forbidden form**

`tests/etkl/test_row_groups.py` — the two float-valued `y0` sites become `Decimal(str(...))`.
Nothing about those tests is about literal typing; this is mechanical. **MEASURE rather than trust
this list:** re-run the guard over the fast suite and confirm these are the only TYPE sites. An
earlier grep-based attribution named the wrong files and was refuted by re-running them.

Two tests must still construct the forbidden form and therefore need `audit=False`:

- the Task 1 divergence oracle — the guard is the *production* defence, the oracle is about the
  *transport*;
- `test_the_differential_is_not_vacuous` as rewritten in Task 1 Step 4, which compares pySHACL on
  the live graph against pySHACL on `_payload`'s graph and so must reach `_payload` with the
  forbidden form intact.

Both get a comment naming why. Neither is converted — converting them destroys their subject.

- [ ] **Step 5: Run the full fast suite and the corpus battery**

Run: `python -m pytest tests/ -q -m "not corpus"` then `python -m pytest tests/ -q -m corpus`
Expected: fast suite green; corpus **36 passed** with the guard live — the measurement that
licensed `raise` in the first place, now enforced rather than observed.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/membrane.py tests/etkl/test_decimal_typing.py \
        tests/etkl/test_row_groups.py tests/etkl/test_membrane_equiv.py
git commit -m "feat(membrane): literal-hygiene guard for what byte-parity hides"
```

## FALSIFICATION

Delete the `audit_literals` call from `_payload` — leaving the function itself in place. Show
`test_the_membrane_itself_refuses_the_forbidden_form` **failing**, while
`test_the_guard_refuses_a_float_valued_decimal` still passes because it calls the function directly.
**That pair is the point:** a guard that exists but is not wired is exactly the defect a
direct-call test cannot see. Then delete `test_the_audit_escape_hatch_is_not_used_in_production`'s
subject by adding `audit=False` at one `src/` call site and show that test failing too. Restore
both; show the suite green.

---

## Task 3: Skolemize, and remove the pin

**Files:**
- Modify: `src/iladub/etkl/membrane.py` — skolemize inside `_payload`; de-skolemize report text;
  rewrite `validate`'s docstring at `:44-70`
- Modify: `src/iladub/etkl/compile.py:396` (delete `_DEC_ENGINE`), `:440` (drop `engine=`)
- Modify: `src/iladub/feed.py:615` (drop `engine=`)
- Modify: `tests/etkl/test_compile_membrane_shapes.py:59` (asserts `_DEC_ENGINE == "pyshacl"`)
- Modify: `tests/etkl/test_membrane_equiv.py` — leg 5, and `:351`

**Why this is safe, measured (spec §2 P3, P4):** skolemize is verdict-neutral for pySHACL in both
directions and unblocks rudof in both. No shape anywhere uses `sh:nodeKind`
(`grep -n "nodeKind" vocab/shapes/*.ttl` → no matches) and no `sh:sparql` body tests
`isBlank`/`isIRI`/`isURI`/`BNODE` (grep → no matches), so skolemizing cannot flip a constraint.

**MEASURE these two before writing the code — they are named, not answered (spec §6, §7):**

1. What IRI shape `Graph.skolemize(authority=…)` actually produces in this rdflib version. P3
   observed the *default* (`https://rdflib.github.io/.well-known/genid/rdflib/N…`) reaching the
   human-read report. Decide the de-skolemization from what you measure, not from this sentence.
2. The extra parse's cost on a **real 8.6k-triple corpus page**. Spec P6 measured 0.2 ms on a tiny
   decision graph and explicitly **does not license** a claim about a real page. Record the figure
   in the task report; it is the loop's only performance evidence.

### THE TRAP — read this before touching leg 5

`tests/etkl/test_membrane_equiv.py:300-301` says: *"THIS TEST FAILING IS GOOD NEWS. It means rudof
learned to evaluate `sh:sparql` on blank-node focus nodes."*

**That comment becomes FALSE the moment skolemize lands.** The test stops raising because we routed
around the incapacity, not because rudof gained it. Deleting the test on the strength of its own
comment destroys the only standing justification for skolemizing at all.

Both surviving leg-5 tests must therefore drive `pyrudof` **directly**, on their own un-skolemized
serialization, rather than through `_validate_rudof`. Their subject is *rudof*, not our membrane —
making that explicit is the fix, and it avoids a second escape-hatch flag.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_payload_contains_no_blank_nodes():
    """The one-line structural invariant that makes the unpin safe: rudof can never be
    handed a blank-node focus node, because the membrane never produces one."""
    from iladub.etkl import membrane
    graph_payload, nt_payload = membrane._payload(_bnode_promotion(), _dec_ont())
    bnodes = {t for t in graph_payload.all_nodes() if isinstance(t, BNode)}
    assert bnodes == set(), f"the payload must be blank-node free, found {len(bnodes)}"
    assert "_:" not in nt_payload


def test_both_engines_agree_on_a_blank_node_promotion_through_validate():
    """The one-engine story, asserted through the PUBLIC seam. This could not be written
    while _DEC_ENGINE pinned pySHACL — validate() raised on a forced rudof."""
    from iladub.etkl import membrane
    g = _bnode_promotion()
    p, _ = membrane.validate(g, _dec_shapes(), _dec_ont(), engine="pyshacl")
    r, _ = membrane.validate(g, _dec_shapes(), _dec_ont(), engine="rudof")
    assert p is True and r is True

    bad = _bnode_promotion()
    pd = next(bad.subjects(RDF.type, ILADUB.PromotionDecision))
    for o in list(bad.objects(pd, DEC.optionSpace)):
        bad.remove((pd, DEC.optionSpace, o))
    pb, _ = membrane.validate(bad, _dec_shapes(), _dec_ont(), engine="pyshacl")
    rb, _ = membrane.validate(bad, _dec_shapes(), _dec_ont(), engine="rudof")
    assert pb is False and rb is False, "both must still REFUSE an under-furnished decision"


def test_rudof_itself_still_cannot_evaluate_sparql_on_a_blank_node_focus():
    """THE STANDING JUSTIFICATION FOR SKOLEMIZING. This drives pyrudof DIRECTLY on an
    un-skolemized serialization — its subject is rudof, not our membrane.

    THIS TEST FAILING IS GOOD NEWS: rudof gained the capability and the skolemize step in
    _payload can be reconsidered. It must NOT be read as good news that _validate_rudof
    stopped raising — that happens because we route around the incapacity.
    """
    import pyrudof
    from iladub.etkl import membrane
    expanded = membrane.subclass_closure(_bnode_promotion(), _dec_ont())
    r = pyrudof.Rudof(pyrudof.RudofConfig())
    r.read_shacl(_dec_shapes().serialize(format="turtle"), format=pyrudof.ShaclFormat.Turtle)
    r.read_data(expanded.serialize(format="nt"), format=pyrudof.RDFFormat.NTriples)
    with pytest.raises(ValueError) as exc:
        r.validate_shacl(mode=pyrudof.ShaclValidationMode.Native)
    assert "SHACL" in str(exc.value), str(exc.value)


def test_the_report_does_not_leak_skolem_iris():
    """A human reads validation reports. Skolem IRIs are an implementation detail of the
    transport and must not appear in one."""
    from iladub.etkl import membrane
    bad = _bnode_promotion()
    pd = next(bad.subjects(RDF.type, ILADUB.PromotionDecision))
    for o in list(bad.objects(pd, DEC.optionSpace)):
        bad.remove((pd, DEC.optionSpace, o))
    for engine in ("pyshacl", "rudof"):
        conforms, report = membrane.validate(bad, _dec_shapes(), _dec_ont(), engine=engine)
        assert conforms is False
        assert "genid" not in report, f"{engine} report leaks a skolem IRI:\n{report}"
```

- [ ] **Step 2: Run them and watch them fail**

Run: `python -m pytest tests/etkl/test_membrane_equiv.py -q -k "payload_contains_no_blank or agree_on_a_blank or report_does_not_leak"`
Expected: FAIL — `test_both_engines_agree…` raises the capability-pin `ValueError`;
`test_the_payload_contains_no_blank_nodes` finds blank nodes; the report test finds `genid`.

- [ ] **Step 3: Skolemize in `_payload`, de-skolemize the report**

Skolemize **after** `audit_literals` and **before** serialization, so the guard still sees the graph
as emitted. De-skolemize report text in both legs. Both are PROCEDURAL; say so.

- [ ] **Step 4: Remove the pin**

Delete `compile._DEC_ENGINE`; drop `engine=` at `compile.py:440` and `feed.py:615`. **Keep**
`validate()`'s `engine=` parameter and **keep** its raise on an `ILADUB_MEMBRANE` conflict — the
behaviour is still right, but its stated reason changes from *"a capability rudof lacks"* to
*"an operator must never be handed the other engine's verdict unannounced."* Rewrite the docstring
at `:44-70` accordingly; the measured-incapacity paragraph is now history, not justification.

Delete `tests/etkl/test_compile_membrane_shapes.py:59`'s `_DEC_ENGINE` assertion and
`test_membrane_equiv.py:351`'s `test_the_capability_pin_refuses_a_conflicting_forced_engine`;
rewrite the latter's surviving intent — an `ILADUB_MEMBRANE`/`engine=` conflict still raises.

Rewrite `test_rudof_handles_a_blank_node_focus_once_the_sparql_shapes_are_gone` (`:332`) to drive
`pyrudof` directly as in Step 1, or it becomes **vacuous**: after skolemize there are no blank nodes
left for it to be about.

- [ ] **Step 5: Run everything, including the corpus, and record the cost**

Run: `python -m pytest tests/ -q -m "not corpus"` then `python -m pytest tests/ -q -m corpus`
Expected: fast suite green; corpus 36 passed. Record the per-page timing measured in the preamble.

Then confirm the one-engine story end to end:
`ILADUB_MEMBRANE=rudof python -m pytest tests/ -q -m "not corpus"` — this **raises today** at the
pinned call and must now run clean. That command is the loop's headline evidence.

- [ ] **Step 6: Commit**

```bash
git add src/iladub/etkl/membrane.py src/iladub/etkl/compile.py src/iladub/feed.py \
        tests/etkl/test_membrane_equiv.py tests/etkl/test_compile_membrane_shapes.py
git commit -m "fix(membrane): skolemize the payload and remove the pySHACL pin (closes R88)"
```

## FALSIFICATION

Remove the skolemize step from `_payload`. Show `test_the_payload_contains_no_blank_nodes` **failing**
on a non-empty blank-node set and `test_both_engines_agree_on_a_blank_node_promotion_through_validate`
**failing** with rudof's `ValueError`. Separately, restore skolemize but drop the report
de-skolemization and show `test_the_report_does_not_leak_skolem_iris` failing on `genid`. Restore
both; show the suite green.

---

## Task 4: The record

**Files:**
- Modify: `docs/wiki/concepts/grounding-membrane.md`
- Modify: `docs/superpowers/residues-open.md`, `docs/superpowers/residues.md`

**MEASURED:** that wiki page currently mentions neither engine nor the pin
(`grep -n "rudof\|pySHACL\|pin\|engine" docs/wiki/concepts/grounding-membrane.md` → no matches), and
no `mkdocs.yml` nav page describes membrane engines (`grep -n "rudof\|membrane" mkdocs.yml` → no
matches). So this is an **increment**, and nothing blocks a release tag.

- [ ] **Step 1: Wiki increment**

Add the one-engine membrane section: the byte-parity contract, the guard and the two classes it
catches, and — stated plainly, because it is the interesting part — that the engines still disagree
on ill-typed lexical forms and that **rudof is right there**. Wiki pages are propositions: tag
confidence and cite the spec.

- [ ] **Step 2: Strike R88 and R94**

Strike both numbers (`~~R88~~`, `~~R94~~`) and record the closure evidence **in place**. Do **not**
delete the rows — a deleted row erases the proof of repair and shrinks the denominator. Update the
index lines in `residues.md` to `closed`. Register goes **15/84 → 17/84**.

R94's closure evidence must record that its own prescribed remedy was **refuted**: feeding both legs
the same artifact does not make them agree, because the parser is inside the engine boundary.

- [ ] **Step 3: Raise a residue for the escape hatch, if one is owed**

If `audit=False` survives in the tree, open a row: *a guard with a test-only disable flag is a
standing hazard, fenced today by `test_the_audit_escape_hatch_is_not_used_in_production`*. Carry the
`(closed/total)` snapshot at raise time — `(17/85 closed)`.

- [ ] **Step 4: Verify governance and commit**

Run: `python -m pytest tests/test_doc_governance.py -q`
Expected: PASS.

```bash
git add docs/
git commit -m "docs: one-engine membrane; strike R88 and R94"
```

## FALSIFICATION

Doc-only task. In place of a code falsification, paste `git diff --stat` for the residue files
showing the rows **modified, not removed**, and the `grep -c "^| ~~R" docs/superpowers/residues-open.md`
count before and after.

---

## Self-Review

**Spec coverage.** §3 parity contract → Task 1. §4.1 builder → Task 1. §4.2 guard → Task 2.
§4.3 unpin → Task 3. §5 both oracles → Task 1 Step 1 and Task 2 FALSIFICATION. §6 test rewrites and
the skolemize seam → Task 3. §7 ordering → task order; the "not done" list is carried into Global
Constraints and Task 4. §8 doc impact → Task 4. **No spec section is unassigned.**

**Placeholder scan.** No TBD/TODO. Every code block is a test, given verbatim; no implementation
body appears anywhere, per CLAUDE.md plan rule 1.

**Type consistency.** `_payload` is `(Graph, ont) -> (Graph, str)` in Tasks 1 and 3 and gains only
the keyword-only `audit` in Task 2. `audit_literals(graph) -> None` is used identically in Tasks 2
and 3. Helpers reused from the existing battery — `_bnode_promotion` (`:303`), `_dec_shapes`
(`:188`), `_dec_ont` (`:195`) — are referenced by their current names. Every name the supplied tests
use was checked against the target file's imports: `test_membrane_equiv.py:10-12` provides `Graph`,
`Literal`, `Namespace`, `URIRef`, `RDF`, `SH`, `XSD`, `TAB`; `test_decimal_typing.py:24-31` provides
`BNode`, `Decimal`, `pytest`, `RDF`, `XSD`.

**Two defects were found in this plan by that check and fixed before it shipped:**

1. The supplied guard tests referenced an undefined `TAB_N`; `test_decimal_typing.py` uses
   `n = BNode()`. Corrected to `BNode()`.
2. **Load-bearing.** The plan originally handled `test_the_differential_is_not_vacuous` in Task 2 as
   a guard-bypass problem. It is not: that test asserts the two legs **split**, and **Task 1's
   parity removes the split**, so it breaks one task earlier and for a different reason. Moved to
   Task 1 Step 4 with an explicit rewrite, and Task 1's file list now names it. Found by reading
   every membrane call site in that file rather than trusting the plan's own narrative.

**Reconciled against spec §7** (plan rule 5). No supplied test asserts the engines agree on an
ill-typed lexical form; the Task 1 oracle asserts the opposite, deliberately. No supplied test needs
a shape change, an emitter change, or state the code cannot construct: every fixture it needs
(`_bnode_promotion`, the forbidden decimal form at `test_decimal_typing.py:108`) exists today.
