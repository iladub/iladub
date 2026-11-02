"""CLI: python -m scripts.synthetic_contracts {fetch,fills,build}. Licence: Apache-2.0.

Justified PROCEDURAL (CLAUDE.md § 8): argument dispatch only. A build refusal (a template absent or
of another edition, Word failing or timing out, the Word flavour refusing its layout) is printed as
one line on stderr with exit 1, not a traceback."""
import argparse
import subprocess
import sys

from scripts.synthetic_contracts import manifest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="scripts.synthetic_contracts")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="download and sha256-verify the four templates")
    sub.add_parser("fills", help="write the committed fill specs that are absent")
    sub.add_parser("build", help="verify the templates, build every PDF and truth record")
    args = ap.parse_args(argv)
    if args.cmd == "fetch":
        return manifest.fetch()
    if args.cmd == "fills":
        from scripts.synthetic_contracts import fills

        paths = fills.write_all(manifest.load_manifest())
        print(f"wrote {len(paths)} fill spec(s)")
        return 0
    if args.cmd == "build":
        from scripts.synthetic_contracts import build
        from scripts.synthetic_contracts.flavours.wordexport import BuildRefused
        from scripts.synthetic_contracts.word import WordFailed

        try:
            paths = build.build()
        except (manifest.TemplateMissing, manifest.TemplateMismatch, WordFailed,
                subprocess.TimeoutExpired, BuildRefused) as e:
            first = (str(e).splitlines() or [type(e).__name__])[0]
            print(f"build refused: {type(e).__name__}: {first}", file=sys.stderr)
            return 1
        print(f"built {len(paths)} PDF(s) under {build.OUT_DIR}, truth under {build.TRUTH_DIR}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
