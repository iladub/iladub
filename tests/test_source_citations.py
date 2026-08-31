"""The comment cannot cite below itself — R139 disjunct (a)'s instrument.

Spec: `docs/superpowers/specs/2026-08-31-the-comment-cannot-cite-below-itself-design.md`.
The rule is derived in that spec §2 and cited here, never re-derived (plan-rule 6).

**Gate classification (CLAUDE.md §8).** Split, per spec §5. The extraction is PROCEDURAL and
argues its own irreducibility in `tests/source_citations.py`. The REFUSAL is AXIOM in constraint
form — a closed-world SHACL membrane, `vocab/shapes/source-citation-shapes.ttl` — because it
validates what may cross into the tracked tree and never derives. No tuned constant, no reading
judgment, appears on either side.

WHAT THIS DOES NOT CHECK: whether any citation is CORRECT, and anything at all under `docs/**`
(spec §8 — the census measured 71-99% false positives there, and one of R139's three measured
instances was in markdown and is invisible to this test. That is a stated limit, not an oversight).

Run: ./.venv/bin/python -m pytest tests/test_source_citations.py -q
"""

from pathlib import Path

import pyshacl
from rdflib import Graph

from tests.source_citations import REPO, SC, citations, source_files

SHAPES = REPO / "vocab" / "shapes" / "source-citation-shapes.ttl"


def _refusals(graph: Graph) -> list[str]:
    """Every node the membrane refuses, as `file:line -> :NNN`, sorted. Offenders accumulated
    and asserted once by the caller — never a bare assert inside a loop."""
    shapes = Graph().parse(SHAPES, format="turtle")
    conforms, results, _ = pyshacl.validate(
        graph, shacl_graph=shapes, inference="rdfs", advanced=True,
    )
    if conforms:
        return []
    focus = {o for _, _, o in results.triples(
        (None, __import__("rdflib").URIRef("http://www.w3.org/ns/shacl#focusNode"), None))}
    out = []
    for node in focus:
        f = graph.value(node, SC.inFile)
        at = graph.value(node, SC.atLine)
        cites = graph.value(node, SC.citesLine)
        text = graph.value(node, SC.text)
        out.append(f"{f}:{at} -> :{cites}    {text}")
    return sorted(out)


def test_no_tracked_comment_cites_a_line_below_itself():
    """The membrane over the live tree (spec §2). O1."""
    offenders = _refusals(citations(source_files()))
    assert not offenders, (
        "a comment cites a line BELOW itself in its own file; the edit that corrects such a "
        "citation shifts what it cites. Cite the symbol, or the grep that finds it "
        "(CLAUDE.md plan-rule 7):\n  " + "\n  ".join(offenders)
    )


def _one(tmp_path: Path, name: str, body: str) -> Graph:
    """A single-file population, so a fixture case cannot be answered by the real tree."""
    p = tmp_path / name
    p.write_text(body)
    g = citations([p])
    # `citations` reports paths relative to REPO; a tmp file is outside it, so re-root by hand.
    return g


def test_an_upward_citation_is_not_refused(tmp_path):
    """O4: an edit AT the comment cannot move a line above it, so upward is outside the class.

    Pinned on the real tree too: `src/iladub/etkl/document.py:1747-1752` carries six upward
    tokens (`:1395`, `:1421`, `:1561`, `:1573`, `:1605`, `:1743`) and must stay silent — if any
    flags, spec §2's "downward" clause is wrong. That is covered by the whole-tree test above.
    """
    body = "\n".join(["x = 1"] * 40 + ["# see :3 above", "y = 2"])
    assert _refusals(_one(tmp_path, "up.py", body)) == []


def test_a_downward_self_citation_is_refused(tmp_path):
    body = "\n".join(["# the writer is at :40"] + ["x = 1"] * 60)
    assert len(_refusals(_one(tmp_path, "down.py", body))) == 1


def test_a_citation_past_the_files_own_end_is_not_refused(tmp_path):
    """O2 — the EOF filter. A number past this file's length cannot be a line of it, so it is a
    cross-file citation whose anchor the block scope did not carry.

    Live subjects on the real tree: `vocab/queries/arc-position.rq:65` cites `:139-146` and that
    file is 84 lines; `src/iladub/etkl/datagrid.py:733` cites `:949` and that file is 790.
    Both are correct cross-file citations and both are silent only because of this clause.
    """
    body = "\n".join(["# the other file's :400"] + ["x = 1"] * 10)
    assert _refusals(_one(tmp_path, "eof.py", body)) == []


def test_a_bare_citation_inherits_its_blocks_anchor(tmp_path):
    """O3 — referent resolution, spec §6 E2.

    LOAD-BEARING ON THE LIVE TREE, and measured: deleting `paragraph_referent = Path(anchor).name`
    turns the whole-tree oracle above RED with **10** hits, every one an explicit cross-file
    citation — `compile.py:42` (`regions.py:88-98`), `:402` (`feed.py:586`), `:469`/`:476`
    (`datagrid.py:622-623`, `:626`), `document.py:131` (`feed.py:586-587`) and both anchors on
    `tests/arc-m19-false-edge-leak.ttl:13-14`. The fixture arm here is the guard against a
    future tree that happens to carry none of them, not a confession that the tree carries none
    today. (The spec's first draft said the opposite; that claim was made with a regex whose
    anchored branch could never match, and it is corrected in spec §3.)
    """
    anchored = "\n".join(["# per other.py:70 and :80"] + ["x = 1"] * 100)
    assert _refusals(_one(tmp_path, "anchor.py", anchored)) == []

    unanchored = "\n".join(["# per :70 and :80"] + ["x = 1"] * 100)
    assert len(_refusals(_one(tmp_path, "anchor2.py", unanchored))) == 2


def test_the_block_ends_at_a_non_comment_line(tmp_path):
    """E2's reset: a code line ends the block, so the next bare token is self-referent again."""
    body = "\n".join(["# per other.py:70", "x = 1", "# and :80"] + ["y = 1"] * 100)
    refused = _refusals(_one(tmp_path, "reset.py", body))
    assert len(refused) == 1 and "-> :80" in refused[0]


def test_a_slice_and_a_prefixed_name_are_not_citations(tmp_path):
    """The three non-citations that wear the citation shape (spec §6 E3)."""
    body = "\n".join(["# x[:40] and holon:40 and a::40"] + ["x = 1"] * 60)
    assert _refusals(_one(tmp_path, "lex.py", body)) == []


def test_the_population_is_every_tracked_py_ttl_and_rq():
    """Enumerated from `git ls-files`, never from a hard-coded list.

    MEASURED 2026-08-31 at `9198300`: `git ls-files '*.py' '*.ttl' '*.rq' | wc -l` = 462.
    Asserted as an identity against a re-run of the same enumeration rather than as a constant,
    so a new source file joins the population at `git add` without failing this test — the count
    is pinned in `tests/source_citations.py`'s docstring as evidence, not as a gate.
    """
    files = source_files()
    assert files, "the population is empty — `git ls-files` returned nothing"
    assert all(p.suffix in {".py", ".ttl", ".rq"} for p in files)
    assert len(set(files)) == len(files)
