"""The statement contract on a real statement: the corpus arm of the matrix-cell loop.

Spec: docs/superpowers/specs/2026-10-12-a-matrix-cell-is-an-observation-design.md § 5 (P1 to P6)
and § 9.2 (P3 restated). Corpus-marked: skips when corpus/ is not populated. The CI arm, on a
matrix built in the test, is `tests/test_finance_contract.py`.

EVERY COUNT HERE WAS A PREDICTION BEFORE IT WAS A PIN. Each is derived in a comment from what the
feed was measured to deliver (the Task 2 report's `## APPLE OUTPUTS`: 180 records of three
concepts; 128 unshared and 52 shared row keys; six column-key texts; seven figure shapes) and
from `examples/finance/`, then compared with the run. A count that moves is a reading that moved
or a contract that changed, and the comment says which arithmetic to redo.

One compile for the module: `ground_document` writes into the graph it is handed and never into
the compiled one.
"""
from collections import Counter
from pathlib import Path

import pytest
from rdflib import Graph, Namespace, RDF

REPO = Path(__file__).resolve().parent.parent
APPLE = REPO / "corpus" / "financial" / "apple-fy2026q3-statements.pdf"
CONTRACT = REPO / "examples" / "finance" / "statement-contract.ttl"
TERMS = REPO / "examples" / "finance" / "statement-terms.ttl"
SHAPES = REPO / "examples" / "finance" / "statement-shapes.ttl"

FIN = Namespace("https://example.org/finance#")
ILA = Namespace("https://w3id.org/iladub#")

pytestmark = [pytest.mark.corpus,
              pytest.mark.skipif(not APPLE.is_file(),
                                 reason="corpus not populated (scripts/fetch_corpus.py)")]

# DERIVED, label -> row-key concepts, from the 128 unshared row keys the feed delivers (44
# distinct texts) and the 13 prefLabels of `fin:scheme-line-item`. A label on the four-period
# statement mints 4 row keys, one on the two-period statement mints 2.
SCHEME_COVER = {
    "Gross margin": 4,
    "Total operating expenses": 4,
    "Operating income": 4,
    "Provision for income taxes": 4,
    "Net income": 4,
    "Cash and cash equivalents": 2,
    "Inventories": 2,
    "Total current assets": 2,
    "Total assets": 2,
    "Accounts payable": 2,
    "Total current liabilities": 2,
    "Total liabilities": 2,
}
# The thirteenth prefLabel, `Total net sales`, is on 8 SHARED row keys and on no unshared one:
# the unshared line prints as `Total net sales (1)`, a different text. So it grounds nothing.
ROW_KEYS_GROUNDED = sum(SCHEME_COVER.values())          # 5 x 4 + 7 x 2 = 34 of the 128
# grounded = 34 row keys + 180 periods + 180 figures; proposed = (128 - 34) + 52 shared.
GROUNDED = ROW_KEYS_GROUNDED + 180 + 180                # 394
PROPOSED = (128 - ROW_KEYS_GROUNDED) + 52               # 146


class _Recording:
    """A proposer that answers with one fixed proposal and keeps what it was asked."""

    def __init__(self, proposal):
        self.proposal = proposal
        self.asked = []

    def propose_grounding(self, concept, fields, page_context=None):
        self.asked.append(concept)
        return self.proposal


@pytest.fixture(scope="module")
def apple():
    from iladub.etkl.document import compile_document
    return compile_document(str(APPLE)).graph


@pytest.fixture(scope="module")
def records(apple):
    from iladub.feed import table_records
    return table_records(apple, per_cell=True)


