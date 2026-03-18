"""Schedule K-1 (S-Corp / Form 1120-S) — Required fields for quality scoring.

Critical fields for S-Corp K-1 analysis:
  Part I: Corporation identification
  Part II: Shareholder identification and ownership
  Part III: Income/deductions
"""

REQUIRED_FIELDS: list[str] = [

    # ── Part I: Information About the Corporation ─────────────────
    "entity.ein",                              # Corporation EIN
    "entity.name",                             # Corporation name
    "entity.address.street",                   # Address
    "entity.address.city",
    "entity.address.state",
    "entity.address.zip",

    # ── Part II: Information About the Shareholder ────────────────
    "shareholder.ssn_or_ein",                  # Box E: Shareholder SSN/EIN
    "shareholder.name",                        # Box F: Shareholder name
    "shareholder.address.street",              # Box F: Address
    "shareholder.address.city",
    "shareholder.address.state",
    "shareholder.address.zip",
    "shareholder.allocation_percentage",       # Box G: Ownership percentage
    "shareholder.shares_beginning",            # Box H: Shares — beginning
    "shareholder.shares_ending",               # Box H: Shares — ending

    # ── Part III: Key Income & Deduction Lines ────────────────────
    "income_deductions.line_1_ordinary_business_income",   # Line 1
    "income_deductions.line_2_net_rental_real_estate",     # Line 2
    "income_deductions.line_4_interest_income",            # Line 4
    "income_deductions.line_5a_ordinary_dividends",        # Line 5a
    "income_deductions.line_11_section_179_deduction",     # Line 11
    "income_deductions.line_12_other_deductions",          # Line 12
]
