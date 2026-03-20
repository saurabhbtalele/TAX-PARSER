from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm


class W2EmployeeInfo(BaseModel):
    """Employee Information Section - Page 1"""
    
    social_security_number: str | None = Field(
        default=None,
        description="Employee's social security number",
        page=1,
        box="a"
    )
    first_name: str | None = Field(
        default=None,
        description="Employee's first name and initial",
        page=1,
        box="e"
    )
    last_name: str | None = Field(
        default=None,
        description="Employee's last name",
        page=1,
        box="e"
    )
    suffix: str | None = Field(
        default=None,
        description="Employee's suffix (Jr., Sr., III, etc.)",
        page=1,
        box="e"
    )
    address: str | None = Field(
        default=None,
        description="Employee's address and ZIP code",
        page=1,
        box="f"
    )


class W2EmployerInfo(BaseModel):
    """Employer Information Section - Page 1"""
    
    ein: str | None = Field(
        default=None,
        description="Employer identification number (EIN)",
        page=1,
        box="b"
    )
    name: str | None = Field(
        default=None,
        description="Employer's name",
        page=1,
        box="c"
    )
    address: str | None = Field(
        default=None,
        description="Employer's address, city, state, and ZIP code",
        page=1,
        box="c"
    )
    control_number: str | None = Field(
        default=None,
        description="Control number (if applicable)",
        page=1,
        box="d"
    )
    state_id_number: str | None = Field(
        default=None,
        description="State Employer's state ID number",
        page=1,
        box="15"
    )


class W2WageTaxInfo(BaseModel):
    """Wage and Tax Information Section - Page 1"""
    
    wages_tips_compensation: float | None = Field(
        default=None,
        description="Wages, tips, other compensation (Box 1)",
        page=1,
        box="1"
    )
    federal_income_tax_withheld: float | None = Field(
        default=None,
        description="Federal income tax withheld (Box 2)",
        page=1,
        box="2"
    )
    social_security_wages: float | None = Field(
        default=None,
        description="Social security wages (Box 3)",
        page=1,
        box="3"
    )
    social_security_tax_withheld: float | None = Field(
        default=None,
        description="Social security tax withheld (Box 4)",
        page=1,
        box="4"
    )
    medicare_wages_tips: float | None = Field(
        default=None,
        description="Medicare wages and tips (Box 5)",
        page=1,
        box="5"
    )
    medicare_tax_withheld: float | None = Field(
        default=None,
        description="Medicare tax withheld (Box 6)",
        page=1,
        box="6"
    )
    social_security_tips: float | None = Field(
        default=None,
        description="Social security tips (Box 7)",
        page=1,
        box="7"
    )
    allocated_tips: float | None = Field(
        default=None,
        description="Allocated tips (Box 8)",
        page=1,
        box="8"
    )
    dependent_care_benefits: float | None = Field(
        default=None,
        description="Dependent care benefits (Box 10)",
        page=1,
        box="10"
    )
    nonqualified_plans: float | None = Field(
        default=None,
        description="Nonqualified plans (Box 11)",
        page=1,
        box="11"
    )
    state_wages_tips: float | None = Field(
        default=None,
        description="State wages, tips, etc. (Box 16)",
        page=1,
        box="16"
    )
    state_income_tax: float | None = Field(
        default=None,
        description="State income tax (Box 17)",
        page=1,
        box="17"
    )
    local_wages_tips: float | None = Field(
        default=None,
        description="Local wages, tips, etc. (Box 18)",
        page=1,
        box="18"
    )
    local_income_tax: float | None = Field(
        default=None,
        description="Local income tax (Box 19)",
        page=1,
        box="19"
    )
    locality_name: str | None = Field(
        default=None,
        description="Locality name (Box 20)",
        page=1,
        box="20"
    )


