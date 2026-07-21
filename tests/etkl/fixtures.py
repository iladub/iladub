"""Synthetic PDFs with KNOWN geometry, for testing the deterministic engine.

reportlab draws at exact points from the page's bottom-left origin. pdfplumber
reports `top` from the page's TOP, so a string drawn at reportlab y maps to
pdfplumber top = page_height - y (minus font ascent, but tests use tolerances).
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = letter  # 612 x 792 points


def simple_table_pdf(path: str) -> dict:
    """A title band + a 3-column table (header row + 3 data rows).

    Returns the ground truth: column x-positions and row y-positions (reportlab
    coords), so tests can assert against known geometry.
    """
    cols = [72.0, 240.0, 400.0]           # left x of each column
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    c.drawString(72.0, PAGE_H - 72.0, "Complete Blood Count")   # title band
    rows = [
        ("Analyte", "Value", "Unit"),
        ("Hemoglobin", "13.2", "g/dL"),
        ("Hematocrit", "39.5", "%"),
        ("Platelets", "250", "x10^9/L"),
    ]
    y0 = PAGE_H - 130.0                     # table starts well below the title
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {
        "cols": cols,
        "n_body_rows": 3,
        "n_table_rows": 4,
        "title": "Complete Blood Count",
    }


# NOTE: this geometry is a faithful copy of demo/etkl_demo_data.py::pivoted_report_pdf,
# empirically verified (2026-07-05) to keep the merged parent header + sub-header +
# (SI) line + 5 body rows in ONE band, so the classifier sees the merged header and
# escalates. Do NOT change the spacing without re-verifying it stays a single band —
# if the body bands away from its header it could be misread as a clean record table.
def pivoted_table_pdf(path: str) -> dict:
    """A pivoted table: two merged, centered parent headers over leaf columns —
    the case the record-table slice must ESCALATE, not assert."""
    leaves = [(50.0, 150.0, "left"), (160.0, 215.0, "right"), (225.0, 280.0, "left"),
              (290.0, 335.0, "center"), (365.0, 420.0, "right"), (430.0, 485.0, "left"),
              (495.0, 545.0, "center")]
    parents = [("Current Visit", 1, 3), ("Prior Visit", 4, 6)]
    subs = ["Analyte", "Result", "Unit", "Flag", "Result", "Unit", "Flag"]
    body = [("Hemoglobin", "13.2", "g/dL", "LOW", "12.8", "g/dL", "LOW"),
            ("Hematocrit", "39.5", "%", "LOW", "38.1", "%", "LOW"),
            ("WBC", "7.8", "x10^9/L", "", "9.2", "x10^9/L", "HIGH"),
            ("Platelets", "252", "x10^9/L", "", "248", "x10^9/L", ""),
            ("MCV", "88.4", "fL", "", "87.9", "fL", "")]

    def place(c, text, left, right, align, y):
        if not text:
            return
        if align == "right":
            c.drawRightString(right, y, text)
        elif align == "center":
            c.drawCentredString((left + right) / 2.0, y, text)
        else:
            c.drawString(left, y, text)

    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 14)
    c.drawString(50.0, PAGE_H - 55.0, "SERIAL CBC")
    top = PAGE_H - 95.0
    c.setFont("Courier-Bold", 10)
    for label, i, j in parents:
        c.drawCentredString((leaves[i][0] + leaves[j][1]) / 2.0, top, label)
    for (l, r, align), name in zip(leaves, subs):
        place(c, name, l, r, "center" if name != "Analyte" else "left", top - 15.0)
    for idx in (1, 4):
        l, r, _ = leaves[idx]
        c.drawCentredString((l + r) / 2.0, top - 28.0, "(SI)")
    c.setFont("Courier", 10)
    for i, row in enumerate(body):
        y = top - 50.0 - i * 18.0
        for (l, r, align), cell in zip(leaves, row):
            place(c, cell, l, r, align, y)
    c.save()
    return {"n_leaf_cols": 7, "title": "SERIAL CBC"}


def record_and_pivot_pdf(path: str) -> dict:
    """One record table (top) + one pivot table (bottom) on a single page.

    The two tables are separated by a large vertical gap (~186 pt in pdfplumber
    coords) so detect_bands always assigns them to distinct bands.  The record
    table has no prose title so the page yields exactly two bands:
      Band 1 → RECORD_TABLE (asserted)
      Band 2 → UNSUPPORTED_TABLE (escalated)

    Verified empirically: the record rows are spaced 18 pt apart (gap ≈ 8 pt
    each); the pivot rows are spaced 15–18 pt apart (gaps ≈ 3–12 pt); the
    inter-table gap is ≈186 pt >> 1.8 × median_gap, so banding splits cleanly.
    Returns a truth dict with the record column positions.
    """
    # ── Record table (no title) ──────────────────────────────────────────────
    cols = [72.0, 240.0, 400.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rec_rows = [
        ("Analyte", "Value", "Unit"),
        ("Hemoglobin", "13.2", "g/dL"),
        ("Hematocrit", "39.5", "%"),
        ("Platelets", "250", "x10^9/L"),
    ]
    rec_y0 = PAGE_H - 100.0
    for i, row in enumerate(rec_rows):
        y = rec_y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)

    # ── Pivot table (no title) ───────────────────────────────────────────────
    # Adapted from pivoted_table_pdf — same merged-header structure, starts
    # far below the record table so the inter-band gap is >> 1.8 × median gap.
    piv_top = PAGE_H - 350.0            # pdfplumber top ≈ 350 for the parent-header line
    leaves = [(50.0, 150.0, "left"), (160.0, 215.0, "right"), (225.0, 280.0, "left"),
              (290.0, 335.0, "center"), (365.0, 420.0, "right"), (430.0, 485.0, "left"),
              (495.0, 545.0, "center")]
    parents = [("Current Visit", 1, 3), ("Prior Visit", 4, 6)]
    subs = ["Analyte", "Result", "Unit", "Flag", "Result", "Unit", "Flag"]
    body = [("Hemoglobin", "13.2", "g/dL", "LOW", "12.8", "g/dL", "LOW"),
            ("Hematocrit", "39.5", "%", "LOW", "38.1", "%", "LOW"),
            ("WBC", "7.8", "x10^9/L", "", "9.2", "x10^9/L", "HIGH"),
            ("Platelets", "252", "x10^9/L", "", "248", "x10^9/L", ""),
            ("MCV", "88.4", "fL", "", "87.9", "fL", "")]

    def place(c, text, left, right, align, y):
        if not text:
            return
        if align == "right":
            c.drawRightString(right, y, text)
        elif align == "center":
            c.drawCentredString((left + right) / 2.0, y, text)
        else:
            c.drawString(left, y, text)

    c.setFont("Courier-Bold", 10)
    for label, i, j in parents:
        c.drawCentredString((leaves[i][0] + leaves[j][1]) / 2.0, piv_top, label)
    for (l, r, align), name in zip(leaves, subs):
        place(c, name, l, r, "center" if name != "Analyte" else "left", piv_top - 15.0)
    for idx in (1, 4):
        l, r, _ = leaves[idx]
        c.drawCentredString((l + r) / 2.0, piv_top - 28.0, "(SI)")
    c.setFont("Courier", 10)
    for i, row in enumerate(body):
        y = piv_top - 50.0 - i * 18.0
        for (l, r, align), cell in zip(leaves, row):
            place(c, cell, l, r, align, y)

    c.save()
    return {"rec_cols": cols, "rec_n_body_rows": 3, "piv_n_leaf_cols": 7}


def verbose_header_table_pdf(path: str) -> dict:
    """A 3-column table whose FIRST row is a single merged/centered title with MORE
    word tokens than any data row (the old max-by-tokens code would mistake the
    title row for the tiling set and return ncols < 3). Layout:

      Row 0 (title):  "Quarterly Revenue Summary By Product Line"  (centred, spanning)
      Row 1 (labels): "Product"   "Q1"   "Q2"
      Rows 2-4 (data): one short word per column
    """
    cols = [72.0, 240.0, 400.0]          # left x of each of the 3 columns
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    # Title row — draw as a single centred string spanning all three columns so
    # pdfplumber sees it as one word cluster covering the full width.
    title = "Quarterly Revenue Summary By Product Line"
    span_centre = (cols[0] + cols[-1] + 200.0) / 2.0   # ≈ centre of the table
    y0 = PAGE_H - 130.0
    c.drawCentredString(span_centre, y0, title)
    # Leaf-label row (Row 1)
    labels = ("Product", "Q1", "Q2")
    y1 = y0 - 18.0
    for x, lbl in zip(cols, labels):
        c.drawString(x, y1, lbl)
    # Data rows (Rows 2-4)
    data = [("Alpha", "100", "120"),
            ("Beta",  "200", "210"),
            ("Gamma", "150", "160")]
    for i, row in enumerate(data):
        y = y1 - (i + 1) * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_leaf_cols": 3}


def wide_cell_table_pdf(path: str) -> dict:
    """A clean 3-col header, but one data value is wide enough to fill the
    gutter — collapses the profiled grid; must escalate the whole region."""
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    cols = [72.0, 240.0, 400.0]
    rows = [("Analyte", "Value", "Unit"),
            ("Hemoglobin", "13.2", "g/dL"),
            ("Note", "THIS_CELL_IS_FAR_TOO_WIDE_AND_FILLS_THE_GUTTER", "x")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols}


def all_text_table_pdf(path: str) -> dict:
    """A normal all-text record table: single-word headers, all-text body cells.

    No numeric values anywhere — the type-orientation oracle must not flag this
    as transposed (text is symmetric; both axes carry labels).  This fixture
    guards the conservative 'text is symmetric, never flagged' property.

    Layout:
      Region | Manager | Backup
      North  | Alice   | Bob
      South  | Carol   | Dave
      East   | Eve     | Frank
    """
    cols = [72.0, 240.0, 400.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [
        ("Region", "Manager", "Backup"),
        ("North", "Alice", "Bob"),
        ("South", "Carol", "Dave"),
        ("East", "Eve", "Frank"),
    ]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_body_rows": 3}


def false_transposed_pdf(path: str) -> dict:
    """Trips looks_transposed (the 'Count' row is all-numeric across cols, and NO
    column is all-numeric) yet is NOT a genuine transposition: the 'Mix' row is
    type-mixed (5 numeric, ok text), so transpose_is_coherent is False. Guards the
    compile-direction silent-wrong: a false-positive detection must ESCALATE, not
    compile an inverted RecordTable."""
    cols = [72.0, 240.0, 400.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Item", "A", "B"), ("Count", "10", "20"),
            ("Note", "hi", "bye"), ("Mix", "5", "ok")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols}


def transposed_table_pdf(path: str) -> dict:
    """A TRANSPOSED table: field names run down the first column, each other column
    is a record. The 'Age' row is all-numeric ACROSS the record columns, while no
    column is all-numeric — the transposition signature."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 11)
    rows = [("Name", "Alice", "Bob"), ("Age", "30", "25"), ("City", "NYC", "LA")]
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 20.0
        for x, cell in zip((80.0, 240.0, 400.0), row):
            c.drawString(x, y, cell)
    c.save()
    return {"n_cols": 3, "n_rows": 3}


