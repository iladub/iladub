"""Unit tests for the corpus reach instrument (scripts/reach_probe.py, R158).

These run against a FIXTURE cache, never a PDF: `run` is minutes per document and
is exercised by the loop that produces the committed figures, not by CI. What is
pinned here is the part that reads the cache and can be silently wrong — the reach
arithmetic, the two-modules-one-name case, and the never-called path.

The two-modules case is not hypothetical: the prototype of this instrument keyed a
function to the file its diff hunk header named, resolved `_emit_candidate` to the
wrong module, and reported 0/7 for a function called 1850 times. A lookup that
misses reads exactly like a function nothing reaches, which is the one answer this
instrument exists to give.
"""
import importlib.util
import sys
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "reach_probe", REPO / "scripts" / "reach_probe.py")
reach_probe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reach_probe)


@pytest.fixture
def cache(tmp_path):
    """Two documents. `walked` is called by both, `limb` by one, `twin` is defined
    in two different modules and called from one of them only."""
    (tmp_path / "a.json").write_text(json.dumps({
        "file": "x/a.pdf", "short": "gstem", "legs": ["compile"], "wall": 1.0,
        "score": 0.9, "calls": {"src/iladub/etkl/geometry.py:walked": 14,
                                "src/iladub/ground.py:twin": 1850}}))
    (tmp_path / "b.json").write_text(json.dumps({
        "file": "x/b.pdf", "short": "who", "legs": ["compile", "grounding"],
        "wall": 2.0, "score": 0.5,
        "calls": {"src/iladub/etkl/geometry.py:walked": 28,
                  "src/iladub/etkl/matrix.py:limb": 3,
                  "src/iladub/splitkey.py:twin": 0}}))
    return tmp_path


def test_reach_counts_documents_not_calls(cache, capsys):
    reach_probe.report(cache, ["walked", "limb"])
    out = capsys.readouterr().out
    assert "2/2" in out and "14" in out and "28" in out
    limb = [l for l in out.splitlines() if "limb" in l][0]
    assert limb.endswith("1/2"), limb


def test_a_name_defined_in_two_modules_reports_both(cache, capsys):
    """The prototype's defect: one hit silently stood for every module."""
    reach_probe.report(cache, ["twin"])
    lines = [l for l in capsys.readouterr().out.splitlines() if "twin" in l]
    assert len(lines) == 2, lines
    assert any("ground.py" in l and "1850" in l and l.endswith("1/2") for l in lines)
    assert any("splitkey.py" in l and l.endswith("0/2") for l in lines)


def test_a_never_called_name_is_reported_as_such_not_omitted(cache, capsys):
    reach_probe.report(cache, ["absent"])
    out = capsys.readouterr().out
    assert "NEVER CALLED" in out and "0/2" in out


def test_corpus_wide_distribution_counts_each_function_once(cache, capsys):
    reach_probe.report(cache, [])
    out = capsys.readouterr().out
    # 4 distinct keys across both documents; walked in 2, twin(ground) in 1,
    # limb in 1, twin(splitkey) recorded 0 so it is reached by 0.
    assert "over 4 src/iladub functions called at least once" in out
    assert "reached by 0/2 documents:    1" in out
    assert "reached by 1/2 documents:    2" in out
    assert "reached by 2/2 documents:    1" in out


def test_run_gives_every_document_a_fresh_interpreter(tmp_path, monkeypatch):
    """MEASURED defect, not a hypothetical: the first version of the script compiled
    all seven documents in one process and reported `_build_membrane` — which is
    lru_cache'd — at 1/7 instead of 7/7, because documents 2..7 were served the cache
    and cProfile recorded no call for them. Every memoized or run-once function fails
    the same way, silently and in the understating direction. A shared process is the
    defect; one per document is the fix."""
    seen = []

    def fake_run(argv, **kw):
        seen.append(argv)
        class R: returncode = 0
        return R()

    monkeypatch.setattr(reach_probe.subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", ["reach_probe.py", "run", "--out", str(tmp_path)])
    reach_probe.main()

    docs = [e["file"] for e in reach_probe.manifest()]
    assert len(seen) == len(docs), f"{len(seen)} subprocesses for {len(docs)} documents"
    assert {a[a.index("--doc") + 1] for a in seen} == set(docs)
    assert all("_one" in a for a in seen)
