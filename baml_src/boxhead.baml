// "Which column does each header word head?" — the boxhead of a data grid.
//
// `datagrid.py` derives a table's ENTRIES and, by design, no header (R71: reading the header first
// is circular). So an adopted grid asserts cells with coordinates and no column identity — on ons
// p7/p8, 552 cells and 0 column labels, with every one of the document's 175 escalated tokens
// being header metadata nobody reads. Measured 2026-09-18 (`scripts/grid_boxhead_spike.py`): the
// refused lines directly above the grid's first row label nearly every column on all 16
// grid-deriving pages of the corpus, and 23% of their words CROSS a column boundary — spanners,
// titles, wide labels. Leaf label vs spanner vs title is a reading judgement, and the one
// geometric attempt (strict containment) already misfiles a line on the page that suggested it.
//
// THE OUTPUT IS ADDRESSES, NEVER TEXT (the RF8 rule `unshown_ink.baml` states): a header word is
// named by (line, word) in the numbered listing supplied, so the answer cannot carry a value that
// is on the page and cannot invent a label. The disposal — `boxhead.dispose_boxhead` — checks
// every address arithmetically and every leaf placement against the grid's own column intervals.

class HeaderWordAddress {
  line int @description("the L-number of the line in the numbered listing")
  word int @description("the [index] of the word within that line")
}

class ColumnLabel {
  col int @description("0-based index of the ONE column this label heads, counting row-label columns too, left to right")
  words HeaderWordAddress[] @description("every word of that column's label, across all its lines, top to bottom")
}

class SpanningLabel {
  first_col int @description("leftmost data column the spanning label covers")
  last_col int @description("rightmost data column the spanning label covers")
  words HeaderWordAddress[]
}

class BoxheadReading {
  refuses_grid bool @description("true if the table you see does NOT have the stated number of data columns — then leave every list empty and say why in note")
  cols_you_see int @description("how many data columns you actually see; 0 if you are not refusing")
  leaf_labels ColumnLabel[] @description("one entry per data column that has a header of its own")
  spanning_labels SpanningLabel[] @description("labels that sit over SEVERAL columns at once")
  other_words HeaderWordAddress[] @description("every listed word that is NOT a column header: titles, captions, units, footnote marks")
  note string @description("one short sentence on how you read the header; NEVER any text or value from the page")
}

function ReadBoxhead(page: image, ncols: int, listing: string) -> BoxheadReading {
  client ClaudeLongAnswer
  prompt #"
    {{ _.role("user") }}
    {{ page }}

    The image shows the top of one table: its header area, then its first rows of data. The
    table has {{ ncols }} columns IN ALL, numbered from 0 at the left — and that count INCLUDES
    the leftmost column(s) of row labels (dates, names, categories) as well as the columns of
    figures. So if the rows begin with a date or a name, that is column 0, not a header.

    Below is every word of the header area, line by line, each word with its index:

    {{ listing }}

    READ THE HEADER AS A PERSON READS A TABLE, and sort every listed word into exactly one place:

    - leaf_labels: a label that heads ONE data column. A label often wraps over several lines —
      collect all of its words, top to bottom, under that one column.
    - spanning_labels: a label that sits over SEVERAL columns at once and groups them.
    - other_words: everything that is not a column header — the table's title, a caption, a
      unit line, a footnote mark.

    EVERY listed word must appear exactly once across the three lists. Leaving a word out, or
    using one twice, makes the whole answer unusable.

    If the table you see does not have {{ ncols }} columns counted that way, set refuses_grid to true, put
    the number you see in cols_you_see, and leave the lists empty. Refusing is a correct answer.

    Answer with addresses only. Never write any text, number or value that appears on the page —
    not in note, not anywhere.
    {{ ctx.output_format }}
  "#
}
