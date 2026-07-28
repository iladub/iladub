class HeaderRowRoleProposal {
  roles string[] @description("exactly one of furniture|continuation|level per non-leaf header row, in the same top-to-bottom order as the input rows")
  confidence float @description("0.0-1.0, calibrated confidence in the whole reading")
  rationale string @description("one sentence per row on why")
}

function ProposeHeaderRowRoles(
  rows: string[][], leaf_labels: string[], row_columns: int[][],
  merge_candidates: string[][], row_cell_counts: int[], leaf_column_count: int
) -> HeaderRowRoleProposal {
  client Claude
  prompt #"
    A table's header region was read as several rows of text. The BOTTOM row holds the
    column labels (one per column): {{ leaf_labels }}. The table has {{ leaf_column_count }}
    columns.

    The rows ABOVE it are: {{ rows }}, and for each of their cells the column index the cell
    sits over is: {{ row_columns }}. Each of those rows has this many cells: {{ row_cell_counts }}.

    If a cell were read as a "continuation", joining it to the label below would produce:
    {{ merge_candidates }} (an empty string means the cell sits over no column that has a label,
    so it CANNOT be a continuation). Each candidate is computed per cell IN ISOLATION, one row at
    a time — so when SEVERAL rows above the same column are all read as "continuation", their
    fragments compose top to bottom into the final label ("Date of Grain" + "Loading" +
    "Commencement" -> "Date of Grain Loading Commencement"); a single candidate shown here may be
    only a fragment of that final name, not the whole of it.

    Classify EACH row above the bottom row, top to bottom, as exactly one of:
      - "furniture"    — not part of the table: a report date, a title, a page number.
      - "continuation" — a wrapped fragment of the column label below it; joining it to that
                         label (fragment first) produces the real column name.
      - "level"        — a genuine hierarchical group label spanning several columns, where the
                         labels below it are its sub-columns.

    Judge each candidate join on whether it READS AS A SINGLE COLUMN NAME. "Date of Grain" joined
    to "Commencement" gives "Date of Grain Loading Commencement" — a real column name, so that row
    is a "continuation". "Monday" joined to "Qty" gives "Monday Qty" — two unrelated things, so
    that row is not. This is the decisive evidence: a short merged group label and a wrapped
    fragment have IDENTICAL geometry, and only the language tells them apart.

    A row with a single cell over a table of many columns is more likely a title than a group
    label — UNLESS it plausibly groups a subset of the columns beneath it (a lone "Region" over
    four direction columns beside a "Year" stub IS a genuine group label). Weigh
    {{ row_cell_counts }} against {{ leaf_column_count }} with that exception in mind.

    Use the column indices to see WHICH label a fragment would complete. A column index of -1
    means the cell's ink sits outside every column of the table — a strong signal that the row is
    "furniture", not a "continuation". Prefer "continuation" over "furniture" whenever a fragment
    plausibly reads as part of a label — "furniture" discards text from the table, so it is the
    lossy answer and must be reserved for lines that genuinely are not header content.

    Return one role per row above the bottom row, in order.
    {{ ctx.output_format }}
  "#
}
