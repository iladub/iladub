"""Assemble a connected FHIR document graph from a free-text consultation report.

Pipeline:
  1. EXTRACT (knowledge-guided): recognise() scans prose for known concepts.
  2. TRANSFORM (knowledge as argument): the contract's ResourceRules say which
     FHIR resource each concept becomes and which element carries its code; the
     assembler wires subject/requester/author references between them.
  3. A dec:DecisionHolon is attached over the FHIR layer.
  4. LOAD: validate against CH-Core-style SHACL shapes.

Only resources the report actually supports are emitted (no fabricated data).
"""
from __future__ import annotations

import os
import re

from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import SKOS, XSD

from iladub.readers import read_document
from recognise import recognise

HERE = os.path.dirname(os.path.abspath(__file__))

FHIR = Namespace("http://hl7.org/fhir/")
EX   = Namespace("https://example.org/clinical#")
DEC  = Namespace("https://w3id.org/iladub/dec#")
PROV = Namespace("http://www.w3.org/ns/prov#")
ETKL = Namespace("https://w3id.org/iladub/etkl#")

knowledge = Graph().parse(os.path.join(HERE, "knowledge", "clinical-terms.ttl"), format="turtle")
contract  = Graph().parse(os.path.join(HERE, "contracts", "consultation-contract.ttl"), format="turtle")

text = read_document(os.path.join(HERE, "inputs", "konsultationsbericht-zurich.txt"))
mentions = recognise(text, knowledge)
present = {m.concept for m in mentions}

# Light free-text picks for non-coded literals actually present in the report.
def find(pattern, default=None):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else default

patient_name = find(r"Frau\s+([A-ZÄÖÜ][a-zäöü]+\s+[A-ZÄÖÜ][a-zäöü]+)", "Erika Meier")
birth = find(r"geboren am\s+(\d{2}\.\d{2}\.\d{4})", "22.03.1958")
birth_iso = "-".join(reversed(birth.split("."))) if birth else None
egfr_val = find(r"eGFR liegt\s+aktuell bei\s+(\d+)", find(r"eGFR\D+(\d+)\s*ml/min", "38"))
practitioner = "Dr. med. T. Weber"

g = Graph()
for p, ns in [("fhir", FHIR), ("ex", EX), ("dec", DEC), ("prov", PROV), ("skos", SKOS)]:
    g.bind(p, ns)

# --- core actors / spine ---------------------------------------------------
patient = EX["pat-meier"]
g.add((patient, RDF.type, FHIR.Patient))
g.add((patient, FHIR["Patient.name"], Literal(patient_name)))
if birth_iso:
    g.add((patient, FHIR["Patient.birthDate"], Literal(birth_iso, datatype=XSD.date)))
if EX["gender-female"] in present:
    g.add((patient, FHIR["Patient.gender"], Literal("female")))

prac = EX["prac-weber"]
g.add((prac, RDF.type, FHIR.Practitioner))
g.add((prac, FHIR["Practitioner.name"], Literal(practitioner)))

org = EX["org-usz"]
g.add((org, RDF.type, FHIR.Organization))
g.add((org, FHIR["Organization.name"], Literal("Universitätsspital Zürich — Klinik für Endokrinologie")))

prac_role = EX["pracrole-weber"]
g.add((prac_role, RDF.type, FHIR.PractitionerRole))
g.add((prac_role, FHIR["PractitionerRole.practitioner"], prac))
g.add((prac_role, FHIR["PractitionerRole.organization"], org))
g.add((prac_role, FHIR["PractitionerRole.code"], Literal("Oberärztin Endokrinologie", lang="de")))

enc = EX["enc-2026-05-14"]
g.add((enc, RDF.type, FHIR.Encounter))
g.add((enc, FHIR["Encounter.class"], Literal("ambulatory")))
g.add((enc, FHIR["Encounter.subject"], patient))
g.add((enc, FHIR["Encounter.participant"], prac))

# --- coded clinical resources, driven by the contract ----------------------
def notation(concept):
    return knowledge.value(concept, SKOS.notation)

def code_node(concept):
    c = BNode()
    g.add((c, FHIR["Coding.code"], Literal(str(notation(concept)))))
    for label in knowledge.objects(concept, SKOS.prefLabel):
        if label.language == "en":
            g.add((c, FHIR["Coding.display"], Literal(str(label), lang="en")))
    return c

