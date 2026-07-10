"""A richer, visually compelling synthetic lab report for the ETKL 1a showcase.

Self-contained (no dependency on the test suite). Courier is used so the
column gutters are clean and the whitespace-profile method is easy to *see* —
though the method operates on real word bounding boxes in points, not on a
monospace character grid, so it works with proportional fonts too.
"""
from __future__ import annotations

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = letter  # 612 x 792 points

# Left x (points) of each of the 5 table columns.
COLS = [60.0, 250.0, 330.0, 410.0, 520.0]

_HEADER = ("Analyte", "Result", "Unit", "Reference Range", "Flag")
_ROWS = [
    ("Hemoglobin", "13.2", "g/dL", "13.5 - 17.5", "LOW"),
    ("Hematocrit", "39.5", "%", "41.0 - 53.0", "LOW"),
    ("WBC", "7.8", "x10^9/L", "4.0 - 11.0", ""),
    ("Platelets", "252", "x10^9/L", "150 - 400", ""),
    ("MCV", "88.4", "fL", "80.0 - 100.0", ""),
    ("Neutrophils", "62.1", "%", "40.0 - 70.0", ""),
]


def lab_report_pdf(path: str) -> dict:
    """Draw a lab report: a title band, a patient/meta band, and a 5-column
    table band (header row + 6 analytes). Returns ground-truth geometry."""
    c = canvas.Canvas(str(path), pagesize=letter)

    # --- title band ---
    c.setFont("Courier-Bold", 15)
    c.drawString(60.0, PAGE_H - 60.0, "HEMATOLOGY REPORT")

    # --- patient / meta band (well below the title) ---
    c.setFont("Courier", 10)
    c.drawString(60.0, PAGE_H - 100.0, "Patient: Jane Doe        MRN: 000-42-1337        Collected: 2026-07-04")

    # --- table band (well below the meta line) ---
    table_top_y = PAGE_H - 150.0
    c.setFont("Courier-Bold", 10)
    for x, cell in zip(COLS, _HEADER):
        c.drawString(x, table_top_y, cell)
    c.setFont("Courier", 10)
    for i, row in enumerate(_ROWS, start=1):
        y = table_top_y - i * 18.0
        for x, cell in zip(COLS, row):
            if cell:
                c.drawString(x, y, cell)

    c.save()
    return {
        "cols": COLS,
        "n_table_cols": len(COLS),
        "n_body_rows": len(_ROWS),
        "n_table_rows": len(_ROWS) + 1,  # + header
        "title": "HEMATOLOGY REPORT",
        "bands_expected": 3,  # title, meta line, table
    }


# --- Supported case: a flat record table with single-word column headers ------

# 4 columns, single-word headers -> the kind the closing slice fully compiles.
_REC_COLS = [60.0, 250.0, 350.0, 460.0]
_REC_HEADER = ("Analyte", "Result", "Unit", "Flag")
_REC_ROWS = [
    ("Hemoglobin", "13.2", "g/dL", "LOW"),
    ("Hematocrit", "39.5", "%", "LOW"),
    ("WBC", "7.8", "x10^9/L", "HIGH"),
    ("Platelets", "252", "x10^9/L", "OK"),
    ("MCV", "88.4", "fL", "OK"),
    ("Neutrophils", "62.1", "%", "OK"),
]


def record_report_pdf(path: str) -> dict:
    """A flat record table (single-word headers, one value per cell) — the kind
    the closing slice compiles end-to-end into a validated table-holon. Title
    and meta bands sit above it so the classifier must also reject non-tables."""
    c = canvas.Canvas(str(path), pagesize=letter)

    c.setFont("Courier-Bold", 15)
    c.drawString(60.0, PAGE_H - 60.0, "HEMATOLOGY PANEL")
    c.setFont("Courier", 10)
    c.drawString(60.0, PAGE_H - 100.0, "Patient: Jane Doe        MRN: 000-42-1337")

    top = PAGE_H - 150.0
    c.setFont("Courier-Bold", 10)
    for x, h in zip(_REC_COLS, _REC_HEADER):
        c.drawString(x, top, h)
    c.setFont("Courier", 10)
    for i, row in enumerate(_REC_ROWS, start=1):
        y = top - i * 18.0
        for x, cell in zip(_REC_COLS, row):
            c.drawString(x, y, cell)

    c.save()
    return {
        "cols": _REC_COLS,
        "n_table_cols": len(_REC_COLS),
        "n_body_rows": len(_REC_ROWS),
        "title": "HEMATOLOGY PANEL",
    }


