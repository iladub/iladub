"""Suite-wide guard: a test that skips for want of a corpus document must carry
`pytest.mark.corpus` (R173), or `-m "not corpus"` silently runs it locally while CI skips it.
Pinned by `tests/test_corpus_tag_guard.py`."""
import re

import pytest

CORPUS_SKIP = re.compile(r"corpus.*not (fetched|populated)|held-out/.*absent")


def _skip_reason(rep):
    return str(rep.longrepr[2]) if rep.skipped and isinstance(rep.longrepr, tuple) else ""


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    if item.get_closest_marker("corpus") is not None:
        return
    # A declared `skipif` is judged by its reason, not its condition, so the defect shows on a
    # machine that HAS the corpus too. A run-time `pytest.skip` is only visible when it fires.
    declared = ([m.kwargs.get("reason", "") for m in item.iter_markers("skipif")]
                if call.when == "setup" else [])
    hit = next((r for r in [*declared, _skip_reason(rep)] if CORPUS_SKIP.search(r)), None)
    if hit:
        rep.outcome = "failed"
        rep.longrepr = (f"{item.nodeid} skips for a corpus document ({hit!r}) but does not carry "
                        f"pytest.mark.corpus, so `-m \"not corpus\"` runs it locally while CI "
                        f"skips it (R173; see tests/conftest.py)")
