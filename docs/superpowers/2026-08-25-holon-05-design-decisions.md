# Handoff — `holon:05` design decided, spec NOT written

**Topic:** process · **Date:** 2026-08-25 · **`main` @ `e162ce0`** (merge of PR #115,
`membrane-health-handoff`) · **Shape: originating, stopped at 90,666 tokens** — 1.8× the 50k
floor, logged `stop`. This session did the brainstorming and the measurement; it did **not**
write the spec, and the spec must not be written from this file's context.

**Supersedes `docs/superpowers/2026-08-24-membrane-health-handoff.md` as the standing pointer.**
That file's measurements were re-verified here (see § Re-verification) — read this one first, and
open that one only for the `holon:05` vs R123/R113 direction rationale, which is not repeated here.

## Goal

Unchanged from the 2026-08-24 handoff: give a compiled document an `etkl:membraneHealth` signal,
closing arc criterion `holon:05` and moving the `holon` rung 4/6 → 5/6. What changed this session
is that the two forks it left open are now **decided**, and a **third vacuity hazard** was measured
that neither the handoff nor the arc manifest had.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `tests/arc-manifest.ttl:352-359` | the criterion. `prog:oracleTest` is the exact string `tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health` — a **target that does not exist** (`ls` re-confirmed 2026-08-25). It carries **no `prog:oracleArtifact`**. The `prog:proposedDependsOn holon:01` edge and its rationale are at `:1332-1337` |
| `vocab/ontology/etkl-holons.ttl:42-44` | `etkl:DocumentHolon` is declared **abstract** *in its own `rdfs:comment`* — "Abstract parent of the raw and clean document holons." This is what closes the cheap escape of typing the doc URI as the property's declared domain class |
| `vocab/ontology/etkl-holons.ttl:62-64, 75-88` | `etkl:CleanDocumentHolon` (concrete; its comment already says *"Its cleanliness is its membrane health"*), the three `etkl:MembraneHealth` individuals, and `etkl:membraneHealth` with `rdfs:domain etkl:DocumentHolon` |
| `src/iladub/etkl/compile.py:1167-1175` | the page-scope raise site **and** the skip guard: validation runs only if the graph holds a `tab:RecordTable` or `tab:HierarchicalTable` |
| `src/iladub/etkl/document.py:1624-1626` | the document-scope raise site |
| `src/iladub/etkl/membrane.py:45-46, 104-108, 122-126, 167-174` | the seam's public `(bool, str)` return, **and** the two places a report graph is already built and discarded |
| `src/iladub/etkl/holon.py:424-472` | `escalate_region` — where a held-at-the-membrane proposition is minted, and where the doc URI appears as an **object** (`prov:wasDerivedFrom`) |
| `vocab/queries/*.rq` | 20+ siblings; the established home for an AXIOM |
| `docs/holonic-interaction.md:55-95` | the design intent, including the mermaid's dotted *"held at the membrane"* edge that the chosen `Weakened` derivation reads literally |

## What was decided, and where each decision is recorded

Both of the following were **chosen by the maintainer on 2026-08-25**, in conversation, and are
recorded **here and nowhere else** — so both are reversible, and the spec should re-state them as
its own decisions rather than cite this file as authority.

1. **The subject: mint `etkl:CleanDocumentHolon`, and only that.** The document URI is typed as
   the concrete class, so the health triple sits inside `etkl:membraneHealth`'s declared domain
   with no exception to justify. **Not** the Raw holon, **not** the portal — those are `holon:06`,
   and this decision deliberately does not touch them.
2. **`etkl:Weakened` is derived from propositions held at the membrane**, not from SHACL
   severities: the interior conforms, but unpromoted `iladub:CandidateConcept`s remain. This
   requires amending `Weakened`'s `rdfs:comment` (`etkl-holons.ttl:81`) away from *"warnings are
   present"* — vocabulary we own, but a **published** change, so it belongs in the spec's Doc
   impact block.

   **The cost of the rejected alternative was quoted too high, and the maintainer was told so
   after choosing.** The severity route was presented as needing `membrane.validate` widened to
   expose a report graph; measurement (below) shows both engine legs already build one. If the
   spec author wants to re-open this, that is the reason to.

