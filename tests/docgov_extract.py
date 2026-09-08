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
from decimal import Decimal
from pathlib import Path
from typing import Mapping, Sequence

import yaml
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

DG = Namespace("https://w3id.org/iladub/docgov#")
_DOC = "https://w3id.org/iladub/docgov/doc/"

MANUAL_ALLOWLIST = frozenset({
    "README.md", "vocab/README.md", "demo/README-etkl-showcase.md", "RELEASE.md",
})
EVIDENCE_DIRS = ("docs/superpowers/", "docs/loops/", "docs/w3id/")
EXEMPT_PREFIXES = (".claude/", ".agents/")
#: The contradiction-drain register (spec 2026-09-08 §4.1) — a tracked governance
#: input read like mkdocs.yml, not a derived fact. It is loaded HERE rather than in
#: scripts/release_gate.py so that the SHACL membrane validates the drains in the same
#: graph it validates the documents: both of ContradictionDrainShape's sh:sparql
#: constraints are joins against extracted doc facts and are unexpressible otherwise.
DRAIN_REGISTER = Path("tests") / "docgov-drains.ttl"
#: The corpus reading register (spec 2026-09-08 §3.1) — the dated readings a prose
#: figure may be a quotation OF. It is READ, never written (spec §6 I2), and it is not
#: merged into the fact graph: its thousands of prose triples would swamp the membrane,
#: so denoted readings are re-minted here as dg:Reading nodes carrying only what a
#: finding must be able to say — which document, which value, read on which day.
READING_REGISTER = Path("tests") / "corpus-manifest.ttl"
COR = Namespace("https://w3id.org/iladub/corpus#")
_READING = "https://w3id.org/iladub/docgov/reading/"


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


# ---------------------------------------------------------------- figures
# PROCEDURAL (spec §2, D3): decidable exact arithmetic over a lexical form. There is
# no tolerance and no threshold anywhere below — the precision of a claim is the
# author's, read off the literal they wrote, never a constant this module chooses.

#: A decimal literal, not part of a longer dotted token (a version, an IP, a range).
_DECIMAL = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
#: What dates a block: an ISO date, or a backticked commit sha (>= one digit, so an
#: ordinary hex-lettered word in backticks is not mistaken for a commit).
_ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_SHA = re.compile(r"`(?=[0-9a-f]*\d)[0-9a-f]{7,40}`")


def blocks(text: str) -> list[tuple[int, list[str]]]:
    """(first line number, lines) for every maximal run of non-blank lines.

    The block is the closure boundary for datedness (spec §3.2), exactly as a holon
    is elsewhere (CLAUDE.md §8). MEASURED reason it is not the line:
    docs/wiki/concepts/dimension-split.md carries `(tests/test_cbh_e2e.py, 2026-08-04)`
    one line above the figures it dates, so a line-scoped rule reports a correctly
    dated claim as a finding."""
    out: list[tuple[int, list[str]]] = []
    start, run = 0, []
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not run:
                start = n
            run.append(line)
        elif run:
            out.append((start, run))
            run = []
    if run:
        out.append((start, run))
    return out


def is_dated(block: str) -> bool:
    return bool(_ISO_DATE.search(block) or _SHA.search(block))


def separating_precision(values: Sequence[Decimal]) -> int:
    """Least k at which every registered value is pairwise distinct at k decimals.

    NOT a threshold and NOT tuned: it is a property OF the register, recomputed from
    it on every run, with no free parameter. Below it the register cannot identify its
    own rows, so a literal at that precision is under-determined by construction and
    cannot be a quotation of the register — whichever single row it happens to collide
    with in one particular sample. This is what makes a `0.1` in prose ("quarantines
    exactly like a 0.1-scored one") not a claim about a corpus score, without any
    minimum-precision constant being chosen to make it so."""
    for k in range(20):
        rounded = [round(v, k) for v in values]
        if len(set(rounded)) == len(rounded):
            return k
    raise ValueError("register holds two identical values — one node per distinct value")


def denotes(lexical: str, readings: Mapping[str, Decimal], sep: int) -> str | None:
    """The unique reading `lexical` is a quotation of, or None.

    `round(value, k) == Decimal(lexical)` with k read off the literal itself — exact
    decimal arithmetic, no epsilon (spec §6 I1). None when k < sep (under-determined,
    see separating_precision) or when zero or more than one reading satisfies it:
    an ambiguous form is not a finding, which is the honest reading and not a
    softening."""
    k = len(lexical.partition(".")[2])
    if k < sep:
        return None
    want = Decimal(lexical)
    hits = [key for key, value in readings.items() if round(value, k) == want]
    return hits[0] if len(hits) == 1 else None


