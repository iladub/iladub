# The worktree that resolves — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make M19's ablation worktree resolve the library it is ablating (closing [[R121]]),
refuse to judge in an environment it has not first proved faithful, and stop reading an
unattributable collection ERROR as consumption — without fetching a corpus, adding a CI job, or
asserting a single new edge.

**Architecture:** Five changes, all inside `tests/test_arc_ablation.py`, plus one new committed
probe module. `_run_module` prepends `<cwd>/src` to the subprocess `PYTHONPATH` so the editable
install stops shadowing the checkout under test; `_ablate` copies the one declared environment
input (`baml_client/`) into the worktree and refuses a declared artifact that collides with it;
`ablation_refusals` runs one un-ablated **control** over the union of endpoint oracles and raises
if any is not `PASSED`; `_scores` requires a collection ERROR's exception to name a removed path
before scoring it as evidence.

**Tech Stack:** Python 3.12, pytest 9.0.3, rdflib, `git worktree`. Runner is
`./.venv/bin/python`, never `python3`.

**Spec:** `docs/superpowers/specs/2026-08-23-the-worktree-that-resolves-design.md` (approved
2026-08-23). Read it before Task 1. Its §9 (*what this loop does NOT do*) is binding on every
test in this plan — see § Rule-5 reconciliation below.

**Doc impact:** none. No CI job, no workflow change, no `prog:met` value moves, no published
assertion changes. Carried from spec § header.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **Runner:** `./.venv/bin/python -m pytest`. **NEVER `python3`** — it carries rdflib 7.1.4 and
   no pyrudof, and M19's subprocesses inherit `sys.executable`.
2. **The real tree is never mutated.** `git status --porcelain` must be empty before and after
   every M19 run. Every deletion happens inside a worktree; `git worktree remove --force` runs in
   a `finally`.
3. **No tuned constant, threshold, tolerance or subprocess timeout** (CLAUDE.md §8). A wall-clock
   number here is prima facie evidence of a misclassified decision.
4. **Code never writes `tests/arc-manifest.ttl`** (Global Constraint 4 of the arc,
   `tests/arc-manifest.ttl:16-18`). M19 returns refusals for a hand to resolve in a reviewed
   commit.
5. **No new M-number.** `tests/arc-shapes.ttl` gains nothing. A control failure, a disjointness
   collision and an unattributable collection ERROR are *instrument failures* — `RuntimeError`
   with the transcript — not refusals (spec §5).
6. **The corpus is NOT materialised** and no CI job is added. The abandoned spec's CI ruling is
   reversed (spec §2.5, §6 item 2). Measured hazard, re-derived for this plan below.
7. **Copy, never symlink.** `_ablate`'s job is to delete files; through a symlinked directory
   `Path.unlink()` deletes the real file in the main tree.
8. **Falsification is mandatory, per task** (CLAUDE.md § Plan authoring rule 4). Each task report
   carries a `## FALSIFICATION` block: remove or invert the thing the new test pins, show it
   **failing**, restore, show green. No falsification evidence ⇒ the task review fails.
9. **This loop asserts no new edge.** A newly grounding pair is RECORDED AS A FINDING and
   authored in a later loop (spec §8 item 2). Suppressing such a result, or re-tuning the
   instrument until `[]` comes back, is the one forbidden response.

---

## Measurements taken while writing this plan

Every load-bearing claim below was re-derived on branch `the-worktree-that-resolves` @ `8f4f115`
on **2026-08-23**, with the command inline (CLAUDE.md § Plan authoring rule 2). The real tree was
`git status --porcelain`-clean before and after each. **Nothing in this plan is quoted from the
spec or from a prior handoff without being re-run here**, except the two named seams, which are
left unmeasured on purpose (§ Named seams).

### M1 — The spec's premise: the editable install is a plain path `.pth` (spec §2.1)

```
$ ls .venv/lib/python3.12/site-packages/*.pth
-rw-r--r--  1 …  36 Jul  4 07:32 .venv/lib/python3.12/site-packages/_editable_impl_iladub.pth
$ cat .venv/lib/python3.12/site-packages/_editable_impl_iladub.pth
/Volumes/WD Green/dev/git/iladub/src
$ ls .venv/lib/python3.12/site-packages/ | grep -i editable
_editable_impl_iladub.pth
```

One `.pth`, 36 bytes, one absolute path, and **no `__editable___*_finder` module** — so no
`MetaPathFinder` is registered and `PYTHONPATH` still wins. Confirms spec §2.1. **Task 1 pins
this as a property rather than a file** — see Task 1's rationale.

### M2 — The artifact census (spec §2.4 — the number limitation 4 gets wrong)

```
$ ./.venv/bin/python -c "<rdflib over tests/arc-manifest.ttl, _LINE_SUFFIX-stripped>"
raw prog:oracleArtifact triples: 48
distinct artifact FILES (line suffix stripped): 29
per top dir: Counter({'examples': 12, 'tests': 9, 'vocab': 8})
criteria carrying an artifact: 24     oracle_rows total criteria: 43
under src/: []
```

**29** distinct files — `examples` 12, `tests` 9, `vocab` **8**, `src/` **0**; **48** raw triples.
The docstring's `35 … vocab (14), examples (12), tests (9)` is wrong twice, exactly as spec §2.4
says: `35` is neither the file count nor the triple count, and `14` is `vocab/`'s *triple* count
mixed into a file census. Task 5 corrects it.

The exact reproduction command is preserved in Task 5, Step 1.

### M3 — The worktree collection census, before the change (spec §2.6)

Built with the same command `_ablate` uses (`git worktree add --detach <wt> HEAD`):

```
$ git worktree add --detach $WT HEAD
$ cd $WT && …/iladub/.venv/bin/python -m pytest --collect-only -q -p no:cacheprovider
ERROR tests/test_extract_baml.py
ERROR tests/test_loop.py
ERROR tests/test_m4_databook.py
ERROR tests/test_m4_pipeline.py
ERROR tests/test_targeted.py
ERROR tests/test_to_rdf.py
!!!!!!!!!!!!!!!!!! Interrupted: 6 errors during collection !!!!!!!!!!!!!!!!!!
1293 tests collected, 6 errors in 3.43s
```

**1293 collected, 6 errors** — re-derived, not carried. The 6 modules are named above.
The same transcript also re-derives **[[R121]]'s shadow for free**:

```
tests/test_to_rdf.py:4: in <module>
    from iladub.extract_baml import OfferExtraction, CodedConcept
/Volumes/WD Green/dev/git/iladub/src/iladub/extract_baml.py:8: in <module>
```

A test file **inside the worktree** importing a library file **from the main tree**. That is D2,
printed by pytest, in a worktree nobody instrumented.

### M4 — The remedy, and that the two halves compose

```
$ cp -R baml_client $WT/baml_client        # 27 files; .gitignore:30 carries `/baml_client`
$ cd $WT && …/python -m pytest --collect-only -q -p no:cacheprovider
1314 tests collected in 2.81s                                   # A: no PYTHONPATH
$ cd $WT && PYTHONPATH=$WT/src …/python -m pytest --collect-only -q -p no:cacheprovider
1314 tests collected in 1.15s                                   # B: with PYTHONPATH
$ cd $WT && PYTHONPATH=$WT/src …/python -c "import iladub; print(iladub.__file__)"
/tmp/arc-m19-plann2Qx/wt/src/iladub/__init__.py                 # C: re-rooted
```

**1293/6 → 1314/0 on `baml_client` alone** (spec §2.6 re-derived), and `PYTHONPATH=<wt>/src`
re-roots the library **without changing the collection count**. §4.1 and §4.2 compose; neither
regresses the other.

### M5 — The corpus hazard is LIVE on this machine (spec §2.5)

```
$ ls -d corpus && find corpus -maxdepth 2 -name '*.pdf' | wc -l
corpus
7
$ cd $WT && PYTHONPATH=$WT/src COLUMNS=250 …/python -m pytest \
      tests/test_corpus.py::test_expected_verdict -v --tb=no -p no:cacheprovider
tests/test_corpus.py::test_expected_verdict[ag-trade/graincorp-capacity-2026-08-04.pdf] SKIPPED (…)
… 5 more …
7 skipped in 0.08s
```

