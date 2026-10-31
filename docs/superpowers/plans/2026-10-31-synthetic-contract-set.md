# Synthetic Contract Set Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Serves:** maintenance — project 1 of the contract:01 rescope; no criterion yet.

**Execution method: subagent-driven** (ruled by the maintainer 2026-10-31, in chat).

**Doc impact: none.** A generator under `scripts/`, fixture data under `examples/`, tests. No vocabulary,
shape or released page changes.

**Goal:** one command builds 39 fake filled-contract PDFs (12 fills × 3 flavours + 3 mixed) from four
real, locally downloaded templates, each with a generator-written Turtle truth record.

**Architecture:** a package `scripts/synthetic_contracts/` reads committed fill specs and hand-authored
part maps (`examples/synthetic-contracts/`), places the values onto the local template in one of three
flavours, writes each PDF to the gitignored `synthetic/out/` and its truth to
`examples/synthetic-contracts/truth/`. Truth is always in the output page's own coordinates.

**Tech Stack:** Python 3.12; already in the main checkout's `.venv` (measured below): reportlab 5.0.0,
pypdfium2 5.11.0, pdfplumber 0.11.10, pillow 12.2.0, opencv-python 5.0.0.93, numpy 2.5.0, rdflib 7.6.0.
Microsoft Word (macOS) via `osascript`. **No new dependency** — see Global Constraints.

**Spec:** `docs/superpowers/specs/2026-10-31-synthetic-contract-set-design.md` (APPROVED 2026-10-31).

## Measured before writing (2026-10-31, session scratchpad)

The handoff named three facts the spec left unmeasured. All three are now measured; they settle § 4.2
and § 4.3's branches.

| template | URL | sha256 | pages | size (pt) |
|---|---|---|---|---|
| `gafta-48` | `https://www.gafta.com/media/tthjkq34/48_2026.pdf` | `ed2e58f37433221155c43e33763d956807ff50a54b32ec97bf5fd5dd8aeb5103` | 8 | 595×842 |
| `gafta-79b` | `https://www.gafta.com/media/xw4nroew/79b_2026.pdf` | `8daad72c5cc0230a933a3f9b457f3069f7d1a98cd9d9f0e1852831a3e3359dfa` | 6 | 595×842 |
| `gafta-124` | `https://www.gafta.com/media/5qynr511/124_2026.pdf` | `76bb91193bf4607c848c16dc398d41ee7047700d7653fa6b42744491aea3fde4` | 14 | 595×842 |
| `usda-ffp-cp` | `https://omb.report/icr/201404-0551-002/doc/47577601.pdf` | `d677ebc9d0b5523e1997469b4370602ca58c4f3074c7efbd4c30ad450b40018f` | 13 | 612×792 |

1. **AcroForm fields (§ 4.3): none, in all four.** `pypdfium2 PdfDocument.init_forms(); get_formtype()`
   → `0` and `0` widget annotations on every page of every template. **So the form-fill flavour is the
   overlay branch for all four.**
2. **Blanks in No. 124 (§ 4.2): yes.** p7 (1-based) is a sample label with 14 dot-leader lines (*Sender*,
   *From*, *To*, *Set No … Sample No.*, *Seals*, …; 15 runs by `_{4,}|\.{6,}|…{2,}`). So No. 124 is
   fillable and the count is **36 PDFs**, not 27; it also appears unfilled as the rules part of a mixed
   document. Blank runs elsewhere: 48 p1/p3/p4/p8 = 14/3/1/2; 79B p1/p2/p6 = 12/3/2; USDA p1–p4,p6,p8,p11
   = 18/9/4/8/3/1/2. All blanks are dot leaders; no ruled underline over 40 pt was found on any page.
3. **Table figures (§ 4.1)**, pdfplumber `find_tables()`, rows ≥ 2 and cols ≥ 2, 1-based pages: 124 p6
   **7×6** (the survey's figure, confirmed); 79B p1 **2×5**, p2 **2×5** and **2×4** (the clause-6 quality
   table spans the page break); 48 none; USDA none.
