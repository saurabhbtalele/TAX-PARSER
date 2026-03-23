"""Form 1099-MISC - Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    # ── Payer Information ──────────────────────────────────────
    "payer.tin",                               # Payer's TIN
    "payer.name",                              # Payer's name
    
    # ── Recipient Information ──────────────────────────────────
    "recipient.tin",                           # Recipient's TIN
    "recipient.name",                          # Recipient's name

    # ── Critical Income Information ────────────────────────────
    "main.box_1_rents",                        # Box 1: Rents
    "main.box_2_royalties",                    # Box 2: Royalties
    "main.box_3_other_income",                 # Box 3: Other income
    "main.box_4_federal_tax_withheld",         # Box 4: Federal income tax withheld
]
