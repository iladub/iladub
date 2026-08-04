# Corpus Harness (full plan) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the real-document corpus battery permanent — a UA-capable fetcher with first-fetch pinning, a SHACL membrane over the tracked manifest, a manifest-driven `tests/test_corpus.py` that asserts each document's expected verdict under a wall-clock budget, and the 6 remaining seed documents (spec 2026-08-02 §4–§5).

**Architecture:** The tracked RDF manifest (`tests/corpus-manifest.ttl`, `cor:` repo-internal namespace) is the single oracle: the fetcher populates gitignored `corpus/` from it, the membrane (`tests/corpus-shapes.ttl`, closed-world SHACL) guards the register's integrity, and the battery parametrizes one pytest per `cor:Document`, asserting `cor:CompilesAbove`/`cor:SemanticEscalation`/`cor:Unadjudicated` semantics via the public `compile_document` API (+ `ground_document` where the manifest declares a contract). Absent documents skip visibly; nothing ever writes the manifest automatically.

**Tech Stack:** Python 3 (`.venv`), rdflib, pySHACL (`inference="rdfs"`, `advanced=True`), pdfplumber, reportlab (synthetic unit fixtures), pytest (`corpus` marker already in `pyproject.toml`).

**Doc impact:** increment — a wiki concept page for the corpus harness (fetch / run / adjudicate workflow), queued for the next release; no contradiction.

## Global Constraints

