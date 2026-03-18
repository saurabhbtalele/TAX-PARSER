"""Schedule K-1 (Partnership / Form 1065) — Required fields for quality scoring.

These are the critical fields that mortgage underwriters and tax professionals
MUST see for a complete K-1 analysis. Based on IRS Form 1065 K-1:
  Part I: Partnership identification
  Part II: Partner identification and ownership
  Part III: Income/deductions
  Section L: Capital account analysis

Field paths correspond to structured_data keys from the schema:
  ScheduleK1Partnership → entity, partner, income_deductions, capital_account
"""

REQUIRED_FIELDS: list[str] = [

    # ── Part I: Information About the Partnership ─────────────────
    "entity.ein",                              # Box A: Partnership EIN
    "entity.name",                             # Box B: Partnership legal name
    "entity.address.street",                   # Box B: Street address
    "entity.address.city",                     # Box B: City
    "entity.address.state",                    # Box B: State
    "entity.address.zip",                      # Box B: ZIP
    "entity.irs_center",                       # Box C: IRS Service Center
    "entity.publicly_traded_partnership",      # Box D: PTP flag

    # ── Part II: Information About the Partner ────────────────────
    "partner.ssn_or_ein",                      # Box E: Partner SSN/ITIN
    "partner.name",                            # Box F: Partner name
    "partner.address.street",                  # Box F: Partner street address
    "partner.address.city",                    # Box F: City
    "partner.address.state",                   # Box F: State
    "partner.address.zip",                     # Box F: ZIP
    "partner.is_general_partner",              # Box G: General partner / LLC member-manager
    "partner.is_domestic_partner",             # Box H: Domestic partner flag
    "partner.partner_type",                    # Box I1: Entity type (Individual, Corp, Trust)

    # Box J: Partner's Share of Profit, Loss, and Capital
    "partner.profit_sharing_beginning",        # Profit % — Beginning
    "partner.profit_sharing_ending",           # Profit % — Ending (used by lenders)
    "partner.loss_sharing_beginning",          # Loss % — Beginning
    "partner.loss_sharing_ending",             # Loss % — Ending
    "partner.capital_sharing_beginning",       # Capital % — Beginning
    "partner.capital_sharing_ending",          # Capital % — Ending

    # Box K: Partner's Share of Liabilities
    "partner.nonrecourse_liability_ending",            # Nonrecourse
    "partner.qualified_nonrecourse_liability_ending",  # Qualified nonrecourse
    "partner.recourse_liability_ending",               # Recourse

    # ── Section L: Partner's Capital Account Analysis ─────────────
    "capital_account.beginning_capital_account",      # Beginning balance
    "capital_account.capital_contributed",             # Capital contributed
    "capital_account.current_year_net_income_loss",   # Current year net income/loss
    "capital_account.other_increase_decrease",        # Other increase/decrease
    "capital_account.withdrawals_distributions",      # Withdrawals & distributions
    "capital_account.ending_capital_account",          # Ending balance

    # ── Part III: Key Income & Deduction Lines ────────────────────
    "income_deductions.line_1_ordinary_business_income",    # Line 1: Ordinary income
    "income_deductions.line_2_net_rental_real_estate",      # Line 2: Net rental RE
    "income_deductions.line_4c_total_guaranteed_payments",  # Line 4c: Total guaranteed payments
    "income_deductions.line_5_interest_income",             # Line 5: Interest income
    "income_deductions.line_6a_ordinary_dividends",         # Line 6a: Ordinary dividends
    "income_deductions.line_19_distributions",              # Line 19: Distributions (via other)

    # Self-employment
    "self_employment.line_15_net_earnings",                 # Line 15: SE earnings
]
