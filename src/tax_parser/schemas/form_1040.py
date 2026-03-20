from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm


class Form1040Header(BaseModel):
    """Page 1 - Header Section"""
    
    filing_status: str | None = Field(
        default=None,
        description="Filing status (single, married_joint, married_separate, head_of_household, qualifying_surviving_spouse)",
        page=1,
        box="Filing Status"
    )
    first_name: str | None = Field(
        default=None,
        description="Taxpayer's first name and middle initial",
        page=1,
        box="Your first name and middle initial"
    )
    last_name: str | None = Field(
        default=None,
        description="Taxpayer's last name",
        page=1,
        box="Last name"
    )
    spouse_first_name: str | None = Field(
        default=None,
        description="Spouse's first name and middle initial (if filing jointly)",
        page=1,
        box="If joint return, spouse's first name and middle initial"
    )
    spouse_last_name: str | None = Field(
        default=None,
        description="Spouse's last name (if filing jointly)",
        page=1,
        box="Last name"
    )
    ssn: str | None = Field(
        default=None,
        description="Taxpayer's social security number",
        page=1,
        box="Your social security number"
    )
    spouse_ssn: str | None = Field(
        default=None,
        description="Spouse's social security number (if filing jointly)",
        page=1,
        box="Spouse's social security number"
    )
    digital_assets: bool | None = Field(
        default=None,
        description="Indicates if taxpayer received, sold, or disposed of digital assets",
        page=1,
        box="Digital Assets"
    )
    standard_deduction_you_dependent: bool | None = Field(
        default=None,
        description="Check if someone can claim you as a dependent",
        page=1,
        box="12a Someone can claim You as a dependent"
    )
    standard_deduction_spouse_dependent: bool | None = Field(
        default=None,
        description="Check if someone can claim your spouse as a dependent",
        page=1,
        box="12a Someone can claim Your spouse as a dependent"
    )
    age_65_or_older_you: bool | None = Field(
        default=None,
        description="Check if you were born before January 2, 1961",
        page=1,
        box="12b You: Were born before January 2, 1961"
    )
    age_65_or_older_spouse: bool | None = Field(
        default=None,
        description="Check if your spouse was born before January 2, 1961",
        page=1,
        box="12b Spouse: Was born before January 2, 1961"
    )
    blind_you: bool | None = Field(
        default=None,
        description="Check if you are blind",
        page=1,
        box="12b You: Are blind"
    )
    blind_spouse: bool | None = Field(
        default=None,
        description="Check if your spouse is blind",
        page=1,
        box="12b Spouse: Is blind"
    )
    home_address: str | None = Field(
        default=None,
        description="Taxpayer's home address (number and street)",
        page=1,
        box="Home address (number and street)"
    )
    city_state_zip: str | None = Field(
        default=None,
        description="Taxpayer's city, town, or post office, state, and ZIP code",
        page=1,
        box="City, town, or post office. If you have a foreign address, also complete spaces below."
    )
    foreign_country: str | None = Field(
        default=None,
        description="Foreign country name (if applicable)",
        page=1,
        box="Foreign country name"
    )
    foreign_province: str | None = Field(
        default=None,
        description="Foreign province/state/county (if applicable)",
        page=1,
        box="Foreign province/state/county"
    )
    foreign_postal_code: str | None = Field(
        default=None,
        description="Foreign postal code (if applicable)",
        page=1,
        box="Foreign postal code"
    )
    presidential_campaign: bool | None = Field(
        default=None,
        description="Check if you want $3 to go to the Presidential Election Campaign Fund",
        page=1,
        box="Presidential Election Campaign"
    )


