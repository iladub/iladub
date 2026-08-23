"""M19 — A5's two-sided ablation: the leg that grounds the DIRECTION of a dependency edge.

**Gate classification (CLAUDE.md §8): PROCEDURAL, and here is why it is irreducible.**
M12–M18 (`tests/arc-shapes.ttl`) are AXIOM / constraint, closed world: a dependency edge is a
triple, so a membrane can see it, and everything checkable in the membrane stays there. M19 is
the one refusal of spec 2026-08-22 §5 that no SHACL engine can make, because the question it
asks is not about the graph at all:

    delete a criterion's `prog:oracleArtifact` FILES from a second checkout of the tree,
    then run another criterion's `prog:oracleTest` node ids as a SUBPROCESS
    and read the EXIT CODE.

A filesystem mutation is not a triple and a process exit status is not a triple. Inventing
triples that mirror them would be deriving-by-absence — the move CLAUDE.md §8 forbids the
membrane — and a *stored* record of a past ablation would be a stored label for a derived fact,
which spec §3 refuses for the same reason it refuses `risk:RiskAssessment` as a stored label:
true on the day it is written, unfalsifiable afterwards. **The CI run IS the grounding.** So
this leg is procedural, and it is procedural for a reason that is stated rather than assumed.

**It derives nothing into either manifest.** Like `tests/test_arc_manifest.py`, this module
never writes `tests/arc-manifest.ttl` (Global Constraint 4; spec §9, the `cor:` precedent). It
returns refusals for a hand to resolve in a reviewed commit.

**Why a module of its own, and not beside M5/M5b/M5c/M7/M10.** The split is by COST, not by
concern: `tests/test_arc_manifest.py`'s environment leg runs in under a second, while this one
creates `git worktree`s and spawns pytest subprocesses inside them. Mixing them would change
the membrane module's cost profile for every developer who runs it. Both legs are procedural
and both answer questions about the environment; only the price differs.

---

**What A5 says (spec §4), and why BOTH arms exist.** For an asserted `X prog:dependsOn Y`:

  * **arm 1** — remove **Y's** artifacts ⇒ **X's** oracle test must **FAIL**. X consumes Y.
  * **arm 2** — remove **X's** artifacts ⇒ **Y's** oracle test must **PASS**. Y does not
    consume X.

Arm 1 alone establishes *coupling* and says nothing about which way round it runs; the pair
establishes direction, with no appeal to dates. If both arms fail the coupling is symmetric,
which is not a dependency: the edge is refuted, not demoted to a proposition.

**Grouping is by CRITERION, not by file** (plan §0/C2, which supersedes spec §4's per-file
"11 worktrees"): one worktree per criterion C that is an endpoint of an asserted edge, with
**all** of C's artifact files removed at once. Inside it, arm 1 runs the oracles of every X
with `X dependsOn C`, and arm 2 the oracles of every Y with `C dependsOn Y`. The bound is the
number of endpoint criteria — at most 17 for the current met set — whatever the edge count.

**ONE PYTEST SUBPROCESS PER MODULE. This is the correctness hazard of the whole file.**
MEASURED by Task 1 (`docs/superpowers/2026-08-22-worktree-oracle-seam.md`, § "An instrument
defect found and fixed during this task", with the full transcript): a single pytest invocation
carrying explicit node ids from SEVERAL modules exits `rc=4` and runs **none** of them when one
named module fails to import — and `--continue-on-collection-errors` does not rescue it. A
removed artifact is exactly what makes a module fail to import, so the combined shape would
silently report "no result" for a healthy sibling oracle. In arm 2, "no result" scored as a
pass turns a false edge green. Hence: one subprocess per module, per-id attribution read out of
pytest's own `-v` progress lines, and `_scores` **raises** rather than guessing when a
requested node id comes back with no outcome at all.

**Why the `-v` progress region and not the `-rA` short summary.** The summary cannot attribute a
SKIP to a node id at all — MEASURED, it renders one as `SKIPPED [1] tests/test_corpus.py:67: …`,
naming a *file and line* rather than the id that skipped, so a skipped oracle would be
unattributable however wide the terminal. The progress region does name the id. It is **not**
true, though, that the progress region is a simple `<id> <OUTCOME>` grid: it appends `(reason)`
to SKIPPED and XFAIL whenever the line fits the terminal, which is a real hazard the first
version of `_PROGRESS` was blind to. See that regex's own comment for the measurement and the
test that pins it.

**Four stated limitations.** None is hidden and none is worked around:

  1. **The worktree is checked out at `HEAD`, so M19 validates the COMMITTED tree.**
     Uncommitted edits to an artifact are invisible to it, and an artifact that exists in the
     working tree but not at `HEAD` makes the ablation vacuous — so that case raises loudly
     instead of scoring.
  2. **A6 (artifact-file disjointness) is necessary but NOT sufficient**, and this bounds what
     arm 1 grounds. Task 1 measured **44** ordered cross-criterion blast-radius pairs in the
     met set, of which **18 share no declared `prog:oracleArtifact` file at all** — because
     some oracle tests load a wider shape/knowledge graph than their criterion declares
     (`tests/test_escalation_shacl.py::test_escalation_conformant_passes` loads
     `dec-shapes.ttl` as well as `escalation-shapes.ttl`; `tests/test_hga_alignment.py`'s tests
     build a graph wider than any one criterion's artifact). So arm 1 can FAIL for a reason
     unrelated to the edge, and the pairs it can happen for are named in Task 1's matrix. M19
     cannot fix this at file granularity; it is a limit on the *reading* an arm-1 failure
     supports, and Task 4 needs it when grading an edge asserted-vs-proposed.
  3. **Grounding is to FILE granularity** (spec §4's own stated limitation): `X dependsOn
     dec:01` is demonstrated as "X consumes `dec-shapes.ttl`", not as "X consumes the shape at
     line 15". Ablation deletes files.
  4. **THE ABLATION IS NOT HERMETIC FOR `src/`: the editable install is never ablated, and this
     is the only limitation here that can produce a FALSE GREEN.** MEASURED in this tree:
     `.venv/lib/python3.*/site-packages/_editable_impl_iladub.pth` carries the **absolute
     main-tree** path `…/iladub/src`, and `pyproject.toml:98` sets `pythonpath = ["."]` — the
     worktree *root*, never `worktree/src`. So `import iladub` inside a worktree resolves to the
     main tree, even for a module deleted from the worktree:

         $ git worktree add --detach $WT HEAD && rm -rf $WT/src/iladub/ground.py
         $ cd $WT && …/iladub/.venv/bin/python -c "import iladub.ground as g; print(g.__file__)"
         /Volumes/WD Green/dev/git/iladub/src/iladub/ground.py     # the MAIN tree's copy

     **No live impact today, and that too is measured:** all 35 distinct `prog:oracleArtifact`
     values in `tests/arc-manifest.ttl` live under `vocab/` (14), `examples/` (12) and `tests/`
     (9) — **zero** under `src/`. Non-`src/` artifacts ablate correctly, because pytest's rootdir
     *is* the worktree (Task 1's `tab:06` `COLLECT_ERROR` row is the positive evidence).
     **The failure scenario, stated so a later author cannot walk into it unwarned:** a criterion
     declares e.g. `src/iladub/ground.py:199` — a natural thing to declare, since `dec:08`'s
     epistemics live there. M19 deletes that file inside the worktree; the oracle imports the
     main tree's surviving copy and **PASSES**. Arm 2 (`C dependsOn Y` ⇒ Y's tests must PASS)
     therefore goes green on a file that was never effectively removed, and a false edge is
     **asserted**. Arm 1 would spuriously refute, which is the safe direction; arm 2 is the
     unsafe one — exactly the direction the producer-side guards below exist to protect.
     Do not declare a `src/` artifact on a criterion that is an edge endpoint until `_ablate`
     carries a producer-side refusal for a removed path that lies under a directory named by a
     `.pth` on `sys.path` — the same shape as the two guards already there.

**No tuned constant, threshold or tolerance** (Global Constraint 3), and **no subprocess
timeout**: any wall-clock number here would be exactly the tuned constant CLAUDE.md §8 calls
prima facie evidence of a misclassified decision, and the liveness bound that already exists
— CI's own job timeout — costs nothing and decides nothing. A `SKIPPED` or otherwise
non-executed oracle is scored as neither pass nor fail: it grounds nothing, so it refuses the
edge, and says so in its own words.

The `<path>:<line>` suffix is stripped with `tests/test_arc_manifest.py`'s `_LINE_SUFFIX`,
IMPORTED rather than restated — R109 is open because this repo already carries divergent
pointer parsers, and a fourth copy here would be the next one.

Run: ./.venv/bin/python -m pytest tests/test_arc_ablation.py -q
NEVER `python3` (Global Constraint 1) — it carries rdflib 7.1.4 and no pyrudof, and the
subprocesses this module spawns inherit `sys.executable`, so a foreign interpreter would
ablate against the wrong runner as well as read the manifest with it.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from unittest import mock

import pytest
from rdflib import RDF, Graph, Namespace

from tests.test_arc_manifest import (MANIFEST, REPO, _LINE_SUFFIX, oracle_rows,
                                     validate_manifest)

PROG = Namespace("https://w3id.org/iladub/progress#")

FIXTURE = REPO / "tests" / "arc-m19-false-edge-leak.ttl"

# pytest's own `-v` progress lines, one per executed test and ending in a percentage:
#     tests/test_risk.py::test_empiric_risk_stamp_rejected PASSED              [100%]
# Read out of pytest rather than inferred from the exit code, because an exit code cannot say
# WHICH id failed when one module carries two criteria's oracles.
#
# THE OPTIONAL `(reason)` IS LOAD-BEARING AND THE REGEX ONCE MISSED IT. MEASURED 2026-08-22 on
# pytest 9.0.3, the same node id under two terminal widths:
#     COLUMNS=80   …::test_expected_verdict[…] SKIPPED                          [ 14%]
#     COLUMNS=250  …::test_expected_verdict[…] SKIPPED (corpus not populated: … ) [ 14%]
# pytest prints the reason for SKIPPED/XFAIL **whenever the line fits the terminal** and drops
# it when it does not, so a pattern demanding the `[ nn%]` column immediately after the outcome
# token parses the SAME RUN differently depending on the window size. It never produced a false
# pass — the id came back unattributed and `_scores` raised — but "raises on a wide terminal,
# refuses politely on 80-column CI" is a defect, and it is not hypothetical: the 9 corpus oracle
# ids skip WITH a reason (`tests/test_corpus.py:67,69`), and `corpus/` is gitignored so they
# always skip inside a worktree. `.*` is greedy on purpose — the reasons themselves carry nested
# parens (`… (scripts/fetch_corpus.py))`), so the match must run to the LAST one on the line.
# `test_m19_reads_a_skip_that_carries_its_reason_at_any_terminal_width` pins both renderings.
_PROGRESS = re.compile(
    r"^(\S.*?) (PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)(?: \(.*\))?\s+\[\s*\d+%\]\s*$", re.M)
# …and the one thing the progress region cannot show, because the test never started: a module
# that failed to import. `ERROR tests/x.py - FileNotFoundError: …` in the summary.
_COLLECT_ERROR = re.compile(r"^ERROR (\S+)", re.M)

PASSED, FAILED = "passed", "failed"


# ------------------------------------------------------------------ the graph, read as rows

def asserted_edges(graph):
    """Every `X prog:dependsOn Y` as (X, Y) IRI strings, sorted. Propositions are NOT here.

    `prog:proposedDependsOn` is deliberately excluded: a proposition is the grade an author
    takes when the edge CANNOT be grounded, and running an ablation over it would either
    ground it — in which case M17 already refuses the proposition — or refute it, which is
    what the rationale already says. M19 disposes assertions and nothing else.
    """
    return sorted((str(x), str(y)) for x, y in graph.subject_objects(PROG.dependsOn))


def _oracles(graph):
    """{criterion_iri: (artifact_files, test_ids)} — line suffixes already stripped."""
    return {iri: (tuple(sorted({_LINE_SUFFIX.sub("", a) for a in artifacts})), tests)
            for iri, _met, artifacts, tests in oracle_rows(graph)}


# ------------------------------------------------------- the environment, measured not read

def _run_module(node_ids, cwd):
    """Run ONE module's node ids as ONE subprocess with `cwd` inside the worktree.

    Per-module and never wider: see this module's docstring for the measured reason. The
    interpreter is `sys.executable`, which is absolute and therefore unaffected by the
    worktree having no `.venv` of its own (measured, Task 1 § Step 2).

    [[R121]], spec §4.1: the editable install's `_editable_impl_iladub.pth` carries the MAIN
    tree's `src/`, so `import iladub` in the subprocess would otherwise resolve there instead of
    into `cwd` (the worktree), and every ablation would be silently reading unablated files. A
    plain path `.pth` is outranked by `PYTHONPATH`, so prepending `<cwd>/src` re-roots every
    import onto the worktree. Measured (Task 1 § Step 1): `PYTHONPATH` is unset in this
    environment, so there is nothing to preserve beyond appending it if it is ever set.
    """
    env = dict(os.environ)
    src = str(Path(cwd) / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = src if not existing else os.pathsep.join([src, existing])
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *node_ids,
         "-v", "--tb=no", "-p", "no:cacheprovider"],
        cwd=cwd, capture_output=True, text=True, env=env)
    reported = {}
    for node, outcome in _PROGRESS.findall(proc.stdout):
        reported.setdefault(node, []).append(outcome)
    return proc, reported


def _scores(module, node_ids, proc, reported):
    """{requested node id: PASSED | FAILED | a sentence saying it did not execute}.

    A requested id with NO reported outcome is an instrument failure, not a datum: it is the
    exact shape Task 1's combined-invocation defect produced, and scoring it either way would
    make an oracle that never ran decide an edge. So it RAISES, with the transcript attached,
    unless pytest itself reported the module as a collection ERROR — in which case every id
    the module was asked for is a genuine ablation signal (the test cannot even import once
    its artifact is gone) and scores as a failure.
    """
    collect_error = module in _COLLECT_ERROR.findall(proc.stdout)
    out, unresolved = {}, []
    for node in node_ids:
        # A parametrized oracle may be cited bare while pytest only ever reports its
        # parametrized ids (`tests/test_arc_manifest.py:231`). Both resolve; nothing else does.
        outcomes = [o for n, outs in reported.items() if n == node or n.startswith(node + "[")
                    for o in outs]
        if not outcomes:
            if collect_error:
                out[node] = FAILED
                continue
            unresolved.append(node)
        elif all(o == "PASSED" for o in outcomes):
            out[node] = PASSED
        elif any(o in ("FAILED", "ERROR") for o in outcomes):
            out[node] = FAILED
        else:
            out[node] = (f"did not execute — pytest reported {sorted(set(outcomes))}, which "
                         f"is neither a pass nor a failure and grounds nothing")
    if unresolved:
        raise RuntimeError(
            f"M19 instrument failure: {unresolved} were requested and pytest reported no "
            f"outcome for them. An oracle that never ran must never be scored (Task 1, "
            f"docs/superpowers/2026-08-22-worktree-oracle-seam.md § An instrument defect).\n"
            f"exit={proc.returncode}\nSTDOUT\n{proc.stdout[-3000:]}\nSTDERR\n"
            f"{proc.stderr[-3000:]}")
    return out


def _ablate(removed_files, node_ids, repo=REPO):
    """Run `node_ids` in a throwaway worktree of `repo` @ HEAD with `removed_files` deleted.

    THE SAFETY PROPERTY: the real tree is never mutated. Every deletion happens inside the
    worktree, and `git worktree remove --force` runs in a `finally`, so a crashed subprocess
    — or an exception raised by `_scores` — cannot leave the repository broken.
    """
    parent = Path(tempfile.mkdtemp(prefix="arc-m19-"))
    wt = parent / "wt"
    try:
        subprocess.run(["git", "worktree", "add", "--detach", str(wt), "HEAD"],
                       cwd=repo, capture_output=True, text=True, check=True)
        for f in removed_files:
            target = wt / f
            if not target.exists():
                raise RuntimeError(
                    f"M19 cannot ablate {f!r}: it is absent from a worktree checked out at "
                    f"HEAD. M19 validates the COMMITTED tree (see this module's docstring), "
                    f"so an uncommitted artifact makes the ablation vacuous rather than "
                    f"negative — commit it, or do not assert an edge that depends on it")
            target.unlink()
        by_module = defaultdict(list)
        for node in node_ids:
            by_module[node.split("::", 1)[0]].append(node)
        scored = {}
        for module, ids in sorted(by_module.items()):
            proc, reported = _run_module(ids, wt)
            scored.update(_scores(module, ids, proc, reported))
        return scored
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)],
                       cwd=repo, capture_output=True, text=True)
        shutil.rmtree(parent, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], cwd=repo, capture_output=True, text=True)


# ------------------------------------------------------------------------- the one refusal

def ablation_refusals(graph):
    """Every M19 refusal this graph's asserted edges earn. Empty == admitted.

    Mirrors `environment_refusals` (`tests/test_arc_manifest.py:294`) deliberately: a list of
    sentences, each opening `"M19: "`, so the fixture helper pattern transfers unchanged.

    One worktree per endpoint criterion (plan §0/C2). A criterion that is both a source and a
    target of asserted edges is ablated ONCE and scored for both arms out of the same run.
    """
    edges = asserted_edges(graph)
    if not edges:
        return []
    oracles = _oracles(graph)
    ends = {e for edge in edges for e in edge}
    dangling = sorted(ends - set(oracles))
    # NOT a refusal of M19's — M12 owns the dangling target and refuses it in the membrane,
    # where it belongs. This only says so legibly instead of raising a bare KeyError two
    # frames down, and it never invents an M-numbered refusal for a graph SHACL already
    # rejects (that would be two refusals answering one question).
    assert not dangling, (
        f"M19 was handed edges whose ends are not declared prog:Criterion subjects: "
        f"{dangling}. That is M12's refusal, in tests/arc-shapes.ttl — validate the graph "
        f"through the membrane before asking the ablation to run against it")

    # …and the same shape for A2, which is M16's refusal. BOTH ends of an edge are RUN: the
    # source in arm 1 (inside the target's worktree) and the target in arm 2 (inside the
    # source's). An end with no prog:oracleTest therefore contributes an EMPTY result set, and
    # arm 2's `broken` list — computed by filtering that set — comes back empty, so the edge is
    # ADMITTED having been tested by nothing. (Arm 1 is safe by luck of the quantifier: `all()`
    # over an empty set is True, so a testless source refutes rather than admits.)
    #
    # This is a producer-side guard that the membrane also enforces, and CLAUDE.md § "Producer-
    # side guards vs the membrane" is why it stays: `ablation_refusals` is a public entry point
    # that any caller may reach without validating first, so total coverage by the membrane is
    # not provable here — and the failure it prevents is silent admission, which is the one
    # direction that must never happen. It fails at the call site that handed in the bad graph,
    # naming the refusal that owns the question.
    testless = sorted(e for e in ends if not oracles[e][1])
    assert not testless, (
        f"M19 was handed edges whose ends carry no prog:oracleTest: {testless}. Both ends of "
        f"an edge are RUN — the source in arm 1, the target in arm 2 — so an end with no "
        f"oracle would make arm 2 vacuously green. That is M16's A2 precondition, in "
        f"tests/arc-shapes.ttl; validate the graph through the membrane first")
    sources, targets = defaultdict(list), defaultdict(list)
    for x, y in edges:
        sources[y].append(x)      # arm 1: remove y, run x
        targets[x].append(y)      # arm 2: remove x, run y

    out = []
    for c in sorted(set(sources) | set(targets)):
        removed, _ = oracles[c]
        run_for = {other: oracles[other][1]
                   for other in sorted(set(sources[c]) | set(targets[c]))}
        scored = _ablate(removed, sorted({t for ts in run_for.values() for t in ts}))

        for x in sorted(sources[c]):
            results = {t: scored[t] for t in run_for[x]}
            if all(r == PASSED for r in results.values()):
                out.append(
                    f"M19: arm 1 refutes {x} prog:dependsOn {c} — with {c}'s artifacts "
                    f"{list(removed)} removed, every one of {x}'s oracle tests still passes "
                    f"({results}), so {x} does not consume {c}")
            for t, r in sorted(results.items()):
                if r not in (PASSED, FAILED):
                    out.append(f"M19: arm 1 cannot judge {x} prog:dependsOn {c} — {t} {r}")

        for y in sorted(targets[c]):
            results = {t: scored[t] for t in run_for[y]}
            broken = sorted(t for t, r in results.items() if r == FAILED)
            if broken:
                out.append(
                    f"M19: arm 2 refutes {c} prog:dependsOn {y} — with {c}'s artifacts "
                    f"{list(removed)} removed, {y}'s oracle tests {broken} fail too, so the "
                    f"coupling is symmetric and this is not a dependency")
            for t, r in sorted(results.items()):
                if r not in (PASSED, FAILED):
                    out.append(f"M19: arm 2 cannot judge {c} prog:dependsOn {y} — {t} {r}")
    return out


# ------------------------------------------------------------------------------- the tests

def test_m19_an_edge_the_membrane_admits_and_the_ablation_refutes():
    """The negative fixture, and the only thing that says M19 can refuse anything at all.

    `dec:11 prog:dependsOn dec:03` satisfies A1–A4 and A6, so Task 2's membrane ADMITS it —
    asserted first, because an M19 refusal of a graph SHACL already refuses would be evidence
    about neither leg. `test_risk.py` does not load `dec-shapes.ttl` or either heart-timeline
    example, so with dec:03's three artifacts gone dec:11's oracles still pass, and arm 1
    refutes the reading.

    Exactly one refusal, and it must name both ends AND the arm: an ablation with one working
    arm grounds adjacency, not direction (spec §2's Q2 finding), so a message that does not
    say which arm spoke leaves the reader unable to tell coupling from dependence.
    """
    ok, report = validate_manifest(FIXTURE)
    assert ok, (f"{FIXTURE.name} must be SHACL-clean so that only M19 can refuse it; the "
                f"graph membrane already objects:\n{report}")

    reasons = ablation_refusals(Graph().parse(FIXTURE, format="turtle"))
    assert len(reasons) == 1, reasons
    (reason,) = reasons
    assert reason.startswith("M19: arm 1 refutes "), reason
    for end in ("criterion:dec:11", "criterion:dec:03"):
        assert end in reason, f"M19 must name both ends of the edge it refutes: {reason}"


def test_m19_refuses_to_run_against_a_graph_the_membrane_would_have_stopped():
    """The two PRODUCER-SIDE GUARDS, and why they are not duplicates of M12 and M16/A2.

    CLAUDE.md § "Producer-side guards vs the membrane": a guard the membrane also enforces earns
    its place when the membrane's total coverage of that producer is not provable.
    `ablation_refusals` is a public entry point — Task 4's tooling, a future query script, any
    caller — and nothing in its signature forces a `validate_manifest` first. So it checks the
    two things it cannot survive, and names the refusal that OWNS each question rather than
    minting a third M-number for a graph SHACL already rejects.

      * an end that is not a declared criterion — M12's refusal. Without this it is a bare
        `KeyError` two frames down, with the manifest nowhere in the message.
      * an end carrying no `prog:oracleTest` — M16's A2. This one is not cosmetic: BOTH ends of
        an edge are run (the source in arm 1, the target in arm 2), so a testless end gives arm 2
        an EMPTY result set, `broken` comes back empty, and the edge is ADMITTED having been
        tested by nothing. **Silent admission is the one direction M19 must never fail in.**
        Arm 1 is safe only by luck of the quantifier — `all()` over an empty set refutes — and
        luck is not a guard, which is why this asserts rather than relying on it.

    Both graphs are built in memory from the LIVE manifest, so the only thing wrong with each is
    the end this test is about.
    """
    live = Graph().parse(MANIFEST, format="turtle")

    dangling = Graph() + live
    dangling.add((PROG["criterion:dec:11"], PROG.dependsOn, PROG["criterion:nope:99"]))
    with pytest.raises(AssertionError, match="not declared prog:Criterion subjects"):
        ablation_refusals(dangling)

    testless = Graph() + live
    testless.add((PROG["criterion:dec:99"], RDF.type, PROG.Criterion))
    testless.add((PROG["criterion:dec:11"], PROG.dependsOn, PROG["criterion:dec:99"]))
    with pytest.raises(AssertionError, match="carry no prog:oracleTest"):
        ablation_refusals(testless)


_SKIPS_WITH_A_REASON = "tests/test_corpus.py::test_expected_verdict"


def test_m19_reads_a_skip_that_carries_its_reason_at_any_terminal_width():
    """THE SAME RUN MUST NOT GET TWO ANSWERS DEPENDING ON THE WINDOW SIZE.

    pytest 9.0.3 appends `(reason)` to a `-v` SKIPPED/XFAIL line whenever the line fits the
    terminal and drops it when it does not, so terminal width silently changes the shape of the
    text M19 parses. The first version of `_PROGRESS` demanded the `[ nn%]` column immediately
    after the outcome token: on 80 columns it read the skip correctly, and on a wide terminal it
    matched nothing, `_scores` found the id unattributed, and M19 died with an instrument-failure
    RuntimeError instead of the refusal it documents. Never a false pass — but "raises at home,
    refuses on CI" is a defect, and it is squarely in Task 4's path: `corpus/` is gitignored, so
    every one of the 9 corpus oracle ids skips WITH a reason inside every worktree M19 creates.

    So this runs the real oracle in a real worktree TWICE, forcing each rendering, and demands
    the two agree. 80 and 250 are the two renderings, not a threshold: nothing is compared
    against them and no behaviour is tuned to either (CLAUDE.md §8).

    The assertion is on the OUTCOME, not on the text: a skip grounds nothing, so it must come
    back as the documented "did not execute" sentence — neither `PASSED` (which would admit an
    arm-2 edge on an oracle that never ran) nor a raise.
    """
    seen = {}
    for columns in ("80", "250"):
        with mock.patch.dict(os.environ, {"COLUMNS": columns}):
            seen[columns] = _ablate([], [_SKIPS_WITH_A_REASON])[_SKIPS_WITH_A_REASON]

    assert seen["80"] == seen["250"], (
        f"M19 read the same skipped oracle two different ways depending on terminal width: "
        f"{seen} — the `(reason)` pytest appends when the line fits is not optional text")
    for columns, verdict in sorted(seen.items()):
        assert verdict not in (PASSED, FAILED), (
            f"at COLUMNS={columns} a SKIPPED oracle was scored {verdict!r}; it executed nothing "
            "and must ground nothing")
        assert verdict.startswith("did not execute") and "SKIPPED" in verdict, (
            f"at COLUMNS={columns} the refusal must say what pytest actually reported, so a "
            f"reader can tell a skip from a failure: {verdict!r}")


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


def test_m19_the_live_manifest_carries_no_refuted_edge():
    """The live leg — AND IT IS NO LONGER VACUOUS. Task 4 authored the first edges.

    When this test shipped, `tests/arc-manifest.ttl` carried no `prog:dependsOn` at all and
    `ablation_refusals` returned `[]` without creating a single worktree; the docstring said so
    and the second assertion below existed to make the day that changed impossible to miss. That
    day was 2026-08-22: Task 4 of the same loop authored 7 asserted edges, M19 refuted one
    (`holon:02 -> holon:01`, arm 1 — holon:02's oracles never load `etkl-holons.ttl`), it was
    DELETED rather than demoted (plan §0/C4, because M17 refuses the demotion), and **6** remain.

    So this now creates real worktrees and runs real oracles. MEASURED 2026-08-22 over those 6
    edges: 9 endpoint criteria, 6.69 s wall-clock, real tree `git status --porcelain` clean
    throughout. The second assertion keeps stating the count the first one ran against — a
    guard against the gate silently going vacuous again if a future edit empties the section.
    """
    g = Graph().parse(MANIFEST, format="turtle")
    edges = asserted_edges(g)
    assert ablation_refusals(g) == [], (
        "every asserted prog:dependsOn must survive A5's two-sided ablation; an edge the "
        "ablation refutes is a reading to fix by hand in a reviewed commit — DELETE it (M17 "
        "refuses demoting a groundable pair to a proposition), or reverse it")
    assert edges, (
        "the live manifest carries 0 asserted prog:dependsOn edges, so the assertion above is "
        "VACUOUS. Task 4 of the 2026-08-22 loop authored 6; if they are gone, say so in a "
        "reviewed commit and update this test — do not let the gate quietly stop gating")
