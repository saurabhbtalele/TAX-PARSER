from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm


class ScheduleC(BaseTaxForm):
    """Schedule C - Profit or Loss From Business"""
    
    form_type: Literal["Schedule C"] = "Schedule C"
    page: int = 1
    
    # Header Section
    name: str | None = Field(
        default=None,
        description="Name of proprietor",
        page=1
    )
    ssn: str | None = Field(
        default=None,
        description="Social security number (SSN)",
        page=1
    )
    
    # Business Information
    business_type: str | None = Field(
        default=None,
        description="Principal business or profession, including product or service",
        page=1,
        box="A"
    )
    business_code: str | None = Field(
        default=None,
        description="Business activity code from instructions",
        page=1,
        box="B"
    )
    business_name: str | None = Field(
        default=None,
        description="Business name (if different from proprietor's name)",
        page=1,
        box="C"
    )
    ein: str | None = Field(
        default=None,
        description="Employer ID number (EIN)",
        page=1,
        box="D"
    )
    business_address: str | None = Field(
        default=None,
        description="Business address (including suite or room number)",
        page=1,
        box="E"
    )
    business_city: str | None = Field(
        default=None,
        description="City, town or post office, state, and ZIP code",
        page=1,
        box="E"
    )
    accounting_method: str | None = Field(
        default=None,
        description="Accounting method: (1) Cash (2) Accrual (3) Other",
        page=1,
        box="F"
    )
    material_participation: bool | None = Field(
        default=None,
        description="Did you 'materially participate' in the operation of this business during 2025?",
        page=1,
        box="G"
    )
    new_business: bool | None = Field(
        default=None,
        description="If you started or acquired this business during 2025, check here",
        page=1,
        box="H"
    )
    form_1099_payments: bool | None = Field(
        default=None,
        description="Did you make any payments in 2025 that would require you to file Form(s) 1099?",
        page=1,
        box="I"
    )
    form_1099_filed: bool | None = Field(
        default=None,
        description="If 'Yes' to question I, did you or will you file required Form(s) 1099?",
        page=1,
        box="J"
    )
    
    # Part I - Income
    part_i_title: str | None = Field(
        default="Part I",
        description="Income section header",
        page=1
    )
    gross_receipts: float | None = Field(
        default=None,
        description="Gross receipts or sales",
        page=1,
        line=1
    )
    returns_allowances: float | None = Field(
        default=None,
        description="Returns and allowances",
        page=1,
        line=2
    )
    net_receipts: float | None = Field(
        default=None,
        description="Subtract line 2 from line 1",
        page=1,
        line=3
    )
    cost_of_goods_sold: float | None = Field(
        default=None,
        description="Cost of goods sold (from line 42)",
        page=1,
        line=4
    )
    gross_profit: float | None = Field(
        default=None,
        description="Gross profit. Subtract line 4 from line 3",
        page=1,
        line=5
    )
    other_income: float | None = Field(
        default=None,
        description="Other income, including federal and state gasoline or fuel tax credit or refund",
        page=1,
        line=6
    )
    gross_income: float | None = Field(
        default=None,
        description="Gross income. Add lines 5 and 6",
        page=1,
        line=7
    )
    
    # Part II - Expenses
    part_ii_title: str | None = Field(
        default="Part II",
        description="Expenses section header",
        page=1
    )
    advertising: float | None = Field(
        default=None,
        description="Advertising",
        page=1,
        line=8
    )
    car_truck_expenses: float | None = Field(
        default=None,
        description="Car and truck expenses",
        page=1,
        line=9
    )
    commissions_fees: float | None = Field(
        default=None,
        description="Commissions and fees",
        page=1,
        line=10
    )
    contract_labor: float | None = Field(
        default=None,
        description="Contract labor",
        page=1,
        line=11
    )
    depletion: float | None = Field(
        default=None,
        description="Depletion",
        page=1,
        line=12
    )
    depreciation: float | None = Field(
        default=None,
        description="Depreciation and section 179 expense deduction",
        page=1,
        line=13
    )
    employee_benefits: float | None = Field(
        default=None,
        description="Employee benefit programs (other than on line 19)",
        page=1,
        line=14
    )
    insurance: float | None = Field(
        default=None,
        description="Insurance (other than health)",
        page=1,
        line=15
    )
    mortgage_interest: float | None = Field(
        default=None,
        description="Mortgage (paid to banks, etc.)",
        page=1,
        line=16,
        box="a"
    )
    other_interest: float | None = Field(
        default=None,
        description="Other interest",
        page=1,
        line=16,
        box="b"
    )
    legal_professional: float | None = Field(
        default=None,
        description="Legal and professional services",
        page=1,
        line=17
    )
    office_expense: float | None = Field(
        default=None,
        description="Office expense",
        page=1,
        line=18
    )
    pension_profits: float | None = Field(
        default=None,
        description="Pension and profit-sharing plans",
        page=1,
        line=19
    )
    vehicles_machinery: float | None = Field(
        default=None,
        description="Vehicles, machinery, and equipment",
        page=1,
        line=20,
        box="a"
    )
    other_business_property: float | None = Field(
        default=None,
        description="Other business property",
        page=1,
        line=20,
        box="b"
    )
    repairs_maintenance: float | None = Field(
        default=None,
        description="Repairs and maintenance",
        page=1,
        line=21
    )
    supplies: float | None = Field(
        default=None,
        description="Supplies (not included in Part III)",
        page=1,
        line=22
    )
    taxes_licenses: float | None = Field(
        default=None,
        description="Taxes and licenses",
        page=1,
        line=23
    )
    travel: float | None = Field(
        default=None,
        description="Travel",
        page=1,
        line=24,
        box="a"
    )
    deductible_meals: float | None = Field(
        default=None,
        description="Deductible meals",
        page=1,
        line=24,
        box="b"
    )
    utilities: float | None = Field(
        default=None,
        description="Utilities",
        page=1,
        line=25
    )
    wages: float | None = Field(
        default=None,
        description="Wages (less employment credits)",
        page=1,
        line=26
    )
    energy_efficient: float | None = Field(
        default=None,
        description="Energy efficient commercial buildings deduction",
        page=1,
        line=27,
        box="a"
    )
    other_expenses: float | None = Field(
        default=None,
        description="Other expenses (from line 48)",
        page=1,
        line=27,
        box="b"
    )
    total_expenses: float | None = Field(
        default=None,
        description="Total expenses before expenses for business use of home",
        page=1,
        line=28
    )
    tentative_profit_loss: float | None = Field(
        default=None,
        description="Tentative profit or (loss). Subtract line 28 from line 7",
        page=1,
        line=29
    )
    home_business_expenses: float | None = Field(
        default=None,
        description="Expenses for business use of your home",
        page=1,
        line=30
    )
    net_profit_loss: float | None = Field(
        default=None,
        description="Net profit or (loss). Subtract line 30 from line 29",
        page=1,
        line=31
    )
    
    # Part III - Cost of Goods Sold
    part_iii_title: str | None = Field(
        default="Part III",
        description="Cost of Goods Sold section header",
        page=2
    )
    inventory_valuation: str | None = Field(
        default=None,
        description="Method(s) used to value closing inventory",
        page=2,
        line=33
    )
    inventory_change: bool | None = Field(
        default=None,
        description="Was there any change in determining quantities, costs, or valuations between opening and closing inventory?",
        page=2,
        line=34
    )
    opening_inventory: float | None = Field(
        default=None,
        description="Inventory at beginning of year",
        page=2,
        line=35
    )
    purchases: float | None = Field(
        default=None,
        description="Purchases less cost of items withdrawn for personal use",
        page=2,
        line=36
    )
    labor_cost: float | None = Field(
        default=None,
        description="Cost of labor",
        page=2,
        line=37
    )
    materials_supplies: float | None = Field(
        default=None,
        description="Materials and supplies",
        page=2,
        line=38
    )
    other_costs: float | None = Field(
        default=None,
        description="Other costs",
        page=2,
        line=39
    )
    total_cost: float | None = Field(
        default=None,
        description="Add lines 35 through 39",
        page=2,
        line=40
    )
    ending_inventory: float | None = Field(
        default=None,
        description="Inventory at end of year",
        page=2,
        line=41
    )
    cost_of_goods_sold: float | None = Field(
        default=None,
        description="Cost of goods sold. Subtract line 41 from line 40",
        page=2,
        line=42
    )
    
    # Part IV - Vehicle Information
    part_iv_title: str | None = Field(
        default="Part IV",
        description="Information on Your Vehicle section header",
        page=2
    )
    vehicle_in_service_date: str | None = Field(
        default=None,
        description="When did you place your vehicle in service for business purposes?",
        page=2,
        line=43
    )
    business_miles: int | None = Field(
        default=None,
        description="Number of miles used for business",
        page=2,
        line=44,
        box="a"
    )
    commuting_miles: int | None = Field(
        default=None,
        description="Number of miles used for commuting",
        page=2,
        line=44,
        box="b"
    )
    other_miles: int | None = Field(
        default=None,
        description="Number of miles used for other purposes",
        page=2,
        line=44,
        box="c"
    )
    personal_use: bool | None = Field(
        default=None,
        description="Was your vehicle available for personal use during off-duty hours?",
        page=2,
        line=45
    )
    other_vehicle: bool | None = Field(
        default=None,
        description="Do you (or your spouse) have another vehicle available for personal use?",
        page=2,
        line=46
    )
    evidence: bool | None = Field(
        default=None,
        description="Do you have evidence to support your deduction?",
        page=2,
        line=47,
        box="a"
    )
    written_evidence: bool | None = Field(
        default=None,
        description="If 'Yes' to question 47a, is the evidence written?",
        page=2,
        line=47,
        box="b"
    )
    
    # Part V - Other Expenses
    part_v_title: str | None = Field(
        default="Part V",
        description="Other Expenses section header",
        page=2
    )
    other_expenses: list[dict] = Field(
        default=[],
        description="Other business expenses not included on lines 8-27a, or line 30",
        page=2
    )
    total_other_expenses: float | None = Field(
        default=None,
        description="Total other expenses",
        page=2,
        line=48
    )

    def get_line_fields(self) -> dict[str, str]:
        return {
            "gross_income": "Line 7 (Gross Income)",
            "total_expenses": "Line 28 (Total Expenses)",
            "net_profit_loss": "Line 31 (Net Profit/Loss)"
        }