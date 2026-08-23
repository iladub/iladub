# The worktree that resolves — the loop's measurements, in one place

Closing evidence for the loop argued from
`docs/superpowers/specs/2026-08-23-the-worktree-that-resolves-design.md` and executed from
`docs/superpowers/plans/2026-08-23-the-worktree-that-resolves.md` (subagent-driven, six tasks).

Branch `the-worktree-that-resolves`; the six commits are `7e4f84c` (Task 1), `2d08f06` (Task 2),
`95bfb9a` (Task 3), `5f2cad9` (Task 4), `d6b393c` (Task 5), `bde884a` (Task 5 fix round), plus
this task's own. Runner `./.venv/bin/python` (Python 3.12.0, pytest 9.0.3, darwin), **never
`python3`** — Global Constraint 1: `python3` carries rdflib 7.1.4 and no pyrudof, and M19's
subprocesses inherit `sys.executable`.

The per-task reports this file draws on are
`.superpowers/sdd/2026-08-23-the-worktree-that-resolves/task-{1,2,3,4,5,6}-report.md`. Where a
transcript is reproduced here it is reproduced from the task that measured it.

---

## §0 The headline, before the detail

**The live result is `[]`, and it is the outcome the spec predicted up front (§9) rather than one
discovered afterwards.** M19 now gives its ablated worktrees an explicit `PYTHONPATH`, copies in
the declared environment inputs it did not check out, proves the environment faithful with an
un-ablated control before it scores anything, and refuses to read a collection ERROR as
consumption unless the exception names the removed artifact. Under all four changes the six
asserted `prog:dependsOn` edges still ground, and no pair changed state.

Two numbers moved that were *not* predicted:

1. `pytest --collect-only -q` inside a worktree the **shipped** `_ablate` creates reports **1320
   collected, 0 errors** (§4) — DoD item 3, which asked for 0 down from 6.
2. Task 4's census *"all 29 declared artifacts are `.ttl`/`.rq`/`.md`-class data files, **zero**
   are `.py`"* is **refuted**: two are (§6.2). That refutation is why [[R123]] is a measured row
   and not a speculative one.

---

## §1 S1 and S2 — the two facts the plan deliberately refused to supply

CLAUDE.md § Plan authoring rule 3 says *name the seam the implementer must check, not the answer*.
The plan named two and answered neither. Both were measured before the code that depends on them
was written.

### S1 — is `PYTHONPATH` set, in a shell and inside a pytest run? (Task 1)

The spec's §4.1 says *prepend* `<cwd>/src`, preserving any inherited value. Whether there is
anything to preserve was left open on purpose.

```
$ echo "shell PYTHONPATH: [${PYTHONPATH}]"; env | grep -i pythonpath || echo "no PYTHONPATH in env (shell)"
shell PYTHONPATH: []
no PYTHONPATH in env (shell)
```

And from inside a pytest run of the module itself (a throwaway test, appended, run, then removed
with `git checkout --` before any real edit):

```python
def test_s1_probe_TEMP():
    import os
    print("S1 (inside test_arc_ablation.py) PYTHONPATH REPR:", repr(os.environ.get("PYTHONPATH")))
    assert False
```

```
$ ./.venv/bin/python -m pytest tests/test_arc_ablation.py::test_s1_probe_TEMP -v -s
tests/test_arc_ablation.py::test_s1_probe_TEMP S1 (inside test_arc_ablation.py) PYTHONPATH REPR: None
FAILED
```

**Answer: unset (`None`), both ways.** So there is nothing to preserve on this machine today. The
shipped code still handles the general case — `env["PYTHONPATH"] = src if not existing else
os.pathsep.join([src, existing])` — it is simply not exercised here. Recording the *unset* result
matters as much as a set one would have: it is the reason the implementation's `else` branch has
no live coverage, and a reader who assumes it does would be wrong.

### S2 — what does pytest actually print for a collection ERROR, and under which `--tb`? (Task 4)

The spec's §4.5 reads the exception text of a collection ERROR. `_run_module` passed `--tb=no`, so
the plan asked: *establish what pytest prints before choosing the rule's input; do not assume a
format.* Two worktrees built the way `_ablate` builds one (`git worktree add --detach <wt> HEAD`,
`baml_client/` copied in), one node id
(`tests/test_docgov_shapes.py::test_conforming_minimal_graph`), two removals, three `--tb` styles,
two terminal widths.

* **case A** — `rm <wt>/vocab/shapes/doc-governance-shapes.ttl`; `tests/test_docgov_shapes.py:12`
  parses it at module scope. The exception names the removed path.
* **case B** — `rm <wt>/tests/docgov_extract.py`; `tests/test_docgov_shapes.py:9` imports
  `tests.docgov_extract` at module scope. The exception names the dotted module only.

