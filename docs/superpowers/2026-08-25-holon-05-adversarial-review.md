# Adversarial review — `the membrane reports its health` (`holon:05`)

**Date:** 2026-08-25 · **Target:** `docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md`
· **`main` @ `d343d23`** (merge of PR #117) · **Shape: originating, run at 106,589 tokens — 2.1× the
50k floor, override logged.** Measurement was delegated to three subagents; the findings and the
ruling below are this session's.

**This review is the named step required since 2026-08-24** and never previously run. Its only job is
to attack the spec's premises **before** any plan (memory `adversarial-spec-review`).

## Verdict

**The spec does not survive unchanged.** Its measurement discipline is real — every line-citation in
§2.3 and §2.4 checked out to the digit, and 9 of 13 claim families came back CONFIRMED. The failures
are almost all of the second kind the review exists for: **true facts that do not support the
conclusion drawn from them.** Eight blocking findings (B1–B8) change the design; three (P1–P3) change
the plan; five bookkeeping errors must be corrected before the plan cites them.

**B6 is the one to read first** if only one is read: the design's `Compromised` guard fails *upward*
on a datatype slip, silently reporting `Intact` for a refusing membrane.

**What survives is substantial and should not be re-derived:** §2.1's safety argument entirely,
§5.4's zero-legs refutation, every line citation in §2.3/§2.4, §5.5's corpus table **confirmed to the
triple**, and §4.3's CONSTRUCT — which executes, discriminates, is idempotent, and yields nothing
without a verdict fact, exactly as designed.

The three targets the handoff named are answered at the end (§ The three targets).

---

## B1 — The subject is the wrong class, and on the refusing path it contradicts itself

§4.1 mints `<doc> a etkl:CleanDocumentHolon` and §4.4 argues *"the compiled graph **is** the
CleanDocumentHolon's interior."* The vocabulary says otherwise, in two independent places:

```
$ sed -n '62,66p' vocab/ontology/etkl-holons.ttl
etkl:CleanDocumentHolon a owl:Class ;
    rdfs:subClassOf etkl:DocumentHolon ;
    …
    rdfs:comment "The compiled output as a holon. Interior: the grounded graph + the promotion
    decisions that produced it. …"@en .

$ sed -n '112p' docs/holonic-interaction.md
| the **grounded graph** | the clean document holon's **interior** |
```

The compile graph contains **neither** constituent, and the spec measured both absences itself:

- **0 `iladub:PromotionDecision`** in all 34 compile-scope measurements (spec §5.6), independently
  reconfirmed on apple this session (`PromotionDecision in graph: 0`).
- **0 `iladub:GroundedNode`** on the compile path — `iladub:wasPromotedBy`/`GroundedNode` are written
  only at `ground.py:175-176` and `splitkey.py:192-193` (spec §2.2), and §4.4 measures the grounded
  graph as a **disjoint artifact** with no merge site anywhere.

So the design would type a graph `CleanDocumentHolon` when it contains none of the two things that
class's interior is *defined* to be. **This is R126's other half wearing new clothes** — R126 is
"the fabric has no instance data"; this is "the first instance data does not match the class's
extension."

**And it is self-contradictory on one of the three paths.** `etkl:Compromised` reads (`:84`):
*"Interior violates the membrane: **the holon is not clean**."* §4.5 row 2 mints, from one CONSTRUCT,
into one graph:

```
<doc> a etkl:CleanDocumentHolon ; etkl:membraneHealth etkl:Compromised .
```

*"This clean holon is not clean."* Nothing in the repo would refuse it — see B2's governance note.

**Options, with costs:**

| | change | cost |
|---|---|---|
| **(a) recommended** | mint one new concrete term, `etkl:CompiledDocumentHolon ⊑ etkl:DocumentHolon`, and type the doc with it | one term in a loop already bumping `owl:versionInfo`; keeps §4.1's R126-instantiation claim; removes the contradiction on all three paths |
| (b) | drop the type triple entirely | free, and `rdfs:domain` is unenforced anyway (B2 note) — but §4.1 loses its R126 claim, which is one of the loop's two stated products |
| (c) | amend `CleanDocumentHolon`'s definition so its interior is the compiled graph | re-opens what the doc-holon fabric means; that is `holon:06`, and §9 scopes `holon:06` out |

---

## B2 — The verdict fact is a malformed `sh:ValidationReport`

§4.2 mints:

```
<{doc}#membrane-report> a sh:ValidationReport ; sh:conforms "false"^^xsd:boolean ; prov:wasDerivedFrom <{doc}> .
```

**SHACL defines `sh:conforms` on a validation report as true if and only if the report carries no
`sh:result`** (SHACL Rec §3.6). A report typed `sh:ValidationReport` with `sh:conforms false` and
**zero** `sh:result` is inconsistent with the class's own definition. *(This is the one claim in this
review measured against the standard rather than against the repo — check the Rec text before
acting.)*

