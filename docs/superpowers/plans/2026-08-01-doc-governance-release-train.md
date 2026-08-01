# Documentation Governance — Phase 2 (Release Train) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the CI + tag-driven release pipeline (spec §7, §8 items 6–7) and the declarative doc-impact facts it gates on (residues R21 + R22) — after this plan, `pytest` runs on every push/PR, and a `v*` tag tests, gates on undrained contradictions, builds the flat site, smoke-checks the w3id targets, deploys iladub.dev, and publishes to PyPI via trusted publishing.

**Architecture:** Task 1 makes the doc-impact rule declarative (extractor emits `dg:docDate` + the declared `dg:docImpact` value; the cutoff moves into the SHACL shape as a date FILTER; `dg:isEvidence` and dead `dg:navPath` are deleted). Task 2 builds the release gate (a SPARQL query + thin PROCEDURAL runner) on those facts. Tasks 3–5 add packaging extras and the two GitHub Actions workflows. Task 6 writes the release checklist as a new Manual and restores `CLAUDE.md`'s now-true CI claims.

**Tech Stack:** GitHub Actions (`actions/checkout@v4`, `actions/setup-python@v5`, `pypa/gh-action-pypi-publish@release/v1`), rdflib/pySHACL (already deps), `baml-cli 0.222.0` (regenerates the gitignored `baml_client/` — verified locally: `baml-cli generate --from baml_src` writes 14 files), mkdocs-material 9.7.x, `build` for sdist/wheel.

**Doc impact:** increment — CI/release machinery + two contract-truth corrections; no published page contradicted.

## Global Constraints

- **Neurosymbolic gate (CLAUDE.md §8):** the cutoff date and the impact-value vocabulary are MEMBRANE decisions → they live in SHACL (`sh:sparql` FILTER, value `IN` list), not Python. The extractor only emits facts (a date, a captured token). `scripts/release_gate.py` is a justified PROCEDURAL runner (git subprocess + query execution + exit code) and must say so in its docstring.
- **Checkout depth:** every workflow uses `fetch-depth: 0` — `extract()` raises `RuntimeError` on shallow clones (shipped Phase-1 guard).
- **Flat site, no `mike`:** the w3id redirects target flat paths; the smoke test asserts exactly `index.html`, `404.html`, `holonic-interaction/index.html`, `etkl/index.html`, `dec/index.html`, `assertion-proposition/index.html` in the local `site/` build output (pre-deploy, deterministic).
- **PyPI:** trusted publishing (OIDC, `id-token: write`), `skip-existing: true`, never a token secret. Package `iladub`, version currently `0.0.2` — this plan does NOT bump it and does NOT tag; the first tag (`v0.0.3`) is Phase 3's closing proof.
- **Residue register rule:** Task 1 closes R21 and R22 → it deletes those two rows from `docs/superpowers/residues.md` in the same commit.
- **Tests:** run with the repo venv — `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest …`. Full-suite baseline on `main`: 724 passed, 5 skipped.
- **Doc-impact registration:** after Task 1 lands, every spec/plan dated ≥ 2026-07-31 must carry a *parseable* `Doc impact:` value (`none|increment|contradiction`). The three existing dated docs (the governance spec, the Phase-1 plan, this plan) all declare `increment` — verify, don't assume, in Task 1 Step 4.
- **Commits:** conventional style (`feat(docgov): …`, `ci: …`, `docs: …`).

---

### Task 1: Declarative doc-impact facts (closes R21 + R22; deletes dead `dg:navPath`)

**Files:**
- Modify: `tests/docgov_extract.py` (constants block, `_evidence_facts`, `_wiki_facts`, `extract`)
- Modify: `vocab/shapes/doc-governance-shapes.ttl` (`dg:DocImpactShape` only)
- Modify: `vocab/queries/docgov-staleness-evidence.rq`, `vocab/queries/docgov-staleness-code.rq`
- Modify: `tests/test_docgov_extract.py`, `tests/test_docgov_shapes.py`, `tests/test_docgov_queries.py`
- Modify: `docs/superpowers/residues.md` (delete rows R21, R22)

