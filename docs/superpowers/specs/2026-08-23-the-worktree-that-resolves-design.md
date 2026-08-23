# The worktree that resolves — closing R121, and making M19 refuse to judge what it cannot see

**Date:** 2026-08-23 · **Topic:** the arc / M19 · **Supersedes:**
`docs/superpowers/specs/2026-08-23-the-faithful-worktree-design.md`, abandoned at spec stage by
its own correction (`docs/superpowers/2026-08-23-faithful-worktree-handoff.md` §3bis).
**Runner:** `./.venv/bin/python`, never `python3`.

**Doc impact:** none — no CI job, no workflow change, no published assertion changes, no
`prog:met` value moves. The change is confined to `tests/test_arc_ablation.py` and its docstring.
`CLAUDE.md` gains nothing; the wiki gains nothing; no contradiction with a released artifact.

> **What this supersedes, in one line.** The abandoned spec bought a corpus fetch and a CI job to
> make `etkl:01`'s oracle *run*, and its own probe then measured the yield of that purchase at
> **zero edges** — because making an oracle run does not make it *ablatable*. This spec fixes
> what actually blocks ablation, costs no corpus, no CI job and no 164 s, and predicts **zero new
> edges** up front rather than discovering it afterwards.

---

## §1 The question

M19 (`tests/test_arc_ablation.py`) grounds a dependency edge `X → Y` by deleting `Y`'s declared
`prog:oracleArtifact` in a throwaway worktree and observing whether `X`'s oracle fails. The
instrument is only as good as the worktree: **an oracle that cannot run there, or that reads its
evidence from somewhere the deletion never touched, produces an outcome that grounds nothing.**

Two independent defects break exactly that, and the previous loop conflated them:

| | defect | consequence | filed as |
| --- | --- | --- | --- |
| **D1** | `baml_client/` is gitignored and generated, so **6** modules ERROR at collection in any worktree | arm 1 reads an unrelated import break as consumption — *permissive* | [[R118]] |
| **D2** | the editable-install `.pth` pins `src/iladub/` to the **main tree**, so any oracle reaching its evidence through library code is blind to the worktree's deletions | arm 1 reads an invisible deletion as non-consumption — a **silent false refutation** | [[R121]] |

D2 is the one the previous loop misnamed as D3-the-gitignored-corpus, and it is the one that
gates the `etkl` rung.

## §2 What is measured before anything is designed

Every claim below carries the command that produced it. Run 2026-08-23 on `main` @ `b03efb6`;
the working tree was `git status --porcelain`-clean before and after.

### §2.1 The editable install is a plain path `.pth`, not a meta-path finder

```
$ cat .venv/lib/python3.12/site-packages/_editable_impl_iladub.pth
/Volumes/WD Green/dev/git/iladub/src
```

**This is the load-bearing fact of the whole spec.** A setuptools ≥64 finder-based editable
install registers a `MetaPathFinder`, which takes precedence over `sys.path` and therefore over
`PYTHONPATH`; a plain path `.pth` appends to `sys.path` during `site` processing, *after*
`PYTHONPATH`. The remedy in §4.1 works only in the second case, and this is the second case.
**An implementer who finds this file changed has found the spec's premise broken** — say so, do
not work around it.

### §2.2 `PYTHONPATH=<wt>/src` re-roots the library into the worktree

```
$ git worktree add --detach $WT HEAD
$ cd $WT && PYTHONPATH=$WT/src …/iladub/.venv/bin/python -c "…"
iladub.__file__ : $WT/src/iladub/__init__.py
_repo_vocab()   : $WT/vocab
GRID_REGION_RQ  : $WT/vocab/queries/grid-region.rq
=> worktree?    : True
```

Both resolution styles re-root: `_repo_vocab()` (`src/iladub/etkl/compile.py:374-383`, walks up
from `os.path.abspath(__file__)`) and the module-constant style
(`src/iladub/etkl/gridregion.py:29-31` and seven siblings,
`Path(__file__).resolve().parents[3] / "vocab" / …`).

