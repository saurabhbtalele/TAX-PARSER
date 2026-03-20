from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm, Address


# ------------------------------------------------------------------
# Part I – Information About the Corporation
# ------------------------------------------------------------------
class EntityInfo(BaseModel):
    """Part I - Information About the Corporation"""
    
    ein: str | None = Field(
        default=None,
        description="Corporation's employer identification number (Box A)"
    )
    name: str | None = Field(
        default=None,
        description="Corporation's name (Box B)"
    )
    address: Address = Field(
        default_factory=Address,
        description="Corporation's address, city, state, and ZIP code (Box B)"
    )
    irs_center: str | None = Field(
        default=None,
        description="IRS Center where corporation filed return (Box C)"
    )
    total_shares_beginning: int | None = Field(
        default=None,
        description="Corporation's total number of shares - Beginning of tax year (Box D)"
    )
    total_shares_ending: int | None = Field(
        default=None,
        description="Corporation's total number of shares - End of tax year (Box D)"
    )


# ------------------------------------------------------------------
# Part II – Information About the Shareholder
# ------------------------------------------------------------------
class ShareholderInfo(BaseModel):
    """Part II - Information About the Shareholder"""
    
    ssn_or_ein: str | None = Field(
        default=None,
        description="Shareholder's identifying number (Box E)"
    )
    name: str | None = Field(
        default=None,
        description="Shareholder's name (Box F)"
    )
    address: Address = Field(
        default_factory=Address,
        description="Shareholder's address, city, state, and ZIP code (Box F)"
    )
    allocation_percentage: float | None = Field(
        default=None,
        description="Current year allocation percentage (Box G) - e.g., 25.0 for 25%"
    )
    shares_beginning: int | None = Field(
        default=None,
        description="Shareholder's number of shares - Beginning of tax year (Box H)"
    )
    shares_ending: int | None = Field(
        default=None,
        description="Shareholder's number of shares - End of tax year (Box H)"
    )
    shareholder_loan_balance_beginning: float | None = Field(
        default=None,
        description="Loans from shareholder - Beginning of tax year (Box I)"
    )
    shareholder_loan_balance_ending: float | None = Field(
        default=None,
        description="Loans from shareholder - End of tax year (Box I)"
    )
    is_shareholder_final_return: bool | None = Field(
        default=None,
        description="Indicates if this is the shareholder's final return"
    )
    shareholder_type: str | None = Field(
        default=None,
        description="Shareholder type (e.g., 'individual', 'corporation')"
    )


# ------------------------------------------------------------------
# Part III – Shareholder’s Share of Income, Deductions, Credits, etc.
# ------------------------------------------------------------------

class K1IncomeDeductions(BaseModel):
    """Part III - Lines 1-13 (numeric items)"""
    
    line_1_ordinary_business_income: float | None = Field(
        default=None,
        description="Ordinary business income(loss) (Line 1)"
    )
    line_2_net_rental_real_estate: float | None = Field(
        default=None,
        description="Net rental real estate income(loss) (Line 2)"
    )
    line_3_other_net_rental_income: float | None = Field(
        default=None,
        description="Other net rental income(loss) (Line 3)"
    )
    line_4_interest_income: float | None = Field(
        default=None,
        description="Interest income (Line 4)"
    )
    line_5a_ordinary_dividends: float | None = Field(
        default=None,
        description="Ordinary dividends (Line 5a)"
    )
    line_5b_qualified_dividends: float | None = Field(
        default=None,
        description="Qualified dividends (Line 5b)"
    )
    line_6_royalties: float | None = Field(
        default=None,
        description="Royalties (Line 6)"
    )
    line_7_net_short_term_capital_gain: float | None = Field(
        default=None,
        description="Net short-term capital gain(loss) (Line 7)"
    )
    line_8a_net_long_term_capital_gain: float | None = Field(
        default=None,
        description="Net long-term capital gain(loss) (Line 8a)"
    )
    line_8b_collectibles_gain: float | None = Field(
        default=None,
        description="Collectibles(28%) gain(loss) (Line 8b)"
    )
    line_8c_unrecaptured_section_1250: float | None = Field(
        default=None,
        description="Unrecaptured section 1250 gain (Line 8c)"
    )
    line_9_net_section_1231_gain: float | None = Field(
        default=None,
        description="Net section 1231 gain(loss) (Line 9)"
    )
    line_10_other_income_loss: float | None = Field(
        default=None,
        description="Other income(loss) (Line 10)"
    )
    line_11_section_179_deduction: float | None = Field(
        default=None,
        description="Section 179 deduction (Line 11)"
    )
    line_12_other_deductions: float | None = Field(
        default=None,
        description="Other deductions (Line 12)"
    )
    line_13_credits: float | None = Field(
        default=None,
        description="Credits (Line 13)"
    )


