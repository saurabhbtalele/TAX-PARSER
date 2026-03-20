from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm


class ScheduleB(BaseTaxForm):
    """Schedule B - Interest and Ordinary Dividends"""
    
    form_type: Literal["Schedule B"] = "Schedule B"
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
    
    # Part I - Interest
    part_i_title: str | None = Field(
        default="Part I",
        description="Interest section header",
        page=1
    )
    interest_line_1: list[dict] = Field(
        default=[],
        description="List of interest income items (up to 10 entries)",
        page=1,
        box="1"
    )
    interest_line_2: float | None = Field(
        default=None,
        description="Add the amounts on line 1",
        page=1,
        line=2
    )
    interest_line_3: float | None = Field(
        default=None,
        description="Excludable interest on series EE and I U.S. savings bonds issued after 1989",
        page=1,
        line=3
    )
    interest_line_4: float | None = Field(
        default=None,
        description="Subtract line 3 from line 2. Enter the result here and on Form 1040 or 1040-SR, line 2b",
        page=1,
        line=4
    )
    
    # Part II - Ordinary Dividends
    part_ii_title: str | None = Field(
        default="Part II",
        description="Ordinary dividends section header",
        page=1
    )
    dividends_line_5: list[dict] = Field(
        default=[],
        description="List of ordinary dividend items (up to 10 entries)",
        page=1,
        box="5"
    )
    dividends_line_6: float | None = Field(
        default=None,
        description="Add the amounts on line 5. Enter the total here and on Form 1040 or 1040-SR, line 3b",
        page=1,
        line=6
    )
    
    # Part III - Foreign Accounts and Trusts
    part_iii_title: str | None = Field(
        default="Part III",
        description="Foreign accounts and trusts section header",
        page=1
    )
    foreign_account_question_7a: bool | None = Field(
        default=None,
        description="At any time during 2025, did you have a financial interest in or signature authority over a financial account located in a foreign country?",
        page=1,
        box="7a"
    )
    foreign_account_question_7b: bool | None = Field(
        default=None,
        description="If 'Yes' to question 7a, are you required to file FinCEN Form 114 (FBAR)?",
        page=1,
        box="7b"
    )
    foreign_countries: list[str] = Field(
        default=[],
        description="List of foreign countries where financial accounts are located (if required to file FinCEN Form 114)",
        page=1,
        box="7b"
    )
    foreign_trust_question_8: bool | None = Field(
        default=None,
        description="During 2025, did you receive a distribution from, or were you the grantor of, or transferor to, a foreign trust?",
        page=1,
        box="8"
    )

    def get_line_fields(self) -> dict[str, str]:
        return {
            "interest_line_4": "Line 4 (Taxable Interest)",
            "dividends_line_6": "Line 6 (Ordinary Dividends)"
        }