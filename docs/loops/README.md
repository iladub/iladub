# iladub loops — the build paradigm

> *Stop prompting. Design the loop. Get a score.* — adapted for iladub:
> **design the *verifier* first; let a bounded loop converge; never let a proposition pass as an assertion.**

iladub is built as a set of **loops**, not one-shot pipelines. Prompt-engineering (phrase the request) and
context-engineering (structure the input) hit a ceiling on hard, open-ended problems like document
compilation — you cannot *phrase* your way to a table parser. **Loop engineering** ([Lindenberg],
[Greyling]) is the next step: you stop trying to *solve* the problem and instead **build the system that
converges to a checkable score** — the maker/checker split, durable state, hard limits, and a verifier you
design *first*.

This maps almost 1:1 onto what iladub already is:

| Loop engineering | iladub |
|---|---|
| verifier, designed first | the **oracle** (round-trip + invariants) + the **contract** (SHACL) + assert/propose |
| maker / checker split | the **determinism cursor** — a model *proposes*, the deterministic layer *validates* |
| Control: continue/retry/repair/escalate/ship | **`dec`** + `risk` escalation |
| durable State / skills | the **holon** being built + learned patterns |
| model chosen last | the small model, **residue only** |

So adopting loop engineering isn't a rewrite — it's **naming and completing the loop**.

## How we work now

1. **Every build increment is a loop, designed on a one-page [canvas](loop-canvas-template.md) before code.**
   Fill the canvas outside-in: **Goal/Verifier first**, model last.
2. **The Goal is a *proof*, not a claim.** *"A loop does not satisfy your goal; it satisfies the gate you
   wrote."* If the verifier is wrong, nothing else matters — so it is designed first and it must
   **generalise to every document** (no overfitting a single example; see `no-overfitting`).
3. **Roll out in trust tiers:** **L1 report** (observe/draft only) → **L2 assisted** (propose, human
   reviews) → **L3 unattended** (autonomous, within Limits). Nothing runs at L3 until its verifier is trusted.
4. **State is the spine.** Each loop keeps a `STATE.md`-style record of what it knows and decides, and
   accrues durable **skills** (learned generator/kind patterns) so it gets better over time.

## Two invariants stamped on every iladub loop

- **Verifier = the deterministic oracle; maker = the proposer.** Determinism validates; the model only
  generates the *residue* the geometry can't decide. (The determinism cursor.)
- **No overfitting.** The gate must hold for *every* document. A loop tuned to make one example pass is a
  **false score** — zero tolerance.

## The loops

| # | Loop | Owns | Status |
|---|---|---|---|
| 1 | [table-holon compiler](2026-07-05-table-holon-loop.md) | compile any table region → a validated table-holon | design |
| … | (document-holon, promotion, governance loops) | later | — |

[Lindenberg]: https://www.linkedin.com/pulse/from-prompts-loops-next-step-agent-engineering-andré-lindenberg-wnqre/
[Greyling]: https://github.com/cobusgreyling/loop-engineering