class K1AMTItems(BaseModel):
    """Part III - Line 15 – Alternative Minimum Tax (AMT) Items"""
    
    line_15_post_1986_depreciation: float | None = Field(
        default=None,
        description="Post-1986 depreciation (Line 15)"
    )
    line_15_adjusted_gain_loss: float | None = Field(
        default=None,
        description="Adjusted gain or loss (Line 15)"
    )
    line_15_depletion: float | None = Field(
        default=None,
        description="Depletion (Line 15)"
    )
    line_15_oil_gas_gross_income: float | None = Field(
        default=None,
        description="Oil and gas gross income (Line 15)"
    )
    line_15_other_amt_items: float | None = Field(
        default=None,
        description="Other AMT items (Line 15)"
    )


class K1BasisItems(BaseModel):
    """Part III - Line 16 – Items Affecting Shareholder Basis"""
    
    line_16a_increase_from_income: float | None = Field(
        default=None,
        description="Increase from income (Line 16)"
    )
    line_16b_decrease_from_distributions: float | None = Field(
        default=None,
        description="Decrease from distributions (Line 16)"
    )
    line_16c_decrease_from_loss_deductions: float | None = Field(
        default=None,
        description="Decrease from loss deductions (Line 16)"
    )
    line_16d_decrease_from_nondeductible_expenses: float | None = Field(
        default=None,
        description="Decrease from nondeductible expenses (Line 16)"
    )
    line_16e_other_basis_adjustments: float | None = Field(
        default=None,
        description="Other basis adjustments (Line 16)"
    )


class K1OtherInfo(BaseModel):
    """Part III - Line 17 – Other Information"""
    
    line_17_other_information: str | None = Field(
        default=None,
        description="Other information (Line 17)"
    )


class K1ForeignTransactions(BaseModel):
    """Part III - Foreign transactions statement items"""
    
    line_16a_foreign_country: str | None = Field(
        default=None,
        description="Foreign country (Line 16a)"
    )
    line_16b_foreign_gross_income: float | None = Field(
        default=None,
        description="Foreign gross income (Line 16b)"
    )
    line_16c_foreign_deductions: float | None = Field(
        default=None,
        description="Foreign deductions (Line 16c)"
    )
    line_16d_total_foreign_taxes: float | None = Field(
        default=None,
        description="Total foreign taxes (Line 16d)"
    )
    line_16e_reduction_in_taxes: float | None = Field(
        default=None,
        description="Reduction in taxes (Line 16e)"
    )


# ------------------------------------------------------------------
# Top-level Schedule K-1 (S-Corp)
# ------------------------------------------------------------------
class ScheduleK1SCorp(BaseTaxForm):
    """
    Schedule K-1 (Form 1120-S) 2023 — Shareholder's Share of Income, Deductions, Credits, and Other Items
    """
    
    form_type: Literal["Schedule K-1 (S-Corp)"] = "Schedule K-1 (S-Corp)"

    # Part I
    entity: EntityInfo = Field(
        default_factory=EntityInfo,
        description="Part I - Information About the Corporation"
    )

    # Part II
    shareholder: ShareholderInfo = Field(
        default_factory=ShareholderInfo,
        description="Part II - Information About the Shareholder"
    )

    # Part III — Core numeric lines
    income_deductions: K1IncomeDeductions = Field(
        default_factory=K1IncomeDeductions,
        description="Part III - Lines 1-13 (numeric items)"
    )
    amt_items: K1AMTItems = Field(
        default_factory=K1AMTItems,
        description="Part III - Line 15 (AMT Items)"
    )
    basis_items: K1BasisItems = Field(
        default_factory=K1BasisItems,
        description="Part III - Line 16 (Items Affecting Shareholder Basis)"
    )
    other: K1OtherInfo = Field(
        default_factory=K1OtherInfo,
        description="Part III - Line 17 (Other Information)"
    )

    # Optional foreign
    foreign_transactions: K1ForeignTransactions = Field(
        default_factory=K1ForeignTransactions,
        description="Part III - Foreign transactions statement items"
    )

    # Special flags (bottom of form)
    k3_attached: bool | None = Field(
        default=None,
        description="Schedule K-3 is attached if checked (Line 14)"
    )
    line_18_risk_multiple_activities: bool | None = Field(
        default=None,
        description="More than one activity for at-risk purposes (Line 18)"
    )
    line_19_passive_multiple_activities: bool | None = Field(
        default=None,
        description="More than one activity for passive activity purposes (Line 19)"
    )

    # Metadata
    is_final_k1: bool | None = Field(
        default=None,
        description="Indicates if this is a Final K-1 (from form header)"
    )
    is_amended_k1: bool | None = Field(
        default=None,
        description="Indicates if this is an Amended K-1 (from form header)"
    )