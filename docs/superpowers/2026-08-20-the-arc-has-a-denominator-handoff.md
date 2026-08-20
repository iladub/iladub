# Handoff — the arc has a denominator: spec written, plan is the next act

**Topic:** process · **Date:** 2026-08-20 · **Branch:** none yet (start from `main`) ·
**Shape: originating** · **Status: SPEC WRITTEN AND MEASURED. PLAN NOT WRITTEN.**

> Written at 158,896 tokens — 3.2× the originating floor — which is why the plan is the next
> session's first act and not this one's last. Preflight logged (`stop`).

## Goal

One line: the strategy instrument, slice 1 — **give each named rung of the arc a countable
denominator and a dependency edge to the register**, so the cockpit stops printing `stage ?/5`.

## Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` (536 lines) | **the spec. Read this one first and in full.** §7 carries the five denominators with their measurements inline; §11 lists the seven seams a plan must measure, in order |
| `docs/superpowers/2026-08-20-strategy-instrument-handoff.md` | the previous handoff — the eight decisions, the arc inventory, the render design. **Evidence class, immutable. Two of its citations are wrong on disk** (spec §7.2.1) and one of its claims is refuted (spec §7.2). Read it for the decisions, not for the line numbers |
| `docs/superpowers/2026-08-20-strategy-instrument-brief.md` | the maintainer's own words. Origin only |
| `docs/narrative/scope-evolution.md` | **already edited this loop** — five named rungs, `tab` added, numbering removed. Assertion class; site builds `--strict` |
| `scripts/cockpit.py` + `tests/test_cockpit.py` | the surface. `arc()` at `:134` is the hole. Its regex defect is ALREADY FIXED (`8bd3120`) — the previous handoff's defect (1) is closed, do not re-fix it |
| `tests/corpus-manifest.ttl` + `tests/corpus-shapes.ttl` + `tests/test_corpus_manifest.py` | the pattern to copy for the state half: tracked hand-authored graph, validated, never auto-written |
| `vocab/shapes/doc-governance-shapes.ttl` + `vocab/queries/docgov-*.rq` | the pattern to copy for the membrane and derivation halves |

## What was decided, and where that decision is recorded

**The eight prior decisions are recorded ONLY in the previous handoff** (§ *What was decided*) — the
maintainer's live answers, reversible. They are restated as inputs in spec §2 and are not re-opened.

**Decided THIS session, recorded only in the spec:**

1. **`prog:retrospective` is required on every criterion** (spec §3.2). `declaredOn < reachedOn` is
   unsatisfiable retroactively, so grandfathering is *labelled* rather than pretended. The membrane
   enforces the clause going forward (M4). **This is the spec's one substantive addition to the
   prior design and the clause most worth attacking.**
2. **`met` is asserted, not derived** (§3.1) — forced by the cockpit's no-rdflib performance
   contract, with honesty restored by the membrane and an agreement test.
3. **File layout**: state at `tests/arc-manifest.ttl`, membrane at `tests/arc-shapes.ttl` (the `cor:`
   precedent), derivations at `vocab/queries/arc-*.rq` (the `dg:` precedent). The previous handoff
   left this unresolved between `docs/` and `tests/`; `docs/` was rejected because a stray `.ttl`
   there would be published by mkdocs and `prog:` is unpublished.
4. **`tab`'s denominator is the eight escalation-reason classes, adjudicated — not "does not fire"**
   (§7.4), and **not one criterion per residue**. The reasoning for rejecting the register-as-
   denominator is in §7.4's first paragraph and is the part to attack if any part is wrong.
5. **A fourth derivation, `arc-orphan.rq`** — open residues blocking no criterion of any rung (§5).

## Measured this session — four corrections to the previous handoff

1. **`dec` HAS a declared denominator**, in `CLAUDE.md:252` (worked example + negative test per
   shape). Measured **10 of 15 shapes carry both**; five are positive-only. Plus a 16th criterion:
   `CLAUDE.md:249-251` requires four `prov:` alignment axioms that `dec.ttl:38,55,72,85` declares and
   **no test asserts**. The rung reads **10/16**, not "the most complete." (Spec §7.2.)
2. **Both of the previous handoff's rung-2 citations are wrong**: `iladub-shapes.ttl:38` is `:37`
   (shape) / `:39` (the invariant); `src/iladub/compile.py` does not exist — it is
   `src/iladub/etkl/compile.py:421`. (§7.2.1.)
