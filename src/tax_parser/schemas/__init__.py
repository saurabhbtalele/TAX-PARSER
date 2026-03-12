"""Schema registry – maps FormType to its Pydantic model class."""

from __future__ import annotations

from typing import Type

from tax_parser.models.result import FormType
from tax_parser.schemas.base import BaseTaxForm
from tax_parser.schemas.form_1040 import Form1040
from tax_parser.schemas.form_1065 import Form1065
from tax_parser.schemas.form_1120 import Form1120
from tax_parser.schemas.form_1120s import Form1120S
from tax_parser.schemas.schedule_k1_1065 import ScheduleK1Partnership
from tax_parser.schemas.schedule_k1_1120s import ScheduleK1SCorp

# Registry: FormType enum → schema class
SCHEMA_REGISTRY: dict[FormType, Type[BaseTaxForm]] = {
    FormType.FORM_1040: Form1040,
    FormType.FORM_1065: Form1065,
    FormType.FORM_1120: Form1120,
    FormType.FORM_1120S: Form1120S,
    FormType.SCHEDULE_K1_PARTNERSHIP: ScheduleK1Partnership,
    FormType.SCHEDULE_K1_SCORP: ScheduleK1SCorp,
}


def get_schema_for_form(form_type: FormType) -> Type[BaseTaxForm] | None:
    """Return the Pydantic schema class for a given form type."""
    return SCHEMA_REGISTRY.get(form_type)


def get_json_schema_for_form(form_type: FormType) -> dict | None:
    """Return the JSON schema dict for a given form type (used in LLM prompts)."""
    schema_cls = SCHEMA_REGISTRY.get(form_type)
    if schema_cls is None:
        return None
    return schema_cls.model_json_schema()


__all__ = [
    "SCHEMA_REGISTRY",
    "get_schema_for_form",
    "get_json_schema_for_form",
    "Form1040",
    "Form1065",
    "Form1120",
    "Form1120S",
    "ScheduleK1Partnership",
    "ScheduleK1SCorp",
]
