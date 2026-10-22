"""The ground-truth floor: the committed corpus snapshot's `truth` block, per table.

Spec 2026-10-22-ground-truth-slice-one § 3.4, § 5 test 3. Lowering a floor needs a dated
note in floor.json; that rule is enforced by review, not here.
"""
import csv
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
GT = ROOT / "tests" / "ground-truth"
BASELINE = ROOT / "tests" / "corpus-baseline"
SIX = ("CORRECT", "WRONG_VALUE", "MISATTACHED", "LOST", "MISSING", "REFUSED")
FLOORS = sorted(GT.glob("*/floor.json"))


def _csv_rows(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return sum(1 for _ in csv.DictReader(fh))


def test_at_least_one_document_has_a_floor():
    assert FLOORS


@pytest.mark.parametrize("floor_path", FLOORS, ids=lambda p: p.parent.name)
def test_truth_block_meets_floor_and_accounts_for_every_csv_row(floor_path):
    stem = floor_path.parent.name
    floor = json.loads(floor_path.read_text(encoding="utf-8"))
    snap = json.loads((BASELINE / f"{stem}.json").read_text(encoding="utf-8"))
    assert "truth" in snap, f"{stem}: committed baseline has no `truth` block"
    truth = snap["truth"]
    tables = {k: v for k, v in floor.items() if k != "notes"}
    assert tables, f"{stem}: floor.json declares no table"
    for table, minimum in tables.items():
        assert table in truth, f"{stem}: truth block has no {table}"
        counts = truth[table]
        assert counts["CORRECT"] >= minimum["CORRECT"], (
            f"{stem}/{table}: CORRECT {counts['CORRECT']} < floor {minimum['CORRECT']}")
        rows = _csv_rows(GT / stem / f"{table}.csv")
        assert sum(counts[k] for k in SIX) == rows, (
            f"{stem}/{table}: six outcomes sum to {sum(counts[k] for k in SIX)}, CSV has {rows}")
