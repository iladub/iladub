"""CLI: python -m scripts.synthetic_contracts {fetch,fills,build}. Licence: Apache-2.0.

Justified PROCEDURAL (CLAUDE.md § 8): argument dispatch only. `fetch` is wired; `fills` and
`build` arrive in later tasks."""
import argparse

from scripts.synthetic_contracts import manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="scripts.synthetic_contracts")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="download and sha256-verify the four templates")
    args = ap.parse_args(argv)
    if args.cmd == "fetch":
        return manifest.fetch()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
