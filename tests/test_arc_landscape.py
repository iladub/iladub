"""The gate on the generated landscape — `docs/superpowers/arc-dependency-landscape.md`.

**This module is the whole reason that file is allowed to exist.** `CLAUDE.md`
§ Documentation governance grants evidence-immutability's second exception to *"a generated
cache — a file written by a script from a committed source and gated by regenerate-and-diff, so
CI fails unless the tracked bytes are exactly what the source produces"* — and states that the
gate is what earns the exception. An ungated derived file committed under `docs/superpowers/` is
a stored label and is forbidden by that same sentence. So: no gate, no file.

**The gate must be a pytest test, and that is MEASURED, not assumed.** CI runs
`./.venv/bin/python -m pytest -q` and nothing else (`.github/workflows/ci.yml:26-27`) — a
Makefile target, a pre-commit hook or a new workflow step would simply never run, and the cache
would drift silently, which is the exact failure the exception is conditioned against.

**Gate classification (CLAUDE.md §8): PROCEDURAL, for the ordinary reason a test is** — it runs
a renderer and compares bytes. It derives nothing: every fact in the file under test comes from
`vocab/queries/arc-*.rq`, and this module re-runs the generator rather than re-deriving any of
them (a second reader of a derived fact is the M9/M9b defect generator, spec §6).

Run: ./.venv/bin/python -m pytest tests/test_arc_landscape.py -q
NEVER `python3` — it carries rdflib 7.1.4 and reports false reds across this repo (Global
Constraint 1).
"""
import sys
from pathlib import Path

import pytest
from rdflib import Graph, Literal, URIRef

REPO = Path(__file__).resolve().parent.parent
LANDSCAPE = REPO / "docs" / "superpowers" / "arc-dependency-landscape.md"
MANIFEST = REPO / "tests" / "arc-manifest.ttl"
QUERIES = REPO / "vocab" / "queries"

REGENERATE = "./.venv/bin/python scripts/arc_depends.py"


def _generator():
    """Import `scripts/arc_depends.py` LAZILY, inside the test body.

    Deliberate, and it is the ordering the RED state of this file depended on: a module-level
    import of a generator that does not exist yet makes every test in this file an ERROR at
    COLLECTION time, and an error is not a failing gate — it is a broken test module. Imported
    here, the gate below reaches its `file missing` assertion first and FAILS, which is what a
    gate is supposed to do when its subject is absent."""
    sys.path.insert(0, str(REPO / "scripts"))
    import arc_depends  # noqa: PLC0415 — see docstring

    return arc_depends


def test_the_tracked_landscape_is_byte_identical_to_a_fresh_regeneration(tmp_path):
    """THE GATE. Regenerate into `tmp_path` from the committed manifest and demand the tracked
    bytes are exactly what the generator produces.

    Two failures, and the message must distinguish them, because the fixes differ:
      - the tracked file is ABSENT — the cache was never committed;
      - the tracked file DIFFERS — the manifest moved, or somebody hand-edited a derived file.
    Both are repaired by running the generator; neither is repaired by editing the markdown."""
    assert LANDSCAPE.is_file(), (
        f"the tracked landscape is missing: {LANDSCAPE.relative_to(REPO)} — "
        f"a generated cache must be committed alongside its gate; regenerate with `{REGENERATE}`"
    )

    out = tmp_path / "arc-dependency-landscape.md"
    assert _generator().main(["--out", str(out)]) == 0
    fresh = out.read_bytes()
    tracked = LANDSCAPE.read_bytes()

    if fresh != tracked:
        # A byte diff on a 100-line table is unreadable; show the first differing LINE.
        f_lines = fresh.decode("utf-8").splitlines()
        t_lines = tracked.decode("utf-8").splitlines()
        for i, (a, b) in enumerate(zip(f_lines, t_lines), start=1):
            if a != b:
                pytest.fail(
                    f"{LANDSCAPE.relative_to(REPO)} has DRIFTED from its source at line {i}:\n"
                    f"  tracked:   {b!r}\n  regenerated: {a!r}\n"
                    f"This file is a generated cache, never hand-edited: run `{REGENERATE}`."
                )
        pytest.fail(
            f"{LANDSCAPE.relative_to(REPO)} has DRIFTED from its source in LENGTH: tracked "
            f"{len(t_lines)} lines, regenerated {len(f_lines)}. Run `{REGENERATE}`."
        )


def test_regeneration_is_deterministic(tmp_path):
    """A gate that its own generator cannot satisfy twice is worse than no gate: it goes red on
    an unrelated PR and gets deleted. Two renders of one manifest must be identical byte for
    byte — no timestamp, no run-dependent ordering, no absolute path."""
    gen = _generator()
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    assert gen.main(["--out", str(a)]) == 0
    assert gen.main(["--out", str(b)]) == 0
    assert a.read_bytes() == b.read_bytes()

    text = a.read_text(encoding="utf-8")
    assert str(REPO) not in text, (
        "an absolute path in the output makes the tracked bytes a fact about one laptop"
    )


