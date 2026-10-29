"""The truth block in the corpus snapshot (ground truth slice one, spec 3.4)."""
import importlib.util
import shutil
from pathlib import Path
from types import SimpleNamespace

from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "corpus_verdict_snapshot", ROOT / "scripts" / "corpus_verdict_snapshot.py")
snap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(snap)

KEYS = {"CORRECT", "WRONG_VALUE", "MISATTACHED", "LOST", "MISSING", "REFUSED",
        "SPURIOUS", "MARKED_LABEL", "UNCLAIMED"}


def _rep():
    return SimpleNamespace(graph=Graph(), pages=(SimpleNamespace(regions=[]),))


def test_no_truth_directory_yields_none(tmp_path):
    assert snap.truth_block("no-such-document", _rep(), tmp_path) is None


def test_one_key_per_table_csv_and_provenance_is_not_a_table(tmp_path):
    d = tmp_path / "tests/ground-truth/doc"
    d.mkdir(parents=True)
    src = ROOT / "tests/ground-truth/fed-h41-2025-01-02"
    for name in ("table-1.csv", "provenance.json"):
        shutil.copy(src / name, d / name)
    block = snap.truth_block("doc", _rep(), tmp_path)
    assert set(block) == {"table-1"}
    assert set(block["table-1"]) == KEYS


def test_refused_texts_come_from_non_asserted_regions_on_listed_pages(tmp_path):
    d = tmp_path / "tests/ground-truth/doc"
    d.mkdir(parents=True)
    src = ROOT / "tests/ground-truth/fed-h41-2025-01-02"
    for name in ("table-1.csv", "provenance.json"):
        shutil.copy(src / name, d / name)
    first = next(l for l in (src / "table-1.csv").read_text().splitlines()[1:])
    label = first.split(",")[0]
    reg = lambda v, t: SimpleNamespace(verdict=v, text=t)
    rep = SimpleNamespace(graph=Graph(), pages=(
        SimpleNamespace(regions=[reg("escalated", label), reg("asserted", "zzz")]),
        SimpleNamespace(regions=[reg("escalated", "other page")])))
    assert snap.refused_texts(rep, [0]) == [label]
    assert snap.truth_block("doc", rep, tmp_path)["table-1"]["REFUSED"] >= 1
