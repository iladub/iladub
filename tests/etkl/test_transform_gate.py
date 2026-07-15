"""Neurosymbolic-first gate (CLAUDE.md §8): the transform is AXIOM (SPARQL); no tuned
constant or numeric tolerance may live in the .rq files or in interpret.py. The only
numeric tolerance in the substrate is _TOL in oracle.py — the decidable exact-equality
compare (PROCEDURAL), never a transform tuning knob."""
import os
import re
import glob

HERE = os.path.dirname(__file__)
QUERIES = os.path.join(HERE, "..", "..", "vocab", "queries")
INTERPRET = os.path.join(HERE, "..", "..", "src", "iladub", "etkl", "interpret.py")

# a bare decimal/float literal (a tuned tolerance/constant). RDF header-level integers
# 0/1 have no decimal point and never match; xsd:decimal casts contain no digit.digit.
_FLOAT = re.compile(r"(?<![\w:])\d+\.\d+")


def _strip_comments(text):
    """Drop '#'-to-end-of-line comments (both SPARQL and Python) before scanning, so a
    version reference in a comment (e.g. 'SPARQL 1.1', 'A2.1') is not misread as a tuned
    constant. Only executable transform text is scanned."""
    return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def test_no_tuned_constant_in_rq_files():
    rqs = glob.glob(os.path.join(QUERIES, "*.rq"))
    assert rqs, "expected the reshape CONSTRUCT files to exist"
    for path in rqs:
        body = _strip_comments(open(path, encoding="utf-8").read())
        assert not _FLOAT.search(body), "tuned float constant in transform query %s" % path


def test_no_tuned_constant_in_interpret():
    body = _strip_comments(open(INTERPRET, encoding="utf-8").read())
    assert not _FLOAT.search(body), "interpret.py (engine glue) must carry no numeric tolerance"


def test_replay_and_fmt_are_retired():
    import iladub.etkl.oracle as oracle
    assert not hasattr(oracle, "replay"), "oracle.replay (Python interpreter) must be retired"
    assert not hasattr(oracle, "_fmt"), "oracle._fmt (float-format twin) must be retired"


def test_recover_base_is_retired():
    import iladub.etkl.reshape as reshape
    assert not hasattr(reshape, "recover_base"), "reshape.recover_base must be retired (use derive_base)"


def test_role_axiom_queries_present_and_axis_dimensions_retired():
    import glob, os
    rqs = {os.path.basename(p) for p in glob.glob(os.path.join(QUERIES, "*.rq"))}
    assert {"name-levels.rq", "recover-dimensions.rq", "operand-exclusions.rq"} <= rqs
    import iladub.etkl.denormalization as dn
    assert not hasattr(dn, "_axis_dimensions"), "_axis_dimensions (set-algebra role body) must be retired"
