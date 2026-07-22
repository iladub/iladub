# ET(K)L OCR First Mile — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a scanned / image-only PDF (no text layer) compile end-to-end through the existing `compile_tables` pipeline by supplying `Word`s from a faithful OCR transcriber, with OCR as an optional dependency and a single integration seam in `extract_words`.

**Architecture:** New `src/iladub/etkl/ocr.py` renders a page with `pypdfium2`, transcribes it with a discriminative backend (RapidOCR), and maps each OCR line-region to one `Word` in PDF points (region-as-Word, no invented coordinates). `extract_words` falls back to this only when the pdfplumber text layer is empty and the optional `ocr` extra is importable. Everything downstream (`text_lines`, `detect_bands`, `infer_leaf_grid`, `classify`, `compile_tables`) is unchanged.

**Tech Stack:** Python 3.12, `pypdfium2` (render), `rapidocr` + `onnxruntime` (transcribe), `numpy`, `pdfplumber` (existing), `reportlab` (fixtures), `pytest`.

## Global Constraints

- **Faithfulness invariant:** OCR backends MUST be discriminative transcribers (detection + CTC/attention). Autoregressive generative-VLM decoders are FORBIDDEN. Enforced architecturally via the `OcrBackend` contract docstring + backend choice; no generative path exists to gate.
- **No invented coordinates (§7):** region-as-Word only; never interpolate per-word x-positions. A tight, gapless multi-column row stays one region/one column — a documented limitation, not a silent gap.
- **§8 gate:** every step is PROCEDURAL (raw extraction or exact arithmetic) and must state *in the code* why it is irreducible to AXIOM/NEURAL. The render `scale` is a rendering-fidelity constant, NOT a decision threshold — say so in the code. No tuned tolerance may gate any classification.
- **Optional dependency:** OCR code lazy-imports `rapidocr`/`pypdfium2`; absent the `ocr` extra, image pages escalate as today (return `[]`), never crash, no hard dep added to `etkl`.
- **Coordinate convention:** PDF points, `x` from page-left, `top`/`bottom` from page-TOP (pdfplumber convention). `pypdfium2` renders top-origin → `point = pixel / scale`, NO y-flip.
- **Testing:** run tests ONLY via `./.venv/bin/python -m pytest` (bare `python3` uses the wrong rdflib and yields spurious SPARQL failures). OCR-dependent tests use `pytest.importorskip("rapidocr")` / `importorskip("pypdfium2")`.
- Code Apache-2.0. © 2026 François Rosselet. Default branch `main`; work on `etkl-ocr-first-mile`.

---

### Task 1: `ocr` module scaffold — `OcrRegion`, `OcrBackend` contract, pixel→point transform, `[ocr]` extra

**Files:**
- Create: `src/iladub/etkl/ocr.py`
- Modify: `pyproject.toml:40-71` (add `ocr` optional-dependencies group)
- Test: `tests/etkl/test_ocr_transform.py`

**Interfaces:**
- Consumes: `iladub.etkl.geometry.Word`.
- Produces:
  - `OcrRegion(text: str, x0: float, x1: float, top: float, bottom: float, confidence: float)` — frozen dataclass, PIXEL coords at render scale.
  - `OcrBackend` `Protocol` with `transcribe(self, image) -> list[OcrRegion]`.
  - `pixels_to_word(region: OcrRegion, scale: float, page_number: int = 0) -> Word` — exact `pixel/scale` transform.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_ocr_transform.py
from iladub.etkl.ocr import OcrRegion, OcrBackend, pixels_to_word
from iladub.etkl.geometry import Word


def test_pixels_to_word_divides_by_scale_no_yflip():
    # a region at 3x render scale -> points are pixels/3, top stays top (no flip)
    r = OcrRegion("Alpha Widget", x0=300.0, x1=600.0, top=150.0, bottom=210.0, confidence=0.99)
    w = pixels_to_word(r, scale=3.0, page_number=2)
    assert w == Word("Alpha Widget", 100.0, 200.0, 50.0, 70.0, 2)


