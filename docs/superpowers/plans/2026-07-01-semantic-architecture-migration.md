# iladub Namespace Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Re-root every owned IRI from `https://w3id.org/etkl/*` to `https://w3id.org/iladub/*`, split the fabric holon-types out of the `iladub` core into the `etkl` module, and rename the `hol:` module to `dec:` — a **behaviour-preserving** migration (same test pass/skip counts throughout).

**Architecture:** Two kinds of change. (1) A **non-uniform split**: the doc-holon fabric (`RawDocumentHolon` … `MembraneHealth`, currently `iladub:` in `iladub-holons.ttl`) moves to the `etkl:` prefix; the `iladub` core keeps only the assertion/proposition epistemics. (2) A **uniform re-rooting** of all IRIs + the `hol:`→`dec:` prefix rename, applied by one ordered string-replacement script. Do the split first (Task 1) while IRIs are still on the `etkl` root, then re-root everything uniformly (Task 2).

**Tech Stack:** Python 3.12, rdflib, pySHACL, pytest. RDF Turtle. Migration performed by a Python script (portable; avoids BSD/GNU `sed` differences).

**Reference:** design at `docs/superpowers/specs/2026-07-01-semantic-architecture-design.md`.

**Test command (this repo):** always use the venv interpreter so `baml_client` + `iladub` resolve:
```bash
.venv/bin/python -m pytest -q
```
**Baseline before starting:** `134 passed, 4 skipped`. Every task must preserve this.

**Target IRI map (authoritative — used by Task 2's script, ordered longest-first):**

| Old | New |
|---|---|
| `https://w3id.org/etkl/iladub/hga-alignment` | `https://w3id.org/iladub/hga-alignment` |
| `https://w3id.org/etkl/iladub/holons` | `https://w3id.org/iladub/etkl/holons` |
| `https://w3id.org/etkl/iladub#` | `https://w3id.org/iladub#` |
| `https://w3id.org/etkl/iladub` | `https://w3id.org/iladub` |
| `https://w3id.org/etkl/hol/hga-alignment` | `https://w3id.org/iladub/dec/hga-alignment` |
| `https://w3id.org/etkl/hol#` | `https://w3id.org/iladub/dec#` |
| `https://w3id.org/etkl/hol` | `https://w3id.org/iladub/dec` |
| `https://w3id.org/etkl/risk/hga-alignment` | `https://w3id.org/iladub/risk/hga-alignment` |
| `https://w3id.org/etkl/risk#` | `https://w3id.org/iladub/risk#` |
| `https://w3id.org/etkl/risk` | `https://w3id.org/iladub/risk` |
| `https://w3id.org/etkl/governance-shapes#` | `https://w3id.org/iladub/governance-shapes#` |
| `https://w3id.org/etkl#` | `https://w3id.org/iladub/etkl#` |
| `https://w3id.org/etkl` | `https://w3id.org/iladub/etkl` |

**Fabric term set (moves `iladub:` → `etkl:`):** `DocumentHolon`, `RawDocumentHolon`, `SemanticHolon`, `AlignmentHolon`, `CleanDocumentHolon`, `GroundingPortal`, `MembraneHealth`, `Intact`, `Weakened`, `Compromised`, `membraneHealth`, `throughPortal`, `reconciles`. (**`SourceRegion` is NOT fabric** — it is a core term in `iladub.ttl`, referenced as the range of `reconciles`; it stays `iladub:`.)

---

## Task 1: Split the fabric out of the `iladub` core into `etkl`

Done first, while IRIs are still on the `etkl` root, so the suite stays consistent. After this task, fabric terms live at `etkl:` (= `https://w3id.org/etkl#` for now); Task 2 re-roots them with everything else.

**Files:**
- Rename: `vocab/ontology/iladub-holons.ttl` → `vocab/ontology/etkl-holons.ttl`
- Modify: `vocab/ontology/etkl-holons.ttl`, `vocab/ontology/iladub-hga-align.ttl`, `tests/test_hga_alignment.py`

- [ ] **Step 1: Rename the fabric file**

```bash
git mv vocab/ontology/iladub-holons.ttl vocab/ontology/etkl-holons.ttl
```

- [ ] **Step 2: Reassign fabric CURIEs `iladub:`→`etkl:` in the two vocab files, and declare the `etkl:` prefix where missing**

Write this script to `/tmp/split_fabric.py` and run it with `.venv/bin/python /tmp/split_fabric.py`:

```python
import pathlib

FABRIC = ["CleanDocumentHolon", "RawDocumentHolon", "AlignmentHolon", "SemanticHolon",
          "DocumentHolon", "GroundingPortal", "MembraneHealth", "membraneHealth",
          "throughPortal", "reconciles", "Compromised", "Weakened", "Intact"]

for rel in ["vocab/ontology/etkl-holons.ttl", "vocab/ontology/iladub-hga-align.ttl"]:
    p = pathlib.Path(rel)
    t = p.read_text(encoding="utf-8")
    for term in FABRIC:                       # longest-first; none is a substring of another
        t = t.replace(f"iladub:{term}", f"etkl:{term}")
    # ensure the etkl: prefix is declared (both files already declare iladub:)
    if "@prefix etkl:" not in t:
        t = t.replace('@prefix iladub: <https://w3id.org/etkl/iladub#> .',
                      '@prefix iladub: <https://w3id.org/etkl/iladub#> .\n'
                      '@prefix etkl:   <https://w3id.org/etkl#> .', 1)
    p.write_text(t, encoding="utf-8")
    print("split", rel)
```

- [ ] **Step 3: Retitle `etkl-holons.ttl` so it reads as an etkl-module file**

Edit `vocab/ontology/etkl-holons.ttl`: change the ontology `dcterms:title` from
`"iladub — holon-interaction types"@en` to `"etkl — holon-production fabric"@en`, and update
the header comment block's first line from `#  iladub's holon-interaction types.` to
`#  etkl's holon-production fabric (moved from the iladub core 2026-07-01).` (Leave the
ontology IRI `<https://w3id.org/etkl/iladub/holons>` as-is; Task 2 re-roots it.)