### §2.3 And the result is ablation-sensitive — the property that actually matters

```
$ rm -f $WT/vocab/queries/grid-region.rq
$ cd $WT && PYTHONPATH=$WT/src …/python -c "from iladub.etkl import gridregion as g; print(g.GRID_REGION_RQ.exists())"
path   : $WT/vocab/queries/grid-region.rq
exists : False
```

This is the measurement the abandoned spec's §2.3 never made. Its existence proof retired the
question *"does the oracle run?"* and left *"is the oracle ablatable?"* unasked — which is why its
probe answered the wrong question and its yield was zero.

### §2.4 Limitation 4 already documents D2 — and dismisses it by the wrong test

`tests/test_arc_ablation.py:87-99` states the `.pth` shadow with a correct reproduction, then:

> *"**No live impact today, and that too is measured:** all 35 distinct `prog:oracleArtifact`
> values … live under `vocab/` (14), `examples/` (12) and `tests/` (9) — **zero** under `src/`."*

**The test is wrong twice.**

1. *Wrong question.* The hazard is not an artifact **under** `src/`; it is an artifact **resolved
   through** `src/`. By the right test — *does the consuming oracle reach this file through
   library code?* — **8 of the 29 declared artifact files are un-ablatable**
   (`2026-08-23-faithful-worktree-handoff.md` §3bis).
2. *Wrong census.* 35 is not the file count. Measured over all 43 criteria with
   `graph.objects()`: **29** distinct files — `tests` 9, `examples` 12, `vocab` **8**, `src/` 0;
   48 raw `prog:oracleArtifact` triples. The `14` is `vocab/`'s *triple* count, so the citation
   mixes one namespace counted as triples with two counted as files. This is [[R120]]'s shape —
   a load-bearing number in shipped source that nobody could re-derive — one file over from
   where R120 found it.

The **conclusion** limitation 4 draws (that no edge shipped so far is affected) survives, but for
a different reason than the one written: the 6 asserted edges grounded because their oracles root
their evidence in the **test file's** `__file__`, which in a worktree *is* the worktree
(`tests/test_boundary.py:6` and siblings). That is self-evidencing — an edge that grounded is an
edge whose oracle was ablation-sensitive.

### §2.5 The corpus must NOT be materialised, and this is measured, not preferred

`_SKIPS_WITH_A_REASON = "tests/test_corpus.py::test_expected_verdict"`
(`tests/test_arc_ablation.py:434`) is a **bare** node id, invoked at `:460` inside M19's own
parser self-test as `_ablate([], [_SKIPS_WITH_A_REASON])`. It relies on receiving a **skip**. The
moment a corpus exists in the worktree, that bare id fans out to all 7 corpus documents, the
self-test goes red, and the run costs ~11 minutes on any corpus-present machine.

**Therefore the declared environment inputs are `baml_client/` and nothing else** (§4.2), and
the maintainer's CI-fetch ruling of 2026-08-23 is **reversed** (§7).

### §2.6 D1's remedy, already measured

`baml_client/` alone takes the worktree from *1293 collected, 6 errors* to *1314 collected, 0
errors*; the corpus contributes nothing to that
(`2026-08-23-faithful-worktree-handoff.md` §7 item 1). `.gitignore:30` carries `/baml_client` —
repo root, so a copy lands at `<wt>/baml_client` and resolves through `cwd=wt`.
**MEASURE before writing the assertion**: re-derive both numbers in the worktree the shipped
`_ablate` creates; do not carry them from the handoff.

## §3 What proposes, what disposes, and why they are independent

