from __future__ import annotations

from pydantic import BaseModel, Field

from tax_parser.schemas.base import BaseTaxForm, TaxpayerInfo


# ---------------------------------------------------------------------------
# Header / Entity Info
# ---------------------------------------------------------------------------

class Form1120Header(BaseModel):
    business_activity_code: str | None = Field(
        default=None,
        description="Business activity code (e.g., 000000 for general business)",
        page=1,
        box="a"
    )
    business_activity: str | None = Field(
        default=None,
        description="Description of business activity (e.g., manufacturing, retail, etc.)",
        page=1,
        box="b"
    )
    product_or_service: str | None = Field(
        default=None,
        description="Description of primary product or service",
        page=1,
        box="c"
    )
    date_incorporated: str | None = Field(
        default=None,
        description="Date of incorporation (MM/DD/YYYY)",
        page=1,
        box="d"
    )
    date_s_election_effective: str | None = Field(
        default=None,
        description="Date S election became effective (MM/DD/YYYY)",
        page=1,
        box="e"
    )
    accounting_method: str | None = Field(
        default=None,
        description="Accounting method used: cash | accrual | other",
        page=1,
        box="f"
    )
    number_of_shareholders: int | None = Field(
        default=None,
        description="Number of shareholders at end of tax year (if 100 or fewer)",
        page=1,
        box="g"
    )
    total_assets: float | None = Field(
        default=None,
        description="Total assets at end of tax year (from balance sheet)",
        page=1,
        box="h"
    )


# ---------------------------------------------------------------------------
# Income (Lines 1–6)
# ---------------------------------------------------------------------------

class Income(BaseModel):
    line_1a_gross_receipts: float | None = Field(
        default=None,
        description="Gross receipts or sales for the tax year",
        page=1,
        box="1a"
    )
    line_1b_returns_allowances: float | None = Field(
        default=None,
        description="Returns and allowances",
        page=1,
        box="1b"
    )
    line_1c_balance: float | None = Field(
        default=None,
        description="Balance (line 1a minus line 1b)",
        page=1,
        box="1c"
    )
    line_2_cost_of_goods_sold: float | None = Field(
        default=None,
        description="Cost of goods sold (must attach Form 1125-A)",
        page=1,
        box="2"
    )
    line_3_gross_profit: float | None = Field(
        default=None,
        description="Gross profit (line 1c minus line 2)",
        page=1,
        box="3"
    )
    line_4_net_gain_loss_form_4797: float | None = Field(
        default=None,
        description="Net gain or (loss) from Form 4797, Part II, line 17",
        page=1,
        box="4"
    )
    line_5_other_income_loss: float | None = Field(
        default=None,
        description="Other income (loss) (attach statement if necessary)",
        page=1,
        box="5"
    )
    line_6_total_income: float | None = Field(
        default=None,
        description="Total income (sum of lines 3 through 5)",
        page=1,
        box="6"
    )


# ---------------------------------------------------------------------------
# Deductions (Lines 7–20)
# ---------------------------------------------------------------------------

