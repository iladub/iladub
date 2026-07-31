# Documentation Governance — Phase 1 (Foundation) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the doc-class lint (PROCEDURAL extractor → SHACL membrane → SPARQL derivations), resolve the orphan doc, and update the contract docs — Phase 1 of `docs/superpowers/specs/2026-07-31-documentation-governance-design.md`.

**Architecture:** A procedural extractor (`tests/docgov_extract.py`) walks tracked markdown, parses `mkdocs.yml` and wiki frontmatter, reads git dates, and emits typed RDF facts. A SHACL shapes file (`vocab/shapes/doc-governance-shapes.ttl`) is the closed-world membrane (every doc has exactly one class, nav resolves, nothing confidential is tracked…). SPARQL `CONSTRUCT` queries (`vocab/queries/docgov-*.rq`) derive the staleness sets and promotion queue, open-world. `tests/test_doc_governance.py` runs the whole thing against the live repo under `pytest`.

**Tech Stack:** Python 3, rdflib ≥ 7.0, pySHACL ≥ 0.26, PyYAML ≥ 6.0 (all already in `pyproject.toml` dependencies — add nothing). Existing pySHACL idiom: `validate(data, shacl_graph=…, inference="rdfs", advanced=True)` (see `tests/test_m4_databook.py:54`).

**Doc impact:** increment — establishes `docs/wiki/` and the governance rules; `CLAUDE.md` + loop canvas template updated in-band; no published page contradicted.

**Phases 2 (release train / CI) and 3 (wiki seeding + v0.0.3) get their own plans once this ships.**

## Global Constraints

- **Neurosymbolic gate (CLAUDE.md §8):** the extractor is PROCEDURAL (file I/O, YAML, git subprocess — state the justification in its docstring); ALL membership/membrane rules live in SHACL; ALL derivations in SPARQL. Any Python `if` that encodes a governance *rule* (rather than extracting a fact) is a defect.
- **No overfitting:** the final lint must run green on the *live* repo census (148 tracked `.md` files + the moved orphan) without special-casing any file beyond the spec's explicit allowlist/exemptions.
- **Honest failure:** a file the extractor cannot classify gets NO `dg:docClass` triple — SHACL fails it loudly. Never guess a class.
- **Open/closed split:** SHACL never derives; SPARQL never validates. Holon-scoped `FILTER NOT EXISTS` inside a query is permitted (query-local closure).
- **Serialization:** shapes/queries in Turtle/.rq under `vocab/`; multilingual literals unconstrained (no `xsd:string` on label-like properties).
- **Namespace:** `dg:` = `https://w3id.org/iladub/docgov#` — repo-internal governance vocabulary; NOT part of the published ontology, NOT added to w3id. Say so in the shapes file header.
- **Doc-impact cutoff:** `2026-07-31`. Specs/plans dated before it are grandfathered.
- **Commits:** conventional-commit style matching repo history (`feat(docgov): …`, `docs: …`, `test(docgov): …`).

---

### Task 1: Classification + config parsing (pure functions)

**Files:**
- Create: `tests/docgov_extract.py`
- Test: `tests/test_docgov_extract.py`

**Interfaces:**
- Consumes: nothing (first task).
- Produces (used by Tasks 3–6):
  - `DG = Namespace("https://w3id.org/iladub/docgov#")`
  - `DOC_IMPACT_CUTOFF: datetime.date = date(2026, 7, 31)`
  - `MANUAL_ALLOWLIST: frozenset[str]`, `EVIDENCE_DIRS: tuple[str, ...]`
  - `is_exempt(path: str) -> bool`
  - `classify(path: str, nav_paths: set[str]) -> str | None`
  - `load_mkdocs(mkdocs_yml: Path) -> dict`
  - `nav_paths(cfg: dict) -> set[str]` — repo-relative, `docs/`-prefixed
  - `exclude_prefixes(cfg: dict) -> tuple[str, ...]` — repo-relative, `docs/`-prefixed
  - `is_excluded(path: str, prefixes: tuple[str, ...]) -> bool`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_docgov_extract.py
"""Unit tests for the docgov PROCEDURAL extractor (pure functions, no git)."""
from pathlib import Path

from tests.docgov_extract import (
    classify, is_exempt, load_mkdocs, nav_paths, exclude_prefixes, is_excluded,
)

NAV = {"docs/index.md", "docs/manifesto.md", "docs/narrative/scope-evolution.md"}


def test_exemptions():
    assert is_exempt(".claude/skills/baml-core/SKILL.md")
    assert is_exempt(".agents/skills/baml-core/SKILL.md")
    assert is_exempt("examples/transplant/offer.databook.md")
    assert not is_exempt("docs/manifesto.md")


def test_classify_precedence_most_specific_wins():
    assert classify("CLAUDE.md", NAV) == "contract"
    assert classify("README.md", NAV) == "manual"
    assert classify("vocab/README.md", NAV) == "manual"
    assert classify("demo/README-etkl-showcase.md", NAV) == "manual"
    assert classify("internal/decisions/x.md", NAV) == "confidential"
    assert classify("docs/wiki/concepts/foo.md", NAV) == "wiki"
    # docs/loops/README.md: Evidence dir beats any README intuition (spec §3 precedence)
    assert classify("docs/loops/README.md", NAV) == "evidence"
    assert classify("docs/superpowers/specs/2026-07-30-row-groups-design.md", NAV) == "evidence"
    assert classify("docs/w3id/iladub-htaccess.md", NAV) == "evidence"
    assert classify("docs/manifesto.md", NAV) == "assertion"
    assert classify("docs/narrative/scope-evolution.md", NAV) == "assertion"


def test_classify_unknown_is_none_not_a_guess():
    assert classify("docs/neurosymbolic-exemplars.md", NAV) is None
    assert classify("somewhere/else.md", NAV) is None