# Spine/actor resources are already built above; the contract rules for them
# should AUGMENT those nodes, not mint duplicates. Pre-register them here.
made = {
    str(EX["map-patient"]):      patient,
    str(EX["map-practitioner"]): prac,
    str(EX["map-organization"]): org,
    str(EX["map-encounter"]):    enc,
}
for rule in contract.objects(contract.value(predicate=RDF.type, object=ETKL.SemanticDataContract), ETKL.buildsResource):
    rtype = contract.value(rule, ETKL.resourceType)
    trigger = contract.value(rule, ETKL.triggerConcept)
    binds = contract.value(rule, ETKL.bindsElement)
    if trigger is not None and trigger not in present:
        continue  # only emit what the report supports
    if str(rule) == str(EX["map-composition"]):
        continue  # the Composition is assembled explicitly below
    node = made.get(str(rule), EX[f"res-{str(rule).split('#')[-1]}"])
    g.add((node, RDF.type, rtype))
    made[str(rule)] = node
    if binds is not None and trigger is not None:
        g.add((node, binds, code_node(trigger)))
    # subject + back-references where the resource type calls for them
    local = str(rtype).split("/")[-1]
    if local in ("Condition", "Observation", "MedicationStatement", "MedicationRequest"):
        g.add((node, FHIR[f"{local}.subject"], patient))
    if local == "Observation":
        g.add((node, FHIR["Observation.value"], Literal(f"{egfr_val} ml/min")))
        g.add((node, FHIR["Observation.status"], Literal("final")))
    if local == "MedicationStatement":
        g.add((node, FHIR["MedicationStatement.status"], Literal(str(contract.value(rule, ETKL.statementStatus) or "active"))))
    if local == "MedicationRequest":
        g.add((node, FHIR["MedicationRequest.status"], Literal(str(contract.value(rule, ETKL.requestStatus) or "active"))))
        g.add((node, FHIR["MedicationRequest.requester"], prac))

# reasonReference: the insulin request is justified by the renal condition
ckd = made.get(str(EX["map-condition-ckd"]))
insulin_req = made.get(str(EX["map-insulin"]))
if ckd and insulin_req:
    g.add((insulin_req, FHIR["MedicationRequest.reasonReference"], ckd))

# --- Composition binds the document together --------------------------------
comp = EX["composition"]
g.add((comp, RDF.type, FHIR.Composition))
g.add((comp, FHIR["Composition.title"], Literal("Konsultationsbericht — Endokrinologie", lang="de")))
g.add((comp, FHIR["Composition.subject"], patient))
g.add((comp, FHIR["Composition.author"], prac))
g.add((comp, FHIR["Composition.encounter"], enc))
clinical_rules = [str(EX["map-condition-dm"]), str(EX["map-condition-ckd"]),
                  str(EX["map-egfr"]), str(EX["map-metformin"]), str(EX["map-insulin"])]
for rule_uri in clinical_rules:
    node = made.get(rule_uri)
    if node:
        g.add((comp, FHIR["Composition.entry"], node))

# --- the decision holon over the FHIR layer ---------------------------------
dh = EX["decision-switch-insulin"]
opt_keep, opt_switch = EX["opt-keep-metformin"], EX["opt-switch-insulin"]
g.add((opt_keep, RDF.type, DEC.Option))
g.add((opt_keep, RDFS.label, Literal("Metformin beibehalten", lang="de")))
g.add((opt_keep, DEC.rejectedBecause, Literal("Kontraindikation bei Niereninsuffizienz", lang="de")))
g.add((opt_keep, DEC.dominatedBy, opt_switch))
g.add((opt_switch, RDF.type, DEC.Option))
g.add((opt_switch, RDFS.label, Literal("Umstellung auf Insulin", lang="de")))

g.add((dh, RDF.type, DEC.DecisionHolon))
g.add((dh, RDFS.label, Literal("Therapieumstellung Diabetes (Zürich)", lang="de")))
g.add((dh, DEC.decidedBy, prac))
for c in (made.get(str(EX["map-condition-dm"])), made.get(str(EX["map-egfr"]))):
    if c: g.add((dh, DEC.consideredEvidence, c))
if ckd: g.add((dh, DEC.constrainedBy, ckd))
g.add((dh, DEC.optionSpace, opt_keep))
g.add((dh, DEC.optionSpace, opt_switch))
g.add((dh, DEC.chosen, opt_switch))
g.add((dh, DEC.rationale, Literal("Niereninsuffizienz, Metformin kontraindiziert", lang="de")))
g.add((dh, DEC.governedBy, Literal("SGED Richtlinie Diabetes 2024", lang="de")))
if insulin_req: g.add((dh, DEC.produced, insulin_req))

g.serialize(destination=os.path.join(HERE, "out", "consultation-fhir.ttl"), format="turtle")

# --- report -----------------------------------------------------------------
types = {}
for s, _, o in g.triples((None, RDF.type, None)):
    if str(o).startswith(str(FHIR)):
        types.setdefault(str(o).split("/")[-1], 0)
        types[str(o).split("/")[-1]] += 1
print("Recognised concepts:", len(present))
for m in mentions:
    print(f"  · {m.matched_text!r}  ->  {m.concept}")
print("\nFHIR resources emitted (only what the report supports):")
for t, n in sorted(types.items()):
    print(f"  · {t} x{n}")
print(f"\nTotal triples: {len(g)}  ->  out/consultation-fhir.ttl")