**Interfaces:**
- Consumes: Phase-1 extractor (`_DATED` regex, `DG`, `doc_iri`, `extract`).
- Produces (Task 2 and the shapes rely on these): per dated spec/plan — `dg:docDate` (xsd:date, from the filename, emitted for EVERY dated spec/plan regardless of cutoff) and `dg:docImpact` (plain literal, only when the doc declares a valid value). REMOVED from the vocabulary: `dg:requiresDocImpact`, `dg:hasDocImpact`, `dg:isEvidence`, `dg:navPath`. Staleness queries now distinguish evidence from code via `?src dg:docClass "evidence"` (present on cited tracked-markdown sources because they share their IRI with their `dg:Document` node).

- [ ] **Step 1: Update the extractor tests** (in `tests/test_docgov_extract.py`)

Replace `test_extract_live_repo_smoke`'s doc-impact assertions and add a frontmatter-independent unit test. The live smoke test's nav/class assertions stay; delete any assertion mentioning `requiresDocImpact`/`hasDocImpact`. Add:

```python
def test_dated_spec_emits_docdate_and_impact():
    g = extract(REPO)
    spec = doc_iri("docs/superpowers/specs/2026-07-31-documentation-governance-design.md")
    assert (spec, DG.docDate,
            Literal(date(2026, 7, 31), datatype=XSD.date)) in g
    assert (spec, DG.docImpact, Literal("increment")) in g
    # undated evidence (e.g. residues.md) carries neither fact
    residues = doc_iri("docs/superpowers/residues.md")
    assert list(g.objects(residues, DG.docDate)) == []


def test_impact_value_is_first_valid_token_only():
    from tests.docgov_extract import _IMPACT
    assert _IMPACT.search("**Doc impact:** increment — adds X").group(1) == "increment"
    assert _IMPACT.search("Doc impact: contradiction\n").group(1) == "contradiction"
    assert _IMPACT.search("Doc impact: TBD") is None
    assert _IMPACT.search("no block at all") is None
```

Also update the module's imports (`date` from `datetime`, `XSD`) if not present, and remove `DOC_IMPACT_CUTOFF` from any import list.

- [ ] **Step 2: Run to verify failure**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_docgov_extract.py -q`
Expected: FAIL/ERROR (`_IMPACT` not defined; `docDate` triples absent).

- [ ] **Step 3: Rewrite the extractor facts**

In `tests/docgov_extract.py`:

1. Delete the `DOC_IMPACT_CUTOFF` constant and its comment (the cutoff now lives ONLY in the shape — R21).
2. Add next to `_DATED`:

```python
# First valid declared value wins; an invalid/missing declaration emits no fact,
# and the membrane fails it loudly (honest failure — R22).
_IMPACT = re.compile(r"\*{0,2}Doc impact:\*{0,2}\s*(none|increment|contradiction)\b")
```

3. Replace `_evidence_facts` entirely:

```python
def _evidence_facts(g: Graph, repo: Path, d: URIRef, path: str) -> None:
    m = _DATED.match(path)
    if not m:
        return
    g.add((d, DG.docDate,
           Literal(date(int(m[1]), int(m[2]), int(m[3])), datatype=XSD.date)))
    mi = _IMPACT.search((repo / path).read_text())
    if mi:
        g.add((d, DG.docImpact, Literal(mi.group(1))))
```

4. In `_wiki_facts`, delete the `dg:isEvidence` emission (the two lines adding `DG.isEvidence`).
5. In `extract()`, delete the `dg:navPath` emission line (dead predicate — final-review F6).

- [ ] **Step 4: Update shapes + queries**

Replace `dg:DocImpactShape` in `vocab/shapes/doc-governance-shapes.ttl` (keep its position and the surrounding comment style):

```turtle
# Doc-impact declaration is required for specs/plans dated >= 2026-07-31.
# The cutoff and the value vocabulary are MEMBRANE policy and live HERE, not in
# Python (R21/R22): the extractor only emits dg:docDate and the captured token.
dg:DocImpactShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:sparql [
        sh:message "spec/plan dated >= 2026-07-31 must declare 'Doc impact: none | increment | contradiction' (spec §5.1)" ;
        sh:select """
            SELECT $this WHERE {
                $this <https://w3id.org/iladub/docgov#docDate> ?d .
                FILTER (?d >= "2026-07-31"^^<http://www.w3.org/2001/XMLSchema#date>)
                FILTER NOT EXISTS {
                    $this <https://w3id.org/iladub/docgov#docImpact> ?v .
                    FILTER (?v IN ("none", "increment", "contradiction"))
                }
            }""" ;
    ] .
