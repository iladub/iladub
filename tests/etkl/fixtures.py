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


def offer_table_pdf(path):
    """A 4-column organ-offer record table (Organ/LVEF/ABO/COD) with two donor rows. Row 2 uses
    'Liver' (in scheme-organ); single-token cells, wide gaps -> compiles RECORD_TABLE. For the
    concept-feed end-to-end (raw-doc→grounded-graph)."""
    cols = [72.0, 200.0, 320.0, 440.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Organ", "LVEF", "ABO", "COD"),
            ("Heart", "60", "O", "MVA"),
            ("Liver", "55", "A", "CVA")]
    y0 = PAGE_H - 100.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return path


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


def _all_text_hier(path, ruled):
    """All-TEXT hierarchical table: 'Contact' spans Email+Phone; text body. `ruled` draws a
    horizontal rule under the header (the only header/body signal, since no column is non-Text)."""
    leaves = [(60.0, 150.0), (170.0, 320.0), (340.0, 470.0)]
    c = canvas.Canvas(str(path), pagesize=letter)
    top = PAGE_H - 90.0
    rh = 18.0
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, top, "Name")
    c.drawCentredString((170 + 470) / 2.0, top, "Contact")          # spanning parent (text)
    c.drawString(170, top - 14, "Email")
    c.drawString(340, top - 14, "Phone")
    if ruled:
        c.setLineWidth(0.7)
        c.line(55, top - 18, 480, top - 18)                         # horizontal rule under header
    rows = [("Alice", "alice@x.com", "555-0101"), ("Bob", "bob@y.org", "555-0102"),
            ("Carol", "carol@z.net", "555-0103"), ("Dave", "dave@w.io", "555-0104"),
            ("Eve", "eve@v.co", "555-0105"), ("Frank", "frank@u.dev", "555-0106")]
    c.setFont("Helvetica", 10)
    for i, row in enumerate(rows):
        y = top - 28 - i * rh
        for (l, r), cell in zip(leaves, row):
            c.drawString(l, y, cell)
    c.save()
    return {"n_leaf_cols": 3}


def all_text_hier_ruled_pdf(path: str) -> dict:
    return _all_text_hier(path, ruled=True)


def all_text_hier_borderless_pdf(path: str) -> dict:
    return _all_text_hier(path, ruled=False)


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


def caption_wrap_report_pdf(path: str) -> dict:
    """Loop C fixture: a leaked date CAPTION row + a wrap-CONTINUATION row, over a clean
    4-column leaf table (Item/Ref/Qty/Cost) — the real-PDF analogue of
    test_rowrole_reading.caption_and_wrap_band. UNIFORM 18pt line spacing throughout
    (header leading == body leading) so group_wrapped's adaptive wrap-continuation gap
    cannot absorb 'Unit' into the leaf row — the exact condition loop C exists for
    (headers.header_rows_of's KNOWN LIMIT).

    Row 0 (caption):      'Monday' + '05May2026', two centered words whose symmetrized
                           column-spans OVERLAP at column 1 (Ref) — the same level-0
                           overlap mechanism as offcenter_merge_report_pdf, so
                           merge_tiling_ok is False and the region reaches the NEURAL
                           slice. Geometry is empirically verified (see
                           tests/etkl/test_rowrole_integration.py) to route
                           UNSUPPORTED_TABLE -> classify_hierarchical (a HierRegion) with
                           a non-tiling tree.
    Row 1 (wrap):          'Unit', centered over the Ref column only — a wrap fragment
                           that, read as a 'continuation', merges onto 'Ref' -> 'Unit Ref'.
    Row 2 (leaf labels):   Item | Ref | Qty | Cost.
    Rows 3-4 (body):       text/text/numeric/text, so header_body_split resolves (Qty
                           is the sole homogeneous-numeric data column) while Cost stays
                           Text — breaking the clean stub|data suffix so the region does
                           NOT reach is_matrix_candidate (mirrors offcenter's mixed-type
                           body routing the hierarchical, not matrix, path).

    Coordinates are load-bearing — do not change them without re-verifying (via
    tests/etkl/test_rowrole_integration.py) that the no-proposer case still escalates
    MERGE_AMBIGUOUS and the with-proposer(furniture, continuation) case still asserts.
    """
    cols = [72.0, 200.0, 330.0, 460.0]           # Item, Ref, Qty, Cost
    c = canvas.Canvas(str(path), pagesize=letter)
    top = PAGE_H - 90.0
    rh = 18.0                                     # uniform leading, header == body
    c.setFont("Courier-Bold", 10)
    c.drawCentredString(240.0, top, "Monday")
    c.drawCentredString(300.0, top, "05May2026")
    c.drawCentredString(cols[1] + 15.0, top - rh, "Unit")
    c.setFont("Courier", 10)
    for x, lbl in zip(cols, ["Item", "Ref", "Qty", "Cost"]):
        c.drawString(x, top - 2 * rh, lbl)
    body = [("aa", "R1", "10", "ok"), ("bb", "R2", "20", "no")]
    for i, row in enumerate(body):
        y = top - (3 + i) * rh
        for x, v in zip(cols, row):
            c.drawString(x, y, v)
    c.save()
    return {"cols": cols, "caption": ["Monday", "05May2026"], "wrap": "Unit",
            "merged_label": "Unit Ref", "leaf_labels": ["Item", "Ref", "Qty", "Cost"]}


