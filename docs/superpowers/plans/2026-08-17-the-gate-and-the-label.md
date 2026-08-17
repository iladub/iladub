# Plan — the gate and the label (Loop 1 of the R97–R104 split)

**Spec:** [`../specs/2026-08-17-the-gate-and-the-label-design.md`](../specs/2026-08-17-the-gate-and-the-label-design.md)
· **Tree:** `main` @ `d3ba25a`, clean · **Rows:** R102, R104 close · R89 amends · R103 carries

**Doc impact: increment.** Two, both from spec §6: R89's rule into CLAUDE.md (a Contract edit, and
the maintainer's explicit request of 2026-08-17), and one wiki line — **if** a wiki page states the
membrane gate, which Task 3 measures rather than assumes.

**This plan states interfaces, invariants and oracles. It contains no function bodies.** Tests are
given verbatim only where this plan has verified the setup is constructible; where it has not, it
names the seam and states the assertion required. Every task report carries a `## FALSIFICATION`
block (CLAUDE.md plan rule 4) — **no falsification evidence ⇒ the task review fails.**

**Suite command, measured:** `.github/workflows/ci.yml:26` is `pytest -q`. Use it for the full run.

---

## Global constraints

- **Neurosymbolic gate (CLAUDE.md §8).** Spec §5 classifies every change in this loop. Two new
  helpers appear below (Task 1's message formatter, Task 2's leg selector); **neither adds a
  decision** — each names a predicate or a format string that already exists inline. Both are
  PROCEDURAL and each must say so in a docstring. **No tuned constant or tolerance anywhere.** If
  you find yourself writing one, stop and escalate.
- **Spec §7 is the scope fence.** Reconcile every test you write against it before committing
  (plan rule 5). In particular: nothing here emits RDF, the page gate is not ungated, the `tab`
  leg is not ungated, `BandRecorder.record`'s guards are not deleted, R103 does not close.
- **Source ownership.** No `.ttl` is authored or edited in this loop. No HGA term is touched.
- **Order is load-bearing.** Task 1 changes `_validate`'s signature; Task 2 changes the call site
  that reads it. Reversed, `document.py:1585` gets edited twice.

## Measurements this plan rests on

All taken at `e3f447a`/`d3ba25a` in the session that wrote the spec, and reproduced here with the
command that produced them. **Re-run the greps in Task 1 — do not trust these lines to still be
current after your own edits.**

`grep -rn '_validate' src tests scripts`, filtered to `compile._validate` (the `membrane._validate_pyshacl`
/ `_validate_rudof` / `feed._validate_grounding` hits are different functions):

```
src/iladub/etkl/compile.py:453:def _validate(graph: Graph) -> tuple[bool, str]:
src/iladub/etkl/compile.py:1101:        conforms, text = _validate(graph)
src/iladub/etkl/document.py:110:from .compile import CompilationReport, compile_tables, page_bands, _DOC, _validate
src/iladub/etkl/document.py:1585:        conforms, text = _validate(graph)
tests/etkl/test_compile_membrane_shapes.py:35:    compile_mod._validate(seed)             # force the lazy build
tests/etkl/test_compile_membrane_shapes.py:94:    conforms, report = compile_mod._validate(g)     # must not raise
tests/etkl/test_compile_membrane_shapes.py:122:    conforms, report = compile_mod._validate(_under_furnished_promotion())
tests/etkl/test_compile_membrane_shapes.py:143:    conforms, report = compile_mod._validate(g)
tests/etkl/test_membrane.py:92:    assert "membrane" in inspect.getsource(C._validate)
```

Read first-hand, `compile.py:453-465`: both legs run unconditionally
(`_TAB_SHAPES` at `:460`, `_DEC_SHAPES` at `:461`), `:463` returns `True, tab_report` when both
conform, `:464-465` joins the refusing legs' reports. The raise sites hardcode the label:
`compile.py:1103` `f"asserted holon failed tab: SHACL:\n{text}"`, `document.py:1587` the same for
`"document-level facts failed tab: SHACL"`.

