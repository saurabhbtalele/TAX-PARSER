"""Form 1120-S — Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    # Header / Entity
    "taxpayer.name",
    "taxpayer.ein",
    "header.date_incorporated",
    "header.total_assets",
    "header.accounting_method",
    "header.number_of_shareholders",

    # Income
    "income.line_1a_gross_receipts",
    "income.line_1c_balance",
    "income.line_2_cost_of_goods_sold",
    "income.line_3_gross_profit",
    "income.line_6_total_income",

    # Deductions
    "deductions.line_7_compensation_of_officers",
    "deductions.line_8_salaries_wages",
    "deductions.line_12_taxes_licenses",
    "deductions.line_13_interest",
    "deductions.line_14_depreciation",
    "deductions.line_20_total_deductions",

    # Tax & Payments
    "tax_payments.line_21_ordinary_business_income",
    "tax_payments.line_22c_total_tax",
    "tax_payments.line_24_total_payments",

    # Schedule K
    "schedule_k.line_1_ordinary_business_income",

    # Balance Sheet (end of year)
    "schedule_l.total_assets.end_of_year",
    "schedule_l.total_liabilities_equity.end_of_year",
]