The main tree **has** the 7 corpus PDFs. The bare id `_SKIPS_WITH_A_REASON`
(`tests/test_arc_ablation.py:434`, used at `:460`) fans out to **7** parametrized ids. All 7 skip
inside the worktree because `corpus/` is gitignored — which is what M19's own parser self-test
depends on receiving. **Materialising the corpus would turn that self-test red on this machine
today.** Global Constraint 6 is a measurement, not a preference.

The same transcript shows the post-change environment (`baml_client` copied, `PYTHONPATH` set)
leaves the self-test's skip **unchanged** — Task 1 and Task 2 do not disturb `:460`.

### M6 — The control run passes today, and what it costs

The union of endpoint oracle ids over the 6 asserted edges, in a worktree with `baml_client`
copied and `PYTHONPATH=<wt>/src`, **nothing deleted**:

```
$ ./.venv/bin/python -c "<asserted_edges + _oracles over the live manifest>"
asserted edges: 6
   criterion:dec:06 -> criterion:dec:01
   criterion:dec:16 -> criterion:holon:01
   criterion:holon:03 -> criterion:holon:01
   criterion:holon:04 -> criterion:dec:07
   criterion:holon:04 -> criterion:dec:10
   criterion:holon:04 -> criterion:holon:01
endpoint criteria: 8
union of endpoint oracle ids: 10   across 4 modules
$ cd $WT && PYTHONPATH=$WT/src …/python -m pytest <the 10 ids> -v --tb=no -p no:cacheprovider
10 passed in 0.52 s
```

**The control is green today** — so Task 3 lands without a red suite, and any future red is a
real environment defect. The 10 ids are:

```
tests/test_boundary.py::test_leak_rejected
tests/test_boundary.py::test_promotion_grounds
tests/test_boundary.py::test_proposal_wellformed
tests/test_escalation_shacl.py::test_escalation_conformant_passes
tests/test_escalation_shacl.py::test_escalation_leak_fails
tests/test_hga_alignment.py::test_governed_grounding_conformant
tests/test_hga_alignment.py::test_holons_module_standalone
tests/test_hga_alignment.py::test_ungoverned_grounding_rejected
tests/test_vocab_shapes.py::test_hol_decision_conformant
tests/test_vocab_shapes.py::test_hol_rubber_stamp_rejected
```

**0.52 s is one combined invocation. `_ablate` splits by module (`:281-286`), so the shipped
control is 4 subprocess startups, not 1 — re-measure it, do not carry 0.52 s.**

### M7 — A NEW record defect this plan found: `9 endpoint criteria` is stale

`tests/test_arc_ablation.py:485` states *"MEASURED 2026-08-22 over those 6 edges: **9** endpoint
criteria, 6.69 s"*. M6 measures **8** over those 6 edges. Nine is the *seven*-edge figure — it
includes `holon:02`, whose edge the same docstring says two lines earlier was **deleted**. The
sentence is internally inconsistent: it names 6 edges and reports the 7-edge endpoint count.

This is [[R120]]'s shape again, in the same docstring, and it was not in the spec. Task 5 owns
it as a fifth record correction.

### M8 — The probe's three resolution styles all import cheaply

```
$ time ./.venv/bin/python -c "import iladub; from iladub.etkl import gridregion as g; \
      from iladub.etkl.compile import _repo_vocab; print(iladub.__file__, g.GRID_REGION_RQ, _repo_vocab())"
/Volumes/WD Green/dev/git/iladub/src/iladub/__init__.py
/Volumes/WD Green/dev/git/iladub/vocab/queries/grid-region.rq
/Volumes/WD Green/dev/git/iladub/vocab
0.20s user 0.08s system — 0.579 total
```

`src/iladub/etkl/gridregion.py:29` (`Path(__file__).resolve().parents[3] / "vocab" / …`) and
`src/iladub/etkl/compile.py:374-382` (`_repo_vocab()`, walks up from `os.path.abspath(__file__)`)
are the two resolution styles spec §2.2 names. Both import without a BAML client and without a
corpus. `vocab/queries/grid-region.rq` is **tracked at HEAD** (`git cat-file -e
HEAD:vocab/queries/grid-region.rq` → exit 0), so it exists in every worktree and is ablatable.

### M9 — The register's tally, for the rows Task 6 raises

```
$ grep -c '^| R' docs/superpowers/residues.md      -> 111
$ grep -c '^| R[0-9]* | closed' …/residues.md      ->  22
$ grep -c '^| R[0-9]* | open'   …/residues.md      ->  89
```

**22/111 closed at plan time.** The next row is **R122**. Re-run these two greps at raise time —
the snapshot goes in the row's parentheses and is never updated afterwards.

### M10 — `pyproject.toml` pytest config (why `<wt>/src` is not already on the path)

```
$ grep -n "pythonpath\|addopts\|testpaths\|\[tool.pytest" pyproject.toml
96:[tool.pytest.ini_options]
97:testpaths = ["tests"]
98:pythonpath = ["."]
```

`pythonpath = ["."]` adds the **rootdir** — the worktree root — never `<wt>/src`. That is why
`import iladub` inside a worktree falls through to the `.pth`. **`addopts` is absent**, so
[[R119]]'s undeclared assumption still holds; this plan does not touch it.

---

## Named seams — measure these BEFORE writing the call, not after

Two facts this plan deliberately does **not** supply. Each is a place where an assumption would
become a defect. Measure, record the measurement in the task report, then write the code.

**S1 — What `_run_module`'s subprocess already inherits in `PYTHONPATH` (Task 1).**
`_run_module:203-206` passes **no `env=` at all** today, so the subprocess inherits the parent's
environment wholesale. Nobody has looked at what `PYTHONPATH` already carries when M19 runs
under `pytest`, under CI, or under a developer shell. **Measure it in all three shapes you can
reach before deciding how to prepend** — the invariant is *prepend, preserving any inherited
value*, and "preserving" cannot be written correctly against an unexamined value (is it unset? a
single `.`? a colon-list?). Do not assume `os.environ.get("PYTHONPATH", "")` is empty.

**S2 — Which pytest flag puts a collection ERROR's exception in `proc.stdout` (Task 4).**
`_run_module:205` passes `--tb=no`, so today the exception text is absent and `_COLLECT_ERROR`
(`:171`) matches only `^ERROR (\S+)` — the bare module path. The module docstring at `:169-170`
*claims* the summary form is `ERROR tests/x.py - FileNotFoundError: …`. **That claim is a
candidate, not a measurement: confirm or refute it.** Establish what pytest 9.0.3 actually
prints for a collection error under each of `-rE`, `--tb=line`, `--tb=short` **before** choosing
the rule's input, and record the transcripts. Note that `--collect-only -q` (which M3 used) is a
*different invocation* from `-v --tb=no` and its output is **not** evidence about this seam.

Both seams are named rather than answered on purpose (CLAUDE.md § Plan authoring rule 3).

---

## File Structure

| file | responsibility | change |
| --- | --- | --- |
| `tests/test_arc_ablation.py` | M19: the instrument | modified — §4.1–§4.5 + docstring corrections |
| `tests/test_arc_worktree_probe.py` | **new**: a committed test that asserts the library resolves to *this* checkout | created (Task 1) |
| `tests/arc-m19-materialised-artifact.ttl` | **new**: negative fixture declaring a `prog:oracleArtifact` under a materialised path | created (Task 2) |
| `tests/arc-m19-control-fails.ttl` | **new**: fixture whose edge endpoint's only oracle cannot execute in a worktree | created (Task 3) |
| `docs/superpowers/residues.md` / `residues-open.md` / `residues-closed.md` | the register | modified (Task 6) |