class W2Box12(BaseModel):
    """Box 12 Information Section - Page 1"""
    
    code_a: float | None = Field(
        default=None,
        description="Uncollected social security or RRTA tax on tips (Box 12, Code A)",
        page=1,
        box="12a",
        code="A"
    )
    code_b: float | None = Field(
        default=None,
        description="Uncollected Medicare tax on tips (Box 12, Code B)",
        page=1,
        box="12b",
        code="B"
    )
    code_c: float | None = Field(
        default=None,
        description="Taxable cost of group-term life insurance over $50,000 (Box 1, Code C)",
        page=1,
        box="12c",
        code="C"
    )
    code_d: float | None = Field(
        default=None,
        description="Elective deferrals to a section 401(k) cash or deferred arrangement (Box 12, Code D)",
        page=1,
        box="12d",
        code="D"
    )
    code_e: float | None = Field(
        default=None,
        description="Elective deferrals under a section 403(b) salary reduction agreement (Box 12, Code E)",
        page=1,
        box="12e",
        code="E"
    )
    code_f: float | None = Field(
        default=None,
        description="Elective deferrals under a section 408(k)(6) salary reduction SEP (Box 12, Code F)",
        page=1,
        box="12f",
        code="F"
    )
    code_g: float | None = Field(
        default=None,
        description="Elective deferrals and employer contributions to a section 457(b) deferred compensation plan (Box 12, Code G)",
        page=1,
        box="12g",
        code="G"
    )
    code_h: float | None = Field(
        default=None,
        description="Elective deferrals to a section 501(c)(18)(D) tax-exempt organization plan (Box 12, Code H)",
        page=1,
        box="12h",
        code="H"
    )
    code_j: float | None = Field(
        default=None,
        description="Nontaxable sick pay (Box 12, Code J)",
        page=1,
        box="12j",
        code="J"
    )
    code_k: float | None = Field(
        default=None,
        description="20% excise tax on excess golden parachute payments (Box 12, Code K)",
        page=1,
        box="12k",
        code="K"
    )
    code_l: float | None = Field(
        default=None,
        description="Substantiated employee business expense reimbursements (Box 12, Code L)",
        page=1,
        box="12l",
        code="L"
    )
    code_m: float | None = Field(
        default=None,
        description="Uncollected social security or RRTA tax on taxable cost of group-term life insurance (Box 12, Code M)",
        page=1,
        box="12m",
        code="M"
    )
    code_n: float | None = Field(
        default=None,
        description="Uncollected Medicare tax on taxable cost of group-term life insurance (Box 12, Code N)",
        page=1,
        box="12n",
        code="N"
    )
    code_p: float | None = Field(
        default=None,
        description="Excludable moving expense reimbursements (Box 12, Code P)",
        page=1,
        box="12p",
        code="P"
    )
    code_q: float | None = Field(
        default=None,
        description="Nontaxable combat pay (Box 12, Code Q)",
        page=1,
        box="12q",
        code="Q"
    )
    code_r: float | None = Field(
        default=None,
        description="Employer contributions to Archer MSA (Box 12, Code R)",
        page=1,
        box="12r",
        code="R"
    )
    code_s: float | None = Field(
        default=None,
        description="Employee salary reduction contributions under a section 408(p) SIMPLE plan (Box 12, Code S)",
        page=1,
        box="12s",
        code="S"
    )
    code_t: float | None = Field(
        default=None,
        description="Adoption benefits (Box 12, Code T)",
        page=1,
        box="12t",
        code="T"
    )
    code_v: float | None = Field(
        default=None,
        description="Income from exercise of nonstatutory stock options (Box 12, Code V)",
        page=1,
        box="12v",
        code="V"
    )
    code_w: float | None = Field(
        default=None,
        description="Employer contributions to health savings account (Box 12, Code W)",
        page=1,
        box="12w",
        code="W"
    )
    code_y: float | None = Field(
        default=None,
        description="Deferrals under a section 409A nonqualified deferred compensation plan (Box 12, Code Y)",
        page=1,
        box="12y",
        code="Y"
    )
    code_z: float | None = Field(
        default=None,
        description="Income under a nonqualified deferred compensation plan that fails to satisfy section 409A (Box 12, Code Z)",
        page=1,
        box="12z",
        code="Z"
    )
    code_aa: float | None = Field(
        default=None,
        description="Designated Roth contributions under a section 401(k) plan (Box 12, Code AA)",
        page=1,
        box="12aa",
        code="AA"
    )
    code_bb: float | None = Field(
        default=None,
        description="Designated Roth contributions under a section 403(b) plan (Box 12, Code BB)",
        page=1,
        box="12bb",
        code="BB"
    )
    code_dd: float | None = Field(
        default=None,
        description="Cost of employer-sponsored health coverage (Box 12, Code DD)",
        page=1,
        box="12dd",
        code="DD"
    )
    code_ee: float | None = Field(
        default=None,
        description="Designated Roth contributions under a governmental section 457(b) plan (Box 12, Code EE)",
        page=1,
        box="12ee",
        code="EE"
    )
    code_ff: float | None = Field(
        default=None,
        description="Permitted benefits under a qualified small employer health reimbursement arrangement (Box 12, Code FF)",
        page=1,
        box="12ff",
        code="FF"
    )
    code_gg: float | None = Field(
        default=None,
        description="Income from qualified equity grants under section 83(i) (Box 12, Code GG)",
        page=1,
        box="12gg",
        code="GG"
    )
    code_hh: float | None = Field(
        default=None,
        description="Aggregate deferrals under section 83(i) elections (Box 12, Code HH)",
        page=1,
        box="12hh",
        code="HH"
    )
    code_ii: float | None = Field(
        default=None,
        description="Medicaid waiver payments excluded from gross income (Box 12, Code II)",
        page=1,
        box="12ii",
        code="II"
    )
    code_ta: float | None = Field(
        default=None,
        description="Employer contributions under a section 128 Trump account contribution program (Box 12, Code TA)",
        page=1,
        box="12ta",
        code="TA"
    )
    code_tp: float | None = Field(
        default=None,
        description="Total amount of cash tips reported to the employer (Box 12, Code TP)",
        page=1,
        box="12tp",
        code="TP"
    )
    code_tt: float | None = Field(
        default=None,
        description="Total amount of qualified overtime compensation (Box 12, Code TT)",
        page=1,
        box="12tt",
        code="TT"
    )


