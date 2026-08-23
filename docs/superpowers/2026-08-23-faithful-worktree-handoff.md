# Handoff — R114 measured out, spec written, and a probe that changes the economics

**Topic:** the arc / M19 · **Date:** 2026-08-23 · **Branch:** `the-faithful-worktree` @ `f0f5ce3`
(one commit off `main` @ `8523462`) · **Runner:** `./.venv/bin/python`, never `python3`.
**Shape: originating, stopped at 156k** — the spec is written; the *reconsideration* it now needs
is deliberately not done here (§5).

> ## ⚠ READ THIS FIRST — the spec on this branch is ABANDONED, and this file is the record of why
>
> The loop was specced, then killed at spec stage by its own measurement. **Read §3bis, then §7,
> then §5.** §1, §3 and §4 describe the superseded design and are kept only because their
> *measurements* are sound and re-derivable — their *conclusions* are not.
>
> **The one-line outcome:** R114's cause is misnamed. Making `etkl:01`'s oracle *run* (materialise
> the corpus) leaves it *un-ablatable*, because the editable-install `.pth` pins `src/iladub/` to
> the main tree — so the corpus half of the design buys **zero** edges. Raised as [[R121]].
>
> **Nothing was implemented. No plan was written. The §6 CI ruling should be reversed.**

## §1 Goal (as originally framed — superseded, see §3bis)

Close [[R114]] — `etkl:01`'s oracle cannot execute in an M19 ablation worktree — by making the
worktree a faithful environment, then re-reading `etkl:01`'s ends for dependency edges.

## §2 Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-23-the-faithful-worktree-design.md` | **the spec** — §1 the root cause, §2 every measurement with its command, §3 proposer/disposer, §4 the design, §5 why no new M-number, §6 the CI ruling, §8 what it does not do, §9 falsifications, §10 done, §11 two record corrections, Appendix the six rejected designs |
| `docs/superpowers/residues-open.md`, rows R113–R120 | the previous loop's seven residues. **R113 is the one that binds this work**, not R114 — see §4 |
| `tests/test_arc_ablation.py` | M19: `_ablate:253`, worktree at `:263`, `_scores:214-250`, the arms at `:334-367`, the four stated limitations at `:68-111` |
| `tests/arc-manifest.ttl` | the 43 criteria; the `etkl` rung at `:149-232`; the 6 asserted + 22 proposed edges at the foot |
| `docs/superpowers/2026-08-22-arc-edges-close-handoff.md` | the previous loop's close — §C's four spec corrections and §E's definition-of-done audit |
| `.github/workflows/ci.yml:22-26` | one job, `pytest -q`, no `-m` filter, generates `baml_client`, **never fetches corpus** |
| **§4 below** | the probe, its numbers, and the script that regenerates them |

## §3 What was decided, and where each decision is recorded

| decision | recorded where | status |
| --- | --- | --- |
| R114 is one face of *"the ablation worktree is not a faithful environment"*; three faces, failing in three directions | spec §1, §2.1 | **settled by measurement** |
| Materialise by **copy**, never symlink — `_ablate` unlinks declared artifacts, and through a symlink that deletes the main tree's irreplaceable corpus | spec §4.1 | settled (argument is measured; **no code written**) |
| Demand for an environment input is **discovered by the control run**, not declared in a mapping table | spec §4.3 | **decided against the author's own first instinct**; nowhere but the spec — reversible |
| The environment declaration lives in the instrument, **not** in `arc-manifest.ttl` | spec §4.2 | settled by Global Constraint 4 (`arc-manifest.ttl:16-18`) |
| No new M-number; a control failure and a disjointness collision are **instrument failures**, not membrane refusals | spec §5 | **spec only — and under adversarial attack, see §6** |
| CI fetches the corpus in a **dedicated job**, cached on the tracked sha256 pins; the existing job unchanged | spec §6 | **maintainer ruling, 2026-08-23**, recorded in the spec. Reversible — no workflow written |
| The `etkl` rung can never be internally assertable (all seven share one artifact ⇒ A6) | spec §2.4 | **settled by measurement**; R114's remedy column does not know this |
| Maintainer chose "fetch corpus in CI" **over the author's recommendation** of declaring capability in the graph | this file, and the spec's Appendix | settled as a ruling; the *reason it was right* is in §6 below |

**Nothing has been implemented.** The branch contains the spec and this file. No test, no workflow,
no change to `test_arc_ablation.py`.

## §3bis CORRECTION, same day — §4's probe answered the wrong question; the yield is ZERO

**Raised by an adversarial review, verified independently before being recorded here.** §4 below
is left standing because its *method* is sound and its file list is accurate; its **conclusion is
wrong**, and this section supersedes it.

§4's probe ran in the **main tree**. It established which files the compile *opens* — it never
established whether deleting one in a **worktree** would change anything. It cannot: the oracle
does not resolve `vocab/` relative to its own checkout. It resolves it through the editable
install, from `src/iladub/`, which the `.pth` pins to the main tree:

