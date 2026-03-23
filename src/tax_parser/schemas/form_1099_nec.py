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

class Form1099NEC(BaseModel):
    box_1_nonemployee_compensation: float | None = Field(
        default=None,
        description="Nonemployee compensation",
        page=1,
        box="1"
    )
    box_2_direct_sales: bool | None = Field(
        default=None,
        description="Payer made direct sales totaling $5,000 or more of consumer products to recipient for resale",
        page=1,
        box="2"
    )
    box_3_excess_golden_parachute: float | None = Field(
        default=None,
        description="Excess golden parachute payments",
        page=1,
        box="3"
    )
    box_4_backup_withholding: float | None = Field(
        default=None,
        description="Backup withholding",
        page=1,
        box="4"
    )
    box_5_state_tax_withheld: float | None = Field(
        default=None,
        description="State tax withheld",
        page=1,
        box="5"
    )
    box_6_state_payers_state_no: str | None = Field(
        default=None,
        description="State/Payer's state no.",
        page=1,
        box="6"
    )
    box_7_state_income: float | None = Field(
        default=None,
        description="State income",
        page=1,
        box="7"
    )


# ---------------------------------------------------------------------------
# Top-level Form 1099-NEC
# ---------------------------------------------------------------------------

class Form1099NEC(BaseTaxForm):
    """Complete IRS Form 1099-NEC schema."""

    form_type: str = "1099-NEC"
    year: int = 2025  # Based on the document (Rev. April 2025)

    payer: PayerInfo = PayerInfo()
    recipient: RecipientInfo = RecipientInfo()
    main: Form1099NEC = Form1099NEC()

    def get_line_fields(self) -> dict[str, str]:
        return {
            "main.box_1_nonemployee_compensation": "Box 1, Nonemployee Compensation",
            "main.box_2_direct_sales": "Box 2, Direct Sales for Resale",
            "main.box_3_excess_golden_parachute": "Box 3, Excess Golden Parachute Payments",
            "main.box_4_backup_withholding": "Box 4, Backup Withholding",
        }