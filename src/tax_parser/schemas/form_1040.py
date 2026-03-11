"""Schema for IRS Form 1040 – U.S. Individual Income Tax Return.

This schema is primarily used as a reference model for Azure DI output mapping.
Azure DI handles extraction; we normalize its output to this structure.
"""

from __future__ import annotations

from pydantic import BaseModel

from tax_parser.schemas.base import BaseTaxForm


class Form1040Header(BaseModel):
    filing_status: str | None = None  # single | married_joint | married_separate | head_of_household | qualifying_surviving_spouse
    first_name: str | None = None
    last_name: str | None = None
    spouse_first_name: str | None = None
    spouse_last_name: str | None = None
    ssn: str | None = None
    spouse_ssn: str | None = None
    digital_assets: bool | None = None
    standard_deduction_you_dependent: bool | None = None
    standard_deduction_spouse_dependent: bool | None = None
    age_65_or_older_you: bool | None = None
    age_65_or_older_spouse: bool | None = None
    blind_you: bool | None = None
    blind_spouse: bool | None = None


class Form1040Income(BaseModel):
    line_1a_wages: float | None = None
    line_1b_household_employee_wages: float | None = None
    line_1c_tip_income: float | None = None
    line_1d_medicaid_waiver: float | None = None
    line_1e_dependent_care_benefits: float | None = None
    line_1f_employer_adoption_benefits: float | None = None
    line_1g_form_8919_wages: float | None = None
    line_1h_strike_benefits: float | None = None
    line_1i_stock_option_excess: float | None = None
    line_1z_add_1a_through_1i: float | None = None
    line_2a_tax_exempt_interest: float | None = None
    line_2b_taxable_interest: float | None = None
    line_3a_qualified_dividends: float | None = None
    line_3b_ordinary_dividends: float | None = None
    line_4a_ira_distributions: float | None = None
    line_4b_taxable_ira: float | None = None
    line_5a_pensions_annuities: float | None = None
    line_5b_taxable_pensions: float | None = None
    line_6a_social_security: float | None = None
    line_6b_taxable_social_security: float | None = None
    line_7_capital_gain_loss: float | None = None
    line_8_other_income: float | None = None
    line_9_total_income: float | None = None
    line_10_adjustments: float | None = None
    line_11_adjusted_gross_income: float | None = None
    line_12_standard_or_itemized: float | None = None
    line_13_qualified_business_income: float | None = None
    line_14_total_deductions: float | None = None
    line_15_taxable_income: float | None = None


class Form1040TaxPayments(BaseModel):
    line_16_tax: float | None = None
    line_17_amount_from_schedule_2: float | None = None
    line_18_add_lines_16_17: float | None = None
    line_19_child_tax_credit: float | None = None
    line_20_amount_from_schedule_3: float | None = None
    line_21_add_lines_19_20: float | None = None
    line_22_subtract_21_from_18: float | None = None
    line_23_other_taxes: float | None = None
    line_24_total_tax: float | None = None
    line_25a_w2_withholding: float | None = None
    line_25b_1099_withholding: float | None = None
    line_25c_other_withholding: float | None = None
    line_25d_total_withholding: float | None = None
    line_26_estimated_tax_payments: float | None = None
    line_27_earned_income_credit: float | None = None
    line_33_total_payments: float | None = None
    line_34_overpayment: float | None = None
    line_37_amount_owed: float | None = None


class Form1040(BaseTaxForm):
    """IRS Form 1040 schema."""

    form_type: str = "1040"

    header: Form1040Header = Form1040Header()
    income: Form1040Income = Form1040Income()
    tax_payments: Form1040TaxPayments = Form1040TaxPayments()