4. **Word export spike: NOT working yet.** `textutil -convert docx` made a `.docx`; Word opened it (its
   `~$t.docx` lock file appeared), and `save as … file format format PDF` to a path under `/private/tmp`
   failed after 2 minutes with `Délai dépassé pour un AppleEvent (-1712)`. The likely cause is Word's
   sandbox asking for file access outside its container; **unverified**. Task 6 Step 1 settles it.
5. **Handwriting fonts present as TTF:** `/System/Library/Fonts/Supplemental/` has `Bradley Hand Bold.ttf`,
   `Comic Sans MS.ttf`, `Apple Chancery.ttf`, `Chalkduster.ttf`.
6. **Baseline inputs** (CLAUDE.md § Corpus baseline): `scripts/` is not one except two named files;
   `examples/` and `tests/` are not. `pyproject.toml` **is**, so a dependency added there forces the
   24-minute regenerate — which is why this plan adds none.
7. **Precedent:** `scripts/fetch_corpus.py` + `tests/corpus-manifest.ttl` (`cor:` = repo-internal, "not
   published, not w3id-registered"). The manifest and fetcher here follow it.

## Global Constraints

- **Committed:** generator, fill specs, part maps, truth, template manifest. **Never committed:**
  templates, PDFs, `.docx`, rasters — all under the gitignored `/synthetic/` (spec § 3).
- **No template text in any committed file** (spec § 3). Maps and fills carry labels, field keys, fake
  values, page numbers and coordinates only. Field keys are our own lowercase keys (`^[a-z][a-z0-9.-]*$`),
  never a template's label copied.
- **Nothing outside `scripts/synthetic_contracts/` imports it or names `examples/synthetic-contracts/truth`**
  (A3), except its own tests.
- **Nothing under `src/`, `vocab/`, `readings/`, `corpus/`, `pyproject.toml` changes.** No new dependency.
- **Vocabulary:** `syn:` = `https://w3id.org/iladub/synthetic#`, repo-internal like `cor:`; declared in
  `examples/synthetic-contracts/synthetic.ttl`; provenance via `prov:`. Part types are plain literals from
  the closed set `contract-form`, `rules`, `charter-party`, `table`, `blank` (spec § 4.5; no type tree).
- **Coordinates:** points, origin top-left, `(x0, top, x1, bottom)` — pdfplumber's convention — on 1-based
  pages, in the **output** document (spec § 4.5).
- **Neurosymbolic gate:** every module docstring states the PROCEDURAL justification: the generator makes
  documents; its jitter/noise constants are generation parameters, not reading tolerances; the only two
  reads (Task 6's text extraction from the template, and exact-string location of strings the generator
  itself wrote) are raw extraction and decidable exact matching. No generator function may be called from
  a reader.
- **Build refuses** if any template's sha256 differs from the manifest (spec § 6).
- **Licences:** code Apache-2.0; `examples/synthetic-contracts/**` CC-BY-4.0 with `dcterms:creator
  "François Rosselet"` and `dcterms:license` on every file's header node.
- Run tests with the main checkout's venv: `PYTHONPATH=src ../../../.venv/bin/python -m pytest …` (the
  worktree has no `.venv`).

## Review Focus

1. **A value longer than its blank.** Expect the fill-spec writer to refuse it (not overflow onto template
   text). Pinned in Task 3 (`test_every_value_fits_its_blank`).
2. **A value string that occurs twice in one output document** (e.g. the same port on two lines, or a
   value that also appears in template text). Word-flavour location by exact match would be ambiguous.
   Expect the build to refuse, naming the value. Pinned in Task 6 (`test_locate_refuses_ambiguous`) and
   Task 3 (`test_values_unique_within_document`).
3. **The scan step moves text but truth does not follow.** Expect every value's truth bbox, after skew,
   to contain ink. Pinned in Task 5 (`test_scan_truth_boxes_contain_ink`).
4. **A template re-served with a new edition.** Expect `fetch` to report the mismatch and `build` to refuse.
   Pinned in Task 1 (`test_build_refuses_sha_mismatch`).
