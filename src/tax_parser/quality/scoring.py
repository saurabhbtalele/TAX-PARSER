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
    - found: AI emitted this key in JSON with any value (including 0 or empty string).
             This shows 'Model Recognition' - the AI found where the field should be.
    - extracted: AI pulled a non-null, non-empty value. 
                 This shows 'Extraction Coverage' - the field has actual data for underwriting.

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
        
        # If the key exists in the path resolution (not None/Missing)
        # In our implementation, resolve_dotted_path returns None if key is missing.
        # But for tax forms, '0' or '' are real extractions.
        
        if value is not None:
            found_keys += 1
            # If it's a "real" value (non-empty string, non-zero number)
            if value != "" and value != 0:
                extracted_values += 1

    # Final Quality Score is a weighted blend:
    # Finding the field is 40% of the score (AI intelligence)
    # Extracting a non-empty value is 60% of the score (Data completeness)
    
    recognition_score = (found_keys / len(required)) * 100
    extraction_score = (extracted_values / len(required)) * 100
    
    # Simple average for now, but leans towards discovery as requested
    quality = (recognition_score * 0.5) + (extraction_score * 0.5)
    
    return round(quality, 1), found_keys, len(required)
