"""Core scoring logic — form-type agnostic."""

from __future__ import annotations

from typing import Any

from tax_parser.models.result import FormType
from tax_parser.quality.required_fields import REQUIRED_FIELDS_REGISTRY


def get_required_fields(form_type: FormType) -> list[str]:
    """Return the list of required field paths for a form type."""
    return REQUIRED_FIELDS_REGISTRY.get(form_type, [])


def resolve_dotted_path(data: dict, path: str) -> Any:
    """Walk a dotted path like 'entity.ein' into nested dict.
    Returns the value at that path, or None if any key is missing.
    """
    keys = path.split(".")
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
        if current is None:
            return None
    return current


def calculate_required_field_quality(
    structured_data: dict, form_type: FormType
) -> tuple[float, int, int]:
    """
    Calculate quality based on required fields.
    
    Why we do this:
    In the Mortgage Industry, underwriters need fixed data points (EIN, Dividends, etc.).
    A high score (100%) means the AI successfully identified and extracted ALL 
    critical fields.
    
    Logic:
    - total: Total number of required fields for this form type (e.g., 39 for K-1 Partnership).
    - found: AI emitted this key in JSON (key exists, value is not None).
             This shows 'Model Recognition' - the AI found where the field should be.
    - extracted: AI pulled a meaningful value (not None).
                 IMPORTANT: 0, False, and "" ARE valid extractions in tax forms!
                 e.g. Line 1: Ordinary Income = 0 is a real, valid data point.
                 Only None (field missing entirely) counts as "not extracted".

    Returns:
        (quality_score 0-100, fields_found, fields_required)
    """
    required = get_required_fields(form_type)
    if not required:
        return 0.0, 0, 0

    found_keys = 0
    extracted_values = 0
    
    for path in required:
        value = resolve_dotted_path(structured_data, path)
        
        # resolve_dotted_path returns None if key is missing from the JSON.
        # Any non-None value means the model both recognized AND extracted the field.
        # In tax forms, 0, False, and "" are legitimate extracted values:
        #   - Income line = 0 means $0 income (valid data)
        #   - Checkbox = False means unchecked (valid data)
        #   - Empty string for optional text fields (valid recognition)
        
        if value is not None:
            found_keys += 1
            extracted_values += 1

    # Quality = percentage of required fields that were found and extracted.
    # Since recognition and extraction are now equivalent (both require non-None),
    # the score directly reflects data completeness.
    quality = (extracted_values / len(required)) * 100
    
    return round(quality, 1), found_keys, len(required)
