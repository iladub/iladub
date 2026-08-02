# Releasing iladub

A release is the promotion campaign (governance spec 2026-07-31 §7): the one
accountable act that changes iladub.dev and PyPI. The tag drives everything —
`.github/workflows/release.yml` tests, gates, builds, smoke-checks, deploys
the site, and publishes the package.

## One-time prerequisite (manual, pypi.org)

PyPI → project `iladub` → Publishing → add a **Trusted Publisher**:
owner `iladub`, repository `iladub`, workflow `release.yml`, environment blank.
Without this, the publish step fails with an OIDC error; everything before it
(site deploy included) still completes.

## Per release

1. **Drain the promotion queue.** See what the lint reports:

       .venv/bin/python -m pytest tests/test_doc_governance.py -q -W default::UserWarning

   For each queued page you choose to promote THIS release: author/refresh the
   state-page prose it feeds, set `promoted_to:` in the wiki page's frontmatter,
   update its `updated:`. Unpromoted pages stay queued — the queue is the
   visible, enumerable lag (spec §5), not a blocker.
   Doctrine pages change only if a decision changed.

2. **Check the contradiction gate** (also enforced by the tag build):

       .venv/bin/python scripts/release_gate.py

   If it lists blockers, fix the affected published page(s) in this release.

   Also eyeball any spec/plan declaring `Doc impact: contradiction` dated the
   SAME day as the previous release tag — the gate's day-granularity comparison
   misses those (R26).

3. **Bump the version** — it must be single-sourced across three files, all in
   lockstep (guarded by `tests/test_smoke.py::test_version_single_source`):
   `pyproject.toml` (`project.version`), `src/iladub/__init__.py`
   (`__version__`), and `CITATION.cff` (`version:` and `date-released:`).

4. **Full suite + strict site build:**

       .venv/bin/python -m pytest -q
       .venv/bin/python -m mkdocs build --strict

5. **Tag and push** (the tag must equal `v<version>`; annotated, on main):

       git tag -a v0.0.3 -m "iladub v0.0.3"
       git push origin main v0.0.3

6. **Watch the run:** `gh run watch` — the pipeline order is
   version-guard → tests → gate → build → w3id smoke → deploy → PyPI.
   The non-blocking live probe at the end may WARN while GitHub Pages
   rebuilds; re-check https://iladub.dev after a few minutes.
