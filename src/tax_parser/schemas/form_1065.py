"""Schema for IRS Form 1065 – U.S. Return of Partnership Income."""

from __future__ import annotations

from pydantic import BaseModel

from tax_parser.schemas.base import BaseTaxForm


class Form1065Header(BaseModel):
    business_activity_code: str | None = None
    business_activity: str | None = None
    product_or_service: str | None = None
    date_business_started: str | None = None
    accounting_method: str | None = None
    number_of_schedules_k1: int | None = None
    partnership_type: str | None = None
    total_assets: float | None = None


class Form1065Income(BaseModel):
    line_1a_gross_receipts: float | None = None
    line_1b_returns_allowances: float | None = None
    line_1c_balance: float | None = None
    line_2_cost_of_goods_sold: float | None = None
    line_3_gross_profit: float | None = None
    line_4_ordinary_income_from_other: float | None = None
    line_5_net_farm_profit: float | None = None
    line_6_net_gain_loss_form_4797: float | None = None
    line_7_other_income_loss: float | None = None
    line_8_total_income: float | None = None


class Form1065Deductions(BaseModel):
    line_9_salaries_wages: float | None = None
    line_10_guaranteed_payments: float | None = None
    line_11_repairs_maintenance: float | None = None
    line_12_bad_debts: float | None = None
    line_13_rent: float | None = None
    line_14_taxes_licenses: float | None = None
    line_15_interest: float | None = None
    line_16a_depreciation: float | None = None
    line_16b_less_included_cogs: float | None = None
    line_16c_net_depreciation: float | None = None
    line_17_depletion: float | None = None
    line_18_retirement_plans: float | None = None
    line_19_employee_benefit_programs: float | None = None
    line_20_other_deductions: float | None = None
    line_21_total_deductions: float | None = None
    line_22_ordinary_business_income: float | None = None


class Form1065ScheduleK(BaseModel):
    """Schedule K – Partners' Distributive Share Items."""
    line_1_ordinary_business_income: float | None = None
    line_2_net_rental_real_estate: float | None = None
    line_3_other_net_rental_income: float | None = None
    line_4_guaranteed_payments: float | None = None
    line_5_interest_income: float | None = None
    line_6a_ordinary_dividends: float | None = None
    line_6b_qualified_dividends: float | None = None
    line_7_royalties: float | None = None
    line_8_net_short_term_capital_gain: float | None = None
    line_9a_net_long_term_capital_gain: float | None = None
    line_10_net_section_1231_gain: float | None = None
    line_11_other_income_loss: float | None = None
    line_12_section_179_deduction: float | None = None
    line_13a_charitable_contributions: float | None = None
    line_13b_investment_interest_expense: float | None = None
    line_13d_other_deductions: float | None = None
    line_14a_net_earnings_self_employment: float | None = None
    line_14b_gross_farming_income: float | None = None
    line_14c_gross_nonfarm_income: float | None = None

    # Foreign transactions
    line_16a_foreign_country: str | None = None
    line_16b_foreign_gross_income: float | None = None
    line_16c_foreign_deductions: float | None = None
    line_16d_total_foreign_taxes: float | None = None

    # AMT
    line_17a_post_1986_depreciation: float | None = None
    line_17b_adjusted_gain_loss: float | None = None
    line_17c_depletion: float | None = None

    # Distributions
    line_19a_distributions_cash: float | None = None
    line_19b_distributions_property: float | None = None


class Form1065ScheduleL(BaseModel):
    """Schedule L – Balance Sheets per Books (simplified)."""

    class BalanceLine(BaseModel):
        beginning: float | None = None
        ending: float | None = None

    total_assets: BalanceLine = BalanceLine()
    total_liabilities: BalanceLine = BalanceLine()
    partners_capital: BalanceLine = BalanceLine()


class Form1065(BaseTaxForm):
    """Complete IRS Form 1065 schema."""

    form_type: str = "1065"

    header: Form1065Header = Form1065Header()
    income: Form1065Income = Form1065Income()
    deductions: Form1065Deductions = Form1065Deductions()
    schedule_k: Form1065ScheduleK = Form1065ScheduleK()
    schedule_l: Form1065ScheduleL = Form1065ScheduleL()

    def get_line_fields(self) -> dict[str, str]:
        return {
            "income.line_8_total_income": "Page 1, Line 8",
            "deductions.line_21_total_deductions": "Page 1, Line 21",
            "deductions.line_22_ordinary_business_income": "Page 1, Line 22",
        }