def load_readings(repo: Path) -> tuple[Graph, dict[str, Decimal], set[str]]:
    """The register, as (facts to emit, key -> value, keys that may not be quoted).

    One dg:Reading node per registered corpus reading, keyed by document slug and
    value so that a finding can name what the figure claims to be."""
    reg = Graph().parse(repo / READING_REGISTER)
    facts, values, unquotable = Graph(), {}, set()
    for doc, node in reg.subject_objects(COR.reading):
        value = Decimal(str(reg.value(node, COR.value)))
        slug = str(doc).rsplit(":", 1)[-1]
        key = f"{slug}/{value}"
        iri = URIRef(_READING + key)
        facts.add((iri, RDF.type, DG.Reading))
        facts.add((iri, DG.readingOf, Literal(slug)))
        facts.add((iri, DG.readingValue, Literal(value)))
        for d in reg.objects(node, COR.readAt):
            facts.add((iri, DG.readAt, Literal(str(d), datatype=XSD.date)))
        values[key] = value
        if reg.value(node, COR.notQuotable):
            unquotable.add(key)
    return facts, values, unquotable


def _figure_facts(g: Graph, d: URIRef, path: str, text: str,
                  values: Mapping[str, Decimal], sep: int) -> None:
    """Emit one dg:FigureOccurrence per literal that DENOTES a registered reading.

    A literal denoting nothing emits nothing: the graph carries figures, not every
    decimal in the tree. Whether a denoting occurrence is admissible is not decided
    here — that is the membrane's (spec §2, D2) and this function stays a pure fact
    emitter (spec §6 I3)."""
    for start, lines in blocks(text):
        dated = Literal(is_dated("\n".join(lines)))
        for offset, line in enumerate(lines):
            for m in _DECIMAL.finditer(line):
                key = denotes(m.group(), values, sep)
                if key is None:
                    continue
                n = start + offset
                occ = URIRef(f"{_DOC}{path}#figure-{n}-{m.start()}")
                g.add((occ, RDF.type, DG.FigureOccurrence))
                g.add((occ, DG.inDoc, d))
                g.add((occ, DG.line, Literal(n)))
                g.add((occ, DG.lexical, Literal(m.group())))
                g.add((occ, DG.blockDated, dated))
                g.add((occ, DG.denotesReading, URIRef(_READING + key)))


def doc_iri(path: str) -> URIRef:
    return URIRef(_DOC + path)


def extract(repo: Path) -> Graph:
    _require_full_history(repo)
    g = Graph()
    g.bind("dg", DG)
    g.parse(repo / DRAIN_REGISTER)
    cfg = load_mkdocs(repo / "mkdocs.yml")
    nav = nav_paths(cfg)
    prefixes = exclude_prefixes(cfg)
    index_links = _index_links(repo)
    reading_facts, values, unquotable = load_readings(repo)
    g += reading_facts
    # The quotable extension is what a FINDING may name; the ambiguity test in
    # `denotes` runs over the WHOLE register (spec §3.3, plan D-C) — dropping a row
    # would shrink the extension `sep` is computed from and could silently promote a
    # different literal to uniqueness.
    sep = separating_precision(list(values.values()))
    quotable = {k: v for k, v in values.items() if k not in unquotable}

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
        # Read once, here: _evidence_facts and _wiki_facts each used to open the file
        # for themselves, and the figure walk covers EVERY tracked markdown file.
        text = (repo / path).read_text()
        _figure_facts(g, d, path, text, quotable, sep)
        if cls == "evidence":
            _evidence_facts(g, d, path, text)
        elif cls == "wiki":
            _wiki_facts(g, repo, d, path, text)
            if path != "docs/wiki/index.md":
                g.add((d, DG.inWikiIndex, Literal(path in index_links)))
    return g


def _evidence_facts(g: Graph, d: URIRef, path: str, text: str) -> None:
    m = _DATED.match(path)
    if not m:
        return
    g.add((d, DG.docDate,
           Literal(date(int(m[1]), int(m[2]), int(m[3])), datatype=XSD.date)))
    mi = _IMPACT.search(text)
    if mi:
        g.add((d, DG.docImpact, Literal(mi.group(1))))


def _index_links(repo: Path) -> set[str]:
    """Paths (repo-relative) that docs/wiki/index.md links to — PROCEDURAL
    extraction of markdown link targets, resolved against docs/wiki/."""
    idx = repo / "docs" / "wiki" / "index.md"
    if not idx.is_file():
        return set()
    return {
        str((Path("docs/wiki") / m).as_posix())
        for m in re.findall(r"\]\(([^)#]+\.md)\)", idx.read_text())
    }


def _wiki_facts(g: Graph, repo: Path, d: URIRef, path: str, text: str) -> None:
    fm = parse_frontmatter(text)
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