```

In `vocab/queries/docgov-staleness-evidence.rq`, replace the line `?src  dg:isEvidence     true ;` (and re-join) so the WHERE reads:

```sparql
WHERE {
    ?page dg:docClass "wiki" ;
          dg:updated  ?updated ;
          dg:cites    ?src .
    ?src  dg:docClass       "evidence" ;
          dg:lastCommitDate ?lastCommit .
    FILTER (?lastCommit > ?updated)
}
```

In `vocab/queries/docgov-staleness-code.rq`, replace the `dg:isEvidence false` join with a holon-scoped complement (update the header comment to note it):

```sparql
WHERE {
    ?page dg:docClass "wiki" ;
          dg:updated  ?updated ;
          dg:cites    ?src .
    ?src  dg:lastCommitDate ?lastCommit .
    # Holon-scoped closure over ONE source node (CLAUDE.md §8): a cited source
    # that is not an evidence-classed document is code/other → warning path.
    FILTER NOT EXISTS { ?src dg:docClass "evidence" }
    FILTER (?lastCommit > ?updated)
}
```

- [ ] **Step 5: Update the shapes + queries tests**

In `tests/test_docgov_shapes.py`: in `_wiki`, replace the source's `DG.isEvidence` line with `g.add((s, DG.docClass, Literal("evidence")))`. Replace `test_missing_doc_impact_after_cutoff_fails` with:

```python
def test_missing_doc_impact_after_cutoff_fails():
    g = Graph()
    d = _doc(g, "docs/superpowers/specs/2026-08-01-new-design.md", "evidence")
    g.add((d, DG.docDate, Literal("2026-08-01", datatype=XSD.date)))
    ok, report = _conforms(g)
    assert not ok and "Doc impact" in str(report)


def test_invalid_doc_impact_value_fails():
    g = Graph()
    d = _doc(g, "docs/superpowers/specs/2026-08-01-new-design.md", "evidence")
    g.add((d, DG.docDate, Literal("2026-08-01", datatype=XSD.date)))
    g.add((d, DG.docImpact, Literal("TBD")))
    assert not _conforms(g)[0]


def test_grandfathered_pre_cutoff_spec_passes():
    g = Graph()
    d = _doc(g, "docs/superpowers/specs/2026-07-01-old-design.md", "evidence")
    g.add((d, DG.docDate, Literal("2026-07-01", datatype=XSD.date)))
    assert _conforms(g)[0]


def test_declared_impact_after_cutoff_passes():
    g = Graph()
    d = _doc(g, "docs/superpowers/specs/2026-08-01-new-design.md", "evidence")
    g.add((d, DG.docDate, Literal("2026-08-01", datatype=XSD.date)))
    g.add((d, DG.docImpact, Literal("increment")))
    assert _conforms(g)[0]
```

Also update `test_conforming_minimal_graph`'s nav-entry fixture: drop the `DG.navPath` line (predicate deleted). Same in `test_unresolved_nav_entry_fails`.

In `tests/test_docgov_queries.py`: in `_wiki_citing`, replace the `DG.isEvidence` parameter/line — signature becomes `_wiki_citing(updated, src_path, src_date, evidence)` where `evidence: bool` now adds `g.add((s, DG.docClass, Literal("evidence")))` when True and adds no class triple when False. Test bodies keep their call sites (`True`/`False` args unchanged).

- [ ] **Step 6: Run all docgov tests + the live lint**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_docgov_extract.py tests/test_docgov_shapes.py tests/test_docgov_queries.py tests/test_doc_governance.py -q -W default::UserWarning`
Expected: all pass; live lint green (the three dated docs — governance spec, Phase-1 plan, this plan — all declare `increment`; verify the warning output still shows promotion queue = 1). If the membrane fails on a dated doc with an unparseable declaration, fix that DOC's `Doc impact:` line — never the regex.

- [ ] **Step 7: Delete residue rows R21 and R22**

In `docs/superpowers/residues.md`, delete the two full table rows starting `| R21 |` and `| R22 |` (register rule: the change that closes a residue deletes its row). Leave R23–R25 untouched.

- [ ] **Step 8: Commit**