**A1 — `-v --tb=no`, case A, COLUMNS=80:**

```
collected 0 items / 1 error

=========================== short test summary info ============================
ERROR tests/test_docgov_shapes.py - FileNotFoundError: [Errno 2] No such file...
=============================== 1 error in 0.11s ===============================
rc=4
```

**A2 — the same command, case A, COLUMNS=250:**

```
ERROR tests/test_docgov_shapes.py - FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/.../s2wt/vocab/shapes/doc-governance-shapes.ttl'
```

**This is S2's finding.** The short-summary tail is **clipped to the terminal width**. At 80
columns the removed path — the only thing §4.5 reads — is replaced by `...`. Same run, same exit
code, two different texts: exactly the width sensitivity `_PROGRESS`'s own comment already records
for SKIP reasons.

**A3 — `-v --tb=no`, case B, COLUMNS=80 *and* 250:**

```
collected 0 items / 1 error

=========================== short test summary info ============================
ERROR tests/test_docgov_shapes.py
=============================== 1 error in 0.11s ===============================
```

**Second finding:** for an *import* collection error the summary line carries **no exception tail
at all**, at any width — and `--tb=no` suppresses the whole `ERRORS` section, so under the flags
in force before this loop the exception text §4.5 needs **did not exist anywhere in the output**.

**B1/B2 — `--tb=line`, case A, COLUMNS=80 and 250 (the `E` line is byte-identical at both):**

```
==================================== ERRORS ====================================
_________________ ERROR collecting tests/test_docgov_shapes.py _________________
E   FileNotFoundError: [Errno 2] No such file or directory: '/private/tmp/.../s2wt/vocab/shapes/doc-governance-shapes.ttl'
```

**B3 — `--tb=line`, case B, COLUMNS=80 and 250 (identical at both):**

```
==================================== ERRORS ====================================
_________________ ERROR collecting tests/test_docgov_shapes.py _________________
ImportError while importing test module '/private/tmp/.../s2wt2/tests/test_docgov_shapes.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_docgov_shapes.py:9: in <module>
    from tests.docgov_extract import DG, doc_iri
E   ModuleNotFoundError: No module named 'tests.docgov_extract'
```

`--tb=short` (C1/C2) produces the same un-clipped `E` line preceded by four extra frames — strictly
more output and no more information. `-rE` was not measured as a separate arm and deliberately so:
pytest's default `reportchars` already emits the `ERROR …` summary line with no `-r` flag at all
(visible in A1/A2/A3), so `-rE` adds nothing and does not touch the clipping, which is the actual
defect.

**Answer: `--tb=line`, and read the `ERRORS` section, never the summary line.** It is the minimum
that makes the text exist, it is un-clipped at both widths in both cases, and it leaves
`_PROGRESS`'s input untouched (measured on a mixed run — one FAILED id plus the seven skipping
corpus ids — the `-v` progress region is identical under both flags, and the `FAILURES` section
`--tb=line` adds carries no line ending in `[ nn%]` and none beginning `ERROR `).

**The docstring claim S2 was sent to check was confirmed in shape and refuted in the half §4.5
depends on.** `ERROR tests/x.py - FileNotFoundError: …` does exist and does have that form — but
its tail is truncated at 80 columns and absent entirely for an import error. A rule reading §4.5's
evidence out of that line would have matched on a wide developer terminal and never on 80-column
CI, turning every true positive into a raise. That is why S2 was ordered first.

---

## §2 What shipped

| spec | change | commit |
| --- | --- | --- |
| §4.1 | `_run_module` runs its subprocess with `env=` whose `PYTHONPATH` has `<cwd>/src` prepended, re-rooting every `import iladub…` onto the worktree; new probe module `tests/test_arc_worktree_probe.py` and a two-leg test | `7e4f84c` |
| §4.2 | `_MATERIALISED = ("baml_client",)`, `_declared_inputs`, `_materialise` — copy, never symlink; called between `git worktree add` and the first `unlink()` | `2d08f06` |
| §4.4 | `_refuse_materialisation_collision`, called at the top of **both** `ablation_refusals` (over the union of every endpoint's artifacts) and `_ablate` (over its own argument), before any worktree exists | `2d08f06` |
| §4.3 | `_run_control` — one un-ablated worktree over the union of endpoint oracle ids, before the ablation loop; any id not `PASSED` raises with the transcript and the materialised/absent partition | `95bfb9a` |
| §4.5 | `_COLLECT_ERROR_TEXT`, `--tb=no` → `--tb=line`, `_scores` gains a fifth parameter `removed` and raises on a collection ERROR whose exception names none of it | `5f2cad9` |
| §6 | limitation 4's census and reasoning corrected in the module docstring; ~~R121~~ and ~~R118~~ closed; R114's remedy and R120's measurement amended | `d6b393c`, `bde884a` |
| §6 (residual) | the two stale `_scores:219-226` cross-references corrected to `_scores:440-446` | this task |

Note on §4.1's shape: `sys.executable` is untouched (absolute, so unaffected by the worktree having
no `.venv`), `env` starts from a **copy** of `os.environ` so every other inherited variable
survives, and the re-rooting applies to every `_run_module` call including `_ablate([], …)`.

