"""Schemas for Schedule K-1 – Partner's / Shareholder's Share of Income."""

from __future__ import annotations

from pydantic import BaseModel

from tax_parser.schemas.base import BaseTaxForm, Address


# ---------------------------------------------------------------------------
# Part I – Information About the Partnership / S-Corp
# ---------------------------------------------------------------------------

class EntityInfo(BaseModel):
    name: str | None = None
    ein: str | None = None
    address: Address = Address()
    irs_center: str | None = None
    publicly_traded_partnership: bool | None = None


# ---------------------------------------------------------------------------
# Part II – Information About the Partner / Shareholder
# ---------------------------------------------------------------------------

class PartnerInfo(BaseModel):
    name: str | None = None
    ssn_or_ein: str | None = None
    address: Address = Address()
    is_general_partner: bool | None = None
    is_limited_partner: bool | None = None
    is_domestic_partner: bool | None = None
    is_foreign_partner: bool | None = None
    is_disregarded_entity: bool | None = None
    partner_type: str | None = None  # individual | corporation | estate | trust | etc.

    # Ownership
    profit_sharing_beginning: float | None = None
    profit_sharing_ending: float | None = None
    loss_sharing_beginning: float | None = None
    loss_sharing_ending: float | None = None
    capital_sharing_beginning: float | None = None
    capital_sharing_ending: float | None = None

    # Capital account
    beginning_capital_account: float | None = None
    capital_contributed: float | None = None
    current_year_increase_decrease: float | None = None
    withdrawals_distributions: float | None = None
    ending_capital_account: float | None = None
    capital_account_method: str | None = None  # tax basis | GAAP | section 704(b) | other


# ---------------------------------------------------------------------------
# Part III – Partner's / Shareholder's Share Items
# ---------------------------------------------------------------------------

class K1IncomeDeductions(BaseModel):
    """Lines 1-13 of K-1 Part III."""
    line_1_ordinary_business_income: float | None = None
    line_2_net_rental_real_estate: float | None = None
    line_3_other_net_rental_income: float | None = None
    line_4_guaranteed_payments: float | None = None  # Partnership only
    line_4a_guaranteed_payments_services: float | None = None
    line_4b_guaranteed_payments_capital: float | None = None
    line_4c_total_guaranteed_payments: float | None = None
    line_5a_interest_income: float | None = None
    line_5b_ordinary_dividends: float | None = None
    line_6a_qualified_dividends: float | None = None  # Partnership
    line_6_royalties: float | None = None
    line_7_net_short_term_capital_gain: float | None = None
    line_8a_net_long_term_capital_gain: float | None = None
    line_8b_collectibles_gain: float | None = None
    line_8c_unrecaptured_section_1250: float | None = None
    line_9_net_section_1231_gain: float | None = None
    line_10_other_income_loss: float | None = None
    line_11_section_179_deduction: float | None = None
    line_12_other_deductions: float | None = None
    line_13_credits: float | None = None


class K1SelfEmployment(BaseModel):
    """Lines 14 – self-employment earnings (Partnership K-1)."""
    line_14a_net_earnings: float | None = None
    line_14b_gross_farming_income: float | None = None
    line_14c_gross_nonfarm_income: float | None = None


class K1ForeignTransactions(BaseModel):
    line_16a_foreign_country: str | None = None
    line_16b_foreign_gross_income: float | None = None
    line_16c_foreign_deductions: float | None = None
    line_16d_total_foreign_taxes: float | None = None
    line_16e_reduction_in_taxes: float | None = None


class K1AMTItems(BaseModel):
    line_17a_post_1986_depreciation: float | None = None
    line_17b_adjusted_gain_loss: float | None = None
    line_17c_depletion: float | None = None
    line_17d_oil_gas_gross_income: float | None = None
    line_17e_other_amt_items: float | None = None


class K1OtherInfo(BaseModel):
    """Lines 18-20."""
    line_18_tax_exempt_income: float | None = None
    line_19_distributions: float | None = None
    line_20_other_information: str | None = None


# ---------------------------------------------------------------------------
# Top-level K-1 forms
# ---------------------------------------------------------------------------

class ScheduleK1Partnership(BaseTaxForm):
    """Schedule K-1 (Form 1065) – Partner's Share of Income."""

    form_type: str = "Schedule K-1 (Partnership)"

    entity: EntityInfo = EntityInfo()
    partner: PartnerInfo = PartnerInfo()
    income_deductions: K1IncomeDeductions = K1IncomeDeductions()
    self_employment: K1SelfEmployment = K1SelfEmployment()
    foreign_transactions: K1ForeignTransactions = K1ForeignTransactions()
    amt_items: K1AMTItems = K1AMTItems()
    other: K1OtherInfo = K1OtherInfo()


class ShareholderInfo(BaseModel):
    """S-Corp K-1 Part II – shareholder-specific fields."""
    name: str | None = None
    ssn_or_ein: str | None = None
    address: Address = Address()
    is_shareholder_final_return: bool | None = None
    shareholder_type: str | None = None

    # Ownership percentages
    stock_ownership_beginning: float | None = None
    stock_ownership_ending: float | None = None

    # Loan basis
    shareholder_loan_balance_beginning: float | None = None
    shareholder_loan_balance_ending: float | None = None


class ScheduleK1SCorp(BaseTaxForm):
    """Schedule K-1 (Form 1120-S) – Shareholder's Share of Income."""

    form_type: str = "Schedule K-1 (S-Corp)"

    entity: EntityInfo = EntityInfo()
    shareholder: ShareholderInfo = ShareholderInfo()
    income_deductions: K1IncomeDeductions = K1IncomeDeductions()
    foreign_transactions: K1ForeignTransactions = K1ForeignTransactions()
    amt_items: K1AMTItems = K1AMTItems()
    other: K1OtherInfo = K1OtherInfo()
