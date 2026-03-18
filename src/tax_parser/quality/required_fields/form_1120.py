"""Form 1120 — Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    "taxpayer.name",
    "taxpayer.ein",
    "income.line_1a_gross_receipts",
    "income.line_3_gross_profit",
    "income.line_11_total_income",
    "deductions.line_27_total_deductions",
    "tax.line_30_taxable_income",
    "tax.line_31_total_tax",
]
