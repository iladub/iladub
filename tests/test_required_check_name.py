"""The name of the required status check — the one rename that blocks every PR forever.

CLAUDE.md § Branch protection: since 2026-08-31 `main` is guarded by the repository ruleset
`main-requires-green-pr` (id 21898723, `enforcement: active`, `bypass_actors: null`). Its
required check is the literal string **`test`**, bound to GitHub Actions by
`integration_id: 15368`:

    $ gh api repos/iladub/iladub/rules/branches/main
      … "required_status_checks": [{"context": "test", "integration_id": 15368}] …

Nothing supplies that string except the JOB name at `.github/workflows/ci.yml`'s `jobs:` key.
GitHub reports a check run under the job's name, so **renaming the job renames the check**, the
ruleset goes on waiting for a `test` that will never arrive, and every pull request is
`BLOCKED` with no red test to explain why. The bypass list is empty by design, so the escape
hatch is deleting the rule — an owner-only action on a User-account repo, which no collaborator
token can perform. CLAUDE.md states this hazard in prose twice and **nothing enforced it**
(measured 2026-08-31: `grep -rn "ci.yml\\|workflows" tests/ --include="*.py"` returned one
docstring in `tests/test_arc_landscape.py` citing what the CI *command* is, not the job name).

The second arm is the same failure by a different route: a workflow that no longer runs on
`pull_request` reports no check on a PR at all, so the required context never arrives and the
PR blocks exactly as if the job had been renamed.

**Gate classification (CLAUDE.md §8): PROCEDURAL, and irreducible for the reason M7 states in
`tests/test_arc_manifest.py`.** The subject is a YAML file on the filesystem and a rule held in
GitHub's API — neither is a triple, no shape can target either, and minting triples to mirror
them would put a derived copy under the membrane while the originals stayed unguarded. No tuned
constant, no reading judgment: two equality checks against a string this docstring cites.

WHAT THIS DOES NOT CHECK: that the ruleset still names `test`. That lives in GitHub, not in the
working tree, and reading it needs a network call and a token — so this guard pins the half that
is in the repo, and the other half is pinned by the ruleset payload recorded in CLAUDE.md
§ Open items. If the ruleset is ever changed to require a different context, this test is the
file to update, and its failure is the intended way to find that out.
"""
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CI = REPO / ".github" / "workflows" / "ci.yml"

# The context the ruleset requires. Cited from the payload in CLAUDE.md § Open items, which is
# itself a `gh api …/rules/branches/main` transcript, not a recollection.
REQUIRED_CHECK = "test"


def _workflow():
    return yaml.safe_load(CI.read_text(encoding="utf-8"))


def _triggers(cfg):
    """YAML 1.1 parses a bare `on:` key as the boolean True, so accept either spelling."""
    return cfg.get("on", cfg.get(True))


def test_ci_defines_a_job_named_exactly_test():
    jobs = _workflow().get("jobs") or {}
    assert REQUIRED_CHECK in jobs, (
        f"{CI.relative_to(REPO)} defines jobs {sorted(jobs)!r} — none named "
        f"{REQUIRED_CHECK!r}. The `main-requires-green-pr` ruleset requires a check with that "
        f"exact context and its bypass list is empty, so every PR would block forever on a "
        f"check that never arrives. Rename the job back, or change the ruleset FIRST "
        f"(owner-only) and update this test with the new payload")


def test_ci_still_runs_on_pull_requests():
    triggers = _triggers(_workflow())
    assert triggers is not None and "pull_request" in triggers, (
        f"{CI.relative_to(REPO)} no longer triggers on pull_request (triggers: {triggers!r}). "
        f"The required check {REQUIRED_CHECK!r} would then never be reported on a PR at all, "
        f"which blocks the merge exactly as a rename does")