# --- Hard case: a pivoted report with a 2-level, merged, centered header ------

# 7 leaf columns. (left_x, right_x, align) — align drives how each cell's text
# is placed inside its column, so the ink lands in DIFFERENT places per column.
_PIV_LEAVES = [
    (50.0, 150.0, "left"),    # 0  Analyte  (row-header, no parent)
    (160.0, 215.0, "right"),  # 1  Current · Result
    (225.0, 280.0, "left"),   # 2  Current · Unit
    (290.0, 335.0, "center"), # 3  Current · Flag
    (365.0, 420.0, "right"),  # 4  Prior · Result
    (430.0, 485.0, "left"),   # 5  Prior · Unit
    (495.0, 545.0, "center"), # 6  Prior · Flag
]
# Parent super-headers, each spanning a contiguous run of leaf columns.
_PIV_PARENTS = [("Current Visit", 1, 3), ("Prior Visit", 4, 6)]
_PIV_SUB = ["Analyte", "Result", "Unit", "Flag", "Result", "Unit", "Flag"]
_PIV_BODY = [
    ("Hemoglobin", "13.2", "g/dL", "LOW", "12.8", "g/dL", "LOW"),
    ("Hematocrit", "39.5", "%", "LOW", "38.1", "%", "LOW"),
    ("WBC", "7.8", "x10^9/L", "", "9.2", "x10^9/L", "HIGH"),
    ("Platelets", "252", "x10^9/L", "", "248", "x10^9/L", ""),
    ("MCV", "88.4", "fL", "", "87.9", "fL", ""),
]


def _place(c, text, left, right, align, y):
    if not text:
        return
    if align == "right":
        c.drawRightString(right, y, text)
    elif align == "center":
        c.drawCentredString((left + right) / 2.0, y, text)
    else:
        c.drawString(left, y, text)


def pivoted_report_pdf(path: str) -> dict:
    """A pivoted lab report: two visit groups, each a merged parent header
    ('Current Visit' / 'Prior Visit') CENTERED over three leaf columns, with
    a wrapped ('Result' over '(SI)') sub-header, and per-column alignment
    (numbers right-aligned, flags centered, labels left). This is the case
    increment 1a's whole-band grid is NOT designed to fully solve."""
    c = canvas.Canvas(str(path), pagesize=letter)

    c.setFont("Courier-Bold", 14)
    c.drawString(50.0, PAGE_H - 55.0, "SERIAL CBC — VISIT COMPARISON")

    top = PAGE_H - 95.0
    # parent header row (merged, centered over each group)
    c.setFont("Courier-Bold", 10)
    for label, i, j in _PIV_PARENTS:
        left = _PIV_LEAVES[i][0]
        right = _PIV_LEAVES[j][1]
        c.drawCentredString((left + right) / 2.0, top, label)
    # sub-header row 1 (leaf names)
    for (left, right, align), name in zip(_PIV_LEAVES, _PIV_SUB):
        _place(c, name, left, right, "center" if name != "Analyte" else "left", top - 15.0)
    # sub-header row 2 (a WRAPPED second header line under the two Result cols)
    for idx in (1, 4):
        left, right, _ = _PIV_LEAVES[idx]
        c.drawCentredString((left + right) / 2.0, top - 28.0, "(SI)")

    # body
    c.setFont("Courier", 10)
    body_top = top - 50.0
    for r, row in enumerate(_PIV_BODY):
        y = body_top - r * 18.0
        for (left, right, align), cell in zip(_PIV_LEAVES, row):
            _place(c, cell, left, right, align, y)

    c.save()
    return {
        "n_leaf_cols": len(_PIV_LEAVES),           # 7
        "parents": _PIV_PARENTS,                    # merged super-headers
        "n_body_rows": len(_PIV_BODY),              # 5
        "n_header_rows": 3,                          # parent + leaf + wrapped (SI)
        "title": "SERIAL CBC — VISIT COMPARISON",
    }


