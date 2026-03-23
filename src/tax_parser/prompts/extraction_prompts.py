"""Per-form extraction prompts for the GPT-4o LLM extractor.

Each prompt instructs the model to return structured JSON matching the
Pydantic schema for that form type. The JSON schema is injected at runtime.
"""

from __future__ import annotations

from tax_parser.models.result import FormType

# ---------------------------------------------------------------------------
# Shared preamble
# ---------------------------------------------------------------------------

_PREAMBLE = """\
You are an expert US tax document data extractor. You will be given scanned images of \
an IRS tax form. Extract ALL data from the form into the JSON structure defined below.

RULES:
1. Return ONLY valid JSON – no markdown fences, no commentary.
2. Use null for any field that is blank, illegible, or not present on the form.
3. For monetary amounts, return plain numbers (no $ signs, no commas). Negative values use a minus sign.
4. For checkboxes, return true if checked, false if unchecked, null if unclear.
5. For percentages, return the decimal form if on the form (e.g. 100% → 100.0).
6. If a field has a "See Statement" or similar reference, extract the reference text as the value.
7. For dates, use the format shown on the form (typically MM/DD/YYYY or MM-DD-YYYY).
8. If there is a watermark (e.g. "Client Copy"), ignore it completely.
9. For each field, also estimate your confidence (0.0 to 1.0) that the extracted value is correct.

CRITICAL: Extract values from EVERY line on the form, even if a line appears blank (use null). \
Do not skip any section or schedule shown in the images.
"""

# ---------------------------------------------------------------------------
# Form-specific instructions
# ---------------------------------------------------------------------------

_FORM_1120S_INSTRUCTIONS = """\
This is IRS Form 1120-S (U.S. Income Tax Return for an S Corporation).

The form typically spans multiple pages:
- Page 1: Header info (name, EIN, address, activity codes) + Income (lines 1-6) + Deductions (lines 7-20) + Tax/Payments (lines 21-27)
- Page 2: Schedule B – Other Information (yes/no questions)
- Page 3: Schedule K – Shareholders' Pro Rata Share Items (lines 1-18)
- Page 4: Schedule L – Balance Sheets per Books (beginning/end of year columns) + Schedule M-1 + Schedule M-2

Extract the complete data into the following JSON schema:
"""

_FORM_1120_INSTRUCTIONS = """\
This is IRS Form 1120 (U.S. Corporation Income Tax Return).

The form typically spans multiple pages:
- Page 1: Header info + Income (lines 1-11) + Deductions (lines 12-27) + Tax (lines 28-35)
- Schedule C: Dividends, Inclusions, and Special Deductions
- Schedule J: Tax Computation and Payment

Extract the complete data into the following JSON schema:
"""

_FORM_1065_INSTRUCTIONS = """\
This is IRS Form 1065 (U.S. Return of Partnership Income).

The form typically spans multiple pages:
- Page 1: Header info + Income (lines 1-8) + Deductions (lines 9-22)
- Schedule K: Partners' Distributive Share Items
- Schedule L: Balance Sheets per Books

Extract the complete data into the following JSON schema:
"""

_K1_PARTNERSHIP_INSTRUCTIONS = """\
This is Schedule K-1 (Form 1065) – Partner's Share of Income, Deductions, Credits, etc.

The form has three main parts:
- Part I: Information About the Partnership (name, EIN, address)
- Part II: Information About the Partner (name, SSN/EIN, ownership %, capital account)
- Part III: Partner's Share of Current Year Income, Deductions, Credits, and Other Items (lines 1-20)

Extract the complete data into the following JSON schema:
"""

_K1_SCORP_INSTRUCTIONS = """\
This is Schedule K-1 (Form 1120-S) – Shareholder's Share of Income, Deductions, Credits, etc.

The form has three main parts:
- Part I: Information About the Corporation (name, EIN, address)
- Part II: Information About the Shareholder (name, SSN/EIN, ownership %)
- Part III: Shareholder's Share of Current Year Income, Deductions, Credits, and Other Items

Extract the complete data into the following JSON schema:
"""

_FORM_1099_MISC_INSTRUCTIONS = """\
This is IRS Form 1099-MISC (Miscellaneous Information).

The form contains information about miscellaneous income such as rents, royalties, other income, substitute payments, etc.

Extract the complete data into the following JSON schema:
"""

_FORM_1099_NEC_INSTRUCTIONS = """\
This is IRS Form 1099-NEC (Nonemployee Compensation).

The form contains information about nonemployee compensation, direct sales, backup withholding, state tax withheld, etc.

Extract the complete data into the following JSON schema:
"""

_FORM_1099_R_INSTRUCTIONS = """\
This is IRS Form 1099-R (Distributions From Pensions, Annuities, Retirement or Profit-Sharing Plans, IRAs, Insurance Contracts, etc.).

The form contains information about gross distribution, taxable amount, capital gain, federal income tax withheld, employee contributions, etc.

Extract the complete data into the following JSON schema:
"""

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

FORM_INSTRUCTIONS: dict[FormType, str] = {
    FormType.FORM_1120S: _FORM_1120S_INSTRUCTIONS,
    FormType.FORM_1120: _FORM_1120_INSTRUCTIONS,
    FormType.FORM_1065: _FORM_1065_INSTRUCTIONS,
    FormType.SCHEDULE_K1_PARTNERSHIP: _K1_PARTNERSHIP_INSTRUCTIONS,
    FormType.SCHEDULE_K1_SCORP: _K1_SCORP_INSTRUCTIONS,
    FormType.FORM_1099_MISC: _FORM_1099_MISC_INSTRUCTIONS,
    FormType.FORM_1099_NEC: _FORM_1099_NEC_INSTRUCTIONS,
    FormType.FORM_1099_R: _FORM_1099_R_INSTRUCTIONS,
}


def build_extraction_prompt(form_type: FormType, json_schema: dict) -> str:
    """Build the full extraction prompt for a given form type.

    Args:
        form_type: The form type to extract.
        json_schema: The Pydantic JSON schema dict to include in the prompt.

    Returns:
        Complete prompt string.
    """
    import json

    instructions = FORM_INSTRUCTIONS.get(form_type, "")
    schema_str = json.dumps(json_schema, indent=2)

    confidence_addendum = """

IMPORTANT: In addition to the main JSON object, include a top-level key "field_confidence" \
that maps dotted field paths to confidence scores (0.0-1.0). Example:
{
  "form_type": "1120-S",
  "tax_year": "2022",
  "...": "...",
  "field_confidence": {
    "taxpayer.name": 0.99,
    "taxpayer.ein": 0.97,
    "income.line_1a_gross_receipts": 0.95,
    "income.line_6_total_income": 0.90
  }
}

Only include fields that you extracted (not null fields) in field_confidence. \
Return the JSON object now.
"""

    return _PREAMBLE + "\n\n" + instructions + "\n\n```json\n" + schema_str + "\n```\n" + confidence_addendum
