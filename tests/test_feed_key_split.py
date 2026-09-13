"""The key split — one row becomes one record per spanning childless header (R211, Layer B).

Spec: docs/superpowers/specs/2026-09-11-the-span-the-author-drew-design.md § 3.2
Plan: docs/superpowers/plans/2026-09-13-the-span-the-author-drew.md, Tasks 4 and 5

THE CONDITION, read off the compiled graph: a header node with NO parent, covering MORE THAN ONE
leaf column, and being the `tab:parentHeader` of NO node. "Level 0" means no parent rather than a
syntactic level, because `holon.assert_hier_region` promotes every parentless node to level 0.
The coverage predicate is `tab:coversColumn`; `tab:covers` is a decoy (domain tab:HeaderCell,
transient evidence, never asserted into a holon).

MEASURED, corpus-wide, POST-Layer-A: the condition fires on ONE document — graincorp-capacity p0
— and on exactly 7 of its 9 header nodes, the seven ports. `Year` and `Elevation Period` cover one
column each and are excluded by *covers more than one*; apple's 2 and who's 6 multi-column nodes
are excluded by *childless*. Before Layer A it fired on nothing at all (evidence § 8), which is
why this file's synthetic arms carry the general claim and the corpus arm carries the document.

WHY THE SEPARATOR DOES NOT MATTER FOR IDENTITY, measured before one was chosen (plan rule 3):
`_record_uri` replaces every run of non-[A-Za-z0-9._-] with '_', so ' > ', ' | ' and ' :: ' all
slug to the SAME subject, `urn:iladub:record:p0_htable3-r0_Mackay`. The choice is therefore about
the READABLE row_id only. ' > ' is kept, because it is what every other segment of a row id
already uses and a fourth spelling would imply a distinction that does not survive slugging —
the cost, named rather than hidden, is that a split segment is lexically indistinguishable from
the multiplicity and residual discriminators, which also join with ' > '.
"""
import os

import pytest
from rdflib import Graph

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

CORPUS = os.path.join(os.path.dirname(__file__), "..", "corpus")
GRAINCORP = os.path.join(CORPUS, "ag-trade", "graincorp-capacity-2026-08-04.pdf")
corpus_only = pytest.mark.skipif(not os.path.exists(GRAINCORP), reason="corpus not fetched")

_PREFIX = """
@prefix tab:  <https://w3id.org/iladub/tab#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix ex:   <https://example.org/split#> .
"""


def _table(nodes, ncols=6, nrows=2):
    """A hierarchical table over `ncols` leaf columns and `nrows` body rows.

    `nodes` is (name, covered column indices, parent-or-None) per header node. Entry cells carry
    text 'v{row}{col}' so a split can be checked cell by cell.
    """
    ttl = [_PREFIX, "ex:tbl a tab:HierarchicalTable ;"]
    ttl.append("    tab:hasLeafColumn " + ", ".join(f"ex:c{i}" for i in range(ncols)) + " ;")
    ttl.append("    tab:hasLeafRow " + ", ".join(f"ex:r{r}" for r in range(nrows)) + " ;")
    ttl.append("    tab:hasHeaderNode " + ", ".join(f"ex:{n}" for n, _, _ in nodes) + " ;")
    cells = [f"ex:e{r}_{c}" for r in range(nrows) for c in range(ncols)]
    ttl.append("    tab:hasCell " + ", ".join(cells)
               + ", " + ", ".join(f"ex:l{n}" for n, _, _ in nodes) + " .")
    for i in range(ncols):
        ttl.append(f"ex:c{i} a tab:LeafColumn .")
    for r in range(nrows):
        ttl.append(f"ex:r{r} a tab:LeafRow .")
    for name, cols, parent in nodes:
        ttl.append(f"ex:{name} a tab:HeaderNode ; tab:headerLevel {0 if parent is None else 1} ; "
                   + "".join(f"tab:coversColumn ex:c{c} ; " for c in cols)
                   + (f"tab:parentHeader ex:{parent} ; " if parent else "")
                   + f"tab:hasLabel ex:l{name} .")
        ttl.append(f'ex:l{name} a tab:LabelCell ; tab:cellText "{name}" .')
    for r in range(nrows):
        for c in range(ncols):
            ttl.append(f'ex:e{r}_{c} a tab:EntryCell ; tab:atRow ex:r{r} ; tab:atColumn ex:c{c} ; '
                       f'tab:cellText "v{r}{c}" ; tab:onPage 0 ; '
                       f'prov:wasDerivedFrom <https://example.org/doc#p0-{c}-{r}> .')
    return Graph().parse(data="\n".join(ttl), format="turtle")


# --- the split ---------------------------------------------------------------------------