```bash
git add tests/docgov_extract.py tests/test_docgov_extract.py tests/test_docgov_shapes.py tests/test_docgov_queries.py vocab/shapes/doc-governance-shapes.ttl vocab/queries/docgov-staleness-evidence.rq vocab/queries/docgov-staleness-code.rq docs/superpowers/residues.md
git commit -m "feat(docgov): declarative doc-impact — dg:docDate + declared dg:docImpact; cutoff moves into the membrane (closes R21, R22)"
```

---

### Task 2: The release gate — query + PROCEDURAL runner

**Files:**
- Create: `vocab/queries/docgov-release-gate.rq`
- Create: `scripts/release_gate.py`
- Test: `tests/test_release_gate.py`

**Interfaces:**
- Consumes: `dg:docImpact` / `dg:docDate` facts (Task 1), `extract(repo)` (Phase 1).
- Produces: `scripts/release_gate.py` — exit 0 (no undrained contradiction) / exit 1 (lists blocking docs); `release.yml` (Task 5) runs it as a blocking step. Internal: `_since_date(repo: Path) -> datetime.date` (previous release tag's commit date; fallback `date(2026, 7, 31)`).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_release_gate.py
"""Release gate (spec §7): a contradiction registered since the previous
release blocks the tag. Query tested on synthetic facts; _since_date on a
throwaway git repo (never the live one — its tag list changes over time)."""
import subprocess
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD

from tests.docgov_extract import DG, doc_iri
from scripts.release_gate import _since_date, blocking_docs

Q = Path(__file__).resolve().parent.parent / "vocab" / "queries" / "docgov-release-gate.rq"


def _spec(g, path, impact, when):
    d = doc_iri(path)
    g.add((d, RDF.type, DG.Document))
    g.add((d, DG.path, Literal(path)))
    g.add((d, DG.docDate, Literal(when, datatype=XSD.date)))
    g.add((d, DG.docImpact, Literal(impact)))
    return d


def test_contradiction_after_since_blocks():
    g = Graph()
    _spec(g, "docs/superpowers/specs/2026-08-02-x-design.md", "contradiction", "2026-08-02")
    assert blocking_docs(g, date(2026, 7, 31)) == [
        "docs/superpowers/specs/2026-08-02-x-design.md"]


def test_increment_and_old_contradiction_do_not_block():
    g = Graph()
    _spec(g, "docs/superpowers/specs/2026-08-02-y-design.md", "increment", "2026-08-02")
    _spec(g, "docs/superpowers/specs/2026-07-20-z-design.md", "contradiction", "2026-07-20")
    assert blocking_docs(g, date(2026, 7, 31)) == []


def _git(cwd, *args, when=None):
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "PATH": "/usr/bin:/bin", "HOME": str(cwd)}
    if when:  # backdate so the two tags carry DIFFERENT creatordates
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, env=env)


def test_since_date_fallback_and_previous_tag(tmp_path):
    _git(tmp_path, "init", "-q")
    (tmp_path / "f").write_text("x")
    _git(tmp_path, "add", "f")
    _git(tmp_path, "commit", "-qm", "one", when="2026-01-01T12:00:00")
    # no v* tags → governance-adoption fallback
    assert _since_date(tmp_path) == date(2026, 7, 31)
    _git(tmp_path, "tag", "v0.0.1")  # lightweight → creatordate = 2026-01-01
    (tmp_path / "f").write_text("y")
    _git(tmp_path, "add", "f")
    _git(tmp_path, "commit", "-qm", "two", when="2026-06-01T12:00:00")
    # HEAD untagged (dev run) → newest tag overall is the previous release
    assert _since_date(tmp_path) == date(2026, 1, 1)
    _git(tmp_path, "tag", "v0.0.2")
    # HEAD tagged (release run) → the HEAD tag (2026-06-01) is excluded;
    # v0.0.1 is the previous release. A broken exclusion would return 2026-06-01.
    assert _since_date(tmp_path) == date(2026, 1, 1)
```

- [ ] **Step 2: Run to verify failure**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_release_gate.py -q`
Expected: ERROR — `No module named 'scripts.release_gate'`.

- [ ] **Step 3: Write the query and the runner**