`grep -n "_under_furnished_promotion" tests/etkl/test_compile_membrane_shapes.py` → `98` (def),
`122`, `132`. Its docstring at `:99-100` states it satisfies `iladub:PromotionDecisionShape` and
violates **only** `dec:DecisionHolonShape` — which is why Task 1's oracle setup exists already.

`grep -rn probe_emitter_typing` → documentation hits only; **no test and no CI job invokes it.**

---

## Task 1 — R104: carry the leg identity

### Interface

`compile._validate` becomes:

```
_validate(graph, legs=("tab", "dec")) -> tuple[bool, str, tuple[str, ...]]
```

Plus one new module-level helper in `compile.py` whose only job is the refusal message, so that
**I-D is testable without a PDF and without the corpus** (see § Why a helper, below):

```
_refusal_message(subject: str, legs: tuple[str, ...], text: str) -> str
```

`subject` is the caller's own noun — `"asserted holon"` at `compile.py:1103`, `"document-level
facts"` at `document.py:1587`. Preserve both nouns exactly; only the leg label changes.

### Invariants (spec §3.2)

- **I-A** — conforming ⇒ third element is `()`. Refusing ⇒ it lists exactly the refusing legs.
- **I-B** — every leg in `legs` runs, always, even after an earlier one refuses. This is the
  `:457-459` comment's argument and it must survive the change (spec §2.3).
- **I-C** — the default runs both legs; no existing caller changes behaviour.
- **I-D** — the raise message names exactly the legs in the third element and **no other leg**.
- **I-E** — the conforming path's returned text is unchanged (spec §3.2's `:463` ruling). Do not
  "fix" the discarded dec report; it is out of scope in writing.

### Why a helper rather than an end-to-end raise test

An end-to-end test of the raise message needs a compile that produces an under-furnished promotion
through a real PDF with the gate open. The corpus is **gitignored** (`.gitignore:44`), so such a
test would skip in CI — which is R101/D2's exact disease and would be a self-inflicted instance of
what Loop 3 exists to fix. The helper makes I-D a pure-function assertion that runs everywhere.

### Edits

1. `compile.py:453-465` — the signature, the leg selection, the third return element.
2. `compile.py:1101,1103` and `document.py:1585,1587` — unpack three, call `_refusal_message`.
3. `tests/etkl/test_compile_membrane_shapes.py:94,122,143` — three 2-tuple unpacks become three.

### Seams — MEASURE, do not assume

- **`document.py:110` binds `_validate` by name at import.** Any spy or monkeypatch on
  `compile._validate` alone does **not** reach the document call site. This matters in Task 2's
  measurement more than here, but check it before writing either.
- **`tests/etkl/test_membrane.py:92` pins `inspect.getsource(C._validate)`** and asserts
  `"membrane"` appears in it. Run that test after the signature change and report the result. If it
  goes red, the fix is the test's expectation, not the design — but say so explicitly rather than
  editing it silently.
- **`tests/etkl/test_compile_membrane_shapes.py:35` discards `_validate`'s return** (it only forces
  the lazy build). Confirm it needs no edit rather than assuming from this plan.

### Tests

**T1a — a dec-only refusal reports the dec leg and not the tab leg (oracle O4).** Setup verified
constructible: the helper at `:98` already builds exactly this graph and `:122` already drives it
through `_validate`. Supplied verbatim; add beside the existing `:122` test:

```python
def test_a_dec_leg_refusal_names_dec_and_not_tab():
    """O4. The message a diagnosing reader sees must send them to the vocabulary that actually
    refused. Asserting the ABSENCE of `tab` is the half that matters: a test checking only that
    `dec` is named passes when the message names both."""
    from iladub.etkl import compile as compile_mod
    conforms, report, legs = compile_mod._validate(_under_furnished_promotion())
    assert conforms is False, report
    assert legs == ("dec",), f"the refusing leg was mislabelled: {legs}"
    assert "tab" not in legs
```