- [ ] **Step 4: Update `tests/test_hga_alignment.py` for the fabric's new prefix + the file rename**

The fabric alignment axioms now use the `etkl` base, and the standalone test reads the renamed file. Apply these exact edits:

Add an `ETKL` base constant next to the existing ones (near `ILADUB = "https://w3id.org/etkl/iladub#"`):
```python
ETKL = "https://w3id.org/etkl#"
```
In `test_alignment_axioms_present`, change the assertion loop to use `ETKL` for the fabric subjects (they are no longer `iladub:`):
```python
    for sub, obj in expected:
        assert (URIRef(ETKL + sub), RDFS.subClassOf, URIRef(HOLON + obj)) in g, \
            f"missing alignment: etkl:{sub} rdfs:subClassOf holon:{obj}"
```
In `test_holons_module_standalone`, change the path `"iladub-holons.ttl"` → `"etkl-holons.ttl"` and its assertion message accordingly.

- [ ] **Step 5: Verify the suite is green (still on the etkl root)**

Run: `.venv/bin/python -m pytest -q`
Expected: `134 passed, 4 skipped`.
Also run: `.venv/bin/python -m pytest tests/test_source_ownership.py tests/test_hga_alignment.py -v`
Expected: all pass (fabric now `etkl:`, still under `w3id.org/etkl`, so source-ownership "ours" checks still hold).

- [ ] **Step 6: Commit**

```bash
git add vocab/ontology/etkl-holons.ttl vocab/ontology/iladub-hga-align.ttl tests/test_hga_alignment.py
git commit -m "refactor(vocab): move doc-holon fabric from iladub core to etkl module"
```

---

## Task 2: Re-root all IRIs (`etkl/* → iladub/*`) + rename `hol:`→`dec:`

The uniform mechanical migration. One ordered-replacement script over the functional artifacts (vocab, examples, tests, src), then file renames, then the one manual special-case.

**Files:** all `vocab/ontology/*.ttl`, `vocab/shapes/*.ttl`, `examples/**/*.ttl`, `examples/**/*.md`, `tests/*.ttl`, `tests/*.py`, `src/iladub/*.py`. (Docs prose + CLAUDE.md are Task 3 — do **not** run the script on them.)

- [ ] **Step 1: Write and run the migration script**

Write this to `/tmp/migrate_ns.py` and run `.venv/bin/python /tmp/migrate_ns.py`:

