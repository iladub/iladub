"""The arc manifest's membrane (spec 2026-08-20 §4, extended 2026-08-22 §5) — eighteen
refusals over prog:, counted as `tests/arc-shapes.ttl`'s own header counts them (M2/M2b are
one, M9/M9b are one, M5/M5b/M5c are one).

**Gate classification (CLAUDE.md §8): PROCEDURAL, and here is why it is irreducible.**
Fifteen of the eighteen refusals are NOT here. Fourteen — M1, M2 (+M2b), M3, M4, M6, M8,
M9 (+M9b) over a single criterion, and **M12–M18 over the DEPENDENCY GRAPH between criteria**
(added 2026-08-22) — are declarative over the manifest graph and live in
`tests/arc-shapes.ttl` as SHACL — AXIOM / constraint, closed world, the membrane. The
fifteenth, **M19**, is not here either and could not be: it is A5's two-sided ablation, which
creates a `git worktree`, deletes a file inside it and reads a pytest exit code, so it lives
in `tests/test_arc_ablation.py` — split off by COST, not by concern (see that module's
docstring). This module owns only the five questions **no SHACL engine can see, because they
are facts about the environment rather than about the graph**:

  * **M5**  — does the file named by `prog:oracleArtifact` exist in the working tree?
  * **M5b** — does the node id named by `prog:oracleTest` COLLECT under this runner?
  * **M5c** — is the interpreter reading this manifest the one it was validated against?
  * **M7**  — is the row named by `prog:blockedBy` present in the residue register,
              a markdown file that is not part of the graph at all?
  * **M10** — does the `<path>:<line>` named by `prog:source` RESOLVE: does the path exist,
              and is the line in range? (R105, closed 2026-08-21 by Ruling 18.)

A closed-world SHACL constraint can only close over triples. The filesystem, a pytest
collection and `sys.version` are none of those, and inventing triples that mirror them would
be deriving-by-absence — the thing CLAUDE.md §8 forbids the membrane to do. So the split is
not a convenience: the graph half stays in SHACL and the environment half is procedural code,
and neither leg may drift into the other's world. M10 needs no new gate argument: a line
count of a file on disk is the same class of fact as M5's existence check, one file away.

**M10 is the WEAK guard, and the `etkl` pointer test below is the STRONG one. Both are
kept.** `test_etkl_criterion_sources_point_at_the_document_they_name` resolves a pointer by
JOINING the criterion to the corpus row it names — it can say the line is the *wrong* line.
Only `etkl` has a second graph to join against; `dec`, `holon`, `substrate` and `tab` cite
prose files, and there is nothing to join. So M10 is universal and weak (the pointer resolves
to *some* line of *some* real file) and the join stays narrow and strong. Neither subsumes
the other, and M10 must never grow into a claim about what the cited line says.

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

COR = Namespace("https://w3id.org/iladub/corpus#")
CORPUS_MANIFEST = REPO / "tests" / "corpus-manifest.ttl"

# `vocab/shapes/iladub-shapes.ttl:39` is the citation form spec §7.2.1 corrected the handoff
# to; the line number is a pointer INTO the artifact, not part of its path.
_LINE_SUFFIX = re.compile(r":\d+$")


# ---------------------------------------------------------------- the graph, read as rows

def validate_manifest(data_path, shapes_path=SHAPES):
    """The SHACL leg: (conforms, report_text) for one manifest against the membrane.

    `advanced=True` is required — most of the constraints are `sh:sparql` — and
    `inference="rdfs"` matches every other membrane in this repo (CLAUDE.md § Serialization).
    MEASURED 2026-08-22, after M12–M18 landed: `grep -c 'sh:sparql' tests/arc-shapes.ttl` ->
    **19** (it was 6 when this docstring was first written, and the number went stale in
    silence, which is why it now carries the command that produced it).
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


def source_rows(graph):
    """Yield (criterion_iri, prog:source) — one row per criterion, met or not.

    Unlike M5, this is NOT restricted to `met true`. prog:source is what makes
    prog:declaredOn auditable (arc-shapes.ttl:82-90), and a criterion asserts its
    declaration date whether or not it claims to be met — so an unmet row's pointer is
    exactly as load-bearing as a met one's.
    """
    for c in sorted(graph.subjects(RDF.type, PROG.Criterion), key=str):
        for s in sorted(graph.objects(c, PROG.source), key=str):
            yield str(c), str(s)