**T1b — a both-legs refusal names both.** This is I-D's other direction, and the assertion the
label fix needs so it does not become a mislabel the other way. **Setup NOT verified by this plan.**
*Seam:* find or build a graph that `compile._validate` refuses on the **tab** leg —
`tests/etkl/test_closure_equiv.py:221` uses a `_bad_bbox_graph()` helper against
`membrane._validate_rudof`, which is **not** the same function; verify it also refuses through
`compile._validate` before reusing it. If no reusable helper exists, construct the minimal
violation and **name in the test's docstring which shape you made fail**. Required assertion:
`legs == ("tab", "dec")` for a graph violating both, and the message names both.

**T1c — the message names exactly the failing legs (I-D).** Pure function, trivially constructible.
Required assertions, for `_refusal_message("asserted holon", legs, "…")`:

| legs | message must contain | message must NOT contain |
| --- | --- | --- |
| `("dec",)` | `dec` | `tab` |
| `("tab",)` | `tab` | `dec` |
| `("tab", "dec")` | both | — |

Assert on the message, and keep `"asserted holon"` / `"document-level facts"` in the expectations so
a future refactor cannot quietly drop the subject noun.

**T1d — neither raise site hardcodes a leg name.** Structural pin, in the style of the existing
`test_membrane.py:92`: `inspect.getsource` of the two raising functions must not contain the literal
`"tab: SHACL"`. This is the regression guard; T1c is the behaviour.

### FALSIFICATION (required in the report)

Revert the leg parameter — make `_validate` return the old 2-tuple's label behaviour, or make
`_refusal_message` ignore `legs` and emit `"tab:"` — and show **T1a and T1c failing**. Restore, show
`pytest -q tests/etkl/` green, then `pytest -q` green.

**Report separately** whether `tests/etkl/test_membrane.py:92` passed unchanged.

---

## Task 2 — R102: ungate the `dec` leg at the document gate

### The decision, restated so it cannot drift

**The document gate (`document.py:1584`) only. The `dec` leg only.** The page gate
(`compile.py:1097-1100`) is untouched; the `tab` leg is ungated nowhere. Spec §2.2 carries the
coverage and redundancy arguments — do not re-derive them, and do not widen this.

### Interface

One new helper, in the module that owns the gate, whose only job is to name the legs the document
membrane runs:

```
_legs_for_document(recognized, section_facts) -> tuple[str, ...]
```

- **I-F** — `"dec"` ∈ the result for **every** input combination. This is the whole of R102.
- **I-G** — the result is `("tab", "dec")` **iff** `recognized or section_facts`, i.e. the existing
  tab condition is preserved bit-for-bit.
- **I-H** — the result is never empty, so the document membrane always runs at least one leg when
  `validate_shapes` is true. `validate_shapes` itself stays a separate, unchanged condition.

**§8 note for the docstring:** this helper introduces **no new decision** — it gives a name to the
predicate already inline at `:1584` and removes it for the `dec` leg. **The `tab` half's
classification is Loop 2's D8(a) and is NOT settled by naming it here.** Say that in the docstring
so the next reader does not mistake the helper for an adjudication.

### Seams — MEASURE before writing the call

1. **The spec §4.1 seam, reused verbatim and reviewer-confirmed:** *MEASURE which shape sets each
   gate actually guards at `compile.py:453-465` before writing the call.* `_validate` ran both sets
   under one condition before Task 1; confirm what Task 1 left, and confirm the gate-open path's
   combined report is unchanged (I-B). **The `:457-459` comment's argument must be answered, not
   bypassed** — spec §2.3 gives the answer this plan expects you to check, not accept.
2. **Does any *production* caller invoke `compile_tables` outside `compile_document`?** Spec §2.7.
   If one does, R102's close is narrower than it reads and a residue row must be raised for the
   page-scope residual. Record the answer **in R102's register row**, not only in the task report.
