// LEAN variant of ProposeHeaderRowRoles. Same question, same typed answer.

// (1) A closed ENUM instead of free string[]: the model emits 1-char aliases, the parser
//     hands back HeaderRowRole.Continuation. @description lives ONCE, in the schema.
enum HeaderRowRole {
  Furniture    @alias("F") @description("not table content: title, report date, page no. LOSSY - last resort")
  Continuation @alias("C") @description("wrapped fragment; fragment + label below reads as ONE column name")
  Level        @alias("L") @description("group label; the labels below are its sub-columns")
}

// (2) The return type is the bare list. No wrapper class, no keys, no rationale-after-the-fact.
function ProposeHeaderRowRolesLean(table: string, n_rows: int) -> HeaderRowRole[] {
  client Claude
  prompt #"
    Header rows above a table's column labels. Classify each.
    Same geometry, only language separates C from L: "Date of Grain"+"Commencement" is one
    name (C); "Monday"+"Qty" is a group over a sub-column (L). col -1 = ink outside every column (F).

    {{ table }}

    {# (3) reasoning scaffold: the model completes the dots BEFORE it answers #}
    Think, max 8 words per row:
    {% for i in range(n_rows) %}- r{{ i }}: join reads as ... so ...
    {% endfor %}
    {{ ctx.output_format(prefix="Then answer, one code per row, as a list:\n") }}
  "#
}