3. **`Compromised` is minted at the raise site.** The maintainer chose this over scoping
   `Compromised` out as a named residue, when both were put with their costs (2026-08-25,
   recorded **here and nowhere else**). The producer-side guard **stays** — the raise is not
   softened, not downgraded, not made conditional. The health triples are minted into the graph
   *before* the raise, and the error carries that graph.

   The R89 test is satisfied for a reason worth restating once in the spec and then citing:
   § Producer-side guards vs the membrane licenses deleting a guard only when the membrane
   provably validates **every** product of that producer — and here it demonstrably cannot, because
   a refusing product never becomes a returned `CompilationReport` at all. So this is the opposite
   of the R102 pattern: not a guard that looks redundant, but a guard that is the *only* thing
   standing between a non-conforming graph and its caller.

   **The seam this creates, which the spec must state and the plan must measure:** what the error
   carries is now part of an interface. `tests/test_corpus.py:129` is the only catcher in the tree
   and it re-raises — but "only catcher today" is exactly the claim
   `enumerating-before-claiming` exists to make you re-measure before you build on it.

Sections 1–3 above are settled. **Nothing else in § The design as it stood is approved** — it is
one session's proposal, and the adversarial review has still never run.

## The third vacuity hazard — MEASURED 2026-08-25, and it is the finding this session adds

The 2026-08-24 handoff names two vacuity hazards (unreachable `Weakened`, uninstantiated domain).
There is a **third**, and it is the sharpest, because it makes the *most severe* state the
unreachable one:

```
$ grep -rn "_refusal_message" src/iladub/etkl/
  compile.py:1171-1173    conforms, text, legs = _validate(graph)
                          if not conforms: raise AssertionError(_refusal_message(...))
  document.py:1624-1626   same shape at document scope
$ grep -rn "except AssertionError" src/ tests/
  tests/test_corpus.py:129        # and it re-raises
```

**A refusing membrane raises. No `CompilationReport` for a non-conforming document is ever
returned.** So `etkl:Compromised` cannot attach to any graph a caller can hold — the same R106
class as the other two, in the majority value. A health signal derived only from what compile
returns would be constant `Intact`/`Weakened` by construction.

**A fourth, weaker one, in the same family:** `compile.py:1167-1170` skips validation entirely for
a page with no `tab:RecordTable`/`tab:HierarchicalTable`. Reporting such a document `Intact` claims
conformance from zero focus nodes.

## The design as it stood when the session stopped (NOT approved)

Sections 1–4 follow from the two decisions above. Sections 5–6 are this session's proposal for the
third hazard, and **section 5 is the one the maintainer was asked about and did not answer.**

1. **Scope** — `holon:05` only; the pre-declared oracle string above turned red-then-green.
2. **Subject** — decision 1. Document scope only; page scope (`{_DOC}/p{n}`) gets no health, so
   the document's signal is unambiguous.
3. **Derivation** — an AXIOM in `vocab/queries/membrane-health.rq`, `CONSTRUCT` over the compiled
   evidence graph.
4. **Reachability rule** — mint health **only where the membrane actually ran**; absence of the
   triple, never a fourth state. This is the gate's open-world rule (derive only from support that
   is present), applied to the skip guard.
5. **`Compromised`** — **DECIDED**, see decision 3 above. Mint at the raise site; the guard stays.
6. **Falsifying oracle** — strip the health triple, re-run the `.rq`, assert byte-identical
   re-derivation. This is also the answer to the stored-label objection: a materialized projection
   whose derivation is re-runnable is not a label. Plus one forced non-conforming graph for
   `Compromised` and one corpus document with escalations for `Weakened`.

## The seam the plan must MEASURE, not assume

`iladub:status` has exactly two values repo-wide — `proposed` and `asserted` (`ground.py:102,178`,
`holon.py:461`, `splitkey.py:137,195`, pinned by `iladub-shapes.ttl:29,43`). **But `promote.py:74,
121,165` also writes `status proposed` on candidates it then promotes**, so *"unpromoted"* is
**not** expressible as `status proposed` alone. Which discriminator actually separates held
candidates from promoted ones is a measurement to run **before** writing the query — the gate
permits a holon-scoped `NOT EXISTS` here ("query-local `NOT EXISTS` closes *within* the one holon"),
but which pattern it closes over is unmeasured as of this handoff.