def row_grouped_table_pdf(path: str) -> dict:
    """A ROW-header hierarchy: 'Region' groups (North/South) run DOWN the first stub
    column via the blank-below (forward-fill) encoding; 'Metric' is a fully-populated
    finer stub; 'Value' is the numeric data column. North spans Revenue/Cost/Margin;
    South spans Revenue/Cost. Today this flattens to a RecordTable; the loop compiles
    the row-header tree."""
    cols = [72.0, 200.0, 360.0]           # Region, Metric, Value
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Region", "Metric", "Value"),
            ("North", "Revenue", "100"),
            ("", "Cost", "60"),
            ("", "Margin", "40"),
            ("South", "Revenue", "120"),
            ("", "Cost", "70")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            if cell:
                c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_leaf_rows": 5, "n_data_cols": 1,
            "groups": {"North": 3, "South": 2}}


def single_stub_blank_pdf(path: str) -> dict:
    """One stub column ('Region') with blank-below, but NO fully-populated finer stub
    column — just Region + Value(numeric). The sub-rows have no identity, so this must
    NOT be detected as row-grouped (leaf rows unidentifiable)."""
    cols = [72.0, 300.0]                   # Region, Value
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Region", "Value"), ("North", "100"), ("", "60"), ("South", "120")]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            if cell:
                c.drawString(x, y, cell)
    c.save()
    return {"cols": cols}


