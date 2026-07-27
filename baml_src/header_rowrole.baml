class HeaderRowRoleProposal {
  roles string[] @description("exactly one of furniture|continuation|level per non-leaf header row, in the same top-to-bottom order as the input rows")
  confidence float @description("0.0-1.0, calibrated confidence in the whole reading")
  rationale string @description("one sentence per row on why")
}

function ProposeHeaderRowRoles(
  rows: string[][], leaf_labels: string[], row_columns: int[][]
) -> HeaderRowRoleProposal {
  client Claude
  prompt #"
    A table's header region was read as several rows of text. The BOTTOM row holds the
    column labels (one per column): {{ leaf_labels }}.

    The rows ABOVE it are: {{ rows }}, and for each of their cells the column index the cell
    sits over is: {{ row_columns }}.

    Classify EACH row above the bottom row, top to bottom, as exactly one of:
      - "furniture"    — not part of the table: a report date, a title, a page number.
      - "continuation" — a wrapped fragment of the column label below it; joining it to that
                         label (fragment first) produces the real column name.
      - "level"        — a genuine hierarchical group label spanning several columns, where the
                         labels below it are its sub-columns.

    Use the column indices to see WHICH label a fragment would complete: a fragment sitting over
    the same column as a label below it, that reads as the start of a longer name, is a
    "continuation". A column index of -1 means the cell's ink sits outside every column of the
    table — a strong signal that the row is "furniture", not a "continuation". Prefer
    "continuation" over "furniture" whenever a fragment plausibly reads as part of a label —
    "furniture" discards text from the table, so it is the lossy answer and must be reserved for
    lines that genuinely are not header content.

    Return one role per row above the bottom row, in order.
    {{ ctx.output_format }}
  "#
}