def stacked_banner_ruled_pdf(path: str, block_rule: bool = True) -> dict:
    """LOOP L FIXTURE — a RULED table whose header is a STACK: a banner line drawn over
    the ruled grid, two wrap-continuation lines, then the 1:1 leaf header line.

    Five ruled columns (rules at 40/110/180/250/320/390). Line by line:
      line 0  'Monday-03-August-Rpt' centred at x=180, ABOVE a full-width horizontal rule
              that crosses every interior ruled boundary. That rule is the author's own
              header-block boundary, and it is the ONLY reason this line reads as furniture
              (review round 1: reaching 'furniture' by elimination — "ink addressed to no
              column" — cannot tell a leaked date line from a short merged parent, so the
              law now demands this mark). Remove the rule and the line correctly falls back
              to `level`, i.e. the region escalates: see
              test_banner_without_block_rule_is_not_demoted.
      lines 1-2  'Total' / 'Grain' drawn at EXACTLY the x of the leaf label below them
              (112 and 252) — strictly inside one ruled column AND sharing that column's
              leaf-label alignment origin, which is what makes them wrap-continuation
              fragments ('Total Grain Tonnes'). The shared origin is load-bearing: it is
              the renderer's own cell layout, and it is the whole evidence for the role.
      line 3  'Port' 'Tonnes' 'Ship' 'Tonnes' 'Ship' — one label strictly inside each of
              the five ruled columns: the LEAF header, aligned 1:1.
      lines 4+  twenty body rows; columns 1 and 3 numeric, 0/2/4 text (so the region routes
              the HIERARCHICAL path, not matrix.py's all-numeric-suffix pivot path).

    Measured while writing this fixture (2026-08-02): under the pre-loop-L reading every
    header line is a header LEVEL, the resulting tree does not tile, and the region
    escalates REGION_TILING_FAILED with score 0.0.

    The body has TWENTY rows on purpose: compile.py scores a hierarchical region as
    asserted_body_tokens / all_band_tokens, so the header region's own tokens count
    against the ratio; a four-row body scores 20/31 = 0.65 for a PERFECTLY compiled
    table. Twenty rows (100/111 = 0.90) puts a correct reading above the 0.9 floor,
    matching the row-count regime of the real reports this law is for.

    `block_rule=False` omits the header-block rule, leaving the banner unevidenced — the
    honest-refusal variant.
    """
    edges = [40.0, 110.0, 180.0, 250.0, 320.0, 390.0]
    xs = [42.0, 112.0, 182.0, 252.0, 322.0]
    n_body = 20
    rh = 14.0
    top = 40.0 + (3 + n_body) * rh
    c = canvas.Canvas(str(path), pagesize=(430.0, top + 30.0))
    c.setFont("Courier-Bold", 10)
    c.drawCentredString(180.0, top, "Monday-03-August-Rpt")          # the banner
    c.setFont("Courier-Bold", 8)
    for x in (112.0, 252.0):
        c.drawString(x, top - rh, "Total")                            # wrap fragment 1
    for x in (112.0, 252.0):
        c.drawString(x, top - 2 * rh, "Grain")                        # wrap fragment 2
    for x, t in zip(xs, ["Port", "Tonnes", "Ship", "Tonnes", "Ship"]):
        c.drawString(x, top - 3 * rh, t)                              # the leaf header
    c.setFont("Courier", 8)
    ports = ["Mackay", "Gladstone", "Newcastle", "Portland"]
    for i in range(n_body):
        row = (ports[i % len(ports)], str(1000 + 50 * i), "V%02d" % i,
               str(2000 + 40 * i), "W%02d" % i)
        for x, t in zip(xs, row):
            c.drawString(x, top - (4 + i) * rh, t)
    c.setLineWidth(0.5)
    for e in edges:
        c.line(e, top - (4 + n_body) * rh - 4, e, top + 10)
    if block_rule:
        # THE HEADER-BLOCK RULE: spans every interior ruled boundary, between the banner
        # and the first wrap row — the author's "the header block starts below here".
        c.line(edges[0] - 2.0, top - 0.4 * rh, edges[-1] + 2.0, top - 0.4 * rh)
    c.save()
    return {"rule_xs": edges, "n_leaf_cols": 5, "banner": "Monday-03-August-Rpt",
            "leaf_labels": ["Port", "Tonnes", "Ship", "Tonnes", "Ship"],
            "merged_labels": ["Total Grain Tonnes"], "n_body_rows": n_body,
            "has_block_rule": block_rule}