def crosstab_table_pdf(path: str) -> dict:
    """A cross-tab: hierarchical COLUMN header (Q1/Q2 each over Rev/Cost/Unit) + a
    flat stub ROW axis (North/South) + a numeric data matrix. Short column-group
    labels over wide numeric groups — the case Loop 2's text-extent span recovery
    under-covers and proximity handles. Blank corner (the stub has no header)."""
    stub_x = 55.0
    data_x = [140.0, 210.0, 280.0, 380.0, 450.0, 520.0]   # Q1:Rev,Cost,Unit | Q2:Rev,Cost,Unit
    top = PAGE_H - 90.0
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 9)
    c.drawCentredString((data_x[0] + data_x[2]) / 2.0, top, "Q1")
    c.drawCentredString((data_x[3] + data_x[5]) / 2.0, top, "Q2")
    for x, name in zip(data_x, ["Rev", "Cost", "Unit", "Rev", "Cost", "Unit"]):
        c.drawCentredString(x, top - 13.0, name)
    c.setFont("Courier", 9)
    body = [("North", ["100", "60", "5", "110", "65", "6"]),
            ("South", ["120", "70", "7", "130", "75", "8"])]
    for i, (lbl, vals) in enumerate(body):
        y = top - 30.0 - i * 16.0
        c.drawString(stub_x, y, lbl)
        for x, v in zip(data_x, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"n_data_cols": 6, "n_leaf_rows": 2,
            "col_groups": {"Q1": [1, 2, 3], "Q2": [4, 5, 6]},
            "row_axis": ["North", "South"]}


