from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm, Address


# ------------------------------------------------------------------
# Part I – Information About the Corporation
# ------------------------------------------------------------------
class EntityInfo(BaseModel):
    ein: str | None = None
    name: str | None = None
    address: Address = Address()
    irs_center: str | None = None
    total_shares_beginning: int | None = None   # Line D (Part I)
    total_shares_ending: int | None = None     # Line D (Part I)


# ------------------------------------------------------------------
# Part II – Information About the Shareholder
# ------------------------------------------------------------------
class ShareholderInfo(BaseModel):
    ssn_or_ein: str | None = None               # Line E
    name: str | None = None                     # Line F
    address: Address = Address()                # Line F
    allocation_percentage: float | None = None  # Line G (% — e.g., 25.0 for 25%)
    shares_beginning: int | None = None         # Line H (beginning shares)
    shares_ending: int | None = None            # Line H (ending shares)
    shareholder_loan_balance_beginning: float | None = None  # Line I
    shareholder_loan_balance_ending: float | None = None    # Line I
    is_shareholder_final_return: bool | None = None
    shareholder_type: str | None = None         # e.g., "individual", "corporation"


# ------------------------------------------------------------------
# Part III – Shareholder’s Share of Income, Deductions, Credits, etc.
# ------------------------------------------------------------------

class K1IncomeDeductions(BaseModel):
    """Lines 1–13 (numeric items)"""
    line_1_ordinary_business_income: float | None = None          # Line 1
    line_2_net_rental_real_estate: float | None = None           # Line 2
    line_3_other_net_rental_income: float | None = None          # Line 3
    line_4_interest_income: float | None = None                  # Line 4
    line_5a_ordinary_dividends: float | None = None              # Line 5a
    line_5b_qualified_dividends: float | None = None             # Line 5b
    line_6_royalties: float | None = None                        # Line 6
    line_7_net_short_term_capital_gain: float | None = None      # Line 7
    line_8a_net_long_term_capital_gain: float | None = None      # Line 8a
    line_8b_collectibles_gain: float | None = None               # Line 8b
    line_8c_unrecaptured_section_1250: float | None = None       # Line 8c
    line_9_net_section_1231_gain: float | None = None            # Line 9
    line_10_other_income_loss: float | None = None               # Line 10
    line_11_section_179_deduction: float | None = None           # Line 11
    line_12_other_deductions: float | None = None                # Line 12
    line_13_credits: float | None = None                         # Line 13


class K1AMTItems(BaseModel):
    """Line 15 – Alternative Minimum Tax (AMT) Items"""
    line_15_post_1986_depreciation: float | None = None
    line_15_adjusted_gain_loss: float | None = None
    line_15_depletion: float | None = None
    line_15_oil_gas_gross_income: float | None = None
    line_15_other_amt_items: float | None = None


class K1BasisItems(BaseModel):
    """Line 16 – Items Affecting Shareholder Basis"""
    line_16a_increase_from_income: float | None = None
    line_16b_decrease_from_distributions: float | None = None
    line_16c_decrease_from_loss_deductions: float | None = None
    line_16d_decrease_from_nondeductible_expenses: float | None = None
    line_16e_other_basis_adjustments: float | None = None


class K1OtherInfo(BaseModel):
    """Line 17 – Other Information"""
    line_17_other_information: str | None = None


class K1ForeignTransactions(BaseModel):
    """Optional foreign transactions statement items."""
    line_16a_foreign_country: str | None = None
    line_16b_foreign_gross_income: float | None = None
    line_16c_foreign_deductions: float | None = None
    line_16d_total_foreign_taxes: float | None = None
    line_16e_reduction_in_taxes: float | None = None


# ------------------------------------------------------------------
# Top-level Schedule K-1 (S-Corp)
# ------------------------------------------------------------------
class ScheduleK1SCorp(BaseTaxForm):
    """
    Schedule K-1 (Form 1120-S) 2023 — Shareholder’s Share of Income, Deductions, Credits, and Other Items
    """

    form_type: Literal["Schedule K-1 (S-Corp)"] = "Schedule K-1 (S-Corp)"

    # Part I
    entity: EntityInfo = EntityInfo()

    # Part II
    shareholder: ShareholderInfo = ShareholderInfo()

    # Part III — Core numeric lines
    income_deductions: K1IncomeDeductions = K1IncomeDeductions()
    amt_items: K1AMTItems = K1AMTItems()
    basis_items: K1BasisItems = K1BasisItems()
    other: K1OtherInfo = K1OtherInfo()

    # Optional foreign
    foreign_transactions: K1ForeignTransactions = K1ForeignTransactions()

    # Special flags (bottom of form)
    k3_attached: bool | None = None  # Line 14: "Schedule K-3 is attached if checked"
    line_18_risk_multiple_activities: bool | None = None   # Line 18
    line_19_passive_multiple_activities: bool | None = None   # Line 19

    # Metadata
    is_final_k1: bool | None = None      # From header: "Final K-1"
    is_amended_k1: bool | None = None    # From header: "Amended K-1"
