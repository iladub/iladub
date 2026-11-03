"""Router model clients and their live gates.

PROCEDURAL — environment gates and a name table; no reading decision is made here. Irreducible to
AXIOM/NEURAL: whether a key and a generated client exist is a fact about the process environment.
"""
import importlib.util
import os

# BAML client name -> model id. Pinned to baml_src/clients.baml by tests/test_route_models.py.
# RouterJev is absent on purpose: see jev_available().
MODEL_IDS: dict[str, str] = {
    "RouterHaiku": "claude-haiku-5-5",
}


def haiku_available() -> bool:
    """Live only under `BAML_LIVE=1` with a generated client (mirrors `baml_caption_available`)."""
    return (os.environ.get("BAML_LIVE") == "1"
            and importlib.util.find_spec("baml_client") is not None)


def jev_available() -> bool:
    """Always False. The Jev seam was measured on 2026-11-03: TypeSafe documents no OpenAI-compatible
    endpoint (native `POST https://api.typesafe.ai/v1/systemone`, state + questions map) and BAML 0.222
    has no typesafe provider, so no BAML client can reach `jev-1.14.0`. Haiku decides alone (spec § 4).
    Report: .superpowers/sdd/2026-11-02-document-router/task-1-report.md
    """
    return False