class Deductions(BaseModel):
    line_7_compensation_of_officers: float | None = Field(
        default=None,
        description="Compensation of officers (must attach Form 1125-E)",
        page=1,
        box="7"
    )
    line_8_salaries_wages: float | None = Field(
        default=None,
        description="Salaries and wages (less employment credits)",
        page=1,
        box="8"
    )
    line_9_repairs_maintenance: float | None = Field(
        default=None,
        description="Repairs and maintenance expenses",
        page=1,
        box="9"
    )
    line_10_bad_debts: float | None = Field(
        default=None,
        description="Bad debts (direct write-offs only)",
        page=1,
        box="10"
    )
    line_11_rents: float | None = Field(
        default=None,
        description="Rents paid (including real estate)",
        page=1,
        box="11"
    )
    line_12_taxes_licenses: float | None = Field(
        default=None,
        description="Taxes and licenses (state, local, foreign)",
        page=1,
        box="12"
    )
    line_13_interest: float | None = Field(
        default=None,
        description="Interest expense (see instructions for limitations)",
        page=1,
        box="13"
    )
    line_14_depreciation: float | None = Field(
        default=None,
        description="Depreciation (from Form 4562 not claimed elsewhere)",
        page=1,
        box="14"
    )
    line_15_depletion: float | None = Field(
        default=None,
        description="Depletion (natural resources)",
        page=1,
        box="15"
    )
    line_16_advertising: float | None = Field(
        default=None,
        description="Advertising expenses",
        page=1,
        box="16"
    )
    line_17_pension_profit_sharing: float | None = Field(
        default=None,
        description="Pension, profit-sharing, and other retirement plans",
        page=1,
        box="17"
    )
    line_18_employee_benefit_programs: float | None = Field(
        default=None,
        description="Employee benefit programs (health, insurance, etc.)",
        page=1,
        box="18"
    )
    line_19_other_deductions: float | None = Field(
        default=None,
        description="Other deductible expenses",
        page=1,
        box="19"
    )
    line_20_total_deductions: float | None = Field(
        default=None,
        description="Total deductions (sum of lines 7 through 19)",
        page=1,
        box="20"
    )


# ---------------------------------------------------------------------------
# Tax and Payments (Lines 21–27)
# ---------------------------------------------------------------------------

class TaxPayments(BaseModel):
    line_21_ordinary_business_income: float | None = Field(
        default=None,
        description="Ordinary business income (line 6 minus line 20)",
        page=1,
        box="21"
    )
    line_22a_excess_net_passive_income_tax: float | None = Field(
        default=None,
        description="Excess net passive income tax",
        page=1,
        box="22a"
    )
    line_22b_lifo_recapture_tax: float | None = Field(
        default=None,
        description="LIFO recapture tax",
        page=1,
        box="22b"
    )
    line_22c_total_tax: float | None = Field(
        default=None,
        description="Total tax (sum of lines 21, 22a, and 22b)",
        page=1,
        box="22c"
    )
    line_23a_estimated_tax_payments: float | None = Field(
        default=None,
        description="2025 estimated tax payments and amount applied from 2024 return",
        page=1,
        box="23a"
    )
    line_23b_tax_deposited_form_7004: float | None = Field(
        default=None,
        description="Tax deposited with Form 7004 (extension)",
        page=1,
        box="23b"
    )
    line_23c_credit_for_federal_tax_paid: float | None = Field(
        default=None,
        description="Credit for federal tax paid on undistributed capital gains",
        page=1,
        box="23c"
    )
    line_24_total_payments: float | None = Field(
        default=None,
        description="Total payments (sum of lines 23a, 23b, and 23c)",
        page=1,
        box="24"
    )
    line_25_estimated_tax_penalty: float | None = Field(
        default=None,
        description="Estimated tax penalty (check if Form 2220 is attached)",
        page=1,
        box="25"
    )
    line_26_amount_owed: float | None = Field(
        default=None,
        description="Amount owed (if line 24 is less than line 22c plus line 25)",
        page=1,
        box="26"
    )
    line_27_overpayment: float | None = Field(
        default=None,
        description="Overpayment (if line 24 is greater than line 22c plus line 25)",
        page=1,
        box="27"
    )


# ---------------------------------------------------------------------------
# Schedule B – Other Information
# ---------------------------------------------------------------------------