```python
import re, pathlib, glob

REPLACEMENTS = [  # ORDER MATTERS — longest / most-specific first
    ("https://w3id.org/etkl/iladub/hga-alignment", "https://w3id.org/iladub/hga-alignment"),
    ("https://w3id.org/etkl/iladub/holons",        "https://w3id.org/iladub/etkl/holons"),
    ("https://w3id.org/etkl/iladub#",              "https://w3id.org/iladub#"),
    ("https://w3id.org/etkl/iladub",               "https://w3id.org/iladub"),
    ("https://w3id.org/etkl/hol/hga-alignment",    "https://w3id.org/iladub/dec/hga-alignment"),
    ("https://w3id.org/etkl/hol#",                 "https://w3id.org/iladub/dec#"),
    ("https://w3id.org/etkl/hol",                  "https://w3id.org/iladub/dec"),
    ("https://w3id.org/etkl/risk/hga-alignment",   "https://w3id.org/iladub/risk/hga-alignment"),
    ("https://w3id.org/etkl/risk#",                "https://w3id.org/iladub/risk#"),
    ("https://w3id.org/etkl/risk",                 "https://w3id.org/iladub/risk"),
    ("https://w3id.org/etkl/governance-shapes#",   "https://w3id.org/iladub/governance-shapes#"),
    ("https://w3id.org/etkl#",                     "https://w3id.org/iladub/etkl#"),
    ("https://w3id.org/etkl",                      "https://w3id.org/iladub/etkl"),
]

files = (glob.glob("vocab/ontology/*.ttl") + glob.glob("vocab/shapes/*.ttl")
         + glob.glob("examples/**/*.ttl", recursive=True)
         + glob.glob("examples/**/*.md",  recursive=True)
         + glob.glob("tests/*.ttl") + glob.glob("tests/*.py")
         + glob.glob("src/iladub/*.py"))

for rel in sorted(set(files)):
    p = pathlib.Path(rel)
    t = orig = p.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS:
        t = t.replace(old, new)
    if p.suffix in (".ttl", ".md"):
        t = t.replace("hol:", "dec:")   # CURIE prefix rename; 'holon:' is NOT affected ('hol:' != 'holon:')
        t = t.replace('sh:prefix "hol"', 'sh:prefix "dec"')  # SHACL SPARQL prefix decl (no colon — missed above)
    if p.suffix == ".py":
        t = re.sub(r"(?<![A-Za-z0-9])HOL(?![A-Za-z0-9])", "DEC", t)  # HOL / _HOL / HOL_NS constants; HOLON untouched
    if t != orig:
        p.write_text(t, encoding="utf-8")
        print("migrated", rel)
```

- [ ] **Step 2: Rename the `hol`-named files to `dec`**

```bash
git mv vocab/ontology/hol.ttl        vocab/ontology/dec.ttl
git mv vocab/ontology/hol-hga-align.ttl vocab/ontology/dec-hga-align.ttl
git mv vocab/shapes/hol-shapes.ttl   vocab/shapes/dec-shapes.ttl
git mv tests/hol-bad.ttl             tests/dec-bad.ttl
```

- [ ] **Step 3: Fix references to the renamed files in Python tests**

Any test that parses these files by name must use the new names. Find them:
```bash
grep -rn "hol\.ttl\|hol-shapes\.ttl\|hol-hga-align\.ttl\|hol-bad\.ttl" tests/ src/
```
For each hit, edit the string: `hol.ttl`→`dec.ttl`, `hol-shapes.ttl`→`dec-shapes.ttl`, `hol-hga-align.ttl`→`dec-hga-align.ttl`, `hol-bad.ttl`→`dec-bad.ttl`. (Known: `tests/test_decision.py`, `tests/test_reopen.py`, `tests/test_escalation_shacl.py`, `tests/test_event_shacl.py`, `tests/test_timeline_shacl.py`, `tests/test_hga_alignment.py` reference `hol-shapes.ttl`/`hol.ttl`; `tests/test_hga_alignment.py` references `hol-hga-align.ttl`. Verify with the grep — fix exactly what it reports.)

- [ ] **Step 4: Fix the one special case — `tests/test_source_ownership.py` `ours`**