**Why a separate probe module.** The property §4.1 ships — *the library resolves to the checkout
under test* — is only observable **inside** a worktree, in a subprocess. `_ablate` can only run
committed pytest node ids, so the observation has to be a committed test. In the main tree it
passes trivially (rootdir *is* the main tree); its purpose is to be runnable **elsewhere**. State
that in its docstring so a future reader does not delete it as vacuous.

---

## Interfaces

Stated as signatures and invariants. **Bodies are the implementer's** (CLAUDE.md § Plan authoring
rule 1).

| name | signature | notes |
| --- | --- | --- |
| `_MATERIALISED` | `tuple[str, ...]` | repo-root-relative declared environment inputs. **Value: `("baml_client",)`** and nothing else (Global Constraint 6). |
| `_declared_inputs` | `(repo: Path) -> tuple[list[str], list[str]]` | pure partition of `_MATERIALISED` into *(present in the main tree, absent)*. No filesystem writes. Used by the control's error message. |
| `_materialise` | `(wt: Path, repo: Path) -> None` | copies each present input into `wt`. Copy, never symlink. An absent input is **not an error**. |
| `_refuse_materialisation_collision` | `(removed_files: Iterable[str]) -> None` | raises `RuntimeError` naming the colliding path if any removed path lies under any `_MATERIALISED` entry. |
| `_run_module` | `(node_ids, cwd) -> (proc, reported)` | **signature unchanged**; gains an `env=` whose `PYTHONPATH` has `<cwd>/src` prepended (S1). |
| `_scores` | `(module, node_ids, proc, reported, removed) -> dict` | **gains `removed`** — the paths deleted in this worktree — so §4.5's rule can ask whether the exception names one. |
| `_ablate` | `(removed_files, node_ids, repo=REPO) -> dict` | **return type unchanged.** Gains: the collision guard *before* `git worktree add`; `_materialise` *between* `git worktree add` (`:263`) and the first `unlink()` (`:273`); passes `removed_files` through to `_scores`. |
| `ablation_refusals` | `(graph) -> list[str]` | **signature unchanged.** Gains: the collision guard over the union of endpoint artifacts *before the first worktree*, then the control run, then the ablation loop unchanged. |

**Guard placement, and why it is in two places.** §7 oracle 3 requires the collision to raise
*before any worktree is created*, which only the `ablation_refusals` placement satisfies (by the
time `_ablate` sees a colliding criterion, earlier criteria have already had worktrees). But
`_ablate` is reachable directly — `:460`, Task 1's and Task 2's tests, any future caller — so it
guards its own argument too. CLAUDE.md § *Producer-side guards vs the membrane*: total coverage
of `_ablate`'s callers by `ablation_refusals` is **not** provable, so the second call earns its
place. It is one helper called twice, not two implementations.

**The control's shape.** The control is `_ablate([], <union of endpoint oracle ids>)` — nothing
deleted, so `_ablate` materialises and runs but removes nothing — with the **verdict check in
`ablation_refusals`**. No control logic goes inside `_ablate` (§4.3 invariant 1): `_ablate([],
[_SKIPS_WITH_A_REASON])` at `:460` depends on receiving a **skip**, and a control inside `_ablate`
would turn M19's own parser self-test into an instrument failure. One worktree, one teardown.

---

## Task ordering and the one cross-task interaction

Tasks land 1 → 6. **Task 4 changes what Task 2's falsification looks like**, and this must not
surprise the implementer:

Task 2's falsification removes the copy step and observes that a `baml_client`-dependent oracle
id does **not** come back `PASSED`. *Before* Task 4 it comes back `FAILED` (the collection-ERROR
branch at `_scores:200-204`). *After* Task 4 the same removal makes it **raise**, because the
exception names no removed path. **Write Task 2's assertion as "not `PASSED`", never as
"`== FAILED`"** — the weaker form is the true invariant and survives Task 4. If you land Task 4
first, say so in the report and record the raise instead.

---

## Rule-5 reconciliation — every plan-supplied test against spec §9

CLAUDE.md § Plan authoring rule 5: a plan-supplied test asserting behaviour the spec scoped
**out** is a contradiction. Checked, one by one:

| test | spec §9 says NOT to… | reconciled |
| --- | --- | --- |
| Task 1 probe + `_ablate` round trip | *"ships no hermeticity machinery, permanent or one-shot"* | **Not machinery.** §9 declines the *audit* — *"is anything else still resolving to the main tree?"*. This pins the one path §4.1 ships and §2.2 measured. It sweeps nothing and enumerates nothing. It is spec §7 oracle 1, which §7 makes **mandatory**. |
| Task 2 materialisation test | *"fetches no corpus"* | Asserts `baml_client` only. The corpus is never named. M5 is the measured reason. |
| Task 3 control test | *"asserts no new edge"* | The control reads outcomes and raises; it writes no triple and returns no refusal. |
| Task 4 unattributable-ERROR test | *"does not close [[R118]]"* — §9 lists R115–R120 as **not closed**, and R118 is **not** in that list | R118 **is** in scope (spec §4.5 is titled *"R118's general form"*). No contradiction. |
| Task 6 live run | *"asserts no new edge, and predicts zero"* | Reports the result **as-is** and files a finding row. It authors nothing. Global Constraint 9. |
| — | *"does not make the `etkl` rung internally assertable"* | No task touches `etkl:01`, the corpus, or A6. |
| — | *"does not close [[R113]]"* | No task changes ablation granularity from file to line. |

**Setup reachability** (rule 5's extension of rule 2 to the test's *setup*): every state these
tests need was constructed for real while writing this plan — M1, M3, M4, M5, M6, M8. The one
setup **not** constructed is Task 2's fixture graph declaring an artifact under `baml_client/`;
it is a hand-written `.ttl` in the same shape as the existing `tests/arc-m19-false-edge-leak.ttl`
(`FIXTURE`, `:139`), which `validate_manifest` already parses. **Task 2 Step 1 measures that the
fixture is SHACL-clean before relying on it** — if the membrane refuses it, the guard is never
reached and the test proves nothing.

---

## Task 1: Worktree-rooted library resolution (spec §4.1 — closes [[R121]])

**Files:**
- Create: `tests/test_arc_worktree_probe.py`
- Modify: `tests/test_arc_ablation.py:197-212` (`_run_module`)
- Test: `tests/test_arc_ablation.py` (new test, placed **before**
  `test_m19_the_live_manifest_carries_no_refuted_edge` at `:474` so a broken premise is red
  above the live gate in the report)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `_run_module` with a worktree-rooted `PYTHONPATH`; the node id
  `tests/test_arc_worktree_probe.py::test_library_resolves_to_this_checkout`, which Tasks 2–4 may
  reuse as a cheap in-worktree observation point.

**Why the probe pins a property, not the `.pth` file.** The maintainer's caveat is that nothing
tests whether `_editable_impl_iladub.pth` is still a *plain path* `.pth`; if setuptools ever
emits a finder-based editable install instead, a registered `MetaPathFinder` outranks
`sys.path`, `PYTHONPATH` stops winning, and **§4.1 fails silently** — the worst failure available
to this design. Inspecting the `.pth` file would pin the wrong thing: it is venv-layout-specific,
absent under a wheel install, and would go red for reasons that are not the hazard. The probe
asserts the **consequence** instead — *does the library resolve to this checkout?* — and a
finder-based install flips it red for the right reason, in the right words. Spec §2.1 says an
implementer who finds the premise broken has found the spec's premise broken and must **say so,
not work around it**; the probe's failure message must say exactly that.

- [ ] **Step 1: Measure seam S1 before touching `_run_module`**

Record `PYTHONPATH` as `_run_module`'s subprocess would inherit it — at minimum from a shell,
and from inside a pytest run of `tests/test_arc_ablation.py`. Put the transcripts in the task
report. Do not proceed to Step 3 without them.

- [ ] **Step 2: Write the probe module (this is the new committed test — verbatim)**

Create `tests/test_arc_worktree_probe.py`:

```python
"""A committed observation point for M19: does the library resolve to THIS checkout?

M19 ablates by deleting files inside a `git worktree`. That only grounds anything if the code
under test reads its evidence from the worktree — and the editable install makes that a real
question, not a given: `.venv/…/site-packages/_editable_impl_iladub.pth` carries the MAIN tree's
`src/`, so without `PYTHONPATH=<wt>/src` an `import iladub` inside a worktree resolves to the
main tree ([[R121]], `tests/test_arc_ablation.py` limitation 4).

The property is only observable INSIDE a worktree, in a subprocess, so the observation has to be
a committed node id `_ablate` can run. **In the main tree this passes trivially — rootdir IS the
main tree — and that is not a reason to delete it.** Its job is to be runnable elsewhere;
`tests/test_arc_ablation.py::test_m19_resolves_the_library_into_the_worktree_it_ablates` is the
caller that gives it teeth.

Anchored on `pytestconfig.rootpath`, never `Path.cwd()`: rootdir is the worktree when pytest is
invoked with `cwd=<wt>` (`_run_module`), and stays correct for a developer running pytest from a
subdirectory, which `cwd` would not.

All three resolution styles in `src/iladub/` are checked, because §4.1 must re-root all of them:
  * the package itself (`iladub.__file__`);
  * a module constant (`gridregion.GRID_REGION_RQ`, `Path(__file__).resolve().parents[3] / …`,
    the style used by eight modules);
  * a walk-up (`iladub.etkl.compile._repo_vocab()`).
"""
from pathlib import Path

import iladub
from iladub.etkl import gridregion
from iladub.etkl.compile import _repo_vocab

_PREMISE = (
    "the library did not resolve to the checkout under test. If this fails inside an M19 "
    "worktree, the ablation is measuring the MAIN tree and grounds nothing (R121). If the "
    "editable install has become finder-based (a `__editable___*_finder` module rather than a "
    "plain path `_editable_impl_iladub.pth`), a MetaPathFinder now outranks PYTHONPATH and the "
    "spec's premise (2026-08-23-the-worktree-that-resolves-design.md §2.1) is BROKEN — say so, "
    "do not work around it"
)


def test_library_resolves_to_this_checkout(pytestconfig):
    root = Path(pytestconfig.rootpath).resolve()

    pkg = Path(iladub.__file__).resolve()
    assert pkg.is_relative_to(root), f"{_PREMISE}: iladub is {pkg}, rootdir is {root}"

    rq = gridregion.GRID_REGION_RQ.resolve()
    assert rq.is_relative_to(root), f"{_PREMISE}: GRID_REGION_RQ is {rq}, rootdir is {root}"
    assert rq.is_file(), (
        f"{rq} is missing from this checkout — the ablation-sensitivity leg of "
        f"test_m19_resolves_the_library_into_the_worktree_it_ablates deletes exactly this file, "
        f"so its absence here means the probe can no longer tell ablated from un-ablated"
    )

    vocab = Path(_repo_vocab()).resolve()
    assert vocab.is_relative_to(root), f"{_PREMISE}: _repo_vocab() is {vocab}, rootdir is {root}"
```

- [ ] **Step 3: Write the failing M19 test (verbatim)**

Add to `tests/test_arc_ablation.py`, immediately before
`test_m19_the_live_manifest_carries_no_refuted_edge`:

```python
_PROBE = "tests/test_arc_worktree_probe.py::test_library_resolves_to_this_checkout"


def test_m19_resolves_the_library_into_the_worktree_it_ablates():
    """[[R121]]: the ablation must edit the tree the oracles actually read.

    Two legs, and the second is the one the abandoned spec never measured:

      1. **It resolves.** In an un-ablated worktree the probe PASSES, so `import iladub` and both
         `vocab/`-resolution styles land inside the checkout under test rather than in the main
         tree the editable install pins.
      2. **And it is ABLATION-SENSITIVE.** Deleting a `vocab/` file that library code resolves
         makes the probe FAIL. Resolution alone is not the property M19 needs — an oracle that
         runs but cannot see the deletion produces a silent false refutation — so the deletion
         must be *observable through library code*.

    Run through the SHIPPED `_ablate`, not a hand-built worktree: leg 2 depends on the ordering
    of `git worktree add` -> materialise -> `unlink()`, and a hand-built probe proves the
    mechanism without proving the mechanism survives materialisation.
    """
    assert _ablate([], [_PROBE])[_PROBE] == PASSED, (
        "the library did not resolve into an un-ablated M19 worktree — every ablation this "
        "module performs is reading the main tree (R121)"
    )

    ablated = _ablate(["vocab/queries/grid-region.rq"], [_PROBE])[_PROBE]
    assert ablated == FAILED, (
        f"a vocab/ file deleted inside the worktree was still visible to library code: the "
        f"probe scored {ablated!r}, not {FAILED!r}. Resolution without ablation-sensitivity is "
        f"the silent false refutation R121 names"
    )
```

- [ ] **Step 4: Run it and watch it fail**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py::test_m19_resolves_the_library_into_the_worktree_it_ablates -v`

Expected: **FAIL on the first assertion** — without §4.1 the probe resolves `iladub` to the main
tree inside the worktree, so it comes back `FAILED`, not `PASSED`. Paste the transcript.

- [ ] **Step 5: Implement §4.1 in `_run_module`**

Give the subprocess an explicit `env` whose `PYTHONPATH` has `<cwd>/src` **prepended**, preserving
whatever S1 measured. Invariants (spec §4.1):

- `sys.executable` stays as it is — absolute, unaffected by the worktree having no `.venv`.
- The re-rooting applies to **every** `_run_module` call, including `_ablate([], …)` at `:460`.
- Nothing else about the invocation changes: same argv, same `--tb=no`, same
  `-p no:cacheprovider`, same `cwd`.
- `cwd` is a `Path` at every call site — check before assuming string concatenation.

No body here. Write it against the S1 transcript.

- [ ] **Step 6: Run the test, then the whole module**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py -v`
Expected: PASS, including `test_m19_reads_a_skip_that_carries_its_reason_at_any_terminal_width`
(M5 measured that §4.1 leaves its skip unchanged — confirm, do not assume).

- [ ] **Step 7: Confirm the real tree is untouched**

Run: `git status --porcelain` (Global Constraint 2). Expected: only the two files this task edits.

- [ ] **Step 8: FALSIFICATION (spec §7 oracle 1)**

Remove the `env=` from `_run_module`, run the new test, show it **failing on leg 1**; restore;
show `tests/test_arc_ablation.py` green. Paste both transcripts under `## FALSIFICATION`.

- [ ] **Step 9: Commit**

```bash
git add tests/test_arc_worktree_probe.py tests/test_arc_ablation.py
git commit -m "M19: resolve the library into the worktree it ablates (closes R121)"
```

---

## Task 2: Materialise `baml_client`, and refuse a collision (spec §4.2 + §4.4)

**Files:**
- Modify: `tests/test_arc_ablation.py` — `_ablate:253-289`, new module constant + two helpers
- Create: `tests/arc-m19-materialised-artifact.ttl`
- Test: `tests/test_arc_ablation.py` (two new tests)

**Interfaces:**
- Consumes: Task 1's `_ablate` (unchanged signature).
- Produces: `_MATERIALISED`, `_declared_inputs(repo)`, `_materialise(wt, repo)`,
  `_refuse_materialisation_collision(removed_files)` — Task 3 consumes `_declared_inputs` for the
  control's error message.

**Why these two ship together.** The disjointness invariant is *about* the materialised set: it
has no subject until materialisation exists, and materialisation without it is the exact
false-green §4.4 names — the materialiser restoring what the ablation just deleted, and every
arm-1 run going silently green. A reviewer cannot meaningfully accept one and reject the other.

- [ ] **Step 1: Build the collision fixture and prove the membrane admits it**

Create `tests/arc-m19-materialised-artifact.ttl` in the shape of `tests/arc-m19-false-edge-leak.ttl`
(`FIXTURE`, `tests/test_arc_ablation.py:139`), declaring on an edge **endpoint** criterion a
`prog:oracleArtifact` under `baml_client/`.

