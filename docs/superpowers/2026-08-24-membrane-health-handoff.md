# Handoff — next loop is `holon:05`, membrane health; and rule 6 has landed

**Topic:** process · **Date:** 2026-08-24 · **`main` @ `be41973`** (merge of PR #114,
`the-worktree-that-resolves`) · **Shape: mechanical** — written at 85k as a pointer document.
The direction below was CHOSEN by the maintainer this session; the spec is NOT written and must
not be written from this file's context (originating floor 50k, crossed at 71k; logged `stop`).

## Goal

Give a compiled document a **membrane-health signal** — `etkl:membraneHealth` →
`etkl:Intact` / `etkl:Weakened` / `etkl:Compromised` — computed from validation results, closing
arc criterion `holon:05` and moving the `holon` rung 4/6 → 5/6. `holon:06` (the full
Raw → portal → Clean traversal example) is the follow-on, not this loop.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `tests/arc-manifest.ttl` → `prog:criterion:holon:05` | the criterion, its `prog:source` (`docs/holonic-interaction.md:160-161`), and its **pre-declared oracle** `tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health` — a target that **does not exist yet** (`ls` confirms). The criterion also carries a `prog:proposedDependsOn holon:01` whose rationale records why it cannot ground: *"fails A1 (holon:05 is unmet — there is no green oracle to turn red)"* |
| `vocab/ontology/etkl-holons.ttl:74-88` | the whole vocabulary already exists: `etkl:MembraneHealth`, the three individuals, and `etkl:membraneHealth` (domain `etkl:DocumentHolon`, range `etkl:MembraneHealth`). **Nothing new needs minting for the states themselves** |
| `src/iladub/etkl/membrane.py:45` | `validate(data, shapes, ont, engine=None) -> tuple[bool, str]` — the seam. Read its docstring in full before designing: it states the two-engine parity contract and warns *"Callers must not depend on the report's exact wording"* |
| `src/iladub/etkl/compile.py:504` | `_validate(graph, legs=("tab","dec")) -> (bool, str, refusing_legs)` — the call site that already runs both legs and returns leg identity (R104's shape). This is where a health signal would be derived from, and I-E's note at `:519` is relevant: the conforming path already **discards** the dec leg's report |
| `docs/holonic-interaction.md:66,84,160-163` | the design intent — *"whose membrane-health is its cleanliness"* — and the two remaining bullets (holon:05, holon:06) written as the open items |
| `CLAUDE.md` § Plan authoring discipline, rule 6 | **added this session**; see below |

## What was decided, and where each decision is recorded

- **Direction: `holon:05`, sliced to one criterion** (maintainer, 2026-08-24; recorded **here and
  nowhere else** — reversible). Weighed against R123+R125+R124 (the one-file ablator loop) and
  R113 (line-granularity ablation). R113 was set aside for a measured reason on its own row: it is
  blocked on **R109** (the `<path>:<line>` parser that does not exist) *and* on an unanswered
  design question (what a partially-excised Turtle should do). R123's own row rules it **latent,
  not live** — neither `tab:06` nor `tab:10` is an endpoint of any of the 6 asserted edges, and it
  raises loudly rather than admitting silently. Both stay on the menu behind this loop.
- **Rule 6 is IN `CLAUDE.md`** (maintainer request, 2026-08-24; recorded in the Contract itself,
  § Plan authoring discipline): *state each invariant once; a plan that argues the same point in
  three places is a spec that was not finished.* Its measurement is inline (1212 vs 368 lines,
  310 fenced ⇒ **902 prose**, re-run before writing, which is what refutes the on-record defence
  *"the bulk is transcripts plus verbatim tests"*). The rule explicitly carries what it is **not**:
  the ratio was ruled not a rule-1 violation and not a merge blocker, **there is no line budget**,
  and rule 6 is a **spec** finding whose fix goes upstream. `tests/test_doc_governance.py` green
  (4 passed) after the edit.
- **Adversarial review is REQUIRED for this loop's spec** (maintainer, 2026-08-24; recorded here).
  It has never run as a named step, and PF-4 plus Task 4's two findings in the last loop all came
  from that class of reading. Attack the premises *before* any plan: measure every load-bearing
  claim, and check each plan-supplied test's **setup** can actually be constructed (rule 5).

## The two measurements that should shape the spec — made this session, re-verify them

Both were measured here, not read, and both are the kind of premise an adversarial review exists
to attack. **Re-run them; do not carry them as fact.**

1. **`etkl:Weakened` is UNREACHABLE today, and that is this loop's central problem.** Its
   definition at `etkl-holons.ttl:81` is *"Interior conforms but warnings are present."* But:

   ```
   $ grep -rn "sh:severity" vocab/ tests/*.ttl | wc -l
   0
   ```

   No shape anywhere declares a severity, and SHACL's default is `sh:Violation` — so every result
   this repo can produce is a Violation, and the conforms/violates split is **binary**. Shipping
   `holon:05` with a three-valued property whose middle value can never be minted is **exactly the
   R106 class** (a `met true` criterion citing evidence with zero focus nodes for what it claims).
   The spec must decide this deliberately and say so: either give `Weakened` a real derivation
   (which means some shape must declare a non-Violation severity, and *which* is a semantic
   decision, not a tuning one), or scope the loop to the two reachable states and record the third
   as a named residue. **Do not let it ship as a state nothing can produce.**

2. **The seam does not currently return what a health derivation needs.**
   `membrane.validate` returns `(bool, str)` — conforms plus report **text** (`membrane.py:46,108`)
   — and its own docstring forbids callers depending on the wording, because the two engines word
   it differently. A severity-aware health signal needs the validation **report graph**
   (`sh:resultSeverity`), not its text. Whether to widen that return, or obtain the graph another
   way, is a design decision with a parity consequence across both engines — name it in the spec
   before designing, and check it against § Producer-side guards vs the membrane.

## Unverified or assumed

- **The `holon:05` → `holon:01` dependency is `proposedDependsOn`, not asserted**, and its own
  rationale says why. Once `holon:05` has a green oracle, that edge becomes ablatable for the first
  time — **but I did not check whether the A6 artifact-file-disjointness arm would admit it**, and
  a loop that closes `holon:05` may be able to promote the proposed edge as a second product. Treat
  that as an opportunity to measure, not a plan.
- **Whether `etkl:membraneHealth`'s domain (`etkl:DocumentHolon`) is actually minted by the compile
  path** was not checked. If compiled output carries no `etkl:DocumentHolon` subject, the property
  has nothing to attach to and that is a larger loop than this handoff assumes. **Measure this
  first** — it is the cheapest thing that could invalidate the whole slice.
- **No test was run this session beyond `tests/test_doc_governance.py`** (4 passed). The full suite
  was last green at the PR #114 merge; `main` has moved by exactly this session's CLAUDE.md edit.
- **The register is 24 closed / 91 open**, verified with the register's own `awk` command, and the
  cockpit reads `▼0.2 │ 7d: 21 raised, 4 closed`. This loop adds capability rather than repaying
  debt, which continues that trend deliberately — the R123 bundle is the loop that reverses it, and
  choosing this one is choosing the rung over the ratio.

## The next concrete action

In a **fresh session, in its first third**: measure the `etkl:DocumentHolon` question in
§ Unverified first (it can invalidate the slice for a few hundred tokens), then write the spec for
`holon:05` — what disposes the health states, whether `Weakened` is in scope or a named residue,
where the derivation lives under the neurosymbolic gate (a health signal derived from a validation
report is an **AXIOM over an RDF evidence graph**, not Python), and the falsifying oracle. Then run
the adversarial review on that spec **before** any plan is written.
