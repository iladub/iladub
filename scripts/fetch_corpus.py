#!/usr/bin/env python
"""Corpus fetcher (spec 2026-08-02 §4) — justified PROCEDURAL: network + file I/O +
checksum, irreducible to AXIOM/NEURAL. Reads tests/corpus-manifest.ttl, downloads
absent documents into corpus/, verifies sha256. A checksum mismatch is REPORTED and
the file removed — the URL now serves a different edition; updating the manifest is a
deliberate, reviewed act.

First fetch of a fresh entry (no cor:sha256 yet): the file is KEPT and the values the
manifest needs (sha256, producer, pages, date) are PRINTED for a deliberate manifest
edit — never written back automatically (spec §4 verdict discipline). Exit is nonzero
until every entry is pinned and verified, so an unpinned register is always visible."""
from __future__ import annotations

import datetime
import hashlib
import urllib.request
from pathlib import Path

from rdflib import Graph, Namespace, RDF

REPO = Path(__file__).resolve().parent.parent
COR = Namespace("https://w3id.org/iladub/corpus#")

# Institutional CDNs/WAFs (GrainCorp's included — measured, loop L) return 403 to bare
# "Python-urllib". A plain desktop browser UA is enough; nothing else is spoofed.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def _pdf_facts(dest: Path) -> tuple[str | None, int]:
    import pdfplumber
    with pdfplumber.open(dest) as pdf:
        return (pdf.metadata or {}).get("Producer"), len(pdf.pages)


def fetch_one(g: Graph, doc, corpus_root: Path, download=_download) -> str:
    """One manifest document -> 'present'|'fetched'|'pin'|'mismatch'|'failed'."""
    rel, url = str(g.value(doc, COR.file)), str(g.value(doc, COR.url))
    want = g.value(doc, COR.sha256)
    dest = Path(corpus_root) / rel
    if dest.is_file():
        print(f"present  {rel}")
        return "present"
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"fetching {rel} <- {url}")
    try:
        data = download(url)
    except OSError as e:
        print(f"  FETCH FAILED ({e}) — URL may have rotted; document skipped")
        return "failed"
    dest.write_bytes(data)
    got = hashlib.sha256(data).hexdigest()
    if want is None:
        producer, pages = _pdf_facts(dest)
        print("  FIRST FETCH — pin these in tests/corpus-manifest.ttl "
              "(a deliberate edit, never automatic):")
        print(f'    cor:producer "{producer}" ;')
        print(f'    cor:fetched "{datetime.date.today().isoformat()}"^^xsd:date ;')
        print(f'    cor:sha256 "{got}" ;')
        print(f"    cor:pages {pages} ;")
        return "pin"
    if got != str(want):
        dest.unlink()
        print(f"  CHECKSUM MISMATCH (got {got[:12]}…) — a different edition now "
              f"lives at this URL; file removed, manifest unchanged")
        return "mismatch"
    print(f"  ok ({got[:12]}…)")
    return "fetched"


def main() -> int:
    g = Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle")
    outcomes = [fetch_one(g, doc, REPO / "corpus")
                for doc in g.subjects(RDF.type, COR.Document)]
    return 1 if any(o in ("mismatch", "failed", "pin") for o in outcomes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
