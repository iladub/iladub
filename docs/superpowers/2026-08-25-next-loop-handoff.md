# Handoff — choosing the loop after `holon:05`

**Topic:** the next loop — `holon:05` is merged to `main`, and the maintainer has chosen **candidate
A, the declaration instrument (R135 + R117)**. This file carries that choice, the other three
candidates as the rejected alternatives, and the evidence for each.

**Date:** 2026-08-25 · **Branch:** `main` at `2ae8103` · **Shape: pointers only.**

**Why this exists and what it is NOT:** it was written at 172k tokens, **3.4× the 50k originating
floor**. Choosing the next loop is originating work, so it was not done here. This file is the
*survey*; the *choice* and the spec belong to a fresh session. Nothing below is a decision.

## Goal

One line: **write the spec for candidate A — the declaration instrument closing R135 (and possibly
R117) — in a cleared session, in that session's first third.**

**The choice is MADE; do not re-litigate it.** The maintainer chose A on 2026-08-25, over B
(`holon:06` / the grounding portal), C (record-keeping integrity, R136+R137) and D (R130's forward
arm), which are surveyed below and remain open. The reason given was **not** that A is the most
important — B is the more significant architectural step and the honest successor. It was that A's
**scoping call is already taken and recorded**, so this session can go straight to a spec instead of
spending its best third re-deriving a decision; A is small, genuinely vertical, and its falsifying
oracle already exists.

**What is NOT decided, and is yours:** whether the shipped instrument closes **R117 as well as
R135**. The standing call is *plan ONE instrument; close both in the same act **only if** it
demonstrably covers `iladub-hga-align.ttl`; do NOT merge the rows now.* R117 carries a scoping
question R135 does not — **what *declared* means at the alignment seam** — and answering that is
spec work, not a decision already taken.

## Where the primaries are, and what to establish at each

| primary | what to establish there |
|---|---|
| `docs/superpowers/residues.md` | **The INDEX — read it in full (~2.8k tokens).** It is the only file you are expected to read entirely. An index line is a pointer: never plan against one without opening its full row. |
| `docs/superpowers/residues-open.md` | The full rows. Open only the ones the index sends you to. Register state at merge: **129 rows / 25 closed / 104 open**, next free number **R140**. |
| `docs/superpowers/2026-08-25-holon-05-loop-ledger.md` | The just-closed loop's ledger, 1031 lines. **Its § Rulings are the decisions taken on the maintainer's behalf** — including the R135/R117 call, which is already made. Read it only if your candidate touches `holon:05`'s surface. |
| `docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md` | §11 for what `holon:05` deliberately left unbuilt, and §7 for what it scoped out. **Caution: §4.5's five `document.py` citations are stale — that is R138.** |
| `tests/arc-manifest.ttl` | The rung/criterion state. What `holon:06` and the `etkl:` rung actually require, as opposed to what prose says they do. |
| `CLAUDE.md` | § Loop & context hygiene, § Plan authoring discipline (six rules), the neurosymbolic gate, source ownership. All binding. |

## The four candidates, with where each is measured

