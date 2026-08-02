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
