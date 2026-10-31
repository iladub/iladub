# A synthetic contract set — fake filled contracts to develop the router and the contract compiler on (design, 2026-10-31)

**Serves:** maintenance — project 1 of the three that the contract:01 rescope became (handoff
`docs/superpowers/2026-10-31-handoff-document-router-brainstorm.md`). No criterion exists for it yet.

**Topic:** contract · **Date:** 2026-10-31

**Doc impact: none.** It adds a generator script, fill specs and a truth format. No vocabulary,
shape or released page changes.

**Status: DRAFT for the maintainer.** It writes up the 2026-10-31 brainstorm. Each statement is
marked **(owner)** if the owner decided it in chat, and **(call)** if it is the author's call, open
to correction.

## 1. Intent

The document router (project 2) and contract compiling (project 3) need documents to be developed
on, and those documents need known answers. Real filled contracts are not available, and they could
not be used if they were. So iladub **makes its own**: real blank contract templates, filled with
fake values, in the forms a reader actually meets (a filled PDF form, a Word document exported to
PDF, a handwritten form that was scanned). Because iladub made every fill, it knows the answer for
each one.

The set's first job is the router's first proof: **route a GAFTA form and its tables correctly**
(owner). Contract compiling consumes it after that.

## 2. Goals, non-goals, anti-goals

**Goals**

- G1. Filled contracts made from **real templates**, filled **synthetically** (owner). Real
  contracts come later (owner).
- G2. **Three flavours of every filled contract** (owner):
  1. **form fill**: the values written into the PDF itself, the way a form is filled;
  2. **Word export**: a Word document with the values inline in the text, exported to PDF;
  3. **simulated handwriting**: the values handwritten onto the printed form, then scanned. The
     handwriting is simulated, not real.
- G3. **Two domains**, so nothing in the set or its truth names one domain's terms (decision 18 of
  `specs/2026-10-30-hdc-first-contract-compiler-design.md`): **GAFTA** forms and the **USDA Food
  for Progress charter party**, and only that charter party for now (owner).
- G4. **Truth for every generated document**, written by the generator, kept where the router
  cannot see it (call).