# --- Ambiguous case: all-text, merged header, no numeric column -> escalates ---

def ambiguous_report_pdf(path: str) -> dict:
    """A merged-header table with an all-text body and NO numeric column, so the
    header/body boundary is genuinely undecidable. Row 0 is a single centered
    label ('Regions') whose word count (1) != the leaf-column count (3), so it is
    not a flat record; and no column ever becomes type-homogeneous (every cell is
    a text label), so the hierarchical maker cannot place the boundary. ET(K)L
    escalates the whole region rather than guess."""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 10)
    ys = [PAGE_H - 100.0, PAGE_H - 118.0, PAGE_H - 136.0, PAGE_H - 154.0]
    c.drawCentredString((60.0 + 390.0) / 2.0, ys[0], "Regions")   # centered merged header
    rows = [("Region", "North", "South"), ("Area", "Alpha", "Beta"), ("Zone", "Red", "Blue")]
    for y, row in zip(ys[1:], rows):
        for x, cell in zip((60.0, 220.0, 360.0), row):
            c.drawString(x, y, cell)
    c.save()
    return {"title": "Regions (all-text, ambiguous)"}


# --- Transposed case: fields down the first column, records along the others ---

def transposed_report_pdf(path: str) -> dict:
    """A TRANSPOSED patient table: the field names ('Age', 'Sex', 'City') run DOWN
    the first column, and each OTHER column is a record (a patient). The 'Age' row
    is numeric ACROSS the record columns, while each record column mixes types
    (a number, then text) — so no column is all-numeric. That asymmetry is the
    transposition signature. Geometrically a valid grid, so the round-trip and the
    tab: SHACL both pass; only the semantic (type-orientation) oracle catches it,
    and ET(K)L escalates rather than assert an inverted RecordTable.

    (A *fully*-numeric transposed table is genuinely ambiguous — both axes look
    numeric — and is left unflagged, like the all-text case.)"""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier", 11)
    rows = [
        ("Field", "Alice", "Bob"),   # header: field-label column + one column per patient
        ("Age",   "30",    "25"),    # numeric ACROSS the record columns
        ("Sex",   "F",     "M"),
        ("City",  "NYC",   "LA"),
    ]
    for i, row in enumerate(rows):
        y = PAGE_H - 110.0 - i * 20.0
        for x, cell in zip((70.0, 250.0, 400.0), row):
            c.drawString(x, y, cell)
    c.save()
    return {"title": "Transposed patient table (records along columns)"}


# --- Row-header hierarchy: grouped labels run DOWN the stub (blank-below encoding) ---

def row_grouped_report_pdf(path: str) -> dict:
    """A ROW-header hierarchy: a merged 'Region' group (North/South) runs DOWN the
    first stub column via the blank-below (forward-fill) encoding — the vertical
    mirror of Part C's merged COLUMN header. 'Team' is a fully-populated finer stub;
    'Headcount' and 'Budget' are the numeric data columns. North spans Alpha/Bravo,
    South spans Charlie/Delta.

    Today this flattens to a RecordTable (the Bravo/Delta rows lose their group);
    ET(K)L compiles the row-header tree instead — stub columns become the row-header
    axis (tab:coversRow), only the data columns are leaf columns."""
    cols = [60.0, 175.0, 330.0, 440.0]     # Region, Team, Headcount, Budget
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 14)
    c.drawString(60.0, PAGE_H - 60.0, "HEADCOUNT BY REGION")
    top = PAGE_H - 110.0
    rows = [("Region", "Team", "Headcount", "Budget"),
            ("North", "Alpha", "12", "1.2"),
            ("", "Bravo", "8", "0.9"),
            ("South", "Charlie", "15", "1.6"),
            ("", "Delta", "9", "1.1")]
    c.setFont("Courier", 10)
    for i, row in enumerate(rows):
        y = top - i * 18.0
        for x, cell in zip(cols, row):
            if cell:
                c.drawString(x, y, cell)
    c.save()
    return {"title": "HEADCOUNT BY REGION", "groups": {"North": 2, "South": 2},
            "n_leaf_rows": 4, "n_data_cols": 2}


# --- Matrix / cross-tab: BOTH axes are header trees (the 2-D culmination) ---