5. **A mixed document's later part keeps its own page numbers.** Expect page offsets applied. Pinned in
   Task 7 (`test_mixed_truth_offsets_pages`).

---

### Task 1: Manifest, fetch, verify

**Files:**
- Create: `scripts/synthetic_contracts/__init__.py`, `__main__.py`, `manifest.py`
- Create: `examples/synthetic-contracts/templates.ttl`, `examples/synthetic-contracts/synthetic.ttl`
- Modify: `.gitignore` (add `/synthetic/` beside `corpus/`, with a one-line comment citing the spec)
- Test: `tests/test_synthetic_contracts_manifest.py`

**Interfaces:**
- Produces: `Template(id: str, url: str, sha256: str, pages: int)`;
  `load_manifest(path: Path = MANIFEST) -> dict[str, Template]`;
  `template_path(t: Template, root: Path = SYNTH_ROOT) -> Path` (→ `synthetic/templates/<id>.pdf`);
  `verify(t: Template, root) -> None` raising `TemplateMismatch(id, expected, actual)` or
  `TemplateMissing(id)`; `fetch(root, download=...) -> int` (exit code, the `fetch_corpus.main` shape:
  downloads absent files, removes and reports a mismatching one, nonzero until all verify).
- CLI: `python -m scripts.synthetic_contracts {fetch,fills,build}`; this task wires `fetch` only.

- [ ] **Step 1:** Write `templates.ttl` with the four rows of the measured table (`syn:Template`, `syn:id`,
  `syn:url`, `syn:sha256`, `syn:pages`), and `synthetic.ttl` declaring every `syn:` class and property
  this plan uses, each with `rdfs:label` and `rdfs:comment`.
- [ ] **Step 2: Failing tests**: `test_manifest_pins_four_templates` (ids == `{"gafta-48","gafta-79b",
  "gafta-124","usda-ffp-cp"}`, each sha256 64 hex chars); `test_fetch_downloads_and_verifies` (fake
  `download` returning fixed bytes, manifest written to `tmp_path` with that bytes' sha → exit 0, file
  present); `test_build_refuses_sha_mismatch` (wrong bytes → `verify` raises `TemplateMismatch`, `fetch`
  exits nonzero and removes the file); `test_synthetic_dir_is_ignored` (`git check-ignore synthetic/x.pdf`
  exits 0).
- [ ] **Step 3:** Run; expect ImportError / failures.
- [ ] **Step 4:** Implement `manifest.py` and `__main__.py` (argparse subcommands).
- [ ] **Step 5:** Tests green; then the real fetch: `PYTHONPATH=src ../../../.venv/bin/python -m
  scripts.synthetic_contracts fetch` → exit 0, four files in `synthetic/templates/`.
- [ ] **Step 6: FALSIFICATION** — make `verify` return without comparing; show
  `test_build_refuses_sha_mismatch` failing; restore (`cp` from a saved copy); suite green.
- [ ] **Step 7:** Commit `feat(synthetic): template manifest + fetch/verify`.

### Task 2: Part maps (hand-authored; owner reviews)

**Files:**
- Create: `examples/synthetic-contracts/maps/{gafta-48,gafta-79b,gafta-124,usda-ffp-cp}.ttl`
- Create: `examples/synthetic-contracts/shapes.ttl`, `examples/synthetic-contracts/negative/map-negative.ttl`
- Create: `scripts/synthetic_contracts/maps.py`
- Test: `tests/test_synthetic_contracts_maps.py`

**Interfaces:**
- Produces: `Box(page: int, x0: float, top: float, x1: float, bottom: float)`;
  `Part(id: str, type: str, box: tuple[Box, ...], parent: str | None)` (a part may span pages, so `box`
  is one `Box` per page); `Blank(field: str, box: Box, part: str)`;
  `TableGrid(part: str, page: int, col_edges: tuple[float, ...], row_edges: tuple[float, ...])`;
  `PartMap(template: str, parts, blanks, grids, review: str)`; `load_map(template_id) -> PartMap`.

