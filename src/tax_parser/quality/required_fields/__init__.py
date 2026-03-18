"""Required fields registry — aggregates all per-form-type definitions."""

from __future__ import annotations

from tax_parser.models.result import FormType
from tax_parser.quality.required_fields.form_1040 import REQUIRED_FIELDS as FORM_1040
from tax_parser.quality.required_fields.form_1065 import REQUIRED_FIELDS as FORM_1065
from tax_parser.quality.required_fields.form_1120 import REQUIRED_FIELDS as FORM_1120
from tax_parser.quality.required_fields.form_1120s import REQUIRED_FIELDS as FORM_1120S
from tax_parser.quality.required_fields.schedule_k1_partnership import REQUIRED_FIELDS as K1_PARTNERSHIP
from tax_parser.quality.required_fields.schedule_k1_scorp import REQUIRED_FIELDS as K1_SCORP

REQUIRED_FIELDS_REGISTRY: dict[FormType, list[str]] = {
    FormType.FORM_1040: FORM_1040,
    FormType.FORM_1065: FORM_1065,
    FormType.FORM_1120: FORM_1120,
    FormType.FORM_1120S: FORM_1120S,
    FormType.SCHEDULE_K1_PARTNERSHIP: K1_PARTNERSHIP,
    FormType.SCHEDULE_K1_SCORP: K1_SCORP,
}
