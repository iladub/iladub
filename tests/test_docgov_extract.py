"""Unit tests for the docgov PROCEDURAL extractor (pure functions, no git)."""
import subprocess
from datetime import date
from pathlib import Path

import pytest
from rdflib import Graph, Literal, RDF
from rdflib.namespace import XSD

from tests.docgov_extract import (
    classify, is_exempt, load_mkdocs, nav_paths, exclude_prefixes, is_excluded,
    DG, parse_frontmatter, doc_iri, extract, tracked_markdown,
)

NAV = {"docs/index.md", "docs/manifesto.md", "docs/narrative/scope-evolution.md"}
REPO = Path(__file__).resolve().parent.parent


def test_exemptions():
    assert is_exempt(".claude/skills/baml-core/SKILL.md")
    assert is_exempt(".agents/skills/baml-core/SKILL.md")
    assert is_exempt("examples/transplant/offer.databook.md")
    assert not is_exempt("docs/manifesto.md")


def test_classify_precedence_most_specific_wins():
    assert classify("CLAUDE.md", NAV) == "contract"
    assert classify("README.md", NAV) == "manual"
    assert classify("vocab/README.md", NAV) == "manual"
    assert classify("demo/README-etkl-showcase.md", NAV) == "manual"
    assert classify("RELEASE.md", NAV) == "manual"
    assert classify("internal/decisions/x.md", NAV) == "confidential"
    assert classify("docs/wiki/concepts/foo.md", NAV) == "wiki"
    # docs/loops/README.md: Evidence dir beats any README intuition (spec §3 precedence)
    assert classify("docs/loops/README.md", NAV) == "evidence"
    assert classify("docs/superpowers/specs/2026-07-30-row-groups-design.md", NAV) == "evidence"
    assert classify("docs/w3id/iladub-htaccess.md", NAV) == "evidence"
    assert classify("docs/manifesto.md", NAV) == "assertion"
    assert classify("docs/narrative/scope-evolution.md", NAV) == "assertion"


def test_classify_unknown_is_none_not_a_guess():
    assert classify("docs/neurosymbolic-exemplars.md", NAV) is None
    assert classify("somewhere/else.md", NAV) is None


def test_load_mkdocs_tolerates_python_name_tags(tmp_path):
    # mkdocs.yml contains `!!python/name:pymdownx...` — yaml.safe_load would raise.
    y = tmp_path / "mkdocs.yml"
    y.write_text(
        "site_name: x\n"
        "exclude_docs: |\n  superpowers/\n  wiki/\n"
        "nav:\n  - Home: index.md\n  - Sub:\n      - A: narrative/scope-evolution.md\n"
        "markdown_extensions:\n  - pymdownx.superfences:\n      custom_fences:\n"
        "        - name: mermaid\n          class: mermaid\n"
        "          format: !!python/name:pymdownx.superfences.fence_code_format\n"
    )
    cfg = load_mkdocs(y)
    assert nav_paths(cfg) == {"docs/index.md", "docs/narrative/scope-evolution.md"}
    prefixes = exclude_prefixes(cfg)
    assert prefixes == ("docs/superpowers/", "docs/wiki/")
    assert is_excluded("docs/wiki/concepts/foo.md", prefixes)
    assert not is_excluded("docs/index.md", prefixes)


def test_parse_frontmatter():
    fm = parse_frontmatter(
        "---\ntitle: X\ntype: concept\nconfidence: high\nupdated: 2026-07-30\n"
        "sources:\n  - docs/superpowers/specs/a.md\n  - vault:wiki/concepts/h.md\n---\nbody\n"
    )
    assert fm["title"] == "X"
    assert fm["updated"] == date(2026, 7, 30)
    assert fm["sources"][1] == "vault:wiki/concepts/h.md"
    assert parse_frontmatter("no frontmatter\n") is None


