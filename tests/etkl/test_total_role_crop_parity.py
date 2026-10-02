"""R261 loop (b) Task 6 Step 3 (plan `docs/superpowers/plans/2026-10-02-r261-grand-total.md`,
spec `docs/superpowers/specs/2026-10-02-r261-grand-total-design.md` § 3 "the crop"): production's
`totalrole.crop_box` for cbh's grand-total candidate (`1,951,264`) equals the probe's `derived_box`
(`scripts/r261_grand_total_role_probe.py`, measured by Task 0 § 0.3,
`docs/superpowers/2026-10-02-r261-grand-total-evidence.md`) — the SAME box, exactly, no tolerance.

Corpus-marked (`-m corpus`), local: it compiles `corpus/ag-trade/cbh-stem-2026-08-03.pdf` through
`compile_document`, the production path, with no env vars set — `readings/total_role/` already
carries the one recorded `total_role` reading (Task 6 Step 1), so no network call happens.

WHY THIS DOES NOT IMPORT THE PROBE MODULE (plan/brief: "or equivalent if importing is impossible
— then say why"). `scripts/r261_grand_total_role_probe.py` has no `if __name__ == "__main__":`
guard: everything from its `path = glob.glob("corpus/**/cbh*.pdf", ...)` line to EOF — opening the
PDF, cropping, drawing the red box and (under the default `VIA=http`) reading
`ANTHROPIC_API_KEY` and making an HTTP call per case — runs unconditionally at import time
(measured: `scripts/r261_grand_total_role_probe.py:122-140`). A plain `import
r261_grand_total_role_probe` from this test would therefore attempt live API calls on every run.
Instead, `_probe_derived_box` execs the file's own source, TRUNCATED at that line (everything
above it: the module docstring, constants and the `ask`/`derived_box` function definitions, none
of which reads an env var or touches the network), and returns the `derived_box` function object
that exec produced — the committed function, byte-for-byte, never re-implemented.

Classification (CLAUDE.md § 8): PROCEDURAL instrumentation. It reads back a value `totalrole.py`
already computed (via a spy on `crop_box`, restored after) and a value the probe's own function
computes; it judges nothing and carries no constant beyond the 4 pt margin already in both
functions under test.

## FALSIFICATION
Change `totalrole.crop_box`'s margin from 4 to 5 pt (both occurrences: the `- 4` on `xs0`/`tops`
and the `+ 4` on `xs1`/`bottoms`) -> `test_production_crop_box_equals_the_probes_derived_box` goes
red (production box shifted 1 pt on every side, probe box unchanged). Restore -> green.
"""
from pathlib import Path

import pdfplumber
import pytest

from iladub.etkl import totalrole as R

pytestmark = pytest.mark.corpus

REPO = Path(__file__).resolve().parent.parent.parent
CBH = REPO / "corpus" / "ag-trade" / "cbh-stem-2026-08-03.pdf"
PROBE = REPO / "scripts" / "r261_grand_total_role_probe.py"

needs_cbh = pytest.mark.skipif(not CBH.is_file(),
                                reason="corpus not populated (scripts/fetch_corpus.py)")


def _probe_derived_box():
    """Execs the probe's source up to (not including) its module-level side-effecting block and
    returns the `derived_box` function it defines. See module docstring for why this is the
    equivalent of importing it."""
    src = PROBE.read_text(encoding="utf-8")
    marker = '\npath = glob.glob("corpus/**/cbh*.pdf", recursive=True)[0]\n'
    idx = src.index(marker)
    ns: dict = {"__name__": "r261_grand_total_role_probe_truncated", "__file__": str(PROBE)}
    exec(compile(src[:idx], str(PROBE), "exec"), ns)
    return ns["derived_box"]


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    R._TOTAL_ROLE_CACHE.clear()
    for k in ("BAML_LIVE", "ILADUB_RECORD_READINGS"):
        monkeypatch.delenv(k, raising=False)
    yield
    R._TOTAL_ROLE_CACHE.clear()


@needs_cbh
def test_production_crop_box_equals_the_probes_derived_box():
    captured: list = []
    original = R.crop_box

    def spy(*args, **kwargs):
        box = original(*args, **kwargs)
        captured.append(box)
        return box

    R.crop_box = spy
    try:
        from iladub.etkl.document import compile_document
        compile_document(str(CBH))
    finally:
        R.crop_box = original

    assert captured, ("totalrole.crop_box was never called compiling cbh — the grand-total "
                       "candidate did not reach the totals level")
    assert len(set(captured)) == 1, (
        f"crop_box was called with {len(set(captured))} distinct boxes, expected exactly one: "
        f"{sorted(set(captured))}")
    production_box = captured[0]

    derived_box = _probe_derived_box()
    with pdfplumber.open(str(CBH)) as pdf:
        page = pdf.pages[0]
        probe_box = derived_box(str(CBH), page)

    assert production_box == probe_box, (production_box, probe_box)
