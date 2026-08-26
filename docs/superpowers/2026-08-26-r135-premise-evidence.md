# R135/R117 premise evidence — measured 2026-08-26, `main` @ 0d82736

## M1 — The ablation REPRODUCES (R135 arm 1)

Throwaway worktree at `0d82736`, detached. **PYTHONPATH pinned to the worktree's `src/`**, because
the editable install otherwise resolves to the main tree (the R114/R121 seam):

    $ cd <worktree> && python3 -c "import iladub.etkl.compile as c; print(c._repo_vocab())"
    /Volumes/WD Green/dev/git/iladub/vocab            <-- MAIN TREE, wrong
    $ PYTHONPATH="$PWD/src" python3 -c "... same ..."
    <worktree>/vocab                                   <-- correct

Baseline, file present (8858 bytes):

    $ PYTHONPATH="$PWD/src" .venv/bin/pytest \
        tests/etkl/test_membrane_health.py::test_compiled_document_reports_membrane_health -q
    1 passed in 1.70s

Ablated (`rm vocab/ontology/etkl-holons.ttl`):

    1 passed in 1.40s        <-- holon:05's declared oracle, GREEN with holon:01's artifact gone

And holon:02's two oracles, same ablated tree (R117's half):

    $ PYTHONPATH="$PWD/src" .venv/bin/pytest \
        tests/test_hga_alignment.py::test_alignment_axioms_present \
        tests/test_source_ownership.py::test_alignment_modules_only_point_outward -q
    2 passed in 0.13s

## M2 — Structural half

    $ grep -rn "etkl-holons" src/ --include='*.py'
    (no matches)

`compile.py:441-453` `_build_membrane` loads `tab.ttl`, `dec.ttl`, `iladub.ttl` only.
`_TAB_SHAPE_FILES` / `_DEC_SHAPE_FILES` (`compile.py:398,421`) name shapes, not `etkl-holons.ttl`.
`_repo_vocab` (`compile.py:374-382`) walks up from `__file__`.

`vocab/queries/membrane-health.rq` names `etkl:CompiledDocumentHolon`, `etkl:membraneHealth`,
`etkl:MembraneValidation`, `etkl:Intact`, `etkl:Weakened`, `etkl:Compromised` as bare IRIs.
`tests/etkl/test_membrane_health.py` asserts against rdflib `Namespace` constants — no ontology
is loaded anywhere on the path.

## M3 — RUNNER TRAP (costs 4 minutes and a false red)

    $ python3   -m pytest tests/etkl/test_membrane_health.py -q   ->  5 failed, 12 passed, 2 errors
    $ .venv/bin/pytest    tests/etkl/test_membrane_health.py -q   ->  19 passed in 252.96s

System `python3` is NOT the runner. `main` is green for this module.
(The module takes 4m12s; the declared oracle test alone takes 1.7s.)

## M4 — The `.rq` census: ONE live undeclared term, and it is load-bearing

46 `.rq` files; 10 name owned-namespace terms; 33 distinct owned IRIs named.
32 are declared. **One is not:**

    https://w3id.org/iladub/risk#order  <- named by vocab/queries/escalation-furnish.rq

Verified independently, merged graph over all 13 `vocab/ontology/*.ttl`:

    as subject: []
    as predicate, count: 4
    dec:order as subject: [rdf:type, rdfs:label, rdfs:domain, rdfs:range, rdfs:comment]

`risk.ttl:62,64,66,68` use `risk:order` as a predicate on the four severities; nothing declares it.
Its exact analogue `dec:order` IS fully declared. `escalation-furnish.rq` leans on it in the
CONSTRUCT template (`:73-74`) and the WHERE (`:91,93`) driving `FILTER(?so > ?co)`.

**This is a real negative fixture, not a synthetic one.**

## M5 — R117 has NO live instance today

All four `*-hga-align.ttl` files enumerated with rdflib. Every term subject (19) IS declared in the
owned tree. The only undeclared subjects are the three modules' own `owl:Ontology` metadata IRIs
(`.../hga-alignment`), which are not dangling terms.

`tests/test_hga_alignment.py:39` — `test_alignment_axioms_present` parses `iladub-hga-align.ttl`
ALONE; `ONTS` (`:33`) is not loaded into that graph.
`tests/test_source_ownership.py:77` — `test_alignment_modules_only_point_outward` is a prefix check
on subject strings; it never cross-references the owned tree.
9 tests in the two modules; `9 passed in 0.59s`.

So R117 is a hole with no current leak. R135 is a hole WITH one (`risk:order`).

## M6 — A LARGER instance of the same class, found in passing: `prog:`

`prog:` = `https://w3id.org/iladub/progress#` is an OWNED namespace with **no ontology file at all**:

    $ grep -ln "progress#" vocab/ontology/*.ttl
    (none)
    $ git grep -ln "w3id.org/iladub/progress" -- vocab/
    vocab/queries/arc-{depends,frontier,orphan,position,reach,ready,unblocked}.rq

Seven queries plus `tests/arc-manifest.ttl` use it. Every `prog:` term is undeclared.
**This is the instrument's scope question**: a check applied to `prog:` fails on day one, everywhere.

## Still unverified

- The FULL suite has not been run on `main` at `0d82736` (only `test_membrane_health.py`, 19 passed,
  and the two hga modules, 9 passed).
- R115's "72 of 87 open rows block no criterion" not re-measured at 104 rows.

## M7 — Two independent extractors AGREE on all 46 queries (added 2026-08-26)

Method A: rdflib `parseQuery` → `translateQuery` → exhaustive traversal of the algebra
(dict / sequence / `__dict__`, cycle-guarded), collecting every `URIRef`.
Method B: an independent text scan — PREFIX map, PREFIX lines removed from the body, `#`
comments stripped, prefixed names expanded, plus longhand `<https://w3id.org/iladub…>`.

    46 files; disagreements: 0; distinct owned IRIs found by parser: 171

**A NAIVE algebra walk is NOT sufficient and this was measured, not assumed.** Walking only
`CompValue.items()` finds 7 of `membrane-health.rq`'s 9 owned terms — it misses
`iladub:PromotionDecision` and `iladub:reviews`, both nested inside
`BIND(EXISTS { … FILTER NOT EXISTS { … } })`. An incomplete extractor is a silently vacuous
instrument. The cross-check against method B is what caught it.

## M8 — The real population, by namespace (the day-one failure count)

Declaring set = subjects of the **non-align** `vocab/ontology/*.ttl` files.

| ns | named by queries | declared | UNDECLARED |
|---|---|---|---|
| `tab:` | 116 | 116 | **0** |
| `dec:` | 14 | 14 | **0** |
| `etkl:` | 12 | 12 | **0** |
| `iladub:` | 6 | 6 | **0** |
| `risk:` | 2 | 1 | **1** — `risk:order` |
| `prog:` | 9 | 0 | **9** — namespace has no ontology file |
| `docgov:` | 12 | 0 | **12** — namespace has no ontology file |
| **total** | **171** | **149** | **22** |

`risk:order` is NOT rescued by any align file (checked against the align subjects separately).

**Two findings that were not available when the scope question was asked:**
1. `tab:` (116 terms) is entirely clean — including it costs nothing and quadruples coverage.
2. `docgov:` = `https://w3id.org/iladub/docgov#` is a SECOND owned namespace with no ontology
   file, 12 terms, used by the `docgov-*.rq` queries. `prog:` was not the only one.
