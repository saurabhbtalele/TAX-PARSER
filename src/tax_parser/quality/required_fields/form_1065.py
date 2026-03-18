"""Form 1065 — Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    "taxpayer.name",
    "taxpayer.ein",

    # Income
    "income.line_1a_gross_receipts",
    "income.line_3_gross_profit",
    "income.line_8_total_income",

    # Deductions
    "deductions.line_21_total_deductions",

    # Bottom line
    "income.line_22_ordinary_business_income",

    # Schedule K
    "schedule_k.line_1_ordinary_business_income",
]