Then measure: `validate_manifest(<the fixture>)` must return `ok == True`. **If the membrane
refuses the fixture, the guard is never reached and the test proves nothing** — say so and fix
the fixture, exactly as `test_m19_an_edge_the_membrane_admits_and_the_ablation_refutes:383-385`
already insists for its own fixture. Record the result in the task report.

- [ ] **Step 2: Write the two failing tests (verbatim)**

```python
_MATERIALISED_PROBE = "tests/test_to_rdf.py::test_groundable_abo_becomes_asserted_literal"
MATERIALISED_FIXTURE = REPO / "tests" / "arc-m19-materialised-artifact.ttl"


def test_m19_materialises_the_generated_client_it_did_not_check_out():
    """`baml_client/` is gitignored and generated, so no worktree at HEAD contains it.

    MEASURED 2026-08-23 in a worktree built with `_ablate`'s own `git worktree add --detach <wt>
    HEAD`: `pytest --collect-only -q` reports **1293 tests collected, 6 errors** — six modules
    (`test_extract_baml`, `test_loop`, `test_m4_databook`, `test_m4_pipeline`, `test_targeted`,
    `test_to_rdf`) cannot import `baml_client` — and **1314 collected, 0 errors** once the
    directory is copied in. That import break has NO relation to any removed artifact, so an
    oracle in one of those modules would read as consumption of a file M19 never touched
    ([[R118]]).

    Asserted as *not* PASSED rather than *equal to* FAILED on the falsification side, because
    §4.5 (Task 4) turns the unattributable ERROR from a score into a raise. The invariant that
    survives both is: **with the client materialised the oracle runs; without it, it does not
    come back PASSED.**
    """
    assert _ablate([], [_MATERIALISED_PROBE])[_MATERIALISED_PROBE] == PASSED, (
        "a module that needs the generated BAML client did not run in an M19 worktree; every "
        "collection ERROR it raises there is an instrument artefact, not ablation evidence"
    )


def test_m19_refuses_an_artifact_that_materialisation_would_restore():
    """THE DISJOINTNESS INVARIANT — vacuous today, and that is precisely why it is enforced.

    Measured 2026-08-23 over the live manifest: 29 distinct declared `prog:oracleArtifact` files
    — `examples/` 12, `tests/` 9, `vocab/` 8 — and **none** under `baml_client/`. The day someone
    declares one there, `_materialise` copies the file back in **after** `_ablate` deleted it,
    the oracle passes on evidence that was never removed, and arm 1 goes SILENTLY green. A
    false-assertion path is closed by a raise, not by the observation that nobody has done it yet
    (CLAUDE.md § Producer-side guards vs the membrane).

    It must raise BEFORE any worktree exists: by the time `_ablate` reaches the colliding
    criterion, earlier criteria have already had worktrees created and torn down, and a guard
    that fires there is a guard that fired late.
    """
    fixture = Graph().parse(MATERIALISED_FIXTURE, format="turtle")
    ok, report = validate_manifest(MATERIALISED_FIXTURE)
    assert ok, (f"{MATERIALISED_FIXTURE.name} must be SHACL-clean so that only the guard can "
                f"refuse it; the graph membrane already objects:\n{report}")

    with mock.patch("tests.test_arc_ablation._ablate") as never:
        with pytest.raises(RuntimeError, match="baml_client"):
            ablation_refusals(fixture)
    assert not never.called, (
        "the disjointness guard fired only once _ablate had already been entered; it must "
        "refuse before the first worktree is created"
    )
```

- [ ] **Step 3: Run both and watch them fail**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py -k "materialis" -v`
Expected: the first FAILS (the module errors at collection in the worktree, so it scores
`FAILED`, or raises once Task 4 has landed); the second FAILS with `DID NOT RAISE`. Paste both.

- [ ] **Step 4: Implement §4.2 and §4.4**

Invariants (spec §4.2, §4.4), no bodies:

- `_MATERIALISED = ("baml_client",)`. **Not the corpus** — M5 measured that materialising it fans
  `_SKIPS_WITH_A_REASON` out to 7 parametrized ids and turns M19's own parser self-test red on
  any corpus-present machine.
- The declaration lives **in the instrument**, never in `tests/arc-manifest.ttl` (Global
  Constraint 4): *"this repo's test environment needs a generated client"* is not a claim about
  the arc.
- **Copy, never symlink** (Global Constraint 7). Do not "optimise" this later.
- **Best effort:** an input absent from the main tree is not an error and is not copied. Demand
  is *discovered* by Task 3's control, never declared in a mapping table.
- Materialisation happens **between** `git worktree add` (`:263`) and the first `unlink()`
  (`:273`) — so a declared artifact deleted after materialisation stays deleted, and the guard
  makes that ordering unobservable anyway.
- The collision guard runs at the top of `ablation_refusals` over the union of every endpoint's
  artifacts **and** at the top of `_ablate` over its own argument. See § Interfaces for why both.
- The guard's message names the colliding path **and** the `_MATERIALISED` entry it collides with.

- [ ] **Step 5: Run the module green**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py -v` — expected PASS throughout.

- [ ] **Step 6: FALSIFICATION (spec §7 oracles 2-part, 3 and 4)**

Three inversions, each with its failing transcript, restore, and green suite:

1. **Delete the materialisation call** → `test_m19_materialises_the_generated_client_it_did_not_check_out`
   goes red (the probe id is not `PASSED`).
2. **Point `_MATERIALISED` at a path absent from the main tree** (e.g. `("no_such_dir",)`) →
   materialisation stays **silent**, `_ablate` still runs, and
   `test_m19_reads_a_skip_that_carries_its_reason_at_any_terminal_width` still passes. **If this
   raises, the design has become declared-demand instead of discovered-demand** — spec §7 oracle
   4. (Its control half lands in Task 3; record here that the ablate path stayed silent.)
3. **Remove the collision guard** → `test_m19_refuses_an_artifact_that_materialisation_would_restore`
   goes red with `DID NOT RAISE`. Then **move the guard so it fires inside `_ablate` only** and
   show the test still red on `never.called` — this is what proves "before the first worktree",
   which a `pytest.raises` alone does not.

- [ ] **Step 7: Confirm `git status --porcelain` shows only this task's files. Commit**

```bash
git add tests/test_arc_ablation.py tests/arc-m19-materialised-artifact.ttl
git commit -m "M19: materialise declared environment inputs, and refuse an artifact they would restore"
```

---

## Task 3: The un-ablated control run (spec §4.3)

**Files:**
- Modify: `tests/test_arc_ablation.py` — `ablation_refusals:291-367`
- Create: `tests/arc-m19-control-fails.ttl`, bound to the module constant
  `CONTROL_FAILS_FIXTURE = REPO / "tests" / "arc-m19-control-fails.ttl"` beside `FIXTURE` (`:139`)
- Test: `tests/test_arc_ablation.py` (one new test)

**Interfaces:**
- Consumes: Task 2's `_declared_inputs(repo)`; Task 1's re-rooted `_run_module`.
- Produces: no new public name. `ablation_refusals`'s signature and return type are unchanged.

**What the control is for, and what it cannot do.** It disposes the proposition *"this worktree is
an environment in which every endpoint oracle runs"* by asking one question — *does this oracle
pass here when nothing was taken away?* — and `SKIPPED`, `ERROR` and `FAILED` all answer it
identically: the environment is not faithful and nothing measured in it grounds anything. It
inspects no materialisation logic, no input list and no path, which is what makes it independent
of §4.2 (spec §3). **It would have caught D1 and the corpus without knowing either existed. It
would NOT have caught D2** — an invisible deletion passes the control by construction — which is
why Task 1 exists and why neither replaces the other.

- [ ] **Step 1: Write the failing test (verbatim)**