class Form1040Income(BaseModel):
    """Page 1 - Income Section"""
    
    line_1a_wages: float | None = Field(
        default=None,
        description="Total amount from Form(s) W-2, box 1",
        page=1,
        line=1,
        box="a"
    )
    line_1b_household_employee_wages: float | None = Field(
        default=None,
        description="Household employee wages not reported on Form(s) W-2",
        page=1,
        line=1,
        box="b"
    )
    line_1c_tip_income: float | None = Field(
        default=None,
        description="Tip income not reported on line 1a",
        page=1,
        line=1,
        box="c"
    )
    line_1d_medicaid_waiver: float | None = Field(
        default=None,
        description="Medicaid waiver payments not reported on Form(s) W-2",
        page=1,
        line=1,
        box="d"
    )
    line_1e_dependent_care_benefits: float | None = Field(
        default=None,
        description="Taxable dependent care benefits from Form 2441, line 26",
        page=1,
        line=1,
        box="e"
    )
    line_1f_employer_adoption_benefits: float | None = Field(
        default=None,
        description="Employer-provided adoption benefits from Form 8839, line 31",
        page=1,
        line=1,
        box="f"
    )
    line_1g_form_8919_wages: float | None = Field(
        default=None,
        description="Wages from Form 8919, line 6",
        page=1,
        line=1,
        box="g"
    )
    line_1h_strike_benefits: float | None = Field(
        default=None,
        description="Other earned income (strike benefits)",
        page=1,
        line=1,
        box="h"
    )
    line_1i_stock_option_excess: float | None = Field(
        default=None,
        description="Nontaxable combat pay election",
        page=1,
        line=1,
        box="i"
    )
    line_1z_add_1a_through_1i: float | None = Field(
        default=None,
        description="Total of lines 1a through 1h",
        page=1,
        line=1,
        box="z"
    )
    line_2a_tax_exempt_interest: float | None = Field(
        default=None,
        description="Tax-exempt interest",
        page=1,
        line=2,
        box="a"
    )
    line_2b_taxable_interest: float | None = Field(
        default=None,
        description="Taxable interest",
        page=1,
        line=2,
        box="b"
    )
    line_3a_qualified_dividends: float | None = Field(
        default=None,
        description="Qualified dividends",
        page=1,
        line=3,
        box="a"
    )
    line_3b_ordinary_dividends: float | None = Field(
        default=None,
        description="Ordinary dividends",
        page=1,
        line=3,
        box="b"
    )
    line_4a_ira_distributions: float | None = Field(
        default=None,
        description="IRA distributions",
        page=1,
        line=4,
        box="a"
    )
    line_4b_taxable_ira: float | None = Field(
        default=None,
        description="Taxable amount of IRA distributions",
        page=1,
        line=4,
        box="b"
    )
    line_5a_pensions_annuities: float | None = Field(
        default=None,
        description="Pensions and annuities",
        page=1,
        line=5,
        box="a"
    )
    line_5b_taxable_pensions: float | None = Field(
        default=None,
        description="Taxable amount of pensions and annuities",
        page=1,
        line=5,
        box="b"
    )
    line6a_social_security: float | None = Field(
        default=None,
        description="Social security benefits",
        page=1,
        line=6,
        box="a"
    )
    line_6b_taxable_social_security: float | None = Field(
        default=None,
        description="Taxable amount of social security benefits",
        page=1,
        line=6,
        box="b"
    )
    line_7_capital_gain_loss: float | None = Field(
        default=None,
        description="Capital gain or (loss)",
        page=1,
        line=7
    )
    line_8_other_income: float | None = Field(
        default=None,
        description="Additional income from Schedule 1, line 10",
        page=1,
        line=8
    )
    line_9_total_income: float | None = Field(
        default=None,
        description="Total income (sum of lines 1z, 2b, 3b, 4b, 5b, 6b, 7a, and 8)",
        page=1,
        line=9
    )
    line_10_adjustments: float | None = Field(
        default=None,
        description="Adjustments to income from Schedule 1, line 26",
        page=1,
        line=10
    )
    line_11_adjusted_gross_income: float | None = Field(
        default=None,
        description="Adjusted gross income (line 9 minus line 10)",
        page=1,
        line=11
    )
    line_12_standard_or_itemized: float | None = Field(
        default=None,
        description="Standard deduction or itemized deductions",
        page=1,
        line=12,
        box="e"
    )
    line_13_qualified_business_income: float | None = Field(
        default=None,
        description="Qualified business income deduction from Form 8995 or Form 8995-A",
        page=1,
        line=13,
        box="a"
    )
    line_14_total_deductions: float | None = Field(
        default=None,
        description="Total deductions (sum of lines 12e, 13a, and 13b)",
        page=1,
        line=14
    )
    line_15_taxable_income: float | None = Field(
        default=None,
        description="Taxable income (line 11b minus line 14)",
        page=1,
        line=15
    )