3. **Does `tests/etkl/test_vacuity_registry.py` stay green?** Reasoned unaffected (its focus-node
   counts are rdflib over the 7 final graphs, independent of `_validate` calls) but **not run** by
   this plan. If a registered-idle row goes live, the standing two-edit coupling applies: fix and
   row in the same change.

### Tests

**T2a — the dec leg is unconditional (oracle O3's CI-runnable half).** Corpus-free, pure function.
Supplied verbatim:

```python
import pytest

@pytest.mark.parametrize("recognized,section_facts", [(True, True), (True, False),
                                                      (False, True), (False, False)])
def test_the_dec_leg_is_never_gated_away(recognized, section_facts):
    """R102. 316 of 769 minted decision holons crossed no membrane because the dec leg rode the
    tab-fact condition. The promotion epistemics are not conditional on a document having tables."""
    from iladub.etkl.document import _legs_for_document
    assert "dec" in _legs_for_document(recognized, section_facts)


def test_the_tab_leg_keeps_its_condition_exactly():
    """I-G. Ungating dec must not also put the tab shapes onto graphs the gate excludes — the
    §4.1 seam's specific worry."""
    from iladub.etkl.document import _legs_for_document
    assert _legs_for_document(True, False) == ("tab", "dec")
    assert _legs_for_document(False, True) == ("tab", "dec")
    assert _legs_for_document(True, True) == ("tab", "dec")
    assert _legs_for_document(False, False) == ("dec",)
```

*Reconciled against spec §7:* it asserts nothing about the page gate, emits no RDF, and does not
touch the `tab` leg's classification.

**T2b — O3 proper, a LOCAL measurement and not a committed test.** The 316→0 count needs the
corpus, which is gitignored; committing it would make a skip that reports as health (R101's
disease). So it belongs in the task report, with the command that produced it:

- Method: spy **both** `_validate` references — `compile._validate` **and** the name
  `document.py:110` binds at import (I3). Take the union of decision holons any call saw, across all
  7 corpus documents, `validate_shapes=True`.
- **Required: 0.** **Falsification: re-gate the dec leg and reproduce 316.** Both numbers in the
  report, both from runs you performed.
- Also required: the **corpus suite wall-clock delta**, before and after. E2's dec-leg figures
  (0.6 s graincorp, 0.6 s bfs, 0.8 s ons ≈ **2.0 s**) are a standalone validate and are an estimate
  only. **Do not quote E2's "~4 s" — that is the both-legs figure.** If the delta is material, say
  so and raise a row. **Tune nothing** (R57 and R60 are the standing perf residues here).

### If the corpus goes red (spec §2.5)

At HEAD both legs conform on all three never-gated documents (E2), so this is not expected. If it
happens anyway: report the offending decision-holon URIs from the SHACL report and **stop for
adjudication.** Do **not** re-gate, weaken a shape, or add an exception — the new membrane has found
a real defect, which is the point of the change. **D16: the report must distinguish "the guard
failed" from "the compile raised."** They are different events and only one is a test result.

### FALSIFICATION (required in the report)

Re-gate the dec leg (restore the pre-fix condition for both legs) and show **T2a's `(False, False)`
case failing**. Restore, `pytest -q` green. Then the T2b pair: 316 with the gate, 0 without.

---

## Task 3 — the contract paragraph and the register pass

No code. No tests. Verification is the doc-governance suite plus the honesty of the rows.

### Edits

1. **CLAUDE.md** — add spec §6's paragraph verbatim as a short subsection immediately after
   § Core design principles' principle 8 block. It is a **Contract** document, edited here on the
   maintainer's explicit request of 2026-08-17 (recorded in the spec's §6 and in
   `2026-08-17-r97-r104-handoff.md:28-31`). **Do not add the scope note to CLAUDE.md** — spec §6
   puts it in the register.
2. **`docs/superpowers/residues.md:6`** — the preamble still says a closing loop *"deletes its row
   in the same change."* CLAUDE.md § Deferred residues reverses this. Fix it (E4).
