"""``iladub run`` — drive the ET(K)L pipeline from the command line."""
from __future__ import annotations

import argparse
import sys

from .contract import SemanticDataContract
from .pipeline import ContractViolation, Pipeline


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="iladub", description="Knowledge-first document compiling (ET(K)L).")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run the Extract -> Transform -> validate -> Load pipeline.")
    run.add_argument("--contract", required=True, help="Semantic data contract (.ttl).")
    run.add_argument("--shapes", required=True, help="Target SHACL shapes (.ttl).")
    run.add_argument("--knowledge", required=True, help="Knowledge module (.ttl).")
    run.add_argument("--input", required=True, help="Source document to compile.")
    run.add_argument("--out", help="Where to write the output graph (Turtle). Defaults to stdout.")

    args = parser.parse_args(argv)

    if args.command == "run":
        contract = SemanticDataContract.from_files(args.contract, args.shapes, args.knowledge)
        pipeline = Pipeline(contract)
        try:
            graph, result = pipeline.run(args.input)
        except ContractViolation as exc:
            print("Contract violation — output not loaded:\n", exc, file=sys.stderr)
            return 1
        data = graph.serialize(format="turtle")
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(data)
            print(f"Conforms: {result.conforms}. Wrote {len(graph)} triples to {args.out}.")
        else:
            print(data)
            print(f"# Conforms: {result.conforms}. {len(graph)} triples.", file=sys.stderr)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
