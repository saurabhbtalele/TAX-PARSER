"""Form 1040 — Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    "taxpayer.name",
    "taxpayer.ssn",
    "income.line_1_wages",
    "income.line_9_total_income",
    "income.line_11_adjusted_gross_income",
    "income.line_15_taxable_income",
    "tax.line_16_tax",
    "tax.line_24_total_tax",
    "payments.line_33_total_payments",
]
