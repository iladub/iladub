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

**Three stated limitations.** None is hidden and none is worked around:

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
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Namespace

from tests.test_arc_manifest import (MANIFEST, REPO, _LINE_SUFFIX, oracle_rows,
                                     validate_manifest)

PROG = Namespace("https://w3id.org/iladub/progress#")

FIXTURE = REPO / "tests" / "arc-m19-false-edge-leak.ttl"

# pytest's own `-v` progress lines, one per executed test and ending in a percentage:
#     tests/test_risk.py::test_empiric_risk_stamp_rejected PASSED              [100%]
# Read out of pytest rather than inferred from the exit code, because an exit code cannot say
# WHICH id failed when one module carries two criteria's oracles. The `-rA` short summary is
# NOT the source here: MEASURED 2026-08-22, it renders a skip as `SKIPPED [1] file.py:67: …`,
# with no node id at all, so a skipped oracle would come back unattributable.
_PROGRESS = re.compile(
    r"^(\S.*?) (PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\s+\[\s*\d+%\]\s*$", re.M)
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
    """
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *node_ids,
         "-v", "--tb=no", "-p", "no:cacheprovider"],
        cwd=cwd, capture_output=True, text=True)
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
    dangling = sorted({e for edge in edges for e in edge} - set(oracles))
    # NOT a refusal of M19's — M12 owns the dangling target and refuses it in the membrane,
    # where it belongs. This only says so legibly instead of raising a bare KeyError two
    # frames down, and it never invents an M-numbered refusal for a graph SHACL already
    # rejects (that would be two refusals answering one question).
    assert not dangling, (
        f"M19 was handed edges whose ends are not declared prog:Criterion subjects: "
        f"{dangling}. That is M12's refusal, in tests/arc-shapes.ttl — validate the graph "
        f"through the membrane before asking the ablation to run against it")
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


def test_m19_the_live_manifest_carries_no_refuted_edge():
    """The live leg — and TODAY IT IS VACUOUS, deliberately, which a later reader must not
    mistake for evidence.

    `tests/arc-manifest.ttl` carries no `prog:dependsOn` at this commit (Task 4 of the
    2026-08-22 loop authors the first edges), so `ablation_refusals` returns `[]` without
    creating a single worktree. The assertion below is the loop's REAL gate the moment Task 4
    lands, and nothing about it changes then — which is why it ships now rather than being
    written against edges that do not exist yet.

    The second assertion is what keeps the vacuity honest rather than hidden: it states the
    edge count this test ran against, so the day the count moves off zero the docstring above
    stops being true and this line is what says so.
    """
    g = Graph().parse(MANIFEST, format="turtle")
    edges = asserted_edges(g)
    assert ablation_refusals(g) == [], (
        "every asserted prog:dependsOn must survive A5's two-sided ablation; an edge the "
        "ablation refutes is a reading to fix by hand in a reviewed commit — demote it to "
        "prog:proposedDependsOn with a rationale, or reverse it")
    assert len(edges) == 0, (
        "MEASURED 2026-08-22: the live manifest carries 0 asserted edges, so the assertion "
        f"above is VACUOUS. It now carries {len(edges)} — update this test's docstring: the "
        "gate has become real and the vacuity note is stale")
