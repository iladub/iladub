class DimensionNameProposal {
  name string @description("the single attribute/dimension name these column labels are the values of")
  confidence float @description("0.0-1.0, calibrated confidence in the name")
  rationale string @description("one sentence on why")
}

function ProposeDimensionName(values: string[], stub: string?, table_title: string?) -> DimensionNameProposal {
  client Claude
  prompt #"
    These column labels are the VALUES of one pivoted dimension in a table: {{ values }}.
    The row-key (stub) column is: {{ stub }}. Table title: {{ table_title }}.
    Name the single dimension whose values these are (one word or short phrase, e.g. "Quarter" for Q1..Q4).
    {{ ctx.output_format }}
  "#
}
