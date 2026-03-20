from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm


class ScheduleK1SCorp(BaseTaxForm):
    """Schedule K-1 (Form 1120-S) - Shareholder's Share of Income, Deductions, Credits, etc."""
    
    form_type: Literal["Schedule K-1 (S-Corp)"] = "Schedule K-1 (S-Corp)"
    page: int = 1
    
    # Header Section
    is_final_k1: bool | None = Field(
        default=None,
        description="Indicates if this is a Final K-1",
        page=1,
        box="Final K-1"
    )
    is_amended_k1: bool | None = Field(
        default=None,
        description="Indicates if this is an Amended K-1",
        page=1,
        box="Amended K-1"
    )
    
    # Part I - Information About the Corporation
    part_i_title: str | None = Field(
        default="Part I",
        description="Information About the Corporation section header",
        page=1
    )
    ein: str | None = Field(
        default=None,
        description="Corporation's employer identification number",
        page=1,
        box="A"
    )
    corporation_name: str | None = Field(
        default=None,
        description="Corporation's name, address, city, state, and ZIP code",
        page=1,
        box="B"
    )
    irs_center: str | None = Field(
        default=None,
        description="IRS Center where corporation filed return",
        page=1,
        box="C"
    )
    total_shares_beginning: int | None = Field(
        default=None,
        description="Corporation's total number of shares - Beginning of tax year",
        page=1,
        box="D",
        line="Beginning of tax year"
    )
    total_shares_ending: int | None = Field(
        default=None,
        description="Corporation's total number of shares - End of tax year",
        page=1,
        box="D",
        line="End of tax year"
    )
    
    # Part II - Information About the Shareholder
    part_ii_title: str | None = Field(
        default="Part II",
        description="Information About the Shareholder section header",
        page=1
    )
    ssn_or_ein: str | None = Field(
        default=None,
        description="Shareholder's identifying number",
        page=1,
        box="E"
    )
    shareholder_name: str | None = Field(
        default=None,
        description="Shareholder's name, address, city, state, and ZIP code",
        page=1,
        box="F"
    )
    allocation_percentage: float | None = Field(
        default=None,
        description="Current year allocation percentage",
        page=1,
        box="G"
    )
    shares_beginning: int | None = Field(
        default=None,
        description="Shareholder's number of shares - Beginning of tax year",
        page=1,
        box="H",
        line="Beginning of tax year"
    )
    shares_ending: int | None = Field(
        default=None,
        description="Shareholder's number of shares - End of tax year",
        page=1,
        box="H",
        line="End of tax year"
    )
    shareholder_loan_balance_beginning: float | None = Field(
        default=None,
        description="Loans from shareholder - Beginning of tax year",
        page=1,
        box="I",
        line="Beginning of tax year"
    )
    shareholder_loan_balance_ending: float | None = Field(
        default=None,
        description="Loans from shareholder - End of tax year",
        page=1,
        box="I",
        line="End of tax year"
    )
    
    # Part III - Shareholder's Share of Income, Deductions, Credits, etc.
    part_iii_title: str | None = Field(
        default="Part III",
        description="Shareholder's Share of Income, Deductions, Credits, etc. section header",
        page=1
    )
    ordinary_business_income: float | None = Field(
        default=None,
        description="Ordinary business income (loss)",
        page=1,
        line=1
    )
    net_rental_real_estate: float | None = Field(
        default=None,
        description="Net rental real estate income (loss)",
        page=1,
        line=2
    )
    other_net_rental: float | None = Field(
        default=None,
        description="Other net rental income (loss)",
        page=1,
        line=3
    )
    interest_income: float | None = Field(
        default=None,
        description="Interest income",
        page=1,
        line=4
    )
    ordinary_dividends: float | None = Field(
        default=None,
        description="Ordinary dividends",
        page=1,
        line=5,
        box="a"
    )
    qualified_dividends: float | None = Field(
        default=None,
        description="Qualified dividends",
        page=1,
        line=5,
        box="b"
    )
    royalties: float | None = Field(
        default=None,
        description="Royalties",
        page=1,
        line=6
    )
    net_short_term_capital_gain: float | None = Field(
        default=None,
        description="Net short-term capital gain (loss)",
        page=1,
        line=7
    )
    net_long_term_capital_gain: float | None = Field(
        default=None,
        description="Net long-term capital gain (loss)",
        page=1,
        line=8,
        box="a"
    )
    collectibles_gain: float | None = Field(
        default=None,
        description="Collectibles (28%) gain (loss)",
        page=1,
        line=8,
        box="b"
    )
    unrecaptured_section_1250: float | None = Field(
        default=None,
        description="Unrecaptured section 1250 gain",
        page=1,
        line=8,
        box="c"
    )
    net_section_1231_gain: float | None = Field(
        default=None,
        description="Net section 1231 gain (loss)",
        page=1,
        line=9
    )
    other_income_loss: float | None = Field(
        default=None,
        description="Other income (loss)",
        page=1,
        line=10
    )
    section_179_deduction: float | None = Field(
        default=None,
        description="Section 179 deduction",
        page=1,
        line=11
    )
    other_deductions: float | None = Field(
        default=None,
        description="Other deductions",
        page=1,
        line=12
    )
    credits: float | None = Field(
        default=None,
        description="Credits",
        page=1,
        line=13
    )
    alternative_minimum_tax: float | None = Field(
        default=None,
        description="Alternative minimum tax (AMT) items",
        page=1,
        line=15
    )
    items_affecting_basis: float | None = Field(
        default=None,
        description="Items affecting shareholder basis",
        page=1,
        line=16
    )
    other_information: str | None = Field(
        default=None,
        description="Other information",
        page=1,
        line=17
    )
    schedule_k3_attached: bool | None = Field(
        default=None,
        description="Schedule K-3 is attached if checked",
        page=1,
        line=14
    )
    more_than_one_activity_at_risk: bool | None = Field(
        default=None,
        description="More than one activity for at-risk purposes",
        page=1,
        line=18
    )
    more_than_one_activity_passive: bool | None = Field(
        default=None,
        description="More than one activity for passive activity purposes",
        page=1,
        line=19
    )