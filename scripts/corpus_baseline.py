"""The committed corpus baseline (R305): one regeneration plus a `git diff` is a blast radius.

`tests/corpus-baseline/` holds `corpus_verdict_snapshot.snapshot()` for each of the eleven
documents below, plus `inputs.json`, which records the fingerprint of the tree they were generated
from. A loop that changes the reading runs `regenerate` once, and `git diff --
tests/corpus-baseline/` is what moved. The "before" is the committed file, so `main` is never
re-measured. Spec: `docs/superpowers/specs/2026-10-10-r305-corpus-baseline-design.md`.

    PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate
    PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py check     # CI-safe, no corpus
    PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py verify    # regenerate-and-diff

`check` proves the baseline was regenerated from these inputs. It cannot prove the bytes are what
these inputs produce, because the corpus is third-party and never reaches CI. `verify` proves
that, locally (spec § 2.5).

Gate classification (CLAUDE.md § 8): PROCEDURAL. It lists files, hashes bytes, runs one
subprocess per document and compares files. It decides nothing about any document and carries no
constant or tolerance. Irreducible to AXIOM because its subject is files and processes, not an RDF
evidence graph, and irreducible to NEURAL because nothing in it is underdetermined.
"""
from __future__ import annotations

import filecmp
import hashlib
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile
from importlib import metadata

REPO = pathlib.Path(__file__).resolve().parents[1]
BASELINE = REPO / "tests" / "corpus-baseline"

# By path, not by rglob, so a document that failed to fetch fails loudly instead of shrinking the
# baseline. Changing this list changes this file, and so the fingerprint.
DOCUMENTS = (
    "corpus/ag-trade/cbh-stem-2026-08-03.pdf",
    "corpus/ag-trade/graincorp-capacity-2026-08-04.pdf",
    "corpus/ag-trade/graincorp-stem-2026-07-31.pdf",
    "corpus/financial/apple-fy2026q3-statements.pdf",
    "corpus/gov-stats/bfs-population-bilan-2023.pdf",
    "corpus/gov-stats/ons-index-of-services-2026-02.pdf",
    "corpus/health/who-wfa-boys-zscore-0-5.pdf",
    "held-out/arxiv-1706.03762v7.pdf",
    "held-out/caltrain-weekend-timetable.pdf",
    "held-out/fed-h41-2025-01-02.pdf",
    "held-out/who-covid-sitrep-41.pdf",
)

# Everything a compile reads from the repo (spec § 1), plus the two scripts that shape the bytes.
INPUTS = ("src", "vocab", "readings", "pyproject.toml",
          "scripts/corpus_baseline.py", "scripts/corpus_verdict_snapshot.py")

# Either one makes a compile call a live model, so it is neither offline nor reproducible.
LIVE_ENV = ("BAML_LIVE", "ILADUB_RECORD_READINGS")

# Recorded beside the fingerprint for a human to compare; no gate reads it (spec § 6).
DISTRIBUTIONS = ("rdflib", "pyshacl", "pyyaml", "pdfplumber", "pdfminer.six", "numpy")


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(root: pathlib.Path) -> str:
    """SHA-256 over the tracked input paths, sorted, each with the SHA-256 of its bytes on disk."""
    listed = subprocess.run(["git", "ls-files", "-z", "--", *INPUTS], cwd=root, check=True,
                            capture_output=True).stdout.decode("utf-8").split("\0")
    h = hashlib.sha256()
    for rel in sorted(p for p in listed if p):
        h.update(rel.encode("utf-8") + b"\0" + _sha256(root / rel).encode("ascii") + b"\n")
    return h.hexdigest()


def _refusals() -> list[str]:
    out = [f"{v} is set: a compile would not be offline" for v in LIVE_ENV if os.environ.get(v)]
    out += [f"missing on disk: {p}" for p in DOCUMENTS if not (REPO / p).is_file()]
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", *INPUTS],
                               cwd=REPO, check=True, capture_output=True, text=True).stdout.split()
    out += [f"untracked input (git add it, or the fingerprint cannot see it): {p}" for p in untracked]
    return out


def _environment() -> dict:
    versions = {}
    for d in DISTRIBUTIONS:
        try:
            versions[d] = metadata.version(d)
        except metadata.PackageNotFoundError:
            versions[d] = None
    return {"python": platform.python_version(), "distributions": versions}


def _generate(out: pathlib.Path) -> None:
    """One subprocess per document, serially: no state crosses documents, and order is irrelevant."""
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    for rel in DOCUMENTS:
        subprocess.run([sys.executable, str(REPO / "scripts" / "corpus_verdict_snapshot.py"),
                        str(out), "--pdf", rel], cwd=REPO, env=env, check=True)
    inputs = {
        "fingerprint": fingerprint(REPO),
        "documents": [{"path": rel, "sha256": _sha256(REPO / rel)} for rel in DOCUMENTS],
        "environment": _environment(),
    }
    (out / "inputs.json").write_text(json.dumps(inputs, indent=2, sort_keys=True) + "\n")


def regenerate() -> int:
    refused = _refusals()
    if refused:
        print("refused, nothing written:\n  " + "\n  ".join(refused), file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        _generate(pathlib.Path(tmp))
        # Only now, with every document done, is the committed baseline replaced.
        shutil.rmtree(BASELINE, ignore_errors=True)
        shutil.copytree(tmp, BASELINE)
    return 0


def check() -> int:
    recorded = json.loads((BASELINE / "inputs.json").read_text())["fingerprint"]
    if fingerprint(REPO) != recorded:
        print("stale: an input changed since tests/corpus-baseline/ was regenerated; run "
              "`PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate`",
              file=sys.stderr)
        return 1
    print("fresh")
    return 0


def verify() -> int:
    refused = _refusals()
    if refused:
        print("refused:\n  " + "\n  ".join(refused), file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        _generate(pathlib.Path(tmp))
        names = sorted({p.name for p in BASELINE.iterdir()} | {p.name for p in pathlib.Path(tmp).iterdir()})
        differ = [n for n in names if not (BASELINE / n).is_file() or not (pathlib.Path(tmp) / n).is_file()
                  or not filecmp.cmp(BASELINE / n, pathlib.Path(tmp) / n, shallow=False)]
    for n in differ:
        print(f"differs: {n}", file=sys.stderr)
    print(f"{len(names) - len(differ)} of {len(names)} files byte-equal")
    return 1 if differ else 0


if __name__ == "__main__":
    commands = {"regenerate": regenerate, "check": check, "verify": verify}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        raise SystemExit(f"usage: corpus_baseline.py {{{'|'.join(commands)}}}")
    raise SystemExit(commands[sys.argv[1]]())