def test_extract_raises_on_shallow_clone(tmp_path):
    """A shallow clone silently makes `git log -1 -- <path>` return HEAD's
    date for every path — wrong lastCommitDate, false staleness verdicts.
    extract() must fail loudly instead of guessing (F2, final review)."""
    repo = Path(__file__).resolve().parent.parent
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "--depth", "1", f"file://{repo}", str(shallow)],
        capture_output=True, text=True, check=True,
    )
    with pytest.raises(RuntimeError, match="shallow clone"):
        extract(shallow)


def test_extract_live_repo_smoke():
    """extract() runs on the real repo: every non-exempt tracked md becomes a
    dg:Document with a path; nav entries all resolve. (Full conformance is
    tests/test_doc_governance.py — this is the plumbing smoke test.)"""
    REPO = Path(__file__).resolve().parent.parent
    g = extract(REPO)
    docs = set(g.subjects(RDF.type, DG.Document))
    tracked = [p for p in tracked_markdown(REPO)]
    assert doc_iri("CLAUDE.md") in docs
    assert doc_iri("docs/manifesto.md") in docs
    assert doc_iri(".claude/skills/baml-core/SKILL.md") not in docs  # exempt
    assert len(docs) <= len(tracked)
    assert (doc_iri("CLAUDE.md"), DG.docClass, Literal("contract")) in g
    for entry in g.subjects(RDF.type, DG.NavEntry):
        assert (entry, DG.resolves, Literal(True)) in g


def test_dated_spec_emits_docdate_and_impact():
    g = extract(REPO)
    spec = doc_iri("docs/superpowers/specs/2026-07-31-documentation-governance-design.md")
    assert (spec, DG.docDate,
            Literal(date(2026, 7, 31), datatype=XSD.date)) in g
    assert (spec, DG.docImpact, Literal("increment")) in g
    # undated evidence (e.g. residues.md) carries neither fact
    residues = doc_iri("docs/superpowers/residues.md")
    assert list(g.objects(residues, DG.docDate)) == []


def test_impact_value_is_first_valid_token_only():
    from tests.docgov_extract import _IMPACT
    assert _IMPACT.search("**Doc impact:** increment — adds X").group(1) == "increment"
    assert _IMPACT.search("Doc impact: contradiction\n").group(1) == "contradiction"
    assert _IMPACT.search("Doc impact: TBD") is None
    assert _IMPACT.search("no block at all") is None


def test_wiki_pages_carry_index_membership():
    g = extract(REPO)
    exemplars = doc_iri("docs/wiki/concepts/neurosymbolic-exemplars.md")
    assert (exemplars, DG.inWikiIndex, Literal(True)) in g
    # the index itself carries no membership fact
    index = doc_iri("docs/wiki/index.md")
    assert list(g.objects(index, DG.inWikiIndex)) == []


# ------------------------------------------------------- figure occurrences
# The PROCEDURAL half of the figure gate (spec 2026-09-08 §2, D3): exact decimal
# arithmetic over a lexical form. Every assertion below is two-sided — what the
# rule accepts AND what it refuses — because a matcher that only ever matches is
# indistinguishable from one that matches everything.

from decimal import Decimal  # noqa: E402

from tests.docgov_extract import (  # noqa: E402
    blocks, denotes, is_dated, separating_precision, load_readings,
)

STEM = Decimal("0.9654553611484971")
READINGS = {"stem": STEM, "apple": Decimal("0.06068601583113457")}


def test_precision_is_exact_not_approximate():
    """O5: `0.9655` IS a quotation of the stem's reading; `0.9659` is not — and
    `0.9659` is the value that superseded it, so this is the discrimination the
    whole gate rests on."""
    assert denotes("0.9655", READINGS, 4) == "stem"
    assert denotes("0.9654553611484971", READINGS, 4) == "stem"
    assert denotes("0.9659", READINGS, 4) is None
    assert denotes("0.96545536114849", READINGS, 4) is None


def test_a_form_too_coarse_to_identify_the_register_is_not_a_finding():
    """`0.1` rounds from apple's 0.0607 and is unique in this register — and is
    still refused, because at one decimal the register cannot identify its own
    rows. Measured false positives this kills: two, both the phrase 'quarantines
    exactly like a 0.1-scored one'."""
    assert denotes("0.1", READINGS, 1) == "apple"
    assert denotes("0.1", READINGS, 4) is None


