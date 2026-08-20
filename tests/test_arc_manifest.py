"""The arc manifest's membrane (spec 2026-08-20 §4) — nine refusals over prog:.

**Gate classification (CLAUDE.md §8): PROCEDURAL, and here is why it is irreducible.**
Seven of the nine refusals are NOT here: M1, M2 (+M2b), M3, M4, M6, M8 and M9 (+M9b) are
declarative over the manifest graph and live in `tests/arc-shapes.ttl` as SHACL — AXIOM /
constraint, closed world, the membrane. This module owns only the four questions **no SHACL
engine can see, because they are facts about the environment rather than about the graph**:

  * **M5**  — does the file named by `prog:oracleArtifact` exist in the working tree?
  * **M5b** — does the node id named by `prog:oracleTest` COLLECT under this runner?
  * **M5c** — is the interpreter reading this manifest the one it was validated against?
  * **M7**  — is the row named by `prog:blockedBy` present in the residue register,
              a markdown file that is not part of the graph at all?

A closed-world SHACL constraint can only close over triples. The filesystem, a pytest
collection and `sys.version` are none of those, and inventing triples that mirror them would
be deriving-by-absence — the thing CLAUDE.md §8 forbids the membrane to do. So the split is
not a convenience: the graph half stays in SHACL and the environment half is procedural code,
and neither leg may drift into the other's world.

This module derives nothing and computes no fraction. It NEVER writes the manifest (spec §9,
the `cor:` precedent): a criterion is flipped to met by a hand in a reviewed commit or not at
all.

Run: ./.venv/bin/python -m pytest tests/test_arc_manifest.py -q
NEVER `python3` — it carries rdflib 7.1.4 and no pyrudof, and reports false reds (spec §7.2.2).
That interpreter split is exactly what M5c refuses, so under `python3` this module is
*supposed* to go red.
"""
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import rdflib
from pyshacl import validate
from rdflib import RDF, Graph, Namespace

REPO = Path(__file__).resolve().parent.parent
PROG = Namespace("https://w3id.org/iladub/progress#")

MANIFEST = REPO / "tests" / "arc-manifest.ttl"
SHAPES = REPO / "tests" / "arc-shapes.ttl"
REGISTER = REPO / "docs" / "superpowers" / "residues.md"

# `vocab/shapes/iladub-shapes.ttl:39` is the citation form spec §7.2.1 corrected the handoff
# to; the line number is a pointer INTO the artifact, not part of its path.
_LINE_SUFFIX = re.compile(r":\d+$")


# ---------------------------------------------------------------- the graph, read as rows

def validate_manifest(data_path, shapes_path=SHAPES):
    """The SHACL leg: (conforms, report_text) for one manifest against the membrane.

    `advanced=True` is required — six of the constraints are `sh:sparql` — and
    `inference="rdfs"` matches every other membrane in this repo (CLAUDE.md § Serialization).
    """
    ok, _, report = validate(
        Graph().parse(data_path, format="turtle"),
        shacl_graph=Graph().parse(shapes_path, format="turtle"),
        inference="rdfs", advanced=True)
    return ok, report


def oracle_rows(graph):
    """Yield (criterion_iri, met, artifacts, tests) — one row per prog:Criterion.

    `met` is None when the criterion asserts none; M1 refuses that in SHACL, so this leg
    reports it as unmet rather than guessing.
    """
    for c in sorted(graph.subjects(RDF.type, PROG.Criterion), key=str):
        met = graph.value(c, PROG.met)
        yield (str(c),
               None if met is None else met.toPython(),
               tuple(sorted(str(o) for o in graph.objects(c, PROG.oracleArtifact))),
               tuple(sorted(str(o) for o in graph.objects(c, PROG.oracleTest))))


