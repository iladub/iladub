class GroundingProposal {
  field_iri string? @description("IRI of the contract field this concept grounds to, or null if genuinely novel")
  anchor_iri string @description("a suggested upper-ontology (gist) class IRI for the concept")
  confidence float @description("0.0-1.0 calibrated confidence")
  rationale string @description("one sentence on why")
}

function ProposeGrounding(surface_text: string, value: string, field_labels: string[]) -> GroundingProposal {
  client Claude
  prompt #"
    A document field reads {{ surface_text }} = {{ value }}.
    The target contract offers these field labels: {{ field_labels }}.
    Which contract field does this ground to (return its exact label), or null if none fits?
    Also suggest an upper-ontology (gist) anchor class and a calibrated confidence.
    {{ ctx.output_format }}
  "#
}