---

## §3 The five falsification blocks

CLAUDE.md § Plan authoring rule 4: remove or invert the thing a test pins, show it failing,
restore, show green. Reproduced from the task reports that ran them.

### F1 — §4.1: remove the `PYTHONPATH` env from `_run_module` (Task 1)

Reverted `_run_module` to its pre-fix body in the working tree, on top of the already-committed
fix, so the probe module and the new test stay present at `HEAD` and the falsification isolates
the one change:

```
$ ./.venv/bin/python -m pytest tests/test_arc_ablation.py::test_m19_resolves_the_library_into_the_worktree_it_ablates -v
>       assert _ablate([], [_PROBE])[_PROBE] == PASSED, (
E       AssertionError: the library did not resolve into an un-ablated M19 worktree — every ablation this module performs is reading the main tree (R121)
E       assert 'failed' == 'passed'
1 failed in 1.24s
```

Restored (`git checkout --`), `git status --porcelain` empty, module green: **5 passed in 10.63s**.

### F2 — §4.2/§4.4: three inversions (Task 2)

Each applied to a saved-good copy, run, restored, and the restore verified byte-identical
(`diff -q` → IDENTICAL) before the next.

**2a — delete the materialisation call** (`_materialise(wt, repo)` → a no-op comment):

```
tests/test_arc_ablation.py::test_m19_materialises_the_generated_client_it_did_not_check_out FAILED
E       AssertionError: a module that needs the generated BAML client did not run in an M19 worktree; …
E       assert 'failed' == 'passed'
1 failed, 1 passed, 5 deselected in 1.39s
```

**2b — point `_MATERIALISED` at a path absent from the main tree** (`("no_such_dir",)`) —
spec §7 oracle 4, which asserts the design is **discovered**-demand, not declared-demand.
Materialisation stayed **silent**, no raise, and the skip-parser self-test still passed:

```
$ ./.venv/bin/python -m pytest tests/test_arc_ablation.py -k "reads_a_skip" -v
tests/test_arc_ablation.py::test_m19_reads_a_skip_that_carries_its_reason_at_any_terminal_width PASSED
1 passed, 6 deselected in 1.29s
```

**2c — remove the collision guard**, in two steps, because a bare `pytest.raises` cannot
distinguish *"raised before the first worktree"* from *"raised before **this** worktree"*.
With both call sites deleted: `E Failed: DID NOT RAISE <class 'RuntimeError'>`. With the guard
merely **moved** into the per-criterion loop, the `pytest.raises` block *succeeds* and the test
still fails, on the assertion that exists for exactly this:

```
>       assert not never.called, (...)
E       AssertionError: the disjointness guard fired only once _ablate had already been entered; it must refuse before the first worktree is created
E       assert not True
E        +  where True = <MagicMock name='_ablate' id='4409501088'>.called
1 failed, 6 deselected in 0.50s
```

That second half is what proves the shipped placement (union-scoped, above the loop, in
`ablation_refusals`) is load-bearing rather than incidental.

### F3 — §4.3: remove the `_declared_inputs` partition from the control's message (Task 3)

**This is the substituted oracle, and the substitution is part of the spec, not a footnote to
it.** Spec §7 oracle 2 as originally written — *delete the materialisation step, the control goes
red naming the missing input* — is **unsatisfiable**: the control runs the union of the six
asserted edges' endpoint oracles, which lives in exactly four modules, and none imports
`baml_client`. Re-verified by Task 3 rather than taken on trust:

```
$ for m in test_boundary test_escalation_shacl test_hga_alignment test_vocab_shapes; do \
      printf "%-28s %s\n" "$m" "$(grep -c baml tests/$m.py) baml refs"; done
test_boundary                0 baml refs
test_escalation_shacl        0 baml refs
test_hga_alignment           0 baml refs
test_vocab_shapes            0 baml refs
```

Deleting materialisation therefore leaves the control green — a test that passes with its subject
deleted, CLAUDE.md's own defect 5. The satisfiable oracle carrying the same force, dropping the
trailing `{partition}` interpolation from `_run_control`'s raise:

