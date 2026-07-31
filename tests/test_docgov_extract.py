"""Unit tests for the docgov PROCEDURAL extractor (pure functions, no git)."""
from pathlib import Path

from tests.docgov_extract import (
    classify, is_exempt, load_mkdocs, nav_paths, exclude_prefixes, is_excluded,
)

NAV = {"docs/index.md", "docs/manifesto.md", "docs/narrative/scope-evolution.md"}


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
