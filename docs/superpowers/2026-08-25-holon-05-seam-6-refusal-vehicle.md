# Seam 6 measured — the refusal vehicle (`holon:05`)

**Date:** 2026-08-25 · **Answers:** §10 seam 6 of
`docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md` · **`main` @ `538f1e6`**
(merge of PR #120) · **Shape: mechanical** — this file records measurements. It authors no design and
rules on nothing; the ruling it asks for is named at the end.

## The question, verbatim from the spec

> *What is the smallest real graph mutation that makes the document leg refuse at
> `document.py:1624`, and is it reachable without `validate_shapes=False`?*

Measured **before** the plan, because it is the one unknown that can invalidate two oracles (O2's
`Compromised` leg, O7). Three routes were run in parallel by three subagents; the findings and this
file are the controller's. Every run used `validate_shapes=True` and **no monkeypatch of
`membrane.validate` or `compile._validate`** — the R73 defect-5 trap the spec forbids.

---

## THE ANSWER

**The smallest real graph mutation is ONE added triple: a second `dec:rationale` on a decision holon
whose chosen option is labelled `escalated`.** It refuses the **`dec`** leg — which is unconditional
at document scope (R102) — via `dec:EventShape`'s `sh:maxCount 1` on `dec:condition`
(`dec-shapes.ttl:60-63`), after `escalation-furnish.rq` at `document.py:1609` carries the second
rationale into the `dec:ExpansionRequest`.

**It is provably document-only.** Measured both directions on an escalating fixture:

```
PAGE graph + extra rationale: _validate(legs=('tab','dec')) conforms=True  refusing=()
PAGE graph + extra rationale: _validate(legs=('dec',))      conforms=True  refusing=()
before re-furnish: dec:condition count on the request = 1
after  re-furnish: dec:condition count on the request = 2
DOC graph + extra rationale + furnish: _validate(legs=('dec',)) conforms=False refusing=('dec',)
    ['sh:resultMessage "An event must declare exactly one condition." ;']
```

**One added triple, page-scope-invisible, document-scope-fatal.**

**And it is NOT reachable without `validate_shapes=False` — not today.** `BandRecorder.record`
(`decisionlog.py:50-56`) writes exactly **one** `dec:rationale` per minted node, and the four
decision-URI namespaces are disjoint by construction (`page_doc_uri(p)` at `document.py:1277`,
`{…}/r2` at `:1336`, `{…}/adopt` at `:1473`, `{grid_uri}-admission` at `:1560`). Census over two
documents:

```
escalating-fixture: DecisionHolons=17  rationale-count histogram={1: 17}
graincorp-capacity: DecisionHolons=18  rationale-count histogram={1: 18}
```

**No exceptions.** So the lever exists, the membrane reacts to it correctly, and **no compile can pull
it.** What stops it is URI discipline in the recorder, not the membrane.

---

## Route 1 — the existing mutation catalogue: DEAD on structure

`tests/etkl/test_membrane_equiv.py:115-145`'s four `_mutations`, applied to real graphs at both scopes
(`simple_table_pdf`, 0.96 s page / 0.85 s document):

```
PAGE-graph  [drop-onPage / blank-cellText / drop-bbox / orphan-unit-marker] conforms=False refusing=('tab',)
DOC-graph   [same four]  tab+dec conforms=False refusing=('tab',)  |  dec-only conforms=True refusing=()
```

**All four are pure TAB-leg violations.** Two consequences, either fatal:

1. A real graph carrying such a defect refuses at the **page** gate (`compile.py:1170-1173`) first, so
   `document.py:1624` is never reached.
2. At document scope the tab leg runs only when `recognized or section_facts`
   (`_legs_for_document`, `document.py:1162`). None of the four refuses `dec`-only — so on a document
   whose legs are `("dec",)` these mutations pass the document gate **entirely**.

## Route 2 — a pathological source document: DEAD on measurement

Forcing `("tab","dec")` on the four documents whose real legs are `("dec",)` — i.e. asking whether the
leg-dropping is hiding a refusal:

| document | compile | triples | `_validate(dec)` | `_validate(tab,dec)` |
|---|---|---|---|---|
| `graincorp-capacity-2026-08-04` | 9.0 s | 5,705 | conforms=True | **conforms=True** |
| `ons-index-of-services-2026-02` | 7.8 s | 11,076 | conforms=True | **conforms=True** |
| `bfs-population-bilan-2023` | 22.7 s | 8,244 | conforms=True | **conforms=True** |
| `who-wfa-boys-zscore-0-5` | 36.4 s | 8,098 | conforms=True | **conforms=True** |

**4 of 4 conform under the forced tab leg.** The tab gate is not hiding a refusal on any of them.
(apple, cbh-stem, graincorp-stem were not run — too expensive; **stated rather than guessed.**)

## Route 3 — the proposer route: DEAD, and it confirms B5 from a second direction

The hypothesis was that a malformed proposer — proposers being *public parameters* of
`compile_document` — could drive a non-conforming promotion into the document graph. **A malformed
proposal does produce a real refusal**, with no monkeypatch:

```
RowRoleProposal(("furniture","continuation"), confidence=1.5, …) on caption_wrap_report_pdf
  RAISED AssertionError.  RAISE SITE: src/iladub/etkl/compile.py:1173  in compile_tables
  AssertionError: asserted holon failed dec: SHACL:
    sh:resultMessage "A candidate must carry a confidence in [0,1]." … sh:value 1.5
  (4 violations; a NaN variant gives 12)
```

**But it lands at `compile.py:1173` — page scope — every time.** Two independent structural blockers,
both measured:

1. **A promotion always implies a table type on that page.** Every promotion emitter runs only after
   an `assert_*_region` that types the page graph `tab:HierarchicalTable`/`tab:RecordTable`
   (`holon.py:108,162,222,325,497`) — which is *exactly* the page gate's guard
   (`compile.py:1167-1170`). The bad promotion therefore always meets the page membrane first.
2. **`validate_shapes` cannot be split between scopes.** All three `compile_tables` call sites pass it
   verbatim (`document.py:1274,1337,1474`). There is no public way to ask for the document membrane
   while suppressing the page one.

Also measured: the option space **cannot** be starved by a proposer — `_deliberate` (`promote.py:33`)
builds `dec:optionSpace`/`dec:chosen` from the code's own enumeration, so the
`dec:DecisionHolonShape` violation `test_compile_membrane_shapes.py:123` uses is unreachable from any
input. And `certify_with_proposals` (`reshape.py:199`) has **zero call sites in `src/`**, so the
reshape emitter is not reachable from `compile_document` at all.

## What IS document-only, and what constrains it

The genuinely document-only vocabulary, measured by spying on every `compile_tables` call the driver
makes (pass 1, `/r2` repair, `/adopt`) and diffing — **not** by the naive doc-vs-independent-pages
diff, which overcounts badly because section repair asserts through a second page-scope compile:

| document-only fact | constrained by |
|---|---|
| `tab:inLogicalColumn` | `tab:InLogicalColumnDisciplineShape`, `tab-shapes.ttl:410-421` |
| `tab:continuesColumn` | `tab:ContinuesColumnDisciplineShape`, `tab-shapes.ttl:366-378` |
| `tab:licenceRefused` | `tab:LicenceRefusalShape`, `tab-shapes.ttl:384-395` (idle on all fixtures) |
| `tab:SectionTotal` / `tab:confirmsSection` | `tab:SectionTotalShape`, `tab-shapes.ttl:323-326` |
| the `escalation-furnish.rq` output | `dec:EventShape` / `dec:ExpansionRequestShape`, `dec-shapes.ttl:60-74`; `dec:EscalationShape`, `escalation-shapes.ttl:16-33` |
| **`dec:supersedes`** | **NOTHING** — `git grep -n "supersedes" -- vocab/shapes/` → exit 1 |
| `tab:continuesTable` | nothing targets its subjects; it appears only as a precondition inside the two shapes above |

`git grep -n "sh:closed" -- vocab/` → **exit 1**, so no document-only fact can refuse merely by being
an unexpected predicate.

The four tab-side levers are all gated off precisely when they would matter, by the same
`_legs_for_document` condition as Route 1. **The escalation-furnish surface is the only one behind the
unconditional `dec` leg**, which is why it is the answer.

---

## Three findings that are defects, not test gaps

These were not what the seam asked for. They came out of asking it, and each is a candidate row for
the spec's §11 list (which currently runs to five; **the next register number is R127**).

**6. `dec:rationale` has no cardinality constraint, and CLAUDE.md permits a second one.**
`escalation-furnish.rq` binds `?req dec:condition ?why` from `?d dec:rationale ?why`, and
`dec:EventShape` caps `dec:condition` at 1 — but **nothing anywhere caps `dec:rationale`**. CLAUDE.md
§ Serialization says *"rationale/label literals may be language-tagged (de/fr/it)"* and forbids
constraining such properties to `xsd:string`. **So the day any escalating decision carries a
language-tagged rationale pair, every document containing it refuses at document scope**, with a
message about `dec:condition` that names neither `dec:rationale` nor the language tag. This is a
latent conflict between a stated project principle and a shape, found by two agents independently.
*Closes when:* the furnish query collapses multiple rationales, or `dec:rationale` is capped, or
`dec:EventShape` admits one condition per language.

**7. `dec:supersedes` is constrained by nothing.** It is document-only, it is load-bearing for
withdrawal, section repair and adoption — and `git grep -n "supersedes" -- vocab/shapes/` returns no
rows. A malformed supersession cannot refuse at any membrane.

**8. A non-IRI `suggester_iri` crashes the membrane rather than refusing.** A proposer returning
`suggester_iri="not an iri at all"` dies at `membrane.py:348` with a raw
`Exception: … does not look like a valid URI, I cannot serialize this as N3/Turtle` — not an
`AssertionError`, so it is neither a membrane verdict nor catchable as one.

---

## What this means for the plan — and the ruling it needs

**O7 is fine.** It needs a `MembraneRefusal` carrying a graph, and the mutation above produces a real
document-scope refusal once applied to a compiled graph. The open question is only *where* the test
applies it.

**O2's third leg is NOT fine, and the spec cannot resolve this by itself.** §7 O2 says, in terms:

> *"`Compromised` from a forced non-conforming graph at the real raise site … **If a value cannot be
> produced from real input, this test fails and says which — it does not fall back to a fixture.**"*

**Measured: `Compromised` cannot be produced from real input.** No PDF, no proposer, and no public
parameter of `compile_document` reaches the document gate ahead of the page gate. O2 as written
therefore fails, by design, and that is the spec working correctly rather than a defect in it — but
**the plan must not silently weaken O2 to make it pass.** That is the exact failure CLAUDE.md rule 1
records: *"a plan-supplied test is a proposition, and an implementer who cannot make it pass has found
a plan defect… never weaken the assertion to make a broken contract go green."*

**The ruling needed, before the plan is written** (options, with what each costs — this file
deliberately does not choose):

| | option | cost |
|---|---|---|
| (a) | **Apply the mutation to a compiled graph, then re-enter the document gate.** Needs a seam that does not exist on `compile_document` | new public surface on the compiler, in a loop that already mints three terms and a shape |
| (b) | **Fix finding 6 first** (cap `dec:rationale`, or collapse in the furnish), then the lever is gone and `Compromised` needs a different one | fixes a real latent defect, but forecloses the only measured route and grows the loop |
| (c) | **Split O2**: `Intact`/`Weakened` on real input as specified; `Compromised` on a fixture, with the impossibility recorded as a named residue and the spec's O2 wording amended to say so | honest and cheap, but it is an amendment to the spec's own standard and must be written as one, not slipped in |
| (d) | **Scope `Compromised` out of this loop** entirely | ships a three-valued property with one unmintable value — the R106 class the loop exists to avoid |

**Nothing here should be read as a recommendation.** The measurement's job was to make the choice
visible before the plan was written, and it has.
