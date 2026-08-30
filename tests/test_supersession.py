"""R128 — dec:supersedes is constrained. It was constrained by NOTHING until 2026-08-30.

The row: `dec:supersedes` is declared in `dec.ttl:173-175` with a domain and a range, is
load-bearing for withdrawal, section repair and datagrid adoption, and is read by three shipped
queries — and `git grep -n "supersedes" -- vocab/shapes/` returned **exit 1, no output**. A
malformed supersession could refuse at no membrane.

A worked example that CONFORMS plus a negative per constraint that must FAIL, per CLAUDE.md
§ Serialization. Every case is checked at BOTH seams — `iladub.validate.validate` (pySHACL with
rdfs inference, the seam every vocabulary example is validated at) and `membrane.validate` (the
seam the compile membrane actually uses, whichever engine is installed) — because the two are
not interchangeable: they disagreed on `sh:nodeKind`, which is why the shape carries none.
"""
import glob
import os

import pytest
from rdflib import Graph, Namespace

from iladub.etkl import membrane
from iladub.validate import validate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEC = Namespace("https://w3id.org/iladub/dec#")

NEGATIVES = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "tests", "supersession-*.ttl")))


def _shapes():
    return Graph().parse(os.path.join(ROOT, "vocab", "shapes", "dec-shapes.ttl"), format="turtle")


def _ont():
    return Graph().parse(os.path.join(ROOT, "vocab", "ontology", "dec.ttl"), format="turtle")


def _data(relpath):
    return Graph().parse(os.path.join(ROOT, relpath), format="turtle")


# ==================================================================== the worked example

def test_the_worked_example_conforms_at_both_seams():
    """It is shaped like the corpus, not like a minimal fixture: the fan-out in it (one
    admission superseding three verdicts) is the shape apple's datagrid admission actually has,
    measured at out-degree 5 on 2026-08-30."""
    data, shapes, ont = _data("examples/supersession.ttl"), _shapes(), _ont()
    assert validate(data, shapes, ont).conforms
    conforms, report = membrane.validate(data, shapes, ont)
    assert conforms, report


def test_a_fan_out_is_admitted_because_the_corpus_has_one():
    """The measurement that decided there is no `sh:maxCount` on the arc: apple's
    `.../p1/adopt#p1-datagrid-admission` supersedes FIVE distinct verdict decisions, because
    `document.py`'s adoption site adds one edge per superseded band, in a loop. A `sh:maxCount 1`
    there would refuse a document that is correct — so this asserts the fan-out is present in the
    example AND that the example conforms."""
    data = _data("examples/supersession.ttl")
    admission = Namespace("https://example.org/demo#")["p1-datagrid-admission"]
    assert len(set(data.objects(admission, DEC.supersedes))) == 3
    assert validate(data, _shapes(), _ont()).conforms


# ==================================================================== the negatives

def test_there_is_a_negative_case_for_every_constraint():
    """Four constraints, four negatives. A guard against a constraint being added later with no
    case that must fail — which is how `dec:supersedes` came to be unconstrained in the first
    place."""
    assert NEGATIVES == ["supersession-self-loop.ttl", "supersession-two-superseders.ttl",
                         "supersession-untyped-object.ttl", "supersession-untyped-subject.ttl"]


@pytest.mark.parametrize("negative", NEGATIVES)
def test_the_negative_refuses_under_pyshacl_with_rdfs_inference(negative):
    assert not validate(_data("tests/" + negative), _shapes(), _ont()).conforms


@pytest.mark.parametrize("negative", NEGATIVES)
def test_the_negative_refuses_at_the_compile_membrane_seam(negative):
    """The seam that matters operationally: `_validate` reaches these shapes through
    `membrane.validate`, and that path skolemizes and applies only a subclass closure — not the
    full RDFS inference `iladub.validate.validate` runs. A negative that refuses only under the
    richer seam would be a shape the membrane cannot actually enforce."""
    conforms, _ = membrane.validate(_data("tests/" + negative), _shapes(), _ont())
    assert not conforms


@pytest.mark.parametrize("negative", NEGATIVES)
def test_both_engines_agree_on_every_negative(negative):
    """Engine parity, and it is not decoration here: `dec:SupersededOnceShape` is the FIRST
    `sh:inversePath` in `vocab/` (`grep -rn inversePath vocab/shapes/` was empty before this
    shape), so rudof's support for it is measured rather than assumed."""
    if not membrane.rudof_available():
        pytest.skip("pyrudof not installed")
    data, shapes, ont = _data("tests/" + negative), _shapes(), _ont()
    assert membrane._validate_pyshacl(data, shapes, ont)[0] is False
    assert membrane._validate_rudof(data, shapes, ont)[0] is False


def test_both_engines_agree_the_worked_example_conforms():
    if not membrane.rudof_available():
        pytest.skip("pyrudof not installed")
    data, shapes, ont = _data("examples/supersession.ttl"), _shapes(), _ont()
    assert membrane._validate_pyshacl(data, shapes, ont)[0] is True
    assert membrane._validate_rudof(data, shapes, ont)[0] is True


# ==================================================================== the row's own measurement

def test_supersedes_is_targeted_by_a_shape_at_all():
    """The row's literal defect, pinned so it cannot recur silently: `dec:supersedes` appeared in
    no shape file. This is the assertion that goes red if the shapes are deleted."""
    from rdflib.namespace import SH
    shapes = _shapes()
    targeted = set(shapes.subjects(SH.targetSubjectsOf, DEC.supersedes)) | \
        set(shapes.subjects(SH.targetObjectsOf, DEC.supersedes))
    assert targeted, "no shape targets dec:supersedes — R128 has regressed"