def blocked_rows(graph):
    """Yield (criterion_iri, residue_id) — one row per prog:blockedBy edge."""
    for c in sorted(graph.subjects(RDF.type, PROG.Criterion), key=str):
        for r in sorted(graph.objects(c, PROG.blockedBy), key=str):
            yield (str(c), str(r))


# ------------------------------------------------------- the environment, measured not read

@lru_cache(maxsize=1)
def collectable_node_ids():
    """Every pytest node id this runner can collect — ONE subprocess for the whole set.

    MEASURED 2026-08-20 on this tree:
        $ ./.venv/bin/python -m pytest --collect-only -q
        1252 tests collected in 3.86s      # before this module (0 errors, 0 skips)
        1266 tests collected in 1.16s      # after it; 1.2-3.9 s depending on cache warmth

    That is the entire cost of M5b, once per session, no matter how many criteria name an
    oracle. A `--collect-only` per criterion would pay seconds EACH and be unusable at the
    ~42 criteria this manifest is heading for; membership in a set is the same answer for
    one collection. This is the seam the brief said to measure before writing, and it is
    why the check is a set and not a loop of subprocesses.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO, capture_output=True, text=True)
    ids = frozenset(
        line.strip() for line in proc.stdout.splitlines()
        if "::" in line and line[:1] not in ("", " ", "\t"))
    assert ids, (
        "collection produced no node ids — M5b cannot refuse anything and must not report "
        f"green:\nSTDOUT\n{proc.stdout[-2000:]}\nSTDERR\n{proc.stderr[-2000:]}")
    return ids


def _collects(node_id):
    ids = collectable_node_ids()
    # A parametrized oracle may be cited bare (`…::test_expected_verdict`) while collection
    # only ever reports its parametrized ids (`…[bfs.pdf]`). Both resolve; nothing else does.
    return node_id in ids or any(i.startswith(node_id + "[") for i in ids)


@lru_cache(maxsize=1)
def register_rows():
    """Every residue id the register INDEX carries — `| R95 | open | …`.

    The index is the canonical list (CLAUDE.md § Deferred residues); a row absent from it
    does not exist, whether or not some prose mentions it.
    """
    return frozenset(re.findall(r"^\| *(R\d+) *\|", REGISTER.read_text(encoding="utf-8"),
                                re.M))


def _recorded_version_holds(recorded, running):
    """Dotted-prefix equality: the RECORDED PRECISION IS THE ASSERTION.

    "3.12" against a running 3.12.11 holds; "3.12.0" against it does not. So the manifest
    chooses what it is claiming by how many components it writes down, and no threshold or
    tuned tolerance decides anything (CLAUDE.md §8).
    """
    want = recorded.split(".")
    return running.split(".")[:len(want)] == want


# ------------------------------------------------------------------- the four refusals

def environment_refusals(graph):
    """Every M5 / M5b / M5c / M7 refusal this graph earns, as messages. Empty == admitted."""
    out = []

    for iri, met, artifacts, tests in oracle_rows(graph):
        if met is not True:
            # An UNMET criterion may name a TARGET oracle that does not exist yet
            # (spec §3, §7.5). M5 bites only on an assertion of met-ness.
            continue
        for a in artifacts:
            if not (REPO / _LINE_SUFFIX.sub("", a)).exists():
                out.append(f"M5: {iri} is met on prog:oracleArtifact {a!r}, "
                           f"which does not exist in the working tree")
        for t in tests:
            if not _collects(t):
                out.append(f"M5b: {iri} is met on prog:oracleTest {t!r}, "
                           f"which does not collect under {sys.executable}")

    for manifest in sorted(graph.subjects(RDF.type, PROG.Manifest), key=str):
        for prop, running, what in (
                (PROG.pythonVersion, sys.version.split()[0], "Python"),
                (PROG.rdflibVersion, rdflib.__version__, "rdflib")):
            recorded = graph.value(manifest, prop)
            if recorded is None:
                continue          # SHACL's ManifestShape owns the missing-field refusal
            if not _recorded_version_holds(str(recorded), running):
                out.append(
                    f"M5c: validated against {what} {str(recorded)!r}, read under "
                    f"{running!r} — re-validate under the recorded runner, or pin the new "
                    f"one in a reviewed commit (the cor:sha256 precedent)")

    known = register_rows()
    for iri, residue in blocked_rows(graph):
        if residue not in known:
            out.append(f"M7: {iri} is prog:blockedBy {residue!r}, which is not a row in "
                       f"{REGISTER.relative_to(REPO)}")
    return out


# ------------------------------------------------------------------------------ helpers

_REFUSAL = re.compile(r"\bM\d+b?c?:")


def _refused_by_shacl(fixture, refusal):
    """Assert the SHACL membrane refuses `fixture`, and refuses it for exactly one reason.

    The exact-set assertion is the point: a fixture that trips three constraints proves
    nothing about the one it was written for.
    """
    ok, report = validate_manifest(REPO / "tests" / fixture)
    assert not ok, f"the membrane admitted {fixture}, which it must refuse:\n{report}"
    assert set(_REFUSAL.findall(report)) == {refusal + ":"}, (
        f"{fixture} must be refused by {refusal} alone:\n{report}")


def _refused_by_environment(fixture, refusal):
    """Assert the environment leg refuses `fixture` — and that SHACL does NOT.

    SHACL-cleanliness is half the assertion: it proves the refusal came from the filesystem,
    the collection or the interpreter, and could not have come from the graph. The other half
    is exact-set, as on the SHACL side — a fixture that earns three refusals is evidence
    about none of them.
    """
    ok, report = validate_manifest(REPO / "tests" / fixture)
    assert ok, f"{fixture} must be SHACL-clean so that only the {refusal} leg can refuse " \
               f"it; the graph membrane already objects:\n{report}"
    reasons = environment_refusals(Graph().parse(REPO / "tests" / fixture, format="turtle"))
    assert {r.split(":", 1)[0] for r in reasons} == {refusal}, (
        f"{fixture} must be refused by {refusal} alone: {reasons}")


# --------------------------------------------------------------- M1–M4, M6, M8, M9: SHACL

def test_m1_a_criterion_without_its_required_fields_is_refused():
    """A criterion with no prog:declaredOn cannot participate in §3.2 at all: there is no
    date to compare prog:metOn against, so neither M3 nor M4 can ever see it."""
    _refused_by_shacl("arc-m1-missing-field-leak.ttl", "M1")


def test_m2_a_met_criterion_without_a_date_is_refused():
    """A claim with no date is not auditable — nobody can ask what changed when."""
    _refused_by_shacl("arc-m2-met-without-date-leak.ttl", "M2")


def test_m2b_an_unmet_criterion_carrying_a_met_date_is_refused():
    """The inverse leak: a prog:metOn left behind when the criterion was un-met. The fill
    can go down (decision 6), and when it does the date must go with it."""
    _refused_by_shacl("arc-m2b-unmet-with-met-date-leak.ttl", "M2b")


def test_m3_met_before_declared_is_refused():
    """Met before it was defined. §3.2's independence comes entirely from the dates."""
    _refused_by_shacl("arc-m3-met-before-declared-leak.ttl", "M3")