- **Neurosymbolic gate (CLAUDE.md §8):** fetcher + battery glue are *justified PROCEDURAL* (network, file I/O, checksum, test-harness engine glue — irreducible; say so in each file's docstring). The manifest membrane is a **SHACL closed-world constraint** (register integrity = membrane, never derivation). No reading/geometry decision is touched anywhere in this loop.
- **`BUDGET_S = 222` is test infrastructure, not a tuned semantic constant** (precedent: `tests/etkl/test_derivation_perf.py`): derived from the measured 180 s whole-stem compile at loop-N close + ~23% headroom; R39 is the named perf slice that lowers it. Document the derivation at the constant.
- **Verdict discipline (spec §4):** the battery NEVER auto-updates the manifest. Measured outcomes go into task reports and the plan status note; François adjudicates every verdict change in a reviewed commit. If a measurement disagrees with an expectation: STOP, report the measured value — never lower a floor, never raise the budget yourself.
- **`corpus/` is gitignored; a corpus PDF is NEVER committed.** Check `git status` before every commit.
- **Canonical test command:** `./.venv/bin/python -m pytest` (bare `python3` = rdflib 7.1.4 → ~60 spurious SPARQL failures).
- **Suite baseline before this loop:** 803 passed / 5 skipped (non-corpus) + 10 corpus tests (`tests/test_corpus_stem.py`). Every task ends with the non-corpus suite green.
- **Git in this session:** the system `git` is broken (Xcode CLT dlopen failure) — use `/opt/homebrew/bin/git` for every git command. Branch: `corpus-harness` off `main`; default branch is `main`, never `master`.
- Commit messages end with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## File Structure

| File | Responsibility |
|---|---|
| `scripts/fetch_corpus.py` (modify) | Manifest-driven download: browser UA header, sha256 verify, first-fetch pinning report (prints sha256/producer/pages/date for a *deliberate* manifest edit). |
| `tests/test_fetch_corpus.py` (create) | Network-free unit battery for the fetcher (`download` injected). Not corpus-marked. |
| `tests/corpus-shapes.ttl` (create) | The register membrane: closed-world SHACL over `cor:Document`. |
| `tests/test_corpus_manifest.py` (create) | Always-on: the tracked manifest conforms; negative fixtures must fail (repo convention: every shape ships with a conforming example AND a negative test). |
| `tests/test_corpus.py` (create) | The manifest-driven battery (corpus-marked): verdict + budget + grounding-where-contracted + visible coverage count. Helpers importable (`from tests.test_corpus import …`). |
| `tests/test_corpus_battery_unit.py` (create) | Network-free unit battery for the battery's own logic, on a `simple_table_pdf` synthetic + tmp manifest. Not corpus-marked. |
| `tests/corpus-manifest.ttl` (modify) | Stem entry gains `cor:contract/terms/shapes`; six new `cor:Unadjudicated` seed entries (Tasks 4–7). |
| `docs/superpowers/residues.md` (modify, Task 8 only) | Rows for any defect the first battery run measures. |
| `docs/wiki/…` (modify, Task 8) | Corpus-harness concept page + index line (Doc impact increment). |

---

### Task 1: UA-header fetcher with first-fetch pinning

**Files:**
- Modify: `scripts/fetch_corpus.py`
- Test: `tests/test_fetch_corpus.py`

**Interfaces:**
- Produces: `fetch_one(g: Graph, doc, corpus_root: Path, download=_download) -> str` returning one of `"present" | "fetched" | "pin" | "mismatch" | "failed"`; `_download(url: str) -> bytes`; module constant `USER_AGENT: str`. Task 4–7 run the script CLI; nothing else imports it.

- [ ] **Step 1: Create the branch**

```bash
cd "/Volumes/WD Green/dev/git/iladub"
/opt/homebrew/bin/git checkout -b corpus-harness main
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_fetch_corpus.py`:

```python
"""scripts/fetch_corpus.py unit battery — network-free (`download` is injected)."""
import hashlib

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF, Graph

from scripts.fetch_corpus import COR, USER_AGENT, _download, fetch_one
from tests.etkl.fixtures import simple_table_pdf

ENTRY = """@prefix cor: <https://w3id.org/iladub/corpus#> .
<urn:t> a cor:Document ; cor:file "fam/doc.pdf" ;
    cor:url "https://example.org/doc.pdf" ; cor:family "health" ;
    cor:series "s" ; cor:expectedVerdict cor:Unadjudicated {pin}.
"""


def _graph(sha=None):
    pin = f'; cor:sha256 "{sha}" ' if sha else ""
    return Graph().parse(data=ENTRY.format(pin=pin), format="turtle")


def _doc(g):
    return next(g.subjects(RDF.type, COR.Document))


def _pdf_bytes(tmp_path):
    p = tmp_path / "src.pdf"
    simple_table_pdf(str(p))
    return p.read_bytes()


def test_first_fetch_pins_and_keeps(tmp_path, capsys):
    """No cor:sha256 yet -> the file is KEPT and the values to pin are PRINTED
    (never written back — spec §4 verdict discipline)."""
    data = _pdf_bytes(tmp_path)
    g = _graph()
    out = fetch_one(g, _doc(g), tmp_path / "corpus", download=lambda url: data)
    assert out == "pin"
    assert (tmp_path / "corpus" / "fam" / "doc.pdf").is_file()
    printed = capsys.readouterr().out
    assert hashlib.sha256(data).hexdigest() in printed
    assert "cor:pages 1" in printed


def test_matching_checksum_fetches(tmp_path):
    data = _pdf_bytes(tmp_path)
    g = _graph(hashlib.sha256(data).hexdigest())
    assert fetch_one(g, _doc(g), tmp_path / "corpus",
                     download=lambda url: data) == "fetched"
    assert (tmp_path / "corpus" / "fam" / "doc.pdf").read_bytes() == data


def test_mismatch_removes_file(tmp_path, capsys):
    data = _pdf_bytes(tmp_path)
    g = _graph("0" * 64)
    assert fetch_one(g, _doc(g), tmp_path / "corpus",
                     download=lambda url: data) == "mismatch"
    assert not (tmp_path / "corpus" / "fam" / "doc.pdf").exists()
    assert "MISMATCH" in capsys.readouterr().out


def test_present_short_circuits_network(tmp_path):
    g = _graph()
    dest = tmp_path / "corpus" / "fam" / "doc.pdf"
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b"x")

    def boom(url):
        raise AssertionError("network touched for a present file")

    assert fetch_one(g, _doc(g), tmp_path / "corpus", download=boom) == "present"


def test_fetch_failure_reported(tmp_path, capsys):
    g = _graph("0" * 64)

    def down(url):
        raise OSError("HTTP Error 403: Forbidden")

    assert fetch_one(g, _doc(g), tmp_path / "corpus", download=down) == "failed"
    assert "FETCH FAILED" in capsys.readouterr().out


def test_download_sends_browser_ua(monkeypatch):
    """GrainCorp's CDN 403s bare Python-urllib — the UA header is the whole point."""
    seen = {}

    class _Resp:
        def read(self):
            return b"pdf"

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(req):
        seen["ua"] = req.get_header("User-agent")
        return _Resp()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    assert _download("https://example.org/x.pdf") == b"pdf"
    assert seen["ua"] == USER_AGENT
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `./.venv/bin/python -m pytest tests/test_fetch_corpus.py -v`
Expected: FAIL / ImportError — `fetch_one`, `USER_AGENT`, `_download` do not exist yet (current script is one `main()`).

- [ ] **Step 4: Rewrite `scripts/fetch_corpus.py`**

Full replacement (keeps the existing docstring's contract, adds UA + pinning + testable seams):

```python
#!/usr/bin/env python
"""Corpus fetcher (spec 2026-08-02 §4) — justified PROCEDURAL: network + file I/O +
checksum, irreducible to AXIOM/NEURAL. Reads tests/corpus-manifest.ttl, downloads
absent documents into corpus/, verifies sha256. A checksum mismatch is REPORTED and
the file removed — the URL now serves a different edition; updating the manifest is a
deliberate, reviewed act.

First fetch of a fresh entry (no cor:sha256 yet): the file is KEPT and the values the
manifest needs (sha256, producer, pages, date) are PRINTED for a deliberate manifest
edit — never written back automatically (spec §4 verdict discipline). Exit is nonzero
until every entry is pinned and verified, so an unpinned register is always visible."""
from __future__ import annotations

import datetime
import hashlib
import urllib.request
from pathlib import Path

from rdflib import Graph, Namespace, RDF

REPO = Path(__file__).resolve().parent.parent
COR = Namespace("https://w3id.org/iladub/corpus#")

# Institutional CDNs/WAFs (GrainCorp's included — measured, loop L) return 403 to bare
# "Python-urllib". A plain desktop browser UA is enough; nothing else is spoofed.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def _pdf_facts(dest: Path) -> tuple[str | None, int]:
    import pdfplumber
    with pdfplumber.open(dest) as pdf:
        return (pdf.metadata or {}).get("Producer"), len(pdf.pages)


def fetch_one(g: Graph, doc, corpus_root: Path, download=_download) -> str:
    """One manifest document -> 'present'|'fetched'|'pin'|'mismatch'|'failed'."""
    rel, url = str(g.value(doc, COR.file)), str(g.value(doc, COR.url))
    want = g.value(doc, COR.sha256)
    dest = Path(corpus_root) / rel
    if dest.is_file():
        print(f"present  {rel}")
        return "present"
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"fetching {rel} <- {url}")
    try:
        data = download(url)
    except OSError as e:
        print(f"  FETCH FAILED ({e}) — URL may have rotted; document skipped")
        return "failed"
    dest.write_bytes(data)
    got = hashlib.sha256(data).hexdigest()
    if want is None:
        producer, pages = _pdf_facts(dest)
        print("  FIRST FETCH — pin these in tests/corpus-manifest.ttl "
              "(a deliberate edit, never automatic):")
        print(f'    cor:producer "{producer}" ;')
        print(f'    cor:fetched "{datetime.date.today().isoformat()}"^^xsd:date ;')
        print(f'    cor:sha256 "{got}" ;')
        print(f"    cor:pages {pages} ;")
        return "pin"
    if got != str(want):
        dest.unlink()
        print(f"  CHECKSUM MISMATCH (got {got[:12]}…) — a different edition now "
              f"lives at this URL; file removed, manifest unchanged")
        return "mismatch"
    print(f"  ok ({got[:12]}…)")
    return "fetched"