Two supporting measurements:

- **This would be the first minted `sh:ValidationReport` in the tree.** The only occurrences today are
  two hand-written Turtle *strings* in a parser test (`tests/etkl/test_membrane.py:269,272`); `src/`
  reads `SH.conforms` once (`membrane.py:173`) and discards. There is no precedent to inherit.
- **Nothing would refuse the malformed node.** Measured: no SHACL shape anywhere in the repo targets
  or constrains `etkl:DocumentHolon`, `etkl:CleanDocumentHolon`, `etkl:MembraneHealth`, or
  `etkl:membraneHealth` (`git grep` over all 17 tracked shape files → exit 1 for the fabric; the six
  `etkl:` targets that exist are contract classes in `vocab/shapes/etkl-shapes.ttl`, which the compile
  membrane never loads).

**This is also the honest answer to the stored-label objection** (target 1). The verdict fact is a
claim about a *mutable graph*, stored **inside that graph**. Raw extraction records an observation of
an immutable source; this records the current state of the artifact it lives in, and goes stale the
moment anything is added — including the health triple added microseconds later. O6 patches the
immediate self-invalidation; it does not make the triple a fact rather than a label.

**Recommendation.** Keep the PROCEDURAL *class* — the classification is right, an engine verdict is
not derivable from the evidence graph — and change the *subject* from the graph's conformance status
to **the validation act**: an `etkl:MembraneValidation ⊑ prov:Activity` node, `prov:used` the doc,
carrying `sh:conforms` **and the leg identity `_validate` already returns and the design discards**
(`conforms, text, legs = _validate(...)`, `document.py:1624`). An activity record is immutable and
always true; a state label is neither. It also aligns with the repo's own norm — CLAUDE.md
§ Serialization: `dec:DecisionHolon ⊑ prov:Activity`, evidence via `prov:used`, *"don't reinvent
provenance."*

The CONSTRUCT of §4.3 changes by one line (`?report a etkl:MembraneValidation`).

---

## B3 — `Weakened`'s re-reading contradicts the criterion the loop is about to flip, and the amendment set is under-scoped

The criterion's `prog:statement` is a **verbatim** join of its `prog:source` lines
(`tests/arc-manifest.ttl:354`, confirmed to the character):

> "A membrane-health check that computes and reports a compiled document's cleanliness
> (etkl:membraneHealth → Intact / Weakened / Compromised) **from validation results**."

Held candidates are **not** validation results. Under the design, one of the three values is derived
from evidence the criterion's own statement excludes — and §8 item 4 flips that criterion to
`prog:met true`.

Two further defects in the warrant §4.4 offers:

1. **The cited line says the opposite of what it is cited for.** §4.4 grounds the reading in *"literally
   the dotted 'held at the membrane' edge in `docs/holonic-interaction.md:55`."* That edge is at
   **:56**; **:55** is the `crossed ✔ — assertion` edge. And :56's candidates are fed by
   `PORTAL ==> MEM` — the **grounding portal's** output, which §4.4 *itself* measures as living in a
   disjoint graph and excludes by design. The spec cannot both exclude the portal's propositions and
   claim the diagram edge that depicts them as its warrant.
