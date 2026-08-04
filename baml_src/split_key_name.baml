class ScoredKeyCandidate {
  name string @description("proposed name for the denormalized split-key dimension, e.g. 'port'")
  anchor_iri string @description("a suggested upper-ontology (gist) class IRI for the dimension")
  score float @description("0.0-1.0 calibrated confidence")
  rationale string @description("one sentence on why")
}

function ProposeSplitKeyName(markers: string[], context: string) -> ScoredKeyCandidate[] {
  client Claude
  prompt #"
    A document's rows are grouped under repeating section markers (bare values, no field
    name attached): {{ markers }}.
    Document context: {{ context }}
    What single dimension do these markers name (e.g. "port", "region", "commodity")?
    Propose one or more ranked candidate names, each with a suggested upper-ontology
    (gist) anchor class and a calibrated confidence.
    {{ ctx.output_format }}
  "#
}
