"""Schema for IRS Form 1120-S – U.S. Income Tax Return for an S Corporation."""

from __future__ import annotations

from pydantic import BaseModel, Field

from tax_parser.schemas.base import BaseTaxForm, TaxpayerInfo


# ---------------------------------------------------------------------------
# Header / Entity Info
# ---------------------------------------------------------------------------

class Form1120SHeader(BaseModel):
    business_activity_code: str | None = None
    business_activity: str | None = None
    product_or_service: str | None = None
    date_incorporated: str | None = None
    date_s_election_effective: str | None = None
    accounting_method: str | None = Field(
        default=None, description="cash | accrual | other"
    )
    number_of_shareholders: int | None = None
    total_assets: float | None = None


# ---------------------------------------------------------------------------
# Income (Lines 1–6)
# ---------------------------------------------------------------------------

class Income(BaseModel):
    line_1a_gross_receipts: float | None = None
    line_1b_returns_allowances: float | None = None
    line_1c_balance: float | None = None
    line_2_cost_of_goods_sold: float | None = None
    line_3_gross_profit: float | None = None
    line_4_net_gain_loss_form_4797: float | None = None
    line_5_other_income_loss: float | None = None
    line_6_total_income: float | None = None


# ---------------------------------------------------------------------------
# Deductions (Lines 7–20)
# ---------------------------------------------------------------------------

class Deductions(BaseModel):
    line_7_compensation_of_officers: float | None = None
    line_8_salaries_wages: float | None = None
    line_9_repairs_maintenance: float | None = None
    line_10_bad_debts: float | None = None
    line_11_rents: float | None = None
    line_12_taxes_licenses: float | None = None
    line_13_interest: float | None = None
    line_14_depreciation: float | None = None
    line_15_depletion: float | None = None
    line_16_advertising: float | None = None
    line_17_pension_profit_sharing: float | None = None
    line_18_employee_benefit_programs: float | None = None
    line_19_other_deductions: float | None = None
    line_20_total_deductions: float | None = None


# ---------------------------------------------------------------------------
# Tax and Payments (Lines 21–27)
# ---------------------------------------------------------------------------

class TaxPayments(BaseModel):
    line_21_ordinary_business_income: float | None = None
    line_22a_excess_net_passive_income_tax: float | None = None
    line_22b_lifo_recapture_tax: float | None = None
    line_22c_total_tax: float | None = None
    line_23a_estimated_tax_payments: float | None = None
    line_23b_tax_deposited_form_7004: float | None = None
    line_23c_credit_for_federal_tax_paid: float | None = None
    line_24_total_payments: float | None = None
    line_25_estimated_tax_penalty: float | None = None
    line_26_amount_owed: float | None = None
    line_27_overpayment: float | None = None


# ---------------------------------------------------------------------------
# Schedule B – Other Information
# ---------------------------------------------------------------------------

class ScheduleB(BaseModel):
    accounting_method: str | None = None
    business_activity: str | None = None
    product_or_service: str | None = None
    shareholder_owned_disregarded_entity: bool | None = None
    owns_20_pct_or_more: bool | None = None
    owns_interest_in_partnership: bool | None = None
    outstanding_stock_restricted: bool | None = None
    outstanding_stock_options: bool | None = None
    material_advisor_disclosure: bool | None = None
    aggregated_activities: bool | None = None
    election_section_163j: bool | None = None
    tax_shelter_registration: bool | None = None
    receipts_less_than_250k: bool | None = None
    assets_less_than_250k: bool | None = None


# ---------------------------------------------------------------------------
# Schedule K – Shareholders' Pro Rata Share Items
# ---------------------------------------------------------------------------

class ScheduleK(BaseModel):
    # Income/Loss
    line_1_ordinary_business_income: float | None = None
    line_2_net_rental_real_estate: float | None = None
    line_3_other_net_rental_income: float | None = None
    line_4_interest_income: float | None = None
    line_5a_ordinary_dividends: float | None = None
    line_5b_qualified_dividends: float | None = None
    line_6_royalties: float | None = None
    line_7_net_short_term_capital_gain: float | None = None
    line_8a_net_long_term_capital_gain: float | None = None
    line_8b_collectibles_gain: float | None = None
    line_8c_unrecaptured_section_1250_gain: float | None = None
    line_9_net_section_1231_gain: float | None = None
    line_10_other_income_loss: float | None = None

    # Deductions
    line_11_section_179_deduction: float | None = None
    line_12a_charitable_contributions: float | None = None
    line_12b_investment_interest_expense: float | None = None
    line_12c_section_59e2_expenditures: float | None = None
    line_12d_other_deductions: float | None = None

    # Credits
    line_13a_low_income_housing_credit: float | None = None
    line_13b_low_income_housing_credit_other: float | None = None
    line_13c_qualified_rehabilitation_expenditures: float | None = None
    line_13d_other_credits: float | None = None

    # Foreign transactions
    line_14a_foreign_country: str | None = None
    line_14b_gross_income_foreign: float | None = None
    line_14c_foreign_gross_income_deductions: float | None = None
    line_14d_total_foreign_taxes: float | None = None

    # AMT items
    line_15a_post_1986_depreciation: float | None = None
    line_15b_adjusted_gain_loss: float | None = None
    line_15c_depletion: float | None = None
    line_15d_oil_gas_gross_income: float | None = None
    line_15e_other_amt_items: float | None = None

    # Other
    line_16a_tax_exempt_interest: float | None = None
    line_16b_other_tax_exempt_income: float | None = None
    line_16c_nondeductible_expenses: float | None = None
    line_16d_distributions: float | None = None
    line_16e_repayment_of_loans: float | None = None

    line_17_investment_income: float | None = None
    line_18_investment_expenses: float | None = None


