"""Source-ownership boundary (durable decision — see CLAUDE.md § Source ownership).

We DEVELOP only our own namespaces (etkl / dec / iladub / risk, all under
https://w3id.org/iladub/etkl…). HGA (Cagle's W3C Holon CG ontology, http://w3id.org/holon/
and its sub-namespaces hev:/hpol:/hmk:/hproj:/hbayes:/hprov:/hspec:/hmedia:/hvc:) is an
EXTERNAL source of truth we CONSUME. We never define, redefine, or extend an HGA term.

The invariant, in one line:
    In every authored RDF file, the SUBJECT of every triple is a term WE own.
    HGA terms appear ONLY as objects/types/targets, and a hard-standalone set of core
    ontologies must not reference HGA at all (they stay reasoner-free).

Two enforced rules:
  A. Standalone core: vocab/ontology/*.ttl EXCEPT *-hga-align.ttl contain NO HGA IRI.
  B. No redefinition: across all authored .ttl (vocab/ + examples/ + tests/*.ttl),
     no HGA IRI is ever a triple SUBJECT.
"""
import glob
import os

from rdflib import Graph, URIRef

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The HGA authority. Every HGA sub-namespace (holon:/hev:/hpol:/hmk:/hproj:/hbayes:/
# hprov:/hspec:/hmedia:/hvc:) shares this base. NOTE: distinct from the doc pointer
# https://github.com/w3c-cg/holon, which is a see-also link, not a term IRI.
HGA_BASE = "http://w3id.org/holon/"


def _ttls(*relglobs):
    out = []
    for rg in relglobs:
        out.extend(sorted(glob.glob(os.path.join(ROOT, rg))))
    return out


def _is_align(path):
    return path.endswith("-hga-align.ttl")


def test_core_ontologies_are_standalone():
    """Rule A: core ontology files (not the alignment modules) must not reference HGA
    at all — they stay standalone and reasoner-free. Alignment lives only in
    *-hga-align.ttl."""
    offenders = []
    for path in _ttls("vocab/ontology/*.ttl"):
        if _is_align(path):
            continue
        text = open(path, encoding="utf-8").read()
        if HGA_BASE in text:
            offenders.append(os.path.relpath(path, ROOT))
    assert not offenders, (
        "core ontology files must not reference HGA (move alignment to a "
        f"*-hga-align.ttl module): {offenders}")


def test_no_authored_file_redefines_an_hga_term():
    """Rule B: we never define/redefine an HGA term — no HGA IRI may appear as a triple
    SUBJECT in any authored file. HGA terms may appear only as objects/types/targets."""
    offenders = []
    for path in _ttls("vocab/ontology/*.ttl", "vocab/shapes/*.ttl",
                       "examples/**/*.ttl", "examples/*.ttl", "tests/*.ttl"):
        g = Graph()
        try:
            g.parse(path, format="turtle")
        except Exception as exc:  # a fixture that is *syntactically* invalid is not our concern here
            raise AssertionError(f"{os.path.relpath(path, ROOT)} failed to parse: {exc}")
        for s in set(g.subjects()):
            if isinstance(s, URIRef) and str(s).startswith(HGA_BASE):
                offenders.append((os.path.relpath(path, ROOT), str(s)))
    assert not offenders, (
        "HGA terms must never be the subject of a triple in our files "
        f"(we consume, never redefine): {offenders}")


def test_alignment_modules_only_point_outward():
    """An *-hga-align.ttl is OURS: every subject is one of our terms (etkl/dec/iladub/
    risk) or our own ontology-metadata IRI; HGA IRIs appear only as objects."""
    ours = "https://w3id.org/iladub"
    offenders = []
    for path in _ttls("vocab/ontology/*-hga-align.ttl"):
        g = Graph()
        g.parse(path, format="turtle")
        for s in set(g.subjects()):
            if isinstance(s, URIRef) and not str(s).startswith(ours):
                offenders.append((os.path.relpath(path, ROOT), str(s)))
    assert not offenders, (
        f"alignment-module subjects must be our own terms: {offenders}")