- G5. **Mixed documents**: some generated documents join several parts (e.g. a contract followed by
  the rules it incorporates), because the router must split them (owner: "mixed documents are
  split"). Building them from the set's own parts is the author's call.
- G6. **Regenerable**: one command rebuilds every PDF from the committed fill specs and the pinned
  templates, with the same content (call). **Not byte for byte**: Word export stamps times and IDs
  on every run, so the committed truth never records a PDF's hash (§ 4.5); it records what the PDF
  was made from.

**Non-goals**

- The router and the contract compiler themselves (projects 2 and 3).
- DRYVOY, TANKVOY, BIMCO and other charter parties (owner: deferred; DRYVOY also needs a browser
  download, since curl gets `Access Denied`).
- Real contracts, real parties, real trades.
- Scoring or ranking the router. The set supplies the truth; the router's criterion defines the
  oracle.

**Anti-goals**

- A1. **These contracts are fake, and are never enforced, reproduced or shared** (owner). They exist
  to develop on. That is also how the licence question (O4 in the HDC-first spec) is settled for
  GAFTA and USDA alike: the filled PDFs stay on the owner's machine.
- A2. **Passing on simulated handwriting proves nothing about real scans** (call). No document or
  criterion may claim it does.
- A3. **Truth that leaks to the reader.** If the router can read the truth, or the generator's
  layout choices, the proof is void (call).
- A4. **Overfitting to the generator.** Whatever the generator does uniformly (one font, one
  position per field, one noise recipe) a reader can learn by accident. The flavours and fills must
  vary enough that the generator's habits aren't the signal (call; the amount of variation is the
  builder's, § 6).

## 3. Constraints

- **What is committed, and what is not (owner, 2026-10-31).** The repo is public.
  - **Committed:** the generator, the fill specs (fake values) and the truth.
  - **Never committed:** the templates and the filled PDFs. They are rebuilt locally from templates
    the owner downloads.
  - This is the split `corpus/` and `held-out/` already use (`.gitignore:51-55`).
- **No template text is committed** (contract-rung spec § 6.6, "GAFTA text is never committed").
  Truth and fill specs carry fake values, page numbers, coordinates and part labels. They never
  carry a template's own words. Templates are identified by name and **sha256**, and the committed
  manifest pins those hashes.
- **Outside `corpus/` and outside every baseline input** (call). `corpus/` is swept by the baseline
  snapshot, and every tracked path under `src/`, `vocab/`, `readings/` is a baseline input (CLAUDE.md
  § Corpus baseline). Anything added there forces a 24-minute regenerate and changes the committed
  blast radius. Proposed home:
  - generator: `scripts/synthetic_contracts/` (not a baseline input; only
    `scripts/corpus_baseline.py` and `scripts/corpus_verdict_snapshot.py` are);
  - fill specs + truth + template manifest: `examples/synthetic-contracts/`;
  - templates and PDFs: a gitignored top-level `synthetic/`.
- **Neurosymbolic gate (CLAUDE.md § 8).** The generator **makes** documents; it reads none. Making
  a fixture is not a reading decision, so it is PROCEDURAL by nature, and its noise and jitter
  constants are generation parameters, not tolerances a reading depends on. Its module docstring
  says so. Nothing in the generator may later be reused to **read** a document.
- **Licences:** code Apache-2.0, fill specs and truth CC-BY-4.0, author metadata as usual.

## 4. The set

### 4.1 Templates

- **GAFTA (call):** start with three of the 90 forms on https://www.gafta.com/contracts (paged with
  `?page=2..6`), chosen for what they test:
  - **No. 124**, Sampling Rules: p6 has a 7×6 ruled metric table, the only real metric table found
    in the 2026-10-31 survey;
  - **No. 79B**: a blank quality table **nested inside clause 6** (p1–2), which tests parts inside
    parts;
  - **No. 48**: a clause contract with no table, as the control.
  The survey figures (pdfplumber `find_tables()`, rows ≥ 2 and cols ≥ 2) are unverified until
  re-fetched (handoff § 4).
- **USDA Food for Progress charter party** (owner), 13 pp.:
  https://omb.report/icr/201404-0551-002/doc/47577601.pdf.

The builder re-fetches all four and records their sha256 in the manifest. The set is designed to
grow: adding a template means adding a fill spec, not changing the generator.

### 4.2 Fills

- **Values (call):** fake but plausible for the domain, from a **seeded** generator, so the same
  seed gives the same values: commodity, quantity, price, parties, ports, dates, quality figures.
  The fill specs are committed, so the values are fixed data, not regenerated randomness.
- **Onto the real template (call):** the values are placed in the template's own blanks. Nothing is
  retyped.
- **How many (call):** start small: **3 fills per fillable template × 3 flavours**, plus the mixed
  documents (§ 4.4). If all four templates have blanks that is 36 PDFs. **No. 124 is a rules
  document**: if the builder measures no blanks in it, it is not filled, and it appears only as an
  unfilled part of mixed documents (the rules a contract incorporates). It grows only when a router
  experiment needs more.

### 4.3 Flavours

- **Form fill.** If a template has AcroForm fields, fill them. If it has none, draw the values as
  text in a layer over the blanks. Whether GAFTA's and USDA's PDFs have fields is **unmeasured**;
  the builder checks first.
- **Word export.** A Word document carries the values inline in running text, and is exported to
  PDF. Two things to settle:
  - Word-exported PDFs are a different object from filled templates, so this flavour rebuilds the
    template in Word: its **structure** (headings, clause numbering, the table) and its **real
    text**, extracted from the downloaded template at build time (owner, 2026-10-31). The same
    words then appear in all three flavours, so the agreement check of § 4.5 means something. The
    text never enters committed code or files; like the others, this flavour depends on the local
    template.
  - The machine has Microsoft Word and neither LibreOffice nor pandoc (measured 2026-10-31).
    Automating Word on macOS is not portable; the builder picks the converter and records it.
- **Simulated handwriting.** The values are drawn in handwriting-style fonts with per-glyph jitter,
  on the printed form; the page is then degraded like a scan (skew, blur, noise, contrast). Library
  choice is the builder's. **No value may be invented by the scan step**; it only degrades.

### 4.4 Mixed documents

A mixed document is the concatenation of parts the set already has (call):
- a contract followed by the rules it incorporates (e.g. a contract + No. 124 Sampling Rules);
- a GAFTA form and the charter party in one PDF;
- one with a flavour change inside it (a typed contract followed by a handwritten one).
Start with **3**.

### 4.5 Truth

One truth record per generated PDF (call), in **Turtle** (the repo's authoring format), written by
the generator, never read by the router at run time. It records:

- **document level:** which template(s) (by manifest sha256), which flavour, which fill spec, and
  the seed. Not the output PDF's hash (G6);
- **part level:** for each part, its page range and region and its part type, at the **router's
  granularity** (call): document parts (*contract form*, *rules*, *charter party*) and, within a
  form, *table* and *blank*. Clause-level truth is project 3's and is not built here.
  - A **per-template part map** is authored once by hand, in the template's coordinates: labels and
    coordinates only, no template text. The builder drafts it; the **owner reviews it** before it is
    labelled human truth (call).
  - **Truth is always in the output page's own coordinates** (call). The generator writes it as it
    lays out each flavour, since it knows where it put everything: the form-fill flavour copies the
    template map; the Word flavour records where its own layout put each part; the scan step
    applies its skew and scale to the coordinates too. A mixed document composes its parts' truth
    with page offsets.
- **value level:** each filled value, the field it fills, and where it was placed on the page.

**Agreement across flavours** is a second check (call): the three flavours of one fill must yield
the same values and the same parts, so a reader that gives different answers on them is wrong on at
least one, even before the truth is consulted.

**A3 is enforced mechanically** (call): a test fails if any module outside
`scripts/synthetic_contracts/` names the truth directory or imports the generator. Router
experiments receive PDFs only.

Truth is **document-type neutral**: part types are plain labels in the truth file, not a type tree.
Designing the type tree and its DoCO/FaBiO alignment is the router's job (project 2).

## 5. What the owner decided (2026-10-31, in chat)

1. A document router comes before the compilers; the set is designed first, on its own.
2. Mixed documents are split, and each part goes to its own compiler.
3. The router proposes new types; the owner admits them.
4. First proof: route a GAFTA form and its tables correctly.
5. The examples are filled synthetically; real contracts come later.
6. Three flavours: PDF form fill, Word export, simulated handwriting scan.
7. The second domain is the USDA charter party alone for now.
8. The contracts are fake: never enforced, reproduced or shared.
9. The generator, the fill specs and the truth are committed. The filled PDFs are regenerated
   locally from templates the owner downloads.
10. The Word flavour uses the template's real text, extracted at build time and never committed.

## 6. Left to the builder

- Libraries for PDF filling, overlay, handwriting fonts and scan degradation, and the Word
  converter. Record each choice and its version.
- The exact fill-spec and truth vocabulary, within § 4.5 and the source-ownership rule (owned
  terms only; `etkl:`/`iladub:` or a namespace the plan proposes).
- How much variation is enough for A4 (fonts, positions, noise), as long as the plan says what
  varies.
- Whether the part maps carry regions as bounding boxes or as page-and-line spans.
- How the scan step's coordinate transform is represented, as long as truth stays in output
  coordinates (§ 4.5).
- The CLI: one command to fetch-and-verify templates, one to build. The build refuses if a
  template's sha256 differs from the manifest.

## 7. Open

- ~~O1. The Word flavour's text.~~ **Ruled (owner, 2026-10-31): real text**, extracted from the
  local template at build time (§ 4.3).
- **O2.** The USDA form's public-domain status rests on the general rule for US federal works and a
  2014 OMB filing. Under A1 it no longer blocks anything; it matters only if the set is ever shared.
