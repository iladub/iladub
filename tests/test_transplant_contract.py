import os
from iladub.contract import SemanticDataContract

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")


def test_contract_loads_target_class():
    c = SemanticDataContract.from_files(
        os.path.join(TXD, "offer-contract.ttl"),
        os.path.join(TXD, "offer-shapes.ttl"),
        os.path.join(TXD, "transplant-terms.ttl"),
    )
    assert any(str(tc).endswith("OrganOffer") for tc in c.target_classes())


def test_offer_document_mentions_unmapped_term():
    with open(os.path.join(TXD, "offer.txt"), encoding="utf-8") as fh:
        text = fh.read()
    assert "takotsubo" in text  # the deliberate proposition trigger
