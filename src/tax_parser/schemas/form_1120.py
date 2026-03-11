"""Schema for IRS Form 1120 – U.S. Corporation Income Tax Return."""

from __future__ import annotations

from pydantic import BaseModel, Field

from tax_parser.schemas.base import BaseTaxForm


class Form1120Header(BaseModel):
    business_activity_code: str | None = None
    date_incorporated: str | None = None
    accounting_method: str | None = None
    total_assets: float | None = None
    consolidated_return: bool | None = None
    personal_holding_company: bool | None = None
    schedule_m3_attached: bool | None = None


class Form1120Income(BaseModel):
    line_1a_gross_receipts: float | None = None
    line_1b_returns_allowances: float | None = None
    line_1c_balance: float | None = None
    line_2_cost_of_goods_sold: float | None = None
    line_3_gross_profit: float | None = None
    line_4_dividends: float | None = None
    line_5_interest: float | None = None
    line_6_gross_rents: float | None = None
    line_7_gross_royalties: float | None = None
    line_8_capital_gain: float | None = None
    line_9_net_gain_loss_4797: float | None = None
    line_10_other_income: float | None = None
    line_11_total_income: float | None = None


class Form1120Deductions(BaseModel):
    line_12_compensation_of_officers: float | None = None
    line_13_salaries_wages: float | None = None
    line_14_repairs_maintenance: float | None = None
    line_15_bad_debts: float | None = None
    line_16_rents: float | None = None
    line_17_taxes_licenses: float | None = None
    line_18_interest: float | None = None
    line_19_charitable_contributions: float | None = None
    line_20_depreciation_form_4562: float | None = None
    line_21_depletion: float | None = None
    line_22_advertising: float | None = None
    line_23_pension_profit_sharing: float | None = None
    line_24_employee_benefit_programs: float | None = None
    line_25_domestic_production_activities: float | None = None
    line_26_other_deductions: float | None = None
    line_27_total_deductions: float | None = None


class Form1120TaxPayments(BaseModel):
    line_28_taxable_income_before_nol: float | None = None
    line_29a_nol_deduction: float | None = None
    line_29b_special_deductions: float | None = None
    line_30_taxable_income: float | None = None
    line_31_total_tax: float | None = None
    line_32_total_payments_credits: float | None = None
    line_33_estimated_tax_penalty: float | None = None
    line_34_amount_owed: float | None = None
    line_35_overpayment: float | None = None


class Form1120ScheduleC(BaseModel):
    """Schedule C – Dividends, Inclusions, and Special Deductions."""
    dividends_domestic_corporations: float | None = None
    dividends_foreign_corporations: float | None = None
    total_dividends: float | None = None
    total_special_deductions: float | None = None


class Form1120ScheduleJ(BaseModel):
    """Schedule J – Tax Computation and Payment."""
    line_1_check_box_member_controlled_group: bool | None = None
    line_2_income_tax: float | None = None
    line_3_alternative_minimum_tax: float | None = None
    line_4_total_tax: float | None = None
    line_5a_prior_year_overpayment_credited: float | None = None
    line_5b_estimated_tax_payments: float | None = None
    line_5c_tax_deposited_form_7004: float | None = None
    line_5d_credits: float | None = None


class Form1120(BaseTaxForm):
    """Complete IRS Form 1120 schema."""

    form_type: str = "1120"

    header: Form1120Header = Form1120Header()
    income: Form1120Income = Form1120Income()
    deductions: Form1120Deductions = Form1120Deductions()
    tax_payments: Form1120TaxPayments = Form1120TaxPayments()
    schedule_c: Form1120ScheduleC = Form1120ScheduleC()
    schedule_j: Form1120ScheduleJ = Form1120ScheduleJ()

    def get_line_fields(self) -> dict[str, str]:
        return {
            "income.line_11_total_income": "Page 1, Line 11",
            "deductions.line_27_total_deductions": "Page 1, Line 27",
            "tax_payments.line_30_taxable_income": "Page 1, Line 30",
        }