| | |
| --- | --- |
| **Proposition** | *"This worktree is an environment in which every endpoint oracle runs, and in which every declared artifact is reachable-and-removable by the oracle that consumes it."* |
| **Disposer** | **An un-ablated control run.** In a materialised worktree with **nothing** deleted, every endpoint oracle id must report `PASSED`. |
| **Independent?** | **Yes.** The control inspects no materialisation logic, no input list and no path. It asks one question — *does this oracle pass here when nothing was taken away?* — and `SKIPPED`, `ERROR` and `FAILED` answer it identically: the environment is not faithful, and nothing measured in it grounds anything. |

The control would have caught D1 and D3-the-corpus without knowing either existed. **It would not
have caught D2**, and that asymmetry is the reason §4.1 exists: an invisible deletion passes the
control by construction. Prevention and disposal are doing different jobs here; neither replaces
the other.

**Consequence, stated up front:** an oracle that fails the control is an **instrument failure**,
not evidence. It raises with the transcript — as an unresolved node id already does
(`tests/test_arc_ablation.py:243-249`) — and is never scored.

## §4 The design — five changes to `tests/test_arc_ablation.py`, no new M-number

State the invariants; the bodies are the implementer's (CLAUDE.md § Plan authoring rule 1).

### §4.1 Worktree-rooted library resolution (closes [[R121]])

`_run_module` (`:197`) runs its subprocess with an environment whose `PYTHONPATH` has `<cwd>/src`
**prepended** (preserving any inherited value). Invariants:

- `sys.executable` stays as it is — absolute, and unaffected by the worktree having no `.venv`.
- The re-rooting applies to **every** `_run_module` call, including `_ablate([], …)` at `:460`.
- Nothing else about the invocation changes.

**Named seam, not answered here:** `_run_module`'s subprocess currently passes no `env=` at all
and inherits. Measure what the inherited environment already carries in `PYTHONPATH` before
deciding how to prepend.

### §4.2 Materialisation of declared environment inputs — by copy, never by symlink

`_ablate` (`:253`) gains a step between `git worktree add` (`:263`) and the first `unlink()`
(`:273`): copy each declared environment input that exists in the main tree into the worktree.

- **The declared set is `baml_client/`. It is not the corpus** (§2.5).
- **Copy, not symlink.** `_ablate`'s job is to *delete declared artifacts*; through a symlinked
  directory `Path.unlink()` deletes the real file in the main tree. The implementer must not
  "optimise" this back to a symlink.
- **Best effort.** An input absent from the main tree is **not an error** — it is not copied.
  Demand is *discovered* by the control run (§4.3), never declared in a mapping table.
- **The declaration lives in the instrument, not in `tests/arc-manifest.ttl`** — Global Constraint
  4 (`tests/arc-manifest.ttl:16-18`, *code never writes this file*), and more fundamentally
  *"this repo's test environment needs a generated client"* is not a claim about the arc.

### §4.3 The control run — and the one place it must NOT go

Invariants:

1. It runs **in `ablation_refusals` (`:291`)**, once per invocation, over the **union** of
   endpoint oracle ids — **never inside `_ablate`**. `_ablate([], [_SKIPS_WITH_A_REASON])` at
   `:460` depends on receiving a **skip**; a control inside `_ablate` turns M19's own parser
   self-test into an instrument failure (§2.5).
2. One control worktree serves every endpoint: create once, materialise once, run the union,
   tear down. It deletes nothing.
3. Any requested id not `PASSED` ⇒ `RuntimeError` carrying the transcript, the failing id, its
   outcome, **and which declared inputs were and were not materialised** — so a developer who
   has never generated a `baml_client` gets an actionable sentence, not a bare red.
4. Ablation and scoring then proceed unchanged.

Cost today: one worktree + the union of 6 asserted edges' endpoint oracles. No `etkl` end exists
(A6 — §6), so no 164 s enters the suite.

### §4.4 The disjointness invariant

> **The set of materialised paths and the set of ablatable artifact paths must be disjoint.**

A producer-side guard raising **before** the first worktree is created, naming the colliding path.
Not a comment, not a test-only assertion (CLAUDE.md § Producer-side guards, R89).