class ScheduleB(BaseModel):
    accounting_method: str | None = Field(
        default=None,
        description="Accounting method: Cash, Accrual, or Other (specify)",
        page=2,
        box="1"
    )
    business_activity: str | None = Field(
        default=None,
        description="Principal business activity",
        page=2,
        box="2"
    )
    product_or_service: str | None = Field(
        default=None,
        description="Principal product or service",
        page=2,
        box="3"
    )
    shareholder_owned_disregarded_entity: bool | None = Field(
        default=None,
        description="Check if any shareholder owns a disregarded entity",
        page=2,
        box="4"
    )
    owns_20_pct_or_more: bool | None = Field(
        default=None,
        description="Check if corporation owns 20% or more of another corporation",
        page=2,
        box="5"
    )
    owns_interest_in_partnership: bool | None = Field(
        default=None,
        description="Check if corporation owns interest in partnership",
        page=2,
        box="6"
    )
    outstanding_stock_restricted: bool | None = Field(
        default=None,
        description="Check if outstanding stock is restricted",
        page=2,
        box="7"
    )
    outstanding_stock_options: bool | None = Field(
        default=None,
        description="Check if outstanding stock options exist",
        page=2,
        box="8"
    )
    material_advisor_disclosure: bool | None = Field(
        default=None,
        description="Check if material advisor disclosure is required",
        page=2,
        box="9"
    )
    aggregated_activities: bool | None = Field(
        default=None,
        description="Check if aggregated activities",
        page=2,
        box="10"
    )
    election_section_163j: bool | None = Field(
        default=None,
        description="Check if election under section 163(j) made",
        page=2,
        box="11"
    )
    tax_shelter_registration: bool | None = Field(
        default=None,
        description="Check if tax shelter registration required",
        page=2,
        box="12"
    )
    receipts_less_than_250k: bool | None = Field(
        default=None,
        description="Check if gross receipts less than $250,000",
        page=2,
        box="13"
    )
    assets_less_than_250k: bool | None = Field(
        default=None,
        description="Check if total assets less than $250,000",
        page=2,
        box="14"
    )


# ---------------------------------------------------------------------------
# Schedule K – Shareholders' Pro Rata Share Items
# ---------------------------------------------------------------------------