class W2Box13(BaseModel):
    """Box 13 Information Section - Page 1"""
    
    statutory_employee: bool | None = Field(
        default=None,
        description="Statutory employee (Box 13)",
        page=1,
        box="13",
        code="Statutory employee"
    )
    retirement_plan: bool | None = Field(
        default=None,
        description="Retirement plan (Box 13)",
        page=1,
        box="13",
        code="Retirement plan"
    )
    third_party_sick_pay: bool | None = Field(
        default=None,
        description="Third-party sick pay (Box 13)",
        page=1,
        box="13",
        code="Third-party sick pay"
    )


class W2Box14(BaseModel):
    """Box 14 Information Section - Page 1"""
    
    other_info: list[dict] | None = Field(
        default=None,
        description="Other information (Box 14) - May include state disability insurance taxes, union dues, health insurance premiums, etc.",
        page=1,
        box="14"
    )
    treasury_tipped_occupation_codes: list[str] | None = Field(
        default=None,
        description="Treasury Tipped Occupation Code(s) (Box 14b)",
        page=1,
        box="14b"
    )


class W2(BaseTaxForm):
    """IRS Form W-2 - Wage and Tax Statement"""
    
    form_type: Literal["W-2"] = "W-2"
    year: int = 2026
    page: int = 1
    
    # Header Section
    employee_info: W2EmployeeInfo = Field(
        default_factory=W2EmployeeInfo,
        description="Employee information section",
        page=1
    )
    employer_info: W2EmployerInfo = Field(
        default_factory=W2EmployerInfo,
        description="Employer information section",
        page=1
    )
    
    # Wage and Tax Information
    wage_tax_info: W2WageTaxInfo = Field(
        default_factory=W2WageTaxInfo,
        description="Wage and tax information section",
        page=1
    )
    
    # Box 12 Information
    box_12: W2Box12 = Field(
        default_factory=W2Box12,
        description="Box 12 information with various codes",
        page=1
    )
    
    # Box 13 Information
    box_13: W2Box13 = Field(
        default_factory=W2Box13,
        description="Box 13 information with checkboxes",
        page=1
    )
    
    # Box 14 Information
    box_14: W2Box14 = Field(
        default_factory=W2Box14,
        description="Box 14 information with other details",
        page=1
    )
    
    # Additional Information
    digital_assets: bool | None = Field(
        default=None,
        description="Indicates if employee received, sold, or disposed of digital assets",
        page=1
    )
    presidential_election_campaign: bool | None = Field(
        default=None,
        description="Check if $3 should go to the Presidential Election Campaign Fund",
        page=1
    )

    def get_line_fields(self) -> dict[str, str]:
        return {
            "employer_info.name": "Employer",
            "wage_tax_info.wages_tips_compensation": "Box 1 (Wages)",
            "wage_tax_info.federal_income_tax_withheld": "Box 2 (Fed Tax)",
            "wage_tax_info.state_income_tax": "Box 17 (State Tax)"
        }