def test_load_mkdocs_tolerates_python_name_tags(tmp_path):
    # mkdocs.yml contains `!!python/name:pymdownx...` — yaml.safe_load would raise.
    y = tmp_path / "mkdocs.yml"
    y.write_text(
        "site_name: x\n"
        "exclude_docs: |\n  superpowers/\n  wiki/\n"
        "nav:\n  - Home: index.md\n  - Sub:\n      - A: narrative/scope-evolution.md\n"
        "markdown_extensions:\n  - pymdownx.superfences:\n      custom_fences:\n"
        "        - name: mermaid\n          class: mermaid\n"
        "          format: !!python/name:pymdownx.superfences.fence_code_format\n"
    )
    cfg = load_mkdocs(y)
    assert nav_paths(cfg) == {"docs/index.md", "docs/narrative/scope-evolution.md"}
    prefixes = exclude_prefixes(cfg)
    assert prefixes == ("docs/superpowers/", "docs/wiki/")
    assert is_excluded("docs/wiki/concepts/foo.md", prefixes)
    assert not is_excluded("docs/index.md", prefixes)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_docgov_extract.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tests.docgov_extract'`

- [ ] **Step 3: Write the implementation**

```python
# tests/docgov_extract.py
"""docgov extractor — PROCEDURAL (CLAUDE.md §8 gate).

Justification: raw extraction only — walking tracked markdown, parsing YAML
(mkdocs config, wiki frontmatter), reading git commit dates, emitting typed RDF
facts. Irreducible to AXIOM/NEURAL: no ontology can perform file I/O or run git.
ALL membership/membrane decisions live in vocab/shapes/doc-governance-shapes.ttl
(SHACL, closed world); ALL derivations in vocab/queries/docgov-*.rq (SPARQL,
open world). Path-glob classification below is fact extraction per spec §6.
"""
from __future__ import annotations

import re
import subprocess
from datetime import date
from pathlib import Path

import yaml
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

DG = Namespace("https://w3id.org/iladub/docgov#")
_DOC = "https://w3id.org/iladub/docgov/doc/"

DOC_IMPACT_CUTOFF = date(2026, 7, 31)  # spec §5.1 — earlier specs/plans grandfathered

MANUAL_ALLOWLIST = frozenset({
    "README.md", "vocab/README.md", "demo/README-etkl-showcase.md",
})
EVIDENCE_DIRS = ("docs/superpowers/", "docs/loops/", "docs/w3id/")
EXEMPT_PREFIXES = (".claude/", ".agents/")


def is_exempt(path: str) -> bool:
    """Data or tooling, not prose (spec §3): skill files, DataBook artifacts."""
    return path.startswith(EXEMPT_PREFIXES) or path.endswith(".databook.md")


def classify(path: str, nav: set[str]) -> str | None:
    """Class by location, most specific rule first (spec §3). None = classless
    — emitted without dg:docClass so the SHACL membrane fails it loudly."""
    if path == "CLAUDE.md":
        return "contract"
    if path in MANUAL_ALLOWLIST:
        return "manual"
    if path.startswith("internal/"):
        return "confidential"
    if path.startswith("docs/wiki/"):
        return "wiki"
    if path.startswith(EVIDENCE_DIRS):
        return "evidence"
    if path in nav:
        return "assertion"
    return None


class _AnyTagLoader(yaml.SafeLoader):
    """SafeLoader that tolerates unknown tags (mkdocs.yml uses !!python/name:…)."""


_AnyTagLoader.add_multi_constructor("", lambda loader, suffix, node: None)


def load_mkdocs(mkdocs_yml: Path) -> dict:
    return yaml.load(mkdocs_yml.read_text(), Loader=_AnyTagLoader)


def nav_paths(cfg: dict) -> set[str]:
    out: set[str] = set()

    def walk(item):
        if isinstance(item, str):
            out.add("docs/" + item)
        elif isinstance(item, dict):
            for v in item.values():
                walk(v)
        elif isinstance(item, list):
            for v in item:
                walk(v)

    walk(cfg.get("nav", []))
    return out


def exclude_prefixes(cfg: dict) -> tuple[str, ...]:
    raw = cfg.get("exclude_docs") or ""
    return tuple("docs/" + line.strip() for line in raw.splitlines() if line.strip())


def is_excluded(path: str, prefixes: tuple[str, ...]) -> bool:
    return path.startswith(prefixes) if prefixes else False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_docgov_extract.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add tests/docgov_extract.py tests/test_docgov_extract.py
git commit -m "feat(docgov): class-by-location extractor primitives (PROCEDURAL, spec §3/§6)"
```

---

### Task 2: Frontmatter, git dates, and the full `extract()` graph

**Files:**
- Modify: `tests/docgov_extract.py` (append)
- Test: `tests/test_docgov_extract.py` (append)

**Interfaces:**
- Consumes: everything from Task 1.
- Produces (used by Tasks 4–6):
  - `parse_frontmatter(text: str) -> dict | None`
  - `tracked_markdown(repo: Path) -> list[str]`
  - `last_commit_date(repo: Path, path: str) -> str | None` — `YYYY-MM-DD` or None (uncommitted)
  - `doc_iri(path: str) -> URIRef` — `https://w3id.org/iladub/docgov/doc/<path>`
  - `extract(repo: Path) -> rdflib.Graph` emitting, per non-exempt tracked `.md`:
    `dg:Document` with `dg:path` (string), `dg:docClass` (string, ABSENT when classless),
    `dg:inNav` / `dg:excludedFromSite` (booleans); per nav entry: `dg:NavEntry` with
    `dg:navPath`, `dg:resolves` (boolean); per dated spec/plan ≥ cutoff:
    `dg:requiresDocImpact true`, `dg:hasDocImpact` (boolean); per wiki page:
    `dg:title`, `dg:docType`, `dg:confidence` (strings), `dg:updated` (xsd:date),
    `dg:cites` → `dg:Source` node (`dg:path`, `dg:exists` boolean, `dg:isEvidence`
    boolean, `dg:lastCommitDate` xsd:date), `dg:citesExternal` (literal, `vault:…`),
    `dg:promotedTo` → doc IRI.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_docgov_extract.py`)

```python
from datetime import date

