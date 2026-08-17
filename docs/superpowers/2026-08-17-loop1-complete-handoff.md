# Handoff — Loop 1 (the gate and the label) is COMPLETE; Loop 2 needs a fresh session

**Date:** 2026-08-17 · **Branch:** `loop1-gate-and-label` · **Head:** `a0e7ee1` · **Tree:** clean
· **Not merged to `main`.**

## Goal

Loop 1 of the R97–R104 split shipped all four tasks. This file points at the evidence and names
what Loop 2 starts from. It is a **set of pointers** — it does not restate the primaries.

## Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the spec | `docs/superpowers/specs/2026-08-17-the-gate-and-the-label-design.md` | §7 is the scope fence Loop 2 must not silently cross; §5's D8(a) row is Loop 2's actual subject |
| the plan | `docs/superpowers/plans/2026-08-17-the-gate-and-the-label.md` | the four tasks and their falsification requirements, as executed |
| the code | `742e862` (R104), `b09dbd1` (R102), `d84956d` (docs), `a0e7ee1` (probe) | each commit message carries its own measurements |
| the register | `docs/superpowers/residues.md` → `residues-open.md` / `residues-closed.md` | ~~R102~~ and ~~R104~~ closed with evidence; R89 amended; R103 carried; R100's citation corrected |
| the contract | `CLAUDE.md` § Core design principles → *Producer-side guards vs the membrane* | R89's adopted rule now lives here, not only in a handoff |

## What was decided, and where each decision is recorded

1. **Ungate the `dec` leg at the DOCUMENT gate only; page gate untouched; `tab` leg ungated
   nowhere.** — spec §2.2, and now `document._legs_for_document`'s docstring + `compile_document`'s
   docstring paragraph. Reversible: it is one helper and one call site.
2. **A gate change is in scope; a wiring change is not** (why R102 was fixable while R99 defers) —
   spec §2.6, and recorded as an amendment **inside ~~R102~~'s struck row**, because that row had
   called its own fix "a membrane-composition question" and that was wrong.
3. **R89's producer-side-guard rule** — CLAUDE.md, as above. The *application* to
   `BandRecorder.record` is **not** decided; R89's row says which half moved and stays open.
4. **The conforming path's discarded `dec` report stays discarded** (`compile.py`'s `_validate`,
   the `I-E` comment) — spec §3.2 ruled it out of scope in writing. Recorded in the code comment
   and in ~~R104~~'s closure text. **Reversible and cheap; nobody has argued it should change.**
5. **A closing loop strikes and MOVES a row, never deletes it** — the `residues.md` preamble said
   the opposite until this loop (E4). Now recorded in both CLAUDE.md and the preamble, with the
   reason.

## Measured, with the command, in this session

- **R102, O3:** 769 minted / 453 validated / **316 never** with the gate → 769 / 769 / **0** without.
  Method and the false-0 trap (per-document `seen` reset; global set reports 0 because page-scoped
  decision URIs collide across documents — union 428 vs sum 769) are in ~~R102~~'s row.
- **Cost:** +2.8 s across the three newly-validated documents on ~320 s for the 7-document compile.
- **R103, Task 4:** `tab-datagrid.ttl` = 13 rules, 3 violated, 18 nodes, **0 live**. Reverting
  `ONT_FILES` gives 56 nodes / 5 rules / no datagrid line.
- **Suites:** `pytest -q` green after Task 2 (1228 passed / 7 skipped / 1 xpassed) and after Task 3
  (1228 / 7 / 1 xfailed). After Task 4, `pytest -q -m "not corpus"`: 1185 passed / 7 skipped /
  43 deselected / 1 xfailed.

## UNVERIFIED or ASSUMED

- **The full `pytest -q` has NOT been run at `a0e7ee1`.** Task 4 touched only
  `scripts/probe_emitter_typing.py` (invoked by no test and no CI job — verified by grep over
  `tests/` and `.github/`) and one register row, so the 43 deselected corpus tests were reasoned
  unaffected rather than run. **Run it before merging.**
- **The `xpassed` → `xfailed` flip** between the two full runs is `test_derivation_perf.py:146`,
  `strict=False`, whose own marker documents a ~10% margin at the affordable N. Read as documented
  flakiness, **not** re-measured as such in this session.
- **The 16 probe artifacts are a NEW finding, made late**, and nothing downstream has been re-read
  in their light. In particular, `tab.ttl`'s pre-existing 5 violated rules have **not** been
  re-examined for the same false-positive class. See R103's row.
- **Every figure here is the rudof leg.** The pySHACL leg stays unrun — standing since R87.
- **`compile_tables` is publicly exported**, so the document-scope coverage R102 achieved can be
  bypassed by an external caller. Recorded in ~~R102~~'s row; judged the same shape as R34's
  already-registered bypass, and **not** raised as a new row. That judgement is reversible.
- **Nothing was merged.** The branch is `loop1-gate-and-label`; no PR opened.

## The next concrete action

Open a fresh session, run the full `pytest -q` at `a0e7ee1`, and if green open the PR for
`loop1-gate-and-label`. **Loop 2 (the coverage ledger — spec §5's D8(a), whether the `tab` leg's
gate condition is AXIOM/NEURAL/PROCEDURAL) has neither spec nor plan and must start in its own
session**, per CLAUDE.md § Loop & context hygiene.
