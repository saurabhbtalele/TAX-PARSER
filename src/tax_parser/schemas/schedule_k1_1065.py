from __future__ import annotations

from pydantic import BaseModel, Field, field_validator
from typing import Literal
from tax_parser.schemas.base import BaseTaxForm, Address


# ------------------------------------------------------------------
# Part I – Information About the Partnership
# ------------------------------------------------------------------
class EntityInfo(BaseModel):
    """Part I: Partnership-level metadata (Lines A–D)."""
    ein: str | None = Field(
        default=None,
        description="Employer Identification Number (EIN) of the partnership"
    )
    name: str | None = Field(
        default=None,
        description="Legal name of the partnership (as on Form 1065)"
    )
    address: Address = Field(
        default_factory=Address,
        description="Principal business address (Line B)"
    )
    irs_center: str | None = Field(
        default=None,
        description="IRS center where partnership filed return (Line C)"
    )
    publicly_traded_partnership: bool | None = Field(
        default=None,
        description="Check if this is a publicly traded partnership (PTP) (Line D)"
    )


# ------------------------------------------------------------------
# Part II – Information About the Partner
# ------------------------------------------------------------------
class PartnerInfo(BaseModel):
    """Part II: Partner-level identification and classification (Lines E–K)."""
    ssn_or_ein: str | None = Field(
        default=None,
        description="Partner’s SSN or EIN (Line E). Do NOT use TIN of a disregarded entity."
    )
    name: str | None = Field(
        default=None,
        description="Partner’s legal name (Line F)"
    )
    address: Address = Field(
        default_factory=Address,
        description="Partner’s address (Line F)"
    )

    # Partner type & classification (Lines G, H1/H2, I1/I2, J, K1/K2/K3)
    is_general_partner: bool | None = Field(
        default=None,
        description="Checked if general partner or LLC member-manager (Line G)"
    )
    is_limited_partner: bool | None = Field(
        default=None,
        description="Checked if limited partner or other LLC member (Line G)"
    )
    is_domestic_partner: bool | None = Field(
        default=None,
        description="Checked if domestic partner (Line J)"
    )
    is_foreign_partner: bool | None = Field(
        default=None,
        description="Checked if foreign partner (Line J)"
    )
    is_disregarded_entity: bool | None = Field(
        default=None,
        description="Checked if partner is a disregarded entity (DE) (Line K1)"
    )
    partner_type: str | None = Field(
        default=None,
        description="Entity type: individual, corporation, estate, trust, partnership, etc. (Line K2)"
    )
    is_retirement_plan: bool | None = Field(
        default=None,
        description="Checked if partner is an IRA/SEP/Keogh/etc. (Line K3)"
    )

    # Profit, loss, and capital percentages (Line G)
    profit_sharing_beginning: float | None = Field(
        default=None,
        description="Partner’s % share of profits at beginning of tax year (Line G)"
    )
    profit_sharing_ending: float | None = Field(
        default=None,
        description="Partner’s % share of profits at end of tax year (Line G)"
    )
    loss_sharing_beginning: float | None = Field(
        default=None,
        description="Partner’s % share of losses at beginning of tax year (Line G)"
    )
    loss_sharing_ending: float | None = Field(
        default=None,
        description="Partner’s % share of losses at end of tax year (Line G)"
    )
    capital_sharing_beginning: float | None = Field(
        default=None,
        description="Partner’s % share of capital at beginning of tax year (Line G)"
    )
    capital_sharing_ending: float | None = Field(
        default=None,
        description="Partner’s % share of capital at end of tax year (Line G)"
    )

    # Capital account method (Line L)
    capital_account_method: Literal["tax basis", "GAAP", "section 704(b)", "other"] | None = Field(
        default=None,
        description="Method used for capital account (tax basis, GAAP, §704(b), or other)"
    )

    # Liabilities (Lines K1–K3, bottom section)
    nonrecourse_liability_beginning: float | None = Field(
        default=None,
        description="Partner’s share of nonrecourse liabilities at beginning of year (Line K1)"
    )
    nonrecourse_liability_ending: float | None = Field(
        default=None,
        description="Partner’s share of nonrecourse liabilities at end of year (Line K1)"
    )
    qualified_nonrecourse_liability_beginning: float | None = Field(
        default=None,
        description="Partner’s share of qualified nonrecourse financing at beginning (Line K1)"
    )
    qualified_nonrecourse_liability_ending: float | None = Field(
        default=None,
        description="Partner’s share of qualified nonrecourse financing at end (Line K1)"
    )
    recourse_liability_beginning: float | None = Field(
        default=None,
        description="Partner’s share of recourse liabilities at beginning (Line K1)"
    )
    recourse_liability_ending: float | None = Field(
        default=None,
        description="Partner’s share of recourse liabilities at end (Line K1)"
    )

    # Lower-tier partnership liability flag (Line K2)
    includes_lower_tier_liabilities: bool | None = Field(
        default=None,
        description="Checked if liability amounts include lower-tier partnership allocations (Line K2)"
    )

    # Built-in gain/loss contribution (Line M)
    contributed_property_with_builtin_gain_loss: bool | None = Field(
        default=None,
        description="Checked if partner contributed property with built-in gain/loss (Line M)"
    )

    # Section 704(c) gain/loss (Line N)
    section_704c_gain_beginning: float | None = Field(
        default=None,
        description="Partner’s share of net unrecognized §704(c) gain/loss at beginning (Line N)"
    )
    section_704c_gain_ending: float | None = Field(
        default=None,
        description="Partner’s share of net unrecognized §704(c) gain/loss at end (Line N)"
    )