from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD

from tests.docgov_extract import (
    DG, parse_frontmatter, doc_iri, extract, tracked_markdown,
)

REPO = Path(__file__).resolve().parent.parent


def test_parse_frontmatter():
    fm = parse_frontmatter(
        "---\ntitle: X\ntype: concept\nconfidence: high\nupdated: 2026-07-30\n"
        "sources:\n  - docs/superpowers/specs/a.md\n  - vault:wiki/concepts/h.md\n---\nbody\n"
    )
    assert fm["title"] == "X"
    assert fm["updated"] == date(2026, 7, 30)
    assert fm["sources"][1] == "vault:wiki/concepts/h.md"
    assert parse_frontmatter("no frontmatter\n") is None


def test_extract_live_repo_smoke():
    """extract() runs on the real repo: every non-exempt tracked md becomes a
    dg:Document with a path; nav entries all resolve. (Full conformance is
    tests/test_doc_governance.py — this is the plumbing smoke test.)"""
    g = extract(REPO)
    docs = set(g.subjects(RDF.type, DG.Document))
    tracked = [p for p in tracked_markdown(REPO)]
    assert doc_iri("CLAUDE.md") in docs
    assert doc_iri("docs/manifesto.md") in docs
    assert doc_iri(".claude/skills/baml-core/SKILL.md") not in docs  # exempt
    assert len(docs) <= len(tracked)
    assert (doc_iri("CLAUDE.md"), DG.docClass, Literal("contract")) in g
    for entry in g.subjects(RDF.type, DG.NavEntry):
        assert (entry, DG.resolves, Literal(True)) in g
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_docgov_extract.py -v -k "frontmatter or live_repo"`
Expected: FAIL with `ImportError: cannot import name 'parse_frontmatter'`

- [ ] **Step 3: Write the implementation** (append to `tests/docgov_extract.py`)

```python
_DATED = re.compile(r"^docs/superpowers/(?:specs|plans)/(\d{4})-(\d{2})-(\d{2})-")


def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    loaded = yaml.safe_load(text[4:end])
    return loaded if isinstance(loaded, dict) else None


def tracked_markdown(repo: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "*.md"], cwd=repo,
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def last_commit_date(repo: Path, path: str) -> str | None:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", path], cwd=repo,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return out[:10] or None


def doc_iri(path: str) -> URIRef:
    return URIRef(_DOC + path)


def extract(repo: Path) -> Graph:
    g = Graph()
    g.bind("dg", DG)
    cfg = load_mkdocs(repo / "mkdocs.yml")
    nav = nav_paths(cfg)
    prefixes = exclude_prefixes(cfg)

    for np in sorted(nav):
        entry = URIRef(_DOC + "nav/" + np)
        g.add((entry, RDF.type, DG.NavEntry))
        g.add((entry, DG.navPath, Literal(np)))
        g.add((entry, DG.resolves, Literal((repo / np).is_file())))

    for path in tracked_markdown(repo):
        if is_exempt(path):
            continue
        d = doc_iri(path)
        g.add((d, RDF.type, DG.Document))
        g.add((d, DG.path, Literal(path)))
        cls = classify(path, nav)
        if cls is not None:  # honest failure: classless docs carry no class triple
            g.add((d, DG.docClass, Literal(cls)))
        g.add((d, DG.inNav, Literal(path in nav)))
        g.add((d, DG.excludedFromSite, Literal(is_excluded(path, prefixes))))
        if cls == "evidence":
            _evidence_facts(g, repo, d, path)
        elif cls == "wiki":
            _wiki_facts(g, repo, d, path)
    return g


def _evidence_facts(g: Graph, repo: Path, d: URIRef, path: str) -> None:
    m = _DATED.match(path)
    if not m:
        return
    if date(int(m[1]), int(m[2]), int(m[3])) >= DOC_IMPACT_CUTOFF:
        g.add((d, DG.requiresDocImpact, Literal(True)))
        text = (repo / path).read_text()
        g.add((d, DG.hasDocImpact, Literal("Doc impact:" in text)))


def _wiki_facts(g: Graph, repo: Path, d: URIRef, path: str) -> None:
    fm = parse_frontmatter((repo / path).read_text())
    if not fm:
        return  # missing frontmatter → WikiShape minCounts fail it loudly
    for key, prop in (("title", DG.title), ("type", DG.docType),
                      ("confidence", DG.confidence)):
        if key in fm:
            g.add((d, prop, Literal(fm[key])))
    if "updated" in fm:
        g.add((d, DG.updated, Literal(fm["updated"], datatype=XSD.date)))
    for src in fm.get("sources") or []:
        if src.startswith("vault:"):
            g.add((d, DG.citesExternal, Literal(src)))
            continue
        s = doc_iri(src)
        g.add((d, DG.cites, s))
        g.add((s, RDF.type, DG.Source))
        g.add((s, DG.path, Literal(src)))
        g.add((s, DG.exists, Literal((repo / src).is_file())))
        g.add((s, DG.isEvidence,
               Literal(src.startswith(EVIDENCE_DIRS) and src.endswith(".md"))))
        lcd = last_commit_date(repo, src)
        if lcd:
            g.add((s, DG.lastCommitDate, Literal(lcd, datatype=XSD.date)))
    if fm.get("promoted_to"):
        g.add((d, DG.promotedTo, doc_iri(fm["promoted_to"])))
