"""Schedule K-1 (S-Corp / Form 1120-S) — Required fields for quality scoring.

Critical fields for S-Corp K-1 analysis:
  Part I: Corporation identification
  Part II: Shareholder identification and ownership
  Part III: Income/deductions
"""

REQUIRED_FIELDS: list[str] = [
    # ── Part I: Information About the Corporation ─────────────────
    "ein",                                     # Corporation EIN
    "corporation_name",                        # Corporation name (Box B)
    
    # ── Part II: Information About the Shareholder ────────────────
    "ssn_or_ein",                              # Box E: Shareholder SSN/EIN
    "shareholder_name",                        # Box F: Shareholder name
    "allocation_percentage",                   # Box G: Ownership percentage
    "shares_beginning",                        # Box H: Shares — beginning
    "shares_ending",                           # Box H: Shares — ending

    # ── Part III: Key Income & Deduction Lines ────────────────────
    "ordinary_business_income",                # Line 1
    "net_rental_real_estate",                  # Line 2
    "interest_income",                         # Line 4
    "ordinary_dividends",                      # Line 5a
    "section_179_deduction",                   # Line 11
    "other_deductions",                        # Line 12
]
