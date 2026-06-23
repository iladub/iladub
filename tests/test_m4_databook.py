import os
from rdflib import Namespace
from rdflib.namespace import RDF
from iladub.databook import read_databook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXD = os.path.join(ROOT, "examples", "transplant")

def test_raw_offer_databook_loads():
    db = read_databook(os.path.join(TXD, "offer.databook.md"))
    assert db.frontmatter["id"].endswith("offer-2026-0091")
    assert db.frontmatter["source"]["reference"] == "ET-2026-0091"
    assert "Organ offered: HEART" in db.prose
