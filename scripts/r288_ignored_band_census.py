"""R288 census — every `etkl:IgnoredBand` corpus-wide: its reason, word count, and text head.

PROCEDURAL (CLAUDE.md s8): raw extraction only. It compiles each corpus document and lists the
ignored bands' carried text; it decides nothing about any band and changes no reading.

Run from the repo root (corpus runs are serial; ~10 min for the 7 documents):
    env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python \
        scripts/r288_ignored_band_census.py
"""
import pathlib
import sys

sys.path.insert(0, "src")
from rdflib import RDF, Namespace

from iladub.etkl.document import compile_document

E = Namespace("https://w3id.org/iladub/etkl#")

for pdf in sorted(pathlib.Path("corpus").rglob("*.pdf")):
    rep = compile_document(str(pdf))
    g = rep.graph
    rows = []
    for b in g.subjects(RDF.type, E.IgnoredBand):
        t = str(g.value(b, E.bandText) or "")
        why = str(g.value(b, E.ignoredBecause) or "")
        rows.append((str(b), len(t.split()), why[:40], t.replace("\n", " | ")[:150]))
    print(f"### {pdf.stem} score={rep.score} ignored={len(rows)} "
          f"words={sum(r[1] for r in rows)}", flush=True)
    for r in sorted(rows):
        print("  ", r[0].split("/")[-2:], r[1], r[2], "::", r[3], flush=True)