```
>       assert "baml_client" in message, (...)
E       AssertionError: the control must report which declared environment inputs were
        materialised, so a developer without a generated client gets an actionable sentence:
        M19: the control run found ['tests/test_corpus.py::test_expected_verdict[...]'] not
        PASSED in an UN-ABLATED worktree (nothing was removed): {...}. …
1 failed in 1.45s
```

Restored → **1 passed in 1.12s**. A third inversion — replacing the `_run_control(...)` call with
`pass` — gives `E Failed: DID NOT RAISE <class 'RuntimeError'>`, pinning the control's own
existence; restored → **8 passed in 17.99s**.

### F4/F5 — §4.5, both directions (Task 4)

A one-sided falsification cannot distinguish this rule from *"always raise"*, so both were run.

**Direction A — score every collection ERROR `FAILED` again** (`if not named:` → `if False:`):

```
        assert consumed == FAILED, (…)          # first half still passes
>       with pytest.raises(RuntimeError) as caught:
E       Failed: DID NOT RAISE <class 'RuntimeError'>
1 failed in 1.92s
```

**Direction B — raise on every collection ERROR** (`if not named:` → `if True:`):

```
E               ==================================== ERRORS ====================================
E               _________________ ERROR collecting tests/test_docgov_shapes.py _________________
E               E   FileNotFoundError: [Errno 2] No such file or directory: '/private/var/folders/…/arc-m19-ro_o5pgq/wt/vocab/shapes/doc-governance-shapes.ttl'
tests/test_arc_ablation.py:383: RuntimeError
1 failed in 0.78s
```

**The two directions fail on opposite halves** — A on the `pytest.raises`, B on the true positive,
which raised out of `_ablate` before `assert consumed == FAILED` could run. That is the proof the
test distinguishes the shipped rule from both degenerate rules. Restored → **9 passed in 17.23s**.

### Task 5 and Task 6 pin nothing new with a test, and say so

Task 5's commit changes prose only — module docstrings and register rows; every `assert` in
`tests/test_arc_ablation.py` is byte-identical to `5f2cad9`. Task 6 adds no test either: its
deliverables are measurements, two register rows, this file, and a two-site docstring
cross-reference correction. Global Constraint 8 requires falsification *per task that pins
something new with a test*; neither does, and **stating that plainly is the required response, not
fabricating an inversion.**

---

## §4 DoD item 3 — `--collect-only` in a worktree the SHIPPED `_ablate` creates

Not a hand-built worktree: `_ablate` was instrumented temporarily so the collect ran inside the
worktree it produces, *after* `git worktree add --detach <wt> HEAD` and *after* `_materialise`, and
the instrumentation was removed before committing (`git checkout -- tests/test_arc_ablation.py`,
then `git diff` empty — verified, §7).

Driven by `_ablate([], ['tests/test_arc_worktree_probe.py::test_library_resolves_to_this_checkout'])`,
running `pytest --collect-only -q -p no:cacheprovider` with `cwd=<wt>`, once with
`PYTHONPATH=<wt>/src` (the shipped condition, what `_run_module` sets) and once without it:

```
WITH PYTHONPATH=/var/folders/k7/…/T/arc-m19-qo3ohjfs/wt/src
rc=0
…
1320 tests collected in 2.44s

$ grep -c "^ERROR " collect2.txt
0
```

```
NO PYTHONPATH
rc=0
…
1320 tests collected in 1.13s

$ grep -c "^ERROR " collect.txt.nopypath
0
```

**0 collection errors, from 6.** The baseline is spec §2.6's *1293 collected, 6 errors* — six
modules (`test_extract_baml`, `test_loop`, `test_m4_databook`, `test_m4_pipeline`, `test_targeted`,
`test_to_rdf`) unable to import the gitignored, generated `baml_client/`. That baseline was
re-measured twice during the loop and drifted upward each time as the branch added tests: Task 2
measured **1295** collected / 6 errors, Task 5 measured **1299** / 6 errors with the six module
names matching exactly. The **denominator is not the claim** — 1320 is simply this tree's test
count at `bde884a` plus the loop's own additions — and it is recorded here rather than pinned
anywhere, because pinning it would be pinning a number that moves for reasons unrelated to the
instrument. **The claim is the error count, and it is 0 under both environments.**

That `PYTHONPATH` makes no difference to *collection* is itself worth recording: §4.1's fix
changes which `src/` an import resolves to, not whether it resolves. What it changes is
**ablation-sensitivity**, and that is pinned by leg 2 of
`test_m19_resolves_the_library_into_the_worktree_it_ablates`, not by a collect count.

---

## §5 DoD item 2 — `ablation_refusals` over the LIVE manifest, reported as it came

Real tree `git status --porcelain` empty before and after, `git worktree list` showing the main
checkout only.

