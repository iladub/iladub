"""The extractor's own oracles — O3, I2, I3 and the population pin (spec §4.3, §7).

These test `tests/query_terms.py`, the PROCEDURAL extraction step. They do NOT test the
declaration membrane; that is `tests/test_query_declarations.py` (AXIOM, constraint form).
"""
from pathlib import Path

from tests.query_terms import (
    ETKL,
    QUERY_DIR,
    extract_named_terms,
    named_terms_by_text,
    query_files,
    query_iri,
)

NESTED_FIXTURE = Path(__file__).resolve().parent / "query-nested-bind-exists.rq"


def test_a_term_nested_in_bind_exists_is_reported():
    """O3 — the only oracle that can pin I1 (spec §7).

    MEASURED 2026-08-28 (plan §0.1 F2): a walk that handles dicts and returns loses
    iladub:PromotionDecision and iladub:reviews from membrane-health.rq, and 5 tab: terms
    from 5 other files — 164 distinct instead of 171, 6 files disagreeing with method B.
    """
    g = extract_named_terms(NESTED_FIXTURE)
    named = {str(o) for o in g.objects(query_iri(NESTED_FIXTURE), ETKL.namesTerm)}
    assert "https://w3id.org/iladub#PromotionDecision" in named, named
    assert "https://w3id.org/iladub#reviews" in named, named


def test_both_extractors_agree_on_every_authored_query():
    """I2 — SHIPPED, not scaffolding (spec §2.4, §3). The parser proposes; the text scan
    disposes; disagreement in EITHER direction is a failure."""
    disagreements = {}
    for path in query_files():
        by_algebra = {str(o) for o in extract_named_terms(path).objects(None, ETKL.namesTerm)}
        by_text = named_terms_by_text(path)
        if by_algebra != by_text:
            disagreements[path.name] = sorted(by_algebra ^ by_text)
    assert not disagreements, disagreements


def test_every_authored_query_parses():
    """I3 — a parse failure is LOUD, never a skipped file. A skipped file is a silently
    narrowed population, which is I1's defect wearing a different hat (spec §5, V5)."""
    for path in query_files():
        extract_named_terms(path)          # raises, and the raise names the file


def test_the_population_is_every_file_in_vocab_queries():
    """The population is enumerated from the directory, never typed (G3). 50 today; this
    asserts the identity with the glob first, and the count second as the pin against the
    glob itself collapsing. RE-MEASURED 2026-08-29: 46 -> 48, the two queries this loop's D1 and
    D2 derivations add (`vocabulary-role.rq`, `alignment-subject.rq`).

    RE-MEASURED 2026-09-02 (spec §10 seam 6: compute the count, never copy it): 48 -> 49,
    `matrix-body-start.rq` the 2026-09-02 the-body-starts-at-the-stub loop adds (spec
    `2026-09-02-the-body-starts-at-the-stub-design.md` § 3.1).

    RE-MEASURED 2026-09-04: 49 -> 50, `band-run.rq` the R165 the-run-is-one-band loop
    adds — the adjacent-subsumption derivation that proposes a contiguous run of ruled
    bands as one band (spec `2026-09-04-the-run-is-one-band-design.md` § 3.4)."""
    assert query_files() == sorted(QUERY_DIR.glob("*.rq"))
    assert len(query_files()) == 50, len(query_files())