class ScheduleK(BaseModel):
    # Income/Loss
    line_1_ordinary_business_income: float | None = Field(
        default=None,
        description="Ordinary business income (loss)",
        page=2,
        box="1"
    )
    line_2_net_rental_real_estate: float | None = Field(
        default=None,
        description="Net rental real estate income (loss)",
        page=2,
        box="2"
    )
    line_3_other_net_rental_income: float | None = Field(
        default=None,
        description="Other net rental income (loss)",
        page=2,
        box="3"
    )
    line_4_interest_income: float | None = Field(
        default=None,
        description="Interest income",
        page=2,
        box="4"
    )
    line_5a_ordinary_dividends: float | None = Field(
        default=None,
        description="Ordinary dividends",
        page=2,
        box="5a"
    )
    line_5b_qualified_dividends: float | None = Field(
        default=None,
        description="Qualified dividends",
        page=2,
        box="5b"
    )
    line_6_royalties: float | None = Field(
        default=None,
        description="Royalties",
        page=2,
        box="6"
    )
    line_7_net_short_term_capital_gain: float | None = Field(
        default=None,
        description="Net short-term capital gain (loss)",
        page=2,
        box="7"
    )
    line_8a_net_long_term_capital_gain: float | None = Field(
        default=None,
        description="Net long-term capital gain (loss)",
        page=2,
        box="8a"
    )
    line_8b_collectibles_gain: float | None = Field(
        default=None,
        description="Collectibles gain (loss)",
        page=2,
        box="8b"
    )
    line_8c_unrecaptured_section_1250_gain: float | None = Field(
        default=None,
        description="Unrecaptured section 1250 gain",
        page=2,
        box="8c"
    )
    line_9_net_section_1231_gain: float | None = Field(
        default=None,
        description="Net section 1231 gain (loss)",
        page=2,
        box="9"
    )
    line_10_other_income_loss: float | None = Field(
        default=None,
        description="Other income (loss)",
        page=2,
        box="10"
    )

    # Deductions
    line_11_section_179_deduction: float | None = Field(
        default=None,
        description="Section 179 deduction",
        page=2,
        box="11"
    )
    line_12a_charitable_contributions: float | None = Field(
        default=None,
        description="Charitable contributions",
        page=2,
        box="12a"
    )
    line_12b_investment_interest_expense: float | None = Field(
        default=None,
        description="Investment interest expense",
        page=2,
        box="12b"
    )
    line_12c_section_59e2_expenditures: float | None = Field(
        default=None,
        description="Section 59(e)(2) expenditures",
        page=2,
        box="12c"
    )
    line_12d_other_deductions: float | None = Field(
        default=None,
        description="Other deductions",
        page=2,
        box="12d"
    )

    # Credits
    line_13a_low_income_housing_credit: float | None = Field(
        default=None,
        description="Low-income housing credit",
        page=2,
        box="13a"
    )
    line_13b_low_income_housing_credit_other: float | None = Field(
        default=None,
        description="Low-income housing credit (other)",
        page=2,
        box="13b"
    )
    line_13c_qualified_rehabilitation_expenditures: float | None = Field(
        default=None,
        description="Qualified rehabilitation expenditures",
        page=2,
        box="13c"
    )
    line_13d_other_credits: float | None = Field(
        default=None,
        description="Other credits",
        page=2,
        box="13d"
    )

    # Foreign transactions
    line_14a_foreign_country: str | None = Field(
        default=None,
        description="Foreign country",
        page=2,
        box="14a"
    )
    line_14b_gross_income_foreign: float | None = Field(
        default=None,
        description="Gross income from foreign sources",
        page=2,
        box="14b"
    )
    line_14c_foreign_gross_income_deductions: float | None = Field(
        default=None,
        description="Deductions allocated to foreign gross income",
        page=2,
        box="14c"
    )
    line_14d_total_foreign_taxes: float | None = Field(
        default=None,
        description="Total foreign taxes paid or accrued",
        page=2,
        box="14d"
    )

    # AMT items
    line_15a_post_1986_depreciation: float | None = Field(
        default=None,
        description="Post-1986 depreciation adjustments",
        page=2,
        box="15a"
    )
    line_15b_adjusted_gain_loss: float | None = Field(
        default=None,
        description="Adjusted gain or loss",
        page=2,
        box="15b"
    )
    line_15c_depletion: float | None = Field(
        default=None,
        description="Depletion adjustments",
        page=2,
        box="15c"
    )
    line_15d_oil_gas_gross_income: float | None = Field(
        default=None,
        description="Oil and gas gross income",
        page=2,
        box="15d"
    )
    line_15e_other_amt_items: float | None = Field(
        default=None,
        description="Other alternative minimum tax items",
        page=2,
        box="15e"
    )

    # Other
    line_16a_tax_exempt_interest: float | None = Field(
        default=None,
        description="Tax-exempt interest",
        page=2,
        box="16a"
    )
    line_16b_other_tax_exempt_income: float | None = Field(
        default=None,
        description="Other tax-exempt income",
        page=2,
        box="16b"
    )
    line_16c_nondeductible_expenses: float | None = Field(
        default=None,
        description="Nondeductible expenses",
        page=2,
        box="16c"
    )
    line_16d_distributions: float | None = Field(
        default=None,
        description="Distributions (cash, stock, or property)",
        page=2,
        box="16d"
    )
    line_16e_repayment_of_loans: float | None = Field(
        default=None,
        description="Repayment of loans to shareholders",
        page=2,
        box="16e"
    )

    line_17_investment_income: float | None = Field(
        default=None,
        description="Investment income",
        page=2,
        box="17"
    )
    line_18_investment_expenses: float | None = Field(
        default=None,
        description="Investment expenses",
        page=2,
        box="18"
    )


# ---------------------------------------------------------------------------
# Schedule L – Balance Sheet per Books
# ---------------------------------------------------------------------------

