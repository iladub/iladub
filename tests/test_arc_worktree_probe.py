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
