"""Form 1120 — Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    "taxpayer.name",
    "taxpayer.ein",
    "income.line_1a_gross_receipts",
    "income.line_3_gross_profit",
    "income.line_6_total_income",
    "deductions.line_20_total_deductions",
    "tax_payments.line_21_ordinary_business_income",
    "tax_payments.line_22c_total_tax",
]