def spanner_with_space_ruled_pdf(path: str, chop_mid_word: bool = False) -> dict:
    """LOOP L ADVERSARIAL FIXTURE (review finding F1/F8) — a ruled table with a GENUINE
    merged parent label above the leaf header, and NO header-block rule.

    'Arrivals Total' is centred over ruled columns 0-1. There is nothing in the document
    that says it is furniture, and nothing that says it continues either column's label
    (it shares neither leaf label's alignment origin), so the law MUST leave it at `level`
    — its pre-loop-L reading — and the region must escalate rather than assert a reading
    in which a real group label is demoted to a caption or welded onto a leaf.

    Two variants, because the two ways `rule_aware_lines` can cut the label were both shown
    to defeat the first version of the law:
      chop_mid_word=True   the rule falls INSIDE a word, so the two chopped cells sit flush
                           against the boundary from both sides.
      chop_mid_word=False  the rule falls in the label's internal SPACE, so the two cells
                           are separated exactly as a leaked two-word date line would be —
                           geometrically indistinguishable from furniture.
    Expected outcome for BOTH: NO derivation (all roles `level`) and an escalated region.
    """
    edges = [40.0, 110.0, 180.0, 250.0, 320.0]
    xs = [42.0, 112.0, 182.0, 252.0]
    n_body = 20
    rh = 14.0
    top = 40.0 + (2 + n_body) * rh
    c = canvas.Canvas(str(path), pagesize=(360.0, top + 30.0))
    c.setFont("Courier-Bold", 10)
    # Courier is monospaced at 0.6 em: 'Arrivals Total' is 14 chars = 84 pt wide. Centring
    # it at 110 (the rule) puts the rule mid-word; centring at 128 puts the SPACE there.
    c.drawCentredString(110.0 if chop_mid_word else 128.0, top, "Arrivals Total")
    c.setFont("Courier-Bold", 8)
    for x, t in zip(xs, ["Port", "Tonnes", "Ship", "Berth"]):
        c.drawString(x, top - rh, t)
    c.setFont("Courier", 8)
    for i in range(n_body):
        for x, t in zip(xs, ("Mackay", str(1000 + 50 * i), "V%02d" % i, "B%02d" % i)):
            c.drawString(x, top - (2 + i) * rh, t)
    c.setLineWidth(0.5)
    for e in edges:
        c.line(e, top - (2 + n_body) * rh - 4, e, top + 10)
    c.save()
    return {"rule_xs": edges, "n_leaf_cols": 4, "parent": "Arrivals Total",
            "expect": "escalated", "n_body_rows": n_body}


def left_aligned_parent_ruled_pdf(path: str) -> dict:
    """LOOP L ADVERSARIAL FIXTURE (re-review finding N1) — a SHORT merged parent drawn
    LEFT-ALIGNED at exactly its column's leaf-label x, and no header-block rule.

    'Arr' sits at x=112, the same x as the leaf label 'Tonnes' below it, because in a
    left-aligned table every cell in a column starts at the same coordinate. It therefore
    shares the leaf label's alignment origin BY CONSTRUCTION — which is precisely why that
    predicate cannot, on its own, tell a parent from a wrap fragment. Measured before the
    round-2 narrowing: the law derived ('continuation',) and welded BASE's CORRECT
    two-level header ('Arr' over 'Tonnes') into a flat 'Arr Tonnes', silently, at the same
    score, on a region that already tiled.

    Expected: no header-block rule -> outside the engagement context -> NO derivation, and
    the region compiles exactly as BASE does, with 'Arr' still a header node of its own.
    """
    edges = [40.0, 110.0, 180.0, 250.0, 320.0]
    xs = [42.0, 112.0, 182.0, 252.0]
    n_body, rh = 20, 14.0
    top = 40.0 + (2 + n_body) * rh
    c = canvas.Canvas(str(path), pagesize=(360.0, top + 30.0))
    c.setFont("Courier-Bold", 8)
    c.drawString(112.0, top, "Arr")                       # left-aligned ON the leaf origin
    for x, t in zip(xs, ["Port", "Tonnes", "Ship", "Berth"]):
        c.drawString(x, top - rh, t)
    c.setFont("Courier", 8)
    for i in range(n_body):
        for x, t in zip(xs, ("Mackay", str(1000 + 50 * i), "V%02d" % i, "B%02d" % i)):
            c.drawString(x, top - (2 + i) * rh, t)
    c.setLineWidth(0.5)
    for e in edges:
        c.line(e, top - (2 + n_body) * rh - 4, e, top + 10)
    c.save()
    return {"rule_xs": edges, "n_leaf_cols": 4, "parent": "Arr", "leaf_under_parent": "Tonnes",
            "welded_if_broken": "Arr Tonnes", "n_body_rows": n_body}


def bordered_two_level_header_ruled_pdf(path: str) -> dict:
    """LOOP L ADVERSARIAL FIXTURE (re-review finding N2) — TWO genuine group-label rows above
    ONE header-block rule, with NO row between that rule and the leaf header.

    This is what Excel's "all borders" produces for a bordered multi-row header: a rule is
    drawn between the last parent row and the leaf row. Measured before the round-2
    narrowing, at law level: both parent rows lie above the rule, so both derived
    'furniture' and every genuine header level would have been demoted to a caption.

    Expected: the engagement context requires a row BELOW the block rule as well as above
    it; here there is none, so the law abstains and the region keeps its BASE reading.
    """
    edges = [40.0, 110.0, 180.0, 250.0, 320.0]
    xs = [42.0, 112.0, 182.0, 252.0]
    n_body, rh = 20, 14.0
    top = 40.0 + (3 + n_body) * rh
    c = canvas.Canvas(str(path), pagesize=(360.0, top + 30.0))
    c.setFont("Courier-Bold", 8)
    c.drawString(112.0, top, "Grp")                       # parent row 0
    c.drawString(252.0, top, "Grp")
    c.drawString(112.0, top - rh, "Sub")                  # parent row 1
    c.drawString(252.0, top - rh, "Sub")
    for x, t in zip(xs, ["Port", "Tonnes", "Ship", "Berth"]):
        c.drawString(x, top - 2 * rh, t)                  # the leaf header
    c.setFont("Courier", 8)
    for i in range(n_body):
        for x, t in zip(xs, ("Mackay", str(1000 + 50 * i), "V%02d" % i, "B%02d" % i)):
            c.drawString(x, top - (3 + i) * rh, t)
    c.setLineWidth(0.5)
    for e in edges:
        c.line(e, top - (3 + n_body) * rh - 4, e, top + 10)
    # the block rule sits between the last PARENT row and the leaf row — no row below it
    c.line(edges[0] - 2.0, top - 1.4 * rh, edges[-1] + 2.0, top - 1.4 * rh)
    c.save()
    return {"rule_xs": edges, "n_leaf_cols": 4, "parents": ["Grp", "Sub"], "n_body_rows": n_body}