def main() -> int:
    g = Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle")
    outcomes = [fetch_one(g, doc, REPO / "corpus")
                for doc in g.subjects(RDF.type, COR.Document)]
    return 1 if any(o in ("mismatch", "failed", "pin") for o in outcomes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `./.venv/bin/python -m pytest tests/test_fetch_corpus.py -v`
Expected: 6 PASS.

- [ ] **Step 6: Real-world smoke: the stem still fetches (or is present)**

Run: `./.venv/bin/python scripts/fetch_corpus.py`
Expected: `present  ag-trade/graincorp-stem-2026-07-31.pdf` (it is on disk), exit 0. If the file were absent, the UA header must get past the CDN that 403'd plain urllib — do NOT delete the local stem to force this; the header is unit-proven.

- [ ] **Step 7: Full non-corpus suite green, then commit**

Run: `./.venv/bin/python -m pytest -m "not corpus" -q`
Expected: 803 + 6 = 809 passed / 5 skipped.

```bash
/opt/homebrew/bin/git add scripts/fetch_corpus.py tests/test_fetch_corpus.py
/opt/homebrew/bin/git commit -m "feat(corpus): UA-header fetcher with first-fetch pinning (spec §4)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: The register membrane (SHACL over the manifest)

**Files:**
- Create: `tests/corpus-shapes.ttl`
- Test: `tests/test_corpus_manifest.py`

**Interfaces:**
- Consumes: the tracked `tests/corpus-manifest.ttl`.
- Produces: `tests/corpus-shapes.ttl` (Task 3's battery does not read it, but Tasks 4–7's manifest edits must keep `test_corpus_manifest.py` green — it is always-on, not corpus-marked).

- [ ] **Step 1: Write the failing test**

Create `tests/test_corpus_manifest.py`:

```python
"""The corpus register's membrane (spec 2026-08-02 §4): the tracked manifest conforms
to tests/corpus-shapes.ttl. Always-on — the register is tracked; no network, no corpus/.
Closed-world constraint side of the §8 split: the membrane validates what may enter the
battery; it derives nothing."""
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tests" / "corpus-manifest.ttl"
SHAPES = REPO / "tests" / "corpus-shapes.ttl"

PREFIXES = """@prefix cor: <https://w3id.org/iladub/corpus#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

BASE = ('<urn:x> a cor:Document ; cor:file "f.pdf" ; cor:url "https://example.org/f" ; '
        'cor:series "s" ')


def _conforms(data: Graph):
    ok, _, report = validate(
        data, shacl_graph=Graph().parse(SHAPES, format="turtle"),
        inference="rdfs", advanced=True)
    return ok, report


def _neg(ttl: str):
    ok, report = _conforms(Graph().parse(data=PREFIXES + ttl, format="turtle"))
    assert not ok, f"membrane failed to refuse:\n{ttl}"


def test_manifest_conforms():
    ok, report = _conforms(Graph().parse(MANIFEST, format="turtle"))
    assert ok, report


def test_refuses_compilesabove_without_floor():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:CompilesAbove ; '
         'cor:sha256 "%s" ; cor:adjudication [ cor:by "x" ] .' % ("0" * 64))


def test_refuses_unknown_family():
    _neg(BASE + '; cor:family "crypto" ; cor:expectedVerdict cor:Unadjudicated .')


def test_refuses_adjudicated_verdict_without_pin():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:SemanticEscalation ; '
         'cor:ambiguity "which header row" ; cor:adjudication [ cor:by "x" ] .')


def test_refuses_escalation_without_named_ambiguity():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:SemanticEscalation ; '
         'cor:sha256 "%s" ; cor:adjudication [ cor:by "x" ] .' % ("0" * 64))


def test_refuses_partial_contract_triple():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
         'cor:contract "examples/x.ttl" .')


def test_refuses_malformed_sha256():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
         'cor:sha256 "not-a-hash" .')
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `./.venv/bin/python -m pytest tests/test_corpus_manifest.py -v`
Expected: ERROR — `tests/corpus-shapes.ttl` does not exist.

- [ ] **Step 3: Write the shapes**

Create `tests/corpus-shapes.ttl` (copy the `sh:declare` pattern from `vocab/shapes/etkl-shapes.ttl`):

```turtle
# tests/corpus-shapes.ttl — membrane over the corpus register (spec 2026-08-02 §4).
# cor: is repo-internal (like dg:) — not published, not w3id-registered. The shape
# guards the REGISTER's integrity before a 3-minute compile trusts it; it never
# validates the corpus documents themselves. Closed-world constraint (§8 split).
@prefix sh:  <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix cor: <https://w3id.org/iladub/corpus#> .

cor:prefixes sh:declare [ sh:prefix "cor" ;
    sh:namespace "https://w3id.org/iladub/corpus#"^^xsd:anyURI ] .

cor:DocumentShape a sh:NodeShape ;
    sh:targetClass cor:Document ;
    sh:property [ sh:path cor:file ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path cor:url ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path cor:family ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:in ("ag-trade" "gov-stats" "financial" "health") ] ;
    sh:property [ sh:path cor:series ; sh:minCount 1 ; sh:maxCount 1 ] ;
    sh:property [ sh:path cor:expectedVerdict ; sh:minCount 1 ; sh:maxCount 1 ;
                  sh:in (cor:CompilesAbove cor:SemanticEscalation cor:Unadjudicated) ] ;
    sh:property [ sh:path cor:sha256 ; sh:maxCount 1 ;
                  sh:pattern "^[0-9a-f]{64}$" ] ;
    sh:property [ sh:path cor:scoreFloor ; sh:maxCount 1 ; sh:datatype xsd:decimal ] ;
    sh:property [ sh:path cor:pages ; sh:maxCount 1 ; sh:datatype xsd:integer ] ;
    sh:property [ sh:path cor:contract ; sh:maxCount 1 ] ;
    sh:property [ sh:path cor:terms ; sh:maxCount 1 ] ;
    sh:property [ sh:path cor:shapes ; sh:maxCount 1 ] ;
    sh:sparql [
        sh:message "cor:CompilesAbove requires exactly one cor:scoreFloor" ;
        sh:prefixes cor:prefixes ;
        sh:select """SELECT $this WHERE {
            $this cor:expectedVerdict cor:CompilesAbove .
            FILTER NOT EXISTS { $this cor:scoreFloor ?f } }""" ] ;
    sh:sparql [
        sh:message "cor:SemanticEscalation requires cor:ambiguity naming it in prose" ;
        sh:prefixes cor:prefixes ;
        sh:select """SELECT $this WHERE {
            $this cor:expectedVerdict cor:SemanticEscalation .
            FILTER NOT EXISTS { $this cor:ambiguity ?a } }""" ] ;
    sh:sparql [
        sh:message "an adjudicated verdict requires a pinned edition (cor:sha256) and a recorded cor:adjudication" ;
        sh:prefixes cor:prefixes ;
        sh:select """SELECT $this WHERE {
            $this cor:expectedVerdict ?v .
            FILTER(?v != cor:Unadjudicated)
            FILTER(NOT EXISTS { $this cor:sha256 ?s } ||
                   NOT EXISTS { $this cor:adjudication ?a }) }""" ] ;
    sh:sparql [
        sh:message "cor:contract / cor:terms / cor:shapes travel together (all or none)" ;
        sh:prefixes cor:prefixes ;
        sh:select """SELECT $this WHERE {
            { $this cor:contract ?x } UNION { $this cor:terms ?x }
            UNION { $this cor:shapes ?x }
            FILTER(NOT EXISTS { $this cor:contract ?c } ||
                   NOT EXISTS { $this cor:terms ?t } ||
                   NOT EXISTS { $this cor:shapes ?p }) }""" ] .
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `./.venv/bin/python -m pytest tests/test_corpus_manifest.py -v`
Expected: 7 PASS (the real manifest conforms — the stem entry has verdict CompilesAbove + floor + sha + 3 adjudications).

- [ ] **Step 5: Full non-corpus suite green, then commit**

Run: `./.venv/bin/python -m pytest -m "not corpus" -q`
Expected: 816 passed / 5 skipped.

```bash
/opt/homebrew/bin/git add tests/corpus-shapes.ttl tests/test_corpus_manifest.py
/opt/homebrew/bin/git commit -m "feat(corpus): SHACL membrane over the corpus register + negative battery

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: The manifest-driven battery (`tests/test_corpus.py`)

**Files:**
- Create: `tests/test_corpus.py`
- Create: `tests/test_corpus_battery_unit.py`
- Modify: `tests/corpus-manifest.ttl` (stem entry gains `cor:contract/terms/shapes`)

**Interfaces:**
- Consumes: `scripts/fetch_corpus.py` populated `corpus/`; manifest semantics from Task 2's membrane.
- Produces: `manifest_entries(manifest_path) -> list[dict]` (keys: `iri, file, sha256, verdict, floor, contract, terms, shapes`), `require_pinned_edition(entry, corpus_root) -> Path`, `check_verdict(rep, entry) -> list`, `_compiled(path: str) -> (DocumentReport, float)`, constants `COR`, `BUDGET_S` — all importable as `from tests.test_corpus import …` (tests is a package, `pythonpath=["."]`). Tasks 4–8 run this battery.

- [ ] **Step 1: Write the failing unit tests**

Create `tests/test_corpus_battery_unit.py`:

```python
"""Battery-logic unit battery — network-free, corpus-free: exercises the helpers in
tests/test_corpus.py on a synthetic reportlab document + a tmp manifest. The real
battery (corpus-marked) reuses exactly these helpers, so verdict semantics are proven
without a single fetch."""
import hashlib

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import Graph

from tests.etkl.fixtures import simple_table_pdf
from tests.test_corpus import (COR, check_verdict, manifest_entries,
                               require_pinned_edition, _compiled)

MANIFEST = """@prefix cor: <https://w3id.org/iladub/corpus#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
<urn:t> a cor:Document ; cor:file "synthetic/cbc.pdf" ; cor:url "urn:none" ;
    cor:family "health" ; cor:series "synthetic-cbc" ;
    cor:expectedVerdict {verdict} ; {extra}
    cor:sha256 "{sha}" .
"""


def _seed(tmp_path, sha=None, verdict="cor:Unadjudicated", extra=""):
    pdf = tmp_path / "synthetic" / "cbc.pdf"
    pdf.parent.mkdir(parents=True)
    simple_table_pdf(str(pdf))
    real = hashlib.sha256(pdf.read_bytes()).hexdigest()
    m = tmp_path / "manifest.ttl"
    m.write_text(MANIFEST.format(sha=sha or real, verdict=verdict, extra=extra))
    return m, tmp_path


def test_compilesabove_passes_on_synthetic(tmp_path):
    # Floor 0.5 for a clean synthetic 3-column table. If this fixture measures below
    # 0.5, report the measured score and set the floor at-or-below it (synthetic
    # fixture calibration, not a real-document verdict).
    m, root = _seed(tmp_path, verdict="cor:CompilesAbove",
                    extra='cor:scoreFloor "0.5"^^xsd:decimal ;')
    [entry] = manifest_entries(m)
    dest = require_pinned_edition(entry, root)
    rep, dt = _compiled(str(dest))
    check_verdict(rep, entry)          # must not raise
    assert dt >= 0.0


def test_unadjudicated_measures_without_gating(tmp_path):
    m, root = _seed(tmp_path)
    [entry] = manifest_entries(m)
    rep, _ = _compiled(str(require_pinned_edition(entry, root)))
    verdicts = check_verdict(rep, entry)   # no assertion beyond non-crash
    assert isinstance(verdicts, list) and verdicts


def test_absent_document_skips(tmp_path):
    m, root = _seed(tmp_path)
    [entry] = manifest_entries(m)
    (root / entry["file"]).unlink()
    with pytest.raises(pytest.skip.Exception):
        require_pinned_edition(entry, root)


def test_unpinned_document_skips(tmp_path):
    m, root = _seed(tmp_path)
    text = m.read_text()
    m.write_text(text[: text.rindex("cor:sha256")].rstrip().rstrip(";") + " .\n")
    [entry] = manifest_entries(m)
    assert entry["sha256"] is None
    with pytest.raises(pytest.skip.Exception):
        require_pinned_edition(entry, root)


def test_edition_drift_fails_not_skips(tmp_path):
    m, root = _seed(tmp_path, sha="0" * 64)
    [entry] = manifest_entries(m)
    with pytest.raises(AssertionError, match="pinned"):
        require_pinned_edition(entry, root)
```

- [ ] **Step 2: Run unit tests to verify they fail**

Run: `./.venv/bin/python -m pytest tests/test_corpus_battery_unit.py -v`
Expected: ImportError — `tests/test_corpus.py` does not exist.

- [ ] **Step 3: Write the battery**

Create `tests/test_corpus.py`:

```python
"""The manifest-driven corpus battery (spec 2026-08-02 §4): for every manifest
document present in corpus/, compile through the PUBLIC document API and assert the
manifest's expected verdict. Absent documents SKIP visibly; the battery never edits
the manifest (verdict discipline — a verdict change is a measured event a loop
records in a reviewed commit). Engine glue is justified PROCEDURAL (§8).

Run locally: ./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -s
"""
import functools
import hashlib
import signal
import time
from pathlib import Path

import pytest
from rdflib import Graph, Namespace, RDF

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "corpus"
COR = Namespace("https://w3id.org/iladub/corpus#")

pytestmark = pytest.mark.corpus

# Wall-clock ceiling per document — test infrastructure, not a tuned semantic
# constant (precedent: tests/etkl/test_derivation_perf.py). Derivation (measured):
# the whole 3-page stem compile cost 180 s at loop-N close
# (tests/test_corpus_stem.py::stem_document) + ~23% headroom. Under the
# fluent-reader invariant (spec §2) a HANG is a harness defect — the alarm turns it
# into a visible failure. R39 (row-group-nesting.rq, ~93 s of that budget) is the
# named perf slice that will lower this. Never raise it to make a document pass:
# report the overrun instead.
BUDGET_S = 222


def manifest_entries(manifest_path):
    """The register, read as the oracle it is: one dict per cor:Document."""
    g = Graph().parse(manifest_path, format="turtle")
    out = []
    for doc in g.subjects(RDF.type, COR.Document):
        def v(p):
            return g.value(doc, p)
        out.append({
            "iri": str(doc),
            "file": str(v(COR.file)),
            "sha256": str(v(COR.sha256)) if v(COR.sha256) is not None else None,
            "verdict": v(COR.expectedVerdict),
            "floor": float(v(COR.scoreFloor)) if v(COR.scoreFloor) is not None else None,
            "contract": str(v(COR.contract)) if v(COR.contract) is not None else None,
            "terms": str(v(COR.terms)) if v(COR.terms) is not None else None,
            "shapes": str(v(COR.shapes)) if v(COR.shapes) is not None else None,
        })
    return sorted(out, key=lambda e: e["file"])


ENTRIES = manifest_entries(REPO / "tests" / "corpus-manifest.ttl")


def require_pinned_edition(entry, corpus_root):
    """Skip (absent / unpinned) or FAIL (edition drift); returns the on-disk path.
    Drift fails rather than skips: measuring an unpinned edition would silently
    decouple the register from the evidence."""
    dest = Path(corpus_root) / entry["file"]
    if not dest.is_file():
        pytest.skip(f"corpus not populated: {entry['file']} (scripts/fetch_corpus.py)")
    if entry["sha256"] is None:
        pytest.skip(f"unpinned edition: {entry['file']} (first fetch, then pin cor:sha256)")
    got = hashlib.sha256(dest.read_bytes()).hexdigest()
    assert got == entry["sha256"], (
        f"{entry['file']}: on-disk edition {got[:12]}… is not the pinned "
        f"{entry['sha256'][:12]}… — refetch, or pin the new edition in a reviewed commit")
    return dest


class _alarm:
    """SIGALRM budget guard (pytest runs us in the main thread)."""

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._fire)
        signal.alarm(BUDGET_S)

    def _fire(self, *_):
        raise AssertionError(
            f"BUDGET EXCEEDED: compile ran past {BUDGET_S}s (R39 family) — "
            f"report the overrun; do not raise the budget")

    def __exit__(self, *_):
        signal.alarm(0)


@functools.lru_cache(maxsize=None)
def _compiled(path: str):
    """One compile per document per session: the stem alone costs ~180 s and the
    grounding test reads the same frozen DocumentReport (loop-M F7 precedent —
    ground_document writes into a caller-supplied graph, never the source)."""
    from iladub.etkl.document import compile_document
    t0 = time.monotonic()
    with _alarm():
        rep = compile_document(path)
    return rep, time.monotonic() - t0


def check_verdict(rep, entry):
    """Assert the manifest's expected verdict against a DocumentReport; returns the
    per-region verdict tuples for the caller's print."""
    verdicts = [(r.kind.name, r.verdict, r.reason)
                for p in rep.pages for r in p.regions]
    if entry["verdict"] == COR.CompilesAbove:
        assert rep.score >= entry["floor"], (
            f"score {rep.score:.4f} < floor {entry['floor']} — do NOT lower the "
            f"floor; report the measured score (Global Constraints)")
        assert any(r.verdict == "asserted"
                   for p in rep.pages for r in p.regions), verdicts
    elif entry["verdict"] == COR.SemanticEscalation:
        assert any(r.verdict == "escalated"
                   for p in rep.pages for r in p.regions), verdicts
    # cor:Unadjudicated: compile returning AT ALL is the gate (never crash, never
    # hang); the printed measurement is adjudication evidence, asserted by no one here.
    return verdicts


@pytest.mark.parametrize("entry", ENTRIES, ids=[e["file"] for e in ENTRIES])
def test_expected_verdict(entry):
    dest = require_pinned_edition(entry, CORPUS)
    rep, dt = _compiled(str(dest))
    verdicts = check_verdict(rep, entry)
    print(f"\n{entry['file']}: score={rep.score:.4f} pages={len(rep.pages)} "
          f"chains={[len(c) for c in rep.chains]} wall={dt:.0f}s")
    if entry["verdict"] == COR.Unadjudicated:
        print(f"  UNADJUDICATED — regions: {verdicts}")


@pytest.mark.parametrize(
    "entry", [e for e in ENTRIES if e["contract"]],
    ids=[e["file"] for e in ENTRIES if e["contract"]])
def test_grounding_where_contracted(entry):
    """Spec §4: '+ grounding where a contract exists'. The §3 invariant is the gate:
    every grounded node behind exactly one accountable promotion."""
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

    ILADUB = Namespace("https://w3id.org/iladub#")
    dest = require_pinned_edition(entry, CORPUS)
    rep, _ = _compiled(str(dest))
    contract = load_contract(str(REPO / entry["contract"]))
    terms = Graph().parse(str(REPO / entry["terms"]), format="turtle")
    shapes = Graph().parse(str(REPO / entry["shapes"]), format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, "https://example.org/shipping#x", 0.1, "n/a",
        "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(rep.graph, contract, abstain, terms, shapes, g)
    grounded = list(g.subjects(RDF.type, ILADUB.GroundedNode))
    print(f"\n{entry['file']}: records={result.records} grounded={len(grounded)} "
          f"still-quarantined={result.proposed}")
    assert grounded, "a contracted document must ground SOMETHING"
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1


def test_corpus_coverage_report():
    """Spec §4: absent documents skip WITH A VISIBLE COUNT — this is the count."""
    present = [e["file"] for e in ENTRIES if (CORPUS / e["file"]).is_file()]
    absent = [e["file"] for e in ENTRIES if not (CORPUS / e["file"]).is_file()]
    print(f"\ncorpus coverage: {len(present)}/{len(ENTRIES)} present; absent: {absent}")
```

- [ ] **Step 4: Run the unit battery to verify it passes**

Run: `./.venv/bin/python -m pytest tests/test_corpus_battery_unit.py -v`
Expected: 5 PASS. If `test_compilesabove_passes_on_synthetic` fails on the floor: print the measured score, set the synthetic floor at-or-below it (calibration of a synthetic fixture, allowed), re-run.

- [ ] **Step 5: Declare the stem's contract in the manifest**

In `tests/corpus-manifest.ttl`, add to the `<urn:iladub:corpus:graincorp-stem-2026-07-31>` entry (before the adjudication list, keeping Turtle valid):

```turtle
    cor:contract "examples/shipping/stem-contract.ttl" ;
    cor:terms "examples/shipping/stem-terms.ttl" ;
    cor:shapes "examples/shipping/stem-shapes.ttl" ;
```

Run: `./.venv/bin/python -m pytest tests/test_corpus_manifest.py -q`
Expected: 7 passed (the membrane's all-or-none contract rule is satisfied).

- [ ] **Step 6: Run the real battery on the stem**

Run: `./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -v -s`
Expected: `test_expected_verdict[ag-trade/graincorp-stem-2026-07-31.pdf]` PASS (score ≥ 0.95, within 222 s), `test_grounding_where_contracted[...]` PASS, coverage report prints `1/1 present`. Record the printed score/wall in the task report. This costs ~3–4 minutes — run it in the foreground; do NOT background it (known SDD stall pattern).

- [ ] **Step 7: Full non-corpus suite green, then commit**

Run: `./.venv/bin/python -m pytest -m "not corpus" -q`
Expected: 821 passed / 5 skipped (816 + 5 unit tests; the corpus-marked battery is excluded by the marker).

```bash
/opt/homebrew/bin/git add tests/test_corpus.py tests/test_corpus_battery_unit.py tests/corpus-manifest.ttl
/opt/homebrew/bin/git commit -m "feat(corpus): manifest-driven battery — verdict oracle, 222s budget, grounding-where-contracted

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Tasks 4–7: Seed the six remaining documents

**Shared mechanics for every document (referenced by each task below — follow verbatim):**

1. **Discover** a live URL with `curl` using the fetcher's UA (`curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" -sIL <url>` to probe; follow the candidate pages listed in the task). Selection criteria (spec §5): a real tabular PDF, stable institutional URL preferred, and for gov-stats/financial specifically hierarchical headers + subtotals. Prefer compact documents (≲ 10 pages) — the 222 s budget is per document. **URLs rot in days** (measured, loop L): if a candidate 403s/404s even with the UA, substitute another document meeting the same criteria and record the substitution in the plan status note.
2. **Add a stub manifest entry** to `tests/corpus-manifest.ttl` — `a cor:Document` with `cor:file "<family>/<slug>.pdf"`, `cor:url`, `cor:family`, `cor:series`, `cor:expectedVerdict cor:Unadjudicated` — no sha256 yet.
3. Run `./.venv/bin/python scripts/fetch_corpus.py` → expect the `FIRST FETCH — pin these` block. **Copy the printed `cor:producer` / `cor:fetched` / `cor:sha256` / `cor:pages` lines into the entry by hand** (the deliberate edit).
4. Re-run the fetcher → the document must now report `ok`/`present` and exit 0 (for the entries so far).
5. Validate the register: `./.venv/bin/python -m pytest tests/test_corpus_manifest.py -q` → green.
6. **Measure**: `./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -v -s -k "<slug>"` — foreground, never backgrounded. The Unadjudicated gate is compile-returns-without-crash-or-hang; whatever it prints (score, per-region verdicts, escalation reasons, wall seconds) is the adjudication evidence — **copy it verbatim into the plan status note and the task report. Do not change any `cor:expectedVerdict`** — François adjudicates in Task 8's report. A crash, a hang past 222 s, or an obviously non-semantic escalation is a MEASURED DEFECT: record it (it becomes its own loop), do not fix it here.
7. **Commit the manifest edit only** (`/opt/homebrew/bin/git add tests/corpus-manifest.ttl` — verify `git status` shows no `corpus/` file staged; `corpus/` is gitignored, keep it that way).

### Task 4: ag-trade seeds — GrainCorp Capacity + CBH shipping stem

**Files:**
- Modify: `tests/corpus-manifest.ttl` (2 new entries)

**Interfaces:**
- Consumes: `scripts/fetch_corpus.py` CLI (Task 1), battery `-k` runs (Task 3).
- Produces: `corpus/ag-trade/graincorp-capacity-<date>.pdf` + `corpus/ag-trade/cbh-stem-<date>.pdf` locally; two pinned `cor:Unadjudicated` entries.

- [ ] **Step 1: GrainCorp Capacity** — discovery starts at the page that links the shipping stem (`https://grains.graincorp.com.au/` — the stem URL pattern is `wp-content/uploads/.../Shipping-Stem-<date>.pdf`; look for the sibling "Port Capacity"/"Capacity" PDF link on the same page). `cor:series "graincorp-capacity"`, `cor:file "ag-trade/graincorp-capacity-<date>.pdf"`. Follow shared mechanics 2–7.
- [ ] **Step 2: CBH shipping stem** — discovery at `https://www.cbh.com.au` (search the site for "shipping stem"; CBH publishes a current-edition stem PDF). `cor:series "cbh-shipping-stem"`, `cor:file "ag-trade/cbh-stem-<date>.pdf"`. Follow shared mechanics 2–7.
- [ ] **Step 3: Commit** (message: `feat(corpus): seed ag-trade — GrainCorp capacity + CBH stem (Unadjudicated, measured)` + trailer).

### Task 5: gov-stats seeds — one ABS table + one Eurostat/BFS table

**Files:**
- Modify: `tests/corpus-manifest.ttl` (2 new entries)

**Interfaces:** same as Task 4; files land under `corpus/gov-stats/`.

- [ ] **Step 1: ABS release table** — a PDF release table from `https://www.abs.gov.au` with hierarchical headers + subtotals (many ABS releases are xlsx/web-only — pick one that ships a PDF table; if none suits, substitute another national-statistics PDF, e.g. ONS/BLS, and record the substitution). `cor:series` names the release series. Follow shared mechanics 2–7.
- [ ] **Step 2: Eurostat/BFS table** — prefer BFS (Swiss FSO): `https://www.bfs.admin.ch` DAM asset URLs (`dam-api.bfs.admin.ch/hub/api/dam/assets/<id>/master`) are stable; pick a compact statistical table PDF with hierarchical headers. Alternatively a Eurostat PDF table. Follow shared mechanics 2–7.
- [ ] **Step 3: Commit** (message: `feat(corpus): seed gov-stats — ABS + BFS tables (Unadjudicated, measured)` + trailer).

### Task 6: financial seed — annual-report financial-statements extract

**Files:**
- Modify: `tests/corpus-manifest.ttl` (1 new entry)

**Interfaces:** same as Task 4; file lands under `corpus/financial/`.

- [ ] **Step 1:** One public annual-report **financial-statements extract** (nested subtotal ladder, multi-year comparatives — spec §5). Prefer a standalone "Financial Statements" or condensed interim-statements PDF over a full 200-page annual report: the 222 s budget is per document, and a whole report would measure the harness, not the reading. If the compile overruns the budget anyway, that IS the measurement — record it against R39 and leave the entry Unadjudicated. Follow shared mechanics 1–7.
- [ ] **Step 2: Commit** (message: `feat(corpus): seed financial — statements extract (Unadjudicated, measured)` + trailer).

### Task 7: health seed — WHO / public clinical reference table

**Files:**
- Modify: `tests/corpus-manifest.ttl` (1 new entry)

**Interfaces:** same as Task 4; file lands under `corpus/health/`.

- [ ] **Step 1:** A WHO or comparable public clinical reference table PDF (keeps the neutral-domain family exercised — spec §5; candidates: a WHO growth-reference z-score table extract, an essential-medicines list table). Compact (≲ 10 pages) preferred. Synthetic-examples rule (CLAUDE.md open items) applies to *committed examples*, not the gitignored corpus — but still prefer reference tables over anything patient-derived. Follow shared mechanics 1–7.
- [ ] **Step 2: Commit** (message: `feat(corpus): seed health — WHO reference table (Unadjudicated, measured)` + trailer).

---

### Task 8: Full battery evidence, adjudication table, residues, wiki increment

**Files:**
- Modify: `docs/superpowers/plans/2026-08-04-corpus-harness.md` (status note)
- Modify: `docs/superpowers/residues.md` (rows for measured defects only)
- Create: `docs/wiki/concepts/corpus-harness.md` (+ its line in the wiki index — follow the existing wiki page frontmatter/`sources:` convention; cite spec §4, `tests/test_corpus.py`, `scripts/fetch_corpus.py`; confidence-tagged as a proposition)

**Interfaces:**
- Consumes: everything above.
- Produces: the loop-close evidence + the adjudication request for François.

- [ ] **Step 1: Full non-corpus suite** — `./.venv/bin/python -m pytest -m "not corpus" -q`. Expected: 821 passed / 5 skipped (or the corrected tally from earlier tasks). Record the exact number.
- [ ] **Step 2: Full corpus battery** — `./.venv/bin/python -m pytest -m corpus -v -s` (foreground; expect ~10–20 min: the stem's ~3 min + six first compiles). Expected: 10 stem tests + 7 verdict tests + ≥1 grounding test + coverage report `7/7 present`. Record every printed measurement.
- [ ] **Step 3: Write the adjudication table** into this plan's status note and the final report — one row per document: file, family, pages, wall s, score, chains, region verdicts/escalation reasons, and a one-line proposed adjudication (e.g. "compiles 0.97 — propose CompilesAbove floor 0.95" or "escalates on X — propose SemanticEscalation / new loop"). **Do not edit any manifest verdict** — that is François's reviewed commit, exactly as the stem's three adjudication notes were.
- [ ] **Step 4: Register residues** — one row in `docs/superpowers/residues.md` per measured defect (crash class, budget overrun, non-semantic escalation), each citing where it was *measured* (the battery output) and what would close it. Grep the register first for existing corpus/fetch rows to update instead of duplicating. Do NOT fix any defect in this loop — each becomes its own loop (spec §5: "Each defect the battery reveals becomes its own loop").
- [ ] **Step 5: Wiki increment** — write `docs/wiki/concepts/corpus-harness.md` (the fetch → pin → measure → adjudicate workflow, the verdict semantics, the budget's derivation, the never-auto-update discipline) and add its index line. Run `./.venv/bin/python -m pytest tests/test_doc_governance.py -q` — the doc-governance membrane must stay green.
- [ ] **Step 6: Final suite + commit** — both suites green; commit docs (`docs/…` + any residue rows) with trailer. Then use superpowers:finishing-a-development-branch (PR `corpus-harness` → `main` via `gh`, `/opt/homebrew/bin/git`).

---

## Self-review (done at plan time)

- **Spec §4 coverage:** gitignored `corpus/` (pre-existing, verified), tracked manifest ✓ (extended T3–T7), fetch script ✓ T1, `test_corpus.py` + skip-with-visible-count ✓ T3, marker ✓ (already in `pyproject.toml`), verdict discipline ✓ (Global Constraints + T8), grounding-where-contract ✓ T3. Spec §5 seven seed docs: stem (present) + 2 ag-trade (T4) + 2 gov-stats (T5) + 1 financial (T6) + 1 health (T7) = 7 ✓. Budget ~222 s ✓ T3 (derivation documented at the constant).
- **Known open risks, stated honestly:** (a) region-verdict string literals `"asserted"`/`"escalated"` — `tests/test_corpus_stem.py:25` already tests against `"escalated"`, so the strings are the shipped public surface; (b) `simple_table_pdf`'s document-level score is unmeasured — the unit test carries an explicit calibration instruction; (c) discovery URLs in T4–T7 are candidates, not facts — the substitution rule covers rot; (d) expected suite tallies assume no collection surprises — the canonical baseline is "previous tally + new tests", and any drift must be investigated, not absorbed.
- **Type consistency:** `fetch_one` return strings match between T1 code and tests; `manifest_entries` dict keys match every consumer; `check_verdict` returns the verdict list used by both battery and unit tests; `_compiled` returns `(rep, seconds)` everywhere.

---

## Status note (loop close, 2026-08-04)

Task 8 closes the loop. Steps 1–2 (full suites) were run once by the controller and are
recorded here verbatim; Steps 3–6 (adjudication table, residues, wiki, commit) are this task.

### Suite tallies

- **Non-corpus suite** (`./.venv/bin/python -m pytest -m "not corpus" -q`, unchanged code since
  Task 3): **820 passed / 5 skipped** + 1 scrubbed-env `release_gate` failure — environmental
  (the broken system `git`, not a code regression) — so the healthy-environment tally is
  **821 passed / 5 skipped**, matching Task 3's expectation.
- **Corpus battery** (`./.venv/bin/python -m pytest -m corpus -v -s`, `battery-run-final.log`,
  644.58 s total): **18 passed / 1 failed** — 10 stem tests (`test_corpus_stem.py`, all pass,
  numbers unchanged: 0.9655 / 2152 cells / 133 records / 585 grounded / 1265 quarantined /
  missing-year-key 0) + 7 `test_expected_verdict` (6 pass, 1 honest red — see below) + 1
  `test_grounding_where_contracted` (stem, pass) + 1 `test_corpus_coverage_report` (`7/7 present,
  absent: []`). The one failure is the **honest driver**: the Apple statements document crashes
  the compiler (measured defect, not a harness bug) — see the adjudication table and R41 below.

### Adjudication table (PROPOSALS for François — no manifest verdict has been changed)

| Document | Family | Pages | Wall | Score | Chains | Measured outcome | Proposed adjudication |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ag-trade/graincorp-stem-2026-07-31.pdf` | ag-trade | 3 | 232 s | 0.9655 | `[3]` | PASS `CompilesAbove` (floor 0.95); chain of 3; grounding 133 records / 585 grounded / 1265 still-quarantined | Already `CompilesAbove` 0.95 — re-verified, no change |
| `ag-trade/graincorp-capacity-2026-08-04.pdf` | ag-trade | 1 | 11 s | 1.0000 | `[1]` | Compiles clean — 1 asserted `RECORD_TABLE` | PROPOSE `CompilesAbove`, floor 0.95 (measured 1.0000) |
| `ag-trade/cbh-stem-2026-08-03.pdf` | ag-trade | 1 | 9 s | 0.0698 | `[1]` | 4/5 regions escalate `MERGE_AMBIGUOUS` (Excel-print stem, different house style) | PROPOSE keep `Unadjudicated` — defect-loop candidate (merged-header house style); see R42 |
| `gov-stats/ons-index-of-services-2026-02.pdf` | gov-stats | 9 | 6 s | 0.4419 | `[1]` | 1× `REGION_TILING_FAILED`; oddity: one region prints `('UNSUPPORTED_TABLE', 'asserted', None)` — an UNSUPPORTED kind carrying an `asserted` verdict | PROPOSE keep `Unadjudicated` — generalization-gap loop candidate (tiling); see R43 |
| `gov-stats/bfs-population-bilan-2023.pdf` | gov-stats | 7 | 23 s | 0.3438 | `[1, 1, 1, 1, 1, 1, 1]` | 2× `KIND_NOT_SUPPORTED`, 2× `REGION_TILING_FAILED`, 5× `ROUND_TRIP_FAIL`; 8 `RECORD_TABLE` regions assert | PROPOSE keep `Unadjudicated` — generalization-gap loop candidate (kind support / round-trip); see R44 |
| `financial/apple-fy2026q3-statements.pdf` | financial | 3 | 7 s | CRASH | — (crashed before a report) | `IndexError: tuple index out of range` at `src/iladub/etkl/headers.py:400` in `header_rows_of` (`band.lines[body_line].top`, `body_line=7` > `len(band.lines)`); trigger: a segment-footnote sub-table. Battery test RED — the honest state (fluent-reader invariant violation, crash class) | PROPOSE keep `Unadjudicated` — CRASH-loop candidate (`headers.py:400` bound check); battery stays red until that loop lands, or François substitutes the doc; see R41 |
| `health/who-wfa-boys-zscore-0-5.pdf` | health | 3 | 45 s | 0.5597 | `[1, 1, 1, 1, 1, 1, 1]` | 3× `MATRIX_AMBIGUOUS` on the dense age × z-score matrix | PROPOSE keep `Unadjudicated` — generalization-gap loop candidate (matrix ambiguity); see R45 |

### BUDGET_S adjudication history

`BUDGET_S` started this loop stale at **222 s** (carried from loop N's 180 s whole-stem compile +
~23% headroom, documented at the constant in `tests/test_corpus.py`). Measured this loop: **254.1 s**
standalone stem compile / **270 s** in-battery / **232 s** in this final run. **François adjudicated
the budget to 320 s** — the constant has not been edited in this task (code-file edit is out of
scope for Task 8); the adjudicated value is recorded here as the loop-close evidence for whichever
loop next touches `tests/test_corpus.py`.

### ABS → ONS substitution (Task 5)

ABS (Australian Bureau of Statistics) release tables ship as xlsx/web-only for the candidates
surveyed — no suitable PDF table was found. Substituted with ONS (UK Office for National
Statistics) `Index of Services` PDF, recorded in-manifest (`cor:series "ons-index-of-services"`),
per the shared-mechanics substitution rule (URLs/format availability rot; substitute another
document meeting the same family criteria and record it here).
