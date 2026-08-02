#!/usr/bin/env python
"""Corpus fetcher (spec 2026-08-02 §4) — justified PROCEDURAL: network + file I/O +
checksum. Reads tests/corpus-manifest.ttl, downloads absent documents into corpus/,
verifies sha256. A checksum mismatch is REPORTED and the file removed — the URL now
serves a different edition; updating the manifest is a deliberate, reviewed act."""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

from rdflib import Graph, Namespace, RDF

REPO = Path(__file__).resolve().parent.parent
COR = Namespace("https://w3id.org/iladub/corpus#")


def main() -> int:
    g = Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle")
    failures = 0
    for doc in g.subjects(RDF.type, COR.Document):
        rel, url = str(g.value(doc, COR.file)), str(g.value(doc, COR.url))
        want = str(g.value(doc, COR.sha256))
        dest = REPO / "corpus" / rel
        if dest.is_file():
            print(f"present  {rel}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"fetching {rel} <- {url}")
        try:
            urllib.request.urlretrieve(url, dest)
        except OSError as e:
            print(f"  FETCH FAILED ({e}) — URL may have rotted; document skipped")
            failures += 1
            continue
        got = hashlib.sha256(dest.read_bytes()).hexdigest()
        if got != want:
            dest.unlink()
            print(f"  CHECKSUM MISMATCH (got {got[:12]}…) — a different edition now "
                  f"lives at this URL; file removed, manifest unchanged")
            failures += 1
        else:
            print(f"  ok ({want[:12]}…)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
