"""Tests for schema registry and Pydantic models."""

import json

import pytest

from tax_parser.models.result import FormType
from tax_parser.schemas import get_json_schema_for_form, get_schema_for_form, SCHEMA_REGISTRY
from tax_parser.schemas.form_1120s import Form1120S
from tax_parser.schemas.form_1120 import Form1120
from tax_parser.schemas.form_1065 import Form1065
from tax_parser.schemas.schedule_k1 import ScheduleK1Partnership, ScheduleK1SCorp


class TestSchemaRegistry:
    def test_all_llm_forms_have_schemas(self):
        """Every LLM extraction form must have a registered schema."""
        from tax_parser.models.result import LLM_EXTRACTION_FORMS

        for ft in LLM_EXTRACTION_FORMS:
            schema = get_schema_for_form(ft)
            assert schema is not None, f"Missing schema for {ft.value}"

    def test_json_schema_generation(self):
        """JSON schemas should be valid dicts with required keys."""
        for ft, cls in SCHEMA_REGISTRY.items():
            schema = get_json_schema_for_form(ft)
            assert isinstance(schema, dict)
            assert "properties" in schema
            assert "title" in schema


class TestForm1120S:
    def test_default_construction(self):
        form = Form1120S()
        assert form.form_type == "1120-S"
        assert form.tax_year is None
        assert form.income.line_1a_gross_receipts is None

    def test_populated(self):
        form = Form1120S(
            tax_year="2022",
            taxpayer={"name": "Lovelight LLC", "ein": "81-4174306"},
            income={"line_1a_gross_receipts": 103910, "line_6_total_income": 103910},
        )
        assert form.taxpayer.name == "Lovelight LLC"
        assert form.income.line_1a_gross_receipts == 103910

    def test_serialization_roundtrip(self):
        form = Form1120S(
            tax_year="2022",
            taxpayer={"name": "Test Corp", "ein": "12-3456789"},
        )
        data = form.model_dump()
        restored = Form1120S(**data)
        assert restored.taxpayer.name == form.taxpayer.name

    def test_json_schema_has_key_fields(self):
        schema = Form1120S.model_json_schema()
        # Should contain nested definitions
        assert "properties" in schema
        json_str = json.dumps(schema)
        assert "line_1a_gross_receipts" in json_str
        assert "schedule_k" in json_str
        assert "schedule_l" in json_str


class TestScheduleK1:
    def test_partnership_k1(self):
        form = ScheduleK1Partnership(
            tax_year="2022",
            entity={"name": "Test Partnership", "ein": "98-7654321"},
            partner={"name": "John Doe", "profit_sharing_ending": 50.0},
            income_deductions={"line_1_ordinary_business_income": 25000},
        )
        assert form.entity.name == "Test Partnership"
        assert form.partner.profit_sharing_ending == 50.0
        assert form.income_deductions.line_1_ordinary_business_income == 25000

    def test_scorp_k1(self):
        form = ScheduleK1SCorp(
            tax_year="2022",
            entity={"name": "Test S-Corp", "ein": "11-2233445"},
            shareholder={"name": "Jane Smith", "stock_ownership_ending": 100.0},
        )
        assert form.shareholder.stock_ownership_ending == 100.0
