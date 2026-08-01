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


_DATED = re.compile(r"^docs/superpowers/(?:specs|plans)/(\d{4})-(\d{2})-(\d{2})-")

# First valid declared value wins; an invalid/missing declaration emits no fact,
# and the membrane fails it loudly (honest failure — R22).
_IMPACT = re.compile(r"\*{0,2}Doc impact:\*{0,2}\s*(none|increment|contradiction)\b")


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


def _require_full_history(repo: Path) -> None:
    """On a shallow clone, `git log -1 -- <path>` silently returns HEAD's date
    for every path (no history to walk) — wrong lastCommitDate for every doc,
    a false staleness pass/fail. Fail loudly instead of guessing (honest-
    failure principle, CLAUDE.md § Core design principles)."""
    out = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"], cwd=repo,
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    if out == "true":
        raise RuntimeError(
            "docgov extract requires full git history (shallow clone "
            "detected): fetch with --unshallow / fetch-depth: 0"
        )


def doc_iri(path: str) -> URIRef:
    return URIRef(_DOC + path)


def extract(repo: Path) -> Graph:
    _require_full_history(repo)
    g = Graph()
    g.bind("dg", DG)
    cfg = load_mkdocs(repo / "mkdocs.yml")
    nav = nav_paths(cfg)
    prefixes = exclude_prefixes(cfg)

    for np in sorted(nav):
        entry = URIRef(_DOC + "nav/" + np)
        g.add((entry, RDF.type, DG.NavEntry))
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
    g.add((d, DG.docDate,
           Literal(date(int(m[1]), int(m[2]), int(m[3])), datatype=XSD.date)))
    mi = _IMPACT.search((repo / path).read_text())
    if mi:
        g.add((d, DG.docImpact, Literal(mi.group(1))))


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
        lcd = last_commit_date(repo, src)
        if lcd:
            g.add((s, DG.lastCommitDate, Literal(lcd, datatype=XSD.date)))
    if fm.get("promoted_to"):
        g.add((d, DG.promotedTo, doc_iri(fm["promoted_to"])))
