"""Synthetic contract set Task 7: the leak guard (spec § 2 A3, § 4.5). CI-runnable.

If a reader can import the generator or read the truth, the proof is void. So no file under `src/`,
`readings/`, `scripts/` outside `scripts/synthetic_contracts/`, or `tests/` other than this set's own
`tests/test_synthetic_contracts_*.py` may contain `synthetic_contracts` (the generator's package) or
`synthetic-contracts/truth` (the truth directory). Exact substring match over every tracked-or-not
file in those trees: decidable, no tolerance.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NEEDLES = ("synthetic_contracts", "synthetic-contracts/truth")
ROOTS = ("src", "scripts", "readings", "tests")


def _allowed(rel: Path) -> bool:
    parts = rel.parts
    if parts[:2] == ("scripts", "synthetic_contracts"):
        return True
    return (len(parts) == 2 and parts[0] == "tests"
            and parts[1].startswith("test_synthetic_contracts_") and parts[1].endswith(".py"))


def _scanned():
    for root in ROOTS:
        for p in (REPO / root).rglob("*"):
            if not p.is_file() or "__pycache__" in p.parts or p.suffix == ".pyc":
                continue
            rel = p.relative_to(REPO)
            if not _allowed(rel):
                yield rel, p


def test_leak_guard_scans_something():
    rels = [r for r, _ in _scanned()]
    assert any(r.parts[0] == "src" for r in rels) and any(r.parts[0] == "tests" for r in rels)


def test_no_reader_sees_truth():
    leaks = []
    for rel, p in _scanned():
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        leaks += [f"{rel}: {n}" for n in NEEDLES if n in text]
    assert not leaks, leaks
