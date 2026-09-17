"""R247's seam, measured OFFLINE: is docling-graph's one-node graph a tool limit or a template flag?

NOT iladub code. A third-party probe, committed only so the measurement recorded in
docs/superpowers/2026-09-17-r247-seam-measured.md is reproducible. It runs in the benchmark's
scratch venv (docling-graph 1.9.1), and nothing in iladub imports it.

WHAT IT DOES: takes an extraction that was ALREADY recorded (the single root node of a run's
graph.json, components embedded), re-validates it against the same generated template with every
`is_entity=False` turned to `is_entity=True`, and hands it to docling-graph's own GraphConverter.
No LLM is called and no document is read, so the run is free and deterministic.

THE CONTROL: each template is also converted UNFLIPPED. That arm must reproduce the recorded
one-node, zero-edge graph; if it does not, the offline path is not the path the CLI took and the
flipped figure means nothing.

WHAT IT DOES NOT MEASURE: extraction under a flipped template. `is_entity` is also read by the
dense extraction catalog (core/extractors/contracts/dense/catalog.py), so an LLM run with the
flipped template is a different extraction, unrun here.

PROCEDURAL, justified: it drives a third-party converter over recorded JSON; there is no iladub
decision in it to classify.

USAGE: <harness>/dgvenv/bin/python entity_flip_seam.py <harness> <workdir>
  <harness> holds tmpl/<template>.py and run/<rundir>/*/docling_graph/graph.json
"""

import collections
import glob
import importlib.util
import json
import pathlib
import sys

from docling_graph.core.converters.graph_converter import GraphConverter

ARMS = [
    ("apple_induced", "FinancialStatement", "out_patched_control"),
    ("tab_min", "HierarchicalTable", "out_patched_tabmin"),
]


def _load(src: str, name: str, workdir: pathlib.Path):
    path = workdir / f"{name}.py"
    path.write_text(src)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def convert(harness: pathlib.Path, workdir: pathlib.Path, tmpl: str, root: str, rundir: str, flip: bool):
    src = (harness / "tmpl" / f"{tmpl}.py").read_text()
    flags = src.count("is_entity=False")
    if flip:
        src = src.replace("is_entity=False", "is_entity=True")
    module = _load(src, f"{tmpl}_{'flipped' if flip else 'control'}", workdir)
    recorded = glob.glob(str(harness / "run" / rundir / "*" / "docling_graph" / "graph.json"))[0]
    node = json.loads(pathlib.Path(recorded).read_text())["nodes"][0]
    model = getattr(module, root)
    instance = model.model_validate({k: v for k, v in node.items() if k in model.model_fields})
    graph, _ = GraphConverter(auto_cleanup=True).pydantic_list_to_graph([instance])
    types = collections.Counter(d.get("label") for _, d in graph.nodes(data=True))
    labels = collections.Counter(d.get("label") for *_, d in graph.edges(data=True))
    return flags, graph.number_of_nodes(), graph.number_of_edges(), dict(types), dict(labels)


def main() -> None:
    harness, workdir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    workdir.mkdir(parents=True, exist_ok=True)
    for tmpl, root, rundir in ARMS:
        for flip in (False, True):
            flags, nodes, edges, types, labels = convert(harness, workdir, tmpl, root, rundir, flip)
            arm = "flipped" if flip else "control"
            print(f"{tmpl:14s} {arm:8s} flags={flags} nodes={nodes} edges={edges} types={types} edge_labels={labels}")


if __name__ == "__main__":
    main()
