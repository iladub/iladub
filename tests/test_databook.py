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
