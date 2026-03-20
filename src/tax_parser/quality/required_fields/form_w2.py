"""Form W-2 (Wage and Tax Statement) — Required fields for quality scoring.

These are the critical fields that mortgage underwriters and tax professionals
MUST see for a complete W-2 analysis. Based on IRS Form W-2:
  - Box a: Employee Social Security Number
  - Box b: Employer Identification Number (EIN)
  - Box c: Employer name, address, and ZIP code
  - Box 1: Wages, tips, other compensation
  - Box 2: Federal income tax withheld
  - Box 15: State, Employer's state ID number
  - Box 16: State wages, tips, etc.
  - Box 17: State income tax
"""

REQUIRED_FIELDS: list[str] = [
    # ── Employer Information ───────────────────────────────────
    "employer_info.ein",                       # Box b
    "employer_info.name",                      # Box c
    "employer_info.address",                   # Box c
    
    # ── Employee Information ───────────────────────────────────
    "employee_info.social_security_number",    # Box a
    "employee_info.first_name",                # Box e
    "employee_info.last_name",                 # Box e
    "employee_info.address",                   # Box f

    # ── Wage and Tax Information ──────────────────────────────
    "wage_tax_info.wages_tips_compensation",   # Box 1
    "wage_tax_info.federal_income_tax_withheld", # Box 2
    "wage_tax_info.social_security_wages",      # Box 3
    "wage_tax_info.social_security_tax_withheld", # Box 4
    "wage_tax_info.medicare_wages_tips",        # Box 5
    "wage_tax_info.medicare_tax_withheld",      # Box 6
    
    # ── State Information ──────────────────────────────────────
    "wage_tax_info.state_wages_tips",           # Box 16
    "wage_tax_info.state_income_tax",           # Box 17
    "employer_info.state_id_number",            # Box 15
]