def test_ocrregion_is_frozen():
    import dataclasses
    r = OcrRegion("x", 0, 1, 0, 1, 1.0)
    assert dataclasses.is_dataclass(r)
    try:
        r.text = "y"  # type: ignore[misc]
        assert False, "OcrRegion must be frozen"
    except dataclasses.FrozenInstanceError:
        pass


def test_backend_protocol_is_runtime_checkable_shape():
    # a minimal transcriber satisfies the protocol structurally
    class Stub:
        def transcribe(self, image):
            return []
    assert hasattr(OcrBackend, "transcribe")
    Stub().transcribe(None)  # shape smoke
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_transform.py -v`
Expected: FAIL — `ModuleNotFoundError: iladub.etkl.ocr`.

- [ ] **Step 3: Write minimal implementation**

```python
# src/iladub/etkl/ocr.py
"""ocr — faithful OCR first mile: a scanned (text-layer-less) page -> Words.

§8 gate: every step here is PROCEDURAL raw extraction or exact arithmetic (see the
per-function docstrings for the irreducibility statement). There is NO AXIOM/NEURAL step:
OCR is the image analog of geometry.extract_words. Faithfulness is guaranteed by FORBIDDING
the generative backend class (see OcrBackend), not by a confidence oracle.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .geometry import Word


@dataclass(frozen=True)
class OcrRegion:
    """One transcribed text line/segment. Bounds are PIXELS at the render scale,
    x from page-left, top/bottom from page-TOP (matching pdfplumber after /scale)."""
    text: str
    x0: float
    x1: float
    top: float
    bottom: float
    confidence: float


@runtime_checkable
class OcrBackend(Protocol):
    """A page transcriber. image -> transcribed line-regions.

    FAITHFULNESS CONTRACT (first-mile, load-bearing): an OcrBackend MUST be a
    DISCRIMINATIVE TRANSCRIBER — detection + CTC/attention recognition over image regions,
    faithful by construction. AUTOREGRESSIVE GENERATIVE-VLM DECODERS ARE FORBIDDEN: they can
    paraphrase, hallucinate, repeat, or silently omit, which poisons everything downstream.
    This is the §8/§3/§7 guarantee expressed as a type contract."""
    def transcribe(self, image) -> list[OcrRegion]: ...


def pixels_to_word(region: OcrRegion, scale: float, page_number: int = 0) -> Word:
    """PROCEDURAL exact arithmetic: pixel bounds at `scale` -> PDF points (point = pixel/scale).
    pypdfium2 renders top-origin, so `top` maps to `top` with NO y-flip. Irreducible: a unit
    conversion, not a decision — gates no classification."""
    return Word(region.text, region.x0 / scale, region.x1 / scale,
                region.top / scale, region.bottom / scale, page_number)
```

Add to `pyproject.toml` under `[project.optional-dependencies]` (after the `demo` group):

```toml
ocr = [
    "rapidocr>=1.4",
    "onnxruntime>=1.17",
    "pypdfium2>=4",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_transform.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/ocr.py tests/etkl/test_ocr_transform.py pyproject.toml
git commit -m "feat(etkl): ocr scaffold — OcrRegion, faithful OcrBackend contract, pixel->point transform, [ocr] extra"
```

---

### Task 2: `RapidOcrBackend` — wrap RapidOCR, adapt polygons to `OcrRegion`

**Files:**
- Modify: `src/iladub/etkl/ocr.py`
- Test: `tests/etkl/test_ocr_rapid.py`

**Interfaces:**
- Consumes: `OcrRegion` (Task 1); `rapidocr.RapidOCR` (lazy import); `numpy`.
- Produces: `RapidOcrBackend` with `transcribe(image) -> list[OcrRegion]`; `_bounds(poly) -> tuple[float,float,float,float]` axis-aligned bounds of a 4-point polygon.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_ocr_rapid.py
import numpy as np
import pytest
pytest.importorskip("rapidocr")
from iladub.etkl.ocr import RapidOcrBackend, OcrRegion, _bounds


def test_bounds_of_polygon_is_axis_aligned():
    poly = [[300.0, 150.0], [600.0, 150.0], [600.0, 210.0], [300.0, 210.0]]
    assert _bounds(poly) == (300.0, 600.0, 150.0, 210.0)  # x0, x1, top, bottom


def test_rapidocr_transcribes_rendered_text_faithfully():
    # a white image with black text drawn via PIL -> RapidOCR reads it back
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (600, 120), "white")
    d = ImageDraw.Draw(img)
    d.text((20, 40), "Alpha Widget 42", fill="black")
    regions = RapidOcrBackend().transcribe(np.array(img))
    assert regions, "RapidOCR should find at least one region"
    joined = " ".join(r.text for r in regions)
    assert "Alpha" in joined and "Widget" in joined     # faithful transcription
    for r in regions:
        assert isinstance(r, OcrRegion)
        assert r.x1 > r.x0 and r.bottom > r.top and 0.0 <= r.confidence <= 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_rapid.py -v`
Expected: FAIL — `ImportError: cannot import name 'RapidOcrBackend'`.

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/etkl/ocr.py`:

```python
def _bounds(poly) -> tuple[float, float, float, float]:
    """Axis-aligned (x0, x1, top, bottom) of a 4-point OCR polygon. PROCEDURAL exact
    arithmetic (min/max over corners) — no tuned constant."""
    xs = [float(p[0]) for p in poly]
    ys = [float(p[1]) for p in poly]
    return min(xs), max(xs), min(ys), max(ys)


class RapidOcrBackend:
    """Default backend: RapidOCR (PP-OCR on ONNX Runtime) — a DISCRIMINATIVE TRANSCRIBER
    (detection + CTC recognition), faithful by construction. Satisfies OcrBackend. Emits one
    region per detected text line/segment; per-word boxes are NOT available (region-as-Word
    downstream). Lazy-imports rapidocr so the dep stays optional."""

    def __init__(self):
        from rapidocr import RapidOCR  # lazy: optional [ocr] extra
        self._engine = RapidOCR()

    def transcribe(self, image) -> list["OcrRegion"]:
        res = self._engine(image)
        if res is None or getattr(res, "boxes", None) is None:
            return []
        out: list[OcrRegion] = []
        for poly, txt, score in zip(res.boxes, res.txts, res.scores):
            x0, x1, top, bottom = _bounds(poly)
            out.append(OcrRegion(str(txt), x0, x1, top, bottom, float(score)))
        return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_rapid.py -v`
Expected: PASS (2 passed). If PIL's default font renders too small for RapidOCR, the test may need a larger image/font — enlarge the image to 800x160 and draw at a larger size; the assertion (Alpha/Widget present) is the invariant.

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/ocr.py tests/etkl/test_ocr_rapid.py
git commit -m "feat(etkl): RapidOcrBackend — faithful transcriber, polygon->OcrRegion adapter"
```

---

### Task 3: `render_page_to_words` — render + transcribe + adapt (region-as-Word), and the image-only fixture

**Files:**
- Modify: `src/iladub/etkl/ocr.py`
- Modify: `tests/etkl/fixtures.py` (add `image_only_table_pdf`)
- Test: `tests/etkl/test_ocr_render.py`

**Interfaces:**
- Consumes: `pixels_to_word`, `RapidOcrBackend`, `OcrBackend`, `OcrRegion` (Tasks 1-2); `pypdfium2` (lazy); `iladub.etkl.geometry.Word`.
- Produces:
  - `render_page_to_words(pdf_path: str, page_number: int = 0, backend: OcrBackend | None = None, scale: float = 3.0) -> list[Word]`.
  - `tests.etkl.fixtures.image_only_table_pdf(path) -> str` — writes a text-layer-LESS PDF (a table raster on a full page) and returns `path`.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_ocr_render.py
import os, tempfile
import pytest
pytest.importorskip("pypdfium2")
from iladub.etkl.ocr import render_page_to_words, OcrRegion
from iladub.etkl.geometry import Word, extract_words


class _StubBackend:
    """Deterministic transcriber: three gap-separated regions (pixel coords at scale=3)."""
    def transcribe(self, image):
        return [OcrRegion("Alpha", 30, 120, 30, 60, 1.0),
                OcrRegion("Widget", 300, 450, 30, 60, 1.0),
                OcrRegion("42", 600, 660, 30, 60, 1.0)]


def _any_pdf():
    from tests.etkl import fixtures as F
    p = os.path.join(tempfile.mkdtemp(), "s.pdf"); F.simple_table_pdf(p); return p


def test_render_maps_regions_to_words_in_points_region_as_word():
    words = render_page_to_words(_any_pdf(), backend=_StubBackend(), scale=3.0)
    assert words == [Word("Alpha", 10, 40, 10, 20, 0),
                     Word("Widget", 100, 150, 10, 20, 0),
                     Word("42", 200, 220, 10, 20, 0)]


def test_image_only_pdf_has_no_text_layer():
    from tests.etkl import fixtures as F
    p = os.path.join(tempfile.mkdtemp(), "img.pdf"); F.image_only_table_pdf(p)
    assert extract_words.__module__  # sanity
    # pdfplumber sees no words on a pure-image page:
    import pdfplumber
    with pdfplumber.open(p) as pdf:
        assert pdf.pages[0].extract_words() == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_render.py -v`
Expected: FAIL — `ImportError: cannot import name 'render_page_to_words'` (and `image_only_table_pdf` missing).

- [ ] **Step 3: Write minimal implementation**

Append to `src/iladub/etkl/ocr.py`:

```python
def render_page_to_words(pdf_path: str, page_number: int = 0,
                         backend: "OcrBackend | None" = None, scale: float = 3.0) -> list[Word]:
    """Scanned page -> Words. PROCEDURAL raw extraction: (1) pypdfium2 rasterizes the page at
    `scale` (a rendering-FIDELITY constant — more pixels = better recognition; it gates NO
    classification, so it is not a tuned decision threshold); (2) the backend transcribes it
    (discriminative, faithful); (3) each line-region becomes ONE Word (region-as-Word — no
    invented per-word coordinates, §7). Lazy-imports pypdfium2 so the dep stays optional."""
    import numpy as np
    import pypdfium2 as pdfium

    if backend is None:
        backend = RapidOcrBackend()
    pdf = pdfium.PdfDocument(pdf_path)
    try:
        image = np.array(pdf[page_number].render(scale=scale).to_pil().convert("RGB"))
    finally:
        pdf.close()
    regions = backend.transcribe(image)
    return [pixels_to_word(r, scale, page_number) for r in regions]
```

Add to `tests/etkl/fixtures.py` (uses the existing reportlab imports `canvas`, `letter`; adds `pypdfium2` + `ImageReader`):

```python
def image_only_table_pdf(path):
    """A text-layer-LESS PDF: render simple_table_pdf to a raster and place it full-page.
    Pure-pip (PNG, no JPEG encoder). Simulates a scan for the OCR first-mile tests."""
    import os, tempfile
    import pypdfium2 as pdfium
    from reportlab.lib.utils import ImageReader
    src = os.path.join(tempfile.mkdtemp(), "src.pdf")
    simple_table_pdf(src)
    pdf = pdfium.PdfDocument(src)
    try:
        page = pdf[0]
        w_pt, h_pt = page.get_size()
        pil = page.render(scale=3.0).to_pil().convert("RGB")
    finally:
        pdf.close()
    png = os.path.join(tempfile.mkdtemp(), "page.png")
    pil.save(png)  # PNG: no JPEG encoder needed
    c = canvas.Canvas(path, pagesize=(w_pt, h_pt))
    c.drawImage(ImageReader(png), 0, 0, width=w_pt, height=h_pt)
    c.save()
    return path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_render.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/ocr.py tests/etkl/fixtures.py tests/etkl/test_ocr_render.py
git commit -m "feat(etkl): render_page_to_words (region-as-Word) + image-only scan fixture"
```

---

### Task 4: Integration seam — `extract_words` OCR fallback (only when no text layer, only if extra present)

**Files:**
- Modify: `src/iladub/etkl/geometry.py:39-48` (`extract_words`)
- Test: `tests/etkl/test_ocr_fallback.py`

**Interfaces:**
- Consumes: `iladub.etkl.ocr.render_page_to_words` (lazy import, Task 3).
- Produces: `extract_words(pdf_path, page_number=0) -> list[Word]` with an OCR fallback: unchanged when a text layer exists; OCR when empty AND `ocr` importable; `[]` otherwise.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_ocr_fallback.py
import os, tempfile, builtins
import pytest
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl import geometry
from iladub.etkl.geometry import extract_words, Word
from tests.etkl import fixtures as F


def _pdf(fn, name):
    p = os.path.join(tempfile.mkdtemp(), name + ".pdf"); fn(p); return p


def test_born_digital_never_invokes_ocr(monkeypatch):
    # a real text layer -> OCR must NOT run
    def _boom(*a, **k):
        raise AssertionError("OCR must not run when a text layer is present")
    monkeypatch.setattr("iladub.etkl.ocr.render_page_to_words", _boom, raising=False)
    words = extract_words(_pdf(F.simple_table_pdf, "digital"))
    assert words and all(isinstance(w, Word) for w in words)


def test_image_only_falls_back_to_ocr(monkeypatch):
    # no text layer -> OCR fallback is called; stub it to avoid the heavy engine
    stub = [Word("Alpha", 10, 40, 10, 20, 0)]
    monkeypatch.setattr("iladub.etkl.ocr.render_page_to_words",
                        lambda *a, **k: stub, raising=False)
    words = extract_words(_pdf(F.image_only_table_pdf, "scan"))
    assert words == stub


def test_graceful_escalation_when_ocr_extra_absent(monkeypatch):
    # simulate the [ocr] extra not installed -> extract_words returns [] (no crash)
    real_import = builtins.__import__
    def _no_ocr(name, *a, **k):
        if name == "iladub.etkl.ocr" or name.endswith(".ocr"):
            raise ImportError("simulated: ocr extra absent")
        return real_import(name, *a, **k)
    monkeypatch.setattr(builtins, "__import__", _no_ocr)
    assert extract_words(_pdf(F.image_only_table_pdf, "scan2")) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_fallback.py -v`
Expected: FAIL — `test_image_only_falls_back_to_ocr` returns `[]` (no fallback yet).

- [ ] **Step 3: Write minimal implementation**

Modify `extract_words` in `src/iladub/etkl/geometry.py`:

```python
def extract_words(pdf_path: str, page_number: int = 0) -> list[Word]:
    """All text runs on a page, with bounding boxes in PDF points.

    Text-layer first: when pdfplumber finds words (a born-digital page), they are returned
    exactly. When the page has NO text layer (a scan/image), fall back to OCR — but ONLY if
    the optional `ocr` extra is importable; absent it, return [] and let the pipeline escalate
    (unchanged behaviour). OCR never competes with a present text layer."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        raw = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    words = [
        Word(w["text"], float(w["x0"]), float(w["x1"]),
             float(w["top"]), float(w["bottom"]), page_number)
        for w in raw
    ]
    if words:
        return words
    try:
        from .ocr import render_page_to_words
    except ImportError:
        return []
    return render_page_to_words(pdf_path, page_number)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_fallback.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add src/iladub/etkl/geometry.py tests/etkl/test_ocr_fallback.py