## Re-verification of the 2026-08-24 handoff (delegated; run live, repo venv, not bare `python3`)

CONFIRMED as stated: 326 triples from both `compile_tables(pdf,0)` and `compile_document(pdf)`,
score 1.0; **0** triples with the doc URI as subject at either scope (56 of 69 subjects start with
it); 11 distinct `rdf:type` values, `dec:` 34 / `tab:` 34 / `prov:` 1 and **zero** in `etkl:`; zero
`a etkl:<fabric class>` instance triples in the tracked tree; `sh:severity` 0 in `vocab/` and
`tests/*.ttl`, and `sh:severity`/`sh:Warning`/`sh:Info`/`resultSeverity` 0 repo-wide outside prose.

**PARTIALLY REFUTED — handoff claim #2.** *"The seam does not currently return what a health
derivation needs"* is true of the **public return** (`membrane.py:46,108` → `(bool, str)`) but not
of availability: pySHACL's `validate` returns a 3-tuple whose middle element **is** the
`sh:ValidationReport` graph and the code discards it into `_` (`membrane.py:124`), and the rudof leg
**already parses** its Turtle report into an rdflib `Graph` to read `sh:conforms`
(`membrane.py:170`) and discards that. A report graph is available on both legs without an engine
rewrite. The genuine design point is that `_deskolemize` (`membrane.py:297-315`) operates on the
report **string**, so a graph-returning path must decide where de-skolemization happens.

Two additional facts not in the 2026-08-24 handoff: the **page-scoped** stem `…/doc/p0` is also
0-as-subject; and `etkl:` does appear as a *subject* in compiled graphs (`etkl:reader`, a
`prov:SoftwareAgent`) — it is `etkl:` as an `rdf:type` **object** that is absent.

## Unverified or assumed

- **Sections 4 and 6 of § The design as it stood are a proposal, not an approved design** —
  only decisions 1–3 are settled. In particular the falsifying oracle (section 6) has been
  argued but never attacked, and it is the piece the adversarial review should hit first after
  the three measurements below.
- **No test was run this session.** Not `pytest`, not `tests/test_doc_governance.py`. The full
  suite was last green at the PR #114 merge; `main` has since taken the PR #115 merge and this
  file. **Run the suite before designing against any behaviour here.**
- **The `_deskolemize`-on-a-graph question is unanalysed.** It is named above because it was
  measured to exist, not because anyone worked out what it costs.
- **Whether typing the doc URI as `etkl:CleanDocumentHolon` trips a membrane shape is unmeasured.**
  If any shape is `sh:closed` or targets by class in a way a newly-typed subject reaches, minting
  the node could change existing verdicts. This is the first thing to measure in the spec, because
  it is the one way decision 1 could fail outright.
- **Whether the `holon:05 → holon:01` proposed edge becomes promotable** once `holon:05` has a
  green oracle — carried forward unexamined from the 2026-08-24 handoff, where it was already
  flagged as an opportunity to measure rather than a plan.
- **The register tally was not re-counted this session.** The 2026-08-24 figure was 24 closed /
  91 open; treat it as stale and re-run the register's own `awk`.

## The next concrete action

Nothing is blocked on the maintainer. In a **fresh session, in its first third**: write the spec
for `holon:05` against decisions 1–3, then run the **adversarial review on it before any plan** —
a standing requirement since the 2026-08-24 handoff, still never run as a named step.

Run the suite first (nothing was run here), then take the review's three named targets in this
order, because each can invalidate the design rather than merely refine it:

1. **the `sh:closed` question** — can decision 1 mint `etkl:CleanDocumentHolon` without changing an
   existing verdict? This is the only measurement that can kill the chosen subject outright.
2. **the `promote.py` discriminator** — what actually separates held candidates from promoted ones,
   given both carry `status proposed`? Decision 2's query cannot be written until this is measured.
3. **the falsifying oracle** — strip-and-re-derive was argued, never attacked.
