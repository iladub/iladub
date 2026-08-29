"""Query-term extractor — PROCEDURAL (CLAUDE.md §8 gate; spec §4.3, §6).

Justification: raw extraction only — reading `.rq` source text, parsing it to SPARQL
algebra, and emitting typed RDF facts (`etkl:QueryArtifact` / `etkl:namesTerm`). SPARQL
source text is not RDF. Irreducible to AXIOM because there is no evidence graph to derive
over until this step has run: it is the step that MAKES one. Irreducible to NEURAL because
nothing here is perceptual or underdetermined — an IRI either occurs in the query or does
not. No threshold, tolerance or tuned constant appears in this module; one would be a defect
by §8's own words.

THIS MODULE DECIDES NOTHING. It reports which owned-namespace IRIs a query names — ALL of
them, `prog:` and `docgov:` included. Whether naming one is acceptable is the membrane's
question, and it is answered in `vocab/shapes/query-declaration-shapes.ttl` (AXIOM,
constraint form, closed world), never here.

It never imports `iladub`: from a worktree the editable install resolves that package to the
MAIN tree (spec §2.1; R114/R121), so an instrument that imports it can be silently re-opened
by the tree it is meant to be measuring. The repo is located from `__file__` instead, the way
`tests/test_arc_manifest.py` does.
"""
from __future__ import annotations

import re
from pathlib import Path

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parser import parseQuery

REPO = Path(__file__).resolve().parent.parent
QUERY_DIR = REPO / "vocab" / "queries"
ONTOLOGY_DIR = REPO / "vocab" / "ontology"

ETKL = Namespace("https://w3id.org/iladub/etkl#")

#: Every namespace this project owns lives under this root (CLAUDE.md § Source ownership).
#: This is a NAMESPACE prefix, not a term list — no term is ever typed here (G3 / I4).
OWNED_ROOT = "https://w3id.org/iladub"

#: Minted subjects for the evidence graph. Not an owned namespace, so a query IRI can never
#: collide with a term under test; repo-relative, so no absolute local path reaches a
#: failure message (`tests/test_arc_landscape.py` refuses those in a tracked artifact).
_QUERY_IRI_BASE = "urn:iladub:query:"


def query_files() -> list[Path]:
    """The population: every `.rq` in `vocab/queries`, enumerated, never typed (I4)."""
    return sorted(QUERY_DIR.glob("*.rq"))


def declaring_files() -> list[Path]:
    """The disposer (spec §4.2): the NON-ALIGN owned ontologies.

    Align modules are excluded deliberately. `iladub-hga-align.ttl` makes
    `etkl:CleanDocumentHolon` a subject; counting that would let a term declared ONLY in an
    align file pass, which is precisely R117's dangling case — the hole next door.
    """
    return sorted(p for p in ONTOLOGY_DIR.glob("*.ttl") if not p.name.endswith("-align.ttl"))


def query_iri(path: Path) -> URIRef:
    """`urn:iladub:query:<repo-relative posix path>`."""
    return URIRef(_QUERY_IRI_BASE + Path(path).resolve().relative_to(REPO).as_posix())


# --------------------------------------------------------------------------------------
# Method A — the SPARQL algebra walk.
# --------------------------------------------------------------------------------------

def _walk(node, seen: set[int], out: set[str]) -> None:
    """Exhaustively collect every `URIRef` reachable from the translated algebra.

    MEASURED 2026-08-28 (plan §0.1 F2, spec §2.4) — both halves of this walk are load-bearing
    and neither may `return` before the other runs. `rdflib`'s `CompValue` IS a `dict`
    subclass AND carries its own `__dict__` alongside its items, so:
      * walking only `.items()`      -> 161 distinct owned IRIs, 12 files disagreeing with B;
      * walking items then returning -> 164 distinct, 6 files disagreeing;
      * walking items AND `__dict__` -> 171 distinct, 0 disagreements (M7).
    The terms lost are exactly the ones nested in `BIND(EXISTS { … FILTER NOT EXISTS { … } })`.
    Pinned by `test_a_term_nested_in_bind_exists_is_reported` (O3).
    """
    if id(node) in seen:
        return
    seen.add(id(node))
    if isinstance(node, URIRef):
        out.add(str(node))
        return
    if isinstance(node, str):                      # Literal/Variable/plain str: no IRI inside
        return
    if isinstance(node, dict):
        for key, value in node.items():
            _walk(key, seen, out)
            _walk(value, seen, out)
        # deliberately NOT a return — see the docstring
    if isinstance(node, (list, tuple, set, frozenset)):
        for value in node:
            _walk(value, seen, out)
    attrs = getattr(node, "__dict__", None)
    if isinstance(attrs, dict):
        for value in attrs.values():
            _walk(value, seen, out)


