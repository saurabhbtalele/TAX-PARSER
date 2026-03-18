"""Quality scoring package.

Provides required-fields-based quality scoring for each form type.
Quality = (extracted required fields / total required fields) × 100

Package Structure:
    quality/
    ├── __init__.py            # Public API
    ├── scoring.py             # Core scoring logic
    └── required_fields/       # One file per form type
        ├── __init__.py
        ├── form_1040.py
        ├── form_1065.py
        ├── form_1120.py
        ├── form_1120s.py
        ├── schedule_k1_partnership.py
        └── schedule_k1_scorp.py
"""

from tax_parser.quality.scoring import (
    calculate_required_field_quality,
    get_required_fields,
    resolve_dotted_path,
)

__all__ = [
    "calculate_required_field_quality",
    "get_required_fields",
    "resolve_dotted_path",
]
