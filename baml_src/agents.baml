function ExtractDonorClinical(doc: string) -> DonorClinical {
  client Claude
  prompt #"
    From the donor organ offer below, extract ONLY donor clinical facts:
    organ, ejectionFraction, causeOfDeath, sizeMetric.
    For each, copy the exact source phrase into source_quote and give a 0..1 confidence.
    If a field is absent, omit it. Do not invent values.

    Document:
    ---
    {{ doc }}
    ---
    {{ ctx.output_format }}
  "#
}

function ExtractImmunology(doc: string) -> Immunology {
  client Claude
  prompt #"
    From the donor organ offer below, extract ONLY immunology facts:
    aboGroup, hlaTyping, serology. Copy the exact source phrase into source_quote
    and give a 0..1 confidence. Omit absent fields. Do not invent values.

    Document:
    ---
    {{ doc }}
    ---
    {{ ctx.output_format }}
  "#
}

function ExtractLogistics(doc: string) -> Logistics {
  client Claude
  prompt #"
    From the donor organ offer below, extract ONLY logistics facts:
    projectedTransportMinutes. Copy the exact source phrase into source_quote
    and give a 0..1 confidence. Omit absent fields. Do not invent values.

    Document:
    ---
    {{ doc }}
    ---
    {{ ctx.output_format }}
  "#
}
