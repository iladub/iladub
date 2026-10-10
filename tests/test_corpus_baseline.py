"""R305: the committed corpus baseline is fresh for the tree it sits in.

`tests/corpus-baseline/` is a generated cache of `corpus_verdict_snapshot.snapshot()` over the
eleven documents. CI has no corpus (`corpus/` and `held-out/` are gitignored), so it cannot
regenerate the baseline. What it can prove is that the baseline was regenerated from THESE inputs:
the fingerprint recorded in `inputs.json` must equal the fingerprint of the tree under test.
Byte-equality with what the inputs produce is `corpus_baseline.py verify`'s job, run locally
(spec `docs/superpowers/specs/2026-10-10-r305-corpus-baseline-design.md` § 2.5).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASELINE = REPO / "tests" / "corpus-baseline"
sys.path.insert(0, str(REPO / "scripts"))
import corpus_baseline  # noqa: E402


def test_the_baseline_was_regenerated_from_this_tree():
    recorded = json.loads((BASELINE / "inputs.json").read_text())["fingerprint"]
    assert corpus_baseline.fingerprint(REPO) == recorded, (
        "an input of the compile changed since tests/corpus-baseline/ was regenerated; run "
        "`PYTHONPATH=src .venv/bin/python scripts/corpus_baseline.py regenerate` and commit "
        "the result (its git diff is this change's blast radius)")


def test_the_baseline_holds_exactly_the_listed_documents():
    stems = {Path(p).stem for p in corpus_baseline.DOCUMENTS}
    assert len(stems) == len(corpus_baseline.DOCUMENTS) == 11
    assert {p.stem for p in BASELINE.glob("*.json")} - {"inputs"} == stems
    recorded = json.loads((BASELINE / "inputs.json").read_text())["documents"]
    assert sorted(d["path"] for d in recorded) == sorted(corpus_baseline.DOCUMENTS)


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_the_fingerprint_moves_with_every_input_class_and_only_with_inputs(tmp_path):
    files = {
        "src/iladub/etkl/m.py": "x = 1\n",
        "vocab/queries/q.rq": "SELECT * {}\n",
        "readings/boxhead/r.json": "{}\n",
        "pyproject.toml": "[project]\n",
        "scripts/corpus_baseline.py": "# s\n",
        "scripts/corpus_verdict_snapshot.py": "# s\n",
        "tests/t.py": "# not an input\n",
        "docs/d.md": "not an input\n",
    }
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    base = corpus_baseline.fingerprint(tmp_path)

    for rel, text in files.items():
        (tmp_path / rel).write_text(text + "#\n")
        moved = corpus_baseline.fingerprint(tmp_path) != base
        (tmp_path / rel).write_text(text)
        is_input = not rel.startswith(("tests/", "docs/"))
        assert moved == is_input, f"{rel}: fingerprint moved={moved}, is an input={is_input}"
    assert corpus_baseline.fingerprint(tmp_path) == base
