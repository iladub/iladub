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