def blocked_rows(graph):
    """Yield (criterion_iri, residue_id) — one row per prog:blockedBy edge."""
    for c in sorted(graph.subjects(RDF.type, PROG.Criterion), key=str):
        for r in sorted(graph.objects(c, PROG.blockedBy), key=str):
            yield (str(c), str(r))


# ------------------------------------- the etkl rung, RECOMPUTED from the corpus register
#
# Why this leg lives here and not in tests/arc-shapes.ttl. The arc membrane closes over the
# arc manifest, and `tests/corpus-manifest.ttl` is a DIFFERENT GRAPH in a different file that
# the membrane's data graph does not contain. Joining the two at validation time would make
# the closed-world membrane derive from a world it does not close over — the move CLAUDE.md
# §8 forbids. So this is the same shape of question as M5 and M7: a fact about another
# artifact on disk, which is why it is procedural code beside them rather than SHACL.
#
# It derives nothing INTO either manifest. `prog:met` stays hand-asserted in a reviewed
# commit (spec §9); this leg only refuses an assertion the corpus register does not support.

def etkl_met_by_document(corpus_graph):
    """{cor:file -> bool}: the `etkl` rung's numerator, COMPUTED from the corpus register.

    Spec §7.1 states the criterion in prose — *"under a `cor:adjudication` whose rationale
    **accepts** that score — not one that holds it"* — and prose is not a predicate. The
    distinction is STRUCTURAL, and the corpus manifest's own header states where it lives
    (`tests/corpus-manifest.ttl:16-20`): *"There is no separate cor:Hold term: a HOLD is
    encoded AS cor:Unadjudicated plus a cor:adjudication node carrying the reviewer's
    rationale."* So the acceptance is carried by **cor:expectedVerdict**, and the
    adjudication carries the reason for whichever state the verdict names.

    The predicate, in one line:
        met  <=>  cor:expectedVerdict == cor:CompilesAbove
                  AND some cor:scoreFloor  AND some cor:adjudication

    Two consequences worth stating, because both are choices.

    * It is EXISTENTIAL over adjudications, not universal. `cor:adjudication` is an
      append-only history: graincorp-stem's own 2026-08-02 note is a HOLD and always will
      be, and its 2026-08-20 note supersedes that one. A universal reading (*every*
      adjudication must accept) would un-meet the one met document the moment its history
      was written down honestly — it would punish keeping the record. The verdict is the
      current state; the notes are how it got there.
    * It cannot be gamed by a rationale, because it never reads one. It CAN still be moved
      by a hand flipping cor:expectedVerdict to cor:CompilesAbove with a floor at today's
      score — that is spec §7.1's row 1 and it counts, by design: it is a dated, accountable
      act in a reviewed commit, and the corpus membrane makes it cost a cor:sha256 and a
      cor:adjudication. What is refused is the cheap version — writing a number down while
      the record still says the reading is held.
    """
    out = {}
    for doc in corpus_graph.subjects(RDF.type, COR.Document):
        f = str(corpus_graph.value(doc, COR.file))
        assert f not in out, f"two cor:Document entries claim {f!r}"
        out[f] = (corpus_graph.value(doc, COR.expectedVerdict) == COR.CompilesAbove
                  and corpus_graph.value(doc, COR.scoreFloor) is not None
                  and corpus_graph.value(doc, COR.adjudication) is not None)
    return out


def etkl_criteria(arc_graph):
    """{cor:file -> (criterion_iri, asserted_met, prog:source)} for the `etkl` rung.

    The document a criterion is about is the head of its `prog:statement`, up to the first
    ": " — the form task 3 authored all seven in. No corpus file path contains that
    separator, so the split is total.
    """
    out = {}
    for c in sorted(arc_graph.subjects(RDF.type, PROG.Criterion), key=str):
        if str(arc_graph.value(c, PROG.ofRung)) != "etkl":
            continue
        f = str(arc_graph.value(c, PROG.statement)).split(": ", 1)[0]
        assert f not in out, f"two etkl criteria claim {f!r}"
        out[f] = (str(c),
                  arc_graph.value(c, PROG.met).toPython(),
                  str(arc_graph.value(c, PROG.source)))
    return out


# ------------------------------------------------------- the environment, measured not read

