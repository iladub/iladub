# Reference use case — Swiss clinical documents → FHIR

A demonstrator of the whole stack on a *typically Swiss* problem: a German-language
consultation report that must become machine-readable, terminology-validated,
FHIR-conformant, and decision-aware — feeding the kind of semantically-validated FHIR
the Swiss Health Data Space / national FHIR terminology server expects to consume.

Why this domain: it is high-value, document-centric (the EPR moves PDFs), federated and
multilingual (de/fr/it), and **not** tied to any commodity-trading employer's domain.

## What the demo shows (all on synthetic data)

- A free-text German consultation report is read once (knowledge-driven concept
  recognition over prose — the ontology drives extraction).
- A declarative contract maps recognized concepts to **~10 cross-referenced FHIR
  resource types** (Composition, Encounter, Patient, Practitioner, PractitionerRole,
  Organization, Condition ×2, Observation/eGFR, MedicationStatement, MedicationRequest)
  with subject/requester/author/reason references wired between them.
- Terminology is bound to SKOS-projected concepts (SNOMED/LOINC) with multilingual
  labels; a value can be read in German and rendered in French — *concepts, not strings*.
- The therapy change is captured as a `dec:DecisionHolon` over the FHIR layer:
  evidence (the conditions/observation), the rejected option and why, the deciding
  clinician, the governing guideline, and `produced` → the MedicationRequest.
- Validated against CH-Core-style FHIR shapes **and** the `dec` decision shapes.

## The point

FHIR can carry the new prescription. It cannot carry *the option that was rejected, and
why* — that a clinician reading in another language now sees without a phone call.
Tables, prose, and (eventually) figures converge on the same concept IRIs; the contract
and the ontology supply the structure before any transformation runs.

> Synthetic data only. SNOMED CT / LOINC identifiers are illustrative — confirm
> terminology licensing before redistributing real mappings.
