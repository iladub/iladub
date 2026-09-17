// LEAN v2. Two repairs over v1, both measured as necessary:
//  - the evidence moves into the DATA: each column's stacked fragments arrive already composed,
//    so the "fragments compose top to bottom" paragraph is not needed at all;
//  - the scaffold is a COMPLETION the model must finish before the list, not a suggestion.
function ProposeHeaderRowRolesLean2(table: string, n_rows: int) -> HeaderRowRole[] {
  client Claude
  prompt #"
    Header rows r0..r{{ n_rows - 1 }} sit above a table's column labels. Per column, the stack
    top-to-bottom and the name it would compose:

    {{ table }}

    A row is C if its fragments make the composed names read as ONE natural column name,
    L if it names a group whose sub-columns are the labels below, F if it is not table content
    (col -1 = outside every column). F discards text: last resort.

    Complete these lines first, max 10 words each:
    {% for i in range(n_rows) %}r{{ i }}: composed names read as ... so ...
    {% endfor %}
    {{ ctx.output_format(prefix="Only then, the list of codes, one per row:\n") }}
  "#
}