```

- [ ] **Step 4: Run the full extractor test file**

Run: `pytest tests/test_docgov_extract.py -v`
Expected: 6 PASS. (`test_extract_live_repo_smoke` passing does NOT mean the repo conforms — classless docs simply carry no class triple here; conformance is Task 6.)

- [ ] **Step 5: Commit**

```bash
git add tests/docgov_extract.py tests/test_docgov_extract.py
git commit -m "feat(docgov): full fact extraction — frontmatter, git dates, nav, doc-impact (spec §6)"
```

---

### Task 3: The SHACL membrane

**Files:**
- Create: `vocab/shapes/doc-governance-shapes.ttl`
- Test: `tests/test_docgov_shapes.py`

**Interfaces:**
- Consumes: the fact vocabulary emitted by `extract()` (Task 2 Produces block).
- Produces: `vocab/shapes/doc-governance-shapes.ttl` — validated with the repo idiom
  `pyshacl.validate(data, shacl_graph=shapes, inference="rdfs", advanced=True)`.
  Task 6 loads this file by path.

- [ ] **Step 1: Write the failing tests**

Repo convention: every shape ships with a conforming example AND a negative that must fail. Both are built inline as small graphs.

```python
# tests/test_docgov_shapes.py
"""Membrane tests (spec §6, closed world): conforming minimal graph + one
negative per shape. AXIOM/SHACL — validation only, never derivation."""
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

from tests.docgov_extract import DG, doc_iri

REPO = Path(__file__).resolve().parent.parent
SHAPES = Graph().parse(REPO / "vocab" / "shapes" / "doc-governance-shapes.ttl")


def _doc(g, path, cls, in_nav=False, excluded=True):
    d = doc_iri(path)
    g.add((d, RDF.type, DG.Document))
    g.add((d, DG.path, Literal(path)))
    if cls:
        g.add((d, DG.docClass, Literal(cls)))
    g.add((d, DG.inNav, Literal(in_nav)))
    g.add((d, DG.excludedFromSite, Literal(excluded)))
    return d


def _wiki(g, path="docs/wiki/concepts/ok.md"):
    d = _doc(g, path, "wiki")
    g.add((d, DG.title, Literal("Ok")))
    g.add((d, DG.docType, Literal("concept")))
    g.add((d, DG.confidence, Literal("high")))
    g.add((d, DG.updated, Literal("2026-07-30", datatype=XSD.date)))
    s = doc_iri("docs/superpowers/specs/2026-07-01-x-design.md")
    g.add((d, DG.cites, s))
    g.add((s, RDF.type, DG.Source))
    g.add((s, DG.path, Literal("docs/superpowers/specs/2026-07-01-x-design.md")))
    g.add((s, DG.exists, Literal(True)))
    g.add((s, DG.isEvidence, Literal(True)))
    return d


def _conforms(g):
    ok, _, report = validate(g, shacl_graph=SHAPES, inference="rdfs", advanced=True)
    return ok, report


def test_conforming_minimal_graph():
    g = Graph()
    _doc(g, "CLAUDE.md", "contract")
    a = _doc(g, "docs/manifesto.md", "assertion", in_nav=True, excluded=False)
    _doc(g, "docs/superpowers/specs/2026-07-01-old-design.md", "evidence")
    w = _wiki(g)
    g.add((w, DG.promotedTo, a))
    n = doc_iri("nav/docs/manifesto.md")  # same IRI scheme as extract()
    g.add((n, RDF.type, DG.NavEntry))
    g.add((n, DG.navPath, Literal("docs/manifesto.md")))
    g.add((n, DG.resolves, Literal(True)))
    ok, report = _conforms(g)
    assert ok, report


def test_classless_document_fails():
    g = Graph()
    _doc(g, "docs/orphan.md", None)
    ok, report = _conforms(g)
    assert not ok and "exactly one class" in str(report)


def test_tracked_confidential_fails():
    g = Graph()
    _doc(g, "internal/decisions/x.md", "confidential")
    ok, report = _conforms(g)
    assert not ok and "internal/" in str(report)


def test_assertion_not_in_nav_fails():
    g = Graph()
    _doc(g, "docs/stray.md", "assertion", in_nav=False, excluded=False)
    assert not _conforms(g)[0]


def test_unexcluded_wiki_or_evidence_fails():
    g = Graph()
    d = _wiki(g)
    g.set((d, DG.excludedFromSite, Literal(False)))
    assert not _conforms(g)[0]


def test_unresolved_nav_entry_fails():
    g = Graph()
    n = doc_iri("nav/docs/gone.md")
    g.add((n, RDF.type, DG.NavEntry))
    g.add((n, DG.navPath, Literal("docs/gone.md")))
    g.add((n, DG.resolves, Literal(False)))
    assert not _conforms(g)[0]


def test_wiki_missing_frontmatter_fields_fails():
    g = Graph()
    d = _doc(g, "docs/wiki/concepts/bare.md", "wiki")  # no title/updated/… facts
    assert not _conforms(g)[0]


def test_wiki_citing_missing_source_fails():
    g = Graph()
    d = _wiki(g)
    s = doc_iri("docs/superpowers/specs/2026-07-01-x-design.md")
    g.set((s, DG.exists, Literal(False)))
    assert not _conforms(g)[0]


def test_promoted_to_non_assertion_fails():
    g = Graph()
    w = _wiki(g)
    e = doc_iri("docs/superpowers/specs/2026-07-01-old-design.md")
    _doc(g, "docs/superpowers/specs/2026-07-01-old-design.md", "evidence")
    g.add((w, DG.promotedTo, e))
    assert not _conforms(g)[0]