class Form1040TaxPayments(BaseModel):
    """Page 1 - Tax and Payments Section"""
    
    line_16_tax: float | None = Field(
        default=None,
        description="Tax amount (see instructions)",
        page=1,
        line=16
    )
    line_17_amount_from_schedule_2: float | None = Field(
        default=None,
        description="Amount from Schedule 2, line 3",
        page=1,
        line=17
    )
    line_18_add_lines_16_17: float | None = Field(
        default=None,
        description="Total tax (sum of lines 16 and 17)",       
        page=1,
        line=18
    )
    line_19_child_tax_credit: float | None = Field(
        default=None,
        description="Child tax credit or credit for dependents from Schedule 8812",
        page=1,
        line=19
    )
    line_20_amount_from_schedule_3: float | None = Field(
        default=None,
        description="Amount from Schedule 3, line 8",
        page=1,
        line=20
    )
    line_21_add_lines_19_20: float | None = Field(
        default=None,
        description="Total credits (sum of lines 19 and 20)",
        page=1,
        line=21
    )
    line_22_subtract_21_from_18: float | None = Field(
        default=None,
        description="Tax after credits (line 18 minus line 21)",
        page=1,
        line=22
    )
    line_23_other_taxes: float | None = Field(
        default=None,
        description="Other taxes, including self-employment tax, from Schedule 2, line 21",
        page=1,
        line=23
    )
    line_24_total_tax: float | None = Field(
        default=None,
        description="Total tax (sum of lines 22 and 23)",
        page=1,
        line=24
    )
    line_25a_w2_withholding: float | None = Field(
        default=None,
        description="Federal income tax withheld from Form(s) W-2",
        page=1,
        line=25,
        box="a"
    )
    line_25b_1099_withholding: float | None = Field(
        default=None,
        description="Federal income tax withheld from Form(s) 1099",
        page=1,
        line=25,
        box="b"
    )
    line_25c_other_withholding: float | None = Field(
        default=None,
        description="Federal income tax withheld from other forms",
        page=1,
        line=25,
        box="c"
    )
    line_25d_total_withholding: float | None = Field(
        default=None,
        description="Total federal income tax withheld",
        page=1,
        line=25,
        box="d"
    )
    line_26_estimated_tax_payments: float | None = Field(
        default=None,
        description="2025 estimated tax payments and amount applied from 2024 return",
        page=1,
        line=26
    )
    line_27_earned_income_credit: float | None = Field(
        default=None,
        description="Earned income credit (EIC)",
        page=1,
        line=27,
        box="a"
    )
    line_33_total_payments: float | None = Field(
        default=None,
        description="Total payments (sum of lines 25d, 26, and 32)",
        page=1,
        line=33
    )
    line_34_overpayment: float | None = Field(
        default=None,
        description="Overpayment (line 33 minus line 24)",
        page=1,
        line=34
    )
    line_37_amount_owed: float | None = Field(
        default=None,
        description="Amount you owe (line 24 minus line 33)",
        page=1,
        line=37
    )


class Form1040(BaseTaxForm):
    """IRS Form 1040 - U.S. Individual Income Tax Return"""
    
    form_type: Literal["1040"] = "1040"
    page: int = 1
    
    header: Form1040Header = Field(
        default_factory=Form1040Header,
        description="Header section containing personal information and filing status",
        page=1
    )
    income: Form1040Income = Field(
        default_factory=Form1040Income,
        description="Income section containing all income sources",
        page=1
    )
    tax_payments: Form1040TaxPayments = Field(
        default_factory=Form1040TaxPayments,
        description="Tax and payments section containing tax calculations and payments",
        page=1
    )

    def get_line_fields(self) -> dict[str, str]:
        return {
            "income.line_11_adjusted_gross_income": "Line 11 (AGI)",
            "income.line_15_taxable_income": "Line 15 (Taxable Income)",
            "tax_payments.line_24_total_tax": "Line 24 (Total Tax)",
            "tax_payments.line_33_total_payments": "Line 33 (Total Payments)",
            "tax_payments.line_37_amount_owed": "Line 37 (Amount Owed)"
        }