It holds vacuously today — 29 artifact files under `tests/` (9), `examples/` (12), `vocab/` (8),
none under `baml_client/`. **That vacuity is the reason to enforce it:** the day someone declares
a `prog:oracleArtifact` under a materialised path, the materialiser restores what the ablation
just deleted and **every arm-1 run goes silently green**. A false-assertion path is closed by a
raise, not by the observation that nobody has done it yet.

### §4.5 [[R118]]'s general form — read the exception, not its existence

`_scores` (`:214`) currently scores a collection ERROR as `FAILED` whenever the module appears in
`_COLLECT_ERROR` (`:171,224`) — so *any* import break reads as consumption of the removed
artifact. Materialising `baml_client` removes the **live** instance; it does not remove the rule.

Invariant: **a collection ERROR is ablation evidence only if its exception names the removed
artifact.** Anything else is an instrument failure and raises.

**Named seam, measure before writing:** `_run_module` passes `--tb=no` (`:206`), so the exception
text is not in `proc.stdout` today. Establish what pytest actually prints for a collection error
under each candidate flag (`-rE`, `--tb=line`, `--tb=short`) **before** choosing the rule's input;
do not assume a format. This is evidence-positive by construction — a name present, never a name
inferred from absence (CLAUDE.md § the AXIOM split).

## §5 The probe — run once, shipped as evidence, not as machinery

Under the control run, install a `sys.addaudithook` recording repo-file `open` events whose
resolved path lies **outside the worktree** and **outside `.venv/`**, and report the set.

- Before §4.1 this predicate is useless: every oracle imports `iladub` from the main tree, so it
  fires universally. After §4.1 it is sharp.
- **Run it once, over the oracles that can run in a worktree.** If the set is empty, ship an
  assertion and no machinery. If it is non-empty, raise a residue row with the transcript and
  ship no machinery **this** loop.
- This is what turns limitation 4's F3 from *declared latent* into *measured*. The abandoned
  spec declared it; nobody had measured it.

YAGNI is deliberate: a permanent hook is instrument surface guarding a hazard with zero known
live instances once §4.1 lands. Measure first; build only against a finding.

## §6 Why no new M-number

`tests/arc-shapes.ttl` gains nothing.

| kind | means | mechanism | home |
| --- | --- | --- | --- |
| **refusal** | the graph asserts something the evidence will not support | a message, collected and returned | `arc-shapes.ttl` (M12–M18) / `test_arc_ablation.py` (M19) |
| **instrument failure** | the instrument cannot judge at all | `RuntimeError` with the transcript | `test_arc_ablation.py` only |

A control failure, a disjointness collision and an unattributable collection ERROR are all the
second kind. None of them is a claim about the arc.

## §7 Corrections to the record this loop owes

1. **Limitation 4's docstring** (`tests/test_arc_ablation.py:87-111`): `35` → `29` with the
   per-directory census corrected (`vocab` 8, not 14), **and** the dismissal reasoning replaced —
   the right test is *"does the consuming oracle resolve this artifact through library code?"*,
   not *"does this artifact live under `src/`?"* (§2.4). Correcting only the number leaves the
   defect.
2. **The §6 CI ruling of the abandoned spec is REVERSED.** It was requested and granted against an
   unmeasured yield that is in fact zero. No corpus fetch, no second CI job, no cache, no
   `cor:sha256` re-pinning exposure. Recorded here so the reversal is discoverable from the
   ruling.
3. **[[R121]]'s row** gains the remedy measured in §2.1–§2.3 and its closure evidence
   (`~~R121~~`, per CLAUDE.md § the register).
4. **[[R114]]'s row**: its remedy column still argues from the gitignored corpus. Its cause was
   corrected 2026-08-23; the remedy column has not been.

## §8 The falsifying oracles — one per shipped rule, all mandatory

Per CLAUDE.md § Plan authoring rule 4, each ships with the test failing, restored, and the suite
green.