def side_by_side_pdf(path: str) -> dict:
    """Two independent record tables abreast, separated by a wide full-height gutter.
    detect_bands (1-D) fuses them into one wide table today; segment must split them."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    left = [(72.0, "Analyte"), (150.0, "Value")]
    right = [(330.0, "Item"), (410.0, "Qty")]
    lrows = [("Analyte", "Value"), ("Hb", "13.2"), ("WBC", "7.8")]
    rrows = [("Item", "Qty"), ("Apple", "10"), ("Pear", "5")]
    for i, (lr, rr) in enumerate(zip(lrows, rrows)):
        y = PAGE_H - 120.0 - i * 18.0
        for (x, _), v in zip(left, lr):
            c.drawString(x, y, v)
        for (x, _), v in zip(right, rr):
            c.drawString(x, y, v)
    c.save()
    return {"left_header": ["Analyte", "Value"], "right_header": ["Item", "Qty"]}


def stacked_repeated_header_pdf(path: str) -> dict:
    """Two record tables stacked with NO vertical gap; the second table repeats the
    header row. detect_bands keeps them one band; segment must split at the repeat."""
    cols = [72.0, 240.0, 400.0]
    rows = [("Analyte", "Value", "Unit"), ("Hb", "13.2", "g/dL"), ("WBC", "7.8", "x10^9"),
            ("Analyte", "Value", "Unit"), ("Ca", "9.5", "mg/dL"), ("Na", "140", "mmol/L")]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            c.drawString(x, y, v)
    c.save()
    return {"header": ["Analyte", "Value", "Unit"], "repeat_at": 3}


def record_plus_stub_hier_pdf(path: str) -> dict:
    """A record table (left) beside a table with its OWN stub but a MULTI-WORD /
    non-record header (right) — a genuine second table that is not two clean records.
    Used for the MULTI_TABLE_AMBIGUOUS escalation (has_own_stub right = True, but the
    pair is not both-RECORD)."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 9)
    for i, (a, v) in enumerate([("Analyte", "Value"), ("Hb", "13"), ("WBC", "8")]):
        y = PAGE_H - 120.0 - i * 16.0
        c.drawString(72.0, y, a); c.drawString(150.0, y, v)
    # right: a merged/2-level header over its own 'Dept' stub -> classifies UNSUPPORTED
    c.setFont("Courier-Bold", 9)
    c.drawCentredString((430.0 + 500.0) / 2.0, PAGE_H - 116.0, "Metrics")   # merged parent (row 0)
    c.setFont("Courier", 9)
    for i, row in enumerate([("Dept", "M1", "M2"), ("Sales", "10", "20"), ("Ops", "30", "40")]):
        y = PAGE_H - 132.0 - i * 16.0
        for x, v in zip([340.0, 430.0, 500.0], row):
            c.drawString(x, y, v)
    c.save()
    return {"right_stub": "Dept"}