class BalanceSheetLine(BaseModel):
    beginning_of_year: float | None = Field(
        default=None,
        description="Beginning of year balance",
        page=3,
        box="beginning"
    )
    end_of_year: float | None = Field(
        default=None,
        description="End of year balance",
        page=3,
        box="end"
    )


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
    line_1_net_income_per_books: float | None = Field(
        default=None,
        description="Net income (loss) per books",
        page=3,
        box="1"
    )
    line_2_income_on_schedule_k: float | None = Field(
        default=None,
        description="Income reported on Schedule K",
        page=3,
        box="2"
    )
    line_3_expenses_on_books_not_on_k: float | None = Field(
        default=None,
        description="Expenses on books not on Schedule K",
        page=3,
        box="3"
    )
    line_3a_depreciation: float | None = Field(
        default=None,
        description="Depreciation",
        page=3,
        box="3a"
    )
    line_3b_travel_entertainment: float | None = Field(
        default=None,
        description="Travel and entertainment",
        page=3,
        box="3b"
    )
    line_4_add_lines_1_through_3: float | None = Field(
        default=None,
        description="Total (sum of lines 1 through 3)",
        page=3,
        box="4"
    )
    line_5_income_on_books_not_on_k: float | None = Field(
        default=None,
        description="Income on books not on Schedule K",
        page=3,
        box="5"
    )
    line_5a_tax_exempt_interest: float | None = Field(
        default=None,
        description="Tax-exempt interest",
        page=3,
        box="5a"
    )
    line_6_deductions_on_k_not_on_books: float | None = Field(
        default=None,
        description="Deductions on Schedule K not on books",
        page=3,
        box="6"
    )
    line_6a_depreciation: float | None = Field(
        default=None,
        description="Depreciation",
        page=3,
        box="6a"
    )
    line_7_add_lines_5_and_6: float | None = Field(
        default=None,
        description="Total (sum of lines 5 and 6)",
        page=3,
        box="7"
    )
    line_8_income_loss: float | None = Field(
        default=None,
        description="Income (loss) (line 4 minus line 7)",
        page=3,
        box="8"
    )


# ---------------------------------------------------------------------------
# Schedule M-2 – Analysis of AAA, Shareholders' Equity, etc.
# ---------------------------------------------------------------------------

class ScheduleM2Column(BaseModel):
    balance_beginning: float | None = Field(
        default=None,
        description="Balance at beginning of year",
        page=3,
        box="beginning"
    )
    ordinary_income: float | None = Field(
        default=None,
        description="Ordinary income",
        page=3,
        box="ordinary"
    )
    other_additions: float | None = Field(
        default=None,
        description="Other additions",
        page=3,
        box="additions"
    )
    loss_from_page1: float | None = Field(
        default=None,
        description="Loss from page 1",
        page=3,
        box="loss"
    )
    other_reductions: float | None = Field(
        default=None,
        description="Other reductions",
        page=3,
        box="reductions"
    )
    combine_lines_1_through_5: float | None = Field(
        default=None,
        description="Combined total of lines 1 through 5",
        page=3,
        box="combined"
    )
    distributions: float | None = Field(
        default=None,
        description="Distributions",
        page=3,
        box="distributions"
    )
    balance_end_of_year: float | None = Field(
        default=None,
        description="Balance at end of year",
        page=3,
        box="end"
    )


class ScheduleM2(BaseModel):
    accumulated_adjustments: ScheduleM2Column = ScheduleM2Column()
    other_adjustments: ScheduleM2Column = ScheduleM2Column()
    shareholders_undistributed_taxable_income: ScheduleM2Column = ScheduleM2Column()
    accumulated_earnings_profits: ScheduleM2Column = ScheduleM2Column()


# ---------------------------------------------------------------------------
# Top-level Form 1120-S
# ---------------------------------------------------------------------------

class Form1120(BaseTaxForm):
    """Complete IRS Form 1120 schema."""

    form_type: Literal["1120"] = "1120"

    header: Form1120Header = Form1120Header()
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