```
$ ./.venv/bin/python -m pytest tests/test_arc_ablation.py::test_m19_the_live_manifest_carries_no_refuted_edge -v
platform darwin -- Python 3.12.0, pytest-9.0.3, pluggy-1.6.0
collected 1 item

tests/test_arc_ablation.py::test_m19_the_live_manifest_carries_no_refuted_edge PASSED [100%]

============================== 1 passed in 8.32s ===============================
```

And the value itself, printed rather than asserted:

```
ablation_refusals(LIVE MANIFEST) = []
len: 0
```

**`[]` — the outcome spec §9 predicted before the loop began.** Spec §7's closing paragraph names
this exact result and requires it to be reported as-is: *"§4.1 lands, the ablation runs, and no
edge changes state — leaving an instrument that is honest and a graph that is identical. That
outcome is expected and must be reported as-is."* Global Constraint 9's forbidden response — a
non-empty result suppressed, or the instrument re-tuned until `[]` came back — did not arise: the
first run returned `[]` and nothing was adjusted.

### The one previously-refuting pair on record still refutes

`ablation_refusals` returns refusals for *asserted* edges only, so its `[]` cannot by itself
distinguish *"nothing changed"* from *"a pair that used to refute now grounds"* — the third outcome
Global Constraint 9 is written for. There is exactly one such pair on the record:
`holon:02 → holon:01`, authored 2026-08-22, refuted by arm 1 on the pre-§4.1 instrument and
**deleted** rather than demoted (M17 refuses the demotion). It was re-run under the changed
instrument, **in memory, with `tests/arc-manifest.ttl` untouched** (Global Constraint 4):

```
$ ./.venv/bin/python -c "… probe = Graph() + live;
    probe.add((PROG['criterion:holon:02'], PROG.dependsOn, PROG['criterion:holon:01']));
    print(ablation_refusals(probe))"
edges in probe graph: 7
M19: arm 1 refutes …criterion:holon:02 prog:dependsOn …criterion:holon:01 — with
…criterion:holon:01's artifacts ['vocab/ontology/etkl-holons.ttl'] removed, every one of
…criterion:holon:02's oracle tests still passes
({'tests/test_hga_alignment.py::test_alignment_axioms_present': 'passed',
  'tests/test_source_ownership.py::test_alignment_modules_only_point_outward': 'passed'}),
so …criterion:holon:02 does not consume …criterion:holon:01
len: 1
```

**Still refuted, and for the reason [[R117]] already gives** — the refutation found a hole in the
*oracle*, not a path-resolution defect: `test_alignment_axioms_present` parses
`iladub-hga-align.ttl` alone, so deleting `etkl-holons.ttl` cannot break it however faithfully the
worktree resolves. §4.1 was never going to change that, and now it is measured rather than argued.

**What this comparison does NOT cover, stated so it is not read as more than it is.** No pair
outside the 6 asserted edges and this one has ever been run through `ablation_refusals`, on either
version of the instrument, so *"a newly grounding pair"* is unfalsified rather than refuted for the
rest of the criterion space. Spec §9 scopes that out with a reason: `etkl:01` is the only met
criterion whose oracle reaches evidence through `src/iladub/`, and it still cannot run without a
corpus this loop deliberately does not materialise (§2.5, [[R114]]). Authoring any new edge is a
later loop's work with its own review (spec §8 item 2), and [[R113]]'s file granularity would make
several candidates ambiguous anyway.

---

## §6 The two measurements routed to Task 6 by controller rulings

### §6.1 The live leg reaches **0** collection ERRORs — Task 4's plan-defect note STANDS

Task 4's brief asserted that `test_m19_the_live_manifest_carries_no_refuted_edge` *"is the one that
would notice a rule that never matches"*. Task 4 replied that it would not, having spied on
`_scores` and found zero collection ERRORs in the live leg; its reviewer could not verify that from
the diff and routed the measurement here. Re-measured by Task 6 by construction, spying on
`_scores` across a full live `ablation_refusals(MANIFEST)` run:

```
ablation_refusals(LIVE MANIFEST) = []
_scores invocations (control + ablation): 13
modules run: ['tests/test_boundary.py', 'tests/test_escalation_shacl.py',
              'tests/test_hga_alignment.py', 'tests/test_vocab_shapes.py']
COLLECTION ERRORS observed: 0 []
```

**Confirmed: 0.** So §4.5's rule is **dormant** on the live manifest — 13 scored module runs across
4 modules, and the branch that reads an exception is never entered. The live test proves the rule
does not spuriously raise; it cannot notice a rule that never matches. **Task 4's note is
correct and its brief's Step 5 rationale is refuted.** The true positive is pinned only by the
first half of `test_m19_refuses_a_collection_error_that_names_no_removed_artifact`, and
falsification direction B (§3, F5) is the only evidence that half has teeth. A future reader must
not treat the live test as a second oracle for §4.5.