3. **`holon` reads 4/6, not 0/2 remaining** — `docs/holonic-interaction.md` § *What is built* has
   **four** bullets (`:145-156`), not two, and § *Planned work* two (`:158-163`). (§7.3.)
4. **The strip is already 169 characters** and the arc segment is 82, on an 80-column terminal. The
   previous handoff estimated ~70 for the whole arc gauge. (§6, commands inline.)

**And two broken pointers in the register itself**, which are the live case for the membrane:
`battery-run-final.log` is cited as measurement evidence by R43, R44 and R45 and **is not in the repo
or in git history**; R74's closure names `test_cbh_p0_known_defects_are_pinned_not_hidden`, which
**does not exist** (the real pin is `tests/etkl/test_datagrid.py::test_cbh_p0_table_b_leak_is_pinned_not_hidden:1135`, PASS 0.89s).

## Unverified or assumed

- **`tab`'s numerator is UNMEASURED.** Which of the eight escalation reasons fire on the corpus, and
  how often, has never been counted. It costs a ~5.5-minute corpus run (spec §11 seam 1) and it is
  on the critical path: `tab` renders `?` until it is done, and authoring its rows from the register
  alone would put a fabricated number on the strip.
- **`prog:declaredOn` per criterion is not yet measured** — the rule is *the commit date of the
  declaring line of prose*, and no `git blame` has been run for any of them (§11 seam 3).
- **Whether the harness renders a multi-line `statusLine`** is unknown; `tests/test_cockpit.py:54`
  pins exactly one line (§11 seam 5).
- **Whether liveness is a `dec` criterion or only a residue edge** is named as a decision the plan
  must make, not one this spec made (§11 seam 7).
- **Nothing in this loop has been implemented.** No TTL, no shape, no query, no cockpit change. The
  only file changed is `docs/narrative/scope-evolution.md` (plus the two new evidence documents).
- The `#11 seam 6` residue→residue backfill set is 7 rows under this spec's grep and 6 under the
  previous handoff's. Neither has been reconciled.

## The RUNNER trap — read this before running any test

**`python3` on this machine is the wrong interpreter.** It carries rdflib 7.1.4; the venv carries
7.6.0 and `tests/test_corpus.py:7` names `./.venv/bin/python` as the runner. Under `python3` every
corpus test reports a **false red** (`TypeError: int() … not 'NoneType'` from `classify-kind.rq`) and
`pyrudof` appears absent, so the membrane-equivalence battery silently skips.

This session hit it twice and wrote a defect report for a defect that does not exist before catching
it (spec §7.2.2 keeps the correction, because the mistake produced the better rule: **oracle
greenness is runner-relative, so the manifest records the runner it was validated against** — M5's
third arm). **Use `./.venv/bin/python -m pytest`.**

## The next concrete action

In a **fresh session**: write the plan from
`docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md`, starting with §11 seam 1
(the corpus measurement) because everything about the `tab` rung waits on it.

**Folded into that seam on the maintainer's call, 2026-08-20 (recorded here and in spec §11 only):**
the six unadjudicated corpus documents are adjudicated **in the plan session, on the same corpus
run**, not as a separate loop ahead of it. The reasoning: the per-document escalation-reason census
the `tab` rung needs is exactly the evidence an adjudication requires, so it is one loop rather than
six — and the register has already priced the alternative at *"its own reading loop"* per document
(R43, R44, R45, R62).

**Expect the fraction not to move, and do not make it move.** The likely outcome is five or six
recorded HOLDs (`cor:Unadjudicated` + a `cor:adjudication` carrying the reasoning — the manifest's
own encoding, `tests/corpus-manifest.ttl:16-20`). That is the success condition. Pinning a
`cor:scoreFloor` at a document's current score would take the rung to 7/7 with no reading improved;
**spec §7.1 was corrected on 2026-08-20 to refuse exactly that**, and §8 names the falsifying test
the plan must supply.

CLAUDE.md § Plan authoring is in force and this spec was written to make it cheap: every load-bearing
claim carries its command and output inline, §9 states what is deliberately NOT built, and §11 names
the seams to measure rather than the answers. **A plan containing a function body, an unmeasured
load-bearing claim, or a test contradicting §9 is a review failure.**