def test_one_row_becomes_one_record_per_spanning_childless_header():
    """Three childless spanning nodes over six columns, two rows -> six records, not two."""
    from iladub.feed import table_records

    g = _table([("Mackay", (0, 1), None), ("Gladstone", (2, 3), None),
                ("Portland", (4, 5), None)])
    recs = table_records(g)
    assert len(recs) == 6, [r.row_id for r in recs]
    assert len({r.row_id for r in recs}) == 6, [r.row_id for r in recs]
    for name in ("Mackay", "Gladstone", "Portland"):
        assert sum(1 for r in recs if r.row_id.endswith(name)) == 2, name


def test_a_split_record_carries_its_own_columns_and_the_shared_ones():
    """§ 3.2: each record carries the cells of every column NO spanning node covers, copied in,
    plus its own node's leaf cells — and nothing from a sibling node's columns."""
    from iladub.feed import table_records

    g = _table([("Year", (0,), None), ("Mackay", (1, 2), None), ("Gladstone", (3, 4), None),
                ("Spare", (5,), None)])
    recs = [r for r in table_records(g) if r.row_id.endswith("Mackay")]
    assert len(recs) == 2, [r.row_id for r in recs]
    by_value = {c.value: c for c in recs[0].concepts}
    assert {"v00", "v01", "v02", "v05"} <= set(by_value), sorted(by_value)   # shared + own
    assert "v03" not in by_value and "v04" not in by_value, sorted(by_value)  # the sibling's

    # § 3.2: the SHARED columns keep their own field names -- they are copied in unchanged.
    assert by_value["v00"].text == "Year"
    assert by_value["v05"].text == "Spare"
    # § 3.2: "H's leaf cells, each with an EMPTY header text. Nothing is invented." The port
    # label has become the record's KEY, so it is no longer the name of the field its own
    # columns sit under -- and no other name is available without inventing one (CLAUDE.md §7).
    # Before the split these two cells read text='Mackay', which is what made two measures
    # collapse onto one property (handoff § 8b).
    assert by_value["v01"].text == "", by_value["v01"]
    assert by_value["v02"].text == "", by_value["v02"]


def test_the_spanning_label_is_carried_as_a_key_candidate():
    """The label becomes a concept whose TEXT IS ITS VALUE — the same kind of concept R207
    grounds, which is why Task 5 routes it to `marker_field` rather than to `exact_field`."""
    from iladub.feed import table_records

    g = _table([("Mackay", (0, 1), None), ("Gladstone", (2, 3), None),
                ("Portland", (4, 5), None)])
    rec = next(r for r in table_records(g) if r.row_id.endswith("Mackay"))
    key = [c for c in rec.concepts if c.value == "Mackay"]
    assert len(key) == 1, [(c.text, c.value) for c in rec.concepts]
    assert key[0].text == "Mackay"
    assert key[0].is_split_key is True
    assert key[0].is_section_marker is False, "the split key is a SIBLING flag, not this one"


# --- the negatives -----------------------------------------------------------------------

def test_a_single_column_header_does_not_split_and_stays_a_field_name():
    """`Year` and `Elevation Period` span ONE column each. THE FALSIFIER for this task: delete
    *covers more than one* and `Year` becomes a key."""
    from iladub.feed import table_records

    g = _table([("Year", (0,), None), ("Period", (1,), None), ("A", (2,), None),
                ("B", (3,), None), ("C", (4,), None), ("D", (5,), None)])
    recs = table_records(g)
    assert len(recs) == 2, [r.row_id for r in recs]
    assert not any(r.row_id.endswith("Year") for r in recs), [r.row_id for r in recs]
    texts = {c.text for c in recs[0].concepts}
    assert "Year" in texts, texts            # still a FIELD NAME
    assert not any(c.value == "Year" for c in recs[0].concepts)


def test_a_multi_column_header_WITH_children_does_not_split():
    """apple's 2 and who's 6 nodes, in CI. They cover several columns and have children, so the
    childless clause excludes them — delete it and those documents' column groups split."""
    from iladub.feed import table_records

    g = _table([("Group", (0, 1, 2), None), ("L", (0,), "Group"), ("M", (1,), "Group"),
                ("N", (2,), "Group"), ("Other", (3, 4, 5), None), ("P", (3,), "Other"),
                ("Q", (4,), "Other"), ("R", (5,), "Other")])
    recs = table_records(g)
    assert len(recs) == 2, [r.row_id for r in recs]


def test_an_unsplit_table_keeps_byte_identical_records():
    """Every table the condition does not fire on must read exactly as it does today — the
    guarantee that makes this change safe on 6 of the 7 corpus documents."""
    from iladub.feed import table_records

    g = _table([("A", (0,), None), ("B", (1,), None), ("C", (2,), None),
                ("D", (3,), None), ("E", (4,), None), ("F", (5,), None)])
    recs = table_records(g)
    assert [r.row_id for r in recs] == ["r0", "r1"] or len(recs) == 2
    assert all(len(r.concepts) == 6 for r in recs), [len(r.concepts) for r in recs]


