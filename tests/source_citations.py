"""Source-comment citation extractor — PROCEDURAL (CLAUDE.md §8 gate; R139 disjunct (a); spec
`docs/superpowers/specs/2026-08-31-the-comment-cannot-cite-below-itself-design.md` §5, §6).

**Gate classification (CLAUDE.md §8): PROCEDURAL, and here is why it is irreducible.** This module
reads tracked `.py`/`.ttl`/`.rq` source text and turns each `:NNN` token on a comment line into an
RDF fact carrying where it sits, what it points at, and which file it resolves against. It is
IRREDUCIBLE TO AXIOM for the reason M7 states in `tests/test_arc_manifest.py`: there is no evidence
graph to derive over until it has run — it is the step that MAKES one, and a `CONSTRUCT` cannot
tokenise a file it cannot yet see. It is IRREDUCIBLE TO NEURAL because nothing here is perceptual or
underdetermined: a line either begins with `#` or does not, and a token either matches the citation
lexicon or does not. No threshold, no tolerance, no tuned constant, no reading judgment.

**IT DECIDES NOTHING, deliberately** (spec §6, invariant E1). It never filters and never compares a
cited line to a citing line. Selection is the membrane's job
(`vocab/shapes/source-citation-shapes.ttl`); an extractor that pre-filtered could not be falsified
independently of the constraint it feeds.

WHAT THIS DOES NOT CHECK: whether a citation is CORRECT. Three of the four sites this instrument was
built against were correct at the moment it was written — the class it names is a HAZARD (an edit at
the comment invalidates the number), not a wrong number. Nor does it read `.md`: the R139 census
measured 71–99% false positives over `docs/**`, where a citation is a narrative whose referent
crosses heading boundaries. See the spec §8.

MEASURED 2026-08-31 at `9198300`, over `git ls-files '*.py' '*.ttl' '*.rq'` = 462 files: 76 tokens on
comment lines, of which 10 point downward and 7 also fall within their own file's length.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterable

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

REPO = Path(__file__).resolve().parent.parent

#: Repo-internal membrane vocabulary. NOT part of the published iladub/etkl/dec/risk ontologies and
#: NOT registered at w3id — the same standing, and the same disclaimer, as `dg:`
#: (`vocab/shapes/doc-governance-shapes.ttl:8-9`, `grep -rln docgov vocab/ontology/` → nothing).
SC = Namespace("https://w3id.org/iladub/srccite#")

#: Minted subjects for the evidence graph. Not an owned namespace, so a citation node can never
#: collide with a term under test.
_CITATION_IRI_BASE = "urn:iladub:srccite:"

#: The extensions whose comments are read. `.md` is deliberately absent (see the docstring).
EXTENSIONS = ("*.py", "*.ttl", "*.rq")

#: The citation lexicon. Two branches, tried in this order at every position:
#:   ANCHORED — `basename.ext:NNN`, optionally `-MMM`. Names its own referent.
#:   BARE     — `:NNN`, optionally `-MMM`. Inherits the referent of its comment block.
#: The bare branch's lookbehind excludes the three non-citations that wear the same shape: a Python
#: slice (`x[:12]`), a prefixed name (`holon:03`), and a second colon (`a::12`). A format spec
#: (`{c:>16}`) cannot match because a digit must follow the colon directly.
_ANCHOR_EXT = "py|ttl|rq|md|toml|yml|yaml|json|cfg"
_TOKEN = re.compile(
    rf"(?P<anchor>[\w.\-/]+\.(?:{_ANCHOR_EXT})):(?P<aline>\d{{2,5}})(?:-(?P<aend>\d{{2,5}}))?\b"
    rf"|(?<![\w\[>:]):(?P<line>\d{{2,5}})(?:-(?P<end>\d{{2,5}}))?\b"
)


def source_files() -> list[Path]:
    """The population: every tracked `.py`, `.ttl` and `.rq`, sorted.

    Enumerated from `git ls-files`, never from a hard-coded list. `-z` because a tracked path is
    allowed to contain a space; the form is `tests/artifact_terms.py:62-67`, copied rather than
    re-invented — there is no shared enumerator for these extensions (`artifact_files()` is
    `.ttl`-only, `tracked_markdown()` is `.md`-only, `query_files()` is a `vocab/queries` glob).
    """
    out = subprocess.run(
        ["git", "ls-files", "-z", *EXTENSIONS],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout
    return sorted(REPO / p for p in out.split("\0") if p)


def _is_comment(line: str) -> bool:
    """A comment line: first non-whitespace character is `#`. True of all three extensions.

    WHY the restriction (spec §2): in CODE a `:NNN` is a slice, a format spec or a dict value —
    `{"weight": 200}` is not a pointer to line 200.
    """
    return line.lstrip().startswith("#")


def _ends_paragraph(line: str) -> bool:
    """A referent scope ends at a non-comment line OR at a CONTENTLESS comment line (`#`).

    MEASURED 2026-08-31, and this is why the scope is the paragraph and not the block: the
    longest contiguous `#` block in the tree is **122 lines** (`tests/arc-manifest.ttl:644`), and
    a block-scoped referent leaked across one in the first implementation of this module —
    `compile.py:402` anchors `feed.py:586`, and `:1083` eight lines and one blank comment line
    later inherited `feed.py`, hiding a real instance. A paragraph is the unit a reader resolves
    a bare `:NNN` against; a 122-line block is not.
    """
    return not _is_comment(line) or line.lstrip().lstrip("#").strip() == ""


def citations(paths: Iterable[Path]) -> Graph:
    """Every `:NNN` token on a comment line of `paths`, as one node each. Never filters (E1).

    Referent resolution (E2): a token is resolved against THIS file unless an explicit
    `basename.ext:MMM` anchor appeared earlier in the same comment PARAGRAPH, in which case later
    bare tokens in that paragraph inherit it. A code line, or a contentless `#` line, ends the
    paragraph and resets the referent — see `_ends_paragraph` for the measurement that forced the
    unit to be the paragraph and not the contiguous block. This is how a human reads the passage:
    `datagrid.py:733` writes ``compile.py:878`` and then a bare ``:949``, and the second means
    compile.py, not datagrid.py.

    A range `:NNN-MMM` emits BOTH endpoints as separate nodes: an edit can invalidate either end.
    """
    g = Graph()
    g.bind("sc", SC)
    n = 0
    for path in paths:
        # Repo-relative inside the repo, so no absolute local path reaches a failure message;
        # bare name outside it, which is the case an oracle's fixture file takes.
        rel = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.name
        self_name = path.name
        text = path.read_text(errors="replace")
        lines = text.splitlines()
        length = len(lines)
        paragraph_referent: str | None = None
        in_paragraph = False
        for lineno, line in enumerate(lines, 1):
            if _ends_paragraph(line):
                in_paragraph = False
                if not _is_comment(line):
                    continue
            if not in_paragraph:
                paragraph_referent = None
            in_paragraph = True
            for m in _TOKEN.finditer(line):
                anchor = m.group("anchor")
                if anchor:
                    paragraph_referent = Path(anchor).name
                    cited = [m.group("aline"), m.group("aend")]
                else:
                    cited = [m.group("line"), m.group("end")]
                referent = paragraph_referent or self_name
                for raw in cited:
                    if raw is None:
                        continue
                    n += 1
                    node = URIRef(f"{_CITATION_IRI_BASE}{n}")
                    g.add((node, RDF.type, SC.Citation))
                    g.add((node, SC.inFile, Literal(rel)))
                    g.add((node, SC.atLine, Literal(lineno, datatype=XSD.integer)))
                    g.add((node, SC.citesLine, Literal(int(raw), datatype=XSD.integer)))
                    g.add((node, SC.referent, Literal(referent)))
                    g.add((node, SC.selfName, Literal(self_name)))
                    g.add((node, SC.fileLength, Literal(length, datatype=XSD.integer)))
                    g.add((node, SC.text, Literal(line.strip())))
    return g