2. **`etkl:MembraneHealth`'s own comment contradicts the design too** (`:77`): *"the result of
   validating its interior against its membrane (SHACL shapes)."* §4.6 amends only `Weakened` (`:81-82`).

**Recommendation.** Decision 2 is defensible on the merits — held propositions *are* a better reading
of "cleanliness" for this project than SHACL severities, which do not exist. But it must be carried
out completely and stated as what it is: **a semantic amendment to the health model**, not a
one-comment tweak. The amendment set is at least:

- `etkl:Weakened` `rdfs:comment` (§4.6, already planned)
- `etkl:MembraneHealth` `rdfs:comment` (`:77`)
- `etkl:CleanDocumentHolon` `rdfs:comment` (`:66`) — or B1(a) instead
- `docs/holonic-interaction.md:160-161` — §8 item 6 already edits this line to move it out of
  *"Planned work"*; **edit its wording in the same act**, since it is the criterion's `prog:source`
- `tests/arc-manifest.ttl:354`'s `prog:statement`, which quotes it verbatim

Amending a criterion's statement in the loop that closes it deserves its own comment in the manifest
saying so. The alternative — keep validation-only semantics and scope `Weakened` out as a residue —
is still open and was the option decision 2 rejected; it is *more* honest but ships a three-valued
property with an unmintable value.

---

## B4 — `Compromised` has no test vehicle, and §10 does not name it as a seam

**Measured: no test in the tree drives `compile_tables` or `compile_document` to raise.**

```
$ grep -rn -B3 "compile_tables(\|compile_document(" tests | grep -i "raises"
(no output)
```

The nearest precedents both **avoid** the raise site:

| existing mechanism | why it does not serve O2/O7 |
|---|---|
| `tests/etkl/test_membrane_equiv.py:108,152` — compiles with `validate_shapes=False` to *bypass* the guard, mutates the real graph, calls `membrane.validate` directly | never reaches `document.py:1626`, so it can neither mint the verdict fact nor exercise `MembraneRefusal` |
| `tests/etkl/test_compile_membrane_shapes.py:96,120` — hand-built bad graphs into `compile_mod._validate` | same: below the raise site |
| `tests/etkl/test_escalation_wiring.py:84` (T3.2) | documents the only known route to a real refusal as a **manual source mutation**, not an executable test |
| `tests/test_concept_feed.py:344-351` | forces `feed.py:643` — the grounding membrane §9 scopes out |

So **O2's `Compromised` leg and O7 both require a mechanism that does not exist**, and the cheapest
one available (monkeypatch `validate`/`_validate` to return `False`) is the R73 defect-5 shape: a test
that would pass with its subject deleted, because nothing real produced the refusal.

This is the single highest-risk item for the plan, and the spec is silent on it — §10 lists five
seams and this is not among them. **It must be named as a seam with the fact to measure**: *what is
the smallest real graph mutation that makes the document leg refuse at `document.py:1624`, and is it
reachable without `validate_shapes=False`?* `test_membrane_equiv.py:115-146`'s `_mutations`
(`drop-onPage`, `blank-cellText`, `drop-bbox`, `orphan-unit-marker`) are the candidate mutations —
but they are applied *after* a bypassing compile, and the plan must establish whether any of them can
be applied *before* validation on a real path.

---

## B5 — Page-scope refusal preempts document-scope refusal, so `Compromised` is unreachable for a whole class of violation

`compile_document` passes `validate_shapes` straight down to every page compile:

```
$ grep -n "compile_tables(" src/iladub/etkl/document.py
1274:        pages.append(compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes, …
1337:        rep2 = compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes, …
1474:        rep_a = compile_tables(pdf_path, page_number=p, validate_shapes=validate_shapes, …
```

Those calls are at `:1274/:1337/:1474`; document validation is at `:1624`. §9 explicitly keeps
`compile.py:1173`'s bare `AssertionError`, and the catcher census (P2) confirms nothing between them
catches it. **Therefore: any page-level violation aborts the document before document-scope validation
runs — no verdict fact, no health triple, no carried graph, and a bare `AssertionError` rather than
`MembraneRefusal`.**

