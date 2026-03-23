"""Form 1099-R - Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    # ── Payer Information ──────────────────────────────────────
    "payer.tin",                               # Payer's TIN
    "payer.name",                              # Payer's name
    
    # ── Recipient Information ──────────────────────────────────
    "recipient.tin",                           # Recipient's TIN
    "recipient.name",                          # Recipient's name

    # ── Critical Income Information ────────────────────────────
    "main.box_1_gross_distribution",           # Box 1: Gross distribution
    "main.box_2a_taxable_amount",              # Box 2a: Taxable amount
    "main.box_4_federal_tax_withheld",         # Box 4: Federal income tax withheld
    "main.box_7_ira_sep_simple",               # Box 7: IRA/SEP/SIMPLE flag or code
]