git commit -m "feat(etkl): extract_words OCR fallback — no-text-layer only, optional extra, graceful escalation"
```

---

### Task 5: End-to-end DoD — a scanned table PDF compiles to an asserted region

**Files:**
- Test: `tests/etkl/test_ocr_end_to_end.py`

**Interfaces:**
- Consumes: `iladub.etkl.compile_tables`; `tests.etkl.fixtures.image_only_table_pdf` (Task 3). No new production code — this task proves the loop closes on the real engine.

- [ ] **Step 1: Write the failing test**

```python
# tests/etkl/test_ocr_end_to_end.py
import os, tempfile
import pytest
pytest.importorskip("rapidocr"); pytest.importorskip("pypdfium2")
pytest.importorskip("pdfplumber"); pytest.importorskip("reportlab")
from iladub.etkl import compile_tables
from tests.etkl import fixtures as F


def test_scanned_table_pdf_compiles_to_asserted_region():
    p = os.path.join(tempfile.mkdtemp(), "scan_e2e.pdf")
    F.image_only_table_pdf(p)
    rep = compile_tables(p)                       # no text layer -> real OCR runs
    verdicts = [r.verdict for r in rep.regions]
    assert "asserted" in verdicts, [(str(r.kind).split(".")[-1], r.verdict, r.reason)
                                    for r in rep.regions]
    assert rep.score > 0.0, "a scanned table should compile via OCR (was nothing pre-slice)"
