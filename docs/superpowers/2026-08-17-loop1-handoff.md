# Handoff — Loop 1 (the gate and the label), specced and unplanned

**Date:** 2026-08-17 · **Branch:** `main`, HEAD `b99e68c`, tree clean
**Written at:** 111.8K tokens, 2.2× the 50K originating floor — which is why this is a handoff and
not a plan. **Nothing below was designed in this session beyond the spec itself.**

## Goal

Execute Loop 1 of the R97–R104 split: ungate the compile membrane's `dec` leg at document scope
(R102), carry the leg identity through `_validate` (R104), record R89's adopted rule in CLAUDE.md,
run the register-honesty pass, and take R103's probe measurement.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-17-the-gate-and-the-label-design.md` | **The contract for this loop. Read it first and in full — it is short.** §2.2 settles which gate. §3.2 is `_validate`'s new signature and its four invariants. §7 is what the loop must NOT do. §9 is the oracles. §10 is the task order and why R104 precedes R102. |
| `docs/superpowers/2026-08-17-loop-split-decision.md` | Why the loop is this size, and what Loops 2 and 3 own. Read its Loop 1 section if the spec's scope is ever in question; do not re-open the split. |
| `docs/superpowers/2026-08-17-empirical-review-findings.md` | Every measurement the spec quotes, with its reproduction. E2's timing table is the cost baseline; § Verified is the claim-by-claim confirmation. |
| `src/iladub/etkl/compile.py:453-465`, `:1097-1103` | `_validate` and the page-scope call site + its hardcoded `"tab: SHACL"` raise. |
| `src/iladub/etkl/document.py:1584-1587`, and `:110` | The document gate, its raise site, and the **second binding of `_validate` by name at import** — instrumenting `compile._validate` alone misses it. |
| `tests/etkl/test_compile_membrane_shapes.py:35,94,98,122,143` | The three 2-tuple unpacks that must change, plus `_under_furnished_promotion()` at `:98` — the constructible setup O4 needs. |
| `tests/etkl/test_membrane.py:92` | Pins `inspect.getsource(C._validate)`. Check it against the signature change; do not assume it survives. |
| `docs/superpowers/residues-open.md:73` (R89), `:82` (R102), `:83` (R103), `:84` (R104) | The four rows this loop touches. §4 of the spec says which strike, which carry, which amend. |

## What was decided, and where each decision is recorded

1. **Which gate is ungated — the document gate, `dec` leg only.** Recorded in the spec, §2.2, with
   the coverage and redundancy arguments. This was the load-bearing unknown; it is now settled in a
   tracked file, not in conversation.
2. **D7's principle — a gate change is in scope, a wiring change is not.** Spec §2.6. This is what
   separates R102 (proceeds) from R99 (waits for Loop 2).
3. **R104's contract is a 3-tuple, not a leg-prefixed report string.** Spec §3.2, with the reason
   (O4 must assert the *absence* of `tab`, unpinnable by substring search over a SHACL report).
4. **The `:463` conforming-path wrinkle is out of scope.** Spec §3.2, final paragraph — ruled in
   writing rather than left silent.
5. **E1's correction to the canonical register.** Committed at `d455766`, ahead of the spec.
6. **R89's rule text for CLAUDE.md.** Drafted verbatim in spec §6. It has **not** been written into
   CLAUDE.md yet — that is Loop 1 task work, and CLAUDE.md is a Contract document.

## Unverified or assumed

- **The corpus wall-clock delta of ungating is not measured through the compile path.** E2's
  ~2.0 s (dec column) is a standalone validate. Spec §2.4 makes reporting the real delta a task
  obligation. **Do not quote E2's "~4 s" as this change's cost** — that figure is both legs.
- **Whether any production caller invokes `compile_tables` outside `compile_document`** — spec
  §2.7's seam, unmeasured, and it bounds how wide R102's close actually is.
- **Whether a `docs/wiki/` page states the membrane gate** — spec §6 names it as a grep, not a fact.
  If none exists, the doc increment is the CLAUDE.md paragraph alone.
- **Whether `test_vacuity_registry.py` stays green** after ungating. Reasoned to be unaffected (its
  focus-node counts are rdflib over the 7 final graphs, independent of `_validate` calls) but **not
  run**. The standing two-edit coupling applies if a registered row goes live.
- **The pySHACL leg has still not run**, standing since R87. Every verdict figure in the spec is the
  rudof leg.
- **`compile.py:408-409`'s and R100's row's `:1083` citation are stale** (at HEAD `:1083` is
  `if denom:`). Spec §4 item 2 makes fixing both part of the register pass.

## The next concrete action

**In a fresh session: write Loop 1's plan from the spec's §10, then execute it.**

Three tasks, in this order — the order is load-bearing (R104 changes `_validate`'s signature and
R102 changes the call site that reads it; doing R102 first means editing `document.py:1585` twice):

1. **R104** — the label. Oracles O4 and O4b, spec §9.
2. **R102** — the gate. Measure §2.3's seam *before* writing the call; report §2.4's delta; have
   §2.5's response ready if the corpus goes red. Oracle O3, falsification = 316.
3. **The contract paragraph + register pass** (§6, §4), then **§8's probe measurement**, which is
   independent and may be dropped without affecting the slice.

Plan rules 1–5 bind: no function bodies, every load-bearing claim measured inline, named seams, a
`## FALSIFICATION` block per task, and every plan-supplied test reconciled against spec §7 before it
ships.