def uniform_wide_record_pdf(path: str) -> dict:
    """A single 4-column record table with roughly uniform column spacing.

    Layout:
      Name    | Age | City  | Country
      Alice   | 30  | NYC   | USA
      Bob     | 25  | LA    | UK
      Charlie | 35  | Paris | France

    Columns at x = 72, 200, 330, 460. The three inter-column gutters are all
    roughly equal (~84–112 pt), so the widest-to-second-widest ratio is ≈1.1–1.3
    — well below the _GUTTER_DOMINANCE threshold of 2.0.

    Guards the gap-dominance fix: this table must NEVER be split and must NOT
    be escalated as MULTI_TABLE_AMBIGUOUS.
    """
    cols = [72.0, 200.0, 330.0, 460.0]     # Name, Age, City, Country
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [
        ("Name",    "Age", "City",  "Country"),
        ("Alice",   "30",  "NYC",   "USA"),
        ("Bob",     "25",  "LA",    "UK"),
        ("Charlie", "35",  "Paris", "France"),
    ]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_body_rows": 3}


def row_hierarchy_wide_pdf(path: str) -> dict:
    """A ROW-header hierarchy with TWO numeric data columns (Headcount + Budget).

    Layout:
      Region | Team  | Headcount | Budget
      North  | Alpha |        10 |    100
             | Beta  |        20 |    200
      South  | Gamma |        30 |    300
             | Delta |        40 |    400

    'Region' uses blank-below (forward-fill) grouping; 'Team' is the fully-populated
    finer stub; 'Headcount' and 'Budget' are the two numeric data columns.

    This is the 2-data-column variant of row_grouped_table_pdf. The widest gutter falls
    between Team (last stub column) and Headcount (first data column). The right half
    is all-numeric, so has_own_stub(right) is False — find_table_gutter must NOT split
    it. Guards the fix for the false-positive gutter cut on row-hierarchy tables.
    """
    cols = [72.0, 180.0, 300.0, 420.0]    # Region, Team, Headcount, Budget
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [
        ("Region", "Team",  "Headcount", "Budget"),
        ("North",  "Alpha", "10",        "100"),
        ("",       "Beta",  "20",        "200"),
        ("South",  "Gamma", "30",        "300"),
        ("",       "Delta", "40",        "400"),
    ]
    y0 = PAGE_H - 130.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            if cell:
                c.drawString(x, y, cell)
    c.save()
    return {"cols": cols, "n_leaf_rows": 4, "n_data_cols": 2,
            "groups": {"North": 2, "South": 2}}


def totals_table_pdf(path: str) -> dict:
    """Region x Quarter with a Total column (Q1+Q2) and a Total row (North+South)."""
    cols = [72.0, 200.0, 300.0, 400.0]
    rows = [("Region", "Q1", "Q2", "Total"), ("North", "100", "110", "210"),
            ("South", "120", "130", "250"), ("Total", "220", "240", "460")]
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            c.drawString(x, y, v)
    c.save()
    return {"grand_total": 460}


def subtotals_row_group_pdf(path: str) -> dict:
    """Row-grouped (Region: North/South) with a per-group Total row = sum of members."""
    cols = [60.0, 180.0, 320.0, 430.0]
    rows = [("Region", "Dept", "H1", "H2"),
            ("North", "Sales", "10", "5"), ("", "Ops", "20", "7"), ("", "Total", "30", "12"),
            ("South", "Sales", "15", "8"), ("", "Ops", "25", "9"), ("", "Total", "40", "17")]
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            if v:
                c.drawString(x, y, v)
    c.save()
    return {"groups": {"North": 30, "South": 40}}


def no_aggregation_pdf(path: str) -> dict:
    """A record table whose values have NO arithmetic relationship (guard fixture)."""
    cols = [72.0, 200.0, 320.0]
    rows = [("Item", "A", "B"), ("P", "3", "7"), ("Q", "9", "1"), ("R", "4", "8")]
    c = canvas.Canvas(str(path), pagesize=letter); c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = PAGE_H - 120.0 - i * 18.0
        for x, v in zip(cols, row):
            c.drawString(x, y, v)
    c.save()
    return {}


