from rdflib import Namespace, Literal
from rdflib.namespace import RDF
from iladub.events import Event

DEC = Namespace("https://w3id.org/iladub/dec#")
TX = Namespace("https://example.org/transplant#")


def test_event_holds_condition_and_payload():
    e = Event("ischemiaExceeded", {"projected_ischemia_minutes": 270})
    assert e.condition == "ischemiaExceeded"
    assert e.payload["projected_ischemia_minutes"] == 270


def test_event_to_rdf_emits_typed_node_with_condition():
    e = Event("ischemiaExceeded", {})
    g = e.to_rdf(TX["event-1"])
    assert (TX["event-1"], RDF.type, DEC.Event) in g
    assert (TX["event-1"], DEC.condition, Literal("ischemiaExceeded")) in g