Map content, from the measurements above: one whole-document part per template (`contract-form` for 48 and
79B, `rules` for 124, `charter-party` for USDA); a `table` part for 124 p6 and for 79B's quality table
(two `Box`es, p1 and p2, `parent` = the 79B form — the nesting the spec § 4.1 wants); one `blank` per
dot-leader run, each with our field key; a `TableGrid` for each table (hand-measured edges, used by Task
6 to rebuild the table without table-finding). The builder may locate dot leaders with a throwaway
scratchpad script; **that script is not committed** (it reads a document). Every map starts at
`syn:review "draft"`; the owner changes it to `"owner-reviewed"` (spec § 4.5) — the build does not
require it, but truth records it.

- [ ] **Step 1: Failing tests**: `test_maps_conform` (each map + `synthetic.ttl` conforms to `shapes.ttl`
  under pySHACL `inference="rdfs"`); `test_map_negative_fails` (the negative file — a part type outside the
  closed set, a field key with a space, a box with `x1 < x0` — does not conform, with ≥ 3 results);
  `test_blanks_inside_their_part` (every blank's box is inside one box of its part, same page);
  `test_counts_match_measurement` (blank count per template = the measured dot-leader runs — 48: 20, 79B:
  17, 124: 15, USDA: 45 — minus the runs the task report names as not a blank, each with its reason; table parts: 124 one on p6, 79B one spanning p1–p2); and, **local only**
  (`pytest.skip` if `synthetic/templates/` is absent), `test_no_template_text_committed` (no line of ≥ 4
  words from any template's `extract_text()` occurs in any file under `examples/synthetic-contracts/`).
- [ ] **Step 2:** Run; failing.
- [ ] **Step 3:** Write `shapes.ttl` (`sh:in` for part types, `sh:pattern` for field keys, SPARQL
  constraint for `x0 < x1`, `top < bottom`), the negative file, `maps.py`, then the four maps.
- [ ] **Step 4:** Green, including the local-only test on this machine (show it ran, not skipped).
- [ ] **Step 5: FALSIFICATION** — paste one real template line into a map comment; show
  `test_no_template_text_committed` failing; restore; green.
- [ ] **Step 6:** Commit `feat(synthetic): part maps for four templates (draft, for owner review)`.

### Task 3: Fill specs

**Files:**
- Create: `scripts/synthetic_contracts/values.py`, `scripts/synthetic_contracts/fills.py`
- Create (generated once, then committed as data): `examples/synthetic-contracts/fills/<template>-<n>.ttl`,
  n ∈ {1,2,3}, 12 files
- Test: `tests/test_synthetic_contracts_fills.py`

**Interfaces:**
- Consumes: `PartMap`, `Blank` (Task 2).
- Produces: `Fill(id: str, template: str, seed: int, values: dict[str, str], font: str, size: float)`;
  `make_fill(m: PartMap, n: int) -> Fill` (seed = `n` mixed with a stable hash of the template id —
  `zlib.crc32`, never `hash()`); `write_fill(f) -> Path`; `load_fill(id) -> Fill`; CLI `fills`
  (writes only absent files; refuses to overwrite).

Values are fake and plausible per field key: party names from a seeded syllable generator (never a real
company), ports from a fixed list of real port names, dates in 2027, quantities and prices as numbers with
units. `font` ∈ {`Helvetica`, `Times-Roman`, `Courier`} and `size` ∈ [8, 10], both seeded per fill (A4
variation for the printed flavours).

- [ ] **Step 1: Failing tests**: `test_same_seed_same_fill` (`make_fill(m,1) == make_fill(m,1)`, and
  `!= make_fill(m,2)`); `test_every_blank_filled_once` (keys == blank fields); `test_every_value_fits_its_blank`
  (`reportlab.pdfbase.pdfmetrics.stringWidth(v, font, size) <= blank width − 2`; `make_fill` re-draws a
  value that does not fit and raises `ValueTooLong(field)` after 20 draws); `test_values_unique_within_document`
  (no value is a substring of another value in the same fill); `test_committed_fills_load` (12 files, all
  loading, all matching `make_fill` for their n).
- [ ] **Step 2:** Run; failing. **Step 3:** implement. **Step 4:** run `fills`; 12 files; green.
- [ ] **Step 5: FALSIFICATION** — drop the width check in `make_fill`; show `test_every_value_fits_its_blank`
  failing on at least one template; restore; green.
- [ ] **Step 6:** Commit `feat(synthetic): seeded fill specs (12)`.

### Task 4: Truth model and the form-fill flavour

**Files:**
- Create: `scripts/synthetic_contracts/truth.py`, `scripts/synthetic_contracts/overlay.py`,
  `scripts/synthetic_contracts/flavours/formfill.py`
- Test: `tests/test_synthetic_contracts_formfill.py`

**Interfaces:**
- Consumes: `Template`, `template_path`, `PartMap`, `Fill`.
- Produces: `PartTruth(id, type, boxes: tuple[Box, ...], parent)`, `ValueTruth(field, value, box: Box)`,
  `Truth(doc_id, flavour: str, templates: tuple[str, ...] (sha256), fills: tuple[str, ...], seed, review,
  parts, values, transform: tuple[float, ...] | None)`; `Truth.to_turtle() -> str`;
  `Truth.from_turtle(path) -> Truth`; `Truth.shift_pages(offset: int) -> Truth`.
  `overlay(template_pdf: Path, draw: Callable[[canvas, page_no], None]) -> pypdfium2.PdfDocument` —
  each template page and a reportlab overlay page are placed as XObjects onto a new page
  (`PdfDocument.page_as_xobject`, `as_pageobject`, `insert_obj`, `gen_content`). No pypdf: it is not
  installed and is not added.
  `render_formfill(t, m, f) -> tuple[bytes, Truth]`; flavour label `"form-fill"`.

Values are drawn as text on the blank's baseline (left-aligned at `x0 + jitter`, jitter ∈ [0, 6] pt seeded
from the fill). Value truth = the drawn string's box (from `stringWidth` and the font's ascent/descent —
exact arithmetic). Parts are copied from the map unchanged. Truth never records the output PDF's hash (G6).