```sparql
# vocab/queries/docgov-release-gate.rq
# Derivation, OPEN WORLD (spec §7): the docs that block a release tag — specs/
# plans declaring 'Doc impact: contradiction' dated after the previous release
# (?since bound by the runner). Draining = the release that fixes the affected
# published page(s); the human confirms the fix via RELEASE.md before tagging.
PREFIX dg: <https://w3id.org/iladub/docgov#>
CONSTRUCT { ?doc dg:blocksRelease true }
WHERE {
    ?doc dg:docImpact "contradiction" ;
         dg:docDate   ?d .
    FILTER (?d > ?since)
}
```

```python
# scripts/release_gate.py
"""Release gate (spec §7) — PROCEDURAL runner (CLAUDE.md §8).

Justification: irreducible orchestration — reads git tag dates (subprocess),
executes the AXIOM query, and maps its result to a process exit code. The
gating RULE lives entirely in vocab/queries/docgov-release-gate.rq; nothing
here decides what blocks.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import XSD

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

QUERY = REPO / "vocab" / "queries" / "docgov-release-gate.rq"
GOVERNANCE_ADOPTED = date(2026, 7, 31)  # spec §5.1 grandfather line


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=True, check=True).stdout


def _since_date(repo: Path) -> date:
    """Commit date of the previous release tag (v*), excluding tags on HEAD
    (during a release run HEAD carries the tag being built)."""
    at_head = set(_git(repo, "tag", "--points-at", "HEAD", "--list", "v*").split())
    for line in _git(repo, "for-each-ref", "--sort=-creatordate",
                     "--format=%(refname:short) %(creatordate:short)",
                     "refs/tags/v*").splitlines():
        name, _, day = line.partition(" ")
        if name and name not in at_head:
            return date.fromisoformat(day)
    return GOVERNANCE_ADOPTED


def blocking_docs(facts: Graph, since: date) -> list[str]:
    from tests.docgov_extract import DG
    out = Graph()
    for t in facts.query(QUERY.read_text(),
                         initBindings={"since": Literal(since, datatype=XSD.date)}):
        out.add(t)
    docs = [str(next(facts.objects(s, DG.path))) for s in
            {s for s, _, _ in out.triples((None, DG.blocksRelease, None))}]
    return sorted(docs)


def main() -> int:
    from tests.docgov_extract import extract
    since = _since_date(REPO)
    blockers = blocking_docs(extract(REPO), since)
    if blockers:
        print(f"RELEASE BLOCKED — undrained contradiction(s) since {since}:")
        for p in blockers:
            print(f"  - {p}")
        print("Fix the affected published page(s) in this release, per RELEASE.md.")
        return 1
    print(f"release gate clear (no contradiction registered since {since})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Also create an empty `scripts/__init__.py` so `from scripts.release_gate import …` works under pytest.

- [ ] **Step 4: Run tests, then the runner live**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_release_gate.py -q`
Expected: 3 PASS.
Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python scripts/release_gate.py`
Expected: `release gate clear (no contradiction registered since 2026-07-31)`, exit 0.

- [ ] **Step 5: Commit**

```bash
git add vocab/queries/docgov-release-gate.rq scripts/__init__.py scripts/release_gate.py tests/test_release_gate.py
git commit -m "feat(docgov): release gate — contradiction-since-previous-tag query + PROCEDURAL runner (spec §7)"
```

---

### Task 3: Declare the dev/docs dependency extras

**Files:**
- Modify: `pyproject.toml` (`[project.optional-dependencies]`)

**Interfaces:**
- Produces: `pip install -e ".[baml,dev,docs]"` as the single install command both workflows use (Task 4/5 copy it verbatim).

- [ ] **Step 1: Add the extras**

In `pyproject.toml`, extend `[project.optional-dependencies]` (keep the existing `baml` list untouched):

```toml
dev = [
    "pytest>=8",
]
docs = [
    "mkdocs-material>=9.7",
]
```

(Locked-in versions in the venv: pytest 9.0.3, mkdocs-material 9.7.6 — floors chosen below them deliberately.)

- [ ] **Step 2: Verify resolvability without touching the venv**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pip install --dry-run -q -e ".[baml,dev,docs]" 2>&1 | tail -3`
Expected: resolves with no errors (everything already satisfied locally).

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "build: declare dev (pytest) and docs (mkdocs-material) extras for CI"
```

---

### Task 4: `ci.yml` — pytest + strict site build on every push/PR

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: the extras (Task 3); the shallow-clone guard (Phase 1) forces `fetch-depth: 0`.
- Produces: the required check future PRs ride on; `release.yml` (Task 5) mirrors its install block exactly.

- [ ] **Step 1: Write the workflow**

```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
    branches: [main]
  pull_request:
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # docgov extractor raises on shallow clones (R2 guard)
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install
        run: pip install -e ".[baml,dev,docs]"
      - name: Generate baml_client (gitignored; 6 test modules import it)
        run: baml-cli generate --from baml_src
      - name: Tests (incl. doc-governance lint)
        run: pytest -q
      - name: Site builds strict, internal trees excluded
        run: |
          mkdocs build --strict
          for d in wiki superpowers loops w3id; do
            test ! -d "site/$d" || { echo "LEAK: site/$d published"; exit 1; }
          done
