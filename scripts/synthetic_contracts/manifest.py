"""Template manifest, fetch and verify for the synthetic contract set. Licence: Apache-2.0.

Justified PROCEDURAL (CLAUDE.md § 8): network + file I/O + sha256 comparison — raw
extraction and decidable exact arithmetic, irreducible to AXIOM or NEURAL. The generator
makes documents; nothing here is a reading decision and there is no tuned constant.
Build refuses if any template's sha256 differs from the manifest (spec § 6): a mismatch is
REPORTED and the file removed — the URL now serves a different edition."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from rdflib import RDF, Graph, Namespace

from scripts.fetch_corpus import _download

REPO = Path(__file__).resolve().parents[2]
SYN = Namespace("https://w3id.org/iladub/synthetic#")
MANIFEST = REPO / "examples" / "synthetic-contracts" / "templates.ttl"
SYNTH_ROOT = REPO / "synthetic"


@dataclass(frozen=True)
class Template:
    id: str
    url: str
    sha256: str
    pages: int


class TemplateMissing(Exception):
    def __init__(self, id: str):
        super().__init__(f"template {id} is missing")
        self.id = id


class TemplateMismatch(Exception):
    def __init__(self, id: str, expected: str, actual: str):
        super().__init__(f"template {id}: sha256 {actual} != pinned {expected}")
        self.id, self.expected, self.actual = id, expected, actual


def load_manifest(path: Path = MANIFEST) -> dict[str, Template]:
    g = Graph().parse(path, format="turtle")
    out = {}
    for s in g.subjects(RDF.type, SYN.Template):
        t = Template(str(g.value(s, SYN.id)), str(g.value(s, SYN.url)),
                     str(g.value(s, SYN.sha256)), int(g.value(s, SYN.pages)))
        out[t.id] = t
    return out


def template_path(t: Template, root: Path = SYNTH_ROOT) -> Path:
    return Path(root) / "templates" / f"{t.id}.pdf"


def verify(t: Template, root: Path = SYNTH_ROOT) -> None:
    p = template_path(t, root)
    if not p.is_file():
        raise TemplateMissing(t.id)
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    if got != t.sha256:
        raise TemplateMismatch(t.id, t.sha256, got)


def fetch(root: Path = SYNTH_ROOT, download=_download, manifest: Path = MANIFEST) -> int:
    """Download absent templates, verify all. Exit code: 0 iff every template verifies."""
    bad = False
    for t in load_manifest(manifest).values():
        p = template_path(t, root)
        if not p.is_file():
            p.parent.mkdir(parents=True, exist_ok=True)
            print(f"fetching {t.id} <- {t.url}")
            try:
                p.write_bytes(download(t.url))
            except OSError as e:
                print(f"  FETCH FAILED ({e})")
                bad = True
                continue
        try:
            verify(t, root)
            print(f"  ok {t.id}")
        except TemplateMismatch as e:
            p.unlink()
            print(f"  CHECKSUM MISMATCH {t.id} (got {e.actual[:12]}...) — file removed")
            bad = True
    return 1 if bad else 0