@lru_cache(maxsize=1)
def collectable_node_ids():
    """Every pytest node id this runner can collect — ONE subprocess for the whole set.

    MEASURED 2026-08-20 on this tree:
        $ ./.venv/bin/python -m pytest --collect-only -q
        1252 tests collected in 3.86s      # before this module (0 errors, 0 skips)
        1266 tests collected in 1.16s      # after it; 1.2-3.9 s depending on cache warmth
    RE-MEASURED 2026-08-21, same command, after task 5 added three tests to this module:
        1270 tests collected in 1.51s
    A count in a docstring goes stale on any commit that adds a test, and nothing checks it
    — so it is re-measured whenever this module is edited rather than carried forward.

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


_SOURCE_LOC = re.compile(r"^(\d+)(?:-(\d+))?$")


def _source_refusal(iri, source):
    """The M10 message this prog:source earns, or None. Path existence + line range ONLY.

    Deliberately NOT a check that the cited line SAYS anything in particular — that is a
    different question and a different residue, and smuggling it in here would make one
    refusal answer two.

    The pointer form is `<path>:<line>` or `<path>:<start>-<end>`, both already in the
    manifest (`CLAUDE.md:252`, `docs/holonic-interaction.md:147-148`). A value with no
    line suffix is a bare path and is checked for existence alone — the membrane requires
    prog:source to exist, not to carry a line.
    """
    path, _, loc = source.rpartition(":")
    m = _SOURCE_LOC.match(loc)
    if not m:
        path, m = source, None
    target = REPO / path
    if not target.exists():
        return (f"M10: {iri} declares itself at prog:source {source!r}, whose path does not "
                f"exist in the working tree")
    if m is None:
        return None
    start, end = int(m.group(1)), int(m.group(2) or m.group(1))
    n = len(target.read_text(encoding="utf-8").splitlines())
    if not 1 <= start <= end <= n:
        return (f"M10: {iri} declares itself at prog:source {source!r}, but {path} has {n} "
                f"lines — the pointer resolves to nothing, so prog:declaredOn cannot be "
                f"audited by `git blame` on the line it names")
    return None


def _recorded_version_holds(recorded, running):
    """Dotted-prefix equality: the RECORDED PRECISION IS THE ASSERTION.

    "3.12" against a running 3.12.11 holds; "3.12.0" against it does not. So the manifest
    chooses what it is claiming by how many components it writes down, and no threshold or
    tuned tolerance decides anything (CLAUDE.md §8).
    """
    want = recorded.split(".")
    return running.split(".")[:len(want)] == want


# ------------------------------------------------------------------- the five refusals

def environment_refusals(graph):
    """Every M5 / M5b / M5c / M7 / M10 refusal this graph earns. Empty == admitted."""
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

    for iri, source in source_rows(graph):
        refusal = _source_refusal(iri, source)
        if refusal is not None:
            out.append(refusal)

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


def test_m1_a_criterion_that_does_not_say_where_it_was_declared_is_refused():
    """prog:declaredOn is only auditable through prog:source.

    The dating rule (spec §3.2) is that the date is the commit date of the LINE OF PROSE
    that declares the criterion — which is checkable by exactly one move, `git blame` on
    that line. A criterion with no prog:source names no line, so its date cannot be
    checked by anyone, and it degrades from a measurement into an assertion.

    The second assertion is what makes this fixture evidence about THIS clause rather than
    about M1 in general: `arc-m1-missing-field-leak.ttl` also earns exactly {M1}, so the
    refusal number alone cannot tell the two apart. The result PATH can.
    """
    _refused_by_shacl("arc-m1-missing-source-leak.ttl", "M1")
    _, report = validate_manifest(REPO / "tests" / "arc-m1-missing-source-leak.ttl")
    assert "Result Path: prog:source" in report, (
        "the refusal must be about prog:source itself, not some other M1 field:\n"
        f"{report}")


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
    """scripts/cockpit.py must read the manifest WITHOUT rdflib (cockpit.py:76-80). A regex
    read of arbitrary Turtle is unsafe; a regex read of a file where every criterion is a
    top-level IRI subject is safe, and M9 is what buys that."""
    _refused_by_shacl("arc-m9-blank-node-criterion-leak.ttl", "M9")


def test_m9b_an_iri_that_disagrees_with_its_rung_is_refused():
    """The IRI says `tab`, prog:ofRung says `dec`. The two encodings must agree, or the fast
    reader and rdflib disagree about which rung the criterion counts for."""
    _refused_by_shacl("arc-m9b-iri-rung-disagreement-leak.ttl", "M9b")


# ------------------------------------------- M12–M18: the dependency graph, also SHACL
#
# Seven refusals over the EDGES between criteria (spec 2026-08-22 §5). They are AXIOM /
# constraint, closed world, and they live in `tests/arc-shapes.ttl` for the same reason M1–M9b
# do: a dependency edge is a triple, so a membrane can see it. M19 — A5's two-sided ablation —
# is the one that cannot be here, and it is not in this module either: it creates a worktree,
# deletes a file and reads a pytest exit code, and lives in `tests/test_arc_ablation.py`.
#
# Every fixture below is a COMPLETE manifest fragment, copied from `tests/arc-manifest.ttl` so
# that no criterion in it earns an M1 as well; each one's header comment names, explicitly, why
# the other six refusals stay silent on it. That is what makes `_refused_by_shacl`'s exact-set
# assertion evidence about the constraint the fixture was written for.

def test_m12_a_dependency_on_something_that_is_not_a_criterion_is_refused():
    """A dangling edge is worse than no edge: it reads as structure and points at nothing.

    The contrast that makes this refusal correct rather than merely tidy is `prog:blockedBy`,
    whose values are plain string literals naming rows of a markdown register that is not in
    the graph at all — so the membrane cannot check them and M7 does it from the filesystem.
    A dependency target IS in the graph, so dangling is checkable here, and what is checkable
    in the membrane never gets delegated to procedural code.
    """
    _refused_by_shacl("arc-m12-dangling-target-leak.ttl", "M12")


def test_m13_a_criterion_that_depends_on_itself_is_refused():
    """A criterion cannot be its own precondition.

    M13 OWNS the self-edge and M14 is written not to see one — measured, and it is the whole
    reason M14 carries `FILTER(?y != $this)`. If both fired here the fixture would be
    evidence about neither, and the cycle refusal would be pinned by nothing.
    """
    _refused_by_shacl("arc-m13-self-edge-leak.ttl", "M13")


def test_m14_a_dependency_cycle_is_refused():
    """The GLOBAL refusal, and the one no local rule can stand in for.

    Every edge of `arc-m14-cycle-leak.ttl` is individually impeccable: both ends met, oracle
    tests disjoint, artifact files disjoint, both met the same day so A4 holds in BOTH
    directions. M15 sees nothing (nothing is unmet), M16 sees nothing (every precondition
    holds), M13 sees nothing (neither edge is a self-edge). Only the cycle is wrong, and only
    a query that follows the closure can find it.

    The second assertion is what stops M14 collapsing into M13: it must fire on BOTH members
    of the two-cycle, which a self-edge rule never would.
    """
    _refused_by_shacl("arc-m14-cycle-leak.ttl", "M14")
    _, report = validate_manifest(REPO / "tests" / "arc-m14-cycle-leak.ttl")
    for iri in ("criterion:holon:01", "criterion:holon:03"):
        assert f"progress#{iri}>" in report, (
            f"M14 must name every member of the cycle, and {iri} is missing:\n{report}")


def test_m15_a_met_criterion_may_not_depend_on_an_unmet_one():
    """The analogue of M8, and the cheapest catcher of a reversed edge: if the work landed,
    it was not waiting on something that has not.

    The constraint is EVIDENCE-POSITIVE — it matches a target asserting `prog:met false`, not
    one that merely fails to assert `prog:met true`. That is what keeps it off M12's dangling
    target, which has no `prog:met` at all, and it is CLAUDE.md §8's rule that a derivation
    never infers from absence applied to a membrane that easily could have.
    """
    _refused_by_shacl("arc-m15-met-depends-on-unmet-leak.ttl", "M15")


def test_m16_an_asserted_edge_that_fails_a_precondition_is_refused():
    """A1–A4 and A6, one fixture each, all five carrying the refusal number M16.

    Five assertions and not one, because five separate `sh:sparql` constraints answer five
    different questions and a single fixture would leave four of them unpinned — a constraint
    no fixture reaches is a constraint that can rot silently, which is the failure CLAUDE.md
    § Plan authoring rule 4 exists to prevent.

      * A1 — an end that is not met. The unmet end is the SUBJECT, deliberately: a met
        criterion asserting a dependency on an unmet one is M15's case, not M16's.
      * A2 — an end naming no oracle at all: nothing to delete, nothing to run.
      * A3 — the Q2 refusal: the two ends share both oracle tests, so both arms of the
        ablation would fail for the same reason and say nothing about either criterion.
      * A4 — a target met five days AFTER the criterion that supposedly depended on it.
        Non-strict, so a same-day pair is admitted; only the contradiction is refused.
      * A6 — the Q6 refusal: `vocab/shapes/dec-shapes.ttl:60` and `…:48` are ONE file, and
        ablation deletes files.
    """
    for fixture in ("arc-m16-ungrounded-assertion-leak.ttl",
                    "arc-m16-a1-unmet-end-leak.ttl",
                    "arc-m16-a2-no-oracle-leak.ttl",
                    "arc-m16-a4-target-met-later-leak.ttl",
                    "arc-m16-a6-shared-artifact-file-leak.ttl"):
        _refused_by_shacl(fixture, "M16")

    # …and each fixture must reach ITS OWN precondition. Without this the five could all be
    # tripping A1 and the exact-set assertion above would not notice.
    for fixture, precondition in (("arc-m16-ungrounded-assertion-leak.ttl", "M16: A3"),
                                  ("arc-m16-a1-unmet-end-leak.ttl", "M16: A1"),
                                  ("arc-m16-a2-no-oracle-leak.ttl", "M16: A2"),
                                  ("arc-m16-a4-target-met-later-leak.ttl", "M16: A4"),
                                  ("arc-m16-a6-shared-artifact-file-leak.ttl", "M16: A6")):
        _, report = validate_manifest(REPO / "tests" / fixture)
        assert precondition in report, f"{fixture} must trip {precondition}:\n{report}"


def test_m17_a_proposition_that_hides_a_groundable_edge_is_refused():
    """THE FORCING FUNCTION. It makes "propose it and move on" unavailable wherever grounding
    is possible.

    `holon:03 → holon:01` satisfies every membrane precondition of the asserted grade, so the
    author owes the assertion and owes CI the chance to refute the reading. Without M17 the
    proposition grade becomes a place to hide and the two-predicate split buys nothing —
    `prog:dependsOn+` would still be a grounded closure, over an arbitrarily small subset of
    the edges the author actually believes in.

    The exact complement is asserted too: the SAME pair at the SAME grade with a rationale is
    what `arc-m17-hidden-groundable-leak.ttl` carries, and `arc-m18-asserted-with-rationale-
    leak.ttl` is that pair at the OTHER grade — so between them the two fixtures prove M17
    fires on the grade and not on the pair.
    """
    _refused_by_shacl("arc-m17-hidden-groundable-leak.ttl", "M17")


def test_m18_the_rationale_cardinality_of_an_edge_is_refused_when_wrong():
    """Exactly one rationale per proposition, none per assertion — three fixtures, three ways
    to get it wrong, and all three are real.

      * NONE on a proposition. An ungrounded claim entered without saying why it could not be
        grounded is indistinguishable, later, from an assertion somebody forgot to ground.
      * TWO on a proposition. Not a richer record: an unresolved disagreement stored as if it
        were a fact. Pinning only the zero side would leave a membrane that accepted any
        number above zero looking green.
      * ANY on an assertion. An assertion is grounded by A5's ablation running in CI and by
        nothing else; prose beside it is a second, unfalsifiable account that will still read
        as true on the day the ablation refutes the edge. Spec §3 refuses a stored
        `prog:ablation` record for exactly this reason.

    The rationale rides an `rdf:Statement` reification node, not a literal on the criterion
    (plan §0/C3): a literal on the criterion cannot say WHICH proposed edge it explains, so
    "exactly one" would be unstatable the moment a criterion proposed two targets.
    """
    for fixture in ("arc-m18-rationale-cardinality-leak.ttl",
                    "arc-m18-two-rationales-leak.ttl",
                    "arc-m18-asserted-with-rationale-leak.ttl"):
        _refused_by_shacl(fixture, "M18")

    for fixture, arm in (("arc-m18-rationale-cardinality-leak.ttl", "carries no prog:depend"),
                         ("arc-m18-two-rationales-leak.ttl", "carries more than one"),
                         ("arc-m18-asserted-with-rationale-leak.ttl", "may not carry a")):
        _, report = validate_manifest(REPO / "tests" / fixture)
        assert arm in report, f"{fixture} must trip the {arm!r} arm of M18:\n{report}"


# ------------------------------------------ the one <path>:<line> parser, asserted to be one

_REPLACE_CALL = re.compile(r'REPLACE\(STR\(\?\w+\), "([^"]+)", ""\)')


def test_the_sparql_line_strip_agrees_with_the_python_one():
    """A6 STRIPS `<path>:<line>` IN SPARQL AND `_LINE_SUFFIX` STRIPS IT IN PYTHON, and this is
    the only thing that says the two agree.

    R109 is open precisely because this repo already carries two divergent `<path>:<line>`
    parsers; M16/A6 would have been a third if it were pinned by a comment. So this reads the
    regex OUT OF the membrane rather than restating it — a restated regex is a fourth copy —
    demands that every `REPLACE` in `tests/arc-shapes.ttl` uses the same one, and then makes
    the two implementations strip every `prog:oracleArtifact` value in the live manifest and
    agree on the result.

    The last assertion is the one that keeps the agreement HONEST rather than accidental.
    MEASURED 2026-08-22 over all 43 criteria: `prog:oracleArtifact` takes exactly two forms,
    `<path>` and `<path>:<n>`. The range form `<path>:<n>-<m>` occurs in `prog:source` and in
    no `prog:oracleArtifact`, and `":[0-9]+$"` and `r":\\d+$"` agree on every form that does
    occur. The day one does not, this goes red and the divergence becomes a decision instead
    of a silent third parser.
    """
    shapes_text = SHAPES.read_text(encoding="utf-8")
    calls = _REPLACE_CALL.findall(shapes_text)
    # The SET assertion below cannot see a call the REGEX misses — a `REPLACE( STR(?a), …)`
    # written with different spacing would be a second parser that never enters `strips` at
    # all, so `len(strips) == 1` would stay green while the divergence shipped. This counts
    # the calls INDEPENDENTLY, by the bare token, and is the only thing that says the regex
    # reads every one of them. MEASURED 2026-08-22: 4 (M16/A6 and M17, two each).
    assert len(calls) == shapes_text.count("REPLACE("), (
        f"{shapes_text.count('REPLACE(')} REPLACE calls in tests/arc-shapes.ttl but "
        f"_REPLACE_CALL matches only {len(calls)} — one is written in a form this test "
        "cannot read, so it is an unchecked <path>:<line> parser (R109)")
    strips = set(calls)
    assert len(strips) == 1, (
        f"tests/arc-shapes.ttl strips a line suffix {len(strips)} different ways: {strips}. "
        "M16/A6 and M17 must use one regex, or an edge can fail one and pass the other")
    (sparql_strip,) = strips

    g = Graph().parse(MANIFEST, format="turtle")
    rows = list(g.query("""PREFIX prog: <https://w3id.org/iladub/progress#>
        SELECT ?a (REPLACE(STR(?a), "%s", "") AS ?f) WHERE { ?c prog:oracleArtifact ?a }"""
                        % sparql_strip))
    assert rows, "the manifest names no prog:oracleArtifact; this test would be vacuous"

    for artifact, stripped in rows:
        assert str(stripped) == _LINE_SUFFIX.sub("", str(artifact)), (
            f"{artifact!s}: the membrane strips it to {stripped!s} and _LINE_SUFFIX "
            f"(tests/test_arc_manifest.py:63) strips it to "
            f"{_LINE_SUFFIX.sub('', str(artifact))} — R109's third parser has arrived")
        assert ":" not in str(stripped), (
            f"{artifact!s} carries a suffix neither parser was measured against (a range, a "
            "drive letter, a URL scheme). Decide what A6 means for it before adding it")


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


def test_m10_a_source_pointer_that_resolves_to_nothing_is_refused():
    """R105, closed. `prog:source` is the ONLY thing that makes `prog:declaredOn` auditable
    (arc-shapes.ttl:82-90), and the membrane checks only that it is present and a string.

    Both arms are asserted, because M10 has two and the refusal number alone cannot tell
    them apart: a path that does not exist, and a line beyond the end of a path that does.
    This is the WEAK-BUT-UNIVERSAL guard. It deliberately does NOT subsume
    test_etkl_criterion_sources_point_at_the_document_they_name, which resolves a pointer by
    JOINING the criterion to the document it names — only `etkl` has a second graph to join
    against, so that one stays the strong guard for the one rung that supports it. Two
    instruments, both kept.
    """
    _refused_by_environment("arc-m10-stale-source-pointer-leak.ttl", "M10")
    reasons = environment_refusals(Graph().parse(
        REPO / "tests" / "arc-m10-stale-source-pointer-leak.ttl", format="turtle"))
    assert len(reasons) == 2, reasons
    assert any("does not exist" in r and "battery-run-final" in r for r in reasons), reasons
    assert any("has 1" in r or "line" in r for r in reasons if "CLAUDE.md" in r), reasons


# -------------------------------------------- the etkl rung: computed, pinned, ungameable

_HOLD = ('cor:expectedVerdict cor:Unadjudicated ; '
         'cor:adjudication [ cor:by "F" ; cor:on "2026-08-20"^^xsd:date ; cor:rationale '
         '"HOLD: 0.3438 is a measurement, nobody has read this compile against the PDF." ]')
_ACCEPT = ('cor:expectedVerdict cor:CompilesAbove ; '
           'cor:adjudication [ cor:by "F" ; cor:on "2026-08-20"^^xsd:date ; cor:rationale '
           '"ACCEPTED: read against the source; 0.3438 is what this document supports." ]')


def _synthetic(body):
    return Graph().parse(data="""@prefix cor: <https://w3id.org/iladub/corpus#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
