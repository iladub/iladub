"""REPRODUCER + workaround for a measured defect in docling-graph v1.9.1. NOT iladub code.

THIS IS A THIRD-PARTY WORKAROUND, committed only so the 2026-09-17 benchmark is
reproducible (see docs/superpowers/2026-09-17-docling-graph-benchmark-evidence.md s3b).
iladub neither vendors nor maintains docling-graph; this patches it at runtime, in a
scratch venv, and nothing in iladub imports it.

THE DEFECT, measured: docling_graph/llm_clients/schema_utils.py:11-53
`normalize_schema_for_response_format` returns `strict: True` but never sets
`additionalProperties: false` and never promotes optional properties into `required`.
OpenAI strict mode requires both, recursively, so EVERY json_schema request is rejected:

    litellm.BadRequestError: OpenAIException - Invalid schema for response_format
    'extraction_result': In context=(), 'additionalProperties' is required to be
    supplied and to be false.

`_call_api` (llm_clients/litellm.py:237-257) catches it, logs a WARNING, falls back to
legacy prompt-schema mode, and reports "Pipeline Completed Successfully" -- so the failure
is SILENT and the graph is near-empty (1 cell of ~200 on apple p0).

THE CONTROL that makes it a defect rather than an environment fault: the identical LiteLLM
path, same venv/key/model, with a HAND-WRITTEN strict schema succeeds. Only schemas built
by their normalizer are rejected -- including ones from their own induced templates.

USAGE: place on PYTHONPATH as `sitecustomize.py` beside the generated template, so CPython
imports it at interpreter start, before the docling-graph CLI runs.
"""

import docling_graph.llm_clients.litellm as L

_orig = L.normalize_schema_for_response_format


def _strictify(node):
    if isinstance(node, list):
        for v in node:
            _strictify(v)
        return node
    if not isinstance(node, dict):
        return node
    props = node.get("properties")
    if isinstance(props, dict):
        node["additionalProperties"] = False
        required = set(node.get("required", []))
        for key, sub in props.items():
            if key not in required:
                props[key] = {"anyOf": [sub, {"type": "null"}]}
        node["required"] = list(props.keys())
    for value in node.values():
        _strictify(value)
    return node


def _patched(schema, **kwargs):
    out = _orig(schema, **kwargs)
    _strictify(out.get("schema", out))
    return out


L.normalize_schema_for_response_format = _patched