- `src/iladub/etkl/compile.py:374-383` — `_repo_vocab()` walks up from `os.path.abspath(__file__)`
- `src/iladub/etkl/gridregion.py:29-31` and seven sibling modules — `Path(__file__).resolve().parents[3] / "vocab" / …`

Measured in a worktree with **the entire `vocab/` tree deleted**:

```
cwd            : …/scratchpad/wt-verify
_repo_vocab()  : /Volumes/WD Green/dev/git/iladub/vocab
GRID_REGION_RQ : /Volumes/WD Green/dev/git/iladub/vocab/queries/grid-region.rq
  exists?      : True
=> resolves to WORKTREE? False
```

**Consequence.** All 8 of §4's "can ground" candidates declare `vocab/` files. Arm 1 grounds only
if deleting `Y`'s artifact makes `etkl:01`'s oracle **FAIL** — and the deletion is invisible to it.
Every one of the 8 refutes, `etkl:01 → dec:06` included. **The measured yield of the corpus/CI
half is zero edges, not one.**

**The root cause of R114 is therefore misnamed.** It is not the gitignored corpus; it is the
`.pth` shadow that makes every `vocab/` artifact un-ablatable for any oracle reaching it through
library code. The corpus fix makes the oracle *run*; nothing in this spec makes it *ablatable*.

**Scope of the shadow — the shipped graph is NOT affected.** `tests/test_boundary.py:6` and its
siblings derive their root from the **test file's** `__file__`, which in a worktree is the
worktree. That is why the 6 asserted edges grounded, and it is self-evidencing: an edge that
grounded is an edge whose oracle was ablation-sensitive. In the met set, `etkl:01` is the **only**
oracle that reaches its evidence through `src/iladub/`.

**What this invalidates in the spec:** §2.3's existence proof (it retired "does it run?", not "is
it ablatable?"), §2.1's dismissal of F3 as latent (the test *"zero declared artifacts under
`src/`"* is the wrong test; the right one is *"does the oracle resolve the artifact through a
main-tree-rooted path?"*, and by it **8 of the 29 declared files are un-ablatable**), §7, §9's
headline, and DoD items 1, 7, 8, 10.

---

## §4 The probe — the measurement that changes the economics

> **Superseded by §3bis.** The file list below is accurate and re-derivable; the yield conclusion
> it draws is wrong. Read §3bis first.

Taken **after** the spec was committed; the spec does not contain it. One traced compile answers
all 15 candidate pairs at once, because an edge `etkl:01 → Y` can only ground if the compile
actually reads one of `Y`'s declared artifacts.

```python
# scratch, run from the repo root with ./.venv/bin/python — embedded here rather than
# committed to scripts/ so the numbers below are re-derivable from committed bytes
# without adding maintained surface (this is [[R120]]'s lesson applied).
import sys, os, json
from pathlib import Path
REPO = Path("/Volumes/WD Green/dev/git/iladub")
opened = set()
def hook(event, args):
    if event == "open":
        p = args[0]
        if isinstance(p, (str, bytes, os.PathLike)):
            try:
                rp = Path(os.fsdecode(p)).resolve()
                if str(rp).startswith(str(REPO)):
                    opened.add(str(rp.relative_to(REPO)))
            except Exception:
                pass
sys.addaudithook(hook)
from iladub.etkl.document import compile_document
rep = compile_document(str(REPO / "corpus/ag-trade/graincorp-stem-2026-07-31.pdf"))
print("score=", rep.score)
print(sorted(f for f in opened if f.split("/")[0] in ("vocab", "examples", "tests")))
```

**Result** (164.19 s):

```
compile returned: DocumentReport score= 0.9654553611484971
repo files opened under vocab/ examples/ tests/ : 28
```

All 28 are under `vocab/` — **5 ontologies, 18 queries, 5 shapes. Zero under `examples/`, zero
under `tests/`.** The score is `0.9654` against `cor:scoreFloor 0.95` — **a margin of 0.0154**,
which matters, because arm 1 needs the test to *fail* when `Y`'s file is removed.

Cross-referenced against the manifest:

| | count | |
| --- | --- | --- |
| A4-legal `etkl:01 → Y` candidates | 15 | all met `dec:*` (11) + all met `holon:*` (4) |
| …whose declared artifact the compile **opens** | **8** | `dec:01 03 04 05 06 07 08 10` |
| …that it never opens | 7 | `dec:11 14 16`, `holon:01 02 03 04` |
| A4-legal `X → etkl:01` | 1 | `tab:06` only (near-certainly empty) |

**And then R113 collapses the 8:**

```
vocab/shapes/dec-shapes.ttl            declared by 4: dec:01 dec:03 dec:04 dec:05
vocab/shapes/escalation-shapes.ttl     declared by 1: dec:06
vocab/shapes/iladub-shapes.ttl         declared by 3: dec:07 dec:08 dec:10
```

Ablating `dec-shapes.ttl` is evidence for four criteria at once and `iladub-shapes.ttl` for three
— the exact ambiguity that made the previous loop decline to author `dec:09 → dec:07/08/10` at
all (`2026-08-22-arc-edges-authored.md` §1, rejected reading 6). By that precedent:

> **The expected yield of the whole corpus/CI half is ONE asserted edge: `etkl:01 → dec:06`.**
> The binding constraint is [[R113]] (file-granularity ablation), which this loop does not touch —
> **not** [[R114]], which it does.

**A second finding, independent of every edge and free:** the graincorp compile opens **zero**
`holon` artifacts. The previous loop argued at rung scope that *"`etkl` needs a minimal holon
substrate to compile into"* and could not ground it at criterion scope. Measured: at criterion
scope it does not reproduce. That belongs in the record whatever happens to this loop.

## §5 Unverified or assumed — not empty

1. **"Opens the file" is necessary, not sufficient.** Arm 1 grounds only if deleting `Y`'s
   artifact makes `test_expected_verdict` **fail**. A compile that opens `dec-shapes.ttl` but
   tolerates its absence, or degrades without dropping below the 0.95 floor, refutes the edge.
   **Nobody has run a single real ablation.** The 8 is an upper bound on the 15; the 1 is an upper
   bound on the 8.
2. **The 164 s figure is one measurement of one document on one machine**, twice (164.37 s under
   the symlink probe, 164.19 s under the audit-hook probe). No cold-cache or CI-hardware figure
   exists.
3. **The CI job's wall-clock and pass/fail delta are unmeasured** — spec §10.7 is a MEASURE box,
   and §2.5's *209 tests across 14 modules* is an envelope of what changes state, **not** a count
   of tests that currently skip. Establishing the latter needs a corpus-absent full run.
4. **The cache does not solve rot.** It reduces exposure from every CI run to every cache miss
   (GitHub evicts at 7 days; any pin change invalidates the key). And the failure cannot be made
   soft: `continue-on-error` on the fetch leaves `corpus/` absent, the oracle skips, M19 cannot
   ground, and the job goes red anyway — **R114 re-entering by the door this loop closed.**
5. **Corpus rot can silently redefine a met criterion.** When a shipping stem is republished, the
   options are drop the job or re-pin `cor:sha256` — and re-pinning makes `etkl:01`'s `met true`
   rest on a different document than the one adjudicated 2026-08-03
   (`tests/corpus-manifest.ttl:37-43`). Same objection the spec's Appendix raises against a
   synthetic stand-in, arriving by attrition instead of by decision.
6. **The spec's option set was single-sourced.** The same reading framed the alternatives,
   recommended among them, and wrote the spec. The maintainer overrode exactly one — and that
   override caught a real defect (§6). An adversarial review was dispatched at the end of this
   session; **its findings are not in this file.**

## §6 The one place the author was wrong, recorded because it is the useful part

The author recommended *"declare capability in the graph"* (a `prog:requiresEnvironment` term,
grading an unrunnable edge down to a proposition). The maintainer chose the CI fetch instead. The
override was correct on two counts, both discovered afterwards:

- It was **R114's remedy (c) with better manners** — it ships no asserted `etkl` edge ever, and
  R114's own last column argues (a)/(b) are worth more than (c).
- It **contradicts spec §4.2**, written later by the same author, which argues that an environment
  fact must not go in `arc-manifest.ttl` because it is not a claim about the arc. The recommended
  option would have put exactly that there.

Recorded so the next session trusts the spec's *measurements* more than its *recommendations*.

## §7 The next concrete action

**Do not write a plan from this spec.** §3bis removes its reason for existing. The three actions,
in order:

1. **Ship the instrument-only slice.** The control run, the disjointness guard, [[R118]]'s
   **general** form (read the ERROR's exception, not merely its existence), `baml_client`-only
   materialisation, and the two record corrections in spec §11. Costs **no** corpus, **no** CI
   job, **no** 164 s — and measured, `baml_client` alone takes the worktree from *1293 collected,
   6 errors* to *1314 collected, 0 errors*; the corpus contributes nothing to that.
2. **Re-file R114** with its true cause: the `.pth` shadow, not the gitignored corpus. It gates
   the whole `etkl` rung, and the remedy is the guard `test_arc_ablation.py:109-111` already
   prescribes plus a per-worktree install or a vocab-root injection point.
3. **Reverse the §6 CI ruling.** It was requested and granted against an unmeasured yield that is
   in fact zero. Nothing should be built on it.

Do this in a **fresh session**, reading §3bis and §5 of this file first, then the spec cold.

**Three further blockers the adversarial review measured**, not repeated here in full and worth
reading before any implementation: (i) spec §5's claim that the terminal-width skip test survives
is false — `_SKIPS_WITH_A_REASON` is a **bare** node id that fans out to all 7 corpus documents
once a corpus is materialised, turning that test red and ~11 minutes long on any corpus-present
machine; (ii) spec §6's containment fails — `tests/test_arc_ablation.py` carries no `pytestmark`
and CI runs a bare `pytest -q`, so an asserted `etkl` edge makes the **default** job raise, not
the new one; (iii) §2.5's *209* is the sum of module totals, and the real corpus-gated envelope is
`43` deselected by `-m corpus` plus ~35 static skipifs — a number the spec spent to reject an
architecture in its Appendix without measuring.