def test_missing_doc_impact_after_cutoff_fails():
    g = Graph()
    d = _doc(g, "docs/superpowers/specs/2026-08-01-new-design.md", "evidence")
    g.add((d, DG.requiresDocImpact, Literal(True)))
    g.add((d, DG.hasDocImpact, Literal(False)))
    assert not _conforms(g)[0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_docgov_shapes.py -v`
Expected: ERROR at collection — `FileNotFoundError` for `doc-governance-shapes.ttl`

- [ ] **Step 3: Write the shapes file**

```turtle
# vocab/shapes/doc-governance-shapes.ttl
#
# Documentation-governance membrane (spec: docs/superpowers/specs/
# 2026-07-31-documentation-governance-design.md §6). CLOSED WORLD: this file
# only VALIDATES what the PROCEDURAL extractor asserted — it never derives
# (derivations live in vocab/queries/docgov-*.rq, open world).
#
# The dg: namespace is repo-internal governance vocabulary. It is NOT part of
# the published iladub/etkl/dec/risk ontologies and is NOT registered at w3id.
#
# © 2026 François Rosselet · CC-BY-4.0
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix dg:  <https://w3id.org/iladub/docgov#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

dg:DocumentShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:property [
        sh:path dg:docClass ;
        sh:minCount 1 ; sh:maxCount 1 ;
        sh:in ( "evidence" "wiki" "assertion" "manual" "contract" "confidential" ) ;
        sh:message "every tracked markdown file must belong to exactly one class (spec §3)" ;
    ] ;
    sh:property [ sh:path dg:path ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path dg:inNav ; sh:minCount 1 ; sh:datatype xsd:boolean ] ;
    sh:property [ sh:path dg:excludedFromSite ; sh:minCount 1 ; sh:datatype xsd:boolean ] .

# No confidential material may be tracked at all (spec §3 class 6).
dg:NoTrackedConfidentialShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:sparql [
        sh:message "confidential material under internal/ must never be tracked (spec §3)" ;
        sh:select """
            SELECT $this WHERE {
                $this <https://w3id.org/iladub/docgov#path> ?p .
                FILTER STRSTARTS(?p, "internal/")
            }""" ;
    ] .

# Assertions are exactly the nav (spec §3 class 3).
dg:AssertionInNavShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:sparql [
        sh:message "an Assertion must be in the mkdocs nav (spec §3)" ;
        sh:select """
            SELECT $this WHERE {
                $this <https://w3id.org/iladub/docgov#docClass> "assertion" ;
                      <https://w3id.org/iladub/docgov#inNav> false .
            }""" ;
    ] .

# Wiki and Evidence must be covered by exclude_docs (spec §2.2, §6).
dg:UnpublishableShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:sparql [
        sh:message "wiki/evidence docs must be excluded from the published site (spec §6)" ;
        sh:select """
            SELECT $this WHERE {
                $this <https://w3id.org/iladub/docgov#docClass> ?c ;
                      <https://w3id.org/iladub/docgov#excludedFromSite> false .
                FILTER (?c IN ("wiki", "evidence"))
            }""" ;
    ] .

# Every nav entry resolves to a real file.
dg:NavEntryShape a sh:NodeShape ;
    sh:targetClass dg:NavEntry ;
    sh:property [
        sh:path dg:resolves ; sh:hasValue true ;
        sh:message "mkdocs nav entry does not resolve to a file" ;
    ] .

# Wiki frontmatter completeness (spec §4). Target: wiki-classed documents.
dg:WikiShape a sh:NodeShape ;
    sh:target [
        a sh:SPARQLTarget ;
        sh:select """
            SELECT ?this WHERE {
                ?this <https://w3id.org/iladub/docgov#docClass> "wiki" .
            }""" ;
    ] ;
    sh:property [ sh:path dg:title ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:message "wiki page: title missing" ] ;
    sh:property [ sh:path dg:docType ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:in ( "concept" "source" "index" ) ;
        sh:message "wiki page: type must be concept | source | index" ] ;
    sh:property [ sh:path dg:confidence ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:in ( "high" "medium" "low" ) ;
        sh:message "wiki page: confidence must be high | medium | low" ] ;
    sh:property [ sh:path dg:updated ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:datatype xsd:date ; sh:message "wiki page: updated date missing" ] ;
    sh:property [
        sh:path [ sh:alternativePath ( dg:cites dg:citesExternal ) ] ;
        sh:minCount 1 ;
        sh:message "wiki page: every page cites at least one source (spec §4)" ;
    ] .

# Every internally-cited source must exist on disk.
dg:SourceExistsShape a sh:NodeShape ;
    sh:targetClass dg:Source ;
    sh:property [
        sh:path dg:exists ; sh:hasValue true ;
        sh:message "wiki page cites a source path that does not exist" ;
    ] .

# promoted_to must land on an Assertion (spec §4). Holon-scoped NOT EXISTS.
dg:PromotedToAssertionShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:sparql [
        sh:message "promoted_to must reference an Assertion (spec §4)" ;
        sh:select """
            SELECT $this WHERE {
                $this <https://w3id.org/iladub/docgov#promotedTo> ?t .
                FILTER NOT EXISTS {
                    ?t <https://w3id.org/iladub/docgov#docClass> "assertion" .
                }
            }""" ;
    ] .

# Doc-impact registration is required for specs/plans dated >= 2026-07-31
# (spec §5.1; requiresDocImpact is a mechanical fact from the filename date).
dg:DocImpactShape a sh:NodeShape ;
    sh:targetClass dg:Document ;
    sh:sparql [
        sh:message "spec/plan dated >= 2026-07-31 must contain a 'Doc impact:' block (spec §5.1)" ;
        sh:select """
            SELECT $this WHERE {
                $this <https://w3id.org/iladub/docgov#requiresDocImpact> true .
                FILTER NOT EXISTS {
                    $this <https://w3id.org/iladub/docgov#hasDocImpact> true .
                }
            }""" ;
    ] .
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_docgov_shapes.py -v`
Expected: 10 PASS. If `test_conforming_minimal_graph` fails on the SPARQLTarget, check pySHACL emitted the violation with `advanced=True` present — the target requires it.

- [ ] **Step 5: Commit**

```bash
git add vocab/shapes/doc-governance-shapes.ttl tests/test_docgov_shapes.py
git commit -m "feat(docgov): SHACL membrane — class totality, leak boundary, nav, wiki frontmatter, doc-impact (spec §6)"
```

---

### Task 4: SPARQL derivations — staleness sets + promotion queue

**Files:**
- Create: `vocab/queries/docgov-staleness-evidence.rq`
- Create: `vocab/queries/docgov-staleness-code.rq`
- Create: `vocab/queries/docgov-promotion-queue.rq`
- Test: `tests/test_docgov_queries.py`

**Interfaces:**
- Consumes: fact graph vocabulary (Task 2), `DG`, `doc_iri`.
- Produces: three `.rq` files, each a `CONSTRUCT` run via
  `rdflib.Graph.query(Path(...).read_text())` → result graph. Constructed
  predicates: `dg:staleAgainstEvidence` (hard fail), `dg:staleAgainstCode`
  (warning), `dg:inPromotionQueue` (report). Task 6 runs them by path.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_docgov_queries.py
"""Derivation tests (spec §6, open world): SPARQL CONSTRUCT over facts
PRESENT. Only the promotion queue uses a holon-scoped NOT EXISTS."""
from pathlib import Path

from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD

from tests.docgov_extract import DG, doc_iri

REPO = Path(__file__).resolve().parent.parent
Q = REPO / "vocab" / "queries"


def _wiki_citing(updated, src_path, src_date, is_evidence):
    g = Graph()
    d = doc_iri("docs/wiki/concepts/p.md")
    g.add((d, RDF.type, DG.Document))
    g.add((d, DG.docClass, Literal("wiki")))
    g.add((d, DG.docType, Literal("concept")))
    g.add((d, DG.updated, Literal(updated, datatype=XSD.date)))
    s = doc_iri(src_path)
    g.add((d, DG.cites, s))
    g.add((s, RDF.type, DG.Source))
    g.add((s, DG.path, Literal(src_path)))
    g.add((s, DG.isEvidence, Literal(is_evidence)))
    g.add((s, DG.lastCommitDate, Literal(src_date, datatype=XSD.date)))
    return g, d, s


def _construct(g, name):
    out = Graph()
    for t in g.query((Q / name).read_text()):
        out.add(t)
    return out


def test_stale_against_evidence_derived():
    g, d, s = _wiki_citing("2026-07-15", "docs/superpowers/specs/2026-07-30-x.md",
                           "2026-07-30", True)
    rows = _construct(g, "docgov-staleness-evidence.rq")
    assert (d, DG.staleAgainstEvidence, s) in rows


def test_fresh_page_not_stale():
    g, d, s = _wiki_citing("2026-07-30", "docs/superpowers/specs/2026-07-30-x.md",
                           "2026-07-30", True)
    assert len(_construct(g, "docgov-staleness-evidence.rq")) == 0


def test_code_staleness_separate_and_not_evidence():
    g, d, s = _wiki_citing("2026-07-15", "vocab/shapes/promotion-shapes.ttl",
                           "2026-07-30", False)
    assert len(_construct(g, "docgov-staleness-evidence.rq")) == 0
    assert (d, DG.staleAgainstCode, s) in _construct(g, "docgov-staleness-code.rq")


def test_promotion_queue_is_unpromoted_wiki_pages():
    g, d, s = _wiki_citing("2026-07-30", "docs/superpowers/specs/2026-07-30-x.md",
                           "2026-07-30", True)
    assert (d, DG.inPromotionQueue, Literal(True)) in _construct(
        g, "docgov-promotion-queue.rq")
    g.add((d, DG.promotedTo, doc_iri("docs/manifesto.md")))
    assert len(_construct(g, "docgov-promotion-queue.rq")) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_docgov_queries.py -v`
Expected: 4 FAIL/ERROR with `FileNotFoundError` on the first `.rq`

- [ ] **Step 3: Write the three queries**

```sparql
# vocab/queries/docgov-staleness-evidence.rq
# Derivation, OPEN WORLD (spec §6): a wiki page is stale against evidence when
# a cited evidence doc's last commit POSTDATES the page's `updated`. Derived
# only from facts present. HARD FAIL in tests/test_doc_governance.py.
PREFIX dg: <https://w3id.org/iladub/docgov#>
CONSTRUCT { ?page dg:staleAgainstEvidence ?src }
WHERE {
    ?page dg:docClass "wiki" ;
          dg:updated  ?updated ;
          dg:cites    ?src .
    ?src  dg:isEvidence     true ;
          dg:lastCommitDate ?lastCommit .
    FILTER (?lastCommit > ?updated)
}
```

```sparql
# vocab/queries/docgov-staleness-code.rq
# Derivation, OPEN WORLD (spec §6): staleness against a cited CODE source
# (.py/.ttl/…). WARNING ONLY — code churns every commit; a hard gate here
# would make every loop a doc loop.
PREFIX dg: <https://w3id.org/iladub/docgov#>
CONSTRUCT { ?page dg:staleAgainstCode ?src }
WHERE {
    ?page dg:docClass "wiki" ;
          dg:updated  ?updated ;
          dg:cites    ?src .
    ?src  dg:isEvidence     false ;
          dg:lastCommitDate ?lastCommit .
    FILTER (?lastCommit > ?updated)
}
```

```sparql
# vocab/queries/docgov-promotion-queue.rq
# Derivation (spec §5/§6): the promotion queue = wiki pages not yet lifted to a
# published Assertion. The NOT EXISTS is holon-scoped (query-local closure per
# CLAUDE.md §8) — it closes only this page's promotion state.
PREFIX dg: <https://w3id.org/iladub/docgov#>
CONSTRUCT { ?page dg:inPromotionQueue true }
WHERE {
    ?page dg:docClass "wiki" ; dg:docType "concept" .
    FILTER NOT EXISTS { ?page dg:promotedTo ?target }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_docgov_queries.py -v`
Expected: 4 PASS. (`docgov-promotion-queue.rq` deliberately restricts to `docType "concept"` — `index`/`source` pages are never promotion candidates; the fixture asserts `docType "concept"` for exactly this reason.)

- [ ] **Step 5: Commit**

```bash
git add vocab/queries/docgov-*.rq tests/test_docgov_queries.py
git commit -m "feat(docgov): open-world derivations — staleness sets + promotion queue (spec §6)"
```

---

### Task 5: Repo fixes — exclude wiki/, resolve the orphan, register doc impact

**Files:**
- Modify: `mkdocs.yml` (the `exclude_docs` block)
- Create: `docs/wiki/index.md`
- Create: `docs/wiki/concepts/neurosymbolic-exemplars.md` (moved from `docs/neurosymbolic-exemplars.md`, currently **untracked**)
- Modify: `CLAUDE.md` (one path reference, ~line 140 — note: `CLAUDE.md` already has uncommitted user edits; they are committed together here, flag it in the commit body)
- Modify: `docs/superpowers/specs/2026-07-31-documentation-governance-design.md` (add a `Doc impact:` line — the spec itself is dated on the cutoff and must satisfy its own rule)

**Interfaces:**
- Consumes: the class rules of Task 1 (the orphan becomes class `wiki`; `wiki/` joins `exclude_docs`).
- Produces: a repo tree on which Task 6's live lint can go green.

- [ ] **Step 1: Exclude `wiki/` from the published site**

In `mkdocs.yml`, change:

```yaml
exclude_docs: |
  superpowers/
  w3id/
  loops/
```

to:

```yaml
exclude_docs: |
  superpowers/
  w3id/
  loops/
  wiki/
```

- [ ] **Step 2: Move the orphan into the wiki and add frontmatter**

```bash
mkdir -p docs/wiki/concepts
git mv docs/neurosymbolic-exemplars.md docs/wiki/concepts/neurosymbolic-exemplars.md 2>/dev/null \
  || mv docs/neurosymbolic-exemplars.md docs/wiki/concepts/neurosymbolic-exemplars.md   # untracked → plain mv
```

Then prepend this frontmatter to `docs/wiki/concepts/neurosymbolic-exemplars.md` (the two `sources:` are real paths the catalog cites — its gate-enforcing test and its flagship AXIOM query; verify both exist with `git ls-files tests/etkl/test_transform_gate.py vocab/queries/classify-kind.rq` and, if the catalog has since grown, add any further code paths it names):

```yaml
---
title: Neurosymbolic exemplars — the loop-by-loop catalog
type: concept
sources:
  - tests/etkl/test_transform_gate.py
  - vocab/queries/classify-kind.rq
related: []
confidence: high
updated: 2026-07-31
---
```

- [ ] **Step 3: Create `docs/wiki/index.md`**

```markdown
---
title: iladub wiki — index
type: index
sources:
  - docs/superpowers/specs/2026-07-31-documentation-governance-design.md
related: []
confidence: high
updated: 2026-07-31
---

# iladub wiki — read this first

LLM-maintained synthesis layer (committed, never published — see the
documentation-governance spec). Specs are **evidence**, these pages are
**propositions**, the site is **assertion**. One line per page:

| Page | Confidence | Updated |
|---|---|---|
| [neurosymbolic-exemplars](concepts/neurosymbolic-exemplars.md) — loop-by-loop catalog of gate-compliant AXIOM/NEURAL/PROCEDURAL code | high | 2026-07-31 |
```

- [ ] **Step 4: Update the `CLAUDE.md` reference**

In `CLAUDE.md` ~line 140, change `docs/neurosymbolic-exemplars.md` → `docs/wiki/concepts/neurosymbolic-exemplars.md`.

- [ ] **Step 5: Register the spec's own doc impact**

In `docs/superpowers/specs/2026-07-31-documentation-governance-design.md`, under the `**Scope:**` line in the header block, add:

```markdown
**Doc impact:** increment — establishes `docs/wiki/` (this spec seeds it); `CLAUDE.md`
governance section updated in-band; no published page contradicted.
```

(This plan file already carries its own `Doc impact:` line in its header.)

- [ ] **Step 6: Verify the site build still excludes everything internal**

Run: `mkdocs build --strict 2>&1 | tail -5 && ls site/ | head && test ! -d site/wiki && test ! -d site/superpowers && echo EXCLUDED-OK`
Expected: build succeeds, `EXCLUDED-OK`

- [ ] **Step 7: Commit**

```bash
git add mkdocs.yml docs/wiki/ CLAUDE.md docs/superpowers/specs/2026-07-31-documentation-governance-design.md
git rm --cached docs/neurosymbolic-exemplars.md 2>/dev/null; true
git commit -m "feat(docgov): seed docs/wiki/ — orphan resolved, wiki excluded from site, spec doc-impact registered

CLAUDE.md commit includes the pre-existing uncommitted exemplars reference
(the working-tree edit this governance work formalizes)."
```

---

### Task 6: The live lint — `tests/test_doc_governance.py`

**Files:**
- Create: `tests/test_doc_governance.py`
- Test: itself (this IS the test)

**Interfaces:**
- Consumes: `extract(REPO)` (Task 2), `vocab/shapes/doc-governance-shapes.ttl` (Task 3), the three `.rq` files (Task 4), the repo tree fixed in Task 5.
- Produces: the governance gate every loop must keep green (spec §5 “detect”); Phase 2 wires it into CI unchanged.

- [ ] **Step 1: Write the lint**

```python
# tests/test_doc_governance.py
"""The documentation-governance lint (spec §6): PROCEDURAL extraction →
SHACL membrane (hard fail) → SPARQL derivations (evidence-staleness hard,
code-staleness warning, promotion queue report). Runs on the LIVE repo."""
import warnings
from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph

from tests.docgov_extract import extract

REPO = Path(__file__).resolve().parent.parent
SHAPES = REPO / "vocab" / "shapes" / "doc-governance-shapes.ttl"
QUERIES = REPO / "vocab" / "queries"


@pytest.fixture(scope="module")
def facts() -> Graph:
    return extract(REPO)


def _construct(g: Graph, name: str) -> Graph:
    out = Graph()
    for triple in g.query((QUERIES / name).read_text()):
        out.add(triple)
    return out


def test_membrane(facts):
    """Closed world: class totality, leak boundary, nav integrity, wiki
    frontmatter, doc-impact registration."""
    conforms, _, report = validate(
        facts, shacl_graph=Graph().parse(SHAPES),
        inference="rdfs", advanced=True,
    )
    assert conforms, f"doc-governance membrane violated:\n{report}"


def test_no_wiki_page_stale_against_evidence(facts):
    stale = _construct(facts, "docgov-staleness-evidence.rq")
    assert len(stale) == 0, (
        "wiki pages stale against changed evidence (update the page + its "
        f"`updated:` date):\n{stale.serialize(format='turtle')}"
    )


def test_code_staleness_is_a_warning_not_a_gate(facts):
    stale = _construct(facts, "docgov-staleness-code.rq")
    if len(stale):
        warnings.warn(
            "wiki pages stale against cited code (non-blocking, spec §6):\n"
            + stale.serialize(format="turtle"),
            UserWarning,
        )


def test_promotion_queue_report(facts):
    queue = _construct(facts, "docgov-promotion-queue.rq")
    if len(queue):
        warnings.warn(
            f"promotion queue: {len(queue)} wiki page(s) awaiting a release "
            "(spec §5, drained at the next tag):\n"
            + queue.serialize(format="turtle"),
            UserWarning,
        )
```

- [ ] **Step 2: Run the lint against the live repo**

Run: `pytest tests/test_doc_governance.py -v -W default::UserWarning`
Expected: 4 PASS. `test_promotion_queue_report` should warn with exactly 1 queued page (`neurosymbolic-exemplars` — unpromoted by design until a release drains it). If `test_membrane` fails, the report names the offending file and rule — fix the FILE (or, if the census genuinely changed since 2026-07-31, extend the spec's allowlist/exemptions in `tests/docgov_extract.py` AND the spec §3 table in the same commit) — never special-case the shape.

- [ ] **Step 3: Run the whole suite (no regressions)**

Run: `pytest -q`
Expected: everything green (plus the two docgov UserWarnings).

- [ ] **Step 4: Commit**

```bash
git add tests/test_doc_governance.py
git commit -m "feat(docgov): live doc-governance lint — membrane + staleness + promotion queue (spec §6, Phase 1 gate)"
```

---

### Task 7: Contract updates — CLAUDE.md governance section, CI-claim corrections, canvas Doc-impact block

**Files:**
- Modify: `CLAUDE.md` (new section after “## Deferred residues — the register”; two wording corrections)
- Modify: `docs/loops/loop-canvas-template.md` (append one required section)

**Interfaces:**
- Consumes: the shipped lint (Task 6) — the section must only claim what now runs.
- Produces: the durable rules future loops and agents follow.

- [ ] **Step 1: Add the governance section to `CLAUDE.md`**

Insert after the “## Deferred residues — the register” section:

```markdown
## Documentation governance (spec 2026-07-31; lint-enforced)

Every tracked markdown file belongs to **exactly one class**, by location —
enforced by `tests/test_doc_governance.py` (SHACL membrane + SPARQL staleness,
under `pytest`): **Evidence** (`docs/superpowers/**`, `docs/loops/**`,
`docs/w3id/**` — immutable after loop close; `residues.md` is the mutable
register), **Wiki** (`docs/wiki/**` — LLM-maintained synthesis, committed,
never published), **Assertion** (the `mkdocs.yml` nav — authored, CC-BY,
describes the *released* artifact only), **Manual** (the three READMEs —
their commands must run), **Contract** (this file — edited only on explicit
request), **Confidential** (`internal/` — never tracked).

- **Agents: for concepts, read `docs/wiki/index.md` first.** Specs are
  evidence, wiki is synthesis, the site is assertion. The wiki never
  substitutes for reading the exact `.ttl`/`.py`.
- **Epistemics as in §3:** a wiki page is a *proposition* (confidence-tagged,
  cites its sources, freely rewritten); a site page is an *assertion*, entered
  only via a release (`promoted_to` records the promotion). iladub.dev builds
  from release tags, never from `main`.
- **Every spec/plan dated ≥ 2026-07-31 carries a `Doc impact:` block**
  (`none | increment | contradiction`). Increments queue for the next release;
  contradictions block the next tag (not the loop). Earlier docs grandfathered.
- **Vault is cited (`vault:…` in wiki `sources:`), never merged, never
  written** — the prose analogue of § Source ownership.
```

- [ ] **Step 2: Correct the two false CI claims in `CLAUDE.md`**

1. In “## Serialization & stack conventions”, change
   `Tests run under `pytest`; CI runs them on push/PR.` →
   `Tests run under `pytest` (CI lands with the release-train phase of the 2026-07-31 governance spec; until then, run locally before push).`
2. In “## Source ownership”, change `**CI-enforced** by` → `**pytest-enforced** by`.

- [ ] **Step 3: Add the Doc-impact section to the loop canvas template**

Append to `docs/loops/loop-canvas-template.md`:

```markdown
## ⑩ Doc impact — *required at loop close (governance spec 2026-07-31)*
One of — recorded here AND as a `Doc impact:` line in the loop's spec/plan:
- **none** — touches no documented concept.
- **increment** — adds to a state page's story → update the wiki page in-band
  (`sources:` + `updated:`); it queues for the next release.
- **contradiction** — falsifies a published claim → register it; the next
  release tag is blocked until drained (the loop itself is not).
The lint (`tests/test_doc_governance.py`) fails any spec/plan dated
≥ 2026-07-31 without the block.
```

- [ ] **Step 4: Re-run the lint and full suite**

Run: `pytest tests/test_doc_governance.py -q && pytest -q`
Expected: green (canvas template is Evidence — no doc-impact requirement applies to the template itself since its filename carries no date).

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md docs/loops/loop-canvas-template.md
git commit -m "docs(contract): documentation-governance section, honest CI wording, canvas doc-impact block (spec §8 items 3+5)"
```

---

## Completion checklist (Phase 1 definition of done)

- [ ] `pytest -q` fully green on the live repo.
- [ ] `mkdocs build --strict` succeeds; `site/` contains no `wiki/`, `superpowers/`, `loops/`, `w3id/`.
- [ ] The lint's promotion-queue warning lists exactly the seeded wiki page(s).
- [ ] `git log --oneline` shows the 6 commits above; nothing else in the working tree.
- [ ] Residue check (`docs/superpowers/residues.md`): Phase 1 defers nothing measured — if anything WAS deferred during execution (e.g. an unclassifiable file needing a spec amendment), register it as a row in the same change.
