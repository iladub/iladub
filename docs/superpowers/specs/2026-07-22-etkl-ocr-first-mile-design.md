# `iladub.etkl.ocr` — the scanned-document first mile (design)

> Status: approved 2026-07-22. Author: François Rosselet. © 2026.
> Code Apache-2.0. Part of the ET(K)L pipeline (`iladub.etkl`).

## Problem

`compile_tables` reads a PDF's **text layer** via pdfplumber (`extract_words`). A
**scanned / image-only PDF has no text layer** — `extract_words` returns `[]`, so
`detect_bands`/`classify`/`compile_tables` produce nothing. The most common real-world
"hardest" document (a scanned tabular report) is therefore uncompilable today.

This slice makes a scanned PDF compile end-to-end through the **existing** pipeline by
supplying the same `Word` list from an OCR source — while keeping the **first mile
faithful: text is transcribed, never generated.** Hallucinated OCR text would poison
everything downstream, so the faithfulness invariant is load-bearing, not a nicety.

## Decisions (locked with the user)

1. **Auto-fallback, only when there is no text layer.** A page *with* a text layer always
   uses the exact born-digital words (OCR never runs, never competes). OCR runs only when
   `extract_words` would otherwise return `[]`. OCR is an **optional dependency** (`[ocr]`
   extra); absent it, image pages escalate exactly as today (no crash, no hard dep).
2. **Region-as-Word; whitespace splits columns.** RapidOCR emits one box per text
   line/segment (a phrase or cell), not per word. Each OCR region becomes **one `Word`** at
   its measured bbox. Column separation relies on the whitespace *between* regions — exactly
   how `detect_bands`/`infer_leaf_grid` already separate gap-separated tables. **No
   coordinate is invented** (we never interpolate per-word x-positions the source doesn't
   support — that would violate §7). A tight row with no inter-column gap stays one region
   and one column: a **documented limitation** (the same tight-column limit born-digital
   already has, there handled by ruled columns), deferred to a future slice.

## The faithfulness invariant (why this is safe at the first mile)

OCR backends MUST be **discriminative transcribers** — detection + CTC/attention
recognition over image regions, *faithful by construction*. **Autoregressive
generative-VLM decoders are forbidden** (they can paraphrase, hallucinate, repeat, or
silently omit). This is enforced **architecturally**: the `OcrBackend` contract documents
the requirement, and the only shipped backend (RapidOCR / PP-OCR on ONNX Runtime) is a
transcriber. There is no generative path to gate. This is the §8 gate expressed as a type
contract plus a backend-selection rule, not a runtime confidence check.

## §8 neurosymbolic gate classification

Every step is faithful and justified. There is **no AXIOM or NEURAL step** — OCR is the
image analog of `extract_words` (raw extraction: source → typed facts), and faithfulness is
guaranteed by *forbidding the generative class*, not by a semantic oracle.

| Step | Class | Justification (stated in code + here) |
|---|---|---|
| render PDF page → raster (`pypdfium2`) | **PROCEDURAL** raw extraction | deterministic rasterization; irreducible to AXIOM/NEURAL |
| OCR transcribe (image → text + box) | **PROCEDURAL** raw extraction | discriminative transcriber, faithful-by-construction; generative class forbidden; no ontology derives glyph identity from pixels |
| pixel → point transform | **PROCEDURAL** exact arithmetic | `point = pixel / scale`; deterministic, decidable |
| no-text-layer → OCR routing | **PROCEDURAL** | `len(words) == 0` — a count of extracted words, not a tuned tolerance |

The render `scale` (≈216 DPI) is a **rendering-fidelity** constant (more pixels = better
recognition), **not a decision threshold** — it gates no classification, so it is not the
"tuned constant" the gate forbids. It is documented as such in the code.

## Architecture

Placement: **`src/iladub/etkl/ocr.py`** — a submodule of the etkl pipeline, beside
`geometry.py`, because it produces `Word`s that feed `iladub.etkl`. (Not top-level
`iladub.ocr`.)

### Components

**1. Backend seam (`ocr.py`)**