```python
def test_m19_refuses_to_score_in_an_environment_it_has_not_proved_faithful():
    """THE CONTROL: before any deletion, every endpoint oracle must PASS with nothing removed.

    An oracle that fails an UN-ABLATED run is an instrument failure, not evidence (spec §3): its
    outcome under ablation says nothing about the removed artifact, because it did not pass
    without it either. So it raises with the transcript — the same shape `_scores:219-226`
    already uses for an unresolved node id — and is never scored.

    MEASURED 2026-08-23 over the live manifest: 6 asserted edges, 8 endpoint criteria, a union of
    10 endpoint oracle ids across 4 modules, all 10 PASSED in an un-ablated worktree with
    `baml_client` materialised. **The control is green today**, so this test pins the refusal, not
    a live failure — it forges the failure by handing `ablation_refusals` a graph whose endpoint
    oracle is a node id that cannot pass in a worktree.

    `tests/test_corpus.py::test_expected_verdict` is that id: `corpus/` is gitignored and this
    loop deliberately does not materialise it (spec §2.5), so all 7 of its parametrized ids SKIP
    in every worktree M19 creates — measured, not assumed. A SKIP is not a PASS, so the control
    must refuse rather than let the edge be scored on an oracle that never executed.

    The message must name the failing id, its outcome, AND which declared inputs were and were
    not materialised (§4.3 invariant 3) — a developer who has never generated a `baml_client`
    needs an actionable sentence, not a bare red.
    """
    live = Graph().parse(MANIFEST, format="turtle")
    edges = asserted_edges(live)
    assert edges, "the live manifest carries no asserted edge, so this test has no endpoint"

    with pytest.raises(RuntimeError) as caught:
        ablation_refusals(Graph().parse(CONTROL_FAILS_FIXTURE, format="turtle"))

    message = str(caught.value)
    assert "tests/test_corpus.py::test_expected_verdict" in message, message
    assert "SKIPPED" in message, (
        f"the control must say WHAT pytest reported, so a reader can tell a skip from a "
        f"failure: {message}"
    )
    assert "baml_client" in message, (
        f"the control must report which declared environment inputs were materialised, so a "
        f"developer without a generated client gets an actionable sentence: {message}"
    )
```