<urn:iladub:corpus:synthetic> a cor:Document ;
    cor:file "gov-stats/bfs-population-bilan-2023.pdf" ;
    cor:url "https://example.org/f" ; cor:family "gov-stats" ; cor:series "s" ;
    cor:sha256 "%s" ; %s .
""" % ("0" * 64, body), format="turtle")


_FILE = "gov-stats/bfs-population-bilan-2023.pdf"
# bfs's measured score, census § Seam 1 (2026-08-20, HEAD 820ab24). It is here as the
# WORST CASE for the gameability defect and is never compared against anything: pinning a
# floor AT the measured score is the move under test, so the number's only job is to be the
# one a floor would be pinned at. Not a threshold, nothing is tuned to it.
_MEASURED = '0.3438'


def test_a_hold_with_a_floor_pinned_at_its_measured_score_is_not_met():
    """Spec §8's named falsifier, and the defect `820ab24` fixed only in prose.

    A `cor:scoreFloor` is a REGRESSION GUARD, so nothing stops it being pinned at whatever a
    document scores today. Under the criterion as §7.1 first worded it, six such lines would
    take this rung from 1/7 to 7/7 without a single reading improving — a criterion that
    rewards writing the number down. This pins all three rows of §7.1's table on the same
    synthetic document, so the refusal is provably about the hold-vs-accept STATE and not
    about the floor, the score, or the document:

      * floor pinned at the measured score + a recorded HOLD -> NOT met  (the falsifier)
      * the same floor + an accepting verdict                -> met      (not vacuous)
      * a bare unadjudicated row, no floor at all            -> NOT met

    Without the middle row a predicate that returned False unconditionally would pass this
    test, which is the failure mode CLAUDE.md § Plan authoring rule 4 exists for.
    """
    gamed = _synthetic(f'cor:scoreFloor "{_MEASURED}"^^xsd:decimal ; {_HOLD}')
    assert etkl_met_by_document(gamed)[_FILE] is False, (
        "a floor pinned at the measured score, under a rationale that HOLDS the reading, "
        "must not satisfy the etkl criterion — never lower a bar to meet it")

    accepted = _synthetic(f'cor:scoreFloor "{_MEASURED}"^^xsd:decimal ; {_ACCEPT}')
    assert etkl_met_by_document(accepted)[_FILE] is True, (
        "the predicate must be able to say YES, or the falsifier above proves nothing")

    bare = _synthetic("cor:expectedVerdict cor:Unadjudicated")
    assert etkl_met_by_document(bare)[_FILE] is False


def test_etkl_criteria_agree_with_the_corpus_manifest():
    """The `etkl` numerator is DERIVED-AND-CHECKED, not merely asserted.

    Task 3 authored all seven `prog:met` booleans by hand. This recomputes them from
    `tests/corpus-manifest.ttl` and refuses any disagreement — so an edit to either manifest
    that moves this rung without moving the other one goes red. It is the only thing in the
    repo that makes the strip's `etkl` fraction answerable to the corpus register. (It read
    `etkl 1/7` when written; R45 took who-wfa to an accepting adjudication on 2026-08-31 and
    the fraction is 2/7. The count is pinned below and moves only by a reviewed hand.)

    Note what this does NOT do: it never writes `prog:met` (spec §9). A disagreement is a
    refusal for a hand to resolve in a reviewed commit, in whichever direction is true.
    """
    computed = etkl_met_by_document(Graph().parse(CORPUS_MANIFEST, format="turtle"))
    asserted = etkl_criteria(Graph().parse(MANIFEST, format="turtle"))

    assert set(asserted) == set(computed), (
        "every corpus document must have exactly one etkl criterion and vice versa; "
        f"only in the arc manifest: {sorted(set(asserted) - set(computed))}; "
        f"only in the corpus register: {sorted(set(computed) - set(asserted))}")
    for f, (iri, met, _) in sorted(asserted.items()):
        assert met == computed[f], (
            f"{iri} asserts prog:met {met} for {f}, but the corpus register computes "
            f"{computed[f]} — fix whichever is wrong by hand; nothing here writes either file")
    assert sum(computed.values()) == 2, (
        f"measured 2026-08-31: exactly two corpus documents are accepted; got {computed}")


def test_etkl_criterion_sources_point_at_the_document_they_name():
    """`prog:source` is a LINE POINTER into a file that keeps growing, and the membrane
    checks neither its path nor its line — `prog:source` is required to be PRESENT and
    nothing more. So every commit that inserts a line into the corpus register silently
    invalidates the pointers below it, which is exactly what this task's own adjudication
    pass did to six of the seven. Prose cannot hold that; this can.
    """
    corpus = Graph().parse(CORPUS_MANIFEST, format="turtle")
    subject_of = {str(corpus.value(d, COR.file)): str(d)
                  for d in corpus.subjects(RDF.type, COR.Document)}
    lines = CORPUS_MANIFEST.read_text(encoding="utf-8").splitlines()

    for f, (iri, _, source) in sorted(etkl_criteria(Graph().parse(MANIFEST, format="turtle")).items()):
        path, _, lineno = source.rpartition(":")
        assert path == "tests/corpus-manifest.ttl", f"{iri}: unexpected prog:source {source!r}"
        assert lines[int(lineno) - 1].startswith(f"<{subject_of[f]}>"), (
            f"{iri} points at {source}, which is not the subject line of {f} — "
            f"that line now reads {lines[int(lineno) - 1]!r}; re-point it")


# ------------------------------------------------------------------------ the one positive

ZERO_CRITERIA = REPO / "tests" / "arc-zero-criteria-rung.ttl"


def test_a_rung_with_no_criteria_conforms_and_is_not_a_refusal():
    """Decision 6 doing its work: UNKNOWN IS NOT ZERO.

    A rung that declares no criteria renders `?` — never an empty bar, never 0/0 — and is
    deliberately not a refusal. This is the one test in the file that asserts CONFORMANCE,
    and it asserts it of two graphs, both of which matter:

      * the LIVE tracked manifest, against BOTH legs of the membrane. It is this membrane's
        worked example (CLAUDE.md § Serialization), and the only assertion here that goes
        red when a hand-authored criterion is wrong.
      * `arc-zero-criteria-rung.ttl`, which is where the zero-criteria claim itself lives.
        It lived on the live manifest while that file was a seed; the moment this loop
        authored the first criteria the live file stopped being able to carry it, and once
        all five rungs are populated it could not carry it at all. A claim that expires as
        the repo fills was never pinned to the right graph.
    """
    for path in (MANIFEST, ZERO_CRITERIA):
        ok, report = validate_manifest(path)
        assert ok, report
        assert environment_refusals(Graph().parse(path, format="turtle")) == []

    g = Graph().parse(MANIFEST, format="turtle")
    assert len(set(g.subjects(RDF.type, PROG.Manifest))) == 1
    assert {str(g.value(r, PROG.rungKey)) for r in g.subjects(RDF.type, PROG.Rung)} == {
        "etkl", "dec", "holon", "tab", "substrate"}

    z = Graph().parse(ZERO_CRITERIA, format="turtle")
    assert set(z.subjects(RDF.type, PROG.Rung)), "the fixture must declare a rung"
    assert list(oracle_rows(z)) == [], "…and that rung must declare no criteria"
