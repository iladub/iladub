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