**Setup note for the implementer (rule 2, extended to the setup).** `CONTROL_FAILS_FIXTURE` names
`tests/arc-m19-control-fails.ttl`, a new fixture graph you must build in Step 1: an edge whose endpoint criterion's only
`prog:oracleTest` is `tests/test_corpus.py::test_expected_verdict`. **`etkl:01` already carries
exactly that oracle in the live manifest** (`tests/arc-manifest.ttl:158`, per [[R114]]'s row) —
so the cheapest fixture is the live manifest plus one asserted edge with `etkl:01` at an end.
**MEASURE that this is still true before writing the fixture**; if `etkl:01`'s oracle has moved,
find the current skipping id rather than inventing one. Then confirm the fixture is SHACL-clean
with `validate_manifest`, as in Task 2 Step 1 — if the membrane refuses it, the control is never
reached.

- [ ] **Step 2: Run it and watch it fail**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py::test_m19_refuses_to_score_in_an_environment_it_has_not_proved_faithful -v`
Expected: FAIL — no control exists, so `ablation_refusals` returns a *"cannot judge"* refusal
string instead of raising. Paste it.

- [ ] **Step 3: Implement §4.3**

Invariants (spec §4.3), no bodies:

1. The control runs **in `ablation_refusals`**, once per invocation, over the **union** of
   endpoint oracle ids — **never inside `_ablate`**. `_ablate([], [_SKIPS_WITH_A_REASON])` at
   `:460` depends on receiving a skip; a control inside `_ablate` turns M19's own parser
   self-test into an instrument failure.
2. **One** control worktree serves every endpoint: create once, materialise once, run the union,
   tear down. It deletes nothing. `_ablate([], <union>)` is that worktree.
3. It runs **after** the two existing producer-side guards (`:311`, `:329`) and the collision
   guard, and **before** the ablation loop at `:338`.
4. Any requested id not `PASSED` ⇒ `RuntimeError` carrying the transcript, the failing id, its
   outcome, and the `_declared_inputs` partition.
5. An edge set that is empty still returns `[]` at `:301-302` **without** creating a control
   worktree — the early return stays first.
6. Ablation and scoring then proceed unchanged.

- [ ] **Step 4: Run the module, then measure the control's real cost**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py -v`
Then time `test_m19_the_live_manifest_carries_no_refuted_edge` and report the delta. **Do not
carry M6's 0.52 s** — that was one combined invocation and `_ablate` splits by module (`:281`),
so expect 4 subprocess startups. Record what you measure.

- [ ] **Step 5: FALSIFICATION (spec §7 oracles 2 and 4)**

1. **Delete the materialisation step from Task 2** → this control test's *sibling* behaviour
   changes: run `test_m19_the_live_manifest_carries_no_refuted_edge` and show the control raising
   and **naming the missing input**, with the ablation not proceeding. Restore; green.
2. **Point `_MATERIALISED` at a path absent from the main tree** → materialisation stays silent
   **and the control still passes**, because no endpoint needed it. If this raises, the design is
   declared-demand, not discovered-demand (spec §7 oracle 4) — report it as a design defect, do
   not weaken the test.
3. **Remove the control** → `test_m19_refuses_to_score_in_an_environment_it_has_not_proved_faithful`
   goes red. Restore; green.

- [ ] **Step 6: `git status --porcelain`, then commit**

```bash
git add tests/test_arc_ablation.py tests/arc-m19-*.ttl
git commit -m "M19: refuse to score in an environment it has not proved faithful"
```

---

## Task 4: A collection ERROR is evidence only if it names the removed artifact (spec §4.5, [[R118]])

**Files:**
- Modify: `tests/test_arc_ablation.py` — `_run_module:203-206`, `_COLLECT_ERROR:171`,
  `_scores:214-251`, `_ablate:283-285` (the `_scores` call site)
- Test: `tests/test_arc_ablation.py` (one new test)

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: `_scores(module, node_ids, proc, reported, removed)` — **the new fifth parameter**.
  `_ablate` is the only caller (`:284`); grep before you assume that.

**The defect.** `_scores:199` sets `collect_error` from the bare `^ERROR <module>` summary line and
`:200-204` scores **every** requested id of that module `FAILED`. Arm 1 refuses an edge only when
**all** of X's results are `PASSED` (`:346`), so a `FAILED` **admits**. The intended reading is
right — a module that cannot import once its artifact is gone is genuine consumption — but the
instrument cannot separate that from an import break with no relation to the removed file.
Materialising `baml_client` removed the *live* instance; it did not remove the rule.

**The invariant:** a collection ERROR is ablation evidence **only if its exception names one of
the removed paths**. Anything else is an instrument failure and raises. This is evidence-positive
by construction — a name **present**, never a name inferred from absence (CLAUDE.md § the AXIOM
split, §7).

- [ ] **Step 1: Measure seam S2 — do not skip this**

Establish what pytest 9.0.3 actually prints for a collection error under `-rE`, `--tb=line` and
`--tb=short`, in the `-v -p no:cacheprovider` invocation `_run_module` uses. Build the case by
deleting a real artifact a module imports at module scope. Record every transcript in the task
report, then choose the flag. **The docstring claim at `:169-170` (`ERROR tests/x.py -
FileNotFoundError: …`) is a candidate to confirm or refute, not a measurement.** If the chosen
flag changes `_PROGRESS`'s input, re-run
`test_m19_reads_a_skip_that_carries_its_reason_at_any_terminal_width` at both terminal widths
before proceeding — that parser is width-sensitive by measurement and a flag change is exactly
the kind of thing that breaks it.

- [ ] **Step 2: Write the failing test (verbatim)**

```python
def test_m19_refuses_a_collection_error_that_names_no_removed_artifact():
    """[[R118]]'s general form: read the exception, not the mere existence of an ERROR.

    Arm 1 admits an edge when X's oracles FAIL with Y's artifacts gone, so scoring *any* import
    break as FAILED makes arm 1 permissive: a missing dependency, a syntax error on the branch or
    a broken conftest all read as "X consumes Y" — an edge asserted on no evidence at all. The
    direction matters: arm 2 is unaffected in the unsafe direction, because there a FAILED
    refutes.

    Two halves, and both are needed — a rule that only raises is as wrong as one that only
    scores:

      * an ERROR whose exception NAMES a removed path is genuine consumption and scores FAILED.
        This is the commonest TRUE positive the instrument has, and refusing it would refuse
        every edge whose oracle module cannot import without its artifact.
      * an ERROR whose exception names nothing removed is an instrument failure and RAISES with
        the transcript, exactly as an unresolved node id already does (`_scores:219-226`).
    """
    consumed = _ablate([_ERROR_ARTIFACT], [_ERROR_PROBE])[_ERROR_PROBE]
    assert consumed == FAILED, (
        f"a module that cannot import once its declared artifact is removed IS consumption; "
        f"scoring it {consumed!r} would refuse the instrument's commonest true positive"
    )

    with pytest.raises(RuntimeError) as caught:
        _ablate([_UNRELATED_REMOVAL], [_ERROR_PROBE])
    message = str(caught.value)
    assert _ERROR_PROBE.split("::")[0] in message, message
    assert _UNRELATED_REMOVAL in message, (
        f"the refusal must name what WAS removed, so a reader can see that the exception does "
        f"not mention it: {message}"
    )
```

**Setup note (rule 2, extended to the setup).** `_ERROR_PROBE`, `_ERROR_ARTIFACT` and
`_UNRELATED_REMOVAL` are yours to choose and **must be measured before the test is written**:

- `_ERROR_PROBE` must be a node id in a module that raises a **collection** ERROR — not a test
  failure — when `_ERROR_ARTIFACT` is gone. That means the import happens at **module scope**.
  Verify with `pytest --collect-only` in a worktree with the file removed.
- `_UNRELATED_REMOVAL` must be a path whose removal the exception does **not** mention, while the
  module still errors at collection for the original reason. **If no such pair exists in the
  tracked tree, say so in the task report** and construct the second half by removing a file the
  module does not touch while forcing the same break — do **not** weaken the assertion to make a
  broken setup go green (CLAUDE.md § Plan authoring, the sixth-defect note).

- [ ] **Step 3: Run it and watch it fail**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py::test_m19_refuses_a_collection_error_that_names_no_removed_artifact -v`
Expected: FAIL on the second half with `DID NOT RAISE` — today every collection ERROR scores
`FAILED`. Paste it.

- [ ] **Step 4: Implement §4.5**

Invariants, no bodies:

- `_run_module` gains whatever S2 measured; `_COLLECT_ERROR` is widened to capture the exception
  text alongside the module path, or a second pattern is added — your call, stated in the report.
- `_scores` gains `removed` and scores the collection-ERROR branch `FAILED` **only** when the
  exception text contains one of the removed paths.
- Otherwise it raises `RuntimeError` naming the module, the exception text, the removed paths and
  the transcript.
- `_ablate` passes its `removed_files` through.
- **Match on the removed path, never on a heuristic about exception type.** An `OSError` is not
  the criterion; the *name* is (§7's evidence-positive requirement).
- Path-form check: `removed_files` entries are repo-root-relative (`_ablate:270`), while a
  traceback prints absolute paths. Measure which form appears in the transcript before choosing
  the containment test — a rule that never matches turns every true positive into a raise.

- [ ] **Step 5: Run the module green**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py -v`. Expected PASS. Confirm
`test_m19_an_edge_the_membrane_admits_and_the_ablation_refutes` and the live-manifest test are
still green — the second is the one that would notice a rule that never matches.

- [ ] **Step 6: FALSIFICATION (spec §7 oracle 5)**

Invert the rule — score every collection ERROR `FAILED` again — and show the new test red on its
`pytest.raises` half; restore; green. Then invert the *other* way — raise on every collection
ERROR — and show the test red on its first half. **Both directions**, because a one-sided
falsification cannot distinguish this rule from "always raise".

- [ ] **Step 7: `git status --porcelain`, then commit**

```bash
git add tests/test_arc_ablation.py
git commit -m "M19: a collection ERROR is evidence only if its exception names the removed artifact (R118)"
```

---

## Task 5: The record corrections this loop owes (spec §6 + M7)

**Files:**
- Modify: `tests/test_arc_ablation.py:87-111` (limitation 4), `:485` (the endpoint count)
- Modify: `docs/superpowers/residues.md`, `docs/superpowers/residues-open.md`,
  `docs/superpowers/residues-closed.md`

**Interfaces:** consumes Tasks 1–4 (the closures they evidence). Produces nothing code-facing.

**Five corrections, not four.** The spec names four; M7 found a fifth while this plan was written.

- [ ] **Step 1: Re-derive the census yourself, then correct limitation 4**

Run this and paste the output in the task report — the docstring must cite a command a reader can
re-run, which is the whole point of [[R120]]:

```bash
./.venv/bin/python - <<'PY'
import sys; sys.path.insert(0, ".")
from collections import Counter
from rdflib import Graph, Namespace
from tests.test_arc_manifest import MANIFEST, _LINE_SUFFIX
PROG = Namespace("https://w3id.org/iladub/progress#")
g = Graph().parse(MANIFEST, format="turtle")
raw = list(g.subject_objects(PROG.oracleArtifact))
files = {_LINE_SUFFIX.sub("", str(o)) for _s, o in raw}
print("triples:", len(raw), "files:", len(files),
      Counter(f.split("/")[0] for f in sorted(files)))
PY
```

Expected (M2, 2026-08-23): `triples: 48 files: 29 Counter({'examples': 12, 'tests': 9, 'vocab': 8})`.

Then rewrite `tests/test_arc_ablation.py:87-111`:

- `35` → **29** distinct files, with the per-directory census corrected: `examples` 12, `tests` 9,
  `vocab` **8** (not 14 — `14` was `vocab/`'s *triple* count), `src/` 0. Cite `48` raw triples
  separately so the two counts are never conflated again.
- **Replace the dismissal reasoning, not only the number.** The hazard is not an artifact *under*
  `src/`; it is an artifact *resolved through* `src/`. The right test is **"does the consuming
  oracle reach this file through library code?"** By that test **8 of the 29 are un-ablatable**
  without §4.1. Correcting only the number leaves the defect in place.
- Record that the conclusion *"no shipped edge is affected"* survives **for a different reason
  than the one written**: the 6 asserted edges grounded because their oracles root their evidence
  in the **test file's** `__file__`, which in a worktree *is* the worktree
  (`tests/test_boundary.py:6` and siblings). That is self-evidencing — an edge that grounded is
  an edge whose oracle was ablation-sensitive.
- Record that §4.1 now re-roots `src/`, and that limitation 4's remaining claim — *is anything
  **else** still resolving to the main tree?* — stays **declared, not measured** (spec §9), and
  point at the R122 row Task 6 raises. Do **not** delete limitation 4; it is corrected, not
  retired.

- [ ] **Step 2: Correct the stale endpoint count at `:485` (M7)**

`:484-486` reads *"MEASURED 2026-08-22 over those 6 edges: 9 endpoint criteria, 6.69 s"*. Measured
2026-08-23 over those same 6 edges: **8** endpoint criteria, **10** oracle ids, **4** modules.
Nine is the *seven*-edge figure — it counts `holon:02`, whose edge the same docstring says two
lines earlier was **deleted**. Re-derive it (M6's command), correct the count, and re-time the
test after Task 3 so the wall-clock figure describes the shipped instrument rather than the
pre-control one.

- [ ] **Step 3: Close [[R121]] in the register**

Per CLAUDE.md § the register: **strike the number (`~~R121~~`), record the closure evidence in
place, and do NOT delete the row.** Move it to `residues-closed.md`, leave the index line struck
with a pointer. The closure evidence is Task 1's two-leg test plus M1/M4. Note that the remedy
shipped is **not** the one R121's own remedy column prescribed — the row proposes *"a per-worktree
isolated install, or an injection point (`ILADUB_VOCAB` / rootdir-relative resolution)"*; what
shipped is a subprocess `PYTHONPATH`, which needed no library change at all. Say so: a row whose
prescribed remedy was bypassed is worth more to the next reader than one that appears to have
been followed.

- [ ] **Step 4: Correct [[R114]]'s remedy column**

R114's remedy still argues from the gitignored corpus alone — *"(a) M19 materialises the
gitignored corpus … so the oracle executes"*. Its **cause** was corrected 2026-08-23; the remedy
was not. Materialising the corpus makes `etkl:01`'s oracle **run** and leaves it **un-ablatable**;
after Task 1 the second half is fixed and the corpus half is not. Rewrite the column to say what
now remains: the corpus (execution) **and** [[R113]] (file granularity), with R121's half struck
through. Do not close R114.

- [ ] **Step 5: Amend [[R118]]'s row**

R118 closes in the general form Task 4 shipped **and** its live instance is gone (Task 2). Strike
it, record both, and note the row's own arithmetic correction: it says *"five modules raise a
collection ERROR"*; the index already corrects this to **6**, and M3 re-derives 6 with
`tests/test_to_rdf.py` breaking transitively. Record the re-derivation, not the memory.

- [ ] **Step 6: Correct [[R120]]'s row where this loop touched it**

R120 stays **open** — its subject is the `44`/`18` blast-radius pair census, which this loop does
not reproduce. But add the fifth-correction finding (M7) to it: the `9 endpoint criteria` figure
was a second unreproducible number in the same docstring, found and corrected 2026-08-23. That is
evidence R120's class is not a one-off.

- [ ] **Step 7: Commit**

```bash
git add tests/test_arc_ablation.py docs/superpowers/residues*.md
git commit -m "record: correct limitation 4's census and reasoning, close R121/R118, amend R114/R120"
```

---

## Task 6: Run the instrument against the live manifest and report what it says (spec §8)

**Files:**
- Modify: `docs/superpowers/residues.md` + `residues-open.md` (new rows)
- Create: `docs/superpowers/2026-08-23-worktree-that-resolves-evidence.md` (the loop's evidence
  file, immutable after close — Documentation governance)

**Interfaces:** consumes everything. Produces the loop's closing evidence.

**This task is where the loop's honesty is tested.** The spec predicts **zero new edges** (§9).
If the run comes back non-empty, the loop **still closes** — it reports, files the row, and stops.
Global Constraint 9.

- [ ] **Step 1: Re-derive DoD item 3 in a worktree the SHIPPED `_ablate` creates**

Not a hand-built worktree. Instrument `_ablate` temporarily (or add a throwaway test that calls
it) so that `pytest --collect-only -q -p no:cacheprovider` runs inside the worktree it produces,
and record the result. Expected: **0 collection errors** (M3 measured 6 before). Paste the
transcript. Remove the instrumentation before committing.

- [ ] **Step 2: Run `ablation_refusals` over the LIVE manifest and report the result verbatim**

Run: `./.venv/bin/python -m pytest tests/test_arc_ablation.py::test_m19_the_live_manifest_carries_no_refuted_edge -v`

and separately print `ablation_refusals(Graph().parse(MANIFEST, format="turtle"))`.

**Report what it says, whatever it is.** Three outcomes and what each means:

- `[]` — the predicted outcome. §4.1 landed, the instrument is honest, the graph is identical.
  Spec §7's closing paragraph: *"that outcome is expected and must be reported as-is."*
- **A refusal appears** — an edge that grounded on the old instrument no longer does. That is a
  finding about the **arc**, and the edge must be fixed by hand in a reviewed commit. Report it;
  do not touch the manifest in this loop unless the maintainer rules otherwise.
- **A pair that previously refuted now grounds** — visible only by comparing against the
  pre-change run, since `ablation_refusals` returns refusals for *asserted* edges only. **RECORD
  IT AS A FINDING and file a residue row. Do NOT author the edge** (spec §8 item 2): authoring is
  its own loop with its own review; [[R113]]'s file-granularity may make the pair ambiguous across
  several criteria sharing one artifact; and an instrument change and the first graph claim it
  produces must not be reviewed together.

**Re-tuning the instrument until `[]` comes back is the one forbidden response.**

- [ ] **Step 3: Raise R122 — the question this loop declines to ask (spec §8 item 4)**

Re-run M9's two greps to get the tally snapshot, then append to `residues-open.md` and a one-line
pointer to `residues.md`:

> **R122 (n/m closed)** — *After §4.1 re-roots `src/`, is any oracle still resolving evidence to
> the main tree?* §4.1 closes the one path measured to shadow the worktree (spec §2.2), and this
> loop deliberately ships **no** hermeticity machinery, permanent or one-shot — an audit-hook
> probe was scoped out as not worth the loop, its expected finding being empty. So
> `test_arc_ablation.py` limitation 4's residual claim (F3) stays **declared** rather than
> measured. What would close it: a one-shot audit that, inside an ablated worktree, records every
> path the endpoint oracles actually open and refuses any that lies outside the worktree.

Raise a second row **only if Step 2 produced a finding**; give it the finding, the pair, and the
[[R113]] ambiguity if any.

- [ ] **Step 4: Write the evidence file**

`docs/superpowers/2026-08-23-worktree-that-resolves-evidence.md`, carrying: every measurement
this loop made (S1's and S2's transcripts especially — they are the two facts the plan refused to
supply), the five falsification blocks, Step 2's live result verbatim, and the rows raised.
Immutable after loop close (Documentation governance).

- [ ] **Step 5: Full suite, real tree clean, then commit**

Run: `./.venv/bin/python -m pytest -q` — expected **1314 collected** in the main tree, no new
failures. Then `git status --porcelain` (Global Constraint 2).

```bash
git add docs/superpowers/
git commit -m "evidence: the worktree that resolves — live run reported, R122 raised"
```

---

## Definition of done (spec §8, mapped to tasks)

| # | spec §8 item | task |
| --- | --- | --- |
| 1 | §4.1–§4.5 implemented, each with §7 falsification evidence | 1, 2, 3, 4 |
| 2 | `ablation_refusals` re-run over the LIVE manifest, result reported whatever it is; a newly grounding pair is a FINDING, never an edge | 6 Step 2 |
| 3 | `pytest --collect-only -q` in a shipped-`_ablate` worktree reports **0** errors (from 6 — M3) | 6 Step 1 |
| 4 | A residue row raised for the question this loop declines to ask | 6 Step 3 |
| 5 | The §6 corrections landed in the TRACKED artifacts, not only in the spec | 5 |
| 6 | Real tree `git status --porcelain`-clean before and after every M19 run | every task's last-but-one step |
| 7 | Every number re-derived at implementation time | Tasks 1–6; M1–M10 are the plan's own re-derivations, not a substitute for yours |

---

## Unverified at plan time — read this before Task 1

Honest list, in the shape spec §4 used.

1. **The two named seams (S1, S2) are unmeasured on purpose.** They are the two places where this
   plan supplies a question instead of an answer. Measure before writing the call.
2. **Task 4's `_ERROR_PROBE` / `_UNRELATED_REMOVAL` pair is not known to exist.** The plan states
   how to find it and what to do if it does not (Task 4, setup note). This is the plan's weakest
   setup claim and the likeliest place a plan-supplied test turns out to be unwritable.
3. **Task 3's `CONTROL_FAILS_FIXTURE` rests on `etkl:01`'s oracle still being
   `tests/test_corpus.py::test_expected_verdict`** — read from [[R114]]'s row citing
   `tests/arc-manifest.ttl:158`, **not re-measured here**. Measure it in Task 3 Step 1.
4. **Whether §4.1 flips any live pair is still unknown** (spec §9 predicts zero). Nobody has run
   `ablation_refusals` under the change. That is Task 6, and it is a measurement, not a
   formality.
5. **No adversarial review has run on the spec.** This plan is a second independent reading of
   its numbers — M1–M6 re-derived every measured claim, and M7 found a defect the spec missed —
   but a second reading of the *numbers* is not a review of the *design*.
6. **The control's cost is measured as one combined invocation (M6), not as `_ablate` runs it.**
   Four subprocess startups, not one. Re-measure in Task 3 Step 4.
