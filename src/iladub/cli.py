"""``iladub`` command-line interface."""
from __future__ import annotations

import argparse

from .m4 import compile_offer


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="iladub", description="Knowledge-first document compiling (ET(K)L).")
    sub = parser.add_subparsers(dest="command", required=True)

    m4 = sub.add_parser("m4", help="Compile a transplant organ offer into an M4 decision (live; needs ANTHROPIC_API_KEY).")
    m4.add_argument("doc", help="Path to the organ-offer document (.txt/.pdf).")

    args = parser.parse_args(argv)

    if args.command == "m4":
        result = compile_offer(args.doc)
        n_props = len(set(result.extraction_graph.propositions.subjects(None, None)))
        print(f"Recommendation: {result.decision.recommendation} "
              f"(rejected: {result.decision.rejected_option})")
        print(f"Reason: {result.decision.reason}")
        print(f"Context conforms: {result.validation.conforms}")
        print(f"Quarantined propositions: {n_props}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