### §6.2 The `.py` census — Task 4's dismissal is REFUTED, and [[R123]] is measured because of it

Task 4's finding 2 said a declared `prog:oracleArtifact` that is a **Python module** would be
genuine consumption §4.5 refuses to score, because the exception names the dotted module and never
the path — then dismissed it as not live: *"all 29 declared artifacts are `.ttl`/`.rq`/`.md`-class
data files, zero are `.py`."* The controller routed the census here with an explicit instruction to
verify it rather than carry it. Re-run against the live manifest with `tests/test_arc_manifest.py`'s
`MANIFEST` and `_LINE_SUFFIX`:

```
triples: 48 files: 29
by top dir: Counter({'examples': 12, 'tests': 9, 'vocab': 8})
by suffix : Counter({'.ttl': 27, '.py': 2})
PY artifacts: ['tests/etkl/fixtures.py', 'tests/etkl/test_vacuity_registry.py']
```

**Two of the 29 are Python modules.** The dir-level census (29 files / 48 triples / 12-9-8) that
Tasks 2 and 5 both re-derived is untouched and correct; the *suffix* claim laid over it was never
measured, and it is false. Which criteria declare them:

```
criterion: criterion:tab:06 -> tests/etkl/fixtures.py:726
criterion: criterion:tab:10 -> tests/etkl/test_vacuity_registry.py:87
```

`tests/etkl/fixtures.py` is imported by **36** test modules
(`grep -rl "etkl.fixtures" --include="*.py" tests/ | wc -l`), and at **module scope** by
`tests/etkl/test_closing_slice.py:5`, which is the oracle module of both `tab:01`
(`test_multi_table_ambiguous_escalates`) and `tab:03` (`test_false_positive_transpose_escalates`).
So the limitation is reachable through the shipped instrument today, and it was driven through it —
no fixture, no manifest edit, `_ablate` called directly the way this module's own tests call it:

```
$ ./.venv/bin/python -c "_ablate(['tests/etkl/fixtures.py'],
      ['tests/etkl/test_closing_slice.py::test_multi_table_ambiguous_escalates'])"
RAISED RuntimeError:

M19 instrument failure: tests/etkl/test_closing_slice.py failed to COLLECT, and its exception names
none of the removed artifacts ['tests/etkl/fixtures.py']. A collection ERROR grounds an ablation
only when the exception says the removed file is what broke it (spec §4.5, [[R118]]) — otherwise a
missing dependency or a broken conftest would read as consumption, and arm 1 admits on a FAILED.
EXCEPTION
ImportError while importing test module '/private/var/folders/…/arc-m19-absh8m8c/wt/tests/etkl/test_closing_slice.py'.
Traceback:
tests/etkl/test_closing_slice.py:5: in <module>
    from tests.etkl.fixtures import simple_table_pdf, pivoted_table_pdf
E   ModuleNotFoundError: No module named 'tests.etkl.fixtures'
```

