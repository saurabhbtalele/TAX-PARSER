"""Form 1099-NEC - Required fields for quality scoring."""

REQUIRED_FIELDS: list[str] = [
    # ── Payer Information ──────────────────────────────────────
    "payer.tin",                               # Payer's TIN
    "payer.name",                              # Payer's name
    
    # ── Recipient Information ──────────────────────────────────
    "recipient.tin",                           # Recipient's TIN
    "recipient.name",                          # Recipient's name

    # ── Critical Income Information ────────────────────────────
    "main.box_1_nonemployee_compensation",     # Box 1: Nonemployee compensation
    "main.box_4_backup_withholding",           # Box 4: Backup withholding
]
