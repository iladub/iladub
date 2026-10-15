"""Every test that skips for want of a corpus document carries `pytest.mark.corpus` (R173).

THE POINT: `corpus/` and `held-out/` are gitignored, so CI skips every test that reads them, and
the local pre-PR gate `-m "not corpus"` is meant to select exactly what CI runs. A test gated by a
`skipif` alone is invisible to that filter: measured 2026-10-15, 104 such tests ran locally under
`-m "not corpus"` and cost 6069 of the suite's 8878 test-seconds, which is why a CI-equivalent
local run took 37 minutes instead of 6. The guard in `tests/conftest.py` refuses the untagged
form, whether the skip is declared (`skipif`, checked even when the document IS present) or raised
at run time (`pytest.skip`, visible wherever the document is absent — CI)."""
import pytest

pytest_plugins = "pytester"

GUARD = open(__file__.replace("test_corpus_tag_guard.py", "conftest.py")).read()


def _run(pytester, body):
    pytester.makeconftest(GUARD)
    pytester.makepyfile(test_inner=body)
    return pytester.runpytest_inprocess("-p", "no:xdist", "-p", "no:cacheprovider")


def test_an_untagged_corpus_skipif_fails_even_when_the_document_is_present(pytester):
    rep = _run(pytester, """
import pytest
@pytest.mark.skipif(False, reason="corpus not fetched")
def test_reads_corpus():
    pass
""")
    rep.assert_outcomes(errors=1)
    rep.stdout.fnmatch_lines(["*pytest.mark.corpus*"])


def test_an_untagged_runtime_corpus_skip_fails(pytester):
    rep = _run(pytester, """
import pytest
def test_reads_corpus():
    pytest.skip("apple: corpus document not fetched")
""")
    rep.assert_outcomes(failed=1)


def test_an_untagged_held_out_skipif_fails(pytester):
    rep = _run(pytester, """
import pytest
@pytest.mark.skipif(True, reason="held-out/fed-h41 absent (gitignored corpus)")
def test_reads_held_out():
    pass
""")
    rep.assert_outcomes(errors=1)


def test_a_tagged_corpus_test_skips_and_runs_as_before(pytester):
    rep = _run(pytester, """
import pytest
pytestmark = pytest.mark.corpus
@pytest.mark.skipif(True, reason="corpus not fetched")
def test_absent():
    pass
@pytest.mark.skipif(False, reason="corpus not fetched")
def test_present():
    pass
def test_runtime():
    pytest.skip("corpus document not fetched")
""")
    rep.assert_outcomes(passed=1, skipped=2)


def test_a_skip_for_another_reason_is_untouched(pytester):
    rep = _run(pytester, """
import pytest
@pytest.mark.skipif(True, reason="reportlab missing")
def test_optional_dep():
    pass
def test_live():
    pytest.skip("set BAML_LIVE=1 to call the real API")
""")
    rep.assert_outcomes(skipped=2)