```

- [ ] **Step 2: Validate the YAML locally**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('yaml ok')"`
Expected: `yaml ok`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: pytest + strict site build on push/PR (fetch-depth 0 for the docgov guard)"
```

(The live green run is verified once the branch is pushed — see Completion checklist; the execution session watches it with `gh run watch`.)

---

### Task 5: `release.yml` — the tag pipeline

**Files:**
- Create: `.github/workflows/release.yml`

**Interfaces:**
- Consumes: `scripts/release_gate.py` (Task 2), extras (Task 3), the same install block as `ci.yml` (Task 4).
- Produces: on tag `v*` — version guard → tests → release gate → strict build → w3id smoke → `mkdocs gh-deploy` (flat, to the existing `gh-pages` Pages branch; `docs/CNAME` is tracked so the domain survives) → PyPI via OIDC.

- [ ] **Step 1: Write the workflow**

```yaml
# .github/workflows/release.yml
name: release
on:
  push:
    tags: ["v*"]
permissions:
  contents: write  # mkdocs gh-deploy pushes the gh-pages branch
  id-token: write  # PyPI trusted publishing (OIDC)
concurrency:
  group: release
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # docgov extractor raises on shallow clones (R2 guard)
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Tag must match pyproject version
        run: |
          V=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
          test "v$V" = "$GITHUB_REF_NAME" || { echo "pyproject $V != tag $GITHUB_REF_NAME"; exit 1; }
      - name: Install
        run: pip install -e ".[baml,dev,docs]" build
      - name: Generate baml_client
        run: baml-cli generate --from baml_src
      - name: Tests (incl. doc-governance lint)
        run: pytest -q
      - name: Release gate — no undrained contradiction (spec §7)
        run: python scripts/release_gate.py
      - name: Build site (flat, from this tag)
        run: mkdocs build --strict
      - name: w3id smoke test — live redirect targets exist in the build
        run: |
          for p in index.html 404.html holonic-interaction/index.html \
                   etkl/index.html dec/index.html assertion-proposition/index.html; do
            test -f "site/$p" || { echo "w3id target missing: site/$p"; exit 1; }
          done
      - name: Deploy iladub.dev (gh-pages; docs/CNAME keeps the domain)
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          mkdocs gh-deploy --force
      - name: Build sdist + wheel
        run: python -m build
      - name: Publish to PyPI (trusted publishing; no-op if version exists)
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          skip-existing: true
      - name: Live w3id probe (non-blocking; Pages legacy build lags)
        continue-on-error: true
        run: |
          sleep 90
          for u in "" holonic-interaction/ etkl/ dec/ assertion-proposition/; do
            curl -sfI "https://iladub.dev/$u" > /dev/null \
              && echo "OK  /$u" || echo "WARN /$u not live yet"
          done
```

- [ ] **Step 2: Validate the YAML locally**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml')); print('yaml ok')"`
Expected: `yaml ok`.

- [ ] **Step 3: Rehearse the release steps locally (no tag, no deploy)**

