from iladub.databook import read_databook, write_databook, Block, validate_frontmatter

SAMPLE = """---
id: https://example.org/db/sample
title: Sample
type: databook
version: 1.0.0
created: 2026-06-23
---

Some prose.

<!-- databook:id: asserted -->
<!-- databook:graph: https://example.org/db/sample#g -->
```turtle
@prefix ex: <https://example.org/> .
ex:a ex:b ex:c .
```
"""

def test_read_parses_frontmatter_prose_and_block(tmp_path):
    p = tmp_path / "sample.databook.md"
    p.write_text(SAMPLE, encoding="utf-8")
    db = read_databook(str(p))
    assert db.frontmatter["id"] == "https://example.org/db/sample"
    assert db.frontmatter["type"] == "databook"
    assert "Some prose." in db.prose
    assert len(db.blocks) == 1
    b = db.blocks[0]
    assert b.lang == "turtle"
    assert b.id == "asserted"
    assert b.graph_iri == "https://example.org/db/sample#g"
    assert "ex:a ex:b ex:c ." in b.content

def test_write_then_read_roundtrip(tmp_path):
    fm = {"id": "https://example.org/db/x", "title": "X", "type": "databook",
          "version": "1.0.0", "created": "2026-06-23"}
    blocks = [Block(lang="turtle", id="asserted", graph_iri="https://example.org/db/x#g",
                    content="@prefix ex: <https://example.org/> .\nex:a ex:b ex:c .")]
    p = tmp_path / "x.databook.md"
    write_databook(fm, blocks, "Hello prose.", str(p))
    db = read_databook(str(p))
    assert db.frontmatter["id"] == "https://example.org/db/x"
    assert db.prose == "Hello prose."
    assert len(db.blocks) == 1
    assert db.blocks[0].id == "asserted"
    assert db.blocks[0].graph_iri == "https://example.org/db/x#g"
    assert "ex:a ex:b ex:c ." in db.blocks[0].content
    assert db.blocks[0].lang == "turtle"

def test_graph_selector_extracts_block(tmp_path):
    fm = {"id": "https://example.org/db/y", "title": "Y", "type": "databook",
          "version": "1.0.0", "created": "2026-06-23"}
    blocks = [Block(lang="turtle", id="asserted",
                    content="@prefix ex: <https://example.org/> .\nex:s ex:p ex:o .")]
    p = tmp_path / "y.databook.md"
    write_databook(fm, blocks, "", str(p))
    g = read_databook(str(p)).graph("asserted")
    assert len(g) == 1

def test_validate_frontmatter_required_keys():
    assert validate_frontmatter({"id": "x", "title": "t", "type": "databook",
                                 "version": "1.0.0", "created": "2026-06-23"}) == []
    errs = validate_frontmatter({"id": "x"})
    assert any("title" in e for e in errs)

def test_validate_frontmatter_requires_process_stamp():
    fm = {"id": "x", "title": "t", "type": "databook", "version": "1.0.0",
          "created": "2026-06-23"}
    errs = validate_frontmatter(fm, require_process=True)
    assert any("process" in e for e in errs)
    fm["process"] = {"transformer": "BAML", "transformer_type": "llm",
                     "inputs": [], "timestamp": "2026-06-23T00:00:00Z"}
    assert validate_frontmatter(fm, require_process=True) == []