3. **R100's row and `src/iladub/etkl/compile.py:408-409`** — both cite `compile.py:1083` for the
   page-scope call; at `d3ba25a` `:1083` is `if denom:` and the call is at `:1101`. Correct both.
4. **Strike R102 and R104** — `~~R102~~`, closure evidence recorded in place, **row NOT deleted**.
   R102's strike carries spec §2.6 (a gate change, not a composition question) and spec §2.7's
   scope boundary with seam 2's measured answer.
5. **Amend R89** — the rule is adopted and recorded; applying it to `BandRecorder.record` is still
   open. Say which half moved. **The row does not close.**
6. **Tally.** 94 rows / 18 closed at `e3f447a` (empirical review, verified) → 20 closed after this
   loop. Any new row records its own snapshot `(n/m closed)` and never updates it.
7. **Anything else found stale** is corrected in place with the refuting measurement cited, or
   downgraded and marked as such. Never silently edited, never deleted.

### Seams

- **MEASURE what `tests/test_doc_governance.py` actually asserts** about a new spec/plan and about
  edits under `docs/superpowers/**` — in particular whether it requires the `Doc impact:` block and
  how it treats evidence immutability. It passed **4 passed** on the spec commit, so the spec and
  the already-committed banner edit are fine; the register edits are a different shape.
- **`grep docs/wiki/` for the page that states the membrane gate.** If one exists, add the line that
  the `dec` leg is unconditional at document scope. **If none exists, say so** and the increment is
  the CLAUDE.md paragraph alone.

### FALSIFICATION (required in the report)

There is no test to invert, so falsify the **oracle that governs these files**: break one thing the
doc-governance suite checks (drop the plan's `Doc impact:` block, or leave a struck row deleted
rather than struck), show `pytest -q tests/test_doc_governance.py` **red**, restore, show green. If
the suite turns out to check neither, **say that in the report** — an unfalsifiable pass is a finding
about the governance suite, and it is Loop 3's kind of finding.

---

## Task 4 — R103's mechanical half (independent; droppable)

**Widen `scripts/probe_emitter_typing.py` to parse `vocab/ontology/tab-datagrid.ttl` alongside
`tab.ttl` (`:111`) and report the count.** It closes nothing.

Safe to carry, measured: no test and no CI job invokes the probe (§ Measurements), and it compiles
with `validate_shapes=False`, so **Task 2's gate change cannot move its result.** It needs the
corpus, so this is a local measurement exactly as R61's original run was.

**Deliverable:** violated rules and violating nodes attributable to `tab-datagrid.ttl`, split as
R61's probe splits them — live hazard (the class is shape-targeted) vs inert — appended to **R103's
row as a carry**. The row is **not** struck.

Expect at least `tab-datagrid.ttl:261`'s `tab:universeSource rdfs:domain tab:ColumnUniverse` against
`datagrid.py:625-626`, which hangs it on the grid node. **Report it; fix nothing** — *"do not close
this by fixing `tab:universeSource` alone"* (R103's row), and R61's modelling question stays
deferred (spec §7).

### FALSIFICATION (required in the report)

Revert the widening and show the probe reports **zero** rules from `tab-datagrid.ttl`, then restore
and show the count. That is the proof the widening is load-bearing rather than decorative.

---

## Stopping points

Each leaves the tree green and shippable, in this order: **Task 1** (closes a row) · **Task 2**
(closes the largest row) · **Task 3** (no code) · **Task 4** (independent, may be dropped).

## Definition of done

- `pytest -q` green, reported with its count.
- T2b's pair reported: **316 with the gate, 0 without**, plus the corpus wall-clock delta.
- Four `## FALSIFICATION` blocks, one per task, each showing red → restore → green.
- Seam answers recorded **in the register rows**, not only in task reports: the `compile_tables`
  caller question (spec §2.7) and the wiki-page question (spec §6).
- R102 and R104 struck with evidence in place; R89 amended; R103 carried; the tally at 20 closed.
