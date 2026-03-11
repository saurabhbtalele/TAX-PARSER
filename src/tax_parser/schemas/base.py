"""Base schema and common field definitions shared across tax forms."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Address(BaseModel):
    street: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = Field(default="US")


class TaxpayerInfo(BaseModel):
    name: str | None = None
    ein: str | None = Field(default=None, description="Employer Identification Number (XX-XXXXXXX)")
    ssn: str | None = Field(default=None, description="Social Security Number (XXX-XX-XXXX)")
    address: Address = Address()


class BaseTaxForm(BaseModel):
    """Base class for all tax form schemas."""

    form_type: str
    tax_year: str | None = None
    taxpayer: TaxpayerInfo = TaxpayerInfo()

    def get_line_fields(self) -> dict[str, str]:
        """Return a mapping of field_name → IRS line reference for validation."""
        return {}