def test_the_generator_refuses_a_criterion_that_is_not_a_uriref():
    """THE `arc-depends.rq` TRAP, pinned here for the first time.

    MEASURED (task 5's review, re-measured below): bound as a `Literal`, `arc-depends.rq` does
    NOT error — it matches nothing and returns `[]`, which reads as *"nothing must land before
    this criterion"*. That is the one wrong answer that looks like a right one, and until this
    test existed it was pinned by nothing but a docstring in the query header.

    The guard is producer-side (CLAUDE.md § Producer-side guards): it fails at the call site
    that built the bad term, with that call site on the stack."""
    gen = _generator()
    g = Graph()
    g.parse(MANIFEST, format="turtle")

    # A criterion that HAS a closure, so an empty answer is unambiguous evidence of the trap.
    subject = URIRef("https://w3id.org/iladub/progress#criterion:dec:16")
    assert gen.depends(g, subject), "this arm needs a criterion with a non-empty closure"

    # Arm 1 — the trap is real: the raw query answers "depends on nothing" for a Literal.
    text = (QUERIES / "arc-depends.rq").read_text(encoding="utf-8")
    silent = list(g.query(text, initBindings={"criterion": Literal(str(subject))}))
    assert silent == [], (
        "the trap this test exists for has changed shape: a Literal binding now returns rows"
    )

    # Arm 2 — the generator refuses the term instead of rendering that silence as a fact.
    for bad in (str(subject), Literal(str(subject))):
        with pytest.raises(TypeError):
            gen.depends(g, bad)


# A residue that gates nothing measurable, hand-built — and it is hand-built for a MEASURED
# reason. On `tests/arc-manifest.ttl` as it stands, ALL 15 residues named in `prog:blockedBy`
# gate at least one unmet criterion (measured 2026-08-22: the rendered §3 carries no `?` at
# all), so the live file cannot exercise the absent-row branch. That is a fact about today's
# arc and it will change the first time a blocked criterion is met — which is exactly why the
# renderer's behaviour must be pinned on a fixture instead of on the arc's current shape.
#
# `tab:02` is the arc-reach.rq header's own measured case: MET, carrying a stale blocker, so
# the query gives it no row (choice 1 of that header — a met criterion's blocker is a stale
# edge, not a frontier). Residue ids are R90x so nothing here can be confused with a register
# row, the same convention tests/test_arc_queries.py's fixture uses.
_NO_REACH_FIXTURE = """
@prefix prog: <https://w3id.org/iladub/progress#> .

prog:rung:tab a prog:Rung ; prog:rungKey "tab" .

prog:criterion:tab:01 a prog:Criterion ; prog:ofRung "tab" ; prog:met false ;
    prog:statement "unmet, and something is named as blocking it" ; prog:blockedBy "R901" .
prog:criterion:tab:02 a prog:Criterion ; prog:ofRung "tab" ; prog:met true ;
    prog:statement "met, carrying a stale blocker" ; prog:blockedBy "R902" .
"""


def test_a_residue_that_gates_nothing_measurable_renders_as_unknown_never_zero():
    """`arc-reach.rq` returns NO ROW where a residue gates nothing measurable — it never
    returns `0` (its own header: *"NO ROW MEANS 'GATES NOTHING MEASURABLE', NOT '0'"*, and
    decision 6 of the 2026-08-20 loop: unknown is not zero). Rendering an absent row as `0`
    would be inventing a measurement, so the renderer must print `?`.

    Both branches in one graph, so the test cannot pass by rendering everything as `?`: R901
    gates a real criterion and must come back as a NUMBER; R902's blocker is stale and must
    come back as the absence it is."""
    gen = _generator()
    g = Graph()
    g.parse(data=_NO_REACH_FIXTURE, format="turtle")

    assert gen.residues(g) == ["R901", "R902"]
    rendered = dict(gen.reach_all(g))
    assert rendered["R901"] == "1", "the positive branch: a residue that gates an unmet criterion"
    assert rendered["R902"] == gen.UNKNOWN, (
        "R902 has no arc-reach row and must render as unknown, never as a number"
    )
    assert rendered["R902"] != "0"
    assert "| `R902` | ? |" in gen.render(g)
    assert "| `R902` | 0 |" not in gen.render(g)


def test_the_tracked_landscape_reports_no_reach_as_a_number_it_was_not_given():
    """The same rule, asserted against the file that actually ships: every `unmet criteria
    gated` cell is either a positive count the derivation returned or `?`. A `0` in that column
    could only have been invented by the renderer."""
    gen = _generator()
    g = Graph()
    g.parse(MANIFEST, format="turtle")
    values = {v for _, v in gen.reach_all(g)}
    assert values, "the live manifest must name blockers for this arm to mean anything"
    assert all(v == gen.UNKNOWN or (v.isdigit() and int(v) > 0) for v in values), values
