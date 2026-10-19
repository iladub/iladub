"""Lift corpus firings from the committed corpus baseline JSON into RDF (R259, spec 2026-09-18 § 8).

CLAUDE.md § 8 classification: PROCEDURAL raw extraction. Irreducible to AXIOM because the input
is a JSON file, not a graph -- there is no RDF evidence yet for SPARQL/SHACL to range over; this
step is what makes it. It makes no judgment and carries no tolerance: a region's reason is a
firing iff it fully matches the escalation-constant shape [A-Z][A-Z_]*, and its verdict maps
one-to-one onto a count. Everything decidable afterwards (D1 shape, D2 oracle) is SHACL/SPARQL.

Firings are derived, never authored: nothing here is written to a tracked .ttl.

lift_snapshots (tab:07, spec 2026-10-19 § 4.1 row 3, § 4.3) is the same PROCEDURAL class: it reads a
dated git blob (`git cat-file`) and the first-parent history of origin/main (`git log --raw`) and
emits the facts it finds -- the blob's constant-reason counts, which manifest document its "pdf"
names, and whether the blob is durable. Irreducible to AXIOM for the same reason: git's object store
is not a graph. It judges nothing; admissibility of the disposal over these facts is SHACL (D2).
"""
from __future__ import annotations

import json
import re
import subprocess
from functools import lru_cache
from collections import Counter
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

COR = Namespace("https://w3id.org/iladub/corpus#")
_CONSTANT = re.compile(r"[A-Z][A-Z_]*")
_REPO = Path(__file__).resolve().parent.parent


def _recorded_in(path: Path) -> str:
    """The path actually read: repo-relative when under the repo, else its absolute path.
    Never a path that was not read (CLAUDE.md principle 7: emit only what the source supports)."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(_REPO).as_posix()
    except ValueError:
        return resolved.as_posix()


def _docs_by_pdf(manifest: Graph) -> dict[str, URIRef]:
    docs: dict[str, URIRef] = {}
    for d, f in sorted(manifest.subject_objects(COR.file)):
        key = "corpus/" + str(f)
        if key in docs and docs[key] != d:
            raise ValueError(f"cor:file {str(f)!r} is claimed by two manifest documents: "
                             f"{sorted([str(docs[key]), str(d)])}")
        docs[key] = d
    return docs


def _count_firings(pdf: str, data: dict) -> tuple[Counter, Counter]:
    """The one counting core: constant-reason regions by verdict (shared by both lifts)."""
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
    return live, sup


def _emit_firings(out: Graph, subject, live: Counter, sup: Counter, recorded_in: str) -> None:
    for reason in sorted(set(live) | set(sup)):
        f = BNode()
        out.add((subject, COR.firing, f))
        out.add((f, RDF.type, COR.Firing))
        out.add((f, COR.reason, Literal(reason)))
        out.add((f, COR.live, Literal(live[reason], datatype=XSD.nonNegativeInteger)))
        out.add((f, COR.superseded, Literal(sup[reason], datatype=XSD.nonNegativeInteger)))
        out.add((f, COR.recordedIn, Literal(recorded_in)))


def lift_firings(manifest: Graph, baseline_dir: Path) -> Graph:
    """Return only the lifted triples: one cor:Firing per (document, constant reason)."""
    docs = _docs_by_pdf(manifest)
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
        live, sup = _count_firings(pdf, data)
        _emit_firings(out, URIRef(docs[pdf]), live, sup, _recorded_in(path))
    return out


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"git {' '.join(args)} failed in {repo}: {r.stderr.strip()}")
    return r.stdout


@lru_cache(maxsize=None)
def _main_blobs(repo: str, main_sha: str, path: str) -> frozenset[str]:
    """Post-image blobs of `path` over origin/main's first-parent history. One query per
    (repo, origin/main sha, path). A --raw line is `:old_mode new_mode old_sha new_sha STATUS\tpath`;
    only the post-image (field 3) counts -- a deletion's pre-image is a blob that is gone, and its
    post-image is all zeros, which is never a blob."""
    out = _git(Path(repo), "log", "--first-parent", "--raw", "--no-abbrev", "--format=",
               main_sha, "--", path)
    blobs = set()
    for line in out.splitlines():
        meta = line.split("\t", 1)[0].split()
        if len(meta) >= 5 and not set(meta[3]) <= {"0"}:
            blobs.add(meta[3])
    return frozenset(blobs)


def _durable(repo: Path, path: str, blob: str) -> bool:
    try:
        if _git(repo, "rev-parse", f"HEAD:{path}").strip() == blob:
            return True
    except ValueError:
        pass                                    # no such path in HEAD's tree: fall to history
    try:
        main_sha = _git(repo, "rev-parse", "--verify", "origin/main").strip()
    except ValueError as e:
        raise ValueError(f"cannot decide durability of {path}@{blob}: origin/main is absent "
                         f"(fetch it; never fall back to HEAD's chain): {e}") from e
    return blob in _main_blobs(str(Path(repo).resolve()), main_sha, path)


def lift_snapshots(manifest: Graph, repo: Path = _REPO) -> Graph:
    """Return only the lifted triples for each cor:judgedAgainst snapshot, attached to the same node:
    its blob's firings, cor:snapshotOf, cor:durable."""
    snaps = sorted(set(manifest.objects(None, COR.judgedAgainst)))
    out = Graph()
    if not snaps:
        return out
    docs = _docs_by_pdf(manifest)
    for snap in snaps:
        blob = str(manifest.value(snap, COR.blob))
        path = str(manifest.value(snap, COR.recordedIn))
        data = json.loads(_git(repo, "cat-file", "-p", blob))
        pdf = data.get("pdf")
        if pdf not in docs:
            raise ValueError(f"snapshot {path}@{blob}: pdf {pdf!r} matches no manifest cor:file")
        live, sup = _count_firings(pdf, data)
        _emit_firings(out, snap, live, sup, f"{path}@{blob}")
        out.add((snap, COR.snapshotOf, URIRef(docs[pdf])))
        out.add((snap, COR.durable, Literal(_durable(repo, path, blob), datatype=XSD.boolean)))
    return out


def live_pairs(graph: Graph) -> list[tuple[str, str]]:
    """Sorted (document IRI, reason) pairs whose cor:live is above zero."""
    pairs = set()
    for doc, f in graph.subject_objects(COR.firing):
        if not isinstance(doc, URIRef):
            continue                            # snapshot nodes are not documents (spec § 8 A8)
        if int(graph.value(f, COR.live)) > 0:
            pairs.add((str(doc), str(graph.value(f, COR.reason))))
    return sorted(pairs)