```python
@dataclass(frozen=True)
class OcrRegion:
    text: str
    x0: float; x1: float           # PIXEL coords at render scale, page-left / page-top
    top: float; bottom: float
    confidence: float

class OcrBackend(Protocol):
    def transcribe(self, image) -> list[OcrRegion]: ...
    # CONTRACT: a backend MUST be a discriminative transcriber (detection + CTC/attention),
    # faithful by construction. Autoregressive generative-VLM decoders are FORBIDDEN
    # (hallucinate / paraphrase / omit). This is the first-mile faithfulness invariant.

class RapidOcrBackend:                 # default; lazy-imports rapidocr (optional dep)
    def transcribe(self, image) -> list[OcrRegion]: ...
```

RapidOCR returns 4-point polygons + text + score; the adapter takes each polygon's axis-
aligned bounds as `(x0, x1, top, bottom)` and the score as `confidence`. Tesseract is left
as a **documented future backend** (real word/char boxes, but a *system binary* → not the
pure-pip default) — not built in this slice (YAGNI).

**2. Render + adapt (`ocr.py`)**

```python
def render_page_to_words(pdf_path, page_number=0, backend=None, scale=3.0) -> list[Word]:
    # 1. pypdfium2 renders the page to a raster at `scale` (pure-pip; already a dep tree member)
    # 2. backend.transcribe(image) -> list[OcrRegion]  (pixel coords)
    # 3. pixel -> point: point = pixel / scale; pdfium renders top-origin, matching
    #    pdfplumber's `top` convention (NO y-flip). Each region -> ONE Word at its bbox.
```

- `backend` defaults to `RapidOcrBackend()`.
- A `_pixels_to_points(region, scale) -> Word` helper isolates the exact-arithmetic
  transform (unit-tested independently).

**3. Integration — one seam only (`geometry.py`)**

`extract_words` gains an OCR fallback:

```python
def extract_words(pdf_path, page_number=0) -> list[Word]:
    words = [ ... pdfplumber ... ]          # unchanged
    if words:
        return words                        # text layer present -> exact born-digital words
    # no text layer: OCR fallback, ONLY if the optional extra is importable
    try:
        from .ocr import render_page_to_words
    except ImportError:
        return []                           # graceful escalation as today
    return render_page_to_words(pdf_path, page_number)
```

Everything downstream — `text_lines`, `detect_bands`, `infer_leaf_grid`, `classify`,
`compile_tables` — is **unchanged**. `extract_rules`/`extract_hrules`/`extract_chars`
return `[]` on a scan (no vector lines), so whitespace inference carries gap-separated
tables. **Image-based rule detection is explicitly out of scope** (future slice).

**4. Optional dependency (`pyproject.toml`)**

```toml
ocr = [
    "rapidocr>=1.4",
    "onnxruntime>=1.17",
    "pypdfium2>=4",
]
```

## Definition of done (the loop closes — vertical slice, not a layer)

A synthetic **image-only PDF** (a table rendered to raster, wrapped as a text-layer-less
PDF via reportlab `drawImage` — pure-pip, PNG, no JPEG encoder needed) compiles through
`compile_tables` to an **asserted** region with `score > 0`, where today (no text layer) it
yields nothing. Born-digital fixtures are byte-identical (OCR never runs). OCR-absent =
graceful escalation.

## Tests

1. **pixel→point transform** — a known region at a known scale maps to the expected PDF
   points, exactly (round-trip / fixed-position assertion).
2. **region-as-Word adapter** — three gap-separated OCR regions → three `Word`s → three
   columns via the existing `text_lines`/grid path.
3. **end-to-end** — an image-only table PDF → `compile_tables` → `"asserted"` in verdicts,
   `score > 0` (was nothing). `importorskip("rapidocr")`.
4. **born-digital unchanged** — a shipped fixture *with* a text layer: OCR is never invoked
   (monkeypatch `render_page_to_words` to raise; `extract_words` still returns the
   pdfplumber words).
5. **graceful escalation** — simulate the `ocr` extra absent (import failure) →
   `extract_words` returns `[]`, `compile_tables` escalates, no crash.

## Out of scope (named, not silent — future slices)

- Image-based **rule/line detection** (scans have no vector rules → tight-column tables
  without inter-column whitespace stay one region). The tight-column limitation is
  inherited from born-digital and documented, not hidden.
- **Tesseract** backend (word/char boxes; system binary).
- Multi-page scans (slice targets one page, like the rest of the pipeline today).
- OCR **confidence as promotion/proposition signal** — carried on `OcrRegion` for
  provenance, but no gating in this slice (transcription is asserted raw extraction).