§5's hazard table row 3 says `Compromised`'s unreachability is answered by *"§4.5 mints before the
raise."* That answer covers **one of the two raise sites a document can hit**, and it is the
*less* likely one — page shapes (`tab`) are where the violations live; the document leg is `dec` plus
`tab` over merged content.

**This does not require minting health at page scope** (§9's scope-out can stand). It requires the
spec to state the consequence out loud: `Compromised` reports document-scope refusals only, page-scope
refusals still escape as an untyped `AssertionError`, and that asymmetry is a named residue rather
than an unnoticed hole.

---

## P1 — O3 is **not** fixture-only: the promotion clause can be pinned on a real execution path

§5.6 concludes: *"It cannot be pinned on real input: promoted = 0 in all 34 corpus measurements, so
the plan must build the graph by hand and must not reach for a corpus document."*

**The causal claim is confirmed exactly** — the `promote.py` emitters are proposer-driven, a bare
compile passes no proposer, so `promoted = 0` on the corpus (independently reconfirmed: apple → 11
candidates, **0** `PromotionDecision`). **The consequence is over-stated.** A test already exists that
compiles with a proposer wired, at the default `validate_shapes=True`, and asserts the promotion in
the committed graph:

```
tests/etkl/test_rowrole_integration.py:106
    test_caption_wrap_report_asserts_with_a_resolving_proposer
    → compile_tables(p, row_role_proposer=FakeRowRoleProposer(prop))
    → asserts list(rep.graph.subjects(RDF.type, ILADUB.PromotionDecision)) is non-empty
$ .venv/bin/python -m pytest tests/etkl/test_rowrole_integration.py tests/etkl/test_b1_3_merge_resolution.py -q -p no:randomly
10 passed in 16.72s
```

And at **document scope**, which no existing test does but the signature supports
(`document.py:1166`):

```
DOCUMENT SCOPE, with proposer: wall=2.6s
  PromotionDecision: 2  CandidateConcept: 2  held: 0  promoted: 2
DOCUMENT SCOPE, no proposer: wall=1.9s
  PromotionDecision: 0  CandidateConcept: 1
```

**held 0 / promoted 2 through the real membrane, in 2.6 seconds.** The distinction §5.6 failed to draw
is *corpus document* vs *real execution path*: this is a fixture PDF, but it is not a hand-built
graph, and it exercises the discriminator end-to-end. **O3 should use this vehicle.** It also gives
O1's third state a real-path sibling for free.

**And the residual should be registered, not prosed.** After P1, the true residual is narrower: the
clause is unexercised *on the corpus sweep*. The repo already owns the machinery for exactly this —
`tests/etkl/test_vacuity_registry.py` runs criterion 2 (**term reachability**: "a body naming a term
that appears nowhere in the data cannot fire") plus a **bidirectional** tripwire,
`test_no_registered_shape_has_gone_live`, so a registered-idle clause that later goes live *fails the
suite* and forces de-registration. That registry covers **shapes only**; this loop introduces the
first AXIOM `.rq` with the same property. R106's own row says *"the rule that catches it is prose"* —
a prose residue here would be its second instance. Extending criterion 2's term-reachability to
`vocab/queries/*.rq`, or registering `membrane-health.rq`'s promotion clause, converts it into a
machine tripwire. **Whether that fits this loop is the maintainer's call; the review's point is that
the prose residue is not the only option and is the weaker one.**

---

## P2 — Target 3's census: `MembraneRefusal` is safe, but "exhaustively" is over-claimed

Re-run and **widened** beyond the spec's `except`-statement search:

```
$ git grep -n "except AssertionError" -- src/ tests/ scripts/
tests/test_corpus.py:129        (re-raises at :130 — CONFIRMED)
$ git grep -n "except BaseException" / "except\s*:" / "suppress(" -- src/ tests/ scripts/
→ exit 1 for all three
```

The spec's **conclusion survives**: a subclass of `AssertionError` breaks nothing. But six
`pytest.raises(AssertionError)` catchers were not counted, and `pytest.raises` is a catcher:

```
tests/test_arc_ablation.py:698,704        arc-manifest linting — not a compile
tests/test_corpus_battery_unit.py:79,91,103   battery helpers; the compile is deliberately OUTSIDE the block (:90, :102)
tests/test_concept_feed.py:349            ← catches a real membrane AssertionError (the grounding leg, feed.py:643)
```

None wraps a compile, so the design holds. Two consequences: delete the word **"Exhaustively"** from
§2.4, and note that the omitted class is precisely the one that matters **if §9's grounding-leg
scope-out is ever revisited** — `test_concept_feed.py:349` would be the site that has to change.

---

## P3 — O2's cost, and its independence from the proposer

**Cost.** One document-scope compile of apple: **37.9 s** measured (`score 0.3556`, `3788` triples,
`11` candidates — matching §5.5 exactly). `graincorp-stem` is recorded at ~180 s
(`tests/test_corpus.py:96`). So O2's two real-input specimens add **~3.5 minutes** to a suite whose
baseline is already 2386.82 s, before the `Compromised` leg. The caption-wrap fixture compiles at
document scope in **1.9–2.6 s** — 15–70× cheaper, and the right vehicle for every leg that does not
specifically require a corpus document.

**Independence.** §3 is right that O1 must be hand-computed. **O2 is not independent**: the expected
values (`graincorp-stem → Intact`, `apple → Weakened`) were produced by running *the same
held-candidate SPARQL pattern* the query under test uses. If §2.2's discriminator is the wrong reading
of "held", the query and its oracle share the error. Either derive O2's expectations from a different
signal (the `CompilationReport`/`RegionReport` escalation verdicts, which are what *make* the
candidates), or state plainly that O2 is a **reachability** check and not an independence check —
§3's own standard.

---

## Bookkeeping errors — correct before the plan cites any of them

1. **§2.7's "20 of 45" is wrong, and conflates three populations.** Measured:
   `grep -l "^# GATE (CLAUDE.md §8):" vocab/queries/*.rq | wc -l` → **1** (`escalation-furnish.rq:10`,
   the file the spec calls canonical). Eight more use a *different* form,
   `# GATE CLASSIFICATION (CLAUDE.md §8):`. **20 is the count of files containing the word `AXIOM`**,
   11 of which carry no `CLAUDE.md §8` reference at all. The convention "20 of 45" describes does not
   exist at that scale; the author must **pick a form** (n=1 literal, or n=8 variant).
   *Also:* nothing enforces the header — the decimal lint strips comments before matching
   (`test_transform_gate.py:30`). What the lint **does** do is glob `vocab/queries/*.rq` with no
   explicit list, so a new `.rq` is covered automatically, with no wiring. §2.7's second claim is
   sound; its first is not.
2. **§2.4's "Exhaustively … the only"** — see P2.
3. **§5.4's pasted transcript cannot have come from one run.** `_validate(g, ("dec",))` on an *empty*
   graph raises `ValueError: … The provided input is empty` from `membrane.py:195` before any verdict;
   the `IndexError` half reproduces only on an empty graph (no `validate` call happens). Both halves
   are individually true, on different graphs. Rule 2 says the measurement is pasted inline — so it
   must be one reproducible run.
4. **§2.5's own quoted command now exits 0**, because the spec's text matches its own grep. Substance
   intact (zero hits outside `docs/` prose), but a `git grep` that sweeps `docs/` cannot be pasted as
   evidence *into* `docs/`. Scope it to `vocab/ src/ tests/ examples/`.
5. **Three off-by-one citations:** §4.1 cites `etkl-holons.ttl:44` for `DocumentHolon`'s "abstract"
   comment (it is `:45`; `:44` is the label); §4.4 cites `holonic-interaction.md:55` (it is `:56`, and
   see B3); R126's own row cites `etkl-holons.ttl:74-88` (the block is `75-89`).

---

## What survives the review untouched

- **§2.1's safety argument, entirely.** No `sh:closed` in any `.ttl` (exit 1); none of the five loaded
  shape files names an `etkl:` term; `etkl-holons.ttl` is not in `_FULL_ONT` (`compile.py:441,452,453`
  parse only `tab.ttl`, `dec.ttl`, `iladub.ttl`); `inference="none"` at `membrane.py:124-125`. All
  exact. **One caveat to carry:** it is true because `vocab/shapes/etkl-shapes.ttl` (the one shape file
  with 22 `etkl:` references) is **not loaded**, not because no shape file mentions `etkl:`.
- **§5.4's zero-legs refutation.** `_legs_for_document` is exactly the total one-liner at
  `document.py:1142-1162`, one production call site (`:1624`), pinned 4-way at
  `test_document_membrane_gate.py:22-33`. `_validate(g, ())` → `IndexError` at `compile.py:523`
  reproduced.
- **Every line citation in §2.3 and §2.4** — `membrane.py:45-46,108,124-126,159-174,297-315`;
  `compile.py:504-525,528-535,1115,1167-1170,1171,1173,1175`; `document.py:1623,1624,1626,1636-1639`.
  `DocumentReport` is constructed **by keyword** (so §10.4's R73 trap does not bite at document scope);
  `CompilationReport` is positional, page-scope only. At `document.py:1624/1626` the local `graph`
  **is** the returned object — nothing rebinds it, and `+=` mutates in place.
- **O4's premise, better than the spec knew.** `validate_shapes` defaults to **`True`** at both scopes
  (`document.py:1165`, `compile.py:539`), so health is on by default and the O4 state is a genuine,
  rare opt-out — only `scripts/probe_domain_range_agreement.py:265` and two test sites take it.
- **§5.5's apple specimen**, independently reproduced this session.

## One observation neither the spec nor the handoff raises

**The thing that reports the membrane's health is outside every membrane.** §2.1 proves the mint is
safe *because* nothing validates `etkl:` terms; the same fact means a malformed health signal — two
values for one document, a value outside the three individuals, a `CleanDocumentHolon` that is
`Compromised` (B1) — would pass silently. The concrete risk is not hypothetical: §4.3's CONSTRUCT
emits one health triple **per `sh:ValidationReport` node in the graph**, and nothing constrains that
to one.

For a project whose §3 principle is *SHACL-enforced* promotion epistemics, shipping the health signal
with **no shape at all** is worth a deliberate decision rather than a silence. A minimal
`MembraneHealthShape` — `sh:maxCount 1` on `etkl:membraneHealth`, `sh:in (Intact Weakened
Compromised)` — costs one shape file entry. Note it would need to be loaded to have any effect, which
touches §2.1's argument and must be re-measured if adopted.

---

## The specimens re-run, and three findings from executing the CONSTRUCT

**§5.5's two rows are CONFIRMED exactly, to the triple**, at document scope with `validate_shapes=True`
through the same public API `tests/test_corpus.py:106` drives:

| specimen | spec triples | measured | spec held | measured | PD | → |
| --- | --- | --- | --- | --- | --- | --- |
| `graincorp-stem-2026-07-31` | 29,999 | **29,999** | 0 | **0** | 0 | `Intact` (164.9 s) |
| `apple-fy2026q3-statements` | 3,788 | **3,788** | 11 | **11** | 0 | `Weakened` (36.1 s) |

**§4.3's CONSTRUCT executes and behaves as designed** in rdflib 7.6.0: `EXISTS` inside `BIND` is
supported, `!` on an `xsd:boolean` literal works, `false` correctly beats `held`, the result is
**idempotent** (set-identical on re-run over its own product), and it yields **zero triples** with no
verdict fact — so §4.5's third row is a genuine consequence, not a special case. Nothing pre-exists
to collide with. That much of the design is sound and should be preserved.

Three findings came out of running it.

### B6 — `!?conforms` fails **upward** if the datatype ever slips

```
[conforms = Literal("false"), no datatype ]  -> etkl:Intact  (graincorp) / etkl:Weakened (apple)
[conforms = Literal("false", datatype=xsd:string)] -> etkl:Intact / etkl:Weakened
```

A refusing membrane whose verdict is minted as `Literal(str(conforms))` rather than `Literal(False)`
reports **`Intact`**, silently: SPARQL's EBV on a non-empty string is `true`, so `!` yields `false`
and `Compromised` is unreachable. §4.2 shows `"true"^^xsd:boolean` in prose, but **nothing in the
design pins the datatype, and the failure direction is the worst one** — this is R73 defect 2's class
(*failing upward, invisible to the plan's own tests*), which CLAUDE.md names as the reason plans get
reviewed at all.

Fix, and the plan must do both halves: require `Literal(conforms)` (rdflib types a Python `bool` as
`xsd:boolean` automatically — measured), **and** make the query refuse to guess —
`IF(?conforms = false, …)` or a `datatype(?conforms) = xsd:boolean` filter — **and** carry an oracle
that asserts `Compromised` from a real `false`, which is B4's missing vehicle again.

### B7 — the health triple's subject is a hard-coded constant, identical for every document

```
$ grep -n "_DOC" src/iladub/etkl/compile.py src/iladub/etkl/document.py
compile.py:22    _DOC = "https://example.org/etkl/doc"
compile.py:572, document.py:268   (the only uses)
```

**Every compiled document in the corpus gets the same document IRI.** Two consequences the spec does
not state:

1. **§4.3's site constraint is load-bearing for a reason the spec does not give.** It justifies
   *"run over one document's graph, never a union"* as closed-world scoping. The stronger reason is
   **subject-IRI collision**: merge two documents and both health values land on one subject.
   Measured, with two report nodes on one `?doc`:
   ```
   -> 3 triples:  <…/doc> etkl:membraneHealth etkl:Compromised .
                  <…/doc> etkl:membraneHealth etkl:Intact .
   ```
2. **Nothing refuses that.** `etkl:membraneHealth` is a bare `owl:ObjectProperty`
   (`etkl-holons.ttl:86-89`) — no `owl:FunctionalProperty`, no `sh:maxCount`, and (B2) no shape
   targets it. This is the concrete instance of § *One observation neither the spec nor the handoff
   raises*, above, and it upgrades that observation from a principle to a measured defect.

**And the subject carries no other statement.** `https://example.org/etkl/doc` appears **nowhere** in
either compiled graph — not as subject, predicate, or object. This corroborates §4.1's R126 claim, but
it means the health triple would hang on an IRI with **zero links to the `…/doc/p0…` URIs that carry
all the content**. Combined with B1, the loop's "first instance data for the fabric" would be an
isolated node of the wrong class. Whether to also link it (`etkl:hasPage` / `prov:hadMember`) is a
design question the spec never reaches.

*Incidental, for the plan's cost model:* `interpret.run` (`interpret.py:19-30`) copies every input
graph into a fresh union — one call over the 29,999-triple stem is a full 30k-triple copy.

### B8 — `Intact` is reported for a document with 77 tokens of unread ink

`graincorp-stem` scores **0.9655**, not 1.0, and the design labels it `Intact`:

```
p0 band2 UNSUPPORTED_TABLE verdict=asserted tokens_asserted=586 tokens_escalated=27
p1 band1 UNSUPPORTED_TABLE verdict=asserted tokens_asserted=825 tokens_escalated=25
p2 band1 UNSUPPORTED_TABLE verdict=asserted tokens_asserted=741 tokens_escalated=25
report totals: asserted=2152 escalated=77
```

Every non-asserted region is `verdict='ignored'` (`NON_TABLE`), so **zero `CandidateConcept`s** — but
3.45% of the table ink did not cross. `CompilationReport.asserted/escalated` are *token* counts
(`compile.py:367-368`), and a partially-read band books escalated tokens **without minting a
candidate**.

So §4.4's gloss — *"the interior conforms, but not everything that reached the boundary crossed it"* —
is **false as stated for `Intact`**. This is not a reason to change the discriminator (candidate
nodes are the right membrane-scoped population), but it is a reason to change the **words**: §4.4's
prose and, more importantly, §4.6's amended `rdfs:comment` — a *published* surface — must say **held
propositions**, not *everything that reached the boundary*, or `Intact` will be read as "fully read"
when it means "nothing is held at the membrane." **`score` and `membraneHealth` are two different
signals and the loop must say so.** Folds into B3's amendment set.

## The three targets, answered

**1. Is §4.2's verdict fact PROCEDURAL raw extraction, or a stored label?** *Both, and the spec is
half right.* The **classification** is correct — an engine verdict is not derivable from the evidence
graph, which is what PROCEDURAL is reserved for. The **subject** is wrong: as written it is a claim
about the current state of a mutable graph, stored inside that graph, which is what "stored label"
means. O5 does not answer this (it tests re-derivability of the health triple, not the staleness of
the verdict fact). Fix it by recording the validation **act** rather than the graph's status — see B2.
Independently, the node as specified is **malformed SHACL** on the `false` path.

**2. Should the loop wire a proposer so §5.6's clause is exercised on real input?** *Neither of the two
options the handoff offered.* It should not wire a new proposer (scope creep), and it should not
settle for a hand-built graph — **a fixture+proposer vehicle already exists and produces
`promoted=2, held=0` at document scope in 2.6 s** (P1). Use it for O3. Then register the narrowed
residual — *unexercised on the corpus sweep* — in the vacuity registry that already owns this exact
question, rather than in prose.

**3. `MembraneRefusal` — re-run the catcher census.** *Done, and widened.* The design is safe: no
`except AssertionError` outside `test_corpus.py:129` (which re-raises), no bare `except`, no
`BaseException`, no `suppress`, and none of the six uncounted `pytest.raises(AssertionError)` sites
wraps a compile. Two corrections, neither fatal: drop "Exhaustively" (P2), and note that
`test_concept_feed.py:349` catches the grounding-leg raise §9 scopes out. **The real risk at this seam
is not the census — it is B4:** there is no existing way to *produce* the refusal that
`MembraneRefusal` is meant to carry.

---

## What must happen before a plan is written

1. **Rule on B1** — which class the compile-scope document URI gets. Everything else in §4 depends on it.
2. **Rule on B2** — `sh:ValidationReport` as specified, or an owned activity node.
3. **Rule on B3** — carry the semantic amendment fully (five artifacts, including the criterion's own
   `prog:statement`), or scope `Weakened` out.
4. **Add B4 to §10 as a named seam**, with the fact to measure, not the answer.
5. **State B5's asymmetry** in §4.5/§9 and raise it as a residue.
6. **Rewrite §5.6's consequence and O3** per P1; decide whether the registry extension is in scope.
7. **Pin the verdict datatype and make the query refuse to guess** (B6) — the only finding here that
   fails *upward*, and the one a plan is least likely to catch on its own.
8. **Rule on B7** — the shared `_DOC` constant means the health subject is the same IRI for every
   document and carries no other statement. At minimum restate §4.3's site constraint with the
   collision as its reason; decide whether `etkl:membraneHealth` gets `owl:FunctionalProperty` /
   `sh:maxCount 1`, and whether the subject is linked to anything.
9. **Reword §4.4 and §4.6 per B8** before the amended `rdfs:comment` ships to a published surface.
10. **Fix the five bookkeeping errors**, especially §2.7's "20 of 45" — the plan will otherwise author
   a `.rq` header against a convention that does not exist.

**Not blocking, and explicitly ruled so:** the spec is 519 lines against 379 lines of evidence, only
17 of them fenced, and it cites `§2.x` rather than re-deriving — **rule 6 compliant.** No function
body appears in it. Its §9 and §10 are the two best-executed sections in the document and should be
preserved through the revision.