- [ ] **Step 1: Failing tests** (skip if templates absent): `test_formfill_values_where_truth_says`
  (pdfplumber `crop(value.box).extract_text()` on the output equals the value, for every value — the
  oracle is an independent reader of the output, used in the test only); `test_formfill_template_text_kept`
  (same page count, and each template page's word multiset ⊆ the output page's); `test_truth_roundtrips` (`from_turtle(to_turtle(t)) == t`, CI-runnable on a hand-built `Truth`);
  `test_truth_has_no_pdf_hash` (no `syn:sha256` on the document node except the templates').
- [ ] **Step 2:** fail. **Step 3:** implement. **Step 4:** green.
- [ ] **Step 5: FALSIFICATION** — offset drawn text by +30 pt in x; show
  `test_formfill_values_where_truth_says` failing; restore; green.
- [ ] **Step 6:** Commit `feat(synthetic): truth model + form-fill flavour`.

### Task 5: Simulated handwriting + scan

**Files:**
- Create: `scripts/synthetic_contracts/flavours/handwriting.py`, `scripts/synthetic_contracts/scan.py`
- Test: `tests/test_synthetic_contracts_scan.py`

**Interfaces:**
- Consumes: `overlay`, `Truth`, `Box`.
- Produces: `affine_box(box: Box, m: np.ndarray (2×3), page_size) -> Box` (bounding box of the four
  transformed corners, clipped to the page); `degrade(img: np.ndarray, params: ScanParams) -> np.ndarray`
  — **takes no text, no fill, no truth**: it only degrades (spec § 4.3); `ScanParams(angle_deg, blur_sigma,
  noise_sd, contrast, dpi)` seeded per fill (angle ∈ [−1.5, 1.5], dpi 200);
  `render_handwriting(t, m, f) -> tuple[bytes, Truth]`; flavour label `"handwriting-scan"`.

Handwriting: each glyph drawn separately in one of the three handwriting TTFs (measured, item 5 —
chosen per fill), with per-glyph baseline jitter ±1.2 pt and size jitter ±8 %. Then the overlaid page is
rasterised (pypdfium2 `render(scale=dpi/72)`), degraded with OpenCV (`warpAffine` rotation about the page
centre, Gaussian blur, Gaussian noise, contrast), and saved as an image-only PDF at the original page size
(Pillow). Truth boxes pass through `affine_box` with the same matrix, expressed in points; `transform` on
the `Truth` records the matrix.

- [ ] **Step 1: Failing tests**: `test_affine_identity` and `test_affine_rotation_known` (90° about a known
  centre maps a known box to a known box; CI-runnable); `test_degrade_adds_no_ink` (`degrade` of an
  all-white 200×200 image: mean ≥ 240 and no 5×5 window with mean < 128); `test_degrade_takes_no_text`
  (`inspect.signature(degrade)` has exactly `img, params`); skip-if-absent:
  `test_scan_truth_boxes_contain_ink` (for every value, the transformed box on the rendered output page has
  ≥ 2 % pixels darker than 100 that were not dark in the same box of the degraded *unfilled* page);
  `test_scan_has_no_text_layer` (pdfplumber finds 0 chars).
- [ ] **Step 2:** fail. **Step 3:** implement. **Step 4:** green.
- [ ] **Step 5: FALSIFICATION** — skip `affine_box` in truth (keep un-skewed boxes) with angle forced to
  1.5°; show `test_scan_truth_boxes_contain_ink` failing; restore; green.
- [ ] **Step 6:** Commit `feat(synthetic): simulated handwriting + scan flavour`.

### Task 6: Word export flavour

**Files:**
- Create: `scripts/synthetic_contracts/docx_writer.py`, `scripts/synthetic_contracts/word.py`,
  `scripts/synthetic_contracts/flavours/wordexport.py`, `scripts/synthetic_contracts/locate.py`
- Test: `tests/test_synthetic_contracts_word.py`

**Interfaces:**
- Consumes: `PartMap` (incl. `TableGrid`), `Fill`, `Truth`.
- Produces: `template_lines(pdf, part: Part) -> list[str]` (pdfplumber words inside the part's boxes,
  joined into lines by `top`) and `grid_cells(pdf, g: TableGrid) -> list[list[str]]` (text cropped to each
  hand-measured cell) — raw extraction, PROCEDURAL, at build time only, never written to disk outside
  `synthetic/`; `write_docx(blocks: list[Block], path) -> None` (stdlib `zipfile` WordprocessingML:
  `Heading`, `Paragraph`, `Table` blocks; no python-docx — not installed and not added);
  `export_pdf(docx: Path, pdf: Path) -> None` (Word via `osascript`, converter recorded in `synthetic.ttl`
  as `syn:converter "Microsoft Word <version> via osascript"`);
  `locate(pdf: Path, needle: str) -> Box` raising `NotFound(needle)` or `Ambiguous(needle, n)`;
  `render_wordexport(t, m, f) -> tuple[bytes, Truth]`; flavour label `"word-export"`.

A blank's line is the template line whose words overlap the blank's box; the dot-leader run in it is
replaced by the value. Value truth = `locate(value)`. Part truth = union of `locate(first line)` and
`locate(last line)` of the part's real text per page — exact matching of strings the generator wrote, so
0 or > 1 hits refuses the build rather than guessing.

- [ ] **Step 1: Converter spike (measure first; settles item 4 above).** Try, in order: (a) save the PDF
  into Word's container (`~/Library/Containers/com.microsoft.Word/Data/tmp/`) and move it out;
  (b) `osascript` with `with timeout of 300 seconds` after granting access once by hand. Record the
  working command and Word's version in the task report. **If neither works without a dialog per run,
  STOP and ask the owner** — do not substitute a non-Word renderer (owner decision 6).
- [ ] **Step 2: Failing tests**: `test_docx_opens` (the written `.docx` is a valid zip with
  `word/document.xml` parseable and one `w:tbl` per `Table` block; CI-runnable); `test_locate_refuses_ambiguous`
  and `test_locate_refuses_missing` (on a reportlab-made two-line PDF; CI-runnable); skip-if-no-Word:
  `test_wordexport_values_where_truth_says` (as Task 4's, on the Word output);
  `test_wordexport_carries_real_text` (≥ 95 % of the template's words for each part appear in the output's
  text, multiset-compared — the owner's decision 10).
- [ ] **Step 3:** fail. **Step 4:** implement. **Step 5:** green.
- [ ] **Step 6: FALSIFICATION** — make `locate` return the first hit instead of raising on > 1; show
  `test_locate_refuses_ambiguous` failing; restore; green.
- [ ] **Step 7:** Commit `feat(synthetic): Word export flavour`.

### Task 7: Build, mixed documents, agreement, leak guard

**Files:**
- Create: `scripts/synthetic_contracts/build.py`, `scripts/synthetic_contracts/agreement.py`
- Create: `examples/synthetic-contracts/mixed/{m1,m2,m3}.ttl`; generated and committed:
  `examples/synthetic-contracts/truth/*.ttl` (39 files); `examples/synthetic-contracts/README.md`
  (how to fetch and build; licence; the anti-goals A1 and A2 verbatim: fake, never enforced, reproduced or
  shared; passing on simulated handwriting proves nothing about real scans)
- Test: `tests/test_synthetic_contracts_build.py`, `tests/test_synthetic_contracts_leak.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `build(root=SYNTH_ROOT) -> list[Path]` (verifies every template first; writes
  `synthetic/out/<doc_id>.pdf` and `truth/<doc_id>.ttl`; `doc_id` = `<fill-id>.<flavour>` or `<mixed-id>`);
  `compose(parts: list[tuple[bytes, Truth]]) -> tuple[bytes, Truth]` (`import_pages`, `shift_pages`);
  `agree(a: Truth, b: Truth) -> list[str]` (differences in `(field, value)` sets and part-type multisets,
  coordinates ignored; empty means agreement).

Mixed (spec § 4.4): **m1** = `gafta-48-1` form-fill + No. 124 *unfilled* (template pages as-is, truth =
its map's parts, no values); **m2** = `gafta-79b-2` word-export + `usda-ffp-cp-2` form-fill;
**m3** = `gafta-48-3` form-fill + `gafta-48-3` handwriting-scan (the flavour change inside one PDF).

- [ ] **Step 1: Failing tests**: `test_mixed_truth_offsets_pages` (CI-runnable on hand-built truths: the
  second part's pages start at first's page count + 1); `test_agreement_across_flavours` (skip-if-absent:
  for each of the 12 fills, `agree` over its three truths is empty); `test_build_counts` (skip-if-absent:
  39 PDFs, 39 truth files, each truth's template sha256s ∈ the manifest); `test_no_reader_sees_truth`
  (CI-runnable: no file under `src/`, `scripts/` outside `scripts/synthetic_contracts/`, `readings/`, or
  `tests/` other than `tests/test_synthetic_contracts_*.py` contains `synthetic_contracts` or
  `synthetic-contracts/truth`); `test_committed_truth_conforms` (all 39 conform to `shapes.ttl`).
- [ ] **Step 2:** fail. **Step 3:** implement; run `build`; 39 + 39.
- [ ] **Step 4:** green; full suite `PYTHONPATH=src ../../../.venv/bin/python -m pytest -q` — read
  `N passed`, not the exit code; and `PYTHONPATH=src ../../../.venv/bin/python scripts/corpus_baseline.py
  check` passes (no baseline input touched).
- [ ] **Step 5: FALSIFICATION** — add `import scripts.synthetic_contracts` to any `src/` module (in the
  working tree only); show `test_no_reader_sees_truth` failing; restore with `git checkout -- <file>`; green.
- [ ] **Step 6:** Commit `feat(synthetic): build, mixed documents, agreement, leak guard`; push; PR body
  lists the owner's review items: the four maps (`syn:review` flip) and the converter choice.
