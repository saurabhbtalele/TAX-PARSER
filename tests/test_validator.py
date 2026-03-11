"""Tests for the tax validation rules."""

import pytest

from tax_parser.models.result import FormType, ReviewSeverity
from tax_parser.validators.tax_rules import TaxValidator


@pytest.fixture
def validator():
    return TaxValidator()


class TestEINValidation:
    def test_valid_ein(self, validator):
        data = {"taxpayer": {"name": "Test Corp", "ein": "81-4174306"}}
        flags = validator.validate(FormType.FORM_1120S, data)
        assert not any(f.field_name == "taxpayer.ein" for f in flags)

    def test_invalid_ein_format(self, validator):
        data = {"taxpayer": {"name": "Test Corp", "ein": "814174306"}}
        flags = validator.validate(FormType.FORM_1120S, data)
        ein_flags = [f for f in flags if f.field_name == "taxpayer.ein"]
        assert len(ein_flags) == 1
        assert ein_flags[0].severity == ReviewSeverity.WARNING

    def test_missing_ein_no_flag(self, validator):
        """Missing EIN should not produce an EIN format error."""
        data = {"taxpayer": {"name": "Test Corp"}}
        flags = validator.validate(FormType.FORM_1120S, data)
        assert not any(f.field_name == "taxpayer.ein" for f in flags)


class TestRequiredFields:
    def test_missing_name_flagged(self, validator):
        data = {"taxpayer": {"ein": "12-3456789"}}
        flags = validator.validate(FormType.FORM_1120S, data)
        name_flags = [f for f in flags if f.field_name == "taxpayer.name"]
        assert len(name_flags) == 1
        assert name_flags[0].severity == ReviewSeverity.ERROR


class TestArithmeticValidation1120S:
    def test_line6_correct(self, validator):
        data = {
            "taxpayer": {"name": "Test Corp", "ein": "12-3456789"},
            "income": {
                "line_3_gross_profit": 100000,
                "line_4_net_gain_loss_form_4797": 5000,
                "line_5_other_income_loss": 2000,
                "line_6_total_income": 107000,
            },
        }
        flags = validator.validate(FormType.FORM_1120S, data)
        line6_flags = [f for f in flags if f.field_name == "income.line_6_total_income"]
        assert len(line6_flags) == 0

    def test_line6_incorrect(self, validator):
        data = {
            "taxpayer": {"name": "Test Corp", "ein": "12-3456789"},
            "income": {
                "line_3_gross_profit": 100000,
                "line_4_net_gain_loss_form_4797": 5000,
                "line_5_other_income_loss": 2000,
                "line_6_total_income": 200000,  # Wrong
            },
        }
        flags = validator.validate(FormType.FORM_1120S, data)
        line6_flags = [f for f in flags if f.field_name == "income.line_6_total_income"]
        assert len(line6_flags) == 1
        assert line6_flags[0].severity == ReviewSeverity.ERROR

    def test_line21_correct(self, validator):
        data = {
            "taxpayer": {"name": "Test Corp", "ein": "12-3456789"},
            "income": {"line_6_total_income": 100000},
            "deductions": {"line_20_total_deductions": 60000},
            "tax_payments": {"line_21_ordinary_business_income": 40000},
        }
        flags = validator.validate(FormType.FORM_1120S, data)
        line21_flags = [
            f for f in flags
            if f.field_name == "tax_payments.line_21_ordinary_business_income"
        ]
        assert len(line21_flags) == 0


class TestBalanceSheetValidation:
    def test_balanced(self, validator):
        data = {
            "taxpayer": {"name": "Test Corp", "ein": "12-3456789"},
            "schedule_l": {
                "total_assets": {"end_of_year": 500000},
                "total_liabilities_equity": {"end_of_year": 500000},
            },
        }
        flags = validator.validate(FormType.FORM_1120S, data)
        bs_flags = [f for f in flags if "schedule_l" in (f.field_name or "")]
        assert len(bs_flags) == 0

    def test_unbalanced(self, validator):
        data = {
            "taxpayer": {"name": "Test Corp", "ein": "12-3456789"},
            "schedule_l": {
                "total_assets": {"end_of_year": 500000},
                "total_liabilities_equity": {"end_of_year": 400000},
            },
        }
        flags = validator.validate(FormType.FORM_1120S, data)
        bs_flags = [f for f in flags if "schedule_l" in (f.field_name or "")]
        assert len(bs_flags) == 1
