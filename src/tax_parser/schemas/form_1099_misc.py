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

class Form1099MISC(BaseModel):
    box_1_rents: float | None = Field(
        default=None,
        description="Rents",
        page=1,
        box="1"
    )
    box_2_royalties: float | None = Field(
        default=None,
        description="Royalties",
        page=1,
        box="2"
    )
    box_3_other_income: float | None = Field(
        default=None,
        description="Other income",
        page=1,
        box="3"
    )
    box_4_federal_tax_withheld: float | None = Field(
        default=None,
        description="Federal income tax withheld",
        page=1,
        box="4"
    )
    box_5_fishing_boat_proceeds: float | None = Field(
        default=None,
        description="Fishing boat proceeds",
        page=1,
        box="5"
    )
    box_6_medical_health_care: float | None = Field(
        default=None,
        description="Medical and health care payments",
        page=1,
        box="6"
    )
    box_7_direct_sales: bool | None = Field(
        default=None,
        description="Payer made direct sales totaling $5,000 or more of consumer products to recipient for resale",
        page=1,
        box="7"
    )
    box_8_substitute_payments: float | None = Field(
        default=None,
        description="Substitute payments in lieu of dividends or interest",
        page=1,
        box="8"
    )
    box_9_crop_insurance: float | None = Field(
        default=None,
        description="Crop insurance proceeds",
        page=1,
        box="9"
    )
    box_10_gross_proceeds_attorney: float | None = Field(
        default=None,
        description="Gross proceeds paid to an attorney",
        page=1,
        box="10"
    )
    box_11_fish_purchased: float | None = Field(
        default=None,
        description="Fish purchased for resale",
        page=1,
        box="11"
    )
    box_12_section_409a_deferrals: float | None = Field(
        default=None,
        description="Section 409A deferrals",
        page=1,
        box="12"
    )
    box_13_fatca_filing: str | None = Field(
        default=None,
        description="FATCA filing requirement",
        page=1,
        box="13"
    )
    box_14_blank: str | None = Field(
        default=None,
        description="Blank field",
        page=1,
        box="14"
    )
    box_15_nonqualified_deferred_compensation: float | None = Field(
        default=None,
        description="Nonqualified deferred compensation",
        page=1,
        box="15"
    )
    box_16_state_tax_withheld: float | None = Field(
        default=None,
        description="State tax withheld",
        page=1,
        box="16"
    )
    box_17_state_payers_state_no: str | None = Field(
        default=None,
        description="State/Payer's state no.",
        page=1,
        box="17"
    )
    box_18_state_income: float | None = Field(
        default=None,
        description="State income",
        page=1,
        box="18"
    )


# ---------------------------------------------------------------------------
# Top-level Form 1099-MISC
# ---------------------------------------------------------------------------

class Form1099MISC(BaseTaxForm):
    """Complete IRS Form 1099-MISC schema."""

    form_type: str = "1099-MISC"
    year: int = 2025  # Based on the document (Rev. April 2025)

    payer: PayerInfo = PayerInfo()
    recipient: RecipientInfo = RecipientInfo()
    main: Form1099MISC = Form1099MISC()

    def get_line_fields(self) -> dict[str, str]:
        return {
            "main.box_1_rents": "Box 1, Rents",
            "main.box_2_royalties": "Box 2, Royalties",
            "main.box_3_other_income": "Box 3, Other Income",
            "main.box_7_direct_sales": "Box 7, Direct Sales for Resale",
        }