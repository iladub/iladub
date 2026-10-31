# Synthetic contract set

Fake filled contracts made from four real, published templates (GAFTA No. 48, No. 79B, No. 124 and
the USDA Food for Progress charter party), each with a Turtle truth record. The set exists to
develop the document router on. Spec: `docs/superpowers/specs/2026-10-31-synthetic-contract-set-design.md`.

## Anti-goals

- **A1. These contracts are fake, and are never enforced, reproduced or shared.** They exist to
  develop on. The filled PDFs stay on the owner's machine.
- **A2. Passing on simulated handwriting proves nothing about real scans.** No document or
  criterion may claim it does.

## What is committed, and what is not

Committed here: the template manifest (`templates.ttl`, pinned by sha256), the hand-drafted part
maps (`maps/`, `syn:review "draft"` until the owner reviews them), the fill specs (`fills/`), the
mixed-document specs (`mixed/`), the truth records (`truth/`), the vocabulary (`synthetic.ttl`) and
its shapes (`shapes.ttl`, with negatives under `negative/`). None of them carries template text.

Never committed: the templates, the built PDFs and the Word documents. They live under the
gitignored `synthetic/` at the repo root.

The truth is for checking a reader's output, never for a reader to see: nothing outside the
generator's package and its own tests may import the generator or name the truth directory
(`tests/test_synthetic_contracts_leak.py`). A router experiment receives PDFs only.

## Fetch and build

From the repo root, with the repo's virtual environment:

```sh
PYTHONPATH=src .venv/bin/python -m scripts.synthetic_contracts fetch
PYTHONPATH=src .venv/bin/python -m scripts.synthetic_contracts build
```

`fetch` downloads any absent template and checks every template's sha256 against the manifest; a
template whose sha256 differs is reported and removed (the URL now serves another edition). `build`
refuses unless every template matches, then writes 39 PDFs to `synthetic/out/` (12 fills in three
flavours, plus the three mixed documents `m1`, `m2`, `m3`) and their 39 truth records to `truth/`.

The build is local: the handwriting flavour needs OpenCV and the macOS handwriting fonts under
`/System/Library/Fonts/Supplemental/`, and the Word flavour drives Microsoft Word for macOS through
`osascript` (the converter is recorded as `syn:converter` in `synthetic.ttl`). It rebuilds the same
content, not the same bytes: Word stamps times and IDs on every export, so a truth record never
records its PDF's hash.

Then check the set:

```sh
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_synthetic_contracts_build.py tests/test_synthetic_contracts_leak.py
```

## Licence

The files in this directory are CC-BY-4.0, François Rosselet. The generator under
`scripts/synthetic_contracts/` is Apache-2.0. The templates belong to their publishers and are not
redistributed.
