from __future__ import annotations

from pydantic import BaseModel, Field

from tax_parser.schemas.base import BaseTaxForm, TaxpayerInfo


# ---------------------------------------------------------------------------
# Header / Payer Information
# ---------------------------------------------------------------------------

class PayerInfo(BaseModel):
    name: str | None = Field(
        default=None,
        description="Payer's name",
        page=1,
        box="PAYER'S name"
    )
    address: str | None = Field(
        default=None,
        description="Payer's street address (including apt. no.)",
        page=1,
        box="Street address"
    )
    city_state_country_zip: str | None = Field(
        default=None,
        description="Payer's city or town, state or province, country, and ZIP or foreign postal code",
        page=1,
        box="City or town, state or province, country, and ZIP or foreign postal code"
    )
    telephone: str | None = Field(
        default=None,
        description="Payer's telephone number",
        page=1,
        box="telephone no."
    )
    tin: str | None = Field(
        default=None,
        description="Payer's TIN (Taxpayer Identification Number)",
        page=1,
        box="PAYER'S TIN"
    )
    account_number: str | None = Field(
        default=None,
        description="Account number (see instructions)",
        page=1,
        box="Account number"
    )


# ---------------------------------------------------------------------------
# Recipient Information
# ---------------------------------------------------------------------------

class RecipientInfo(BaseModel):
    name: str | None = Field(
        default=None,
        description="Recipient's name",
        page=1,
        box="RECIPIENT'S name"
    )
    address: str | None = Field(
        default=None,
        description="Recipient's street address (including apt. no.)",
        page=1,
        box="Street address"
    )
    city_state_country_zip: str | None = Field(
        default=None,
        description="Recipient's city or town, state or province, country, and ZIP or foreign postal code",
        page=1,
        box="City or town, state or province, country, and ZIP or foreign postal code"
    )
    tin: str | None = Field(
        default=None,
        description="Recipient's TIN (Taxpayer Identification Number)",
        page=1,
        box="RECIPIENT'S TIN"
    )


# ---------------------------------------------------------------------------
# Main Form Fields
# ---------------------------------------------------------------------------

class Form1099R(BaseModel):
    box_1_gross_distribution: float | None = Field(
        default=None,
        description="Gross distribution",
        page=1,
        box="1"
    )
    box_2a_taxable_amount: float | None = Field(
        default=None,
        description="Taxable amount",
        page=1,
        box="2a"
    )
    box_2b_taxable_not_determined: bool | None = Field(
        default=None,
        description="Taxable amount not determined",
        page=1,
        box="2b"
    )
    box_3_capital_gain: float | None = Field(
        default=None,
        description="Capital gain (included in box 2a)",
        page=1,
        box="3"
    )
    box_4_federal_tax_withheld: float | None = Field(
        default=None,
        description="Federal income tax withheld",
        page=1,
        box="4"
    )
    box_5_employee_contributions: float | None = Field(
        default=None,
        description="Employee contributions/Designated Roth contributions or insurance",
        page=1,
        box="5"
    )
    box_6_distribution_code: str | None = Field(
        default=None,
        description="Distribution code(s)",
        page=1,
        box="6"
    )
    box_7_ira_sep_simple: str | None = Field(
        default=None,
        description="IRA/SEP/SIMPLE",
        page=1,
        box="7"
    )
    box_8_other: float | None = Field(
        default=None,
        description="Other",
        page=1,
        box="8"
    )
    box_9a_percentage_total_distribution: float | None = Field(
        default=None,
        description="Your percentage of total distribution",
        page=1,
        box="9a"
    )
    box_9b_percentage_total_distribution: float | None = Field(
        default=None,
        description="Your percentage of total distribution (repeated)",
        page=1,
        box="9b"
    )
    box_10_irr_within_5_years: float | None = Field(
        default=None,
        description="Amount allocable to IRR within 5 years",
        page=1,
        box="10"
    )
    box_11_first_year_roth: bool | None = Field(
        default=None,
        description="1st year of designated Roth contribution",
        page=1,
        box="11"
    )
    box_12_fatca_filing: str | None = Field(
        default=None,
        description="FATCA filing requirement",
        page=1,
        box="12"
    )
    box_13_date_of_payment: str | None = Field(
        default=None,
        description="Date of payment",
        page=1,
        box="13"
    )
    box_14_state_tax_withheld: float | None = Field(
        default=None,
        description="State tax withheld",
        page=1,
        box="14"
    )
    box_15_state_payers_state_no: str | None = Field(
        default=None,
        description="State/Payer's state no.",
        page=1,
        box="15"
    )
    box_16_state_distribution: float | None = Field(
        default=None,
        description="State distribution",
        page=1,
        box="16"
    )
    box_17_local_tax_withheld: float | None = Field(
        default=None,
        description="Local tax withheld",
        page=1,
        box="17"
    )
    box_18_locality_name: str | None = Field(
        default=None,
        description="Name of locality",
        page=1,
        box="18"
    )
    box_19_local_distribution: float | None = Field(
        default=None,
        description="Local distribution",
        page=1,
        box="19"
    )


# ---------------------------------------------------------------------------
# Top-level Form 1099-R
# ---------------------------------------------------------------------------

class Form1099R(BaseTaxForm):
    """Complete IRS Form 1099-R schema."""

    form_type: str = "1099-R"
    year: int = 2025  # Based on the document (Rev. April 2025)

    payer: PayerInfo = PayerInfo()
    recipient: RecipientInfo = RecipientInfo()
    main: Form1099R = Form1099R()

    def get_line_fields(self) -> dict[str, str]:
        return {
            "main.box_1_gross_distribution": "Box 1, Gross Distribution",
            "main.box_4_federal_tax_withheld": "Box 4, Federal Income Tax Withheld",
            "main.box_6_distribution_code": "Box 6, Distribution Code(s)",
            "main.box_12_fatca_filing": "Box 12, FATCA Filing Requirement",
        }