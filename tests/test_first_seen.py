"""`scripts/first_seen.py` — the R198 dating primitive.

WHAT THESE PIN. Not today's dates: a new reading appended to the register changes the
table and must not break this file. What is pinned is the instrument's MEANING —
every quotable reading is recoverable, the exclusion is read from the register rather
than written here, a shallow clone fails loudly instead of reporting "unrecoverable"
for everything, and a shared literal is refused rather than silently attributed.

The one numeric assertion is the spec's falsifying oracle (§6), and it is an
INVARIANT, not a baseline: a value cannot have been read before it existed, so
`readAt` must never pre-date first observation. If that ever fails, either a register
row carries a hand-written wrong date or the pickaxe matched noise — which is exactly
how `graincorp-capacity 1.0` fails, at 81 days, and why it is excluded (spec §2).
"""
import subprocess
from pathlib import Path

import pytest
from rdflib import Graph

from scripts.first_seen import (
    COR,
    REGISTER,
    first_seen,
    quotable_readings,
    require_full_history,
)

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def resolved() -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    readings = quotable_readings(REPO)
    return readings, first_seen(REPO, list(readings))


def test_every_quotable_reading_is_recoverable(resolved):
    """R198's blocking question, asked by the predecessor handoff's 5a BEFORE any
    design: is first observation recoverable for the readings already registered, or
    only for readings taken from here on? If only the latter, the repair could never
    validate itself against the occurrences that motivated it.

    It is recoverable. Anything unrecoverable here is a finding, not a tolerance."""
    readings, seen = resolved
    missing = sorted(v for v in readings if v not in seen)
    assert not missing, (
        "no commit on main adds these registered values, so first observation is "
        f"unrecoverable for them: {missing}"
    )


def _register(tmp_path: Path, *rows: str) -> Path:
    manifest = tmp_path / REGISTER
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "@prefix cor: <https://w3id.org/iladub/corpus#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n" + "".join(rows)
    )
    return manifest


def test_clearing_the_register_flag_puts_a_reading_back_in_scope(tmp_path):
    """The exclusion must be READ from the register, never written in the module.

    Pinned behaviourally and not by inspection, because today the only flagged value
    and the only value worth skipping are the same one (`1.0`) — so a hardcoded
    `if value == "1.0"` would satisfy any assertion made against the real register,
    and the test would pass with its own subject deleted (CLAUDE.md § Plan authoring
    discipline, defect 5). Toggling the flag on a synthetic register cannot.

    A second, separately-maintained skip list is the R188 failure: an exemption is a
    coverage loss dressed as a fix."""
    flagged = _register(
        tmp_path,
        '<urn:a> cor:reading [ cor:value "1.0"^^xsd:decimal ;\n'
        '    cor:readAt "2026-09-09"^^xsd:date ; cor:notQuotable true ] .\n',
    )
    assert quotable_readings(tmp_path) == {}

    flagged.write_text(flagged.read_text().replace(" ; cor:notQuotable true", ""))
    assert quotable_readings(tmp_path) == {"1.0": "a"}, (
        "clearing cor:notQuotable did not put the reading back in scope, so the "
        "exclusion is hardcoded here rather than read from the register"
    )


def test_the_register_flags_what_the_derivation_drops(resolved):
    """And, against the REAL register: the two sets agree exactly — the derivation
    drops every flagged reading and no other."""
    readings, _ = resolved
    reg = Graph().parse(REPO / REGISTER)
    every = {str(reg.value(n, COR.value)) for _, n in reg.subject_objects(COR.reading)}
    flagged = {
        str(reg.value(n, COR.value))
        for _, n in reg.subject_objects(COR.reading)
        if reg.value(n, COR.notQuotable)
    }
    assert flagged, "the register flags nothing notQuotable — this test proves nothing"
    assert set(readings) == every - flagged


def test_readat_never_predates_first_observation(resolved):
    """SPEC §6, the falsifying oracle, in its committed form.

    A negative lag says the value was in the tree before the register claims anyone
    read it, which means the match is coincidental rather than provenantial — and a
    coincidental match would make the whole R198 measurement unsound. Positive lags
    are the defect R198 names and are expected; ZERO is the healthy case."""
    readings, seen = resolved
    reg = Graph().parse(REPO / REGISTER)
    read_at = {
        str(reg.value(n, COR.value)): min(str(d) for d in reg.objects(n, COR.readAt))
        for _, n in reg.subject_objects(COR.reading)
    }
    early = {v: (read_at[v], seen[v][1]) for v in readings if read_at[v] < seen[v][1]}
    assert not early, (
        "a reading is registered as read BEFORE its value first appears on main, so "
        f"the pickaxe is matching noise rather than provenance: {early}"
    )


def test_a_shallow_clone_fails_loudly(tmp_path, monkeypatch):
    """On a shallow clone the pickaxe has no history to walk and returns nothing, so
    EVERY reading would read as unrecoverable — a false negative indistinguishable
    from a real finding. Same guard and same reasoning as
    `tests/docgov_extract.py::_require_full_history`."""
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="true\n", stderr=""),
    )
    with pytest.raises(RuntimeError, match="shallow"):
        require_full_history(tmp_path)


def test_the_shallow_guard_is_WIRED_into_the_derivation(tmp_path, monkeypatch):
    """And that the guard is actually CALLED, not merely present.

    Falsification found this gap: deleting `require_full_history(repo)` from
    `first_seen` left the test above green, because it exercises the guard directly.
    A guard nothing calls pins nothing (CLAUDE.md § Plan authoring discipline rule 4)."""
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="true\n", stderr=""),
    )
    with pytest.raises(RuntimeError, match="shallow"):
        first_seen(tmp_path, ["0.5"])


def test_a_literal_registered_by_two_documents_is_refused(tmp_path):
    """The register's one-node-per-distinct-value rule is scoped per DOCUMENT, so two
    documents may register the same value. Git cannot tell those apart; attributing
    the commit to whichever parsed first would be a silent wrong answer."""
    _register(
        tmp_path,
        '<urn:a> cor:reading [ cor:value "0.5"^^xsd:decimal ;\n'
        '    cor:readAt "2026-09-09"^^xsd:date ] .\n',
        '<urn:b> cor:reading [ cor:value "0.5"^^xsd:decimal ;\n'
        '    cor:readAt "2026-09-09"^^xsd:date ] .\n',
    )
    with pytest.raises(ValueError, match="two documents"):
        quotable_readings(tmp_path)