# ------------------------------------------------------------------
# Part III – Partner’s Share of Income, Deductions, Credits, etc.
# ------------------------------------------------------------------
class K1IncomeDeductions(BaseModel):
    """Part III, Lines 1–13: Ordinary items (numeric)."""
    line_1_ordinary_business_income: float | None = Field(
        default=None, description="Ordinary business income (loss) (Line 1)"
    )
    line_2_net_rental_real_estate: float | None = Field(
        default=None, description="Net rental real estate income (loss) (Line 2)"
    )
    line_3_other_net_rental_income: float | None = Field(
        default=None, description="Other net rental income (loss) (Line 3)"
    )
    line_4a_guaranteed_payments_services: float | None = Field(
        default=None, description="Guaranteed payments for services (Line 4a)"
    )
    line_4b_guaranteed_payments_capital: float | None = Field(
        default=None, description="Guaranteed payments for capital (Line 4b)"
    )
    line_4c_total_guaranteed_payments: float | None = Field(
        default=None, description="Total guaranteed payments (Line 4c) = 4a + 4b"
    )
    line_5_interest_income: float | None = Field(
        default=None, description="Interest income (Line 5)"
    )
    line_6a_ordinary_dividends: float | None = Field(
        default=None, description="Ordinary dividends (Line 6a)"
    )
    line_6b_qualified_dividends: float | None = Field(
        default=None, description="Qualified dividends (Line 6b)"
    )
    line_6c_dividend_equivalents: float | None = Field(
        default=None, description="Dividend equivalents (Line 6c)"
    )
    line_7_royalties: float | None = Field(
        default=None, description="Royalties (Line 7)"
    )
    line_8_net_short_term_capital_gain: float | None = Field(
        default=None, description="Net short-term capital gain (loss) (Line 8)"
    )
    line_9a_net_long_term_capital_gain: float | None = Field(
        default=None, description="Net long-term capital gain (loss) (Line 9a)"
    )
    line_9b_collectibles_gain: float | None = Field(
        default=None, description="Collectibles (28%) gain (loss) (Line 9b)"
    )
    line_9c_unrecaptured_section_1250: float | None = Field(
        default=None, description="Unrecaptured section 1250 gain (Line 9c)"
    )
    line_10_net_section_1231_gain: float | None = Field(
        default=None, description="Net §1231 gain (loss) (Line 10)"
    )
    line_11_other_income_loss: float | None = Field(
        default=None, description="Other income (loss) (Line 11)"
    )
    line_12_section_179_deduction: float | None = Field(
        default=None, description="Section 179 deduction (Line 12)"
    )
    line_13_other_deductions: float | None = Field(
        default=None, description="Other deductions (Line 13)"
    )
    line_14_credits: float | None = Field(
        default=None, description="Credits (Line 14)"
    )

    @field_validator("line_4c_total_guaranteed_payments", mode="before")
    @classmethod
    def validate_guaranteed_payments(cls, v, info):
        if v is None:
            a = info.data.get("line_4a_guaranteed_payments_services")
            b = info.data.get("line_4b_guaranteed_payments_capital")
            if a is not None and b is not None:
                return a + b
        return v


class K1SelfEmployment(BaseModel):
    """Part III, Line 15: Self-employment earnings (partnership-only)."""
    line_15_net_earnings: float | None = Field(
        default=None, description="Net earnings from self-employment (Line 15)"
    )
    line_15_gross_farming_income: float | None = Field(
        default=None, description="Gross farming income (Line 15a)"
    )
    line_15_gross_nonfarm_income: float | None = Field(
        default=None, description="Gross nonfarm income (Line 15b)"
    )