# --- the corpus --------------------------------------------------------------------------

# --- Task 5: the oracle — one oracle, two populations ------------------------------------

def _contract_and_terms():
    """A scheme-bound `port` field and a plain `year` field, with two ports in the scheme."""
    from rdflib import Literal, Namespace
    from rdflib.namespace import SKOS

    from iladub.ground import Contract, ContractField

    ship = Namespace("https://example.org/ship#")
    terms = Graph()
    for label in ("Mackay", "Gladstone"):
        terms.add((ship[label.lower()], SKOS.inScheme, ship["scheme-port"]))
        terms.add((ship[label.lower()], SKOS.prefLabel, Literal(label)))
    contract = Contract(str(ship.Capacity), (
        ContractField(str(ship.fPort), str(ship.port), str(ship["scheme-port"])),
        ContractField(str(ship.fYear), str(ship.year), None),
    ))
    return contract, terms


class _Abstain:
    """The battery's posture: proposes nothing, so only `exact_field` and `marker_field` can
    ground. Anything they cannot place is quarantined, which is the honest outcome (§ 3.3)."""

    def propose_grounding(self, concept, fields):
        from types import SimpleNamespace
        return SimpleNamespace(field_iri=None, anchor_iri="https://example.org/anchor#x",
                               confidence=0.0, rationale="abstains",
                               suggester_iri="urn:iladub:suggester/abstaining")


def test_a_split_key_grounds_through_the_same_oracle_a_section_marker_uses():
    """DECISION E, end to end. THE FALSIFIER for Task 5: revert `marker_field`'s gate to the
    single `is_section_marker` flag and this goes RED — the split key quarantines instead."""
    from rdflib import URIRef

    from iladub.ground import SurfaceConcept, ground_concept

    contract, terms = _contract_and_terms()
    g = Graph()
    status = ground_concept(
        SurfaceConcept("Mackay", "Mackay", "reg", is_split_key=True),
        contract, URIRef("urn:iladub:record:x"), _Abstain(), terms, Graph(), g)
    assert status == "grounded", status


def test_a_split_key_no_scheme_admits_is_quarantined_and_the_records_stay_split():
    """§ 3.2's disposal: none or several admitting fields means the KEY is a proposition. The
    split itself is the author's structure and does not depend on the contract, so the records
    remain split either way — grounding decides the key's name, never the record's existence."""
    from rdflib import URIRef

    from iladub.feed import table_records
    from iladub.ground import SurfaceConcept, ground_concept

    contract, terms = _contract_and_terms()
    g = Graph()
    status = ground_concept(
        SurfaceConcept("Nowhere", "Nowhere", "reg", is_split_key=True),
        contract, URIRef("urn:iladub:record:y"), _Abstain(), terms, Graph(), g)
    assert status == "proposed", status

    split = _table([("Nowhere", (0, 1), None), ("Elsewhere", (2, 3), None),
                    ("Absent", (4, 5), None)])
    assert len(table_records(split)) == 6


def test_a_plain_data_cell_is_still_not_admitted_to_the_marker_oracle():
    """The gate WIDENED to a second population; it did not open. A data cell whose value happens
    to be a port label carries neither flag, so grounding it by value alone — letting the value
    rather than the author's structure decide the field — stays impossible (§0)."""
    from rdflib import URIRef

    from iladub.ground import SurfaceConcept, ground_concept

    contract, terms = _contract_and_terms()
    g = Graph()
    status = ground_concept(
        SurfaceConcept("", "Mackay", "reg"), contract, URIRef("urn:iladub:record:z"),
        _Abstain(), terms, Graph(), g)
    assert status == "proposed", status


@corpus_only
def test_graincorp_p0_splits_27_rows_into_one_record_per_port():
    """The document. 27 rows x 7 ports = 189 records, each carrying Year, Elevation Period and
    its own port's two leaf cells. MEASURED: the condition fires on this document and no other."""
    from iladub.etkl.compile import compile_tables
    from iladub.feed import table_records

    rep = compile_tables(GRAINCORP, 0, validate_shapes=False)
    recs = table_records(rep.graph)
    assert len(recs) == 189, len(recs)
    assert len({r.row_id for r in recs}) == 189

    ports = ("Mackay", "Gladstone", "Fisherman Islands", "Carrington", "Port Kembla",
             "Geelong", "Portland")
    for p in ports:
        assert sum(1 for r in recs if r.row_id.endswith(p)) == 27, p
    rec = next(r for r in recs if r.row_id.endswith("Mackay"))
    assert any(c.text == "Year" for c in rec.concepts)
    assert any(c.value == "Mackay" and c.is_split_key for c in rec.concepts)