Run each blocking step's local equivalent from the repo root:
`/Volumes/WD Green/dev/git/iladub/.venv/bin/python scripts/release_gate.py` → exit 0;
`/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m mkdocs build --strict` → success;
the w3id `for p in …` loop verbatim → prints nothing, exit 0.
Expected: all three green. (PyPI/gh-deploy are NOT rehearsed — first real run is Phase 3's `v0.0.3`.)

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/release.yml
git commit -m "ci: release train — version guard, tests, contradiction gate, w3id smoke, gh-pages deploy, PyPI OIDC (spec §7)"
```

---

### Task 6: `RELEASE.md` (new Manual) + contract truth restored

**Files:**
- Create: `RELEASE.md`
- Modify: `tests/docgov_extract.py` (`MANUAL_ALLOWLIST` gains `"RELEASE.md"`)
- Modify: `tests/test_docgov_extract.py` (`test_classify_precedence_most_specific_wins` gains one assert)
- Modify: `CLAUDE.md` (three wording updates — authorized by spec §8 item 7 and the user's Phase-2 request)

**Interfaces:**
- Consumes: everything prior (the checklist references the gate, the workflows, the promotion queue).
- Produces: the human release procedure Phase 3 executes for `v0.0.3`.

- [ ] **Step 1: Extend the allowlist + its test**

In `tests/docgov_extract.py`:

```python
MANUAL_ALLOWLIST = frozenset({
    "README.md", "vocab/README.md", "demo/README-etkl-showcase.md", "RELEASE.md",
})
```

In `tests/test_docgov_extract.py`, add to `test_classify_precedence_most_specific_wins`:

```python
    assert classify("RELEASE.md", NAV) == "manual"
```

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_docgov_extract.py -q` → all pass.

- [ ] **Step 2: Write `RELEASE.md`**

```markdown
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

   For each queued wiki page: author/refresh the state-page prose it feeds,
   set `promoted_to:` in the wiki page's frontmatter, update its `updated:`.
   Doctrine pages change only if a decision changed.

2. **Check the contradiction gate** (also enforced by the tag build):

       .venv/bin/python scripts/release_gate.py

   If it lists blockers, fix the affected published page(s) in this release.

3. **Bump the version** in `pyproject.toml` (`project.version`).

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
```

- [ ] **Step 3: Update `CLAUDE.md` (three precise edits)**

1. In § Serialization & stack conventions: replace the sentence ending `(CI lands with the release-train phase of the 2026-07-31 governance spec; until then, run locally before push).` with `Tests run under `pytest`; CI runs them on every push/PR (`.github/workflows/ci.yml`).`
2. In § Source ownership: replace `**pytest-enforced** by` with `**CI-enforced** by` (true again — `ci.yml` runs the suite).
3. In § Documentation governance: replace `**Manual** (the three READMEs —` with `**Manual** (the READMEs + `RELEASE.md` —`; and replace the sentence `iladub.dev *will* build from release tags once the release-train phase lands (spec 2026-07-31 §7); today the site is deployed by hand from `main`.` with `iladub.dev builds from release tags (`.github/workflows/release.yml`); the first tagged release supersedes the hand-deployed site.`; and replace `contradictions are registered now and will block the release tag once the release train lands (not the loop).` with `contradictions block the release tag (`scripts/release_gate.py`), not the loop.`

- [ ] **Step 4: Lint + full suite**

Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest tests/test_doc_governance.py -q` → green (RELEASE.md now classifies as manual; membrane passes).
Run: `/Volumes/WD Green/dev/git/iladub/.venv/bin/python -m pytest -q` → no regressions vs baseline 724+5 (this branch adds tests; expect ~730 passed).

- [ ] **Step 5: Commit**

```bash
git add RELEASE.md tests/docgov_extract.py tests/test_docgov_extract.py CLAUDE.md
git commit -m "docs: RELEASE.md manual + contract truth restored — CI claims real again, Manual class extended (spec §8 item 7)"
```

---

## Completion checklist (Phase 2 definition of done)

- [ ] `pytest -q` fully green locally (baseline 724 passed / 5 skipped, plus this branch's new tests).
- [ ] Branch pushed; **`ci.yml` observed green on the PR** (`gh run watch` / `gh pr checks`) — this is the phase's end-to-end proof for the CI half.
- [ ] Local rehearsal of every blocking `release.yml` step green (Task 5 Step 3). The tag half's first live run is deliberately Phase 3 (`v0.0.3`).
- [ ] Residue rows R21 + R22 deleted; R23–R25 untouched.
- [ ] **Human action flagged to François (cannot be automated):** register the PyPI Trusted Publisher (RELEASE.md § prerequisite) before Phase 3 tags.
- [ ] Merge with a **merge commit** (never squash — committer-date rewrite breaks the staleness lint's date comparisons).