```

- [ ] **Step 2: Run test to verify it fails/passes**

Run: `./.venv/bin/python -m pytest tests/etkl/test_ocr_end_to_end.py -v`
Expected: PASS once Tasks 1-4 are in. If it FAILS on OCR reading the raster (regions found but columns not separated), the cause is the fixture's rendered gap width, not the pipeline — widen the column spacing in the source table (`simple_table_pdf`) OR raise the render `scale`; do NOT tune any pipeline constant (§8). If RapidOCR reads the table as one region per row (tight columns), that is the documented region-as-Word limitation — switch the fixture to a clearly gap-separated table so the DoD exercises the supported case.

- [ ] **Step 3: Run the full etkl suite (no regressions)**

Run: `./.venv/bin/python -m pytest tests/etkl -q`
Expected: all pass (existing born-digital tests unaffected; OCR tests pass or skip).

- [ ] **Step 4: Commit**

```bash
git add tests/etkl/test_ocr_end_to_end.py
git commit -m "test(etkl): end-to-end — scanned table PDF compiles to asserted region via OCR (DoD)"
```

---

## Self-Review

**Spec coverage:**
- Auto-fallback when no text layer → Task 4. ✓
- OCR optional extra + graceful escalation → Task 1 (extra), Task 4 (escalation test). ✓
- Region-as-Word, no invented coords → Task 3 (`render_page_to_words`, stub test). ✓
- Faithfulness invariant (transcriber only, generative forbidden) → Task 1 (`OcrBackend` docstring), Task 2 (RapidOCR). ✓
- §8 classification stated in code → Tasks 1-3 docstrings. ✓
- pypdfium2 render, pixel→point no y-flip → Task 1 (transform), Task 3 (render). ✓
- Image-only fixture (pure-pip, PNG) → Task 3. ✓
- Five spec tests → transform (T1), adapter/region-as-Word (T3), end-to-end (T5), born-digital unchanged (T4), graceful escalation (T4). ✓
- Out-of-scope (rules on scans, Tesseract, multi-page, confidence gating) → not implemented; documented in spec. ✓

**Placeholder scan:** none — every step has full code and exact commands.

**Type consistency:** `OcrRegion(text,x0,x1,top,bottom,confidence)`, `pixels_to_word(region,scale,page_number)`, `render_page_to_words(pdf_path,page_number,backend,scale)`, `RapidOcrBackend.transcribe(image)->list[OcrRegion]`, `_bounds(poly)->(x0,x1,top,bottom)` are used identically across tasks. `Word(text,x0,x1,top,bottom,page)` matches `geometry.Word`. ✓