def image_only_table_pdf(path):
    """A text-layer-LESS PDF: render simple_table_pdf to a raster and place it full-page.
    Pure-pip (PNG, no JPEG encoder). Simulates a scan for the OCR first-mile tests."""
    import os, tempfile
    import pypdfium2 as pdfium
    from reportlab.lib.utils import ImageReader
    src = os.path.join(tempfile.mkdtemp(), "src.pdf")
    simple_table_pdf(src)
    pdf = pdfium.PdfDocument(src)
    try:
        page = pdf[0]
        w_pt, h_pt = page.get_size()
        pil = page.render(scale=3.0).to_pil().convert("RGB")
    finally:
        pdf.close()
    png = os.path.join(tempfile.mkdtemp(), "page.png")
    pil.save(png)  # PNG: no JPEG encoder needed
    c = canvas.Canvas(path, pagesize=(w_pt, h_pt))
    c.drawImage(ImageReader(png), 0, 0, width=w_pt, height=h_pt)
    c.save()
    return path


def pattern_enum_table_pdf(path):
    """A 2-column record table: a PATTERN column 'Size' (78kg/big) + an ENUM column 'Sero'
    (negative/unknown), two rows. Single-token cells, wide gap -> compiles RECORD_TABLE. For the
    enum/pattern end-to-end grounding demonstration (raw-doc -> grounded-graph via sh:pattern/sh:in)."""
    cols = [72.0, 260.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    rows = [("Size", "Sero"), ("78kg", "negative"), ("big", "unknown")]
    y0 = PAGE_H - 100.0
    for i, row in enumerate(rows):
        y = y0 - i * 18.0
        for x, cell in zip(cols, row):
            c.drawString(x, y, cell)
    c.save()
    return path


def aligned_space_table_pdf(path: str) -> dict:
    """THE R13 COUNTER-EXAMPLE (attempt 1's killer), committed as the permanent red test.

    A monospaced ruled table whose values carry a COLUMN-ALIGNED internal space ('AB CDEFGH',
    '01 JAN 2026', '12 500'). The aligned spaces form a persistent blank run with ink on both
    sides — the same signal as a real un-ruled column boundary. Measured: candidates ARE
    generated in the ID and Date intervals and are refused by header confirmation (one-sided
    header ink — the label sits on only one side of the candidate). No candidate arises in the
    Tonnes interval at all: the header word 'Tonnes' inks the run enough that the blank fraction
    falls below the generation threshold, so refine_rule_columns never proposes a boundary there
    — confirmation never gets a chance to see it. Header confirmation must refuse every split and
    the table must compile exactly as if refinement did not exist: RECORD_TABLE, 18 cells, score
    1.0. Attempt 1 asserted the split and CRASHED compile_tables at tab:CoverageShape."""
    c = canvas.Canvas(path, pagesize=(400, 200))
    c.setFont("Courier", 9)
    cols = [60, 180, 300]
    header = ["ID", "Date", "Tonnes"]
    rows = [["AB CDEFGH", "01 JAN 2026", "12 500"], ["CD EFGHIJ", "02 FEB 2026", "13 750"],
            ["EF GHIJKL", "03 MAR 2026", "14 250"], ["GH IJKLMN", "04 APR 2026", "15 100"],
            ["IJ KLMNOP", "05 MAY 2026", "16 300"], ["KL MNOPQR", "06 JUN 2026", "17 800"]]
    y = 170
    for i, h in enumerate(header):
        c.drawString(cols[i], y, h)
    y -= 16
    for r in rows:
        for i, v in enumerate(r):
            c.drawString(cols[i], y, v)
        y -= 16
    for x in (50, 170, 290, 395):
        c.line(x, 20, x, 180)
    c.save()
    return {"cols": 3, "data_cells": 18}


def confirmed_split_table_pdf(path: str) -> dict:
    """THE E8 FIXTURE: a ruled table whose middle interval holds TWO header-labeled columns
    with no rule between them — the header confirms the candidate, so this is the committed
    positive case for header-confirmed refinement (GrainCorp's shape, synthetically).

    Rules at 50/170/310/395; headers 'ID' | 'Qty' + 'Unit' (two labels inside one interval,
    separated by a wide gutter) | 'Total'. Measured while writing this fixture: candidate
    [218.5] is generated, grid.ncols == 3, split == 1, the header confirms it (CONFIRMED =
    {218.5}), column_xs becomes (50.0, 170.0, 218.5, 310.0, 395.0), and the table compiles
    end to end with 24 data cells (RECORD_TABLE, score 1.0) where the unrefined 3-column grid
    would give 18."""
    c = canvas.Canvas(path, pagesize=(430, 200))
    c.setFont("Courier", 9)
    c.drawString(60, 170, "ID")
    c.drawString(180, 170, "Qty")
    c.drawString(240, 170, "Unit")
    c.drawString(320, 170, "Total")
    rows = [["A1", "10", "kg", "100"], ["B2", "20", "kg", "200"], ["C3", "30", "kg", "300"],
            ["D4", "40", "kg", "400"], ["E5", "50", "kg", "500"], ["F6", "60", "kg", "600"]]
    y = 154
    for r in rows:
        c.drawString(60, y, r[0])
        c.drawString(180, y, r[1])
        c.drawString(240, y, r[2])
        c.drawString(320, y, r[3])
        y -= 16
    for x in (50, 170, 310, 395):
        c.line(x, 20, x, 180)
    c.save()
    return {"cols": 4, "data_cells": 24}


def two_page_unrelated_pdf(path: str) -> dict:
    """Taxonomy case 1: two CONSECUTIVE pages, each a self-contained ruled record
    table with DIFFERENT leaf headers AND different column x-positions
    (page 1: Port|Ship|Tonnes at one grid; page 2: Patient|Analyte|Result|Unit at
    a 4-column grid shifted right). compile_document must NOT stitch them.

    Ruled (vertical rules at each column edge, `_tight_table`'s idiom) so each page
    compiles as a clean RECORD_TABLE standalone — the point of this fixture is that
    the driver must NOT chain them into one table across the page break, not that
    either page is individually hard to read."""
    rh = 18.0

    def _ruled_page(c, cols, headers, rows, top):
        c.setFont("Courier-Bold", 10)
        for (l, r), h in zip(cols, headers):
            c.drawString(l, top, h)
        c.setFont("Courier", 10)
        for i, row in enumerate(rows):
            y = top - (i + 1) * rh
            for (l, r), cell in zip(cols, row):
                c.drawString(l, y, cell)
        c.setLineWidth(0.7)
        bottom = top - (len(rows) + 1) * rh
        for (l, r) in cols:
            c.line(l - 4, top + 12, l - 4, bottom)
        c.line(cols[-1][1] + 4, top + 12, cols[-1][1] + 4, bottom)

    c = canvas.Canvas(str(path), pagesize=letter)
    top = PAGE_H - 90.0

    # Page 1: Port | Ship | Tonnes — a shipping stem record table.
    cols1 = [(60.0, 160.0), (170.0, 260.0), (270.0, 360.0)]
    headers1 = ["Port", "Ship", "Tonnes"]
    rows1 = [("Mackay", "V1", "1000"), ("Gladstone", "V2", "1500"),
             ("Newcastle", "V3", "2000")]
    _ruled_page(c, cols1, headers1, rows1, top)
    c.showPage()

    # Page 2: Patient | Analyte | Result | Unit, shifted right, 4-column grid —
    # an unrelated lab-report record table. Different domain, different x's.
    cols2 = [(220.0, 300.0), (310.0, 390.0), (400.0, 460.0), (470.0, 530.0)]
    headers2 = ["Patient", "Analyte", "Result", "Unit"]
    rows2 = [("P001", "Hb", "13.2", "g/dL"), ("P002", "WBC", "7.8", "x10^9/L"),
             ("P003", "Na", "140", "mmol/L")]
    _ruled_page(c, cols2, headers2, rows2, top)
    c.save()
    return {"page1_headers": headers1, "page2_headers": headers2,
            "page1_cols": [l for l, r in cols1], "page2_cols": [l for l, r in cols2]}


def subtotal_hier_table_pdf(path: str, hrules: bool = True) -> dict:
    """Loop H E2E: a merged 2-level header (Voyage spans Ship+Qty+Berth, forcing the
    hierarchical path), suppressed keys, ONE subtotal row, and hrules between all body rows
    (the author's row delimiters). The subtotal row sits at the ABSORBABLE 12pt pitch below
    its group (the ordinary pitch is 16pt, so lead stays 16 and 12 < lead), so the hrule
    between them is LOAD-BEARING:
    with hrules=False the SUB row is a proper-subset partial row inside the wrap window and
    group_wrapped fuses it into the record above (measured — pinned by
    test_without_hrules_the_subtotal_row_fuses). This is the integrated Task 1 + Task 3
    slice: de-fusion is what makes the subtotal a detectable row at all.

    NO vertical rules on purpose: whitespace-gutter column recovery (as pivoted_table_pdf
    uses) gives the correct narrow merged span. The trailing text column Berth (never
    numeric) is required: without it, Mon/Port/Ship read as stub and Qty alone as a
    homogeneous-numeric data suffix, which is_matrix_candidate reads as a PIVOT matrix
    (loop 2's matrix.py path) rather than the loop H hierarchical path this test targets —
    Berth (text, never numeric) breaks that homogeneous-numeric suffix."""
    leaves = [(40.0, 90.0), (110.0, 170.0), (190.0, 230.0), (250.0, 300.0), (320.0, 360.0)]
    names = ["Mon", "Port", "Ship", "Qty", "Berth"]
    c = canvas.Canvas(path, pagesize=(400, 220))
    c.setFont("Helvetica", 9)
    c.drawCentredString((leaves[2][0] + leaves[3][1]) / 2.0, 196, "Voyage")
    for (l, r), n in zip(leaves, names):
        c.drawString(l, 182, n)
    body = [("Jul", "Mackay", "V1", "100", "B1"), ("", "Mackay", "V2", "150", "B2"),
            ("", "SUB", "", "250", ""), ("Aug", "Gladstone", "V3", "300", "B4")]
    y = 166
    ys = []
    for i, (mon, port, ship, qty, berth) in enumerate(body):
        if mon:
            c.drawString(leaves[0][0], y, mon)
        c.drawString(leaves[1][0], y, port)
        if ship:
            c.drawString(leaves[2][0], y, ship)
        c.drawString(leaves[3][0], y, qty)
        if berth:
            c.drawString(leaves[4][0], y, berth)
        ys.append(y)
        # the SUB row (next row after index 1) sits at the absorbable 12pt pitch (< lead,
        # with room for the separating hrule to clear the glyphs); every other gap is the
        # ordinary 16pt, so lead (the median gap) stays 16
        y -= 12 if i == 1 else 16
    if hrules:
        for yy in ys:                                    # hrule under EVERY body row
            c.line(35, yy - 4, 355, yy - 4)
        c.line(35, 178, 355, 178)                        # header/body rule
    c.save()
    return {"cols": 5, "subtotal_value": "250"}


def cut_group_two_page_pdf(path: str) -> dict:
    """LOOP N FIXTURE (R35) — subtotal_hier_table_pdf's own proven hierarchical shape (Mon /
    Port / Ship / Qty / Berth, 'Voyage' merged over Ship+Qty+Berth, forcing loop H's
    arithmetic path — the ONLY path detect_aggregation_rows runs, per holon.py's
    assert_hier_region), made RULED (vertical rules at the leaf column edges, the loop-M
    continuation law's author-drawn grid — see document.py's `_author_boundaries`) and split
    across a page break so ONE group's members straddle it:

      page 0: the group's first two voyages (Mackay V1=100, V2=150) under the full
              Voyage/leaf header block.
      page 1: the SAME header block redrawn on the SAME ruled grid (same leaf texts at the
              same origin x's, same rule x's -> the continuation law's clauses all hold, so
              compile_document must recognize and chain the pair) + the group's THIRD voyage
              (Mackay V3=200) + a 'SUB' subtotal row (2 populated cells: Port='SUB', the
              label; Qty='450', the measure) whose value is the FULL group's sum
              (100+150+200=450) — NOT page 1's own local sum (200). detect_aggregation_rows
              run on page 1's rows alone therefore finds the candidate but refuses it (200 !=
              450); only a window spanning BOTH pages' body rows confirms it. That is the
              whole point of this fixture: it is confirmable ONLY at document level (R35).

    Every row (both pages) carries the author's own hrule beneath it — subtotal_hier_table_pdf's
    own load-bearing convention (Task 3 review, Important 1): without it, group_wrapped's
    row-clock can fuse an oddly-pitched row into its neighbour. Here every pitch is the ordinary
    16pt (no absorbable-pitch trick is needed — the SUB row is simply page 1's last row), so
    the hrules are a belt-and-braces match to the proven shape, not load-bearing by construction.
    """
    from reportlab.pdfgen import canvas as _canvas
    leaves = [(40.0, 90.0), (110.0, 170.0), (190.0, 230.0), (250.0, 300.0), (320.0, 360.0)]
    names = ["Mon", "Port", "Ship", "Qty", "Berth"]
    rh = 16.0
    top = 196.0
    W, H = 400.0, 220.0
    edges = [leaves[0][0] - 4.0] + [l - 4.0 for (l, r) in leaves[1:]] + [leaves[-1][1] + 4.0]

    c = _canvas.Canvas(str(path), pagesize=(W, H))

    def _page(body_rows):
        c.setFont("Helvetica", 9)
        c.drawCentredString((leaves[2][0] + leaves[3][1]) / 2.0, top, "Voyage")
        for (l, r), n in zip(leaves, names):
            c.drawString(l, top - rh, n)
        c.setFont("Helvetica", 8)
        ys = []
        y = top - 2 * rh
        for row in body_rows:
            for (l, r), v in zip(leaves, row):
                if v:
                    c.drawString(l, y, v)
            ys.append(y)
            y -= rh
        c.setLineWidth(0.7)
        bottom = y + rh - 6.0
        for e in edges:
            c.line(e, top - rh + 10.0, e, bottom)
        c.line(edges[0], top - rh - 4.0, edges[-1], top - rh - 4.0)   # header/body rule
        for yy in ys:
            c.line(edges[0], yy - 4.0, edges[-1], yy - 4.0)          # per-row hrule

    body0 = [("Jul", "Mackay", "V1", "100", "B1"), ("Jul", "Mackay", "V2", "150", "B2")]
    _page(body0)
    c.showPage()
    body1 = [("Jul", "Mackay", "V3", "200", "B3"), ("", "SUB", "", "450", "")]
    _page(body1)
    c.save()
    return {"leaves": leaves, "names": names, "rule_xs": edges,
            "page0_rows": body0, "page1_rows": body1,
            "group_members": ["V1", "V2", "V3"], "full_sum": 450,
            "page1_local_sum": 200}


def page_local_group_two_page_pdf(path: str) -> dict:
    """LOOP N FIXTURE — the RETRACTION case (loop-N review M-1), cut_group_two_page_pdf's mirror.

    Same ruled two-page continuation shape (Mon / Port / Ship / Qty / Berth, 'Voyage' merged over
    Ship+Qty+Berth, per-row hrules, the header block redrawn identically so the continuation law
    stitches the pair), but the page-1 subtotal is page 1's OWN local sum:

      page 0: Mackay V1=100, V2=150
      page 1: Mackay V3=100, V4=150 + 'SUB' = 250

    Page-locally the SUB row CONFIRMS (100 + 150 = 250), so the per-page pass types it
    tab:DetectedAggregationRow AND loop I derives a tab:DerivedRowGroup off it (its two members
    carry the unique non-blank Port value 'Mackay', which is the group key). At DOCUMENT level the
    walk-back reaches page 0's rows too — no enclosing aggregation stops it — and 100+150+100+150
    = 500 != 250, so the document window REFUSES the row: the one measured-on-nothing case the
    stem never produces (every stem retraction count is 0), constructed so the retraction path can
    be pinned. The group's witness is then gone, and the group must go with it.
    """
    from reportlab.pdfgen import canvas as _canvas
    leaves = [(40.0, 90.0), (110.0, 170.0), (190.0, 230.0), (250.0, 300.0), (320.0, 360.0)]
    names = ["Mon", "Port", "Ship", "Qty", "Berth"]
    rh = 16.0
    top = 196.0
    W, H = 400.0, 220.0
    edges = [leaves[0][0] - 4.0] + [l - 4.0 for (l, r) in leaves[1:]] + [leaves[-1][1] + 4.0]

    c = _canvas.Canvas(str(path), pagesize=(W, H))

    def _page(body_rows):
        c.setFont("Helvetica", 9)
        c.drawCentredString((leaves[2][0] + leaves[3][1]) / 2.0, top, "Voyage")
        for (l, r), n in zip(leaves, names):
            c.drawString(l, top - rh, n)
        c.setFont("Helvetica", 8)
        ys = []
        y = top - 2 * rh
        for row in body_rows:
            for (l, r), v in zip(leaves, row):
                if v:
                    c.drawString(l, y, v)
            ys.append(y)
            y -= rh
        c.setLineWidth(0.7)
        bottom = y + rh - 6.0
        for e in edges:
            c.line(e, top - rh + 10.0, e, bottom)
        c.line(edges[0], top - rh - 4.0, edges[-1], top - rh - 4.0)   # header/body rule
        for yy in ys:
            c.line(edges[0], yy - 4.0, edges[-1], yy - 4.0)          # per-row hrule

    body0 = [("Jul", "Mackay", "V1", "100", "B1"), ("Jul", "Mackay", "V2", "150", "B2")]
    _page(body0)
    c.showPage()
    body1 = [("Jul", "Mackay", "V3", "100", "B3"), ("Jul", "Mackay", "V4", "150", "B4"),
             ("", "SUB", "", "250", "")]
    _page(body1)
    c.save()
    return {"leaves": leaves, "names": names, "rule_xs": edges,
            "page0_rows": body0, "page1_rows": body1,
            "page1_local_sum": 250, "document_sum": 500}


def bare_identical_two_page_pdf(path: str) -> dict:
    """LOOP O FIXTURE (R33, task 1) — the genuinely INDISTINGUISHABLE case-3 sibling.

    The SAME template (`Store|Item|Qty`, same ruled grid, same header text and origin) on
    BOTH pages — NO banner, NO subtotal, just different data. A fluent reader cannot tell
    these two pages apart from one continuous table split at the page break; stitching them
    is the CORRECT reading here, not a defect (loop O's residual — `test_bare_identical_-
    still_stitches` pins this as invariant-consistent behaviour that must survive whatever
    licence closes R33). Contrast with `case3_with_subtotals_pdf`, whose per-page banners
    are the (non-table-band) evidence that the two tables are logically independent.

    Geometry is `test_template_pages_stitch_the_known_case3_false_positive`'s own fixture
    (test_document.py) with the banner line removed — everything else (columns, rules,
    header text) is unchanged, since only the leaf header block and the author-drawn grid
    are what the continuation law (continuation-of.rq) ever reads."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    cols = [(60.0, 160.0), (170.0, 260.0), (270.0, 360.0)]

    def _page(c, rows, top):
        c.setFont("Courier-Bold", 10)
        for (l, _r), h in zip(cols, ["Store", "Item", "Qty"]):
            c.drawString(l, top, h)
        c.setFont("Courier", 10)
        for i, row in enumerate(rows):
            y = top - (i + 1) * 18.0
            for (l, _r), cell in zip(cols, row):
                c.drawString(l, y, cell)
        c.setLineWidth(0.7)
        bottom = top - (len(rows) + 1) * 18.0
        for (l, _r) in cols:
            c.line(l - 4, top + 12, l - 4, bottom)
        c.line(cols[-1][1] + 4, top + 12, cols[-1][1] + 4, bottom)

    page0_rows = [("Alpha", "Bolt", "10"), ("Beta", "Nut", "20")]
    page1_rows = [("Gamma", "Screw", "30"), ("Delta", "Nail", "40")]
    top = letter[1] - 90.0
    c = canvas.Canvas(str(path), pagesize=letter)
    _page(c, page0_rows, top)
    c.showPage()
    _page(c, page1_rows, top)
    c.save()
    return {"cols": cols, "page0_rows": page0_rows, "page1_rows": page1_rows}


def case3_with_subtotals_pdf(path: str, conflicting_labels: bool) -> dict:
    """LOOP O FIXTURE (R33, task 1) — the pinned case-3 shape (independent template tables
    sharing one header+grid, DIFFERENT per-page banners in a non-table band — see
    test_document.py's test_template_pages_stitch_the_known_case3_false_positive and
    continuation-of.rq's header, whose measurement this reproduces) EXTENDED with a
    per-store subtotal row that CONFIRMS PAGE-LOCALLY on its own page (loop-H arithmetic,
    `rows.detect_aggregation_rows`, reached via the HIERARCHICAL path: a 'Voyage' parent
    merged over Ship/Qty/Berth forces UNSUPPORTED_TABLE classification, exactly the proven
    shape `cut_group_two_page_pdf` / `page_local_group_two_page_pdf` already compile
    through `holon.assert_hier_region`).

    Page 0 ("NORTH REGION WEEKLY"): ONE data row, Qty=0 — a DELIBERATELY zero quantity.
    Chosen so that IF the false continuation stitches the pair (measured: it does — R33)
    and the document-level pass (`document.reconcile_chain_arithmetic`) widens page 1's
    subtotal window across the break, the document-level sum is UNCHANGED from page 1's
    own local sum (a zero operand contributes nothing to the walk-back total). This
    isolates the loop's two faces from one another on purpose: it lets face 5 (does a
    document-level GROUP derive across the two independent tables?) be observed without
    face 4 (does the wider window RETRACT the confirmation?) also firing and destroying
    the group by orphaning its witness first — see the task-1 report for which faces this
    fixture actually measures, and which do not reproduce on it.

    Page 1 ("SOUTH REGION MONTHLY"): two data rows + one 'SUB' row whose value is exactly
    their sum (100 + 150 = 250) — confirms PAGE-LOCALLY on page 1 alone.

    `conflicting_labels` controls the group-identity column ('Port'):
      False — the SAME label ('Alpha') on every row of BOTH pages: the shape under which,
              if a document-level group is derived at all, it silently ADOPTS page 0's row
              as a member sharing page 1's key (the fabrication face).
      True  — page 0's row carries a DIFFERENT label ('Beta') from page 1's rows
              ('Alpha'): the shape under which the group KEY becomes non-unique across the
              false boundary and the document-level re-derivation refuses outright, while
              page 1's OWN page-local group (superseded once the chain forms — see
              `document._supersede_page_groups`) is never replaced (the loss face).
    Every OTHER fact (header text, grid, rule positions) is identical between the two
    variants and between the two pages, because only the leaf header block and the
    author-drawn grid are what the continuation law reads."""
    from reportlab.pdfgen import canvas as _canvas

    leaves = [(40.0, 90.0), (110.0, 170.0), (190.0, 230.0), (250.0, 300.0), (320.0, 360.0)]
    names = ["Mon", "Port", "Ship", "Qty", "Berth"]
    rh = 16.0
    table_top = 196.0
    banner_gap = 40.0                 # >> 1.8x the table's own ~9pt median line gap
    W = 400.0
    H = table_top + banner_gap + 30.0
    edges = [leaves[0][0] - 4.0] + [l - 4.0 for (l, r) in leaves[1:]] + [leaves[-1][1] + 4.0]

    c = _canvas.Canvas(str(path), pagesize=(W, H))

    def _page(banner, body_rows):
        c.setFont("Courier-Bold", 11)
        c.drawString(leaves[0][0], table_top + banner_gap, banner)   # non-table band
        c.setFont("Helvetica", 9)
        c.drawCentredString((leaves[2][0] + leaves[3][1]) / 2.0, table_top, "Voyage")
        for (l, r), n in zip(leaves, names):
            c.drawString(l, table_top - rh, n)
        c.setFont("Helvetica", 8)
        ys = []
        y = table_top - 2 * rh
        for row in body_rows:
            for (l, r), v in zip(leaves, row):
                if v:
                    c.drawString(l, y, v)
            ys.append(y)
            y -= rh
        c.setLineWidth(0.7)
        bottom = y + rh - 6.0
        for e in edges:
            c.line(e, table_top - rh + 10.0, e, bottom)
        c.line(edges[0], table_top - rh - 4.0, edges[-1], table_top - rh - 4.0)
        for yy in ys:
            c.line(edges[0], yy - 4.0, edges[-1], yy - 4.0)

    label1 = "Beta" if conflicting_labels else "Alpha"
    body0 = [("Jul", "Alpha", "V1", "0", "B1")]
    body1 = [("Jul", label1, "V2", "100", "B2"), ("Jul", label1, "V3", "150", "B3"),
             ("", "SUB", "", "250", "")]

    _page("NORTH REGION WEEKLY", body0)
    c.showPage()
    _page("SOUTH REGION MONTHLY", body1)
    c.save()
    return {"leaves": leaves, "names": names, "rule_xs": edges,
            "page0_rows": body0, "page1_rows": body1, "page1_local_sum": 250,
            "conflicting_labels": conflicting_labels,
            "label_page0": "Alpha", "label_page1": label1}