def _grounded(apple, field_iri):
    """`ground_document` under a proposer that names `field_iri` (or abstains, for None), with
    the promotion membrane run: P6 is that this returns at all."""
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import GroundingProposal
    proposer = _Recording(GroundingProposal(field_iri, str(FIN) + "x", 0.9, "fixed",
                                            "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(apple, load_contract(str(CONTRACT)), proposer,
                             Graph().parse(str(TERMS), format="turtle"),
                             Graph().parse(str(SHAPES), format="turtle"), g,
                             validate_shapes=True)
    return result, g, proposer


@pytest.fixture(scope="module")
def abstaining(apple):
    return _grounded(apple, None)


@pytest.fixture(scope="module")
def naming(apple):
    """Spec § 9.2's arm: the proposer names the row-key field for whatever it is asked."""
    return _grounded(apple, str(FIN["f-line-item"]))


def _by_subject(g, prop):
    out = {}
    for s, o in g.subject_objects(prop):
        out.setdefault(s, []).append(str(o))
    return out


def _subject_of(record):
    from iladub.feed import _record_uri
    return _record_uri(record.row_id)


def _concept(record, role):
    return next(c for c in record.concepts if c.role == role)


def test_p1_one_record_per_cell(abstaining):
    result, _, _ = abstaining
    assert result.records == 180
    assert result.grounded + result.proposed == 540


def test_no_two_cells_share_a_subject(records, abstaining):
    _, g, _ = abstaining
    assert len({_subject_of(r) for r in records}) == 180
    assert len(set(g.subjects(RDF.type, FIN.StatementFigure))) == 180


def test_p2_every_period_grounds(abstaining):
    _, g, _ = abstaining
    periods = _by_subject(g, FIN.period)
    counts = Counter(v for vs in periods.values() for v in vs)
    assert sum(counts.values()) == 180, counts
    assert len(periods) == 180 and all(len(v) == 1 for v in periods.values())
    assert len(counts) == 6, counts


def test_p4_every_figure_grounds(records, abstaining):
    """D7: the numeral pattern admits a leading `$ `, which 40 of the 180 cells carry inside
    the cell text, and the value is carried as printed. Predicted 180 under that choice."""
    from iladub.ground import ROLE_CELL_VALUE
    _, g, _ = abstaining
    values = _by_subject(g, FIN.value)
    refused = sorted(_concept(r, ROLE_CELL_VALUE).value for r in records
                     if _subject_of(r) not in values)
    assert sum(len(v) for v in values.values()) == 180, f"refused figures: {refused}"
    assert refused == []
    assert sum(1 for vs in values.values() for v in vs if v.startswith("$ ")) == 40


def test_the_scheme_grounds_the_row_keys_it_carries(abstaining):
    _, g, _ = abstaining
    counts = Counter(v for vs in _by_subject(g, FIN.lineItem).values() for v in vs)
    assert dict(counts) == SCHEME_COVER
    assert sum(counts.values()) == ROW_KEYS_GROUNDED == 34


def test_the_tally_is_the_sum_of_its_three_roles(abstaining):
    from iladub.feed import FeedResult
    result, _, proposer = abstaining
    assert result == FeedResult(180, GROUNDED, PROPOSED) == FeedResult(180, 394, 146)
    # Every concept of a matrix record has a role, and apple's rows carry no role-less rider
    # (no section marker, no group key): nothing is left for a proposer.
    assert proposer.asked == []


def test_p3_a_shared_row_label_never_grounds(records, naming):
    """Spec § 9.2: 52 row keys are shared, 8 of them `Total net sales`, which the scheme
    admits. Under a proposer that names the row-key field none of the 52 grounds, and no line
    item is carried twice under one period."""
    from iladub.feed import FeedResult
    from iladub.ground import SHARED_ROW_KEY
    result, g, proposer = naming
    shared = [r for r in records if any(c.role == SHARED_ROW_KEY for c in r.concepts)]
    assert len(shared) == 52
    assert sum(1 for r in shared
               if _concept(r, SHARED_ROW_KEY).value == "Total net sales") == 8
    line_items = _by_subject(g, FIN.lineItem)
    periods = _by_subject(g, FIN.period)
    leaked = sorted((line_items[_subject_of(r)][0], periods.get(_subject_of(r), [""])[0])
                    for r in shared if _subject_of(r) in line_items)
    assert leaked == [], f"shared row labels grounded as line items: {leaked}"
    assert all(len(v) == 1 for v in line_items.values())
    # a subject whose period did not ground has no pair to collide on, and is P2's to report
    keyed = Counter((line_items[s][0], periods[s][0]) for s in line_items if s in periods)
    assert [k for k, n in keyed.items() if n > 1] == []
    # the rule refuses before any field is looked for, so the proposer is never asked and the
    # tally is the abstaining arm's
    assert proposer.asked == []
    assert result == FeedResult(180, GROUNDED, PROPOSED)


def test_p6_the_promotion_membrane_conforms(abstaining, naming):
    """`validate_shapes=True` already raised if it did not; said again so the claim has a name."""
    from iladub.feed import _validate_grounding
    for _, g, _ in (abstaining, naming):
        conforms, report = _validate_grounding(g)
        assert conforms, report
