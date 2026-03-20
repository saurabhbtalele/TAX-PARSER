from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm


class ScheduleD(BaseTaxForm):
    """Schedule D - Capital Gains and Losses"""
    
    form_type: Literal["Schedule D"] = "Schedule D"
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
    
    # Part I - Short-Term Capital Gains and Losses
    part_i_title: str | None = Field(
        default="Part I",
        description="Short-term capital gains and losses section header",
        page=1
    )
    short_term_line_1a: float | None = Field(
        default=None,
        description="Totals for all short-term transactions reported on Form 1099-B or Form 1099-DA for which basis was reported to the IRS",
        page=1,
        line=1,
        box="a"
    )
    short_term_line_1b: float | None = Field(
        default=None,
        description="Totals for all transactions reported on Form(s) 8949 with Box A or Box G checked",
        page=1,
        line=1,
        box="b"
    )
    short_term_line_2: float | None = Field(
        default=None,
        description="Totals for all transactions reported on Form(s) 8949 with Box B or Box H checked",
        page=1,
        line=2
    )
    short_term_line_3: float | None = Field(
        default=None,
        description="Totals for all transactions reported on Form(s) 8949 with Box C or Box I checked",
        page=1,
        line=3
    )
    short_term_line_4: float | None = Field(
        default=None,
        description="Short-term gain from Form 6252 and short-term gain or (loss) from Forms 4684, 6781, and 8824",
        page=1,
        line=4
    )
    short_term_line_5: float | None = Field(
        default=None,
        description="Net short-term gain or (loss) from partnerships, S corporations, estates, and trusts from Schedule(s) K-1",
        page=1,
        line=5
    )
    short_term_line_6: float | None = Field(
        default=None,
        description="Short-term capital loss carryover",
        page=1,
        line=6
    )
    short_term_line_7: float | None = Field(
        default=None,
        description="Net short-term capital gain or (loss)",
        page=1,
        line=7
    )
    
    # Part II - Long-Term Capital Gains and Losses
    part_ii_title: str | None = Field(
        default="Part II",
        description="Long-term capital gains and losses section header",
        page=1
    )
    long_term_line_8a: float | None = Field(
        default=None,
        description="Totals for all long-term transactions reported on Form 1099-B or Form 1099-DA for which basis was reported to the IRS",
        page=1,
        line=8,
        box="a"
    )
    long_term_line_8b: float | None = Field(
        default=None,
        description="Totals for all transactions reported on Form(s) 8949 with Box D or Box J checked",
        page=1,
        line=8,
        box="b"
    )
    long_term_line_9: float | None = Field(
        default=None,
        description="Totals for all transactions reported on Form(s) 8949 with Box E or Box K checked",
        page=1,
        line=9
    )
    long_term_line_10: float | None = Field(
        default=None,
        description="Totals for all transactions reported on Form(s) 8949 with Box F or Box L checked",
        page=1,
        line=10
    )
    long_term_line_11: float | None = Field(
        default=None,
        description="Gain from Form 4797, Part I; long-term gain from Forms 2439 and 6252; and long-term gain or (loss) from Forms 4684, 6781, and 8824",
        page=1,
        line=11
    )
    long_term_line_12: float | None = Field(
        default=None,
        description="Net long-term gain or (loss) from partnerships, S corporations, estates, and trusts from Schedule(s) K-1",
        page=1,
        line=12
    )
    long_term_line_13: float | None = Field(
        default=None,
        description="Capital gain distributions",
        page=1,
        line=13
    )
    long_term_line_14: float | None = Field(
        default=None,
        description="Long-term capital loss carryover",
        page=1,
        line=14
    )
    long_term_line_15: float | None = Field(
        default=None,
        description="Net long-term capital gain or (loss)",
        page=1,
        line=15
    )
    
    # Part III - Summary
    part_iii_title: str | None = Field(
        default="Part III",
        description="Summary section header",
        page=2
    )
    line_16: float | None = Field(
        default=None,
        description="Combine lines 7 and 15 and enter the result",
        page=2,
        line=16
    )
    line_17: bool | None = Field(
        default=None,
        description="Are lines 15 and 16 both gains?",
        page=2,
        line=17
    )
    line_18: float | None = Field(
        default=None,
        description="28% Rate Gain Worksheet amount",
        page=2,
        line=18
    )
    line_19: float | None = Field(
        default=None,
        description="Unrecaptured Section 1250 Gain Worksheet amount",
        page=2,
        line=19
    )
    line_20: bool | None = Field(
        default=None,
        description="Are lines 18 and 19 both zero or blank and you are not filing Form 4952?",
        page=2,
        line=20
    )
    line_21: float | None = Field(
        default=None,
        description="If line 16 is a loss, enter here and on Form 1040, 1040-SR, or 1040-NR, line 7a",
        page=2,
        line=21
    )
    line_22: bool | None = Field(
        default=None,
        description="Do you have qualified dividends on Form 1040, 1040-SR, or 1040-NR, line 3a?",
        page=2,
        line=22
    )

    def get_line_fields(self) -> dict[str, str]:
        return {
            "short_term_line_7": "Line 7 (Net ST Gain/Loss)",
            "long_term_line_15": "Line 15 (Net LT Gain/Loss)",
            "line_16": "Line 16 (Combined Net Gain/Loss)"
        }