# ---------------------------------------------------------------------------
# Schedule L – Balance Sheet per Books
# ---------------------------------------------------------------------------

class BalanceSheetLine(BaseModel):
    beginning_of_year: float | None = None
    end_of_year: float | None = None


class ScheduleL(BaseModel):
    # Assets
    cash: BalanceSheetLine = BalanceSheetLine()
    trade_notes_receivable: BalanceSheetLine = BalanceSheetLine()
    less_allowance_bad_debts: BalanceSheetLine = BalanceSheetLine()
    inventories: BalanceSheetLine = BalanceSheetLine()
    us_government_obligations: BalanceSheetLine = BalanceSheetLine()
    tax_exempt_securities: BalanceSheetLine = BalanceSheetLine()
    other_current_assets: BalanceSheetLine = BalanceSheetLine()
    loans_to_shareholders: BalanceSheetLine = BalanceSheetLine()
    mortgage_loans: BalanceSheetLine = BalanceSheetLine()
    other_investments: BalanceSheetLine = BalanceSheetLine()
    buildings_depreciable_assets: BalanceSheetLine = BalanceSheetLine()
    less_accumulated_depreciation: BalanceSheetLine = BalanceSheetLine()
    depletable_assets: BalanceSheetLine = BalanceSheetLine()
    less_accumulated_depletion: BalanceSheetLine = BalanceSheetLine()
    land: BalanceSheetLine = BalanceSheetLine()
    intangible_assets: BalanceSheetLine = BalanceSheetLine()
    less_accumulated_amortization: BalanceSheetLine = BalanceSheetLine()
    other_assets: BalanceSheetLine = BalanceSheetLine()
    total_assets: BalanceSheetLine = BalanceSheetLine()

    # Liabilities & Equity
    accounts_payable: BalanceSheetLine = BalanceSheetLine()
    mortgages_notes_payable_lt1yr: BalanceSheetLine = BalanceSheetLine()
    other_current_liabilities: BalanceSheetLine = BalanceSheetLine()
    loans_from_shareholders: BalanceSheetLine = BalanceSheetLine()
    mortgages_notes_payable_gt1yr: BalanceSheetLine = BalanceSheetLine()
    other_liabilities: BalanceSheetLine = BalanceSheetLine()
    capital_stock: BalanceSheetLine = BalanceSheetLine()
    additional_paid_in_capital: BalanceSheetLine = BalanceSheetLine()
    retained_earnings: BalanceSheetLine = BalanceSheetLine()
    adjustments_to_shareholders_equity: BalanceSheetLine = BalanceSheetLine()
    less_cost_treasury_stock: BalanceSheetLine = BalanceSheetLine()
    total_liabilities_equity: BalanceSheetLine = BalanceSheetLine()


# ---------------------------------------------------------------------------
# Schedule M-1 – Reconciliation of Income
# ---------------------------------------------------------------------------

class ScheduleM1(BaseModel):
    line_1_net_income_per_books: float | None = None
    line_2_income_on_schedule_k: float | None = None
    line_3_expenses_on_books_not_on_k: float | None = None
    line_3a_depreciation: float | None = None
    line_3b_travel_entertainment: float | None = None
    line_4_add_lines_1_through_3: float | None = None
    line_5_income_on_books_not_on_k: float | None = None
    line_5a_tax_exempt_interest: float | None = None
    line_6_deductions_on_k_not_on_books: float | None = None
    line_6a_depreciation: float | None = None
    line_7_add_lines_5_and_6: float | None = None
    line_8_income_loss: float | None = None


# ---------------------------------------------------------------------------
# Schedule M-2 – Analysis of AAA, Shareholders' Equity, etc.
# ---------------------------------------------------------------------------

class ScheduleM2Column(BaseModel):
    balance_beginning: float | None = None
    ordinary_income: float | None = None
    other_additions: float | None = None
    loss_from_page1: float | None = None
    other_reductions: float | None = None
    combine_lines_1_through_5: float | None = None
    distributions: float | None = None
    balance_end_of_year: float | None = None


class ScheduleM2(BaseModel):
    accumulated_adjustments: ScheduleM2Column = ScheduleM2Column()
    other_adjustments: ScheduleM2Column = ScheduleM2Column()
    shareholders_undistributed_taxable_income: ScheduleM2Column = ScheduleM2Column()
    accumulated_earnings_profits: ScheduleM2Column = ScheduleM2Column()


# ---------------------------------------------------------------------------
# Top-level Form 1120-S
# ---------------------------------------------------------------------------

class Form1120S(BaseTaxForm):
    """Complete IRS Form 1120-S schema."""

    form_type: str = "1120-S"

    header: Form1120SHeader = Form1120SHeader()
    income: Income = Income()
    deductions: Deductions = Deductions()
    tax_payments: TaxPayments = TaxPayments()
    schedule_b: ScheduleB = ScheduleB()
    schedule_k: ScheduleK = ScheduleK()
    schedule_l: ScheduleL = ScheduleL()
    schedule_m1: ScheduleM1 = ScheduleM1()
    schedule_m2: ScheduleM2 = ScheduleM2()

    def get_line_fields(self) -> dict[str, str]:
        return {
            "income.line_6_total_income": "Page 1, Line 6",
            "deductions.line_20_total_deductions": "Page 1, Line 20",
            "tax_payments.line_21_ordinary_business_income": "Page 1, Line 21",
            "schedule_k.line_1_ordinary_business_income": "Schedule K, Line 1",
        }
