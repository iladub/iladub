// R213 — "which cells of this table appear EMPTY to you?"
//
// The repo's first image-input BAML function, built for this one question and factored for no
// second caller (spec 2026-09-17 § 6). The decidable fact is not a colour distance: it is a
// DISAGREEMENT between two independent readings of one cell (§ 4.1).
//
//   the text layer says | a reader of the rendered page says | the cell is
//   a glyph is here     | a mark is here                     | ordinary ink
//   a glyph is here     | NO mark                            | tab:UnshownInk
//   no glyph            | no mark                            | tab:Blank (unchanged)
//   no glyph            | a mark                             | out of scope — flag, do not type
//
// This function supplies ONLY the second column. The disagreement is an AXIOM over the two
// evidence sets, open-world and evidence-positive: both readings must be PRESENT for a cell to
// type tab:UnshownInk, so a missing or refused answer types nothing.
//
// THE OUTPUT SHAPE IS CLOSED AND CANNOT EXPRESS A VALUE ON THE PAGE (RF8). Addresses and
// abstentions only. Run 1 of the blind disposal returned the string "14,000" — a tonnage off the
// page — because the shape it was given allowed it to. Nothing here has a string field that
// could carry one.

class EmptyCellAddress {
  row int @description("0-based row index within the supplied grid, top to bottom")
  col int @description("0-based column index within the supplied grid, left to right")
}

class UnshownInkReading {
  refuses_grid bool @description("true if the grid dimensions you were given do NOT match the table you see — then leave empty_cells empty and say why in note")
  rows_you_see int @description("how many rows you actually see; 0 if you are not refusing")
  cols_you_see int @description("how many columns you actually see; 0 if you are not refusing")
  empty_cells EmptyCellAddress[] @description("every grid position where you see NOTHING at all — no digits, no letters, no dash, no mark of any kind")
  note string @description("one short sentence on how you read the table; NEVER any text, number or value that appears in it")
}

function ReadEmptyCells(page: image, nrows: int, ncols: int) -> UnshownInkReading {
  client ClaudeLongAnswer
  prompt #"
    {{ _.role("user") }}
    {{ page }}

    The image above shows one table. Treat it as a grid of {{ nrows }} rows and {{ ncols }}
    columns, numbered from 0: row 0 is the topmost row, column 0 is the leftmost column.

    LOOK AT THE PAGE AND TELL ME WHICH GRID POSITIONS APPEAR EMPTY TO YOU — positions where you
    look and see nothing at all: no digits, no letters, no dash, no mark of any kind.

    READ IT AS A PERSON READS A PAGE. Look at it once, at its normal size, the way you would
    glance at a printed table. Do NOT magnify it, do NOT adjust or stretch its contrast, do NOT
    sample or compare pixel values, and do NOT reason about colours or shades. If a mark is there
    but so faint that you would not notice it in ordinary reading, then for this question it is
    not there. The question is exactly "would a reader see something here?" and nothing else.

    A position covered by a cell that SPANS several rows or columns is not empty — you see that
    cell's content there. Report a position as empty only when the place itself shows nothing.

    If the table you see is not {{ nrows }} by {{ ncols }}, say so: set refuses_grid to true,
    put the dimensions you actually see in rows_you_see and cols_you_see, leave empty_cells
    empty, and explain in one sentence. Answering in a different grid than the one you were
    given would put every address in the wrong place, so refusing is the correct answer and
    never a failure.

    Never write any text, number or value that appears in the table — not in note, not anywhere.
    Report positions only.
    {{ ctx.output_format }}
  "#
}