def test_m4_same_day_grandfathering_must_be_labelled():
    """metOn == declaredOn is grandfathering: the criterion was written against evidence
    that already existed, so its fraction is an adjudication and not an independent
    measurement. §3.2 requires that to be LABELLED, never hidden."""
    _refused_by_shacl("arc-m4-unlabelled-grandfathering-leak.ttl", "M4")


def test_m6_a_sixth_rung_is_refused():
    """The five names are settled (decision 8). A sixth rung is a decision the maintainer
    makes, not an edit a loop slips into a manifest."""
    _refused_by_shacl("arc-m6-sixth-rung-leak.ttl", "M6")


def test_m8_a_met_criterion_may_not_be_blocked():
    """A met criterion is not blocked. This catches the stalest kind of row — the work
    landed and the dependency edge stayed up, so the frontier query keeps naming it."""
    _refused_by_shacl("arc-m8-met-and-blocked-leak.ttl", "M8")


def test_m9_a_blank_node_criterion_is_refused():
    """scripts/cockpit.py must read the manifest WITHOUT rdflib (cockpit.py:34-38). A regex
    read of arbitrary Turtle is unsafe; a regex read of a file where every criterion is a
    top-level IRI subject is safe, and M9 is what buys that."""
    _refused_by_shacl("arc-m9-blank-node-criterion-leak.ttl", "M9")


