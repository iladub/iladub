class GroundingProposal {
  field_iri string? @description("IRI of the contract field this concept grounds to, or null if genuinely novel")
  anchor_iri string @description("a suggested upper-ontology (gist) class IRI for the concept")
  confidence float @description("0.0-1.0 calibrated confidence")
  rationale string @description("one sentence on why")
}

// page_context carries the document furniture the reader did NOT read as table content -- the
// title, the date line, the footer -- as etkl:IgnoredBand/etkl:bandText put them in the graph
// ([[R212]]). It exists because of the maintainer's 2026-09-12 ruling that the MACHINE derives
// an unlabelled measure's name, not the contract author: an unlabelled leaf arrives here with
// surface_text == "", so without the page the prompt reads "A document field reads  = 845870."
// and the question has a blank subject. Optional, so every caller that has no page still works.
function ProposeGrounding(surface_text: string, value: string, field_labels: string[], page_context: string?) -> GroundingProposal {
  client Claude
  prompt #"
    A document field reads {{ surface_text }} = {{ value }}.
    The target contract offers these field labels: {{ field_labels }}.
    {% if page_context %}
    The page this value was read from carries this text outside the table itself -- its title,
    date line and footer. Use it to work out what an UNLABELLED column measures, and ignore it
    where the field already names itself:
    {{ page_context }}
    {% endif %}
    Which contract field does this ground to (return its exact label), or null if none fits?
    Also suggest an upper-ontology (gist) anchor class and a calibrated confidence.
    {{ ctx.output_format }}
  "#
}