1. **Remove the `PYTHONPATH` env from `_run_module`** → the test pinning worktree-rooted
   resolution goes red. Cheap, no corpus, directly assertable (§2.2 is the assertion).
2. **Delete the materialisation step** → the control run goes red **naming the missing input**,
   and the ablation does not proceed.
3. **Declare a `prog:oracleArtifact` under `baml_client/` in a fixture** → the guard raises
   **before** any worktree is created. If it raises later, or not at all, §4.4 is prose.
4. **Point a declared input at a path absent from the main tree** → materialisation stays silent
   and the control still passes, because no endpoint needed it. If this raises, the design is
   declared-demand, not discovered-demand.
5. **Break a module's collection for a reason unrelated to the removed artifact** → scored as an
   instrument failure, not `FAILED`.

**What a real failure of this spec looks like**, stated so it is recognised rather than explained
away: §4.1 lands, the ablation runs, and no edge changes state — leaving an instrument that is
honest and a graph that is identical. **That outcome is expected (§10) and must be reported
as-is.** The unacceptable outcome is an edge asserted or refuted on an arm whose control was never
checked.

## §9 Definition of done

1. §4.1–§4.5 implemented, each with its §8 falsification evidence.
2. **`ablation_refusals` over the LIVE manifest re-run, and its result reported whatever it is.**
   §4.1 changes what oracles can see: a pair that refuted because the deletion was invisible may
   now ground. If the live result is no longer `[]`, that is a **finding**, not a regression to be
   suppressed — report it and stop for a maintainer ruling.
3. `pytest --collect-only -q` inside a worktree created by the shipped `_ablate` reports **0**
   collection errors, re-derived there (from 6 — §2.6).
4. The §5 probe run once, its result in the loop's evidence, and a residue row if non-empty.
5. The four §7 corrections landed **in the tracked artifacts**, not only in this spec.
6. The real tree `git status --porcelain`-clean before and after every M19 run.
7. Every number this spec cites re-derived by the implementer at implementation time. §2.6's
   1293/1314 and §2.4's 29 are the two carried from elsewhere; both are marked MEASURE.

## §10 What this loop does NOT do

- **It asserts no new edge, and predicts zero.** `etkl:01` is the only met oracle reaching
  evidence through `src/iladub/`, and it still cannot run without a corpus this loop does not
  materialise. §4.1 closes the defect structurally, with no live yield today. Stated as a
  prediction up front so it cannot be reported later as a disappointment.
- **It does not make the `etkl` rung internally assertable** — A6 forbids it permanently (all
  seven criteria share one artifact).
- **It does not close** [[R113]] (file-granularity ablation — still the binding constraint on
  yield), [[R115]], [[R116]], [[R117]], [[R119]], [[R120]].
- **It fetches no corpus, adds no CI job, changes no workflow, and moves no `prog:met` value.**
- **It ships no permanent hermeticity machinery** — §5 is a measurement, not a component.

## §11 Provenance of the abandoned spec — what is reused and what is discarded

| from `2026-08-23-the-faithful-worktree-design.md` | here |
| --- | --- |
| §3 proposer/disposer (the control run) | **reused**, §3 — with the D2 asymmetry it did not state |
| §4.1 copy-never-symlink | **reused**, §4.2 |
| §4.3 discovered-demand, no mapping table | **reused**, §4.2 |
| §4.4 disjointness | **reused**, §4.4 |
| §4.5 one control worktree | **reused**, §4.3 |
| §5 no new M-number | **reused**, §6 |
| §11.1/§11.2 record corrections | **reused and extended**, §7 |
| §2.3 the feasibility probe | **discarded** — retired the wrong question |
| §2.5 CI census (209), §6 the CI job, the corpus half | **discarded and reversed**, §2.5 + §7.2 |
| §7 the reading, §9 headline, DoD 1/7/8/10 | **discarded** — all rest on the zero-yield purchase |
| Appendix's six rejected designs | **standing** — not re-derived here; read them there |
