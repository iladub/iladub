"""Knowledge-guided extraction.

The contract's field rules tell extraction *what to look for*; extraction does
not invent values. Each rule is a (target property, regex) pair whose first
capture group is the extracted value. Only what the source supports is emitted.
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

from rdflib import URIRef

from .readers import read_document


def extract(input_path: str, target_paths: List[Tuple[URIRef, str]]) -> Dict[URIRef, str]:
    """Read ``input_path`` and pull the value for each (property, pattern) rule."""
    text = read_document(input_path)
    fields: Dict[URIRef, str] = {}
    for prop, pattern in target_paths:
        match = re.search(pattern, text)
        if match and match.group(1).strip():
            fields[prop] = match.group(1).strip()
    return fields