def crosstab_report_pdf(path: str) -> dict:
    """A MATRIX / cross-tab: a hierarchical COLUMN header (Q1/Q2 each over
    Rev/Cost/Unit) AND a stub ROW axis (North/South), with a numeric data matrix.
    Each value is addressed by (column-path x row-path) — Part C's column pivot and
    Part F's row hierarchy composed into a true 2-D table. Short column-group labels
    (Q1/Q2) over wide numeric groups are recovered by the proximity span builder;
    the stub (blank corner) becomes the row axis (Design A), so only the data columns
    are leaf columns. No new vocabulary — the union of the column + row SHACL certifies it."""
    stub_x = 55.0
    data_x = [140.0, 210.0, 280.0, 380.0, 450.0, 520.0]   # Q1:Rev,Cost,Unit | Q2:Rev,Cost,Unit
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 13)
    c.drawString(stub_x, PAGE_H - 55.0, "QUARTERLY RESULTS BY REGION")
    top = PAGE_H - 100.0
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
    return {"title": "QUARTERLY RESULTS BY REGION",
            "col_groups": {"Q1": 3, "Q2": 3}, "row_axis": ["North", "South"],
            "n_data_cols": 6, "n_leaf_rows": 2}


# --- Multi-table page: two independent tables abreast (segmentation, not fusion) ---

def multi_table_report_pdf(path: str) -> dict:
    """ONE page holding TWO independent record tables side-by-side, separated by a wide
    full-height gutter. detect_bands is 1-D (vertical only), so it would FUSE them into
    one wide table; the segmentation pass splits the page at the certified gutter and
    compiles each table on its own. (A single table — e.g. the cross-tab — is provably
    never split.)"""
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 12)
    c.drawString(60.0, PAGE_H - 60.0, "LAB PANEL")
    c.drawString(360.0, PAGE_H - 60.0, "INVENTORY")
    c.setFont("Courier", 10)
    left = [("Analyte", "Value", "Unit"), ("Hb", "13.2", "g/dL"),
            ("WBC", "7.8", "x10^9"), ("Plt", "252", "x10^9")]
    right = [("Item", "Qty", "Loc"), ("Apple", "10", "A1"),
             ("Pear", "5", "B2"), ("Plum", "8", "C3")]
    lx = [60.0, 150.0, 230.0]
    rx = [360.0, 450.0, 520.0]
    top = PAGE_H - 100.0
    for i, (lr, rr) in enumerate(zip(left, right)):
        y = top - i * 18.0
        for x, v in zip(lx, lr):
            c.drawString(x, y, v)
        for x, v in zip(rx, rr):
            c.drawString(x, y, v)
    c.save()
    return {"tables": 2, "left_header": ["Analyte", "Value", "Unit"],
            "right_header": ["Item", "Qty", "Loc"]}


# --- Denormalized report: a pivoted dimension + measures (invert to 3NF) ---

def denormalized_report_pdf(path: str) -> dict:
    """A denormalized report: 'Region' pivoted into the header over North/South/East/West
    leaf columns, with a 'Year' stub down the side. ET(K)L recovers the pivoted Region
    dimension and inverts to tidy (Year, Region, value) base facts."""
    leaves = [150.0, 250.0, 350.0, 450.0]
    c = canvas.Canvas(str(path), pagesize=letter)
    c.setFont("Courier-Bold", 13)
    c.drawString(60.0, PAGE_H - 60.0, "SALES BY REGION")
    top = PAGE_H - 100.0
    c.setFont("Courier-Bold", 10)
    c.drawCentredString((leaves[0] + leaves[3]) / 2.0, top, "Region")
    for x, n in zip(leaves, ["North", "South", "East", "West"]):
        c.drawCentredString(x, top - 14.0, n)
    c.drawString(60.0, top - 14.0, "Year")
    c.setFont("Courier", 10)
    for i, (yr, vals) in enumerate([("2023", ["10", "20", "30", "40"]),
                                    ("2024", ["12", "22", "33", "44"])]):
        y = top - 32.0 - i * 16.0
        c.drawString(60.0, y, yr)
        for x, v in zip(leaves, vals):
            c.drawCentredString(x, y, v)
    c.save()
    return {"pivot": "Region", "stub": "Year", "n_base_facts": 8}