The script's bare-`etkl` rule turned `ours = "https://w3id.org/etkl"` into `"https://w3id.org/iladub/etkl"`, which is too specific (it must match ALL our terms: core `iladub#`, `iladub/dec#`, `iladub/risk#`, `iladub/etkl#`). Set it to the root:
```python
    ours = "https://w3id.org/iladub"
```
(Leave `HGA_BASE = "http://w3id.org/holon/"` unchanged — it was never an `etkl` string.)

- [ ] **Step 5: Verify — suite green, no residual `etkl` IRIs, ownership intact**

Run: `.venv/bin/python -m pytest -q`
Expected: `134 passed, 4 skipped`.

Run the residual check (must print nothing):
```bash
grep -rn "w3id.org/etkl" vocab examples tests src
```
Expected: no output. (If anything remains, it's a missed reference — fix it and re-run.)

Confirm the new roots resolve internally:
```bash
grep -rl "w3id.org/iladub" vocab | sort | head
```
Expected: the migrated vocab files listed.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "refactor(ns): re-root etkl/* -> iladub/*; rename hol module to dec"
```

---

## Task 3: Docs prose, databooks, README, and finalize CLAUDE.md

The functional migration is done; now update human-facing references and flip CLAUDE.md from "migration pending" to "migrated".

**Files:** `docs/*.md`, `vocab/README.md`, `README.md` (repo root, if it references IRIs), `CLAUDE.md`, any `examples/**/*.databook.md` prose not already handled.

- [ ] **Step 1: Migrate prose IRI references**

Run the same replacement table over the docs (reuse `/tmp/migrate_ns.py`'s `REPLACEMENTS`, `hol:`→`dec:` for `.md`). Write `/tmp/migrate_docs.py`:

```python
import pathlib, glob
from importlib.machinery import SourceFileLoader
REPLACEMENTS = SourceFileLoader("m", "/tmp/migrate_ns.py").load_module().REPLACEMENTS
for rel in sorted(set(glob.glob("docs/*.md") + ["vocab/README.md", "README.md"])):
    p = pathlib.Path(rel)
    if not p.exists():
        continue
    t = orig = p.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS:
        t = t.replace(old, new)
    t = t.replace("hol:", "dec:")
    if t != orig:
        p.write_text(t, encoding="utf-8"); print("migrated", rel)
```
Run `.venv/bin/python /tmp/migrate_docs.py`.

- [ ] **Step 2: Fix prose that names the old modules by concept (manual)**

Grep docs for stale module framing and correct it by hand where the *words* (not just IRIs) are wrong:
```bash
grep -rn "etkl/hol\|holonic decision-context\|document compiler\b\|umbrella" docs/*.md
```
Update: `docs/hol.md` → rename its concept to "dec — the decidability / decisionality layer" (retitle heading, keep content); `docs/etkl.md` "Modules" line and `docs/index.md`/`docs/naming.md` namespace lines → the new `w3id.org/iladub` root. Keep edits minimal and factual — don't rewrite the docs, just correct the naming/IRIs. Rename `docs/hol.md` → `docs/dec.md` and fix its link in `docs/index.md`.

- [ ] **Step 3: Finalize CLAUDE.md (migration complete)**

In `CLAUDE.md`: in the Serialization § namespace bullet, drop the "current (pre-migration)" line and keep only the target IRIs as the live values (`iladub:` = `https://w3id.org/iladub#`, `etkl:` = `https://w3id.org/iladub/etkl#`, `dec:` = `https://w3id.org/iladub/dec#`, `risk:` = `https://w3id.org/iladub/risk#`). In the "project family" §, change "the re-rooting … is planned but NOT yet executed" to "the re-rooting … was completed 2026-07-01 (old `w3id.org/etkl/*` IRIs 301-redirect to the new roots once the w3id PR merges — Task 4)." In the Source-ownership §, drop the "pre-migration `…/etkl…`" parenthetical and the "was `hol:`" note (now simply `dec:`), and in Concrete rule 2 update the core-ontology filename list to `dec.ttl, risk.ttl, iladub.ttl, etkl.ttl, etkl-holons.ttl`.

- [ ] **Step 4: Verify docs build references + no stale IRIs in prose**

Run (must print nothing):
```bash
grep -rn "w3id.org/etkl" docs vocab/README.md README.md CLAUDE.md
```
Expected: no output. Then re-run the full suite to be safe: `.venv/bin/python -m pytest -q` → `134 passed, 4 skipped`.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs: migrate prose/IRIs to iladub root; finalize CLAUDE.md; hol.md -> dec.md"
```

---

## Task 4: Draft the w3id.org redirect configuration

Deliverable for submission to `perma-id/w3id.org` (external; the author submits — see the design doc's w3id note). This task produces the config file(s) and instructions; it does **not** submit anything.

**Files:** Create `docs/w3id/iladub-htaccess.md` (a documented redirect spec).

- [ ] **Step 1: Write the redirect spec**

Create `docs/w3id/iladub-htaccess.md` describing the `w3id.org/iladub` entry, modelled on the existing `w3id.org/etkl` registration (PR #6144). It must specify: content negotiation (Accept: text/turtle / application/rdf+xml / application/ld+json → the raw `.ttl` on GitHub `main`; default/browser → `https://iladub.dev`), for the base `/iladub` and each sub-path (`/iladub/etkl`, `/iladub/dec`, `/iladub/risk`, `/iladub/hga-alignment`, `/iladub/etkl/holons`, `/iladub/governance-shapes`); and **301 redirects from every old `/etkl*` path to its new `/iladub*` path** (per the Target IRI map above) so the dated record is preserved. Include the exact `.htaccess` rewrite rules (RewriteCond on `%{HTTP_ACCEPT}`, RewriteRule per path) and a one-paragraph submission note (submit as a PR to `perma-id/w3id.org` under the author's GitHub account; a w3id maintainer merges, as dgarijo did for #6144).

- [ ] **Step 2: Commit**

```bash
git add docs/w3id/iladub-htaccess.md
git commit -m "docs(w3id): draft iladub redirect config + etkl->iladub 301s for submission"
```

---

## Final verification

- [ ] **Full suite:** `.venv/bin/python -m pytest -q` → `134 passed, 4 skipped` (unchanged — behaviour preserved).
- [ ] **No residual old IRIs anywhere:** `grep -rn "w3id.org/etkl" . --include=*.ttl --include=*.py --include=*.md` prints nothing except inside `docs/w3id/iladub-htaccess.md` (which documents the old→new 301s) and the two migration spec/plan docs (which reference the old IRIs by design).
- [ ] **Source-ownership + alignment green:** `.venv/bin/python -m pytest tests/test_source_ownership.py tests/test_hga_alignment.py -v`.
- [ ] Dispatch the final whole-migration review, then use `superpowers:finishing-a-development-branch`.

## Self-review notes (author)

- **Spec coverage:** re-rooting (Task 2) ✓; fabric split iladub→etkl (Task 1) ✓; `hol:`→`dec:` rename + file renames (Task 2) ✓; risk stays its own module — the script re-roots `etkl/risk` → `iladub/risk` without merging into dec ✓; source-ownership boundary preserved (`ours` → `https://w3id.org/iladub`, Task 2 Step 4) ✓; w3id resolution + 301s drafted (Task 4) ✓; "no functional change" enforced by the constant `134 passed / 4 skipped` gate at every task.
- **Ordering safety:** the IRI replacement list is longest-first, so nested paths (`/etkl/iladub`, `/etkl/hol`, `/etkl/risk`, `/etkl/governance-shapes`) are consumed before bare `/etkl#` and `/etkl`; the produced `.../iladub/etkl...` strings never re-match `https://w3id.org/etkl`.
- **`hol:`→`dec:` safety:** `holon:` does not contain the substring `hol:` (the char after `hol` is `o`, not `:`), so the HGA prefix is untouched. The Python `HOL` regex excludes `HOLON`. The SHACL SPARQL prefix *declaration* `sh:prefix "hol"` (a bare string, no colon) is handled by its own explicit replace — without it the shapes' SPARQL would reference an undeclared `dec:` prefix and fail (the escalation + dec shapes both use `sh:declare`).
- **The one manual special-case** (`test_source_ownership.py` `ours`) is called out explicitly in Task 2 Step 4 — the blind script would otherwise mis-set it to `/iladub/etkl`.
- **`SourceRegion` stays core** — it is defined in `iladub.ttl`, not in the fabric file, so it is correctly excluded from the fabric term set.
