# Handoff — the next loop after R103 closed

**Date:** 2026-08-20 · **Branch:** none (start from `main`, **after PR #109 merges**) ·
**Shape: originating** — choosing and specifying a loop. Not started.

> Written from a session at 141K, 2.8× the originating floor, immediately after closing R103.
> Nothing below is a design. Treat any sentence that sounds like a conclusion as a claim to
> re-derive.

## Goal

Choose the next loop and write its spec. **Recommended: R61** — this loop just supplied the input
R61 was explicitly waiting on. Two alternatives are live and neither is blocked.

## Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the loop tracker | memory `next-loop-r97-r101.md` | the three-way split (Loop 1 done, Loop 2, Loop 3) and what each covers. **It is a tracker, not a spec** |
| the split decision | `docs/superpowers/2026-08-17-loop-split-decision.md` | why the original R97–R104 spec was superseded in scope; still the authority on Loops 2 and 3 |
| R61's row | `residues-open.md` (index line 127 in `residues.md`) | the 14 live emitter/vocabulary disagreements and the 4 attributable ones. **Open the row; the index line is a pointer** |
| what R103 just handed R61 | `docs/superpowers/2026-08-20-r103-membrane-decision.md` | the constraint R61's spec must start from — see below |
| the instrument | `scripts/probe_domain_range_agreement.py` | the four classes and, since 2026-08-20, what they do and do not claim |

## What was decided, and where that decision is recorded

- **R103 is closed** — `residues-closed.md`, `compile._build_membrane`, and the 2026-08-20
  evidence doc. The decision (`tab-datagrid.ttl` stays out) is recorded in code at its own
  absence, and its **reversal condition** is pinned by
  `test_tab_datagrid_axioms_are_unreachable_by_every_membrane_shape`.
- **R61 is unblocked** — recorded in the memory tracker and in R103's closing row. It had been
  waiting on "R103's count"; the count is in.
- **The next loop is NOT chosen.** Nowhere but this file, and this file only recommends. Reversible.

## The constraint R61's spec must start from (this is the load-bearing carry)

`membrane.subclass_closure` (`membrane.py:448`) reads **only** `rdfs:subClassOf` from the ontology
and never mixes it into the validated payload — **no ontology subject ever reaches an engine**
(MEASURED 2026-08-20: 0 `tab:`-namespace subjects in the 4,773-triple closure of ons p7).

Consequence, and the reason R61 cannot be specced the way it kept being approached: **the four
real emitter/vocabulary disagreements are unenforceable by the membrane by construction.** Adding
files to the membrane ontology list is not a lever. R61 needs a different instrument, and naming
what disposes it — before designing — is the first question.

The four, from R103's row: `domain universeSource -> ColumnUniverse` (2 nodes,
`datagrid.py:625-626` vs `tab-datagrid.ttl:261`) and `range columnFamily -> CellDatatypeFamily`
on `tab:Text` (2 nodes; `tab.ttl:211` declares `tab:Text a tab:CellDatatype`, while
`tab-datagrid.ttl:177`'s prose calls it a legal family and `datagrid.py:638` emits it as one).
**Re-run the probe; do not quote these numbers from here.**

## The register ratio — measured 2026-08-20, and it should inform the pick

Raised by the maintainer as the framing question for the next loop, so it is recorded here.

- **Current: 21/94 closed (22.3%).** 73 rows open.
- **The trend the tally convention exists to expose** (only rows from R95 carry snapshots):
  `R95 20.0% → R96 19.8% → R97 20.7% → R98 20.5% → R99 20.2% → R100 20.0% → R101 19.8%`, and
  now **22.3%**. It bottomed at R101 and has risen since.
- **Recent rate, 2026-08-12 → 2026-08-20: 9 raised, 9 closed.** Break-even. That is a real
  change from the ~6:1 the earlier arithmetic recorded — but **break-even means the backlog
  never shrinks**, and 73 open rows is the number that matters, not the percentage.

**Two cautions this measurement raises, both unverified:**

1. **A close that re-attributes its residue to another open row improves the ratio without
   repairing anything.** R103's own close does some of this — its 4 leftover disagreements went
   to R61. That particular attribution looks sound (R61 already owned them, and R103's actual
   question was genuinely answered), but *the pattern is worth auditing across the 21 closed
   rows before treating 22.3% as earned*. Nobody has done that audit.
2. **The closes are concentrated in a few loops** (3 on 2026-08-12, 2 on 08-13, 2 on 08-17), which
   suggests debt-reduction loops close rows and feature loops raise them. If true, the pick below
   should be biased toward whichever candidate closes the most rows — **not** the one with the
   most interesting question. That is an argument this handoff does not settle.

**How it bears on the pick, honestly: it argues against R61.** R61 is one row and the loop would
likely raise others. **Loop 2 (R97/R98/R99/R100) is four rows**, and Loop 3 covers R101 plus a
named CI gap. If the ratio is the priority, Loop 2 is the pick and the recommendation below is
the wrong one. The recommendation stands as written because it was made on adjacency; this
section is the counter-argument, and the maintainer has the call.

## The alternatives, if R61 is not the pick

- **Loop 2 — the coverage ledger** (R97/R98/R99/R100). A *vocabulary* loop: namespace, `vocab/`
  file, worked example, negative test. Note the tracker's warning: **R100's cheap close was
  REFUTED** by measurement M-B (five shapes differ by leg, not one).
- **Loop 3 — what CI does not run** (R101), *plus* the finding that `corpus/` is gitignored and
  the guard R87 shipped **has never run in CI** — the repo's own vacuity guard is an instance of
  R101.

## Unverified / assumed

- **That R61 is the right pick.** It is a recommendation from adjacency (R103 just fed it), not a
  measured priority. Loop 3 has a plausible claim to being more urgent — a guard that has never
  run is a stronger defect than a modelling disagreement affecting 4 nodes.
- **That R61 is one loop and not two.** The `tab:universeSource` and `tab:Text` disagreements have
  different shapes (one is an emitter attaching a property to the wrong subject; the other is a
  vocabulary contradicting its own prose). Whether one instrument disposes both is unmeasured.
- **That the probe is the right instrument for R61.** It *reports* the disagreements; nothing
  establishes it should also *gate* them. Its exit code is already wired to do so
  (`UNTYPED`/`DISAGREE` on a shape-targeted class → non-zero) and currently returns 14 live — so
  turning it into a gate today would fail. That interaction is unmeasured.
- **The pySHACL leg still has not run against `540e608` or later** — carried unchanged from the
  2026-08-17 tracker, still true as far as this session knows, not re-checked.

## The next concrete action

**Merge PR #109 first** (green; CI passed in 10m58s; the classifier blocked the automated merge).
Then, in a fresh session, before any design: open R61's full row and re-run
`scripts/probe_domain_range_agreement.py`, and answer the two questions
[[spec-writing-and-fresh-loops]] requires — *what proposes, what disposes, and are they
independent?* — for R61 specifically, given that the membrane is now known not to be the
disposer. Name the falsifying oracle before designing anything.