def region_pivot_pdf(path: str) -> dict:
    """A single spanning parent 'Region' over four WIDE numeric leaf columns
    (North/South/East/West) + a 'Year' stub. The short 'Region' label under-covers
    its span under text-extent recovery; repair_coverage must extend it to all four."""
    leaves = [150.0, 250.0, 350.0, 450.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString((leaves[0] + leaves[3]) / 2.0, PAGE_H - 90.0, "Region")
    for x, n in zip(leaves, ["North", "South", "East", "West"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(60.0, PAGE_H - 104.0, "Year")
    c.setFont("Courier", 10)
    for i, (yr, vals) in enumerate([("2020", ["10", "20", "30", "40"]),
                                    ("2021", ["11", "21", "31", "41"])]):
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(60.0, y, yr)
        for x, v in zip(leaves, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"parent": "Region", "values": ["North", "South", "East", "West"], "stub": "Year"}


def partial_merge_report_pdf(path: str) -> dict:
    """A partial merge: a 'WIDE' parent CENTERED over three leaf columns (Val,Unit,Flag)
    beside a standalone fourth column 'Note' that has NO parent group. WIDE's ink
    center (x=250) is the midpoint of cols 1-3, NOT of cols 1-4 (x=300). The
    centering convention therefore reads WIDE=[1,2,3] with col 4 a parentless leaf;
    the pre-B1.1 greedy repair wrongly folds col 4 under WIDE ([1,2,3,4])."""
    leaves = [150.0, 250.0, 350.0, 450.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString((leaves[0] + leaves[2]) / 2.0, PAGE_H - 90.0, "WIDE")  # center=250 over cols 1-3
    for x, n in zip(leaves, ["Val", "Unit", "Flag", "Note"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(60.0, PAGE_H - 104.0, "Key")
    c.setFont("Courier", 10)
    for i, (k, vals) in enumerate([("R1", ["10", "mg", "LOW", "ok"]), ("R2", ["50", "kg", "HIGH", "no"])]):
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(60.0, y, k)
        for x, v in zip(leaves, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"parent": "WIDE", "parent_cols": [1, 2, 3], "standalone_col": 4,
            "leaves": ["Val", "Unit", "Flag", "Note"], "stub": "Key"}


def unequal_width_merge_report_pdf(path: str) -> dict:
    """A merged 'GROUP' centered over THREE UNEQUAL-WIDTH columns (col 1 narrow & close,
    col 3 wide & far) — the geometry where a median-of-midpoints centering statistic
    silently resolves GROUP to [2,3], dropping col 1. Correct: GROUP spans all three
    ([1,2,3]) by endpoint-center, or the region escalates — never a column-dropping subset.
    Mixed-type body so it routes the hierarchical path."""
    xs = [120.0, 170.0, 330.0]                                   # unequal spacing -> unequal widths
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString((xs[0] + xs[2]) / 2.0, PAGE_H - 90.0, "GROUP")   # visual center of the 3-col span
    for x, n in zip(xs, ["V", "U", "D"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(55.0, PAGE_H - 104.0, "Key")
    c.setFont("Courier", 10)
    for i, (k, vals) in enumerate([("R1", ["1", "aa", "xx"]), ("R2", ["2", "bb", "yy"])]):
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(55.0, y, k)
        for x, v in zip(xs, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"parent": "GROUP", "data_cols": [1, 2, 3]}


def _tight_table(path, ruled):
    """5 tight columns (~2pt gutters). `ruled` draws vertical separators (canvas.line)."""
    cols = [(60, 120), (122, 175), (177, 230), (232, 285), (287, 340)]
    headers = ["Product", "Q1", "Q2", "Q3", "Q4"]
    rows = [("Alpha", "120", "135", "150", "160"), ("Beta", "90", "95", "100", "110"),
            ("Gamma", "45", "50", "55", "60"), ("Delta", "200", "210", "220", "240"),
            ("Epsilon", "30", "35", "40", "45"), ("Zeta", "75", "80", "85", "90")]
    c = canvas.Canvas(str(path), pagesize=letter)
    top = PAGE_H - 90.0
    rh = 20.0
    tbl_bottom = top - (len(rows) + 1) * rh
    if ruled:
        c.setLineWidth(0.7)
        for (l, r) in cols:
            c.line(l - 2, top + 12, l - 2, tbl_bottom)        # vertical separators
        c.line(cols[-1][1] + 2, top + 12, cols[-1][1] + 2, tbl_bottom)
    c.setFont("Helvetica-Bold", 9)
    for (l, r), h in zip(cols, headers):
        c.drawString(l, top, h)
    c.setFont("Helvetica", 9)
    for i, row in enumerate(rows):
        y = top - (i + 1) * rh
        for (l, r), cell in zip(cols, row):
            c.drawString(l, y, cell)
    c.save()
    # true separator x's (canvas.line x = col_left-2 ; last = col_right+2)
    return {"n_leaf_cols": 5, "rule_xs": [cols[0][0] - 2] + [l - 2 for (l, r) in cols[1:]] + [cols[-1][1] + 2]}


def ruled_tight_table_pdf(path: str) -> dict:
    return _tight_table(path, ruled=True)


def borderless_tight_table_pdf(path: str) -> dict:
    return _tight_table(path, ruled=False)


def _merged_table(path, ruled):
    """5 columns packed so tightly (Courier, ~40pt cells, values nearly filling) that pdfplumber
    MERGES adjacent cell texts into one word. `ruled` draws separators at the cell edges — the only
    way to recover the true 5-cell structure (rule-aware char re-extraction)."""
    edges = [60.0, 100.0, 140.0, 180.0, 220.0, 260.0]     # 5 cells, 40pt each; rules at edges
    heads = ["Product", "Revenue", "Expense", "Margin", "Growth"]
    rows = [("Alpha", "123456", "98765", "24691", "12.30%"), ("Beta", "234567", "187654", "46913", "19.80%"),
            ("Gamma", "345678", "298543", "47135", "15.70%"), ("Delta", "456789", "387654", "69135", "17.90%"),
            ("Epsln", "567890", "487123", "80767", "16.60%"), ("Zeta", "678901", "587432", "91469", "15.50%")]
    c = canvas.Canvas(str(path), pagesize=letter)
    top = PAGE_H - 90.0
    rh = 16.0
    tbl_bottom = top - (len(rows) + 1) * rh
    if ruled:
        c.setLineWidth(0.7)
        for e in edges:
            c.line(e, top + 11, e, tbl_bottom)
    c.setFont("Courier-Bold", 9)
    for j, h in enumerate(heads):
        c.drawString(edges[j] + 1, top, h)
    c.setFont("Courier", 9)
    for i, row in enumerate(rows):
        y = top - (i + 1) * rh
        for j, cell in enumerate(row):
            c.drawString(edges[j] + 1, y, cell)
    c.save()
    return {"n_leaf_cols": 5, "rule_xs": edges, "headers": heads}


def ruled_merged_table_pdf(path: str) -> dict:
    return _merged_table(path, ruled=True)


def borderless_merged_table_pdf(path: str) -> dict:
    return _merged_table(path, ruled=False)


def offcenter_merge_report_pdf(path: str) -> dict:
    """Ambiguous merge: two SHORT parent labels 'LEFT' (center x=200) and 'RIGHT'
    (center x=300) whose centering claims collide — the centering resolver gives them
    OVERLAPPING spans (LEFT->[1,2,3], RIGHT->[2,3,4]), so no clean tiling exists.
    B1.1 must ESCALATE MERGE_AMBIGUOUS rather than assert an overlapping/arbitrary tiling.

    MIXED-TYPE body (Val numeric; Unit/Flag/Note text) so it routes the HIERARCHICAL
    path (where merge_tiling_ok gates). Controller-verified: this geometry yields
    merge_tiling_ok()==False via the per-level overlap check. (An all-numeric body would
    route matrix.py Voronoi and never reach the oracle.)"""
    leaves = [150.0, 250.0, 350.0, 450.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 10)
    c.drawCentredString(200.0, PAGE_H - 90.0, "LEFT")    # center 200 (midpoint of cols 1-2)
    c.drawCentredString(300.0, PAGE_H - 90.0, "RIGHT")   # center 300 (midpoint of cols 1-4) -> claims collide
    for x, n in zip(leaves, ["Val", "Unit", "Flag", "Note"]):
        c.drawCentredString(x, PAGE_H - 104.0, n)
    c.drawString(60.0, PAGE_H - 104.0, "Key")
    c.setFont("Courier", 10)
    for i, (k, vals) in enumerate([("R1", ["10", "mg", "LOW", "ok"]),
                                   ("R2", ["50", "kg", "HIGH", "no"])]):  # mixed -> hierarchical path
        y = PAGE_H - 122.0 - i * 16.0
        c.drawString(60.0, y, k)
        for x, v in zip(leaves, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"labels": ["LEFT", "RIGHT"], "expect": "MERGE_AMBIGUOUS"}