def test_an_ambiguous_form_is_not_a_finding():
    two = {"a": Decimal("0.90001"), "b": Decimal("0.90002")}
    assert denotes("0.9000", two, 4) is None


def test_separating_precision_is_derived_from_the_register():
    assert separating_precision([Decimal("0.51"), Decimal("0.52")]) == 2
    assert separating_precision([Decimal("0.90001"), Decimal("0.90002")]) == 5
    assert separating_precision([Decimal("1.0")]) == 0


def test_the_shipped_registers_separating_precision_is_four():
    """O5b, asserted BY VALUE: `sep` is data-derived, so it moves. Two future
    readings of one document differing only at 17dp would push it to 17 and
    silence the gate — the under-firing shape [[R188]] exists for. This is the
    only place that movement is visible before it hides a defect."""
    _, values, _ = load_readings(REPO)
    assert separating_precision(list(values.values())) == 4


def test_a_block_is_dated_by_any_of_its_lines():
    """O4: the block, not the line, is the closure boundary."""
    dated = "Measured 2026-08-04 on CBH:\nscore 0.0698 -> 0.9047, four bands.\n"
    assert [b[0] for b in blocks(dated)] == [1]
    assert is_dated(dated)
    moved = "Measured 2026-08-04 on CBH:\n\nscore 0.0698 -> 0.9047, four bands.\n"
    assert [b[0] for b in blocks(moved)] == [1, 3]
    assert not is_dated("\n".join(blocks(moved)[1][1]))


def test_a_commit_sha_dates_a_block_but_a_hex_word_does_not():
    assert is_dated("stem reads 0.9655 at `20cc5b8`")
    assert not is_dated("the decade `add` `defaced` reads 0.9655")


def _lexicals(text: str) -> list[str]:
    """The lexical forms `_figure_facts` emits for `text`, in line order."""
    from tests.docgov_extract import _figure_facts

    g = Graph()
    _figure_facts(g, doc_iri("p.md"), "p.md", text, READINGS, 4)
    # Sort by (line, column): the occurrence IRI ends `#figure-<line>-<column>`,
    # and two figures on one line must come back in the order they were written.
    def where(occ):
        line, column = str(occ).rsplit("-", 2)[-2:]
        return int(line), int(column)

    return [str(g.value(occ, DG.lexical))
            for occ in sorted(g.subjects(RDF.type, DG.FigureOccurrence), key=where)]


def test_a_figure_at_the_end_of_a_sentence_is_still_a_figure():
    """MEASURED 2026-09-09 at `4991dd1`: every one of the three sites [[R189]]
    names is invisible to this module, and NOT for the reason R189 gives. Each
    writes the reading at the end of a sentence, and the lexical rule refused any
    decimal followed by a dot. Its stated intent is to refuse a LONGER DOTTED
    TOKEN — a full stop is not one, so this was over-refusal against the rule's
    own comment, not a design choice. Census: widening it makes exactly those
    three visible across all 497 tracked .py/.ttl/.rq files, and adds ZERO
    occurrences to docs/wiki/**, the class the hard gate guards."""
    assert _lexicals("the stem compiles at 0.9654553611484971.\n") == [
        "0.9654553611484971"]
    assert _lexicals("stem 0.9655. apple 0.0607.\n") == ["0.9655", "0.0607"]
    # A truncation ellipsis is a quotation of the reading, not a dotted token.
    assert _lexicals("stem 0.9655... in the table\n") == ["0.9655"]


def test_a_longer_dotted_token_is_still_refused():
    """The widening keeps every refusal the rule was written for: a version, an
    IP, a dotted range. FALSIFIES the fix by the only route that matters — a
    tokeniser that matches a sentence-final figure by matching everything would
    pass the test above and fail this one."""
    assert _lexicals("released 0.9655.9659 as one token\n") == []
    assert _lexicals("v1.0.9655 and 10.0.9655.1 and 0.9655.0\n") == []
    assert _lexicals("the range 0.9655.0607 is not two figures\n") == []
