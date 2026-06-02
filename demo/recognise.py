"""Knowledge-driven concept recognition for the demo.

Scans free-text prose for the surface forms (SKOS pref/alt labels, any
language) declared in a knowledge graph, and returns the concepts found.
The ontology drives extraction — only declared concepts are recognised.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from rdflib import Graph, URIRef
from rdflib.namespace import SKOS


@dataclass(frozen=True)
class Mention:
    concept: URIRef
    matched_text: str


def recognise(text: str, knowledge: Graph) -> List[Mention]:
    """Return one Mention per knowledge concept whose label appears in ``text``."""
    low = text.lower()
    mentions: List[Mention] = []
    seen = set()
    for concept in set(knowledge.subjects(SKOS.prefLabel, None)):
        if concept in seen:
            continue
        labels = list(knowledge.objects(concept, SKOS.prefLabel)) + \
            list(knowledge.objects(concept, SKOS.altLabel))
        for label in labels:
            surface = str(label).strip()
            if surface and surface.lower() in low:
                mentions.append(Mention(concept, surface))
                seen.add(concept)
                break
    return mentions