**A. The declaration instrument — R135 + R117.** Nothing checks that a term a runtime artifact names
is *declared* anywhere: `membrane-health.rq` BINDs `etkl:Intact`/`Weakened`/`Compromised` as bare
IRIs, so deleting `etkl-holons.ttl` leaves `holon:05`'s oracle green — measured by M19's ablation on
2026-08-25, and it refuted a manifest edge. R117 is the same failure class at the alignment seam
(`iladub-hga-align.ttl`'s subclass axioms). *Distinctive property: the scoping call is already
taken and recorded* — plan ONE instrument; close both in the same act **only if** the shipped
instrument demonstrably covers `iladub-hga-align.ttl`; do **not** merge the rows now.

**B. `holon:06` — the grounding portal's health.** R134 names itself "`holon:06` territory":
`etkl:GroundingPortal` is instantiated **nowhere** in `*.py`/`*.rq`, and `feed.py:642-643` guards a
different graph behind a different boundary with a bare `assert` that `python -O` erases. Several of
`holon:05`'s own §11 residues (R131–R134) close "with `holon:06`". *Distinctive property: it is the
architectural successor* — `holon:05` did the compile membrane; this is the portal.

**C. Record-keeping integrity — R136 + R137.** A criterion can be `prog:met true` while its own
`prog:source` points into "Planned work (not done yet)" and nothing refuses it (R136); and the
residue register has **no integrity check at all** — deleting an index row, or flipping a closed row
back to `open`, both leave the suite green (R137). *Distinctive property: these are the instruments
the other three loops will be judged by, and this branch proved both bite in practice.*

**D. R130's forward arm.** The `(query, term)` vacuity registry ships its reverse arm only. Measured
blocker: over the 29 `.rq` files mentioned in `src/**.py` the criterion yields **164** unreachable
pairs of which **162 are a category error** (the query runs over a transient
`urn:iladub:evidence:` graph, never the compiled one). *Distinctive property: it has a known,
measured obstacle — do not start it without a plan for the category error.*

## What was decided, and where each decision is recorded

- **The R135/R117 scoping call is TAKEN** and recorded in the `holon:05` ledger (§ final review) and
  in `2026-08-25-holon-05-final-review-handoff.md`. Nowhere else. **Therefore reversible.**
- **Candidate A is chosen** — maintainer decision, 2026-08-25, recorded **here and nowhere else**,
  therefore reversible. B, C and D stay open in the register and lose nothing by waiting.
- **Nothing about A's design is decided.** The ordering of A–D is the order they were surveyed, not
  a ranking of anything but this one choice.

## Unverified or assumed

- **The candidate set is not proven exhaustive.** It was drawn from the register index plus the
  `holon:05` ledger, not from a full read of all 104 open rows. A fresh session should re-survey.
- **`R115` says 72 of 87 open rows block no criterion of any rung.** If that still holds at 104 rows,
  then most of the register is orphaned from the arc, and "which residue is next" may be the wrong
  question — the right one may be R115 itself. **Not re-measured here.**
- **The full suite was not green-verified at the moment this was written.** `holon:05` merged after a
  targeted run (`55 passed`) on the merged tree; the full run was launched separately. Check its
  result before treating `main` as a clean base.
- The `holon:06` framing assumes the arc manifest's rung structure is still what `holon:05`'s Task 7
  left it as — that task **deleted a manifest edge**, so re-read the manifest rather than the prose.

## The next concrete action

**In a fresh session, write candidate A's spec.** In this order:

1. **Open R135's and R117's full rows** in `residues-open.md` (the index lines above are pointers,
   not the residues). Establish at each: what the failure actually is, and what the row says would
   close it.
2. **Reproduce the hole before designing a guard for it.** The evidence is M19's ablation, run
   2026-08-25: delete `vocab/ontology/etkl-holons.ttl` and `holon:05`'s oracle stays **green**,
   because `vocab/queries/membrane-health.rq` BINDs `etkl:Intact`/`Weakened`/`Compromised` as bare
   IRIs. A spec written without re-running that is a spec whose author did not measure its premise
   (CLAUDE.md plan-rule 2). The structural half is cheap and was verified independently:
   `grep -rn "etkl-holons" src/ --include='*.py'` returns nothing, and the file is in none of
   `_TAB_SHAPE_FILES` / `_DEC_SHAPE_FILES` / `_FULL_ONT` (`compile.py:398,421,441-453`).
3. **Answer the two questions this repo requires before any design** — *what proposes and what
   disposes, and are they independent?* and *what is the falsifying oracle?* **Name the oracle
   BEFORE designing.** Note the trap this loop just paid for twice: an instrument that pins its own
   hand-typed registry rather than the artifact is vacuous, and a test that stays green with its
   subject deleted pins nothing.
4. **Classify the decision under the neurosymbolic gate before writing any Python.** "Is this term
   declared?" is a question about an RDF evidence graph. Both AXIOM forms are live options and the
   split is load-bearing — a *derivation* over the graph is open-world SPARQL; a *constraint* on
   what may cross is closed-world SHACL. **Never use closed-world/SHACL to derive.** Procedural code
   here must be earned and justified in the spec.
5. **Then rule on the R117 question** — what *declared* means at the alignment seam — and let that
   ruling decide whether one instrument closes one row or two.

**Do not start implementation in the spec's session.** The spec is written first; the plan and the
SDD loop follow, per § Loop & context hygiene.
