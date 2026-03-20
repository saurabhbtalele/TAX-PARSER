"""Form 1040 — Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    "header.first_name",
    "header.last_name",
    "header.ssn",
    "income.line_1a_wages",
    "income.line_9_total_income",
    "income.line_11_adjusted_gross_income",
    "income.line_15_taxable_income",
    "tax_payments.line_16_tax",
    "tax_payments.line_24_total_tax",
    "tax_payments.line_33_total_payments",
]