def test_m9b_an_iri_that_disagrees_with_its_rung_is_refused():
    """The IRI says `tab`, prog:ofRung says `dec`. The two encodings must agree, or the fast
    reader and rdflib disagree about which rung the criterion counts for."""
    _refused_by_shacl("arc-m9b-iri-rung-disagreement-leak.ttl", "M9b")


# ------------------------------------------------- M5, M5b, M5c, M7: the environment leg

def test_m5_a_met_criterion_pointing_at_an_absent_artifact_is_refused():
    """`battery-run-final.log` is not a hypothetical: R43, R44 and R45 all rest their
    measurement on it, and it is absent from the repo AND from git history
    (`git log --all -- '*battery-run-final*'` -> empty, spec §7.4)."""
    _refused_by_environment("arc-m5-absent-artifact-leak.ttl", "M5")


def test_m5b_a_met_criterion_whose_oracle_test_does_not_collect_is_refused():
    """R74's closure names `test_cbh_p0_known_defects_are_pinned_not_hidden`; no such
    function exists (the real pin is `::test_cbh_p0_table_b_leak_is_pinned_not_hidden`).

    Cost: ONE `--collect-only` for the whole manifest — measured 1266 tests in 1.16s on
    2026-08-20. See collectable_node_ids() for why it is a set and not a subprocess per row.
    """
    _refused_by_environment("arc-m5b-uncollectable-test-leak.ttl", "M5b")


def test_m5c_a_manifest_validated_under_another_interpreter_is_refused():
    """Spec §7.2.2: green is relative to a runner. Under the system python3 (rdflib 7.1.4,
    no pyrudof) the corpus battery reports false reds, and a gauge inheriting that would
    silently un-meet criteria for an ENVIRONMENT reason rather than an evidential one."""
    _refused_by_environment("arc-m5c-foreign-interpreter-leak.ttl", "M5c")


def test_m7_a_blocking_edge_to_a_nonexistent_residue_is_refused():
    """A dangling edge is worse than no edge: it reads as strategy and points at nothing.
    R999 is not a row in the register index."""
    _refused_by_environment("arc-m7-dangling-residue-leak.ttl", "M7")


# ------------------------------------------------------------------------ the one positive

def test_a_rung_with_no_criteria_conforms_and_is_not_a_refusal():
    """The seed state, and decision 6 doing its work: UNKNOWN IS NOT ZERO.

    Five rungs, zero criteria. Every rung renders `?` — never an empty bar, never 0/0. This
    is the one test in the file that asserts conformance, and it asserts it of the LIVE
    tracked manifest against BOTH legs of the membrane, not of a fixture.
    """
    ok, report = validate_manifest(MANIFEST)
    assert ok, report

    g = Graph().parse(MANIFEST, format="turtle")
    assert environment_refusals(g) == []

    assert len(set(g.subjects(RDF.type, PROG.Manifest))) == 1
    assert {str(g.value(r, PROG.rungKey)) for r in g.subjects(RDF.type, PROG.Rung)} == {
        "etkl", "dec", "holon", "tab", "substrate"}
    assert list(oracle_rows(g)) == [], "the seed manifest declares no criteria yet"
