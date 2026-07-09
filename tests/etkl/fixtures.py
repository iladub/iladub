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
