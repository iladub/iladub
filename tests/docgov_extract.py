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