def _owned(iris) -> set[str]:
    return {i for i in iris if i.startswith(OWNED_ROOT)}


def named_terms_by_algebra(query_path: Path) -> set[str]:
    """Method A. Raises on a parse failure, naming the file (I3) — never a silent skip."""
    text = Path(query_path).read_text(encoding="utf-8")
    try:
        algebra = translateQuery(parseQuery(text)).algebra
    except Exception as exc:                       # noqa: BLE001 — re-raised, never swallowed
        raise ValueError(f"{query_path}: SPARQL parse failed: {exc}") from exc
    found: set[str] = set()
    _walk(algebra, set(), found)
    return _owned(found)


# --------------------------------------------------------------------------------------
# Method B — the independent text scan (I2). It shares NO code with method A: it never
# parses SPARQL, and it is the disposer of method A's completeness. If it were a rewrite of
# A, the cross-check would be theatre (spec §2.4, §3).
# --------------------------------------------------------------------------------------

_PREFIX = re.compile(r"PREFIX\s+([A-Za-z][\w.\-]*)?:\s*<([^>]*)>", re.IGNORECASE)
_PNAME = re.compile(r"(?<![\w:<])([A-Za-z][\w.\-]*)?:([A-Za-z_][\w.\-]*)")
_IRIREF = re.compile(r"<([^>\s]+)>")


def _strip_comments(text: str) -> str:
    """Drop `#`-to-end-of-line comments, respecting `<IRI>`s and quoted literals.

    A naive line-wise strip would decapitate every namespace IRI in the file — they all
    contain `#` — and silently empty the prefix map, which would make this method agree with
    a broken method A by finding nothing at all.
    """
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        char = text[i]
        if char == "#":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if char == "<":
            close = text.find(">", i)
            if close != -1 and "\n" not in text[i:close]:
                out.append(text[i:close + 1])
                i = close + 1
                continue
        if char in "'\"":
            quote = char
            out.append(char)
            i += 1
            while i < n and text[i] != quote:
                if text[i] == "\\":
                    out.append(text[i])
                    i += 1
                if i < n:
                    out.append(text[i])
                    i += 1
            if i < n:
                out.append(text[i])
                i += 1
            continue
        out.append(char)
        i += 1
    return "".join(out)


def named_terms_by_text(query_path: Path) -> set[str]:
    """Method B: read the file as text — prefix map, prefix lines removed from the body,
    comments stripped, prefixed names expanded, plus longhand `<…>` IRIs."""
    text = _strip_comments(Path(query_path).read_text(encoding="utf-8"))
    prefixes = {(m.group(1) or ""): m.group(2) for m in _PREFIX.finditer(text)}
    body = _PREFIX.sub(" ", text)
    found: set[str] = set()
    for match in _PNAME.finditer(body):
        prefix = match.group(1) or ""
        if prefix in prefixes:
            found.add(prefixes[prefix] + match.group(2))
    for match in _IRIREF.finditer(body):
        found.add(match.group(1))
    return _owned(found)


# --------------------------------------------------------------------------------------
# The evidence graph, and the declaring graph.
# --------------------------------------------------------------------------------------

def extract_named_terms(query_path: Path) -> Graph:
    """One `.rq` -> the typed RDF facts of spec §4.3:

        <query-iri>  a               etkl:QueryArtifact ;
                     etkl:namesTerm  <every owned-namespace IRI the query names> .

    EVERY owned IRI, `prog:` and `docgov:` included. Scope is the shape's decision, not this
    module's (spec §4.3: the extractor decides nothing).
    """
    graph = Graph()
    subject = query_iri(query_path)
    graph.add((subject, RDF.type, ETKL.QueryArtifact))
    for iri in named_terms_by_algebra(query_path):
        graph.add((subject, ETKL.namesTerm, URIRef(iri)))
    return graph


def evidence_graph() -> Graph:
    """The union over the whole population. One focus node per `.rq` file (O4)."""
    graph = Graph()
    for path in query_files():
        graph += extract_named_terms(path)
    return graph


def declaring_graph() -> Graph:
    """The union of the non-align owned ontologies — the closure boundary of the membrane's
    `NOT EXISTS` (spec §4.4: the vocabulary holon is what licenses the closed world)."""
    graph = Graph()
    for path in declaring_files():
        graph.parse(path, format="turtle")
    return graph
