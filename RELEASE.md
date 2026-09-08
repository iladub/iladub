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

   If it lists blockers, fix the affected published page(s) in this release,
   then **record the drain** — one `docgov:ContradictionDrain` per blocking
   document, in `tests/docgov-drains.ttl`. Nothing else clears the gate: the
   declaring spec cannot drain itself, and editing its `Doc impact:` line is
   forbidden (it is Evidence). Each drain names the document, the date the PAGE
   was fixed (from git, not today), who ruled it drained, and what makes the
   claim true. The membrane refuses a drain missing any of those, one naming a
   document that declared no contradiction, or one predating its document.

   **The one thing this gate cannot catch is a drain recorded without fixing
   the page** — SHACL cannot read prose. The record is dated and attributed so
   that the judgement is answerable; it is not evidence that the judgement was
   right. See `docs/superpowers/specs/2026-09-08-the-drain-is-a-release-act-design.md` §3.3.

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
