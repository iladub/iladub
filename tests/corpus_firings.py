"""Lift corpus firings from the committed corpus baseline JSON into RDF (R259, spec 2026-09-18 § 8).

CLAUDE.md § 8 classification: PROCEDURAL raw extraction. Irreducible to AXIOM because the input
is a JSON file, not a graph -- there is no RDF evidence yet for SPARQL/SHACL to range over; this
step is what makes it. It makes no judgment and carries no tolerance: a region's reason is a
firing iff it fully matches the escalation-constant shape [A-Z][A-Z_]*, and its verdict maps
one-to-one onto a count. Everything decidable afterwards (D1 shape, D2 oracle) is SHACL/SPARQL.

Firings are derived, never authored: nothing here is written to a tracked .ttl.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

COR = Namespace("https://w3id.org/iladub/corpus#")
_CONSTANT = re.compile(r"[A-Z][A-Z_]*")
_REPO = Path(__file__).resolve().parent.parent


def _recorded_in(path: Path) -> str:
    try:
        return path.resolve().relative_to(_REPO).as_posix()
    except ValueError:
        return f"tests/corpus-baseline/{path.name}"


def lift_firings(manifest: Graph, baseline_dir: Path) -> Graph:
    """Return only the lifted triples: one cor:Firing per (document, constant reason)."""
    docs = {"corpus/" + str(f): d for d, f in manifest.subject_objects(COR.file)}
    scoped: dict[str, tuple[Path, dict]] = {}
    for path in sorted(Path(baseline_dir).glob("*.json")):
        data = json.loads(path.read_text())
        pdf = data.get("pdf")
        if not isinstance(pdf, str) or not pdf.startswith("corpus/"):
            continue
        scoped[pdf] = (path, data)

    orphans = sorted(set(scoped) - set(docs))
    if orphans:
        raise ValueError(f"baseline file(s) with no manifest document: {orphans}")
    missing = sorted(str(docs[p]) for p in set(docs) - set(scoped))
    if missing:
        raise ValueError(f"manifest document(s) with no baseline file: {missing}")

    out = Graph()
    for pdf, (path, data) in sorted(scoped.items()):
        live: Counter = Counter()
        sup: Counter = Counter()
        for page in data["pages"]:
            for region in page["regions"]:
                reason = region.get("reason")
                if not isinstance(reason, str) or not _CONSTANT.fullmatch(reason):
                    continue
                verdict = region.get("verdict")
                if verdict == "escalated":
                    live[reason] += 1
                elif verdict == "superseded":
                    sup[reason] += 1
                else:
                    raise ValueError(
                        f"{pdf}: constant reason {reason} has verdict {verdict!r}, "
                        "expected 'escalated' or 'superseded'")
        for reason in sorted(set(live) | set(sup)):
            f = BNode()
            out.add((URIRef(docs[pdf]), COR.firing, f))
            out.add((f, RDF.type, COR.Firing))
            out.add((f, COR.reason, Literal(reason)))
            out.add((f, COR.live, Literal(live[reason], datatype=XSD.nonNegativeInteger)))
            out.add((f, COR.superseded, Literal(sup[reason], datatype=XSD.nonNegativeInteger)))
            out.add((f, COR.recordedIn, Literal(_recorded_in(path))))
    return out


def live_pairs(graph: Graph) -> list[tuple[str, str]]:
    """Sorted (document IRI, reason) pairs whose cor:live is above zero."""
    pairs = set()
    for doc, f in graph.subject_objects(COR.firing):
        if int(graph.value(f, COR.live)) > 0:
            pairs.add((str(doc), str(graph.value(f, COR.reason))))
    return sorted(pairs)
