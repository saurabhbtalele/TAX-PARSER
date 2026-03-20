from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm


class ScheduleE(BaseTaxForm):
    """Schedule E - Supplemental Income and Loss"""
    
    form_type: Literal["Schedule E"] = "Schedule E"
    page: int = 1
    
    # Header Section
    name: str | None = Field(
        default=None,
        description="Name(s) shown on return",
        page=1
    )
    ssn: str | None = Field(
        default=None,
        description="Your social security number",
        page=1
    )
    
    # Part I - Income or Loss From Rental Real Estate and Royalties
    part_i_title: str | None = Field(
        default="Part I",
        description="Rental real estate and royalties section header",
        page=1
    )
    form_1099_payments: bool | None = Field(
        default=None,
        description="Did you make any payments in 2025 that would require you to file Form(s) 1099?",
        page=1,
        box="A"
    )
    form_1099_filed: bool | None = Field(
        default=None,
        description="If 'Yes', did you or will you file required Form(s) 1099?",
        page=1,
        box="B"
    )
    rental_properties: list[dict] = Field(
        default=[],
        description="List of rental properties",
        page=1
    )
    rental_property_type: str | None = Field(
        default=None,
        description="Type of Property: 1 Single Family Residence, 2 Multi-Family Residence, 3 Vacation/Short-Term Rental, 4 Commercial, 5 Land, 6 Royalties, 7 Self-Rental, 8 Other",
        page=1,
        box="1b"
    )
    fair_rental_days: int | None = Field(
        default=None,
        description="Number of fair rental days",
        page=1,
        box="2A"
    )
    personal_use_days: int | None = Field(
        default=None,
        description="Number of personal use days",
        page=1,
        box="2B"
    )
    qvj: bool | None = Field(
        default=None,
        description="Check the QJV box only if you meet the requirements to file as a qualified joint venture",
        page=1,
        box="2QJV"
    )
    rents_received: float | None = Field(
        default=None,
        description="Rents received",
        page=1,
        line=3
    )
    royalties_received: float | None = Field(
        default=None,
        description="Royalties received",
        page=1,
        line=4
    )
    advertising: float | None = Field(
        default=None,
        description="Advertising",
        page=1,
        line=5
    )
    auto_travel: float | None = Field(
        default=None,
        description="Auto and travel",
        page=1,
        line=6
    )
    cleaning_maintenance: float | None = Field(
        default=None,
        description="Cleaning and maintenance",
        page=1,
        line=7
    )
    commissions: float | None = Field(
        default=None,
        description="Commissions",
        page=1,
        line=8
    )
    insurance: float | None = Field(
        default=None,
        description="Insurance",
        page=1,
        line=9
    )
    legal_professional: float | None = Field(
        default=None,
        description="Legal and other professional fees",
        page=1,
        line=10
    )
    management_fees: float | None = Field(
        default=None,
        description="Management fees",
        page=1,
        line=11
    )
    mortgage_interest: float | None = Field(
        default=None,
        description="Mortgage interest paid to banks, etc.",
        page=1,
        line=12
    )
    other_interest: float | None = Field(
        default=None,
        description="Other interest",
        page=1,
        line=13
    )
    repairs: float | None = Field(
        default=None,
        description="Repairs",
        page=1,
        line=14
    )
    supplies: float | None = Field(
        default=None,
        description="Supplies",
        page=1,
        line=15
    )
    taxes: float | None = Field(
        default=None,
        description="Taxes",
        page=1,
        line=16
    )
    utilities: float | None = Field(
        default=None,
        description="Utilities",
        page=1,
        line=17
    )
    depreciation: float | None = Field(
        default=None,
        description="Depreciation expense or depletion",
        page=1,
        line=18
    )
    other_expenses: float | None = Field(
        default=None,
        description="Other expenses",
        page=1,
        line=19
    )
    total_expenses: float | None = Field(
        default=None,
        description="Total expenses. Add lines 5 through 19",
        page=1,
        line=20
    )
    net_income_loss: float | None = Field(
        default=None,
        description="Subtract line 2 from line 3 (rents) and/or 4 (royalties)",
        page=1,
        line=21
    )
    deductible_loss: float | None = Field(
        default=None,
        description="Deductible rental real estate loss after limitation",
        page=1,
        line=22
    )
    total_rental_royalties: float | None = Field(
        default=None,
        description="Total of all amounts reported on line 3 for all rental properties",
        page=1,
        line=23,
        box="a"
    )
    total_royalties: float | None = Field(
        default=None,
        description="Total of all amounts reported on line 4 for all royalty properties",
        page=1,
        line=23,
        box="b"
    )
    total_mortgage_interest: float | None = Field(
        default=None,
        description="Total of all amounts reported on line 12 for all properties",
        page=1,
        line=23,
        box="c"
    )
    total_depreciation: float | None = Field(
        default=None,
        description="Total of all amounts reported on line 18 for all properties",
        page=1,
        line=23,
        box="d"
    )
    total_expenses_all: float | None = Field(
        default=None,
        description="Total of all amounts reported on line 20 for all properties",
        page=1,
        line=23,
        box="e"
    )
    income: float | None = Field(
        default=None,
        description="Income. Add positive amounts shown on line 21",
        page=1,
        line=24
    )
    losses: float | None = Field(
        default=None,
        description="Losses. Add royalty losses from line 21 and rental real estate losses from line 22",
        page=1,
        line=25
    )
    total_rental_royalty: float | None = Field(
        default=None,
        description="Total rental real estate and royalty income or (loss)",
        page=1,
        line=26
    )
    
    # Part II - Income or Loss From Partnerships and S Corporations
    part_ii_title: str | None = Field(
        default="Part II",
        description="Partnerships and S corporations section header",
        page=2
    )
    prior_year_loss: bool | None = Field(
        default=None,
        description="Are you reporting any loss not allowed in a prior year due to the at-risk or basis limitations?",
        page=2,
        line=27
    )
    partnership_s_corporation: list[dict] = Field(
        default=[],
        description="List of partnerships and S corporations",
        page=2
    )
    passive_loss_allowed: float | None = Field(
        default=None,
        description="Passive loss allowed (attach Form 8582 if required)",
        page=2,
        box="g"
    )
    passive_income: float | None = Field(
        default=None,
        description="Passive income from Schedule K-1",
        page=2,
        box="h"
    )
    nonpassive_loss: float | None = Field(
        default=None,
        description="Nonpassive loss allowed (see Schedule K-1)",
        page=2,
        box="i"
    )
    section_179_expense: float | None = Field(
        default=None,
        description="Section 179 expense deduction from Form 4562",
        page=2,
        box="j"
    )
    nonpassive_income: float | None = Field(
        default=None,
        description="Nonpassive income from Schedule K-1",
        page=2,
        box="k"
    )
    partnership_s_corporation_total: float | None = Field(
        default=None,
        description="Total partnership and S corporation income or (loss)",
        page=2,
        line=32
    )
    
    # Part III - Income or Loss From Estates and Trusts
    part_iii_title: str | None = Field(
        default="Part III",
        description="Estates and trusts section header",
        page=2
    )
    estate_trust: list[dict] = Field(
        default=[],
        description="List of estates and trusts",
        page=2
    )
    passive_deduction_loss: float | None = Field(
        default=None,
        description="Passive deduction or loss allowed (attach Form 8582 if required)",
        page=2,
        box="c"
    )
    passive_income_estate: float | None = Field(
        default=None,
        description="Passive income from Schedule K-1",
        page=2,
        box="d"
    )
    deduction_loss: float | None = Field(
        default=None,
        description="Deduction or loss from Schedule K-1",
        page=2,
        box="e"
    )
    other_income: float | None = Field(
        default=None,
        description="Other income from Schedule K-1",
        page=2,
        box="f"
    )
    estate_trust_total: float | None = Field(
        default=None,
        description="Total estate and trust income or (loss)",
        page=2,
        line=37
    )
    
    # Part IV - Income or Loss From REMICs
    part_iv_title: str | None = Field(
        default="Part IV",
        description="REMICs section header",
        page=2
    )
    remic: list[dict] = Field(
        default=[],
        description="List of REMICs",
        page=2
    )
    excess_inclusion: float | None = Field(
        default=None,
        description="Excess inclusion from Schedules Q, line 2c",
        page=2,
        box="c"
    )
    taxable_income: float | None = Field(
        default=None,
        description="Taxable income (net loss) from Schedules Q, line 1b",
        page=2,
        box="d"
    )
    income: float | None = Field(
        default=None,
        description="Income from Schedules Q, line 3b",
        page=2,
        box="e"
    )
    remic_total: float | None = Field(
        default=None,
        description="Combine columns (d) and (e) only. Enter the result here and include in the total on line 41 below",
        page=2,
        line=39
    )
    
    # Part V - Summary
    part_v_title: str | None = Field(
        default="Part V",
        description="Summary section header",
        page=2
    )
    net_farm_rental: float | None = Field(
        default=None,
        description="Net farm rental income or (loss) from Form 4835",
        page=2,
        line=40
    )
    total_income_loss: float | None = Field(
        default=None,
        description="Total income or (loss). Combine lines 26, 32, 37, 39, and 40",
        page=2,
        line=41
    )
    farming_fishing_reconciliation: float | None = Field(
        default=None,
        description="Reconciliation of farming and fishing income",
        page=2,
        line=42
    )
    real_estate_reconciliation: float | None = Field(
        default=None,
        description="Reconciliation for real estate professionals",
        page=2,
        line=43
    )

    def get_line_fields(self) -> dict[str, str]:
        return {
            "total_rental_royalty": "Line 26 (Total Rental/Royalty)",
            "partnership_s_corporation_total": "Line 32 (Partnership/S-Corp Total)",
            "estate_trust_total": "Line 37 (Estate/Trust Total)",
            "total_income_loss": "Line 41 (Total Supplemental Income)"
        }