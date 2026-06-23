"""Thin DataBook (W3C Holon CG) I/O adapter — read/write only.

A DataBook is how a holon is serialized: YAML frontmatter (context layer),
typed fenced blocks (interior), prose (projection). This module parses and
emits that markdown; it deliberately does NOT implement the DataBook CLI,
triplestore push/pull, or the format spec — those are the CG's responsibility.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

import yaml
from rdflib import Graph

_FM_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
_META_RE = re.compile(r"<!--\s*databook:(\w+):\s*(.*?)\s*-->")
_FENCE_OPEN = re.compile(r"^```(\w*)\s*$")
_FENCE_CLOSE = re.compile(r"^```\s*$")

_RDF_LANGS = {"turtle", "turtle12", "trig", "shacl", "ntriples"}


@dataclass
class Block:
    lang: str
    content: str
    id: Optional[str] = None
    graph_iri: Optional[str] = None


@dataclass
class Databook:
    frontmatter: dict = field(default_factory=dict)
    prose: str = ""
    blocks: list = field(default_factory=list)

    def graph(self, *selectors) -> Graph:
        """Parse the requested RDF blocks (by block id or by lang) into one graph.
        With no selectors, merge every RDF block."""
        g = Graph()
        want = set(selectors)
        for b in self.blocks:
            if b.lang not in _RDF_LANGS:
                continue
            if want and b.id not in want and b.lang not in want:
                continue
            g.parse(data=b.content, format="turtle")
        return g


def read_databook(path: str) -> Databook:
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    m = _FM_RE.match(raw)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    frontmatter = yaml.safe_load(m.group(1)) or {}
    blocks: list = []
    prose_lines: list = []
    pending: dict = {}
    lines = m.group(2).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        meta = _META_RE.search(line)
        fence = _FENCE_OPEN.match(line)
        if meta and not fence:
            pending[meta.group(1)] = meta.group(2)
            i += 1
            continue
        if fence:
            lang = fence.group(1)
            body: list = []
            i += 1
            while i < len(lines) and not _FENCE_CLOSE.match(lines[i]):
                body.append(lines[i])
                i += 1
            i += 1  # consume closing fence
            blocks.append(Block(lang=lang, content="\n".join(body),
                                id=pending.get("id"), graph_iri=pending.get("graph")))
            pending = {}
            continue
        prose_lines.append(line)
        i += 1
    return Databook(frontmatter=frontmatter,
                    prose="\n".join(prose_lines).strip(),
                    blocks=blocks)


def write_databook(frontmatter: dict, blocks, prose: str, path: str) -> None:
    out = ["---", yaml.safe_dump(frontmatter, sort_keys=False).strip(), "---", ""]
    if prose:
        out.append(prose)
        out.append("")
    for b in blocks:
        if b.id:
            out.append(f"<!-- databook:id: {b.id} -->")
        if b.graph_iri:
            out.append(f"<!-- databook:graph: {b.graph_iri} -->")
        out.append(f"```{b.lang}")
        out.append(b.content)
        out.append("```")
        out.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out).rstrip() + "\n")


_REQUIRED = ("id", "title", "type", "version", "created")
_PROCESS_REQUIRED = ("transformer", "transformer_type", "inputs", "timestamp")


def validate_frontmatter(fm: dict, require_process: bool = False) -> list:
    """Return a list of human-readable problems (empty == valid)."""
    errs = [f"missing frontmatter key: {k}" for k in _REQUIRED if k not in fm]
    if require_process:
        proc = fm.get("process")
        if not isinstance(proc, dict):
            errs.append("missing process stamp")
        else:
            errs += [f"missing process.{k}" for k in _PROCESS_REQUIRED if k not in proc]
    return errs