class K1ForeignTransactions(BaseModel):
    """Part III, Lines 16–21: Foreign items."""
    line_16a_foreign_country: str | None = Field(
        default=None, description="Foreign country (Line 16a)"
    )
    line_16b_foreign_gross_income: float | None = Field(
        default=None, description="Foreign gross income (Line 16b)"
    )
    line_16c_foreign_deductions: float | None = Field(
        default=None, description="Foreign deductions (Line 16c)"
    )
    line_16d_total_foreign_taxes: float | None = Field(
        default=None, description="Total foreign taxes paid/accrued (Line 16d)"
    )
    line_16e_reduction_in_taxes: float | None = Field(
        default=None, description="Reduction in foreign taxes (Line 16e)"
    )
    line_21_foreign_taxes_paid: float | None = Field(
        default=None, description="Foreign taxes paid or accrued (Line 21)"
    )


class K1AMTItems(BaseModel):
    """Part III, Line 17: Alternative Minimum Tax (AMT) items."""
    line_17a_post_1986_depreciation: float | None = Field(
        default=None, description="Post-1986 depreciation (Line 17a)"
    )
    line_17b_adjusted_gain_loss: float | None = Field(
        default=None, description="Adjusted gain or loss (Line 17b)"
    )
    line_17c_depletion: float | None = Field(
        default=None, description="Depletion (Line 17c)"
    )
    line_17d_oil_gas_gross_income: float | None = Field(
        default=None, description="Oil, gas, and geothermal gross income (Line 17d)"
    )
    line_17e_other_amt_items: float | None = Field(
        default=None, description="Other AMT items (Line 17e)"
    )


class K1OtherInfo(BaseModel):
    """Part III, Lines 18–20 & 22–23: Supplemental disclosures."""
    line_18_tax_exempt_income: float | None = Field(
        default=None, description="Tax-exempt income (Line 18)"
    )
    line_19_distributions: float | None = Field(
        default=None, description="Distributions (Line 19)"
    )
    line_20_other_information: str | None = Field(
        default=None, description="Other information (Line 20)"
    )
    line_22_at_risk_multiple_activities: bool | None = Field(
        default=None, description="More than one activity for at-risk purposes (Line 22)"
    )
    line_23_passive_multiple_activities: bool | None = Field(
        default=None, description="More than one activity for passive activity purposes (Line 23)"
    )


class PartnerCapitalAccountAnalysis(BaseModel):
    """Section L: Partner’s Capital Account Analysis."""
    beginning_capital_account: float | None = Field(
        default=None, description="Beginning capital account (Line L)"
    )
    capital_contributed: float | None = Field(
        default=None, description="Capital contributed during the year"
    )
    current_year_net_income_loss: float | None = Field(
        default=None, description="Current year net income (loss) (allocated to partner)"
    )
    other_increase_decrease: float | None = Field(
        default=None, description="Other increase (decrease) — attach explanation"
    )
    withdrawals_distributions: float | None = Field(
        default=None, description="Withdrawals and distributions"
    )
    ending_capital_account: float | None = Field(
        default=None, description="Ending capital account"
    )

    @field_validator("ending_capital_account", mode="before")
    @classmethod
    def validate_capital_balance(cls, v, info):
        if v is None:
            b = info.data.get("beginning_capital_account")
            c = info.data.get("capital_contributed")
            i = info.data.get("current_year_net_income_loss")
            o = info.data.get("other_increase_decrease")
            w = info.data.get("withdrawals_distributions")
            if all(x is not None for x in [b, c, i, o, w]):
                return b + c + i + o - w
        return v


# ------------------------------------------------------------------
# Top-level Schedule K-1 (Partnership)
# ------------------------------------------------------------------
class ScheduleK1Partnership(BaseTaxForm):
    """
    Schedule K-1 (Form 1065) 2023 — Partner’s Share of Income, Deductions, Credits, and Other Items.
    """

    form_type: Literal["Schedule K-1 (Partnership)"] = "Schedule K-1 (Partnership)"

    # Part I
    entity: EntityInfo = Field(default_factory=EntityInfo)

    # Part II
    partner: PartnerInfo = Field(default_factory=PartnerInfo)

    # Part III — core numeric items
    income_deductions: K1IncomeDeductions = Field(default_factory=K1IncomeDeductions)
    self_employment: K1SelfEmployment = Field(default_factory=K1SelfEmployment)
    foreign_transactions: K1ForeignTransactions = Field(default_factory=K1ForeignTransactions)
    amt_items: K1AMTItems = Field(default_factory=K1AMTItems)
    other: K1OtherInfo = Field(default_factory=K1OtherInfo)

    # Capital Account Analysis (Section L)
    capital_account: PartnerCapitalAccountAnalysis = Field(default_factory=PartnerCapitalAccountAnalysis)

    # Metadata / flags
    is_final_k1: bool | None = Field(
        default=None, description="Checked if this is a final K-1 (top left)"
    )
    is_amended_k1: bool | None = Field(
        default=None, description="Checked if this is an amended K-1 (top left)"
    )

    source_pdf_version: str = Field(
        default="2023",
        description="Version identifier"
    )