The contrast is measured too, and it is what bounds the row: `tests/etkl/test_tiling_gate.py:55`
(`tab:04`'s oracle) imports the *same* file **inside a function**, so removing it scores an
ordinary `failed` with no raise —

```
SCORED (no raise): {'tests/etkl/test_tiling_gate.py::test_gate_reject_escalates_gracefully': 'failed'}
```

— the limitation bites only on a **module-scope** import.

**It is latent, not live, and the direction is the safe one.** Neither `tab:06` nor `tab:10` is an
endpoint of any of the 6 asserted edges — the 8 endpoints are `dec:01`, `dec:06`, `dec:07`,
`dec:10`, `dec:16`, `holon:01`, `holon:03`, `holon:04` (measured, §5's live run) — so nothing
shipped is scored through this path, and when it is reached it raises loudly rather than admitting
silently. Filed as [[R123]] with the remedy: teach §4.5 a **second evidence-positive form** (map a
removed `.py` path to its dotted module name and accept an exception naming *that*), never a looser
one.

---

## §6bis The full suite at loop close

```
$ ./.venv/bin/python -m pytest -q
…
1312 passed, 7 skipped, 1 xfailed, 10 warnings in 2201.24s (0:36:41)
PYTEST_EXIT=0
```

No failures, no errors. `1312 + 7 + 1 = ` **1320 collected** — exactly the count §4 measured inside
a shipped-`_ablate` worktree. The main tree and an M19 worktree now collect the same set of tests,
which is what §4.2 was for; the agreement was not planned as a check and is recorded as one. The
7 skips are the corpus oracles (`corpus/` is gitignored — [[R114]] and `_SKIPS_WITH_A_REASON`); the
10 warnings are the suite's designed wiki-staleness, promotion-queue and rdflib
`ConjunctiveGraph`-deprecation `UserWarning`s.

**A process finding worth carrying forward.** The first attempt at this run was piped through
`tail -30 > file` and was killed by the environment at ~68 minutes with **zero output written** —
a buffered pipe leaves no evidence of how far a killed run got. The second attempt redirected
pytest's own stdout to a file and appended an explicit `PYTEST_EXIT=` sentinel, making progress
observable throughout and completion unambiguous. Task 5's report records an environment sleep
interrupting it mid-task; this is the same hazard one task later. **Never buffer a 37-minute suite
through a pipe, and always write a completion sentinel.**

## §7 The real tree was never mutated

Global Constraint 2, checked at every step of this task:

```
$ git status --porcelain
(empty)
$ git worktree list
/Volumes/WD Green/dev/git/iladub  bde884a [the-worktree-that-resolves]
```

Empty before and after the Step 1 collect probe, the Step 2 live run, the `holon:02` probe, and
both §6.2 `_ablate` calls. The Step 1 instrumentation was reverted with
`git checkout -- tests/test_arc_ablation.py` and the revert verified — `git status --porcelain`
empty and `git diff` empty — before any of this task's real edits were made. Every worktree M19
built was removed by the `finally` in `_ablate` (`git worktree remove --force`, `shutil.rmtree`,
`git worktree prune`); none survives in `$TMPDIR`.

---

## §8 The loop's own corrections to its plan and spec

Recorded here because they are the loop's findings about itself, and a loop that only records its
successes is the register problem in miniature.

1. **Spec §7 oracle 2 was unsatisfiable and the spec says so in place** (§3/F3 above). The
   correction is *in the spec*, struck and replaced with the satisfiable form, rather than left as
   a footnote in a plan — because a reader who reaches §7 from the spec must not be sent to write a
   test that cannot fail.
2. **Task 4's `_UNRELATED_REMOVAL` fallback, as the brief wrote it, is self-contradictory** — and
   Task 2 is why. The brief asked for *"a path whose removal the exception does not mention, while
   the module still errors at collection for the original reason."* No such pair exists in the
   tracked tree any more: `baml_client` was the one always-broken import inside every M19 worktree,
   and Task 2 materialises it, so after that nothing in the tracked tree breaks a module's
   collection except a file that module actually reads or imports. The brief's fallback
   (*"force the same break by removing a file the module does not touch"*) is not constructible
   through `_ablate`'s signature: the only lever on the worktree is `removed_files`, so the break
   can only be forced by a removal, and a removal that forces the break is by definition one the
   module touches. **Task 4 substituted the harder satisfiable probe rather than weakening the
   assertion** — `tests/docgov_extract.py`, a removal that *did* cause the error whose exception
   says nothing about it — which is exactly the response CLAUDE.md § Plan authoring prescribes: a
   plan-supplied test is a proposition, and an implementer who cannot make it pass has found a plan
   defect, not a personal failure.
3. **Task 2's own materialisation destroyed the probe Task 4's brief assumed.** Worth stating as a
   sequencing lesson and not only as a fact about these two tasks: in a subagent-driven loop the
   *n*th task's fixture premises are measured against a tree the *n−1*th task has already changed,
   so a plan that names a probe must name the tree state it was measured in.
4. **Task 5 measured that limitation 4's literal reading is closed too**, one step past its own
   brief's framing. The brief scoped Step 1 to the library-code reading; Task 5 additionally
   measured the literal one — a criterion declaring a file physically under `src/`:
   without the `PYTHONPATH` prefix, `import iladub.ground` inside a worktree with
   `src/iladub/ground.py` deleted silently returns the **main tree's** copy; with it, the same
   import raises `ModuleNotFoundError`. A regular Python package resolves to a single directory, so
   once `<worktree>/src` outranks the `.pth`, a missing submodule there is not found anywhere else
   on `sys.path` — the import mechanism enforces it and the producer-side guard the old text
   recommended is moot for this mechanism.
5. **`9 endpoint criteria, 6.69 s` in shipped source was the 7-edge figure** (M7, Task 5): it
   counted `holon:02`, whose edge the same paragraph already says was deleted. Re-derived with the
   module's own helpers over the live manifest — `6 edges 8 endpoints 10 ids 4 modules` — and the
   wall-clock re-timed against the *shipped* instrument (control + ablation) at ≈9.3 s, since Task
   3 added `_run_control` ahead of the ablation loop. Filed as a second instance of [[R120]]'s
   class, in the same docstring, found on a different day by a different review.
6. **The measured cost of the control is +2.90 s** (6.14 s → 9.04 s on
   `test_m19_the_live_manifest_carries_no_refuted_edge`, one run each side of `2d08f06`/`95bfb9a`):
   four subprocess startups plus one `git worktree add`/`remove` pair, not M6's 0.52 s single
   combined invocation. **This is a report of a measured cost, not a threshold** — nothing in the
   code compares against it, and Global Constraint 3 forbids it becoming one.
7. **The register's strike convention was over-read once and corrected** (Task 5, self-review):
   closed rows are struck in the two DETAIL files and left **plain** in the 3-column index, because
   the index's own `awk` self-verification matches only unstruck `R<n>` at line start. A literal
   reading of CLAUDE.md's *"strikes the number"* would have quietly defeated the register's own
   tooling.
8. **The two `_scores:219-226` cross-references are corrected to `_scores:440-446`, and the target
   was located by content rather than carried.** Both sentences describe *"the same shape … for an
   unresolved node id"*, which is the `if unresolved: raise RuntimeError(…)` block — at `:243-249`
   in the pre-loop file (the range spec §3 itself cites) and at **`:440-446`** now, verified in the
   file after the edit. Task 4's report and the controller's brief both proposed `:412-418`; that
   range is the **§4.5 collection-ERROR raise** Task 4 itself added, a *different* raise in the same
   function, so it is not what either sentence points at. Both sites were fixed in one pass — a
   reviewer had already flagged that fixing one and leaving the other is worse than leaving both.

---

## §9 The rows raised

Tally re-run at the moment of raising, so the snapshot is measured and not copied from a
neighbouring row:

```
$ awk -F'|' '/^\| R[0-9]/ {gsub(/ /,"",$3); print $3}' docs/superpowers/residues.md | sort | uniq -c
  24 closed
  87 open
$ for f in residues-open.md residues-closed.md; do echo -n "$f: "; grep -cE '^\| ~?~?R[0-9]' docs/superpowers/$f; done
residues-open.md: 87
residues-closed.md: 24
```

Both rows therefore carry `(24/111 closed)`.

* **[[R122]] (24/111 closed)** — *after §4.1 re-roots `src/`, is any oracle still resolving
  evidence to the main tree?* The question spec §9 declines. Two resolution styles were inventoried
  and closed; a third is not ruled out and nothing in this repo would notice one. Closed by a
  one-shot audit inside an ablated worktree that records every path the endpoint oracles open and
  refuses any outside the worktree root. DoD item 4.
* **[[R123]] (24/111 closed)** — a declared `prog:oracleArtifact` that is a **Python module** is
  genuine consumption §4.5 refuses to score, and the census that dismissed it as hypothetical is
  refuted: 2 of the 29 are `.py` today (§6.2). Latent — neither declaring criterion is an edge
  endpoint — and safe in direction, but measured rather than imagined.

The register moves to **113 rows, 24 closed, 89 open**; the headline sentence and its embedded
`awk` self-verification block were both re-run and updated.

---

## §10 Definition of done, item by item (spec §8)

| # | item | where |
| --- | --- | --- |
| 1 | §4.1–§4.5 implemented, each with §7 falsification evidence | §2, §3 (F1–F5) |
| 2 | `ablation_refusals` re-run over the LIVE manifest, result reported whatever it is; a newly grounding pair is a FINDING, never an edge | §5 — **`[]`**, plus the `holon:02` re-probe and an explicit statement of what the comparison does not cover |
| 3 | `pytest --collect-only -q` in a shipped-`_ablate` worktree reports **0** errors (from 6) | §4 — 0 errors, 1320 collected, both with and without `PYTHONPATH` |
| 4 | a residue row raised for the question the loop declines to ask | §9 — [[R122]] (and [[R123]] beside it) |
| 5 | the §6 corrections landed in the TRACKED artifacts, not only in the spec | §2's last two rows; Task 5's report for the row-by-row detail |
| 6 | real tree `git status --porcelain`-clean before and after every M19 run | §7 |
| 7 | every number re-derived at implementation time | throughout; the two the spec marked MEASURE (§2.6's 1293/1314 and §2.4's 29) were re-derived in §4 and §6.2, and §6.2's re-derivation **refuted** a claim laid over the second |

**What this loop did not do**, restated so the next one does not assume otherwise: it asserts no
new edge and predicted zero (§5); it does not make the `etkl` rung internally assertable (A6
forbids it permanently); it does not close [[R113]], [[R114]], [[R115]], [[R116]], [[R117]],
[[R119]] or [[R120]]; it fetches no corpus, adds no CI job, changes no workflow, and moves no
`prog:met` value.
